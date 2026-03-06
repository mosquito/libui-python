"""Tests for widget creation and basic properties."""

from libui import core


def test_window_create():
    w = core.Window("Test", 200, 100)
    assert w.title == "Test"
    w.title = "Changed"
    assert w.title == "Changed"
    assert w.visible is False
    w.destroy()


def test_button_create():
    b = core.Button("Press")
    assert b.text == "Press"
    b.text = "Push"
    assert b.text == "Push"
    b.destroy()


def test_label_create():
    label = core.Label("Hello")
    assert label.text == "Hello"
    label.text = "World"
    assert label.text == "World"
    label.destroy()


def test_box_append():
    box = core.Box(vertical=True)
    btn = core.Button("A")
    box.append(btn)
    assert box.padded is False
    box.padded = True
    assert box.padded is True
    box.destroy()


def test_entry_types():
    e1 = core.Entry()
    e1.text = "hello"
    assert e1.text == "hello"
    assert e1.read_only is False
    e1.read_only = True
    assert e1.read_only is True
    e1.destroy()

    e2 = core.Entry(type="password")
    e2.destroy()

    e3 = core.Entry(type="search")
    e3.destroy()


def test_checkbox():
    cb = core.Checkbox("Agree")
    assert cb.text == "Agree"
    assert cb.checked is False
    cb.checked = True
    assert cb.checked is True
    cb.destroy()


def test_combobox():
    c = core.Combobox()
    c.append("one")
    c.append("two")
    c.selected = 0
    assert c.selected == 0
    c.selected = 1
    assert c.selected == 1
    c.destroy()


def test_window_set_child():
    w = core.Window("Test", 200, 100)
    box = core.Box()
    w.set_child(box)
    w.destroy()


def test_callback():
    called = []
    b = core.Button("X")
    b.on_clicked(lambda: called.append(1))
    # We can't simulate a click, but at least verify it doesn't crash
    b.destroy()
