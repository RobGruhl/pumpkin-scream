#!/usr/bin/env bash
# Erase the M13's micro SD and copy a card set onto it in play order.
# Usage: write-card.sh /dev/diskN SRC_DIR > card-map.txt   (stdout = NNN.MP3 -> source map)
# Same layout as the factory card (MBR + FAT16). Copies one file at a time as
# 8.3 names (001.MP3, 002.MP3, ...): a short name takes exactly one FAT
# directory slot, so files fill the root directory strictly in order (long
# names need several slots and get placed into earlier holes). Directory
# order = name order = play order; the WT2003B indexes tracks by write order.
# macOS still writes ._ AppleDouble companions (com.apple.provenance) even
# with cp -X, so they are removed after copying and the result is verified.
set -euo pipefail
disk=$1; src=$2; label=PUMPKIN

info=$(diskutil info "$disk")
grep -q 'Removable Media: *Removable' <<<"$info" || { echo "refusing: $disk is not removable" >&2; exit 2; }
grep -Eq 'Protocol: *(USB|Secure Digital)' <<<"$info" || { echo "refusing: $disk is not a USB/SD device (disk image?)" >&2; exit 2; }
bytes=$(awk -F'[()]' '/Disk Size/{print $2}' <<<"$info" | awk '{print $1}')
(( bytes < 4000000000 )) || { echo "refusing: $disk is larger than 4GB" >&2; exit 2; }

diskutil eraseDisk "MS-DOS FAT16" "$label" MBRFormat "$disk" >&2
# Ask diskutil where this device mounted; another volume may already own
# /Volumes/$label, in which case the card lands at "/Volumes/$label 1".
vol=$(diskutil info "${disk}s1" | sed -n 's/^ *Mount Point: *//p')
[[ -n "$vol" && -d "$vol" ]] || { echo "error: ${disk}s1 is not mounted" >&2; exit 1; }
echo "writing to $vol (${disk}s1)" >&2
mdutil -i off "$vol" >/dev/null 2>&1 || true
rm -rf "$vol/.Spotlight-V100" "$vol/.fseventsd" "$vol/.Trashes"

files=$(cd "$src" && ls *.mp3 | sort)
n=0
for f in $files; do
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

# Verify against the same mount point, re-resolved from the device.
[[ "$(diskutil info "${disk}s1" | sed -n 's/^ *Mount Point: *//p')" == "$vol" ]] || { echo "verify: mount point moved" >&2; exit 1; }
on_card=$(ls -f "$vol" | grep -i '\.mp3$' || true)
[[ "$on_card" == "$(sort <<<"$on_card")" ]] || { echo "verify: directory order != name order" >&2; exit 1; }
(( $(grep -c . <<<"$on_card") == n )) || { echo "verify: expected $n MP3s on card" >&2; exit 1; }
[[ -z "$(find "$vol" -name '._*')" ]] || { echo "verify: ._ files remain" >&2; exit 1; }
n=0
for f in $files; do
  n=$((n + 1))
  cmp -s "$src/$f" "$vol/$(printf '%03d.MP3' "$n")" || { echo "verify: $f differs on card" >&2; exit 1; }
done
echo "verified: $n files, in order, byte-identical, no ._ files on ${disk}s1" >&2
