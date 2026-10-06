"""Tests for SRT re-number and swap."""

from __future__ import annotations

from pathlib import Path

import pytest

from sub_tool.errors import SubToolError
from sub_tool.srt_edit import generate_srt_edit, is_bilingual_srt, process_srt_content


def test_renumber() -> None:
    srt = """99
00:00:01,000 --> 00:00:02,000
Only line
"""
    out = process_srt_content(srt, swap=False)
    assert out.startswith("1\n")


def test_swap_reverses_lines() -> None:
    srt = """1
00:00:01,000 --> 00:00:02,000
Top
Bottom
"""
    out = process_srt_content(srt, swap=True)
    assert "Bottom\nTop" in out


def test_shift_ms() -> None:
    srt = """1
00:00:01,000 --> 00:00:02,000
Hi
"""
    out = process_srt_content(srt, swap=False, shift_ms=500)
    assert "00:00:01,500 --> 00:00:02,500" in out


def test_in_place_edit(tmp_path: Path) -> None:
    srt = tmp_path / "demo.srt"
    srt.write_text(
        "5\n00:00:01,000 --> 00:00:02,000\nA\n",
        encoding="utf-8",
    )
    out = generate_srt_edit(srt, input_path=srt, output_dir=None, swap=False)
    assert out == srt.resolve()
    assert out.read_text(encoding="utf-8").startswith("1\n")


def test_is_bilingual_srt() -> None:
    bilingual = [
        ("00:00:01,000 --> 00:00:02,000", ["EN", "ZH"]),
        ("00:00:02,000 --> 00:00:03,000", ["note only"]),
        ("00:00:03,000 --> 00:00:04,000", ["EN", "ZH"]),
    ]
    assert is_bilingual_srt(bilingual)

    monolingual = [
        ("00:00:01,000 --> 00:00:02,000", ["only"]),
        ("00:00:02,000 --> 00:00:03,000", ["also only"]),
    ]
    assert not is_bilingual_srt(monolingual)
    assert not is_bilingual_srt([])


def test_drop_notes_removes_single_line_cues() -> None:
    srt = """1
00:00:01,000 --> 00:00:02,000
Hello
你好

2
00:00:02,000 --> 00:00:03,000
补选  指在两个常规选举日之间

3
00:00:03,000 --> 00:00:04,000
World
世界
"""
    out = process_srt_content(srt, swap=False, drop_notes=True)
    assert "补选" not in out
    assert "Hello\n你好" in out
    assert "World\n世界" in out
    assert out.startswith("1\n")
    assert "\n2\n" in out
    assert "\n3\n" not in out


def test_drop_notes_rejects_monolingual() -> None:
    srt = """1
00:00:01,000 --> 00:00:02,000
Only line

2
00:00:02,000 --> 00:00:03,000
Another
"""
    with pytest.raises(SubToolError, match="--drop-notes requires a bilingual"):
        process_srt_content(srt, swap=False, drop_notes=True)
