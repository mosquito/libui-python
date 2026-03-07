"""Python bindings for libui-ng — thread-safe proxy wrappers."""

from libui import core
from libui.loop import (
    _ensure_sync,
    _register_window,
    invoke_on_main,
    invoke_on_main_async,
    quit,
    run,
)

# -- Re-exports that need no wrapping ----------------------------------

from libui.core import (
    # Base
    Control,
    # Menu (not uiControl — direct re-export, guarded by ENSURE_MAIN_THREAD)
    Menu,
    MenuItem,
    # Complex widgets (not proxied)
    Image,
    OpenTypeFeatures,
    Attribute,
    AttributedString,
    DrawPath,
    DrawBrush,
    DrawStrokeParams,
    DrawMatrix,
    DrawContext,
    DrawTextLayout,
    Area,
    ScrollingArea,
    TableModel,
    # Attribute factory functions
    family_attribute,
    size_attribute,
    weight_attribute,
    italic_attribute,
    stretch_attribute,
    color_attribute,
    background_attribute,
    underline_attribute,
    underline_color_attribute,
    features_attribute,
    # Enum classes
    Align,
    At,
    BrushType,
    LineCap,
    LineJoin,
    FillMode,
    TextAlign,
    Modifier,
    ExtKey,
    WindowResizeEdge,
    AttributeKind,
    TextWeight,
    TextItalic,
    TextStretch,
    Underline,
    UnderlineColor,
    TableValueType,
    TableModelColumn,
    SelectionMode,
    SortIndicator,
    ForEach,
)


# -- Proxy infrastructure ---------------------------------------------


class _CachedProperty:
    """Descriptor: reads from Python cache, writes cache + queues C set."""

    def __init__(self, name):
        self.name = name

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        return obj._cache.get(self.name)

    def __set__(self, obj, value):
        obj._cache[self.name] = value
        name, ctrl = self.name, obj._core
        core.queue_main(lambda: setattr(ctrl, name, value))


class _Proxy:
    """Base proxy: wraps a core widget and dispatches mutations via queue_main."""

    _cached_props: tuple[str, ...] = ()

    def __init__(self, *args, _core=None, **kwargs):
        object.__setattr__(self, "_cache", {})
        if _core is not None:
            object.__setattr__(self, "_core", _core)
        else:
            object.__setattr__(
                self, "_core", invoke_on_main(self._create_core, *args, **kwargs)
            )
        self._sync_cache()

    @classmethod
    def _create_core(cls, *a, **kw):
        raise NotImplementedError

    def _sync_cache(self):
        """Populate cache from the core widget. Must run on main thread."""

        def _read():
            for p in self._cached_props:
                try:
                    self._cache[p] = getattr(self._core, p)
                except Exception:
                    pass

        # _sync_cache is called right after invoke_on_main(_create_core),
        # so we're on the asyncio thread — dispatch to main.
        invoke_on_main(_read)

    def show(self):
        core.queue_main(self._core.show)

    def hide(self):
        core.queue_main(self._core.hide)

    def enable(self):
        core.queue_main(self._core.enable)

    def disable(self):
        core.queue_main(self._core.disable)

    def destroy(self):
        core.queue_main(self._core.destroy)


# -- Widget proxies ---------------------------------------------------


class Label(_Proxy):
    _cached_props = ("text",)
    text = _CachedProperty("text")

    @classmethod
    def _create_core(cls, text=""):
        return core.Label(text)


class Button(_Proxy):
    _cached_props = ("text",)
    text = _CachedProperty("text")

    @classmethod
    def _create_core(cls, text=""):
        return core.Button(text)

    def on_clicked(self, cb):
        cb = _ensure_sync(cb)
        core.queue_main(lambda: self._core.on_clicked(cb))


class Entry(_Proxy):
    _cached_props = ("text", "read_only")
    text = _CachedProperty("text")
    read_only = _CachedProperty("read_only")

    @classmethod
    def _create_core(cls, type="normal"):
        return core.Entry(type=type)

    def on_changed(self, cb):
        cb = _ensure_sync(cb)

        def _wrapper():
            self._cache["text"] = self._core.text
            if cb:
                cb()

        core.queue_main(lambda: self._core.on_changed(_wrapper))


class Checkbox(_Proxy):
    _cached_props = ("text", "checked")
    text = _CachedProperty("text")
    checked = _CachedProperty("checked")

    @classmethod
    def _create_core(cls, text=""):
        return core.Checkbox(text)

    def on_toggled(self, cb):
        cb = _ensure_sync(cb)

        def _wrapper():
            self._cache["checked"] = self._core.checked
            if cb:
                cb()

        core.queue_main(lambda: self._core.on_toggled(_wrapper))


class Combobox(_Proxy):
    _cached_props = ("selected",)
    selected = _CachedProperty("selected")

    @classmethod
    def _create_core(cls):
        return core.Combobox()

    def append(self, text):
        core.queue_main(lambda: self._core.append(text))

    def on_selected(self, cb):
        cb = _ensure_sync(cb)

        def _wrapper():
            self._cache["selected"] = self._core.selected
            if cb:
                cb()

        core.queue_main(lambda: self._core.on_selected(_wrapper))


class Slider(_Proxy):
    _cached_props = ("value", "has_tooltip")
    value = _CachedProperty("value")
    has_tooltip = _CachedProperty("has_tooltip")

    @classmethod
    def _create_core(cls, min=0, max=100):
        return core.Slider(min, max)

    def on_changed(self, cb):
        cb = _ensure_sync(cb)

        def _wrapper():
            self._cache["value"] = self._core.value
            if cb:
                cb()

        core.queue_main(lambda: self._core.on_changed(_wrapper))

    def on_released(self, cb):
        cb = _ensure_sync(cb)
        core.queue_main(lambda: self._core.on_released(cb))

    def set_range(self, min, max):
        core.queue_main(lambda: self._core.set_range(min, max))


class Spinbox(_Proxy):
    _cached_props = ("value",)
    value = _CachedProperty("value")

    @classmethod
    def _create_core(cls, min=0, max=100):
        return core.Spinbox(min, max)

    def on_changed(self, cb):
        cb = _ensure_sync(cb)

        def _wrapper():
            self._cache["value"] = self._core.value
            if cb:
                cb()

        core.queue_main(lambda: self._core.on_changed(_wrapper))


class ProgressBar(_Proxy):
    _cached_props = ("value",)
    value = _CachedProperty("value")

    @classmethod
    def _create_core(cls):
        return core.ProgressBar()


class ColorButton(_Proxy):
    _cached_props = ("color",)
    color = _CachedProperty("color")

    @classmethod
    def _create_core(cls):
        return core.ColorButton()

    def on_changed(self, cb):
        cb = _ensure_sync(cb)

        def _wrapper():
            self._cache["color"] = self._core.color
            if cb:
                cb()

        core.queue_main(lambda: self._core.on_changed(_wrapper))


class FontButton(_Proxy):
    @classmethod
    def _create_core(cls):
        return core.FontButton()

    @property
    def font(self):
        return invoke_on_main(lambda: self._core.font)

    def on_changed(self, cb):
        cb = _ensure_sync(cb)
        core.queue_main(lambda: self._core.on_changed(cb))


class DateTimePicker(_Proxy):
    _cached_props = ("time",)
    time = _CachedProperty("time")

    @classmethod
    def _create_core(cls, type="datetime"):
        return core.DateTimePicker(type=type)

    def on_changed(self, cb):
        cb = _ensure_sync(cb)

        def _wrapper():
            self._cache["time"] = self._core.time
            if cb:
                cb()

        core.queue_main(lambda: self._core.on_changed(_wrapper))


class EditableCombobox(_Proxy):
    _cached_props = ("text",)
    text = _CachedProperty("text")

    @classmethod
    def _create_core(cls):
        return core.EditableCombobox()

    def append(self, text):
        core.queue_main(lambda: self._core.append(text))

    def on_changed(self, cb):
        cb = _ensure_sync(cb)

        def _wrapper():
            self._cache["text"] = self._core.text
            if cb:
                cb()

        core.queue_main(lambda: self._core.on_changed(_wrapper))


class MultilineEntry(_Proxy):
    _cached_props = ("text", "read_only")
    text = _CachedProperty("text")
    read_only = _CachedProperty("read_only")

    @classmethod
    def _create_core(cls, wrapping=True):
        return core.MultilineEntry(wrapping=wrapping)

    def append(self, text):
        core.queue_main(lambda: self._core.append(text))

    def on_changed(self, cb):
        cb = _ensure_sync(cb)

        def _wrapper():
            self._cache["text"] = self._core.text
            if cb:
                cb()

        core.queue_main(lambda: self._core.on_changed(_wrapper))


class RadioButtons(_Proxy):
    _cached_props = ("selected",)
    selected = _CachedProperty("selected")

    @classmethod
    def _create_core(cls):
        return core.RadioButtons()

    def append(self, text):
        core.queue_main(lambda: self._core.append(text))

    def on_selected(self, cb):
        cb = _ensure_sync(cb)

        def _wrapper():
            self._cache["selected"] = self._core.selected
            if cb:
                cb()

        core.queue_main(lambda: self._core.on_selected(_wrapper))


class Separator(_Proxy):
    @classmethod
    def _create_core(cls, vertical=False):
        return core.Separator(vertical=vertical)


class Tab(_Proxy):
    _cached_props = ("selected",)
    selected = _CachedProperty("selected")

    @classmethod
    def _create_core(cls):
        return core.Tab()

    def append(self, name, child):
        c = child._core if hasattr(child, "_core") else child
        core.queue_main(lambda: self._core.append(name, c))

    def delete(self, index):
        core.queue_main(lambda: self._core.delete(index))

    def insert_at(self, name, index, child):
        c = child._core if hasattr(child, "_core") else child
        core.queue_main(lambda: self._core.insert_at(name, index, c))

    def set_margined(self, index, margined):
        core.queue_main(lambda: self._core.set_margined(index, margined))

    def margined(self, index):
        return invoke_on_main(self._core.margined, index)

    def num_pages(self):
        return invoke_on_main(self._core.num_pages)

    def on_selected(self, cb):
        cb = _ensure_sync(cb)

        def _wrapper():
            self._cache["selected"] = self._core.selected
            if cb:
                cb()

        core.queue_main(lambda: self._core.on_selected(_wrapper))


class Table(_Proxy):
    _cached_props = ("header_visible", "selection", "selection_mode")
    header_visible = _CachedProperty("header_visible")
    selection = _CachedProperty("selection")
    selection_mode = _CachedProperty("selection_mode")

    @classmethod
    def _create_core(cls, model):
        return core.Table(model)

    def on_row_clicked(self, cb):
        cb = _ensure_sync(cb)
        core.queue_main(lambda: self._core.on_row_clicked(cb))

    def on_row_double_clicked(self, cb):
        cb = _ensure_sync(cb)
        core.queue_main(lambda: self._core.on_row_double_clicked(cb))

    def on_header_clicked(self, cb):
        cb = _ensure_sync(cb)
        core.queue_main(lambda: self._core.on_header_clicked(cb))

    def on_selection_changed(self, cb):
        cb = _ensure_sync(cb)
        core.queue_main(lambda: self._core.on_selection_changed(cb))

    def append_text_column(self, *args, **kwargs):
        core.queue_main(lambda: self._core.append_text_column(*args, **kwargs))

    def append_checkbox_column(self, *args, **kwargs):
        core.queue_main(lambda: self._core.append_checkbox_column(*args, **kwargs))

    def append_checkbox_text_column(self, *args, **kwargs):
        core.queue_main(lambda: self._core.append_checkbox_text_column(*args, **kwargs))

    def append_progress_bar_column(self, *args, **kwargs):
        core.queue_main(lambda: self._core.append_progress_bar_column(*args, **kwargs))

    def append_button_column(self, *args, **kwargs):
        core.queue_main(lambda: self._core.append_button_column(*args, **kwargs))

    def append_image_column(self, *args, **kwargs):
        core.queue_main(lambda: self._core.append_image_column(*args, **kwargs))

    def append_image_text_column(self, *args, **kwargs):
        core.queue_main(lambda: self._core.append_image_text_column(*args, **kwargs))

    def column_width(self, col):
        return invoke_on_main(self._core.column_width, col)

    def set_column_width(self, col, width):
        core.queue_main(lambda: self._core.set_column_width(col, width))

    def header_sort_indicator(self, col):
        return invoke_on_main(self._core.header_sort_indicator, col)

    def header_set_sort_indicator(self, col, indicator):
        core.queue_main(lambda: self._core.header_set_sort_indicator(col, indicator))


# -- Container proxies ------------------------------------------------


class Box(_Proxy):
    _cached_props = ("padded",)
    padded = _CachedProperty("padded")

    def append(self, child, stretchy=False):
        c = child._core if hasattr(child, "_core") else child
        core.queue_main(lambda: self._core.append(c, stretchy=stretchy))

    def delete(self, index):
        core.queue_main(lambda: self._core.delete(index))


class VerticalBox(Box):
    @classmethod
    def _create_core(cls, padded=False):
        w = core.VerticalBox()
        if padded:
            w.padded = True
        return w


class HorizontalBox(Box):
    @classmethod
    def _create_core(cls, padded=False):
        w = core.HorizontalBox()
        if padded:
            w.padded = True
        return w


class Group(_Proxy):
    _cached_props = ("title", "margined")
    title = _CachedProperty("title")
    margined = _CachedProperty("margined")

    @classmethod
    def _create_core(cls, title):
        return core.Group(title)

    def set_child(self, child):
        c = child._core if hasattr(child, "_core") else child
        core.queue_main(lambda: self._core.set_child(c))


class Form(_Proxy):
    _cached_props = ("padded",)
    padded = _CachedProperty("padded")

    @classmethod
    def _create_core(cls):
        return core.Form()

    def append(self, label, child, stretchy=False):
        c = child._core if hasattr(child, "_core") else child
        core.queue_main(lambda: self._core.append(label, c, stretchy=stretchy))

    def delete(self, index):
        core.queue_main(lambda: self._core.delete(index))


class Grid(_Proxy):
    _cached_props = ("padded",)
    padded = _CachedProperty("padded")

    @classmethod
    def _create_core(cls):
        return core.Grid()

    def append(
        self,
        child,
        left,
        top,
        xspan=1,
        yspan=1,
        hexpand=False,
        halign=Align.FILL,
        vexpand=False,
        valign=Align.FILL,
    ):
        c = child._core if hasattr(child, "_core") else child
        core.queue_main(
            lambda: self._core.append(
                c, left, top, xspan, yspan, hexpand, halign, vexpand, valign
            )
        )

    def insert_at(self, *args, **kwargs):
        core.queue_main(lambda: self._core.insert_at(*args, **kwargs))


# -- Window proxy -----------------------------------------------------


class Window(_Proxy):
    _cached_props = ("title", "margined", "borderless", "fullscreen", "resizeable")
    title = _CachedProperty("title")
    margined = _CachedProperty("margined")
    borderless = _CachedProperty("borderless")
    fullscreen = _CachedProperty("fullscreen")
    resizeable = _CachedProperty("resizeable")

    @classmethod
    def _create_core(cls, title, width=640, height=480, has_menubar=False):
        return core.Window(title, width, height, has_menubar=has_menubar)

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        _register_window(self)

    def set_child(self, child):
        c = child._core if hasattr(child, "_core") else child
        core.queue_main(lambda: self._core.set_child(c))

    def on_closing(self, cb):
        cb = _ensure_sync(cb, default_return=True)
        core.queue_main(lambda: self._core.on_closing(cb))


# -- Async dialog wrappers --------------------------------------------


async def open_file(window):
    w = window._core if hasattr(window, "_core") else window
    return await invoke_on_main_async(core.open_file, w)


async def open_folder(window):
    w = window._core if hasattr(window, "_core") else window
    return await invoke_on_main_async(core.open_folder, w)


async def save_file(window):
    w = window._core if hasattr(window, "_core") else window
    return await invoke_on_main_async(core.save_file, w)


async def msg_box(window, title, description):
    w = window._core if hasattr(window, "_core") else window
    return await invoke_on_main_async(core.msg_box, w, title, description)


async def msg_box_error(window, title, description):
    w = window._core if hasattr(window, "_core") else window
    return await invoke_on_main_async(core.msg_box_error, w, title, description)


__all__ = [
    "run",
    "quit",
    # Base
    "Control",
    # Containers
    "Box",
    "Form",
    "Grid",
    "Group",
    "HorizontalBox",
    "Tab",
    "VerticalBox",
    "Window",
    # Controls
    "Button",
    "Checkbox",
    "ColorButton",
    "Combobox",
    "DateTimePicker",
    "EditableCombobox",
    "Entry",
    "FontButton",
    "Label",
    "MultilineEntry",
    "ProgressBar",
    "RadioButtons",
    "Separator",
    "Slider",
    "Spinbox",
    # Menu
    "Menu",
    "MenuItem",
    # Complex widgets
    "Image",
    "OpenTypeFeatures",
    "Attribute",
    "AttributedString",
    "DrawPath",
    "DrawBrush",
    "DrawStrokeParams",
    "DrawMatrix",
    "DrawContext",
    "DrawTextLayout",
    "Area",
    "ScrollingArea",
    "TableModel",
    "Table",
    # Dialogs
    "msg_box",
    "msg_box_error",
    "open_file",
    "open_folder",
    "save_file",
    # Attribute factory functions
    "family_attribute",
    "size_attribute",
    "weight_attribute",
    "italic_attribute",
    "stretch_attribute",
    "color_attribute",
    "background_attribute",
    "underline_attribute",
    "underline_color_attribute",
    "features_attribute",
    # Enum classes
    "Align",
    "At",
    "BrushType",
    "LineCap",
    "LineJoin",
    "FillMode",
    "TextAlign",
    "Modifier",
    "ExtKey",
    "WindowResizeEdge",
    "AttributeKind",
    "TextWeight",
    "TextItalic",
    "TextStretch",
    "Underline",
    "UnderlineColor",
    "TableValueType",
    "TableModelColumn",
    "SelectionMode",
    "SortIndicator",
    "ForEach",
    # Bridge functions
    "invoke_on_main",
    "invoke_on_main_async",
]
