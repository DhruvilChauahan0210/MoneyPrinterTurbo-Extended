#!/usr/bin/env python3
"""Finish one approved render from an existing task's cached local assets.

This utility never calls TTS, search, download, or LLM providers.
"""

from __future__ import annotations

import argparse
import json
import os
from glob import glob

from app.models.schema import VideoParams
from app.services import one_shot, task, video
from app.utils import utils


def render_cached(task_id: str) -> str:
    task_dir = utils.task_dir(task_id)
    manifest_path = os.path.join(task_dir, "script.json")
    with open(manifest_path, encoding="utf-8") as handle:
        manifest = json.load(handle)

    params = VideoParams(**manifest["params"])
    params.video_count = 1
    params._hook_text = (getattr(params, "hook_text", "") or "").strip()
    params._hook_image_path = os.path.join(task_dir, "hook_cover.jpg")
    params._enhanced_subtitle_path = os.path.join(task_dir, "subtitle_enhanced.json")

    audio_file = os.path.join(task_dir, "audio.mp3")
    from moviepy import AudioFileClip

    audio = AudioFileClip(audio_file)
    expected = float(audio.duration)
    audio.close()
    speech_end = video._speech_end_time(audio_file, expected)
    if speech_end:
        params._required_visual_duration = min(
            expected,
            float(speech_end) + float(getattr(params, "loop_tail_pad", 0.1) or 0.1),
        )

    clips = sorted(
        glob(os.path.join(task_dir, "temp-clip-*.mp4")),
        key=lambda item: int(os.path.basename(item).split("-")[-1].split(".")[0]),
    )
    if not clips:
        raise one_shot.OneShotError("cached task has no prepared timeline clips")

    subtitle_file = os.path.join(task_dir, "subtitle.srt")
    final_paths, _ = task.generate_final_videos(
        task_id=task_id,
        params=params,
        downloaded_videos=clips,
        audio_file=audio_file,
        subtitle_path=subtitle_file,
        video_script=manifest["script"],
    )
    if not final_paths:
        raise one_shot.OneShotError("cached render produced no final video")

    report = one_shot.validate_render(final_paths[0], expected)
    report_path = os.path.join(task_dir, "quality_report.json")
    with open(report_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
    print(f"GENERATED_VIDEO={final_paths[0]}")
    return final_paths[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("task_id")
    args = parser.parse_args()
    render_cached(args.task_id)
