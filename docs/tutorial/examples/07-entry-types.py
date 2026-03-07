"""Entry types — normal, password, and search entries."""
import libui
from libui.declarative import (
    App, Window, VBox, Form, Group,
    Label, Entry, MultilineEntry, State, stretchy,
)


async def main():
    app = App()
    status = State("Type in any field.")

    app.build(window=Window(
        "Entry Types", 500, 400,
        child=VBox(
            Label(text=status),
            Group("Single-line Entries", Form(
                ("Normal:", Entry(
                    on_changed=lambda t: status.set(f"Normal: {t}"),
                )),
                ("Password:", Entry(
                    type="password",
                    on_changed=lambda t: status.set(f"Password length: {len(t)}"),
                )),
                ("Search:", Entry(
                    type="search",
                    on_changed=lambda t: status.set(f"Search: {t}"),
                )),
                padded=True,
            )),
            Group("Multi-line Entry", stretchy(
                MultilineEntry(
                    text="Multi-line text with word wrapping enabled.",
                    wrapping=True,
                    on_changed=lambda t: status.set(f"Lines: {t.count(chr(10)) + 1}"),
                ),
            )),
        ),
    ))

    app.show()
    await app.wait()


libui.run(main())
