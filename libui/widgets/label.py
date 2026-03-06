"""Label widget node."""

from __future__ import annotations

from libui import core
from libui.node import Node
from libui.state import Computed, State
from libui.widgets._helpers import _resolve


class Label(Node):
    """Static text label."""

    def __init__(self, text: str | State[str] | Computed[str] = ""):
        super().__init__()
        self._text = text

    def create_widget(self, ctx):
        return core.Label(_resolve(self._text))

    def bind_props(self, widget):
        if isinstance(self._text, (State, Computed)):
            widget.text = self._text.value
            unsub = self._text.subscribe(
                lambda: core.queue_main(
                    lambda: setattr(widget, "text", self._text.value)
                ),
            )
            self.unsubs.append(unsub)
