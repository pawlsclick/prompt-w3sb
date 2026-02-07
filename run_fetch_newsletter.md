# Fetch live newsletters to markdown

Script: `scripts/fetch_newsletter_md.py`. Fetches Paragraph newsletter URLs via Firecrawl and writes cleaned markdown to `live_sync_newsletter/` (or `--out-dir`). Output is suitable for `newsletter_to_podcast.py --file` and for section/paragraph parsing by agents.

## Setup

1. **API key**: Set `FIRECRAWL_API_KEY` in your environment or in a `.env` file in the project root. Get a key from [firecrawl.dev](https://firecrawl.dev/).
2. **Dependencies**: `pip install -r requirements_podcast.txt` (includes `firecrawl-py`).

## Usage

```bash
# One URL (writes live_sync_newsletter/0x19-web3-security-bulletin.md)
python scripts/fetch_newsletter_md.py "https://paragraph.com/@w3sb/0x19-web3-security-bulletin"

# Multiple URLs
python scripts/fetch_newsletter_md.py "https://paragraph.com/@w3sb/0x19-web3-security-bulletin" "https://paragraph.com/@w3sb/0x18-web3-security-bulletin"

# Custom output directory
python scripts/fetch_newsletter_md.py --out-dir ./out "https://paragraph.com/@w3sb/0x19-web3-security-bulletin"

# Skip validation (e.g. for testing or speed)
python scripts/fetch_newsletter_md.py --no-validate "https://paragraph.com/@w3sb/0x19-web3-security-bulletin"
```

## Behavior

- **Fetch**: Uses Firecrawl only (no fallback). On timeout, 4xx/5xx, or missing/invalid `FIRECRAWL_API_KEY`, prints a clear error and exits non-zero; no file is written.
- **Output**: One markdown file per URL. Filename = slug from URL path (e.g. `0x19-web3-security-bulletin.md`), sanitized for the filesystem. Files are UTF-8 with `\n` line endings. Existing files are overwritten.
- **Validation (default on)**: After writing, counts section headers and article summaries in the parsed source and in the written file; if counts differ, prints a message and exits non-zero. Use `--no-validate` to skip.
- **Embeds**: All sections are kept, including those with X.com/Twitter or other embeds. Only nav and trailing junk (footer, Cloudflare text, exact junk phrases) are stripped.

## Using the output

- Pass the written path to the podcast script:  
  `python scripts/newsletter_to_podcast.py --file live_sync_newsletter/0x19-web3-security-bulletin.md`
- Use the markdown for downstream agents (section/paragraph parsing). Format matches `.cursor/rules/newsletter-style.md` and `parse_newsletter` in `newsletter_to_podcast.py`.
