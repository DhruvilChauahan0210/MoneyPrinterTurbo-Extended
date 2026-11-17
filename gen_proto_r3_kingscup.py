import sys, json
sys.path.insert(0, ".claude/skills/football-shorts/scripts")
from shortbuild import build  # noqa: E402


def B(says, visual, *images):
    return {"says": says, "visual": visual, "images": list(images)}


OUT = "batch_proto_r3_kingscup.json"
build("batch_ronaldo_wolfsburg_hattrick.json", OUT,
      subject="In the 31 May 2024 Saudi King's Cup final in Jeddah Al Nassr drew 1-1 with Al Hilal and lost 5-4 on penalties, Cristiano Ronaldo scoring his penalty before Yassine Bounou saved Al Nassr's last two, and Ronaldo wept on the pitch.",
      beats=[
          B("Ronaldo sobbed after the King's Cup final.", "big close up of Cristiano Ronaldo crying in yellow Al Nassr kit", "Cristiano Ronaldo crying Al Nassr", "Ronaldo tears King's Cup final"),
          B("Al Hilal led from the seventh minute.", "Aleksandar Mitrovic Al Hilal celebrating", "Aleksandar Mitrovic Al Hilal", "Mitrovic goal Al Nassr"),
          B("Ospina's red card left Al Nassr with ten.", "David Ospina Al Nassr goalkeeper", "David Ospina Al Nassr", "Ospina red card"),
          B("Still, Aiman Yahya equalised in the eighty-eighth.", "Aiman Yahya Al Nassr celebrating", "Aiman Yahya Al Nassr", "Ayman Yahya goal"),
          B("One-one after extra time. Penalties.", "Cristiano Ronaldo Al Nassr serious face", "Cristiano Ronaldo Al Nassr", "Ronaldo Al Nassr penalty"),
          B("Ronaldo scored his penalty.", "Cristiano Ronaldo taking a penalty Al Nassr", "Ronaldo penalty Al Nassr", "Cristiano Ronaldo Al Nassr 2024"),
          B("Bounou saved Al Nassr's last two.", "Yassine Bounou Al Hilal goalkeeper", "Yassine Bounou Al Hilal", "Bounou penalty save"),
          B("Al Hilal won five-four.", "Al Hilal players celebrating King's Cup", "Al Hilal King's Cup 2024", "Al Hilal celebrate"),
          B("Ronaldo slumped to the turf, inconsolable.", "Cristiano Ronaldo crying on the pitch", "Ronaldo crying pitch Al Nassr", "Ronaldo emotional Al Nassr"),
          B("At thirty-nine, tears streamed down his face.", "close up of Cristiano Ronaldo in tears", "Ronaldo tears Al Nassr", "Cristiano Ronaldo sad Al Nassr"),
          B("His thirty-five goals didn't win the league.", "Cristiano Ronaldo Al Nassr portrait", "Cristiano Ronaldo Al Nassr portrait", "Cristiano Ronaldo Al Nassr goal celebration"),
          B("Are those tears passion, or pressure?", "close up of Cristiano Ronaldo in Al Nassr kit", "Cristiano Ronaldo Al Nassr close up", "Cristiano Ronaldo face Al Nassr"),
      ],
      hook="5-4 HEARTBREAK IN JEDDAH",
      cta="PASSION OR PRESSURE? \U0001F447",
      terms="Ronaldo, Al Nassr, Al Hilal, King's Cup final 2024, penalties, Bounou, tears, Jeddah",
      cover="big close up of Cristiano Ronaldo crying, Al Nassr",
      positives=["a real photograph of Cristiano Ronaldo",
                 "a real photograph of Aleksandar Mitrovic",
                 "a real photograph of Yassine Bounou",
                 "a real photograph of David Ospina"])

d = json.load(open(OUT))
df = d["defaults"]
df.update(
    enable_hook_card=True,
    hook_duration=1.2,
    hook_overlay_opacity=0.35,
    enable_subscribe_button=False,
    enable_cta=True,
    cover_min_keep=0.36,
    min_shot_seconds=2.4,
    image_motion_style="varied",
)
json.dump(d, open(OUT, "w"), indent=2, ensure_ascii=False)
print("patched defaults")
