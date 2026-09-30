"""Tests for ASS export to LRC and txt."""

from __future__ import annotations

from sub_tool.ass_export import parse_ass_to_lrc, parse_ass_to_txt


def test_ass_to_txt() -> None:
    ass = """[Events]
Format: Start, End, Text
Dialogue: 0:00:01.00,0:00:02.00,Line one\\NLine two
"""
    assert parse_ass_to_txt(ass) == "Line one\nLine two"


def test_ass_to_lrc() -> None:
    ass = """[Events]
Format: Start, End, Text
Dialogue: 0:00:10.00,0:00:13.00,Hello\\NWorld
"""
    lrc = parse_ass_to_lrc(ass)
    assert lrc.startswith("[00:10.00]")
    assert "Hello | World" in lrc
