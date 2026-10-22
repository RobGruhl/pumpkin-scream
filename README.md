# pumpkin-scream

AI-meme Halloween scares for a Waytronic MicroSound M13 (WT-M13) motion-activated speaker. Monster voices from the ElevenLabs voice library, rendered with `eleven_v4` audio tags, loudness-normalized for a 1 W speaker, and laid out on the micro SD card so the chip plays them in a fixed order.

> "As a large language monster, I cannot eat you... without your consent."

## What's here

| Path | What |
|---|---|
| `clips.json` → `generated/` | First test batch: 10 lines in stock ElevenLabs voices. Superseded by the monster voices; kept for comparison. |
| `clips-monsters.json` → `generated-clips-monsters/` | Batch 1 in monster voices (40): 35 AI-meme lines plus 5 plain Halloween lines (`trickster-boo`, `who-dares`, `scared-pumpkin`, `trick-or-treat`, `old-man-candy`). |
| `shortlist-dev.json`, `shortlist-ai2.json` | Batch 2 shortlists: 24 developer-meme and 24 AI-meme lines, each picked from ~56 candidates by four theme writers, a comedy judge and a porch/voice judge. |
| `clips-batch2.json` → `generated-clips-batch2/` | Batch 2 rendered (48), both shortlists merged with ElevenLabs voice ids. |
| `generated-*/` | Raw `eleven_v4` output, mono 44.1 kHz 128 kbps, uneven loudness. Source of truth for re-processing. |
| `normalized/` | Every monster-voice clip (88) after `normalize.sh`: 120 Hz high-pass, light compression, -14 LUFS, -1.5 dB limiter. These are what go on cards. |
| `card-order.txt` | Play order for the current 35-clip card (no voice plays twice in a row, including the wrap). |
| `card-128/`, `card-96/` | That 35-clip card set in play order, at 128 and 96 kbps (`NNN-name.mp3`). `card-128` is what's on the cards. |
| `card-map.txt` | `NNN.MP3` on the card → clip name, written by `write-card.sh`. |
| `card-81-1/` … `card-81-5/` (+ `-order.txt`) | Five card sets of the 81-clip pool (35 batch 1 + 46 batch 2; the two Whisper-garbled clips dropped), each a different baked shuffle, one per speaker so neighbours don't play in step. |
| `card-shuffle/` (+ `-order.txt`) | The same 81 clips as three back-to-back shuffled rounds (243 files) for a longer loop. |
| `transcripts-batch2.tsv` | Local Whisper transcript of each batch-2 clip, used to check no audio tag was read aloud (none were). |
| `MANUAL.md` | Notes from the M13 manual: buttons, modes, update procedure, timing. |

## Scripts

- `gen.py [--clips FILE] [--only NAME ...] [--dry-run]` renders clips via the ElevenLabs API. The key comes from the macOS Keychain item `ELEVENLABS_API_KEY`; every paid call appends a line to `~/.local/state/agent-voice/audit.log`. A per-run ceiling of 2000 characters is in code.
- `make-shuffle.py [--rounds N] [--seed S] [--min-gap G] [--out NAME]` bakes a shuffle into a card set, since the M13 can only loop in order (the chip's random mode is reachable only over its UART). Every round is a fresh permutation; across the loop, including the wrap, no voice plays twice in a row, no set plays three in a row, and no clip repeats within `--min-gap` plays (default 30).
- `normalize.sh SRC OUT` high-passes at 120 Hz, lightly compresses, two-pass `loudnorm` to -14 LUFS, then a -1.5 dB brick-wall limiter.
- `write-card.sh /dev/diskN SRC > card-map.txt` erases a removable USB/SD card (refuses disk images and anything over 4 GB) as MBR + FAT16 like the factory card, and copies files as 8.3 names `001.MP3`… one at a time, so FAT directory order, name order and play order all match (the WT2003B indexes tracks by write order). It resolves the card's real mount point from `diskutil` rather than assuming `/Volumes/PUMPKIN`, removes the `._` AppleDouble files macOS creates even with `cp -X`, and finishes by verifying order, count and checksums on the card.

## Loading the M13

**Play from the card (confirmed on hardware, 2026-10-22).** With a card in the slot the M13 plays straight from it, so the 4 MB flash limit doesn't apply: an 81-clip, 9.2 MB `card-81-N` set plays fine. Insert the card with the power off, switch on, wait ~20 s, and leave the card in. Do **not** hold B with a card over 4 MB: that starts the copy into flash, which Waytronic says transfers nothing when the audio exceeds 4 MB.

**Copy into flash (≤ 4 MB only).** For a set that fits (the 35 clips in `card-128/` are 3.5 MB): insert the card, hold **B**, switch power on, release when the red LED flashes; the copy is done when the LED goes off. The card can then be removed.

The M13 loops in file order (long-press **A** toggles loop-all, 1 flash, and single-track, 2 flashes); it has no shuffle, hence `make-shuffle.py`. Only insert or remove a card with the power off.

If macOS says a card is "not readable" (blank, e.g. after an interrupted erase), click **Ignore** and run `write-card.sh`. If `diskutil eraseDisk` stalls for more than a few seconds, the card or reader has hung: stop it, reseat the card, and try again.

Factory sounds are not included in this repo (they're Waytronic's).
