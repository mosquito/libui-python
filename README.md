# python-libui-ng

[![PyPI Version](https://img.shields.io/pypi/v/libui.svg)](https://pypi.org/project/libui/)
[![Python](https://img.shields.io/pypi/pyversions/libui.svg)](https://pypi.org/project/libui/)
[![License: MIT](https://img.shields.io/github/license/mosquito/libui-python.svg)](https://github.com/mosquito/libui-python/blob/main/LICENSE)
[![GitHub Issues](https://img.shields.io/github/issues/mosquito/libui-python.svg)](https://github.com/mosquito/libui-python/issues)

Native GUI toolkit for Python. Lightweight bindings for [libui-ng](https://github.com/libui-ng/libui-ng) — real native widgets on Linux (GTK+3), macOS (Cocoa), and Windows (Win32).

No electron. No web views. Just native controls.

## Features

- **30+ native widgets** — buttons, entries, sliders, tables, color pickers, drawing surfaces, and more
- **Declarative API** — reactive state, composable components, two-way data binding
- **Imperative API** — direct low-level control when you need it
- **Async-first** — built-in asyncio integration with thread-safe UI updates
- **Cross-platform** — one codebase, native look and feel everywhere

## Quick Start

```bash
pip install libui
```

### Hello World

```python
import libui
from libui.declarative import App, Window, VBox, Label, Button, State

async def main():
    app = App()
    count = State(0)

    app.build(window=Window(
        "Hello", 400, 300,
        child=VBox(
            Label(text=count.map(lambda n: f"Count: {n}")),
            Button("Click me", on_clicked=lambda: count.update(lambda n: n + 1)),
        ),
    ))

    app.show()
    await app.wait()

libui.run(main())
```

---

## Declarative API

The declarative API is the recommended way to build UIs. Describe your interface as a tree of components with reactive state — the framework handles synchronization.

### State Management

`State` is a reactive container. When its value changes, all subscribers and bound widgets update automatically.

```python
import libui
from libui.declarative import App, Window, VBox, Label, Button, State

async def main():
    app = App()

    name = State("World")
    count = State(0)

    # Derived state (read-only, auto-updates)
    greeting = name.map(lambda n: f"Hello, {n}!")

    # Subscribe to changes
    unsub = count.subscribe(lambda: print(count.value))

    def on_click():
        count.update(lambda n: n + 1)
        name.value = "Python"    # triggers greeting update

    app.build(window=Window("State Demo", 400, 300, child=VBox(
        Label(text=greeting),
        Label(text=count.map(lambda n: f"Clicks: {n}")),
        Button("Click", on_clicked=on_click),
    )))

    app.show()
    await app.wait()

libui.run(main())
```

### Layout Containers

```python
import libui
from libui.declarative import (
    App, Window, VBox, HBox, Group, Form, Tab, Grid, GridCell,
    Label, Button, Entry, MultilineEntry, stretchy,
)

async def main():
    app = App()

    app.build(window=Window("Layouts", 700, 500, child=Tab(
        # Vertical / Horizontal stacking
        ("Boxes", VBox(
            Label("Title"),
            Button("Click me"),
            stretchy(MultilineEntry()),  # stretchy = fills available space
            padded=True,
        )),

        # Form — two-column label + control layout
        ("Form", Form(
            ("Name:", Entry()),
            ("Password:", Entry(type="password")),
            ("Bio:", MultilineEntry(), True),  # True = stretchy
            padded=True,
        )),

        # Grid — precise positioning
        ("Grid", Grid(
            GridCell(Label("X:"), left=0, top=0, halign=libui.Align.END),
            GridCell(Entry(),      left=1, top=0, hexpand=True),
            GridCell(Label("Y:"), left=0, top=1, halign=libui.Align.END),
            GridCell(Entry(),      left=1, top=1, hexpand=True),
            GridCell(Button("OK"), left=0, top=2, xspan=2, halign=libui.Align.CENTER),
            padded=True,
        )),

        # Grouped container
        ("Group", Group("Connection", child=Form(
            ("Host:", Entry()),
            ("Port:", Entry()),
            padded=True,
        ), margined=True)),
    )))

    app.show()
    await app.wait()

libui.run(main())
```

### Widgets

All widgets support reactive binding with `State`:

```python
import libui
from libui.declarative import (
    App, Window, VBox, Form, Group, Separator, State, stretchy,
    Label, Button, Entry, MultilineEntry, Checkbox,
    Slider, Spinbox, ProgressBar,
    Combobox, RadioButtons, EditableCombobox,
    ColorButton, FontButton, DateTimePicker,
)

async def main():
    app = App()
    status = State("Ready.")
    value = State(50)
    dark_mode = State(False)

    app.build(window=Window("Widgets", 600, 500, child=VBox(
        Label(text=status),

        Group("Text Input", Form(
            ("Normal:", Entry(on_changed=lambda t: status.set(f"Entry: {t}"))),
            ("Password:", Entry(type="password")),
            ("Search:", Entry(type="search")),
            padded=True,
        )),

        Group("Controls", Form(
            ("Button:", Button("Save", on_clicked=lambda: status.set("Saved!"))),
            ("Checkbox:", Checkbox("Dark mode", checked=dark_mode,
                                   on_toggled=lambda c: status.set(f"Dark: {c}"))),
            ("Slider:", Slider(0, 100, value=value,
                               on_changed=lambda v: status.set(f"Value: {v}"))),
            ("Spinbox:", Spinbox(0, 999, value=value)),
            ("Progress:", ProgressBar(value=value)),
            padded=True,
        )),

        Group("Selection", Form(
            ("Combobox:", Combobox(items=["Red", "Green", "Blue"], selected=0)),
            ("Radio:", RadioButtons(items=["Low", "Medium", "High"])),
            ("Editable:", EditableCombobox(items=["Apple", "Banana"])),
            padded=True,
        )),

        Group("Pickers", Form(
            ("Color:", ColorButton(on_changed=lambda rgba: status.set(f"Color: {rgba}"))),
            ("Font:", FontButton(on_changed=lambda f: status.set(f"{f['family']} {f['size']}pt"))),
            ("DateTime:", DateTimePicker(type="datetime")),
            padded=True,
        )),

        Separator(),
        stretchy(MultilineEntry(wrapping=True)),
    )))

    app.show()
    await app.wait()

libui.run(main())
```

### Data Tables

Tables use `ListState` — an observable list that automatically syncs insertions, deletions, and edits with the UI.

```python
import libui
from libui.declarative import (
    App, Window, VBox, HBox, Label, Button, State, stretchy,
    DataTable, ListState,
    TextColumn, CheckboxTextColumn, ProgressColumn, ButtonColumn,
)

async def main():
    app = App()
    status = State("Click a row.")

    data = ListState([
        {"checked": 1, "name": "Alice", "role": "Engineer",  "score": 85, "action": "View"},
        {"checked": 0, "name": "Bob",   "role": "Designer",  "score": 72, "action": "View"},
        {"checked": 1, "name": "Carol", "role": "Manager",   "score": 90, "action": "View"},
    ])

    def on_button(row):
        d = data[row]
        app.msg_box("Details", f"{d['name']} — {d['role']}\nScore: {d['score']}")

    table = DataTable(
        data,
        CheckboxTextColumn("Name", checkbox_key="checked", text_key="name",
                           checkbox_editable=True),
        TextColumn("Role", key="role"),
        ProgressColumn("Score", key="score"),
        ButtonColumn("Action", text_key="action", on_click=on_button),
        on_row_clicked=lambda row: status.set(f"Clicked: {data[row]['name']}"),
    )

    counter = State(len(data))

    def add_row():
        counter.update(lambda n: n + 1)
        data.append({"checked": 0, "name": f"Person {counter.value}",
                      "role": "New", "score": 50, "action": "View"})

    app.build(window=Window("Table", 600, 400, child=VBox(
        Label(text=status),
        stretchy(table),
        HBox(
            Button("Add Row", on_clicked=add_row),
            Button("Remove Last", on_clicked=lambda: data.pop() if len(data) else None),
        ),
    )))

    app.show()
    await app.wait()

libui.run(main())
```

### Menus

Menus are defined before the window and passed to `App.build()`:

```python
import libui
from libui.declarative import (
    App, Window, VBox, Label, State,
    MenuDef, MenuItem, CheckMenuItem, MenuSeparator,
    QuitItem, PreferencesItem, AboutItem,
)

async def main():
    app = App()
    dark_state = State(False)
    status = State("Ready.")

    menus = [
        MenuDef("File",
            MenuItem("Open...", on_click=lambda: app.open_file()),
            MenuItem("Save As...", on_click=lambda: app.save_file()),
            MenuSeparator(),
            QuitItem(),
        ),
        MenuDef("Edit",
            CheckMenuItem("Dark Mode", checked=dark_state,
                          on_click=lambda: status.set(f"Dark: {dark_state.value}")),
            PreferencesItem(),
        ),
        MenuDef("Help",
            AboutItem(),
        ),
    ]

    app.build(
        menus=menus,
        window=Window("Menus", 500, 300, has_menubar=True, child=VBox(
            Label(text=status),
        )),
    )

    app.show()
    await app.wait()

libui.run(main())
```

### Dialogs

```python
import libui
from libui.declarative import App, Window, VBox, Button, Label, State

async def main():
    app = App()
    status = State("")

    def do_open():
        path = app.open_file()
        if path:
            status.set(f"Opened: {path}")

    async def do_open_async():
        path = await app.open_file_async()
        if path:
            status.set(f"Opened: {path}")

    app.build(window=Window("Dialogs", 400, 200, child=VBox(
        Label(text=status),
        Button("Open File (sync)", on_clicked=do_open),
        Button("Open File (async)", on_clicked=do_open_async),
        Button("Message Box", on_clicked=lambda: app.msg_box("Info", "Hello!")),
        Button("Error Box", on_clicked=lambda: app.msg_box_error("Error", "Something failed.")),
    )))

    app.show()
    await app.wait()

libui.run(main())
```

### Custom Drawing

```python
import math
import libui
from libui.declarative import App, Window, VBox, DrawArea, stretchy

def on_draw(ctx, area_w, area_h, clip_x, clip_y, clip_w, clip_h):
    # Filled rectangle
    path = libui.DrawPath()
    path.add_rectangle(20, 20, 200, 100)
    path.end()

    brush = libui.DrawBrush()
    brush.r, brush.g, brush.b, brush.a = 0.2, 0.6, 0.9, 1.0
    ctx.fill(path, brush)

    # Stroked circle
    circle = libui.DrawPath()
    circle.new_figure_with_arc(300, 70, 50, 0, 2 * math.pi, False)
    circle.end()

    stroke = libui.DrawStrokeParams()
    stroke.thickness = 3.0
    ctx.stroke(circle, brush, stroke)

    # Gradient
    grad_path = libui.DrawPath()
    grad_path.add_rectangle(20, 150, 200, 80)
    grad_path.end()

    grad = libui.DrawBrush()
    grad.type = libui.BrushType.LINEAR_GRADIENT
    grad.x0, grad.y0 = 20, 150
    grad.x1, grad.y1 = 220, 230
    grad.set_stops([(0.0, 1, 0, 0, 1), (0.5, 1, 1, 0, 1), (1.0, 0, 0, 1, 1)])
    ctx.fill(grad_path, grad)

    # Styled text
    text = libui.AttributedString("Hello Drawing!")
    text.set_attribute(libui.weight_attribute(libui.TextWeight.BOLD), 0, 5)
    text.set_attribute(libui.color_attribute(0.8, 0.0, 0.0, 1.0), 6, 14)
    layout = libui.DrawTextLayout(text, {"family": "sans-serif", "size": 18.0}, area_w)
    ctx.text(layout, 20, 260)

async def main():
    app = App()

    app.build(window=Window("Drawing", 500, 350,
        child=VBox(stretchy(DrawArea(on_draw=on_draw))),
    ))

    app.show()
    await app.wait()

libui.run(main())
```

The drawing API supports paths, fills, strokes, gradients (linear/radial), bezier curves, transforms (translate, rotate, scale, skew), clipping, and rich attributed text.

### Full Declarative Example

```python
import libui
from libui.declarative import *

async def main():
    app = App()
    status = State("Ready.")
    value = State(50)
    value.subscribe(lambda: status.set(f"Value: {value.value}"))

    app.build(
        menus=[
            MenuDef("File",
                MenuItem("About...", on_click=lambda: app.msg_box("About", "Demo v1.0")),
                MenuSeparator(),
                QuitItem(),
            ),
        ],
        window=Window("Demo", 600, 400, has_menubar=True, child=VBox(
            Label(text=status),
            Group("Controls", Form(
                ("Slider:", Slider(0, 100, value=value)),
                ("Spinbox:", Spinbox(0, 100, value=value)),
                ("Progress:", ProgressBar(value=value)),
                padded=True,
            )),
            Group("Selection", Form(
                ("Quality:", RadioButtons(items=["Low", "Medium", "High"])),
                ("Color:", Combobox(items=["Red", "Green", "Blue"], selected=0)),
                padded=True,
            )),
            Separator(),
            Group("Notes", stretchy(MultilineEntry(wrapping=True))),
        )),
    )

    app.show()
    await app.wait()

libui.run(main())
```

---

## Imperative API

The imperative API gives you direct control over every widget. It maps closely to the underlying libui-ng C library and is useful when you need fine-grained control, custom event loops, or want to integrate with existing code.

All imperative widgets are thread-safe proxies — mutations are automatically marshalled to the UI thread.

### Basic Example

```python
import asyncio
import libui

async def main():
    window = libui.Window("Hello", 400, 300)

    box = libui.VerticalBox(padded=True)
    window.set_child(box)

    label = libui.Label("Count: 0")
    box.append(label)

    count = 0

    def on_click():
        nonlocal count
        count += 1
        label.text = f"Count: {count}"

    button = libui.Button("Click me!")
    button.on_clicked(on_click)
    box.append(button)

    window.on_closing(lambda: (libui.quit(), True)[-1])
    window.show()

    await asyncio.Event().wait()

libui.run(main())
```

### Containers

```python
import asyncio
import libui

async def main():
    window = libui.Window("Containers", 600, 400)

    # Vertical / Horizontal box
    vbox = libui.VerticalBox(padded=True)
    hbox = libui.HorizontalBox(padded=True)
    vbox.append(hbox)
    hbox.append(libui.Button("Left"), stretchy=True)
    hbox.append(libui.Button("Right"), stretchy=True)

    # Group
    group = libui.Group("Settings")
    group.margined = True
    vbox.append(group)

    # Form — label + control pairs
    form = libui.Form(padded=True)
    form.append("Name:", libui.Entry())
    form.append("Bio:", libui.MultilineEntry(wrapping=True), stretchy=True)
    group.set_child(form)

    # Tab
    tab = libui.Tab()
    tab.append("Page 1", vbox)
    tab.append("Page 2", libui.Label("Second page"))
    tab.set_margined(0, True)
    tab.set_margined(1, True)

    # Grid
    grid = libui.Grid(padded=True)
    grid.append(libui.Label("Name:"), 0, 0, 1, 1, False, libui.Align.END, False, libui.Align.FILL)
    grid.append(libui.Entry(), 1, 0, 1, 1, True, libui.Align.FILL, False, libui.Align.FILL)

    window.set_child(tab)
    window.on_closing(lambda: (libui.quit(), True)[-1])
    window.show()

    await asyncio.Event().wait()

libui.run(main())
```

### Widgets

```python
import asyncio
import libui

async def main():
    window = libui.Window("Widgets", 500, 600)
    vbox = libui.VerticalBox(padded=True)
    window.set_child(vbox)

    # Label
    label = libui.Label("Hello")
    vbox.append(label)

    # Button
    btn = libui.Button("Click")
    btn.on_clicked(lambda: setattr(label, "text", "Clicked!"))
    vbox.append(btn)

    # Entry (text input)
    entry = libui.Entry()                    # normal (also: "password", "search")
    entry.on_changed(lambda: setattr(label, "text", f"Entry: {entry.text}"))
    vbox.append(entry)

    # Multiline Entry
    mle = libui.MultilineEntry(wrapping=True)
    mle.text = "Type here..."
    vbox.append(mle, stretchy=True)

    # Checkbox
    cb = libui.Checkbox("Enable feature")
    cb.on_toggled(lambda: setattr(label, "text", f"Checked: {cb.checked}"))
    vbox.append(cb)

    # Slider
    slider = libui.Slider(0, 100)
    slider.on_changed(lambda: setattr(label, "text", f"Slider: {slider.value}"))
    vbox.append(slider)

    # Spinbox
    spinbox = libui.Spinbox(0, 100)
    spinbox.on_changed(lambda: setattr(label, "text", f"Spinbox: {spinbox.value}"))
    vbox.append(spinbox)

    # Progress Bar
    progress = libui.ProgressBar()
    progress.value = 75
    vbox.append(progress)

    # Combobox
    combo = libui.Combobox()
    for item in ("Red", "Green", "Blue"):
        combo.append(item)
    combo.selected = 0
    combo.on_selected(lambda: setattr(label, "text", f"Combo: {combo.selected}"))
    vbox.append(combo)

    # Radio Buttons
    radio = libui.RadioButtons()
    for item in ("Option A", "Option B"):
        radio.append(item)
    radio.on_selected(lambda: setattr(label, "text", f"Radio: {radio.selected}"))
    vbox.append(radio)

    # Separator
    vbox.append(libui.Separator())

    window.on_closing(lambda: (libui.quit(), True)[-1])
    window.show()

    await asyncio.Event().wait()

libui.run(main())
```

### Pickers

```python
import asyncio
import libui

async def main():
    window = libui.Window("Pickers", 400, 300)
    form = libui.Form(padded=True)
    window.set_child(form)

    label = libui.Label("Pick something...")
    form.append("Status:", label)

    # Color picker
    color_btn = libui.ColorButton()
    color_btn.on_changed(lambda: setattr(
        label, "text", "Color: R={:.2f} G={:.2f} B={:.2f}".format(*color_btn.color[:3])))
    form.append("Color:", color_btn)

    # Font picker
    font_btn = libui.FontButton()
    font_btn.on_changed(lambda: setattr(
        label, "text", f"Font: {font_btn.font['family']} {font_btn.font['size']}pt"))
    form.append("Font:", font_btn)

    # Date/Time pickers
    dtp = libui.DateTimePicker()              # datetime
    dtp.on_changed(lambda: setattr(
        label, "text", "{0:04d}-{1:02d}-{2:02d} {3:02d}:{4:02d}".format(*dtp.time[:5])))
    form.append("DateTime:", dtp)

    dtp_date = libui.DateTimePicker(type="date")
    form.append("Date:", dtp_date)

    dtp_time = libui.DateTimePicker(type="time")
    form.append("Time:", dtp_time)

    window.on_closing(lambda: (libui.quit(), True)[-1])
    window.show()

    await asyncio.Event().wait()

libui.run(main())
```

### Tables

```python
import asyncio
import libui

async def main():
    window = libui.Window("Table", 500, 300)

    data = [
        ["Alice", "Engineer", 85],
        ["Bob",   "Designer", 72],
        ["Carol", "Manager",  90],
    ]

    model = libui.TableModel(
        num_columns=lambda: 3,
        column_type=lambda col: libui.TableValueType.STRING if col < 2 else libui.TableValueType.INT,
        num_rows=lambda: len(data),
        cell_value=lambda row, col: str(data[row][col]) if col < 2 else int(data[row][col]),
        set_cell_value=lambda row, col, val: data[row].__setitem__(col, val),
    )

    table = libui.Table(model)
    table.append_text_column("Name", 0)
    table.append_text_column("Role", 1)
    table.append_progress_bar_column("Score", 2)

    table.on_row_clicked(lambda row: print(f"Clicked: {data[row][0]}"))

    # Dynamic updates
    data.append(["Dave", "Intern", 50])
    model.row_inserted(len(data) - 1)

    window.set_child(table)
    window.on_closing(lambda: (libui.quit(), True)[-1])
    window.show()

    await asyncio.Event().wait()

libui.run(main())
```

**Available column types:**

```python
table.append_text_column(name, col, editable=NEVER_EDITABLE)
table.append_checkbox_column(name, col, editable=ALWAYS_EDITABLE)
table.append_checkbox_text_column(name, cb_col, cb_editable, text_col)
table.append_progress_bar_column(name, col)
table.append_button_column(name, col, clickable=ALWAYS_EDITABLE)
table.append_image_column(name, col)
table.append_image_text_column(name, img_col, text_col)
```

### Menus

Menus must be created **before** the window:

```python
import asyncio
import libui

async def main():
    # Menus first
    file_menu = libui.Menu("File")
    item = file_menu.append_item("Open...")
    item.on_clicked(lambda: print("Open clicked"))
    file_menu.append_separator()
    file_menu.append_quit_item()

    edit_menu = libui.Menu("Edit")
    edit_menu.append_preferences_item()
    toggle = edit_menu.append_check_item("Dark Mode")
    toggle.on_clicked(lambda: print(f"Dark: {toggle.checked}"))

    help_menu = libui.Menu("Help")
    help_menu.append_about_item()

    # Then the window with has_menubar=True
    window = libui.Window("Menus", 500, 300, has_menubar=True)
    window.set_child(libui.Label("Menu demo"))
    window.on_closing(lambda: (libui.quit(), True)[-1])
    window.show()

    await asyncio.Event().wait()

libui.run(main())
```

### Drawing

```python
import asyncio
import math
import libui

def on_draw(ctx, area_w, area_h, clip_x, clip_y, clip_w, clip_h):
    # Path + fill
    path = libui.DrawPath()
    path.add_rectangle(10, 10, 200, 100)
    path.end()

    brush = libui.DrawBrush()
    brush.r, brush.g, brush.b, brush.a = 0.8, 0.2, 0.2, 1.0
    ctx.fill(path, brush)

    # Stroke
    circle = libui.DrawPath()
    circle.new_figure_with_arc(160, 200, 50, 0, 2 * math.pi, False)
    circle.end()

    params = libui.DrawStrokeParams()
    params.thickness = 3.0
    params.cap = libui.LineCap.ROUND
    ctx.stroke(circle, brush, params)

    # Gradient
    rect = libui.DrawPath()
    rect.add_rectangle(250, 10, 150, 100)
    rect.end()

    grad = libui.DrawBrush()
    grad.type = libui.BrushType.LINEAR_GRADIENT
    grad.x0, grad.y0 = 250, 10
    grad.x1, grad.y1 = 400, 110
    grad.set_stops([(0.0, 1, 0, 0, 1), (1.0, 0, 0, 1, 1)])
    ctx.fill(rect, grad)

    # Transform
    matrix = libui.DrawMatrix()
    matrix.set_identity()
    matrix.rotate(300, 200, 30)
    ctx.save()
    ctx.transform(matrix)
    p = libui.DrawPath()
    p.add_rectangle(270, 185, 60, 30)
    p.end()
    ctx.fill(p, brush)
    ctx.restore()

    # Attributed text
    text = libui.AttributedString("Styled text")
    text.set_attribute(libui.weight_attribute(libui.TextWeight.BOLD), 0, 6)
    text.set_attribute(libui.color_attribute(0.0, 0.5, 0.0, 1.0), 7, 11)
    layout = libui.DrawTextLayout(text, {"family": "sans-serif", "size": 14.0}, area_w)
    ctx.text(layout, 10, 130)

async def main():
    window = libui.Window("Drawing", 500, 350)

    vbox = libui.VerticalBox()
    area = libui.Area(on_draw)
    vbox.append(area, stretchy=True)
    window.set_child(vbox)

    window.on_closing(lambda: (libui.quit(), True)[-1])
    window.show()

    await asyncio.Event().wait()

libui.run(main())
```

### Async Integration

`libui.run()` sets up a two-thread architecture: the main thread pumps the native event loop while an asyncio event loop runs on a background thread.

```python
import asyncio
import libui

async def main():
    window = libui.Window("Async Demo", 500, 400)
    vbox = libui.VerticalBox(padded=True)
    window.set_child(vbox)

    label = libui.Label("Starting...")
    vbox.append(label)

    # Async callbacks work naturally
    async def on_click():
        label.text = "Fetching..."
        await asyncio.sleep(1)
        label.text = "Done!"

    btn = libui.Button("Go")
    btn.on_clicked(on_click)
    vbox.append(btn)

    # Background tasks
    async def ticker():
        n = 0
        while True:
            await asyncio.sleep(1)
            n += 1
            label.text = f"Tick #{n}"

    asyncio.create_task(ticker())

    window.on_closing(lambda: (libui.quit(), True)[-1])
    window.show()
    await asyncio.Event().wait()

libui.run(main())
```

### Dialogs

```python
import asyncio
import libui

async def main():
    window = libui.Window("Dialogs", 400, 200)
    vbox = libui.VerticalBox(padded=True)
    window.set_child(vbox)

    label = libui.Label("")
    vbox.append(label)

    def do_open():
        path = libui.open_file(window)
        if path:
            label.text = f"Opened: {path}"

    btn_open = libui.Button("Open File")
    btn_open.on_clicked(do_open)

    btn_folder = libui.Button("Open Folder")
    btn_folder.on_clicked(lambda: setattr(
        label, "text", f"Folder: {libui.open_folder(window) or '(cancelled)'}"))

    btn_msg = libui.Button("Message Box")
    btn_msg.on_clicked(lambda: libui.msg_box(window, "Info", "Operation complete."))

    btn_err = libui.Button("Error Box")
    btn_err.on_clicked(lambda: libui.msg_box_error(window, "Error", "Something failed."))

    for b in (btn_open, btn_folder, btn_msg, btn_err):
        vbox.append(b)

    window.on_closing(lambda: (libui.quit(), True)[-1])
    window.show()

    await asyncio.Event().wait()

libui.run(main())
```

---

## Widget Reference

### All Controls

| Widget | Description |
|---|---|
| `Label` | Static or reactive text display |
| `Button` | Clickable button |
| `Entry` | Single-line text input (normal, password, search) |
| `MultilineEntry` | Multi-line text editor |
| `Checkbox` | Toggle with label |
| `Slider` | Horizontal slider with range |
| `Spinbox` | Numeric spinner with range |
| `ProgressBar` | Progress indicator (0–100) |
| `Combobox` | Dropdown selection |
| `EditableCombobox` | Dropdown with text input |
| `RadioButtons` | Mutually exclusive choices |
| `ColorButton` | Color picker |
| `FontButton` | Font picker |
| `DateTimePicker` | Date, time, or datetime picker |
| `Separator` | Visual divider (horizontal/vertical) |
| `Area` / `DrawArea` | Custom 2D drawing surface |
| `Table` / `DataTable` | Data grid with columns |

### Containers

| Container | Description |
|---|---|
| `VBox` / `VerticalBox` | Stack children vertically |
| `HBox` / `HorizontalBox` | Stack children horizontally |
| `Group` | Titled container with border |
| `Form` | Two-column label + control pairs |
| `Tab` | Tabbed pages |
| `Grid` | Position-based grid layout |
| `Window` | Top-level window |

### Enumerations

| Enum | Values |
|---|---|
| `libui.Align` | `FILL`, `START`, `CENTER`, `END` |
| `libui.BrushType` | `SOLID`, `LINEAR_GRADIENT`, `RADIAL_GRADIENT` |
| `libui.LineCap` | `FLAT`, `ROUND`, `SQUARE` |
| `libui.LineJoin` | `MITER`, `ROUND`, `BEVEL` |
| `libui.TextWeight` | `THIN` ... `NORMAL` ... `BOLD` ... `MAXIMUM` |
| `libui.TextItalic` | `NORMAL`, `OBLIQUE`, `ITALIC` |
| `libui.Underline` | `NONE`, `SINGLE`, `DOUBLE`, `SUGGESTION` |
| `libui.SelectionMode` | `NONE`, `ONE`, `ZERO_OR_ONE`, `MULTI` |
| `libui.SortIndicator` | `NONE`, `ASCENDING`, `DESCENDING` |
| `libui.TableValueType` | `INT`, `STRING`, `IMAGE` |
| `libui.TableModelColumn` | `NEVER_EDITABLE`, `ALWAYS_EDITABLE` |

---

## Examples

Run the examples from the project root:

```bash
python examples/hello.py                # minimal button + label
python examples/showcase_declarative.py # full declarative showcase (all widgets)
python examples/showcase.py             # full imperative showcase
python examples/example_async.py        # async widgets + background tasks
python examples/draw.py                 # custom drawing
python examples/table.py               # data table
```

## Requirements

- Python >= 3.13
- Linux: GTK+-3.0
- macOS: Cocoa (built-in)
- Windows: Win32 API (built-in)

## License

MIT — see [LICENSE](https://github.com/mosquito/libui-python/blob/main/LICENSE).
