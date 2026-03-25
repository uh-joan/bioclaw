---
name: pharma-market-access
description: "Pharma pricing, reimbursement, and market access strategy. Payer landscape analysis, formulary positioning, HTA evidence planning, value dossier structure, geographic launch sequencing, budget impact modeling, comparator pricing, NICE/ICER assessment frameworks. Use when user mentions market access, pricing strategy, reimbursement, formulary, payer, HTA, health technology assessment, NICE, ICER, value dossier, budget impact, drug pricing, payer landscape, coverage, or launch sequencing."
---

# Pharma Market Access & Pricing Strategy

Pricing, reimbursement, and payer strategy specialist for drug commercialization. Covers US payer landscape (Medicare Part B/D, Medicaid, commercial), EU HTA frameworks (NICE, G-BA, HAS, AIFA), formulary positioning, comparator analysis, budget impact modeling, and geographic launch sequencing.

## Report-First Workflow

1. **Create report file immediately**: `[drug]_market_access_strategy.md`
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update as data is gathered
4. **Final verification**: Ensure no placeholders remain

## When NOT to Use This Skill

- Drug discovery and target validation → use `drug-target-analyst` or `drug-research`
- Clinical trial design → use `clinical-trial-analyst`
- FDA regulatory pathway → use `fda-consultant`
- Competitive pipeline intelligence → use `pharma-ci-monitor`
- Market sizing (epidemiology, TAM) → use `pharma-market-sizing`
- Financial valuation → use `pharma-financial-analyst`

## Cross-Reference: Other Skills

- **Market sizing inputs** → use pharma-market-sizing (epidemiology, patient segments, TAM/SAM)
- **Launch planning** → use pharma-launch-strategy (KOL, field force, channel)
- **Regulatory context** → use fda-consultant (US) or check EMA MCP (EU)
- **Competitive landscape** → use pharma-ci-monitor and competitive-intelligence
- **Clinical evidence** → use clinical-trial-analyst for trial data supporting access

## Available MCP Tools

### `mcp__medicare__medicare_data` (US Medicare — Part B/D Pricing & Coverage)

| Method | Market access use |
|--------|-----------------|
| `search_drugs` | Find drug in Medicare Part B/D coverage |
| `get_drug_spending` | Medicare spending per drug (total, per claim, per beneficiary) |
| `get_drug_utilization` | Prescription volume and trends |
| `get_nadac` | National Average Drug Acquisition Cost (pharmacy benchmark) |
| `get_asp` | Average Sales Price (Part B reimbursement rate) |

### `mcp__medicaid__medicaid_data` (US Medicaid — State Coverage & Rebates)

| Method | Market access use |
|--------|-----------------|
| `search_drugs` | Medicaid drug utilization by state |
| `get_drug_utilization` | State-level Rx volume and spending |
| `get_nadac_pricing` | Pharmacy acquisition cost benchmark |

### `mcp__fda__fda_data` (FDA — Regulatory & Orange Book Context)

| Method | Market access use |
|--------|-----------------|
| `search_drugs` | FDA-approved label (indication, dosing for formulary) |
| `get_drug_label` | Full prescribing information (PI) for formulary review |
| `get_adverse_events` | FAERS safety data (payer safety concerns) |
| `search_orange_book` | Patent/exclusivity status (generic entry timing) |

### `mcp__ema__ema_data` (EMA — EU Market Authorization)

| Method | Market access use |
|--------|-----------------|
| `search_medicines` | EU-authorized medicines and indications |
| `get_medicine_details` | EPAR, therapeutic area, authorization status |

### `mcp__pubmed__pubmed_data` (Literature — HEOR Evidence)

| Method | Market access use |
|--------|-----------------|
| `search` | Search for health economics, cost-effectiveness, QALY studies |
| `fetch_details` | Retrieve abstracts for HEOR evidence synthesis |

### `mcp__ctgov__ctgov_data` (ClinicalTrials.gov — Clinical Evidence)

| Method | Market access use |
|--------|-----------------|
| `search` | Find clinical trials with PRO/QoL endpoints (payer-relevant) |
| `get_study` | Trial design details for evidence gap analysis |

### `mcp__cdc__cdc_data` (CDC — Disease Burden Context)

| Method | Market access use |
|--------|-----------------|
| `search_data` | Disease prevalence and burden data for budget impact models |

---

## Market Access Strategy Workflow

### Phase 1: Competitive Pricing Landscape

```
1. Identify comparator drugs (same class, same indication)
2. Medicare ASP/NADAC for each comparator
3. Medicaid utilization and spending by state
4. Map pricing tiers: WAC, ASP, NADAC, net price estimates
```

### Phase 2: US Payer Landscape Analysis

```
1. Medicare Part B vs Part D coverage (physician-administered vs self-administered)
2. Medicare spending trends for the therapeutic area
3. Medicaid state-level coverage and utilization
4. Commercial payer formulary tier expectations (Tier 2/3/specialty)
5. Prior authorization and step therapy requirements for comparators
```

### Phase 3: Evidence Gap Analysis for HTA

```
1. Search PubMed for existing HEOR evidence (cost-effectiveness, QALYs)
2. Identify clinical trials with PRO/QoL endpoints
3. Map evidence to HTA requirements:
   - NICE: ICER threshold £20K-£30K/QALY
   - G-BA: added therapeutic benefit categories
   - ICER: US value framework thresholds $50K-$200K/QALY
4. Identify gaps requiring additional real-world evidence studies
```

### Phase 4: Value Dossier Structure

```
1. Disease burden and unmet need (epidemiology + clinical)
2. Clinical value proposition (efficacy, safety, convenience)
3. Economic value (cost-effectiveness model, budget impact)
4. Patient value (PRO data, adherence, quality of life)
5. Societal value (productivity, caregiver burden)
```

### Phase 5: Geographic Launch Sequencing

```
1. Assess regulatory timelines by market (US, EU5, Japan, China)
2. Map HTA requirements and timelines per country
3. Reference pricing implications (which markets set benchmarks)
4. Recommended launch order based on:
   - Speed to revenue (US first typically)
   - Reference pricing protection (avoid low-price markets early)
   - HTA evidence readiness
```

---

## Key Frameworks

### NICE Technology Appraisal

| ICER Range | NICE Decision |
|-----------|--------------|
| < £20,000/QALY | Likely recommended |
| £20,000-£30,000/QALY | Consider with strong case |
| > £30,000/QALY | Requires special circumstances (end of life, rare disease) |
| > £50,000/QALY | Highly Specialised Technologies pathway only |

### US Payer Formulary Tiers

| Tier | Coverage | Patient Cost | Access Requirement |
|------|---------|-------------|-------------------|
| Tier 1 (Generic) | Preferred | $0-15 copay | Open |
| Tier 2 (Preferred Brand) | Covered | $25-50 copay | Open or PA |
| Tier 3 (Non-Preferred) | Covered | $50-100 copay | Step therapy + PA |
| Specialty | Covered | 25-33% coinsurance | PA + specialty pharmacy |

## Completeness Checklist

- [ ] Comparator drugs identified with current pricing (ASP, NADAC, WAC)
- [ ] US Medicare Part B/D coverage landscape mapped
- [ ] Medicaid state-level coverage analyzed for key states
- [ ] Commercial payer tier expectations assessed
- [ ] HEOR evidence gaps identified (CE, QoL, PRO)
- [ ] Value dossier sections outlined with available evidence
- [ ] Geographic launch sequence recommended with rationale
- [ ] Budget impact model framework described
- [ ] HTA submission requirements mapped (NICE, G-BA, ICER)
