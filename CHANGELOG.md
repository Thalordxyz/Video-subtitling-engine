# Changelog

All notable changes to the Subtitling Engine are documented here.
Format: [version] — date — description

---

## [1.0.0] — 2026-05-27 — Initial Release

### Added
- Phase 1: automatic tool and file verification
- Phase 2: Whisper transcription with word-level timestamps
- Phase 3: interactive segment-level correction interface
- Phase 3: ability to add missing segments manually
- Phase 4: style selection with 4 options (Classic, Bold, Box, Glow)
- Phase 5: size selection with 3 options (Small, Medium, Large)
- Phase 6: position selection with 3 options (Bottom, Lower-third, Mid-low)
- Phase 7: final render with FFmpeg hardware-accelerated decode
- Karaoke-style subtitles: word-by-word yellow highlight
- Output folder structure: 01_style / 02_size / 03_position / 04_final
- config.json for user defaults
- Support for portrait and landscape 4K video
- --smart-correct flag for optional LLM-assisted corrections
- --model flag for Whisper model selection
- --lang flag for language override

### Technical
- ASS subtitle format with libass rendering
- DXVA2 hardware decode for fast rendering
- Zero LLM tokens by default
- Original video never modified

---

## [Planned] — Stage 2

### To be added
- Web UI using Gradio or Streamlit
- Visual transcription editor (click to edit segments)
- Drag-and-drop video input

---

## [Planned] — Stage 3

### To be added
- Server deployment (cloud VM or VPS)
- Multi-user support
- Job queue system
- Progress tracking via web interface

---

## [Planned] — Stage 4

### To be added
- REST API with FastAPI
- POST /transcribe endpoint
- POST /correct endpoint
- POST /generate-preview endpoint
- POST /render endpoint
- GET /status/{job_id} endpoint
- API key authentication
