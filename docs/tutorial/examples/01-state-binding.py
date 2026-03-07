"""State basics — create, read, modify, subscribe."""

import libui
from libui.declarative import App, Window, VBox, Label, Button, Entry, State


async def main():
    app = App()

    name = State("World")
    greeting = name.map(lambda n: f"Hello, {n}!")

    # Subscribe to changes (prints to console)
    name.subscribe(lambda: print(f"Name changed to: {name.value}"))

    app.build(
        window=Window(
            "State Binding",
            400,
            300,
            child=VBox(
                Label(text=greeting),
                Entry(text=name),
                Button("Reset", on_clicked=lambda: name.set("World")),
            ),
        )
    )

    app.show()
    await app.wait()


libui.run(main())
