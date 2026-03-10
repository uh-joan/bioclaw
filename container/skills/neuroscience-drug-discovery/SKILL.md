---
name: neuroscience-drug-discovery
description: "BBB permeability scoring, CNS MPO optimization, receptor occupancy modeling, neuro biomarkers, CNS target validation, neurotoxicity assessment"
---

# Neuroscience Drug Discovery

Specialist skill for CNS drug discovery and development. Covers blood-brain barrier (BBB) permeability prediction, CNS multiparameter optimization (MPO) scoring, receptor occupancy (RO) modeling from PET tracer data, CNS target validation using genetic and expression evidence, neurotoxicity risk assessment (seizure liability, EPS, serotonin syndrome), CNS biomarker strategy (CSF analytes, PET imaging, digital biomarkers), and CNS clinical trial design with appropriate endpoint selection.

CNS drug development has the highest failure rate of any therapeutic area (~90% attrition in Phase II/III), driven by BBB penetration challenges, difficulty demonstrating target engagement in the human brain, reliance on subjective clinical endpoints, and complex disease heterogeneity.

## Report-First Workflow

1. **Create report file immediately**: `[compound]_neuroscience-drug-discovery_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Full drug monographs and compound identity disambiguation → use `drug-research`
- Medicinal chemistry SAR, scaffold hopping, and lead optimization → use `medicinal-chemistry`
- PK/PD modeling and dose optimization beyond CNS-specific RO → use `clinical-pharmacology`
- Biomarker validation and clinical qualification workflows → use `biomarker-discovery`
- Competitive landscape and pipeline intelligence → use `competitive-intelligence`

## Cross-Reference: Other Skills

- **Comprehensive drug monographs, compound disambiguation, full drug profiles** -> use drug-research skill
- **Medicinal chemistry SAR, lead optimization, scaffold hopping** -> use medicinal-chemistry skill
- **PK/PD modeling, dose optimization, compartmental analysis** -> use clinical-pharmacology skill
- **Biomarker identification, validation, clinical qualification** -> use biomarker-discovery skill
- **Competitive landscape, pipeline intelligence, market positioning** -> use competitive-intelligence skill

## Available MCP Tools

### `mcp__drugbank__drugbank_data` (CNS Drug Pharmacology)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search drug database by name or CNS indication | `query`, `limit` |
| `get_drug` | Full drug profile including CNS-relevant PK (BBB penetration, P-gp status) | `drugbank_id` |
| `get_pharmacology` | Mechanism, pharmacodynamics, receptor binding profile | `drugbank_id` |
| `get_targets` | All molecular targets (receptors, enzymes, transporters, ion channels) | `drugbank_id` |

### `mcp__chembl__chembl_data` (CNS Compound SAR & Binding Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_molecule` | Search compounds by name, SMILES, or development code | `query`, `limit` |
| `get_molecule` | Full compound profile (physicochemical properties, drug-likeness) | `chembl_id` |
| `get_activities` | Binding affinity data (Ki, IC50, EC50) against CNS targets | `chembl_id`, `target_id`, `limit` |
| `search_target` | Search CNS targets (receptors, ion channels, enzymes) | `query`, `limit` |

### `mcp__pubmed__pubmed_data` (Neuroscience Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search biomedical literature for neuroscience topics | `query`, `num_results` |
| `fetch_details` | Full article metadata, abstract, MeSH terms | `pmid` |

### `mcp__clinicaltrials__ct_data` (CNS Clinical Trials)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_studies` | Search CNS trials by drug, condition, or endpoint | `query`, `status`, `phase`, `limit` |
| `get_study` | Full trial record (design, endpoints, rating scales, results) | `nct_id` |

### `mcp__fda__fda_data` (Approved CNS Drugs & Safety)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search FDA-approved CNS drugs | `query`, `limit` |
| `get_drug_label` | Full prescribing information (boxed warnings, REMS, neurotoxicity) | `set_id` or `drug_name` |

### `mcp__opentargets__ot_data` (CNS Target-Disease Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_target` | Search CNS drug targets by gene symbol or name | `query`, `size` |
| `get_target_info` | Target details: function, expression, tractability, pathways | `id` (Ensembl ID) |
| `get_associations` | Target-disease evidence scores (genetic, expression, literature) | `targetId`, `diseaseId`, `minScore`, `size` |

### `mcp__alphafold__alphafold_data` (CNS Target Protein Structures)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_prediction` | AlphaFold predicted structure for CNS target protein | `uniprot_id` |
| `search_structures` | Search predicted structures by protein name or gene | `query`, `limit` |

### `mcp__pdb__pdb_data` (Receptor Co-Crystal & Cryo-EM Structures)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_structures` | Search PDB for CNS receptor structures (GPCR, ion channel, transporter) | `query`, `limit` |
| `get_structure` | Full structure details (resolution, ligand, binding site) | `pdb_id` |

### `mcp__kegg__kegg_data` (Neurotransmitter Pathways & Neurodegeneration)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_pathway` | Full pathway details (dopaminergic, serotonergic, GABAergic, glutamatergic) | `pathway_id` |
| `find_pathway` | Search pathways by neurotransmitter system or neurodegenerative disease | `query` |

### `mcp__ensembl__ensembl_data` (CNS Genetic Risk Factors)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_gene_info` | Gene details for CNS targets (location, transcripts, regulation) | `gene_id` |
| `get_variants` | Genetic variants associated with CNS disease risk | `gene_id`, `variant_type` |

### `mcp__hpo__hpo_data` (Neurological Phenotypes)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_hpo_terms` | Search Human Phenotype Ontology for neurological phenotypes | `query` |
| `get_hpo_term` | Detailed phenotype definition, associated genes, diseases | `hpo_id` |

---

## Core Workflows

### Workflow 1: BBB Permeability Assessment

Evaluate whether a compound achieves adequate brain exposure. The BBB is formed by tight junctions between brain endothelial cells with active efflux transporters (P-gp/ABCB1, BCRP/ABCG2, MRP/ABCC).

**Key physicochemical predictors of BBB penetration:**
- Molecular weight < 450 Da (ideally < 400 Da)
- Topological polar surface area (TPSA) < 90 A² (ideally < 70 A²)
- Hydrogen bond donors (HBD) <= 3 (ideally <= 1)
- cLogP between 1.0 and 3.0
- cLogD at pH 7.4 between 1.0 and 3.0
- pKa of most basic center between 7.5 and 10.5
- P-gp efflux ratio < 2 in MDCK-MDR1 assay

**Transport mechanisms:** passive transcellular diffusion (most small-molecule CNS drugs), carrier-mediated transport (LAT1 for L-DOPA, GLUT1 for glucose analogs), receptor-mediated transcytosis (transferrin receptor, insulin receptor for antibody shuttles), adsorptive transcytosis (cationic molecules).

```
1. mcp__chembl__chembl_data(method: "get_molecule", chembl_id: "CHEMBLxxxxx")
   → MW, ALogP, PSA, HBD, HBA, pKa

2. mcp__drugbank__drugbank_data(method: "get_drug", drugbank_id: "DBxxxxx")
   → P-gp substrate/inhibitor status, transporter data

3. Calculate CNS MPO score (see Workflow 2)

4. mcp__drugbank__drugbank_data(method: "search_drugs", query: "THERAPEUTIC_CLASS CNS")
   → Benchmark candidate against approved CNS drug property space

5. mcp__pubmed__pubmed_data(method: "search", query: "COMPOUND blood-brain barrier penetration brain exposure")
   → Published brain-to-plasma ratios, CSF/plasma ratios, PET data

6. mcp__kegg__kegg_data(method: "find_pathway", query: "ABC transporters")
   → BBB efflux transporter interactions
```

**BBB Permeability Decision Matrix:**

| Parameter | High Confidence | Moderate Risk | Low Confidence |
|-----------|----------------|---------------|----------------|
| MW | < 400 | 400-500 | > 500 |
| TPSA | < 70 A² | 70-90 A² | > 90 A² |
| HBD | 0-1 | 2-3 | > 3 |
| cLogP | 1.5-3.0 | 1.0-1.5 or 3.0-4.0 | < 1.0 or > 4.0 |
| P-gp ER | < 2 | 2-3 | > 3 |
| CNS MPO | >= 4.5 | 3.5-4.5 | < 3.5 |

---

### Workflow 2: CNS MPO Scoring

Pfizer's 6-parameter CNS MPO (Wager et al., ACS Chem Neurosci 2010). Each parameter has a monotonic desirability function (0-1). Total score 0-6.

| Parameter | T0 (desirability=1) | T1 (desirability=0) | Direction |
|-----------|---------------------|---------------------|-----------|
| CLogP | <= 3 | >= 5 | Lower better |
| CLogD | <= 2 | >= 4 | Lower better |
| MW | <= 360 | >= 500 | Lower better |
| TPSA | <= 40 | >= 120 | Lower better |
| HBD | <= 0.5 | >= 3.5 | Lower better |
| pKa | <= 8 | >= 10 | Lower better |

**Score interpretation:** >= 4 desirable (74% of marketed CNS drugs), >= 5 excellent, < 4 significant BBB risk, < 3 very unlikely viable.

```
1. mcp__chembl__chembl_data(method: "get_molecule", chembl_id: "CHEMBLxxxxx")
   → MW, ALogP, PSA, HBD; use computational pKa if not available

2. Calculate desirability for each parameter (see Python template)

3. mcp__chembl__chembl_data(method: "search_molecule", query: "DRUG_CLASS")
   → CNS MPO for approved drugs in class; report percentile ranking

4. Flag parameters with desirability < 0.5 → medicinal chemistry optimization targets
```

---

### Workflow 3: Receptor Occupancy Modeling

RO is the gold standard for CNS target engagement. Fundamental equation: `RO(%) = Cp_free / (Cp_free + Kd) * 100`. For CNS: `RO(%) = Cu_brain / (Cu_brain + Ki_in_vivo) * 100`.

**Key PET tracers:**

| Target | PET Tracer | Indication |
|--------|-----------|------------|
| D2/D3 | [11C]raclopride, [18F]fallypride | Schizophrenia, Parkinson's |
| 5-HT1A | [11C]WAY-100635 | Depression, anxiety |
| 5-HT2A | [18F]altanserin, [11C]MDL 100907 | Schizophrenia, psychedelics |
| SERT | [11C]DASB | Depression (SSRI dosing) |
| DAT | [11C]PE2I, [123I]FP-CIT | Parkinson's, ADHD |
| mGluR5 | [11C]ABP688, [18F]FPEB | Depression, addiction |
| TSPO | [11C]PBR28 | Neuroinflammation |
| SV2A | [11C]UCB-J | Synaptic density |
| Tau | [18F]flortaucipir | Alzheimer's (tau) |
| Amyloid | [11C]PiB, [18F]florbetapir | Alzheimer's (amyloid) |
| GABAA-BZD | [11C]flumazenil | Epilepsy, anxiety |

**RO-Efficacy benchmarks:** D2 antagonist 60-80% (>80% causes EPS), SERT >80% (SSRIs), 5-HT2A >60% (atypical antipsychotics), AChE 30-60% (donepezil), MAO-B >80% (selegiline).

```
1. mcp__chembl__chembl_data(method: "get_activities", chembl_id: "CHEMBLxxxxx", target_id: "TARGET_ID")
   → Ki, Kd values (use Ki or Kd, NOT IC50, for RO calculations)

2. mcp__drugbank__drugbank_data(method: "get_drug", drugbank_id: "DBxxxxx")
   → Cmax, protein binding, half-life → calculate fu = 1 - protein_binding

3. mcp__pubmed__pubmed_data(method: "search", query: "COMPOUND PET receptor occupancy human")
   → Published PET RO data at clinical doses

4. Model dose-RO using Emax equation (see Python template)
   → Identify dose for target RO range

5. mcp__fda__fda_data(method: "get_drug_label", drug_name: "REFERENCE_DRUG")
   → Approved dose and known RO for benchmarking
```

---

### Workflow 4: CNS Target Validation

Multi-evidence framework: human genetics (strongest), brain expression, pharmacological tools, preclinical in vivo, in vitro/cellular.

**Key CNS target families:**

| Class | Examples | Disease Areas |
|-------|----------|---------------|
| GPCRs | D1-D5, 5-HT1-7, mGluR1-8, M1-M5, CB1/CB2 | Schizophrenia, depression, Parkinson's, pain |
| Ion channels | NMDA (GluN2A/B), GABAA, Nav1.x, Kv7, TRPV1 | Epilepsy, pain, depression, anxiety |
| Transporters | SERT, DAT, NET, VMAT2, GAT1 | Depression, ADHD, Parkinson's |
| Enzymes | AChE, MAO-A/B, COMT, IDO1, PDE4/10A | Alzheimer's, Parkinson's, depression |
| Kinases | LRRK2, CDK5, GSK3B, DYRK1A, RIPK1 | Parkinson's, Alzheimer's, ALS |
| Aggregation | alpha-synuclein, tau, amyloid-beta, TDP-43 | Neurodegeneration |
| Immune/glial | TREM2, CD33, CSF1R, TSPO, P2X7 | Neuroinflammation, Alzheimer's |

**KEGG neurotransmitter pathway IDs:** Dopaminergic (hsa04728), Serotonergic (hsa04726), GABAergic (hsa04727), Glutamatergic (hsa04724), Cholinergic (hsa04725), Alzheimer (hsa05010), Parkinson (hsa05012), Huntington (hsa05016), ALS (hsa05014).

```
1. mcp__opentargets__ot_data(method: "search_target", query: "TARGET_GENE") → Ensembl ID
   mcp__opentargets__ot_data(method: "get_associations", targetId: "ENSG...", diseaseId: "EFO_...")
   → Genetic association score, GWAS loci, Mendelian disease links

2. mcp__ensembl__ensembl_data(method: "get_gene_info", gene_id: "ENSG...")
   mcp__opentargets__ot_data(method: "get_target_info", id: "ENSG...")
   → Verify brain expression (cortex, hippocampus, substantia nigra, striatum, cerebellum)

3. mcp__pdb__pdb_data(method: "search_structures", query: "TARGET_NAME")
   mcp__alphafold__alphafold_data(method: "get_prediction", uniprot_id: "UNIPROTID")
   → Structural data for binding site analysis, druggability

4. mcp__chembl__chembl_data(method: "search_target", query: "TARGET_NAME") → ChEMBL target ID
   mcp__chembl__chembl_data(method: "get_activities", target_id: "CHEMBL_TARGET_ID", limit: 50)
   → Known ligands, affinities, selectivity data

5. mcp__ensembl__ensembl_data(method: "get_variants", gene_id: "ENSG...")
   mcp__pubmed__pubmed_data(method: "search", query: "TARGET_GENE GWAS CNS_DISEASE")
   → Genetic risk variants, GWAS publications

6. mcp__kegg__kegg_data(method: "find_pathway", query: "NEUROTRANSMITTER_SYSTEM")
   → Pathway position of target

7. mcp__hpo__hpo_data(method: "search_hpo_terms", query: "NEUROLOGICAL_PHENOTYPE")
   mcp__hpo__hpo_data(method: "get_hpo_term", hpo_id: "HP:0000xxx")
   → Standardized phenotypes, associated genes
```

---

### Workflow 5: Neurotoxicity Assessment

**Major CNS safety liabilities:**

**Seizure liability:** Risk factors include GABAA antagonism, glutamate agonism, high brain penetration with low MW. Check GABAA binding (CHEMBL2093872), NMDA binding (CHEMBL2095181), class history via FDA labels and PubMed.

**Serotonin syndrome:** Risk with serotonergic combinations (SSRIs, SNRIs, MAOIs, triptans, tramadol). Assess SERT, 5-HT1A, 5-HT2A, MAO-A/B activity via ChEMBL. Check DDI warnings via DrugBank and FDA labels.

**EPS/Tardive dyskinesia:** D2 antagonism with RO > 80%. Calculate D2 RO at therapeutic doses. 5-HT2A/D2 Ki ratio < 1 suggests atypical profile (lower EPS). Check clinical EPS rates in FDA labels.

**Cognitive impairment:** Anticholinergic burden (M1 binding, CHEMBL211), antihistaminic sedation (H1 binding, CHEMBL231). Review cognitive safety literature.

**Suicidality:** FDA boxed warning for antidepressants in patients under 25. Check label requirements and published analyses.

**QTc prolongation:** hERG channel blockade risk. Many CNS drugs have cardiac warnings. Check hERG IC50 relative to therapeutic Cmax (safety margin > 30x desirable). Review TQT study results in FDA labels.

**Abuse potential / dependence:** Schedule assessment for CNS-active compounds. Evaluate binding to mu-opioid receptor, GABAA-BZD site, dopamine reward pathways. Check DEA scheduling and FDA abuse-deterrent labeling requirements.

**ARIA (amyloid-related imaging abnormalities):** Specific to anti-amyloid antibodies. ARIA-E (edema) and ARIA-H (hemorrhage). Correlates with amyloid removal rate, APOE4 status, and dose intensity. Monitor with serial MRI.

```
For each liability:
1. mcp__chembl__chembl_data(method: "get_activities", chembl_id: "CHEMBLxxxxx", target_id: "RELEVANT_TARGET")
   → Off-target binding relevant to safety concern

2. mcp__fda__fda_data(method: "get_drug_label", drug_name: "CLASS_REFERENCE")
   → Warnings, boxed warnings, clinical safety data

3. mcp__pubmed__pubmed_data(method: "search", query: "DRUG_NAME SAFETY_CONCERN")
   → Published safety studies
```

---

### Workflow 6: CNS Biomarkers

**CSF biomarkers:**

| Biomarker | Disease | Application |
|-----------|---------|-------------|
| Abeta42, Abeta42/40 ratio | Alzheimer's | Patient selection, target engagement |
| p-tau181/217 | Alzheimer's | Tau pathology staging |
| NfL (neurofilament light) | Multiple | Axonal damage, neurodegeneration |
| alpha-synuclein SAA | Parkinson's/DLB | Synucleinopathy confirmation |
| GFAP | TBI, Alzheimer's | Astrocyte activation |
| 5-HIAA, HVA | Depression, Schizophrenia | Serotonin/dopamine metabolism |

**PET imaging:** See Workflow 3 for tracers. Provides target engagement (RO), target density (SV2A), pathology burden (amyloid/tau-PET), neuroinflammation (TSPO-PET).

**EEG/digital biomarkers:** qEEG (pharmaco-EEG signatures), P300 ERP (cognitive processing), MMN (sensory gating in schizophrenia), sleep PSG (hypnotics), actigraphy (circadian), digital speech analysis (motor/cognitive).

```
1. mcp__pubmed__pubmed_data(method: "search", query: "CNS_DISEASE biomarker CSF")
   → Published biomarker studies

2. mcp__fda__fda_data(method: "search_drugs", query: "biomarker CNS_DISEASE")
   → FDA-qualified biomarkers

3. mcp__pubmed__pubmed_data(method: "search", query: "DRUG_TARGET target engagement biomarker CSF PET")
   → Target-specific TE biomarker strategies
```

---

### Workflow 7: CNS Clinical Trial Design

**Clinical endpoints by indication:**

| Indication | Primary Endpoint | Scale | MCID |
|------------|-----------------|-------|------|
| Alzheimer's (cognition) | ADAS-Cog 11/13 | 0-70/85 | 2-4 pts |
| Alzheimer's (global) | CDR-SB | 0-18 | 1-2 pts |
| Schizophrenia | PANSS total | 30-210 | 15-20 pts |
| Depression | HAM-D 17 / MADRS | 0-52 / 0-60 | 3 pts / 2 pts |
| Parkinson's motor | MDS-UPDRS Part III | 0-132 | 3.25 pts |
| Epilepsy | Seizure frequency | % change | >=50% responder |
| ALS | ALSFRS-R | 0-48 | 20% slope reduction |
| Pain (neuropathic) | NRS | 0-10 | 2 pts / 30% |
| ADHD | ADHD-RS-IV | 0-54 | 6-8 pts |
| Migraine | Monthly migraine days | Days | >=50% responder |

**Design best practices:** Centralized raters, SPCD for high-placebo indications, biomarker enrichment (amyloid-PET for AD, DAT-SPECT for PD), PK sampling for exposure-response, PET sub-study for TE, adaptive dose-finding (MCP-Mod) in Phase II.

```
1. mcp__clinicaltrials__ct_data(method: "search_studies", query: "CNS_DISEASE phase 3", phase: "3", limit: 20)
   → Endpoints used in approved drug trials

2. mcp__pubmed__pubmed_data(method: "search", query: "CNS_DISEASE placebo response clinical trial meta-analysis")
   → Historical placebo response rates

3. mcp__clinicaltrials__ct_data(method: "search_studies", query: "CNS_DISEASE enrichment biomarker")
   → Biomarker-enriched designs

4. mcp__fda__fda_data(method: "get_drug_label", drug_name: "APPROVED_DRUG")
   → Clinical studies section: endpoints that supported approval
```

---

## CNS Drug Candidate Scoring (0-100)

### 1. BBB Permeability / CNS MPO (25 points)

| Score | Criteria |
|-------|----------|
| 22-25 | CNS MPO >= 5.0, confirmed brain penetration (PET/CSF), P-gp ER < 2 |
| 17-21 | CNS MPO 4.0-4.9, properties within CNS space, no P-gp flags |
| 12-16 | CNS MPO 3.5-3.9, borderline parameters, moderate P-gp concern |
| 6-11 | CNS MPO 3.0-3.4, multiple parameters outside CNS space |
| 0-5 | CNS MPO < 3.0, PSA > 120, MW > 500, known P-gp substrate |

### 2. Target Engagement Evidence (20 points)

| Score | Criteria |
|-------|----------|
| 18-20 | Clinical PET RO data, CSF biomarker changes, dose-RO-efficacy correlation |
| 13-17 | Preclinical PET or ex vivo RO, validated TE biomarker |
| 8-12 | In vitro binding Ki < 10 nM, selectivity > 30x vs off-targets |
| 4-7 | In vitro binding only, limited selectivity |
| 0-3 | No direct binding data, TE inferred from phenotype |

### 3. Safety / Neurotoxicity Risk (20 points)

| Score | Criteria |
|-------|----------|
| 18-20 | Clean CNS safety panel, clinical safety confirmed |
| 13-17 | Minor liabilities manageable with titration, no class black box |
| 8-12 | Moderate liability (mild sedation/EPS at high RO), requires monitoring |
| 4-7 | Significant liability (seizure risk supratherapeutic, serotonin syndrome with combos) |
| 0-3 | Dose-limiting CNS toxicity (severe EPS, seizures at therapeutic dose) |

### 4. Efficacy Translation Confidence (20 points)

| Score | Criteria |
|-------|----------|
| 18-20 | Phase II/III POC with significant primary endpoint, effect > MCID |
| 13-17 | Phase I/II positive PD signal, strong genetics (GWAS + Mendelian) |
| 8-12 | Robust preclinical efficacy in multiple validated models, genetic support |
| 4-7 | Single model efficacy, limited translational validation |
| 0-3 | In vitro only, no animal efficacy, no genetic link |

### 5. Clinical Feasibility (15 points)

| Score | Criteria |
|-------|----------|
| 13-15 | Validated endpoint, regulatory precedent, biomarker enrichment possible |
| 9-12 | Established endpoint but high placebo response, feasible duration |
| 5-8 | Subjective endpoints, long duration >18 months, difficult recruitment |
| 2-4 | No validated endpoint, no regulatory precedent |
| 0-1 | Requires novel endpoint development and regulatory qualification |

### Score Interpretation

| Total | Rating | Recommendation |
|-------|--------|---------------|
| 80-100 | Excellent | Prioritize for clinical development |
| 65-79 | Good | Viable — proceed with mitigation plan |
| 50-64 | Moderate | Address BBB/safety/translation gaps before advancing |
| 35-49 | Weak | Consider backup compound or target re-evaluation |
| 0-34 | Poor | Reassess target or modality |

---

## Python Code Templates

### CNS MPO Desirability Function

```python
def cns_mpo_desirability(value, low, high):
    """Monotonic linear desirability: 1 at <=low, 0 at >=high."""
    if value <= low: return 1.0
    if value >= high: return 0.0
    return 1.0 - (value - low) / (high - low)

def calculate_cns_mpo(clogp, clogd, mw, tpsa, hbd, pka):
    """Pfizer CNS MPO score (Wager et al., ACS Chem Neurosci 2010). Returns 0-6."""
    scores = {
        "CLogP": cns_mpo_desirability(clogp, 3, 5),
        "CLogD": cns_mpo_desirability(clogd, 2, 4),
        "MW": cns_mpo_desirability(mw, 360, 500),
        "TPSA": cns_mpo_desirability(tpsa, 40, 120),
        "HBD": cns_mpo_desirability(hbd, 0.5, 3.5),
        "pKa": cns_mpo_desirability(pka, 8, 10),
    }
    scores["Total"] = sum(scores.values())
    return scores

# Example: Donepezil
result = calculate_cns_mpo(clogp=4.28, clogd=2.36, mw=379.49, tpsa=38.77, hbd=0, pka=8.82)
# Expected Total ~4.5 (desirable CNS profile)
```

### Receptor Occupancy Curve (Emax Model)

```python
import numpy as np
import matplotlib.pyplot as plt

def plot_ro_curve(kd, cmax_free, drug_name, target, therapeutic_ro=(60, 80)):
    """Plot concentration-RO curve with therapeutic window."""
    conc = np.logspace(np.log10(kd * 0.01), np.log10(kd * 100), 500)
    ro = conc / (conc + kd) * 100
    ro_at_cmax = cmax_free / (cmax_free + kd) * 100

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.semilogx(conc, ro, 'b-', lw=2, label=f'{drug_name} (Kd={kd:.1f} nM)')
    ax.axhspan(therapeutic_ro[0], therapeutic_ro[1], alpha=0.15, color='green',
               label=f'Therapeutic window ({therapeutic_ro[0]}-{therapeutic_ro[1]}% RO)')
    ax.plot(cmax_free, ro_at_cmax, 'ro', ms=10)
    ax.annotate(f'Cmax_free={cmax_free:.1f} nM\nRO={ro_at_cmax:.1f}%',
                xy=(cmax_free, ro_at_cmax), xytext=(cmax_free*3, ro_at_cmax-15),
                arrowprops=dict(arrowstyle='->'), color='red')
    ax.set_xlabel('Free Concentration (nM)'); ax.set_ylabel('RO (%)')
    ax.set_title(f'{drug_name} {target} Receptor Occupancy'); ax.set_ylim(0, 105)
    ax.legend(); ax.grid(True, alpha=0.3); plt.tight_layout()
    plt.savefig(f'{drug_name}_{target}_RO.png', dpi=150)
    return ro_at_cmax

# Example: Haloperidol D2 (Ki=1.4 nM, free Cmax ~2.8 nM at 5 mg)
plot_ro_curve(kd=1.4, cmax_free=2.8, drug_name="Haloperidol", target="D2")
```

### BBB Likelihood Scoring

```python
def bbb_likelihood(mw, tpsa, hbd, clogp, pgp_er=None, cns_mpo=None):
    """Composite BBB likelihood score (0-100). Weighted: MW 25, TPSA 25, HBD 20, CLogP 15, P-gp 10, MPO bonus 5."""
    s = {}
    s["MW"] = max(0, 25 - max(0, mw - 350) / 6)
    s["TPSA"] = max(0, 25 - max(0, tpsa - 60) / 1.2)
    s["HBD"] = {0: 20, 1: 18, 2: 12, 3: 5}.get(int(hbd), 0)
    s["CLogP"] = 15 if 1.0 <= clogp <= 3.0 else (10 if 0 <= clogp <= 4.0 else (5 if -1 <= clogp <= 5.0 else 0))
    s["P-gp"] = (10 if pgp_er < 2 else (5 if pgp_er < 3 else 0)) if pgp_er is not None else 5
    s["MPO_bonus"] = (5 if cns_mpo >= 5 else (3 if cns_mpo >= 4 else 0)) if cns_mpo is not None else 0
    s["Total"] = sum(s.values())
    return s

# Example: Memantine (MW=179.3, TPSA=26, HBD=2, CLogP=2.07, P-gp ER=1.1, MPO=5.2)
result = bbb_likelihood(179.3, 26.0, 2, 2.07, pgp_er=1.1, cns_mpo=5.2)
# Expected: ~90+ (excellent BBB penetration)
```

### PK/RO Simulation for Dose Selection

```python
import numpy as np
import matplotlib.pyplot as plt

def simulate_pk_ro(dose_mg, f_oral, vd_L, ka_hr, ke_hr, fu, kd_nM, mw,
                   drug_name="Compound", target="Target", ro_window=(60, 80), hours=24):
    """One-compartment oral PK with RO prediction over time."""
    t = np.linspace(0.01, hours, 1000)
    dose_nM_vd = (dose_mg * 1e6 / mw) / (vd_L * 1000)
    c_total = (f_oral * dose_nM_vd * ka_hr) / (ka_hr - ke_hr) * (np.exp(-ke_hr*t) - np.exp(-ka_hr*t))
    c_free = c_total * fu
    ro = c_free / (c_free + kd_nM) * 100

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    ax1.plot(t, c_total, 'b-', lw=2, label='Total')
    ax1.plot(t, c_free, 'b--', lw=2, label='Free')
    ax1.set_ylabel('Concentration (nM)'); ax1.legend(); ax1.grid(True, alpha=0.3)
    ax1.set_title(f'{drug_name} {dose_mg} mg PO — PK/RO Simulation')

    ax2.plot(t, ro, 'r-', lw=2)
    ax2.axhspan(ro_window[0], ro_window[1], alpha=0.15, color='green',
                label=f'Target RO ({ro_window[0]}-{ro_window[1]}%)')
    ax2.set_xlabel('Time (hr)'); ax2.set_ylabel(f'{target} RO (%)')
    ax2.set_ylim(0, 105); ax2.legend(); ax2.grid(True, alpha=0.3)
    plt.tight_layout(); plt.savefig(f'{drug_name}_{dose_mg}mg_PKRO.png', dpi=150)

    time_above = np.sum(ro >= ro_window[0]) / len(t) * hours
    return {"Cmax_free_nM": round(np.max(c_free), 1), "RO_max_%": round(np.max(ro), 1),
            "Time_above_target_RO_hr": round(time_above, 1), "t_half_hr": round(0.693/ke_hr, 1)}

# Example: Risperidone 2 mg, D2 RO
simulate_pk_ro(2, 0.70, 100, 1.5, 0.23, 0.10, 3.3, 410.49, "Risperidone", "D2")
```

---

## Evidence Grading

| Tier | Label | Criteria | Sources |
|------|-------|----------|---------|
| **T1** | Clinical CNS endpoints | Phase II/III with validated CNS endpoints (ADAS-Cog, PANSS, HAM-D, UPDRS), clinical PET RO, CSF biomarker changes | ClinicalTrials.gov, FDA labels, published RCTs |
| **T2** | Preclinical in vivo CNS | Validated CNS animal models (EAE, 6-Hz, forced swim, MPTP, transgenic AD), in vivo brain PK, ex vivo RO | PubMed preclinical, DrugBank pharmacology |
| **T3** | In vitro BBB/binding | MDCK-MDR1, PAMPA-BBB, P-gp efflux, receptor binding Ki/Kd, functional assays, brain organoids | ChEMBL bioactivity, published in vitro |
| **T4** | Computational | In silico BBB prediction, CNS MPO, docking, QSAR, AI-predicted affinity, pathway inference | Computational tools, Open Targets text mining |

### Fallback Chains

```
BBB penetration:   Clinical PET/CSF (T1) → In vivo brain PK (T2) → PAMPA-BBB/MDCK (T3) → CNS MPO (T4)
Target engagement: Clinical PET RO (T1) → Ex vivo RO/CSF TE (T2) → In vitro Ki (T3) → Docking (T4)
Efficacy:          Phase II/III endpoint (T1) → Validated animal model (T2) → In vitro functional (T3) → Pathway (T4)
Safety:            FDA label/clinical AEs (T1) → In vivo tox (T2) → Safety panel (T3) → Structural alerts (T4)
Genetic evidence:  GWAS+Mendelian (T1) → GWAS alone (T2) → eQTL/expression (T3) → Pathway membership (T4)
```

---

## Multi-Agent Workflow Examples

**"Evaluate a novel NMDA receptor modulator for treatment-resistant depression"**
1. Neuroscience Drug Discovery → CNS MPO scoring, BBB assessment, NMDA RO modeling, neurotoxicity (seizure/dissociation risk), HAM-D/MADRS endpoint selection
2. Drug Research → Full compound monograph with identity disambiguation across databases
3. Medicinal Chemistry → SAR around GluN2B subunit selectivity, lead optimization strategies
4. Clinical Pharmacology → PK/PD modeling, first-in-human dose selection from preclinical NOAEL
5. Competitive Intelligence → NMDA modulator pipeline analysis (esketamine, rapastinel, SAGE-718, apimostinel)

**"Assess LRRK2 target validation for Parkinson's disease"**
1. Neuroscience Drug Discovery → Full target validation workflow (GWAS evidence, brain expression in substantia nigra, druggability from kinase domain structures, existing pharmacology)
2. Biomarker Discovery → LRRK2-specific biomarkers (pRab10 in exosomes, urinary bis(monoacylglycero)phosphate, CSF LRRK2 activity)
3. Drug Research → Review of LRRK2 inhibitors in development (DNL201, BIIB122/LY3884961, MLi-2)
4. Clinical Pharmacology → Dose selection strategy using peripheral biomarker (pRab10 inhibition) as bridge to brain PET engagement

**"Design a Phase II trial for a 5-HT2A agonist psychedelic therapy in MDD"**
1. Neuroscience Drug Discovery → 5-HT2A RO modeling, serotonin syndrome risk assessment, CNS clinical trial design with HAM-D/MADRS endpoints, placebo response mitigation
2. Clinical Pharmacology → PK/PD for session-based dosing (single or few administrations), active metabolite assessment
3. Biomarker Discovery → EEG biomarkers for psychedelic response prediction, BDNF as pharmacodynamic marker, 5-HT2A occupancy via PET
4. Competitive Intelligence → Psychedelic therapy landscape (psilocybin, MDMA, DMT, arketamine, 5-MeO-DMT)

**"Evaluate BBB penetration strategy for an anti-amyloid antibody"**
1. Neuroscience Drug Discovery → BBB transport mechanisms (transferrin receptor shuttle, receptor-mediated transcytosis engineering), amyloid PET for target engagement confirmation
2. Drug Research → Monograph and class comparison for aducanumab, lecanemab, donanemab
3. Biomarker Discovery → Amyloid PET (florbetapir/flutemetamol), CSF Abeta42/40 ratio, plasma p-tau217 as surrogate endpoints
4. Clinical Pharmacology → Antibody PK modeling, brain Cmax estimation from CSF sampling, dose-ARIA relationship

**"Score a CNS drug candidate portfolio for investment decision"**
1. Neuroscience Drug Discovery → Apply CNS Drug Candidate Scoring (0-100) to each compound in portfolio, generate comparative dashboard with BBB, TE, safety, efficacy, and feasibility subscores
2. Competitive Intelligence → Market analysis and competitive positioning for each indication area
3. Clinical Pharmacology → PK/PD comparison across portfolio, dose optimization feasibility
4. Drug Research → Individual drug profiles for portfolio compounds, evidence tier assessment

## Completeness Checklist

- [ ] BBB permeability assessed with physicochemical parameters and P-gp efflux status
- [ ] CNS MPO score calculated (0-6) with per-parameter desirability breakdown
- [ ] Receptor occupancy modeled with Kd, free concentration, and dose-RO curve
- [ ] CNS target validation performed with genetics, brain expression, and druggability evidence
- [ ] Neurotoxicity assessment covers seizure liability, EPS, serotonin syndrome, and QTc risk
- [ ] Biomarker strategy defined (CSF analytes, PET tracers, digital biomarkers)
- [ ] Clinical trial design includes validated endpoints and placebo response mitigation
- [ ] CNS Drug Candidate Score calculated (0-100) with all 5 subscores
- [ ] All evidence graded T1-T4 with fallback chains documented
- [ ] Report file verified: no `[Analyzing...]` placeholders remain

**"Investigate neurotoxicity signals for a marketed CNS drug"**
1. Neuroscience Drug Discovery → Comprehensive neurotoxicity assessment (seizure, EPS, serotonin syndrome, cognitive impairment), dose-RO-toxicity correlation
2. Drug Research → Full safety profile from FDA labels, FAERS, DrugBank
3. Biomarker Discovery → Safety biomarkers (QTc, EEG for seizure risk, cognitive testing batteries)
4. Clinical Pharmacology → Exposure-safety relationship, special population dose adjustment recommendations
