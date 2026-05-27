# 🎬 Subtitling Engine

A local, fully automated karaoke-style subtitle generator for video files.
No internet required. No LLM tokens consumed. Runs entirely on your machine.

---

## ✅ What it does

1. Transcribes audio from any `.mp4` video using Whisper (local AI)
2. Lets you review and correct the transcription segment by segment
3. Generates short preview clips for you to choose subtitle style, size and position
4. Renders the final video with burned-in karaoke subtitles

---

## 🖥️ Requirements

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.9+ | Runs the engine |
| FFmpeg | Any recent | Video rendering |
| Whisper | Latest | Audio transcription |

Install Python dependencies:
```bash
pip install -r requirements.txt
```

FFmpeg must be installed separately and available in your system PATH.

---

## 🚀 How to run

```bash
python subtitling_engine.py "path/to/your/video.mp4"
```

### Optional flags

| Flag | Description |
|------|-------------|
| `--smart-correct` | Use LLM to apply natural language corrections |
| `--model base` | Whisper model size: tiny, base, small, medium, large |
| `--lang es` | Force language (default: auto-detect) |

### Examples

```bash
# Basic usage
python subtitling_engine.py "V2.5.mp4"

# Force Spanish, use medium Whisper model
python subtitling_engine.py "V2.5.mp4" --lang es --model medium

# Enable smart corrections via LLM
python subtitling_engine.py "V2.5.mp4" --smart-correct
```

---

## 📁 Output folder structure

A folder is automatically created next to the original video:

```
📁 VideoName_subtitles/
│
├── 📁 01_style_selection/       ← 4 preview clips (~5 sec each)
│   ├── preview_A_classic.mp4
│   ├── preview_B_bold.mp4
│   ├── preview_C_box.mp4
│   └── preview_D_glow.mp4
│
├── 📁 02_size_selection/        ← 3 preview clips (chosen style)
│   ├── preview_small.mp4
│   ├── preview_medium.mp4
│   └── preview_large.mp4
│
├── 📁 03_position_selection/    ← 3 preview clips (chosen style + size)
│   ├── preview_bottom.mp4
│   ├── preview_lowerthird.mp4
│   └── preview_midlow.mp4
│
└── 📁 04_final/                 ← final rendered video
    └── VideoName_karaoke.mp4
```

---

## 📁 Engine folder structure

```
subtitling_engine/
│
├── subtitling_engine.py         ← main entry point
│
├── engine/
│   ├── steps/
│   │   ├── 01_transcribe.py    ← Whisper transcription
│   │   ├── 02_correct.py       ← apply user corrections
│   │   ├── 03_generate_ass.py  ← build ASS subtitle file
│   │   ├── 04_preview.py       ← generate preview clips
│   │   └── 05_render.py        ← final FFmpeg render
│
├── styles/
│   ├── classic_karaoke.json    ← white/yellow/outline
│   ├── bold_karaoke.json       ← thicker outline
│   ├── box_karaoke.json        ← dark background box
│   └── glow_karaoke.json       ← glow on current word
│
├── config/
│   └── config.json             ← default settings
│
└── docs/
    ├── WORKFLOW.md              ← full workflow documentation
    └── workflow_diagram.png     ← visual diagram
```

---

## ⚙️ Configuration

Edit `config/config.json` to set your personal defaults:

```json
{
  "default_style": "classic",
  "default_size": "medium",
  "default_position": "lowerthird"
}
```

---

## 🗺️ Roadmap

| Stage | Description | Status |
|-------|-------------|--------|
| 1 | Local CLI engine | 🔨 In progress |
| 2 | Web UI (Gradio or Streamlit) | 📋 Planned |
| 3 | Server deployment | 📋 Planned |
| 4 | REST API | 📋 Planned |

---

## 📄 License

Private — all rights reserved.
