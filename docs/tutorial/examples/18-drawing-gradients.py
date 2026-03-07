"""Drawing gradients — linear and radial gradient fills."""

import math
import libui
from libui.declarative import App, Window, VBox, DrawArea, stretchy


def on_draw(ctx, area_w, area_h, clip_x, clip_y, clip_w, clip_h):
    # Linear gradient
    rect = libui.DrawPath()
    rect.add_rectangle(20, 20, 200, 100)
    rect.end()

    lin = libui.DrawBrush()
    lin.type = libui.BrushType.LINEAR_GRADIENT
    lin.x0, lin.y0 = 20, 20
    lin.x1, lin.y1 = 220, 120
    lin.set_stops(
        [
            (0.0, 1.0, 0.0, 0.0, 1.0),  # red
            (0.5, 1.0, 1.0, 0.0, 1.0),  # yellow
            (1.0, 0.0, 0.0, 1.0, 1.0),  # blue
        ]
    )
    ctx.fill(rect, lin)

    # Radial gradient
    circle = libui.DrawPath()
    circle.new_figure_with_arc(370, 70, 60, 0, 2 * math.pi, False)
    circle.end()

    rad = libui.DrawBrush()
    rad.type = libui.BrushType.RADIAL_GRADIENT
    rad.x0, rad.y0 = 370, 70  # center
    rad.x1, rad.y1 = 370, 70  # focus (same as center)
    rad.outer_radius = 60
    rad.set_stops(
        [
            (0.0, 1.0, 1.0, 1.0, 1.0),  # white center
            (1.0, 0.2, 0.0, 0.6, 1.0),  # purple edge
        ]
    )
    ctx.fill(circle, rad)

    # Another linear gradient — vertical
    rect2 = libui.DrawPath()
    rect2.add_rectangle(20, 150, 430, 60)
    rect2.end()

    lin2 = libui.DrawBrush()
    lin2.type = libui.BrushType.LINEAR_GRADIENT
    lin2.x0, lin2.y0 = 20, 150
    lin2.x1, lin2.y1 = 450, 150
    lin2.set_stops(
        [
            (0.0, 0.0, 0.8, 0.0, 1.0),  # green
            (0.5, 0.0, 0.8, 0.8, 1.0),  # teal
            (1.0, 0.0, 0.0, 0.8, 1.0),  # blue
        ]
    )
    ctx.fill(rect2, lin2)


async def main():
    app = App()

    app.build(
        window=Window(
            "Gradients",
            500,
            250,
            child=VBox(stretchy(DrawArea(on_draw=on_draw))),
        )
    )

    app.show()
    await app.wait()


libui.run(main())
