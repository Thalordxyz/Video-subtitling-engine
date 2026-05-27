# 🎬 Subtitling Engine — Full Workflow Documentation

---

## Overview

```
subtitling_engine.py "video.mp4"
│
├── PHASE 1 → AUTO   → verify tools + file
├── PHASE 2 → AUTO   → Whisper transcription
├── PHASE 3 → HUMAN  → review + correct segments
├── PHASE 4 → HUMAN  → pick subtitle style   (previews auto-generated)
├── PHASE 5 → HUMAN  → pick font size        (previews auto-generated)
├── PHASE 6 → HUMAN  → pick position         (previews auto-generated)
└── PHASE 7 → AUTO   → final render
```

| Metric | Value |
|--------|-------|
| Human decisions | 4 |
| LLM tokens used | 0 (default) |
| Total time | ~3–4 minutes |

---

## PHASE 1 — Setup Verification
**Type:** Automatic
**Duration:** ~2 seconds

The engine checks that all required tools are installed and the input
video file exists before doing any work.

### What it checks
- FFmpeg is installed and in PATH
- Python version is compatible
- Whisper is installed
- Input video file exists and is readable
- Detects video resolution and duration

### Output
```
✔ FFmpeg found
✔ Python found
✔ Whisper found
✔ File found: V2.5.mp4
  Resolution : 2160x3840
  Duration   : 41s
  Location   : C:\Users\proye\OneDrive\Escritorio\
```

### On failure
The engine stops immediately and shows which tool is missing,
with instructions on how to install it.

---

## PHASE 2 — Audio Transcription
**Type:** Automatic
**Duration:** ~1–3 minutes (depends on video length and Whisper model)

Whisper runs locally on the machine. No internet connection required.
No API keys needed. No tokens consumed.

### What it does
- Extracts audio from the video
- Auto-detects the language (or uses --lang flag)
- Transcribes with word-level timestamps
- Saves full result as JSON

### Output
```
⏳ Transcribing audio with Whisper...
✔ Done — 16 segments | 105 words | Language: ES
   Saved: VideoName_subtitles/VideoName_whisper.json
```

### Files produced
```
VideoName_subtitles/
└── VideoName_whisper.json      ← full transcription with timestamps
```

### Whisper models (configurable)
| Model | Speed | Accuracy | Best for |
|-------|-------|----------|---------|
| tiny | Fastest | Lower | Quick tests |
| base | Fast | Good | Default |
| small | Medium | Better | Short videos |
| medium | Slow | High | Important projects |
| large | Slowest | Highest | Maximum accuracy |

---

## PHASE 3 — Review & Correct Transcription
**Type:** Human interaction
**Duration:** 1–5 minutes (depends on corrections needed)

The engine displays the full transcription in a clean table.
The user can correct any segment or add missing ones.

### Display format
```
─────────────────────────────────────────────────────────────
 #    TIME                TEXT
─────────────────────────────────────────────────────────────
 1    00:00 → 00:04       5 años enviando dinero a Colombia...
 2    00:05 → 00:06       Y si cada peso que envío,
 3    00:06 → 00:09       construyerá un patrimonio real...
─────────────────────────────────────────────────────────────
```

### How to make corrections
Type the segment number followed by a colon and the corrected text.
Press Enter with no input to skip and continue.

```
Corrections (1: new text) or press Enter to skip:
> 1: 5 años enviando dinero a colombia y mi familia aun vive en arriendo
> 9: a través de un crédito hipotecario
> (Enter)
```

### Rules
- Corrections are at segment level (full text of a segment)
- Word-level corrections are not supported
- Timestamps are trusted as-is (Whisper timing is not modified)
- Multiple corrections can be made before pressing Enter

### Adding a missing segment
After corrections, the engine asks if a segment needs to be added:

```
Do you want to add a missing segment? (yes/no): yes

Start time (example → 00:42.00): 00:42.00
End time   (example → 00:45.50): 00:45.50
Text: Este es el texto del segmento faltante.

Do you want to add another segment? (yes/no): no
```

### Files produced
```
VideoName_subtitles/
└── VideoName_corrected.json    ← corrected transcription
```

---

## PHASE 4 — Style Selection
**Type:** Automatic previews + Human choice
**Duration:** ~30 seconds (previews) + your decision time

The engine generates a 5-second preview clip for each available style,
saves them to the style selection folder, then asks you to choose.

### Available styles
| Option | Name | Description |
|--------|------|-------------|
| A | Classic Karaoke | White text · Yellow highlight · Black outline |
| B | Bold Karaoke | Thicker outline · Stronger yellow · No background |
| C | Box Karaoke | Dark semi-transparent box · Yellow highlight |
| D | Glow Karaoke | Soft glow on current word · No outline |

### Terminal display
```
⏳ Generating style previews...
✔ Saved to: VideoName_subtitles/01_style_selection/

Open the preview files and choose:

  [A] Classic  — white text, yellow highlight, black outline
  [B] Bold     — thicker outline, stronger yellow
  [C] Box      — dark background behind text, yellow highlight
  [D] Glow     — soft glow on current word

Your choice (A/B/C/D): B
```

### Files produced
```
VideoName_subtitles/
└── 📁 01_style_selection/
    ├── preview_A_classic.mp4
    ├── preview_B_bold.mp4
    ├── preview_C_box.mp4
    └── preview_D_glow.mp4
```

---

## PHASE 5 — Size Selection
**Type:** Automatic previews + Human choice
**Duration:** ~20 seconds (previews) + your decision time

Three preview clips are generated using the chosen style, each with a
different font size. The user picks the one that looks best.

### Available sizes
| Option | Size | Best for |
|--------|------|---------|
| S | 90px | Subtle, longer text lines |
| M | 120px | Balanced — most common |
| L | 150px | High impact, short phrases |

### Terminal display
```
⏳ Generating size previews with Bold style...
✔ Saved to: VideoName_subtitles/02_size_selection/

  [S] Small  —  90px
  [M] Medium — 120px
  [L] Large  — 150px

Your choice (S/M/L): L
```

### Files produced
```
VideoName_subtitles/
└── 📁 02_size_selection/
    ├── preview_small.mp4
    ├── preview_medium.mp4
    └── preview_large.mp4
```

---

## PHASE 6 — Position Selection
**Type:** Automatic previews + Human choice
**Duration:** ~20 seconds (previews) + your decision time

Three preview clips are generated using the chosen style and size,
each with a different vertical position. The user picks the one that
looks best with their video content.

### Available positions
| Option | Name | Description |
|--------|------|-------------|
| 1 | Bottom | Very close to the bottom edge |
| 2 | Lower-third | Classic TV / social media position |
| 3 | Mid-low | More centered, above lower-third |

### Terminal display
```
⏳ Generating position previews with Bold + Large...
✔ Saved to: VideoName_subtitles/03_position_selection/

  [1] Bottom       — close to the edge
  [2] Lower-third  — classic TV / social media
  [3] Mid-low      — more centered

Your choice (1/2/3): 2
```

### Files produced
```
VideoName_subtitles/
└── 📁 03_position_selection/
    ├── preview_bottom.mp4
    ├── preview_lowerthird.mp4
    └── preview_midlow.mp4
```

---

## PHASE 7 — Final Render
**Type:** Automatic
**Duration:** ~37 seconds for 4K 42-second video

The engine generates the final ASS subtitle file with all confirmed
settings and burns it permanently into the video using FFmpeg.
The original video is never modified.

### What it does
- Generates final ASS subtitle file with chosen style, size and position
- Uses hardware-accelerated decode (DXVA2) for speed
- Copies audio untouched (no re-encoding)
- Outputs H.264 video with burned-in subtitles

### Terminal display
```
⏳ Rendering final video...
   Style    : Bold (B)
   Size     : 150px (L)
   Position : Lower-third (2)

✔ Done!
   Output   : VideoName_subtitles/04_final/VideoName_karaoke.mp4
   Duration : 00:00:41.76
   Size     : 188 MB
```

### Files produced
```
VideoName_subtitles/
├── VideoName_karaoke.ass       ← subtitle file (editable)
└── 📁 04_final/
    └── VideoName_karaoke.mp4   ← final video with subtitles
```

---

## Complete file output summary

```
📁 VideoName_subtitles/
│
├── VideoName_whisper.json          ← raw Whisper transcription
├── VideoName_corrected.json        ← corrected transcription
├── VideoName_karaoke.ass           ← final subtitle file
│
├── 📁 01_style_selection/
│   ├── preview_A_classic.mp4
│   ├── preview_B_bold.mp4
│   ├── preview_C_box.mp4
│   └── preview_D_glow.mp4
│
├── 📁 02_size_selection/
│   ├── preview_small.mp4
│   ├── preview_medium.mp4
│   └── preview_large.mp4
│
├── 📁 03_position_selection/
│   ├── preview_bottom.mp4
│   ├── preview_lowerthird.mp4
│   └── preview_midlow.mp4
│
└── 📁 04_final/
    └── VideoName_karaoke.mp4       ← ✅ final output
```

---

## Karaoke subtitle technical details

### Format
ASS (Advanced SubStation Alpha) — burned into video via FFmpeg

### How karaoke highlighting works
For each segment containing N words, the engine creates N subtitle events.
Each event shows the full segment text with only the current word highlighted.

Example — segment with 4 words, word 2 active:
```
word1  [WORD2]  word3  word4
white  yellow   white  white
```

### Style parameters (ASS)
| Parameter | Classic | Bold | Box | Glow |
|-----------|---------|------|-----|------|
| Primary color | White | White | White | White |
| Highlight color | Yellow | Yellow | Yellow | Yellow |
| Outline | 4px black | 8px black | 4px black | 0px |
| Background | None | None | Dark box | None |
| Shadow | No | No | No | Glow |

---

## LLM usage

By default the engine uses **zero LLM tokens**.

The optional `--smart-correct` flag enables natural language corrections:
```bash
python subtitling_engine.py "video.mp4" --smart-correct
```

| Mode | Tokens | Cost |
|------|--------|------|
| Default | 0 | $0.00 |
| --smart-correct | ~500–800 | ~$0.001 |

The LLM provider can be configured in `config/config.json`.
