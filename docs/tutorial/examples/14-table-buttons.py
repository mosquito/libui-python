"""Table with button columns — clickable actions per row."""

import libui
from libui.declarative import (
    App,
    Window,
    VBox,
    Label,
    State,
    stretchy,
    DataTable,
    ListState,
    TextColumn,
    ProgressColumn,
    ButtonColumn,
)


async def main():
    app = App()
    status = State("Click a button in the table.")

    data = ListState(
        [
            {"name": "Alice", "score": 85, "action": "View"},
            {"name": "Bob", "score": 72, "action": "View"},
            {"name": "Carol", "score": 90, "action": "View"},
        ]
    )

    def on_button(row):
        if row < len(data):
            d = data[row]
            app.msg_box("Details", f"{d['name']}\nScore: {d['score']}")

    app.build(
        window=Window(
            "Table Buttons",
            450,
            300,
            child=VBox(
                Label(text=status),
                stretchy(
                    DataTable(
                        data,
                        TextColumn("Name", key="name"),
                        ProgressColumn("Score", key="score"),
                        ButtonColumn("Action", text_key="action", on_click=on_button),
                        on_row_clicked=lambda row: status.set(
                            f"Selected: {data[row]['name']}"
                        ),
                    )
                ),
            ),
        )
    )

    app.show()
    await app.wait()


libui.run(main())
