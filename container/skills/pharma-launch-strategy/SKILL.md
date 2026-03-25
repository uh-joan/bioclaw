---
name: pharma-launch-strategy
description: "Pharma commercial launch planning and launch excellence. Launch analog analysis, KOL identification from publication networks, patient journey mapping, demand forecasting, indication sequencing, field force sizing, channel strategy, launch readiness assessment. Use when user mentions launch strategy, commercial launch, launch planning, launch excellence, KOL mapping, key opinion leader, field force, indication sequencing, patient journey, demand forecast, launch analog, launch readiness, or go-to-market pharma."
---

# Pharma Commercial Launch Strategy

Commercial launch planning specialist covering the full journey from regulatory approval to peak sales. Uses clinical trial investigator networks as KOL proxies, publication analysis for thought leader identification, epidemiology data for demand forecasting, and competitive intelligence for launch timing.

## Report-First Workflow

1. **Create report file immediately**: `[drug]_launch_strategy.md`
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update as data is gathered
4. **Final verification**: Ensure no placeholders remain

## When NOT to Use This Skill

- Market access and pricing → use `pharma-market-access`
- Market sizing (epidemiology, TAM) → use `pharma-market-sizing`
- Competitive pipeline monitoring → use `pharma-ci-monitor`
- Financial forecasting/valuation → use `pharma-financial-analyst`
- Regulatory pathway → use `fda-consultant`

## Cross-Reference: Other Skills

- **Pricing and payer strategy** → use pharma-market-access
- **Market size and patient segments** → use pharma-market-sizing
- **Competitive landscape** → use pharma-ci-monitor and competitive-intelligence
- **Patent/exclusivity timing** → use pharma-patent-analyst
- **Deal landscape** → use pharma-bd-intelligence
- **Scenario analysis** → use what-if-oracle

## Available MCP Tools

### `mcp__ctgov__ctgov_data` (ClinicalTrials.gov — KOL & Trial Intelligence)

| Method | Launch strategy use |
|--------|-------------------|
| `search` | Find trials for the drug/indication (investigator networks = KOL proxies) |
| `get_study` | PI name, sites, enrollment — maps KOL influence |

### `mcp__pubmed__pubmed_data` (PubMed — KOL Publication Networks)

| Method | Launch strategy use |
|--------|-------------------|
| `search` | Find top publishers in the therapeutic area (KOL identification) |
| `fetch_details` | Author affiliations, publication frequency, citation context |

### `mcp__openalex__openalex_data` (OpenAlex — Author & Institution Analysis)

| Method | Launch strategy use |
|--------|-------------------|
| `search_works` | Publication volume by author in therapy area |
| `search_authors` | Author h-index, institution, publication count |

### `mcp__fda__fda_data` (FDA — Approval & Label Context)

| Method | Launch strategy use |
|--------|-------------------|
| `search_drugs` | Approval date, indication, formulation |
| `get_drug_label` | Dosing, administration route (field force implications) |

### `mcp__medicare__medicare_data` / `mcp__medicaid__medicaid_data` (Payer Data)

| Method | Launch strategy use |
|--------|-------------------|
| `get_drug_spending` | Revenue trajectory of launch analogs |
| `get_drug_utilization` | Prescription uptake curves for analogs |

---

## Launch Strategy Workflow

### Phase 1: Launch Analog Analysis

```
1. Identify 3-5 launch analogs (similar indication, mechanism, market)
2. Pull Medicare spending trajectories for each analog
3. Map time-to-peak from launch date
4. Identify success factors (indication breadth, convenience, safety profile)
5. Benchmark: fast launch (pembrolizumab) vs slow (initial niche)
```

### Phase 2: KOL Identification & Mapping

```
1. Search ClinicalTrials.gov for PIs in target indication
2. Search PubMed/OpenAlex for top authors by publication volume
3. Cross-reference: PIs who also publish = highest-value KOLs
4. Map by institution, geography, influence tier:
   - Tier 1: National KOLs (>20 publications, multi-site PI, guideline authors)
   - Tier 2: Regional KOLs (10-20 publications, single-site PI)
   - Tier 3: Local KOLs (5-10 publications, sub-investigators)
5. Identify advisory board candidates from Tier 1
```

### Phase 3: Indication Sequencing

```
1. Map all potential indications (approved + pipeline)
2. For each indication, assess:
   - Patient population size (pharma-market-sizing)
   - Competitive intensity (pharma-ci-monitor)
   - Evidence strength (clinical-trial-analyst)
   - Payer willingness (pharma-market-access)
3. Sequence: lead indication → first-line expansion → adjacent indications
4. Consider label breadth strategy (broad vs narrow initial indication)
```

### Phase 4: Patient Journey & Channel Strategy

```
1. Map the patient journey: symptoms → diagnosis → treatment decision → access → adherence
2. Identify bottlenecks (diagnostic delay, specialist referral, prior auth)
3. Channel strategy:
   - Physician-administered: buy-and-bill, specialty distributor
   - Self-administered: specialty pharmacy, hub services
   - Oral: retail pharmacy, mail order
4. Patient support program design (copay assistance, adherence)
```

### Phase 5: Demand Forecasting

```
1. Epidemiology base: incidence × diagnosis rate × treatment rate × market share
2. Launch curve shape from analog analysis
3. Month-by-month forecast: Year 1 quarterly, Years 2-5 annual
4. Sensitivity analysis: ±20% on market share, diagnosis rate
5. Peak sales estimate with confidence range
```

### Phase 6: Launch Readiness Assessment

```
Readiness dimensions (score 1-5 each):
- Regulatory: approval timeline confidence
- Clinical: evidence package completeness
- Commercial: field force readiness, KOL engagement
- Market access: payer strategy, formulary positioning
- Supply chain: manufacturing, distribution
- Medical affairs: publication plan, MSL deployment
- Patient support: hub services, copay programs

Overall readiness: mean score ≥ 4.0 = GO, 3.0-4.0 = conditional, < 3.0 = delay
```

## Completeness Checklist

- [ ] Launch analogs identified with revenue trajectories
- [ ] KOL landscape mapped (Tier 1/2/3 with institutions)
- [ ] Indication sequencing recommended with rationale
- [ ] Patient journey mapped with bottlenecks identified
- [ ] Channel strategy selected (buy-and-bill / specialty / retail)
- [ ] Demand forecast built with sensitivity analysis
- [ ] Launch readiness scored across all dimensions
- [ ] Geographic launch order aligned with market access strategy
