#!/usr/bin/env python3
"""Turn a YouTube Studio content export into a reusable channel strategy report.

This is deliberately read-only: it never calls YouTube or changes videos. Public
views and subscriber conversion are kept separate because a reach winner can be
a weak channel-growth winner (as the Roy Keane/Haaland Short demonstrated).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
import tempfile
import zipfile
from collections import defaultdict
from pathlib import Path


PLAYERS = (
    "ronaldo", "messi", "haaland", "mbappé", "mbappe", "neymar",
    "bellingham", "vinícius", "vinicius", "yamal", "barcelona", "real madrid",
)


def _table_path(source: str, temp_dir: str) -> str:
    if zipfile.is_zipfile(source):
        with zipfile.ZipFile(source) as archive:
            match = next((n for n in archive.namelist() if n.endswith("Table data.csv")), None)
            if not match:
                raise ValueError("export ZIP does not contain Table data.csv")
            archive.extract(match, temp_dir)
            return os.path.join(temp_dir, match)
    if os.path.isdir(source):
        return os.path.join(source, "Table data.csv")
    return source


def _cluster(title: str) -> str:
    lower = title.lower()
    for player in PLAYERS:
        if player in lower:
            return "mbappe" if player == "mbappé" else "vinicius" if player == "vinícius" else player
    return "other"


def analyze(source: str) -> dict:
    with tempfile.TemporaryDirectory() as temp:
        table = _table_path(source, temp)
        rows = []
        with open(table, newline="", encoding="utf-8-sig") as handle:
            for row in csv.DictReader(handle):
                if row.get("Content") == "Total" or not row.get("Views"):
                    continue
                try:
                    views = int(row["Views"])
                    subs = int(row.get("Subscribers") or 0)
                    duration = int(row.get("Duration") or 0)
                except ValueError:
                    continue
                if views <= 0:
                    continue
                rows.append(
                    {
                        "id": row["Content"].strip(),
                        "title": row["Video title"].strip(),
                        "views": views,
                        "subscribers": subs,
                        "duration": duration,
                        "subs_per_1k_public_views": round(1000 * subs / views, 3),
                        "cluster": _cluster(row["Video title"]),
                    }
                )

    if not rows:
        raise ValueError("no video rows with views were found")

    total_views = sum(r["views"] for r in rows)
    attributed_subs = sum(r["subscribers"] for r in rows)
    median_views = statistics.median(r["views"] for r in rows)
    baseline_conversion = 1000 * attributed_subs / total_views if total_views else 0

    for row in rows:
        row["reach_index"] = round(row["views"] / median_views, 3)
        conversion_index = (
            row["subs_per_1k_public_views"] / baseline_conversion
            if baseline_conversion else 0
        )
        row["conversion_index"] = round(conversion_index, 3)
        high_reach = row["reach_index"] >= 1.5
        high_conversion = row["conversion_index"] >= 1.5
        row["role"] = (
            "hybrid_winner" if high_reach and high_conversion
            else "reach_winner" if high_reach
            else "loyalty_winner" if high_conversion
            else "baseline"
        )

    clusters = defaultdict(lambda: {"videos": 0, "views": 0, "subscribers": 0})
    for row in rows:
        item = clusters[row["cluster"]]
        item["videos"] += 1
        item["views"] += row["views"]
        item["subscribers"] += row["subscribers"]
    for item in clusters.values():
        item["views_per_video"] = round(item["views"] / item["videos"])
        item["subs_per_1k_public_views"] = round(1000 * item["subscribers"] / item["views"], 3)

    duration_buckets = []
    for label, low, high in (("10-15s", 0, 15), ("16-25s", 16, 25), ("26-40s", 26, 40), ("41s+", 41, 10_000)):
        selected = [r for r in rows if low <= r["duration"] <= high]
        if not selected:
            continue
        views = sum(r["views"] for r in selected)
        subs = sum(r["subscribers"] for r in selected)
        duration_buckets.append(
            {
                "label": label,
                "videos": len(selected),
                "median_views": round(statistics.median(r["views"] for r in selected)),
                "subs_per_1k_public_views": round(1000 * subs / views, 3),
            }
        )

    sorted_views = sorted(rows, key=lambda r: r["views"], reverse=True)
    sorted_conversion = sorted(
        [r for r in rows if r["views"] >= 500],
        key=lambda r: (r["subs_per_1k_public_views"], r["views"]),
        reverse=True,
    )
    return {
        "summary": {
            "videos": len(rows),
            "public_views": total_views,
            "video_attributed_subscribers": attributed_subs,
            "median_views": median_views,
            "baseline_subs_per_1k_public_views": round(baseline_conversion, 3),
            "note": "Use Engaged views for retention decisions; public Shorts views include starts/replays.",
        },
        "top_reach": sorted_views[:10],
        "top_conversion": sorted_conversion[:10],
        "clusters": dict(sorted(clusters.items(), key=lambda x: x[1]["views"], reverse=True)),
        "duration_buckets": duration_buckets,
        "experiments": [
            "Publish two reach stories for each loyalty story.",
            "Keep reach stories near 10-16 seconds; do not stretch a one-beat fact.",
            "Use emotional/identity stories to earn subscriptions, with a CTA after the payoff.",
            "Evaluate stayed-to-watch, average percentage viewed, and subscribers per 1,000 engaged views after 48 hours.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="YouTube Studio ZIP, export directory, or Table data.csv")
    parser.add_argument("--output", default="storage/analytics/channel_strategy.json")
    args = parser.parse_args()
    report = analyze(args.source)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"STRATEGY_REPORT={output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
