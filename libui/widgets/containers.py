"""Container widget nodes: VBox, HBox, Group, Form, Tab, Grid."""

from __future__ import annotations

from libui import core
from libui.node import Node
from libui.state import Computed, State
from libui.widgets._helpers import _resolve


class VBox(Node):
    """Vertical box container."""

    def __init__(self, *children: Node, padded: bool = True):
        super().__init__()
        self.children = list(children)
        self.props["padded"] = padded

    def create_widget(self, ctx):
        return core.VerticalBox()

    def attach_children(self, widget, ctx):
        for child in self.children:
            child.build(ctx)
            widget.append(child.widget, stretchy=child.stretchy)


class HBox(Node):
    """Horizontal box container."""

    def __init__(self, *children: Node, padded: bool = True):
        super().__init__()
        self.children = list(children)
        self.props["padded"] = padded

    def create_widget(self, ctx):
        return core.HorizontalBox()

    def attach_children(self, widget, ctx):
        for child in self.children:
            child.build(ctx)
            widget.append(child.widget, stretchy=child.stretchy)


class Group(Node):
    """Labeled group container with a single child."""

    def __init__(self, title: str | State[str], child: Node, margined: bool = True):
        super().__init__()
        self._title = title
        self._child = child
        self.props["margined"] = margined

    def create_widget(self, ctx):
        return core.Group(_resolve(self._title))

    def attach_children(self, widget, ctx):
        self._child.build(ctx)
        widget.set_child(self._child.widget)

    def bind_props(self, widget):
        super().bind_props(widget)
        if isinstance(self._title, (State, Computed)):
            unsub = self._title.subscribe(
                lambda: core.queue_main(
                    lambda: setattr(widget, "title", self._title.value)
                ),
            )
            self.unsubs.append(unsub)


class Form(Node):
    """Two-column label-control form.

    Children are ``(label, node)`` tuples or ``(label, node, stretchy)`` triples.
    """

    def __init__(self, *rows: tuple, padded: bool = True):
        super().__init__()
        self._rows = rows
        self.props["padded"] = padded

    def create_widget(self, ctx):
        return core.Form()

    def attach_children(self, widget, ctx):
        for row in self._rows:
            if len(row) == 3:
                label, child, st = row
            else:
                label, child = row
                st = False
            child.build(ctx)
            widget.append(label, child.widget, stretchy=st)


class Tab(Node):
    """Tabbed container. Children are ``("Page Name", node)`` tuples."""

    def __init__(self, *pages: tuple[str, Node], margined: bool = True):
        super().__init__()
        self._pages = pages
        self._margined = margined

    def create_widget(self, ctx):
        return core.Tab()

    def attach_children(self, widget, ctx):
        for i, (name, child) in enumerate(self._pages):
            child.build(ctx)
            widget.append(name, child.widget)
            if self._margined:
                widget.set_margined(i, True)


class GridCell:
    """Placement descriptor for a child in a Grid."""

    def __init__(
        self,
        child: Node,
        left: int,
        top: int,
        xspan: int = 1,
        yspan: int = 1,
        hexpand: bool = False,
        halign=core.Align.FILL,
        vexpand: bool = False,
        valign=core.Align.FILL,
    ):
        self.child = child
        self.left = left
        self.top = top
        self.xspan = xspan
        self.yspan = yspan
        self.hexpand = hexpand
        self.halign = halign
        self.vexpand = vexpand
        self.valign = valign


class Grid(Node):
    """Grid layout container."""

    def __init__(self, *cells: GridCell, padded: bool = True):
        super().__init__()
        self._cells = cells
        self.props["padded"] = padded

    def create_widget(self, ctx):
        return core.Grid()

    def attach_children(self, widget, ctx):
        for c in self._cells:
            c.child.build(ctx)
            widget.append(
                c.child.widget,
                c.left,
                c.top,
                c.xspan,
                c.yspan,
                c.hexpand,
                c.halign,
                c.vexpand,
                c.valign,
            )
