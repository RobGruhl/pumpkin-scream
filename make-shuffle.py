#!/usr/bin/env python3
"""Bake a shuffle into a card set, since the M13 only plays in order.

Usage: make-shuffle.py [--rounds N] [--seed S] [--min-gap G] [--out NAME]
Writes NAME-order.txt (one clip name per line) and NAME/ (NNN-name.mp3
copies of normalized/ clips) ready for write-card.sh. NAME defaults to
card-shuffle.

Each round is a fresh permutation of every clip. Across the whole loop,
including the wrap from the last file back to the first:
  - the same voice never plays twice in a row,
  - the same set (AI batch 1 / developer / AI batch 2) never plays 3 in a row,
  - a clip never repeats within --min-gap plays.
"""
import argparse
import json
import pathlib
import random
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
DROP = {"squashed-precious-commits", "standup-blocker-is-you"}  # garbled per Whisper


def load_clips():
    voice = {}
    group = {}
    for c in json.loads((HERE / "clips-monsters.json").read_text()):
        voice[c["name"]] = c["voice"]
        group[c["name"]] = "ai1"
    for c in json.loads((HERE / "clips-batch2.json").read_text()):
        voice[c["name"]] = c["voice"]
        group[c["name"]] = c["set"]
    names = (HERE / "card-order.txt").read_text().split()  # the 35 already on cards
    names += [c["name"] for c in json.loads((HERE / "clips-batch2.json").read_text())]
    names = [n for n in names if n not in DROP]
    return names, voice, group


def ok(seq, name, voice, group, min_gap, total):
    if seq and voice[seq[-1]] == voice[name]:
        return False
    if len(seq) >= 2 and group[seq[-1]] == group[seq[-2]] == group[name]:
        return False
    if name in seq[-min_gap:]:
        return False
    # Near the end, the loop wraps back to the start: apply the same rules
    # against the first files, which play right after the last ones.
    ahead = len(seq) + min_gap - total
    if ahead > 0 and name in seq[:ahead]:
        return False
    if len(seq) == total - 1:
        if voice[name] == voice[seq[0]]:
            return False
        if group[seq[-1]] == group[name] == group[seq[0]]:
            return False
        if group[name] == group[seq[0]] == group[seq[1]]:
            return False
    return True


def build(names, voice, group, rounds, min_gap, rng):
    seq = []
    total = rounds * len(names)
    for _ in range(rounds):
        pool = names[:]
        rng.shuffle(pool)
        while pool:
            choices = [n for n in pool if ok(seq, n, voice, group, min_gap, total)]
            if not choices:
                return None
            # Favour voices and sets with the most clips left in this round,
            # so busy voices (Dante, Azazel) are spread out instead of piling
            # up at the end of the round where they would have to play back to back.
            vleft = {}
            gleft = {}
            for n in pool:
                vleft[voice[n]] = vleft.get(voice[n], 0) + 1
                gleft[group[n]] = gleft.get(group[n], 0) + 1
            weights = [vleft[voice[n]] ** 2 * gleft[group[n]] for n in choices]
            pick = rng.choices(choices, weights)[0]
            seq.append(pick)
            pool.remove(pick)
    return seq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--seed", type=int, default=31)
    ap.add_argument("--min-gap", type=int, default=30)
    ap.add_argument("--out", default="card-shuffle")
    args = ap.parse_args()

    names, voice, group = load_clips()
    missing = [n for n in names if not (HERE / "normalized" / f"{n}.mp3").exists()]
    if missing:
        sys.exit(f"missing normalized clips: {missing}")
    rng = random.Random(args.seed)
    for attempt in range(1, 5001):
        seq = build(names, voice, group, args.rounds, args.min_gap, rng)
        if seq:
            break
    else:
        sys.exit("no arrangement found; lower --min-gap")

    (HERE / f"{args.out}-order.txt").write_text("\n".join(seq) + "\n")
    out = HERE / args.out
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir()
    for i, n in enumerate(seq, 1):
        shutil.copyfile(HERE / "normalized" / f"{n}.mp3", out / f"{i:03d}-{n}.mp3")
    size = sum(p.stat().st_size for p in out.iterdir())
    print(f"{len(names)} clips x {args.rounds} rounds = {len(seq)} files, "
          f"{size / 1048576:.1f} MB, seed {args.seed}, attempt {attempt}")


if __name__ == "__main__":
    main()
