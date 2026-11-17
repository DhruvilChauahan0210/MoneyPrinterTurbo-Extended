#!/bin/zsh
# Usage: render_worker.sh WORKER_INDEX NUM_WORKERS    (plan = topics_nov13_27/plan_nov13_27.json, normal Shorts only)
# Each Short is rendered exactly ONCE (CD's rule), only after its finisher wrote topics_nov13_27/finish/<name>.json.
cd ~/Developer/CDH/MoneyPrinterTurbo-Extended
export PATH="$HOME/.deno/bin:$PWD/.venv/bin:$PATH"
export HF_HUB_DISABLE_TELEMETRY=1
W=$1 N=$2
caffeinate -dimsu -w $$ &
python3 - <<'PY' > /tmp/render_plan.txt
import json
for p in json.load(open("topics_nov13_27/plan_nov13_27.json")):
    if p["cfg"]: print(p["cfg"], p["out"], p["name"])
PY
i=0
exec 4< /tmp/render_plan.txt
while read -r -u4 cfg out name; do
  (( i++ ))
  (( (i-1) % N == W )) || continue
  fin=topics_nov13_27/finish/$name.json
  until [[ -f $fin ]]; do sleep 20; done
  if [[ -f ~/Desktop/$out.mp4 ]]; then echo "skip $out (exists)"; continue; fi
  log=~/Desktop/BUILDLOG_${cfg%.json}.log
  if [[ -f $log ]] && grep -q 'task_id:' $log; then echo "skip $out (already attempted once)"; continue; fi
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
echo ALL_DONE_W$W
