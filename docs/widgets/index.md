# Widget Reference

All widgets are available from `libui.declarative`. Widgets that accept `State` support automatic two-way binding (user input updates the state, state changes update the widget). Widgets that accept `Computed` or `State` for display-only props support one-way binding (state changes update the widget).

## Containers

### Window

```python
Window(
    title: str = "Application",
    width: int = 800,
    height: int = 600,
    child: Node | None = None,
    has_menubar: bool = False,
    margined: bool = True,
    on_closing: Callable | None = None,
)
```

Top-level window. Set `has_menubar=True` when using menus. The `on_closing` callback is called when the user closes the window; by default it quits the app.

### VBox / HBox

```python
VBox(*children: Node, padded: bool = True)
HBox(*children: Node, padded: bool = True)
```

Stack children vertically or horizontally. Use `stretchy(child)` to make a child fill available space.

### Group

```python
Group(
    title: str | State[str],
    child: Node,
    margined: bool = True,
)
```

Titled container with a border. `title` can be reactive.

### Form

```python
Form(*rows: tuple, padded: bool = True)
```

Two-column label + control layout. Each row is `(label, widget)` or `(label, widget, stretchy)`.

### Tab

```python
Tab(*pages: tuple[str, Node], margined: bool = True)
```

Tabbed container. Each page is `(page_name, widget)`.

### Grid / GridCell

```python
Grid(*cells: GridCell, padded: bool = True)

GridCell(
    child: Node,
    left: int,
    top: int,
    xspan: int = 1,
    yspan: int = 1,
    hexpand: bool = False,
    halign=Align.FILL,
    vexpand: bool = False,
    valign=Align.FILL,
)
```

Position-based grid layout. `Align` values: `FILL`, `START`, `CENTER`, `END`.

## Controls

### Label

```python
Label(text: str | State[str] | Computed[str] = "")
```

Static or reactive text display.

### Button

```python
Button(text: str = "", on_clicked: Callable | None = None)
```

Clickable button. `on_clicked` can be sync or async.

### Entry

```python
Entry(
    text: State[str] | str | None = None,
    type: str = "normal",          # "normal", "password", "search"
    read_only: State[bool] | bool = False,
    on_changed: Callable | None = None,
)
```

Single-line text input. Two-way binding when `text` is `State[str]`. The `on_changed` callback receives the new text as a string.

### MultilineEntry

```python
MultilineEntry(
    text: State[str] | str = "",
    wrapping: bool = True,
    read_only: State[bool] | bool = False,
    on_changed: Callable | None = None,
)
```

Multi-line text editor with optional word wrapping.

### Checkbox

```python
Checkbox(
    text: str = "",
    checked: State[bool] | bool = False,
    on_toggled: Callable | None = None,
)
```

Toggle checkbox. Two-way binding when `checked` is `State[bool]`. The `on_toggled` callback receives the new checked state as a boolean.

### Slider

```python
Slider(
    min: int = 0,
    max: int = 100,
    value: State[int] | int = 0,
    has_tooltip: bool = True,
    on_changed: Callable | None = None,
)
```

Horizontal slider. Two-way binding when `value` is `State[int]`. The `on_changed` callback receives the new value as an integer.

### Spinbox

```python
Spinbox(
    min: int = 0,
    max: int = 100,
    value: State[int] | int = 0,
    on_changed: Callable | None = None,
)
```

Numeric spinbox. Two-way binding when `value` is `State[int]`.

### ProgressBar

```python
ProgressBar(value: State[int] | Computed[int] | int = 0)
```

Progress indicator (0-100). One-way binding only.

### Combobox

```python
Combobox(
    items: Sequence[str] = (),
    selected: State[int] | int = 0,
    on_selected: Callable | None = None,
)
```

Drop-down selector. Two-way binding via `selected` index. The `on_selected` callback receives the selected index.

### EditableCombobox

```python
EditableCombobox(
    items: Sequence[str] = (),
    text: State[str] | str = "",
    on_changed: Callable | None = None,
)
```

Editable dropdown. Two-way binding via `text`.

### RadioButtons

```python
RadioButtons(
    items: Sequence[str] = (),
    selected: State[int] | int = -1,
    on_selected: Callable | None = None,
)
```

Mutually exclusive options. `-1` means nothing selected. Two-way binding via `selected`.

### ColorButton

```python
ColorButton(on_changed: Callable | None = None)
```

Color picker. The `on_changed` callback receives `(r, g, b, a)` as floats.

### FontButton

```python
FontButton(on_changed: Callable | None = None)
```

Font picker. The `on_changed` callback receives a dict with keys: `family`, `size`, `weight`, `italic`, `stretch`.

### DateTimePicker

```python
DateTimePicker(
    type: str = "datetime",    # "datetime", "date", "time"
    on_changed: Callable | None = None,
)
```

Date/time picker. The `on_changed` callback receives a tuple `(year, month, day, hour, minute, second, ...)`.

### Separator

```python
Separator(vertical: bool = False)
```

Visual divider line.

## Drawing

### DrawArea

```python
DrawArea(
    on_draw: Callable | None = None,
    on_mouse_event: Callable | None = None,
    on_mouse_crossed: Callable | None = None,
    on_drag_broken: Callable | None = None,
    on_key_event: Callable | None = None,
)
```

Custom 2D drawing surface. The `on_draw` callback signature:

```python
def on_draw(ctx, area_w, area_h, clip_x, clip_y, clip_w, clip_h):
    ...
```

### ScrollingDrawArea

```python
ScrollingDrawArea(
    on_draw: Callable | None = None,
    width: int = 1000,
    height: int = 1000,
    on_mouse_event: Callable | None = None,
    on_mouse_crossed: Callable | None = None,
    on_drag_broken: Callable | None = None,
    on_key_event: Callable | None = None,
)
```

Scrollable drawing surface with a virtual canvas size.

### Drawing types

| Type | Description |
|---|---|
| `libui.DrawPath` | Geometry path (rectangles, arcs, lines, beziers) |
| `libui.DrawBrush` | Fill/stroke color or gradient |
| `libui.DrawStrokeParams` | Line thickness, cap, join, dash pattern |
| `libui.DrawMatrix` | Affine transform (translate, rotate, scale, skew) |
| `libui.DrawTextLayout` | Formatted text layout |
| `libui.AttributedString` | Rich text with attributes |

## Tables

### DataTable

```python
DataTable(
    data: ListState,
    *columns: ColumnDescriptor,
    on_row_clicked: Callable | None = None,
    on_row_double_clicked: Callable | None = None,
    on_header_clicked: Callable | None = None,
    on_selection_changed: Callable | None = None,
)
```

Data grid backed by `ListState`. Each row is a dict; column descriptors define which keys to display.

### Column descriptors

```python
TextColumn(name, key, editable=False, color_col=-1, width=-1)
CheckboxColumn(name, key, editable=True, width=-1)
CheckboxTextColumn(name, checkbox_key, text_key,
                   checkbox_editable=True, text_editable=False,
                   text_color_col=-1, width=-1)
ProgressColumn(name, key, width=-1)
ButtonColumn(name, text_key, on_click=None, clickable=True, width=-1)
ImageColumn(name, key, width=-1)
ImageTextColumn(name, image_key, text_key, editable=False,
                color_col=-1, width=-1)
```

## Menus

```python
MenuDef(title: str, *items)

MenuItem(name: str, on_click: Callable | None = None)
CheckMenuItem(name: str, checked: State[bool] | None = None,
              on_click: Callable | None = None)
MenuSeparator()
QuitItem()
PreferencesItem()
AboutItem()
```

## State

```python
State(initial: T)           # mutable reactive container
Computed(source, fn)         # read-only derived value (use State.map())
ListState(initial: list[T])  # observable list for tables
```

## App

```python
app = App()
app.build(window=..., menus=...)
app.show()
await app.wait()

# Dialogs (sync)
app.msg_box(title, description)
app.msg_box_error(title, description)
app.open_file() -> str | None
app.open_folder() -> str | None
app.save_file() -> str | None

# Dialogs (async)
await app.msg_box_async(title, description)
await app.msg_box_error_async(title, description)
await app.open_file_async() -> str | None
await app.open_folder_async() -> str | None
await app.save_file_async() -> str | None
```

## Enumerations

| Enum | Values |
|---|---|
| `libui.Align` | `FILL`, `START`, `CENTER`, `END` |
| `libui.BrushType` | `SOLID`, `LINEAR_GRADIENT`, `RADIAL_GRADIENT` |
| `libui.LineCap` | `FLAT`, `ROUND`, `SQUARE` |
| `libui.LineJoin` | `MITER`, `ROUND`, `BEVEL` |
| `libui.TextWeight` | `THIN` ... `NORMAL` ... `BOLD` ... `MAXIMUM` |
| `libui.TextItalic` | `NORMAL`, `OBLIQUE`, `ITALIC` |
| `libui.Underline` | `NONE`, `SINGLE`, `DOUBLE`, `SUGGESTION` |
| `libui.SelectionMode` | `NONE`, `ONE`, `ZERO_OR_ONE`, `MULTI` |
| `libui.SortIndicator` | `NONE`, `ASCENDING`, `DESCENDING` |
| `libui.TableValueType` | `INT`, `STRING`, `IMAGE` |
| `libui.TableModelColumn` | `NEVER_EDITABLE`, `ALWAYS_EDITABLE` |
