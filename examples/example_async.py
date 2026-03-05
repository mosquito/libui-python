"""Async example with multiple widgets and an async background task."""

import asyncio
import libui


async def main():
    window = libui.Window("Async Widget Demo", 500, 400)

    vbox = libui.VerticalBox(padded=True)
    window.set_child(vbox)

    label = libui.Label("Hello, libui-ng!")
    vbox.append(label)

    # Button with async callback
    count = 0

    async def on_click():
        nonlocal count
        count += 1
        label.text = f"Clicked {count} time(s)"

    button = libui.Button("Click me")
    button.on_clicked(on_click)
    vbox.append(button)

    # Text entry with change callback
    entry = libui.Entry()

    def on_entry_changed():
        label.text = f"Entry: {entry.text}"

    entry.on_changed(on_entry_changed)
    vbox.append(entry)

    # Checkbox
    checkbox = libui.Checkbox("Enable feature")

    def on_toggled():
        label.text = f"Checkbox: {'checked' if checkbox.checked else 'unchecked'}"

    checkbox.on_toggled(on_toggled)
    vbox.append(checkbox)

    # Combobox
    combo = libui.Combobox()
    options = ["Option A", "Option B", "Option C"]
    for opt in options:
        combo.append(opt)
    combo.selected = 0

    def on_selected():
        idx = combo.selected
        if 0 <= idx < len(options):
            label.text = f"Selected: {options[idx]}"

    combo.on_selected(on_selected)
    vbox.append(combo)

    # Background async task — updates label every second
    async def ticker():
        tick = 0
        while True:
            await asyncio.sleep(2)
            tick += 1
            label.text = f"Tick #{tick}"

    asyncio.create_task(ticker())

    def on_closing():
        libui.quit()
        return True

    window.on_closing(on_closing)
    window.show()

    await asyncio.Event().wait()


if __name__ == "__main__":
    libui.run(main())
