---
name: research-synthesis
description: Systematic large-scale literature synthesis that builds structured knowledge models from many papers. Not a simple literature search -- implements a 6-phase process (scope definition, systematic search, evidence extraction, knowledge model construction, evidence triangulation, synthesis and gap analysis) inspired by large-scale synthesis frameworks. Full traceability from every conclusion back to source papers with evidence strength grading. Use when asked to synthesize a body of literature, build a knowledge model from many papers, triangulate evidence across study types, identify knowledge gaps and consensus findings, perform comprehensive evidence mapping, or create a structured understanding of what a field knows and doesn't know.
---

# Research Synthesis

Systematic large-scale literature synthesis that builds structured knowledge models from many papers. Not a simple literature search or single-study review -- this skill implements a 6-phase synthesis process inspired by large-scale synthesis frameworks (such as Kosmos's 1500-paper synthesis with structured world models). Every conclusion is traceable back to source papers with evidence strength grading. Produces structured reports that map consensus, contested findings, knowledge gaps, translation gaps, and emerging trends.

Distinct from **literature-deep-research** (which iteratively investigates a focused question), **systematic-literature-reviewer** (which follows PRISMA protocol for formal systematic reviews), **scientific-critical-thinking** (which evaluates individual study quality), and **peer-review** (which evaluates manuscripts for journal submission). This skill operates at the knowledge architecture level -- building a structured model of what an entire field knows and doesn't know.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_research_synthesis_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Quick factoid check or focused literature question -> use `literature-deep-research`
- PRISMA-compliant systematic review with formal screening -> use `systematic-literature-reviewer`
- Evaluating the quality of a single study -> use `scientific-critical-thinking`
- Reviewing a manuscript for journal submission -> use `peer-review`
- Generating competing hypotheses for a phenomenon -> use `hypothesis-generation`
- Pharma-specific target research and validation -> use `target-research`
- Auditing the reasoning process of an existing analysis -> use `meta-cognition`
- Drug-disease-target landscape analysis -> use `drug-target-analyst`

## Cross-Skill Routing

- **Focused literature investigation** -> use literature-deep-research skill
- **Formal PRISMA systematic review** -> use systematic-literature-reviewer skill
- **Individual study quality assessment** -> use scientific-critical-thinking skill
- **Manuscript review** -> use peer-review skill
- **Hypothesis generation from synthesis** -> use hypothesis-generation skill
- **Target validation and druggability** -> use target-research skill
- **Reasoning quality audit** -> use meta-cognition skill
- **Statistical methodology assessment** -> use statistical-modeling skill
- **Disease mechanism overview** -> use disease-research skill

---

## Available MCP Tools

### `mcp__pubmed__pubmed_data` (PRIMARY - Literature Search & Retrieval)

| Method | Synthesis use | Key parameters |
|--------|--------------|----------------|
| `search` | Systematic literature retrieval across PubMed | `query`, `num_results` |
| `fetch_details` | Extract structured data from individual papers | `pmid` |

**Synthesis-specific search strategies:**
```
Phase 1 — Broad scoping search:
  mcp__pubmed__pubmed_data(method: "search",
    query: "[phenomenon] AND (review[pt] OR systematic review[pt])",
    num_results: 30)
  -> Identify existing reviews to understand the landscape

Phase 2 — Targeted evidence retrieval:
  mcp__pubmed__pubmed_data(method: "search",
    query: "[phenomenon] AND [mechanism/pathway] AND [study type]",
    num_results: 50)
  -> Retrieve primary studies within each theme

Phase 3 — Temporal trend analysis:
  mcp__pubmed__pubmed_data(method: "search",
    query: "[phenomenon] AND [specific aspect]",
    num_results: 20)
  -> Search with date ranges to track how the field's view has evolved

Phase 4 — Contradictory evidence search:
  mcp__pubmed__pubmed_data(method: "search",
    query: "[phenomenon] AND (negative results OR no effect OR contradictory OR failed)",
    num_results: 20)
  -> Actively seek disconfirming evidence to avoid confirmation bias

Phase 5 — Cross-domain search:
  mcp__pubmed__pubmed_data(method: "search",
    query: "[phenomenon] AND [adjacent field/application]",
    num_results: 20)
  -> Find translation gaps and cross-domain evidence
```

### `mcp__biorxiv__biorxiv_data` (Preprints & Emerging Research)

| Method | Synthesis use | Key parameters |
|--------|--------------|----------------|
| `search_preprints` | Find recent unpublished work | `query`, `server`, `limit` |
| `get_preprint_details` | Get full preprint metadata and abstract | `doi` |
| `get_recent_preprints` | Latest preprints for emerging trend detection | `topic`, `days`, `limit` |

**Synthesis-specific uses:**
```
Emerging trend detection:
  mcp__biorxiv__biorxiv_data(method: "get_recent_preprints",
    topic: "[synthesis topic]",
    days: 180,
    limit: 30)
  -> Identify recent shifts in the field not yet captured in reviews

Cross-server search (bioRxiv + medRxiv):
  mcp__biorxiv__biorxiv_data(method: "search_preprints",
    query: "[synthesis question]",
    server: "biorxiv",
    limit: 20)
  mcp__biorxiv__biorxiv_data(method: "search_preprints",
    query: "[synthesis question]",
    server: "medrxiv",
    limit: 20)
  -> Cover both basic science and clinical preprints
```

### `mcp__opentargets__opentargets_data` (Target-Disease Evidence)

| Method | Synthesis use | Key parameters |
|--------|--------------|----------------|
| `get_target_disease_associations` | Evidence-scored associations for triangulation | `targetId`, `diseaseId`, `minScore` |
| `get_disease_targets_summary` | All known targets for a disease | `diseaseId`, `size` |
| `get_target_details` | Comprehensive target information | `id` |
| `get_disease_details` | Disease ontology and known associations | `id` |

**Synthesis-specific uses:**
```
Evidence triangulation across data types:
  mcp__opentargets__opentargets_data(method: "get_target_disease_associations",
    targetId: "[ENSG ID]",
    diseaseId: "[EFO ID]",
    minScore: 0.1)
  -> Open Targets integrates genetic, somatic, literature, drug, animal model,
     and pathway evidence — ideal for triangulation across evidence types
```

### `mcp__chembl__chembl_data` (Bioactivity & Drug Evidence)

| Method | Synthesis use | Key parameters |
|--------|--------------|----------------|
| `compound_search` | Find compounds studied against synthesis targets | `query`, `limit` |
| `get_bioactivity` | Bioactivity data for evidence extraction | `chembl_id`, `target_id` |
| `drug_search` | Find approved drugs and clinical candidates | `query`, `limit` |

### `mcp__reactome__reactome_data` (Pathway Context)

| Method | Synthesis use | Key parameters |
|--------|--------------|----------------|
| `search_pathways` | Identify relevant pathways for knowledge model | `query`, `limit` |
| `get_pathway_participants` | Map genes/proteins within pathways | `pathway_id` |
| `analyze_gene_list` | Pathway enrichment across synthesis gene set | `genes`, `limit` |

### `mcp__kegg__kegg_data` (Metabolic & Disease Pathways)

| Method | Synthesis use | Key parameters |
|--------|--------------|----------------|
| `search_pathways` | Cross-reference pathway involvement | `query` |
| `get_pathway_genes` | Complete gene sets for pathway-level synthesis | `pathway_id` |
| `get_disease_info` | Disease pathway and gene associations | `disease_id` |

### `mcp__ctgov__ctgov_data` (Clinical Trial Evidence)

| Method | Synthesis use | Key parameters |
|--------|--------------|----------------|
| `search` | Find clinical trials relevant to synthesis question | `intervention`, `condition` |
| `get` | Detailed trial information for evidence extraction | `nct_id` |

**Synthesis-specific uses:**
```
Clinical evidence mapping:
  mcp__ctgov__ctgov_data(method: "search",
    intervention: "[intervention from synthesis]",
    condition: "[condition from synthesis]")
  -> Map the clinical trial landscape for evidence triangulation
  -> Compare registered endpoints with published results
```

### `mcp__openalex__openalex_data` (Large-Scale Literature & Citation Analysis)

| Method | Synthesis use | Key parameters |
|--------|--------------|----------------|
| `search_works` | Large-scale literature retrieval with citation counts for evidence weighting | `query` |
| `get_work` | Get full work metadata by OpenAlex ID, DOI, or PMID | `id` |
| `search_authors` | Identify leading researchers in the synthesis topic | `query` |
| `get_author` | Author citation metrics and publication trends by year | `id` |
| `search_topics` | Map research topic landscape with field/domain classification | `query` |
| `get_cited_by` | Citation network analysis — find papers citing key works | `workId` |
| `get_works_by_author` | Author's works sorted by citation count for identifying seminal papers | `authorId` |
| `get_works_by_institution` | Institution publication trends for temporal analysis | `institutionId` |
| `search_institutions` | Identify leading research institutions in the synthesis area | `query` |

**Synthesis-specific uses:**
```
Publication trend analysis:
  mcp__openalex__openalex_data(method: "search_topics",
    query: "[synthesis topic]")
  -> Map the research landscape with works counts and citation metrics
  -> Identify subfields and domain classification for theme identification

Citation network for snowball searching:
  mcp__openalex__openalex_data(method: "get_cited_by",
    workId: "[OpenAlex work ID of seminal paper]")
  -> Forward citation chaining to find papers building on key findings
  -> Complements backward reference chaining from PubMed
```

---

## Core Methodology: 6-Phase Synthesis Process

### Phase 1: Scope Definition

Define the synthesis question precisely before searching. The quality of the synthesis depends entirely on the quality of the question.

#### Framework Selection

| Question Type | Framework | Components |
|--------------|-----------|------------|
| **Clinical** | PICO | Population, Intervention, Comparison, Outcome |
| **Prognostic** | PECO | Population, Exposure, Comparison, Outcome |
| **Basic research** | PPC | Population/System, Phenomenon, Context |
| **Mechanistic** | MPCO | Mechanism, Pathway, Context, Outcome |
| **Diagnostic** | PIRD | Population, Index test, Reference standard, Diagnosis |

#### PICO Framework (Clinical Questions)

```
P (Population): Who? (species, disease state, demographics, comorbidities)
I (Intervention): What? (drug, procedure, behavioral change, exposure)
C (Comparison): Compared to what? (placebo, standard of care, no treatment)
O (Outcome): Measuring what? (survival, response rate, biomarker change, adverse events)

Example:
  P: Adult patients with treatment-resistant depression
  I: Psilocybin-assisted therapy
  C: Placebo, SSRIs, other psychedelic therapies
  O: Depression severity (PHQ-9, MADRS), remission rate, adverse events, durability
```

#### PPC Framework (Basic Research Questions)

```
P (Population/System): What biological system? (cell type, organism, pathway)
Ph (Phenomenon): What is happening? (mechanism, process, interaction)
C (Context): Under what conditions? (disease state, developmental stage, environmental)

Example:
  P: Tumor microenvironment in solid tumors
  Ph: Mechanisms of T-cell exhaustion
  C: Checkpoint inhibitor resistance
```

#### Inclusion and Exclusion Criteria

Define explicitly before searching. These prevent scope creep and ensure reproducibility.

```
Inclusion criteria:
  - Study types: [RCTs, observational, in vitro, in vivo, reviews, etc.]
  - Date range: [e.g., 2015-present, or all time for foundational work]
  - Languages: [English, or specify others]
  - Populations: [As defined in PICO/PPC]
  - Minimum quality: [e.g., peer-reviewed only, or include preprints]

Exclusion criteria:
  - Study types to exclude: [case reports, editorials, opinion pieces, etc.]
  - Irrelevant populations: [e.g., pediatric if studying adult disease]
  - Irrelevant interventions: [e.g., surgical if studying pharmacological]
  - Non-relevant endpoints: [specify]
```

#### Search Strategy Documentation

```
Databases to search:
  1. PubMed (via mcp__pubmed__pubmed_data)
  2. bioRxiv/medRxiv (via mcp__biorxiv__biorxiv_data)
  3. ClinicalTrials.gov (via mcp__ctgov__ctgov_data)
  4. Open Targets (via mcp__opentargets__opentargets_data)
  5. ChEMBL (via mcp__chembl__chembl_data)

Search terms:
  Primary: [main concept terms]
  Secondary: [related terms, synonyms, MeSH terms]
  Boolean strategy: [how terms are combined]

Date of search: [record for reproducibility]
```

---

### Phase 2: Systematic Search

Execute the search strategy comprehensively. Document everything for reproducibility.

#### Search Execution Protocol

```
Step 1: Scoping reviews and meta-analyses
  mcp__pubmed__pubmed_data(method: "search",
    query: "[synthesis topic] AND (systematic review[pt] OR meta-analysis[pt])",
    num_results: 30)
  -> Understand what syntheses already exist
  -> Identify gaps in existing reviews
  -> Extract references from existing reviews for snowball searching

Step 2: Primary research by theme
  For each theme/sub-question identified in scoping:
  mcp__pubmed__pubmed_data(method: "search",
    query: "[theme-specific terms]",
    num_results: 50)
  -> Cast a wide net initially, then screen

Step 3: Preprint search for emerging evidence
  mcp__biorxiv__biorxiv_data(method: "search_preprints",
    query: "[synthesis question]",
    limit: 30)
  -> Capture recent work not yet in PubMed

Step 4: Clinical trial evidence
  mcp__ctgov__ctgov_data(method: "search",
    intervention: "[relevant intervention]",
    condition: "[relevant condition]")
  -> Map clinical evidence landscape

Step 5: Contradictory evidence (CRITICAL — do not skip)
  mcp__pubmed__pubmed_data(method: "search",
    query: "[synthesis topic] AND (negative OR contradictory OR no effect OR failed OR null)",
    num_results: 20)
  -> Actively seek disconfirming evidence
```

#### Screening and Documentation

Screen each result: Does it address the question? Meet inclusion criteria? Within scope? Keep (yes to all), flag for full-text review (maybe), or exclude with reason. Use `fetch_details` for full-text review of borderline papers. Document results counts per database at each screening stage.

---

### Phase 3: Evidence Extraction

Extract structured data from each included source. This is the raw material for the knowledge model.

#### Evidence Extraction Template

For each included paper, extract:

```
Paper ID: [PMID or DOI]
Authors: [First author et al.]
Year: [Publication year]
Journal: [Journal name]
Study Design: [RCT, cohort, case-control, in vitro, in vivo, computational, review]
Population/System: [What was studied]
Sample Size: [N]
Key Finding(s): [1-3 sentence summary of main results]
Effect Size: [Quantitative result with CI if available]
Statistical Significance: [p-value, CI]
Quality Indicators:
  - Study design level: [1-5, see Evidence Strength Grading]
  - Risk of bias: [Low/Medium/High]
  - Sample size adequacy: [Adequate/Borderline/Inadequate]
  - Reproducibility: [Replicated/Single study/Awaiting replication]
Limitations: [Key limitations noted by authors or identified by reviewer]
Relevance to Synthesis: [Which theme(s) does this inform?]
Agreement with Other Evidence: [Consistent/Mixed/Contradictory]
```

#### Evidence Extraction Table

| Paper | Year | Design | N | Key Finding | Effect Size | Quality (1-5) | Theme |
|-------|------|--------|---|-------------|-------------|---------------|-------|
| [Author et al.] | [Year] | [Design] | [N] | [Finding] | [Effect] | [Score] | [Theme] |

---

### Phase 4: Knowledge Model Construction

This is the core differentiator of research synthesis. Not just a list of papers -- a structured representation of what the field knows, organized by themes, with evidence strength tracked at every node.

#### Knowledge Model Architecture

```
Synthesis Question
|
+-- Theme 1: [Name]
|   |-- Consensus Findings (multiple sources agree)
|   |   |-- Finding 1.1 [Source A (L2), Source B (L3), Source C (L2)]
|   |   +-- Finding 1.2 [Source D (L1), Source E (L2)]
|   |-- Contested Findings (sources disagree)
|   |   |-- Finding 1.3: Source F says X, Source G says Y
|   |   +-- Possible explanations for disagreement
|   |-- Evidence Gaps (questions with no or insufficient evidence)
|   |   +-- Gap 1.1: No studies have examined [specific aspect]
|   +-- Evidence Strength: [Strong/Moderate/Weak]
|
+-- Theme 2: [Name]
|   |-- Consensus Findings
|   |-- Contested Findings
|   |-- Evidence Gaps
|   +-- Evidence Strength: [Strong/Moderate/Weak]
|
+-- Cross-Theme Connections
|   |-- Theme 1 Finding X supports Theme 2 Finding Y
|   |-- Theme 3 contradicts Theme 1 on [specific point]
|   +-- Emergent pattern across themes: [description]
|
+-- Temporal Trends
    |-- Pre-2015 view: [description]
    |-- 2015-2020 shift: [description]
    +-- 2020-present: [description]
```

#### Theme Identification Process

```
1. Read all extracted evidence (Phase 3 output)
2. Identify recurring topics, mechanisms, or questions
3. Group papers by theme
4. For each theme:
   a. What do most papers agree on? (consensus)
   b. Where do papers disagree? (contested)
   c. What questions remain unanswered? (gaps)
   d. How strong is the overall evidence? (strength)
5. Identify connections between themes
6. Track how the field's view has changed over time
```

#### Evidence Strength Assessment Per Theme

| Evidence Profile | Strength Rating | Description |
|-----------------|----------------|-------------|
| Multiple Level 1-2 studies, consistent results | **Strong** | High confidence, unlikely to change with new data |
| Mix of Level 2-3 studies, mostly consistent | **Moderate** | Reasonable confidence, could shift with large new studies |
| Few studies, mixed results, or only Level 4-5 | **Weak** | Low confidence, significant uncertainty remains |
| Single study or only expert opinion | **Very Weak** | Preliminary, requires substantial additional evidence |
| No evidence found | **Gap** | Question has not been adequately addressed |

---

### Phase 5: Evidence Triangulation

Cross-validate findings across different types of evidence. Agreement across evidence types dramatically increases confidence. Disagreement across evidence types reveals the most interesting and important questions.

#### Triangulation Matrix

| Finding | Genetic Evidence | Clinical Evidence | In Vitro | In Vivo (Animal) | Epidemiological | Computational |
|---------|-----------------|-------------------|----------|-------------------|-----------------|---------------|
| [Finding 1] | Supports/Contradicts/No data | ... | ... | ... | ... | ... |
| [Finding 2] | ... | ... | ... | ... | ... | ... |

#### Triangulation Rules

| Pattern | Interpretation | Confidence Impact |
|---------|---------------|-------------------|
| All evidence types agree | Strong convergent evidence | High confidence |
| Most agree, one contradicts | Likely real with important caveat | Moderate-high, investigate the contradiction |
| Evidence types split | Genuinely contested, more research needed | Low-moderate confidence |
| Only one evidence type available | Cannot triangulate | Confidence limited by single evidence type |
| Evidence types agree but all from same group | Potential replication dependency | Moderate, seek independent replication |

#### Cross-Evidence Type Questions

```
For each key finding, systematically ask:

1. GENETIC: Does genetic evidence support this?
   mcp__opentargets__opentargets_data(method: "get_target_disease_associations",
     targetId: "[ENSG ID]", diseaseId: "[EFO ID]")
   -> Check genetic association score

2. CLINICAL: Do clinical trials support this?
   mcp__ctgov__ctgov_data(method: "search",
     intervention: "[intervention]", condition: "[condition]")
   -> Check clinical trial results

3. PHARMACOLOGICAL: Do drug studies support this?
   mcp__chembl__chembl_data(method: "get_bioactivity",
     target_id: "[ChEMBL target ID]")
   -> Check bioactivity data

4. PATHWAY: Is this consistent with known pathway biology?
   mcp__reactome__reactome_data(method: "search_pathways",
     query: "[mechanism/pathway]")
   -> Check pathway context

5. EPIDEMIOLOGICAL: Do population studies support this?
   mcp__pubmed__pubmed_data(method: "search",
     query: "[phenomenon] AND (epidemiology OR cohort OR population-based)",
     num_results: 20)

6. CROSS-SPECIES: Does animal evidence support this?
   mcp__pubmed__pubmed_data(method: "search",
     query: "[phenomenon] AND (mouse model OR animal model OR in vivo)",
     num_results: 20)
```

#### Triangulation Discrepancy Analysis

When evidence types disagree, analyze why:

| Discrepancy Type | Possible Explanations | Resolution Strategy |
|-----------------|----------------------|-------------------|
| In vitro positive, in vivo negative | Bioavailability, microenvironment, systemic effects | PK/PD studies, more physiological in vitro models |
| Animal positive, human negative | Species difference, dose translation, disease model fidelity | Check for translational studies, species-specific mechanisms |
| Genetic positive, clinical negative | Genetic effect too small, wrong therapeutic approach, modifier genes | Larger clinical studies, pharmacogenomic stratification |
| Epidemiological positive, RCT negative | Confounding in observational data, or RCT population too narrow | Mendelian randomization, broader RCT inclusion |
| Computational positive, experimental negative | Model assumptions wrong, parameter estimation error | Model validation, sensitivity analysis |

---

### Phase 6: Synthesis and Gap Analysis

Integrate all evidence into a coherent picture of what the field knows, thinks, and doesn't know.

#### Synthesis Categories

**What We Know (High Confidence)**
- Findings supported by multiple evidence types
- Consistent across studies and research groups
- Level 1-2 evidence with strong triangulation
- Replicated independently

**What We Think (Moderate Confidence)**
- Findings supported by some evidence types but not all
- Generally consistent but with notable exceptions
- Level 2-3 evidence with partial triangulation
- Limited independent replication

**What We Don't Know (Evidence Gaps)**
- Questions with no or insufficient evidence
- Areas where existing studies are underpowered
- Populations or contexts not yet studied
- Mechanisms not yet elucidated

**Translation Gaps**
- Knowledge established in one field but not applied in another
- Basic science findings not yet tested clinically
- Clinical observations not yet explained mechanistically
- Cross-disease insights not yet transferred

**Emerging Trends**
- Recent shift in the field's understanding
- New evidence challenging established views
- Novel methodologies opening new questions
- Preprints suggesting upcoming paradigm changes

---

## Evidence Strength Grading

### Grading Hierarchy

| Level | Evidence Type | Description | Weight in Synthesis |
|-------|-------------|-------------|-------------------|
| **Level 1** | Systematic reviews / meta-analyses of RCTs | Gold standard; pooled estimates from multiple RCTs | Highest |
| **Level 2** | Individual RCTs | Controlled, randomized; single study | High |
| **Level 3** | Controlled observational studies | Cohort, case-control with appropriate controls | Moderate |
| **Level 4** | Case series, case reports | Uncontrolled observations, small N | Low |
| **Level 5** | Expert opinion, mechanism-based reasoning | No empirical data; theoretical or authority-based | Lowest |

### Quality Modifiers

Apply modifiers on top of evidence level: **Increase** confidence for large sample size, multi-center design, pre-registration, and independent replication. **Decrease** confidence for high risk of bias, small sample size, single research group, or potential conflicts of interest.

---

## Traceability Requirement (Kosmos-Inspired)

Every conclusion in the synthesis MUST be traceable to its source evidence. No unsupported claims. This is the fundamental principle that distinguishes a synthesis from an opinion.

### Traceability Format

```
Finding: [Clear statement of what the evidence shows]
Evidence:
  - Paper A (Author et al., Year) — Level 2, N=200: [specific result]
  - Paper B (Author et al., Year) — Level 3, N=500: [specific result]
  - Paper C (Author et al., Year) — Level 2, N=150: [specific result]
Strength: Strong / Moderate / Weak
Agreement: Consistent / Mixed / Contradictory
Confidence: High / Moderate / Low
Notes: [Any important caveats or qualifiers]
```

### Traceability Rules

1. **Every factual claim** in the synthesis must cite at least one source
2. **Strength ratings** must reflect the evidence level and quality of cited sources
3. **Agreement ratings** must reflect the consistency across cited sources
4. **Confidence ratings** integrate strength, agreement, and triangulation
5. **No claim** should be made that exceeds what the cited evidence supports
6. **Contradictory evidence** must be cited alongside supporting evidence
7. **Evidence gaps** must be explicitly stated, not silently passed over

---

## Full Report Structure

```
# Research Synthesis: [Question]

## Executive Summary
[3-5 sentences: question, approach, key findings, main gaps, significance]

## 1. Scope & Methods

### 1.1 Research Question
[PICO/PPC framework applied]

### 1.2 Search Strategy
[Databases, search terms, Boolean strategy]

### 1.3 Inclusion/Exclusion Criteria
[Explicit criteria with rationale]

### 1.4 Databases Searched
| Database | Query | Date | Results |
|----------|-------|------|---------|

## 2. Search Results

### 2.1 Flow Summary
- Total papers identified: [N]
- After title/abstract screening: [N]
- After full-text review: [N]
- Included in final synthesis: [N]
- Exclusion reasons: [breakdown]

### 2.2 Evidence Landscape
[Brief characterization: study types, date range, geographic coverage, evidence levels]

## 3. Evidence Table

| Paper | Year | Design | N | Key Finding | Effect Size | Quality (1-5) | Theme |
|-------|------|--------|---|-------------|-------------|---------------|-------|

## 4. Knowledge Model

### Theme 1: [Name]

#### Consensus Findings
[Traceable findings with source citations and evidence strength]

#### Contested Findings
[Areas of disagreement with sources on each side]

#### Evidence Gaps
[Unanswered questions within this theme]

#### Theme Evidence Strength: [Strong/Moderate/Weak]

### Theme 2: [Name]
[Same structure]

### Theme N: [Name]
[Same structure]

### Cross-Theme Connections
[How themes relate to each other]

### Temporal Trends
[How the field's understanding has evolved]

## 5. Evidence Triangulation

### Triangulation Matrix
| Finding | Genetic | Clinical | In Vitro | In Vivo | Epidemiological | Computational |
|---------|---------|----------|----------|---------|-----------------|---------------|

### Triangulation Analysis
[Where evidence types agree and disagree, with implications]

### Key Discrepancies
[Most important disagreements between evidence types, with analysis of possible explanations]

## 6. Synthesis

### 6.1 What We Know (High Confidence)
[Findings with strong evidence and triangulation — traceable]

### 6.2 What We Think (Moderate Confidence)
[Findings with supporting but incomplete evidence — traceable]

### 6.3 What We Don't Know (Evidence Gaps)
[Questions without adequate evidence]

### 6.4 Translation Gaps
[Knowledge established in one context but not applied in another]

### 6.5 Emerging Trends
[Recent shifts and preprint-stage developments]

## 7. Quality Assessment

### Synthesis Quality Metrics
- Systematic completeness: [X/10] — How thoroughly was the literature searched?
- Evidence quality: [X/10] — What is the overall level of evidence?
- Triangulation depth: [X/10] — How many evidence types were cross-validated?
- Traceability: [X/10] — Is every conclusion linked to source evidence?
- Bias awareness: [X/10] — Were search biases (publication, language, time) addressed?

### Overall Synthesis Quality Score: [X/50]

### Limitations of This Synthesis
[Honest assessment of gaps in the synthesis itself]

## 8. Implications & Recommendations

### For Research
[What studies would most advance understanding?]

### For Clinical Practice (if applicable)
[What can currently be applied? What needs more evidence?]

### For Drug Development (if applicable)
[Target validation status, clinical development implications]

### Priority Research Questions
1. [Most impactful unanswered question]
2. [Second priority]
3. [Third priority]
```

---

## Python Code Templates

### Evidence Table Builder

```python
"""
Structured evidence extraction and tabulation.
"""

from dataclasses import dataclass, field
from enum import IntEnum

class EvidenceLevel(IntEnum):
    SYSTEMATIC_REVIEW = 1
    RCT = 2
    CONTROLLED_OBSERVATIONAL = 3
    CASE_SERIES = 4
    EXPERT_OPINION = 5

class EvidenceStrength(str):
    STRONG = "Strong"
    MODERATE = "Moderate"
    WEAK = "Weak"
    VERY_WEAK = "Very Weak"
    GAP = "Gap"

@dataclass
class EvidenceEntry:
    pmid: str
    authors: str
    year: int
    journal: str
    design: str
    sample_size: int
    key_finding: str
    effect_size: str
    evidence_level: EvidenceLevel
    risk_of_bias: str  # Low/Medium/High
    themes: list[str] = field(default_factory=list)
    limitations: str = ""
    agreement: str = ""  # Consistent/Mixed/Contradictory

@dataclass
class ThemeSynthesis:
    name: str
    consensus_findings: list[dict] = field(default_factory=list)  # {finding, sources, strength}
    contested_findings: list[dict] = field(default_factory=list)  # {finding, for_sources, against_sources}
    evidence_gaps: list[str] = field(default_factory=list)
    overall_strength: str = ""


def grade_theme_strength(entries: list[EvidenceEntry]) -> str:
    """
    Grade overall evidence strength for a theme based on its entries.
    """
    if not entries:
        return "Gap"

    levels = [e.evidence_level for e in entries]
    n_studies = len(entries)
    best_level = min(levels)
    avg_level = sum(levels) / len(levels)

    # Check for consistency
    agreements = [e.agreement for e in entries if e.agreement]
    consistent = all(a == "Consistent" for a in agreements) if agreements else False

    if best_level <= 2 and n_studies >= 3 and consistent:
        return "Strong"
    elif best_level <= 3 and n_studies >= 2:
        return "Moderate"
    elif n_studies >= 2:
        return "Weak"
    else:
        return "Very Weak"


def build_triangulation_matrix(entries: list[EvidenceEntry], findings: list[str]) -> dict:
    """
    Build a triangulation matrix mapping findings to evidence types.
    """
    evidence_types = {
        "Genetic": ["GWAS", "genetic", "variant", "SNP", "linkage"],
        "Clinical": ["RCT", "clinical trial", "patients", "phase"],
        "In Vitro": ["in vitro", "cell line", "culture", "HEK", "CHO"],
        "In Vivo": ["mouse", "rat", "animal model", "in vivo", "xenograft"],
        "Epidemiological": ["cohort", "population", "epidemiol", "registry"],
        "Computational": ["computational", "in silico", "simulation", "model"]
    }

    matrix = {}
    for finding in findings:
        matrix[finding] = {}
        relevant = [e for e in entries if finding.lower() in e.key_finding.lower()]
        for etype, keywords in evidence_types.items():
            matching = [e for e in relevant
                       if any(k in e.design.lower() or k in e.key_finding.lower()
                             for k in keywords)]
            if matching:
                agreements = [e.agreement for e in matching]
                if all(a == "Consistent" for a in agreements):
                    matrix[finding][etype] = "Supports"
                elif all(a == "Contradictory" for a in agreements):
                    matrix[finding][etype] = "Contradicts"
                else:
                    matrix[finding][etype] = "Mixed"
            else:
                matrix[finding][etype] = "No data"

    return matrix
```


---

## Multi-Agent Workflow Examples

**"Synthesize the evidence on PCSK9 inhibition for cardiovascular risk reduction"**
1. Research Synthesis -> 6-phase synthesis with PICO scope, systematic search, knowledge model, triangulation
2. Drug Target Validator -> Independent validation scoring for PCSK9 as a cardiovascular target
3. Clinical Trial Analyst -> Detailed analysis of PCSK9 inhibitor trial data
4. Meta-Cognition -> Audit the synthesis for biases and confidence calibration

**"What does the field know about gut-brain axis mechanisms in depression?"**
1. Research Synthesis -> Full synthesis with PPC scope across microbiome, immunological, and neural evidence
2. Disease Research -> Disease mechanism context for depression
3. Hypothesis Generation -> Generate mechanistic hypotheses from synthesis gaps
4. Literature Deep Research -> Deep dive into specific contested findings

**"Build a knowledge model of CAR-T cell therapy resistance mechanisms"**
1. Research Synthesis -> Structured knowledge model across resistance themes (antigen loss, TME, T-cell exhaustion)
2. Systems Biology -> Pathway-level analysis of resistance mechanisms
3. Single Cell Analysis -> Single-cell evidence for T-cell exhaustion phenotypes
4. Scientific Critical Thinking -> Evaluate quality of key resistance mechanism studies

**"Map the evidence landscape for GLP-1 agonists beyond diabetes"**
1. Research Synthesis -> Multi-indication synthesis with triangulation across metabolic, cardiovascular, neurological evidence
2. Drug Research -> Comprehensive GLP-1 agonist monograph
3. Competitive Intelligence -> Competitive landscape for GLP-1 pipeline
4. What-If Oracle -> Scenario modeling for indication expansion strategies

**"Synthesize single-cell transcriptomics findings in tumor immunology"**
1. Research Synthesis -> Technology-focused synthesis with temporal trend analysis
2. Single Cell Analysis -> Technical depth on scRNA-seq methodologies
3. Precision Oncology Advisor -> Clinical implications of tumor immune subtypes
4. Biomarker Discovery -> Biomarker candidates emerging from synthesis

**"What is the current evidence on neuroinflammation as a driver of Alzheimer's disease?"**
1. Research Synthesis -> Full synthesis with evidence triangulation (genetic, biomarker, imaging, pathology)
2. Disease Research -> Alzheimer's disease mechanism overview
3. Drug Target Analyst -> Neuroinflammation targets and their validation status
4. Research Grants -> Frame synthesis gaps as fundable research questions

---

## Handling Large-Scale Synthesis (50+ Papers)

Use a tiered approach to manage scope:

```
Tier 1: Existing reviews/meta-analyses (5-10 papers) -> landscape map, extract reference lists
Tier 2: Key primary studies cited across multiple reviews (15-25 papers) -> foundational evidence
Tier 3: Recent studies not yet in reviews (10-20 papers) -> cutting edge
Tier 4: Contradictory/outlier studies (5-10 papers) -> actively seek negative results

Build incrementally: complete one theme at a time (extract -> model -> write),
then add cross-theme connections and triangulation progressively.
```

---

## Common Pitfalls in Research Synthesis

| Pitfall | Prevention |
|---------|-----------|
| **Narrative review disguised as synthesis** | Use systematic search, actively seek contradictory evidence |
| **Scope creep** | Define PICO/PPC before searching, enforce inclusion/exclusion criteria |
| **Recency bias** | Include temporal analysis, search without date restrictions for key concepts |
| **Publication bias** | Search for negative results, check ClinicalTrials.gov for unreported studies |
| **Citation chain bias** | Search independently across databases, don't rely solely on reference lists |
| **Counting papers instead of weighing evidence** | Use evidence level grading, weight by quality not quantity |
| **Conflating association with causation** | Label evidence types, reserve causal language for interventional studies |
| **Ignoring null results** | Dedicate a section to null and negative findings |

---

## Completeness Checklist

- [ ] Research question defined using appropriate framework (PICO, PPC, or variant)
- [ ] Inclusion and exclusion criteria explicitly stated before searching
- [ ] Search strategy documented with databases, queries, dates, and result counts
- [ ] At least 3 databases searched (PubMed + bioRxiv + one additional)
- [ ] Contradictory/negative evidence actively sought (not just positive findings)
- [ ] Screening process documented with inclusion/exclusion counts
- [ ] Evidence table completed with structured extraction from each included paper
- [ ] Each paper coded for study design, evidence level, sample size, and quality
- [ ] Knowledge model constructed with themes, consensus, contested findings, and gaps
- [ ] Cross-theme connections identified
- [ ] Temporal trends analyzed (has the field's view changed over time?)
- [ ] Evidence triangulation performed across at least 3 evidence types
- [ ] Triangulation discrepancies analyzed with possible explanations
- [ ] Every conclusion traceable to source papers with evidence strength rating
- [ ] Synthesis organized into What We Know / What We Think / What We Don't Know
- [ ] Translation gaps identified (knowledge in one field not applied in another)
- [ ] Emerging trends captured (preprints, recent paradigm shifts)
- [ ] Quality assessment scored across 5 dimensions
- [ ] Limitations of the synthesis itself honestly assessed
- [ ] Priority research questions identified from evidence gaps
- [ ] No `[Analyzing...]` placeholders remain in final report
