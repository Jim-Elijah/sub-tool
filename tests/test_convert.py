"""Tests for subtitle conversion."""

from __future__ import annotations

from pathlib import Path

import pytest

from sub_tool.convert import (
    generate_convert,
    resolve_target,
    source_suffixes_for_target,
)
from sub_tool.errors import SubToolError


def test_resolve_target_normalizes() -> None:
    assert resolve_target("SRT") == "srt"
    assert resolve_target(".txt") == "txt"


def test_resolve_target_rejects_unknown() -> None:
    with pytest.raises(SubToolError, match="unsupported"):
        resolve_target("vtt")


def test_convert_to_ass_rejected() -> None:
    with pytest.raises(SubToolError, match="not supported"):
        resolve_target("ass")


def test_source_suffixes_for_lrc() -> None:
    suffixes = source_suffixes_for_target("lrc")
    assert ".srt" in suffixes
    assert ".ass" in suffixes


def test_ass_to_srt(tmp_path: Path) -> None:
    ass = tmp_path / "demo.ass"
    ass.write_text(
        "[Events]\nFormat: Start, End, Text\nDialogue: 0:00:00.00,0:00:01.00,Hi\n",
        encoding="utf-8",
    )
    out = generate_convert(ass, to="srt", input_path=ass, output_dir=None)
    assert out == (tmp_path / "demo.srt").resolve()
    assert "Hi" in out.read_text(encoding="utf-8")


def test_srt_to_txt(tmp_path: Path) -> None:
    srt = tmp_path / "demo.srt"
    srt.write_text(
        "1\n00:00:01,000 --> 00:00:02,000\nHello\n",
        encoding="utf-8",
    )
    out = generate_convert(srt, to="txt", input_path=srt, output_dir=None)
    assert out.read_text(encoding="utf-8") == "Hello"


def test_same_format_rejected(tmp_path: Path) -> None:
    srt = tmp_path / "demo.srt"
    srt.write_text("1\n", encoding="utf-8")
    with pytest.raises(SubToolError, match="already srt"):
        generate_convert(srt, to="srt", input_path=srt, output_dir=None)


def test_srt_to_lrc(tmp_path: Path) -> None:
    srt = tmp_path / "demo.srt"
    srt.write_text(
        "1\n00:00:10,000 --> 00:00:13,500\nHello\nWorld\n",
        encoding="utf-8",
    )
    out = generate_convert(srt, to="lrc", input_path=srt, output_dir=None)
    assert out.suffix == ".lrc"
    assert "Hello | World" in out.read_text(encoding="utf-8")


def test_lrc_to_srt(tmp_path: Path) -> None:
    lrc = tmp_path / "demo.lrc"
    lrc.write_text("[00:10.00]Only cue\n", encoding="utf-8")
    out = generate_convert(lrc, to="srt", input_path=lrc, output_dir=None)
    assert "00:00:13,000" in out.read_text(encoding="utf-8")
    assert "Only cue" in out.read_text(encoding="utf-8")


def test_lrc_to_srt_custom_last_ms(tmp_path: Path) -> None:
    lrc = tmp_path / "demo.lrc"
    lrc.write_text("[00:10.00]Only cue\n", encoding="utf-8")
    out = generate_convert(
        lrc,
        to="srt",
        input_path=lrc,
        output_dir=None,
        lrc_last_ms=5000,
    )
    assert "00:00:15,000" in out.read_text(encoding="utf-8")
