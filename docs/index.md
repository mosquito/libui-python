# libui-python

[![GitHub](https://img.shields.io/badge/GitHub-mosquito%2Flibui--python-blue?logo=github)](https://github.com/mosquito/libui-python)
[![CI](https://img.shields.io/github/actions/workflow/status/mosquito/libui-python/ci.yml?branch=master&logo=github-actions&logoColor=white&label=CI)](https://github.com/mosquito/libui-python/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](https://github.com/mosquito/libui-python/blob/master/LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%E2%80%933.14-blue?logo=python&logoColor=white)](https://pypi.org/project/libui/)
[![Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen)](https://github.com/mosquito/libui-python)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey)](https://github.com/mosquito/libui-python)
[![Native UI](https://img.shields.io/badge/UI-100%25%20native-ff69b4)](https://github.com/libui-ng/libui-ng)

Native GUI toolkit for Python. Lightweight bindings for [libui-ng](https://github.com/libui-ng/libui-ng) — real native widgets on Linux (GTK+3), macOS (Cocoa), and Windows (Win32).

No Electron. No web views. Just native controls.

## Features

- **30+ native widgets** — buttons, entries, sliders, tables, color pickers, drawing surfaces, and more
- **Declarative API** — reactive state, composable components, two-way data binding
- **Async-first** — built-in asyncio integration with thread-safe UI updates
- **Cross-platform** — one codebase, native look and feel everywhere

```{figure} tutorial/screenshots/showcase.png
:alt: Widget showcase
:target: _images/showcase.png
:class: screenshot
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

```{figure} tutorial/screenshots/00-hello-world.png
:alt: Quick example
:target: _images/00-hello-world.png
:class: screenshot
```

## Screenshots

Native look and feel on every platform — the same code, rendered with real OS widgets:

::::{grid} 1 1 3 3
:gutter: 3

:::{grid-item-card} macOS
:img-top: screenshots/showcase-macos.png
:link: _images/showcase-macos.png
Cocoa
:::

:::{grid-item-card} Linux
:img-top: screenshots/showcase-linux.png
:link: _images/showcase-linux.png
GTK+3
:::

:::{grid-item-card} Windows
:img-top: screenshots/showcase-windows.png
:link: _images/showcase-windows.png
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
