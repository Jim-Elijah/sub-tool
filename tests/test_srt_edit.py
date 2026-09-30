"""Tests for SRT re-number and swap."""

from __future__ import annotations

from pathlib import Path

from sub_tool.srt_edit import generate_srt_edit, process_srt_content


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


def test_in_place_edit(tmp_path: Path) -> None:
    srt = tmp_path / "demo.srt"
    srt.write_text(
        "5\n00:00:01,000 --> 00:00:02,000\nA\n",
        encoding="utf-8",
    )
    out = generate_srt_edit(srt, input_path=srt, output_dir=None, swap=False)
    assert out == srt.resolve()
    assert out.read_text(encoding="utf-8").startswith("1\n")
