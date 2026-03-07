# Quick Start

This page walks through a minimal libui-python application line by line.

## Your first app

Create a file called `hello.py`:

```{literalinclude} tutorial/examples/00-hello-world.py
```

Run it:

```bash
python hello.py
```

A native window appears with a label and a button. Clicking the button increments the counter.

<!-- screenshot placeholder -->
<!-- ```{image} tutorial/screenshots/00-hello-world.png
:alt: Hello world window
``` -->

## Line-by-line walkthrough

```python
import libui
from libui.declarative import App, Window, VBox, Label, Button, State
```

Import the library and the declarative building blocks. `State` is a reactive container that automatically updates bound widgets when its value changes.

```python
async def main():
    app = App()
```

The entry point is an `async` function. `App` manages the application lifecycle — menus, windows, and dialogs.

```python
    count = State(0)
```

Create a reactive state holding an integer. Any widget bound to this state will update automatically when it changes.

```python
    app.build(window=Window(
        "Hello", 400, 300,
        child=VBox(
            Label(text=count.map(lambda n: f"Count: {n}")),
            Button("Click me", on_clicked=lambda: count.update(lambda n: n + 1)),
        ),
    ))
```

Build the widget tree:
- `Window` creates a native window with a title and size
- `VBox` stacks children vertically
- `Label` displays text — `count.map(...)` creates a derived value that updates when `count` changes
- `Button` calls its `on_clicked` callback when pressed, which increments the count

```python
    app.show()
    await app.wait()
```

Show the window and wait until the user closes it.

```python
libui.run(main())
```

`libui.run()` starts the two-thread architecture: the main thread pumps the native UI event loop while an asyncio loop runs your coroutine on a background thread.

## Next steps

- Follow the {doc}`tutorial <tutorial/index>` for a progressive guide through all features
- Read {doc}`concepts` to understand the architecture
- Browse the {doc}`widgets/index` for a complete widget reference
