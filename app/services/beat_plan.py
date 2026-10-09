"""Beat-plan mode: one hand-verified media per spoken beat, placed on its exact words.

The shared-pool path (download one pool for the whole short, CLIP-gate it on WHO, then
let assign_images_to_segments pick per caption) cannot put the right picture on the
right line: CLIP has no idea who "Bella" is, so on the 8 Oct Bella build "Ronaldo named
her Bella" landed on a stranger in a Portugal shirt and "the first time" on his son.
The competitor short it was benchmarked against picks one visual per ~1.1s phrase.

A beat plan is that, written down. Each beat is a contiguous slice of video_script
(`says`) with the media chosen for it (`media`, filled in after beat_source.py has
sourced and contact-sheeted candidates). When every beat has media on disk, task.py
skips the pool, the gates and the assigner entirely and renders this timeline.
"""

import json
import os
import re
from typing import List, Optional, Tuple

from loguru import logger

from app.utils import utils

_VIDEO_EXTS = (".mp4", ".mov", ".webm", ".mkv", ".avi")


def _norm(word: str) -> str:
    return re.sub(r"[^a-z0-9]", "", word.lower())


def _tokens(text: str) -> List[str]:
    return [t for t in (_norm(w) for w in text.split()) if t]


def is_active(params) -> bool:
    plan = getattr(params, "beat_plan", None) or []
    if not plan:
        return False
    missing = [i + 1 for i, b in enumerate(plan)
               if not (b.get("media") and os.path.exists(b["media"]))]
    if missing:
        logger.warning(f"beat plan: beats {missing} have no media on disk; "
                       f"run beat_source.py and pick first. Using the shared pool instead.")
        return False
    return True


def _spoken_words(task_id: str) -> List[Tuple[str, float]]:
    path = os.path.join(utils.task_dir(task_id), "subtitle_enhanced.json")
    with open(path, "r", encoding="utf-8") as f:
        segments = json.load(f)
    words = []
    for seg in segments:
        seg_words = seg.get("words") or []
        if seg_words:
            for w in seg_words:
                tok = _norm(w.get("word", ""))
                if tok:
                    words.append((tok, float(w.get("start", seg.get("start_time", 0.0)))))
        else:
            # No word timing: spread the segment's words evenly across it.
            toks = _tokens(seg.get("text", ""))
            st, en = float(seg.get("start_time", 0.0)), float(seg.get("end_time", 0.0))
            for k, tok in enumerate(toks):
                words.append((tok, st + (en - st) * k / max(1, len(toks))))
    return words


def _renderable(task_id: str, media: str, idx: int, min_width: int = 1080) -> str:
    """Upscale small stills before render. preprocess_video's low-resolution path
    (anything under 480px) emitted a ~0.04s clip instead of the planned duration: on
    the first beat-plan build two 406x720 photos lost 3.1s of picture and the one-shot
    coverage guard failed the render."""
    if media.lower().endswith(_VIDEO_EXTS):
        return media
    from PIL import Image
    with Image.open(media) as im:
        w, h = im.size
        if w >= min_width:
            return media
        scale = min_width / float(w)
        size = (int(w * scale) // 2 * 2, int(h * scale) // 2 * 2)
        out = os.path.join(utils.task_dir(task_id), f"beat_{idx + 1:02d}_up.jpg")
        im.convert("RGB").resize(size, Image.LANCZOS).save(out, "JPEG", quality=94)
    logger.info(f"beat plan: upscaled beat {idx + 1} still {w}x{h} -> {size[0]}x{size[1]}")
    return out


def build_timeline(task_id: str, params, audio_duration: float,
                   tail_guard: float = 0.35) -> Tuple[List[str], List[float]]:
    """Return (media paths, durations), one entry per beat, covering the narration."""
    plan = params.beat_plan
    words = _spoken_words(task_id)
    if not words:
        raise ValueError("beat plan: no spoken word timings to align against")

    # Walk the spoken words in order. Each beat starts where its first token is found
    # near the expected position, so a TTS/whisper token split ("2022," vs "twenty")
    # only shifts that one boundary instead of drifting every beat after it.
    starts, ptr = [], 0
    for i, beat in enumerate(plan):
        toks = _tokens(beat.get("says", ""))
        if not toks:
            raise ValueError(f"beat plan: beat {i + 1} has no `says` text")
        found = None
        for off in sorted(range(-3, 6), key=abs):
            j = ptr + off
            if 0 <= j < len(words) and words[j][0] == toks[0]:
                found = j
                break
        if found is None:
            found = min(ptr, len(words) - 1)
            logger.warning(f"beat plan: beat {i + 1} first word '{toks[0]}' not found near "
                           f"word {ptr}; starting at '{words[found][0]}'")
        starts.append(0.0 if i == 0 else words[found][1])
        ptr = found + len(toks)

    end_total = max(audio_duration or 0.0, words[-1][1]) + tail_guard
    durations = []
    for i, st in enumerate(starts):
        nxt = starts[i + 1] if i + 1 < len(starts) else end_total
        durations.append(max(0.4, nxt - st))
    paths = [_renderable(task_id, b["media"], i) for i, b in enumerate(plan)]

    # Shot-list times for beat_source.py --shotlist (keyed by script, like its reader).
    try:
        import hashlib
        tl = os.path.join(utils.storage_dir(), "beats", "timeline_"
                          + hashlib.md5((params.video_script or "").encode()).hexdigest()[:10]
                          + ".json")
        os.makedirs(os.path.dirname(tl), exist_ok=True)
        with open(tl, "w") as f:
            json.dump([[round(st, 2), round(d, 2)] for st, d in zip(starts, durations)], f)
    except Exception as e:
        logger.warning(f"beat plan: could not write shot-list timeline: {e}")

    for i, (b, st, d) in enumerate(zip(plan, starts, durations)):
        logger.info(f"beat {i + 1:02d} @{st:5.2f}s {d:4.2f}s  "
                    f"'{b['says'][:40]}' -> {os.path.basename(b['media'])}")
    logger.success(f"beat plan: {len(paths)} beats, {len(set(paths))} distinct media, "
                   f"avg {sum(durations) / len(durations):.2f}s per shot")
    return paths, durations


def hook_still(task_id: str, first_media: str) -> Optional[str]:
    """The hook card needs a still; pull a frame when beat 1 is a clip."""
    if not first_media.lower().endswith(_VIDEO_EXTS):
        return first_media
    from app.services import image_ranker
    return image_ranker.extract_video_frame(
        first_media, os.path.join(utils.task_dir(task_id), "beat_hook.jpg")) or None
