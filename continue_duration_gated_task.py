#!/usr/bin/env python3
"""Finish unclaimed stages using a duration-gated task's sole cached narration.

No TTS, LLM, or script call is made. The cached narration is gently compressed
locally, then footage acquisition and final render may each be claimed once.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess

from moviepy import AudioFileClip

from app.models.schema import VideoParams
from app.services import image_ranker, one_shot, task
from app.utils import utils


def _duration(path: str) -> float:
    clip = AudioFileClip(path)
    value = float(clip.duration)
    clip.close()
    return value


def _fit_cached_audio(source: str, output: str, ceiling: float) -> float:
    original = _duration(source)
    target = max(0.5, ceiling - 0.08)
    if original <= ceiling:
        return original
    tempo = original / target
    if not 0.5 <= tempo <= 2.0:
        raise one_shot.OneShotError(f"local audio-fit tempo is unsafe: {tempo:.3f}")
    result = subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error", "-i", source,
            "-filter:a", f"atempo={tempo:.8f}", "-b:a", "192k", output,
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0 or not os.path.isfile(output):
        raise one_shot.OneShotError(
            f"local narration fit failed: {result.stderr.strip()[-180:]}"
        )
    fitted = _duration(output)
    if fitted > ceiling:
        raise one_shot.OneShotError(
            f"locally fitted narration is still {fitted:.2f}s (ceiling {ceiling:.2f}s)"
        )
    return fitted


def continue_task(task_id: str, keep_original_audio: bool = False) -> str:
    task_dir = utils.task_dir(task_id)
    manifest_path = os.path.join(task_dir, "script.json")
    with open(manifest_path, encoding="utf-8") as handle:
        manifest = json.load(handle)
    params = VideoParams(**manifest["params"])
    guard = one_shot.OneShotGuard.resume_after_duration_gate(task_id, params)
    params._one_shot_guard = guard

    try:
        source_audio = os.path.join(task_dir, "audio.mp3")
        fitted_audio = os.path.join(task_dir, "audio-fitted.mp3")
        ceiling = float(getattr(params, "one_shot_max_audio_seconds", 0.0) or 0.0)
        if keep_original_audio:
            render_audio = source_audio
            audio_duration = _duration(source_audio)
        else:
            render_audio = fitted_audio
            audio_duration = _fit_cached_audio(source_audio, fitted_audio, ceiling)

        video_script = manifest["script"]
        video_terms = manifest["search_terms"]
        subtitle_path = task.generate_subtitle(
            task_id, params, video_script, None, render_audio
        )
        if params.subtitle_enabled and not subtitle_path:
            raise one_shot.OneShotError("local continuation produced no subtitles")

        downloaded = task.get_video_materials(
            task_id, params, video_terms, audio_duration
        )
        if not downloaded:
            raise one_shot.OneShotError("sole material acquisition produced no timeline")

        params._hook_text = (getattr(params, "hook_text", "") or "").strip()
        hook_image = getattr(params, "_best_image_path", None)
        if not hook_image:
            hook_image = image_ranker.extract_video_frame(
                downloaded[0], downloaded[0] + ".hook.jpg"
            ) or None
        params._hook_image_path = hook_image

        params._media_quality_report = one_shot.validate_media_plan(
            downloaded,
            audio_duration,
            min_media=int(getattr(params, "one_shot_min_media", 3) or 3),
            min_sources=int(getattr(params, "one_shot_min_visual_sources", 0) or 0),
        )
        guard.claim("final_render")
        final_paths, _ = task.generate_final_videos(
            task_id,
            params,
            downloaded,
            render_audio,
            subtitle_path,
            video_script,
        )
        if not final_paths:
            raise one_shot.OneShotError("sole continuation render produced no video")
        expected = getattr(params, "_rendered_duration", None) or audio_duration
        report = one_shot.validate_render(final_paths[0], expected)
        report["media_plan"] = params._media_quality_report
        with open(os.path.join(task_dir, "quality_report.json"), "w", encoding="utf-8") as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2)
        guard.finish("complete", output=final_paths[0], quality_report=report)
        print(f"GENERATED_VIDEO={final_paths[0]}")
        return final_paths[0]
    except Exception as exc:
        guard.finish("failed", error=str(exc))
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("task_id")
    parser.add_argument(
        "--keep-original-audio",
        action="store_true",
        help="continue with the sole cached narration unchanged",
    )
    args = parser.parse_args()
    continue_task(args.task_id, keep_original_audio=args.keep_original_audio)
