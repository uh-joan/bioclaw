---
name: indication-drug-pipeline-breakdown
description: >
  Active drug pipeline analysis for any indication/disease. Phase breakdown with
  unique drug counts, FDA/EMA approval status, company/sponsor attribution with
  M&A tracking, enrollment data, and competitive landscape visualization. Filters
  for ACTIVE trials only. Use when user mentions indication pipeline, disease
  pipeline, drugs in development for, competitive landscape, phase breakdown,
  recruiting trials, active pipeline, or drug development for [disease].
category: competitive-intelligence
mcp_servers:
  - ctgov-mcp-server
  - fda-mcp-server
  - ema-mcp-server
  - pubchem-mcp-server
  - drugbank-mcp-server
  - nlm-mcp-server
complexity: complex
execution_time: "15-35 seconds"
version: "1.0.0"
---

# Indication Drug Pipeline Breakdown

> **Executable script**: Run via `python3 scripts/get_indication_drug_pipeline_breakdown.py "obesity"`

Active drug pipeline analysis for any disease/indication. Opposite perspective from
company-pipeline-breakdown: this is indication-centric (all companies developing for
one disease) vs company-centric (one company across all diseases).

**Ported from riot-flames** with BioClaw MCP client adapter.

## Usage

```bash
# Full analysis
python3 scripts/get_indication_drug_pipeline_breakdown.py "obesity"

# Sample N trials per phase (faster)
python3 scripts/get_indication_drug_pipeline_breakdown.py "heart failure" 50

# Skip regulatory checks (fastest)
python3 scripts/get_indication_drug_pipeline_breakdown.py "obesity" 20 --skip-regulatory

# Limit regulatory checks to top N drugs
python3 scripts/get_indication_drug_pipeline_breakdown.py "breast cancer" --max-checks=10
```

## Cross-Reference: Other Skills

- **Company-centric pipeline** → use company-pipeline-breakdown (one company, all indications)
- **Drug sales forecast** → use drug-sales-forecasting (revenue projections)
- **Competitive monitoring** → use pharma-ci-monitor (scheduled tracking)
- **Market sizing** → use pharma-market-sizing (epidemiology + TAM)

## Completeness Checklist

- [ ] Indication synonyms resolved via NLM
- [ ] Active trials searched per phase (Phase 1-4)
- [ ] Drug interventions extracted and deduplicated
- [ ] FDA/EMA approval cross-checked (unless skipped)
- [ ] Company/sponsor attribution with M&A tracking
- [ ] Phase breakdown with unique drug counts
- [ ] Competitive landscape visualization generated
