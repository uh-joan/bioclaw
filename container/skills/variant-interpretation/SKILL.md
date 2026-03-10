---
name: variant-interpretation
description: Clinical variant interpretation and classification. ACMG/AMP variant classification, pathogenicity scoring, population frequency analysis, functional impact prediction, clinical significance assessment. Use when user mentions variant interpretation, ACMG classification, pathogenicity, variant of uncertain significance, VUS, ClinVar, gnomAD, variant classification, missense variant, frameshift, splice variant, loss of function, gain of function, or variant curation.
---

# Variant Interpretation

Systematic clinical variant interpretation that classifies genetic variants according to ACMG/AMP guidelines into Pathogenic, Likely Pathogenic, VUS, Likely Benign, or Benign. Integrates population frequency data, computational predictions, functional evidence, and clinical databases to produce scored pathogenicity assessments with explicit evidence code attribution.

## Report-First Workflow

1. **Create report file immediately**: `variant_interpretation_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## Cross-Reference: Other Skills

- **Somatic cancer variant interpretation and molecular tumor board** -> use cancer-variant-interpreter skill
- **Genomic-clinical patient stratification and treatment routing** -> use precision-medicine-stratifier skill
- **GWAS SNP annotation and locus-to-gene mapping** -> use gwas-snp-interpretation skill
- **Rare disease differential diagnosis with HPO phenotype matching** -> use rare-disease-diagnosis skill
- **Genotype-guided dosing and CYP450 metabolizer phenotypes** -> use pharmacogenomics-specialist skill

## Available MCP Tools

### `mcp__opentargets__opentargets_info` (Variant-Disease Associations)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `search_diseases` | Search diseases by name/synonym | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId` (Ensembl ID), `diseaseId` (EFO ID), `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes) | `id` (EFO ID) |

### `mcp__pubmed__pubmed_articles` (Clinical Evidence Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__drugbank__drugbank_info` (Pharmacogenomic Context)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_by_name` | Find drug by name | `query` |
| `get_drug_details` | Full drug profile (mechanism, pharmacodynamics, targets) | `drugbank_id` |
| `search_by_target` | All drugs acting on a target | `target`, `limit` |
| `get_pathways` | Metabolic/signaling pathways | `drugbank_id` |

### `mcp__ensembl__ensembl_data` (Genomic Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `lookup_gene` | Get gene info by ID or symbol | `gene_id`, `species`, `expand` |
| `get_transcripts` | Get transcripts for a gene | `gene_id`, `canonical_only` |
| `get_variant_consequences` | Predict variant effects (VEP) | `variants` (array of HGVS) |
| `get_sequence` | Get genomic/transcript sequence | `region`, `species`, `format`, `mask` |
| `get_xrefs` | Get cross-database references | `gene_id`, `external_db`, `all_levels` |

### `mcp__hpo__hpo_data` (Human Phenotype Ontology)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_hpo_terms` | Search phenotype terms for phenotype-genotype correlation | `query`, `max`, `category` |
| `get_hpo_term` | Get full phenotype term details | `id` (HP:XXXXXXX) |
| `compare_hpo_terms` | Compare patient phenotype to known gene-disease phenotype | `id1`, `id2` |
| `get_hpo_ancestors` | Find broader phenotype categories for PP4 assessment | `id`, `max` |
| `batch_get_hpo_terms` | Batch resolve phenotype terms for a patient | `ids` |
| `validate_hpo_id` | Verify HPO ID before querying | `id` |

### `mcp__gnomad__gnomad_data` (Population Frequencies & Gene Constraint)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_variant` | Variant frequencies, consequences, LoF annotations, ClinVar link | `variant_id` (chr-pos-ref-alt) |
| `get_population_frequencies` | Per-population allele frequencies (BA1/BS1/PM2 ACMG criteria) | `variant_id` |
| `get_gene_constraint` | pLI, LOEUF, missense z-score — gene-level intolerance to variation | `gene_symbol` or `gene_id` |
| `filter_rare_variants` | Find rare variants in a gene (max AF filter) | `gene_symbol`, `max_af` |
| `get_gene_variants` | All known variants in a gene with frequencies | `gene_symbol` or `gene_id` |
| `batch_gene_constraint` | Constraint scores for gene panels (up to 20) | `gene_symbols` (array) |

### `mcp__gtex__gtex_data` (Tissue Expression & eQTLs)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_genes` | Search genes in GTEx | `query`, `page`, `pageSize` |
| `get_gene_expression` | Expression across tissues | `gencodeId`, `tissueSiteDetailId` |
| `get_median_gene_expression` | Median expression per tissue | `gencodeId`, `tissueSiteDetailId` |

### `mcp__clinpgx__clinpgx_data` (Pharmacogenomic Variant Significance)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_variants` | PGx variant clinical significance lookup | `query`, `gene`, `limit` |
| `get_clinical_annotations` | Gene-drug-variant clinical annotations (CPIC/DPWG evidence) | `gene`, `variant`, `drug`, `level` |
| `get_drug_labels` | PGx drug labeling information (FDA/EMA) | `drug`, `gene`, `limit` |

**ClinPGx Workflow:** Check ClinPGx for pharmacogenomic significance of the variant under review. Variants in pharmacogenes (CYP2D6, CYP2C19, DPYD, TPMT, etc.) may carry PGx clinical annotations that inform drug-response phenotypes. Use `search_variants` to determine if the variant has known PGx significance, `get_clinical_annotations` to retrieve gene-drug-variant level evidence, and `get_drug_labels` to identify affected drug labels.

### `mcp__monarch__monarch_data` (Gene-Disease & Phenotype Associations)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_gene_diseases` | Gene-disease associations for PM1/PP1 evidence assessment | `gene`, `limit`, `association_type` |
| `phenotype_gene_search` | Phenotype-to-gene matching for variant prioritization | `phenotype`, `limit`, `species` |

**Monarch Workflow:** Check Monarch for gene-disease evidence to support ACMG criteria. Use `get_gene_diseases` to retrieve known disease associations for the gene harboring the variant — strong gene-disease associations support PM1 (functional domain in disease gene) and PP1 (co-segregation context). Use `phenotype_gene_search` when patient phenotypes are available to match phenotype terms to candidate genes, supporting PP4 (phenotype specificity) and aiding variant prioritization in multi-gene panels.

### `mcp__clinvar__clinvar_data` (ClinVar Variant Classification)

Use ClinVar to retrieve existing ACMG classifications, submission-level evidence, and clinical significance for variants under review — directly supports PP5/BP6 evidence codes and cross-references expert panel consensus.

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_variants` | Free-text search for ClinVar variants | `query`, `retmax`, `retstart` |
| `get_variant_summary` | Get summary for variant IDs (max 50) | `id` or `ids` (array) |
| `search_by_gene` | Search variants by gene symbol | `gene`, `retmax`, `retstart` |
| `search_by_condition` | Search by disease/phenotype | `condition`, `retmax`, `retstart` |
| `search_by_significance` | Search by clinical significance (e.g. pathogenic) | `significance`, `retmax`, `retstart` |
| `get_variant_details` | Detailed variant record with HGVS, locations, submissions | `id` |
| `combined_search` | Multi-filter: gene + condition + significance | `gene`, `condition`, `significance`, `retmax`, `retstart` |
| `get_gene_variants_summary` | Search gene then return summaries (max 50) | `gene`, `limit` |

### `mcp__jaspar__jaspar_data` (Transcription Factor Binding Analysis)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `variant_impact` | Assess TF binding impact for non-coding variants | `variant`, `genome`, `threshold` |
| `scan_sequence` | Identify TF binding sites in a genomic sequence | `sequence`, `matrix_id`, `threshold` |

**JASPAR Workflow:** Check JASPAR for transcription factor binding disruption in non-coding variants. For variants in regulatory regions (promoters, enhancers, UTRs), use `variant_impact` to determine whether the variant disrupts or creates a TF binding motif — this provides mechanistic evidence for regulatory variants that lack coding consequence predictions. Use `scan_sequence` to identify all TF binding sites across a region of interest, which helps contextualize whether the variant falls within a regulatory element with functional TF occupancy.

### `mcp__gwas__gwas_data` (GWAS Catalog — Population-Level Variant Associations)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_associations` | Search associations by query or PubMed ID | `query`, `pubmed_id`, `page`, `size` |
| `get_variant` | Get variant info by rs ID e.g. rs7329174 | `rs_id` |
| `get_variant_associations` | All associations for a variant | `rs_id`, `page`, `size` |
| `search_by_trait` | Search EFO traits by term, get associations for top match | `trait`, `page`, `size` |
| `get_study` | Study details by GCST accession | `study_id` |
| `search_studies` | Search studies by disease trait name | `disease_trait`, `page`, `size` |
| `get_gene_associations` | All GWAS associations for a gene | `gene`, `page`, `size` |
| `get_region_associations` | Associations in a genomic region | `chromosome`, `start`, `end`, `page`, `size` |
| `get_trait_associations` | All associations for an EFO trait ID | `efo_id`, `page`, `size` |
| `search_genes` | Gene info with genomic context | `gene` |

**GWAS Catalog Workflow:** Use the GWAS Catalog to retrieve population-level variant-trait associations that inform ACMG evidence assessment. For variants under clinical interpretation, query `get_variant_associations` to identify all published GWAS associations — variants with genome-wide significant associations to the patient's phenotype support PS4 (prevalence in affected vs controls). Use `get_gene_associations` to check whether the gene harboring the variant has broader GWAS evidence linking it to the disease, reinforcing gene-disease validity. Use `search_by_trait` to identify other variants and loci associated with the same condition, providing context for the genetic architecture and supporting PP4 (phenotype specificity) when GWAS findings converge on the same gene or pathway.

## Python Environment

Python 3 is available in the container with `scipy`, `statsmodels`, `pandas`, `numpy`, `scikit-learn`. Use `python3` to execute scripts. All code templates below are ready to run with minor parameter substitution.

---

## ACMG/AMP Classification Framework

### Pathogenic Evidence Codes

| Code | Strength | Criteria |
|------|----------|----------|
| **PVS1** | Very Strong | Null variant in gene where LoF is a known disease mechanism |
| **PS1** | Strong | Same amino acid change as established pathogenic variant |
| **PS2** | Strong | De novo (confirmed maternity/paternity) in patient with disease |
| **PS3** | Strong | Well-established functional studies show damaging effect |
| **PS4** | Strong | Prevalence significantly increased in affected vs controls |
| **PM1** | Moderate | Located in mutational hotspot or critical functional domain |
| **PM2** | Moderate | Absent from controls or extremely low frequency in population databases |
| **PM3** | Moderate | Detected in trans with pathogenic variant (recessive disorders) |
| **PM4** | Moderate | Protein length change from in-frame del/ins in non-repeat region |
| **PM5** | Moderate | Novel missense at same position as known pathogenic missense |
| **PM6** | Moderate | Assumed de novo without parental confirmation |
| **PP1** | Supporting | Co-segregation with disease in multiple family members |
| **PP2** | Supporting | Missense in gene with low benign missense rate |
| **PP3** | Supporting | Multiple computational tools predict deleterious |
| **PP4** | Supporting | Phenotype highly specific for single-gene disease |
| **PP5** | Supporting | Reputable source reports variant as pathogenic |

### Benign Evidence Codes

| Code | Strength | Criteria |
|------|----------|----------|
| **BA1** | Stand-alone | Allele frequency >5% in any population database |
| **BS1** | Strong | Allele frequency greater than expected for disorder |
| **BS2** | Strong | Observed in healthy adult with full penetrance expected |
| **BS3** | Strong | Functional studies show no damaging effect |
| **BS4** | Strong | Lack of segregation in affected family members |
| **BP1** | Supporting | Missense in gene where only LoF causes disease |
| **BP2** | Supporting | Observed in trans with pathogenic variant (dominant) or in cis |
| **BP3** | Supporting | In-frame del/ins in repetitive region without known function |
| **BP4** | Supporting | Multiple computational tools predict no impact |
| **BP5** | Supporting | Case with alternate molecular basis for disease |
| **BP6** | Supporting | Reputable source reports variant as benign |
| **BP7** | Supporting | Synonymous with no predicted splice impact |

### Pathogenicity Scoring Rules

```
PATHOGENIC (requires one of):
  (a) 1 Very Strong (PVS1) + >= 1 Strong (PS1-PS4)
  (b) 1 Very Strong (PVS1) + >= 2 Moderate (PM1-PM6)
  (c) >= 2 Strong (PS1-PS4)
  (d) 1 Strong (PS1-PS4) + >= 3 Supporting (PP1-PP5)
  (e) >= 2 Moderate (PM1-PM6) + >= 2 Supporting (PP1-PP5)

LIKELY PATHOGENIC (requires one of):
  (a) 1 Very Strong (PVS1) + 1 Moderate (PM1-PM6)
  (b) 1 Strong (PS1-PS4) + 1-2 Moderate (PM1-PM6)
  (c) 1 Strong (PS1-PS4) + >= 2 Supporting (PP1-PP5)
  (d) >= 3 Moderate (PM1-PM6)
  (e) 2 Moderate (PM1-PM6) + >= 2 Supporting (PP1-PP5)
  (f) 1 Moderate (PM1-PM6) + >= 4 Supporting (PP1-PP5)

LIKELY BENIGN: 1 Strong (BS1-BS4) + 1 Supporting (BP1-BP7)
BENIGN: 1 Stand-alone (BA1) OR >= 2 Strong (BS1-BS4)
VUS: Criteria for neither pathogenic nor benign are met
```

---

## Variant Interpretation Pipeline

### Phase 1: Variant Identification & Normalization

Parse and normalize to canonical HGVS notation. Map to gene and transcript.

```
1. Parse input: rsID -> coordinates; HGVS genomic -> normalize; HGVS coding -> gene; protein -> back-map
2. mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL", size: 5)
   -> Ensembl gene ID for downstream queries
3. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Gene function, protein class, pathways, constraint metrics
4. mcp__ensembl__ensembl_data(method: "lookup_gene", gene_id: "ENSG00000xxxxx", species: "homo_sapiens", expand: true)
   -> Canonical gene coordinates, biotype, strand, description
5. mcp__ensembl__ensembl_data(method: "get_transcripts", gene_id: "ENSG00000xxxxx", canonical_only: true)
   -> MANE Select / canonical transcript for HGVS notation
6. Establish: Gene symbol (HGNC), Transcript (MANE Select), HGVS c./p., GRCh38 coordinates
```

Always use MANE Select transcript when available. Document transcript choice.

### Phase 2: Population Frequency Analysis

```
gnomAD thresholds:
  >5% any population   -> BA1 (stand-alone benign)
  >1% any population   -> BS1 (strong benign)
  <0.01%               -> PM2 (moderate pathogenic)
  Absent               -> PM2 (strong supporting)

Check >= 3 ancestry groups. Founder mutations exempt from BA1.
```

#### Python: Population Frequency Filtering

```python
import pandas as pd
import numpy as np

def population_frequency_analysis(variant_frequencies: dict) -> dict:
    """
    Analyze population frequencies for ACMG evidence code assignment.
    variant_frequencies: {"european_nfe": 0.0003, "african": 0.0, ...}
    Returns: max_af, acmg_codes, frequency_score (0-20), founder detection.
    """
    BA1_THRESHOLD = 0.05
    BS1_THRESHOLD = 0.01
    PM2_THRESHOLD = 0.0001
    FOUNDER_FLAG = 0.005

    df = pd.DataFrame([
        {"population": pop, "allele_frequency": freq}
        for pop, freq in variant_frequencies.items()
    ])
    max_af = df["allele_frequency"].max()
    max_pop = df.loc[df["allele_frequency"].idxmax(), "population"]

    acmg_codes = []
    if max_af > BA1_THRESHOLD:
        acmg_codes.append(("BA1", "stand-alone", f"AF={max_af:.4f} in {max_pop} >5%"))
    elif max_af > BS1_THRESHOLD:
        acmg_codes.append(("BS1", "strong_benign", f"AF={max_af:.4f} in {max_pop} >1%"))
    if max_af < PM2_THRESHOLD:
        acmg_codes.append(("PM2", "moderate_pathogenic", f"Max AF={max_af:.6f} <0.01%"))

    # Founder mutation detection: high in one pop, rare everywhere else
    is_founder = False
    if max_af > FOUNDER_FLAG:
        other_max = df[df["population"] != max_pop]["allele_frequency"].max()
        is_founder = other_max < PM2_THRESHOLD

    # Score (0-20): higher = rarer = more pathogenic
    if max_af > BS1_THRESHOLD: score = 0
    elif max_af > 0.001: score = 2
    elif max_af > PM2_THRESHOLD: score = 8
    elif max_af > 0.00001: score = 14
    elif max_af > 0: score = 18
    else: score = 20

    return {
        "max_af": max_af, "population_with_max": max_pop,
        "acmg_codes": acmg_codes, "frequency_score": score,
        "is_founder_candidate": is_founder,
        "ancestry_summary": {r["population"]: r["allele_frequency"] for _, r in df.iterrows()},
    }

# Usage
result = population_frequency_analysis({
    "european_nfe": 0.00003, "african": 0.0, "east_asian": 0.0,
    "south_asian": 0.00001, "latino": 0.00002, "ashkenazi_jewish": 0.0,
})
print(f"Max AF: {result['max_af']:.6f} | Score: {result['frequency_score']}/20")
print(f"ACMG: {result['acmg_codes']}")
```

### gnomAD Population Frequency Assessment (ACMG)

Use gnomAD MCP to directly query variant frequencies and gene constraint for ACMG evidence code assignment.

**Step 1: Get variant frequency and annotation**

```
mcp__gnomad__gnomad_data(method: "get_variant", variant_id: "17-43094692-G-A")
```
Returns overall allele frequency, consequence, LoF annotations, and ClinVar cross-reference.

**Step 2: Check per-population frequencies for BA1/BS1/PM2**

```
mcp__gnomad__gnomad_data(method: "get_population_frequencies", variant_id: "17-43094692-G-A")
```
Returns allele frequencies across ancestry groups (NFE, AFR, EAS, SAS, AMR, ASJ, etc.).

Apply ACMG frequency criteria:
- **BA1** (stand-alone benign): AF > 0.05 in any population
- **BS1** (strong benign): AF > population-specific threshold (typically >0.01)
- **PM2** (moderate pathogenic): Absent from gnomAD or AF < 0.0001

Check at least 3 ancestry groups. Account for founder mutations (high in one population, rare in all others).

**Step 3: Get gene constraint for PP2/PVS1 assessment**

```
mcp__gnomad__gnomad_data(method: "get_gene_constraint", gene_symbol: "BRCA1")
```
Returns pLI, LOEUF, and missense z-score.

Apply to ACMG criteria:
- **PVS1**: LoF variant in a LoF-intolerant gene (pLI > 0.9 or LOEUF < 0.35)
- **PP2**: Missense in a gene with high missense constraint (missense z-score > 3.09)
- Supports PM1 assessment when combined with domain-level constraint

**Step 4: Contextualize with gene-level variant landscape**

```
mcp__gnomad__gnomad_data(method: "filter_rare_variants", gene_symbol: "BRCA1", max_af: 0.001)
mcp__gnomad__gnomad_data(method: "get_gene_variants", gene_symbol: "BRCA1")
```
Compare the variant under review against the full spectrum of known variation in the gene. Identify whether the position is devoid of common variation (supports PM2) or sits in a region with many benign variants (argues against PM1).

---

### Phase 3: Computational Predictions

Aggregate in silico predictions. No single predictor is sufficient.

```
Thresholds:
  REVEL:         >0.75 specific pathogenic, >0.5 sensitive, <0.25 benign
  CADD:          >25 top 0.3%, >30 top 0.1%
  AlphaMissense: >0.564 pathogenic, <0.340 benign
  SpliceAI:      >0.5 likely splice effect, >0.8 high confidence
  GERP++/phyloP: >2 conserved, >4 highly conserved
  PolyPhen-2:    >0.908 probably damaging
  SIFT:          <0.05 deleterious

Consensus: >= 3 tools agree deleterious -> PP3; >= 3 agree benign -> BP4
```

#### Python: Multi-Predictor Pathogenicity Scoring

```python
import numpy as np

def multi_predictor_scoring(predictions: dict) -> dict:
    """
    Combine computational predictor scores into consensus assessment.
    predictions: {"revel": 0.85, "cadd": 28.3, ...} (None for unavailable)
    Returns: consensus, acmg_code, weighted_composite, computational_score (0-20).
    """
    THRESHOLDS = {
        "revel":        {"path": 0.75,  "benign": 0.25,  "dir": "above", "w": 3.0},
        "cadd":         {"path": 25.0,  "benign": 15.0,  "dir": "above", "w": 2.5},
        "alphamissense":{"path": 0.564, "benign": 0.340, "dir": "above", "w": 3.0},
        "sift":         {"path": 0.05,  "benign": 0.30,  "dir": "below", "w": 1.5},
        "polyphen2":    {"path": 0.908, "benign": 0.446, "dir": "above", "w": 1.5},
        "gerp":         {"path": 4.0,   "benign": 2.0,   "dir": "above", "w": 1.0},
        "phylop":       {"path": 2.0,   "benign": 0.5,   "dir": "above", "w": 1.0},
        "spliceai":     {"path": 0.5,   "benign": 0.1,   "dir": "above", "w": 2.0},
    }

    verdicts = {}
    w_path, w_benign, total_w, n = 0.0, 0.0, 0.0, 0

    for pred, score in predictions.items():
        if score is None or pred not in THRESHOLDS:
            continue
        cfg = THRESHOLDS[pred]
        w = cfg["w"]
        total_w += w
        n += 1

        if cfg["dir"] == "above":
            v = "pathogenic" if score >= cfg["path"] else ("benign" if score <= cfg["benign"] else "uncertain")
        else:
            v = "pathogenic" if score <= cfg["path"] else ("benign" if score >= cfg["benign"] else "uncertain")

        if v == "pathogenic": w_path += w
        elif v == "benign": w_benign += w
        verdicts[pred] = {"score": score, "verdict": v}

    composite = w_path / total_w if total_w > 0 else 0.5
    pc = sum(1 for v in verdicts.values() if v["verdict"] == "pathogenic")
    bc = sum(1 for v in verdicts.values() if v["verdict"] == "benign")

    acmg_code = None
    if n >= 3:
        if pc >= 3 and bc == 0: acmg_code = "PP3"
        elif bc >= 3 and pc == 0: acmg_code = "BP4"

    # Score 0-20
    if composite >= 0.9: cs = 20
    elif composite >= 0.75: cs = 18
    elif composite >= 0.6: cs = 14
    elif composite >= 0.4: cs = 8
    elif composite >= 0.2: cs = 4
    else: cs = 0

    return {
        "verdicts": verdicts, "weighted_composite": round(composite, 3),
        "path_count": pc, "benign_count": bc, "acmg_code": acmg_code,
        "computational_score": cs,
        "consensus": ("CONCORDANT_PATHOGENIC" if pc >= 3 and bc == 0
                      else "CONCORDANT_BENIGN" if bc >= 3 and pc == 0
                      else "DISCORDANT" if pc > 0 and bc > 0 else "INSUFFICIENT"),
    }

# Usage
result = multi_predictor_scoring({
    "revel": 0.85, "cadd": 28.3, "alphamissense": 0.72,
    "sift": 0.01, "polyphen2": 0.95, "gerp": 4.2, "phylop": 3.1,
})
print(f"Consensus: {result['consensus']} | ACMG: {result['acmg_code']}")
print(f"Score: {result['computational_score']}/20")
```

### Phase 4: Functional Evidence

```
1. mcp__pubmed__pubmed_articles(method: "search_keywords",
       keywords: "GENE_SYMBOL functional study in vitro assay mutation", num_results: 20)
2. mcp__pubmed__pubmed_articles(method: "search_advanced",
       term: "GENE_SYMBOL HGVS_NOTATION functional", num_results: 10)
3. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Protein domains, functional regions

4. mcp__gtex__gtex_data(method: "search_genes", query: "GENE_SYMBOL")
   -> Get GENCODE ID for tissue expression context

5. mcp__gtex__gtex_data(method: "get_median_gene_expression", gencodeId: "ENSG00000xxxxx.xx")
   -> Tissue expression profile — variants in genes with tissue-restricted expression inform clinical phenotype expectations and penetrance assessment

6. mcp__ensembl__ensembl_data(method: "get_variant_consequences", variants: ["ENST00000xxxxx:c.XXX>Y"])
   -> VEP consequence prediction: impact, SIFT, PolyPhen, affected transcript features

PS3 requires well-established assay with validated controls measuring relevant biological function.
BS3 requires well-established assay showing normal activity.
Patient-derived cell lines, knock-in animal models, validated reporter assays = well-established.
Over-expression systems alone or single computational models are NOT sufficient.
```

### Phase 5: Clinical Database Cross-Reference

```
1. mcp__pubmed__pubmed_articles(method: "search_keywords",
       keywords: "GENE_SYMBOL variant ClinVar pathogenic classification", num_results: 15)
2. mcp__pubmed__pubmed_articles(method: "search_keywords",
       keywords: "GENE_SYMBOL variant case report clinical presentation", num_results: 15)
3. mcp__opentargets__opentargets_info(method: "get_target_disease_associations",
       targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx", size: 50)
4. mcp__drugbank__drugbank_info(method: "search_by_target", target: "GENE_SYMBOL", limit: 20)
   -> Pharmacogenomic relevance

5. Phenotype-genotype correlation via HPO:
   mcp__hpo__hpo_data(method: "search_hpo_terms", query: "patient_phenotype", max: 10)
   → Match patient phenotypes to HPO terms
   mcp__hpo__hpo_data(method: "compare_hpo_terms", id1: "HP:patient_term", id2: "HP:gene_disease_term")
   → Assess whether patient phenotype matches known gene-disease presentation (supports PP4)

ClinVar confidence: Expert panel (3-4 star) > multiple submitters (2 star) > single (1 star)
```

### Phase 6: Final Classification & Report

Synthesize all evidence. Apply combining rules. Calculate Pathogenicity Score (0-100):

| Component | Points | What it measures |
|-----------|--------|-----------------|
| Population Frequency | 0-20 | Rarity in population databases |
| Computational Predictions | 0-20 | In silico consensus |
| Functional Evidence | 0-25 | Experimental functional data |
| Clinical Evidence | 0-25 | Clinical observations, case reports |
| Segregation & De Novo | 0-10 | Family studies, de novo status |

Score interpretation: 0-19 Benign, 20-39 Likely Benign, 40-59 VUS, 60-79 Likely Pathogenic, 80-100 Pathogenic. The ACMG evidence code combination is the PRIMARY classification; the score is an adjunct.

#### Python: ACMG Criteria Aggregation Algorithm

```python
from typing import Optional

class ACMGClassifier:
    """ACMG/AMP variant classification engine."""

    EVIDENCE_WEIGHTS = {
        "PVS1": ("very_strong", "pathogenic"),
        "PS1": ("strong", "pathogenic"), "PS2": ("strong", "pathogenic"),
        "PS3": ("strong", "pathogenic"), "PS4": ("strong", "pathogenic"),
        "PM1": ("moderate", "pathogenic"), "PM2": ("moderate", "pathogenic"),
        "PM3": ("moderate", "pathogenic"), "PM4": ("moderate", "pathogenic"),
        "PM5": ("moderate", "pathogenic"), "PM6": ("moderate", "pathogenic"),
        "PP1": ("supporting", "pathogenic"), "PP2": ("supporting", "pathogenic"),
        "PP3": ("supporting", "pathogenic"), "PP4": ("supporting", "pathogenic"),
        "PP5": ("supporting", "pathogenic"),
        "BA1": ("stand_alone", "benign"),
        "BS1": ("strong", "benign"), "BS2": ("strong", "benign"),
        "BS3": ("strong", "benign"), "BS4": ("strong", "benign"),
        "BP1": ("supporting", "benign"), "BP2": ("supporting", "benign"),
        "BP3": ("supporting", "benign"), "BP4": ("supporting", "benign"),
        "BP5": ("supporting", "benign"), "BP6": ("supporting", "benign"),
        "BP7": ("supporting", "benign"),
    }

    def __init__(self):
        self.applied_codes: list[dict] = []
        self.scores = {
            "population_frequency": 0, "computational_predictions": 0,
            "functional_evidence": 0, "clinical_evidence": 0, "segregation_de_novo": 0,
        }

    def add_evidence(self, code: str, justification: str,
                     tier: str = "T4", source: Optional[str] = None):
        if code not in self.EVIDENCE_WEIGHTS:
            raise ValueError(f"Unknown ACMG code: {code}")
        strength, direction = self.EVIDENCE_WEIGHTS[code]
        self.applied_codes.append({
            "code": code, "strength": strength, "direction": direction,
            "justification": justification, "tier": tier, "source": source,
        })

    def set_score(self, component: str, score: int):
        maxes = {"population_frequency": 20, "computational_predictions": 20,
                 "functional_evidence": 25, "clinical_evidence": 25, "segregation_de_novo": 10}
        self.scores[component] = min(score, maxes[component])

    def classify(self) -> dict:
        path = [c for c in self.applied_codes if c["direction"] == "pathogenic"]
        ben = [c for c in self.applied_codes if c["direction"] == "benign"]

        pvs = [c for c in path if c["strength"] == "very_strong"]
        ps = [c for c in path if c["strength"] == "strong"]
        pm = [c for c in path if c["strength"] == "moderate"]
        pp = [c for c in path if c["strength"] == "supporting"]
        ba = [c for c in ben if c["strength"] == "stand_alone"]
        bs = [c for c in ben if c["strength"] == "strong"]
        bp = [c for c in ben if c["strength"] == "supporting"]

        cls = "VUS"
        rules = []

        # Benign (BA1 is absolute)
        if ba:
            cls, rules = "Benign", ["BA1 stand-alone"]
        elif len(bs) >= 2:
            cls, rules = "Benign", [f"{len(bs)} strong benign"]
        elif bs and bp:
            cls, rules = "Likely Benign", [f"{len(bs)} strong + {len(bp)} supporting benign"]

        # Pathogenic (only if still VUS)
        if cls == "VUS":
            if pvs and ps:
                cls, rules = "Pathogenic", ["PVS1 + strong"]
            elif pvs and len(pm) >= 2:
                cls, rules = "Pathogenic", ["PVS1 + 2+ moderate"]
            elif len(ps) >= 2:
                cls, rules = "Pathogenic", ["2+ strong"]
            elif ps and len(pp) >= 3:
                cls, rules = "Pathogenic", ["1 strong + 3+ supporting"]
            elif len(pm) >= 2 and len(pp) >= 2:
                cls, rules = "Pathogenic", ["2+ moderate + 2+ supporting"]

        if cls == "VUS":
            if pvs and pm:
                cls, rules = "Likely Pathogenic", ["PVS1 + moderate"]
            elif ps and 1 <= len(pm) <= 2:
                cls, rules = "Likely Pathogenic", [f"1 strong + {len(pm)} moderate"]
            elif ps and len(pp) >= 2:
                cls, rules = "Likely Pathogenic", ["1 strong + 2+ supporting"]
            elif len(pm) >= 3:
                cls, rules = "Likely Pathogenic", ["3+ moderate"]
            elif len(pm) >= 2 and len(pp) >= 2:
                cls, rules = "Likely Pathogenic", ["2 moderate + 2+ supporting"]
            elif pm and len(pp) >= 4:
                cls, rules = "Likely Pathogenic", ["1 moderate + 4+ supporting"]

        total = sum(self.scores.values())
        evidence_lines = []
        for c in self.applied_codes:
            line = f"  {c['code']} ({c['strength']}): {c['justification']} [{c['tier']}]"
            if c["source"]: line += f" ({c['source']})"
            evidence_lines.append(line)

        return {
            "classification": cls, "pathogenicity_score": total,
            "evidence_summary": "\n".join(evidence_lines),
            "score_breakdown": dict(self.scores), "applied_rules": rules,
        }

    def report(self, variant: str, gene: str, transcript: str, consequence: str) -> str:
        r = self.classify()
        lines = [
            "=" * 60, "VARIANT CLASSIFICATION REPORT", "=" * 60,
            f"Variant:         {variant}", f"Gene:            {gene}",
            f"Transcript:      {transcript}", f"Consequence:     {consequence}",
            "-" * 60, f"CLASSIFICATION:  {r['classification']}",
            f"PATHOGENICITY SCORE: {r['pathogenicity_score']}/100", "",
            "Evidence Codes:", r["evidence_summary"], "",
            "Score Breakdown:",
        ]
        for comp, s in r["score_breakdown"].items():
            mx = 25 if "evidence" in comp else (10 if "segregation" in comp else 20)
            lines.append(f"  {comp.replace('_',' ').title():30s} {s}/{mx}")
        lines += ["", f"Rules: {', '.join(r['applied_rules']) or 'VUS'}", "=" * 60]
        return "\n".join(lines)

# Usage
c = ACMGClassifier()
c.add_evidence("PVS1", "Frameshift in LoF-intolerant gene", "T1", "ClinVar expert panel")
c.add_evidence("PS4", "Enriched in breast/ovarian cancer vs controls", "T1", "PMID:20104584")
c.add_evidence("PM2", "AF < 0.01% in gnomAD", "T3", "gnomAD v4.0")
c.add_evidence("PP5", "ClinVar 4-star pathogenic", "T1", "VCV000017661")
c.set_score("population_frequency", 18)
c.set_score("computational_predictions", 18)
c.set_score("functional_evidence", 25)
c.set_score("clinical_evidence", 25)
c.set_score("segregation_de_novo", 9)
print(c.report("NM_007294.4:c.5266dupC", "BRCA1", "NM_007294.4", "frameshift"))
```

---

## Variant Type Decision Trees

### Missense Variants

```
1. Population frequency -> BA1/BS1/PM2
2. Computational predictions (REVEL, CADD, AlphaMissense, PolyPhen-2, SIFT) -> PP3/BP4
3. Same amino acid change as known pathogenic? -> PS1
4. Novel missense at same position as known pathogenic? -> PM5
5. Mutational hotspot or functional domain? -> PM1
6. Functional studies? -> PS3/BS3
7. Low benign missense rate? -> PP2     8. LoF-only gene? -> BP1
9. Segregation/de novo? -> PP1/PS2/PM6  10. Combine -> classify
```

### Nonsense Variants

```
1. LoF = disease mechanism? -> PVS1 applicable
2. Last exon or last 50bp of penultimate exon? YES -> PVS1 reduced; NO -> full PVS1
3. Frequency -> BA1/BS1/PM2   4. NMD evidence -> PS3   5. Combine -> classify
```

### Frameshift Variants

```
1. LoF = disease mechanism? -> PVS1   2. Last exon? -> PVS1 reduced
3. Reading frame restored nearby? -> treat as in-frame
4. Frequency -> BA1/BS1/PM2   5. Functional evidence -> PS3   6. Combine -> classify
```

### Splice Variants

```
1. Canonical +/-1,2? YES -> PVS1 if LoF mechanism; NO -> SpliceAI + literature
2. SpliceAI: >0.8 high confidence, 0.5-0.8 likely, 0.2-0.5 possible, <0.2 unlikely
3. RNA/minigene studies? -> PS3
4. mcp__pubmed__pubmed_articles(method: "search_keywords",
       keywords: "GENE splice RNA minigene", num_results: 10)
5. Frequency -> BA1/BS1/PM2   6. Combine -> classify
```

### In-Frame Indel Variants

```
1. Repeat region without function? -> BP3   2. Non-repeat -> PM4
3. Critical domain? -> PM1   4. Frequency -> BA1/BS1/PM2
5. Predictions -> PP3/BP4   6. Functional -> PS3/BS3   7. Combine -> classify
```

---

## Special Considerations

### De Novo Variants

- Confirmed de novo (maternity + paternity): PS2 (strong)
- Assumed de novo (no confirmation): PM6 (moderate)
- Consider gene-specific de novo rates (e.g., NF1 ~50% de novo)

### Compound Heterozygosity

- Variant in trans with known pathogenic (recessive): PM3 (moderate)
- Phase must be confirmed (parental testing or long-read sequencing)
- Each variant classified independently; compound het informs PM3 only

### Mosaicism

- Low allele fraction does NOT automatically mean benign
- Search: `mcp__pubmed__pubmed_articles(keywords: "GENE mosaic postzygotic")`
- Standard ACMG criteria apply with caveats on frequency interpretation

### Somatic vs. Germline

- This skill is for GERMLINE interpretation (ACMG/AMP)
- For somatic: use cancer-variant-interpreter skill (AMP/ASCO/CAP tiers)
- Confirm germline status with matched normal if variant found in tumor

---

## Evidence Grading (T1-T4)

| Grade | Type | Examples |
|-------|------|----------|
| **T1** | Human/Clinical | ClinVar expert panel; FDA biomarker; clinical correlation |
| **T2** | Functional Studies | In vitro/in vivo assay; splicing assay; protein activity |
| **T3** | Association | Population frequency; co-segregation; CADD >30 |
| **T4** | Computational | PolyPhen-2 prediction; conservation analysis; text mining |

Every evidence code MUST carry a T-grade. Multiple evidence types upgrade the grade. Absence of evidence is "No data", not T4.

---

## Multi-Agent Workflow Examples

**"Interpret this germline BRCA2 missense variant for a breast cancer patient"**
1. Variant Interpretation -> 6-phase ACMG classification, pathogenicity scoring
2. Cancer Variant Interpreter -> somatic context, therapeutic associations
3. Pharmacogenomics Specialist -> PARP inhibitor eligibility
4. Precision Medicine Stratifier -> overall genomic risk profile

**"Classify a novel VUS in a rare disease gene"**
1. Variant Interpretation -> ACMG classification, evidence gaps, VUS management plan
2. Rare Disease Diagnosis -> HPO phenotype matching, differential diagnosis
3. Precision Medicine Stratifier -> patient stratification with VUS context

**"Assess pharmacogenomic impact of CYP2D6 variant"**
1. Variant Interpretation -> ACMG classification, multi-ancestry frequency
2. Pharmacogenomics Specialist -> metabolizer phenotype, CPIC dosing
3. Drug Interaction Analyst -> multi-drug interaction profile

**"Re-classify a VUS reported 3 years ago"**
1. Variant Interpretation -> full re-assessment, document what changed
2. Rare Disease Diagnosis -> updated HPO matching
3. GWAS SNP Interpretation -> new associations at this locus
4. Precision Medicine Stratifier -> re-evaluate treatment plan

## Completeness Checklist

- [ ] Variant normalized to HGVS notation on MANE Select transcript
- [ ] Gene resolved to Ensembl ID with function and constraint data retrieved
- [ ] Population frequency queried across gnomAD ancestry groups (BA1/BS1/PM2 assessed)
- [ ] Computational predictions aggregated from at least 3 tools (REVEL, CADD, AlphaMissense, SIFT, PolyPhen-2)
- [ ] Functional evidence searched in PubMed (PS3/BS3 assessment)
- [ ] Clinical database cross-reference completed (ClinVar, case reports)
- [ ] All applicable ACMG evidence codes assigned with T-grade and justification
- [ ] ACMG combining rules applied and final classification determined (Pathogenic/LP/VUS/LB/Benign)
- [ ] Pathogenicity score calculated (0-100) with component breakdown
- [ ] Variant type decision tree followed (missense/nonsense/frameshift/splice/indel as applicable)
