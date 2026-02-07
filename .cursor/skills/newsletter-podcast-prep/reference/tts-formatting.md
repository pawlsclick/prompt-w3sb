# TTS-Friendly Formatting Reference (English)

Guidelines for formatting dialogue text so it works well with text-to-speech (e.g. ElevenLabs). All rules below are for English.

## Numbers and Years

Write numbers in words so TTS engines pronounce them correctly.

- **Years**: "1989" → "nineteen eighty-nine"; "2026" → "twenty twenty-six"
- **Large numbers**: "3.7 million" not "3.7M"; "100 thousand" not "100K"
- **Decimals**: "three point seven" not "3.7"
- **Percentages**: "twenty percent" not "20%"
- **Ordinals**: "first", "second", "third" not "1st", "2nd", "3rd"

## Abbreviations

Spell out abbreviations or use the full form. TTS cannot reliably guess pronunciation.

### Titles

- "Doctor" not "Dr."
- "Professor" not "Prof."
- "Mister" not "Mr."

### Organizations and acronyms

- "U S A" or "United States" not "USA"
- "E U" or "European Union" not "EU"
- "A I" or "artificial intelligence" not "AI"
- "A P I" or "application programming interface" not "API"

### Common symbols

- **&**: Write "and"
- **#**: Write "number" or "hashtag" as appropriate
- **@**: Write "at" when referring to handles (e.g. "at username" instead of "@username")
- **%**: Always spell out (e.g. "twenty percent")

## Dates and Currency

### Dates

Use full words:

- "November twenty-third, twenty twenty-six" not "23/11/2026" or "Nov 23, 2026"

### Currency

Spell out the amount and the currency name:

- "one hundred dollars" not "$100"
- "fifty euros" not "€50"
- "twenty pounds" not "£20"

## Units and Measurements

Write units in full with numbers in words where it reads naturally:

- "ten kilometers" not "10km"
- "five meters" not "5m"
- "two liters" not "2L"
- "three point seven million subscribers" not "3.7M subscribers"

## URLs and Technical Terms

TTS cannot meaningfully read URLs or raw identifiers. Describe them instead.

### URLs

- Use "on their website" or "at the link in the show notes" instead of reading "https://example.com"

### Email and handles

- "contact them by email" instead of reading an email address
- "on Twitter as username" instead of "@username"

### Hashtags

- "hashtag A I coding" instead of "#AICoding"

## Web3 and tech terms

For security and crypto newsletters, these patterns help:

- **zkEVM, zkVM**: Can be read as "Z K E V M" / "Z K V M" or "zero-knowledge E V M" when clarity matters.
- **DeFi**: "De Fi" or "decentralized finance"
- **EVM**: "E V M" or "Ethereum Virtual Machine"
- **dApp / dApps**: "d app" / "d apps" or "decentralized app(s)"
- **NFT**: "N F T" or "non-fungible token"
- **TVL**: "T V L" or "total value locked"
- **AML/CFT**: "A M L" / "C F T" or "anti-money laundering" / "combating the financing of terrorism"

When in doubt, spell so a listener can follow without seeing the text.

## Best practices summary

1. **Numbers in words** – Avoid digits in dialogue.
2. **Spell out abbreviations** – Don't rely on TTS to pronounce acronyms.
3. **Full dates** – No numeric date formats.
4. **Currency names** – Never use symbols alone.
5. **Describe technical identifiers** – URLs, emails, handles described, not read.
6. **Natural flow** – Write how you would say it aloud.
