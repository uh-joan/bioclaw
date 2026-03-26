---
name: target-landscape-analysis
description: >
  Comprehensive competitive intelligence around a biological target. Genetic
  validation, drug/trial discovery, competitive positioning, safety analysis,
  and white space identification. Target-centric view across all indications,
  companies, and development stages. Use when user mentions target landscape,
  target competitive, target validation, druggability, class effects, target
  safety, who targets, target white space, GLP-1 drugs, PD-1 inhibitors.
category: drug-discovery
mcp_servers:
  - opentargets-mcp-server
  - drugbank-mcp-server
  - ctgov-mcp-server
  - fda-mcp-server
  - ema-mcp-server
complexity: complex
execution_time: "60-90 seconds"
version: "1.0.0"
---

# Target Landscape Analysis

> **Executable script**: Run via `python3 scripts/get_target_landscape_analysis.py GLP1R`

Comprehensive competitive intelligence around a biological target. Genetic
validation from OpenTargets, drug discovery from DrugBank, clinical trial
landscape from ClinicalTrials.gov, regulatory status from FDA/EMA.

**Ported from riot-flames** with BioClaw MCP client adapter.

## Usage

```bash
python3 scripts/get_target_landscape_analysis.py GLP1R
python3 scripts/get_target_landscape_analysis.py "GLP-1 receptor"
python3 scripts/get_target_landscape_analysis.py EGFR --no-phase3
python3 scripts/get_target_landscape_analysis.py PD-1
```

## Cross-Reference: Other Skills

- **Drug-centric safety** → use drug-safety-intelligence
- **Indication pipeline** → use indication-drug-pipeline-breakdown
- **Company pipeline** → use company-pipeline-breakdown
- **Drug target validation** → use drug-target-analyst / drug-target-validator

## Completeness Checklist

- [ ] Target resolved (gene symbol, Ensembl ID)
- [ ] Genetic validation and druggability assessed
- [ ] Drugs targeting this protein identified (DrugBank)
- [ ] Clinical trial landscape mapped (ClinicalTrials.gov)
- [ ] FDA/EMA approval status cross-checked
- [ ] Company positioning analyzed
- [ ] Safety profile summarized (class effects)
- [ ] White space opportunities identified
