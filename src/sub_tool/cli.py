"""Command-line entry point for sub-tool."""

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Callable
from pathlib import Path

from sub_tool import __version__
from sub_tool.convert import generate_convert, source_suffixes_for_target
from sub_tool.lrc_to_srt import DEFAULT_LAST_CUE_MS
from sub_tool.errors import SubToolError
from sub_tool.srt_edit import generate_srt_edit
from sub_tool.subtitles import SRT_SUFFIXES, resolve_subtitles
from sub_tool.timing import format_duration


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sub-tool",
        description="A Python toolkit for subtitle conversion and utilities.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command")

    convert = subparsers.add_parser(
        "convert",
        help="Convert subtitle(s) to another format or plain text",
        description=(
            "Convert between subtitle formats or to .txt. Source format is inferred "
            "from the file extension; use --to to choose the target."
        ),
    )
    _add_shared_io_args(convert)
    convert.add_argument(
        "--to",
        required=True,
        metavar="FMT",
        help="Target format: srt, txt, lrc, or json",
    )
    convert.add_argument(
        "--lrc-last-ms",
        type=int,
        default=DEFAULT_LAST_CUE_MS,
        metavar="MS",
        help=(
            "When converting LRC to SRT or JSON, duration in ms for the last cue "
            "(default: 3000)"
        ),
    )

    srt = subparsers.add_parser(
        "srt",
        help="Edit SRT files (re-number, swap bilingual lines)",
        description=(
            "Re-number cues from 1. With --swap, swap primary/translation per "
            "docs/srt-format.md. With --shift, offset all cue times. With "
            "--drop-notes, remove translator-note cues from bilingual files. "
            "In-place when --output is omitted. Does not convert to other formats."
        ),
    )
    _add_shared_io_args(srt)
    srt.add_argument(
        "-s",
        "--swap",
        action="store_true",
        help="Swap top and bottom lines in bilingual subtitles",
    )
    srt.add_argument(
        "--shift",
        type=int,
        default=0,
        metavar="MS",
        help="Shift cue times by MS milliseconds (negative allowed)",
    )
    srt.add_argument(
        "--drop-notes",
        action="store_true",
        help=(
            "Drop single-line cues (translator notes) from bilingual SRTs; "
            "errors on monolingual files"
        ),
    )

    return parser


def _add_shared_io_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "path",
        type=Path,
        help="Subtitle file, or directory of subtitles (recursive by default)",
    )
    parser.add_argument(
        "--include",
        action="append",
        default=None,
        metavar="PATTERN",
        help=(
            "Filename glob when path is a directory; repeat to match any pattern "
            "(default: all supported subtitles for this command)"
        ),
    )
    parser.add_argument(
        "-L",
        "--depth",
        type=int,
        default=None,
        metavar="N",
        help=(
            "Max directory depth like tree -L (1=current dir only; default: unlimited)"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        metavar="DIR",
        help=(
            "Output directory (default: next to each source). "
            "When DIR equals path, names become name.<command>.<ext>"
        ),
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    if args.command == "convert":
        return _run_convert(args)
    if args.command == "srt":
        return _run_srt(args)
    parser.print_help()
    return 0


def _log(message: str) -> None:
    print(message, file=sys.stderr)


def _resolve_subtitles_timed(
    path: Path,
    include: list[str] | None,
    depth: int | None,
    suffixes: frozenset[str],
) -> list[Path]:
    started = time.perf_counter()
    files = resolve_subtitles(path, include, depth=depth, suffixes=suffixes)
    elapsed = time.perf_counter() - started
    _log(f"resolve: {len(files)} subtitle file(s) in {format_duration(elapsed)}")
    return files


def _run_each_file(
    command: str,
    files: list[Path],
    process: Callable[[Path], Path],
) -> int:
    batch_started = time.perf_counter()
    failed = 0
    for item in files:
        started = time.perf_counter()
        try:
            result = process(item)
            elapsed = time.perf_counter() - started
            print(result)
            _log(f"{command} {item.name}: {format_duration(elapsed)}")
        except SubToolError as exc:
            elapsed = time.perf_counter() - started
            print(exc, file=sys.stderr)
            _log(f"{command} {item.name}: failed in {format_duration(elapsed)}")
            failed += 1
    ok = len(files) - failed
    total = time.perf_counter() - batch_started
    _log(f"done: {ok} ok, {failed} failed, total {format_duration(total)}")
    return 1 if failed else 0


def _run_convert(args: argparse.Namespace) -> int:
    try:
        suffixes = source_suffixes_for_target(args.to)
        files = _resolve_subtitles_timed(args.path, args.include, args.depth, suffixes)
    except SubToolError as exc:
        print(exc, file=sys.stderr)
        return 1

    def process(source: Path) -> Path:
        return generate_convert(
            source,
            to=args.to,
            input_path=args.path,
            output_dir=args.output,
            lrc_last_ms=args.lrc_last_ms,
        )

    return _run_each_file("convert", files, process)


def _run_srt(args: argparse.Namespace) -> int:
    try:
        files = _resolve_subtitles_timed(
            args.path, args.include, args.depth, SRT_SUFFIXES
        )
    except SubToolError as exc:
        print(exc, file=sys.stderr)
        return 1

    def process(srt_file: Path) -> Path:
        return generate_srt_edit(
            srt_file,
            input_path=args.path,
            output_dir=args.output,
            swap=args.swap,
            shift_ms=args.shift,
            drop_notes=args.drop_notes,
        )

    return _run_each_file("srt", files, process)


if __name__ == "__main__":
    sys.exit(main())
