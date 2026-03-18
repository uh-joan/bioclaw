# Autoresearch x NanoClaw: Predictive Modeling Brainstorm

## What Is Autoresearch?

Karpathy's [autoresearch](https://github.com/karpathy/autoresearch) is an AI-driven autonomous research loop: an LLM agent modifies code → runs an experiment → evaluates the result → keeps or discards → repeats. ~12 experiments/hour, ~100 overnight. The key insight is **program.md** (research instructions) + **a single measurable metric** + **git as memory**.

NanoClaw already has a version of this pattern in `autoresearch/` — skill optimizers that use LLM-as-judge to score variant-interpretation and drug-interaction skills. The CT predictor extends this to **ML model optimization** using our 40 biomedical MCP servers as data sources.

---

## MCP Utilization Matrix

Which MCPs each project would query:

```
                          CT   DDI  Device Drug    Biomark  PGx      Safety  Repurp  Rare
                          Pred Pred Recall Attrtn  Panel    Response Signal  Score   Diag
                          ───  ───  ───    ───     ───      ───      ───     ───     ───
FDA                        ✓    ✓    ✓      ✓                        ✓       ✓
EMA                        ✓           ✓    ✓                        ✓       ✓
ClinicalTrials.gov         ✓✓        ✓      ✓✓              ✓                ✓
DrugBank                   ✓    ✓✓          ✓               ✓       ✓       ✓✓
ChEMBL                     ✓    ✓           ✓✓              ✓       ✓       ✓✓
PubChem                         ✓           ✓                        ✓       ✓
OpenTargets                ✓✓               ✓        ✓       ✓               ✓✓
PubMed                     ✓    ✓    ✓      ✓        ✓       ✓       ✓       ✓       ✓
bioRxiv                    ✓                ✓        ✓                        ✓
OpenAlex                   ✓                ✓        ✓                        ✓
NLM                        ✓    ✓    ✓      ✓        ✓       ✓       ✓       ✓       ✓
ClinVar                                     ✓        ✓✓      ✓✓              ✓
COSMIC                                      ✓        ✓✓      ✓✓
GWAS Catalog                                ✓        ✓✓      ✓               ✓✓
gnomAD                                      ✓        ✓       ✓               ✓       ✓
Ensembl                                     ✓        ✓✓      ✓✓              ✓       ✓
GTEx                                        ✓        ✓✓      ✓               ✓       ✓
GEO                                                  ✓       ✓
JASPAR                                               ✓                                ✓
UniProt                         ✓           ✓        ✓       ✓               ✓       ✓
AlphaFold                       ✓           ✓                                ✓       ✓
PDB                             ✓           ✓                                ✓       ✓
STRING-db                       ✓           ✓        ✓       ✓               ✓       ✓
BindingDB                       ✓✓          ✓✓                       ✓       ✓✓
Reactome                        ✓           ✓        ✓       ✓               ✓       ✓
KEGG                            ✓           ✓        ✓       ✓               ✓       ✓
Gene Ontology                               ✓        ✓       ✓               ✓       ✓
HPO                                  ✓      ✓        ✓       ✓                       ✓✓
Monarch                              ✓      ✓        ✓       ✓               ✓       ✓✓
DepMap                                      ✓        ✓       ✓✓
cBioPortal                                  ✓        ✓✓      ✓✓
HMDB                            ✓                    ✓       ✓
ClinPGx                   ✓    ✓✓                    ✓       ✓✓      ✓       ✓
Medicare                   ✓         ✓                        ✓       ✓✓
Medicaid                   ✓         ✓                        ✓       ✓✓
CDC                                  ✓                        ✓       ✓
EU Filings                 ✓              ✓                           ✓       ✓
BRENDA                          ✓           ✓                                ✓       ✓
CELLxGENE                                            ✓✓      ✓✓
ESM                                         ✓                                ✓       ✓
───────────────────────────────────────────────────────────────────────────────────────────
MCP count:                18   16    8     30       26       27       14      30      20
```

---

## All Projects

### 1. Clinical Trial Outcome Predictor ⭐ (BUILDING FIRST — 18 MCPs)

**Goal:** Predict whether a Phase 2/3 clinical trial will meet its primary endpoint.

**Why this is the best starting point:**
- Binary outcome with clear labels (FDA approval = success, terminated/no approval = failure)
- 18 MCPs provide deep feature coverage
- ClinicalTrials.gov has structured, queryable data
- Ground truth is publicly available
- The data collection pattern generalizes to all other projects

**Feature vector per trial:**

| Feature | Source MCP | Why it's predictive |
|---------|-----------|---------------------|
| Phase (2 vs 3) | ClinicalTrials.gov | Base rates differ dramatically |
| Indication area | ClinicalTrials.gov | Oncology vs CNS vs metabolic have different success rates |
| Target genetic evidence score | OpenTargets | Trials with strong genetic evidence succeed 2x more |
| Number of GWAS hits for indication | GWAS Catalog | More genetic validation = higher success probability |
| Target constraint (pLI score) | gnomAD | Highly constrained targets → essential → more side effects |
| Target tissue expression specificity | GTEx | Ubiquitous expression → off-target toxicity risk |
| Known pathogenic variants in target | ClinVar | Genetic proof that target drives disease |
| Target in cancer dependency screen | DepMap | Functional validation of target essentiality |
| cBioPortal mutation frequency | cBioPortal | How often target is mutated in patient tumors |
| Compound selectivity (# targets) | ChEMBL | More selective = fewer side effects |
| Best-in-class potency ratio | BindingDB | Competitive potency advantage |
| Known drug interactions for class | DrugBank | Interaction complexity |
| CYP metabolism liability | ClinPGx | PGx-related variability risk |
| Target pathway centrality | Reactome + STRING-db | Central targets harder to drug safely |
| Competitor trial count | ClinicalTrials.gov | Competitive landscape |
| Publication velocity | PubMed + OpenAlex | Research momentum signal |
| Preprint signal | bioRxiv | Early research activity |
| Medicare/Medicaid spend on SOC | Medicare + Medicaid | Unmet need proxy |
| Enrollment size | ClinicalTrials.gov | Statistical power proxy |
| Sponsor type (pharma vs biotech) | ClinicalTrials.gov | Resource/experience proxy |
| Prior phase success | ClinicalTrials.gov | Historical track record |
| Endpoint type (OS, PFS, ORR) | ClinicalTrials.gov | Different bar heights |
| FDA precedent for indication | FDA | Regulatory pathway clarity |
| EMA approval pattern | EMA + EU Filings | Dual-market signal |
| Disease phenotype complexity | HPO + Monarch | Complex phenotypes = harder trials |

**Ground truth labeling:**
- ClinicalTrials.gov status = "Completed" + FDA approval within 3 years → **success**
- ClinicalTrials.gov status = "Terminated" / "Withdrawn" / completed without approval → **failure**

See `projects/ct-predictor/` for implementation.

---

### 2. Drug Attrition Stage Predictor (30 MCPs)

**Goal:** Given a compound in Phase 1, predict *where* it will fail: Phase 1 (safety), Phase 2 (efficacy), Phase 3 (efficacy at scale), or regulatory rejection. Multi-class version of CT predictor.

**Phase 1 failure (safety) features:**
- Target pLI constraint score (gnomAD)
- Number of tissues with high expression (GTEx)
- Selectivity ratio on vs off-target (ChEMBL + BindingDB)
- Structural alerts PAINS/Brenk (PubChem)
- CYP inhibition profile (ClinPGx)
- PPI degree (STRING-db)
- Target in essential gene list (DepMap)
- Enzyme kinetics tight binding (BRENDA)
- Target cellular compartment (Gene Ontology)
- FAERS class-level adverse events (FDA)
- Metabolite toxicity flags (HMDB)

**Phase 2 failure (efficacy) features:**
- Genetic evidence score (OpenTargets)
- GWAS effect size (GWAS Catalog)
- Target-disease evidence types (OpenTargets)
- Pathway redundancy/paralogs (Reactome + KEGG)
- Biomarker availability (ClinVar + cBioPortal)
- Single-cell expression in disease cells (CELLxGENE)
- Gene regulatory centrality (Ensembl + JASPAR)
- Published preclinical effect sizes (PubMed)
- Protein structure druggability (AlphaFold + PDB)

**Phase 3 failure features:**
- Phase 2 effect size from literature (PubMed)
- Patient population heterogeneity (gnomAD ancestry)
- PGx variability (ClinPGx)
- Competing trial landscape (ClinicalTrials.gov)
- Real-world SOC effectiveness (Medicare + Medicaid)
- Disease phenotype heterogeneity (HPO + Monarch)

**Regulatory failure features:**
- FDA precedent (FDA)
- EMA pattern (EMA + EU Filings)
- Endpoint acceptance history (ClinicalTrials.gov + PubMed)
- CDC disease burden/unmet need (CDC)

---

### 3. Drug Repurposing Opportunity Scorer (30 MCPs)

**Goal:** Given an approved drug, score all untested indications by probability of success. Recommendation system, not binary classifier.

For every (drug, new_indication) pair, predict a repurposing success probability.

**Drug characterization features:**
- All known targets + affinities (DrugBank + ChEMBL + BindingDB)
- Mechanism of action (DrugBank)
- Protein structure of targets (AlphaFold + PDB)
- Target pathway membership (Reactome + KEGG)
- Target PPI network (STRING-db)
- Target protein function (UniProt + Gene Ontology)
- Known safety profile (FDA FAERS)
- CYP metabolism (ClinPGx)
- Metabolite profile (HMDB)
- ESM embedding similarity (ESM)
- Enzyme kinetics (BRENDA)

**New indication features:**
- Disease-target genetic evidence (OpenTargets)
- GWAS associations (GWAS Catalog)
- Disease-associated variants (ClinVar)
- Disease phenotype overlap with approved indication (HPO + Monarch)
- Disease gene expression signature (GEO + GTEx + CELLxGENE)
- Cancer landscape if oncology (COSMIC + cBioPortal + DepMap)
- Population allele frequencies (gnomAD)
- Regulatory elements (JASPAR + Ensembl)
- Epidemiological burden (CDC)
- Treatment cost (Medicare + Medicaid)
- Existing trials (ClinicalTrials.gov)
- Literature signal (PubMed + bioRxiv + OpenAlex)
- Regulatory precedent (FDA + EMA + EU Filings)
- Terminology mapping (NLM)

**Ground truth:** Historical repurposing successes (thalidomide → myeloma, sildenafil → PAH, metformin → PCOS) vs. failed attempts.

---

### 4. Pharmacogenomic Response Predictor (27 MCPs)

**Goal:** Given a drug + patient genotype, predict response category: optimal, normal, poor responder, or adverse reactor.

**Direct PGx evidence:** ClinPGx (CPIC level, star alleles, metabolizer status), gnomAD (population frequency)

**Drug-side:** DrugBank + ClinPGx (metabolizing enzymes), DrugBank (therapeutic index), HMDB (active metabolites), ChEMBL + BindingDB (target affinity), PDB + AlphaFold (binding site), BRENDA (enzyme kinetics)

**Patient-side genomic:** ClinVar (target gene variants), GTEx (eQTL effects), GTEx + CELLxGENE (tissue expression), Ensembl (gene copy number), Reactome + KEGG (pathway burden), STRING-db (PPI perturbation), UniProt + GO (protein function), Monarch + HPO + OpenTargets (disease-gene), COSMIC + cBioPortal + DepMap (somatic context), GWAS Catalog (drug response traits), JASPAR (regulatory variants)

**Validation:** FDA (FAERS demographics), Medicare + Medicaid (claims outcomes), PubMed + bioRxiv + OpenAlex (published PGx), FDA + EMA (label requirements)

**Ground truth:** CPIC level A guidelines where genotype-outcome mapping is established. Train on these, predict for level B/C drugs.

---

### 5. Biomarker Panel Discovery Engine (26 MCPs)

**Goal:** For a given disease, automatically discover the optimal biomarker panel (3-10 markers) that maximally predicts disease status, progression, or treatment response.

The autoresearch loop searches the **feature space across omics layers:**

| Layer | Source MCPs | Feature type |
|-------|-----------|-------------|
| Genomic variants | ClinVar, GWAS, gnomAD | SNPs, pathogenicity scores |
| Somatic mutations | COSMIC, cBioPortal | Mutation frequency, TMB |
| Gene expression | GTEx, GEO, CELLxGENE | Expression levels, ratios |
| Protein levels | UniProt, AlphaFold | Structure-function |
| Protein interactions | STRING-db | Network centrality |
| Pathways | Reactome, KEGG, GO | Pathway enrichment |
| Epigenetic | JASPAR, Ensembl | Regulatory disruption |
| Metabolites | HMDB | Metabolite ratios |
| Phenotype | HPO, Monarch | Phenotype similarity |
| Functional | DepMap | Gene essentiality |
| Enzyme kinetics | BRENDA | Activity changes |
| Protein sequence | ESM | Embedding anomaly scores |

---

### 6. Safety Signal Early Warning (14 MCPs)

**Goal:** Predict which currently-approved drugs will receive new FDA safety warnings (black box, REMS, withdrawal) in the next 12-24 months.

**Features:**
- AE reporting rate trend slope (FDA FAERS)
- Serious outcome ratio (FDA)
- Proportional reporting ratio for top AEs (FDA)
- Time-on-market (FDA)
- EMA safety signal history (EMA)
- Medicare utilization trend (Medicare)
- Medicaid population exposure (Medicaid)
- CDC population health correlation (CDC)
- Drug interaction count growth (DrugBank)
- CYP liability profile (ClinPGx)
- Target safety literature velocity (PubMed + bioRxiv)
- Citation growth rate for safety papers (OpenAlex)
- Known metabolite toxicity (HMDB)
- Off-target binding predictions (ChEMBL + BindingDB)

**Ground truth:** Historical FDA label changes, withdrawals, REMS additions.

---

### 7. Rare Disease Diagnosis Prioritizer (20 MCPs)

**Goal:** Given patient phenotypes (HPO terms), rank candidate diagnoses and causal genes by probability.

**Features per (phenotype_set, candidate_gene) pair:**
- HPO semantic similarity (HPO + Monarch)
- Gene-disease association strength (OpenTargets + Monarch)
- Variant pathogenicity (ClinVar)
- Population constraint pLI/LOEUF (gnomAD)
- Tissue expression match (GTEx + CELLxGENE)
- Functional annotation (Gene Ontology + UniProt)
- Protein structure impact (AlphaFold + PDB + ESM)
- Pathway involvement (Reactome + KEGG)
- PPI network disease gene neighbors (STRING-db)
- Regulatory element overlap (JASPAR + Ensembl)
- Cancer overlap if relevant (COSMIC + DepMap)
- GWAS association (GWAS Catalog)
- Literature evidence (PubMed + bioRxiv)
- Enzyme kinetics perturbation (BRENDA)
- Metabolite pathway disruption (HMDB)

---

### 8. Device Recall Predictor (8 MCPs)

**Goal:** Predict which FDA-cleared devices face Class I/II recalls.

Features from FDA MCP (classification, MAUDE adverse events, manufacturer history, predicate device recalls, time since clearance) + Medicare/Medicaid (utilization), CDC (population health), HPO (phenotype severity).

---

### 9. DDI Severity Predictor (16 MCPs)

**Goal:** Given two drugs, predict interaction severity (none/mild/moderate/severe/contraindicated).

Features: shared CYP substrates (ClinPGx), overlapping targets (ChEMBL + DrugBank), same pathway (Reactome + KEGG), FAERS co-reporting signal (FDA), protein binding competition (DrugBank), half-life ratio (DrugBank), therapeutic index (DrugBank), mechanism similarity (ChEMBL), structural similarity (PubChem + AlphaFold + PDB), metabolite interactions (HMDB), enzyme kinetics (BRENDA), PPI overlap (STRING-db + UniProt), binding affinity overlap (BindingDB).

---

## Project Rankings

| # | Project | MCPs | Ground Truth | Impact | Difficulty |
|---|---------|------|-------------|--------|-----------|
| 1 | **Clinical Trial Predictor** | 18 | High (binary) | Very high | Medium |
| 2 | **Drug Attrition Stage** | 30 | High (public) | Very high | Hard |
| 3 | **Drug Repurposing Scorer** | 30 | Medium (few cases) | Enormous | Hard |
| 4 | **PGx Response** | 27 | High (CPIC) | High | Medium |
| 5 | **Biomarker Panel** | 26 | Medium (cohorts) | Very high | Hard |
| 6 | **Safety Signal Warning** | 14 | High (FDA actions) | Very high | Medium |
| 7 | **Rare Disease Diagnosis** | 20 | High (solved cases) | High | Medium |
| 8 | **Device Recall** | 8 | High (FDA database) | Medium | Easy |
| 9 | **DDI Severity** | 16 | High (DrugBank) | Medium | Easy |

---

## Architecture

```
autoresearch/
├── BRAINSTORM.md                # This file
├── projects/
│   ├── ct-predictor/            # ⭐ Building first
│   │   ├── program.md           # Research instructions for autoresearch agent
│   │   ├── collect.py           # MCP data extraction → CSV cache
│   │   ├── features.py          # Feature engineering (MUTABLE by agent)
│   │   ├── train.py             # Model training (MUTABLE by agent)
│   │   ├── evaluate.py          # Held-out evaluation (FROZEN)
│   │   ├── results.tsv          # Experiment log
│   │   ├── data/                # Cached MCP extractions
│   │   └── logs/                # Round-by-round results
│   └── ... future projects ...
├── run-ct.ts                    # Autoresearch loop for CT predictor
└── shared/                      # Reusable MCP query modules
```

**Key design:** Data collection runs inside NanoClaw containers (MCP access). Autoresearch loop runs outside on cached data. Agent modifies features.py and train.py, evaluates on held-out set.

---

## Wild Ideas

- **Meta-predictor**: Predict which research questions your MCP data can answer well
- **Patent expiry opportunity scorer**: Off-patent molecules × OpenTargets genetic evidence × trial landscape gaps
- **Biomarker discovery loop**: Iterate on which omics features best predict treatment response in specific cancer types
- **Compound the predictors**: CT predictor feeds Drug Attrition, which feeds Repurposing Scorer — a full drug development probability engine
