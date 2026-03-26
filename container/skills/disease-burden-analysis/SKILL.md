---
name: disease-burden-analysis
description: >
  Epidemiology and disease burden analysis — prevalence, incidence, mortality,
  treatment landscape, unmet need, and health economics. Aggregates CDC, WHO,
  PubMed, ClinicalTrials.gov, Medicare, OpenTargets. Use when user mentions
  disease burden, epidemiology, prevalence, incidence, mortality, unmet need,
  treatment landscape, economic burden, DALY, disease demographics, or disease trends.
category: global-health
mcp_servers:
  - cdc-mcp-server
  - pubmed-mcp-server
  - ctgov-mcp-server
  - medicaid-mcp-server
  - fda-mcp-server
  - opentargets-mcp-server
complexity: moderate
execution_time: "~20 seconds"
version: "1.0.0"
---

# Disease Burden Analysis

> **Executable script**: Run via `python3 scripts/get_disease_burden_analysis.py "obesity"`

Comprehensive epidemiology and disease burden — prevalence, incidence, mortality,
demographic distribution, treatment landscape, unmet need, and economic impact.

**Ported from riot-flames** with BioClaw MCP client adapter.

## Usage

```bash
python3 scripts/get_disease_burden_analysis.py "obesity"
python3 scripts/get_disease_burden_analysis.py "type 2 diabetes" --geography global
python3 scripts/get_disease_burden_analysis.py "MASH" --skip-economics
```

## Cross-Reference

- **Market sizing** → use pharma-market-sizing (TAM/SAM from epi data)
- **Indication pipeline** → use indication-drug-pipeline-breakdown
- **Clinical trial landscape** → use clinical-trial-landscape
- **Launch strategy** → use pharma-launch-strategy (demand forecasting)
