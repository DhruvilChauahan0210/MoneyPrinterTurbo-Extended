"""
Automatic REAL-footage sourcing via yt-dlp + ffmpeg.

Given a topic and a list of YouTube search queries, this:
  1. searches YouTube and downloads a few highlight videos (video-only, 720p,
     H.264, capped size — we use the pipeline's own TTS so no audio is needed),
  2. cuts each into short action clips, reframed to vertical 9:16,
  3. returns local clip paths.

These clips are injected into the existing image_search pool, so they flow
through the same CLIP photo/relevance/subject gates and timed-sync — only real,
on-subject MOTION footage survives. This is what replaces Ken-Burns stills with
actual highlight motion (the real retention unlock for Shorts).

Requires `yt-dlp` and `ffmpeg` on PATH (both ship with this repo's env). A JS
runtime (node) is auto-used when present to unlock HD formats.
"""
import os
import json
import shutil
import hashlib
import subprocess
from typing import List

from loguru import logger

VIDEO_EXTS = (".mp4", ".mov", ".webm", ".mkv", ".avi")


def _which(name: str) -> str:
    return shutil.which(name) or ""


def _ytdlp_bin() -> str:
    # Prefer the venv's yt-dlp, fall back to PATH.
    here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cand = os.path.join(here, ".venv", "bin", "yt-dlp")
    if os.path.exists(cand):
        return cand
    return _which("yt-dlp")


def _run(cmd: List[str], timeout: int = 240) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _ffprobe_duration(path: str) -> float:
    try:
        out = _run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", path,
        ], timeout=30).stdout.strip()
        return float(out)
    except Exception:
        return 0.0


def _download_one(query: str, dest_dir: str, max_height: int, max_filesize_mb: int,
                  use_node: bool, timeout: int) -> List[str]:
    """Search YouTube for `query` and download the top match (video-only, mp4/h264)."""
    ytdlp = _ytdlp_bin()
    if not ytdlp:
        logger.error("auto_footage: yt-dlp not found")
        return []
    before = set(os.listdir(dest_dir)) if os.path.isdir(dest_dir) else set()
    # Prefer H.264 (avc1) video-only at <=max_height; fall back to muxed mp4.
    fmt = (
        f"bestvideo[height<={max_height}][vcodec^=avc1][ext=mp4]/"
        f"bestvideo[height<={max_height}][ext=mp4]/"
        f"best[height<={max_height}][ext=mp4]/best[ext=mp4]/best"
    )
    # Pull the top 2 matches per query (not 1) and keep retries on — yt-dlp throttles
    # after a few rapid searches, so a single result per query leaves most queries
    # empty and the footage pool tiny (→ the same clips repeat). 2 distinct source
    # matches per working query is the cheapest way to raise visual variety.
    cmd = [
        ytdlp, "--no-playlist", "--socket-timeout", "20",
        "--no-warnings", "--ignore-errors",
        "--retries", "3", "--extractor-retries", "3",
        "--match-filter", "duration < 1200 & duration > 12",
        "-f", fmt,
        "--max-filesize", f"{max_filesize_mb}M",
        "-o", os.path.join(dest_dir, "%(id)s.%(ext)s"),
        f"ytsearch2:{query}",
    ]
    if use_node:
        cmd[1:1] = ["--js-runtimes", "node"]
    try:
        r = _run(cmd, timeout=timeout)
        if r.returncode != 0:
            logger.warning(f"auto_footage: yt-dlp non-zero for '{query[:40]}': {r.stderr.strip()[-180:]}")
    except subprocess.TimeoutExpired:
        logger.warning(f"auto_footage: yt-dlp timed out for '{query[:40]}'")
    after = set(os.listdir(dest_dir)) if os.path.isdir(dest_dir) else set()
    new = [os.path.join(dest_dir, f) for f in (after - before) if f.lower().endswith(VIDEO_EXTS)]
    return new


def _clip_is_dark(path: str, thresh: float = 22.0, black_floor: float = 9.0) -> bool:
    """True if the clip is mostly dark OR contains a near-black frame (a fade /
    cut-to-black transition). Highlight reels are full of fades between plays;
    even a brief black flash looks broken under captions and spikes swipe-away,
    so we sample densely and drop the clip if ANY frame goes near-black."""
    import io
    try:
        from PIL import Image
        import numpy as np
        dur = _ffprobe_duration(path) or 1.0
        vals = []
        for frac in (0.08, 0.22, 0.36, 0.5, 0.64, 0.78, 0.92):
            r = subprocess.run([
                "ffmpeg", "-v", "error", "-ss", f"{dur*frac:.2f}", "-i", path,
                "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-",
            ], capture_output=True, timeout=30)   # binary stdout (no text=True)
            if r.returncode == 0 and r.stdout:
                arr = np.asarray(Image.open(io.BytesIO(r.stdout)).convert("L"))
                vals.append(float(arr.mean()))
        if not vals:
            return False
        # Drop if: a near-black frame appears anywhere (fade), the whole clip is
        # dark, or the average is low.
        return (min(vals) < black_floor) or (max(vals) < thresh) or \
               ((sum(vals) / len(vals)) < thresh * 0.8)
    except Exception:
        return False


def _cut_vertical_clips(src: str, out_dir: str, base: str, clip_len: float,
                        n_clips: int, video_width: int, video_height: int,
                        head_skip: float = 6.0, tail_skip: float = 4.0) -> List[str]:
    """Cut `n_clips` evenly-spaced clips of `clip_len`s from src, reframed to 9:16."""
    dur = _ffprobe_duration(src)
    if dur <= 0:
        return []
    usable_start = head_skip
    usable_end = max(usable_start + clip_len, dur - tail_skip)
    span = usable_end - usable_start
    if span <= clip_len:
        offsets = [usable_start]
    else:
        # Evenly spaced, non-overlapping where possible.
        step = max(clip_len, span / n_clips)
        offsets = []
        t = usable_start
        while t + clip_len <= usable_end and len(offsets) < n_clips:
            offsets.append(t)
            t += step
    W, H = video_width, video_height
    # Center vertical crop to target aspect, then scale to WxH. -an drops audio.
    vf = (
        f"crop='min(iw,ih*{W}/{H})':'min(ih,iw*{H}/{W})',"
        f"scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},setsar=1"
    )
    made = []
    for i, off in enumerate(offsets):
        out = os.path.join(out_dir, f"{base}_c{i}.mp4")
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-ss", f"{off:.2f}", "-i", src, "-t", f"{clip_len:.2f}",
            "-an", "-vf", vf,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p", out,
        ]
        try:
            r = _run(cmd, timeout=120)
            if r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 10000:
                # Drop clips that landed on a fade/black transition — they look
                # broken under captions and spike swipe-away.
                if _clip_is_dark(out):
                    logger.debug(f"auto_footage: dropping dark/fade clip @{off:.1f}s")
                    try: os.remove(out)
                    except OSError: pass
                else:
                    made.append(out)
            else:
                logger.debug(f"auto_footage: ffmpeg cut failed @{off:.1f}s: {r.stderr.strip()[-120:]}")
        except subprocess.TimeoutExpired:
            logger.warning(f"auto_footage: ffmpeg cut timed out @{off:.1f}s")
    return made


def fetch_clips(
    task_id: str,
    queries: List[str],
    video_width: int,
    video_height: int,
    max_videos: int = 3,
    clip_len: float = 3.0,
    clips_per_video: int = 5,
    max_clips: int = 24,
    max_height: int = 720,
    max_filesize_mb: int = 80,
) -> List[str]:
    """
    Download + cut real highlight footage for `queries`. Returns a list of local
    vertical .mp4 clip paths (already 9:16). Best-effort: failures are skipped,
    never raised, so the pipeline can fall back to image_search.
    """
    if not queries:
        return []
    if not _which("ffmpeg"):
        logger.error("auto_footage: ffmpeg not found, skipping real footage")
        return []
    use_node = bool(_which("node") or _which("deno"))

    root = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "storage", "cache_videos", "auto",
    )
    key = hashlib.md5(("|".join(queries)).encode()).hexdigest()[:10]
    dl_dir = os.path.join(root, key, "src")
    cut_dir = os.path.join(root, key, "clips")
    os.makedirs(dl_dir, exist_ok=True)
    os.makedirs(cut_dir, exist_ok=True)

    # Reuse already-cut clips if this exact query set ran before (fast re-runs).
    existing = [os.path.join(cut_dir, f) for f in sorted(os.listdir(cut_dir))
                if f.lower().endswith(".mp4")] if os.path.isdir(cut_dir) else []
    if len(existing) >= min(max_clips, 6):
        logger.info(f"auto_footage: reusing {len(existing)} cached clips for this query set")
        return existing[:max_clips]

    logger.info(f"auto_footage: fetching real footage for {len(queries)} queries "
                f"(node_js={use_node}, target {max_height}p)")
    n_have = len([f for f in os.listdir(dl_dir) if f.lower().endswith(VIDEO_EXTS)])
    for q in queries:
        if n_have >= max_videos:
            break
        got = _download_one(q, dl_dir, max_height, max_filesize_mb, use_node, timeout=240)
        for g in got:
            logger.info(f"auto_footage: downloaded '{q[:42]}' → {os.path.basename(g)}")
        n_have = len([f for f in os.listdir(dl_dir) if f.lower().endswith(VIDEO_EXTS)])
    # Use every source video present in the cache dir (handles already-downloaded
    # files that yt-dlp skips on re-run).
    downloaded = sorted(os.path.join(dl_dir, f) for f in os.listdir(dl_dir)
                        if f.lower().endswith(VIDEO_EXTS))[:max_videos]
    if not downloaded:
        logger.warning("auto_footage: no source videos downloaded — falling back to image_search")
        return []

    clips: List[str] = []
    for src in downloaded:
        base = os.path.splitext(os.path.basename(src))[0]
        made = _cut_vertical_clips(
            src, cut_dir, base, clip_len, clips_per_video, video_width, video_height,
        )
        clips.extend(made)
        logger.info(f"auto_footage: cut {len(made)} clips from {os.path.basename(src)}")
        if len(clips) >= max_clips:
            break

    clips = clips[:max_clips]
    logger.success(f"auto_footage: produced {len(clips)} vertical highlight clips")
    return clips
