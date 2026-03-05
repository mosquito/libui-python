"""Declarative UI layer for python-libui-ng."""

from libui.declarative.state import Computed, ListState, State
from libui.declarative.node import BuildContext, Node, stretchy
from libui.declarative.nodes import (
    # Containers
    VBox,
    HBox,
    Group,
    Form,
    Tab,
    Grid,
    GridCell,
    # Leaf widgets
    Label,
    Button,
    Entry,
    Checkbox,
    Slider,
    Spinbox,
    ProgressBar,
    Combobox,
    RadioButtons,
    EditableCombobox,
    MultilineEntry,
    ColorButton,
    FontButton,
    DateTimePicker,
    Separator,
    # Drawing
    DrawArea,
    # Table
    DataTable,
    TextColumn,
    CheckboxColumn,
    CheckboxTextColumn,
    ProgressColumn,
    ButtonColumn,
    ImageColumn,
    ImageTextColumn,
)
from libui.declarative.app import (
    App,
    Window,
    MenuDef,
    MenuItem,
    CheckMenuItem,
    MenuSeparator,
    QuitItem,
    PreferencesItem,
    AboutItem,
)

__all__ = [
    # State
    "State",
    "Computed",
    "ListState",
    # Infrastructure
    "BuildContext",
    "Node",
    "stretchy",
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
    # Table
    "DataTable",
    "TextColumn",
    "CheckboxColumn",
    "CheckboxTextColumn",
    "ProgressColumn",
    "ButtonColumn",
    "ImageColumn",
    "ImageTextColumn",
    # App
    "App",
    "Window",
    "MenuDef",
    "MenuItem",
    "CheckMenuItem",
    "MenuSeparator",
    "QuitItem",
    "PreferencesItem",
    "AboutItem",
]
