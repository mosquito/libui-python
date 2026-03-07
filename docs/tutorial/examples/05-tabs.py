"""Tab container — multiple pages in a tabbed view."""
import libui
from libui.declarative import (
    App, Window, Tab, VBox, Form,
    Label, Button, Entry, MultilineEntry, stretchy,
)


async def main():
    app = App()

    app.build(window=Window(
        "Tabs", 500, 350,
        child=Tab(
            ("Profile", Form(
                ("Name:", Entry()),
                ("Email:", Entry()),
                padded=True,
            )),
            ("Settings", VBox(
                Label("Application settings go here."),
                Button("Reset to Defaults"),
            )),
            ("Notes", VBox(
                stretchy(MultilineEntry(
                    text="Write your notes here...",
                    wrapping=True,
                )),
            )),
        ),
    ))

    app.show()
    await app.wait()


libui.run(main())
