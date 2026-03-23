# Pharma Persona Gap Analysis

Cross-reference of pharma/biotech personas against existing NanoClaw skills. Only build new skills where real gaps exist.

## Persona Coverage Summary

| Persona | New Skill Needed? | Rationale |
|---|---|---|
| Competitive Intelligence | **Yes** → `pharma-ci-monitor` | Existing `competitive-intelligence` is on-demand; gap is scheduled monitoring and change detection |
| Market Research / BI | **Yes** → `pharma-market-sizing` | No epi data workflow (incidence, prevalence, subpopulation sizing) |
| Forecasting | **No** — extension of `pharma-market-sizing` | Same data needs, adds projection layer |
| Business Development | **Yes** → `pharma-bd-intelligence` | Deal/partnership data is a real gap; no MCP for deal comps or partner evaluation |
| Portfolio Strategy | **No** — extension of `pharma-bd-intelligence` | Pure synthesis/decision layer consuming other skills |
| Clinical Development | **No** — fully covered | See detailed mapping below |

## Clinical Development — Full Coverage Mapping

| Need | Covered By |
|---|---|
| Mine past protocols | `clinical-trial-analyst` (ClinicalTrials.gov search) |
| Biomarker selection | `biomarker-discovery` (BEST framework, companion dx, validation) |
| Competitor trial tracking | `competitive-intelligence` (pipeline tracking, trial results) |
| Patient segmentation | `clinical-trial-analyst` (population recipes) + `biomarker-discovery` |
| Eligibility criteria mining | `clinical-trial-protocol-designer` (precedent trial mining) |
| Endpoint selection | `clinical-trial-analyst` (endpoint selection, survival analysis) |
| Full protocol design | `clinical-trial-protocol-designer` (NIH/FDA template) |
| Multi-source synthesis | `competitive-intelligence` (PubMed, bioRxiv, OpenAlex, ClinicalTrials.gov) |

**No new skill required.** Existing skills fully cover the Clinical Development persona.

## New Skills To Build

### 1. `pharma-ci-monitor` (scheduled)
- See [pharma-ci-monitor-skill-design.md](pharma-ci-monitor-skill-design.md)
- Gap: automated, recurring competitive landscape monitoring with change detection

### 2. `pharma-market-sizing` (on-demand)
- See [pharma-market-sizing-skill-design.md](pharma-market-sizing-skill-design.md)
- Gap: epidemiology data workflows (incidence, prevalence, drug-treated prevalence, subpopulation sizing)
- Includes forecasting extension (go/no-go, revenue projection, re-forecasting triggers)

### 3. `pharma-bd-intelligence` (on-demand, orchestration)
- See [pharma-bd-intelligence-skill-design.md](pharma-bd-intelligence-skill-design.md)
- Gap: deal/partnership tracking, deal comps, partner evaluation
- Includes portfolio strategy extension (portfolio comparison, risk heatmap)
- Biggest blocker: no public MCP for deal data (SEC EDGAR or press release scraping needed)

## Architecture

```
pharma-ci-monitor (scheduled)
  │ competitor alerts
  v
pharma-market-sizing ←──── clinical-trial-analyst
  │ epi + forecasting       biomarker-discovery
  v                         clinical-trial-protocol-designer
competitive-intelligence    (existing, no changes needed)
  │ deep-dive landscape
  v
pharma-bd-intelligence
  │ deals + portfolio
  v
 DECISION MAKER
```
