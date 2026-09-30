"""Extract plain text from SRT subtitle content."""

from __future__ import annotations

import re


def clean_srt_content(srt_content: str) -> str:
    if srt_content.startswith("\ufeff"):
        srt_content = srt_content[1:]

    srt_content = srt_content.replace("\r\n", "\n")
    lines = srt_content.split("\n")
    text_lines: list[str] = []

    timestamp_re = re.compile(
        r"\d{2}:\d{2}:\d{2}[,.]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[,.]\d{3}"
    )

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        if (
            line.isdigit()
            and i + 1 < len(lines)
            and timestamp_re.match(lines[i + 1].strip())
        ):
            i += 2
            continue

        if timestamp_re.match(line):
            i += 1
            continue

        clean_line = re.sub(r"<[^>]+>", "", line)
        if clean_line.strip():
            text_lines.append(clean_line)
        i += 1

    return "\n".join(text_lines)
