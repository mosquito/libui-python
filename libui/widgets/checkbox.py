"""Checkbox widget node."""

from __future__ import annotations

from typing import Callable

from libui import core
from libui.node import Node, make_two_way
from libui.state import State
from libui.loop import _ensure_sync


class Checkbox(Node):
    """Checkbox with optional two-way binding for ``checked``."""

    def __init__(
        self,
        text: str = "",
        checked: State[bool] | bool = False,
        on_toggled: Callable | None = None,
    ):
        super().__init__()
        self._text = text
        self._checked = checked
        self._on_toggled = on_toggled

    def create_widget(self, ctx):
        return core.Checkbox(self._text)

    def bind_props(self, widget):
        if isinstance(self._checked, State):
            widget.checked = self._checked.value
            make_two_way(
                self,
                widget,
                "checked",
                self._checked,
                "on_toggled",
                user_cb=self._on_toggled,
            )
        else:
            widget.checked = self._checked

    def attach_callbacks(self, widget):
        if self._on_toggled and not isinstance(self._checked, State):
            wrapped = _ensure_sync(self._on_toggled)
            widget.on_toggled(lambda: wrapped(widget.checked))
