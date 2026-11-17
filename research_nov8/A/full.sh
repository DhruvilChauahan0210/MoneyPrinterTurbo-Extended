#!/bin/bash
# usage: full.sh handle [n]
export PATH="$HOME/.deno/bin:$HOME/Developer/CDH/MoneyPrinterTurbo-Extended/.venv/bin:$PATH"
cd ~/Developer/CDH/MoneyPrinterTurbo-Extended/research_nov8/A
h="$1"; n="${2:-45}"
yt-dlp --skip-download --ignore-errors --no-warnings --sleep-requests 1 --playlist-end $n -j "https://www.youtube.com/@$h/${TAB:-shorts}" 2>>ch/err_$h.txt | python3 -I -c '
import sys,json
for l in sys.stdin:
    try: d=json.loads(l)
    except: continue
    keep={k:d.get(k) for k in ["id","title","channel","uploader_id","channel_follower_count","upload_date","timestamp","duration","view_count","like_count","comment_count","tags","width","height","categories"]}
    keep["desc"]=(d.get("description") or "")[:300]
    print(json.dumps(keep,ensure_ascii=False))
' > ch/full_$h.jsonl
wc -l ch/full_$h.jsonl
