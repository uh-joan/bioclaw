---
name: clinical-pharmacology
description: "PK/PD modeling, dose optimization, first-in-human dose selection, therapeutic drug monitoring, drug-drug interaction prediction"
---

# Clinical Pharmacology

Specialist skill for pharmacokinetic/pharmacodynamic (PK/PD) analysis, dose optimization, and translational pharmacology. This skill provides structured workflows for extracting PK parameters from regulatory and literature sources, predicting first-in-human doses using NOAEL-based and MABEL-based approaches, evaluating drug-drug interaction risk through CYP and transporter analysis, designing therapeutic drug monitoring strategies for narrow therapeutic index drugs, and performing population PK-informed dose adjustments for special populations. All analyses follow ICH E4/E5/M3 guidance and FDA/EMA dose-finding recommendations. Outputs are quantitative, citation-backed, and structured for integration with downstream drug-research and adverse-event-detection workflows.

## Report-First Workflow

1. **Create report file immediately**: `clinical_pharmacology_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Comprehensive drug monographs and compound profiles → use `drug-research`
- Post-market adverse event signal detection and FAERS analysis → use `adverse-event-detection`
- SAR optimization, lead compound design, and medicinal chemistry → use `medicinal-chemistry`
- Biomarker identification, qualification, and clinical utility assessment → use `biomarker-discovery`
- Pharmacogenomic variant interpretation and CYP polymorphism dosing → use `pharmacogenomics-specialist`
- FDA regulatory strategy, labeling, and Orange Book analysis → use `fda-consultant`
- Drug-drug interaction mechanistic evaluation → use `drug-interaction-analyst`
- Clinical trial protocol design and dose-escalation strategies → use `clinical-trial-protocol-designer`

---

## Available MCP Tools

### `mcp__drugbank__drugbank_data` (Drug PK Data & Interactions)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search drugs by name or synonym | `query`, `limit` |
| `get_drug` | Full drug profile including PK parameters, metabolism, half-life | `drugbank_id` |
| `get_interactions` | Drug-drug interactions with severity and mechanism | `drugbank_id`, `limit` |
| `get_pharmacology` | Absorption, distribution, metabolism, excretion (ADME) data | `drugbank_id` |
| `get_targets` | Molecular targets, enzymes, carriers, transporters | `drugbank_id` |

**Example: Retrieve PK profile for warfarin**

```
mcp__drugbank__drugbank_data({
  method: "search_drugs",
  query: "warfarin"
})

mcp__drugbank__drugbank_data({
  method: "get_pharmacology",
  drugbank_id: "DB00682"
})

mcp__drugbank__drugbank_data({
  method: "get_targets",
  drugbank_id: "DB00682"
})
```

### `mcp__fda__fda_data` (FDA Labeling & Approved Dosing)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search FDA drug database by name or active ingredient | `query`, `limit` |
| `get_drug_label` | Full prescribing information: clinical pharmacology section, dosing, PK tables | `set_id` or `drug_name` |
| `search_adverse_events` | FAERS adverse event reports for safety-PK correlation | `drug_name`, `limit`, `serious` |

**Example: Extract clinical pharmacology from FDA label**

```
mcp__fda__fda_data({
  method: "search_drugs",
  query: "rivaroxaban"
})

mcp__fda__fda_data({
  method: "get_drug_label",
  drug_name: "rivaroxaban"
})
```

The `clinical_pharmacology` section of the FDA label contains PK parameter tables (Cmax, Tmax, AUC, t1/2), food effect data, special population PK, and DDI study results.

### `mcp__clinicaltrials__ct_data` (PK/PD Clinical Studies)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_studies` | Search ClinicalTrials.gov for PK/PD studies | `query`, `status`, `phase`, `limit` |
| `get_study` | Full study record including endpoints, dosing arms, results | `nct_id` |

**Example: Find Phase I PK studies for a compound**

```
mcp__clinicaltrials__ct_data({
  method: "search_studies",
  query: "pharmacokinetics AND dabrafenib",
  phase: "Phase 1",
  limit: 20
})

mcp__clinicaltrials__ct_data({
  method: "get_study",
  nct_id: "NCT01677741"
})
```

### `mcp__pubmed__pubmed_data` (PK/PD Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search PubMed for PK/PD publications | `keywords`, `num_results` |
| `fetch_details` | Full article metadata including abstract | `pmid` |

**Example: Find population PK publications**

```
mcp__pubmed__pubmed_data({
  method: "search",
  keywords: "population pharmacokinetics osimertinib nonlinear mixed effects",
  num_results: 15
})

mcp__pubmed__pubmed_data({
  method: "fetch_details",
  pmid: "29876543"
})
```

### `mcp__opentargets__ot_data` (Target-Drug Relationships)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drug` | Find drug records by name | `query` |
| `get_drug_info` | Drug mechanism, linked targets, indications | `drug_id` |

**Example: Identify all targets for imatinib**

```
mcp__opentargets__ot_data({
  method: "search_drug",
  query: "imatinib"
})

mcp__opentargets__ot_data({
  method: "get_drug_info",
  drug_id: "CHEMBL941"
})
```

### `mcp__chembl__chembl_data` (In Vitro PK & Bioactivity)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_molecule` | Search molecules by name, SMILES, or ChEMBL ID | `query`, `limit` |
| `get_molecule` | Full molecule record including physicochemical properties | `chembl_id` |
| `get_activities` | Bioactivity data: IC50, Ki, EC50, CYP inhibition assays | `chembl_id`, `target_id`, `limit` |
| `get_assays` | Assay descriptions and conditions for PK-relevant assays | `chembl_id`, `assay_type` |

**Example: Retrieve CYP inhibition data**

```
mcp__chembl__chembl_data({
  method: "search_molecule",
  query: "ketoconazole"
})

mcp__chembl__chembl_data({
  method: "get_activities",
  chembl_id: "CHEMBL75",
  target_id: "CHEMBL3397",
  limit: 50
})
```

### `mcp__clinpgx__clinpgx_data` (PharmGKB / ClinPGx — Pharmacogenomic Dosing)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_gene_drug_pairs` | All gene-drug pair guidelines — PGx-informed dosing recommendations | `gene`, `drug` |
| `get_guidelines` | CPIC and DPWG dose adjustment guidelines for gene-drug pairs | `source`, `gene` |
| `get_clinical_annotations` | Clinical annotations linking PGx evidence to drug response | `gene` |
| `get_drug_labels` | FDA/EMA pharmacogenomic drug labeling (required/recommended testing) | `drug` |

#### ClinPGx Workflow: Pharmacogenomic Dose Adjustments

Check ClinPGx for pharmacogenomic dose adjustments before finalizing dosing recommendations:

```
1. Query gene-drug pair guidelines for the target drug:
   mcp__clinpgx__clinpgx_data(method="get_gene_drug_pairs", drug="drug_name")
   → Identify all PGx genes with dosing implications

2. Get CPIC dosing guidelines:
   mcp__clinpgx__clinpgx_data(method="get_guidelines", source="CPIC", gene="CYP2D6")
   → Phenotype-specific dose adjustments (PM, IM, NM, UM)

3. Check clinical annotations for evidence strength:
   mcp__clinpgx__clinpgx_data(method="get_clinical_annotations", gene="CYP2D6")
   → Level of evidence for PGx-guided dosing

4. Review FDA/EMA labeling for PGx requirements:
   mcp__clinpgx__clinpgx_data(method="get_drug_labels", drug="drug_name")
   → Mandatory vs recommended PGx testing before prescribing

5. Integrate PGx dosing adjustment into final dose recommendation
```

### `mcp__hmdb__hmdb_data` (Drug Metabolite Identification & Concentrations)

Use HMDB to identify drug metabolites, retrieve active metabolite concentration ranges in biofluids, and map metabolic pathways relevant to PK profiling. Supports therapeutic drug monitoring by providing reference concentration data. Note: HMDB uses Cloudflare protection so some requests may be blocked intermittently.

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_metabolite` | Comprehensive metabolite data (name, formula, SMILES, InChI, description, biofluid/tissue locations, pathways, diseases) | `hmdb_id` (required) |
| `search_metabolites` | Search metabolites by name/keyword | `query` (required), `limit` (optional, default 25) |
| `get_metabolite_concentrations` | Normal and abnormal concentration data across biofluids | `hmdb_id` (required) |
| `get_metabolite_pathways` | Biological pathways, biofluid locations, tissue locations, cellular locations | `hmdb_id` (required) |
| `get_metabolite_properties` | Chemical/physical properties (MW, logP, pKa, solubility, state) | `hmdb_id` (required) |
| `search_by_mass` | Find metabolites by molecular weight in Daltons | `mass` (required), `tolerance` (optional, default 0.05), `limit` (optional, default 25) |

---

## Python Environment

The container has Python 3 with `numpy`, `scipy`, `pandas`, and `matplotlib` available. Use `python3` or write scripts to `/tmp/` for execution. All PK/PD calculations should be performed in Python with reproducible code.

```python
import numpy as np, pandas as pd
from scipy.integrate import odeint, solve_ivp
from scipy.optimize import curve_fit, minimize
from scipy.stats import t as t_dist, norm, linregress
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
```

---

## Core Workflows

### Workflow 1: PK Parameter Extraction

Extract key pharmacokinetic parameters for a drug from FDA labels, DrugBank, and published literature. This is the foundational step for all downstream analyses.

**Target parameters:**

| Parameter | Symbol | Units | Source Priority |
|-----------|--------|-------|----------------|
| Maximum concentration | Cmax | ng/mL or ug/mL | FDA label > Clinical study > Literature |
| Time to maximum concentration | Tmax | hours | FDA label > Clinical study > Literature |
| Area under the curve (0-inf) | AUC0-inf | ng*h/mL | FDA label > Clinical study |
| Area under the curve (0-tau) | AUC0-tau | ng*h/mL | FDA label (steady-state) |
| Terminal half-life | t1/2 | hours | FDA label > DrugBank > Literature |
| Volume of distribution | Vd | L or L/kg | FDA label > DrugBank |
| Clearance | CL | L/h or mL/min | FDA label > DrugBank |
| Oral bioavailability | F | % | FDA label > DrugBank |
| Protein binding | PB | % | FDA label > DrugBank |
| Renal clearance | CLr | L/h | FDA label > Literature |

**Step-by-step workflow:**

1. Search FDA label for clinical pharmacology section:
```
mcp__fda__fda_data({ method: "get_drug_label", drug_name: "<DRUG>" })
```
Parse the "Clinical Pharmacology" section for PK parameter tables.

2. Cross-reference with DrugBank pharmacology:
```
mcp__drugbank__drugbank_data({ method: "get_pharmacology", drugbank_id: "<ID>" })
```

3. Search PubMed for dedicated PK studies:
```
mcp__pubmed__pubmed_data({
  method: "search",
  keywords: "pharmacokinetics <DRUG> healthy volunteers single dose",
  num_results: 10
})
```

4. Check for in vitro ADME data in ChEMBL:
```
mcp__chembl__chembl_data({ method: "get_activities", chembl_id: "<ID>", assay_type: "ADME" })
```

5. Compile PK parameter table with sources and evidence tier for each value.

**Key relationships to verify:**

- `CL = Dose / AUC0-inf` (for IV dosing)
- `CL/F = Dose / AUC0-inf` (for oral dosing, apparent clearance)
- `Vd = CL * t1/2 / 0.693` (one-compartment model)
- `Vd = Dose / C0` (IV bolus, extrapolated C0)
- `t1/2 = 0.693 * Vd / CL`
- `AUC0-inf = AUC0-t + Ct / ke` (where ke = 0.693 / t1/2)
- Accumulation ratio at steady state: `Rac = 1 / (1 - e^(-ke * tau))`

**Compiled output format:**

```
DRUG PK PROFILE: [NAME]
  Absorption:  F=_%, Tmax=_h, Cmax=_ng/mL (at dose _mg), food effect: _
  Distribution: Vd=_L (_L/kg), fu=_ (protein binding _%), Vss=_L
  Metabolism:  Primary CYP: _, Secondary: _, Active metabolites: _, fm(CYP3A4)=_
  Elimination: t1/2=_h, CL=_L/h, CLr=_L/h, Renal: _%, Fecal: _%
  Linearity:   Dose-proportional over _-_ mg range: Yes/No
```

---

### Workflow 2: First-in-Human (FIH) Dose Selection

Determine a safe starting dose for first-in-human clinical trials using multiple approaches per ICH M3(R2) and FDA Guidance for Industry (2005).

#### Approach A: NOAEL-Based (Standard Small Molecule)

1. Identify NOAEL from preclinical toxicology studies (most sensitive species)
2. Convert to Human Equivalent Dose (HED) using body surface area (BSA) scaling:

```
HED (mg/kg) = NOAEL (mg/kg) * (Animal Km / Human Km)
```

BSA conversion factors (Km values):

| Species | Body Weight (kg) | Km factor | HED Factor (Km/37) |
|---------|-----------------|-----------|---------------------|
| Mouse | 0.02 | 3 | 0.081 |
| Rat | 0.15 | 6 | 0.162 |
| Guinea pig | 0.40 | 8 | 0.216 |
| Rabbit | 1.8 | 12 | 0.324 |
| Monkey | 3 | 12 | 0.324 |
| Dog | 10 | 20 | 0.541 |
| Mini-pig | 20 | 27 | 0.730 |
| **Human** | **60** | **37** | **Reference** |

3. Apply safety factor (typically 10x) to derive Maximum Recommended Starting Dose (MRSD):

```
MRSD (mg/kg) = HED / Safety Factor
MRSD (mg for 60 kg human) = MRSD (mg/kg) * 60
```

4. Cross-check with pharmacologically active dose (PAD) in animals

**Example calculation (Python):**

```python
def calculate_fih_dose(noael_mg_kg, species, safety_factor=10, human_weight=60):
    """NOAEL-based FIH dose selection per FDA 2005 Guidance.

    HED = NOAEL * (Km_animal / Km_human)
    MRSD = HED / safety_factor

    Args:
        noael_mg_kg: NOAEL in animal species (mg/kg)
        species: animal species name
        safety_factor: default 10x per FDA guidance
        human_weight: default 60 kg

    Returns:
        dict with HED and MRSD in mg/kg and total mg
    """
    km = {
        'mouse': 3, 'rat': 6, 'guinea_pig': 8, 'rabbit': 12,
        'dog': 20, 'monkey': 12, 'mini_pig': 27
    }
    if species not in km:
        raise ValueError(f"Unknown species: {species}")

    conv = km[species] / 37  # Km_animal / Km_human
    hed = noael_mg_kg * conv
    mrsd = hed / safety_factor

    print(f"=== FIH Dose Selection (NOAEL-Based) ===")
    print(f"  Species: {species}")
    print(f"  NOAEL: {noael_mg_kg} mg/kg")
    print(f"  BSA conversion factor: {conv:.3f}")
    print(f"  HED: {hed:.4f} mg/kg = {hed * human_weight:.2f} mg")
    print(f"  Safety factor: {safety_factor}x")
    print(f"  MRSD: {mrsd:.4f} mg/kg = {mrsd * human_weight:.2f} mg")

    return {
        'HED_mg_kg': hed,
        'HED_mg': hed * human_weight,
        'MRSD_mg_kg': mrsd,
        'MRSD_mg': mrsd * human_weight,
    }

# Example: NOAEL 10 mg/kg in rat
result = calculate_fih_dose(10, 'rat')
# HED = 10 * (6/37) = 1.62 mg/kg
# MRSD = 1.62 / 10 = 0.162 mg/kg = 9.73 mg
```

#### Approach B: MABEL-Based (Biologics / High-Risk Targets)

For biologics or compounds with steep dose-response curves, use Minimum Anticipated Biological Effect Level:

1. Determine EC10 or EC20 from in vitro concentration-response curves
2. Identify target receptor occupancy (typically 10-20% RO for starting dose):

```
RO = [Drug] / ([Drug] + Kd)
```

Rearranging for target concentration:

```
[Drug] = RO * Kd / (1 - RO)
```

3. Calculate dose to achieve target concentration:

```
Dose = Target_Css * CL * tau / F
```

where:
- Target_Css = concentration achieving desired receptor occupancy
- CL = predicted human clearance (allometric scaling)
- tau = dosing interval
- F = predicted bioavailability

4. Compare with in vivo pharmacological doses in animal models
5. Select lowest dose from MABEL analysis, apply safety margin (2-10x)

```python
def mabel_receptor_occupancy(Kd_nM, target_RO=0.10):
    """Calculate MABEL concentration via receptor occupancy.

    [Drug] = RO * Kd / (1 - RO)

    Args:
        Kd_nM: dissociation constant in nM
        target_RO: target receptor occupancy fraction (default 10%)

    Returns:
        dict with MABEL concentration and dose context
    """
    mabel_conc = (target_RO * Kd_nM) / (1 - target_RO)

    print(f"=== MABEL via Receptor Occupancy ===")
    print(f"  Kd: {Kd_nM} nM")
    print(f"  Target RO: {target_RO * 100}%")
    print(f"  MABEL concentration: {mabel_conc:.2f} nM")
    print(f"  EC50 (by definition = Kd for simple binding): {Kd_nM} nM")
    print(f"  EC90: {Kd_nM * 9:.2f} nM")

    return {'MABEL_nM': mabel_conc, 'Kd_nM': Kd_nM, 'target_RO': target_RO}
```

**NOAEL vs MABEL Decision Tree:**

```
Use NOAEL when:
  - Small molecules with predictable cross-species PK
  - Linear PK, no immunomodulatory activity
  - Well-characterized target biology

Use MABEL when:
  - Biologics (mAbs, fusion proteins), immunomodulators
  - Steep dose-response (Hill coeff > 2), novel targets
  - Agonists with cytokine release risk (TGN1412 lesson)
  - First-in-class with no clinical precedent

When both apply: use the LOWER of NOAEL-HED/SF and MABEL as starting dose.
```

#### Approach C: Allometric Scaling of Clearance and Volume

Scale PK parameters from animal species to predict human PK:

```
Y = a * BW^b
```

where Y is the PK parameter, BW is body weight, and a/b are derived from multi-species log-log regression.

**Expected allometric exponents:**

| Parameter | Expected Exponent (b) | Reliable Range |
|-----------|----------------------|----------------|
| Clearance | 0.75 | 0.55-0.80 |
| Volume of distribution | 1.0 | 0.80-1.10 |
| Half-life | 0.25 | 0.15-0.35 |

If the CL exponent deviates significantly from 0.75, consider:
- Rule of Exponents correction (multiply by MLP or BrW)
- In vitro-in vivo extrapolation (IVIVE) using hepatocyte or microsomal data
- Physiologically-based PK (PBPK) modeling

```
Retrieve FIH context:
  mcp__pubmed__pubmed_data(method: "search", keywords: "DRUG_NAME toxicology NOAEL preclinical", num_results: 10)
  mcp__clinicaltrials__ct_data(method: "search_studies", query: "DRUG_NAME first-in-human phase 1", limit: 10)
  mcp__chembl__chembl_data(method: "get_activities", chembl_id: "CHEMBLxxxxx", limit: 30)
```

---

### Workflow 3: Drug-Drug Interaction (DDI) Prediction

Systematically evaluate DDI risk for CYP-mediated and transporter-mediated interactions.

**Step 1: Identify metabolic pathways**

```
mcp__drugbank__drugbank_data({ method: "get_targets", drugbank_id: "<ID>" })
mcp__drugbank__drugbank_data({ method: "get_pharmacology", drugbank_id: "<ID>" })
```

Extract: CYP enzymes responsible for metabolism (fm values), UGT enzymes, transporters.

**Step 2: Assess perpetrator potential (inhibition)**

Retrieve in vitro CYP inhibition data (Ki or IC50 values):

```
mcp__chembl__chembl_data({
  method: "get_activities",
  chembl_id: "<ID>",
  target_id: "<CYP_TARGET_ID>"
})
```

Key CYP ChEMBL target IDs:
- CYP3A4: CHEMBL340
- CYP2D6: CHEMBL289
- CYP2C9: CHEMBL3397
- CYP2C19: CHEMBL3356
- CYP1A2: CHEMBL3356

**Step 3: Calculate R-values for clinical DDI risk (FDA Guidance)**

Basic static model (R1 value for reversible inhibition):

```
R1 = 1 + [I]max,u / Ki,u
```

where:
- `[I]max,u` = maximum unbound systemic concentration of inhibitor at steady state
- `Ki,u` = unbound in vitro inhibition constant

**DDI risk thresholds (FDA 2020 Guidance):**

| R1 value | Risk | Action |
|----------|------|--------|
| R1 >= 1.02 | Potential interaction | In vivo DDI study recommended |
| R1 < 1.02 | Low risk | No clinical study needed |

For intestinal inhibition (CYP3A4):

```
R1,gut = 1 + [I]gut / Ki
```

where `[I]gut = Dose / 250 mL` (concentration in GI lumen, assumes 250 mL fluid volume)

**Step 4: Assess induction potential**

R3 value for CYP3A4 induction:

```
R3 = 1 / (1 + d * Emax * [I]max,u / (EC50 + [I]max,u))
```

where d = scaling factor (typically 1), Emax = maximum fold induction, EC50 = concentration for 50% of Emax.

If R3 <= 0.8, in vivo induction study is recommended.

**Step 5: Transporter-mediated DDI assessment**

Key transporters to evaluate:

| Transporter | Location | Substrates | Clinical Significance |
|-------------|----------|------------|----------------------|
| P-gp (MDR1) | Gut, liver, kidney, BBB | Digoxin, dabigatran, fexofenadine | Absorption, CNS penetration |
| BCRP | Gut, liver | Rosuvastatin, sulfasalazine | Absorption, hepatic uptake |
| OATP1B1 | Liver (sinusoidal) | Statins, repaglinide, methotrexate | Hepatic uptake, statin myopathy |
| OATP1B3 | Liver (sinusoidal) | Statins, telmisartan | Hepatic uptake |
| OAT1 | Kidney (basolateral) | Tenofovir, methotrexate, adefovir | Renal secretion |
| OAT3 | Kidney (basolateral) | Furosemide, pravastatin, ciprofloxacin | Renal secretion |
| OCT2 | Kidney (basolateral) | Metformin, cisplatin | Renal secretion, nephrotoxicity |
| MATE1 | Kidney (apical) | Metformin, cisplatin | Renal excretion |
| MATE2-K | Kidney (apical) | Metformin | Renal excretion |

```
mcp__drugbank__drugbank_data({ method: "get_interactions", drugbank_id: "<ID>" })
```

**Step 6: Check known clinical DDIs in FDA label**

```
mcp__fda__fda_data({ method: "get_drug_label", drug_name: "<DRUG>" })
```

Parse "Drug Interactions" section for clinical DDI study results with AUC/Cmax fold-changes.

**Step 7: Static DDI prediction model (Python)**

```python
def predict_ddi_auc_ratio(inhibitor_conc_uM, Ki_uM, fm):
    """Predict AUC ratio for CYP inhibition using basic static model.

    R = 1 / [fm / (1 + [I]/Ki) + (1 - fm)]

    Args:
        inhibitor_conc_uM: [I] at enzyme site (uM).
            For gut: Dose_mg * 1000 / (250 * MW)
            For liver: Cmax,u (unbound systemic)
        Ki_uM: inhibition constant (uM). Use IC50/2 if Ki unavailable.
        fm: fraction metabolized by inhibited CYP (0-1)

    Returns:
        AUC ratio (fold-increase)
    """
    auc_ratio = 1 / (fm / (1 + inhibitor_conc_uM / Ki_uM) + (1 - fm))
    return auc_ratio

def classify_ddi(auc_ratio):
    """Classify DDI severity per FDA guidance."""
    if auc_ratio >= 5:
        return 'Strong (>=5-fold AUC increase)'
    elif auc_ratio >= 2:
        return 'Moderate (2-5 fold AUC increase)'
    elif auc_ratio >= 1.25:
        return 'Weak (1.25-2 fold AUC increase)'
    else:
        return 'No significant interaction (<1.25-fold)'

def predict_induction_effect(fm, fold_change_CL):
    """Predict AUC decrease from CYP induction.

    R = 1 / [fm * fold_change_CL + (1 - fm)]

    Args:
        fm: fraction metabolized by induced CYP
        fold_change_CL: fold-increase in CYP activity due to induction

    Returns:
        dict with AUC ratio and classification
    """
    R = 1 / (fm * fold_change_CL + (1 - fm))
    if R <= 0.2:
        cls = 'Strong induction (>=80% AUC decrease)'
    elif R <= 0.5:
        cls = 'Moderate induction (50-80% AUC decrease)'
    elif R <= 0.8:
        cls = 'Weak induction (20-50% AUC decrease)'
    else:
        cls = 'No significant induction (<20% AUC decrease)'
    return {'AUC_ratio': R, 'classification': cls}
```

**Step 8: Compile DDI risk matrix**

| Perpetrator | Victim CYP/Transporter | Mechanism | R-value | Clinical Significance | Dose Adjustment |
|-------------|----------------------|-----------|---------|----------------------|-----------------|
| Drug A | CYP3A4 | Reversible inhibition | R1=1.8 | Moderate | Reduce victim dose 50% |
| Drug A | P-gp | Inhibition | R > 1.1 | Minor | Monitor |

**fm Impact on DDI Magnitude (Complete Inhibition):**

| fm | Max AUC Fold-Increase | Clinical Impact |
|----|----------------------|-----------------|
| 1.00 | Infinite (all elimination blocked) | Extremely high DDI risk |
| 0.90 | 10-fold | High; contraindicated combinations |
| 0.75 | 4-fold | Significant; dose reduction typically needed |
| 0.50 | 2-fold | Moderate; monitor or reduce dose |
| 0.25 | 1.33-fold | Low; usually no adjustment needed |
| 0.10 | 1.11-fold | Negligible |

---

### Workflow 4: Therapeutic Drug Monitoring (TDM)

Design TDM protocols for narrow therapeutic index (NTI) drugs.

**NTI drugs requiring TDM:**

| Drug | Therapeutic Range | Toxic Threshold | Sample Timing | Critical Toxicities |
|------|------------------|-----------------|---------------|---------------------|
| Vancomycin | AUC/MIC 400-600 (trough 15-20 ug/mL) | Trough >20 ug/mL | Pre-dose (trough); AUC via 2-point | Nephrotoxicity |
| Aminoglycosides | Peak/MIC > 8-10; trough < 1 ug/mL | Trough >2 ug/mL | 1h post-dose (peak), pre-dose | Nephro/ototoxicity |
| Phenytoin | 10-20 ug/mL (total), 1-2 ug/mL (free) | >20 ug/mL | Trough, steady-state | Ataxia, nystagmus |
| Carbamazepine | 4-12 ug/mL | >15 ug/mL | Trough, steady-state | Aplastic anemia, SJS |
| Lithium | 0.6-1.2 mEq/L (acute), 0.4-1.0 (maintenance) | >1.5 mEq/L | 12h post-dose | Renal, thyroid, tremor |
| Digoxin | 0.5-2.0 ng/mL (HF: 0.5-0.9) | >2.0 ng/mL | >= 6h post-dose (distribution) | Arrhythmias, visual |
| Tacrolimus | 5-15 ng/mL (varies by indication/time) | >20 ng/mL | Pre-dose trough | Nephrotoxicity |
| Cyclosporine | 100-400 ng/mL (varies) or C2 monitoring | >400 ng/mL | Trough or 2h post-dose | Nephrotoxicity |
| Methotrexate (high-dose) | < 0.05 uM at 72h | >1 uM at 48h | 24h, 48h, 72h post-infusion | Mucositis, myelosuppression |
| Valproic acid | 50-100 ug/mL | >100 ug/mL | Trough at steady state | Hepatotoxicity, teratogenicity |
| Theophylline | 10-20 ug/mL | >20 ug/mL | Trough at steady state | Seizures, arrhythmias |

**TDM workflow steps:**

1. Retrieve drug therapeutic range from FDA label:
```
mcp__fda__fda_data({ method: "get_drug_label", drug_name: "<DRUG>" })
```

2. Get pharmacology data for protein binding (critical for free drug monitoring):
```
mcp__drugbank__drugbank_data({ method: "get_pharmacology", drugbank_id: "<ID>" })
```

3. For highly protein-bound drugs (> 90%), calculate free concentration:

```
C_free = C_total * fu
fu = (100 - PB%) / 100
```

4. Adjust for hypoalbuminemia (phenytoin example, Sheiner-Tozer equation):

```
C_adjusted = C_measured / (0.2 * albumin/4.4 + 0.1)
```

For patients on dialysis:

```
C_adjusted = C_measured / (0.1 * albumin/4.4 + 0.1)
```

5. Determine sampling strategy:
   - Time to steady state = 4-5 half-lives
   - Trough sampling: within 30 min before next dose
   - Peak sampling: depends on route (IV: end of infusion; oral: at expected Tmax)

6. Dose adjustment calculations:

```python
def linear_dose_adjustment(current_dose, measured_level, target_level):
    """Linear PK dose adjustment (valid at steady state only).
    New_Dose = Current_Dose * (Target / Measured)
    """
    new_dose = current_dose * (target_level / measured_level)
    print(f"Current dose: {current_dose} mg, Measured: {measured_level}, Target: {target_level}")
    print(f"New dose: {new_dose:.1f} mg")
    return new_dose

def phenytoin_dose_adjustment(current_dose_mg_day, measured_css, target_css, Km=4.0):
    """Michaelis-Menten dose adjustment for phenytoin (non-linear PK).
    R = Vmax * Css / (Km + Css)
    Solve for Vmax from current data, then calculate new dose.

    Default Km = 4.0 mg/L (population average; range 1-15 mg/L)
    """
    Vmax = current_dose_mg_day * (Km + measured_css) / measured_css
    new_dose = Vmax * target_css / (Km + target_css)
    print(f"Estimated Vmax: {Vmax:.1f} mg/day")
    print(f"New dose for target Css {target_css}: {new_dose:.1f} mg/day")
    return new_dose
```

7. Search literature for Bayesian TDM approaches:
```
mcp__pubmed__pubmed_data({
  method: "search",
  keywords: "Bayesian therapeutic drug monitoring <DRUG> population pharmacokinetics",
  num_results: 10
})
```

---

### Workflow 5: Dose Optimization for Special Populations

Adjust doses based on population PK data for renal impairment, hepatic impairment, pediatric, geriatric, and obese patients.

#### Renal Impairment

1. Determine fraction excreted unchanged in urine (fe):
```
mcp__drugbank__drugbank_data({ method: "get_pharmacology", drugbank_id: "<ID>" })
```

2. If fe > 0.3, dose adjustment is likely needed. Use the Dettli method:

```
Dose_adjusted = Dose_normal * [1 - fe * (1 - KF)]
```

where KF = patient's kidney function fraction = eGFR_patient / 120

3. FDA renal impairment categories:

| eGFR (mL/min/1.73m2) | Stage | Typical Adjustment |
|----------------------|-------|--------------------|
| >= 90 | Normal | 100% dose |
| 60-89 | Mild | Usually 100%, check label |
| 30-59 | Moderate | 50-75% if fe > 0.3 |
| 15-29 | Severe | 25-50% if fe > 0.3 |
| < 15 | ESRD | Per label; consider dialyzability |

```python
def cockcroft_gault(age, weight_kg, serum_cr_mg_dL, sex='male'):
    """Estimate CrCl using Cockcroft-Gault equation.
    CrCl (mL/min) = [(140-age) * weight / (72 * SCr)] * 0.85 if female
    """
    clcr = ((140 - age) * weight_kg) / (72 * serum_cr_mg_dL)
    if sex == 'female':
        clcr *= 0.85
    return clcr

def renal_dose_adjustment(fe, egfr, normal_dose):
    """Dettli method for renal dose adjustment.
    Dose_adj = Normal_dose * [1 - fe * (1 - eGFR/120)]

    Args:
        fe: fraction excreted unchanged in urine (0-1)
        egfr: estimated GFR (mL/min)
        normal_dose: standard dose (mg)
    """
    factor = max(1 - fe * (1 - egfr / 120), 0.1)
    adjusted = normal_dose * factor
    print(f"fe={fe}, eGFR={egfr}, adjustment factor={factor:.2f}")
    print(f"Adjusted dose: {adjusted:.1f} mg (from {normal_dose} mg)")
    return {'adjusted_dose_mg': adjusted, 'factor': factor}
```

#### Hepatic Impairment

Child-Pugh scoring:

| Parameter | 1 pt | 2 pts | 3 pts |
|-----------|------|-------|-------|
| Bilirubin (mg/dL) | <2 | 2-3 | >3 |
| Albumin (g/dL) | >3.5 | 2.8-3.5 | <2.8 |
| INR | <1.7 | 1.7-2.3 | >2.3 |
| Ascites | None | Mild | Mod-severe |
| Encephalopathy | None | I-II | III-IV |

| Score | Class | Expected CL Reduction | Dose Adjustment |
|-------|-------|----------------------|-----------------|
| 5-6 | A (Mild) | 10-40% | Usually no adjustment or minor |
| 7-9 | B (Moderate) | 40-70% | Reduce 50% or extend interval |
| 10-15 | C (Severe) | >70% | Avoid or minimal dose with monitoring |

Hepatic clearance model (well-stirred model):

```
CL_hepatic = Q_H * fu * CL_int / (Q_H + fu * CL_int)
```

where Q_H = hepatic blood flow (~1.5 L/min), fu = fraction unbound, CL_int = intrinsic clearance.

- High extraction ratio drugs (ER > 0.7): CL depends on hepatic blood flow (Q_H). In cirrhosis with portal hypertension, expect 50-70% CL reduction.
- Low extraction ratio drugs (ER < 0.3): CL depends on fu * CL_int. In cirrhosis, reduced protein binding increases fu but reduced CL_int may partially offset this.

#### Pediatric Dose Adjustment

Developmental pharmacology considerations:
- Neonates (0-28 days): immature CYP enzymes, reduced GFR (~2-4 mL/min), increased Vd (higher body water %)
- Infants (1-12 months): rapidly maturing enzyme activity, GFR approaches adult values by 6-12 months
- Children (1-12 years): often have highest weight-normalized CL (supraadult clearance for some CYPs)
- Adolescents (12-18 years): approaching adult PK

Scaling approaches:

1. Allometric scaling with maturation function:

```
CL_pediatric = CL_adult * (BW_child / 70)^0.75 * MF(PMA)
```

where MF = maturation factor as a function of post-menstrual age (PMA), typically sigmoidal:

```
MF = PMA^Hill / (TM50^Hill + PMA^Hill)
```

2. BSA-based dosing (Mosteller formula):

```
BSA (m2) = sqrt(height_cm * weight_kg / 3600)
Dose_pediatric = Dose_adult * (BSA_child / 1.73)
```

```python
def pediatric_allometric_dose(adult_dose, child_weight_kg, adult_weight=70):
    """Allometric scaling for pediatric dose (without maturation).
    CL_child = CL_adult * (Wt_child / Wt_adult)^0.75
    """
    return adult_dose * (child_weight_kg / adult_weight) ** 0.75

def maturation_factor(age_months, enzyme='CYP3A4'):
    """Sigmoidal maturation: MF = age^n / (TM50^n + age^n)

    TM50 = age at 50% mature activity (months)
    n = Hill coefficient for maturation curve
    """
    params = {
        'CYP3A4':  (1.0, 2.0),   # Rapid maturation, ~adult by 6 months
        'CYP1A2':  (6.0, 1.5),   # Slower, ~adult by 1-2 years
        'CYP2D6':  (1.0, 2.5),   # Rapid maturation
        'CYP2C9':  (3.0, 1.5),   # ~adult by 6-12 months
        'CYP2C19': (6.0, 1.0),   # Slower maturation
        'UGT1A1':  (3.0, 1.5),   # Variable
        'GFR':     (1.5, 2.5),   # Rapid, ~adult by 6-12 months
    }
    TM50, n = params.get(enzyme, (3.0, 1.5))
    mf = age_months**n / (TM50**n + age_months**n)
    return mf
```

#### Geriatric Patients

| PK Change | Magnitude | Clinical Impact |
|-----------|-----------|----------------|
| GFR decline | ~1 mL/min/year after age 40 | Dose reduction for renally cleared drugs |
| Hepatic blood flow reduction | 20-40% decline | Reduced first-pass for high-ER drugs |
| Phase I metabolism | ~30% decrease | Prolonged t1/2 for CYP-metabolized drugs |
| Body composition | Increased fat, decreased lean mass, decreased total body water | Increased Vd for lipophilic drugs |
| Albumin | Decreased 10-20% | Higher free fractions |
| CNS sensitivity | Increased | Lower doses for benzodiazepines, opioids |

#### Obesity

| Drug Characteristic | Weight Metric | Rationale |
|--------------------|--------------|-----------|
| Hydrophilic, small Vd | Adjusted Body Weight (ABW) | Does not distribute extensively into fat |
| Lipophilic, large Vd | Total Body Weight (TBW) | Distributes into adipose tissue |
| Aminoglycosides | ABW = IBW + 0.4 * (TBW - IBW) | Partial distribution into fat |
| Vancomycin | TBW | Distributes into adipose tissue |
| Low-molecular-weight heparins | TBW (capped) or ABW | Variable, check specific agent |

```
ABW = IBW + 0.4 * (TBW - IBW)
IBW (male) = 50 + 2.3 * (height_inches - 60)
IBW (female) = 45.5 + 2.3 * (height_inches - 60)
```

#### Pregnancy PK Changes

| Parameter | Change | Mechanism |
|-----------|--------|-----------|
| GFR | Increased ~50% | Increased renal blood flow |
| CYP3A4, CYP2D6 | Induced 50-100% | Hormonal induction |
| CYP1A2, CYP2C19 | Decreased 30-50% | Hormonal inhibition |
| Albumin | Decreased ~30% | Hemodilution |
| Vd | Increased | Expanded plasma volume, body water |

```
Retrieve special population data:
  mcp__fda__fda_data(method: "get_drug_label", drug_name: "DRUG_NAME")
  -> Parse "USE IN SPECIFIC POPULATIONS" section
  mcp__pubmed__pubmed_data(method: "search", keywords: "DRUG_NAME renal impairment pharmacokinetics", num_results: 10)
```

---

### Workflow 6: Bioequivalence Assessment

Evaluate bioequivalence (BE) between test (generic) and reference formulations per FDA guidance.

**BE criteria (average bioequivalence):**

The 90% confidence interval for the geometric mean ratio (test/reference) of:
- AUC0-t
- AUC0-inf
- Cmax

must fall entirely within 80.00-125.00%.

**Study design:**
- Typically 2-period, 2-sequence, 2-treatment crossover
- Adequate washout period (>= 5 * t1/2)
- Fasting or fed conditions per FDA product-specific guidance

**Statistical analysis (Python):**

```python
import numpy as np
from scipy import stats

def bioequivalence_assessment(ln_auc_test, ln_auc_ref, ln_cmax_test, ln_cmax_ref):
    """Bioequivalence assessment using log-transformed paired data.

    90% CI for geometric mean ratio must be within 80.00-125.00%.

    Args:
        ln_auc_test: log-transformed AUC values for test formulation
        ln_auc_ref: log-transformed AUC values for reference formulation
        ln_cmax_test: log-transformed Cmax values for test
        ln_cmax_ref: log-transformed Cmax values for reference

    Returns:
        dict with GMR, 90% CI, and BE determination
    """
    def _calc_be(ln_test, ln_ref, param_name):
        diff = np.array(ln_test) - np.array(ln_ref)
        n = len(diff)
        mean_diff = np.mean(diff)
        se = stats.sem(diff)
        t_crit = stats.t.ppf(0.95, df=n-1)  # one-sided 0.05 for 90% CI

        gmr = np.exp(mean_diff) * 100
        ci_lower = np.exp(mean_diff - t_crit * se) * 100
        ci_upper = np.exp(mean_diff + t_crit * se) * 100
        is_be = 80 <= ci_lower and ci_upper <= 125

        return {
            f'{param_name}_GMR': round(gmr, 2),
            f'{param_name}_90CI_lower': round(ci_lower, 2),
            f'{param_name}_90CI_upper': round(ci_upper, 2),
            f'{param_name}_BE': is_be,
        }

    results = {}
    results.update(_calc_be(ln_auc_test, ln_auc_ref, 'AUC'))
    results.update(_calc_be(ln_cmax_test, ln_cmax_ref, 'Cmax'))
    results['overall_BE'] = results['AUC_BE'] and results['Cmax_BE']

    print("=== Bioequivalence Assessment ===")
    print(f"  AUC  GMR: {results['AUC_GMR']}% (90% CI: {results['AUC_90CI_lower']}-{results['AUC_90CI_upper']}%) -> {'BE' if results['AUC_BE'] else 'NOT BE'}")
    print(f"  Cmax GMR: {results['Cmax_GMR']}% (90% CI: {results['Cmax_90CI_lower']}-{results['Cmax_90CI_upper']}%) -> {'BE' if results['Cmax_BE'] else 'NOT BE'}")
    print(f"  Overall: {'BIOEQUIVALENT' if results['overall_BE'] else 'NOT BIOEQUIVALENT'}")

    return results
```

**Special BE considerations:**

| Situation | Criteria |
|-----------|----------|
| Standard drugs | 80.00-125.00% for AUC and Cmax |
| NTI drugs (some agencies) | 90.00-111.11% (tightened limits) |
| Highly variable drugs (CVintra > 30%) | Reference-scaled average BE allowed |
| Endogenous compounds | Baseline correction required |
| Modified-release formulations | May require multi-dose steady-state BE |

```
Retrieve BE context:
  mcp__fda__fda_data(method: "search_drugs", query: "DRUG_NAME")
  mcp__clinicaltrials__ct_data(method: "search_studies", query: "DRUG_NAME bioequivalence", limit: 10)
  mcp__pubmed__pubmed_data(method: "search", keywords: "DRUG_NAME bioequivalence generic 90% confidence interval", num_results: 10)
```

---

## PK/PD Scoring Framework

Score each drug's pharmacokinetic characterization on a 0-100 scale across five dimensions.

### Dimension 1: Therapeutic Window Assessment (25 points)

| Score | Criteria |
|-------|----------|
| 25 | Well-defined therapeutic range from multiple clinical studies; established TDM protocols; clear concentration-response and concentration-toxicity relationships |
| 20 | Therapeutic range defined from Phase 2/3 data; general concentration-response relationship established |
| 15 | Approximate therapeutic range from limited clinical data; concentration-toxicity relationship partially characterized |
| 10 | Therapeutic range inferred from animal pharmacology; no human concentration-response data |
| 5 | No therapeutic range data; dosing based on empirical titration only |

### Dimension 2: DDI Risk Score (25 points)

| Score | Criteria |
|-------|----------|
| 25 | Complete DDI characterization: all major CYP enzymes, transporters evaluated in vitro and in vivo; clinical DDI studies with strong and moderate inhibitors/inducers; clear labeling guidance |
| 20 | Major CYP pathways characterized; clinical DDI studies with key perpetrators; transporter data available |
| 15 | In vitro CYP inhibition/induction data available; limited clinical DDI studies |
| 10 | Only in vitro metabolism identification (reaction phenotyping); no clinical DDI studies |
| 5 | Metabolic pathway unknown; no DDI data available |

### Dimension 3: Special Population Dose Adjustment Confidence (20 points)

| Score | Criteria |
|-------|----------|
| 20 | Dedicated PK studies in renal impairment, hepatic impairment, pediatric, geriatric; population PK model with covariates; quantitative dose recommendations in labeling |
| 15 | PK studies in renal and hepatic impairment; some pediatric data; general dose recommendations available |
| 10 | Limited organ impairment data; dose recommendations extrapolated from PK properties |
| 5 | No special population PK data; dose adjustments based on general principles only |

### Dimension 4: PK Linearity and Predictability (15 points)

| Score | Criteria |
|-------|----------|
| 15 | Demonstrated dose-proportional PK across clinical dose range; time-independent PK; predictable accumulation at steady state; well-characterized absorption |
| 10 | Generally dose-proportional with minor deviations; time-independent within typical doses; food effect characterized |
| 7 | Non-linear PK (saturable metabolism or absorption); autoinduction; time-dependent PK partially characterized |
| 3 | Highly non-linear or unpredictable PK; large inter-subject variability (CV > 60%); complex absorption |

### Dimension 5: Bioavailability Characterization (15 points)

| Score | Criteria |
|-------|----------|
| 15 | Absolute bioavailability determined (IV vs oral study); food effect study completed; formulation-PK relationship characterized; BCS class known |
| 10 | Relative bioavailability data available; food effect known; absorption characteristics partially defined |
| 7 | Oral bioavailability estimated from mass balance or preclinical data; limited formulation data |
| 3 | Bioavailability unknown; no food effect data; absorption poorly characterized |

**Total Score Interpretation:**

| Range | Interpretation |
|-------|---------------|
| 85-100 | Comprehensively characterized PK; high confidence in dosing recommendations |
| 70-84 | Well-characterized PK; adequate for most clinical decisions |
| 50-69 | Moderately characterized; gaps in DDI or special population data |
| 30-49 | Poorly characterized; significant uncertainty in dose optimization |
| 0-29 | Minimally characterized; preclinical or early Phase 1 stage |

---

## Python Code Templates

### Template 1: One-Compartment PK Model Fitting

```python
import numpy as np
from scipy.optimize import curve_fit

def one_compartment_oral(t, ka, ke, Vd, F, Dose):
    """One-compartment model with first-order absorption and elimination.

    C(t) = (F * Dose * ka) / (Vd * (ka - ke)) * (exp(-ke*t) - exp(-ka*t))

    Parameters:
        t: time points (hours)
        ka: absorption rate constant (1/h)
        ke: elimination rate constant (1/h)
        Vd: volume of distribution (L)
        F: bioavailability (fraction)
        Dose: dose administered (mg), converted to ng internally
    """
    if abs(ka - ke) < 1e-10:
        ka = ka * 1.01  # Avoid division by zero when ka ~ ke
    C = (F * Dose * ka) / (Vd * (ka - ke)) * (np.exp(-ke * t) - np.exp(-ka * t))
    return np.maximum(C, 0)

def fit_one_compartment(time_h, conc_ng_ml, dose_mg, F=1.0):
    """Fit one-compartment model to observed concentration-time data.

    Args:
        time_h: array of time points (hours)
        conc_ng_ml: array of observed concentrations (ng/mL)
        dose_mg: dose in mg
        F: bioavailability (fixed or estimated)

    Returns:
        dict with fitted parameters and derived PK values
    """
    dose_ng = dose_mg * 1e6  # Convert mg to ng

    def model(t, ka, ke, Vd_L):
        return one_compartment_oral(t, ka, ke, Vd_L * 1000, F, dose_ng)
        # Vd in mL for ng/mL units

    # Initial guesses: ka=1/h, ke=0.1/h, Vd=50L
    p0 = [1.0, 0.1, 50.0]
    bounds = ([0.01, 0.001, 1.0], [20.0, 5.0, 1000.0])

    popt, pcov = curve_fit(model, time_h, conc_ng_ml, p0=p0, bounds=bounds,
                           maxfev=10000)
    ka, ke, Vd = popt
    perr = np.sqrt(np.diag(pcov))

    # Derived parameters
    t_half = 0.693 / ke
    CL = ke * Vd  # L/h
    Tmax = np.log(ka / ke) / (ka - ke)
    Cmax = model(np.array([Tmax]), ka, ke, Vd)[0]
    AUC_0_inf = F * dose_ng / (CL * 1000)  # ng*h/mL

    results = {
        'ka (1/h)': round(ka, 4),
        'ke (1/h)': round(ke, 4),
        'Vd (L)': round(Vd, 2),
        't1/2 (h)': round(t_half, 2),
        'CL (L/h)': round(CL, 2),
        'Tmax (h)': round(Tmax, 2),
        'Cmax (ng/mL)': round(Cmax, 2),
        'AUC0-inf (ng*h/mL)': round(AUC_0_inf, 2),
    }

    print("=== One-Compartment PK Model Fit ===")
    for k, v in results.items():
        print(f"  {k}: {v}")

    return results

# Example usage:
# time = np.array([0.5, 1, 1.5, 2, 3, 4, 6, 8, 12, 24])
# conc = np.array([50, 180, 280, 320, 290, 240, 160, 100, 45, 8])
# fit_one_compartment(time, conc, dose_mg=100)
```

### Template 2: Non-Compartmental Analysis (NCA)

```python
import numpy as np
from scipy import stats

def nca_analysis(time_h, conc, dose_mg, route='oral', tau=None):
    """Perform non-compartmental analysis on concentration-time data.

    Uses linear-log trapezoidal method (linear up, log down) for AUC.

    Args:
        time_h: array of time points (hours)
        conc: array of concentrations (ng/mL)
        dose_mg: dose administered (mg)
        route: 'oral' or 'iv'
        tau: dosing interval for steady-state analysis (hours)

    Returns:
        dict of NCA parameters
    """
    time_h = np.array(time_h, dtype=float)
    conc = np.array(conc, dtype=float)
    conc = np.maximum(conc, 0)

    # --- Cmax and Tmax ---
    idx_max = np.argmax(conc)
    Cmax = conc[idx_max]
    Tmax = time_h[idx_max]

    # --- AUC by linear-log trapezoidal method ---
    auc_segments = []
    for i in range(len(time_h) - 1):
        dt = time_h[i+1] - time_h[i]
        c1, c2 = conc[i], conc[i+1]
        if c1 > 0 and c2 > 0 and c2 < c1:
            # Log-trapezoidal for declining concentrations
            auc_seg = dt * (c1 - c2) / np.log(c1 / c2)
        else:
            # Linear trapezoidal for ascending or equal concentrations
            auc_seg = dt * (c1 + c2) / 2
        auc_segments.append(auc_seg)

    AUC_0_t = sum(auc_segments)

    # --- Terminal phase estimation (lambda_z) ---
    n_terminal = min(4, len(time_h) - idx_max)
    lambda_z = t_half = r_squared = None
    if n_terminal >= 3:
        t_term = time_h[-n_terminal:]
        c_term = conc[-n_terminal:]
        mask = c_term > 0
        if sum(mask) >= 3:
            slope, intercept, r, p, se = stats.linregress(
                t_term[mask], np.log(c_term[mask])
            )
            lambda_z = -slope
            t_half = 0.693 / lambda_z
            r_squared = r ** 2

    # --- AUC0-inf ---
    AUC_0_inf = pct_extrap = None
    if lambda_z and lambda_z > 0:
        C_last = conc[-1]
        AUC_extrap = C_last / lambda_z
        AUC_0_inf = AUC_0_t + AUC_extrap
        pct_extrap = (AUC_extrap / AUC_0_inf) * 100

    # --- Clearance and Volume ---
    dose_ng = dose_mg * 1e6
    CL = Vd = None
    if AUC_0_inf and AUC_0_inf > 0:
        CL = dose_ng / AUC_0_inf / 1000  # L/h (CL for IV, CL/F for oral)
        if lambda_z:
            Vd = CL / lambda_z  # Vz for IV, Vz/F for oral

    # --- AUMC and MRT ---
    aumc_segments = []
    for i in range(len(time_h) - 1):
        dt = time_h[i+1] - time_h[i]
        tc1 = time_h[i] * conc[i]
        tc2 = time_h[i+1] * conc[i+1]
        aumc_seg = dt * (tc1 + tc2) / 2
        aumc_segments.append(aumc_seg)
    AUMC_0_t = sum(aumc_segments)

    MRT = None
    if lambda_z and lambda_z > 0 and AUC_0_inf:
        C_last = conc[-1]
        t_last = time_h[-1]
        AUMC_extrap = (t_last * C_last / lambda_z) + (C_last / lambda_z**2)
        AUMC_0_inf = AUMC_0_t + AUMC_extrap
        MRT = AUMC_0_inf / AUC_0_inf

    cl_label = "CL" if route == 'iv' else "CL/F"
    vd_label = "Vz" if route == 'iv' else "Vz/F"

    results = {
        'Cmax (ng/mL)': round(Cmax, 2),
        'Tmax (h)': round(Tmax, 2),
        'AUC0-t (ng*h/mL)': round(AUC_0_t, 2),
        'AUC0-inf (ng*h/mL)': round(AUC_0_inf, 2) if AUC_0_inf else 'N/A',
        '% AUC extrapolated': round(pct_extrap, 1) if pct_extrap else 'N/A',
        'lambda_z (1/h)': round(lambda_z, 4) if lambda_z else 'N/A',
        't1/2 (h)': round(t_half, 2) if t_half else 'N/A',
        'Terminal R-squared': round(r_squared, 4) if r_squared else 'N/A',
        f'{cl_label} (L/h)': round(CL, 2) if CL else 'N/A',
        f'{vd_label} (L)': round(Vd, 2) if Vd else 'N/A',
        'MRT (h)': round(MRT, 2) if MRT else 'N/A',
    }

    print("=== Non-Compartmental Analysis ===")
    for k, v in results.items():
        print(f"  {k}: {v}")

    if pct_extrap and pct_extrap > 20:
        print("\n  WARNING: >20% AUC extrapolated. Terminal phase may be inadequately sampled.")

    return results
```

### Template 3: Allometric Scaling Calculations

```python
import numpy as np
from scipy import stats

def allometric_scaling(species_data, human_bw=70, parameter='CL',
                       correction=None, brain_weights=None, mle_values=None):
    """Predict human PK parameter using allometric scaling.

    Y = a * BW^b (simple allometry)

    Rule of Exponents (Mahmood & Balian):
      - b = 0.55-0.80: simple allometry (no correction)
      - b = 0.80-1.00: multiply CL by brain weight
      - b > 1.00: multiply CL by MLP (maximum life-span potential)

    Args:
        species_data: dict of {species: {'bw': kg, 'value': parameter_value}}
        human_bw: human body weight in kg (default 70)
        parameter: 'CL' (mL/min), 'Vd' (L), or 't_half' (h)
        correction: None, 'brain_weight', or 'MLP'
        brain_weights: dict {species: brain_weight_g} if correction='brain_weight'
        mle_values: dict {species: MLP_years} if correction='MLP'

    Returns:
        dict with predicted human value and regression statistics
    """
    species = list(species_data.keys())
    bw = np.array([species_data[s]['bw'] for s in species])
    values = np.array([species_data[s]['value'] for s in species])

    # Apply corrections if needed
    if correction == 'brain_weight' and brain_weights:
        brw = np.array([brain_weights[s] for s in species])
        y_data = values * brw
        label = f'{parameter} * BrW'
    elif correction == 'MLP' and mle_values:
        mlp = np.array([mle_values[s] for s in species])
        y_data = values * mlp
        label = f'{parameter} * MLP'
    else:
        y_data = values
        label = parameter

    # Log-log regression
    log_bw = np.log(bw)
    log_y = np.log(y_data)
    slope, intercept, r_value, p_value, std_err = stats.linregress(log_bw, log_y)

    a = np.exp(intercept)
    b = slope
    r_sq = r_value ** 2

    # Predict human value
    if correction == 'brain_weight' and brain_weights:
        human_brw = brain_weights.get('human', 1400)  # default 1400g
        predicted_corrected = a * (human_bw ** b)
        predicted = predicted_corrected / human_brw
    elif correction == 'MLP' and mle_values:
        human_mlp = mle_values.get('human', 93)  # default 93 years
        predicted_corrected = a * (human_bw ** b)
        predicted = predicted_corrected / human_mlp
    else:
        predicted = a * (human_bw ** b)

    # Rule of Exponents guidance
    if parameter == 'CL':
        if 0.55 <= b <= 0.80:
            rule = "Simple allometry (exponent 0.55-0.80): no correction needed"
        elif 0.80 < b <= 1.0:
            rule = "Exponent 0.80-1.0: apply brain weight correction"
        elif b > 1.0:
            rule = "Exponent >1.0: apply MLP correction or use IVIVE"
        else:
            rule = "Exponent <0.55: unusual, verify data quality"
    else:
        rule = f"Exponent = {b:.3f}"

    print(f"=== Allometric Scaling: {parameter} ===")
    print(f"  Equation: {label} = {a:.4f} * BW^{b:.3f}")
    print(f"  R-squared: {r_sq:.4f}")
    print(f"  Predicted human {parameter}: {predicted:.2f}")
    print(f"  {rule}")

    return {
        'coefficient_a': a,
        'exponent_b': b,
        'r_squared': r_sq,
        'predicted_human': predicted,
        'rule_of_exponents': rule,
    }

# Example usage:
# data = {
#     'mouse':  {'bw': 0.025, 'value': 0.5},
#     'rat':    {'bw': 0.25,  'value': 3.2},
#     'monkey': {'bw': 5,     'value': 28},
#     'dog':    {'bw': 10,    'value': 45},
# }
# result = allometric_scaling(data, parameter='CL')
```

### Template 4: Exposure-Response Modeling

```python
import numpy as np
from scipy.optimize import curve_fit

def emax_model(conc, E0, Emax, EC50):
    """Simple Emax model.
    E = E0 + Emax * C / (EC50 + C)
    """
    return E0 + Emax * conc / (EC50 + conc)

def sigmoid_emax_model(conc, E0, Emax, EC50, n):
    """Sigmoid Emax (Hill) model.
    E = E0 + Emax * C^n / (EC50^n + C^n)

    n = Hill coefficient (steepness of curve)
    n = 1: standard Emax (hyperbolic)
    n > 1: steeper curve (switch-like)
    n < 1: shallower curve
    """
    return E0 + Emax * (conc ** n) / (EC50 ** n + conc ** n)

def fit_exposure_response(concentrations, responses, model='emax'):
    """Fit exposure-response model to data.

    Args:
        concentrations: array of drug concentrations
        responses: array of pharmacodynamic responses
        model: 'emax' or 'sigmoid_emax'

    Returns:
        dict with fitted parameters
    """
    conc = np.array(concentrations, dtype=float)
    resp = np.array(responses, dtype=float)

    if model == 'emax':
        p0 = [np.min(resp), np.max(resp) - np.min(resp), np.median(conc)]
        bounds = ([-np.inf, 0, 0], [np.inf, np.inf, np.inf])
        popt, pcov = curve_fit(emax_model, conc, resp, p0=p0, bounds=bounds,
                               maxfev=10000)
        E0, Emax, EC50 = popt
        perr = np.sqrt(np.diag(pcov))
        fitted = emax_model(conc, *popt)

        # EC90 = EC50 * 9 (for Hill coefficient = 1)
        results = {
            'E0 (baseline)': round(E0, 4),
            'Emax': round(Emax, 4),
            'EC50': round(EC50, 4),
            'EC50 SE': round(perr[2], 4),
            'EC90': round(EC50 * 9, 4),
        }

    elif model == 'sigmoid_emax':
        p0 = [np.min(resp), np.max(resp) - np.min(resp), np.median(conc), 1.0]
        bounds = ([-np.inf, 0, 0, 0.1], [np.inf, np.inf, np.inf, 10])
        popt, pcov = curve_fit(sigmoid_emax_model, conc, resp, p0=p0,
                               bounds=bounds, maxfev=10000)
        E0, Emax, EC50, n = popt
        perr = np.sqrt(np.diag(pcov))
        fitted = sigmoid_emax_model(conc, *popt)

        # EC90 for sigmoid: EC90 = EC50 * (90/10)^(1/n) = EC50 * 9^(1/n)
        EC90 = EC50 * (9 ** (1 / n))
        results = {
            'E0 (baseline)': round(E0, 4),
            'Emax': round(Emax, 4),
            'EC50': round(EC50, 4),
            'Hill coefficient (n)': round(n, 4),
            'EC90': round(EC90, 4),
        }

    # Goodness of fit
    ss_res = np.sum((resp - fitted) ** 2)
    ss_tot = np.sum((resp - np.mean(resp)) ** 2)
    r_squared = 1 - ss_res / ss_tot
    results['R-squared'] = round(r_squared, 4)

    print(f"=== Exposure-Response Model ({model}) ===")
    for k, v in results.items():
        print(f"  {k}: {v}")

    return results

# Example usage:
# conc = [0, 1, 5, 10, 25, 50, 100, 250, 500, 1000]
# resp = [5, 8, 22, 38, 62, 75, 85, 92, 96, 98]
# fit_exposure_response(conc, resp, model='sigmoid_emax')
```

---

## CYP Metabolism Quick-Reference Matrix

| CYP | % Drug Metabolism | Key Substrates | Strong Inhibitors | Strong Inducers |
|-----|------------------|----------------|-------------------|-----------------|
| 3A4 | ~50% | Midazolam, simvastatin, tacrolimus, fentanyl, cyclosporine | Ketoconazole, itraconazole, ritonavir, clarithromycin | Rifampin, carbamazepine, phenytoin, St. John's wort |
| 2D6 | ~25% | Codeine, metoprolol, tamoxifen, fluoxetine, dextromethorphan | Paroxetine, fluoxetine, quinidine, bupropion | Not significantly inducible |
| 2C9 | ~10% | Warfarin (S-), phenytoin, losartan, celecoxib, glipizide | Fluconazole, amiodarone | Rifampin |
| 2C19 | ~5% | Omeprazole, clopidogrel, voriconazole, diazepam | Fluvoxamine, fluconazole, ticlopidine | Rifampin, efavirenz |
| 1A2 | ~5% | Theophylline, caffeine, clozapine, tizanidine | Fluvoxamine, ciprofloxacin | Smoking, charbroiled food |
| 2B6 | ~3% | Efavirenz, methadone, bupropion, cyclophosphamide | Ticlopidine | Rifampin |
| 2C8 | ~2% | Repaglinide, paclitaxel, rosiglitazone, amodiaquine | Gemfibrozil glucuronide | Rifampin |

---

## PK Parameter Reference

| Parameter | Symbol | Units | Typical Range | Clinical Notes |
|-----------|--------|-------|---------------|----------------|
| Bioavailability | F | % | 0-100 | <20% poor; >80% high; consider food effect |
| Volume of distribution | Vd | L/kg | 0.04-20+ | <0.1 intravascular; 0.1-0.7 extracellular; >0.7 tissue |
| Clearance | CL | L/h | Drug-specific | >hepatic blood flow (90 L/h) suggests extrahepatic CL |
| Half-life | t1/2 | h | 0.5-100+ | <2h frequent dosing; >24h QD feasible; dependent parameter |
| Protein binding | PB | % | 0-99.9 | >95% highly bound; DDI risk if displaced |
| Fraction unbound | fu | - | 0.001-1 | Only unbound drug is pharmacologically active |
| Absorption rate | ka | 1/h | 0.3-5 | IR: 0.5-3; ER: 0.1-0.5 |
| Hepatic extraction | ER | - | 0-1 | >0.7 high (flow-dependent CL); <0.3 low (capacity-dependent) |
| Renal fraction | fe | - | 0-1 | >0.3: renal adjustment likely needed |

---

## Evidence Grading

All PK/PD data must be graded by evidence tier to communicate confidence in parameter values and recommendations.

### Tier Definitions

| Tier | Label | Source | Confidence | Example |
|------|-------|--------|------------|---------|
| **T1** | Clinical PK Studies | Human PK studies (Phase I SAD/MAD, absolute bioavailability, mass balance, DDI studies, organ impairment studies) | Highest | FDA label Section 12.3, published clinical PK studies |
| **T2** | Population PK Models | PopPK analyses from Phase 2/3 data; Bayesian TDM models; exposure-response analyses | High | Published popPK papers, FDA clinical pharmacology reviews |
| **T3** | In Vitro ADME | Metabolic stability (microsomes, hepatocytes), CYP phenotyping, permeability (Caco-2), protein binding, CYP inhibition/induction, transporter studies | Moderate | ChEMBL ADME data, published in vitro ADME papers |
| **T4** | In Silico Predictions | PBPK model predictions, QSAR, allometric scaling from animals, in silico ADMET predictions | Supportive | Simcyp/GastroPlus predictions, allometric scaling results |

### Grading Rules

1. Always prefer T1 data over lower tiers. If T1 data exists, report it as the primary value.
2. When T1 data is unavailable, clearly state the tier of the reported value.
3. For DDI predictions: T3 in vitro data can trigger the need for T1 clinical DDI studies (per FDA guidance, R-value thresholds).
4. For FIH dose selection: T4 allometric predictions must be supported by at least T3 in vitro data for key parameters (CL, Vd).
5. In final reports, tag each PK parameter with its evidence tier:

```
| Parameter | Value | Unit | Tier | Source |
|-----------|-------|------|------|--------|
| t1/2 | 12.5 | h | T1 | FDA label (rivaroxaban) |
| CL/F | 10.2 | L/h | T1 | Phase I study (PMID: 12345678) |
| CYP3A4 Ki | 0.8 | uM | T3 | ChEMBL (CHEMBL25) |
| Human CL (predicted) | 8.5 | L/h | T4 | Allometric scaling (3 species) |
```

### Fallback Chains

```
PK parameters:    FDA label -> DrugBank details -> PubMed PopPK -> allometric prediction
DDI magnitude:    FDA label DDI studies -> ChEMBL Ki/IC50 -> static model -> case reports
Special pop PK:   FDA label (specific populations) -> PubMed studies -> physiological scaling
Dose optimization: FDA label dosing -> ClinTrials dose-ranging -> PubMed E-R -> model prediction
```

---

## Multi-Agent Coordination Examples

### Example 1: Comprehensive Drug Assessment (with drug-research skill)

When a user requests a full drug profile with detailed PK/PD analysis, coordinate with the drug-research skill:

**Handoff protocol:**

1. The drug-research skill generates the full monograph (identity, targets, trials, safety).
2. This clinical-pharmacology skill is invoked for deep-dive on:
   - Detailed PK parameter extraction with evidence grading
   - DDI risk assessment with R-value calculations
   - Dose optimization recommendations for special populations
   - Exposure-response analysis

**Trigger phrases for this skill (when drug-research identifies PK complexity):**
- "Needs detailed PK characterization" -> invoke clinical-pharmacology
- "Complex DDI profile" -> invoke clinical-pharmacology for R-value analysis
- "Narrow therapeutic index" -> invoke clinical-pharmacology for TDM protocol
- "Special population dosing needed" -> invoke clinical-pharmacology for dose adjustments

**Example coordination flow:**

```
User: "Give me a complete profile of tacrolimus including detailed PK and dosing"

Step 1 (drug-research): Generate drug monograph sections 1-11
Step 2 (clinical-pharmacology):
  - Extract PK parameters from FDA label (T1) and PopPK literature (T2)
  - Calculate DDI risk for common co-medications (CYP3A4 inhibitors/inducers)
  - Design TDM protocol with target trough ranges by indication
  - Provide dose adjustments for renal/hepatic impairment and pediatric patients
  - Score PK characterization (expected: 85-95/100 for tacrolimus)
Step 3: Merge outputs into unified report
```

### Example 2: Safety Signal Investigation (with adverse-event-detection skill)

When a safety signal is detected, this skill provides PK-based mechanistic explanation:

**Handoff protocol:**

1. The adverse-event-detection skill identifies a signal (e.g., elevated PRR for rhabdomyolysis with statin X).
2. This clinical-pharmacology skill is invoked to:
   - Determine if the signal correlates with supratherapeutic exposure
   - Evaluate DDI potential (was the signal driven by CYP inhibitor co-administration?)
   - Assess whether dose-dependent toxicity explains the signal
   - Check if special populations (CYP poor metabolizers, renal impairment) are overrepresented

**Example coordination flow:**

```
User: "Investigate rhabdomyolysis signal for simvastatin"

Step 1 (adverse-event-detection):
  - FAERS query -> PRR = 3.2 for rhabdomyolysis
  - Co-reported drugs analysis -> identify CYP3A4 inhibitors in reports

Step 2 (clinical-pharmacology):
  - Extract simvastatin PK: CYP3A4-dependent metabolism (fm ~ 0.95), t1/2 = 2-3h
  - DDI analysis: strong CYP3A4 inhibitors (itraconazole, clarithromycin)
    increase simvastatin AUC 10-20 fold
  - Dose-exposure-toxicity: rhabdomyolysis risk increases sharply above
    AUC threshold; 80mg dose withdrawn due to myopathy risk
  - Recommendation: the safety signal is mechanistically explained by
    CYP3A4 DDI-driven supratherapeutic exposure

Step 3: Combined report with PK-informed safety assessment
```

### Example 3: Biomarker-Guided Dose Selection (with biomarker-discovery skill)

**Handoff protocol:**

1. The biomarker-discovery skill identifies a PD biomarker correlated with efficacy.
2. This clinical-pharmacology skill:
   - Builds an exposure-biomarker-response model (Emax or sigmoid Emax)
   - Determines the target exposure (AUC or Cmin) that achieves desired biomarker modulation
   - Translates target exposure into dose recommendation
   - Accounts for PK variability to estimate probability of target attainment

**Example coordination flow:**

```
User: "What dose of Drug X achieves 90% target inhibition?"

Step 1 (biomarker-discovery):
  - Identify target biomarker (e.g., phospho-ERK) and its clinical threshold
  - Provide concentration-biomarker data from Phase 1b

Step 2 (clinical-pharmacology):
  - Fit sigmoid Emax model to concentration-biomarker data
  - Determine EC90 from model: EC90 = EC50 * 9^(1/n)
  - Use PopPK model to simulate doses achieving EC90 in >= 90% of patients
  - Account for between-subject variability in CL and Vd
  - Output: recommended dose with probability of target attainment analysis

Step 3: Unified dose recommendation with biomarker rationale
```

---

## Output Format

All clinical pharmacology analyses should follow this structure:

```
## Clinical Pharmacology Assessment: [Drug Name]

### 1. PK Parameter Summary
[Table with parameters, values, units, evidence tier, source]

### 2. Absorption and Distribution
[Bioavailability, food effect, protein binding, Vd, tissue distribution]

### 3. Metabolism and Elimination
[CYP enzymes, fm values, metabolites (active?), fe, routes of elimination, t1/2]

### 4. Drug-Drug Interaction Risk
[DDI matrix with R-values, clinical significance, dose adjustment recommendations]

### 5. Special Population Dosing
[Renal, hepatic, pediatric, geriatric, obesity recommendations with rationale]

### 6. Therapeutic Drug Monitoring
[Indication for TDM, target range, sampling strategy, dose adjustment algorithm]

### 7. PK/PD Score
[0-100 score with dimensional breakdown]

### 8. Evidence Summary
[All sources cited with tier classification]

### 9. Clinical Recommendations
[Actionable dosing recommendations with confidence level]
```

---

## Completeness Checklist

- [ ] PK parameters extracted with evidence tier assigned (T1-T4) for each value
- [ ] Absorption characterization complete (bioavailability, food effect, BCS class)
- [ ] Metabolism pathway identified (CYP enzymes, fm values, active metabolites)
- [ ] DDI risk assessed with R-value calculations for major CYP pathways
- [ ] Special population dosing addressed (renal, hepatic, pediatric, geriatric, obesity)
- [ ] Therapeutic drug monitoring protocol designed if NTI drug
- [ ] PK linearity and time-dependency evaluated across clinical dose range
- [ ] PK/PD scoring completed (0-100 across 5 dimensions)
- [ ] All sources cited with evidence tier classification
- [ ] Actionable dosing recommendations provided with confidence level
