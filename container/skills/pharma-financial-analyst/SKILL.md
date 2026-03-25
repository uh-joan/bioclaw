---
name: pharma-financial-analyst
description: "Pharma and biotech financial analysis connecting drug pipeline to stock valuation. Revenue by drug/segment, pipeline rNPV valuation, patent cliff revenue impact, earnings with R&D context, therapeutic area peer comps, commercial launch revenue curves, SEC filing analysis. Use when user mentions pharma financials, biotech valuation, drug revenue, pipeline valuation, rNPV, pharma stock analysis, pharma earnings, R&D spending, pharma peers, patent cliff financial impact, pharma comps, or biotech stock."
---

# Pharma & Biotech Financial Analyst

Pharma/biotech financial analysis specialist connecting drug pipelines to financial performance. Bridges clinical/regulatory milestones to stock valuation, revenue forecasting, and investment thesis construction. Uses real-time financial data (Yahoo Finance), SEC filings (EDGAR), and macro indicators (FRED) alongside existing pharma MCP tools.

## Report-First Workflow

1. **Create report file immediately**: `[company]_financial_analysis.md`
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update as data is gathered
4. **Final verification**: Ensure no placeholders remain

## When NOT to Use This Skill

- Drug mechanism and pharmacology → use `drug-research`
- Clinical trial design → use `clinical-trial-analyst`
- Market access and pricing strategy → use `pharma-market-access`
- BD deal strategy → use `pharma-bd-intelligence`
- Patent landscape → use `pharma-patent-analyst`

## Cross-Reference: Other Skills

- **Deal valuation and M&A** → use pharma-deal-valuation
- **Patent cliff timing** → use pharma-patent-analyst
- **Market sizing inputs** → use pharma-market-sizing
- **Pipeline competitive context** → use pharma-ci-monitor
- **Scenario modeling** → use what-if-oracle

## Available MCP Tools

### `mcp__financials__financial_mcp_server` (Yahoo Finance + FRED)

| Method | Financial analysis use |
|--------|----------------------|
| `stock_profile` | Company overview, sector, industry, employees |
| `stock_summary` | Current price, market cap, P/E, EPS, dividend yield |
| `stock_financials` | Income statement, balance sheet, cash flow (annual/quarterly) |
| `stock_revenue_breakdown` | **Revenue by product/segment and geography** |
| `stock_earnings_history` | EPS history and surprise analysis |
| `stock_estimates` | Analyst consensus: revenue, EPS, growth estimates |
| `stock_recommendations` | Analyst buy/hold/sell ratings |
| `stock_peers` | Industry peer comparison |
| `stock_dividends` | Dividend history and yield |
| `stock_esg` | ESG scores (environmental, social, governance) |
| `stock_technicals` | Moving averages, RSI, momentum |
| `stock_news` | Sentiment-tagged news |
| `stock_screener` | Multi-criteria stock discovery |
| `stock_correlation` | Portfolio correlation matrix |
| `economic_indicators` | GDP, unemployment, inflation, interest rates |
| `market_indices` | S&P 500, NASDAQ, VIX, sector indices |
| `fred_series_search` | Search 800K+ economic data series |
| `fred_series_data` | Historical economic data by series ID |

### `mcp__sec__sec_edgar` (SEC EDGAR — Company Filings)

| Method | Financial analysis use |
|--------|----------------------|
| `search_companies` | Find pharma/biotech companies by name/ticker |
| `get_company_facts` | All XBRL financial data (structured revenues, costs, assets) |
| `get_company_concept` | Single financial concept with historical trend |
| `get_dimensional_facts` | Revenue by geography/segment from XBRL dimensions |
| `get_company_submissions` | Filing history (10-K, 10-Q, 8-K) |
| `get_frames_data` | Cross-company aggregated data for benchmarking |

### Existing MCP Tools (Pharma Context)

| Tool | Financial analysis use |
|------|----------------------|
| `mcp__fda__fda_data` | Approval dates, label changes (catalysts) |
| `mcp__ctgov__ctgov_data` | Pipeline readouts (binary events) |
| `mcp__pubmed__pubmed_data` | Publication catalysts |
| `mcp__medicare__medicare_data` | Drug spending data (revenue validation) |

---

## Financial Analysis Workflow

### Phase 1: Company Financial Profile

```
1. stock_profile → company overview, market cap, industry
2. stock_financials → 3-statement model (income, balance, cash flow)
3. stock_revenue_breakdown → revenue by drug/segment
4. SEC get_company_facts → XBRL financial data for deeper drill
5. stock_estimates → consensus revenue and EPS forecasts
```

### Phase 2: Pipeline Valuation (rNPV)

```
For each pipeline asset:
1. ClinicalTrials.gov → phase, enrollment, expected readout date
2. FDA → any breakthrough/fast track designations
3. Assign probability of success (PoS) by phase:
   - Phase 1→2: 52%, Phase 2→3: 29%, Phase 3→NDA: 58%, NDA→Approval: 90%
   - Oncology: lower (Phase 2: 21%), Rare disease: higher (Phase 2: 38%)
4. pharma-market-sizing → peak sales estimate per indication
5. Discount at WACC (typically 10-12% for biotech)
6. rNPV = Σ(peak_sales × PoS × NPV_factor)
```

### Phase 3: Revenue Analysis

```
1. stock_revenue_breakdown → current revenue by drug
2. SEC get_dimensional_facts → geographic revenue breakdown
3. Medicare get_drug_spending → US drug spending validation
4. Identify revenue concentration risk (>50% from single drug)
5. Map LOE dates from pharma-patent-analyst → revenue cliff timing
```

### Phase 4: Peer Comparison

```
1. stock_peers → identify comparable companies
2. For each peer: stock_summary → market cap, P/E, EV/Revenue
3. stock_financials → R&D spend as % of revenue
4. Compare: pipeline richness (rNPV) vs market valuation
5. Identify over/undervalued companies relative to pipeline
```

### Phase 5: Catalyst Timeline

```
Map upcoming binary events:
1. ClinicalTrials.gov → Phase 3 readout dates
2. FDA → PDUFA dates, advisory committee meetings
3. EMA → CHMP opinion dates
4. Patent expiry → LOE dates from pharma-patent-analyst
5. Commercial milestones → launch in new markets/indications

Score each catalyst: probability × magnitude × timing
```

---

## Key Pharma Financial Metrics

| Metric | Formula | Benchmark |
|--------|---------|-----------|
| R&D % of Revenue | R&D expense / total revenue | Large pharma: 15-20%, Biotech: 50-200% |
| SG&A % of Revenue | SG&A / total revenue | Pre-launch: >100%, Mature: 25-35% |
| Gross Margin | (Revenue - COGS) / Revenue | Branded pharma: 70-85% |
| Operating Margin | Operating income / Revenue | Large pharma: 25-35%, Biotech: negative to 30% |
| Price/Sales (P/S) | Market cap / Revenue | Large pharma: 3-5x, Biotech: 5-20x |
| EV/Revenue | Enterprise value / Revenue | Large pharma: 4-6x, Biotech: varies widely |
| Revenue per Employee | Revenue / FTE count | Pharma: $500K-1.5M |

## Completeness Checklist

- [ ] Company financial profile assembled (3-statement model)
- [ ] Revenue breakdown by drug/segment documented
- [ ] Pipeline rNPV calculated with PoS assumptions
- [ ] Peer comparison with valuation multiples
- [ ] Catalyst timeline with probability-weighted impact
- [ ] Patent cliff / LOE revenue impact assessed
- [ ] R&D productivity metrics computed
- [ ] Geographic revenue concentration analyzed
- [ ] Investment thesis summarized
