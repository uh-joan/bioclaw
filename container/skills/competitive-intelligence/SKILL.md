---
name: competitive-intelligence
description: "Patent landscape analysis, pipeline tracking, market exclusivity, competitive positioning, LOE analysis, therapeutic area landscaping"
---

# Competitive Intelligence

Pharma and biotech competitive intelligence specialist for systematic analysis of therapeutic landscapes, pipeline competitors, patent/exclusivity positions, and market dynamics. This skill combines regulatory data (FDA, EMA), clinical trial intelligence, patent and exclusivity tracking, and scientific publication monitoring to produce actionable competitive assessments. It covers the full CI lifecycle: therapeutic area landscaping, pipeline competitor tracking, differentiation assessment, loss of exclusivity (LOE) analysis, and congress/publication monitoring.

Distinct from **drug-research** (which produces comprehensive single-drug monographs) and **clinical-pharmacology** (which focuses on PK/PD modeling and dose optimization). This skill operates at the landscape level, comparing multiple drugs, sponsors, and programs within a therapeutic area to inform strategic positioning decisions.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_competitive-intelligence_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Comprehensive single-drug monograph or compound deep-dive → use `drug-research`
- PK/PD modeling, dose optimization, or therapeutic window analysis → use `clinical-pharmacology`
- FAERS signal detection or disproportionality analysis → use `adverse-event-detection`
- Clinical trial design or statistical analysis → use `clinical-trial-analyst`
- FDA regulatory pathway or submission strategy → use `fda-consultant`
- Biomarker identification or companion diagnostic strategy → use `biomarker-discovery`

## Cross-Reference: Other Skills

- **Comprehensive single-drug monographs, compound disambiguation** -> use drug-research skill
- **PK/PD modeling, dose optimization, therapeutic window analysis** -> use clinical-pharmacology skill
- **FAERS signal detection, disproportionality analysis, safety scoring** -> use adverse-event-detection skill
- **Biomarker identification, patient stratification, companion diagnostics** -> use biomarker-discovery skill

---

## Available MCP Tools

### `mcp__clinicaltrials__ct_data` (Pipeline Tracking & Competitor Trials)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_studies` | Search clinical trials by drug, condition, sponsor, phase | `query`, `status`, `phase`, `limit` |
| `get_study` | Full trial record: design, endpoints, enrollment, sponsor, sites | `nct_id` |
| `get_study_results` | Published trial results (primary/secondary endpoints) | `nct_id` |

**CI-specific queries:**
- Search by condition to map all pipeline entrants for a disease area
- Filter by phase to build pipeline waterfalls (Phase 1/2/3/filed/approved)
- Search by sponsor to track competitor portfolios
- Filter by status (RECRUITING, ACTIVE_NOT_RECRUITING, COMPLETED) for timeline intelligence
- Cross-reference interventions to identify mechanism-of-action clusters

### `mcp__fda__fda_data` (Approved Products & Safety Differentiation)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search FDA drug database by name, sponsor, or active ingredient | `query`, `limit` |
| `get_drug_label` | Full prescribing information: indications, dosing, warnings, clinical studies | `set_id` or `drug_name` |
| `search_adverse_events` | FAERS adverse event reports for safety differentiation | `drug_name`, `limit`, `serious` |

**CI-specific uses:**
- Extract approved indications, dosing regimens, and patient populations from labels
- Compare boxed warnings, contraindications, and REMS across competitors
- Identify NDA/ANDA/BLA application numbers and applicant (sponsor) information
- Track supplemental approvals for indication expansions and new formulations
- Mine FAERS for comparative safety profiles (tolerability differentiation)

### `mcp__ema__ema_data` (EU Regulatory Landscape)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_medicines` | Search EMA-authorized medicines by name or therapeutic area | `query`, `limit` |
| `get_medicine` | Full EMA product information: authorization status, conditions, EPAR | `product_id` |

**CI-specific uses:**
- Track EU marketing authorizations and conditional approvals
- Identify products authorized in EU but not US (and vice versa) for regulatory gap analysis
- Extract CHMP opinions and referral outcomes for competitive signal detection
- Monitor orphan drug designations and associated market exclusivity in EU

### `mcp__pubmed__pubmed_data` (Scientific Publications & Congress Abstracts)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search PubMed by keywords, MeSH terms, author, journal | `query`, `num_results` |
| `fetch_details` | Full article metadata: abstract, authors, journal, DOI, MeSH | `pmid` |

**CI-specific uses:**
- Monitor competitor publications for efficacy/safety data disclosures
- Track congress abstract publications (ASCO, AACR, AHA, ESC, ACR, EASL, AAN, etc.)
- Identify key opinion leaders (KOLs) publishing on competitive programs
- Search for head-to-head comparison studies and meta-analyses
- Monitor systematic reviews and network meta-analyses for indirect comparisons

### `mcp__opentargets__ot_data` (Drug-Target-Disease Landscape)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drug` | Search drugs by name across the Open Targets platform | `query`, `size` |
| `get_drug_info` | Drug details: mechanism, indications, linked targets, clinical trials | `drug_id` |
| `get_associations` | Evidence-scored target-disease associations | `target_id`, `disease_id`, `size` |

**CI-specific uses:**
- Map all drugs linked to a target for mechanism-class competitive analysis
- Identify novel targets with genetic evidence supporting disease association
- Assess target tractability and druggability for pipeline opportunity evaluation
- Cross-reference genetic associations to validate competitor target choices

### `mcp__drugbank__drugbank_data` (Competitor Drug Profiles)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Find drugs by name, identifier, or therapeutic category | `query`, `limit` |
| `get_drug` | Full drug profile: mechanism, pharmacology, targets, metabolism | `drugbank_id` |
| `get_interactions` | Drug-drug interactions (competitive DDI burden analysis) | `drugbank_id` |

**CI-specific uses:**
- Extract mechanism of action and pharmacology for competitive benchmarking
- Compare metabolic pathways (CYP liabilities as competitive differentiator)
- Identify all drugs acting on the same target (mechanism-class landscape)
- Assess pharmacological differentiation (selectivity, potency, PK profile)

### `mcp__chembl__chembl_data` (Pipeline Compound Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_molecule` | Search molecules by name, structure, or identifier | `query`, `limit` |
| `get_molecule` | Molecule details: structure, properties, development status, first approval | `chembl_id` |

**CI-specific uses:**
- Track development status of pipeline compounds (clinical candidate, Phase 1-3, approved)
- Identify compounds in development for the same indication
- Compare drug-like properties across competitors (MW, logP, selectivity)
- Map pipeline compounds to their targets for mechanism clustering

### `mcp__biorxiv__biorxiv_data` (Preprints Signaling Competitive Moves)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search bioRxiv/medRxiv preprints by keyword | `query`, `limit` |

**CI-specific uses:**
- Early detection of competitor data disclosures before peer review
- Identify emerging mechanisms or targets that may disrupt current landscapes
- Monitor preprints from competitor research teams
- Track real-world evidence studies posted as preprints ahead of congress presentation

### `mcp__openalex__openalex_data` (Competitor Publication Tracking & Research Expertise)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_works` | Track competitor publications by keywords; returns citation counts | `query` |
| `get_work` | Get publication details by DOI or PMID for competitive evidence | `id` |
| `search_authors` | Identify key researchers at competitor organizations | `query` |
| `get_author` | Researcher expertise profile, citation metrics, and institutional affiliation | `id` |
| `get_works_by_author` | Competitor researcher's publication record for IP and expertise assessment | `authorId` |
| `get_works_by_institution` | Track competitor institution's recent publications | `institutionId` |
| `search_institutions` | Identify research institutions active in the competitive space | `query` |
| `get_institution` | Institution research output, top topics, and associated organizations | `id` |
| `search_topics` | Map research topic activity for competitive white space analysis | `query` |
| `get_cited_by` | Track citation impact of competitor publications | `workId` |

**CI-specific uses:**
- Monitor competitor research teams' publication activity for early signal detection
- Assess research team expertise and depth by citation metrics and publication volume
- Identify potential acqui-hire targets or KOLs based on publication track records
- Map institutional research strengths for partnership or competitive threat assessment
- Detect emerging competitive mechanisms via topic-level publication trend analysis

### `mcp__cbioportal__cbioportal_data` (Cancer Market Landscape & Patient Populations)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_studies` | Cancer market landscape — find cancer cohorts and datasets for competitive sizing | `keyword`, `cancer_type` |
| `get_mutation_frequency` | Target mutation prevalence = addressable patient population for oncology drugs | `study_id`, `gene`, `profile_id` |

**cBioPortal workflow:** Use cBioPortal mutation frequencies to estimate addressable patient populations for oncology competitive analysis. Query mutation prevalence across TCGA and MSK-IMPACT datasets to size the biomarker-defined patient segments that competitor drugs target (e.g., KRAS G12C prevalence in NSCLC, BRAF V600E in melanoma).

```
mcp__cbioportal__cbioportal_data(method: "search_studies", cancer_type: "non-small cell lung cancer")
mcp__cbioportal__cbioportal_data(method: "get_mutation_frequency", study_id: "luad_tcga", gene: "KRAS")
mcp__cbioportal__cbioportal_data(method: "get_mutation_frequency", study_id: "skcm_tcga", gene: "BRAF")
```

---

## Core Workflows

### Workflow 1: Therapeutic Area Landscaping

Map all approved and pipeline drugs for a disease area, organized by phase and mechanism of action.

**Step 1: Identify all approved products**

```
mcp__fda__fda_data(method: "search_drugs", query: "DISEASE_NAME")
   -> List all FDA-approved drugs for the indication
   -> Extract: brand name, generic name, sponsor, approval date, NDA/BLA number

mcp__ema__ema_data(method: "search_medicines", query: "DISEASE_NAME")
   -> Cross-reference with EU authorizations
   -> Identify EU-only or US-only products
```

**Step 2: Map the clinical pipeline**

```
mcp__clinicaltrials__ct_data(method: "search_studies", query: "DISEASE_NAME", phase: "3", status: "RECRUITING")
   -> Active Phase 3 programs (near-term competitive threats)

mcp__clinicaltrials__ct_data(method: "search_studies", query: "DISEASE_NAME", phase: "2", status: "RECRUITING")
   -> Phase 2 programs (medium-term threats)

mcp__clinicaltrials__ct_data(method: "search_studies", query: "DISEASE_NAME", phase: "1", status: "RECRUITING")
   -> Phase 1 programs (early-stage landscape)
```

**Step 3: Cluster by mechanism of action**

```
mcp__drugbank__drugbank_data(method: "get_drug", drugbank_id: "DBxxxxx")
   -> Extract mechanism of action for each approved product

mcp__opentargets__ot_data(method: "get_drug_info", drug_id: "DRUG_ID")
   -> Extract target and mechanism for pipeline compounds

mcp__chembl__chembl_data(method: "get_molecule", chembl_id: "CHEMBLxxxxx")
   -> Development status and mechanism for early-stage compounds
```

**Step 4: Build the landscape matrix**

Organize all products and pipeline entries into a matrix:

```
| Mechanism / Target | Approved | Phase 3 | Phase 2 | Phase 1 | Preclinical |
|-------------------|----------|---------|---------|---------|-------------|
| [MoA Class 1]     | Drug A   | Drug D  | Drug G  |         |             |
| [MoA Class 2]     | Drug B   | Drug E  |         | Drug H  |             |
| [MoA Class 3]     | Drug C   |         | Drug F  |         | Drug I      |
| [Novel MoA]       |          |         |         | Drug J  | Drug K      |
```

**Step 5: Enrich with scientific context**

```
mcp__pubmed__pubmed_data(method: "search", query: "DISEASE_NAME treatment landscape review", num_results: 10)
   -> Recent landscape reviews and treatment guidelines

mcp__biorxiv__biorxiv_data(method: "search", query: "DISEASE_NAME novel therapy", limit: 10)
   -> Emerging approaches not yet in clinical trials
```

---

### Workflow 2: Pipeline Competitor Analysis

Deep-dive into a specific competitor's clinical program: trial design, endpoints, timelines, enrollment, and data readout expectations.

**Step 1: Identify competitor trials**

```
mcp__clinicaltrials__ct_data(method: "search_studies", query: "COMPETITOR_DRUG_NAME", limit: 50)
   -> All trials for the competitor compound
   -> Sort by phase and status
   -> Note: search by sponsor name to capture all programs

mcp__clinicaltrials__ct_data(method: "search_studies", query: "SPONSOR_NAME", limit: 100)
   -> Full sponsor portfolio view
```

**Step 2: Analyze pivotal trial design**

```
mcp__clinicaltrials__ct_data(method: "get_study", nct_id: "NCTxxxxxxxx")
   -> Extract: study design (parallel, crossover, adaptive)
   -> Primary endpoint and key secondary endpoints
   -> Target enrollment and actual enrollment
   -> Estimated primary completion date (data readout timing)
   -> Comparator arm (placebo, active, SOC)
   -> Key inclusion/exclusion criteria (patient population)
   -> Number of sites and geographic distribution
```

**Step 3: Check for published results**

```
mcp__clinicaltrials__ct_data(method: "get_study_results", nct_id: "NCTxxxxxxxx")
   -> Published results (if completed)

mcp__pubmed__pubmed_data(method: "search", query: "COMPETITOR_DRUG NCTxxxxxxxx", num_results: 5)
   -> Published trial results in peer-reviewed journals
```

**Step 4: Assess competitive positioning**

```
mcp__fda__fda_data(method: "get_drug_label", drug_name: "COMPETITOR_DRUG")
   -> If approved: full label for benchmarking

mcp__drugbank__drugbank_data(method: "get_drug", drugbank_id: "DBxxxxx")
   -> Mechanism, pharmacology, metabolism for differentiation analysis
```

**Step 5: Timeline intelligence**

Extract from trial records:
- Study start date -> time in clinic
- Primary completion date -> expected data readout
- Estimated study completion date -> full dataset availability
- Current enrollment vs target -> enrollment velocity
- PDUFA date (if NDA/BLA filed) -> regulatory decision timeline

---

### Workflow 3: Patent/Exclusivity Analysis

Track patent and regulatory exclusivity status for competitive products.

**Step 1: Identify regulatory exclusivities from FDA**

```
mcp__fda__fda_data(method: "search_drugs", query: "DRUG_NAME")
   -> Extract NDA/ANDA/BLA number
   -> Identify application type: 505(b)(1), 505(b)(2), ANDA, BLA
   -> Check for pediatric exclusivity extension (+6 months)
```

**Step 2: Determine exclusivity types and expiration**

Key Hatch-Waxman exclusivity categories:

| Exclusivity Code | Type | Duration | Trigger |
|-----------------|------|----------|---------|
| NCE | New Chemical Entity | 5 years | First approval of active moiety |
| NEW DOSAGE FORM | New Dosage Form | 3 years | New clinical investigations essential |
| ODE | Orphan Drug Exclusivity | 7 years | Orphan-designated indication |
| PED | Pediatric Exclusivity | +6 months | Completed pediatric studies per Written Request |
| FIRST GENERIC | 180-day FTF Exclusivity | 180 days | First ANDA with Para IV certification |
| CGE | Competitive Generic Therapy | 180 days | For complex generics (GDUFA II) |

**Step 3: Cross-reference patent listings**

```
mcp__fda__fda_data(method: "search_drugs", query: "DRUG_NAME")
   -> Orange Book listed patents (small molecules)
   -> Patent number, expiry date, patent type (drug substance, drug product, method of use)
   -> Para IV certification status (any ANDA filers?)

For biologics:
   -> Purple Book listing
   -> Reference product exclusivity (12 years BLA, 4 years BsLA)
   -> Biosimilar/interchangeable approvals
```

**Step 4: Analyze patent landscape**

```
mcp__pubmed__pubmed_data(method: "search", query: "DRUG_NAME patent landscape exclusivity", num_results: 5)
   -> Published patent analyses

mcp__chembl__chembl_data(method: "get_molecule", chembl_id: "CHEMBLxxxxx")
   -> First approval date (anchor for exclusivity calculations)
```

**Key patent concepts for CI analysis:**

- **Composition of matter (COM) patents**: Strongest protection; covers the molecule itself
- **Formulation patents**: Protect specific drug product configurations (extended-release, combination)
- **Method of use (MoU) patents**: Protect specific indications; can be "carved out" by generics
- **Process patents**: Weakest; protect manufacturing method only
- **Patent term extension (PTE)**: Up to 5 years added to one patent per product (35 USC 156)
- **Patent term adjustment (PTA)**: Compensates for USPTO prosecution delays
- **Paragraph IV certification**: ANDA filer challenges listed patents; triggers 30-month stay
- **Authorized generic (AG)**: Brand company licenses generic version; no Para IV needed
- **At-risk launch**: Generic launch before patent litigation resolved

---

### Workflow 4: Differentiation Assessment

Systematically compare a drug program against competitors across efficacy, safety, convenience, and access dimensions.

**Step 1: Gather efficacy data**

```
mcp__fda__fda_data(method: "get_drug_label", drug_name: "DRUG_A")
   -> Clinical studies section: pivotal trial results, response rates, survival data
   -> Repeat for each comparator drug

mcp__clinicaltrials__ct_data(method: "get_study_results", nct_id: "NCTxxxxxxxx")
   -> Primary endpoint results for head-to-head or common comparator trials

mcp__pubmed__pubmed_data(method: "search", query: "DRUG_A vs DRUG_B randomized", num_results: 10)
   -> Head-to-head comparison data
   -> Network meta-analyses for indirect comparisons
```

**Step 2: Compare safety profiles**

```
mcp__fda__fda_data(method: "search_adverse_events", drug_name: "DRUG_A", limit: 100)
   -> FAERS adverse event profile
   -> Repeat for each comparator

mcp__fda__fda_data(method: "get_drug_label", drug_name: "DRUG_A")
   -> Boxed warnings, contraindications, warnings & precautions
   -> Adverse reactions table (incidence in clinical trials)
   -> Compare REMS requirements across competitors
```

**Step 3: Assess convenience and compliance**

Extract from labels and trial records:
- Route of administration (oral > SC > IV for convenience)
- Dosing frequency (once daily > BID > TID; monthly > weekly > daily for injectables)
- Food restrictions (with/without food, fasting requirements)
- Monitoring requirements (lab tests, ECG, imaging)
- Drug-drug interaction burden (CYP liabilities)
- Storage requirements (room temperature > refrigerated > frozen)
- Administration setting (home self-administration > infusion center > hospital)

**Step 4: Evaluate patient population coverage**

```
mcp__fda__fda_data(method: "get_drug_label", drug_name: "DRUG_A")
   -> Approved population: age range, disease severity, prior therapy requirements
   -> Contraindicated populations (renal impairment, hepatic impairment, pregnancy)
   -> Special population data (pediatric, geriatric, race/ethnicity subgroups)
```

**Step 5: Build the differentiation matrix**

```
| Attribute           | Drug A      | Drug B       | Drug C       | Advantage |
|--------------------|-------------|--------------|--------------|-----------|
| Primary efficacy   | ORR 45%     | ORR 38%      | ORR 52%      | Drug C    |
| Median PFS         | 12.3 mo     | 10.1 mo      | 14.2 mo      | Drug C    |
| Grade 3+ AEs       | 28%         | 35%          | 41%          | Drug A    |
| Boxed warning      | No          | Yes (cardiac)| No           | A, C      |
| Dosing             | QD oral     | BID oral     | Q3W IV       | Drug A    |
| Line of therapy    | 1L-3L       | 2L+          | 1L-2L        | Drug A    |
| Pediatric data     | Yes         | No           | Pending      | Drug A    |
```

---

### Workflow 5: Loss of Exclusivity (LOE) Analysis

Track patent expiry timelines and assess generic/biosimilar entry scenarios.

**Step 1: Build the exclusivity timeline**

```
mcp__fda__fda_data(method: "search_drugs", query: "DRUG_NAME")
   -> NDA/BLA number, approval date
   -> Listed patents with expiry dates
   -> Regulatory exclusivities with expiry dates
   -> Pediatric exclusivity status (+6 months if granted)
```

**Step 2: Identify the "last exclusivity" date**

The LOE date is the latest of:
- Last Orange Book patent expiry (including any PTE)
- Last regulatory exclusivity expiry (NCE, ODE, PED)
- 30-month stay expiry (if Para IV litigation pending)

For biologics:
- 12-year reference product exclusivity from BLA approval
- 4-year data exclusivity (no BsLA filing before year 4)
- Patent dance outcomes (BPCIA 42 USC 262(l))

**Step 3: Assess generic/biosimilar pipeline**

```
mcp__clinicaltrials__ct_data(method: "search_studies", query: "DRUG_NAME generic OR biosimilar OR bioequivalence", limit: 20)
   -> Bioequivalence studies (signals ANDA filing intent)
   -> Biosimilar clinical trials (PK similarity, comparative efficacy)

mcp__fda__fda_data(method: "search_drugs", query: "DRUG_NAME")
   -> Check for approved ANDAs/BsLAs already on market
   -> Tentative approvals (approved but blocked by exclusivity)
```

**Step 4: Evaluate AG (authorized generic) strategy**

An authorized generic (AG) is a brand-company-licensed generic that can launch on the LOE date without Para IV certification. AG strategies include:
- Brand launches own AG to capture generic market share
- Brand licenses AG to a generic partner (revenue sharing)
- AG suppresses first-filer economics (reduces 180-day FTF value)

**Step 5: Model revenue impact**

Key LOE dynamics:
- Small molecules: 80-90% revenue erosion within 12 months of first generic entry
- Biologics: 20-40% erosion in first 2 years of biosimilar entry (slower due to interchangeability, payer dynamics)
- 180-day FTF exclusivity: First generic filer has 180-day market exclusivity (shared if multiple first filers)
- Limited competition: Fewer than 3 ANDA filers may retain higher pricing

---

### Workflow 6: Congress/Publication Monitoring

Track key medical congresses and publications for competitive data disclosures.

**Key congresses by therapeutic area:**

| Therapeutic Area | Major Congresses |
|-----------------|-----------------|
| Oncology | ASCO, AACR, ESMO, ASH, ASCO GU, ASCO GI, SNO, WCLC |
| Cardiology | AHA, ACC, ESC, HRS, TCT |
| Immunology/Rheumatology | ACR, EULAR, AAD |
| Neurology | AAN, AES, ECTRIMS, CTAD |
| Hepatology/GI | AASLD, EASL, DDW, UEG |
| Respiratory | ATS, ERS, CHEST |
| Endocrinology | ADA, EASD, ENDO |
| Hematology | ASH, EHA, ISTH |
| Nephrology | ASN, ERA-EDTA |
| Infectious Disease | IDWeek, ECCMID, CROI |

**Step 1: Pre-congress monitoring**

```
mcp__pubmed__pubmed_data(method: "search", query: "CONGRESS_NAME 2026 abstract DISEASE_NAME", num_results: 20)
   -> Abstracts published ahead of congress

mcp__biorxiv__biorxiv_data(method: "search", query: "COMPETITOR_DRUG DISEASE_NAME", limit: 10)
   -> Preprints posted pre-congress (common for late-breaking data)
```

**Step 2: Identify key presentations**

```
mcp__pubmed__pubmed_data(method: "search", query: "TRIAL_NAME results primary endpoint", num_results: 5)
   -> Published results from named trials (e.g., KEYNOTE-XXX, CHECKMATE-XXX)

mcp__clinicaltrials__ct_data(method: "get_study_results", nct_id: "NCTxxxxxxxx")
   -> ClinicalTrials.gov results posting (often within 12 months of completion)
```

**Step 3: Post-congress analysis**

```
mcp__pubmed__pubmed_data(method: "search", query: "COMPETITOR_DRUG phase 3 results 2026", num_results: 15)
   -> Full publications following congress presentations (typically 3-12 months lag)

mcp__fda__fda_data(method: "get_drug_label", drug_name: "COMPETITOR_DRUG")
   -> Check for label updates reflecting new data presented at congress
```

---

## Competitive Position Scoring

Quantitative scoring framework for assessing a drug program's competitive position relative to existing and pipeline competitors. Score range: 0-100.

### Score Components

| Component | Weight | Score Range | Assessment Criteria |
|-----------|--------|-------------|-------------------|
| **Efficacy differentiation** | 25% | 0-25 | Magnitude of clinical benefit vs SOC and competitors |
| **Safety differentiation** | 20% | 0-20 | Tolerability advantage, absence of class-effect toxicities |
| **Convenience/compliance** | 15% | 0-15 | Route, frequency, monitoring, storage, administration setting |
| **Time-to-market / regulatory** | 15% | 0-15 | Development speed, pathway advantages, regulatory interactions |
| **Patent/exclusivity protection** | 15% | 0-15 | Remaining exclusivity, patent estate strength, AG risk |
| **Pricing/access strategy** | 10% | 0-10 | HEOR positioning, reimbursement potential, competitive pricing |

### Scoring Rubric

**Efficacy Differentiation (0-25)**

| Score | Criteria |
|-------|----------|
| 21-25 | Statistically significant superiority on primary endpoint vs all competitors; potential best-in-class |
| 16-20 | Superiority vs SOC; comparable or numerically better than key competitors |
| 11-15 | Non-inferior to SOC; comparable to competitors; differentiated in subgroups |
| 6-10 | Non-inferior to SOC but no differentiation vs competitors |
| 0-5 | Inferior or insufficient data to demonstrate competitive efficacy |

**Safety Differentiation (0-20)**

| Score | Criteria |
|-------|----------|
| 17-20 | Significantly better safety/tolerability profile than all competitors; no boxed warnings |
| 13-16 | Safety advantage over most competitors; no unique safety signals |
| 9-12 | Comparable safety to competitors; manageable AE profile |
| 5-8 | Some safety concerns relative to competitors; REMS or boxed warning |
| 0-4 | Significant safety disadvantage; serious AEs limiting clinical use |

**Convenience/Compliance (0-15)**

| Score | Criteria |
|-------|----------|
| 13-15 | Oral QD, no food restrictions, no monitoring, home administration |
| 10-12 | Oral BID or weekly SC, minimal monitoring |
| 7-9 | Daily SC or biweekly IV, moderate monitoring |
| 4-6 | Weekly IV or frequent monitoring requirements |
| 0-3 | Hospital-based administration, intensive monitoring, complex preparation |

**Time-to-Market / Regulatory Pathway (0-15)**

| Score | Criteria |
|-------|----------|
| 13-15 | Filed or under review; breakthrough/accelerated/priority designation; PDUFA date set |
| 10-12 | Phase 3 complete; positive data; regulatory filing expected within 12 months |
| 7-9 | Phase 3 ongoing; positive Phase 2 data; clear regulatory path |
| 4-6 | Phase 2 ongoing; uncertain regulatory path; no special designations |
| 0-3 | Phase 1 or preclinical; high regulatory risk; complex endpoint requirements |

**Patent/Exclusivity Protection (0-15)**

| Score | Criteria |
|-------|----------|
| 13-15 | >10 years of exclusivity remaining; strong COM patent; no Para IV challenges |
| 10-12 | 5-10 years remaining; multiple patent layers; pediatric exclusivity granted |
| 7-9 | 3-5 years remaining; some patent challenges pending |
| 4-6 | 1-3 years remaining; active Para IV litigation; AG strategy deployed |
| 0-3 | <1 year to LOE; generics/biosimilars filed or approved |

**Pricing/Access Strategy (0-10)**

| Score | Criteria |
|-------|----------|
| 9-10 | Strong HEOR data; cost-effective vs SOC; broad payer coverage expected |
| 7-8 | Competitive pricing; adequate HEOR support; manageable access barriers |
| 5-6 | Premium pricing with moderate HEOR justification; some access restrictions |
| 3-4 | High price with limited HEOR differentiation; significant access barriers |
| 0-2 | Price not competitive; weak HEOR package; extensive prior authorization |

### Score Interpretation

| Total Score | Classification | Strategic Implication |
|-------------|---------------|---------------------|
| 80-100 | **Best-in-class** | Strong competitive position; defend and expand |
| 60-79 | **Competitive** | Viable position; differentiate on specific attributes |
| 40-59 | **Challenged** | Needs clear differentiation strategy or niche positioning |
| 20-39 | **Weak** | Consider strategic options (partnering, indication pivot, lifecycle management) |
| 0-19 | **Non-viable** | Fundamental competitive disadvantage; re-evaluate program |

---

## Analysis Templates

### Template 1: Competitive Landscape Matrix

```
# Competitive Landscape: [DISEASE AREA]
Generated: [DATE]

## Market Overview
- Total addressable market: $[X]B ([YEAR])
- Patient population: [N] patients ([geography])
- Current standard of care: [SOC description]
- Unmet needs: [key gaps]

## Approved Products

| Drug | Brand | Sponsor | MoA | Approval | Key Indication | LOE |
|------|-------|---------|-----|----------|---------------|-----|
| [generic] | [brand] | [company] | [mechanism] | [date] | [indication] | [date] |

## Pipeline (Phase 2+)

| Drug | Sponsor | MoA | Phase | Key Trial | Est. Data | Status |
|------|---------|-----|-------|-----------|-----------|--------|
| [name] | [company] | [mechanism] | [phase] | [NCT#] | [date] | [status] |

## Mechanism Class Analysis

| MoA Class | Approved | Pipeline | Differentiation Potential |
|-----------|----------|----------|--------------------------|
| [class 1] | [n] drugs | [n] programs | [assessment] |

## Competitive Position Scores

| Drug | Efficacy | Safety | Convenience | Regulatory | Patent | Pricing | TOTAL |
|------|----------|--------|-------------|------------|--------|---------|-------|
| [drug] | [/25] | [/20] | [/15] | [/15] | [/15] | [/10] | [/100] |
```

### Template 2: Pipeline Waterfall by Phase

```
# Pipeline Waterfall: [DISEASE AREA]
Generated: [DATE]

## Phase Distribution

PRECLINICAL  [|||||||||||] 11 programs
PHASE 1      [||||||||]    8 programs
PHASE 2      [||||||]      6 programs
PHASE 3      [||||]        4 programs
FILED/NDA    [||]          2 programs
APPROVED     [|||||||||]   9 products

## Phase 3 Detail (Near-Term Competitive Threats)

### [Drug Name] — [Sponsor]
- Mechanism: [MoA]
- Key Trial: [NCT#] ([trial name])
- Design: [randomized, double-blind, Phase 3 vs [comparator]]
- Primary Endpoint: [endpoint]
- Enrollment: [N actual] / [N target]
- Primary Completion: [date]
- Est. Filing: [date]
- PDUFA Date: [date, if filed]
- Competitive Position Score: [X/100]
- Key Differentiator: [what sets this apart]
- Key Risk: [main competitive vulnerability]

[Repeat for each Phase 3 program]

## Phase 2 Detail (Medium-Term Landscape Shifts)

[Similar format for Phase 2 programs with emphasis on data readout timing]
```

### Template 3: LOE Timeline Visualization

```
# LOE Timeline: [THERAPEUTIC AREA]
Generated: [DATE]

## Timeline (sorted by LOE date)

2024 |--[Drug A LOE]-------------------------------------------|
2025 |--------[Drug B LOE]------------------------------------|
2026 |----------------[Drug C LOE]----------------------------|
2027 |------------------------[Drug D LOE]--------------------|
2028 |--------------------------------[Drug E LOE]------------|
2029 |----------------------------------------[Drug F LOE]---|

## Detailed LOE Analysis

### [Drug Name] ([Brand]) — LOE: [DATE]
- Sponsor: [company]
- Peak sales: $[X]B ([year])
- Last patent: [patent #] expires [date] ([type: COM/formulation/MoU])
- Pediatric exclusivity: [Yes/No] (+6 months if yes)
- Orphan exclusivity: [Yes/No] (7 years from approval)
- Para IV filers: [n] ([company names])
- First-to-file: [company] (180-day FTF exclusivity)
- AG strategy: [deployed/not deployed/unknown]
- Biosimilar pipeline: [n programs, lead biosimilar name and sponsor]
- Est. generic/biosimilar entry: [date]
- Revenue impact: [% erosion estimate at 12/24 months]
```

### Template 4: SWOT Analysis for Drug Programs

```
# SWOT Analysis: [DRUG NAME] in [INDICATION]
Generated: [DATE]
Competitive Position Score: [X/100]

## STRENGTHS (Internal Advantages)
- [Efficacy differentiation: specific data points]
- [Safety advantage: specific comparisons]
- [Convenience: dosing, route, monitoring]
- [Regulatory: designations, pathway advantages]
- [Patent: strong IP position, exclusivity duration]
- [Commercial: established brand, physician familiarity]

## WEAKNESSES (Internal Disadvantages)
- [Efficacy gaps: specific limitations]
- [Safety concerns: boxed warnings, REMS, specific AEs]
- [Convenience barriers: route, frequency, monitoring]
- [Regulatory: incomplete regulatory submissions, delays]
- [Patent: approaching LOE, active litigation]
- [Commercial: limited market access, high price]

## OPPORTUNITIES (External Favorable Factors)
- [Indication expansion: new patient populations]
- [Combination therapy: synergistic combinations in development]
- [Competitor failures: recent competitor trial failures or safety issues]
- [Guideline updates: potential for improved positioning in treatment algorithms]
- [New formulations: lifecycle management opportunities]
- [Biomarker: companion diagnostic for patient selection]

## THREATS (External Unfavorable Factors)
- [Pipeline entrants: specific competitors and timelines]
- [Biosimilar/generic entry: LOE timing for the product or competitors]
- [Disruptive mechanisms: novel MoA classes that could leapfrog]
- [Regulatory risk: safety signals, labeling changes]
- [Payer dynamics: biosimilar-driven price erosion, reference pricing]
- [Clinical: competitor trial readouts expected at upcoming congresses]
```

---

## Evidence Grading for Competitive Intelligence

All competitive intelligence data must be graded by source quality. Apply the following tiers to every data point in CI deliverables.

| Tier | Label | Criteria | Typical Sources | CI Application |
|------|-------|----------|-----------------|----------------|
| **T1** | Regulatory / Definitive | Official regulatory filings, approved labels, published results from pivotal trials | FDA labels, EMA EPARs, Orange/Purple Book, ClinicalTrials.gov results | Approved indications, labeled efficacy/safety data, patent/exclusivity dates |
| **T2** | Clinical / Published | Peer-reviewed clinical trial results, published meta-analyses, regulatory meeting transcripts | PubMed RCTs, NMAs, ODAC transcripts, published Phase 2/3 results | Clinical benchmarking, head-to-head comparisons, treatment guidelines |
| **T3** | Conference / Emerging | Congress presentations, abstracts, preprints, interim analyses | ASCO/AHA/AACR abstracts, bioRxiv/medRxiv, interim data releases | Early competitive signals, pipeline data readouts, emerging efficacy/safety trends |
| **T4** | Analyst / Inferred | Press releases, analyst reports, investor presentations, pipeline databases, SEC filings | Company press releases, 10-K/10-Q filings, pipeline trackers | Timeline estimates, commercial forecasts, strategic intent, portfolio priorities |

### Evidence Grading Rules

1. **Always cite the tier** when presenting data: e.g., "ORR 45.2% (T1: FDA label)" or "Est. filing H2 2026 (T4: company press release)"
2. **Prioritize higher tiers**: When conflicting data exists across tiers, the higher tier takes precedence
3. **Flag T3/T4 uncertainty**: Data from conference presentations and press releases may change upon full publication; note this explicitly
4. **Date-stamp T3/T4 data**: Conference/analyst data has short shelf life; always record the source date
5. **Cross-validate**: Where possible, corroborate T3/T4 data with T1/T2 sources before making strategic recommendations

---

## FDA Regulatory Pathways Reference

Understanding approval pathways is essential for competitive timeline analysis and market entry prediction.

### NDA Pathways (Small Molecules)

| Pathway | Section | Description | CI Implication |
|---------|---------|-------------|----------------|
| **505(b)(1)** | Full NDA | Complete safety and efficacy data package | Longest timeline; strongest data package; NCE exclusivity eligible |
| **505(b)(2)** | Partial reliance | References existing approved drug data + bridging studies | Faster development; useful for reformulations, new salts, new indications; 3-year exclusivity for new clinical investigations |
| **ANDA** | Generic | Bioequivalence to reference listed drug (RLD) | Generic entry pathway; Para IV for patent challenge; 180-day FTF |

### Biologic Pathways

| Pathway | Description | CI Implication |
|---------|-------------|----------------|
| **BLA (351(a))** | Original biologic application | 12-year reference product exclusivity; 4-year data exclusivity |
| **BsLA (351(k))** | Biosimilar application | Cannot file until year 4; cannot approve until year 12; interchangeability designation for automatic substitution |

### Special Designations (Timeline Accelerators)

| Designation | Benefit | Typical Time Savings |
|------------|---------|---------------------|
| **Breakthrough Therapy** | Intensive FDA guidance, rolling review, organizational commitment | 1-3 years |
| **Accelerated Approval** | Approval on surrogate/intermediate endpoint | 2-4 years (but confirmatory trial required) |
| **Priority Review** | 6-month review vs standard 10-month | 4 months |
| **Fast Track** | Rolling review, more frequent FDA meetings | Variable (6-12 months) |
| **RTOR (Real-Time Oncology Review)** | Concurrent review of submitted portions | 1-3 months |
| **Orphan Drug** | 7-year market exclusivity, tax credits, fee waivers | Exclusivity protection (not speed) |

### PDUFA Date Intelligence

The Prescription Drug User Fee Act (PDUFA) target action date is the most reliable predictor of approval timing:
- Standard review: 10 months from filing acceptance (Day 0)
- Priority review: 6 months from filing acceptance
- FDA can issue a Complete Response Letter (CRL) instead of approval
- PDUFA dates are publicly tracked and provide competitive timeline intelligence
- 3-month extension possible if FDA requests additional information (Major Amendment)

---

## Competitive Benchmarking Methodologies

### Direct Comparison (Head-to-Head Trials)

The gold standard for competitive differentiation. Search for:
```
mcp__clinicaltrials__ct_data(method: "search_studies", query: "DRUG_A versus DRUG_B", limit: 10)
mcp__pubmed__pubmed_data(method: "search", query: "DRUG_A vs DRUG_B randomized controlled", num_results: 10)
```

### Indirect Comparison (Network Meta-Analysis)

When no head-to-head data exists, use published NMAs:
```
mcp__pubmed__pubmed_data(method: "search", query: "DISEASE network meta-analysis treatment comparison", num_results: 10)
```
NMA hierarchy: Bayesian NMA with SUCRA/P-score ranking > frequentist NMA > naive indirect comparison (Bucher method)

### Cross-Trial Comparison (Descriptive Only)

Compare results across separate trials. Always caveat:
- Different patient populations, endpoints, and comparators
- Immature vs mature data
- Different lines of therapy or disease severity
- Use only when no direct or indirect comparison available
- Evidence tier: T3 at best (hypothesis-generating)

### Real-World Evidence (RWE) Comparison

Post-marketing comparative effectiveness from registries, claims databases, EHR data:
```
mcp__pubmed__pubmed_data(method: "search", query: "DRUG_NAME real-world evidence comparative effectiveness", num_results: 10)
```
RWE provides T2-T3 evidence for competitive positioning in routine clinical practice.

---

## Multi-Agent Workflow Examples

**"Map the competitive landscape for NASH/MASH therapeutics"**
1. Competitive Intelligence (this skill) -> Full therapeutic area landscape with pipeline waterfall, LOE timeline, and competitive position scoring for all approved and Phase 2+ programs
2. Drug Research -> Individual drug monographs for the top 5 competitive threats
3. Clinical Pharmacology -> PK/PD comparison of oral vs injectable approaches, dose optimization considerations

**"Assess our drug's competitive position vs 3 competitors in HER2+ breast cancer"**
1. Competitive Intelligence (this skill) -> Differentiation assessment matrix, competitive position scores, SWOT analysis
2. Adverse Event Detection -> Comparative FAERS safety profiling across all 4 drugs
3. Drug Research -> Deep monograph on the client's drug for internal reference

**"Track upcoming LOE events in the autoimmune space for biosimilar opportunity assessment"**
1. Competitive Intelligence (this skill) -> LOE timeline for all major autoimmune biologics, biosimilar pipeline mapping, revenue impact modeling
2. Clinical Pharmacology -> Biosimilar PK similarity requirements, analytical similarity considerations

**"Monitor ASCO 2026 for competitive oncology data readouts"**
1. Competitive Intelligence (this skill) -> Pre-congress competitor trial inventory, expected data readouts, post-congress competitive impact assessment
2. Drug Research -> Rapid monographs on any newly disclosed compounds
3. Adverse Event Detection -> Safety signal assessment for competitor drugs with new safety data presented

**"Evaluate patent cliff impact on our cardiovascular portfolio"**
1. Competitive Intelligence (this skill) -> Patent/exclusivity analysis for portfolio products, AG strategy evaluation, generic entry timeline modeling
2. Drug Research -> Identify lifecycle management candidates (new formulations, indications, combinations)
3. Clinical Pharmacology -> 505(b)(2) feasibility assessment for reformulation strategies

## Completeness Checklist

- [ ] All approved products identified with sponsor, approval date, and key indication
- [ ] Clinical pipeline mapped by phase (Phase 1/2/3/filed) with NCT numbers
- [ ] Mechanisms of action clustered and landscape matrix populated
- [ ] Competitive position scores calculated for key products (efficacy, safety, convenience, regulatory, patent, pricing)
- [ ] Patent/exclusivity analysis includes LOE dates, Para IV challenges, and AG strategy
- [ ] Evidence grading applied to all data points (T1-T4 tiers with source citations)
- [ ] Congress/publication monitoring covers relevant upcoming data readouts
- [ ] Differentiation matrix includes head-to-head or indirect comparison data
- [ ] SWOT analysis completed for the focal drug program
- [ ] Report includes date stamps on all T3/T4 data for shelf-life tracking
