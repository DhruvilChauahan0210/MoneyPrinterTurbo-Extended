#!/bin/zsh
# 15-21 Aug 2026 — 21 VOICEOVER shorts, NO background music, no phonk.
# Ronaldo/Messi alternate slot 1 / slot 3 daily (15 Aug = day B: slot1 Messi, slot3 Ronaldo).
# ONE attempt per short, no retries. Runs under caffeinate so the Mac cannot idle-sleep.
cd ~/Developer/CDH/MoneyPrinterTurbo-Extended
export PATH="$HOME/.deno/bin:$PWD/.venv/bin:$PATH"
export HF_HUB_DISABLE_TELEMETRY=1
PY=./.venv/bin/python

ORDER=(
  "batch_messi_copa2021:15AUG_slot1_1300_messi_copa2021"
  "batch_salah_ramos:15AUG_slot2_1700_salah_ramos"
  "batch_ronaldo_moscow:15AUG_slot3_2100_ronaldo_moscow"
  "batch_ronaldo_atletico:16AUG_slot1_1300_ronaldo_atletico"
  "batch_kane_curse:16AUG_slot2_1700_kane_curse"
  "batch_messi_43seconds:16AUG_slot3_2100_messi_43seconds"
  "batch_messi_bobo:17AUG_slot1_1300_messi_bobo"
  "batch_modric_war:17AUG_slot2_1700_modric_war"
  "batch_ronaldo_benched:17AUG_slot3_2100_ronaldo_benched"
  "batch_ronaldo_taxes:18AUG_slot1_1300_ronaldo_taxes"
  "batch_debruyne_mourinho:18AUG_slot2_1700_debruyne_mourinho"
  "batch_messi_suspended:18AUG_slot3_2100_messi_suspended"
  "batch_messi_chess:19AUG_slot1_1300_messi_chess"
  "batch_benzema_booed:19AUG_slot2_1700_benzema_booed"
  "batch_ronaldo_anfield:19AUG_slot3_2100_ronaldo_anfield"
  "batch_ronaldo_saudi:20AUG_slot1_1300_ronaldo_saudi"
  "batch_rashford_mural:20AUG_slot2_1700_rashford_mural"
  "batch_messi_miami:20AUG_slot3_2100_messi_miami"
  "batch_messi_bisht:21AUG_slot1_1300_messi_bisht"
  "batch_griezmann_return:21AUG_slot2_1700_griezmann_return"
  "batch_ronaldo_dinner:21AUG_slot3_2100_ronaldo_dinner"
)

ok=0; fail=0
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
    ok=$((ok+1))
  else
    echo ">>> !!! BUILD FAILED for $batch (no retry)"
    print -r -- "$build_log" | tail -25
    fail=$((fail+1))
  fi
done
echo "ALL 21 ATTEMPTED — ok=$ok failed=$fail"
