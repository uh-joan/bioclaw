---
name: spatial-omics-analysis
description: Biological interpretation of spatial multi-omics data. Transforms spatially variable genes, domain annotations, and tissue context into pathway enrichment, cell interactions, druggable targets, and immune characterization. Use when user mentions spatial omics, spatial transcriptomics analysis, spatially variable genes, SVGs, spatial domains, tissue architecture, cell-cell interactions, ligand-receptor pairs, spatial gene expression, domain annotation, immune microenvironment, spatial multi-omics, Visium, MERFISH, Slide-seq, spatial proteomics, spatial metabolomics, or Spatial Omics Integration Score.
---

# Spatial Omics Analysis

Biological interpretation of spatial multi-omics data. Integrates spatially variable genes, domain annotations, and tissue context to produce pathway enrichment, cell-cell interaction maps, druggable target identification, and immune microenvironment characterization. Uses Open Targets for target-disease associations, ChEMBL for compound bioactivity, DrugBank for drug-target pharmacology, PubMed for literature evidence, and ClinicalTrials.gov for therapeutic pipeline intelligence. Produces a Spatial Omics Integration Score (0-100).

## Report-First Workflow

1. **Create report file immediately**: `[tissue]_spatial_omics_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill
- Spatial transcriptomics preprocessing, QC, and SVG detection → use `spatial-transcriptomics`
- Single-cell deconvolution without spatial context → use `single-cell-analysis`
- General gene set enrichment analysis → use `gene-enrichment`
- Network-level pathway modeling → use `systems-biology`
- Deep target validation and druggability assessment → use `target-research`
- Multi-omic disease characterization without spatial data → use `multiomic-disease-characterization`

## Cross-Reference: Other Skills

- **Spatial transcriptomics preprocessing and SVG detection** -> use spatial-transcriptomics skill
- **Single-cell deconvolution of spatial data** -> use single-cell-analysis skill
- **Pathway and gene set enrichment analysis** -> use gene-enrichment skill
- **Network-level pathway modeling** -> use systems-biology skill
- **Multi-omic disease characterization** -> use multiomic-disease-characterization skill
- **Druggable target deep-dive and validation** -> use target-research skill

## Available MCP Tools

### `mcp__opentargets__opentargets_info` (Target-Disease Associations)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `search_diseases` | Search diseases by name/synonym | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId` (Ensembl ID), `diseaseId` (EFO ID), `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes) | `id` (EFO ID) |

### `mcp__chembl__chembl_info` (Bioactivity & SAR)

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

### `mcp__pubmed__pubmed_articles` (Spatial Omics Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__ctgov__ctgov_info` (Clinical Trial Intelligence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search clinical trials | `condition`, `intervention`, `phase`, `status`, `location`, `lead`, `ages`, `studyType`, `pageSize` |
| `get` | Get full trial details by NCT ID | `nctId` |
| `suggest` | Autocomplete terms | `input`, `dictionary` |
| `stats` | Trial statistics and counts | `condition`, `intervention` |

---

## 9-Phase Spatial Omics Interpretation Workflow

### Phase 1: Input Disambiguation

```
Identify input data type and context:
- Spatially variable gene lists (SVGs from SpatialDE, SPARK, nnSVG)
- Domain/cluster annotations (e.g., BayesSpace, SpaGCN, STAGATE domains)
- Tissue type and pathological context
- Technology platform (Visium, MERFISH, Slide-seq, CODEX, spatial ATAC)
- Species and reference genome

Parse user input:
- Gene lists: split by domain/region if provided
- Domain labels: map to tissue compartments (tumor core, invasive margin, stroma, immune infiltrate, necrotic, normal adjacent)
- Clinical context: disease, stage, treatment status
```

### Phase 2: Gene Characterization

```
For each spatially variable gene or domain-specific marker:

1. mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL")
   -> Get Ensembl gene ID, protein class, subcellular location

2. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Full target profile: function, pathways, tractability, protein interactions

3. mcp__chembl__chembl_info(method: "target_search", query: "GENE_SYMBOL")
   -> ChEMBL target classification, target type

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL spatial transcriptomics expression", num_results: 5)
   -> Published spatial expression context

Classify each gene:
- Functional category: receptor, ligand, transcription factor, kinase, metabolic enzyme, structural, immune marker
- Spatial relevance: domain-restricted, gradient, ubiquitous, interface-enriched
```

### Phase 3: Pathway Enrichment

```
Group genes by spatial domain and perform pathway analysis:

1. For each domain gene set, query pathway databases:
   mcp__drugbank__drugbank_info(method: "search_by_target", target: "GENE_SYMBOL")
   -> Pathway involvement for each gene

2. mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   -> Detailed pathway mapping for drugged targets

3. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Reactome pathways, GO terms from target details

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "PATHWAY_NAME spatial tissue DISEASE_CONTEXT", num_results: 10)
   -> Literature support for pathway activation in spatial context

Aggregate into pathway categories:
- Signaling: Wnt, Hedgehog, Notch, TGF-beta, MAPK, PI3K/AKT/mTOR, JAK/STAT, NF-kB
- Metabolic: glycolysis, oxidative phosphorylation, fatty acid metabolism, amino acid metabolism
- Immune: antigen presentation, T cell activation, complement, cytokine signaling
- ECM/adhesion: integrin signaling, focal adhesion, matrix remodeling
- Cell cycle/proliferation: DNA replication, mitosis, apoptosis
```

### Phase 4: Domain-by-Domain Analysis

```
For each spatial domain/cluster:

1. Identify top marker genes (by spatial variability score or fold change)

2. Characterize domain biological identity:
   - Cell type composition (from marker genes)
   - Dominant pathways (from Phase 3)
   - Functional state (proliferating, quiescent, stressed, activated)

3. For key domain markers, assess disease relevance:
   mcp__opentargets__opentargets_info(method: "search_diseases", query: "DISEASE_NAME")
   -> Get EFO disease ID

   mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   -> Association score and evidence breakdown

4. Domain-specific drug target identification:
   mcp__drugbank__drugbank_info(method: "search_by_target", target: "DOMAIN_MARKER_GENE")
   -> Existing drugs targeting domain-specific genes

Output per domain:
- Domain identity and cell composition
- Top 5 pathways with evidence level
- Druggable targets ranked by tractability
- Clinical relevance score
```

### Phase 5: Cell-Cell Interactions

```
Analyze ligand-receptor pairs across spatial domains:

1. For each putative ligand-receptor pair at domain interfaces:
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG_LIGAND")
   -> Confirm ligand function and known receptors

   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG_RECEPTOR")
   -> Confirm receptor function and downstream signaling

2. Assess druggability of interaction:
   mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "CHEMBL_RECEPTOR_ID", limit: 20)
   -> Existing compounds targeting the receptor

   mcp__drugbank__drugbank_info(method: "search_by_target", target: "RECEPTOR_NAME")
   -> Approved drugs blocking this interaction

3. Literature validation:
   mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "LIGAND RECEPTOR cell interaction spatial TISSUE_TYPE", num_results: 10)
   -> Published evidence for this interaction in spatial context

Interaction categories:
- Paracrine signaling (ligand in domain A, receptor in domain B)
- Juxtacrine signaling (contact-dependent, interface-enriched)
- Autocrine loops (ligand and receptor co-expressed in same domain)
- ECM-mediated (matrix components bridging domains)
```

### Phase 6: Disease and Therapeutic Context

```
1. Map spatially variable genes to disease associations:
   mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.3, size: 50)
   -> All validated targets for the disease, cross-reference with SVG list

2. Identify therapeutic opportunities per domain:
   mcp__chembl__chembl_info(method: "drug_search", query: "DISEASE_NAME", limit: 30)
   -> Approved and investigational drugs

3. Clinical pipeline for spatially identified targets:
   mcp__ctgov__ctgov_info(method: "search", condition: "DISEASE_NAME", intervention: "TARGET_GENE inhibitor", pageSize: 20)
   -> Active trials targeting domain-specific genes

   mcp__ctgov__ctgov_info(method: "stats", condition: "DISEASE_NAME", intervention: "TARGET_GENE")
   -> Trial landscape and phase distribution

4. Drug repurposing opportunities:
   mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   -> Full pharmacology for drugs hitting spatially enriched targets

   mcp__drugbank__drugbank_info(method: "get_similar_drugs", drugbank_id: "DBxxxxx", limit: 10)
   -> Structurally or pharmacologically similar alternatives
```

### Phase 7: Multi-Modal Integration

```
Integrate findings across data modalities (when available):

1. Spatial transcriptomics + spatial proteomics:
   - Concordance: genes with matching protein spatial patterns
   - Discordance: post-transcriptional regulation candidates

2. Spatial transcriptomics + spatial ATAC-seq:
   - Chromatin accessibility at spatially variable gene loci
   - Transcription factor motif enrichment per domain

3. Spatial transcriptomics + spatial metabolomics:
   - Metabolic pathway activation correlated with enzyme expression
   - Metabolite-gene spatial co-localization

For each integrated finding:
   mcp__pubmed__pubmed_articles(method: "search_advanced", term: "GENE multi-omics spatial integration TISSUE", num_results: 10)
   -> Literature support for multi-modal observations

Cross-modal validation score:
- Single modality support: +5 points
- Two modalities concordant: +15 points
- Three+ modalities concordant: +25 points
```

### Phase 8: Immune Microenvironment Profiling

```
Characterize the spatial immune landscape:

1. Immune cell marker identification per domain:
   - T cells: CD3D, CD3E, CD4, CD8A, CD8B, FOXP3 (Treg), PDCD1 (PD-1)
   - B cells: CD19, CD20 (MS4A1), CD79A, IGHG1
   - Macrophages: CD68, CD163 (M2), CD80/CD86 (M1), MARCO
   - NK cells: NCAM1 (CD56), NKG7, GNLY, KLRB1
   - Dendritic cells: ITGAX (CD11c), CLEC9A, CD1C
   - Neutrophils: FCGR3B, CSF3R, CXCR2
   - Mast cells: KIT, TPSAB1, CPA3

2. Checkpoint and immunotherapy targets:
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG_CHECKPOINT_GENE")
   -> Tractability and drug landscape for checkpoint molecules

   mcp__drugbank__drugbank_info(method: "search_by_target", target: "PD-L1")
   -> Approved checkpoint inhibitors

   mcp__chembl__chembl_info(method: "drug_search", query: "checkpoint inhibitor", limit: 20)
   -> All checkpoint-targeting compounds

3. Spatial immune patterns:
   - Hot zones: high immune infiltration, checkpoint expression
   - Cold zones: immune-excluded or immune-desert regions
   - Tertiary lymphoid structures: B cell and T cell co-localization
   - Immune-stromal interfaces: myeloid cell enrichment at boundaries

4. Immunotherapy response prediction:
   mcp__ctgov__ctgov_info(method: "search", condition: "DISEASE_NAME", intervention: "immunotherapy", pageSize: 20)
   -> Immunotherapy trials for this indication

   mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "spatial immune microenvironment DISEASE_NAME immunotherapy response prediction", num_results: 15)
   -> Literature on spatial immune predictors

Immune characterization output:
- Immune cell composition per domain (proportions)
- Immune phenotype: hot, cold, excluded, compartmentalized
- Checkpoint expression map: PD-L1, CTLA-4, LAG-3, TIM-3, TIGIT spatial distribution
- Immunotherapy target ranking with evidence tier
```

### Phase 9: Validation Recommendations

```
Generate experimental validation plan:

1. Spatial validation:
   - Multiplexed immunofluorescence (mIF) for top protein targets
   - RNAscope/smFISH for key SVGs requiring transcript-level confirmation
   - Spatial ATAC-seq for chromatin accessibility validation

2. Functional validation:
   - CRISPR perturbation of domain-specific targets
   - Organoid co-culture for cell-cell interaction validation
   - Drug sensitivity testing on spatially defined subpopulations

3. Clinical translation:
   mcp__ctgov__ctgov_info(method: "search", condition: "DISEASE_NAME", intervention: "SPATIAL_TARGET", pageSize: 10)
   -> Existing trials targeting spatially identified targets

   mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "SPATIAL_TARGET biomarker DISEASE_NAME clinical", num_results: 10)
   -> Published clinical biomarker evidence

4. Prioritize validation targets by:
   - Spatial specificity (domain-restricted > gradient > ubiquitous)
   - Druggability (Tclin > Tchem > Tbio > Tdark)
   - Disease association strength (Open Targets score > 0.5)
   - Immune relevance (checkpoint or immune effector)
   - Clinical pipeline activity (active trials = higher priority)
```

---

## Spatial Omics Integration Score (0-100)

### Scoring Framework

| Component | Points | Criteria |
|-----------|--------|----------|
| **Data Completeness** | 0-30 | Coverage of input data types and domains |
| **Biological Insight Depth** | 0-40 | Pathway, interaction, and immune characterization quality |
| **Evidence Quality** | 0-30 | Strength and concordance of supporting evidence |

### Data Completeness (0-30)

| Criterion | Points |
|-----------|--------|
| SVG list provided with statistics | 5 |
| Domain/cluster annotations present | 5 |
| Tissue type and disease context specified | 5 |
| Multiple spatial modalities available | 5 |
| Clinical metadata (stage, treatment) provided | 5 |
| Ligand-receptor pair data or cell type deconvolution included | 5 |

### Biological Insight Depth (0-40)

| Criterion | Points |
|-----------|--------|
| Pathway enrichment completed for all domains | 8 |
| Cell-cell interaction network characterized | 8 |
| Immune microenvironment profiled | 8 |
| Druggable targets identified with tractability | 8 |
| Domain-specific biological narratives constructed | 8 |

### Evidence Quality (0-30)

| Criterion | Points |
|-----------|--------|
| Target-disease associations from Open Targets (score > 0.5) | 6 |
| Bioactivity data from ChEMBL (nanomolar compounds) | 6 |
| Drug-target relationships from DrugBank confirmed | 6 |
| Literature support from PubMed (>5 relevant publications) | 6 |
| Clinical trial evidence from ClinicalTrials.gov | 6 |

### Score Interpretation

| Range | Interpretation | Action |
|-------|---------------|--------|
| **80-100** | Comprehensive spatial omics integration | Results suitable for clinical translation planning |
| **60-79** | Strong integration with minor gaps | Address specific missing evidence domains |
| **40-59** | Moderate integration | Additional data modalities or deeper analysis recommended |
| **20-39** | Preliminary integration | Significant gaps; prioritize missing phases |
| **0-19** | Insufficient data | Requires additional spatial data collection |

---

## Evidence Grading System (T1-T4)

| Tier | Evidence Type | Description |
|------|-------------|-------------|
| **T1 (Strongest)** | Clinical proof | Approved drugs targeting the gene/pathway; clinical trial efficacy data; validated clinical biomarker |
| **T2** | Strong preclinical | Human genetic evidence (GWAS, somatic mutations); functional genomics validation (CRISPR); concordant multi-omics data |
| **T3** | Moderate evidence | Animal model data; in vitro functional studies; pathway inference from literature; single-modality spatial data |
| **T4 (Weakest)** | Hypothesis level | Text mining associations; computational predictions; single-study observations without replication |

### Applying Evidence Tiers to Spatial Findings

```
For each spatially variable gene or domain finding:

1. Check clinical evidence:
   mcp__drugbank__drugbank_info(method: "search_by_target", target: "GENE_SYMBOL")
   -> If approved drug exists -> T1

   mcp__ctgov__ctgov_info(method: "search", intervention: "GENE_SYMBOL", pageSize: 5)
   -> If active clinical trials -> T1-T2

2. Check genetic evidence:
   mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   -> If genetic_association score > 0.5 -> T2
   -> If overall score > 0.7 -> T1-T2

3. Check functional evidence:
   mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "CHEMBLxxxxx", limit: 20)
   -> If nanomolar compounds with functional data -> T2-T3

4. Check literature:
   mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL spatial DISEASE functional", num_results: 10)
   -> If >5 functional studies -> T2-T3
   -> If only co-mention -> T4
```

---

## Domain-Specific Recommendations

### Per-Domain Output Template

```
DOMAIN: [Domain ID / Tissue Compartment Name]

IDENTITY:
- Cell type composition: [e.g., 60% tumor cells, 25% fibroblasts, 15% macrophages]
- Functional state: [proliferating / quiescent / inflammatory / hypoxic]

TOP GENES (by spatial variability):
1. GENE_A — [function] — Evidence: T[1-4]
2. GENE_B — [function] — Evidence: T[1-4]
3. GENE_C — [function] — Evidence: T[1-4]

PATHWAYS:
- [Pathway 1]: activated / suppressed — Evidence: T[1-4]
- [Pathway 2]: activated / suppressed — Evidence: T[1-4]

DRUGGABLE TARGETS:
| Gene | Drug | Mechanism | Status | Evidence |
|------|------|-----------|--------|----------|
| GENE_A | Drug_X | Inhibitor | Approved | T1 |
| GENE_B | Drug_Y | Antagonist | Phase III | T2 |

INTERACTIONS WITH ADJACENT DOMAINS:
- Domain X <-> Domain Y: LIGAND-RECEPTOR pair — [biological significance]

CLINICAL RELEVANCE:
- Disease association score: [Open Targets score]
- Active trials: [count from ClinicalTrials.gov]
- Biomarker potential: [high / moderate / low]
```

---

## Immune Microenvironment Profiling

### Immune Cell Marker Reference

| Cell Type | Primary Markers | Activation Markers | Exhaustion Markers |
|-----------|----------------|-------------------|-------------------|
| CD8+ T cells | CD8A, CD8B | GZMB, PRF1, IFNG | PDCD1, HAVCR2, LAG3, TIGIT |
| CD4+ T helper | CD4, IL7R | IFNG, IL2, TNF | PDCD1, CTLA4 |
| Tregs | CD4, FOXP3, IL2RA | CTLA4, TNFRSF18 | — |
| B cells | MS4A1, CD79A, CD19 | AICDA, MKI67 | — |
| Plasma cells | SDC1, XBP1, IGHG1 | — | — |
| M1 macrophages | CD68, CD80, CD86 | NOS2, IL1B, TNF | — |
| M2 macrophages | CD68, CD163, MRC1 | ARG1, IL10, TGFB1 | — |
| NK cells | NCAM1, NKG7, GNLY | GZMB, PRF1 | KLRG1, TIGIT |
| cDC1 | CLEC9A, XCR1, BATF3 | IL12A, IL12B | — |
| cDC2 | CD1C, CLEC10A | IL23A, TNF | — |
| Neutrophils | FCGR3B, CSF3R, CXCR2 | IL1B, CXCL8 | — |
| Mast cells | KIT, TPSAB1, CPA3 | IL4, IL13 | — |

### Checkpoint Expression Spatial Map

```
For each checkpoint molecule (PD-L1/CD274, PD-1/PDCD1, CTLA-4, LAG-3, TIM-3/HAVCR2, TIGIT, VISTA/VSIR):

1. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG_CHECKPOINT")
   -> Tractability assessment for therapeutic targeting

2. mcp__drugbank__drugbank_info(method: "search_by_target", target: "CHECKPOINT_NAME")
   -> Approved and investigational checkpoint inhibitors

3. Spatial pattern classification:
   - Diffuse expression: checkpoint expressed across all domains
   - Interface-restricted: checkpoint enriched at tumor-immune boundary
   - Domain-restricted: checkpoint confined to specific immune domain
   - Absent: no significant checkpoint expression detected

4. Therapeutic implication:
   - Diffuse PD-L1 + CD8+ infiltrate -> likely checkpoint responder
   - Interface PD-L1 only -> potential responder with combination therapy
   - Absent checkpoint + no infiltrate -> immune cold, consider priming strategies
```

### Immune Phenotype Classification

| Phenotype | Spatial Features | Therapeutic Implications |
|-----------|-----------------|------------------------|
| **Hot (inflamed)** | Dense immune infiltrate throughout tumor, high checkpoint expression | Checkpoint inhibitor monotherapy candidate |
| **Excluded** | Immune cells at tumor periphery but not infiltrating | Combination with stromal remodeling (TGF-beta, CXCL12) |
| **Cold (desert)** | Minimal immune cells in or around tumor | Immune priming needed (vaccination, oncolytic virus, STING agonist) |
| **Compartmentalized** | Tertiary lymphoid structures, organized immune aggregates | Favorable prognosis indicator, may respond to checkpoint therapy |

---

## Multi-Agent Workflow Examples

**"Interpret spatially variable genes from a Visium breast cancer experiment"**
1. Spatial Omics Analysis -> SVG characterization, domain analysis, pathway enrichment, immune profiling, druggable targets with Spatial Omics Integration Score
2. Gene Enrichment -> Deep gene set enrichment across MSigDB, KEGG, Reactome for domain-specific gene lists
3. Target Research -> Full druggability assessment for top spatially restricted targets
4. Systems Biology -> Network modeling of domain-specific pathway crosstalk

**"Characterize the tumor immune microenvironment from spatial multi-omics data"**
1. Spatial Omics Analysis -> Immune cell marker mapping, checkpoint spatial distribution, immune phenotype classification, immunotherapy target ranking
2. Single Cell Analysis -> Deconvolution of spatial domains into cell type proportions, cell state assignment
3. Multiomic Disease Characterization -> Integration of spatial transcriptomics with proteomics and metabolomics for immune contextualization
4. Spatial Transcriptomics -> Preprocessing, SVG detection, spatial autocorrelation analysis

**"Identify druggable targets in spatially defined tumor subclones"**
1. Spatial Omics Analysis -> Domain-by-domain target identification, pathway enrichment, evidence grading, clinical pipeline assessment
2. Target Research -> Deep target validation for top candidates: genetics, bioactivity, selectivity, tractability
3. Gene Enrichment -> Pathway analysis per spatial domain with statistical rigor
4. Systems Biology -> Pathway crosstalk between tumor subclones and microenvironment

**"Evaluate spatial ligand-receptor interactions for therapeutic intervention"**
1. Spatial Omics Analysis -> Ligand-receptor pair mapping across domain interfaces, druggability assessment, clinical trial landscape
2. Target Research -> Mechanism of action analysis for drugs targeting identified receptors
3. Multiomic Disease Characterization -> Multi-modal validation of interaction networks
4. Single Cell Analysis -> Cell-type resolution of ligand and receptor expression

## Completeness Checklist
- [ ] Input data type identified (SVGs, domains, tissue context, platform)
- [ ] Gene characterization completed for all spatially variable genes
- [ ] Pathway enrichment performed per spatial domain
- [ ] Domain-by-domain biological narrative constructed
- [ ] Cell-cell interaction network mapped across domain interfaces
- [ ] Immune microenvironment profiled with checkpoint expression map
- [ ] Druggable targets identified with tractability and evidence tier
- [ ] Clinical trial landscape assessed for top targets
- [ ] Spatial Omics Integration Score calculated (0-100)
- [ ] Validation recommendations prioritized by spatial specificity and druggability
