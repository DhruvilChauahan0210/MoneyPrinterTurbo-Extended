"""Slot 2 (17:00) normal Shorts for 2/4/6/8/10 NOV 2026. Odd days are What-Ifs (run_whatif_nov.sh)."""
from shortbuild import build

# 2 NOV — Mbappé: Clásico double, then loses the Ballon d'Or by 28 points the next night.
build(
    "batch_mbappe_madrid_goaltally.json",
    "batch_mbappe_clasico_ballondor_28pts.json",
    subject=(
        "Kylian Mbappe scored twice in Real Madrid's 2-1 Clasico win at Camp Nou on 25 October 2026, "
        "then lost the Ballon d'Or to Harry Kane by 28 points the next night"
    ),
    beats=[
        {"says": "In twenty-four hours, Kylian Mbappé went from hero to heartbreak.",
         "visual": "Kylian Mbappe celebrating a goal for Real Madrid",
         "images": ["Mbappe celebration Camp Nou October 2026", "Kylian Mbappe Real Madrid celebration"]},
        {"says": "At Camp Nou, he scored twice against Barcelona,",
         "visual": "Kylian Mbappe scoring against Barcelona",
         "images": ["Mbappe goal Barcelona Clasico 2026", "Mbappe Clasico Camp Nou"]},
        {"says": "including an eighty-seventh minute winner that ended their perfect start.",
         "visual": "Real Madrid players celebrating a late winner",
         "images": ["Real Madrid celebrate Clasico win Camp Nou", "Mbappe winner Barcelona Real Madrid celebration"]},
        {"says": "Those goals took him to one hundred for Real Madrid.",
         "visual": "close up of Kylian Mbappe in Real Madrid white kit",
         "images": ["Kylian Mbappe Real Madrid close up", "Mbappe Real Madrid portrait"]},
        {"says": "The next night in London, he lost the Ballon d'Or to Harry Kane",
         "visual": "Harry Kane holding the Ballon d'Or trophy",
         "images": ["Harry Kane Ballon d'Or 2026", "Harry Kane Ballon d'Or trophy London"]},
        {"says": "by just twenty-eight points.",
         "visual": "Kylian Mbappe in a suit at the Ballon d'Or ceremony",
         "images": ["Mbappe Ballon d'Or ceremony suit", "Kylian Mbappe Ballon d'Or gala"]},
        {"says": "It was the closest vote since twenty nineteen,",
         "visual": "the Ballon d'Or trophy on stage",
         "images": ["Ballon d'Or trophy", "Ballon d'Or trophy close up"]},
        {"says": "and three jurors left him out of their top ten completely.",
         "visual": "Kylian Mbappe looking disappointed",
         "images": ["Mbappe disappointed Real Madrid", "Kylian Mbappe sad"]},
        {"says": "Was Mbappé robbed?",
         "visual": "Kylian Mbappe looking straight at the camera",
         "images": ["Kylian Mbappe serious face", "Mbappe intense Real Madrid"]},
    ],
    hook="ROBBED BY 28 POINTS?",
    cta="WAS MBAPPÉ ROBBED? 👇",
    terms="Mbappe Clasico double Camp Nou October 2026, Mbappe Ballon d'Or 2026 28 points, Kane Ballon d'Or",
    cover="Kylian Mbappe celebrating a goal for Real Madrid",
    positives=[
        "a real photograph of Kylian Mbappe",
        "a real photograph of Kylian Mbappe playing for Real Madrid",
        "a real photograph of Harry Kane",
    ],
)

# 4 NOV — Yamal: Thierry Henry's on-stage jab at the Ballon d'Or.
build(
    "batch_yamal_mbappe_teen_record.json",
    "batch_yamal_henry_kopa_jab.json",
    subject=(
        "Thierry Henry teased Lamine Yamal on stage after he won a record third Kopa Trophy at the "
        "2026 Ballon d'Or, asking if it was the one he really wanted"
    ),
    beats=[
        {"says": "Thierry Henry teased Lamine Yamal live on stage.",
         "visual": "Thierry Henry smiling on stage at an award ceremony",
         "images": ["Thierry Henry Ballon d'Or 2026 host", "Thierry Henry stage presenter"]},
        {"says": "Yamal had just won the Kopa Trophy for a record third year in a row.",
         "visual": "Lamine Yamal holding the Kopa Trophy",
         "images": ["Lamine Yamal Kopa Trophy", "Lamine Yamal Kopa Trophy 2026"]},
        {"says": "Then Henry asked: is it the one you really wanted tonight?",
         "visual": "Thierry Henry laughing",
         "images": ["Thierry Henry laughing", "Thierry Henry Ballon d'Or"]},
        {"says": "Yamal laughed and said he wanted all of them.",
         "visual": "Lamine Yamal smiling in a suit",
         "images": ["Lamine Yamal suit Ballon d'Or", "Lamine Yamal smiling ceremony"]},
        {"says": "He finished third, behind Harry Kane and Kylian Mbappé.",
         "visual": "Lamine Yamal looking disappointed",
         "images": ["Lamine Yamal disappointed", "Lamine Yamal serious Barcelona"]},
        {"says": "The next day, he posted: it will come, good things take time.",
         "visual": "Lamine Yamal celebrating a goal for Barcelona",
         "images": ["Lamine Yamal goal celebration Barcelona", "Lamine Yamal celebration"]},
        {"says": "Hansi Flick said this is how champions respond.",
         "visual": "Hansi Flick Barcelona coach on the touchline",
         "images": ["Hansi Flick Barcelona", "Hansi Flick touchline Barcelona"]},
        {"says": "Was Henry's joke too far?",
         "visual": "close up of Lamine Yamal",
         "images": ["Lamine Yamal close up", "Lamine Yamal portrait"]},
    ],
    hook="A JOKE THAT WENT TOO FAR?",
    cta="WAS HENRY TOO HARSH? 👇",
    terms="Thierry Henry Lamine Yamal Kopa Trophy joke, Yamal Ballon d'Or 2026 third, Yamal it will come",
    cover="Lamine Yamal holding the Kopa Trophy",
    positives=[
        "a real photograph of Lamine Yamal",
        "a real photograph of Thierry Henry",
        "a real photograph of Hansi Flick",
    ],
)

# 6 NOV — Neymar: red card and ban for covering his mouth (Vinícius Júnior protocol).
build(
    "batch_neymar_santos_retirement_hint.json",
    "batch_neymar_mouth_red_card.json",
    subject=(
        "Neymar was sent off for covering his mouth while arguing with Bahia's Rodrigo Nestor and "
        "banned under a Brazilian protocol named after Vinicius Junior"
    ),
    beats=[
        {"says": "Neymar was sent off for covering his mouth.",
         "visual": "Neymar in Santos kit being shown a red card",
         "images": ["Neymar red card Santos", "Neymar Santos red card Bahia"]},
        {"says": "Santos beat Bahia one-nil, but Neymar had been arguing with Rodrigo Nestor,",
         "visual": "Neymar arguing with an opponent",
         "images": ["Neymar Rodrigo Nestor", "Neymar Santos Bahia argument"]},
        {"says": "and he hid his words behind his hand.",
         "visual": "Neymar covering his mouth with his hand",
         "images": ["Neymar covering mouth", "Neymar hand over mouth Santos"]},
        {"says": "In Brazil, that breaks a protocol named after Vinícius Júnior,",
         "visual": "Vinicius Junior in a Brazil shirt",
         "images": ["Vinicius Junior Brazil", "Vinicius Junior close up"]},
        {"says": "who accused an opponent of hiding racial abuse that way.",
         "visual": "Vinicius Junior pointing angrily",
         "images": ["Vinicius Junior racism protest", "Vinicius Junior angry Real Madrid"]},
        {"says": "Neymar admitted covering his mouth was wrong, but denied insulting Nestor,",
         "visual": "Neymar looking frustrated in Santos kit",
         "images": ["Neymar frustrated Santos 2026", "Neymar Santos serious"]},
        {"says": "and accused him of one of the dirtiest tricks in football.",
         "visual": "Neymar speaking angrily",
         "images": ["Neymar angry Santos", "Neymar shouting"]},
        {"says": "Now he is banned for three matches.",
         "visual": "Neymar walking off the pitch",
         "images": ["Neymar walking off Santos", "Neymar sent off walking"]},
        {"says": "Was the referee right?",
         "visual": "close up of Neymar",
         "images": ["Neymar close up Santos", "Neymar portrait 2026"]},
    ],
    hook="THE RULE NAMED AFTER VINI",
    cta="WAS THE REFEREE RIGHT? 👇",
    terms="Neymar red card covering mouth Santos Bahia, Neymar Vinicius Junior rule ban, Rodrigo Nestor Neymar",
    cover="Neymar in Santos kit being sent off",
    positives=[
        "a real photograph of Neymar",
        "a real photograph of Neymar playing for Santos",
        "a real photograph of Vinicius Junior",
    ],
)

# 8 NOV — Bellingham: made the Clásico winner, ranked 11th, Mourinho "No further comments".
build(
    "batch_bellingham_2031.json",
    "batch_bellingham_eleventh_mourinho.json",
    subject=(
        "Jude Bellingham created Real Madrid's Clasico winner at Camp Nou, then finished 11th in the "
        "2026 Ballon d'Or, and Mourinho said he was surprised with no further comments"
    ),
    beats=[
        {"says": "Jude Bellingham made the Clásico winner happen.",
         "visual": "Jude Bellingham celebrating for Real Madrid",
         "images": ["Jude Bellingham celebration Real Madrid", "Bellingham Clasico celebration"]},
        {"says": "With the score level at Camp Nou, his skill released Eduardo Camavinga,",
         "visual": "Jude Bellingham dribbling against Barcelona",
         "images": ["Bellingham dribble Barcelona", "Bellingham Camp Nou 2026"]},
        {"says": "and Kylian Mbappé finished in the eighty-seventh minute.",
         "visual": "Kylian Mbappe celebrating a winner against Barcelona",
         "images": ["Mbappe winner Clasico celebration", "Mbappe Bellingham celebration"]},
        {"says": "José Mourinho celebrated with a knee slide.",
         "visual": "Jose Mourinho knee slide celebration",
         "images": ["Mourinho knee slide Camp Nou", "Jose Mourinho Real Madrid celebration"]},
        {"says": "One night later, the Ballon d'Or ranked Bellingham just eleventh.",
         "visual": "Jude Bellingham in a suit at the Ballon d'Or",
         "images": ["Jude Bellingham Ballon d'Or suit", "Bellingham Ballon d'Or ceremony"]},
        {"says": "Mourinho was asked about it.",
         "visual": "Jose Mourinho at a press conference",
         "images": ["Jose Mourinho press conference Real Madrid", "Mourinho press conference"]},
        {"says": "He said he was surprised by the position of Jude Bellingham, who was eleventh.",
         "visual": "Jose Mourinho looking serious",
         "images": ["Jose Mourinho serious", "Mourinho Real Madrid 2026"]},
        {"says": "Then he added: no further comments.",
         "visual": "Jose Mourinho shrugging",
         "images": ["Mourinho shrug", "Jose Mourinho smirk"]},
        {"says": "Was Bellingham underrated?",
         "visual": "close up of Jude Bellingham",
         "images": ["Jude Bellingham close up", "Jude Bellingham Real Madrid portrait"]},
    ],
    hook="MOURINHO HAD NOTHING MORE TO SAY",
    cta="TOO LOW AT 11TH? 👇",
    terms="Bellingham Clasico assist Camp Nou 2026, Bellingham Ballon d'Or 11th, Mourinho no further comments",
    cover="Jude Bellingham celebrating for Real Madrid",
    positives=[
        "a real photograph of Jude Bellingham",
        "a real photograph of Jose Mourinho",
        "a real photograph of Kylian Mbappe",
    ],
)

# 10 NOV — Haaland: Anfield chants "cheats", Haaland scores in front of his father.
build(
    "batch_haaland_150goals.json",
    "batch_haaland_anfield_cheats.json",
    subject=(
        "Liverpool fans booed Manchester City and chanted cheats at Anfield on 11 October 2026, and "
        "Erling Haaland opened the scoring in City's 3-0 win in front of his father"
    ),
    beats=[
        {"says": "Anfield had one word for Manchester City: cheats.",
         "visual": "Liverpool fans at Anfield",
         "images": ["Anfield crowd Liverpool fans", "Liverpool fans Anfield Kop"]},
        {"says": "Days after the verdict in City's financial rules case, Liverpool fans booed them.",
         "visual": "Manchester City players at Anfield",
         "images": ["Manchester City players Anfield", "Man City Liverpool Anfield 2026"]},
        {"says": "Then Ryan Gravenberch was sent off,",
         "visual": "Ryan Gravenberch red card",
         "images": ["Ryan Gravenberch Liverpool", "Gravenberch red card"]},
        {"says": "and three minutes later, Erling Haaland broke the deadlock in front of his father.",
         "visual": "Erling Haaland celebrating a goal at Anfield",
         "images": ["Haaland goal Anfield celebration", "Erling Haaland celebration Liverpool"]},
        {"says": "Jérémy Doku and Rayan Cherki added more.",
         "visual": "Manchester City players celebrating a goal",
         "images": ["Doku Cherki Manchester City celebration", "Man City players celebrate goal 2026"]},
        {"says": "City won three-nil,",
         "visual": "Erling Haaland celebrating with teammates",
         "images": ["Haaland celebrate teammates Man City", "Erling Haaland Man City celebration"]},
        {"says": "their first back-to-back league wins at Anfield since nineteen fifty-three.",
         "visual": "Erling Haaland looking intense",
         "images": ["Erling Haaland intense", "Erling Haaland close up Man City"]},
        {"says": "Did Haaland silence Anfield?",
         "visual": "Erling Haaland shushing the crowd",
         "images": ["Haaland silence celebration", "Erling Haaland roar celebration"]},
    ],
    hook="HE SILENCED THE BOOS",
    cta="DID HE SILENCE ANFIELD? 👇",
    terms="Haaland Anfield goal October 2026, Liverpool 0-3 Man City cheats chants, Haaland father Anfield",
    cover="Erling Haaland celebrating a goal at Anfield",
    positives=[
        "a real photograph of Erling Haaland",
        "a real photograph of Manchester City players",
        "a real photograph of Liverpool fans at Anfield",
    ],
)
