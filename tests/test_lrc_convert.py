"""Tests for LRC conversion."""

from __future__ import annotations

from sub_tool.lrc_to_srt import parse_lrc_content
from sub_tool.lrc_to_txt import parse_lrc_to_txt
from sub_tool.srt_to_lrc import parse_srt_to_lrc


def test_srt_bilingual_to_lrc() -> None:
    srt = (
        "1\n00:00:10,000 --> 00:00:13,500\n"
        "Hello, world!\n"
        "Translation here\n"
    )
    lrc = parse_srt_to_lrc(srt)
    assert lrc == "[00:10.00]Hello, world! | Translation here\n"


def test_lrc_to_srt_end_from_next_line() -> None:
    lrc = "[00:10.00]First line\n[00:14.00]Second line\n"
    srt = parse_lrc_content(lrc)
    assert "00:00:10,000 --> 00:00:13,999" in srt
    assert "First line" in srt
    assert "Second line" in srt


def test_lrc_to_txt() -> None:
    lrc = "[ar:Artist]\n[00:10.00]Lyric one\n[00:14.00]Lyric two\n"
    assert parse_lrc_to_txt(lrc) == "Lyric one\nLyric two"
