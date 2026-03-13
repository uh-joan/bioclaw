---
name: protein-structure-retrieval
description: Protein structure retrieval and assessment specialist. Retrieves and assesses protein structural data from PDB and AlphaFold with quality tiering, ligand analysis, and use-case-specific routing. Use when user mentions protein structure, PDB, AlphaFold, crystal structure, cryo-EM, X-ray crystallography, resolution, binding site, ligand-bound structure, co-crystal, binding pocket, pLDDT, structure quality, homology model, 3D structure, protein conformation, structural data, R-factor, electron density.
---

# Protein Structure Retrieval

Retrieves and assesses protein structural data from PDB and AlphaFold with quality tiering, ligand analysis, and use-case-specific routing. Uses Open Targets for structure references via target details, ChEMBL for compound-structure relationships, DrugBank for drug-protein structural data, PubMed for structure determination literature, and PubChem for compound 3D structures.

## Report-First Workflow

1. **Create report file immediately**: `[target]_structure_retrieval_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## Cross-Reference: Other Skills

- **Target identification and druggability** → use target-research skill
- **Drug-target pharmacology and bioactivity** → use drug-target-analyst skill
- **Binder design against structural targets** → use binder-discovery-specialist skill
- **Antibody engineering with structural context** → use antibody-engineering skill
- **Protein-protein interaction interfaces** → use protein-interactions skill
- **ESMFold single-sequence structure prediction (no MSA needed)** → use esm-protein-design skill

## When NOT to Use This Skill

- Target druggability scoring or tractability assessment → use `target-research`
- Bioactivity data mining or SAR analysis → use `drug-target-analyst`
- De novo binder design or scaffold optimization → use `binder-discovery-specialist`
- Antibody CDR engineering or humanization → use `antibody-engineering`
- PPI network construction or hub protein analysis → use `protein-interactions`
- De novo protein therapeutic design or ProteinMPNN workflows → use `protein-therapeutic-design`

## Available MCP Tools

### `mcp__opentargets__opentargets_info` (Target Details with Structure References)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `search_diseases` | Search diseases by name/synonym | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId` (Ensembl ID), `diseaseId` (EFO ID), `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability, structure refs) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes) | `id` (EFO ID) |

### `mcp__chembl__chembl_info` (Compound-Structure Relationships)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |
| `get_admet` | ADMET/drug-likeness properties | `chembl_id` |

### `mcp__drugbank__drugbank_info` (Drug-Protein Structural Data)

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

### `mcp__pubmed__pubmed_articles` (Structure Determination Literature)

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
| `get_protein_sequence` | Get protein sequence (FASTA/JSON) | `accession`, `format` |
| `get_protein_features` | Protein features (domains, sites, PTMs) | `accession` |
| `get_protein_structure` | Structural data (PDB, AlphaFold) | `accession` |
| `get_protein_domains_detailed` | Detailed domain architecture | `accession` |

### `mcp__pubchem__pubchem_info` (Compound 3D Structures)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_by_name` | Search compound by name | `name` |
| `search_by_smiles` | Search by SMILES string | `smiles` |
| `search_by_inchi` | Search by InChI | `inchi` |
| `search_by_formula` | Search by molecular formula | `formula` |
| `get_compound_details` | Full compound profile (2D/3D structure, properties) | `cid` |
| `get_compound_properties` | Physicochemical properties | `cid` |
| `get_compound_synonyms` | All synonyms and identifiers | `cid` |
| `get_compound_sids` | Substance IDs linked to compound | `cid` |
| `get_compound_aids` | BioAssay IDs linked to compound | `cid` |
| `get_3d_conformer` | 3D conformer coordinates | `cid` |
| `search_by_similarity` | Similar compound search by structure | `smiles` or `cid`, `threshold` |
| `search_by_substructure` | Substructure search | `smiles` |

### `mcp__alphafold__alphafold_data` (AlphaFold Predicted Structures)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_structure` | Get AlphaFold predicted structure | `uniprotId`, `format` (json/pdb/cif) |
| `download_structure` | Download structure file | `uniprotId`, `format` |
| `check_availability` | Check if prediction exists | `uniprotId` |
| `get_confidence_scores` | Get pLDDT confidence scores | `uniprotId` |
| `analyze_confidence_regions` | Identify high/low confidence regions | `uniprotId` |
| `get_prediction_metadata` | Prediction version and metadata | `uniprotId` |
| `batch_structure_info` | Batch lookup multiple proteins | `uniprotIds` |
| `batch_confidence_analysis` | Batch confidence analysis | `uniprotIds` |
| `compare_structures` | Compare two predicted structures | `uniprotId1`, `uniprotId2` |
| `find_similar_structures` | Find structurally similar proteins | `uniprotId` |
| `validate_structure_quality` | Quality assessment | `uniprotId` |

### `mcp__pdb__pdb_data` (Experimental Structures from PDB)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_structures` | Search experimental structures | `query`, `limit`, `experimental_method`, `resolution_range`, `sort_by` |
| `get_structure_info` | Get structure details | `pdb_id`, `format` |
| `download_structure` | Download structure file | `pdb_id`, `format` |
| `search_by_uniprot` | Find PDB structures for UniProt ID | `uniprot_id`, `limit` |
| `get_structure_quality` | Resolution, R-factor, validation | `pdb_id` |

---

## 4-Phase Structure Retrieval Workflow

### Phase 1: Clarification and Protein Disambiguation

```
1. Determine input type:
   - PDB ID (e.g., 1HHO, 6LU7) → proceed directly to retrieval
   - UniProt accession (e.g., P00533) → map to PDB entries
   - Gene symbol or protein name → resolve to identifiers

2. mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL_OR_NAME")
   → Get Ensembl gene ID and confirm protein identity

3. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Retrieve target profile including PDB cross-references, UniProt ID, protein class

4. mcp__uniprot__uniprot_data(method: "get_protein_structure", accession: "UNIPROT_ACC")
   → PDB and AlphaFold structure cross-references from UniProt

5. mcp__uniprot__uniprot_data(method: "get_protein_domains_detailed", accession: "UNIPROT_ACC")
   → Detailed domain architecture to identify structurally characterized regions

6. Determine use case:
   - Drug discovery → prioritize ligand-bound, high-resolution structures
   - Homology modeling → prioritize template selection by coverage and resolution
   - Structure comparison → systematic cross-variant retrieval
   - General inquiry → best available structure with quality summary
```

### Phase 2: Multi-Database Retrieval with Fallback Chain

```
Primary: Experimental structure (PDB)
1. mcp__pdb__pdb_data(method: "search_by_uniprot", uniprot_id: "UNIPROT_ACC", limit: 20)
   → Find all PDB structures for this protein directly

2. mcp__pdb__pdb_data(method: "get_structure_info", pdb_id: "XXXX", format: "json")
   → Get structure details (method, resolution, ligands, chains)

3. mcp__pdb__pdb_data(method: "get_structure_quality", pdb_id: "XXXX")
   → Resolution, R-factor, validation metrics for quality tier assignment

4. mcp__chembl__chembl_info(method: "target_search", query: "target_name")
   → Get ChEMBL target ID for compound-structure lookups

5. mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "CHEMBLxxxxx", limit: 50)
   → Identify compounds with known co-crystal structures

Fallback 1: AlphaFold predicted structure
4. mcp__alphafold__alphafold_data(method: "check_availability", uniprotId: "UNIPROT_ACC")
   → Check if AlphaFold prediction exists for this protein
5. mcp__alphafold__alphafold_data(method: "get_structure", uniprotId: "UNIPROT_ACC", format: "pdb")
   → Retrieve AlphaFold predicted structure
6. mcp__alphafold__alphafold_data(method: "get_confidence_scores", uniprotId: "UNIPROT_ACC")
   → Get pLDDT confidence scores per residue
7. mcp__alphafold__alphafold_data(method: "analyze_confidence_regions", uniprotId: "UNIPROT_ACC")
   → Identify high/low confidence regions for quality assessment
8. mcp__uniprot__uniprot_data(method: "get_protein_features", accession: "UNIPROT_ACC")
   → Map functional sites and domains onto AlphaFold prediction for confidence context

Fallback 2: Homology model
5. If no AlphaFold prediction available:
   → Search PubMed for published homology models
   → mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "PROTEIN_NAME homology model structure", num_results: 10)

Fallback 3: Related structures
6. mcp__drugbank__drugbank_info(method: "search_by_target", target: "target_name")
   → Find drugs with known binding data → infer structural information
7. mcp__pubchem__pubchem_info(method: "get_3d_conformer", cid: "CID")
   → Retrieve 3D conformer for bound ligands
```

### Phase 3: Quality Assessment

```
1. Apply Quality Tier rating (see framework below)
2. Assess completeness:
   - Chain coverage (full-length vs fragment)
   - Missing residues/loops
   - Ligand occupancy and B-factors
3. Cross-validate across databases:
   - mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
     → Confirm structural binding data for known drugs
   - mcp__pubchem__pubchem_info(method: "get_compound_details", cid: "CID")
     → Verify ligand identity and 3D structure
```

### Phase 4: Quality-Assessed Report Generation

```
Compile Structure Profile Report (see template below) including:
- All available structures ranked by quality tier
- Ligand analysis for drug discovery use cases
- AlphaFold confidence mapping for regions without experimental data
- Recommended structure for the stated use case
- Download links and database cross-references
```

---

## Quality Assessment Framework

### Experimental Structure Quality Tiers

| Tier | Resolution | Rating | Suitability |
|------|-----------|--------|-------------|
| **T1 — Excellent** | < 1.5 Å | Atomic detail, individual atoms resolved | Drug design, binding site analysis, water network |
| **T2 — Good** | 1.5–2.0 Å | Clear side-chain density | Docking, SAR interpretation, ligand placement |
| **T3 — Moderate** | 2.0–3.0 Å | Backbone trace reliable, side-chains approximate | Homology modeling template, domain architecture |
| **T4 — Low** | > 3.0 Å | Overall fold only | Topology confirmation, domain boundaries |

### Additional Quality Metrics

| Metric | Good | Acceptable | Concerning |
|--------|------|-----------|------------|
| **R-free** | < 0.22 | 0.22–0.28 | > 0.28 |
| **R-work** | < 0.18 | 0.18–0.25 | > 0.25 |
| **R-free − R-work** | < 0.05 | 0.05–0.08 | > 0.08 (possible overfitting) |
| **Clashscore** | < 5 | 5–15 | > 15 |
| **Ramachandran outliers** | < 0.5% | 0.5–2% | > 2% |

### AlphaFold Confidence (pLDDT) Assessment

| pLDDT Range | Confidence | Interpretation |
|-------------|-----------|----------------|
| **> 90** | Very high | Backbone and side-chain positions reliable |
| **70–90** | Good | Backbone reliable, some side-chain uncertainty |
| **50–70** | Uncertain | Fold may be correct, loops/disorder likely |
| **< 50** | Low | Likely disordered or unstructured region |

### Experimental Method Considerations

| Method | Typical Resolution | Strengths | Limitations |
|--------|-------------------|-----------|-------------|
| **X-ray crystallography** | 1.0–3.0 Å | Highest resolution, mature method | Crystal packing artifacts, static snapshot |
| **Cryo-EM** | 2.0–4.0 Å | Large complexes, near-native state | Resolution varies by region, flexibility |
| **NMR** | N/A (ensemble) | Solution state, dynamics | Size limit (~40 kDa), no single resolution value |
| **Neutron diffraction** | 1.5–2.5 Å | Hydrogen positions visible | Requires large crystals, rare |

---

## Use-Case Routing

### Drug Discovery (Ligand-Bound, High-Resolution)

```
Priority: T1/T2 ligand-bound structures
1. mcp__pdb__pdb_data(method: "search_structures", query: "TARGET_NAME", experimental_method: "X-RAY DIFFRACTION", resolution_range: "0-2.0", sort_by: "resolution", limit: 20)
   → Search for high-resolution ligand-bound structures

2. mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "CHEMBLxxxxx", limit: 100)
   → Map compounds with co-crystal structures to activity data

3. mcp__drugbank__drugbank_info(method: "search_by_target", target: "target_name")
   → Identify approved drugs with known binding poses

4. mcp__pubchem__pubchem_info(method: "get_3d_conformer", cid: "CID")
   → Retrieve 3D conformer of best ligands for docking reference

5. Filter structures:
   - Resolution < 2.0 Å preferred
   - Must contain bound ligand (not apo)
   - R-free < 0.25
   - Report binding site residues and pocket properties
```

### Homology Modeling (Template Selection)

```
Priority: Highest coverage + best resolution
1. Retrieve all available structures for target and close homologs

2. mcp__opentargets__opentargets_info(method: "search_targets", query: "protein_family", size: 20)
   → Find related family members with solved structures

3. Rank templates by:
   - Sequence identity to query (> 30% threshold)
   - Resolution (T1/T2 preferred)
   - Chain coverage (full-length preferred)
   - Presence of functionally relevant ligands/cofactors

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "PROTEIN homology model template crystal structure", num_results: 10)
   → Published homology modeling studies for this target
```

### Structure Comparison (Systematic Cross-Variant)

```
1. Retrieve all structures for the target protein
   → Different conformational states (apo, holo, inhibitor-bound, substrate-bound)
   → Different species orthologs
   → Mutant vs wild-type

2. mcp__chembl__chembl_info(method: "compound_search", query: "compound_name")
   → Identify specific co-crystallized compounds

3. mcp__drugbank__drugbank_info(method: "get_similar_drugs", drugbank_id: "DBxxxxx", limit: 20)
   → Find structurally related drugs for binding mode comparison

4. Tabulate comparison:
   - PDB ID | Resolution | Ligand | Conformation | Species | Key differences
```

---

## Ligand Analysis

### Binding Site Characterization

```
1. From ligand-bound structure:
   - Identify binding pocket residues (within 4 Å of ligand)
   - Classify interactions: hydrogen bonds, hydrophobic, π-stacking, salt bridges
   - Assess pocket volume and druggability

2. mcp__pubchem__pubchem_info(method: "get_compound_details", cid: "CID")
   → Full compound profile of co-crystallized ligand

3. mcp__pubchem__pubchem_info(method: "get_compound_properties", cid: "CID")
   → Physicochemical properties relevant to binding

4. mcp__pubchem__pubchem_info(method: "search_by_similarity", cid: "CID", threshold: 0.8)
   → Find similar compounds that may also bind the pocket

5. mcp__chembl__chembl_info(method: "get_admet", chembl_id: "CHEMBLxxxxx")
   → Drug-likeness of known binders
```

### Co-Crystallized Compound Analysis

```
1. mcp__chembl__chembl_info(method: "compound_search", query: "ligand_name")
   → Get ChEMBL ID and properties

2. mcp__drugbank__drugbank_info(method: "search_by_name", query: "ligand_name")
   → Check if ligand is an approved/investigational drug

3. mcp__pubchem__pubchem_info(method: "get_3d_conformer", cid: "CID")
   → 3D coordinates of bound ligand for docking comparison

4. mcp__pubchem__pubchem_info(method: "search_by_substructure", smiles: "CORE_SCAFFOLD_SMILES")
   → Find compounds sharing the same core scaffold
```

### Binding Pocket Properties

```
Characterize pocket by:
- Volume (Å³): < 300 = tight, 300–800 = medium, > 800 = large/allosteric
- Hydrophobicity: fraction of non-polar residues lining pocket
- Flexibility: B-factor distribution of pocket residues
- Solvent exposure: buried vs surface-accessible
- Druggability score: combination of above factors

Cross-reference with known ligand properties:
- mcp__pubchem__pubchem_info(method: "get_compound_properties", cid: "CID")
  → Molecular weight, logP, PSA of known binders → infer pocket preferences
```

---

## Structure Profile Report Template

```
═══════════════════════════════════════════════════
STRUCTURE PROFILE REPORT: [PROTEIN NAME]
═══════════════════════════════════════════════════

TARGET IDENTIFICATION
  Gene Symbol: [SYMBOL]
  UniProt ID: [ACCESSION]
  Ensembl ID: [ENSG00000xxxxx]
  Protein Class: [e.g., Kinase, GPCR, Ion channel]

───────────────────────────────────────────────────
EXPERIMENTAL STRUCTURES
───────────────────────────────────────────────────

  PDB ID    Method          Res (Å)  Tier  Ligand        Chains  Year
  ──────    ──────          ───────  ────  ──────        ──────  ────
  [ID]      X-ray           [X.X]    T1    [LIGAND_ID]   [N]     [YYYY]
  [ID]      Cryo-EM         [X.X]    T2    Apo           [N]     [YYYY]
  [ID]      X-ray           [X.X]    T3    [LIGAND_ID]   [N]     [YYYY]

  Best structure for drug discovery: [PDB_ID] — [rationale]
  Best structure for modeling: [PDB_ID] — [rationale]

───────────────────────────────────────────────────
QUALITY METRICS (Best Structure)
───────────────────────────────────────────────────

  Resolution:           [X.X] Å
  R-work / R-free:      [X.XX] / [X.XX]
  Clashscore:           [X]
  Ramachandran favored: [XX.X]%
  Missing residues:     [ranges]
  Quality Tier:         [T1/T2/T3/T4]

───────────────────────────────────────────────────
ALPHAFOLD PREDICTION
───────────────────────────────────────────────────

  AlphaFold DB:         [URL]
  Mean pLDDT:           [XX.X]
  High-confidence (>90): [residue ranges]
  Low-confidence (<50):  [residue ranges — likely disordered]

───────────────────────────────────────────────────
LIGAND ANALYSIS
───────────────────────────────────────────────────

  Co-crystallized ligands:
  Ligand ID   PDB     Name            MW      Activity
  ─────────   ───     ────            ──      ────────
  [HET_CODE]  [PDB]   [compound]      [X.X]   IC50=[X] nM
  [HET_CODE]  [PDB]   [compound]      [X.X]   Ki=[X] nM

  Binding pocket residues: [list key residues]
  Pocket volume:           [X] Å³
  Key interactions:        [H-bonds, hydrophobic, etc.]

───────────────────────────────────────────────────
CROSS-DATABASE REFERENCES
───────────────────────────────────────────────────

  PDB:          https://www.rcsb.org/structure/[ID]
  UniProt:      https://www.uniprot.org/uniprot/[ACC]
  AlphaFold:    https://alphafold.ebi.ac.uk/entry/[ACC]
  Open Targets: https://platform.opentargets.org/target/[ENSG]
  ChEMBL:       https://www.ebi.ac.uk/chembl/target_report_card/[CHEMBL_ID]

───────────────────────────────────────────────────
RECOMMENDATION
───────────────────────────────────────────────────

  Use case: [stated use case]
  Recommended structure: [PDB_ID or AlphaFold]
  Rationale: [resolution, ligand, coverage, confidence]
  Caveats: [missing regions, crystal contacts, prediction uncertainty]

═══════════════════════════════════════════════════
```

---

## Evidence Grading

| Grade | Source | Confidence |
|-------|--------|-----------|
| **T1** | Experimental structure, resolution < 1.5 Å, R-free < 0.22 | Atomic-level detail, highest confidence |
| **T2** | Experimental structure, resolution 1.5–2.0 Å, acceptable metrics | Reliable for drug design and docking |
| **T3** | Experimental structure > 2.0 Å, or AlphaFold pLDDT > 70 | Useful for modeling, cautious interpretation |
| **T4** | Low-resolution structure > 3.0 Å, AlphaFold pLDDT < 70, or homology model | Topology/fold level only, not suitable for atomic analysis |

---

## Multi-Agent Workflow Examples

**"Retrieve structural data for EGFR for drug design"**
1. Protein Structure Retrieval → PDB structures with quality tiers, ligand-bound entries, binding pocket analysis
2. Drug Target Analyst → Bioactivity data for co-crystallized compounds, SAR from structural series
3. Binder Discovery Specialist → Design new binders using best structural template

**"Find the best template for homology modeling of a novel kinase"**
1. Protein Structure Retrieval → Systematic retrieval of family member structures, template ranking by coverage and resolution
2. Protein Interactions → Interaction interfaces that must be preserved in the model
3. Target Research → Functional annotation to guide model validation

**"Compare binding modes of approved drugs at the same target"**
1. Protein Structure Retrieval → All ligand-bound structures, binding pocket comparison, conformation analysis
2. Drug Target Analyst → Mechanism of action and selectivity profiles for each drug
3. Antibody Engineering → If biologics target the same site, structural basis of epitope overlap

**"Assess structural coverage for antibody target validation"**
1. Protein Structure Retrieval → Experimental structures of target extracellular domain, AlphaFold confidence for unresolved regions
2. Antibody Engineering → Epitope mapping onto available structures
3. Protein Interactions → PPI interface structures relevant to antibody blocking

**"Evaluate AlphaFold prediction reliability for an understudied protein"**
1. Protein Structure Retrieval → AlphaFold pLDDT mapping via `mcp__alphafold__alphafold_data(method: "analyze_confidence_regions")`, comparison with PDB via `mcp__pdb__pdb_data(method: "search_by_uniprot")`, disorder prediction
2. Target Research → Functional domains and known motifs to anchor confidence assessment
3. Drug Target Analyst → Druggability assessment considering structural uncertainty

## Completeness Checklist

- [ ] Protein identity confirmed and mapped to UniProt accession and Ensembl ID
- [ ] All PDB experimental structures retrieved and listed with resolution and method
- [ ] Quality tier (T1-T4) assigned to each structure based on resolution and validation metrics
- [ ] AlphaFold prediction checked and pLDDT confidence regions mapped
- [ ] Best structure recommended for the stated use case with rationale
- [ ] Ligand analysis completed for drug discovery use cases (co-crystallized compounds, binding pocket)
- [ ] Cross-database references provided (PDB, UniProt, AlphaFold, Open Targets, ChEMBL)
- [ ] Structure Profile Report template populated with all sections
- [ ] Report file finalized with no `[Analyzing...]` placeholders remaining
