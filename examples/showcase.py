"""Comprehensive showcase of every widget in python-libui-ng.

Demonstrates all ~30 widget types, drawing primitives, tables, menus, and
dialogs — organised into six tabbed panels with interactive connections
between controls.

Usage:
    python examples/showcase.py
"""

import asyncio
import math

import libui


# ── Menus (must be created BEFORE the Window) ───────────────────────


def build_menus(window_ref):
    """Build application menus. Returns list of refs to keep alive."""
    refs = []

    # File menu
    file_menu = libui.Menu("File")
    refs.append(file_menu)

    item_open = file_menu.append_item("Open File...")
    item_open.on_clicked(lambda: _do_open_file(window_ref))

    item_folder = file_menu.append_item("Open Folder...")
    item_folder.on_clicked(lambda: _do_open_folder(window_ref))

    item_save = file_menu.append_item("Save As...")
    item_save.on_clicked(lambda: _do_save_file(window_ref))

    file_menu.append_separator()
    file_menu.append_quit_item()

    # Edit menu
    edit_menu = libui.Menu("Edit")
    refs.append(edit_menu)

    edit_menu.append_preferences_item()
    edit_menu.append_separator()

    toggle_item = edit_menu.append_check_item("Toggle Feature")
    toggle_item.on_clicked(lambda: _do_toggle(toggle_item, window_ref))
    refs.append(toggle_item)

    # Help menu
    help_menu = libui.Menu("Help")
    refs.append(help_menu)

    help_menu.append_about_item()

    docs_item = help_menu.append_item("Documentation")
    docs_item.on_clicked(lambda: _do_docs(window_ref))

    return refs


def _do_open_file(wref):
    w = wref[0]
    if w is None:
        return
    path = libui.open_file(w)
    if path:
        libui.msg_box(w, "Open File", f"Selected: {path}")


def _do_open_folder(wref):
    w = wref[0]
    if w is None:
        return
    path = libui.open_folder(w)
    if path:
        libui.msg_box(w, "Open Folder", f"Selected: {path}")


def _do_save_file(wref):
    w = wref[0]
    if w is None:
        return
    path = libui.save_file(w)
    if path:
        libui.msg_box(w, "Save File", f"Will save to: {path}")


def _do_toggle(item, wref):
    w = wref[0]
    if w is None:
        return
    state = "ON" if item.checked else "OFF"
    libui.msg_box(w, "Toggle Feature", f"Feature is now {state}")


def _do_docs(wref):
    w = wref[0]
    if w is None:
        return
    libui.msg_box(
        w, "Documentation", "Visit the python-libui-ng repository for full docs."
    )


# ── Tab 0: Basic Controls ───────────────────────────────────────────


def build_basic_tab(window):
    vbox = libui.VerticalBox(padded=True)

    status = libui.Label("Interact with the controls below.")
    vbox.append(status)

    # Text Entry group
    entry_group = libui.Group("Text Entry")
    entry_group.margined = True
    vbox.append(entry_group)

    form = libui.Form(padded=True)
    entry_group.set_child(form)

    entry_normal = libui.Entry()
    entry_password = libui.Entry(type="password")
    entry_search = libui.Entry(type="search")
    entries = [entry_normal, entry_password, entry_search]

    entry_normal.on_changed(
        lambda: _update_status(status, f"Normal entry: {entry_normal.text}")
    )
    entry_password.on_changed(
        lambda: _update_status(
            status, f"Password entry changed (len={len(entry_password.text)})"
        )
    )
    entry_search.on_changed(
        lambda: _update_status(status, f"Search entry: {entry_search.text}")
    )

    form.append("Normal:", entry_normal)
    form.append("Password:", entry_password)
    form.append("Search:", entry_search)

    vbox.append(libui.Separator())

    # Buttons & Checkboxes group
    btn_group = libui.Group("Buttons & Checkboxes")
    btn_group.margined = True
    vbox.append(btn_group)

    hbox = libui.HorizontalBox(padded=True)
    btn_group.set_child(hbox)

    left_col = libui.VerticalBox(padded=True)
    right_col = libui.VerticalBox(padded=True)
    hbox.append(left_col, stretchy=True)
    hbox.append(right_col, stretchy=True)

    # Left column: buttons and feature checkboxes
    click_count = [0]
    btn_click = libui.Button("Click Me")

    def on_click():
        click_count[0] += 1
        status.text = f"Button clicked {click_count[0]} time(s)"

    btn_click.on_clicked(on_click)
    left_col.append(btn_click)

    btn_reset = libui.Button("Reset")
    btn_reset.on_clicked(
        lambda: _update_status(status, "Interact with the controls below.")
    )
    left_col.append(btn_reset)

    cb_feature = libui.Checkbox("Enable feature")
    cb_feature.on_toggled(
        lambda: _update_status(
            status, f"Feature {'enabled' if cb_feature.checked else 'disabled'}"
        )
    )
    left_col.append(cb_feature)

    cb_readonly = libui.Checkbox("Read-only entries")

    def toggle_readonly():
        ro = cb_readonly.checked
        for e in entries:
            e.read_only = ro
        status.text = f"Entries are {'read-only' if ro else 'editable'}"

    cb_readonly.on_toggled(toggle_readonly)
    left_col.append(cb_readonly)

    # Right column: window toggles
    cb_borderless = libui.Checkbox("Borderless window")
    cb_borderless.on_toggled(
        lambda: setattr(window, "borderless", cb_borderless.checked)
    )
    right_col.append(cb_borderless)

    cb_fullscreen = libui.Checkbox("Fullscreen")
    cb_fullscreen.on_toggled(
        lambda: setattr(window, "fullscreen", cb_fullscreen.checked)
    )
    right_col.append(cb_fullscreen)

    return vbox


def _update_status(label, text):
    label.text = text


# ── Tab 1: Selectors & Numbers ──────────────────────────────────────


def build_selectors_tab():
    vbox = libui.VerticalBox(padded=True)

    status = libui.Label("Adjust the controls below.")
    vbox.append(status)

    # Numeric Controls group
    num_group = libui.Group("Numeric Controls")
    num_group.margined = True
    vbox.append(num_group)

    form = libui.Form(padded=True)
    num_group.set_child(form)

    slider = libui.Slider(0, 100)
    slider.has_tooltip = True
    spinbox = libui.Spinbox(0, 100)
    progress = libui.ProgressBar()

    syncing = [False]

    def on_slider_changed():
        if syncing[0]:
            return
        syncing[0] = True
        v = slider.value
        spinbox.value = v
        progress.value = v
        status.text = f"Value: {v}"
        syncing[0] = False

    def on_spinbox_changed():
        if syncing[0]:
            return
        syncing[0] = True
        v = spinbox.value
        slider.value = v
        progress.value = v
        status.text = f"Value: {v}"
        syncing[0] = False

    slider.on_changed(on_slider_changed)
    spinbox.on_changed(on_spinbox_changed)

    form.append("Slider:", slider)
    form.append("Spinbox:", spinbox)
    form.append("Progress:", progress)

    vbox.append(libui.Separator())

    # Selection Controls group
    sel_group = libui.Group("Selection Controls")
    sel_group.margined = True
    vbox.append(sel_group)

    sel_form = libui.Form(padded=True)
    sel_group.set_child(sel_form)

    radio = libui.RadioButtons()
    for label in ("Low", "Medium", "High", "Ultra"):
        radio.append(label)
    radio_labels = ["Low", "Medium", "High", "Ultra"]
    radio.on_selected(
        lambda: _update_status(status, f"Radio: {radio_labels[radio.selected]}")
    )

    combo = libui.Combobox()
    combo_items = ["Red", "Green", "Blue", "Yellow"]
    for item in combo_items:
        combo.append(item)
    combo.selected = 0
    combo.on_selected(
        lambda: _update_status(status, f"Combobox: {combo_items[combo.selected]}")
    )

    ecb = libui.EditableCombobox()
    for item in ("Apple", "Banana", "Cherry"):
        ecb.append(item)
    ecb.on_changed(lambda: _update_status(status, f"EditableCombobox: {ecb.text}"))

    sel_form.append("Quality:", radio)
    sel_form.append("Color:", combo)
    sel_form.append("Fruit:", ecb)

    return vbox


# ── Tab 2: Rich Input ───────────────────────────────────────────────


def build_rich_input_tab():
    hbox = libui.HorizontalBox(padded=True)

    # Left: Multiline Entry
    ml_group = libui.Group("Multiline Entry")
    ml_group.margined = True
    hbox.append(ml_group, stretchy=True)

    ml_vbox = libui.VerticalBox(padded=True)
    ml_group.set_child(ml_vbox)

    mle = libui.MultilineEntry(wrapping=True)
    mle.text = "Type or paste text here.\nMultiple lines supported."
    ml_vbox.append(mle, stretchy=True)

    ml_btn_box = libui.HorizontalBox(padded=True)
    ml_vbox.append(ml_btn_box)

    append_count = [0]
    btn_append = libui.Button("Append Text")

    def do_append():
        append_count[0] += 1
        mle.append(f"\nAppended line #{append_count[0]}")

    btn_append.on_clicked(do_append)
    ml_btn_box.append(btn_append)

    btn_clear = libui.Button("Clear")
    btn_clear.on_clicked(lambda: setattr(mle, "text", ""))
    ml_btn_box.append(btn_clear)

    cb_ml_ro = libui.Checkbox("Read Only")
    cb_ml_ro.on_toggled(lambda: setattr(mle, "read_only", cb_ml_ro.checked))
    ml_btn_box.append(cb_ml_ro)

    # Right: Pickers
    pick_group = libui.Group("Pickers")
    pick_group.margined = True
    hbox.append(pick_group, stretchy=True)

    pick_vbox = libui.VerticalBox(padded=True)
    pick_group.set_child(pick_vbox)

    pick_form = libui.Form(padded=True)
    pick_vbox.append(pick_form, stretchy=True)

    pick_status = libui.Label("Pick a value to see it here.")
    pick_vbox.append(pick_status)

    color_btn = libui.ColorButton()
    color_btn.on_changed(
        lambda: _update_status(
            pick_status,
            "Color: R={:.2f} G={:.2f} B={:.2f} A={:.2f}".format(*color_btn.color),
        )
    )

    font_btn = libui.FontButton()
    font_btn.on_changed(
        lambda: _update_status(
            pick_status, "Font: {family} {size}pt".format(**font_btn.font)
        )
    )

    dtp_full = libui.DateTimePicker()
    dtp_full.on_changed(
        lambda: _update_status(
            pick_status,
            "DateTime: {0:04d}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}".format(
                *dtp_full.time[:6]
            ),
        )
    )

    dtp_date = libui.DateTimePicker(type="date")
    dtp_date.on_changed(
        lambda: _update_status(
            pick_status, "Date: {0:04d}-{1:02d}-{2:02d}".format(*dtp_date.time[:3])
        )
    )

    dtp_time = libui.DateTimePicker(type="time")
    dtp_time.on_changed(
        lambda: _update_status(
            pick_status, "Time: {3:02d}:{4:02d}:{5:02d}".format(*dtp_time.time[:6])
        )
    )

    pick_form.append("Color:", color_btn)
    pick_form.append("Font:", font_btn)
    pick_form.append("Date & Time:", dtp_full)
    pick_form.append("Date:", dtp_date)
    pick_form.append("Time:", dtp_time)

    return hbox


# ── Tab 3: Layout ───────────────────────────────────────────────────


def build_layout_tab():
    vbox = libui.VerticalBox(padded=True)

    # Grid Layout group
    grid_group = libui.Group("Grid Layout")
    grid_group.margined = True
    vbox.append(grid_group)

    grid = libui.Grid(padded=True)
    grid_group.set_child(grid)

    lbl_name = libui.Label("Name:")
    entry_name = libui.Entry()
    grid.append(lbl_name, 0, 0, 1, 1, False, libui.Align.END, False, libui.Align.FILL)
    grid.append(entry_name, 1, 0, 1, 1, True, libui.Align.FILL, False, libui.Align.FILL)

    lbl_email = libui.Label("Email:")
    entry_email = libui.Entry()
    grid.append(lbl_email, 0, 1, 1, 1, False, libui.Align.END, False, libui.Align.FILL)
    grid.append(
        entry_email, 1, 1, 1, 1, True, libui.Align.FILL, False, libui.Align.FILL
    )

    btn_submit = libui.Button("Submit")
    grid.append(
        btn_submit, 0, 2, 2, 1, False, libui.Align.CENTER, False, libui.Align.FILL
    )

    vbox.append(libui.Separator())

    # Form Layout group
    form_group = libui.Group("Form Layout")
    form_group.margined = True
    vbox.append(form_group)

    form = libui.Form(padded=True)
    form_group.set_child(form)

    form.append("Username:", libui.Entry())
    form.append("Password:", libui.Entry(type="password"))

    role_combo = libui.Combobox()
    for r in ("Admin", "Editor", "Viewer"):
        role_combo.append(r)
    role_combo.selected = 0
    form.append("Role:", role_combo)

    form.append("Bio:", libui.MultilineEntry(wrapping=True), stretchy=True)

    vbox.append(libui.Separator())

    # Nested Boxes group
    nest_group = libui.Group("Nested Boxes")
    nest_group.margined = True
    vbox.append(nest_group)

    outer_hbox = libui.HorizontalBox(padded=True)
    nest_group.set_child(outer_hbox)

    for col_label in ("Column A", "Column B", "Column C"):
        col_vbox = libui.VerticalBox(padded=True)
        col_vbox.append(libui.Label(col_label))
        col_vbox.append(libui.Button(f"Btn {col_label[-1]}"))
        col_vbox.append(libui.ProgressBar())
        outer_hbox.append(col_vbox, stretchy=True)

    return vbox


# ── Tab 4: Drawing ──────────────────────────────────────────────────


def build_drawing_tab():
    vbox = libui.VerticalBox(padded=True)
    area = libui.Area(_on_draw)
    vbox.append(area, stretchy=True)
    return vbox


def _on_draw(ctx, area_w, area_h, clip_x, clip_y, clip_w, clip_h):
    _draw_filled_shapes(ctx)
    _draw_gradients(ctx)
    _draw_stroke_styles(ctx)
    _draw_attributed_text(ctx, area_w)
    _draw_rotated_rect(ctx)


def _draw_filled_shapes(ctx):
    # Red rectangle
    p = libui.DrawPath()
    p.add_rectangle(20, 20, 120, 70)
    p.end()
    b = libui.DrawBrush()
    b.r, b.g, b.b, b.a = 0.85, 0.15, 0.15, 1.0
    ctx.fill(p, b)

    # Green circle
    p2 = libui.DrawPath()
    p2.new_figure_with_arc(230, 55, 35, 0, 2 * math.pi, False)
    p2.end()
    b2 = libui.DrawBrush()
    b2.r, b2.g, b2.b, b2.a = 0.15, 0.7, 0.15, 1.0
    ctx.fill(p2, b2)

    # Blue triangle
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

    # Linear gradient rectangle
    p = libui.DrawPath()
    p.add_rectangle(ox, oy, 150, 70)
    p.end()

    lb = libui.DrawBrush()
    lb.type = libui.BrushType.LINEAR_GRADIENT
    lb.x0, lb.y0 = ox, oy
    lb.x1, lb.y1 = ox + 150, oy + 70
    lb.set_stops(
        [
            (0.0, 1.0, 0.0, 0.0, 1.0),
            (0.5, 1.0, 1.0, 0.0, 1.0),
            (1.0, 0.0, 0.0, 1.0, 1.0),
        ]
    )
    ctx.fill(p, lb)

    # Radial gradient circle
    cx, cy, r = ox + 75, oy + 130, 40
    p2 = libui.DrawPath()
    p2.new_figure_with_arc(cx, cy, r, 0, 2 * math.pi, False)
    p2.end()

    rb = libui.DrawBrush()
    rb.type = libui.BrushType.RADIAL_GRADIENT
    rb.x0, rb.y0 = cx, cy
    rb.x1, rb.y1 = cx, cy
    rb.outer_radius = r
    rb.set_stops(
        [
            (0.0, 1.0, 1.0, 1.0, 1.0),
            (1.0, 0.2, 0.0, 0.6, 1.0),
        ]
    )
    ctx.fill(p2, rb)


def _draw_stroke_styles(ctx):
    y_base = 120

    black = libui.DrawBrush()
    black.r, black.g, black.b, black.a = 0.0, 0.0, 0.0, 1.0

    # Line cap styles: FLAT, ROUND, SQUARE
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

        # label
        astr = libui.AttributedString(name)
        font = {"family": "sans-serif", "size": 10.0}
        layout = libui.DrawTextLayout(astr, font, 200)
        ctx.text(layout, 155, y - 6)

    # Line join styles: MITER, ROUND, BEVEL
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

    # Dashed line
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

    # Bezier curve
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

    # Bold: "Bold" (0..4)
    astr.set_attribute(libui.weight_attribute(libui.TextWeight.BOLD), 0, 4)

    # Colored: "Colored" (5..12)
    astr.set_attribute(libui.color_attribute(0.8, 0.0, 0.0, 1.0), 5, 12)

    # Italic: "Italic" (13..19)
    astr.set_attribute(libui.italic_attribute(libui.TextItalic.ITALIC), 13, 19)

    # Underlined: "Underlined" (20..30)
    astr.set_attribute(libui.underline_attribute(libui.Underline.SINGLE), 20, 30)

    # Background highlight: "Highlight" (31..40)
    astr.set_attribute(libui.background_attribute(1.0, 1.0, 0.0, 0.5), 31, 40)

    # Custom family: "Family" (41..47)
    astr.set_attribute(libui.family_attribute("serif"), 41, 47)

    # Custom size: "Size" (48..52)
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


# ── Tab 5: Data Table ───────────────────────────────────────────────


def build_table_tab(window):
    vbox = libui.VerticalBox(padded=True)

    status = libui.Label("Table events appear here.")
    vbox.append(status)

    # Table data: [checked, name, role, progress, button_text]
    data = [
        [1, "Alice Johnson", "Engineer", 85, "Details"],
        [0, "Bob Smith", "Designer", 72, "Details"],
        [1, "Carol White", "Manager", 90, "Details"],
        [0, "Dave Brown", "Intern", 45, "Details"],
        [1, "Eve Davis", "Engineer", 95, "Details"],
        [0, "Frank Miller", "Analyst", 68, "Details"],
        [1, "Grace Lee", "Lead", 88, "Details"],
        [0, "Hank Wilson", "QA", 77, "Details"],
    ]

    def num_columns():
        return 5

    def column_type(col):
        if col in (0, 3):
            return libui.TableValueType.INT
        return libui.TableValueType.STRING

    def num_rows():
        return len(data)

    def cell_value(row, col):
        v = data[row][col]
        return int(v) if col in (0, 3) else str(v)

    def set_cell_value(row, col, value):
        data[row][col] = value
        if col == 0:
            name = data[row][1]
            state = "checked" if value else "unchecked"
            status.text = f"{name}: {state}"
        elif col == 4:
            name = data[row][1]
            role = data[row][2]
            libui.msg_box(window, "Details", f"{name} — {role}\nScore: {data[row][3]}")

    model = libui.TableModel(
        num_columns, column_type, num_rows, cell_value, set_cell_value
    )

    table = libui.Table(model)
    table.append_checkbox_text_column(
        "Employee", 0, libui.TableModelColumn.ALWAYS_EDITABLE, 1
    )
    table.append_text_column("Role", 2)
    table.append_progress_bar_column("Score", 3)
    table.append_button_column("Action", 4, libui.TableModelColumn.ALWAYS_EDITABLE)

    table.on_row_clicked(
        lambda row: _update_status(status, f"Clicked row {row}: {data[row][1]}")
    )
    table.on_row_double_clicked(
        lambda row: _update_status(status, f"Double-clicked row {row}: {data[row][1]}")
    )
    table.on_header_clicked(
        lambda col: _update_status(status, f"Header clicked: column {col}")
    )
    table.on_selection_changed(
        lambda: _update_status(status, f"Selection: {table.selection}")
    )

    vbox.append(table, stretchy=True)

    # Add / Remove buttons
    btn_box = libui.HorizontalBox(padded=True)
    vbox.append(btn_box)

    add_counter = [len(data)]
    btn_add = libui.Button("Add Row")

    def do_add():
        add_counter[0] += 1
        new_row = [0, f"New Person {add_counter[0]}", "New", 50, "Details"]
        data.append(new_row)
        model.row_inserted(len(data) - 1)
        status.text = f"Added row {len(data) - 1}"

    btn_add.on_clicked(do_add)
    btn_box.append(btn_add)

    btn_remove = libui.Button("Remove Last")

    def do_remove():
        if len(data) == 0:
            return
        idx = len(data) - 1
        name = data[idx][1]
        data.pop()
        model.row_deleted(idx)
        status.text = f"Removed: {name}"

    btn_remove.on_clicked(do_remove)
    btn_box.append(btn_remove)

    return vbox


# ── Main ─────────────────────────────────────────────────────────────


async def main():
    window_ref = [None]
    build_menus(window_ref)

    window = libui.Window("Python libui-ng Showcase", 900, 700, has_menubar=True)
    window_ref[0] = window

    tab = libui.Tab()
    tab.append("Basic Controls", build_basic_tab(window))
    tab.append("Selectors & Numbers", build_selectors_tab())
    tab.append("Rich Input", build_rich_input_tab())
    tab.append("Layout", build_layout_tab())
    tab.append("Drawing", build_drawing_tab())
    tab.append("Data Table", build_table_tab(window))

    for i in range(tab.num_pages()):
        tab.set_margined(i, True)

    window.set_child(tab)

    def on_closing():
        libui.quit()
        return True

    window.on_closing(on_closing)
    window.show()

    await asyncio.Event().wait()


if __name__ == "__main__":
    libui.run(main())
