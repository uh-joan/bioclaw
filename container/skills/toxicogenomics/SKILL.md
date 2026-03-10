---
name: toxicogenomics
description: "Mechanism-of-toxicity analysis, organ toxicity prediction, Tox21/ToxCast integration, IVIVE modeling, adverse outcome pathways, safety biomarkers"
---

# Toxicogenomics Specialist

Integrative toxicogenomics and safety assessment combining transcriptomic signatures, adverse outcome pathway (AOP) frameworks, in vitro to in vivo extrapolation (IVIVE), and multi-source toxicity data. This skill specializes in mechanism-of-toxicity (MoT) elucidation, organ-specific toxicity prediction, safety biomarker evaluation, and toxicity risk scoring. It bridges molecular-level perturbations (gene expression changes, pathway dysregulation) with organism-level adverse outcomes using structured AOP logic. Distinct from the chemical-safety-toxicology skill, which focuses on structural alerts and drug-likeness rules, this skill emphasizes genomic and pathway-level toxicity mechanisms, dose-response modeling, and translational safety assessment.

## Report-First Workflow

1. **Create report file immediately**: `compound_toxicogenomics_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## Cross-Reference: Other Skills

- **Adverse event signal detection and FAERS analysis** -> use adverse-event-detection skill
- **Drug monographs, pharmacology, clinical profiles** -> use drug-research skill
- **Clinical pharmacology and PK/PD modeling** -> use clinical-pharmacology skill
- **Differential expression analysis from RNA-seq** -> use rnaseq-deseq2 skill
- **Biomarker identification and validation** -> use biomarker-discovery skill
- **Structural alerts, PAINS, drug-likeness rules** -> use chemical-safety-toxicology skill
- **Pharmacovigilance and regulatory safety reporting** -> use pharmacovigilance-specialist skill
- **Drug-drug interaction safety** -> use drug-interaction-analyst skill

## Available MCP Tools

### `mcp__drugbank__drugbank_data` (Known Toxicity Profiles)

| Method | Toxicogenomics use | Key parameters |
|--------|-------------------|----------------|
| `search_drugs` | Find drug by name, retrieve DrugBank ID | `query` |
| `get_drug` | Full drug profile including toxicity section, LD50, contraindications | `drugbank_id` |
| `get_toxicity` | Dedicated toxicity data: carcinogenicity, mutagenicity, reproductive tox | `drugbank_id` |
| `get_pharmacology` | Mechanism of action, pharmacodynamics, metabolism (CYP involvement) | `drugbank_id` |

### `mcp__fda__fda_data` (Post-Market Safety & Labeling)

| Method | Toxicogenomics use | Key parameters |
|--------|-------------------|----------------|
| `search_adverse_events` | FAERS reports for clinical toxicity signals | `drug_name`, `limit` |
| `get_drug_label` | Boxed warnings, REMS, nonclinical toxicology sections | `drug_name` or `set_id` |

### `mcp__pubmed__pubmed_data` (Toxicology Literature)

| Method | Toxicogenomics use | Key parameters |
|--------|-------------------|----------------|
| `search` | Toxicogenomics studies, MoT publications, AOP literature | `keywords`, `num_results` |
| `fetch_details` | Full abstract with mechanistic toxicity findings | `pmid` |

### `mcp__chembl__chembl_data` (In Vitro Tox Assays & Safety Panels)

| Method | Toxicogenomics use | Key parameters |
|--------|-------------------|----------------|
| `search_molecule` | Find ChEMBL ID for compound | `query` |
| `get_activities` | hERG, CYP inhibition, BSEP, safety pharmacology panel data | `chembl_id`, `target_id` |
| `get_assays` | Tox assay descriptions, endpoints, protocols | `chembl_id` |

### `mcp__pubchem__pubchem_data` (Tox21 Data & Bioassays)

| Method | Toxicogenomics use | Key parameters |
|--------|-------------------|----------------|
| `search_compounds` | Compound lookup by name, CID, SMILES | `query` |
| `get_compound` | Full compound record, properties, cross-references | `cid` |
| `get_bioassays` | Tox21/ToxCast bioassay results (NR signaling, stress response, mitotox) | `cid` |

### `mcp__kegg__kegg_data` (Toxicity-Relevant Pathways)

| Method | Toxicogenomics use | Key parameters |
|--------|-------------------|----------------|
| `get_pathway` | Retrieve specific toxicity pathway (oxidative stress, apoptosis, DNA damage) | `pathway_id` |
| `find_pathway` | Search pathways by keyword (e.g., "glutathione", "NRF2", "p53") | `query` |

Key toxicity-relevant KEGG pathways:

| Pathway ID | Pathway Name | Toxicity Relevance |
|------------|-------------|-------------------|
| hsa04210 | Apoptosis | Cell death, organ damage |
| hsa04115 | p53 signaling pathway | DNA damage response, genotoxicity |
| hsa04066 | HIF-1 signaling pathway | Hypoxia, ischemic injury |
| hsa00480 | Glutathione metabolism | Oxidative stress defense, reactive metabolite conjugation |
| hsa04151 | PI3K-Akt signaling pathway | Cell survival/death balance |
| hsa04010 | MAPK signaling pathway | Stress response, inflammation |
| hsa00982 | Drug metabolism - cytochrome P450 | Bioactivation, reactive metabolites |
| hsa00983 | Drug metabolism - other enzymes | Phase II conjugation, detoxification |
| hsa04217 | Necroptosis | Programmed necrosis, tissue injury |
| hsa04064 | NF-kappa B signaling pathway | Inflammatory response |

### `mcp__geneontology__go_data` (Toxicity-Related GO Terms)

| Method | Toxicogenomics use | Key parameters |
|--------|-------------------|----------------|
| `search_go_terms` | Find GO terms for toxicity processes (oxidative stress, apoptosis, xenobiotic metabolism) | `query` |

Key toxicity-related GO terms:

| GO Term | Description | Toxicity Application |
|---------|-------------|---------------------|
| GO:0006979 | Response to oxidative stress | Oxidative damage markers |
| GO:0006915 | Apoptotic process | Cell death assessment |
| GO:0071356 | Cellular response to tumor necrosis factor | Immune-mediated toxicity |
| GO:0006805 | Xenobiotic metabolic process | Drug metabolism, bioactivation |
| GO:0097193 | Intrinsic apoptotic signaling pathway | Mitochondrial toxicity |
| GO:0006974 | Cellular response to DNA damage stimulus | Genotoxicity |
| GO:0042493 | Response to drug | General drug response |
| GO:0034599 | Cellular response to oxidative stress | ROS-mediated injury |

### `mcp__opentargets__ot_data` (Off-Target Safety)

| Method | Toxicogenomics use | Key parameters |
|--------|-------------------|----------------|
| `search_target` | Find target by gene name | `query` |
| `get_target_info` | Target safety data, known on-target toxicities, tissue expression | `target_id` |

### `mcp__reactome__reactome_data` (Detoxification & Stress Response Pathways)

| Method | Toxicogenomics use | Key parameters |
|--------|-------------------|----------------|
| `search_pathways` | Find detoxification, stress response, xenobiotic pathways | `query` |
| `get_pathway` | Full pathway detail including component genes for signature building | `pathway_id` |

Key Reactome pathways for toxicogenomics:

| Pathway | Toxicity Relevance |
|---------|-------------------|
| R-HSA-211859 | Biological oxidations (Phase I/II metabolism) |
| R-HSA-156580 | Phase II conjugation of compounds |
| R-HSA-5668914 | NRF2 pathway (oxidative stress master regulator) |
| R-HSA-69620 | Cell cycle checkpoints (genotoxic stress) |
| R-HSA-109581 | Apoptosis |
| R-HSA-2262752 | Cellular responses to stress |
| R-HSA-9711097 | Cellular senescence |
| R-HSA-1280218 | Adaptive immune system (immune-mediated toxicity) |

### `mcp__hpo__hpo_data` (Human Phenotype Correlates of Toxicity)

| Method | Toxicogenomics use | Key parameters |
|--------|-------------------|----------------|
| `search_hpo_terms` | Map toxicity endpoints to human phenotype terms | `query` |

Key HPO terms for organ toxicity:

| HPO Term | Description | Organ System |
|----------|-------------|-------------|
| HP:0001399 | Hepatic failure | Liver |
| HP:0002910 | Elevated hepatic transaminases | Liver (DILI biomarker) |
| HP:0001677 | Coronary artery atherosclerosis | Cardiovascular |
| HP:0001657 | QT prolongation | Cardiovascular (hERG) |
| HP:0000083 | Renal insufficiency | Kidney |
| HP:0003259 | Elevated serum creatinine | Kidney (nephrotox biomarker) |
| HP:0001873 | Thrombocytopenia | Hematological |
| HP:0001903 | Anemia | Hematological |
| HP:0002014 | Diarrhea | Gastrointestinal |
| HP:0002719 | Recurrent infections | Immune suppression |

### `mcp__hmdb__hmdb_data` (Metabolite-Gene Expression Links & Dose-Response Signatures)

Use HMDB to identify metabolites whose perturbations link to toxicogenomic gene expression signatures, investigate dose-response metabolite patterns, and map metabolites to adverse outcome pathways. Note: HMDB uses Cloudflare protection so some requests may be blocked intermittently.

| Method | Toxicogenomics use | Key parameters |
|--------|-------------------|----------------|
| `search_metabolites` | Search for metabolites associated with toxicity gene signatures | `query` (required), `limit` (optional, default 25) |
| `get_metabolite` | Full metabolite profile including pathways and disease associations | `hmdb_id` (required) |
| `get_metabolite_pathways` | Map metabolites to detoxification/bioactivation pathways for AOP integration | `hmdb_id` (required) |
| `get_metabolite_diseases` | Disease associations — link metabolite perturbations to organ toxicity phenotypes | `hmdb_id` (required) |
| `get_metabolite_concentrations` | Normal and abnormal concentrations — establish dose-response metabolite baselines | `hmdb_id` (required) |
| `search_by_mass` | Identify toxicity-associated metabolites from untargeted metabolomics | `mass` (required), `tolerance` (optional, default 0.05), `limit` (optional, default 25) |

---

## Python Environment

The container has `scipy`, `numpy`, `pandas`, `seaborn`, `matplotlib`, and `statsmodels` available. Run Python code via the Bash tool.

---

## Core Workflows

### Workflow 1: Mechanism-of-Toxicity (MoT) Tree Analysis

Systematic elucidation of the molecular mechanism driving an observed toxic effect.

**MoT Decision Tree:**

```
Observed Toxicity
├── Reactive Metabolite Formation
│   ├── Electrophilic intermediates (quinones, epoxides, nitroso)
│   ├── GSH depletion / GSH adduct detection
│   ├── Covalent protein binding → hapten formation → immune response
│   └── Assess: CYP involvement, daily dose, structural alerts
│
├── Mitochondrial Toxicity
│   ├── ETC complex inhibition (I, III, IV)
│   ├── Uncoupling of oxidative phosphorylation
│   ├── mtDNA damage / replication inhibition
│   ├── Fatty acid oxidation inhibition → microvesicular steatosis
│   └── Assess: JC-1 assay, Seahorse OCR, ATP depletion
│
├── Phospholipidosis
│   ├── Cationic amphiphilic drug (CAD) accumulation in lysosomes
│   ├── Phospholipid-drug complex formation
│   ├── Lamellar body formation
│   └── Assess: CAD score, in vitro phospholipidosis assay
│
├── Oxidative Stress
│   ├── ROS generation (superoxide, H2O2, hydroxyl radical)
│   ├── NRF2/KEAP1 pathway activation
│   ├── Lipid peroxidation → 4-HNE, MDA
│   ├── DNA oxidation → 8-OHdG
│   └── Assess: DCFDA assay, GSH/GSSG ratio, NRF2 target genes
│
└── Immune-Mediated Toxicity
    ├── Hapten hypothesis (reactive metabolite + protein)
    ├── Pharmacological interaction (p-i) hypothesis
    ├── Danger hypothesis (cellular stress → DAMP release)
    ├── HLA-restricted (abacavir-HLA-B*57:01 paradigm)
    └── Assess: HLA genotyping, lymphocyte transformation test
```

**MCP call sequence for MoT investigation:**

```
Step 1: Identify compound and known toxicity
  mcp__drugbank__drugbank_data(method: "search_drugs", query: "compound_name")
  mcp__drugbank__drugbank_data(method: "get_toxicity", drugbank_id: "DBxxxxx")

Step 2: Retrieve metabolic pathway and CYP involvement
  mcp__drugbank__drugbank_data(method: "get_pharmacology", drugbank_id: "DBxxxxx")
  mcp__kegg__kegg_data(method: "get_pathway", pathway_id: "hsa00982")

Step 3: Check Tox21 bioassay results for mechanistic endpoints
  mcp__pubchem__pubchem_data(method: "get_bioassays", cid: CID_NUMBER)
  → Filter for: mitochondrial membrane potential, NR signaling, stress response

Step 4: Identify toxicity-relevant pathways
  mcp__reactome__reactome_data(method: "search_pathways", query: "oxidative stress")
  mcp__kegg__kegg_data(method: "find_pathway", query: "glutathione metabolism")

Step 5: Literature evidence for mechanism
  mcp__pubmed__pubmed_data(method: "search", keywords: "compound_name mechanism toxicity")
```

---

### Workflow 2: Organ-Specific Toxicity Prediction

#### Hepatotoxicity (DILI) Assessment

**DILIrank Classification:**

| Category | Definition | Examples |
|----------|-----------|----------|
| **Most-DILI-concern** | Drugs with strong evidence of causing clinically significant DILI | Isoniazid, diclofenac, amiodarone, valproic acid |
| **Less-DILI-concern** | Drugs with some DILI reports but lower frequency/severity | Atorvastatin, omeprazole |
| **No-DILI-concern** | Drugs with no substantial evidence of DILI | Insulin, heparin |
| **Ambiguous** | Insufficient or conflicting evidence | Many newer agents |

**DILI Mechanistic Categories:**

| Mechanism | Key Features | Biomarkers | Latency |
|-----------|-------------|------------|---------|
| **Direct hepatotoxicity** | Dose-dependent, predictable | ALT, AST, ALP | Hours-days |
| **Idiosyncratic (metabolic)** | Aberrant metabolism, dose-related component | ALT, bilirubin | 1-8 weeks |
| **Idiosyncratic (immune)** | Hypersensitivity features, HLA-associated | Eosinophilia, rash, ALT | 1-12 weeks |
| **Mitochondrial** | Steatosis, lactic acidosis | Lactate, microvesicular fat | Weeks-months |
| **Cholestatic** | Bile transport inhibition (BSEP, MRP2) | ALP, GGT, bilirubin | Weeks |

**DILI risk factor assessment:**

```
Step 1: Drug properties
  mcp__pubchem__pubchem_data(method: "get_compound", cid: CID_NUMBER)
  → Daily dose >100 mg? LogP >3? Molecular weight >600?

Step 2: BSEP inhibition and bile acid transport
  mcp__chembl__chembl_data(method: "get_activities", chembl_id: "CHEMBLxxxx", target_id: "CHEMBL6060")
  → BSEP IC50 <25 μM = HIGH RISK

Step 3: Reactive metabolite potential
  mcp__kegg__kegg_data(method: "get_pathway", pathway_id: "hsa00982")
  → CYP3A4/2C9-mediated bioactivation risk

Step 4: Clinical DILI signals
  mcp__fda__fda_data(method: "get_drug_label", drug_name: "compound_name")
  → Check for boxed warnings, REMS, Hy's Law cases

Step 5: Literature DILI evidence
  mcp__pubmed__pubmed_data(method: "search", keywords: "compound_name DILI hepatotoxicity liver injury")
```

**Hy's Law Criteria (prognostic for fatal DILI):**
- ALT or AST > 3x ULN AND
- Total bilirubin > 2x ULN AND
- No other explanation (biliary obstruction, other hepatotoxins)
- Case fatality rate: 10-50% if drug not promptly discontinued

#### Cardiotoxicity Assessment

**hERG IC50 Thresholds:**

```
hERG IC50 interpretation:
  < 1 μM:    HIGH RISK — likely clinically significant QTc prolongation
  1-10 μM:   MODERATE RISK — thorough QT (TQT) study required
  10-30 μM:  LOW RISK — monitor in clinical development
  > 30 μM:   MINIMAL RISK — unlikely QTc concern

Cardiac safety margin = hERG IC50 / free Cmax
  < 30x:   HIGH RISK — likely QTc prolongation at therapeutic doses
  30-100x: MODERATE RISK — may show QTc effect in sensitive populations
  > 100x:  LOW RISK — adequate safety margin
```

**Comprehensive cardiac safety panel:**

| Target | Assay | Concern |
|--------|-------|---------|
| hERG (Kv11.1) | Patch clamp, binding | QTc prolongation, TdP |
| Nav1.5 | Patch clamp | QRS widening, Brugada |
| Cav1.2 | Patch clamp | QTc shortening, hemodynamics |
| IKs (KCNQ1/KCNE1) | Patch clamp | QTc prolongation (additive with hERG) |
| Myocyte contractility | hiPSC-CM | Structural cardiotoxicity |

```
Step 1: hERG data retrieval
  mcp__chembl__chembl_data(method: "get_activities", chembl_id: "CHEMBLxxxx", target_id: "CHEMBL240")
  → hERG IC50 values from patch clamp assays

Step 2: Cardiac ion channel panel
  mcp__chembl__chembl_data(method: "get_assays", chembl_id: "CHEMBLxxxx")
  → Filter for Nav1.5, Cav1.2, IKs assay results

Step 3: Clinical QTc signals
  mcp__fda__fda_data(method: "search_adverse_events", drug_name: "compound_name")
  → Filter for: QT prolonged, Torsade de Pointes, cardiac arrest, sudden death
```

#### Nephrotoxicity Assessment

**Key nephrotoxicity mechanisms:**

| Mechanism | Compounds | Biomarkers |
|-----------|----------|------------|
| Acute tubular necrosis | Cisplatin, aminoglycosides | KIM-1, NGAL, clusterin |
| Crystal nephropathy | Acyclovir, methotrexate | Urine crystals, creatinine |
| Glomerular injury | NSAIDs, gold compounds | Proteinuria, albumin/creatinine |
| Interstitial nephritis | PPIs, antibiotics | Eosinophiluria, WBC casts |
| Osmotic nephrosis | Mannitol, IVIG | Low-molecular-weight proteinuria |

#### Neurotoxicity Assessment

**Neurotoxicity endpoints:**

| Endpoint | Mechanism | Assessment |
|----------|-----------|------------|
| Seizure liability | GABA antagonism, glutamate agonism | In vitro: MEA assay; off-target: GABA-A binding |
| Peripheral neuropathy | Tubulin binding, mitochondrial damage | Nerve conduction, DRG neuron viability |
| CNS depression | Off-target GABA-A, histamine H1 | Binding assays, behavioral assessment |
| Serotonin syndrome | 5-HT reuptake, MAO inhibition | Serotonin receptor panel |

#### Hematotoxicity Assessment

**Key hematotoxicity concerns:**

| Type | Mechanism | Monitoring |
|------|-----------|------------|
| Neutropenia/agranulocytosis | Myelosuppression, immune-mediated | ANC, bone marrow biopsy |
| Thrombocytopenia | Megakaryocyte suppression, anti-platelet Abs | Platelet count, anti-platelet antibodies |
| Hemolytic anemia | Oxidative hemolysis (G6PD), immune-mediated | Haptoglobin, LDH, Coombs test |
| Aplastic anemia | Stem cell toxicity | Pancytopenia, reticulocyte count |

---

### Workflow 3: Adverse Outcome Pathway (AOP) Analysis

**AOP Framework:**

```
Molecular Initiating Event (MIE)
  → Key Event 1 (cellular level)
    → Key Event 2 (tissue level)
      → Key Event 3 (organ level)
        → Adverse Outcome (organism/population level)
```

**Example AOP: Mitochondrial Complex I Inhibition → Parkinsonian Motor Deficits**

```
MIE: Inhibition of mitochondrial complex I
 ↓ (KER: dose-dependent)
KE1: Decreased ATP production, increased ROS
 ↓ (KER: threshold-dependent)
KE2: Dopaminergic neuron degeneration (substantia nigra)
 ↓ (KER: progressive)
KE3: Striatal dopamine depletion
 ↓ (KER: >80% depletion threshold)
AO: Parkinsonian motor deficits
```

**Example AOP: BSEP Inhibition → Cholestatic Liver Injury**

```
MIE: Inhibition of bile salt export pump (BSEP/ABCB11)
 ↓ (KER: IC50-dependent)
KE1: Intracellular bile acid accumulation
 ↓ (KER: concentration-dependent)
KE2: Mitochondrial permeability transition, oxidative stress
 ↓ (KER: threshold-dependent)
KE3: Hepatocyte apoptosis/necrosis
 ↓ (KER: extent-dependent)
AO: Cholestatic liver injury
```

**MCP call sequence for AOP construction:**

```
Step 1: Identify the molecular initiating event
  mcp__chembl__chembl_data(method: "get_activities", chembl_id: "CHEMBLxxxx")
  → Primary target interaction, off-target hits

Step 2: Map downstream pathway perturbations
  mcp__kegg__kegg_data(method: "find_pathway", query: "relevant_pathway_keyword")
  mcp__reactome__reactome_data(method: "search_pathways", query: "stress response")

Step 3: Link to organ-level phenotype
  mcp__hpo__hpo_data(method: "search_hpo_terms", query: "liver failure")
  mcp__opentargets__ot_data(method: "get_target_info", target_id: "ENSG_ID")
  → Target safety, known adverse phenotypes

Step 4: Clinical evidence for the AO
  mcp__fda__fda_data(method: "search_adverse_events", drug_name: "compound_name")
  mcp__pubmed__pubmed_data(method: "search", keywords: "compound AOP adverse outcome pathway")

Step 5: Weight of evidence assessment
  Evaluate each KER: strong, moderate, or weak evidence
  Assign overall AOP confidence: high, moderate, low
```

---

### Workflow 4: IVIVE Modeling (In Vitro to In Vivo Extrapolation)

**IVIVE Framework:**

```
In Vitro Effective Concentration (EC50, IC50)
  → Nominal-to-free concentration correction (fu,inc, protein binding)
    → Reverse dosimetry (PBK modeling)
      → Predicted in vivo dose (mg/kg/day)
        → Margin of Safety = NOAEL / Human Equivalent Dose
```

**Key IVIVE Parameters:**

| Parameter | Source | Purpose |
|-----------|--------|---------|
| IC50/EC50 (nominal) | In vitro assay | Starting point |
| fu,inc | Measured or predicted | Free fraction in incubation |
| fu,plasma | Measured or predicted | Free fraction in plasma |
| Cmax,free | PK data or prediction | Maximum free plasma concentration |
| Vd | PK data | Volume of distribution |
| CLint | Microsomal/hepatocyte data | Intrinsic clearance |

**Margin of Safety Calculation:**

```
Safety Margin = In vitro IC50 (free) / Cmax,free (at therapeutic dose)

Interpretation:
  < 1x:    Toxicity expected at therapeutic doses
  1-10x:   Narrow margin — high risk
  10-30x:  Moderate margin — monitor closely
  30-100x: Adequate margin — standard monitoring
  > 100x:  Wide margin — low concern
```

**MCP calls for IVIVE data gathering:**

```
Step 1: In vitro potency data
  mcp__chembl__chembl_data(method: "get_activities", chembl_id: "CHEMBLxxxx")
  → IC50/EC50 for toxicity endpoints (hERG, BSEP, mitotox)

Step 2: Pharmacokinetic parameters
  mcp__drugbank__drugbank_data(method: "get_pharmacology", drugbank_id: "DBxxxxx")
  → Cmax, protein binding, Vd, clearance

Step 3: Dose and exposure information
  mcp__fda__fda_data(method: "get_drug_label", drug_name: "compound_name")
  → Approved dose, PK section with Cmax/AUC data
```

---

### Workflow 5: Safety Biomarker Assessment

**Traditional vs. Novel Safety Biomarkers:**

| Organ | Traditional Biomarkers | Novel/Qualified Biomarkers | Advantage of Novel |
|-------|----------------------|---------------------------|-------------------|
| **Liver** | ALT, AST, ALP, TBil | GLDH, miR-122, HMGB1, K18 (M30/M65), OPN | Earlier detection, mechanistic specificity |
| **Kidney** | BUN, sCr, urinalysis | KIM-1, NGAL, clusterin, cystatin C, trefoil factor 3 | Detect injury before functional loss |
| **Heart** | CK-MB, troponin | hs-troponin, NT-proBNP, FABP3, myosin | Greater sensitivity, structural vs. functional |
| **Skeletal muscle** | CK, aldolase | FABP3, sTnI, myosin light chain | Tissue specificity |
| **Testis** | Testosterone, inhibin B | SP-10, clusterin, FABP9 | Earlier detection of germ cell injury |
| **Pancreas** | Amylase, lipase | miR-216a, miR-217 | Tissue specificity |

**FDA/EMA Qualified Biomarkers (Context of Use):**

| Biomarker | Organ | Qualification Status | Context of Use |
|-----------|-------|---------------------|----------------|
| KIM-1 | Kidney | FDA/EMA qualified | Nonclinical AKI detection |
| NGAL | Kidney | FDA/EMA qualified | Nonclinical AKI detection |
| Clusterin | Kidney | FDA/EMA qualified | Nonclinical tubular injury |
| Cystatin C | Kidney | FDA/EMA qualified | Nonclinical GFR change |
| Trefoil Factor 3 | Kidney | FDA/EMA qualified | Nonclinical collecting duct injury |
| GLDH | Liver | FDA qualified | Hepatocellular injury (clinical) |
| miR-122 | Liver | EMA letter of support | Hepatocyte-specific injury |
| HMGB1 | Liver | Exploratory | Necrosis marker |
| hs-Troponin | Heart | Clinical standard | Myocardial injury |

**MCP calls for biomarker evaluation:**

```
Step 1: Identify expected organ toxicity
  mcp__drugbank__drugbank_data(method: "get_toxicity", drugbank_id: "DBxxxxx")
  mcp__fda__fda_data(method: "get_drug_label", drug_name: "compound_name")
  → Target organ identification from nonclinical/clinical sections

Step 2: Map to phenotype
  mcp__hpo__hpo_data(method: "search_hpo_terms", query: "elevated transaminases")
  → Human phenotype correlates

Step 3: Literature on biomarker performance
  mcp__pubmed__pubmed_data(method: "search", keywords: "KIM-1 nephrotoxicity biomarker qualification")

Step 4: Pathway context for biomarker
  mcp__geneontology__go_data(method: "search_go_terms", query: "response to oxidative stress")
  mcp__reactome__reactome_data(method: "search_pathways", query: "cellular stress response")
```

---

### Workflow 6: Structural Toxicity Alert Analysis

**Known Toxicophores and Reactive Metabolite Alerts:**

| Toxicophore | Reactive Intermediate | Toxicity Risk | Example Drugs |
|-------------|----------------------|---------------|---------------|
| Aniline / aromatic amine | Hydroxylamine → nitroso | Genotoxicity, agranulocytosis | Dapsone, procainamide |
| Nitroaromatic | Nitroso, hydroxylamine | Genotoxicity, carcinogenicity | Metronidazole, nitrofurantoin |
| Thiophene | S-oxide, epoxide | Hepatotoxicity (reactive metabolite) | Tienilic acid, suprofen |
| Furan | cis-Enedial | Hepatotoxicity | Furosemide, prazosin |
| Hydrazine | Diazene, radical | Hepatotoxicity, genotoxicity | Isoniazid, hydralazine |
| Quinone/hydroquinone | Semiquinone radical | Oxidative stress, cytotoxicity | Acetaminophen (NAPQI) |
| Michael acceptor | Direct electrophile | Protein adducts, organ toxicity | Acrylamide |
| Terminal alkene | Epoxide | Genotoxicity | Styrene |
| Acyl glucuronide | Protein adducts | Immune-mediated DILI | Diclofenac, zomepirac |

**Idiosyncratic Toxicity Risk Factors:**

| Factor | High Risk | Low Risk |
|--------|-----------|----------|
| Daily dose | > 50 mg/day | < 10 mg/day |
| Reactive metabolite formation | GSH adducts detected in vitro | No covalent binding |
| Lipophilicity (cLogP) | > 3 | < 1 |
| Extensive hepatic metabolism | > 50% hepatically cleared | Renal elimination |
| BSEP inhibition | IC50 < 25 μM | IC50 > 300 μM |

---

## Toxicity Risk Scoring (0-100)

Composite risk score integrating five domains. Each domain is weighted to reflect its predictive value for clinical toxicity.

### Scoring Components

#### 1. Known Toxicophore Alerts (20 points max)

| Finding | Score |
|---------|-------|
| No structural alerts | 0 |
| Single low-risk alert (e.g., phenol) | 5 |
| Single moderate-risk alert (e.g., aniline, thiophene) | 10 |
| Multiple moderate alerts or one high-risk alert (e.g., nitroaromatic, hydrazine) | 15 |
| Multiple high-risk alerts or known carcinogen scaffold | 20 |

#### 2. Off-Target Safety Panel (20 points max)

| Finding | Score |
|---------|-------|
| Clean panel (hERG >30 μM, no NHR activation, no PXR) | 0 |
| Single weak off-target hit (hERG 10-30 μM or weak NHR) | 5 |
| hERG 1-10 μM or PXR activation (CYP induction risk) | 10 |
| hERG <1 μM or multiple NHR activations | 15 |
| hERG <1 μM AND NHR/PXR hits AND additional ion channel activity | 20 |

#### 3. Organ Toxicity Risk (25 points max)

| Finding | Score |
|---------|-------|
| No organ toxicity signals | 0 |
| Single organ: weak signal (e.g., mild ALT elevation in preclinical) | 7 |
| Single organ: moderate signal (e.g., DILI with identifiable mechanism) | 12 |
| Multi-organ or severe single organ (e.g., Hy's Law case, renal failure) | 18 |
| Boxed warning, REMS, or drug withdrawal for organ toxicity | 25 |

#### 4. Reactive Metabolite Potential (15 points max)

| Finding | Score |
|---------|-------|
| No reactive metabolite risk | 0 |
| Theoretical risk from structure but no data | 4 |
| CYP-mediated bioactivation predicted, no GSH adducts detected | 8 |
| GSH adducts detected in vitro, daily dose <50 mg | 11 |
| GSH adducts detected, daily dose >50 mg, covalent binding to proteins | 15 |

#### 5. Therapeutic Index Estimation (20 points max)

| Finding | Score |
|---------|-------|
| Wide therapeutic index (TI >100, safety margin >100x) | 0 |
| Moderate TI (30-100x safety margin) | 5 |
| Narrow TI (10-30x safety margin) | 10 |
| Very narrow TI (3-10x safety margin) | 15 |
| Ultra-narrow TI (<3x safety margin) or no margin data | 20 |

### Risk Classification

| Total Score | Risk Level | Interpretation |
|-------------|-----------|----------------|
| 0-15 | LOW | Acceptable safety profile for standard development |
| 16-35 | MODERATE | Proceed with enhanced safety monitoring and specific studies |
| 36-55 | HIGH | Significant concern — requires risk mitigation strategy |
| 56-75 | VERY HIGH | Development at risk — needs compelling efficacy or redesign |
| 76-100 | CRITICAL | Development not recommended without major structural modification |

**MCP-driven scoring workflow:**

```
Step 1: Structural alert scan
  mcp__pubchem__pubchem_data(method: "get_compound", cid: CID_NUMBER)
  → Identify toxicophores from SMILES → Score component 1

Step 2: Safety panel data
  mcp__chembl__chembl_data(method: "get_activities", chembl_id: "CHEMBLxxxx")
  → hERG, NHR panel, PXR → Score component 2

Step 3: Organ toxicity signals
  mcp__fda__fda_data(method: "get_drug_label", drug_name: "compound_name")
  mcp__drugbank__drugbank_data(method: "get_toxicity", drugbank_id: "DBxxxxx")
  → Boxed warnings, organ tox findings → Score component 3

Step 4: Reactive metabolite assessment
  mcp__kegg__kegg_data(method: "get_pathway", pathway_id: "hsa00982")
  mcp__pubmed__pubmed_data(method: "search", keywords: "compound reactive metabolite GSH adduct")
  → Bioactivation risk → Score component 4

Step 5: Therapeutic index
  mcp__drugbank__drugbank_data(method: "get_pharmacology", drugbank_id: "DBxxxxx")
  mcp__chembl__chembl_data(method: "get_activities", chembl_id: "CHEMBLxxxx")
  → Efficacy vs toxicity exposure comparison → Score component 5
```

---

## Python Code Templates

### Dose-Response Curve Fitting

```python
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import t as t_dist
import matplotlib.pyplot as plt

def hill_equation(x, top, bottom, ec50, hill_slope):
    """Four-parameter logistic (Hill equation) for dose-response."""
    return bottom + (top - bottom) / (1 + (ec50 / x) ** hill_slope)

def fit_dose_response(concentrations, responses, compound_name="Compound"):
    """
    Fit a 4-parameter Hill equation to dose-response data.
    Returns EC50, Hill slope, confidence intervals.
    """
    conc = np.array(concentrations, dtype=float)
    resp = np.array(responses, dtype=float)

    # Initial parameter estimates
    p0 = [max(resp), min(resp), np.median(conc), 1.0]
    bounds = ([0, -np.inf, 1e-12, 0.1], [np.inf, np.inf, np.inf, 10])

    try:
        popt, pcov = curve_fit(hill_equation, conc, resp, p0=p0, bounds=bounds, maxfev=10000)
        top, bottom, ec50, hill_slope = popt

        # Confidence intervals
        perr = np.sqrt(np.diag(pcov))
        n = len(conc)
        dof = n - len(popt)
        t_val = t_dist.ppf(0.975, dof)
        ci = t_val * perr

        # R-squared
        residuals = resp - hill_equation(conc, *popt)
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((resp - np.mean(resp)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Plot
        x_fit = np.logspace(np.log10(min(conc)), np.log10(max(conc)), 200)
        y_fit = hill_equation(x_fit, *popt)

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(conc, resp, c='black', zorder=5, label='Data')
        ax.plot(x_fit, y_fit, 'r-', linewidth=2, label=f'Hill fit (R²={r_squared:.3f})')
        ax.axhline(y=50, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(x=ec50, color='blue', linestyle='--', alpha=0.5, label=f'EC50={ec50:.3f} μM')
        ax.set_xscale('log')
        ax.set_xlabel('Concentration (μM)')
        ax.set_ylabel('Response (%)')
        ax.set_title(f'{compound_name} Dose-Response Curve')
        ax.legend()
        plt.tight_layout()
        plt.savefig('dose_response.png', dpi=150)
        plt.close()

        print(f"EC50: {ec50:.4f} μM (95% CI: {ec50-ci[2]:.4f} - {ec50+ci[2]:.4f})")
        print(f"Hill slope: {hill_slope:.3f} (95% CI: {hill_slope-ci[3]:.3f} - {hill_slope+ci[3]:.3f})")
        print(f"Top: {top:.2f}, Bottom: {bottom:.2f}")
        print(f"R²: {r_squared:.4f}")

        return {"ec50": ec50, "hill_slope": hill_slope, "top": top, "bottom": bottom,
                "r_squared": r_squared, "ci_ec50": (ec50 - ci[2], ec50 + ci[2])}
    except Exception as e:
        print(f"Fitting failed: {e}")
        return None
```

### Margin of Safety Calculations

```python
import numpy as np
import pandas as pd

def calculate_margins_of_safety(compound_name, tox_endpoints, pk_params):
    """
    Calculate margins of safety for multiple toxicity endpoints.

    tox_endpoints: list of dicts with keys:
        - name: endpoint name (e.g., "hERG IC50")
        - value_uM: IC50/EC50 in μM
        - endpoint_type: "IC50", "EC50", "NOAEL", "LOAEL"

    pk_params: dict with keys:
        - cmax_total_uM: total Cmax at therapeutic dose (μM)
        - protein_binding_pct: plasma protein binding (%)
        - therapeutic_dose_mg: therapeutic dose (mg)
        - noael_mg_kg: NOAEL from animal studies (mg/kg/day), optional
        - human_equiv_dose_mg: HED from allometric scaling (mg), optional
    """
    fu = 1 - (pk_params["protein_binding_pct"] / 100)
    cmax_free = pk_params["cmax_total_uM"] * fu

    results = []
    for ep in tox_endpoints:
        mos = ep["value_uM"] / cmax_free if cmax_free > 0 else float('inf')

        if mos < 10:
            risk = "HIGH"
        elif mos < 30:
            risk = "MODERATE"
        elif mos < 100:
            risk = "LOW"
        else:
            risk = "MINIMAL"

        results.append({
            "Endpoint": ep["name"],
            "Type": ep["endpoint_type"],
            "Value (μM)": ep["value_uM"],
            "Cmax,free (μM)": round(cmax_free, 4),
            "Margin of Safety": round(mos, 1),
            "Risk Level": risk
        })

    # NOAEL-based margin if available
    if pk_params.get("noael_mg_kg") and pk_params.get("human_equiv_dose_mg"):
        noael = pk_params["noael_mg_kg"]
        hed = pk_params["human_equiv_dose_mg"]
        # HED = animal NOAEL * (animal Km / human Km) — already converted
        mos_noael = (noael * 60) / pk_params["therapeutic_dose_mg"]  # assuming 60 kg human
        results.append({
            "Endpoint": "NOAEL (preclinical)",
            "Type": "NOAEL",
            "Value (μM)": f"{noael} mg/kg/day",
            "Cmax,free (μM)": f"{pk_params['therapeutic_dose_mg']} mg dose",
            "Margin of Safety": round(mos_noael, 1),
            "Risk Level": "HIGH" if mos_noael < 10 else "MODERATE" if mos_noael < 30 else "LOW"
        })

    df = pd.DataFrame(results)
    print(f"\n{'='*70}")
    print(f"MARGIN OF SAFETY ANALYSIS: {compound_name}")
    print(f"{'='*70}")
    print(f"Therapeutic dose: {pk_params['therapeutic_dose_mg']} mg")
    print(f"Total Cmax: {pk_params['cmax_total_uM']} μM")
    print(f"Protein binding: {pk_params['protein_binding_pct']}%")
    print(f"Free Cmax: {cmax_free:.4f} μM")
    print(f"\n{df.to_string(index=False)}")
    print(f"{'='*70}\n")
    return df
```

### Toxicity Heatmap Visualization

```python
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

def toxicity_heatmap(compounds, endpoints, scores, output_file="tox_heatmap.png"):
    """
    Generate a toxicity heatmap across compounds and endpoints.

    compounds: list of compound names
    endpoints: list of endpoint names (e.g., ["hERG", "DILI", "Nephro", "Geno", "Cardio"])
    scores: 2D array (compounds x endpoints) with values 0-100
    """
    df = pd.DataFrame(scores, index=compounds, columns=endpoints)

    # Custom colormap: green → yellow → red
    tox_cmap = LinearSegmentedColormap.from_list("tox",
        [(0, "#2ecc71"), (0.3, "#f1c40f"), (0.6, "#e67e22"), (1, "#e74c3c")])

    fig, ax = plt.subplots(figsize=(max(8, len(endpoints) * 1.5), max(4, len(compounds) * 0.6)))

    sns.heatmap(df, annot=True, fmt=".0f", cmap=tox_cmap, vmin=0, vmax=100,
                linewidths=0.5, linecolor='white', cbar_kws={'label': 'Toxicity Risk Score'},
                ax=ax)

    ax.set_title("Toxicity Risk Profile Comparison", fontsize=14, fontweight='bold')
    ax.set_xlabel("Toxicity Endpoint", fontsize=11)
    ax.set_ylabel("Compound", fontsize=11)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_file, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Heatmap saved to {output_file}")

    # Summary statistics
    print(f"\nCompound Risk Summary:")
    for comp in compounds:
        total = df.loc[comp].sum()
        max_ep = df.loc[comp].idxmax()
        print(f"  {comp}: Total={total:.0f}, Highest risk: {max_ep} ({df.loc[comp, max_ep]:.0f})")
    return df
```

### Gene Signature Enrichment for Toxicity Pathways

```python
import numpy as np
import pandas as pd
from scipy.stats import fisher_exact, hypergeom

def toxicity_pathway_enrichment(degs, pathway_gene_sets, background_size=20000):
    """
    Test enrichment of differentially expressed genes in toxicity-related pathways.

    degs: list of differentially expressed gene symbols
    pathway_gene_sets: dict of {pathway_name: set_of_gene_symbols}
    background_size: total number of genes in the background (default: ~20k protein-coding)
    """
    degs_set = set(degs)
    n_degs = len(degs_set)
    results = []

    for pathway, genes in pathway_gene_sets.items():
        genes_set = set(genes)
        overlap = degs_set & genes_set
        k = len(overlap)  # DEGs in pathway
        K = len(genes_set)  # pathway size
        n = n_degs  # total DEGs
        N = background_size  # background

        # Fisher's exact test (2x2 contingency)
        table = [[k, K - k], [n - k, N - K - n + k]]
        odds_ratio, pval = fisher_exact(table, alternative='greater')

        # Hypergeometric p-value
        pval_hyper = hypergeom.sf(k - 1, N, K, n)

        # Fold enrichment
        expected = (K * n) / N
        fold_enrichment = k / expected if expected > 0 else 0

        results.append({
            "Pathway": pathway,
            "Pathway Size": K,
            "Overlap": k,
            "Expected": round(expected, 2),
            "Fold Enrichment": round(fold_enrichment, 2),
            "P-value (Fisher)": pval,
            "P-value (Hypergeometric)": pval_hyper,
            "Genes": ", ".join(sorted(overlap)) if overlap else "None"
        })

    df = pd.DataFrame(results).sort_values("P-value (Fisher)")

    # Bonferroni correction
    n_tests = len(results)
    df["P-adj (Bonferroni)"] = np.minimum(df["P-value (Fisher)"] * n_tests, 1.0)

    # BH correction
    ranks = range(1, n_tests + 1)
    df_sorted = df.sort_values("P-value (Fisher)")
    df_sorted["P-adj (BH)"] = np.minimum(
        df_sorted["P-value (Fisher)"] * n_tests / np.array(list(ranks)), 1.0
    )
    df_sorted["P-adj (BH)"] = df_sorted["P-adj (BH)"][::-1].cummin()[::-1]

    significant = df_sorted[df_sorted["P-adj (BH)"] < 0.05]

    print(f"Toxicity Pathway Enrichment Analysis")
    print(f"{'='*60}")
    print(f"Input DEGs: {n_degs}")
    print(f"Pathways tested: {n_tests}")
    print(f"Significant pathways (BH < 0.05): {len(significant)}")
    print(f"\nTop enriched toxicity pathways:")
    for _, row in significant.iterrows():
        print(f"  {row['Pathway']}: {row['Overlap']}/{row['Pathway Size']} genes, "
              f"FE={row['Fold Enrichment']:.1f}x, p-adj={row['P-adj (BH)']:.2e}")
    return df_sorted

# Example toxicity pathway gene sets (build from KEGG/Reactome queries):
TOXICITY_PATHWAYS = {
    "Oxidative Stress Response (NRF2)": {"NFE2L2", "KEAP1", "HMOX1", "NQO1", "GCLC", "GCLM",
                                          "TXNRD1", "GPX2", "SOD1", "SOD2", "CAT", "GSR"},
    "p53 DNA Damage Response": {"TP53", "MDM2", "CDKN1A", "BAX", "BBC3", "GADD45A", "GADD45B",
                                 "ATM", "ATR", "CHEK1", "CHEK2", "DDB2", "XPC"},
    "Mitochondrial Apoptosis": {"BAX", "BAK1", "BCL2", "BCL2L1", "CYCS", "APAF1", "CASP9",
                                 "CASP3", "BID", "DIABLO", "XIAP"},
    "Unfolded Protein Response": {"HSPA5", "ATF4", "ATF6", "ERN1", "EIF2AK3", "DDIT3", "XBP1",
                                   "CALR", "HSP90B1", "PDIA4"},
    "NF-kB Inflammation": {"NFKB1", "RELA", "TNF", "IL1B", "IL6", "CXCL8", "IKBKB", "NFKBIA",
                            "TNFAIP3", "PTGS2", "ICAM1"},
    "Bile Acid Transport": {"ABCB11", "ABCC2", "ABCB1", "SLC10A1", "ABCB4", "NR1H4",
                            "SLC51A", "SLC51B", "CYP7A1"},
    "Drug Metabolism Phase I": {"CYP1A2", "CYP2C9", "CYP2C19", "CYP2D6", "CYP3A4", "CYP2E1",
                                 "CYP1A1", "CYP2B6", "FMO3", "ADH1B", "ALDH2"},
    "Drug Metabolism Phase II": {"UGT1A1", "UGT2B7", "GSTA1", "GSTM1", "GSTP1", "SULT1A1",
                                  "NAT2", "TPMT", "COMT"},
}
```

---

## Evidence Grading for Toxicity Data

### Toxicity Evidence Tiers

| Tier | Label | Source | Weight | Examples |
|------|-------|--------|--------|----------|
| **T1** | Clinical Safety Data | Post-market human data | Highest | FAERS reports, REMS programs, boxed warnings, drug withdrawals, Phase III/IV safety data |
| **T2** | Preclinical In Vivo | Animal toxicology studies | High | GLP repeat-dose studies, carcinogenicity bioassays, reproductive/developmental toxicity (ICH S5) |
| **T3** | In Vitro Tox Assays | Cell-based and biochemical | Moderate | Ames test, hERG patch clamp, Tox21/ToxCast, BSEP inhibition, mitochondrial toxicity assays |
| **T4** | In Silico/QSAR | Computational prediction | Lowest | QSAR models, structural alerts, read-across, pharmacophore-based toxicity prediction |

### Applying Evidence Tiers

- Always report the highest available evidence tier for each toxicity finding
- When multiple tiers agree, confidence increases (concordance)
- T4 evidence alone should be flagged as "provisional — requires experimental confirmation"
- Discordant results across tiers require explicit discussion (e.g., in vitro positive but clinical data negative)

### Confidence Assessment

| Confidence | Criteria |
|------------|----------|
| **High** | T1 data available, concordant across tiers, biological mechanism understood |
| **Moderate** | T2-T3 data concordant, plausible mechanism, no contradicting clinical data |
| **Low** | T3-T4 data only, limited concordance, mechanism uncertain |
| **Very Low** | T4 predictions only, no experimental validation |

---

## Key Toxicology Concepts Reference

### LD50 / NOAEL / LOAEL

| Parameter | Definition | Application |
|-----------|-----------|-------------|
| **LD50** | Dose lethal to 50% of test animals | Acute toxicity classification (GHS categories 1-5) |
| **NOAEL** | No Observed Adverse Effect Level | Starting dose for first-in-human (FIH) calculation |
| **LOAEL** | Lowest Observed Adverse Effect Level | Identifies threshold for toxicity onset |
| **MRHD** | Maximum Recommended Human Dose | Basis for safety margin calculations |
| **HED** | Human Equivalent Dose (allometric scaling) | FIH dose = HED / safety factor (typically 10x) |

**GHS Acute Toxicity Categories (oral LD50, rat):**

| Category | LD50 (mg/kg) | Signal Word | Hazard |
|----------|-------------|-------------|--------|
| 1 | ≤ 5 | Danger | Fatal if swallowed |
| 2 | 5-50 | Danger | Fatal if swallowed |
| 3 | 50-300 | Danger | Toxic if swallowed |
| 4 | 300-2000 | Warning | Harmful if swallowed |
| 5 | 2000-5000 | Warning | May be harmful if swallowed |

### Threshold of Toxicological Concern (TTC)

Decision-tree approach for assessing risk from low-level exposure to chemicals without substance-specific toxicity data.

| Cramer Class | Description | TTC (μg/day) | Basis |
|--------------|-------------|-------------|-------|
| **Class I** | Simple structures, efficiently metabolized | 1800 | Low toxicity potential |
| **Class II** | Intermediate structures, less innocuous | 540 | Moderate toxicity potential |
| **Class III** | Complex structures, reactive groups | 90 | Significant toxicity potential |
| **Genotoxic** | Compounds with genotoxic alerts (non-cohort) | 1.5 | Lifetime cancer risk <10⁻⁵ |
| **Cohort of Concern** | Aflatoxin-like, azoxy, N-nitroso | 0.15 | Highly potent genotoxins |

**TTC does NOT apply to:** high-potency carcinogens, inorganic compounds, metals, proteins, steroids, nanomaterials, radioactive substances, PFAS.

### Ames Test Interpretation

| Result | Interpretation | Regulatory Action |
|--------|---------------|-------------------|
| **Negative** (all strains ± S9) | No evidence of mutagenicity | Proceed; additional genotox battery per ICH S2 |
| **Positive** (any strain ± S9) | Mutagenic potential | Triggers follow-up: in vivo micronucleus, comet assay |
| **Equivocal** | Borderline response | Repeat with modified protocol, additional strains |
| **Positive with S9 only** | Requires metabolic activation | Suggests CYP-mediated bioactivation to mutagen |
| **Positive without S9** | Direct-acting mutagen | Higher concern; reactive electrophile likely |

**Standard Ames strains:**

| Strain | Detection | Mutation Type |
|--------|-----------|---------------|
| TA98 | Frameshift mutations | GC base pairs |
| TA100 | Base-pair substitutions | GC base pairs |
| TA1535 | Base-pair substitutions | GC base pairs |
| TA1537 | Frameshift mutations | GC base pairs |
| TA102 or E. coli WP2 uvrA | Oxidative mutagens, cross-linkers | AT base pairs |

### ICH Guidelines Relevant to Toxicogenomics

| Guideline | Title | Toxicogenomics Relevance |
|-----------|-------|-------------------------|
| ICH S1 | Carcinogenicity Testing | Weight-of-evidence, 2-year bioassay alternatives |
| ICH S2 | Genotoxicity Testing | Ames test, in vivo micronucleus, standard battery |
| ICH S5 | Reproductive/Developmental Toxicity | Embryofetal development, fertility, peri-postnatal |
| ICH S6 | Preclinical Safety for Biotechnology Products | Species selection, immunogenicity |
| ICH S7A | Safety Pharmacology | Core battery (CNS, CV, respiratory) |
| ICH S7B | QTc Prolongation | hERG assay, in vivo QT studies, CiPA framework |
| ICH S9 | Nonclinical for Anticancer Drugs | Abbreviated tox programs for oncology |
| ICH M3 | Nonclinical Safety Studies for Clinical Trials | Timing and duration of nonclinical studies |
| ICH M7 | Mutagenic Impurities | Acceptable intake limits, TTC, QSAR assessment |

---

## Multi-Agent Workflow Examples

**"Assess the hepatotoxicity risk of our lead compound before IND"**
1. Toxicogenomics -> DILI mechanism analysis, DILIrank classification, BSEP assessment, safety biomarker panel, toxicity risk score
2. Chemical Safety & Toxicology -> Structural alert screen, drug-likeness, reactive metabolite flags
3. Drug Research -> Full pharmacology and PK profile
4. FDA Consultant -> IND nonclinical safety package requirements

**"Why does this drug cause kidney injury and what biomarkers should we monitor?"**
1. Toxicogenomics -> Nephrotoxicity AOP construction, IVIVE modeling, novel biomarker evaluation (KIM-1, NGAL)
2. Biomarker Discovery -> Biomarker qualification strategy, assay selection
3. Adverse Event Detection -> FAERS renal event signal detection
4. Clinical Pharmacology -> Dose-exposure-response for nephrotoxicity threshold

**"Characterize the toxicogenomic signature of compound X from our RNA-seq data"**
1. RNA-seq DESeq2 -> Differential expression analysis, fold changes, adjusted p-values
2. Toxicogenomics -> Toxicity pathway enrichment (NRF2, p53, UPR, mitochondrial), MoT tree classification, AOP mapping
3. Biomarker Discovery -> Identify translatable safety biomarker candidates from gene signature

**"Evaluate the cardiac safety of a kinase inhibitor series"**
1. Toxicogenomics -> hERG assessment, cardiac ion channel panel, QTc risk scoring, margin of safety
2. Drug Research -> Kinase selectivity profile, off-target identification
3. Clinical Pharmacology -> Free Cmax estimation, exposure-QTc modeling

## Completeness Checklist

- [ ] Compound identified and cross-referenced across DrugBank, ChEMBL, and PubChem
- [ ] Mechanism-of-toxicity (MoT) tree constructed with key initiating events
- [ ] Adverse outcome pathway (AOP) mapped from molecular initiating event to adverse outcome
- [ ] Organ-specific toxicity assessment completed (hepatotoxicity, nephrotoxicity, cardiotoxicity at minimum)
- [ ] Safety biomarker panel identified with translational relevance
- [ ] IVIVE modeling performed with margin-of-safety calculations
- [ ] Toxicity risk score assigned with evidence tier (T1-T4) for each finding
- [ ] Regulatory guideline alignment documented (ICH S2, S7A/B, S8, S9, M7 as applicable)
- [ ] Literature support retrieved for key toxicity mechanisms
- [ ] No `[Analyzing...]` placeholders remain in the report
