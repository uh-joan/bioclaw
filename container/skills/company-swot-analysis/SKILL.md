---
name: company-swot-analysis
description: >
  Strategic SWOT analysis for pharmaceutical and biotechnology companies.
  Integrates clinical pipeline (ClinicalTrials.gov), financial data (SEC EDGAR,
  Yahoo Finance), FDA/EMA approved products, patent exclusivity, and market
  performance into evidence-based Strengths, Weaknesses, Opportunities, Threats.
  Use when user mentions company analysis, SWOT, competitive assessment, strategic
  evaluation, pharma company profile, biotech analysis, acquisition target, or
  investment analysis.
category: strategic-analysis
mcp_servers:
  - ctgov-mcp-server
  - sec-mcp-server
  - fda-mcp-server
  - ema-mcp-server
  - financials-mcp-server
complexity: complex
execution_time: "30-60 seconds"
version: "1.2"
---

# Company SWOT Analysis

> **Executable script**: Run directly via `python3 scripts/generate_company_swot_analysis.py "Moderna"`

Strategic SWOT analysis for pharma/biotech companies integrating 5 MCP data sources: clinical pipeline, SEC filings, FDA/EMA products, patent data, and market performance.

**Ported from riot-flames** with BioClaw MCP client adapter.

## Usage

```bash
python3 scripts/generate_company_swot_analysis.py "Moderna"
python3 scripts/generate_company_swot_analysis.py "Pfizer"
python3 scripts/generate_company_swot_analysis.py "Exelixis"
```

## Cross-Reference: Other Skills

- **Company pipeline** → use company-pipeline-breakdown (detailed pipeline)
- **Company earnings** → use company-us-earnings (XBRL segment revenue)
- **Deal valuation** → use pharma-deal-valuation (M&A analysis)
- **Competitive monitoring** → use pharma-ci-monitor (scheduled tracking)

## Completeness Checklist

- [ ] Clinical pipeline data collected (ClinicalTrials.gov)
- [ ] Financial data extracted (SEC EDGAR + Yahoo Finance)
- [ ] FDA/EMA approved products identified
- [ ] Patent exclusivity mapped
- [ ] Market performance analyzed
- [ ] SWOT categories populated with evidence
- [ ] Strategic assessment summarized
