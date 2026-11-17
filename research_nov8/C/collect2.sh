#!/bin/bash
export PATH="$HOME/.deno/bin:$HOME/Developer/CDH/MoneyPrinterTurbo-Extended/.venv/bin:$PATH"
cd ~/Developer/CDH/MoneyPrinterTurbo-Extended/research_nov8/C
OUT=$2; LOG=$3; START=$1
Q=("cristiano ronaldo" "lionel messi" "kylian mbappe" "erling haaland" "lamine yamal" "vinicius junior" "jude bellingham" "harry kane" "mohamed salah" "neymar" "ballon d'or" "world cup 2026" "champions league" "el clasico" "premier league" "transfer news football" "football what if" "football never forget" "unforgettable football moment" "football rivalry" "footballer family" "footballer childhood story" "humiliated football" "football revenge" "football record" "funniest football moments" "ronaldo vs messi" "football legend story" "football comeback" "football referee VAR" "football quiz" "world cup final" "ronaldo portugal" "messi inter miami" "barcelona" "real madrid" "liverpool" "manchester united" "arsenal" "football heartbreak")
V=("A:EgIYAQ%253D%253D" "B:EgQIBBgB" "C:CAMSBAgEGAE%253D" "W:CAMSBAgDGAE%253D")
for q in "${Q[@]:$START:$4}"; do
  for v in "${V[@]}"; do
    tag=${v%%:*}; sp=${v#*:}
    qq=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote_plus(sys.argv[1]))" "$q")
    yt-dlp --flat-playlist --playlist-end 30 -j --sleep-requests 1 "https://www.youtube.com/results?search_query=$qq&sp=$sp" 2>/dev/null \
     | python3 -c "
import sys,json
for l in sys.stdin:
    try:d=json.loads(l)
    except: continue
    if d.get('duration') is None or d.get('ie_key')!='Youtube': continue
    print(json.dumps({'id':d['id'],'title':d['title'],'channel':d.get('channel'),'channel_id':d.get('channel_id'),'views':d.get('view_count'),'duration':d.get('duration'),'query':sys.argv[1],'variant':sys.argv[2]},ensure_ascii=False))
" "$q" "$tag" >> $OUT
    sleep 1
  done
  echo "done $q $(wc -l < $OUT)" >> $LOG
done
echo FINISHED >> $LOG
