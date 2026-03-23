# Pharma CI Monitor Skill Design

Source: Competitive Intelligence persona overview (pharma/biotech).

## Problem

CI analysts spend enormous time collecting, synthesizing, and updating competitive data across multiple sources. Analysis becomes outdated almost immediately. The core pain is **freshness and automation**, not depth — depth already exists in the `competitive-intelligence` skill.

## Existing Coverage

| Need | Current Skill | Gap |
|---|---|---|
| Competitor pipeline & trials | `competitive-intelligence` | Minimal |
| New competitor identification | `competitive-intelligence` (partial) | Could be more proactive |
| Partnership/deal tracking | None | Significant — no MCP for deal/M&A data |
| Market share / patient share | `competitive-intelligence` (cBioPortal) | No commercial sales data |
| Geographic expansion | `apify-market-research` (partial) | Pharma-specific geo missing |
| Digital health pipeline | None | Gap |
| Anticipating competitor moves | None | Synthesis workflow missing |
| Continuous monitoring | All skills are on-demand | No scheduled updates |

## Proposal: `pharma-ci-monitor`

A scheduled monitoring agent that runs via `task-scheduler`, tracks a defined set of competitors and therapeutic areas, and produces incremental competitive landscape updates.

### Core design

- **Configuration**: User defines a watchlist — competitors (sponsors), therapeutic areas, targets, mechanisms
- **Scheduled runs**: Periodic (daily/weekly) checks across existing MCP tools (ClinicalTrials.gov, FDA, EMA, PubMed, bioRxiv, OpenAlex, Open Targets)
- **Incremental updates**: Writes to a per-group competitive landscape file, appending only changes since last run
- **Change detection**: Flags new trials, status changes, new approvals, new publications, new preprints
- **Alerting**: Sends summary to user's channel when significant changes detected

### Differentiator from `competitive-intelligence`

| `competitive-intelligence` | `pharma-ci-monitor` |
|---|---|
| On-demand deep dives | Scheduled recurring scans |
| Produces one-off reports | Maintains a living landscape file |
| User initiates each query | Agent runs autonomously on schedule |
| Full analysis per request | Lightweight change detection per run |

### Key workflows

1. **Watchlist setup** — User defines competitors, TAs, targets to track
2. **Baseline scan** — Initial landscape snapshot across all sources
3. **Recurring delta scan** — Check each source for changes since last run, write deltas
4. **Alert digest** — Summarize changes and notify via channel (WhatsApp/Telegram/Slack)
5. **Deep dive trigger** — When a significant change is detected, suggest invoking `competitive-intelligence` for full analysis

### Open questions

- Data source for deal/partnership tracking (no existing MCP — may need web search or SEC/press release scraping)
- How to define "significant change" thresholds for alerting
- Storage format for the living landscape file (structured JSON vs readable markdown)
- Whether to integrate commercial data sources (e.g., IQVIA, Evaluate Pharma) if APIs become available
