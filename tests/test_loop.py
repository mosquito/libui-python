"""Tests for the asyncio integration loop."""

from libui import core


def test_main_steps():
    """main_steps + main_step should work without blocking."""
    core.main_steps()
    result = core.main_step(wait=False)
    assert isinstance(result, bool)
