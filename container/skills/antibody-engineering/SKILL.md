---
name: antibody-engineering
description: Antibody engineering and biologics development specialist. Guides antibody optimization from preclinical leads to clinical candidates. Covers humanization strategy, developability assessment, immunogenicity prediction, manufacturing feasibility (CMC), affinity maturation, Fc engineering, and antibody format selection. Use when user mentions antibody, biologics, humanization, CDR grafting, developability, immunogenicity, CMC, cell line development, antibody format, IgG subclass, Fc engineering, ADC, bispecific, affinity maturation, aggregation, PTM liability, or antibody manufacturing.
---

# Antibody Engineering

Biologics development specialist guiding antibody optimization from preclinical leads to clinical candidates. Covers humanization strategy, developability assessment, immunogenicity prediction, and manufacturing feasibility (CMC). Uses Open Targets for target biology, ChEMBL for bioactivity benchmarking, DrugBank for approved antibody intelligence, PubMed for literature, FDA for regulatory precedent, ClinicalTrials.gov for pipeline intelligence, and PubChem for chemical/conjugate data.

## Report-First Workflow

1. **Create report file immediately**: `[target]_antibody_engineering_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Target validation and druggability scoring -> use `drug-target-analyst` or `drug-target-validator`
- Biologic quality attributes, glycosylation profiling, and biosimilarity -> use `biologic-quality`
- Protein therapeutic design from scratch (non-antibody scaffolds) -> use `protein-therapeutic-design`
- Post-market safety signals for approved antibodies -> use `pharmacovigilance-specialist`
- FDA regulatory pathway for BLA or biosimilar submissions -> use `fda-consultant`
- Clinical trial design and competitive pipeline analysis -> use `clinical-trial-analyst`

## Cross-Reference: Other Skills

- **Target validation and druggability assessment** -> use drug-target-analyst skill
- **Multi-dimensional target validation scoring** -> use drug-target-validator skill
- **FDA regulatory pathway for biologics (BLA, biosimilar)** -> use fda-consultant skill
- **Clinical trial design and pipeline intelligence** -> use clinical-trial-analyst skill
- **Post-market safety signals for approved antibodies** -> use pharmacovigilance-specialist skill

## Available MCP Tools

### `mcp__opentargets__opentargets_info` (Target Biology & Disease Associations)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `search_diseases` | Search diseases by name/synonym | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId` (Ensembl ID), `diseaseId` (EFO ID), `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes) | `id` (EFO ID) |

### `mcp__chembl__chembl_info` (Bioactivity & Compound Benchmarking)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50, Kd) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |
| `get_admet` | ADMET/drug-likeness properties | `chembl_id` |

### `mcp__drugbank__drugbank_info` (Approved Antibody Intelligence)

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

### `mcp__pubmed__pubmed_articles` (Antibody Engineering Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__fda__fda_info` (Regulatory & Biosimilar Intelligence)

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

### `mcp__ctgov__ctgov_info` (Antibody Clinical Pipeline)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search clinical trials | `condition`, `intervention`, `phase`, `status`, `location`, `lead`, `ages`, `studyType`, `pageSize` |
| `get` | Get full trial details by NCT ID | `nctId` |
| `suggest` | Autocomplete terms | `input`, `dictionary` |
| `stats` | Trial statistics and counts | `condition`, `intervention` |

### `mcp__uniprot__uniprot_data` (Target Protein Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_protein_info` | Full protein profile | `accession`, `format` |
| `search_by_gene` | Find proteins by gene name | `gene`, `organism`, `size` |
| `get_protein_sequence` | Get protein sequence (FASTA/JSON) | `accession`, `format` |
| `get_protein_domains_detailed` | Detailed domain architecture | `accession` |
| `get_protein_features` | Protein features (domains, sites, PTMs) | `accession` |
| `get_protein_variants` | Known protein variants | `accession` |
| `get_external_references` | Cross-database references | `accession` |

### `mcp__pubchem__pubchem_info` (Chemical & Conjugate Data)

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
| `get_structure` | Get AlphaFold predicted structure for epitope analysis | `uniprotId`, `format` (json/pdb/cif) |
| `check_availability` | Check if prediction exists | `uniprotId` |
| `get_confidence_scores` | Get pLDDT scores for epitope region confidence | `uniprotId` |
| `analyze_confidence_regions` | Identify high/low confidence regions on target surface | `uniprotId` |

### `mcp__pdb__pdb_data` (Experimental Structures from PDB)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_structures` | Search for antibody-antigen complex structures | `query`, `limit`, `experimental_method`, `resolution_range`, `sort_by` |
| `get_structure_info` | Get structure details (chains, resolution, ligands) | `pdb_id`, `format` |
| `search_by_uniprot` | Find PDB structures for target antigen | `uniprot_id`, `limit` |
| `get_structure_quality` | Resolution, R-factor, validation metrics | `pdb_id` |

---

## 8-Phase Antibody Development Pipeline

### Phase 1: Input Analysis — Target & Lead Characterization

Characterize the target antigen and assess the starting antibody lead.

```
1. mcp__opentargets__opentargets_info(method: "search_targets", query: "TARGET_GENE", size: 10)
   -> Get Ensembl ID, verify target identity, note isoforms

2. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Target biology: subcellular location, membrane topology, domain architecture, glycosylation sites

3. mcp__drugbank__drugbank_info(method: "search_by_target", target: "target_name", limit: 20)
   -> Existing antibodies and biologics against this target

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "TARGET_NAME antibody epitope binding domain structure", num_results: 15)
   -> Published structural and epitope mapping data

5. mcp__chembl__chembl_info(method: "target_search", query: "target_name", limit: 10)
   -> ChEMBL target classification, existing bioactivity data

6. mcp__uniprot__uniprot_data(method: "search_by_gene", gene: "TARGET_GENE", organism: "human", size: 5)
   -> Get UniProt accession for target antigen

7. mcp__uniprot__uniprot_data(method: "get_protein_domains_detailed", accession: "UNIPROT_ACC")
   -> Domain architecture: extracellular domains, transmembrane topology, epitope-accessible regions

8. mcp__uniprot__uniprot_data(method: "get_protein_variants", accession: "UNIPROT_ACC")
   -> Known variants that may affect epitope binding or antigen expression
```

**Input Characterization Checklist:**

| Parameter | Required Information |
|-----------|---------------------|
| **Species of origin** | Mouse, rabbit, llama, phage display, transgenic mouse |
| **Antibody format** | Full IgG, scFv, Fab, VHH/nanobody |
| **Sequence availability** | VH/VL sequences, CDR definitions (Kabat, IMGT, Chothia) |
| **Binding data** | Kd, kon, koff, epitope bin/competition data |
| **Functional data** | Neutralization, ADCC, CDC, internalization, agonism/antagonism |
| **Target biology** | Soluble vs membrane-bound, expression level, shedding |

### Phase 2: Humanization Strategy

Select optimal humanization approach based on lead characteristics.

```
1. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "antibody humanization germline CDR grafting framework", num_results: 15)
   -> Current humanization methodology literature

2. mcp__drugbank__drugbank_info(method: "search_by_category", category: "monoclonal antibodies", limit: 30)
   -> Approved humanized antibodies as references for framework selection

3. mcp__fda__fda_info(method: "search_purple_book", drug_name: "reference_antibody")
   -> Regulatory status of comparable humanized antibodies
```

**Humanization Scoring Framework:**

| Metric | Calculation | Target |
|--------|------------|--------|
| **Framework retention** | % parental framework residues kept | > 85% for CDR grafting |
| **Germline identity (VH)** | % identity to closest human VH germline | > 80% (ideally > 85%) |
| **Germline identity (VL)** | % identity to closest human VL germline | > 80% (ideally > 85%) |
| **Vernier zone preservation** | Key residues supporting CDR conformation | All critical positions retained |
| **T-cell epitope count** | Predicted MHC II binding peptides | Minimize vs parental |

**Humanization Decision Tree:**

```
IF germline identity > 90%:
   -> Minimal humanization (point mutations in framework only)
   -> Retain all CDRs and Vernier zone residues

ELIF germline identity 75-90%:
   -> CDR grafting onto best-fit human germline
   -> Back-mutate Vernier zone positions if affinity loss > 3-fold
   -> Consider SDR (Specificity Determining Residue) transfer for difficult cases

ELIF germline identity < 75%:
   -> SDR transfer preferred (graft only antigen-contacting CDR residues)
   -> Or: Superhumanization (select human framework by structural fit, not sequence)
   -> Consider resurfacing as alternative (replace surface-exposed framework residues only)

IF source is camelid VHH:
   -> Framework adaptation to human VH3 germline
   -> Address hallmark residues at VH-VL interface (positions 37, 44, 45, 47)
```

**Germline Family Selection Guide:**

| Human VH Germline | Characteristics | Best For |
|-------------------|----------------|----------|
| **VH1-69** | Long HCDR3 accommodating, hydrophobic HCDR2 | Broadly neutralizing, influenza-like |
| **VH3-23** | Versatile, high stability, common in repertoire | General purpose, high developability |
| **VH3-30** | Good expression, stable framework | Default choice for many CDR grafts |
| **VH4-34** | Caveat: cold agglutinin association | Avoid unless necessary |
| **VH4-59** | Good stability, common therapeutic framework | Frequently used in approved mAbs |

### Phase 3: Structure Modeling & Affinity Assessment

Evaluate structural integrity of humanized variants and assess affinity retention.

```
1. mcp__pdb__pdb_data(method: "search_structures", query: "TARGET_NAME antibody", experimental_method: "X-RAY DIFFRACTION", resolution_range: "0-3.0", limit: 20)
   -> Search for antibody-antigen co-crystal structures

2. mcp__pdb__pdb_data(method: "search_by_uniprot", uniprot_id: "UNIPROT_ACC", limit: 15)
   -> All PDB structures of target antigen (including antibody complexes)

3. mcp__alphafold__alphafold_data(method: "get_structure", uniprotId: "UNIPROT_ACC", format: "pdb")
   -> AlphaFold predicted structure for epitope regions without experimental data

4. mcp__alphafold__alphafold_data(method: "analyze_confidence_regions", uniprotId: "UNIPROT_ACC")
   -> Identify high-confidence surface regions suitable for epitope targeting

5. mcp__chembl__chembl_info(method: "get_bioactivity", target_id: "CHEMBLxxxxx", limit: 50)
   -> Binding data for known antibodies/compounds against this target

6. mcp__uniprot__uniprot_data(method: "get_protein_sequence", accession: "UNIPROT_ACC")
   -> Canonical target sequence for epitope mapping and structural modeling

4. mcp__uniprot__uniprot_data(method: "get_protein_features", accession: "UNIPROT_ACC")
   -> Glycosylation sites, disulfide bonds, signal peptides — critical for antigen topology

5. mcp__pubchem__pubchem_info(method: "get_bioassay_results", cid: CID_NUMBER, limit: 50)
   -> Bioassay data for relevant biologics or ADC payloads
```

**Affinity Benchmarks for Therapeutic Antibodies:**

| Application | Target Kd Range | Rationale |
|-------------|----------------|-----------|
| **Soluble target neutralization** | < 1 nM | Must outcompete endogenous ligand |
| **Receptor blocking** | < 10 nM | Receptor occupancy at therapeutic dose |
| **ADCC/CDC effector function** | 1-100 nM | Affinity ceiling effect for FcgR engagement |
| **ADC (internalizing)** | 1-50 nM | Balance between binding and internalization rate |
| **Bispecific (bridging)** | 1-100 nM per arm | Avidity compensates for lower monovalent affinity |
| **Checkpoint inhibitor** | < 10 nM | High occupancy needed for efficacy |

### Phase 4: Affinity Optimization

Guide affinity maturation campaigns when humanized variants lose binding.

```
1. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "antibody affinity maturation CDR mutagenesis library design", num_results: 10)
   -> Published affinity maturation strategies

2. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "TARGET_NAME antibody affinity optimization", journal: "", start_date: "2020-01-01", num_results: 10)
   -> Recent optimization data for same target class
```

**Affinity Maturation Strategy Selection:**

| Approach | When to Use | Expected Improvement |
|----------|------------|---------------------|
| **Targeted CDR mutagenesis** | Known binding hotspots, crystal structure available | 5-50x Kd improvement |
| **Error-prone PCR library** | No structural data, broad exploration needed | 2-10x per round |
| **CDR walking** | Systematic single-position scanning | Identifies key positions for combinatorial library |
| **Light chain shuffling** | VH dominant binding, VL contributes minimally | 2-20x, improves developability simultaneously |
| **Computational design** | Structure available, specific contacts to optimize | 10-100x possible with validated models |

### Phase 5: Developability Assessment

Score the antibody candidate across six manufacturability dimensions.

```
1. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "antibody developability assessment aggregation viscosity PTM liability", num_results: 15)
   -> Current developability assessment literature and CQA frameworks

2. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   -> Formulation and manufacturing details of approved comparator antibodies

3. mcp__fda__fda_info(method: "lookup_drug", search_term: "comparator_antibody", search_type: "label", limit: 5)
   -> Label information including formulation, storage, concentration
```

**Developability Assessment Matrix (score 1-5 per dimension):**

| Dimension | Score 1 (High Risk) | Score 2 | Score 3 (Acceptable) | Score 4 | Score 5 (Low Risk) |
|-----------|--------------------|---------|--------------------|---------|-------------------|
| **Aggregation propensity** | > 5% HMW by SEC | 3-5% HMW | 1-3% HMW | 0.5-1% HMW | < 0.5% HMW |
| **PTM liability** | Multiple exposed Asp isomerization + Asn deamidation + Met oxidation in CDRs | 2+ liabilities in CDRs | 1 liability in CDR, manageable | Liabilities in framework only | No significant liabilities |
| **Thermal stability** | Tm onset < 55C | 55-60C | 60-65C | 65-70C | > 70C |
| **Expression yield** | < 0.5 g/L (CHO transient) | 0.5-1 g/L | 1-2 g/L | 2-4 g/L | > 4 g/L |
| **Solubility** | < 20 mg/mL | 20-50 mg/mL | 50-100 mg/mL | 100-150 mg/mL | > 150 mg/mL |
| **Viscosity** | > 30 cP at target conc | 20-30 cP | 15-20 cP | 10-15 cP | < 10 cP at 150 mg/mL |

**Total developability score: sum of 6 dimensions (range 6-30)**

| Total Score | Rating | Recommendation |
|-------------|--------|---------------|
| **25-30** | Excellent | Proceed to CMC development |
| **18-24** | Good | Proceed with monitoring of flagged dimensions |
| **12-17** | Moderate | Engineering required before CMC commitment |
| **6-11** | Poor | Consider backup candidates or significant re-engineering |

**Common PTM Liabilities in CDRs:**

| Modification | Sequence Motif | Risk | Mitigation |
|-------------|---------------|------|-----------|
| Asn deamidation | NG, NS, NT, NH | High — alters charge, reduces potency | Mutate Asn or flanking residue |
| Asp isomerization | DG, DS, DT | High — alters backbone conformation | Mutate Asp or flanking Gly |
| Met oxidation | Exposed Met | Moderate — reduces binding if in paratope | Replace with Leu or Ile |
| Trp oxidation | Solvent-exposed Trp | Moderate — potential aggregation seed | Shield or replace |
| N-linked glycosylation | NxS/T in CDR | High — heterogeneity, immunogenicity | Remove motif |
| Unpaired Cys | Free Cys in CDR | High — crosslinking, aggregation | Remove or pair |

### Phase 6: Immunogenicity Prediction

Assess risk of anti-drug antibody (ADA) responses.

```
1. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "antibody immunogenicity prediction anti-drug antibody ADA T-cell epitope", num_results: 15)
   -> Immunogenicity prediction methodology and clinical ADA rates

2. mcp__fda__fda_info(method: "lookup_drug", search_term: "comparator_antibody", search_type: "label", limit: 5)
   -> ADA rates reported in FDA-approved labels

3. mcp__ctgov__ctgov_info(method: "search", condition: "immunogenicity", intervention: "antibody_name", pageSize: 20)
   -> Clinical immunogenicity data from trials
```

**Immunogenicity Risk Assessment:**

| Risk Factor | Low Risk | Medium Risk | High Risk |
|------------|----------|-------------|-----------|
| **Humanization level** | Fully human (transgenic/phage) | Humanized (> 85% human) | Chimeric or < 80% human |
| **T-cell epitopes** | < 2 predicted strong binders | 2-5 predicted binders | > 5 predicted binders |
| **Route of administration** | IV (tolerogenic) | SC (moderate) | IM or intrathecal (higher risk) |
| **Dose and frequency** | Single dose or infrequent | Monthly | Weekly or more frequent |
| **Patient population** | Immunosuppressed (oncology) | Autoimmune (on combo immunosuppression) | Immunocompetent, chronic dosing |
| **ADA benchmark** | < 5% incidence (comparator class) | 5-15% incidence | > 15% incidence |

**Immunogenicity Mitigation Strategies:**

```
1. Deimmunization: Remove or modify predicted T-cell epitopes
   - MHC II binding prediction (NetMHCIIpan, IEDB)
   - Replace anchor residues while preserving binding
   - Validate: no affinity loss > 2-fold

2. Tolerization: Fc engineering for Treg engagement
   - IgG4 backbone (reduced effector function)
   - Glycoengineering for tolerogenic DC uptake

3. Formulation: Reduce aggregates (aggregates boost ADA)
   - Target < 1% HMW species
   - Optimize pH, surfactant, excipients

4. Clinical: Immunosuppression co-administration
   - Methotrexate co-dosing (established for anti-TNF class)
   - Induction dosing for tolerance
```

### Phase 7: Manufacturing Feasibility (CMC)

Assess producibility and establish CMC development timeline.

```
1. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   -> Manufacturing and formulation details of approved comparators

2. mcp__fda__fda_info(method: "lookup_drug", search_term: "antibody_name", search_type: "label", limit: 5)
   -> Approved formulation, concentration, storage conditions

3. mcp__fda__fda_info(method: "search_purple_book", drug_name: "reference_antibody")
   -> BLA approval status, biosimilar landscape

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "CHO cell line development antibody manufacturing titer upstream process", num_results: 10)
   -> Current manufacturing benchmarks and process innovations
```

**CMC Feasibility Assessment:**

| CMC Parameter | Feasible | Challenging | High Risk |
|--------------|----------|-------------|-----------|
| **Cell line titer** | > 3 g/L (stable CHO) | 1-3 g/L | < 1 g/L |
| **Purification yield** | > 70% (Protein A + polish) | 50-70% | < 50% |
| **Target concentration** | < 50 mg/mL (IV) | 50-150 mg/mL (SC) | > 150 mg/mL (SC high conc) |
| **Viscosity at target conc** | < 15 cP | 15-25 cP | > 25 cP |
| **Stability (2-8C)** | > 24 months | 12-24 months | < 12 months |
| **Freeze-thaw stability** | > 5 cycles | 3-5 cycles | < 3 cycles |

**CMC Development Timeline (IND-enabling):**

| Phase | Duration | Key Activities |
|-------|----------|---------------|
| **Cell line development** | 6-9 months | Transfection, selection, single-cell cloning, clone screening, stability assessment |
| **Upstream process development** | 3-6 months | Fed-batch optimization, media screening, scale-down model qualification |
| **Downstream process development** | 3-6 months | Protein A capture, polish steps (CEX/AEX/HIC), viral inactivation/filtration |
| **Formulation development** | 3-4 months | Buffer screening, excipient optimization, accelerated stability |
| **Analytical method development** | 4-6 months | Potency assay, SEC, cIEF, peptide mapping, glycan analysis, host cell protein |
| **GMP manufacturing** | 3-4 months | Engineering run, GMP production, release testing |
| **Total to IND** | ~18-24 months | From final sequence to IND-enabling GMP lot |

**Antibody Format Decision Tree:**

```
IF target requires effector function (ADCC/CDC):
   -> IgG1 (standard effector function)
   -> Consider afucosylation for enhanced ADCC (e.g., obinutuzumab model)

ELIF target requires blocking only (no effector function):
   -> IgG4 (S228P hinge stabilization mandatory)
   -> Or IgG1-LALA (L234A/L235A) for silenced effector function
   -> IgG1-LALA-PG (additional P329G) for complete silencing

ELIF half-life extension needed:
   -> IgG1 or IgG4 with YTE mutations (M252Y/S254T/T256E)
   -> Or LS mutations (M428L/N434S)
   -> Expected: 2-4x half-life extension

ELIF bispecific needed:
   -> Knob-into-hole (KiH) for heterodimerization
   -> CrossMAb for correct light chain pairing
   -> Or DVD-Ig, BiTE, DART depending on application
   -> Note: bispecific manufacturing complexity is significantly higher

ELIF ADC (antibody-drug conjugate):
   -> IgG1 preferred (internalizing required)
   -> Site-specific conjugation preferred (ThioMab, engineered Cys, enzymatic)
   -> DAR target: 2-4 (balance efficacy vs pharmacokinetics)
   -> Assess linker-payload stability in circulation

ELIF subcutaneous high-concentration formulation:
   -> IgG1 or IgG4 with low viscosity profile
   -> Consider co-formulation with hyaluronidase (Enhanze) for volumes > 2 mL
   -> Target: < 20 cP at 150 mg/mL
```

### Phase 8: Final Reporting — Candidate Assessment Summary

Synthesize all phases into a GO/NO-GO recommendation.

```
1. mcp__ctgov__ctgov_info(method: "search", condition: "indication", intervention: "target_name antibody", pageSize: 50)
   -> Competitive landscape: other antibodies in clinical development

2. mcp__fda__fda_info(method: "search_purple_book", drug_name: "comparator_antibody")
   -> Biosimilar landscape for reference products

3. mcp__drugbank__drugbank_info(method: "get_similar_drugs", drugbank_id: "DBxxxxx", limit: 10)
   -> Pharmacologically similar approved antibodies for benchmarking

4. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "TARGET_NAME antibody clinical Phase", start_date: "2022-01-01", num_results: 15)
   -> Recent clinical data for competitive intelligence
```

---

## Clinical Precedent Benchmarking

### Workflow

```
1. mcp__drugbank__drugbank_info(method: "search_by_target", target: "target_name", limit: 20)
   -> All approved antibodies for this target

2. mcp__fda__fda_info(method: "search_purple_book", drug_name: "approved_antibody")
   -> BLA approval date, reference product status, biosimilar count

3. mcp__fda__fda_info(method: "lookup_drug", search_term: "approved_antibody", search_type: "label", limit: 5)
   -> Dosing, formulation, ADA rates, boxed warnings

4. mcp__ctgov__ctgov_info(method: "stats", condition: "indication", intervention: "antibody")
   -> Pipeline density and competitive trial activity

5. mcp__fda__fda_info(method: "get_biosimilar_interchangeability", reference_product: "reference_antibody")
   -> Biosimilar competitive pressure
```

**Clinical Precedent Categories:**

| Category | Definition | Implication for New Candidate |
|----------|-----------|------------------------------|
| **First-in-class** | No approved antibody for this target | Higher risk, higher reward, novel MOA |
| **Best-in-class opportunity** | Approved antibodies exist, differentiation possible | Must demonstrate clear advantage (efficacy, safety, dosing) |
| **Biosimilar opportunity** | Reference product off-patent or approaching patent cliff | Lower risk, defined regulatory pathway, cost advantage |
| **Crowded class** | 3+ approved antibodies, multiple biosimilars | Differentiation critical, consider novel formats or combinations |

---

## Evidence Grading System

### Evidence Tiers for Antibody Development Decisions

| Tier | Evidence Type | Confidence | Action |
|------|-------------|------------|--------|
| **T1** | Clinical proof — approved antibody for same target with published Phase 3 data, ADA rates, manufacturing experience | Highest | Benchmark directly, adopt proven strategies |
| **T2** | Clinical data — antibodies in Phase 1-3 for same target with published interim results, preclinical packages | High | Incorporate learnings, anticipate class effects |
| **T3** | Preclinical evidence — published in vivo efficacy, PK/PD modeling, cross-reactive antibody data | Moderate | Inform design decisions, plan confirmatory studies |
| **T4** | Computational/in vitro only — sequence-based predictions, in silico models, in vitro binding data only | Low | Use as hypothesis, require experimental validation |

---

## Developability Red Flags

### Immediate Attention Required

```
CRITICAL (must resolve before CMC):
- Aggregation > 5% HMW at target concentration
- Viscosity > 30 cP at target concentration (SC formulation impossible)
- Unpaired cysteine in CDR (crosslinking, heterogeneity)
- N-glycosylation site (NxS/T) in CDR (heterogeneity, immunogenicity)
- Polyreactivity (nonspecific binding to DNA, insulin, cardiolipin)
- Expression yield < 0.5 g/L after optimization

WARNING (monitor and mitigate):
- Asp isomerization motif (DG) in HCDR1/HCDR2
- Asn deamidation (NG/NS) in CDR loops
- Exposed Met in binding interface
- Tm onset < 60C (accelerated stability risk)
- High surface hydrophobicity (HIC retention time > 10 min)
```

---

## IgG Subclass Selection Guide

| Subclass | FcgR Binding | C1q Binding | Half-life | Key Properties | Common Use |
|----------|-------------|-------------|-----------|---------------|-----------|
| **IgG1** | Strong (FcgRI, IIa, IIIa) | Strong | ~21 days | ADCC + CDC capable, standard effector function | Oncology (effector-dependent), depletion |
| **IgG1-LALA** | Silenced | Silenced | ~21 days | No effector function, blocking only | Receptor blocking, neutralization |
| **IgG1-afucosyl** | Enhanced FcgRIIIa | Strong | ~21 days | 10-100x enhanced ADCC | Oncology (ADCC-dependent) |
| **IgG2** | Weak | Weak | ~21 days | Reduced effector function, rigid hinge | Blocking, agonist antibodies |
| **IgG4** | Weak FcgRI only | None | ~21 days | No ADCC/CDC, Fab-arm exchange risk | Blocking, checkpoint inhibitors |
| **IgG4-S228P** | Weak FcgRI only | None | ~21 days | Stabilized hinge, no Fab-arm exchange | Standard for IgG4 therapeutics |

---

## Multi-Agent Workflow Examples

**"Humanize our mouse anti-PD-L1 antibody for clinical development"**
1. Antibody Engineering -> Humanization strategy, germline selection, CDR grafting design, developability assessment
2. Drug Target Analyst -> PD-L1 target biology, expression profile, pathway context
3. Clinical Trial Analyst -> Competitive landscape for anti-PD-L1 antibodies in clinical trials
4. FDA Consultant -> BLA precedent for PD-L1 antibodies, biosimilar landscape, Purple Book status

**"Assess developability of our anti-HER2 bispecific antibody"**
1. Antibody Engineering -> Developability matrix scoring, format selection (KiH vs CrossMAb), CMC feasibility, viscosity assessment
2. Drug Target Validator -> HER2 target validation score, pathway analysis
3. FDA Consultant -> Bispecific regulatory precedent, BLA pathway considerations
4. Pharmacovigilance Specialist -> Safety signals from approved HER2 antibodies (cardiac, infusion reactions)

**"Design an ADC targeting Nectin-4 for urothelial cancer"**
1. Antibody Engineering -> Antibody format, conjugation strategy, DAR optimization, internalization requirements, CMC timeline
2. Drug Target Analyst -> Nectin-4 expression profiling, target biology, bioactivity data for known binders
3. Clinical Trial Analyst -> Enfortumab vedotin trial data, competing ADC pipeline
4. FDA Consultant -> ADC regulatory pathway precedent, accelerated approval history

**"Evaluate immunogenicity risk for our humanized anti-TNF antibody"**
1. Antibody Engineering -> Immunogenicity prediction, T-cell epitope analysis, deimmunization strategy, ADA benchmarking
2. Pharmacovigilance Specialist -> ADA-related safety signals across anti-TNF class (infliximab, adalimumab, golimumab)
3. FDA Consultant -> ADA rate requirements in FDA labels, biosimilar immunogenicity comparability standards
4. Clinical Trial Analyst -> Head-to-head immunogenicity trial data, concomitant immunosuppression protocols

**"Plan CMC development for our first-in-class anti-TREM2 antibody"**
1. Antibody Engineering -> CMC feasibility assessment, cell line development timeline, formulation strategy, critical quality attributes
2. Drug Target Analyst -> TREM2 target characterization, pathway biology, competitive MOA landscape
3. Drug Target Validator -> TREM2 target validation score for Alzheimer's disease
4. FDA Consultant -> IND-enabling requirements for novel biologic, breakthrough therapy designation eligibility

## Completeness Checklist

- [ ] Report file created with all section headers and placeholders populated
- [ ] Target antigen characterized (expression, topology, epitope-accessible regions)
- [ ] Existing antibodies and biologics against the target cataloged
- [ ] Humanization strategy selected with germline identity assessment
- [ ] Developability matrix scored across all six dimensions (aggregation, PTM, Tm, expression, solubility, viscosity)
- [ ] Immunogenicity risk assessed with ADA benchmarks from approved comparators
- [ ] Antibody format and IgG subclass selected with rationale
- [ ] CMC feasibility evaluated (titer, purification yield, formulation concentration)
- [ ] Clinical precedent benchmarked (first-in-class, best-in-class, or biosimilar positioning)
- [ ] GO/NO-GO recommendation provided with evidence tier citations
