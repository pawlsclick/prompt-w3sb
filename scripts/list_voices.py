#!/usr/bin/env python3
"""
List ElevenLabs voices (name and voice_id) for use in podcast_config.yaml.
Requires ELEVENLABS_API_KEY in the environment or .env.
"""
import json
import os
import sys
import urllib.request

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def main():
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("Set ELEVENLABS_API_KEY in .env or the environment.", file=sys.stderr)
        sys.exit(1)

    url = "https://api.elevenlabs.io/v1/voices?page_size=100"
    req = urllib.request.Request(url, headers={"xi-api-key": api_key})
    try:
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"API error: {e.code} {e.reason}", file=sys.stderr)
        if e.code == 401:
            print("Check that ELEVENLABS_API_KEY is correct.", file=sys.stderr)
        sys.exit(1)

    voices = data.get("voices", [])
    if not voices:
        print("No voices returned.")
        return

    print("voice_id (use in podcast_config.yaml)")
    print("-" * 50)
    for v in voices:
        name = v.get("name", "?")
        voice_id = v.get("voice_id") or v.get("id", "?")
        print(f"  {voice_id}  {name}")
    print("\nCopy two voice_id values into podcast_config.yaml (speaker_a.voice_id and speaker_b.voice_id).")


if __name__ == "__main__":
    main()
