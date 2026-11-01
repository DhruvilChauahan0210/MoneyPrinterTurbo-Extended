# Rules and traps (read before the first build of a session)

## CD's standing rules
- Build all slots of every requested day in one go, then report once. No mid-run approval stops.
- One render per Short, no retries. Failures are reported, and replaced with new topics only if CD asks.
- Real clips wherever they exist (famous match moments); photos elsewhere.
- Megastars only, fresh angles, drama over safe facts.
- Metadata in chat only, in full blocks, after everything is built.
- Go fast with browser work: no step-by-step screenshots.
- Deliver every Short to `~/Desktop` with the `DDMON_slotN_HHMM_topic.mp4` name.

## Jev preflight gate (batch_generator.py), the most common failure
- **Duplicate topic** (> 0.8 similar to any existing `batch_*.json` subject) blocks the render. Grep the ledger
  for the event, people and keywords. Example: an "Anfield 2019 Messi" topic was blocked by an existing
  `trent_corner` config at 0.92.
- **Claim gate** blocks on 'defamatory' / 'rumour_as_fact'. Blocked lines: "Neymar accused Nestor of the dirtiest
  tricks", "Canelo accused Messi of…", "Ronaldo called him a liar", "PIF is reportedly clearing debt". Write facts
  and neutral attributions instead ("X said …", "declined to comment", "a deal might not happen").
- 'overclaim' / 'invented_quote' are warnings only. They don't block.

## Script and length
- Measured: 65–80 words at voice_rate 0.88 gives 27–35s. 81+ words or long numbers spoken in full can push past
  38s (a hard fail in check_render: Pelé 39.1s, Juve 39.4s, Wolfsburg 40.4s shipped over). Aim for about 72 words.
- check_config warns when the hook overlaps line 1 by 50% or more. Rewrite the hook (e.g. "NOBODY SAW THIS COMING").

## Photos (beat_source.py + DuckDuckGo)
- Long or descriptive queries return junk (game screenshots, phone ads, landscapes, lions). Use plain names plus one keyword.
- About 1 in 3 beats need re-sourcing or borrowing. Look at every sheet, because CLIP scores don't tell you who is in the photo.
- One query can hang sourcing forever. Use a watchdog, then change the query.
- Running several sourcing jobs in parallel triggered DDG throttling and junk. Run them sequentially.
- Sourcing rewrites the whole JSON at the end. Picks and clip pins made while it runs are lost.

## Clips
- Search results are dominated by 442oons cartoons and fan-phone uploads. Reject both.
- Broadcast highlight timestamps can be offset. A "Neuer save" window showed a goat on the pitch. Scan finer
  (`--scan-from A --scan-to B --scan-every 0.5`) around the chosen seconds if in doubt.
- Coverage failure = clip `len` shorter than the spoken beat. Use 6.0s on long beats, and `rm` the cached shot to re-cut.

## Rendering
- `run_day.sh` skips Shorts that were already attempted (a BUILDLOG containing `task_id`). That's how one-shot is enforced.
- Two render batches in parallel are fine. Never rewrite a run script while it executes, because zsh reads it as it goes.
- Stop jobs by PID only. `pkill -f` matches its own command line.

## What-If
- Remotion project: `whatif-remotion/` (composition `WhatIf`, `npx remotion render src/index.ts WhatIf …`).
- Public assets: music.mp3–music5.mp3, boom.mp3, stadium.mp3. Rotate the music.
- Pronunciation: edge-tts mangles "Mbappé". Spell names as they should sound if needed.
