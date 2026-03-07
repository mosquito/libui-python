"""VBox and HBox — vertical and horizontal stacking with stretchy."""

import libui
from libui.declarative import (
    App,
    Window,
    VBox,
    HBox,
    Label,
    Button,
    MultilineEntry,
    Separator,
    stretchy,
)


async def main():
    app = App()

    app.build(
        window=Window(
            "VBox & HBox",
            500,
            400,
            child=VBox(
                Label("Top (fixed)"),
                Separator(),
                HBox(
                    stretchy(Button("Left (stretchy)")),
                    Button("Center (fixed)"),
                    stretchy(Button("Right (stretchy)")),
                ),
                Separator(),
                stretchy(
                    MultilineEntry(
                        text="This multiline entry is stretchy — it fills the remaining space.",
                        wrapping=True,
                    )
                ),
                Label("Bottom (fixed)"),
            ),
        )
    )

    app.show()
    await app.wait()


libui.run(main())
