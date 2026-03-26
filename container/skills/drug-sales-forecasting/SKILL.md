---
name: drug-sales-forecasting
description: >
  Drug sales trajectory prediction with patent cliff modeling. Market sizing (TAM,
  patient population, market share), comparable drug benchmarking, patent/exclusivity
  analysis (Orange Book), generic erosion curves, year-by-year revenue projections
  with base/optimistic/pessimistic scenarios. Use when user mentions drug revenue
  forecast, sales projection, patent cliff, loss of exclusivity, generic erosion,
  drug market sizing, peak sales estimate, or revenue trajectory.
category: financial-analysis
mcp_servers:
  - fda-mcp-server
  - medicare-mcp-server
  - medicaid-mcp-server
  - drugbank-mcp-server
  - ctgov-mcp-server
  - financials-mcp-server
  - sec-mcp-server
  - cdc-mcp-server
complexity: high
execution_time: "60-120 seconds"
version: "1.0.0"
---

# Drug Sales & Patent Cliff Forecasting

> **Executable script**: Run via `python3 scripts/drug_sales_forecasting.py "Ozempic" "obesity"`

Predicts drug sales trajectories using market sizing, comparable drug analysis, and patent cliff (LOE) modeling. Two-phase approach: (1) estimate market potential from epidemiology + spending data, (2) project sales with generic erosion curves.

**Ported from riot-flames** with BioClaw MCP client adapter.

## Usage

```bash
# Basic forecast
python3 scripts/drug_sales_forecasting.py "Ozempic" "obesity"

# With options
python3 scripts/drug_sales_forecasting.py "Keytruda" "non-small cell lung cancer" --years 10
python3 scripts/drug_sales_forecasting.py "Humira" "rheumatoid arthritis" --scenario pessimistic
python3 scripts/drug_sales_forecasting.py "Eliquis" "atrial fibrillation" --no-comparables
```

## Analysis Modules

1. **Drug Resolution** — brand ↔ generic name mapping via FDA/DrugBank
2. **Patent Analysis** — Orange Book expiry dates, exclusivity periods, biologic status
3. **Market Sizing** — TAM from epidemiology (CDC), spending data (Medicare/Medicaid), treatment rates
4. **Comparable Drugs** — benchmarks from similar drugs (same class, mechanism, indication)
5. **Sales Forecast** — year-by-year projections with pre/post-LOE scenarios, generic erosion curves

## Cross-Reference: Other Skills

- **Company-level revenue** → use company-us-earnings (XBRL segment breakdown)
- **Patent landscape** → use pharma-patent-analyst (detailed Orange Book/FTO)
- **Market access** → use pharma-market-access (payer strategy, formulary)
- **Company financials** → use pharma-financial-analyst (stock, peers, rNPV)

## Completeness Checklist

- [ ] Drug identified (brand/generic resolved)
- [ ] Patent/exclusivity dates extracted from Orange Book
- [ ] Market size estimated (TAM, patient population)
- [ ] Comparable drugs identified with spending benchmarks
- [ ] Sales forecast generated with scenarios (base/optimistic/pessimistic)
- [ ] Generic erosion curve modeled (if applicable)
- [ ] Risk factors identified
