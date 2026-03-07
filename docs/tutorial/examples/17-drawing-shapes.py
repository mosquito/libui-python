"""Drawing shapes — rectangles, circles, triangles, and strokes."""
import math
import libui
from libui.declarative import App, Window, VBox, DrawArea, stretchy


def on_draw(ctx, area_w, area_h, clip_x, clip_y, clip_w, clip_h):
    # Filled rectangle
    path = libui.DrawPath()
    path.add_rectangle(20, 20, 200, 100)
    path.end()

    blue = libui.DrawBrush()
    blue.r, blue.g, blue.b, blue.a = 0.2, 0.4, 0.8, 1.0
    ctx.fill(path, blue)

    # Stroked circle
    circle = libui.DrawPath()
    circle.new_figure_with_arc(350, 70, 50, 0, 2 * math.pi, False)
    circle.end()

    red = libui.DrawBrush()
    red.r, red.g, red.b, red.a = 0.8, 0.2, 0.2, 1.0

    stroke = libui.DrawStrokeParams()
    stroke.thickness = 3.0
    stroke.cap = libui.LineCap.ROUND
    ctx.stroke(circle, red, stroke)

    # Filled triangle
    tri = libui.DrawPath()
    tri.new_figure(20, 200)
    tri.line_to(120, 140)
    tri.line_to(220, 200)
    tri.close_figure()
    tri.end()

    green = libui.DrawBrush()
    green.r, green.g, green.b, green.a = 0.2, 0.7, 0.3, 1.0
    ctx.fill(tri, green)

    # Bezier curve
    bezier = libui.DrawPath()
    bezier.new_figure(250, 200)
    bezier.bezier_to(300, 120, 400, 220, 450, 150)
    bezier.end()

    purple = libui.DrawBrush()
    purple.r, purple.g, purple.b, purple.a = 0.5, 0.0, 0.7, 1.0

    sp = libui.DrawStrokeParams()
    sp.thickness = 2.5
    sp.cap = libui.LineCap.ROUND
    ctx.stroke(bezier, purple, sp)


async def main():
    app = App()

    app.build(window=Window(
        "Drawing Shapes", 500, 250,
        child=VBox(stretchy(DrawArea(on_draw=on_draw))),
    ))

    app.show()
    await app.wait()


libui.run(main())
