# SRT formats (sub-tool)

This document describes common SRT layouts supported by **sub-tool** and how the `srt` subcommand (`--swap`, `--drop-notes`) interprets each cue.  
Cross-format ASS / LRC rules: [subtitle-formats.md](subtitle-formats.md). Implementation: `src/sub_tool/srt_cue.py`.  
Chinese (Simplified): [srt-format.zh-CN.md](srt-format.zh-CN.md).

## Basic structure

Each **cue** (subtitle block) has three parts:

1. Index (digits only; any values are fine — `sub-tool srt` renumbers to 1, 2, 3…)
2. Time range: `HH:MM:SS,mmm --> HH:MM:SS,mmm` (`.` is also accepted as the millisecond separator)
3. One or more **text lines** (players show them as lines; this tool parses line by line)

```srt
1
00:01:14,740 --> 00:01:16,740
Example dialogue line.
```

Blank lines separate cues. UTF-8; optional BOM.

---

## Layout overview

| Type | Typical use | Bilingual? | `--drop-notes` |
|------|-------------|------------|----------------|
| Monolingual, one line | Dialogue, narration | No | May remove in bilingual files (translator notes) |
| Monolingual, multi-line `-` | Same-timeline speakers, no ID | No | Not removed (multi-line) |
| Bilingual, two lines | Most common bilingual | Yes | Not removed |
| Bilingual, one line ` \| ` | Compact bilingual | Yes | Not removed |
| `[SPEAKER_xx]:` | Diarization / speaker labels | Depends | Tagged single lines not removed |
| Multi-speaker + ` \| ` per line | Same-timeline bilingual | Yes | Not removed |
| Stacked halves | Primary block + translation block | Yes | Not removed |

---

## 1. Monolingual subtitles

### 1.1 Single-line dialogue

```srt
1
00:00:10,000 --> 00:00:13,500
You're an idiot!
```

`convert --to txt` / `--to lrc`: exports text per cue; `srt --swap` has no effect (one line only).

### 1.2 Same-timeline multiple speakers (no speaker ID)

Each line starting with **`- `** is a different speaker, still in **one cue, one time range**:

```srt
1
00:01:20,000 --> 00:01:23,500
- What time do you get off today?
- Around six.
```

Compact form (multiple `- ` segments on one line):

```srt
1
00:01:20,000 --> 00:01:23,500
- What time do you get off today? - Around six.
```

**Not bilingual**: when both lines start with `-`, the tool does not treat them as primary + translation.

---

## 2. Bilingual subtitles (no speaker tags)

### 2.1 Recommended: two stacked lines

First line primary language, second line translation; lines must **not** start with `-` and must **not** include `[SPEAKER_xx]:`.

```srt
1
00:01:14,740 --> 00:01:16,740
Oh, my God.
上帝啊
```

- `srt --swap`: swaps the two lines.  
- `convert --to lrc`: merges to `Oh, my God. | 上帝啊` (one line).

### 2.2 Single line: ` | ` separator

Join primary and translation with **` | `** (space-pipe-space):

```srt
1
00:00:10,000 --> 00:00:13,500
Hello, world! | 你好，世界！
```

- `srt --swap`: swaps text on both sides of ` | `.  
- Files that mostly use this or two-line bilingual cues are treated as **bilingual files**.

---

## 3. Translator notes

During production you may insert **single-line** explanations (terms, context) with no translation pair and no speaker tag, overlapping or separate from dialogue:

```srt
4
00:00:42,970 --> 00:00:45,650
所以她的真正动机众说纷纭

7
00:00:51,480 --> 00:00:53,660
补选  指在两个常规选举日之间
```

Traits: one line, no ` | `, no `[SPEAKER_xx]:`.

On files where **bilingual cues are the majority**, `srt --drop-notes` **removes** these cues and renumbers; monolingual files exit with an error.

---

## 4. Speaker IDs (Whisper / PyAnnote, etc.)

Tag format: **`[SPEAKER_digits]:`** (case-insensitive) at the start of a line.

### 4.1 One speaker, monolingual

```srt
1
00:00:05,000 --> 00:00:07,000
[SPEAKER_01]: I won't be long.
```

### 4.2 One speaker, bilingual: one line with ` | `

```srt
1
00:00:08,000 --> 00:00:11,000
[SPEAKER_01]: You're late when I say you're late. | 我说你迟了就是迟了
```

`srt --swap`: keeps `[SPEAKER_01]:`, swaps only the sides of ` | `.

### 4.3 One speaker, bilingual: two lines, same ID

```srt
1
00:00:12,000 --> 00:00:14,000
[SPEAKER_03]: Well, quite right, too.
[SPEAKER_03]: 说得没错
```

`srt --swap`: swaps the two lines (same speaker).

---

## 5. Same-timeline multiple speakers + bilingual

### 5.1 Recommended: one line per speaker, inline ` | `

```srt
2
00:03:34,460 --> 00:03:36,710
[SPEAKER_01]: - Where have you been? | 你上哪儿去了
[SPEAKER_02]: - I'm not late, am I? | 我没迟到吧
```

`srt --swap`: swaps ` | ` on **each line** separately (keeps `[SPEAKER_xx]: -` prefix).

### 5.2 Two compact lines: multiple speakers per line

One line primary, one line translation; **`[SPEAKER_xx]` count and order must match** on both lines:

```srt
2
00:03:34,460 --> 00:03:36,710
[SPEAKER_01]: - Where have you been?  [SPEAKER_02]: - I'm not late, am I?
[SPEAKER_01]: - 你上哪儿去了  [SPEAKER_02]: - 我没迟到吧
```

`srt --swap`: swaps the **upper line block** with the **lower line block** (aligned by speaker order, not a simple per-line reversal).

### 5.3 Multiple speakers + stacked halves (no inline ` | `)

Within one cue, **one utterance per line** (`[SPEAKER_xx]:` + dialogue). The tool reads speaker tags **per line**; it does not merge multiple lines for one speaker into one record, and it does not pair “sentence N” in one language with “sentence N” in the other.

**Minimal example** (2 lines in the first half, 2 in the second; matching IDs per row):

```srt
2
00:03:34,460 --> 00:03:36,710
[SPEAKER_01]: - Where have you been?
[SPEAKER_02]: - I'm not late, am I?
[SPEAKER_01]: - 你上哪儿去了
[SPEAKER_02]: - 我没迟到吧
```

**Extended example** (4 + 4 lines; IDs still 01→02→01→02 per row):

```srt
2
00:03:34,460 --> 00:03:36,710
[SPEAKER_01]: - Where have you been?
[SPEAKER_02]: - I'm not late, am I?
[SPEAKER_01]: - You're late when I say you're late.
[SPEAKER_02]: - Ok.
[SPEAKER_01]: - 你上哪儿去了
[SPEAKER_02]: - 我没迟到吧
[SPEAKER_01]: - 我说你迟了就是迟了
[SPEAKER_02]: - 好的.
```

**Bilingual detection**: even line count, and the `[SPEAKER_xx]` sequence in the first half **matches row-by-row** in the second half.

**`srt --swap`**: **swaps whole halves** only (all lines from the second half move before the first); text and tags on each line stay unchanged. After swap on the extended example:

```srt
[SPEAKER_01]: - 你上哪儿去了
[SPEAKER_02]: - 我没迟到吧
[SPEAKER_01]: - 我说你迟了就是迟了
[SPEAKER_02]: - 好的.
[SPEAKER_01]: - Where have you been?
[SPEAKER_02]: - I'm not late, am I?
[SPEAKER_01]: - You're late when I say you're late.
[SPEAKER_02]: - Ok.
```

For **adjacent primary/translation per utterance**, use §5.1 (inline ` | `) or §5.2 (two compact lines); do not rely on half-block swap for per-sentence reordering.

### 5.4 Multi-speaker monolingual (one language only, no ` | `)

```srt
2
00:03:34,460 --> 00:03:36,710
[SPEAKER_01]: - Where have you been?
[SPEAKER_02]: - I'm not late, am I?
```

Two lines and no translation half → **monolingual**, not a bilingual cue.

---

## 6. Multiple speakers + single line with multiple ` | ` segments (no ID)

```srt
1
00:00:10,000 --> 00:00:13,500
- Hello, world! | 你好，世界！ - How are you? | 你最近怎么样？
```

Split on **` - `**; if a segment contains ` | `, `srt --swap` swaps within each segment. Fine for a few compact cues; prefer §5.1 for complex dialogue.

---

## 7. Command summary

| Command | Behavior |
|---------|----------|
| `srt` | Renumber; optional `--swap` / `--shift` / `--drop-notes` |
| `srt --swap` | Swap primary/translation per rules above (see `swap_cue_text_lines`) |
| `srt --drop-notes` | Bilingual files only; removes §3 note cues |
| `convert --to txt` | All text lines (SRT strips `<...>` tags) |
| `convert --to lrc` | One line per cue; **only** §2.1 two lines without `-`/SPEAKER become ` \| ` |
| `convert --to json` | One record per cue: `start_ms`/`end_ms` + `lines` array; see JSON in [subtitle-formats.md](subtitle-formats.md) |

Flags can be combined, e.g. `sub-tool srt file.srt --drop-notes --swap`.

---

## 8. Common mistakes

1. **Do not label all English as SPEAKER_01 and all Chinese as SPEAKER_02** if the second block is really translation — use §2, §4, or §5 bilingual layouts; otherwise `--swap` / LRC treat them as speaker blocks.

2. **` | ` is a bilingual separator, not a speaker separator**  
   Use `- `, `[SPEAKER_xx]:`, or separate lines for speakers.

3. **Players do not implement this project’s SPEAKER / ` | ` rules**  
   These conventions are for authoring and tooling; display depends on the player.

4. **`--drop-notes` does not remove** single-line bilingual cues with ` | `, or single lines with `[SPEAKER_xx]:`.

5. **§5.3 stacked halves are not a per-sentence translation table**  
   `--swap` only swaps language halves; it does not merge or reorder sentence 3 in English with sentence 3 in Chinese.

---

## 9. When is a file “bilingual”?

`--drop-notes` requires **more than half** of cues to satisfy `cue_is_bilingual` (§2, §4 bilingual, §5 bilingual, etc.).  
Otherwise the file is treated as monolingual and the command errors.
