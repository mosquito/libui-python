"""Spinbox widget node."""

from __future__ import annotations

from typing import Callable

from libui import core
from libui.node import Node, make_two_way
from libui.state import Computed, State
from libui.loop import _ensure_sync


class Spinbox(Node):
    """Numeric spinbox with optional two-way ``value`` binding."""

    def __init__(
        self,
        min: int = 0,
        max: int = 100,
        value: State[int] | int = 0,
        on_changed: Callable | None = None,
    ):
        super().__init__()
        self._min = min
        self._max = max
        self._value = value
        self._on_changed = on_changed

    def create_widget(self, ctx):
        return core.Spinbox(self._min, self._max)

    def bind_props(self, widget):
        if isinstance(self._value, State):
            widget.value = self._value.value
            make_two_way(
                self,
                widget,
                "value",
                self._value,
                "on_changed",
                user_cb=self._on_changed,
            )
        elif isinstance(self._value, Computed):
            widget.value = self._value.value
            unsub = self._value.subscribe(
                lambda: core.queue_main(
                    lambda: setattr(widget, "value", self._value.value)
                ),
            )
            self.unsubs.append(unsub)
        else:
            widget.value = self._value

    def attach_callbacks(self, widget):
        if self._on_changed and not isinstance(self._value, State):
            wrapped = _ensure_sync(self._on_changed)
            widget.on_changed(lambda: wrapped(widget.value))
