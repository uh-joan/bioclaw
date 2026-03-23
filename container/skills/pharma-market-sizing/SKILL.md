---
name: pharma-market-sizing
description: "Disease epidemiology, market sizing, patient segmentation, addressable market estimation, geographic breakdown, revenue forecasting, go/no-go assessment, opportunity scoring. Use when user mentions market size, prevalence, incidence, epidemiology, patient population, addressable market, subpopulation, forecasting, go/no-go, revenue projection, or opportunity assessment."
---

# Pharma Market Sizing & Epidemiology

On-demand disease-level market analysis for pharma and biotech. Combines epidemiological data (CDC, PubMed, cBioPortal) with competitive landscape and payer data to produce addressable market estimates, patient segmentation waterfalls, and opportunity scores. Includes a forecasting extension for go/no-go decisions and revenue projections.

Distinct from **competitive-intelligence** (which compares competitors within a landscape) and **pharma-ci-monitor** (which tracks competitor activity over time). This skill focuses on the market itself — how big is it, who are the patients, and is the opportunity worth pursuing.

## Report-First Workflow

1. **Create report file immediately**: `[disease]_market_sizing_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Cross-reference sources**: When multiple sources give different numbers, show all with citations
6. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Competitive landscape or pipeline tracking → use `competitive-intelligence`
- Ongoing competitive monitoring → use `pharma-ci-monitor`
- Deal landscape, partner evaluation, or due diligence → use `pharma-bd-intelligence`
- Biomarker identification or companion diagnostics → use `biomarker-discovery`
- Clinical trial design or protocol → use `clinical-trial-analyst` or `clinical-trial-protocol-designer`
- Single drug monograph → use `drug-research`
- FDA regulatory pathway → use `fda-consultant`

## Cross-Reference: Other Skills

- **Competitive landscape deep dive** → use competitive-intelligence skill
- **Scheduled competitive monitoring** → use pharma-ci-monitor skill
- **Deal intelligence, partner screening** → use pharma-bd-intelligence skill
- **Biomarker-defined patient stratification** → use biomarker-discovery skill
- **Clinical trial enrollment/population data** → use clinical-trial-analyst skill (population recipes)

---

## Epidemiology Data Strategy

No single source covers all diseases. Use a multi-source approach and cross-reference:

1. **CDC first** (US data): Chronic disease indicators, PLACES, BRFSS, mortality, cancer statistics, diabetes surveillance, heart disease data — structured, reliable, but US-only
2. **PubMed second** (global data): Search for systematic reviews and meta-analyses of incidence/prevalence — covers all diseases and geographies but requires synthesis
3. **cBioPortal third** (oncology-specific): Mutation frequencies across TCGA and MSK-IMPACT datasets for biomarker-defined subpopulation sizing
4. **OpenAlex fourth** (burden-of-disease studies): Search for GBD publications, WHO reports, and large epidemiological studies
5. **ClinicalTrials.gov** (enrollment proxy): Trial enrollment numbers and inclusion/exclusion criteria provide indirect evidence of treatable populations

**When sources disagree**: Present all estimates with citations in a source comparison table. Note the methodology differences (population-based registry vs. claims-based vs. survey-based). Flag which estimate is most relevant for the user's purpose.

**Known data gaps**:
- No GBD (Global Burden of Disease) API — rely on published GBD studies in PubMed/OpenAlex
- No Orphanet MCP — for rare diseases, rely on PubMed prevalence studies and FDA orphan drug designation data
- No commercial claims/RWD data (IQVIA, Komodo, Flatiron) — drug-treated prevalence must be estimated from published treatment pattern studies and Medicare/Medicaid data

---

## Available MCP Tools

### `mcp__cdc__cdc_health_data` (US Epidemiology — Primary)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_chronic_disease_indicators` | Chronic disease prevalence and incidence | `topic`, `question`, `state`, `limit` |
| `get_places_data` | Local health data (county/city level) | `measure`, `state`, `year`, `limit` |
| `get_brfss_data` | Behavioral risk factor survey | `question`, `year`, `state`, `limit` |
| `get_mortality_data` | Death/mortality statistics by cause | `cause`, `year`, `state`, `limit` |
| `get_cancer_statistics` | Cancer incidence and mortality | `cancer_type`, `state`, `year`, `limit` |
| `get_diabetes_surveillance` | Diabetes prevalence indicators | `indicator`, `state`, `year`, `limit` |
| `get_heart_disease_data` | Heart disease statistics | `indicator`, `state`, `year`, `limit` |
| `get_wonder_data` | CDC WONDER database queries | `query`, `limit` |

**Market sizing usage:**
- `get_chronic_disease_indicators(topic: "[disease]")` → US prevalence and incidence
- `get_places_data(measure: "[disease measure]", state: "[state]")` → geographic variation at county level
- `get_mortality_data(cause: "[disease]")` → burden/severity indicator
- `get_cancer_statistics(cancer_type: "[cancer]")` → oncology incidence/mortality by state
- `get_brfss_data(question: "[risk factor]")` → risk factor prevalence for comorbidity analysis

### `mcp__pubmed__pubmed_data` (Global Epidemiology via Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search PubMed by keywords, MeSH terms | `query`, `num_results` |
| `fetch_details` | Full article metadata including abstract | `pmid` |

**Market sizing queries:**
- `"[disease] epidemiology incidence prevalence systematic review"` → global epi estimates
- `"[disease] burden global"` → GBD study results
- `"[disease] treatment patterns real world"` → drug-treated prevalence
- `"[disease] underdiagnosis"` → diagnosis rate estimation
- `"[disease] [country/region] prevalence"` → regional epi data

### `mcp__pubmed__pubmed_articles` (Date-Filtered Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search with date range | `term`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

**Market sizing queries:**
- Use `search_advanced` with recent date range to find the most current epi estimates

### `mcp__openalex__openalex_data` (Burden-of-Disease Research)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_works` | Search publications by keywords | `query` |
| `get_work` | Publication details by DOI or PMID | `id` |
| `search_topics` | Research topic activity | `query` |

**Market sizing queries:**
- Search for GBD (Global Burden of Disease) publications by disease
- Find highly cited epidemiology reviews and meta-analyses

### `mcp__cbioportal__cbioportal_data` (Oncology Subpopulation Sizing)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_studies` | Cancer cohorts and datasets | `keyword`, `cancer_type` |
| `get_mutation_frequency` | Mutation prevalence in cancer datasets | `study_id`, `gene`, `profile_id` |

**Market sizing workflow:** Query mutation frequencies across TCGA and MSK-IMPACT datasets to size biomarker-defined patient segments (e.g., KRAS G12C prevalence in NSCLC = ~13%, BRAF V600E in melanoma = ~50%).

### `mcp__clinicaltrials__ct_data` (Enrollment & Population Proxy)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_studies` | Search trials by condition, phase | `query`, `status`, `phase`, `limit` |
| `get_study` | Full trial record including enrollment, eligibility | `nct_id` |

**Market sizing usage:**
- Enrollment numbers across Phase 3 trials as proxy for treatable population size
- Inclusion/exclusion criteria define clinical subpopulations
- Number of recruiting trials indicates market activity level

### `mcp__opentargets__ot_data` (Disease-Target Associations)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drug` | Search drugs by name | `query`, `size` |
| `get_drug_info` | Drug details, mechanism, indications | `drug_id` |
| `get_associations` | Evidence-scored target-disease associations | `target_id`, `disease_id`, `size` |

**Market sizing usage:**
- Disease-target associations for biomarker-defined subpopulations
- Genetic evidence strength supports subpopulation biology

### `mcp__fda__fda_data` (Current Standard of Care)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search FDA drug database | `query`, `limit` |
| `get_drug_label` | Full prescribing information | `set_id` or `drug_name` |

**Market sizing usage:**
- Approved labels define current SOC and treated populations
- Label indications show which patient segments are currently addressable
- Orphan drug designations indicate rare disease status and prevalence estimates

### `mcp__ema__ema_data` (EU Market Context)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_medicines` | Search EMA-authorized medicines | `query`, `limit` |
| `get_medicine` | Full EMA product information | `product_id` |

### `mcp__medicare__medicare_info` (US Payer — Pricing & Utilization)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `formulary` | Medicare formulary coverage | query varies |
| `asp_pricing` | Average Sales Price data | query varies |
| `prescriber_data` | Prescriber utilization patterns | query varies |

**Market sizing usage:**
- ASP pricing for current therapies → revenue benchmarking
- Prescriber data → treatment penetration proxy
- Formulary coverage → access landscape

### `mcp__medicaid__medicaid_info` (Medicaid Coverage & Pricing)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `formulary` | Medicaid formulary coverage | query varies |
| `nadac_pricing` | National Average Drug Acquisition Cost | query varies |
| `state_coverage` | State-level coverage data | query varies |
| `utilization_data` | Drug utilization statistics | query varies |

**Market sizing usage:**
- Utilization data → treatment volume proxy for Medicaid population
- NADAC pricing → pricing benchmarks
- State coverage variation → geographic access differences

---

## Workflows

### Workflow 1: Disease Epidemiology Landscape

Produce a comprehensive epidemiology summary for a disease.

**Step 1: US prevalence/incidence (CDC)**
- `get_chronic_disease_indicators(topic: "[disease]")` for prevalence and incidence
- For cancer: `get_cancer_statistics(cancer_type: "[cancer]")`
- For diabetes: `get_diabetes_surveillance(indicator: "prevalence")`
- For cardiovascular: `get_heart_disease_data(indicator: "prevalence")`
- `get_mortality_data(cause: "[disease]")` for mortality burden

**Step 2: Geographic variation (CDC)**
- `get_places_data(measure: "[disease measure]")` for county/city level variation
- Note states/regions with highest and lowest prevalence

**Step 3: Global epidemiology (PubMed)**
- Search: `"[disease] epidemiology prevalence incidence systematic review meta-analysis"`
- Prioritize: Lancet, NEJM, JAMA, BMJ systematic reviews; GBD publications
- Extract: global prevalence, incidence, regional variation, temporal trends

**Step 4: Demographic stratification**
- From CDC data: stratify by age, sex, race/ethnicity where available
- From PubMed: search for `"[disease] age distribution"`, `"[disease] sex differences"`

**Step 5: For oncology — mutation prevalence**
- `search_studies(keyword: "[cancer type]")` in cBioPortal → find relevant datasets
- `get_mutation_frequency(study_id: "[TCGA study]", gene: "[target gene]")` → biomarker prevalence

**Output:** Epidemiology summary table:

| Metric | US | Global | Source |
|--------|-----|--------|--------|
| Prevalence | X per 100K | Y per 100K | CDC / [PMID] |
| Incidence | X/year | Y/year | CDC / [PMID] |
| Mortality | X/year | Y/year | CDC / [PMID] |
| 5-year trend | +/-% | +/-% | CDC / [PMID] |

### Workflow 2: Subpopulation Sizing

Break the patient population into clinically relevant segments.

**Step 1: Define segmentation axes**
- Ask user or infer from context: biomarker, severity, line of therapy, demographic, comorbidity

**Step 2: Biomarker-defined subpopulations**
- For oncology: cBioPortal mutation frequencies (e.g., EGFR mutant NSCLC = ~15% of NSCLC in Western populations)
- For all diseases: PubMed search for `"[disease] [biomarker] prevalence"` and `"[disease] biomarker subtype"`
- Open Targets: `get_associations(disease_id, target_id)` for genetic evidence supporting subpopulation biology

**Step 3: Treatment-line segmentation**
- ClinicalTrials.gov: Search for trials with `"first line"`, `"second line"`, `"refractory"` in titles/descriptions
- PubMed: Search for `"[disease] treatment patterns"` and `"[disease] lines of therapy"`
- FDA labels: Check approved indications for line-of-therapy restrictions

**Step 4: Severity segmentation**
- PubMed: Search for `"[disease] severity classification"` and `"[disease] staging"` for standard grading systems
- Clinical trial eligibility criteria often define severity cutoffs

**Step 5: Compute subpopulation sizes**
- Total prevalence (from Workflow 1) x subpopulation % = subpopulation size
- Build a segmentation waterfall

**Output:** Segmentation waterfall:

```
Total prevalence:           1,000,000 patients (US)
├─ Diagnosed:                 800,000 (80% diagnosis rate)
│  ├─ Biomarker+:             200,000 (25% of diagnosed)
│  │  ├─ Treatment-eligible:  160,000 (80% eligible)
│  │  │  ├─ 1L addressable:   120,000 (75% 1L)
│  │  │  └─ 2L+ addressable:   40,000 (25% 2L+)
│  │  └─ Ineligible:           40,000 (20%)
│  └─ Biomarker-:             600,000 (75%)
└─ Undiagnosed:               200,000 (20%)
```

### Workflow 3: Addressable Market Estimation

Calculate the addressable patient population and market value.

**Step 1: Diagnosed prevalence**
- From Workflow 1 epi data
- Adjust for diagnosis rate (PubMed: `"[disease] underdiagnosis rate"`, `"[disease] diagnostic delay"`)

**Step 2: Treatment rate**
- PubMed: `"[disease] treatment rate"`, `"[disease] treatment patterns real world"`
- Medicare prescriber data for treatment penetration in relevant drug classes
- Medicaid utilization data for treated population volume

**Step 3: Target subpopulation**
- From Workflow 2 segmentation waterfall
- Apply biomarker, severity, and line-of-therapy filters

**Step 4: Addressable patients**
- Addressable = Diagnosed prevalence x treatment rate x target subpopulation %

**Step 5: Market value estimation**
- Current market: count approved therapies x ASP pricing (Medicare ASP data) x estimated utilization
- For new entrant: addressable patients x assumed price x assumed uptake (user-supplied or benchmark)

**Step 6: Geographic breakdown**
- US: CDC PLACES data for state/county variation
- EU/global: PubMed regional epi studies
- Highlight high-prevalence regions

**Output:** Market sizing pyramid with step-by-step calculations and source citations.

### Workflow 4: Competitive Share Mapping

Overlay competitive data onto the sized market.

**Step 1: Current SOC**
- FDA: `search_drugs(query: "[disease]")` → approved therapies
- FDA: `get_drug_label(drug_name: "[drug]")` → approved indications, patient populations

**Step 2: Pipeline entrants**
- ClinicalTrials.gov: `search_studies(query: "[disease]", phase: "PHASE3")` → near-term competition
- Organize by phase: Filed/Approved, Phase 3, Phase 2, Phase 1

**Step 3: Market share overlay**
- Map: addressable patients (from Workflow 3) vs. number of approved products vs. pipeline entrants by phase
- Estimate share fragmentation based on number of competitors

**Output:** Table showing addressable market, current products, pipeline, and competitive intensity score.

### Workflow 5: Opportunity Scoring

Score the commercial opportunity.

**Dimensions:**
1. **Market size** (from Workflow 3): addressable patients and estimated market value
2. **Unmet need**: total prevalence - adequately treated patients; weight by disease severity
3. **Competitive intensity** (from Workflow 4): number of approved and pipeline competitors
4. **Differentiation potential**: is there room for a meaningfully better product? (mechanism novelty, safety advantage, convenience)
5. **Growth trajectory**: is prevalence increasing or decreasing? (from epi trend data)

**Scoring**: 1-5 per dimension, with supporting evidence. Overall opportunity score = weighted average.

**Output:** Opportunity scorecard with evidence-backed scores.

### Workflow 6: Revenue Projection (Forecasting Extension)

Requires user-supplied assumptions. Agent provides the patient numbers.

**Agent provides:**
- Addressable patient population (from Workflow 3)
- Competitive intensity (from Workflow 4)
- Market growth rate (from epi trends)
- Pricing benchmarks (from Medicare/Medicaid data)

**User supplies (or accepts defaults):**
- Price per treatment course
- Expected peak market share %
- Uptake curve shape (linear, S-curve)
- Time to peak (years)

**Projection:**
- Year 1-5 revenue = addressable patients x share(year) x price
- Sensitivity analysis: vary price +/-20%, share +/-20%, addressable population +/-20%

**Output:** Revenue projection table with base case, upside, and downside scenarios.

### Workflow 7: Go/No-Go Framework (Forecasting Extension)

Structured assessment for investment decisions.

| Dimension | Score (1-5) | Evidence |
|-----------|------------|----------|
| Market size | | Addressable patients from Workflow 3 |
| Unmet need | | Gap between prevalence and adequate treatment |
| Competitive landscape | | Number and phase of competitors from Workflow 4 |
| Differentiation | | Mechanism novelty, potential advantages |
| Probability of success | | Target validation from Open Targets, comparable trial outcomes |
| Time to market | | Comparable trial timelines from ClinicalTrials.gov |
| Commercial viability | | Revenue projection from Workflow 6 |

**Overall recommendation:** GO / CONDITIONAL GO / NO-GO with key risks and mitigants.

### Workflow 8: Comorbidity Analysis

Map comorbid conditions that affect the patient population.

**Step 1:** PubMed: `"[disease] comorbidity prevalence"`, `"[disease] comorbid conditions"`
**Step 2:** CDC BRFSS: risk factor co-occurrence data
**Step 3:** Open Targets: overlapping disease-target associations (shared genetic basis)
**Step 4:** Impact assessment: how do comorbidities affect treatment eligibility, drug selection, and market segmentation?

**Output:** Comorbidity profile with prevalence rates and treatment implications.

---

## Output Format Guidance

Market sizing reports should always include:
- **Summary table**: prevalence, incidence, mortality by geography with source citations
- **Segmentation waterfall**: text-based visualization of patient funnel
- **Source comparison table**: when CDC, PubMed, and other sources give different numbers, show all with methodology notes
- **Assumptions log**: every estimate should state the source, year, and any adjustments applied
- **Data gap flags**: explicitly note where estimates rely on indirect evidence or are extrapolated

## Completeness Checklist

- [ ] Epidemiology data from at least 2 independent sources (CDC + PubMed minimum)
- [ ] Sources cross-referenced with discrepancies noted
- [ ] Subpopulations defined with clinical criteria and prevalence percentages
- [ ] Addressable market calculated step-by-step with transparent assumptions
- [ ] Geographic breakdown included (at minimum US vs. global)
- [ ] All assumptions documented with sources and year of data
- [ ] For oncology: cBioPortal mutation prevalence data included
- [ ] Current SOC identified from FDA/EMA approved labels
- [ ] Payer data (Medicare/Medicaid) consulted for pricing and access context
