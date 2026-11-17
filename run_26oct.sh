#!/bin/zsh
# 26 OCT 2026 build: 3 beat-plan shorts, sequential, 25-min watchdog each, Desktop-skip.
cd ~/Developer/CDH/MoneyPrinterTurbo-Extended
export PATH="$HOME/.deno/bin:$PWD/.venv/bin:$PATH"
export HF_HUB_DISABLE_TELEMETRY=1
caffeinate -dimsu -w $$ &
PY=.venv/bin/python

build() {
  local cfg=$1 out=$2
  if [[ -f ~/Desktop/$out.mp4 ]]; then echo "skip $out (exists)"; return 0; fi
  local log=~/Desktop/BUILDLOG_${cfg%.json}.log
  $PY batch_generator.py $cfg > $log 2>&1 &
  local bpid=$! rc=0 i
  for i in {1..100}; do
    kill -0 $bpid 2>/dev/null || break
    sleep 15
  done
  if kill -0 $bpid 2>/dev/null; then
    kill -9 $bpid; rc=124; echo "TIMEOUT $out"
  else
    wait $bpid; rc=$?
  fi
  local tid=$(grep -o 'task_id: [0-9a-f-]*' $log | tail -1 | awk '{print $2}')
  if [[ -n $tid && -f storage/tasks/$tid/final-1.mp4 ]]; then
    cp storage/tasks/$tid/final-1.mp4 ~/Desktop/$out.mp4
    echo "OK $out <- $tid (rc=$rc)"
  else
    echo "FAILED $out (rc=$rc, task=$tid)"
  fi
}

build batch_messi_asturias_award.json 26OCT_slot1_1300_messi_asturias_award
build batch_yamal_mbappe_teen_record.json 26OCT_slot2_1700_yamal_mbappe_teen_record
build batch_ronaldo_alnassr_stake.json 26OCT_slot3_2100_ronaldo_alnassr_stake
echo ALL_DONE
