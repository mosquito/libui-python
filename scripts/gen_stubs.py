#!/usr/bin/env python3
"""Generate a .pyi stub file for the libui.core C extension module.

Introspects the built .so at runtime to discover classes, methods,
properties, functions, and constants.  Outputs the stub to stdout.

Usage:
    python scripts/gen_stubs.py > libui/core.pyi
"""

from __future__ import annotations

import ctypes
import enum
import inspect
import sys
import textwrap
import types


def format_docstring(doc: str | None, indent: str) -> list[str]:
    """Format a docstring as indented triple-quoted lines.

    Returns an empty list if doc is None or empty.
    """
    if not doc:
        return []
    doc = textwrap.dedent(doc).strip()
    if "\n" not in doc:
        return [f'{indent}"""{doc}"""']
    lines = [f'{indent}"""']
    for line in doc.splitlines():
        lines.append(f"{indent}{line}" if line.strip() else "")
    lines.append(f'{indent}"""')
    return lines


def is_readonly_getset(descriptor: object) -> bool:
    """Check if a getset_descriptor has no setter via CPython internals.

    PyGetSetDescrObject layout (CPython 3.13):
      +0:  ob_refcnt   (8 bytes)
      +8:  ob_type     (8 bytes)
      +16: d_type      (8 bytes)
      +24: d_name      (8 bytes)
      +32: d_qualname  (8 bytes)
      +40: d_getset    -> PyGetSetDef*

    PyGetSetDef layout:
      +0:  name    (char*, 8 bytes)
      +8:  get     (getter, 8 bytes)
      +16: set     (setter, 8 bytes)
      +24: doc     (char*, 8 bytes)
      +32: closure (void*, 8 bytes)
    """
    addr = id(descriptor)
    getset_ptr = ctypes.c_void_p.from_address(addr + 40).value
    if getset_ptr is None:
        return True
    setter_ptr = ctypes.c_void_p.from_address(getset_ptr + 16).value
    return setter_ptr is None or setter_ptr == 0


def format_signature(obj: object) -> str | None:
    """Try to get a signature string from inspect.signature().

    Returns the formatted parameter list (without parens) or None if
    the signature can't be determined (METH_VARARGS fallback).
    """
    try:
        sig = inspect.signature(obj)  # type: ignore[arg-type]
        params = []
        for name, param in sig.parameters.items():
            if name == "self":
                params.append("self")
            elif param.kind == param.VAR_POSITIONAL:
                # *args from a METH_VARARGS method — give up
                return None
            elif param.kind == param.VAR_KEYWORD:
                return None
            elif param.default is param.empty:
                params.append(f"{name}: Any")
            else:
                params.append(f"{name}: Any = ...")
        return ", ".join(params)
    except (ValueError, TypeError):
        return None


def topo_sort_classes(
    classes: list[tuple[str, type]],
) -> list[tuple[str, type]]:
    """Sort classes so that base classes appear before subclasses."""
    name_set = {name for name, _ in classes}
    cls_map = {name: cls for name, cls in classes}

    visited: set[str] = set()
    order: list[str] = []

    def visit(name: str) -> None:
        if name in visited:
            return
        visited.add(name)
        cls = cls_map[name]
        for base in cls.__mro__[1:]:
            bname = base.__name__
            if bname in name_set:
                visit(bname)
        order.append(name)

    for name, _ in classes:
        visit(name)

    return [(name, cls_map[name]) for name in order]


def generate_enum_stub(name: str, cls: type) -> str:
    """Generate stub text for an IntEnum or IntFlag class."""
    if issubclass(cls, enum.IntFlag):
        base = "enum.IntFlag"
    else:
        base = "enum.IntEnum"
    lines = [f"class {name}({base}):"]
    for member in cls:
        lines.append(f"    {member.name}: int")
    if not list(cls):
        lines.append("    ...")
    return "\n".join(lines)


def generate_class_stub(name: str, cls: type, module: types.ModuleType) -> str:
    """Generate stub text for a single class."""
    # Handle enum classes separately
    if issubclass(cls, (enum.IntEnum, enum.IntFlag)):
        return generate_enum_stub(name, cls)

    lines: list[str] = []

    # Class declaration with base
    base_name: str | None = None
    for base in cls.__mro__[1:]:
        if base is object:
            continue
        # Only use bases defined in the same module
        if getattr(module, base.__name__, None) is base:
            base_name = base.__name__
            break

    if base_name:
        lines.append(f"class {name}({base_name}):")
    else:
        lines.append(f"class {name}:")

    body_lines: list[str] = []

    # Class docstring
    body_lines.extend(format_docstring(cls.__doc__, "    "))

    # Walk own members only (cls.__dict__)
    members = sorted(cls.__dict__.keys())

    # Collect properties
    for attr_name in members:
        if attr_name.startswith("_"):
            continue
        obj = cls.__dict__[attr_name]
        if not isinstance(obj, types.GetSetDescriptorType):
            continue

        readonly = is_readonly_getset(obj)
        doc = getattr(obj, "__doc__", None)
        body_lines.append("    @property")
        if doc:
            body_lines.append(f"    def {attr_name}(self) -> Any:")
            body_lines.extend(format_docstring(doc, "        "))
        else:
            body_lines.append(f"    def {attr_name}(self) -> Any: ...")
        if not readonly:
            body_lines.append(f"    @{attr_name}.setter")
            body_lines.append(f"    def {attr_name}(self, value: Any) -> None: ...")

    # Collect methods
    for attr_name in members:
        obj = cls.__dict__[attr_name]
        is_method = isinstance(
            obj, (types.MethodDescriptorType, types.WrapperDescriptorType)
        )
        is_builtin_method = isinstance(obj, types.BuiltinMethodType)
        if not is_method and not is_builtin_method:
            continue

        # Skip dunder methods except __init__
        if attr_name.startswith("_") and attr_name != "__init__":
            continue

        sig_str = format_signature(obj)
        doc = getattr(obj, "__doc__", None)
        doc_lines = format_docstring(doc, "        ")

        if attr_name == "__init__":
            if sig_str is not None:
                params = sig_str
            else:
                params = "self, *args: Any, **kwargs: Any"
            if doc_lines:
                body_lines.append(f"    def __init__({params}) -> None:")
                body_lines.extend(doc_lines)
            else:
                body_lines.append(f"    def __init__({params}) -> None: ...")
        else:
            if sig_str is not None:
                params = sig_str
            else:
                params = "self, *args: Any, **kwargs: Any"
            ret = "None" if attr_name == "__init__" else "Any"
            if doc_lines:
                body_lines.append(f"    def {attr_name}({params}) -> {ret}:")
                body_lines.extend(doc_lines)
            else:
                body_lines.append(f"    def {attr_name}({params}) -> {ret}: ...")

    if body_lines:
        lines.extend(body_lines)
    else:
        lines.append("    ...")

    return "\n".join(lines)


def generate_stubs(module_name: str) -> str:
    """Generate the complete .pyi stub for a C extension module."""
    module = __import__(module_name, fromlist=["_"])

    output_lines: list[str] = []
    output_lines.append("import enum")
    output_lines.append("from typing import Any")
    output_lines.append("")

    # Categorize all public names
    all_classes: list[tuple[str, type]] = []
    all_functions: list[tuple[str, object]] = []
    all_constants: list[tuple[str, int]] = []

    for name in sorted(dir(module)):
        if name.startswith("_"):
            continue
        obj = getattr(module, name)
        if isinstance(obj, type):
            all_classes.append((name, obj))
        elif isinstance(obj, int):
            all_constants.append((name, obj))
        elif callable(obj):
            all_functions.append((name, obj))

    # Constants
    for name, _ in all_constants:
        output_lines.append(f"{name}: int")
    if all_constants:
        output_lines.append("")

    # Functions
    for name, obj in all_functions:
        sig_str = format_signature(obj)
        params = sig_str if sig_str is not None else "*args: Any, **kwargs: Any"
        doc = getattr(obj, "__doc__", None)
        doc_lines = format_docstring(doc, "    ")
        if doc_lines:
            output_lines.append(f"def {name}({params}) -> Any:")
            output_lines.extend(doc_lines)
        else:
            output_lines.append(f"def {name}({params}) -> Any: ...")
    if all_functions:
        output_lines.append("")

    # Classes (topologically sorted)
    sorted_classes = topo_sort_classes(all_classes)
    for name, cls in sorted_classes:
        output_lines.append(generate_class_stub(name, cls, module))
        output_lines.append("")

    return "\n".join(output_lines)


def main() -> None:
    module_name = sys.argv[1] if len(sys.argv) > 1 else "libui.core"
    print(generate_stubs(module_name))


if __name__ == "__main__":
    main()
