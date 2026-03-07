"""Form layout — two-column label + control pairs."""

import libui
from libui.declarative import (
    App,
    Window,
    VBox,
    Form,
    Group,
    Label,
    Entry,
    MultilineEntry,
    Combobox,
    State,
    stretchy,
)


async def main():
    app = App()
    status = State("Fill in the form below.")

    app.build(
        window=Window(
            "Form Layout",
            500,
            400,
            child=VBox(
                Label(text=status),
                stretchy(
                    Group(
                        "User Profile",
                        Form(
                            (
                                "First name:",
                                Entry(
                                    on_changed=lambda t: status.set(f"First: {t}"),
                                ),
                            ),
                            (
                                "Last name:",
                                Entry(
                                    on_changed=lambda t: status.set(f"Last: {t}"),
                                ),
                            ),
                            ("Email:", Entry()),
                            (
                                "Role:",
                                Combobox(
                                    items=["Admin", "Editor", "Viewer"],
                                    selected=0,
                                ),
                            ),
                            (
                                "Bio:",
                                MultilineEntry(wrapping=True),
                                True,
                            ),  # True = stretchy
                            padded=True,
                        ),
                    )
                ),
            ),
        )
    )

    app.show()
    await app.wait()


libui.run(main())
