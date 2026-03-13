---
name: drug-target-analyst
description: Drug target and molecular pharmacology analyst. Target identification, target-disease associations, mechanism of action, bioactivity data, compound-target relationships, pathway analysis, structure-activity relationships. Use when user mentions drug target, target identification, mechanism of action, MOA, bioactivity, IC50, EC50, Ki, binding affinity, target validation, druggability, protein target, gene target, pathway analysis, SAR, or structure-activity.
---

# Drug Target Analyst

Drug target identification, validation, and molecular pharmacology analysis. Uses Open Targets for target-disease evidence, ChEMBL for bioactivity data, DrugBank for drug-target relationships, and PubMed for literature evidence.

> **Druggability recipes**: See [druggability-recipes.md](druggability-recipes.md) for multi-dimensional druggability assessment code templates (protein class scoring, ChEMBL ligand counts, pocket detection, GTEx tau index, co-essentiality, composite scoring, anti-target checks, tractability, competitive landscape).

## Report-First Workflow

1. **Create report file immediately**: `[target]_drug-target-analyst_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## Cross-Reference: Other Skills

- **Enzyme target kinetics (Km, kcat, inhibitors, cofactors)** -> use enzyme-kinetics skill

## When NOT to Use This Skill

- Drug safety signals from target activity → use `pharmacovigilance-specialist`
- Clinical trials targeting this pathway → use `clinical-trial-analyst`
- FDA-approved drugs for this target → use `fda-consultant`
- Risk assessment for target-related effects → use `risk-management-specialist`
- Systematic target validation with GO/NO-GO scoring → use `drug-target-validator`
- Drug repurposing for validated targets → use `drug-repurposing-analyst`

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

### `mcp__pubmed__pubmed_articles` (Target Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__uniprot__uniprot_data` (Protein Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_protein_info` | Full protein profile | `accession`, `format` |
| `search_by_gene` | Find proteins by gene name | `gene`, `organism`, `size` |
| `get_protein_structure` | Structural data (PDB, AlphaFold) | `accession` |
| `get_protein_domains_detailed` | Detailed domain architecture | `accession` |
| `get_protein_variants` | Known protein variants | `accession` |
| `get_protein_features` | Protein features (domains, sites, PTMs) | `accession` |
| `search_by_localization` | Search by subcellular location | `localization`, `organism`, `size` |
| `get_external_references` | Cross-database references | `accession` |

### `mcp__reactome__reactome_data` (Pathway Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `find_pathways_by_gene` | Pathways containing a gene | `gene_id`, `species` |
| `get_pathway_details` | Full pathway info | `pathway_id` |
| `get_pathway_hierarchy` | Parent/child pathway tree | `pathway_id` |

### `mcp__gtex__gtex_data` (Tissue Expression & eQTLs)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_genes` | Search genes in GTEx | `query`, `page`, `pageSize` |
| `get_gene_expression` | Expression across tissues | `gencodeId`, `tissueSiteDetailId` |
| `get_median_gene_expression` | Median expression per tissue | `gencodeId`, `tissueSiteDetailId` |
| `get_top_expressed_genes` | Top expressed genes in a tissue | `tissueSiteDetailId`, `limit` |
| `get_tissue_info` | Available tissue metadata | — |

### `mcp__ensembl__ensembl_data` (Genomic Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `lookup_gene` | Get gene info by ID or symbol | `gene_id`, `species`, `expand` |
| `get_transcripts` | Get transcripts for a gene | `gene_id`, `canonical_only` |
| `get_xrefs` | Get cross-database references | `gene_id`, `external_db`, `all_levels` |
| `get_sequence` | Get genomic/transcript sequence | `region`, `species`, `format`, `mask` |

### `mcp__alphafold__alphafold_data` (AlphaFold Predicted Structures)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_structure` | Get AlphaFold predicted structure for druggability context | `uniprotId`, `format` (json/pdb/cif) |
| `check_availability` | Check if prediction exists | `uniprotId` |
| `get_confidence_scores` | Get pLDDT confidence scores for binding site assessment | `uniprotId` |
| `analyze_confidence_regions` | Identify high/low confidence regions | `uniprotId` |
| `validate_structure_quality` | Quality assessment of predicted structure | `uniprotId` |

### `mcp__pdb__pdb_data` (Experimental Structures from PDB)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_structures` | Search experimental structures for target | `query`, `limit`, `experimental_method`, `resolution_range`, `sort_by` |
| `get_structure_info` | Get structure details (method, resolution, ligands) | `pdb_id`, `format` |
| `search_by_uniprot` | Find PDB structures for UniProt ID | `uniprot_id`, `limit` |
| `get_structure_quality` | Resolution, R-factor, validation metrics | `pdb_id` |

### gnomAD (Genetic Constraint)

| Tool | Method | Use |
|------|--------|-----|
| `mcp__gnomad__gnomad_data` | `get_gene_constraint` | LoF intolerance (LOEUF/pLI) — essential gene = good target but safety concern |
| | `batch_gene_constraint` | Compare constraint across target family members |

### cBioPortal (Cancer Genomics)

| Tool | Method | Use |
|------|--------|-----|
| `mcp__cbioportal__cbioportal_data` | `get_mutation_frequency` | Target mutation frequency in cancer (oncogene evidence) |
| | `search_studies` | Find cancer datasets relevant to target |

### BindingDB (Binding Affinity Data)

| Tool | Method | Use |
|------|--------|-----|
| `mcp__bindingdb__bindingdb_data` | `get_ligands_by_target` | Known binders with IC50/Ki — druggability evidence |
| | `search_by_target_name` | Find binding data by target name |
| | `get_ki_by_target` | Ki values for target — binding affinity landscape |

### `mcp__depmap__depmap_data` (DepMap — Cancer Dependency Map)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_gene_dependency` | Functional essentiality — is the target required for cancer cell survival? | `gene`, `lineage`, `dataset` |
| `get_gene_dependency_summary` | Pan-cancer dependency profile — common essential vs context-specific | `gene` |
| `get_biomarker_analysis` | Predictive biomarkers for target dependency | `gene`, `feature_type`, `limit` |
| `get_gene_expression` | Expression-dependency correlation | `gene`, `lineage`, `dataset` |
| `get_multi_gene_profile` | Pathway-level dependency assessment | `genes`, `lineage`, `dataset` |

---

## Target Identification Workflow

### Step 1: Find and Characterize the Target

```
1. mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL")
   → Get Ensembl gene ID and basic target info

2. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Full target profile: function, subcellular location, protein structure, tractability

3. mcp__chembl__chembl_info(method: "target_search", query: "target_name")
   → Get ChEMBL target ID and target classification

4. mcp__drugbank__drugbank_info(method: "search_by_target", target: "target_name")
   → Existing drugs that modulate this target

5. mcp__ensembl__ensembl_data(method: "lookup_gene", gene_id: "GENE_SYMBOL", species: "homo_sapiens", expand: true)
   → Gene coordinates, biotype, description, transcript count

6. mcp__ensembl__ensembl_data(method: "get_transcripts", gene_id: "ENSG00000xxxxx", canonical_only: true)
   → Canonical transcript ID, protein length, exon structure

7. mcp__ensembl__ensembl_data(method: "get_xrefs", gene_id: "ENSG00000xxxxx", external_db: "UniProt/SWISSPROT")
   → Cross-references to UniProt for structural/functional annotation

8. mcp__gtex__gtex_data(method: "search_genes", query: "GENE_SYMBOL")
   → Get GENCODE ID for GTEx expression queries

9. mcp__gtex__gtex_data(method: "get_median_gene_expression", gencodeId: "ENSG00000xxxxx.xx")
   → Tissue expression profile — identify tissues where target is selectively expressed vs ubiquitous (key for target selectivity)

10. mcp__uniprot__uniprot_data(method: "search_by_gene", gene: "GENE_SYMBOL", organism: "human", size: 5)
    → Get UniProt accession, protein name, and functional annotations

11. mcp__uniprot__uniprot_data(method: "get_protein_info", accession: "UNIPROT_ACC")
    → Full protein profile: function, subcellular location, domain architecture, structure refs

12. mcp__uniprot__uniprot_data(method: "get_protein_domains_detailed", accession: "UNIPROT_ACC")
    → Detailed domain architecture for binding site identification
```

### Step 2: Assess Target-Disease Evidence

```
1. mcp__opentargets__opentargets_info(method: "search_diseases", query: "disease_name")
   → Get EFO disease ID

2. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   → Association score with evidence breakdown (genetic, somatic, literature, known drugs, animal models)

3. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.5, size: 20)
   → Top validated targets for this disease (competitive landscape)

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL disease_name target validation", num_results: 15)
   → Published target validation studies
```

### Step 3: Analyze Bioactivity Data

```
1. mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "CHEMBLxxxxx", target_id: "CHEMBLxxxxx", limit: 50)
   → IC50, Ki, EC50 values for known compounds against this target

2. mcp__chembl__chembl_info(method: "compound_search", query: "compound_name")
   → Find specific compound ChEMBL ID

3. mcp__chembl__chembl_info(method: "get_mechanism", chembl_id: "CHEMBLxxxxx")
   → Mechanism of action (agonist, antagonist, inhibitor, etc.)

4. mcp__chembl__chembl_info(method: "get_admet", chembl_id: "CHEMBLxxxxx")
   → Drug-likeness properties (Lipinski, molecular weight, logP, PSA)
```

### Step 4: Map the Pathway

```
1. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   → Pharmacodynamics, mechanism, pathway involvement

2. mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   → Metabolic/signaling pathway mapping

3. mcp__drugbank__drugbank_info(method: "search_by_target", target: "upstream_or_downstream_target")
   → Other drugs hitting related targets in the same pathway

3b. mcp__reactome__reactome_data(method: "find_pathways_by_gene", gene_id: "GENE_SYMBOL", species: "Homo sapiens")
    → Direct Reactome pathway lookup for the target

3c. mcp__reactome__reactome_data(method: "get_pathway_hierarchy", pathway_id: "R-HSA-XXXXX")
    → Place target pathway in hierarchical context (top-level → specific → sub-pathway)

4. mcp__uniprot__uniprot_data(method: "get_protein_variants", accession: "UNIPROT_ACC")
   → Known variants that may affect drug binding or protein function

5. mcp__pdb__pdb_data(method: "search_by_uniprot", uniprot_id: "UNIPROT_ACC", limit: 10)
   → Find experimental structures for binding site characterization

6. mcp__alphafold__alphafold_data(method: "get_confidence_scores", uniprotId: "UNIPROT_ACC")
   → Assess AlphaFold prediction confidence for regions without experimental structures

7. mcp__uniprot__uniprot_data(method: "search_by_localization", localization: "membrane", organism: "human", size: 20)
   → Find drug-accessible membrane targets in the same pathway
```

### DepMap Target Assessment

```
1. Query target dependency across all cancer lineages:
   mcp__depmap__depmap_data(method: "get_gene_dependency_summary", gene: "GENE_SYMBOL")
   → Pan-cancer dependency scores; negative scores indicate essentiality

2. Classify the target:
   - Common essential: dependency score < -0.5 across most lineages (unfavorable — toxicity risk)
   - Selective dependency: strong dependency in specific lineages only (favorable — therapeutic window)
   - Non-essential: dependency score near 0 across all lineages (target modulation unlikely to kill cancer cells)

3. Identify lineages with strongest dependency (therapeutic window):
   mcp__depmap__depmap_data(method: "get_gene_dependency", gene: "GENE_SYMBOL", lineage: "lung")
   mcp__depmap__depmap_data(method: "get_gene_dependency", gene: "GENE_SYMBOL", lineage: "breast")
   mcp__depmap__depmap_data(method: "get_gene_dependency", gene: "GENE_SYMBOL", lineage: "pancreas")
   → Compare dependency scores across lineages to find where target is most essential

4. Find predictive biomarkers for target dependency:
   mcp__depmap__depmap_data(method: "get_biomarker_analysis", gene: "GENE_SYMBOL", feature_type: "mutation")
   mcp__depmap__depmap_data(method: "get_biomarker_analysis", gene: "GENE_SYMBOL", feature_type: "expression")
   → Identify mutations or expression patterns that predict which tumors depend on the target

5. Assess pathway redundancy via multi-gene profiles:
   mcp__depmap__depmap_data(method: "get_multi_gene_profile", genes: ["GENE_A", "GENE_B", "GENE_C"], lineage: "lung")
   → Compare dependency of pathway members; if paralogs are also essential, synthetic lethality may apply;
     if paralogs are non-essential, compensatory mechanisms are unlikely

6. Correlate expression with dependency:
   mcp__depmap__depmap_data(method: "get_gene_expression", gene: "GENE_SYMBOL", lineage: "lung")
   → Determine whether target expression level predicts dependency (expression-addiction)
```

---

### Multi-Database Target Druggability Assessment

Combine gnomAD, cBioPortal, and BindingDB to build a comprehensive druggability profile for any target.

```
1. Assess genetic constraint (gnomAD):
   mcp__gnomad__gnomad_data(method: "get_gene_constraint", gene: "GENE_SYMBOL")
   -> LOEUF < 0.35 = highly constrained (essential gene — good target but safety concern)
   -> pLI > 0.9 = loss-of-function intolerant

2. Compare constraint across target family:
   mcp__gnomad__gnomad_data(method: "batch_gene_constraint", genes: ["GENE_A", "GENE_B", "GENE_C"])
   -> Identify which family members are most/least constrained (selectivity window)

3. Check somatic mutation landscape (cBioPortal):
   mcp__cbioportal__cbioportal_data(method: "get_mutation_frequency", gene: "GENE_SYMBOL")
   -> High mutation frequency = oncogene evidence (gain-of-function target)
   -> Low mutation frequency in cancer = less likely oncology driver

4. Find relevant cancer datasets:
   mcp__cbioportal__cbioportal_data(method: "search_studies", keyword: "disease_name")
   -> Identify cancer types where target is most frequently mutated

5. Retrieve known binders and druggability evidence (BindingDB):
   mcp__bindingdb__bindingdb_data(method: "get_ligands_by_target", target: "TARGET_NAME")
   -> Known compounds with IC50/Ki values — confirms chemical tractability

6. Search binding data by target name:
   mcp__bindingdb__bindingdb_data(method: "search_by_target_name", name: "TARGET_NAME")
   -> Broader search for all binding data associated with the target

7. Assess binding affinity landscape:
   mcp__bindingdb__bindingdb_data(method: "get_ki_by_target", target: "TARGET_NAME")
   -> Ki value distribution — establishes achievable potency range

8. Integrate findings:
   - Constrained gene + frequent cancer mutations + known binders = HIGH druggability, validated oncology target
   - Constrained gene + no binders = genetically validated but chemically intractable — needs screening
   - Unconstrained gene + many binders = chemically tractable but weaker genetic validation
   - Cross-reference with ChEMBL bioactivity and Open Targets tractability for complete picture
```

---

## Target Validation Framework

### Evidence Hierarchy for Target Validation

| Level | Evidence Type | Strength |
|-------|-------------|----------|
| **1 (Strongest)** | Human genetics — GWAS, Mendelian disease, somatic mutations | Causal link established |
| **2** | Clinical evidence — approved drugs, clinical trials with target biomarker | Target modulation → clinical benefit shown |
| **3** | Functional genomics — CRISPR/siRNA knockdown, overexpression | Target modulation → phenotype in human cells |
| **4** | Animal models — knockout, transgenic, pharmacological | Target modulation → phenotype in vivo |
| **5** | In vitro biochemistry — binding assays, enzyme activity | Target engagement confirmed |
| **6 (Weakest)** | Literature/text mining — co-mention, pathway inference | Hypothesis level only |

### Druggability Assessment

**Tractability categories (from Open Targets):**

| Category | Meaning | Drug Modality |
|----------|---------|---------------|
| **Small molecule — clinical** | Small molecule drugs in clinical trials or approved | Oral/injectable small molecule |
| **Small molecule — discovery** | Ligandable (has binding site), compounds in discovery | Small molecule |
| **Antibody — clinical** | Antibody drugs in clinical trials or approved | Biologic |
| **Antibody — predicted** | Extracellular protein, antibody-accessible | Biologic |
| **Other modalities** | PROTAC, antisense, gene therapy candidates | Advanced therapeutics |

### Key Druggability Criteria

```
Favorable target characteristics:
✓ Extracellular or membrane-bound (biologic-accessible)
✓ Well-defined binding pocket (small molecule-accessible)
✓ Enzyme with catalytic site (inhibitor design)
✓ GPCR or ion channel (established drug target classes)
✓ Human genetic validation (GWAS, Mendelian)
✓ Existing chemical matter (known ligands with nanomolar affinity)
✓ Selectivity achievable (distinct from close family members)

Unfavorable characteristics:
✗ Protein-protein interaction with flat surface
✗ Intracellular with no known binding pocket
✗ Scaffolding/structural protein (no enzymatic function)
✗ Essential housekeeping gene (toxicity risk)
✗ Redundant pathway (compensatory mechanisms)
```

---

## Structure-Activity Relationship (SAR) Analysis

### SAR Workflow

```
1. mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "CHEMBL_TARGET_ID", limit: 100)
   → Retrieve all bioactivity data for the target

2. Analyze by activity type:
   - Group compounds by IC50/Ki/EC50 ranges
   - Identify most potent compounds (nanomolar range)
   - Compare structural features of active vs inactive

3. mcp__chembl__chembl_info(method: "get_admet", chembl_id: "CHEMBL_COMPOUND")
   → Check drug-likeness of hit compounds

4. mcp__drugbank__drugbank_info(method: "search_by_structure", smiles: "SMILES_STRING")
   → Find structurally similar approved drugs
```

### Activity Interpretation

| Metric | What it measures | Good range |
|--------|-----------------|------------|
| **IC50** | Concentration for 50% inhibition | < 100 nM (potent), < 1 μM (active) |
| **Ki** | Binding constant (thermodynamic) | < 10 nM (high affinity) |
| **EC50** | Concentration for 50% effect (agonist) | < 100 nM |
| **Kd** | Dissociation constant | < 10 nM |
| **% Inhibition** | Activity at fixed concentration | > 50% at 10 μM (screening hit) |

### Selectivity Assessment

```
1. Identify close family members:
   mcp__opentargets__opentargets_info(method: "search_targets", query: "protein_family_name", size: 20)

2. Check cross-reactivity:
   mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "COMPOUND_ID", target_id: "OFF_TARGET_ID")

3. Calculate selectivity ratio:
   Selectivity = IC50(off-target) / IC50(on-target)
   > 100x = good selectivity
   > 1000x = excellent selectivity
```

---

## Competitive Target Landscape

### Workflow

```
1. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.3, size: 50)
   → All validated targets for this disease, ranked by evidence

2. For top targets, check existing drugs:
   mcp__drugbank__drugbank_info(method: "search_by_target", target: "target_name")
   → What's already approved or in development?

3. mcp__chembl__chembl_info(method: "drug_search", query: "disease_name", limit: 30)
   → All drugs for this indication in ChEMBL

4. Cross-reference with trials:
   (use clinical-trial-analyst skill for pipeline intelligence)
```

---

## Multi-Agent Workflow Examples

**"Identify new drug targets for Alzheimer's disease"**
1. Drug Target Analyst → Open Targets disease-target associations, druggability assessment, existing compounds
2. Clinical Trial Analyst → Active trials for each target, pipeline gaps
3. Pharmacovigilance Specialist → Safety signals from drugs hitting these targets (class effects)

**"Evaluate our compound's target selectivity"**
1. Drug Target Analyst → ChEMBL bioactivity for on-target and off-targets, SAR analysis, ADMET
2. Risk Management Specialist → Predicted risks from off-target activity
3. FDA Consultant → Regulatory precedent for this target class

**"Compare mechanisms of action for GLP-1 agonists"**
1. Drug Target Analyst → Target details, pathway mapping, bioactivity comparison across compounds
2. Pharmacovigilance Specialist → Safety profile differences (target-mediated vs off-target effects)
3. Clinical Trial Analyst → Head-to-head trial data

---

## Completeness Checklist

- [ ] Target resolved to Ensembl ID, ChEMBL target ID, and UniProt accession
- [ ] Target-disease association scored via Open Targets with evidence breakdown
- [ ] Bioactivity data retrieved (IC50, Ki, EC50) for known compounds
- [ ] Druggability assessed (tractability, binding pocket, protein family)
- [ ] Selectivity profile evaluated against close family members
- [ ] Pathway mapping completed via DrugBank and Reactome
- [ ] Tissue expression profile reviewed (GTEx)
- [ ] Competitive target landscape documented
- [ ] SAR analysis performed for existing chemical matter
- [ ] DepMap essentiality data queried for oncology targets
