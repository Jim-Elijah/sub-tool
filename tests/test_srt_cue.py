"""Tests for SRT cue format helpers."""

from __future__ import annotations

from sub_tool.srt_cue import (
    cue_is_bilingual,
    cue_is_translator_note,
    swap_cue_text_lines,
)
from sub_tool.srt_edit import process_srt_content


def test_plain_bilingual_two_lines() -> None:
    lines = ["Oh, my God.", "上帝啊"]
    assert cue_is_bilingual(lines)
    assert not cue_is_translator_note(lines)
    swapped = swap_cue_text_lines(lines)
    assert swapped == ["上帝啊", "Oh, my God."]


def test_speaker_single_line_pipe() -> None:
    line = "[SPEAKER_01]: You're late when I say you're late. | 我说你迟了就是迟了"
    assert cue_is_bilingual([line])
    assert not cue_is_translator_note([line])
    swapped = swap_cue_text_lines([line])
    assert swapped[0] == (
        "[SPEAKER_01]: 我说你迟了就是迟了 | You're late when I say you're late."
    )


def test_speaker_two_lines_same_id() -> None:
    lines = [
        "[SPEAKER_03]: Well, quite right, too.",
        "[SPEAKER_03]: 说得没错",
    ]
    assert cue_is_bilingual(lines)
    swapped = swap_cue_text_lines(lines)
    assert swapped[0].startswith("[SPEAKER_03]: 说得没错")


def test_multi_speaker_per_line_pipe() -> None:
    lines = [
        "[SPEAKER_01]: - Where have you been? | 你上哪儿去了",
        "[SPEAKER_02]: - I'm not late, am I? | 我没迟到吧",
    ]
    assert cue_is_bilingual(lines)
    swapped = swap_cue_text_lines(lines)
    assert swapped[0] == "[SPEAKER_01]: - 你上哪儿去了 | Where have you been?"


def test_multi_speaker_stacked_halves() -> None:
    lines = [
        "[SPEAKER_01]: - Where have you been?",
        "[SPEAKER_02]: - I'm not late, am I?",
        "[SPEAKER_01]: - 你上哪儿去了",
        "[SPEAKER_02]: - 我没迟到吧",
    ]
    assert cue_is_bilingual(lines)
    swapped = swap_cue_text_lines(lines)
    assert swapped[0].endswith("你上哪儿去了")
    assert swapped[2].endswith("Where have you been?")


def test_monolingual_two_speakers_not_bilingual() -> None:
    lines = [
        "[SPEAKER_01]: - Where have you been?",
        "[SPEAKER_02]: - I'm not late, am I?",
    ]
    assert not cue_is_bilingual(lines)


def test_drop_notes_keeps_pipe_line() -> None:
    srt = """1
00:00:01,000 --> 00:00:02,000
Hello | 你好

2
00:00:02,000 --> 00:00:03,000
note only

3
00:00:03,000 --> 00:00:04,000
World
世界
"""
    out = process_srt_content(srt, swap=False, drop_notes=True)
    assert "Hello | 你好" in out
    assert "note only" not in out
    assert "World\n世界" in out


def test_drop_notes_keeps_speaker_monologue() -> None:
    srt = """1
00:00:01,000 --> 00:00:02,000
Hello
你好

2
00:00:02,000 --> 00:00:03,000
[SPEAKER_01]: stage direction only

3
00:00:03,000 --> 00:00:04,000
World
世界
"""
    out = process_srt_content(srt, swap=False, drop_notes=True)
    assert "[SPEAKER_01]: stage direction only" in out
