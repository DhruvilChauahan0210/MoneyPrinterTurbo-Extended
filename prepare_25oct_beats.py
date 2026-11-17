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
    "batch_barca_psg_firstloss.json",
    [
        {"says": "Barcelona's perfect start is over,", "visual": "Barcelona players after losing to PSG", "images": ["Barcelona PSG 4-2 Champions League October 2026", "Barcelona players PSG defeat October 2026"], "clips": []},
        {"says": "and PSG left it late.", "visual": "PSG players celebrating against Barcelona", "images": ["PSG celebrate Barcelona 4-2 October 2026", "PSG players Parc des Princes Barcelona"], "clips": []},
        {"says": "Barça fought back twice to make it two-all,", "visual": "Barcelona attacking PSG in Paris", "images": ["Barcelona PSG attack 2-2 October 2026", "Barcelona PSG match action October 2026"], "clips": []},
        {"says": "with Xavi Espart and Lamine Yamal scoring.", "visual": "Lamine Yamal celebrates Barcelona goal against PSG", "images": ["Lamine Yamal goal PSG Barcelona October 2026", "Xavi Espart goal PSG Barcelona 2026"], "clips": []},
        {"says": "Then Vitinha struck in the eighty-first minute,", "visual": "Vitinha celebrates PSG goal against Barcelona", "images": ["Vitinha goal Barcelona PSG 2026", "Vitinha PSG celebration Champions League"], "clips": []},
        {"says": "and Fabián Ruiz sealed PSG's four-two win", "visual": "Fabián Ruiz celebrates for PSG", "images": ["Fabian Ruiz goal PSG Barcelona 2026", "Fabian Ruiz PSG celebration"], "clips": []},
        {"says": "six minutes later.", "visual": "PSG players celebrate final goal", "images": ["PSG Barcelona final goal 4-2 October 2026", "PSG team celebration Barcelona 2026"], "clips": []},
        {"says": "Was this just one bad night, or a warning before El Clásico?", "visual": "Lamine Yamal before Barcelona Real Madrid El Clasico", "images": ["Lamine Yamal Barcelona El Clasico 2026", "Barcelona Real Madrid El Clasico October 2026"], "clips": []},
    ],
)

set_plan(
    "batch_man_united_como_41.json",
    [
        {"says": "Manchester United have hit a new low in Europe.", "visual": "Manchester United players dejected after Como defeat", "images": ["Manchester United Como 4-1 October 2026", "Manchester United players dejected Como 2026"], "clips": []},
        {"says": "Como beat them four-one,", "visual": "Como players celebrate against Manchester United", "images": ["Como Manchester United 4-1 Champions League 2026", "Como celebrate Manchester United October 2026"], "clips": []},
        {"says": "with Nico Paz scoring twice", "visual": "Nico Paz celebrates Como goal", "images": ["Nico Paz Como Manchester United goal October 2026", "Nico Paz Como celebration 2026"], "clips": []},
        {"says": "and setting up another.", "visual": "Nico Paz assists Como against Manchester United", "images": ["Nico Paz assist Manchester United Como October 2026", "Nico Paz Como Champions League 2026"], "clips": []},
        {"says": "United are now winless in seven matches,", "visual": "Manchester United players walking off after Como loss", "images": ["Manchester United Como defeat players 2026", "Manchester United Champions League Como 2026"], "clips": []},
        {"says": "and Bruno Fernandes publicly questioned the team's decision not to press.", "visual": "Bruno Fernandes speaking after Manchester United match", "images": ["Bruno Fernandes Como post match October 2026", "Bruno Fernandes Manchester United interview 2026"], "clips": []},
        {"says": "Is Michael Carrick running out of time?", "visual": "Michael Carrick reacts to Como defeat", "images": ["Michael Carrick Como Manchester United reaction October 2026", "Carrick Manchester United Como 2026"], "clips": []},
    ],
)

set_plan(
    "batch_liverpool_villarreal_comeback.json",
    [
        {"says": "Liverpool were two goals down at Anfield,", "visual": "Liverpool falling behind Villarreal at Anfield", "images": ["Liverpool Villarreal 4-3 Champions League October 2026", "Villarreal lead Liverpool 2-0 Anfield 2026"], "clips": []},
        {"says": "but this Champions League match turned into a thriller.", "visual": "Anfield crowd during Liverpool Villarreal Champions League", "images": ["Liverpool Villarreal Champions League Anfield October 2026", "Anfield Champions League night Liverpool 2026"], "clips": []},
        {"says": "Alexis Mac Allister started the comeback before half-time.", "visual": "Alexis Mac Allister celebrates Liverpool goal against Villarreal", "images": ["Alexis Mac Allister goal Liverpool Villarreal 2026", "Mac Allister Liverpool Villarreal October 2026"], "clips": []},
        {"says": "Liverpool then scored three more,", "visual": "Liverpool players celebrate comeback against Villarreal", "images": ["Liverpool comeback Villarreal 4-3 Anfield 2026", "Liverpool players celebrate Villarreal Champions League 2026"], "clips": []},
        {"says": "with teenage winger Rio Ngumoha starring", "visual": "Rio Ngumoha playing for Liverpool", "images": ["Rio Ngumoha Liverpool Villarreal October 2026", "Rio Ngumoha Liverpool Champions League 2026"], "clips": []},
        {"says": "as they beat Villarreal four-three.", "visual": "Liverpool celebrate final whistle win over Villarreal", "images": ["Liverpool Villarreal 4-3 final whistle 2026", "Liverpool Villarreal match October 2026 photos"], "clips": []},
        {"says": "The Reds have now won all three of their opening league-phase matches.", "visual": "Liverpool celebrate Champions League victory at Anfield", "images": ["Liverpool three wins Champions League October 2026", "Liverpool Champions League 2026 celebration"], "clips": []},
        {"says": "Is this Liverpool side built for Europe?", "visual": "Liverpool team before Champions League match", "images": ["Liverpool Champions League team Anfield 2026", "Liverpool European campaign 2026"], "clips": []},
    ],
)

print("Prepared controlled beat plans for all three October 25 Shorts")
