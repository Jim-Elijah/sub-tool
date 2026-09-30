"""Join cue text lines for single-line LRC export."""

from __future__ import annotations


def cue_text_to_lrc_line(text_lines: list[str]) -> str:
    lines = [line.strip() for line in text_lines if line.strip()]
    if not lines:
        return ""
    if (
        len(lines) == 2
        and not lines[0].startswith("-")
        and not lines[1].startswith("-")
    ):
        return f"{lines[0]} | {lines[1]}"
    return " ".join(lines)
