"""Comprehensive widget showcase.

Demonstrates all widget types using the declarative UI layer —
reactive State, auto-syncing, and composable nodes.

Usage:
    python examples/showcase.py
"""

import math

import libui
from libui.declarative import (
    AboutItem,
    App,
    Button,
    ButtonColumn,
    Checkbox,
    CheckMenuItem,
    ColorButton,
    Combobox,
    DataTable,
    DateTimePicker,
    DrawArea,
    ScrollingDrawArea,
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
    CheckboxColumn,
    CheckboxTextColumn,
    TextColumn,
    VBox,
    Window,
    stretchy,
)


# -- Reusable components ---------------------------------------------


def StatusPanel(status: State[str]) -> Label:
    return Label(text=status)


# -- Tab 0: Basic Controls -------------------------------------------


def build_basic_tab(app: App):
    status = State("Interact with the controls below.")
    click_count = State(0)
    read_only = State(False)

    def on_click():
        click_count.update(lambda x: x + 1)
        status.set(f"Button clicked {click_count.value} time(s)")

    return VBox(
        StatusPanel(status),
        Group(
            "Text Entry",
            Form(
                (
                    "Normal:",
                    Entry(
                        read_only=read_only,
                        on_changed=lambda text: status.set(f"Normal entry: {text}"),
                    ),
                ),
                (
                    "Password:",
                    Entry(
                        type="password",
                        read_only=read_only,
                        on_changed=lambda text: status.set(
                            f"Password entry changed (len={len(text)})"
                        ),
                    ),
                ),
                (
                    "Search:",
                    Entry(
                        type="search",
                        read_only=read_only,
                        on_changed=lambda text: status.set(f"Search entry: {text}"),
                    ),
                ),
            ),
        ),
        Separator(),
        Group(
            "Buttons & Checkboxes",
            HBox(
                stretchy(
                    VBox(
                        Button("Click Me", on_clicked=on_click),
                        Button(
                            "Reset",
                            on_clicked=lambda: status.set(
                                "Interact with the controls below."
                            ),
                        ),
                        Checkbox(
                            "Enable feature",
                            on_toggled=lambda checked: status.set(
                                f"Feature {'enabled' if checked else 'disabled'}"
                            ),
                        ),
                        Checkbox(
                            "Read-only entries",
                            on_toggled=lambda checked: (
                                read_only.set(checked),
                                status.set(
                                    f"Entries are {'read-only' if checked else 'editable'}"
                                ),
                            ),
                        ),
                    )
                ),
                stretchy(
                    VBox(
                        Checkbox(
                            "Borderless window",
                            on_toggled=lambda checked: (
                                setattr(app.window, "borderless", checked)
                                if app.window
                                else None
                            ),
                        ),
                        Checkbox(
                            "Fullscreen",
                            on_toggled=lambda checked: (
                                setattr(app.window, "fullscreen", checked)
                                if app.window
                                else None
                            ),
                        ),
                    )
                ),
            ),
        ),
    )


# -- Tab 1: Selectors & Numbers --------------------------------------


def build_selectors_tab():
    status = State("Adjust the controls below.")
    value = State(0)
    value.subscribe(lambda: status.set(f"Value: {value.value}"))

    radio_labels = ["Low", "Medium", "High", "Ultra"]
    combo_items = ["Red", "Green", "Blue", "Yellow"]

    return VBox(
        StatusPanel(status),
        Group(
            "Numeric Controls",
            Form(
                ("Slider:", Slider(0, 100, value=value)),
                ("Spinbox:", Spinbox(0, 100, value=value)),
                ("Progress:", ProgressBar(value=value)),
            ),
        ),
        Separator(),
        Group(
            "Selection Controls",
            Form(
                (
                    "Quality:",
                    RadioButtons(
                        items=radio_labels,
                        on_selected=lambda idx: status.set(
                            f"Radio: {radio_labels[idx]}" if idx >= 0 else "Radio: none"
                        ),
                    ),
                ),
                (
                    "Color:",
                    Combobox(
                        items=combo_items,
                        selected=0,
                        on_selected=lambda idx: status.set(
                            f"Combobox: {combo_items[idx]}"
                        ),
                    ),
                ),
                (
                    "Fruit:",
                    EditableCombobox(
                        items=["Apple", "Banana", "Cherry"],
                        on_changed=lambda text: status.set(f"EditableCombobox: {text}"),
                    ),
                ),
            ),
        ),
    )


# -- Tab 2: Rich Input -----------------------------------------------


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
        stretchy(
            Group(
                "Multiline Entry",
                VBox(
                    stretchy(mle),
                    HBox(
                        Button("Append Text", on_clicked=do_append),
                        Button("Clear", on_clicked=do_clear),
                        Checkbox(
                            "Read Only",
                            on_toggled=lambda checked: mle_read_only.set(checked),
                        ),
                    ),
                ),
            )
        ),
        stretchy(
            Group(
                "Pickers",
                VBox(
                    stretchy(
                        Form(
                            (
                                "Color:",
                                ColorButton(
                                    on_changed=lambda color: pick_status.set(
                                        "Color: R={:.2f} G={:.2f} B={:.2f} A={:.2f}".format(
                                            *color
                                        )
                                    ),
                                ),
                            ),
                            (
                                "Font:",
                                FontButton(
                                    on_changed=lambda font: pick_status.set(
                                        "Font: {family} {size}pt".format(**font)
                                    ),
                                ),
                            ),
                            (
                                "Date & Time:",
                                DateTimePicker(
                                    on_changed=lambda time: pick_status.set(
                                        "DateTime: {0:04d}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}".format(
                                            *time[:6]
                                        )
                                    ),
                                ),
                            ),
                            (
                                "Date:",
                                DateTimePicker(
                                    type="date",
                                    on_changed=lambda time: pick_status.set(
                                        "Date: {0:04d}-{1:02d}-{2:02d}".format(
                                            *time[:3]
                                        )
                                    ),
                                ),
                            ),
                            (
                                "Time:",
                                DateTimePicker(
                                    type="time",
                                    on_changed=lambda time: pick_status.set(
                                        "Time: {3:02d}:{4:02d}:{5:02d}".format(
                                            *time[:6]
                                        )
                                    ),
                                ),
                            ),
                        )
                    ),
                    Label(text=pick_status),
                ),
            )
        ),
    )


# -- Tab 3: Layout ---------------------------------------------------


def build_layout_tab():
    return VBox(
        Group(
            "Grid Layout",
            Grid(
                GridCell(Label("Name:"), 0, 0, halign=libui.Align.END),
                GridCell(Entry(), 1, 0, hexpand=True),
                GridCell(Label("Email:"), 0, 1, halign=libui.Align.END),
                GridCell(Entry(), 1, 1, hexpand=True),
                GridCell(Button("Submit"), 0, 2, xspan=2, halign=libui.Align.CENTER),
                padded=True,
            ),
        ),
        Separator(),
        Group(
            "Form Layout",
            Form(
                ("Username:", Entry()),
                ("Password:", Entry(type="password")),
                ("Role:", Combobox(items=["Admin", "Editor", "Viewer"], selected=0)),
                ("Bio:", MultilineEntry(wrapping=True), True),
            ),
        ),
        Separator(),
        Group(
            "Nested Boxes",
            HBox(
                *[
                    stretchy(
                        VBox(
                            Label(f"Column {c}"),
                            Button(f"Btn {c}"),
                            ProgressBar(),
                        )
                    )
                    for c in ("A", "B", "C")
                ]
            ),
        ),
    )


# -- Tab 4: Drawing --------------------------------------------------


def _draw_label(ctx, text, x, y, size=10.0):
    """Draw a text label with a background pill for readability on any theme."""
    astr = libui.AttributedString(text)
    astr.set_attribute(libui.color_attribute(0.0, 0.0, 0.0, 1.0), 0, len(text))
    font = {"family": "sans-serif", "size": size}
    layout = libui.DrawTextLayout(astr, font, 800)
    w, h = layout.extents()
    pad = 3.0
    bg = libui.DrawPath()
    bg.add_rectangle(x - pad, y - pad, w + pad * 2, h + pad * 2)
    bg.end()
    br = libui.DrawBrush()
    br.r, br.g, br.b, br.a = 1.0, 1.0, 1.0, 0.8
    ctx.fill(bg, br)
    ctx.text(layout, x, y)


class Shape:
    """A draggable shape with a bounding box."""

    def __init__(self, x, y, w, h, draw_fn):
        self.x, self.y, self.w, self.h = x, y, w, h
        self._draw = draw_fn

    def hit(self, mx, my):
        return self.x <= mx <= self.x + self.w and self.y <= my <= self.y + self.h

    def draw(self, ctx):
        self._draw(ctx, self.x, self.y)


def _make_shapes():
    """Create the list of draggable shapes."""
    shapes = []

    # Red rectangle
    def draw_rect(ctx, x, y):
        p = libui.DrawPath()
        p.add_rectangle(x, y, 120, 70)
        p.end()
        b = libui.DrawBrush()
        b.r, b.g, b.b, b.a = 0.85, 0.15, 0.15, 1.0
        ctx.fill(p, b)

    shapes.append(Shape(20, 20, 120, 70, draw_rect))

    # Green circle
    def draw_circle(ctx, x, y):
        p = libui.DrawPath()
        p.new_figure_with_arc(x + 35, y + 35, 35, 0, 2 * math.pi, False)
        p.end()
        b = libui.DrawBrush()
        b.r, b.g, b.b, b.a = 0.15, 0.7, 0.15, 1.0
        ctx.fill(p, b)

    shapes.append(Shape(195, 20, 70, 70, draw_circle))

    # Blue triangle
    def draw_triangle(ctx, x, y):
        p = libui.DrawPath()
        p.new_figure(x, y + 70)
        p.line_to(x + 40, y)
        p.line_to(x + 80, y + 70)
        p.close_figure()
        p.end()
        b = libui.DrawBrush()
        b.r, b.g, b.b, b.a = 0.15, 0.15, 0.85, 1.0
        ctx.fill(p, b)

    shapes.append(Shape(310, 20, 80, 70, draw_triangle))

    # Linear gradient rectangle
    def draw_lin_grad(ctx, x, y):
        p = libui.DrawPath()
        p.add_rectangle(x, y, 150, 70)
        p.end()
        lb = libui.DrawBrush()
        lb.type = libui.BrushType.LINEAR_GRADIENT
        lb.x0, lb.y0 = x, y
        lb.x1, lb.y1 = x + 150, y + 70
        lb.set_stops([
            (0.0, 1.0, 0.0, 0.0, 1.0),
            (0.5, 1.0, 1.0, 0.0, 1.0),
            (1.0, 0.0, 0.0, 1.0, 1.0),
        ])
        ctx.fill(p, lb)

    shapes.append(Shape(430, 10, 150, 70, draw_lin_grad))

    # Radial gradient circle
    def draw_rad_grad(ctx, x, y):
        r = 40
        cx, cy = x + r, y + r
        p = libui.DrawPath()
        p.new_figure_with_arc(cx, cy, r, 0, 2 * math.pi, False)
        p.end()
        rb = libui.DrawBrush()
        rb.type = libui.BrushType.RADIAL_GRADIENT
        rb.x0, rb.y0 = cx, cy
        rb.x1, rb.y1 = cx, cy
        rb.outer_radius = r
        rb.set_stops([
            (0.0, 1.0, 1.0, 1.0, 1.0),
            (1.0, 0.2, 0.0, 0.6, 1.0),
        ])
        ctx.fill(p, rb)

    shapes.append(Shape(465, 100, 80, 80, draw_rad_grad))

    # Stroke styles block
    def draw_strokes(ctx, x, y):
        black = libui.DrawBrush()
        black.r, black.g, black.b, black.a = 0.0, 0.0, 0.0, 1.0
        caps = [libui.LineCap.FLAT, libui.LineCap.ROUND, libui.LineCap.SQUARE]
        cap_names = ["Flat", "Round", "Square"]
        for i, (cap, name) in enumerate(zip(caps, cap_names)):
            ly = y + i * 25
            p = libui.DrawPath()
            p.new_figure(x, ly)
            p.line_to(x + 130, ly)
            p.end()
            sp = libui.DrawStrokeParams()
            sp.thickness = 6.0
            sp.cap = cap
            ctx.stroke(p, black, sp)
            _draw_label(ctx, name, x + 135, ly - 6)
        # Dashed line
        ly = y + 80
        p = libui.DrawPath()
        p.new_figure(x, ly)
        p.line_to(x + 180, ly)
        p.end()
        sp = libui.DrawStrokeParams()
        sp.thickness = 3.0
        sp.set_dashes([10.0, 5.0, 3.0, 5.0])
        ctx.stroke(p, black, sp)
        _draw_label(ctx, "Dashed", x + 185, ly - 6)

    shapes.append(Shape(20, 120, 240, 100, draw_strokes))

    # Join styles block
    def draw_joins(ctx, x, y):
        black = libui.DrawBrush()
        black.r, black.g, black.b, black.a = 0.0, 0.0, 0.0, 1.0
        joins = [libui.LineJoin.MITER, libui.LineJoin.ROUND, libui.LineJoin.BEVEL]
        join_names = ["Miter", "Round", "Bevel"]
        for i, (join, name) in enumerate(zip(joins, join_names)):
            xo = x + i * 70
            p = libui.DrawPath()
            p.new_figure(xo, y + 50)
            p.line_to(xo + 20, y)
            p.line_to(xo + 40, y + 50)
            p.end()
            sp = libui.DrawStrokeParams()
            sp.thickness = 5.0
            sp.join = join
            ctx.stroke(p, black, sp)
            _draw_label(ctx, name, xo + 5, y + 55)

    shapes.append(Shape(280, 120, 210, 75, draw_joins))

    # Bezier curve
    def draw_bezier(ctx, x, y):
        p = libui.DrawPath()
        p.new_figure(x, y + 30)
        p.bezier_to(x + 60, y - 30, x + 140, y + 60, x + 230, y)
        p.end()
        sp = libui.DrawStrokeParams()
        sp.thickness = 2.5
        sp.cap = libui.LineCap.ROUND
        purple = libui.DrawBrush()
        purple.r, purple.g, purple.b, purple.a = 0.5, 0.0, 0.7, 1.0
        ctx.stroke(p, purple, sp)
        _draw_label(ctx, "Bezier", x + 235, y - 6)

    shapes.append(Shape(20, 230, 280, 60, draw_bezier))

    # Attributed text
    def draw_attr_text(ctx, x, y):
        text = "Bold Colored Italic Underlined Highlight Family Size"
        astr = libui.AttributedString(text)
        # Base: black text on white pill for theme safety
        astr.set_attribute(libui.color_attribute(0.0, 0.0, 0.0, 1.0), 0, len(text))
        astr.set_attribute(libui.weight_attribute(libui.TextWeight.BOLD), 0, 4)
        astr.set_attribute(libui.color_attribute(0.8, 0.0, 0.0, 1.0), 5, 12)
        astr.set_attribute(libui.italic_attribute(libui.TextItalic.ITALIC), 13, 19)
        astr.set_attribute(libui.underline_attribute(libui.Underline.SINGLE), 20, 30)
        astr.set_attribute(libui.background_attribute(1.0, 1.0, 0.0, 0.5), 31, 40)
        astr.set_attribute(libui.family_attribute("serif"), 41, 47)
        astr.set_attribute(libui.size_attribute(22.0), 48, 52)
        font = {"family": "sans-serif", "size": 14.0}
        layout = libui.DrawTextLayout(astr, font, 600)
        # Background pill
        w, h = layout.extents()
        pad = 3.0
        bg = libui.DrawPath()
        bg.add_rectangle(x - pad, y - pad, w + pad * 2, h + pad * 2)
        bg.end()
        br = libui.DrawBrush()
        br.r, br.g, br.b, br.a = 1.0, 1.0, 1.0, 0.8
        ctx.fill(bg, br)
        ctx.text(layout, x, y)

    shapes.append(Shape(20, 300, 600, 30, draw_attr_text))

    # Rotated rectangle
    def draw_rotated(ctx, x, y):
        cx, cy = x + 30, y + 30
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

    shapes.append(Shape(330, 300, 60, 60, draw_rotated))

    return shapes


def _draw_hint(ctx, area_w, area_h):
    """Draw a hint label at the bottom."""
    _draw_label(ctx, "Drag shapes to rearrange them", 20, area_h - 20, size=11.0)


def build_drawing_tab():
    shapes = _make_shapes()
    drag = {"active": None, "ox": 0.0, "oy": 0.0}
    area_node = None  # set after build

    def on_draw(ctx, area_w, area_h, clip_x, clip_y, clip_w, clip_h):
        for s in shapes:
            s.draw(ctx)
        _draw_hint(ctx, area_w, area_h)

    def on_mouse(event):
        if event["down"] == 1:
            # Hit test in reverse order (topmost first)
            for s in reversed(shapes):
                if s.hit(event["x"], event["y"]):
                    drag["active"] = s
                    drag["ox"] = event["x"] - s.x
                    drag["oy"] = event["y"] - s.y
                    # Move to top
                    shapes.remove(s)
                    shapes.append(s)
                    break
        elif event["up"] == 1:
            drag["active"] = None
        elif drag["active"] is not None:
            s = drag["active"]
            # Clamp to area bounds
            aw, ah = event["area_width"], event["area_height"]
            nx = max(0, min(event["x"] - drag["ox"], aw - s.w))
            ny = max(0, min(event["y"] - drag["oy"], ah - s.h))
            s.x, s.y = nx, ny
            if area_node and area_node.widget:
                area_node.widget.queue_redraw_all()

    def on_mouse_left(left):
        if left:
            drag["active"] = None

    area_node = DrawArea(
        on_draw=on_draw,
        on_mouse_event=on_mouse,
        on_mouse_crossed=on_mouse_left,
    )

    # -- Scrolling sub-tab: freehand drawing canvas --

    strokes = []  # list of lists of (x, y) points
    current_stroke = {"pts": None}
    scroll_node = None

    def on_scroll_draw(ctx, area_w, area_h, clip_x, clip_y, clip_w, clip_h):
        # Grid background
        gray = libui.DrawBrush()
        gray.r, gray.g, gray.b, gray.a = 0.0, 0.0, 0.0, 0.08
        sp = libui.DrawStrokeParams()
        sp.thickness = 1.0
        for x in range(0, 2001, 50):
            p = libui.DrawPath()
            p.new_figure(x, 0)
            p.line_to(x, 2000)
            p.end()
            ctx.stroke(p, gray, sp)
        for y in range(0, 2001, 50):
            p = libui.DrawPath()
            p.new_figure(0, y)
            p.line_to(2000, y)
            p.end()
            ctx.stroke(p, gray, sp)

        # Draw all strokes
        ink = libui.DrawBrush()
        ink.r, ink.g, ink.b, ink.a = 0.1, 0.1, 0.8, 1.0
        sp2 = libui.DrawStrokeParams()
        sp2.thickness = 2.5
        sp2.cap = libui.LineCap.ROUND
        sp2.join = libui.LineJoin.ROUND
        all_strokes = strokes + ([current_stroke["pts"]] if current_stroke["pts"] else [])
        for pts in all_strokes:
            if len(pts) < 2:
                continue
            p = libui.DrawPath()
            p.new_figure(pts[0][0], pts[0][1])
            for px, py in pts[1:]:
                p.line_to(px, py)
            p.end()
            ctx.stroke(p, ink, sp2)

        # Hint
        _draw_label(ctx, "Draw with mouse \u2014 click and drag to sketch lines", 20, 20, size=14.0)

    def on_scroll_mouse(event):
        nonlocal scroll_node
        if event["down"] == 1:
            current_stroke["pts"] = [(event["x"], event["y"])]
        elif event["up"] == 1:
            if current_stroke["pts"] and len(current_stroke["pts"]) >= 2:
                strokes.append(current_stroke["pts"])
            current_stroke["pts"] = None
            if scroll_node and scroll_node.widget:
                scroll_node.widget.queue_redraw_all()
        elif current_stroke["pts"] is not None:
            current_stroke["pts"].append((event["x"], event["y"]))
            if scroll_node and scroll_node.widget:
                scroll_node.widget.queue_redraw_all()

    scroll_node = ScrollingDrawArea(
        on_draw=on_scroll_draw,
        width=2000,
        height=2000,
        on_mouse_event=on_scroll_mouse,
    )

    return Tab(
        ("DrawArea", VBox(stretchy(area_node))),
        ("Drawing Canvas", VBox(stretchy(scroll_node))),
    )


# -- Tab 5: Data Table -----------------------------------------------


def build_table_tab(app: App):
    status = State("Table events appear here.")

    data = ListState(
        [
            {"checked": 1, "name": "Alice Johnson", "role": "Engineer", "score": 85, "vip": 1, "action": "Details"},
            {"checked": 0, "name": "Bob Smith", "role": "Designer", "score": 72, "vip": 0, "action": "Details"},
            {"checked": 1, "name": "Carol White", "role": "Manager", "score": 90, "vip": 1, "action": "Details"},
            {"checked": 0, "name": "Dave Brown", "role": "Intern", "score": 45, "vip": 0, "action": "Details"},
            {"checked": 1, "name": "Eve Davis", "role": "Engineer", "score": 95, "vip": 1, "action": "Details"},
            {"checked": 0, "name": "Frank Miller", "role": "Analyst", "score": 68, "vip": 0, "action": "Details"},
            {"checked": 1, "name": "Grace Lee", "role": "Lead", "score": 88, "vip": 0, "action": "Details"},
            {"checked": 0, "name": "Hank Wilson", "role": "QA", "score": 77, "vip": 0, "action": "Details"},
        ]
    )

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
        CheckboxColumn("VIP", key="vip"),
        ButtonColumn("Action", text_key="action", on_click=on_button_click),
        on_row_clicked=lambda row: status.set(
            f"Clicked row {row}: {data[row]['name']}" if row < len(data) else ""
        ),
        on_row_double_clicked=lambda row: status.set(
            f"Double-clicked row {row}: {data[row]['name']}" if row < len(data) else ""
        ),
        on_header_clicked=lambda col: status.set(f"Header clicked: column {col}"),
        on_selection_changed=lambda: status.set(
            f"Selection: {table.widget.selection}" if table.widget else ""
        ),
    )

    def do_add():
        add_counter.update(lambda x: x + 1)
        data.append(
            {
                "checked": 0,
                "name": f"New Person {add_counter.value}",
                "role": "New",
                "score": 50,
                "vip": 0,
                "action": "Details",
            }
        )
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


# -- Menus ------------------------------------------------------------


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
        app.msg_box(
            "Documentation", "Visit the python-libui-ng repository for full docs."
        )

    return [
        MenuDef(
            "File",
            MenuItem("Open File...", on_click=do_open),
            MenuItem("Open Folder...", on_click=do_open_folder),
            MenuItem("Save As...", on_click=do_save),
            MenuSeparator(),
            QuitItem(),
        ),
        MenuDef(
            "Edit",
            PreferencesItem(),
            MenuSeparator(),
            CheckMenuItem("Toggle Feature", checked=toggle_state, on_click=do_toggle),
        ),
        MenuDef(
            "Help",
            AboutItem(),
            MenuItem("Documentation", on_click=do_docs),
        ),
    ]


# -- Main -------------------------------------------------------------


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
            "Python libui-ng Showcase",
            900,
            700,
            child=content,
            has_menubar=True,
        ),
    )
    app.show()
    await app.wait()


if __name__ == "__main__":
    libui.run(main())
