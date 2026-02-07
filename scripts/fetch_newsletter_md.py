#!/usr/bin/env python3
"""
Fetch live Paragraph newsletters via Firecrawl and save as markdown to live_sync_newsletter/.

Usage:
  python scripts/fetch_newsletter_md.py "https://paragraph.com/@w3sb/0x19-web3-security-bulletin"
  python scripts/fetch_newsletter_md.py --out-dir ./out url1 url2
  python scripts/fetch_newsletter_md.py --no-validate "https://paragraph.com/@w3sb/0x18-web3-security-bulletin"

Requires: FIRECRAWL_API_KEY in environment (or .env). Output: one .md file per URL in
live_sync_newsletter/ (or --out-dir). Validation runs by default (section/summary count);
use --no-validate to skip. Exits non-zero on fetch failure or validation mismatch.
"""
# Suppress urllib3/SSL warning before any imports that pull in urllib3 (e.g. firecrawl)
import warnings
warnings.filterwarnings("ignore", message=".*OpenSSL.*", category=UserWarning)
warnings.filterwarnings("ignore", module="urllib3")

import argparse
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

# Load .env from project root (so it's found even when run from another cwd)
try:
    from dotenv import load_dotenv
    _project_root = Path(__file__).resolve().parent.parent
    load_dotenv(_project_root / ".env")
except ImportError:
    pass

# Firecrawl (firecrawl-py): may expose Firecrawl or FirecrawlApp
try:
    from firecrawl import Firecrawl
except ImportError:
    Firecrawl = None
try:
    from firecrawl import FirecrawlApp
except ImportError:
    FirecrawlApp = None

# Section order aligned with newsletter_to_podcast.parse_newsletter
KNOWN_SECTIONS = [
    "Insightful",
    "Companies in the news",
    "Gimme the loot",
    "We must have regulations",
    "VCs & funding",
    "Research corner",
    "Etc",
]

# Blocklist: lines or patterns that indicate trailing junk to strip
TRAILING_JUNK = [
    "Subscribe to W3SB",
    "More from W3SB",
    "Checking your Browser",
    "Verifying...",
    "Stuck here?",
    "Success!",
    "Error",
    "Having trouble?",
    "Expired.",
    "Refresh",
    "Privacy",
    "Terms",
    "Wallet · Privy",
    "No comments yet",
    "Login to comment",
]

SECTION_HEADER_RE = re.compile(r"^#+\s+(.+)$")


def slug_from_url(url: str) -> str:
    """Extract a filesystem-safe slug from the last path segment of URL."""
    parsed = urlparse(url)
    path = (parsed.path or "").strip().rstrip("/")
    segment = path.split("/")[-1] if path else "newsletter"
    # Sanitize: allow only a-z, 0-9, hyphen, underscore
    safe = re.sub(r"[^a-z0-9\-_]", "-", segment.lower())
    safe = re.sub(r"-+", "-", safe).strip("-")
    return safe or "newsletter"


def fetch_with_firecrawl(url: str) -> str:
    """Fetch URL with Firecrawl; return markdown. On failure print error and exit non-zero."""
    if not Firecrawl and not FirecrawlApp:
        print("Error: firecrawl-py is not installed. Install with: pip install firecrawl-py", file=sys.stderr)
        sys.exit(1)
    api_key = os.environ.get("FIRECRAWL_API_KEY", "").strip()
    if not api_key:
        print("Error: FIRECRAWL_API_KEY is not set. Set it in the environment or .env.", file=sys.stderr)
        sys.exit(1)
    firecrawl_client = None
    try:
        if Firecrawl:
            firecrawl_client = Firecrawl(api_key=api_key)
            if hasattr(firecrawl_client, "scrape"):
                result = firecrawl_client.scrape(url, formats=["markdown"], only_main_content=True)
            else:
                result = firecrawl_client.scrape_url(url, params={"formats": ["markdown"], "onlyMainContent": True})
        else:
            app = FirecrawlApp(api_key=api_key)
            result = app.scrape_url(url, params={"formats": ["markdown"], "onlyMainContent": True})
    except Exception as e:
        err = str(e).lower()
        print(f"Error: Firecrawl fetch failed for {url}: {e}", file=sys.stderr)
        if "unauthorized" in err or "invalid token" in err:
            print(
                "Hint: Check FIRECRAWL_API_KEY in your .env or environment. "
                "The key may be missing, wrong, or expired. Get a key at https://firecrawl.dev",
                file=sys.stderr,
            )
        sys.exit(1)

    if result is None:
        print(f"Error: Firecrawl returned no data for {url}.", file=sys.stderr)
        sys.exit(1)

    # Extract markdown from various response shapes (SDK may return dict or object)
    markdown = None
    if isinstance(result, dict):
        data = result.get("data", result)
        if isinstance(data, dict):
            markdown = data.get("markdown")
        if not markdown:
            markdown = result.get("markdown")
    else:
        markdown = getattr(result, "markdown", None)
        if not markdown:
            d = getattr(result, "data", None)
            if d is not None:
                markdown = getattr(d, "markdown", None) if not isinstance(d, dict) else d.get("markdown")

    job_id = (result.get("id") if isinstance(result, dict) else getattr(result, "id", None))

    # If API returned a job id (async), poll until we have markdown
    if (not markdown or not isinstance(markdown, str)) and job_id and firecrawl_client:
        poll_interval = 2
        timeout = 90
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            time.sleep(poll_interval)
            try:
                status = firecrawl_client.get_batch_scrape_status(job_id)
            except Exception:
                continue
            st = status if isinstance(status, dict) else getattr(status, "__dict__", None) or {}
            data_list = st.get("data", [])
            if data_list:
                first = data_list[0]
                md = first.get("markdown") if isinstance(first, dict) else getattr(first, "markdown", None)
                if md:
                    markdown = md
                    break
            if getattr(status, "data", None) and len(status.data) > 0:
                first = status.data[0]
                md = getattr(first, "markdown", None) or (first.get("markdown") if isinstance(first, dict) else None)
                if md:
                    markdown = md
                    break
            if st.get("status") == "failed":
                break

    if not markdown or not isinstance(markdown, str):
        meta = {}
        if isinstance(result, dict):
            meta = result.get("metadata") or {}
            if not meta and isinstance(result.get("data"), dict):
                meta = result["data"].get("metadata", {})
        if isinstance(meta, dict) and meta.get("statusCode", 200) >= 400:
            print(f"Error: Fetch returned HTTP {meta.get('statusCode')} for {url}.", file=sys.stderr)
        else:
            print(
                f"Error: No markdown in Firecrawl response for {url}. "
                "The scrape may still be in progress; try again in a moment.",
                file=sys.stderr,
            )
        sys.exit(1)
    return markdown


def strip_before_first_section(md: str) -> str:
    """Drop everything before the first section heading (known section or any # heading)."""
    lines = md.split("\n")
    start = 0
    for i, line in enumerate(lines):
        m = SECTION_HEADER_RE.match(line.strip())
        if m:
            title = m.group(1).strip()
            if title in KNOWN_SECTIONS:
                start = i
                break
            if not any(
                x in title.lower()
                for x in ("bulletin", "newsletter", "0x", "subscribe", "paragraph", "home", "explore")
            ):
                start = i
                break
    return "\n".join(lines[start:])


# Footer line from Paragraph: "0x17 Web3 Security Bulletin" etc.
TRAILING_JUNK_FOOTER_RE = re.compile(r"^0x[0-9a-f]+\s+Web3 Security Bulletin$", re.I)


def strip_trailing_junk(md: str) -> str:
    """Remove trailing blocklist lines and everything after. Only use exact junk phrases and footer regex (do not cut at any [](paragraph.com) line - those appear in-body as citation links)."""
    lines = md.split("\n")
    cut = len(lines)
    junk_set = {j.strip().lower() for j in TRAILING_JUNK}
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        if line.lower() in junk_set:
            cut = i
        elif TRAILING_JUNK_FOOTER_RE.match(line):
            cut = i
    return "\n".join(lines[:cut]).rstrip()


def split_into_sections(md: str) -> list[tuple[str, str]]:
    """Split markdown into (section_title, content) list by # or ## headers."""
    sections: list[tuple[str, str]] = []
    lines = md.split("\n")
    current_title = ""
    current_lines: list[str] = []
    for line in lines:
        m = SECTION_HEADER_RE.match(line.strip())
        if m:
            if current_title or current_lines:
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = m.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_title or current_lines:
        sections.append((current_title, "\n".join(current_lines).strip()))
    return sections


def normalize_section_headers(md: str) -> str:
    """Ensure section headers are ## Section Name."""
    def repl(match):
        title = match.group(1).strip()
        return f"## {title}"
    return SECTION_HEADER_RE.sub(repl, md)


def build_cleaned_markdown(md: str) -> str:
    """Clean raw Firecrawl markdown: strip nav/trailing junk, keep all sections (including embeds)."""
    md = strip_before_first_section(md)
    md = strip_trailing_junk(md)
    sections = split_into_sections(md)
    kept: list[str] = []
    for title, content in sections:
        effective_title = title.strip() or "Intro"
        if not content.strip():
            continue
        kept.append(f"## {effective_title}\n\n{content}")
    return "\n\n".join(kept) if kept else ""


def count_sections_and_summaries(md: str) -> tuple[int, int]:
    """Count section headers (# or ##) and article summaries (**Title**-led entries). Same notion as parse_newsletter."""
    n_sections = 0
    n_summaries = 0
    lines = md.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if SECTION_HEADER_RE.match(stripped):
            n_sections += 1
            i += 1
            continue
        if stripped.startswith("**") and "**" in stripped[2:]:
            n_summaries += 1
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    i += 1
                    continue
                if next_line.startswith("#") or next_line.startswith("**"):
                    break
                i += 1
            continue
        i += 1
    return n_sections, n_summaries


def validate_output(source_md: str, output_path: Path) -> None:
    """Assert written file has same section and summary counts as source; exit non-zero on mismatch."""
    expected_sections, expected_summaries = count_sections_and_summaries(source_md)
    text = output_path.read_text(encoding="utf-8")
    actual_sections, actual_summaries = count_sections_and_summaries(text)
    if actual_sections != expected_sections or actual_summaries != expected_summaries:
        print(
            f"Validation failed for {output_path}: "
            f"section count source={expected_sections} output={actual_sections}, "
            f"summary count source={expected_summaries} output={actual_summaries}.",
            file=sys.stderr,
        )
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch Paragraph newsletters via Firecrawl and save as markdown to live_sync_newsletter/."
    )
    parser.add_argument(
        "urls",
        nargs="+",
        help="One or more Paragraph newsletter URLs",
    )
    parser.add_argument(
        "--out-dir",
        default="live_sync_newsletter",
        help="Output directory (default: live_sync_newsletter)",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip validation (section/summary count check) after writing",
    )
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for url in args.urls:
        url = url.strip()
        if not url.startswith("http"):
            print(f"Error: Not a URL: {url}", file=sys.stderr)
            sys.exit(1)
        raw = fetch_with_firecrawl(url)
        cleaned = build_cleaned_markdown(raw)
        if not cleaned.strip():
            print(f"Error: No content left after cleaning for {url}.", file=sys.stderr)
            sys.exit(1)
        slug = slug_from_url(url)
        out_path = out_dir / f"{slug}.md"
        normalized = "\n".join(cleaned.splitlines())
        out_path.write_text(normalized, encoding="utf-8")
        print(out_path)
        if not args.no_validate:
            validate_output(cleaned, out_path)


if __name__ == "__main__":
    main()
