"""Example: Custom drawing with Area widget."""

import math
import libui
from libui import core


def on_draw(ctx, area_width, area_height, clip_x, clip_y, clip_w, clip_h):
    # Draw a red rectangle
    path = core.DrawPath()
    path.add_rectangle(10, 10, 200, 100)
    path.end()

    brush = core.DrawBrush()
    brush.r = 0.8
    brush.g = 0.2
    brush.b = 0.2
    brush.a = 1.0

    ctx.fill(path, brush)

    # Draw a blue stroked circle
    circle = core.DrawPath()
    circle.new_figure_with_arc(160, 200, 50, 0, 2 * math.pi, False)
    circle.end()

    blue_brush = core.DrawBrush()
    blue_brush.r = 0.2
    blue_brush.g = 0.2
    blue_brush.b = 0.8
    blue_brush.a = 1.0

    stroke_params = core.DrawStrokeParams()
    stroke_params.thickness = 3.0

    ctx.stroke(circle, blue_brush, stroke_params)

    # Draw text
    astr = core.AttributedString("Hello from libui!")
    bold = core.weight_attribute(core.TextWeight.BOLD)
    astr.set_attribute(bold, 0, 5)

    color = core.color_attribute(0.0, 0.5, 0.0, 1.0)
    astr.set_attribute(color, 6, 17)

    font = {"family": "sans-serif", "size": 18.0}
    layout = core.DrawTextLayout(astr, font, area_width)
    ctx.text(layout, 10, 130)


async def main():
    w = core.Window("Drawing Example", 400, 350, False)
    area = core.Area(on_draw)
    w.set_child(area)
    w.show()


if __name__ == "__main__":
    libui.run(main())
