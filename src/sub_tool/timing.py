"""Timing helpers for CLI progress logs (stderr)."""

from __future__ import annotations


def format_duration(seconds: float) -> str:
    """Human-readable duration for step logs."""
    if seconds < 0.01:
        return f"{seconds * 1000:.1f}ms"
    return f"{seconds:.2f}s"
