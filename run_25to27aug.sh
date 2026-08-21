#!/bin/zsh
# 25-27 Aug 2026 — 9 VOICEOVER shorts, NO background music, no phonk.
# Ronaldo/Messi alternate slot 1 / slot 3 daily (25 Aug = day B: slot1 Messi, slot3 Ronaldo).
# ONE attempt per short, no retries. 25-min watchdog per build. Skips finished shorts.
cd ~/Developer/CDH/MoneyPrinterTurbo-Extended
export PATH="$HOME/.deno/bin:$PWD/.venv/bin:$PATH"
export HF_HUB_DISABLE_TELEMETRY=1
PY=./.venv/bin/python

ORDER=(
  "batch_messi_helicopter:25AUG_slot1_1300_messi_helicopter"
  "batch_pogba_ban:25AUG_slot2_1700_pogba_ban"
  "batch_ronaldo_euro2004:25AUG_slot3_2100_ronaldo_euro2004"
  "batch_ronaldo_spain_hattrick:26AUG_slot1_1300_ronaldo_spain_hattrick"
  "batch_ramos_reds:26AUG_slot2_1700_ramos_reds"
  "batch_messi_tax:26AUG_slot3_2100_messi_tax"
  "batch_messi_sleeping:27AUG_slot1_1300_messi_sleeping"
  "batch_trent_corner:27AUG_slot2_1700_trent_corner"
  "batch_ronaldo_donations:27AUG_slot3_2100_ronaldo_donations"
)

ok=0; fail=0
for pair in $ORDER; do
  batch="${pair%%:*}"; out="${pair##*:}"
  if [[ -f ~/Desktop/"$out.mp4" ]]; then
    echo ">>> SKIP $out (already on Desktop)"
    continue
  fi
  echo "### BUILDING $batch  ->  ~/Desktop/$out.mp4"
  tmplog="/tmp/mpt_${batch}.log"
  $PY batch_generator.py "$batch.json" > "$tmplog" 2>&1 &
  bpid=$!
  killed=0
  for i in {1..100}; do
    kill -0 $bpid 2>/dev/null || break
    sleep 15
  done
  if kill -0 $bpid 2>/dev/null; then
    echo ">>> !!! TIMEOUT after 25 min — killing $batch and moving on"
    kill -9 $bpid 2>/dev/null
    killed=1
  fi
  wait $bpid 2>/dev/null
  rc=$?
  (( killed )) && rc=124
  build_log=$(cat "$tmplog")
  generated=$(print -r -- "$build_log" | sed -n 's/^GENERATED_VIDEO=//p' | tail -1)
  if (( rc == 0 )) && [[ -n "$generated" && -f "$generated" ]]; then
    cp "$generated" ~/Desktop/"$out.mp4"
    dur=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$generated" 2>/dev/null)
    echo ">>> COPIED -> ~/Desktop/$out.mp4  (duration=${dur}s)"
    ok=$((ok+1))
  else
    echo ">>> !!! BUILD FAILED for $batch (no retry)"
    print -r -- "$build_log" | tail -25
    fail=$((fail+1))
  fi
done
echo "9 SHORTS ATTEMPTED — ok=$ok failed=$fail"
