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
    """Load an image file, or extract a middle frame from a video file, as PIL RGB."""
    from PIL import Image
    if path.lower().endswith((".mp4", ".mov", ".webm", ".mkv", ".avi")):
        import cv2
        cap = cv2.VideoCapture(path)
        try:
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
            if total > 1:
                cap.set(cv2.CAP_PROP_POS_FRAMES, total // 2)
            ok, frame = cap.read()
            if ok and frame is not None:
                return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        finally:
            cap.release()
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

        kept = [(s, p) for s, p in zip(sim, paths) if s >= min_score]
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

        chosen: List[int] = []
        prev = -1
        used_count = [0] * n_img
        for s in range(n_seg):
            scores = sim[s].copy()
            # Penalize images already used so variety is maximized — a clearly
            # better image can still win, but fresh images are strongly preferred.
            for i in range(n_img):
                scores[i] -= 0.12 * used_count[i]
            if prev >= 0 and n_img > 1:
                scores[prev] = -1e9            # never repeat back-to-back
            best = int(scores.argmax())
            chosen.append(best)
            used_count[best] += 1
            prev = best
            logger.debug(
                f"image_ranker: segment[{s}] '{segment_texts[s][:30]}' → img[{best}] "
                f"(score={sim[s][best]:.3f})"
            )
        distinct = len(set(chosen))
        logger.info(f"image_ranker: assigned {distinct} distinct images across {n_seg} segments")
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

        scored = []   # (margin, keep_bool, path)
        for i, p in enumerate(paths):
            pos_p = float(probs[i][:n_pos].max())
            neg_p = float(probs[i][n_pos:].max())
            m = pos_p - neg_p
            scored.append((m, m >= margin, p))

        kept = [p for m, ok, p in scored if ok]
        if len(kept) < min_keep:
            # back-fill with the highest-margin items so we never go empty
            ranked = sorted(scored, key=lambda x: -x[0])
            kept = [p for _, _, p in ranked[: min(min_keep, len(ranked))]]

        # preserve original order
        kept = [p for p in paths if p in set(kept)]

        dropped = len(paths) - len(kept)
        logger.info(
            f"image_ranker: subject gate kept {len(kept)}/{len(paths)} "
            f"(dropped {dropped} without {positive_labels}, margin>={margin})"
        )
        for m, ok, p in scored:
            if not ok and p not in kept:
                logger.debug(f"image_ranker: subject gate DROP (margin={m:.3f}) {os.path.basename(p)}")
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
