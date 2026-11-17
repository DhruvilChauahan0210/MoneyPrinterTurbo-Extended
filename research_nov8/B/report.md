# Research B: 2026 faceless Shorts formats and the 2026 Shorts algorithm
Date of research: 8 Nov 2026. Author: research agent B. Research only; no Studio or schedule access.

Legend: [FACT-OFFICIAL] = YouTube's own page/post read via fetch. [FACT-DATA] = I pulled it with yt-dlp. [REPORTED] = secondary article quoting YouTube. [VENDOR] = vendor/blog study (weak). [INFERENCE] = my reasoning.

---------------------------------------------------------------------------------------------------
## PART 1. How the 2026 Shorts system works (evidence, with dates)

### 1.1 What counts as a view (changed twice)
- [FACT-OFFICIAL] 31 Mar 2025: a Shorts view = Short starts or replays, no minimum watch time; the old definition was kept as "Engaged views" (YouTube Help).
- [FACT-OFFICIAL] YouTube blog, 19 Aug 2026 (effective 24 Aug 2026), https://blog.youtube/inside-youtube/engaged-views-youtube-explained/ : a "view" now counts from the first frame on ALL formats; an "engaged view" is the previous definition (watching past the initial seconds, or clicking to watch). Earnings depend on engaged views. Analytics (CTR, AVD, retention) are still mostly based on engaged views. "Recommendations are unchanged."
- Consequence for CD [INFERENCE]: public view counts are now inflated by swipe-aways; the only honest health metric is "stayed to watch / engaged views", which CD already tracks (39% -> 28-34%).

### 1.2 Viewed vs swiped away ("How many chose to view")
- [FACT-OFFICIAL] YouTube Help, Shorts "Content tab analytics tips" (support.google.com/youtube/answer/12942217): "How many chose to view" = "the percentage of times that viewers viewed your Shorts versus swiped away." Also shows "Shown in feed". YouTube gives NO numeric target. It tells you to compare like-with-like formats and to "avoid comparing each video against a viral hit".
- [VENDOR/OLD DATA] Paddy Galloway thread (Apr 2023 text, 33 channels, 5,400 Shorts, 3.3B views, https://threadreaderapp.com/thread/1646898356419981315.html): Shorts under 60% viewed-vs-swiped rarely performed; best performers 70-90%; most Shorts 20-40 s; longer Shorts had higher averages; AVD > 50 s averaged 4.1M views; likes/comments/shares had no strong relationship with performance; long-form converts more subs per 10K views than Shorts except for channels > 1M subs. Self-described as early research. Treat the 60% / 70-90% numbers as a rule of thumb, not YouTube policy. The "70-90%" figure that appears in 2026 blogs traces to this.
- YouTube's general recommender page (youtube.com/howyoutubeworks/recommendations): signals include viewing behaviour, likes/dislikes, subscriptions and feedback "including from satisfaction surveys", plus channel "reputation and quality". It does not mention Shorts specifically.
- [REPORTED] Todd Sherman (Shorts lead, Creator Insider, Aug 2023): Shorts are shown to a seed audience first, then reach grows or tapers on their response; no ideal length; no daily-post threshold that unlocks reach (via OutlierKit, which sells a product; quote is from 2023).

### 1.3 Length
- [FACT-OFFICIAL] Shorts can be up to 3 minutes since 15 Oct 2024 (YouTube Help, via OutlierKit). YouTube says there is no ideal length.
- [FACT-DATA] In my sample (Part 2) the recent 1M+ Shorts from small channels are mostly SHORT: of 111 football Shorts from channels < 100K subs, median duration 17 s; 46 are <= 15 s, 58 are 16-30 s, only 6 are 31-45 s and 1 is 46+ s. CD's 27-35 s is in the thinnest tail of the viral sample. CAVEAT: hashtag feeds over-represent short loop-able clips; this is not proof 30 s cannot work (CD's own data says 25-45 s performs best for CD).
- [VENDOR] Metricool (29 Jul 2026, 799,718 videos / 71,177 accounts, https://metricool.com/youtube-trends/): average Shorts view duration fell ~67% to about 16 s (32 s shorter than a year earlier) while Shorts views rose 127%. Interpretation [INFERENCE]: the average Short now gets watched for ~16 s, so a 30 s video starts life needing above-average retention.

### 1.4 Loops / rewatch
- [FACT-OFFICIAL] Engaged views "not including any loops" (YouTube Content report glossary, per search summary); replays count as views since Mar 2025.
- [VENDOR] Looping can push average percentage viewed above 100% (vidIQ, 1of10, fluxnote blogs). No primary dataset found. Treat "loop" as a plausible but unproven lever. Benchmarks quoted (85-95% APV; 100%+ for <30 s) are rules of thumb with no source data.

### 1.5 Titles, thumbnails, first frame
- [FACT-OFFICIAL/REPORTED] Custom thumbnails for Shorts rolled out 24-25 Jul 2026 (Creator Insider, Rene Ritchie; PPC Land https://ppc.land/youtube-ends-2-year-wait-for-shorts-thumbnails-but-blocks-a-b-testing/): YPP channels first, desktop only, no A/B test. They show on the homepage and channel Home/Shorts tabs, NOT in the swipe feed. In the feed, the first frame is the "thumbnail". So for CD: the first frame (and first 1-2 s) must carry the hook; no title is visible in the feed except the caption overlay.
- [FACT-OFFICIAL] Custom feeds (22 Oct 2026, US English viewers) rely on titles/descriptions matching viewer text prompts (air.io Oct 2026 summary) - minor for CD.

### 1.6 Policy: inauthentic / mass-produced / reused / originality (this matters most for CD)
1. [FACT-OFFICIAL] YouTube monetization policies page (support.google.com/youtube/answer/1311392): since 15 Jul 2025 "repetitious content" renamed "inauthentic content". Not allowed: "Image slideshows, templated storylines, or scrolling text with minimal or no narrative, commentary, or educational value"; "AI-generated content made with generic or unoriginal templates giving the impression of mass production". Allowed: same intro/outro if main content varies, series where each video has a distinct storyline/concept. Applies to the channel, not only to one video. Reused content ("repurpose content already on YouTube or another online source"): applies "even if you have permission"; clips "edited together with little or no narrative" not allowed; reaction/commentary allowed. 15 Jul 2025: no change to reused-content policy.
2. [REPORTED] Tubefilter 13 Jul 2026: policy text reworded into 3 named groups of non-monetizable content: (a) Generic or Repetitive (template look, "image slideshows and templated storylines", characters repeatedly in the same situation with the same outcome); (b) Unsatisfying or Off-putting (emotionally manipulative formulas, interchangeable mimic formats, AI clips stitched without a logical arc, realistic fake celebrity death); (c) AI personas on sensitive topics (health, legal, finance, politics). Said to be clarification, not new rules. The article lists no TTS/AI voice rule.
3. [REPORTED] 1 Oct 2026, YouTube Help community post "Prioritizing original content on Shorts" (thread 470890423; page itself would not load for me, so wording is from 9to5Google 2 Oct 2026 and PPC Land): "we're updating our recommendation systems to further prioritize original content and reduce the reach of content re-uploaded from other creators." Channels "primarily aggregating or re-uploading other creators' videos" will "likely see less distribution within the Shorts feed". "Rather than making minor technical edits or template-based changes simply to alter a video". Creator Insider video by Rene Ritchie (per Search Engine Journal via Relevant Audience): voice-over that only describes on-screen action, minor technical edits and template-based bulk changes are NOT enough; compilations/highlight reposts count as unoriginal; use the Posts tab to share others' videos; channels can recover, "the recommendation system will re-evaluate reach" with no time given. Channel-level judgement. Rollout date not stated.
   - Did NOT address: still photos, slideshows, AI voices, own-edited footage.
4. [FACT-OFFICIAL] Aug 2026 YPP changes (YouTube blog 10 Aug 2026, effective 1 Feb 2027): new-entry bar 8,000 watch hours or 20M qualified Shorts views / 90 days; existing members must keep 10M Shorts views / 90 days to keep Shorts revenue share (below that, Shorts revenue pauses, long-form earnings stay). Not directly a reach factor, but it means Shorts-only monetization is effectively off the table for a small channel; reach and subscribers are the goal (plus the new "shopping/brand-deal" incentives YouTube says it will detail).
5. Other late-2026 items: 16 Oct 2026 Shorts bonus pilot (invite-only, 6 countries: US, UK, DE, BR, JP, KR); 23 Sep 2026 "Shorts series" (structured series on TV); 29 Oct 2026 test of 30-day fix window instead of immediate termination for spam (air.io / OutlierKit lists, YouTube Help links).

How CD's current pipeline maps to this [INFERENCE, not verified by YouTube]:
- Photo slideshow with slow zoom + stock EricNeural TTS reading facts + 8-9 same-shaped beats + same caption/music, 3x/day: this is almost literally "image slideshows ... templated storylines ... generic or unoriginal templates giving the impression of mass production". That is a MONETIZATION risk (channel-wide) and the recommender text above says template-based changes do not count as original.
- 6-s official match-highlight clips: "highlight reposts" fall under the Oct 1 de-prioritization if they are unmodified third-party footage. Own commentary helps only if it adds an argument, not narration of what is on screen.
- The timing does not perfectly match the collapse (policy 1 Oct; Jul 180K -> Sep 80K -> Oct 24-28 ~1,000/Short -> 29 Oct 40-320), so there are probably other causes (retention drop 39% to ~28-34%, hook, saturation). The honest statement is: the Oct 1 change is a plausible contributor, not proven.

### 1.7 Posting frequency (3/day vs 1/day) - is there evidence of a penalty?
- [VENDOR, large sample] Metricool 29 Jul 2026: per-post performance best at 2-4 Shorts/week; channels posting ~5 Shorts/month had long-form videos averaging 8,789 views (46% above the 5,985 global average); channels posting 35+ Shorts a month fell back to the level of channels posting none (4,364). Correlation only, and it measures effect on LONG-FORM views, not on the Shorts themselves. Not a measure of a penalty for 3/day Shorts.
- [FACT-OFFICIAL via report] Sherman 2023: no threshold of daily posts that unlocks reach.
- [VENDOR, weak] FlowShorts (sells auto-posting): says 3/day beats 1/day (+3,500 vs +800 subs/month) from "500+ channels" with no source; its spam thresholds (10+/day) are unsourced and internally inconsistent. I found NO measured evidence that posting 3/day low-retention Shorts lowers the performance of later Shorts. What the sources support is a PER-VIDEO effect: a Short that gets swiped away is not pushed further. The channel-level mechanism I can support is the quality/"reputation" signal in YouTube's recommender page, plus the inauthentic-content classifier, which is channel-level and is triggered by sameness, not by the posting count itself. [INFERENCE] Mass production of near-identical Shorts is the risk factor, so frequency x sameness matters more than frequency alone.
- Practical read: with 45 Shorts already scheduled, you cannot test this on the existing queue; from 28 Nov run 2/day for 2 weeks against the 3/day history and compare "stayed to watch" per format, not raw views.

### 1.8 Timing for an India + UK + US audience
- [VENDOR] PostEverywhere (6,500+ Shorts, creator's local time, lift vs the channel's own median of 20 neighbouring Shorts, https://posteverywhere.ai/blog/best-time-to-schedule-youtube-shorts): best windows Mon 10-13 (+21%), Sun 08-11 (+14%), Fri 16-19 (+12%), Sat 20-23 (+12%); weakest: Thursday -11%, evening 18-21 -8%. Every day within 11% of baseline; no country split; the page's own caveat: YouTube says publish time does not affect long-term performance. Date inconsistent (Nov 2025 vs data to Oct 2026).
- [VENDOR] SocialPilot (301K videos, 27K channels): Shorts 12-14 or 18-19 local time, Thu-Sat; poor 03-07 and Sunday evening. Internally inconsistent.
- India-specific pages (fluxnote, wscubetech, timetopost): evening 18-22 IST most common claim, with no methodology; "7-9 PM IST" not confirmed by any dataset.
- No source tested a mixed IN+UK+US audience. CD's slots (13:00 / 17:00 / 21:00 IST) = 07:30 / 11:30 / 15:30 UTC = 07:30 / 11:30 / 15:30 UK (GMT in Nov) = 02:30 / 06:30 / 10:30 ET. Effects found elsewhere are small (<= ~10%), so timing is a second-order lever [INFERENCE]; the 21:00 IST slot is the only one landing in UK afternoon and US morning. Use Studio "When your viewers are on YouTube" for the real answer.

### 1.9 Subscriber conversion (all weak)
- Galloway 2023: long-form converts more subs per 10K views than Shorts except for channels > 1M subs. Blogs quote anywhere from 0.05% to 1.9% of Shorts views converting; no primary source found. CD has 99% of watch time from non-subscribers: nothing to anchor on, so measure it per format in Studio.

### Weak sources to ignore
vidIQ/OutlierKit/Fluxnote/FlowShorts/aituber.app/ytshark blogs that assert signal weights, "800 views test", spam thresholds, "50 s AVD" etc. without data. Treated here only where traceable to a primary document.

---------------------------------------------------------------------------------------------------
## PART 2. Format discovery with yt-dlp

### Method (and its limits)
- yt-dlp YouTube search with `sp=` filters returned only normal videos (not Shorts) for the Shorts-length filter, so I could not use "search sorted by views + Shorts + this month". I fell back to `https://www.youtube.com/hashtag/<tag>/shorts` feeds (50 tags: football/messi/ronaldo/mbappe/yamal/haaland/whatif/footballquiz/guesstheplayer/footballfacts/footballstory/ballondor/footballedit/footballai/footballcartoon + nba, nfl, f1, boxing, ufc/mma, cricket, history, finance, reddit/stories, quiz, top5/top10/ranking, 3danimation/aianimation, facts). Each feed gives up to 60 Shorts with view counts. I then enriched 800+ candidates (views >= 1M) one by one with yt-dlp to get channel, subscriber count (current), duration, upload date.
- BIAS: hashtag feeds are popularity-ranked and skew toward the hashtag-stuffing, loop-friendly, short Shorts. They do not show what is NOT viral. Subscriber counts are today's counts (a channel may have grown). All view numbers are public views and since 24 Aug 2026 include swiped-away starts, so are not comparable to pre-Aug counts [FACT-OFFICIAL].
- Filter used: uploaded >= 15 Sep 2026, duration <= 61 s, channel < 100K subs, views >= 1M. Result: 178 videos in `videos_small_channels_1M_plus.csv` (target was 40+). Clustered set (views >= 500K, all channel sizes): `videos_clustered.csv`. Raw: `raw/` (hashtag jsonl, enriched jsonl/json).
- Non-football niches were sampled more thinly (top ~9 per hashtag, then date-filtered), so their counts are small.

### Cluster table (football hashtag sample, uploaded >= 15 Sep 2026, <= 61 s, views >= 500K)
(n = videos in cluster, n_small = from channels < 100K subs)

| # | Cluster | n | n_small | Median views (all / small) | Median length | Retention device | Cost for CD |
|---|---|---|---|---|---|---|---|
| 1 | AI/3D comedy skit with the Haaland-Mbappe-Yamal cast (ice cream, waterslide, cake, lollipop, rope prank, parody) | 88 | 46 | 5.3M / 3.9M | 16 s | wait-for-the-ending gag, payoff on last second, rewatch | High: needs AI video (photoreal clip, see mosaic) or 3D animation; not producible with photos+TTS |
| 3 | Find-the-player / guess quiz ("FIND YAMAL RONALDO NEYMAR", "which footballer is under which battery") | 15 | 12 | 4.5M / 3.6M | 15 s | countdown bar + question + reveal; viewer replays to find the answer | LOW: static grid image + progress bar; Remotion-native |
| 4 | Pick-one / fan-poll ("which player fits next to Georgina?", "who will win?") | 12 | 5 | 5.0M / 2.8M | 17 s | question as hook, comment bait | Low-medium |
| 5 | Versus bracket / elimination ("A VS B VS C VS Messi VS Ronaldo", "who are you helping") | 33 | 9 | 2.4M / 3.0M | 25 s | elimination / pick, long-running series | Low-medium (faces + stats cards) |
| 6 | Kindness / charity animated story ("Poor and Kind Ronaldo helps everyone") | 11 | 5 | 2.7M / 2.5M | 23 s | sympathy twist; same template reused on many players | Medium (animation), AND matches the YouTube "templated/emotionally manipulative" language |
| 7 | Ballon d'Or 2026 news/reaction (Kane wins, Yamal/Mbappe react) | 13 | 7 | 1.9M / 1.9M | 15 s | topical spike | Low-medium; time-limited |
| 8 | Facts explainer ("Why are goalkeeper gloves so sticky?", shin guards, boots, spitting water) | 7 | 5 | 2.3M / 2.3M | 19 s | curiosity question in the first line | Low: TTS + photos/short real clips; needs sourced facts |
| 9 | Edit / goals compilation ("Ha Ha Ha" Haaland edit) | 10 | 7 | 2.6M / 2.3M | 24.5 s | viral sound | Low, but reused-footage risk (Oct 1 policy) |
| 10 | Match result / prediction ("Spain beat Croatia 2-1", "Barcelona vs Man City prediction") | 9 | 5 | 2.8M / 2.8M | 16 s | scoreline hook | Low; footage rights risk |
| 11 | Story / biography animation (Yamal journey, "what happened to Ronaldo and IShowSpeed's plane") | 2 | 1 | n/a | 25 s | story | Medium |
| 12 | Other football | 24 | 9 | 3.8M / 3.4M | 18 s | mixed | - |
| X | Non-football spam loops ("POWER OF JESUS" identical title across 20+ channels, 2-29M views) | 18 | 10 | 5.2M / 5.6M | 23 s | unknown, looks like a coordinated template / possibly inflated | Ignore; do not copy |

Non-football niches (recent, <= 61 s, hashtag samples; small n, treat as anecdotes):
- Basketball: "Ranking 1 in a Trillion Basketball Moments" 44.2M views, 64K-sub channel, 25 s (JQ440kmooUU): ranking/rating of other people's trick-shot clips with a face-on-camera host holding "8/10" cards. Not faceless; clips credited to other creators. Median of the 8 recent basketball examples 16.8M views.
- Ranking format generally (12 recent): "Ranking the best volcano throwing moments" 28M (42K subs), "Ranking the most hilarious expensive mistakes" 20M (13.7K subs): rank X compilation clips, 23-42 s, median 15.4M. Ranking-compilation = a clip-reuse format, exposed to the Oct 1 policy.
- 3D/AI animation (11 recent, all < 100K subs, median 7.2M views, 25 s): includes "She was just trying to look normal..." 20.6M (49K subs, 39 s) - emotional AI animated story.
- NFL (10), cricket (30, but many are the spam loops), F1 (9), MMA/boxing (6), history (4), finance (1), reddit stories (3), what-if (9): too few or too noisy to size a cluster. Items worth knowing: "What if you woke up 6 feet underground?" 3.2M (7K subs, 45 s, what-if physics, TTS explainer); F1 "Marc Marquez aura farming" 14.3M (21K subs, 19 s). Stories: one Reddit-story-with-illustrations Short 2.0M (10.7K subs).
- I found no clean evidence of a "countdown top-5 football" cluster, a text-message story cluster or a tactical-board cluster in these feeds (the top5/top10 hashtags returned non-football ranking compilations). Absence in this sample is not proof of absence.

Other measured facts from the 111-video small-channel football set: median views 3.03M; median likes/views 0.47% (low, consistent with Galloway: likes are not the driver); only 1 of 111 is over 45 s.

### What the 4 downloaded videos actually look like (mosaics in `mosaics/`)
1. `vzFWN2AgxaU` - Haaland + Mbappe waterslide skit, 77.3M views, 50.4K-sub channel, 15 s, uploaded 18 Oct 2026: photoreal AI-generated video, multiple shots, no text overlay, no photos. Format = pure AI video. We cannot reproduce it with photos + TTS.
2. `HoHyf09sV80` - "FIND YAMAL RONALDO NEYMAR", 17.0M views, 63.1K subs, 15 s, uploaded 20 Oct 2026: one static puzzle grid (5x5 of caricatured faces, one different), a title banner, "Subscribe/Like" stickers, a progress bar as the timer, three rounds (Yamal, Ronaldo, Neymar) in 15 s. Zero footage, zero voice needed. This is the cheapest format in the whole dataset to rebuild in Remotion.
3. `JQ440kmooUU` - "Ranking 1 in a Trillion Basketball Moments", 44.2M, 64K subs, 25 s, uploaded 1 Oct 2026: a man on camera rating other people's clips "8/10", "6/10" in between the clips (UGC credited with handles, then NBA broadcast clips). Not faceless, reuse-heavy.
4. `sD3gq1WaqFk` - "Why Are Goalkeeper Gloves So Sticky?", 3.8M, 10.5K subs, 19 s, uploaded 12 Oct 2026: original real-world footage of resin, gloves in POV, goalkeeper actually filming; includes on-screen text. Needs filming.

Take-away [INFERENCE]: on the 4 I looked at, the high-view small-channel Shorts are either (a) AI-generated video, (b) cheap puzzle/graphic constructions with a visible timer, or (c) original footage. None is a "photo slideshow + narration", which is what CD makes.

---------------------------------------------------------------------------------------------------
## PART 3. Caveats on what could not be verified
- The official 1 Oct 2026 post could not be fetched (HTTP socket error); wording is from 9to5Google/PPC Land quoting it.
- Sources disagree on the date of the view-count change (OutlierKit lists a 17 Aug TeamYouTube post; the blog is 19 Aug, effective 24 Aug).
- No dataset exists in what I found that splits time-of-day by India/UK/US, or that measures a channel-level penalty for 3 Shorts/day.
- Subscriber counts in the CSVs are current; I cannot tell how big the channel was at upload.
- I cannot see retention, swipe rate or traffic source for any competitor Short.

---------------------------------------------------------------------------------------------------
## PART 4. Ranked list: 8 formats a faceless football channel could test (from 28 Nov)

Ranking = evidence of reach in this dataset x fit with policy (original, non-templated) x cost with our stack. Test each with 6-10 Shorts, 2/day max, and read "stayed to watch" not views. All use a visible hook on frame 1 and 12-25 s.

1. Find the player (puzzle with a countdown bar) - evidence: cluster 3, 12 small channels, median 3.6M, 15 s. Recipe: Remotion composition, a 5x5 grid of 25 player photos (cropped faces from the DDG/Google photo step) with one subtly different (different year or different player), banner "FIND HAALAND", a progress bar as the timer, a second of silence/tick sound, then circle the answer; ffmpeg only for audio mix. Vary the puzzle each time (different rule, different players) so it is not one template.
2. Who is it? silhouette/blur/clue guess - evidence: adjacent to cluster 3 (guess-the-player, 2.7M-4.5M examples in guesstheplayer/footballquiz tags). Recipe: Remotion with blurred-to-clear photo reveal over 10 s, three TTS clues with a visible number counter, reveal and one-line fact; ffmpeg for the TTS timing.
3. "Pick one" duel with a hard stat pair (Player A vs Player B, 5 stats, viewer picks) - evidence: clusters 4-5, medians 2.8M-3.0M small channels, 17-25 s. Recipe: two photos split-screen in Remotion, stats animate in as bars, TTS says "pick before the bar ends", end on a hard number; no clips needed.
4. Elimination bracket "6 players, one survives" - evidence: cluster 5 (33 videos, up to 16M). Recipe: Remotion grid of 6 photos, one gets a red X every 3-4 s with a stat reason in TTS, final winner zoom; the same engine as #3, with 25 s runtime.
5. Curiosity fact explainer "Why do goalkeepers wear sticky gloves / why are shin pads small" - evidence: cluster 8, 5 small channels, 2.3M median, 19 s. Recipe: TTS hook question in the first 2 s, 3 beats of photo/short clip + one on-screen stat card (Remotion), a loop line that returns to the first question for rewatch; each fact must be sourced and original in framing.
6. Hot-topic news explainer with one argument ("Kane's Ballon d'Or: the 3 numbers that decided it") - evidence: cluster 7, 7 small channels, 1.9M median, 15 s, but time-limited. Recipe: photo + 3 stat cards + TTS argued position (your own opinion = originality per the Oct 1 guidance), Remotion cards; ffmpeg mix.
7. What-if with a visible simulation result ("What if Messi had stayed at X: goals per season chart") - evidence: only the generic what-if explainer (3.2M, 7K subs, 45 s) in this dataset; CD already has 7 s What-Ifs. Recipe: one photo + animated Remotion chart that resolves to a number in the last seconds; TTS asks the question first; keep to 15-20 s.
8. Kindness/charity animated story or AI-skit style - evidence: clusters 1 and 6 are the biggest by volume (88 and 11 videos), but they need AI video/animation and cluster 6 sits right on YouTube's "templated / emotionally manipulative" wording. Recipe if tried: 3-4 AI-generated stills animated with Remotion Ken Burns plus a one-line TTS payoff; test at most 5 videos and check monetization/reach before scaling. Lowest rank because of cost and policy risk, not because of lack of views.

Cross-cutting recommendations [INFERENCE]
- Make each Short structurally different (puzzle vs duel vs explainer); do not run the same 8-beat slideshow 3x/day.
- Put a visible timer/number or a question in frame 1, because the first frame is the thumbnail in the feed.
- Cut the match-highlight clips unless you add an argument; prefer own graphics, photos plus your own stats.
- Shorten test videos to 12-25 s: 104 of 111 viral small-channel football Shorts are <= 30 s.
- Re-check Studio: "How many chose to view" per format and "Shown in feed" (new metric) to separate a distribution drop from a retention drop.

## Files
- /Users/dhruvilchauhan/Developer/CDH/MoneyPrinterTurbo-Extended/research_nov8/B/report.md (this)
- .../B/videos_small_channels_1M_plus.csv (178 videos: url, title, channel, subs now, views, likes, duration, upload date)
- .../B/videos_clustered.csv (all channel sizes, views >= 500K, cluster labels)
- .../B/cluster_table.json
- .../B/mosaics/*.jpg (4 mosaics)
- .../B/raw/ (hashtags/*.jsonl, enriched*.jsonl, enriched_everything.json)
- .../B/scratch/dl/ (4 downloaded videos, 0.6-2.5 MB each)
