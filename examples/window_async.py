"""Async window example — the window stays open until closed by the user."""

import asyncio
import libui


async def main():
    window = libui.Window("Async Window", 400, 300)

    def on_closing():
        libui.quit()
        return True

    window.on_closing(on_closing)
    window.show()

    # Keep running until the quit signal
    await asyncio.Event().wait()


if __name__ == "__main__":
    libui.run(main())
