"""Checkbox, slider, and spinbox — two-way binding with shared state."""
import libui
from libui.declarative import (
    App, Window, VBox, Form, Group, Separator,
    Label, Checkbox, Slider, Spinbox, ProgressBar, State,
)


async def main():
    app = App()
    status = State("Adjust the controls.")
    value = State(50)
    enabled = State(True)

    # Subscribe to print changes
    value.subscribe(lambda: status.set(f"Value: {value.value}"))

    app.build(window=Window(
        "Controls", 450, 350,
        child=VBox(
            Label(text=status),
            Separator(),
            Group("Shared Value", Form(
                ("Slider:", Slider(0, 100, value=value)),
                ("Spinbox:", Spinbox(0, 100, value=value)),
                ("Progress:", ProgressBar(value=value)),
                padded=True,
            )),
            Group("Checkbox", VBox(
                Checkbox("Enable feature", checked=enabled,
                         on_toggled=lambda c: status.set(
                             f"Feature {'enabled' if c else 'disabled'}"
                         )),
                Label(text=enabled.map(
                    lambda e: "Status: enabled" if e else "Status: disabled"
                )),
            )),
        ),
    ))

    app.show()
    await app.wait()


libui.run(main())
