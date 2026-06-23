"""
CLIP-based image-to-script ranker (Task 1).
Ranks downloaded local images so each appears during the script sentence it best matches.
Falls back to original order silently when CLIP is unavailable.
"""
import re
import os
import io
from typing import List, Dict
from loguru import logger

# ---------------------------------------------------------------------------
# Sentence splitter (mirrors semantic_video.segment_script_into_sentences)
# ---------------------------------------------------------------------------

def _split_sentences(script: str, min_len: int = 20) -> List[str]:
    parts = re.split(r'[.!?]+', script)
    sentences = [s.strip() for s in parts if s.strip()]
    merged, buf = [], ""
    for s in sentences:
        buf = (buf + " " + s).strip() if buf else s
        if len(buf) >= min_len:
            merged.append(buf)
            buf = ""
    if buf:
        if merged:
            merged[-1] = merged[-1] + " " + buf
        else:
            merged.append(buf)
    return merged or [script]


# ---------------------------------------------------------------------------
# CLIP helpers (load once, reuse across calls)
# ---------------------------------------------------------------------------

_clip_model = None
_clip_processor = None
_clip_available = None   # None = untested, True/False = known


def _try_load_clip(model_name: str = "clip-vit-base-patch32"):
    global _clip_model, _clip_processor, _clip_available
    if _clip_available is False:
        return False
    if _clip_model is not None:
        return True
    try:
        import torch
        from transformers import CLIPModel, CLIPProcessor
        hf_name = {
            "clip-vit-base-patch32": "openai/clip-vit-base-patch32",
            "clip-vit-base-patch16": "openai/clip-vit-base-patch16",
        }.get(model_name, model_name)
        cache = os.path.expanduser("~/.cache/huggingface/transformers")
        _clip_processor = CLIPProcessor.from_pretrained(hf_name, cache_dir=cache, use_fast=False)
        _clip_model = CLIPModel.from_pretrained(hf_name, cache_dir=cache).to("cpu")
        _clip_available = True
        logger.info(f"image_ranker: CLIP model loaded ({model_name})")
        return True
    except Exception as e:
        _clip_available = False
        logger.warning(f"image_ranker: CLIP unavailable ({e}), using original image order")
        return False


def _as_tensor(emb):
    # transformers v5 wraps get_*_features output in a ModelOutput;
    # its pooler_output is the projected joint-space embedding
    return emb.pooler_output if hasattr(emb, "pooler_output") else emb


def _embed_texts(texts: List[str]):
    import torch
    inputs = _clip_processor(text=texts, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        emb = _as_tensor(_clip_model.get_text_features(**inputs))
    emb = emb / emb.norm(p=2, dim=-1, keepdim=True)
    return emb.cpu()


def _load_media_as_image(path: str):
    """Load an image file, or extract a middle frame from a video file, as PIL RGB.

    Video frames are pulled with ffmpeg (always present in this env) so we don't
    depend on opencv/cv2 — when cv2 was missing this silently returned blank
    frames, making every clip embed identically and get gated out.
    """
    from PIL import Image
    if path.lower().endswith((".mp4", ".mov", ".webm", ".mkv", ".avi")):
        import io, subprocess
        # Probe duration so we can grab a frame from the middle (more representative).
        ss = 1.0
        try:
            out = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", path],
                capture_output=True, text=True, timeout=20,
            ).stdout.strip()
            dur = float(out)
            if dur > 0:
                ss = max(0.0, dur / 2.0)
        except Exception:
            pass
        try:
            r = subprocess.run(
                ["ffmpeg", "-v", "error", "-ss", f"{ss:.2f}", "-i", path,
                 "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                capture_output=True, timeout=40,
            )
            if r.returncode == 0 and r.stdout:
                return Image.open(io.BytesIO(r.stdout)).convert("RGB")
        except Exception as e:
            logger.debug(f"image_ranker: ffmpeg frame extract failed for {path}: {e}")
        raise ValueError(f"could not extract frame from {path}")
    return Image.open(path).convert("RGB")


def extract_video_frame(video_path: str, out_path: str) -> str:
    """Save a middle frame of a video to out_path (jpg). Returns out_path or ''."""
    try:
        img = _load_media_as_image(video_path)
        img.save(out_path, "JPEG", quality=92)
        return out_path
    except Exception as e:
        logger.warning(f"image_ranker: frame extraction failed for {video_path}: {e}")
        return ""


def _sharpness(img) -> float:
    """Variance-of-gradient sharpness (no cv2). Motion-blurred frames score low."""
    import numpy as np
    g = np.asarray(img.convert("L"), dtype="float32")
    gx = np.diff(g, axis=1)
    gy = np.diff(g, axis=0)
    return float(gx.var() + gy.var())


def pick_sharp_subject_frame(video_paths, cover_term, out_path,
                             n_samples: int = 6,
                             prefer_substr: str = "/auto/",
                             model_name: str = "clip-vit-base-patch32"):
    """
    Find the best HOOK moment across REAL-footage clips: sample frames from each
    clip, score each by CLIP match to `cover_term` AND sharpness, save the winning
    frame, and report which clip/timestamp it came from (so the hook card can play
    that moving clip, not just a still).

    Only auto-fetched footage (paths containing `prefer_substr`) is considered —
    those are reliably the actual player. Stock clips (Pexels) and photos are
    excluded so the hook is never a generic look-alike.

    Returns (jpg_path, source_clip_path, start_time) or ('', '', 0.0) on failure.
    """
    import io, subprocess
    from PIL import Image
    vids = [p for p in (video_paths or [])
            if p.lower().endswith((".mp4", ".mov", ".webm", ".mkv", ".avi"))]
    auto = [p for p in vids if prefer_substr in p.replace("\\", "/")]
    if auto:
        vids = auto
    if not vids or not _try_load_clip(model_name):
        return "", "", 0.0
    try:
        import torch
        import numpy as np
        txt = _embed_texts([cover_term])
        cand_imgs, cand_meta = [], []
        for v in vids:
            dur = 0.0
            try:
                dur = float(subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "default=noprint_wrappers=1:nokey=1", v],
                    capture_output=True, text=True, timeout=15).stdout.strip())
            except Exception:
                pass
            if dur <= 0:
                dur = 3.0
            for k in range(n_samples):
                t = dur * (k + 0.5) / n_samples
                r = subprocess.run(
                    ["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", v,
                     "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                    capture_output=True, timeout=30)
                if r.returncode == 0 and r.stdout:
                    im = Image.open(io.BytesIO(r.stdout)).convert("RGB")
                    cand_imgs.append(im)
                    cand_meta.append((v, t))
        if not cand_imgs:
            return "", "", 0.0
        inputs = _clip_processor(images=cand_imgs, return_tensors="pt")
        with torch.no_grad():
            emb = _as_tensor(_clip_model.get_image_features(**inputs))
        emb = emb / emb.norm(p=2, dim=-1, keepdim=True)
        sims = torch.mm(txt, emb.T).numpy()[0]
        sharp = np.array([_sharpness(im) for im in cand_imgs])
        # Normalize sharpness to 0..1 and combine: relevance dominates, sharpness
        # breaks ties / penalizes motion blur.
        sN = (sharp - sharp.min()) / (sharp.max() - sharp.min() + 1e-6)
        score = sims + 0.12 * sN
        best = int(score.argmax())
        cand_imgs[best].save(out_path, "JPEG", quality=92)
        src_v, src_t = cand_meta[best]
        logger.info(f"image_ranker: hook frame from clip {os.path.basename(src_v)} "
                    f"@{src_t:.1f}s (sim={sims[best]:.3f}, sharp_n={sN[best]:.2f})")
        return out_path, src_v, float(src_t)
    except Exception as e:
        logger.warning(f"image_ranker: sharp hook-frame pick failed ({e})")
        return "", "", 0.0


def _embed_images(paths: List[str]):
    from PIL import Image
    import torch
    imgs = []
    for p in paths:
        try:
            imgs.append(_load_media_as_image(p))
        except Exception:
            imgs.append(Image.new("RGB", (224, 224)))
    inputs = _clip_processor(images=imgs, return_tensors="pt")
    with torch.no_grad():
        emb = _as_tensor(_clip_model.get_image_features(**inputs))
    emb = emb / emb.norm(p=2, dim=-1, keepdim=True)
    return emb.cpu()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def pick_best_media(paths: List[str], text: str, model_name: str = "clip-vit-base-patch32"):
    """
    Return (best_path, score) — the media item (image or video) whose CLIP embedding
    best matches `text`. Returns (None, 0.0) if CLIP is unavailable or paths is empty.
    """
    if not paths or not text or not _try_load_clip(model_name):
        return None, 0.0
    try:
        import torch
        text_emb = _embed_texts([text])          # (1, d)
        img_emb = _embed_images(paths)           # (n, d)
        sim = torch.mm(text_emb, img_emb.T).numpy()[0]  # (n,)
        best_i = int(sim.argmax())
        logger.info(
            f"image_ranker: best match for '{text[:60]}' → {paths[best_i]} (score={sim[best_i]:.3f})"
        )
        return paths[best_i], float(sim[best_i])
    except Exception as e:
        logger.warning(f"image_ranker: pick_best_media failed ({e})")
        return None, 0.0


def filter_by_relevance(
    paths: List[str],
    subject_text: str,
    min_score: float = 0.20,
    min_keep: int = 6,
    model_name: str = "clip-vit-base-patch32",
) -> List[str]:
    """
    Drop media whose CLIP similarity to the video subject is below min_score,
    so off-topic downloads (e.g. random DDG results) never reach the final video.
    Always keeps at least min_keep items (the highest-scoring ones).
    Falls back to the original list if CLIP is unavailable.
    """
    if not paths or not subject_text or not _try_load_clip(model_name):
        return paths
    try:
        import torch
        text_emb = _embed_texts([subject_text])
        img_emb = _embed_images(paths)
        sim = torch.mm(text_emb, img_emb.T).numpy()[0]

        # Video clips bypass the relevance threshold: they're fetched from
        # targeted searches and their wide, motion-blurred mid-frames score low
        # against a verbose subject sentence even when they're exactly on topic.
        _vid_ext = (".mp4", ".mov", ".webm", ".mkv", ".avi")
        kept = [(s, p) for s, p in zip(sim, paths)
                if s >= min_score or p.lower().endswith(_vid_ext)]
        if len(kept) < min_keep:
            ranked = sorted(zip(sim, paths), key=lambda x: -x[0])
            kept = ranked[: min(min_keep, len(ranked))]
        kept_paths = [p for _, p in sorted(kept, key=lambda x: paths.index(x[1]))]

        dropped = len(paths) - len(kept_paths)
        if dropped:
            logger.info(
                f"image_ranker: dropped {dropped}/{len(paths)} off-topic media "
                f"(score < {min_score} vs subject '{subject_text[:50]}')"
            )
        return kept_paths
    except Exception as e:
        logger.warning(f"image_ranker: relevance filter failed ({e}), keeping all media")
        return paths


def _graphic_stats(path: str):
    """Cheap visual stats used to tell real photos from graphics/posters/junk."""
    from PIL import Image
    import numpy as np
    img = Image.open(path).convert("RGB").resize((160, 160))
    arr = np.asarray(img)
    q = (arr >> 4).astype(int)                      # 16 levels/channel
    codes = (q[..., 0] << 8) | (q[..., 1] << 4) | q[..., 2]
    _, counts = np.unique(codes, return_counts=True)
    tot = codes.size
    dom = float(counts.max() / tot)                 # fraction in the single most common color
    nsig = int((counts / tot > 0.005).sum())        # number of colors with >0.5% area
    gray = np.asarray(img.convert("L")).astype(float)
    detail = float((np.abs(np.diff(gray, axis=1)).mean() + np.abs(np.diff(gray, axis=0)).mean()) / 2)
    g = np.asarray(img.convert("L"))
    border = np.concatenate([g[:12].ravel(), g[-12:].ravel()])
    dark_border = float((border < 40).mean())       # uniform dark bands → cutout/letterbox
    return dom, nsig, detail, dark_border


def is_graphic_image(path: str) -> bool:
    """
    True if the image looks like a graphic/poster/cutout/logo rather than a real
    photograph. Thresholds calibrated on real downloaded candidates: clean photos
    have low dominant-color share, many colors, no dark bands; graphics don't.
    """
    try:
        dom, nsig, detail, db = _graphic_stats(path)
    except Exception:
        return False
    if dom >= 0.45 or nsig <= 12 or db >= 0.70 or detail < 3.5:
        return True
    if db >= 0.45 and dom >= 0.30:        # poster: dark bands + a big flat region
        return True
    return False


def filter_graphics(paths: List[str], min_keep: int = 5) -> List[str]:
    """
    Drop graphics/posters/cutouts/logos, keeping only real photos. Never drops
    below min_keep (falls back to the original list) so we can't end up empty.
    """
    if not paths:
        return paths
    kept, dropped = [], []
    for p in paths:
        (dropped if is_graphic_image(p) else kept).append(p)
    if len(kept) < min_keep:
        logger.info(f"image_ranker: photo-quality filter would keep only {len(kept)} (<{min_keep}), keeping all")
        return paths
    if dropped:
        logger.info(f"image_ranker: photo-quality filter dropped {len(dropped)} graphic/poster images, kept {len(kept)} real photos")
    return kept


def assign_images_to_segments(
    image_paths: List[str],
    segment_texts: List[str],
    reuse_penalty: float = 0.12,
    video_bonus: float = 0.0,
    min_video_fraction: float = 0.0,
    model_name: str = "clip-vit-base-patch32",
) -> List[int]:
    """
    For each caption segment (in spoken order) pick the index of the image that
    best matches it (CLIP cosine similarity), avoiding using the same image two
    segments in a row. Images may repeat across non-adjacent segments when there
    are more segments than images.

    Returns a list of image indices, one per segment (same length as segment_texts).
    Falls back to a simple round-robin over images if CLIP is unavailable.
    """
    n_img = len(image_paths)
    n_seg = len(segment_texts)
    if n_img == 0 or n_seg == 0:
        return [0] * n_seg

    if not _try_load_clip(model_name):
        return [i % n_img for i in range(n_seg)]

    try:
        import torch
        text_emb = _embed_texts(segment_texts)     # (n_seg, d)
        img_emb = _embed_images(image_paths)        # (n_img, d)
        sim = torch.mm(text_emb, img_emb.T).numpy() # (n_seg, n_img)

        # Real video clips read as motion-blurred mid-frames, so their CLIP
        # text-match is systematically lower than crisp photos — without a nudge
        # the assigner picks stills every time. `video_bonus` tilts selection
        # toward real footage (motion retains far better) while a clearly superior
        # photo (e.g. a perfect face close-up) can still win.
        _vid_ext = (".mp4", ".mov", ".webm", ".mkv", ".avi")
        is_video = [p.lower().endswith(_vid_ext) for p in image_paths]
        vid_idx = [i for i, v in enumerate(is_video) if v]
        img_idx = [i for i, v in enumerate(is_video) if not v]

        # Decide which SEGMENTS should show real video. Crisp photos out-score
        # motion-blurred clip frames on CLIP every time, so a soft bonus is not
        # enough — we GUARANTEE coverage: pick the segments whose best clip fits
        # best (highest video sim) and force real footage there. The rest use
        # photos (great for the face/hook/portrait moments). This keeps motion on
        # screen — the real retention driver — without throwing away good stills.
        force_video_segs = set()
        if vid_idx and min_video_fraction > 0.0:
            target = min(len(vid_idx) and n_seg, int(round(min_video_fraction * n_seg)))
            best_vid_sim = [(max(sim[s][i] for i in vid_idx), s) for s in range(n_seg)]
            best_vid_sim.sort(reverse=True)
            force_video_segs = {s for _, s in best_vid_sim[:target]}

        chosen: List[int] = []
        prev = -1
        used_count = [0] * n_img
        for s in range(n_seg):
            scores = sim[s].copy()
            for i in range(n_img):
                scores[i] -= reuse_penalty * used_count[i]
                if is_video[i]:
                    scores[i] += video_bonus
            # Restrict the candidate pool for this segment to the chosen media type.
            pool = vid_idx if s in force_video_segs else (
                img_idx if (img_idx and s not in force_video_segs and force_video_segs) else list(range(n_img))
            )
            if not pool:
                pool = list(range(n_img))
            if prev >= 0 and len(pool) > 1 and prev in pool:
                scores[prev] = -1e9            # never repeat the same media back-to-back
            best = max(pool, key=lambda i: scores[i])
            chosen.append(best)
            used_count[best] += 1
            prev = best
        n_vid_used = sum(1 for c in chosen if is_video[c])
        distinct = len(set(chosen))
        logger.info(
            f"image_ranker: assigned {distinct} distinct media across {n_seg} segments "
            f"({n_vid_used} real video clips, {n_seg - n_vid_used} photos)"
        )
        return chosen
    except Exception as e:
        logger.warning(f"image_ranker: segment assignment failed ({e}), using round-robin")
        return [i % n_img for i in range(n_seg)]


def filter_by_subject_presence(
    paths: List[str],
    positive_labels: List[str],
    negative_labels: List[str] = None,
    margin: float = 0.05,
    min_keep: int = 4,
    abs_floor: float = 0.0,
    model_name: str = "clip-vit-base-patch32",
) -> List[str]:
    """
    Keep only media in which the target subject(s) actually appear.

    For each image we run a CLIP zero-shot classification over
    [positive_labels + negative_labels]. An image is kept only if the best
    POSITIVE label's probability beats the best NEGATIVE label's probability
    by at least `margin`. This drops "relevant-but-wrong" media — e.g. a random
    Argentina shirt, an empty stadium, a logo, a crowd — that the plain
    relevance filter lets through because it only matches the script *words*.

    Always keeps at least min_keep items (those with the highest positive margin)
    so a too-strict gate can never empty the video. Falls back to the input list
    if CLIP is unavailable or no positive labels are given.
    """
    if not paths or not positive_labels or not _try_load_clip(model_name):
        return paths

    negative_labels = negative_labels or [
        "a random soccer player",
        "an empty football stadium",
        "a football crowd",
        "a crowd of spectators waving flags",
        "people in winter coats watching an event",
        "a ski jump or winter sports venue",
        "an empty landscape or scenery with no people",
        "a sports logo",
        "a generic soccer photo",
    ]

    # Prefix with "a photo of" — CLIP zero-shot works better with templated labels
    def _tmpl(lbl: str) -> str:
        return lbl if lbl.lower().startswith(("a ", "an ", "the ")) else f"a photo of {lbl}"

    pos = [_tmpl(l) for l in positive_labels]
    neg = [_tmpl(l) for l in negative_labels]
    n_pos = len(pos)

    try:
        import torch
        label_emb = _embed_texts(pos + neg)        # (n_labels, d)
        img_emb = _embed_images(paths)             # (n_img, d)
        # CLIP logit scale (~100) then softmax → probabilities per image
        logits = torch.mm(img_emb, label_emb.T) * 100.0   # (n_img, n_labels)
        probs = torch.softmax(logits, dim=-1).numpy()

        _vid_ext = (".mp4", ".mov", ".webm", ".mkv", ".avi")
        scored = []   # (margin, pos_p, keep_bool, path)
        for i, p in enumerate(paths):
            pos_p = float(probs[i][:n_pos].max())
            neg_p = float(probs[i][n_pos:].max())
            m = pos_p - neg_p
            # Photos pass only if they (a) beat the best negative by `margin` AND
            # (b) actually look like the subject (pos_p ≥ abs_floor) — this blocks
            # random/off-topic stills.
            # Video clips get a LENIENT pass: they come from targeted player
            # searches and are wide action frames (player small, crowd in shot,
            # motion blur) that can't beat a tight face positive — yet they're
            # exactly the motion footage we want. Keep them unless a clip is
            # CLEARLY junk (a graphic/logo/infographic dominates by a wide margin).
            is_video = p.lower().endswith(_vid_ext)
            if is_video:
                ok = (neg_p - pos_p) < 0.35   # drop only obvious graphic/junk clips
            else:
                ok = (m >= margin) and (pos_p >= abs_floor)
            scored.append((m, pos_p, ok, p))

        kept = [p for m, pp, ok, p in scored if ok]
        if len(kept) < min_keep:
            # Back-fill toward min_keep, but NEVER below the absolute floor — better
            # to ship fewer images (the segment assigner reuses good ones) than to
            # pad with irrelevant photos that trigger swipe-away. Rank back-fill
            # candidates by positive-likeness, not just margin.
            floor_ok = [t for t in scored if (t[3].lower().endswith(_vid_ext) or t[1] >= abs_floor)
                        and t[3] not in set(kept)]
            ranked = sorted(floor_ok, key=lambda x: -x[1])
            for _, _, _, p in ranked:
                if len(kept) >= min_keep:
                    break
                kept.append(p)

        # preserve original order; guarantee we never return empty
        kept = [p for p in paths if p in set(kept)]
        if not kept:
            ranked_all = sorted(scored, key=lambda x: -x[1])
            kept = [p for _, _, _, p in ranked_all[: min(min_keep, len(ranked_all))]]
            kept = [p for p in paths if p in set(kept)]

        dropped = len(paths) - len(kept)
        logger.info(
            f"image_ranker: subject gate kept {len(kept)}/{len(paths)} "
            f"(dropped {dropped} without {positive_labels}, margin>={margin}, floor>={abs_floor})"
        )
        for m, pp, ok, p in scored:
            if p not in kept:
                logger.debug(f"image_ranker: subject gate DROP (margin={m:.3f} pos={pp:.3f}) {os.path.basename(p)}")
        return kept
    except Exception as e:
        logger.warning(f"image_ranker: subject gate failed ({e}), keeping all media")
        return paths


def rank_images_for_script(
    image_paths: List[str],
    script: str,
    model_name: str = "clip-vit-base-patch32",
    min_score: float = 0.18,
) -> List[str]:
    """
    Return image_paths re-ordered so each image aligns with the script sentence
    it best matches (CLIP cosine similarity).

    Falls back to original order if CLIP is unavailable or scoring fails.
    Always returns len(image_paths) paths (with repetition if needed).
    """
    if not image_paths:
        return image_paths

    if not _try_load_clip(model_name):
        return image_paths

    try:
        import torch
        sentences = _split_sentences(script, min_len=20)
        n_sent = len(sentences)
        n_img = len(image_paths)

        logger.info(f"image_ranker: ranking {n_img} images against {n_sent} sentences")

        text_emb = _embed_texts(sentences)   # (n_sent, d)
        img_emb = _embed_images(image_paths)  # (n_img, d)

        # cosine similarity matrix (n_sent × n_img)
        sim = torch.mm(text_emb, img_emb.T).numpy()  # (n_sent, n_img)

        # Greedy assignment: for each sentence pick best unused image
        assigned: List[str] = []
        used = set()
        last_idx = -1

        for s_idx in range(n_sent):
            scores = sim[s_idx].copy()
            # Suppress images used too recently (avoid two identical in a row)
            if last_idx >= 0:
                scores[last_idx] = -1

            # Among unused images pick highest score
            unused_candidates = [(scores[i], i) for i in range(n_img) if i not in used]
            if unused_candidates:
                best_score, best_i = max(unused_candidates)
            else:
                # All used — allow reuse, but not the last one
                all_candidates = [(scores[i], i) for i in range(n_img)]
                best_score, best_i = max(all_candidates)

            # Drop images that are completely irrelevant IF we have enough
            if best_score < min_score and len(assigned) >= n_sent:
                logger.debug(f"image_ranker: dropping image (score={best_score:.3f} < {min_score})")
                continue

            assigned.append(image_paths[best_i])
            used.add(best_i)
            last_idx = best_i

            logger.debug(
                f"image_ranker: sentence[{s_idx}] → img[{best_i}] score={best_score:.3f} "
                f"'{sentences[s_idx][:60]}'"
            )

        # Pad to cover full audio if we have more images than sentences
        if n_img > len(assigned):
            remaining = [p for p in image_paths if p not in assigned]
            assigned.extend(remaining)

        logger.info(f"image_ranker: ordered {len(assigned)} images for {n_sent} sentences")
        return assigned

    except Exception as e:
        logger.error(f"image_ranker: ranking failed ({e}), using original order")
        return image_paths
