"""Drawing area widget nodes."""

from __future__ import annotations

from typing import Callable

from libui import core
from libui.loop import _ensure_sync
from libui.node import Node


class DrawArea(Node):
    """Custom drawing area with optional event callbacks.

    Callbacks:
        on_draw(ctx, area_w, area_h, clip_x, clip_y, clip_w, clip_h):
            Called to paint the area. Must be synchronous.
        on_mouse_event(event_dict):
            Mouse button/move. Keys: x, y, area_width, area_height,
            down, up, count, modifiers, held. May be async.
        on_mouse_crossed(left: bool):
            Mouse entered (False) or left (True) the area. May be async.
        on_drag_broken():
            OS interrupted a drag. May be async.
        on_key_event(event_dict) -> bool:
            Key press/release. Keys: key, ext_key, modifier, modifiers, up.
            Return True to consume. Must be synchronous.
    """

    def __init__(
        self,
        on_draw: Callable | None = None,
        on_mouse_event: Callable | None = None,
        on_mouse_crossed: Callable | None = None,
        on_drag_broken: Callable | None = None,
        on_key_event: Callable | None = None,
    ):
        super().__init__()
        self._on_draw = on_draw
        # on_draw and on_key_event must stay synchronous (return values matter)
        # on_mouse_event, on_mouse_crossed, on_drag_broken can be async
        self._on_mouse_event = _ensure_sync(on_mouse_event)
        self._on_mouse_crossed = _ensure_sync(on_mouse_crossed)
        self._on_drag_broken = _ensure_sync(on_drag_broken)
        self._on_key_event = on_key_event

    def create_widget(self, ctx):
        return core.Area(
            self._on_draw,
            on_mouse_event=self._on_mouse_event,
            on_mouse_crossed=self._on_mouse_crossed,
            on_drag_broken=self._on_drag_broken,
            on_key_event=self._on_key_event,
        )


class ScrollingDrawArea(Node):
    """Scrollable custom drawing area with a fixed content size.

    Same callbacks as DrawArea, plus width/height for the scrollable region.
    """

    def __init__(
        self,
        on_draw: Callable | None = None,
        width: int = 1000,
        height: int = 1000,
        on_mouse_event: Callable | None = None,
        on_mouse_crossed: Callable | None = None,
        on_drag_broken: Callable | None = None,
        on_key_event: Callable | None = None,
    ):
        super().__init__()
        self._on_draw = on_draw
        self._width = width
        self._height = height
        self._on_mouse_event = _ensure_sync(on_mouse_event)
        self._on_mouse_crossed = _ensure_sync(on_mouse_crossed)
        self._on_drag_broken = _ensure_sync(on_drag_broken)
        self._on_key_event = on_key_event

    def create_widget(self, ctx):
        return core.ScrollingArea(
            self._on_draw,
            self._width,
            self._height,
            on_mouse_event=self._on_mouse_event,
            on_mouse_crossed=self._on_mouse_crossed,
            on_drag_broken=self._on_drag_broken,
            on_key_event=self._on_key_event,
        )
