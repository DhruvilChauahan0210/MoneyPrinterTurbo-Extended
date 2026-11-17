import sys, json
sys.path.insert(0, ".claude/skills/football-shorts/scripts")
from shortbuild import build  # noqa: E402


def B(says, visual, *images):
    return {"says": says, "visual": visual, "images": list(images)}


OUT = "batch_proto_r3_yamal_euro24_birthday.json"
build("batch_ronaldo_wolfsburg_hattrick.json", OUT,
      subject="Lamine Yamal turned 17 on 13 July 2024, the day before the Euro 2024 final in Berlin, became the youngest player ever to appear in a European Championship final as Spain beat England 2-1 (Williams 47, Palmer 73, Oyarzabal 86), and crossed for Nico Williams's opening goal.",
      beats=[
          B("Yamal turned seventeen. Then, a European final.", "big close up of Lamine Yamal face, Spain kit, Euro 2024", "Lamine Yamal Spain Euro 2024", "Lamine Yamal close up"),
          B("Berlin. Spain against England. Euro final.", "Olympiastadion Berlin Euro 2024 final", "Euro 2024 final Berlin Spain England", "Spain England Euro 2024 final"),
          B("He became the youngest Euro finalist ever.", "Lamine Yamal Spain walking out", "Lamine Yamal Euro 2024 final", "Lamine Yamal Spain"),
          B("Seventeen years and one day old.", "Lamine Yamal portrait Spain", "Lamine Yamal portrait", "Lamine Yamal face Spain"),
          B("Yamal got behind Shaw and crossed low.", "Lamine Yamal dribbling past Luke Shaw", "Yamal cross Nico Williams goal", "Lamine Yamal assist final"),
          B("Nico Williams scored in the forty-seventh minute.", "Nico Williams celebrating goal Spain", "Nico Williams Spain Euro 2024 goal", "Nico Williams celebrating"),
          B("Cole Palmer equalised in the seventy-third.", "Cole Palmer England goal celebration", "Cole Palmer Euro 2024 final goal", "Cole Palmer England"),
          B("Oyarzabal won it in the eighty-sixth.", "Mikel Oyarzabal celebrating Spain", "Mikel Oyarzabal Euro 2024 final goal", "Oyarzabal Spain celebrating"),
          B("Spain won two-one, a record fourth title.", "Spain players lifting the Euro 2024 trophy", "Spain Euro 2024 trophy", "Spain win Euro 2024"),
          B("He also broke Pele's age record.", "Lamine Yamal celebrating with trophy", "Lamine Yamal Euro 2024 trophy", "Lamine Yamal celebrating"),
          B("He won Young Player of the Tournament.", "Lamine Yamal with young player award", "Lamine Yamal young player of the tournament", "Lamine Yamal award Euro 2024"),
          B("Greatest teenage final performance ever?", "close up of Lamine Yamal Spain", "Lamine Yamal smiling Spain", "Lamine Yamal Barcelona portrait"),
      ],
      hook="17 YEARS, 1 DAY, EURO RECORD",
      cta="GREATEST TEENAGE FINAL EVER? \U0001F447",
      terms="Lamine Yamal Euro 2024 final, Spain England 2-1 Berlin, Nico Williams goal, youngest finalist",
      cover="big close up of Lamine Yamal, Spain Euro 2024",
      positives=["a real photograph of Lamine Yamal",
                 "a real photograph of Nico Williams",
                 "a real photograph of Mikel Oyarzabal"])

d = json.load(open(OUT))
df = d["defaults"]
df.update(
    enable_hook_card=True,
    hook_duration=1.2,
    hook_overlay_opacity=0.35,
    enable_subscribe_button=False,
    enable_cta=False,
    cover_min_keep=0.34,
    min_shot_seconds=2.4,
    image_motion_style="varied",
    hook_cover_term="big close up of Lamine Yamal, Spain Euro 2024",
)
json.dump(d, open(OUT, "w"), indent=2, ensure_ascii=False)
print("patched defaults")
