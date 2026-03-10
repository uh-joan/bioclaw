---
name: pharmacogenomics-specialist
description: Pharmacogenomics and precision medicine specialist. Genotype-guided dosing, CPIC guidelines, CYP450 metabolizer phenotypes, allele function interpretation, pharmacogenomic biomarkers, phenoconversion, population allele frequencies. Use when user mentions pharmacogenomics, PGx, genotype-guided dosing, CPIC, CYP2D6, CYP2C19, CYP3A4, poor metabolizer, ultra-rapid metabolizer, allele function, HLA-B, SLCO1B1, DPWG, or precision medicine.
---

# Pharmacogenomics Specialist

Genotype-guided prescribing using CPIC guidelines, FDA PGx biomarker labels, and population genetics. Translates genetic test results into actionable dosing recommendations.

## Report-First Workflow

1. **Create report file immediately**: `[drug_or_gene]_pharmacogenomics-specialist_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Non-genetic drug interactions and contraindications → use `clinical-decision-support`
- Drug safety signal detection and FAERS analysis → use `pharmacovigilance-specialist`
- Drug target biology and druggability assessment → use `drug-target-analyst`
- Clinical trial PGx sub-study data → use `clinical-trial-analyst`
- GWAS and variant-level genomic interpretation → use `variant-interpretation`
- Population-level variant frequency analysis beyond PGx context → use `variant-analysis`

## Cross-Reference: Other Skills

- **Drug interactions (non-genetic)** → use clinical-decision-support skill
- **Drug safety signals** → use pharmacovigilance-specialist skill
- **Drug target biology** → use drug-target-analyst skill
- **Clinical trial PGx data** → use clinical-trial-analyst skill

## Available MCP Tools

### `mcp__drugbank__drugbank_info`

| Method | PGx use |
|--------|---------|
| `search_by_name` | Find drug DrugBank ID |
| `get_drug_details` | Metabolism enzymes, pharmacokinetics, CYP involvement |
| `get_drug_interactions` | Interaction potential (CYP-mediated) |
| `get_pathways` | Metabolic pathways — identify PGx-relevant enzymes |
| `search_by_target` | All drugs metabolized by same enzyme |
| `search_by_category` | Drugs in same class (class-wide PGx effects) |

### `mcp__fda__fda_info`

| Call | PGx use |
|------|---------|
| `method: "lookup_drug", search_type: "label"` | FDA PGx biomarker labeling, dosing adjustments |
| `method: "lookup_drug", search_type: "adverse_events"` | ADRs related to metabolizer status |

### `mcp__pubmed__pubmed_articles`

| Method | PGx use |
|--------|---------|
| `search_keywords` | PGx literature, CPIC guideline publications |
| `search_advanced` | Filtered by Pharmacogenomics, CPT journals |

### `mcp__nlm__nlm_ct_codes`

| Method | PGx use |
|--------|---------|
| `ncbi-genes` | Gene information (CYP2D6, CYP2C19, etc.) |
| `conditions` | Conditions with PGx-relevant treatments |
| `rx-terms` | Drug formulations and strengths for dosing |

### `mcp__opentargets__opentargets_info`

| Method | PGx use |
|--------|---------|
| `search_targets` | Gene/protein details for PGx genes |
| `get_target_details` | Pharmacogenomic annotations |

### `mcp__hpo__hpo_data` (Human Phenotype Ontology)

| Method | PGx use |
|--------|---------|
| `search_hpo_terms` | Find HPO terms for adverse drug reaction phenotypes (`query`, `max`, `category`) |
| `get_hpo_term` | Get full phenotype details for PGx-related clinical outcomes (`id` HP:XXXXXXX) |
| `compare_hpo_terms` | Compare expected vs observed phenotypic outcomes (`id1`, `id2`) |
| `batch_get_hpo_terms` | Resolve multiple phenotype terms for ADR profiling (`ids`) |

### `mcp__chembl__chembl_info`

| Method | PGx use |
|--------|---------|
| `get_mechanism` | Mechanism of action (relevant for PD-based PGx) |
| `get_bioactivity` | Activity data across metabolizer phenotypes |

### `mcp__gnomad__gnomad_data` (gnomAD Population Genomics)

| Method | PGx use |
|--------|---------|
| `get_variant` | PGx variant population frequencies across gnomAD |
| `get_population_frequencies` | Population-specific allele frequencies — critical for ancestry-specific dosing recommendations |
| `get_gene_variants` | All known variants in PGx genes (e.g., CYP2D6, CYP2C19, DPYD) |

### `mcp__clinvar__clinvar_data` (ClinVar PGx Variant Significance)

Use ClinVar to retrieve clinical significance annotations for pharmacogenomic variants — identifies PGx-relevant variants with drug response classifications and links star alleles to their ClinVar submission-level evidence for CPIC/DPWG guideline cross-referencing.

| Method | PGx use |
|--------|---------|
| `search_variants` | Free-text search for PGx variants by rsID or HGVS (`query`, `retmax`, `retstart`) |
| `get_variant_summary` | Get summary for variant IDs, max 50 (`id` or `ids` array) |
| `search_by_gene` | Search all ClinVar variants in a pharmacogene (`gene`, `retmax`, `retstart`) |
| `search_by_condition` | Search variants by drug response condition (`condition`, `retmax`, `retstart`) |
| `search_by_significance` | Search by clinical significance e.g. drug response (`significance`, `retmax`, `retstart`) |
| `get_variant_details` | Detailed variant record with HGVS, locations, submissions (`id`) |
| `combined_search` | Multi-filter: gene + condition + significance (`gene`, `condition`, `significance`, `retmax`, `retstart`) |
| `get_gene_variants_summary` | Search gene then return summaries, max 50 (`gene`, `limit`) |

### `mcp__clinpgx__clinpgx_data` (PharmGKB / ClinPGx — Core PGx Resource)

| Method | PGx use |
|--------|---------|
| `get_gene` | PGx gene info (CYP2D6, CYP2C19, VKORC1, etc.) |
| `get_guidelines` | CPIC and DPWG clinical guidelines for gene-drug pairs |
| `get_gene_drug_pairs` | All gene-drug pair guidelines |
| `get_alleles` | Star alleles for a PGx gene (e.g., CYP2D6 *1-*100+) |
| `get_clinical_annotations` | Clinical annotations for gene-drug-phenotype |
| `get_drug_labels` | FDA/EMA pharmacogenomic drug labels |
| `search_variants` | PGx variant lookup by rsID |
| `get_chemical` | Drug PGx info |

---

## Key Pharmacogenes

### CYP450 Enzymes

| Gene | Key Substrates | Clinical Impact | CPIC Guidelines |
|------|---------------|-----------------|-----------------|
| **CYP2D6** | Codeine, tramadol, tamoxifen, fluoxetine, atomoxetine, ondansetron | PM: toxicity or no efficacy (prodrugs). UM: rapid metabolism, overdose risk | Codeine, tramadol, tamoxifen, TCAs, SSRIs, atomoxetine, ondansetron |
| **CYP2C19** | Clopidogrel, PPIs, voriconazole, escitalopram, sertraline | PM: clopidogrel failure (no activation). UM: PPI reduced efficacy | Clopidogrel, voriconazole, PPIs, SSRIs, TCAs |
| **CYP2C9** | Warfarin, phenytoin, NSAIDs, losartan | PM: warfarin bleeding risk, phenytoin toxicity | Warfarin, phenytoin |
| **CYP3A4/5** | Tacrolimus, cyclosporine, statins, many oncology drugs | CYP3A5 expressers: need higher tacrolimus doses | Tacrolimus |
| **CYP2B6** | Efavirenz, methadone, bupropion | PM: efavirenz CNS toxicity | Efavirenz |

### Non-CYP Pharmacogenes

| Gene | Drug | Clinical Impact | CPIC Guideline |
|------|------|-----------------|----------------|
| **HLA-B*57:01** | Abacavir | Hypersensitivity reaction (fatal if not tested) | Abacavir |
| **HLA-B*15:02** | Carbamazepine | Stevens-Johnson syndrome (SJS/TEN) in SE Asian descent | Carbamazepine, oxcarbazepine |
| **HLA-B*58:01** | Allopurinol | SJS/TEN | Allopurinol |
| **HLA-A*31:01** | Carbamazepine | Drug reaction with eosinophilia (DRESS) | Carbamazepine |
| **SLCO1B1** | Simvastatin | Myopathy risk (rs4149056 T>C) | Simvastatin |
| **TPMT/NUDT15** | Azathioprine, 6-MP | Myelosuppression in PM | Thiopurines |
| **DPYD** | Fluorouracil, capecitabine | Fatal toxicity in PM | Fluoropyrimidines |
| **UGT1A1** | Irinotecan, atazanavir | Neutropenia, hyperbilirubinemia | Atazanavir |
| **G6PD** | Rasburicase, dapsone, primaquine | Hemolytic anemia | Rasburicase |
| **IFNL3 (IL28B)** | PEG-IFN/ribavirin | HCV treatment response prediction | Peginterferon alfa-2a/2b |
| **VKORC1** | Warfarin | Dose sensitivity (with CYP2C9) | Warfarin |
| **CYP2C cluster** | Clopidogrel | *2/*3 loss of function → stent thrombosis | Clopidogrel |

---

## Metabolizer Phenotype Classification

### Activity Score System (AS)

Each allele assigned a value based on enzyme activity:

| Allele Function | Activity Value |
|----------------|---------------|
| Normal function | 1.0 |
| Decreased function | 0.5 |
| No function | 0 |
| Increased function | >1.0 (CYP2D6 gene duplications) |

**Diplotype AS = sum of both allele values**

### Phenotype Assignment

| Phenotype | Abbreviation | Activity Score | Clinical Meaning |
|-----------|-------------|---------------|------------------|
| Ultra-rapid metabolizer | UM | >2.0 | Drug cleared too fast — subtherapeutic levels or excess active metabolite |
| Normal (extensive) metabolizer | NM/EM | 1.5-2.0 | Standard dosing applies |
| Intermediate metabolizer | IM | 0.5-1.0 | Reduced clearance — consider dose reduction |
| Poor metabolizer | PM | 0 | Severely impaired — use alternative drug or major dose reduction |

### CYP2D6 Special Cases

- **Gene duplication/multiplication**: *1/*1xN or *2/*2xN → UM (AS >2.0)
- **Hybrid alleles**: *36, *68 — structural variants, zero function
- **Unclear alleles**: Some alleles have uncertain function — report as "indeterminate"

---

## Phenoconversion

Drug-induced changes in metabolizer phenotype via CYP inhibition.

### Concept

A patient who is genotypically NM for CYP2D6 can become a **phenotypic PM** if co-prescribed a strong CYP2D6 inhibitor (fluoxetine, paroxetine, bupropion).

### Assessment Workflow

```
1. Determine genotypic phenotype from PGx test results

2. Check co-medications for CYP inhibition:
   mcp__drugbank__drugbank_info(method: "get_drug_interactions", drugbank_id: "DBxxxxx")
   mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")

3. Apply inhibition penalty:
   Strong CYP inhibitor: reduce AS by 1.0 (e.g., NM → PM)
   Moderate CYP inhibitor: reduce AS by 0.5 (e.g., NM → IM)

4. Re-assign phenotype based on adjusted AS

5. Apply CPIC dosing recommendation for the ADJUSTED phenotype
```

### Phenotypic Outcome Characterization

```
When documenting adverse drug reactions linked to PGx variants, standardize to HPO:
1. mcp__hpo__hpo_data(method: "search_hpo_terms", query: "adverse reaction phenotype", max: 10)
   → e.g., "myelosuppression", "Stevens-Johnson syndrome", "hepatotoxicity"
2. mcp__hpo__hpo_data(method: "get_hpo_term", id: "HP:XXXXXXX")
   → Full phenotype definition and cross-references for clinical documentation
```

### Common Phenoconversion Scenarios

| Genotype | Co-medication | Adjusted Phenotype | Clinical Action |
|----------|--------------|--------------------|--------------------|
| CYP2D6 NM | + paroxetine (strong 2D6 inhibitor) | Phenotypic PM | Avoid codeine (no activation), reduce tamoxifen effect |
| CYP2C19 NM | + omeprazole (moderate 2C19 inhibitor) | Phenotypic IM | Monitor clopidogrel response |
| CYP3A4 NM | + ketoconazole (strong 3A4 inhibitor) | Phenotypic PM | Reduce statin dose, tacrolimus dose |

---

## CPIC Guideline Lookup Workflow

```
1. Identify the gene-drug pair:
   mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   → Check metabolism section for PGx-relevant enzymes

2. Get FDA labeling information:
   mcp__fda__fda_info(method: "lookup_drug", search_term: "drug_name", search_type: "label")
   → Check "CLINICAL PHARMACOLOGY" and "USE IN SPECIFIC POPULATIONS" for PGx biomarkers

3. Search CPIC literature:
   mcp__pubmed__pubmed_articles(method: "search_advanced", term: "CPIC drug_name pharmacogenomics guideline", journal: "Clinical Pharmacology and Therapeutics", num_results: 5)
   → Find the CPIC guideline publication

4. Apply dosing recommendation based on phenotype
```

### CPIC Guideline-Based Dosing Recommendation

Use ClinPGx (PharmGKB) as the primary source for CPIC guideline-based dosing:

```
1. Look up gene information:
   mcp__clinpgx__clinpgx_data(method="get_gene", gene="CYP2D6")
   → Gene summary, PharmGKB annotations, clinical importance

2. Get CPIC guidelines for the gene:
   mcp__clinpgx__clinpgx_data(method="get_guidelines", source="CPIC", gene="CYP2D6")
   → Full CPIC guideline text, dosing recommendations by phenotype

3. Get star alleles for diplotype interpretation:
   mcp__clinpgx__clinpgx_data(method="get_alleles", gene="CYP2D6")
   → Complete allele function table (*1-*100+), activity scores

4. Check clinical annotations for the specific drug:
   mcp__clinpgx__clinpgx_data(method="get_clinical_annotations", gene="CYP2D6")
   → Gene-drug-phenotype evidence with clinical significance levels

5. Check FDA drug label for PGx language:
   mcp__clinpgx__clinpgx_data(method="get_drug_labels", drug="drug_name")
   → FDA/EMA pharmacogenomic labeling, required/recommended testing
```

---

## CPIC Evidence Levels

| Level | Description | Action |
|-------|-------------|--------|
| **1A** | Strong evidence, strong recommendation | Change prescribing (required) |
| **1B** | Strong evidence, moderate recommendation | Change prescribing (recommended) |
| **2A** | Moderate evidence, strong recommendation | Consider changing |
| **2B** | Moderate evidence, moderate recommendation | Consider changing |
| **3** | Weak evidence | Informational only |
| **4** | Expert consensus | Informational only |

---

## FDA PGx Biomarker Table Categories

| Category | Labeling Language | Action Required |
|----------|------------------|-----------------|
| **Required testing** | "Test before prescribing" | Must test (e.g., HLA-B*57:01 for abacavir) |
| **Recommended testing** | "Consider testing" | Should test (e.g., CYP2C19 for clopidogrel) |
| **Actionable PGx** | "Dosing based on..." | Adjust if results available |
| **Informative PGx** | Mentioned in label | No required action |

### gnomAD PGx Variant Frequency Lookup

Look up PGx variant population frequencies in gnomAD — essential for ancestry-adjusted allele frequency tables:

```
1. Check population-specific frequency for a PGx variant:
   mcp__gnomad__gnomad_data(method: "get_population_frequencies", variant_id: "VARIANT_ID")
   → Per-population AF (African, East Asian, European, Latino, South Asian, etc.)
   → Critical for ancestry-specific dosing guidance

2. Get overall variant annotation and frequency:
   mcp__gnomad__gnomad_data(method: "get_variant", variant_id: "VARIANT_ID")
   → Global allele frequency, annotation, and functional impact

3. Enumerate all known variants in a PGx gene:
   mcp__gnomad__gnomad_data(method: "get_gene_variants", gene: "CYP2D6")
   → Comprehensive variant catalog for star allele cross-referencing
   → Also useful for CYP2C19, CYP2C9, DPYD, TPMT, UGT1A1, etc.
```

---

## Population Pharmacogenomics

### Allele Frequency Variation

| Gene/Allele | Clinical Impact | High-Frequency Populations |
|-------------|----------------|---------------------------|
| CYP2D6 PM (*4/*4) | Codeine failure | European (5-10%) |
| CYP2D6 UM (*1xN) | Codeine toxicity | North African, Ethiopian (29%) |
| CYP2C19 PM (*2/*2) | Clopidogrel failure | East Asian (13-23%) |
| CYP2C19 UM (*17) | PPI rapid metabolism | European (18-28%) |
| HLA-B*15:02 | Carbamazepine SJS | Southeast Asian (6-8%) |
| HLA-B*58:01 | Allopurinol SJS | Southeast Asian, African (6-8%) |
| DPYD *2A | 5-FU fatal toxicity | European (1-2%) |
| SLCO1B1 521T>C | Statin myopathy | All populations (15-20% heterozygous) |

---

## Multi-Agent Workflow Examples

**"Patient has CYP2D6 *4/*4 — what drugs should we avoid?"**
1. Pharmacogenomics Specialist → Phenotype assignment (PM), CPIC-guided drug list, alternative recommendations
2. Clinical Decision Support → Interaction check with current medications including phenoconversion
3. Pharmacovigilance Specialist → ADR risk for PM phenotype

**"Pre-emptive PGx panel — which genes should we test?"**
1. Pharmacogenomics Specialist → Panel design based on patient's medication list, CPIC Level 1A/1B pairs
2. Clinical Decision Support → Cost-benefit of testing, ICD coding for PGx tests
3. FDA Consultant → FDA-required vs recommended testing for current medications

## Completeness Checklist

- [ ] Gene-drug pair identified with CPIC evidence level (1A/1B/2A/2B)
- [ ] Diplotype resolved to activity score and metabolizer phenotype
- [ ] Phenoconversion assessed for co-medications that inhibit relevant CYP enzymes
- [ ] CPIC dosing recommendation applied for the adjusted phenotype
- [ ] FDA PGx biomarker labeling reviewed (required/recommended/actionable/informative)
- [ ] Population allele frequencies documented for relevant ancestry groups
- [ ] Alternative drug recommendations provided for poor/ultra-rapid metabolizers
- [ ] Phenotypic outcomes characterized with HPO terms where applicable
- [ ] Report file verified: no `[Analyzing...]` placeholders remain
