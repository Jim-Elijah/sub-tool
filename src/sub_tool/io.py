"""Text file I/O helpers."""

from __future__ import annotations

from pathlib import Path


def read_text(path: Path) -> str:
    """Read a subtitle file, trying common encodings."""
    encodings = ["utf-8-sig", "utf-16", "utf-16-le", "utf-16-be", "gb18030", "utf-8"]
    for enc in encodings:
        try:
            return path.read_text(encoding=enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return path.read_text(encoding="utf-8", errors="ignore")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
