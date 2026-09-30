"""Shared output path resolution for sub-tool subcommands."""

from __future__ import annotations

from pathlib import Path

from sub_tool.errors import SubToolError


def resolve_output_path(
    source: Path,
    *,
    input_path: Path,
    output_dir: Path | None,
    command: str,
    suffix: str,
    keep_command_in_default: bool,
) -> Path:
    """Resolve where to write a processed file for ``source``.

    ``suffix`` includes the leading dot (e.g. ``.srt``, ``.txt``).

    - No ``output_dir``: write next to ``source``. Default name is
      ``{stem}{suffix}``, or ``{stem}.{command}{suffix}`` when
      ``keep_command_in_default`` is true.
    - ``output_dir`` equals resolved ``input_path``: use
      ``{stem}.{command}{suffix}`` to avoid clobbering sources.
    - Otherwise: ``{stem}{suffix}`` under ``output_dir``.
    - If the candidate path still resolves to ``source``, fall back to the
      collision-safe ``{stem}.{command}{suffix}`` name.
    """
    if not suffix.startswith("."):
        raise SubToolError(f"suffix must start with '.', got {suffix!r}")
    if not command:
        raise SubToolError("command name is required for output resolution")

    stem = source.stem
    collision_name = f"{stem}.{command}{suffix}"
    same_basename = f"{stem}{suffix}"

    if output_dir is None:
        name = collision_name if keep_command_in_default else same_basename
        return (source.parent / name).resolve()

    out = _require_output_dir(output_dir)
    inp = input_path.expanduser().resolve()
    name = collision_name if out == inp else same_basename

    candidate = (out / name).resolve()
    if candidate == source.expanduser().resolve():
        candidate = (out / collision_name).resolve()
    return candidate


def _require_output_dir(output_dir: Path) -> Path:
    resolved = output_dir.expanduser().resolve()
    if not resolved.exists():
        raise SubToolError(f"--output directory not found: {output_dir}")
    if not resolved.is_dir():
        raise SubToolError(f"--output must be a directory: {output_dir}")
    return resolved
