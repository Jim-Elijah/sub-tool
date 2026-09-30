"""Tests for subtitle file discovery."""

from __future__ import annotations

from pathlib import Path

import pytest

from sub_tool.errors import SubToolError
from sub_tool.subtitles import ASS_SUFFIXES, SRT_SUFFIXES, resolve_subtitles


def test_single_srt_file(tmp_path: Path) -> None:
    srt = tmp_path / "a.srt"
    srt.write_text("1\n", encoding="utf-8")
    assert resolve_subtitles(srt, None, depth=None, suffixes=SRT_SUFFIXES) == [
        srt.resolve()
    ]


def test_wrong_suffix_rejected(tmp_path: Path) -> None:
    ass = tmp_path / "a.ass"
    ass.write_text("[Events]\n", encoding="utf-8")
    with pytest.raises(SubToolError, match="not a supported"):
        resolve_subtitles(ass, None, depth=None, suffixes=SRT_SUFFIXES)


def test_directory_depth_limit(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    top = tmp_path / "top.srt"
    deep = nested / "deep.srt"
    top.write_text("1\n", encoding="utf-8")
    deep.write_text("1\n", encoding="utf-8")
    assert resolve_subtitles(tmp_path, None, depth=1, suffixes=SRT_SUFFIXES) == [
        top.resolve()
    ]
    assert (
        len(resolve_subtitles(tmp_path, None, depth=None, suffixes=SRT_SUFFIXES)) == 2
    )


def test_include_glob(tmp_path: Path) -> None:
    a = tmp_path / "en.srt"
    b = tmp_path / "zh.srt"
    a.write_text("1\n", encoding="utf-8")
    b.write_text("1\n", encoding="utf-8")
    found = resolve_subtitles(tmp_path, ["en.srt"], depth=None, suffixes=SRT_SUFFIXES)
    assert found == [a.resolve()]


def test_depth_must_be_positive(tmp_path: Path) -> None:
    with pytest.raises(SubToolError, match="--depth"):
        resolve_subtitles(tmp_path, None, depth=0, suffixes=SRT_SUFFIXES)


def test_ass_directory(tmp_path: Path) -> None:
    ass = tmp_path / "x.ass"
    ass.write_text("[Events]\n", encoding="utf-8")
    assert resolve_subtitles(ass, None, depth=None, suffixes=ASS_SUFFIXES) == [
        ass.resolve()
    ]
