---
name: peer-review
description: Structured scientific manuscript and grant proposal review following journal reviewer standards. Performs section-by-section assessment (abstract, introduction, methods, results, discussion), evaluates methodological and statistical rigor, checks reproducibility and transparency, assesses figure quality and data integrity, evaluates ethical compliance, and generates structured reviewer reports with major/minor comments. Also includes ScholarEval framework for scoring across 8 dimensions. Use when asked to review a manuscript, evaluate a paper, assess a grant proposal, provide reviewer feedback, or critique scientific work.
---

# Peer Review

Provides structured manuscript and grant proposal review following journal reviewer standards. Generates detailed, actionable reviewer reports with scored assessments across multiple quality dimensions.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_peer_review_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Writing a manuscript from scratch → use `scientific-writing`
- Systematic evidence synthesis or meta-analysis → use `systematic-literature-reviewer`
- Statistical methodology design or sample size calculation → use `scientific-critical-thinking`
- Clinical study report writing (ICH-E3) → use `clinical-report-writer`
- Grant proposal writing or drafting → use `research-grants`
- Hypothesis generation or evaluation → use `hypothesis-generation`
- Deep literature search on a single topic → use `literature-deep-research`

## Cross-Reference: Other Skills

- **Writing a manuscript** → use scientific-writing skill
- **Systematic evidence synthesis** → use systematic-literature-reviewer skill
- **Statistical methodology assessment** → use scientific-critical-thinking skill
- **Clinical report writing** → use clinical-report-writer skill
- **Grant proposal writing** → use research-grants skill
- **Hypothesis evaluation** → use hypothesis-generation skill

## Available MCP Tools

### `mcp__pubmed__pubmed_data`

| Method | Review use |
|--------|-----------|
| `search_keywords` | Verify cited references exist and are accurate |
| `search_advanced` | Check novelty — search for prior work on same topic |
| `get_article_metadata` | Retrieve full citation details for cross-checking |

### `mcp__biorxiv__biorxiv_data`

| Method | Review use |
|--------|-----------|
| `search_preprints` | Check for related preprints not cited |
| `get_preprint_details` | Verify preprint claims and publication status |

### `mcp__ctgov__ctgov_data`

| Method | Review use |
|--------|-----------|
| `search` | Verify clinical trial registrations cited in manuscript |
| `get` | Cross-check reported methods/results against registered protocol |

### `mcp__opentargets__opentargets_data`

| Method | Review use |
|--------|-----------|
| `get_target_disease_associations` | Validate biological target claims |
| `get_disease_details` | Verify disease context and known therapeutics |

### `mcp__openalex__openalex_data`

| Method | Review use |
|--------|-----------|
| `search_works` | Check novelty — search for prior work with citation impact data |
| `get_work` | Verify citation metadata for referenced papers by DOI or PMID |
| `search_authors` | Assess author track record and publication history |
| `get_author` | Author citation metrics, h-index proxy, and institutional affiliation |
| `get_cited_by` | Check citation impact of key referenced papers |
| `get_works_by_author` | Review author's publication record for expertise assessment |

**Usage note:** Use OpenAlex to assess the citation impact of papers referenced in the manuscript, verify author track records and institutional affiliations, and check whether the manuscript's claims of novelty hold up against the broader literature indexed in OpenAlex.

---

## Review Workflow — 7 Stages

### Stage 1: Initial Assessment

Evaluate the manuscript at a high level before diving into sections.

| Criterion | Key Questions |
|-----------|---------------|
| **Scope** | Does the work fall within the journal's scope and audience? |
| **Novelty** | Does this advance the field beyond existing literature? Is it incremental or transformative? |
| **Significance** | What is the potential impact on the field? Does it address an important question? |
| **Appropriate venue** | Is this the right journal/conference for the work's quality and scope? |
| **Ethical overview** | Any immediate red flags (data fabrication, plagiarism, dual submission)? |
| **Competing work** | Has similar work been published or posted as a preprint recently? |

```
Novelty verification:
  mcp__pubmed__pubmed_data(method: "search_advanced",
    term: "[key findings from manuscript]",
    start_date: "[5 years prior]",
    num_results: 20)

  mcp__biorxiv__biorxiv_data(method: "search_preprints",
    query: "[manuscript topic and key claims]",
    date_from: "[2 years prior]",
    limit: 20)
```

### Stage 2: Section-by-Section Review

#### Abstract Assessment

| Criterion | What to Check |
|-----------|---------------|
| **Structure** | Background, objective, methods, results, conclusion all present? |
| **Accuracy** | Does the abstract accurately reflect the full manuscript? |
| **Data reporting** | Key quantitative results included (effect sizes, p-values, confidence intervals)? |
| **Conclusions** | Supported by the reported results? Not overstated? |
| **Word count** | Within journal guidelines? |
| **Keywords** | Appropriate, specific, useful for indexing? |

Common deficiencies:
- Conclusions extend beyond what data support
- Missing quantitative results (only qualitative statements)
- Discrepancies between abstract and body text numbers
- Selective reporting of only positive findings

#### Introduction Assessment

| Criterion | What to Check |
|-----------|---------------|
| **Background adequacy** | Sufficient context for the reader to understand the problem? |
| **Literature coverage** | Key prior work cited? Any major omissions? |
| **Knowledge gap** | Clearly articulated gap or unresolved question? |
| **Specific aims** | Hypotheses or objectives stated explicitly? |
| **Logical flow** | Does the narrative progress logically from broad context to specific question? |
| **Proportionality** | Appropriate length — not a full literature review? |

```
Reference verification:
  For each key claim in the introduction, verify the cited reference:
  mcp__pubmed__pubmed_data(method: "get_article_metadata", pmid: "[PMID]")
  → Does the cited paper actually support the claim made?
```

#### Methods Assessment

| Criterion | What to Check |
|-----------|---------------|
| **Study design** | Clearly described? Appropriate for the research question? |
| **Population/samples** | Inclusion/exclusion criteria? Sample size justification? |
| **Interventions/exposures** | Fully described? Reproducible by another lab? |
| **Controls** | Appropriate positive/negative controls included? |
| **Randomization** | Method described? Allocation concealment? |
| **Blinding** | Who was blinded? How was blinding maintained? |
| **Outcome measures** | Primary/secondary endpoints pre-specified? Validated measures? |
| **Statistical plan** | Tests named? Assumptions checked? Multiple comparisons addressed? |
| **Ethical approvals** | IRB/IACUC numbers provided? Informed consent described? |
| **Reproducibility** | Enough detail for independent replication? |

Critical red flags:
- Post-hoc endpoint changes without acknowledgment
- Missing sample size justification
- Inappropriate statistical tests for data type
- No mention of ethical approval for human/animal research
- Vague descriptions ("standard methods were used")

#### Results Assessment

| Criterion | What to Check |
|-----------|---------------|
| **Completeness** | All methods described yield corresponding results? |
| **Data presentation** | Effect sizes with confidence intervals, not just p-values? |
| **Statistical reporting** | Test statistic, degrees of freedom, exact p-values? |
| **Consistency** | Numbers match between text, tables, and figures? |
| **Negative results** | Non-significant findings reported, not buried? |
| **All participants** | Missing data, dropouts, exclusions accounted for? |
| **Subgroup analyses** | Pre-specified or exploratory? Interaction tests used? |

Common deficiencies:
- "Data not shown" for key analyses
- p-value without effect size or confidence interval
- Inconsistent N values across analyses
- Selective reporting of significant results only
- Inappropriate use of bar plots for continuous data

#### Discussion Assessment

| Criterion | What to Check |
|-----------|---------------|
| **Summary** | Key findings restated without simply repeating results? |
| **Interpretation** | Results placed in context of existing literature? |
| **Novelty claim** | What is new? How does this advance the field? |
| **Limitations** | Acknowledged honestly and specifically? |
| **Alternative explanations** | Considered for key findings? |
| **Generalizability** | Population and setting limitations discussed? |
| **Clinical/practical implications** | If applicable, are they stated appropriately? |
| **Future directions** | Specific, actionable next steps? |
| **Overstatement** | Claims proportional to the evidence? Causal language appropriate? |

Watch for:
- "First study to show..." without adequate literature search
- Causal claims from observational data
- Downplaying or ignoring limitations
- Overgeneralization beyond study population
- Ignoring contradictory published evidence

#### References Assessment

| Criterion | What to Check |
|-----------|---------------|
| **Adequacy** | Sufficient references for claims made? |
| **Currency** | Recent literature included (last 3-5 years)? |
| **Balance** | Not dominated by single research group or self-citations? |
| **Accuracy** | Citations support the claims attributed to them? |
| **Completeness** | Key landmark papers in the field included? |
| **Format** | Consistent with journal requirements? |

```
Self-citation analysis:
  Count references where any manuscript author is also a reference author.
  Flag if self-citation rate exceeds 15-20% of total references.
```

### Stage 3: Methodological and Statistical Rigor

| Domain | Assessment Questions |
|--------|---------------------|
| **Study design adequacy** | Is the design appropriate for the research question? Are there fundamental design flaws? |
| **Statistical test appropriateness** | Do the tests match the data type (continuous/categorical), distribution, and independence assumptions? |
| **Multiple comparisons** | Were corrections applied (Bonferroni, Benjamini-Hochberg, FDR)? How many comparisons were made? |
| **Effect sizes** | Reported alongside p-values? Clinically/practically meaningful? |
| **Statistical power** | Was a power analysis performed? Is the study adequately powered for the primary endpoint? |
| **Missing data handling** | Method described (listwise deletion, imputation, mixed models)? Sensitivity analysis? |
| **Computational methods** | Software versions stated? Algorithms described? Parameters reported? Code available? |
| **Sensitivity analyses** | Were key findings tested for robustness under different assumptions? |

#### Common Statistical Errors to Flag

| Error | Description |
|-------|-------------|
| **p-hacking** | Multiple analyses run until significance found, without correction |
| **HARKing** | Hypothesizing After Results are Known — presenting post-hoc as a priori |
| **Garden of forking paths** | Many undisclosed analytical choices |
| **Pseudoreplication** | Non-independent observations treated as independent |
| **Inappropriate parametric tests** | Parametric tests on non-normal data without justification |
| **Dichotomizing continuous variables** | Splitting continuous variables at arbitrary cutpoints |
| **Ignoring clustering** | Failing to account for hierarchical/nested data structure |
| **Ecological fallacy** | Drawing individual-level conclusions from group-level data |
| **Immortal time bias** | Time periods in cohort studies where outcome cannot occur |
| **Baseline imbalance** | Testing baseline differences with p-values in RCTs |

### Stage 4: Reproducibility and Transparency

#### Data and Code Availability

| Criterion | Rating |
|-----------|--------|
| **Data availability statement** | Present / Absent / Inadequate |
| **Raw data deposited** | Public repository with accession number / Available on request / Not available |
| **Analysis code shared** | GitHub/Zenodo with DOI / Available on request / Not available |
| **Materials availability** | Key reagents, cell lines, antibodies identified with RRID? |
| **Pre-registration** | Registered (with link) / Not registered / Not applicable |

#### Reporting Standard Compliance

| Standard | Applies To | Key Elements to Verify |
|----------|-----------|----------------------|
| **CONSORT** | Randomized controlled trials | Flow diagram, randomization, blinding, ITT analysis |
| **STROBE** | Observational studies | Study design stated, bias handling, participant flow |
| **PRISMA** | Systematic reviews & meta-analyses | Search strategy, inclusion criteria, PRISMA flow, ROB assessment |
| **ARRIVE** | Animal research | Species, strain, housing, sample size justification, randomization |
| **CARE** | Case reports | Timeline, diagnostic assessment, therapeutic intervention, follow-up |
| **MDAR** | General life sciences | Mandatory fields covering data, code, materials, protocols |
| **TRIPOD** | Prediction models | Model development, validation, performance metrics |
| **STARD** | Diagnostic accuracy | Index test, reference standard, flow diagram |
| **SPIRIT** | Trial protocols | Objectives, design, participants, interventions, outcomes |
| **MIAME** | Microarray experiments | Experimental design, samples, hybridizations, measurements, normalization |

```
For clinical trials, verify registration:
  mcp__ctgov__ctgov_data(method: "search",
    intervention: "[intervention from manuscript]",
    condition: "[condition from manuscript]")
  → Does the registered protocol match the reported methods?
  → Were primary endpoints changed after registration?
```

### Stage 5: Figure and Data Presentation

| Criterion | What to Check |
|-----------|---------------|
| **Quality** | Resolution sufficient? Legible at print size? |
| **Integrity** | Any signs of image splicing, duplication, or manipulation? |
| **Appropriate visualization** | Bar plots for means only (not distributions)? Violin/box for distributions? |
| **Colorblind accessibility** | Colorblind-friendly palette? Not relying solely on red/green distinction? |
| **Legends** | Self-contained? All symbols, abbreviations, statistical annotations defined? |
| **Statistical annotations** | Significance indicators defined? Exact p-values preferred over stars? |
| **Axes** | Clearly labeled with units? Appropriate scale (log if needed)? Not truncated misleadingly? |
| **Error bars** | Defined (SD, SEM, CI)? SEM appropriate or misleadingly small? |
| **Individual data points** | Shown for small N? Overlaid on summary statistics? |
| **Sample sizes** | N indicated for each group/condition? |

#### Figure Red Flags

- Duplicated gel bands or microscopy images across conditions
- Unusually clean or uniform data distributions
- Inconsistent background between image panels
- Error bars smaller than expected for sample size
- Bar plots hiding bimodal or skewed distributions
- Axis breaks that exaggerate small differences
- 3D plots that distort proportions

### Stage 6: Ethical Considerations

| Domain | What to Verify |
|--------|---------------|
| **IRB/IACUC approval** | Approval number stated? Institution named? |
| **Informed consent** | Described? Written vs verbal? Special populations (children, incapacitated)? |
| **Clinical trial registration** | Registered before enrollment? NCT number or equivalent provided? |
| **Conflicts of interest** | Declared? Funding sources could introduce bias? |
| **Authorship** | All authors meet ICMJE criteria? Ghost or gift authorship concerns? |
| **Data integrity** | Any patterns suggesting fabrication or falsification? |
| **Dual/prior publication** | Is this a duplicate submission? Overlap with prior publications? |
| **Patient privacy** | De-identification adequate? Identifiable photos with consent? |
| **Biosafety** | BSL requirements addressed? Dual-use research of concern? |
| **Cultural sensitivity** | Appropriate framing of vulnerable populations? |

#### ICMJE Authorship Criteria

All four criteria must be met:
1. Substantial contributions to conception/design OR data acquisition/analysis
2. Drafting the article OR revising it critically for intellectual content
3. Final approval of the version to be published
4. Agreement to be accountable for all aspects of the work

### Stage 7: Writing Quality

| Criterion | What to Check |
|-----------|---------------|
| **Clarity** | Can a reader in the field understand each section on first reading? |
| **Conciseness** | Unnecessary repetition? Verbose passages? |
| **Grammar and syntax** | Grammatical errors? Awkward constructions? |
| **Logical flow** | Smooth transitions between paragraphs and sections? |
| **Jargon** | Excessive use of unexplained acronyms or specialized terms? |
| **Active voice** | Appropriate use of active voice? Excessive passive voice? |
| **Tense consistency** | Methods/results in past tense? General knowledge in present tense? |
| **Internal consistency** | Terminology used consistently throughout? Same abbreviation usage? |
| **Hedging** | Appropriate use of uncertainty language? Not overclaiming? |

---

## ScholarEval Scoring Framework

Score each dimension on a 1-5 scale. Sum for overall score (8-40).

### Scoring Rubric

| Dimension | 1 (Poor) | 2 (Below Average) | 3 (Adequate) | 4 (Good) | 5 (Excellent) |
|-----------|----------|-------------------|--------------|----------|---------------|
| **Problem Formulation** | Unclear, trivial, or poorly scoped question | Vague question or limited significance | Clear question but limited novelty | Well-defined, significant question | Clear, significant, well-scoped question advancing the field |
| **Literature Review** | Missing or severely inadequate | Major gaps in coverage | Adequate but missing recent work | Comprehensive, mostly current | Comprehensive, current, identifies clear gap |
| **Methodology** | Fundamentally flawed design | Significant weaknesses | Appropriate but with notable limitations | Rigorous with minor issues | Appropriate, rigorous, fully reproducible |
| **Data Collection** | Inadequate sample, no quality controls | Weak sampling or quality issues | Adequate sample, basic controls | Good sample size, appropriate controls | Adequate sample, quality controls, complete reporting |
| **Analysis** | Incorrect or absent statistical analysis | Inappropriate tests or major errors | Correct basic statistics | Appropriate tests, well-executed | Correct statistics, robust sensitivity analyses |
| **Results** | Results do not support conclusions | Incomplete reporting, selective presentation | Adequate presentation with gaps | Clear presentation, mostly complete | Clear, complete presentation fully supported by data |
| **Writing** | Incomprehensible or severely disorganized | Poor organization, frequent errors | Adequate clarity with some issues | Well-written with minor issues | Clear, organized, appropriate terminology |
| **Citations** | Absent or severely inadequate | Major omissions or heavily biased | Adequate but with gaps | Good coverage, mostly balanced | Adequate, balanced, properly formatted |

### Overall Score Interpretation

| Score Range | Decision | Description |
|-------------|----------|-------------|
| **35-40** | Accept / Accept with minor revisions | Excellent work with minimal issues. Publication-ready or near-ready. |
| **28-34** | Minor revisions | Sound work requiring targeted improvements. No fundamental flaws. |
| **20-27** | Major revisions | Significant issues that must be addressed but the work has potential. |
| **12-19** | Reject with resubmission encouraged | Fundamental problems but the research question has merit. |
| **8-11** | Reject | Fatally flawed design, analysis, or interpretation. Not suitable. |

---

## Reviewer Report Output Format

Generate the following structured report for every review.

```
## Summary Statement
[2-3 sentence overview of the work and its significance]

## Recommendation
[Accept / Minor Revisions / Major Revisions / Reject]

## Overall Score: [X/40]

| Dimension | Score | Comments |
|-----------|-------|----------|
| Problem Formulation | X/5 | [Brief justification] |
| Literature Review | X/5 | [Brief justification] |
| Methodology | X/5 | [Brief justification] |
| Data Collection | X/5 | [Brief justification] |
| Analysis | X/5 | [Brief justification] |
| Results | X/5 | [Brief justification] |
| Writing | X/5 | [Brief justification] |
| Citations | X/5 | [Brief justification] |

## Major Comments (must be addressed)
1. [Comment with specific section/line reference]
   - Location: [Section X, paragraph Y / Figure Z / Table N]
   - Issue: [Clear description of the problem]
   - Suggestion: [Constructive recommendation for resolution]
2. ...

## Minor Comments (should be addressed)
1. [Comment with specific section/line reference]
   - Location: [Section X, paragraph Y / Line N]
   - Issue: [Description]
   - Suggestion: [Recommendation]
2. ...

## Questions for Authors
1. [Clarification needed — specific and answerable]
2. ...

## Confidential Comments to Editor
[Assessment of novelty, significance, suitability for journal]
[Any concerns about ethics, data integrity, or competing interests]
[Recommendation with rationale not shared with authors]
```

### Comment Classification Guide

| Category | Major Comment | Minor Comment |
|----------|--------------|---------------|
| **Design flaw** | Missing control group, inadequate blinding | Suboptimal randomization description |
| **Statistical error** | Wrong test, no multiple comparison correction | Missing exact p-values |
| **Missing data** | Key results not reported | Supplementary data could enhance |
| **Interpretation** | Conclusions not supported by data | Slight overstatement |
| **Ethical concern** | Missing IRB approval, undeclared COI | Minor consent language issue |
| **Presentation** | Figure integrity concerns | Formatting inconsistencies |
| **Writing** | Sections missing or incomprehensible | Grammar or style issues |

---

## Grant Proposal Review

### NIH Review Criteria (1-9 Scale)

For NIH-style grant reviews, score each criterion on a 1-9 scale (1 = exceptional, 9 = poor).

| Criterion | Score | Assessment Questions |
|-----------|-------|---------------------|
| **Significance** | 1-9 | Does the project address an important problem? Will it improve scientific knowledge or clinical practice? |
| **Investigator(s)** | 1-9 | Are the PD/PIs and key personnel qualified? Do they have appropriate experience and training? |
| **Innovation** | 1-9 | Does the project employ novel concepts, approaches, or technologies? Is it a refinement of existing methods? |
| **Approach** | 1-9 | Are the strategy, methodology, and analyses well-reasoned and appropriate? Are potential problems considered? |
| **Environment** | 1-9 | Will the scientific environment contribute to the project? Are institutional support and resources adequate? |

#### NIH Overall Impact Score

| Score Range | Description |
|-------------|-------------|
| **1-3** | High impact — addresses a critical need with excellent approach |
| **4-6** | Moderate impact — sound science with some weaknesses |
| **7-9** | Low impact — significant weaknesses undermine potential |

#### NIH Review Additional Considerations

| Factor | What to Assess |
|--------|---------------|
| **Protections for human subjects** | Risk/benefit, informed consent, vulnerable populations, data safety |
| **Vertebrate animals** | Justification, species, minimization of pain/distress |
| **Biohazards** | Adequate biosafety measures |
| **Budget** | Appropriate and well-justified for scope of work |
| **Timeline** | Realistic milestones? Achievable within funding period? |
| **Rigor and reproducibility** | Scientific premise, rigor of prior research, biological variables |
| **Authentication** | Plans for authenticating key biological and chemical resources |

### NSF Review Criteria

| Criterion | Assessment Questions |
|-----------|---------------------|
| **Intellectual Merit** | What is the potential to advance knowledge? How well conceived and organized is the activity? Is there sufficient access to resources? |
| **Broader Impacts** | What is the potential to benefit society? Does it promote teaching, training, diversity? Will results be broadly disseminated? |

#### NSF Review Format

```
## Intellectual Merit
[Assessment of scientific rigor, novelty, and potential for advancing knowledge]

## Broader Impacts
[Assessment of societal benefit, education, diversity, dissemination]

## Summary Assessment
[Overall evaluation with strengths and weaknesses]

## Rating: [Excellent / Very Good / Good / Fair / Poor]
```

---

## Review Tone and Ethics

### Constructive Review Principles

- **Be specific**: Reference exact sections, figures, tables, or line numbers
- **Be constructive**: Every criticism should include a suggestion for improvement
- **Be respectful**: Critique the work, not the authors; avoid condescending language
- **Be balanced**: Acknowledge strengths alongside weaknesses
- **Be honest**: Do not soften fundamental flaws — clearly state when a study is fatally flawed
- **Be timely**: Prioritize comments by importance; do not bury critical issues among minor points
- **Separate opinion from evidence**: Distinguish "I would prefer..." from "The data do not support..."

### Reviewer Bias Awareness

| Bias Type | Description | Mitigation |
|-----------|-------------|------------|
| **Confirmation bias** | Favoring manuscripts that align with your views | Evaluate methods independently of conclusions |
| **Prestige bias** | Rating higher based on author/institution reputation | Focus on methodology and data quality |
| **Novelty bias** | Preferring flashy results over solid incremental work | Assess rigor equally regardless of novelty |
| **Conservatism bias** | Rejecting work that challenges established paradigms | Evaluate the evidence on its own merits |
| **Scope bias** | Judging outside your expertise area | Explicitly state areas outside your competence |

---

## Specialized Review Considerations

### Clinical Trial Manuscripts

Additional checks for clinical trial reports:
- CONSORT checklist compliance (all 25 items)
- Protocol registration verification via ClinicalTrials.gov
- Primary endpoint matches registered protocol
- ITT vs per-protocol analysis reported
- DSMB mentioned for high-risk interventions
- Adverse event reporting complete

```
Verify trial registration:
  mcp__ctgov__ctgov_data(method: "get", nct_id: "[NCT number from manuscript]")
  → Compare registered primary outcome vs reported primary outcome
  → Check if endpoints were changed after enrollment began
  → Verify sample size matches registration
```

### Systematic Review and Meta-Analysis Manuscripts

Additional checks:
- PRISMA checklist compliance
- Search strategy reproducible
- Study selection process described with flow diagram
- Risk of bias assessment performed
- Heterogeneity assessed (I-squared, Q statistic)
- Publication bias evaluated (funnel plot, Egger's test)
- GRADE evidence certainty rated
- Protocol pre-registered (PROSPERO)

### Basic Science Manuscripts

Additional checks:
- Biological replicates vs technical replicates distinguished
- Antibody validation (RRID numbers)
- Cell line authentication
- Mycoplasma testing
- Blinding during data collection and analysis
- Raw data for key experiments (e.g., full Western blots)

### Computational/Bioinformatics Manuscripts

Additional checks:
- Code availability and documentation
- Software versions and dependencies specified
- Benchmark datasets used for validation
- Computational reproducibility (Docker/Singularity, conda environment)
- Training/test data split for ML models
- Cross-validation strategy appropriate
- Overfitting addressed
- Performance compared to existing methods on same benchmarks

---

## Multi-Agent Workflow Examples

**"Review this manuscript for Nature Communications"**
1. Peer Review → Full 7-stage assessment with ScholarEval scoring
2. Systematic Literature Reviewer → Verify novelty claims against existing literature
3. Scientific Critical Thinking → Deep dive into statistical methodology concerns

**"Evaluate this NIH R01 grant proposal"**
1. Peer Review → NIH 5-criterion scoring with impact assessment
2. Research Grants → Grant structure and budget evaluation
3. Hypothesis Generation → Assess scientific premise and alternative approaches

**"Review this clinical trial manuscript"**
1. Peer Review → Section-by-section review and CONSORT compliance
2. Clinical Report Writer → Verify reporting standards and SAE narrative quality
3. Systematic Literature Reviewer → Check background literature completeness

**"Assess this preprint for our journal club"**
1. Peer Review → Rapid structured assessment with ScholarEval scoring
2. Scientific Critical Thinking → Statistical rigor deep dive
3. Literature Deep Research → Context in broader field developments

---

## Completeness Checklist

- [ ] Initial assessment performed (scope, novelty, significance, venue appropriateness)
- [ ] All manuscript sections reviewed (abstract, introduction, methods, results, discussion, references)
- [ ] Methodological and statistical rigor evaluated with specific concerns identified
- [ ] Reproducibility and transparency assessed (data/code availability, reporting standards)
- [ ] Figures and data presentation examined for quality, integrity, and accessibility
- [ ] Ethical considerations verified (IRB/IACUC, consent, COI, authorship, registration)
- [ ] Writing quality assessed (clarity, conciseness, grammar, logical flow)
- [ ] ScholarEval scores assigned for all 8 dimensions with justification
- [ ] Overall score calculated and mapped to recommendation
- [ ] Major comments include specific section/line references and constructive suggestions
- [ ] Minor comments clearly distinguished from major comments
- [ ] Questions for authors are specific and answerable
- [ ] Confidential comments to editor address novelty, significance, and suitability
- [ ] Novelty verified via MCP tools (PubMed, bioRxiv searches)
- [ ] Clinical trial registration verified if applicable (ClinicalTrials.gov)
- [ ] Grant review criteria applied if reviewing a grant proposal (NIH or NSF)
- [ ] No `[Analyzing...]` placeholders remain in final report
- [ ] Report follows structured output format with all required sections
