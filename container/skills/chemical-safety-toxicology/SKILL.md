---
name: chemical-safety-toxicology
description: Chemical safety and predictive toxicology specialist. ADMET assessment, structural alerts (PAINS, Brenk), drug-likeness (Lipinski, Veber, QED), toxicogenomics, hERG liability, hepatotoxicity prediction, genotoxicity, carcinogenicity, LD50 estimation, risk classification. Use when user mentions toxicology, ADMET, drug-likeness, Lipinski, PAINS, structural alert, hERG, hepatotoxicity, DILI, genotoxicity, AMES test, carcinogenicity, LD50, safety assessment, or compound triage.
---

# Chemical Safety & Toxicology Specialist

Predictive toxicology and compound safety assessment integrating structural alerts, drug-likeness rules, and multi-source safety data. 8-phase pipeline from compound identification through integrated risk assessment.

## Report-First Workflow

1. **Create report file immediately**: `compound_safety_toxicology_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Post-market adverse events and FAERS analysis → use `pharmacovigilance-specialist`
- Drug target off-target activity profiling → use `drug-target-analyst`
- Drug-drug interaction checking and clinical management → use `clinical-decision-support`
- Regulatory safety requirements and IND filing → use `fda-consultant`
- Risk management plans and benefit-risk assessment → use `risk-management-specialist`
- Medicinal chemistry scaffold optimization → use `medicinal-chemistry`

## Available MCP Tools

### `mcp__pubchem__pubchem`

| Method | Toxicology use |
|--------|---------------|
| `search_compounds` | Compound lookup by name/CID/SMILES |
| `get_compound_properties` | Molecular properties (MW, logP, PSA, rotatable bonds) |
| `get_safety_data` | GHS hazard classifications, signal words, pictograms |
| `search_similar_compounds` | Structural analogs for read-across toxicology |
| `get_compound_info` | Full compound record |
| `analyze_stereochemistry` | Stereo-specific toxicity assessment |

### `mcp__chembl__chembl_info`

| Method | Toxicology use |
|--------|---------------|
| `compound_search` | Find ChEMBL ID |
| `get_bioactivity` | Off-target activity data (hERG, CYP inhibition) |
| `get_admet` | ADMET properties, drug-likeness scores |
| `get_mechanism` | Mechanism — predict mechanism-based toxicity |

### `mcp__drugbank__drugbank_info`

| Method | Toxicology use |
|--------|---------------|
| `get_drug_details` | Toxicity section, contraindications, pharmacokinetics |
| `get_drug_interactions` | Metabolic interaction risks |
| `search_by_category` | Drugs in same class (class-effect toxicity) |
| `get_similar_drugs` | Safety data from similar approved drugs |
| `get_pathways` | Metabolic pathways (reactive metabolite risk) |
| `search_by_halflife` | Accumulation risk assessment |

### `mcp__fda__fda_info`

| Call | Toxicology use |
|------|---------------|
| `lookup_drug`, `search_type: "label"` | Nonclinical toxicology, carcinogenicity, reproductive toxicity sections |
| `lookup_drug`, `search_type: "adverse_events"` | Post-market toxicity signals |
| `lookup_drug`, `search_type: "recalls"` | Safety-related market withdrawals |

### `mcp__opentargets__opentargets_info`

| Method | Toxicology use |
|--------|---------------|
| `get_target_details` | Target safety — known on-target toxicities |
| `get_target_disease_associations` | Safety-related disease associations for targets |

### `mcp__pubmed__pubmed_articles`

Literature evidence for toxicity findings.

---

## Drug-Likeness Rules

### Lipinski Rule of Five

| Parameter | Limit | Rationale |
|-----------|-------|-----------|
| Molecular weight | ≤ 500 Da | Absorption barrier |
| LogP | ≤ 5 | Solubility/permeability |
| H-bond donors | ≤ 5 | Permeability |
| H-bond acceptors | ≤ 10 | Permeability |

**Violation threshold:** ≤1 violation acceptable. Biologics, natural products exempt.

### Extended Rules

| Rule Set | Key Criteria | Application |
|----------|-------------|-------------|
| **Veber** | Rotatable bonds ≤10, PSA ≤140 Å² | Oral bioavailability |
| **Ghose** | MW 160-480, logP -0.4 to 5.6, atoms 20-70, refractivity 40-130 | Drug-like range |
| **Egan** | PSA ≤132 Å², logP ≤5.88 | Absorption |
| **Rule of 3** | MW ≤300, logP ≤3, HBD ≤3, HBA ≤3, PSA ≤60, RotBonds ≤3 | Fragment-based screening |
| **CNS MPO** | MW, logP, logD, PSA, HBD, pKa optimized for BBB penetration | CNS drug candidates |
| **QED** | Quantitative Estimate of Drug-likeness (0-1, weighted desirability) | Overall drug-likeness score |

### Drug-Likeness Assessment Workflow

```
1. mcp__pubchem__pubchem(method: "get_compound_properties", cid: CID_NUMBER)
   → MW, logP, PSA, HBD, HBA, rotatable bonds

2. mcp__chembl__chembl_info(method: "get_admet", chembl_id: "CHEMBLxxxx")
   → QED score, calculated ADMET properties

3. Apply rule sets:
   - Lipinski: count violations
   - Veber: check RotBonds and PSA
   - Calculate QED if not available

4. Flag compounds failing >1 Lipinski rule or QED <0.3
```

---

## Structural Alert Detection

### PAINS (Pan-Assay Interference Compounds)

Substructures that cause false positives in biological assays via non-specific reactivity.

| Alert Class | Examples | Risk |
|-------------|----------|------|
| **Quinones** | Benzoquinone, naphthoquinone | Redox cycling, protein reactivity |
| **Catechols** | Catechol, hydroquinone | Oxidation to quinones |
| **Rhodanines** | Rhodanine scaffold | Non-selective binding |
| **Michael acceptors** | α,β-unsaturated carbonyls | Covalent protein modification |
| **Phenol-sulfonamides** | Certain sulfonamide patterns | Aggregation |

### Structural Toxicity Alerts

| Alert | Risk | Toxicity Type |
|-------|------|---------------|
| **Aniline** | Moderate | Genotoxicity (aromatic amine → metabolic activation) |
| **Nitroaromatics** | High | Genotoxicity (nitroreduction → reactive intermediates) |
| **Epoxides** | High | Genotoxicity (alkylation) |
| **Hydrazines** | High | Hepatotoxicity, genotoxicity |
| **Acyl halides** | High | Chemical reactivity |
| **Alkyl halides** | Moderate | Alkylation |
| **Peroxides** | High | Oxidative damage |
| **Azo compounds** | Moderate | Reductive metabolism to aromatic amines |
| **Polycyclic aromatics** | High | Carcinogenicity (DNA intercalation) |
| **Thiols** | Moderate | Oxidation, disulfide formation |

---

## Predictive Toxicity Endpoints

### Critical Endpoints

| Endpoint | Prediction Method | Regulatory Significance |
|----------|------------------|------------------------|
| **AMES mutagenicity** | Structural alerts + QSAR | ICH M7, FDA mutagenicity testing requirement |
| **hERG inhibition** | Electrophysiology / in silico | QTc prolongation → cardiac arrhythmia risk |
| **DILI (hepatotoxicity)** | Structural alerts + BSEP inhibition | Leading cause of drug withdrawals |
| **ClinTox** | Clinical trial toxicity prediction | Phase 1/2 attrition reduction |
| **Carcinogenicity** | 2-year rodent bioassay / transgenic models | ICH S1 testing requirement |
| **LD50** | EPA acute oral toxicity categories | GHS classification |
| **Phospholipidosis** | Cationic amphiphilic drug (CAD) assessment | Regulatory concern for chronic dosing |

### hERG Assessment

```
hERG IC50 interpretation:
  < 1 μM:  HIGH RISK — likely clinically significant QTc prolongation
  1-10 μM:  MODERATE RISK — may need thorough QT study
  > 10 μM:  LOW RISK — unlikely QTc concern
  > 30 μM:  MINIMAL RISK

Safety margin = hERG IC50 / free Cmax at therapeutic dose
  < 30x:  HIGH RISK
  30-100x:  MODERATE RISK
  > 100x:  LOW RISK
```

### DILI Risk Factors

| Factor | High Risk | Low Risk |
|--------|-----------|----------|
| Daily dose | >100 mg/day | <10 mg/day |
| Lipophilicity | LogP >3 | LogP <1 |
| Reactive metabolites | GSH adducts detected | No reactive metabolites |
| BSEP inhibition | IC50 <25 μM | IC50 >100 μM |
| Mitochondrial toxicity | Disrupts ETC | No effect |

---

## Risk Classification Matrix

| Level | Criteria | Action |
|-------|----------|--------|
| **Critical** | Failed AMES + structural alert, hERG IC50 <1 μM, known carcinogen structure | Stop development, redesign scaffold |
| **High** | DILI risk factors present, multiple structural alerts, QED <0.2 | Requires extensive preclinical safety testing before advancement |
| **Medium** | Single structural alert, moderate hERG (1-10 μM), 1 Lipinski violation | Proceed with monitoring, plan mitigation studies |
| **Low** | Drug-like properties, no alerts, clean hERG | Standard safety testing program |
| **Insufficient Data** | Cannot assess — no structural/activity data available | Generate data before decision |

---

## 8-Phase Safety Assessment Pipeline

```
Phase 1: Compound Identification
  mcp__pubchem__pubchem(method: "search_compounds", query: "compound_name", search_type: "name")
  → Resolve to CID, canonical SMILES, InChI

Phase 2: Molecular Properties
  mcp__pubchem__pubchem(method: "get_compound_properties", cid: CID)
  → MW, logP, PSA, HBD, HBA, RotBonds, complexity
  Apply Lipinski, Veber, QED rules

Phase 3: Structural Alert Screen
  Identify PAINS, toxicophores, reactive substructures from SMILES
  Flag by alert class and severity

Phase 4: GHS Safety Data
  mcp__pubchem__pubchem(method: "get_safety_data", cid: CID)
  → Hazard statements, signal words, LD50 data

Phase 5: Bioactivity Safety Profile
  mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "CHEMBLxxxx")
  → hERG activity, CYP inhibition, off-target hits
  mcp__chembl__chembl_info(method: "get_admet", chembl_id: "CHEMBLxxxx")
  → Predicted ADMET properties

Phase 6: Drug Comparator Safety
  mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
  → Toxicity section, known ADRs, contraindications
  mcp__drugbank__drugbank_info(method: "get_similar_drugs", drugbank_id: "DBxxxxx")
  → Safety data from similar approved drugs

Phase 7: Regulatory Safety Data
  mcp__fda__fda_info(method: "lookup_drug", search_term: "drug_name", search_type: "label")
  → Nonclinical toxicology, carcinogenicity, reproductive toxicity
  mcp__fda__fda_info(method: "lookup_drug", search_term: "drug_name", search_type: "recalls")
  → Safety-related withdrawals for class

Phase 8: Integrated Risk Assessment
  Assign risk classification (Critical/High/Medium/Low)
  Generate evidence summary with citations
  Recommend: proceed / proceed with conditions / stop
```

---

## Multi-Agent Workflow Examples

**"Assess the safety of our lead compound before IND filing"**
1. Chemical Safety & Toxicology → Full 8-phase pipeline, risk classification, structural alerts
2. Drug Target Analyst → On-target vs off-target activity profile
3. FDA Consultant → IND safety requirements, nonclinical study design

**"Why was this drug withdrawn? Could we redesign it?"**
1. Chemical Safety & Toxicology → Structural alert analysis, identify toxicophore
2. Pharmacovigilance Specialist → FAERS data, adverse event characterization
3. Drug Repurposing Analyst → Similar compounds without the toxicophore

---

## Completeness Checklist

- [ ] Compound resolved to CID with canonical SMILES and structure confirmed
- [ ] Molecular properties assessed against Lipinski, Veber, and QED rules
- [ ] Structural alerts screened (PAINS, toxicophores, reactive substructures)
- [ ] GHS safety data retrieved (hazard statements, signal words, LD50)
- [ ] hERG liability assessed with safety margin calculation
- [ ] DILI risk factors evaluated (daily dose, lipophilicity, reactive metabolites, BSEP)
- [ ] AMES mutagenicity risk assessed via structural alerts
- [ ] Drug comparator safety data retrieved from approved analogs
- [ ] Risk classification assigned (Critical/High/Medium/Low)
- [ ] Final recommendation provided (proceed / proceed with conditions / stop)
