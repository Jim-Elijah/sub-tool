# Subtitle format conventions

These conventions apply to files processed by **sub-tool** (`.srt`, `.ass`, and future `.lrc`). They are not universal standards for every player—players treat cue text as plain lines—but they keep bilingual and multi-speaker cues consistent across convert and edit commands.

## Core rules

1. **One time range = one unit** — one SRT cue, one ASS `Dialogue:` line, or one LRC timestamp line. Same-timeline multiple speakers and bilingual text live inside that unit (no separate “tracks” in SRT/LRC).
2. **Bilingual** — Prefer **two lines** per cue: first line primary language, second line translation. For a single display line, join with **` | `** (spaces optional but consistent within a file).
3. **Multi-speaker (same cue)** — Prefer **one speaker per line**, each line starting with **`- `**. Optional label: **`[SPEAKER_ID]: - text`**. Compact same-line form: **`- utterance A - utterance B`** (space-separated `- ` segments). Use **`|`** only for **bilingual pairs within one utterance**, not between speakers.
4. **ASS → SRT** — Line breaks from `\N` / `\n` in ASS text are kept; `{...}` override tags are stripped; speakers are not split or merged automatically.
5. **`srt --swap`** — Swaps primary/translation per cue using rules in [srt-format.md](srt-format.md) (two lines, inline ` | `, same-speaker pairs, stacked speaker halves).
6. **`srt --drop-notes`** — On bilingual SRTs (strict majority per [srt-format.md](srt-format.md)), drops translator-note cues (single line, no ` | `, no `[SPEAKER_xx]:`). Refused on monolingual files.
7. **`convert --to txt`** — Exports dialogue text from SRT, ASS, or LRC (SRT: every cue text line, strips `<...>` tags; ASS: cleaned dialogue lines; LRC: text after each timestamp).
8. **`convert --to lrc`** — One `[mm:ss.xx]` line per cue; two-line non-speaker cues become `line1 | line2`; other multi-line cues join with spaces (see LRC section).
9. **`convert --to srt` from LRC** — End time is the next line’s start minus 1 ms, or start + 3 s for the last cue.

## Supported formats (in this project)

| Extension | Role in sub-tool |
|-----------|-------------------|
| `.ass` | Source for `convert --to srt`, `txt`, or `lrc` (not a convert target) |
| `.srt` | Target from ASS/LRC; source for `convert --to txt`/`lrc` and `srt` edits |
| `.lrc` | Target from SRT/ASS; source for `convert --to srt`/`txt` |
| `.txt` | Plain text export from SRT/ASS/LRC (not a timed subtitle format) |

---

## SRT

Structure: index, timestamp line, then one or more text lines.

**Full catalog** of monolingual, bilingual, speaker-tagged, and translator-note layouts: **[srt-format.md](srt-format.md)**.

### Bilingual (recommended: two lines)

```srt
1
00:00:10,000 --> 00:00:13,500
Welcome to the tutorial.
欢迎观看本教程。

2
00:00:14,000 --> 00:00:17,200
Let's learn about SRT dual subtitles.
让我们来了解一下SRT双语字幕。
```

### Bilingual (single line)

```srt
1
00:00:10,000 --> 00:00:13,500
Hello, world! | 你好，世界！
```

### Multi-speaker (recommended: one line per speaker)

```srt
1
00:01:20,000 --> 00:01:23,500
- 你今天几点下班？
- 大概六点。

2
00:03:34,460 --> 00:03:36,710
[SPEAKER_01]: - Where have you been?
[SPEAKER_02]: - I'm not late, am I?
[SPEAKER_01]: - 你上哪儿去了
[SPEAKER_02]: - 我没迟到吧
```

### Multi-speaker + bilingual (one line per speaker, `|` inside each)

```srt
1
00:03:34,460 --> 00:03:36,710
[SPEAKER_01]: - Where have you been? | 你上哪儿去了
[SPEAKER_02]: - I'm not late, am I? | 我没迟到吧
```

### Multi-speaker (compact, same cue, one line each or merged)

```srt
1
00:01:20,000 --> 00:01:23,500
- 你今天几点下班？ - 大概六点。
```

```srt
1
00:00:10,000 --> 00:00:13,500
- Hello, world! | 你好，世界！ - How are you? | 你最近怎么样？
```

---

## ASS / SSA

One `Dialogue:` row per time range. Use `\N` for line breaks in the `Text` field. Styles and the `Name` column can distinguish speakers in advanced files; conversion to SRT only preserves cleaned text and newlines.

### Bilingual (two lines in Text)

```ass
Dialogue: 0,0:00:10.00,0:00:13.50,Default,,0,0,0,,Welcome to the tutorial.\N欢迎观看本教程。
```

### Multi-speaker (text convention matching SRT)

```ass
Dialogue: 0,0:01:20.00,0:01:23.50,Default,,0,0,0,,- 你今天几点下班？\N- 大概六点。
```

After `sub-tool convert --to srt`, `\N` becomes real newlines in the `.srt` cue body.

---

## LRC

LRC has no reliable multi-line cue in most players. **Use one timestamp line** and put speakers and bilingual pairs on that line.

### Bilingual (single line, recommended)

```lrc
[00:15.00]Hello, world! | 你好，世界！
[00:18.50]How are you? | 你最近怎么样？
```

### Multi-speaker (same timestamp line, `- ` separators)

```lrc
[01:20.00] - 你今天几点下班？ - 大概六点。
[01:24.15] - 那一起吃晚饭吗？ - 好啊。
```

### Not recommended: duplicate timestamps for “two lines”

Some tools use two lines with the same time for bilingual display; many players show only one or flicker. Prefer **` | `** on one line until a dedicated LRC feature documents otherwise.

---

## Plain text (`convert --to txt`)

Output is all dialogue lines from `.srt`, in file order, separated by newlines—timestamps and cue numbers are omitted. Treat it as a lossy, untimed extract, not a round-trippable subtitle format.
