#!/bin/zsh
# 8 Aug 2026 batch — 3 shorts, slots 13:00 / 17:00 / 21:00 IST
cd ~/Developer/CDH/MoneyPrinterTurbo-Extended
export PATH="$HOME/.deno/bin:$PWD/.venv/bin:$PATH"
export HF_HUB_DISABLE_TELEMETRY=1
PY=./.venv/bin/python

ORDER=(
  "batch_ronaldo_number7:08AUG_slot1_1300_ronaldo_number7"
  "batch_mbappe_madrid13:08AUG_slot2_1700_mbappe_madrid13"
  "batch_messi_nashville_solo_phonk:08AUG_slot3_2100_messi_solo_phonk"
)

for pair in $ORDER; do
  batch="${pair%%:*}"; out="${pair##*:}"
  echo "############################################################"
  echo "### BUILDING $batch  ->  ~/Desktop/$out.mp4"
  echo "############################################################"
  build_log=$($PY batch_generator.py "$batch.json" 2>&1)
  rc=$?
  print -r -- "$build_log" | tail -40
  generated=$(print -r -- "$build_log" | sed -n 's/^GENERATED_VIDEO=//p' | tail -1)
  if (( rc == 0 )) && [[ -n "$generated" && -f "$generated" ]]; then
    cp "$generated" ~/Desktop/"$out.mp4"
    dur=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$generated" 2>/dev/null)
    echo ">>> COPIED $generated -> ~/Desktop/$out.mp4  (duration=${dur}s)"
  else
    echo ">>> !!! BUILD FAILED for $batch — stale output was NOT copied"
  fi
done
echo "ALL THREE DONE"
