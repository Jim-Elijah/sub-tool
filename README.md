# sub-tool

A Python toolkit for subtitle conversion and utilities.

**For personal use; not published to PyPI for now.**

## Requirements

- Python 3.12+

## Install

Not published to PyPI yet. Install from a clone:

```bash
git clone <your-repo-url>
cd sub-tool
pip install .
```

Then run:

```bash
sub-tool --help
sub-tool --version
```

With [uv](https://docs.astral.sh/uv/) (also installs development dependencies):

```bash
uv sync
uv run sub-tool --help
```

## Subcommands

| Command | Purpose |
|---------|---------|
| `convert --to FMT` | Change format or export to plain text (source from file extension) |
| `srt` | Edit `.srt` files only (re-number, optional bilingual line swap) |

Format-specific subcommands (`ass`, `lrc`, …) can be added later for operations that are not simple conversion.

## Convert (`convert --to`)

Supported targets: `srt`, `txt`, `lrc`, `ass` (only some source→target pairs are implemented).

| `--to` | Implemented sources | Default output |
|--------|---------------------|----------------|
| `srt` | `.ass` | `name.srt` next to source |
| `txt` | `.srt` | `name.txt` next to source |
| `lrc`, `ass` | — | not implemented yet |

```bash
sub-tool convert --to srt path/to/subtitle.ass
sub-tool convert --to srt path/to/dir -L 1
sub-tool convert --to txt path/to/subtitle.srt
sub-tool convert --to txt path/to/dir --output path/to/out
```

Bilingual (multi-line) cues are preserved when converting ASS → SRT.

## Subtitle format conventions

Authoring rules for **bilingual** and **same-timeline multi-speaker** cues (SRT, ASS, planned LRC), with examples: [docs/subtitle-formats.md](docs/subtitle-formats.md).

## SRT edits (`srt`)

Does **not** convert formats. Re-number cues from 1; `--swap` reverses **all** text lines within each cue (typical use: swap two bilingual lines). See [docs/subtitle-formats.md](docs/subtitle-formats.md).

```bash
sub-tool srt path/to/subtitle.srt
sub-tool srt path/to/subtitle.srt --swap
sub-tool srt path/to/dir --swap --output path/to/out
```

Without `--output`, writes back to each source `.srt` file.

## Shared options

Most subcommands accept the same input/output discovery flags:

| Flag | Meaning |
|------|---------|
| `path` | Subtitle file, or directory of subtitles (recursive by default) |
| `--include PATTERN` | Filename glob when `path` is a directory (repeatable) |
| `-L` / `--depth N` | Max directory depth like `tree -L` (`1` = current dir only) |
| `--output DIR` | Output **directory** (default: next to each source) |

`--output` naming:

- No `--output`: default next to the source (`convert --to srt` → `name.srt`; `convert --to txt` → `name.txt`; `srt` → in-place `name.srt`)
- `--output` equals the CLI `path`: `{stem}.{command}{suffix}` (e.g. `name.convert.srt`)
- Otherwise: `{stem}{suffix}` under that directory
- If the computed path would overwrite the source, falls back to `{stem}.{command}{suffix}`

**Output streams:** stdout prints output paths only (one per line); discovery, per-file work, and batch timing go to stderr.

## Development

```bash
uv sync
uv run ruff format .
uv run ruff check .
uv run pytest
```
