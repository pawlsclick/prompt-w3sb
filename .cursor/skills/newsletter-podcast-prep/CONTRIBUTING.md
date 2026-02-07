# Contributing to Newsletter-to-Podcast Prep Skill

## Guidelines

- **SKILL.md**: Keep under 500 lines; use imperative voice; link to `reference/tts-formatting.md` for detailed TTS rules. Do not nest references deeper than one level.
- **Description**: Frontmatter `description` must state what the skill does and when to use it (trigger scenarios).
- **Factual only**: The skill must not add invented facts, examples, or context; all expert content comes from the newsletter.
- **Output contract**: Script JSON must be a list of `{"speaker": "A"|"B", "text": "..."}`; each `text` under 4500 characters.

## Testing

After changing SKILL.md or reference files:

1. Run with a real newsletter from `live_sync_newsletter/` (e.g. ask the agent to prep one file for podcast).
2. Confirm the generated JSON is valid and accepted by: `python scripts/newsletter_to_podcast.py --script <path>`.
3. Optionally generate an MP3 and spot-check that numbers and abbreviations are spoken correctly (TTS formatting).

## Checklist before submitting changes

- [ ] Frontmatter `name` and `description` are set; description includes both capability and triggers.
- [ ] SKILL.md is under 500 lines and uses imperative voice.
- [ ] References are one level deep (SKILL.md → reference/*.md).
- [ ] TTS rules in `reference/tts-formatting.md` are consistent with pipeline needs (English, Web3 terms as needed).
- [ ] No invented content; dialogue uses only newsletter source material.
