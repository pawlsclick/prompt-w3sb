# Prompt Web3 Security Newsletter

This repo contains a small, focused workflow for producing a weekly **web3 security and privacy** newsletter.  
It is designed to be:

- **Repeatable** – the same steps every week
- **Text‑only** – everything is markdown, easy to diff and review
- **Agent‑friendly** – clear instructions so AI tools can help without breaking style

Only a few core files are tracked in git so that the workflow and rules are versioned, but large/generated weekly outputs stay local.

---

## What this project does

At a high level, the project helps you:

1. **Collect sources** – research papers, incident write‑ups, deal/funding news, and blog posts about web3 security and privacy.
2. **Plan the issue** – choose which links to feature and group them into newsletter sections.
3. **Draft the newsletter** – turn links into short, skimmable summaries in a consistent format.
4. **Humanize and finalize** – clean up AI‑ish writing tics while keeping the facts and structure.
5. **Publish** – optionally mirror the final markdown into Notion using MCP tools.

The concrete steps for each run live in `run_newsletter.md`. The detailed style and structure rules live in `.cursor/rules/newsletter-style.md`.

---

## Core files under version control

- `run_newsletter.md`  
  End‑to‑end checklist for producing a single issue:
  - How to search for sources (research, deals, blogs)
  - Which markdown files to generate (`web3_*_urls.md`, `plan_newsletter_YY-MM-DD.md`, etc.)
  - Validation checks before moving from planning → draft → final → publish

- `.cursor/rules/newsletter-style.md`  
  Project rule file that defines:
  - Section structure and ordering (`Insightful`, `Companies in the news`, `Gimme the loot`, `We must have regulations`, `VCs & funding`, `Research corner`, `Etc`)
  - Exact entry format (bold title, ≤ 70‑word summary, URL on its own line)
  - Tone guidelines (third‑person, factual, non‑hype)

- `.cursor/skills/humanizer/SKILL.md`  
  Cursor skill used in the “finalize” phase to:
  - Remove common AI‑generated writing patterns
  - Keep structure and facts intact while making the prose feel human

- `.gitignore`  
  Keeps weekly, date‑stamped outputs and scratch files out of git so the repo stays small and focused.

- **Live newsletter fetch**  
  `scripts/fetch_newsletter_md.py` fetches published Paragraph newsletters via [Firecrawl](https://firecrawl.dev) and writes cleaned markdown to `live_sync_newsletter/`. One file per URL (e.g. `0x19-web3-security-bulletin.md`). Useful for turning past issues into podcast input or for agent parsing.
  - **Setup**: Set `FIRECRAWL_API_KEY` (env or `.env`). Install deps: `pip install -r requirements_podcast.txt`.
  - **Usage**: `python scripts/fetch_newsletter_md.py "https://paragraph.com/@w3sb/0x19-web3-security-bulletin"` → writes `live_sync_newsletter/0x19-web3-security-bulletin.md`. Use `--out-dir` for a different directory, `--no-validate` to skip section/summary count check.
  - **Behavior**: Strips nav and trailing junk (footer, Cloudflare text, etc.); keeps all sections including embeds. Output is UTF‑8 markdown; existing files are overwritten. See `run_fetch_newsletter.md` for more detail.

- **S3 upload (podcast bucket)**  
  `scripts/copy_to_w3sb_bucket.sh` copies a local file to the `w3sb-bucket-pod` S3 bucket (region `eu-north-1`). Uses AWS CLI with credentials from `~/.aws`.
  - **Usage**: `./scripts/copy_to_w3sb_bucket.sh <local_file> [s3_key]`. If `s3_key` is omitted, the object key is the basename of the local file.
  - **Examples**: `./scripts/copy_to_w3sb_bucket.sh ./podcast_output/podcast_0x19.mp3` or `./scripts/copy_to_w3sb_bucket.sh ./podcast_output/podcast_0x19.mp3 0x19-w3sb.m4a`.
  - **Output**: Prints the object URL (`https://w3sb-bucket-pod.s3.eu-north-1.amazonaws.com/<key>`) when done; the last line is the URL only, so you can capture it with `| tail -1`.

---

## Files intentionally **not** tracked

The newsletter workflow produces several per‑issue markdown files. These are treated as **ephemeral artifacts** and are ignored via `.gitignore`:

- `web3*.md` – URL lists for research, deals, and security blogs
- `plan_newsletter_YY-MM-DD.md` – planning file for a specific issue
- `draft_newsletter_YY-MM-DD.md` – draft newsletter text
- `final_newsletter_YY-MM-DD.md` – final, humanized newsletter

This keeps the public repo focused on:

- The **process** (`run_newsletter.md`)
- The **style rules** (`newsletter-style.md`)
- The **editing skill** (`humanizer`)

…while you are free to generate as many local issues as you want without creating noisy history.

---

## Typical run: from empty repo to one newsletter

1. **Update inputs**
   - Refresh the URL source files (`web3_security_blogs.md`, `web3_research_urls.md`, `web3_deals_urls.md`, `todays_urls.txt`) according to `run_newsletter.md`.

2. **Create the planning file**
   - Use the sources above to generate `plan_newsletter_YY-MM-DD.md`, grouping items into the standard sections.

3. **Draft the newsletter**
   - Convert the planning file into `draft_newsletter_YY-MM-DD.md` following `.cursor/rules/newsletter-style.md`.

4. **Humanize and finalize**
   - Apply the `humanizer` skill to the draft and save as `final_newsletter_YY-MM-DD.md`.

5. **Publish**
   - Optionally use the Notion MCP tools (see `run_newsletter.md`) to create a Notion page under `Weekly Newsletter Drafts` with the final markdown.

---

## Working with git and GitHub

Only a minimal set of files is committed:

```text
.cursor/
  rules/newsletter-style.md
  skills/humanizer/SKILL.md
.gitignore
README.md
run_newsletter.md
```

Everything else is either generated per‑issue or local tooling.

If you clone this repo and want to run the workflow yourself:

1. Make sure you’re on the `main` branch and up to date:
   ```bash
   git clone git@github.com:pawlsclick/prompt-w3sb.git
   cd prompt-w3sb
   git pull
   ```
2. Follow the steps documented in `run_newsletter.md` for the current date.

---

## Future ideas

Some potential extensions that would fit cleanly into this structure:

- Add automation scripts to:
  - Fetch fresh URLs into the `web3_*.md` files
  - Validate section word counts automatically
  - Run a “lint” pass over newsletter entries
- Add examples of past `plan_`, `draft_`, and `final_` files (in a separate branch or sample directory) to serve as templates.

For now, the focus is on keeping this repo small, readable, and easy to use as an agent‑friendly newsletter workstation.

