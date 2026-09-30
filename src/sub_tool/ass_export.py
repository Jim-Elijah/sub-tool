"""Export ASS subtitles to LRC or plain text."""

from __future__ import annotations

from sub_tool.ass_to_srt import parse_ass_dialogues
from sub_tool.lrc_text import cue_text_to_lrc_line
from sub_tool.timestamp import srt_start_to_lrc_tag


def parse_ass_to_txt(content: str) -> str:
    text_lines: list[str] = []
    for _start, _end, text in parse_ass_dialogues(content):
        for line in text.split("\n"):
            stripped = line.strip()
            if stripped:
                text_lines.append(stripped)
    return "\n".join(text_lines)


def parse_ass_to_lrc(content: str) -> str:
    lrc_lines: list[str] = []
    for start, _end, text in parse_ass_dialogues(content):
        body = cue_text_to_lrc_line(text.split("\n"))
        if not body:
            continue
        lrc_lines.append(f"{srt_start_to_lrc_tag(start)}{body}")
    return "\n".join(lrc_lines) + ("\n" if lrc_lines else "")
