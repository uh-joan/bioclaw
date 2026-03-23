# Pharma Market Sizing & Epidemiology Skill Design

Source: Market Research, Customer Insights, BI and Analytics persona overview (pharma/biotech).

## Problem

Market researchers need to size addressable markets, understand disease epidemiology, segment patient populations, and assess commercial opportunity — all before brand strategy or go-to-market decisions can be made. Current skills cover competitive landscaping and pipeline tracking but not the underlying market fundamentals.

## Existing Coverage

| Need | Current Skill | Gap |
|---|---|---|
| Competitive landscape | `competitive-intelligence` | Covered |
| Pipeline tracking | `competitive-intelligence` | Covered |
| Addressable market sizing | `competitive-intelligence` (cBioPortal, oncology only) | No general epidemiology data |
| Incidence / prevalence / drug-treated prevalence | None | Significant |
| Patient subpopulation sizing | `biomarker-discovery` (partial) | No claims or RWD sources |
| Integrated patient journey | None | Significant |
| Geographic patient distribution | None | No epi geo data |
| Physician targeting / KOL mapping | `competitive-intelligence` (OpenAlex for KOL publications) | No prescriber data |
| Commercial forecasting / Rx data | None | Out of scope without commercial data |
| Brand segmentation / targeting | None | Strategy layer, not data layer |

## Proposal: `pharma-market-sizing`

An on-demand skill for disease-level market analysis — epidemiology, patient flow, subpopulation sizing, and opportunity assessment.

### Data sources (existing MCP tools)

- **PubMed / bioRxiv / OpenAlex** — Epidemiology publications (incidence/prevalence studies, burden-of-disease, patient registries)
- **ClinicalTrials.gov** — Enrollment numbers as proxy for treatable population; trial inclusion/exclusion criteria define subpopulations
- **Open Targets** — Disease-target associations, genetic evidence for subpopulation biology
- **cBioPortal** — Mutation prevalence for oncology market sizing
- **FDA/EMA** — Approved labels define current standard of care and treated populations

### Data sources (gaps that need new MCP or web search)

- **GBD (Global Burden of Disease)** — IHME dataset for incidence/prevalence/DALYs by country
- **WHO / CDC / disease registries** — Public epi data
- **Orphanet** — Rare disease prevalence estimates
- **Claims / RWD** — Would need commercial data (IQVIA, Komodo, Flatiron) for drug-treated prevalence and patient journey

### Key workflows

1. **Disease landscape** — Given a disease, pull incidence, prevalence, and mortality from published epi studies (PubMed search for "epidemiology" + disease + "incidence" + "prevalence")
2. **Subpopulation sizing** — Break the patient population by biomarker, genotype, line of therapy, severity, or demographic using trial enrollment criteria and published subgroup analyses
3. **Addressable market estimation** — Diagnosed prevalence x treatment rate x target subpopulation % = addressable patients
4. **Geographic breakdown** — Regional prevalence differences from published epi studies and GBD data
5. **Competitive share mapping** — Cross-reference with `competitive-intelligence` to overlay approved products and pipeline onto the sized market
6. **Opportunity scoring** — Unmet need = total prevalence - adequately treated patients; weight by severity and available alternatives

### Relationship to other skills

- Composes with `competitive-intelligence` (market sizing + competitive overlay = full strategic picture)
- Composes with `pharma-ci-monitor` (ongoing tracking of how the sized market evolves)
- Composes with `biomarker-discovery` (biomarker-defined subpopulations feed into segmentation)
- Distinct from `drug-research` (single compound focus) and `clinical-trial-analyst` (trial design focus)

## Forecasting Extension

Source: Forecasting persona overview (pharma/biotech). Heavy overlap with Market Research persona — same data needs (market sizing, prevalence, subpopulations) but adds a **modeling and projection layer**.

### Why not a separate skill

The Forecasting persona's business questions are ~80% identical to Market Research. The differentiator is what they do *with* the data: build forecast models, make go/no-go recommendations, re-forecast when market shifts occur. This is better handled as an additional workflow within `pharma-market-sizing` rather than a standalone skill.

### Additional workflows (beyond base market sizing)

6. **Opportunity assessment** — Given sized market + competitive overlay, score opportunity: unmet need x addressable population x competitive intensity x differentiation potential
7. **Go/no-go framework** — Structured assessment: market size, competitive landscape, probability of technical success, time to market, differentiation, commercial viability
8. **Revenue projection** — Addressable patients x expected market share x price assumption x uptake curve. Requires user-supplied pricing/share assumptions; skill provides the patient numbers
9. **Re-forecasting triggers** — When `pharma-ci-monitor` detects a market shift (new competitor approval, failed trial, new entrant), flag for re-forecast and show what changed
10. **Comorbidity analysis** — Use PubMed epi studies and Open Targets disease associations to map comorbid conditions that affect patient segmentation and treatment decisions

### Additional pain points addressed

- "Many data sources — which is source of truth?" — Skill should cross-reference multiple sources and flag discrepancies rather than relying on a single source
- "Continuous re-forecasting" — Ties into `pharma-ci-monitor` scheduled scans; when competitive landscape changes, trigger a market sizing refresh

### Open questions

- Best public data source for general epidemiology (GBD API vs. PubMed mining vs. WHO)
- Whether to build an Orphanet MCP for rare disease prevalence
- How to estimate drug-treated prevalence without commercial claims data
- Output format: structured market model (JSON) vs. narrative report (markdown) vs. both
- How to handle user-supplied assumptions (pricing, share, uptake curves) — config file? interactive prompts?
- Whether forecasting models should be code-generated (Python/R scripts) or narrative-based
