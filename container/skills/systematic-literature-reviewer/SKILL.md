---
name: systematic-literature-reviewer
description: Systematic literature review specialist using PRISMA methodology. PICO question formulation, multi-database search strategy, study screening, quality assessment (Cochrane ROB, Newcastle-Ottawa, AMSTAR 2, QUADAS-2), evidence synthesis, forest plot interpretation, meta-analysis. Use when user mentions systematic review, literature review, PRISMA, meta-analysis, evidence synthesis, PICO, Cochrane, risk of bias, scoping review, narrative review, or evidence-based review.
---

# Systematic Literature Reviewer

Conducts rigorous evidence reviews following PRISMA 2020 methodology. Multi-database search, study screening, quality assessment, and evidence synthesis.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_systematic_review_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill
- Individual clinical trial data analysis → use `clinical-trial-analyst`
- Drug safety signal detection and pharmacovigilance → use `pharmacovigilance-specialist`
- Clinical study report writing (ICH-E3) → use `clinical-report-writer`
- Statistical modeling and meta-analysis computation → use `statistical-modeling`
- Regulatory submission strategy → use `fda-consultant`
- Deep research on a single topic without PRISMA rigor → use `literature-deep-research`

## Cross-Reference: Other Skills

- **Clinical trial data** → use clinical-trial-analyst skill
- **Drug safety literature** → use pharmacovigilance-specialist skill
- **Preprint screening** → use this skill (covers bioRxiv/medRxiv)
- **Clinical report writing (CSR, case reports)** → use clinical-report-writer skill

## Available MCP Tools

### `mcp__pubmed__pubmed_articles`

| Method | Review use |
|--------|-----------|
| `search_keywords` | Initial scoping search |
| `search_advanced` | Structured search with journal, date, author filters |
| `get_article_metadata` | Full article details (abstract, authors, journal, MeSH) |

### `mcp__biorxiv__biorxiv_info`

| Method | Review use |
|--------|-----------|
| `search_preprints` | Search bioRxiv/medRxiv preprints |
| `get_preprint_details` | Full preprint metadata |
| `get_categories` | Browse bioRxiv/medRxiv subject categories |
| `search_published_preprints` | Find preprints that became peer-reviewed publications |

### `mcp__ctgov__ct_gov_studies`

| Method | Review use |
|--------|-----------|
| `search` | Find registered trials (completed with results) |
| `get` | Full trial record including results |

### `mcp__opentargets__opentargets_info`

| Method | Review use |
|--------|-----------|
| `get_target_disease_associations` | Evidence landscape for target-disease pair |
| `get_disease_details` | Known therapeutics, disease ontology |

### `mcp__pubchem__pubchem`

| Method | Review use |
|--------|-----------|
| `get_patent_ids` | Patent literature for IP-sensitive reviews |

### `mcp__openalex__openalex_data`

| Method | Review use |
|--------|-----------|
| `search_works` | Complementary search coverage beyond PubMed; retrieve citation counts and open access status |
| `get_work` | Verify citation metadata and open access availability for included studies |
| `search_authors` | Identify prolific authors in the review topic for completeness checks |
| `get_author` | Author publication track record and citation metrics |
| `get_cited_by` | Citation network expansion — find papers citing key included studies |
| `get_works_by_author` | Retrieve an author's full publication list to catch missed relevant studies |
| `search_institutions` | Identify leading research institutions for geographic coverage assessment |

**Usage note:** Use OpenAlex to supplement PubMed search coverage, verify open access status of included studies, and expand the citation network during the screening phase. Citation counts from OpenAlex help prioritize highly-cited studies during full-text review.

---

## PRISMA 2020 Workflow

### Phase 1: Question Formulation (PICO)

| Component | Definition | Example |
|-----------|-----------|---------|
| **P**opulation | Patient group or condition | Adults with type 2 diabetes |
| **I**ntervention | Treatment under review | SGLT2 inhibitors |
| **C**omparator | Alternative or control | Placebo or standard care |
| **O**utcome | Primary endpoint | Cardiovascular mortality |

For diagnostic reviews use **PIRD**: Population, Index test, Reference standard, Diagnosis.

For prognostic reviews use **PICOTS**: add Time and Setting.

### Phase 2: Search Strategy

#### Database Selection

| Database | Strength | MCP Tool |
|----------|----------|----------|
| **PubMed/MEDLINE** | Biomedical, MeSH indexing | `mcp__pubmed__pubmed_articles` |
| **bioRxiv/medRxiv** | Preprints (emerging evidence) | `mcp__biorxiv__biorxiv_info` |
| **ClinicalTrials.gov** | Registered trial results | `mcp__ctgov__ct_gov_studies` |

#### Search Construction

```
1. Identify key concepts from PICO (typically 3-4 concepts)

2. For each concept, build search blocks:
   - MeSH terms / controlled vocabulary
   - Free-text synonyms with truncation
   - Combine within-block with OR
   - Combine between-blocks with AND

3. Example PubMed search:
   mcp__pubmed__pubmed_articles(method: "search_advanced",
     term: "(SGLT2 inhibitor OR empagliflozin OR dapagliflozin OR canagliflozin) AND (cardiovascular mortality OR MACE OR heart failure) AND (randomized controlled trial OR meta-analysis)",
     start_date: "2015/01/01",
     num_results: 100)

4. Parallel preprint search:
   mcp__biorxiv__biorxiv_info(method: "search_preprints",
     query: "SGLT2 inhibitor cardiovascular",
     server: "medrxiv",
     date_from: "2023-01-01",
     limit: 30)

5. Trial search:
   mcp__ctgov__ct_gov_studies(method: "search",
     intervention: "SGLT2 inhibitor",
     condition: "cardiovascular",
     status: "completed",
     phase: "PHASE3")
```

### Phase 3: Screening

#### Title/Abstract Screening Criteria

| Include | Exclude |
|---------|---------|
| Matches PICO components | Wrong population (pediatric if adult review) |
| Study type matches protocol | Wrong intervention |
| Language matches (or has translation) | Animal studies (if human review) |
| Publication date in range | Conference abstracts without full data |

#### Full-Text Screening

```
For each included article:
  mcp__pubmed__pubmed_articles(method: "get_article_metadata", pmid: "PMID")
  → Full abstract, MeSH terms, publication type

  Apply inclusion/exclusion criteria to full text
  Document reason for exclusion
```

### Phase 4: Quality Assessment

#### Study Design → Assessment Tool

| Study Design | Tool | Domains |
|-------------|------|---------|
| **RCT** | Cochrane RoB 2.0 | Randomization, deviations, missing data, measurement, selection |
| **Observational cohort** | Newcastle-Ottawa Scale | Selection (4★), comparability (2★), outcome (3★) |
| **Diagnostic** | QUADAS-2 | Patient selection, index test, reference standard, flow/timing |
| **Systematic review** | AMSTAR 2 | Protocol, search, selection, ROB, synthesis, publication bias |
| **Case series** | JBI Critical Appraisal | Inclusion, measurement, analysis, confounding |

#### Cochrane Risk of Bias 2.0 (RCTs)

| Domain | Key Questions | Judgment |
|--------|--------------|----------|
| **D1: Randomization** | Was allocation sequence random? Concealed? Baseline balance? | Low / Some concerns / High |
| **D2: Deviations** | Were participants/personnel aware of assignment? Appropriate analysis? | Low / Some concerns / High |
| **D3: Missing data** | Was outcome data complete? Were dropouts balanced? | Low / Some concerns / High |
| **D4: Measurement** | Was outcome assessment blinded? Was the measure appropriate? | Low / Some concerns / High |
| **D5: Selection** | Was analysis pre-specified? Multiple outcomes selectively reported? | Low / Some concerns / High |
| **Overall** | Lowest domain judgment applies | Low / Some concerns / High |

#### Newcastle-Ottawa Scale (Observational)

| Category | Maximum Stars | Assessment |
|----------|-------------|------------|
| **Selection** | ★★★★ | Representativeness, selection of non-exposed, ascertainment, no outcome at start |
| **Comparability** | ★★ | Controls for most important factor + additional factor |
| **Outcome** | ★★★ | Assessment method, follow-up length, adequacy of follow-up |
| **Total** | 9★ | ≥7 = good quality, 5-6 = fair, <5 = poor |

### Phase 5: Data Extraction

| Data Element | Details |
|-------------|---------|
| Study ID | First author, year, journal |
| Design | RCT, cohort, case-control, cross-sectional |
| Population | N, age, sex, condition severity, setting |
| Intervention | Drug, dose, duration, comparator |
| Outcomes | Primary, secondary, safety outcomes |
| Results | Effect size, CI, p-value, NNT/NNH |
| Quality | ROB judgment per domain |

### Phase 6: Evidence Synthesis

#### Narrative Synthesis

When studies are too heterogeneous for meta-analysis:
- Group by outcome, intervention, population
- Describe patterns of direction and magnitude
- Explain heterogeneity (clinical, methodological, statistical)

#### Quantitative Synthesis (Meta-Analysis)

| Parameter | Description |
|-----------|------------|
| **Effect measure** | OR/RR (binary), MD/SMD (continuous), HR (time-to-event) |
| **Model** | Fixed-effect (homogeneous studies) or random-effects (heterogeneous) |
| **Heterogeneity** | I² (0-100%), Cochran's Q test, tau² |
| **Publication bias** | Funnel plot asymmetry, Egger's test |
| **Subgroup analysis** | Pre-specified subgroups only |
| **Sensitivity analysis** | Leave-one-out, quality-restricted, fixed vs random |

#### I² Interpretation

| I² Value | Heterogeneity | Interpretation |
|----------|--------------|----------------|
| 0-25% | Low | Studies are consistent |
| 25-50% | Moderate | Some variation |
| 50-75% | Substantial | Consider sources of heterogeneity |
| 75-100% | Considerable | Meta-analysis may not be appropriate |

---

## GRADE Evidence Assessment

### Certainty of Evidence

| Level | Definition | Starting Point |
|-------|-----------|---------------|
| **High** | Very confident effect is close to estimate | RCTs start here |
| **Moderate** | Moderately confident; true effect likely close | |
| **Low** | Limited confidence; true effect may differ | Observational start here |
| **Very Low** | Very little confidence | |

### Downgrade Factors (-1 or -2 per factor)

| Factor | Downgrade When |
|--------|---------------|
| **Risk of bias** | Most studies at high risk |
| **Inconsistency** | I² >50%, conflicting directions |
| **Indirectness** | Population, intervention, or outcome differs from question |
| **Imprecision** | Wide CI crossing clinically important threshold, small sample |
| **Publication bias** | Funnel plot asymmetry, small-study effects |

### Upgrade Factors (+1 per factor, observational only)

| Factor | Upgrade When |
|--------|-------------|
| **Large effect** | RR >2 or <0.5 with no plausible confounding |
| **Dose-response** | Clear gradient |
| **Residual confounding** | Would reduce effect (conservative bias) |

---

## Review Types Decision Tree

```
What is the goal?
├── Answer a focused clinical question → Systematic Review
│   ├── Enough homogeneous studies? → Meta-Analysis
│   └── Too heterogeneous? → Narrative Synthesis
├── Map evidence landscape → Scoping Review
├── Synthesize qualitative evidence → Qualitative Synthesis
├── Rapid evidence for urgent decision → Rapid Review
└── Summarize for non-specialists → Narrative Review
```

---

## Multi-Agent Workflow Examples

**"Systematic review of GLP-1 agonists for weight loss"**
1. Systematic Literature Reviewer → PRISMA protocol, multi-database search, screening, ROB assessment, GRADE
2. Clinical Trial Analyst → ClinicalTrials.gov completed trials with results
3. Pharmacovigilance Specialist → Safety data synthesis across the class

**"Evidence synthesis for regulatory submission (CER/CSR)"**
1. Systematic Literature Reviewer → PRISMA-compliant search and appraisal
2. Clinical Report Writer → ICH-E3 clinical study report formatting
3. MDR 745 Consultant → EU CER requirements for the literature review section

## Completeness Checklist
- [ ] PICO/PIRD question clearly formulated
- [ ] Search strategy constructed with MeSH terms and free-text synonyms
- [ ] Multiple databases searched (PubMed, bioRxiv/medRxiv, ClinicalTrials.gov)
- [ ] Screening criteria applied with exclusion reasons documented
- [ ] Quality assessment completed using appropriate tool (RoB 2.0, NOS, QUADAS-2)
- [ ] Data extraction table populated for all included studies
- [ ] Evidence synthesis performed (narrative or quantitative)
- [ ] Heterogeneity assessed and explained (I-squared, subgroup analysis)
- [ ] GRADE certainty of evidence rated for each outcome
- [ ] PRISMA flow diagram counts verified (identified, screened, included)
