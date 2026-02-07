# Cursor Skill: Newsletter-to-Podcast Prep

Prepares newsletter markdown for the podcast pipeline by analyzing content, creating host-expert dialogue, and applying TTS-friendly formatting. Output is a JSON script file consumable by `newsletter_to_podcast.py --script`.

## Features

- **Analysis**: Extracts key facts from newsletter markdown (sections, titles, summaries, URLs) without inventing content.
- **Dialogue**: Creates host (~20%) and expert (~80%) turns with natural questions and factual responses.
- **TTS formatting**: Converts numbers, abbreviations, dates, and technical terms to speech-friendly form (see `reference/tts-formatting.md`).
- **Pipeline output**: Produces a JSON dialogue script that the existing ElevenLabs pipeline can consume.

## Usage

1. Have newsletter markdown (e.g. from `scripts/fetch_newsletter_md.py` in `live_sync_newsletter/`).
2. In Cursor, ask the agent to prep the newsletter for podcast (e.g. "Prep live_sync_newsletter/0x19-web3-security-bulletin.md for podcast").
3. The skill writes a script file (e.g. `live_sync_newsletter/0x19-web3-security-bulletin_podcast_script.json`).
4. Run the pipeline: `python scripts/newsletter_to_podcast.py --script live_sync_newsletter/0x19-web3-security-bulletin_podcast_script.json`
5. MP3 is written to `output/` (or `--output` path).

## Directory layout

```
newsletter-podcast-prep/
├── README.md           # This file
├── SKILL.md            # Main skill instructions (workflow, output format)
├── reference/
│   └── tts-formatting.md   # TTS rules (numbers, abbreviations, Web3 terms)
├── CONTRIBUTING.md
└── LICENSE
```

## Skill best practices

This skill follows [Cursor/Claude skill best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices): concise SKILL.md, progressive disclosure via `reference/`, clear trigger description, and a defined output contract for the pipeline.

## Requirements

- Newsletter markdown in the format produced by `scripts/fetch_newsletter_md.py` (e.g. `## Section` headers, `**Title**` entries, summaries).
- Pipeline: `scripts/newsletter_to_podcast.py` with `--script` support, `ELEVENLABS_API_KEY`, and `podcast_config.yaml` with `speaker_a` and `speaker_b` voice IDs.
