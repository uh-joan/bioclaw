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

### `mcp__hmdb__hmdb_data` (Metabolite-Level Interaction Detection)

Use HMDB to identify metabolites involved in drug interactions, map metabolic conjugate pathways, and detect metabolite-level interaction mechanisms (e.g., competitive inhibition of shared metabolic routes). Note: HMDB uses Cloudflare protection so some requests may be blocked intermittently.

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_metabolites` | Search for drug metabolites or conjugates involved in interactions | `query` (required), `limit` (optional, default 25) |
| `get_metabolite` | Comprehensive metabolite data including pathways and tissue locations | `hmdb_id` (required) |
| `get_metabolite_pathways` | Metabolic conjugate pathways — identify shared metabolic routes between interacting drugs | `hmdb_id` (required) |
| `get_metabolite_concentrations` | Normal and abnormal concentration data — detect interaction-altered metabolite levels | `hmdb_id` (required) |
| `search_by_mass` | Identify unknown interaction metabolites from mass spectrometry data | `mass` (required), `tolerance` (optional, default 0.05), `limit` (optional, default 25) |

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

**CRITICAL: If MCP tool calls fail or return no data, do NOT halt the analysis.** Use available clinical knowledge and whatever partial data was retrieved to complete the analysis. Always produce a full report with risk score, severity, and management — even if evidence is limited. Note data gaps explicitly.

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
| **CYP2C9** | ~10% | Warfarin (S-enantiomer), phenytoin, losartan, celecoxib | Fluconazole, amiodarone, metronidazole | Rifampin, phenytoin (auto-induction) |
| **CYP2C19** | ~5% | Omeprazole, clopidogrel (prodrug activation), diazepam, voriconazole | Omeprazole, fluvoxamine, fluconazole | Rifampin, efavirenz |
| **CYP1A2** | ~5% | Theophylline, caffeine, clozapine, tizanidine | Fluvoxamine, ciprofloxacin, cimetidine | Smoking, omeprazole, rifampin |

**Interaction consequence:**
- Inhibitor + Substrate -> Increased substrate levels (toxicity risk)
- Inducer + Substrate -> Decreased substrate levels (efficacy loss)
- Prodrug + Inhibitor -> DECREASED active metabolite (efficacy loss) — e.g., clopidogrel + CYP2C19 inhibitor
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
- Serotonin syndrome: SSRI + MAO inhibitor, SSRI + tramadol, SSRI + fentanyl/meperidine
- CNS depression (additive): opioid + benzodiazepine + antihistamine
- Hypotension (additive): antihypertensive + alpha-blocker + PDE5 inhibitor
- Bleeding risk (additive): anticoagulant + antiplatelet + NSAID
- Nephrotoxicity (additive): NSAID + ACE inhibitor + diuretic ("triple whammy")
- Hyperkalemia (additive): ACE inhibitor + potassium-sparing diuretic + potassium supplement
- Bradycardia/heart block: beta-blocker + non-dihydropyridine calcium channel blocker (verapamil/diltiazem)

---

## Complex Bidirectional Interactions (Both Drugs Are Perpetrators)

Some drug pairs involve mutual metabolic interference where each drug alters the other's metabolism simultaneously. These are high-complexity interactions requiring careful analysis of each direction independently.

### Recognition Pattern

A complex bidirectional interaction exists when:
- Drug A is **both** a substrate and inhibitor/inducer of an enzyme, AND
- Drug B is **both** a substrate and inhibitor/inducer of the same or different enzymes, AND
- The net effect on plasma levels is paradoxical or non-obvious

### Canonical Examples

**Phenytoin + Valproate (prototypical complex bidirectional):**
- Direction 1: Valproate **inhibits CYP2C9** → increases total phenytoin levels
- Direction 1 also: Valproate **displaces phenytoin from plasma protein binding** → increases free (unbound) phenytoin even further; total level may appear normal or even decrease while free level is toxic
- Direction 2: Phenytoin **induces CYP2C9, CYP2C19, and UGT enzymes** → accelerates valproate metabolism → decreases valproate levels
- Net result: Phenytoin toxicity risk (from increased free fraction) + reduced seizure protection from valproate
- **SEVERITY: Major** — requires free phenytoin monitoring, not total levels

**Warfarin + Phenytoin:**
- Direction 1: Phenytoin initially inhibits then induces CYP2C9 → biphasic warfarin effect
- Direction 2: Warfarin may inhibit phenytoin metabolism initially

### Analysis Protocol for Complex Bidirectional Pairs

```
1. Analyze EACH direction completely and independently:
   Direction A→B:
   - What CYP/UGT/transporter does Drug A affect?
   - Is Drug B a substrate of that pathway?
   - Predicted effect on Drug B levels?

   Direction B→A:
   - What CYP/UGT/transporter does Drug B affect?
   - Is Drug A a substrate of that pathway?
   - Predicted effect on Drug A levels?

2. Assess protein binding displacement:
   - Are both drugs highly protein-bound (>85%)?
   - Can one displace the other, increasing the free fraction?
   - Note: Total drug level may not reflect free (active) drug level

3. For paradoxical interactions (e.g., levels decrease but toxicity increases):
   - Distinguish total vs. free drug levels
   - Specify that standard monitoring may be misleading
   - Recommend free drug level monitoring where applicable

4. Assign SEPARATE risk scores for each direction
5. Report the HIGHER score as the overall interaction severity
```

---

## Evidence Grading System

### 3-Star Evidence Grading

| Grade | Criteria | Source Verification |
|-------|----------|---------------------|
| **★★★** | FDA labeling contains contraindication or boxed warning; OR drug withdrawn/restricted due to interaction | `mcp__fda__fda_info(method: "search_drug_labels")` -> contraindication section |
| **★★** | Published clinical pharmacokinetic study demonstrating significant AUC/Cmax change (>2-fold); OR controlled clinical outcome study | `mcp__pubmed__pubmed_articles(method: "search_keywords")` -> clinical PK/PD studies |
| **★** | In vitro CYP inhibition data only; OR theoretical based on metabolic pathway overlap; OR case reports without controlled data | `mcp__chembl__chembl_info(method: "get_bioactivity")` -> CYP inhibition IC50 |

---

## Risk Score Calculation (0–100)

**MANDATORY: A risk score MUST be calculated and reported for every interaction, even when data retrieval is partial or tool calls fail. Use available evidence and clinical knowledge; note data limitations explicitly.**

### Formula (ADDITIVE — sum the three components)

```
Risk Score = Mechanism Severity + Evidence Strength + Patient Safety Impact
             (0–40)              (0–30)               (0–30)
             ─────────────────────────────────────────────────────
             Maximum total: 100

Mechanism Severity (choose ONE range — select the HIGHEST applicable):
  35–40: Mechanism-based (irreversible) CYP inhibition of primary metabolic pathway
         OR complete blockade of prodrug activation (e.g., CYP2C19 inhibitor + clopidogrel)
         OR pharmacodynamic combination with documented life-threatening synergy (e.g., serotonin syndrome pair)
         OR IV calcium channel blocker + beta-blocker (direct cardiac conduction risk)
  25–34: Strong reversible CYP inhibition (Ki < 1 µM) of primary pathway
         OR P-gp inhibition substantially increasing bioavailability
         OR pharmacodynamic combination with serious additive risk (QT prolongation, bradycardia)
  15–24: Moderate CYP inhibition (Ki 1–10 µM) or secondary pathway affected
         OR moderate pharmacodynamic overlap (additive sedation, hypotension)
  5–14:  Weak CYP inhibition (Ki > 10 µM) or minor transporter effect
  0–4:   Theoretical only, no measured kinetic interaction

Evidence Strength (choose ONE range):
  25–30: FDA black box warning or contraindication label for this specific combination
  15–24: Published clinical PK study showing >2-fold AUC change OR documented serious clinical outcome
  8–14:  In vitro data + clinical extrapolation OR multiple case reports
  0–7:   Theoretical or single case report

Patient Safety Impact (choose ONE range):
  25–30: Narrow therapeutic index drug affected: warfarin, digoxin, lithium, phenytoin, cyclosporine,
         tacrolimus, theophylline — OR life-threatening ADR (cardiac arrest, severe serotonin syndrome,
         severe rhabdomyolysis)
  15–24: Serious ADR possible: QT prolongation, significant serotonin syndrome risk, major bleeding,
         severe bradycardia, respiratory depression
  8–14:  Moderate ADR possible: hypotension, sedation, GI effects, moderate bleeding risk
  0–7:   Mild or easily monitored effects
```

### Calibration Examples (use these to anchor your scoring)

| Drug Pair | Mech | Evid | Safety | Total | Severity |
|-----------|------|------|--------|-------|----------|
| Warfarin + fluconazole | 30 (strong CYP2C9 inhibitor + NTI substrate) | 25 (FDA warning + clinical PK data) | 28 (warfarin = NTI, major bleeding risk) | **83** | Contraindicated |
| Omeprazole + clopidogrel | 38 (blocks prodrug activation via CYP2C19) | 25 (FDA black box warning) | 20 (thrombosis/MACE risk) | **83** | Contraindicated/Major |
| Fluoxetine + tramadol | 37 (CYP2D6 inhibition + serotonergic PD synergy) | 22 (clinical case reports + PK data) | 22 (serotonin syndrome, seizure risk) | **81** | Contraindicated |
| Metoprolol + verapamil (IV) | 38 (additive AV node blockade) | 22 (clinical cases, FDA warning) | 22 (complete heart block, asystole) | **82** | Contraindicated (IV) |
| Metoprolol + verapamil (oral) | 28 (same mechanism, slower onset) | 18 (clinical PK + case data) | 20 (bradycardia, heart failure) | **66** | Major (oral) |
| Phenytoin + valproate | 32 (bidirectional: CYP2C9 inhibition + protein displacement + CYP induction) | 20 (clinical PK studies) | 26 (both NTI drugs; paradoxical free drug toxicity) | **78** | Major |
| Simvastatin + rifampin | 35 (strong CYP3A4 induction) | 18 (clinical PK data) | 15 (efficacy loss, not acute toxicity) | **68** | Major |

### Route-of-Administration Severity Rules

Some interactions are severity-dependent on the route. **Always specify route when it changes the classification:**

- **IV verapamil + any beta-blocker** → Contraindicated (risk of complete AV block, asystole)
- **Oral verapamil/diltiazem + beta-blocker** → Major (bradycardia/heart failure risk, requires monitoring)
- When route changes severity, report BOTH classifications explicitly:
  `SEVERITY: Contraindicated (IV route) / Major (oral route)`

---

## Severity Classification

| Severity | Risk Score | Clinical Criteria | Action Required |
|----------|-----------|-------------------|-----------------|
| **Contraindicated** | 80–100 | FDA contraindication or black box warning for this combination; OR life-threatening interaction documented in clinical studies; OR complete blockade of prodrug activation | Do not co-administer; mandate use of alternative |
| **Major** | 60–79 | Significant harm possible (hospitalization, serious ADR); established clinical PK interaction with NTI drug; OR same mechanism as Contraindicated but lower-risk route | Avoid if possible; if unavoidable, intensive monitoring with specific parameters and intervals |
| **Moderate** | 30–59 | Clinically significant but manageable; dose adjustment likely required | Dose adjustment and/or therapeutic drug monitoring; specify exact monitoring schedule |
| **Minor** | 0–29 | Unlikely to require intervention; theoretical or weak evidence | Awareness only; monitor if risk factors present |

### Severity Classification Rules

1. **When in doubt between Contraindicated and Major**: If the FDA label contains a boxed warning or explicit contraindication, classify as Contraindicated regardless of risk score.
2. **Route-specific interactions**: Report both severities when IV vs. oral route changes the classification (e.g., `Contraindicated (IV) / Major (oral)`).
3. **Prodrug activation blockade** (e.g., clopidogrel + CYP2C19 inhibitor): Classify as Contraindicated or Major because the pharmacodynamic consequence (thrombosis) is severe even though the mechanism is "decreased levels."
4. **NTI substrate + potent inhibitor**: Default to Contraindicated if the AUC increase is predicted to be >3-fold for a narrow therapeutic index drug.
5. **Bidirectional interactions**: Assign the HIGHER severity of the two directions as the overall classification.

---

## Clinical Management Recommendations Framework

### Decision Template

For each identified interaction, produce:

```
INTERACTION: [Drug A] + [Drug B]
DIRECTION: [Drug A → Drug B] and/or [Drug B → Drug A]
MECHANISM: [CYP inhibition/induction | Transporter effect | Pharmacodynamic | Mixed]
DETAIL: [Specific enzyme/transporter/receptor, e.g., "CYP2C9 inhibition reducing S-warfarin clearance by ~90%"]
EVIDENCE: [★ | ★★ | ★★★] — [source: FDA label / clinical PK study PMID / in vitro IC50]
SEVERITY: [Contraindicated | Major (oral) / Contraindicated (IV) | Moderate | Minor]
RISK SCORE: [calculated total] = [Mechanism: X] + [Evidence: Y] + [Safety: Z]
EXPECTED EFFECT: [e.g., "S-warfarin AUC increases ~2–3-fold; INR may double within 3–5 days"]

MANAGEMENT:
1. Dose adjustment: [Specific recommendation with numbers, e.g., "Reduce warfarin dose by 30–50%; resume
   pre-fluconazole dose upon discontinuation" — or "Not applicable; use alternative"]
2. Monitoring: [Parameters with frequency and duration, e.g., "Check INR daily for 5 days, then every
   3 days for 2 weeks; target INR 2–3"]
3. Alternative drugs: [Specific alternatives that avoid this interaction, e.g., "For antifungal: use
   micafungin or anidulafungin (no CYP2C9 inhibition); for anticoagulant: consider heparin bridge"]
4. Timing/sequencing: [Stagger by X hours if applicable; or "No timing separation resolves this interaction"]
5. Patient counseling: [Specific symptoms to report: e.g., "Report unusual bruising, blood in urine/stool,
   prolonged bleeding from cuts; seek emergency care for severe headache, coughing blood"]
```

### Management Specificity Requirements

Vague management is insufficient. Each recommendation **MUST** include:

- **Dose adjustment**: Specific percentage or absolute dose change (e.g., "reduce by 25–50%"), not just "consider dose reduction"
- **Monitoring**: Named parameter (INR, serum drug level, ECG QTc, serum potassium), frequency (daily / every 3 days / weekly), and duration (for 2 weeks / until stable)
- **Alternatives**: Named alternative drugs with brief rationale (e.g., "pravastatin — not metabolized by CYP3A4, no interaction with fluconazole")
- **Timing**: Specific hours if staggering helps (e.g., "separate by ≥2 hours"); state explicitly if timing does not resolve the interaction

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
| 2 | **Bidirectional analysis** | Drug A→B AND Drug B→A directions both evaluated; complex pairs analyzed per protocol above |
| 3 | **CYP450 assessment** | Substrate/inhibitor/inducer status checked for CYP1A2, 2C9, 2C19, 2D6, 3A4; prodrug activation noted |
| 4 | **Transporter assessment** | P-gp, OATP, BCRP involvement checked |
| 5 | **Pharmacodynamic overlap** | Shared mechanisms, additive toxicity risks evaluated |
| 6 | **Known interaction lookup** | DrugBank, RxNorm, and PubChem interaction databases queried |
| 7 | **FDA labeling check** | Contraindications and warnings sections reviewed; black box warnings noted |
| 8 | **Clinical evidence search** | PubMed searched for clinical PK/PD interaction studies |
| 9 | **Evidence grade assigned** | ★/★★/★★★ with source justification |
| 10 | **Risk score calculated** | Mechanism + Evidence + Safety components summed (0–100); all three components stated explicitly |
| 11 | **Severity classified** | Contraindicated/Major/Moderate/Minor with route-specific note if applicable; calibrated against reference examples |
| 12 | **Management plan provided** | Dose adjustment (specific %), monitoring (parameter + frequency + duration), named alternatives, patient counseling |
| 13 | **Alternatives verified** | At least 2 alternative drugs confirmed to lack the interaction with metabolic pathway rationale |

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
- [ ] Bidirectional analysis completed (Drug A→B and Drug B→A); complex bidirectional pairs analyzed per protocol
- [ ] CYP450 substrate/inhibitor/inducer status assessed for all major CYP enzymes; prodrug activation noted
- [ ] Transporter involvement evaluated (P-gp, OATPs, BCRP)
- [ ] Pharmacodynamic overlap and additive toxicity risks documented
- [ ] Known interactions cross-validated across DrugBank, RxNorm, and PubChem
- [ ] FDA labeling reviewed for contraindications, warnings, and black box warnings
- [ ] Evidence grade (star rating) assigned with source justification
- [ ] Risk score calculated with all three components (Mechanism + Evidence + Safety) explicitly stated
- [ ] Severity classified with route-specific note if applicable; checked against calibration examples
- [ ] Management includes specific dose % change, named monitoring parameters with frequency and duration, named alternative drugs
- [ ] At least 2 alternative drugs verified to lack the interaction with metabolic rationale
