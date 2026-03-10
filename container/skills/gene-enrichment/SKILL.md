---
name: gene-enrichment
description: Comprehensive gene enrichment analysis specialist. Over-Representation Analysis (ORA) and Gene Set Enrichment Analysis (GSEA) across GO, KEGG, Reactome, WikiPathways, and MSigDB. Cross-validation, multiple testing correction, and evidence grading. Use when user mentions gene enrichment, pathway enrichment, ORA, GSEA, gene ontology, GO terms, KEGG pathways, Reactome, WikiPathways, MSigDB, hallmark gene sets, functional enrichment, gene set analysis, overrepresentation, FDR correction, Benjamini-Hochberg, enriched pathways, gene list analysis, or biological process enrichment.
---

# Gene Enrichment

> **Code recipes**: See [recipes.md](recipes.md) for general enrichment templates, and [gsea-recipes.md](gsea-recipes.md) for GSEA/ORA with clusterProfiler, fgsea, GSEApy, MSigDB collections, ReactomePA, and multi-condition comparison.

Comprehensive gene enrichment analysis using Over-Representation Analysis (ORA) and Gene Set Enrichment Analysis (GSEA) across multiple pathway databases. Uses Open Targets for gene-disease context, ChEMBL for pharmacological pathway mapping, DrugBank for drug-pathway relationships, PubMed for literature evidence, PubChem for chemical-gene interactions, and NLM for gene ID resolution and cross-referencing.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_gene_enrichment_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Drug target druggability and tractability assessment → use `drug-target-analyst`
- Protein interaction network topology and hub analysis → use `network-pharmacologist`
- Disease-gene association context and phenotype mapping → use `disease-research`
- Systems-level pathway modeling and flux analysis → use `systems-biology`
- Target validation with multi-evidence scoring → use `target-research`
- Gene Ontology term lookup and validation (without enrichment) → use `geneontology`

## Cross-Reference: Other Skills

- **Target druggability for enriched genes** → use drug-target-analyst skill
- **Network topology of enriched pathways** → use network-pharmacologist skill
- **Disease context for enriched gene sets** → use disease-research skill
- **Systems-level pathway integration** → use systems-biology skill
- **Target validation for top hits** → use target-research skill

## Available MCP Tools

### `mcp__opentargets__opentargets_info` (Gene-Disease Context)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `search_diseases` | Search diseases by name/synonym | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId` (Ensembl ID), `diseaseId` (EFO ID), `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes) | `id` (EFO ID) |

### `mcp__chembl__chembl_info` (Pharmacological Pathway Mapping)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |
| `get_admet` | ADMET/drug-likeness properties | `chembl_id` |

### `mcp__drugbank__drugbank_info` (Drug-Pathway Relationships)

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

### `mcp__pubmed__pubmed_articles` (Enrichment Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__pubchem__pubchem_info` (Chemical-Gene Interactions)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_compound` | Search compounds by name or identifier | `query`, `limit` |
| `get_compound_details` | Full compound profile | `cid` |
| `get_compound_properties` | Physicochemical properties | `cid` |
| `get_compound_synonyms` | All names and identifiers for a compound | `cid` |
| `get_bioassays` | Bioassay results for a compound | `cid`, `limit` |
| `get_gene_interactions` | Chemical-gene interaction data | `cid`, `limit` |
| `search_by_formula` | Search by molecular formula | `formula`, `limit` |
| `search_by_structure` | Structural similarity/substructure search | `smiles`, `search_type`, `limit` |
| `get_compound_classification` | Compound classification hierarchy | `cid` |
| `get_patent_info` | Patent data linked to compound | `cid`, `limit` |
| `get_safety_info` | GHS hazard, toxicity, and safety data | `cid` |
| `get_pharmacology` | Pharmacology and drug interaction data | `cid` |

### `mcp__stringdb__stringdb_data` (Protein-Level Functional Enrichment)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_functional_enrichment` | GO/KEGG/Reactome enrichment for protein set | `protein_ids`, `species`, `background_string_identifiers` |
| `get_protein_annotations` | Get functional annotations | `protein_ids`, `species` |
| `search_proteins` | Search proteins by name | `query`, `species`, `limit` |

### `mcp__kegg__kegg_data` (Pathway & Gene-Pathway Mapping)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_pathways` | Search KEGG pathways by keyword | `query` |
| `get_pathway_info` | Full pathway details (description, classes, modules) | `pathway_id` |
| `get_pathway_genes` | All genes in a pathway (for overlap calculation) | `pathway_id` |
| `get_pathway_compounds` | All compounds in a pathway | `pathway_id` |
| `search_genes` | Search genes by keyword | `query` |
| `get_gene_info` | Gene details (orthologs, pathways, motifs) | `gene_id` |
| `convert_identifiers` | Convert between KEGG and external IDs (Ensembl, NCBI) | `identifiers`, `source_db`, `target_db` |
| `batch_entry_lookup` | Batch lookup of multiple KEGG entries | `entry_ids` |
| `find_related_entries` | Find entries related to a given KEGG entry | `entry_id` |

### `mcp__reactome__reactome_data` (Pathway Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_pathways` | Search pathways by keyword | `query`, `species` |
| `get_pathway_details` | Full pathway info | `pathway_id` |
| `find_pathways_by_gene` | Pathways containing a gene | `gene_id`, `species` |
| `get_pathway_participants` | Molecules in a pathway | `pathway_id` |

### `mcp__geneontology__go_data` (Gene Ontology)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_go_terms` | Search GO terms by keyword | `query`, `size`, `ontology` (molecular_function/biological_process/cellular_component), `include_obsolete` |
| `get_go_term` | Get full GO term details (definition, synonyms, xrefs) | `id` (GO:XXXXXXX) |
| `validate_go_id` | Check if GO ID is valid | `id` |
| `get_ontology_stats` | GO ontology statistics | -- |

### `mcp__nlm__nlm_ct_codes` (Gene ID Resolution & Cross-Referencing)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `ncbi-genes` | Resolve gene symbols to NCBI Gene IDs, retrieve gene info | `query`, `organism` |
| `search_icd10` | Search ICD-10 diagnosis codes | `query`, `limit` |
| `search_icd10pcs` | Search ICD-10-PCS procedure codes | `query`, `limit` |
| `search_cpt` | Search CPT procedure codes | `query`, `limit` |
| `search_hcpcs` | Search HCPCS codes | `query`, `limit` |
| `search_ndc` | Search NDC drug codes | `query`, `limit` |
| `search_rxnorm` | Search RxNorm drug identifiers | `query`, `limit` |
| `search_snomed` | Search SNOMED CT clinical terms | `query`, `limit` |
| `search_loinc` | Search LOINC lab/observation codes | `query`, `limit` |
| `search_mesh` | Search MeSH medical subject headings | `query`, `limit` |
| `search_umls` | Search UMLS unified medical language | `query`, `limit` |

---

## ORA vs GSEA Decision Framework

### When to Use Each Method

| Criterion | ORA (Over-Representation Analysis) | GSEA (Gene Set Enrichment Analysis) |
|-----------|-----------------------------------|--------------------------------------|
| **Input** | Unranked gene list (e.g., DEGs from a threshold cutoff) | Ranked gene list (e.g., all genes ranked by fold change or p-value) |
| **Statistical test** | Fisher's exact test / hypergeometric | Permutation testing (Kolmogorov-Smirnov) |
| **Significance cutoff** | p < 0.05 (after correction) | FDR q < 0.25 |
| **Strengths** | Simple, interpretable, works with any gene list | No arbitrary threshold, detects coordinated changes |
| **Weaknesses** | Requires arbitrary cutoff, loses magnitude information | Requires ranking metric, computationally heavier |
| **Best for** | Proteomics hits, CRISPR screen hits, mutation lists | RNA-seq, microarray, any expression experiment |

### Decision Logic

```
IF user provides a gene list without ranking/scores:
   → Use ORA (Fisher's exact test)
   → Ask if they have fold changes or p-values available

IF user provides ranked data (fold change, p-value, log2FC):
   → Use GSEA (permutation testing)
   → Rank by: -log10(p-value) × sign(log2FC)

IF user provides both:
   → Run both ORA (on significant genes) and GSEA (on full ranked list)
   → Compare results — concordant findings are higher confidence
```

---

## Gene Enrichment Workflow

### Step 1: Gene ID Disambiguation and Resolution

```
1. Auto-detect input gene ID type:
   - Gene symbols (e.g., TP53, BRCA1, EGFR)
   - Ensembl IDs (e.g., ENSG00000141510)
   - Entrez/NCBI Gene IDs (e.g., 7157)
   - UniProt accessions (e.g., P04637)

2. mcp__nlm__nlm_ct_codes(method: "ncbi-genes", query: "GENE_SYMBOL", organism: "human")
   → Resolve gene symbol to NCBI Gene ID, confirm official symbol, get aliases

3. mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL", size: 5)
   → Get Ensembl gene ID for cross-database linking

4. For ambiguous symbols, resolve all aliases:
   - Check NCBI Gene for official symbol vs synonyms
   - Confirm organism (human, mouse, rat, etc.)
   - Flag deprecated or withdrawn gene symbols
```

### Step 2: Multi-Source Enrichment Analysis

```
1. Gene Ontology (GO) — Three sub-ontologies:
   - Biological Process (BP): cellular/organismal processes (e.g., apoptosis, cell cycle)
   - Molecular Function (MF): biochemical activities (e.g., kinase activity, DNA binding)
   - Cellular Component (CC): subcellular localization (e.g., nucleus, membrane)
   - mcp__geneontology__go_data(method: "search_go_terms", query: "apoptotic process", ontology: "biological_process", size: 10)
     → Resolve enriched GO term names to GO IDs with full definitions
   - mcp__geneontology__go_data(method: "get_go_term", id: "GO:0006915")
     → Validate enriched GO term, retrieve definition, synonyms, and cross-references

2. KEGG Pathways:
   - Metabolic pathways, signaling cascades, disease pathways
   - mcp__kegg__kegg_data(method: "search_pathways", query: "apoptosis")
     → Search KEGG pathways by keyword to find relevant pathway IDs
   - mcp__kegg__kegg_data(method: "get_pathway_genes", pathway_id: "hsa04210")
     → Get all genes in the KEGG pathway for precise overlap calculation
   - mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
     → Cross-reference enriched KEGG pathways with drug-pathway data

3. Reactome:
   - Hierarchical pathway database with reaction-level detail
   - mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
     → Extract Reactome pathway annotations from target profiles
   - mcp__reactome__reactome_data(method: "find_pathways_by_gene", gene_id: "GENE_SYMBOL", species: "Homo sapiens")
     → Direct Reactome pathway lookup with full pathway details
   - mcp__reactome__reactome_data(method: "get_pathway_participants", pathway_id: "R-HSA-XXXXX")
     → All molecules in the pathway for precise gene overlap calculation

4. WikiPathways:
   - Community-curated pathway models
   - Cross-validate with KEGG/Reactome findings

5. STRING Functional Enrichment (protein-level, alternative to compute-based):
   - mcp__stringdb__stringdb_data(method: "get_functional_enrichment", protein_ids: ["GENE_A", "GENE_B", "GENE_C"], species: 9606)
     → GO/KEGG/Reactome/PFAM enrichment with p-values, directly from STRING
   - Useful as cross-validation source for ORA/GSEA results from other databases

6. MSigDB Hallmark Gene Sets:
   - 50 curated hallmark gene sets representing well-defined biological states
   - Key sets: inflammatory response, hypoxia, p53 pathway, EMT, angiogenesis
   - mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "MSigDB hallmark GENE_SET enrichment", num_results: 10)
     → Literature context for hallmark enrichment
```

### Step 3: Cross-Validation and Evidence Integration

```
1. Cross-validate across databases:
   - Same pathway enriched in GO BP AND KEGG → higher confidence
   - Same process enriched in Reactome AND WikiPathways → confirmed
   - STRING enrichment concordant with ORA/GSEA results → additional confirmation
   - REQUIREMENT: At least 2 independent sources must confirm a finding

2. mcp__stringdb__stringdb_data(method: "get_protein_annotations", protein_ids: ["GENE_A", "GENE_B"], species: 9606)
   → Functional annotations from STRING to cross-validate enrichment findings

3. mcp__pubchem__pubchem_info(method: "get_gene_interactions", cid: COMPOUND_CID)
   → Chemical-gene interactions for enriched pathway members

3. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "enriched_pathway gene_list_context", num_results: 15)
   → Literature evidence for enriched pathways in the biological context

4. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   → Disease relevance of enriched pathway members
```

### Step 4: Statistical Rigor and Multiple Testing Correction

```
1. Multiple Testing Correction:
   - Benjamini-Hochberg (BH) — DEFAULT: controls False Discovery Rate
   - Bonferroni — conservative, use when few tests or high stringency required
   - Apply correction WITHIN each database separately

2. Significance thresholds:
   - ORA: adjusted p-value < 0.05 (BH), < 0.01 for stringent
   - GSEA: FDR q-value < 0.25 (standard), < 0.05 (stringent)
   - Normalized Enrichment Score (NES) > |1.5| for biological relevance

3. Minimum gene set overlap:
   - Require ≥ 3 genes overlapping with pathway
   - Report gene ratio (overlap / pathway size)
   - Flag pathways with < 10 or > 500 genes (too specific or too broad)
```

---

## Evidence Grading Framework

### Enrichment Evidence Tiers

| Tier | Source Type | Confidence | Description |
|------|-----------|------------|-------------|
| **T1 (Highest)** | Curated pathway databases | High | Enrichment confirmed in Reactome AND KEGG with adj. p < 0.01. Manually curated, peer-reviewed pathway annotations. |
| **T2** | Validated gene sets | Medium-High | Enrichment in GO (experimental evidence codes: EXP, IDA, IPI, IMP, IGI, IEP) or MSigDB Hallmark. Validated through experiments. |
| **T3** | Text-mined / computationally inferred | Medium | Enrichment based on GO electronic annotations (IEA), text-mined associations, or single-database enrichment with adj. p < 0.05. |
| **T4 (Lowest)** | Single-source / marginal | Low | Enrichment in only one database, marginal significance (0.05 < adj. p < 0.1), or based on predicted annotations only. |

### Evidence Grading Logic

```
T1 criteria (report as HIGH confidence):
  - Enriched in ≥ 2 curated databases (KEGG, Reactome, WikiPathways)
  - Adjusted p-value < 0.01 in primary analysis
  - ≥ 5 gene overlap with pathway
  - Supported by PubMed literature

T2 criteria (report as MEDIUM-HIGH confidence):
  - Enriched in ≥ 1 curated database + GO with experimental evidence
  - Adjusted p-value < 0.05
  - ≥ 3 gene overlap with pathway
  - MSigDB Hallmark concordance

T3 criteria (report as MEDIUM confidence):
  - Enriched in GO (any evidence code) or single curated database
  - Adjusted p-value < 0.05
  - Cross-supported by PubChem gene interactions or ChEMBL target data

T4 criteria (report as LOW confidence):
  - Single-source enrichment only
  - Marginal significance (0.05 < adj. p < 0.1)
  - No cross-validation from independent source
  - Flag for further investigation
```

---

## Organism Support

### Supported Organisms and ID Mapping

| Organism | Common name | NCBI Taxonomy | Gene ID format | Notes |
|----------|-------------|---------------|----------------|-------|
| *Homo sapiens* | Human | 9606 | HGNC symbols, Ensembl, Entrez | Default organism. Most complete annotations. |
| *Mus musculus* | Mouse | 10090 | MGI symbols, Ensembl, Entrez | Use ortholog mapping for human pathway enrichment. |
| *Rattus norvegicus* | Rat | 10116 | RGD symbols, Ensembl, Entrez | Pharmacology/toxicology studies. |
| *Drosophila melanogaster* | Fly | 7227 | FlyBase IDs, Ensembl | Model organism genetics. |
| *Caenorhabditis elegans* | Worm | 6239 | WormBase IDs | Aging, neurobiology studies. |
| *Saccharomyces cerevisiae* | Yeast | 4932 | SGD symbols | Metabolic pathway studies. |
| *Danio rerio* | Zebrafish | 7955 | ZFIN IDs, Ensembl | Developmental biology, toxicology. |

### Cross-Organism Workflow

```
1. mcp__nlm__nlm_ct_codes(method: "ncbi-genes", query: "gene_symbol", organism: "mouse")
   → Resolve non-human gene to NCBI Gene ID

2. Map to human orthologs for pathway enrichment:
   - Use NCBI HomoloGene or Ensembl Compara ortholog tables
   - mcp__opentargets__opentargets_info(method: "search_targets", query: "human_ortholog_symbol")
     → Confirm human ortholog exists and has pathway annotations

3. Run enrichment on human orthologs:
   - Most pathway databases have deepest annotation for human
   - Report which genes lacked orthologs (potential species-specific biology)

4. Validate species-specific findings:
   mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "gene_symbol organism pathway", num_results: 10)
```

---

## Publication-Ready Output Format

### Enrichment Results Table

```
| Rank | Term | Database | Gene Count | Gene Ratio | p-value | Adj. p-value | FDR q-value | Evidence Tier | Genes |
|------|------|----------|------------|------------|---------|-------------|-------------|---------------|-------|
| 1 | Apoptotic process | GO:BP | 12/45 | 0.267 | 2.3e-8 | 1.1e-6 | 8.5e-7 | T1 | TP53, BAX, BCL2, ... |
| 2 | p53 signaling pathway | KEGG | 8/45 | 0.178 | 5.1e-6 | 1.2e-4 | 9.8e-5 | T1 | TP53, MDM2, CDKN1A, ... |
| 3 | Programmed cell death | Reactome | 10/45 | 0.222 | 1.7e-5 | 2.8e-4 | 2.1e-4 | T2 | CASP3, CASP9, CYCS, ... |
```

### GSEA Results Table

```
| Rank | Gene Set | Database | Size | NES | p-value | FDR q-value | Evidence Tier | Leading Edge Genes |
|------|----------|----------|------|-----|---------|-------------|---------------|--------------------|
| 1 | HALLMARK_P53_PATHWAY | MSigDB | 200 | 2.31 | <0.001 | 0.002 | T1 | TP53, MDM2, CDKN1A, BAX, ... |
| 2 | HALLMARK_APOPTOSIS | MSigDB | 161 | 1.98 | <0.001 | 0.005 | T1 | CASP3, BCL2, BID, ... |
```

### Summary Statistics to Include

```
- Total genes submitted: N
- Genes mapped successfully: N (%)
- Genes with pathway annotations: N (%)
- Background gene set: genome-wide / custom (specify)
- Databases queried: GO (BP/MF/CC), KEGG, Reactome, WikiPathways, MSigDB
- Multiple testing correction: Benjamini-Hochberg
- Significant terms (adj. p < 0.05): N per database
- Cross-validated findings (≥ 2 databases): N
```

---

## Multi-Agent Workflow Examples

**"Perform pathway enrichment on my differentially expressed genes from RNA-seq"**
1. Gene Enrichment → ID resolution, ORA/GSEA across GO/KEGG/Reactome/MSigDB, cross-validation, evidence grading
2. Systems Biology → Network visualization of enriched pathways, hub gene identification
3. Disease Research → Disease associations for top enriched pathways

**"What biological processes are disrupted by these CRISPR screen hits?"**
1. Gene Enrichment → ORA on hit gene list across GO BP/MF/CC, KEGG, Reactome with cross-validation
2. Drug Target Analyst → Druggability assessment for genes in top enriched pathways
3. Network Pharmacologist → Protein interaction networks connecting enriched pathway members

**"Compare pathway enrichment between treatment and control groups"**
1. Gene Enrichment → GSEA on ranked gene list, comparative enrichment across databases, evidence grading
2. Target Research → Target validation evidence for leading edge genes
3. Drug Target Analyst → Existing compounds targeting enriched pathways

**"Identify druggable pathways from patient genomics data"**
1. Gene Enrichment → Multi-source enrichment of mutated/altered genes, T1/T2 evidence filtering
2. Drug Target Analyst → Druggability of pathway members, existing compounds with bioactivity data
3. Network Pharmacologist → Multi-target drug opportunities across enriched pathways
4. Disease Research → Indication-specific pathway relevance and clinical context

---

## GEO Public Data Integration

### `mcp__geo__geo_data` (Expression Dataset Discovery for Enrichment Context)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_datasets` | Find expression datasets to provide biological context for enrichment results | `query`, `organism`, `study_type` |
| `search_by_gene` | Find gene expression profiles across public studies | `gene`, `organism` |

**Workflow — GEO for enrichment context:**
Search GEO for expression datasets to provide biological context for enrichment analysis results. Use `search_datasets` to find relevant expression studies for the condition or tissue of interest, and `search_by_gene` to examine how enriched genes behave across independent public datasets.

```
mcp__geo__geo_data(method: "search_datasets", query: "RNA-seq breast cancer differential expression")
→ Find expression datasets to contextualize enrichment findings

mcp__geo__geo_data(method: "search_by_gene", gene: "TP53", organism: "Homo sapiens")
→ Examine TP53 expression across public studies to validate enrichment-driven hypotheses
```

## Completeness Checklist

- [ ] Gene IDs resolved and disambiguated (symbols mapped to Ensembl/Entrez IDs)
- [ ] Enrichment method selected and justified (ORA vs GSEA vs both)
- [ ] Multiple databases queried (GO BP/MF/CC, KEGG, Reactome, MSigDB minimum)
- [ ] Multiple testing correction applied (Benjamini-Hochberg default)
- [ ] Cross-validation performed (findings confirmed in at least 2 independent databases)
- [ ] Evidence tier assigned to each enriched term (T1-T4)
- [ ] Summary statistics reported (genes mapped, background set, significant terms per database)
- [ ] Publication-ready enrichment results table generated
- [ ] Leading edge genes identified for top enriched terms
- [ ] Literature evidence cited for top enriched pathways via PubMed
