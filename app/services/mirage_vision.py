"""Optional Mirage (Cactus Compute) vision helpers: burned-in text/logo boxes, main-subject box, shot class.

Mirage is a ~23 MB on-device vision model (`pip install cactus-compute`). It finds and OCRs overlays and gives
object boxes, but it has NO identities: it cannot tell which player is on screen (the CLIP gate does that).
Labels hallucinate ("woman in water" for a shirtless striker); trust the boxes, not the names.

Everything degrades to None / [] when cactus is not installed, the same pattern as cv2 in craft.py.
Boxes in this module are fractions of the frame (0..1) as (x0, y0, x1, y1).
Results are cached by file content hash in storage/cache_mirage/, so re-checks are instant.
Measured on CPU (Windows laptop, 20 Nov 2026): ~1.3 s per frame. Use a few probe frames, not dense sampling.
"""
import hashlib
import json
import os
from typing import List, Optional, Tuple

os.environ.setdefault("CACTUS_TELEMETRY", "0")

try:
    import cactus  # type: ignore
    _HAS_MIRAGE = True
except Exception:  # pragma: no cover - optional dependency
    cactus = None
    _HAS_MIRAGE = False

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE = os.path.join(ROOT, "storage", "cache_mirage")

PLAYER = ("player", "jersey")
HUMAN = PLAYER + ("person", "man", "woman", "boy", "girl")
FOOTBALL_SCENE = ("soccer", "football", "stadium", "field", "pitch")
OVERLAY_OBJECTS = ("logo", "text overlay", "text", "text box", "text banner")

_model = None


def available() -> bool:
    return _HAS_MIRAGE


def _get_model():
    global _model
    if _model is None:
        _model = cactus.Mirage()
    return _model


def describe(path: str) -> Optional[dict]:
    """Raw Mirage describe() output for an image file (cached by content hash). None without cactus."""
    if not _HAS_MIRAGE or not os.path.exists(path):
        return None
    h = hashlib.md5(open(path, "rb").read()).hexdigest()
    os.makedirs(CACHE, exist_ok=True)
    cp = os.path.join(CACHE, h + ".json")
    if os.path.exists(cp):
        try:
            return json.load(open(cp, encoding="utf-8"))
        except Exception:
            pass
    r = _get_model().describe(path)
    for o in r.get("objects", []):  # masks are large and unused here
        o.pop("mask", None)
    json.dump(r, open(cp, "w", encoding="utf-8"))
    return r


def _frac(b) -> Tuple[float, float, float, float]:
    return (b[0] / 1000.0, b[1] / 1000.0, b[2] / 1000.0, b[3] / 1000.0)


def _area(b) -> float:
    return max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])


def text_furniture(m: dict) -> List[dict]:
    """Overlay candidates in one frame: OCR text in the top 20% / bottom 22% (score >= 0.35), plus logo/text-overlay
    objects in a corner. In-scene ad boards and shirt numbers also show up here; persistent_furniture() filters them."""
    out = []
    for t in (m or {}).get("text", []):
        b = _frac(t["bbox"])
        if t.get("score", 0) >= 0.35 and (b[3] <= 0.20 or b[1] >= 0.78):
            out.append({"box": b, "kind": "text", "text": t.get("string", "")})
    for o in (m or {}).get("objects", []):
        if o.get("name") in OVERLAY_OBJECTS:
            b = _frac(o["bbox"])
            corner_x = b[0] >= 0.85 or b[2] <= 0.15
            corner_y = b[3] <= 0.20 or b[1] >= 0.80
            if corner_x and corner_y:
                out.append({"box": b, "kind": "logo", "text": o.get("name", "")})
    return out


def _iou(a, b) -> float:
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    u = _area(a) + _area(b) - inter
    return inter / u if u > 0 else 0.0


def persistent_furniture(per_frame: List[List[dict]], min_frac: float = 0.5, iou: float = 0.5) -> List[dict]:
    """Boxes that recur in >= min_frac of a source's probe frames = burned-in overlays (captions, logos,
    header bars). Ad boards move with the camera and drop out. Returns the union box of each cluster."""
    clusters: List[dict] = []
    for fi, items in enumerate(per_frame):
        for it in items:
            for c in clusters:
                if _iou(c["box"], it["box"]) >= iou:
                    c["frames"].add(fi)
                    b = c["box"]
                    c["box"] = (min(b[0], it["box"][0]), min(b[1], it["box"][1]), max(b[2], it["box"][2]), max(b[3], it["box"][3]))
                    c["texts"].append(it["text"])
                    break
            else:
                clusters.append({"box": it["box"], "kind": it["kind"], "frames": {fi}, "texts": [it["text"]]})
    need = max(2, int(round(min_frac * len(per_frame))))
    return [{"box": c["box"], "kind": c["kind"], "seen": len(c["frames"]), "text": c["texts"][0]}
            for c in clusters if len(c["frames"]) >= need]


def subject_box(m: dict) -> Optional[Tuple[float, float, float, float]]:
    """Main subject: the largest human box if it covers >= 8% of the frame, else a score-weighted box around
    all human boxes. None when Mirage saw no person (common on tight torso close-ups)."""
    hs = [o for o in (m or {}).get("objects", []) if any(h in o.get("name", "") for h in HUMAN)]
    if not hs:
        return None
    big = max(hs, key=lambda o: _area(_frac(o["bbox"])) * o.get("score", 1))
    bb = _frac(big["bbox"])
    if _area(bb) >= 0.08:
        return bb
    tot = sum(o.get("score", 1) for o in hs) or 1.0
    cx = sum((_frac(o["bbox"])[0] + _frac(o["bbox"])[2]) / 2 * o.get("score", 1) for o in hs) / tot
    cy = sum((_frac(o["bbox"])[1] + _frac(o["bbox"])[3]) / 2 * o.get("score", 1) for o in hs) / tot
    return (cx - 0.02, cy - 0.05, cx + 0.02, cy + 0.05)


def shot_class(m: dict) -> str:
    """'player' (a person fills the frame), 'wide' (several players), 'crowd', or 'other' (graphics, outros).
    17/24 right on the 20 Nov test set vs 10/24 for craft.shot_size; the rule was fitted on that set."""
    objs = (m or {}).get("objects", [])
    scene = " ".join(str(v) for v in (m or {}).get("scene", {}).values()).lower()
    football = any(w in scene for w in FOOTBALL_SCENE)
    humans = [o for o in objs if any(h in o.get("name", "") for h in HUMAN)]
    players = [o for o in objs if any(h in o.get("name", "") for h in PLAYER)]
    big = max((_area(_frac(o["bbox"])) for o in (humans if football else players)), default=0.0)
    crowd = max((_area(_frac(o["bbox"])) for o in objs if o.get("name") == "crowd"), default=0.0)
    if big >= 0.15:
        return "player"
    if len(players) >= 2:
        return "wide"
    if crowd >= 0.4:
        return "crowd"
    return "other"
