---
name: claim-scraper
description: "Scrape social media for real-world health claims that are optimal inputs for the peptide-investigator skill. Use when asked to 'find claims', 'scrape for pain points', 'find test cases', or 'find examples for the investigator'. Accepts a platform parameter: reddit, twitter, instagram."
---

# Claim Scraper

Scrape social media platforms via Apify to find real-world peptide/health claims. Filters, scores, and curates optimal inputs for the peptide-investigator skill.

## When to Use

When a user asks to find claims, pain points, or test cases for the peptide-investigator skill. Trigger phrases:
- "find claims on [platform]"
- "scrape [platform] for pain points"
- "find test cases"
- "find examples for the investigator"

## Prerequisites

- `.env` file with `APIFY_TOKEN`
- Node.js 20.6+

## Input

Extract from the user's message:
1. **Platform** — reddit, twitter, or instagram (default: reddit)
2. **Topic focus** — optional narrowing (e.g., "GLP-1 side effects", "BPC-157 recovery"). Default: broad peptide claims.
3. **Count** — how many curated claims to output (default: 12)

## Step 1: Select Actors and Build Queries

### Platform → Actor Mapping

| Platform | Actor ID | Notes |
|----------|----------|-------|
| reddit | `comchat~reddit-api-scraper` | Search-based. Use `searchList` param with multiple query strategies. |
| twitter | Search Apify store for "twitter scraper" or "x scraper" | Use `mcpc` to find the best available actor. Twitter actors change frequently. |
| instagram | `apify/instagram-hashtag-scraper` | Hashtag-based. Scrape peptide-related hashtags. |

### Query Strategy

Choose the right approach based on whether the user specified a compound/topic:

**If the user specified a specific compound or topic** → skip discovery, go straight to targeted scrapes:

| Run | Strategy | Example queries |
|-----|----------|-----------------|
| 1 | **Positive claims** | "[compound] helped my", "[compound] healed", "[compound] fixed" |
| 2 | **Negative claims / side effects** | "[compound] caused", "[compound] side effect", "[compound] made worse" |
| 3 | **Exploration** | "has anyone tried [compound] for", "[compound] experience", "[compound] results" |
| 4 | **Compound + condition combos** | "[compound] pain", "[compound] sleep", "[compound] anxiety", etc. |
| 5 | **Strong signal** | "[compound] completely", "[compound] transformed", "[compound] ruined" |

Target ~50 items per run, ~250 total.

**If the user wants a broad scrape (no specific compound)** → use two phases:

*Phase 1 — Broad discovery.* Use generic, domain-level queries with NO compound names. The goal is to find what the community is actually talking about right now.

| Run | Strategy | Example queries (adapt to user's domain) |
|-----|----------|-----------------|
| 1 | **Positive outcomes** | "helped my", "healed my", "fixed my", "cured my" |
| 2 | **Negative outcomes / side effects** | "caused", "side effect", "made worse", "ruined" |
| 3 | **Exploration** | "has anyone tried", "thinking about trying", "considering" |

Scope these to the right communities — use subreddit filters for Reddit (e.g., `r/Peptides`, `r/Nootropics`), hashtags for Instagram, etc. The user's topic focus or the group's `CLAUDE.md` tells you which communities to target. If neither is available, ask the user.

Target ~50 items per run, ~150 total in Phase 1.

*Phase 2 — Targeted deep scrape.* Analyze Phase 1 results to extract the top 10-15 compound names that appear most frequently. Then run targeted queries using those discovered compounds:

| Run | Strategy | Example queries |
|-----|----------|-----------------|
| 4 | **Compound + condition combos** | "[discovered compound] [condition mentioned alongside it]" |
| 5 | **Strong signal claims** | "[discovered compound] completely", "[discovered compound] transformed" |

Target ~50 items per run, ~100 total in Phase 2.

This two-phase approach means no hardcoded compound list — the platform tells you what matters right now. Works for any domain.

### Reddit-Specific Config

```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "comchat~reddit-api-scraper" \
  --input '{"searchList": ["QUERY1", "QUERY2", "QUERY3"], "maxItems": 50, "sort": "relevance", "time": "year", "type": "link"}' \
  --output /workspace/group/scrape-run-N.json \
  --format json
```

Run each of the 5 query strategies as a separate actor call, saving to separate files (`scrape-run-1.json` through `scrape-run-5.json`). Target ~50 items per run, ~250 total.

### Twitter-Specific Config

First, find a working Twitter/X actor:
```bash
export $(grep APIFY_TOKEN .env | xargs) && mcpc --json mcp.apify.com --header "Authorization: Bearer $APIFY_TOKEN" tools-call search-actors keywords:="twitter scraper" limit:=5 offset:=0 category:="" | jq -r '.content[0].text'
```

Then fetch its schema:
```bash
export $(grep APIFY_TOKEN .env | xargs) && mcpc --json mcp.apify.com --header "Authorization: Bearer $APIFY_TOKEN" tools-call fetch-actor-details actor:="ACTOR_ID" | jq -r ".content"
```

Adapt the 5-query strategy to the actor's input schema.

### Instagram-Specific Config

Use hashtag-based scraping. For Phase 1, use broad domain hashtags from the user's topic or the group context. For Phase 2, convert discovered compound names to hashtag format (strip hyphens/spaces, e.g., "BPC-157" → "bpc157"):
```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "apify/instagram-hashtag-scraper" \
  --input '{"hashtags": ["HASHTAG1", "HASHTAG2", "HASHTAG3"], "resultsLimit": 50}' \
  --output /workspace/group/scrape-run-N.json \
  --format json
```

## Step 2: Load and Merge Results

After all scrape runs complete, load all JSON files and merge into a single array. Deduplicate by URL or post ID.

## Step 3: Filter Out Noise

Remove posts that match ANY of these noise categories:

| Category | Pattern |
|----------|---------|
| Sourcing | "where to buy", "best vendor", "source", "supplier", "coupon", "discount" |
| Dosing/reconstitution | "how to reconstitute", "how many units", "insulin syringe", "BAC water", "mixing" |
| Regulatory | "FDA", "legal", "banned", "DEA", "schedule", unless the post ALSO contains a health claim |
| Vendor reviews | "quality", "shipping", "arrived", "packaging", review of a vendor not a compound |
| Generic lifestyle | no specific peptide mentioned, just general health/fitness/diet talk |
| Low content | title-only posts with no body text, or body < 50 characters |

## Step 4: Score and Rank

Score each remaining post on these dimensions (higher = better):

| Dimension | Points | Criteria |
|-----------|--------|----------|
| **Specificity** | +30 | Named peptide + named condition + dose or timeline mentioned |
| | +20 | Named peptide + named condition, no dose/timeline |
| | +10 | Named peptide only, vague condition |
| **Claim language** | +25 | Negative claim (side effect, harm, "made worse") |
| | +20 | Positive claim ("healed", "fixed", "resolved") |
| | +15 | Exploration ("has anyone tried", "thinking about") |
| | +5 | Neutral/informational |
| **Engagement** | +15 | High engagement (top 20% by upvotes+comments in dataset) |
| | +10 | Medium engagement (top 50%) |
| | +5 | Low engagement |
| **Platform relevance** | +10 | From a peptide-specific community (r/Peptides, r/bpc_157, r/Retatrutide, #peptidetherapy, etc.) |
| | +5 | From a condition-specific community (r/Gastritis, r/PCOS, r/Nootropics, etc.) |
| | +0 | General community |
| **Clarity** | +10 | Single peptide + single condition = cleanest investigator input |
| | +5 | Single peptide + multiple conditions OR multiple peptides + single condition |
| | +0 | Multiple peptides + multiple conditions (too messy) |

## Step 5: Curate and Format Output

Take the top N scored claims (default 12). Ensure diversity:
- At least 3 claim types represented (positive, negative, exploration)
- At least 5 different peptides
- At least 5 different conditions
- If the top N is too homogeneous, swap lower-ranked claims in for diversity

### Output Format

For each curated claim, output:

```
### #N | CLAIM_TYPE | Peptide → Condition
**Source:** [platform/community]
**Skill input:** "[natural language claim formatted as input for peptide-investigator]"
**Why optimal:** [1 sentence — why this is a good test case]
**Score:** [total points] (specificity: X, language: X, engagement: X, relevance: X, clarity: X)
```

The **Skill input** field is critical — it should be written as a natural sentence that a real user might send to the peptide-investigator, e.g.:
- "investigate this: someone on r/Peptides says BPC-157 healed their torn ACL in 3 weeks"
- "is this legit: a user on r/Retatrutide reports emotional blunting at 12mg"

### Summary Table

After all claims, include:

```
## Coverage
- **Peptides:** [list]
- **Conditions:** [list]
- **Claim types:** Positive: N, Negative: N, Exploration: N
- **Platforms scraped:** [list]
- **Funnel:** X scraped → Y filtered → Z curated
```

## Step 6: Save Report

Save the full report to `/workspace/group/YYYY-MM-DD-claim-scrape-[platform].md`.

Report back to the user with:
1. The curated claims (full output)
2. The file location
3. A note that they can send any of the "Skill input" lines directly to trigger an investigation

## Error Handling

- `APIFY_TOKEN not found` → ask user to set up `.env`
- Actor not found or rental required → search for alternative actors via `mcpc search-actors`
- No results → broaden queries, try different time ranges
- Too few claims after filtering → lower the noise filter thresholds
