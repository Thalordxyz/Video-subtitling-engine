"""
Step 04 — Preview Generator
Renders short preview clips (~5 sec) for each style / size / position option.
Uses the same FFmpeg pipeline as the final render for accuracy.
"""

import os
import subprocess
from engine.steps import generate_ass


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_video_dimensions(video_path):
    """Return (width, height) of the video."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "csv=p=0",
            video_path,
        ],
        capture_output=True,
        text=True,
    )
    parts = result.stdout.strip().split(",")
    return int(parts[0]), int(parts[1])


def _get_video_duration(video_path):
    """Return video duration in seconds."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=duration",
            "-of", "csv=p=0",
            video_path,
        ],
        capture_output=True,
        text=True,
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 30.0


def _safe_offset(video_path, desired_offset, duration):
    """Ensure the preview offset + duration does not exceed video length."""
    total = _get_video_duration(video_path)
    if desired_offset + duration > total:
        return max(0.0, total - duration)
    return desired_offset


def _render_clip(video_path, ass_path, output_path, start_offset, duration):
    """
    Render a short preview clip with burned-in subtitles.
    Uses cwd trick to avoid Windows path escaping issues in FFmpeg.
    """
    ass_dir  = os.path.dirname(ass_path)
    ass_name = os.path.basename(ass_path)

    cmd = [
        "ffmpeg", "-y",
        "-hwaccel", "dxva2",
        "-ss", str(start_offset),
        "-i", video_path,
        "-vf", f"ass={ass_name}",
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
        "-c:a", "copy",
        output_path,
    ]
    subprocess.run(cmd, capture_output=True, cwd=ass_dir)
    return output_path


def _make_preview(video_path, segments, output_folder, temp_ass_name,
                  style, size, position, out_filename,
                  video_w, video_h, start_offset, duration):
    """Generate one preview clip for a given style/size/position combination."""
    ass_path = os.path.join(output_folder, temp_ass_name)
    out_path = os.path.join(output_folder, out_filename)

    generate_ass.generate(
        segments, style, size, position, video_w, video_h, ass_path
    )
    _render_clip(video_path, ass_path, out_path, start_offset, duration)
    os.remove(ass_path)   # clean up temp ASS file

    print(f"    ✔ {out_filename}")
    return out_path


# ── Public functions ──────────────────────────────────────────────────────────

def generate_style_previews(video_path, segments, folders, video_name, config):
    """
    Generate 4 preview clips — one per subtitle style.
    Saved to: 01_style_selection/
    """
    w, h = _get_video_dimensions(video_path)
    dur  = config["preview"]["duration_seconds"]
    off  = _safe_offset(video_path, config["preview"]["start_offset_seconds"], dur)

    options = [
        ("classic", "A_classic"),
        ("bold",    "B_bold"),
        ("box",     "C_box"),
        ("glow",    "D_glow"),
    ]

    previews = []
    for style, label in options:
        path = _make_preview(
            video_path, segments,
            folders["style"],
            f"_tmp_{label}.ass",
            style, "medium", "lowerthird",
            f"preview_{label}.mp4",
            w, h, off, dur,
        )
        previews.append(path)

    return previews


def generate_size_previews(video_path, segments, folders, video_name,
                           chosen_style, config):
    """
    Generate 3 preview clips — one per font size (with chosen style).
    Saved to: 02_size_selection/
    """
    w, h = _get_video_dimensions(video_path)
    dur  = config["preview"]["duration_seconds"]
    off  = _safe_offset(video_path, config["preview"]["start_offset_seconds"], dur)

    options = ["small", "medium", "large"]
    previews = []

    for size in options:
        path = _make_preview(
            video_path, segments,
            folders["size"],
            f"_tmp_size_{size}.ass",
            chosen_style, size, "lowerthird",
            f"preview_{size}.mp4",
            w, h, off, dur,
        )
        previews.append(path)

    return previews


def generate_position_previews(video_path, segments, folders, video_name,
                                chosen_style, chosen_size, config):
    """
    Generate 3 preview clips — one per position (with chosen style + size).
    Saved to: 03_position_selection/
    """
    w, h = _get_video_dimensions(video_path)
    dur  = config["preview"]["duration_seconds"]
    off  = _safe_offset(video_path, config["preview"]["start_offset_seconds"], dur)

    options = ["bottom", "lowerthird", "midlow"]
    previews = []

    for pos in options:
        path = _make_preview(
            video_path, segments,
            folders["position"],
            f"_tmp_pos_{pos}.ass",
            chosen_style, chosen_size, pos,
            f"preview_{pos}.mp4",
            w, h, off, dur,
        )
        previews.append(path)

    return previews
