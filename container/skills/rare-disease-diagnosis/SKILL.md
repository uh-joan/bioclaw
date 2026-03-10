---
name: rare-disease-diagnosis
description: Rare disease differential diagnosis specialist. HPO phenotype matching, ACMG/AMP variant classification, gene panel prioritization, variant pathogenicity assessment (CADD, AlphaMissense), phenotype-genotype correlation, orphan drug identification. Use when user mentions rare disease, orphan disease, HPO, phenotype matching, ACMG classification, variant interpretation, VUS, pathogenic variant, gene panel, undiagnosed disease, genetic diagnosis, or orphan drug.
---

# Rare Disease Diagnosis Specialist

Differential diagnosis support for rare diseases using phenotype matching, genomic variant interpretation, and evidence-based gene panel prioritization.

## Report-First Workflow

1. **Create report file immediately**: `[patient/case]_rare_disease_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## Cross-Reference: Other Skills

- **Orphan drug regulatory pathway** → use fda-consultant skill
- **EU orphan designations** → use mdr-745-consultant skill
- **Clinical trials for rare diseases** → use clinical-trial-analyst skill
- **Pharmacogenomics for rare disease drugs** → use pharmacogenomics-specialist skill
- **Drug target biology** → use drug-target-analyst skill

## When NOT to Use This Skill

- FDA orphan drug designation or regulatory strategy → use `fda-consultant`
- EU orphan medicinal product designations → use `mdr-745-consultant`
- Clinical trial search, eligibility, or enrollment → use `clinical-trial-analyst`
- Pharmacogenomic dosing or drug metabolism variants → use `pharmacogenomics-specialist`
- Drug target validation or druggability assessment → use `drug-target-analyst`
- Common variant GWAS interpretation or polygenic risk → use `gwas-snp-interpretation`

## Available MCP Tools

### `mcp__opentargets__opentargets_info`

| Method | Rare disease use |
|--------|-----------------|
| `search_diseases` | Find disease EFO/Orphanet ID |
| `get_disease_details` | Disease ontology, phenotypes, known therapeutics |
| `get_disease_targets_summary` | Validated gene-disease associations with evidence scores |
| `search_targets` | Gene/protein lookup |
| `get_target_details` | Gene function, pathways, constraint scores |
| `get_target_disease_associations` | Evidence breakdown (genetic, literature, animal models) |

### `mcp__pubmed__pubmed_articles`

| Method | Rare disease use |
|--------|-----------------|
| `search_keywords` | Case reports, phenotype descriptions, gene discovery papers |
| `search_advanced` | Filtered by genetics journals, date range |
| `get_article_metadata` | Full article details |

### `mcp__nlm__nlm_ct_codes`

| Method | Rare disease use |
|--------|-----------------|
| `hpo-vocabulary` | HPO term lookup for phenotype standardization |
| `ncbi-genes` | Gene information (symbol, location, function) |
| `icd-10-cm` | Diagnosis coding for rare diseases |
| `conditions` | Medical condition cross-references |

### `mcp__hpo__hpo_data` (Human Phenotype Ontology)

| Method | Rare disease use |
|--------|-----------------|
| `search_hpo_terms` | Find HPO terms for patient phenotypes (`query`, `max`, `category`) |
| `get_hpo_term` | Full term details for a phenotype (`id` HP:XXXXXXX) |
| `get_hpo_children` | Explore more specific sub-phenotypes (`id`) |
| `get_hpo_ancestors` | Find broader phenotype categories (`id`, `max`) |
| `get_hpo_descendants` | All descendant terms for phenotype grouping (`id`, `max`) |
| `compare_hpo_terms` | Measure phenotype similarity between patient and disease (`id1`, `id2`) |
| `get_hpo_term_path` | Trace phenotype term to ontology root (`id`) |
| `validate_hpo_id` | Verify HPO ID is valid before querying (`id`) |
| `batch_get_hpo_terms` | Look up multiple patient phenotypes at once (`ids`) |
| `get_hpo_term_stats` | Check how commonly a term is used in annotations (`id`) |

### `mcp__ctgov__ct_gov_studies`

| Method | Rare disease use |
|--------|-----------------|
| `search` | Clinical trials for rare diseases, natural history studies |
| `get` | Trial details — eligibility criteria, endpoints |

### `mcp__drugbank__drugbank_info`

| Method | Rare disease use |
|--------|-----------------|
| `search_by_indication` | Approved/investigational drugs for the condition |
| `search_by_target` | Drugs targeting the disease gene product |
| `get_drug_details` | Drug mechanism, dosing, pharmacology |

### `mcp__ema__ema_info`

| Method | Rare disease use |
|--------|-----------------|
| `get_orphan_designations` | EU orphan drug designations |
| `search_medicines` | EU-approved rare disease treatments |

### `mcp__monarch__monarch_data` (Monarch Initiative — Disease-Gene-Phenotype Knowledge Graph)

| Tool | Method | Use |
|------|--------|-----|
| `mcp__monarch__monarch_data` | `phenotype_gene_search` | CORE: Rank candidate genes by matching multiple HPO phenotypes (rare disease gene finder) |
| | `get_disease_genes` | Find genes associated with a disease (MONDO/OMIM ID) |
| | `get_gene_diseases` | Find diseases associated with a candidate gene |
| | `get_disease_phenotypes` | Get expected HPO phenotypes for a disease |
| | `get_gene_phenotypes` | Get phenotypes associated with a gene |
| | `get_phenotype_genes` | Find genes for a specific HPO phenotype |
| | `search` | Search for diseases, genes, phenotypes by text |
| | `get_entity` | Get entity details (MONDO, HP, HGNC IDs) |

### `mcp__clinvar__clinvar_data` (ClinVar Pathogenicity Lookups)

Use ClinVar to retrieve known pathogenicity classifications for candidate variants in rare disease genes — supports ACMG PP5/BP6 evidence codes and identifies expert-panel-reviewed variants that can accelerate diagnostic interpretation.

| Method | Rare disease use |
|--------|-----------------|
| `search_variants` | Free-text search for ClinVar variants (`query`, `retmax`, `retstart`) |
| `get_variant_summary` | Get summary for variant IDs, max 50 (`id` or `ids` array) |
| `search_by_gene` | Search variants by gene symbol (`gene`, `retmax`, `retstart`) |
| `search_by_condition` | Search by disease/phenotype (`condition`, `retmax`, `retstart`) |
| `search_by_significance` | Search by clinical significance e.g. pathogenic (`significance`, `retmax`, `retstart`) |
| `get_variant_details` | Detailed variant record with HGVS, locations, submissions (`id`) |
| `combined_search` | Multi-filter: gene + condition + significance (`gene`, `condition`, `significance`, `retmax`, `retstart`) |
| `get_gene_variants_summary` | Search gene then return summaries, max 50 (`gene`, `limit`) |

### `mcp__gnomad__gnomad_data` (gnomAD Population Genomics)

| Method | Rare disease use |
|--------|-----------------|
| `get_gene_constraint` | pLI/LOEUF scores — assess haploinsufficiency for dominant disorder candidates |
| `filter_rare_variants` | Find rare variants below allele frequency threshold |
| `get_variant` | Variant annotation + population frequency data |
| `get_population_frequencies` | Per-population allele frequencies for ancestry-matched filtering |
| `batch_gene_constraint` | Gene panel constraint assessment across multiple genes |

---

## Diagnostic Workflow

### Step 1: Phenotype Standardization (HPO)

```
1. For each clinical feature, search HPO for matching terms:
   mcp__hpo__hpo_data(method: "search_hpo_terms", query: "clinical_feature", max: 10)
   → Get standardized HPO term IDs and names

2. Get full details for each matched term:
   mcp__hpo__hpo_data(method: "get_hpo_term", id: "HP:XXXXXXX")
   → Definition, synonyms, cross-references

3. For batch phenotype entry, resolve multiple terms at once:
   mcp__hpo__hpo_data(method: "batch_get_hpo_terms", ids: ["HP:0001250", "HP:0001263", "HP:0002119"])

4. Explore phenotype hierarchy to refine specificity:
   mcp__hpo__hpo_data(method: "get_hpo_children", id: "HP:XXXXXXX")
   → More specific sub-phenotypes the patient may match

5. Build phenotype profile:
   - Core features (present in all/most patients)
   - Variable features (present in some patients)
   - Absent features (specifically noted as absent — important for exclusion)

6. Categorize by organ system:
   - Neurological
   - Musculoskeletal
   - Cardiovascular
   - Metabolic
   - Dysmorphic features
   - Growth parameters
```

### Step 2: Differential Diagnosis Generation

```
1. mcp__opentargets__opentargets_info(method: "search_diseases", query: "core_phenotype_description", size: 20)
   → Candidate diseases matching the phenotype

2. For each candidate:
   mcp__opentargets__opentargets_info(method: "get_disease_details", id: "disease_EFO_ID")
   → Check phenotype overlap, prevalence, known genes

3. Compare patient phenotypes against disease phenotypes:
   mcp__hpo__hpo_data(method: "compare_hpo_terms", id1: "HP:patient_term", id2: "HP:disease_term")
   → Semantic similarity score between phenotype pairs

4. Trace phenotype to ontology root for broader matching:
   mcp__hpo__hpo_data(method: "get_hpo_term_path", id: "HP:XXXXXXX")
   → Find shared ancestor terms across patient and disease phenotypes

5. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "phenotype1 AND phenotype2 AND phenotype3 case report", num_results: 20)
   → Published cases with similar phenotype combinations

6. Score each candidate by phenotype overlap:
   Overlap Score = (matching HPO terms / total patient HPO terms) × 100
```

### Step 3: Gene Panel Prioritization

```
1. For top candidate diseases:
   mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_ID", minScore: 0.3, size: 30)
   → Genes associated with each disease

2. Score each gene:
   | Factor | Points |
   |--------|--------|
   | Genetic evidence (GWAS, linkage, Mendelian) | 0-40 |
   | Literature evidence (case reports, functional studies) | 0-20 |
   | Animal model evidence | 0-15 |
   | Gene constraint (pLI >0.9 for dominant, LOEUF <0.35) | 0-15 |
   | Phenotype match to known gene-disease presentations | 0-10 |

3. mcp__nlm__nlm_ct_codes(method: "ncbi-genes", terms: "gene_symbol", maxList: 5)
   → Gene location, function, known disorders

4. Prioritize genes with score >50 for panel testing
```

---

## ACMG/AMP Variant Classification

### Evidence Categories

#### Pathogenic Criteria

| Code | Type | Description |
|------|------|-------------|
| **PVS1** | Very Strong | Null variant in gene where LOF is known disease mechanism |
| **PS1** | Strong | Same amino acid change as established pathogenic variant |
| **PS2** | Strong | De novo (confirmed) in patient with disease, no family history |
| **PS3** | Strong | Well-established functional studies show deleterious effect |
| **PS4** | Strong | Prevalence in affected significantly increased vs controls |
| **PM1** | Moderate | Located in mutation hotspot or critical functional domain |
| **PM2** | Moderate | Absent or extremely low frequency in population databases |
| **PM3** | Moderate | For recessive: detected in trans with a known pathogenic variant |
| **PM4** | Moderate | Protein length change (in-frame del/ins in non-repeat region) |
| **PM5** | Moderate | Novel missense at same position as known pathogenic missense |
| **PM6** | Moderate | Assumed de novo (without paternity/maternity confirmation) |
| **PP1** | Supporting | Co-segregation with disease in family members |
| **PP2** | Supporting | Missense in gene with low rate of benign missense |
| **PP3** | Supporting | Multiple computational predictions support deleterious effect |
| **PP4** | Supporting | Patient's phenotype highly specific for the gene |
| **PP5** | Supporting | Reputable source reports as pathogenic |

#### Benign Criteria

| Code | Type | Description |
|------|------|-------------|
| **BA1** | Stand-alone | Allele frequency >5% in any population |
| **BS1** | Strong | Allele frequency greater than expected for disorder |
| **BS2** | Strong | Observed in healthy adult (for fully penetrant conditions) |
| **BS3** | Strong | Functional studies show no damaging effect |
| **BS4** | Strong | Lack of segregation in affected family members |
| **BP1** | Supporting | Missense in gene where only LOF causes disease |
| **BP2** | Supporting | Observed in trans with a known pathogenic variant (dominant) |
| **BP3** | Supporting | In-frame del/ins in repetitive region |
| **BP4** | Supporting | Multiple computational predictions suggest no impact |
| **BP6** | Supporting | Reputable source reports as benign |
| **BP7** | Supporting | Synonymous variant with no predicted splice impact |

### Classification Rules

| Classification | Criteria Combination |
|---------------|---------------------|
| **Pathogenic** | PVS1 + ≥1 PS, OR ≥2 PS, OR 1 PS + ≥3 PM, OR ≥2 PM + ≥2 PP |
| **Likely Pathogenic** | PVS1 + 1 PM, OR 1 PS + 1-2 PM, OR 1 PS + ≥2 PP, OR ≥3 PM |
| **VUS** | Doesn't meet criteria for either pathogenic or benign |
| **Likely Benign** | 1 BS + 1 BP, OR ≥2 BP |
| **Benign** | BA1, OR ≥2 BS |

---

## Computational Variant Predictors

| Tool | What it predicts | Interpretation |
|------|-----------------|----------------|
| **CADD** | Combined annotation-dependent depletion | >20 = top 1% deleterious, >30 = top 0.1% |
| **AlphaMissense** | Protein structure-based pathogenicity | >0.564 = likely pathogenic, <0.34 = likely benign |
| **REVEL** | Ensemble missense prediction | >0.5 = likely deleterious |
| **SpliceAI** | Splice site disruption | >0.5 = likely splice-altering |
| **EVE** | Evolutionary model of variant effect | Class labels: pathogenic, benign, uncertain |
| **pLI** | Probability of loss-of-function intolerance | >0.9 = highly intolerant (haploinsufficient) |
| **LOEUF** | Loss-of-function observed/expected upper bound | <0.35 = constrained |

### Multiple Predictor Interpretation

```
If ≥3 predictors agree on pathogenicity → PP3 (supporting pathogenic)
If ≥3 predictors agree on benign → BP4 (supporting benign)
If predictors disagree → Do not apply PP3 or BP4

For splice variants:
If SpliceAI >0.5 → consider PVS1 (if LOF is disease mechanism)
```

### gnomAD Variant Filtering for Rare Disease

```
1. Filter candidate variants by population frequency:
   mcp__gnomad__gnomad_data(method: "get_variant", variant_id: "1-55516888-G-A")
   → Check if variant is absent or extremely rare in gnomAD

2. Apply PM2 criterion:
   - Absent from gnomAD → PM2 supporting (moderate evidence for pathogenicity)
   - AF > 0.01 in any population → exclude as likely benign (BS1)

3. Check ancestry-matched frequencies:
   mcp__gnomad__gnomad_data(method: "get_population_frequencies", variant_id: "1-55516888-G-A")
   → Per-population AF to avoid filtering artifacts from population stratification

4. Assess gene constraint for dominant disorder candidates:
   mcp__gnomad__gnomad_data(method: "get_gene_constraint", gene: "GENE_SYMBOL")
   → pLI > 0.9 or LOEUF < 0.35 supports haploinsufficiency mechanism

5. Batch assess gene panel constraint:
   mcp__gnomad__gnomad_data(method: "batch_gene_constraint", genes: ["GENE1", "GENE2", "GENE3"])
   → Prioritize constrained genes in differential diagnosis gene panels

6. Filter for rare variants in a gene:
   mcp__gnomad__gnomad_data(method: "filter_rare_variants", gene: "GENE_SYMBOL", af_threshold: 0.001)
   → Identify candidate variants below specified allele frequency
```

---

### Monarch Phenotype-Driven Gene Ranking

```
1. Collect patient HPO terms from clinical features (Step 1 above)
   → e.g., seizures (HP:0001250), hypotonia (HP:0001252), generalized hypotonia (HP:0002069)

2. Run phenotype_gene_search to rank candidate genes across all HPO terms:
   mcp__monarch__monarch_data(method="phenotype_gene_search", hpo_ids=["HP:0001250", "HP:0001252", "HP:0002069"])
   → Returns genes ranked by phenotype match score across the Monarch knowledge graph

3. For top candidate genes, check gene-disease associations:
   mcp__monarch__monarch_data(method="get_gene_diseases", gene_id="HGNC:XXXX")
   → Known diseases caused by variants in each candidate gene

4. Get disease phenotypes and compare with patient:
   mcp__monarch__monarch_data(method="get_disease_phenotypes", disease_id="MONDO:XXXXXXX")
   → Expected HPO phenotypes for each candidate disease — compare overlap with patient's phenotype profile

5. Cross-reference with gnomAD constraint and HPO MCP:
   mcp__gnomad__gnomad_data(method="get_gene_constraint", gene="GENE_SYMBOL")
   → pLI/LOEUF scores to assess haploinsufficiency for dominant disorder candidates
   mcp__hpo__hpo_data(method="compare_hpo_terms", id1="HP:patient_term", id2="HP:disease_term")
   → Semantic similarity between patient and disease phenotypes
```

---

## Treatment Identification

```
1. mcp__drugbank__drugbank_info(method: "search_by_indication", query: "disease_name", limit: 10)
   → Approved or investigational therapies

2. mcp__ema__ema_info(method: "get_orphan_designations", active_substance: "", therapeutic_area: "disease_area")
   → EU orphan drug designations for this disease area

3. mcp__ctgov__ct_gov_studies(method: "search", condition: "disease_name", status: "recruiting")
   → Active clinical trials the patient could join

4. mcp__drugbank__drugbank_info(method: "search_by_target", target: "disease_gene_product")
   → Drugs targeting the protein affected by the mutation
```

---

## Multi-Agent Workflow Examples

**"Patient with undiagnosed neuromuscular disease — help with diagnosis"**
1. Rare Disease Diagnosis → HPO phenotyping, differential generation, gene panel prioritization, variant interpretation
2. Clinical Trial Analyst → Natural history studies, interventional trials for top candidates
3. Pharmacogenomics Specialist → PGx considerations for treatment options

**"Interpret this variant: NM_000059.4:c.5946delT in BRCA2"**
1. Rare Disease Diagnosis → ACMG classification, computational predictions, population frequency
2. Drug Target Analyst → BRCA2 pathway, therapeutic targets (PARP inhibitors)
3. Clinical Decision Support → Treatment guidelines, ICD coding

## Completeness Checklist

- [ ] Patient phenotypes standardized to HPO terms with term IDs
- [ ] Phenotype profile categorized by organ system (core vs. variable features)
- [ ] Differential diagnosis generated with phenotype overlap scores
- [ ] Gene panel prioritized with scoring (genetic, literature, animal model, constraint evidence)
- [ ] ACMG/AMP classification applied to any candidate variants with criteria codes listed
- [ ] Population frequency checked via gnomAD for candidate variants
- [ ] Computational predictors consulted (CADD, AlphaMissense, REVEL, SpliceAI) with thresholds noted
- [ ] Treatment options identified (approved drugs, orphan designations, clinical trials)
- [ ] Evidence tier assigned to each candidate diagnosis
- [ ] Report file finalized with no `[Analyzing...]` placeholders remaining
