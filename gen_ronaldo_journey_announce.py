#!/usr/bin/env python3
"""One-off: 30s Ronaldo career-journey SERIES ANNOUNCEMENT short (upload today).

Longer than the usual 15s format on CD's explicit request. Era-matched footage:
each script sentence carries era keywords that the semantic matcher aligns to an
era-specific youtube_footage_query (Sporting teen -> United -> Madrid -> Juve/
Al Nassr/Portugal), so the age of Ronaldo on screen tracks the narration.
"""
import json
import os

from gen_15to21aug import NEG, HOOK_NEG

SLUG = "ronaldo_journey_announce"

HOOK = "DOCTORS ALMOST ENDED HIS CAREER \U0001F633"
CTA = "SERIES STARTS 25 AUGUST \U0001F447"

SUBJECT = (
    "The full career journey of Cristiano Ronaldo from a one-room house in Madeira and a "
    "teenage heart operation, to Manchester United, Real Madrid, Juventus, Al Nassr and "
    "Portugal's first trophy, announcing a daily series telling the whole story"
)

# ~67 words -> ~29s at Eric Neural voice_rate 1.2
SCRIPT = (
    "At fifteen, doctors told Ronaldo his racing heart could end football forever. "
    "He grew up in Madeira in one room, and never stopped running. "
    "United signed him at eighteen. Ferguson made him a Ballon d'Or winner. "
    "Real Madrid paid a world record and got four hundred and fifty goals. "
    "Then Juventus, Al Nassr, and Portugal's first ever trophy. "
    "From August twenty fifth, the full story, every single day."
)

POSITIVES = [
    "a real photograph of Cristiano Ronaldo the footballer",
    "a skinny teenage Cristiano Ronaldo in a green and white Sporting Lisbon jersey",
    "young Cristiano Ronaldo in a red Manchester United jersey",
    "Cristiano Ronaldo in a white Real Madrid jersey",
    "Cristiano Ronaldo in a red Portugal jersey",
    "Cristiano Ronaldo in a yellow and blue Al Nassr jersey",
    "a tight close up of Cristiano Ronaldo's face",
]

# ordered to mirror the script sentences so semantic selection tracks his age
QUERIES = [
    "teenage Cristiano Ronaldo Sporting Lisbon 2002 skinny close up",
    "young Cristiano Ronaldo Madeira early years close up face",
    "young Cristiano Ronaldo Manchester United 2004 stepovers close up",
    "Cristiano Ronaldo Manchester United 2008 Ballon d'Or close up",
    "Cristiano Ronaldo Real Madrid goal celebration close up slow motion",
    "Cristiano Ronaldo Real Madrid Champions League trophy close up",
    "Cristiano Ronaldo Juventus close up face serious",
    "Cristiano Ronaldo Al Nassr yellow jersey close up",
    "Cristiano Ronaldo Portugal Euro 2016 trophy celebration close up",
    "Cristiano Ronaldo Portugal close up face serious",
]

COVER = (
    "a tight close up of a young Cristiano Ronaldo's face looking toward the camera, "
    "intense and serious, his face filling the frame, sharp and clear, no other players"
)

TERMS = (
    "Cristiano Ronaldo, Ronaldo career journey, young Ronaldo Sporting, Ronaldo Manchester "
    "United, Ronaldo Real Madrid, Ronaldo Al Nassr, Ronaldo close up face"
)

cfg = {
    "defaults": {
        "video_aspect": "9:16",
        "video_concat_mode": "semantic",
        "video_transition_mode": "None",
        "video_clip_duration": 2,
        "video_count": 1,
        "video_source": "image_search",
        "video_language": "",
        "voice_name": "en-US-EricNeural-Male",
        "voice_volume": 1.2,
        "voice_rate": 1.2,
        "bgm_type": "",
        "bgm_volume": 0.0,
        "subtitle_enabled": True,
        "subtitle_position": "custom",
        "custom_position": 74.0,
        "font_name": "MicrosoftYaHeiBold.ttc",
        "text_fore_color": "#FFFFFF",
        "text_background_color": True,
        "font_size": 56,
        "stroke_color": "#000000",
        "stroke_width": 1.5,
        "enable_word_highlighting": True,
        "word_highlight_color": "#FFD700",
        "max_chars_per_line": 18,
        "max_lines_per_subtitle": 2,
        "max_words_per_subtitle": 2,
        "segmentation_method": "sentences",
        "min_segment_length": 18,
        "enable_image_ranking": True,
        "image_ranking_min_score": 0.22,
        "enable_subject_gate": True,
        "subject_positive_labels": POSITIVES,
        "subject_negative_labels": NEG,
        "subject_gate_margin": 0.1,
        "subject_gate_abs_floor": 0.35,
        "segment_reuse_penalty": 0.25,
        # 30s script needs ~2x the footage of the usual 15s short
        "max_video_reuse": 3,
        "enable_timed_sync": True,
        "enable_grayscale": False,
        "video_clip_ratio": 0.0,
        "cover_min_keep": 0.5,
        "enable_youtube_footage": True,
        "youtube_footage_queries": QUERIES,
        "youtube_max_videos": 16,
        "youtube_clip_len": 3.0,
        "youtube_clips_per_video": 6,
        "youtube_max_clips": 84,
        "youtube_max_height": 1080,
        "footage_video_bonus": 0.12,
        "footage_min_fraction": 1.0,
        "image_motion_style": "varied",
        "enable_color_grade": True,
        "enable_hook_card": True,
        "hook_text": HOOK,
        "hook_cover_term": COVER,
        "hook_min_similarity": 0.2,
        "hook_require_video": False,
        "hook_negative_labels": HOOK_NEG,
        "hook_negative_margin": 0.08,
        "hook_overlay_opacity": 0.25,
        "hook_duration": 1.5,
        "enable_sfx": True,
        "sfx_volume": 0.5,
        "enable_cta": True,
        "cta_text": CTA,
        "loop_seamless": False,
        "loop_follow_tag": False,
        "loop_tight_trim": True,
        "n_threads": 2,
        "paragraph_number": 1,
    },
    "videos": [
        {"video_subject": SUBJECT, "video_script": SCRIPT, "video_terms": TERMS}
    ],
}

root = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(root, f"batch_{SLUG}.json"), "w") as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)
print(f"wrote batch_{SLUG}.json  ({len(SCRIPT.split())} words)")
