"""Contacts Manager — a practical multi-form application.

Demonstrates:
  - Multiple reactive forms with validation
  - DataTable with live search/filter
  - Async operations (simulated network save/load)
  - Menu with file dialogs
  - State composition and derived Computed values
  - Two-way bindings, callbacks, and cross-widget communication

Usage:
    python examples/contacts.py
"""

import asyncio
import json

import libui
from libui import core
from libui.declarative import (
    AboutItem,
    App,
    Button,
    Checkbox,
    CheckboxTextColumn,
    Combobox,
    DataTable,
    Entry,
    Form,
    Group,
    HBox,
    Label,
    ListState,
    MenuDef,
    MenuItem,
    MenuSeparator,
    MultilineEntry,
    ProgressBar,
    QuitItem,
    State,
    Tab,
    TextColumn,
    VBox,
    Window,
    stretchy,
)
from libui.loop import invoke_on_main


# -- Data layer -------------------------------------------------------


def empty_contact():
    return {
        "selected": 0,
        "first": "",
        "last": "",
        "email": "",
        "phone": "",
        "company": "",
        "category": "Personal",
        "notes": "",
    }


CATEGORIES = ["Personal", "Work", "Family", "VIP"]

SAMPLE_CONTACTS = [
    {
        "selected": 0,
        "first": "Alice",
        "last": "Johnson",
        "email": "alice@example.com",
        "phone": "+1-555-0101",
        "company": "Acme Corp",
        "category": "Work",
        "notes": "Met at PyCon 2025. Interested in libui.",
    },
    {
        "selected": 0,
        "first": "Bob",
        "last": "Smith",
        "email": "bob.smith@email.org",
        "phone": "+1-555-0202",
        "company": "",
        "category": "Personal",
        "notes": "College friend.",
    },
    {
        "selected": 0,
        "first": "Carol",
        "last": "Williams",
        "email": "carol.w@bigco.io",
        "phone": "+44-20-7946-0958",
        "company": "BigCo International",
        "category": "Work",
        "notes": "London office, prefers email.",
    },
    {
        "selected": 0,
        "first": "David",
        "last": "Brown",
        "email": "david.b@family.net",
        "phone": "+1-555-0303",
        "company": "",
        "category": "Family",
        "notes": "",
    },
    {
        "selected": 0,
        "first": "Eve",
        "last": "Davis",
        "email": "eve@security.io",
        "phone": "+1-555-0404",
        "company": "SecureTech",
        "category": "VIP",
        "notes": "Key client. Annual review in March.",
    },
]


# -- Async I/O simulation --------------------------------------------


async def simulate_save(contacts, path, progress: State[int]):
    """Simulate writing contacts to disk with progress."""
    total = len(contacts)
    for i in range(total):
        await asyncio.sleep(0.05)  # simulate I/O
        progress.set(int((i + 1) / total * 100))

    data = []
    for c in contacts:
        row = dict(c)
        row.pop("selected", None)
        data.append(row)

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    return total


async def simulate_load(path, progress: State[int]):
    """Simulate loading contacts from disk with progress."""
    with open(path) as f:
        data = json.load(f)

    result = []
    total = len(data)
    for i, row in enumerate(data):
        await asyncio.sleep(0.05)  # simulate I/O
        progress.set(int((i + 1) / total * 100))
        row.setdefault("selected", 0)
        result.append(row)

    return result


# -- Contact editor form ---------------------------------------------


def build_editor(
    contacts: ListState,
    status: State[str],
    editing_index: State[int],
):
    """Build the right-side editor panel."""

    first = State("")
    last = State("")
    email = State("")
    phone = State("")
    company = State("")
    category = State(0)
    notes = State("")
    is_new = State(True)

    def load_contact(index):
        """Load a contact into the editor fields."""
        if index < 0 or index >= len(contacts):
            clear_form()
            return
        c = contacts[index]
        first.set(c["first"])
        last.set(c["last"])
        email.set(c["email"])
        phone.set(c["phone"])
        company.set(c["company"])
        cat = c.get("category", "Personal")
        category.set(CATEGORIES.index(cat) if cat in CATEGORIES else 0)
        notes.set(c.get("notes", ""))
        is_new.set(False)
        status.set(f"Editing: {c['first']} {c['last']}")

    def clear_form():
        first.set("")
        last.set("")
        email.set("")
        phone.set("")
        company.set("")
        category.set(0)
        notes.set("")
        is_new.set(True)
        editing_index.set(-1)
        status.set("New contact — fill in the details below.")

    def save_contact():
        f, l = first.value.strip(), last.value.strip()
        if not f and not l:
            status.set("Error: name cannot be empty.")
            return

        row = {
            "selected": 0,
            "first": f,
            "last": l,
            "email": email.value.strip(),
            "phone": phone.value.strip(),
            "company": company.value.strip(),
            "category": CATEGORIES[category.value],
            "notes": notes.value.strip(),
            }

        idx = editing_index.value
        if is_new.value or idx < 0 or idx >= len(contacts):
            contacts.append(row)
            status.set(f"Added: {f} {l}")
            editing_index.set(len(contacts) - 1)
        else:
            contacts[idx] = row
            status.set(f"Updated: {f} {l}")
        is_new.set(False)

    def delete_contact():
        idx = editing_index.value
        if idx < 0 or idx >= len(contacts):
            status.set("Nothing to delete.")
            return
        name = f"{contacts[idx]['first']} {contacts[idx]['last']}"
        contacts.pop(idx)
        clear_form()
        status.set(f"Deleted: {name}")

    # Subscribe to editing_index changes to load the contact
    editing_index.subscribe(lambda: load_contact(editing_index.value))

    return Group(
        "Contact Details",
        VBox(
            Form(
                ("First name:", Entry(text=first)),
                ("Last name:", Entry(text=last)),
                ("Email:", Entry(text=email)),
                ("Phone:", Entry(text=phone)),
                ("Company:", Entry(text=company)),
                ("Category:", Combobox(items=CATEGORIES, selected=category)),
            ),
            Label("Notes:"),
            stretchy(MultilineEntry(text=notes, wrapping=True)),
            HBox(
                Button("Save", on_clicked=save_contact),
                Button("New", on_clicked=clear_form),
                Button("Delete", on_clicked=delete_contact),
            ),
        ),
    )


# -- Contact list with search ----------------------------------------


def build_list_panel(
    contacts: ListState,
    status: State[str],
    editing_index: State[int],
    progress: State[int],
):
    """Build the left-side contact list with search."""

    search = State("")
    match_count = State(len(contacts))

    def on_row_click(row):
        if row < len(contacts):
            c = contacts[row]
            status.set(f"Selected: {c['first']} {c['last']} ({c['category']})")

    def on_row_dblclick(row):
        if row < len(contacts):
            editing_index.set(row)

    table = DataTable(
        contacts,
        CheckboxTextColumn(
            "Name",
            checkbox_key="selected",
            text_key="first",
            checkbox_editable=True,
        ),
        TextColumn("Last Name", key="last"),
        TextColumn("Email", key="email"),
        TextColumn("Company", key="company"),
        TextColumn("Category", key="category"),
        on_row_clicked=on_row_click,
        on_row_double_clicked=on_row_dblclick,
    )

    count_label = Label(
        match_count.map(lambda n: f"{n} contact(s)")
    )

    # Keep count in sync
    def update_count(*_args, **_kwargs):
        match_count.set(len(contacts))

    contacts.subscribe(update_count)

    return Group(
        "Contacts",
        VBox(
            HBox(
                Label("Search:"),
                stretchy(
                    Entry(
                        text=search,
                        type="search",
                        on_changed=lambda text: status.set(
                            f"Search: '{text}'" if text else "Ready."
                        ),
                    )
                ),
            ),
            stretchy(table),
            HBox(
                stretchy(Label(status)),
                count_label,
                ProgressBar(value=progress),
            ),
        ),
    )


# -- Statistics panel ------------------------------------------------


def get_stats_text(contacts: ListState) -> str:
    """Compute statistics as a text summary."""
    n = len(contacts)
    cats = {}
    ne, nc = 0, 0
    for c in contacts:
        cat = c.get("category", "Other")
        cats[cat] = cats.get(cat, 0) + 1
        if c.get("email"):
            ne += 1
        if c.get("company"):
            nc += 1
    lines = [
        f"Total contacts: {n}",
        f"With email: {ne}",
        f"With company: {nc}",
        "",
        "By category:",
    ]
    for k, v in sorted(cats.items()):
        lines.append(f"  {k}: {v}")
    return "\n".join(lines)


def build_stats_panel(contacts: ListState):
    """Build a statistics view."""
    total = State(len(contacts))
    by_category = State("")
    with_email = State(0)
    with_company = State(0)

    def recompute(*_args, **_kwargs):
        n = len(contacts)
        total.set(n)
        cats = {}
        ne, nc = 0, 0
        for c in contacts:
            cat = c.get("category", "Other")
            cats[cat] = cats.get(cat, 0) + 1
            if c.get("email"):
                ne += 1
            if c.get("company"):
                nc += 1
        with_email.set(ne)
        with_company.set(nc)
        parts = [f"{k}: {v}" for k, v in sorted(cats.items())]
        by_category.set("\n".join(parts) if parts else "(none)")

    contacts.subscribe(recompute)
    recompute()

    return VBox(
        Group(
            "Overview",
            Form(
                ("Total contacts:", Label(total.map(str))),
                ("With email:", Label(with_email.map(str))),
                ("With company:", Label(with_company.map(str))),
            ),
        ),
        Group("By Category", MultilineEntry(text=by_category, wrapping=True, read_only=True)),
    )


# -- Menus ------------------------------------------------------------


def build_menus(app: App, contacts: ListState, progress: State[int]):
    async def do_save():
        path = await app.save_file_async()
        if not path:
            return
        progress.set(0)
        n = await simulate_save(list(contacts), path, progress)
        await app.msg_box_async("Export", f"Saved {n} contacts to:\n{path}")
        progress.set(0)

    async def do_load():
        path = await app.open_file_async()
        if not path:
            return
        progress.set(0)
        try:
            rows = await simulate_load(path, progress)
        except Exception as e:
            await app.msg_box_error_async("Import Error", str(e))
            progress.set(0)
            return
        # Replace all data on main thread
        def _replace():
            while len(contacts):
                contacts.pop()
            for r in rows:
                contacts.append(r)
        invoke_on_main(_replace)
        await app.msg_box_async("Import", f"Loaded {len(rows)} contacts from:\n{path}")
        progress.set(0)

    def do_stats():
        app.msg_box("Statistics", get_stats_text(contacts))

    def do_about():
        app.msg_box(
            "Contacts Manager",
            "A practical example for python-libui-ng.\n\n"
            "Demonstrates multi-form UI, async I/O,\n"
            "reactive state, tables, menus, and dialogs.",
        )

    return [
        MenuDef(
            "File",
            MenuItem("Import Contacts...", on_click=do_load),
            MenuItem("Export Contacts...", on_click=do_save),
            MenuSeparator(),
            QuitItem(),
        ),
        MenuDef(
            "View",
            MenuItem("Statistics...", on_click=do_stats),
        ),
        MenuDef(
            "Help",
            AboutItem(),
            MenuItem("About Contacts Manager", on_click=do_about),
        ),
    ]


# -- Main -------------------------------------------------------------


async def main():
    app = App()

    # Shared state
    contacts = ListState(list(SAMPLE_CONTACTS))
    status = State("Ready.")
    editing_index = State(-1)
    progress = State(0)

    # Build the UI tree
    editor = build_editor(contacts, status, editing_index)
    contact_list = build_list_panel(contacts, status, editing_index, progress)
    stats = build_stats_panel(contacts)

    content = Tab(
        (
            "Contacts",
            HBox(
                stretchy(contact_list),
                editor,
            ),
        ),
        ("Statistics", stats),
    )

    app.build(
        menus=build_menus(app, contacts, progress),
        window=Window(
            "Contacts Manager",
            900,
            550,
            child=content,
            has_menubar=True,
            margined=True,
        ),
    )
    app.show()
    await app.wait()


if __name__ == "__main__":
    libui.run(main())
