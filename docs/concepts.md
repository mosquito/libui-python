# Concepts

This page explains the key architectural ideas behind libui-python.

## Three-layer design

libui-python has three layers, from lowest to highest:

1. **C extension (`libui.core`)** — Direct CPython wrappers around the libui-ng C API. Each widget has its own C file. This layer is fast but not thread-safe on its own.

2. **Thread-safe proxy layer (`libui`)** — Python classes like `libui.Window`, `libui.Button` that wrap core objects. All mutations are dispatched to the main thread via `core.queue_main()`. Properties use a cache: reads come from the Python side, writes update the cache and queue the C setter.

3. **Declarative layer (`libui.declarative`)** — High-level API with reactive `State`, a `Node` tree that builds into core widgets, and an `App` class managing the full lifecycle. This is the recommended way to build UIs.

## Reactive state

### State

`State[T]` is a reactive container. When its value changes, all subscribers and bound widgets update automatically:

```python
name = State("World")
name.value = "Python"       # triggers subscribers
name.set("libui")           # same thing
name.update(lambda s: s.upper())  # transform in place
```

### Computed

`Computed[T]` is a read-only derived state created via `.map()`:

```python
greeting = name.map(lambda n: f"Hello, {n}!")
# greeting.value is always in sync with name
```

Computed values can be chained:

```python
upper_greeting = greeting.map(str.upper)
```

### ListState

`ListState[T]` is an observable list for table data:

```python
data = ListState([{"name": "Alice"}, {"name": "Bob"}])
data.append({"name": "Carol"})  # notifies subscribers with event="inserted"
data[0] = {"name": "Alicia"}    # notifies with event="changed"
data.pop()                       # notifies with event="deleted"
```

`DataTable` binds directly to `ListState` — mutations automatically update the table UI.

## Threading model

### Two-thread architecture

`libui.run(coro)` starts two threads:

- **Main thread** — initializes libui, pumps the native event loop via `main_step(wait=True)` in a loop
- **Background thread** — runs `asyncio.run(coro)` with your application logic

This separation keeps the UI responsive while async code runs freely.

### Cross-thread communication

| Function | Direction | Blocking? |
|---|---|---|
| `core.queue_main(fn)` | any thread -> main | No (fire-and-forget) |
| `invoke_on_main(fn)` | any thread -> main | Yes (waits for result) |
| `invoke_on_main_async(fn)` | asyncio -> main | No (returns awaitable) |

The proxy layer and declarative layer use these internally — you rarely need them directly unless working with `libui.core`.

### Safety guards

Every C API function checks the calling thread at runtime. If called from the wrong thread, you get a clear `RuntimeError` instead of a native crash:

```
RuntimeError: this function must be called from the main UI thread
```

Exceptions: `queue_main` (cross-thread by design) and `quit` (thread-safe).

## Node tree and build lifecycle

In the declarative API, you describe your UI as a tree of `Node` objects:

```python
Window("Title", 400, 300, child=VBox(
    Label("Hello"),
    Button("Click"),
))
```

When `app.build()` is called, each node goes through:

1. `create_widget()` — instantiate the core widget
2. `bind_props()` — subscribe State/Computed values to widget properties
3. `attach_callbacks()` — register event handlers (async callbacks are auto-wrapped)
4. `attach_children()` — recursively build and attach child nodes

State bindings created during build auto-update the widget whenever the state changes. Two-way bindings (e.g., `Entry(text=some_state)`) update in both directions: state changes update the widget, and user input updates the state.

## Async callbacks

Event handlers can be either sync or async functions:

```python
# Sync — runs on the main thread
Button("Save", on_clicked=lambda: status.set("Saved!"))

# Async — scheduled on the asyncio loop
async def on_click():
    status.set("Loading...")
    await asyncio.sleep(1)
    status.set("Done!")

Button("Load", on_clicked=on_click)
```

The framework detects async callbacks and wraps them with `_ensure_sync()`, which schedules the coroutine on the asyncio event loop via `call_soon_threadsafe()`.
