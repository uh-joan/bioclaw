---
name: clinical-trial-landscape
description: >
  Comprehensive clinical trial landscape analysis for a drug or indication.
  Phase distribution, enrollment trends, endpoint selection, geographic spread,
  competitor positioning, and sponsor analysis. Use when user mentions clinical
  trial landscape, trial landscape, phase distribution, enrollment trends,
  trial endpoints, trial sponsors, trial geography, competitor trials,
  clinical development overview, or active trials for [drug/disease].
category: clinical-development
mcp_servers:
  - ctgov-mcp-server
  - pubmed-mcp-server
  - opentargets-mcp-server
complexity: complex
execution_time: "45-90 seconds"
version: "1.0.0"
---

# Clinical Trial Landscape Analysis

> **Executable script**: Run via `python3 scripts/get_clinical_trial_landscape.py "semaglutide"`

Comprehensive clinical trial landscape for any drug or indication. Phase breakdown,
enrollment trends, endpoint patterns, geographic distribution, sponsor analysis,
and competitor mapping.

**Ported from riot-flames** with BioClaw MCP client adapter.

## Usage

```bash
python3 scripts/get_clinical_trial_landscape.py "semaglutide"
python3 scripts/get_clinical_trial_landscape.py "non-small cell lung cancer" --query-type indication
python3 scripts/get_clinical_trial_landscape.py "pembrolizumab" --skip-endpoints
python3 scripts/get_clinical_trial_landscape.py "obesity" --skip-sponsors
```

## Cross-Reference: Other Skills

- **Indication pipeline** → use indication-drug-pipeline-breakdown (drug-centric)
- **Company pipeline** → use company-pipeline-breakdown (company-centric)
- **Drug research** → use drug-research (full monograph)
- **Competitive monitoring** → use pharma-ci-monitor

## Completeness Checklist

- [ ] Phase distribution mapped (P1/P2/P3/P4 with YoY trend)
- [ ] Enrollment trends analyzed (total, median, largest trials)
- [ ] Primary endpoints extracted (OS, PFS, ORR patterns)
- [ ] Geographic distribution mapped (US vs EU vs Asia)
- [ ] Top sponsors identified (pharma vs biotech vs academic)
- [ ] Competitors/indications mapped
