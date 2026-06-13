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
