#!/bin/zsh
# Build one 'PICK ONE' duel Short from a JSON spec (default: Dembele vs Yamal). ~10 minutes per new pair.
#   prototypes/r2/make_duel.sh [spec.json]          # TTS + mix + render + copy to ~/Desktop/<spec.out>.mp4
#   prototypes/r2/make_duel.sh spec.json --no-render # only TTS/mix/props (timeline printed)
# New pair = copy duel_dembele_yamal.json, change: key/out, left/right (name, sub, color, posX/posY), photos (src + face crop box),
# rows (4 verified stat pairs), reveal (number/label/detail/question), source, segments (voice lines; row0..row3, reveal).
# Photos: ./ddg_lock.sh env PYTHONPATH=. .venv/bin/python .claude/skills/football-shorts/scripts/whatif_photos.py prototypes/r2/photos KEY "q1" "q2"
#         then LOOK at the sheet, copy the pick to prototypes/r2/photos/<x>_src.jpg and set the crop box (aspect 510:560 for duel).
cd "${0:A:h}/../.." || exit 1
caffeinate -dimsu -w $$ &
.venv/bin/python gen_proto_r2.py "${1:-prototypes/r2/duel_dembele_yamal.json}" "${@:2}"
