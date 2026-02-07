---
name: newsletter-podcast-prep
description: Prepares newsletter markdown for the podcast pipeline by analyzing content, creating host-expert dialogue, and applying TTS-friendly formatting. Use when the user has newsletter markdown from fetch_newsletter_md.py and wants to create or refine input for newsletter_to_podcast.py, or when they ask to prep a newsletter for podcast or AudioPod.
allowed-tools:
  - Read
  - Write
  - Grep
  - Glob
---

# Newsletter-to-Podcast Prep

Prepares newsletter markdown for the ElevenLabs podcast pipeline: analyze content, create host/expert dialogue, apply TTS formatting, and output a script file consumable by `newsletter_to_podcast.py --script`.

## Workflow Decision Tree

### User provides a newsletter file path (e.g. in live_sync_newsletter/)
→ Read the file and run the full workflow (Analyze → Dialogue → TTS → Output).

### User pastes newsletter content
→ Use the pasted content as source and run the full workflow.

### User provides only a topic or vague request
→ Ask for the newsletter markdown file path or pasted content before proceeding.

## Phase 1: Analyze

1. **Read** the newsletter markdown completely.
2. **Detect sections** using `##` (or `#`) headers. Expected section names align with the pipeline: Insightful, Companies in the news, Gimme the loot, We must have regulations, VCs & funding, Research corner, Etc. Other section titles are allowed.
3. **Extract key facts** per section and per entry: article titles (bold lines), summaries, and URLs. Do not invent facts, examples, or context.

## Phase 2: Dialogue

Build a two-speaker script (Speaker A = Host, Speaker B = Expert):

- **Speaker A (Host)** ~30% of lines: intro, section transitions, short questions (e.g. "What's in Companies in the news?", "What else?", "Tell me more.").
- **Speaker B (Expert)** ~70% of lines: factual answers using mainly the newsletter 85% of the response; the expert can do a websearch for more context, but keep it short and ensure it matches the topic 15% of the response; one response can cover multiple items; natural flow; avoid rapid back-and-forth after every sentence.
- **Optional emotion tags**: To match `newsletter_to_podcast.py` and `podcast_config.yaml` dialogue_style, you may prefix lines with tags like `[calmly]`, `[thoughtfully]`, `[wryly]`, `[matter-of-factly]` (e.g. `[calmly] Welcome to the Web3 Security Bulletin.`).

## Phase 3: TTS Formatting

Apply speech-friendly formatting so the script sounds correct when spoken:

- **Numbers and years**: Write in words (e.g. "twenty twenty-six", "three point seven million").
- **Abbreviations**: Spell out (e.g. "U S A", "A I", "A P I") or use full form where appropriate.
- **Dates and currency**: Use words, not symbols or digits (e.g. "twenty percent", "one hundred dollars").
- **URLs and handles**: Describe the resource (e.g. "on their website") rather than reading URLs or @handles aloud.

For full rules and examples, read [reference/tts-formatting.md](reference/tts-formatting.md).

## Phase 4: Output

1. **Format**: Produce a JSON array of objects: `{"speaker": "A"|"B", "text": "..."}`. Each `text` may include optional `[emotion]` prefixes.
2. **Line length**: Keep each `text` under 4500 characters so the pipeline's chunking and API limits are satisfied.
3. **Save**: Write the script to a file using the Write tool. Suggested path: same directory as the source newsletter, with a suffix (e.g. `live_sync_newsletter/0x19-web3-security-bulletin_podcast_script.json`), or a path the user specifies.
4. **Tell the user**: After saving, instruct them to run: `python scripts/newsletter_to_podcast.py --script <path>` to generate the MP3.

## Output Format Contract

```json
[
  {"speaker": "A", "text": "[calmly] Welcome to the Web3 Security Bulletin."},
  {"speaker": "B", "text": "[thoughtfully] Let's get into it."},
  {"speaker": "A", "text": "What's in Insightful this week?"},
  {"speaker": "B", "text": "DappRadar explains why blockchain privacy matters in twenty twenty-six..."}
]
```

## Quality Requirements

- **Factual**: Use information from the newsletter. No invented examples, context, or interpretations. Use web search to add context 15% of the time. 
- **Complete**: Cover all sections and entries that carry substantive content; do not drop sections unless the user asks to focus on a subset.
- **TTS-compliant**: All spoken text must follow the TTS rules (numbers in words, abbreviations spelled out, etc.) so the resulting audio sounds correct.
- **Pipeline-compatible**: Output must be valid JSON accepted by `newsletter_to_podcast.py --script` (list of `{speaker, text}` with speaker "A" or "B").

## Reference

- For detailed TTS rules (numbers, abbreviations, dates, URLs, Web3 terms), read [reference/tts-formatting.md](reference/tts-formatting.md).
- Pipeline script: `scripts/newsletter_to_podcast.py` (accepts `--file`, `--url`, or `--script`).
- Newsletter source: output of `scripts/fetch_newsletter_md.py` (e.g. files in `live_sync_newsletter/`).
