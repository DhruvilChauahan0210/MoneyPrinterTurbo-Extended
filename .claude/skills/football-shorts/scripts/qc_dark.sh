#!/bin/zsh
# Flag black / near-black stretches in a finished Short (a dark stadium shot or a bad clip start reads as a glitch).
# Usage: qc_dark.sh video.mp4      -> prints each stretch >= 0.15 s, or "no dark frames"
export PATH="$HOME/Developer/CDH/MoneyPrinterTurbo-Extended/.venv/bin:$PATH"
out=$(ffmpeg -hide_banner -nostats -i "$1" -vf "blackdetect=d=0.15:pix_th=0.12" -an -f null - 2>&1 | grep -o "black_start:[0-9.]* black_end:[0-9.]* black_duration:[0-9.]*")
[[ -z $out ]] && echo "no dark frames" || echo "$out"
