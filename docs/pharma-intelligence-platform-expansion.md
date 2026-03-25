# Pharma Intelligence Platform Expansion

Extending BioClaw from R&D focus to full **discovery → development → commercialization → financial performance** coverage.

## New MCP Servers (3)

| Server | Data Source | Methods | Key capabilities |
|--------|-----------|---------|-----------------|
| `financials-mcp` | Yahoo Finance + FRED | 29 | Stock profile, revenue breakdown, earnings, estimates, ESG, peers, screener, FRED economic data (800K+ series) |
| `sec-mcp` | SEC EDGAR | 10 | Company filings (10-K, 10-Q, 8-K), XBRL financial data, dimensional facts (geography, segment), filing history |
| `patents-mcp` | USPTO | 21 | Patent search (granted + applications), full document text, assignment history, continuity data, transaction history |

## New Skills (5)

### pharma-financial-analyst
**Purpose**: Pharma/biotech financial analysis connecting drug pipeline to stock valuation.
**MCPs**: financials-mcp, sec-mcp + existing (FDA, ClinicalTrials.gov, PubMed, Medicare)
**Workflows**: Revenue by drug/segment, pipeline rNPV valuation, patent cliff revenue impact, earnings analysis with R&D context, therapeutic area peer comps, commercial launch revenue curves.

### pharma-deal-valuation
**Purpose**: M&A and licensing deal analysis with SEC filing deep-dives.
**MCPs**: sec-mcp, financials-mcp + existing (ClinicalTrials.gov, FDA, PubMed, OpenTargets)
**Workflows**: Deal term extraction from 8-K filings, rNPV with pipeline risk, comparable transaction analysis, milestone + royalty stream modeling, target company due diligence.

### pharma-market-access
**Purpose**: Pricing, reimbursement, and payer strategy for drug commercialization.
**MCPs**: existing only (Medicare, Medicaid, FDA, EMA, EU-filings, PubMed, CDC, OpenAlex)
**Workflows**: Payer landscape analysis, formulary positioning, HTA evidence planning, value dossier structure, geographic launch sequencing, budget impact modeling, comparator pricing analysis.

### pharma-launch-strategy
**Purpose**: Commercial launch planning from approval to peak sales.
**MCPs**: existing only (ClinicalTrials.gov, FDA, EMA, PubMed, OpenAlex, Medicare, Medicaid)
**Workflows**: Launch analog analysis, KOL identification (publication networks), patient journey mapping, demand forecasting, channel strategy, launch readiness assessment, field force sizing.

### pharma-patent-analyst
**Purpose**: Drug patent landscape and IP strategy.
**MCPs**: patents-mcp + existing (FDA, ChEMBL, DrugBank, PubMed)
**Workflows**: Patent landscape mapping, LOE/patent cliff timeline, freedom-to-operate assessment, Orange Book patent identification, Paragraph IV analysis, biosimilar entry timing, patent family tracking.

## Skill Cross-Reference Matrix

| New Skill | Enhances | References |
|-----------|----------|-----------|
| pharma-financial-analyst | pharma-market-sizing (adds revenue data) | pharma-deal-valuation, competitive-intelligence |
| pharma-deal-valuation | pharma-bd-intelligence (adds SEC data) | pharma-financial-analyst, pharma-patent-analyst |
| pharma-market-access | pharma-market-sizing (adds payer strategy) | pharma-launch-strategy, clinical-trial-analyst |
| pharma-launch-strategy | pharma-ci-monitor (adds launch planning) | pharma-market-access, pharma-market-sizing |
| pharma-patent-analyst | competitive-intelligence (adds patent detail) | pharma-deal-valuation, pharma-financial-analyst |

## Full Pharma Value Chain Coverage

```
Discovery → Development → Regulatory → Commercial → Financial
    ↓            ↓            ↓            ↓            ↓
drug-target  clinical-    fda-        pharma-      pharma-
-analyst     trial-       consultant   market-      financial-
drug-research analyst                  access       analyst
binder-      clinical-    ema MCP     pharma-      pharma-deal-
discovery    pharmacology              launch-      valuation
                                      strategy
                                                   pharma-
                                                   patent-analyst
```
