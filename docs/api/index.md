# API Reference

## Module structure

```
libui
├── core          # C extension — low-level bindings to libui-ng
├── loop          # Threading model — run(), invoke_on_main(), etc.
├── state         # Reactive state — State, Computed, ListState
├── node          # Node base class, BuildContext, stretchy, make_two_way
├── declarative   # High-level API — App, Window, MenuDef, all widget nodes
│   ├── app       # App, Window, MenuDef, MenuItem, etc.
│   └── ...
└── widgets       # Individual widget node implementations
    ├── containers  # VBox, HBox, Group, Form, Tab, Grid
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

- `libui.run(coro)` — Start the two-thread architecture and run your async function
- `libui.quit()` — Stop the UI event loop (thread-safe)

## `libui.declarative`

The declarative module provides all building blocks for the recommended API:

```python
from libui.declarative import App, Window, VBox, Label, Button, State
```

See the {doc}`../widgets/index` for complete widget documentation.

### Exports

**App & Window:** `App`, `Window`

**Containers:** `VBox`, `HBox`, `Group`, `Form`, `Tab`, `Grid`, `GridCell`

**Controls:** `Label`, `Button`, `Entry`, `MultilineEntry`, `Checkbox`, `Slider`, `Spinbox`, `ProgressBar`, `Combobox`, `EditableCombobox`, `RadioButtons`, `ColorButton`, `FontButton`, `DateTimePicker`, `Separator`

**Drawing:** `DrawArea`, `ScrollingDrawArea`

**Tables:** `DataTable`, `ListState`, `TextColumn`, `CheckboxColumn`, `CheckboxTextColumn`, `ProgressColumn`, `ButtonColumn`, `ImageColumn`, `ImageTextColumn`

**Menus:** `MenuDef`, `MenuItem`, `CheckMenuItem`, `MenuSeparator`, `QuitItem`, `PreferencesItem`, `AboutItem`

**State:** `State`, `Computed`, `ListState`

**Helpers:** `stretchy`

## `libui.state`

### `State[T]`

| Method | Description |
|---|---|
| `State(initial)` | Create with initial value |
| `.value` | Get/set current value |
| `.get()` | Get current value |
| `.set(new)` | Set value and notify |
| `.update(fn)` | Apply `fn(current) -> new` and notify |
| `.subscribe(cb)` | Add subscriber, returns unsubscribe function |
| `.unsubscribe(cb)` | Remove subscriber |
| `.map(fn)` | Create `Computed` derived value |

### `Computed[T]`

| Method | Description |
|---|---|
| `.value` | Get current computed value (read-only) |
| `.get()` | Get current computed value |
| `.subscribe(cb)` | Add subscriber |
| `.unsubscribe(cb)` | Remove subscriber |
| `.map(fn)` | Chain another derived value |

### `ListState[T]`

| Method | Description |
|---|---|
| `ListState(initial)` | Create with initial list |
| `.append(item)` | Add item, notify with `event="inserted"` |
| `.pop(index=-1)` | Remove item, notify with `event="deleted"` |
| `[index]` | Get item |
| `[index] = value` | Set item, notify with `event="changed"` |
| `len()` | Get length |
| `.subscribe(cb)` | Add subscriber for change events |

## `libui.loop`

| Function | Description |
|---|---|
| `run(coro)` | Start UI + asyncio event loops |
| `quit()` | Stop the event loop |
| `invoke_on_main(fn, *args, **kwargs)` | Run `fn` on main thread, block for result |
| `invoke_on_main_async(fn, *args, **kwargs)` | Run `fn` on main thread, return awaitable |

## `libui.core`

The C extension module. Provides direct access to libui-ng widgets without thread-safety wrappers. All functions (except `queue_main` and `quit`) must be called from the main thread.

| Function | Thread-safe | Description |
|---|---|---|
| `core.init()` | No | Initialize libui |
| `core.uninit()` | No | Clean up libui |
| `core.main()` | No | Run the main event loop |
| `core.main_step(wait)` | No | Process one event |
| `core.main_steps()` | No | Process pending events |
| `core.quit()` | Yes | Stop the event loop |
| `core.queue_main(fn)` | Yes | Enqueue function for main thread |
| `core.is_main_thread()` | Yes | Check if on main thread |
