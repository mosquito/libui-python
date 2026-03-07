"""Drawing styled text — attributed strings with formatting."""

import libui
from libui.declarative import App, Window, VBox, DrawArea, stretchy


def on_draw(ctx, area_w, area_h, clip_x, clip_y, clip_w, clip_h):
    # Create an attributed string with various styles
    text = "Bold Colored Italic Underlined"
    astr = libui.AttributedString(text)

    # Bold (0-4)
    astr.set_attribute(libui.weight_attribute(libui.TextWeight.BOLD), 0, 4)

    # Red color (5-12)
    astr.set_attribute(libui.color_attribute(0.8, 0.0, 0.0, 1.0), 5, 12)

    # Italic (13-19)
    astr.set_attribute(libui.italic_attribute(libui.TextItalic.ITALIC), 13, 19)

    # Underline (20-30)
    astr.set_attribute(libui.underline_attribute(libui.Underline.SINGLE), 20, 30)

    font = {"family": "sans-serif", "size": 18.0}
    layout = libui.DrawTextLayout(astr, font, area_w - 40)
    ctx.text(layout, 20, 20)

    # Second line with more attributes
    text2 = "Large serif text with background highlight"
    astr2 = libui.AttributedString(text2)
    astr2.set_attribute(libui.family_attribute("serif"), 0, len(text2))
    astr2.set_attribute(libui.size_attribute(24.0), 0, 5)
    astr2.set_attribute(libui.background_attribute(1.0, 1.0, 0.0, 0.5), 26, 36)

    font2 = {"family": "serif", "size": 16.0}
    layout2 = libui.DrawTextLayout(astr2, font2, area_w - 40)
    ctx.text(layout2, 20, 60)


async def main():
    app = App()

    app.build(
        window=Window(
            "Styled Text",
            500,
            150,
            child=VBox(stretchy(DrawArea(on_draw=on_draw))),
        )
    )

    app.show()
    await app.wait()


libui.run(main())
