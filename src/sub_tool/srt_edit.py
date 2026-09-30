"""Re-number and optionally swap bilingual lines in SRT files."""

from __future__ import annotations

import re
from pathlib import Path

from sub_tool.io import read_text, write_text
from sub_tool.outputs import resolve_output_path

COMMAND = "srt"
COMMAND_SWAP = "srt-swap"
OUTPUT_SUFFIX = ".srt"


def srt_output_path_for(
    srt_file: Path,
    *,
    input_path: Path,
    output_dir: Path | None,
    swap: bool,
) -> Path:
    if output_dir is None:
        return srt_file.expanduser().resolve()

    command = COMMAND_SWAP if swap else COMMAND
    keep_command = swap
    return resolve_output_path(
        srt_file,
        input_path=input_path,
        output_dir=output_dir,
        command=command,
        suffix=OUTPUT_SUFFIX,
        keep_command_in_default=keep_command,
    )


def parse_srt_content(content: str) -> list[tuple[str, list[str]]]:
    if content.startswith("\ufeff"):
        content = content[1:]

    content = content.replace("\r\n", "\n").replace("\r", "\n")
    timestamp_re = re.compile(
        r"\d{2}:\d{2}:\d{2}[,.]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[,.]\d{3}"
    )

    raw_blocks = re.split(r"\n\s*\n", content)
    blocks: list[tuple[str, list[str]]] = []

    for raw in raw_blocks:
        lines = [line.strip() for line in raw.split("\n") if line.strip()]
        if not lines:
            continue

        time_idx = -1
        for idx, line in enumerate(lines):
            if timestamp_re.search(line):
                time_idx = idx
                break

        if time_idx != -1:
            time_line = lines[time_idx]
            text_lines = lines[time_idx + 1 :]
            if text_lines:
                blocks.append((time_line, text_lines))

    return blocks


def process_srt_content(content: str, *, swap: bool) -> str:
    blocks = parse_srt_content(content)
    output_blocks: list[str] = []

    for i, (time_str, text_lines) in enumerate(blocks, 1):
        if swap and len(text_lines) >= 2:
            text_lines = list(reversed(text_lines))

        text_str = "\n".join(text_lines)
        output_blocks.append(f"{i}\n{time_str}\n{text_str}")

    return "\n\n".join(output_blocks) + ("\n" if output_blocks else "")


def generate_srt_edit(
    srt_file: Path,
    *,
    input_path: Path,
    output_dir: Path | None,
    swap: bool,
) -> Path:
    content = read_text(srt_file)
    new_content = process_srt_content(content, swap=swap)
    out_path = srt_output_path_for(
        srt_file,
        input_path=input_path,
        output_dir=output_dir,
        swap=swap,
    )
    write_text(out_path, new_content)
    return out_path
