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
    data["videos"] = [{
        "video_subject": subject,
        "video_script": script,
        "video_terms": terms,
        "hook_text": hook,
        "cta_text": cta,
    }]
    with open(output, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(f"{output}: {len(script.split())} words")


build(
    "batch_messi_nycfc_playoffs.json",
    "batch_barca_psg_firstloss.json",
    subject=(
        "Barcelona's perfect start to the 2026/27 season ended with a 4-2 Champions League "
        "loss at PSG after the teams were level at 2-2 in the 79th minute"
    ),
    script=(
        "Barcelona were unbeaten all season, but at two-two in Paris, the match changed in "
        "six minutes. Xavi Espart and Lamine Yamal had twice dragged Barça level with PSG. "
        "Vitinha scored in the eighty-first minute; Fabián Ruiz added another in the eighty-"
        "seventh. Was this one bad night, or a warning before El Clásico?"
    ),
    hook="A TWO-ALL SCORE WASN'T ENOUGH",
    cta="WARNING BEFORE EL CLÁSICO? 👇",
    terms=(
        "Barcelona PSG 4-2 Champions League October 2026, Lamine Yamal PSG goal, "
        "Vitinha late goal Barcelona, Fabian Ruiz PSG Barcelona"
    ),
    cover="Lamine Yamal reacting after Barcelona's Champions League defeat to PSG",
    positives=[
        "a real photograph of Lamine Yamal playing for Barcelona",
        "a real photograph of Barcelona players against Paris Saint-Germain",
        "a real photograph of Vitinha playing for PSG",
        "a real photograph of Fabián Ruiz celebrating for PSG",
        "a real photograph of Barcelona players reacting after a defeat",
    ],
    queries=[
        "PSG Barcelona 4-2 Champions League October 2026 highlights",
        "Lamine Yamal goal PSG Barcelona October 2026",
        "Vitinha goal Barcelona PSG 2026",
        "Fabian Ruiz goal Barcelona PSG 2026",
        "Xavi Espart goal PSG Barcelona 2026",
        "Barcelona PSG Champions League match photos October 2026",
        "Lamine Yamal Barcelona close up 2026",
        "Barcelona players disappointed PSG Champions League 2026",
    ],
)

build(
    "batch_bellingham_2031.json",
    "batch_man_united_como_41.json",
    subject=(
        "Como beat Manchester United 4-1 in the Champions League on 21 October 2026, "
        "extending United's winless run to seven matches and increasing pressure on Michael Carrick"
    ),
    script=(
        "Manchester United have hit a new low in Europe. Como beat them four-one, with "
        "Nico Paz scoring twice and setting up another. United are now winless in seven "
        "matches, and Bruno Fernandes publicly questioned the team's decision not to press. "
        "Is Michael Carrick running out of time?"
    ),
    hook="COMO JUST HUMILIATED MAN UNITED",
    cta="IS CARRICK RUNNING OUT OF TIME? 👇",
    terms=(
        "Como Manchester United 4-1 Champions League 2026, Nico Paz brace, Michael Carrick "
        "Bruno Fernandes tactics, Como Cesc Fabregas"
    ),
    cover="Nico Paz celebrating against Manchester United in Como",
    positives=[
        "a real photograph of Nico Paz playing for Como",
        "a real photograph of Manchester United players in their red kit",
        "a real photograph of Michael Carrick coaching Manchester United",
        "a real photograph of Bruno Fernandes playing for Manchester United",
        "a real photograph of Como players celebrating a goal",
    ],
    queries=[
        "Como Manchester United 4-1 Champions League October 2026 highlights",
        "Nico Paz Como Manchester United goals October 2026",
        "Manchester United Como 4-1 match October 21 2026",
        "Michael Carrick Como Manchester United reaction 2026",
        "Bruno Fernandes Como Manchester United post match 2026",
        "Cesc Fabregas Como Manchester United Champions League",
        "Como players celebrate Manchester United 2026",
        "Manchester United players dejected Como 2026",
    ],
)

build(
    "batch_vinicius_ban.json",
    "batch_liverpool_villarreal_comeback.json",
    subject=(
        "Liverpool came from two goals down to beat Villarreal 4-3 at Anfield in the Champions League"
    ),
    script=(
        "Liverpool were two goals down at Anfield, but this Champions League match turned into a thriller. "
        "Alexis Mac Allister started the comeback before half-time. Liverpool then scored three more, "
        "with teenage winger Rio Ngumoha starring as they beat Villarreal four-three. The Reds have now "
        "won all three of their opening league-phase matches. Is this Liverpool side built for Europe?"
    ),
    hook="LIVERPOOL CAME BACK FROM TWO DOWN",
    cta="BUILT FOR EUROPE? 👇",
    terms=(
        "Liverpool Villarreal 4-3 Champions League October 2026, Liverpool comeback at Anfield, "
        "Alexis Mac Allister goal, Rio Ngumoha Liverpool"
    ),
    cover="Liverpool players celebrating their comeback win over Villarreal at Anfield",
    positives=[
        "a real photograph of Liverpool players celebrating at Anfield",
        "a real photograph of Alexis Mac Allister playing for Liverpool",
        "a real photograph of Rio Ngumoha playing for Liverpool",
        "a real photograph of Villarreal players in their yellow kit",
        "a real photograph of Anfield during a Champions League match",
    ],
    queries=[
        "Liverpool Villarreal 4-3 Champions League October 2026 highlights",
        "Alexis Mac Allister goal Liverpool Villarreal 2026",
        "Rio Ngumoha Liverpool Villarreal October 2026",
        "Liverpool comeback Villarreal 4-3 Anfield 2026",
        "Liverpool players celebrate Villarreal Champions League 2026",
        "Villarreal Liverpool match October 2026 photos",
        "Anfield Champions League night Liverpool 2026",
        "Liverpool Villarreal match report 20 October 2026",
    ],
)
