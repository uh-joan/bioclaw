---
name: regulatory-precedent-pathway
description: >
  Regulatory precedent and pathway analysis for any indication + modality.
  Finds approved drug precedents (FDA/EMA), extracts approval pathways,
  pivotal trial designs, regulator-raised issues, maps optimal submission
  strategies. No-Precedent Mode for novel areas. Covers designations
  (Orphan, BTD, Fast Track, PRIME), pediatric obligations, companion dx.
  Use when user mentions regulatory strategy, regulatory pathway, submission
  pathway, precedent analysis, NDA vs 505(b)(2), centralized MAA,
  breakthrough designation, orphan drug, regulatory landscape.
category: regulatory-strategy
mcp_servers:
  - fda-mcp-server
  - ema-mcp-server
  - ctgov-mcp-server
  - nlm-mcp-server
  - opentargets-mcp-server
complexity: complex
execution_time: "30-60 seconds"
version: "1.0.0"
---

# Regulatory Precedent & Pathway Analyzer

> **Executable script**: Run via `python3 scripts/get_regulatory_precedent_pathway.py "MASH" --modality "small molecule"`

Regulatory precedent and pathway analysis for any indication + modality. Finds
approved precedents (FDA/EMA), extracts pathways, pivotal trial designs, and maps
submission strategies. Auto-switches to No-Precedent Mode when few approvals exist.

**Ported from riot-flames** with BioClaw MCP client adapter.

## Usage

```bash
python3 scripts/get_regulatory_precedent_pathway.py "MASH" --modality "small molecule"
python3 scripts/get_regulatory_precedent_pathway.py "obesity" --modality "biologic"
python3 scripts/get_regulatory_precedent_pathway.py "non-small cell lung cancer"
python3 scripts/get_regulatory_precedent_pathway.py "Alzheimer's disease" --no-designations
```

## Cross-Reference: Other Skills

- **FDA regulatory deep-dive** → use fda-consultant
- **Drug pipeline** → use indication-drug-pipeline-breakdown
- **Market access** → use pharma-market-access (pricing after approval)
- **Patent landscape** → use pharma-patent-analyst (IP strategy)

## Completeness Checklist

- [ ] Precedent drugs identified (FDA + EMA)
- [ ] Approval pathways extracted (NDA/BLA/505(b)(2)/MAA)
- [ ] Pivotal trial designs benchmarked
- [ ] Designation eligibility assessed (BTD, Orphan, Fast Track, PRIME)
- [ ] Pediatric obligations mapped (PIP/PREA)
- [ ] Submission strategy recommended by region
