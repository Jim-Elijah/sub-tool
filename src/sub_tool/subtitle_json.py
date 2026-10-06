"""Export subtitles to a structured JSON document."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from sub_tool.ass_to_srt import parse_ass_dialogues
from sub_tool.lrc_to_srt import lrc_end_ms_for_index, parse_lrc_entries
from sub_tool.srt_edit import parse_srt_content
from sub_tool.timestamp import ms_to_srt_timestamp, parse_srt_range, srt_timestamp_to_ms

FORMAT_ID = "sub-tool-subtitles"
FORMAT_VERSION = 1


@dataclass(frozen=True)
class SubtitleCue:
    index: int
    start_ms: int
    end_ms: int
    lines: list[str]

    def to_json_dict(self) -> dict[str, object]:
        return {
            "index": self.index,
            "start_ms": self.start_ms,
            "end_ms": self.end_ms,
            "start": ms_to_srt_timestamp(self.start_ms),
            "end": ms_to_srt_timestamp(self.end_ms),
            "lines": list(self.lines),
        }


def cues_from_srt(content: str) -> list[SubtitleCue]:
    blocks = parse_srt_content(content)
    cues: list[SubtitleCue] = []
    for i, (time_line, text_lines) in enumerate(blocks, 1):
        start_ms, end_ms = parse_srt_range(time_line)
        cues.append(SubtitleCue(i, start_ms, end_ms, list(text_lines)))
    return cues


def cues_from_ass(content: str) -> list[SubtitleCue]:
    dialogues = parse_ass_dialogues(content)
    cues: list[SubtitleCue] = []
    for i, (start_srt, end_srt, text) in enumerate(dialogues, 1):
        start_ms = srt_timestamp_to_ms(start_srt)
        end_ms = srt_timestamp_to_ms(end_srt)
        lines = text.split("\n") if text else []
        cues.append(SubtitleCue(i, start_ms, end_ms, lines))
    return cues


def cues_from_lrc(content: str, *, last_cue_ms: int) -> list[SubtitleCue]:
    entries = parse_lrc_entries(content)
    cues: list[SubtitleCue] = []
    for i, (start_ms, text) in enumerate(entries):
        end_ms = lrc_end_ms_for_index(entries, i, last_cue_ms=last_cue_ms)
        lines = [text] if text else []
        cues.append(SubtitleCue(i + 1, start_ms, end_ms, lines))
    return cues


def cues_to_document(
    cues: list[SubtitleCue],
    *,
    source_kind: str,
    source_path: Path | None = None,
    timing_note: str | None = None,
) -> dict[str, object]:
    doc: dict[str, object] = {
        "format": FORMAT_ID,
        "version": FORMAT_VERSION,
        "source": {"kind": source_kind},
        "cues": [cue.to_json_dict() for cue in cues],
    }
    if source_path is not None:
        cast_source = doc["source"]
        assert isinstance(cast_source, dict)
        cast_source["path"] = source_path.name
    if timing_note is not None:
        doc["timing"] = timing_note
    return doc


def serialize_document(doc: dict[str, object]) -> str:
    return json.dumps(doc, ensure_ascii=False, indent=2) + "\n"


def parse_srt_to_json(content: str) -> str:
    doc = cues_to_document(cues_from_srt(content), source_kind="srt")
    return serialize_document(doc)


def parse_ass_to_json(content: str) -> str:
    doc = cues_to_document(cues_from_ass(content), source_kind="ass")
    return serialize_document(doc)


def parse_lrc_to_json(content: str, *, last_cue_ms: int) -> str:
    doc = cues_to_document(
        cues_from_lrc(content, last_cue_ms=last_cue_ms),
        source_kind="lrc",
        timing_note="inferred",
    )
    return serialize_document(doc)
