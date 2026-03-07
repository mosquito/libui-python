"""Full application — contact manager with table, editor, menus, and async I/O."""
import asyncio
import libui
from libui.declarative import (
    App, Window, Tab, VBox, HBox, Form, Separator,
    Label, Button, Entry, MultilineEntry, Combobox,
    State, ListState, stretchy,
    DataTable, TextColumn, CheckboxTextColumn,
    MenuDef, MenuItem, MenuSeparator, QuitItem, AboutItem,
    ProgressBar,
)


CATEGORIES = ["Personal", "Work", "Family", "VIP"]


def build_editor(contacts, status, editing_index):
    """Right-side editor panel with form fields."""
    first = State("")
    last = State("")
    email = State("")
    category = State(0)
    notes = State("")
    is_new = State(True)

    def load_contact(index):
        if index < 0 or index >= len(contacts):
            return
        c = contacts[index]
        first.set(c["first"])
        last.set(c["last"])
        email.set(c["email"])
        cat = c.get("category", "Personal")
        category.set(CATEGORIES.index(cat) if cat in CATEGORIES else 0)
        notes.set(c.get("notes", ""))
        is_new.set(False)
        status.set(f"Editing: {c['first']} {c['last']}")

    def clear_form():
        for s in (first, last, email, notes):
            s.set("")
        category.set(0)
        is_new.set(True)
        editing_index.set(-1)
        status.set("New contact.")

    def save_contact():
        f, l = first.value.strip(), last.value.strip()
        if not f and not l:
            status.set("Error: name required.")
            return
        row = {
            "selected": 0, "first": f, "last": l,
            "email": email.value.strip(),
            "category": CATEGORIES[category.value],
            "notes": notes.value.strip(),
        }
        idx = editing_index.value
        if is_new.value or idx < 0 or idx >= len(contacts):
            contacts.append(row)
            status.set(f"Added: {f} {l}")
        else:
            contacts[idx] = row
            status.set(f"Updated: {f} {l}")
        is_new.set(False)

    def delete_contact():
        idx = editing_index.value
        if idx < 0 or idx >= len(contacts):
            return
        name = f"{contacts[idx]['first']} {contacts[idx]['last']}"
        contacts.pop(idx)
        clear_form()
        status.set(f"Deleted: {name}")

    editing_index.subscribe(lambda: load_contact(editing_index.value))

    return VBox(
        Form(
            ("First:", Entry(text=first)),
            ("Last:", Entry(text=last)),
            ("Email:", Entry(text=email)),
            ("Category:", Combobox(items=CATEGORIES, selected=category)),
            ("Notes:", MultilineEntry(text=notes, wrapping=True), True),
        ),
        HBox(
            Button("Save", on_clicked=save_contact),
            Button("New", on_clicked=clear_form),
            Button("Delete", on_clicked=delete_contact),
        ),
    )


def build_list(contacts, status, editing_index):
    """Left-side contact list with table."""
    return VBox(
        stretchy(DataTable(
            contacts,
            CheckboxTextColumn("Name", checkbox_key="selected",
                               text_key="first", checkbox_editable=True),
            TextColumn("Last", key="last"),
            TextColumn("Email", key="email"),
            TextColumn("Category", key="category"),
            on_row_clicked=lambda row: status.set(
                f"Selected: {contacts[row]['first']} {contacts[row]['last']}"
            ),
            on_row_double_clicked=lambda row: editing_index.set(row),
        )),
    )


async def main():
    app = App()

    contacts = ListState([
        {"selected": 0, "first": "Alice", "last": "Johnson",
         "email": "alice@example.com", "category": "Work", "notes": "Met at PyCon."},
        {"selected": 0, "first": "Bob", "last": "Smith",
         "email": "bob@email.org", "category": "Personal", "notes": ""},
        {"selected": 0, "first": "Carol", "last": "Williams",
         "email": "carol@bigco.io", "category": "Work", "notes": "London office."},
    ])
    status = State("Ready. Double-click a row to edit.")
    editing_index = State(-1)
    progress = State(0)

    async def do_export():
        path = await app.save_file_async()
        if not path:
            return
        for i in range(len(contacts)):
            await asyncio.sleep(0.05)
            progress.set(int((i + 1) / len(contacts) * 100))
        await app.msg_box_async("Export", f"Exported {len(contacts)} contacts.")
        progress.set(0)

    menus = [
        MenuDef("File",
            MenuItem("Export...", on_click=do_export),
            MenuSeparator(),
            QuitItem(),
        ),
        MenuDef("Help",
            AboutItem(),
        ),
    ]

    editor = build_editor(contacts, status, editing_index)
    contact_list = build_list(contacts, status, editing_index)

    app.build(
        menus=menus,
        window=Window("Contact Manager", 800, 500, has_menubar=True, child=VBox(
            stretchy(HBox(
                stretchy(contact_list),
                stretchy(editor),
            )),
            Separator(),
            HBox(
                stretchy(Label(text=status)),
                ProgressBar(value=progress),
            ),
        )),
    )

    app.show()
    await app.wait()


libui.run(main())
