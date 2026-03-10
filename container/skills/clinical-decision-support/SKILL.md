---
name: clinical-decision-support
description: Evidence-based clinical decision support specialist. Drug selection, dosing guidance, formulary alternatives, drug interactions, contraindication checking, guideline-based recommendations, clinical coding, population health data. Use when user mentions drug selection, dosing, formulary, drug interaction check, contraindication, clinical guideline, prescribing, ICD code, LOINC, NPI lookup, treatment algorithm, therapeutic substitution, or evidence-based medicine.
---

# Clinical Decision Support

Evidence-based clinical decision support for drug selection, interaction checking, dosing guidance, and population health intelligence. Integrates multiple clinical data sources.

## Report-First Workflow

1. **Create report file immediately**: `clinical_decision_support_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Drug safety signals and adverse event analysis → use `pharmacovigilance-specialist`
- Drug target and mechanism of action analysis → use `drug-target-analyst`
- Clinical trial evidence and study design → use `clinical-trial-analyst`
- Risk-benefit assessment and risk management → use `risk-management-specialist`
- FDA regulatory status and labeling detail → use `fda-consultant`
- Clinical practice guideline search and comparison → use `clinical-guidelines`

## Available MCP Tools

### `mcp__drugbank__drugbank_info` (Drug Information & Interactions)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_by_name` | Find drug by name | `query` |
| `get_drug_details` | Full drug profile — mechanism, pharmacodynamics, dosing, toxicity | `drugbank_id` |
| `get_drug_interactions` | All drug-drug interactions | `drugbank_id` |
| `search_by_indication` | Find drugs for a condition | `query`, `limit` |
| `search_by_target` | Drugs acting on same target | `target`, `limit` |
| `get_similar_drugs` | Therapeutic alternatives | `drugbank_id`, `limit` |
| `get_pathways` | Metabolic pathways (CYP450 interactions) | `drugbank_id` |
| `search_by_category` | Drugs by therapeutic class | `category`, `limit` |
| `get_products` | Market products, approval status | `drugbank_id`, `country` |
| `search_by_halflife` | Find drugs by elimination half-life | `min_hours`, `max_hours`, `limit` |
| `search_by_carrier` | Drugs sharing carrier protein | `carrier`, `limit` |
| `search_by_transporter` | Drugs sharing transporter | `transporter`, `limit` |
| `search_by_atc_code` | Drugs by ATC classification | `code`, `limit` |

### `mcp__fda__fda_info` (FDA Labeling & Safety)

| Call | What it does |
|------|-------------|
| `method: "lookup_drug", search_type: "label"` | Prescribing information — dosing, contraindications, warnings |
| `method: "lookup_drug", search_type: "adverse_events"` | FAERS adverse event reports |
| `method: "lookup_drug", search_type: "shortages"` | Drug shortage tracking |
| `method: "search_orange_book"` | Therapeutic equivalence (generic substitution) |
| `method: "get_therapeutic_equivalents"` | TE-rated generic alternatives |
| `method: "get_patent_exclusivity"` | Patent/exclusivity status (generic availability) |

### `mcp__nlm__nlm_ct_codes` (Clinical Coding & Terminology)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `icd-10-cm` | Diagnosis codes | `terms`, `maxList` |
| `icd-11` | ICD-11 diagnosis codes (WHO 2023) | `terms`, `maxList` |
| `rx-terms` | Drug names with strengths/forms | `terms`, `maxList` |
| `loinc-questions` | Lab test codes (LOINC) | `terms`, `maxList` |
| `conditions` | Medical conditions with ICD mappings | `terms`, `maxList` |
| `npi-organizations` | Healthcare organization lookup | `terms`, `maxList` |
| `npi-individuals` | Provider lookup by name/specialty | `terms`, `maxList` |
| `hcpcs-LII` | Procedure/equipment codes | `terms`, `maxList` |
| `ncbi-genes` | Gene information (BRCA1, TP53) | `terms`, `maxList` |
| `major-surgeries-implants` | Surgical procedure codes | `terms`, `maxList` |
| `hpo-vocabulary` | Human Phenotype Ontology terms | `terms`, `maxList` |

### `mcp__hpo__hpo_data` (Human Phenotype Ontology)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_hpo_terms` | Search phenotype terms for clinical feature coding | `query`, `max`, `category` |
| `get_hpo_term` | Get full phenotype term details and cross-references | `id` (HP:XXXXXXX) |
| `get_hpo_children` | Browse more specific phenotype subtypes | `id` |
| `validate_hpo_id` | Verify HPO ID is valid | `id` |
| `batch_get_hpo_terms` | Resolve multiple phenotype terms at once | `ids` |

### `mcp__cdc__cdc_health_data` (Population Health)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_places_data` | Local disease prevalence by county/ZIP | `measure_id`, `state`, `geography_level` |
| `get_brfss_data` | Behavioral risk factors | `dataset_type`, `state` |
| `get_vaccination_coverage` | Vaccination rates | `age_group`, `vaccine_type`, `state` |
| `get_overdose_surveillance` | Overdose monitoring | `drug_type`, `state` |
| `get_respiratory_surveillance` | RSV/COVID/flu surveillance | `virus`, `state` |
| `get_nndss_surveillance` | Notifiable disease tracking | `nndss_disease`, `state` |
| `get_yrbss_data` | Youth risk behaviors | `topic`, `state` |
| `get_birth_statistics` | Birth/preterm data | `indicator`, `state` |
| `get_environmental_health` | Air quality & health impacts | `pollutant`, `state` |

### `mcp__monarch__monarch_data` (Disease-Phenotype-Gene Associations)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Disease lookup by name or synonym | `query`, `limit` |
| `get_disease_phenotypes` | Expected phenotypes for a disease (differential diagnosis support) | `disease_id` |
| `get_disease_genes` | Genes associated with a disease | `disease_id` |

**Monarch workflow:** Use Monarch to look up disease-phenotype associations for differential diagnosis support.

```
1. mcp__monarch__monarch_data(method: "search", query: "DISEASE_NAME")
   → Resolve disease to Monarch ID

2. mcp__monarch__monarch_data(method: "get_disease_phenotypes", disease_id: "MONDO:xxxxxxx")
   → Expected phenotype profile for differential diagnosis

3. mcp__monarch__monarch_data(method: "get_disease_genes", disease_id: "MONDO:xxxxxxx")
   → Associated genes for genetic workup guidance
```

### `mcp__pubmed__pubmed_articles` (Clinical Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick literature search | `keywords`, `num_results` |
| `search_advanced` | Filtered by journal, date, author | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__ema__ema_info` (EU Drug Information)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_medicines` | EU-approved medicines | `active_substance`, `therapeutic_area` |
| `get_supply_shortages` | EU shortage tracking | `active_substance`, `status` |
| `get_pips` | Pediatric Investigation Plans | `active_substance` |

---

## Drug Selection Workflow

### Step 1: Identify Candidates

```
1. mcp__drugbank__drugbank_info(method: "search_by_indication", query: "condition_name", limit: 20)
   → All drugs indicated for this condition

2. mcp__drugbank__drugbank_info(method: "search_by_category", category: "therapeutic_class", limit: 20)
   → Drugs in the relevant class

3. mcp__fda__fda_info(method: "lookup_drug", search_term: "drug_name", search_type: "label")
   → FDA-approved indications, dosing, contraindications
```

### Step 2: Check Interactions

```
1. mcp__drugbank__drugbank_info(method: "get_drug_interactions", drugbank_id: "DBxxxxx")
   → All known DDIs for the candidate drug

2. For each co-medication:
   mcp__drugbank__drugbank_info(method: "search_by_name", query: "co_med_name")
   → Get DrugBank ID
   mcp__drugbank__drugbank_info(method: "get_drug_interactions", drugbank_id: "DByyyyy")
   → Cross-check interactions

3. mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   → Identify CYP450 pathway overlaps with co-medications
```

### Step 3: Assess Safety Profile

```
1. mcp__fda__fda_info(method: "lookup_drug", search_term: "drug_name+AND+serious:1", search_type: "adverse_events", count: "patient.reaction.reactionmeddrapt.exact", limit: 15)
   → Top serious adverse events

2. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   → Toxicity, contraindications, pharmacokinetics

3. mcp__fda__fda_info(method: "lookup_drug", search_term: "drug_name", search_type: "shortages")
   → Is the drug in shortage?
```

### Step 4: Find Alternatives

```
1. mcp__drugbank__drugbank_info(method: "get_similar_drugs", drugbank_id: "DBxxxxx", limit: 10)
   → Pharmacologically similar alternatives

2. mcp__fda__fda_info(method: "get_therapeutic_equivalents", search_term: "drug_name")
   → TE-rated generics (AB-rated substitutable)

3. mcp__fda__fda_info(method: "get_patent_exclusivity", search_term: "drug_name")
   → Generic availability timeline
```

---

## Drug Interaction Checking

### Interaction Severity Classification

| Severity | Description | Action |
|----------|-------------|--------|
| **Contraindicated** | Life-threatening or permanently damaging interaction | Do NOT co-administer |
| **Major** | May be life-threatening or require intervention | Avoid combination or monitor closely |
| **Moderate** | May worsen condition or require dose adjustment | Monitor and adjust as needed |
| **Minor** | Limited clinical significance | Be aware, usually no action needed |

### CYP450 Interaction Analysis

```
1. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   → Identify metabolism enzymes (CYP3A4, CYP2D6, etc.)

2. mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   → Full metabolic pathway

3. Check for enzyme inhibition/induction with co-medications:
   mcp__drugbank__drugbank_info(method: "get_drug_interactions", drugbank_id: "DBxxxxx")

4. mcp__drugbank__drugbank_info(method: "search_by_transporter", transporter: "P-glycoprotein")
   → Transporter-mediated interactions
```

### Common High-Risk Interaction Pairs

| Drug A | Drug B | Mechanism | Risk |
|--------|--------|-----------|------|
| Warfarin | NSAIDs | Anticoagulant + antiplatelet | GI bleeding |
| Warfarin | Fluconazole | CYP2C9 inhibition | Supratherapeutic INR |
| SSRIs | MAOIs | Serotonin accumulation | Serotonin syndrome |
| Methotrexate | NSAIDs | Reduced renal clearance | Methotrexate toxicity |
| Statins | CYP3A4 inhibitors | Impaired statin metabolism | Rhabdomyolysis |
| QTc-prolonging drugs | Other QTc drugs | Additive QT prolongation | Torsades de pointes |
| Digoxin | Amiodarone | P-gp inhibition + CYP3A4 | Digoxin toxicity |

---

## Clinical Coding Workflows

### Diagnosis Coding

```
1. mcp__nlm__nlm_ct_codes(method: "icd-10-cm", terms: "condition description", maxList: 10)
   → ICD-10-CM codes with descriptions

2. mcp__nlm__nlm_ct_codes(method: "conditions", terms: "condition", maxList: 10)
   → Medical conditions with ICD-9/ICD-10 cross-mappings

3. mcp__hpo__hpo_data(method: "search_hpo_terms", query: "clinical_feature", max: 10)
   → Standardize phenotype descriptions to HPO terms for genetic disease coding

4. mcp__hpo__hpo_data(method: "get_hpo_term", id: "HP:XXXXXXX")
   → Get full phenotype details, definition, and cross-references to ICD/SNOMED
```

### Lab Test Ordering

```
1. mcp__nlm__nlm_ct_codes(method: "loinc-questions", terms: "test name", maxList: 10)
   → LOINC codes for lab tests

2. mcp__nlm__nlm_ct_codes(method: "hcpcs-LII", terms: "procedure", maxList: 10)
   → HCPCS procedure codes for billing
```

### Drug Terminology

```
1. mcp__nlm__nlm_ct_codes(method: "rx-terms", terms: "drug name", maxList: 10)
   → Drug name/route pairs with strengths and forms

2. mcp__drugbank__drugbank_info(method: "search_by_atc_code", code: "ATC_CODE", limit: 20)
   → Drugs by WHO ATC classification
```

### Provider/Facility Lookup

```
1. mcp__nlm__nlm_ct_codes(method: "npi-individuals", terms: "doctor name or specialty", maxList: 10)
   → Individual provider NPI lookup

2. mcp__nlm__nlm_ct_codes(method: "npi-organizations", terms: "hospital name", maxList: 10)
   → Organization NPI lookup
```

---

## Population Health Analysis

### Disease Prevalence Assessment

```
1. mcp__cdc__cdc_health_data(method: "get_places_data", measure_id: "DIABETES", state: "CA", geography_level: "county")
   → County-level diabetes prevalence in California

2. mcp__cdc__cdc_health_data(method: "get_brfss_data", dataset_type: "obesity_state", state: "TX")
   → Obesity rates in Texas

3. mcp__cdc__cdc_health_data(method: "get_vaccination_coverage", age_group: "teen", vaccine_type: "hpv", state: "NY")
   → HPV vaccination rates in New York
```

### Surveillance Workflows

```
1. mcp__cdc__cdc_health_data(method: "get_respiratory_surveillance", virus: "combined", state: "FL")
   → Current RSV/COVID/flu activity

2. mcp__cdc__cdc_health_data(method: "get_overdose_surveillance", drug_type: "fentanyl", overdose_geography: "state")
   → Fentanyl overdose trends by state

3. mcp__cdc__cdc_health_data(method: "get_nndss_surveillance", nndss_disease: "hepatitis", state: "PA")
   → Hepatitis case surveillance
```

---

## Therapeutic Decision Trees

### Hypertension (ACC/AHA 2024)

```
Stage 1 (130-139/80-89):
├── Non-Black → ACE inhibitor or ARB
├── Black → CCB or thiazide
└── CKD → ACE inhibitor or ARB

Stage 2 (≥140/90):
├── Start 2-drug combination
├── Preferred: ACE/ARB + CCB or thiazide
└── If uncontrolled on 3 drugs → add spironolactone (resistant HTN)
```

### Type 2 Diabetes (ADA 2024)

```
First-line → Metformin
├── ASCVD or high CV risk → Add GLP-1 RA or SGLT2i
├── Heart failure → Add SGLT2i
├── CKD → Add SGLT2i (if eGFR ≥ 20) or GLP-1 RA
├── Need additional A1c lowering → GLP-1 RA, SGLT2i, DPP-4i, TZD, or insulin
└── Cost concern → Sulfonylurea or TZD
```

### Pain Management (WHO Ladder)

```
Step 1 (Mild) → Non-opioid (acetaminophen, NSAID) ± adjuvant
Step 2 (Moderate) → Weak opioid (tramadol, codeine) ± non-opioid ± adjuvant
Step 3 (Severe) → Strong opioid (morphine, oxycodone) ± non-opioid ± adjuvant
```

---

## Multi-Agent Workflow Examples

**"What's the best treatment for this patient with diabetes and CKD?"**
1. Clinical Decision Support → Drug selection per guidelines, interaction check with current meds, ICD coding
2. Pharmacovigilance Specialist → Safety profiles of candidate drugs in CKD population
3. Clinical Trial Analyst → Latest trial evidence for SGLT2i in CKD

**"Check all interactions for this medication list"**
1. Clinical Decision Support → DrugBank interaction check for all pairs, CYP450 pathway analysis
2. Risk Management Specialist → Risk categorization for identified interactions

**"Help me find a formulary alternative for this shortage drug"**
1. Clinical Decision Support → FDA shortage status, therapeutic equivalents, similar drugs, ATC alternatives
2. FDA Consultant → Orange Book TE ratings, generic availability timeline

**"What's the disease burden in our service area?"**
1. Clinical Decision Support → CDC PLACES prevalence data by county/ZIP, BRFSS behavioral risk factors
2. Clinical Trial Analyst → Active trials recruiting in the area (patient referral opportunities)

---

## Completeness Checklist

- [ ] Drug candidates identified by indication with FDA-approved status confirmed
- [ ] Drug-drug interactions checked for all co-medications (pairwise)
- [ ] CYP450 metabolic pathway overlaps assessed
- [ ] Safety profile reviewed (serious adverse events, contraindications)
- [ ] Therapeutic alternatives identified with TE ratings where applicable
- [ ] Drug shortage status checked for recommended medications
- [ ] ICD-10-CM codes mapped for the condition
- [ ] Guideline-concordant treatment algorithm referenced
- [ ] Population health context provided where relevant (CDC data)
- [ ] Dosing guidance included with special population considerations
