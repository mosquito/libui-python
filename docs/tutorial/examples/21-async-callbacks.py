"""Async callbacks — event handlers that are coroutines."""
import asyncio
import libui
from libui.declarative import (
    App, Window, VBox,
    Label, Button, ProgressBar, State,
)


async def main():
    app = App()
    status = State("Click a button.")
    progress = State(0)

    async def fetch_data():
        """Simulate an async network request."""
        status.set("Fetching data...")
        for i in range(1, 101):
            await asyncio.sleep(0.02)
            progress.set(i)
        status.set("Data loaded!")
        progress.set(0)

    async def save_data():
        """Simulate saving with a dialog."""
        path = await app.save_file_async()
        if not path:
            status.set("Save cancelled.")
            return
        status.set(f"Saving to {path}...")
        await asyncio.sleep(1)
        status.set(f"Saved to {path}")

    def sync_action():
        """A sync callback runs on the main thread."""
        status.set("Sync action executed!")

    app.build(window=Window(
        "Async Callbacks", 450, 250,
        child=VBox(
            Label(text=status),
            ProgressBar(value=progress),
            Button("Fetch Data (async)", on_clicked=fetch_data),
            Button("Save Data (async)", on_clicked=save_data),
            Button("Sync Action", on_clicked=sync_action),
        ),
    ))

    app.show()
    await app.wait()


libui.run(main())
