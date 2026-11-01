#!/bin/zsh
# Render one What-If Short with the Remotion WhatIf composition and copy it to the Desktop.
# Usage: whatif.sh OUT IMAGE "VOICE TEXT" "LINE 1" "LINE 2" [music.mp3]
#   OUT    e.g. 13NOV_slot2_1700_WHATIF_kane_spurs
#   IMAGE  a file already in whatif-remotion/public/ (e.g. wi_kane_spurs.jpg)
#   VOICE  the full question read aloud ("What if Harry Kane had never left Tottenham?")
#   LINE 1/2  the headline split over two ALL-CAPS lines ("WHAT IF KANE NEVER" / "LEFT TOTTENHAM?")
# Duration = voice length + 1.2s. Rotate music.mp3 .. music5.mp3 between Shorts.
cd ~/Developer/CDH/MoneyPrinterTurbo-Extended
caffeinate -dimsu -w $$ &
FF=$PWD/.venv/bin/ffmpeg
out=$1 img=$2 voice=$3 l1=$4 l2=$5 music=${6:-music.mp3}
[[ -f ~/Desktop/$out.mp4 ]] && { echo "skip $out"; exit 0; }
wav=whatif-remotion/public/vo_${out}.wav
.venv/bin/edge-tts --voice en-US-EricNeural --text "$voice" --write-media /tmp/vo_$$.mp3 >/dev/null 2>&1
$FF -v error -y -i /tmp/vo_$$.mp3 -ar 48000 -ac 2 $wav
dur=$($FF -i $wav 2>&1 | grep -o 'Duration: [0-9:.]*' | awk -F: '{print $4}')
total=$(printf "%.2f" $(( dur + 1.2 )))
props=$(.venv/bin/python -c "import json,sys;print(json.dumps(dict(imageFile=sys.argv[1],voiceFile=sys.argv[2],musicFile=sys.argv[3],line1=sys.argv[4],line2=sys.argv[5],musicVolume=0.12,sfxFile='boom.mp3',ambienceFile='stadium.mp3',ambienceVolume=0.06,durationInSeconds=float(sys.argv[6]))))" $img vo_${out}.wav $music "$l1" "$l2" $total)
(cd whatif-remotion && npx remotion render src/index.ts WhatIf out/$out.mp4 --props="$props" --log=error) \
  && cp whatif-remotion/out/$out.mp4 ~/Desktop/$out.mp4 && echo "OK $out ${total}s"
