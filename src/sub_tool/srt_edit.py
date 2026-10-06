"""Re-number and optionally swap bilingual lines in SRT files."""

from __future__ import annotations

import re
from pathlib import Path

from sub_tool.errors import SubToolError
from sub_tool.io import read_text, write_text
from sub_tool.outputs import resolve_output_path
from sub_tool.srt_cue import (
    cue_is_bilingual,
    cue_is_translator_note,
    swap_cue_text_lines,
)
from sub_tool.timestamp import format_srt_range, parse_srt_range

COMMAND = "srt"
COMMAND_SWAP = "srt-swap"
OUTPUT_SUFFIX = ".srt"

SrtBlock = tuple[str, list[str]]


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


def parse_srt_content(content: str) -> list[SrtBlock]:
    if content.startswith("\ufeff"):
        content = content[1:]

    content = content.replace("\r\n", "\n").replace("\r", "\n")
    timestamp_re = re.compile(
        r"\d{2}:\d{2}:\d{2}[,.]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[,.]\d{3}"
    )

    raw_blocks = re.split(r"\n\s*\n", content)
    blocks: list[SrtBlock] = []

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


def is_bilingual_srt(blocks: list[SrtBlock]) -> bool:
    """True when a strict majority of cues match project bilingual conventions."""
    if not blocks:
        return False
    bilingual = sum(1 for _, lines in blocks if cue_is_bilingual(lines))
    return bilingual > len(blocks) / 2


def process_srt_content(
    content: str,
    *,
    swap: bool,
    shift_ms: int = 0,
    drop_notes: bool = False,
) -> str:
    blocks = parse_srt_content(content)

    if drop_notes:
        if not is_bilingual_srt(blocks):
            raise SubToolError(
                "--drop-notes requires a bilingual SRT "
                "(most cues must match bilingual conventions; see docs/srt-format.md)"
            )
        blocks = [
            (time_str, lines)
            for time_str, lines in blocks
            if not cue_is_translator_note(lines)
        ]

    output_blocks: list[str] = []

    for i, (time_str, text_lines) in enumerate(blocks, 1):
        if swap:
            text_lines = swap_cue_text_lines(text_lines)

        if shift_ms:
            start_ms, end_ms = parse_srt_range(time_str)
            start_ms += shift_ms
            end_ms += shift_ms
            time_str = format_srt_range(start_ms, end_ms)

        text_str = "\n".join(text_lines)
        output_blocks.append(f"{i}\n{time_str}\n{text_str}")

    return "\n\n".join(output_blocks) + ("\n" if output_blocks else "")


def generate_srt_edit(
    srt_file: Path,
    *,
    input_path: Path,
    output_dir: Path | None,
    swap: bool,
    shift_ms: int = 0,
    drop_notes: bool = False,
) -> Path:
    content = read_text(srt_file)
    new_content = process_srt_content(
        content,
        swap=swap,
        shift_ms=shift_ms,
        drop_notes=drop_notes,
    )
    out_path = srt_output_path_for(
        srt_file,
        input_path=input_path,
        output_dir=output_dir,
        swap=swap,
    )
    write_text(out_path, new_content)
    return out_path
