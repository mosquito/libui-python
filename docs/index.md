# libui-python

Native GUI toolkit for Python. Lightweight bindings for [libui-ng](https://github.com/libui-ng/libui-ng) — real native widgets on Linux (GTK+3), macOS (Cocoa), and Windows (Win32).

No Electron. No web views. Just native controls.

## Features

- **30+ native widgets** — buttons, entries, sliders, tables, color pickers, drawing surfaces, and more
- **Declarative API** — reactive state, composable components, two-way data binding
- **Async-first** — built-in asyncio integration with thread-safe UI updates
- **Cross-platform** — one codebase, native look and feel everywhere

```{image} tutorial/screenshots/showcase.png
:alt: Widget showcase
```

## Quick example

```python
import libui
from libui.declarative import App, Window, VBox, Label, Button, State

async def main():
    app = App()
    count = State(0)

    app.build(window=Window(
        "Hello", 400, 300,
        child=VBox(
            Label(text=count.map(lambda n: f"Count: {n}")),
            Button("Click me", on_clicked=lambda: count.update(lambda n: n + 1)),
        ),
    ))

    app.show()
    await app.wait()

libui.run(main())
```

```{image} tutorial/screenshots/00-hello-world.png
:alt: Quick example
```

## Screenshots

Native look and feel on every platform — the same code, rendered with real OS widgets:

::::{grid} 1 1 3 3
:gutter: 3

:::{grid-item-card} macOS
:img-top: screenshots/showcase-macos.png
Cocoa
:::

:::{grid-item-card} Linux
:img-top: screenshots/showcase-linux.png
GTK+3
:::

:::{grid-item-card} Windows
:img-top: screenshots/showcase-windows.png
Win32
:::

::::

```{toctree}
:maxdepth: 2
:caption: Getting Started

installation
quickstart
concepts
```

```{toctree}
:maxdepth: 2
:caption: Tutorial

tutorial/index
```

```{toctree}
:maxdepth: 2
:caption: Reference

widgets/index
api/index
changelog
```
