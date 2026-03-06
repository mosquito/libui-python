"""Picker widget nodes: ColorButton, FontButton, DateTimePicker."""

from __future__ import annotations

from typing import Callable

from libui import core
from libui.node import Node
from libui.loop import _ensure_sync


class ColorButton(Node):
    """Color picker button."""

    def __init__(self, on_changed: Callable | None = None):
        super().__init__()
        self._on_changed = on_changed

    def create_widget(self, ctx):
        return core.ColorButton()

    def attach_callbacks(self, widget):
        if self._on_changed:
            wrapped = _ensure_sync(self._on_changed)
            widget.on_changed(lambda: wrapped(widget.color))


class FontButton(Node):
    """Font picker button."""

    def __init__(self, on_changed: Callable | None = None):
        super().__init__()
        self._on_changed = on_changed

    def create_widget(self, ctx):
        return core.FontButton()

    def attach_callbacks(self, widget):
        if self._on_changed:
            wrapped = _ensure_sync(self._on_changed)
            widget.on_changed(lambda: wrapped(widget.font))


class DateTimePicker(Node):
    """Date/time picker."""

    def __init__(self, type: str = "datetime", on_changed: Callable | None = None):
        super().__init__()
        self._type = type
        self._on_changed = on_changed

    def create_widget(self, ctx):
        return core.DateTimePicker(type=self._type)

    def attach_callbacks(self, widget):
        if self._on_changed:
            wrapped = _ensure_sync(self._on_changed)
            widget.on_changed(lambda: wrapped(widget.time))
