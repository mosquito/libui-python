# Building an App

This chapter puts everything together into a complete application — a contact manager with a table, editor form, menus, async I/O, and reactive state.

## The full example

```{literalinclude} examples/22-full-app.py
```

```{image} screenshots/22-full-app.png
:alt: Full application
```

## Patterns used

### Reusable components as functions

Break your UI into functions that return `Node` trees:

```python
def build_editor(contacts, status):
    name = State("")
    # ... local state and logic ...
    return VBox(
        Form(("Name:", Entry(text=name))),
        Button("Save", on_clicked=save),
    )
```

Each function encapsulates its own local state and callbacks. The caller passes in shared state.

### Shared state across components

Pass `State` and `ListState` objects to multiple components to connect them:

```python
contacts = ListState([...])
status = State("Ready.")
editing_index = State(-1)

editor = build_editor(contacts, status, editing_index)
table_view = build_list(contacts, status, editing_index)
```

When one component modifies the shared state, all others update automatically.

### Async I/O with progress

Combine async callbacks with `State[int]` for progress tracking:

```python
progress = State(0)

async def do_save():
    path = await app.save_file_async()
    if not path:
        return
    for i, item in enumerate(data):
        await process(item)
        progress.set(int((i + 1) / len(data) * 100))
    progress.set(0)
```

Bind `progress` to a `ProgressBar` in the UI for visual feedback.

### Menu-driven actions

Menus trigger both sync and async operations:

```python
menus = [
    MenuDef("File",
        MenuItem("Export...", on_click=do_export),   # async ok
        MenuItem("Stats", on_click=do_stats),        # sync ok
        MenuSeparator(),
        QuitItem(),
    ),
]
```

## Next steps

- See `examples/showcase.py` for a complete widget gallery
- See `examples/contacts.py` for the full-featured contacts app
- Browse the {doc}`../widgets/index` for all available widgets
- Read {doc}`../concepts` for architecture details
