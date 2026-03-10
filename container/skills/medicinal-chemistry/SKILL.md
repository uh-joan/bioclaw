---
name: medicinal-chemistry
description: "ADMET optimization, drug-likeness scoring, PAINS alerts, ligand efficiency metrics, multi-parameter optimization, SAR analysis"
---

# Medicinal Chemistry Specialist

Specialist skill for compound optimization and drug-likeness assessment. Provides systematic evaluation of hit-to-lead and lead-to-candidate progression through ADMET profiling, structural alert detection, ligand efficiency metrics, multi-parameter optimization scoring, and structure-activity relationship analysis. Integrates data from chemical databases, bioactivity repositories, protein structure archives, and biomedical literature to deliver actionable medicinal chemistry recommendations.

> **Code recipes**: See [recipes.md](recipes.md) for copy-paste executable code templates covering RDKit and DeepChem.
> **ML recipes**: See [ml-recipes.md](ml-recipes.md) for machine learning and cheminformatics recipes (Datamol, DeepChem GCN/AttentiveFP, ChemBERTa, GROVER, virtual screening, ADMET, multi-task learning).

## Report-First Workflow

1. **Create report file immediately**: `[topic]_medicinal-chemistry_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Comprehensive drug monographs and regulatory intelligence -> use `drug-research`
- Clinical pharmacology, PK/PD modeling, dose-response -> use `clinical-pharmacology`
- Biologics engineering and antibody optimization -> use `protein-therapeutic-design`
- Formulation development and delivery systems -> use `formulation-science`
- Chemical safety and toxicology risk assessment -> use `chemical-safety-toxicology`
- Drug-drug interaction prediction and clinical impact -> use `drug-interaction-analyst`

## Cross-Reference: Other Skills

- **Comprehensive drug monographs and regulatory intelligence** -> use drug-research skill
- **Clinical pharmacology, PK/PD modeling, dose-response** -> use clinical-pharmacology skill
- **Biologics engineering, antibody optimization** -> use protein-therapeutic-design skill
- **Formulation development, excipient selection, delivery systems** -> use formulation-science skill

---

## Available MCP Tools

### `mcp__drugbank__drugbank_data`

| Method | Medicinal chemistry use | Key parameters |
|--------|------------------------|----------------|
| `search_drugs` | Find reference compounds by name, identify approved analogs | `query`, `limit` |
| `get_drug` | Retrieve full drug profile including PK, metabolism, toxicity | `drugbank_id` |
| `get_pharmacology` | ADMET data, metabolic enzymes, transporter substrates | `drugbank_id` |

### `mcp__chembl__chembl_data`

| Method | Medicinal chemistry use | Key parameters |
|--------|------------------------|----------------|
| `search_molecule` | Find compound ChEMBL ID from name, SMILES, or InChIKey | `query`, `limit` |
| `get_molecule` | Molecular properties, calculated descriptors, drug-likeness | `chembl_id` |
| `get_activities` | IC50, Ki, EC50 bioactivity data for SAR analysis | `chembl_id`, `target_id`, `limit` |
| `get_assays` | Assay descriptions, assay type, confidence scores | `chembl_id`, `limit` |
| `search_target` | Find biological targets by gene name or protein name | `query`, `limit` |
| `get_target` | Target details, target type, organism, components | `target_id` |

### `mcp__pubchem__pubchem_data`

| Method | Medicinal chemistry use | Key parameters |
|--------|------------------------|----------------|
| `search_compounds` | Compound lookup by name, SMILES, or InChIKey | `query`, `limit` |
| `get_compound` | Full compound record with physicochemical properties | `cid` |
| `get_properties` | MW, LogP, TPSA, HBD, HBA, RotB, exact mass, 2D/3D coords | `cid` |

### `mcp__pubmed__pubmed_data`

| Method | Medicinal chemistry use | Key parameters |
|--------|------------------------|----------------|
| `search` | Medchem literature: SAR studies, optimization strategies, scaffold classes | `keywords`, `num_results` |
| `fetch_details` | Full article metadata, abstract, MeSH terms | `pmid` |

### `mcp__opentargets__ot_data`

| Method | Medicinal chemistry use | Key parameters |
|--------|------------------------|----------------|
| `search_drug` | Find drug-target associations, indications, mechanisms | `query`, `size` |
| `get_drug_info` | Drug details with linked targets, diseases, evidence scores | `drug_id` |

### `mcp__alphafold__alphafold_data`

| Method | Medicinal chemistry use | Key parameters |
|--------|------------------------|----------------|
| `get_prediction` | Predicted 3D protein structure for structure-based drug design | `uniprot_id` |
| `search_structures` | Find available AlphaFold models for target proteins | `query`, `limit` |

### `mcp__pdb__pdb_data`

| Method | Medicinal chemistry use | Key parameters |
|--------|------------------------|----------------|
| `search_structures` | Find co-crystal structures, identify binding site geometry | `query`, `limit` |
| `get_structure` | Retrieve PDB entry with ligand, resolution, binding interactions | `pdb_id` |

### `mcp__bindingdb__bindingdb_data` (BindingDB — Binding Affinity Data)

| Method | Medicinal chemistry use | Key parameters |
|--------|------------------------|----------------|
| `search_by_name` | Reference compound binding data — look up known affinities for comparison | `name` |
| `search_by_smiles` | SAR by similarity — find structurally related compounds with binding data | `smiles` |
| `get_ligands_by_target` | Known SAR for target — retrieve all measured binders and their affinities | `uniprot_id`, `affinity_type`, `affinity_cutoff` |

---

## Core Workflows

### BindingDB SAR Data Retrieval

Query BindingDB for existing SAR data before starting medicinal chemistry optimization. BindingDB contains binding affinity measurements from academic and patent literature that complement ChEMBL. Before designing analogs or planning synthesis, check whether SAR around the scaffold has already been explored.

```
1. mcp__bindingdb__bindingdb_data(method="get_ligands_by_target", uniprot_id="TARGET_UNIPROT_ID", affinity_type="IC50", affinity_cutoff=10000)
   -> Retrieve all known binders with measured IC50 values for the target

2. mcp__bindingdb__bindingdb_data(method="search_by_name", name="REFERENCE_COMPOUND")
   -> Look up binding data for the lead compound across all targets (selectivity view)

3. mcp__bindingdb__bindingdb_data(method="search_by_smiles", smiles="LEAD_SMILES")
   -> Find structurally similar compounds with binding data — reveals existing SAR trends

Use this data to:
- Avoid re-synthesizing compounds already tested
- Identify productive and unproductive substitution patterns
- Benchmark new analogs against known SAR
- Detect selectivity liabilities early
```

### Workflow 1: Drug-Likeness Assessment

Evaluate a compound against established physicochemical rule sets to predict oral absorption and drug-like behavior.

#### 1.1 Lipinski Rule of Five (Ro5)

Predicts oral absorption. A compound is Ro5-compliant if it violates at most one rule.

| Property | Threshold | Rationale |
|----------|-----------|-----------|
| Molecular weight (MW) | <= 500 Da | Intestinal permeability drops above 500 |
| LogP (cLogP) | <= 5 | Aqueous solubility and passive absorption |
| H-bond donors (HBD) | <= 5 | Membrane permeability (NH, OH count) |
| H-bond acceptors (HBA) | <= 10 | Membrane permeability (N, O count) |

**Exception space**: Natural products, peptidomimetics, and substrates of active transporters (e.g., OATP, PEPT1) regularly violate Ro5 yet remain orally bioavailable. Note violations but do not disqualify automatically.

#### 1.2 Veber Rules

Predicts oral bioavailability independent of MW.

| Property | Threshold | Evidence |
|----------|-----------|----------|
| Topological polar surface area (TPSA) | <= 140 A^2 | Rat oral bioavailability >= 20% |
| Rotatable bonds (RotB) | <= 10 | Conformational flexibility affects absorption |

#### 1.3 Ghose Filter

Defines an optimized drug-like chemical space derived from known drugs.

| Property | Range |
|----------|-------|
| MW | 160-480 Da |
| LogP | -0.4 to 5.6 |
| Molar refractivity (MR) | 40-130 |
| Total atom count | 20-70 |

#### 1.4 Lead-Likeness Criteria

Lead compounds need room for optimization (property inflation during SAR).

| Property | Lead-Like Range |
|----------|----------------|
| MW | 200-350 Da |
| cLogP | -1 to 3 |
| HBD | <= 3 |
| HBA | <= 6 |
| RotB | <= 5 |
| LE | >= 0.3 kcal/mol/HA |

#### 1.5 Rule of Three (Ro3) for Fragments

Fragment hits from FBDD screening.

| Property | Threshold |
|----------|-----------|
| MW | <= 300 Da |
| cLogP | <= 3 |
| HBD | <= 3 |
| HBA | <= 3 |
| RotB | <= 3 |
| TPSA | <= 60 A^2 |
| LE | >= 0.3 (ideally >= 0.4) |

#### MCP Calls for Drug-Likeness

```
Step 1: Retrieve compound and properties
  mcp__pubchem__pubchem_data.search_compounds(query="compound name or SMILES")
  mcp__pubchem__pubchem_data.get_properties(cid=CID)
  --> MW, LogP, TPSA, HBD, HBA, RotB

Step 2: Cross-check with ChEMBL descriptors
  mcp__chembl__chembl_data.search_molecule(query="compound name")
  mcp__chembl__chembl_data.get_molecule(chembl_id=CHEMBL_ID)
  --> Calculated descriptors, Ro5 violations, ALogP, molecular species

Step 3: Compare to approved drugs in class
  mcp__drugbank__drugbank_data.search_drugs(query="drug class name")
  --> Property ranges of successful drugs in the same target class

Step 4: Apply all rule sets from Sections 1.1-1.5
  --> Generate composite drug-likeness profile
```

---

### Workflow 2: ADMET Prediction

Systematic evaluation of Absorption, Distribution, Metabolism, Excretion, and Toxicity.

#### 2.1 Absorption

| Parameter | Green | Yellow | Red | Key Drivers |
|-----------|-------|--------|-----|-------------|
| Aqueous solubility | > 100 ug/mL | 10-100 ug/mL | < 10 ug/mL | LogP, crystal packing, ionization |
| Caco-2 Papp | > 10 x10^-6 cm/s | 1-10 x10^-6 cm/s | < 1 x10^-6 cm/s | TPSA, HBD, MW |
| PAMPA permeability | > 5 x10^-6 cm/s | 1-5 x10^-6 cm/s | < 1 x10^-6 cm/s | LogP, TPSA |
| P-gp efflux ratio | < 2 | 2-5 | > 5 | HBD, PSA, basicity |
| Oral bioavailability (F) | > 30% | 10-30% | < 10% | Composite of above |

**Property relationships**: LogP 1-3 optimal for oral absorption. TPSA > 140 A^2 strongly predicts poor permeability. Each additional HBD above 3 reduces permeability ~10-fold.

#### 2.2 Distribution

| Parameter | Green | Yellow | Red | Significance |
|-----------|-------|--------|-----|-------------|
| Volume of distribution (Vd) | 0.5-3 L/kg | 0.1-0.5 or 3-10 L/kg | < 0.1 or > 10 L/kg | Tissue vs plasma partitioning |
| Plasma protein binding (PPB) | < 95% | 95-99% | > 99% | Free fraction drives efficacy |
| Brain penetration (Kp,uu) | > 0.3 (CNS target) | 0.1-0.3 | < 0.1 | P-gp, BCRP efflux, TPSA |
| fu,brain | > 0.01 | 0.001-0.01 | < 0.001 | Non-specific brain binding |

**Design levers**: Reduce cLogP to lower Vd. Reduce basicity (pKa < 8) to lower phospholipidosis risk. For CNS targets, TPSA < 90 A^2 and MW < 450 Da improve brain penetration.

#### 2.3 Metabolism

| Parameter | Green | Yellow | Red |
|-----------|-------|--------|-----|
| HLM CLint | < 15 uL/min/mg | 15-50 uL/min/mg | > 50 uL/min/mg |
| RLM CLint | < 30 uL/min/mg | 30-80 uL/min/mg | > 80 uL/min/mg |
| Human hepatocyte CLint | < 10 uL/min/10^6 cells | 10-30 uL/min/10^6 | > 30 uL/min/10^6 |
| CYP3A4 inhibition IC50 | > 10 uM | 3-10 uM | < 3 uM |
| CYP2D6 inhibition IC50 | > 10 uM | 3-10 uM | < 3 uM |
| CYP2C9 inhibition IC50 | > 10 uM | 3-10 uM | < 3 uM |
| CYP2C19 inhibition IC50 | > 10 uM | 3-10 uM | < 3 uM |
| CYP1A2 inhibition IC50 | > 10 uM | 3-10 uM | < 3 uM |
| CYP TDI (time-dependent inhibition) | No shift | < 2x shift | > 2x shift |

**CYP isoform specifics**:
- **CYP3A4**: Major drug-metabolizing enzyme (~50% of drugs). Substrates often lipophilic, MW > 300. Inhibitors: ketoconazole, ritonavir. Inducers: rifampin, carbamazepine.
- **CYP2D6**: Polymorphic (7% Caucasians are poor metabolizers). Substrates: basic amines, lipophilic. No induction. Inhibitors: paroxetine, quinidine.
- **CYP2C9**: Metabolizes acidic drugs (NSAIDs, warfarin). Polymorphic (*2, *3 alleles). Inhibitors: fluconazole.
- **CYP2C19**: Polymorphic (15-20% Asians are poor metabolizers). Substrates: PPIs, clopidogrel. Inhibitors: omeprazole.
- **CYP1A2**: Induced by smoking, charbroiled foods. Substrates: planar aromatic amines. Inhibitors: fluvoxamine, ciprofloxacin.

**Common metabolic soft spots**: benzylic positions, allylic C-H, N-dealkylation of tertiary amines, O-dealkylation, aromatic hydroxylation para to electron-donating groups, ester/amide hydrolysis.

#### 2.4 Excretion

| Parameter | Green | Yellow | Red |
|-----------|-------|--------|-----|
| In vivo clearance | < 30% hepatic blood flow | 30-70% | > 70% |
| Half-life (predicted human) | 4-12 h (QD target) | 2-4 h or 12-24 h | < 2 h or > 24 h |
| Renal excretion of parent | < 25% | 25-50% | > 50% (renal dose adjustment needed) |

#### 2.5 Toxicity

| Parameter | Green | Yellow | Red |
|-----------|-------|--------|-----|
| hERG IC50 | > 30 uM | 10-30 uM | < 10 uM |
| hERG safety margin (IC50 / free Cmax) | > 100x | 30-100x | < 30x |
| Ames mutagenicity | Negative | Equivocal | Positive |
| Micronucleus (in vitro) | Negative | Positive at high conc only | Positive at low conc |
| Phototoxicity (SOP > 2) | < 2 | 2-5 | > 5 |
| Hepatotoxicity (DILI) | No signal | In vitro signal only | Known DILI risk |
| Phospholipidosis | Negative | Equivocal | Positive |

**hERG liability**: Compounds with basic amine (pKa > 7) + cLogP > 3 + aromatic ring are high risk. T-shaped topology with two hydrophobic wings flanking a basic center is the classic hERG pharmacophore.

#### MCP Calls for ADMET

```
Step 1: Retrieve known ADMET data
  mcp__chembl__chembl_data.get_molecule(chembl_id=CHEMBL_ID)
  --> Calculated properties, drug-likeness, predicted ADMET flags

Step 2: Get reference drug PK data
  mcp__drugbank__drugbank_data.get_drug(drugbank_id=DB_ID)
  mcp__drugbank__drugbank_data.get_pharmacology(drugbank_id=DB_ID)
  --> Absorption, distribution, metabolism, elimination, toxicity

Step 3: Check CYP interaction profile
  mcp__chembl__chembl_data.get_activities(chembl_id=CHEMBL_ID, target_id="CYP3A4_TARGET_ID")
  --> Measured CYP inhibition data from ChEMBL

Step 4: Literature for class-specific ADMET issues
  mcp__pubmed__pubmed_data.search(keywords="compound class ADMET metabolism CYP")
  --> Published ADMET data, metabolite identification studies

Step 5: Apply traffic light system (Section 2.1-2.5)
  --> Color-coded ADMET profile with prioritized flags
```

---

### Workflow 3: PAINS and Structural Alert Detection

Identify problematic substructures that cause assay interference, toxicity, or metabolic instability.

#### 3.1 PAINS Filters (Pan-Assay Interference Compounds)

Frequent hitters in HTS that produce false positives through non-specific mechanisms.

| PAINS Class | Mechanism | Risk Level |
|-------------|-----------|------------|
| Rhodanines | Michael acceptor, metal chelation, aggregation | High |
| Catechols | Redox cycling, metal chelation, quinone formation | High |
| Quinones | Redox cycling, covalent modification of proteins | High |
| Hydroxyphenyl hydrazones | Metal chelation, redox activity | High |
| 2-Amino-3-carbonyl thiophenes | Decomposition in assay conditions | Medium |
| Curcuminoids | Electrophilic, assay interference, aggregation | High |
| Toxoflavins | Redox cycling | Medium |
| Isothiazolones | Thiol-reactive electrophile | High |
| Alkylidene barbiturates | Knoevenagel electrophile | Medium |
| Enones (cross-conjugated) | Michael acceptor | Medium |
| Ene-rhodanines | Michael acceptor + metal chelation | High |
| Catechol-like (aminophenols) | Auto-oxidation, quinone-imine formation | Medium |

**Decision rule**: If compound triggers >= 1 PAINS alert, require orthogonal biophysical confirmation (SPR, ITC, TSA, or X-ray crystallography) before progressing. If the PAINS motif is not part of the pharmacophore, replace the substructure and retest.

#### 3.2 Known Toxicophores

| Structural Alert | Toxicity Mechanism | Action |
|-----------------|-------------------|--------|
| Nitroaromatic | Mutagenicity (nitroreduction to hydroxylamine) | Eliminate |
| Aniline (unsubstituted) | Methemoglobinemia, mutagenicity | Block metabolism or replace |
| Hydrazine / hydrazide | Hepatotoxicity, mutagenicity | Eliminate unless essential |
| Polycyclic aromatic (>= 4 fused rings) | DNA intercalation, carcinogenicity | Reduce ring count |
| Alkyl halide | DNA alkylation | Eliminate |
| Epoxide (non-arene) | Electrophilic, mutagenic | Eliminate unless prodrug |
| Acyl halide | Non-selective acylation | Eliminate |
| Michael acceptor (unhindered) | Covalent protein modification | Eliminate unless targeted covalent |
| Thiourea | Thyroid toxicity, hepatotoxicity | Replace with urea or amide |
| Hydroxamic acid | Metal chelation, mutagenicity | Acceptable only if MOA requires metal chelation (e.g., HDAC inhibitors) |

#### 3.3 Reactive Metabolite Alerts

| Structural Motif | Reactive Metabolite | CYP Involved | Clinical Risk |
|-----------------|-------------------|--------------|---------------|
| Furan | cis-Enedial | CYP3A4 | Hepatotoxicity |
| Thiophene | Thiophene S-oxide, epoxide | CYP2C9 | Agranulocytosis, hepatotox |
| para-Aminophenol | Quinone-imine (NAPQI-like) | CYP2E1, CYP1A2 | Hepatotoxicity |
| Methylenedioxy | Carbene intermediate | CYP3A4 | CYP3A4 MBI (mechanism-based inhibition) |
| Terminal alkyne | Ketene intermediate | CYP3A4 | CYP3A4 MBI |
| Cyclopropylamine | Radical intermediate | Multiple | Hepatotoxicity |
| Aniline | Hydroxylamine, nitroso | CYP1A2 | Mutagenicity, blood toxicity |

#### Structural Alert Decision Tree

```
Compound Input (SMILES)
  |
  +-- Screen for PAINS motifs
  |     |
  |     +-- PAINS hit? --> Flag specific class
  |     |                   |
  |     |                   +-- Essential to pharmacophore?
  |     |                   |     +-- YES --> Require biophysical validation (SPR, ITC, X-ray)
  |     |                   |     +-- NO  --> Replace substructure, resynthesize, retest
  |     |                   |
  |     +-- Clean --> Continue
  |
  +-- Screen for toxicophores (Section 3.2)
  |     |
  |     +-- DNA-reactive motif? --> HARD STOP, do not progress
  |     +-- Known hepatotoxic motif? --> Flag, assess risk-benefit for indication
  |     +-- Mutagenic alert? --> Ames test required before progression
  |     +-- Clean --> Continue
  |
  +-- Screen for reactive metabolite alerts (Section 3.3)
  |     |
  |     +-- Reactive metabolite risk? --> Test in GSH trapping assay
  |     |                                 Quantify covalent binding in hepatocytes
  |     |                                 If positive: modify or abandon
  |     +-- Clean --> Continue
  |
  +-- RESULT: Clean / Flagged (with specific action items) / Rejected
```

---

### Workflow 4: Ligand Efficiency Metrics

Normalize potency by molecular size to guide optimization and detect molecular obesity.

#### 4.1 Metric Definitions and Formulas

| Metric | Full Name | Formula | Ideal Range | Interpretation |
|--------|-----------|---------|-------------|----------------|
| LE | Ligand Efficiency | LE = -deltaG / HA = 1.4(-logIC50) / HA | >= 0.3 kcal/mol/atom | Binding energy per heavy atom; gold standard for hit triage |
| LLE (LipE) | Lipophilic Ligand Efficiency | LLE = pIC50 - cLogP | >= 5 | Potency not driven by lipophilicity; higher = more specific binding |
| LELP | LE-dependent Lipophilicity | LELP = cLogP / LE | -10 to 10 | Lipophilicity cost per unit of efficiency; optimal < 10 |
| SILE | Size-Independent LE | SILE = -deltaG / HA^0.3 | >= 5.5 | Corrects for the mathematical size-dependency of LE |
| FQ | Fit Quality | FQ = LE / LE_predicted(HA) | 0.8-1.2 | LE relative to theoretical maximum for that size |
| BEI | Binding Efficiency Index | BEI = pIC50 / (MW/1000) | >= 15 | Potency normalized by molecular weight |
| SEI | Surface Efficiency Index | SEI = pIC50 / (PSA/100) | >= 10 | Potency normalized by polar surface area |

**Key relationships**:
- LE approximation: LE = 1.4 * pIC50 / HA (where 1.4 = -RT * ln(10) / 1000 at 298K, scaled for kcal/mol)
- Exact: deltaG = RT * ln(Kd) = 0.592 * ln(Kd) kcal/mol at 298K
- For IC50 in nM: pIC50 = -log10(IC50 * 1e-9) = 9 - log10(IC50_nM)
- LE_predicted(HA) = 0.0715 + 7.5328/HA + 25.7079/HA^2 (empirical fit for FQ calculation)

#### 4.2 Efficiency Tracking During Optimization

Acceptable optimization trajectories:
- **Ideal**: LE stable or increasing, LLE increasing, MW growing <= 80 Da per 10x potency gain
- **Molecular obesity**: LE declining, MW growing fast, potency improving slowly -- adding atoms without productive binding interactions
- **Lipophilic trap**: LLE declining, cLogP rising, potency driven by hydrophobic burial -- leads to poor solubility, high CYP metabolism, high PPB

**Alarm thresholds during optimization**:
- LE drops below 0.25 --> restructure approach (scaffold hop or fragment merge)
- LLE drops below 3 --> reduce lipophilicity, add polarity to binding interactions
- LELP exceeds 15 --> too much lipophilicity invested per unit of efficiency
- BEI drops below 10 --> molecular weight growing without proportional potency gain

#### MCP Calls for Ligand Efficiency

```
Step 1: Retrieve bioactivity data
  mcp__chembl__chembl_data.get_activities(chembl_id=CHEMBL_ID)
  --> IC50, Ki values against primary target

Step 2: Retrieve molecular properties
  mcp__pubchem__pubchem_data.get_properties(cid=CID)
  --> MW, heavy atom count, cLogP, TPSA

Step 3: Calculate efficiency metrics using formulas in Section 4.1
  --> LE, LLE, LELP, SILE, FQ, BEI, SEI

Step 4: Benchmark against class
  mcp__chembl__chembl_data.search_molecule(query="target-class scaffold SMILES")
  --> Efficiency metrics for comparator compounds in same series

Step 5: Literature context for efficiency benchmarks
  mcp__pubmed__pubmed_data.search(keywords="target name ligand efficiency optimization")
  --> Published LE/LLE values for the target class
```

---

### Workflow 5: Multi-Parameter Optimization (MPO)

Composite scoring frameworks that balance competing properties.

#### 5.1 CNS MPO Score (Pfizer)

Desirability function for brain-penetrant compounds. Scale: 0-6.

| Property | Score = 1.0 | Score = 0.0 | Linear interpolation |
|----------|-------------|-------------|---------------------|
| cLogP | <= 3 | >= 5 | Between 3 and 5 |
| cLogD (pH 7.4) | <= 2 | >= 4 | Between 2 and 4 |
| MW | <= 360 | >= 500 | Between 360 and 500 |
| TPSA | 40-90 (optimal) | > 120 or < 20 | Linear decay outside 40-90 |
| HBD | <= 0.5 | >= 3.5 | Between 0.5 and 3.5 |
| pKa (most basic center) | <= 8 | >= 10 | Between 8 and 10 |

**Target**: CNS MPO >= 4 predicts good brain penetration. 74% of marketed CNS drugs score >= 4. Score < 3 = low probability of CNS exposure.

#### 5.2 Pfizer 3/75 Rule

Compounds with cLogP > 3 AND TPSA < 75 A^2 have a higher incidence of toxicity in preclinical studies. Design away from this "danger zone."

- cLogP > 3 AND TPSA < 75 --> increased toxicity risk (promiscuity, off-target binding)
- cLogP <= 3 OR TPSA >= 75 --> acceptable space

#### 5.3 GSK 4/400 Rule

Compounds with cLogP > 4 AND MW > 400 have lower probability of advancing through development.

- cLogP > 4 AND MW > 400 --> high attrition risk
- cLogP <= 4 OR MW <= 400 --> preferred space

#### 5.4 Desirability Function MPO

General-purpose MPO scoring using desirability functions for arbitrary property sets.

| Property | Optimal Range | Tolerable Range | Weight |
|----------|--------------|-----------------|--------|
| pIC50 (primary target) | >= 7 (100 nM) | >= 6 (1 uM) | 25% |
| Selectivity (off-target ratio) | >= 100x | >= 30x | 10% |
| HLM CLint | < 15 uL/min/mg | < 50 uL/min/mg | 15% |
| Solubility | > 100 ug/mL | > 10 ug/mL | 10% |
| Caco-2 Papp | > 10 x10^-6 cm/s | > 1 x10^-6 cm/s | 10% |
| hERG IC50 | > 30 uM | > 10 uM | 10% |
| CYP3A4 IC50 | > 10 uM | > 3 uM | 5% |
| LE | >= 0.3 | >= 0.25 | 5% |
| LLE | >= 5 | >= 3 | 5% |
| TPSA | 60-120 A^2 | 40-140 A^2 | 5% |

#### MCP Calls for MPO

```
Step 1: Gather all required properties
  mcp__pubchem__pubchem_data.get_properties(cid=CID)
  mcp__chembl__chembl_data.get_activities(chembl_id=CHEMBL_ID)
  mcp__chembl__chembl_data.get_molecule(chembl_id=CHEMBL_ID)
  --> MW, cLogP, TPSA, HBD, pIC50, selectivity data

Step 2: Get ADMET data
  mcp__drugbank__drugbank_data.get_pharmacology(drugbank_id=DB_ID)
  --> CLint, CYP inhibition, hERG, solubility, permeability

Step 3: For CNS targets, retrieve pKa
  mcp__chembl__chembl_data.get_molecule(chembl_id=CHEMBL_ID)
  --> Most basic pKa for CNS MPO calculation

Step 4: Check protein target structure for SBDD context
  mcp__pdb__pdb_data.search_structures(query="target name + inhibitor")
  mcp__alphafold__alphafold_data.get_prediction(uniprot_id=UNIPROT_ID)
  --> Binding site geometry to rationalize MPO trade-offs

Step 5: Calculate MPO scores from Sections 5.1-5.4
  --> CNS MPO, Pfizer 3/75, GSK 4/400, desirability MPO
```

---

### Workflow 6: SAR Analysis

Systematic interpretation of structure-activity relationships.

#### 6.1 Matched Molecular Pair (MMP) Analysis

An MMP is two compounds differing by a single structural transformation at one site, sharing the same molecular context.

**Common productive transformations in medchem**:

| Transformation | delta cLogP | Typical Effect | Design Context |
|---------------|-------------|----------------|----------------|
| H -> F | +0.14 | Block metabolic soft spot, minimal steric change | CYP oxidation site |
| H -> Cl | +0.71 | Hydrophobic contact, increased potency | Hydrophobic subpocket |
| H -> Me | +0.56 | Fill small pocket, block metabolism | Steric shielding |
| CH3 -> CF3 | +0.55 | Metabolic stability, electron withdrawal | Electron-poor environment |
| OH -> OMe | +0.47 | Block glucuronidation | Phase II metabolism |
| NH -> NMe | +0.47 | Reduce HBD, improve permeability | TPSA reduction |
| Phenyl -> Pyridyl (3-) | -0.96 | Reduce LogP, improve solubility | Lower lipophilicity |
| Phenyl -> Cyclohexyl | +0.23 | Remove aromatic ring, improve Fsp3 | Reduce flatness |
| Ester -> Amide | -1.0 | Metabolic stability (block esterases) | In vivo stability |
| CH2 -> O | -1.0 | Reduce LogP, add H-bond acceptor | Tune polarity |
| Morpholine -> Piperazine | -0.54 | Change basicity, H-bond pattern | Target interaction |

#### 6.2 Activity Cliff Detection

An activity cliff: structurally similar compounds (Tanimoto >= 0.8) with large potency difference (delta pIC50 >= 2.0, i.e., 100-fold).

**Classification**:
- **Scaffold cliffs**: Core change drives potency -- probe binding mode requirements
- **R-group cliffs**: Substituent change at one position -- high-information SAR points
- **Stereochemical cliffs**: Enantiomer/diastereomer with large potency difference -- confirm binding geometry

**Action on activity cliffs**: Investigate binding mode differences by docking or co-crystallography. Use cliff data to refine pharmacophore models and build predictive SAR models.

#### 6.3 R-Group Decomposition

For a congeneric series with common scaffold and variable positions R1, R2, ..., Rn:

1. **Free-Wilson analysis**: Decompose activity = scaffold contribution + sum(R-group contributions) + interaction terms
2. **Additivity check**: If R1 and R2 contributions are additive, design combinatorial matrix
3. **Saturation assessment**: Has the SAR at each position been adequately explored? Minimum 5-8 diverse R-groups per position
4. **Cooperative effects**: When observed activity deviates from sum of individual R-group contributions -- indicates synergistic or antagonistic interactions requiring explicit pair testing

#### MCP Calls for SAR

```
Step 1: Retrieve all analogs in a series
  mcp__chembl__chembl_data.search_molecule(query="scaffold SMILES or core name")
  mcp__pubchem__pubchem_data.search_compounds(query="scaffold SMILES")
  --> Enumerate known analogs with same core

Step 2: Bioactivity for each analog
  mcp__chembl__chembl_data.get_activities(chembl_id=COMPOUND_ID)
  --> IC50, Ki, EC50 values for SAR table construction

Step 3: Structural context from co-crystals
  mcp__pdb__pdb_data.search_structures(query="target name + compound class")
  mcp__pdb__pdb_data.get_structure(pdb_id=PDB_ID)
  --> Binding mode, key interactions, water molecules

Step 4: AlphaFold for targets without co-crystals
  mcp__alphafold__alphafold_data.search_structures(query="target protein")
  mcp__alphafold__alphafold_data.get_prediction(uniprot_id=UNIPROT_ID)
  --> Predicted binding site for docking studies

Step 5: Literature SAR
  mcp__pubmed__pubmed_data.search(keywords="compound series SAR optimization")
  --> Published SAR studies, medicinal chemistry letters

Step 6: Drug-target association context
  mcp__opentargets__ot_data.search_drug(query="compound name")
  mcp__opentargets__ot_data.get_drug_info(drug_id=DRUG_ID)
  --> Mechanism context for SAR interpretation
```

---

## MedChem Scoring Framework (0-100)

Composite compound quality score integrating six domains. Each domain produces a 0-100 subscore; the weighted composite is the MedChem Score.

### Component Weights

| Domain | Weight | What It Measures |
|--------|--------|-----------------|
| Drug-likeness compliance | 20% | Ro5, Veber, Ghose, lead-likeness, stage-appropriate criteria |
| ADMET profile | 25% | Traffic light system across A/D/M/E/T parameters |
| Structural alerts / PAINS | 15% | Absence of problematic substructures; clean = full score |
| Ligand efficiency metrics | 20% | LE, LLE, LELP, BEI -- normalized potency quality |
| Synthetic accessibility | 10% | SA score (1-10 scale), route feasibility, step count |
| IP / novelty space | 10% | Structural novelty vs prior art, freedom-to-operate |

### Scoring Details

#### Drug-Likeness (20%)

| Condition | Points (out of 100) |
|-----------|-------------------|
| Passes Lipinski Ro5 (0 violations) | 30 |
| Passes Lipinski Ro5 (1 violation) | 20 |
| Passes Veber rules | 20 |
| Passes Ghose filter | 15 |
| Passes Egan filter | 15 |
| Passes Muegge filter | 10 |
| Stage-appropriate properties (Section 1.4-1.5) | 10 |

#### ADMET Profile (25%)

Convert traffic light counts to score:
- Each Green parameter: +100/N points (N = number of parameters assessed)
- Each Yellow parameter: +50/N points
- Each Red parameter: 0 points
- Any Red toxicity parameter (hERG, Ames, hepatotox): -20 penalty to domain score (floor at 0)

#### Structural Alerts / PAINS (15%)

| Condition | Score |
|-----------|-------|
| No alerts of any kind | 100 |
| 1 low-risk PAINS alert (e.g., borderline motif) | 70 |
| 1 medium-risk PAINS or Brenk alert | 40 |
| Multiple alerts or 1 high-risk toxicophore | 10 |
| DNA-reactive motif or hard-stop alert | 0 |

#### Ligand Efficiency Metrics (20%)

| Metric | Full Score Condition | Zero Score Condition |
|--------|---------------------|---------------------|
| LE | >= 0.3 | < 0.2 |
| LLE | >= 5 | < 2 |
| LELP | -10 to 10 | < -15 or > 20 |
| BEI | >= 15 | < 8 |

Domain score = average of the four metric scores (each 0-100, linearly interpolated).

#### Synthetic Accessibility (10%)

| SA Score (Ertl) | Domain Score |
|-----------------|-------------|
| 1-3 (easy) | 100 |
| 3-5 (moderate) | 70 |
| 5-7 (difficult) | 40 |
| 7-10 (very difficult) | 10 |

Additional factors: number of chiral centers (>3 = -20), rare building blocks (-10), multi-step sequences >10 steps (-10).

#### IP / Novelty Space (10%)

| Condition | Domain Score |
|-----------|-------------|
| Novel scaffold, no close prior art (Tanimoto < 0.6 to known drugs/patents) | 100 |
| Moderately novel (Tanimoto 0.6-0.8) | 60 |
| Close to existing IP (Tanimoto > 0.8) | 20 |
| Direct analog of patented compound | 0 |

### MedChem Score Interpretation

| Score Range | Grade | Recommendation |
|-------------|-------|---------------|
| 80-100 | Excellent | Advance to candidate selection / in vivo studies |
| 60-79 | Good | Address 1-2 weakest domains, then advance |
| 40-59 | Moderate | Significant optimization required; focus on red flags |
| 20-39 | Poor | Consider scaffold hop or new chemical matter |
| 0-19 | Reject | Fundamental liabilities; do not invest further |

---

## Python Code Templates

### Template 1: Lipinski/Veber Rule Calculations

```python
def assess_drug_likeness(mw, clogp, hbd, hba, tpsa, rotb, mr=None, atom_count=None):
    """Evaluate compound against Lipinski Ro5, Veber, Ghose, and Egan filters.

    Args:
        mw: Molecular weight (Da)
        clogp: Calculated LogP
        hbd: Hydrogen bond donor count
        hba: Hydrogen bond acceptor count
        tpsa: Topological polar surface area (A^2)
        rotb: Rotatable bond count
        mr: Molar refractivity (optional, for Ghose)
        atom_count: Total atom count (optional, for Ghose)

    Returns:
        Dict with filter results and composite score
    """
    results = {}

    # Lipinski Ro5
    lip_checks = {
        'MW <= 500': mw <= 500,
        'cLogP <= 5': clogp <= 5,
        'HBD <= 5': hbd <= 5,
        'HBA <= 10': hba <= 10
    }
    violations = sum(1 for v in lip_checks.values() if not v)
    results['lipinski'] = {
        'pass': violations <= 1,
        'violations': violations,
        'checks': lip_checks
    }

    # Veber
    veber_checks = {
        'TPSA <= 140': tpsa <= 140,
        'RotB <= 10': rotb <= 10
    }
    results['veber'] = {
        'pass': all(veber_checks.values()),
        'checks': veber_checks
    }

    # Egan
    egan_checks = {
        'TPSA <= 132': tpsa <= 132,
        'cLogP in [-1, 6]': -1.0 <= clogp <= 6.0
    }
    results['egan'] = {
        'pass': all(egan_checks.values()),
        'checks': egan_checks
    }

    # Ghose (if optional params provided)
    if mr is not None and atom_count is not None:
        ghose_checks = {
            'MW 160-480': 160 <= mw <= 480,
            'cLogP -0.4 to 5.6': -0.4 <= clogp <= 5.6,
            'MR 40-130': 40 <= mr <= 130,
            'Atoms 20-70': 20 <= atom_count <= 70
        }
        results['ghose'] = {
            'pass': all(ghose_checks.values()),
            'checks': ghose_checks
        }

    # Lead-likeness
    lead_checks = {
        'MW 200-350': 200 <= mw <= 350,
        'cLogP <= 3': clogp <= 3,
        'HBD <= 3': hbd <= 3,
        'HBA <= 6': hba <= 6,
        'RotB <= 5': rotb <= 5
    }
    results['lead_like'] = {
        'pass': all(lead_checks.values()),
        'checks': lead_checks
    }

    # Fragment Ro3
    ro3_checks = {
        'MW <= 300': mw <= 300,
        'cLogP <= 3': clogp <= 3,
        'HBD <= 3': hbd <= 3,
        'HBA <= 3': hba <= 3,
        'RotB <= 3': rotb <= 3
    }
    results['fragment_ro3'] = {
        'pass': all(ro3_checks.values()),
        'checks': ro3_checks
    }

    # Composite: fraction of applicable filters passed
    filters_passed = sum(1 for f in results.values() if f.get('pass', False))
    total_filters = len(results)
    results['composite_score'] = round(filters_passed / total_filters * 100, 1)

    # Stage assignment
    if results['fragment_ro3']['pass']:
        results['stage'] = 'Fragment'
    elif results['lead_like']['pass']:
        results['stage'] = 'Lead-like'
    elif results['lipinski']['pass'] and results['veber']['pass']:
        results['stage'] = 'Drug-like'
    else:
        results['stage'] = 'Beyond Rule of 5 (bRo5)'

    return results
```

### Template 2: Ligand Efficiency Calculations

```python
import math

R_KCAL = 1.987e-3   # kcal/(mol*K)
T_STD = 298.15       # K (25 C)
RT = R_KCAL * T_STD  # 0.592 kcal/mol

def calc_ligand_efficiency(ic50_nM=None, ki_nM=None, mw=None, hac=None,
                           clogp=None, psa=None):
    """Calculate ligand efficiency metrics from potency and property data.

    Args:
        ic50_nM: IC50 in nanomolar (use ki_nM preferentially)
        ki_nM: Ki in nanomolar
        mw: Molecular weight (Da)
        hac: Heavy atom count
        clogp: Calculated LogP
        psa: Polar surface area (A^2)

    Returns:
        Dict of efficiency metrics with assessments
    """
    metrics = {}

    # Determine potency
    if ki_nM is not None:
        conc_M = ki_nM * 1e-9
    elif ic50_nM is not None:
        conc_M = ic50_nM * 1e-9
    else:
        return {'error': 'Provide ic50_nM or ki_nM'}

    pActivity = -math.log10(conc_M)
    delta_g = RT * math.log(conc_M)  # kcal/mol, negative for binders

    metrics['pActivity'] = round(pActivity, 2)
    metrics['deltaG_kcal_mol'] = round(delta_g, 2)

    # LE = -deltaG / HAC
    if hac and hac > 0:
        le = -delta_g / hac
        metrics['LE'] = round(le, 3)
        metrics['LE_assessment'] = (
            'good' if le >= 0.3 else
            'marginal' if le >= 0.25 else
            'poor'
        )

        # SILE = -deltaG / HAC^0.3
        sile = -delta_g / (hac ** 0.3)
        metrics['SILE'] = round(sile, 2)

        # FQ = LE / LE_predicted
        le_pred = 0.0715 + 7.5328 / hac + 25.7079 / (hac ** 2)
        fq = le / le_pred if le_pred > 0 else 0
        metrics['FQ'] = round(fq, 2)
        metrics['FQ_assessment'] = (
            'good' if 0.8 <= fq <= 1.2 else
            'overperforming' if fq > 1.2 else
            'underperforming'
        )

        # LELP = cLogP / LE
        if clogp is not None and le > 0:
            lelp = clogp / le
            metrics['LELP'] = round(lelp, 2)
            metrics['LELP_assessment'] = (
                'good' if -10 <= lelp <= 10 else 'concern'
            )

    # BEI = pActivity / (MW / 1000)
    if mw and mw > 0:
        bei = pActivity / (mw / 1000)
        metrics['BEI'] = round(bei, 2)
        metrics['BEI_assessment'] = (
            'good' if bei >= 15 else
            'marginal' if bei >= 10 else
            'poor'
        )

    # SEI = pActivity / (PSA / 100)
    if psa and psa > 0:
        sei = pActivity / (psa / 100)
        metrics['SEI'] = round(sei, 2)

    # LLE = pActivity - cLogP
    if clogp is not None:
        lle = pActivity - clogp
        metrics['LLE'] = round(lle, 2)
        metrics['LLE_assessment'] = (
            'good' if lle >= 5 else
            'marginal' if lle >= 3 else
            'poor'
        )

    return metrics
```

### Template 3: MPO Scoring Functions

```python
import math

def _sigmoid(value, midpoint, slope=1.0):
    """Sigmoid 0-1 score centered at midpoint."""
    return 1.0 / (1.0 + math.exp(-slope * (value - midpoint)))

def _linear_score(value, optimal_low, optimal_high, min_val=None, max_val=None):
    """Linear 0-1 score: 1.0 in [optimal_low, optimal_high], decays outside."""
    if optimal_low <= value <= optimal_high:
        return 1.0
    elif value < optimal_low:
        floor = min_val if min_val is not None else optimal_low - (optimal_high - optimal_low)
        return max(0.0, (value - floor) / (optimal_low - floor))
    else:
        ceil = max_val if max_val is not None else optimal_high + (optimal_high - optimal_low)
        return max(0.0, (ceil - value) / (ceil - optimal_high))

def calc_cns_mpo(clogp, clogd, mw, tpsa, hbd, pka_basic):
    """Pfizer CNS MPO score (0-6 scale).

    Returns dict with total score, component breakdown, assessment.
    """
    scores = {}
    scores['cLogP'] = max(0, min(1, 1 - (clogp - 3) / 2))
    scores['cLogD'] = max(0, min(1, 1 - (clogd - 2) / 2))
    scores['MW'] = max(0, min(1, 1 - (mw - 360) / 140))

    if 40 <= tpsa <= 90:
        scores['TPSA'] = 1.0
    elif tpsa < 40:
        scores['TPSA'] = max(0, tpsa / 40)
    else:
        scores['TPSA'] = max(0, 1 - (tpsa - 90) / 30)

    scores['HBD'] = max(0, min(1, 1 - (hbd - 0.5) / 3.0))
    scores['pKa'] = max(0, min(1, 1 - (pka_basic - 8) / 2))

    total = sum(scores.values())
    return {
        'cns_mpo': round(total, 2),
        'components': {k: round(v, 2) for k, v in scores.items()},
        'assessment': (
            'Good CNS penetration' if total >= 4 else
            'Marginal' if total >= 3 else
            'Poor CNS penetration'
        )
    }

def check_pfizer_375(clogp, tpsa):
    """Pfizer 3/75 rule: cLogP > 3 AND TPSA < 75 = toxicity risk."""
    in_danger = clogp > 3 and tpsa < 75
    return {
        'in_danger_zone': in_danger,
        'cLogP': clogp,
        'TPSA': tpsa,
        'recommendation': 'Increase TPSA or reduce cLogP' if in_danger else 'Acceptable'
    }

def check_gsk_4400(clogp, mw):
    """GSK 4/400 rule: cLogP > 4 AND MW > 400 = high attrition risk."""
    high_risk = clogp > 4 and mw > 400
    return {
        'high_attrition_risk': high_risk,
        'cLogP': clogp,
        'MW': mw,
        'recommendation': 'Reduce MW or cLogP' if high_risk else 'Acceptable'
    }

def calc_desirability_mpo(properties):
    """General desirability-function MPO (0-100 scale).

    Args:
        properties: dict with keys:
            pic50, selectivity_ratio, hlm_clint, solubility_ug_ml,
            caco2_papp_e6, herg_ic50_uM, cyp3a4_ic50_uM, le, lle, tpsa

    Returns:
        Dict with total MPO, component scores, grade
    """
    p = properties
    components = {}

    # Potency (25%)
    components['potency'] = min(1.0, _sigmoid(p.get('pic50', 5), 7.0, 1.5))

    # Selectivity (10%)
    sel = p.get('selectivity_ratio', 1)
    components['selectivity'] = min(1.0, sel / 100)

    # Metabolic stability (15%)
    clint = p.get('hlm_clint', 50)
    components['metabolism'] = max(0, 1.0 - clint / 100)

    # Solubility (10%)
    components['solubility'] = _linear_score(
        p.get('solubility_ug_ml', 10), 100, 1000, 0, 2000)

    # Permeability (10%)
    components['permeability'] = min(1.0, _sigmoid(
        p.get('caco2_papp_e6', 1), 10, 0.3))

    # hERG safety (10%)
    components['herg'] = min(1.0, p.get('herg_ic50_uM', 1) / 30)

    # CYP3A4 (5%)
    components['cyp3a4'] = min(1.0, p.get('cyp3a4_ic50_uM', 1) / 10)

    # LE (5%)
    components['le'] = min(1.0, p.get('le', 0) / 0.3)

    # LLE (5%)
    components['lle'] = min(1.0, p.get('lle', 0) / 5)

    # TPSA (5%)
    components['tpsa'] = _linear_score(p.get('tpsa', 80), 60, 120, 20, 160)

    weights = {
        'potency': 0.25, 'selectivity': 0.10, 'metabolism': 0.15,
        'solubility': 0.10, 'permeability': 0.10, 'herg': 0.10,
        'cyp3a4': 0.05, 'le': 0.05, 'lle': 0.05, 'tpsa': 0.05
    }

    total = sum(components[k] * weights[k] for k in components) * 100

    grade = (
        'Excellent' if total >= 80 else
        'Good' if total >= 60 else
        'Moderate' if total >= 40 else
        'Poor'
    )

    return {
        'mpo_total': round(total, 1),
        'components': {k: round(v * 100, 1) for k, v in components.items()},
        'grade': grade
    }
```

### Template 4: Property-Activity Relationship Plots

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def plot_sar_landscape(compounds, output_path='sar_landscape.png'):
    """Plot property-activity relationships for a compound series.

    Args:
        compounds: list of dicts, each with keys:
            name, pic50, mw, clogp, le, lle, tpsa
        output_path: file path for saved figure
    """
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle('SAR Landscape Analysis', fontsize=14, fontweight='bold')

    names = [c['name'] for c in compounds]
    pic50 = [c['pic50'] for c in compounds]
    mw = [c['mw'] for c in compounds]
    clogp = [c['clogp'] for c in compounds]
    le = [c['le'] for c in compounds]
    lle = [c['lle'] for c in compounds]
    tpsa = [c['tpsa'] for c in compounds]

    # Plot 1: pIC50 vs MW (size-efficiency)
    ax = axes[0, 0]
    sc = ax.scatter(mw, pic50, c=le, cmap='RdYlGn', s=80,
                    edgecolors='black', linewidth=0.5)
    ax.set_xlabel('MW (Da)')
    ax.set_ylabel('pIC50')
    ax.set_title('Potency vs Size')
    ax.axhline(y=7, color='green', linestyle='--', alpha=0.5, label='100 nM')
    ax.axvline(x=500, color='red', linestyle='--', alpha=0.5, label='Ro5 limit')
    ax.legend(fontsize=8)
    plt.colorbar(sc, ax=ax, label='LE')

    # Plot 2: pIC50 vs cLogP (lipophilic efficiency)
    ax = axes[0, 1]
    sc = ax.scatter(clogp, pic50, c=lle, cmap='RdYlGn', s=80,
                    edgecolors='black', linewidth=0.5)
    ax.set_xlabel('cLogP')
    ax.set_ylabel('pIC50')
    ax.set_title('Potency vs Lipophilicity')
    ax.axvline(x=5, color='red', linestyle='--', alpha=0.5, label='Ro5 limit')
    ax.legend(fontsize=8)
    plt.colorbar(sc, ax=ax, label='LLE')

    # Plot 3: LE vs HAC (size-independent efficiency)
    hac = [m / 14 for m in mw]  # approximate HAC from MW
    ax = axes[0, 2]
    ax.scatter(hac, le, c=pic50, cmap='viridis', s=80,
               edgecolors='black', linewidth=0.5)
    ax.set_xlabel('Heavy Atom Count (approx)')
    ax.set_ylabel('LE (kcal/mol/HA)')
    ax.set_title('Ligand Efficiency vs Size')
    ax.axhline(y=0.3, color='green', linestyle='--', alpha=0.5, label='LE = 0.3')
    ax.axhline(y=0.25, color='orange', linestyle='--', alpha=0.5, label='LE = 0.25')
    ax.legend(fontsize=8)

    # Plot 4: LLE vs cLogP (quality of binding)
    ax = axes[1, 0]
    ax.scatter(clogp, lle, c=pic50, cmap='viridis', s=80,
               edgecolors='black', linewidth=0.5)
    ax.set_xlabel('cLogP')
    ax.set_ylabel('LLE (pIC50 - cLogP)')
    ax.set_title('Binding Quality')
    ax.axhline(y=5, color='green', linestyle='--', alpha=0.5, label='LLE = 5')
    ax.axhline(y=3, color='orange', linestyle='--', alpha=0.5, label='LLE = 3')
    ax.legend(fontsize=8)

    # Plot 5: MW vs cLogP (property space with GSK 4/400)
    ax = axes[1, 1]
    ax.scatter(mw, clogp, c=pic50, cmap='viridis', s=80,
               edgecolors='black', linewidth=0.5)
    ax.set_xlabel('MW (Da)')
    ax.set_ylabel('cLogP')
    ax.set_title('Property Space')
    ax.axvline(x=400, color='red', linestyle='--', alpha=0.3)
    ax.axhline(y=4, color='red', linestyle='--', alpha=0.3)
    ax.fill_between([400, 700], 4, 8, alpha=0.1, color='red',
                    label='GSK 4/400 zone')
    ax.set_xlim(100, 700)
    ax.set_ylim(-1, 8)
    ax.legend(fontsize=8)

    # Plot 6: TPSA vs cLogP (Pfizer 3/75)
    ax = axes[1, 2]
    ax.scatter(tpsa, clogp, c=pic50, cmap='viridis', s=80,
               edgecolors='black', linewidth=0.5)
    ax.set_xlabel('TPSA (A^2)')
    ax.set_ylabel('cLogP')
    ax.set_title('Pfizer 3/75 Analysis')
    ax.axvline(x=75, color='red', linestyle='--', alpha=0.3)
    ax.axhline(y=3, color='red', linestyle='--', alpha=0.3)
    ax.fill_betweenx([3, 8], 0, 75, alpha=0.1, color='red',
                     label='3/75 danger zone')
    ax.legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    return output_path


def plot_optimization_trajectory(rounds, output_path='optimization_trajectory.png'):
    """Plot compound optimization trajectory across rounds.

    Args:
        rounds: list of dicts, each with keys:
            round_name, pic50, mw, clogp, le, lle
        output_path: file path for saved figure
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Optimization Trajectory', fontsize=14, fontweight='bold')

    labels = [r['round_name'] for r in rounds]
    x = range(len(labels))

    # Panel 1: Potency and MW
    ax1 = axes[0]
    color1 = 'tab:blue'
    ax1.set_xlabel('Optimization Round')
    ax1.set_ylabel('pIC50', color=color1)
    ax1.plot(x, [r['pic50'] for r in rounds], 'o-', color=color1, label='pIC50')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(labels, rotation=45, ha='right')

    ax1b = ax1.twinx()
    color2 = 'tab:red'
    ax1b.set_ylabel('MW (Da)', color=color2)
    ax1b.plot(x, [r['mw'] for r in rounds], 's--', color=color2, label='MW')
    ax1b.tick_params(axis='y', labelcolor=color2)
    ax1.set_title('Potency vs Size')

    # Panel 2: LE and LLE
    ax2 = axes[1]
    ax2.plot(x, [r['le'] for r in rounds], 'o-', color='green', label='LE')
    ax2.plot(x, [r['lle'] for r in rounds], 's-', color='purple', label='LLE')
    ax2.axhline(y=0.3, color='green', linestyle='--', alpha=0.4)
    ax2.axhline(y=5, color='purple', linestyle='--', alpha=0.4)
    ax2.set_xlabel('Optimization Round')
    ax2.set_ylabel('Efficiency')
    ax2.set_xticks(list(x))
    ax2.set_xticklabels(labels, rotation=45, ha='right')
    ax2.legend()
    ax2.set_title('Efficiency Tracking')

    # Panel 3: cLogP trajectory
    ax3 = axes[2]
    ax3.plot(x, [r['clogp'] for r in rounds], 'o-', color='orange', label='cLogP')
    ax3.axhline(y=5, color='red', linestyle='--', alpha=0.4, label='Ro5 limit')
    ax3.axhline(y=3, color='orange', linestyle='--', alpha=0.4, label='Optimal ceiling')
    ax3.set_xlabel('Optimization Round')
    ax3.set_ylabel('cLogP')
    ax3.set_xticks(list(x))
    ax3.set_xticklabels(labels, rotation=45, ha='right')
    ax3.legend()
    ax3.set_title('Lipophilicity Control')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    return output_path
```

---

## Evidence Grading

Assign an evidence tier to every data point and recommendation based on data quality and source.

| Tier | Label | Criteria | Typical Sources |
|------|-------|----------|-----------------|
| **T1** | Clinical PK/Safety data | Human clinical pharmacokinetic data, post-marketing safety, approved label information | FDA labels, Phase 2/3 PK results, FAERS, therapeutic drug monitoring data |
| **T2** | In vivo animal data | Preclinical in vivo PK, efficacy, and toxicology studies | Rat/dog PK studies, in vivo efficacy models, GLP tox studies, published animal PK |
| **T3** | In vitro assay data | Measured in vitro properties from validated assays | HLM/RLM CLint, Caco-2, PAMPA, hERG patch clamp, CYP inhibition IC50, plasma protein binding, Ames test |
| **T4** | Computational predictions | In silico predictions without experimental validation | Predicted LogP, TPSA, ADMET models, docking scores, QSAR predictions, rule-based alerts |

### Evidence Grading Rules

1. **Always report the tier** alongside any data point: "HLM CLint = 12 uL/min/mg [T3]" or "Predicted oral bioavailability > 50% [T4]"
2. **Do not mix tiers without noting**: If combining T1 clinical PK with T4 predicted properties, explicitly state which values are measured vs predicted
3. **Tier drives confidence in recommendations**:
   - T1/T2 data: Make definitive recommendations
   - T3 data: Make recommendations with the caveat "pending in vivo confirmation"
   - T4 data: Flag as hypothesis-generating; recommend experimental validation before decision-making
4. **Upgrade path**: T4 predictions should always include a recommendation for which T3 assay to run for validation (e.g., "Predicted high CYP3A4 inhibition [T4] -> recommend CYP3A4 IC50 measurement [T3]")
5. **Conflict resolution**: When tiers conflict (e.g., T4 predicts good permeability but T3 Caco-2 shows poor), always defer to the higher-tier (lower number) data

### Source-to-Tier Mapping for MCP Tools

| MCP Tool | Typical Evidence Tier | Notes |
|----------|----------------------|-------|
| `mcp__drugbank__drugbank_data` | T1-T2 | Clinical PK from approved drugs = T1; preclinical data = T2 |
| `mcp__chembl__chembl_data` (bioactivity) | T3 | Measured in vitro assay data |
| `mcp__chembl__chembl_data` (calculated props) | T4 | Computed descriptors and predictions |
| `mcp__pubchem__pubchem_data` (properties) | T4 | Calculated molecular properties |
| `mcp__pubmed__pubmed_data` | T1-T3 | Depends on study type (clinical = T1, in vitro = T3) |
| `mcp__opentargets__ot_data` | T2-T4 | Integrated evidence, varies by data type |
| `mcp__alphafold__alphafold_data` | T4 | Predicted structures, use for hypothesis generation |
| `mcp__pdb__pdb_data` | T2-T3 | Experimental structures = T2-T3 depending on resolution |

---

## Response Format

When performing medicinal chemistry analysis, structure the response as:

1. **Compound Identity**: Name, SMILES, ChEMBL ID, CID, molecular formula
2. **Property Summary**: MW, cLogP, TPSA, HBD, HBA, RotB in a table
3. **Drug-Likeness Profile**: Results from all applicable filters (Ro5, Veber, Ghose, Egan, lead-likeness, Ro3)
4. **Structural Alerts**: PAINS / toxicophore / reactive metabolite results with specific flags and actions
5. **Efficiency Metrics**: LE, LLE, LELP, BEI, FQ with assessments and comparisons to class benchmarks
6. **ADMET Traffic Light**: Color-coded parameter table with evidence tiers
7. **MPO Score**: Total score with component breakdown (CNS MPO if applicable, Pfizer 3/75, GSK 4/400, desirability MPO)
8. **SAR Context**: Position in series, activity cliffs, productive transformation opportunities
9. **MedChem Score**: 0-100 composite with domain breakdown
10. **Recommendations**: Prioritized optimization actions with evidence tier for each supporting data point
11. **Key Literature**: Relevant publications from PubMed search with evidence tier assignments

## Completeness Checklist

- [ ] Compound identity confirmed with ChEMBL ID, PubChem CID, and SMILES
- [ ] Drug-likeness assessed against all applicable filters (Ro5, Veber, Ghose, Egan)
- [ ] Structural alerts screened (PAINS, Brenk, toxicophores) with specific flags noted
- [ ] Ligand efficiency metrics calculated (LE, LLE, LELP, BEI) with assessment
- [ ] ADMET traffic light table generated with evidence tier for each parameter
- [ ] MPO score calculated (CNS MPO if applicable, Pfizer 3/75, GSK 4/400)
- [ ] SAR context provided (activity cliffs, MMP analysis, R-group exploration)
- [ ] MedChem composite score (0-100) computed with domain breakdown
- [ ] Evidence tier (T1-T4) assigned to every data point and recommendation
- [ ] Prioritized optimization actions listed with supporting evidence
