# Per-Short Studio analytics (views, engaged views, stayed to watch)

Use this to judge any recipe; do not judge by views alone. Works in CD's real Chrome via the chrome MCP (tested 8 Nov 2026).

1. In the Studio tab, `evaluate_script` with `location.href = <URL>` (the navigate tool hangs on Studio).
2. URL (Shorts only, per-video table):
   `https://studio.youtube.com/channel/UCfLjJwaxD7VhKwfSmTDQv3Q/analytics/tab-content/period-default/explore?entity_type=CHANNEL&entity_id=UCfLjJwaxD7VhKwfSmTDQv3Q&ur_dimensions=CREATOR_CONTENT_TYPE&ur_values=%27SHORTS%27&ur_inclusive_starts=&ur_exclusive_ends=&time_period=4_weeks&explore_type=TABLE_AND_CHART&metrics_computation_type=DELTA&metric=EXTERNAL_VIEWS&granularity=DAY&t_metrics=EXTERNAL_VIEWS&t_metrics=ENGAGED_VIEWS&t_metrics=SHORTS_FEED_IMPRESSIONS&t_metrics=SHORTS_FEED_IMPRESSIONS_VTR&t_metrics=RATINGS_LIKES&t_metrics=SHARINGS&t_metrics=SUBSCRIBERS_NET_CHANGE&dimension=VIDEO&o_column=EXTERNAL_VIEWS&o_direction=ANALYTICS_ORDER_DIRECTION_DESC`
3. `time_period` that works: `4_weeks`, `current_month`, `minus_1_month`, `lifetime`. `7_days` redirects to a blank page. Wait ~9 s; reload if blank. The table lists the top 50 rows.
4. Parse `document.body.innerText`: after the `Total` line (8 tokens), each row is duration, title, views, views%, engaged, engaged%, `—`, `—`, stayed-to-watch%, likes, likes%, shares, shares%, subs, subs% (15 tokens). Save with `evaluate_script filePath`.
5. The "When your viewers are on YouTube" heatmap is an image: scroll to it on `.../analytics/tab-build_audience/period-default` and screenshot.
6. Never change an already-Scheduled Short through automation (see youtube-schedule.md Recovery).
