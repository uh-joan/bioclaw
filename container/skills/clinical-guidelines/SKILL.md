---
name: clinical-guidelines
description: Clinical practice guideline search and retrieval specialist. Evidence-based guideline matching, multi-source guideline search, pharmacogenomic guideline integration, AGREE II quality assessment, evidence level mapping, guideline comparison. Use when user mentions clinical guideline, practice guideline, treatment guideline, screening guideline, vaccination schedule, CPIC guideline, DPWG guideline, guideline recommendation, evidence level, standard of care, clinical pathway, treatment algorithm, guideline concordance, or guideline comparison.
---

# Clinical Guidelines

Searches and retrieves evidence-based clinical practice guidelines from multiple authoritative sources. Matches guidelines to clinical queries with pharmacogenomic integration. Uses PubMed for guideline literature, FDA for drug-specific regulatory guidance, CDC for public health and screening guidelines, NLM for clinical coding and terminology, and DrugBank for drug information referenced in guidelines.

## Report-First Workflow

1. **Create report file immediately**: `clinical_guidelines_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Clinical decision support, drug selection, and interaction checking → use `clinical-decision-support`
- FDA regulatory detail and drug labeling → use `fda-consultant`
- Pharmacogenomic dosing guidelines (CPIC/DPWG) → use `pharmacogenomics-specialist`
- Disease biology and target context → use `disease-research`
- Precision medicine and patient stratification → use `precision-medicine-stratifier`
- PK/PD modeling and dose optimization → use `clinical-pharmacology`

## Available MCP Tools

### `mcp__pubmed__pubmed_articles` (PRIMARY — Guideline Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search for guidelines | `keywords`, `num_results` |
| `search_advanced` | Filtered guideline search by journal, date, publication type | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details for guideline publications | `pmid` |

### `mcp__fda__fda_info` (Regulatory Guidance)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search FDA-approved drugs | `query`, `limit` |
| `get_drug_label` | Full prescribing information — dosing, contraindications, warnings | `drug_name` |
| `get_adverse_events` | Post-market adverse event reports | `drug_name`, `limit` |
| `search_by_active_ingredient` | Find drugs by active ingredient | `ingredient` |
| `get_drug_interactions` | FDA-reported drug interactions | `drug_name` |
| `get_recalls` | Drug recall history | `query`, `limit` |
| `get_approvals` | Recent drug approvals | `query`, `limit` |
| `search_devices` | Medical device data | `query`, `limit` |

### `mcp__drugbank__drugbank_info` (Drug Information Referenced in Guidelines)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_by_name` | Find drug by name | `query` |
| `get_drug_details` | Full drug profile — mechanism, pharmacodynamics, dosing, toxicity | `drugbank_id` |
| `search_by_target` | All drugs acting on a target | `target`, `limit` |
| `get_drug_interactions` | Drug-drug interactions | `drugbank_id` |
| `get_similar_drugs` | Pharmacologically similar drugs (therapeutic alternatives) | `drugbank_id`, `limit` |
| `get_pathways` | Metabolic/signaling pathways | `drugbank_id` |
| `search_by_category` | Drugs by therapeutic category | `category`, `limit` |
| `search_by_structure` | Structural similarity search | `smiles` or `inchi`, `limit` |
| `search_by_carrier` | Drugs using same carrier protein | `carrier`, `limit` |
| `search_by_transporter` | Drugs using same transporter | `transporter`, `limit` |
| `get_external_identifiers` | Cross-database IDs (PubChem, ChEMBL, KEGG) | `drugbank_id` |

### `mcp__nlm__nlm_ct_codes` (ICD Codes, HPO Vocabulary, Conditions, Rx-Terms)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `icd-10-cm` | ICD-10-CM diagnosis codes | `terms`, `maxList` |
| `icd-11` | ICD-11 diagnosis codes (WHO 2023) | `terms`, `maxList` |
| `rx-terms` | Drug names with strengths/forms | `terms`, `maxList` |
| `loinc-questions` | Lab test codes (LOINC) | `terms`, `maxList` |
| `conditions` | Medical conditions with ICD mappings | `terms`, `maxList` |
| `npi-organizations` | Healthcare organization lookup | `terms`, `maxList` |
| `npi-individuals` | Provider lookup by name/specialty | `terms`, `maxList` |
| `hcpcs-LII` | Procedure/equipment codes | `terms`, `maxList` |
| `ncbi-genes` | Gene information (BRCA1, CYP2D6, etc.) | `terms`, `maxList` |
| `major-surgeries-implants` | Surgical procedure codes | `terms`, `maxList` |
| `hpo-vocabulary` | Human Phenotype Ontology terms | `terms`, `maxList` |

### `mcp__ctgov__ctgov_info` (Trials Supporting Guidelines)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_studies` | Search clinical trials by keyword | `query`, `limit` |
| `get_study_details` | Full trial record | `nct_id` |
| `search_by_condition` | Trials for a disease/condition | `condition`, `limit` |
| `search_by_intervention` | Trials using a drug/treatment | `intervention`, `limit` |

### `mcp__opentargets__opentargets_info` (Disease Context)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `search_diseases` | Search diseases by name/synonym | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId` (Ensembl ID), `diseaseId` (EFO ID), `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes) | `id` (EFO ID) |

### `mcp__chembl__chembl_info` (Drug Mechanism Context)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |
| `get_admet` | ADMET/drug-likeness properties | `chembl_id` |

### `mcp__cdc__cdc_health_data` (Public Health Guidelines, Vaccination, Screening)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_places_data` | Local disease prevalence by county/ZIP | `measure_id`, `state`, `geography_level` |
| `get_brfss_data` | Behavioral risk factors | `dataset_type`, `state` |
| `get_vaccination_coverage` | Vaccination rates by age/vaccine/state | `age_group`, `vaccine_type`, `state` |
| `get_overdose_surveillance` | Overdose monitoring | `drug_type`, `state` |
| `get_respiratory_surveillance` | RSV/COVID/flu surveillance | `virus`, `state` |
| `get_nndss_surveillance` | Notifiable disease tracking | `nndss_disease`, `state` |
| `get_yrbss_data` | Youth risk behaviors | `topic`, `state` |
| `get_birth_statistics` | Birth/preterm data | `indicator`, `state` |
| `get_environmental_health` | Air quality & health impacts | `pollutant`, `state` |
| `get_immunization_schedule` | Recommended immunization schedules | `age_group`, `vaccine` |
| `get_screening_guidelines` | Preventive screening recommendations | `condition`, `age_group`, `sex` |
| `get_travel_health` | Travel health notices and recommendations | `destination`, `disease` |
| `get_sti_surveillance` | STI surveillance data | `sti_type`, `state` |
| `get_chronic_disease_indicators` | Chronic disease indicators by state | `indicator`, `state` |
| `get_cancer_statistics` | Cancer incidence and mortality | `cancer_type`, `state` |
| `get_mortality_data` | Mortality statistics | `cause`, `state`, `age_group` |
| `get_nutrition_data` | Nutrition and physical activity data | `indicator`, `state` |
| `get_maternal_health` | Maternal morbidity/mortality data | `indicator`, `state` |
| `get_hiv_surveillance` | HIV surveillance data | `indicator`, `state` |
| `get_tb_surveillance` | Tuberculosis surveillance data | `indicator`, `state` |
| `get_hepatitis_surveillance` | Viral hepatitis surveillance data | `type`, `state` |

---

## Multi-Source Guideline Search Workflow

### Step 1: Query Multiple Databases (Minimum 3 Sources)

```
1. PubMed — Clinical practice guideline filter:
   mcp__pubmed__pubmed_articles(method: "search_advanced", term: "condition_name clinical practice guideline[pt]", num_results: 20)
   → Retrieve published guidelines, systematic reviews, consensus statements

2. FDA — Drug-specific regulatory guidance:
   mcp__fda__fda_info(method: "get_drug_label", drug_name: "drug_name")
   → FDA-approved labeling with dosing, indications, contraindications

3. CDC — Public health / vaccination / screening:
   mcp__cdc__cdc_health_data(method: "get_screening_guidelines", condition: "condition_name", age_group: "adult")
   → Preventive screening recommendations
   mcp__cdc__cdc_health_data(method: "get_immunization_schedule", age_group: "adult")
   → Current immunization schedule

4. NLM — ICD coding guidance and terminology:
   mcp__nlm__nlm_ct_codes(method: "icd-10-cm", terms: "condition_name", maxList: 10)
   → Standardized coding for the condition
   mcp__nlm__nlm_ct_codes(method: "conditions", terms: "condition_name", maxList: 10)
   → Condition mappings and cross-references
```

### Step 2: Source-Specific Query Optimization

```
PubMed strategy:
- Use MeSH terms + publication type filter: "Practice Guideline[pt]" OR "Guideline[pt]"
- Restrict to major guideline journals: Annals of Internal Medicine, JAMA, BMJ, Lancet, NEJM
- Date filter for most recent guidelines
  mcp__pubmed__pubmed_articles(method: "search_advanced", term: "condition[MeSH] AND practice guideline[pt]", journal: "Annals of Internal Medicine", start_date: "2022/01/01", num_results: 10)

FDA strategy:
- Search drug labels for "INDICATIONS AND USAGE" and "DOSAGE AND ADMINISTRATION"
- Check for REMS, boxed warnings, and PGx biomarker labeling
  mcp__fda__fda_info(method: "get_drug_label", drug_name: "drug_name")
  mcp__fda__fda_info(method: "get_adverse_events", drug_name: "drug_name", limit: 20)

CDC strategy:
- Use specific data endpoints for public health guidelines
- Vaccination coverage data to assess guideline adherence
  mcp__cdc__cdc_health_data(method: "get_vaccination_coverage", age_group: "adult", vaccine_type: "influenza", state: "US")
  mcp__cdc__cdc_health_data(method: "get_screening_guidelines", condition: "colorectal_cancer", age_group: "adult")

NLM strategy:
- Map conditions to ICD codes for guideline context
- Use HPO vocabulary for phenotype-specific guidelines
  mcp__nlm__nlm_ct_codes(method: "hpo-vocabulary", terms: "phenotype_description", maxList: 10)
```

### Step 3: Verify Guideline Currency and Scope

```
1. Check guideline publication date:
   mcp__pubmed__pubmed_articles(method: "get_article_metadata", pmid: "guideline_pmid")
   → Confirm publication year, authoring body, journal

2. Search for updates or superseding guidelines:
   mcp__pubmed__pubmed_articles(method: "search_advanced", term: "condition_name guideline update", start_date: "last_2_years", num_results: 10)

3. Cross-check with active clinical trials (guideline-changing evidence):
   mcp__ctgov__ctgov_info(method: "search_by_condition", condition: "condition_name", limit: 20)
   → Identify phase III/IV trials that may update current guidelines
```

---

## Guideline Quality Assessment (AGREE II Framework)

### AGREE II Domains

| Domain | Assessment Criteria | Score Range |
|--------|-------------------|-------------|
| **1. Scope and Purpose** | Objectives clearly described, clinical question defined, target population specified | 1-7 |
| **2. Stakeholder Involvement** | Multidisciplinary team, patient preferences considered, target users defined | 1-7 |
| **3. Rigor of Development** | Systematic search, evidence selection criteria, evidence-recommendation link, external review, update procedure | 1-7 |
| **4. Clarity of Presentation** | Specific recommendations, management options clearly presented, key recommendations identifiable | 1-7 |
| **5. Applicability** | Implementation facilitators/barriers, resource implications, monitoring criteria | 1-7 |
| **6. Editorial Independence** | Funding body influence, competing interests declared | 1-7 |

### Quality Assessment Workflow

```
1. Retrieve the guideline:
   mcp__pubmed__pubmed_articles(method: "get_article_metadata", pmid: "guideline_pmid")
   → Assess authoring body, journal, publication date

2. Evaluate authoring organization credibility:
   - Professional society (AHA, ASCO, IDSA) → high credibility
   - Government body (USPSTF, NICE, WHO) → high credibility
   - Single institution → moderate credibility
   - Industry-sponsored → potential bias — check editorial independence

3. Check evidence base:
   mcp__pubmed__pubmed_articles(method: "search_advanced", term: "condition systematic review meta-analysis", num_results: 15)
   → Verify systematic reviews underpin the guideline

4. Verify no retraction or correction:
   mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "guideline_title retraction OR correction OR erratum", num_results: 5)
```

---

## Evidence Level Mapping

### Mapping Guideline Recommendations to Evidence Levels

| Level | Evidence Basis | Strength | Example |
|-------|---------------|----------|---------|
| **Level A** | Multiple randomized controlled trials (RCTs) or meta-analysis of RCTs | Strongest — high confidence in effect estimate | ACC/AHA Class I, Level A: beta-blockers post-MI |
| **Level B-R** | Single RCT or high-quality non-randomized studies | Moderate — moderate confidence, randomized | ASCO Category 1: pembrolizumab in PD-L1+ NSCLC |
| **Level B-NR** | Non-randomized studies (observational, cohort, case-control) | Moderate — moderate confidence, non-randomized | Statin use in CKD patients based on cohort data |
| **Level C-LD** | Limited data — case series, registry data | Weak — limited confidence | Rare disease treatment based on case series |
| **Level C-EO** | Expert opinion/consensus | Weakest — consensus without direct evidence | Expert panel recommendation for orphan conditions |

### Evidence Level Assessment Workflow

```
1. Identify the recommendation statement in the guideline:
   mcp__pubmed__pubmed_articles(method: "get_article_metadata", pmid: "guideline_pmid")

2. Search for supporting RCTs:
   mcp__pubmed__pubmed_articles(method: "search_advanced", term: "intervention condition randomized controlled trial[pt]", num_results: 20)
   → Count and assess quality of supporting RCTs

3. Search for supporting meta-analyses:
   mcp__pubmed__pubmed_articles(method: "search_advanced", term: "intervention condition meta-analysis[pt]", num_results: 10)
   → If meta-analysis exists with consistent results → Level A

4. Check trial registry for pivotal trials:
   mcp__ctgov__ctgov_info(method: "search_by_intervention", intervention: "drug_name", limit: 20)
   → Phase III completed trials supporting the recommendation

5. Assign evidence level:
   - Multiple consistent RCTs or robust meta-analysis → Level A
   - Single RCT or well-designed non-randomized study → Level B
   - Limited data (case series, registries) → Level C-LD
   - No direct evidence, expert consensus only → Level C-EO
```

---

## Pharmacogenomic Guidelines Integration (CPIC/DPWG)

### CPIC Guideline Lookup Workflow

```
1. Identify gene-drug pair:
   mcp__nlm__nlm_ct_codes(method: "ncbi-genes", terms: "CYP2D6", maxList: 5)
   → Gene information and identifiers
   mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   → Metabolism enzymes, pharmacokinetics

2. Search for CPIC guideline publication:
   mcp__pubmed__pubmed_articles(method: "search_advanced", term: "CPIC guideline drug_name gene_name", journal: "Clinical Pharmacology and Therapeutics", num_results: 5)
   → Retrieve CPIC guideline publication

3. Check FDA PGx biomarker labeling:
   mcp__fda__fda_info(method: "get_drug_label", drug_name: "drug_name")
   → PGx biomarker information in prescribing label

4. Search for allele definitions and clinical annotations:
   mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "gene_name allele function clinical annotation pharmacogenomics", num_results: 10)
   → Allele function tables and clinical significance

5. Apply dosing guideline based on metabolizer phenotype
```

### DPWG Guideline Workflow

```
1. Search for DPWG recommendation:
   mcp__pubmed__pubmed_articles(method: "search_advanced", term: "DPWG Dutch Pharmacogenetics Working Group drug_name", num_results: 5)
   → DPWG guideline publication

2. Compare CPIC vs DPWG recommendations:
   - Both may exist for same gene-drug pair
   - DPWG sometimes differs from CPIC on dose adjustments
   - Present side-by-side when both available

3. Get drug details for dosing context:
   mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   → Standard dosing, available formulations
   mcp__nlm__nlm_ct_codes(method: "rx-terms", terms: "drug_name", maxList: 10)
   → Available strengths and forms for dose adjustment
```

### Key CPIC Evidence Levels

| Level | Description | Action |
|-------|-------------|--------|
| **1A** | Strong evidence, strong recommendation | Change prescribing (required) |
| **1B** | Strong evidence, moderate recommendation | Change prescribing (recommended) |
| **2A** | Moderate evidence, strong recommendation | Consider changing |
| **2B** | Moderate evidence, moderate recommendation | Consider changing |
| **3** | Weak evidence | Informational only |

---

## Guideline Comparison Framework

### When Multiple Guidelines Disagree

```
1. Retrieve all relevant guidelines:
   mcp__pubmed__pubmed_articles(method: "search_advanced", term: "condition_name clinical practice guideline[pt]", num_results: 30)
   → Collect guidelines from different organizations (e.g., ACC/AHA vs ESC, ASCO vs NCCN)

2. For each guideline, assess:
   - Authoring body and jurisdiction (US vs EU vs WHO)
   - Publication date (most recent)
   - Evidence base cited (same trials interpreted differently?)
   - Patient population scope (general vs subpopulation)

3. Build comparison table:
   | Aspect | Guideline A (Org) | Guideline B (Org) | Guideline C (Org) |
   |--------|------------------|------------------|------------------|
   | Recommendation | ... | ... | ... |
   | Evidence level | ... | ... | ... |
   | Key supporting trial(s) | ... | ... | ... |
   | Publication year | ... | ... | ... |
   | Target population | ... | ... | ... |

4. Check disease context for each recommendation:
   mcp__opentargets__opentargets_info(method: "search_diseases", query: "condition_name")
   mcp__opentargets__opentargets_info(method: "get_disease_details", id: "EFO_xxxxxxx")
   → Understand disease biology context for differing recommendations

5. Identify the pivotal trials that drive divergence:
   mcp__ctgov__ctgov_info(method: "search_by_condition", condition: "condition_name", limit: 30)
   → Find key trials cited differently by competing guidelines
```

### Common Guideline Discordance Scenarios

| Scenario | Example | Resolution Approach |
|----------|---------|---------------------|
| **Different evidence thresholds** | ACC/AHA vs ESC on statin initiation | Compare risk calculators and trial populations |
| **Different population focus** | US vs European hypertension thresholds | Note geographic/ethnic considerations |
| **Newer trial not yet incorporated** | Pre- vs post-landmark trial guidelines | Flag as potentially outdated |
| **Different weighting of harms vs benefits** | Cancer screening age disagreements (USPSTF vs ACS) | Present both with rationale |
| **Pharmacogenomic integration** | CPIC vs DPWG dose recommendations | Note methodology differences, present both |

---

## Clinical Decision Support — Translating Guidelines to Action

### Guideline-to-Action Workflow

```
1. Match patient query to guideline:
   mcp__pubmed__pubmed_articles(method: "search_advanced", term: "condition clinical practice guideline[pt]", num_results: 15)
   → Find most current, highest-quality guideline

2. Identify recommended intervention:
   mcp__drugbank__drugbank_info(method: "search_by_name", query: "recommended_drug")
   mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   → Drug details, dosing, contraindications

3. Check FDA labeling alignment:
   mcp__fda__fda_info(method: "get_drug_label", drug_name: "drug_name")
   → Confirm FDA-approved indication matches guideline recommendation

4. Verify drug-drug interactions:
   mcp__drugbank__drugbank_info(method: "get_drug_interactions", drugbank_id: "DBxxxxx")
   → Check against patient's current medication list

5. Map to ICD codes for documentation:
   mcp__nlm__nlm_ct_codes(method: "icd-10-cm", terms: "condition_name", maxList: 10)
   → Proper coding for guideline-based treatment

6. Check population-level guideline adherence:
   mcp__cdc__cdc_health_data(method: "get_places_data", measure_id: "CONDITION_MEASURE", state: "XX", geography_level: "county")
   → Population disease burden to contextualize recommendation
```

### Vaccination Guideline Workflow

```
1. Retrieve current immunization schedule:
   mcp__cdc__cdc_health_data(method: "get_immunization_schedule", age_group: "adult")
   → CDC-recommended immunization schedule

2. Check vaccination coverage in population:
   mcp__cdc__cdc_health_data(method: "get_vaccination_coverage", age_group: "adult", vaccine_type: "vaccine_name", state: "XX")
   → Current coverage rates

3. Search for guideline updates:
   mcp__pubmed__pubmed_articles(method: "search_advanced", term: "ACIP vaccine_name recommendation", start_date: "2024/01/01", num_results: 10)
   → Recent ACIP recommendations

4. Check for contraindications:
   mcp__drugbank__drugbank_info(method: "search_by_name", query: "vaccine_name")
   mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   → Vaccine product information, contraindications
```

### Screening Guideline Workflow

```
1. Retrieve USPSTF / CDC screening recommendations:
   mcp__cdc__cdc_health_data(method: "get_screening_guidelines", condition: "cancer_type", age_group: "adult", sex: "female")
   → Preventive screening recommendation

2. Search for guideline publication:
   mcp__pubmed__pubmed_articles(method: "search_advanced", term: "USPSTF cancer_type screening recommendation statement", num_results: 10)
   → USPSTF recommendation statement with evidence review

3. Check disease prevalence for risk context:
   mcp__cdc__cdc_health_data(method: "get_cancer_statistics", cancer_type: "breast", state: "XX")
   → Cancer incidence/mortality in relevant population

4. Map screening to procedure codes:
   mcp__nlm__nlm_ct_codes(method: "hcpcs-LII", terms: "screening_procedure", maxList: 10)
   → HCPCS codes for the screening test
```

---

## AGREE II Scoring Reference

### Scaled Domain Scores

```
Domain Score (%) = (Obtained Score - Minimum Possible Score) / (Maximum Possible Score - Minimum Possible Score) x 100

Interpretation:
> 70%  → High quality, recommend for use
50-69% → Moderate quality, recommend with modifications
< 50%  → Low quality, not recommended without substantial revision
```

### Quick Quality Checklist

```
High-quality guideline indicators:
+ Published by recognized professional society or government body
+ Systematic evidence review described
+ GRADE or equivalent evidence grading used
+ Multidisciplinary author panel
+ Conflict of interest statements present
+ Update schedule defined
+ Patient/public input documented
+ External peer review performed

Red flags:
- Single-author or single-institution guideline
- No systematic search methodology described
- Industry-funded without editorial independence statement
- No evidence grading system used
- Published > 5 years ago with no update
- Recommendations not clearly linked to evidence
```

---

## Multi-Agent Workflow Examples

**"What are the current guidelines for managing type 2 diabetes with CKD?"**
1. Clinical Guidelines → Multi-source search (ADA, KDIGO, ACC/AHA), evidence level mapping, guideline comparison table
2. Clinical Decision Support → Drug selection per guidelines (SGLT2i, GLP-1 RA), interaction checking, ICD coding
3. Pharmacogenomics Specialist → PGx considerations for recommended drugs (e.g., CYP2C9 for sulfonylureas)

**"Compare ACC/AHA vs ESC hypertension guidelines"**
1. Clinical Guidelines → Retrieve both guidelines, AGREE II assessment, side-by-side comparison with evidence basis
2. Disease Research → Hypertension pathophysiology context, target-disease associations
3. Precision Medicine Stratifier → Patient subpopulation considerations (race, comorbidities, age)

**"What vaccinations does a 65-year-old need?"**
1. Clinical Guidelines → CDC immunization schedule, ACIP recommendations, screening guidelines by age
2. Clinical Decision Support → Vaccine product information, contraindications, drug interactions
3. FDA Consultant → Vaccine labeling, recent approvals, safety data

**"Find pharmacogenomic dosing guidelines for clopidogrel"**
1. Clinical Guidelines → CPIC and DPWG guideline search, evidence level mapping, comparison
2. Pharmacogenomics Specialist → CYP2C19 metabolizer phenotype interpretation, dosing adjustments, allele function tables
3. FDA Consultant → FDA PGx biomarker labeling for clopidogrel, boxed warning review

**"Are there updated screening guidelines for colorectal cancer?"**
1. Clinical Guidelines → USPSTF, ACS, ACG guideline search, publication date comparison, evidence level assessment
2. Disease Research → Colorectal cancer epidemiology, risk factors, disease burden
3. Clinical Decision Support → ICD coding, HCPCS screening procedure codes, population prevalence data

**"What does the evidence say about PCSK9 inhibitors for hypercholesterolemia?"**
1. Clinical Guidelines → ACC/AHA lipid guidelines, ESC/EAS guidelines, evidence level for PCSK9 inhibitor recommendations
2. Drug Target Analyst → PCSK9 target biology, mechanism of action, bioactivity data
3. Clinical Trial Analyst → Pivotal trials (FOURIER, ODYSSEY), ongoing trials

---

## Completeness Checklist

- [ ] Multiple guideline sources searched (minimum 3: PubMed, FDA, CDC/NLM)
- [ ] Most current guideline version identified and publication date verified
- [ ] Authoring organization credibility assessed (professional society, government body)
- [ ] Evidence level mapped for each recommendation (Level A through C-EO)
- [ ] AGREE II quality assessment performed for primary guideline
- [ ] Guideline discordances identified and presented with rationale
- [ ] Pharmacogenomic guidelines checked where relevant (CPIC/DPWG)
- [ ] Superseding or updated guidelines searched for
- [ ] Guideline recommendations translated to actionable clinical steps
- [ ] ICD codes and clinical terminology mapped for documentation
