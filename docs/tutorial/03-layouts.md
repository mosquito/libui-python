# Layouts

libui-python provides several containers for arranging widgets. This chapter covers all of them.

## VBox and HBox

`VBox` stacks children vertically, `HBox` horizontally. Use `stretchy()` to make a child fill available space:

```{literalinclude} examples/03-vbox-hbox.py
```

```{image} screenshots/03-vbox-hbox.png
:alt: VBox and HBox layout
```

## Form

`Form` creates a two-column layout with labels on the left and controls on the right:

```{literalinclude} examples/04-form-layout.py
```

```{image} screenshots/04-form-layout.png
:alt: Form layout
```

Each row is a tuple: `(label, widget)` or `(label, widget, stretchy)`.

## Tab

`Tab` creates a tabbed container. Each page is a `(name, widget)` tuple:

```{literalinclude} examples/05-tabs.py
```

```{image} screenshots/05-tabs.png
:alt: Tab container
```

## Grid

`Grid` places children at exact (column, row) coordinates with optional spanning — useful for keypad-style layouts and other 2D arrangements that `VBox`/`HBox`/`Form` cannot express:

```{literalinclude} examples/06-grid-layout.py
```

```{image} screenshots/06-grid-layout.png
:alt: Grid layout
```

Key `GridCell` parameters:

| Parameter | Description |
|---|---|
| `left`, `top` | Grid position (zero-based) |
| `xspan`, `yspan` | How many columns/rows to span |
| `hexpand`, `vexpand` | Whether to expand to fill space |
| `halign`, `valign` | Alignment within the cell (`Align.FILL`, `START`, `CENTER`, `END`) |

:::{note}
On macOS, `Grid` cells do not expand horizontally even with `hexpand=True` — this is a known [libui-ng upstream bug](https://github.com/libui-ng/libui-ng) in the Cocoa backend's Auto Layout constraints. `vexpand` works correctly. For label + control forms that need to stretch horizontally, use `Form` instead. Grid works well for fixed-size coordinate layouts like keypads and toolbars.
:::

## Group

`Group` wraps a single child with a titled border. Combine with other containers for labeled sections:

```python
Group("Connection Settings", child=Form(
    ("Host:", Entry()),
    ("Port:", Entry()),
), margined=True)
```

## stretchy

`stretchy(node)` marks a child as expandable in `VBox` or `HBox`. Without it, children take only their natural size. Only children marked stretchy will grow to fill available space.

```python
VBox(
    Label("Fixed size"),
    stretchy(MultilineEntry()),  # fills remaining space
    Button("Also fixed"),
)
```
