"""Tests for shared output path resolution."""

from __future__ import annotations

from pathlib import Path

import pytest

from sub_tool.errors import SubToolError
from sub_tool.outputs import resolve_output_path


def test_default_without_command_in_name(tmp_path: Path) -> None:
    source = tmp_path / "clip.srt"
    source.write_text("x", encoding="utf-8")
    assert (
        resolve_output_path(
            source,
            input_path=source,
            output_dir=None,
            command="convert",
            suffix=".txt",
            keep_command_in_default=False,
        )
        == (tmp_path / "clip.txt").resolve()
    )


def test_output_other_dir_keeps_stem(tmp_path: Path) -> None:
    source = tmp_path / "clip.srt"
    source.write_text("x", encoding="utf-8")
    out = tmp_path / "out"
    out.mkdir()
    assert (
        resolve_output_path(
            source,
            input_path=source,
            output_dir=out,
            command="convert",
            suffix=".srt",
            keep_command_in_default=False,
        )
        == (out / "clip.srt").resolve()
    )


def test_output_same_as_input_dir_uses_command(tmp_path: Path) -> None:
    source = tmp_path / "clip.ass"
    source.write_text("x", encoding="utf-8")
    assert (
        resolve_output_path(
            source,
            input_path=tmp_path,
            output_dir=tmp_path,
            command="convert",
            suffix=".srt",
            keep_command_in_default=False,
        )
        == (tmp_path / "clip.convert.srt").resolve()
    )


def test_output_must_be_existing_directory(tmp_path: Path) -> None:
    source = tmp_path / "clip.srt"
    source.write_text("x", encoding="utf-8")
    missing = tmp_path / "missing"
    with pytest.raises(SubToolError, match="not found"):
        resolve_output_path(
            source,
            input_path=source,
            output_dir=missing,
            command="convert",
            suffix=".txt",
            keep_command_in_default=False,
        )
