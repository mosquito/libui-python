"""Separator widget node."""

from __future__ import annotations

from libui import core
from libui.node import Node


class Separator(Node):
    """Visual separator line."""

    def __init__(self, vertical: bool = False):
        super().__init__()
        self._vertical = vertical

    def create_widget(self, ctx):
        return core.Separator(vertical=self._vertical)
