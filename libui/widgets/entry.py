"""Entry and MultilineEntry widget nodes."""

from __future__ import annotations

from typing import Callable

from libui import core
from libui.node import Node, make_two_way
from libui.state import Computed, State
from libui.loop import _ensure_sync


class Entry(Node):
    """Single-line text entry with optional two-way binding."""

    def __init__(
        self,
        text: State[str] | str | None = None,
        type: str = "normal",
        read_only: State[bool] | bool = False,
        on_changed: Callable | None = None,
    ):
        super().__init__()
        self._text_state = text if isinstance(text, (State, Computed)) else None
        self._text_init = text if not isinstance(text, (State, Computed)) else None
        self._type = type
        self._read_only = read_only
        self._on_changed = on_changed

    def create_widget(self, ctx):
        return core.Entry(type=self._type)

    def bind_props(self, widget):
        widget.read_only = (
            self._read_only
            if not isinstance(self._read_only, (State, Computed))
            else self._read_only.value
        )
        if isinstance(self._read_only, (State, Computed)):
            unsub = self._read_only.subscribe(
                lambda: core.queue_main(
                    lambda: setattr(widget, "read_only", self._read_only.value)
                ),
            )
            self.unsubs.append(unsub)
        if self._text_state is not None:
            widget.text = self._text_state.value
            if isinstance(self._text_state, State):
                make_two_way(
                    self,
                    widget,
                    "text",
                    self._text_state,
                    "on_changed",
                    user_cb=self._on_changed,
                )
            else:
                unsub = self._text_state.subscribe(
                    lambda: core.queue_main(
                        lambda: setattr(widget, "text", self._text_state.value)
                    ),
                )
                self.unsubs.append(unsub)
        elif self._text_init is not None:
            widget.text = self._text_init

    def attach_callbacks(self, widget):
        if self._on_changed:
            if self._text_state is None:
                wrapped = _ensure_sync(self._on_changed)
                widget.on_changed(lambda: wrapped(widget.text))


class MultilineEntry(Node):
    """Multi-line text entry with optional two-way ``text`` binding."""

    def __init__(
        self,
        text: State[str] | str = "",
        wrapping: bool = True,
        read_only: State[bool] | bool = False,
        on_changed: Callable | None = None,
    ):
        super().__init__()
        self._text = text
        self._wrapping = wrapping
        self._read_only = read_only
        self._on_changed = on_changed

    def create_widget(self, ctx):
        return core.MultilineEntry(wrapping=self._wrapping)

    def bind_props(self, widget):
        widget.read_only = (
            self._read_only
            if not isinstance(self._read_only, (State, Computed))
            else self._read_only.value
        )
        if isinstance(self._read_only, (State, Computed)):
            unsub = self._read_only.subscribe(
                lambda: core.queue_main(
                    lambda: setattr(widget, "read_only", self._read_only.value)
                ),
            )
            self.unsubs.append(unsub)
        if isinstance(self._text, State):
            widget.text = self._text.value
            make_two_way(
                self, widget, "text", self._text, "on_changed", user_cb=self._on_changed
            )
        elif isinstance(self._text, Computed):
            widget.text = self._text.value
            unsub = self._text.subscribe(
                lambda: core.queue_main(
                    lambda: setattr(widget, "text", self._text.value)
                ),
            )
            self.unsubs.append(unsub)
        elif self._text:
            widget.text = self._text

    def attach_callbacks(self, widget):
        if self._on_changed and not isinstance(self._text, State):
            wrapped = _ensure_sync(self._on_changed)
            widget.on_changed(lambda: wrapped(widget.text))
