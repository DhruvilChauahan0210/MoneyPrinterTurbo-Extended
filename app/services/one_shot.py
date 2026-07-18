"""Fail-closed, one-attempt generation controls.

The expensive pipeline is deliberately split into three phases:
1. validate the complete request without calling a provider;
2. atomically reserve the unique task invocation;
3. record every external/render stage and inspect the one final output.

Nothing in this module retries a provider or a render.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import random
import re
import shutil
import subprocess
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import config
from app.utils import utils


class OneShotError(RuntimeError):
    """A request cannot safely enter or continue the one-shot pipeline."""


_GENERATION_LOCK = threading.Lock()
_LOCK_HOLDER = {"task_id": None, "acquired_at": None}
# A render that's still holding the slot after this long almost certainly means
# a stuck/crashed worker rather than a real in-progress generation — surfaced as
# a log warning for operators, not auto-broken (breaking a live lock could let
# two generations write to the same task dir at once).
_STALE_HOLD_WARN_SECONDS = 30 * 60


@contextmanager
def generation_slot(task_id: str | None = None):
    """Allow only one strict generation in-process; never queue surprise spend.

    Fails immediately (no wait) when busy, by design — a bounded wait would
    turn a rejected duplicate request into a queued one, silently spending
    money/time the caller didn't ask for.
    """
    if not _GENERATION_LOCK.acquire(blocking=False):
        holder = _LOCK_HOLDER.get("task_id")
        held_for = time.time() - (_LOCK_HOLDER.get("acquired_at") or time.time())
        detail = f" (held by task {holder} for {held_for:.0f}s" if holder else ""
        if held_for > _STALE_HOLD_WARN_SECONDS:
            detail += "; this looks stale — check for a stuck/crashed worker"
        detail += ")" if holder else ""
        raise OneShotError(f"another one-shot generation is active; this request was not consumed{detail}")
    _LOCK_HOLDER["task_id"] = task_id
    _LOCK_HOLDER["acquired_at"] = time.time()
    try:
        yield
    finally:
        _LOCK_HOLDER["task_id"] = None
        _LOCK_HOLDER["acquired_at"] = None
        _GENERATION_LOCK.release()


def is_enabled(params) -> bool:
    value = getattr(params, "one_shot_mode", None)
    if value is None:
        value = config.app.get("one_shot_mode", True)
    return bool(value)


def apply_growth_profile(params) -> list[str]:
    """Apply deterministic channel decisions before fingerprinting/preflight."""
    changes = []
    if getattr(params, "loop_follow_tag", False):
        params.loop_follow_tag = False
        changes.append("removed persistent frame-zero FOLLOW tag")
    cta = (getattr(params, "cta_text", "") or "").strip()
    if cta.upper().startswith("FOLLOW FOR MORE"):
        params.cta_text = "FOLLOW FOR UNTOLD FOOTBALL STORIES ⚡"
        changes.append("replaced generic CTA with a channel promise")
    params._growth_profile_changes = changes
    return changes


def _params_dict(params) -> dict[str, Any]:
    if hasattr(params, "model_dump"):
        data = params.model_dump(mode="json")
    elif hasattr(params, "dict"):
        data = params.dict()
    else:
        data = dict(params)
    # Legacy/manual override flags are not part of the content identity.
    data.pop("one_shot_allow_retry", None)
    return data


def fingerprint(params) -> str:
    payload = json.dumps(
        _params_dict(params), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _words(text: str) -> list[str]:
    return re.findall(r"[\w’'-]+", text or "", flags=re.UNICODE)


def preflight(params, stop_at: str = "video") -> dict[str, Any]:
    """Validate a request without network/provider calls or ledger consumption."""
    errors: list[str] = []
    warnings: list[str] = []
    comparison = bool(getattr(params, "comparison_mode", False))

    if stop_at == "video" and int(getattr(params, "video_count", 1) or 1) != 1:
        errors.append("one-shot mode requires video_count=1")
    aspect = getattr(params, "video_aspect", "9:16")
    aspect = getattr(aspect, "value", aspect)
    if str(aspect) != "9:16":
        errors.append("channel one-shot profile requires portrait video_aspect=9:16")

    if not shutil.which("ffmpeg"):
        errors.append("ffmpeg is not available on PATH")
    if not shutil.which("ffprobe"):
        errors.append("ffprobe is not available on PATH")

    font_name = getattr(params, "font_name", "") or "STHeitiMedium.ttc"
    if not os.path.isfile(os.path.join(utils.font_dir(), font_name)):
        errors.append(f"font does not exist: {font_name}")

    if comparison:
        clips = getattr(params, "comparison_clips", None) or []
        if len(clips) < 2:
            errors.append("comparison_mode requires at least two explicit clips")
    else:
        subject = (getattr(params, "video_subject", "") or "").strip()
        script = (getattr(params, "video_script", "") or "").strip()
        terms = getattr(params, "video_terms", None)
        voice_name = (getattr(params, "voice_name", "") or "").strip()
        if not subject:
            errors.append("video_subject is required")
        if not script:
            errors.append("video_script must be supplied; one-shot mode will not buy an LLM draft")
        if getattr(params, "video_source", "") != "local" and not terms:
            errors.append("video_terms must be supplied; one-shot mode will not buy search-term generation")
        if not voice_name:
            errors.append("voice_name is required")

        word_count = len(_words(script))
        max_words = int(getattr(params, "one_shot_max_script_words", 90) or 90)
        if script and word_count < 12:
            errors.append(f"script is too thin for a complete story ({word_count} words; minimum 12)")
        if word_count > max_words:
            errors.append(f"script is too long ({word_count} words; maximum {max_words})")

        rate = max(0.5, float(getattr(params, "voice_rate", 1.0) or 1.0))
        estimated_seconds = word_count / (2.65 * rate) if word_count else 0.0
        max_audio_seconds = float(
            getattr(params, "one_shot_max_audio_seconds", 0.0) or 0.0
        )
        if max_audio_seconds > 0 and estimated_seconds > max_audio_seconds:
            errors.append(
                f"estimated narration is {estimated_seconds:.1f}s; "
                f"one-shot ceiling is {max_audio_seconds:.1f}s"
            )
        if estimated_seconds > 45:
            warnings.append(
                f"estimated narration is {estimated_seconds:.1f}s; reach Shorts usually need a tighter cut"
            )

        if getattr(params, "enable_hook_card", True):
            hook = (getattr(params, "hook_text", "") or "").strip()
            cover = (getattr(params, "hook_cover_term", "") or "").strip()
            if not hook:
                errors.append("hook_text is required; one-shot mode will not generate a second hook")
            if len(_words(hook)) > 9:
                errors.append("hook_text must be nine words or fewer")
            if not cover and not (getattr(params, "hook_image_path", "") or "").strip():
                errors.append("hook_cover_term or hook_image_path is required")
            if getattr(params, "hook_require_video", False) and not getattr(
                params, "hook_negative_labels", None
            ):
                warnings.append(
                    "moving hook has no contrastive negatives; text-heavy posters may outrank a face"
                )

        if getattr(params, "enable_cta", True):
            cta = (getattr(params, "cta_text", "") or "").strip().lower()
            if cta in {"follow for more", "follow for more ⚡", "subscribe for more"}:
                warnings.append(
                    "CTA is generic; a specific promise such as 'FOLLOW FOR UNTOLD FOOTBALL STORIES' should convert better"
                )

        pinned = []
        hook_image = (getattr(params, "hook_image_path", "") or "").strip()
        if hook_image:
            pinned.append(hook_image)
        pinned.extend(getattr(params, "intro_image_paths", None) or [])
        for pinned_path in pinned:
            if not os.path.isfile(pinned_path):
                errors.append(f"pinned image does not exist: {pinned_path}")

        if getattr(params, "video_source", "") == "local":
            for item in getattr(params, "video_materials", None) or []:
                url = getattr(item, "url", "")
                if not url or not os.path.isfile(url):
                    errors.append(f"local material does not exist: {url or '<empty>'}")

        risky = re.findall(
            r"\b(ended (?:his|her|their) career|never|always|first ever|on purpose)\b",
            script,
            flags=re.IGNORECASE,
        )
        if risky:
            warnings.append(
                "script contains an absolute/high-risk factual claim: "
                + ", ".join(sorted(set(x.lower() for x in risky)))
            )

    report = {
        "ok": not errors,
        "fingerprint": fingerprint(params),
        "errors": errors,
        "warnings": warnings,
    }
    if errors:
        raise OneShotError("preflight failed: " + "; ".join(errors))
    return report


def _probe(path: str) -> dict[str, Any]:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_streams", "-show_format",
            "-of", "json", path,
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise OneShotError(f"ffprobe rejected {path}: {result.stderr.strip()[:180]}")
    return json.loads(result.stdout)


_IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff")


def _frame_quality(path: str, duration: float) -> dict[str, Any]:
    """Cheap local blank/dark/blur protection using one representative frame."""
    from PIL import Image, ImageFilter, ImageStat

    # A static image has no real timeline — ffmpeg's image2 demuxer reports a
    # nominal ~1-frame "duration" for it, and seeking with -ss to ANY offset
    # (even 0) against that nominal duration returns zero bytes in this
    # environment. Only video files have a timeline worth seeking into.
    is_image = path.lower().endswith(_IMAGE_EXTS)
    cmd = ["ffmpeg", "-v", "error"]
    if not is_image:
        cmd += ["-ss", f"{max(0.0, duration / 2):.3f}"]
    cmd += [
        "-i", path, "-frames:v", "1", "-vf", "scale=180:-2",
        "-f", "image2pipe", "-vcodec", "png", "-",
    ]
    result = subprocess.run(cmd, capture_output=True, timeout=30)
    if result.returncode != 0 or not result.stdout:
        raise OneShotError(f"could not inspect representative frame: {path}")
    gray = Image.open(io.BytesIO(result.stdout)).convert("L")
    stats = ImageStat.Stat(gray)
    edges = ImageStat.Stat(gray.filter(ImageFilter.FIND_EDGES))
    return {
        "brightness": round(float(stats.mean[0]), 2),
        "contrast": round(float(stats.stddev[0]), 2),
        "edge_detail": round(float(edges.mean[0]), 2),
        "frame_signature": hashlib.sha1(gray.resize((16, 16)).tobytes()).hexdigest()[:16],
    }


def _media_source_key(media_path: str) -> str:
    """Return the original upload identity for an auto-footage cut/segment."""
    base = os.path.basename(media_path).lower()
    match = re.match(r"(.+?)_c\d+(?:\.|$)", base)
    return match.group(1) if match else base


def validate_media_plan(
    paths: list[str],
    audio_duration: float,
    min_media: int = 3,
    min_sources: int = 0,
    image_duration: float = 2.0,
) -> dict[str, Any]:
    """Fail before final rendering when the local visual plan is incomplete."""
    if len(paths or []) < min_media:
        raise OneShotError(f"media gate found {len(paths or [])} clips; minimum is {min_media}")

    total_duration = 0.0
    details = []
    unusable = []
    for media_path in paths:
        if not os.path.isfile(media_path) or os.path.getsize(media_path) < 1024:
            raise OneShotError(f"media gate found a missing/empty file: {media_path}")
        probe = _probe(media_path)
        stream = next((s for s in probe.get("streams", []) if s.get("codec_type") == "video"), None)
        if not stream:
            raise OneShotError(f"media gate found no video stream: {media_path}")
        width, height = int(stream.get("width") or 0), int(stream.get("height") or 0)
        is_image = media_path.lower().endswith(_IMAGE_EXTS)
        if is_image:
            # Stills have no real timeline — ffmpeg reports a nominal ~1-frame
            # "duration" (~1/fps) for any static image regardless of content,
            # and they haven't been reframed to portrait yet (preprocess_video
            # crops/blur-fills to portrait later, whatever the source shape).
            # Their actual on-screen time is decided per-segment afterward, so
            # only confirm the file itself is a readable image here.
            if not width or not height:
                raise OneShotError(f"media gate found an unreadable image: {media_path}")
            seek_duration = float(stream.get("duration") or probe.get("format", {}).get("duration") or 0)
            duration = float(image_duration)
        else:
            duration = float(stream.get("duration") or probe.get("format", {}).get("duration") or 0)
            if duration < 0.35:
                raise OneShotError(f"media clip is too short ({duration:.2f}s): {media_path}")
            if not width or not height or height <= width:
                raise OneShotError(f"media clip is not valid portrait footage ({width}x{height}): {media_path}")
            seek_duration = duration
        frame = _frame_quality(media_path, seek_duration)
        if (
            frame["brightness"] < 8
            or frame["brightness"] > 247
            or frame["contrast"] < 4
            or frame["edge_detail"] < 1.5
        ):
            unusable.append(media_path)
        total_duration += duration
        details.append(
            {
                "path": media_path,
                "duration": round(duration, 3),
                "size": [width, height],
                "frame_quality": frame,
            }
        )

    if len(unusable) > max(1, len(paths) // 3):
        raise OneShotError(
            f"visual gate rejected {len(unusable)}/{len(paths)} clips as blank, dark, or badly blurred"
        )

    unique_frames = len({item["frame_quality"]["frame_signature"] for item in details})
    if len(paths) >= 5 and unique_frames < max(3, int(len(paths) * 0.4)):
        raise OneShotError(
            f"visual variety gate found only {unique_frames} distinct frames across {len(paths)} clips"
        )

    unique_sources = len({_media_source_key(p) for p in paths})
    if min_sources > 0 and unique_sources < min_sources:
        raise OneShotError(
            f"visual source gate found only {unique_sources} original source videos; "
            f"{min_sources} are required before the only render"
        )

    # A tiny encode tolerance is allowed; the renderer itself must not loop clips.
    if total_duration + 0.2 < float(audio_duration):
        raise OneShotError(
            f"visual coverage is {total_duration:.2f}s for {audio_duration:.2f}s audio; render blocked"
        )
    return {
        "ok": True,
        "clip_count": len(paths),
        "visual_seconds": round(total_duration, 3),
        "low_quality_clips": unusable,
        "distinct_frame_signatures": unique_frames,
        "distinct_source_videos": unique_sources,
        "clips": details,
    }


def validate_render(path: str, expected_duration: float) -> dict[str, Any]:
    """Inspect the single output. Failure is reported; this never regenerates."""
    if not os.path.isfile(path) or os.path.getsize(path) < 10_000:
        raise OneShotError(f"final render is missing or empty: {path}")
    probe = _probe(path)
    streams = probe.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if not video or not audio:
        raise OneShotError("final render must contain both video and audio streams")
    width, height = int(video.get("width") or 0), int(video.get("height") or 0)
    duration = float(probe.get("format", {}).get("duration") or video.get("duration") or 0)
    if (width, height) != (1080, 1920):
        raise OneShotError(f"final render has wrong dimensions: {width}x{height}")
    if abs(duration - float(expected_duration)) > 1.0:
        raise OneShotError(
            f"final duration {duration:.2f}s differs from audio {expected_duration:.2f}s by more than 1s"
        )
    return {
        "ok": True,
        "path": path,
        "bytes": os.path.getsize(path),
        "duration": round(duration, 3),
        "size": [width, height],
        "has_audio": True,
    }


class OneShotGuard:
    def __init__(self, task_id: str, params, report: dict[str, Any]):
        self.task_id = task_id
        self.params = params
        self.fingerprint = report["fingerprint"]
        self.directory = Path(utils.storage_dir("one_shot_ledger", create=True))
        # One-shot applies to one requested task, not to a topic or script. Two
        # separately requested Shorts may intentionally use identical inputs and
        # must each receive a fresh provider/render pipeline. Re-entering the
        # *same task id* is what constitutes an accidental retry.
        self.path = self.directory / f"{self.task_id}.json"
        self.data = {
            "task_id": task_id,
            "fingerprint": self.fingerprint,
            "status": "reserved",
            "created_at": _now(),
            "updated_at": _now(),
            "stages": [],
            "preflight": report,
        }
        self._reserve()
        # Separately requested Shorts on the same topic get distinct edit
        # decisions, while a task remains reproducible for diagnostics.
        seed = hashlib.sha256(f"{self.fingerprint}:{self.task_id}".encode()).hexdigest()
        random.seed(int(seed[:16], 16))

    def _reserve(self) -> None:
        if self.path.exists():
            old = json.loads(self.path.read_text(encoding="utf-8"))
            raise OneShotError(
                "this task already consumed its one attempt "
                f"(task={old.get('task_id')}, status={old.get('status')}); "
                "create a new task for a newly requested Short"
            )
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        fd = os.open(self.path, flags, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(self.data, handle, ensure_ascii=False, indent=2)

    @classmethod
    def resume_after_duration_gate(cls, task_id: str, params):
        """Continue only the unclaimed stages of a duration-gated task.

        This is not a generation retry: the sole voice stage remains consumed,
        its cached file is reused locally, and the normal ``claim`` method still
        prevents acquisition or render from running more than once.
        """
        directory = Path(utils.storage_dir("one_shot_ledger", create=True))
        ledger_path = directory / f"{task_id}.json"
        if not ledger_path.exists():
            raise OneShotError(f"duration continuation ledger is missing: {task_id}")
        data = json.loads(ledger_path.read_text(encoding="utf-8"))
        stages = [item.get("name") for item in data.get("stages", [])]
        error = str(data.get("error", ""))
        if data.get("status") != "failed" or stages != ["voice_generation"]:
            raise OneShotError(
                "duration continuation requires one failed task with only the "
                "voice_generation stage consumed"
            )
        if "above the" not in error or "retention ceiling" not in error:
            raise OneShotError("task did not fail at the narration duration gate")
        if data.get("fingerprint") != fingerprint(params):
            raise OneShotError("cached task parameters changed; continuation blocked")

        guard = cls.__new__(cls)
        guard.task_id = task_id
        guard.params = params
        guard.fingerprint = data["fingerprint"]
        guard.directory = directory
        guard.path = ledger_path
        guard.data = data
        guard.data.pop("error", None)
        guard.data["status"] = "running"
        guard._write()
        return guard

    def claim(self, stage: str) -> None:
        if any(item["name"] == stage for item in self.data["stages"]):
            raise OneShotError(f"stage '{stage}' was already attempted; automatic retry blocked")
        self.data["stages"].append({"name": stage, "claimed_at": _now()})
        self.data["status"] = "running"
        self._write()

    def finish(self, status: str, **extra: Any) -> None:
        self.data["status"] = status
        self.data.update(extra)
        self._write()

    def _write(self) -> None:
        self.data["updated_at"] = _now()
        temp = self.path.with_suffix(".tmp")
        temp.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(temp, self.path)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
