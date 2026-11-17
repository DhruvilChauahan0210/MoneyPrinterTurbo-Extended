# CD PHANTOM: what went wrong, and the plan from 28 Nov 2026

Written 8 Nov 2026 while CD was away. All 45 Shorts (13-27 Nov) stay Scheduled and untouched. Nothing was deleted or made private.
Every number below is from data pulled today. **FACT** = measured. **INFERENCE** = my reading. **UNVERIFIED** = reported by a research agent or a web page I could not open.

---

## 1. The 60-second version

1. **Views were flat at about 1,000 per Short for 3 months, then fell about 80% on one date (28/29 Oct).** It hit every star, topic, length and time slot at once. 276 Shorts before the drop had a median of ~1,000; the 32 after it have a median of 180. (FACT, own data, 308 Shorts, `D/timeline_views.png`)
2. **The ~1,000 was a fixed test-audience quota, not a measure of quality.** A Short with 53% stayed-to-watch and one with 26% both landed near 1,000. Nothing graduated to a bigger audience. That is why we have had no breakout since July. (FACT)
3. **Not the cause (evidence against):** publish time, which slot of the day, weekday, Short length, which star, title wording, cannibalisation between our own Shorts. All were flat before the drop. (FACT; p-values in `D/stats_output.txt`)
4. **Probable cause: a platform-level change in how the Shorts feed treats "templated / re-used" content, plus a weak retention record on top.** On 1 Oct 2026 YouTube announced that Shorts recommendations will cut reach for channels that mostly aggregate or re-upload other creators' footage, and that template-based edits and voice-over that only describes the picture do not count as original. Our recipe (stock photos, 6 s highlight clips, the same TTS voice, the same 8-9 beat shape, the same title suffix, 3 a day) matches that description closely. (FACT that the announcement exists: 9to5Google, PPC Land, Search Engine Journal, checked today. INFERENCE that it hit us.) The giant benchmark channel @_simplesports, built on the same style, has a median of 3.8K on its last 40 Shorts against 140K in September, so this is not only our problem.
5. **Photo slides are probably not what triggered the drop, but they are what keeps us down.** Photo-only Shorts were fine (median 1,016) on 21-28 Oct. But every Short since the drop is at least 66% stills, so the data cannot separate "stills" from "the new regime". (FACT / limit)
6. **The winners right now are not narrated photo stories.** Narrated untold-story-over-photos channels sit at a median of 0.85-1.3K views. The channels that are growing use moving visuals, a face or strong motion in the first second, a cut every 2.5-3.5 s, a loud voice with attitude, and a current news conflict. (FACT from 17 channels; INFERENCE on causes.)
7. **Plan: a 14-day structured learning sprint from 28 Nov** (3 new recipes + 1 control, same-day interleaved, decision rules fixed in advance). Details in section 5.

---

## 2. Our own numbers (FACT)

**Views per Short by era** (public data, IST publish time; `D/channel_shorts.jsonl`, `master.csv`):

| Era | Recipe | n | Median | Share under 300 views |
|---|---|---|---|---|
| 1 Aug - 5 Sep | 9-15 s real clips | 109 | 1,012 | 8% |
| 6 Sep - 16 Oct | 20-30 s clips, `#halo` titles | 129 | 909 | 19% |
| 17 - 28 Oct | photo beat-plan | 38 | 1,041 | 3% |
| 29 Oct - 8 Nov | photo beat-plan + What-If | 32 | 180 | 75% |

- Two earlier dips (15-20 Sep, 10-14 Oct) recovered on their own in about 5 days. This one has lasted 11+ days, so it behaves differently.
- 28 Oct: 1,007 / 1,094 / 358 views for the 13/17/21 slots. 29 Oct: 408 / 437 / 13. Re-uploads of three 28 Oct titles got 40%, 40% and 4% of the first copy.
- Monthly views: Aug 101.7K, Sep 73.0K, Oct 83.3K, 1-8 Nov 6.3K. Last 28 days in Studio: 61.2K views, 150 new subscribers.

**Studio, per-Short "stayed to watch"** (my pull, `studio_*_rows.json`):

| Group | Median views | Mean stayed to watch |
|---|---|---|
| Lifetime top 50 | 2,172 | **51%** (best: 63%) |
| October Shorts | 1,068 | 39% |
| 1-7 Nov (Shorts live in that week) | 170 | **29.5%** |

- The all-time top 50 are 10-15 s personal-story or conflict Shorts ("Roy Keane DESTROYED Haaland's Dad", "They Called Ronaldo CRYBABY", "Neymar REJECTED Real Madrid", "Haaland's WEIRD Diet Secret"). Median duration 12-13 s, stayed 50-63%.
- The newest Shorts are mostly records and match facts told over photos, at 29% stayed.
- Only two post-drop Shorts broke 900 views: "Mbappé was ROBBED by 28 points?" (1,666 views, 52.5% stayed) and "23 YEARS AND STILL GOING" (925, 53.3%). Both have a hard number in the title and the opening line. I have not checked their visuals.
- The 7 s What-If Shorts: 70-321 views, 20-28% stayed. No special penalty against same-day neighbours (ratio 1.0), but no upside either.

**Audience** (Studio, last 28 days): 96.8% new viewers, 3.2% casual, under 0.1% regular. Subscribers are 1% of watch time. Shorts feed is 95.1% of views. Mobile 69%, tablet 14%, TV 13%. India 20%, US 6.8%, UK 6.6%, South Africa 5%, Indonesia 3.3%. Age 25-44 is 58%. Male 67%.

**Timing** (Studio heatmap, `heatmap.png`): viewers are most active 18:00-24:00 IST and stronger on Sat/Sun. Our 13:00 slot is in the dim part of the day, and 13:00 IST is 07:30 in the UK and 02:30 in New York. But views by slot were flat (medians 1,002 / 946 / 970, p = 0.57), and YouTube itself says publish time does not affect long-term performance. **Timing is a minor lever, not the cause.**

**What the best vs worst Shorts look like** (19 hand-reviewed mosaics, `D/mosaics/`, `D/visual_labels.csv`; descriptive, not proof):

| | 7 top Shorts (1,663-3,422 views) | 9 bottom Shorts (4-81 views) |
|---|---|---|
| Real footage | 6 of 7 | 4 of 9 |
| Face close-up in the first second | 6 of 7 | 3 of 9 |
| Hook text burned in at t=0 | 6 of 7 | 4 of 9 |
| Median cuts per 10 s | 9.9 | 2.5 |

Compare `D/mosaics/2026-08-05_13_v2719.jpg` (full-frame clips, face close-ups, emoji overlays, 2,719 views) with `D/mosaics/2026-11-04_17_v81.jpg` (small photo in the middle, blurred bars, same still for several seconds, 81 views). I looked at both myself.

Since late Oct our photo Shorts use a landscape photo in the middle third with blurred bars above and below, stills held 3-4.5 s, no hook card, a "Subscribe" end card, and an opening that is a wide shot, collage or scoreboard graphic rather than a face.

---

## 3. Weak points, ranked by evidence

| # | Suspect | Verdict | Evidence |
|---|---|---|---|
| 1 | Channel/recipe is now classed as templated or re-used, so the feed gives us a smaller test audience | **Most likely, but unproven** | Single-date step across everything; 1 Oct originality update; benchmark channel decayed too; policy text names slideshows, templates, highlight reposts |
| 2 | Retention too low for too long (39% then 29%, against 51% for our winners) | **Real, and the thing we can fix** | Stayed-to-watch by group; no Short ever graduated from the quota |
| 3 | Photo-slide look (stills, letterbox, no face, slow cuts) | **Plausible limiter** | Top-vs-bottom mosaics; competitors' winners all move; cannot be tested inside the post-drop data |
| 4 | Topic type: records and facts instead of conflict or personal story | **Plausible** | Lifetime top 50 are stories and conflicts; refusal / rejection / money stories have a 3x higher ceiling (post-hoc, p = 0.0004) |
| 5 | Title template identical on ~300 Shorts ("... 😳 #halo try this sound #shorts") | **Possible** | Titles run 55-85 characters; in a 397-Short market sample, titles of 26-40 characters had a 3.05M median against 163K for 61+ (correlation only) |
| 6 | Volume (3 a day) | **No evidence either way** | Volume never varied. Same-day Shorts were positively correlated, so no cannibalisation |
| 7 | Publish time | **Ruled out as a cause; small possible upside** | Flat across slots and weekdays |

---

## 4. What is working for others (and what we can and cannot copy)

Sources: agents A, B, C. Search results over-represent outliers, so treat these as hypotheses.

**Channels growing right now (A, full per-video data):**
- **@NEScalingAi** (80.7K subs): AI-generated photoreal video "soap operas" of real players in conflict, 55-125 s. Median 165K, 70% of Shorts over 100K. Runs a serial arc (Yamal / Kane / Mbappé Ballon d'Or) with the context in the title: 13 arc videos median 1.11M vs 118K for non-arc. **We cannot and should not copy this:** it needs video generation and puts invented dialogue in real players' mouths (likeness and defamation risk, and our compliance gate blocks it).
- **@Schteiny** (318K subs): human-voice meme commentary over moving found clips, about 1 Short a day, 55-63 s, every one over 100K, loud audio (-7.8 LUFS vs our calm voice). Titles are statements of an event with a 😭 emoji. **This is the model closest to what we can build.** Risk: some footage is other creators' streams.
- Weakest class: narrated "untold story" over photos (@evarwood01 median 0.85K, @KomalKumari 1.3K). That is our current format.

**Small channels with 1M+ football Shorts (B, 111 videos):** median length 17 s. Clusters: AI skits (88 videos), find-the-player puzzles (15, 4.5M median), pick-one polls (12, 5.0M), versus / elimination brackets (33, 2.4M). One 17M-view example is a static puzzle grid with a countdown bar, no footage, no voice. These are original graphics, which is also the safest route on the originality rule.

**Topics (C, 397 Shorts):** Yamal is the best-covered star by views (median 1.41M), Messi and Ronaldo are saturated (Ronaldo = 49% of titles) and Messi's median is tiny. Two-star titles do 1.8M vs 311K for one star. Records and numbers have the best floor; warm personal moments with a current star have the fat tail. Ronaldo's Portugal retirement Shorts did 2-4M in 3 days then faded, so after 28 Nov use evergreen or scheduled hooks, not "breaking".

**Titles (A + C):** 30-45 characters, star or event first, one dramatic emoji (😳 😭 💀), no colon, pipe or quote marks, no hashtags in the title, a statement not a question. Our current titles break most of these.

**Policy (B, verified for the 1 Oct item):** the monetisation text since July 2025 names "image slideshows, templated storylines" and "generic or unoriginal templates giving the impression of mass production" as non-monetisable. The 1 Oct recommendation change is the reach side of the same idea. YouTube has not said whether still photos or TTS count. **Shorts-only monetisation is effectively off the table for a small channel from Feb 2027 (10M Shorts views in 90 days to keep the Shorts revenue share), so the goal is reach and subscribers.**

**Conflicts between sources (so we test instead of guessing):**
- Length: A's channels do better at 55-65 s and B's viral small channels are 15-25 s. Our own data shows no difference by length. -> test both.
- Arcs: A says serial arcs work. Our older rule says "Part N" repels cold viewers. -> test an arc with context in the title and no "Part N" label.
- Volume: no study found of a 3-a-day penalty; the winners post 1 a day. -> go to 2 a day for the sprint.

---

## 5. The plan: 14-day learning sprint, 28 Nov - 11 Dec

**Principle: stop making more of the same. Test recipes against each other on the same days, decide on numbers fixed in advance.**

### 5.1 Schedule
- Keep the 45 scheduled Shorts exactly as they are. They are 45 more data points of the current recipe (a free baseline).
- From 28 Nov: **2 Shorts a day** (17:00 and 21:00 IST). Drop the 13:00 slot. Reason: it is the dimmest period on the heatmap, and it frees build time. This is a build-quality call, not a proven reach gain.
- 28 Shorts total. Rotate recipes so each one lands in each slot equally.

### 5.2 The four cells

| Cell | n | What it is |
|---|---|---|
| **C0 Control** | 4 | The current photo beat-plan, built with the topic discipline below. 2 with our old title template, 2 with the new title style. |
| **R1 Commentary over moving clips** (the Schteiny model) | 8 | 35-45 s. Voice with attitude (louder, faster, loudness about -10 LUFS), a cut every 2.5-3 s, all moving visuals, face or strong motion in the first second, hook text on frame 1, word-by-word captions, one argued opinion. |
| **R2 Original graphics** (puzzle / duel / bracket) | 8 | 15-22 s. Remotion: "Find the player" grid with a timer bar, "Who is it?" blur-to-clear reveal, "Pick one" duel with animated stat bars. Fully original assets. |
| **R3 Conflict or story Short with an argued position** | 8 | 25-30 s. Built like our best pre-drop Shorts: clip-first, face close-up and hook card at t=0, 10+ cuts per 10 s, a refusal / rejection / money / conflict angle, 2 of the 8 as a two-part arc with the context in the title. |

New title style for R1-R3 and the 2 new-style controls: 30-45 characters, statement not question, star or event first, one emoji, no `#halo try this sound #shorts`, no colon / pipe / quotes.

### 5.3 Rules for every Short
- **Original element required:** every Short must carry something we made (our own stat card or graphic, an argued position, a comparison). Narration that only describes the picture does not count.
- **No invented quotes or dialogue.** No accusations (the compliance gate blocks them anyway).
- **Open on a face or strong motion in the first second.** No wide shots, collages or scoreboard stills as the opener.
- **At least 60% moving visuals** in R1 and R3. Stills no longer than 2 s.
- Unique title, no repeated suffix, no re-uploads of old titles.
- Each Short structurally different from the last one in the same cell where possible.

### 5.4 Topics
Use **story and conflict angles**, not records. Agent C's 60-topic menu (`C/menu.json`) is raw material only. Many items are "record/number" angles and have to be recast into a conflict or personal story. Pull 15 from it, mixing:
- Current stars with fat-tail interest: **Yamal** (best-covered), Mbappé, Haaland, Kane (Ballon d'Or aftermath), Bellingham, plus two-star pairings (Yamal vs Mbappé, Kane vs Yamal).
- Under-supplied names: Rodri, Unai Simón, Cubarsí, Rice, Saka, Putellas.
- **Dated hooks** to schedule on or the day before: 28 Nov Arsenal v Man City and Everton v Liverpool, 5 Dec Tottenham v Arsenal and Chelsea v Liverpool, 8-9 Dec Champions League matchday 6 (Barcelona v Man City, Arsenal v Real Madrid), 13-15 Dec one year since Messi's India tour (India is our largest audience), 18 Dec MLS Cup final and the 2022 World Cup final anniversary, 20 Dec Mbappé turns 28. **UNVERIFIED:** agent C's list of news facts (Kane's Ballon d'Or on 26 Oct, Spain winning the 2026 World Cup 1-0 after extra time, the Portugal retirement figures) comes from web searches it flagged as partly conflicting. Our usual rule applies: fetch the source page before any fact goes in a script.
- Hold 4 of the 28 slots for reactive news.
- Messi / Ronaldo only with a genuinely new angle.

### 5.5 How we measure (fixed now, before any result is seen)
- Pull per-Short Studio data at **72 hours** after publish: views, engaged views, stayed to watch, subscribers. (Method documented in section 7; it works.)
- **Win:** a recipe whose median views are at least **2x the control median** AND whose mean stayed-to-watch is at least **45%**, with 8 Shorts.
- **Kill:** a recipe that is at or below the control median after its first 6 Shorts.
- **Read the control first.** If the 45 scheduled Shorts (13-27 Nov) come back to a median of 600 or more, the drop was temporary and platform-side, and the sprint results are judged against that new baseline. If they stay near 180, the sprint is the first real test of the recipe.
- Check-ins: 5 Dec (half way: stop only a clear loser), 12 Dec (decision).
- Do not change two things at once inside a cell. A follow-up sprint crosses title style with the winning recipe.

### 5.6 What I would build first (engineering order)
1. **R3 first (cheapest):** the beat-plan already does most of it. Changes: hook card on (`enable_hook_card: True`), clip beats of about 2.5-3 s, a face-first opening rule, 10-12 beats, a final argued-opinion beat. About 1 day of work, reuses the clip pipeline.
2. **R2 Duel and Who-is-it:** two new Remotion compositions on the existing WhatIf pattern (1 photo or 2 photos plus animated bars or blur). The 25-photo puzzle grid comes second because it needs a face-crop pool.
3. **R1:** needs a punchier voice and a louder master. Already installed and untried: `en-US-GuyNeural` (tagged "Passion"), `en-US-RogerNeural` ("Lively"), `en-US-AndrewNeural`; add a faster rate and `loudnorm` near -10 LUFS. Checked in code: the hook-card switch `enable_hook_card` exists (`app/models/schema.py:257`, default True; our beat-plan donor config turns it off), so R3 needs a config change, not new code, and a moving-clip sourcing step that avoids watermarks and fan-phone footage. Copyright caution: use short broadcast or press clips with our own argument over them.
4. Title generator that enforces the new title rules.
5. A saved script that pulls the per-Short Studio table (section 7).

### 5.7 Decisions
**Answered by CD on 8 Nov:** 2 a day (decision 1); build prototypes now (decision 4). The voice decision (2) is still open, so R1 tests the louder voice and the other recipes keep the calm one. The sprint slate is in `prototypes/SPRINT_SLATE_28NOV.md`; prototypes are being built in `prototypes/`.

**Original questions:**
1. 2 a day for the sprint, or keep 3 a day (more data, less build time per Short)?
2. Is a loud, opinionated commentary voice on-brand, or should R1 keep the calm voice?
3. OK to spend on any paid tools (stock footage, AI video)? Everything above is free-tools only.
4. Should I start building R3 and R2 prototypes now, ahead of 28 Nov?

---

## 6. Honest limits
- **I cannot prove why the drop happened.** Public data shows when and how broadly, not why. The originality update is a plausible and well-sourced candidate. The sprint exists to separate the possibilities.
- Competitor data comes from search results and hashtag feeds, which over-represent winners. I could not see any competitor's retention or impressions.
- Our own mosaic labels cover 19 Shorts picked from the extremes. They describe, they do not prove.
- Shorts from 6-8 Nov may still be growing.
- Agent C's news facts and the agents' per-topic "verified" tags need a fetch-and-check before scripting.
- Agent B could not open YouTube's own 1 Oct post. I confirmed the announcement through several news reports instead.

---

## 7. How to pull per-Short Studio analytics (works today)

In the Studio tab, open the "See more" link under **Analytics > Content > Top Shorts**, or navigate to this URL by setting `location.href` from an `evaluate_script` call (direct navigation tool calls hang on Studio):

```
https://studio.youtube.com/channel/UCfLjJwaxD7VhKwfSmTDQv3Q/analytics/tab-content/period-default/explore?entity_type=CHANNEL&entity_id=UCfLjJwaxD7VhKwfSmTDQv3Q&ur_dimensions=CREATOR_CONTENT_TYPE&ur_values=%27SHORTS%27&ur_inclusive_starts=&ur_exclusive_ends=&time_period=4_weeks&explore_type=TABLE_AND_CHART&metrics_computation_type=DELTA&metric=EXTERNAL_VIEWS&granularity=DAY&t_metrics=EXTERNAL_VIEWS&t_metrics=ENGAGED_VIEWS&t_metrics=SHORTS_FEED_IMPRESSIONS&t_metrics=SHORTS_FEED_IMPRESSIONS_VTR&t_metrics=RATINGS_LIKES&t_metrics=SHARINGS&t_metrics=SUBSCRIBERS_NET_CHANGE&dimension=VIDEO&o_column=EXTERNAL_VIEWS&o_direction=ANALYTICS_ORDER_DIRECTION_DESC
```

`time_period` values that work: `4_weeks`, `current_month`, `minus_1_month`, `lifetime`. (`7_days` does not.) The table shows the top 50 rows; each row is duration, title, views, engaged views, stayed to watch, likes, shares, subscribers. Wait about 9 seconds after loading. The page sometimes renders blank; reload it.

---

## 8. Files
- Our data: `research_nov8/D/` (`channel_shorts.jsonl`, `master.csv`, `visual_labels.csv`, `timeline_views.png`, `mosaics/`, `stats_output.txt`)
- Studio pulls: `research_nov8/studio_oct_rows.json`, `studio_nov_rows.json`, `studio_28d_rows.json`, `studio_lifetime_rows.json`, `heatmap.png`
- Competitor teardown: `research_nov8/A/` (`channel_stats.json`, `all_shorts.json`, `mosaics/`, `top30_titles.json`)
- Formats and policy: `research_nov8/B/report.md`, `videos_clustered.csv`
- Topic demand: `research_nov8/C/menu.json`, `stats.json`, `shorts_dataset.csv`
