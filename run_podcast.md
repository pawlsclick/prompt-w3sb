# Newsletter to Podcast (ElevenLabs)

Generate a two-speaker podcast from a W3SB newsletter using the ElevenLabs Text-to-Dialogue API.

## Setup

1. **API key**  
   Create an API key in the [ElevenLabs dashboard](https://elevenlabs.io/app/settings/api-keys). Put it in a `.env` file in the project root (do not commit this file):

   ```
   ELEVENLABS_API_KEY=your_api_key_here
   ```

2. **Dependencies**  
   Install the required packages:

   ```bash
   pip install -r requirements_podcast.txt
   ```
   or:
   ```bash
   python3 -m pip install -r requirements_podcast.txt
   ```

3. **Speaker voices**  
   Edit `podcast_config.yaml` in the project root and set `speaker_a.voice_id` and `speaker_b.voice_id` to two different ElevenLabs voice IDs.

   To list your available voices (name and ID):

   ```bash
   python3 scripts/list_voices.py
   ```

   Copy two voice IDs into `podcast_config.yaml`.

4. **Optional config**  
   In `podcast_config.yaml` you can also set:
   - `speaker_a.name` / `speaker_b.name` — used only for script generation (e.g. "Host", "Co-host").
   - `dialogue_style` — one of `professional`, `casual`, or `wry` to influence tone and emotion tags in the dialogue.

## Usage

**From a local newsletter markdown file (recommended):**

```bash
python3 scripts/newsletter_to_podcast.py --file final_newsletter_26-02-06.md
```

You can test with the included sample: `--file sample_newsletter_0x19.md`

**From a Paragraph URL:**

```bash
python3 scripts/newsletter_to_podcast.py --url "https://paragraph.com/@w3sb/0x19-web3-security-bulletin"
```

Paragraph is often client-rendered, so `--url` may not receive the article body and you’ll see “No sections/entries parsed.” In that case, save the newsletter as markdown (e.g. copy from the page or use another tool to export) and run with `--file` instead.

**Options:**

- `--config PATH` — Path to podcast config YAML (default: `podcast_config.yaml`).
- `--output PATH` — Full path for the output MP3 (default: `podcast_output/podcast_<slug>.mp3`).
- `--output-dir DIR` — Directory for the default output file (default: `podcast_output`).

## Output

The script writes a single MP3 file (e.g. `podcast_output/podcast_Web3_Security_Bulletin.mp3`). It prints the path and size when done. Open the file in any audio player or move it wherever you like.

## Troubleshooting

- **"Set ELEVENLABS_API_KEY"** — Create a `.env` file with `ELEVENLABS_API_KEY=...` in the project root, or export the variable in your shell.
- **"No sections/entries parsed"** — The newsletter should use `## Section` headings and entries with `**Title**`, a summary paragraph, and optionally a URL. Use a local `--file` that matches the format in `.cursor/rules/newsletter-style.md`.
- **"Install requests and beautifulsoup4 for --url"** — Install dependencies: `pip install -r requirements_podcast.txt`.
- **pydub / ffmpeg** — If you use chunked API calls and concatenate audio, `pydub` is used. On some systems you may need `ffmpeg` installed for MP3 export.

- **ConnectError / Operation timed out** — The script uses a 120s timeout and retries each API call up to 3 times. If timeouts persist, check your network (firewall, VPN, or outbound HTTPS to `api.elevenlabs.io`). Running from a different network or disabling a VPN sometimes helps.
