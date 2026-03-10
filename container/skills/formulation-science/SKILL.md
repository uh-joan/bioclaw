---
name: formulation-science
description: "BCS classification, solubility enhancement, stability testing, excipient compatibility, dosage form design, bioavailability optimization"
---

# Formulation Science

Specialist in pharmaceutical formulation and drug delivery system design. Covers the full preformulation-to-product pipeline: BCS classification, physicochemical profiling, solubility enhancement strategies (salt selection, amorphous solid dispersions, lipid-based systems, cyclodextrin complexation, nanosuspensions), ICH-compliant stability testing, excipient compatibility screening, dosage form design (immediate release, modified release, parenteral, topical, inhalation), and bioavailability optimization. Integrates physicochemical data, regulatory precedent, and manufacturing feasibility into developability assessments and formulation recommendations.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_formulation_science_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Medicinal chemistry SAR optimization and structural alerts → use `medicinal-chemistry`
- PK/PD modeling, dose optimization, bioequivalence studies → use `clinical-pharmacology`
- FDA regulatory pathway selection and submission strategy → use `fda-consultant`
- Toxicology profiling and safety assessment → use `chemical-safety-toxicology`
- Drug-drug interaction prediction and clinical management → use `drug-interaction-analyst`
- Comprehensive drug monographs and compound disambiguation → use `drug-research`

## Cross-Reference: Other Skills

- **Comprehensive drug monographs, compound disambiguation** -> use drug-research skill
- **Medicinal chemistry, ADMET optimization, structural alerts** -> use medicinal-chemistry skill
- **PK/PD modeling, dose optimization, bioequivalence** -> use clinical-pharmacology skill
- **FDA regulatory pathways, labeling, approval strategies** -> use fda-consultant skill
- **Toxicology and safety profiling** -> use chemical-safety-toxicology skill
- **Drug-drug interaction analysis** -> use drug-interaction-analyst skill

## Available MCP Tools

### `mcp__drugbank__drugbank_data` (Formulation Data, Excipients, Dosage Forms)

| Method | Formulation use | Key parameters |
|--------|----------------|----------------|
| `search_drugs` | Find drug by name; retrieve available dosage forms and formulations | `query`, `limit` |
| `get_drug` | Full drug profile: dosage forms, route of administration, excipients, salt forms, PK parameters relevant to formulation | `drugbank_id` |
| `get_pharmacology` | Absorption characteristics, bioavailability, food effects — critical for BCS classification and formulation strategy | `drugbank_id` |

### `mcp__fda__fda_data` (Approved Formulations, Dissolution Specs)

| Method | Formulation use | Key parameters |
|--------|----------------|----------------|
| `search_drugs` | Find FDA-approved products and formulation precedent | `query`, `limit` |
| `get_drug_label` | Prescribing information: approved dosage forms, strengths, inactive ingredients, dissolution specifications, storage conditions | `drug_name` or `set_id` |

### `mcp__pubchem__pubchem_data` (Physicochemical Properties for Formulation)

| Method | Formulation use | Key parameters |
|--------|----------------|----------------|
| `search_compounds` | Compound lookup by name, CID, or SMILES | `query` |
| `get_compound` | Full compound record: structure, identifiers, synonyms | `cid` |
| `get_properties` | Physicochemical properties critical for formulation: MW, LogP, TPSA, H-bond donors/acceptors, rotatable bonds, exact mass | `cid` |

### `mcp__pubmed__pubmed_data` (Formulation Literature)

| Method | Formulation use | Key parameters |
|--------|----------------|----------------|
| `search` | Literature on formulation strategies, excipient studies, dissolution methods, stability data, bioavailability enhancement | `keywords`, `num_results` |
| `fetch_details` | Full article metadata and abstract for formulation studies | `pmid` |

### `mcp__chembl__chembl_data` (Compound Properties)

| Method | Formulation use | Key parameters |
|--------|----------------|----------------|
| `search_molecule` | Find compound ChEMBL ID from name, SMILES, or InChIKey | `query`, `limit` |
| `get_molecule` | Molecular properties: MW, LogP, LogD, PSA, aromatic rings, HBA/HBD — inputs for BCS classification and formulation design | `chembl_id` |

---

## Python Environment

The following packages are available for formulation computations:

```python
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit, minimize
from scipy.stats import f as f_dist, t as t_dist, norm
import statsmodels.api as sm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
```

All Python code should be executed via Bash tool using `python3 -c "..."` or by writing a script to a file and running it.

---

## Core Workflow 1: BCS Classification

The Biopharmaceutics Classification System (ICH M9) classifies drugs into four classes based on solubility and permeability, which directly dictates formulation strategy.

### BCS Decision Tree

```
                    High Permeability          Low Permeability
                   (Papp >= 1×10⁻⁴ cm/s)    (Papp < 1×10⁻⁴ cm/s)
High Solubility   ┌─────────────────┐        ┌─────────────────┐
(Dose/Solubility  │   CLASS I       │        │   CLASS III      │
 ratio < 250 mL)  │ Well absorbed   │        │ Permeability-    │
                   │ IR formulation  │        │ limited          │
                   └─────────────────┘        └─────────────────┘
Low Solubility    ┌─────────────────┐        ┌─────────────────┐
(Dose/Solubility  │   CLASS II      │        │   CLASS IV       │
 ratio >= 250 mL) │ Solubility-     │        │ Poor solubility  │
                   │ limited         │        │ & permeability   │
                   └─────────────────┘        └─────────────────┘
```

### BCS Classification Protocol

```
1. mcp__pubchem__pubchem_data(method: "search_compounds", query: "DRUG_NAME")
   -> Get PubChem CID

2. mcp__pubchem__pubchem_data(method: "get_properties", cid: "CID")
   -> Extract: MW, LogP, TPSA, H-bond donors, H-bond acceptors
   -> Estimate aqueous solubility from LogP if experimental data unavailable

3. mcp__drugbank__drugbank_data(method: "get_pharmacology", drugbank_id: "DBxxxxx")
   -> Extract: absorption %, bioavailability, Caco-2 permeability if available

4. mcp__fda__fda_data(method: "get_drug_label", drug_name: "DRUG_NAME")
   -> Check Clinical Pharmacology section for: food effect data, dissolution specs
   -> Food effect magnitude suggests solubility-limited absorption (BCS II/IV)

5. mcp__pubmed__pubmed_data(method: "search", keywords: "DRUG_NAME BCS classification solubility permeability", num_results: 10)
   -> Published BCS classification data, equilibrium solubility studies

6. mcp__chembl__chembl_data(method: "get_molecule", chembl_id: "CHEMBLxxxxx")
   -> LogP, LogD7.4, PSA — cross-reference with PubChem values
```

### Solubility Assessment

Solubility is determined at the highest dose strength across pH 1.0, 4.5, and 6.8 (37 +/- 1 degC):

| Parameter | High Solubility Criterion |
|-----------|--------------------------|
| Dose number (Do) | Do = Dose / (Cs x 250 mL) < 1 |
| pH range | Completely dissolves in 250 mL at all pH 1.0-6.8 |
| Temperature | 37 +/- 1 degC |
| Method | Shake-flask or USP intrinsic dissolution |

### Permeability Assessment

| Method | High Permeability Criterion |
|--------|----------------------------|
| Human PK (absolute BA) | >= 85% absorbed (mass balance or absolute BA) |
| In situ perfusion | Peff >= metoprolol reference |
| Caco-2 monolayer | Papp >= 1 x 10^-4 cm/s (or >= metoprolol) |
| MDCK-MDR1 | Efflux ratio < 2 and Papp A->B comparable to reference |

### Formulation Strategy by BCS Class

| BCS Class | Key Challenge | Primary Strategies |
|-----------|--------------|-------------------|
| I | None (well absorbed) | Simple IR tablet/capsule; biowaiver eligible (ICH M9) |
| II | Low solubility | Salt selection, particle size reduction, amorphous SD, SEDDS, cyclodextrins |
| III | Low permeability | Permeation enhancers, tight junction modulators, prodrug approach, minimize excipient variability |
| IV | Both | Combination of Class II + III strategies; lipid-based formulations, nanoparticles |

---

## Core Workflow 2: Solubility Enhancement

### 2.1 Salt Selection

Salt screening is the first-line strategy for ionizable compounds.

```
Decision criteria:
1. Is the compound ionizable? (pKa within 1-2 units of physiological pH)
   - Acids (pKa 3-7): pair with basic counterions (Na+, K+, Ca2+, Mg2+, meglumine, tromethamine)
   - Bases (pKa 6-10): pair with acidic counterions (HCl, mesylate, besylate, tosylate, maleate, fumarate, tartrate, citrate)

2. Evaluate salt properties:
   - Solubility ratio vs free form (target >= 3-fold improvement)
   - Hygroscopicity (DVS: < 0.5% w/w at 75% RH ideal)
   - Crystallinity (sharp XRPD peaks preferred for stability)
   - Melting point (higher mp generally = better physical stability)
   - Common ion effect risk in GI fluids
   - Disproportionation risk at intestinal pH

3. Regulatory precedent:
   - Check IIG database for approved counterions
   - Class 1 counterions (Na, K, Cl) have most regulatory precedent
```

### 2.2 Amorphous Solid Dispersions (ASD)

For BCS Class II compounds where salt selection is insufficient or the compound is non-ionizable.

| Parameter | Considerations |
|-----------|---------------|
| Polymer selection | HPMC-AS (preferred for enteric), PVP-VA (versatile), HPMC (broad compatibility), Soluplus (surfactant properties) |
| Drug loading | Typically 10-40% w/w; higher loading risks recrystallization |
| Tg rule | Target Tg_mixture >= 50 degC above storage temperature (Tg - Ts > 50 degC) |
| Manufacturing | Spray drying (lab-scale preferred), hot-melt extrusion (scale-up preferred), KinetiSol |
| Stability risk | Recrystallization from supersaturated state; must test under accelerated conditions |
| Characterization | mDSC (Tg, crystallinity), XRPD (amorphous halo), FTIR (drug-polymer interactions), dissolution (spring-and-parachute) |

### 2.3 Cyclodextrin Complexation

| Cyclodextrin | Cavity ID (A) | MW (Da) | Max IV conc | Key use |
|-------------|---------------|---------|-------------|---------|
| HP-beta-CD (Captisol) | 6.0-6.5 | ~1400 | 30% w/v | IV, oral; FDA IIG-listed |
| SBE-beta-CD (Captisol) | 6.0-6.5 | ~2163 | 30% w/v | IV solubilization; renal-safe |
| Gamma-CD (Cavamax W8) | 7.5-8.3 | 1297 | 23% w/v | Large molecule guests |
| Alpha-CD | 4.7-5.3 | 972 | 14.5% w/v | Small molecule guests |

Phase solubility study interpretation:
- **AL type**: linear increase; 1:1 stoichiometry; favorable
- **AP type**: positive deviation; higher-order complexes possible
- **BS type**: limited solubility of complex; precipitation risk
- **BI type**: insoluble complex; not suitable

### 2.4 Lipid-Based Drug Delivery Systems (LBDDS)

Lipid Formulation Classification System (LFCS):

| Type | Composition | Dispersion | Best for |
|------|-------------|-----------|----------|
| I | Oils only (e.g., soybean oil, MCT) | Coarse emulsion; needs bile salts | LogP > 4, oil-soluble drugs |
| II | Oils + water-insoluble surfactants (Cremophor EL, Span 80) | SEDDS; self-emulsifying | LogP 2-4, lipophilic drugs |
| IIIA | Oils + water-soluble surfactants + cosolvents | SMEDDS; fine emulsion | LogP 2-4, moderate solubility |
| IIIB | Water-soluble surfactants + cosolvents (low oil) | SNEDDS; nanoemulsion | LogP 1-3, partially water-soluble |
| IV | Water-soluble surfactants + cosolvents (no oil) | Micellar solution | LogP < 2 but poorly water-soluble |

Key excipients:
- **Oils**: MCT (Miglyol 812), long-chain triglycerides (soybean, olive), mono/diglycerides (Capmul MCM)
- **Surfactants**: Cremophor EL (HLB 12-14), polysorbate 80 (HLB 15), Gelucire 44/14 (HLB 14), Labrasol (HLB 12)
- **Cosolvents**: PEG 400, propylene glycol, Transcutol HP

### 2.5 Nanosuspensions

| Parameter | Specification |
|-----------|--------------|
| Target particle size | 200-800 nm (d50); PDI < 0.3 |
| Stabilizers | Polymeric: PVP K30, HPMC E5; Surfactant: SDS, poloxamer 188, TPGS |
| Production methods | Wet media milling (NanoCrystal), high-pressure homogenization, antisolvent precipitation |
| Advantages | Universal applicability; no need for solubility in vehicle; high drug loading |
| Risks | Ostwald ripening; crystal form change; aggregation |
| Characterization | DLS (size, PDI), zeta potential, XRPD (polymorph check), dissolution rate |

### 2.6 Cocrystals

```
Cocrystal screening strategy:
1. Select coformers based on:
   - Synthon matching (carboxylic acid-amide, acid-pyridine, hydroxyl-carbonyl)
   - pKa rule: delta-pKa < 0 favors cocrystal over salt
   - GRAS status or IIG-listed coformers preferred
   - Common coformers: saccharin, nicotinamide, glutaric acid, fumaric acid, citric acid

2. Screening methods:
   - Solvent-drop grinding (mechanochemistry)
   - Reaction crystallization (slurry in solvent)
   - Evaporative crystallization from coformer solutions

3. Confirmation:
   - XRPD: new diffraction pattern (not physical mixture or individual components)
   - DSC: single melting endotherm different from both components
   - Single-crystal XRD: definitive proof of cocrystal structure
```

---

## Core Workflow 3: Stability Testing Protocol Design

### ICH Stability Guidelines Overview

| Guideline | Scope |
|-----------|-------|
| Q1A(R2) | Stability testing of new drug substances and products |
| Q1B | Photostability testing |
| Q1C | Stability testing for new dosage forms |
| Q1D | Bracketing and matrixing designs |
| Q1E | Evaluation of stability data |
| Q1F | Stability data for registration in Climatic Zones III and IV (withdrawn; see WHO guidelines) |

### Long-Term and Accelerated Conditions

| Study | Conditions | Duration | Testing frequency |
|-------|-----------|----------|-------------------|
| Long-term (Zone I/II) | 25 degC +/- 2 / 60% RH +/- 5 | 12 months minimum (36 months for submission) | 0, 3, 6, 9, 12, 18, 24, 36 months |
| Intermediate | 30 degC +/- 2 / 65% RH +/- 5 | 12 months | 0, 6, 9, 12 months |
| Accelerated | 40 degC +/- 2 / 75% RH +/- 5 | 6 months | 0, 3, 6 months |
| Zone III (hot/dry) | 30 degC +/- 2 / 35% RH +/- 5 | 12 months | Per Q1A |
| Zone IVb (hot/humid) | 30 degC +/- 2 / 75% RH +/- 5 | 12 months | Per Q1A |

### Photostability Testing (ICH Q1B)

```
Option 2 (most common):
- Light source: Cool white fluorescent + near-UV lamp
- Exposure: >= 1.2 million lux-hours visible + >= 200 W*h/m2 UV
- Samples: Drug substance (API) and drug product
- Controls: Dark control (foil-wrapped, same conditions)
- Test: Assay, degradation products, appearance, dissolution

Decision tree:
1. Expose API → If degraded, assess packaging protection
2. Expose drug product in proposed packaging → If degraded, assess secondary packaging
3. If secondary packaging protects, include labeling: "Protect from light"
```

### Forced Degradation (Stress Testing)

| Stress Condition | Typical Protocol | Target Degradation |
|-----------------|-----------------|-------------------|
| Acid hydrolysis | 0.1 N HCl, 60 degC, 1-7 days | 5-20% |
| Base hydrolysis | 0.1 N NaOH, 60 degC, 1-7 days | 5-20% |
| Oxidative | 3% H2O2, RT, 1-7 days | 5-20% |
| Thermal | 60-80 degC, solid state, 1-4 weeks | 5-20% |
| Humidity | 75% RH, 40 degC, 1-4 weeks | 5-20% |
| Photolytic | ICH Q1B conditions (1.2M lux-h) | 5-20% |

Purpose: Demonstrate specificity of stability-indicating method, identify degradation pathways, support specification setting.

### Stability Protocol Design Workflow

```
1. mcp__drugbank__drugbank_data(method: "get_drug", drugbank_id: "DBxxxxx")
   -> Extract: known stability issues, storage conditions, salt form
   -> Identify functional groups prone to degradation (esters, amides, lactones, thiols)

2. mcp__fda__fda_data(method: "get_drug_label", drug_name: "DRUG_NAME")
   -> Approved storage conditions, in-use stability, reconstitution stability
   -> Existing shelf-life claims for reference listed drug (RLD)

3. mcp__pubchem__pubchem_data(method: "get_properties", cid: "CID")
   -> LogP, TPSA, functional groups — predict degradation susceptibility
   -> Highly polar (TPSA > 140): hydrolysis risk
   -> Low LogP with many HBDs: moisture sensitivity

4. mcp__pubmed__pubmed_data(method: "search", keywords: "DRUG_NAME stability degradation forced ICH", num_results: 15)
   -> Published degradation pathways, impurity profiles, stability-indicating methods
   -> Arrhenius activation energy data for shelf-life prediction

5. Compile protocol:
   -> Define storage conditions per ICH Q1A
   -> Set testing intervals and parameters
   -> Design container-closure system compatibility study
   -> Include in-use stability if applicable (multidose, reconstitution)
```

---

## Core Workflow 4: Excipient Compatibility

### Excipient Compatibility Study Design

```
Phase 1: Excipient selection rationale
- Identify functional category needed: filler, binder, disintegrant, lubricant, glidant,
  coating, surfactant, pH modifier, preservative, antioxidant
- Check IIG database (FDA Inactive Ingredient Guide) for approved precedent at intended route and dose
- Prefer excipients with established compendial monographs (USP-NF, EP, JP)

Phase 2: Binary compatibility screening
- Mix API with each candidate excipient (1:1 and 1:5 w/w ratios)
- Store open and closed at 40 degC / 75% RH for 2-4 weeks
- Analyze by: HPLC (assay, impurities), DSC, XRPD, visual appearance
- Flag any sample with > 5% assay loss or new impurity > 0.1%

Phase 3: Ternary/multicomponent screening
- Combine API with excipient pairs identified as compatible in Phase 2
- Test at prototype formulation ratios
- Include moisture-stressed samples (open dish at 75% RH)
```

### Common Excipients by Function

#### Fillers/Diluents

| Excipient | Key Properties | Compatibility Notes |
|-----------|---------------|-------------------|
| Microcrystalline cellulose (MCC, Avicel) | Compressible, inert, GRAS | Generally excellent; avoid with highly oxidizable APIs |
| Lactose monohydrate | Good flow, compressible | Maillard reaction with primary amines; avoid with aminoglycosides |
| Mannitol | Non-hygroscopic, sweet taste | Excellent for moisture-sensitive APIs; costlier |
| Dibasic calcium phosphate (DCP) | High density, pH-buffering | May reduce dissolution of weak bases due to alkaline microenvironment |
| Pregelatinized starch | Binder + filler dual function | Hygroscopic; moisture-sensitive APIs need caution |

#### Binders

| Excipient | Typical Use Level | Application |
|-----------|------------------|-------------|
| PVP (Povidone K30) | 2-5% w/w | Wet granulation and dry binder; hygroscopic |
| HPMC (Hypromellose) | 2-5% w/w | Wet granulation; also film-coating polymer |
| PVP-VA (Copovidone) | 2-5% w/w | Hot-melt extrusion; ASD polymer |
| HPC (Hydroxypropyl cellulose) | 2-6% w/w | Wet granulation; thermoplastic |
| Pregelatinized starch | 5-10% w/w | Direct compression binder-filler |

#### Disintegrants

| Excipient | Mechanism | Typical Level | Notes |
|-----------|-----------|--------------|-------|
| Croscarmellose sodium (CCS) | Swelling + wicking | 2-4% (intragranular + extragranular) | Most common superdisintegrant |
| Sodium starch glycolate (SSG) | Swelling | 2-8% | Works well in low-porosity tablets |
| Crospovidone (PVPP) | Wicking + strain recovery | 2-5% | Non-swelling; ideal for orally disintegrating tablets |

#### Lubricants

| Excipient | Typical Level | Notes |
|-----------|--------------|-------|
| Magnesium stearate | 0.25-1.0% | Most common; hydrophobic — overmixing retards dissolution |
| Sodium stearyl fumarate | 0.5-2.0% | Less hydrophobic than MgSt; better dissolution |
| Stearic acid | 1-3% | Less effective than MgSt; fewer dissolution issues |

#### Glidants

| Excipient | Typical Level | Notes |
|-----------|--------------|-------|
| Colloidal silicon dioxide (Aerosil) | 0.1-0.5% | Improves powder flow; may adsorb moisture |
| Talc | 1-2% | Flow aid and anti-adherent |

### Excipient Compatibility MCP Workflow

```
1. mcp__fda__fda_data(method: "get_drug_label", drug_name: "REFERENCE_PRODUCT")
   -> Inactive ingredient list of approved reference product
   -> Provides regulatory precedent for excipient selection

2. mcp__drugbank__drugbank_data(method: "get_drug", drugbank_id: "DBxxxxx")
   -> Known excipient interactions, formulation details of marketed products
   -> Salt form information (relevant to counterion-excipient interactions)

3. mcp__pubchem__pubchem_data(method: "get_properties", cid: "CID")
   -> Functional groups: primary amine (Maillard risk with lactose),
      thiol (oxidation risk), ester (hydrolysis risk with alkaline excipients)

4. mcp__pubmed__pubmed_data(method: "search", keywords: "DRUG_NAME excipient compatibility preformulation", num_results: 10)
   -> Published compatibility data, DSC thermograms, accelerated stability with excipients
```

---

## Core Workflow 5: Dosage Form Design

### 5.1 Immediate Release (IR) Oral Solid

#### Direct Compression vs. Wet Granulation Decision

```
Use Direct Compression when:
- API has adequate flow (Carr Index < 25%)
- API is compressible and dose allows sufficient filler
- No moisture-sensitive stability concerns
- Drug loading < 30% (generally)

Use Wet Granulation when:
- Poor flow or low bulk density API
- High drug loading (> 30-40%)
- Need to improve content uniformity (low-dose drugs < 2 mg)
- Segregation risk with direct compression blend

Use Dry Granulation (roller compaction) when:
- Moisture-sensitive or heat-sensitive API
- High drug loading requiring granulation for flow
- API incompatible with wet granulation solvents
```

#### Dissolution Testing (USP)

| Apparatus | USP # | Typical Use | Key Parameters |
|-----------|-------|-------------|----------------|
| Basket | I | Capsules, floating tablets | 50-100 rpm; 900 mL |
| Paddle | II | IR tablets (most common) | 50-75 rpm; 900 mL |
| Reciprocating cylinder | III | Extended release, beads | 6-35 dpm; 250 mL |
| Flow-through cell | IV | Poorly soluble drugs, implants | Open/closed loop; variable flow |

Dissolution media selection:
- **pH 1.2** (0.1 N HCl or SGF without enzymes): gastric simulation
- **pH 4.5** (acetate buffer): intermediate pH
- **pH 6.8** (phosphate buffer or SIF without enzymes): intestinal simulation
- **Surfactant addition**: SLS 0.1-2%, Tween 80 0.1-1% for BCS II drugs (justify biorelevance)
- **Biorelevant media**: FaSSIF (pH 6.5, 3 mM taurocholate), FeSSIF (pH 5.0, 15 mM taurocholate)

#### f2 Similarity Factor

Two dissolution profiles are considered similar if f2 >= 50 (indicating <= 10% average difference).

```
f2 = 50 * log10( [1 + (1/n) * SUM(Rt - Tt)^2]^(-0.5) * 100 )

Where:
  n  = number of time points (use only one point after 85% dissolved)
  Rt = reference % dissolved at time t
  Tt = test % dissolved at time t

Rules:
- Minimum 12 units per product
- Minimum 3 time points (excluding zero)
- Only one time point after both profiles reach >= 85% dissolution
- CV of early time points should be <= 20%; later points <= 10%
```

### 5.2 Modified Release

| Type | Mechanism | Common Polymers | Release Duration |
|------|-----------|----------------|-----------------|
| Extended Release (ER) | Matrix: drug dispersed in rate-controlling polymer | HPMC (Methocel K4M, K15M, K100M), ethylcellulose, Eudragit RS/RL | 12-24 hours |
| Delayed Release (DR) | Enteric coating dissolves above threshold pH | HPMC-AS, Eudragit L100-55 (pH 5.5), Eudragit L30D (pH 6.0), CAP | Gastric protection |
| Controlled Release (CR) | Osmotic pump or reservoir system | Cellulose acetate membrane + osmotic agents (NaCl, sorbitol) | 12-24 hours; zero-order |
| Pulsatile Release | Time-delayed burst release | Erodible coating or rupturable membrane | Chronotherapy |

Matrix tablet design considerations:
- **HPMC viscosity grade**: Higher viscosity = slower release (K100M > K15M > K4M)
- **Drug:polymer ratio**: Typically 1:1 to 1:3 for hydrophilic matrix
- **Drug solubility**: Soluble drugs suit hydrophilic matrices; insoluble drugs need hydrophobic matrices or osmotic systems
- **Erosion vs. diffusion**: High-solubility drugs release by diffusion; low-solubility drugs by erosion

### 5.3 Parenteral Formulations

| Parameter | Specification |
|-----------|--------------|
| Sterility | Aseptic processing or terminal sterilization |
| Particulate matter | USP <788>: <= 6000 particles >= 10 um, <= 600 particles >= 25 um (per container) |
| Endotoxin | <= 5 EU/kg/h (USP <85>); <= 0.5 EU/mL for IT |
| Osmolality | 280-320 mOsm/kg (isotonic); hypertonic OK for central line |
| pH | 3-9 acceptable (4-8 preferred to minimize pain) |
| Tonicity agents | NaCl, dextrose, glycerol |
| Solubilizers | Polysorbate 80 (0.01-0.1%), Cremophor EL, HP-beta-CD, SBE-beta-CD, PEG 300/400, DMSO (topical only) |
| Preservatives (multidose) | Benzyl alcohol (0.9-2%), phenol (0.25-0.5%), methylparaben + propylparaben |
| Antioxidants | Sodium metabisulfite, ascorbic acid, BHT, nitrogen purge, EDTA (chelator) |

### 5.4 Topical/Transdermal

| Dosage Form | Vehicle Type | Key Excipients |
|-------------|-------------|----------------|
| Cream (O/W) | Emulsion | Cetyl alcohol, stearyl alcohol, polysorbate 60, water |
| Cream (W/O) | Emulsion | Sorbitan monostearate, mineral oil, petrolatum |
| Ointment | Hydrocarbon base | White petrolatum, mineral oil, lanolin |
| Gel (hydrogel) | Aqueous polymer matrix | Carbomer 940/980, HPMC, poloxamer |
| Transdermal patch | Rate-controlling membrane or matrix | EVA membrane, silicone adhesive, acrylate adhesive |

Permeation enhancement strategies:
- Chemical enhancers: oleic acid, propylene glycol, Transcutol, Azone, terpenes (menthol, limonene)
- Physical methods: iontophoresis, microneedles, sonophoresis

### 5.5 Inhalation

| Platform | Particle Size Target | Device | Key Considerations |
|----------|---------------------|--------|-------------------|
| pMDI | 2-5 um MMAD | Pressurized metered-dose inhaler | Propellant (HFA-134a, HFA-227ea); cosolvent (ethanol); surfactant |
| DPI | 1-5 um MMAD | Dry powder inhaler | Carrier (lactose 60-90 um) + micronized drug; capsule or blister-based |
| Nebulizer | 1-5 um MMAD | Jet, ultrasonic, or vibrating mesh | Solution or nanosuspension; osmolality 150-550 mOsm |

Fine particle fraction (FPF): percentage of emitted dose < 5 um; target > 30-40% for deep lung deposition.

---

## Core Workflow 6: Bioavailability Optimization

### Bioavailability Enhancement Decision Tree

```
1. Determine rate-limiting step:
   a. Dissolution-limited (BCS II) -> go to step 2
   b. Permeability-limited (BCS III) -> go to step 3
   c. First-pass metabolism -> go to step 4
   d. Efflux transporter substrate (P-gp) -> go to step 5

2. Dissolution-limited strategies (in order of preference):
   a. Salt selection (if ionizable, pKa 3-10)
   b. Particle size reduction (micronization to 2-10 um; nanosizing to 200-800 nm)
   c. Amorphous solid dispersion (if Tg adequate, polymer available)
   d. Lipid-based formulation (SEDDS/SNEDDS for LogP > 2)
   e. Cyclodextrin complexation (if cavity fit demonstrated)
   f. Cocrystal (if non-ionizable or salt not feasible)

3. Permeability-limited strategies:
   a. Prodrug approach (lipophilic promoiety for passive permeation)
   b. Carrier-mediated transport exploitation (amino acid, peptide transporters)
   c. Permeation enhancers (C10, SNAC, Labrasol)
   d. Nanoparticulate systems (PLGA, chitosan NPs for M-cell uptake)

4. First-pass metabolism mitigation:
   a. Lymphatic delivery (long-chain triglyceride LBDDS, LogP > 5)
   b. CYP3A4 inhibitor co-formulation (ritonavir boosting concept)
   c. Alternative route: buccal, sublingual, transdermal
   d. Sustained release to avoid Cmax-driven saturation of metabolism

5. P-gp efflux mitigation:
   a. Surfactant-based inhibition (TPGS, Cremophor EL, polysorbate 80)
   b. Polymer-based inhibition (Pluronic P85, amphiphilic block copolymers)
   c. Nanoparticulate encapsulation (bypass efflux via endocytosis)
```

### Bioavailability Optimization MCP Workflow

```
1. mcp__drugbank__drugbank_data(method: "get_pharmacology", drugbank_id: "DBxxxxx")
   -> Absolute bioavailability, absorption mechanism, transporter involvement
   -> Identify if P-gp substrate, CYP3A4 substrate, first-pass extraction

2. mcp__pubchem__pubchem_data(method: "get_properties", cid: "CID")
   -> LogP, pKa, MW, TPSA -> predict rate-limiting step
   -> LogP > 5: consider lymphatic delivery
   -> TPSA > 140: likely permeability-limited

3. mcp__fda__fda_data(method: "get_drug_label", drug_name: "DRUG_NAME")
   -> Food effect data: significant food effect suggests dissolution-limited
   -> Approved formulations: what strategies has the originator used?

4. mcp__chembl__chembl_data(method: "get_molecule", chembl_id: "CHEMBLxxxxx")
   -> Molecular descriptors for formulation design
   -> Cross-reference LogP, PSA with PubChem values

5. mcp__pubmed__pubmed_data(method: "search", keywords: "DRUG_NAME bioavailability enhancement formulation", num_results: 15)
   -> Published BA studies, formulation comparisons, food effect investigations
```

### Food Effect Assessment

| Food Effect Type | BA Change | Formulation Implication |
|-----------------|-----------|------------------------|
| Positive food effect (increased AUC) | > 25% increase | Dissolution-limited; consider solubility enhancement to remove food requirement |
| Negative food effect (decreased AUC) | > 25% decrease | May indicate complexation with food or pH-dependent absorption |
| No significant food effect | < 25% change | Favorable; simpler dosing regimen |

---

## Formulation Developability Scoring (0-100)

Rate each compound on five dimensions to generate a composite developability score. Higher scores indicate better formulation tractability.

### Scoring Rubric

#### Physicochemical Properties (25%)

| Parameter | Score 0-5 | 5 (ideal) | 0 (challenging) |
|-----------|-----------|-----------|-----------------|
| Aqueous solubility | | > 1 mg/mL at pH 1-6.8 | < 1 ug/mL at all pH |
| LogP | | 1-3 | > 6 or < -1 |
| pKa | | Ionizable at physiological pH | Non-ionizable, LogP > 4 |
| Melting point | | 100-200 degC | > 300 degC (dissolution risk) or < 50 degC (processing risk) |
| Crystallinity | | Single stable polymorph | Polymorphic with low-energy conversions |
| Hygroscopicity | | < 0.5% w/w gain at 75% RH | > 5% w/w gain at 75% RH |

Subscore = (sum of individual scores / 30) * 25

#### Stability Profile (20%)

| Parameter | Score 0-5 | 5 (ideal) | 0 (challenging) |
|-----------|-----------|-----------|-----------------|
| Thermal stability | | No degradation at 60 degC / 4 weeks | > 10% degradation at 40 degC / 2 weeks |
| Hydrolytic stability | | Stable in pH 1-9 | Rapid hydrolysis at neutral pH |
| Oxidative stability | | No sensitivity to H2O2/peroxides | Rapid oxidation in 3% H2O2 |
| Photostability | | Stable under ICH Q1B conditions | Significant degradation under ambient light |

Subscore = (sum of individual scores / 20) * 20

#### Manufacturability (20%)

| Parameter | Score 0-5 | 5 (ideal) | 0 (challenging) |
|-----------|-----------|-----------|-----------------|
| Powder flow | | Carr Index < 15% (excellent) | Carr Index > 35% (very poor) |
| Compressibility | | Directly compressible | Requires specialized granulation |
| Scalability | | Standard equipment, ambient process | Requires cryogenic milling, inert atmosphere |
| Drug loading | | 1-25% (standard tablet) | > 60% or < 0.1% (content uniformity risk) |

Subscore = (sum of individual scores / 20) * 20

#### Biopharmaceutics (20%)

| Parameter | Score 0-5 | 5 (ideal) | 0 (challenging) |
|-----------|-----------|-----------|-----------------|
| BCS Class | | Class I | Class IV |
| Dissolution | | > 85% in 30 min at all pH | < 10% in 60 min |
| Permeability | | Papp > 10 x 10^-6 cm/s | Papp < 0.1 x 10^-6 cm/s |
| Efflux liability | | Not a P-gp substrate | High P-gp efflux ratio (> 5) |

Subscore = (sum of individual scores / 20) * 20

#### Regulatory/IP (15%)

| Parameter | Score 0-5 | 5 (ideal) | 0 (challenging) |
|-----------|-----------|-----------|-----------------|
| 505(b)(2) opportunity | | Strong RLD precedent, published PK | No precedent, NCE |
| Excipient precedent | | All excipients IIG-listed at route/dose | Novel excipient requiring separate safety package |
| Patent landscape | | FTO clear or expiring formulation patents | Broad formulation patents with long remaining life |

Subscore = (sum of individual scores / 15) * 15

### Composite Score

```
Total = Physicochemical + Stability + Manufacturability + Biopharmaceutics + Regulatory/IP

Interpretation:
  80-100: Highly developable — straightforward IR formulation likely feasible
  60-79:  Developable with optimization — one or two enhancement strategies needed
  40-59:  Challenging — multiple formulation hurdles; extended development timeline
  20-39:  Highly challenging — requires enabling formulation technology; high risk
  0-19:   Undevelopable without major molecular modification or novel delivery system
```

---

## Python Code Templates

### Dissolution Profile Fitting

```python
import numpy as np
from scipy.optimize import curve_fit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# --- Dissolution Models ---

def first_order(t, Qinf, k):
    """First-order dissolution: Q = Qinf * (1 - exp(-k*t))"""
    return Qinf * (1 - np.exp(-k * t))

def weibull(t, Qinf, a, b):
    """Weibull model: Q = Qinf * (1 - exp(-(t/a)^b))
    a = scale parameter (time), b = shape parameter
    b < 1: parabolic (initial burst), b = 1: exponential, b > 1: sigmoidal
    """
    return Qinf * (1 - np.exp(-((t / a) ** b)))

def higuchi(t, kH):
    """Higuchi square-root model: Q = kH * sqrt(t)
    For matrix-controlled release.
    """
    return kH * np.sqrt(t)

def korsmeyer_peppas(t, k, n):
    """Korsmeyer-Peppas: Q = k * t^n
    n = 0.5: Fickian diffusion (thin film)
    n = 0.5-1.0: anomalous transport
    n = 1.0: Case II transport (zero-order)
    Use only for first 60% of dissolution.
    """
    return k * (t ** n)

# --- Example: Fit dissolution data ---
# Replace with actual data
time_points = np.array([5, 10, 15, 20, 30, 45, 60, 90, 120])  # minutes
pct_dissolved = np.array([12, 28, 42, 55, 72, 88, 95, 98, 99])  # %

# Fit first-order
popt_fo, pcov_fo = curve_fit(first_order, time_points, pct_dissolved, p0=[100, 0.05], maxfev=5000)
Qinf_fo, k_fo = popt_fo

# Fit Weibull
popt_wb, pcov_wb = curve_fit(weibull, time_points, pct_dissolved, p0=[100, 30, 1], maxfev=5000)
Qinf_wb, a_wb, b_wb = popt_wb

# Calculate R-squared
def r_squared(y_obs, y_pred):
    ss_res = np.sum((y_obs - y_pred) ** 2)
    ss_tot = np.sum((y_obs - np.mean(y_obs)) ** 2)
    return 1 - (ss_res / ss_tot)

t_fit = np.linspace(0.1, 120, 500)

r2_fo = r_squared(pct_dissolved, first_order(time_points, *popt_fo))
r2_wb = r_squared(pct_dissolved, weibull(time_points, *popt_wb))

plt.figure(figsize=(10, 6))
plt.scatter(time_points, pct_dissolved, color='black', s=80, label='Observed', zorder=5)
plt.plot(t_fit, first_order(t_fit, *popt_fo), 'b--', label=f'First-order (R2={r2_fo:.4f})')
plt.plot(t_fit, weibull(t_fit, *popt_wb), 'r-', label=f'Weibull (R2={r2_wb:.4f})')
plt.xlabel('Time (min)')
plt.ylabel('% Dissolved')
plt.title('Dissolution Profile Fitting')
plt.legend()
plt.grid(True, alpha=0.3)
plt.ylim(0, 105)
plt.savefig('dissolution_fit.png', dpi=150, bbox_inches='tight')
print(f"First-order: Qinf={Qinf_fo:.1f}%, k={k_fo:.4f} min-1, R2={r2_fo:.4f}")
print(f"Weibull: Qinf={Qinf_wb:.1f}%, a={a_wb:.1f} min, b={b_wb:.2f}, R2={r2_wb:.4f}")
if b_wb < 1:
    print("Weibull shape b < 1: parabolic curve (burst release)")
elif b_wb == 1:
    print("Weibull shape b = 1: first-order-like")
else:
    print("Weibull shape b > 1: sigmoidal curve (lag phase)")
```

### f2 Similarity Factor Calculation

```python
import numpy as np

def f2_similarity(reference, test):
    """Calculate f2 similarity factor between two dissolution profiles.

    Args:
        reference: array of % dissolved at each time point (reference product)
        test: array of % dissolved at each time point (test product)

    Returns:
        f2 value (similar if >= 50)
    """
    n = len(reference)
    assert len(test) == n, "Profiles must have same number of time points"
    sum_sq = np.sum((np.array(reference) - np.array(test)) ** 2)
    f2 = 50 * np.log10(100 / np.sqrt(1 + sum_sq / n))
    return f2

# Example
time_pts = [5, 10, 15, 20, 30, 45, 60]  # minutes
ref = [15, 35, 55, 70, 85, 95, 98]       # reference % dissolved
test = [12, 30, 48, 65, 82, 93, 97]      # test % dissolved

f2_val = f2_similarity(ref, test)
print(f"f2 = {f2_val:.1f}")
print(f"Profiles are {'SIMILAR' if f2_val >= 50 else 'NOT SIMILAR'} (threshold: f2 >= 50)")
```

### Stability Shelf-Life Prediction (Arrhenius)

```python
import numpy as np
from scipy.optimize import curve_fit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def arrhenius_rate(T_celsius, A, Ea_R):
    """Arrhenius equation: k = A * exp(-Ea/RT)

    Args:
        T_celsius: temperature in Celsius
        A: pre-exponential factor
        Ea_R: Ea/R (activation energy / gas constant) in Kelvin
    """
    T_kelvin = T_celsius + 273.15
    return A * np.exp(-Ea_R / T_kelvin)

# Example: degradation rate constants at different temperatures
# Replace with actual experimental data
temps_C = np.array([40, 50, 60, 70])         # degC (accelerated conditions)
k_obs = np.array([0.002, 0.006, 0.018, 0.05])  # degradation rate constants (per month)

# Arrhenius linearization: ln(k) = ln(A) - Ea/(R*T)
T_kelvin = temps_C + 273.15
inv_T = 1 / T_kelvin
ln_k = np.log(k_obs)

# Linear regression
coeffs = np.polyfit(inv_T, ln_k, 1)
Ea_R = -coeffs[0]  # Ea/R in Kelvin
ln_A = coeffs[1]
A = np.exp(ln_A)
R = 8.314  # J/(mol*K)
Ea = Ea_R * R / 1000  # kJ/mol

# Predict rate at 25 degC (storage)
k_25 = arrhenius_rate(25, A, Ea_R)

# Shelf life: time to 10% degradation (90% remaining)
# For first-order: t90 = -ln(0.90) / k = 0.1054 / k
shelf_life_months = 0.1054 / k_25

print(f"Activation energy: Ea = {Ea:.1f} kJ/mol")
print(f"Rate at 25 degC: k = {k_25:.6f} per month")
print(f"Predicted shelf life (t90) at 25 degC: {shelf_life_months:.1f} months")
print(f"  = {shelf_life_months/12:.1f} years")

# Arrhenius plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(inv_T * 1000, ln_k, color='red', s=100, zorder=5, label='Experimental')
inv_T_fit = np.linspace(1/(70+273.15), 1/(25+273.15), 100)
ln_k_fit = np.log(A) - Ea_R * inv_T_fit
ax.plot(inv_T_fit * 1000, ln_k_fit, 'b--', label=f'Arrhenius fit (Ea={Ea:.1f} kJ/mol)')
ax.axvline(x=1000/(25+273.15), color='green', linestyle=':', alpha=0.7, label='25 degC')
ax.set_xlabel('1000/T (1/K)')
ax.set_ylabel('ln(k)')
ax.set_title('Arrhenius Plot: Shelf-Life Prediction')
ax.legend()
ax.grid(True, alpha=0.3)
plt.savefig('arrhenius_plot.png', dpi=150, bbox_inches='tight')
print("Arrhenius plot saved to arrhenius_plot.png")
```

### Particle Size Distribution Analysis

```python
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Example: laser diffraction data (volume-weighted)
# Replace with actual particle size distribution data
bin_edges = np.array([0.1, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500])  # um
vol_pct = np.array([0.5, 2.5, 8, 18, 25, 22, 15, 7, 2])  # volume % in each bin

bin_centers = np.sqrt(bin_edges[:-1] * bin_edges[1:])  # geometric mean
cumulative = np.cumsum(vol_pct)

# Interpolate d10, d50, d90
from scipy.interpolate import interp1d
interp_fn = interp1d(cumulative, bin_centers, kind='linear', fill_value='extrapolate')
d10 = float(interp_fn(10))
d50 = float(interp_fn(50))
d90 = float(interp_fn(90))
span = (d90 - d10) / d50

print(f"d10 = {d10:.1f} um")
print(f"d50 = {d50:.1f} um")
print(f"d90 = {d90:.1f} um")
print(f"Span = {span:.2f}")
print()

# Interpret for formulation
if d50 < 1:
    print("Nanosized particles — suitable for nanosuspension or nanoparticulate formulation")
elif d50 < 10:
    print("Micronized — suitable for inhalation (if MMAD 1-5 um) or enhanced dissolution")
elif d50 < 100:
    print("Conventional milled — standard for oral solid dosage forms")
else:
    print("Coarse — may require milling for adequate dissolution and content uniformity")

if span > 2.5:
    print(f"WARNING: Wide distribution (span={span:.2f}). Consider re-milling or classification.")

# Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.bar(range(len(vol_pct)), vol_pct, tick_label=[f"{bin_centers[i]:.1f}" for i in range(len(bin_centers))])
ax1.set_xlabel('Particle Size (um)')
ax1.set_ylabel('Volume %')
ax1.set_title('Particle Size Distribution')
ax1.tick_params(axis='x', rotation=45)

ax2.plot(bin_centers, cumulative, 'bo-', markersize=8)
ax2.axhline(y=10, color='gray', linestyle=':', alpha=0.5)
ax2.axhline(y=50, color='gray', linestyle=':', alpha=0.5)
ax2.axhline(y=90, color='gray', linestyle=':', alpha=0.5)
ax2.axvline(x=d10, color='green', linestyle='--', alpha=0.5, label=f'd10={d10:.1f}')
ax2.axvline(x=d50, color='red', linestyle='--', alpha=0.5, label=f'd50={d50:.1f}')
ax2.axvline(x=d90, color='blue', linestyle='--', alpha=0.5, label=f'd90={d90:.1f}')
ax2.set_xscale('log')
ax2.set_xlabel('Particle Size (um)')
ax2.set_ylabel('Cumulative Volume %')
ax2.set_title('Cumulative Distribution')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('particle_size_distribution.png', dpi=150, bbox_inches='tight')
print("Plot saved to particle_size_distribution.png")
```

### Design of Experiments (DoE) for Formulation Optimization

```python
import numpy as np
import pandas as pd
from itertools import product as iter_product
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# --- Full Factorial Design (2^3) ---
# Factors: polymer_conc (%), surfactant_conc (%), compression_force (kN)
factors = {
    'Polymer (%)': [5, 15],
    'Surfactant (%)': [0.5, 2.0],
    'Compression (kN)': [10, 30]
}

# Generate design matrix
levels = list(factors.values())
factor_names = list(factors.keys())
design = list(iter_product(*levels))
df_design = pd.DataFrame(design, columns=factor_names)

# Coded values (-1, +1)
df_coded = pd.DataFrame()
for col in factor_names:
    low, high = factors[col]
    center = (high + low) / 2
    half_range = (high - low) / 2
    df_coded[col] = (df_design[col] - center) / half_range

print("Full Factorial Design (2^3):")
print(df_design.to_string(index=False))
print()

# --- Response Surface Analysis (if you have response data) ---
# Example response: dissolution at 30 min (%)
# Replace with actual experimental data
responses = np.array([45, 72, 55, 85, 38, 65, 48, 78])
df_design['Dissolution_30min'] = responses

# Main effects
x1 = df_coded[factor_names[0]].values
x2 = df_coded[factor_names[1]].values
x3 = df_coded[factor_names[2]].values

# Effect calculation: average response at high - average response at low
effect_polymer = np.mean(responses[x1 > 0]) - np.mean(responses[x1 < 0])
effect_surfactant = np.mean(responses[x2 > 0]) - np.mean(responses[x2 < 0])
effect_compression = np.mean(responses[x3 > 0]) - np.mean(responses[x3 < 0])

# Interaction effects
effect_12 = np.mean(responses[x1*x2 > 0]) - np.mean(responses[x1*x2 < 0])
effect_13 = np.mean(responses[x1*x3 > 0]) - np.mean(responses[x1*x3 < 0])
effect_23 = np.mean(responses[x2*x3 > 0]) - np.mean(responses[x2*x3 < 0])

print("Main Effects:")
print(f"  {factor_names[0]}: {effect_polymer:+.1f}%")
print(f"  {factor_names[1]}: {effect_surfactant:+.1f}%")
print(f"  {factor_names[2]}: {effect_compression:+.1f}%")
print()
print("Interaction Effects:")
print(f"  {factor_names[0]} x {factor_names[1]}: {effect_12:+.1f}%")
print(f"  {factor_names[0]} x {factor_names[2]}: {effect_13:+.1f}%")
print(f"  {factor_names[1]} x {factor_names[2]}: {effect_23:+.1f}%")

# Pareto chart of effects
effects = [abs(effect_polymer), abs(effect_surfactant), abs(effect_compression),
           abs(effect_12), abs(effect_13), abs(effect_23)]
labels = [factor_names[0], factor_names[1], factor_names[2],
          f'{factor_names[0]}x{factor_names[1]}',
          f'{factor_names[0]}x{factor_names[2]}',
          f'{factor_names[1]}x{factor_names[2]}']

sorted_idx = np.argsort(effects)[::-1]
effects_sorted = [effects[i] for i in sorted_idx]
labels_sorted = [labels[i] for i in sorted_idx]

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(range(len(effects_sorted)), effects_sorted, color='steelblue')
ax.set_yticks(range(len(labels_sorted)))
ax.set_yticklabels(labels_sorted)
ax.set_xlabel('|Effect| on Dissolution (%)')
ax.set_title('Pareto Chart of Factor Effects')
ax.invert_yaxis()
plt.tight_layout()
plt.savefig('doe_pareto.png', dpi=150, bbox_inches='tight')
print("\nPareto chart saved to doe_pareto.png")
```

---

## Evidence Grading

All formulation claims and recommendations must be graded by evidence tier.

| Tier | Label | Source | Confidence |
|------|-------|--------|------------|
| T1 | Clinical BE/BA | Bioequivalence studies in humans, pivotal PK studies, FDA-approved labeling data | Highest — directly demonstrates in vivo performance |
| T2 | In Vivo Preclinical | Animal PK/BA studies, preclinical formulation comparisons, GLP tox formulation data | High — demonstrates in vivo relevance but species differences apply |
| T3 | In Vitro Data | Dissolution profiles (USP apparatus), stability data (ICH conditions), excipient compatibility, permeability (Caco-2), solubility (shake-flask) | Moderate — established regulatory acceptance but IVIVC not guaranteed |
| T4 | In Silico / Predictions | Computational solubility prediction, PBPK modeling, QSPR models, rule-based assessments (BCS prediction from LogP/MW) | Lowest — useful for screening and hypothesis generation |

### Evidence Grading Rules

1. **Always report the tier** alongside each data point or claim
2. **Prefer higher tiers**: T1 data overrides conflicting T3/T4 predictions
3. **Flag discrepancies**: if T3 dissolution data conflicts with T1 BE results, explicitly note and investigate
4. **IVIVC context**: in vitro dissolution (T3) may be elevated to T2-equivalent if a validated IVIVC (Level A) exists for the dosage form
5. **Regulatory weight**: FDA accepts T1 for biowaiver decisions; T3 for SUPAC changes; T4 only as supportive

### Evidence Application Examples

```
GOOD:
"Solubility of itraconazole at pH 6.8 is < 1 ug/mL [T3: shake-flask, USP],
 classifying it as BCS Class II. PBPK simulation predicts 40% oral BA
 from crystalline form [T4: GastroPlus]. The marketed Sporanox capsule
 (HP-beta-CD solution) achieves ~55% BA [T1: FDA label, NDA 020083]."

BAD:
"Itraconazole has low solubility and poor bioavailability."
(No tier, no quantification, no source)
```

---

## ICH Quality Guidelines Reference

| Guideline | Title | Formulation Relevance |
|-----------|-------|----------------------|
| Q1A(R2) | Stability Testing | Long-term, accelerated, and intermediate stability study design |
| Q1B | Photostability | Light exposure testing for API and drug product |
| Q1C | New Dosage Forms | Stability requirements for line extensions |
| Q1D | Bracketing and Matrixing | Reduced stability testing designs |
| Q1E | Evaluation of Stability Data | Statistical analysis, shelf-life estimation |
| Q2(R1) | Analytical Validation | Method validation for stability-indicating assays |
| Q3A(R2) | Impurities in New Drug Substances | Impurity identification and qualification thresholds |
| Q3B(R2) | Impurities in New Drug Products | Degradation product limits in formulations |
| Q3D(R2) | Elemental Impurities | Metal catalyst and excipient impurity limits |
| Q6A | Specifications | Setting acceptance criteria for drug substance and product |
| Q8(R2) | Pharmaceutical Development | Quality by Design (QbD), design space, CQAs, CPPs |
| Q9(R1) | Quality Risk Management | Risk assessment tools (FMEA, Ishikawa) for formulation |
| Q10 | Pharmaceutical Quality System | Lifecycle management of commercial products |
| Q11 | Development of Drug Substance | API form selection, particle engineering |
| Q12 | Lifecycle Management | Post-approval change management, established conditions |

---

## Key Formulation Abbreviations

| Abbreviation | Full Term |
|-------------|-----------|
| ASD | Amorphous Solid Dispersion |
| BA | Bioavailability |
| BCS | Biopharmaceutics Classification System |
| BE | Bioequivalence |
| CQA | Critical Quality Attribute |
| CPP | Critical Process Parameter |
| CR | Controlled Release |
| DC | Direct Compression |
| DoE | Design of Experiments |
| DPI | Dry Powder Inhaler |
| DR | Delayed Release |
| DSC | Differential Scanning Calorimetry |
| DVS | Dynamic Vapor Sorption |
| ER | Extended Release |
| FaSSIF | Fasted State Simulated Intestinal Fluid |
| FeSSIF | Fed State Simulated Intestinal Fluid |
| FPF | Fine Particle Fraction |
| GRAS | Generally Recognized as Safe |
| HME | Hot-Melt Extrusion |
| HP-beta-CD | Hydroxypropyl-beta-cyclodextrin |
| HPMC | Hydroxypropyl Methylcellulose (Hypromellose) |
| HPMC-AS | Hypromellose Acetate Succinate |
| IIG | Inactive Ingredient Guide (FDA) |
| IR | Immediate Release |
| IVIVC | In Vitro-In Vivo Correlation |
| LBDDS | Lipid-Based Drug Delivery System |
| MCC | Microcrystalline Cellulose |
| MCT | Medium-Chain Triglycerides |
| MMAD | Mass Median Aerodynamic Diameter |
| NDA | New Drug Application |
| PBPK | Physiologically Based Pharmacokinetic |
| PDI | Polydispersity Index |
| pMDI | Pressurized Metered-Dose Inhaler |
| PVP | Polyvinylpyrrolidone (Povidone) |
| PVP-VA | Polyvinylpyrrolidone-Vinyl Acetate (Copovidone) |
| QbD | Quality by Design |
| RLD | Reference Listed Drug |
| SBE-beta-CD | Sulfobutylether-beta-cyclodextrin |
| SEDDS | Self-Emulsifying Drug Delivery System |
| SLS | Sodium Lauryl Sulfate |
| SMEDDS | Self-Micro-Emulsifying Drug Delivery System |
| SNEDDS | Self-Nano-Emulsifying Drug Delivery System |
| SUPAC | Scale-Up and Post-Approval Changes |
| TPGS | D-alpha-Tocopheryl Polyethylene Glycol 1000 Succinate |
| TPSA | Topological Polar Surface Area |
| USP | United States Pharmacopeia |
| XRPD | X-Ray Powder Diffraction |

## Completeness Checklist

- [ ] BCS classification determined with supporting physicochemical data (solubility, permeability, LogP)
- [ ] Solubility enhancement strategy selected and justified (if BCS II/IV)
- [ ] Excipient compatibility assessed with rationale for each excipient choice
- [ ] Dosage form design specified with critical quality attributes (CQAs) defined
- [ ] ICH stability conditions identified and testing plan outlined
- [ ] Manufacturing process feasibility evaluated (scalability, critical process parameters)
- [ ] Bioavailability optimization strategy documented (food effects, formulation impact)
- [ ] Regulatory precedent reviewed via FDA-approved formulations for same or similar compounds
- [ ] Risk assessment completed for identified formulation challenges
- [ ] Literature evidence cited for key formulation decisions
