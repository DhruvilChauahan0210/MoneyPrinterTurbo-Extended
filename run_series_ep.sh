#!/bin/zsh
# Ronaldo "The Story" series — build one or more episodes. ONE attempt each, 25-min watchdog.
# usage: ./run_series_ep.sh "batch_ronaldo_ep01_oneroom:25AUG_slot1_1300_RONALDO_EP01_oneroom" [...]
cd ~/Developer/CDH/MoneyPrinterTurbo-Extended
export PATH="$HOME/.deno/bin:$PWD/.venv/bin:$PATH"
export HF_HUB_DISABLE_TELEMETRY=1

# Keep display, system and disk awake for the WHOLE run. Display sleep alone used to
# stall long builds; -dimsu holds every assertion until this script exits.
caffeinate -dimsu -w $$ &

PY=./.venv/bin/python

# Pre-flight: config drift (negative-label bloat, an all-time ledger) is what caused the
# 28 Aug failure spike, not the engine. Warn loudly before burning a 15-min render.
echo "--- config budget check ---"
for pair in "$@"; do $PY check_config.py "${pair%%:*}.json"; done
echo "---------------------------"

ok=0; fail=0
RUN_START=$(date +%s)
typeset -a TIMES
for pair in "$@"; do
  batch="${pair%%:*}"; out="${pair##*:}"
  if [[ -f ~/Desktop/"$out.mp4" ]]; then
    echo ">>> SKIP $out (already on Desktop)"; continue
  fi
  echo "### BUILDING $batch  ->  ~/Desktop/$out.mp4"
  EP_START=$(date +%s)
  # --- LEDGER GUARD: a rejected/failed attempt must never burn the ledger ---
  LEDGER=storage/ronaldo_series_clip_ledger.json
  [[ -f $LEDGER ]] && cp $LEDGER /tmp/ledger_before_${batch}.json
  tmplog=~/Desktop/"BUILDLOG_${batch}.log"   # kept, not /tmp: on failure we need the whole thing
  $PY batch_generator.py "$batch.json" > "$tmplog" 2>&1 &
  bpid=$!
  killed=0
  for i in {1..220}; do kill -0 $bpid 2>/dev/null || break; sleep 15; done
  if kill -0 $bpid 2>/dev/null; then
    echo ">>> !!! TIMEOUT after 55 min — killing $batch"; kill -9 $bpid 2>/dev/null; killed=1
  fi
  wait $bpid 2>/dev/null; rc=$?
  (( killed )) && rc=124
  build_log=$(cat "$tmplog")
  generated=$(print -r -- "$build_log" | sed -n 's/^GENERATED_VIDEO=//p' | tail -1)
  if (( rc == 0 )) && [[ -n "$generated" && -f "$generated" ]]; then
    cp "$generated" ~/Desktop/"$out.mp4"
    dur=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$generated" 2>/dev/null)
    EP_SECS=$(( $(date +%s) - EP_START ))
    echo ">>> COPIED -> ~/Desktop/$out.mp4  (duration=${dur}s)"
    printf '>>> TIME %s: %dm %02ds\n' "$out" $((EP_SECS/60)) $((EP_SECS%60))
    TIMES+=("$out ${EP_SECS}")
    ok=$((ok+1))
  else
    if [[ -f /tmp/ledger_before_${batch}.json ]]; then
      cp /tmp/ledger_before_${batch}.json $LEDGER
      echo ">>> ledger rolled back (failed attempt did not burn media)"
    fi
    EP_SECS=$(( $(date +%s) - EP_START ))
    printf '>>> TIME %s: %dm %02ds (FAILED)\n' "$out" $((EP_SECS/60)) $((EP_SECS%60))
    TIMES+=("$out ${EP_SECS} FAILED")
    echo ">>> !!! BUILD FAILED for $batch (no retry)"
    echo ">>> full log kept at $tmplog"
    print -r -- "$build_log" | tail -30
    fail=$((fail+1))
  fi
done
RUN_SECS=$(( $(date +%s) - RUN_START ))
echo
echo "=============== BUILD TIMES ==============="
for t in "${TIMES[@]}"; do
  name="${t%% *}"; rest="${t#* }"; secs="${rest%% *}"; flag="${rest#* }"
  [[ "$flag" == "$secs" ]] && flag=""
  printf '  %-46s %2dm %02ds %s\n' "$name" $((secs/60)) $((secs%60)) "$flag"
done
printf '  %-46s %2dm %02ds\n' "TOTAL (all $# shorts, sequential)" $((RUN_SECS/60)) $((RUN_SECS%60))
echo "=========================================="
echo "ATTEMPTED $# — ok=$ok failed=$fail"
