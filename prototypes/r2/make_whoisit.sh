#!/bin/zsh
# Build one 'WHO IS IT?' blur-to-clear Short from a JSON spec (default: Haaland).
#   prototypes/r2/make_whoisit.sh [spec.json] [--no-render]
# New player = copy whoisit_haaland.json, change: key/out, photos.photo (src + 9:16 crop box, e.g. [x0,0,x0+h*0.5625,h]),
# shiftY (push face below the header), clues (3 short on-screen lines), segments (clue0, clue1, clue2, reveal voice lines),
# name, fact (one verified line), source. Every clue and the fact must be fetched from a source page first.
cd "${0:A:h}/../.." || exit 1
caffeinate -dimsu -w $$ &
.venv/bin/python gen_proto_r2.py "${1:-prototypes/r2/whoisit_haaland.json}" "${@:2}"
