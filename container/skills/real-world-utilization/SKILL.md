---
name: real-world-utilization
description: >
  Real-world drug utilization from Medicare Part D/B and Medicaid claims.
  Prescriber specialty breakdown, spending trends, geographic hotspots,
  NADAC acquisition pricing, ASP reimbursement, drug interactions, FDA safety
  context, and competitive switching analysis. Use when user mentions prescribing
  data, utilization, Part D, Part B, Medicaid, who prescribes, drug spending,
  NADAC, ASP, real-world, claims data, prescriber analysis, geographic breakdown.
category: market-analysis
mcp_servers:
  - medicare-mcp-server
  - medicaid-mcp-server
  - nlm-mcp-server
  - drugbank-mcp-server
  - fda-mcp-server
complexity: moderate
execution_time: "30-60 seconds"
version: "1.2"
---

# Real-World Drug Utilization Analysis

> **Executable script**: Run via `python3 scripts/get_real_world_utilization_analysis.py semaglutide`

Real-world drug utilization from Medicare Part D/B and Medicaid claims data.
Prescriber specialty breakdown, spending trends, geographic hotspots, NADAC
acquisition pricing, ASP reimbursement, drug interactions, and FDA safety context.

**Ported from riot-flames** with BioClaw MCP client adapter.

## Usage

```bash
python3 scripts/get_real_world_utilization_analysis.py semaglutide
python3 scripts/get_real_world_utilization_analysis.py tirzepatide --top-states=15
python3 scripts/get_real_world_utilization_analysis.py metformin --skip-medicaid
python3 scripts/get_real_world_utilization_analysis.py pembrolizumab --skip-nadac
```

## Cross-Reference: Other Skills

- **Drug sales forecast** → use drug-sales-forecasting (revenue projections)
- **Market access** → use pharma-market-access (pricing, payer strategy)
- **Drug safety** → use drug-safety-intelligence (risk matrix)
- **Company earnings** → use company-us-earnings (XBRL segment revenue)

## Completeness Checklist

- [ ] Medicare Part D prescriber analysis (specialty breakdown)
- [ ] Medicare spending trends extracted
- [ ] Geographic hotspots identified (state-level)
- [ ] NADAC acquisition pricing retrieved
- [ ] ASP Part B pricing (for IV/infusion drugs)
- [ ] Medicaid utilization by state
- [ ] Drug interactions from DrugBank
- [ ] FDA safety context (recalls, shortages)
