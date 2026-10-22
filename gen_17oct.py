import json
LEDGER="storage/daily_shorts_clip_ledger.json"
def _era(name,tag,extra):
    base=["close up face","goal celebration close up","close up serious","celebrating close up","close up intense eyes","hat-trick celebration","highlights goals","close up determined face","smiling close up","roaring celebration","4k clips","skills and goals","close up emotional","arms raised celebration","best goals compilation","close up portrait"]
    return [f"{name} {tag} {b}" for b in base[:13]]+extra
ERA={
 'batch_haaland_derby63.json':_era("Erling Haaland","Manchester City 2022",["Haaland Foden hat-trick derby celebration","Haaland Manchester derby 2022 goals","Haaland Etihad 2022-23 goals"]),
 'batch_messi_clasico2007.json':_era("Lionel Messi","Barcelona 2007",["Messi hat-trick Real Madrid 2007 Clasico","Messi Clasico 2007 Camp Nou","young Messi 2007 blaugrana goals"]),
 'batch_ronaldo_atletico2017.json':_era("Cristiano Ronaldo","Real Madrid 2017",["Ronaldo hat-trick Atletico 2017 semi final","Ronaldo Bernabeu 2017 Champions League goals","Ronaldo Real Madrid 2016-17 goals"])}
WIDE={
 'batch_messi_clasico2007.json':["Messi Barcelona 2007 highlights","Messi 2006-07 Barcelona goals compilation","young Messi Barcelona 2007 dribbling","Messi Barcelona 2007 best goals","Messi Barcelona Real Madrid Clasico goals compilation","Messi 2007 highlights Camp Nou"],
 'batch_haaland_derby63.json':["Haaland Man City 2022 highlights","Haaland Premier League 2022-23 goals compilation","Haaland Man City goals Etihad 2022","Haaland celebration Man City 2022","Haaland Premier League 2022 best goals","Erling Haaland 2022-23 season highlights"],
 'batch_ronaldo_atletico2017.json':["Ronaldo Real Madrid 2017 highlights","Ronaldo Champions League 2017 goals","Ronaldo Real Madrid 2016-17 season goals compilation","Ronaldo Real Madrid 2017 best goals","Ronaldo Champions League 2017 knockout goals","Ronaldo Bernabeu 2017 goals celebration"]}
def build(donor,out,subject,script,hook,cta,cover,queries,terms,pos=None):
    queries=ERA[out]
    d=json.load(open(donor)); df=d['defaults']
    df.update(video_subject=subject,video_script=script,hook_text=hook,cta_text=cta,hook_cover_term=cover,
      youtube_footage_queries=queries,video_terms=terms,curated_image_paths=[],era_negative_labels=[],
      series_badge_text="",series_ledger_path=LEDGER,youtube_clips_per_video=8,youtube_max_videos=40)
    if pos:
        df['subject_positive_labels']=pos; df['visual_evidence_prompts']=pos; df['era_positive_labels']=pos[:2]
    d['videos']=[{"video_subject":subject,"video_script":script}]
    json.dump(d,open(out,'w'),indent=2,ensure_ascii=False); print(out,len(script.split()),'words',len(queries),'queries')

build('batch_messi_wembley2011.json','batch_messi_clasico2007.json',
 "On 10 March 2007, a 19-year-old Lionel Messi scored a hat-trick for Barcelona in a 3-3 draw with Real Madrid at the Camp Nou, including a late equaliser",
 "In March two thousand seven, nineteen year old Lionel Messi walked into a Clasico against Real Madrid. Barcelona fell behind twice. Messi scored to level it, then scored again to level it once more. Then, deep in stoppage time, he scored a third to rescue a three all draw. A hat-trick, against Real Madrid, at nineteen.",
 "A TEENAGER REAL MADRID COULD NOT STOP","BEST CLASICO HAT-TRICK EVER? 👇",
 "a tight close up of a young Lionel Messi's face in a Barcelona shirt, intense, face filling the frame",
 ["Messi hat-trick Real Madrid 2007 Clasico 3-3","Barcelona 3-3 Real Madrid 2007 Messi highlights","Messi last minute equaliser Clasico 2007","Messi 19 years old hat trick Camp Nou Real Madrid","Messi Casillas hat trick 2007 goals","Messi Clasico March 2007 celebration","young Messi Barcelona 2007 Real Madrid goals","Messi Van Nistelrooy Clasico 2007 Camp Nou","Barcelona Real Madrid 10 March 2007 full match highlights","Messi teenager Barcelona 2006-07 season goals","Messi 2007 Clasico stoppage time goal reaction","Messi Ronaldinho Barcelona Real Madrid 2007","Messi 2007 Camp Nou hat-trick celebration shirt","young Messi blaugrana 2007 close up","Messi Clasico 2007 first hat-trick Real Madrid","El Clasico 2007 3-3 best moments Messi"],
 "Messi hat-trick Real Madrid 2007, Barcelona 3-3 Real Madrid, Messi Clasico 19 years old")

build('batch_haaland_leipzigfive.json','batch_haaland_derby63.json',
 "In October 2022, in his first Manchester derby, Erling Haaland scored a hat-trick for Manchester City in a 6-3 win over Manchester United, in a match where Phil Foden also scored a hat-trick",
 "In October twenty twenty two, Erling Haaland played in his first Manchester derby. By the end of it, Manchester United had conceded six goals. Haaland scored a hat-trick. And somehow, he was not even the only one. His teammate Phil Foden scored a hat-trick too, and City won six three.",
 "THE DERBY THAT TURNED INTO A MASSACRE","BEST DERBY PERFORMANCE EVER? 👇",
 "a sharp tight close up of Erling Haaland's face, intense, filling the frame",
 ["Haaland hat-trick Manchester derby 6-3 Etihad","Manchester City 6-3 Manchester United October 2022 highlights","Haaland Foden hat-trick derby celebration","Haaland goals Man United derby Etihad 2022","Haaland first Manchester derby goals","Man City United 6-3 Haaland third goal","Haaland derby hat-trick match ball","Foden Haaland hat-trick 6-3 reaction","Erling Haaland celebration Etihad derby","Man City 6-3 Man United full match highlights","Haaland Man United 2022 goal Etihad crowd","Haaland City October 2022 hat-trick","Haaland Guardiola derby 6-3","Haaland Manchester derby 2022 close up","Haaland hat trick 2022 Premier League derby reaction","City United 6-3 best moments Haaland"],
 "Haaland derby hat-trick 6-3, Manchester City United October 2022, Haaland Foden hat-trick")

build('batch_ronaldo_calma2012.json','batch_ronaldo_atletico2017.json',
 "In the 2017 Champions League semi-final first leg, Cristiano Ronaldo scored a hat-trick as Real Madrid beat Atletico Madrid 3-0 at the Bernabeu on the way to winning the Champions League",
 "In May twenty seventeen, Real Madrid faced their city rivals Atletico Madrid in the Champions League semi final. Cristiano Ronaldo scored a hat-trick in the first leg. Real Madrid won three nil at the Bernabeu. That was enough to send them through, and they went on to win the Champions League again.",
 "ONE NIGHT HE ENDED THEIR HOPES","BEST RONALDO NIGHT IN EUROPE? 👇",
 "a tight close up of Cristiano Ronaldo's face in a white Real Madrid shirt, intense, face filling the frame",
 ["Cristiano Ronaldo hat-trick Atletico Madrid 2017 semi final","Real Madrid 3-0 Atletico Madrid 2017 Champions League highlights","Ronaldo Atletico hat trick Bernabeu May 2017","Ronaldo Oblak hat-trick 2017 semi final goals","Real Madrid Atletico 2017 first leg Ronaldo goals celebration","Ronaldo Bernabeu 2017 semi final celebration","Ronaldo hat-trick Atletico Madrid Champions League 2017 match ball","Real Madrid Atletico semi final 2017 Ronaldo third goal","Ronaldo Atletico 2017 Simeone reaction","Ronaldo 2017 Champions League semi final Madrid derby","Ronaldo Real Madrid 2017 hat-trick celebration shirt","Atletico Real Madrid 2017 3-0 best moments","Ronaldo Bernabeu crowd 2017 goal","Ronaldo Madrid derby 2017 Champions League goals","Real Madrid 2017 Champions League run Ronaldo","Ronaldo Atletico hat-trick 2017 full highlights"],
 "Ronaldo hat-trick Atletico 2017, Real Madrid 3-0 Atletico semi final, Ronaldo Bernabeu Champions League 2017")
