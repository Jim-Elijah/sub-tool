"""Convert SRT subtitle content to LRC."""

from __future__ import annotations

from sub_tool.lrc_text import cue_text_to_lrc_line
from sub_tool.srt_edit import parse_srt_content
from sub_tool.timestamp import (
    ms_to_srt_timestamp,
    parse_srt_range,
    srt_start_to_lrc_tag,
)


def parse_srt_to_lrc(content: str) -> str:
    blocks = parse_srt_content(content)
    lrc_lines: list[str] = []
    for time_line, text_lines in blocks:
        body = cue_text_to_lrc_line(text_lines)
        if not body:
            continue
        start_ms, _end_ms = parse_srt_range(time_line)
        tag = srt_start_to_lrc_tag(ms_to_srt_timestamp(start_ms))
        lrc_lines.append(f"{tag}{body}")
    return "\n".join(lrc_lines) + ("\n" if lrc_lines else "")
