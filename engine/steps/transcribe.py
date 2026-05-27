"""
Step 01 — Transcription
Runs Whisper locally with word-level timestamps.
No internet. No API. No tokens.
"""

import os
import json
import whisper


def run(video_path, output_folder, video_name, model_size="base", language=None):
    """
    Transcribe the audio from a video file using Whisper.

    Args:
        video_path    : absolute path to the input video
        output_folder : folder where whisper JSON will be saved
        video_name    : base name of the video (no extension)
        model_size    : whisper model (tiny/base/small/medium/large)
        language      : language code (es, en...) or None for auto-detect

    Returns:
        segments  : list of segment dicts with word-level timestamps
        json_path : path to the saved whisper JSON file
    """

    print(f"  Loading Whisper model '{model_size}'...")
    model = whisper.load_model(model_size)

    options = {"word_timestamps": True}
    if language:
        options["language"] = language

    print("  Transcribing audio — this may take a few minutes...")
    result = model.transcribe(video_path, **options)

    # Strip leading/trailing spaces from every word
    for seg in result["segments"]:
        for w in seg.get("words", []):
            w["word"] = w["word"].strip()

    # Save raw JSON
    json_path = os.path.join(output_folder, f"{video_name}_whisper.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    lang      = result.get("language", "unknown").upper()
    n_segs    = len(result["segments"])
    n_words   = sum(len(s.get("words", [])) for s in result["segments"])

    print(f"  ✔ Done — {n_segs} segments | {n_words} words | Language: {lang}")
    print(f"    Saved: {json_path}")

    return result["segments"], json_path
