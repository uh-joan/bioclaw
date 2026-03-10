---
name: reproducibility-audit
description: Assess the reproducibility and robustness of scientific claims, results, or analyses using an 8-dimension framework (claim traceability, methodological completeness, data availability, code availability, statistical rigor, internal consistency, bias risk, external validity). Performs GRIM/SPRITE tests, red flag detection, and generates scored reproducibility reports (0-100). Inspired by AI Scientist's automated review, Kosmos's traceability requirement, and the reproducibility crisis literature. Use when asked to audit reproducibility, check if results can be replicated, assess data integrity, verify statistical claims, evaluate transparency of methods, detect p-hacking or selective reporting, or review the robustness of scientific findings.
---

# Reproducibility Audit

Assess the reproducibility and robustness of scientific claims, results, or analyses. Applies an 8-dimension scoring framework covering claim traceability, methodological completeness, data availability, code availability, statistical rigor, internal consistency, bias risk, and external validity. Generates quantified reproducibility scores (0-100) with red flag detection, GRIM/SPRITE consistency tests, and actionable recommendations for improving reproducibility.

Distinct from **peer-review** (which evaluates overall paper quality including novelty, significance, and presentation), **scientific-critical-thinking** (which broadly evaluates methodology and logical reasoning), and **meta-cognition** (which audits the reasoning process itself, not the scientific claims). This skill focuses specifically on whether findings can be independently reproduced and whether reported results are internally consistent.

## Report-First Workflow

1. **Create report file immediately**: `[paper/claim]_reproducibility_audit.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update each dimension score as analysis proceeds
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Evaluating overall paper quality, novelty, and significance -> use `peer-review`
- Broad methodology critique and logical fallacy detection -> use `scientific-critical-thinking`
- Auditing your own reasoning process for cognitive biases -> use `meta-cognition`
- Designing experiments or generating hypotheses -> use `hypothesis-generation`
- Building expert consensus on a question -> use `delphi-method`
- Systematic literature review and evidence synthesis -> use `systematic-literature-reviewer`
- Statistical test selection and power analysis -> use `statistical-modeling`
- Writing or improving a manuscript -> use `scientific-writing`

## Cross-Skill Routing

- Statistical methodology questions identified during audit -> `statistical-modeling`
- Bias detection requiring structured evaluation framework -> `scientific-critical-thinking`
- Paper needs full peer review beyond reproducibility -> `peer-review`
- Literature search for replication studies -> `literature-deep-research`
- Clinical trial protocol verification -> `clinical-trial-analyst`
- Drug safety data integrity assessment -> `pharmacovigilance-specialist`
- Genomic data quality and variant calling verification -> `variant-analysis`
- Protein structure data validation -> `protein-structure-retrieval`

---

## Available MCP Tools

### `mcp__pubmed__pubmed_data` (Replication Evidence)

| Method | Reproducibility use |
|--------|-------------------|
| `search_keywords` | Find replication studies, failed replications, contradictory findings |
| `search_advanced` | Search for methodology papers, reproducibility assessments in field |
| `get_article_metadata` | Verify cited references, check retraction status |

### `mcp__biorxiv__biorxiv_data` (Preprint Verification)

| Method | Reproducibility use |
|--------|-------------------|
| `search_preprints` | Find preprint versions for comparison with published |
| `get_preprint_details` | Check for protocol changes between preprint and publication |
| `get_published_version` | Trace preprint-to-publication changes |

### `mcp__ctgov__ctgov_data` (Protocol Verification)

| Method | Reproducibility use |
|--------|-------------------|
| `search` | Find registered protocol for clinical studies |
| `get` | Compare registered protocol vs. published methods (outcome switching detection) |
| `stats` | Assess trial landscape for context on expected results |

### `mcp__opentargets__opentargets_data` (Biological Plausibility)

| Method | Reproducibility use |
|--------|-------------------|
| `get_target_disease_associations` | Verify claimed target-disease associations against aggregated evidence |
| `get_target_details` | Cross-check biological mechanism claims |

### `mcp__chembl__chembl_data` (Compound Data Verification)

| Method | Reproducibility use |
|--------|-------------------|
| `compound_search` | Verify compound identity and properties |
| `get_bioactivity` | Cross-check reported bioactivity values against databases |
| `get_admet` | Verify ADMET properties against published data |

---

## Core Framework: 8-Dimension Reproducibility Assessment

### Dimension 1: Claim Traceability (0-10)

Assess whether every claim can be traced to specific data and analysis.

**Evaluation Criteria:**

| Score | Criteria |
|-------|---------|
| 9-10 | Every claim traced to specific figure, table, or supplementary data; logical chain fully transparent |
| 7-8 | Most claims well-supported; minor gaps in logical chain |
| 5-6 | Some claims supported but others rely on unstated assumptions or missing data |
| 3-4 | Many claims lack direct data support; logical leaps present |
| 1-2 | Most claims unsupported by presented data; significant logical gaps |
| 0 | No traceability; claims appear disconnected from data |

**Traceability Mapping:**
```python
def trace_claims(claims_list):
    """Map each claim to its supporting evidence.

    claims_list: list of dicts with 'claim', 'figure_ref', 'table_ref',
                 'stats_ref', 'data_source', 'logical_chain'
    """
    traced = []
    untraced = []

    for claim in claims_list:
        has_data = bool(claim.get('figure_ref') or claim.get('table_ref'))
        has_stats = bool(claim.get('stats_ref'))
        has_chain = bool(claim.get('logical_chain'))

        support_score = sum([has_data, has_stats, has_chain])

        entry = {
            'claim': claim['claim'],
            'data_support': has_data,
            'statistical_support': has_stats,
            'logical_chain': has_chain,
            'support_level': ['None', 'Weak', 'Moderate', 'Strong'][support_score]
        }

        if support_score >= 2:
            traced.append(entry)
        else:
            untraced.append(entry)

    traceability_score = len(traced) / len(claims_list) * 10 if claims_list else 0
    return {
        'score': round(traceability_score, 1),
        'traced_claims': traced,
        'untraced_claims': untraced,
        'total': len(claims_list),
        'traced_count': len(traced),
        'untraced_count': len(untraced)
    }
```

**Key Questions:**
- Can every claim be traced to a specific figure, table, or data source?
- Is the logical chain from data -> analysis -> interpretation -> conclusion complete?
- Are there claims that appear "out of nowhere" (not supported by presented data)?
- Are the inferential steps between data and conclusion explicitly stated?
- Are alternative interpretations of the data acknowledged?

### Dimension 2: Methodological Completeness (0-10)

Assess whether methods are described in sufficient detail to replicate.

**Evaluation Criteria:**

| Score | Criteria |
|-------|---------|
| 9-10 | Fully detailed protocol; an independent researcher could replicate from description alone |
| 7-8 | Minor gaps (e.g., buffer compositions, incubation times) but core protocol clear |
| 5-6 | Major experimental parameters specified but some steps ambiguous |
| 3-4 | Key parameters missing; replication would require significant assumptions |
| 1-2 | Methods section skeletal; most steps underspecified |
| 0 | No methods or "methods available upon request" |

**Completeness Checklist by Study Type:**

**Wet Lab Studies:**
- [ ] Cell lines/organisms identified with source and passage number
- [ ] Antibodies identified with catalog numbers, RRIDs, dilutions
- [ ] Reagent concentrations, suppliers, lot numbers
- [ ] Equipment make and model
- [ ] Temperature, pH, incubation times
- [ ] Sample sizes and replicates (biological vs. technical)
- [ ] Randomization and blinding procedures
- [ ] Inclusion/exclusion criteria

**Computational Studies:**
- [ ] Software versions and dependencies
- [ ] Algorithm parameters and hyperparameters
- [ ] Random seeds specified
- [ ] Hardware specifications (GPU, memory)
- [ ] Training/validation/test split methodology
- [ ] Data preprocessing steps with exact parameters
- [ ] Feature selection criteria

**Clinical Studies:**
- [ ] Study design (parallel, crossover, etc.)
- [ ] Randomization method (block, stratified, etc.)
- [ ] Blinding (single, double, assessor)
- [ ] Primary and secondary endpoints pre-specified
- [ ] Sample size calculation with assumptions
- [ ] Inclusion/exclusion criteria
- [ ] Intervention details (dose, schedule, route, duration)
- [ ] Concomitant medication rules
- [ ] Statistical analysis plan specified a priori

### Dimension 3: Data Availability (0-10)

Assess accessibility of raw and processed data.

| Score | Criteria |
|-------|---------|
| 9-10 | Raw data in public repository with DOI; data dictionary provided; FAIR compliant |
| 7-8 | Processed data available; raw data available upon reasonable request |
| 5-6 | Summary statistics in supplement; some individual-level data available |
| 3-4 | Only aggregated data in figures/tables; no individual-level data |
| 1-2 | Data "available upon request" with no evidence of sharing |
| 0 | No data availability statement; data not accessible |

**Data Availability Assessment:**
```python
def assess_data_availability(data_info):
    """Score data availability based on accessibility indicators.

    data_info: dict with keys:
        - raw_data_repository: str or None (e.g., 'GEO', 'SRA', 'Zenodo')
        - raw_data_accession: str or None
        - processed_data_available: bool
        - data_dictionary: bool
        - fair_compliant: bool (Findable, Accessible, Interoperable, Reusable)
        - format_standard: bool (uses standard formats like FASTQ, BAM, CSV)
        - upon_request: bool
        - data_statement: bool
    """
    score = 0

    if data_info.get('raw_data_repository') and data_info.get('raw_data_accession'):
        score += 4  # Raw data in public repository
    elif data_info.get('upon_request'):
        score += 1  # Available upon request (weak)

    if data_info.get('processed_data_available'):
        score += 2

    if data_info.get('data_dictionary'):
        score += 1.5

    if data_info.get('fair_compliant'):
        score += 1.5

    if data_info.get('format_standard'):
        score += 1

    return min(10, round(score, 1))
```

### Dimension 4: Code Availability (0-10)

Assess accessibility and usability of analysis code.

| Score | Criteria |
|-------|---------|
| 9-10 | Code in public repo with README, environment file, test suite; runs on available data |
| 7-8 | Code available with documentation; minor modifications needed to run |
| 5-6 | Code available but incomplete documentation; significant effort to run |
| 3-4 | Partial code (key scripts only); no environment specification |
| 1-2 | Code "available upon request" or in supplementary PDF |
| 0 | No code availability; analysis not transparent |

**Code Quality Scoring:** Repository available (+3), README present (+1), environment file (+1.5), test suite (+1.5), runs on data (+2), documentation quality (+0-1). Cap at 10.

### Dimension 5: Statistical Rigor (0-10)

Assess appropriateness and completeness of statistical analyses.

| Score | Criteria |
|-------|---------|
| 9-10 | All tests appropriate; assumptions verified; effect sizes, CIs, and power reported |
| 7-8 | Tests appropriate; effect sizes reported; minor gaps in assumption checking |
| 5-6 | Tests generally appropriate but assumptions not verified; p-values without effect sizes |
| 3-4 | Some inappropriate tests; no effect sizes; inadequate multiple comparison correction |
| 1-2 | Major statistical errors; inappropriate tests for data type |
| 0 | No statistical analysis or fundamentally flawed approach |

**Statistical Rigor Checklist:**

```python
def statistical_rigor_audit(stats_info):
    """Audit statistical methodology for common issues.

    stats_info: dict with keys for each statistical test reported
    """
    issues = []
    score = 10  # Start at max, deduct for problems

    # Check test appropriateness
    if not stats_info.get('tests_appropriate'):
        issues.append("CRITICAL: Statistical tests may be inappropriate for data type")
        score -= 3

    # Check assumptions
    if not stats_info.get('assumptions_tested'):
        issues.append("MAJOR: Statistical assumptions not verified (normality, homoscedasticity)")
        score -= 2

    # Check effect sizes
    if not stats_info.get('effect_sizes_reported'):
        issues.append("MAJOR: Effect sizes not reported (only p-values)")
        score -= 2

    # Check confidence intervals
    if not stats_info.get('confidence_intervals'):
        issues.append("MINOR: Confidence intervals not provided")
        score -= 1

    # Check multiple comparisons
    if stats_info.get('multiple_comparisons_needed') and not stats_info.get('correction_applied'):
        issues.append("CRITICAL: Multiple comparison correction needed but not applied")
        score -= 3

    # Check sample size justification
    if not stats_info.get('power_analysis'):
        issues.append("MAJOR: No sample size justification or power analysis")
        score -= 1.5

    # Check independence
    if not stats_info.get('independence_verified'):
        issues.append("MINOR: Independence of observations not explicitly verified")
        score -= 0.5

    return {
        'score': max(0, round(score, 1)),
        'issues': issues,
        'critical_count': sum(1 for i in issues if i.startswith('CRITICAL')),
        'major_count': sum(1 for i in issues if i.startswith('MAJOR')),
        'minor_count': sum(1 for i in issues if i.startswith('MINOR'))
    }
```

### Dimension 6: Internal Consistency (0-10)

Assess whether reported numbers are self-consistent.

| Score | Criteria |
|-------|---------|
| 9-10 | All numbers consistent across text, figures, and tables; GRIM/SPRITE pass |
| 7-8 | Minor inconsistencies (rounding errors, typos) but no substantive discrepancies |
| 5-6 | Some inconsistencies between text and figures; sample sizes mostly add up |
| 3-4 | Notable discrepancies; some numbers cannot be verified from presented data |
| 1-2 | Major inconsistencies; impossible values present |
| 0 | Pervasive inconsistencies; data integrity in question |

**GRIM Test Implementation:**
```python
import numpy as np

def grim_test(mean, n, decimals=2):
    """Test whether a reported mean is consistent with integer data and sample size.

    The Granularity-Related Inconsistency of Means (GRIM) test checks whether
    a reported mean of integer-valued data (e.g., Likert scale responses) is
    mathematically possible given the sample size.

    Args:
        mean: reported mean value
        n: sample size
        decimals: number of decimal places in reported mean

    Returns:
        dict with test result and details
    """
    # The sum must be an integer for integer-valued data
    total = mean * n
    remainder = total % 1

    # Account for rounding at the specified decimal places
    tolerance = 0.5 * 10**(-decimals)

    is_consistent = remainder < tolerance or remainder > (1 - tolerance)

    return {
        'mean': mean,
        'n': n,
        'implied_sum': total,
        'remainder': remainder,
        'consistent': is_consistent,
        'verdict': 'PASS' if is_consistent else 'FAIL — mean is impossible for integer data with this N'
    }


```

For batch testing, run `grim_test()` in a loop over all reported means and flag any failures. A single GRIM failure does not prove fabrication but warrants investigation. Multiple failures in the same paper raise serious concerns.

**Cross-Check Process:**
- Extract all quantitative values reported in text, figures, and tables
- Compare values that refer to the same measurement across sources
- Flag discrepancies > 10% as CRITICAL, smaller rounding differences as MINOR
- Check that sample sizes add up across subgroups
- Verify that percentages sum to ~100% where expected
- Look for impossible values (negative counts, percentages >100%, p-values >1)

### Dimension 7: Bias Risk Assessment (0-10)

Adapted from the Cochrane Risk of Bias tool (RoB 2).

| Score | Criteria |
|-------|---------|
| 9-10 | Low risk across all bias domains; rigorous design with adequate controls |
| 7-8 | Low risk in most domains; some concerns in 1-2 areas |
| 5-6 | Some concerns in multiple domains but no high-risk areas |
| 3-4 | High risk in 1-2 domains; results should be interpreted cautiously |
| 1-2 | High risk in multiple domains; results may not be reliable |
| 0 | Critical risk; fundamental design flaws undermine all conclusions |

**Bias Domains:**

| Domain | Key Questions | Risk Indicators |
|--------|--------------|-----------------|
| **Selection** | How were subjects/samples selected? Random? Representative? | Convenience sampling, self-selection, unclear recruitment |
| **Performance** | Were groups treated equally except for intervention? | Unblinded, co-interventions, contamination |
| **Detection** | Were outcomes assessed blindly? Objective measures? | Unblinded assessment, subjective endpoints without blinding |
| **Attrition** | Were dropouts handled appropriately? ITT analysis? | High dropout (>20%), differential attrition, per-protocol only |
| **Reporting** | Were all pre-specified outcomes reported? | Missing outcomes, outcome switching, selective reporting |
| **Measurement** | Were measurement tools validated? Reliable? | Unvalidated instruments, single measurement, observer bias |
| **Confounding** | Were confounders identified and controlled? | No adjustment, unmeasured confounders, residual confounding |

**Bias Risk Scoring:**
Rate each domain as: `low` (0), `some_concerns` (1), `high` (2), or `critical` (3). Sum risk values across domains, normalize to 0-10 scale: `score = (1 - total_risk / (3 * n_domains)) * 10`. Overall risk determination: any `critical` domain = Critical risk; 2+ `high` domains = High risk; 1 `high` or 3+ `some_concerns` = Some concerns; otherwise Low risk.

### Dimension 8: External Validity (0-10)

Assess generalizability and replication status.

| Score | Criteria |
|-------|---------|
| 9-10 | Independently replicated by multiple groups; generalizes across conditions |
| 7-8 | Replicated by 1-2 independent groups; reasonable generalizability |
| 5-6 | No independent replication but no contradictory findings; limited generalizability |
| 3-4 | No replication attempts; narrow experimental conditions; single population |
| 1-2 | Failed replication attempts or known contradictory findings |
| 0 | Multiple failed replications; finding not considered reliable |

**Replication Search Strategy:**
```
Search for replication evidence using MCP tools:

1. PubMed search for direct replications:
   mcp__pubmed__pubmed_data(method: "search_advanced",
     term: "[key finding] AND (replication OR replicate OR reproduce OR confirm)",
     start_date: "[publication date of original]")

2. Search for contradictory findings:
   mcp__pubmed__pubmed_data(method: "search_advanced",
     term: "[key finding] AND (failed OR negative OR contradict OR inconsistent)",
     start_date: "[publication date of original]")

3. Check preprints for recent replication attempts:
   mcp__biorxiv__biorxiv_data(method: "search_preprints",
     query: "[key finding] replication")
```

---

## Reproducibility Score Calculation

### Scoring Formula

```python
def calculate_reproducibility_score(dimension_scores):
    """Calculate overall reproducibility score (0-100).

    dimension_scores: dict with dimension names -> scores (each 0-10)
    Total raw: 0-80, scaled to 0-100
    """
    dimensions = [
        'claim_traceability',
        'methodological_completeness',
        'data_availability',
        'code_availability',
        'statistical_rigor',
        'internal_consistency',
        'bias_risk',
        'external_validity'
    ]

    raw_total = sum(dimension_scores.get(d, 0) for d in dimensions)
    scaled_score = (raw_total / 80) * 100

    # Determine rating
    if scaled_score >= 80:
        rating = "Highly reproducible"
        interpretation = "Robust evidence, ready for building upon"
    elif scaled_score >= 60:
        rating = "Moderately reproducible"
        interpretation = "Some gaps, but generally trustworthy"
    elif scaled_score >= 40:
        rating = "Questionable reproducibility"
        interpretation = "Significant gaps, interpret with caution"
    elif scaled_score >= 20:
        rating = "Low reproducibility"
        interpretation = "Major issues, independent verification needed"
    else:
        rating = "Not reproducible"
        interpretation = "Fundamental problems, do not rely on"

    # Identify weakest dimensions
    sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1])
    weakest = sorted_dims[:3]

    return {
        'raw_total': raw_total,
        'scaled_score': round(scaled_score, 1),
        'rating': rating,
        'interpretation': interpretation,
        'dimension_scores': dimension_scores,
        'weakest_dimensions': weakest,
        'strongest_dimensions': sorted_dims[-3:]
    }
```

### Rating Scale

| Score | Rating | Interpretation | Action |
|-------|--------|----------------|--------|
| 80-100 | Highly reproducible | Robust evidence, ready for building upon | Cite with confidence; use as foundation |
| 60-79 | Moderately reproducible | Some gaps, but generally trustworthy | Cite with caveats; note specific gaps |
| 40-59 | Questionable reproducibility | Significant gaps, interpret with caution | Request additional data/methods before relying on |
| 20-39 | Low reproducibility | Major issues, independent verification needed | Do not rely on without independent verification |
| 0-19 | Not reproducible | Fundamental problems, do not rely on | Flag concerns to authors/editors |

---

## Red Flag Checklist

Automatic warnings triggered during the audit:

```python
def red_flag_scan(audit_data):
    """Scan for reproducibility red flags.

    audit_data: dict with various audit indicators
    Returns list of triggered red flags with severity
    """
    red_flags = []

    # P-value clustering
    if audit_data.get('p_values'):
        p_vals = audit_data['p_values']
        just_below_05 = sum(1 for p in p_vals if 0.01 < p < 0.05)
        if just_below_05 / len(p_vals) > 0.5:
            red_flags.append({
                'flag': 'P-values clustered just below 0.05',
                'severity': 'HIGH',
                'detail': f'{just_below_05}/{len(p_vals)} p-values in (0.01, 0.05) range',
                'implication': 'Possible p-hacking or selective reporting'
            })

    # Implausibly large effect sizes
    if audit_data.get('effect_sizes_implausible'):
        red_flags.append({
            'flag': 'Effect sizes seem implausibly large',
            'severity': 'HIGH',
            'detail': 'Reported effects exceed typical range for field',
            'implication': 'Possible measurement error, selection bias, or inflated estimates'
        })

    # Small sample sizes
    if audit_data.get('min_group_n', float('inf')) < 10:
        red_flags.append({
            'flag': 'Very small sample sizes (N < 10 per group)',
            'severity': 'MEDIUM',
            'detail': f'Minimum group N = {audit_data["min_group_n"]}',
            'implication': 'Low statistical power, high false positive risk, imprecise estimates'
        })

    # No negative results
    if audit_data.get('all_results_positive', False):
        red_flags.append({
            'flag': 'No negative results reported at all',
            'severity': 'MEDIUM',
            'detail': 'Every analysis produced significant results',
            'implication': 'Possible publication bias, file drawer problem, or selective reporting'
        })

    # Brief methods
    if audit_data.get('methods_word_count', float('inf')) < 500:
        red_flags.append({
            'flag': 'Methods section unusually brief',
            'severity': 'MEDIUM',
            'detail': f'Methods section: {audit_data.get("methods_word_count", "unknown")} words',
            'implication': 'Insufficient detail for replication'
        })

    # No raw data or code
    if not audit_data.get('raw_data_available') and not audit_data.get('code_available'):
        red_flags.append({
            'flag': 'No raw data or code available',
            'severity': 'HIGH',
            'detail': 'Neither raw data nor analysis code is accessible',
            'implication': 'Results cannot be independently verified'
        })

    # Claims beyond data
    if audit_data.get('claims_beyond_data', False):
        red_flags.append({
            'flag': 'Claims extend far beyond the data presented',
            'severity': 'HIGH',
            'detail': 'Conclusions not warranted by the evidence shown',
            'implication': 'Overinterpretation; causal claims from correlational data'
        })

    # No internal replication
    if not audit_data.get('internal_replication'):
        red_flags.append({
            'flag': 'Key experiments not replicated within the study',
            'severity': 'MEDIUM',
            'detail': 'No internal replication or validation cohort',
            'implication': 'Results may be due to chance or specific conditions'
        })

    # Inappropriate tests
    if audit_data.get('inappropriate_tests', False):
        red_flags.append({
            'flag': 'Statistical tests inappropriate for data type',
            'severity': 'HIGH',
            'detail': 'Tests do not match data distribution or structure',
            'implication': 'P-values and confidence intervals may be invalid'
        })

    # Selective reporting
    if audit_data.get('outcome_switching', False):
        red_flags.append({
            'flag': 'Selective reporting of outcomes (registered vs. published)',
            'severity': 'HIGH',
            'detail': 'Published outcomes differ from pre-registered protocol',
            'implication': 'Possible outcome switching; positive results cherry-picked'
        })

    return {
        'red_flags': red_flags,
        'total_flags': len(red_flags),
        'high_severity': sum(1 for f in red_flags if f['severity'] == 'HIGH'),
        'medium_severity': sum(1 for f in red_flags if f['severity'] == 'MEDIUM'),
        'overall_concern': 'HIGH' if any(f['severity'] == 'HIGH' for f in red_flags) else
                          'MEDIUM' if red_flags else 'LOW'
    }
```

---

## Protocol Registration Verification

For clinical studies, use `mcp__ctgov__ctgov_data` to retrieve the registered protocol and compare against the published manuscript. Key elements to compare:

| Element | Severity if Changed | Type |
|---------|-------------------|------|
| Primary outcome | CRITICAL | Outcome switching |
| Sample size (>20% deviation) | MAJOR | Sample size deviation |
| Statistical analysis method | MAJOR | Analysis method change |
| Secondary outcomes removed | MAJOR | Selective reporting |
| Secondary outcomes added | MINOR | Post-hoc addition |
| Inclusion/exclusion criteria | MAJOR | Population change |
| Study duration | MINOR | Timeline change |

Flag any discrepancy between registered and published protocols explicitly in the report. Primary outcome switching is the most serious concern and should be classified as a CRITICAL issue.

---

## Python Visualization Templates

### Dimension Radar Chart

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_reproducibility_radar(dimension_scores, title="Reproducibility Audit"):
    """Radar chart of 8-dimension reproducibility scores."""
    dimensions = [
        'Claim\nTraceability', 'Methodological\nCompleteness',
        'Data\nAvailability', 'Code\nAvailability',
        'Statistical\nRigor', 'Internal\nConsistency',
        'Bias\nRisk', 'External\nValidity'
    ]
    scores = list(dimension_scores.values())

    angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False).tolist()
    scores += scores[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

    # Background zones
    for radius, color, label in [(8, '#2ecc71', 'Highly reproducible'),
                                  (6, '#f39c12', 'Moderate'),
                                  (4, '#e74c3c', 'Questionable')]:
        circle = plt.Circle((0, 0), radius, transform=ax.transData, fill=True,
                            alpha=0.05, color=color)

    ax.plot(angles, scores, 'o-', linewidth=2, color='#2c3e50', markersize=8)
    ax.fill(angles, scores, alpha=0.25, color='#3498db')

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dimensions, size=10)
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(['2', '4', '6', '8', '10'], size=8)

    overall = sum(dimension_scores.values()) / 80 * 100
    ax.set_title(f'{title}\nOverall Score: {overall:.0f}/100', size=14, pad=30)

    plt.tight_layout()
    plt.savefig('reproducibility_radar.png', dpi=150, bbox_inches='tight')
    plt.show()
```

Additional visualization options:
- **Red flag bar chart**: Horizontal bars colored by severity (HIGH=red, MEDIUM=orange) for each triggered flag
- **Multi-paper comparison**: Grouped bar chart comparing dimension scores across multiple papers side-by-side
- **Score heatmap**: Heat map with papers as rows, dimensions as columns, color-coded 0-10

---

## Multi-Agent Workflow Examples

### Example 1: "Audit the reproducibility of this Nature paper on CRISPR-Cas9 off-target effects"

1. **Reproducibility Audit (this skill)** -> Full 8-dimension assessment with GRIM/SPRITE tests on reported statistics
2. **Literature Deep Research** -> Search for replication studies, failed replications, and commentaries
3. **Peer Review** -> Complementary overall quality assessment beyond reproducibility
4. **Variant Analysis** -> Verify reported off-target sites against genomic databases

### Example 2: "How reliable are the clinical trial results for Drug X in Type 2 Diabetes?"

1. **Reproducibility Audit (this skill)** -> Protocol registration verification, statistical rigor check, bias assessment
2. **Clinical Trial Analyst** -> Detailed trial design evaluation
3. **Scientific Critical Thinking** -> Methodology and logical reasoning critique
4. **Drug Research** -> Full compound monograph for context

### Example 3: "Evaluate the reproducibility of this machine learning model for drug response prediction"

1. **Reproducibility Audit (this skill)** -> Code availability, data availability, methodological completeness (hyperparameters, random seeds)
2. **Statistical Modeling** -> Cross-validation methodology, overfitting assessment, test set leakage
3. **Peer Review** -> Overall paper quality and novelty assessment

### Example 4: "Assess data integrity in this proteomics study claiming novel biomarkers for Alzheimer's"

1. **Reproducibility Audit (this skill)** -> Internal consistency checks, data availability, statistical rigor, GRIM tests on summary statistics
2. **Proteomics Analysis** -> Technical assessment of proteomics workflow, mass spec methods
3. **Biomarker Discovery** -> Biomarker validation framework and clinical utility assessment
4. **Disease Research** -> Alzheimer's biomarker landscape for external validity context

### Example 5: "Compare the reproducibility of three competing papers on the same gene therapy approach"

1. **Reproducibility Audit (this skill)** -> Run full 8-dimension audit on each paper independently
2. **Literature Deep Research** -> Cross-reference citations, identify areas of agreement and contradiction
3. **Scientific Critical Thinking** -> Comparative methodology critique across the three studies
4. **Research Synthesis** -> Evidence synthesis and weight-of-evidence assessment

---

## Report Template

```
# Reproducibility Audit: [Paper/Claim Title]
Generated: [DATE]
Reproducibility Score: [X/100]
Rating: [Highly Reproducible / Moderately Reproducible / Questionable / Low / Not Reproducible]

## 1. Target
**Paper/Claim:** [Full citation or description]
**Key Claims Audited:** [List of specific claims assessed]
**Audit Scope:** [What was included/excluded from audit]

## 2. 8-Dimension Assessment

### 2.1. Claim Traceability: [X/10]
[Assessment details]
- Claims traced: [N/total]
- Untraced claims: [list]
- Logical chain assessment: [complete/gaps identified]

### 2.2. Methodological Completeness: [X/10]
[Assessment details]
- Key parameters specified: [yes/no for each critical parameter]
- Replication feasibility: [high/medium/low]

### 2.3. Data Availability: [X/10]
[Assessment details]
- Raw data: [repository + accession / upon request / unavailable]
- Processed data: [available / unavailable]
- Data dictionary: [yes / no]

### 2.4. Code Availability: [X/10]
[Assessment details]
- Repository: [URL or unavailable]
- Documentation: [comprehensive / basic / none]
- Runnable: [yes / with modifications / no]

### 2.5. Statistical Rigor: [X/10]
[Assessment details]
- Tests appropriate: [yes / concerns]
- Effect sizes reported: [yes / no]
- Multiple comparison correction: [applied / not needed / missing]

### 2.6. Internal Consistency: [X/10]
[Assessment details]
- GRIM test: [PASS / FAIL / N/A]
- SPRITE test: [PASS / FAIL / N/A]
- Cross-reference check: [consistent / discrepancies found]

### 2.7. Bias Risk: [X/10]
[Assessment details]
- Overall risk: [Low / Some concerns / High / Critical]
- Highest risk domains: [list]

### 2.8. External Validity: [X/10]
[Assessment details]
- Independent replications: [number]
- Contradictory findings: [number]
- Generalizability: [broad / limited / narrow]

## 3. Reproducibility Score: [X/100]
## 4. Rating: [Highly Reproducible / Moderate / Questionable / Low / Not Reproducible]

## 5. Red Flags
[List all triggered red flags with severity]

## 6. Specific Issues Found

### Critical (must address before relying on results)
1. [Issue with evidence]
2. [Issue with evidence]

### Major (should address to strengthen claims)
1. [Issue with evidence]
2. [Issue with evidence]

### Minor (could improve reproducibility)
1. [Issue with suggestion]
2. [Issue with suggestion]

## 7. Recommendations

### For Authors
1. [Specific actionable improvement]
2. [Specific actionable improvement]

### For Readers/Users of This Work
1. [Guidance on how to interpret/use findings given reproducibility assessment]
2. [Caveats to consider]

### For Follow-Up Studies
1. [What should be prioritized for independent replication]
2. [Methodological improvements for future work]

## 8. Visualizations
[Radar chart, red flag summary, dimension comparison as appropriate]
```

---

## Completeness Checklist

- [ ] Target paper/claim clearly identified with full citation
- [ ] All 8 dimensions scored independently (each 0-10)
- [ ] Claim traceability mapping completed (every claim traced to data source)
- [ ] Methodological completeness checklist applied (study-type-specific)
- [ ] Data and code availability verified (repositories checked, not just statements)
- [ ] Statistical rigor audit performed (test appropriateness, effect sizes, corrections)
- [ ] Internal consistency checks run (GRIM/SPRITE where applicable, cross-reference text/figures/tables)
- [ ] Bias risk assessed across all relevant domains (adapted Cochrane RoB)
- [ ] External validity evaluated (replication search via MCP tools, contradictory findings)
- [ ] Red flag checklist scanned with severity ratings
- [ ] Protocol registration verified for clinical studies (ClinicalTrials.gov comparison)
- [ ] Overall reproducibility score calculated (0-100 scale) with rating
- [ ] Issues categorized by severity (Critical / Major / Minor)
- [ ] Specific actionable recommendations provided for authors, readers, and follow-up studies
- [ ] MCP tools used to gather replication evidence and verify external claims
- [ ] Report file created with all sections populated (no remaining placeholders)
