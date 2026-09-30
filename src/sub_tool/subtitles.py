"""Discover subtitle files from a path argument."""

from __future__ import annotations

import fnmatch
import os
from pathlib import Path

from sub_tool.errors import SubToolError

SRT_SUFFIX = ".srt"
ASS_SUFFIX = ".ass"
LRC_SUFFIX = ".lrc"

SRT_SUFFIXES: frozenset[str] = frozenset({SRT_SUFFIX})
ASS_SUFFIXES: frozenset[str] = frozenset({ASS_SUFFIX})
LRC_SUFFIXES: frozenset[str] = frozenset({LRC_SUFFIX})

ALL_SUBTITLE_SUFFIXES: frozenset[str] = SRT_SUFFIXES | ASS_SUFFIXES | LRC_SUFFIXES


def resolve_subtitles(
    path: Path,
    includes: list[str] | None,
    *,
    depth: int | None,
    suffixes: frozenset[str],
) -> list[Path]:
    """Resolve ``path`` to a sorted list of subtitle files with given ``suffixes``."""
    if depth is not None and depth < 1:
        raise SubToolError(f"--depth must be >= 1, got {depth}")

    resolved = path.expanduser().resolve()
    if not resolved.exists():
        raise SubToolError(f"path not found: {path}")

    if resolved.is_file():
        if includes:
            raise SubToolError("--include can only be used with a directory path")
        if depth is not None:
            raise SubToolError("--depth can only be used with a directory path")
        if resolved.suffix.lower() not in suffixes:
            raise SubToolError(f"not a supported subtitle file: {path}")
        return [resolved]

    if resolved.is_dir():
        files = _directory_subtitles(resolved, depth, suffixes)
        if includes:
            files = [
                item
                for item in files
                if any(fnmatch.fnmatch(item.name, pattern) for pattern in includes)
            ]
        if not files:
            detail = " matching --include" if includes else ""
            raise SubToolError(f"no subtitle files found{detail} in directory: {path}")
        return files

    raise SubToolError(f"path is neither a file nor a directory: {path}")


def _directory_subtitles(
    root: Path,
    max_depth: int | None,
    suffixes: frozenset[str],
) -> list[Path]:
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        current = Path(dirpath)
        rel = current.relative_to(root)
        dir_depth = 0 if rel == Path(".") else len(rel.parts)
        file_depth = dir_depth + 1
        if max_depth is not None and file_depth > max_depth:
            dirnames.clear()
            continue
        for name in filenames:
            candidate = current / name
            if candidate.suffix.lower() in suffixes:
                found.append(candidate)
        if max_depth is not None and file_depth >= max_depth:
            dirnames.clear()
    return sorted(found)
