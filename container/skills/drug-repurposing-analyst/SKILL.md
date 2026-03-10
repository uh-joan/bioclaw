---
name: drug-repurposing-analyst
description: Drug repurposing and repositioning specialist. Systematic identification of new therapeutic uses for existing drugs using target-based, compound-based, and disease-driven strategies. Use when user mentions drug repurposing, repositioning, new indication, off-label use, therapeutic switching, drug rescue, phenotypic screening, polypharmacology, or finding new uses for existing drugs.
---

# Drug Repurposing Analyst

Systematic identification of repurposing candidates using multi-database triangulation. Three complementary strategies scored against a composite framework.

## Report-First Workflow

1. **Create report file immediately**: `[drug_or_disease]_drug-repurposing-analyst_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Target validation and druggability assessment → use `drug-target-analyst`
- Safety profile and adverse event detection → use `pharmacovigilance-specialist`
- Clinical trial design and pipeline intelligence → use `clinical-trial-analyst`
- Regulatory pathway for new indication → use `fda-consultant`
- Chemical safety and ADMET profiling → use `chemical-safety-toxicology`
- Comprehensive drug monograph from scratch → use `drug-research`

## Available MCP Tools

### `mcp__opentargets__opentargets_info`

| Method | Use for repurposing |
|--------|-------------------|
| `search_targets` | Find target Ensembl ID |
| `search_diseases` | Find disease EFO ID |
| `get_target_disease_associations` | Evidence-scored target-disease links (genetic, known drugs, literature) |
| `get_disease_targets_summary` | All validated targets for a disease — find druggable ones |
| `get_target_details` | Tractability, pathways, safety data for a target |
| `get_disease_details` | Disease ontology, phenotypes, known therapeutics |

### `mcp__drugbank__drugbank_info`

| Method | Use for repurposing |
|--------|-------------------|
| `search_by_name` | Find drug DrugBank ID |
| `get_drug_details` | Mechanism, pharmacodynamics, all known indications, toxicity |
| `search_by_indication` | All drugs for an indication (competitor landscape) |
| `search_by_target` | All drugs hitting a target (class repurposing) |
| `get_drug_interactions` | Interaction risks for new patient population |
| `get_similar_drugs` | Structurally/pharmacologically similar drugs |
| `get_pathways` | Metabolic pathways — find pathway-based repurposing opportunities |
| `search_by_category` | Drugs by therapeutic class |
| `get_products` | Market availability, approval status |

### `mcp__chembl__chembl_info`

| Method | Use for repurposing |
|--------|-------------------|
| `compound_search` | Find compound ChEMBL ID |
| `target_search` | Find target ChEMBL ID |
| `get_bioactivity` | Compound activity against new targets (IC50, Ki, EC50) |
| `get_mechanism` | Mechanism of action details |
| `drug_search` | Drugs by indication |
| `get_admet` | Drug-likeness and ADMET for the existing compound |

### `mcp__pubchem__pubchem`

| Method | Use for repurposing |
|--------|-------------------|
| `search_compounds` | Compound lookup by name/CID/SMILES |
| `get_compound_properties` | Molecular properties |
| `search_similar_compounds` | Structural analogs (scaffold-hopping) |
| `get_safety_data` | GHS hazard data |
| `get_patent_ids` | Patent landscape for repurposing freedom-to-operate |

### `mcp__fda__fda_info`

| Method | Use for repurposing |
|--------|-------------------|
| `lookup_drug`, `search_type: "label"` | Current approved indications, off-label signals in W&P |
| `lookup_drug`, `search_type: "adverse_events"` | FAERS — look for unexpected therapeutic effects |
| `get_patent_exclusivity` | IP landscape, exclusivity windows |
| `search_orange_book` | Existing formulations, TE ratings |

### `mcp__pubmed__pubmed_articles` & `mcp__ctgov__ct_gov_studies`

Literature evidence and clinical trial landscape for repurposing candidates.

### DepMap — Cancer Dependency Map

| Tool | Method | Use |
|------|--------|-----|
| `mcp__depmap__depmap_data` | `get_drug_sensitivity` | Drug sensitivity across lineages — find new indications for existing drugs |
| | `get_biomarker_analysis` | Identify genotype-drug sensitivity associations for repurposing |
| | `get_gene_dependency` | Target essentiality in new disease contexts |
| | `get_context_info` | Discover sensitive lineages/subtypes for a drug |
| | `get_multi_gene_profile` | Pathway dependency for mechanism-based repurposing |

### BindingDB — Binding Affinity Data

| Tool | Method | Use |
|------|--------|-----|
| `mcp__bindingdb__bindingdb_data` | `search_by_name` | Find all targets a drug binds — polypharmacology for repurposing |
| | `get_ligands_by_target` | Find existing binders for a new target indication |
| | `search_by_smiles` | Find structurally similar compounds with different indications |

**BindingDB workflow:** Use BindingDB polypharmacology data to discover off-target activities for drug repurposing.

```
mcp__bindingdb__bindingdb_data(method: "search_by_name", name: "drug_name")
mcp__bindingdb__bindingdb_data(method: "get_ligands_by_target", target: "new_target")
mcp__bindingdb__bindingdb_data(method: "search_by_smiles", smiles: "SMILES_STRING")
```

---

## Repurposing Strategies

### Strategy 1: Target-Based (Drug → New Disease)

Start with a known drug's target, find diseases where that target is validated.

```
1. mcp__drugbank__drugbank_info(method: "search_by_name", query: "drug_name")
   → Get DrugBank ID

2. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   → Get primary targets, mechanism of action

3. mcp__opentargets__opentargets_info(method: "search_targets", query: "target_gene")
   → Get Ensembl ID for the drug's target

4. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSGxxxxx", minScore: 0.3, size: 50)
   → ALL diseases associated with this target, ranked by evidence

5. For each promising disease association:
   mcp__opentargets__opentargets_info(method: "get_disease_details", id: "EFO_xxxxxxx")
   → Disease details, existing therapeutics, unmet need

6. mcp__ctgov__ct_gov_studies(method: "search", intervention: "drug_name", condition: "new_disease")
   → Has anyone already tested this? What happened?
```

### Strategy 2: Disease-Driven (Disease → Find Drugs)

Start with an unmet disease, find drugs hitting its validated targets.

```
1. mcp__opentargets__opentargets_info(method: "search_diseases", query: "disease_name")
   → Get EFO disease ID

2. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.5, size: 30)
   → Top validated targets for this disease

3. For top targets:
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSGxxxxx")
   → Check tractability (is it druggable?)

4. For druggable targets:
   mcp__drugbank__drugbank_info(method: "search_by_target", target: "target_name")
   → Existing drugs that hit this target

5. Filter for approved drugs (repurposing candidates):
   mcp__drugbank__drugbank_info(method: "get_products", drugbank_id: "DBxxxxx", country: "US")
   → Is it already marketed? Available for repurposing?

6. mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "CHEMBLxxxx", target_id: "CHEMBLxxxx")
   → How potent is the drug against this target? (need nanomolar activity)
```

### Strategy 3: Compound-Based (Structure → New Targets)

Start with a compound's structure, find new targets it may bind.

```
1. mcp__pubchem__pubchem(method: "search_compounds", query: "drug_name", search_type: "name")
   → Get PubChem CID and canonical SMILES

2. mcp__pubchem__pubchem(method: "search_similar_compounds", smiles: "SMILES", threshold: 80)
   → Structural analogs — what are THEY used for?

3. mcp__chembl__chembl_info(method: "compound_search", query: "drug_name")
   → Get ChEMBL ID

4. mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "CHEMBLxxxx", limit: 100)
   → ALL targets this compound has measured activity against

5. For targets with sub-micromolar activity:
   mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSGxxxxx")
   → Which diseases are these off-targets relevant to?

6. mcp__drugbank__drugbank_info(method: "search_by_structure", smiles: "SMILES")
   → Approved drugs with similar structure — what are they used for?
```

### DepMap-Driven Repurposing

Use cancer dependency data to discover new indications for existing drugs. Start with drug sensitivity across cell lineages, then triangulate with biomarkers and target dependency.

```
1. Query drug sensitivity across all lineages:
   mcp__depmap__depmap_data(method: "get_drug_sensitivity", drug: "drug_name")
   → Sensitivity scores across all cancer lineages (lower AUC = more sensitive)

2. Identify unexpectedly sensitive lineages (new indications):
   mcp__depmap__depmap_data(method: "get_context_info", drug: "drug_name")
   → Lineages/subtypes with strongest response — are any outside the approved indication?

3. Find predictive biomarkers in sensitive lines:
   mcp__depmap__depmap_data(method: "get_biomarker_analysis", drug: "drug_name")
   → Mutations, CNVs, or expression patterns that predict sensitivity
   → These biomarkers define the patient population for the new indication

4. Validate target dependency in sensitive vs resistant lines:
   mcp__depmap__depmap_data(method: "get_gene_dependency", gene: "target_gene")
   → Is the drug's target essential in the sensitive lineage?
   → Compare dependency scores: sensitive lineage vs pan-cancer

5. Check pathway-level dependency for mechanism-based rationale:
   mcp__depmap__depmap_data(method: "get_multi_gene_profile", genes: ["gene1", "gene2", "gene3"])
   → Co-dependency of pathway members supports mechanism-based repurposing

6. Cross-reference with clinical trials for the new indication:
   mcp__ctgov__ct_gov_studies(method: "search", intervention: "drug_name", condition: "new_lineage_cancer")
   → Has anyone already tested this drug in the newly identified cancer type?
```

#### Example: Repurposing a BRAF Inhibitor

```
1. mcp__depmap__depmap_data(method: "get_drug_sensitivity", drug: "vemurafenib")
   → Find sensitivity beyond melanoma (e.g., hairy cell leukemia, colorectal with BRAF V600E)

2. mcp__depmap__depmap_data(method: "get_context_info", drug: "vemurafenib")
   → Discover that certain thyroid and colorectal lines are unexpectedly sensitive

3. mcp__depmap__depmap_data(method: "get_biomarker_analysis", drug: "vemurafenib")
   → Confirm BRAF V600E mutation as the predictive biomarker across lineages

4. mcp__depmap__depmap_data(method: "get_gene_dependency", gene: "BRAF")
   → BRAF dependency score in thyroid cancer lines vs pan-cancer baseline

5. mcp__depmap__depmap_data(method: "get_multi_gene_profile", genes: ["BRAF", "MAP2K1", "MAPK1"])
   → MAPK pathway co-dependency confirms mechanism-based rationale

6. mcp__ctgov__ct_gov_studies(method: "search", intervention: "vemurafenib", condition: "thyroid cancer")
   → Find existing trials — vemurafenib in BRAF V600E thyroid cancer
```

---

## Composite Repurposing Score

### Scoring Matrix (0-100)

| Component | Weight | Criteria |
|-----------|--------|----------|
| **Target Association** | 0-40 | Open Targets association score × 40. Genetic evidence (GWAS, Mendelian) scores highest |
| **Safety Profile** | 0-30 | Known safety in approved indication. Deduct for serious ADRs, boxed warnings, narrow TI |
| **Literature Evidence** | 0-20 | Published case reports, retrospective studies, mechanistic rationale |
| **Drug Properties** | 0-10 | Oral bioavailability, half-life suitable for new indication, no formulation barriers |

### Score Interpretation

| Score | Interpretation | Action |
|-------|---------------|--------|
| 80-100 | Strong candidate | Prioritize for clinical development |
| 60-79 | Promising | Worth pursuing with additional preclinical data |
| 40-59 | Moderate | Needs significant de-risking |
| 20-39 | Weak | Only if no better alternatives |
| 0-19 | Not viable | Do not pursue |

### Score Calculation Workflow

```
1. Target Association (0-40):
   score = opentargets_association_score * 40
   If genetic evidence (GWAS p < 5e-8): bonus +10
   If existing drug for same target in same disease: bonus +5

2. Safety Profile (0-30):
   Start at 30
   Boxed warning: -15
   Serious ADR rate > 10%: -10
   Narrow therapeutic index: -10
   Known teratogenicity: -15 (if new indication includes women of childbearing age)
   Favorable safety record (>10yr on market, no recalls): +5

3. Literature Evidence (0-20):
   Prospective study showing efficacy: +15-20
   Retrospective/observational data: +10-15
   Case reports/series: +5-10
   Mechanistic rationale only: +2-5
   No published evidence: 0

4. Drug Properties (0-10):
   Oral formulation available: +3
   Half-life appropriate for new indication: +3
   No reformulation needed: +2
   Generic available (cost advantage): +2
```

---

## FAERS-Based Repurposing Signal Detection

Adverse event reports can reveal unexpected therapeutic effects (serendipitous repurposing).

```
1. mcp__fda__fda_info(method: "lookup_drug", search_term: "drug_name", search_type: "adverse_events", count: "patient.reaction.reactionmeddrapt.exact", limit: 50)
   → Look for POSITIVE outcomes reported as "adverse events" (e.g., weight loss, tumor regression)

2. mcp__fda__fda_info(method: "lookup_drug", search_term: "drug_name", search_type: "label")
   → Check Warnings & Precautions for hints (e.g., "hypoglycemia in non-diabetic patients" → diabetes indication)
```

### Historical Examples

| Drug | Original Indication | Repurposed For | Signal Source |
|------|-------------------|----------------|---------------|
| Sildenafil | Angina | Erectile dysfunction | Clinical trial side effect |
| Thalidomide | Morning sickness | Multiple myeloma | Anti-angiogenic mechanism |
| Minoxidil | Hypertension | Hair loss | Patient observation |
| Metformin | Diabetes | Cancer prevention | Epidemiological data |
| Dapagliflozin | Diabetes | Heart failure | CV outcome trial |

---

## IP & Regulatory Considerations

### Freedom to Operate

```
1. mcp__fda__fda_info(method: "get_patent_exclusivity", search_term: "drug_name")
   → Current patent/exclusivity status

2. mcp__pubchem__pubchem(method: "get_patent_ids", cid: CID_NUMBER)
   → Patent landscape for the compound

3. Key questions:
   - Is the composition of matter patent expired? (enables generic repurposing)
   - Can a new use patent (method of treatment) be obtained?
   - Is there data exclusivity (NCE 5yr, orphan 7yr, pediatric +6mo)?
```

### Regulatory Pathway for New Indication

| Scenario | FDA Pathway | Key Advantage |
|----------|-------------|---------------|
| Same formulation, new indication | sNDA (505(b)(2)) | Reference original NDA safety data |
| New formulation needed | 505(b)(2) NDA | Bridge to prior approval |
| Generic + new indication | 505(b)(2) NDA | Reduced CMC requirements |
| Rare disease repurposing | Orphan Drug + 505(b)(2) | 7yr exclusivity + tax credits |

---

## Multi-Agent Workflow Examples

**"Find new uses for metformin beyond diabetes"**
1. Drug Repurposing Analyst → Target-based scan (AMPK pathway diseases), FAERS signal detection, literature evidence
2. Clinical Trial Analyst → All metformin trials in non-diabetic conditions (cancer, aging, PCOS)
3. Pharmacovigilance Specialist → Safety profile in non-diabetic populations

**"Find existing drugs for our rare disease target"**
1. Drug Repurposing Analyst → Disease-driven strategy, target druggability, compound screening
2. Drug Target Analyst → Deep target validation, bioactivity data, selectivity
3. FDA Consultant → Orphan drug designation, 505(b)(2) pathway

---

## Completeness Checklist

- [ ] At least two repurposing strategies applied (target-based, disease-driven, compound-based)
- [ ] Open Targets association scores retrieved for all candidate target-disease pairs
- [ ] Composite repurposing score calculated with all four components
- [ ] Safety profile assessed for the new patient population
- [ ] Clinical trial landscape searched for existing repurposing trials
- [ ] FAERS signal detection performed for serendipitous therapeutic effects
- [ ] IP and patent exclusivity status checked for freedom to operate
- [ ] Regulatory pathway identified (sNDA, 505(b)(2), orphan)
- [ ] Literature evidence graded and cited
