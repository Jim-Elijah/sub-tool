"""Tests for ASS to SRT conversion."""

from __future__ import annotations

from sub_tool.ass_to_srt import parse_ass_content


def test_parse_minimal_ass() -> None:
    ass = """[Script Info]

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:01.00,0:00:02.00,Default,,0,0,0,,Hello
Dialogue: 0,0:00:03.00,0:00:04.50,Default,,0,0,0,,Line one\\NLine two
"""
    srt = parse_ass_content(ass)
    assert "00:00:01,000 --> 00:00:02,000" in srt
    assert "Hello" in srt
    assert "Line one\nLine two" in srt
    assert srt.strip().split("\n\n")[0].startswith("1\n")
