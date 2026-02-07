#!/usr/bin/env python3
"""
Turn a W3SB newsletter into a two-speaker podcast using ElevenLabs Text-to-Dialogue.

Usage:
  python scripts/newsletter_to_podcast.py --url "https://paragraph.com/@w3sb/0x19-web3-security-bulletin"
  python scripts/newsletter_to_podcast.py --file final_newsletter_26-02-06.md
  python scripts/newsletter_to_podcast.py --script path/to/podcast_script.json

Use --script when you have a pre-generated dialogue script (e.g. from the newsletter-podcast-prep
skill): JSON array of {"speaker": "A"|"B", "text": "..."}. Optional [emotion] tags in text are supported.

Requires: ELEVENLABS_API_KEY in .env, podcast_config.yaml with speaker_a and speaker_b voice_id.
Output: MP3 file in podcast_output/ (or --output path).
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

# Load .env before other imports that might use it
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Suppress urllib3 OpenSSL/LibreSSL warning on some macOS Pythons
import warnings
try:
    from urllib3.exceptions import NotOpenSSLWarning
    warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
except ImportError:
    pass

import yaml

# Optional: for URL fetch
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None

# Eleven v3: limit is 5000 characters per REQUEST (total of all inputs), not per input
MAX_CHARS_PER_REQUEST = 5000
# Per-input cap when splitting long lines (each segment still under request budget)
MAX_CHARS_PER_INPUT = 5000
# Safe margin for dialogue lines (stay under limit after tags)
MAX_CHARS_PER_LINE = 4500
# Chunk script by this many inputs before applying request-size batching
INPUTS_PER_CHUNK = 100


def load_config(config_path: str) -> dict:
    path = Path(config_path)
    if not path.is_file():
        raise FileNotFoundError(f"Config not found: {config_path}")
    with open(path, "r") as f:
        return yaml.safe_load(f)


def fetch_newsletter_from_url(url: str) -> str:
    if not requests or not BeautifulSoup:
        raise RuntimeError("Install requests and beautifulsoup4 for --url: pip install requests beautifulsoup4")
    resp = requests.get(
        url,
        timeout=30,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    # Try common content containers (Paragraph and similar)
    main = (
        soup.find("main")
        or soup.find("article")
        or soup.find(attrs={"role": "article"})
        or soup.find(class_=re.compile(r"post|content|article", re.I))
    )
    if not main:
        main = soup.find("body")
    if not main:
        return resp.text
    # Emit # for all headings so parser accepts (Paragraph uses single # for sections)
    parts = []
    for el in main.find_all(["h1", "h2", "h3", "p", "strong"]):
        tag = el.name
        text = el.get_text(separator=" ", strip=True)
        if not text or len(text) < 2:
            continue
        if tag in ("h1", "h2", "h3"):
            parts.append(f"\n# {text}\n")
        elif tag == "strong" and len(text) > 10 and not text.startswith("http"):
            parts.append(f"**{text}**")
        elif tag == "p":
            parts.append(text)
    raw = "\n".join(parts)
    # Collect hrefs that look like article URLs (not paragraph.com nav)
    for a in main.find_all("a", href=True):
        href = a.get("href", "").strip()
        if href.startswith("http") and "paragraph.com" not in href and href not in raw:
            raw += f"\n`{href}`\n"
    return raw


def read_newsletter_from_file(file_path: str) -> str:
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Newsletter file not found: {file_path}")
    return path.read_text(encoding="utf-8", errors="replace")


def parse_newsletter(text: str) -> tuple[str, list[dict]]:
    """
    Parse markdown-style newsletter into title and list of sections with entries.
    Returns (newsletter_title, [ { "section": str, "entries": [ {"title": str, "summary": str, "url": str} ] } ]).
    Accepts both # and ## for section headers (Paragraph and other sources use single #).
    """
    title = "Web3 Security Bulletin"
    lines = text.split("\n")
    sections = []
    current_section = None
    current_entries = []
    i = 0
    section_order = [
        "Insightful",
        "Companies in the news",
        "Gimme the loot",
        "We must have regulations",
        "VCs & funding",
        "Research corner",
        "Etc",
    ]
    # Match both # and ## section headers
    section_pattern = re.compile(r"^#+\s+(.+)$")

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        section_match = section_pattern.match(stripped)
        if section_match:
            section_name = section_match.group(1).strip()
            # First section header that looks like a newsletter title (not a section name)
            if current_section is None and not sections and (
                "bulletin" in section_name.lower() or "newsletter" in section_name.lower() or "0x" in section_name
            ):
                title = section_name
                i += 1
                continue
            if current_section is not None and current_entries:
                sections.append({"section": current_section, "entries": current_entries})
            current_section = section_name
            current_entries = []
            i += 1
            continue

        # Entry: **Title** then paragraph(s) then optional `url`
        if stripped.startswith("**") and "**" in stripped[2:]:
            end = stripped.index("**", 2) + 2
            entry_title = stripped[2 : end - 2].strip()
            rest_of_line = stripped[end:].strip()
            summary_parts = [rest_of_line] if rest_of_line else []
            url = ""
            i += 1
            # Read following non-empty lines until we hit ** or # section or `url`
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    i += 1
                    continue
                if next_line.startswith("#"):
                    break
                if next_line.startswith("**"):
                    break
                if next_line.startswith("`") and "http" in next_line and next_line.endswith("`"):
                    url = next_line.strip("`").strip()
                    i += 1
                    break
                if next_line.startswith("http") and " " not in next_line:
                    url = next_line
                    i += 1
                    break
                # Extract URL from markdown link ( [text](url) )
                link_match = re.search(r"\[[^\]]*\]\s*\(\s*(https?://[^)]+)\s*\)", next_line)
                if link_match and not url:
                    url = link_match.group(1).strip()
                summary_parts.append(next_line)
                i += 1
            summary = " ".join(summary_parts).strip()
            if not url and i < len(lines):
                u = lines[i].strip().strip("`").strip()
                if u.startswith("http"):
                    url = u
                    i += 1
            current_entries.append({"title": entry_title, "summary": summary, "url": url})
            continue
        i += 1

    if current_section is not None and current_entries:
        sections.append({"section": current_section, "entries": current_entries})

    # Sort sections by standard order
    order_map = {s: idx for idx, s in enumerate(section_order)}
    sections.sort(key=lambda x: order_map.get(x["section"], 99))
    return title, sections


def generate_dialogue_script(
    title: str,
    parsed: list[dict],
    dialogue_style: str,
) -> list[dict]:
    """
    Generate alternating speaker A/B script with optional [emotion] tags.
    Returns list of {"speaker": "A"|"B", "text": "..."}.
    """
    style_tags = {
        "professional": ["[calmly]", "[thoughtfully]", "[matter-of-factly]"],
        "casual": ["[cheerfully]", "[wryly]", "[interested]"],
        "wry": ["[wryly]", "[dryly]", "[amused]"],
    }
    tags = style_tags.get(dialogue_style, style_tags["professional"])
    script = []
    speaker = "A"

    def add(line: str, tag: Optional[str] = None):
        nonlocal speaker
        if tag:
            text = f"{tag} {line}" if not line.startswith("[") else line
        else:
            text = line
        script.append({"speaker": speaker, "text": text.strip()})
        speaker = "B" if speaker == "A" else "A"

    # Intro
    add(f"Welcome to the {title}.", tags[0])
    add("Let's get into it.", tags[1])

    for block in parsed:
        section = block["section"]
        entries = block.get("entries", [])
        if not entries:
            continue
        add(f"First up, {section}.", tags[0])
        for idx, ent in enumerate(entries):
            title_ent = ent.get("title", "")
            summary = ent.get("summary", "")
            if not title_ent and not summary:
                continue
            # Keep each line under API limit (5000 chars per input)
            title_short = (title_ent[:MAX_CHARS_PER_LINE] + "…") if len(title_ent) > MAX_CHARS_PER_LINE else title_ent
            add(f"Here's one: {title_short}.", tags[0])
            summary_short = (summary[:400] + "…") if len(summary) > 400 else summary
            add(summary_short, tags[1])
            if idx < len(entries) - 1:
                add("What else?", tags[2] if len(tags) > 2 else tags[0])

    add("That's it for this week.", tags[0])
    add("See you next time.", tags[1])
    return script


def _split_long_text(text: str, max_chars: int) -> list[str]:
    """Split text into segments each <= max_chars (by sentence, then by character)."""
    if len(text) <= max_chars:
        return [text] if text else []
    out = []
    parts = re.split(r"(?<=[.!?])\s+", text)
    buf = ""
    for p in parts:
        if len(buf) + len(p) + 1 <= max_chars:
            buf += (" " if buf else "") + p
        else:
            if buf.strip():
                out.append(buf)
            buf = p if len(p) <= max_chars else ""
            while len(p) > max_chars:
                out.append(p[:max_chars])
                p = p[max_chars:].lstrip()
            if p:
                buf = (buf + " " + p).strip() if buf else p
    if buf:
        out.append(buf)
    return out


def chunk_script(script: list[dict], max_chars: int = MAX_CHARS_PER_INPUT) -> list[list[dict]]:
    """Split script so each text is <= max_chars; also split into API-sized chunks."""
    chunks = []
    current = []
    for line in script:
        text = line.get("text", "")
        speaker = line.get("speaker", "A")
        for segment in _split_long_text(text, max_chars):
            current.append({"speaker": speaker, "text": segment})
        if len(current) >= INPUTS_PER_CHUNK:
            chunks.append(current)
            current = []
    if current:
        chunks.append(current)
    return chunks if chunks else [[]]


def run_elevenlabs(
    script_chunks: list[list[dict]],
    config: dict,
    output_path: str,
) -> None:
    import httpx
    from elevenlabs.client import ElevenLabs

    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("Set ELEVENLABS_API_KEY in .env or the environment.")

    # Long timeout for connect and read (slow networks and TTS generation)
    timeout = httpx.Timeout(180.0)  # single default applies to connect, read, write, pool
    http_client = httpx.Client(timeout=timeout)
    client = ElevenLabs(api_key=api_key, httpx_client=http_client)
    voice_a = config["speaker_a"]["voice_id"]
    voice_b = config["speaker_b"]["voice_id"]

    def to_inputs(script: list[dict]):
        """Build API inputs; split any line still over limit (safety net)."""
        out = []
        for line in script:
            text = line["text"]
            voice_id = voice_a if line["speaker"] == "A" else voice_b
            for segment in _split_long_text(text, MAX_CHARS_PER_INPUT):
                out.append({"text": segment, "voice_id": voice_id})
        return out

    # Flatten script chunks and build all inputs
    all_inputs = []
    for chunk in script_chunks:
        if not chunk:
            continue
        all_inputs.extend(to_inputs(chunk))

    # API limit is total text per REQUEST (5000 chars). Batch inputs so each request stays under.
    request_batches = []
    current_batch = []
    current_len = 0
    for inp in all_inputs:
        n = len(inp["text"])
        if current_len + n > MAX_CHARS_PER_REQUEST and current_batch:
            request_batches.append(current_batch)
            current_batch = []
            current_len = 0
        current_batch.append(inp)
        current_len += n
    if current_batch:
        request_batches.append(current_batch)

    audio_chunks = []
    max_retries = 3
    retry_delay = 15
    for inputs in request_batches:
        for attempt in range(max_retries):
            try:
                audio = client.text_to_dialogue.convert(
                    inputs=inputs,
                    output_format="mp3_44100_128",
                )
                break
            except Exception as e:
                is_connect_error = "ConnectError" in type(e).__name__ or "timed out" in str(e).lower()
                if attempt < max_retries - 1:
                    import time
                    print(f"  Request failed ({e!r}), retrying in {retry_delay}s...", file=sys.stderr)
                    time.sleep(retry_delay)
                else:
                    if is_connect_error:
                        raise RuntimeError(
                            "Connection to ElevenLabs API timed out or was refused. "
                            "Check your network, VPN, and firewall; then try again."
                        ) from e
                    raise
        # SDK may return bytes or an iterable of bytes (stream)
        if isinstance(audio, (bytes, bytearray)):
            audio_chunks.append(bytes(audio))
        elif hasattr(audio, "__iter__"):
            audio_chunks.append(b"".join(audio))
        else:
            audio_chunks.append(bytes(audio))

    if len(audio_chunks) == 1:
        out_bytes = audio_chunks[0]
    else:
        try:
            from pydub import AudioSegment
            combined = None
            for chunk_bytes in audio_chunks:
                import io
                seg = AudioSegment.from_mp3(io.BytesIO(chunk_bytes))
                combined = seg if combined is None else combined + seg
            buf = io.BytesIO()
            combined.export(buf, format="mp3")
            out_bytes = buf.getvalue()
        except ImportError:
            out_bytes = b"".join(audio_chunks)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(out_bytes)
    size = len(out_bytes)
    print(f"Saved: {output_path} ({size:,} bytes)")


def load_script_from_file(script_path: str) -> list[dict]:
    """Load a pre-generated dialogue script from JSON. Expects list of {speaker, text}."""
    path = Path(script_path)
    if not path.is_file():
        raise FileNotFoundError(f"Script file not found: {script_path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Script JSON must be a list of {speaker, text} objects")
    for i, item in enumerate(data):
        if not isinstance(item, dict) or "speaker" not in item or "text" not in item:
            raise ValueError(f"Script item {i}: must have 'speaker' and 'text' keys")
        if item["speaker"] not in ("A", "B"):
            raise ValueError(f"Script item {i}: speaker must be 'A' or 'B', got {item['speaker']!r}")
    return data


def main():
    parser = argparse.ArgumentParser(description="Turn newsletter into a two-speaker podcast (ElevenLabs).")
    parser.add_argument("--url", type=str, help="Paragraph URL of the newsletter")
    parser.add_argument("--file", type=str, help="Path to newsletter markdown file")
    parser.add_argument(
        "--script",
        type=str,
        help="Path to pre-generated dialogue script JSON (from newsletter-podcast-prep skill)",
    )
    parser.add_argument("--config", type=str, default="podcast_config.yaml", help="Path to podcast config YAML")
    parser.add_argument("--output", type=str, default=None, help="Output MP3 path (default: podcast_output/podcast_<slug>.mp3)")
    parser.add_argument("--output-dir", type=str, default="podcast_output", help="Output directory if --output not set")
    args = parser.parse_args()

    sources = sum([bool(args.url), bool(args.file), bool(args.script)])
    if sources == 0:
        parser.error("Provide exactly one of --url, --file, or --script")
    if sources > 1:
        parser.error("Provide only one of --url, --file, or --script")

    project_root = Path(__file__).resolve().parent.parent
    os.chdir(project_root)

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = project_root / config_path
    config = load_config(str(config_path))
    if "speaker_a" not in config or "speaker_b" not in config:
        print("podcast_config.yaml must define speaker_a and speaker_b with voice_id.", file=sys.stderr)
        sys.exit(1)

    if args.script:
        script_path = Path(args.script)
        if not script_path.is_absolute():
            script_path = project_root / script_path
        try:
            script = load_script_from_file(str(script_path))
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        chunks = chunk_script(script)
        slug = script_path.stem
        if not slug or slug == "podcast_script":
            slug = "prepared_podcast"
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", slug)[:40].strip("_") or "prepared_podcast"
    else:
        dialogue_style = config.get("dialogue_style", "professional")
        if args.url:
            raw = fetch_newsletter_from_url(args.url)
        else:
            file_path = Path(args.file)
            if not file_path.is_absolute():
                file_path = project_root / file_path
            raw = read_newsletter_from_file(str(file_path))

        title, parsed = parse_newsletter(raw)
        if not parsed:
            print("No sections/entries parsed from newsletter.", file=sys.stderr)
            print("Expected format: # or ## Section, then **Title**, summary paragraph, and optional URL.", file=sys.stderr)
            if args.url:
                print("Many sites (e.g. Paragraph) are client-rendered; requests may not get the article body.", file=sys.stderr)
                print("Workaround: save the newsletter as markdown (e.g. copy from the page) to a file and run with --file.", file=sys.stderr)
            sys.exit(1)

        script = generate_dialogue_script(title, parsed, dialogue_style)
        chunks = chunk_script(script)
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", title)[:40].strip("_") or "podcast"

    if args.output:
        output_path = args.output
    else:
        Path(args.output_dir).mkdir(parents=True, exist_ok=True)
        output_path = str(Path(args.output_dir) / f"podcast_{slug}.mp3")

    run_elevenlabs(chunks, config, output_path)


if __name__ == "__main__":
    main()
