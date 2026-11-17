#!/bin/zsh
# Extra worker: renders ANY config whose finisher sign-off exists and that nobody has attempted yet (reverse plan order). One render per Short, ever.
cd ~/Developer/CDH/MoneyPrinterTurbo-Extended
export PATH="$HOME/.deno/bin:$PWD/.venv/bin:$PATH"
export HF_HUB_DISABLE_TELEMETRY=1
caffeinate -dimsu -w $$ &
mkdir -p /tmp/rr_claim
while true; do
  python3 - <<'PY' > /tmp/render_plan_rev.txt
import json,os
rows=[p for p in json.load(open("topics_nov13_27/plan_nov13_27.json")) if p["cfg"]]
for p in reversed(rows):
    d=os.path.expanduser("~/Desktop")
    log=f"{d}/BUILDLOG_{p['cfg'][:-5]}.log"
    if os.path.exists(f"{d}/{p['out']}.mp4") or os.path.exists(log): continue
    if not os.path.exists(f"topics_nov13_27/finish/{p['name']}.json"): continue
    print(p["cfg"], p["out"], p["name"])
PY
  picked=""
  while read -r cfg out name; do
    mkdir /tmp/rr_claim/$name 2>/dev/null || continue
    picked="$cfg $out $name"; break
  done < /tmp/render_plan_rev.txt
  if [[ -z $picked ]]; then
    left=$(python3 - <<'PY'
import json,os
d=os.path.expanduser("~/Desktop"); n=0
for p in json.load(open("topics_nov13_27/plan_nov13_27.json")):
    if p["cfg"] and not os.path.exists(f"{d}/{p['out']}.mp4") and not os.path.exists(f"{d}/BUILDLOG_{p['cfg'][:-5]}.log"): n+=1
print(n)
PY
)
    (( left == 0 )) && break
    sleep 30; continue
  fi
  set -- ${=picked}; cfg=$1 out=$2 name=$3
  log=~/Desktop/BUILDLOG_${cfg%.json}.log
  echo "RENDER $out $(date +%T)"
  .venv/bin/python batch_generator.py $cfg < /dev/null > $log 2>&1 &
  bpid=$!; rc=0
  for k in {1..100}; do kill -0 $bpid 2>/dev/null || break; sleep 15; done
  if kill -0 $bpid 2>/dev/null; then kill -9 $bpid; rc=124; echo "TIMEOUT $out"; else wait $bpid; rc=$?; fi
  tid=$(grep -o 'task_id: [0-9a-f-]*' $log | tail -1 | awk '{print $2}')
  if [[ -n $tid && -f storage/tasks/$tid/final-1.mp4 ]] && ffprobe -v error -show_entries format=duration -of csv=p=0 storage/tasks/$tid/final-1.mp4 >/dev/null 2>&1; then
    cp storage/tasks/$tid/final-1.mp4 ~/Desktop/$out.mp4; echo "OK $out <- $tid $(date +%T)"
  else
    echo "FAILED $out (rc=$rc) -> $(sed 's/\x1b\[[0-9;]*m//g' $log | grep -o -E 'PREFLIGHT FAILED.*|failed; no retry.*' | head -1 | cut -c1-200)"
  fi
done
echo ALL_DONE_REV
