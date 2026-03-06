"""Declarative widget nodes — split by category."""

from libui.widgets.containers import (
    VBox,
    HBox,
    Group,
    Form,
    Tab,
    Grid,
    GridCell,
)
from libui.widgets.label import Label
from libui.widgets.button import Button
from libui.widgets.entry import Entry, MultilineEntry
from libui.widgets.checkbox import Checkbox
from libui.widgets.slider import Slider
from libui.widgets.spinbox import Spinbox
from libui.widgets.progressbar import ProgressBar
from libui.widgets.combobox import Combobox, EditableCombobox
from libui.widgets.radiobuttons import RadioButtons
from libui.widgets.pickers import ColorButton, FontButton, DateTimePicker
from libui.widgets.separator import Separator
from libui.widgets.draw import DrawArea, ScrollingDrawArea
from libui.widgets.table import (
    DataTable,
    TextColumn,
    CheckboxColumn,
    CheckboxTextColumn,
    ProgressColumn,
    ButtonColumn,
    ImageColumn,
    ImageTextColumn,
)

__all__ = [
    # Containers
    "VBox",
    "HBox",
    "Group",
    "Form",
    "Tab",
    "Grid",
    "GridCell",
    # Leaf widgets
    "Label",
    "Button",
    "Entry",
    "Checkbox",
    "Slider",
    "Spinbox",
    "ProgressBar",
    "Combobox",
    "RadioButtons",
    "EditableCombobox",
    "MultilineEntry",
    "ColorButton",
    "FontButton",
    "DateTimePicker",
    "Separator",
    # Drawing
    "DrawArea",
    "ScrollingDrawArea",
    # Table
    "DataTable",
    "TextColumn",
    "CheckboxColumn",
    "CheckboxTextColumn",
    "ProgressColumn",
    "ButtonColumn",
    "ImageColumn",
    "ImageTextColumn",
]
