"""Parse and format SRT / LRC timestamps."""

from __future__ import annotations

import re

_SRT_TS = re.compile(
    r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})",
)
_SRT_RANGE = re.compile(
    r"(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,.]\d{3})",
)
_LRC_TAG = re.compile(
    r"^\[(\d{1,2}):(\d{2})(?:[.:](\d{2,3}))?\]",
)
_LRC_TAG_HMS = re.compile(
    r"^\[(\d{1,2}):(\d{2}):(\d{2})(?:[.,](\d{2,3}))?\]",
)
_LRC_METADATA = re.compile(r"^\[[a-zA-Z]+:", re.IGNORECASE)


def srt_timestamp_to_ms(timestamp: str) -> int:
    match = _SRT_TS.search(timestamp.strip())
    if not match:
        return 0
    h, m, s, ms = (int(match.group(i)) for i in range(1, 5))
    return ((h * 60 + m) * 60 + s) * 1000 + ms


def ms_to_srt_timestamp(ms: int) -> str:
    if ms < 0:
        ms = 0
    total_ms = ms
    ms_part = total_ms % 1000
    total_sec = total_ms // 1000
    s = total_sec % 60
    total_min = total_sec // 60
    m = total_min % 60
    h = total_min // 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms_part:03d}"


def parse_srt_range(time_line: str) -> tuple[int, int]:
    match = _SRT_RANGE.search(time_line.strip())
    if not match:
        return 0, 0
    start = srt_timestamp_to_ms(match.group(1))
    end = srt_timestamp_to_ms(match.group(2))
    return start, end


def format_srt_range(start_ms: int, end_ms: int) -> str:
    if end_ms < start_ms:
        end_ms = start_ms
    return f"{ms_to_srt_timestamp(start_ms)} --> {ms_to_srt_timestamp(end_ms)}"


def srt_start_to_lrc_tag(start_srt: str) -> str:
    ms = srt_timestamp_to_ms(start_srt)
    total_cs = ms // 10
    cs = total_cs % 100
    total_sec = total_cs // 100
    s = total_sec % 60
    total_min = total_sec // 60
    return f"[{total_min:02d}:{s:02d}.{cs:02d}]"


def lrc_tag_to_ms(line: str) -> int | None:
    stripped = line.lstrip("\ufeff").strip()
    match_hms = _LRC_TAG_HMS.match(stripped)
    if match_hms:
        h = int(match_hms.group(1))
        m = int(match_hms.group(2))
        s = int(match_hms.group(3))
        frac = match_hms.group(4) or "0"
        ms = _fraction_to_ms(frac)
        return ((h * 60 + m) * 60 + s) * 1000 + ms

    match = _LRC_TAG.match(stripped)
    if not match:
        return None
    m = int(match.group(1))
    s = int(match.group(2))
    frac = match.group(3) or "0"
    ms = _fraction_to_ms(frac)
    return (m * 60 + s) * 1000 + ms


def _fraction_to_ms(frac: str) -> int:
    if len(frac) == 2:
        return int(frac) * 10
    if len(frac) == 3:
        return int(frac)
    return int(frac[:3].ljust(3, "0"))


def is_lrc_metadata_line(line: str) -> bool:
    return bool(_LRC_METADATA.match(line.strip()))
