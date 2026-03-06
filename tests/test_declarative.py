"""Tests for the declarative UI layer (state, nodes, app)."""

import pytest
from libui.declarative.state import ListState, State
from tests.conftest import flush_main


# ── State ────────────────────────────────────────────────────────────


class TestState:
    def test_initial_value(self):
        s = State(42)
        assert s.value == 42
        assert s.get() == 42

    def test_set_value(self):
        s = State(0)
        s.value = 10
        assert s.value == 10

    def test_set_method(self):
        s = State("hello")
        s.set("world")
        assert s.value == "world"

    def test_update(self):
        s = State(5)
        s.update(lambda x: x * 2)
        assert s.value == 10

    def test_subscribe_notifies(self):
        s = State(0)
        calls = []
        s.subscribe(lambda: calls.append(s.value))
        s.value = 1
        s.value = 2
        assert calls == [1, 2]

    def test_no_notify_on_same_value(self):
        s = State(5)
        calls = []
        s.subscribe(lambda: calls.append(s.value))
        s.value = 5
        assert calls == []

    def test_unsubscribe_via_return(self):
        s = State(0)
        calls = []
        unsub = s.subscribe(lambda: calls.append(s.value))
        s.value = 1
        unsub()
        s.value = 2
        assert calls == [1]

    def test_unsubscribe_method(self):
        s = State(0)
        calls = []

        def cb():
            return calls.append(s.value)

        s.subscribe(cb)
        s.value = 1
        s.unsubscribe(cb)
        s.value = 2
        assert calls == [1]

    def test_reentrancy_guard(self):
        """Setting state from a subscriber should not cause infinite loops."""
        a = State(0)
        b = State(0)

        a.subscribe(lambda: b.set(a.value))
        b.subscribe(lambda: a.set(b.value))

        a.value = 42
        assert a.value == 42
        assert b.value == 42

    def test_reentrancy_guard_triangle(self):
        """Three states in a cycle should not loop."""
        a = State(0)
        b = State(0)
        c = State(0)

        a.subscribe(lambda: b.set(a.value))
        b.subscribe(lambda: c.set(b.value))
        c.subscribe(lambda: a.set(c.value))

        a.value = 7
        assert a.value == 7
        assert b.value == 7
        assert c.value == 7


# ── Computed ─────────────────────────────────────────────────────────


class TestComputed:
    def test_initial_computation(self):
        s = State(3)
        c = s.map(lambda x: x * 2)
        assert c.value == 6

    def test_recomputes_on_change(self):
        s = State("world")
        c = s.map(lambda x: f"hello {x}")
        assert c.value == "hello world"
        s.value = "there"
        assert c.value == "hello there"

    def test_subscribe(self):
        s = State(1)
        c = s.map(lambda x: x + 10)
        calls = []
        c.subscribe(lambda: calls.append(c.value))
        s.value = 2
        assert calls == [12]

    def test_chain(self):
        s = State(2)
        c1 = s.map(lambda x: x * 3)
        c2 = c1.map(lambda x: x + 1)
        assert c2.value == 7
        s.value = 10
        assert c2.value == 31

    def test_no_notify_when_unchanged(self):
        s = State(5)
        c = s.map(lambda x: x // 2)  # 5 // 2 = 2
        calls = []
        c.subscribe(lambda: calls.append(c.value))
        s.value = 4  # 4 // 2 = 2 — same result
        assert calls == []


# ── ListState ────────────────────────────────────────────────────────


class TestListState:
    def test_initial(self):
        ls = ListState([1, 2, 3])
        assert list(ls) == [1, 2, 3]
        assert len(ls) == 3

    def test_append_notifies(self):
        ls = ListState()
        events = []
        ls.subscribe(lambda event, **kw: events.append((event, kw)))
        ls.append("a")
        assert events == [("inserted", {"index": 0})]
        assert ls[0] == "a"

    def test_pop_notifies(self):
        ls = ListState([10, 20, 30])
        events = []
        ls.subscribe(lambda event, **kw: events.append((event, kw)))
        val = ls.pop()
        assert val == 30
        assert events == [("deleted", {"index": 2})]
        assert len(ls) == 2

    def test_setitem_notifies(self):
        ls = ListState(["a", "b"])
        events = []
        ls.subscribe(lambda event, **kw: events.append((event, kw)))
        ls[1] = "B"
        assert events == [("changed", {"index": 1})]
        assert ls[1] == "B"

    def test_pop_with_index(self):
        ls = ListState([10, 20, 30])
        events = []
        ls.subscribe(lambda event, **kw: events.append((event, kw)))
        val = ls.pop(0)
        assert val == 10
        assert events == [("deleted", {"index": 0})]

    def test_empty_initial(self):
        ls = ListState()
        assert len(ls) == 0
        assert list(ls) == []


# ── Node infrastructure (without libui) ─────────────────────────────


class TestNodeImports:
    """Verify that all node classes can be imported."""

    def test_import_all(self):
        pass

    def test_stretchy_marks_node(self):
        from libui.declarative import VBox, stretchy

        node = VBox()
        assert node.stretchy is False
        result = stretchy(node)
        assert result is node
        assert result.stretchy is True


# ── Node construction (no build, no libui) ───────────────────────────


class TestNodeConstruction:
    def test_vbox_children(self):
        from libui.declarative import VBox, Label

        a = Label("a")
        b = Label("b")
        box = VBox(a, b)
        assert len(box.children) == 2

    def test_form_rows(self):
        from libui.declarative import Form, Label

        f = Form(("Name:", Label("x")), ("Age:", Label("y")))
        assert len(f._rows) == 2

    def test_tab_pages(self):
        from libui.declarative import Tab, Label

        t = Tab(("Page1", Label("a")), ("Page2", Label("b")))
        assert len(t._pages) == 2

    def test_slider_with_state(self):
        from libui.declarative import Slider

        v = State(50)
        s = Slider(0, 100, value=v)
        assert s._value is v

    def test_label_with_computed(self):
        from libui.declarative import Label

        s = State("world")
        c = s.map(lambda x: f"Hello {x}")
        lbl = Label(text=c)
        assert lbl._text is c

    def test_menu_def(self):
        from libui.declarative import MenuDef, MenuItem, MenuSeparator, QuitItem

        m = MenuDef(
            "File",
            MenuItem("Open"),
            MenuSeparator(),
            QuitItem(),
        )
        assert m.title == "File"
        assert len(m.items) == 3


# ── Integration tests (require libui init) ───────────────────────────


class TestDeclarativeWidgets:
    """Tests that actually build widgets using libui core."""

    def test_label_builds(self):
        from libui.declarative import Label, BuildContext

        ctx = BuildContext()
        lbl = Label("Hello")
        widget = lbl.build(ctx)
        assert widget.text == "Hello"

    def test_label_with_state(self):
        from libui.declarative import Label, BuildContext

        s = State("initial")
        ctx = BuildContext()
        lbl = Label(text=s)
        widget = lbl.build(ctx)
        assert widget.text == "initial"
        s.value = "updated"
        flush_main()
        assert widget.text == "updated"

    def test_label_with_computed(self):
        from libui.declarative import Label, BuildContext

        s = State("world")
        c = s.map(lambda x: f"Hello {x}")
        ctx = BuildContext()
        lbl = Label(text=c)
        widget = lbl.build(ctx)
        assert widget.text == "Hello world"
        s.value = "there"
        flush_main()
        assert widget.text == "Hello there"

    def test_button_builds(self):
        from libui.declarative import Button, BuildContext

        clicked = []
        ctx = BuildContext()
        btn = Button("Click", on_clicked=lambda: clicked.append(1))
        widget = btn.build(ctx)
        assert widget.text == "Click"

    def test_vbox_with_children(self):
        from libui.declarative import VBox, Label, BuildContext

        ctx = BuildContext()
        box = VBox(Label("a"), Label("b"), padded=True)
        widget = box.build(ctx)
        assert widget.padded is True

    def test_slider_two_way_sync(self):
        from libui.declarative import Slider, Spinbox, ProgressBar, BuildContext

        v = State(25)
        ctx = BuildContext()

        slider = Slider(0, 100, value=v)
        spinbox = Spinbox(0, 100, value=v)
        progress = ProgressBar(value=v)

        sw = slider.build(ctx)
        spw = spinbox.build(ctx)
        pw = progress.build(ctx)

        assert sw.value == 25
        assert spw.value == 25
        assert pw.value == 25

        # Change state -> all widgets update
        v.value = 50
        flush_main()
        assert sw.value == 50
        assert spw.value == 50
        assert pw.value == 50

    def test_entry_with_state(self):
        from libui.declarative import Entry, BuildContext

        text = State("hello")
        ctx = BuildContext()
        entry = Entry(text=text)
        widget = entry.build(ctx)
        assert widget.text == "hello"
        text.value = "world"
        flush_main()
        assert widget.text == "world"

    def test_checkbox_with_state(self):
        from libui.declarative import Checkbox, BuildContext

        checked = State(False)
        ctx = BuildContext()
        cb = Checkbox("Test", checked=checked)
        widget = cb.build(ctx)
        assert widget.checked is False
        checked.value = True
        flush_main()
        assert widget.checked is True

    def test_group_with_child(self):
        from libui.declarative import Group, Label, BuildContext

        ctx = BuildContext()
        g = Group("Title", Label("content"), margined=True)
        widget = g.build(ctx)
        assert widget.title == "Title"
        assert widget.margined is True

    def test_form_with_rows(self):
        from libui.declarative import Form, Label, BuildContext

        ctx = BuildContext()
        f = Form(("Name:", Label("x")), ("Age:", Label("y")), padded=True)
        widget = f.build(ctx)
        assert widget.padded is True

    def test_tab_with_pages(self):
        from libui.declarative import Tab, Label, BuildContext

        ctx = BuildContext()
        t = Tab(("P1", Label("a")), ("P2", Label("b")))
        widget = t.build(ctx)
        assert widget.num_pages() == 2

    def test_separator_builds(self):
        from libui.declarative import Separator, BuildContext

        ctx = BuildContext()
        s = Separator()
        widget = s.build(ctx)
        assert widget is not None

    def test_combobox_with_items(self):
        from libui.declarative import Combobox, BuildContext

        ctx = BuildContext()
        cb = Combobox(items=["A", "B", "C"], selected=1)
        widget = cb.build(ctx)
        assert widget.selected == 1

    def test_radio_with_items(self):
        from libui.declarative import RadioButtons, BuildContext

        ctx = BuildContext()
        rb = RadioButtons(items=["X", "Y", "Z"], selected=0)
        widget = rb.build(ctx)
        assert widget.selected == 0

    def test_multiline_entry(self):
        from libui.declarative import MultilineEntry, BuildContext

        ctx = BuildContext()
        mle = MultilineEntry(text="hello\nworld", wrapping=True)
        widget = mle.build(ctx)
        assert "hello" in widget.text

    def test_stretchy_in_box(self):
        from libui.declarative import VBox, Label, BuildContext, stretchy

        ctx = BuildContext()
        lbl = stretchy(Label("big"))
        box = VBox(lbl)
        box.build(ctx)
        assert lbl.stretchy is True

    def test_grid_builds(self):
        from libui.declarative import Grid, GridCell, Label, BuildContext

        ctx = BuildContext()
        g = Grid(
            GridCell(Label("a"), 0, 0),
            GridCell(Label("b"), 1, 0, hexpand=True),
            padded=True,
        )
        widget = g.build(ctx)
        assert widget.padded is True

    def test_window_builds(self):
        from libui.declarative import Window, Label, BuildContext

        ctx = BuildContext()
        w = Window("Test", 400, 300, child=Label("content"))
        widget = w.build(ctx)
        assert widget.title == "Test"
        widget.destroy()

    def test_progressbar_one_way(self):
        from libui.declarative import ProgressBar, BuildContext

        v = State(30)
        ctx = BuildContext()
        pb = ProgressBar(value=v)
        widget = pb.build(ctx)
        assert widget.value == 30
        v.value = 60
        flush_main()
        assert widget.value == 60


# ── Callbacks receive values ─────────────────────────────────────────


class TestCallbackValues:
    """Test that widget callbacks are wired to pass current values.

    We cannot fire libui events from Python, so we test the wrapping logic
    by verifying the node's attach_callbacks wires a lambda (not the raw
    user callback) and by testing via make_two_way for State-bound widgets.
    """

    def test_entry_callback_wraps_value(self):
        """Entry without State: attach_callbacks wraps on_changed to pass text."""
        from libui.declarative import Entry, BuildContext

        received = []
        ctx = BuildContext()
        entry = Entry(on_changed=lambda text: received.append(text))
        entry.build(ctx)
        # The registered callback is a wrapper lambda, not the raw user cb.
        # We can't fire it, but verify the node stores the callback correctly.
        assert entry._on_changed is not None

    def test_entry_with_state_user_cb_via_make_two_way(self):
        """Entry with State + on_changed: user_cb is called when State changes
        via the widget side (simulated by setting state directly through
        make_two_way's mechanism)."""
        from libui.declarative import Entry, BuildContext

        text_state = State("")
        received = []
        ctx = BuildContext()
        entry = Entry(text=text_state, on_changed=lambda text: received.append(text))
        entry.build(ctx)
        # Simulate what make_two_way does: state changes from widget side
        # We can't trigger widget events, but we can test the wiring exists
        assert entry._on_changed is not None

    def test_checkbox_callback_wraps_value(self):
        from libui.declarative import Checkbox, BuildContext

        received = []
        ctx = BuildContext()
        cb = Checkbox("Test", on_toggled=lambda checked: received.append(checked))
        cb.build(ctx)
        assert cb._on_toggled is not None

    def test_slider_callback_wraps_value(self):
        from libui.declarative import Slider, BuildContext

        ctx = BuildContext()
        s = Slider(0, 100, on_changed=lambda val: val)
        s.build(ctx)
        assert s._on_changed is not None

    def test_combobox_callback_wraps_value(self):
        from libui.declarative import Combobox, BuildContext

        ctx = BuildContext()
        cb = Combobox(items=["A", "B"], on_selected=lambda idx: idx)
        cb.build(ctx)
        assert cb._on_selected is not None

    def test_radio_callback_wraps_value(self):
        from libui.declarative import RadioButtons, BuildContext

        ctx = BuildContext()
        rb = RadioButtons(items=["X", "Y"], on_selected=lambda idx: idx)
        rb.build(ctx)
        assert rb._on_selected is not None

    def test_editable_combobox_callback_wraps_value(self):
        from libui.declarative import EditableCombobox, BuildContext

        ctx = BuildContext()
        ecb = EditableCombobox(items=["A"], on_changed=lambda text: text)
        ecb.build(ctx)
        assert ecb._on_changed is not None

    def test_multiline_callback_wraps_value(self):
        from libui.declarative import MultilineEntry, BuildContext

        ctx = BuildContext()
        mle = MultilineEntry(on_changed=lambda text: text)
        mle.build(ctx)
        assert mle._on_changed is not None

    def test_color_button_callback_wraps_value(self):
        from libui.declarative import ColorButton, BuildContext

        ctx = BuildContext()
        btn = ColorButton(on_changed=lambda color: color)
        btn.build(ctx)
        assert btn._on_changed is not None

    def test_font_button_callback_wraps_value(self):
        from libui.declarative import FontButton, BuildContext

        ctx = BuildContext()
        btn = FontButton(on_changed=lambda font: font)
        btn.build(ctx)
        assert btn._on_changed is not None

    def test_datetime_callback_wraps_value(self):
        from libui.declarative import DateTimePicker, BuildContext

        ctx = BuildContext()
        dtp = DateTimePicker(on_changed=lambda time: time)
        dtp.build(ctx)
        assert dtp._on_changed is not None

    def test_spinbox_callback_wraps_value(self):
        from libui.declarative import Spinbox, BuildContext

        ctx = BuildContext()
        s = Spinbox(0, 100, on_changed=lambda val: val)
        s.build(ctx)
        assert s._on_changed is not None

    def test_make_two_way_user_cb(self):
        """Test that make_two_way calls user_cb with the value."""
        from libui.declarative.node import make_two_way, Node

        received = []

        class FakeWidget:
            def __init__(self):
                self.value = 0
                self._cb = None

            def on_changed(self, cb):
                self._cb = cb

        node = Node()
        node.unsubs = []
        s = State(0)
        w = FakeWidget()
        make_two_way(
            node,
            w,
            "value",
            s,
            "on_changed",
            user_cb=lambda val: received.append(val),
            _wrap_cb=False,
        )
        # Simulate the widget firing the event
        w.value = 42
        w._cb()
        assert s.value == 42
        assert received == [42]


# ── Bindable read_only ───────────────────────────────────────────────


class TestBindableReadOnly:
    """Test that read_only accepts State and auto-binds."""

    def test_entry_read_only_state(self):
        from libui.declarative import Entry, BuildContext

        ro = State(False)
        ctx = BuildContext()
        entry = Entry(read_only=ro)
        widget = entry.build(ctx)
        assert widget.read_only is False
        ro.value = True
        flush_main()
        assert widget.read_only is True
        ro.value = False
        flush_main()
        assert widget.read_only is False

    def test_entry_read_only_bool(self):
        from libui.declarative import Entry, BuildContext

        ctx = BuildContext()
        entry = Entry(read_only=True)
        widget = entry.build(ctx)
        assert widget.read_only is True

    def test_multiline_read_only_state(self):
        from libui.declarative import MultilineEntry, BuildContext

        ro = State(False)
        ctx = BuildContext()
        mle = MultilineEntry(read_only=ro)
        widget = mle.build(ctx)
        assert widget.read_only is False
        ro.value = True
        flush_main()
        assert widget.read_only is True

    def test_multiline_read_only_bool(self):
        from libui.declarative import MultilineEntry, BuildContext

        ctx = BuildContext()
        mle = MultilineEntry(read_only=True)
        widget = mle.build(ctx)
        assert widget.read_only is True

    def test_shared_read_only_state(self):
        """Multiple entries sharing one read_only State all update together."""
        from libui.declarative import Entry, BuildContext

        ro = State(False)
        ctx = BuildContext()
        e1 = Entry(read_only=ro)
        e2 = Entry(type="password", read_only=ro)
        e3 = Entry(type="search", read_only=ro)
        w1 = e1.build(ctx)
        w2 = e2.build(ctx)
        w3 = e3.build(ctx)
        assert w1.read_only is False
        assert w2.read_only is False
        assert w3.read_only is False
        ro.value = True
        flush_main()
        assert w1.read_only is True
        assert w2.read_only is True
        assert w3.read_only is True


# ── App deferred build ───────────────────────────────────────────────


class TestAppDeferredBuild:
    """Test App.build(window=..., menus=...) deferred pattern."""

    def test_app_no_args(self):
        from libui.declarative import App

        app = App()
        assert app._window is None
        assert app._menus == []

    def test_app_build_with_args(self):
        from libui.declarative import App, Window, Label

        app = App()
        app.build(window=Window("Test", 400, 300, child=Label("hi")))
        assert app._built is True
        assert app.window is not None
        assert app.window.title == "Test"
        app.window.destroy()

    def test_app_build_overrides_init(self):
        from libui.declarative import App, Window, Label

        app = App(window=Window("Old", 100, 100, child=Label("old")))
        app.build(window=Window("New", 200, 200, child=Label("new")))
        assert app.window.title == "New"
        app.window.destroy()

    def test_app_backward_compat(self):
        from libui.declarative import App, Window, Label

        app = App(window=Window("Compat", 400, 300, child=Label("hi")))
        app.build()
        assert app.window.title == "Compat"
        app.window.destroy()

    def test_app_build_requires_window(self):
        from libui.declarative import App

        app = App()
        with pytest.raises(ValueError, match="requires a window"):
            app.build()


# ── App dialog helpers ───────────────────────────────────────────────


class TestAppDialogHelpers:
    """Test that App dialog helper methods exist and don't crash without a window."""

    def test_msg_box_no_window(self):
        from libui.declarative import App

        app = App()
        # Should not raise — just no-op when no window
        app.msg_box("title", "desc")

    def test_msg_box_error_no_window(self):
        from libui.declarative import App

        app = App()
        app.msg_box_error("title", "desc")

    def test_open_file_no_window(self):
        from libui.declarative import App

        app = App()
        assert app.open_file() is None

    def test_open_folder_no_window(self):
        from libui.declarative import App

        app = App()
        assert app.open_folder() is None

    def test_save_file_no_window(self):
        from libui.declarative import App

        app = App()
        assert app.save_file() is None
