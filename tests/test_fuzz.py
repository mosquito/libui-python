"""Fuzz tests for libui.core — ensure no native crashes.

Every test here feeds bad arguments (wrong types, None, out-of-range values,
missing required args, etc.) to the C extension and asserts that a Python
exception is raised instead of a segfault/SIGBUS.
"""

import pytest
from libui import core
from tests.conftest import flush_main


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BAD_VALUES = [None, 0, 1, -1, 3.14, True, b"bytes", [], {}, object()]
BAD_STRINGS = [None, 0, 1, -1, 3.14, True, b"bytes", [], {}, object()]
BAD_CONTROLS = [None, 0, "hello", 3.14, True, b"bytes", [], {}, object()]
BAD_INTS = [None, "x", 3.14, [], {}, object(), b"bytes"]
BAD_BOOLS = [None, "x", 3.14, [], {}, object(), b"bytes", 42]
HUGE_INT = 2**63
NEGATIVE_HUGE = -(2**63)


def assert_no_crash(fn, *args, **kwargs):
    """Call fn and expect a Python exception, never a crash."""
    try:
        fn(*args, **kwargs)
    except (TypeError, ValueError, RuntimeError, OverflowError,
            SystemError, AttributeError, OSError, Exception):
        pass  # Any Python exception is fine — no crash is the goal


# ===========================================================================
# Module-level functions
# ===========================================================================


class TestModuleFunctions:
    def test_main_step_without_main_steps(self):
        """Already guarded — just verify the error message."""
        # main_steps is called by the fixture, so this path is tested
        # in a dedicated script. Here we verify main_step works after init.
        assert core.main_step(wait=False) in (True, False)

    def test_main_step_bad_args(self):
        # NOTE: main_step(wait=<truthy>) blocks waiting for an event,
        # so we can only safely test wait=False and extra positional args.
        assert_no_crash(core.main_step, wait=False)
        # Extra/wrong positional args
        assert_no_crash(core.main_step, "extra", "args")
        assert_no_crash(core.main_step, False, False)

    def test_queue_main_bad_args(self):
        for v in [None, 0, "string", 3.14, b"bytes"]:
            assert_no_crash(core.queue_main, v)
        assert_no_crash(core.queue_main)  # no args

    def test_queue_main_callable_that_raises(self):
        def explode():
            raise RuntimeError("boom")
        core.queue_main(explode)
        flush_main()  # should not crash

    def test_on_should_quit_bad_args(self):
        for v in [None, 0, "string", 3.14]:
            assert_no_crash(core.on_should_quit, v)
        assert_no_crash(core.on_should_quit)  # no args

    def test_open_file_bad_args(self):
        # NOTE: passing a valid Window would show a modal dialog and block.
        # We only test type errors here (non-Window args).
        for v in BAD_VALUES:
            assert_no_crash(core.open_file, v)
        assert_no_crash(core.open_file)  # no args

    def test_save_file_bad_args(self):
        for v in BAD_VALUES:
            assert_no_crash(core.save_file, v)
        assert_no_crash(core.save_file)  # no args

    def test_open_folder_bad_args(self):
        for v in BAD_VALUES:
            assert_no_crash(core.open_folder, v)
        assert_no_crash(core.open_folder)  # no args

    def test_msg_box_bad_args(self):
        # NOTE: passing a valid Window + valid strings would show a modal
        # dialog and block. Only test type errors (non-Window first arg,
        # or non-string title/desc).
        for v in BAD_VALUES:
            assert_no_crash(core.msg_box, v, "t", "d")
        assert_no_crash(core.msg_box)
        # Valid window but bad string args — caught by PyArg_ParseTuple
        w = core.Window("t", 100, 100)
        for v in [None, 0, 3.14, [], {}]:
            assert_no_crash(core.msg_box, w, v, "d")
            assert_no_crash(core.msg_box, w, "t", v)
        assert_no_crash(core.msg_box, w)
        assert_no_crash(core.msg_box, w, "t")
        w.destroy()

    def test_msg_box_error_bad_args(self):
        for v in BAD_VALUES:
            assert_no_crash(core.msg_box_error, v, "t", "d")
        assert_no_crash(core.msg_box_error)
        w = core.Window("t", 100, 100)
        for v in [None, 0, 3.14, [], {}]:
            assert_no_crash(core.msg_box_error, w, v, "d")
            assert_no_crash(core.msg_box_error, w, "t", v)
        w.destroy()

    def test_set_asyncio_loop_bad_args(self):
        for v in [0, "string", 3.14, [], {}]:
            assert_no_crash(core._set_asyncio_loop, v)
        # Reset to None
        core._set_asyncio_loop(None)


# ===========================================================================
# Attribute factory functions
# ===========================================================================


class TestAttributeFactories:
    def test_family_attribute_bad(self):
        for v in [None, 0, 3.14, [], {}]:
            assert_no_crash(core.family_attribute, v)
        assert_no_crash(core.family_attribute)

    def test_size_attribute_bad(self):
        for v in [None, "x", [], {}]:
            assert_no_crash(core.size_attribute, v)
        assert_no_crash(core.size_attribute)
        assert_no_crash(core.size_attribute, -1.0)
        assert_no_crash(core.size_attribute, 0.0)
        assert_no_crash(core.size_attribute, 1e30)

    def test_weight_attribute_bad(self):
        for v in [None, "x", [], {}]:
            assert_no_crash(core.weight_attribute, v)
        assert_no_crash(core.weight_attribute)
        assert_no_crash(core.weight_attribute, -999)
        assert_no_crash(core.weight_attribute, HUGE_INT)

    def test_italic_attribute_bad(self):
        for v in [None, "x", [], {}]:
            assert_no_crash(core.italic_attribute, v)
        assert_no_crash(core.italic_attribute)
        assert_no_crash(core.italic_attribute, -1)
        assert_no_crash(core.italic_attribute, 999)

    def test_stretch_attribute_bad(self):
        for v in [None, "x", [], {}]:
            assert_no_crash(core.stretch_attribute, v)
        assert_no_crash(core.stretch_attribute)

    def test_color_attribute_bad(self):
        assert_no_crash(core.color_attribute)
        assert_no_crash(core.color_attribute, 1.0)
        assert_no_crash(core.color_attribute, 1.0, 1.0)
        assert_no_crash(core.color_attribute, 1.0, 1.0, 1.0)
        for v in [None, "x", [], {}]:
            assert_no_crash(core.color_attribute, v, 0, 0, 0)
        # Out of range floats
        assert_no_crash(core.color_attribute, -1.0, 2.0, 1e30, float('nan'))

    def test_background_attribute_bad(self):
        assert_no_crash(core.background_attribute)
        for v in [None, "x", [], {}]:
            assert_no_crash(core.background_attribute, v, 0, 0, 0)

    def test_underline_attribute_bad(self):
        for v in [None, "x", [], {}]:
            assert_no_crash(core.underline_attribute, v)
        assert_no_crash(core.underline_attribute)
        assert_no_crash(core.underline_attribute, -1)
        assert_no_crash(core.underline_attribute, 9999)

    def test_underline_color_attribute_bad(self):
        assert_no_crash(core.underline_color_attribute)
        assert_no_crash(core.underline_color_attribute, 0)
        for v in [None, "x", [], {}]:
            assert_no_crash(core.underline_color_attribute, v, 0, 0, 0, 0)

    def test_features_attribute_bad(self):
        for v in BAD_VALUES:
            assert_no_crash(core.features_attribute, v)
        assert_no_crash(core.features_attribute)


# ===========================================================================
# Window
# ===========================================================================


class TestWindowFuzz:
    def test_constructor_bad_args(self):
        assert_no_crash(core.Window)  # no args
        for v in BAD_STRINGS:
            assert_no_crash(core.Window, v, 100, 100)
        for v in BAD_INTS:
            assert_no_crash(core.Window, "t", v, 100)
            assert_no_crash(core.Window, "t", 100, v)
        assert_no_crash(core.Window, "t", -1, -1)
        assert_no_crash(core.Window, "t", 0, 0)
        assert_no_crash(core.Window, "t", HUGE_INT, HUGE_INT)

    def test_set_child_bad(self):
        w = core.Window("t", 100, 100)
        for v in BAD_CONTROLS:
            assert_no_crash(w.set_child, v)
        assert_no_crash(w.set_child)  # no args
        w.destroy()

    def test_on_closing_bad(self):
        w = core.Window("t", 100, 100)
        for v in [None, 0, "string"]:
            assert_no_crash(w.on_closing, v)
        assert_no_crash(w.on_closing)
        w.destroy()

    def test_properties_bad_types(self):
        w = core.Window("t", 100, 100)
        for v in BAD_STRINGS:
            assert_no_crash(setattr, w, "title", v)
        for v in BAD_BOOLS:
            assert_no_crash(setattr, w, "margined", v)
            assert_no_crash(setattr, w, "fullscreen", v)
            assert_no_crash(setattr, w, "borderless", v)
            assert_no_crash(setattr, w, "resizeable", v)
        w.destroy()

    def test_use_after_destroy(self):
        w = core.Window("t", 100, 100)
        w.destroy()
        assert_no_crash(getattr, w, "title")
        assert_no_crash(setattr, w, "title", "x")
        assert_no_crash(w.set_child, core.Button("b"))
        assert_no_crash(w.show)
        assert_no_crash(w.hide)
        assert_no_crash(w.destroy)


# ===========================================================================
# Button
# ===========================================================================


class TestButtonFuzz:
    def test_constructor_bad(self):
        assert_no_crash(core.Button)
        for v in BAD_STRINGS:
            assert_no_crash(core.Button, v)

    def test_text_bad(self):
        b = core.Button("ok")
        for v in BAD_STRINGS:
            assert_no_crash(setattr, b, "text", v)
        b.destroy()

    def test_on_clicked_bad(self):
        b = core.Button("ok")
        for v in [None, 0, "string"]:
            assert_no_crash(b.on_clicked, v)
        assert_no_crash(b.on_clicked)
        b.destroy()

    def test_use_after_destroy(self):
        b = core.Button("ok")
        b.destroy()
        assert_no_crash(getattr, b, "text")
        assert_no_crash(setattr, b, "text", "x")
        assert_no_crash(b.on_clicked, lambda: None)


# ===========================================================================
# Label
# ===========================================================================


class TestLabelFuzz:
    def test_constructor_bad(self):
        assert_no_crash(core.Label)
        for v in BAD_STRINGS:
            assert_no_crash(core.Label, v)

    def test_text_bad(self):
        lbl = core.Label("ok")
        for v in BAD_STRINGS:
            assert_no_crash(setattr, lbl, "text", v)
        lbl.destroy()

    def test_use_after_destroy(self):
        lbl = core.Label("ok")
        lbl.destroy()
        assert_no_crash(getattr, lbl, "text")
        assert_no_crash(setattr, lbl, "text", "x")


# ===========================================================================
# Box / VerticalBox / HorizontalBox
# ===========================================================================


class TestBoxFuzz:
    def test_constructor_bad(self):
        for v in BAD_BOOLS:
            assert_no_crash(core.Box, vertical=v)
        for v in BAD_BOOLS:
            assert_no_crash(core.VerticalBox, padded=v)
            assert_no_crash(core.HorizontalBox, padded=v)

    def test_append_bad(self):
        box = core.VerticalBox()
        assert_no_crash(box.append)  # no args
        for v in BAD_CONTROLS:
            assert_no_crash(box.append, v)
        # Valid append
        btn = core.Button("b")
        box.append(btn, stretchy=False)
        box.destroy()

    def test_append_already_parented(self):
        """Appending a control that already has a parent should not crash."""
        box1 = core.VerticalBox()
        box2 = core.VerticalBox()
        btn = core.Button("b")
        box1.append(btn)
        assert_no_crash(box2.append, btn)  # already has parent
        assert_no_crash(box1.append, btn)  # re-append to same parent
        box1.destroy()
        box2.destroy()

    def test_delete_bad(self):
        box = core.VerticalBox()
        assert_no_crash(box.delete)  # no args
        assert_no_crash(box.delete, -1)
        assert_no_crash(box.delete, 0)  # empty box
        assert_no_crash(box.delete, 999)
        assert_no_crash(box.delete, HUGE_INT)
        for v in BAD_INTS:
            assert_no_crash(box.delete, v)
        box.destroy()

    def test_padded_bad(self):
        box = core.VerticalBox()
        for v in BAD_BOOLS:
            assert_no_crash(setattr, box, "padded", v)
        box.destroy()

    def test_use_after_destroy(self):
        box = core.VerticalBox()
        box.destroy()
        assert_no_crash(box.append, core.Button("b"))
        assert_no_crash(box.delete, 0)
        assert_no_crash(getattr, box, "padded")


# ===========================================================================
# Entry
# ===========================================================================


class TestEntryFuzz:
    def test_constructor_bad(self):
        for v in BAD_STRINGS:
            assert_no_crash(core.Entry, type=v)
        assert_no_crash(core.Entry, type="invalid_type")

    def test_text_bad(self):
        e = core.Entry()
        for v in BAD_STRINGS:
            assert_no_crash(setattr, e, "text", v)
        e.destroy()

    def test_read_only_bad(self):
        e = core.Entry()
        for v in BAD_BOOLS:
            assert_no_crash(setattr, e, "read_only", v)
        e.destroy()

    def test_on_changed_bad(self):
        e = core.Entry()
        for v in [None, 0, "string"]:
            assert_no_crash(e.on_changed, v)
        assert_no_crash(e.on_changed)
        e.destroy()

    def test_use_after_destroy(self):
        e = core.Entry()
        e.destroy()
        assert_no_crash(getattr, e, "text")
        assert_no_crash(setattr, e, "text", "x")
        assert_no_crash(getattr, e, "read_only")


# ===========================================================================
# Checkbox
# ===========================================================================


class TestCheckboxFuzz:
    def test_constructor_bad(self):
        assert_no_crash(core.Checkbox)
        for v in BAD_STRINGS:
            assert_no_crash(core.Checkbox, v)

    def test_props_bad(self):
        cb = core.Checkbox("ok")
        for v in BAD_STRINGS:
            assert_no_crash(setattr, cb, "text", v)
        for v in BAD_BOOLS:
            assert_no_crash(setattr, cb, "checked", v)
        cb.destroy()

    def test_on_toggled_bad(self):
        cb = core.Checkbox("ok")
        for v in [None, 0, "string"]:
            assert_no_crash(cb.on_toggled, v)
        assert_no_crash(cb.on_toggled)
        cb.destroy()

    def test_use_after_destroy(self):
        cb = core.Checkbox("ok")
        cb.destroy()
        assert_no_crash(getattr, cb, "text")
        assert_no_crash(getattr, cb, "checked")


# ===========================================================================
# Combobox
# ===========================================================================


class TestComboboxFuzz:
    def test_append_bad(self):
        c = core.Combobox()
        assert_no_crash(c.append)
        for v in BAD_STRINGS:
            assert_no_crash(c.append, v)
        c.destroy()

    def test_selected_bad(self):
        c = core.Combobox()
        for v in BAD_INTS:
            assert_no_crash(setattr, c, "selected", v)
        assert_no_crash(setattr, c, "selected", -999)
        assert_no_crash(setattr, c, "selected", HUGE_INT)
        c.destroy()

    def test_on_selected_bad(self):
        c = core.Combobox()
        for v in [None, 0, "string"]:
            assert_no_crash(c.on_selected, v)
        assert_no_crash(c.on_selected)
        c.destroy()

    def test_use_after_destroy(self):
        c = core.Combobox()
        c.destroy()
        assert_no_crash(c.append, "x")
        assert_no_crash(getattr, c, "selected")


# ===========================================================================
# Tab
# ===========================================================================


class TestTabFuzz:
    def test_append_bad(self):
        t = core.Tab()
        assert_no_crash(t.append)
        for v in BAD_STRINGS:
            assert_no_crash(t.append, v, core.Button("b"))
        for v in BAD_CONTROLS:
            assert_no_crash(t.append, "page", v)
        t.destroy()

    def test_insert_at_bad(self):
        t = core.Tab()
        assert_no_crash(t.insert_at)
        assert_no_crash(t.insert_at, "page", -1, core.Button("b"))
        assert_no_crash(t.insert_at, "page", 999, core.Button("b"))
        for v in BAD_INTS:
            assert_no_crash(t.insert_at, "page", v, core.Button("b"))
        t.destroy()

    def test_delete_bad(self):
        t = core.Tab()
        assert_no_crash(t.delete)
        assert_no_crash(t.delete, -1)
        assert_no_crash(t.delete, 0)
        assert_no_crash(t.delete, 999)
        for v in BAD_INTS:
            assert_no_crash(t.delete, v)
        t.destroy()

    def test_num_pages_empty(self):
        t = core.Tab()
        assert t.num_pages() == 0
        t.destroy()

    def test_margined_bad(self):
        t = core.Tab()
        assert_no_crash(t.margined, -1)
        assert_no_crash(t.margined, 0)  # no pages
        assert_no_crash(t.margined, 999)
        assert_no_crash(t.set_margined, -1, True)
        assert_no_crash(t.set_margined, 0, True)  # no pages
        assert_no_crash(t.set_margined, 999, True)
        for v in BAD_INTS:
            assert_no_crash(t.margined, v)
            assert_no_crash(t.set_margined, v, True)
        t.destroy()

    def test_selected_bad(self):
        t = core.Tab()
        for v in BAD_INTS:
            assert_no_crash(setattr, t, "selected", v)
        t.destroy()

    def test_on_selected_bad(self):
        t = core.Tab()
        for v in [None, 0, "string"]:
            assert_no_crash(t.on_selected, v)
        assert_no_crash(t.on_selected)
        t.destroy()

    def test_use_after_destroy(self):
        t = core.Tab()
        t.destroy()
        assert_no_crash(t.append, "page", core.Button("b"))
        assert_no_crash(t.num_pages)
        assert_no_crash(t.delete, 0)


# ===========================================================================
# Group
# ===========================================================================


class TestGroupFuzz:
    def test_constructor_bad(self):
        assert_no_crash(core.Group)
        for v in BAD_STRINGS:
            assert_no_crash(core.Group, v)

    def test_set_child_bad(self):
        g = core.Group("g")
        for v in BAD_CONTROLS:
            assert_no_crash(g.set_child, v)
        assert_no_crash(g.set_child)
        g.destroy()

    def test_props_bad(self):
        g = core.Group("g")
        for v in BAD_STRINGS:
            assert_no_crash(setattr, g, "title", v)
        for v in BAD_BOOLS:
            assert_no_crash(setattr, g, "margined", v)
        g.destroy()

    def test_use_after_destroy(self):
        g = core.Group("g")
        g.destroy()
        assert_no_crash(getattr, g, "title")
        assert_no_crash(g.set_child, core.Button("b"))


# ===========================================================================
# Form
# ===========================================================================


class TestFormFuzz:
    def test_append_bad(self):
        f = core.Form()
        assert_no_crash(f.append)
        for v in BAD_STRINGS:
            assert_no_crash(f.append, v, core.Button("b"))
        for v in BAD_CONTROLS:
            assert_no_crash(f.append, "label", v)
        f.destroy()

    def test_delete_bad(self):
        f = core.Form()
        assert_no_crash(f.delete)
        assert_no_crash(f.delete, -1)
        assert_no_crash(f.delete, 0)
        assert_no_crash(f.delete, 999)
        for v in BAD_INTS:
            assert_no_crash(f.delete, v)
        f.destroy()

    def test_use_after_destroy(self):
        f = core.Form()
        f.destroy()
        assert_no_crash(f.append, "label", core.Button("b"))
        assert_no_crash(f.delete, 0)


# ===========================================================================
# Grid
# ===========================================================================


class TestGridFuzz:
    def test_append_bad(self):
        g = core.Grid()
        assert_no_crash(g.append)
        for v in BAD_CONTROLS:
            assert_no_crash(g.append, v, 0, 0)
        for v in BAD_INTS:
            assert_no_crash(g.append, core.Button("b"), v, 0)
            assert_no_crash(g.append, core.Button("b"), 0, v)
        g.destroy()

    def test_append_bad_spans(self):
        g = core.Grid()
        # Each append needs a fresh control (can't re-parent)
        assert_no_crash(g.append, core.Button("b"), 0, 0, -1, -1)
        assert_no_crash(g.append, core.Button("b"), 0, 0, 0, 0)
        assert_no_crash(g.append, core.Button("b"), 0, 0, HUGE_INT, HUGE_INT)
        g.destroy()

    def test_use_after_destroy(self):
        g = core.Grid()
        g.destroy()
        assert_no_crash(g.append, core.Button("b"), 0, 0)


# ===========================================================================
# Spinbox
# ===========================================================================


class TestSpinboxFuzz:
    def test_constructor_bad(self):
        for v in BAD_INTS:
            assert_no_crash(core.Spinbox, v, 100)
            assert_no_crash(core.Spinbox, 0, v)
        assert_no_crash(core.Spinbox, 100, 0)  # min > max
        assert_no_crash(core.Spinbox, HUGE_INT, HUGE_INT)
        assert_no_crash(core.Spinbox, NEGATIVE_HUGE, NEGATIVE_HUGE)

    def test_value_bad(self):
        s = core.Spinbox(0, 100)
        for v in BAD_INTS:
            assert_no_crash(setattr, s, "value", v)
        assert_no_crash(setattr, s, "value", -999)
        assert_no_crash(setattr, s, "value", 999)
        assert_no_crash(setattr, s, "value", HUGE_INT)
        s.destroy()

    def test_on_changed_bad(self):
        s = core.Spinbox(0, 100)
        for v in [None, 0, "string"]:
            assert_no_crash(s.on_changed, v)
        assert_no_crash(s.on_changed)
        s.destroy()

    def test_use_after_destroy(self):
        s = core.Spinbox(0, 100)
        s.destroy()
        assert_no_crash(getattr, s, "value")
        assert_no_crash(setattr, s, "value", 50)


# ===========================================================================
# Slider
# ===========================================================================


class TestSliderFuzz:
    def test_constructor_bad(self):
        for v in BAD_INTS:
            assert_no_crash(core.Slider, v, 100)
            assert_no_crash(core.Slider, 0, v)
        assert_no_crash(core.Slider, 100, 0)
        assert_no_crash(core.Slider, HUGE_INT, HUGE_INT)

    def test_value_bad(self):
        s = core.Slider(0, 100)
        for v in BAD_INTS:
            assert_no_crash(setattr, s, "value", v)
        assert_no_crash(setattr, s, "value", -999)
        assert_no_crash(setattr, s, "value", 999)
        s.destroy()

    def test_set_range_bad(self):
        s = core.Slider(0, 100)
        assert_no_crash(s.set_range)
        assert_no_crash(s.set_range, 100, 0)
        for v in BAD_INTS:
            assert_no_crash(s.set_range, v, 100)
            assert_no_crash(s.set_range, 0, v)
        s.destroy()

    def test_has_tooltip_bad(self):
        s = core.Slider(0, 100)
        for v in BAD_BOOLS:
            assert_no_crash(setattr, s, "has_tooltip", v)
        s.destroy()

    def test_callbacks_bad(self):
        s = core.Slider(0, 100)
        for v in [None, 0, "string"]:
            assert_no_crash(s.on_changed, v)
            assert_no_crash(s.on_released, v)
        assert_no_crash(s.on_changed)
        assert_no_crash(s.on_released)
        s.destroy()

    def test_use_after_destroy(self):
        s = core.Slider(0, 100)
        s.destroy()
        assert_no_crash(getattr, s, "value")
        assert_no_crash(setattr, s, "value", 50)


# ===========================================================================
# ProgressBar
# ===========================================================================


class TestProgressBarFuzz:
    def test_value_bad(self):
        p = core.ProgressBar()
        for v in BAD_INTS:
            assert_no_crash(setattr, p, "value", v)
        assert_no_crash(setattr, p, "value", -999)
        assert_no_crash(setattr, p, "value", 999)
        assert_no_crash(setattr, p, "value", HUGE_INT)
        p.destroy()

    def test_use_after_destroy(self):
        p = core.ProgressBar()
        p.destroy()
        assert_no_crash(getattr, p, "value")
        assert_no_crash(setattr, p, "value", 50)


# ===========================================================================
# Separator
# ===========================================================================


class TestSeparatorFuzz:
    def test_constructor_bad(self):
        for v in BAD_BOOLS:
            assert_no_crash(core.Separator, vertical=v)

    def test_use_after_destroy(self):
        s = core.Separator()
        s.destroy()
        assert_no_crash(s.destroy)


# ===========================================================================
# RadioButtons
# ===========================================================================


class TestRadioButtonsFuzz:
    def test_append_bad(self):
        r = core.RadioButtons()
        assert_no_crash(r.append)
        for v in BAD_STRINGS:
            assert_no_crash(r.append, v)
        r.destroy()

    def test_selected_bad(self):
        r = core.RadioButtons()
        for v in BAD_INTS:
            assert_no_crash(setattr, r, "selected", v)
        assert_no_crash(setattr, r, "selected", -999)
        assert_no_crash(setattr, r, "selected", 999)
        r.destroy()

    def test_on_selected_bad(self):
        r = core.RadioButtons()
        for v in [None, 0, "string"]:
            assert_no_crash(r.on_selected, v)
        assert_no_crash(r.on_selected)
        r.destroy()

    def test_use_after_destroy(self):
        r = core.RadioButtons()
        r.destroy()
        assert_no_crash(r.append, "x")
        assert_no_crash(getattr, r, "selected")


# ===========================================================================
# EditableCombobox
# ===========================================================================


class TestEditableComboboxFuzz:
    def test_append_bad(self):
        c = core.EditableCombobox()
        assert_no_crash(c.append)
        for v in BAD_STRINGS:
            assert_no_crash(c.append, v)
        c.destroy()

    def test_text_bad(self):
        c = core.EditableCombobox()
        for v in BAD_STRINGS:
            assert_no_crash(setattr, c, "text", v)
        c.destroy()

    def test_on_changed_bad(self):
        c = core.EditableCombobox()
        for v in [None, 0, "string"]:
            assert_no_crash(c.on_changed, v)
        assert_no_crash(c.on_changed)
        c.destroy()

    def test_use_after_destroy(self):
        c = core.EditableCombobox()
        c.destroy()
        assert_no_crash(c.append, "x")
        assert_no_crash(getattr, c, "text")


# ===========================================================================
# MultilineEntry
# ===========================================================================


class TestMultilineEntryFuzz:
    def test_constructor_bad(self):
        for v in BAD_BOOLS:
            assert_no_crash(core.MultilineEntry, wrapping=v)

    def test_text_bad(self):
        m = core.MultilineEntry()
        for v in BAD_STRINGS:
            assert_no_crash(setattr, m, "text", v)
        m.destroy()

    def test_append_bad(self):
        m = core.MultilineEntry()
        assert_no_crash(m.append)
        for v in BAD_STRINGS:
            assert_no_crash(m.append, v)
        m.destroy()

    def test_read_only_bad(self):
        m = core.MultilineEntry()
        for v in BAD_BOOLS:
            assert_no_crash(setattr, m, "read_only", v)
        m.destroy()

    def test_on_changed_bad(self):
        m = core.MultilineEntry()
        for v in [None, 0, "string"]:
            assert_no_crash(m.on_changed, v)
        assert_no_crash(m.on_changed)
        m.destroy()

    def test_use_after_destroy(self):
        m = core.MultilineEntry()
        m.destroy()
        assert_no_crash(getattr, m, "text")
        assert_no_crash(setattr, m, "text", "x")
        assert_no_crash(m.append, "x")


# ===========================================================================
# DateTimePicker
# ===========================================================================


class TestDateTimePickerFuzz:
    def test_constructor_bad(self):
        for v in BAD_STRINGS:
            assert_no_crash(core.DateTimePicker, type=v)
        assert_no_crash(core.DateTimePicker, type="invalid")

    def test_time_bad(self):
        d = core.DateTimePicker()
        for v in [None, 0, "string", 3.14, [], {}]:
            assert_no_crash(setattr, d, "time", v)
        d.destroy()

    def test_on_changed_bad(self):
        d = core.DateTimePicker()
        for v in [None, 0, "string"]:
            assert_no_crash(d.on_changed, v)
        assert_no_crash(d.on_changed)
        d.destroy()

    def test_use_after_destroy(self):
        d = core.DateTimePicker()
        d.destroy()
        assert_no_crash(getattr, d, "time")


# ===========================================================================
# ColorButton
# ===========================================================================


class TestColorButtonFuzz:
    def test_color_bad(self):
        cb = core.ColorButton()
        for v in [None, 0, "string", 3.14, [], {}]:
            assert_no_crash(setattr, cb, "color", v)
        # Wrong tuple sizes
        assert_no_crash(setattr, cb, "color", ())
        assert_no_crash(setattr, cb, "color", (1.0,))
        assert_no_crash(setattr, cb, "color", (1.0, 1.0))
        assert_no_crash(setattr, cb, "color", (1.0, 1.0, 1.0))
        assert_no_crash(setattr, cb, "color", (1.0, 1.0, 1.0, 1.0, 1.0))
        # Bad values in tuple
        assert_no_crash(setattr, cb, "color", ("a", "b", "c", "d"))
        assert_no_crash(setattr, cb, "color", (None, None, None, None))
        cb.destroy()

    def test_on_changed_bad(self):
        cb = core.ColorButton()
        for v in [None, 0, "string"]:
            assert_no_crash(cb.on_changed, v)
        assert_no_crash(cb.on_changed)
        cb.destroy()

    def test_use_after_destroy(self):
        cb = core.ColorButton()
        cb.destroy()
        assert_no_crash(getattr, cb, "color")


# ===========================================================================
# FontButton
# ===========================================================================


class TestFontButtonFuzz:
    def test_on_changed_bad(self):
        fb = core.FontButton()
        for v in [None, 0, "string"]:
            assert_no_crash(fb.on_changed, v)
        assert_no_crash(fb.on_changed)
        fb.destroy()

    def test_use_after_destroy(self):
        fb = core.FontButton()
        fb.destroy()
        assert_no_crash(getattr, fb, "font")


# ===========================================================================
# Menu / MenuItem
# ===========================================================================


class TestMenuFuzz:
    def test_constructor_bad(self):
        assert_no_crash(core.Menu)
        for v in BAD_STRINGS:
            assert_no_crash(core.Menu, v)

    def test_append_item_bad(self):
        m = core.Menu("Test")
        assert_no_crash(m.append_item)
        for v in BAD_STRINGS:
            assert_no_crash(m.append_item, v)

    def test_append_check_item_bad(self):
        m = core.Menu("Test")
        assert_no_crash(m.append_check_item)
        for v in BAD_STRINGS:
            assert_no_crash(m.append_check_item, v)

    def test_menuitem_on_clicked_bad(self):
        m = core.Menu("Test2")
        item = m.append_item("Item")
        for v in [None, 0, "string"]:
            assert_no_crash(item.on_clicked, v)
        assert_no_crash(item.on_clicked)

    def test_menuitem_checked_bad(self):
        m = core.Menu("Test3")
        item = m.append_check_item("Check")
        for v in BAD_BOOLS:
            assert_no_crash(setattr, item, "checked", v)

    def test_menuitem_enable_disable(self):
        m = core.Menu("Test4")
        item = m.append_item("Item")
        item.enable()
        item.disable()
        item.enable()


# ===========================================================================
# Image
# ===========================================================================


class TestImageFuzz:
    def test_constructor_bad(self):
        assert_no_crash(core.Image)
        for v in BAD_INTS:
            assert_no_crash(core.Image, v, 10)
            assert_no_crash(core.Image, 10, v)
        assert_no_crash(core.Image, -1, -1)
        assert_no_crash(core.Image, 0, 0)

    def test_append_bad(self):
        img = core.Image(16, 16)
        assert_no_crash(img.append)
        for v in BAD_VALUES:
            assert_no_crash(img.append, v, 16, 16, 64)
        # Wrong dimensions
        assert_no_crash(img.append, b"\x00" * 4, 1, 1, 4)  # valid
        assert_no_crash(img.append, b"", 16, 16, 64)  # too short
        assert_no_crash(img.append, b"\x00", 16, 16, 64)  # too short
        assert_no_crash(img.append, b"\x00" * 1024, -1, -1, -1)
        assert_no_crash(img.append, b"\x00" * 1024, 0, 0, 0)


# ===========================================================================
# AttributedString
# ===========================================================================


class TestAttributedStringFuzz:
    def test_constructor_bad(self):
        assert_no_crash(core.AttributedString)
        for v in BAD_STRINGS:
            assert_no_crash(core.AttributedString, v)

    def test_append_bad(self):
        s = core.AttributedString("hello")
        assert_no_crash(s.append)
        for v in BAD_STRINGS:
            assert_no_crash(s.append, v)

    def test_insert_at_bad(self):
        s = core.AttributedString("hello")
        assert_no_crash(s.insert_at)
        assert_no_crash(s.insert_at, "x")  # missing pos
        for v in BAD_INTS:
            assert_no_crash(s.insert_at, "x", v)
        assert_no_crash(s.insert_at, "x", -1)
        assert_no_crash(s.insert_at, "x", 999)

    def test_delete_bad(self):
        s = core.AttributedString("hello")
        assert_no_crash(s.delete)
        assert_no_crash(s.delete, 0)  # missing end
        assert_no_crash(s.delete, -1, -1)
        assert_no_crash(s.delete, 999, 999)
        assert_no_crash(s.delete, 3, 1)  # start > end
        for v in BAD_INTS:
            assert_no_crash(s.delete, v, 3)
            assert_no_crash(s.delete, 0, v)

    def test_set_attribute_bad(self):
        s = core.AttributedString("hello")
        assert_no_crash(s.set_attribute)
        for v in BAD_VALUES:
            assert_no_crash(s.set_attribute, v, 0, 5)
        attr = core.family_attribute("Arial")
        assert_no_crash(s.set_attribute, attr, -1, -1)
        assert_no_crash(s.set_attribute, attr, 999, 999)
        for v in BAD_INTS:
            assert_no_crash(s.set_attribute, attr, v, 5)
            assert_no_crash(s.set_attribute, attr, 0, v)

    def test_for_each_attribute_bad(self):
        s = core.AttributedString("hello")
        assert_no_crash(s.for_each_attribute)
        for v in [None, 0, "string"]:
            assert_no_crash(s.for_each_attribute, v)


# ===========================================================================
# OpenTypeFeatures
# ===========================================================================


class TestOpenTypeFeaturesFuzz:
    def test_add_bad(self):
        f = core.OpenTypeFeatures()
        assert_no_crash(f.add)
        for v in BAD_STRINGS:
            assert_no_crash(f.add, v, 1)
        for v in BAD_INTS:
            assert_no_crash(f.add, "liga", v)
        # Tag wrong length
        assert_no_crash(f.add, "", 1)
        assert_no_crash(f.add, "a", 1)
        assert_no_crash(f.add, "ab", 1)
        assert_no_crash(f.add, "abcde", 1)

    def test_remove_bad(self):
        f = core.OpenTypeFeatures()
        assert_no_crash(f.remove)
        for v in BAD_STRINGS:
            assert_no_crash(f.remove, v)

    def test_get_bad(self):
        f = core.OpenTypeFeatures()
        assert_no_crash(f.get)
        for v in BAD_STRINGS:
            assert_no_crash(f.get, v)


# ===========================================================================
# DrawPath
# ===========================================================================


class TestDrawPathFuzz:
    def test_methods_before_new_figure(self):
        p = core.DrawPath()
        assert_no_crash(p.line_to, 0, 0)
        assert_no_crash(p.arc_to, 0, 0, 10, 0, 3.14)
        assert_no_crash(p.bezier_to, 0, 0, 1, 1, 2, 2)
        assert_no_crash(p.close_figure)

    def test_new_figure_bad(self):
        p = core.DrawPath()
        assert_no_crash(p.new_figure)
        for v in BAD_INTS:
            assert_no_crash(p.new_figure, v, 0)
            assert_no_crash(p.new_figure, 0, v)

    def test_line_to_bad(self):
        p = core.DrawPath()
        p.new_figure(0, 0)
        assert_no_crash(p.line_to)
        for v in [None, "x", [], {}]:
            assert_no_crash(p.line_to, v, 0)
            assert_no_crash(p.line_to, 0, v)
        assert_no_crash(p.line_to, float('nan'), float('inf'))

    def test_arc_to_bad(self):
        p = core.DrawPath()
        p.new_figure(0, 0)
        assert_no_crash(p.arc_to)
        assert_no_crash(p.arc_to, 0, 0, -1, 0, 3.14)  # negative radius
        for v in [None, "x", [], {}]:
            assert_no_crash(p.arc_to, v, 0, 10, 0, 3.14)

    def test_bezier_to_bad(self):
        p = core.DrawPath()
        p.new_figure(0, 0)
        assert_no_crash(p.bezier_to)
        for v in [None, "x", [], {}]:
            assert_no_crash(p.bezier_to, v, 0, 1, 1, 2, 2)

    def test_add_rectangle_bad(self):
        p = core.DrawPath()
        assert_no_crash(p.add_rectangle)
        assert_no_crash(p.add_rectangle, 0, 0, -1, -1)
        for v in [None, "x", [], {}]:
            assert_no_crash(p.add_rectangle, v, 0, 10, 10)

    def test_methods_after_end(self):
        p = core.DrawPath()
        p.add_rectangle(0, 0, 10, 10)
        p.end()
        assert p.ended is True
        # Operations after end should not crash
        assert_no_crash(p.new_figure, 0, 0)
        assert_no_crash(p.line_to, 1, 1)
        assert_no_crash(p.end)

    def test_constructor_bad(self):
        for v in [None, "x", [], {}]:
            assert_no_crash(core.DrawPath, fill_mode=v)
        assert_no_crash(core.DrawPath, fill_mode=-1)
        assert_no_crash(core.DrawPath, fill_mode=999)


# ===========================================================================
# DrawBrush
# ===========================================================================


class TestDrawBrushFuzz:
    def test_props_bad(self):
        b = core.DrawBrush()
        for prop in ("r", "g", "b", "a", "x0", "y0", "x1", "y1",
                     "outer_radius"):
            for v in [None, "x", [], {}]:
                assert_no_crash(setattr, b, prop, v)
            assert_no_crash(setattr, b, prop, float('nan'))
            assert_no_crash(setattr, b, prop, float('inf'))
            assert_no_crash(setattr, b, prop, -1e30)

    def test_type_bad(self):
        b = core.DrawBrush()
        for v in [None, "x", [], {}, -1, 999]:
            assert_no_crash(setattr, b, "type", v)

    def test_set_stops_bad(self):
        b = core.DrawBrush()
        assert_no_crash(b.set_stops)
        assert_no_crash(b.set_stops, None)
        assert_no_crash(b.set_stops, "string")
        assert_no_crash(b.set_stops, 42)
        assert_no_crash(b.set_stops, [])  # empty
        assert_no_crash(b.set_stops, [None])
        assert_no_crash(b.set_stops, ["bad"])
        assert_no_crash(b.set_stops, [(1,)])  # wrong tuple size
        assert_no_crash(b.set_stops, [(None, None, None, None, None)])


# ===========================================================================
# DrawStrokeParams
# ===========================================================================


class TestDrawStrokeParamsFuzz:
    def test_props_bad(self):
        sp = core.DrawStrokeParams()
        for v in [None, "x", [], {}]:
            assert_no_crash(setattr, sp, "thickness", v)
            assert_no_crash(setattr, sp, "miter_limit", v)
            assert_no_crash(setattr, sp, "dash_phase", v)
        for v in [None, "x", [], {}, -1, 999]:
            assert_no_crash(setattr, sp, "cap", v)
            assert_no_crash(setattr, sp, "join", v)

    def test_dashes_bad(self):
        sp = core.DrawStrokeParams()
        for v in [None, "x", 42, {}]:
            assert_no_crash(setattr, sp, "dashes", v)
        assert_no_crash(setattr, sp, "dashes", [])
        assert_no_crash(setattr, sp, "dashes", [None])
        assert_no_crash(setattr, sp, "dashes", ["bad"])


# ===========================================================================
# DrawMatrix
# ===========================================================================


class TestDrawMatrixFuzz:
    def test_transform_bad(self):
        m = core.DrawMatrix()
        m.set_identity()
        for v in [None, "x", [], {}]:
            assert_no_crash(m.translate, v, 0)
            assert_no_crash(m.translate, 0, v)
            assert_no_crash(m.scale, v, 0, 1, 1)
            assert_no_crash(m.rotate, v, 0, 0)
            assert_no_crash(m.skew, v, 0, 0, 0)
        assert_no_crash(m.translate, float('nan'), float('inf'))
        assert_no_crash(m.transform_point, float('nan'), 0)
        assert_no_crash(m.transform_size, float('nan'), 0)

    def test_multiply_bad(self):
        m = core.DrawMatrix()
        m.set_identity()
        for v in BAD_VALUES:
            assert_no_crash(m.multiply, v)
        assert_no_crash(m.multiply)

    def test_methods_no_args(self):
        m = core.DrawMatrix()
        assert_no_crash(m.translate)
        assert_no_crash(m.scale)
        assert_no_crash(m.rotate)
        assert_no_crash(m.skew)
        assert_no_crash(m.transform_point)
        assert_no_crash(m.transform_size)


# ===========================================================================
# TableModel
# ===========================================================================


class TestTableModelFuzz:
    def _make_model(self):
        return core.TableModel(
            2, lambda col: 0, lambda: 0, lambda row, col: "")

    def test_constructor_bad(self):
        # Missing args
        assert_no_crash(core.TableModel)
        # Bad types for each positional arg
        for v in BAD_VALUES:
            assert_no_crash(core.TableModel, v, lambda c: 0, lambda: 0, lambda r, c: "")
            assert_no_crash(core.TableModel, 2, v, lambda: 0, lambda r, c: "")
            assert_no_crash(core.TableModel, 2, lambda c: 0, v, lambda r, c: "")
            assert_no_crash(core.TableModel, 2, lambda c: 0, lambda: 0, v)

    def test_row_inserted_bad(self):
        tm = self._make_model()
        assert_no_crash(tm.row_inserted)
        for v in BAD_INTS:
            assert_no_crash(tm.row_inserted, v)
        assert_no_crash(tm.row_inserted, -1)
        assert_no_crash(tm.row_inserted, HUGE_INT)

    def test_row_deleted_bad(self):
        tm = self._make_model()
        assert_no_crash(tm.row_deleted)
        for v in BAD_INTS:
            assert_no_crash(tm.row_deleted, v)
        assert_no_crash(tm.row_deleted, -1)

    def test_row_changed_bad(self):
        tm = self._make_model()
        assert_no_crash(tm.row_changed)
        for v in BAD_INTS:
            assert_no_crash(tm.row_changed, v)
        assert_no_crash(tm.row_changed, -1)

    def test_row_methods_no_args(self):
        tm = self._make_model()
        # Each row method called with wrong types
        for method_name in ("row_inserted", "row_deleted", "row_changed"):
            method = getattr(tm, method_name)
            assert_no_crash(method)
            for v in [None, "string", 3.14, [], {}]:
                assert_no_crash(method, v)


# ===========================================================================
# Table
# ===========================================================================


class TestTableFuzz:
    def _make_model(self):
        return core.TableModel(
            2, lambda col: 0, lambda: 0, lambda row, col: "")

    def test_constructor_bad(self):
        assert_no_crash(core.Table)
        for v in BAD_VALUES:
            assert_no_crash(core.Table, v)

    def test_append_columns_bad(self):
        tm = self._make_model()
        t = core.Table(tm)
        # Wrong column indices
        assert_no_crash(t.append_text_column, "col", -1)
        assert_no_crash(t.append_text_column, "col", 999)
        # Bad name
        for v in BAD_STRINGS:
            assert_no_crash(t.append_text_column, v, 0)
        # No args
        assert_no_crash(t.append_text_column)
        assert_no_crash(t.append_image_column)
        assert_no_crash(t.append_checkbox_column)
        assert_no_crash(t.append_button_column)
        assert_no_crash(t.append_progress_bar_column)
        assert_no_crash(t.append_checkbox_text_column)
        assert_no_crash(t.append_image_text_column)
        t.destroy()

    def test_append_columns_bad_types(self):
        tm = self._make_model()
        t = core.Table(tm)
        for v in BAD_INTS:
            assert_no_crash(t.append_text_column, "col", v)
            assert_no_crash(t.append_image_column, "col", v)
            assert_no_crash(t.append_checkbox_column, "col", v)
            assert_no_crash(t.append_button_column, "col", v)
            assert_no_crash(t.append_progress_bar_column, "col", v)
        t.destroy()


# ===========================================================================
# Area / ScrollingArea
# ===========================================================================


class TestAreaFuzz:
    def _draw_cb(self, ctx, w, h):
        pass

    def test_area_constructor(self):
        a = core.Area(on_draw=self._draw_cb)
        a.destroy()

    def test_area_constructor_bad(self):
        # Missing required on_draw
        assert_no_crash(core.Area)
        # Bad on_draw values
        for v in BAD_VALUES:
            assert_no_crash(core.Area, on_draw=v)

    def test_scrolling_area_bad(self):
        assert_no_crash(core.ScrollingArea)
        # Bad width/height with valid on_draw
        for v in BAD_INTS:
            assert_no_crash(core.ScrollingArea, on_draw=self._draw_cb,
                            width=v, height=100)
            assert_no_crash(core.ScrollingArea, on_draw=self._draw_cb,
                            width=100, height=v)
        assert_no_crash(core.ScrollingArea, on_draw=self._draw_cb,
                        width=-1, height=-1)
        assert_no_crash(core.ScrollingArea, on_draw=self._draw_cb,
                        width=0, height=0)

    def test_area_methods_bad(self):
        a = core.Area(on_draw=self._draw_cb)
        assert_no_crash(a.queue_redraw_all)
        # scroll_to and set_size should fail on non-scrolling Area
        assert_no_crash(a.scroll_to, 0, 0, 100, 100)
        assert_no_crash(a.set_size, 100, 100)
        # Bad arg types
        for v in BAD_VALUES:
            assert_no_crash(a.scroll_to, v, 0, 100, 100)
            assert_no_crash(a.set_size, v, 100)
        a.destroy()

    def test_scrolling_area_methods(self):
        sa = core.ScrollingArea(on_draw=self._draw_cb, width=200, height=200)
        assert_no_crash(sa.queue_redraw_all)
        assert_no_crash(sa.scroll_to, 0, 0, 100, 100)
        assert_no_crash(sa.set_size, 100, 100)
        # Bad arg types
        for v in BAD_VALUES:
            assert_no_crash(sa.scroll_to, v, 0, 100, 100)
            assert_no_crash(sa.set_size, v, 100)
        sa.destroy()


# ===========================================================================
# DrawTextLayout
# ===========================================================================


class TestDrawTextLayoutFuzz:
    def test_constructor_bad(self):
        assert_no_crash(core.DrawTextLayout)
        for v in BAD_VALUES:
            assert_no_crash(core.DrawTextLayout, v, {}, 100.0, 0)
        astr = core.AttributedString("hello")
        for v in BAD_VALUES:
            assert_no_crash(core.DrawTextLayout, astr, v, 100.0, 0)
        for v in [None, "x", [], {}]:
            assert_no_crash(core.DrawTextLayout, astr,
                            {"family": "Arial", "size": 12,
                             "weight": 400, "italic": 0, "stretch": 4},
                            v, 0)
        for v in [None, "x", [], {}]:
            assert_no_crash(core.DrawTextLayout, astr,
                            {"family": "Arial", "size": 12,
                             "weight": 400, "italic": 0, "stretch": 4},
                            100.0, v)


# ===========================================================================
# Double-destroy and cross-widget misuse
# ===========================================================================


class TestLifecycle:
    def test_double_destroy_all_widgets(self):
        """Double destroy should not crash."""
        widgets = [
            core.Window("t", 100, 100),
            core.Button("b"),
            core.Label("l"),
            core.VerticalBox(),
            core.HorizontalBox(),
            core.Entry(),
            core.Checkbox("c"),
            core.Combobox(),
            core.Tab(),
            core.Group("g"),
            core.Form(),
            core.Grid(),
            core.Spinbox(0, 100),
            core.Slider(0, 100),
            core.ProgressBar(),
            core.Separator(),
            core.RadioButtons(),
            core.EditableCombobox(),
            core.MultilineEntry(),
            core.DateTimePicker(),
            core.ColorButton(),
            core.FontButton(),
            core.Area(on_draw=lambda ctx, w, h: None),
        ]
        for w in widgets:
            w.destroy()
        for w in widgets:
            assert_no_crash(w.destroy)

    def test_child_set_to_wrong_parent_type(self):
        """Setting a child to a non-control should not crash."""
        w = core.Window("t", 100, 100)
        g = core.Group("g")
        for v in BAD_CONTROLS:
            assert_no_crash(w.set_child, v)
            assert_no_crash(g.set_child, v)
        w.destroy()
        g.destroy()

    def test_show_hide_enabled_on_destroyed(self):
        """Control methods on destroyed widgets should not crash."""
        widgets = [
            core.Button("b"),
            core.Label("l"),
            core.Entry(),
            core.Checkbox("c"),
        ]
        for w in widgets:
            w.destroy()
        for w in widgets:
            assert_no_crash(w.show)
            assert_no_crash(w.hide)
            assert_no_crash(w.enable)
            assert_no_crash(w.disable)
            assert_no_crash(getattr, w, "visible")
            assert_no_crash(getattr, w, "enabled")
            assert_no_crash(getattr, w, "toplevel")
