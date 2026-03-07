# Async

libui-python has first-class asyncio support. Your application runs as an async function, and event callbacks can be either sync or async.

## Background tasks

Use `asyncio.create_task()` to run background work while the UI stays responsive:

```{literalinclude} examples/20-async-background.py
```

```{image} screenshots/20-async-background.png
:alt: Background tasks
```

The proxy layer handles thread safety — you can set widget properties from async code without worrying about which thread you're on.

## Async callbacks

Event handlers can be `async def` functions. The framework automatically schedules them on the asyncio loop:

```{literalinclude} examples/21-async-callbacks.py
```

```{image} screenshots/21-async-callbacks.png
:alt: Async callbacks
```

Key points:

- Sync callbacks run immediately on the main thread
- Async callbacks are scheduled on the asyncio event loop (background thread)
- Both types can safely update widget properties through the proxy layer
- Use `await app.msg_box_async(...)` instead of `app.msg_box(...)` from async callbacks

## How it works

`libui.run(coro)` creates a two-thread architecture:

```
Main thread                    Background thread
  |                              |
  |-- init libui                 |
  |-- pump main_step()    <-->   |-- asyncio.run(coro)
  |     ^                        |     |
  |     |-- queue_main(fn) ------|-----|
  |                              |
  |-- cleanup                    |-- done
```

- **Main thread**: owns the native UI event loop
- **Background thread**: runs your `async def main()` coroutine
- **`queue_main(fn)`**: enqueues a function to run on the main thread
- **Proxy layer**: automatically dispatches property access through `queue_main`

## Cross-thread helpers

For advanced use cases with `libui.core` directly:

```python
from libui.loop import invoke_on_main, invoke_on_main_async

# Blocking (from sync code on any thread):
result = invoke_on_main(core_function, arg1, arg2)

# Non-blocking (from async code):
result = await invoke_on_main_async(core_function, arg1, arg2)
```
