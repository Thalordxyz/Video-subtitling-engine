#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║              🎬  SUBTITLING ENGINE  v1.0.0                  ║
║     Karaoke-style subtitle generator for video files        ║
║     Zero LLM tokens by default — 100% local                 ║
╚══════════════════════════════════════════════════════════════╝

Usage:
    python subtitling_engine.py "path/to/video.mp4"
    python subtitling_engine.py "video.mp4" --model medium --lang es
    python subtitling_engine.py "video.mp4" --smart-correct
"""

import sys
import os
import json
import argparse
import subprocess

# ── Make sure engine modules are importable ───────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.steps import transcribe, correct, generate_ass, preview, render


# ── Config ────────────────────────────────────────────────────────────────────

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config", "config.json")
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


# ── Output folders ────────────────────────────────────────────────────────────

def create_output_folders(video_path):
    """
    Create the output folder structure next to the original video.

    Returns:
        folders    : dict with keys base / style / size / position / final
        video_name : base filename without extension
    """
    video_dir  = os.path.dirname(os.path.abspath(video_path))
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    base       = os.path.join(video_dir, f"{video_name}_subtitles")

    folders = {
        "base":     base,
        "style":    os.path.join(base, "01_style_selection"),
        "size":     os.path.join(base, "02_size_selection"),
        "position": os.path.join(base, "03_position_selection"),
        "final":    os.path.join(base, "04_final"),
    }
    for path in folders.values():
        os.makedirs(path, exist_ok=True)

    return folders, video_name


# ── Tool verification ─────────────────────────────────────────────────────────

def check_tools():
    """Check that all required tools are installed. Returns True if all OK."""
    all_ok = True

    for tool, args in [("ffmpeg", ["-version"]), ("ffprobe", ["-version"])]:
        try:
            subprocess.run([tool] + args, capture_output=True, check=True)
            print(f"  ✔ {tool} found")
        except (FileNotFoundError, subprocess.CalledProcessError):
            print(f"  ✗ {tool} NOT found — install from https://ffmpeg.org/download.html")
            all_ok = False

    try:
        import whisper  # noqa: F401
        print("  ✔ Whisper found")
    except ImportError:
        print("  ✗ Whisper NOT found — run: pip install openai-whisper")
        all_ok = False

    return all_ok


# ── Video info ────────────────────────────────────────────────────────────────

def get_video_info(video_path):
    """Return (width, height, duration_str) for the input video."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,duration",
            "-of", "csv=p=0",
            video_path,
        ],
        capture_output=True,
        text=True,
    )
    parts = result.stdout.strip().split(",")
    w   = int(parts[0])
    h   = int(parts[1])
    dur = float(parts[2]) if len(parts) > 2 else 0
    m, s = int(dur // 60), int(dur % 60)
    return w, h, f"{m:02d}:{s:02d}"


# ── User input ────────────────────────────────────────────────────────────────

def ask_choice(prompt, valid_options):
    """Ask the user to pick one option from a list. Loops until valid."""
    while True:
        try:
            choice = input(f"\n  {prompt}: ").strip().upper()
        except EOFError:
            choice = valid_options[0]
        if choice in valid_options:
            return choice
        print(f"  ✗  Invalid — please enter one of: {' / '.join(valid_options)}")


# ── Banner ────────────────────────────────────────────────────────────────────

def print_banner():
    print()
    print("  ╔══════════════════════════════════════════════════════════╗")
    print("  ║            🎬  SUBTITLING ENGINE  v1.0.0               ║")
    print("  ║   Karaoke subtitle generator — zero tokens, 100% local  ║")
    print("  ╚══════════════════════════════════════════════════════════╝")
    print()

def print_phase(number, title):
    print(f"\n── PHASE {number} — {title} {'─' * max(1, 50 - len(title))}\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="🎬 Subtitling Engine — Karaoke subtitle generator"
    )
    parser.add_argument("video",
        help="Path to input video file (.mp4)")
    parser.add_argument("--model", default=None,
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: from config.json)")
    parser.add_argument("--lang", default=None,
        help="Language code (es, en, fr...) — default: auto-detect")
    parser.add_argument("--smart-correct", action="store_true",
        help="Use LLM to apply natural language corrections (requires API key)")
    args = parser.parse_args()

    print_banner()
    config = load_config()

    # ──────────────────────────────────────────────────────────────────────────
    # PHASE 1 — Setup verification
    # ──────────────────────────────────────────────────────────────────────────
    print_phase(1, "Setup verification")

    if not check_tools():
        print("\n  ✗  One or more required tools are missing. Exiting.\n")
        sys.exit(1)

    video_path = os.path.abspath(args.video)
    if not os.path.isfile(video_path):
        print(f"\n  ✗  File not found: {video_path}\n")
        sys.exit(1)

    w, h, duration          = get_video_info(video_path)
    folders, video_name     = create_output_folders(video_path)

    print(f"\n  ✔ File      : {os.path.basename(video_path)}")
    print(f"    Resolution : {w}x{h}")
    print(f"    Duration   : {duration}")
    print(f"    Output dir : {folders['base']}")

    # ──────────────────────────────────────────────────────────────────────────
    # PHASE 2 — Transcription
    # ──────────────────────────────────────────────────────────────────────────
    print_phase(2, "Transcription")

    model_size = args.model or config["whisper"]["model"]
    language   = args.lang  or config["whisper"]["language"]
    if language == "auto":
        language = None

    segments, _ = transcribe.run(
        video_path, folders["base"], video_name, model_size, language
    )

    # ──────────────────────────────────────────────────────────────────────────
    # PHASE 3 — Review & correct transcription
    # ──────────────────────────────────────────────────────────────────────────
    print_phase(3, "Review & correct transcription")

    segments = correct.run(segments, folders["base"], video_name)

    # ──────────────────────────────────────────────────────────────────────────
    # PHASE 4 — Style selection
    # ──────────────────────────────────────────────────────────────────────────
    print_phase(4, "Style selection")
    print("  Generating style previews...")

    preview.generate_style_previews(
        video_path, segments, folders, video_name, config
    )

    print(f"\n  ▶ Open the clips in:\n    {folders['style']}\n")
    print("  [A] Classic  — white text, yellow highlight, black outline")
    print("  [B] Bold     — thicker outline, stronger yellow")
    print("  [C] Box      — dark background behind text, yellow highlight")
    print("  [D] Glow     — soft glow on current word")

    style_map    = {"A": "classic", "B": "bold", "C": "box", "D": "glow"}
    style_choice = ask_choice("Your choice (A/B/C/D)", list(style_map.keys()))
    chosen_style = style_map[style_choice]
    print(f"  ✔ Style: {chosen_style}")

    # ──────────────────────────────────────────────────────────────────────────
    # PHASE 5 — Size selection
    # ──────────────────────────────────────────────────────────────────────────
    print_phase(5, "Size selection")
    print(f"  Generating size previews with '{chosen_style}' style...")

    preview.generate_size_previews(
        video_path, segments, folders, video_name, chosen_style, config
    )

    print(f"\n  ▶ Open the clips in:\n    {folders['size']}\n")
    print("  [S] Small  —  90px")
    print("  [M] Medium — 120px")
    print("  [L] Large  — 150px")

    size_map    = {"S": "small", "M": "medium", "L": "large"}
    size_choice = ask_choice("Your choice (S/M/L)", list(size_map.keys()))
    chosen_size = size_map[size_choice]
    print(f"  ✔ Size: {chosen_size}")

    # ──────────────────────────────────────────────────────────────────────────
    # PHASE 6 — Position selection
    # ──────────────────────────────────────────────────────────────────────────
    print_phase(6, "Position selection")
    print(f"  Generating position previews with '{chosen_style}' + '{chosen_size}'...")

    preview.generate_position_previews(
        video_path, segments, folders, video_name,
        chosen_style, chosen_size, config
    )

    print(f"\n  ▶ Open the clips in:\n    {folders['position']}\n")
    print("  [1] Bottom       — close to the bottom edge")
    print("  [2] Lower-third  — classic TV / social media")
    print("  [3] Mid-low      — more centered")

    pos_map      = {"1": "bottom", "2": "lowerthird", "3": "midlow"}
    pos_choice   = ask_choice("Your choice (1/2/3)", list(pos_map.keys()))
    chosen_pos   = pos_map[pos_choice]
    print(f"  ✔ Position: {chosen_pos}")

    # ──────────────────────────────────────────────────────────────────────────
    # PHASE 7 — Final render
    # ──────────────────────────────────────────────────────────────────────────
    print_phase(7, "Final render")
    print(f"  Style    : {chosen_style}")
    print(f"  Size     : {chosen_size}")
    print(f"  Position : {chosen_pos}")
    print()

    # Generate final ASS file
    ass_path = os.path.join(folders["base"], f"{video_name}_karaoke.ass")
    generate_ass.generate(
        segments, chosen_style, chosen_size, chosen_pos,
        w, h, ass_path
    )

    # Render final video
    output_path = os.path.join(folders["final"], f"{video_name}_karaoke.mp4")
    render.run(
        video_path, ass_path, output_path,
        ffmpeg_preset = config["ffmpeg"]["preset"],
        ffmpeg_crf    = config["ffmpeg"]["crf"],
    )

    # ── Done ──────────────────────────────────────────────────────────────────
    print()
    print("  ╔══════════════════════════════════════════════════════════╗")
    print("  ║                    ✅  ALL DONE!                        ║")
    print("  ╚══════════════════════════════════════════════════════════╝")
    print(f"\n  Final video: {output_path}\n")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  ⚠  Interrupted by user. Exiting.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n  ✗  Unexpected error: {e}\n")
        sys.exit(1)
