"""Convert subtitles between formats or to plain text."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from sub_tool.ass_export import parse_ass_to_lrc, parse_ass_to_txt
from sub_tool.ass_to_srt import parse_ass_content
from sub_tool.errors import SubToolError
from sub_tool.io import read_text, write_text
from sub_tool.lrc_to_srt import parse_lrc_content
from sub_tool.lrc_to_txt import parse_lrc_to_txt
from sub_tool.outputs import resolve_output_path
from sub_tool.srt_to_lrc import parse_srt_to_lrc
from sub_tool.srt_to_txt import clean_srt_content
from sub_tool.subtitles import (
    ASS_SUFFIX,
    ASS_SUFFIXES,
    LRC_SUFFIX,
    LRC_SUFFIXES,
    SRT_SUFFIX,
    SRT_SUFFIXES,
)

TXT_SUFFIX = ".txt"

COMMAND = "convert"

TARGET_SUFFIX: dict[str, str] = {
    "srt": SRT_SUFFIX,
    "txt": TXT_SUFFIX,
    "lrc": LRC_SUFFIX,
}

# Which source extensions may appear in a directory scan for each --to target.
SOURCE_SUFFIXES_BY_TARGET: dict[str, frozenset[str]] = {
    "srt": ASS_SUFFIXES | LRC_SUFFIXES,
    "txt": SRT_SUFFIXES | ASS_SUFFIXES | LRC_SUFFIXES,
    "lrc": SRT_SUFFIXES | ASS_SUFFIXES,
}

_SUFFIX_TO_FORMAT: dict[str, str] = {
    SRT_SUFFIX: "srt",
    ASS_SUFFIX: "ass",
    LRC_SUFFIX: "lrc",
    TXT_SUFFIX: "txt",
}


def resolve_target(to: str) -> str:
    """Normalize ``--to`` to a supported target format key."""
    key = to.strip().lower().lstrip(".")
    if not key:
        raise SubToolError("--to must be a non-empty format (srt, txt, or lrc)")
    if key == "ass":
        raise SubToolError(
            "convert --to ass is not supported; use ASS only as a source format"
        )
    if key not in TARGET_SUFFIX:
        allowed = ", ".join(sorted(TARGET_SUFFIX))
        raise SubToolError(f"unsupported --to {to!r}; supported: {allowed}")
    return key


def source_suffixes_for_target(to: str) -> frozenset[str]:
    """Source file suffixes to scan when converting to ``to``."""
    target = resolve_target(to)
    return SOURCE_SUFFIXES_BY_TARGET[target]


def _source_format(path: Path) -> str:
    ext = path.suffix.lower()
    fmt = _SUFFIX_TO_FORMAT.get(ext)
    if fmt is None:
        raise SubToolError(f"not a supported subtitle file: {path}")
    return fmt


def convert_path_for(
    source: Path,
    *,
    to: str,
    input_path: Path,
    output_dir: Path | None,
) -> Path:
    target = resolve_target(to)
    return resolve_output_path(
        source,
        input_path=input_path,
        output_dir=output_dir,
        command=COMMAND,
        suffix=TARGET_SUFFIX[target],
        keep_command_in_default=False,
    )


_CONVERTERS: dict[tuple[str, str], Callable[[str], str]] = {
    ("ass", "srt"): parse_ass_content,
    ("ass", "txt"): parse_ass_to_txt,
    ("ass", "lrc"): parse_ass_to_lrc,
    ("srt", "txt"): clean_srt_content,
    ("srt", "lrc"): parse_srt_to_lrc,
    ("lrc", "srt"): parse_lrc_content,
    ("lrc", "txt"): parse_lrc_to_txt,
}


def generate_convert(
    source: Path,
    *,
    to: str,
    input_path: Path,
    output_dir: Path | None,
) -> Path:
    target = resolve_target(to)
    from_fmt = _source_format(source)
    if from_fmt == target:
        raise SubToolError(
            f"source is already {target}; use the format-specific subcommand "
            f"for edits (e.g. sub-tool {target})"
        )

    converter = _CONVERTERS.get((from_fmt, target))
    if converter is None:
        raise SubToolError(
            f"unsupported conversion: {from_fmt} -> {target} (not implemented yet)"
        )

    content = read_text(source)
    out_content = converter(content)
    out_path = convert_path_for(
        source,
        to=target,
        input_path=input_path,
        output_dir=output_dir,
    )
    write_text(out_path, out_content)
    return out_path
