"""Tests for JSON subtitle export."""

from __future__ import annotations

import json
from pathlib import Path

from sub_tool.convert import generate_convert
from sub_tool.subtitle_json import parse_lrc_to_json, parse_srt_to_json


def test_srt_to_json_bilingual_lines() -> None:
    srt = "1\n00:00:10,000 --> 00:00:13,500\nHello\nTranslation\n"
    doc = json.loads(parse_srt_to_json(srt))
    assert doc["format"] == "sub-tool-subtitles"
    assert doc["version"] == 1
    assert doc["source"]["kind"] == "srt"
    assert len(doc["cues"]) == 1
    cue = doc["cues"][0]
    assert cue["index"] == 1
    assert cue["start_ms"] == 10_000
    assert cue["end_ms"] == 13_500
    assert cue["lines"] == ["Hello", "Translation"]


def test_lrc_to_json_inferred_timing() -> None:
    lrc = "[00:10.00]Only cue\n"
    doc = json.loads(parse_lrc_to_json(lrc, last_cue_ms=5000))
    assert doc["timing"] == "inferred"
    assert doc["cues"][0]["end_ms"] == 15_000


def test_convert_srt_to_json_file(tmp_path: Path) -> None:
    srt = tmp_path / "demo.srt"
    srt.write_text(
        "1\n00:00:01,000 --> 00:00:02,000\nHi\n",
        encoding="utf-8",
    )
    out = generate_convert(srt, to="json", input_path=srt, output_dir=None)
    assert out.suffix == ".json"
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["cues"][0]["lines"] == ["Hi"]
