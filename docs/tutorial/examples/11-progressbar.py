"""ProgressBar — one-way binding to display progress."""
import libui
from libui.declarative import (
    App, Window, VBox, HBox, Form,
    Label, Button, Slider, ProgressBar, State,
)


async def main():
    app = App()
    progress = State(0)

    app.build(window=Window(
        "Progress Bar", 400, 200,
        child=VBox(
            Form(
                ("Adjust:", Slider(0, 100, value=progress)),
                ("Progress:", ProgressBar(value=progress)),
                padded=True,
            ),
            Label(text=progress.map(lambda v: f"{v}%")),
            HBox(
                Button("0%", on_clicked=lambda: progress.set(0)),
                Button("50%", on_clicked=lambda: progress.set(50)),
                Button("100%", on_clicked=lambda: progress.set(100)),
            ),
        ),
    ))

    app.show()
    await app.wait()


libui.run(main())
