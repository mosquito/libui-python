"""Tests for complex widget types: Image, Attribute, AttributedString,
DrawPath, DrawBrush, DrawMatrix, Area, TableModel, Table."""

import enum
import math
import sys

import pytest

from libui import core


# ── Image ────────────────────────────────────────────────────────────


def test_image_creation():
    img = core.Image(16, 16)
    assert img is not None


def test_image_append():
    img = core.Image(2, 2)
    # 2x2 RGBA = 16 bytes, stride = 8
    pixels = bytes([255, 0, 0, 255] * 4)
    img.append(pixels, 2, 2, 8)


# ── OpenTypeFeatures ─────────────────────────────────────────────────


def test_otf_creation():
    otf = core.OpenTypeFeatures()
    assert otf is not None


def test_otf_add_get_remove():
    otf = core.OpenTypeFeatures()
    otf.add("liga", 1)
    assert otf.get("liga") == 1
    otf.remove("liga")
    assert otf.get("liga") is None


def test_otf_clone():
    otf = core.OpenTypeFeatures()
    otf.add("liga", 1)
    clone = otf.clone()
    assert clone.get("liga") == 1
    # Modifying clone doesn't affect original
    clone.remove("liga")
    assert otf.get("liga") == 1


def test_otf_items():
    otf = core.OpenTypeFeatures()
    otf.add("liga", 1)
    otf.add("kern", 0)
    items = otf.items()
    tags = {tag for tag, val in items}
    assert "liga" in tags
    assert "kern" in tags


# ── Attribute factory functions ──────────────────────────────────────


def test_family_attribute():
    a = core.family_attribute("Arial")
    assert a.type == core.AttributeKind.FAMILY
    assert a.family == "Arial"


def test_size_attribute():
    a = core.size_attribute(12.0)
    assert a.type == core.AttributeKind.SIZE
    assert abs(a.size - 12.0) < 0.01


def test_weight_attribute():
    a = core.weight_attribute(core.TextWeight.BOLD)
    assert a.type == core.AttributeKind.WEIGHT
    assert a.weight == core.TextWeight.BOLD


def test_italic_attribute():
    a = core.italic_attribute(core.TextItalic.ITALIC)
    assert a.type == core.AttributeKind.ITALIC
    assert a.italic == core.TextItalic.ITALIC


def test_stretch_attribute():
    a = core.stretch_attribute(core.TextStretch.EXPANDED)
    assert a.type == core.AttributeKind.STRETCH
    assert a.stretch == core.TextStretch.EXPANDED


def test_color_attribute():
    a = core.color_attribute(1.0, 0.0, 0.0, 1.0)
    assert a.type == core.AttributeKind.COLOR
    r, g, b, al = a.color
    assert abs(r - 1.0) < 0.01


def test_background_attribute():
    a = core.background_attribute(0.0, 1.0, 0.0, 0.5)
    assert a.type == core.AttributeKind.BACKGROUND


def test_underline_attribute():
    a = core.underline_attribute(core.Underline.SINGLE)
    assert a.type == core.AttributeKind.UNDERLINE
    assert a.underline == core.Underline.SINGLE


def test_underline_color_attribute():
    a = core.underline_color_attribute(core.UnderlineColor.CUSTOM, 1.0, 0.0, 0.0, 1.0)
    assert a.type == core.AttributeKind.UNDERLINE_COLOR
    kind, r, g, b, al = a.underline_color
    assert kind == core.UnderlineColor.CUSTOM


def test_features_attribute():
    otf = core.OpenTypeFeatures()
    otf.add("liga", 1)
    a = core.features_attribute(otf)
    assert a.type == core.AttributeKind.FEATURES
    feat = a.features
    assert feat.get("liga") == 1


# ── AttributedString ─────────────────────────────────────────────────


def test_attributed_string_creation():
    s = core.AttributedString("hello")
    assert s.string == "hello"
    assert s.length == 5


def test_attributed_string_append():
    s = core.AttributedString("hello")
    s.append(" world")
    assert s.string == "hello world"


def test_attributed_string_insert_at():
    s = core.AttributedString("hllo")
    s.insert_at("e", 1)
    assert s.string == "hello"


def test_attributed_string_delete():
    s = core.AttributedString("hello world")
    s.delete(5, 11)
    assert s.string == "hello"


def test_attributed_string_set_attribute():
    s = core.AttributedString("hello")
    a = core.color_attribute(1.0, 0.0, 0.0, 1.0)
    s.set_attribute(a, 0, 5)


def test_attributed_string_for_each():
    s = core.AttributedString("hello")
    a = core.color_attribute(1.0, 0.0, 0.0, 1.0)
    s.set_attribute(a, 0, 5)
    attrs = []

    def cb(attr, start, end):
        attrs.append((attr.type, start, end))
        return False

    s.for_each_attribute(cb)
    assert len(attrs) > 0


def test_attributed_string_graphemes():
    s = core.AttributedString("hello")
    n = s.num_graphemes()
    assert n == 5
    assert s.byte_index_to_grapheme(0) == 0
    assert s.grapheme_to_byte_index(0) == 0


# ── DrawPath ─────────────────────────────────────────────────────────


def test_draw_path_creation():
    p = core.DrawPath()
    assert p.ended is False


def test_draw_path_rectangle():
    p = core.DrawPath()
    p.add_rectangle(0, 0, 100, 100)
    p.end()
    assert p.ended is True


def test_draw_path_figure():
    p = core.DrawPath()
    p.new_figure(10, 10)
    p.line_to(50, 50)
    p.line_to(10, 50)
    p.close_figure()
    p.end()


def test_draw_path_arc():
    p = core.DrawPath()
    p.new_figure_with_arc(50, 50, 25, 0, 2 * math.pi, False)
    p.end()


def test_draw_path_bezier():
    p = core.DrawPath()
    p.new_figure(0, 0)
    p.bezier_to(10, 20, 30, 40, 50, 60)
    p.end()


# ── DrawBrush ────────────────────────────────────────────────────────


def test_draw_brush_creation():
    b = core.DrawBrush()
    assert b.type == core.BrushType.SOLID
    assert abs(b.a - 1.0) < 0.01


def test_draw_brush_properties():
    b = core.DrawBrush()
    b.r = 1.0
    b.g = 0.5
    b.b = 0.0
    b.a = 0.8
    assert abs(b.r - 1.0) < 0.01
    assert abs(b.g - 0.5) < 0.01


def test_draw_brush_gradient():
    b = core.DrawBrush()
    b.type = core.BrushType.LINEAR_GRADIENT
    b.x0 = 0.0
    b.y0 = 0.0
    b.x1 = 100.0
    b.y1 = 100.0
    b.set_stops(
        [
            (0.0, 1.0, 0.0, 0.0, 1.0),
            (1.0, 0.0, 0.0, 1.0, 1.0),
        ]
    )


# ── DrawStrokeParams ────────────────────────────────────────────────


def test_draw_stroke_params():
    sp = core.DrawStrokeParams()
    assert sp.cap == core.LineCap.FLAT
    assert sp.join == core.LineJoin.MITER
    assert abs(sp.thickness - 1.0) < 0.01
    sp.thickness = 2.5
    assert abs(sp.thickness - 2.5) < 0.01


def test_draw_stroke_params_dashes():
    sp = core.DrawStrokeParams()
    sp.set_dashes([5.0, 3.0])


# ── DrawMatrix ───────────────────────────────────────────────────────


def test_draw_matrix_identity():
    m = core.DrawMatrix()
    assert abs(m.m11 - 1.0) < 0.01
    assert abs(m.m22 - 1.0) < 0.01
    assert abs(m.m12) < 0.01
    assert abs(m.m21) < 0.01


def test_draw_matrix_translate():
    m = core.DrawMatrix()
    m.translate(10, 20)
    assert abs(m.m31 - 10.0) < 0.01
    assert abs(m.m32 - 20.0) < 0.01


def test_draw_matrix_scale():
    m = core.DrawMatrix()
    m.scale(0, 0, 2.0, 3.0)
    assert abs(m.m11 - 2.0) < 0.01
    assert abs(m.m22 - 3.0) < 0.01


@pytest.mark.xfail(
    sys.platform == "darwin",
    reason="libui-ng Cocoa backend returns False for identity matrix",
)
def test_draw_matrix_invertible():
    m = core.DrawMatrix()
    assert m.invertible() is True


def test_draw_matrix_transform_point():
    m = core.DrawMatrix()
    m.translate(10, 20)
    x, y = m.transform_point(5, 5)
    assert abs(x - 15.0) < 0.01
    assert abs(y - 25.0) < 0.01


def test_draw_matrix_transform_size():
    m = core.DrawMatrix()
    m.scale(0, 0, 2.0, 3.0)
    w, h = m.transform_size(10, 10)
    assert abs(w - 20.0) < 0.01
    assert abs(h - 30.0) < 0.01


def test_draw_matrix_multiply():
    m1 = core.DrawMatrix()
    m1.translate(10, 0)
    m2 = core.DrawMatrix()
    m2.translate(0, 20)
    m1.multiply(m2)


def test_draw_matrix_invert():
    m = core.DrawMatrix()
    m.translate(10, 20)
    assert m.invert() is True


# ── Area ─────────────────────────────────────────────────────────────


def test_area_creation():
    def on_draw(ctx, aw, ah, cx, cy, cw, ch):
        pass

    a = core.Area(on_draw)
    assert a is not None
    a.destroy()


def test_scrolling_area_creation():
    def on_draw(ctx, aw, ah, cx, cy, cw, ch):
        pass

    a = core.ScrollingArea(on_draw, 800, 600)
    assert a is not None
    a.destroy()


# ── TableModel + Table ───────────────────────────────────────────────


def test_table_model_creation():
    data = [
        ["Alice", 30],
        ["Bob", 25],
    ]

    def num_columns():
        return 2

    def column_type(col):
        return core.TableValueType.STRING if col == 0 else core.TableValueType.INT

    def num_rows():
        return len(data)

    def cell_value(row, col):
        return data[row][col]

    model = core.TableModel(num_columns, column_type, num_rows, cell_value)
    assert model is not None


def test_table_creation():
    data = [["Alice", 30], ["Bob", 25]]

    model = core.TableModel(
        lambda: 2,
        lambda col: core.TableValueType.STRING if col == 0 else core.TableValueType.INT,
        lambda: len(data),
        lambda row, col: data[row][col],
    )

    table = core.Table(model)
    table.append_text_column("Name", 0)
    table.append_text_column("Age", 1)
    assert table.header_visible is True
    table.destroy()


# ── Enum class behavior ─────────────────────────────────────────────


def test_enum_classes_exist():
    assert issubclass(core.BrushType, enum.IntEnum)
    assert issubclass(core.LineCap, enum.IntEnum)
    assert issubclass(core.LineJoin, enum.IntEnum)
    assert issubclass(core.FillMode, enum.IntEnum)
    assert issubclass(core.TextAlign, enum.IntEnum)
    assert issubclass(core.Modifier, enum.IntFlag)
    assert issubclass(core.ExtKey, enum.IntEnum)
    assert issubclass(core.Align, enum.IntEnum)
    assert issubclass(core.At, enum.IntEnum)
    assert issubclass(core.TextWeight, enum.IntEnum)
    assert issubclass(core.TextItalic, enum.IntEnum)
    assert issubclass(core.TextStretch, enum.IntEnum)
    assert issubclass(core.Underline, enum.IntEnum)
    assert issubclass(core.UnderlineColor, enum.IntEnum)
    assert issubclass(core.TableValueType, enum.IntEnum)
    assert issubclass(core.TableModelColumn, enum.IntEnum)
    assert issubclass(core.SelectionMode, enum.IntEnum)
    assert issubclass(core.SortIndicator, enum.IntEnum)
    assert issubclass(core.ForEach, enum.IntEnum)
    assert issubclass(core.WindowResizeEdge, enum.IntEnum)
    assert issubclass(core.AttributeKind, enum.IntEnum)


def test_enum_members():
    assert core.BrushType.SOLID == 0
    assert core.BrushType.LINEAR_GRADIENT == 1
    assert core.TextWeight.BOLD == 700
    assert core.TextWeight.NORMAL == 400
    assert core.Modifier.CTRL == 1
    assert core.Modifier.SHIFT == 4
    assert core.ExtKey.ESCAPE == 1
    assert core.ForEach.STOP == 1
    assert core.TableModelColumn.NEVER_EDITABLE == -1
    assert core.TableModelColumn.ALWAYS_EDITABLE == -2
    assert core.SortIndicator.NONE == 0


def test_enum_isinstance():
    assert isinstance(core.BrushType.SOLID, core.BrushType)
    assert isinstance(core.BrushType.SOLID, int)
    assert isinstance(core.TextWeight.BOLD, core.TextWeight)
    assert isinstance(core.Modifier.CTRL, core.Modifier)


def test_enum_iteration():
    members = list(core.BrushType)
    assert len(members) == 4
    names = [m.name for m in core.BrushType]
    assert "SOLID" in names
    assert "LINEAR_GRADIENT" in names


def test_enum_repr():
    r = repr(core.BrushType.SOLID)
    assert "BrushType" in r
    assert "SOLID" in r


def test_modifier_flags():
    combined = core.Modifier.CTRL | core.Modifier.SHIFT
    assert combined == 5
    assert isinstance(combined, core.Modifier)
