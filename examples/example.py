"""Synchronous example with multiple widgets using the low-level core API."""

from libui import core


def main():
    core.init()

    window = core.Window("Widget Demo", 500, 400)

    vbox = core.Box(vertical=True)
    vbox.padded = True
    window.set_child(vbox)

    # Label
    label = core.Label("Hello, libui-ng!")
    vbox.append(label)

    # Button with click counter
    count = 0

    def on_click():
        nonlocal count
        count += 1
        label.text = f"Clicked {count} time(s)"

    button = core.Button("Click me")
    button.on_clicked(on_click)
    vbox.append(button)

    # Text entry
    entry = core.Entry()
    entry.text = "Type here..."
    vbox.append(entry)

    # Checkbox
    checkbox = core.Checkbox("Enable feature")

    def on_toggled():
        label.text = f"Checkbox: {'checked' if checkbox.checked else 'unchecked'}"

    checkbox.on_toggled(on_toggled)
    vbox.append(checkbox)

    # Combobox
    combo = core.Combobox()
    combo.append("Option A")
    combo.append("Option B")
    combo.append("Option C")
    combo.selected = 0
    vbox.append(combo)

    def on_closing():
        core.quit()
        return True

    window.on_closing(on_closing)
    window.show()

    core.main()
    core.uninit()


if __name__ == "__main__":
    main()
