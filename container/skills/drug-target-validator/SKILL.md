---
name: drug-target-validator
description: Comprehensive computational validation of drug targets for early-stage drug discovery. Systematic 10-phase pipeline evaluating disease association, druggability, safety, clinical precedent, and validation evidence to produce a quantitative Target Validation Score (0-100) with GO/NO-GO recommendations. Use when user mentions target validation, target feasibility, druggability assessment, target validation score, GO/NO-GO, target prioritization, validation pipeline, target tractability, target safety profile, or drug development feasibility.
---

# Drug Target Validator

Comprehensive computational validation of drug targets for early-stage drug discovery. Evaluates targets across 10 dimensions using multi-database triangulation to produce a quantitative Target Validation Score (0-100) and tiered GO/NO-GO recommendations. This skill is DIFFERENT from the drug-target-analyst: the analyst identifies and characterizes targets, while this validator systematically validates them for drug development feasibility.

## Report-First Workflow

1. **Create report file immediately**: `[target]_drug-target-validator_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Target identification and characterization (not validation) → use `drug-target-analyst`
- Drug repurposing opportunities for validated targets → use `drug-repurposing-analyst`
- Network and pathway pharmacology context → use `network-pharmacologist`
- Clinical trial landscape for the target → use `clinical-trial-analyst`
- FDA regulatory pathway and precedent → use `fda-consultant`
- Chemical safety and toxicology assessment → use `chemical-safety-toxicology`

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

### `mcp__pubmed__pubmed_articles` (Validation Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__fda__fda_info` (Regulatory & Safety Intelligence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `lookup_drug` | Search drugs by name, adverse events, labels, recalls, shortages | `search_term`, `search_type`, `limit`, `count` |
| `lookup_device` | Search medical devices | `search_term`, `search_type`, `limit` |
| `search_orange_book` | Find brand/generic drug products by name | `drug_name`, `include_generics` |
| `get_therapeutic_equivalents` | Find AB-rated generic equivalents | `drug_name` |
| `get_patent_exclusivity` | Look up patents and exclusivity by NDA number | `nda_number` |
| `analyze_patent_cliff` | Forecast when a drug loses patent protection | `drug_name`, `years_ahead` |
| `search_purple_book` | Find biological products and biosimilars | `drug_name` |
| `get_biosimilar_interchangeability` | Check which biosimilars are interchangeable | `reference_product` |

### `mcp__ctgov__ctgov_info` (Clinical Trial Intelligence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search clinical trials | `condition`, `intervention`, `phase`, `status`, `location`, `lead`, `ages`, `studyType`, `pageSize` |
| `get` | Get full trial details by NCT ID | `nctId` |
| `suggest` | Autocomplete terms | `input`, `dictionary` |
| `stats` | Trial statistics and counts | `condition`, `intervention` |

### `mcp__uniprot__uniprot_data` (Protein Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_protein_info` | Full protein profile | `accession`, `format` |
| `search_by_gene` | Find proteins by gene name | `gene`, `organism`, `size` |
| `get_protein_features` | Protein features (domains, sites, PTMs) | `accession` |
| `get_protein_orthologs` | Orthologs across species | `accession` |
| `get_protein_structure` | Structural data (PDB, AlphaFold) | `accession` |
| `get_protein_domains_detailed` | Detailed domain architecture | `accession` |
| `get_protein_variants` | Known protein variants | `accession` |

### `mcp__ensembl__ensembl_data` (Genomic Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `lookup_gene` | Get gene info by ID or symbol | `gene_id`, `species`, `expand` |
| `get_transcripts` | Get transcripts for a gene | `gene_id`, `canonical_only` |
| `get_homologs` | Get gene homologs across species | `gene_id`, `target_species`, `type` |
| `get_regulatory_features` | Get regulatory elements in region | `region`, `species`, `feature_type`, `cell_type` |
| `get_xrefs` | Get cross-database references | `gene_id`, `external_db`, `all_levels` |

### `mcp__stringdb__stringdb_data` (Target Interaction Network & Functional Context)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_protein_interactions` | Get interaction partners for a protein | `protein_id`, `species`, `limit`, `required_score` |
| `get_interaction_network` | Build interaction network from protein list | `protein_ids`, `species`, `required_score`, `network_type`, `add_nodes` |
| `get_functional_enrichment` | GO/KEGG/Reactome enrichment for protein set | `protein_ids`, `species`, `background_string_identifiers` |
| `get_protein_annotations` | Get functional annotations | `protein_ids`, `species` |

### `mcp__reactome__reactome_data` (Pathway Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `find_pathways_by_gene` | Pathways containing a gene | `gene_id`, `species` |
| `get_pathway_details` | Full pathway info | `pathway_id` |
| `get_pathway_hierarchy` | Parent/child pathway tree | `pathway_id` |
| `get_pathway_participants` | Molecules in a pathway | `pathway_id` |

### `mcp__pubchem__pubchem_info` (Chemical & Structural Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_compounds` | Compound lookup by name/CID/SMILES | `query`, `search_type` |
| `get_compound_properties` | Molecular properties (MW, logP, PSA, rotatable bonds) | `cid` |
| `get_compound_info` | Full compound record | `cid` |
| `get_safety_data` | GHS hazard classifications, signal words, pictograms | `cid` |
| `search_similar_compounds` | Structural analogs for scaffold analysis | `smiles`, `threshold` |
| `analyze_stereochemistry` | Stereo-specific assessment | `cid` |
| `get_patent_ids` | Patent landscape | `cid` |
| `get_bioassay_results` | Bioassay activity data | `cid`, `limit` |
| `get_3d_conformer` | 3D structure for binding analysis | `cid` |
| `get_pharmacology` | Pharmacological action data | `cid` |
| `get_synonyms` | All synonyms and identifiers | `cid` |
| `classify_compound` | Chemical classification hierarchy | `cid` |

### `mcp__alphafold__alphafold_data` (AlphaFold Predicted Structures)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `check_availability` | Check if AlphaFold prediction exists | `uniprotId` |
| `get_structure` | Get predicted structure for druggability assessment | `uniprotId`, `format` (json/pdb/cif) |
| `get_confidence_scores` | Get pLDDT scores for binding site confidence | `uniprotId` |
| `analyze_confidence_regions` | Identify high/low confidence regions | `uniprotId` |
| `validate_structure_quality` | Quality assessment of prediction | `uniprotId` |

### `mcp__pdb__pdb_data` (Experimental Structures from PDB)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_structures` | Search experimental structures | `query`, `limit`, `experimental_method`, `resolution_range`, `sort_by` |
| `get_structure_info` | Get structure details (method, resolution, ligands) | `pdb_id`, `format` |
| `search_by_uniprot` | Find PDB structures for UniProt ID | `uniprot_id`, `limit` |
| `get_structure_quality` | Resolution, R-factor, validation metrics | `pdb_id` |

### DepMap — Cancer Dependency Map

| Tool | Method | Use |
|------|--------|-----|
| `mcp__depmap__depmap_data` | `get_gene_dependency` | CRISPR Chronos dependency scores for a target gene across cancer cell lines — THE gold standard for essentiality validation |
| | `get_gene_dependency_summary` | Pan-cancer dependency stats — identify common essential vs selective dependencies |
| | `get_biomarker_analysis` | Test if a biomarker mutation predicts dependency on the target (synthetic lethality) |
| | `get_mutations` | Mutation status across cell lines for the target gene |
| | `get_gene_expression` | Expression correlation with dependency |
| | `get_multi_gene_profile` | Co-dependency analysis for pathway members |
| | `get_context_info` | Available cancer lineages and subtypes |

### `mcp__gtex__gtex_data` (Tissue Expression & eQTLs)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_genes` | Search genes in GTEx | `query`, `page`, `pageSize` |
| `get_gene_expression` | Expression across tissues | `gencodeId`, `tissueSiteDetailId` |
| `get_median_gene_expression` | Median expression per tissue | `gencodeId`, `tissueSiteDetailId` |
| `get_tissue_info` | Available tissue metadata | — |

### gnomAD (Genetic Constraint)

| Tool | Method | Use |
|------|--------|-----|
| `mcp__gnomad__gnomad_data` | `get_gene_constraint` | Genetic evidence — LoF intolerant genes validate as essential targets |
| | `filter_rare_variants` | Rare LoF variants as natural human knockouts |

### cBioPortal (Cancer Genomics)

| Tool | Method | Use |
|------|--------|-----|
| `mcp__cbioportal__cbioportal_data` | `get_mutation_frequency` | Somatic mutation frequency — oncogene/TSG evidence |
| | `get_mutations` | Hotspot mutations = gain-of-function evidence |

### BindingDB (Binding Affinity Data)

| Tool | Method | Use |
|------|--------|-----|
| `mcp__bindingdb__bindingdb_data` | `get_ligands_by_target` | Chemical tractability — existing binders = druggable |
| | `get_ki_by_target` | Binding affinity range = achievable potency |

---

## 10-Phase Target Validation Pipeline

### Phase 1: Target Disambiguation

Resolve gene symbol to canonical identifiers. Detect ambiguous symbols early.

```
1. mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL", size: 10)
   -> Get Ensembl ID, verify correct gene, note aliases

2. mcp__chembl__chembl_info(method: "target_search", query: "GENE_SYMBOL", limit: 10)
   -> Get ChEMBL target ID, verify protein classification

3. mcp__drugbank__drugbank_info(method: "search_by_target", target: "GENE_SYMBOL", limit: 10)
   -> Confirm target identity via existing drug-target relationships
```

**Critical:** If the gene symbol returns multiple targets or protein isoforms, clarify with the user before proceeding. Record the canonical IDs:
- Ensembl: ENSG00000xxxxx
- ChEMBL: CHEMBLxxxxx
- UniProt: Pxxxxx

### Phase 2: Disease Association Assessment

Quantify the strength of target-disease causal evidence.

```
1. mcp__opentargets__opentargets_info(method: "search_diseases", query: "disease_name")
   -> Get EFO disease ID

2. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   -> Association score with evidence breakdown (genetic, somatic, literature, known drugs, animal models)

3. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.3, size: 50)
   -> Rank the target vs. competing targets for this disease

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL disease_name genetic association GWAS", num_results: 15)
   -> Published human genetic evidence

5. mcp__ensembl__ensembl_data(method: "lookup_gene", gene_id: "GENE_SYMBOL", species: "homo_sapiens", expand: true)
   -> Gene coordinates, biotype, description for validation context

6. mcp__ensembl__ensembl_data(method: "get_homologs", gene_id: "ENSG00000xxxxx", type: "orthologues")
   -> Conservation across species — highly conserved targets suggest essential function (safety consideration)
```

### Phase 3: Druggability Assessment

Evaluate whether the target is tractable to therapeutic intervention.

```
1. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Tractability data: small molecule, antibody, other modalities
   -> Pharos Target Development Level (Tclin/Tchem/Tbio/Tdark)
   -> Protein family, subcellular location, binding sites

2. mcp__uniprot__uniprot_data(method: "get_protein_features", accession: "UNIPROT_ACC")
   -> Domain architecture, active sites, binding sites — confirms druggable pockets

3. mcp__uniprot__uniprot_data(method: "get_protein_domains_detailed", accession: "UNIPROT_ACC")
   -> Detailed domain boundaries for modality tractability assessment

4. mcp__uniprot__uniprot_data(method: "get_protein_orthologs", accession: "UNIPROT_ACC")
   -> Species conservation — essential for preclinical model selection

5. Classify by Pharos TDL:
   - Tclin: FDA-approved drug exists for this target (highest confidence)
   - Tchem: Active compounds with potency < 30 nM, no approved drug
   - Tbio: Gene Ontology experimental annotation, no active compounds
   - Tdark: Minimal annotation, no chemical matter (highest risk)
```

**Modality Tractability Matrix:**

| Target Feature | Small Molecule | Antibody | PROTAC/Degrader | Antisense/siRNA |
|---------------|---------------|----------|-----------------|-----------------|
| Extracellular/secreted | Possible | Preferred | N/A | Possible |
| Membrane-bound with pocket | Preferred | Possible | Possible | Possible |
| Intracellular enzyme | Preferred | N/A | Possible | Possible |
| GPCR / Ion channel | Preferred | Possible | N/A | Possible |
| PPI (flat surface) | Difficult | N/A | Preferred | Possible |
| Scaffolding protein | Difficult | N/A | Preferred | Preferred |
| Tdark (unknown biology) | Unknown | Unknown | Unknown | Possible |

### Phase 4: Chemical Matter Assessment

Determine existing chemical tools and drug-like starting points.

```
1. mcp__chembl__chembl_info(method: "get_bioactivity", target_id: "CHEMBLxxxxx", limit: 100)
   -> All known compound-target activity (IC50, Ki, EC50, Kd)

2. mcp__pubchem__pubchem_info(method: "search_compounds", query: "target_name inhibitor", search_type: "name")
   -> Chemical probes and tool compounds

3. mcp__pubchem__pubchem_info(method: "get_bioassay_results", cid: CID_NUMBER, limit: 50)
   -> Bioassay confirmatory data

4. mcp__chembl__chembl_info(method: "get_admet", chembl_id: "CHEMBLxxxxx")
   -> Drug-likeness of best compounds (Lipinski, MW, logP, PSA)
```

**Chemical Matter Scoring:**

| Chemical Matter Status | Score Contribution |
|-----------------------|-------------------|
| Approved drug for this target | +5 (de-risked) |
| Clinical candidate (Phase 1+) | +4 |
| Potent chemical probe (< 100 nM, selective) | +3 |
| Hit matter (< 1 uM, unoptimized) | +2 |
| Weak hits only (> 1 uM) | +1 |
| No known chemical matter | 0 (high risk) |

### Phase 5: Clinical Precedent Assessment

Check if the target or pathway has been clinically tested.

```
1. mcp__ctgov__ctgov_info(method: "search", condition: "disease_name", intervention: "target_name", pageSize: 50)
   -> Active/completed trials targeting this target

2. mcp__drugbank__drugbank_info(method: "search_by_target", target: "target_name", limit: 20)
   -> Approved or investigational drugs for this target

3. mcp__fda__fda_info(method: "lookup_drug", search_term: "target_name inhibitor", search_type: "label", limit: 10)
   -> FDA-approved drugs mentioning this target

4. mcp__fda__fda_info(method: "search_orange_book", drug_name: "known_drug_for_target")
   -> Approval status, formulations, generics
```

**Clinical Precedent Categories:**

| Category | Meaning | Risk Reduction |
|----------|---------|---------------|
| **Clinically validated** | Approved drug for same target-disease pair | Maximum de-risking |
| **Class validated** | Approved drug for same target, different disease | High — target biology confirmed |
| **Pathway validated** | Approved drug for upstream/downstream target | Moderate |
| **In clinical testing** | Phase 1-3 trials ongoing | Moderate (outcome uncertain) |
| **Preclinical only** | No clinical data for this target | Minimal de-risking |
| **Failed in clinic** | Target-directed drug failed trials | RED FLAG — investigate cause |

### Phase 6: Safety Profile Assessment

Evaluate on-target and pathway-related safety risks.

```
1. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Safety data: known on-target toxicities, essential gene status

2. mcp__fda__fda_info(method: "lookup_drug", search_term: "known_drug_for_target", search_type: "adverse_events", count: "patient.reaction.reactionmeddrapt.exact", limit: 20)
   -> Post-market adverse event profile for drugs hitting this target

3. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   -> Toxicity section, contraindications, black box warnings

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL knockout phenotype toxicity", num_results: 10)
   -> Genetic knockout phenotypes — proxy for on-target effects

5. mcp__ensembl__ensembl_data(method: "get_regulatory_features", region: "CHR:START-END", species: "homo_sapiens")
   -> Regulatory elements in gene region — assess regulatory complexity and tissue-specific expression context

6. mcp__gtex__gtex_data(method: "search_genes", query: "GENE_SYMBOL")
   -> Get GENCODE ID for GTEx expression queries

7. mcp__gtex__gtex_data(method: "get_median_gene_expression", gencodeId: "ENSG00000xxxxx.xx")
   -> Tissue expression profile — ubiquitous expression = higher on-target toxicity risk in critical tissues (heart, liver, kidney, brain, bone marrow)
```

**Safety Tissue Checklist — MANDATORY:**

For every target, assess expression and functional role in these 5 critical tissues:

| Tissue | Risk if target inhibited | Data source |
|--------|------------------------|-------------|
| **Heart** | QT prolongation, cardiomyopathy, heart failure | Open Targets expression, hERG liability, FAERS cardiac events |
| **Liver** | Hepatotoxicity, DILI, transaminase elevation | FAERS hepatic events, DrugBank toxicity, PubMed case reports |
| **Kidney** | Nephrotoxicity, renal impairment | FAERS renal events, knockout phenotype |
| **Brain** | CNS effects, seizures, psychiatric events | Blood-brain barrier penetration, FAERS psychiatric events |
| **Bone marrow** | Cytopenias, immunosuppression | FAERS hematologic events, knockout phenotype |

**Safety Classification:**

| Classification | Criteria |
|---------------|----------|
| **GREEN** | No safety signals in critical tissues, no essential gene, acceptable knockout phenotype |
| **YELLOW** | Manageable safety signals (e.g., GI effects, mild hepatic), therapeutic window expected |
| **ORANGE** | Significant safety concern in 1 critical tissue, requires careful dose optimization |
| **RED** | Safety signals in 2+ critical tissues, essential gene, lethal knockout, or black box warning class effect |

### Phase 7: Pathway Context

Map the target within its signaling/metabolic pathway to identify redundancy, feedback loops, and combination opportunities.

```
1. mcp__stringdb__stringdb_data(method: "get_protein_interactions", protein_id: "GENE_SYMBOL", species: 9606, limit: 25, required_score: 700)
   -> High-confidence interaction partners from STRING (identifies pathway neighbors and essential node status)

2. mcp__stringdb__stringdb_data(method: "get_functional_enrichment", protein_ids: ["GENE_SYMBOL", "PARTNER_1", "PARTNER_2"], species: 9606)
   -> Functional enrichment of target neighborhood to assess pathway redundancy and essentiality

3. mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   -> Metabolic/signaling pathway mapping

4. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Reactome pathways, GO biological processes

4b. mcp__reactome__reactome_data(method: "find_pathways_by_gene", gene_id: "GENE_SYMBOL", species: "Homo sapiens")
    -> Direct Reactome pathway lookup for the target with full pathway details

4c. mcp__reactome__reactome_data(method: "get_pathway_hierarchy", pathway_id: "R-HSA-XXXXX")
    -> Hierarchical context: identify if target sits in a redundant or linear pathway

4d. mcp__reactome__reactome_data(method: "get_pathway_participants", pathway_id: "R-HSA-XXXXX")
    -> All molecules in the pathway to assess pathway node essentiality

5. mcp__drugbank__drugbank_info(method: "search_by_target", target: "pathway_partner_target")
   -> Drugs hitting upstream/downstream nodes (combination rationale)

6. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL pathway resistance compensatory mechanism", num_results: 10)
   -> Known compensatory/resistance mechanisms
```

**Pathway Risk Factors:**

| Risk | Description | Impact |
|------|------------|--------|
| **Redundancy** | Parallel pathway can compensate | Reduced efficacy, resistance |
| **Feedback activation** | Inhibition triggers upstream activation | Rebound, paradoxical activation |
| **Essential node** | Target is hub in multiple critical pathways | Toxicity risk |
| **Single linear pathway** | No redundancy, clear biology | Favorable for validation |

### Phase 8: Validation Evidence Grading

Consolidate all evidence into a structured grade.

**Evidence Grade Hierarchy:**

| Grade | Evidence Type | Description |
|-------|-------------|-------------|
| **T1 — Clinical Proof** | Human clinical data showing target modulation leads to therapeutic benefit | Approved drug, positive Phase 2/3 trial |
| **T2 — Functional Studies** | CRISPR/siRNA knockdown, overexpression in human cells showing disease-relevant phenotype change | Cell-based functional validation |
| **T3 — Associations** | GWAS, Mendelian genetics, somatic mutations, expression changes in disease tissue | Correlative but not causal proof |
| **T4 — Predictions** | Text mining, pathway inference, animal model only, computational prediction | Hypothesis-generating only |

```
Assign evidence grade by reviewing:
1. Open Targets evidence breakdown (genetic_association, somatic_mutation, known_drug, affected_pathway, literature)
2. PubMed functional studies
3. Clinical trial outcomes (ctgov)
4. FDA approval status
```

### Phase 9: Structural Insights

Assess structural tractability for rational drug design.

```
1. mcp__pdb__pdb_data(method: "search_by_uniprot", uniprot_id: "UNIPROT_ACC", limit: 10)
   -> Find all experimental structures for the target

2. mcp__pdb__pdb_data(method: "get_structure_quality", pdb_id: "XXXX")
   -> Resolution, R-factor, validation metrics for best structures

3. mcp__alphafold__alphafold_data(method: "check_availability", uniprotId: "UNIPROT_ACC")
   -> Check if AlphaFold prediction exists

4. mcp__alphafold__alphafold_data(method: "analyze_confidence_regions", uniprotId: "UNIPROT_ACC")
   -> Identify high/low confidence regions for druggability assessment

5. mcp__pubchem__pubchem_info(method: "get_3d_conformer", cid: CID_NUMBER)
   -> 3D structure of known ligand

6. mcp__pubchem__pubchem_info(method: "get_compound_properties", cid: CID_NUMBER)
   -> Physicochemical properties of best compounds

7. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL crystal structure binding site X-ray cryo-EM", num_results: 10)
   -> Published structural data

8. mcp__pubchem__pubchem_info(method: "search_similar_compounds", smiles: "SMILES_STRING", threshold: 80)
   -> Structural analogs for SAR inference

9. mcp__uniprot__uniprot_data(method: "get_protein_variants", accession: "UNIPROT_ACC")
   -> Known variants near binding sites that may affect drug design
```

**Structural Readiness Assessment:**

| Level | Status | Implication |
|-------|--------|------------|
| **High** | Co-crystal structure with ligand available (PDB) | Structure-based drug design possible |
| **Medium** | Apo structure available, homology model feasible | Computational docking possible |
| **Low** | No structure, no close homolog | Ligand-based or phenotypic screening required |

### DepMap Essentiality Validation

Assess functional essentiality using CRISPR knockout data from the Cancer Dependency Map. This is the gold standard for determining whether a gene is required for cancer cell survival — critical for oncology targets.

```
1. Query gene dependency scores across all cancer cell lines:
   mcp__depmap__depmap_data(method="get_gene_dependency", gene="EGFR")
   -> Chronos dependency scores per cell line (negative = essential, < -0.5 = strong dependency)

2. Assess if the target is common essential vs selectively essential:
   mcp__depmap__depmap_data(method="get_gene_dependency_summary", genes=["EGFR", "ERBB2", "ERBB3"])
   -> Pan-cancer dependency statistics
   -> Common essential (dependency in >90% of lines): poor therapeutic window — inhibition kills normal cells too
   -> Selectively essential (dependency in specific lineages): ideal drug target — tumor-specific vulnerability

3. Check lineage-specific dependencies:
   mcp__depmap__depmap_data(method="get_context_info")
   -> Available cancer lineages and subtypes
   -> Cross-reference dependency scores with lineage to identify which cancer types depend on the target

4. Run biomarker analysis for synthetic lethality:
   mcp__depmap__depmap_data(method="get_biomarker_analysis", target_gene="SHP2", biomarker_gene="KRAS")
   -> Does KRAS mutation predict dependency on SHP2?
   -> Positive result = synthetic lethality opportunity = patient selection biomarker

5. Check mutation status of the target itself:
   mcp__depmap__depmap_data(method="get_mutations", gene="EGFR")
   -> Mutation landscape across cell lines — activating mutations may drive dependency

6. Multi-gene co-dependency for pathway validation:
   mcp__depmap__depmap_data(method="get_multi_gene_profile", genes=["EGFR", "ERBB2", "ERBB3", "SOS1", "SHP2"])
   -> Co-dependency patterns reveal functional pathway relationships
   -> Genes with correlated dependency scores operate in the same pathway
   -> Useful for identifying combination targets and resistance mechanisms

7. Expression correlation with dependency:
   mcp__depmap__depmap_data(method="get_gene_expression", gene="EGFR")
   -> Does high expression predict dependency? If yes, expression could serve as a patient selection biomarker
```

**DepMap Essentiality Classification:**

| Classification | Criteria | Implication |
|---------------|----------|-------------|
| **Common Essential** | Dependency in >90% of cell lines, median Chronos < -0.5 | Poor therapeutic window — target is required by normal cells too |
| **Selectively Essential** | Strong dependency in specific lineages/genotypes only | Ideal oncology target — tumor-selective vulnerability |
| **Context-Dependent** | Dependency depends on biomarker (e.g., mutation in another gene) | Synthetic lethality opportunity — requires companion diagnostic |
| **Non-Essential** | No significant dependency in any cell line | Target modulation unlikely to kill cancer cells — consider non-oncology indication or non-viability mechanism |

### Phase 10: Validation Roadmap

Synthesize all 9 phases into the Target Validation Score and GO/NO-GO recommendation with a proposed experimental validation plan.

---

## Target Validation Score (0-100)

### Scoring Breakdown

| Dimension | Max Points | Sub-scores |
|-----------|-----------|------------|
| **Disease Association** | 25 | Human genetics (GWAS/Mendelian): 0-10, Somatic mutations: 0-5, Expression in disease tissue: 0-5, Animal model validation: 0-5 |
| **Druggability** | 25 | Pharos TDL (Tclin=10, Tchem=7, Tbio=3, Tdark=0): 0-10, Binding site/pocket: 0-5, Modality tractability: 0-5, Chemical matter quality: 0-5 |
| **Safety Profile** | 20 | Critical tissue safety (GREEN=20, YELLOW=15, ORANGE=8, RED=0): 0-20 |
| **Clinical Precedent** | 10 | Clinically validated=10, Class validated=8, Pathway validated=6, In clinical testing=4, Preclinical only=1, Failed=0 |
| **Validation Evidence** | 10 | T1=10, T2=7, T3=4, T4=1 |
| **DepMap Essentiality** | 10 | Selectively essential with biomarker=10, Selectively essential=8, Context-dependent=6, Common essential=3, Non-essential (oncology)=0 |

### Calculating the Score

```
Step 1: Disease Association (max 25)
  - Human genetics: Check Open Targets genetic_association score
    * GWAS + Mendelian = 10, GWAS only = 7, suggestive = 3, none = 0
  - Somatic mutations: Check somatic_mutation score
    * Recurrent driver mutations = 5, any somatic evidence = 3, none = 0
  - Expression: Disease vs normal tissue differential expression
    * Strong differential = 5, moderate = 3, none = 0
  - Animal models: Knockout/transgenic phenotype recapitulates disease
    * Strong phenocopy = 5, partial = 3, none = 0

Step 2: Druggability (max 25)
  - Pharos TDL: From Open Targets target details
  - Binding site: Crystal structure with pocket = 5, predicted = 3, unknown = 0
  - Modality: Multiple modalities tractable = 5, single = 3, none feasible = 0
  - Chemical matter: See Phase 4 scoring table above

Step 3: Safety Profile (max 20)
  - Apply Safety Tissue Checklist from Phase 6
  - Assign GREEN/YELLOW/ORANGE/RED classification
  - Map to points

Step 4: Clinical Precedent (max 10)
  - Apply categories from Phase 5

Step 5: Validation Evidence (max 10)
  - Assign evidence grade from Phase 8

Step 6: DepMap Essentiality (max 10)
  - Query DepMap dependency scores and biomarker analysis
  - Selectively essential with predictive biomarker = 10
  - Selectively essential (lineage-specific dependency) = 8
  - Context-dependent (dependency correlates with specific genotype) = 6
  - Common essential (dependency in >90% of lines) = 3 (poor therapeutic window)
  - Non-essential in cancer cell lines (oncology target) = 0
  - For non-oncology targets: score based on whether essentiality data supports or contradicts the safety profile
```

### Score Ceiling Rules (Conservative Guardrails)

Before assigning the final tier, apply these ceiling checks:

- **Clinical Precedent = 0 or 1 (Preclinical only / Failed):** Total score is CAPPED at 55 regardless of other dimensions. Rationale: without any human clinical proof-of-concept, a target cannot be CONDITIONAL GO or GO. Preclinical-only targets are CAUTION at best.
- **Clinical Precedent ≤ 4 (In clinical testing, no efficacy data):** Total score is CAPPED at 70. Rationale: Phase 1 dosing alone does not validate the target.
- **Druggability ≤ 10 (low tractability):** Total score is CAPPED at 55. Rationale: strong biology without a drugable path is not actionable.
- **Safety Profile = RED (0 points):** Total score is CAPPED at 40. Rationale: unacceptable safety risk overrides all other dimensions.

Apply ceilings AFTER computing the raw sum. If multiple ceilings apply, use the lowest.

### Priority Tiers and GO/NO-GO Decisions

| Tier | Score Range | Decision | Action |
|------|-----------|----------|--------|
| **Tier 1 — GO** | 80-100 | Proceed to lead optimization | High-confidence target. Initiate medicinal chemistry campaign. |
| **Tier 2 — CONDITIONAL GO** | 60-79 | Proceed with risk mitigation | Viable target with addressable gaps. Define experiments to close gaps before full commitment. |
| **Tier 3 — CAUTION** | 40-59 | Further validation required | Significant uncertainties remain. Invest in target validation experiments before chemistry. |
| **Tier 4 — NO-GO** | 0-39 | Do not pursue | Insufficient evidence, poor druggability, or unacceptable safety risk. Document rationale and archive. |

### GO/NO-GO Report Template

```
TARGET VALIDATION REPORT
========================
Target: [GENE_SYMBOL] ([Full Name])
Disease: [Disease Name]
Date: [Date]

VALIDATION SCORE: [XX]/100 — [TIER X: DECISION]

DIMENSION SCORES:
  Disease Association:    [XX]/25
  Druggability:          [XX]/25
  Safety Profile:        [XX]/20
  Clinical Precedent:    [XX]/10
  Validation Evidence:   [XX]/10
  DepMap Essentiality:   [XX]/10

KEY FINDINGS:
  Strengths:
  - [...]
  Risks:
  - [...]
  Critical Gaps:
  - [...]

RECOMMENDATION: [GO / CONDITIONAL GO / CAUTION / NO-GO]
  [1-2 sentence rationale]

NEXT STEPS (if GO or CONDITIONAL GO):
  1. [Specific experimental validation]
  2. [Chemistry milestone]
  3. [Timeline estimate]
```

---

### Comprehensive Target Validation: Genetics + Cancer + Chemical

Combine gnomAD, cBioPortal, and BindingDB for multi-dimensional target validation integrating genetic constraint, cancer genomics, and chemical tractability.

```
1. Assess genetic essentiality (gnomAD):
   mcp__gnomad__gnomad_data(method: "get_gene_constraint", gene: "GENE_SYMBOL")
   -> LoF intolerant (pLI > 0.9, LOEUF < 0.35) = gene is essential — validates target but flags safety risk
   -> LoF tolerant = gene is dispensable — weaker validation for essentiality-based mechanisms

2. Search for natural human knockouts (gnomAD):
   mcp__gnomad__gnomad_data(method: "filter_rare_variants", gene: "GENE_SYMBOL")
   -> Rare LoF variants in healthy individuals = natural human knockouts
   -> If carriers are healthy, target inhibition may be safe (positive safety signal)
   -> If no LoF carriers exist, gene is likely essential (confirms constraint data)

3. Check somatic mutation frequency (cBioPortal):
   mcp__cbioportal__cbioportal_data(method: "get_mutation_frequency", gene: "GENE_SYMBOL")
   -> High frequency across cancers = strong oncogene/TSG evidence
   -> Mutation frequency validates the target for oncology indications

4. Identify hotspot mutations (cBioPortal):
   mcp__cbioportal__cbioportal_data(method: "get_mutations", gene: "GENE_SYMBOL")
   -> Recurrent hotspot mutations = gain-of-function evidence (oncogene)
   -> Distributed truncating mutations = loss-of-function evidence (tumor suppressor)
   -> Hotspot location informs drug binding site selection

5. Assess chemical tractability (BindingDB):
   mcp__bindingdb__bindingdb_data(method: "get_ligands_by_target", target: "TARGET_NAME")
   -> Existing binders confirm the target is druggable
   -> Number and diversity of binders indicates tractability depth

6. Evaluate achievable potency (BindingDB):
   mcp__bindingdb__bindingdb_data(method: "get_ki_by_target", target: "TARGET_NAME")
   -> Ki value distribution establishes the binding affinity landscape
   -> Sub-nanomolar Ki values = highly druggable with potent compounds achievable
   -> Only micromolar Ki values = may require significant medicinal chemistry optimization

7. Integrate across all three databases:
   - gnomAD constrained + cBioPortal hotspot mutations + BindingDB binders = STRONG VALIDATION (essential, mutated in cancer, druggable)
   - gnomAD constrained + no cBioPortal mutations + BindingDB binders = validated essential target, non-oncology indication, druggable
   - gnomAD tolerant + cBioPortal mutations + no BindingDB binders = cancer-relevant but chemically intractable — needs screening
   - gnomAD tolerant + no mutations + no binders = WEAK VALIDATION — reconsider target
   - Feed integrated findings into Phase 10 scoring (Disease Association, Druggability, Safety dimensions)
```

---

## Literature Collision Detection

**MANDATORY before PubMed searches:** Gene symbols are frequently ambiguous (e.g., ACE = angiotensin-converting enzyme OR a gene in Drosophila, BRAF = the kinase OR unrelated contexts).

### Detection Protocol

```
1. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL", num_results: 20)
   -> Scan first 20 results

2. Count off-topic results:
   - If > 20% of results are clearly off-topic (wrong organism, wrong protein, unrelated field):
     -> COLLISION DETECTED

3. Add disambiguation terms to all subsequent searches:
   - Add protein name: "BRAF AND (serine-threonine kinase OR melanoma OR V600E)"
   - Add organism: "GENE_SYMBOL AND (human OR Homo sapiens)"
   - Exclude noise: "GENE_SYMBOL NOT Drosophila NOT yeast"

4. Record collision status in the validation report
```

---

## Negative Results Protocol

**"No data" is a finding, not a gap in the report.** Every phase MUST produce output.

| Phase | If no data found | Document as |
|-------|-----------------|-------------|
| Disease Association | No GWAS, no Mendelian, no somatic | "No human genetic evidence. Disease Association sub-score: 0/30. This is a significant validation gap." |
| Druggability | Tdark classification, no ligands | "Target is Tdark with no known chemical matter. Druggability sub-score: 0/25. Phenotypic screening or genetic modulation required." |
| Chemical Matter | No compounds in ChEMBL/PubChem | "No chemical probes or tool compounds available. De novo screening campaign required." |
| Clinical Precedent | No trials, no approved drugs | "No clinical precedent for this target. First-in-class risk applies." |
| Safety | No knockout data, no FAERS data | "Safety profile is UNKNOWN — not GREEN. Insufficient data to assess risk. Recommend generating knockout/knockdown data." |
| Structural | No crystal structure, no homolog | "No structural data available. Structure-based drug design not currently possible." |
| DepMap Essentiality | Gene not in DepMap, no dependency data | "No DepMap essentiality data available. Functional essentiality unconfirmed — recommend CRISPR validation in relevant cell lines." |

**Critical rule:** Empty data is NEVER scored as favorable. Unknown safety is NOT safe. Missing evidence scores 0, not "pending."

---

## Druggability Deep Dive

### Pharos Target Development Level (TDL) Classification

| TDL | Definition | Validation Implication |
|-----|-----------|----------------------|
| **Tclin** | Target of an approved drug | Clinically validated, highest confidence |
| **Tchem** | Has small molecule activity < 30 nM (Ki/Kd/IC50/EC50), satisfying IDG activity thresholds | Chemically tractable, tool compounds available |
| **Tbio** | Has Gene Ontology experimental annotation OR OMIM phenotype | Biologically characterized but no chemical tools |
| **Tdark** | Protein with virtually no known biology; < 5 PubMed publications | Highest risk — biology and chemistry unknown |

### Druggability Decision Tree

```
Is the target Tclin?
  YES -> Score 10/10, proceed to modality selection
  NO -> Continue

Is the target Tchem?
  YES -> Score 7/10, assess compound quality
  NO -> Continue

Is the target Tbio?
  YES -> Score 3/10, check for structural data and predicted pockets
  NO -> Target is Tdark

Is the target Tdark?
  YES -> Score 0/10, FLAG: requires significant biology investment before chemistry
```

### Small Molecule vs Antibody vs Other Modality

```
1. Check subcellular location (Open Targets target details):
   - Extracellular/secreted -> Antibody preferred
   - Membrane with binding pocket -> Small molecule or antibody
   - Intracellular with enzymatic site -> Small molecule preferred
   - Intracellular without pocket -> PROTAC or antisense

2. Check protein family:
   - Kinase, GPCR, nuclear receptor, protease, ion channel -> Small molecule
   - Cytokine, growth factor, receptor ligand -> Antibody
   - Transcription factor, scaffolding protein -> Degrader or antisense

3. Assess chemical matter from Phase 4:
   - Potent small molecules exist -> Small molecule modality confirmed
   - No small molecule tools -> Consider biologic or genetic modality
```

---

## Complete Validation Workflow Example

### Validating KRAS G12C for Non-Small Cell Lung Cancer

```
PHASE 1 — Disambiguation:
mcp__opentargets__opentargets_info(method: "search_targets", query: "KRAS", size: 5)
mcp__chembl__chembl_info(method: "target_search", query: "KRAS", limit: 5)
-> Ensembl: ENSG00000133703, ChEMBL: CHEMBL4630

PHASE 2 — Disease Association:
mcp__opentargets__opentargets_info(method: "search_diseases", query: "non-small cell lung cancer")
mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000133703", diseaseId: "EFO_0003060")
-> Score: 0.95 — strong genetic, somatic, known drug evidence
-> Disease Association: 28/30

PHASE 3 — Druggability:
mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000133703")
-> Tclin (sotorasib approved), switch-II pocket identified
-> Druggability: 23/25

PHASE 4 — Chemical Matter:
mcp__chembl__chembl_info(method: "get_bioactivity", target_id: "CHEMBL4630", limit: 100)
-> Multiple covalent inhibitors, sotorasib IC50 = 12 nM
-> Chemical matter: excellent

PHASE 5 — Clinical Precedent:
mcp__ctgov__ctgov_info(method: "search", condition: "NSCLC", intervention: "KRAS G12C", pageSize: 50)
mcp__fda__fda_info(method: "lookup_drug", search_term: "sotorasib", search_type: "label")
-> Sotorasib approved (accelerated), adagrasib approved
-> Clinical Precedent: 15/15

PHASE 6 — Safety:
mcp__fda__fda_info(method: "lookup_drug", search_term: "sotorasib", search_type: "adverse_events", count: "patient.reaction.reactionmeddrapt.exact", limit: 20)
mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DB16641")
-> Hepatotoxicity signal (YELLOW for liver), GI events
-> Safety: 15/20

PHASE 7 — Pathway:
mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DB16641")
-> RAS-MAPK pathway; resistance via MAPK reactivation documented
-> Combination rationale: SHP2 or SOS1 inhibitors

PHASE 8 — Evidence Grade:
-> T1: Clinical proof (approved drugs)
-> Validation Evidence: 10/10

PHASE 9 — Structural:
mcp__pubchem__pubchem_info(method: "get_3d_conformer", cid: 137600584)
-> Co-crystal structures available (PDB: 6OIM, 7RPZ)
-> Structural readiness: HIGH

DepMap ESSENTIALITY:
mcp__depmap__depmap_data(method="get_gene_dependency", gene="KRAS")
-> KRAS is selectively essential in KRAS-mutant lines (not common essential)
mcp__depmap__depmap_data(method="get_biomarker_analysis", target_gene="KRAS", biomarker_gene="KRAS")
-> KRAS mutation strongly predicts KRAS dependency (oncogene addiction)
mcp__depmap__depmap_data(method="get_gene_dependency_summary", genes=["KRAS", "SOS1", "SHP2"])
-> Co-dependency with SOS1/SHP2 confirms RAS pathway vulnerability
-> DepMap Essentiality: 10/10 (selectively essential with predictive biomarker)

PHASE 10 — Score:
Disease Association: 23/25
Druggability: 23/25
Safety: 15/20
Clinical Precedent: 10/10
Validation Evidence: 10/10
DepMap Essentiality: 10/10
TOTAL: 91/100 — TIER 1: GO
```

---

## Multi-Agent Workflow Examples

**"Validate PCSK9 as a target for hypercholesterolemia"**
1. Drug Target Validator -> 10-phase pipeline, Target Validation Score, GO/NO-GO
2. Drug Target Analyst -> Deep target characterization, bioactivity SAR, pathway mapping
3. Clinical Trial Analyst -> Phase 3/4 trial outcomes for PCSK9 inhibitors
4. FDA Consultant -> Regulatory history, post-market safety, patent landscape

**"Compare validation strength of three oncology targets"**
1. Drug Target Validator -> Run 10-phase pipeline for each target, compare scores side-by-side
2. Drug Repurposing Analyst -> Check if existing drugs could be repurposed for any target
3. Chemical Safety Toxicology -> ADMET/toxicity comparison of lead compounds per target
4. Network Pharmacologist -> Pathway overlap and combination rationale

**"Should we pursue CDK9 for AML?"**
1. Drug Target Validator -> Full validation pipeline with GO/NO-GO recommendation
2. Drug Target Analyst -> CDK9 selectivity vs CDK family members (CDK7, CDK12, CDK13)
3. Clinical Trial Analyst -> CDK9 inhibitor trial outcomes (failures = RED FLAG)
4. FDA Consultant -> Regulatory precedent for CDK inhibitors in heme-onc

**"De-risk a Tdark target for rare disease"**
1. Drug Target Validator -> 10-phase pipeline (expect low scores — document gaps precisely)
2. Drug Target Analyst -> Deep literature mining, pathway placement, closest characterized paralog
3. Network Pharmacologist -> Pathway-level druggability even if target itself is Tdark
4. Clinical Trial Analyst -> Any trials for this pathway, natural history studies

**"Validate target panel for inflammatory bowel disease"**
1. Drug Target Validator -> Batch validation of 5-10 targets, ranked by score
2. Drug Repurposing Analyst -> Repurposing candidates from approved anti-inflammatory drugs
3. Chemical Safety Toxicology -> Immunosuppression risk assessment for each target
4. FDA Consultant -> IBD regulatory landscape, breakthrough therapy precedents

---

## Completeness Checklist

- [ ] Target disambiguated across Open Targets, ChEMBL, and DrugBank
- [ ] All 10 validation phases executed and documented
- [ ] Target Validation Score calculated with all 6 dimension sub-scores
- [ ] GO/NO-GO tier assigned with rationale
- [ ] Disease association scored (genetics, somatic, expression, animal models)
- [ ] Druggability assessed with Pharos TDL classification
- [ ] Safety tissue checklist applied with RED/YELLOW/GREEN classification
- [ ] DepMap essentiality data integrated (selectively essential vs common essential)
- [ ] Negative results protocol followed for any phase with no data
- [ ] Validation roadmap and next steps provided for GO/CONDITIONAL GO decisions
