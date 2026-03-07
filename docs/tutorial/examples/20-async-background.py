"""Async background tasks — concurrent work with UI updates."""

import asyncio
import libui
from libui.declarative import (
    App,
    Window,
    VBox,
    Label,
    Button,
    ProgressBar,
    State,
)


async def main():
    app = App()
    status = State("Ready.")
    progress = State(0)

    async def do_work():
        status.set("Working...")
        for i in range(1, 101):
            await asyncio.sleep(0.03)
            progress.set(i)
        status.set("Done!")
        await asyncio.sleep(1)
        progress.set(0)
        status.set("Ready.")

    # Background ticker
    async def ticker():
        n = 0
        while True:
            await asyncio.sleep(2)
            n += 1
            if progress.value == 0:
                status.set(f"Idle tick #{n}")

    asyncio.create_task(ticker())

    app.build(
        window=Window(
            "Async Background",
            400,
            200,
            child=VBox(
                Label(text=status),
                ProgressBar(value=progress),
                Button("Start Work", on_clicked=do_work),
            ),
        )
    )

    app.show()
    await app.wait()


libui.run(main())
