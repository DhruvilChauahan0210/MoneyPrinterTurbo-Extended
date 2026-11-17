#!/bin/zsh
# 2-11 NOV 2026 build: 25 voiced beat-plan Shorts (What-Ifs are run_whatif_nov.sh).
# ONE render per short (CD, 1 Nov 2026: no retries) — a failure is reported, never rebuilt.
# Usage: ./run_nov.sh [grep-filter]   e.g. ./run_nov.sh slot2
cd ~/Developer/CDH/MoneyPrinterTurbo-Extended
export PATH="$HOME/.deno/bin:$PWD/.venv/bin:$PATH"
export HF_HUB_DISABLE_TELEMETRY=1
caffeinate -dimsu -w $$ &
PY=.venv/bin/python
FILTER=${1:-.}

build() {
  local cfg=$1 out=$2
  [[ $out =~ $FILTER ]] || return 0
  if [[ -f ~/Desktop/$out.mp4 ]]; then echo "skip $out (exists)"; return 0; fi
  local log=~/Desktop/BUILDLOG_${cfg%.json}.log
  if [[ -f $log ]] && grep -q 'task_id:' $log; then echo "skip $out (already attempted once)"; return 0; fi
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

build batch_ronaldo_kholood_hattrick.json          02NOV_slot1_1300_ronaldo_kholood_hattrick
build batch_mbappe_clasico_ballondor_28pts.json    02NOV_slot2_1700_mbappe_clasico_ballondor_28pts
build batch_messi_benatia_fifth.json               02NOV_slot3_2100_messi_benatia_fifth
build batch_messi_canelo_threat.json               03NOV_slot1_1300_messi_canelo_threat
build batch_ronaldo_boat_fanvote.json              03NOV_slot3_2100_ronaldo_boat_fanvote
build batch_ronaldo_982_owngoal.json               04NOV_slot1_1300_ronaldo_982_owngoal
build batch_yamal_henry_kopa_jab.json              04NOV_slot2_1700_yamal_henry_kopa_jab
build batch_messi_gvardiol_semifinal.json          04NOV_slot3_2100_messi_gvardiol_semifinal
build batch_messi_muller_mlscup.json               05NOV_slot1_1300_messi_muller_mlscup
build batch_ronaldo_ettifaq_armband.json           05NOV_slot3_2100_ronaldo_ettifaq_armband
build batch_ronaldo_toney_goldenboot.json          06NOV_slot1_1300_ronaldo_toney_goldenboot
build batch_neymar_mouth_red_card.json             06NOV_slot2_1700_neymar_mouth_red_card
build batch_messi_arsenal_fourgoals.json           06NOV_slot3_2100_messi_arsenal_fourgoals
build batch_messi_psg_clubworldcup_40.json         07NOV_slot1_1300_messi_psg_clubworldcup_40
build batch_ronaldo_alhilal_unbeaten_title.json    07NOV_slot3_2100_ronaldo_alhilal_unbeaten_title
build batch_ronaldo_croatia_knockout_curse.json    08NOV_slot1_1300_ronaldo_croatia_knockout_curse
build batch_bellingham_eleventh_mourinho.json      08NOV_slot2_1700_bellingham_eleventh_mourinho
build batch_messi_anfield_2019_collapse.json       08NOV_slot3_2100_messi_anfield_2019_collapse
build batch_messi_ronaldo_riyadh_54.json           09NOV_slot1_1300_messi_ronaldo_riyadh_54
build batch_ronaldo_yamal_consoled_wc.json         09NOV_slot3_2100_ronaldo_yamal_consoled_wc
build batch_ronaldo_abdulghani_pampered.json       10NOV_slot1_1300_ronaldo_abdulghani_pampered
build batch_haaland_anfield_cheats.json            10NOV_slot2_1700_haaland_anfield_cheats
build batch_messi_bayern_82_lisbon.json            10NOV_slot3_2100_messi_bayern_82_lisbon
build batch_messi_chest_goal_estudiantes.json      11NOV_slot1_1300_messi_chest_goal_estudiantes
build batch_ronaldo_ferre_liar_boycott.json        11NOV_slot3_2100_ronaldo_ferre_liar_boycott
build batch_messi_pele_644.json                     03NOV_slot1_1300_messi_pele_644
build batch_salah_trabzon_hattrick.json            06NOV_slot2_1700_salah_trabzon_hattrick
build batch_ronaldo_campnou_juve.json              08NOV_slot1_1300_ronaldo_campnou_juve
build batch_messi_finalissima_chiellini.json       08NOV_slot3_2100_messi_finalissima_chiellini
build batch_ronaldo_wolfsburg_hattrick.json        11NOV_slot3_2100_ronaldo_wolfsburg_hattrick
echo ALL_DONE
