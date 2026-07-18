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

import argparse
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
from app.services import one_shot


def run_batch(batch_file: str, dry_run: bool = False):
    with open(batch_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    defaults = data.get("defaults", {})
    videos = data.get("videos", [])

    if not videos:
        logger.error("batch.json has no 'videos' list — nothing to do.")
        sys.exit(1)

    total = len(videos)
    results = []

    logger.info(f"Batch generator: {total} videos queued (one-shot preflight first).")

    # Validate the ENTIRE batch before the first provider call. This prevents a
    # malformed later entry from being discovered after an earlier entry spent.
    prepared = []
    for i, entry in enumerate(videos, 1):
        merged = {**defaults, **entry}
        subject = merged.get("video_subject", f"video_{i}")
        try:
            params = VideoParams(**merged)
            changes = one_shot.apply_growth_profile(params)
            report = one_shot.preflight(params)
            prepared.append((subject, params, report))
            logger.success(
                f"[{i}/{total}] PREFLIGHT OK: {subject} "
                f"({report['fingerprint'][:12]})"
            )
            for warning in report["warnings"]:
                logger.warning(f"[{i}/{total}] {warning}")
            for change in changes:
                logger.info(f"[{i}/{total}] growth profile: {change}")
        except Exception as exc:
            logger.error(f"[{i}/{total}] PREFLIGHT FAILED: {subject}: {exc}")
            results.append({"subject": subject, "status": "preflight_failed", "error": str(exc), "path": None})

    if results:
        logger.error("Batch blocked before generation because at least one preflight failed.")
        return results

    if dry_run:
        print(f"DRY_RUN_OK={total}")
        return [
            {"subject": subject, "status": "dry_run_ok", "fingerprint": report["fingerprint"], "path": None}
            for subject, _, report in prepared
        ]

    # Import the heavy rendering stack only after every zero-cost check passed.
    from app.services import task as tm

    for i, (subject, params, _) in enumerate(prepared, 1):
        task_id = str(uuid4())
        logger.info(f"\n{'='*60}\n[{i}/{total}] Starting: {subject}\ntask_id: {task_id}\n{'='*60}")

        try:
            result = tm.start(task_id=task_id, params=params)
            if result and result.get("videos"):
                video_path = result["videos"][0]
                logger.success(f"[{i}/{total}] DONE: {video_path}")
                print(f"GENERATED_VIDEO={video_path}")
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
    parser = argparse.ArgumentParser(description="Strict one-shot batch generator")
    parser.add_argument("batch_file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="run zero-cost validation only; does not create a ledger attempt",
    )
    args = parser.parse_args()
    batch_results = run_batch(args.batch_file, dry_run=args.dry_run)
    success_status = "dry_run_ok" if args.dry_run else "ok"
    sys.exit(0 if batch_results and all(r["status"] == success_status for r in batch_results) else 1)
