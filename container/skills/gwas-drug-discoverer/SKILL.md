---
name: gwas-drug-discoverer
description: GWAS drug discoverer and genetic target translator. Transforms genome-wide association study findings into actionable drug targets and repurposing opportunities. Use when user mentions GWAS, genome-wide association, genetic association, SNP, variant, locus, lead variant, fine-mapping, credible set, L2G, locus-to-gene, genetic evidence, Mendelian randomization, PheWAS, polygenic, multi-ancestry, drug repurposing from genetics, genetically-supported targets, or GWAS-to-drug pipeline.
---

# GWAS Drug Discoverer

Transforms genome-wide association study findings into actionable drug targets and repurposing opportunities by connecting genetic discoveries to drug development pipelines. Uses Open Targets for genetic evidence and tractability, ChEMBL for compound data, DrugBank for drug-target pharmacology, PubMed for literature, FDA for regulatory status, ClinicalTrials.gov for pipeline intelligence, and NLM for disease coding and gene lookups.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_gwas-drug-discoverer_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Deep SAR analysis and target characterization → use `drug-target-analyst`
- Independent target validation evidence → use `drug-target-validator`
- Systematic drug repurposing scoring → use `drug-repurposing-analyst`
- Pathway and network context for GWAS loci → use `network-pharmacologist`
- Statistical fine-mapping and credible set construction → use `gwas-finemapping`
- SNP-level interpretation and functional annotation → use `gwas-snp-interpretation`

## Cross-Reference: Other Skills

- **Deep target validation and SAR analysis** -> use drug-target-analyst skill
- **Independent target validation evidence** -> use drug-target-validator skill
- **Systematic repurposing opportunity assessment** -> use drug-repurposing-analyst skill
- **Pathway and network context for GWAS loci** -> use network-pharmacologist skill
- **Clinical trial pipeline for genetically-supported targets** -> use clinical-trial-analyst skill
- **Patient stratification by genotype** -> use precision-medicine-stratifier skill

## Available MCP Tools

### `mcp__opentargets__opentargets_info` (Genetic Evidence & Tractability)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `search_diseases` | Search diseases by name/synonym | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links with genetic evidence breakdown | `targetId` (Ensembl ID), `diseaseId` (EFO ID), `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease ranked by evidence | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability, genetic constraint) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes, known associations) | `id` (EFO ID) |

### `mcp__chembl__chembl_info` (Compound & Bioactivity Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |
| `get_admet` | ADMET/drug-likeness properties | `chembl_id` |

### `mcp__drugbank__drugbank_info` (Drug-Target Pharmacology)

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

### `mcp__pubmed__pubmed_articles` (GWAS & Target Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__fda__fda_info` (Regulatory Status)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search FDA-approved drugs | `query`, `limit` |
| `get_drug_label` | Full prescribing information | `application_number` or `drug_name` |
| `get_approval_history` | Approval dates and supplements | `application_number` |
| `search_adverse_events` | Post-market adverse event reports | `drug_name`, `reaction`, `limit` |
| `get_drug_interactions` | FDA-documented interactions | `drug_name` |
| `search_recalls` | Drug recall information | `query`, `limit` |
| `get_orange_book` | Patent and exclusivity data | `drug_name` or `ingredient` |
| `search_ndcs` | National Drug Code lookup | `query`, `limit` |

### `mcp__ctgov__ctgov_info` (Clinical Trial Pipeline)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_studies` | Search clinical trials by condition/intervention | `query`, `condition`, `intervention`, `status`, `limit` |
| `get_study_details` | Full trial record | `nct_id` |
| `get_study_results` | Results and outcomes for completed trials | `nct_id` |
| `search_by_sponsor` | Trials by sponsor organization | `sponsor`, `status`, `limit` |

### `mcp__gnomad__gnomad_data` (Gene Constraint & Natural Knockouts)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_gene_constraint` | Gene LoF intolerance (pLI, LOEUF) — LoF intolerant genes are better drug targets because modulating them has phenotypic consequences | `gene`, `dataset` |
| `batch_gene_constraint` | Compare constraint across multiple GWAS-nominated drug target candidates simultaneously | `genes` (list), `dataset` |
| `filter_rare_variants` | Find rare LoF variants in a gene — individuals carrying these are natural knockouts informing target safety and efficacy | `gene`, `max_af`, `consequence_type`, `dataset` |

**gnomAD Workflow:** Assess gnomAD constraint for GWAS-nominated drug targets to evaluate druggability. Genes with high pLI (> 0.9) or low LOEUF (< 0.35) are intolerant to loss-of-function, meaning their modulation has biological consequences -- these make better drug targets because perturbation produces a phenotype. Batch-compare constraint across competing target candidates to prioritize. Additionally, search for rare LoF carriers in gnomAD as natural human knockouts; the phenotypic consequences in these individuals provide a preview of on-target drug effects and safety liabilities.

```
# Assess constraint for a GWAS-nominated drug target
mcp__gnomad__gnomad_data(method: "get_gene_constraint", gene: "PCSK9")

# Compare constraint across competing targets
mcp__gnomad__gnomad_data(method: "batch_gene_constraint", genes: ["PCSK9", "ANGPTL3", "APOC3"])

# Find rare LoF carriers as natural knockouts
mcp__gnomad__gnomad_data(method: "filter_rare_variants", gene: "PCSK9", max_af: 0.001, consequence_type: "lof")
```

### `mcp__nlm__nlm_ct_codes` (Disease Coding & Gene Lookups)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_mesh` | Search MeSH terms for disease/gene concepts | `query`, `limit` |
| `get_mesh_details` | Full MeSH descriptor with tree numbers | `mesh_id` |
| `search_snomed` | Search SNOMED CT codes | `query`, `limit` |
| `get_snomed_details` | SNOMED concept details and hierarchy | `concept_id` |
| `search_icd10` | Search ICD-10 codes | `query`, `limit` |
| `search_rxnorm` | Search drug codes in RxNorm | `query`, `limit` |
| `get_rxnorm_details` | RxNorm concept details and relationships | `rxcui` |
| `search_gene` | Search gene information by symbol/name | `query`, `limit` |
| `get_gene_details` | Full gene record (aliases, location, function) | `gene_id` |
| `map_codes` | Cross-map between coding systems (MeSH, SNOMED, ICD-10) | `source_code`, `source_system`, `target_system` |
| `search_omim` | Search OMIM for Mendelian disease-gene links | `query`, `limit` |

### `mcp__gwas__gwas_data` (GWAS Catalog — Lead Variants & Associations)

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

**GWAS Catalog Workflow:** Use the GWAS Catalog to retrieve lead variants and trait associations for GWAS-nominated drug targets. In Step 1 (GWAS Gene Discovery), query `search_by_trait` or `search_associations` to identify all genome-wide significant loci for the disease of interest, complementing Open Targets with the full GWAS Catalog association landscape. Use `get_gene_associations` to retrieve all GWAS associations for a candidate drug target gene — multiple independent associations across traits strengthen the genetic evidence for target validity. Use `get_variant_associations` to check whether lead variants at a locus associate with related phenotypes (PheWAS-style), informing direction-of-effect analysis and potential on-target safety signals for drug repurposing in Step 5.

---

## 6-Step GWAS-to-Drug Pipeline

### Step 1: GWAS Gene Discovery

Identify genome-wide significant loci (p < 5x10^-8) and map them to causal genes.

```
1. mcp__nlm__nlm_ct_codes(method: "search_gene", query: "GENE_SYMBOL")
   -> Confirm gene identity, aliases, chromosomal location

2. mcp__nlm__nlm_ct_codes(method: "get_gene_details", gene_id: "GENE_ID")
   -> Full gene record: function, expression, orthologs

3. mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL")
   -> Get Ensembl ID, verify gene-target mapping

4. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "GENE_SYMBOL GWAS genome-wide association", journal: "", start_date: "", end_date: "", num_results: 20)
   -> Identify original GWAS publications reporting this locus

5. mcp__nlm__nlm_ct_codes(method: "search_omim", query: "GENE_SYMBOL")
   -> Check for Mendelian disease links (strongest genetic evidence)
```

**Genome-Wide Significance Threshold:**
- Standard threshold: p < 5x10^-8 (corrects for ~1 million independent tests across the genome)
- Suggestive threshold: p < 1x10^-5 (requires replication)
- Multiple testing correction: Bonferroni across ~1M independent common variants in European-ancestry LD structure

**Fine-Mapping Awareness:**
- Credible sets: smallest set of variants with >95% posterior probability of containing the causal variant
- Posterior inclusion probability (PIP): probability that a specific variant is causal
- L2G (Locus-to-Gene) score: >0.5 = high confidence gene assignment, >0.7 = very high confidence
- Fine-mapping methods: SuSiE, FINEMAP, CARMA for identifying causal variants within loci

**Multi-Ancestry Considerations:**
- Cross-ancestry replication strengthens causal inference (different LD patterns)
- Trans-ethnic fine-mapping narrows credible sets by leveraging LD differences
- Population-specific effects may indicate allele frequency or LD-driven signals
- Ancestry-specific GWAS (e.g., BioBank Japan, Africa Wits-INDEPTH, UKBB) provide complementary evidence

### Step 2: Druggability Evaluation

Assess whether GWAS-implicated genes encode druggable targets.

```
1. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Tractability data: small molecule, antibody, other modality buckets

2. mcp__chembl__chembl_info(method: "target_search", query: "GENE_SYMBOL")
   -> Existing ChEMBL target classification and known ligands

3. mcp__drugbank__drugbank_info(method: "search_by_target", target: "GENE_SYMBOL", limit: 20)
   -> Any existing drugs or investigational compounds for this target

4. mcp__chembl__chembl_info(method: "get_bioactivity", target_id: "CHEMBL_TARGET_ID", limit: 50)
   -> Known bioactivity data — are there potent compounds?
```

**Druggability Classification (Open Targets Tractability):**

| Category | Meaning | Confidence |
|----------|---------|------------|
| **Small molecule -- clinical** | SM drugs in clinical trials or approved for this target | Highest |
| **Small molecule -- discovery** | Ligandable binding site identified, compounds in discovery | High |
| **Antibody -- clinical** | Antibody drugs in clinical trials or approved | Highest |
| **Antibody -- predicted** | Extracellular/secreted protein, antibody-accessible | Medium |
| **Other modalities** | PROTAC, antisense, siRNA, gene therapy candidates | Variable |
| **Not tractable** | No known druggable modality identified | Lowest |

**Druggability Criteria for GWAS Targets:**

```
Highly druggable (proceed to prioritization):
+ Enzyme with well-defined active site
+ GPCR, ion channel, nuclear receptor (proven drug target families)
+ Existing clinical compounds (fast repurposing path)
+ Extracellular/membrane protein (biologic-accessible)
+ Known binding pocket with structural data

Potentially druggable (requires creative approaches):
~ Protein-protein interaction (PPI) — consider stapled peptides, macrocycles
~ Intracellular scaffold — consider PROTACs, molecular glues
~ Transcription factor — consider upstream pathway targets

Challenging (consider alternative strategies):
- No structural data available
- Essential housekeeping gene (toxicity risk)
- Redundant paralogs with compensatory function
- Disordered protein with no binding surface
```

### Step 3: Target Prioritization

Score and rank GWAS targets using composite evidence.

```
1. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   -> Genetic association score, overall evidence score

2. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.3, size: 50)
   -> Full competitive landscape — all targets ranked by evidence

3. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL target validation functional", num_results: 15)
   -> Published functional validation studies

4. mcp__nlm__nlm_ct_codes(method: "search_omim", query: "GENE_SYMBOL")
   -> Mendelian disease links strengthen causal inference
```

**Target Prioritization Score (TPS):**

```
TPS = (GWAS Score x 0.4) + (Druggability x 0.3) + (Clinical Evidence x 0.2) + (Novelty x 0.1)

Components:
- GWAS Score (0-1): Based on p-value strength, fine-mapping confidence (L2G),
  replication across cohorts, multi-ancestry support, Mendelian disease concordance
- Druggability (0-1): Open Targets tractability bucket, existing chemical matter,
  target family classification, structural data availability
- Clinical Evidence (0-1): Existing drugs for any indication, clinical trial activity,
  biomarker data linking target modulation to clinical outcome
- Novelty (0-1): Inverse of existing drug programs — higher for underexplored targets
  with strong genetic evidence (white space opportunity)
```

**Evidence Grading Tiers:**

| Tier | Criteria | Action |
|------|----------|--------|
| **T1 -- Validated** | Genome-wide significant (p < 5x10^-8), high-confidence fine-mapping (L2G > 0.5), replicated across ancestries, druggable target, existing compounds | Proceed to drug matching and repurposing |
| **T2 -- Strong** | Genome-wide significant, moderate fine-mapping confidence, druggable, limited existing pharmacology | Proceed with additional functional validation |
| **T3 -- Moderate** | Genome-wide significant but gene assignment uncertain, or druggability unclear | Requires fine-mapping and target characterization |
| **T4 -- Emerging** | Suggestive association (p < 1x10^-5), or significant but in gene desert with no clear effector gene | Monitor for replication, deprioritize for now |

### Step 4: Drug Matching

Identify existing drugs and compounds that modulate GWAS-implicated targets.

```
1. mcp__drugbank__drugbank_info(method: "search_by_target", target: "GENE_SYMBOL", limit: 30)
   -> All drugs (approved, investigational, experimental) for this target

2. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   -> Full drug profile: mechanism, indications, pharmacodynamics

3. mcp__chembl__chembl_info(method: "get_mechanism", chembl_id: "CHEMBLxxxxx")
   -> Mechanism of action — agonist, antagonist, inhibitor, etc.

4. mcp__fda__fda_info(method: "search_drugs", query: "drug_name", limit: 10)
   -> FDA approval status

5. mcp__fda__fda_info(method: "get_drug_label", drug_name: "drug_name")
   -> Full prescribing information, approved indications

6. mcp__drugbank__drugbank_info(method: "get_external_identifiers", drugbank_id: "DBxxxxx")
   -> Cross-reference IDs for consistent tracking across databases
```

**Direction-of-Effect Matching (Critical):**

```
GWAS finding implies:                Match with:
- Loss-of-function protective     -> Inhibitor / antagonist / knockdown
- Gain-of-function risk           -> Inhibitor / antagonist / negative modulator
- Loss-of-function risk           -> Agonist / activator / gene therapy
- Expression QTL (increased)      -> Inhibitor (if risk allele increases expression)
- Expression QTL (decreased)      -> Agonist (if risk allele decreases expression)

IMPORTANT: Direction of effect must be concordant. A GWAS locus where loss-of-function
is protective validates INHIBITORS of that target, not activators.
```

### Step 5: Repurposing Assessment

Evaluate whether matched drugs can be repurposed for the GWAS-indicated disease.

```
1. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   -> Current approved indications, mechanism, safety profile

2. mcp__fda__fda_info(method: "get_drug_label", drug_name: "drug_name")
   -> Full label: indications, contraindications, warnings

3. mcp__fda__fda_info(method: "search_adverse_events", drug_name: "drug_name", limit: 50)
   -> Post-market safety signals relevant to the new indication

4. mcp__drugbank__drugbank_info(method: "get_drug_interactions", drugbank_id: "DBxxxxx")
   -> Interaction risks for the target patient population

5. mcp__drugbank__drugbank_info(method: "get_similar_drugs", drugbank_id: "DBxxxxx", limit: 10)
   -> Alternative compounds in the same class

6. mcp__fda__fda_info(method: "get_orange_book", drug_name: "drug_name")
   -> Patent/exclusivity status (generic availability for repurposing)

7. mcp__nlm__nlm_ct_codes(method: "map_codes", source_code: "disease_code", source_system: "ICD10", target_system: "MeSH")
   -> Harmonize disease coding across databases for consistent searching
```

**Repurposing Feasibility Criteria:**

```
Strong repurposing candidate:
+ Approved drug with known safety profile
+ Genetic evidence supports the mechanism for new indication
+ Direction of effect is concordant (see Step 4)
+ Achievable target engagement at approved doses
+ Patent expired or nearing expiry (commercial feasibility)
+ No contraindication for the target patient population

Moderate candidate (requires additional work):
~ Investigational compound with Phase II+ safety data
~ Requires dose adjustment for new indication
~ On-patent but licensable

Weak candidate (high risk):
- Preclinical compound only
- Direction of effect unclear or potentially discordant
- Known toxicity overlapping with target disease comorbidities
- Narrow therapeutic index
```

### Step 6: Clinical Evidence Review

Evaluate existing clinical evidence and trial activity for genetically-supported targets.

```
1. mcp__ctgov__ctgov_info(method: "search_studies", condition: "disease_name", intervention: "drug_name", limit: 20)
   -> Existing trials for this drug-disease combination

2. mcp__ctgov__ctgov_info(method: "get_study_details", nct_id: "NCTxxxxxxxx")
   -> Trial design, endpoints, enrollment

3. mcp__ctgov__ctgov_info(method: "get_study_results", nct_id: "NCTxxxxxxxx")
   -> Completed trial results and outcomes

4. mcp__ctgov__ctgov_info(method: "search_by_sponsor", sponsor: "company_name", status: "RECRUITING", limit: 20)
   -> Active pipeline for this target/indication

5. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "GENE_SYMBOL drug_name clinical trial", journal: "", start_date: "", end_date: "", num_results: 15)
   -> Published trial results and clinical evidence

6. mcp__fda__fda_info(method: "get_approval_history", application_number: "NDAxxxxxx")
   -> Regulatory history and supplemental approvals
```

---

## Genetic Evidence Value Framework

### Nelson et al. (Nature Genetics 2015) Reference

Targets with human genetic support have approximately **2x higher probability of clinical approval** compared to targets without genetic evidence. This foundational finding underpins the entire GWAS-to-drug strategy:

- Genetic association provides causal anchoring that observational data cannot
- GWAS targets are enriched among successful drug programs
- The effect holds across therapeutic areas and target classes
- Strongest effect seen when direction of effect is concordant with drug mechanism

### Genetic Evidence Hierarchy for Drug Discovery

| Evidence Type | Strength | Example |
|--------------|----------|---------|
| **Mendelian disease** | Strongest | PCSK9 loss-of-function -> low LDL -> PCSK9 inhibitors |
| **GWAS + fine-mapping + functional** | Very strong | IL23R variants -> IBD protection -> anti-IL-23 antibodies |
| **GWAS + fine-mapping** | Strong | GWAS locus fine-mapped to single credible variant in gene |
| **GWAS locus (no fine-mapping)** | Moderate | Genome-wide significant but multiple candidate genes |
| **Mendelian randomization** | Supportive | MR analysis supporting causal direction |
| **PheWAS cross-phenotype** | Supportive | Same variant associates with multiple related traits |
| **eQTL/pQTL colocalization** | Supportive | GWAS signal colocalizes with expression/protein QTL |

### Interpreting Open Targets Genetic Association Scores

```
Open Targets genetic_association datasource scores:
- Score > 0.7: Strong genetic link (multiple evidence lines)
- Score 0.4-0.7: Moderate (typically single GWAS + some functional)
- Score 0.1-0.4: Suggestive (GWAS only, borderline significance)
- Score < 0.1: Weak (text mining, low-powered studies)

Always check the evidence breakdown:
- ot_genetics_portal: GWAS catalog associations with L2G scores
- gene_burden: Rare variant burden test evidence
- eva: ClinVar pathogenic variant evidence
- genomics_england: GEL PanelApp gene-disease curation
- gene2phenotype: Expert-curated gene-disease relationships
```

---

## Multi-Ancestry GWAS Analysis

### Workflow for Cross-Ancestry Validation

```
1. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "GENE_SYMBOL GWAS multi-ancestry trans-ethnic", journal: "", start_date: "", end_date: "", num_results: 15)
   -> Find multi-ancestry GWAS publications

2. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   -> Check if genetic evidence spans multiple ancestry sources

3. mcp__nlm__nlm_ct_codes(method: "search_gene", query: "GENE_SYMBOL")
   -> Gene-level information including population genetics context
```

**Multi-Ancestry Interpretation:**

```
Cross-ancestry replication scenarios:
1. Signal replicates across ancestries at same variant
   -> Strong evidence for causality (different LD, same signal)

2. Signal replicates at same locus but different lead variant
   -> Likely same causal gene, LD differences explain lead variant shift

3. Signal present in one ancestry only
   -> Could be: allele frequency difference, population-specific LD,
      gene-environment interaction, or false positive
   -> Check minor allele frequency in gnomAD across populations

4. Fine-mapping narrows credible set in multi-ancestry analysis
   -> Major advantage of trans-ethnic approaches — use the tighter
      credible set for causal gene assignment
```

---

## Competitive Landscape for GWAS-Supported Targets

### Workflow

```
1. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.3, size: 50)
   -> All genetically-supported targets for this disease, ranked

2. For each top target:
   mcp__drugbank__drugbank_info(method: "search_by_target", target: "GENE_SYMBOL")
   -> Existing drugs and development programs

3. mcp__ctgov__ctgov_info(method: "search_studies", condition: "disease_name", status: "RECRUITING", limit: 30)
   -> Active clinical pipeline — identify white space vs crowded targets

4. mcp__fda__fda_info(method: "search_drugs", query: "disease_name", limit: 20)
   -> Already approved therapies for this indication

5. mcp__chembl__chembl_info(method: "drug_search", query: "disease_name", limit: 30)
   -> Full drug landscape in ChEMBL

6. Identify white space:
   Targets with strong genetic evidence (T1/T2) but NO existing drug programs
   -> These are the highest-value opportunities
```

---

## GWAS-to-Drug Success Stories (Reference Framework)

Use these validated examples to calibrate analysis and communicate value:

| GWAS Discovery | Target | Drug | Indication | Status |
|---------------|--------|------|------------|--------|
| PCSK9 loss-of-function protective | PCSK9 | Evolocumab, Alirocumab | Hypercholesterolemia | Approved |
| IL23R variants protective for IBD | IL-23 (p19) | Risankizumab, Guselkumab | Crohn's, Psoriasis | Approved |
| HMGCR variants associate with LDL | HMG-CoA reductase | Statins | Hypercholesterolemia | Approved (pre-GWAS, genetically validated) |
| SLC30A8 loss-of-function protective | ZnT8 | Under investigation | Type 2 Diabetes | Discovery |
| ANGPTL3 loss-of-function protective | ANGPTL3 | Evinacumab | Familial hypercholesterolemia | Approved |

---

## Multi-Agent Workflow Examples

**"Translate GWAS hits for Type 2 Diabetes into drug targets"**
1. GWAS Drug Discoverer -> Identify genome-wide significant loci, map to genes via L2G, assess druggability, match to existing drugs, score repurposing candidates
2. Drug Target Analyst -> Deep SAR analysis for top-priority targets, bioactivity data review
3. Drug Target Validator -> Independent validation evidence (functional genomics, animal models)
4. Clinical Trial Analyst -> Pipeline intelligence for genetically-supported targets, identify gaps

**"Evaluate repurposing opportunities from Alzheimer's GWAS"**
1. GWAS Drug Discoverer -> Extract GWAS targets, druggability screening, drug matching with direction-of-effect analysis
2. Drug Repurposing Analyst -> Systematic repurposing scoring, indication expansion feasibility
3. Network Pharmacologist -> Pathway context for GWAS loci, network-based drug predictions
4. Precision Medicine Stratifier -> Genotype-based patient selection for repurposed drugs

**"Prioritize genetically-supported targets for inflammatory bowel disease"**
1. GWAS Drug Discoverer -> Full 6-step pipeline: GWAS gene discovery, druggability evaluation, target prioritization scoring (TPS), drug matching, repurposing assessment
2. Drug Target Analyst -> Competitive target landscape, existing compound potency analysis
3. Clinical Trial Analyst -> Active trials for each target, phase distribution, success rates
4. Network Pharmacologist -> Shared pathways across IBD GWAS targets, combination opportunities

**"Assess a novel GWAS locus for drug discovery potential"**
1. GWAS Drug Discoverer -> Fine-mapping assessment, L2G confidence, multi-ancestry replication, druggability classification, evidence tier assignment
2. Drug Target Validator -> Functional evidence review, CRISPR/model organism data
3. Drug Target Analyst -> Chemical tractability deep-dive, existing ligands, structural data
4. Precision Medicine Stratifier -> Effect size and allele frequency implications for patient stratification

---

## Completeness Checklist

- [ ] GWAS gene discovery completed with gene identity confirmed via NLM and Open Targets
- [ ] Druggability evaluated using Open Targets tractability and ChEMBL target classification
- [ ] Target prioritization score (TPS) computed with GWAS, druggability, clinical, and novelty components
- [ ] Direction-of-effect matching performed (LoF protective → inhibitor, etc.)
- [ ] Drug matching completed via DrugBank and ChEMBL with mechanism of action identified
- [ ] Repurposing feasibility assessed (safety profile, patent status, dose achievability)
- [ ] Clinical trial landscape reviewed via ClinicalTrials.gov for target-indication pairs
- [ ] Multi-ancestry GWAS evidence checked for cross-population replication
- [ ] Evidence tier (T1-T4) assigned to each GWAS target
- [ ] Report file created with no remaining `[Analyzing...]` placeholders
