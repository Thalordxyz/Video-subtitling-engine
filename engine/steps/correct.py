"""
Step 02 — Correction
Interactive terminal interface for reviewing and correcting
the Whisper transcription at segment level.
"""

import os
import json


# ── Helpers ───────────────────────────────────────────────────────────────────

def _format_time(seconds):
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m:02d}:{s:05.2f}"


def _redistribute_words(text, start, end):
    """Evenly distribute word timestamps across a segment time range."""
    words = text.strip().split()
    n = len(words)
    if not n:
        return []
    dur = (end - start) / n
    return [
        {
            "word":  w,
            "start": round(start + i * dur, 3),
            "end":   round(start + (i + 1) * dur, 3),
        }
        for i, w in enumerate(words)
    ]


def _parse_time(time_str):
    """
    Parse a time string into seconds.
    Accepts: MM:SS.ms  or  SS.ms  or  MM:SS
    """
    time_str = time_str.strip().replace(",", ".")
    if ":" in time_str:
        parts = time_str.split(":")
        return float(parts[0]) * 60 + float(parts[1])
    return float(time_str)


def _display_segments(segments):
    """Print segments in a clean numbered table."""
    print()
    print("  " + "─" * 66)
    print(f"  {'#':<5} {'START → END':<22} TEXT")
    print("  " + "─" * 66)
    for i, seg in enumerate(segments):
        time_str = f"{_format_time(seg['start'])} → {_format_time(seg['end'])}"
        text     = seg["text"].strip()
        # Truncate long lines for display
        if len(text) > 38:
            text = text[:35] + "..."
        print(f"  {i + 1:<5} {time_str:<22} {text}")
    print("  " + "─" * 66)
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def run(segments, output_folder, video_name):
    """
    Show the transcription and let the user correct segments or add new ones.

    Args:
        segments      : list of segment dicts from Whisper
        output_folder : folder where corrected JSON will be saved
        video_name    : base name of the video (no extension)

    Returns:
        segments : corrected list of segment dicts
    """

    _display_segments(segments)

    # ── Apply corrections ─────────────────────────────────────────────────────
    print("  Enter corrections using format →  1: corrected text for segment 1")
    print("  Press Enter with no input to finish corrections.\n")

    while True:
        try:
            line = input("  > ").strip()
        except EOFError:
            break

        if not line:
            break

        if ":" not in line:
            print("  ✗  Format error — use:  1: corrected text\n")
            continue

        try:
            raw_idx, text = line.split(":", 1)
            idx  = int(raw_idx.strip()) - 1
            text = text.strip()

            if not (0 <= idx < len(segments)):
                print(f"  ✗  Segment {idx + 1} does not exist\n")
                continue

            seg             = segments[idx]
            seg["text"]     = " " + text
            seg["words"]    = _redistribute_words(text, seg["start"], seg["end"])
            print(f"  ✔  Segment {idx + 1} updated\n")

        except (ValueError, IndexError):
            print("  ✗  Format error — use:  1: corrected text\n")

    # ── Add missing segments ──────────────────────────────────────────────────
    while True:
        try:
            answer = input("\n  Do you want to add a missing segment? (yes/no): ").strip().lower()
        except EOFError:
            break

        if answer in ("no", "n", ""):
            break

        if answer not in ("yes", "y"):
            print("  ✗  Please type yes or no")
            continue

        try:
            start_str = input("  Start time (example → 00:42.00): ").strip()
            end_str   = input("  End time   (example → 00:45.50): ").strip()
            text      = input("  Text: ").strip()

            start = _parse_time(start_str)
            end   = _parse_time(end_str)

            if end <= start:
                print("  ✗  End time must be after start time\n")
                continue

            new_seg = {
                "id":    len(segments),
                "start": start,
                "end":   end,
                "text":  " " + text,
                "words": _redistribute_words(text, start, end),
            }
            segments.append(new_seg)
            segments.sort(key=lambda s: s["start"])
            print(f"  ✔  Segment added: {_format_time(start)} → {_format_time(end)}\n")

        except Exception as e:
            print(f"  ✗  Error: {e}\n")

    # ── Save corrected JSON ───────────────────────────────────────────────────
    json_path = os.path.join(output_folder, f"{video_name}_corrected.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"segments": segments}, f, ensure_ascii=False, indent=2)

    print(f"\n  ✔  Corrections saved: {json_path}")
    return segments
