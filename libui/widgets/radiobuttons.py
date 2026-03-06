"""RadioButtons widget node."""

from __future__ import annotations

from typing import Callable, Sequence

from libui import core
from libui.node import Node, make_two_way
from libui.state import State
from libui.loop import _ensure_sync


class RadioButtons(Node):
    """Radio button group with optional two-way ``selected`` binding."""

    def __init__(
        self,
        items: Sequence[str] = (),
        selected: State[int] | int = -1,
        on_selected: Callable | None = None,
    ):
        super().__init__()
        self._items = items
        self._selected = selected
        self._on_selected = on_selected

    def create_widget(self, ctx):
        w = core.RadioButtons()
        for item in self._items:
            w.append(item)
        return w

    def bind_props(self, widget):
        if isinstance(self._selected, State):
            if self._selected.value >= 0:
                widget.selected = self._selected.value
            make_two_way(
                self,
                widget,
                "selected",
                self._selected,
                "on_selected",
                user_cb=self._on_selected,
            )
        elif self._selected >= 0:
            widget.selected = self._selected

    def attach_callbacks(self, widget):
        if self._on_selected and not isinstance(self._selected, State):
            wrapped = _ensure_sync(self._on_selected)
            widget.on_selected(lambda: wrapped(widget.selected))
