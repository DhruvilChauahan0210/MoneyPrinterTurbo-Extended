#!/bin/zsh
# Build one short and measure it against a reference, end to end.
# usage: ./build_and_compare.sh batch_ronaldo_5ucl TEST_5UCL 30AUG_UPLOAD/30AUG_slot3_2100_RONALDO_EP12_heart.mp4
set -o pipefail
cd ~/Developer/CDH/MoneyPrinterTurbo-Extended
export PATH="$HOME/.deno/bin:$PWD/.venv/bin:$PATH"
BATCH="${1:-batch_ronaldo_5ucl}"; OUT="${2:-TEST_5UCL}"
REF="${3:-$HOME/Desktop/30AUG_UPLOAD/30AUG_slot3_2100_RONALDO_EP12_heart.mp4}"
PY=./.venv/bin/python
FF=$(ls .venv/lib/python*/site-packages/static_ffmpeg/bin/darwin_arm64/ffmpeg 2>/dev/null | head -1)
[[ -z "$FF" ]] && FF=$(command -v ffmpeg)
REPORT=~/Desktop/COMPARE_${OUT}.txt

echo "=== BUILD: $BATCH -> ~/Desktop/$OUT.mp4 ==="
START=$(date +%s)
./run_series_ep.sh "$BATCH:$OUT" 2>&1 | tee ~/Desktop/BUILD_${OUT}.log
ELAPSED=$(( $(date +%s) - START ))
echo "WALL CLOCK: ${ELAPSED}s ($((ELAPSED/60))m $((ELAPSED%60))s)" | tee -a ~/Desktop/BUILD_${OUT}.log

NEW=~/Desktop/$OUT.mp4
if [[ ! -f "$NEW" ]]; then
  echo "!!! build produced no file — see ~/Desktop/BUILD_${OUT}.log"
  exit 1
fi

echo; echo "=== MEASURING ==="
FFMPEG_BIN="$FF" ELAPSED="$ELAPSED" BUILD_LOG=~/Desktop/BUILD_${OUT}.log \
$PY tools_compare.py "$NEW" "$REF" | tee "$REPORT"
echo; echo "report saved: $REPORT"
