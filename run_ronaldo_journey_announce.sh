#!/bin/zsh
# One-off: 30s Ronaldo career-journey SERIES ANNOUNCEMENT short. ONE attempt, 30-min watchdog.
cd ~/Developer/CDH/MoneyPrinterTurbo-Extended
export PATH="$HOME/.deno/bin:$PWD/.venv/bin:$PATH"
export HF_HUB_DISABLE_TELEMETRY=1
PY=./.venv/bin/python
batch="batch_ronaldo_journey_announce"
out="RONALDO_JOURNEY_SERIES_ANNOUNCEMENT"
[[ -f ~/Desktop/"$out.mp4" ]] && { echo ">>> SKIP (already on Desktop)"; exit 0; }
tmplog="/tmp/mpt_${batch}.log"
$PY batch_generator.py "$batch.json" > "$tmplog" 2>&1 &
bpid=$!
killed=0
for i in {1..120}; do kill -0 $bpid 2>/dev/null || break; sleep 15; done
if kill -0 $bpid 2>/dev/null; then echo ">>> TIMEOUT 30min — killing"; kill -9 $bpid 2>/dev/null; killed=1; fi
wait $bpid 2>/dev/null; rc=$?
(( killed )) && rc=124
generated=$(sed -n 's/^GENERATED_VIDEO=//p' "$tmplog" | tail -1)
if (( rc == 0 )) && [[ -n "$generated" && -f "$generated" ]]; then
  cp "$generated" ~/Desktop/"$out.mp4"
  dur=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$generated")
  echo ">>> COPIED -> ~/Desktop/$out.mp4  (duration=${dur}s)"
else
  echo ">>> BUILD FAILED (no retry)"; tail -30 "$tmplog"
fi
