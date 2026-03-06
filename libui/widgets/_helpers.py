"""Shared helpers for declarative widget nodes."""

from __future__ import annotations

from libui.state import Computed, State


def _resolve(val):
    """Return the plain value from a State/Computed or pass through."""
    if isinstance(val, (State, Computed)):
        return val.value
    return val
