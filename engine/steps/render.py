"""
Step 05 — Final Render
Burns the ASS subtitle file permanently into the video using FFmpeg.
The original video is never modified.
"""

import os
import subprocess


def run(video_path, ass_path, output_path, ffmpeg_preset="ultrafast", ffmpeg_crf=22):
    """
    Render the final video with burned-in karaoke subtitles.

    Args:
        video_path     : absolute path to the original video
        ass_path       : absolute path to the final ASS subtitle file
        output_path    : absolute path for the output video
        ffmpeg_preset  : libx264 speed preset (ultrafast recommended)
        ffmpeg_crf     : quality level — lower = better (18–28 recommended)

    Returns:
        output_path : path to the rendered video
    """

    # Use cwd trick to avoid Windows path escaping issues in the ass filter
    ass_dir  = os.path.dirname(ass_path)
    ass_name = os.path.basename(ass_path)

    cmd = [
        "ffmpeg", "-y",
        "-hwaccel", "dxva2",
        "-i", video_path,
        "-vf", f"ass={ass_name}",
        "-c:v", "libx264",
        "-preset", ffmpeg_preset,
        "-crf", str(ffmpeg_crf),
        "-c:a", "copy",
        output_path,
    ]

    print("  Running FFmpeg...")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ass_dir)

    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg failed with exit code {result.returncode}.\n"
            f"Error output:\n{result.stderr[-2000:]}"
        )

    size_mb = os.path.getsize(output_path) / (1024 * 1024)

    print(f"  ✔ Done!")
    print(f"    Output : {output_path}")
    print(f"    Size   : {size_mb:.1f} MB")

    return output_path
