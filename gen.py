#!/usr/bin/env python3
"""Render clips.json to MP3 with ElevenLabs (eleven_v4).

Usage: gen.py [--clips FILE] [--dry-run] [--only NAME ...]
Output goes to generated/ for clips.json, generated-<stem>/ for any other file.
Key comes from the Keychain item ELEVENLABS_API_KEY (same as the Toolbelt
elevenlabs tool). Every paid call appends one line to the agent-voice audit log.
"""
import argparse
import datetime
import json
import os
import pathlib
import subprocess
import sys
import urllib.error
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "generated"
MODEL = "eleven_v4"
# Matches the factory files on the card: mono, 44.1 kHz, 128 kbps CBR.
FORMAT = "mp3_44100_128"
MAX_TOTAL_CHARS = 2000
AUDIT = pathlib.Path(os.environ.get(
    "AGENT_VOICE_AUDIT_LOG", "~/.local/state/agent-voice/audit.log")).expanduser()


def api_key():
    return subprocess.run(
        ["security", "find-generic-password", "-s", "ELEVENLABS_API_KEY", "-w"],
        check=True, capture_output=True, text=True).stdout.strip()


def audit(voice, chars, name):
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds")
    line = f"[agent-voice audit] {ts.replace('+00:00', 'Z')} verb=pumpkin-gen agent={name} voice={voice} model={MODEL} chars={chars}"
    print(line, file=sys.stderr)
    AUDIT.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with open(AUDIT, "a") as f:
        f.write(line + "\n")
    os.chmod(AUDIT, 0o600)


def render(key, clip):
    body = json.dumps({
        "text": clip["text"],
        "model_id": MODEL,
        "voice_settings": {"stability": 0.3, "similarity_boost": 0.75},
    }).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{clip['voice']}?output_format={FORMAT}",
        data=body, method="POST",
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--clips", default="clips.json")
    args = ap.parse_args()

    clips_file = HERE / args.clips
    clips = json.loads(clips_file.read_text())
    out = OUT if clips_file.stem == "clips" else HERE / f"generated-{clips_file.stem}"
    if args.only:
        clips = [c for c in clips if c["name"] in args.only]
    total = sum(len(c["text"]) for c in clips)
    for c in clips:
        print(f"{c['name']:18} {c['voice_name']:28} {len(c['text']):4} chars  {c['text']}")
    print(f"total {total} chars, model {MODEL}, format {FORMAT}")
    if total > MAX_TOTAL_CHARS:
        sys.exit(f"refusing: {total} chars exceeds MAX_TOTAL_CHARS={MAX_TOTAL_CHARS}")
    if args.dry_run:
        return

    key = api_key()
    out.mkdir(exist_ok=True)
    for c in clips:
        try:
            audio = render(key, c)
        except urllib.error.HTTPError as e:
            print(f"FAIL {c['name']}: HTTP {e.code} {e.read().decode(errors='replace')[:300]}", file=sys.stderr)
            continue
        audit(c["voice"], len(c["text"]), c["name"])
        path = out / f"{c['name']}.mp3"
        path.write_bytes(audio)
        print(f"wrote {path.relative_to(HERE)} ({len(audio)} bytes)")


if __name__ == "__main__":
    main()
