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


def _embed_texts(texts: List[str]):
    import torch
    inputs = _clip_processor(text=texts, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        emb = _clip_model.get_text_features(**inputs)
    emb = emb / emb.norm(p=2, dim=-1, keepdim=True)
    return emb.cpu()


def _embed_images(paths: List[str]):
    from PIL import Image
    import torch
    imgs = []
    for p in paths:
        try:
            imgs.append(Image.open(p).convert("RGB"))
        except Exception:
            imgs.append(Image.new("RGB", (224, 224)))
    inputs = _clip_processor(images=imgs, return_tensors="pt")
    with torch.no_grad():
        emb = _clip_model.get_image_features(**inputs)
    emb = emb / emb.norm(p=2, dim=-1, keepdim=True)
    return emb.cpu()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

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
