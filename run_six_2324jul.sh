#!/bin/zsh
export PATH="/opt/homebrew/bin:$PATH"   # ensure deno (EJS challenge solver) is found
export YT_DLP_COOKIES=~/Desktop/.yt_cookies.txt
cd ~/Desktop/MoneyPrinterTurbo-Extended
PY=.venv/bin/python3

typeset -A JOBS
ORDER=(
  "batch_messi_injections:messi_injections_short"
  "batch_ronaldo_mother:ronaldo_mother_short"
  "batch_messi_olympics:messi_olympics_short"
  "batch_ronaldo_alone12:ronaldo_alone12_short"
  "batch_messi_ronaldinho:messi_ronaldinho_short"
  "batch_ronaldo_recovery:ronaldo_recovery_short"
)

for pair in $ORDER; do
  batch="${pair%%:*}"
  out="${pair##*:}"
  echo "############################################################"
  echo "### BUILDING $batch  ->  ~/Desktop/$out.mp4"
  echo "############################################################"
  build_log=$($PY batch_generator.py "$batch.json" 2>&1)
  rc=$?
  print -r -- "$build_log"
  generated=$(print -r -- "$build_log" | sed -n 's/^GENERATED_VIDEO=//p' | tail -1)
  if (( rc == 0 )) && [[ -n "$generated" && -f "$generated" ]]; then
    cp "$generated" ~/Desktop/"$out.mp4"
    dur=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$generated" 2>/dev/null)
    echo ">>> COPIED $generated -> ~/Desktop/$out.mp4  (duration=${dur}s)"
  else
    echo ">>> !!! CURRENT BUILD FAILED for $batch — stale output was NOT copied"
  fi
done
echo "ALL SIX DONE"
