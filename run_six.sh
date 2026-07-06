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
  $PY batch_generator.py "$batch.json" 2>&1
  # grab the newest rendered final video and copy to Desktop
  newest=$(ls -t storage/tasks/*/final-1.mp4 2>/dev/null | head -1)
  if [[ -n "$newest" ]]; then
    cp "$newest" ~/Desktop/"$out.mp4"
    dur=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$newest" 2>/dev/null)
    echo ">>> COPIED $newest -> ~/Desktop/$out.mp4  (duration=${dur}s)"
  else
    echo ">>> !!! NO OUTPUT for $batch"
  fi
done
echo "ALL SIX DONE"
