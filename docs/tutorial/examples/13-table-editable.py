"""Editable table — inline editing with CheckboxTextColumn."""

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
    CheckboxTextColumn,
)


async def main():
    app = App()
    status = State("Edit cells directly in the table.")

    data = ListState(
        [
            {"done": 1, "task": "Write documentation", "notes": "In progress"},
            {"done": 0, "task": "Fix bug #42", "notes": "Investigate crash"},
            {"done": 1, "task": "Review PR", "notes": "Approved"},
            {"done": 0, "task": "Deploy v2.0", "notes": "Waiting on tests"},
        ]
    )

    app.build(
        window=Window(
            "Editable Table",
            550,
            300,
            child=VBox(
                Label(text=status),
                stretchy(
                    DataTable(
                        data,
                        CheckboxTextColumn(
                            "Task",
                            checkbox_key="done",
                            text_key="task",
                            checkbox_editable=True,
                            text_editable=True,
                        ),
                        TextColumn("Notes", key="notes", editable=True),
                        on_row_clicked=lambda row: status.set(
                            f"Row {row}: {data[row]['task']} "
                            f"({'done' if data[row]['done'] else 'pending'})"
                        ),
                    )
                ),
            ),
        )
    )

    app.show()
    await app.wait()


libui.run(main())
