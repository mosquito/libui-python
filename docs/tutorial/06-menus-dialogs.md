# Menus and Dialogs

## Menus

Menus are defined with `MenuDef` and passed to `app.build()`. They must be created before the window (a libui-ng requirement):

```{literalinclude} examples/15-menus.py
```

```{image} screenshots/15-menus.png
:alt: Menus
```

### Menu item types

| Type | Description |
|---|---|
| `MenuItem(name, on_click=...)` | Regular clickable item |
| `CheckMenuItem(name, checked=..., on_click=...)` | Checkable item, optionally bound to `State[bool]` |
| `MenuSeparator()` | Visual separator line |
| `QuitItem()` | Platform quit item (Cmd+Q / Alt+F4) |
| `PreferencesItem()` | Platform preferences item |
| `AboutItem()` | Platform about item |

Set `has_menubar=True` on the `Window` to display the menu bar.

## Dialogs

`App` provides dialog methods for file selection and message boxes:

```{literalinclude} examples/16-dialogs.py
```

<!-- No screenshot — this example opens interactive system dialogs -->

### Sync vs async dialogs

Dialog methods come in two flavors:

| Sync (from main thread callbacks) | Async (from coroutines) |
|---|---|
| `app.open_file()` | `await app.open_file_async()` |
| `app.open_folder()` | `await app.open_folder_async()` |
| `app.save_file()` | `await app.save_file_async()` |
| `app.msg_box(title, text)` | `await app.msg_box_async(title, text)` |
| `app.msg_box_error(title, text)` | `await app.msg_box_error_async(title, text)` |

Use sync methods inside `on_clicked` lambdas (which run on the main thread). Use async methods inside `async def` callbacks.

File dialog methods return a path string, or `None` if the user cancelled.
