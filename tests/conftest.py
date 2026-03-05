"""Shared fixtures for ui tests."""

import pytest
from libui import core


@pytest.fixture(autouse=True)
def ui_init_teardown():
    """Initialise and tear down libui for each test."""
    core.init()
    core.main_steps()
    yield
    core.uninit()


def flush_main(n=10):
    """Drain queued main-thread work (for tests that use queue_main)."""
    for _ in range(n):
        core.main_step(wait=False)
