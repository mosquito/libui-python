"""Tests for new widget types."""

import datetime

from libui import core


def test_tab():
    t = core.Tab()
    btn = core.Button("Page1")
    t.append("First", btn)
    assert t.num_pages() == 1
    t.set_margined(0, True)
    assert t.margined(0) is True
    t.destroy()


def test_group():
    g = core.Group("Settings")
    assert g.title == "Settings"
    assert g.margined is True  # default
    btn = core.Button("Inside")
    g.set_child(btn)
    g.destroy()


def test_spinbox():
    s = core.Spinbox(0, 100)
    s.value = 50
    assert s.value == 50
    s.destroy()


def test_slider():
    s = core.Slider(0, 100)
    s.value = 30
    assert s.value == 30
    assert isinstance(s.has_tooltip, bool)
    s.set_range(0, 200)
    s.destroy()


def test_progressbar():
    p = core.ProgressBar()
    p.value = 50
    assert p.value == 50
    p.value = -1  # indeterminate
    assert p.value == -1
    p.destroy()


def test_separator():
    h = core.Separator()
    h.destroy()
    v = core.Separator(vertical=True)
    v.destroy()


def test_editable_combobox():
    ec = core.EditableCombobox()
    ec.append("opt1")
    ec.append("opt2")
    ec.text = "custom"
    assert ec.text == "custom"
    ec.destroy()


def test_radio_buttons():
    r = core.RadioButtons()
    r.append("A")
    r.append("B")
    r.append("C")
    r.selected = 1
    assert r.selected == 1
    r.destroy()


def test_datetime_picker():
    d = core.DateTimePicker()
    dt = d.time
    assert isinstance(dt, datetime.datetime)
    d.destroy()

    d2 = core.DateTimePicker(type="date")
    d2.destroy()

    d3 = core.DateTimePicker(type="time")
    d3.destroy()


def test_multiline_entry():
    me = core.MultilineEntry()
    me.text = "line1\nline2"
    assert "line1" in me.text
    me.append("\nline3")
    assert me.read_only is False
    me.read_only = True
    assert me.read_only is True
    me.destroy()

    me2 = core.MultilineEntry(wrapping=False)
    me2.destroy()


def test_color_button():
    cb = core.ColorButton()
    color = cb.color
    assert isinstance(color, tuple)
    assert len(color) == 4
    cb.color = (1.0, 0.0, 0.0, 1.0)
    r, g, b, a = cb.color
    assert abs(r - 1.0) < 0.01
    assert abs(g - 0.0) < 0.01
    cb.destroy()


def test_font_button():
    fb = core.FontButton()
    font = fb.font
    assert isinstance(font, dict)
    assert "family" in font
    assert "size" in font
    fb.destroy()


def test_form():
    f = core.Form()
    assert f.padded is True  # default
    btn = core.Button("Field")
    f.append("Name", btn)
    f.delete(0)
    f.destroy()


def test_grid():
    g = core.Grid()
    assert g.padded is True  # default
    btn = core.Button("Cell")
    g.append(btn, 0, 0)
    g.destroy()


def test_grid_constants():
    assert core.Align.FILL == 0
    assert core.Align.START == 1
    assert core.Align.CENTER == 2
    assert core.Align.END == 3
    assert core.At.LEADING == 0
    assert core.At.TOP == 1
    assert core.At.TRAILING == 2
    assert core.At.BOTTOM == 3


def test_menu():
    m = core.Menu("File")
    item = m.append_item("Open")
    assert isinstance(item, core.MenuItem)
    check = m.append_check_item("Toggle")
    check.checked = True
    assert check.checked is True
    m.append_separator()
    quit_item = m.append_quit_item()
    assert isinstance(quit_item, core.MenuItem)
