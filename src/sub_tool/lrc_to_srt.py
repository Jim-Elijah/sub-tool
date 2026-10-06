"""Convert LRC subtitle content to SRT."""

from __future__ import annotations

from sub_tool.timestamp import format_srt_range, is_lrc_metadata_line, lrc_tag_to_ms

DEFAULT_LAST_CUE_MS = 3000
_MIN_CUE_MS = 500


def parse_lrc_entries(content: str) -> list[tuple[int, str]]:
    if content.startswith("\ufeff"):
        content = content[1:]

    content = content.replace("\r\n", "\n").replace("\r", "\n")
    entries: list[tuple[int, str]] = []

    for raw in content.split("\n"):
        line = raw.strip()
        if not line or is_lrc_metadata_line(line):
            continue

        start_ms = lrc_tag_to_ms(line)
        if start_ms is not None:
            close = line.find("]")
            text = line[close + 1 :].strip() if close != -1 else ""
            entries.append((start_ms, text))
            continue

        if entries:
            prev_ms, prev_text = entries[-1]
            joined = f"{prev_text} {line}".strip() if prev_text else line
            entries[-1] = (prev_ms, joined)

    return entries


def lrc_end_ms_for_index(
    entries: list[tuple[int, str]],
    index: int,
    *,
    last_cue_ms: int,
) -> int:
    start_ms = entries[index][0]
    if index + 1 < len(entries):
        return max(start_ms + _MIN_CUE_MS, entries[index + 1][0] - 1)
    return start_ms + last_cue_ms


def parse_lrc_content(content: str, *, last_cue_ms: int = DEFAULT_LAST_CUE_MS) -> str:
    entries = parse_lrc_entries(content)
    if not entries:
        return ""

    srt_blocks: list[str] = []
    for i, (start_ms, text) in enumerate(entries):
        end_ms = lrc_end_ms_for_index(entries, i, last_cue_ms=last_cue_ms)
        time_line = format_srt_range(start_ms, end_ms)
        srt_blocks.append(f"{i + 1}\n{time_line}\n{text}")

    return "\n\n".join(srt_blocks) + "\n"
