"""Tests for SRT to text conversion."""

from __future__ import annotations

from sub_tool.srt_to_txt import clean_srt_content


def test_clean_strips_timestamps() -> None:
    srt = """1
00:00:01,000 --> 00:00:02,000
Hello

2
00:00:03,000 --> 00:00:04,000
World
"""
    assert clean_srt_content(srt) == "Hello\nWorld"
