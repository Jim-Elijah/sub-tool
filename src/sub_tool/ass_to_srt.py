"""Convert ASS subtitles to SRT."""

from __future__ import annotations

import re


def convert_ass_time_to_srt(ass_time: str) -> str:
    """Convert ASS time (H:MM:SS.cc) to SRT (HH:MM:SS,mmm)."""
    ass_time = ass_time.strip()
    if not ass_time:
        return "00:00:00,000"

    ass_time = ass_time.replace(",", ".")
    parts = ass_time.split(":")
    if len(parts) != 3:
        return ass_time

    try:
        h = int(parts[0])
        m = int(parts[1])
        s_sec_parts = parts[2].split(".")
        s = int(s_sec_parts[0])
        ms_str = s_sec_parts[1] if len(s_sec_parts) > 1 else "0"

        if len(ms_str) == 1:
            ms = int(ms_str) * 100
        elif len(ms_str) == 2:
            ms = int(ms_str) * 10
        else:
            ms = int(ms_str[:3])
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    except ValueError:
        return "00:00:00,000"


def clean_ass_text(text: str) -> str:
    text = re.sub(r"\{[^}]*\}", "", text)
    text = text.replace(r"\N", "\n").replace(r"\n", "\n")
    text = text.replace(r"\h", " ")
    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def parse_ass_content(content: str) -> str:
    if content.startswith("\ufeff"):
        content = content[1:]

    events_section = False
    start_idx, end_idx, text_idx = 1, 2, 9
    num_cols = 10
    dialogues: list[tuple[str, str, str]] = []

    for line in content.splitlines():
        line_str = line.strip()
        if not line_str:
            continue

        if line_str.startswith("[") and line_str.endswith("]"):
            events_section = line_str.lower() == "[events]"
            continue

        if not events_section:
            continue

        if line_str.startswith("Format:"):
            cols = [c.strip().lower() for c in line_str[len("Format:") :].split(",")]
            num_cols = len(cols)
            if "start" in cols:
                start_idx = cols.index("start")
            if "end" in cols:
                end_idx = cols.index("end")
            if "text" in cols:
                text_idx = cols.index("text")
            continue

        if line_str.startswith("Dialogue:"):
            payload = line_str[len("Dialogue:") :].strip()
            parts = payload.split(",", num_cols - 1)
            if len(parts) > max(start_idx, end_idx, text_idx):
                start_srt = convert_ass_time_to_srt(parts[start_idx])
                end_srt = convert_ass_time_to_srt(parts[end_idx])
                text = clean_ass_text(parts[text_idx])
                if text:
                    dialogues.append((start_srt, end_srt, text))

    dialogues.sort(key=lambda x: (x[0], x[1]))

    srt_blocks = []
    for i, (start, end, text) in enumerate(dialogues, 1):
        srt_blocks.append(f"{i}\n{start} --> {end}\n{text}")

    return "\n\n".join(srt_blocks) + ("\n" if srt_blocks else "")
