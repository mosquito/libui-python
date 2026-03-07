# Hello World

Every libui-python application follows the same pattern: create an `App`, build a widget tree, show the window, and wait.

## A window with a button

```{literalinclude} examples/00-hello-world.py
```

```{image} screenshots/00-hello-world.png
:alt: Hello world window
```

Key points:

- `async def main()` — your app runs as an async function
- `App()` — manages the application lifecycle
- `State(0)` — a reactive container; bound widgets auto-update
- `count.map(...)` — derives a read-only computed value
- `count.update(...)` — transforms the value and notifies subscribers
- `libui.run(main())` — starts the UI event loop and asyncio

The `Window` takes a title, width, height, and a single `child` widget. `VBox` stacks its children vertically.
