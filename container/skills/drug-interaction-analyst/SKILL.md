---
name: drug-interaction-analyst
description: Drug-drug interaction analyst. Evaluates interactions through CYP450 enzyme metabolism, transporter effects, and pharmacodynamic mechanisms. Assigns evidence-based severity ratings and produces clinical management recommendations. Use when user mentions drug interaction, DDI, drug-drug interaction, CYP450, cytochrome P450, enzyme inhibition, enzyme induction, P-glycoprotein, P-gp, transporter, polypharmacy, contraindication, serotonin syndrome, QT prolongation, pharmacokinetic interaction, pharmacodynamic interaction, dose adjustment, or drug combination safety.
---

# Drug Interaction Analyst

Evaluates drug-drug interactions through CYP450 enzyme metabolism, transporter effects, and pharmacodynamic mechanisms. Assigns evidence-based severity ratings and produces clinical management recommendations with alternative drug suggestions. Uses DrugBank as the primary interaction source, supplemented by ChEMBL for mechanism data, FDA for labeling and adverse events, PubMed for literature evidence, Open Targets for target-level context, PubChem for compound safety data, and NLM for drug coding.

## Report-First Workflow

1. **Create report file immediately**: `[drug_pair]_drug-interaction-analyst_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Adverse event signal detection from interaction → use `pharmacovigilance-specialist`
- Genetic variation affecting metabolism (CYP polymorphisms) → use `pharmacogenomics-specialist`
- FDA labeling and regulatory status of interaction → use `fda-consultant`
- Clinical decision support for prescribing → use `clinical-decision-support`
- Target-level pharmacology of interacting drugs → use `drug-target-analyst`
- Comprehensive drug monograph or research report → use `drug-research`

## Available MCP Tools

### `mcp__drugbank__drugbank_info` (Primary Interaction Source)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_by_name` | Find drug by name | `query` |
| `get_drug_details` | Full drug profile (metabolism, enzymes, transporters) | `drugbank_id` |
| `get_drug_interactions` | Known drug-drug interactions with descriptions | `drugbank_id` |
| `get_similar_drugs` | Pharmacologically similar drugs (alternatives) | `drugbank_id`, `limit` |
| `get_pathways` | Metabolic/signaling pathways | `drugbank_id` |
| `search_by_target` | All drugs acting on a target | `target`, `limit` |
| `search_by_category` | Drugs by therapeutic category | `category`, `limit` |
| `search_by_structure` | Structural similarity search | `smiles` or `inchi`, `limit` |
| `search_by_carrier` | Drugs using same carrier protein | `carrier`, `limit` |
| `search_by_transporter` | Drugs using same transporter | `transporter`, `limit` |
| `get_external_identifiers` | Cross-database IDs (PubChem, ChEMBL, KEGG) | `drugbank_id` |

### `mcp__chembl__chembl_info` (Mechanism & Bioactivity)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets (CYP enzymes, transporters) | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki for CYP inhibition) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |
| `get_admet` | ADMET/drug-likeness properties | `chembl_id` |

### `mcp__fda__fda_info` (Drug Labels & Adverse Events)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drug_labels` | FDA-approved drug labeling (interactions section) | `query`, `limit` |
| `get_drug_label_details` | Full label text including warnings, contraindications | `application_number` or `spl_id` |
| `search_adverse_events` | FAERS adverse event reports | `query`, `limit` |
| `get_adverse_event_details` | Detailed adverse event case data | `safety_report_id` |
| `search_drug_recalls` | Drug recalls and safety alerts | `query`, `limit` |
| `search_drug_enforcement` | Enforcement actions | `query`, `limit` |
| `search_ndc` | National Drug Code directory | `query`, `limit` |
| `get_drug_shortages` | Current drug shortage information | `query` |

### `mcp__pubmed__pubmed_articles` (Interaction Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__opentargets__opentargets_info` (Target-Level Context)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `search_diseases` | Search diseases by name/synonym | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId`, `diseaseId`, `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes) | `id` (EFO ID) |

### `mcp__pubchem__pubchem_info` (Compound Info & Safety Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_compound` | Search compounds by name or identifier | `query`, `limit` |
| `get_compound_details` | Full compound profile (properties, identifiers) | `cid` |
| `get_compound_properties` | Molecular properties (weight, formula, logP) | `cid` |
| `get_compound_synonyms` | All names and synonyms for a compound | `cid` |
| `get_compound_classification` | Pharmacological classification hierarchy | `cid` |
| `get_compound_safety` | GHS hazard data, toxicity, LD50 | `cid` |
| `search_by_structure` | Structural similarity/substructure search | `smiles`, `search_type`, `limit` |
| `search_by_formula` | Find compounds by molecular formula | `formula`, `limit` |
| `get_bioassay_summary` | Bioassay results summary for a compound | `cid`, `limit` |
| `get_compound_targets` | Known biological targets | `cid`, `limit` |
| `get_compound_drug_interactions` | Interaction annotations from PubChem | `cid`, `limit` |
| `get_compound_pathways` | Pathway involvement | `cid`, `limit` |

### `mcp__nlm__nlm_ct_codes` (Drug Coding & RxTerms)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_rxterms` | Search RxNorm drug terms | `query`, `limit` |
| `get_rxterm_details` | RxNorm concept details | `rxcui` |
| `get_drug_interactions_rxnorm` | RxNorm-based interaction lookup | `rxcui` |
| `get_ndc_properties` | NDC code properties | `ndc` |
| `search_icd10` | Search ICD-10 codes | `query`, `limit` |
| `search_snomed` | Search SNOMED CT concepts | `query`, `limit` |
| `get_snomed_details` | SNOMED concept details | `sctid` |
| `search_loinc` | Search LOINC codes | `query`, `limit` |
| `get_loinc_details` | LOINC code details | `loinc_num` |
| `search_cpt` | Search CPT codes | `query`, `limit` |
| `get_rxclass_members` | Drug class members from RxClass | `class_id`, `relation`, `limit` |

### `mcp__kegg__kegg_data` (Pathway & Enzyme Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_enzymes` | Search enzymes by name (e.g., CYP3A4, CYP2D6) | `query` |
| `get_enzyme_info` | Enzyme details (reactions, substrates, inhibitors) | `enzyme_id` |
| `search_drugs` | Search KEGG drug entries | `query` |
| `get_drug_info` | Drug details (targets, interactions, metabolism) | `drug_id` |
| `get_drug_interactions` | Known drug-drug interactions from KEGG | `drug_id` |
| `search_compounds` | Search KEGG compounds by keyword | `query` |
| `get_compound_reactions` | Reactions involving a compound | `compound_id` |
| `convert_identifiers` | Convert between KEGG and external IDs | `identifiers`, `source_db`, `target_db` |

### `mcp__clinpgx__clinpgx_data` (PharmGKB / ClinPGx — PGx-Mediated Interactions)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_gene_drug_pairs` | Gene-drug interaction guidelines (PGx-mediated DDIs) | `gene`, `drug` |
| `get_clinical_annotations` | Clinical annotations for PGx-mediated interaction evidence | `gene` |
| `get_gene` | Metabolizing enzyme info (CYP2D6, CYP2C19, CYP3A4, etc.) | `gene` |

#### ClinPGx Workflow: Pharmacogenomic-Mediated Drug Interactions

Use ClinPGx to identify pharmacogenomic-mediated drug interactions (e.g., CYP2D6 poor metabolizer + codeine):

```
1. Identify PGx genes involved in the interacting drugs' metabolism:
   mcp__clinpgx__clinpgx_data(method="get_gene", gene="CYP2D6")
   → Gene function, polymorphism impact on drug metabolism

2. Check gene-drug pair guidelines for both drugs:
   mcp__clinpgx__clinpgx_data(method="get_gene_drug_pairs", gene="CYP2D6")
   → All drugs with PGx-guided recommendations for this enzyme

3. Review clinical annotations for interaction evidence:
   mcp__clinpgx__clinpgx_data(method="get_clinical_annotations", gene="CYP2D6")
   → Evidence linking metabolizer status to altered drug response
   → Identifies cases where genetic variation changes interaction severity
     (e.g., PM + CYP2D6 inhibitor = no additional effect vs NM + inhibitor = phenoconversion)

4. Integrate PGx status into interaction severity assessment:
   → Adjust risk score based on patient metabolizer phenotype
   → Flag interactions where genetic testing would change management
```

---

## Bidirectional Interaction Analysis Workflow

### Principle

Always analyze both directions: Drug A's effect on Drug B **AND** Drug B's effect on Drug A. A drug may be a victim (substrate whose levels change) in one direction and a perpetrator (inhibitor/inducer causing the change) in the other.

### Step 1: Identify Both Drugs and Their Metabolic Profiles

```
1. mcp__drugbank__drugbank_info(method: "search_by_name", query: "DRUG_A_NAME")
   -> Get DrugBank ID for Drug A

2. mcp__drugbank__drugbank_info(method: "search_by_name", query: "DRUG_B_NAME")
   -> Get DrugBank ID for Drug B

3. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DB_A")
   -> Drug A: metabolism enzymes, transporters, mechanism, pharmacodynamics

4. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DB_B")
   -> Drug B: metabolism enzymes, transporters, mechanism, pharmacodynamics
```

### Step 2: Query Known Interactions

```
1. mcp__drugbank__drugbank_info(method: "get_drug_interactions", drugbank_id: "DB_A")
   -> Check if Drug B appears in Drug A's interaction list

2. mcp__drugbank__drugbank_info(method: "get_drug_interactions", drugbank_id: "DB_B")
   -> Check if Drug A appears in Drug B's interaction list (may have different description)

3. mcp__nlm__nlm_ct_codes(method: "search_rxterms", query: "DRUG_A_NAME")
   -> Get RxCUI for Drug A

4. mcp__nlm__nlm_ct_codes(method: "get_drug_interactions_rxnorm", rxcui: "RXCUI_A")
   -> Cross-validate with RxNorm interaction data

5. mcp__pubchem__pubchem_info(method: "get_compound_drug_interactions", cid: "CID_A")
   -> Additional interaction annotations from PubChem
```

### Step 3: Analyze CYP450 Metabolism Mechanisms

```
1. mcp__chembl__chembl_info(method: "target_search", query: "CYP3A4")
   -> Get ChEMBL target ID for the relevant CYP enzyme

2. mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "DRUG_A_CHEMBL", target_id: "CYP_TARGET_ID", limit: 20)
   -> Drug A's inhibitory potency against specific CYP enzymes

3. mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "DRUG_B_CHEMBL", target_id: "CYP_TARGET_ID", limit: 20)
   -> Drug B's inhibitory potency against specific CYP enzymes

4. Build the interaction matrix:
   - Drug A inhibits CYP3A4 -> Drug B is CYP3A4 substrate -> Drug B levels increase
   - Drug B induces CYP2D6 -> Drug A is CYP2D6 substrate -> Drug A levels decrease
```

### Step 4: Assess Transporter-Mediated Interactions

```
1. mcp__drugbank__drugbank_info(method: "search_by_transporter", transporter: "P-glycoprotein")
   -> Identify if either drug is a P-gp substrate/inhibitor

2. mcp__drugbank__drugbank_info(method: "search_by_transporter", transporter: "OATP1B1")
   -> Check hepatic uptake transporter involvement

3. mcp__drugbank__drugbank_info(method: "search_by_carrier", carrier: "albumin")
   -> Protein binding displacement potential
```

### Step 5: Evaluate Pharmacodynamic Interactions

```
1. mcp__chembl__chembl_info(method: "get_mechanism", chembl_id: "DRUG_A_CHEMBL")
   -> Drug A mechanism of action

2. mcp__chembl__chembl_info(method: "get_mechanism", chembl_id: "DRUG_B_CHEMBL")
   -> Drug B mechanism of action

3. mcp__opentargets__opentargets_info(method: "get_target_details", id: "SHARED_TARGET_ENSEMBL")
   -> If both drugs act on the same target or pathway, assess additive/synergistic/antagonistic effects

4. mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DB_A")
   -> Pathway overlap analysis

5. mcp__kegg__kegg_data(method: "search_enzymes", query: "CYP3A4")
   -> Get KEGG enzyme entry with substrates, inhibitors, and reaction details
   mcp__kegg__kegg_data(method: "get_enzyme_info", enzyme_id: "1.14.14.1")
   -> Full enzyme record including all known reactions and drug substrates
```

### Step 6: Verify with FDA Labeling and Literature

```
1. mcp__fda__fda_info(method: "search_drug_labels", query: "DRUG_A_NAME interaction", limit: 5)
   -> FDA-approved interaction warnings

2. mcp__fda__fda_info(method: "search_adverse_events", query: "DRUG_A_NAME DRUG_B_NAME", limit: 20)
   -> Real-world adverse event reports when co-administered

3. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "DRUG_A DRUG_B interaction pharmacokinetic", num_results: 15)
   -> Published interaction studies

4. mcp__pubchem__pubchem_info(method: "get_compound_safety", cid: "CID_A")
   -> Safety and toxicity profile
```

### Step 7: Identify Alternatives

```
1. mcp__drugbank__drugbank_info(method: "get_similar_drugs", drugbank_id: "DB_A", limit: 10)
   -> Therapeutic alternatives for Drug A with potentially fewer interactions

2. mcp__drugbank__drugbank_info(method: "search_by_category", category: "THERAPEUTIC_CLASS", limit: 15)
   -> Same-class drugs that may avoid the interaction

3. For each alternative, repeat Step 2 to confirm no interaction with the other drug
```

---

## Interaction Mechanism Categories

### 1. CYP450 Enzyme Metabolism

CYP enzymes metabolize approximately 75% of clinically used drugs. An inhibitor or inducer of a CYP enzyme alters the plasma levels of drugs metabolized by that enzyme.

#### CYP450 Interaction Matrix

| CYP Enzyme | Fraction of Drug Metabolism | Notable Substrates | Notable Inhibitors | Notable Inducers |
|------------|---------------------------|--------------------|--------------------|------------------|
| **CYP3A4** | ~50% | Simvastatin, cyclosporine, midazolam, fentanyl | Ketoconazole, itraconazole, clarithromycin, ritonavir | Rifampin, carbamazepine, phenytoin, St. John's Wort |
| **CYP2D6** | ~25% | Codeine, metoprolol, fluoxetine, tamoxifen | Paroxetine, fluoxetine, quinidine, bupropion | Not significantly inducible |
| **CYP2C9** | ~10% | Warfarin, phenytoin, losartan, celecoxib | Fluconazole, amiodarone, metronidazole | Rifampin |
| **CYP2C19** | ~5% | Omeprazole, clopidogrel, diazepam, voriconazole | Omeprazole, fluvoxamine, fluconazole | Rifampin, efavirenz |
| **CYP1A2** | ~5% | Theophylline, caffeine, clozapine, tizanidine | Fluvoxamine, ciprofloxacin, cimetidine | Smoking, omeprazole, rifampin |

**Interaction consequence:**
- Inhibitor + Substrate -> Increased substrate levels (toxicity risk)
- Inducer + Substrate -> Decreased substrate levels (efficacy loss)
- Time-dependent inhibition (mechanism-based) -> Irreversible; effect persists after inhibitor clearance

### 2. Drug Transporter Effects

| Transporter | Location | Function | Interaction Effect |
|-------------|----------|----------|--------------------|
| **P-gp (MDR1)** | Gut, liver, kidney, BBB | Efflux pump, limits absorption and CNS entry | Inhibition -> increased oral bioavailability and CNS exposure |
| **OATP1B1/1B3** | Hepatocyte sinusoidal | Hepatic uptake | Inhibition -> increased plasma levels (statin myopathy) |
| **BCRP** | Gut, liver, kidney | Efflux pump | Inhibition -> increased bioavailability |
| **MRP2** | Liver canalicular, kidney | Biliary/renal excretion | Inhibition -> decreased clearance |
| **OCT1/2** | Liver, kidney | Organic cation uptake | Inhibition -> altered metformin disposition |
| **OAT1/3** | Kidney proximal tubule | Organic anion secretion | Inhibition -> decreased renal clearance |

### 3. Pharmacodynamic Interactions

| Type | Definition | Example |
|------|-----------|---------|
| **Additive** | Combined effect = sum of individual effects | NSAID + anticoagulant -> increased bleeding risk |
| **Synergistic** | Combined effect > sum of individual effects | Trimethoprim + sulfamethoxazole -> sequential folate pathway blockade |
| **Antagonistic** | One drug reduces the effect of another | Naloxone reverses opioid effects |
| **Potentiation** | One drug with no intrinsic effect enhances another | Clavulanic acid potentiates amoxicillin |

**High-risk pharmacodynamic interaction categories:**
- QT prolongation (additive): multiple QT-prolonging drugs
- Serotonin syndrome: SSRI + MAO inhibitor, SSRI + tramadol
- CNS depression (additive): opioid + benzodiazepine + antihistamine
- Hypotension (additive): antihypertensive + alpha-blocker + PDE5 inhibitor
- Bleeding risk (additive): anticoagulant + antiplatelet + NSAID
- Nephrotoxicity (additive): NSAID + ACE inhibitor + diuretic ("triple whammy")
- Hyperkalemia (additive): ACE inhibitor + potassium-sparing diuretic + potassium supplement

---

## Evidence Grading System

### 3-Star Evidence Grading

| Grade | Criteria | Source Verification |
|-------|----------|---------------------|
| **★★★** | FDA labeling contains contraindication or boxed warning; OR drug withdrawn/restricted due to interaction | `mcp__fda__fda_info(method: "search_drug_labels")` -> contraindication section |
| **★★** | Published clinical pharmacokinetic study demonstrating significant AUC/Cmax change (>2-fold); OR controlled clinical outcome study | `mcp__pubmed__pubmed_articles(method: "search_keywords")` -> clinical PK/PD studies |
| **★** | In vitro CYP inhibition data only; OR theoretical based on metabolic pathway overlap; OR case reports without controlled data | `mcp__chembl__chembl_info(method: "get_bioactivity")` -> CYP inhibition IC50 |

### Risk Score (0-100)

```
Risk Score = Mechanism Severity (0-40) x Evidence Strength (0-30) x Patient Safety Impact (0-30)

Mechanism Severity:
  35-40: Mechanism-based (irreversible) CYP inhibition of major pathway
  25-34: Strong reversible CYP inhibition (Ki < 1 uM) or P-gp inhibition at gut
  15-24: Moderate CYP inhibition (Ki 1-10 uM) or pharmacodynamic overlap
  5-14:  Weak CYP inhibition (Ki > 10 uM) or minor transporter effect
  0-4:   Theoretical only, no measured interaction

Evidence Strength:
  25-30: FDA contraindication or boxed warning
  15-24: Published clinical PK study with >2-fold AUC change
  8-14:  In vitro data with clinical extrapolation
  0-7:   Theoretical or single case report

Patient Safety Impact:
  25-30: Narrow therapeutic index drug (warfarin, digoxin, lithium, phenytoin)
  15-24: Serious ADR possible (QT prolongation, serotonin syndrome, bleeding)
  8-14:  Moderate ADR possible (hypotension, sedation, GI effects)
  0-7:   Mild or easily monitored effects
```

### Severity Classification

| Severity | Risk Score | Clinical Criteria | Action Required |
|----------|-----------|-------------------|-----------------|
| **Contraindicated** | 80-100 | FDA contraindication; life-threatening interaction documented | Do not co-administer; use alternative |
| **Major** | 60-79 | Significant harm possible; may require hospitalization | Avoid combination if possible; if unavoidable, intensive monitoring |
| **Moderate** | 30-59 | Clinically significant but manageable with monitoring | Dose adjustment and/or therapeutic drug monitoring |
| **Minor** | 0-29 | Unlikely to require intervention; theoretical concern | Awareness only; monitor if risk factors present |

---

## Clinical Management Recommendations Framework

### Decision Template

For each identified interaction, produce:

```
INTERACTION: [Drug A] + [Drug B]
DIRECTION: [Drug A -> Drug B] and/or [Drug B -> Drug A]
MECHANISM: [CYP inhibition/induction | Transporter effect | Pharmacodynamic]
DETAIL: [Specific enzyme/transporter/receptor involved]
EVIDENCE: [★ | ★★ | ★★★] — [source citation]
SEVERITY: [Contraindicated | Major | Moderate | Minor]
RISK SCORE: [0-100]
EXPECTED EFFECT: [Increased/decreased levels of X by Y-fold | Additive effect on Z]

MANAGEMENT:
1. Dose adjustment: [Specific recommendation or "not applicable"]
2. Monitoring: [Parameters, frequency — e.g., "INR every 3 days for 2 weeks"]
3. Timing separation: [Stagger administration by X hours, if applicable]
4. Alternative drugs: [List alternatives verified to lack this interaction]
5. Patient counseling: [Symptoms to watch for, when to seek medical attention]
```

### Alternative Drug Selection

```
1. mcp__drugbank__drugbank_info(method: "get_similar_drugs", drugbank_id: "INTERACTING_DRUG_DB_ID", limit: 10)
   -> Get therapeutic alternatives

2. For each alternative:
   a. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "ALT_DB_ID")
      -> Check metabolic pathway — does it avoid the problematic CYP enzyme?
   b. mcp__drugbank__drugbank_info(method: "get_drug_interactions", drugbank_id: "ALT_DB_ID")
      -> Confirm no interaction with the other drug in the pair

3. Rank alternatives by:
   - Lack of interaction with the other drug (required)
   - Similar therapeutic efficacy (preferred)
   - Established safety profile (preferred)
   - Same route of administration (preferred)
```

---

## Polypharmacy Cascade Interaction Detection

### For 5+ Medications

When a patient is on 5 or more medications, pairwise analysis is insufficient. Cascade interactions occur when Drug A affects Drug B's metabolism, which in turn alters Drug B's effect on Drug C.

### Polypharmacy Workflow

```
1. List all medications and obtain DrugBank IDs:
   For each drug: mcp__drugbank__drugbank_info(method: "search_by_name", query: "DRUG_NAME")

2. Build metabolic profile for each drug:
   For each drug: mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DB_ID")
   -> Extract: CYP substrates, CYP inhibitors/inducers, transporters, pharmacodynamic effects

3. Run pairwise interaction check for all combinations:
   For each pair: mcp__drugbank__drugbank_info(method: "get_drug_interactions", drugbank_id: "DB_ID")
   -> Number of pairs = n(n-1)/2

4. Identify cascade risks:
   - If Drug A inhibits CYP3A4, and Drug B is a CYP3A4 substrate AND a CYP2D6 inhibitor:
     Drug A -> raises Drug B levels -> Drug B now inhibits CYP2D6 more potently -> Drug C (CYP2D6 substrate) levels rise
   - Flag any chain where the intermediate drug has a narrow therapeutic index

5. Check for pharmacodynamic stacking:
   - Count how many drugs contribute to the same risk (QT prolongation, sedation, bleeding, etc.)
   - Three or more drugs with the same pharmacodynamic risk = high priority alert

6. Cross-validate with FDA adverse event data:
   mcp__fda__fda_info(method: "search_adverse_events", query: "DRUG_A DRUG_B DRUG_C", limit: 20)
   -> Real-world reports of harm from this combination
```

### Polypharmacy Report Format

```
PATIENT MEDICATION LIST:
1. [Drug A] — [indication] — [dose]
2. [Drug B] — [indication] — [dose]
...

INTERACTION MATRIX:
| Drug Pair | Mechanism | Severity | Risk Score |
|-----------|-----------|----------|------------|
| A + B     | ...       | ...      | ...        |
| A + C     | ...       | ...      | ...        |

CASCADE INTERACTIONS:
- [Description of chain interaction]

PHARMACODYNAMIC STACKING:
- QT prolongation risk: [Drug A, Drug C, Drug E] — 3 drugs contributing
- Bleeding risk: [Drug B, Drug D] — 2 drugs contributing

PRIORITY RECOMMENDATIONS:
1. [Highest risk interaction — recommended action]
2. [Second highest — recommended action]
```

---

## 13-Checkpoint Completeness Validation

Before finalizing any interaction analysis, verify all checkpoints are addressed:

| # | Checkpoint | Verification |
|---|-----------|-------------|
| 1 | **Drug identification** | Both drugs resolved to DrugBank IDs with confirmed names |
| 2 | **Bidirectional analysis** | Drug A->B AND Drug B->A directions both evaluated |
| 3 | **CYP450 assessment** | Substrate/inhibitor/inducer status checked for CYP1A2, 2C9, 2C19, 2D6, 3A4 |
| 4 | **Transporter assessment** | P-gp, OATP, BCRP involvement checked |
| 5 | **Pharmacodynamic overlap** | Shared mechanisms, additive toxicity risks evaluated |
| 6 | **Known interaction lookup** | DrugBank, RxNorm, and PubChem interaction databases queried |
| 7 | **FDA labeling check** | Contraindications and warnings sections reviewed |
| 8 | **Clinical evidence search** | PubMed searched for clinical PK/PD interaction studies |
| 9 | **Evidence grade assigned** | ★/★★/★★★ with source justification |
| 10 | **Risk score calculated** | Mechanism severity x evidence strength x patient safety impact |
| 11 | **Severity classified** | Contraindicated/Major/Moderate/Minor with clinical rationale |
| 12 | **Management plan provided** | Dose adjustment, monitoring, timing, alternatives, counseling |
| 13 | **Alternatives verified** | At least 2 alternative drugs confirmed to lack the interaction |

---

## Multi-Agent Workflow Examples

**"Check if my patient's medications interact — they take warfarin, amiodarone, and omeprazole"**
1. Drug Interaction Analyst -> Pairwise and cascade interaction analysis, CYP2C9/3A4/2C19 metabolism overlap, risk scoring, alternative anticoagulant or antiarrhythmic suggestions
2. Pharmacovigilance Specialist -> FAERS adverse event signals for this triple combination
3. Clinical Decision Support -> Dosing protocol with INR monitoring schedule

**"Is it safe to add fluconazole to a patient on simvastatin?"**
1. Drug Interaction Analyst -> CYP3A4/2C9 inhibition by fluconazole, predicted simvastatin AUC increase, rhabdomyolysis risk, statin alternatives (pravastatin, rosuvastatin)
2. FDA Consultant -> FDA labeling contraindication status, regulatory precedent
3. Pharmacogenomics Specialist -> CYP2C9 polymorphism impact on fluconazole metabolism

**"Evaluate serotonin syndrome risk for tramadol + sertraline combination"**
1. Drug Interaction Analyst -> Pharmacodynamic interaction (serotonin reuptake + weak serotonin activity), CYP2D6 inhibition by sertraline reducing tramadol activation, severity assessment
2. Pharmacovigilance Specialist -> FAERS case reports of serotonin syndrome with this pair
3. Drug Target Analyst -> Serotonin transporter binding affinity comparison, receptor selectivity profiles

**"Review a polypharmacy regimen: metformin, lisinopril, amlodipine, atorvastatin, metoprolol, aspirin, omeprazole"**
1. Drug Interaction Analyst -> Full 21-pair interaction matrix, cascade detection, pharmacodynamic stacking (hypotension from 3 antihypertensives), prioritized risk report
2. Clinical Decision Support -> Optimized regimen with timing recommendations
3. Pharmacogenomics Specialist -> CYP2C19 status for omeprazole, CYP2D6 status for metoprolol

---

## Completeness Checklist

- [ ] Both drugs resolved to DrugBank IDs with confirmed names
- [ ] Bidirectional analysis completed (Drug A→B and Drug B→A)
- [ ] CYP450 substrate/inhibitor/inducer status assessed for all major CYP enzymes
- [ ] Transporter involvement evaluated (P-gp, OATPs, BCRP)
- [ ] Pharmacodynamic overlap and additive toxicity risks documented
- [ ] Known interactions cross-validated across DrugBank, RxNorm, and PubChem
- [ ] FDA labeling reviewed for contraindications and warnings
- [ ] Evidence grade (star rating) assigned with source justification
- [ ] Risk score calculated and severity classified
- [ ] At least 2 alternative drugs verified to lack the interaction
