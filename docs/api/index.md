# API Reference

## Module structure

```
libui
├── core            # C extension — low-level bindings to libui-ng
├── loop            # Threading model — run(), invoke_on_main(), etc.
├── state           # Reactive state — State, Computed, ListState
├── node            # Node base class, BuildContext, stretchy
├── declarative     # High-level API — re-exports everything below
│   └── app         # App, Window, MenuDef, MenuItem, etc.
└── widgets         # Individual widget node implementations
    ├── containers  # VBox, HBox, Group, Form, Tab, Grid, GridCell
    ├── button      # Button
    ├── label       # Label
    ├── entry       # Entry, MultilineEntry
    ├── checkbox    # Checkbox
    ├── slider      # Slider
    ├── spinbox     # Spinbox
    ├── progressbar # ProgressBar
    ├── combobox    # Combobox, EditableCombobox
    ├── radiobuttons # RadioButtons
    ├── pickers     # ColorButton, FontButton, DateTimePicker
    ├── separator   # Separator
    ├── draw        # DrawArea, ScrollingDrawArea
    └── table       # DataTable, column descriptors
```

## `libui` (top-level)

The top-level `libui` module re-exports thread-safe proxy classes for the imperative API:

```python
import libui

window = libui.Window("Title", 400, 300)
button = libui.Button("Click")
label = libui.Label("Hello")
# ... etc
```

These are proxy wrappers around `libui.core` objects that automatically dispatch mutations to the main thread.

### Functions

- {func}`libui.loop.run` — Start the two-thread architecture and run your async function
- {func}`libui.loop.quit` — Stop the UI event loop (thread-safe)

## `libui.declarative`

The declarative module provides all building blocks for the recommended API:

```python
from libui.declarative import App, Window, VBox, Label, Button, State
```

See the {doc}`../widgets/index` for complete widget documentation.

### Exports

**App & Window:** {class}`~libui.declarative.app.App`, {class}`~libui.declarative.app.Window`

**Containers:** {class}`~libui.widgets.containers.VBox`, {class}`~libui.widgets.containers.HBox`, {class}`~libui.widgets.containers.Group`, {class}`~libui.widgets.containers.Form`, {class}`~libui.widgets.containers.Tab`, {class}`~libui.widgets.containers.Grid`, {class}`~libui.widgets.containers.GridCell`

**Controls:** {class}`~libui.widgets.label.Label`, {class}`~libui.widgets.button.Button`, {class}`~libui.widgets.entry.Entry`, {class}`~libui.widgets.entry.MultilineEntry`, {class}`~libui.widgets.checkbox.Checkbox`, {class}`~libui.widgets.slider.Slider`, {class}`~libui.widgets.spinbox.Spinbox`, {class}`~libui.widgets.progressbar.ProgressBar`, {class}`~libui.widgets.combobox.Combobox`, {class}`~libui.widgets.combobox.EditableCombobox`, {class}`~libui.widgets.radiobuttons.RadioButtons`, {class}`~libui.widgets.pickers.ColorButton`, {class}`~libui.widgets.pickers.FontButton`, {class}`~libui.widgets.pickers.DateTimePicker`, {class}`~libui.widgets.separator.Separator`

**Drawing:** {class}`~libui.widgets.draw.DrawArea`, {class}`~libui.widgets.draw.ScrollingDrawArea`

**Tables:** {class}`~libui.widgets.table.DataTable`, {class}`~libui.state.ListState`, {class}`~libui.widgets.table.TextColumn`, {class}`~libui.widgets.table.CheckboxColumn`, {class}`~libui.widgets.table.CheckboxTextColumn`, {class}`~libui.widgets.table.ProgressColumn`, {class}`~libui.widgets.table.ButtonColumn`, {class}`~libui.widgets.table.ImageColumn`, {class}`~libui.widgets.table.ImageTextColumn`

**Menus:** {class}`~libui.declarative.app.MenuDef`, {class}`~libui.declarative.app.MenuItem`, {class}`~libui.declarative.app.CheckMenuItem`, {class}`~libui.declarative.app.MenuSeparator`, {class}`~libui.declarative.app.QuitItem`, {class}`~libui.declarative.app.PreferencesItem`, {class}`~libui.declarative.app.AboutItem`

**State:** {class}`~libui.state.State`, {class}`~libui.state.Computed`, {class}`~libui.state.ListState`

**Helpers:** {func}`~libui.node.stretchy`

## `libui.state`

### {class}`~libui.state.State`

| Method | Description |
|---|---|
| {meth}`~libui.state.State.get` | Get current value |
| {meth}`~libui.state.State.set` | Set value and notify |
| {meth}`~libui.state.State.update` | Apply `fn(current) -> new` and notify |
| {meth}`~libui.state.State.subscribe` | Add subscriber, returns unsubscribe function |
| {meth}`~libui.state.State.unsubscribe` | Remove subscriber |
| {meth}`~libui.state.State.map` | Create {class}`~libui.state.Computed` derived value |

### {class}`~libui.state.Computed`

| Method | Description |
|---|---|
| {meth}`~libui.state.Computed.get` | Get current computed value |
| {meth}`~libui.state.Computed.subscribe` | Add subscriber |
| {meth}`~libui.state.Computed.unsubscribe` | Remove subscriber |
| {meth}`~libui.state.Computed.map` | Chain another derived value |

### {class}`~libui.state.ListState`

| Method | Description |
|---|---|
| {meth}`~libui.state.ListState.append` | Add item, notify with `event="inserted"` |
| {meth}`~libui.state.ListState.pop` | Remove item, notify with `event="deleted"` |
| {meth}`~libui.state.ListState.subscribe` | Add subscriber for change events |

## `libui.loop`

| Function | Description |
|---|---|
| {func}`~libui.loop.run` | Start UI + asyncio event loops |
| {func}`~libui.loop.quit` | Stop the event loop |
| {func}`~libui.loop.invoke_on_main` | Run `fn` on main thread, block for result |
| {func}`~libui.loop.invoke_on_main_async` | Run `fn` on main thread, return awaitable |

## `libui.core`

The C extension module. Provides direct access to libui-ng widgets without thread-safety wrappers. All functions (except `queue_main` and `quit`) must be called from the main thread.

### Functions

| Function | Thread-safe | Description |
|---|---|---|
| {func}`~libui.core.init` | No | Initialize libui |
| {func}`~libui.core.uninit` | No | Clean up libui |
| {func}`~libui.core.main` | No | Run the main event loop (blocking) |
| {func}`~libui.core.main_steps` | No | Enable stepping mode |
| {func}`~libui.core.main_step` | No | Process one event (requires `main_steps()` first) |
| {func}`~libui.core.quit` | Yes | Stop the event loop |
| {func}`~libui.core.queue_main` | Yes | Enqueue function for main thread |
| {func}`~libui.core.is_main_thread` | Yes | Check if on main thread |
| {func}`~libui.core.on_should_quit` | No | Register quit handler |

### Dialogs

| Function | Description |
|---|---|
| {func}`~libui.core.open_file` | Show file open dialog, returns path or `None` |
| {func}`~libui.core.open_folder` | Show folder open dialog, returns path or `None` |
| {func}`~libui.core.save_file` | Show file save dialog, returns path or `None` |
| {func}`~libui.core.msg_box` | Show info message box |
| {func}`~libui.core.msg_box_error` | Show error message box |

### Text attributes

| Function | Description |
|---|---|
| {func}`~libui.core.family_attribute` | Font family attribute |
| {func}`~libui.core.size_attribute` | Font size attribute |
| {func}`~libui.core.weight_attribute` | Font weight attribute |
| {func}`~libui.core.italic_attribute` | Italic style attribute |
| {func}`~libui.core.stretch_attribute` | Font stretch attribute |
| {func}`~libui.core.color_attribute` | Text color attribute |
| {func}`~libui.core.background_attribute` | Background color attribute |
| {func}`~libui.core.underline_attribute` | Underline style attribute |
| {func}`~libui.core.underline_color_attribute` | Underline color attribute |
| {func}`~libui.core.features_attribute` | OpenType features attribute |

### Types

| Type | Description |
|---|---|
| {class}`~libui.core.Window` | Top-level window |
| {class}`~libui.core.Button` | Clickable button |
| {class}`~libui.core.Label` | Text label |
| {class}`~libui.core.Box` | Vertical/horizontal container |
| {class}`~libui.core.Entry` | Text input |
| {class}`~libui.core.Checkbox` | Toggle checkbox |
| {class}`~libui.core.Combobox` | Dropdown selector |
| {class}`~libui.core.EditableCombobox` | Editable dropdown |
| {class}`~libui.core.RadioButtons` | Radio button group |
| {class}`~libui.core.Tab` | Tabbed container |
| {class}`~libui.core.Group` | Titled container |
| {class}`~libui.core.Form` | Label + control pairs |
| {class}`~libui.core.Grid` | Grid layout |
| {class}`~libui.core.Spinbox` | Numeric spinner |
| {class}`~libui.core.Slider` | Range slider |
| {class}`~libui.core.ProgressBar` | Progress indicator |
| {class}`~libui.core.Separator` | Visual divider |
| {class}`~libui.core.MultilineEntry` | Multi-line text editor |
| {class}`~libui.core.DateTimePicker` | Date/time picker |
| {class}`~libui.core.ColorButton` | Color picker |
| {class}`~libui.core.FontButton` | Font picker |
| {class}`~libui.core.Menu` | Menu bar entry |
| {class}`~libui.core.MenuItem` | Menu item |
| {class}`~libui.core.DrawPath` | Geometry path |
| {class}`~libui.core.DrawBrush` | Fill/stroke brush |
| {class}`~libui.core.DrawStrokeParams` | Stroke parameters |
| {class}`~libui.core.DrawMatrix` | Affine transform |
| {class}`~libui.core.DrawTextLayout` | Formatted text layout |
| {class}`~libui.core.AttributedString` | Rich text with attributes |
| {class}`~libui.core.OpenTypeFeatures` | OpenType feature set |
| {class}`~libui.core.Image` | Image for tables |
| {class}`~libui.core.TableModel` | Table data model |
| {class}`~libui.core.Table` | Data table widget |
| {class}`~libui.core.Area` | Custom drawing surface |
| {class}`~libui.core.ScrollingArea` | Scrollable drawing surface |

## Full API docs

```{toctree}
:maxdepth: 2

core
state
loop
node
declarative
widgets
```
