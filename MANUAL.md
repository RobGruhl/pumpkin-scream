# Waytronic MicroSound M13 (WT-M13) — manual notes

Chip: WT2003B03. Internal flash 32Mbit (4MB). MP3 only, 8–320 kbps. 8Ω/1W speaker, PIR ≤4 m / 120°. Power 3×AAA or micro-USB 5V (never both — remove batteries before plugging in).

## Controls
- Slide switch: bottom = off, middle = quiet, top = max.
- LED: on while playing; 8 quick flashes after playback = low battery; 3 quick flashes = battery dead.
- A short = previous track; A long = toggle mode (1 flash = A mode, loop through all; 2 flashes = B mode, repeat one track).
- B short = next track; B long = copy mode (SD → flash).
- Buttons only work while audio is playing. In B mode, press A/B during playback to pick the trigger track.

## Timing
- ~20 s warm-up after power-on.
- 2 s lockout after each trigger; leaving and re-entering the field gives a cleaner re-trigger.

## Update voice files
**Method 1 (SD → flash):** format microSD (<8GB) FAT32, copy MP3s to root. Insert card, hold B, switch power on, release when red LED flashes. Copying runs until the LED goes off. Total must be ≤4MB.

**Method 2 (play from card):** card in slot + micro-USB to computer → shows as a drive; format FAT32, copy MP3s, disconnect, power on. It plays TF content first.

After copying it may play one clip; it may also lock up (no PIR response) — power-cycle. A long copy usually means it is repairing flash from an earlier interrupted copy.

## Install
Side wall ~1.5 m high, ~1 m from door frame, angled 45° toward the door; or above the door at ~2 m.

## FAQ
- Playback cuts out mid-clip and loops: low/unstable power, replace batteries.
- WAV unsupported: convert to MP3.

Factory card: 14 MP3s, mono 44.1 kHz 128 kbps CBR, names like `001 xxx.mp3`. Backed up in `factory-sounds/`.
