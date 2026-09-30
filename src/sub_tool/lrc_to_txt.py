"""Extract plain text from LRC subtitle content."""

from __future__ import annotations

from sub_tool.timestamp import is_lrc_metadata_line, lrc_tag_to_ms


def parse_lrc_to_txt(content: str) -> str:
    if content.startswith("\ufeff"):
        content = content[1:]

    content = content.replace("\r\n", "\n").replace("\r", "\n")
    text_lines: list[str] = []

    for raw in content.split("\n"):
        line = raw.strip()
        if not line or is_lrc_metadata_line(line):
            continue
        if lrc_tag_to_ms(line) is not None:
            close = line.find("]")
            text = line[close + 1 :].strip() if close != -1 else ""
            if text:
                text_lines.append(text)
            continue
        if text_lines:
            text_lines[-1] = f"{text_lines[-1]} {line}".strip()
        else:
            text_lines.append(line)

    return "\n".join(text_lines)
