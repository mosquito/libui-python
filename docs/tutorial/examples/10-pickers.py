"""Pickers — color, font, and date/time selection."""

import libui
from libui.declarative import (
    App,
    Window,
    VBox,
    Form,
    Group,
    Label,
    ColorButton,
    FontButton,
    DateTimePicker,
    State,
)


async def main():
    app = App()
    status = State("Pick a value.")

    app.build(
        window=Window(
            "Pickers",
            450,
            350,
            child=VBox(
                Label(text=status),
                Group(
                    "Pickers",
                    Form(
                        (
                            "Color:",
                            ColorButton(
                                on_changed=lambda rgba: status.set(
                                    "Color: R={:.2f} G={:.2f} B={:.2f} A={:.2f}".format(
                                        *rgba
                                    )
                                ),
                            ),
                        ),
                        (
                            "Font:",
                            FontButton(
                                on_changed=lambda f: status.set(
                                    f"Font: {f['family']} {f['size']}pt"
                                ),
                            ),
                        ),
                        (
                            "Date & Time:",
                            DateTimePicker(
                                type="datetime",
                                on_changed=lambda t: status.set(
                                    "DateTime: {0:04d}-{1:02d}-{2:02d} {3:02d}:{4:02d}".format(
                                        *t[:5]
                                    )
                                ),
                            ),
                        ),
                        ("Date only:", DateTimePicker(type="date")),
                        ("Time only:", DateTimePicker(type="time")),
                        padded=True,
                    ),
                ),
            ),
        )
    )

    app.show()
    await app.wait()


libui.run(main())
