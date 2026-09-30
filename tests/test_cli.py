"""Tests for the sub-tool CLI."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from sub_tool.cli import build_parser, main


def test_build_parser_returns_parser() -> None:
    parser = build_parser()
    assert parser.prog == "sub-tool"


def test_main_prints_help(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main([])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "subtitle" in captured.out.lower()
    assert "convert" in captured.out
    assert "srt" in captured.out


def test_version_flag_exits_successfully() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0


def test_convert_to_txt_success(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    srt = tmp_path / "clip.srt"
    srt.write_text("1\n00:00:01,000 --> 00:00:02,000\nHi\n", encoding="utf-8")
    txt = tmp_path / "clip.txt"
    with patch("sub_tool.cli.generate_convert", return_value=txt):
        exit_code = main(["convert", "--to", "txt", str(srt)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert str(txt) in captured.out


def test_missing_path_exits_nonzero(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    missing = tmp_path / "missing.srt"
    exit_code = main(["convert", "--to", "txt", str(missing)])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "path not found" in captured.err
