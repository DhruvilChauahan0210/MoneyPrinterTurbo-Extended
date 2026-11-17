"""Scene list for the 10-minute 'Ronaldo retires from Portugal' video (5 Nov 2026 announcement).

Every fact below was checked against ESPN / Al Jazeera / Wikipedia / match reports on 6 Nov 2026 (see chat).
Each scene = one narrated line + one photo + optional overlays. `ch` marks a chapter card.
Overlay kinds: date, slam, stats, stat, quote, chip, flash, confetti.
"""


def S(text, shot, *ov, kb=None, sfx=None):
    return {"text": text, "shot": shot, "ov": list(ov), "kb": kb, "sfx": sfx}


def CH(n, title, text, shot):
    return {"ch": n, "title": title, "text": text, "shot": shot, "ov": [], "kb": "in", "sfx": "riser"}


def date(t, at=0.2):
    return {"k": "date", "t": t, "at": at}


def slam(t, c="white", at=0.2, size=170, y=0.5):
    return {"k": "slam", "t": t, "c": c, "at": at, "size": size, "y": y}


def chip(t, c="gold", at=0.4, pos="tl"):
    return {"k": "chip", "t": t, "c": c, "at": at, "pos": pos}


def stat(v, l, sub="", c="gold", at=0.2, suf="", dec=0):
    return {"k": "stat", "v": v, "l": l, "sub": sub, "c": c, "at": at, "suf": suf, "dec": dec}


def stats(items, at=0.2):
    return {"k": "stats", "items": items, "at": at}


def quote(t, who="CRISTIANO RONALDO", at=0.2):
    return {"k": "quote", "t": t, "who": who, "at": at}


FLASH = {"k": "flash", "at": 0.0}
CONF = {"k": "confetti", "at": 0.3}

SCENES = [
    # ---------------- HOOK ----------------
    S("Thursday. November the fifth. Twenty twenty-six.", "ronaldo_2026_portrait", date("THU · 5 NOV 2026"), kb="in", sfx="impact"),
    S("A video appears on Cristiano Ronaldo's Instagram.", "ronaldo_closeup_a", chip("NEW POST · INSTAGRAM", "red"), kb="left"),
    S("In it, he says he will hand back the number seven shirt.", "ronaldo_portugal_7", slam("NUMBER 7", "gold"), kb="in", sfx="whoosh"),
    S("Two hundred and thirty-four caps. A hundred and forty-six goals. Twenty-three years.", "ronaldo_captain_armband",
      stats([{"v": 234, "l": "CAPS"}, {"v": 146, "l": "GOALS"}, {"v": 23, "l": "YEARS"}]), kb="out"),
    S("And now, it's over.", "ronaldo_walking_away", FLASH, slam("IT'S OVER", "red"), kb="in", sfx="impact"),
    S("But the strangest part isn't that he's leaving.", "ronaldo_closeup_b", kb="right"),
    S("It's how it started. With a bench in Norway.", "ronaldo_bench_2022", date("OCT 4 · NORWAY"), kb="in", sfx="whoosh"),
    S("Stay until the end. Because there is one number that explains everything that happens next.", "ronaldo_closeup_c",
      slam("ONE NUMBER", "gold", size=190), kb="out", sfx="riser"),
    S("In the next ten minutes: the bench, the records, the tears, and the goal that is still ahead.", "ronaldo_free_kick", kb="in", sfx="whoosh"),

    # ---------------- CHAPTER 1 ----------------
    CH(1, "THE BENCH", "Chapter one. The bench.", "ronaldo_bench_2022"),
    S("Go back to September. Portugal have a new manager: Jorge Jesus.", "jorge_jesus", chip("NEW MANAGER", "red"), kb="in"),
    S("The same man who coached Ronaldo at Al Nassr.", "ronaldo_alnassr", kb="left"),
    S("Portugal were still hurting. They had just lost their World Cup knockout game in the ninety-first minute, and Roberto Martínez had stepped down.", "ronaldo_wc2026_sad", kb="in"),
    S("Jesus was handed a fresh start, and one very big decision about his captain.", "portugal_squad", kb="out"),
    S("September twenty-fourth. Lisbon. Portugal beat Wales, one-nil, and Ronaldo plays.", "portugal_stadium",
      date("SEP 24 · LISBON"), slam("1–0", "white", at=1.8), kb="out"),
    S("Nobody knows it yet, but it is his last match for Portugal.", "ronaldo_free_kick", slam("HIS LAST", "gold"), kb="in", sfx="impact"),
    S("Next game. Jesus leaves him on the bench.", "ronaldo_training", kb="right"),
    S("October fourth. Norway. Portugal win two-one, and Ronaldo never leaves the bench.", "portugal_squad",
      date("OCT 4 · NORWAY"), kb="in"),
    S("For the first time in eighteen years, he was available and didn't play.", "ronaldo_bench_2022",
      stat(18, "YEARS", "FIRST TIME HE WAS AVAILABLE AND DIDN'T PLAY", c="red"), kb="out", sfx="impact"),
    S("Jesus says he won't start him in the next game either.", "jorge_jesus", kb="left"),
    S("So Ronaldo does something nobody expected. He walks out of the national team camp.", "ronaldo_walking_away",
      FLASH, slam("WALKED OUT", "red"), kb="in", sfx="whoosh"),
    S("The federation answers with a thirty-day suspension.", "ronaldo_training", slam("30-DAY BAN", "red"), kb="right"),
    S("Ronaldo apologises to his teammates, but not to the coach.", "ronaldo_training", kb="in"),
    S("He says Jesus broke his promises about playing time.", "jorge_jesus", chip("'BROKEN PROMISES'", "red", pos="bl"), kb="out"),
    S("Jesus replies that the door is open, and the decision belongs to Ronaldo.", "ronaldo_closeup_c", kb="in"),
    S("And now, that decision has been made.", "ronaldo_2026_portrait", slam("DECISION MADE", "gold", size=150), kb="out", sfx="impact"),
    S("Forty-two days. That is how long it took to go from his last match for Portugal to goodbye.", "ronaldo_closeup_b",
      stat(42, "DAYS", "FROM HIS LAST MATCH TO GOODBYE", c="red"), kb="in", sfx="riser"),

    # ---------------- CHAPTER 2 ----------------
    CH(2, "THE NUMBERS", "Chapter two. The numbers.", "ronaldo_captain_armband"),
    S("Let's put twenty-three years into numbers.", "ronaldo_closeup_a", kb="in"),
    S("Two hundred and thirty-four caps. The most of any man in the history of international football.", "ronaldo_portugal_7",
      stat(234, "CAPS", "MOST EVER", c="gold"), kb="out", sfx="impact"),
    S("A hundred and forty-six goals. Also the most. Ever.", "ronaldo_siuu", stat(146, "GOALS", "ALL-TIME RECORD", c="gold"), kb="in", sfx="impact"),
    S("Forty-one goals in World Cup qualifying. Another record.", "ronaldo_free_kick", stat(41, "QUALIFYING GOALS", "WORLD CUP RECORD", c="white"), kb="right"),
    S("Thirty matches at the European Championship. Fourteen goals. Both records.", "ronaldo_euro2020",
      stats([{"v": 30, "l": "EURO MATCHES"}, {"v": 14, "l": "EURO GOALS"}]), kb="out"),
    S("The only player to score at five European Championships.", "ronaldo_euro2016_trophy", stat(5, "EUROS", "ONLY PLAYER EVER", c="gold"), kb="in", sfx="impact"),
    S("And the only player to score at six World Cups.", "ronaldo_wc2026", stat(6, "WORLD CUPS", "ONLY PLAYER EVER", c="gold"), kb="left", sfx="impact"),
    S("He captained Portugal to Euro 2016, the 2019 Nations League and the 2025 Nations League.", "ronaldo_nl2025_trophy",
      stats([{"v": 2016, "l": "EURO", "raw": 1}, {"v": 2019, "l": "NATIONS LEAGUE", "raw": 1}, {"v": 2025, "l": "NATIONS LEAGUE", "raw": 1}]), kb="out"),
    S("A hundred and forty-one international wins, and more goals than anyone else has ever scored for a country.", "ronaldo_closeup_a", stat(141, "WINS", "WITH PORTUGAL", c="white"), kb="in"),
    S("Three trophies. But one is still missing: the World Cup.", "ronaldo_wc2026_sad", slam("NO WORLD CUP", "red", size=150), kb="in", sfx="riser"),

    # ---------------- CHAPTER 3 ----------------
    CH(3, "THE BOY FROM MADEIRA", "Chapter three. The boy from Madeira.", "ronaldo_young_2003"),
    S("He was born on the island of Madeira, and left home at twelve to join Sporting's academy in Lisbon.", "ronaldo_young_2003", date("FUNCHAL, MADEIRA · 1985"), kb="in"),
    S("That summer of 2003, Manchester United signed him from Sporting. He was eighteen.", "ronaldo_manutd_2008", kb="out"),
    S("Rewind twenty-three years. August twentieth, 2003.", "ronaldo_young_2003", date("20 AUG 2003"), kb="in"),
    S("An eighteen-year-old comes off the bench against Kazakhstan, and a legend begins.", "ronaldo_young_2003", slam("AGE 18", "gold"), kb="out", sfx="whoosh"),
    S("Summer, 2004. Euro 2004, at home. Portugal reach the final.", "ronaldo_fans_portugal", date("EURO 2004 · PORTUGAL"), kb="left"),
    S("They lose to Greece. And the teenager cries on the pitch.", "ronaldo_euro2004_tears", kb="in", sfx="impact"),
    S("Twelve years later. Euro 2016. The final, against France.", "ronaldo_captain_armband", date("JULY 10 · PARIS"), kb="right"),
    S("Portugal had barely scraped through the group stage, with three draws from three games.", "portugal_squad", kb="in"),
    S("But Ronaldo scored in the semi-final, a header against Wales, to put them in the final.", "ronaldo_euro2016_trophy", kb="out"),
    S("Twenty-five minutes in, Ronaldo is forced off, in tears.", "ronaldo_euro2016_injured", slam("25 MINUTES", "red"), kb="in", sfx="impact"),
    S("Then he is on the touchline, shouting instructions like a coach.", "ronaldo_euro2016_injured", kb="out"),
    S("Extra time. Eder scores. One-nil Portugal.", "portugal_stadium", slam("1–0", "gold", size=240), kb="in", sfx="whoosh"),
    S("Portugal are champions of Europe, and Ronaldo lifts the trophy.", "ronaldo_euro2016_trophy", FLASH, CONF, kb="out", sfx="sparkle"),
    S("The boy who cried in 2004 had finally won.", "ronaldo_euro2004_tears", chip("2004  →  2016", "gold"), kb="in"),

    # ---------------- CHAPTER 4 ----------------
    CH(4, "THE RECORD BREAKER", "Chapter four. The record breaker.", "ronaldo_daei_record"),
    S("The goals keep coming. June 2021. Euro 2020. France.", "ronaldo_euro2020", date("23 JUN 2021 · EURO 2020"), kb="in"),
    S("He scores twice and equals the record of the Iranian legend Ali Daei: a hundred and nine.", "ali_daei", slam("109", "gold", size=240), kb="out", sfx="impact"),
    S("It took him nearly eighteen years of international football to catch him.", "ronaldo_young_2003", kb="in"),
    S("Two months later, against Ireland, the record is his alone.", "ronaldo_daei_record", slam("RECORD BROKEN", "gold", size=140), kb="in", sfx="whoosh"),
    S("He finishes that tournament as top scorer and wins the Golden Boot.", "ronaldo_closeup_b", chip("EURO 2020 GOLDEN BOOT", "gold"), kb="left"),
    S("November 2022. Qatar. A penalty against Ghana, and he becomes the first man to score at five World Cups.", "ronaldo_ghana_2022",
      slam("FIRST EVER", "gold", size=160), chip("5 WORLD CUPS", "gold", pos="bl"), kb="in", sfx="impact"),
    S("Then comes the fall. Benched for the round of sixteen.", "ronaldo_bench_2022", slam("BENCHED", "red"), kb="out"),
    S("Portugal win six-one without him.", "portugal_squad", slam("6–1", "white", size=230), kb="in", sfx="impact"),
    S("Then Morocco. A quarter-final lost, and Ronaldo walks down the tunnel in tears.", "ronaldo_morocco_tears", kb="right", sfx="riser"),
    S("Euro 2024. A missed penalty in extra time against Slovenia, and more tears.", "ronaldo_euro2024_tears", date("EURO 2024 · SLOVENIA"), kb="in"),
    S("But goalkeeper Diogo Costa saves three penalties, and Portugal survive.", "diogo_costa", slam("3 SAVES", "gold", size=170), kb="out", sfx="whoosh"),

    # ---------------- CHAPTER 5 ----------------
    CH(5, "THE LAST DANCE", "Chapter five. The last dance.", "ronaldo_nl2025_trophy"),
    S("June eighth, 2025. Munich. The Nations League final against Spain.", "ronaldo_nl2025_trophy", date("8 JUN 2025 · MUNICH"), kb="in"),
    S("Spain score. Nuno Mendes levels it. Spain lead again before half-time.", "ronaldo_closeup_a", chip("SPAIN 2–1 PORTUGAL", "red", pos="bl"), kb="right"),
    S("Then, in the sixty-first minute, forty-year-old Cristiano Ronaldo equalises.", "ronaldo_free_kick", slam("61'", "gold", size=240), chip("40 YEARS OLD", "gold"), kb="in", sfx="impact"),
    S("Two-two. Extra time. Penalties.", "ronaldo_closeup_c", slam("2–2", "white", size=250), kb="out", sfx="riser"),
    S("Diogo Costa saves from Morata. Rúben Neves scores. Portugal win five-three.", "diogo_costa", slam("5–3", "gold", size=250), FLASH, kb="in", sfx="impact"),
    S("Another trophy for Ronaldo, at forty.", "ronaldo_nl2025_trophy", CONF, kb="out", sfx="sparkle"),
    S("He had warned us. In November 2025, he said the 2026 World Cup would be his last tournament.", "ronaldo_closeup_b", kb="in"),
    S("Then comes his sixth and final World Cup. Summer 2026. North America.", "ronaldo_wc2026", date("WORLD CUP 2026"), kb="left"),
    S("He scores three goals, and becomes the only player ever to score at six World Cups.", "ronaldo_wc2026",
      stat(3, "GOALS", "ONLY PLAYER EVER TO SCORE AT 6 WORLD CUPS", c="gold"), kb="in", sfx="impact"),
    S("July sixth. Arlington, Texas. The round of sixteen. Spain, again.", "ronaldo_closeup_b", date("6 JUL · ARLINGTON, TEXAS"), kb="right"),
    S("Nil-nil. The ninety-first minute. Mikel Merino scores.", "ronaldo_wc2026_sad", slam("90+1'", "red", size=240), kb="in", sfx="impact"),
    S("Spain win one-nil, and Portugal are out.", "ronaldo_wc2026_sad", slam("1–0", "red", size=250), kb="out"),
    S("Ronaldo's World Cup story is over, and manager Roberto Martínez steps down.", "ronaldo_closeup_c", kb="in"),
    S("In comes Jorge Jesus.", "jorge_jesus", kb="out", sfx="whoosh"),

    # ---------------- CHAPTER 6 ----------------
    CH(6, "THE GOODBYE", "Chapter six. The goodbye.", "ronaldo_2026_portrait"),
    S("So on Thursday, the message lands. A video, posted on Instagram, with a message to the whole country.", "ronaldo_2026_portrait", date("NOV 5 · INSTAGRAM"), kb="in"),
    S("'It was not an easy decision, because there are decisions that are not made solely with the head.'", "ronaldo_closeup_a",
      quote("It was not an easy decision, because there are decisions that are not made solely with the head."), kb="out"),
    S("He calls his twenty-three years with Portugal a journey that changed his life forever.", "ronaldo_euro2016_trophy", kb="in"),
    S("He says Portugal will always be a part of him.", "ronaldo_portugal_7", quote("Portugal will always be a part of me."), kb="right"),
    S("He admits there were failures along the way, but says he never gave up on representing Portugal.", "ronaldo_morocco_tears", kb="in"),
    S("He thanks his teammates and coaches, and tells the next generation to keep believing.", "portugal_squad", kb="out"),
    S("The federation calls him the greatest player of all time, and promises a tribute so the fans can celebrate him again.", "ronaldo_fans_portugal",
      chip("FPF · 'THE GREATEST PLAYER OF ALL TIME'", "gold", pos="bl"), kb="out"),
    S("Jorge Jesus says he asked Ronaldo to stay, and accepts the decision.", "jorge_jesus", kb="in"),
    S("Manchester United, Sporting and Juventus all pay tribute.", "ronaldo_manutd_2008", chip("MANCHESTER UNITED · SPORTING · JUVENTUS", "white", pos="bl"), kb="left"),
    S("And just last month, Lionel Messi said goodbye to Argentina.", "messi_argentina_farewell", date("MESSI · FAREWELL"), kb="in", sfx="whoosh"),
    S("The two greatest players of their generation, leaving the national stage within weeks of each other.", "ronaldo_closeup_c",
      slam("AN ERA ENDS", "gold", size=170), kb="out", sfx="riser"),
    S("And one question hangs over Portugal now. Who wears the number seven?", "ronaldo_portugal_7", slam("WHO WEARS 7?", "white", size=160), kb="in", sfx="impact"),

    # ---------------- CHAPTER 7 : BOTH SIDES ----------------
    CH(7, "BOTH SIDES", "Chapter seven. Both sides.", "jorge_jesus"),
    S("Here is the question everyone is arguing about. Who was right?", "ronaldo_closeup_c", slam("WHO WAS RIGHT?", "gold", size=150), kb="in", sfx="riser"),
    S("The case for Jorge Jesus. He is the manager, and a manager picks the team.", "jorge_jesus", chip("THE CASE FOR JESUS", "white"), kb="right"),
    S("He had a new team to build after a painful World Cup exit.", "portugal_squad", kb="in"),
    S("And when Ronaldo walked out of camp, the federation backed its manager and suspended its captain.", "portugal_stadium", kb="out"),
    S("The case for Ronaldo. He is the most capped and the highest-scoring international of all time.", "ronaldo_portugal_7", chip("THE CASE FOR RONALDO", "gold"), kb="in", sfx="whoosh"),
    S("Only a few months earlier, he had scored three goals at a World Cup.", "ronaldo_wc2026", kb="left"),
    S("And he says he was promised playing time that never came.", "ronaldo_training", kb="in"),
    S("Then there is the part nobody can argue with. Jesus asked him to stay, and Ronaldo said no.", "ronaldo_walking_away", kb="out"),
    S("Maybe the truth sits somewhere in the middle: a proud captain, and a manager who would not bend.", "ronaldo_closeup_a", kb="in"),
    S("What neither side can deny is this. Portugal lost its greatest ever player, and he lost his national team.", "ronaldo_closeup_b",
      slam("NO WINNER", "gold", size=170), kb="out", sfx="impact"),

    # ---------------- CHAPTER 8 ----------------
    CH(8, "WHAT HAPPENS NEXT", "Chapter eight. What happens next.", "ronaldo_alnassr"),
    S("But this is not the end of Ronaldo. It is only the end of Ronaldo and Portugal.", "ronaldo_alnassr", kb="in"),
    S("Look at what is left of his career. Five Ballon d'Or awards.", "ronaldo_ballondor", stat(5, "BALLON D'OR", "", c="gold"), kb="out", sfx="impact"),
    S("Five Champions League titles, across Manchester United and Real Madrid.", "ronaldo_realmadrid_ucl", stat(5, "CHAMPIONS LEAGUES", "", c="white"), kb="in"),
    S("At Real Madrid alone, nine years, and four hundred and fifty goals in four hundred and thirty-eight games.", "ronaldo_manutd_2008",
      stats([{"v": 450, "l": "GOALS"}, {"v": 438, "l": "GAMES"}]), kb="left"),
    S("Portugal go on without him. Jorge Jesus named his squad for Nations League games against Denmark and Wales the very next day.", "portugal_squad", kb="in"),
    S("He will keep playing for Al Nassr, where his contract runs until June 2027.", "ronaldo_2026_portrait", chip("AL NASSR · UNTIL JUNE 2027", "gold"), kb="right"),
    S("But reports say he is expected to finish his club career at the end of this season.", "ronaldo_alnassr", kb="in"),
    S("And he has already said how it ends. In November 2025, he told us to expect one or two more years.", "ronaldo_closeup_c", kb="out"),
    S("In a recent Vogue interview, he said: 'This is probably my last year of football, and I want to leave a spectacular legacy.'",
      "ronaldo_closeup_b", quote("This is probably my last year of football, and I want to leave a spectacular legacy.", "CRISTIANO RONALDO · VOGUE"), kb="out"),
    S("He is forty-one years old.", "ronaldo_closeup_c", stat(41, "YEARS OLD", "", c="white"), kb="in"),
    S("And he has nine hundred and eighty-five career goals.", "ronaldo_free_kick", stat(985, "CAREER GOALS", "", c="gold"), kb="out", sfx="impact"),
    S("Fifteen more, and he reaches one thousand.", "ronaldo_ballondor", stat(15, "GOALS TO 1,000", "", c="red"), FLASH, kb="in", sfx="riser"),
    S("That is the number. Fifteen.", "ronaldo_closeup_a", slam("15", "gold", size=420, y=0.45), kb="out", sfx="impact"),
    S("So remember three things. One: he leaves as the all-time record holder for both caps and goals.", "ronaldo_portugal_7", kb="in"),
    S("Two: it did not end with a farewell tour. It ended with a bench, a walkout and a suspension.", "ronaldo_walking_away", kb="out"),
    S("And three: there is still one number left to chase.", "ronaldo_free_kick", kb="in", sfx="riser"),
    S("Portugal's chapter is closed. This one is still being written.", "ronaldo_2026_portrait", kb="out"),
    S("So tell me in the comments: did Portugal handle this the right way?", "ronaldo_portugal_7", kb="left"),
    S("Was Jesus wrong, or was Ronaldo? Drop your answer below.", "ronaldo_closeup_b", kb="right"),
    S("And if you want the full story of Ronaldo and Messi, watch Messi versus Ronaldo, the final answer, next. Subscribe, so you don't miss the thousandth goal.",
      "ronaldo_2026_portrait", chip("SUBSCRIBE · CD PHANTOM", "red", pos="bl"), kb="out", sfx="whoosh"),
]

# Trimmed after the first voice pass (12.8 min -> ~10 min): weakest / duplicated lines.
DROP = (
    "Let's put twenty-three years into numbers.",
    "Portugal had barely scraped through",
    "It took him nearly eighteen years",
    "Jesus was handed a fresh start",
    "He had a new team to build",
    "He thanks his teammates and coaches",
    "And he has already said how it ends.",
    "Only a few months earlier, he had scored three goals",
    "A hundred and forty-one international wins",
    "Portugal were still hurting.",
    "The same man who coached Ronaldo at Al Nassr.",
)
SCENES = [s for s in SCENES if not s["text"].startswith(DROP)]
for _s in SCENES:
    if _s["text"].startswith("Go back to September."):
        _s["text"] = "Go back to September. Portugal have a new manager: Jorge Jesus, the same man who coached Ronaldo at Al Nassr."

if __name__ == "__main__":
    words = sum(len(s["text"].split()) for s in SCENES)
    print(len(SCENES), "scenes,", words, "words, est", round(words / 2.75 / 60, 1), "min at 165 wpm")
