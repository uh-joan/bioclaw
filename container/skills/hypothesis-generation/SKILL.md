---
name: hypothesis-generation
description: Systematic scientific hypothesis formulation, evaluation, and experimental design. Generates 3-5 competing hypotheses with quality scoring (testability, falsifiability, parsimony, explanatory power), designs experimental tests, and formulates testable predictions. Use when asked to generate hypotheses, design experiments, evaluate scientific claims, formulate research questions, or plan hypothesis-driven research for drug discovery, disease mechanisms, target validation, or any scientific inquiry.
---

# Hypothesis Generation and Evaluation Specialist

Systematically formulates, evaluates, and ranks competing scientific hypotheses for any biological or pharmacological question. Applies the strong inference method -- generating multiple plausible hypotheses, designing critical experiments that distinguish between them, and scoring each hypothesis on testability, falsifiability, parsimony, explanatory power, and consistency with existing evidence. Integrates literature evidence from PubMed, bioRxiv, Open Targets, ChEMBL, Reactome, KEGG, STRING, Ensembl, and UniProt to ground hypotheses in current knowledge. Produces structured reports with ranked hypotheses, experimental designs, testable predictions, and decision trees for hypothesis-driven research in drug discovery, disease biology, target validation, and translational science.

## Report-First Workflow

1. **Create report file immediately**: `[phenomenon]_hypothesis_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as evidence is gathered
4. **Never show raw tool output**: Synthesize into report
5. **Final verification**: Ensure no placeholders remain

## When NOT to Use This Skill

- Single variant interpretation -> use `variant-interpretation`
- Drug target validation scoring -> use `drug-target-validator`
- Systematic literature review -> use `systematic-literature-reviewer`
- Clinical trial design -> use `clinical-trial-protocol-designer`
- Statistical test selection -> use `statistical-modeling`
- Disease mechanism overview -> use `disease-research`

## Cross-Reference: Other Skills

- **Deep disease biology context** -> use disease-research skill
- **Target druggability and validation** -> use drug-target-analyst skill
- **Biomarker identification for hypothesis testing** -> use biomarker-discovery skill
- **Clinical trial design from hypotheses** -> use clinical-trial-protocol-designer skill
- **Statistical power and test design** -> use statistical-modeling skill
- **Competitive intelligence on therapeutic area** -> use competitive-intelligence skill
- **Pharmacogenomic stratification** -> use precision-medicine-stratifier skill

## Available MCP Tools

### `mcp__pubmed__pubmed_articles` (Literature Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__biorxiv__biorxiv_info` (Preprints & Emerging Research)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_preprints` | Search bioRxiv/medRxiv preprints | `query`, `server`, `limit` |
| `get_preprint_details` | Full preprint metadata | `doi` |
| `get_recent_preprints` | Latest preprints by topic | `topic`, `days`, `limit` |
| `get_published_version` | Find journal-published version | `doi` |

### `mcp__opentargets__opentargets_info` (Target-Disease Associations)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `search_diseases` | Search diseases by name/synonym | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId`, `diseaseId`, `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes) | `id` (EFO ID) |

### `mcp__chembl__chembl_info` (Bioactivity & Drug Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |
| `get_admet` | ADMET/drug-likeness properties | `chembl_id` |

### `mcp__reactome__reactome_data` (Pathway Context)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_pathways` | Search Reactome pathways | `query`, `limit` |
| `get_pathway_details` | Full pathway information | `pathway_id` |
| `get_pathway_participants` | Genes/proteins in a pathway | `pathway_id` |
| `analyze_gene_list` | Pathway enrichment analysis | `genes`, `limit` |

### `mcp__kegg__kegg_data` (Metabolic & Disease Pathways)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_diseases` | Search KEGG disease entries | `query` |
| `get_disease_info` | Disease details (genes, pathways, drugs, markers) | `disease_id` |
| `search_pathways` | Search KEGG pathways by keyword | `query` |
| `get_pathway_info` | Full pathway details | `pathway_id` |
| `get_pathway_genes` | All genes in a pathway | `pathway_id` |
| `search_drugs` | Search KEGG drug entries | `query` |
| `get_drug_info` | Drug details (targets, pathways) | `drug_id` |
| `convert_identifiers` | Convert between KEGG and external IDs | `identifiers`, `source_db`, `target_db` |
| `find_related_entries` | Find entries related to a KEGG entry | `entry_id` |

### `mcp__stringdb__stringdb_data` (Protein-Protein Interactions)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_interactions` | Protein interaction partners | `identifiers`, `species`, `limit` |
| `get_network` | Full interaction network | `identifiers`, `species`, `score` |
| `get_enrichment` | Functional enrichment of a gene set | `identifiers`, `species` |
| `get_functional_annotation` | GO/KEGG annotations for proteins | `identifiers`, `species` |

### `mcp__ensembl__ensembl_data` (Genomic Context)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `lookup_gene` | Gene details by symbol or ID | `symbol`, `species` |
| `get_sequence` | DNA/protein sequence | `id`, `type` |
| `get_variants` | Known variants for a gene/region | `id`, `region` |
| `get_homologues` | Orthologues and paralogues | `id`, `type` |
| `get_regulatory` | Regulatory features for a region | `region`, `species` |

### `mcp__uniprot__uniprot_data` (Protein Function & Structure)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_proteins` | Search UniProt by name/gene | `query`, `limit` |
| `get_protein_details` | Full protein record | `accession` |
| `get_protein_features` | Domains, modifications, variants | `accession` |
| `get_protein_structure` | PDB structure references | `accession` |

### `mcp__openalex__openalex_data` (Citation-Based Hypothesis Scoring & Trend Detection)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_works` | Search papers supporting or refuting hypotheses; returns citation counts | `query` |
| `get_work` | Get work details by DOI or PMID for evidence verification | `id` |
| `search_authors` | Find researchers working on the phenomenon | `query` |
| `get_author` | Author citation metrics for assessing evidence source credibility | `id` |
| `search_topics` | Map research topics to assess research momentum around a hypothesis | `query` |
| `get_cited_by` | Forward citation chaining to track how seminal findings have been built upon | `workId` |
| `get_works_by_author` | Author's top-cited works for identifying foundational evidence | `authorId` |
| `get_works_by_institution` | Detect emerging research clusters at specific institutions | `institutionId` |

**Usage note:** Use OpenAlex for citation-based hypothesis scoring (highly-cited supporting evidence strengthens a hypothesis), research momentum assessment via topic-level publication trends, and preprint detection through recent works tracking. The `search_topics` method helps identify whether a hypothesis aligns with growing or declining research areas.

---

## 8-Phase Hypothesis Generation Workflow

### Phase 1: Phenomenon Understanding

Parse the scientific observation, question, or unexplained finding. Define the scope and identify the key variables.

```
1. Identify the core phenomenon:
   - What has been observed? (observation)
   - What is unexplained? (knowledge gap)
   - What is the question? (research question)

2. Define variables:
   - Independent variables (manipulated/causal)
   - Dependent variables (measured/outcome)
   - Confounding variables (potential confounders)
   - Moderating variables (conditions that alter the relationship)

3. Establish scope:
   - Biological level (molecular, cellular, tissue, organ, organism, population)
   - Therapeutic area (oncology, neuroscience, immunology, metabolic, etc.)
   - Temporal dimension (acute, chronic, developmental)
   - Species context (human, mouse, in vitro, computational)

4. Frame as a structured research question:
   "In [POPULATION/SYSTEM], does [INDEPENDENT VARIABLE] affect [DEPENDENT VARIABLE]
    through [PROPOSED MECHANISM], and can this be measured by [ENDPOINT]?"
```

### Phase 2: Literature Search

Gather existing evidence using MCP tools to understand the current state of knowledge.

```
1. Primary literature search:
   mcp__pubmed__pubmed_articles(method: "search_advanced", term: "PHENOMENON KEY_TERMS mechanism", num_results: 20)
   -> Peer-reviewed evidence on the phenomenon

2. Recent preprints for cutting-edge findings:
   mcp__biorxiv__biorxiv_info(method: "search_preprints", query: "PHENOMENON", limit: 10)
   -> Emerging data not yet in PubMed

3. Target-disease evidence landscape:
   mcp__opentargets__opentargets_info(method: "search_diseases", query: "DISEASE_CONTEXT", size: 10)
   mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_ID", minScore: 0.3, size: 50)
   -> Validated genetic and pharmacological associations

4. Pathway context for mechanistic hypotheses:
   mcp__reactome__reactome_data(method: "search_pathways", query: "PATHWAY_KEYWORD", limit: 10)
   mcp__kegg__kegg_data(method: "search_pathways", query: "PATHWAY_KEYWORD")
   -> Biological pathways relevant to the phenomenon

5. Protein interaction networks:
   mcp__stringdb__stringdb_data(method: "get_interactions", identifiers: "GENE1,GENE2", species: 9606, limit: 20)
   -> Interaction partners that may explain the mechanism

6. Protein function and domain architecture:
   mcp__uniprot__uniprot_data(method: "search_proteins", query: "PROTEIN_NAME", limit: 5)
   mcp__uniprot__uniprot_data(method: "get_protein_features", accession: "ACCESSION_ID")
   -> Functional domains, post-translational modifications, known variants

7. Genomic and evolutionary context:
   mcp__ensembl__ensembl_data(method: "lookup_gene", symbol: "GENE_SYMBOL", species: "homo_sapiens")
   mcp__ensembl__ensembl_data(method: "get_homologues", id: "ENSEMBL_ID", type: "orthologues")
   -> Conservation, regulatory elements, model organism data

8. Compound and pharmacological data (if drug-related):
   mcp__chembl__chembl_info(method: "drug_search", query: "DRUG_OR_INDICATION", limit: 20)
   mcp__chembl__chembl_info(method: "get_mechanism", chembl_id: "CHEMBL_ID")
   -> Known pharmacology, mechanism of action, bioactivity data
```

### Phase 3: Evidence Synthesis

Summarize current knowledge, identify gaps, contradictions, and unexplained observations.

```
1. Organize evidence into categories:
   - Confirmed findings (replicated, multi-source)
   - Preliminary findings (single study, preprint)
   - Contradictory findings (conflicting results across studies)
   - Absence of evidence (questions not yet investigated)

2. Identify knowledge gaps:
   - What mechanisms remain unexplained?
   - Which patient populations are understudied?
   - What temporal dynamics are unknown?
   - Which model systems lack validation?

3. Map contradictions:
   - Study A shows X, Study B shows not-X
   - Possible explanations: different models, doses, timepoints, populations
   - These contradictions are fertile ground for hypothesis generation

4. Assign evidence grades to existing knowledge:
   [T1] - Direct clinical evidence (RCT, human genetics, approved drug)
   [T2] - Strong preclinical/observational (Phase II+, large cohort, GWAS)
   [T3] - Moderate evidence (in vitro, animal model, case series)
   [T4] - Hypothesis-level (text mining, pathway inference, preprint)

5. Create an evidence map:
   - Core established facts (high confidence)
   - Peripheral supporting evidence (moderate confidence)
   - Speculative connections (low confidence, hypothesis-generating)
```

### Phase 4: Hypothesis Generation

Formulate 3-5 competing hypotheses including null and alternative hypotheses. Each hypothesis must have a distinct mechanism, specific predictions, and clearly stated assumptions.

```
Hypothesis Types to Generate:

1. NULL HYPOTHESIS (H0):
   - No effect, no relationship, or no difference
   - Defines the baseline against which alternatives are tested
   - Example: "Drug X has no effect on biomarker Y levels in population Z"

2. MECHANISTIC HYPOTHESIS (H1-type):
   - Proposes a specific causal mechanism
   - "X causes Y through mechanism M"
   - Must specify the molecular/cellular pathway
   - Example: "BRAF V600E activates MEK/ERK signaling, driving melanocyte proliferation"

3. CORRELATIONAL HYPOTHESIS (H2-type):
   - Proposes an association without direct causation
   - "X is associated with Y, possibly through shared factor Z"
   - Useful when causal experiments are not yet feasible
   - Example: "Gut microbiome diversity correlates with immunotherapy response via T-cell repertoire"

4. INTERVENTIONAL HYPOTHESIS (H3-type):
   - Proposes that modifying X will change Y
   - Directly translatable to experimental design
   - "Inhibiting target T will reduce disease phenotype P"
   - Example: "CDK4/6 inhibition will restore cell cycle control in RB1-proficient tumors"

5. COMPARATIVE HYPOTHESIS (H4-type):
   - Compares two or more competing mechanisms
   - "Mechanism A is more likely than mechanism B because of evidence E"
   - Useful when multiple plausible explanations exist
   - Example: "Phase III failure is due to patient heterogeneity rather than insufficient dosing"

For each hypothesis, document:
- Statement: Clear, concise, one-sentence formulation
- Mechanism: Proposed biological/pharmacological pathway
- Assumptions: What must be true for this hypothesis to hold
- Predictions: 2-3 testable predictions that follow from the hypothesis
- Supporting evidence: Current data supporting this hypothesis [with T1-T4 grades]
- Contradicting evidence: Current data arguing against this hypothesis
- Distinguishing feature: What makes this hypothesis different from the others
```

### Phase 5: Hypothesis Quality Evaluation

Score each hypothesis on 5 quality dimensions using the standardized scoring framework.

```
Scoring Framework (0-50 total, weighted composite):

| Dimension         | Weight | Max Score | Scoring Criteria |
|-------------------|--------|-----------|------------------|
| Testability       | 0.25   | 10        | Can it be experimentally tested with available technology? |
| Falsifiability    | 0.25   | 10        | Can it be disproven by a specific experimental outcome? |
| Parsimony         | 0.15   | 10        | Is it the simplest explanation consistent with the data? |
| Explanatory Power | 0.20   | 10        | How much of the observed phenomenon does it explain? |
| Consistency       | 0.15   | 10        | Does it fit existing evidence without contradiction? |

Testability Scoring Guide (0-10):
  10: Can be tested with standard assays in any well-equipped lab
  8:  Requires specialized but available technology (CRISPR, mass spec, etc.)
  6:  Requires model system development or novel assay design
  4:  Requires longitudinal study or rare patient population
  2:  Requires technology not yet validated or population not accessible
  0:  Cannot be tested with current methods

Falsifiability Scoring Guide (0-10):
  10: A single well-designed experiment can definitively disprove it
  8:  Can be disproven with 2-3 complementary experiments
  6:  Can be partially disproven but alternative interpretations exist
  4:  Difficult to disprove due to multiple escape clauses
  2:  Nearly unfalsifiable without extreme experimental conditions
  0:  Unfalsifiable (not a scientific hypothesis)

Parsimony Scoring Guide (0-10):
  10: Invokes a single known mechanism with minimal assumptions
  8:  Invokes 2 known mechanisms with well-supported assumptions
  6:  Requires 3+ mechanisms or some unverified assumptions
  4:  Requires novel mechanisms or multiple unverified assumptions
  2:  Requires extensive novel biology with no precedent
  0:  Requires extraordinary assumptions contradicting known biology

Explanatory Power Scoring Guide (0-10):
  10: Explains all observed data including edge cases and exceptions
  8:  Explains primary observations and most secondary findings
  6:  Explains the core phenomenon but not peripheral observations
  4:  Explains some aspects but leaves major observations unexplained
  2:  Only explains a narrow slice of the available data
  0:  Explains essentially nothing about the phenomenon

Consistency Scoring Guide (0-10):
  10: Fully consistent with all published evidence across multiple sources
  8:  Consistent with most evidence; minor discrepancies have explanations
  6:  Generally consistent but some contradictions exist
  4:  Several contradictions with existing evidence
  2:  Major contradictions with well-established findings
  0:  Directly contradicts established scientific consensus

Weighted Composite Score Calculation:
  Score = (Testability * 0.25) + (Falsifiability * 0.25) + (Parsimony * 0.15) +
          (Explanatory Power * 0.20) + (Consistency * 0.15)
  Normalize to 0-50 scale: Final = Score * 5
```

### Priority Tiers

| Tier | Score Range | Interpretation | Action |
|------|------------|----------------|--------|
| **Tier 1** | 40-50 | Strong hypothesis | Prioritize for immediate experimental testing |
| **Tier 2** | 30-39 | Viable hypothesis | Worth investigating; design experiments |
| **Tier 3** | 20-29 | Weak hypothesis | Needs refinement before testing; gather more evidence |
| **Tier 4** | 0-19 | Poor hypothesis | Reconsider fundamentals; may not be worth pursuing |

### Phase 6: Experimental Design

For each hypothesis (prioritized by score), design 2-3 critical experiments that can confirm or refute it.

```
Experimental Design Template:

Experiment [N]: [Title]
  Hypothesis tested: H[X]
  Objective: [What this experiment will determine]

  Design:
    - Model system: [cell line, animal model, patient cohort, in silico]
    - Key intervention: [treatment, knockout, overexpression, drug, etc.]
    - Primary endpoint: [measurable outcome]
    - Secondary endpoints: [additional measurements]

  Controls:
    - Positive control: [known to produce the expected effect]
    - Negative control: [known to have no effect]
    - Vehicle/sham control: [controls for experimental procedure]
    - Specificity control: [confirms the effect is target-specific]

  Expected outcomes:
    - If H[X] is TRUE: [specific measurable result, direction, magnitude]
    - If H[X] is FALSE: [specific measurable result]
    - If INCONCLUSIVE: [what would make the result ambiguous]

  Power and feasibility:
    - Sample size estimate: [based on expected effect size]
    - Timeline: [weeks/months to completion]
    - Key reagents/resources: [what is needed]
    - Technical risk: [Low/Medium/High — what could go wrong]

  Distinguishing power:
    - This experiment distinguishes H[X] from H[Y] because:
      [Explanation of how the result pattern differs between hypotheses]
```

### Critical Experiment Design Principles

```
1. STRONG INFERENCE (Platt, 1964):
   - Design experiments that distinguish between competing hypotheses
   - An experiment that confirms H1 but cannot rule out H2 is weak
   - Prefer experiments whose outcomes differ for different hypotheses

2. CRUCIAL EXPERIMENTS:
   - Identify the one experiment that most efficiently eliminates hypotheses
   - If H1 predicts outcome A and H2 predicts outcome B, measure the variable
     that produces A or B, not a variable consistent with both

3. CONTROLS HIERARCHY:
   - Every experiment needs: biological, technical, positive, and negative controls
   - Dose-response: test multiple concentrations to establish causality
   - Time-course: capture temporal dynamics, not just endpoint

4. ORTHOGONAL VALIDATION:
   - Use independent methods to confirm key findings
   - Genetic (CRISPR KO) + pharmacological (small molecule) + antibody approaches
   - If all three converge, confidence is high

5. TRANSLATIONAL RELEVANCE:
   - Consider how in vitro findings will be validated in vivo
   - Plan for human-relevant models early (primary cells, organoids, PDX)
   - Think about the clinical endpoint from the start
```

### Phase 7: Prediction Formulation

For each hypothesis, formulate specific, measurable, testable predictions.

```
Prediction Template:

Prediction [N].[M]: [Concise statement]
  Derived from: Hypothesis H[X]
  Type: [Confirmatory / Exploratory / Discriminating]

  Specific prediction:
    "If H[X] is true, then [INTERVENTION] in [SYSTEM] will produce
     [DIRECTION] change in [MEASURABLE ENDPOINT] of [MAGNITUDE],
     within [TIMEFRAME]."

  Measurement:
    - Assay/method: [technique to measure the endpoint]
    - Units: [quantitative units]
    - Expected effect size: [fold-change, percentage, absolute value]
    - Statistical threshold: [p-value, confidence interval, Bayesian criterion]

  Decision rule:
    - CONFIRMED if: [specific quantitative criterion]
    - REFUTED if: [specific quantitative criterion]
    - INCONCLUSIVE if: [conditions that prevent a clear conclusion]

  Impact on hypothesis ranking:
    - If confirmed: H[X] score increases by [N] points in [dimension]
    - If refuted: H[X] is eliminated or score decreases by [N] points
    - If inconclusive: Additional experiment [Y] is triggered
```

### Phase 8: Report Generation

Compile all findings into a structured hypothesis report with ranked hypotheses, experimental plans, and a decision tree.

```
Report Structure:

# Hypothesis Report: [Phenomenon]
**Date:** [DATE] | **Domain:** [Therapeutic Area] | **Scope:** [Biological Level]

## Executive Summary
- Core question and its significance
- Number of hypotheses generated and top-ranked hypothesis
- Key recommended experiment
- Expected timeline to hypothesis resolution

## 1. Phenomenon Definition
- Observation and research question
- Variables (independent, dependent, confounding)
- Scope and biological level

## 2. Evidence Landscape
- Summary of [N] publications retrieved
- Key established findings [T1-T2]
- Knowledge gaps identified
- Contradictions in the literature

## 3. Competing Hypotheses
### H0: Null Hypothesis
### H1: [Mechanistic]
### H2: [Alternative Mechanism]
### H3: [Interventional]
### H4: [Comparative]

## 4. Hypothesis Quality Scores
| Hypothesis | Test. | Fals. | Pars. | Expl. | Cons. | Weighted | Tier |
|------------|-------|-------|-------|-------|-------|----------|------|
| H1         | X/10  | X/10  | X/10  | X/10  | X/10  | XX/50    | T[N] |
| H2         | X/10  | X/10  | X/10  | X/10  | X/10  | XX/50    | T[N] |
| ...        |       |       |       |       |       |          |      |

## 5. Experimental Plans
### Experiment 1: [Title] (tests H[X] vs H[Y])
### Experiment 2: [Title]
...

## 6. Testable Predictions
### Predictions for H1
### Predictions for H2
...

## 7. Decision Tree
- If Experiment 1 shows A -> pursue H1, run Experiment 3
- If Experiment 1 shows B -> pursue H2, run Experiment 4
- If Experiment 1 is inconclusive -> modify protocol and repeat

## 8. Recommendations
- Prioritized experimental plan with timeline
- Resource requirements
- Risk assessment and contingency plans

## Appendix: Evidence Table
| Source | PMID/DOI | Key Finding | Evidence Grade | Supports |
```

---

## Hypothesis Scoring Framework — Detailed Reference

### Weighted Composite Calculation

The composite score maps raw dimension scores to a 0-50 scale:

```
Raw weighted score = (Testability * 0.25) + (Falsifiability * 0.25) +
                     (Parsimony * 0.15) + (Explanatory_Power * 0.20) +
                     (Consistency * 0.15)

Final score = Raw weighted score * 5

Maximum possible: (10 * 0.25 + 10 * 0.25 + 10 * 0.15 + 10 * 0.20 + 10 * 0.15) * 5
               = (2.5 + 2.5 + 1.5 + 2.0 + 1.5) * 5
               = 10.0 * 5 = 50
```

### Dimension Weight Rationale

- **Testability (0.25)**: A hypothesis that cannot be tested is not useful for experimental science. Highest weight because untestable hypotheses waste resources.
- **Falsifiability (0.25)**: Following Popper, falsifiability is the demarcation criterion for scientific hypotheses. Equal to testability because both are essential for the scientific method.
- **Parsimony (0.15)**: Occam's razor favors simpler explanations, but complex biology sometimes requires complex hypotheses. Lower weight to avoid penalizing legitimate multi-mechanism hypotheses.
- **Explanatory Power (0.20)**: A good hypothesis should explain a substantial portion of the observations. Higher than parsimony because breadth of explanation is critical for translational impact.
- **Consistency (0.15)**: Consistency with existing evidence is important but should not overly penalize novel hypotheses that challenge current thinking. Lower weight to allow paradigm-shifting ideas.

### Score Interpretation Matrix

```
High Testability + High Falsifiability + Low Explanatory Power
  -> Narrow but executable hypothesis. Good for a quick win. Consider broadening scope.

Low Testability + High Explanatory Power + High Consistency
  -> "Grand theory" that explains a lot but is hard to test. Break into sub-hypotheses.

High Testability + Low Consistency
  -> Contrarian hypothesis. Could be paradigm-shifting or simply wrong. Worth a pilot.

High Parsimony + Low Explanatory Power
  -> Oversimplified. Consider whether additional mechanisms need to be incorporated.

All dimensions moderate (5-7 range)
  -> Decent starting point. Look for the one experiment that could elevate or eliminate it.
```

---

## Evidence Grading System

Apply evidence tier to every claim supporting or contradicting a hypothesis:

```
[T1] - Direct clinical evidence
       Completed RCT, Phase III data, approved drug label, validated human genetics (GWAS p<5e-8)
       Weight: Strong support for or against a hypothesis

[T2] - Strong preclinical or observational
       Phase II trial, large cohort study (n>1000), GWAS (suggestive), systematic review
       Weight: Substantial support; needs clinical confirmation

[T3] - Moderate evidence
       In vitro studies, animal models (mouse, rat, zebrafish), case series, small trials (n<50)
       Weight: Suggestive; hypothesis-generating rather than confirming

[T4] - Hypothesis-level
       Text mining, pathway inference, computational prediction, preprint, single case report
       Weight: Speculative; useful for hypothesis generation but not for scoring consistency
```

### Evidence Aggregation for Hypothesis Scoring

```
When scoring the Consistency dimension:
- Count supporting evidence by tier: T1 evidence = 4 points, T2 = 3, T3 = 2, T4 = 1
- Count contradicting evidence: T1 contradiction = -4 points, T2 = -3, T3 = -2, T4 = -1
- Net evidence score informs the Consistency rating

When scoring Explanatory Power:
- List all observations the hypothesis explains
- Weight by evidence tier of the observation
- A hypothesis that explains T1-supported observations scores higher
```

---

## Hypothesis Generation Strategies

### Strategy 1: Mechanism Decomposition

Break a complex phenomenon into sub-mechanisms and generate hypotheses for each.

```
Phenomenon: "Drug X shows efficacy in Phase II but fails Phase III"

Sub-mechanisms:
  A. Patient selection differences between trials
  B. Dose-response relationship not optimized
  C. Endpoint sensitivity differences
  D. Disease heterogeneity masking responder subgroups
  E. Placebo response inflation in Phase III
  F. Pharmacokinetic variability at scale

Each sub-mechanism becomes the basis for a competing hypothesis.
```

### Strategy 2: Analogy Transfer

Import mechanisms from related biological systems or therapeutic areas.

```
Observation: "Novel kinase inhibitor shows unexpected cardiotoxicity"

Analogies to explore:
  1. Other kinase inhibitors with cardiac effects (e.g., imatinib, sunitinib)
     -> What was the mechanism? (mitochondrial toxicity, hERG inhibition, metabolic stress)
  2. Related kinases with cardiac expression
     -> Does the target kinase have cardiac functions?
  3. Off-target kinase inhibition panel
     -> Which off-targets are known cardiotoxic kinases?

MCP workflow:
  mcp__chembl__chembl_info(method: "drug_search", query: "kinase inhibitor cardiotoxicity", limit: 20)
  mcp__uniprot__uniprot_data(method: "search_proteins", query: "TARGET_KINASE", limit: 5)
  -> Check tissue expression, especially cardiac
  mcp__stringdb__stringdb_data(method: "get_interactions", identifiers: "TARGET_KINASE", species: 9606)
  -> Interaction partners in cardiac tissue
```

### Strategy 3: Contradiction Exploitation

Use contradictions in the literature as hypothesis generators.

```
Contradiction: "Study A shows gene X is upregulated in disease; Study B shows downregulation"

Hypotheses from this contradiction:
  H1: Disease stage matters — X is upregulated early and downregulated late
  H2: Tissue specificity — X behaves differently in tissue A vs tissue B
  H3: Patient subgroups — genetic background modifies X expression
  H4: Technical artifact — different assay platforms, normalization methods, or sample quality

Each hypothesis generates different experimental predictions and can be tested
by controlling the variable identified as the source of contradiction.
```

### Strategy 4: Negative Space Analysis

Ask what would be expected if the null hypothesis were true, and look for deviations.

```
Null expectation: "If gene X has no role in disease Y, then:"
  - X expression should not differ between disease and healthy tissue
  - X knockout mice should have normal phenotype
  - X variants should not associate with disease risk in GWAS
  - Inhibiting X should not alter disease biomarkers

Check each expectation with MCP tools:
  mcp__opentargets__opentargets_info(method: "get_target_disease_associations", ...)
  mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_X knockout phenotype", ...)
  mcp__ensembl__ensembl_data(method: "get_variants", id: "ENSEMBL_ID")

Each violated expectation supports an alternative hypothesis.
Each confirmed expectation supports the null.
```

### Strategy 5: Network Perturbation

Use protein interaction networks to generate hypotheses about indirect effects.

```
Observation: "Inhibiting target A unexpectedly affects pathway B"

Network analysis:
  mcp__stringdb__stringdb_data(method: "get_interactions", identifiers: "TARGET_A", species: 9606, limit: 50)
  -> Identify proteins that interact with A and participate in pathway B

  mcp__reactome__reactome_data(method: "analyze_gene_list", genes: "TARGET_A,INTERACTOR_1,INTERACTOR_2")
  -> Find shared pathway memberships

Hypotheses:
  H1: Target A directly regulates a component of pathway B (direct interaction)
  H2: Target A shares a binding partner with pathway B component (indirect effect)
  H3: Target A inhibition causes compensatory upregulation of pathway B
  H4: Off-target effect — the inhibitor hits another target in pathway B
```

---

## Python Code Templates for Hypothesis Scoring

### Hypothesis Quality Radar Chart

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def plot_hypothesis_radar(hypotheses: dict, output_file: str = "hypothesis_radar.png"):
    """
    Plot radar chart comparing hypothesis quality scores.

    Parameters:
        hypotheses: dict of {name: {dimension: score}}
            Example: {
                "H1: BRAF-driven proliferation": {
                    "Testability": 9, "Falsifiability": 8,
                    "Parsimony": 7, "Explanatory Power": 8, "Consistency": 9
                },
                "H2: Immune evasion": {
                    "Testability": 7, "Falsifiability": 6,
                    "Parsimony": 5, "Explanatory Power": 9, "Consistency": 7
                }
            }
        output_file: path to save the chart
    """
    dimensions = ["Testability", "Falsifiability", "Parsimony",
                   "Explanatory Power", "Consistency"]
    num_dims = len(dimensions)
    angles = np.linspace(0, 2 * np.pi, num_dims, endpoint=False).tolist()
    angles += angles[:1]  # close the polygon

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    colors = plt.cm.Set2(np.linspace(0, 1, len(hypotheses)))

    for idx, (name, scores) in enumerate(hypotheses.items()):
        values = [scores[d] for d in dimensions]
        values += values[:1]
        ax.plot(angles, values, 'o-', linewidth=2, label=name, color=colors[idx])
        ax.fill(angles, values, alpha=0.15, color=colors[idx])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dimensions, size=12)
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(["2", "4", "6", "8", "10"], size=9)
    ax.set_title("Hypothesis Quality Comparison", size=16, pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Radar chart saved to {output_file}")
```

### Hypothesis Ranking Bar Chart

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def plot_hypothesis_ranking(hypotheses: dict, output_file: str = "hypothesis_ranking.png"):
    """
    Plot stacked bar chart showing weighted scores per hypothesis.

    Parameters:
        hypotheses: dict of {name: {dimension: score}}
        output_file: path to save the chart
    """
    dimensions = ["Testability", "Falsifiability", "Parsimony",
                   "Explanatory Power", "Consistency"]
    weights = {"Testability": 0.25, "Falsifiability": 0.25,
               "Parsimony": 0.15, "Explanatory Power": 0.20,
               "Consistency": 0.15}
    scale_factor = 5  # scale to 0-50

    names = list(hypotheses.keys())
    weighted_scores = {d: [] for d in dimensions}
    totals = []

    for name in names:
        total = 0
        for d in dimensions:
            raw = hypotheses[name][d]
            w = raw * weights[d] * scale_factor
            weighted_scores[d].append(w)
            total += w
        totals.append(total)

    # Sort by total score descending
    sort_idx = np.argsort(totals)[::-1]
    names = [names[i] for i in sort_idx]
    totals = [totals[i] for i in sort_idx]
    for d in dimensions:
        weighted_scores[d] = [weighted_scores[d][i] for i in sort_idx]

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = {"Testability": "#2196F3", "Falsifiability": "#F44336",
              "Parsimony": "#4CAF50", "Explanatory Power": "#FF9800",
              "Consistency": "#9C27B0"}
    bottom = np.zeros(len(names))

    for d in dimensions:
        vals = weighted_scores[d]
        ax.barh(names, vals, left=bottom, label=d, color=colors[d], edgecolor='white')
        bottom += np.array(vals)

    # Add total score labels
    for i, total in enumerate(totals):
        tier = "T1" if total >= 40 else "T2" if total >= 30 else "T3" if total >= 20 else "T4"
        ax.text(total + 0.5, i, f"{total:.1f} ({tier})", va='center', fontsize=11, fontweight='bold')

    # Add tier boundary lines
    for boundary, label in [(40, "Tier 1"), (30, "Tier 2"), (20, "Tier 3")]:
        ax.axvline(x=boundary, color='gray', linestyle='--', alpha=0.5)
        ax.text(boundary, len(names) - 0.5, label, ha='center', va='bottom',
                fontsize=9, color='gray')

    ax.set_xlim(0, 55)
    ax.set_xlabel("Weighted Composite Score (0-50)", fontsize=12)
    ax.set_title("Hypothesis Ranking by Quality Score", fontsize=14)
    ax.legend(loc='lower right', fontsize=10)
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Ranking chart saved to {output_file}")
```

### Hypothesis Scoring Calculator

```python
def score_hypothesis(name: str, testability: int, falsifiability: int,
                     parsimony: int, explanatory_power: int,
                     consistency: int) -> dict:
    """
    Calculate weighted composite score for a hypothesis.

    Parameters:
        name: hypothesis identifier
        testability: 0-10 score
        falsifiability: 0-10 score
        parsimony: 0-10 score
        explanatory_power: 0-10 score
        consistency: 0-10 score

    Returns:
        dict with raw scores, weighted scores, composite, and tier
    """
    weights = {
        "Testability": 0.25,
        "Falsifiability": 0.25,
        "Parsimony": 0.15,
        "Explanatory Power": 0.20,
        "Consistency": 0.15
    }
    raw = {
        "Testability": testability,
        "Falsifiability": falsifiability,
        "Parsimony": parsimony,
        "Explanatory Power": explanatory_power,
        "Consistency": consistency
    }
    weighted = {k: v * weights[k] for k, v in raw.items()}
    composite = sum(weighted.values()) * 5  # scale to 0-50

    if composite >= 40:
        tier = "Tier 1 - Strong hypothesis: prioritize for testing"
    elif composite >= 30:
        tier = "Tier 2 - Viable hypothesis: worth investigating"
    elif composite >= 20:
        tier = "Tier 3 - Weak hypothesis: needs refinement"
    else:
        tier = "Tier 4 - Poor hypothesis: reconsider fundamentals"

    return {
        "name": name,
        "raw_scores": raw,
        "weighted_scores": weighted,
        "composite_score": round(composite, 1),
        "tier": tier
    }


def compare_hypotheses(hypothesis_list: list) -> None:
    """
    Print a formatted comparison table for multiple scored hypotheses.

    Parameters:
        hypothesis_list: list of dicts from score_hypothesis()
    """
    # Sort by composite score descending
    ranked = sorted(hypothesis_list, key=lambda h: h["composite_score"], reverse=True)

    header = f"{'Rank':<5} {'Hypothesis':<40} {'Test':>5} {'Fals':>5} {'Pars':>5} {'Expl':>5} {'Cons':>5} {'Score':>7} {'Tier':<10}"
    print(header)
    print("-" * len(header))

    for rank, h in enumerate(ranked, 1):
        r = h["raw_scores"]
        print(f"{rank:<5} {h['name']:<40} {r['Testability']:>5} {r['Falsifiability']:>5} "
              f"{r['Parsimony']:>5} {r['Explanatory Power']:>5} {r['Consistency']:>5} "
              f"{h['composite_score']:>7.1f} {h['tier'].split(' - ')[0]:<10}")
```

### Decision Tree Visualization

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def plot_decision_tree(experiments: list, output_file: str = "hypothesis_decision_tree.png"):
    """
    Plot a decision tree for hypothesis testing.

    Parameters:
        experiments: list of dicts with structure:
            {
                "name": "Experiment 1: CRISPR KO",
                "outcome_a": {"result": "Cell death observed", "action": "Support H1, test H1.1"},
                "outcome_b": {"result": "No effect", "action": "Reject H1, pursue H2"},
                "outcome_c": {"result": "Partial effect", "action": "Inconclusive, run Exp 2"}
            }
        output_file: path to save the chart
    """
    fig, ax = plt.subplots(figsize=(16, 4 + 3 * len(experiments)))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3 * len(experiments) + 1)
    ax.axis('off')

    colors = {"support": "#4CAF50", "reject": "#F44336", "inconclusive": "#FF9800"}

    for i, exp in enumerate(experiments):
        y_base = 3 * (len(experiments) - i - 1) + 1.5

        # Experiment node
        rect = mpatches.FancyBboxPatch((3.5, y_base - 0.3), 3, 0.6,
                                        boxstyle="round,pad=0.1",
                                        facecolor="#2196F3", edgecolor="black")
        ax.add_patch(rect)
        ax.text(5, y_base, exp["name"], ha='center', va='center',
                fontsize=10, fontweight='bold', color='white')

        outcomes = [
            (1.0, exp["outcome_a"], colors["support"]),
            (5.0, exp["outcome_b"], colors["reject"]),
            (9.0, exp["outcome_c"], colors["inconclusive"])
        ]

        for x_pos, outcome, color in outcomes:
            # Arrow
            ax.annotate("", xy=(x_pos, y_base - 0.8),
                        xytext=(5, y_base - 0.3),
                        arrowprops=dict(arrowstyle="->", color=color, lw=1.5))

            # Outcome box
            rect = mpatches.FancyBboxPatch((x_pos - 1.2, y_base - 1.7), 2.4, 0.8,
                                            boxstyle="round,pad=0.1",
                                            facecolor=color, edgecolor="black", alpha=0.3)
            ax.add_patch(rect)
            ax.text(x_pos, y_base - 1.1, outcome["result"], ha='center', va='center',
                    fontsize=8, style='italic')
            ax.text(x_pos, y_base - 1.5, outcome["action"], ha='center', va='center',
                    fontsize=8, fontweight='bold')

    ax.set_title("Hypothesis Testing Decision Tree", fontsize=14, pad=20)
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Decision tree saved to {output_file}")
```

---

## Multi-Agent Workflow Examples

### Example 1: Drug Failure Investigation

```
User: "Why does Drug X fail in Phase III for Alzheimer's despite strong Phase II results?"

Agent coordinates:
1. hypothesis-generation
   -> Formulate 4 competing hypotheses:
      H1: Patient selection bias (Phase II enriched for early-stage, Phase III includes advanced)
      H2: Endpoint sensitivity (Phase II used biomarker, Phase III used clinical scale)
      H3: Dose-response plateau (efficacious dose in Phase II, underdosed in Phase III)
      H4: Disease heterogeneity (responder subgroup masked by non-responders at scale)
   -> Score each hypothesis and design discriminating experiments

2. disease-research
   -> Deep dive on Alzheimer's disease mechanisms, subtypes, progression biomarkers

3. drug-research
   -> Drug X pharmacology, PK/PD, clinical data from Phase II and III

4. clinical-trial-analyst
   -> Phase II vs Phase III protocol comparison: enrollment criteria, endpoints,
      sample size, duration, sites, regions

5. biomarker-discovery
   -> Identify stratification biomarkers (amyloid PET, tau PET, NfL, p-tau217)
      that could define a responder subgroup
```

### Example 2: Novel Target Validation

```
User: "Is LRRK2 a valid target for Parkinson's disease beyond genetic forms?"

Agent coordinates:
1. hypothesis-generation
   -> H0: LRRK2 is only relevant in LRRK2 mutation carriers (null)
   -> H1: LRRK2 kinase activity is elevated in idiopathic PD via alpha-synuclein pathology
   -> H2: LRRK2 mediates neuroinflammation through microglial activation in all PD
   -> H3: LRRK2 affects lysosomal function, and lysosomal dysfunction is universal in PD
   -> Score and design validation experiments

2. drug-target-validator
   -> LRRK2 druggability assessment, tractability, safety signals from KO models

3. disease-research
   -> Parkinson's disease comprehensive profile: genetics, pathways, current treatments

4. biomarker-discovery
   -> LRRK2 activity biomarkers (pS935-LRRK2, pRab10) for patient selection
```

### Example 3: Biomarker Mechanism Investigation

```
User: "Why do high IL-6 levels predict poor response to checkpoint inhibitors?"

Agent coordinates:
1. hypothesis-generation
   -> H1: IL-6 drives MDSC expansion, suppressing anti-tumor immunity
   -> H2: IL-6/STAT3 signaling upregulates PD-L1 on tumor cells, overwhelming anti-PD-1
   -> H3: IL-6 indicates advanced disease burden (confounder, not causal)
   -> H4: IL-6 promotes T-cell exhaustion through chronic inflammatory signaling
   -> Design experiments to distinguish causal vs. correlational mechanisms

2. biomarker-discovery
   -> IL-6 as a predictive biomarker: ROC analysis, cutoff determination, validation cohorts

3. disease-research
   -> Tumor immunology, checkpoint inhibitor mechanisms, resistance pathways

4. statistical-modeling
   -> Multivariate analysis design to test IL-6 independence from disease burden
```

### Example 4: Unexpected Phenotype Explanation

```
User: "CRISPR knockout of gene Y in hepatocytes causes unexpected cardiac phenotype"

Agent coordinates:
1. hypothesis-generation
   -> H1: Gene Y produces a secreted factor (hepatokine) that acts on cardiomyocytes
   -> H2: Gene Y knockout disrupts hepatic metabolism, causing systemic metabolic stress
   -> H3: Off-target CRISPR editing at a cardiac-expressed gene
   -> H4: Gene Y regulates a circulating lipid or bile acid that affects cardiac ion channels
   -> Design experiments: conditioned media, metabolomics, off-target sequencing

2. disease-research
   -> Liver-heart axis biology, hepatokines, metabolic cardiomyopathy

3. biomarker-discovery
   -> Identify circulating factors altered by gene Y knockout (secretomics, metabolomics)
```

---

## Pharma/Biotech Domain Knowledge

### Common Hypothesis Categories in Drug Development

```
Target Validation:
  - Is the target causally linked to disease? (genetic evidence, KO phenotype)
  - Is the target druggable? (binding pocket, expression, localization)
  - Will target modulation be safe? (essential functions, expression in healthy tissue)

Mechanism of Action:
  - Does the drug engage the intended target? (target engagement biomarkers)
  - Does target engagement produce the expected pharmacodynamic effect?
  - Does the PD effect translate to clinical benefit?

Clinical Translation:
  - Will preclinical efficacy translate to humans? (species differences, model fidelity)
  - Is the therapeutic window sufficient? (efficacy dose vs. toxicity dose)
  - Can we identify the right patients? (biomarker-guided enrichment)

Resistance and Escape:
  - Will the disease develop resistance? (mutation, pathway rewiring, efflux)
  - What is the mechanism of acquired resistance?
  - Can combination therapy prevent resistance?

Safety:
  - Is the observed toxicity on-target or off-target?
  - Is the toxicity mechanism-based or compound-specific?
  - Is the safety signal species-specific or translatable to humans?
```

### Hypothesis Pitfalls to Avoid

```
1. UNFALSIFIABLE HYPOTHESES:
   Bad:  "Gene X may play a role in disease Y under certain conditions"
   Good: "Gene X knockdown in cell line Z reduces biomarker W by >30% at 48h"

2. OVERLY BROAD HYPOTHESES:
   Bad:  "Inflammation contributes to cancer"
   Good: "IL-6/STAT3 signaling in tumor-associated macrophages drives PD-L1 expression
          on tumor cells, reducing T-cell-mediated killing in NSCLC"

3. CONFIRMATION BIAS:
   Bad:  Designing experiments that can only confirm your favored hypothesis
   Good: Designing experiments whose outcomes distinguish between competing hypotheses

4. IGNORING THE NULL:
   Bad:  "We don't need a null hypothesis because we know the drug works"
   Good: "H0: The observed effect is due to placebo response / regression to mean /
          natural disease fluctuation"

5. INSUFFICIENT MECHANISM DETAIL:
   Bad:  "Drug X works by reducing inflammation"
   Good: "Drug X inhibits JAK1/JAK2, blocking IL-6 and IFN-gamma signaling in
          synovial fibroblasts, reducing MMP production and joint destruction"

6. CONFUSING CORRELATION WITH CAUSATION:
   Bad:  "Patients with high CRP have worse outcomes, so CRP causes disease progression"
   Good: "H1: CRP is a causal driver via complement activation
          H2: CRP is a bystander marker of underlying inflammation (confounder)"
```

### Evidence Hierarchy for Hypothesis Support

```
Strongest support (can shift hypothesis to Tier 1):
  - Human genetic evidence (GWAS, Mendelian genetics, LOF variants)
  - Randomized clinical trial results
  - Multiple independent replications across labs/cohorts

Strong support (Tier 2):
  - Causal evidence from animal models (genetic + pharmacological)
  - Large observational cohort studies
  - Dose-response relationships in human data

Moderate support (Tier 3):
  - In vitro mechanistic studies (cell lines, primary cells)
  - Small clinical studies (Phase I/II, pilot studies)
  - Single animal model without genetic validation

Weak support (Tier 4):
  - Computational predictions (pathway analysis, AI/ML)
  - Single preprint without peer review
  - Expert opinion, case reports, analogies from related systems
```

---

## Completeness Checklist

- [ ] Phenomenon clearly defined with variables identified
- [ ] >=10 relevant publications retrieved and synthesized
- [ ] Knowledge gaps and contradictions identified
- [ ] 3-5 competing hypotheses formulated with distinct mechanisms
- [ ] Each hypothesis scored on all 5 quality dimensions
- [ ] Hypotheses ranked by composite score
- [ ] >=2 critical experiments designed per top hypothesis
- [ ] Controls and expected outcomes specified
- [ ] Testable predictions with measurable endpoints defined
- [ ] Decision tree for hypothesis selection provided
- [ ] Evidence grades (T1-T4) assigned to supporting data
- [ ] Report file generated with all sections complete
