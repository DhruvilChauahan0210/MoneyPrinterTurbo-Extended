# One-shot generation workflow

This repository is configured to validate, generate, and render each requested task once.
There are no automatic provider retries, alternate hook generations, media fallbacks,
or progressive re-renders while `one_shot_mode = true`.

## 1. Run the zero-cost preflight

```bash
.venv/bin/python3 batch_generator.py batch_ronaldo_son.json --dry-run
```

The dry run checks the script, hook, search terms, portrait configuration, font,
local pinned media, FFmpeg installation, and one-output rule. It does not call an
LLM, voice provider, footage provider, or renderer. It does not consume a ledger
attempt.

Fix every error before generating. Warnings identify risky factual absolutes,
generic CTAs, and unusually long narration.

## 2. Generate exactly once

```bash
.venv/bin/python3 batch_generator.py batch_ronaldo_son.json
```

Before the first provider call, the request is atomically reserved under:

```text
storage/one_shot_ledger/<task-id>.json
```

The ledger records the content fingerprint plus the voice, material, and render
stages. Re-entering the same task ID is blocked. A newly requested task may cover
the same topic—even with identical parameters—and receives a fresh pipeline and
fresh edit decisions. The runner never copies an older task output.

## 3. Inspect the quality report

A successful task contains:

```text
storage/tasks/<task-id>/quality_report.json
```

It verifies portrait media coverage before rendering and then checks that the one
final file is 1080x1920, has video and audio streams, is non-empty, and matches the
planned duration. A failed inspection reports the problem without regenerating.

## Generate another Short on the same topic

Start the batch again as a new task. The batch runner creates a new task ID, so it
may fetch new media and make a new Short on the same subject. Each task still gets
only one attempt per external provider stage and one final render.

## Refresh the channel strategy

Export the Content analytics ZIP from YouTube Studio, then run:

```bash
.venv/bin/python3 channel_optimizer.py "/path/to/youtube-export.zip"
```

The report is written to `storage/analytics/channel_strategy.json`. It separates
reach winners from subscriber-conversion winners, calculates topic and duration
performance, and preserves the distinction between public starts/replays and
Engaged views.
