import copy
import json


def build(donor, output, *, subject, script, hook, cta, terms, cover, positives, queries):
    with open(donor, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    defaults = copy.deepcopy(data["defaults"])
    defaults.update(
        video_subject=subject,
        video_script=script,
        video_terms=terms,
        hook_text=hook,
        cta_text=cta,
        hook_cover_term=cover,
        subject_positive_labels=positives,
        visual_evidence_prompts=positives,
        curated_image_paths=[],
        intro_image_paths=[],
        beat_plan=[],
        beat_shared_clips=[],
        series_badge_text="",
        series_ledger_path="",
        enable_youtube_footage=True,
        youtube_only_media=True,
        youtube_footage_queries=queries,
        youtube_max_videos=30,
        youtube_clips_per_video=8,
        youtube_max_clips=300,
        footage_min_fraction=1.0,
    )
    data["defaults"] = defaults
    data["videos"] = [
        {
            "video_subject": subject,
            "video_script": script,
            "video_terms": terms,
            "hook_text": hook,
            "cta_text": cta,
        }
    ]

    with open(output, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(f"{output}: {len(script.split())} words")


build(
    "batch_mbappe_100th.json",
    "batch_mbappe_onzedor26.json",
    subject=(
        "Kylian Mbappe won the 2026 Onze d'Or with 48.2 percent of the reader vote, "
        "ahead of Joao Neves and Khvicha Kvaratskhelia, six days before the Ballon d'Or"
    ),
    script=(
        "Six days before the Ballon d'Or, Kylian Mbappe has crushed another major vote. "
        "He won the twenty twenty-six Onze d'Or with forty-eight point two percent, while "
        "Joao Neves finished on eleven point nine and Kvaratskhelia on ten point eight. "
        "Mbappe topped both La Liga and the Champions League for goals, then won the World "
        "Cup Golden Boot. Is Monday now his night?"
    ),
    hook="IS THE BALLON D'OR ALREADY DECIDED?",
    cta="DOES MBAPPE DESERVE IT? 👇",
    terms=(
        "Kylian Mbappe Onze d'Or 2026 award, Mbappe Real Madrid 2026 celebration, "
        "Mbappe World Cup Golden Boot, Mbappe Champions League goals"
    ),
    cover="a sharp tight close up of Kylian Mbappe in a white Real Madrid shirt holding an award",
    positives=[
        "a real photograph of Kylian Mbappe the footballer",
        "a tight close up of Kylian Mbappe's face",
        "Kylian Mbappe in a white Real Madrid shirt",
        "Kylian Mbappe celebrating a goal or holding a football award",
    ],
    queries=[
        "Kylian Mbappe Real Madrid 2026 highlights",
        "Kylian Mbappe Real Madrid goals 2025 2026",
        "Kylian Mbappe Champions League 2026 goals",
        "Kylian Mbappe World Cup 2026 Golden Boot",
        "Kylian Mbappe France World Cup 2026 highlights",
        "Kylian Mbappe award ceremony 2026",
        "Kylian Mbappe Real Madrid close up 2026",
        "Kylian Mbappe Real Madrid celebration 2026",
        "Mbappe La Liga top scorer 2026",
        "Mbappe Champions League top scorer 2026",
        "Mbappe Real Madrid best goals 2026",
        "Kylian Mbappe World Cup goals compilation 2026",
    ],
)

build(
    "batch_ronaldo_neville_rooney.json",
    "batch_ronaldo_tenhag_claims.json",
    subject=(
        "Erik ten Hag said Cristiano Ronaldo let Manchester United and the manager down, "
        "was not fit enough, and did not prepare to meet the team's physical demands"
    ),
    script=(
        "Erik ten Hag has reopened his feud with Cristiano Ronaldo. He says Ronaldo let "
        "Manchester United down and failed him as manager. Ten Hag claims the problem was "
        "not asking Ronaldo to press. He says Ronaldo was exhausted, was not preparing "
        "properly, and did not run with or without the ball. Ronaldo previously said he "
        "had no respect for Ten Hag. Who was really right?"
    ),
    hook="TEN HAG JUST BROKE HIS SILENCE",
    cta="WHO WAS REALLY RIGHT? 👇",
    terms=(
        "Cristiano Ronaldo Erik ten Hag Manchester United argument, Ronaldo Manchester "
        "United 2022 bench, Ten Hag Ronaldo touchline, Ronaldo Old Trafford"
    ),
    cover="Cristiano Ronaldo and Erik ten Hag arguing on the Manchester United touchline",
    positives=[
        "a real photograph of Cristiano Ronaldo at Manchester United",
        "a tight close up of Cristiano Ronaldo's face in a red Manchester United shirt",
        "Erik ten Hag coaching Manchester United from the touchline",
        "Cristiano Ronaldo and Erik ten Hag together at Old Trafford",
    ],
    queries=[
        "Cristiano Ronaldo Erik ten Hag Manchester United touchline",
        "Ronaldo Ten Hag Manchester United 2022",
        "Cristiano Ronaldo Manchester United bench 2022",
        "Ronaldo refuses substitute Tottenham Ten Hag",
        "Cristiano Ronaldo Old Trafford 2022 highlights",
        "Erik ten Hag Ronaldo press conference",
        "Cristiano Ronaldo Manchester United training 2022",
        "Ronaldo Manchester United 2022 close up",
        "Ten Hag coaching Manchester United touchline",
        "Ronaldo Ten Hag argument Manchester United",
        "Cristiano Ronaldo leaves Old Trafford early 2022",
        "Ronaldo Manchester United final season highlights",
    ],
)

build(
    "batch_messi_ballondor26.json",
    "batch_ballondor_london26.json",
    subject=(
        "The 70th Ballon d'Or ceremony will be held at the London Palladium on 26 October "
        "2026, the first time the ceremony has been staged in London"
    ),
    script=(
        "On Monday, the Ballon d'Or will make history. Its seventieth ceremony will be held "
        "in London for the first time, at the London Palladium. The move honours Stanley "
        "Matthews, the award's first winner. Mbappe, Bellingham, Haaland, Kane and Messi are "
        "all nominated to succeed Ousmane Dembele. Football's biggest individual prize has "
        "a new stage. Who should lift it?"
    ),
    hook="FOOTBALL'S BIGGEST AWARD IS MOVING",
    cta="WHO SHOULD WIN IT? 👇",
    terms=(
        "Ballon d'Or 2026 London ceremony, Mbappe Bellingham Haaland Kane Messi nominees, "
        "London Palladium Ballon d'Or, Ousmane Dembele Ballon d'Or"
    ),
    cover="the Ballon d'Or trophy on stage under dramatic golden lights",
    positives=[
        "a real photograph of the Ballon d'Or trophy",
        "a real photograph of Kylian Mbappe the footballer",
        "a real photograph of Jude Bellingham the footballer",
        "a real photograph of Erling Haaland the footballer",
        "a real photograph of Lionel Messi the footballer",
    ],
    queries=[
        "Ballon d'Or 2026 nominees Mbappe Bellingham Haaland Messi",
        "Ballon d'Or trophy ceremony cinematic",
        "Ballon d'Or London 2026 ceremony",
        "Kylian Mbappe 2026 highlights close up",
        "Jude Bellingham 2026 highlights close up",
        "Erling Haaland 2026 highlights close up",
        "Lionel Messi 2026 highlights close up",
        "Ousmane Dembele Ballon d'Or trophy 2025",
        "Ballon d'Or award stage highlights",
        "Stanley Matthews Ballon d'Or historical footage",
    ],
)
