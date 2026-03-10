---
name: literature-deep-research
description: Systematic literature review engine supporting factoid verification and comprehensive deep-research reports. Collision-aware search strategies, evidence grading across 120+ data points, subject disambiguation, citation network expansion. Use when user mentions literature review, deep research, evidence review, factoid check, fact verification, literature search, evidence grading, collision-aware search, comprehensive review, research report, evidence synthesis, citation analysis, or literature evidence.
---

# Literature Deep Research

Systematic literature research engine with two operating modes: quick factoid verification (1-page answer with citations) and comprehensive deep-research reports (15-section structured report with 120+ data points). Uses collision-aware search strategies and 4-tier evidence grading across PubMed, bioRxiv, clinical trials, and compound/target databases.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_literature-deep-research_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- PRISMA-compliant systematic reviews with formal screening -> use `systematic-literature-reviewer`
- Drug target identification, SAR, and druggability assessment -> use `drug-target-analyst`
- Clinical trial pipeline analysis and endpoint data -> use `clinical-trial-analyst`
- Drug repurposing hypothesis generation -> use `drug-repurposing-analyst`
- Regulatory submission guidance and FDA requirements -> use `fda-consultant`
- Competitive landscape and market intelligence -> use `competitive-intelligence`

## Cross-Reference: Other Skills

- **PRISMA-compliant systematic reviews** -> use systematic-literature-reviewer skill
- **Drug target identification and SAR** -> use drug-target-analyst skill
- **Target-disease association evidence** -> use disease-research skill
- **Drug repurposing hypotheses** -> use drug-repurposing-analyst skill
- **Target validation and characterization** -> use target-research skill
- **Clinical trial pipeline data** -> use clinical-trial-analyst skill
- **Regulatory context for findings** -> use fda-consultant skill

## Available MCP Tools

### `mcp__pubmed__pubmed_articles` (PRIMARY - Literature Search)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search across PubMed | `keywords`, `num_results` |
| `search_advanced` | Filtered search with journal, date, author constraints | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details (abstract, authors, MeSH, journal) | `pmid` |

### `mcp__biorxiv__biorxiv_info` (Preprint Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_preprints` | Search bioRxiv/medRxiv preprints | `query`, `server`, `date_from`, `date_to`, `limit` |
| `get_preprint_details` | Full preprint metadata and abstract | `doi` |
| `get_categories` | Browse bioRxiv/medRxiv subject categories | `server` |
| `search_published_preprints` | Find preprints that became peer-reviewed publications | `query`, `server`, `limit` |

### `mcp__opentargets__opentargets_info` (Target/Disease Disambiguation)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Resolve gene symbols/protein names to Ensembl IDs | `query`, `size` |
| `search_diseases` | Resolve disease names to EFO IDs | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId`, `diseaseId`, `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target profile (function, pathways, tractability) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes) | `id` (EFO ID) |

### `mcp__chembl__chembl_info` (Compound/Drug Disambiguation)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |
| `get_admet` | ADMET/drug-likeness properties | `chembl_id` |

### `mcp__drugbank__drugbank_info` (Drug Profiling)

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

### `mcp__pubchem__pubchem_info` (Compound Profiling)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_by_name` | Find compound by name | `name`, `limit` |
| `get_compound_details` | Full compound profile | `cid` |
| `get_synonyms` | All known names and synonyms | `cid` |
| `get_properties` | Chemical/physical properties | `cid`, `properties` |
| `get_bioassay_summary` | Bioassay results summary | `cid`, `limit` |
| `get_bioassay_details` | Detailed bioassay data | `aid` |
| `get_compound_targets` | Known biological targets | `cid`, `limit` |
| `get_similar_compounds` | Structural similarity search | `cid` or `smiles`, `threshold`, `limit` |
| `get_patent_ids` | Patent literature for compound | `cid`, `limit` |
| `get_gene_interactions` | Gene-compound interactions | `cid`, `limit` |
| `get_pathway_info` | Pathway involvement | `cid` |
| `search_by_formula` | Search by molecular formula | `formula`, `limit` |

### `mcp__fda__fda_info` (Regulatory Context)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search FDA drug database | `query`, `limit` |
| `get_drug_label` | Full drug labeling/prescribing info | `application_number` or `drug_name` |
| `search_adverse_events` | FAERS adverse event reports | `query`, `limit` |
| `get_recall_info` | Drug recall information | `query`, `limit` |
| `search_clinical_trials` | FDA-reviewed trial data | `query`, `limit` |
| `get_approval_history` | Drug approval timeline | `drug_name` |
| `search_orange_book` | Patent/exclusivity data | `query`, `limit` |
| `get_ndcs` | National Drug Code lookup | `drug_name` |

### `mcp__ctgov__ctgov_info` (Clinical Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search registered clinical trials | `intervention`, `condition`, `status`, `phase` |
| `get` | Full trial record including results | `nct_id` |
| `get_results` | Trial results data | `nct_id` |
| `get_locations` | Trial site locations | `nct_id` |

---

## Two Operating Modes

### Mode Selection

```
User request analysis:
├── Quick factual question (yes/no, single data point, verification)
│   → FACTOID MODE (1-page answer, 5-15 citations)
│
└── Complex topic (mechanism, landscape, comparison, review)
    → DEEP-RESEARCH MODE (15-section report, 80-120+ citations)
```

**Ask the user which mode they want if ambiguous.** Default to factoid mode for questions that can be answered in a paragraph, deep-research mode for anything requiring synthesis across multiple evidence types.

---

## Phase 1: Clarification and Mode Selection

```
1. Parse the user's question:
   - Identify the subject(s): gene, protein, drug, disease, pathway, mechanism
   - Identify the question type: existence, mechanism, comparison, landscape, safety
   - Identify scope constraints: time range, species, study types

2. Select mode:
   - Factoid: "Does X inhibit Y?", "What is the IC50 of X for Y?", "Is X approved for Y?"
   - Deep-research: "What is known about X in Y?", "Review the evidence for X", "Compare X and Y"

3. Confirm with user:
   - Restate the interpreted question
   - State the selected mode
   - List planned data sources
   - Propose deliverable format
```

---

## Phase 2: Subject Disambiguation

### Why Disambiguation Matters

Many biomedical terms collide across domains. "ACE" could mean angiotensin-converting enzyme, ACE inhibitor drug class, or adverse clinical event. "BRAF" is unambiguous, but "Aurora" could be Aurora kinase A, B, or C, or the drug alisertib. Disambiguation before search prevents contaminated results.

### Disambiguation Workflow

```
1. Resolve biological targets:
   mcp__opentargets__opentargets_info(method: "search_targets", query: "SUBJECT_NAME", size: 10)
   → Check if multiple targets match; select correct Ensembl ID

2. Resolve diseases:
   mcp__opentargets__opentargets_info(method: "search_diseases", query: "DISEASE_NAME", size: 10)
   → Confirm EFO ID; check for parent/child disease terms

3. Resolve compounds/drugs:
   mcp__chembl__chembl_info(method: "compound_search", query: "COMPOUND_NAME", limit: 10)
   mcp__drugbank__drugbank_info(method: "search_by_name", query: "DRUG_NAME")
   mcp__pubchem__pubchem_info(method: "search_by_name", name: "COMPOUND_NAME", limit: 10)
   → Cross-reference ChEMBL ID, DrugBank ID, PubChem CID

4. Record canonical identifiers:
   - Gene symbol + Ensembl ID (e.g., EGFR / ENSG00000146648)
   - Disease name + EFO ID (e.g., non-small cell lung carcinoma / EFO_0003060)
   - Drug name + ChEMBL ID + DrugBank ID (e.g., erlotinib / CHEMBL553 / DB00530)
   - Synonyms list for search expansion
```

### Domain-Aware Routing

| Subject Type | Primary Resolution Tool | Secondary Tools |
|-------------|------------------------|-----------------|
| Gene/Protein target | OpenTargets `search_targets` | ChEMBL `target_search` |
| Disease/Condition | OpenTargets `search_diseases` | PubMed MeSH terms |
| Small molecule drug | ChEMBL `compound_search` | DrugBank, PubChem |
| Biologic drug | DrugBank `search_by_name` | ChEMBL `drug_search` |
| Pathway/Mechanism | DrugBank `get_pathways` | OpenTargets `get_target_details` |
| Clinical concept | PubMed MeSH lookup | ClinicalTrials.gov |

---

## Phase 3: Literature Search

### Seed Query Construction

```
1. Build primary search terms from disambiguated identifiers:
   - Use canonical gene symbol + common synonyms
   - Use drug generic name + brand names
   - Use MeSH terms where available

2. Construct initial PubMed search:
   mcp__pubmed__pubmed_articles(method: "search_advanced",
     term: "(CANONICAL_NAME OR SYNONYM_1 OR SYNONYM_2) AND (TOPIC_TERM_1 OR TOPIC_TERM_2)",
     start_date: "YYYY/01/01",
     num_results: 50)

3. Parallel preprint search:
   mcp__biorxiv__biorxiv_info(method: "search_preprints",
     query: "CANONICAL_NAME TOPIC",
     server: "biorxiv",
     date_from: "YYYY-01-01",
     limit: 30)

4. Check for published preprints:
   mcp__biorxiv__biorxiv_info(method: "search_published_preprints",
     query: "CANONICAL_NAME TOPIC",
     limit: 20)
```

### Citation Network Expansion

```
1. From seed results, identify:
   - Key review articles (cite many primary sources)
   - Seminal papers (highly cited, foundational)
   - Recent papers (may cite the above)

2. Extract PMIDs from references/citations mentioned in abstracts

3. Retrieve metadata for cited papers:
   mcp__pubmed__pubmed_articles(method: "get_article_metadata", pmid: "CITED_PMID")

4. Iterate 1-2 rounds of expansion to reach saturation
   (stop when new papers are already in the set)
```

### Collision-Aware Filtering

```
1. After initial search, scan results for off-topic contamination:
   - Count results that match the intended subject
   - Count results about a different entity with the same name

2. If >20% off-topic contamination detected:
   a. Identify the collision source (e.g., "ACE" returning ACE2 papers)
   b. Construct negative filters:
      mcp__pubmed__pubmed_articles(method: "search_advanced",
        term: "(ACE inhibitor) AND (hypertension) NOT (ACE2 OR coronavirus OR SARS)",
        num_results: 50)
   c. For bioRxiv (no NOT syntax), post-filter results by scanning abstracts

3. Document collision rate and filtering strategy in the report

4. Collision detection heuristics:
   - Gene symbols that are also common words (e.g., WAS, REST, IMPACT)
   - Drug names shared with unrelated products
   - Abbreviations with multiple expansions
   - Target family members (e.g., HDAC1 vs HDAC6)
```

---

## Phase 4: Evidence Synthesis and Grading

### 4-Tier Evidence Grading

| Tier | Label | Definition | Examples |
|------|-------|-----------|----------|
| **T1** | Mechanistic | Direct experimental proof of the claimed relationship | Knockout/knockin studies, crystallography showing binding, dose-response curves, CRISPR validation |
| **T2** | Functional | Validated associations with functional data | Cell-based assays, animal models, biomarker correlations, pathway perturbation experiments |
| **T3** | Association | Statistical or computational evidence | GWAS hits, network analysis predictions, expression correlations, text mining with statistical support |
| **T4** | Mention | Referenced but not directly studied | Review article mentions, database annotations without primary data, conference abstracts |

### Inline Citation Format

Every claim in the report must be tagged with its evidence tier:

```
EGFR mutations drive NSCLC proliferation through constitutive kinase activation [T1: Lynch et al., NEJM 2004, PMID:15118073].

Osimertinib shows superior PFS over gefitinib in first-line EGFR-mutant NSCLC [T1: Soria et al., NEJM 2018, PMID:29151359].

EGFR amplification may predict resistance to anti-EGFR antibodies [T3: Bardelli et al., J Clin Invest 2007, PMID:17557304].

EGFR has been mentioned as a potential biomarker for glioblastoma prognosis [T4: Brennan et al., Cell 2013, PMID:24120142].
```

### Evidence Tier Distribution Targets

| Report Section | Expected Tier Mix |
|---------------|------------------|
| Core mechanism | Primarily T1, some T2 |
| Therapeutic evidence | T1 (clinical trials), T2 (preclinical) |
| Biomarker evidence | Mix of T1-T3 |
| Emerging hypotheses | T3-T4 acceptable |
| Background context | T2-T4 acceptable |

---

## Factoid Mode Workflow

```
1. Disambiguate subject (Phase 2, abbreviated)

2. Targeted search (3-5 queries maximum):
   mcp__pubmed__pubmed_articles(method: "search_keywords",
     keywords: "SUBJECT specific_claim", num_results: 10)

3. Retrieve key article metadata:
   mcp__pubmed__pubmed_articles(method: "get_article_metadata", pmid: "TOP_PMID")

4. Cross-validate with structured databases:
   - Drug claim → mcp__drugbank__drugbank_info or mcp__fda__fda_info
   - Target claim → mcp__opentargets__opentargets_info
   - Compound claim → mcp__chembl__chembl_info or mcp__pubchem__pubchem_info
   - Clinical claim → mcp__ctgov__ctgov_info

5. Deliver 1-page answer:
   - Direct answer to the question (yes/no/nuanced)
   - Evidence tier for the answer
   - 5-15 supporting citations with PMIDs
   - Confidence assessment (high/moderate/low/insufficient)
   - Key caveats or contradictory evidence
```

---

## Deep-Research Mode: 15-Section Report Template

### Deliverable-First Approach

Create the report template BEFORE gathering data. This ensures systematic coverage and prevents scope drift.

### Report Sections

```
SECTION 1: Executive Summary
  - One-paragraph answer to the research question
  - Key findings (3-5 bullet points)
  - Evidence confidence level
  - Total citations: N (T1: n, T2: n, T3: n, T4: n)

SECTION 2: Research Question and Scope
  - Formalized question (PICO if applicable)
  - Inclusion/exclusion criteria
  - Date range and databases searched
  - Mode: deep-research

SECTION 3: Subject Disambiguation
  - Canonical identifiers resolved
  - Synonyms and aliases catalogued
  - Naming collisions detected and resolution strategy
  - Cross-database identifier mapping

SECTION 4: Search Strategy
  - Seed queries used (exact search strings)
  - Databases queried and result counts
  - Citation network expansion rounds
  - Collision filtering applied (if any)
  - Total unique articles screened

SECTION 5: Background and Context
  - Historical overview of the subject
  - Current state of knowledge
  - Key unanswered questions
  [T2-T4 citations acceptable]

SECTION 6: Molecular/Mechanistic Evidence
  - Direct experimental findings
  - Structural biology data
  - In vitro functional data
  [Primarily T1-T2 citations]

SECTION 7: Preclinical Evidence
  - Cell-based studies
  - Animal model data
  - Pharmacokinetic/pharmacodynamic data
  [Primarily T1-T2 citations]

SECTION 8: Clinical Evidence
  - Clinical trial results
  - Observational studies
  - Case reports/series
  [Primarily T1 citations]

SECTION 9: Regulatory Status
  - FDA approvals/indications
  - EMA and other agency decisions
  - Labeling changes
  - Orange Book patent/exclusivity data

SECTION 10: Safety and Adverse Effects
  - Known safety signals
  - FAERS data summary
  - Risk-benefit assessment
  [T1-T2 citations]

SECTION 11: Comparative Analysis
  - Head-to-head comparisons (if applicable)
  - Class effect analysis
  - Differentiation factors

SECTION 12: Biomarkers and Patient Selection
  - Predictive biomarkers
  - Companion diagnostics
  - Pharmacogenomics considerations
  [T1-T3 citations]

SECTION 13: Pipeline and Emerging Evidence
  - Active clinical trials
  - Preprint findings (not yet peer-reviewed)
  - Conference presentations
  [T2-T4 citations acceptable, clearly labeled]

SECTION 14: Knowledge Gaps and Research Opportunities
  - Unanswered questions identified during review
  - Conflicting evidence requiring resolution
  - Proposed next studies

SECTION 15: Complete Reference List
  - All citations organized by evidence tier
  - Format: Author et al., Journal Year, PMID/DOI
  - Tier tag for each reference
```

---

## Deep-Research Data Gathering Workflow

### Step 1: Create Template and Disambiguate

```
1. Create the 15-section template (deliverable-first)

2. Full disambiguation (Phase 2):
   mcp__opentargets__opentargets_info(method: "search_targets", query: "SUBJECT")
   mcp__chembl__chembl_info(method: "compound_search", query: "SUBJECT")
   mcp__drugbank__drugbank_info(method: "search_by_name", query: "SUBJECT")
   mcp__pubchem__pubchem_info(method: "search_by_name", name: "SUBJECT")
```

### Step 2: Broad Literature Search

```
1. PubMed primary search (reviews first):
   mcp__pubmed__pubmed_articles(method: "search_advanced",
     term: "(SUBJECT) AND (review[pt] OR systematic review[pt])",
     num_results: 20)

2. PubMed primary research:
   mcp__pubmed__pubmed_articles(method: "search_advanced",
     term: "(SUBJECT) AND (TOPIC_1 OR TOPIC_2)",
     start_date: "YYYY/01/01",
     num_results: 50)

3. PubMed mechanistic studies:
   mcp__pubmed__pubmed_articles(method: "search_keywords",
     keywords: "SUBJECT mechanism pathway signaling",
     num_results: 30)

4. Preprint search:
   mcp__biorxiv__biorxiv_info(method: "search_preprints",
     query: "SUBJECT TOPIC",
     server: "biorxiv",
     limit: 30)
   mcp__biorxiv__biorxiv_info(method: "search_preprints",
     query: "SUBJECT TOPIC",
     server: "medrxiv",
     limit: 30)

5. Apply collision-aware filtering (Phase 3)
```

### Step 3: Structured Database Queries

```
1. Drug/compound profiling:
   mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   mcp__chembl__chembl_info(method: "get_mechanism", chembl_id: "CHEMBLxxxxx")
   mcp__pubchem__pubchem_info(method: "get_compound_details", cid: "CID")
   mcp__pubchem__pubchem_info(method: "get_compound_targets", cid: "CID")

2. Target-disease evidence:
   mcp__opentargets__opentargets_info(method: "get_target_disease_associations",
     targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")

3. Regulatory context:
   mcp__fda__fda_info(method: "search_drugs", query: "DRUG_NAME")
   mcp__fda__fda_info(method: "get_approval_history", drug_name: "DRUG_NAME")
   mcp__fda__fda_info(method: "search_adverse_events", query: "DRUG_NAME")
   mcp__fda__fda_info(method: "search_orange_book", query: "DRUG_NAME")

4. Clinical trials:
   mcp__ctgov__ctgov_info(method: "search",
     intervention: "DRUG_NAME", condition: "DISEASE_NAME")
   mcp__ctgov__ctgov_info(method: "get_results", nct_id: "NCTxxxxxxxx")
```

### Step 4: Citation Network Expansion

```
1. From top 10 most relevant papers, extract cited PMIDs from abstracts
2. Retrieve metadata for each:
   mcp__pubmed__pubmed_articles(method: "get_article_metadata", pmid: "PMID")
3. Grade each new paper and assign to report sections
4. Repeat 1-2 times until citation saturation
```

### Step 5: Synthesize and Grade

```
1. Populate each report section with evidence
2. Assign evidence tier to every citation
3. Flag conflicting evidence and explain discrepancies
4. Calculate tier distribution and verify targets met
5. Write executive summary last (after all evidence gathered)
```

---

## Collision-Aware Search: Detailed Strategies

### Common Collision Patterns

| Pattern | Example | Strategy |
|---------|---------|----------|
| Gene symbol = common word | WAS, REST, IMPACT, MET | Add protein/gene context terms; use Ensembl ID in OpenTargets |
| Drug name collision | Keytruda vs key + truda | Use generic name (pembrolizumab) for literature |
| Family member confusion | HDAC1 vs HDAC (general) | Specify isoform; exclude other family members |
| Abbreviation overload | ACE (enzyme vs inhibitor class) | Expand abbreviation in search |
| Disease name overlap | ALS (amyotrophic lateral sclerosis vs antiphospholipid syndrome) | Use full disease name; add MeSH qualifier |
| Organism confusion | Mouse vs human studies | Add species filter; use [MeSH] organism terms |

### Negative Filter Construction

```
When contamination rate >20%:

1. Identify contaminating terms from off-topic results
2. Build exclusion list:
   NOT (CONTAMINANT_1 OR CONTAMINANT_2 OR CONTAMINANT_3)

3. PubMed example:
   mcp__pubmed__pubmed_articles(method: "search_advanced",
     term: "(MET[tiab] AND receptor AND cancer) NOT (metformin OR metabolic OR methionine)",
     num_results: 50)

4. For databases without NOT syntax:
   - Retrieve broader result set
   - Post-filter by scanning titles/abstracts for contaminating terms
   - Document exclusion count
```

---

## Quality Checks Before Delivery

```
Pre-delivery checklist:
[ ] Every claim has an inline evidence tier citation
[ ] All PMIDs are real (retrieved via get_article_metadata)
[ ] Collision filtering documented if applied
[ ] Evidence tier distribution matches section expectations
[ ] Conflicting evidence explicitly addressed
[ ] Factoid mode: answer is direct and unambiguous
[ ] Deep-research mode: all 15 sections populated
[ ] Executive summary written last, reflects actual findings
[ ] Reference list is complete and deduplicated
[ ] Confidence assessment provided
```

---

## Multi-Agent Workflow Examples

**"Is PCSK9 a valid target for Alzheimer's disease?"**
1. Literature Deep Research (factoid mode) -> Disambiguation, targeted PubMed search, evidence grading, 1-page answer with tier-tagged citations
2. Drug Target Analyst -> PCSK9 druggability, existing inhibitors, bioactivity data
3. Disease Research -> Alzheimer's disease target landscape for context

**"Comprehensive review of CDK4/6 inhibitors in breast cancer"**
1. Literature Deep Research (deep-research mode) -> 15-section report: disambiguation, collision-aware search (CDK4 vs CDK6 vs CDK4/6), citation network expansion, evidence synthesis across 120+ data points
2. Clinical Trial Analyst -> Active Phase 2/3 trials, pipeline analysis
3. Pharmacovigilance Specialist -> Class-wide safety signals, neutropenia rates
4. FDA Consultant -> Approval history, labeling differences across palbociclib/ribociclib/abemaciclib

**"Fact-check: Does metformin reduce cancer risk?"**
1. Literature Deep Research (factoid mode) -> Collision-aware search (metformin cancer, excluding diabetes-only papers), meta-analysis identification, evidence tier assessment
2. Drug Repurposing Analyst -> Mechanistic rationale for metformin in oncology
3. Clinical Trial Analyst -> Active metformin-cancer trials

**"Review emerging evidence for GLP-1 agonists in neurodegeneration"**
1. Literature Deep Research (deep-research mode) -> Full 15-section report with preprint coverage, collision filtering (GLP-1 diabetes vs neuro), evidence grading emphasizing T3-T4 for emerging area
2. Drug Target Analyst -> GLP-1R expression in CNS, pathway analysis
3. Systematic Literature Reviewer -> PRISMA-quality subset for any meta-analyzable endpoints

## Completeness Checklist

- [ ] Subject disambiguation completed with canonical identifiers (Ensembl ID, EFO ID, ChEMBL ID)
- [ ] Collision-aware filtering applied and contamination rate documented
- [ ] Citation network expanded at least 1-2 rounds beyond seed results
- [ ] Every claim tagged with evidence tier (T1-T4) and PMID
- [ ] All PMIDs verified via `get_article_metadata` (no fabricated citations)
- [ ] Conflicting evidence explicitly addressed with explanation
- [ ] Evidence tier distribution matches section expectations
- [ ] Executive summary written last, reflecting actual findings
- [ ] Reference list complete, deduplicated, and organized by tier
- [ ] Confidence assessment (high/moderate/low/insufficient) provided
