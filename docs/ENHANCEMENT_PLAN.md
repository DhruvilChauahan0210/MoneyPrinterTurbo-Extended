# Video Quality Enhancement Plan — Professional Editing Pipeline

Goal: make generated Shorts look hand-edited (MrBeast/Hormozi-style) so they can be uploaded as-is.
This document is an implementation spec. Each task lists exact files, current behavior, target behavior,
and step-by-step instructions. Implement tasks IN ORDER — they are sorted by impact and each is
independently shippable. Test after each task before moving to the next.

## Codebase Orientation (read first)

| File | Role |
|---|---|
| `app/services/task.py` | Pipeline orchestrator: script → terms → audio → subtitle → materials → combine → final render |
| `app/services/material.py` | Downloads videos (Pexels/Pixabay) and images (DDG/Pexels/Wikipedia) — `download_images()`, `save_image()` |
| `app/services/video.py` | `preprocess_video()` (image→clip with Ken Burns), `combine_videos()`, `generate_video()` (subtitles, BGM, final render) |
| `app/services/image_similarity.py` | Existing CLIP model wrapper (used by semantic stock-video mode) |
| `app/services/semantic_video.py` | Existing script-segment ↔ clip matching for stock videos |
| `app/services/subtitle.py` | SRT + enhanced word-timing JSON generation |
| `app/services/voice.py` | TTS (edge-tts azure_tts_v1, Chatterbox, Sarvam) |
| `app/models/schema.py` | `VideoParams` pydantic model — ALL new options must be added here with defaults |
| `webui/Main.py` | Streamlit UI — new options need a widget + assignment to `params.<field>` |
| `resource/songs/` | BGM mp3 files |
| `resource/fonts/` | Fonts (ttf/ttc) |

Run server: `.venv/bin/streamlit run ./webui/Main.py` from repo root. Python is `.venv/bin/python3` (3.11).
Encoding settings live at top of `video.py` (`video_codec`, `quality_params`, etc.) — reuse them for any new `write_videofile` call.

Rule for every task: add new `VideoParams` fields with safe defaults (feature OFF or current behavior)
so existing API callers and the long-video mode (`sequential_generator.py`) keep working.

---

## TASK 1 — CLIP-based image-to-script matching (biggest quality win)

**Problem:** `download_images()` collects images per search term, then `combine_videos()` plays them in
random order. An image of a generic stadium can appear while the narration says "headbutted him in the
chest". Visual-narration mismatch is the #1 amateur tell.

**Target:** every image is shown during the script sentence it best matches, ranked by CLIP similarity.

**Implementation:**
1. In `material.py` `download_images()`: return a list of dicts `{"path": str, "search_term": str}`
   instead of bare paths — keep a wrapper that still returns paths for backward compat, or update the
   single caller in `task.py` (`get_video_materials`, the `image_search` branch).
2. New file `app/services/image_ranker.py`:
   - `rank_images_for_script(image_paths: list[str], script: str, model_name: str) -> list[dict]`
   - Split script into sentences (reuse the sentence segmentation in `semantic_video.py` —
     `segmentation_method == "sentences"` path — do not write a new splitter).
   - Load CLIP via the existing pattern in `image_similarity.py` (`clip-vit-base-patch32`). Compute
     text embedding per sentence and image embedding per file.
   - Assign images to sentences greedily: for each sentence in order, pick the unused image with the
     highest cosine similarity. If images < sentences, allow reuse but never twice in a row.
   - Return ordered list: `[{"path": ..., "sentence_idx": ..., "score": ...}, ...]`.
   - Drop images whose best score < 0.18 (CLIP cosine floor for "completely unrelated") IF at least
     enough images remain to cover audio duration; log what was dropped.
3. In `task.py` `image_search` branch: after `download_images`, call the ranker, pass the ordered
   paths onward. Then in `generate_final_videos`, force `video_concat_mode = sequential` for
   image_search source (ordering is now meaningful — random shuffle would destroy it).
4. Sentence-timing alignment: clip duration per image should be `sentence_audio_duration` rather than
   fixed 3s. Sentence start/end times are derivable from the SRT (`subtitle.file_to_subtitles`) —
   match sentences to subtitle line ranges by cumulative text position. If this proves hard, ship v1
   with fixed durations + correct ORDER only; order alone is 80% of the win.
5. New `VideoParams` fields: `enable_image_ranking: bool = True` (on by default for image_search),
   `image_ranking_min_score: float = 0.18`.

**Test:** generate the Zidane video; visually confirm headbutt-related images appear during headbutt
sentences. Check log output for per-image scores.

---

## TASK 2 — Professional motion on images (Ken Burns 2.0)

**Problem:** `video.py` `preprocess_video()` applies one weak effect: linear zoom-in to ~109%
(`1 + (clip_duration * 0.03) * (t/duration)`). Every image moves identically → monotone slideshow feel.

**Target:** varied, aggressive, smooth motion per image.

**Implementation (all inside `preprocess_video`, keep function signature):**
1. Build an effects list; pick per image by `index % len(effects)` (NOT `random.choice` — deterministic
   variety, avoids two identical moves in a row):
   - `zoom_in_fast`: scale 1.0 → 1.25 over clip duration
   - `zoom_out`: scale 1.25 → 1.0 (start zoomed, pull back)
   - `pan_left_zoom`: scale fixed 1.15, x-position drifts right→left ~8% of width
   - `pan_right_zoom`: mirror of above
   - `zoom_in_top`: zoom 1.0 → 1.2 anchored at upper third (faces are usually in the upper third)
2. Apply easing: replace linear `t/duration` with ease-out `1 - (1 - t/d)**2` — motion that decelerates
   reads as "edited", linear reads as "generated".
3. IMPORTANT — render scale: to pan without showing black edges, first resize the image so it OVERFILLS
   the target frame by the max scale factor, then animate position/scale, then crop to frame via
   `CompositeVideoClip` with fixed `size=(video_width, video_height)`. `preprocess_video` currently
   doesn't know the aspect — add parameter `video_aspect` and pass it from `task.py` (it's in `params`).
4. Bump image clip fps from 30 → keep 30 but ensure `resized` lambda is smooth (moviepy evaluates per
   frame — fine).
5. New `VideoParams` field: `image_motion_style: str = "varied"` (`"varied" | "subtle" | "off"`;
   `subtle` = current behavior).

**Test:** generate; confirm adjacent images use different motions, no black borders at any time,
motion decelerates (not constant speed).

---

## TASK 3 — Hook card (first 1.5 seconds)

**Problem:** video opens cold on a random image. Scroll-stop rate decides Shorts performance.

**Target:** first 1.2–1.5s shows the single best image, hard zoom, with a 3–6 word hook overlaid in
huge text. Narration starts after (or under) it.

**Implementation:**
1. Hook text source: new `VideoParams.hook_text: str = ""`. If empty AND an LLM provider is configured,
   add `llm.generate_hook(video_subject, video_script)` in `app/services/llm.py` — prompt: "Return ONLY
   a 3-6 word all-caps hook for a YouTube Short about: {subject}. No quotes, no punctuation except ?
   or !. Example: HE ENDED HIS CAREER WITH THIS". Fallback if LLM fails: first 5 words of subject,
   upper-cased.
2. Hook image: if Task 1 is done, use the image with the highest CLIP score against the full script;
   else first image.
3. Build the card in `video.py` as a new function `create_hook_clip(image_path, hook_text, params,
   video_width, video_height) -> VideoClip`:
   - Image with fast zoom 1.0 → 1.3 over 1.5s (reuse Task 2 helpers).
   - Dark overlay: full-frame `ColorClip` black at 35% opacity so text pops.
   - Text via PIL (follow the pattern in `create_word_highlighted_image` — PIL → `ImageClip`), font
     size ~`video_width * 0.085`, white fill, black stroke width 8, wrapped to ≤3 lines, centered at
     45% height. Use the font from `params.font_name`.
   - Optional: text scales 0.9 → 1.0 over first 0.3s (pop-in).
4. Wire-in point: `generate_video()` in `video.py` — prepend hook clip to the composite, shift the
   main video/audio/subtitles start by hook duration, OR simpler: concatenate `[hook_clip,
   main_video]` before the final write and delay subtitle clips by hook duration. The simpler path:
   put the hook INSIDE the timeline (narration plays under it) — no time shift needed, hook just
   overlays the first 1.5s. Start with the overlay variant; it's 10 lines.
5. New fields: `enable_hook_card: bool = True` (for shorts), `hook_duration: float = 1.5`.

**Test:** first frame of output file must show the hook text (extract with
`ffmpeg -i final-1.mp4 -vframes 1 f.png` and inspect).

---

## TASK 4 — Caption style upgrade (word highlighting on, modern look)

**Problem:** users keep `enable_word_highlighting: false`; default subtitle is plain white-on-bar text.
The word-by-word highlight system already exists and works (`create_enhanced_subtitle_clips`).

**Target:** Hormozi-style captions by default for image_search/portrait videos.

**Implementation:**
1. Defaults in `schema.py`: `enable_word_highlighting = True`, `word_highlight_color = "#FFD700"`
   (gold reads better than red on varied photos), `subtitle_position = "center"` for portrait,
   `font_size = 70`, `stroke_width = 6`, `text_background_color = False` (stroke instead of bar).
   Also mirror these as the pre-selected values in `webui/Main.py` widgets.
2. In `create_word_highlighted_image` (`video.py`): add scale "pop" on the highlighted word — render
   the highlighted word at 1.12× font size (rebuild line layout accounting for the wider word; simplest:
   render whole line at base size, render highlighted word again 12% larger on top at same anchor,
   slight y-offset so baselines align).
3. Limit caption to ≤4 words per screen for shorts: in `subtitle.create_enhanced_subtitles`, respect
   `max_chars_per_line` but add `max_words_per_subtitle: int = 4` param — shorter chunks = higher
   perceived pace.
4. Keep ALL changes behind the existing `enable_word_highlighting` flag so traditional mode is intact.

**Test:** generate with defaults; captions must be center-positioned, ≤4 words, current word gold and
slightly larger.

---

## TASK 5 — Audio polish (ducking + transition SFX)

**Problem:** BGM volume is constant (`MultiplyVolume(params.bgm_volume)`) — fights the narration.
No transition sounds → cuts feel unmarked.

**Implementation:**
1. Ducking (simple version, no sidechain needed): narration is continuous in these videos, so just
   lower default `bgm_volume` 0.2 → 0.12 AND add 1.5s BGM fade-in at start. True ducking (volume
   automation against speech gaps) is NOT worth the complexity — skip it.
2. SFX pack: create `resource/sfx/` with 3 files the user must supply (document in README):
   `whoosh.mp3` (image transition), `boom.mp3` (hook card hit), `riser.mp3` (last 3s build).
   If folder/files missing → silently skip (log debug).
3. In `combine_videos` (image path) record each clip's start time; in `generate_video`, for each
   transition timestamp add `AudioFileClip("whoosh.mp3").with_start(t).with_effects([MultiplyVolume(0.5)])`
   to the `CompositeAudioClip`. Boom at t=0 if hook card enabled.
4. New fields: `enable_sfx: bool = True`, `sfx_volume: float = 0.5`.
   Transition timestamps: simplest reliable source = cumulative clip durations returned by
   `combine_videos` — have it return `(path, list_of_cut_times)` or write `cut_times.json` into the
   task dir and read it in `generate_video`.

**Test:** audible whoosh at every image change; BGM never masks speech.

---

## TASK 6 — End-screen CTA (last 2 seconds)

**Implementation:**
1. `create_cta_clip(params, w, h)` in `video.py`: dark background (or last image blurred — blur via
   PIL `ImageFilter.GaussianBlur` then `ImageClip`), text "FOLLOW FOR PART 2 👻" (configurable:
   `cta_text: str = "FOLLOW FOR MORE"`), same PIL-text technique as Task 3.
2. Overlay during final 2s of the timeline (same overlay approach as hook card — no duration change).
3. Field: `enable_cta: bool = True`, `cta_text: str`.

**Test:** last frame shows CTA text.

---

## TASK 7 — Batch queue mode (volume lever)

**Problem:** one topic per click; user is the bottleneck. World Cup window = need daily output.

**Implementation:**
1. New file `batch_generator.py` at repo root (mirror the structure of `sequential_generator.py` —
   read it first and reuse its task-invocation pattern).
2. Input: `batch.json` — `[{"video_subject": ..., "video_script": ..., "video_terms": ...}, ...]`
   plus a shared `defaults` object for all other VideoParams fields.
3. Loop: for each entry build `VideoParams(**defaults, **entry)`, call `tm.start(task_id=uuid4(), ...)`,
   collect output paths, continue on per-video failure (log + skip).
4. CLI: `.venv/bin/python3 batch_generator.py batch.json`.
5. Output summary table at end: subject → final path / FAILED.

**Test:** 2-entry batch.json produces 2 videos unattended.

---

## TASK 8 — Auto thumbnail (optional, lowest priority)

For long-form only (Shorts use first frame — already handled by Task 3 hook card).
`create_thumbnail(best_image, title_words, out_path)`: 1280×720 PIL canvas, image cover-cropped,
4-word max text left-aligned 60% width, thick stroke, save `thumbnail.jpg` in task dir.
Field: `enable_thumbnail: bool = False`.

---

## Execution order & verification

```
1 → 2 → 3 → 4 → 5 → 6 → 7 → (8)
```

After EACH task:
1. `python3 -c "import ast; ast.parse(open('<changed file>').read())"` for every edited file.
2. Restart server (`pkill -f "streamlit run"` then relaunch) and generate the standard test video
   (Zidane headbutt config from `storage/tasks/` history) end-to-end.
3. Watch the output. Do not start the next task if the current one visually regressed anything.
4. Commit per task: `feat(video): <task name>` — one commit per task, never combined.

## Hard constraints (do not violate)

- MoviePy version is 2.x: use `with_position/with_start/with_duration/resized/subclipped` (NOT the 1.x
  `set_*` API), no `align` kwarg on TextClip.
- Every new `write_videofile` must reuse the module-level `quality_params`/`video_codec` from `video.py`.
- libx264 needs even dimensions — any new PIL image rendered to video must have width/height % 2 == 0.
- All new behavior behind `VideoParams` flags with defaults that keep the API backward compatible.
- Never call `random` for anything affecting clip ORDER when image ranking (Task 1) is on.
- Close every clip (`close_clip()`) — the codebase leaks memory otherwise on long batches.
