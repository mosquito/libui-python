"""Combobox and radio buttons — selection-based controls."""

import libui
from libui.declarative import (
    App,
    Window,
    VBox,
    Form,
    Group,
    Separator,
    Label,
    Combobox,
    EditableCombobox,
    RadioButtons,
    State,
)


async def main():
    app = App()
    status = State("Make a selection.")

    colors = ["Red", "Green", "Blue", "Yellow"]
    quality = ["Low", "Medium", "High", "Ultra"]
    fruits = ["Apple", "Banana", "Cherry", "Date"]

    app.build(
        window=Window(
            "Selection Controls",
            450,
            400,
            child=VBox(
                Label(text=status),
                Separator(),
                Group(
                    "Combobox",
                    Form(
                        (
                            "Color:",
                            Combobox(
                                items=colors,
                                selected=0,
                                on_selected=lambda i: status.set(f"Color: {colors[i]}"),
                            ),
                        ),
                        (
                            "Fruit:",
                            EditableCombobox(
                                items=fruits,
                                on_changed=lambda t: status.set(f"Fruit: {t}"),
                            ),
                        ),
                        padded=True,
                    ),
                ),
                Group(
                    "Radio Buttons",
                    VBox(
                        RadioButtons(
                            items=quality,
                            on_selected=lambda i: status.set(
                                f"Quality: {quality[i]}" if i >= 0 else "Quality: none"
                            ),
                        ),
                    ),
                ),
            ),
        )
    )

    app.show()
    await app.wait()


libui.run(main())
