#!/bin/zsh
# Ronaldo "The Story" series — build one or more episodes. ONE attempt each, 25-min watchdog.
# usage: ./run_series_ep.sh "batch_ronaldo_ep01_oneroom:25AUG_slot1_1300_RONALDO_EP01_oneroom" [...]
cd ~/Developer/CDH/MoneyPrinterTurbo-Extended
export PATH="$HOME/.deno/bin:$PWD/.venv/bin:$PATH"
export HF_HUB_DISABLE_TELEMETRY=1
PY=./.venv/bin/python

ok=0; fail=0
for pair in "$@"; do
  batch="${pair%%:*}"; out="${pair##*:}"
  if [[ -f ~/Desktop/"$out.mp4" ]]; then
    echo ">>> SKIP $out (already on Desktop)"; continue
  fi
  echo "### BUILDING $batch  ->  ~/Desktop/$out.mp4"
  tmplog="/tmp/mpt_${batch}.log"
  $PY batch_generator.py "$batch.json" > "$tmplog" 2>&1 &
  bpid=$!
  killed=0
  for i in {1..100}; do kill -0 $bpid 2>/dev/null || break; sleep 15; done
  if kill -0 $bpid 2>/dev/null; then
    echo ">>> !!! TIMEOUT after 25 min — killing $batch"; kill -9 $bpid 2>/dev/null; killed=1
  fi
  wait $bpid 2>/dev/null; rc=$?
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
    print -r -- "$build_log" | tail -30
    fail=$((fail+1))
  fi
done
echo "ATTEMPTED $# — ok=$ok failed=$fail"
