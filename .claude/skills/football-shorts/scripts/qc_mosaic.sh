#!/bin/zsh
# 6 evenly spaced frames per Short (from 1.8s, after the hook card) -> one strip per Short, 5 strips per image.
# Usage: qc_mosaic.sh OUTDIR "<grep pattern for Desktop files, e.g. ^1[2-9]NOV_slot>"
OUT=$1; PAT=$2
FF=~/Developer/CDH/MoneyPrinterTurbo-Extended/.venv/bin/ffmpeg
PY=~/Developer/CDH/MoneyPrinterTurbo-Extended/.venv/bin/python
mkdir -p $OUT; rm -f $OUT/r_*.jpg $OUT/qc_*.jpg
i=0
for f in $(ls ~/Desktop | grep -E "$PAT" | grep -v WHATIF | sort); do
  d=$($FF -i ~/Desktop/$f 2>&1 | grep -o 'Duration: [0-9:.]*' | awk -F: '{print $4}')
  st=$(echo "($d-2)/6" | bc -l)
  $FF -v error -y -ss 1.8 -i ~/Desktop/$f -vf "fps=1/$st,scale=150:-1,tile=6x1" -frames:v 1 $OUT/r_$(printf %02d $i).jpg
  echo "$i $f ${d}s"; i=$((i+1))
done
$PY - "$OUT" <<'E'
import glob, sys
from PIL import Image
out = sys.argv[1]; fs = sorted(glob.glob(f"{out}/r_*.jpg"))
for k in range(0, len(fs), 5):
    ims = [Image.open(f) for f in fs[k:k + 5]]
    c = Image.new("RGB", (max(i.width for i in ims), sum(i.height for i in ims))); y = 0
    for i in ims: c.paste(i, (0, y)); y += i.height
    c.save(f"{out}/qc_{k // 5}.jpg", quality=80)
print("mosaics:", sorted(glob.glob(f"{out}/qc_*.jpg")))
E
