"""Dialogs — file dialogs and message boxes (sync and async)."""

import libui
from libui.declarative import App, Window, VBox, Label, Button, State


async def main():
    app = App()
    status = State("")

    def do_open():
        path = app.open_file()
        status.set(f"Opened: {path}" if path else "Open cancelled.")

    def do_folder():
        path = app.open_folder()
        status.set(f"Folder: {path}" if path else "Folder cancelled.")

    async def do_save_async():
        path = await app.save_file_async()
        status.set(f"Save to: {path}" if path else "Save cancelled.")

    app.build(
        window=Window(
            "Dialogs",
            400,
            300,
            child=VBox(
                Label(text=status),
                Button("Open File", on_clicked=do_open),
                Button("Open Folder", on_clicked=do_folder),
                Button("Save File (async)", on_clicked=do_save_async),
                Button(
                    "Message Box",
                    on_clicked=lambda: app.msg_box("Info", "This is a message box."),
                ),
                Button(
                    "Error Box",
                    on_clicked=lambda: app.msg_box_error(
                        "Error", "Something went wrong!"
                    ),
                ),
            ),
        )
    )

    app.show()
    await app.wait()


libui.run(main())
