---
name: delphi-method
description: Expert consensus building through structured rounds of independent assessment, anonymized sharing, and convergence analysis. Based on the RAND/Delphi methodology used in forecasting, technology assessment, and clinical guideline development. Generates 5-8 expert perspectives across 4 rounds, measures convergence with IQR/CV, produces consensus strength scores (0-100), and preserves minority reports. Use when asked to build expert consensus, estimate probabilities with multiple perspectives, assess technology readiness, develop clinical guidelines, perform risk assessment panels, evaluate complex questions requiring diverse expertise, or resolve disagreements through structured deliberation.
---

# Delphi Method

Expert consensus building through structured rounds of assessment and convergence. Based on the RAND/Delphi methodology used in forecasting, technology assessment, and clinical guideline development. This skill simulates a panel of 5-8 domain experts who independently assess a question, share their reasoning anonymously, revise their positions, and converge toward a consensus position with quantified agreement.

Distinct from **adversarial-collaboration** (which structures debate between two opposing sides to find synthesis), **consciousness-council** (which convenes archetypes for deliberation on any topic), and **peer-review** (which evaluates a specific paper or manuscript). This skill applies the formal Delphi process: independent assessment, anonymized sharing, iterative revision, and measured convergence.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_delphi_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as each Delphi round completes
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Evaluating a specific manuscript or paper -> use `peer-review`
- Two-sided debate with structured advocacy -> use `adversarial-collaboration`
- Broad strategic scenario analysis -> use `what-if-oracle`
- Hypothesis generation and experimental design -> use `hypothesis-generation`
- Assessing reproducibility of specific claims -> use `reproducibility-audit`
- Evaluating methodology or statistical rigor of a study -> use `scientific-critical-thinking`
- First-principles reasoning from axioms -> use `first-principles`
- Archetypal deliberation on open-ended questions -> use `consciousness-council`

## Cross-Skill Routing

- Evidence gathering for expert assessments -> `literature-deep-research` or `deep-research`
- Statistical methodology questions raised by panel -> `statistical-modeling`
- Clinical guideline development output -> `clinical-guidelines`
- Risk assessment output -> `risk-management-specialist`
- Drug development probability estimation -> `what-if-oracle` for scenario branches
- Regulatory pathway questions from panel -> `fda-consultant`
- Target validation evidence for panel inputs -> `drug-target-validator`
- Health economics questions from panel -> `competitive-intelligence`

---

## Available MCP Tools

### `mcp__pubmed__pubmed_data` (Evidence for Expert Assessments)

| Method | Delphi use |
|--------|-----------|
| `search_keywords` | Gather evidence base for expert panel to assess |
| `search_advanced` | Find systematic reviews, meta-analyses for probability anchoring |
| `get_article_metadata` | Retrieve specific studies cited in expert reasoning |

### `mcp__biorxiv__biorxiv_data` (Emerging Evidence)

| Method | Delphi use |
|--------|-----------|
| `search_preprints` | Identify emerging evidence that may shift expert opinion |
| `get_preprint_details` | Assess quality of preprint evidence cited by experts |

### `mcp__ctgov__ctgov_data` (Clinical Trial Evidence)

| Method | Delphi use |
|--------|-----------|
| `search` | Find relevant clinical trials for probability calibration |
| `get` | Retrieve trial details for expert assessment inputs |
| `stats` | Quantify trial landscape for technology readiness assessment |

### `mcp__opentargets__opentargets_data` (Target-Disease Evidence)

| Method | Delphi use |
|--------|-----------|
| `search_targets` | Validate target-related claims in expert assessments |
| `get_target_disease_associations` | Quantify evidence strength for panel inputs |
| `get_target_details` | Full target context for expert deliberation |

### `mcp__fda__fda_data` (Regulatory Precedent)

| Method | Delphi use |
|--------|-----------|
| `lookup_drug` | Regulatory precedent for approval probability estimation |
| `search_orange_book` | Patent and exclusivity context for market assessments |

### `mcp__chembl__chembl_data` (Compound Intelligence)

| Method | Delphi use |
|--------|-----------|
| `compound_search` | Compound data for medicinal chemistry expert inputs |
| `target_search` | Target landscape for pharmacology expert assessments |
| `drug_search` | Drug development history for probability anchoring |

---

## Core Methodology: 4-Round Delphi Process

### Round 1: Independent Expert Assessments

Select 5-8 expert archetypes relevant to the question. Each expert provides their assessment independently, without knowledge of other experts' views.

#### Expert Archetype Pool

Select the most relevant subset for each question:

| Archetype | Domain | Best For |
|-----------|--------|----------|
| **Clinical Expert** | Patient outcomes, treatment protocols, real-world evidence | Efficacy questions, treatment guidelines, clinical feasibility |
| **Molecular Biologist** | Mechanisms, pathways, target biology | Target validation, mechanism of action, biological plausibility |
| **Biostatistician** | Study design, power, multiple comparisons, effect sizes | Trial design, evidence quality, statistical validity |
| **Regulatory Scientist** | FDA/EMA requirements, precedent, risk classification | Approval probability, regulatory strategy, labeling |
| **Medicinal Chemist** | Compound properties, SAR, formulation, synthesis | Drug-likeness, synthesis feasibility, formulation |
| **Pharmacologist** | PK/PD, drug-drug interactions, safety pharmacology | Dose selection, safety assessment, DDI risk |
| **Health Economist** | Cost-effectiveness, QALY, market access, reimbursement | Pricing, HTA submission, payer strategy |
| **Patient Advocate** | Patient burden, quality of life, unmet need, access | Unmet need, patient preference, adherence |
| **Epidemiologist** | Population impact, risk factors, disease burden | Incidence/prevalence, target population, public health impact |
| **Computational Scientist** | Modeling, simulation, AI/ML predictions | In silico evidence, predictive modeling, data integration |
| **Toxicologist** | Safety assessment, therapeutic index, off-target effects | Safety margins, toxicity prediction, risk-benefit |
| **Manufacturing Expert** | Scalability, supply chain, CMC, process development | CMC feasibility, scale-up risk, supply chain |

#### Expert Assessment Template

Each expert provides:

```
### Expert [N]: [Archetype Name]

**Assessment/Estimate:** [Quantitative where possible — probability, score, timeline, etc.]

**Confidence Level:** [0-100%]

**Key Reasoning:**
1. [Primary evidence or argument]
2. [Supporting evidence]
3. [Additional consideration]
4. [Contextual factor]
5. [Historical precedent or analogy]

**Biggest Concern or Uncertainty:**
[Single most important factor that could change this assessment]

**Evidence Cited:**
- [Source 1 with evidence tier T1-T4]
- [Source 2 with evidence tier T1-T4]
```

#### Evidence Tier Classification

| Tier | Label | Examples |
|------|-------|----------|
| **T1** | Definitive | Published pivotal trials, regulatory filings, meta-analyses |
| **T2** | Strong | Peer-reviewed RCTs, systematic reviews, treatment guidelines |
| **T3** | Emerging | Conference abstracts, preprints, interim analyses |
| **T4** | Inferred | Expert opinion, analyst reports, analogies from other fields |

### Round 2: Anonymized Sharing & Revision

After Round 1, share all expert assessments without attribution. Each expert sees:

1. **Distribution of responses**: histogram or range of all estimates
2. **Central tendency**: median and mean of quantitative assessments
3. **Full range**: minimum to maximum estimates
4. **All reasoning**: every expert's key reasoning points (anonymized)
5. **All concerns**: every expert's biggest uncertainty

Each expert then revises their assessment or maintains it with explicit justification.

#### Revision Tracking Template

```
### Expert [N] Revision (Round 2)

**Original Assessment:** [from Round 1]
**Revised Assessment:** [new value, or "Maintained"]
**Change Magnitude:** [absolute and percentage change, or "No change"]

**Revision Reasoning:**
- [What new information influenced the change?]
- [Which other expert's reasoning was most compelling?]
- [What remained unconvincing?]

**Maintained Because:** [if no change — why the original position still holds]
```

### Round 3: Convergence Assessment

Measure the degree of agreement after Round 2 revisions.

#### Convergence Metrics

**Interquartile Range (IQR):**
```python
import numpy as np

def calculate_convergence(estimates):
    """Calculate convergence metrics for Delphi panel estimates."""
    estimates = np.array(estimates)
    q1 = np.percentile(estimates, 25)
    q3 = np.percentile(estimates, 75)
    iqr = q3 - q1
    median = np.median(estimates)
    mean = np.mean(estimates)
    cv = np.std(estimates) / mean * 100 if mean != 0 else float('inf')

    # Relative IQR (normalized to median)
    relative_iqr = iqr / median * 100 if median != 0 else float('inf')

    return {
        'median': median,
        'mean': mean,
        'q1': q1,
        'q3': q3,
        'iqr': iqr,
        'relative_iqr': relative_iqr,
        'cv': cv,
        'min': np.min(estimates),
        'max': np.max(estimates),
        'range': np.max(estimates) - np.min(estimates)
    }

def assess_consensus_level(relative_iqr):
    """Classify consensus strength based on relative IQR."""
    if relative_iqr < 10:
        return "Strong consensus"
    elif relative_iqr < 25:
        return "Moderate consensus"
    elif relative_iqr < 50:
        return "Weak consensus"
    else:
        return "No consensus"
```

**Cluster Identification:**
```python
def identify_clusters(estimates, labels, threshold=0.3):
    """Identify distinct clusters of expert opinion."""
    estimates = np.array(estimates)
    range_val = np.max(estimates) - np.min(estimates)

    if range_val == 0:
        return [{'members': labels, 'center': estimates[0], 'spread': 0}]

    # Normalized estimates
    normalized = (estimates - np.min(estimates)) / range_val

    # Simple gap-based clustering
    sorted_indices = np.argsort(normalized)
    sorted_vals = normalized[sorted_indices]

    clusters = []
    current_cluster = [sorted_indices[0]]

    for i in range(1, len(sorted_vals)):
        if sorted_vals[i] - sorted_vals[i-1] > threshold:
            clusters.append(current_cluster)
            current_cluster = [sorted_indices[i]]
        else:
            current_cluster.append(sorted_indices[i])
    clusters.append(current_cluster)

    result = []
    for cluster in clusters:
        cluster_estimates = estimates[cluster]
        cluster_labels = [labels[i] for i in cluster]
        result.append({
            'members': cluster_labels,
            'center': np.median(cluster_estimates),
            'spread': np.std(cluster_estimates),
            'estimates': cluster_estimates.tolist()
        })

    return result
```

#### Disagreement Classification

For each identified cluster disagreement, classify it:

| Type | Definition | Resolution Strategy |
|------|-----------|-------------------|
| **Empirical** | Disagreement about facts or data interpretation | Resolve with additional evidence, data, or analysis |
| **Methodological** | Disagreement about appropriate methods or frameworks | Resolve with methodological justification or sensitivity analysis |
| **Value-based** | Disagreement about priorities, risk tolerance, or goals | Cannot fully resolve — document and acknowledge in recommendations |
| **Scope-based** | Experts considering different timeframes or contexts | Clarify scope and re-assess within shared frame |

### Round 4: Final Consensus & Minority Report

#### Consensus Position

```
**Consensus Estimate:** [Median with interquartile range]
**Agreement Level:** [Strong/Moderate/Weak/No consensus]
**Confidence-Weighted Estimate:** [Weighted by expert confidence levels]
**Panel Size:** [N experts]
**Rounds Completed:** [4]
```

#### Consensus Strength Score (0-100)

| Component | Weight | Scoring |
|-----------|--------|---------|
| **IQR Convergence** | 30% | 0-30 based on relative IQR (< 10% = 30, 10-25% = 20, 25-50% = 10, > 50% = 0) |
| **Round-over-Round Convergence** | 20% | 0-20 based on IQR reduction from Round 1 to Round 2 |
| **Expert Confidence** | 20% | 0-20 based on average expert self-reported confidence |
| **Evidence Quality** | 15% | 0-15 based on proportion of T1/T2 evidence cited |
| **Panel Coverage** | 15% | 0-15 based on diversity of expert archetypes represented |

**Rating Scale:**

| Score | Label | Interpretation |
|-------|-------|----------------|
| 90-100 | Strong consensus | High confidence, narrow range — reliable basis for action |
| 70-89 | Moderate consensus | General agreement with some outliers — proceed with monitoring |
| 50-69 | Weak consensus | Broad agreement on direction, not specifics — additional data needed |
| 30-49 | Split | Significant disagreement, multiple viable positions — defer decision or gather evidence |
| 0-29 | No consensus | Fundamental disagreement — reframe question or expand panel |

#### Minority Report

Always preserve dissenting views with full reasoning:

```
### Minority Report

**Dissenting Expert(s):** [Archetype(s)]
**Dissenting Position:** [Their final assessment]
**Core Reasoning:** [Why they disagree with consensus]
**Conditions Under Which Minority Is Right:**
[Specific scenarios or evidence that would validate the minority view]
**Recommended Monitoring:** [What to watch for]
```

---

## Specific Applications

### Application 1: Probability Estimation

**Question format:** "What is the probability that [event] will occur?"

**Process:**
1. Each expert estimates probability (0-100%) independently
2. Experts provide calibration anchors (base rates, historical precedent)
3. After anonymized sharing, experts revise estimates
4. Final output: probability distribution with confidence interval

**Calibration Guidance:**
```python
def calibration_check(estimates, confidences):
    """Check if panel estimates are well-calibrated."""
    # Overconfidence detection: high confidence + high variance = red flag
    avg_confidence = np.mean(confidences)
    cv = np.std(estimates) / np.mean(estimates) * 100

    if avg_confidence > 80 and cv > 30:
        return "WARNING: High confidence but high variance suggests overconfidence"
    if avg_confidence < 40 and cv < 15:
        return "NOTE: Low confidence despite high agreement — experts may lack domain knowledge"
    return "Calibration appears reasonable"
```

**Base Rate Anchoring:**
- Drug approval probability by phase: Phase 1 (10%), Phase 2 (15-20%), Phase 3 (50-60%)
- Technology adoption: Rogers diffusion curve as baseline
- Regulatory: historical approval rates by therapeutic area
- Use MCP tools to find specific base rates for the domain

### Application 2: Technology Readiness Assessment

**Question format:** "Is [technology] ready for [application]?"

**Process:**
1. Each expert rates readiness on TRL 1-9 scale independently
2. Experts identify specific gaps preventing advancement
3. After sharing, experts converge on TRL level
4. Final output: TRL consensus with advancement roadmap

**Technology Readiness Levels (adapted for biotech/pharma):**

| TRL | Stage | Description |
|-----|-------|-------------|
| 1 | Basic Research | Basic principles observed, target identified |
| 2 | Concept Formulation | Technology concept, assay development |
| 3 | Proof of Concept | In vitro validation, hit identification |
| 4 | Lab Validation | Lead optimization, in vivo proof of concept |
| 5 | Relevant Environment | IND-enabling studies, GMP process development |
| 6 | Prototype Demo | Phase 1 clinical, manufacturing scale-up |
| 7 | System Demo | Phase 2 clinical, pivotal study design |
| 8 | System Complete | Phase 3 clinical, regulatory submission |
| 9 | Operational | Approved, commercial launch, post-market |

### Application 3: Clinical Guideline Development

**Question format:** "Should [treatment X] be recommended for [condition Y]?"

**Process:**
1. Each expert rates strength of recommendation (Strong for/Conditional for/Conditional against/Strong against)
2. Experts assess quality of evidence using GRADE framework
3. After sharing, experts converge on recommendation
4. Final output: recommendation with evidence quality rating

**GRADE Integration:**

| Evidence Quality | Definition |
|-----------------|------------|
| High | Further research very unlikely to change confidence in estimate |
| Moderate | Further research likely to have important impact |
| Low | Further research very likely to have important impact |
| Very Low | Any estimate is very uncertain |

**Recommendation Strength Matrix:**

| | High Quality Evidence | Moderate | Low | Very Low |
|---|---|---|---|---|
| **Strong For** | Recommend | Recommend | Consider | Insufficient |
| **Conditional For** | Suggest | Suggest | Consider | Insufficient |
| **Conditional Against** | Suggest against | Consider | Consider | Insufficient |
| **Strong Against** | Recommend against | Recommend against | Suggest against | Insufficient |

### Application 4: Risk Assessment

**Question format:** "What are the key risks for [program/project]?"

**Process:**
1. Each expert identifies top 5 risks with likelihood (1-5) and impact (1-5) scores
2. Aggregate all risks, deduplicate, and create master risk list
3. After anonymized sharing, experts re-score the aggregated risks
4. Final output: prioritized risk register with risk matrix

**Risk Score Calculation:**
```python
def aggregate_risk_scores(expert_scores):
    """Aggregate risk scores across Delphi panel.

    expert_scores: list of dicts, each with 'likelihood' and 'impact' (1-5)
    Returns aggregated risk score and classification.
    """
    likelihoods = [s['likelihood'] for s in expert_scores]
    impacts = [s['impact'] for s in expert_scores]

    median_likelihood = np.median(likelihoods)
    median_impact = np.median(impacts)
    risk_score = median_likelihood * median_impact

    if risk_score >= 16:
        classification = "Critical"
    elif risk_score >= 9:
        classification = "High"
    elif risk_score >= 4:
        classification = "Medium"
    else:
        classification = "Low"

    return {
        'median_likelihood': median_likelihood,
        'median_impact': median_impact,
        'risk_score': risk_score,
        'classification': classification,
        'likelihood_iqr': np.percentile(likelihoods, 75) - np.percentile(likelihoods, 25),
        'impact_iqr': np.percentile(impacts, 75) - np.percentile(impacts, 25)
    }
```

---

## Python Visualization Templates

### Radar/Spider Chart: Expert Convergence

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_expert_convergence_radar(dimensions, round1_scores, round2_scores, expert_labels):
    """Radar chart showing expert convergence across assessment dimensions."""
    num_dims = len(dimensions)
    angles = np.linspace(0, 2 * np.pi, num_dims, endpoint=False).tolist()
    angles += angles[:1]  # Close the polygon

    fig, axes = plt.subplots(1, 2, figsize=(16, 8), subplot_kw=dict(polar=True))

    for ax, scores, title in zip(axes, [round1_scores, round2_scores],
                                  ['Round 1 (Independent)', 'Round 2 (Revised)']):
        for i, (expert_scores, label) in enumerate(zip(scores, expert_labels)):
            values = expert_scores + expert_scores[:1]
            ax.plot(angles, values, 'o-', linewidth=1.5, label=label, alpha=0.7)
            ax.fill(angles, values, alpha=0.05)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dimensions, size=9)
        ax.set_title(title, size=14, pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=8)

    plt.tight_layout()
    plt.savefig('delphi_convergence_radar.png', dpi=150, bbox_inches='tight')
    plt.show()
```

### Box Plot: Estimate Distributions Across Rounds

```python
def plot_estimate_distributions(round1_estimates, round2_estimates, question_label):
    """Box plots showing how estimate distributions narrow across rounds."""
    fig, ax = plt.subplots(figsize=(10, 6))

    bp1 = ax.boxplot([round1_estimates], positions=[1], widths=0.6,
                      patch_artist=True, boxprops=dict(facecolor='lightcoral', alpha=0.7))
    bp2 = ax.boxplot([round2_estimates], positions=[2], widths=0.6,
                      patch_artist=True, boxprops=dict(facecolor='lightblue', alpha=0.7))

    # Individual expert points
    x1 = np.random.normal(1, 0.04, size=len(round1_estimates))
    x2 = np.random.normal(2, 0.04, size=len(round2_estimates))
    ax.scatter(x1, round1_estimates, alpha=0.6, color='darkred', zorder=5, s=50)
    ax.scatter(x2, round2_estimates, alpha=0.6, color='darkblue', zorder=5, s=50)

    # IQR annotation
    iqr1 = np.percentile(round1_estimates, 75) - np.percentile(round1_estimates, 25)
    iqr2 = np.percentile(round2_estimates, 75) - np.percentile(round2_estimates, 25)
    reduction = (1 - iqr2 / iqr1) * 100 if iqr1 > 0 else 0

    ax.annotate(f'IQR: {iqr1:.1f}', xy=(1, np.percentile(round1_estimates, 75)),
                xytext=(1.3, np.percentile(round1_estimates, 75)), fontsize=10)
    ax.annotate(f'IQR: {iqr2:.1f}\n({reduction:.0f}% reduction)',
                xy=(2, np.percentile(round2_estimates, 75)),
                xytext=(2.3, np.percentile(round2_estimates, 75)), fontsize=10)

    ax.set_xticks([1, 2])
    ax.set_xticklabels(['Round 1\n(Independent)', 'Round 2\n(Revised)'])
    ax.set_ylabel(question_label)
    ax.set_title(f'Delphi Convergence: {question_label}')
    plt.tight_layout()
    plt.savefig('delphi_distribution.png', dpi=150, bbox_inches='tight')
    plt.show()
```

### Convergence Tracking: IQR Over Rounds

```python
def plot_convergence_tracking(round_iqrs, dimension_labels):
    """Track IQR reduction across Delphi rounds for multiple dimensions."""
    fig, ax = plt.subplots(figsize=(12, 6))

    rounds = range(1, len(round_iqrs) + 1)
    for i, label in enumerate(dimension_labels):
        iqrs = [r[i] for r in round_iqrs]
        ax.plot(rounds, iqrs, 'o-', linewidth=2, markersize=8, label=label)

    ax.axhline(y=10, color='green', linestyle='--', alpha=0.5, label='Strong consensus threshold')
    ax.axhline(y=25, color='orange', linestyle='--', alpha=0.5, label='Moderate consensus threshold')
    ax.axhline(y=50, color='red', linestyle='--', alpha=0.5, label='Weak consensus threshold')

    ax.set_xlabel('Delphi Round')
    ax.set_ylabel('Relative IQR (%)')
    ax.set_title('Convergence Tracking Across Delphi Rounds')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.set_xticks(rounds)
    plt.tight_layout()
    plt.savefig('delphi_convergence_tracking.png', dpi=150, bbox_inches='tight')
    plt.show()
```

### Heat Map: Agreement Matrix

```python
def plot_agreement_matrix(expert_labels, estimates_matrix):
    """Heat map showing pairwise agreement between experts.

    estimates_matrix: N_experts x N_dimensions array of scores
    """
    n = len(expert_labels)
    agreement = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            # Agreement = 1 - normalized absolute difference
            diff = np.mean(np.abs(np.array(estimates_matrix[i]) -
                                   np.array(estimates_matrix[j])))
            max_range = np.max(estimates_matrix) - np.min(estimates_matrix)
            agreement[i][j] = 1 - (diff / max_range) if max_range > 0 else 1

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(agreement, cmap='RdYlGn', vmin=0, vmax=1)

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(expert_labels, rotation=45, ha='right')
    ax.set_yticklabels(expert_labels)

    for i in range(n):
        for j in range(n):
            ax.text(j, i, f'{agreement[i][j]:.2f}', ha='center', va='center',
                    color='black' if agreement[i][j] > 0.3 else 'white')

    plt.colorbar(im, label='Agreement Score')
    ax.set_title('Expert Agreement Matrix (Post Round 2)')
    plt.tight_layout()
    plt.savefig('delphi_agreement_matrix.png', dpi=150, bbox_inches='tight')
    plt.show()
```

---

## Multi-Agent Workflow Examples

### Example 1: "What is the probability that our GLP-1 agonist will receive FDA approval?"

1. **Delphi Method (this skill)** -> Assemble panel: Clinical Expert, Regulatory Scientist, Biostatistician, Pharmacologist, Health Economist, Toxicologist
2. **FDA Consultant** -> Regulatory precedent for GLP-1 agonist approvals, pathway analysis
3. **Drug Research** -> Comprehensive drug monograph for compound context
4. **Competitive Intelligence** -> GLP-1 landscape, competitor pipeline, differentiation assessment
5. **Clinical Trial Analyst** -> Pivotal trial design assessment and enrollment projections

**Delphi-specific workflow:**
- Round 1: Each expert estimates approval probability (0-100%) with reasoning
- Feed FDA consultant and competitive intelligence outputs as evidence for Round 2
- Round 3: Measure convergence — expect clusters around "optimistic" vs "cautious" positions
- Round 4: Consensus probability with CI, minority report on key risks

### Example 2: "Should CRISPR-based gene therapy be recommended for sickle cell disease in pediatric patients?"

1. **Delphi Method (this skill)** -> Assemble panel: Clinical Expert, Molecular Biologist, Patient Advocate, Health Economist, Toxicologist, Regulatory Scientist, Epidemiologist, Biostatistician
2. **Clinical Guidelines** -> Existing sickle cell treatment guidelines
3. **Disease Research** -> Sickle cell disease biology and current standard of care
4. **Literature Deep Research** -> Systematic review of CRISPR-SCD clinical evidence

**Delphi-specific workflow:**
- Round 1: Each expert rates recommendation strength (Strong for / Conditional for / Conditional against / Strong against) with GRADE evidence assessment
- Round 2: Share anonymized ratings and reasoning — expect value-based disagreements between Health Economist (cost) and Patient Advocate (access)
- Round 3: Classify disagreements as empirical vs. value-based
- Round 4: Consensus recommendation with evidence quality rating and minority perspectives preserved

### Example 3: "Is mRNA-based cancer vaccine technology ready for Phase 3 pivotal trials?"

1. **Delphi Method (this skill)** -> Assemble panel: Molecular Biologist, Clinical Expert, Manufacturing Expert, Regulatory Scientist, Biostatistician, Computational Scientist
2. **Drug Target Validator** -> Target validation for selected tumor antigens
3. **Clinical Trial Protocol Designer** -> Phase 3 design options and feasibility
4. **What-If Oracle** -> Scenario analysis for key uncertainties (immunogenicity, manufacturing scale)

**Delphi-specific workflow:**
- Round 1: Each expert rates TRL (1-9) independently with gap identification
- Round 2: After sharing, Manufacturing Expert may lower TRL due to CMC challenges while Molecular Biologist maintains high TRL based on mechanism
- Round 3: Identify scope-based disagreement (lab-scale vs. commercial-scale readiness)
- Round 4: Consensus TRL with advancement roadmap and specific milestones needed

### Example 4: "What are the key risks for our ADC (antibody-drug conjugate) program entering Phase 2?"

1. **Delphi Method (this skill)** -> Assemble panel: Clinical Expert, Toxicologist, Medicinal Chemist, Manufacturing Expert, Pharmacologist, Regulatory Scientist, Biostatistician
2. **Drug Research** -> ADC compound profile, linker-payload characterization
3. **Clinical Pharmacology** -> PK/PD, therapeutic index, dose-response analysis
4. **Risk Management Specialist** -> Formal risk management framework (ISO 14971)

**Delphi-specific workflow:**
- Round 1: Each expert identifies top 5 risks with likelihood and impact scores (1-5)
- Round 2: Aggregate master risk list, experts re-score all identified risks
- Round 3: Generate consensus risk matrix with IQR for each risk score
- Round 4: Prioritized risk register with mitigation strategies and monitoring triggers

### Example 5: "What is the optimal pricing strategy for a first-in-class rare disease therapy?"

1. **Delphi Method (this skill)** -> Assemble panel: Health Economist, Clinical Expert, Patient Advocate, Regulatory Scientist, Epidemiologist, Manufacturing Expert
2. **Competitive Intelligence** -> Rare disease therapy pricing landscape, comparator pricing
3. **Disease Research** -> Disease burden, current treatment costs, patient journey

**Delphi-specific workflow:**
- Round 1: Each expert provides price range estimate with value justification framework
- Round 2: Expect significant divergence between Health Economist (ICER-based) and Patient Advocate (access-based)
- Round 3: Value-based disagreement acknowledged, empirical questions (market size, budget impact) resolved
- Round 4: Consensus price range with sensitivity to payer perspective, minority report on access concerns

---

## Report Template

```
# Delphi Assessment: [Question]
Generated: [DATE]
Consensus Strength Score: [X/100] ([Strong/Moderate/Weak/Split/No consensus])

## 1. Executive Summary
[2-3 paragraph synthesis: question, panel composition, consensus position, key disagreements,
and actionable recommendations]

## 2. Panel Composition
| Expert # | Archetype | Selection Rationale |
|----------|-----------|-------------------|
| 1 | [Archetype] | [Why this perspective is needed] |
| 2 | [Archetype] | [Why this perspective is needed] |
...

## 3. Round 1: Independent Assessments
### Expert 1: [Archetype]
- **Assessment:** [quantitative]
- **Confidence:** [0-100%]
- **Key Reasoning:** [3-5 bullets]
- **Biggest Concern:** [single issue]
- **Evidence:** [sources with tiers]

### Expert 2: [Archetype]
...
[Repeat for all experts]

**Round 1 Summary Statistics:**
- Median: [X] | Mean: [X]
- Range: [min] to [max]
- IQR: [X] (Relative IQR: [X]%)

## 4. Round 2: Revised Assessments
### Expert 1 Revision
- Original: [X] -> Revised: [X] (Change: [+/- X])
- Reasoning: [what influenced the change]
...
[Repeat for all experts]

**Round 2 Summary Statistics:**
- Median: [X] | Mean: [X]
- Range: [min] to [max]
- IQR: [X] (Relative IQR: [X]%)
- IQR Reduction: [X]% from Round 1

## 5. Round 3: Convergence Analysis
- **Agreement Metric:** [Relative IQR or CV]
- **Consensus Level:** [Strong/Moderate/Weak/No consensus]
- **Clusters Identified:** [Number and description]
  - Cluster A: [Members, center, reasoning]
  - Cluster B: [Members, center, reasoning]
- **Core Disagreements:**
  - [Disagreement 1]: [Empirical/Methodological/Value-based/Scope-based]
  - [Disagreement 2]: [Classification and resolution approach]

## 6. Round 4: Final Consensus
- **Consensus Position:** [Median estimate with IQR]
- **Confidence-Weighted Estimate:** [Weighted by expert confidence]
- **Agreement Level:** [Strong/Moderate/Weak/Split/No consensus]
- **Consensus Strength Score:** [X/100]

### Score Breakdown
| Component | Score | Max | Rationale |
|-----------|-------|-----|-----------|
| IQR Convergence | [X] | 30 | |
| Round-over-Round Convergence | [X] | 20 | |
| Expert Confidence | [X] | 20 | |
| Evidence Quality | [X] | 15 | |
| Panel Coverage | [X] | 15 | |
| **TOTAL** | **[X]** | **100** | |

### Minority Report
- **Dissenting Expert(s):** [Archetype(s)]
- **Dissenting Position:** [Assessment]
- **Core Reasoning:** [Why they disagree]
- **Conditions Under Which Minority Is Right:** [Specific scenarios]
- **Recommended Monitoring:** [What to watch for]

## 7. Recommendations
### Primary Recommendation
[Based on consensus position]

### Conditional Recommendations
[Based on minority scenarios]

### Information Gaps
[What additional evidence would strengthen consensus]

## 8. Visualizations
[Radar chart, box plot, convergence tracking, agreement matrix as appropriate]
```

---

## Advanced Techniques

### Confidence-Weighted Aggregation

When expert confidence varies significantly, weight assessments by confidence:

```python
def confidence_weighted_estimate(estimates, confidences):
    """Calculate confidence-weighted consensus estimate."""
    weights = np.array(confidences) / sum(confidences)
    weighted_mean = np.average(estimates, weights=weights)

    # Weighted standard deviation
    weighted_var = np.average((np.array(estimates) - weighted_mean) ** 2,
                               weights=weights)
    weighted_std = np.sqrt(weighted_var)

    return {
        'weighted_mean': weighted_mean,
        'weighted_std': weighted_std,
        'weighted_ci_95': (weighted_mean - 1.96 * weighted_std,
                           weighted_mean + 1.96 * weighted_std),
        'unweighted_median': np.median(estimates),
        'weight_range': (min(weights), max(weights))
    }
```

### Sensitivity Analysis

Test how removing individual experts affects consensus:

```python
def leave_one_out_sensitivity(estimates, expert_labels):
    """Assess consensus robustness by removing one expert at a time."""
    full_median = np.median(estimates)
    results = []

    for i in range(len(estimates)):
        reduced = np.delete(estimates, i)
        reduced_median = np.median(reduced)
        shift = reduced_median - full_median

        results.append({
            'removed': expert_labels[i],
            'original_median': full_median,
            'new_median': reduced_median,
            'shift': shift,
            'shift_pct': abs(shift / full_median * 100) if full_median != 0 else 0,
            'influential': abs(shift / full_median * 100) > 10 if full_median != 0 else False
        })

    return results
```

### Modified Delphi for Time-Constrained Decisions

When full 4-round Delphi is impractical:

1. **Rapid Delphi (2 rounds):** Skip Round 3 analysis, go directly from Round 2 to consensus
2. **Policy Delphi (focus on options):** Instead of convergence, map the landscape of expert positions
3. **Real-Time Delphi:** Continuous updating as experts see evolving panel statistics

---

## Completeness Checklist

- [ ] Question clearly framed with scope, timeframe, and decision context
- [ ] Expert panel selected with 5-8 relevant archetypes and selection rationale documented
- [ ] Round 1 completed: all experts provided independent assessments with confidence levels
- [ ] Evidence cited by experts classified using T1-T4 evidence tiers
- [ ] Round 2 completed: all experts revised or maintained positions with justification
- [ ] Revision tracking documented: who changed, by how much, and why
- [ ] Round 3 convergence metrics calculated: IQR, relative IQR, CV, cluster analysis
- [ ] Disagreements classified: empirical, methodological, value-based, or scope-based
- [ ] Round 4 consensus position stated with quantified confidence interval
- [ ] Consensus Strength Score calculated with component breakdown (0-100)
- [ ] Minority report preserved with dissenting reasoning and monitoring conditions
- [ ] Sensitivity analysis performed (leave-one-out or similar robustness check)
- [ ] MCP tools used to gather evidence for expert assessments
- [ ] Visualization code provided (radar, box plot, convergence tracking, or agreement matrix)
- [ ] Report file created with all sections populated (no remaining placeholders)
- [ ] Actionable recommendations provided with conditions and next steps
