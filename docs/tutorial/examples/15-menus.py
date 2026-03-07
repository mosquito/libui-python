"""Menus — file, edit, and help menus with various item types."""

import libui
from libui.declarative import (
    App,
    Window,
    VBox,
    Label,
    State,
    MenuDef,
    MenuItem,
    CheckMenuItem,
    MenuSeparator,
    QuitItem,
    PreferencesItem,
    AboutItem,
)


async def main():
    app = App()
    dark_mode = State(False)
    status = State("Use the menus above.")

    menus = [
        MenuDef(
            "File",
            MenuItem(
                "Open...",
                on_click=lambda: status.set(
                    f"Open: {app.open_file() or '(cancelled)'}"
                ),
            ),
            MenuItem(
                "Save As...",
                on_click=lambda: status.set(
                    f"Save: {app.save_file() or '(cancelled)'}"
                ),
            ),
            MenuSeparator(),
            QuitItem(),
        ),
        MenuDef(
            "Edit",
            CheckMenuItem(
                "Dark Mode",
                checked=dark_mode,
                on_click=lambda: status.set(f"Dark mode: {dark_mode.value}"),
            ),
            MenuSeparator(),
            PreferencesItem(),
        ),
        MenuDef(
            "Help",
            AboutItem(),
            MenuItem(
                "Documentation",
                on_click=lambda: app.msg_box(
                    "Help", "Visit the project repository for documentation."
                ),
            ),
        ),
    ]

    app.build(
        menus=menus,
        window=Window(
            "Menus",
            500,
            250,
            has_menubar=True,
            child=VBox(
                Label(text=status),
            ),
        ),
    )

    app.show()
    await app.wait()


libui.run(main())
