"""Declarative version of the comprehensive showcase.

Demonstrates the same ~30 widget types as showcase.py but using the
declarative UI layer — reactive State, auto-syncing, and composable nodes.

Usage:
    python examples/showcase_declarative.py
"""

import math

import libui
from libui.declarative import (
    AboutItem,
    App,
    Button,
    ButtonColumn,
    Checkbox,
    CheckboxTextColumn,
    CheckMenuItem,
    ColorButton,
    Combobox,
    DataTable,
    DateTimePicker,
    DrawArea,
    EditableCombobox,
    Entry,
    FontButton,
    Form,
    Grid,
    GridCell,
    Group,
    HBox,
    Label,
    ListState,
    MenuDef,
    MenuItem,
    MenuSeparator,
    MultilineEntry,
    PreferencesItem,
    ProgressBar,
    ProgressColumn,
    QuitItem,
    RadioButtons,
    Separator,
    Slider,
    Spinbox,
    State,
    Tab,
    TextColumn,
    VBox,
    Window,
    stretchy,
)


# ── Reusable components ─────────────────────────────────────────────

def StatusPanel(status: State[str]) -> Label:
    return Label(text=status)


# ── Tab 0: Basic Controls ───────────────────────────────────────────

def build_basic_tab(app: App):
    status = State("Interact with the controls below.")
    click_count = State(0)
    read_only = State(False)

    def on_click():
        click_count.update(lambda x: x + 1)
        status.set(f"Button clicked {click_count.value} time(s)")

    return VBox(
        StatusPanel(status),
        Group("Text Entry", Form(
            ("Normal:", Entry(
                read_only=read_only,
                on_changed=lambda text: status.set(f"Normal entry: {text}"),
            )),
            ("Password:", Entry(
                type="password", read_only=read_only,
                on_changed=lambda text: status.set(
                    f"Password entry changed (len={len(text)})"),
            )),
            ("Search:", Entry(
                type="search", read_only=read_only,
                on_changed=lambda text: status.set(f"Search entry: {text}"),
            )),
        )),
        Separator(),
        Group("Buttons & Checkboxes", HBox(
            stretchy(VBox(
                Button("Click Me", on_clicked=on_click),
                Button("Reset", on_clicked=lambda: status.set(
                    "Interact with the controls below.")),
                Checkbox("Enable feature", on_toggled=lambda checked: status.set(
                    f"Feature {'enabled' if checked else 'disabled'}")),
                Checkbox("Read-only entries", on_toggled=lambda checked: (
                    read_only.set(checked),
                    status.set(f"Entries are {'read-only' if checked else 'editable'}"),
                )),
            )),
            stretchy(VBox(
                Checkbox("Borderless window", on_toggled=lambda checked: (
                    setattr(app.window, "borderless", checked)
                    if app.window else None)),
                Checkbox("Fullscreen", on_toggled=lambda checked: (
                    setattr(app.window, "fullscreen", checked)
                    if app.window else None)),
            )),
        )),
    )


# ── Tab 1: Selectors & Numbers ──────────────────────────────────────

def build_selectors_tab():
    status = State("Adjust the controls below.")
    value = State(0)
    value.subscribe(lambda: status.set(f"Value: {value.value}"))

    radio_labels = ["Low", "Medium", "High", "Ultra"]
    combo_items = ["Red", "Green", "Blue", "Yellow"]

    return VBox(
        StatusPanel(status),
        Group("Numeric Controls", Form(
            ("Slider:", Slider(0, 100, value=value)),
            ("Spinbox:", Spinbox(0, 100, value=value)),
            ("Progress:", ProgressBar(value=value)),
        )),
        Separator(),
        Group("Selection Controls", Form(
            ("Quality:", RadioButtons(
                items=radio_labels,
                on_selected=lambda idx: status.set(
                    f"Radio: {radio_labels[idx]}" if idx >= 0 else "Radio: none"),
            )),
            ("Color:", Combobox(
                items=combo_items, selected=0,
                on_selected=lambda idx: status.set(
                    f"Combobox: {combo_items[idx]}"),
            )),
            ("Fruit:", EditableCombobox(
                items=["Apple", "Banana", "Cherry"],
                on_changed=lambda text: status.set(
                    f"EditableCombobox: {text}"),
            )),
        )),
    )


# ── Tab 2: Rich Input ───────────────────────────────────────────────

def build_rich_input_tab():
    pick_status = State("Pick a value to see it here.")
    append_count = State(0)
    mle_read_only = State(False)

    mle = MultilineEntry(
        text="Type or paste text here.\nMultiple lines supported.",
        wrapping=True,
        read_only=mle_read_only,
    )

    def do_append():
        append_count.update(lambda x: x + 1)
        if mle.widget:
            mle.widget.append(f"\nAppended line #{append_count.value}")

    def do_clear():
        if mle.widget:
            mle.widget.text = ""

    return HBox(
        stretchy(Group("Multiline Entry", VBox(
            stretchy(mle),
            HBox(
                Button("Append Text", on_clicked=do_append),
                Button("Clear", on_clicked=do_clear),
                Checkbox("Read Only", on_toggled=lambda checked: mle_read_only.set(checked)),
            ),
        ))),
        stretchy(Group("Pickers", VBox(
            stretchy(Form(
                ("Color:", ColorButton(
                    on_changed=lambda color: pick_status.set(
                        "Color: R={:.2f} G={:.2f} B={:.2f} A={:.2f}".format(*color)),
                )),
                ("Font:", FontButton(
                    on_changed=lambda font: pick_status.set(
                        "Font: {family} {size}pt".format(**font)),
                )),
                ("Date & Time:", DateTimePicker(
                    on_changed=lambda time: pick_status.set(
                        "DateTime: {0:04d}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}".format(
                            *time[:6])),
                )),
                ("Date:", DateTimePicker(
                    type="date",
                    on_changed=lambda time: pick_status.set(
                        "Date: {0:04d}-{1:02d}-{2:02d}".format(*time[:3])),
                )),
                ("Time:", DateTimePicker(
                    type="time",
                    on_changed=lambda time: pick_status.set(
                        "Time: {3:02d}:{4:02d}:{5:02d}".format(*time[:6])),
                )),
            )),
            Label(text=pick_status),
        ))),
    )


# ── Tab 3: Layout ───────────────────────────────────────────────────

def build_layout_tab():
    return VBox(
        Group("Grid Layout", Grid(
            GridCell(Label("Name:"), 0, 0, halign=libui.Align.END),
            GridCell(Entry(), 1, 0, hexpand=True),
            GridCell(Label("Email:"), 0, 1, halign=libui.Align.END),
            GridCell(Entry(), 1, 1, hexpand=True),
            GridCell(Button("Submit"), 0, 2, xspan=2, halign=libui.Align.CENTER),
            padded=True,
        )),
        Separator(),
        Group("Form Layout", Form(
            ("Username:", Entry()),
            ("Password:", Entry(type="password")),
            ("Role:", Combobox(items=["Admin", "Editor", "Viewer"], selected=0)),
            ("Bio:", MultilineEntry(wrapping=True), True),
        )),
        Separator(),
        Group("Nested Boxes", HBox(
            *[stretchy(VBox(
                Label(f"Column {c}"),
                Button(f"Btn {c}"),
                ProgressBar(),
            )) for c in ("A", "B", "C")]
        )),
    )


# ── Tab 4: Drawing ──────────────────────────────────────────────────

def _on_draw(ctx, area_w, area_h, clip_x, clip_y, clip_w, clip_h):
    _draw_filled_shapes(ctx)
    _draw_gradients(ctx)
    _draw_stroke_styles(ctx)
    _draw_attributed_text(ctx, area_w)
    _draw_rotated_rect(ctx)


def _draw_filled_shapes(ctx):
    p = libui.DrawPath()
    p.add_rectangle(20, 20, 120, 70)
    p.end()
    b = libui.DrawBrush()
    b.r, b.g, b.b, b.a = 0.85, 0.15, 0.15, 1.0
    ctx.fill(p, b)

    p2 = libui.DrawPath()
    p2.new_figure_with_arc(230, 55, 35, 0, 2 * math.pi, False)
    p2.end()
    b2 = libui.DrawBrush()
    b2.r, b2.g, b2.b, b2.a = 0.15, 0.7, 0.15, 1.0
    ctx.fill(p2, b2)

    p3 = libui.DrawPath()
    p3.new_figure(310, 90)
    p3.line_to(350, 20)
    p3.line_to(390, 90)
    p3.close_figure()
    p3.end()
    b3 = libui.DrawBrush()
    b3.r, b3.g, b3.b, b3.a = 0.15, 0.15, 0.85, 1.0
    ctx.fill(p3, b3)


def _draw_gradients(ctx):
    ox, oy = 430, 10

    p = libui.DrawPath()
    p.add_rectangle(ox, oy, 150, 70)
    p.end()
    lb = libui.DrawBrush()
    lb.type = libui.BrushType.LINEAR_GRADIENT
    lb.x0, lb.y0 = ox, oy
    lb.x1, lb.y1 = ox + 150, oy + 70
    lb.set_stops([
        (0.0, 1.0, 0.0, 0.0, 1.0),
        (0.5, 1.0, 1.0, 0.0, 1.0),
        (1.0, 0.0, 0.0, 1.0, 1.0),
    ])
    ctx.fill(p, lb)

    cx, cy, r = ox + 75, oy + 130, 40
    p2 = libui.DrawPath()
    p2.new_figure_with_arc(cx, cy, r, 0, 2 * math.pi, False)
    p2.end()
    rb = libui.DrawBrush()
    rb.type = libui.BrushType.RADIAL_GRADIENT
    rb.x0, rb.y0 = cx, cy
    rb.x1, rb.y1 = cx, cy
    rb.outer_radius = r
    rb.set_stops([
        (0.0, 1.0, 1.0, 1.0, 1.0),
        (1.0, 0.2, 0.0, 0.6, 1.0),
    ])
    ctx.fill(p2, rb)


def _draw_stroke_styles(ctx):
    y_base = 120
    black = libui.DrawBrush()
    black.r, black.g, black.b, black.a = 0.0, 0.0, 0.0, 1.0

    caps = [libui.LineCap.FLAT, libui.LineCap.ROUND, libui.LineCap.SQUARE]
    cap_names = ["Flat", "Round", "Square"]
    for i, (cap, name) in enumerate(zip(caps, cap_names)):
        y = y_base + i * 25
        p = libui.DrawPath()
        p.new_figure(20, y)
        p.line_to(150, y)
        p.end()
        sp = libui.DrawStrokeParams()
        sp.thickness = 6.0
        sp.cap = cap
        ctx.stroke(p, black, sp)
        astr = libui.AttributedString(name)
        font = {"family": "sans-serif", "size": 10.0}
        layout = libui.DrawTextLayout(astr, font, 200)
        ctx.text(layout, 155, y - 6)

    joins = [libui.LineJoin.MITER, libui.LineJoin.ROUND, libui.LineJoin.BEVEL]
    join_names = ["Miter", "Round", "Bevel"]
    for i, (join, name) in enumerate(zip(joins, join_names)):
        x_off = 230 + i * 70
        y = y_base
        p = libui.DrawPath()
        p.new_figure(x_off, y + 50)
        p.line_to(x_off + 20, y)
        p.line_to(x_off + 40, y + 50)
        p.end()
        sp = libui.DrawStrokeParams()
        sp.thickness = 5.0
        sp.join = join
        ctx.stroke(p, black, sp)
        astr = libui.AttributedString(name)
        font = {"family": "sans-serif", "size": 10.0}
        layout = libui.DrawTextLayout(astr, font, 200)
        ctx.text(layout, x_off + 5, y + 55)

    y_dash = y_base + 85
    p = libui.DrawPath()
    p.new_figure(20, y_dash)
    p.line_to(200, y_dash)
    p.end()
    sp = libui.DrawStrokeParams()
    sp.thickness = 3.0
    sp.set_dashes([10.0, 5.0, 3.0, 5.0])
    ctx.stroke(p, black, sp)
    astr = libui.AttributedString("Dashed")
    font = {"family": "sans-serif", "size": 10.0}
    layout = libui.DrawTextLayout(astr, font, 200)
    ctx.text(layout, 210, y_dash - 6)

    y_bez = y_dash + 25
    p = libui.DrawPath()
    p.new_figure(20, y_bez + 30)
    p.bezier_to(80, y_bez - 30, 160, y_bez + 60, 250, y_bez)
    p.end()
    sp = libui.DrawStrokeParams()
    sp.thickness = 2.5
    sp.cap = libui.LineCap.ROUND
    purple = libui.DrawBrush()
    purple.r, purple.g, purple.b, purple.a = 0.5, 0.0, 0.7, 1.0
    ctx.stroke(p, purple, sp)
    astr = libui.AttributedString("Bezier")
    font = {"family": "sans-serif", "size": 10.0}
    layout = libui.DrawTextLayout(astr, font, 200)
    ctx.text(layout, 255, y_bez - 6)


def _draw_attributed_text(ctx, area_w):
    y = 290
    text = "Bold Colored Italic Underlined Highlight Family Size"
    astr = libui.AttributedString(text)
    astr.set_attribute(libui.weight_attribute(libui.TextWeight.BOLD), 0, 4)
    astr.set_attribute(libui.color_attribute(0.8, 0.0, 0.0, 1.0), 5, 12)
    astr.set_attribute(libui.italic_attribute(libui.TextItalic.ITALIC), 13, 19)
    astr.set_attribute(libui.underline_attribute(libui.Underline.SINGLE), 20, 30)
    astr.set_attribute(libui.background_attribute(1.0, 1.0, 0.0, 0.5), 31, 40)
    astr.set_attribute(libui.family_attribute("serif"), 41, 47)
    astr.set_attribute(libui.size_attribute(22.0), 48, 52)
    font = {"family": "sans-serif", "size": 14.0}
    width = min(area_w - 40, 600.0)
    layout = libui.DrawTextLayout(astr, font, width)
    ctx.text(layout, 20, y)


def _draw_rotated_rect(ctx):
    cx, cy = 360, 330
    m = libui.DrawMatrix()
    m.set_identity()
    m.rotate(cx, cy, 30)
    ctx.save()
    ctx.transform(m)
    p = libui.DrawPath()
    p.add_rectangle(cx - 30, cy - 15, 60, 30)
    p.end()
    b = libui.DrawBrush()
    b.r, b.g, b.b, b.a = 0.0, 0.6, 0.6, 0.7
    ctx.fill(p, b)
    ctx.restore()


def build_drawing_tab():
    return VBox(stretchy(DrawArea(on_draw=_on_draw)))


# ── Tab 5: Data Table ───────────────────────────────────────────────

def build_table_tab(app: App):
    status = State("Table events appear here.")

    data = ListState([
        {"checked": 1, "name": "Alice Johnson", "role": "Engineer", "score": 85, "action": "Details"},
        {"checked": 0, "name": "Bob Smith", "role": "Designer", "score": 72, "action": "Details"},
        {"checked": 1, "name": "Carol White", "role": "Manager", "score": 90, "action": "Details"},
        {"checked": 0, "name": "Dave Brown", "role": "Intern", "score": 45, "action": "Details"},
        {"checked": 1, "name": "Eve Davis", "role": "Engineer", "score": 95, "action": "Details"},
        {"checked": 0, "name": "Frank Miller", "role": "Analyst", "score": 68, "action": "Details"},
        {"checked": 1, "name": "Grace Lee", "role": "Lead", "score": 88, "action": "Details"},
        {"checked": 0, "name": "Hank Wilson", "role": "QA", "score": 77, "action": "Details"},
    ])

    add_counter = State(len(data))

    def on_button_click(row):
        if row < len(data):
            d = data[row]
            app.msg_box("Details", f"{d['name']} — {d['role']}\nScore: {d['score']}")

    table = DataTable(
        data,
        CheckboxTextColumn("Employee", checkbox_key="checked", text_key="name"),
        TextColumn("Role", key="role"),
        ProgressColumn("Score", key="score"),
        ButtonColumn("Action", text_key="action", on_click=on_button_click),
        on_row_clicked=lambda row: status.set(
            f"Clicked row {row}: {data[row]['name']}" if row < len(data) else ""),
        on_row_double_clicked=lambda row: status.set(
            f"Double-clicked row {row}: {data[row]['name']}" if row < len(data) else ""),
        on_header_clicked=lambda col: status.set(f"Header clicked: column {col}"),
        on_selection_changed=lambda: status.set(
            f"Selection: {table.widget.selection}" if table.widget else ""),
    )

    def do_add():
        add_counter.update(lambda x: x + 1)
        data.append({
            "checked": 0,
            "name": f"New Person {add_counter.value}",
            "role": "New",
            "score": 50,
            "action": "Details",
        })
        status.set(f"Added row {len(data) - 1}")

    def do_remove():
        if len(data) == 0:
            return
        name = data[len(data) - 1]["name"]
        data.pop()
        status.set(f"Removed: {name}")

    return VBox(
        StatusPanel(status),
        stretchy(table),
        HBox(
            Button("Add Row", on_clicked=do_add),
            Button("Remove Last", on_clicked=do_remove),
        ),
    )


# ── Menus ────────────────────────────────────────────────────────────

def build_menus(app: App):
    toggle_state = State(False)

    def do_open():
        path = app.open_file()
        if path:
            app.msg_box("Open File", f"Selected: {path}")

    def do_open_folder():
        path = app.open_folder()
        if path:
            app.msg_box("Open Folder", f"Selected: {path}")

    def do_save():
        path = app.save_file()
        if path:
            app.msg_box("Save File", f"Will save to: {path}")

    def do_toggle():
        state = "ON" if toggle_state.value else "OFF"
        app.msg_box("Toggle Feature", f"Feature is now {state}")

    def do_docs():
        app.msg_box("Documentation",
                     "Visit the python-libui-ng repository for full docs.")

    return [
        MenuDef("File",
            MenuItem("Open File...", on_click=do_open),
            MenuItem("Open Folder...", on_click=do_open_folder),
            MenuItem("Save As...", on_click=do_save),
            MenuSeparator(),
            QuitItem(),
        ),
        MenuDef("Edit",
            PreferencesItem(),
            MenuSeparator(),
            CheckMenuItem("Toggle Feature", checked=toggle_state, on_click=do_toggle),
        ),
        MenuDef("Help",
            AboutItem(),
            MenuItem("Documentation", on_click=do_docs),
        ),
    ]


# ── Main ─────────────────────────────────────────────────────────────

async def main():
    app = App()

    content = Tab(
        ("Basic Controls", build_basic_tab(app)),
        ("Selectors & Numbers", build_selectors_tab()),
        ("Rich Input", build_rich_input_tab()),
        ("Layout", build_layout_tab()),
        ("Drawing", build_drawing_tab()),
        ("Data Table", build_table_tab(app)),
    )

    app.build(
        menus=build_menus(app),
        window=Window(
            "Python libui-ng Showcase", 900, 700,
            child=content,
            has_menubar=True,
        ),
    )
    app.show()
    await app.wait()


if __name__ == "__main__":
    libui.run(main())
