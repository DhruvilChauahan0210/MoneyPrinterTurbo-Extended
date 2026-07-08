#!/bin/zsh
export PATH="/opt/homebrew/bin:$PATH"   # deno = EJS challenge solver
cd ~/Desktop/MoneyPrinterTurbo-Extended
PY=.venv/bin/python3
ORDER=(
  "batch_neymar_dad:neymar_dad_short"
  "batch_ronaldo_school:ronaldo_school_short"
  "batch_suarez_bite:suarez_bite_short"
)
for pair in $ORDER; do
  batch="${pair%%:*}"; out="${pair##*:}"
  echo "############################################################"
  echo "### BUILDING $batch  ->  ~/Desktop/$out.mp4"
  echo "############################################################"
  $PY batch_generator.py "$batch.json" 2>&1
  newest=$(ls -t storage/tasks/*/final-1.mp4 2>/dev/null | head -1)
  if [[ -n "$newest" ]]; then
    cp "$newest" ~/Desktop/"$out.mp4"
    dur=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$newest" 2>/dev/null)
    echo ">>> COPIED $newest -> ~/Desktop/$out.mp4  (duration=${dur}s)"
    open ~/Desktop/"$out.mp4"
  else
    echo ">>> !!! NO OUTPUT for $batch"
  fi
done
echo "ALL THREE DONE"
