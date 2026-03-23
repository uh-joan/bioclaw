# Pharma BD Intelligence Skill Design

Source: Business Development persona overview (pharma/biotech).

## Problem

BD professionals need to evaluate partnering opportunities (in-license and out-license), research deal history, benchmark deal terms, and rapidly get up to speed on therapeutic areas. The market moves fast — analysis becomes outdated immediately, and deal values keep climbing so negotiation leverage depends on current data.

## Overlap with other proposed skills

| Need | Covered By | Notes |
|---|---|---|
| Competitor pipeline tracking | `pharma-ci-monitor` | Shared need |
| Market sizing / epi | `pharma-market-sizing` | Shared need |
| Competitive landscape deep dive | `competitive-intelligence` | Shared need |
| Deal history / deal comps | **None** | Core gap — unique to BD |
| Partner identification / evaluation | **None** | Core gap — unique to BD |
| "Get smart fast" on a TA | Partial (existing skills can be composed) | Needs an orchestration workflow |
| Out-licensing differentiation narrative | **None** | Unique to BD |

## What's unique to BD (not covered by other skills)

1. **Deal intelligence** — Who partnered with whom, deal terms, deal structure (upfront, milestones, royalties), deal stage, mechanism/indication
2. **Deal comps** — Average deal size for a given mechanism, stage, indication; benchmarking for negotiation
3. **Partner evaluation** — Assess a company's pipeline, capabilities, deal history, financial position as a potential partner
4. **"Get smart fast" orchestration** — Rapidly compose outputs from multiple skills (CI + market sizing + deal landscape) into a single briefing
5. **Out-licensing pitch support** — Competitive differentiation narrative, positioning vs. alternatives

## Proposal: `pharma-bd-intelligence`

On-demand skill for deal landscape research, partner evaluation, and BD-specific strategic analysis.

### Data sources (existing MCP tools)

- **ClinicalTrials.gov** — Pipeline stage, sponsor identification, trial design for asset evaluation
- **FDA / EMA** — Approval status, label differentiation for competitive positioning
- **PubMed / bioRxiv / OpenAlex** — Scientific evidence supporting asset value; KOL identification
- **Open Targets** — Target validation strength, disease association evidence for due diligence
- **DrugBank / ChEMBL** — Mechanism, pharmacology, compound properties for asset comparison

### Data sources (gaps — need new MCP or web search)

- **Deal databases** — No existing MCP. Options:
  - SEC EDGAR filings (10-K, 8-K for public deal terms) — could build MCP
  - PubMed/news for press releases announcing deals
  - Web search as fallback for deal announcements
  - Commercial: Evaluate Pharma, GlobalData, Cortellis (if APIs become available)
- **Company financials** — For partner evaluation (market cap, cash position, burn rate)
- **Patent databases** — USPTO/EPO for IP landscape and exclusivity assessment

### Key workflows

1. **Deal landscape** — Given a mechanism or indication, find all known deals (partnerships, licenses, acquisitions), extract terms where public, and compute deal comp benchmarks
2. **Partner screening** — Given criteria (therapeutic area, capability, geography), identify potential partners by cross-referencing pipeline (ClinicalTrials.gov), publications (OpenAlex), and deal history
3. **Asset due diligence** — Deep evaluation of a specific asset: clinical data, competitive positioning, IP landscape, regulatory path, market opportunity (composes with `competitive-intelligence` + `pharma-market-sizing`)
4. **"Get smart fast" briefing** — Orchestrate a rapid TA overview combining: disease epi, current SOC, pipeline landscape, key competitors, recent deals, unmet need assessment
5. **Out-licensing package** — Generate differentiation narrative: why this asset vs. competitors, supported by clinical data, mechanism differentiation, and market opportunity
6. **Deal comp analysis** — For a proposed deal, find comparable transactions by mechanism, stage, indication, and geography; summarize typical deal structures and value ranges

### Relationship to other skills

```
pharma-ci-monitor (scheduled) ──┐
                                 ├──> pharma-bd-intelligence (composes all three)
pharma-market-sizing (on-demand) ┘
                                 │
competitive-intelligence (deep dive) ─┘
```

- `pharma-ci-monitor` feeds BD with alerts on new deals, competitor moves
- `pharma-market-sizing` provides the market opportunity numbers for asset evaluation
- `competitive-intelligence` provides the detailed landscape for positioning
- `pharma-bd-intelligence` adds the deal/partner layer and orchestrates the "get smart fast" workflow

## Portfolio Strategy Extension

Source: Portfolio Strategy persona overview (pharma/biotech). This is the most senior persona — Global Portfolio Managers, VP/Head of Portfolio Strategy. They decide which projects get funded, eliminated, or partnered.

### Why not a separate skill

Business questions are ~90% identical to BD + Market Research + CI. The unique layer is **portfolio-level comparison and prioritization** — ranking multiple assets/opportunities against each other for resource allocation. This is a synthesis/decision workflow, not a new data capability.

### Additional workflows (beyond BD intelligence)

7. **Portfolio comparison matrix** — Given N assets or opportunities, produce a side-by-side comparison: market size, competitive intensity, probability of success, differentiation, time to market, investment required
8. **Go/no-go scoring** — Structured framework for each asset: weighted scoring across clinical, commercial, competitive, and strategic dimensions (composes with `pharma-market-sizing` forecasting workflows)
9. **Digital therapeutics / companion solutions scan** — Identify opportunities or threats from digital health entrants in the therapeutic area (PubMed + ClinicalTrials.gov for digital therapeutics trials)
10. **Portfolio risk heatmap** — Map the portfolio against competitive threats: which assets face the most crowded landscapes, which have the clearest differentiation, which are at risk from competitor advances

### Updated architecture

```
pharma-ci-monitor (scheduled)
  │ alerts on competitor moves
  v
pharma-market-sizing (on-demand)
  │ epi, market size, forecasting
  v
competitive-intelligence (deep dive)
  │ landscape analysis
  v
pharma-bd-intelligence (on-demand, orchestration)
  │ deals, partners, "get smart fast", due diligence
  │ + portfolio strategy workflows (comparison, go/no-go, risk heatmap)
  v
 DECISION MAKER
```

Portfolio strategy doesn't need its own skill — it's the **top of the funnel** that consumes outputs from all the others. The BD intelligence skill is the natural home since BD and Portfolio Strategy share the same decision-making context.

### Open questions

- Best public source for deal terms (SEC EDGAR parsing vs. press release scraping vs. PubMed)
- Whether to build a dedicated SEC EDGAR MCP for pharma deal extraction
- How to handle confidential deal terms (most real deal data is behind commercial paywalls)
- Whether "get smart fast" should be a standalone workflow or a meta-skill that invokes other skills
- Company financial data source (Yahoo Finance API? SEC filings?)
- How to handle user-defined scoring weights for portfolio comparison (config file? interactive?)
- Whether portfolio views should be maintained as living documents (like CI monitor) or one-off reports
