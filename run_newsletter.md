# Newsletter Generation Workflow

Follow this workflow to generate the weekly web3 security newsletter. All outputs are markdown. If an output file already exists, overwrite it.

## Configuration

- **Today’s date**: use current date.
- **Timeframe**: past 8 days from today.
- **Date format in filenames**: `YY-MM-DD` (for example, `26-01-26` for 26 Jan 2026).
- **Output files**:
  - Planning: `plan_newsletter_YY-MM-DD.md`
  - Draft: `draft_newsletter_YY-MM-DD.md`
  - Final: `final_newsletter_YY-MM-DD.md`
  - Readwise tweets: `web3_readwise.md`
- **Notion Readwise database** (Category = Tweets): `2ef14f7daba281aea46ee886dbea2ca3`. Use Notion MCP to query and fetch page content; output to `web3_readwise.md`.
- **Style rules**: follow `.cursor/rules/newsletter-style.md` for:
  - Sections and ordering
  - Entry format (title, summary, URL)
  - Tone and word-count limits
- **X.com sources**: if a URL is on `x.com` (including `/status/` links), use the **built-in browser MCP** to access/extract the post text (Firecrawl is blocklisted for `x.com`).
- **Firecrawl fallback**: if Firecrawl encounters an error accessing a page (for any URL), retry using the **built-in browser MCP** to access and extract the content.

Before moving between phases, confirm that the expected input file for the next phase exists and is non-empty.

---

## Phase 1: Search

1. Search the web for articles in the past 8 days that focus on web3 crypto blockchain token regulation and compliance in the United States, United Kingdom, Europe and the EU and Asia. 
   - Output: markdown list of URLs for each paper or report.  
   - **Output file**: `web3_regulations_urls.md`

2. Search the web for research publications in the past 8 days that focus on web3 crypto security or privacy, including Bitcoin, Ethereum, Solana, or other blockchains. Use sources such as https://arxiv.org/ and https://www.sciencedirect.com/ 
   - Output: markdown list of URLs for each paper or report.  
   - **Output file**: `web3_research_urls.md`

3. Search the web for venture capital, private equity, M&A, funding (seed, Series A, Series B), and IPO activity in the past 8 days that focuses on web3 crypto security or privacy, including Bitcoin, Ethereum, Solana, or other blockchains. Use sources such as https://crypto-fundraising.info/  
   - Output: markdown list of URLs for each relevant articles.  
   - **Output file**: `web3_deals_urls.md`

4. **Notion Readwise (Category = Tweets)**  
   Use the Notion MCP to extract content from the Readwise database (ID: `2ef14f7daba281aea46ee886dbea2ca3`). This may be the parent page containing an inline “Library” database; the data source URL appears in the fetch response as `data-source-url="collection://..."` inside a `<data-source>` or `<database>` tag.
   - Fetch the database (or parent page) to obtain its data source URL (`collection://...`).
   - Search or query the database for pages where **Category** = **Tweets** (e.g. semantic search with `data_source_url` and a query like “Tweets”, or fetch database contents and filter by Category).
   - For each matching page, use **notion-fetch** to get the full page. Extract and record:
     - **Title** (Full Title property)
     - **Author**
     - **URL**
     - **Last Highlighted** (date)
     - **Content** (page body / blocks as markdown)
   - **Output file**: `web3_readwise.md`  
   - **Output format**: one block per tweet, with clear headings so Phase 2 can use the content without re-fetching. Example structure:
     ```markdown
     ## [Title]
     - **Author**: ...
     - **URL**: ...
     - **Last Highlighted**: ...
     - **Content**: ...
     ---
     ```
   - Overwrite the file if it already exists.

Both URL outputs (steps 1–2) are plain URL lists in markdown. Overwrite existing files with the latest run.

**Validation before Phase 2**:
- [ ] `web3_regulations_urls.md` exists and contains at least one URL or a clear note if no results. 
- [ ] `web3_research_urls.md` exists and contains at least one URL or a clear note if no results.
- [ ] `web3_deals_urls.md` exists and contains at least one URL or a clear note if no results.
- [ ] `web3_readwise.md` exists (and contains at least one tweet block, or a clear note if no Category = Tweets pages found).

---

## Phase 2: Planning

Use the URL sources below to find blogs, posts, Tweets, articles or PDFs published today or within the past 8 days.

Source files with website URLs:
- `web3_regulations_urls.md`
- `web3_security_blogs.md`
- `web3_deals_urls.md`
- `web3_research_urls.md`
- `todays_urls.txt`
- `web3_readwise.md`

For each site or URL:
- If you find at least one article within the timeframe, record the article URL (and brief label) under the appropriate section.
- If no relevant articles are found for a specific website, record `"No Articles"` for that website.

Output:
- A structured markdown planning file that groups URLs by section (Insightful,Companies in the news, Gimme the loot, We must have regulations, VCs & funding, Research corner, Etc.), similar to existing `plan_newsletter_YY-MM-DD.md` examples.
- **Output file**: `plan_newsletter_YY-MM-DD.md`

**Validation before Phase 3**:
- [ ] `plan_newsletter_YY-MM-DD.md` exists.
- [ ] It contains at least one article URL in the “Articles Found” section, or clearly documents that no articles were found.

---

## Phase 3: Draft

Goal: turn `plan_newsletter_YY-MM-DD.md` into a draft newsletter.

Instructions:
- Follow the project rule `.cursor/rules/newsletter-style.md` for:
  - Section structure and ordering.
  - Entry format (bold title line, ≤ 100-word summary, URL on its own line).
  - Tone (third-person, technical, industry insider, factual, calm).
- For each article in the planning file, create **exactly one** newsletter entry under the appropriate section.

Output:
- Draft newsletter in markdown with full sections and entries.
- **Output file**: `draft_newsletter_YY-MM-DD.md`

**Validation before Phase 4**:
- [ ] `draft_newsletter_YY-MM-DD.md` exists.
- [ ] Each entry follows the title / summary / URL pattern.
- [ ] Summaries are ≤ 100 words and match the style rules.

---

## Phase 4: Finalize

### 4.1 Humanize the draft

1. Read `draft_newsletter_YY-MM-DD.md`.
2. Use the `humanizer` skill (`.cursor/skills/humanizer/SKILL.md`) to:
   - Remove AI-sounding patterns (inflated symbolism, vague attributions, overused AI vocabulary, filler).
   - Preserve the newsletter structure and factual content.
3. Apply edits to produce the final newsletter.

Output:
- **Output file**: `final_newsletter_YY-MM-DD.md`
- Overwrite an existing final file if present.

**Validation before publishing**:
- [ ] `final_newsletter_YY-MM-DD.md` exists.
- [ ] Structure matches the project rule (sections, entries, URLs).
- [ ] Style feels human and aligned with the newsletter-style rule.

### 4.2 Publish to Notion

Use the Notion MCP tools (for example, `notion-create-pages`) to publish the final newsletter:

- **Parent page**: `Weekly Newsletter Drafts`
- **Page title**: `Newsletter - <human-readable date range>` (for example, `Newsletter - Jan 15-23, 2026`)
- **Content**: the full contents of `final_newsletter_YY-MM-DD.md` rendered as markdown.

High-level instruction to the agent:
- “Create a new Notion page under `Weekly Newsletter Drafts` using `final_newsletter_YY-MM-DD.md` as the page body, with a title like `Newsletter - Jan 15-23, 2026`.”
