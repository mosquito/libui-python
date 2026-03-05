"""Minimal example: a window with a button that increments a label."""

import asyncio
import libui


async def main():
    window = libui.Window("Hello libui-ng", 400, 300)

    box = libui.VerticalBox(padded=True)
    window.set_child(box)

    label = libui.Label("Count: 0")
    box.append(label)

    count = 0

    def on_click():
        nonlocal count
        count += 1
        label.text = f"Count: {count}"

    button = libui.Button("Click me!")
    button.on_clicked(on_click)
    box.append(button)

    def on_closing():
        libui.quit()
        return True

    window.on_closing(on_closing)
    window.show()

    # Keep alive until the window is closed
    await asyncio.Event().wait()


if __name__ == "__main__":
    libui.run(main())
