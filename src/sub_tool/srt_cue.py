"""SRT cue conventions (bilingual, speaker tags, translator notes)."""

from __future__ import annotations

import re

SPEAKER_TAG_RE = re.compile(r"\[SPEAKER_\d+\]", re.IGNORECASE)
BILINGUAL_PIPE = " | "


def speaker_ids_in_line(line: str) -> list[str]:
    return SPEAKER_TAG_RE.findall(line)


def line_has_bilingual_pipe(line: str) -> bool:
    return BILINGUAL_PIPE in line


def is_plain_bilingual_two_lines(lines: list[str]) -> bool:
    if len(lines) != 2:
        return False
    return (
        not lines[0].startswith("-")
        and not lines[1].startswith("-")
        and not SPEAKER_TAG_RE.search(lines[0])
        and not SPEAKER_TAG_RE.search(lines[1])
    )


def try_swap_speaker_halves(lines: list[str]) -> list[str] | None:
    n = len(lines)
    if n < 2 or n % 2 != 0:
        return None
    half = n // 2
    first = [tuple(speaker_ids_in_line(line)) for line in lines[:half]]
    second = [tuple(speaker_ids_in_line(line)) for line in lines[half:]]
    if not all(first) or not all(second):
        return None
    if first != second:
        return None
    return lines[half:] + lines[:half]


def cue_is_bilingual(text_lines: list[str]) -> bool:
    lines = [line.strip() for line in text_lines if line.strip()]
    if not lines:
        return False
    if len(lines) == 1:
        return line_has_bilingual_pipe(lines[0])
    if any(line_has_bilingual_pipe(line) for line in lines):
        return True
    if is_plain_bilingual_two_lines(lines):
        return True
    if len(lines) == 2:
        ids0 = speaker_ids_in_line(lines[0])
        ids1 = speaker_ids_in_line(lines[1])
        if len(ids0) == 1 and ids0 == ids1:
            return True
    return try_swap_speaker_halves(lines) is not None


def cue_is_translator_note(text_lines: list[str]) -> bool:
    lines = [line.strip() for line in text_lines if line.strip()]
    if len(lines) != 1:
        return False
    line = lines[0]
    if line_has_bilingual_pipe(line):
        return False
    return not SPEAKER_TAG_RE.search(line)


def _swap_pipe_in_body(body: str) -> str:
    idx = body.find(BILINGUAL_PIPE)
    if idx == -1:
        return body
    left = body[:idx].strip()
    right = body[idx + len(BILINGUAL_PIPE) :].strip()
    if BILINGUAL_PIPE in right:
        return body
    return right + BILINGUAL_PIPE + left


def swap_bilingual_pipe_in_line(line: str) -> str:
    if BILINGUAL_PIPE not in line:
        return line
    if line.count(BILINGUAL_PIPE) > 1 and " - " in line:
        segments = line.split(" - ")
        swapped = [
            (
                swap_bilingual_pipe_in_line(segment)
                if BILINGUAL_PIPE in segment
                else segment
            )
            for segment in segments
        ]
        return " - ".join(swapped)

    prefix_match = re.match(r"^(\[SPEAKER_\d+\]:\s*)", line, re.IGNORECASE)
    if prefix_match:
        prefix = prefix_match.group(1)
        rest = line[len(prefix) :]
        dash = ""
        if rest.startswith("- "):
            dash = "- "
            rest = rest[2:]
        return prefix + dash + _swap_pipe_in_body(rest)

    return _swap_pipe_in_body(line)


def swap_cue_text_lines(text_lines: list[str]) -> list[str]:
    lines = list(text_lines)
    if not lines:
        return lines

    swapped_halves = try_swap_speaker_halves(lines)
    if swapped_halves is not None:
        return swapped_halves

    if len(lines) == 1:
        if line_has_bilingual_pipe(lines[0]):
            return [swap_bilingual_pipe_in_line(lines[0])]
        return lines

    if is_plain_bilingual_two_lines(lines):
        return list(reversed(lines))

    if len(lines) == 2:
        ids0 = speaker_ids_in_line(lines[0])
        ids1 = speaker_ids_in_line(lines[1])
        if len(ids0) == 1 and ids0 == ids1:
            return list(reversed(lines))

    if any(line_has_bilingual_pipe(line) for line in lines):
        return [
            swap_bilingual_pipe_in_line(line) if line_has_bilingual_pipe(line) else line
            for line in lines
        ]

    if len(lines) >= 2:
        return list(reversed(lines))
    return lines
