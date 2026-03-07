"""Computed state — derived read-only values that auto-update."""

import libui
from libui.declarative import App, Window, VBox, Form, Label, Button, State


async def main():
    app = App()

    count = State(0)
    doubled = count.map(lambda n: n * 2)
    label_text = count.map(lambda n: f"Count: {n}")
    doubled_text = doubled.map(lambda n: f"Doubled: {n}")
    parity = count.map(lambda n: "even" if n % 2 == 0 else "odd")
    parity_text = parity.map(lambda p: f"Parity: {p}")

    app.build(
        window=Window(
            "Computed State",
            400,
            250,
            child=VBox(
                Form(
                    ("Count:", Label(text=label_text)),
                    ("Doubled:", Label(text=doubled_text)),
                    ("Parity:", Label(text=parity_text)),
                ),
                Button("Increment", on_clicked=lambda: count.update(lambda n: n + 1)),
                Button("Reset", on_clicked=lambda: count.set(0)),
            ),
        )
    )

    app.show()
    await app.wait()


libui.run(main())
