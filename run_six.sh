#!/bin/zsh
export PATH="/opt/homebrew/bin:$PATH"   # ensure deno (EJS challenge solver) is found
cd ~/Desktop/MoneyPrinterTurbo-Extended
PY=.venv/bin/python3

# batch file  ->  desktop output name
typeset -A JOBS
ORDER=(
  "batch_ronaldo_son:ronaldo_son_short"
  "batch_messi_prison:messi_prison_short"
  "batch_neymar_court:neymar_court_short"
  "batch_mbappe_mum:mbappe_mum_short"
  "batch_haaland_madrid:haaland_madrid_short"
  "batch_yamal_threats:yamal_threats_short"
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
