---
name: binder-discovery-specialist
description: Complete drug discovery cascade from target validation through known ligand mining, compound expansion, ADMET filtering, to docking prioritization. Identifies, filters, and prioritizes novel drug-like compounds against validated targets. Use when user mentions binder discovery, hit finding, lead identification, compound screening, ligand mining, scaffold hopping, similarity search, ADMET filtering, docking prioritization, hit-to-lead, lead optimization, drug-like compounds, compound expansion, virtual screening, compound prioritization, or druggable compound search.
---

# Binder Discovery Specialist

> **Boltz-2 recipes**: See [boltz-recipes.md](boltz-recipes.md) for structure-based virtual screening, hit-to-lead affinity ranking, scaffold hopping validation, and ADMET-filtered docking via Boltz-2.

Complete drug discovery cascade from target validation through known ligand mining, compound expansion, ADMET filtering, to docking prioritization. Uses Open Targets for target validation and druggability, ChEMBL for bioactivity and SAR data, DrugBank for drug-target pharmacology, PubChem for compound expansion and similarity searches, PubMed for literature evidence, and FDA for regulatory context on approved compounds.

## Report-First Workflow

1. **Create report file immediately**: `[target]_binder_discovery_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Deep target validation and druggability scoring -> use `drug-target-analyst` or `drug-target-validator`
- Repurposing approved drugs for new indications -> use `drug-repurposing-analyst`
- Toxicity profiling and structural alert analysis -> use `chemical-safety-toxicology`
- Polypharmacology and pathway-level target interactions -> use `network-pharmacologist`
- Medicinal chemistry optimization and lead-to-candidate progression -> use `medicinal-chemistry`
- Antibody or biologic binder discovery -> use `antibody-engineering`

## Cross-Reference: Other Skills

- **Deep target validation and druggability assessment** -> use drug-target-analyst skill
- **Target-disease association evidence scoring** -> use drug-target-validator skill
- **Repurposing approved drugs for new indications** -> use drug-repurposing-analyst skill
- **Toxicity profiling and structural alert analysis** -> use chemical-safety-toxicology skill
- **Polypharmacology and pathway-level target interactions** -> use network-pharmacologist skill

## Available MCP Tools

### `mcp__opentargets__opentargets_info` (Target Validation & Druggability)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `search_diseases` | Search diseases by name/synonym | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId` (Ensembl ID), `diseaseId` (EFO ID), `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes) | `id` (EFO ID) |

### `mcp__chembl__chembl_info` (Bioactivity, SAR & ADMET)

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

### `mcp__pubchem__pubchem_info` (Compound Expansion & Chemical Intelligence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_compounds` | Search compounds by name, SMILES, or InChI | `query`, `search_type`, `limit` |
| `get_compound_info` | Full compound profile (structure, properties, identifiers) | `cid` |
| `search_similar_compounds` | Tanimoto similarity search for scaffold hopping | `smiles` or `cid`, `threshold`, `limit` |
| `get_safety_data` | GHS hazard, toxicity, and safety information | `cid` |
| `get_patent_ids` | Patent coverage for a compound | `cid` |
| `get_compound_properties` | Physicochemical properties (MW, LogP, TPSA, HBD, HBA) | `cid` |
| `get_compound_synonyms` | Alternative names and identifiers | `cid` |
| `search_by_formula` | Find compounds by molecular formula | `formula`, `limit` |
| `search_by_substructure` | Substructure search for core scaffold mining | `smiles`, `limit` |
| `get_compound_assays` | Bioassay results linked to compound | `cid`, `limit` |
| `get_compound_targets` | Known biological targets for a compound | `cid` |
| `get_compound_classification` | Pharmacological and chemical classification | `cid` |

### `mcp__uniprot__uniprot_data` (Protein Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_protein_info` | Full protein profile | `accession`, `format` |
| `search_by_gene` | Find proteins by gene name | `gene`, `organism`, `size` |
| `get_protein_features` | Protein features (domains, sites, PTMs) | `accession` |
| `get_protein_structure` | Structural data (PDB, AlphaFold) | `accession` |
| `get_protein_domains_detailed` | Detailed domain architecture | `accession` |
| `get_protein_sequence` | Get protein sequence (FASTA/JSON) | `accession`, `format` |

### `mcp__pubmed__pubmed_articles` (Literature Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__fda__fda_info` (Regulatory & Approved Drug Context)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search FDA-approved drugs | `query`, `limit` |
| `get_drug_label` | Full prescribing information / drug label | `application_number` or `drug_name` |
| `search_adverse_events` | Post-market adverse event reports | `drug_name`, `reaction`, `limit` |
| `get_approval_history` | NDA/BLA approval timeline | `application_number` |
| `search_recalls` | Drug recall and safety alerts | `query`, `limit` |
| `search_shortages` | Drug shortage reports | `query` |
| `get_orange_book` | Patent and exclusivity data | `drug_name` or `ingredient` |
| `search_clinical_trials` | FDA-linked clinical trial entries | `query`, `limit` |

### `mcp__alphafold__alphafold_data` (AlphaFold Predicted Structures)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_structure` | Get AlphaFold predicted structure for binding site analysis | `uniprotId`, `format` (json/pdb/cif) |
| `check_availability` | Check if prediction exists | `uniprotId` |
| `get_confidence_scores` | Get pLDDT scores for binding pocket confidence | `uniprotId` |
| `analyze_confidence_regions` | Identify high/low confidence regions near binding sites | `uniprotId` |

### `mcp__pdb__pdb_data` (Experimental Structures from PDB)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_structures` | Search for ligand-bound experimental structures | `query`, `limit`, `experimental_method`, `resolution_range`, `sort_by` |
| `get_structure_info` | Get structure details (ligands, chains, resolution) | `pdb_id`, `format` |
| `download_structure` | Download structure file for docking | `pdb_id`, `format` |
| `search_by_uniprot` | Find PDB structures for UniProt ID | `uniprot_id`, `limit` |
| `get_structure_quality` | Resolution, R-factor, validation | `pdb_id` |

### `mcp__bindingdb__bindingdb_data` (BindingDB — Core Binding Affinity Data)

| Tool | Method | Use |
|------|--------|-----|
| `mcp__bindingdb__bindingdb_data` | `get_ligands_by_target` | Find all known binders for a target by UniProt ID with affinity data |
| | `search_by_name` | Search compounds by name for binding data |
| | `search_by_smiles` | Structure similarity search — find analogs of a hit compound |
| | `get_target_info` | Target protein info from BindingDB |
| | `get_ligand_info` | Detailed ligand/compound info |
| | `search_by_target_name` | Find binders by target name |
| | `get_ki_by_target` | Ki values specifically for a target |

---

## 7-Phase Drug Discovery Cascade

### Phase 1: Tool Parameter Verification

Before starting, verify that MCP tools are responsive and parameters are accepted correctly.

```
1. mcp__opentargets__opentargets_info(method: "search_targets", query: "TEST_GENE", size: 1)
   -> Confirm Open Targets connectivity and response format

2. mcp__chembl__chembl_info(method: "target_search", query: "TEST_TARGET", limit: 1)
   -> Confirm ChEMBL connectivity

3. mcp__pubchem__pubchem_info(method: "search_compounds", query: "aspirin", search_type: "name", limit: 1)
   -> Confirm PubChem connectivity

If any tool returns an error, report the failure before proceeding.
```

### Phase 2: Target Validation & Druggability Assessment

```
1. mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL", size: 5)
   -> Get Ensembl gene ID and confirm target identity

2. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Full target profile: function, subcellular location, tractability assessment, protein class

3. mcp__opentargets__opentargets_info(method: "search_diseases", query: "DISEASE_NAME", size: 5)
   -> Get EFO disease ID for association scoring

4. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx", minScore: 0.3, size: 20)
   -> Evidence score breakdown: genetic, somatic, literature, known drugs, animal models

5. mcp__chembl__chembl_info(method: "target_search", query: "TARGET_NAME", limit: 5)
   -> Get ChEMBL target ID and target classification

6. mcp__drugbank__drugbank_info(method: "search_by_target", target: "TARGET_NAME", limit: 20)
   -> Existing approved drugs and investigational compounds for this target

7. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL druggability target validation", num_results: 10)
   -> Recent target validation publications

8. mcp__uniprot__uniprot_data(method: "search_by_gene", gene: "GENE_SYMBOL", organism: "human", size: 5)
   -> Get UniProt accession for structural and domain lookups

9. mcp__uniprot__uniprot_data(method: "get_protein_features", accession: "UNIPROT_ACC")
   -> Binding sites, active site residues, and domain features for binder design

10. mcp__pdb__pdb_data(method: "search_by_uniprot", uniprot_id: "UNIPROT_ACC", limit: 10)
    -> Available experimental structures for docking

11. mcp__alphafold__alphafold_data(method: "get_confidence_scores", uniprotId: "UNIPROT_ACC")
    -> pLDDT scores to assess binding site confidence in AlphaFold model

DECISION GATE: Proceed only if target has tractability evidence AND association score > 0.3.
Report druggability classification: small molecule, antibody, other modality, or undruggable.
```

### Phase 3: Known Ligand Mining with SAR

```
1. mcp__chembl__chembl_info(method: "get_bioactivity", target_id: "CHEMBL_TARGET_ID", limit: 100)
   -> All reported bioactivity data: IC50, Ki, EC50, Kd values

2. Group compounds by activity tiers:
   - Tier A: IC50/Ki < 100 nM (potent leads)
   - Tier B: 100 nM - 1 uM (active hits)
   - Tier C: 1 uM - 10 uM (weak hits)
   - Discard: > 10 uM

3. For each Tier A/B compound:
   mcp__chembl__chembl_info(method: "compound_search", query: "COMPOUND_NAME_OR_ID")
   -> Get full compound profile and SMILES

4. mcp__chembl__chembl_info(method: "get_mechanism", chembl_id: "CHEMBLxxxxx")
   -> Mechanism of action (inhibitor, agonist, antagonist, allosteric modulator)

5. mcp__drugbank__drugbank_info(method: "search_by_name", query: "COMPOUND_NAME")
   -> Check if any known ligands are approved drugs

6. mcp__pubchem__pubchem_info(method: "get_compound_targets", cid: "CID_NUMBER")
   -> Selectivity profile: what other targets does this compound hit?

7. Identify SAR trends:
   - Common scaffolds among Tier A compounds
   - Activity cliffs (structurally similar but large potency differences)
   - Key pharmacophore features

DECISION GATE: At least 3 confirmed ligands with IC50 < 1 uM required to proceed to expansion.
If fewer, flag as "limited chemical matter" and recommend de novo design approaches.
```

### Phase 4: Structure Analysis & Chemical Characterization

```
1. For top hits from Phase 3:
   mcp__pubchem__pubchem_info(method: "get_compound_properties", cid: "CID_NUMBER")
   -> MW, LogP, TPSA, HBD, HBA, rotatable bonds, ring count

2. mcp__pubchem__pubchem_info(method: "get_compound_classification", cid: "CID_NUMBER")
   -> Pharmacological class, chemical taxonomy

3. mcp__chembl__chembl_info(method: "get_admet", chembl_id: "CHEMBLxxxxx")
   -> Drug-likeness flags, Lipinski violations, predicted ADMET

4. mcp__pubchem__pubchem_info(method: "get_compound_synonyms", cid: "CID_NUMBER")
   -> Alternative names, registry numbers, cross-references

5. mcp__drugbank__drugbank_info(method: "get_external_identifiers", drugbank_id: "DBxxxxx")
   -> Cross-database mapping: PubChem CID, ChEMBL ID, KEGG, UniProt

6. mcp__uniprot__uniprot_data(method: "get_protein_domains_detailed", accession: "UNIPROT_ACC")
   -> Target domain architecture for binding site context and selectivity analysis

7. mcp__uniprot__uniprot_data(method: "get_protein_sequence", accession: "UNIPROT_ACC")
   -> Canonical sequence for structural modeling and docking preparation

8. Assess Lipinski/Veber compliance for each compound (see framework below)

OUTPUT: Characterized ligand set with structures, potency, and physicochemical profiles.
```

### Phase 5: Compound Expansion (Similarity Search & Scaffold Hopping)

```
1. For each Tier A reference compound:
   mcp__pubchem__pubchem_info(method: "search_similar_compounds", smiles: "REFERENCE_SMILES", threshold: 0.7, limit: 50)
   -> Tanimoto similarity neighbors (threshold 0.7 for close analogs)

2. Broader scaffold hopping:
   mcp__pubchem__pubchem_info(method: "search_similar_compounds", smiles: "REFERENCE_SMILES", threshold: 0.5, limit: 100)
   -> More diverse analogs for scaffold hopping (threshold 0.5)

3. mcp__pubchem__pubchem_info(method: "search_by_substructure", smiles: "CORE_SCAFFOLD_SMILES", limit: 100)
   -> All compounds containing the active scaffold

4. mcp__drugbank__drugbank_info(method: "search_by_structure", smiles: "REFERENCE_SMILES", limit: 20)
   -> Structurally similar approved drugs (repurposing candidates)

5. mcp__drugbank__drugbank_info(method: "get_similar_drugs", drugbank_id: "DBxxxxx", limit: 20)
   -> Pharmacologically similar drugs (mechanism-based expansion)

6. For novel hits from expansion:
   mcp__pubchem__pubchem_info(method: "get_compound_assays", cid: "CID_NUMBER", limit: 20)
   -> Check if expanded compounds have existing bioassay data

7. mcp__pubchem__pubchem_info(method: "get_patent_ids", cid: "CID_NUMBER")
   -> Patent freedom-to-operate check

8. Deduplicate and merge expanded compound set with known ligands.

OUTPUT: Expanded compound library (typically 50-200 compounds) with source annotations.
```

### Phase 6: Sequential ADMET Filtering Cascade

Apply filters sequentially. Each gate eliminates compounds before the next gate is evaluated.

```
GATE 1 — Physicochemical Properties (Lipinski/Veber):
   For each compound:
   mcp__pubchem__pubchem_info(method: "get_compound_properties", cid: "CID_NUMBER")
   -> Apply: MW <= 500, LogP <= 5, HBD <= 5, HBA <= 10, TPSA <= 140, RotBonds <= 10
   -> Allow max 1 Lipinski violation
   -> PASS/FAIL each compound

GATE 2 — Bioavailability & Drug-Likeness:
   For passing compounds:
   mcp__chembl__chembl_info(method: "get_admet", chembl_id: "CHEMBLxxxxx")
   -> Check: oral bioavailability prediction, Caco-2 permeability, plasma protein binding
   -> Flag compounds with predicted poor absorption or high clearance

GATE 3 — Toxicity Screening:
   For passing compounds:
   mcp__pubchem__pubchem_info(method: "get_safety_data", cid: "CID_NUMBER")
   -> GHS hazard classification, LD50, mutagenicity flags
   mcp__fda__fda_info(method: "search_adverse_events", drug_name: "COMPOUND_NAME", limit: 10)
   -> Post-market safety signals for known drugs in the set

GATE 4 — Structural Alerts:
   Flag compounds containing known toxicophores:
   - Reactive metabolites (epoxides, quinones, acyl halides)
   - PAINS (pan-assay interference compounds)
   - Genotoxic alerts (aromatic amines, nitro groups, alkylating agents)
   -> Remove flagged compounds unless justified by therapeutic context

OUTPUT: Filtered compound set with ADMET pass/fail annotations and survival rate per gate.
```

### Phase 7: Prioritization & Ranking

```
1. Score each surviving compound using the Weighted Prioritization Score (see framework below)

2. mcp__fda__fda_info(method: "search_drugs", query: "TARGET_NAME", limit: 20)
   -> Regulatory precedent: are similar compounds approved?

3. mcp__fda__fda_info(method: "get_orange_book", ingredient: "COMPOUND_NAME")
   -> Patent landscape and exclusivity windows

4. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "COMPOUND_NAME TARGET_NAME", num_results: 10)
   -> Published efficacy data to support ranking

5. Rank compounds by:
   - Weighted Prioritization Score (primary)
   - Evidence Tier (secondary)
   - Patent freedom (tertiary)

6. Generate final ranked list with:
   - Top 10 compounds with full profiles
   - Recommended next steps (synthesis, in vitro validation, co-crystal structure)
   - Risk assessment for each compound

OUTPUT: Prioritized compound shortlist with scores, evidence tiers, and actionable recommendations.
```

### BindingDB Binder Landscape Analysis

```
1. Query all known binders for the target:
   mcp__bindingdb__bindingdb_data(method="get_ligands_by_target", uniprot_id="P00519", affinity_type="IC50", affinity_cutoff=1000)
   -> Retrieve all compounds with IC50 < 1000 nM from BindingDB for the target

2. Find analogs of best binders via SMILES similarity search:
   mcp__bindingdb__bindingdb_data(method="search_by_smiles", smiles="BEST_BINDER_SMILES")
   -> Structure similarity search to expand hit series with BindingDB analogs

3. Get Ki values for selectivity assessment:
   mcp__bindingdb__bindingdb_data(method="get_ki_by_target", uniprot_id="P00519")
   -> Ki-specific data for selectivity profiling across related targets

Use BindingDB data to complement ChEMBL bioactivity mining — BindingDB often contains
binding affinity measurements not present in ChEMBL, especially from academic sources.
Cross-reference hits from both databases to build the most complete binder landscape.
```

---

## Weighted Prioritization Score

Each compound receives a composite score from 0 to 100:

| Component | Weight | Scoring Criteria |
|-----------|--------|-----------------|
| **Bioactivity** | 40% | IC50 < 10 nM = 100, < 100 nM = 80, < 1 uM = 60, < 10 uM = 30, > 10 uM = 0 |
| **ADMET** | 30% | All 4 gates passed = 100, 3 gates = 75, 2 gates = 40, 1 gate = 10, 0 gates = 0 |
| **Similarity to known actives** | 20% | Tanimoto > 0.85 = 100, > 0.7 = 70, > 0.5 = 40, < 0.5 = 10 |
| **Novelty** | 10% | No patents = 100, expired patents = 80, active patents = 20, approved drug = 0 |

```
Prioritization Score = (Bioactivity_score * 0.40) + (ADMET_score * 0.30) + (Similarity_score * 0.20) + (Novelty_score * 0.10)
```

**Interpretation:**
- Score 80-100: Priority 1 — immediate follow-up (synthesis, in vitro confirmation)
- Score 60-79: Priority 2 — strong candidate, optimize ADMET or potency
- Score 40-59: Priority 3 — backup series, needs medicinal chemistry optimization
- Score < 40: Deprioritize unless unique scaffold or mechanism

---

## Evidence Tiers

| Tier | Definition | Example | Confidence |
|------|-----------|---------|------------|
| **T0** | Approved drug for the target | FDA-approved with this MOA | Highest |
| **T1** | Clinical candidate | Phase I-III with published efficacy data | High |
| **T2** | Validated hit (IC50 < 1 uM) | ChEMBL bioactivity with dose-response confirmation | Moderate-High |
| **T3** | Screening hit | Single-point activity in HTS, no dose-response | Moderate |
| **T4** | Computational prediction | Docking score, pharmacophore match, QSAR prediction | Low-Moderate |
| **T5** | De novo design | AI-generated or computationally designed, no experimental data | Low |

**Usage:** Always report evidence tier alongside prioritization score. A T2 compound scoring 70 is more credible than a T4 compound scoring 85.

---

## ADMET Filtering Cascade

### Gate 1: Physicochemical Properties

**Lipinski Rule of Five:**

| Property | Threshold | Rationale |
|----------|----------|-----------|
| Molecular Weight | <= 500 Da | Oral absorption decreases above 500 |
| LogP | <= 5 | High lipophilicity reduces solubility and increases toxicity risk |
| H-bond Donors | <= 5 | Excess donors reduce membrane permeability |
| H-bond Acceptors | <= 10 | Excess acceptors reduce membrane permeability |

**Veber Rules (oral bioavailability):**

| Property | Threshold | Rationale |
|----------|----------|-----------|
| TPSA | <= 140 A^2 | Topological polar surface area predicts intestinal absorption |
| Rotatable Bonds | <= 10 | Molecular flexibility affects oral bioavailability |

**Interpretation:** Allow up to 1 Lipinski violation. Natural products and antibiotics frequently violate but may still be viable. Flag but do not auto-reject compounds with 2 violations if they belong to known drug-like chemotypes.

### Gate 2: Bioavailability Prediction

```
Pass criteria:
- Predicted Caco-2 permeability > 1 x 10^-6 cm/s
- Predicted oral bioavailability > 20%
- Plasma protein binding < 99% (sufficient free fraction)
- Predicted aqueous solubility > 10 ug/mL
```

### Gate 3: Toxicity Flags

```
Reject if:
- hERG IC50 < 10 uM (cardiac liability)
- Ames positive (mutagenicity)
- LD50 < 50 mg/kg (acute toxicity)
- Hepatotoxicity signals in FDA adverse event data
- Known reactive metabolite formation
```

### Gate 4: Structural Alerts

```
PAINS filters (pan-assay interference):
- Rhodanines, enones, quinones, catechols
- Frequent hitters in multiple unrelated assays

Toxicophore alerts:
- Aromatic nitro groups (mutagenicity)
- Anilines / aromatic amines (carcinogenicity)
- Alkyl halides (DNA alkylation)
- Michael acceptors (protein reactivity)
- Epoxides (reactive intermediates)

Context-dependent exceptions:
- Covalent inhibitors (Michael acceptors acceptable if designed intentionally)
- Prodrugs (structural alerts may be part of activation mechanism)
```

---

## SAR Analysis Framework

### Activity Cliff Analysis

Activity cliffs are pairs of structurally similar compounds with large differences in potency.

```
1. Identify compound pairs with Tanimoto similarity > 0.85
2. Calculate potency difference: |pIC50_A - pIC50_B|
3. Activity cliff if similarity > 0.85 AND potency difference > 2 log units (100-fold)

Interpretation:
- Activity cliffs reveal critical pharmacophore features
- Small structural change causing large potency loss = essential binding interaction
- Small structural change causing large potency gain = optimization opportunity
```

### Matched Molecular Pair (MMP) Analysis

```
1. Identify compound pairs differing by a single structural transformation
   (e.g., H -> F, CH3 -> CF3, phenyl -> pyridyl)
2. Track potency and ADMET changes for each transformation
3. Build transformation rules:
   - "H -> F at R2 position: +10x potency, no ADMET penalty"
   - "Phenyl -> pyridyl at R1: -5x potency, improved solubility"

Use for:
- Guiding medicinal chemistry optimization
- Predicting activity of untested analogs
- Identifying metabolic soft spots
```

### Scaffold Analysis

```
1. Extract Murcko scaffolds from all active compounds
2. Group compounds by scaffold
3. For each scaffold:
   - Count number of active analogs
   - Range of potency within scaffold series
   - Best ADMET profile within series
   - Patent coverage

Scaffold prioritization:
- Multiple potent analogs = robust SAR, reliable scaffold
- Single potent compound = activity cliff risk, less reliable
- Novel scaffold with moderate potency = IP opportunity
```

---

## Hit-to-Lead Criteria

A validated hit must meet ALL of the following to advance to lead status:

| Criterion | Threshold | Assessment Method |
|-----------|----------|-------------------|
| **Potency** | IC50/Ki < 1 uM (target), ideally < 100 nM | ChEMBL bioactivity, dose-response confirmed |
| **Selectivity** | > 30x vs closest off-target | ChEMBL cross-screening data |
| **Drug-likeness** | <= 1 Lipinski violation | PubChem properties, ChEMBL ADMET |
| **Solubility** | > 10 ug/mL aqueous | Predicted or measured |
| **Permeability** | Caco-2 > 1 x 10^-6 cm/s | Predicted or measured |
| **Metabolic stability** | t1/2 > 30 min (microsomal) | Predicted or literature |
| **No structural alerts** | Pass PAINS and toxicophore filters | Structural alert screening |
| **Chemical tractability** | Synthetic route feasible in <= 5 steps | Retrosynthetic analysis |
| **IP position** | Freedom to operate or novel scaffold | PubChem patents, Orange Book |

```
Lead classification:
- Meets ALL criteria -> LEAD: ready for optimization
- Meets potency + selectivity, fails 1-2 ADMET -> LEAD-LIKE: optimize ADMET
- Meets potency, fails selectivity or multiple ADMET -> HIT: needs significant optimization
- Fails potency -> INACTIVE: deprioritize
```

---

## Multi-Agent Workflow Examples

**"Find novel binders for KRAS G12C"**
1. Binder Discovery Specialist -> 7-phase cascade: validate KRAS G12C, mine known covalent inhibitors (sotorasib, adagrasib analogs), expand via similarity search, ADMET filter, prioritize novel scaffolds
2. Drug Target Analyst -> Deep SAR analysis of covalent binding mechanism, selectivity vs wild-type KRAS
3. Chemical Safety Toxicology -> Structural alert assessment for covalent warheads, off-target reactivity profiling
4. Network Pharmacologist -> KRAS pathway mapping, synthetic lethal combination opportunities

**"Identify drug-like inhibitors for a novel kinase target"**
1. Binder Discovery Specialist -> Full cascade from target validation through kinase-focused ligand mining, kinase selectivity panel analysis, ADMET filtering
2. Drug Target Validator -> Genetic evidence strength, target-disease causality assessment
3. Drug Repurposing Analyst -> Approved kinase inhibitors with cross-reactivity to this target
4. Network Pharmacologist -> Kinase signaling network, resistance pathway prediction

**"Expand hit series from HTS campaign"**
1. Binder Discovery Specialist -> Start at Phase 5 with HTS hits as reference compounds, similarity expansion, substructure search, ADMET cascade, prioritization
2. Chemical Safety Toxicology -> Toxicophore and PAINS flagging for HTS artifacts
3. Drug Target Analyst -> Confirm on-target mechanism for top expanded hits

**"Prioritize compounds for a validated but undrugged target"**
1. Binder Discovery Specialist -> Phase 2 druggability assessment, Phase 3 ligand mining (expect limited chemical matter), Phase 5 broader scaffold hopping with lower similarity thresholds, prioritize T4/T5 evidence tier compounds
2. Drug Target Validator -> Strengthen target validation with multi-source evidence
3. Drug Repurposing Analyst -> Screen approved drug libraries for weak but real activity against the target
4. Network Pharmacologist -> Identify druggable nodes upstream/downstream as alternative intervention points

**"Assess patent landscape and regulatory path for lead compound"**
1. Binder Discovery Specialist -> Phase 7 prioritization with patent and regulatory focus
2. Drug Repurposing Analyst -> Prior art and existing indications for the compound or close analogs
3. FDA data via fda_info -> Orange Book exclusivity, approval history for target class, adverse event landscape

## Completeness Checklist

- [ ] Report file created with all section headers and placeholders populated
- [ ] Target validated with druggability assessment (tractability, association score)
- [ ] Known ligands mined from ChEMBL and BindingDB with activity tiers assigned
- [ ] SAR trends identified (common scaffolds, activity cliffs, pharmacophore features)
- [ ] Compound expansion performed via similarity search and substructure mining
- [ ] All four ADMET gates applied sequentially with survival rates documented
- [ ] Weighted Prioritization Score calculated for each surviving compound
- [ ] Evidence tier assigned to every compound (T0-T5)
- [ ] Patent freedom-to-operate checked for top candidates
- [ ] Final ranked shortlist provided with actionable next steps
