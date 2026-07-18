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
  build_log=$($PY batch_generator.py "$batch.json" 2>&1)
  rc=$?
  print -r -- "$build_log"
  generated=$(print -r -- "$build_log" | sed -n 's/^GENERATED_VIDEO=//p' | tail -1)
  if (( rc == 0 )) && [[ -n "$generated" && -f "$generated" ]]; then
    cp "$generated" ~/Desktop/"$out.mp4"
    dur=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$generated" 2>/dev/null)
    echo ">>> COPIED $generated -> ~/Desktop/$out.mp4  (duration=${dur}s)"
    open ~/Desktop/"$out.mp4"
  else
    echo ">>> !!! CURRENT BUILD FAILED for $batch — stale output was NOT copied"
  fi
done
echo "ALL THREE DONE"
