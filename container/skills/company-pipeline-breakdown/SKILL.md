---
name: company-pipeline-breakdown
description: >
  Comprehensive drug, biologics, and device pipeline analysis for any pharmaceutical
  or medtech company. Shows therapeutic area focus, phase distribution, late-stage
  assets, regulatory status, and collaboration partnerships. Includes M&A attribution
  for acquired company pipelines. Use when user mentions company pipeline, drug
  portfolio, R&D pipeline, late-stage assets, Phase 3 drugs, pipeline analysis,
  device pipeline, or what is [company] developing.
category: competitive-intelligence
mcp_servers:
  - ctgov-mcp-server
  - fda-mcp-server
  - ema-mcp-server
complexity: complex
execution_time: "20-120 seconds (varies by company size)"
version: "1.0.0"
---

# Company Pipeline Breakdown

> **Executable script**: Run directly via `python3 scripts/get_company_pipeline_breakdown.py "Eli Lilly"`

Comprehensive drug and device pipeline analysis for any pharmaceutical or medtech company. Resolves company name variations and M&A relationships, searches ClinicalTrials.gov for all active trials, classifies by therapeutic area and phase, cross-checks FDA/EMA approval status, and identifies collaboration partners.

**Ported from riot-flames** with BioClaw MCP client adapter for container execution.

## Usage

### CLI (Direct Execution)

```bash
# Full analysis (drugs only)
python3 scripts/get_company_pipeline_breakdown.py "Eli Lilly"

# Skip regulatory checks (faster, ~50%)
python3 scripts/get_company_pipeline_breakdown.py "Novo Nordisk" --skip-regulatory

# Include medical devices
python3 scripts/get_company_pipeline_breakdown.py "J&J" --include-devices

# Devices only (medtech companies)
python3 scripts/get_company_pipeline_breakdown.py "Medtronic" --include-devices --no-drugs

# Limit trials analyzed
python3 scripts/get_company_pipeline_breakdown.py "Pfizer" --max-trials=100

# Exclude subsidiaries
python3 scripts/get_company_pipeline_breakdown.py "Bristol Myers Squibb" --no-subsidiaries

# Skip marketed products
python3 scripts/get_company_pipeline_breakdown.py "AstraZeneca" --no-marketed
```

### Python Import

```python
from get_company_pipeline_breakdown import get_company_pipeline_breakdown

result = get_company_pipeline_breakdown("Eli Lilly")
print(f"Total drugs: {result['total_unique_drugs']}")
print(f"Therapeutic areas: {list(result['therapeutic_areas'].keys())}")
print(f"Late-stage pipeline: {len(result['late_stage_pipeline'])} drugs")
```

## When NOT to Use This Skill

- Individual drug deep-dive → use `drug-research`
- Drug financial valuation → use `pharma-financial-analyst`
- Patent landscape → use `pharma-patent-analyst`
- Market sizing → use `pharma-market-sizing`
- Deal analysis → use `pharma-deal-valuation`

## Cross-Reference: Other Skills

- **Company financials** → use pharma-financial-analyst (revenue, stock, SEC filings)
- **Competitive monitoring** → use pharma-ci-monitor (scheduled pipeline tracking)
- **BD intelligence** → use pharma-bd-intelligence (deal landscape, partner screening)
- **Individual drug profile** → use drug-research (full monograph for a single drug)
- **Patent cliff** → use pharma-patent-analyst (LOE timeline, Orange Book)

## Output Structure

```python
{
    'company': str,                    # Normalized company name
    'total_active_trials': int,        # Active drug trials
    'total_unique_drugs': int,         # Distinct drug interventions
    'therapeutic_area_count': int,     # Number of TAs

    'therapeutic_areas': {             # By therapeutic area
        'Oncology': {'trials': int, 'unique_drugs': int, 'phase_breakdown': {...}},
        ...
    },
    'phase_summary': {                 # By clinical phase
        'Phase 1': {'trials': int, 'drugs': int},
        ...
    },
    'late_stage_pipeline': [...],      # Phase 3+ drugs
    'drugs': {...},                    # Drug-level detail
    'collaborations': {...},           # Partnership analysis
    'regulatory_summary': {...},       # FDA/EMA approved counts
    'device_pipeline': {...},          # If --include-devices
    'marketed_products': {...},        # If not --no-marketed
}
```

## Performance

| Company Size | Active Trials | Execution Time |
|--------------|---------------|----------------|
| Small biotech | 10-30 | 15-25 seconds |
| Mid-cap pharma | 50-150 | 30-60 seconds |
| Big pharma | 200-500 | 60-120 seconds |

Use `--skip-regulatory` for ~50% faster results. Use `--max-trials=N` for large pipelines.

## Completeness Checklist

- [ ] Company name resolved (aliases, subsidiaries)
- [ ] ClinicalTrials.gov searched for all active trials
- [ ] Trials classified by therapeutic area and phase
- [ ] Drug interventions extracted and deduplicated
- [ ] FDA/EMA approval status cross-checked (unless skipped)
- [ ] Collaboration partners identified
- [ ] Late-stage pipeline highlighted
- [ ] Device pipeline analyzed (if requested)
