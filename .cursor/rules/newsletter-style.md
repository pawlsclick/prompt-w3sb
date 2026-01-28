---
name: newsletter-style
description: Define the structure, tone, and formatting for weekly web3 security newsletters. Use when generating or editing plan, draft, or final newsletter markdown files so they follow a consistent section layout, word-count limits, and URL formatting.
---

## Identity and purpose

This project publishes a weekly web3 security and privacy newsletter based on research papers, incident reports, industry analysis, and funding activity.

Use this rule whenever you:
- Turn `plan_newsletter_YY-MM-DD.md` into a draft or final newsletter
- Edit `draft_newsletter_YY-MM-DD.md` or `final_newsletter_YY-MM-DD.md`
- Summarize individual articles into newsletter entries

The goal is a concise, skimmable, fact-focused newsletter that reads like Frontend Weekly but focused on web3 security.

## Date and filenames

- **Date format in filenames**: `YY-MM-DD` (example: `26-01-26` for 26 Jan 2026)
- **Planning file**: `plan_newsletter_YY-MM-DD.md`
- **Draft file**: `draft_newsletter_YY-MM-DD.md`
- **Final file**: `final_newsletter_YY-MM-DD.md`
- All outputs are markdown; if a file already exists, overwrite it.

In the newsletter title, prefer a human-readable range, for example:
- `# Newsletter - Jan 15-23, 2026`

## Sections and ordering

Organize the newsletter into these sections in order. Skip a section entirely if there are no entries for it.

1. `## Insightful`
   - Security technique or research blog posts
   - Trends in the web3 crypto industry 
   - Audit findings 
   - Coding techniques and examples 
2. `## Companies in the news`
   - New product launches
   - Product updates 
   - Company partnerships 
   - Newsworthy headlines 
3. `## Gimme the loot`
   - Crypto hacks and exploits 
   - Root cause analysis 
   - Blockchain investigations 
4. `## We must have regulations`
   - Policy changes, regulatory guidance, enforcement actions
   - Compliance with regulations and laws
5. `## VCs & funding`
   - Venture rounds, M&A, major partnerships
   - New company to market 
6. `## Research corner`
   - Deep technical white papers
   - Sourced from arXiv or similar research publication organizations 
7. `## Etc`
   - Catch-all if an article does not fit in a section above



If you need a dedicated exploits section for a heavy week of incidents:
- Use `## Exploits & Hacks` before `## Security & Research`

## Entry format

Each article becomes exactly one entry:

1. **Title line (bold)**  
   - Format: `**Short, concrete headline**  ` (two spaces at end for line break)
   - Focus on the main event or key takeaway.

2. **Summary paragraph (≤ 70 words)**  
   - One paragraph, plain text.
   - Start with the author or publication when known, e.g.  
     - `Rekt News explains how...`  
     - `Chainalysis argues that...`
   - Cover: who, what happened, why it matters to security or privacy.
   - Avoid promotional language or hype.

3. **Source URL on its own line**  
   - Backticked: `` `https://example.com/article` ``
   - No additional commentary on that line.

Example entry:

```markdown
**The Truebit Exploit Explained**  
Cantina breaks down how an unchecked addition in a 0.5.3 pricing function drove TRU's purchase price to zero, enabling unlimited minting and a $26M loss, plus maintenance lessons for legacy contracts.  
`https://cantina.xyz/blog/the-truebit-exploit-explained`
```

## Tone and style

- **Narration**: Third person, calm, and factual.
- **Voice**: Knowledgeable observer, not a marketing voice.
- **Perspective**: No first-person singular/plural in the newsletter body.
- **Hype**: Avoid phrases like “groundbreaking”, “revolutionary”, “game-changing”.
- **Clarity**: Prefer simple verbs (`is`, `has`, `shows`) over elaborate phrasing.

When in doubt, follow these rules:
- Explain why the item matters in one clause.
- Prefer specific numbers, dates, and entities over vague claims.

## Relationship to the humanizer skill

After draft creation, use the `humanizer` skill to:
- Strip AI-sounding patterns (inflated symbolism, vague attributions, overused AI vocabulary).
- Reduce filler and hedging.
- Keep entries within the target word count.

Do **not** let humanization change:
- The structure (title → summary → URL)
- Factual content or key numbers

## Checklist for each run

Before calling the newsletter “final”, quickly verify:

- [ ] Filenames use `YY-MM-DD` and match each other.
- [ ] The title line includes the correct date range.
- [ ] Sections are in the standard order and only included when they have content.
- [ ] Every entry follows the title / summary / URL pattern.
- [ ] Summaries are under 70 words.
- [ ] Tone is factual and non-promotional.
- [ ] URLs are present and backticked.

