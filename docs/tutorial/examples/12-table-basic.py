"""Basic table — ListState-driven data table."""
import libui
from libui.declarative import (
    App, Window, VBox, HBox,
    Label, Button, State, stretchy,
    DataTable, ListState, TextColumn, ProgressColumn,
)


async def main():
    app = App()
    status = State("Click a row.")

    data = ListState([
        {"name": "Alice", "role": "Engineer", "score": 85},
        {"name": "Bob", "role": "Designer", "score": 72},
        {"name": "Carol", "role": "Manager", "score": 90},
    ])

    counter = State(len(data))

    def add_row():
        counter.update(lambda n: n + 1)
        data.append({
            "name": f"Person {counter.value}",
            "role": "New",
            "score": 50,
        })

    app.build(window=Window(
        "Basic Table", 500, 350,
        child=VBox(
            Label(text=status),
            stretchy(DataTable(
                data,
                TextColumn("Name", key="name"),
                TextColumn("Role", key="role"),
                ProgressColumn("Score", key="score"),
                on_row_clicked=lambda row: status.set(
                    f"Clicked: {data[row]['name']}"
                ),
            )),
            HBox(
                Button("Add Row", on_clicked=add_row),
                Button("Remove Last", on_clicked=lambda: data.pop() if len(data) else None),
            ),
        ),
    ))

    app.show()
    await app.wait()


libui.run(main())
