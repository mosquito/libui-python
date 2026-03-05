"""Minimal synchronous window example using the low-level core API."""

from libui import core


def main():
    core.init()

    window = core.Window("Simple Window", 400, 300)

    def on_closing():
        core.quit()
        return True

    window.on_closing(on_closing)
    window.show()

    core.main()
    core.uninit()


if __name__ == "__main__":
    main()
