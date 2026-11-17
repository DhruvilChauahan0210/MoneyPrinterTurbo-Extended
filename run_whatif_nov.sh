#!/bin/zsh
# What-If slot-2 shorts for 3/5/7/9/11 NOV 2026 (Remotion WhatIf composition).
cd ~/Developer/CDH/MoneyPrinterTurbo-Extended
caffeinate -dimsu -w $$ &
FF=$PWD/.venv/bin/ffmpeg
render() {
  local out=$1 img=$2 voice=$3 l1=$4 l2=$5 music=$6
  [[ -f ~/Desktop/$out.mp4 ]] && { echo "skip $out"; return; }
  local wav=whatif-remotion/public/vo_${out}.wav
  .venv/bin/edge-tts --voice en-US-EricNeural --text "$voice" --write-media /tmp/vo_$$.mp3 >/dev/null 2>&1
  $FF -v error -y -i /tmp/vo_$$.mp3 -ar 48000 -ac 2 $wav
  local dur=$($FF -i $wav 2>&1 | grep -o 'Duration: [0-9:.]*' | awk -F: '{print $4}')
  local total=$(printf "%.2f" $(( dur + 1.2 )))
  local props=$(.venv/bin/python -c "import json,sys;print(json.dumps(dict(imageFile=sys.argv[1],voiceFile=sys.argv[2],musicFile=sys.argv[3],line1=sys.argv[4],line2=sys.argv[5],musicVolume=0.12,sfxFile='boom.mp3',ambienceFile='stadium.mp3',ambienceVolume=0.06,durationInSeconds=float(sys.argv[6]))))" $img vo_${out}.wav $music "$l1" "$l2" $total)
  (cd whatif-remotion && npx remotion render src/index.ts WhatIf out/$out.mp4 --props="$props" --log=error) && cp whatif-remotion/out/$out.mp4 ~/Desktop/$out.mp4 && echo "OK $out ${total}s"
}
render 03NOV_slot2_1700_WHATIF_neymar_2014 wi_neymar_2014.jpg "What if Neymar had never been injured at the 2014 World Cup in Brazil?" "WHAT IF NEYMAR WASN'T" "INJURED IN 2014?" music.mp3
render 05NOV_slot2_1700_WHATIF_ronaldo_stayed_madrid wi_ronaldo_2018.jpg "What if Cristiano Ronaldo had never left Real Madrid in 2018?" "WHAT IF RONALDO NEVER" "LEFT REAL MADRID IN 2018?" music2.mp3
render 07NOV_slot2_1700_WHATIF_messi_stayed_barca wi_messi_2021.jpg "What if Lionel Messi had never left Barcelona in 2021?" "WHAT IF MESSI NEVER" "LEFT BARCELONA IN 2021?" music3.mp3
render 09NOV_slot2_1700_WHATIF_haaland_madrid_2022 wi_haaland_2022.jpg "What if Erling Haaland had joined Real Madrid instead of Manchester City in 2022?" "WHAT IF HAALAND JOINED" "REAL MADRID IN 2022?" music4.mp3
render 11NOV_slot2_1700_WHATIF_yamal_morocco wi_yamal_morocco.jpg "What if Lamine Yamal had chosen to play for Morocco instead of Spain?" "WHAT IF YAMAL CHOSE" "MOROCCO OVER SPAIN?" music5.mp3
echo WHATIF_DONE
