"""User-facing errors for sub-tool."""

from __future__ import annotations


class SubToolError(Exception):
    """Raised for expected failures; the message is safe to print to stderr."""
