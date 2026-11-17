import sys, json
sys.path.insert(0, ".claude/skills/football-shorts/scripts")
from shortbuild import build  # noqa: E402


def B(says, visual, *images):
    return {"says": says, "visual": visual, "images": list(images)}


OUT = "batch_proto_r3_mbappe_final2022.json"
build("batch_ronaldo_wolfsburg_hattrick.json", OUT,
      subject="Kylian Mbappe scored a hat-trick in the 18 December 2022 World Cup final at Lusail, a 3-3 draw that Argentina won 4-2 on penalties, the first final hat-trick since 1966, and President Macron came onto the pitch to console him.",
      beats=[
          B("Mbappe cried after scoring three goals.", "big close up of Kylian Mbappe in tears, France kit, 2022 World Cup final", "Kylian Mbappe crying World Cup final", "Mbappe tears Argentina France"),
          B("France trailed two-nil after thirty-six minutes.", "France players dejected", "France Argentina World Cup final 2022", "Kylian Mbappe France 2022"),
          B("Then Mbappe scored twice within two minutes.", "Kylian Mbappe celebrating a goal", "Mbappe penalty Argentina final", "Mbappe volley World Cup final"),
          B("Two-two after ninety minutes.", "Kylian Mbappe France celebrating", "Mbappe celebrates France Argentina", "Kylian Mbappe goal 2022"),
          B("Extra time: Mbappe's third made it three-three.", "Kylian Mbappe scoring a penalty", "Mbappe third goal World Cup final", "Mbappe hat-trick Argentina"),
          B("The first final hat-trick since nineteen sixty-six.", "Kylian Mbappe holding the match ball", "Mbappe hat-trick ball", "Kylian Mbappe World Cup 2022"),
          B("Argentina still won four-two on penalties.", "Argentina players celebrating World Cup", "Argentina win World Cup 2022", "Lionel Messi World Cup trophy"),
          B("He won the Golden Boot, eight goals.", "Kylian Mbappe with the Golden Boot", "Mbappe Golden Boot 2022", "Kylian Mbappe Golden Boot trophy"),
          B("Mbappe was distraught as Argentina celebrated.", "Kylian Mbappe dejected on the pitch", "Mbappe dejected World Cup final", "Kylian Mbappe sad"),
          B("President Macron came onto the pitch.", "Emmanuel Macron on the pitch at the World Cup final", "Macron World Cup final pitch", "Emmanuel Macron Lusail"),
          B("He tried to comfort Mbappe.", "Emmanuel Macron consoling Kylian Mbappe", "Macron consoles Mbappe", "Macron Mbappe World Cup final"),
          B("Greatest final performance ever, despite losing?", "close up of Kylian Mbappe France", "Kylian Mbappe France close up", "Kylian Mbappe portrait France"),
      ],
      hook="HAT-TRICK, THEN 4-2 HEARTBREAK",
      cta="BEST LOSING PERFORMANCE EVER? \U0001F447",
      terms="Mbappe hat-trick World Cup final 2022, Argentina France penalties, Macron consoles Mbappe, Lusail",
      cover="big close up of Kylian Mbappe crying, France 2022",
      positives=["a real photograph of Kylian Mbappe",
                 "a real photograph of Emmanuel Macron",
                 "a real photograph of Lionel Messi"])

d = json.load(open(OUT))
df = d["defaults"]
df.update(
    enable_hook_card=True,
    hook_duration=1.2,
    hook_overlay_opacity=0.35,
    enable_subscribe_button=False,
    enable_cta=False,
    cover_min_keep=0.36,
    min_shot_seconds=2.4,
    image_motion_style="varied",
    hook_cover_term="big close up of Kylian Mbappe crying, France 2022",
)
json.dump(d, open(OUT, "w"), indent=2, ensure_ascii=False)
print("patched defaults")
