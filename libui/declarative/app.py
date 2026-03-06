"""App root, Window, and Menu descriptors for the declarative UI layer."""

from __future__ import annotations

import asyncio
from typing import Callable

from libui import core
import libui.loop as _loop
from libui.loop import (
    _ensure_sync,
    _register_window,
    invoke_on_main,
    invoke_on_main_async,
)
from libui.declarative.node import BuildContext, Node
from libui.declarative.state import State
from libui.loop import quit as ui_quit


# ── Menu descriptors ─────────────────────────────────────────────────


class _MenuEntry:
    """Base for menu item descriptors."""

    pass


class MenuItem(_MenuEntry):
    """A regular clickable menu item."""

    def __init__(self, name: str, on_click: Callable | None = None):
        self.name = name
        self.on_click = on_click


class CheckMenuItem(_MenuEntry):
    """A checkable menu item with optional State binding."""

    def __init__(
        self,
        name: str,
        checked: State[bool] | None = None,
        on_click: Callable | None = None,
    ):
        self.name = name
        self.checked = checked
        self.on_click = on_click


class MenuSeparator(_MenuEntry):
    """A separator line in a menu."""

    pass


class QuitItem(_MenuEntry):
    """Platform Quit menu item."""

    pass


class PreferencesItem(_MenuEntry):
    """Platform Preferences menu item."""

    pass


class AboutItem(_MenuEntry):
    """Platform About menu item."""

    pass


class MenuDef:
    """Definition for a top-level menu."""

    def __init__(self, title: str, *items: _MenuEntry):
        self.title = title
        self.items = items


# ── Window ───────────────────────────────────────────────────────────


class Window(Node):
    """Top-level window descriptor."""

    def __init__(
        self,
        title: str = "Application",
        width: int = 800,
        height: int = 600,
        child: Node | None = None,
        has_menubar: bool = False,
        margined: bool = True,
        on_closing: Callable | None = None,
    ):
        super().__init__()
        self._title = title
        self._width = width
        self._height = height
        self._child = child
        self._has_menubar = has_menubar
        self._margined = margined
        self._on_closing = on_closing

    def create_widget(self, ctx):
        w = core.Window(
            self._title, self._width, self._height, has_menubar=self._has_menubar
        )
        _register_window(w)
        w.margined = self._margined
        ctx.window = w
        return w

    def attach_children(self, widget, ctx):
        if self._child:
            self._child.build(ctx)
            widget.set_child(self._child.widget)

    def attach_callbacks(self, widget):
        if self._on_closing:
            widget.on_closing(_ensure_sync(self._on_closing, default_return=True))
        else:

            def default_on_closing():
                ui_quit()
                return True

            widget.on_closing(default_on_closing)


# ── App ──────────────────────────────────────────────────────────────


class App:
    """Application root. Manages menus and a single window."""

    def __init__(
        self,
        window: Window | None = None,
        menus: list[MenuDef] | None = None,
    ):
        self._window = window
        self._menus = menus or []
        self._ctx = BuildContext()
        self._built = False

    def build(
        self, window: Window | None = None, menus: list[MenuDef] | None = None
    ) -> None:
        """Materialise the full widget tree: menus first, then window.

        Optional *window* and *menus* args override values set in ``__init__``.
        """
        if self._built:
            return

        if window is not None:
            self._window = window
        if menus is not None:
            self._menus = menus

        if self._window is None:
            raise ValueError("App.build() requires a window")

        # If the two-thread model is active, dispatch to the main thread;
        # otherwise (tests, single-threaded usage) run directly.
        if _loop._asyncio_loop is not None:
            invoke_on_main(self._build_on_main)
        else:
            self._build_on_main()

    def _build_on_main(self) -> None:
        """Run on main thread — all core.* widget creation happens here."""
        # Menus must be created before the window (libui constraint)
        for menu_def in self._menus:
            self._build_menu(menu_def)

        # Build the window and all its children
        self._window.build(self._ctx)
        self._built = True

    def _build_menu(self, menu_def: MenuDef) -> None:
        menu = core.Menu(menu_def.title)
        self._ctx.refs.append(menu)

        for entry in menu_def.items:
            if isinstance(entry, MenuItem):
                item = menu.append_item(entry.name)
                if entry.on_click:
                    # Wrap to pass window reference
                    handler = entry.on_click
                    item.on_clicked(handler)
                self._ctx.refs.append(item)

            elif isinstance(entry, CheckMenuItem):
                item = menu.append_check_item(entry.name)
                if entry.checked is not None and isinstance(entry.checked, State):
                    item.checked = entry.checked.value
                    state = entry.checked
                    user_cb = entry.on_click

                    def make_handler(st, it, cb):
                        def handler():
                            st.set(it.checked)
                            if cb:
                                cb()

                        return handler

                    item.on_clicked(make_handler(state, item, user_cb))
                    unsub = state.subscribe(
                        lambda it=item, st=state: setattr(it, "checked", st.value)
                    )
                    self._ctx.refs.append(unsub)
                elif entry.on_click:
                    item.on_clicked(entry.on_click)
                self._ctx.refs.append(item)

            elif isinstance(entry, MenuSeparator):
                menu.append_separator()

            elif isinstance(entry, QuitItem):
                menu.append_quit_item()

            elif isinstance(entry, PreferencesItem):
                menu.append_preferences_item()

            elif isinstance(entry, AboutItem):
                menu.append_about_item()

    def show(self) -> None:
        """Show the window."""
        if self._window and self._window.widget:
            self._window.widget.show()

    @property
    def window(self):
        """The underlying core Window widget (available after build)."""
        return self._window.widget if self._window else None

    # ── Sync dialog helpers (for main-thread callers) ────────────────

    def msg_box(self, title: str, description: str) -> None:
        """Show an informational message box."""
        w = self.window
        if w:
            core.msg_box(w, title, description)

    def msg_box_error(self, title: str, description: str) -> None:
        """Show an error message box."""
        w = self.window
        if w:
            core.msg_box_error(w, title, description)

    def open_file(self) -> str | None:
        """Show an Open File dialog. Returns path or None."""
        w = self.window
        if w:
            return core.open_file(w)
        return None

    def open_folder(self) -> str | None:
        """Show an Open Folder dialog. Returns path or None."""
        w = self.window
        if w:
            return core.open_folder(w)
        return None

    def save_file(self) -> str | None:
        """Show a Save File dialog. Returns path or None."""
        w = self.window
        if w:
            return core.save_file(w)
        return None

    # ── Async dialog helpers (for asyncio-thread callers) ────────────

    async def open_file_async(self) -> str | None:
        w = self.window
        if w:
            return await invoke_on_main_async(core.open_file, w)
        return None

    async def open_folder_async(self) -> str | None:
        w = self.window
        if w:
            return await invoke_on_main_async(core.open_folder, w)
        return None

    async def save_file_async(self) -> str | None:
        w = self.window
        if w:
            return await invoke_on_main_async(core.save_file, w)
        return None

    async def msg_box_async(self, title: str, description: str) -> None:
        w = self.window
        if w:
            await invoke_on_main_async(core.msg_box, w, title, description)

    async def msg_box_error_async(self, title: str, description: str) -> None:
        w = self.window
        if w:
            await invoke_on_main_async(core.msg_box_error, w, title, description)

    async def wait(self) -> None:
        """Wait until quit is signalled."""
        await asyncio.get_running_loop().create_future()
