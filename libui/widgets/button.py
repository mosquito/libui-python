"""Button widget node."""

from __future__ import annotations

from typing import Callable

from libui import core
from libui.node import Node


class Button(Node):
    """Clickable button."""

    def __init__(self, text: str = "", on_clicked: Callable | None = None):
        super().__init__()
        self._text = text
        if on_clicked:
            self.callbacks["on_clicked"] = on_clicked

    def create_widget(self, ctx):
        return core.Button(self._text)
