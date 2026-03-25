---
name: pharma-deal-valuation
description: "Pharma M&A and licensing deal valuation with SEC filing analysis. Deal term extraction from 8-K filings, rNPV with pipeline risk, comparable transaction analysis, milestone and royalty stream modeling, target company due diligence. Use when user mentions deal valuation, pharma M&A, licensing deal, milestone analysis, royalty valuation, deal comps, pharma acquisition, partnership valuation, 8-K deal terms, rNPV deal, or biotech acquisition target."
---

# Pharma Deal Valuation & M&A Analysis

M&A and licensing deal valuation specialist for pharma/biotech. Extracts deal terms from SEC filings, builds risk-adjusted NPV models, performs comparable transaction analysis, and models milestone + royalty streams. Upgrades `pharma-bd-intelligence` with real SEC data and quantitative deal modeling.

## Report-First Workflow

1. **Create report file immediately**: `[deal]_valuation_analysis.md`
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update as data is gathered
4. **Final verification**: Ensure no placeholders remain

## When NOT to Use This Skill

- Strategic BD decisions (partner screening, portfolio fit) → use `pharma-bd-intelligence`
- Company financial profile → use `pharma-financial-analyst`
- Patent/IP landscape → use `pharma-patent-analyst`
- Clinical trial data → use `clinical-trial-analyst`

## Cross-Reference: Other Skills

- **Strategic BD context** → use pharma-bd-intelligence
- **Company financials** → use pharma-financial-analyst
- **Patent/IP valuation** → use pharma-patent-analyst
- **Pipeline risk assessment** → use clinical-trial-analyst
- **Market sizing for deal models** → use pharma-market-sizing

## Available MCP Tools

### `mcp__sec__sec_edgar` (SEC EDGAR — Deal Filings)

| Method | Deal valuation use |
|--------|-------------------|
| `search_companies` | Find target/acquirer by name or ticker |
| `get_company_submissions` | **8-K filings** contain material agreements, deal announcements |
| `get_company_facts` | XBRL financials for target company due diligence |
| `get_dimensional_facts` | Revenue by segment/geography for asset valuation |
| `filter_filings` | Filter for 8-K (deal announcements), DEF 14A (proxy/mergers) |
| `get_company_concept` | Track specific financial concepts over time |

### `mcp__financials__financial_mcp_server` (Yahoo Finance)

| Method | Deal valuation use |
|--------|-------------------|
| `stock_financials` | Target company 3-statement model |
| `stock_estimates` | Analyst consensus (pre-deal expectations) |
| `stock_summary` | Market cap, EV (deal premium analysis) |
| `stock_peers` | Comparable companies for transaction comps |

### Existing MCP Tools

| Tool | Deal valuation use |
|------|-------------------|
| `mcp__ctgov__ctgov_data` | Pipeline phase/status for rNPV probability |
| `mcp__fda__fda_data` | Regulatory designations (BTD, Fast Track = higher PoS) |
| `mcp__opentargets__opentargets_info` | Target-disease validation evidence |
| `mcp__pubmed__pubmed_data` | Clinical evidence supporting asset value |

---

## Deal Valuation Workflow

### Phase 1: Deal Term Extraction (from SEC Filings)

```
1. search_companies → find target and acquirer CIK
2. get_company_submissions → filter for recent 8-K filings
3. Look for "Material Definitive Agreement" or "Merger Agreement" items
4. Extract: upfront payment, milestones (development + commercial + sales),
   royalty rates, royalty term, territory, indication scope
5. For licensing: development cost sharing, opt-in/opt-out rights
```

### Phase 2: Risk-Adjusted NPV (rNPV)

```
For each asset in the deal:
1. Identify current phase from ClinicalTrials.gov
2. Apply Phase-of-Success probabilities:
   Phase 1: 5-10% cumulative, Phase 2: 15-20%, Phase 3: 40-60%
   FDA BTD: +10-15%, Orphan: +5-10%
3. Peak sales estimate from pharma-market-sizing
4. Revenue build: Years 1-3 launch curve, Year 5 peak, Years 10-12 LOE
5. Apply royalty rate from deal terms
6. Discount at WACC (10-12% biotech, 8-10% large pharma)
7. rNPV = Σ(year_revenue × royalty × PoS / (1+WACC)^t)
```

### Phase 3: Comparable Transaction Analysis

```
1. Search SEC 8-K filings for recent pharma deals in same therapy area
2. Identify deal metrics: upfront/total value, upfront as % of total
3. Normalize by phase: Phase 1 deals, Phase 2 deals, Phase 3 deals
4. Calculate multiples: deal value / peak sales estimate
5. Benchmark: is the proposed deal above/below market comps?
```

### Phase 4: Milestone & Royalty Modeling

```
Milestone analysis:
1. List all milestones with triggers and amounts
2. Assign probability to each (IND filing: 80%, Phase 2 success: 30%, etc.)
3. Expected milestone value = Σ(amount × probability)

Royalty analysis:
1. Tiered royalty schedule (e.g., 10% <$500M, 15% >$500M)
2. Apply to annual revenue forecast
3. Account for royalty term expiry (often 10-12 years from launch)
4. NPV of royalty stream at WACC
```

### Phase 5: Deal Premium Analysis (M&A)

```
1. Target stock_summary → pre-announcement market cap
2. Announced deal value / pre-announcement EV = premium %
3. Historical pharma M&A premiums: median 40-60% for biotech targets
4. Justified premium based on rNPV of pipeline assets
5. Accretion/dilution analysis for acquirer (EPS impact)
```

---

## Key Deal Metrics

| Metric | Description | Benchmark |
|--------|------------|-----------|
| Upfront / Total | Cash now vs total potential | Phase 1: 5-15%, Phase 3: 30-50% |
| Deal Value / Peak Sales | Total value vs peak revenue potential | 1.5-3x for pre-revenue |
| Premium to Market Cap | % above pre-deal market cap | Median: 40-60% |
| Royalty Rate | % of net sales | Single-digit (early) to mid-teens (late) |
| Milestone Split | Development vs commercial vs sales | 30/30/40 typical |

## Completeness Checklist

- [ ] Deal terms extracted from SEC 8-K filing
- [ ] Target company financial profile assembled
- [ ] Pipeline rNPV calculated with phase-adjusted PoS
- [ ] Comparable transactions identified and benchmarked
- [ ] Milestone analysis with probability-weighted expected value
- [ ] Royalty stream NPV modeled
- [ ] Deal premium justified (M&A) or deal value assessed (licensing)
- [ ] Risk factors identified (clinical, regulatory, commercial)
