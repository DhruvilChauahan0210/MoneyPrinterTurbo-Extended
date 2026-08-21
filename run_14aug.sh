#!/bin/zsh
# 14 Aug 2026 batch — 3 VOICEOVER shorts, NO background music, no phonk
# Day parity A: slot 1 Ronaldo, slot 3 Messi
cd ~/Developer/CDH/MoneyPrinterTurbo-Extended
export PATH="$HOME/.deno/bin:$PWD/.venv/bin:$PATH"
export HF_HUB_DISABLE_TELEMETRY=1
PY=./.venv/bin/python

ORDER=(
  "batch_ronaldo_fergie:14AUG_slot1_1300_ronaldo_fergie"
  "batch_mbappe_macron:14AUG_slot2_1700_mbappe_macron"
  "batch_messi_banned:14AUG_slot3_2100_messi_banned"
)

for pair in $ORDER; do
  batch="${pair%%:*}"; out="${pair##*:}"
  echo "### BUILDING $batch  ->  ~/Desktop/$out.mp4"
  build_log=$($PY batch_generator.py "$batch.json" 2>&1)
  rc=$?
  generated=$(print -r -- "$build_log" | sed -n 's/^GENERATED_VIDEO=//p' | tail -1)
  if (( rc == 0 )) && [[ -n "$generated" && -f "$generated" ]]; then
    cp "$generated" ~/Desktop/"$out.mp4"
    dur=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$generated" 2>/dev/null)
    echo ">>> COPIED -> ~/Desktop/$out.mp4  (duration=${dur}s)"
  else
    echo ">>> !!! BUILD FAILED for $batch"
    print -r -- "$build_log" | tail -25
  fi
done
echo "ALL THREE DONE"
