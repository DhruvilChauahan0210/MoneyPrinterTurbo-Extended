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
- Coverage failure = clip `len` shorter than the spoken beat. **Always use `--len 6.0`** (8 words with long names = 4.9s spoken;
  a 4.4s clip failed the 12 Nov 2026 Ronaldo/Bayern render). `rm` the cached shot to re-cut after changing len.

## Rendering
- `run_day.sh` skips Shorts that were already attempted (a BUILDLOG containing `task_id`). That's how one-shot is enforced.
- Two render batches in parallel are fine. Never rewrite a run script while it executes, because zsh reads it as it goes.
- Stop jobs by PID only. `pkill -f` matches its own command line.

## What-If
- Remotion project: `whatif-remotion/` (composition `WhatIf`, `npx remotion render src/index.ts WhatIf …`).
- Public assets: music.mp3–music5.mp3, boom.mp3, stadium.mp3. Rotate the music.
- Pronunciation: edge-tts mangles "Mbappé". Spell names as they should sound if needed.

## Retention (6 Nov 2026 study of CD PHANTOM Shorts)
- Views fell from ~1,000 per Short (24-28 Oct) to 40-320 (29 Oct onward). Length/format were NOT the cause. "Stayed to watch"
  (Studio > video > Analytics) separates winners (~50%+) from losers (18-35%); the swipe decision happens in the first second.
- **The hook text is never on screen**: beat-plan configs have `enable_hook_card: False`, so `hook` is only used to pick the cover.
  What viewers see at 0s is the first photo plus the first spoken words.
- **Opening rule:** beat 1 = a big close-up of the named megastar in the right kit; first spoken words carry a number or the star's
  name, never a bare date ("April 2017...") or a wide shot. Check the first caption's spelling (Benatia was captioned "Banesha").
- Titles lead with a name or number; never reuse a title across Shorts. Check "Stayed to watch" ~2 days after publishing; baseline ~39%.

## Disk and clips (6 Nov 2026)
- The disk filled mid-render and corrupted two renders (and the one-render rule then cost a re-render). Check `df -h .` before a batch;
  `storage/cache_videos/auto` had grown to 273 GB and is safe to prune (files >30d).
- Clip cutting rejects windows with burned-in text bands (ad boards, lower thirds). Try nearby start seconds; keep a photo otherwise.
- `--replace` can leave 261-byte `sec.mp4` stubs in `storage/cache_videos/comparison/<key>/`; if a cut fails, cut from the cached full
  source with `auto_footage.fetch_exact_clip()` and set the beat's `media/url/start/len` fields by hand.

## Parallel build of many days (13-27 Nov 2026 recipe)
- Research agents (one per slot type) write JSON specs; pre-screen every topic with `.venv/bin/python jev_tools.py topics file.txt` (dup >= 0.80 blocks) and `jev_tools.py screen "script"`. Keep spares (5 per star): one real failure happened (editorial gate: < 60% shots with a person).
- Source photos with ONE global queue wrapped in `./ddg_lock.sh` (never run DDG outside it); a watchdog `sleep` that inherits a pipe blocks the next call 10 min (fixed in ddg_lock.sh: redirect the watchdog's stdio).
- Finisher agents pick photos and pin clips per config; renders run in 2-3 workers (`render_worker.sh`, `render_worker_rev.sh` claim files so nothing renders twice). 5-8 min per render under load.
- Port 3000 is CD's dev server: whatif.sh now uses a random Remotion port; pass `--port=3399` to any other remotion call.
- sched.js: right after the last upload the Content list lags; wait ~2 min and re-check BEFORE re-running an index (a re-run created a duplicate). Verify with a count per date and title.

## RULE (CD, 11 Nov 2026): clips first, photos only fill gaps
Every Short is built on moving clips. A photo is only a gap-filler where no usable clip exists, kept under ~2 s.
Never hold one still for a long stretch (Who-is-it and Duel must play video clips in their frames, not a single photo).

## Sprint recipes and engine switches (8-9 Nov 2026)
Plan: research_nov8/PLAN_28NOV.md. Prototypes: prototypes/ (R1 commentary, R2 graphics runner prototypes/r2/, R3 conflict story).
New VideoParams switches (all default to the old behaviour, set them in the config `defaults`):
- `hook_overlay_only: true`: hook veil + text drawn over the LIVE first shot instead of freezing a still of it for `hook_duration`.
- `enable_emoji_stickers: false`: turns off the auto emoji pop on power words (broke -> bandage face on a UEFA president).
- `caption_script_align: true` + `caption_text_overrides`: captions use the script's spelling (`Oyarzabal`, not `O 'years`) with the
  transcript's timing; digits the transcript wrote (`17`, `47th`) are kept; `{"two-one": "2-1"}` fixes spelled-out scores.
- Also: `enable_cta: false` (the CTA card swallows the last ~2 s; make the last beat the visible question), `enable_subscribe_button: false`,
  `cover_min_keep ~0.36` (landscape photos crop-fill instead of the blurred-bar look; there is no face detection, pick centred faces).
Traps found building the prototypes:
- `beat_source.py --replace` fails for sources > 180 s (261-byte stubs): use gen_proto_r1_pin.py (download once at 1080p, cut with
  auto_footage.fetch_exact_clip, set crop x by hand; auto crop picks sleeves).
- The renderer plays the MIDDLE of a pinned 6 s clip, so pin start = wanted second - 3 (more exactly start + (6 - beat_dur)/2 must show it).
- `min_shot_seconds` and `image_motion_style` do nothing in beat-plan mode: cut rate = number of beats; use 12+ beats of <= 7 words.
- The Jev dedup gate blocks any topic that already has a batch_*.json (0.9+); pre-check with
  `jev_tools.py dedup "<subject>" | grep '^same=' | sort -t= -k2 -rn | head -3` (read the HIGHEST matches, not the last lines) before assigning a topic.
- Never use `--allow-risk` to get past that gate without CD's say-so.
- `scripts/qc_dark.sh video.mp4` lists black stretches. Mastering: plain loudnorm only reaches -11.4. Working chain (-10.6 LUFS, peak -1.5 dBFS, verified with ebur128=peak=true): `acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-10.5:TP=-2.0:LRA=7,loudnorm=I=-10.5:TP=-2.0:LRA=7,alimiter=limit=0.8:level=false`, then AAC 192k (TP=-1/limit 0.89 gave a +0.7 dBFS peak).
