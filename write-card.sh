#!/usr/bin/env bash
# Erase the M13's micro SD and copy a card set onto it in play order.
# Usage: write-card.sh /dev/diskN SRC_DIR > card-map.txt   (stdout = NNN.MP3 -> source map)
# Same layout as the factory card (MBR + FAT16). Copies one file at a time
# with cp -X (no ._ AppleDouble files) as 8.3 names (001.MP3, 002.MP3, ...):
# a short name takes exactly one FAT directory slot, so files fill the root
# directory strictly in order (long names need several slots and get placed
# into earlier holes). Directory order = name order = play order.
set -euo pipefail
disk=$1; src=$2; label=PUMPKIN; vol=/Volumes/$label

info=$(diskutil info "$disk")
grep -q 'Removable Media: *Removable' <<<"$info" || { echo "refusing: $disk is not removable" >&2; exit 2; }
bytes=$(awk -F'[()]' '/Disk Size/{print $2}' <<<"$info" | awk '{print $1}')
(( bytes < 4000000000 )) || { echo "refusing: $disk is larger than 4GB" >&2; exit 2; }

diskutil eraseDisk "MS-DOS FAT16" "$label" MBRFormat "$disk" >&2
mdutil -i off "$vol" >/dev/null 2>&1 || true
rm -rf "$vol/.Spotlight-V100" "$vol/.fseventsd" "$vol/.Trashes"

n=0
for f in $(cd "$src" && ls *.mp3 | sort); do
  n=$((n + 1))
  dst=$(printf '%03d.MP3' "$n")
  cp -X "$src/$f" "$vol/$dst"
  echo "$dst  $f"
  sync
done
# Created last so its directory entries land after the audio files.
touch "$vol/.metadata_never_index"
dot_clean -m "$vol"
rm -f "$vol"/._*
sync
