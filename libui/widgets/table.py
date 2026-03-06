"""DataTable widget node and column descriptors."""

from __future__ import annotations

from typing import Callable

from libui import core
from libui.node import Node
from libui.state import ListState


class _ColumnDescriptor:
    """Base class for table column descriptors."""

    pass


class TextColumn(_ColumnDescriptor):
    def __init__(
        self, name: str, key: str, editable: bool = False, color_col: int = -1,
        width: int = -1,
    ):
        self.name = name
        self.key = key
        self.editable = editable
        self.color_col = color_col
        self.width = width


class CheckboxColumn(_ColumnDescriptor):
    def __init__(self, name: str, key: str, editable: bool = True, width: int = -1):
        self.name = name
        self.key = key
        self.editable = editable
        self.width = width


class CheckboxTextColumn(_ColumnDescriptor):
    def __init__(
        self,
        name: str,
        checkbox_key: str,
        text_key: str,
        checkbox_editable: bool = True,
        text_editable: bool = False,
        text_color_col: int = -1,
        width: int = -1,
    ):
        self.name = name
        self.checkbox_key = checkbox_key
        self.text_key = text_key
        self.checkbox_editable = checkbox_editable
        self.text_editable = text_editable
        self.text_color_col = text_color_col
        self.width = width


class ProgressColumn(_ColumnDescriptor):
    def __init__(self, name: str, key: str, width: int = -1):
        self.name = name
        self.key = key
        self.width = width


class ButtonColumn(_ColumnDescriptor):
    def __init__(
        self,
        name: str,
        text_key: str,
        on_click: Callable | None = None,
        clickable: bool = True,
        width: int = -1,
    ):
        self.name = name
        self.text_key = text_key
        self.on_click = on_click
        self.clickable = clickable
        self.width = width


class ImageColumn(_ColumnDescriptor):
    def __init__(self, name: str, key: str, width: int = -1):
        self.name = name
        self.key = key
        self.width = width


class ImageTextColumn(_ColumnDescriptor):
    def __init__(
        self,
        name: str,
        image_key: str,
        text_key: str,
        editable: bool = False,
        color_col: int = -1,
        width: int = -1,
    ):
        self.name = name
        self.image_key = image_key
        self.text_key = text_key
        self.editable = editable
        self.color_col = color_col
        self.width = width


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
        model_cols = []
        col_map = []
        button_handlers = {}

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

        # Apply column widths
        for i, desc in enumerate(self._columns):
            if hasattr(desc, "width") and desc.width > 0:
                table.set_column_width(i, desc.width)

        self._model = model

        def on_data_event(event, index=0):
            def _notify():
                if event == "inserted":
                    model.row_inserted(index)
                elif event == "deleted":
                    model.row_deleted(index)
                elif event == "changed":
                    model.row_changed(index)
            core.queue_main(_notify)

        unsub = data.subscribe(on_data_event)
        self.unsubs.append(unsub)

        if self._on_row_clicked:
            table.on_row_clicked(self._on_row_clicked)
        if self._on_row_double_clicked:
            table.on_row_double_clicked(self._on_row_double_clicked)
        if self._on_header_clicked:
            table.on_header_clicked(self._on_header_clicked)
        if self._on_selection_changed:
            table.on_selection_changed(self._on_selection_changed)

        return table
