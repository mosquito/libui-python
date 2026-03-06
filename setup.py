"""Build setup for libui package — builds libui-ng via meson, then compiles core.c."""

import subprocess
import sys
from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext as _build_ext

LIBUI_SRC = Path(__file__).parent / "src" / "libui-ng"


class build_ext(_build_ext):
    def build_extension(self, ext):
        build_dir = Path(self.build_temp) / "libui-build"
        build_dir.mkdir(parents=True, exist_ok=True)

        # Configure meson
        if not (build_dir / "build.ninja").exists():
            subprocess.check_call(
                [
                    "meson",
                    "setup",
                    str(build_dir),
                    str(LIBUI_SRC),
                    "--default-library=static",
                    "--buildtype=release",
                    "-Dtests=false",
                    "-Dexamples=false",
                ]
            )

        # Build
        subprocess.check_call(["meson", "compile", "-C", str(build_dir)])

        # Find libui.a / libui.lib
        libui_a = build_dir / "libui.a"
        if not libui_a.exists():
            libui_a = build_dir / "libui.lib"
        if not libui_a.exists():
            # Search for it
            for f in build_dir.rglob("libui.*"):
                if f.suffix in (".a", ".lib"):
                    libui_a = f
                    break
        if not libui_a.exists():
            raise RuntimeError(f"Cannot find libui static library in {build_dir}")

        ext.extra_objects = [str(libui_a)]

        # Platform-specific flags
        if sys.platform == "linux":
            pkg_cflags = (
                subprocess.check_output(
                    ["pkg-config", "--cflags", "gtk+-3.0"],
                    text=True,
                )
                .strip()
                .split()
            )
            pkg_libs = (
                subprocess.check_output(
                    ["pkg-config", "--libs", "gtk+-3.0"],
                    text=True,
                )
                .strip()
                .split()
            )
            ext.extra_compile_args.extend(pkg_cflags)
            ext.extra_link_args.extend(pkg_libs)
            ext.extra_link_args.extend(["-lm", "-ldl", "-lstdc++"])
        elif sys.platform == "darwin":
            ext.extra_link_args.extend(
                [
                    "-framework",
                    "Cocoa",
                    "-lobjc",
                    "-lstdc++",
                ]
            )
        elif sys.platform == "win32":
            # Disable /GL and /LTCG — setuptools enables these by default
            # for MSVC release builds, but libui.a is compiled by meson
            # without /GL, causing LNK1143 when the linker tries to process
            # non-LTCG objects under /LTCG mode.
            ext.extra_compile_args.append("/GL-")
            ext.extra_link_args.append("/LTCG:OFF")
            ext.libraries.extend(
                [
                    "user32",
                    "kernel32",
                    "gdi32",
                    "comctl32",
                    "uxtheme",
                    "msimg32",
                    "comdlg32",
                    "d2d1",
                    "dwrite",
                    "ole32",
                    "oleaut32",
                    "oleacc",
                    "uuid",
                    "windowscodecs",
                ]
            )

        super().build_extension(ext)


setup(
    ext_modules=[
        Extension(
            "libui.core",
            sources=[
                "src/py_module/module.c",
                "src/py_module/enums.c",
                "src/py_module/control.c",
                "src/py_module/widget_window.c",
                "src/py_module/widget_box.c",
                "src/py_module/widget_button.c",
                "src/py_module/widget_label.c",
                "src/py_module/widget_entry.c",
                "src/py_module/widget_checkbox.c",
                "src/py_module/widget_combobox.c",
                "src/py_module/widget_tab.c",
                "src/py_module/widget_group.c",
                "src/py_module/widget_spinbox.c",
                "src/py_module/widget_slider.c",
                "src/py_module/widget_progressbar.c",
                "src/py_module/widget_separator.c",
                "src/py_module/widget_editablecombobox.c",
                "src/py_module/widget_radiobuttons.c",
                "src/py_module/widget_datetimepicker.c",
                "src/py_module/widget_multilineentry.c",
                "src/py_module/widget_colorbutton.c",
                "src/py_module/widget_fontbutton.c",
                "src/py_module/widget_form.c",
                "src/py_module/widget_grid.c",
                "src/py_module/widget_menu.c",
                "src/py_module/image.c",
                "src/py_module/attribute.c",
                "src/py_module/attributed_string.c",
                "src/py_module/draw.c",
                "src/py_module/widget_area.c",
                "src/py_module/table_model.c",
                "src/py_module/widget_table.c",
            ],
            include_dirs=[str(LIBUI_SRC), "src/py_module"],
            extra_compile_args=["-D_UI_STATIC"],
        ),
    ],
    cmdclass={"build_ext": build_ext},
)
