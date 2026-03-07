# Controls

This chapter covers all input widgets available in the declarative API.

## Text entry

`Entry` supports three types: `"normal"`, `"password"`, and `"search"`:

```{literalinclude} examples/07-entry-types.py
```

```{figure} screenshots/07-entry-types.png
:alt: Entry types
:target: _images/07-entry-types.png
:class: screenshot
```

`MultilineEntry` provides multi-line text editing with optional word wrapping.

## Checkbox, Slider, and Spinbox

These controls support two-way binding with `State`:

```{literalinclude} examples/08-checkbox-slider-spinbox.py
```

```{figure} screenshots/08-checkbox-slider-spinbox.png
:alt: Checkbox, slider, and spinbox
:target: _images/08-checkbox-slider-spinbox.png
:class: screenshot
```

When multiple widgets bind to the same `State`, they stay in sync automatically. In this example, the slider and spinbox share a `State[int]` — dragging the slider updates the spinbox and vice versa.

## Combobox and RadioButtons

`Combobox` is a dropdown selector, `RadioButtons` shows all options at once. Both use an index-based `selected` state:

```{literalinclude} examples/09-combobox-radio.py
```

```{figure} screenshots/09-combobox-radio.png
:alt: Combobox and radio buttons
:target: _images/09-combobox-radio.png
:class: screenshot
```

`EditableCombobox` combines a dropdown with a free-text entry. It binds to a `State[str]` via `text` instead of `selected`.

## Pickers

Color, font, and date/time pickers provide native OS dialogs:

```{literalinclude} examples/10-pickers.py
```

```{figure} screenshots/10-pickers.png
:alt: Pickers
:target: _images/10-pickers.png
:class: screenshot
```

`DateTimePicker` supports three types: `"datetime"`, `"date"`, and `"time"`.

## ProgressBar

`ProgressBar` displays a value from 0 to 100. It supports one-way binding only (no user input):

```{literalinclude} examples/11-progressbar.py
```

```{figure} screenshots/11-progressbar.png
:alt: Progress bar
:target: _images/11-progressbar.png
:class: screenshot
```

## Separator

`Separator()` draws a horizontal line. Use `Separator(vertical=True)` for a vertical line in an `HBox`.
