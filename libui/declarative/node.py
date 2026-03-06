"""Node base class and build infrastructure for the declarative UI layer."""

from __future__ import annotations

from typing import Any

from libui import core
from libui.declarative.state import Computed, State
from libui.loop import _ensure_sync


class BuildContext:
    """Carries shared state during the build phase."""

    def __init__(self, window=None):
        self.window = window
        self.refs: list[Any] = []  # prevent GC of transient objects


class Node:
    """Base descriptor for a UI element. Lightweight — does not create widgets.

    Subclasses override :meth:`create_widget` and optionally
    :meth:`attach_children`.
    """

    def __init__(self, **kwargs):
        self.props: dict[str, Any] = {}
        self.children: list[Node] = []
        self.callbacks: dict[str, Any] = {}
        self.stretchy: bool = False
        self.widget: Any = None
        self.unsubs: list = []

        # Subclasses pass known kwargs; anything left is an error.
        # This base __init__ is called after the subclass has consumed its own
        # kwargs, so nothing should remain.

    def create_widget(self, ctx: BuildContext) -> Any:
        raise NotImplementedError

    def build(self, ctx: BuildContext) -> Any:
        """Materialise the widget tree rooted at this node."""
        widget = self.create_widget(ctx)
        self.widget = widget
        self.bind_props(widget)
        self.attach_callbacks(widget)
        self.attach_children(widget, ctx)
        return widget

    def bind_props(self, widget: Any) -> None:
        """Bind State/Computed props to widget attributes."""
        for prop, val in self.props.items():
            if isinstance(val, (State, Computed)):
                setattr(widget, prop, val.value)
                unsub = val.subscribe(
                    lambda p=prop, s=val: core.queue_main(
                        lambda p=p, s=s: setattr(self.widget, p, s.value)
                    ),
                )
                self.unsubs.append(unsub)
            else:
                setattr(widget, prop, val)

    def attach_callbacks(self, widget: Any) -> None:
        """Register event callbacks on the widget."""
        for event, handler in self.callbacks.items():
            getattr(widget, event)(_ensure_sync(handler))

    def attach_children(self, widget: Any, ctx: BuildContext) -> None:
        """Override to add children to the widget."""


def make_two_way(
    node: Node,
    widget,
    prop: str,
    state: State,
    event: str,
    user_cb=None,
    _wrap_cb: bool = True,
) -> None:
    """Set up two-way binding between a State and a widget property.

    State -> widget: subscribe to state changes and set widget prop.
    Widget -> state: register the widget event callback to push into state.
    The reentrancy guard in State.set() prevents cycles.

    If *user_cb* is provided it is called with the current value after
    the State has been updated.
    """

    # State → widget (subscriber may fire from asyncio thread)
    def on_state_change():
        val = state.value
        core.queue_main(lambda: setattr(widget, prop, val))

    unsub = state.subscribe(on_state_change)
    node.unsubs.append(unsub)

    # Widget → State (fires on main thread via trampoline)
    wrapped_user_cb = _ensure_sync(user_cb) if _wrap_cb else user_cb

    def on_widget_change():
        val = getattr(widget, prop)
        state.set(val)
        if wrapped_user_cb:
            wrapped_user_cb(val)

    getattr(widget, event)(on_widget_change)


def stretchy(node: Node) -> Node:
    """Mark a node as stretchy in a Box layout."""
    node.stretchy = True
    return node
