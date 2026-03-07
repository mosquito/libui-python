"""Hello world — a window with a button and a reactive counter."""

import libui
from libui.declarative import App, Window, VBox, Label, Button, State


async def main():
    app = App()
    count = State(0)

    app.build(
        window=Window(
            "Hello",
            400,
            300,
            child=VBox(
                Label(text=count.map(lambda n: f"Count: {n}")),
                Button("Click me", on_clicked=lambda: count.update(lambda n: n + 1)),
            ),
        )
    )

    app.show()
    await app.wait()


libui.run(main())
