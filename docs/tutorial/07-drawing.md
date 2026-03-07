# Drawing

`DrawArea` provides a 2D drawing surface with paths, fills, strokes, gradients, transforms, and text.

## Basic shapes

The `on_draw` callback receives a drawing context and the area dimensions:

```{literalinclude} examples/17-drawing-shapes.py
```

```{figure} screenshots/17-drawing-shapes.png
:alt: Drawing shapes
:target: _images/17-drawing-shapes.png
:class: screenshot
```

The drawing workflow is:

1. Create a `DrawPath` and add geometry (rectangles, arcs, lines)
2. Call `path.end()` to close the path
3. Create a `DrawBrush` with color
4. Call `ctx.fill(path, brush)` or `ctx.stroke(path, brush, stroke_params)`

### Path methods

| Method | Description |
|---|---|
| `add_rectangle(x, y, w, h)` | Add a rectangle |
| `new_figure(x, y)` | Start a new sub-path at a point |
| `new_figure_with_arc(cx, cy, r, start, sweep, neg)` | Start with an arc |
| `line_to(x, y)` | Draw a line to a point |
| `bezier_to(c1x, c1y, c2x, c2y, ex, ey)` | Cubic bezier curve |
| `close_figure()` | Close the current sub-path |
| `end()` | Finalize the path (required before use) |

### Stroke parameters

`DrawStrokeParams` controls line appearance:

```python
sp = libui.DrawStrokeParams()
sp.thickness = 3.0
sp.cap = libui.LineCap.ROUND    # FLAT, ROUND, SQUARE
sp.join = libui.LineJoin.ROUND  # MITER, ROUND, BEVEL
sp.set_dashes([10.0, 5.0])     # dash pattern
```

## Gradients

Both linear and radial gradients are supported:

```{literalinclude} examples/18-drawing-gradients.py
```

```{figure} screenshots/18-drawing-gradients.png
:alt: Gradients
:target: _images/18-drawing-gradients.png
:class: screenshot
```

Gradient stops are tuples of `(position, r, g, b, a)` where position is 0.0 to 1.0.

## Styled text

`AttributedString` supports rich text with attributes for weight, color, style, and more:

```{literalinclude} examples/19-drawing-text.py
```

```{figure} screenshots/19-drawing-text.png
:alt: Styled text
:target: _images/19-drawing-text.png
:class: screenshot
```

### Text attributes

| Function | Description |
|---|---|
| `weight_attribute(weight)` | Font weight (e.g., `TextWeight.BOLD`) |
| `italic_attribute(style)` | Italic style (e.g., `TextItalic.ITALIC`) |
| `color_attribute(r, g, b, a)` | Text color |
| `background_attribute(r, g, b, a)` | Background highlight |
| `underline_attribute(style)` | Underline (e.g., `Underline.SINGLE`) |
| `family_attribute(name)` | Font family |
| `size_attribute(size)` | Font size in points |

## Transforms

Use `DrawMatrix` for translations, rotations, and scaling:

```python
matrix = libui.DrawMatrix()
matrix.set_identity()
matrix.rotate(center_x, center_y, degrees)
ctx.save()
ctx.transform(matrix)
# ... draw rotated content ...
ctx.restore()
```

## Mouse events

`DrawArea` supports mouse interaction through callbacks:

```python
DrawArea(
    on_draw=on_draw,
    on_mouse_event=on_mouse,       # click, drag, move
    on_mouse_crossed=on_crossed,   # enter/leave
)
```

The mouse event dict contains: `x`, `y`, `area_width`, `area_height`, `down`, `up`, `count`, `modifiers`, `held`.

Call `widget.queue_redraw_all()` to trigger a repaint after changes.

## ScrollingDrawArea

For content larger than the visible area, use `ScrollingDrawArea`:

```python
ScrollingDrawArea(
    on_draw=on_draw,
    width=2000,   # virtual canvas size
    height=2000,
)
```
