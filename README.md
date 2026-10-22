# pumpkin-scream

AI-meme Halloween scares for a Waytronic MicroSound M13 (WT-M13) motion-activated speaker. Monster voices from the ElevenLabs voice library, rendered with `eleven_v4` audio tags, loudness-normalized for a 1 W speaker, and laid out on the micro SD card so the chip plays them in a fixed order.

> "As a large language monster, I cannot eat you... without your consent."

## What's here

| Path | What |
|---|---|
| `clips.json`, `generated/` | First test batch (stock ElevenLabs voices) |
| `clips-monsters.json`, `generated-clips-monsters/` | Monster-voice clips (40), the source set |
| `normalized/` | Same clips after `normalize.sh` (-14 LUFS, limited, mono 44.1 kHz 128 kbps) |
| `card-order.txt` | Play order for the 35 AI-meme clips (no voice plays twice in a row, including the wrap) |
| `card-128/`, `card-96/` | The 35 clips in play order at 128 and 96 kbps |
| `card-map.txt` | `NNN.MP3` on the card → clip name |
| `MANUAL.md` | Notes from the M13 manual (buttons, modes, update procedure) |

## Scripts

- `gen.py [--clips FILE] [--only NAME ...] [--dry-run]` renders clips via the ElevenLabs API. The key comes from the macOS Keychain item `ELEVENLABS_API_KEY`; every paid call appends a line to `~/.local/state/agent-voice/audit.log`. A per-run ceiling of 2000 characters is in code.
- `normalize.sh SRC OUT` high-passes at 120 Hz, lightly compresses, two-pass `loudnorm` to -14 LUFS, then a -1.5 dB brick-wall limiter.
- `write-card.sh /dev/diskN SRC > card-map.txt` erases a removable card (refuses anything not removable or over 4 GB) as MBR + FAT16 like the factory card, and copies files as 8.3 names `001.MP3`… one at a time with `cp -X`, so FAT directory order, name order and play order all match and no `._` AppleDouble files reach the card.

## Loading the M13

The WT-M13 has 4 MB of internal flash; the 35 clips at 128 kbps are 3.5 MB. Insert the card, hold **B**, switch power on, release when the red LED flashes; the copy is done when the LED goes off. Wait ~20 s after power-on before it triggers. Long-press **A** to toggle loop-all (1 flash) and single-track (2 flashes).

Factory sounds are not included in this repo (they're Waytronic's).
