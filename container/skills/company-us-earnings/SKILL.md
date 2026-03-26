---
name: company-us-earnings
description: >
  Extract business segment and geographic revenue from SEC EDGAR XBRL filings.
  Quarterly time series with YoY/QoQ growth, operating income, margins, R&D spending,
  capital allocation (dividends, buybacks, CapEx, FCF), stock valuation, analyst estimates,
  peer comparison, and revenue reconciliation. Deep-dive into SEC filing narrative text.
  Use when user mentions segment revenue, quarterly earnings, XBRL, SEC filings,
  revenue breakdown, segment margins, capital allocation, or company financials.
category: financial-analysis
mcp_servers:
  - sec-mcp-server
  - financials-mcp-server
complexity: moderate
execution_time: "5-15 seconds per company"
version: "1.3"
---

# Company US Earnings — Segment & Geographic Revenue

> **Executable script**: Run directly via `python3 scripts/get_company_us_earnings.py JNJ`

Extracts detailed business segment and geographic revenue from SEC EDGAR 10-Q/10-K filings using XBRL dimensional analysis. Provides quarterly time series with growth rates, operating income, margins, R&D, capital allocation, stock valuation, analyst estimates, and peer comparison.

**Ported from riot-flames** with BioClaw MCP client adapter. 85% success rate across 30+ tested pharma/biotech/medtech companies.

## Usage

```bash
# Default: 8 quarters of data
python3 scripts/get_company_us_earnings.py JNJ

# 4 quarters
python3 scripts/get_company_us_earnings.py ABT 4

# Division-level granularity
python3 scripts/get_company_us_earnings.py MDT 8 --subsegments

# Deep dive into SEC filing narrative for specific concepts
python3 scripts/get_company_us_earnings.py MDT 4 --deep-dive "PFA,ablation"
```

## Cross-Reference: Other Skills

- **Company pipeline** → use company-pipeline-breakdown (clinical trial pipeline)
- **Deal valuation** → use pharma-deal-valuation (M&A, licensing)
- **Patent cliff** → use pharma-patent-analyst (LOE timeline)
- **Market access** → use pharma-market-access (pricing, payer)

## Completeness Checklist

- [ ] CIK resolved from ticker
- [ ] XBRL dimensional facts extracted
- [ ] Segment revenue time series built with YoY/QoQ growth
- [ ] Geographic revenue breakdown extracted
- [ ] Revenue reconciliation validated (<1% variance)
- [ ] Stock valuation context added (Yahoo Finance)
- [ ] Analyst estimates included
- [ ] Peer comparison generated
