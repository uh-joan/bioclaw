---
name: gwas-snp-interpretation
description: GWAS SNP interpretation and variant analysis specialist. Interprets genetic variants (SNPs) from genome-wide association studies by aggregating evidence from multiple genomic databases, with fine-mapping and gene prioritization. Use when user mentions SNP, variant, rs number, rsid, GWAS, genome-wide association, fine-mapping, credible set, L2G, locus-to-gene, variant annotation, allele frequency, functional consequence, eQTL, variant-to-gene, causal variant, posterior probability, lead variant, or tag SNP.
---

# GWAS SNP Interpretation

Interprets genetic variants (SNPs) from genome-wide association studies by aggregating evidence from multiple genomic databases. Covers SNP annotation, trait/disease association discovery, fine-mapping via credible sets, gene prioritization using locus-to-gene (L2G) predictions, and clinical integration with pharmacogenomic context.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_gwas-snp-interpretation_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Drug discovery from GWAS-prioritized targets → use `gwas-drug-discoverer`
- Statistical fine-mapping and credible set construction → use `gwas-finemapping`
- Trait-to-gene mapping and colocalization → use `gwas-trait-to-gene`
- GWAS study design and meta-analysis comparison → use `gwas-study-explorer`
- Patient stratification from genetic variants → use `precision-medicine-stratifier`

## Cross-Reference: Other Skills

- **Drug discovery from GWAS-prioritized targets** → use gwas-drug-discoverer skill
- **Trait-to-gene mapping and colocalization** → use gwas-trait-to-gene skill
- **Statistical fine-mapping and credible set construction** → use gwas-finemapping skill
- **GWAS study design and summary statistics** → use gwas-study-explorer skill
- **Patient stratification from genetic variants** → use precision-medicine-stratifier skill

## Available MCP Tools

### `mcp__opentargets__opentargets_info` (PRIMARY — L2G Predictions & Credible Sets)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `search_diseases` | Search diseases by name/synonym | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links with genetic evidence | `targetId` (Ensembl ID), `diseaseId` (EFO ID), `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease ranked by evidence | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes) | `id` (EFO ID) |

### `mcp__pubmed__pubmed_articles` (Variant Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__nlm__nlm_ct_codes` (Gene & Phenotype Annotation)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `ncbi_genes` | Gene info by symbol or ID (aliases, chromosome, summary) | `query`, `limit` |
| `ncbi_snps` | SNP details by rsID (alleles, position, MAF, clinical significance) | `query`, `limit` |
| `ncbi_clinvar` | ClinVar variant-disease annotations | `query`, `limit` |
| `conditions` | Search conditions/diseases | `query`, `limit` |
| `hpo_vocabulary` | Human Phenotype Ontology terms | `query`, `limit` |
| `rxnorm_drugs` | Drug names and RxNorm codes | `query`, `limit` |
| `icd10_codes` | ICD-10 diagnosis codes | `query`, `limit` |
| `icd10pcs_codes` | ICD-10-PCS procedure codes | `query`, `limit` |
| `snomed_codes` | SNOMED CT concept lookup | `query`, `limit` |
| `loinc_codes` | LOINC laboratory test codes | `query`, `limit` |
| `cpt_codes` | CPT procedure codes | `query`, `limit` |

### `mcp__drugbank__drugbank_info` (Pharmacogenomic Context)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_by_name` | Find drug by name | `query` |
| `get_drug_details` | Full drug profile (mechanism, pharmacodynamics, targets) | `drugbank_id` |
| `search_by_target` | All drugs acting on a target | `target`, `limit` |
| `get_drug_interactions` | Drug-drug interactions | `drugbank_id` |
| `get_similar_drugs` | Pharmacologically similar drugs | `drugbank_id`, `limit` |
| `get_pathways` | Metabolic/signaling pathways | `drugbank_id` |
| `search_by_category` | Drugs by therapeutic category | `category`, `limit` |
| `search_by_structure` | Structural similarity search | `smiles` or `inchi`, `limit` |
| `search_by_carrier` | Drugs using same carrier protein | `carrier`, `limit` |
| `search_by_transporter` | Drugs using same transporter | `transporter`, `limit` |
| `get_external_identifiers` | Cross-database IDs (PubChem, ChEMBL, KEGG) | `drugbank_id` |

### `mcp__chembl__chembl_info` (Compound & Target Bioactivity)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |
| `get_admet` | ADMET/drug-likeness properties | `chembl_id` |

### `mcp__ensembl__ensembl_data` (Genomic Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `lookup_gene` | Get gene info by ID or symbol | `gene_id`, `species`, `expand` |
| `get_variant_consequences` | Predict variant effects (VEP) | `variants` (array of HGVS) |
| `get_variants` | Get variants in a region | `region`, `species`, `consequence_type` |
| `get_regulatory_features` | Get regulatory elements in region | `region`, `species`, `feature_type`, `cell_type` |
| `get_xrefs` | Get cross-database references | `gene_id`, `external_db`, `all_levels` |
| `map_coordinates` | Map between assemblies | `region`, `species`, `target_assembly` |

### `mcp__gnomad__gnomad_data` (Population Frequencies & Gene Constraint)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_variant` | Variant details including allele frequencies, functional annotations, and clinical significance | `variant_id`, `dataset` |
| `get_population_frequencies` | Population-specific allele frequencies for ancestry context (gnomAD populations: AFR, AMR, ASJ, EAS, FIN, NFE, SAS) | `variant_id`, `dataset` |
| `get_gene_constraint` | Gene intolerance metrics (pLI, LOEUF, missense Z-score) for assessing functional impact of variants in the gene | `gene`, `dataset` |

**gnomAD Workflow:** When interpreting a GWAS hit, look up the variant in gnomAD to obtain population-specific allele frequencies and functional annotations that contextualize the association signal. Population frequency differences across gnomAD ancestry groups (AFR, EAS, NFE, SAS, etc.) help explain ancestry-specific GWAS signals and inform transferability. Gene constraint scores (pLI, LOEUF) from gnomAD indicate whether the gene is intolerant to loss-of-function variation, which strengthens causal gene assignment when combined with L2G and fine-mapping evidence.

```
# Look up a GWAS hit variant for population frequencies and annotation
mcp__gnomad__gnomad_data(method: "get_variant", variant_id: "1-55505647-T-C")

# Get ancestry-specific allele frequencies to contextualize the association
mcp__gnomad__gnomad_data(method: "get_population_frequencies", variant_id: "1-55505647-T-C")

# Check gene constraint to assess functional impact
mcp__gnomad__gnomad_data(method: "get_gene_constraint", gene: "PCSK9")
```

### `mcp__gtex__gtex_data` (Tissue Expression & eQTLs)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_genes` | Search genes in GTEx | `query`, `page`, `pageSize` |
| `get_single_tissue_eqtls` | eQTLs for a gene in a tissue | `gencodeId`, `tissueSiteDetailId`, `datasetId` |
| `get_multi_tissue_eqtls` | eQTLs across all tissues | `gencodeId`, `datasetId` |
| `get_gene_expression` | Expression across tissues | `gencodeId`, `tissueSiteDetailId` |

### `mcp__jaspar__jaspar_data` (Transcription Factor Binding at GWAS Loci)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `variant_impact` | Assess TF motif disruption at GWAS loci | `variant`, `genome`, `threshold` |
| `search_matrices` | Find relevant TF position weight matrices | `query`, `collection`, `tax_id`, `limit` |
| `scan_sequence` | Scan GWAS locus sequence for TF binding sites | `sequence`, `matrix_id`, `threshold` |

**JASPAR Workflow:** Assess non-coding GWAS variant impact on TF binding using JASPAR PWMs. Most GWAS hits fall in non-coding regulatory regions where the causal mechanism involves disruption or creation of transcription factor binding sites. Use `variant_impact` to evaluate whether a GWAS lead SNP or credible set variant alters a TF binding motif — this provides mechanistic evidence linking the variant to gene regulation. Use `search_matrices` to identify TFs relevant to the disease-associated tissue or pathway, then `scan_sequence` to map all TF binding sites across the GWAS locus to identify which regulatory elements overlap credible set variants. Combine with GTEx eQTL and Ensembl regulatory feature data for a complete regulatory mechanism model.

---

## 5-Phase SNP Interpretation Workflow

### Phase 1: SNP Annotation (Coordinates, Alleles, Functional Consequences)

```
1. mcp__nlm__nlm_ct_codes(method: "ncbi_snps", query: "rs12345678")
   → Variant position (chr:pos), reference/alternate alleles, minor allele frequency (MAF), clinical significance

2. mcp__nlm__nlm_ct_codes(method: "ncbi_genes", query: "NEAREST_GENE_SYMBOL")
   → Gene context: chromosome, exon/intron boundaries, function summary, aliases

3. mcp__nlm__nlm_ct_codes(method: "ncbi_clinvar", query: "rs12345678")
   → ClinVar pathogenicity classifications, review status, associated conditions

4. mcp__ensembl__ensembl_data(method: "get_variant_consequences", variants: ["rs12345678"])
   → VEP consequence prediction: impact, affected genes, SIFT/PolyPhen scores

5. mcp__ensembl__ensembl_data(method: "get_regulatory_features", region: "CHR:START-END", species: "homo_sapiens")
   → Regulatory elements (enhancers, promoters, CTCF) overlapping variant position

6. Classify functional consequence:
   → Coding (missense, nonsense, frameshift) vs regulatory (promoter, enhancer, UTR, splice) vs intergenic
```

### Phase 2: Association Discovery Across Traits/Diseases

```
1. mcp__opentargets__opentargets_info(method: "search_diseases", query: "disease_or_trait_name")
   → Get EFO disease ID for the reported GWAS trait

2. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.3, size: 50)
   → All genetically associated targets for this trait, ranked by evidence score

3. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "rs12345678 GWAS association", num_results: 15)
   → Published GWAS reporting this variant, replication studies, meta-analyses

4. mcp__nlm__nlm_ct_codes(method: "conditions", query: "associated_condition")
   → Standardized condition names for cross-referencing
```

### Phase 3: Fine-Mapping via Credible Sets

```
1. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   → Genetic evidence score — includes credible set membership and posterior probabilities

2. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "rs12345678 fine-mapping credible set", num_results: 10)
   → Published fine-mapping studies for this locus

3. Interpret credible set results:
   → 95% credible set = minimum set of variants containing the causal variant with 95% probability
   → Rank variants by posterior inclusion probability (PIP)

4. Assess LD structure:
   → Variants in high LD (r² > 0.8) with lead SNP are candidates
   → Smaller credible sets = better resolution
```

### Phase 4: Gene Prioritization Using L2G Predictions

```
1. mcp__opentargets__opentargets_info(method: "search_targets", query: "CANDIDATE_GENE", size: 5)
   → Get Ensembl ID for each candidate gene at the locus

2. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Full target profile: function, expression, pathways, tractability

3. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   → L2G score and evidence breakdown for this gene-disease pair

4. Rank candidate genes by L2G score and supporting evidence:
   → Combine L2G with: distance to variant, eQTL colocalization, chromatin interaction, coding consequence

5. mcp__gtex__gtex_data(method: "search_genes", query: "CANDIDATE_GENE")
   → Get GENCODE ID for GTEx eQTL queries

6. mcp__gtex__gtex_data(method: "get_single_tissue_eqtls", gencodeId: "ENSG00000xxxxx.xx", tissueSiteDetailId: "RELEVANT_TISSUE")
   → eQTL evidence linking variant to gene expression change in disease-relevant tissue — supports causal gene assignment

7. mcp__gtex__gtex_data(method: "get_multi_tissue_eqtls", gencodeId: "ENSG00000xxxxx.xx")
   → Cross-tissue eQTL patterns — tissue-shared eQTLs strengthen gene prioritization
```

### Phase 5: Clinical Integration

```
1. mcp__drugbank__drugbank_info(method: "search_by_target", target: "PRIORITIZED_GENE")
   → Existing drugs targeting the prioritized gene — pharmacogenomic relevance

2. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   → Pharmacodynamics, mechanism, pathway involvement

3. mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "CHEMBLxxxxx", target_id: "CHEMBLxxxxx", limit: 50)
   → Bioactivity data for compounds targeting the prioritized gene

4. mcp__nlm__nlm_ct_codes(method: "hpo_vocabulary", query: "phenotype_term")
   → Standardized phenotype ontology for variant-phenotype mapping

5. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE pharmacogenomics variant response", num_results: 10)
   → Literature on pharmacogenomic implications of variants in this gene
```

---

## Interpretation Frameworks

### Genome-Wide Significance Threshold

```
p < 5×10⁻⁸  →  Genome-wide significant (standard GWAS threshold)
p < 1×10⁻⁵  →  Suggestive association (may replicate in larger studies)
p < 0.05     →  Nominal significance (not GWAS-significant; requires replication)
```

### L2G Score Interpretation (Open Targets Locus-to-Gene)

| L2G Score | Confidence | Interpretation |
|-----------|-----------|----------------|
| **> 0.7** | High | Strong evidence linking variant to gene; high-confidence causal gene |
| **0.5–0.7** | Moderate | Good evidence; gene likely causal but alternative candidates exist |
| **0.3–0.5** | Weak | Some evidence; gene is plausible but not well-differentiated from neighbors |
| **< 0.3** | Low | Minimal evidence; gene assignment uncertain, further investigation needed |

### Posterior Probability Interpretation (Fine-Mapping)

| Posterior Probability | Interpretation | Action |
|----------------------|----------------|--------|
| **> 0.5** | Very likely causal variant | High-priority for functional follow-up |
| **0.1–0.5** | Plausible causal variant | Include in experimental validation panel |
| **0.01–0.1** | Possible contributor | Consider if in credible set; check functional annotation |
| **< 0.01** | Unlikely causal | Deprioritize unless strong functional evidence |

### Functional Consequence Hierarchy

| Rank | Consequence Type | Impact | Examples |
|------|-----------------|--------|----------|
| **1 (Highest)** | Protein-truncating | Loss of function | Stop-gain, frameshift, splice donor/acceptor |
| **2** | Missense coding | Altered protein function | Amino acid substitution in functional domain |
| **3** | Splice region | Possible splicing effect | Near splice junction, branch point |
| **4** | Regulatory — promoter/enhancer | Altered gene expression | Transcription factor binding site disruption |
| **5** | UTR variant | Post-transcriptional effect | 5'UTR (translation), 3'UTR (stability, miRNA) |
| **6** | Intronic — deep | Usually benign | May affect regulatory elements, lncRNA |
| **7 (Lowest)** | Intergenic | Unknown/distal regulation | Requires chromatin interaction data to link to gene |

### Credible Set Analysis Framework

```
95% Credible Set:
  → The minimum set of variants that contains the true causal variant with ≥95% probability
  → Derived from Bayesian fine-mapping (e.g., FINEMAP, SuSiE, CARMA)

Key metrics:
  - Set size: Smaller = better resolution (1–5 variants ideal)
  - Lead variant PIP: Highest posterior probability in the set
  - Coverage: Sum of PIPs for all variants in the set (should be ≥0.95)

LD considerations:
  - Variants in high LD (r² > 0.8) are difficult to distinguish
  - Trans-ethnic fine-mapping can break LD to reduce set size
  - Functional annotation priors improve resolution (PAINTOR, PolyFun)
```

### Evidence Grading (Variant-to-Gene-to-Disease)

| Tier | Evidence | Description |
|------|----------|-------------|
| **T1 — Definitive** | Coding variant + L2G > 0.7 + PIP > 0.5 | Causal gene and variant established with high confidence |
| **T2 — Strong** | eQTL colocalization + L2G > 0.5 + credible set member | Strong mechanistic link; gene expression mediation demonstrated |
| **T3 — Moderate** | Proximity + L2G 0.3–0.5 + regulatory annotation | Plausible gene assignment; functional validation recommended |
| **T4 — Weak** | Intergenic + L2G < 0.3 + large credible set | Gene assignment uncertain; locus needs further characterization |

---

## Pharmacogenomic Variant Assessment

### Workflow

```
1. mcp__nlm__nlm_ct_codes(method: "ncbi_snps", query: "rs_pharmacogene_variant")
   → Check if variant is in a pharmacogene (CYP2D6, CYP2C19, DPYD, etc.)

2. mcp__nlm__nlm_ct_codes(method: "ncbi_clinvar", query: "rs_pharmacogene_variant")
   → ClinVar annotations for drug response associations

3. mcp__drugbank__drugbank_info(method: "search_by_target", target: "CYP2D6")
   → All drugs metabolized by or acting on this pharmacogene

4. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   → Pharmacogenomic dosing implications

5. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "rs12345678 pharmacogenomics drug response", num_results: 10)
   → Published pharmacogenomic evidence
```

---

## Pleiotropy and Cross-Trait Analysis

### Workflow

```
1. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "rs12345678 GWAS", num_results: 20)
   → Identify all traits/diseases associated with this variant (pleiotropic effects)

2. For each associated trait:
   mcp__opentargets__opentargets_info(method: "search_diseases", query: "trait_name")
   → Get EFO IDs for all associated traits

3. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   → Compare evidence scores across traits

4. Assess directionality:
   → Same variant, same direction of effect → shared biology
   → Same variant, opposite direction → antagonistic pleiotropy (trade-off)
   → Inform drug repurposing or safety signal considerations
```

---

## Multi-Agent Workflow Examples

**"Interpret a GWAS hit at rs12345678 for type 2 diabetes"**
1. GWAS SNP Interpretation → Variant annotation, credible set analysis, L2G gene prioritization, functional consequence assessment
2. GWAS Drug Discoverer → Druggability of prioritized gene, existing compounds, target tractability
3. Precision Medicine Stratifier → Patient subgroup implications based on variant frequency and effect size

**"Fine-map the 9p21 locus for coronary artery disease"**
1. GWAS SNP Interpretation → Lead SNPs, credible sets, posterior probabilities, functional annotation of each variant
2. GWAS Fine-Mapping → Statistical fine-mapping details, conditional analysis, multi-ancestry comparison
3. GWAS Trait-to-Gene → eQTL colocalization, chromatin interaction data, gene expression in relevant tissues

**"Assess pharmacogenomic implications of a CYP2D6 variant"**
1. GWAS SNP Interpretation → Variant annotation, allele frequencies, ClinVar significance, functional consequence
2. Precision Medicine Stratifier → Metabolizer phenotype prediction, population frequency differences
3. GWAS Drug Discoverer → Drugs affected by this variant, dosing adjustment recommendations via DrugBank

**"Evaluate a novel GWAS locus with no known gene"**
1. GWAS SNP Interpretation → Full 5-phase workflow: annotate variant, check associations, fine-map, prioritize candidate genes by L2G, integrate clinical evidence
2. GWAS Trait-to-Gene → Deep eQTL and chromatin interaction analysis to link intergenic variant to distal gene
3. GWAS Study Explorer → Compare effect sizes and significance across published GWAS for this locus

---

## Completeness Checklist

- [ ] SNP annotated with coordinates, alleles, MAF, and ClinVar significance
- [ ] Functional consequence classified (coding, regulatory, intronic, intergenic)
- [ ] VEP consequence prediction obtained from Ensembl with SIFT/PolyPhen scores
- [ ] Trait/disease associations discovered via Open Targets and PubMed
- [ ] Credible set membership and posterior probability assessed
- [ ] L2G gene prioritization performed with evidence breakdown
- [ ] GTEx eQTL evidence checked in disease-relevant tissues
- [ ] Pharmacogenomic context evaluated via DrugBank and ClinVar
- [ ] Pleiotropy and cross-trait associations assessed
- [ ] Report file created with no remaining `[Analyzing...]` placeholders
