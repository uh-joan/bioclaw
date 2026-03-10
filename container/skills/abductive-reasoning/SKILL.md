---
name: abductive-reasoning
description: Inference to the best explanation when data is incomplete. Systematically catalogs observations, generates competing explanations, ranks them on loveliness (explanatory power) and likeliness (evidential support), and designs crucial experiments to distinguish between top candidates. Based on C.S. Peirce's abductive logic and Lipton's inference to the best explanation. Use when asked to explain unexpected findings, diagnose anomalous results, determine the most likely cause of an observation, evaluate competing explanations, investigate puzzling data, explain why something happened, or choose between rival theories. Applies to clinical observations, experimental results, drug development anomalies, disease presentations, adverse events, trial failures, and any situation where data is incomplete and multiple explanations are plausible.
---

# Abductive Reasoning

Inference to the best explanation when data is incomplete. This skill systematically catalogs observations, generates competing explanations, evaluates them on both loveliness (explanatory power) and likeliness (evidential support), and designs crucial experiments to distinguish between top candidates. Based on C.S. Peirce's abductive logic and Lipton's inference to the best explanation (IBE).

Distinct from **hypothesis-generation** (which generates hypotheses from a research question and designs experiments), **scientific-critical-thinking** (which evaluates the rigor of existing claims and studies), and **deep-research** (which investigates questions iteratively through literature). Abductive reasoning starts from *puzzling observations* and works backward to the best explanation -- it is diagnostic rather than exploratory, evaluative rather than generative.

## Report-First Workflow

1. **Create report file immediately**: `[phenomenon]_abductive_analysis_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as evidence is gathered from MCP tools
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Generating hypotheses from a research question (not from puzzling observations) -> use `hypothesis-generation`
- Evaluating the rigor of a published study or claim -> use `scientific-critical-thinking`
- Iterative literature investigation with search refinement -> use `deep-research`
- Exploring branching future scenarios -> use `what-if-oracle`
- Mapping feedback loops and systemic behavior -> use `systems-thinking`
- Decomposing a problem to fundamental principles -> use `first-principles`
- Statistical analysis of experimental data -> use `statistical-modeling`
- Adverse event causality assessment (pharmacovigilance) -> use `pharmacovigilance-specialist`

## Cross-Skill Routing

- Need to generate hypotheses from a question (not observations) -> `hypothesis-generation`
- Need to evaluate a specific study's methodology -> `scientific-critical-thinking`
- Need to investigate a component explanation through literature -> `deep-research`
- Need to model future scenarios based on best explanation -> `what-if-oracle`
- Need to understand the systemic structure producing the observation -> `systems-thinking`
- Need to run statistical tests on data underlying observations -> `statistical-modeling`
- Need molecular pathway detail for a biological explanation -> `disease-research`
- Need pharmacokinetic/pharmacodynamic analysis -> `clinical-pharmacology`
- Need variant interpretation for a genomic observation -> `variant-interpretation`

---

## Available MCP Tools

### `mcp__pubmed__pubmed_data` (Evidence for Explanations)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search PubMed by keywords, MeSH terms, author, journal | `query`, `num_results` |
| `fetch_details` | Full article metadata: abstract, authors, journal, DOI, MeSH | `pmid` |

**Abductive-specific uses:** Find evidence supporting or refuting candidate explanations, identify published case reports of similar observations, locate mechanistic studies that validate or undermine proposed explanations, find precedent for each explanation having been correct in analogous cases.

### `mcp__ctgov__ctgov_data` (Clinical Trial Context)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search clinical trials by condition, intervention, phase, status | `condition`, `intervention`, `phase`, `status`, `pageSize` |
| `get` | Full trial details by NCT ID | `nctId` |
| `stats` | Trial statistics and counts | `condition`, `intervention` |

**Abductive-specific uses:** Find trial results that support or contradict explanations, assess whether an observation matches known trial outcomes, identify trials testing specific mechanistic explanations.

### `mcp__opentargets__opentargets_data` (Biological Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId`, `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability) | `id` |
| `get_disease_details` | Disease info including associated targets and drugs | `id` |

**Abductive-specific uses:** Assess biological plausibility of explanations involving specific targets or pathways, quantify evidence strength for target-disease associations underlying candidate explanations.

### `mcp__fda__fda_data` (Regulatory and Safety Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `lookup_drug` | Search drugs by name, adverse events, labels, recalls | `search_term`, `search_type`, `limit` |
| `search_orange_book` | Find brand/generic drug products | `drug_name`, `include_generics` |

**Abductive-specific uses:** Check adverse event databases for evidence supporting drug-related explanations, find label warnings that corroborate or contradict explanations, assess regulatory precedent for similar observations.

### `mcp__chembl__chembl_data` (Compound Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |

**Abductive-specific uses:** Investigate compound-specific explanations (off-target activity, metabolite effects), find evidence for mechanism-based explanations through target activity profiles.

### `mcp__reactome__reactome_data` (Pathway Mechanisms)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_pathway` | Get pathway details | `id` |
| `get_pathway_participants` | Entities in a pathway | `id` |
| `search` | Search pathways by keyword | `query` |

**Abductive-specific uses:** Validate mechanistic explanations by checking if proposed pathway connections exist, find alternative pathways that could produce the same observation (competing explanations).

---

## Core Framework: 6-Phase Abductive Process

### Phase 1: Observation Cataloging

What do we actually observe? Be exhaustive, precise, and distinguish observation from interpretation.

**Observation Categories:**

| Category | Description | Examples |
|----------|-------------|---------|
| **Direct measurement** | Instrument readings, assay results, quantitative data | IC50 = 2.3 nM, tumor volume reduced 45%, serum creatinine elevated |
| **Clinical observation** | Practitioner-noted findings | Patient presents with rash on day 14, three subjects withdrew due to headache |
| **Reported data** | Published results, database entries | PubMed study reports 60% response rate, FAERS signal for hepatotoxicity |
| **Derived inference** | Conclusions drawn from data (mark as interpretation, not raw observation) | "Drug appears hepatotoxic" -- this is interpretation, not observation |
| **Absence** | What is conspicuously NOT observed (the dog that didn't bark) | No dose-response relationship, expected biomarker unchanged, control group also affected |

**Reliability Rating:**

| Rating | Criteria | Weight in Analysis |
|--------|----------|-------------------|
| **R1: High** | Direct measurement with validated method, replicated | Full weight |
| **R2: Moderate** | Single measurement, published data, clinical observation by expert | Standard weight |
| **R3: Low** | Reported secondhand, preliminary data, small sample | Reduced weight |
| **R4: Very Low** | Anecdotal, unconfirmed, single patient | Flag; do not base conclusions on this alone |

**Observation Cataloging Template:**

```
PHENOMENON: [What is puzzling? What needs explanation?]

OBSERVATIONS:
| # | Observation | Category | Reliability | Source | Date |
|---|------------|----------|-------------|--------|------|
| 1 | [precise description] | [direct/clinical/reported/derived] | [R1-R4] | [source] | [date] |
| 2 | ... | ... | ... | ... | ... |

CONSPICUOUS ABSENCES:
| # | Expected Observation | Why Expected | Significance of Absence |
|---|---------------------|-------------|------------------------|
| 1 | [what we expected to see but did not] | [why we expected it] | [what absence implies] |

OBSERVATION vs INTERPRETATION CHECK:
| Statement | Type | If Interpretation, Raw Observation Is |
|-----------|------|-------------------------------------|
| "Drug is hepatotoxic" | Interpretation | ALT elevated 3x ULN in 4/20 subjects |
| "ALT = 180 U/L" | Observation | -- |
```

**MCP tool usage:**
```
# Find similar observations in literature
mcp__pubmed__pubmed_data(method: "search", query: "[OBSERVATION] case report", num_results: 15)

# Check adverse event databases for similar patterns
mcp__fda__fda_data(method: "lookup_drug", search_term: "[DRUG]", search_type: "adverse_events", limit: 20)
```

---

### Phase 2: Explanation Generation

Generate ALL plausible explanations. Aim for at least 5 distinct explanations. Breadth matters more than depth at this stage.

**Explanation Generation Strategies:**

| Strategy | Description | Cognitive Function |
|----------|-------------|-------------------|
| **Obvious** | What most people would think first | Capture base-rate explanations |
| **Expert** | What a domain specialist would consider | Capture mechanistic explanations |
| **Contrarian** | What if the opposite is true? | Challenge assumptions |
| **Null** | There is nothing to explain -- it is noise, chance, artifact | Prevent false pattern detection |
| **Compound** | Multiple causes contribute simultaneously | Capture multi-factorial reality |
| **Analogical** | What explained a similar observation in another domain? | Import cross-domain insights |

**For each explanation, document:**

```
EXPLANATION [N]: [Name]
Category: [Obvious / Expert / Contrarian / Null / Compound / Analogical]
Description: [Clear, specific statement of the explanation]
Mechanism: [How would this explanation produce the observations?]
Predictions: [What else should be true if this explanation is correct?]
What it does NOT explain: [Which observations are left unexplained?]
```

**Completeness Check for Explanation Generation:**
- Did I include at least one obvious explanation?
- Did I include at least one expert/mechanistic explanation?
- Did I include a contrarian explanation?
- Did I include the null explanation?
- Did I consider compound explanations?
- Did I think about analogous cases in other domains?
- Have I avoided prematurely eliminating any explanation?

**MCP tool usage:**
```
# Find mechanistic basis for explanations
mcp__opentargets__opentargets_data(method: "get_target_details", id: "[TARGET_ID]")
mcp__reactome__reactome_data(method: "search", query: "[MECHANISM]")

# Find analogous cases
mcp__pubmed__pubmed_data(method: "search", query: "[ANALOGOUS PHENOMENON] mechanism", num_results: 10)
```

---

### Phase 3: Loveliness Ranking

Which explanation, if true, would explain the most? Loveliness measures explanatory power -- how much understanding the explanation provides.

**Loveliness Criteria:**

| Criterion | Weight | Description | Scoring Guide |
|-----------|--------|-------------|---------------|
| **Explanatory Breadth** | 25% | How many observations does it account for? | 0: few, 50: most, 100: all |
| **Explanatory Depth** | 25% | Does it explain WHY, not just WHAT? | 0: descriptive only, 50: some mechanism, 100: full causal chain |
| **Unification** | 20% | Does it connect to other known phenomena? | 0: isolated, 50: some connections, 100: unifies disparate observations |
| **Simplicity** | 15% | Does it avoid unnecessary complexity? (Occam's razor) | 0: many ad hoc assumptions, 50: moderate, 100: parsimonious |
| **Fertility** | 15% | Does it suggest new predictions or observations? | 0: no new predictions, 50: some, 100: rich testable predictions |

**Loveliness Scoring Template:**

```
EXPLANATION: [Name]

Explanatory Breadth:  [X/100] — Accounts for observations: [list #s]
                                Does NOT account for: [list #s]
Explanatory Depth:    [X/100] — Mechanism detail: [summary]
Unification:          [X/100] — Connects to: [other phenomena]
Simplicity:           [X/100] — Required assumptions: [list]
Fertility:            [X/100] — New predictions: [list]

LOVELINESS SCORE:     [Weighted average/100]
```

**Common Loveliness Pitfalls:**
- Confusing loveliness with likeliness (a lovely explanation may be unlikely)
- Over-weighting simplicity when evidence suggests genuine complexity
- Under-valuing fertility (the most useful explanations generate new questions)
- Ignoring explanatory depth (correlation is not lovely; mechanism is)

---

### Phase 4: Likeliness Ranking

Which explanation has the most evidence? Likeliness measures evidential support -- how probable the explanation is given current data.

**Likeliness Criteria:**

| Criterion | Weight | Description | Scoring Guide |
|-----------|--------|-------------|---------------|
| **Prior Probability** | 20% | How plausible was this before current observations? | 0: very implausible, 50: neutral, 100: highly expected |
| **Evidential Fit** | 30% | How well does evidence match this explanation? | 0: contradicted, 50: consistent, 100: strongly predicted |
| **Absence of Counter-evidence** | 20% | Is there evidence against this explanation? | 0: strong counter-evidence, 50: some concerns, 100: no counter-evidence |
| **Mechanism** | 15% | Is there a known mechanism? | 0: no mechanism, 50: plausible mechanism, 100: validated mechanism |
| **Precedent** | 15% | Has this explanation been correct in similar cases? | 0: never, 50: sometimes, 100: frequently |

**Likeliness Scoring Template:**

```
EXPLANATION: [Name]

Prior Probability:           [X/100] — Basis: [why this prior]
Evidential Fit:              [X/100] — Key supporting evidence: [list]
Absence of Counter-evidence: [X/100] — Counter-evidence found: [list or none]
Mechanism:                   [X/100] — Mechanism status: [validated/plausible/unknown]
Precedent:                   [X/100] — Similar cases where correct: [list]

LIKELINESS SCORE:            [Weighted average/100]
```

**Bayesian Reasoning Shortcut:**
For each explanation, ask:
- P(Explanation) = prior probability
- P(Observations | Explanation) = how expected are the observations IF this explanation is true?
- P(Observations | NOT Explanation) = how expected are the observations if this is NOT the explanation?
- If P(Obs|Exp) >> P(Obs|NOT Exp), the observations strongly favor this explanation

**MCP tool usage:**
```
# Find evidence for/against each explanation
mcp__pubmed__pubmed_data(method: "search", query: "[EXPLANATION] evidence [PHENOMENON]", num_results: 10)

# Check if mechanism is validated
mcp__opentargets__opentargets_data(method: "get_target_disease_associations", targetId: "[ID]", diseaseId: "[ID]", minScore: 0.5, size: 10)

# Find precedent
mcp__pubmed__pubmed_data(method: "search", query: "[EXPLANATION TYPE] [SIMILAR DOMAIN] confirmed", num_results: 10)
```

---

### Phase 5: Combined Assessment -- Loveliness x Likeliness Matrix

Plot explanations on a 2D matrix to identify the best candidates.

**Quadrant Interpretation:**

```
                    HIGH LIKELINESS
                         |
    Lovely but Unlikely  |  Lovely AND Likely
    (Worth investigating |  (STRONG CANDIDATES)
     -- could be right   |
     with more evidence) |
    ---------------------+---------------------
    Neither lovely       |  Likely but not Lovely
    nor likely           |  (May be true but
    (DEPRIORITIZE)       |   doesn't explain much
                         |   -- check for hidden
                         |   depth)
                         |
                    LOW LIKELINESS
```

**Combined Assessment Template:**

```
EXPLANATION RANKING:
| Rank | Explanation | Loveliness | Likeliness | Quadrant | Action |
|------|------------|-----------|-----------|----------|--------|
| 1 | [Name] | [X/100] | [X/100] | Top-right | Leading candidate |
| 2 | [Name] | [X/100] | [X/100] | Top-right | Strong alternative |
| 3 | [Name] | [X/100] | [X/100] | Top-left | Investigate further |
| 4 | [Name] | [X/100] | [X/100] | Bottom-right | Check for depth |
| 5 | [Name] | [X/100] | [X/100] | Bottom-left | Deprioritize |

BEST EXPLANATION: [Name]
Justification: [Why this ranks highest considering both loveliness and likeliness]
Key uncertainty: [What single piece of evidence would most change the ranking]
```

---

### Phase 6: Crucial Experiment Design

What observation would distinguish between the top candidate explanations?

**Crucial Experiment Principles:**
1. **Discriminating power**: The experiment must produce different results under different explanations
2. **Feasibility**: The experiment must be practically executable
3. **Decisiveness**: Pre-commit to interpretation before seeing results
4. **Falsification focus**: Design to RULE OUT explanations, not just confirm the favorite

**Crucial Experiment Template:**

```
EXPERIMENT [N]: [Name]
Purpose: Distinguish between [Explanation A] and [Explanation B]

Pre-committed interpretation:
  - If we observe [X]: favors [Explanation A], rules out [Explanation B]
  - If we observe [Y]: favors [Explanation B], rules out [Explanation A]
  - If we observe [Z]: neither -- both remain viable (uninformative outcome)

Method: [How to conduct the experiment/analysis]
Feasibility: [High/Medium/Low]
Time required: [estimate]
Cost/resources: [estimate]
Risks: [what could go wrong]

FALSIFICATION TESTS:
| Explanation | Would Be Ruled Out If | Observation Method |
|------------|----------------------|-------------------|
| [Name] | [specific observation] | [how to check] |
```

**Hierarchy of Crucial Experiments (from easiest to hardest):**

| Level | Type | Description | Example |
|-------|------|-------------|---------|
| 1 | **Literature check** | Already published data distinguishes explanations | Search PubMed for contradicting evidence |
| 2 | **Data re-analysis** | Existing data, analyzed differently, distinguishes | Subgroup analysis, different statistical test |
| 3 | **Simple experiment** | Quick, cheap, doable experiment | Check a biomarker, run an assay |
| 4 | **Designed study** | Purpose-built experiment | Prospective cohort, controlled trial |
| 5 | **Natural experiment** | Wait for natural events to distinguish | Observe outcome after policy change |

**MCP tool usage:**
```
# Check if crucial data already exists
mcp__pubmed__pubmed_data(method: "search", query: "[DISTINGUISHING OBSERVATION] [PHENOMENON]", num_results: 10)

# Find trials testing relevant mechanisms
mcp__ctgov__ctgov_data(method: "search", condition: "[CONDITION]", intervention: "[MECHANISM TEST]", pageSize: 10)
```

---

## Abductive Confidence Score (0-100)

### Score Components

| Dimension | Max Points | Criteria |
|-----------|-----------|----------|
| **Observation Quality** | 20 | Exhaustive cataloging, reliable sources, absences noted |
| **Explanation Coverage** | 20 | 5+ explanations, all strategies used, null included |
| **Loveliness Assessment** | 15 | Rigorous scoring on all 5 criteria |
| **Likeliness Assessment** | 15 | Evidence-based scoring, Bayesian reasoning applied |
| **Discrimination** | 15 | Clear separation between candidates, crucial experiments designed |
| **Actionability** | 15 | Practical next steps, pre-committed interpretations |

### Confidence Tiers

| Score | Tier | Interpretation | Recommended Action |
|-------|------|---------------|-------------------|
| **76-100** | Near-certain | Leading candidate explains all observations, alternatives implausible | Act on best explanation; monitor for disconfirmation |
| **51-75** | Probable | Leading candidate clearly ahead but not decisive | Pursue crucial experiment to confirm; act provisionally |
| **26-50** | Moderately uncertain | Leading candidate emerges but alternatives viable | Gather more evidence before committing; run Level 1-2 experiments |
| **0-25** | Highly uncertain | Multiple equally plausible explanations, no clear winner | Do not act on any single explanation; design discriminating experiments |

### Scoring Rubric

**Observation Quality (0-20):**
- 17-20: Exhaustive catalog, all R1/R2, absences noted, observation vs interpretation separated
- 13-16: Good coverage, mostly R1/R2, some absences noted
- 9-12: Adequate coverage, mixed reliability
- 5-8: Incomplete, mostly R3/R4
- 0-4: Minimal observations listed

**Explanation Coverage (0-20):**
- 17-20: 6+ explanations, all strategies used, null included, no premature elimination
- 13-16: 5 explanations, most strategies used
- 9-12: 3-4 explanations, limited strategies
- 5-8: 2-3 explanations, obvious only
- 0-4: Single explanation (not abductive reasoning)

**Loveliness Assessment (0-15):**
- 13-15: All 5 criteria scored with justification, clear ranking emerges
- 10-12: Most criteria scored, reasonable ranking
- 7-9: Partial scoring, intuitive ranking
- 4-6: Minimal scoring
- 0-3: Not assessed

**Likeliness Assessment (0-15):**
- 13-15: Evidence-based scoring on all criteria, MCP tools used, Bayesian reasoning applied
- 10-12: Evidence-based on most criteria
- 7-9: Mixed evidence and intuition
- 4-6: Mostly intuitive
- 0-3: Not assessed

**Discrimination (0-15):**
- 13-15: Clear separation, 2+ crucial experiments designed with pre-committed interpretations
- 10-12: Reasonable separation, 1 crucial experiment
- 7-9: Some separation, experiment suggested but not designed
- 4-6: Weak separation
- 0-3: Explanations not distinguished

**Actionability (0-15):**
- 13-15: Clear next steps, pre-committed interpretations, timeline, feasibility assessed
- 10-12: Good next steps, mostly pre-committed
- 7-9: Some next steps
- 4-6: Vague recommendations
- 0-3: No actionable output

---

## Python Visualization Templates

### Loveliness vs Likeliness Scatter Plot

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_loveliness_likeliness(explanations, title="Loveliness vs Likeliness Matrix"):
    """
    explanations: list of dicts with 'name', 'loveliness' (0-100), 'likeliness' (0-100),
                  'category' (obvious/expert/contrarian/null/compound/analogical)
    """
    fig, ax = plt.subplots(figsize=(10, 10))

    category_colors = {
        'obvious': '#3498db',
        'expert': '#2ecc71',
        'contrarian': '#e74c3c',
        'null': '#95a5a6',
        'compound': '#9b59b6',
        'analogical': '#f39c12',
    }

    # Draw quadrants
    ax.axhline(y=50, color='#bdc3c7', linestyle='--', linewidth=1)
    ax.axvline(x=50, color='#bdc3c7', linestyle='--', linewidth=1)

    # Quadrant labels
    ax.text(75, 95, 'STRONG CANDIDATES\n(Lovely & Likely)', ha='center', va='top',
            fontsize=10, fontweight='bold', color='#27ae60', alpha=0.5)
    ax.text(25, 95, 'WORTH INVESTIGATING\n(Lovely but Unlikely)', ha='center', va='top',
            fontsize=10, fontweight='bold', color='#f39c12', alpha=0.5)
    ax.text(75, 5, 'CHECK FOR DEPTH\n(Likely but not Lovely)', ha='center', va='bottom',
            fontsize=10, fontweight='bold', color='#3498db', alpha=0.5)
    ax.text(25, 5, 'DEPRIORITIZE\n(Neither)', ha='center', va='bottom',
            fontsize=10, fontweight='bold', color='#95a5a6', alpha=0.5)

    # Plot explanations
    for exp in explanations:
        color = category_colors.get(exp.get('category', 'obvious'), '#3498db')
        ax.scatter(exp['likeliness'], exp['loveliness'], s=200, c=color,
                   edgecolors='#2c3e50', linewidth=1.5, zorder=5)
        ax.annotate(exp['name'], (exp['likeliness'], exp['loveliness']),
                    textcoords="offset points", xytext=(10, 10),
                    fontsize=9, fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color='#7f8c8d', lw=0.8))

    ax.set_xlabel('Likeliness (Evidential Support)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Loveliness (Explanatory Power)', fontsize=12, fontweight='bold')
    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 105)
    ax.set_title(title, fontsize=14, fontweight='bold')

    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], marker='o', color='w', markerfacecolor=c,
                              markersize=10, label=cat.capitalize())
                       for cat, c in category_colors.items()]
    ax.legend(handles=legend_elements, loc='lower left', fontsize=9)

    ax.grid(True, alpha=0.2)
    plt.tight_layout()
    plt.savefig('loveliness_likeliness_matrix.png', dpi=150, bbox_inches='tight')
    plt.show()

# Example usage:
# explanations = [
#     {'name': 'Off-target activity', 'loveliness': 75, 'likeliness': 65, 'category': 'expert'},
#     {'name': 'Metabolite toxicity', 'loveliness': 80, 'likeliness': 45, 'category': 'expert'},
#     {'name': 'Dose-related', 'loveliness': 40, 'likeliness': 70, 'category': 'obvious'},
#     {'name': 'Random noise', 'loveliness': 10, 'likeliness': 30, 'category': 'null'},
#     {'name': 'Immune-mediated', 'loveliness': 85, 'likeliness': 55, 'category': 'contrarian'},
# ]
# plot_loveliness_likeliness(explanations, "ALT Elevation Analysis")
```

### Explanation Comparison Radar Chart

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_explanation_radar(explanations, title="Explanation Comparison"):
    """
    explanations: list of dicts with 'name', 'breadth', 'depth', 'unification',
                  'simplicity', 'fertility', 'prior', 'evidential_fit',
                  'no_counter', 'mechanism', 'precedent'
    """
    categories = ['Breadth', 'Depth', 'Unification', 'Simplicity', 'Fertility',
                  'Prior Prob', 'Evid. Fit', 'No Counter-evid', 'Mechanism', 'Precedent']
    N = len(categories)

    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

    colors = ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6', '#f39c12', '#1abc9c']

    for i, exp in enumerate(explanations[:6]):
        values = [exp.get(k, 50) for k in ['breadth', 'depth', 'unification', 'simplicity',
                                             'fertility', 'prior', 'evidential_fit',
                                             'no_counter', 'mechanism', 'precedent']]
        values += values[:1]
        color = colors[i % len(colors)]
        ax.plot(angles, values, 'o-', linewidth=2, label=exp['name'], color=color)
        ax.fill(angles, values, alpha=0.1, color=color)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=9)
    ax.set_ylim(0, 100)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=30)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)

    plt.tight_layout()
    plt.savefig('explanation_radar.png', dpi=150, bbox_inches='tight')
    plt.show()
```

### Crucial Experiment Decision Tree

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def plot_crucial_experiment_tree(experiments, title="Crucial Experiment Decision Tree"):
    """
    experiments: list of dicts with 'name', 'outcomes' (list of dicts with
                 'observation', 'favors', 'rules_out', 'probability')
    """
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')

    y_start = 9
    for i, exp in enumerate(experiments[:3]):
        exp_x = 1
        exp_y = y_start - i * 3.2

        # Experiment box
        exp_box = mpatches.FancyBboxPatch((exp_x - 0.5, exp_y - 0.4), 3, 0.8,
                                           boxstyle="round,pad=0.2",
                                           facecolor='#2c3e50', edgecolor='white')
        ax.add_patch(exp_box)
        ax.text(exp_x + 1, exp_y, f"Experiment {i+1}:\n{exp['name']}",
                ha='center', va='center', fontsize=8, color='white', fontweight='bold')

        for j, outcome in enumerate(exp.get('outcomes', [])[:3]):
            out_x = 7
            out_y = exp_y + 1.2 - j * 1.2

            # Arrow
            ax.annotate('', xy=(out_x - 0.5, out_y), xytext=(exp_x + 2.5, exp_y),
                        arrowprops=dict(arrowstyle='->', color='#7f8c8d', lw=1.5,
                                       connectionstyle='arc3,rad=0.1'))

            # Observation label on arrow
            mid_x = (exp_x + 2.5 + out_x - 0.5) / 2
            mid_y = (exp_y + out_y) / 2
            ax.text(mid_x, mid_y + 0.15, f"Observe: {outcome['observation']}",
                    fontsize=7, ha='center', style='italic', color='#2c3e50')

            # Outcome box
            favors_color = '#27ae60'
            out_box = mpatches.FancyBboxPatch((out_x - 0.5, out_y - 0.35), 4.5, 0.7,
                                               boxstyle="round,pad=0.2",
                                               facecolor=favors_color, alpha=0.15,
                                               edgecolor=favors_color)
            ax.add_patch(out_box)
            ax.text(out_x + 1.75, out_y + 0.05,
                    f"Favors: {outcome['favors']}", ha='center', va='center',
                    fontsize=7, fontweight='bold', color='#27ae60')
            ax.text(out_x + 1.75, out_y - 0.15,
                    f"Rules out: {outcome['rules_out']}", ha='center', va='center',
                    fontsize=7, color='#e74c3c')

            # Probability
            prob = outcome.get('probability', '')
            if prob:
                ax.text(out_x + 4.3, out_y, f"P={prob}%", fontsize=7,
                        fontweight='bold', color='#7f8c8d')

    ax.set_title(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('crucial_experiment_tree.png', dpi=150, bbox_inches='tight')
    plt.show()
```

### Confidence Evolution Chart

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_confidence_evolution(stages, explanation_scores, title="Confidence Evolution Across Evidence Stages"):
    """
    stages: list of stage names (e.g., ['Initial', 'After PubMed', 'After Lab Data', 'After Trial'])
    explanation_scores: dict of {explanation_name: [score_at_each_stage]}
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    colors = ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6', '#f39c12', '#1abc9c']
    x = np.arange(len(stages))

    for i, (name, scores) in enumerate(explanation_scores.items()):
        color = colors[i % len(colors)]
        ax.plot(x, scores, 'o-', label=name, color=color, linewidth=2, markersize=8)

        # Annotate final score
        ax.annotate(f'{scores[-1]}', (x[-1], scores[-1]),
                    textcoords="offset points", xytext=(10, 0),
                    fontsize=9, fontweight='bold', color=color)

    ax.set_xticks(x)
    ax.set_xticklabels(stages, fontsize=10)
    ax.set_ylabel('Combined Score (Loveliness + Likeliness) / 2', fontsize=11)
    ax.set_ylim(0, 100)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig('confidence_evolution.png', dpi=150, bbox_inches='tight')
    plt.show()
```

---

## Analysis Modes

### Quick Abduction (3 Explanations)

Rapid assessment with obvious, expert, and null explanations only. Complete in a single session.

**When to use:**
- Time-sensitive diagnostic situations
- Initial triage of an anomalous result
- Preliminary assessment before committing to deep analysis
- Low-stakes decisions with reversible consequences

### Deep Abduction (5-8 Explanations)

Full 6-phase process with all explanation strategies, comprehensive scoring, and crucial experiment design. Requires MCP tool evidence gathering.

**When to use:**
- Unexplained clinical trial results
- Anomalous preclinical findings that block a program decision
- Puzzling adverse events requiring causal attribution
- Complex diagnostic puzzles with patient impact
- Any situation where acting on the wrong explanation has serious consequences

### Sequential Abduction

Iterative process: run Quick Abduction, then gather evidence, then update scores and re-rank. Repeat until confidence threshold is reached.

**When to use:**
- Evidence can be gathered incrementally
- Budget or time constraints prevent full investigation upfront
- System allows staged decision-making
- Want to track how evidence changes the ranking over time

### Comparative Abduction

Apply abductive reasoning to multiple related observations simultaneously, looking for a single explanation that unifies them.

**When to use:**
- Multiple anomalous findings across related experiments
- Cluster of adverse events that may share a common cause
- Pattern of clinical trial failures in a therapeutic area
- Multiple biomarker movements that may reflect one underlying process

---

## Domain-Specific Templates

### Template 1: Unexpected Clinical Trial Result

```
PHENOMENON: [Trial] produced [unexpected result]

EXPLANATION CATEGORIES:
1. BIOLOGICAL: The drug's pharmacology genuinely produces this effect
   - On-target mechanism (expected biology, unexpected magnitude)
   - Off-target mechanism (unintended biological activity)
   - Metabolite effect (active metabolite with different profile)
   - Drug-disease interaction (disease biology modifies drug effect)

2. METHODOLOGICAL: The result is an artifact of trial design
   - Selection bias (enrolled population differs from intended)
   - Measurement artifact (endpoint sensitivity/specificity issue)
   - Statistical artifact (multiplicity, subgroup fishing, regression to mean)
   - Comparator effect (active comparator/placebo performed unexpectedly)

3. OPERATIONAL: The result reflects trial execution issues
   - Protocol deviations (non-compliance, dosing errors)
   - Site effects (regional variation, site quality)
   - Temporal effects (seasonal, pandemic, standard-of-care changes)

4. NULL: The result is within expected random variation
   - Sample size insufficient to distinguish signal from noise
   - Multiple testing without correction
   - Post-hoc observation (not pre-specified)

5. COMPOUND: Multiple factors contributing
   - Biological + methodological interaction
   - Subgroup-specific effect masked/amplified by trial design
```

### Template 2: Anomalous Preclinical Finding

```
PHENOMENON: [Experiment] showed [unexpected observation]

EXPLANATION CATEGORIES:
1. TRUE BIOLOGY: The observation reflects genuine biology
   - Known mechanism not previously linked to this context
   - Novel mechanism (new biological finding)
   - Species/model-specific effect
   - Dose/time-dependent effect at unexpected range

2. EXPERIMENTAL ARTIFACT: The observation is not real
   - Assay interference (compound properties affect readout)
   - Contamination (biological or chemical)
   - Equipment/reagent issue (batch effect, calibration)
   - Operator effect (technique variation)

3. COMPOUND-SPECIFIC: Related to the specific molecule, not the target
   - Impurity (active impurity producing the signal)
   - Physicochemical property (solubility, aggregation, non-specific binding)
   - Metabolite (in vitro metabolism generating active species)

4. NULL: Random variation within normal assay noise

5. COMPOUND: True biology amplified or masked by experimental conditions
```

### Template 3: Puzzling Clinical Presentation

```
PHENOMENON: Patient presents with [unusual combination of findings]

EXPLANATION CATEGORIES:
1. SINGLE DISEASE: One condition explains all findings
   - Common disease with atypical presentation
   - Rare disease with classic presentation
   - Advanced stage of disease with systemic effects

2. MULTIPLE DISEASES: Two or more concurrent conditions
   - Comorbidities (independent conditions coinciding)
   - Complications (one disease causing another)
   - Iatrogenic (treatment of one condition causing findings)

3. DRUG-RELATED: Medication effects
   - Expected adverse effect (dose-related)
   - Idiosyncratic reaction (unpredictable)
   - Drug-drug interaction
   - Withdrawal effect

4. NON-DISEASE: Findings do not reflect pathology
   - Normal variant (population variation)
   - Laboratory error (specimen handling, assay issue)
   - Factitious (patient-generated)

5. NULL: Incidental findings without clinical significance
```

### Template 4: Adverse Event Causality

```
PHENOMENON: [Adverse event] observed in [N] subjects taking [drug]

EXPLANATION CATEGORIES:
1. DRUG-CAUSED (on-target): Expected from pharmacology
   - Exaggerated pharmacodynamic effect
   - Mechanism-based toxicity

2. DRUG-CAUSED (off-target): Not expected from pharmacology
   - Off-target receptor/enzyme activity
   - Reactive metabolite
   - Immune-mediated (drug as hapten)

3. DISEASE-RELATED: The adverse event reflects disease progression
   - Natural disease course
   - Disease complication
   - Unmasking of pre-existing condition

4. CONCOMITANT: Other medication or environmental cause
   - Drug-drug interaction
   - Concomitant medication effect
   - Environmental exposure

5. NULL: Background rate (expected in this population regardless of drug)
   - Age-related incidence
   - Population baseline rate
   - Nocebo effect

CAUSALITY ASSESSMENT CRITERIA (Bradford Hill adapted):
- Temporal relationship (dose first, then event?)
- Dose-response (higher dose = more events?)
- Dechallenge (event resolves when drug stopped?)
- Rechallenge (event recurs when drug restarted?)
- Biological plausibility (mechanism exists?)
- Consistency (seen in other trials/drugs of class?)
- Specificity (event pattern characteristic of drug class?)
```

---

## Multi-Agent Workflow Examples

### Example 1: "Why did our Phase 2 NASH trial show efficacy on liver enzymes but not on histology?"

1. **Abductive Reasoning (this skill)** -> Catalog observations (enzyme improvement, histology failure, dose-response pattern, subgroup data). Generate explanations: (a) wrong endpoint sensitivity, (b) treatment duration too short for fibrosis resolution, (c) enzyme effect is off-target/anti-inflammatory not anti-fibrotic, (d) histological assessment variability, (e) null -- enzymes improved by chance. Score loveliness/likeliness. Design crucial experiments (extended treatment cohort, paired biopsy timing, mechanism biomarkers).
2. **Clinical Trial Analyst** -> Analyze trial design and endpoint selection for methodological issues
3. **Disease Research** -> Investigate NASH pathophysiology to evaluate biological explanations
4. **Statistical Modeling** -> Power analysis for histology endpoint, assess enzyme-histology correlation

### Example 2: "Three patients in our oncology trial developed unexpected autoimmune symptoms"

1. **Abductive Reasoning (this skill)** -> Catalog all three presentations (timing, severity, organ systems, concomitant medications, medical history). Generate explanations: (a) on-target immune activation, (b) off-target autoimmune trigger, (c) unmasked pre-existing autoimmunity, (d) concomitant medication interaction, (e) background rate in cancer population. Score and rank. Design crucial experiments (autoantibody panel, HLA typing, dechallenge/rechallenge).
2. **Pharmacovigilance Specialist** -> Formal causality assessment and signal evaluation
3. **Immunotherapy Response Predictor** -> Assess immune-related adverse event risk factors
4. **Clinical Pharmacology** -> PK/PD analysis for dose-exposure-response relationship

### Example 3: "Our lead compound shows potent activity in vitro but no efficacy in vivo"

1. **Abductive Reasoning (this skill)** -> Catalog observations (in vitro IC50, in vivo PK, in vivo efficacy data, model characteristics). Generate explanations: (a) insufficient exposure (PK issue), (b) target not relevant in vivo, (c) compensatory pathway activation in vivo, (d) model doesn't recapitulate human disease, (e) plasma protein binding reducing free drug, (f) null -- efficacy signal too weak for in vivo detection. Design crucial experiments (PK/PD correlation, target engagement biomarker, alternative model).
2. **Clinical Pharmacology** -> PK analysis and free drug concentration assessment
3. **Drug Target Validator** -> Target validation in the specific disease model used
4. **Systems Thinking** -> Map compensatory feedback loops that may negate drug effect in vivo

### Example 4: "A known drug is showing unexpected benefit in an unrelated disease"

1. **Abductive Reasoning (this skill)** -> Catalog the evidence (clinical observations, epidemiological data, any mechanistic hints). Generate explanations: (a) direct pharmacological effect on disease pathway, (b) indirect effect via metabolite, (c) anti-inflammatory effect benefiting any inflammatory condition, (d) confounding by indication (patients taking drug differ systematically), (e) reporting bias, (f) shared genetic risk factor. Score loveliness (which explanation is most fertile for drug repurposing) and likeliness (which has most evidence).
2. **Drug Repurposing Analyst** -> Systematic assessment of repurposing potential
3. **Network Pharmacologist** -> Map drug's full interaction network for mechanistic explanation
4. **Deep Research** -> Literature investigation of proposed mechanisms

### Example 5: "GWAS identified a locus with no known gene function -- what does it do?"

1. **Abductive Reasoning (this skill)** -> Catalog observations (GWAS signal strength, LD structure, nearby genes, tissue-specific expression, epigenetic marks). Generate explanations: (a) regulatory element controlling distant gene, (b) novel non-coding RNA, (c) structural variant tagged by SNP, (d) gene desert with unknown long-range enhancer, (e) null -- false positive due to population stratification. Design crucial experiments (eQTL analysis, chromatin conformation, CRISPR perturbation).
2. **Regulatory Genomics** -> Detailed epigenomic and regulatory element analysis
3. **GWAS SNP Interpretation** -> Fine-mapping and credible set analysis
4. **GTEx Expression** -> Tissue-specific expression patterns for nearby genes

---

## Evidence Grading for Abductive Analysis

| Tier | Label | Criteria | Abductive Application |
|------|-------|----------|----------------------|
| **T1** | Definitive | Direct experimental evidence, replicated findings | Strong support for or against an explanation |
| **T2** | Strong | Published peer-reviewed data, established mechanisms | Reliable basis for scoring likeliness |
| **T3** | Emerging | Conference data, preprints, preliminary studies | Suggestive but requires confirmation |
| **T4** | Inferred | Expert opinion, analogy, theoretical reasoning | Basis for generating explanations but not scoring |

**Rules:** Weight T1/T2 evidence heavily in likeliness scoring. T3/T4 can contribute to loveliness (explanatory potential) but should not drive likeliness scores above 50 without higher-tier support. Flag when the leading explanation relies primarily on T3/T4 evidence.

---

## Report Template

```
# Abductive Analysis: [Phenomenon]
Generated: [DATE]
Analysis Mode: [Quick / Deep / Sequential / Comparative]
Abductive Confidence: [X/100] ([Tier])

## 1. Executive Summary
[2-3 paragraphs: phenomenon, best explanation, confidence level,
 recommended crucial experiment, and next steps]

## 2. Observations
| # | Observation | Category | Reliability | Source | Date |
|---|------------|----------|-------------|--------|------|
[Complete table]

## 3. Conspicuous Absences
| # | Expected Observation | Why Expected | Significance of Absence |
|---|---------------------|-------------|------------------------|
[Complete table]

## 4. Candidate Explanations

### Explanation 1: [Name]
- Category: [obvious/expert/contrarian/null/compound/analogical]
- Description: [clear statement]
- Mechanism: [how it produces the observations]
- Loveliness: [X/100]
  - Breadth: [X] | Depth: [X] | Unification: [X] | Simplicity: [X] | Fertility: [X]
- Likeliness: [X/100]
  - Prior: [X] | Evidential fit: [X] | No counter-evidence: [X] | Mechanism: [X] | Precedent: [X]
- Key evidence for: [list]
- Key evidence against: [list]
- Predictions if correct: [list]

[Repeat for each explanation]

## 5. Loveliness x Likeliness Matrix
[Python scatter plot -- see visualization template]

| Rank | Explanation | Loveliness | Likeliness | Quadrant |
|------|------------|-----------|-----------|----------|
[Ranked table]

## 6. Best Explanation: [Name]
- Abductive Confidence: [X/100]
- Why this over alternatives: [reasoning]
- Key remaining uncertainty: [what could change the ranking]

## 7. Crucial Experiments
| # | Experiment | Distinguishes Between | Pre-committed Interpretation | Feasibility | Priority |
|---|-----------|----------------------|----------------------------|-------------|----------|
[Complete table]

### Experiment 1: [Name]
- If observe [X]: favors [Explanation A], rules out [Explanation B]
- If observe [Y]: favors [Explanation B], rules out [Explanation A]
- Method: [description]
- Timeline: [estimate]

## 8. Falsification Tests
| Explanation | Would Be Ruled Out If | How to Check |
|------------|----------------------|-------------|
[Complete table]

## 9. Remaining Uncertainty
- What we still don't know: [list]
- What would increase confidence most: [single most valuable piece of evidence]
- Risk of acting on current best explanation: [assessment]

## 10. Abductive Confidence Score Breakdown
| Dimension | Score | Max | Rationale |
|-----------|-------|-----|-----------|
| Observation Quality | [X] | 20 | |
| Explanation Coverage | [X] | 20 | |
| Loveliness Assessment | [X] | 15 | |
| Likeliness Assessment | [X] | 15 | |
| Discrimination | [X] | 15 | |
| Actionability | [X] | 15 | |
| **TOTAL** | **[X]** | **100** | **[Tier]** |

## 11. Next Steps
[Specific actions with owners, timelines, and decision criteria]
```

---

## Completeness Checklist

- [ ] Phenomenon clearly stated as a puzzling observation requiring explanation
- [ ] All observations cataloged with category and reliability rating (R1-R4)
- [ ] Observation vs interpretation distinguished for each data point
- [ ] Conspicuous absences identified and their significance assessed
- [ ] At least 5 candidate explanations generated
- [ ] All explanation strategies used (obvious, expert, contrarian, null, compound)
- [ ] No explanations prematurely eliminated before scoring
- [ ] Loveliness scored on all 5 criteria (breadth, depth, unification, simplicity, fertility)
- [ ] Likeliness scored on all 5 criteria (prior, evidential fit, counter-evidence, mechanism, precedent)
- [ ] MCP tools used to gather evidence for scoring (PubMed, Open Targets, FDA, etc.)
- [ ] Loveliness x Likeliness matrix plotted with quadrant assignments
- [ ] Best explanation identified with justification for ranking
- [ ] At least 2 crucial experiments designed with pre-committed interpretations
- [ ] Falsification tests defined for each top candidate
- [ ] Experiments prioritized by feasibility and discriminating power
- [ ] Abductive Confidence Score calculated with dimension-by-dimension breakdown
- [ ] Evidence tiers (T1-T4) assigned to key data points supporting each explanation
- [ ] Remaining uncertainty explicitly cataloged
- [ ] Risk of acting on current best explanation assessed
- [ ] Report file created with all sections populated (no remaining placeholders)
- [ ] Visualization code provided for loveliness/likeliness matrix
