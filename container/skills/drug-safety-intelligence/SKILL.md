---
name: drug-safety-intelligence
description: >
  Comprehensive drug safety intelligence — multi-dimensional risk matrix across
  target biology, FDA/EMA labels, terminated trials, literature, drug interactions,
  and epidemiology. Severity x evidence x reversibility x monitorability scoring.
  Use when user mentions drug safety, safety profile, adverse events, safety liabilities,
  risk matrix, class effects, boxed warning, drug interactions, safety intelligence,
  pharmacovigilance, safety signals, terminated trials, toxicity profile, on-target
  toxicity, or off-target effects.
category: safety-pharmacovigilance
mcp_servers:
  - opentargets-mcp-server
  - fda-mcp-server
  - ema-mcp-server
  - ctgov-mcp-server
  - pubmed-mcp-server
  - biorxiv-mcp-server
  - drugbank-mcp-server
  - chembl-mcp-server
  - cdc-mcp-server
complexity: complex
execution_time: "60-120 seconds"
version: "1.0.0"
---

# Drug Safety Intelligence

> **Executable script**: Run via `python3 scripts/get_drug_safety_intelligence.py "BTK"`

Comprehensive drug safety intelligence answering: "What are the known and emerging
safety liabilities for [drug / target / drug class]?" Produces a multi-dimensional
risk matrix with 4-axis scoring (severity × evidence × reversibility × monitorability)
across 9 MCP servers.

**Ported from riot-flames** with BioClaw MCP client adapter.

## Usage

```bash
# By target (analyzes all drugs hitting that target)
python3 scripts/get_drug_safety_intelligence.py "BTK"
python3 scripts/get_drug_safety_intelligence.py "GLP-1 receptor"

# By drug name
python3 scripts/get_drug_safety_intelligence.py --drug ibrutinib

# By drug class
python3 scripts/get_drug_safety_intelligence.py --drug-class "checkpoint inhibitors"

# With epidemiology context (CDC background rates)
python3 scripts/get_drug_safety_intelligence.py "BTK" --include-epidemiology

# Skip sections for speed
python3 scripts/get_drug_safety_intelligence.py "BTK" --no-literature --no-trials
```

## Analysis Modules

1. **Target Biology** — OpenTargets tissue expression → organ toxicity map, knockout phenotypes
2. **Label Comparison** — FDA labels (BBW/W&P/AR) + EMA, class effect detection (>50% of drugs), outlier identification
3. **Trial Safety Signals** — CT.gov TERMINATED + SUSPENDED trials, safety-reason classification
4. **Literature Synthesis** — PubMed safety publications + bioRxiv preprints (last 2yr)
5. **Drug Interactions** — DrugBank DDI, CYP450, food interactions, polypharmacy risk
6. **Epidemiology Context** — CDC background rates for adverse event contextualization
7. **Risk Matrix** — 4-dimensional scoring with tier classification (HIGH/MODERATE/LOW)

## Risk Matrix Scoring

```
overall = 0.40 × severity + 0.30 × evidence + 0.20 × (1 - reversibility) + 0.10 × (1 - monitorability)
```

Tiers: ≥ 0.7 = HIGH, ≥ 0.4 = MODERATE, < 0.4 = LOW

## Cross-Reference: Other Skills

- **Drug research** → use drug-research (full monograph, not safety-focused)
- **Pharmacovigilance** → use pharmacovigilance-specialist (FAERS signal detection)
- **Drug interactions** → use drug-interaction-analyst (CYP, transporter detail)
- **Company pipeline** → use company-pipeline-breakdown (pipeline context)

## Completeness Checklist

- [ ] Drug/target/class resolved with drug list
- [ ] Target biology analyzed (expression, organ toxicity)
- [ ] FDA/EMA labels compared (class effects vs outliers)
- [ ] Terminated/suspended trials scanned for safety signals
- [ ] Literature synthesized (PubMed + bioRxiv)
- [ ] Drug interactions analyzed (DDI, CYP450, food)
- [ ] Risk matrix scored with tiers and recommendations
- [ ] Full ASCII report generated
