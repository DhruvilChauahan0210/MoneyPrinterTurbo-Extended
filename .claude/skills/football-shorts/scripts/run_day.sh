#!/bin/zsh
# One-render-per-Short build runner (CD's no-retry rule).
# Usage: run_day.sh plan.txt [regex-filter]
#   plan.txt: one line per Short ->  batch_config.json  DDMON_slotN_HHMM_topic
# Each build: caffeinate, 25-min watchdog, skip if already on Desktop or already attempted once,
# copy final-1.mp4 to ~/Desktop/<out>.mp4. Failures are printed, never retried.
cd ~/Developer/CDH/MoneyPrinterTurbo-Extended
export PATH="$HOME/.deno/bin:$PWD/.venv/bin:$PATH"
export HF_HUB_DISABLE_TELEMETRY=1
caffeinate -dimsu -w $$ &
PY=.venv/bin/python
PLAN=$1
FILTER=${2:-.}

build() {
  local cfg=$1 out=$2
  [[ $out =~ $FILTER ]] || return 0
  if [[ -f ~/Desktop/$out.mp4 ]]; then echo "skip $out (exists)"; return 0; fi
  local log=~/Desktop/BUILDLOG_${cfg%.json}.log
  if [[ -f $log ]] && grep -q 'task_id:' $log; then echo "skip $out (already attempted once)"; return 0; fi
  $PY batch_generator.py $cfg > $log 2>&1 &
  local bpid=$! rc=0 i
  for i in {1..100}; do kill -0 $bpid 2>/dev/null || break; sleep 15; done
  if kill -0 $bpid 2>/dev/null; then kill -9 $bpid; rc=124; echo "TIMEOUT $out"; else wait $bpid; rc=$?; fi
  local tid=$(grep -o 'task_id: [0-9a-f-]*' $log | tail -1 | awk '{print $2}')
  if [[ -n $tid && -f storage/tasks/$tid/final-1.mp4 ]]; then
    cp storage/tasks/$tid/final-1.mp4 ~/Desktop/$out.mp4; echo "OK $out <- $tid"
  else
    echo "FAILED $out (rc=$rc) -> $(sed 's/\x1b\[[0-9;]*m//g' $log | grep -o -E 'PREFLIGHT FAILED.*|failed; no retry.*' | head -1 | cut -c1-220)"
  fi
}

while read -r cfg out; do
  [[ -z $cfg || $cfg == \#* ]] && continue
  build $cfg $out
done < $PLAN
echo ALL_DONE
