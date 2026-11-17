"""Replacement topics for the four NOV 2026 slots whose first topic failed preflight/render
(Canelo 3 NOV s1, Neymar 6 NOV s2, Croatia 8 NOV s1, Anfield 8 NOV s3). New topics, one render each."""
from shortbuild import build


def B(says, visual, *images):
    return {"says": says, "visual": visual, "images": list(images)}


# 3 NOV slot 1 (13:00) — Messi
build("batch_messi_benatia_fifth.json", "batch_messi_pele_644.json",
      subject="Lionel Messi scored his 644th Barcelona goal against Valladolid in December 2020, assisted by Pedri, "
              "breaking Pele's record for the most goals for a single club",
      beats=[B("For decades, one record belonged to Pelé.", "Pele playing for Santos", "Pele Santos", "Pele Santos goal"),
             B("He scored six hundred and forty-three goals for Santos.", "Pele celebrating for Santos",
               "Pele celebration Santos", "Pele Santos 1960s"),
             B("In December twenty twenty, Messi matched him.", "Lionel Messi celebrating for Barcelona in 2020",
               "Messi 643 goal Barcelona", "Messi Barcelona 2020 celebration"),
             B("Days later, against Valladolid, Pedri set him up,", "Pedri playing for Barcelona",
               "Pedri Barcelona 2020", "Pedri Barcelona"),
             B("and Messi scored his six hundred and forty-fourth goal for Barcelona.", "Lionel Messi scoring against Valladolid",
               "Messi 644 goal Valladolid", "Messi goal Valladolid 2020"),
             B("The most ever by one player for one club.", "Lionel Messi pointing to the sky", "Messi pointing up Barcelona",
               "Messi celebration Barcelona"),
             B("Pelé had already posted: when your heart overflows with love, it is difficult to change your path.",
               "Pele smiling as an older man", "Pele smiling", "Pele portrait"),
             B("Messi said he never imagined breaking Pelé's record.", "Lionel Messi smiling in Barcelona kit",
               "Lionel Messi smiling Barcelona", "Messi Barcelona smile"),
             B("Will anyone ever break it?", "close up of Lionel Messi", "Lionel Messi close up", "Lionel Messi Barcelona portrait")],
      hook="THE RECORD NOBODY TOUCHED", cta="WILL ANYONE BREAK IT? 👇",
      terms="Messi 644 goals Pele record Valladolid 2020, Pedri assist, most goals for one club",
      cover="Lionel Messi celebrating for Barcelona",
      positives=["a real photograph of Lionel Messi", "a real photograph of Lionel Messi playing for Barcelona",
                 "a real photograph of Pele"])

# 6 NOV slot 2 (17:00) — Salah
build("batch_mbappe_clasico_ballondor_28pts.json", "batch_salah_trabzon_hattrick.json",
      subject="Mohamed Salah scored a hat-trick and set up another as Trabzonspor beat champions Galatasaray 4-0 on "
              "19 September 2026, Galatasaray's first defeat of the season",
      beats=[B("Mohamed Salah humiliated Turkey's champions.", "Mohamed Salah celebrating", "Mohamed Salah Trabzonspor",
               "Mohamed Salah celebration"),
             B("Weeks after joining Trabzonspor, he faced Galatasaray.", "Mohamed Salah in Trabzonspor kit",
               "Salah Trabzonspor", "Mohamed Salah Trabzonspor 2026"),
             B("He scored after four minutes,", "Mohamed Salah scoring a goal", "Salah goal Galatasaray", "Mohamed Salah goal"),
             B("set up Noah Saviolo,", "Trabzonspor players celebrating", "Trabzonspor celebration", "Trabzonspor players"),
             B("and scored again just before half-time.", "Mohamed Salah celebrating a goal", "Salah celebration Trabzonspor",
               "Mohamed Salah celebrates"),
             B("Galatasaray's coach Okan Buruk was sent to the stands,", "Okan Buruk Galatasaray coach",
               "Okan Buruk", "Okan Buruk Galatasaray"),
             B("and Salah completed his hat-trick in the eightieth minute.", "Mohamed Salah holding the match ball",
               "Mohamed Salah hat-trick", "Salah hat-trick ball"),
             B("Trabzonspor won four-nil, Galatasaray's first defeat of the season.", "Galatasaray players dejected",
               "Galatasaray players dejected", "Galatasaray defeat"),
             B("Is Salah still one of the best in the world?", "close up of Mohamed Salah", "Mohamed Salah close up",
               "Mohamed Salah portrait")],
      hook="NOBODY SAW THIS COMING", cta="STILL WORLD CLASS? 👇",
      terms="Salah hat-trick Trabzonspor Galatasaray 4-0 September 2026, Okan Buruk sent off",
      cover="Mohamed Salah celebrating a goal",
      positives=["a real photograph of Mohamed Salah", "a real photograph of Mohamed Salah playing football",
                 "a real photograph of Trabzonspor players"])

# 8 NOV slot 1 (13:00) — Ronaldo
build("batch_ronaldo_kholood_hattrick.json", "batch_ronaldo_campnou_juve.json",
      subject="Cristiano Ronaldo scored two penalties as Juventus won 3-0 at Camp Nou in December 2020, while Buffon "
              "denied Lionel Messi five times and Juventus took top spot in the group",
      beats=[B("Cristiano Ronaldo walked into Barcelona's stadium and took over.", "Cristiano Ronaldo in Juventus kit",
               "Cristiano Ronaldo Juventus Camp Nou", "Ronaldo Juventus 2020"),
             B("In December twenty twenty, Juventus visited Camp Nou in the Champions League.", "Juventus players at Camp Nou",
               "Barcelona Juventus 2020 Champions League", "Juventus Camp Nou"),
             B("Ronaldo had missed the first meeting with COVID.", "Cristiano Ronaldo looking serious in Juventus kit",
               "Cristiano Ronaldo Juventus serious", "Ronaldo Juventus 2020 portrait"),
             B("This time, he won a penalty and scored after thirteen minutes.", "Cristiano Ronaldo taking a penalty",
               "Ronaldo penalty Barcelona 2020", "Cristiano Ronaldo penalty Juventus"),
             B("Weston McKennie volleyed in a second.", "Weston McKennie celebrating for Juventus",
               "Weston McKennie Barcelona goal", "Weston McKennie Juventus"),
             B("Gianluigi Buffon stopped Lionel Messi again and again,", "Gianluigi Buffon making a save",
               "Buffon save Messi 2020", "Gianluigi Buffon Juventus 2020"),
             B("and Ronaldo scored another penalty after a handball.", "Cristiano Ronaldo celebrating for Juventus",
               "Ronaldo celebration Camp Nou 2020", "Cristiano Ronaldo Juventus celebration"),
             B("Juventus won three-nil and took top spot in the group.", "Juventus players celebrating",
               "Juventus celebrate Barcelona 3-0", "Juventus players celebration 2020"),
             B("Was this Ronaldo's best night against Messi?", "Cristiano Ronaldo and Lionel Messi",
               "Ronaldo Messi Juventus Barcelona 2020", "Ronaldo Messi 2020")],
      hook="BUFFON STOPPED MESSI FIVE TIMES", cta="HIS BEST NIGHT VS MESSI? 👇",
      terms="Barcelona 0-3 Juventus December 2020, Ronaldo two penalties Camp Nou, Buffon saves Messi",
      cover="Cristiano Ronaldo celebrating for Juventus",
      positives=["a real photograph of Cristiano Ronaldo", "a real photograph of Cristiano Ronaldo playing for Juventus",
                 "a real photograph of Gianluigi Buffon", "a real photograph of Lionel Messi"])

# 8 NOV slot 3 (21:00) — Messi
build("batch_messi_benatia_fifth.json", "batch_messi_finalissima_chiellini.json",
      subject="Lionel Messi set up two goals as Argentina beat Italy 3-0 in the 2022 Finalissima at Wembley, in "
              "Giorgio Chiellini's final game for Italy",
      beats=[B("Giorgio Chiellini's last game for Italy turned into a nightmare.", "Giorgio Chiellini in Italy kit",
               "Giorgio Chiellini Italy Finalissima", "Giorgio Chiellini Italy"),
             B("In June twenty twenty-two, Argentina met Italy at Wembley in the Finalissima.", "Argentina against Italy at Wembley",
               "Argentina Italy Finalissima Wembley", "Finalissima 2022"),
             B("Eighty thousand fans watched.", "Wembley stadium full of fans", "Wembley Finalissima crowd", "Wembley stadium crowd"),
             B("Messi beat Giovanni Di Lorenzo and set up Lautaro Martínez.",
               "Lionel Messi dribbling against Italy", "Messi Finalissima dribble", "Messi Italy 2022"),
             B("Ángel Di María made it two before half-time.", "Angel Di Maria celebrating for Argentina",
               "Di Maria goal Italy Finalissima", "Angel Di Maria Argentina celebration"),
             B("Chiellini, in his final Italy game, was taken off at half-time.", "Giorgio Chiellini looking dejected",
               "Chiellini Finalissima", "Giorgio Chiellini sad"),
             B("In stoppage time, Messi set up Paulo Dybala.", "Paulo Dybala celebrating for Argentina",
               "Dybala goal Finalissima", "Paulo Dybala Argentina"),
             B("Argentina won three-nil, six months before winning the World Cup.", "Lionel Messi lifting the Finalissima trophy",
               "Messi Finalissima trophy", "Argentina Finalissima trophy"),
             B("Was this the start of Messi's greatest year?", "close up of Lionel Messi in Argentina shirt",
               "Lionel Messi Argentina close up", "Messi Argentina 2022 portrait")],
      hook="A LEGEND'S FAREWELL RUINED", cta="HIS GREATEST YEAR? 👇",
      terms="Finalissima 2022 Argentina 3-0 Italy Wembley, Messi two assists, Chiellini last game",
      cover="Lionel Messi lifting the Finalissima trophy",
      positives=["a real photograph of Lionel Messi", "a real photograph of Lionel Messi playing for Argentina",
                 "a real photograph of Giorgio Chiellini"])

# 11 NOV slot 3 (21:00) — Ronaldo (replaces the Ferré "liar" topic, blocked by the Jev claim gate)
build("batch_ronaldo_kholood_hattrick.json", "batch_ronaldo_wolfsburg_hattrick.json",
      subject="Cristiano Ronaldo scored a hat-trick as Real Madrid beat Wolfsburg 3-0 in April 2016 to overturn a "
              "2-0 first-leg defeat and reach the Champions League semi-finals",
      beats=[B("Real Madrid were two-nil down, and the Champions League was slipping away.", "Real Madrid players dejected",
               "Real Madrid Wolfsburg 2016 first leg", "Real Madrid players dejected 2016"),
             B("Wolfsburg had won the first leg of the twenty sixteen quarter-final in Germany.", "Wolfsburg players celebrating",
               "Wolfsburg Real Madrid 2-0 2016", "Wolfsburg celebrate Real Madrid"),
             B("Back at the Bernabéu, Cristiano Ronaldo struck after fifteen minutes.", "Cristiano Ronaldo celebrating for Real Madrid",
               "Ronaldo goal Wolfsburg 2016", "Cristiano Ronaldo Real Madrid 2016 celebration"),
             B("Two minutes later, he headed in Toni Kroos's corner.", "Cristiano Ronaldo heading the ball",
               "Ronaldo header Wolfsburg", "Cristiano Ronaldo header Real Madrid"),
             B("Two-two on aggregate.", "Santiago Bernabeu stadium full of fans", "Bernabeu Champions League night",
               "Santiago Bernabeu crowd"),
             B("Then he drove a free kick through the wall.", "Cristiano Ronaldo taking a free kick for Real Madrid",
               "Ronaldo free kick Wolfsburg", "Cristiano Ronaldo free kick Real Madrid"),
             B("Real Madrid won three-nil and reached a sixth straight semi-final.", "Cristiano Ronaldo roaring in celebration",
               "Ronaldo hat-trick Wolfsburg celebration", "Cristiano Ronaldo roar Real Madrid"),
             B("That season, they went on to win the Champions League.", "Cristiano Ronaldo with the Champions League trophy in 2016",
               "Ronaldo Champions League trophy 2016 Milan", "Real Madrid Champions League 2016 celebration"),
             B("Is this Ronaldo's greatest hat-trick?", "close up of Cristiano Ronaldo in Real Madrid kit",
               "Cristiano Ronaldo Real Madrid close up", "Cristiano Ronaldo Real Madrid portrait")],
      hook="THIS LOOKED IMPOSSIBLE", cta="HIS GREATEST HAT-TRICK? 👇",
      terms="Real Madrid 3-0 Wolfsburg April 2016, Ronaldo hat-trick comeback, free kick through the wall",
      cover="Cristiano Ronaldo celebrating for Real Madrid",
      positives=["a real photograph of Cristiano Ronaldo", "a real photograph of Cristiano Ronaldo playing for Real Madrid"])
