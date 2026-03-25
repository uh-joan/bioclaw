---
name: drug-research
description: Comprehensive drug research report generator. Compound disambiguation, evidence grading, and full drug monographs covering identity, chemistry, pharmacology, targets, clinical trials, safety, pharmacogenomics, ADMET, and regulatory status. Use when user mentions drug research, drug report, drug monograph, compound research, drug profile, drug review, compound analysis, drug dossier, drug summary, investigational drug, approved drug review, or comprehensive drug analysis.
---

# Drug Research

> **Code recipes**: See [recipes.md](recipes.md) for copy-paste executable code templates.
> **Boltz-2 recipes**: See [boltz-recipes.md](boltz-recipes.md) for drug-target docking, binding affinity prediction, covalent binding, and competitive drug comparison via Boltz-2.

Generates comprehensive drug research reports with compound disambiguation, evidence grading, and 11 mandatory sections. Uses 8 MCP servers for full-spectrum pharmaceutical intelligence: FDA regulatory data, DrugBank pharmacology, ChEMBL bioactivity, PubMed literature, PubChem chemistry, ClinicalTrials.gov trials, Open Targets genetics, and bioRxiv preprints.

## Report-First Workflow

1. **Create report file immediately**: `[compound]_drug-research_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- FDA regulatory deep-dives (510(k), patent cliffs, Orange/Purple Book) → use `fda-consultant`
- Target validation and druggability (SAR, target-disease evidence) → use `drug-target-analyst`
- Adverse event signal detection (FAERS analysis, safety signals) → use `pharmacovigilance-specialist`
- Drug-drug interaction analysis (CYP inhibition, transporter effects) → use `drug-interaction-analyst`
- Pharmacogenomic variant interpretation (CYP polymorphisms, dosing) → use `pharmacogenomics-specialist`
- Clinical trial design and pipeline intelligence → use `clinical-trial-analyst`

## Available MCP Tools

### `mcp__fda__fda_info` (FDA Regulatory & Safety Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search FDA drug database by name or active ingredient | `query`, `limit` |
| `get_drug_label` | Full prescribing information (indications, warnings, dosing) | `set_id` or `drug_name` |
| `get_adverse_events` | FAERS adverse event reports | `drug_name`, `limit`, `serious` |
| `search_by_active_ingredient` | Find all products containing an ingredient | `ingredient`, `limit` |
| `get_drug_interactions` | FDA-reported drug interactions | `drug_name` |
| `get_recalls` | Drug recall history | `drug_name`, `limit` |
| `get_approvals` | FDA approval history and dates | `drug_name` |
| `search_devices` | Search medical devices (combination products) | `query`, `limit` |

### `mcp__drugbank__drugbank_info` (Pharmacology & Drug Profiles)

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

### `mcp__chembl__chembl_info` (Bioactivity & Medicinal Chemistry)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |
| `get_admet` | ADMET/drug-likeness properties | `chembl_id` |

### `mcp__pubmed__pubmed_articles` (Biomedical Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search by journal, date range | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details (abstract, authors, MeSH) | `pmid` |

### `mcp__pubchem__pubchem_info` (Chemical Identity & Properties)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_by_name` | Find compound by name | `name` |
| `get_compound_properties` | Physicochemical properties (MW, logP, TPSA, etc.) | `cid` |
| `get_compound_synonyms` | All known names, trade names, codes | `cid` |
| `get_compound_classification` | Pharmacological classification | `cid` |
| `get_compound_description` | Compound summary/description | `cid` |
| `search_by_smiles` | Search by SMILES structure | `smiles` |
| `search_by_formula` | Search by molecular formula | `formula` |
| `get_similar_compounds` | Structural similarity search | `cid`, `threshold`, `limit` |
| `get_compound_assays` | Bioassay results | `cid`, `limit` |
| `get_compound_patents` | Patent mentions | `cid`, `limit` |
| `get_compound_safety` | GHS hazard, toxicity data | `cid` |
| `get_compound_vendors` | Commercial availability | `cid`, `limit` |

### `mcp__ctgov__ctgov_info` (Clinical Trials)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_studies` | Search clinical trials by drug/condition | `query`, `status`, `phase`, `limit` |
| `get_study_details` | Full trial record (design, endpoints, results) | `nct_id` |
| `get_study_results` | Published trial results | `nct_id` |
| `search_by_intervention` | Find trials by specific intervention | `intervention`, `limit` |

### `mcp__opentargets__opentargets_info` (Genetic & Target Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `search_diseases` | Search diseases by name/synonym | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId`, `diseaseId`, `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes) | `id` (EFO ID) |

### `mcp__reactome__reactome_data` (Pathway Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `find_pathways_by_gene` | Pathways containing a gene | `gene_id`, `species` |
| `find_pathways_by_disease` | Pathways associated with disease | `disease_name` |
| `get_pathway_details` | Full pathway info | `pathway_id` |

### `mcp__kegg__kegg_data` (Drug & Compound Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search KEGG drug entries by name | `query` |
| `get_drug_info` | Drug details (targets, interactions, pathways, ATC codes) | `drug_id` |
| `get_drug_interactions` | Known drug interactions from KEGG | `drug_id` |
| `search_compounds` | Search KEGG compounds by keyword | `query` |
| `get_compound_info` | Compound details (formula, reactions, pathways) | `compound_id` |
| `search_diseases` | Search KEGG disease entries | `query` |
| `get_disease_info` | Disease details (genes, drugs, pathways) | `disease_id` |
| `search_pathways` | Search KEGG pathways by keyword | `query` |
| `get_pathway_info` | Full pathway details | `pathway_id` |
| `convert_identifiers` | Convert between KEGG and external IDs (DrugBank, PubChem, ChEMBL) | `identifiers`, `source_db`, `target_db` |

### `mcp__clinpgx__clinpgx_data` (Pharmacogenomic Considerations)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_gene_drug_pairs` | PGx considerations for gene-drug pairs | `gene`, `drug` |
| `get_drug_labels` | PGx labeling requirements for a drug | `drug` |

**ClinPGx workflow:** Check ClinPGx for pharmacogenomic considerations that may affect drug development strategy.

```
1. mcp__clinpgx__clinpgx_data(method: "get_drug_labels", drug: "DRUG_NAME")
   → PGx labeling requirements (FDA, EMA, PMDA)

2. mcp__clinpgx__clinpgx_data(method: "get_gene_drug_pairs", gene: "CYP2D6", drug: "DRUG_NAME")
   → Specific PGx gene-drug interaction evidence
```

### `mcp__biorxiv__biorxiv_info` (Preprints & Emerging Research)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_preprints` | Search bioRxiv/medRxiv preprints | `query`, `limit` |
| `get_preprint_details` | Full preprint metadata and abstract | `doi` |
| `get_recent_preprints` | Latest preprints by subject area | `subject`, `limit` |
| `search_by_author` | Find preprints by author | `author`, `limit` |

### `mcp__openalex__openalex_data` (Publication Evidence & Competitive Landscape)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_works` | Search clinical trial publications and mechanism-of-action evidence by keywords | `query` |
| `get_work` | Get work details by DOI or PMID for citation verification | `id` |
| `search_authors` | Find researchers publishing on the drug or its target | `query` |
| `get_author` | Author publication metrics and institutional affiliation | `id` |
| `search_topics` | Map research topics around the drug's mechanism or indication | `query` |
| `get_cited_by` | Find papers citing key clinical trial publications | `workId` |
| `get_works_by_author` | Researcher's publication record for KOL identification | `authorId` |
| `search_institutions` | Identify institutions leading research on the drug or target | `query` |

**Usage note:** Use OpenAlex to find clinical trial publications and mechanism-of-action evidence beyond PubMed, assess the competitive landscape by tracking research volume and citation patterns around competing drugs, and identify key opinion leaders publishing on the drug's target or indication.

### `mcp__depmap__depmap_data` (Cancer Dependency & Preclinical Validation)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_drug_sensitivity` | Preclinical drug efficacy across cancer cell lines | `drug`, `lineage`, `dataset` |
| `get_gene_dependency` | Target validation via gene essentiality | `gene`, `lineage`, `dataset` |
| `get_biomarker_analysis` | Identify predictive biomarkers for drug response | `gene`, `biomarker_gene`, `lineage` |

### `mcp__bindingdb__bindingdb_data` (Binding Affinity Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_ligands_by_target` | Known binders with affinity data for drug candidates | `target` |
| `search_by_name` | Look up binding data for a specific drug | `name` |
| `get_ki_by_target` | Ki values for target engagement evidence | `target` |

**BindingDB workflow:** Query BindingDB for binding affinity data on drug candidates and known target binders.

```
mcp__bindingdb__bindingdb_data(method: "search_by_name", name: "DRUG_NAME")
mcp__bindingdb__bindingdb_data(method: "get_ligands_by_target", target: "TARGET_NAME")
mcp__bindingdb__bindingdb_data(method: "get_ki_by_target", target: "TARGET_NAME")
```

**DepMap workflow:** Query drug sensitivity data from large-scale cancer cell line screens (PRISM, GDSC) to gather preclinical efficacy evidence, validate that the drug's target is essential in relevant lineages, and identify biomarkers that predict response or resistance.

```
mcp__depmap__depmap_data(method: "get_drug_sensitivity", drug: "semaglutide", lineage: "pancreas")
mcp__depmap__depmap_data(method: "get_gene_dependency", gene: "EGFR", lineage: "lung")
mcp__depmap__depmap_data(method: "get_biomarker_analysis", gene: "BRAF", biomarker_gene: "KRAS", lineage: "colorectal")
```

---

## Compound Disambiguation Chain

Before populating any report section, resolve the compound identity across databases. Salt forms, isomers, and naming ambiguities cause data mismatches.

```
1. mcp__pubchem__pubchem_info(method: "search_by_name", name: "DRUG_NAME")
   → Get PubChem CID (canonical identifier)
   → CRITICAL: Check if result is parent compound or salt form
   → If multiple CIDs returned, check synonyms to pick correct form

2. mcp__pubchem__pubchem_info(method: "get_compound_properties", cid: "CID")
   → Get canonical SMILES, InChI, InChIKey, molecular formula
   → Use SMILES for all subsequent structural searches

3. mcp__chembl__chembl_info(method: "compound_search", query: "DRUG_NAME")
   → Get ChEMBL ID
   → Cross-check: compare SMILES/InChI with PubChem to confirm same compound

4. mcp__drugbank__drugbank_info(method: "search_by_name", query: "DRUG_NAME")
   → Get DrugBank ID
   → If not found by name, use: get_external_identifiers with ChEMBL ID

5. mcp__fda__fda_info(method: "search_drugs", query: "DRUG_NAME")
   → Get FDA Set ID for label lookups
   → Note: FDA uses brand names; search both brand and generic

Disambiguation rules:
- Always prefer parent compound over salt (e.g., atorvastatin over atorvastatin calcium)
- If PubChem returns multiple CIDs, use get_compound_synonyms to identify the correct one
- Record ALL identifiers in Section 1 (Identity Card) before proceeding
- When ChEMBL and DrugBank names differ, note both and explain
```

---

## 9 Research Pathways

Execute pathways in **priority tier order** (see Tiered Pathway Execution above), NOT sequentially 1-9. Each pathway populates one or more of the 11 mandatory report sections. **Save each section to the report file as soon as it completes.**

### Pathway 1: Chemical Properties → Section 2 (Chemistry)

```
1. mcp__pubchem__pubchem_info(method: "get_compound_properties", cid: "CID")
   → MW, XLogP, TPSA, HBD, HBA, rotatable bonds, complexity

2. mcp__pubchem__pubchem_info(method: "get_compound_classification", cid: "CID")
   → Drug class, pharmacological category

3. mcp__chembl__chembl_info(method: "get_admet", chembl_id: "CHEMBLxxxxx")
   → Lipinski rule of 5, lead-likeness, Veber rules

4. mcp__pubchem__pubchem_info(method: "get_compound_safety", cid: "CID")
   → GHS classification, acute toxicity estimates
```

### Pathway 2: Mechanism & Targets → Sections 3–4 (Mechanism, Targets)

```
1. mcp__chembl__chembl_info(method: "get_mechanism", chembl_id: "CHEMBLxxxxx")
   → Primary mechanism of action, target, action type

2. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   → Pharmacodynamics, mechanism narrative, all targets (primary, enzyme, transporter, carrier)

3. mcp__opentargets__opentargets_info(method: "search_targets", query: "PRIMARY_TARGET")
   → Ensembl ID, target family, tractability

4. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Target function, pathways, subcellular location

5. mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "CHEMBLxxxxx", limit: 30)
   → IC50/Ki/EC50 values against primary and off-targets

6. mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   → Pathway involvement (signaling, metabolic)

7. mcp__kegg__kegg_data(method: "search_drugs", query: "DRUG_NAME")
   → KEGG drug entry with ATC codes, targets, and pathway links
   mcp__kegg__kegg_data(method: "get_disease_info", disease_id: "H00001")
   → KEGG disease entry linking drugs, genes, and pathways for the indication

7. mcp__reactome__reactome_data(method: "find_pathways_by_gene", gene_id: "PRIMARY_TARGET", species: "Homo sapiens")
   → Direct Reactome pathway lookup for the drug's primary target

8. mcp__reactome__reactome_data(method: "find_pathways_by_disease", disease_name: "DISEASE_NAME")
   → Disease-associated Reactome pathways to contextualize drug mechanism
```

### Pathway 3: ADMET → Section 5 (ADMET)

```
1. mcp__chembl__chembl_info(method: "get_admet", chembl_id: "CHEMBLxxxxx")
   → Predicted ADMET properties, drug-likeness scores

2. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   → Absorption (bioavailability, Tmax, food effect), Distribution (Vd, protein binding),
     Metabolism (CYP enzymes, metabolites), Elimination (half-life, clearance, route)

3. mcp__fda__fda_info(method: "get_drug_label", drug_name: "DRUG_NAME")
   → Clinical pharmacology section (PK parameters from label)

4. mcp__drugbank__drugbank_info(method: "search_by_transporter", transporter: "P-glycoprotein")
   → Check if drug is P-gp substrate/inhibitor (affects absorption, brain penetration)
```

### Pathway 4: Clinical Trials → Section 6 (Clinical Trials)

```
1. mcp__ctgov__ctgov_info(method: "search_studies", query: "DRUG_NAME", limit: 50)
   → All trials: count by phase, status, indication

2. mcp__ctgov__ctgov_info(method: "search_studies", query: "DRUG_NAME", phase: "3", status: "COMPLETED")
   → Pivotal trials with results

3. mcp__ctgov__ctgov_info(method: "get_study_results", nct_id: "NCTxxxxxxxx")
   → Primary endpoint results from key trials

4. mcp__ctgov__ctgov_info(method: "get_study_details", nct_id: "NCTxxxxxxxx")
   → Design, enrollment, comparator, duration for pivotal trials

5. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "DRUG_NAME phase 3 randomized", num_results: 10)
   → Published trial results and meta-analyses
```

### Pathway 5: Post-Marketing Safety → Section 7 (Safety)

```
1. mcp__fda__fda_info(method: "get_adverse_events", drug_name: "DRUG_NAME", limit: 100)
   → FAERS reports: most common AEs, serious events, outcomes

2. mcp__fda__fda_info(method: "get_drug_label", drug_name: "DRUG_NAME")
   → Boxed warnings, contraindications, warnings & precautions

3. mcp__fda__fda_info(method: "get_recalls", drug_name: "DRUG_NAME")
   → Recall history (safety or quality)

4. mcp__drugbank__drugbank_info(method: "get_drug_interactions", drugbank_id: "DBxxxxx")
   → Major drug-drug interactions

5. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "DRUG_NAME safety adverse events post-marketing", num_results: 10)
   → Published safety reviews and pharmacovigilance studies
```

### Pathway 6: Pharmacogenomics → Section 8 (Pharmacogenomics)

```
1. mcp__fda__fda_info(method: "get_drug_label", drug_name: "DRUG_NAME")
   → Pharmacogenomic biomarker information in label

2. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   → SNP effects, enzyme polymorphisms affecting metabolism

3. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "DRUG_NAME pharmacogenomics CYP polymorphism", num_results: 10)
   → PGx studies and CPIC/DPWG guideline publications

4. mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   → Metabolic pathway (which CYPs, UGTs involved)
```

### Pathway 7: Regulatory & Patents → Section 9 (Regulatory)

```
1. mcp__fda__fda_info(method: "get_approvals", drug_name: "DRUG_NAME")
   → Approval dates, supplemental approvals, indication expansions

2. mcp__fda__fda_info(method: "search_drugs", query: "DRUG_NAME")
   → NDA/ANDA/BLA numbers, applicant, dosage forms

3. mcp__pubchem__pubchem_info(method: "get_compound_patents", cid: "CID", limit: 20)
   → Patent landscape (composition of matter, formulation, use patents)

4. mcp__fda__fda_info(method: "search_by_active_ingredient", ingredient: "DRUG_NAME")
   → All marketed formulations (brand, generic, strengths)
```

### Pathway 8: Real-World Evidence → Section 10 (Literature)

```
1. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "DRUG_NAME", start_date: "2020-01-01", num_results: 20)
   → Recent publications (last 5 years)

2. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "DRUG_NAME systematic review meta-analysis", num_results: 10)
   → High-level evidence synthesis

3. mcp__biorxiv__biorxiv_info(method: "search_preprints", query: "DRUG_NAME", limit: 10)
   → Emerging research not yet peer-reviewed

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "DRUG_NAME real-world evidence observational", num_results: 10)
   → Post-marketing effectiveness studies
```

### Pathway 9: Comparative Analysis → Section 11 (Executive Summary)

```
1. mcp__drugbank__drugbank_info(method: "get_similar_drugs", drugbank_id: "DBxxxxx", limit: 10)
   → Pharmacologically similar drugs for comparison

2. mcp__drugbank__drugbank_info(method: "search_by_category", category: "THERAPEUTIC_CLASS")
   → All drugs in the same therapeutic class

3. mcp__chembl__chembl_info(method: "drug_search", query: "INDICATION", limit: 20)
   → Drugs for same indication (competitive landscape)

4. mcp__ctgov__ctgov_info(method: "search_studies", query: "DRUG_NAME vs", limit: 20)
   → Head-to-head comparison trials
```

---

## 11 Mandatory Report Sections

Every drug research report MUST include all 11 sections. Use the template below and populate progressively as each research pathway completes.

### Report Template

```
# Drug Research Report: [DRUG NAME]
Generated: [DATE]

## 1. Identity Card
- Generic name / INN
- Brand name(s)
- Chemical name (IUPAC)
- PubChem CID / SMILES / InChI / InChIKey
- ChEMBL ID / DrugBank ID / FDA Set ID
- CAS number
- Molecular formula
- Drug class / Pharmacological category
- Development code(s)

## 2. Chemistry & Physicochemical Properties
- Molecular weight
- LogP / XLogP
- TPSA (topological polar surface area)
- Hydrogen bond donors / acceptors
- Rotatable bonds
- Lipinski Rule of 5 compliance
- Solubility profile
- Structural alerts (if any)
- Salt form(s) in marketed products

## 3. Mechanism of Action
- Primary mechanism
- Action type (inhibitor, agonist, antagonist, modulator, etc.)
- Binding site / interaction type
- Pharmacodynamic effects
- Onset and duration of action
- Dose-response relationship (if available)

## 4. Targets & Pathways
- Primary target(s) with Ensembl/UniProt IDs
- Secondary/off-targets
- Bioactivity data (IC50, Ki, EC50)
- Selectivity profile
- Pathway involvement
- Target family and tractability

## 5. ADMET Profile
- Absorption: bioavailability, Tmax, Cmax, food effect
- Distribution: Vd, protein binding, tissue distribution
- Metabolism: CYP enzymes, phase II, active metabolites
- Elimination: half-life, clearance, route of excretion
- Drug-likeness scores
- Transporters (P-gp, BCRP, OATPs)

## 6. Clinical Trials
- Trial landscape (count by phase and status)
- Pivotal trials (design, N, endpoints, results)
- Key efficacy findings
- Ongoing trials of interest
- Indication expansion trials

## 7. Safety Profile
- Most common adverse events (incidence)
- Serious adverse events
- Boxed warnings / contraindications
- Drug-drug interactions (major)
- Recall history
- Post-marketing safety signals
- Risk management (REMS if applicable)

## 8. Pharmacogenomics
- FDA label PGx biomarkers
- CPIC/DPWG guideline status
- CYP polymorphism impact on PK
- Known poor/ultra-rapid metabolizer effects
- Actionable variants

## 9. Regulatory Status
- FDA approval date and NDA/BLA number
- Approved indications (with dates)
- EMA / other regulatory status
- Patent landscape (composition, use, formulation)
- Generic/biosimilar availability
- Marketed formulations and strengths

## 10. Literature Summary
- Key systematic reviews / meta-analyses
- Recent publications (last 3-5 years)
- Emerging preprint research
- Real-world evidence studies
- Knowledge gaps identified

## 11. Executive Summary
- One-paragraph drug profile
- Therapeutic positioning vs competitors
- Key differentiators (efficacy, safety, convenience)
- Unmet needs and opportunities
- Overall evidence grade (see T1-T4 below)
```

---

## T1-T4 Evidence Grading

Assign an evidence tier to each report section based on data quality and source.

| Tier | Label | Criteria | Typical Sources |
|------|-------|----------|-----------------|
| **T1** | Gold standard | Regulatory-approved data, pivotal trial results | FDA label, Phase 3 results, FAERS |
| **T2** | Strong evidence | Peer-reviewed published data, validated databases | PubMed RCTs, DrugBank, ChEMBL measured data |
| **T3** | Moderate evidence | Computational predictions, smaller studies, preprints | ADMET predictions, Phase 1/2, bioRxiv |
| **T4** | Hypothesis-level | Text mining, pathway inference, limited data | PubMed case reports, PubChem assays, Open Targets text mining |

### Fallback Chains

When a primary tool returns no data, follow the fallback chain before marking a section as "insufficient data."

```
Chemical properties:
  PubChem → ChEMBL ADMET → DrugBank details → PubMed literature

Mechanism of action:
  ChEMBL get_mechanism → DrugBank get_drug_details → FDA label → PubMed

Bioactivity data:
  ChEMBL get_bioactivity → PubChem get_compound_assays → PubMed

Clinical trials:
  ClinicalTrials.gov → PubMed (published results) → FDA approvals

Safety data:
  FDA adverse_events → FDA label (warnings) → DrugBank interactions → PubMed

Pharmacogenomics:
  FDA label (PGx section) → DrugBank (SNP effects) → PubMed (CPIC guidelines)

Regulatory:
  FDA approvals → FDA search_drugs → PubChem patents → PubMed

Targets:
  DrugBank targets → ChEMBL mechanism → Open Targets → PubMed
```

---

## Report-First Approach

Always create the report template FIRST, then populate progressively:

```
Step 1: Create the 11-section template with drug name and date
Step 2: Run Compound Disambiguation Chain → populate Section 1
Step 3: Execute Pathways in PRIORITY ORDER (see Tiered Execution below)
Step 4: WRITE EACH SECTION TO THE REPORT FILE AS SOON AS IT COMPLETES
        Do NOT wait until all pathways finish — save progress incrementally
Step 5: Assign T1-T4 evidence grade to each section as it is written
Step 6: Write Executive Summary last, synthesizing whatever sections are complete
```

## Tiered Pathway Execution (Timeout Resilience)

MCP tool calls take time. To ensure useful output even if execution is interrupted,
execute pathways in priority tiers. **Complete each tier and save before starting the next.**

### Tier 1 — MUST COMPLETE (target: first 10 minutes)
These produce the core report. If nothing else runs, these alone are useful.
```
1. Compound Disambiguation Chain → Section 1 (Identity Card)
2. Pathway 2: Mechanism & Targets → Sections 3-4
3. Pathway 4: Clinical Trials → Section 6
>>> CHECKPOINT: Write Sections 1, 3, 4, 6 to report file NOW <<<
```

### Tier 2 — HIGH VALUE (next 10 minutes)
Adds safety and regulatory context.
```
4. Pathway 5: Post-Marketing Safety → Section 7
5. Pathway 7: Regulatory & Patents → Section 9
6. Pathway 1: Chemical Properties → Section 2
>>> CHECKPOINT: Write Sections 2, 7, 9 to report file NOW <<<
```

### Tier 3 — COMPLETE PICTURE (remaining time)
Fills remaining sections. Skip if running low on time.
```
7. Pathway 3: ADMET → Section 5
8. Pathway 6: Pharmacogenomics → Section 8
9. Pathway 8: Real-World Evidence → Section 10
10. Pathway 9: Comparative Analysis → Section 11 (Executive Summary)
>>> FINAL CHECKPOINT: Write all remaining sections <<<
```

### Parallel Execution Within Tiers
Where pathways are independent, run MCP calls in parallel:
- Tier 1: Disambiguation is sequential, but Pathway 2 and 4 are independent — run simultaneously
- Tier 2: Pathways 5, 7, and 1 are all independent — run simultaneously
- Tier 3: All independent — run simultaneously

### Timeout Behavior
If the agent detects it is running low on time or context:
1. Stop starting new pathways
2. Write the Executive Summary (Section 11) from whatever data has been gathered
3. Mark incomplete sections as `[Not completed — prioritized sections above]`
4. A partial report with Sections 1, 3-4, 6 is MORE VALUABLE than no report

---

## Differentiated Depth

Adjust research depth based on drug development stage:

### Approved Drugs (Full Depth)
```
All 9 pathways, all 11 sections populated.
Expected evidence: T1-T2 for most sections.
Focus: Complete monograph with safety/efficacy balance.
```

### Investigational Drugs (Mechanism & Trial Focus)
```
ALWAYS run the Compound Disambiguation Chain first — even for investigational compounds.
Many Phase 2+ compounds have PubChem CIDs, ChEMBL IDs, and sometimes DrugBank entries.
Search by development code (e.g., "LY3437943") if the INN returns no results.
Only mark an ID as unavailable AFTER attempting all 5 disambiguation steps.

Prioritize: Pathway 2 (mechanism), Pathway 4 (trials), Pathway 1 (chemistry).
Sections 6-9 may be sparse — mark as T3/T4.
Focus: Mechanism novelty, trial design, competitive positioning.
Fallback: Use bioRxiv and PubChem assays heavily.
```

### Safety Reviews (AE & PGx Focus)
```
Prioritize: Pathway 5 (safety), Pathway 6 (PGx), Pathway 3 (ADMET).
Focus: Adverse event characterization, risk factors, dose adjustments.
Extended FAERS query with demographic breakdowns.
Cross-reference DDIs with metabolic pathway.
```

---

## Multi-Agent Workflow Examples

**"Generate a comprehensive report on semaglutide"**
1. Drug Research → Full 11-section report with all 9 pathways, compound disambiguation, evidence grading
2. Clinical Trial Analyst → Deep-dive on STEP/SUSTAIN/PIONEER trials, subgroup analyses
3. Pharmacovigilance Specialist → Detailed FAERS signal detection, thyroid safety signal investigation

**"Compare SGLT2 inhibitors for cardio-renal outcomes"**
1. Drug Research → Individual reports for empagliflozin, dapagliflozin, canagliflozin
2. Drug Target Analyst → SGLT2 vs SGLT1 selectivity, target-mediated effects comparison
3. Clinical Trial Analyst → EMPA-REG, DAPA-HF, CREDENCE head-to-head analysis
4. Pharmacogenomics Specialist → Genetic predictors of response across the class

**"Investigate safety profile of a new kinase inhibitor"**
1. Drug Research → Sections 1-5 (identity, chemistry, mechanism, targets, ADMET) as foundation
2. Pharmacovigilance Specialist → Class-effect safety signals from other kinase inhibitors
3. Drug Interaction Analyst → CYP3A4 interaction potential, QT prolongation risk
4. Drug Target Analyst → Off-target kinase activity → predicted toxicity profile

**"Evaluate repurposing potential of metformin for cancer"**
1. Drug Research → Full metformin monograph (approved drug, full depth)
2. Drug Target Analyst → AMPK pathway, mTOR inhibition, cancer-relevant targets
3. Clinical Trial Analyst → Metformin cancer trials (search by intervention)
4. FDA Consultant → Regulatory pathway for repurposing (505(b)(2) considerations)

**"Research an investigational compound in Phase 2"**
1. Drug Research → Investigational depth: mechanism, early trials, chemistry focus
2. Drug Target Analyst → Target validation strength, competitive compounds on same target
3. Clinical Trial Analyst → Trial design analysis, comparator selection, endpoint adequacy

---

## Completeness Checklist

**Tier 1 (minimum viable report):**
- [ ] Compound disambiguation chain completed with database IDs resolved
- [ ] Mechanism of action confirmed (Section 3)
- [ ] Targets and pathways documented (Section 4)
- [ ] Clinical trial landscape summarized (Section 6)
- [ ] Report file saved with Tier 1 sections

**Tier 2 (standard report):**
- [ ] Safety profile and FAERS data reviewed (Section 7)
- [ ] Regulatory status documented (Section 9)
- [ ] Chemical properties retrieved (Section 2)
- [ ] T1-T4 evidence grade assigned to each completed section

**Tier 3 (complete report):**
- [ ] ADMET profile populated (Section 5)
- [ ] Pharmacogenomic considerations documented (Section 8)
- [ ] Literature summary with recent publications (Section 10)
- [ ] Executive summary synthesizes all findings (Section 11)
- [ ] Fallback chains followed for any section with missing primary data
