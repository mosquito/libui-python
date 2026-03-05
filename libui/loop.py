"""Two-thread architecture: main thread owns libui, asyncio in background."""

from __future__ import annotations

import asyncio
import inspect
import logging
import queue
import threading

from libui import core

_log = logging.getLogger("libui")

# Module-level reference to the asyncio loop (set during run())
_asyncio_loop: asyncio.AbstractEventLoop | None = None

_live_windows: set = set()


def _register_window(window) -> None:
    """Track a window so it can be destroyed on shutdown."""
    _live_windows.add(window)


def _handle_task_exception(task):
    if task.cancelled():
        return
    exc = task.exception()
    if exc:
        _log.exception("Unhandled exception in async callback", exc_info=exc)


def _ensure_sync(cb, default_return=None):
    """Wrap an async callback into a sync function that schedules it on the
    asyncio thread.  Sync callbacks pass through untouched.  ``None`` passes
    through as ``None``.
    """
    if cb is None or not inspect.iscoroutinefunction(cb):
        return cb

    def wrapper(*args, **kwargs):
        coro = cb(*args, **kwargs)

        def _schedule():
            task = _asyncio_loop.create_task(coro)
            task.add_done_callback(_handle_task_exception)

        if _asyncio_loop is not None and _asyncio_loop.is_running():
            _asyncio_loop.call_soon_threadsafe(_schedule)
        return default_return

    return wrapper


# ── Bridge functions ──────────────────────────────────────────────────


def invoke_on_main(fn, *args, **kwargs):
    """Block the calling thread until *fn* runs on the main UI thread.

    Returns the result of *fn(\\*args, \\*\\*kwargs)*.  If *fn* raises, the
    exception is re-raised in the caller.
    """
    q = queue.Queue(1)

    def _run():
        try:
            q.put((True, fn(*args, **kwargs)))
        except Exception as e:
            q.put((False, e))

    core.queue_main(_run)
    ok, val = q.get()
    if not ok:
        raise val
    return val


async def invoke_on_main_async(fn, *args, **kwargs):
    """Await the result of *fn* running on the main UI thread (non-blocking)."""
    loop = asyncio.get_running_loop()
    fut = loop.create_future()

    def _run():
        try:
            result = fn(*args, **kwargs)
            loop.call_soon_threadsafe(fut.set_result, result)
        except Exception as e:
            loop.call_soon_threadsafe(fut.set_exception, e)

    core.queue_main(_run)
    return await fut


# ── quit / run ────────────────────────────────────────────────────────


def quit() -> None:
    """Signal the UI event loop to stop.

    Safe to call from any thread.
    """
    core.quit()


def run(coro) -> None:
    """Run *coro* with the libui event loop.

    This is a **synchronous** function — the new entry point is simply::

        libui.run(main())

    Main thread: initialises libui, pumps ``main_step(wait=True)``.
    Background thread: runs ``asyncio.run(coro)``.
    """
    global _asyncio_loop

    core.init()
    core.main_steps()

    quit_event = threading.Event()
    startup_event = threading.Event()
    loop_holder: dict = {}
    task_holder: dict = {}

    async def _asyncio_main():
        aloop = asyncio.get_running_loop()
        loop_holder["loop"] = aloop
        task_holder["task"] = asyncio.current_task()
        core._set_asyncio_loop(aloop)
        startup_event.set()
        try:
            await coro
        except asyncio.CancelledError:
            pass
        finally:
            if not quit_event.is_set():
                quit_event.set()
                core.queue_main(core.quit)

    thread = threading.Thread(
        target=asyncio.run, args=(_asyncio_main(),), daemon=True,
    )
    thread.start()
    startup_event.wait()
    _asyncio_loop = loop_holder["loop"]

    def _on_should_quit():
        quit_event.set()
        return 1

    core.on_should_quit(_on_should_quit)

    # Main-thread pump — GIL released inside main_step(wait=True)
    while not quit_event.is_set():
        core.main_step(wait=True)

    # Cleanup — cancel the main task so CancelledError unwinds cleanly
    task = task_holder.get("task")
    if task and not task.done():
        _asyncio_loop.call_soon_threadsafe(task.cancel)
    thread.join(timeout=5.0)

    for w in list(_live_windows):
        w.destroy()
    _live_windows.clear()

    core._set_asyncio_loop(None)
    _asyncio_loop = None
    core.uninit()
