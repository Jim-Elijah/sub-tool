"""Convert LRC subtitle content to SRT."""

from __future__ import annotations

from sub_tool.timestamp import format_srt_range, is_lrc_metadata_line, lrc_tag_to_ms

_DEFAULT_CUE_MS = 3000
_MIN_CUE_MS = 500


def parse_lrc_content(content: str) -> str:
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

    if not entries:
        return ""

    srt_blocks: list[str] = []
    for i, (start_ms, text) in enumerate(entries):
        if i + 1 < len(entries):
            end_ms = max(start_ms + _MIN_CUE_MS, entries[i + 1][0] - 1)
        else:
            end_ms = start_ms + _DEFAULT_CUE_MS
        time_line = format_srt_range(start_ms, end_ms)
        srt_blocks.append(f"{i + 1}\n{time_line}\n{text}")

    return "\n\n".join(srt_blocks) + "\n"
