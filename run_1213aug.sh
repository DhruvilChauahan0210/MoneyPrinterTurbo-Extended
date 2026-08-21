#!/bin/zsh
# 12–13 Aug 2026 batches — 6 VOICEOVER shorts, NO background music, no phonk
# 12 Aug = day A (slot 1 Ronaldo, slot 3 Messi); 13 Aug = day B (slot 1 Messi, slot 3 Ronaldo)
cd ~/Developer/CDH/MoneyPrinterTurbo-Extended
export PATH="$HOME/.deno/bin:$PWD/.venv/bin:$PATH"
export HF_HUB_DISABLE_TELEMETRY=1
PY=./.venv/bin/python

ORDER=(
  "batch_ronaldo_cocacola:12AUG_slot1_1300_ronaldo_cocacola"
  "batch_neymar_sister:12AUG_slot2_1700_neymar_sister"
  "batch_messi_psg_booed:12AUG_slot3_2100_messi_psg_booed"
  "batch_messi_saidno:13AUG_slot1_1300_messi_saidno"
  "batch_haaland_sleep:13AUG_slot2_1700_haaland_sleep"
  "batch_ronaldo_euro_coach:13AUG_slot3_2100_ronaldo_euro_coach"
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
echo "ALL SIX DONE"
