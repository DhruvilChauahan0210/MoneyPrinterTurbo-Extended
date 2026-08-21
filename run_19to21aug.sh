#!/bin/zsh
# RESUME script — remaining 9 shorts for 19-21 Aug 2026.
# 15-18 Aug were built on 12 Aug 2026 by run_15to21aug.sh.
# Voiceover, NO background music, no phonk. ONE attempt per short, no retries.
cd ~/Developer/CDH/MoneyPrinterTurbo-Extended
export PATH="$HOME/.deno/bin:$PWD/.venv/bin:$PATH"
export HF_HUB_DISABLE_TELEMETRY=1
PY=./.venv/bin/python

ORDER=(
  "batch_messi_chess:19AUG_slot1_1300_messi_chess"
  "batch_benzema_booed:19AUG_slot2_1700_benzema_booed"
  "batch_ronaldo_anfield:19AUG_slot3_2100_ronaldo_anfield"
  "batch_ronaldo_saudi:20AUG_slot1_1300_ronaldo_saudi"
  "batch_rashford_mural:20AUG_slot2_1700_rashford_mural"
  "batch_messi_miami:20AUG_slot3_2100_messi_miami"
  "batch_messi_bisht:21AUG_slot1_1300_messi_bisht"
  "batch_griezmann_return:21AUG_slot2_1700_griezmann_return"
  "batch_ronaldo_dinner:21AUG_slot3_2100_ronaldo_dinner"
)

ok=0; fail=0
for pair in $ORDER; do
  batch="${pair%%:*}"; out="${pair##*:}"
  if [[ -f ~/Desktop/"$out.mp4" ]]; then
    echo ">>> SKIP $out (already on Desktop)"
    continue
  fi
  echo "### BUILDING $batch  ->  ~/Desktop/$out.mp4"
  # 25-min watchdog: a normal build takes ~8 min, so anything past 25 is a hang.
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
echo "REMAINING 9 ATTEMPTED — ok=$ok failed=$fail"
