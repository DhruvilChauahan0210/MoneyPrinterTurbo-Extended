#!/usr/bin/env python3
"""
Sequential chunk generator — submits one chunk at a time,
waits for it to fully complete before submitting the next.
Progress is written to /tmp/seq_gen_progress.json for the UI to read.
"""
import json
import sys
import time
import requests

API = "http://localhost:8080/api/v1"
PROGRESS_FILE = "/tmp/seq_gen_progress.json"


def write_progress(data):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f)


def poll_until_done(task_id, chunk_index, total):
    while True:
        try:
            r = requests.get(f"{API}/tasks/{task_id}", timeout=10)
            d = r.json().get("data", {})
            state = d.get("state")
            progress = d.get("progress", 0)
            videos = d.get("videos", [])

            write_progress({
                "status": "running",
                "current_chunk": chunk_index + 1,
                "total_chunks": total,
                "current_task_id": task_id,
                "current_progress": progress,
                "completed_task_ids": completed_ids,
                "completed_videos": completed_videos,
            })

            if state == 1:  # done
                return videos[0] if videos else None
            elif state == 3:  # failed
                return None
        except Exception as e:
            print(f"Poll error: {e}")

        time.sleep(15)


if __name__ == "__main__":
    chunks_file = sys.argv[1]
    with open(chunks_file) as f:
        data = json.load(f)

    chunks = data["chunks"]
    base_params = data["params"]
    total = len(chunks)

    completed_ids = []
    completed_videos = []

    write_progress({
        "status": "starting",
        "current_chunk": 0,
        "total_chunks": total,
        "current_task_id": None,
        "current_progress": 0,
        "completed_task_ids": [],
        "completed_videos": [],
    })

    for i, script in enumerate(chunks):
        print(f"\n=== Generating chunk {i+1}/{total} ===")

        payload = {**base_params, "video_script": script}

        try:
            r = requests.post(f"{API}/videos", json=payload, timeout=15)
            task_id = r.json()["data"]["task_id"]
            print(f"Task submitted: {task_id}")
        except Exception as e:
            print(f"Submit failed for chunk {i+1}: {e}")
            write_progress({
                "status": "error",
                "error": f"Chunk {i+1} submit failed: {e}",
                "current_chunk": i + 1,
                "total_chunks": total,
                "current_task_id": None,
                "current_progress": 0,
                "completed_task_ids": completed_ids,
                "completed_videos": completed_videos,
            })
            continue

        video_path = poll_until_done(task_id, i, total)
        completed_ids.append(task_id)
        if video_path:
            completed_videos.append(video_path)
            print(f"Chunk {i+1} done: {video_path}")
        else:
            print(f"Chunk {i+1} failed or no video returned")

    write_progress({
        "status": "done",
        "current_chunk": total,
        "total_chunks": total,
        "current_task_id": None,
        "current_progress": 100,
        "completed_task_ids": completed_ids,
        "completed_videos": completed_videos,
    })
    print("\n=== All chunks complete ===")
