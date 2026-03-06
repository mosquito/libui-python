"""Combobox and EditableCombobox widget nodes."""

from __future__ import annotations

from typing import Callable, Sequence

from libui import core
from libui.node import Node, make_two_way
from libui.state import State
from libui.loop import _ensure_sync


class Combobox(Node):
    """Drop-down combobox with optional two-way ``selected`` binding."""

    def __init__(
        self,
        items: Sequence[str] = (),
        selected: State[int] | int = 0,
        on_selected: Callable | None = None,
    ):
        super().__init__()
        self._items = items
        self._selected = selected
        self._on_selected = on_selected

    def create_widget(self, ctx):
        w = core.Combobox()
        for item in self._items:
            w.append(item)
        return w

    def bind_props(self, widget):
        if isinstance(self._selected, State):
            widget.selected = self._selected.value
            make_two_way(
                self,
                widget,
                "selected",
                self._selected,
                "on_selected",
                user_cb=self._on_selected,
            )
        else:
            widget.selected = self._selected

    def attach_callbacks(self, widget):
        if self._on_selected and not isinstance(self._selected, State):
            wrapped = _ensure_sync(self._on_selected)
            widget.on_selected(lambda: wrapped(widget.selected))


class EditableCombobox(Node):
    """Editable combobox with optional two-way ``text`` binding."""

    def __init__(
        self,
        items: Sequence[str] = (),
        text: State[str] | str = "",
        on_changed: Callable | None = None,
    ):
        super().__init__()
        self._items = items
        self._text = text
        self._on_changed = on_changed

    def create_widget(self, ctx):
        w = core.EditableCombobox()
        for item in self._items:
            w.append(item)
        return w

    def bind_props(self, widget):
        if isinstance(self._text, State):
            widget.text = self._text.value
            make_two_way(
                self, widget, "text", self._text, "on_changed", user_cb=self._on_changed
            )
        elif self._text:
            widget.text = self._text

    def attach_callbacks(self, widget):
        if self._on_changed and not isinstance(self._text, State):
            wrapped = _ensure_sync(self._on_changed)
            widget.on_changed(lambda: wrapped(widget.text))
