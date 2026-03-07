"""Grid layout — position-based coordinate placement with GridCell.

Grid places widgets at exact (column, row) coordinates with spanning.
It is best for keypad-style layouts where you need precise 2D placement
that VBox/HBox/Form cannot express.

Note: on macOS, Grid does not expand to fill its parent width —
use Form for label + control layouts that need to stretch.
"""

import libui
from libui.declarative import App, Window, VBox, Grid, GridCell, Button, Entry, State


async def main():
    app = App()
    display = State("0")

    def press(ch):
        cur = display.value
        if cur == "0" and ch not in (".", "0"):
            display.set(ch)
        else:
            display.set(cur + ch)

    def clear():
        display.set("0")

    def btn(text, left, top, xspan=1):
        return GridCell(
            Button(text, on_clicked=lambda t=text: press(t)),
            left,
            top,
            xspan=xspan,
        )

    keypad = Grid(
        # Row 0: display spanning 4 columns
        GridCell(Entry(text=display, read_only=True), 0, 0, xspan=4),
        # Row 1
        btn("7", 0, 1),
        btn("8", 1, 1),
        btn("9", 2, 1),
        GridCell(Button("C", on_clicked=clear), 3, 1),
        # Row 2
        btn("4", 0, 2),
        btn("5", 1, 2),
        btn("6", 2, 2),
        btn("+", 3, 2),
        # Row 3
        btn("1", 0, 3),
        btn("2", 1, 3),
        btn("3", 2, 3),
        btn("-", 3, 3),
        # Row 4: zero spans 2 columns
        btn("0", 0, 4, xspan=2),
        btn(".", 2, 4),
        btn("=", 3, 4),
        padded=True,
    )

    app.build(
        window=Window(
            "Grid Layout — Calculator",
            300,
            250,
            child=VBox(keypad),
        )
    )

    app.show()
    await app.wait()


libui.run(main())
