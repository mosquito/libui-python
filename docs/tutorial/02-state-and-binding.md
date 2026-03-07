# State and Binding

State is the foundation of the declarative API. This chapter covers `State`, `Computed`, and two-way binding.

## Basic state

`State[T]` holds a value and notifies subscribers when it changes:

```{literalinclude} examples/01-state-binding.py
```

```{image} screenshots/01-state-binding.png
:alt: State binding demo
```

Key points:

- `State("World")` — creates a state with an initial value
- `name.value = "Python"` — setting `.value` notifies all subscribers
- `name.set("value")` — equivalent to setting `.value`
- `name.subscribe(cb)` — registers a callback; returns an unsubscribe function

## Computed state

`Computed` is a read-only derived state created with `.map()`:

```{literalinclude} examples/02-computed-state.py
```

```{image} screenshots/02-computed-state.png
:alt: Computed state demo
```

Key points:

- `count.map(fn)` — creates a `Computed` that auto-updates when `count` changes
- Computed values can be chained: `a.map(f).map(g)`
- Computed values are read-only — you can't set them directly
- Pass `Computed` to widget props like `Label(text=...)` for automatic updates

## Two-way binding

When you pass a `State` to a widget that supports user input, you get two-way binding — the widget updates the state, and state changes update the widget:

```python
text = State("")
Entry(text=text)  # two-way: typing updates state, state updates entry
```

Compare with one-way binding:

```python
Label(text=text)           # one-way: state -> widget (State)
Label(text=text.map(str))  # one-way: state -> widget (Computed)
Label(text="static")       # no binding: plain value
```

Widgets that support two-way binding: `Entry`, `MultilineEntry`, `Checkbox`, `Slider`, `Spinbox`, `Combobox`, `EditableCombobox`, `RadioButtons`.
