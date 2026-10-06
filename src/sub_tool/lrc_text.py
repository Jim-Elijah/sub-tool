"""Join cue text lines for single-line LRC export."""

from __future__ import annotations

from sub_tool.srt_cue import BILINGUAL_PIPE, is_plain_bilingual_two_lines


def cue_text_to_lrc_line(text_lines: list[str]) -> str:
    lines = [line.strip() for line in text_lines if line.strip()]
    if not lines:
        return ""
    if is_plain_bilingual_two_lines(lines):
        return f"{lines[0]}{BILINGUAL_PIPE}{lines[1]}"
    return " ".join(lines)
