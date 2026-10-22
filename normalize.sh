#!/usr/bin/env bash
# Normalize clips for the M13's 1W speaker: highpass, light compression,
# two-pass loudnorm to -14 LUFS / -1 dBTP, then a -1.5 dB brick-wall limiter so the MP3 encode stays under 0 dBTP, mono 44.1k 128k CBR (factory format).
# Usage: normalize.sh SRC_DIR OUT_DIR
set -euo pipefail
src=$1; out=$2; mkdir -p "$out"
pre="highpass=f=120,acompressor=threshold=-24dB:ratio=3:attack=5:release=120:makeup=2"
tgt="I=-14:TP=-1:LRA=7"
for f in "$src"/*.mp3; do
  m=$(ffmpeg -hide_banner -nostats -i "$f" -af "$pre,loudnorm=$tgt:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
  get() { echo "$m" | awk -F'"' -v k="$1" '$2==k{print $4}'; }
  ffmpeg -hide_banner -loglevel error -y -i "$f" \
    -af "$pre,loudnorm=$tgt:measured_I=$(get input_i):measured_TP=$(get input_tp):measured_LRA=$(get input_lra):measured_thresh=$(get input_thresh):offset=$(get target_offset):linear=true,aresample=44100,alimiter=limit=0.84:level=false" \
    -ac 1 -c:a libmp3lame -b:a 128k -id3v2_version 0 "$out/$(basename "$f")"
done
