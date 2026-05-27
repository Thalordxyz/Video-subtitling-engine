"""
Step 03 — ASS Subtitle File Generator
Builds an ASS (Advanced SubStation Alpha) karaoke subtitle file.

For each word in each segment, one subtitle event is created showing
the full segment text with only the current word highlighted in yellow.
"""

import os
import json


# ── Style and parameter maps ──────────────────────────────────────────────────

SIZES = {
    "small":  90,
    "medium": 120,
    "large":  150,
}

POSITIONS = {
    "bottom":      130,
    "lowerthird":  700,
    "midlow":     1400,
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_style(style_name):
    """Load style parameters from the styles JSON directory."""
    styles_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "styles"
    )
    style_path = os.path.join(styles_dir, f"{style_name}_karaoke.json")
    with open(style_path, encoding="utf-8") as f:
        return json.load(f)


def _to_ass_time(seconds):
    """Convert seconds (float) to ASS time format H:MM:SS.cs"""
    h  = int(seconds // 3600)
    m  = int((seconds % 3600) // 60)
    cs = round((seconds % 60) * 100)
    return f"{h}:{m:02d}:{int(cs // 100):02d}.{cs % 100:02d}"


# ── Main ──────────────────────────────────────────────────────────────────────

def generate(segments, style_name, size_name, position_name,
             video_w, video_h, output_path):
    """
    Generate a karaoke ASS subtitle file.

    Args:
        segments      : corrected list of segment dicts with word timestamps
        style_name    : one of classic / bold / box / glow
        size_name     : one of small / medium / large
        position_name : one of bottom / lowerthird / midlow
        video_w       : video width in pixels
        video_h       : video height in pixels
        output_path   : full path for the output .ass file

    Returns:
        output_path : path to the generated ASS file
    """

    style     = _load_style(style_name)
    font_size = SIZES[size_name]
    margin_v  = POSITIONS[position_name]

    # ── Color override tags ───────────────────────────────────────────────────
    # Yellow highlight for the active word
    if style["glow_blur"] > 0:
        YEL = r"{\1c&H0000FFFF&\blur" + str(style["glow_blur"]) + r"}"
        WHT = r"{\1c&H00FFFFFF&\blur0}"
    else:
        YEL = r"{\1c&H0000FFFF&}"
        WHT = r"{\1c&H00FFFFFF&}"

    # ── ASS header ────────────────────────────────────────────────────────────
    header = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        f"PlayResX: {video_w}\n"
        f"PlayResY: {video_h}\n"
        "WrapStyle: 0\n"
        "ScaledBorderAndShadow: yes\n"
        "\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,Arial,{font_size},"
        f"&H00FFFFFF,&H0000FFFF,&H00000000,{style['back_colour']},"
        f"1,0,0,0,100,100,0,0,"
        f"{style['border_style']},{style['outline']},{style['shadow']},"
        f"2,30,30,{margin_v},1\n"
        "\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )

    # ── Build dialogue events ─────────────────────────────────────────────────
    events = []

    for seg in segments:
        words = seg.get("words", [])

        if not words:
            # No word timestamps — show full segment as a block
            t0 = _to_ass_time(seg["start"])
            t1 = _to_ass_time(seg["end"])
            events.append(
                f"Dialogue: 0,{t0},{t1},Default,,0,0,0,,{seg['text'].strip()}"
            )
            continue

        clean_words = [w["word"].strip() for w in words]

        for i, word_obj in enumerate(words):
            t0    = _to_ass_time(word_obj["start"])
            t_end = words[i + 1]["start"] if i + 1 < len(words) else seg["end"]
            t1    = _to_ass_time(t_end)

            # Build the line: all words white, current word yellow
            parts = []
            for j, cw in enumerate(clean_words):
                if j == i:
                    parts.append(YEL + cw + WHT)
                else:
                    parts.append(cw)

            line = " ".join(parts)
            events.append(f"Dialogue: 0,{t0},{t1},Default,,0,0,0,,{line}")

    # ── Write file ────────────────────────────────────────────────────────────
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(events))

    return output_path
