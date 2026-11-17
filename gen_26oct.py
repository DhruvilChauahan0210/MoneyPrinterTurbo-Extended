import copy
import json


def build(donor, output, *, subject, beats, hook, cta, terms, cover, positives):
    with open(donor, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    script = " ".join(b["says"] for b in beats)
    plan = [{"says": b["says"], "visual": b["visual"], "images": b["images"], "clips": []} for b in beats]

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
        beat_plan=plan,
        beat_shared_clips=[],
        series_badge_text="",
        series_ledger_path="",
        enable_youtube_footage=False,
        youtube_only_media=False,
        youtube_footage_queries=[],
        voice_rate=0.88,
        bgm_type="random",
        bgm_volume=0.10,
        cover_min_keep=0.62,
    )
    data["defaults"] = defaults
    data["videos"] = [{
        "video_subject": subject,
        "video_script": script,
        "video_terms": terms,
        "hook_text": hook,
        "cta_text": cta,
        "beat_plan": plan,
        "beat_shared_clips": [],
    }]
    with open(output, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(f"{output}: {len(script.split())} words, {len(beats)} beats")


build(
    "batch_messi_cornella_owner.json",
    "batch_messi_asturias_award.json",
    subject=(
        "Lionel Messi became the first footballer to win Spain's Princess of Asturias Award for "
        "Sports on his own, receiving it in Oviedo months after Spain beat Argentina in the 2026 World Cup final"
    ),
    beats=[
        {"says": "Spain beat Messi in the World Cup final.",
         "visual": "Lionel Messi looking dejected in an Argentina shirt",
         "images": ["Messi Argentina Spain World Cup final 2026", "Messi sad Argentina World Cup final"]},
        {"says": "Now Spain has handed him something",
         "visual": "Lionel Messi in a suit at an award ceremony in Spain",
         "images": ["Messi Oviedo Princess of Asturias 2026", "Messi Princesa de Asturias"]},
        {"says": "no footballer had ever won alone.",
         "visual": "Lionel Messi smiling at an award event",
         "images": ["Messi Premio Princesa de Asturias Deportes 2026", "Messi award Oviedo October 2026"]},
        {"says": "In Oviedo, he received the Princess of Asturias Award for Sports,",
         "visual": "Lionel Messi receiving an award on stage at the Campoamor Theatre",
         "images": ["Messi Teatro Campoamor Oviedo", "Messi recibe Premio Princesa de Asturias"]},
        {"says": "often called Spain's Nobel Prize.",
         "visual": "the Princess of Asturias Awards ceremony stage",
         "images": ["Premios Princesa de Asturias ceremonia Teatro Campoamor", "Princess of Asturias Awards ceremony Oviedo"]},
        {"says": "Football had only won it as a team, or shared, like Casillas and Xavi.",
         "visual": "Iker Casillas and Xavi Hernandez together with an award",
         "images": ["Casillas Xavi Premio Principe de Asturias 2012", "Casillas Xavi Prince of Asturias award"]},
        {"says": "Messi said you have to appreciate the journey, because only one team can win.",
         "visual": "Lionel Messi speaking at a press event",
         "images": ["Lionel Messi Oviedo", "Messi Oviedo ninos evento", "Messi Inter Miami press conference"]},
        {"says": "Does this mean more than a Ballon d'Or?",
         "visual": "Lionel Messi holding the Ballon d'Or trophy",
         "images": ["Messi Ballon d'Or trophy", "Messi eighth Ballon d'Or 2023"]},
    ],
    hook="THE COUNTRY THAT BROKE HIS HEART",
    cta="BIGGER THAN A BALLON D'OR? 👇",
    terms=(
        "Messi Princess of Asturias Award 2026, Messi Oviedo, Spain World Cup final Messi, "
        "Casillas Xavi Asturias award"
    ),
    cover="Lionel Messi smiling at the Princess of Asturias Awards in Oviedo",
    positives=[
        "a real photograph of Lionel Messi",
        "a real photograph of Lionel Messi at an award ceremony",
        "a real photograph of Lionel Messi playing for Argentina",
    ],
)

build(
    "batch_barca_psg_firstloss.json",
    "batch_yamal_mbappe_teen_record.json",
    subject=(
        "Lamine Yamal's goal at PSG was his 13th in the Champions League, equalling Kylian Mbappe's "
        "record for the most Champions League goals by a teenager"
    ),
    beats=[
        {"says": "Kylian Mbappé held this Champions League record for years.",
         "visual": "Kylian Mbappe celebrating a Champions League goal as a teenager",
         "images": ["Mbappe Champions League goal 2017 Monaco", "young Mbappe PSG Champions League celebration"]},
        {"says": "Lamine Yamal just caught him.",
         "visual": "Lamine Yamal celebrating a goal for Barcelona",
         "images": ["Lamine Yamal celebration Barcelona 2026", "Lamine Yamal goal celebration"]},
        {"says": "His goal at PSG was his thirteenth in the competition,",
         "visual": "Lamine Yamal scoring against PSG",
         "images": ["Lamine Yamal goal PSG October 2026", "Lamine Yamal PSG Parc des Princes 2026"]},
        {"says": "the most ever by a teenager, level with Mbappé.",
         "visual": "Lamine Yamal and Kylian Mbappe on the same pitch",
         "images": ["Lamine Yamal Kylian Mbappe", "Yamal Mbappe El Clasico"]},
        {"says": "Mbappé needed twenty-three games.",
         "visual": "teenage Kylian Mbappe playing for Monaco",
         "images": ["Mbappe Monaco 2017 Champions League", "Mbappe teenager PSG 2018"]},
        {"says": "Yamal needed thirty-six,",
         "visual": "Lamine Yamal dribbling for Barcelona",
         "images": ["Lamine Yamal Barcelona", "Lamine Yamal dribble", "Lamine Yamal Champions League"]},
        {"says": "but he still has months left as a teenager.",
         "visual": "close up of Lamine Yamal",
         "images": ["Lamine Yamal close up 2026", "Lamine Yamal portrait Barcelona"]},
        {"says": "One more goal and the record is his alone.",
         "visual": "Lamine Yamal pointing to the crowd",
         "images": ["Lamine Yamal celebrates Champions League", "Lamine Yamal Barcelona fans celebration"]},
        {"says": "So who was better at nineteen, Yamal or Mbappé?",
         "visual": "Lamine Yamal and Kylian Mbappe face to face",
         "images": ["Yamal vs Mbappe", "Lamine Yamal Mbappe Real Madrid Barcelona"]},
    ],
    hook="SOMEONE JUST CAUGHT MBAPPÉ",
    cta="YAMAL OR MBAPPÉ AT 19? 👇",
    terms=(
        "Lamine Yamal 13 Champions League goals teenager record, Yamal equals Mbappe record, "
        "Yamal goal PSG October 2026"
    ),
    cover="Lamine Yamal celebrating a Champions League goal for Barcelona",
    positives=[
        "a real photograph of Lamine Yamal playing for Barcelona",
        "a real photograph of Kylian Mbappe playing football",
        "a real photograph of Lamine Yamal celebrating a goal",
    ],
)

build(
    "batch_ronaldo_tenhag_claims.json",
    "batch_ronaldo_alnassr_stake.json",
    subject=(
        "Reports say AC Milan owner RedBird is in early talks to buy 70 percent of Al Nassr for about "
        "$267 million, with Cristiano Ronaldo taking a 20 percent stake; nothing is agreed"
    ),
    beats=[
        {"says": "Cristiano Ronaldo might not just play for Al Nassr.",
         "visual": "Cristiano Ronaldo playing for Al Nassr in yellow",
         "images": ["Cristiano Ronaldo Al Nassr 2026", "Ronaldo Al Nassr yellow kit close up"]},
        {"says": "He could soon own part of it.",
         "visual": "Cristiano Ronaldo in a suit looking confident",
         "images": ["Cristiano Ronaldo suit businessman", "Cristiano Ronaldo suit event 2026"]},
        {"says": "Reports say AC Milan owners RedBird are in talks",
         "visual": "RedBird Capital Gerry Cardinale AC Milan owner",
         "images": ["Gerry Cardinale RedBird AC Milan", "Gerry Cardinale San Siro"]},
        {"says": "to buy seventy percent of the club",
         "visual": "Al Nassr stadium in Riyadh",
         "images": ["Al Nassr Al-Awwal Park stadium", "Al Nassr stadium Riyadh fans"]},
        {"says": "for around two hundred and sixty-seven million dollars,",
         "visual": "Al Nassr club badge and fans",
         "images": ["Al Nassr fans Ronaldo banner", "Al Nassr club logo"]},
        {"says": "with Ronaldo taking twenty percent.",
         "visual": "Cristiano Ronaldo smiling for Al Nassr",
         "images": ["Ronaldo smiling Al Nassr", "Cristiano Ronaldo Al Nassr celebration 2026"]},
        {"says": "RedBird and Saudi Arabia's Public Investment Fund declined to comment,",
         "visual": "Saudi Public Investment Fund headquarters in Riyadh",
         "images": ["Public Investment Fund PIF tower Riyadh", "PIF Saudi Arabia headquarters"]},
        {"says": "and one source says a deal might not happen.",
         "visual": "Cristiano Ronaldo looking serious",
         "images": ["Cristiano Ronaldo serious face Al Nassr", "Ronaldo thinking Al Nassr bench"]},
        {"says": "Should Ronaldo become an owner while he is still playing?",
         "visual": "Cristiano Ronaldo celebrating a goal for Al Nassr",
         "images": ["Ronaldo siu celebration Al Nassr", "Cristiano Ronaldo goal celebration Al Nassr 2026"]},
    ],
    hook="RONALDO'S BIGGEST MOVE YET",
    cta="SHOULD RONALDO BUY IN? 👇",
    terms=(
        "Cristiano Ronaldo Al Nassr stake RedBird takeover, Ronaldo 20 percent Al Nassr, "
        "RedBird PIF Al Nassr talks October 2026"
    ),
    cover="Cristiano Ronaldo close up in Al Nassr kit",
    positives=[
        "a real photograph of Cristiano Ronaldo",
        "a real photograph of Cristiano Ronaldo playing for Al Nassr",
        "a real photograph of Cristiano Ronaldo in a suit",
    ],
)
