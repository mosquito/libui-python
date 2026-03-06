"""Declarative widget node descriptors for all libui-ng controls."""

from __future__ import annotations

from typing import Callable, Sequence

from libui import core
from libui.declarative.node import Node, make_two_way
from libui.declarative.state import Computed, ListState, State
from libui.loop import _ensure_sync


# ── Helpers ──────────────────────────────────────────────────────────


def _resolve(val):
    """Return the plain value from a State/Computed or pass through."""
    if isinstance(val, (State, Computed)):
        return val.value
    return val


# ── Containers ───────────────────────────────────────────────────────


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


# ── Leaf Widgets ─────────────────────────────────────────────────────


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


class Button(Node):
    """Clickable button."""

    def __init__(self, text: str = "", on_clicked: Callable | None = None):
        super().__init__()
        self._text = text
        if on_clicked:
            self.callbacks["on_clicked"] = on_clicked

    def create_widget(self, ctx):
        return core.Button(self._text)


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
                # Computed — one-way only
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
            # When State is bound, user_cb is passed via make_two_way in bind_props


class Checkbox(Node):
    """Checkbox with optional two-way binding for ``checked``."""

    def __init__(
        self,
        text: str = "",
        checked: State[bool] | bool = False,
        on_toggled: Callable | None = None,
    ):
        super().__init__()
        self._text = text
        self._checked = checked
        self._on_toggled = on_toggled

    def create_widget(self, ctx):
        return core.Checkbox(self._text)

    def bind_props(self, widget):
        if isinstance(self._checked, State):
            widget.checked = self._checked.value
            make_two_way(
                self,
                widget,
                "checked",
                self._checked,
                "on_toggled",
                user_cb=self._on_toggled,
            )
        else:
            widget.checked = self._checked

    def attach_callbacks(self, widget):
        if self._on_toggled and not isinstance(self._checked, State):
            wrapped = _ensure_sync(self._on_toggled)
            widget.on_toggled(lambda: wrapped(widget.checked))


class Slider(Node):
    """Horizontal slider with optional two-way ``value`` binding."""

    def __init__(
        self,
        min: int = 0,
        max: int = 100,
        value: State[int] | int = 0,
        has_tooltip: bool = True,
        on_changed: Callable | None = None,
    ):
        super().__init__()
        self._min = min
        self._max = max
        self._value = value
        self._has_tooltip = has_tooltip
        self._on_changed = on_changed

    def create_widget(self, ctx):
        return core.Slider(self._min, self._max)

    def bind_props(self, widget):
        widget.has_tooltip = self._has_tooltip
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


class Combobox(Node):
    """Drop-down combobox with optional two-way ``selected`` binding."""

    def __init__(
        self,
        items: Sequence[str] = (),
        selected: State[int] | int = 0,
        on_selected: Callable | None = None,
    ):
        super().__init__()
        self._items = items
        self._selected = selected
        self._on_selected = on_selected

    def create_widget(self, ctx):
        w = core.Combobox()
        for item in self._items:
            w.append(item)
        return w

    def bind_props(self, widget):
        if isinstance(self._selected, State):
            widget.selected = self._selected.value
            make_two_way(
                self,
                widget,
                "selected",
                self._selected,
                "on_selected",
                user_cb=self._on_selected,
            )
        else:
            widget.selected = self._selected

    def attach_callbacks(self, widget):
        if self._on_selected and not isinstance(self._selected, State):
            wrapped = _ensure_sync(self._on_selected)
            widget.on_selected(lambda: wrapped(widget.selected))


class RadioButtons(Node):
    """Radio button group with optional two-way ``selected`` binding."""

    def __init__(
        self,
        items: Sequence[str] = (),
        selected: State[int] | int = -1,
        on_selected: Callable | None = None,
    ):
        super().__init__()
        self._items = items
        self._selected = selected
        self._on_selected = on_selected

    def create_widget(self, ctx):
        w = core.RadioButtons()
        for item in self._items:
            w.append(item)
        return w

    def bind_props(self, widget):
        if isinstance(self._selected, State):
            if self._selected.value >= 0:
                widget.selected = self._selected.value
            make_two_way(
                self,
                widget,
                "selected",
                self._selected,
                "on_selected",
                user_cb=self._on_selected,
            )
        elif self._selected >= 0:
            widget.selected = self._selected

    def attach_callbacks(self, widget):
        if self._on_selected and not isinstance(self._selected, State):
            wrapped = _ensure_sync(self._on_selected)
            widget.on_selected(lambda: wrapped(widget.selected))


class EditableCombobox(Node):
    """Editable combobox with optional two-way ``text`` binding."""

    def __init__(
        self,
        items: Sequence[str] = (),
        text: State[str] | str = "",
        on_changed: Callable | None = None,
    ):
        super().__init__()
        self._items = items
        self._text = text
        self._on_changed = on_changed

    def create_widget(self, ctx):
        w = core.EditableCombobox()
        for item in self._items:
            w.append(item)
        return w

    def bind_props(self, widget):
        if isinstance(self._text, State):
            widget.text = self._text.value
            make_two_way(
                self, widget, "text", self._text, "on_changed", user_cb=self._on_changed
            )
        elif self._text:
            widget.text = self._text

    def attach_callbacks(self, widget):
        if self._on_changed and not isinstance(self._text, State):
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


class Separator(Node):
    """Visual separator line."""

    def __init__(self, vertical: bool = False):
        super().__init__()
        self._vertical = vertical

    def create_widget(self, ctx):
        return core.Separator(vertical=self._vertical)


# ── Drawing ──────────────────────────────────────────────────────────


class DrawArea(Node):
    """Custom drawing area. Drawing remains imperative via callback."""

    def __init__(self, on_draw: Callable | None = None):
        super().__init__()
        self._on_draw = on_draw

    def create_widget(self, ctx):
        return core.Area(self._on_draw)


# ── DataTable ────────────────────────────────────────────────────────


class _ColumnDescriptor:
    """Base class for table column descriptors."""

    pass


class TextColumn(_ColumnDescriptor):
    def __init__(
        self, name: str, key: str, editable: bool = False, color_col: int = -1
    ):
        self.name = name
        self.key = key
        self.editable = editable
        self.color_col = color_col


class CheckboxColumn(_ColumnDescriptor):
    def __init__(self, name: str, key: str, editable: bool = True):
        self.name = name
        self.key = key
        self.editable = editable


class CheckboxTextColumn(_ColumnDescriptor):
    def __init__(
        self,
        name: str,
        checkbox_key: str,
        text_key: str,
        checkbox_editable: bool = True,
        text_editable: bool = False,
        text_color_col: int = -1,
    ):
        self.name = name
        self.checkbox_key = checkbox_key
        self.text_key = text_key
        self.checkbox_editable = checkbox_editable
        self.text_editable = text_editable
        self.text_color_col = text_color_col


class ProgressColumn(_ColumnDescriptor):
    def __init__(self, name: str, key: str):
        self.name = name
        self.key = key


class ButtonColumn(_ColumnDescriptor):
    def __init__(
        self,
        name: str,
        text_key: str,
        on_click: Callable | None = None,
        clickable: bool = True,
    ):
        self.name = name
        self.text_key = text_key
        self.on_click = on_click
        self.clickable = clickable


class ImageColumn(_ColumnDescriptor):
    def __init__(self, name: str, key: str):
        self.name = name
        self.key = key


class ImageTextColumn(_ColumnDescriptor):
    def __init__(
        self,
        name: str,
        image_key: str,
        text_key: str,
        editable: bool = False,
        color_col: int = -1,
    ):
        self.name = name
        self.image_key = image_key
        self.text_key = text_key
        self.editable = editable
        self.color_col = color_col


class DataTable(Node):
    """Declarative table backed by a :class:`ListState`.

    Each row in the ListState is a dict. Column descriptors define
    which keys to display and how.
    """

    def __init__(
        self,
        data: ListState,
        *columns: _ColumnDescriptor,
        on_row_clicked: Callable | None = None,
        on_row_double_clicked: Callable | None = None,
        on_header_clicked: Callable | None = None,
        on_selection_changed: Callable | None = None,
    ):
        super().__init__()
        self._data = data
        self._columns = columns
        self._on_row_clicked = on_row_clicked
        self._on_row_double_clicked = on_row_double_clicked
        self._on_header_clicked = on_header_clicked
        self._on_selection_changed = on_selection_changed

    def create_widget(self, ctx):
        # Build the column mapping: each descriptor maps to 1 or 2 model columns.
        # Model columns are indexed sequentially.
        model_cols = []  # list of (key, value_type)
        col_map = []  # per-descriptor: dict with model column indices
        button_handlers = {}  # col_index -> on_click handler

        for desc in self._columns:
            info = {}
            if isinstance(desc, CheckboxTextColumn):
                cb_col = len(model_cols)
                model_cols.append((desc.checkbox_key, core.TableValueType.INT))
                text_col = len(model_cols)
                model_cols.append((desc.text_key, core.TableValueType.STRING))
                info = {"cb_col": cb_col, "text_col": text_col}
            elif isinstance(desc, CheckboxColumn):
                col = len(model_cols)
                model_cols.append((desc.key, core.TableValueType.INT))
                info = {"col": col}
            elif isinstance(desc, TextColumn):
                col = len(model_cols)
                model_cols.append((desc.key, core.TableValueType.STRING))
                info = {"col": col}
            elif isinstance(desc, ProgressColumn):
                col = len(model_cols)
                model_cols.append((desc.key, core.TableValueType.INT))
                info = {"col": col}
            elif isinstance(desc, ButtonColumn):
                col = len(model_cols)
                model_cols.append((desc.text_key, core.TableValueType.STRING))
                info = {"col": col}
                if desc.on_click:
                    button_handlers[col] = desc.on_click
            elif isinstance(desc, ImageColumn):
                col = len(model_cols)
                model_cols.append((desc.key, core.TableValueType.IMAGE))
                info = {"col": col}
            elif isinstance(desc, ImageTextColumn):
                img_col = len(model_cols)
                model_cols.append((desc.image_key, core.TableValueType.IMAGE))
                text_col = len(model_cols)
                model_cols.append((desc.text_key, core.TableValueType.STRING))
                info = {"img_col": img_col, "text_col": text_col}
            col_map.append(info)

        data = self._data

        def num_columns():
            return len(model_cols)

        def column_type(col):
            return model_cols[col][1]

        def num_rows():
            return len(data)

        def cell_value(row, col):
            key = model_cols[col][0]
            val = data[row][key]
            vtype = model_cols[col][1]
            if vtype == core.TableValueType.INT:
                return int(val)
            elif vtype == core.TableValueType.STRING:
                return str(val)
            return val

        def set_cell_value(row, col, value):
            key = model_cols[col][0]
            data.data[row][key] = value
            if col in button_handlers:
                button_handlers[col](row)

        model = core.TableModel(
            num_columns,
            column_type,
            num_rows,
            cell_value,
            set_cell_value,
        )
        ctx.refs.append(model)

        table = core.Table(model)

        for desc, info in zip(self._columns, col_map):
            if isinstance(desc, CheckboxTextColumn):
                cb_edit = (
                    core.TableModelColumn.ALWAYS_EDITABLE
                    if desc.checkbox_editable
                    else core.TableModelColumn.NEVER_EDITABLE
                )
                text_edit = (
                    core.TableModelColumn.ALWAYS_EDITABLE
                    if desc.text_editable
                    else core.TableModelColumn.NEVER_EDITABLE
                )
                table.append_checkbox_text_column(
                    desc.name,
                    info["cb_col"],
                    cb_edit,
                    info["text_col"],
                    text_edit,
                    desc.text_color_col,
                )
            elif isinstance(desc, CheckboxColumn):
                edit = (
                    core.TableModelColumn.ALWAYS_EDITABLE
                    if desc.editable
                    else core.TableModelColumn.NEVER_EDITABLE
                )
                table.append_checkbox_column(desc.name, info["col"], edit)
            elif isinstance(desc, TextColumn):
                edit = (
                    core.TableModelColumn.ALWAYS_EDITABLE
                    if desc.editable
                    else core.TableModelColumn.NEVER_EDITABLE
                )
                table.append_text_column(desc.name, info["col"], edit, desc.color_col)
            elif isinstance(desc, ProgressColumn):
                table.append_progress_bar_column(desc.name, info["col"])
            elif isinstance(desc, ButtonColumn):
                click = (
                    core.TableModelColumn.ALWAYS_EDITABLE
                    if desc.clickable
                    else core.TableModelColumn.NEVER_EDITABLE
                )
                table.append_button_column(desc.name, info["col"], click)
            elif isinstance(desc, ImageColumn):
                table.append_image_column(desc.name, info["col"])
            elif isinstance(desc, ImageTextColumn):
                edit = (
                    core.TableModelColumn.ALWAYS_EDITABLE
                    if desc.editable
                    else core.TableModelColumn.NEVER_EDITABLE
                )
                table.append_image_text_column(
                    desc.name,
                    info["img_col"],
                    info["text_col"],
                    edit,
                    desc.color_col,
                )

        # Wire ListState notifications to model
        self._model = model

        def on_data_event(event, index=0):
            if event == "inserted":
                model.row_inserted(index)
            elif event == "deleted":
                model.row_deleted(index)
            elif event == "changed":
                model.row_changed(index)

        unsub = data.subscribe(on_data_event)
        self.unsubs.append(unsub)

        # Wire table event callbacks
        if self._on_row_clicked:
            table.on_row_clicked(self._on_row_clicked)
        if self._on_row_double_clicked:
            table.on_row_double_clicked(self._on_row_double_clicked)
        if self._on_header_clicked:
            table.on_header_clicked(self._on_header_clicked)
        if self._on_selection_changed:
            table.on_selection_changed(self._on_selection_changed)

        return table
