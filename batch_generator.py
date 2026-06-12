#!/usr/bin/env python3
"""
Batch video generator (Task 7).

Usage:
    .venv/bin/python3 batch_generator.py batch.json

batch.json format:
{
    "defaults": {
        "video_aspect": "9:16",
        "voice_name": "en-US-AndrewNeural-Male",
        "video_source": "image_search",
        "video_clip_duration": 3,
        "font_name": "MicrosoftYaHeiBold.ttc"
    },
    "videos": [
        {
            "video_subject": "Maradona Hand of God",
            "video_script": "...",
            "video_terms": "Maradona 1986, ..."
        },
        {
            "video_subject": "Zidane Headbutt 2006"
        }
    ]
}
"""

import json
import sys
import os
from uuid import uuid4

# Add project root to path
root_dir = os.path.dirname(os.path.realpath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from loguru import logger
from app.models.schema import VideoParams, VideoConcatMode
from app.services import task as tm


def run_batch(batch_file: str):
    with open(batch_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    defaults = data.get("defaults", {})
    videos = data.get("videos", [])

    if not videos:
        logger.error("batch.json has no 'videos' list — nothing to do.")
        sys.exit(1)

    total = len(videos)
    results = []

    logger.info(f"Batch generator: {total} videos queued.")

    for i, entry in enumerate(videos, 1):
        merged = {**defaults, **entry}
        task_id = str(uuid4())
        subject = merged.get("video_subject", f"video_{i}")
        logger.info(f"\n{'='*60}\n[{i}/{total}] Starting: {subject}\ntask_id: {task_id}\n{'='*60}")

        try:
            params = VideoParams(**merged)
            result = tm.start(task_id=task_id, params=params)
            if result and result.get("videos"):
                video_path = result["videos"][0]
                logger.success(f"[{i}/{total}] DONE: {video_path}")
                results.append({"subject": subject, "status": "ok", "path": video_path})
            else:
                logger.error(f"[{i}/{total}] FAILED: {subject}")
                results.append({"subject": subject, "status": "failed", "path": None})
        except Exception as e:
            logger.error(f"[{i}/{total}] EXCEPTION for '{subject}': {e}")
            results.append({"subject": subject, "status": "error", "error": str(e), "path": None})

    # Summary
    print("\n" + "="*60)
    print(f"BATCH COMPLETE — {total} videos processed")
    print("="*60)
    ok = [r for r in results if r["status"] == "ok"]
    failed = [r for r in results if r["status"] != "ok"]
    for r in ok:
        print(f"  ✅  {r['subject']}\n      → {r['path']}")
    for r in failed:
        print(f"  ❌  {r['subject']} ({r['status']})")
    print("="*60)

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: .venv/bin/python3 batch_generator.py batch.json")
        sys.exit(1)
    run_batch(sys.argv[1])
