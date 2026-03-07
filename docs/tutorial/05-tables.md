# Tables

`DataTable` displays tabular data backed by a `ListState`. Mutations to the list automatically update the UI.

## Basic table

```{literalinclude} examples/12-table-basic.py
```

```{figure} screenshots/12-table-basic.png
:alt: Basic table
:target: _images/12-table-basic.png
:class: screenshot
```

Each row is a dictionary. Column descriptors map dictionary keys to table columns:

- `TextColumn("Name", key="name")` — displays `row["name"]` as text
- `ProgressColumn("Score", key="score")` — displays `row["score"]` as a progress bar (0-100)

## Editable table

Columns can be made editable so users can modify data in place:

```{literalinclude} examples/13-table-editable.py
```

```{figure} screenshots/13-table-editable.png
:alt: Editable table
:target: _images/13-table-editable.png
:class: screenshot
```

`TextColumn(..., editable=True)` allows inline text editing. `CheckboxColumn` and `CheckboxTextColumn` support editable checkboxes.

## Button columns

`ButtonColumn` renders a clickable button in each row. The `on_click` callback receives the row index:

```{literalinclude} examples/14-table-buttons.py
```

```{figure} screenshots/14-table-buttons.png
:alt: Table with buttons
:target: _images/14-table-buttons.png
:class: screenshot
```

## Column types reference

| Column | Description | Key parameters |
|---|---|---|
| `TextColumn` | Text display/edit | `key`, `editable`, `color_col` |
| `CheckboxColumn` | Checkbox | `key`, `editable` |
| `CheckboxTextColumn` | Checkbox + text | `checkbox_key`, `text_key`, `checkbox_editable`, `text_editable` |
| `ProgressColumn` | Progress bar (0-100) | `key` |
| `ButtonColumn` | Clickable button | `text_key`, `on_click`, `clickable` |
| `ImageColumn` | Image display | `key` |
| `ImageTextColumn` | Image + text | `image_key`, `text_key`, `editable` |

## Table events

`DataTable` supports several event callbacks:

```python
DataTable(
    data,
    *columns,
    on_row_clicked=lambda row: ...,          # single click
    on_row_double_clicked=lambda row: ...,   # double click
    on_header_clicked=lambda col: ...,       # header click
    on_selection_changed=lambda: ...,        # selection change
)
```

## Dynamic updates

Since `DataTable` is backed by `ListState`, any mutation automatically updates the UI:

```python
data.append({"name": "New item", "score": 50})  # row appears
data[0] = {"name": "Updated", "score": 99}       # row updates
data.pop()                                         # row disappears
```
