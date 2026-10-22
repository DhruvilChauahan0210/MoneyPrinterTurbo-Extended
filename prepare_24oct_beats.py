import copy
import json


def set_plan(path, beats):
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    data["defaults"].update(
        enable_youtube_footage=False,
        youtube_only_media=False,
        youtube_footage_queries=[],
        beat_plan=beats,
    )
    data["videos"][0]["beat_plan"] = beats
    data["videos"][0]["beat_shared_clips"] = []
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


set_plan(
    "batch_mbappe_onzedor26.json",
    [
        {"says": "Six days before the Ballon d'Or,", "visual": "Kylian Mbappe Real Madrid close up", "images": ["Kylian Mbappe Real Madrid close up 2026", "Kylian Mbappe Real Madrid portrait"], "clips": []},
        {"says": "Kylian Mbappe has crushed another major vote.", "visual": "Kylian Mbappe holding an award", "images": ["Kylian Mbappe Onze d'Or 2026 award", "Kylian Mbappe holding trophy award"], "clips": []},
        {"says": "He won the twenty twenty-six Onze d'Or with forty-eight point two percent,", "visual": "Kylian Mbappe smiling with an award", "images": ["Mbappe Onze d'Or 2026 48.2 percent", "Kylian Mbappe award 2026"], "clips": []},
        {"says": "while Joao Neves finished on eleven point nine", "visual": "Joao Neves PSG close up", "images": ["Joao Neves PSG close up 2026", "Joao Neves Paris Saint Germain portrait"], "clips": []},
        {"says": "and Kvaratskhelia on ten point eight.", "visual": "Khvicha Kvaratskhelia PSG close up", "images": ["Khvicha Kvaratskhelia PSG close up 2026", "Kvaratskhelia Paris Saint Germain portrait"], "clips": []},
        {"says": "Mbappe topped both La Liga and the Champions League for goals,", "visual": "Kylian Mbappe celebrating for Real Madrid", "images": ["Kylian Mbappe Real Madrid goal celebration 2026", "Mbappe Champions League Real Madrid celebration"], "clips": []},
        {"says": "then won the World Cup Golden Boot.", "visual": "Kylian Mbappe France World Cup Golden Boot", "images": ["Kylian Mbappe World Cup 2026 Golden Boot", "Mbappe France Golden Boot trophy"], "clips": []},
        {"says": "Is Monday now his night?", "visual": "Kylian Mbappe looking confident close up", "images": ["Kylian Mbappe confident close up Real Madrid", "Kylian Mbappe portrait 2026"], "clips": []},
    ],
)

set_plan(
    "batch_ronaldo_tenhag_claims.json",
    [
        {"says": "Erik ten Hag has reopened his feud with Cristiano Ronaldo.", "visual": "Cristiano Ronaldo and Erik ten Hag together", "images": ["Cristiano Ronaldo Erik ten Hag Manchester United touchline", "Ronaldo Ten Hag together Old Trafford"], "clips": []},
        {"says": "He says Ronaldo let Manchester United down and failed him as manager.", "visual": "Erik ten Hag serious Manchester United", "images": ["Erik ten Hag Manchester United serious close up", "Erik ten Hag press conference Manchester United"], "clips": []},
        {"says": "Ten Hag claims the problem was not asking Ronaldo to press.", "visual": "Ten Hag speaking to Cristiano Ronaldo", "images": ["Ten Hag talking to Cristiano Ronaldo Manchester United", "Ronaldo Ten Hag conversation touchline"], "clips": []},
        {"says": "He says Ronaldo was exhausted,", "visual": "Cristiano Ronaldo on Manchester United bench", "images": ["Cristiano Ronaldo Manchester United bench 2022", "Ronaldo tired Manchester United close up"], "clips": []},
        {"says": "was not preparing properly,", "visual": "Cristiano Ronaldo training in a Manchester United shirt", "images": ["Cristiano Ronaldo training Manchester United", "Cristiano Ronaldo Man United practice"], "clips": []},
        {"says": "and did not run with or without the ball.", "visual": "Cristiano Ronaldo playing in a red Manchester United shirt", "images": ["Cristiano Ronaldo playing Manchester United", "Cristiano Ronaldo red Manchester United shirt match"], "clips": []},
        {"says": "Ronaldo previously said he had no respect for Ten Hag.", "visual": "Cristiano Ronaldo serious interview", "images": ["Cristiano Ronaldo Piers Morgan interview Ten Hag", "Cristiano Ronaldo serious interview 2022"], "clips": []},
        {"says": "Who was really right?", "visual": "Cristiano Ronaldo and Erik ten Hag split close up", "images": ["Cristiano Ronaldo Erik ten Hag face to face", "Ronaldo Ten Hag Manchester United collage"], "clips": []},
    ],
)

with open("batch_messi_nycfc_playoffs.json", "r", encoding="utf-8") as handle:
    messi = json.load(handle)

subject = (
    "Lionel Messi acquired Spanish fifth-division club UE Cornella in April 2026, "
    "with plans centred on youth football and local development"
)
script = (
    "Cornella's city council says Messi now owns a football club in Spain, and it is not "
    "Barcelona. In April, the council announced he had acquired UE Cornella, a fifth division "
    "club based near Barcelona. The project is focused on "
    "youth football and developing local talent. Messi is still playing in Miami, but his "
    "next football chapter has already begun. Could he one day return to Barcelona as an owner?"
)
beats = [
    {"says": "Cornella's city council says Messi now owns a football club in Spain,", "visual": "Lionel Messi smiling close up", "images": ["Lionel Messi smiling close up 2026", "Lionel Messi portrait Inter Miami"], "clips": []},
    {"says": "and it is not Barcelona.", "visual": "Lionel Messi Barcelona stadium background", "images": ["Lionel Messi Barcelona Camp Nou", "Messi Barcelona emotional close up"], "clips": []},
    {"says": "In April, the council announced he had acquired UE Cornella,", "visual": "Lionel Messi UE Cornella ownership announcement", "images": ["Lionel Messi buys UE Cornella April 2026", "Messi UE Cornella owner announcement"], "clips": []},
    {"says": "a fifth division club based near Barcelona.", "visual": "UE Cornella football stadium and team", "images": ["UE Cornella football club stadium", "UE Cornella team Spain"], "clips": []},
    {"says": "The project is focused on youth football and developing local talent.", "visual": "UE Cornella youth academy players", "images": ["UE Cornella youth academy football", "UE Cornella academy players"], "clips": []},
    {"says": "Messi is still playing in Miami,", "visual": "Lionel Messi Inter Miami playing", "images": ["Lionel Messi Inter Miami match 2026", "Messi Inter Miami close up"], "clips": []},
    {"says": "but his next football chapter has already begun.", "visual": "Lionel Messi watching football from stands", "images": ["Lionel Messi watching football from stands", "Lionel Messi football owner suit"], "clips": []},
    {"says": "Could he one day return to Barcelona as an owner?", "visual": "Lionel Messi looking at Camp Nou", "images": ["Lionel Messi Camp Nou return", "Messi Barcelona stadium emotional"], "clips": []},
]
messi["defaults"].update(
    video_subject=subject,
    video_script=script,
    video_terms="Lionel Messi UE Cornella owner, Messi Spanish football club, UE Cornella academy",
    hook_text="MESSI'S NEXT MOVE HAS ALREADY BEGUN",
    cta_text="COULD HE OWN BARCELONA ONE DAY? 👇",
    hook_cover_term="a sharp close up of Lionel Messi looking confident",
    subject_positive_labels=["a real photograph of Lionel Messi the footballer", "a tight close up of Lionel Messi's face", "Lionel Messi in an Inter Miami shirt", "Lionel Messi in a Barcelona shirt"],
    visual_evidence_prompts=["a real photograph of Lionel Messi the footballer", "UE Cornella football club in Spain", "Lionel Messi watching a football match"],
    enable_youtube_footage=False,
    youtube_only_media=False,
    youtube_footage_queries=[],
    beat_plan=beats,
    curated_image_paths=[],
    intro_image_paths=[],
)
messi["videos"] = [{"video_subject": subject, "video_script": script, "video_terms": messi["defaults"]["video_terms"], "hook_text": messi["defaults"]["hook_text"], "cta_text": messi["defaults"]["cta_text"], "beat_plan": beats, "beat_shared_clips": []}]
with open("batch_messi_cornella_owner.json", "w", encoding="utf-8") as handle:
    json.dump(messi, handle, indent=2, ensure_ascii=False)
    handle.write("\n")

print("Prepared controlled beat plans for all three October 24 Shorts")
