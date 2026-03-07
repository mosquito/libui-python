# Controls

This chapter covers all input widgets available in the declarative API.

## Text entry

`Entry` supports three types: `"normal"`, `"password"`, and `"search"`:

```{literalinclude} examples/07-entry-types.py
```

```{image} screenshots/07-entry-types.png
:alt: Entry types
```

`MultilineEntry` provides multi-line text editing with optional word wrapping.

## Checkbox, Slider, and Spinbox

These controls support two-way binding with `State`:

```{literalinclude} examples/08-checkbox-slider-spinbox.py
```

```{image} screenshots/08-checkbox-slider-spinbox.png
:alt: Checkbox, slider, and spinbox
```

When multiple widgets bind to the same `State`, they stay in sync automatically. In this example, the slider and spinbox share a `State[int]` — dragging the slider updates the spinbox and vice versa.

## Combobox and RadioButtons

`Combobox` is a dropdown selector, `RadioButtons` shows all options at once. Both use an index-based `selected` state:

```{literalinclude} examples/09-combobox-radio.py
```

```{image} screenshots/09-combobox-radio.png
:alt: Combobox and radio buttons
```

`EditableCombobox` combines a dropdown with a free-text entry. It binds to a `State[str]` via `text` instead of `selected`.

## Pickers

Color, font, and date/time pickers provide native OS dialogs:

```{literalinclude} examples/10-pickers.py
```

```{image} screenshots/10-pickers.png
:alt: Pickers
```

`DateTimePicker` supports three types: `"datetime"`, `"date"`, and `"time"`.

## ProgressBar

`ProgressBar` displays a value from 0 to 100. It supports one-way binding only (no user input):

```{literalinclude} examples/11-progressbar.py
```

```{image} screenshots/11-progressbar.png
:alt: Progress bar
```

## Separator

`Separator()` draws a horizontal line. Use `Separator(vertical=True)` for a vertical line in an `HBox`.
