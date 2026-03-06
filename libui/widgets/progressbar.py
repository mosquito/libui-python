"""ProgressBar widget node."""

from __future__ import annotations

from libui import core
from libui.node import Node
from libui.state import Computed, State


class ProgressBar(Node):
    """Progress bar (one-way binding only)."""

    def __init__(self, value: State[int] | Computed[int] | int = 0):
        super().__init__()
        self._value = value

    def create_widget(self, ctx):
        return core.ProgressBar()

    def bind_props(self, widget):
        if isinstance(self._value, (State, Computed)):
            widget.value = self._value.value
            unsub = self._value.subscribe(
                lambda: core.queue_main(
                    lambda: setattr(widget, "value", self._value.value)
                ),
            )
            self.unsubs.append(unsub)
        else:
            widget.value = self._value
