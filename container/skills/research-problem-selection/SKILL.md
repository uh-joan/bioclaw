---
name: research-problem-selection
description: Strategic research problem selection and evaluation framework. Nine-phase structured methodology for choosing what research problems to work on, based on the principle that problem choice matters more than execution quality. Covers intuition pumps for idea generation, risk assessment, optimization functions, parameter strategy, decision trees for execution vs strategic evaluation, adversity planning, problem inversion, integration and synthesis, and meta-framework orchestration. Use when user mentions choosing a research problem, evaluating research directions, research strategy, problem selection, research prioritization, which problem to work on, research portfolio, idea evaluation, pivoting research direction, research impact assessment, or strategic research planning.
---

# Research Problem Selection Framework

A nine-phase structured methodology for choosing what research problems to work on. Based on the insight from Fischbach & Walsh (Cell, 2024) that **"Problem Choice >> Execution Quality"** — the most important decision in a research career is not how well you execute, but what you choose to work on.

This framework transforms problem selection from an intuitive, ad-hoc process into a rigorous, repeatable methodology. It is designed for researchers at any career stage — from PhD students selecting dissertation topics to PIs redirecting lab focus to industry R&D leaders allocating portfolio resources.

## Report-First Workflow

1. **Create report file immediately**: `research_problem_selection_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Evaluating...]`
3. **Populate progressively**: Update sections as each phase is completed
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Evaluating...]` placeholders remain

## When NOT to Use This Skill

- Evaluating a specific hypothesis -> use `hypothesis-generation`
- Designing an experiment for a chosen problem -> use `experimental-design`
- Critiquing methodology of an existing study -> use `scientific-critical-thinking`
- Deep literature investigation of a topic -> use `literature-deep-research`
- Writing a grant proposal for a chosen problem -> use `scientific-writing`

## Cross-Skill Routing

- **After problem selection (downstream)** -> use `hypothesis-generation` to generate testable hypotheses for the chosen problem
- **After hypothesis generation (downstream)** -> use `experimental-design` to design experiments that test the hypotheses
- **Evaluating reasoning quality (complementary)** -> use `scientific-critical-thinking` to stress-test assumptions in the problem framing
- **Literature landscape (input)** -> use `literature-deep-research` to map the field before applying the framework
- **Questioning assumptions (complementary)** -> use `socratic-inquiry` to challenge problem framing through guided questioning

---

## Available MCP Tools

### `mcp__pubmed__pubmed_data` (Literature Landscape)

| Method | Problem Selection Use | Key Parameters |
|--------|----------------------|----------------|
| `search_keywords` | Map field activity and identify gaps | `keywords`, `num_results` |
| `search_advanced` | Track publication trends, identify declining/emerging areas | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Extract key findings and methodologies from landmark papers | `pmid` |

### `mcp__biorxiv__biorxiv_data` (Emerging Directions)

| Method | Problem Selection Use | Key Parameters |
|--------|----------------------|----------------|
| `search_preprints` | Identify cutting-edge work not yet published | `query`, `server`, `limit` |
| `get_preprint_details` | Assess novelty and momentum of emerging directions | `doi` |

### `mcp__ctgov__ctgov_data` (Translational Relevance)

| Method | Problem Selection Use | Key Parameters |
|--------|----------------------|----------------|
| `search` | Assess clinical translation potential | `query`, `num_results` |
| `get` | Evaluate investment in related clinical work | `nct_id` |

---

## Phase 1: Intuition Pumps — Idea Generation

### The Perturbation x Measurement x Theory Framework

Every research problem can be decomposed into three dimensions:

```
PERTURBATION (what you change):
  - Genetic: knockout, knockdown, overexpression, CRISPR edit, transgenic
  - Chemical: drug, small molecule, natural product, toxin
  - Physical: temperature, pressure, radiation, mechanical force
  - Biological: infection, co-culture, microbiome manipulation
  - Computational: parameter sweep, architecture change, data augmentation
  - Observational: natural variation, disease cohort, longitudinal follow-up

MEASUREMENT (what you observe):
  - Molecular: transcriptomics, proteomics, metabolomics, epigenomics
  - Cellular: viability, proliferation, migration, morphology, signaling
  - Tissue/Organ: histology, imaging, function tests
  - Organism: behavior, survival, disease progression, phenotype
  - Population: epidemiology, evolutionary dynamics
  - Computational: performance metrics, convergence, generalization

THEORY (what you predict):
  - Mechanistic: pathway X controls phenotype Y via intermediate Z
  - Correlative: factor A associates with outcome B
  - Causal: intervention C produces effect D through mechanism E
  - Evolutionary: trait F evolved under selection pressure G
  - Engineering: system H achieves performance I under constraint J
```

### Technology vs Logic Dimensions

| Dimension | Technology-Limited Problem | Logic-Limited Problem |
|-----------|--------------------------|----------------------|
| **Definition** | We know what to measure but lack the tools | We have the tools but don't know what to ask |
| **Example** | "We need single-cell resolution in vivo" | "What controls cell fate decisions?" |
| **Advancement** | New instruments, reagents, protocols | New frameworks, models, conceptual insights |
| **Risk profile** | Lower — clear success criteria | Higher — may not converge |
| **Reward profile** | Enables many downstream studies | Redefines the field |
| **Career fit** | Methods-oriented researchers | Conceptual thinkers |

### Seven Intuition Pumps

Apply each pump systematically to generate candidate problems:

#### Pump 1: "Make It Systematic"

```
PROMPT: "What is currently done in an ad-hoc, case-by-case manner
        that could be made systematic?"

PROCESS:
  1. Identify a common research practice in your field
  2. Ask: Is there a principled framework missing?
  3. Ask: Would systematization change conclusions?

EXAMPLES:
  - Drug dosing is often empirical -> systematic PK/PD modeling
  - Cell line selection is often convenience-based -> systematic panel screening
  - Feature engineering is often manual -> automated feature learning

OUTPUT FORMAT:
  Current practice: [description]
  Systematic alternative: [description]
  What changes: [consequences of systematization]
  Feasibility: [1-5 scale with justification]
```

#### Pump 2: "I Can't Imagine Test"

```
PROMPT: "What would have to be true for the opposite of the
        consensus to hold?"

PROCESS:
  1. State the dominant model or assumption in your field
  2. Invert it completely
  3. Ask: What evidence would support the inversion?
  4. Ask: Has anyone looked for this evidence?

EXAMPLES:
  - Consensus: Aging is driven by accumulated damage
    Inversion: Aging is a programmed developmental process
    Evidence needed: Genetic programs that actively cause aging
  - Consensus: Deep learning needs massive labeled data
    Inversion: Deep learning can work with minimal labels
    Evidence needed: Few-shot methods matching supervised performance

OUTPUT FORMAT:
  Consensus: [dominant view]
  Inversion: [opposite claim]
  Evidence that would support inversion: [specific observations]
  Has anyone looked? [literature check]
  Feasibility of testing: [1-5 scale]
```

#### Pump 3: "Reversibility Test"

```
PROMPT: "What processes that are considered irreversible might
        actually be reversible under the right conditions?"

PROCESS:
  1. Identify a biological/physical process assumed irreversible
  2. Ask: What evidence exists for partial reversibility?
  3. Ask: What conditions might enable full reversal?

EXAMPLES:
  - Fibrosis was considered irreversible -> now known to be partially reversible
  - Cell differentiation was considered terminal -> iPSC reprogramming
  - Antibiotic resistance was considered permanent -> fitness costs enable reversion
```

#### Pump 4: "Scale Shift"

```
PROMPT: "What happens when you study this phenomenon at a
        dramatically different scale (spatial, temporal, population)?"

PROCESS:
  1. Identify the typical scale at which a phenomenon is studied
  2. Shift up 3+ orders of magnitude
  3. Shift down 3+ orders of magnitude
  4. Ask: Do new phenomena emerge at different scales?

EXAMPLES:
  - Gene regulation studied at single-gene level -> genome-wide regulatory networks
  - Drug response at population level -> single-cell pharmacology
  - Neural activity at seconds -> millisecond dynamics reveal oscillatory codes
```

#### Pump 5: "Missing Link"

```
PROMPT: "What connects two well-studied phenomena that have
        never been linked?"

PROCESS:
  1. List two well-established findings in your field
  2. Ask: Is there a mechanistic connection between them?
  3. Ask: Would discovering this connection change either field?
  4. Search literature for the intersection

EXAMPLES:
  - Circadian rhythms + drug metabolism -> chronopharmacology
  - Gut microbiome + cancer immunotherapy -> microbiome-immune-tumor axis
  - Phase separation + gene regulation -> biomolecular condensates
```

#### Pump 6: "Tool Trigger"

```
PROMPT: "What new technology has just become available, and what
        question can it uniquely answer?"

PROCESS:
  1. Identify a new technique, instrument, or computational method
  2. Ask: What was previously impossible that is now feasible?
  3. Ask: What existing questions can now be answered definitively?
  4. Check biorxiv for early adopter studies

EXAMPLES:
  - Spatial transcriptomics -> "Where in the tissue does X happen?"
  - AlphaFold2 -> "What does this protein structure tell us about function?"
  - Large language models -> "Can we mine unstructured clinical notes at scale?"
```

#### Pump 7: "Failure Forensics"

```
PROMPT: "What high-profile failures in the field might reveal
        something fundamental if properly analyzed?"

PROCESS:
  1. Identify a major clinical trial failure or retracted finding
  2. Ask: What assumption was wrong?
  3. Ask: Does the failure reveal a new biological principle?

EXAMPLES:
  - Failed Alzheimer's amyloid trials -> What if amyloid is effect, not cause?
  - Failed cancer vaccine trials -> What if immune evasion is the bottleneck?
  - Irreproducible findings -> What biological variability is being missed?
```

### Phase 1 Output Template

```markdown
# Ideation Document (2 pages max)

## Candidate Problems Generated

### Problem 1: [Title]
- **Pump used**: [which intuition pump]
- **One-sentence statement**: [crisp problem statement]
- **Perturbation**: [what would be changed/observed]
- **Measurement**: [what would be measured]
- **Theory**: [what prediction would be tested]
- **Technology vs Logic**: [which dimension dominates]
- **Novelty signal**: [why this hasn't been done]

### Problem 2: [Title]
[same structure]

### Problem 3: [Title]
[same structure]

## Initial Ranking
| Problem | Excitement (1-5) | Feasibility (1-5) | Novelty (1-5) | Priority |
|---------|------------------|-------------------|----------------|----------|
| 1       |                  |                   |                |          |
| 2       |                  |                   |                |          |
| 3       |                  |                   |                |          |
```

---

## Phase 2: Risk Assessment — Likelihood x Impact

### Two-Axis Evaluation Framework

```
                    HIGH IMPACT
                        |
    "Long Shots"        |        "Sweet Spot"
    (moonshots,         |        (high-impact,
     high risk)         |         achievable)
                        |
   LOW LIKELIHOOD ------+------ HIGH LIKELIHOOD
                        |
    "Avoid"             |        "Low-Hanging Fruit"
    (low impact,        |        (publishable but
     low probability)   |         incremental)
                        |
                    LOW IMPACT
```

### Eight-Phase Risk Scoring

For each candidate problem, score on eight risk dimensions:

| Risk Dimension | 1 (Low Risk) | 3 (Moderate) | 5 (High Risk) |
|---------------|-------------|--------------|---------------|
| **Technical feasibility** | Established methods exist | Methods exist but need adaptation | Methods don't exist yet |
| **Resource requirements** | Within current budget/personnel | Needs 1-2 additional resources | Needs major new investment |
| **Timeline** | Completable in 6-12 months | 1-2 years | 3+ years |
| **Competition** | No active competitors | 2-3 competing groups | Crowded field, well-funded competitors |
| **Preliminary data** | Strong pilot data in hand | Some supporting evidence | Purely theoretical motivation |
| **Expertise match** | Core competency of the group | Partial overlap, trainable gap | Requires entirely new expertise |
| **Collaboration dependency** | Fully independent | Needs 1 collaborator | Depends on multiple external groups |
| **Regulatory/ethical** | No special approvals needed | Standard IRB/IACUC | Novel ethical territory |

### Risk Score Calculation

```python
def calculate_risk_score(scores: dict) -> dict:
    """
    Calculate composite risk score from eight dimensions.

    scores = {
        "technical_feasibility": 3,
        "resource_requirements": 2,
        "timeline": 4,
        "competition": 2,
        "preliminary_data": 3,
        "expertise_match": 1,
        "collaboration_dependency": 2,
        "regulatory_ethical": 1
    }
    """
    weights = {
        "technical_feasibility": 0.20,     # Most important
        "preliminary_data": 0.15,
        "resource_requirements": 0.15,
        "timeline": 0.10,
        "competition": 0.10,
        "expertise_match": 0.10,
        "collaboration_dependency": 0.10,
        "regulatory_ethical": 0.10
    }

    weighted_score = sum(scores[k] * weights[k] for k in scores)
    max_possible = 5.0

    risk_level = "LOW" if weighted_score < 2.0 else "MODERATE" if weighted_score < 3.5 else "HIGH"

    return {
        "composite_score": round(weighted_score, 2),
        "risk_level": risk_level,
        "highest_risk_factor": max(scores, key=scores.get),
        "lowest_risk_factor": min(scores, key=scores.get),
        "recommendation": (
            "Proceed with confidence" if risk_level == "LOW" else
            "Proceed with mitigation plan" if risk_level == "MODERATE" else
            "Consider pivoting or de-risking before committing"
        )
    }
```

### Go/No-Go Experiment Design

Before committing to a multi-year problem, design a "go/no-go" experiment:

```
GO/NO-GO EXPERIMENT TEMPLATE:

Question: Can we achieve [minimum viable result] within [timeframe]?

Design:
  Duration: 2-4 weeks (maximum 8 weeks)
  Resources: [minimal resource commitment]
  Success criterion: [specific, measurable threshold]
  Failure criterion: [what would make you abandon this direction]

Go signal: [positive result specification]
  -> Proceed to full project with confidence

Caution signal: [ambiguous result specification]
  -> Design follow-up go/no-go with different approach

No-go signal: [negative result specification]
  -> Pivot to next candidate problem

EXAMPLE:
  Problem: "Can we predict drug response from tumor organoid cultures?"
  Go/no-go: Grow 10 patient-derived organoids, test 3 drugs.
  Go: >= 7/10 cultures viable, >= 2 drugs show differential response
  Caution: 5-6/10 viable, or uniform response
  No-go: < 5/10 viable, or technical failure of culture system
  Timeline: 4 weeks
  Cost: ~$5,000 in consumables
```

### Mitigation Strategy Development

For each high-risk dimension (score >= 4), develop a mitigation:

```
RISK: [dimension name] - Score: [X/5]
SPECIFIC CONCERN: [what could go wrong]
MITIGATION:
  Primary: [main strategy to reduce risk]
  Backup: [fallback if primary mitigation fails]
  Early warning: [leading indicator that risk is materializing]
  Decision point: [when to invoke backup plan]
```

---

## Phase 3: Optimization Function — Success Metric Selection

### Domain-Specific Optimization Functions

The optimization function defines what "success" means. Different research domains optimize for different objectives:

#### Basic Science: Novelty x Generality

```
SUCCESS = Novelty x Generality

Novelty (0-10):
  0-2: Incremental extension of known results
  3-4: New data on known mechanism
  5-6: New mechanism in a specific system
  7-8: New mechanism with broad implications
  9-10: Paradigm-shifting discovery

Generality (0-10):
  0-2: Applies only to the specific model system
  3-4: Applies to a class of similar systems
  5-6: Applies broadly within one field
  7-8: Applies across multiple fields
  9-10: Universal principle

SCORING:
  Score = Novelty x Generality (0-100)
  0-20: Not worth pursuing (incremental or narrow)
  21-40: Publishable but limited impact
  41-60: Solid contribution, good journal
  61-80: High-impact, top-tier journal
  81-100: Potential Nobel/Breakthrough Prize territory
```

#### Technology Development: Adoption x Criticality

```
SUCCESS = Adoption Potential x Criticality

Adoption Potential (0-10):
  0-2: Niche application, few users
  3-4: Useful to a research community
  5-6: Useful across multiple communities
  7-8: Industry adoption potential
  9-10: Becomes standard practice

Criticality (0-10):
  0-2: Nice-to-have improvement
  3-4: Notable improvement over alternatives
  5-6: Significantly better than existing tools
  7-8: Enables previously impossible experiments
  9-10: No viable alternative exists
```

#### Invention / Translation: Goodness x Scale

```
SUCCESS = Goodness x Scale

Goodness (0-10):
  How much better than the current standard of care/practice?
  0-2: Marginal improvement
  3-4: Noticeable improvement
  5-6: Substantial improvement
  7-8: Transformative for affected population
  9-10: Complete solution to the problem

Scale (0-10):
  How many people/systems/processes are affected?
  0-2: Rare condition/niche application (<10K affected)
  3-4: Uncommon condition (10K-100K)
  5-6: Common condition (100K-1M)
  7-8: Very common (1M-100M)
  9-10: Universal (>100M)
```

### Phase 3 Output Template

```markdown
# Impact Assessment (2 pages max)

## Optimization Function Selected
- **Domain**: [Basic Science / Technology / Invention]
- **Function**: [Novelty x Generality / Adoption x Criticality / Goodness x Scale]

## Scoring for Each Candidate Problem

### Problem 1: [Title]
- **Dimension 1 score**: [X/10] — [justification]
- **Dimension 2 score**: [Y/10] — [justification]
- **Composite score**: [X*Y/100]
- **Comparison to field median**: [above/below/at]

### Problem 2: [Title]
[same structure]

## Ranking by Optimization Function
| Problem | Dim 1 | Dim 2 | Composite | Risk Score | Adjusted Priority |
|---------|-------|-------|-----------|------------|-------------------|
| 1       |       |       |           |            |                   |
| 2       |       |       |           |            |                   |

## Impact Narrative
[2-3 paragraphs explaining why the top-ranked problem matters]
```

---

## Phase 4: Parameter Strategy — Strategic Constraint Selection

### The Fix-One-Let-Others-Float Principle

In any research problem, you choose which parameters to fix (constrain) and which to let vary. The strategy of constraint selection determines the shape of the discovery space.

```
PARAMETER CATEGORIES:

1. FIXED PARAMETERS (chosen, held constant):
   - Model system (e.g., "we use C. elegans")
   - Technique (e.g., "we use single-cell RNA-seq")
   - Disease area (e.g., "we study Parkinson's")
   - Time horizon (e.g., "3-year project")

2. FLOATING PARAMETERS (allowed to vary):
   - Specific genes/targets within the system
   - Experimental conditions
   - Analysis approaches
   - Specific hypotheses

3. IMPLICIT CONSTRAINTS (assumed, often unexamined):
   - Available equipment and expertise
   - Funding agency priorities
   - Career stage considerations
   - Institutional strengths
```

### Constraint Balancing Framework

```
TOO FEW CONSTRAINTS:
  Problem: "Understand cancer"
  Issue: No actionable research direction
  Fix: Add specificity — which cancer? which mechanism? which population?

APPROPRIATE CONSTRAINTS:
  Problem: "How does KRAS G12C drive resistance to immunotherapy in NSCLC"
  Fixed: gene (KRAS G12C), disease (NSCLC), context (immunotherapy resistance)
  Floating: mechanism, cell types involved, biomarkers, therapeutic approach

TOO MANY CONSTRAINTS:
  Problem: "Does KRAS G12C increase PD-L1 in A549 cells at 24h with 10uM sotorasib"
  Issue: Single experiment, not a research program
  Fix: Remove constraints — broader mechanism, multiple models, time course
```

### Decision Matrix: What to Fix

| Fix This When... | Example | Advantage | Risk |
|-----------------|---------|-----------|------|
| **Your lab has unique expertise** | Fix technique to one you mastered | Deep methodological insight | Miss complementary approaches |
| **There's a clear clinical need** | Fix disease area | Translational relevance | May miss mechanistic generality |
| **One model system is dominant** | Fix model organism | Community, reagents, data available | Species-specific artifacts |
| **You have existing data** | Fix dataset or cohort | Leverage sunk cost | Data limitations constrain questions |
| **Funding specifies** | Fix to grant scope | Resource access | May not be optimal scientific choice |

---

## Phase 5: Decision Tree — Execution vs Strategic Evaluation

### Four-Level Oscillation Framework

Research requires constant oscillation between doing the work (execution) and evaluating whether the work is worth doing (strategy). This decision tree structures that oscillation:

```
LEVEL 1: Daily Execution
  Focus: "Am I doing this experiment/analysis correctly?"
  Frequency: Daily
  Time: 10 minutes reflection at end of each day
  Questions:
    - Did today's results match expectations?
    - Are there technical issues to troubleshoot?
    - What is tomorrow's priority?
  Action: Continue execution or adjust technique

      ↕ Trigger: unexpected result, technical failure, or weekly cadence

LEVEL 2: Weekly Reflection
  Focus: "Am I asking the right sub-question?"
  Frequency: Weekly
  Time: 30-60 minutes, Friday afternoon
  Questions:
    - Do this week's results support or refute the working hypothesis?
    - Should I change the experimental approach?
    - Am I spending time on the highest-priority experiment?
    - Is there a faster/cheaper way to get the same answer?
  Action: Adjust experimental plan or escalate to Level 3

      ↕ Trigger: accumulated evidence, paper published by competitor, or monthly cadence

LEVEL 3: Monthly Field Review
  Focus: "Am I working on the right problem?"
  Frequency: Monthly
  Time: 2-4 hours, dedicated session
  Questions:
    - Has new literature changed the landscape?
    - Is my problem still novel, or has someone else solved it?
    - Am I making sufficient progress to justify continued investment?
    - Should I pivot, expand, or narrow the problem?
  Action: Continue, pivot, or escalate to Level 4

      ↕ Trigger: major field development, grant cycle, or quarterly cadence

LEVEL 4: Quarterly Mentor/Advisor Check-In
  Focus: "Is this problem the best use of my career capital?"
  Frequency: Quarterly
  Time: 1-2 hour discussion with mentor/advisor
  Questions:
    - How does this problem fit into my overall career trajectory?
    - Am I building transferable skills and a coherent narrative?
    - What opportunities am I missing by focusing on this problem?
    - What would my ideal research portfolio look like in 3-5 years?
  Action: Major strategic decisions — continue, pivot, or start new direction
```

### Escalation Triggers

| Trigger | From Level | To Level | Example |
|---------|-----------|---------|---------|
| Unexpected negative result | 1 | 2 | Key experiment fails reproducibly |
| Three weeks without progress | 2 | 3 | Hypothesis may be wrong, not just technique |
| Competitor preprint on same problem | 3 | 3 or 4 | Someone published your planned experiment |
| Major technology breakthrough | 3 | 4 | New tool makes current approach obsolete |
| Funding decision | 4 | 4 | Grant not funded, need to restructure |
| Career transition | 4 | 4 | Job market, tenure decision approaching |

---

## Phase 6: Adversity Planning — Reframing Crises as Growth

### Failure Mode Anticipation

For each candidate problem, anticipate the most likely failure modes:

```
FAILURE MODE TEMPLATE:

Mode: [description of what goes wrong]
Probability: [low / medium / high]
Impact: [what is lost if this happens]
Detection: [how you'll know this is happening]
Response options:
  A) [pivot to related question]
  B) [change approach to same question]
  C) [publish partial/negative results]
  D) [abandon and start new direction]
Estimated recovery time: [weeks/months]
```

### Common Research Failure Modes

| Failure Mode | Detection Signal | Best Response |
|-------------|-----------------|---------------|
| Hypothesis is wrong | Consistent negative results across multiple approaches | Publish negative result, pivot to mechanism that IS operating |
| Someone publishes first | Preprint or publication appears | Differentiate (different angle, better data, different model) or accelerate |
| Technical roadblock | Method doesn't work despite optimization | Switch method, collaborate with expert, or redefine endpoint |
| Resource depletion | Funding ends, key person leaves | Seek bridge funding, simplify design, prioritize publishable subset |
| Regulatory barrier | IRB/IACUC/FDA delays or rejections | Modify protocol, use alternative models, engage regulatory consultant |
| Data quality issues | High variability, batch effects, missing data | Add controls, increase n, switch platforms, reassess feasibility |

### Ensemble Thinking for Parallel Paths

Don't bet everything on one path. Structure your research as a portfolio:

```
PORTFOLIO STRUCTURE:

Core project (60% effort):
  - Main research problem
  - Highest risk/reward
  - 1-3 year timeline

Satellite project 1 (20% effort):
  - Related problem that builds on same techniques
  - Lower risk, publishable independently
  - 6-12 month timeline

Satellite project 2 (15% effort):
  - Methodological contribution or review
  - Low risk, high probability of publication
  - 3-6 month timeline

Exploration (5% effort):
  - Reading outside your field
  - Attending talks in unrelated areas
  - "What if?" conversations
  - Source of next problem after current ones resolve
```

---

## Phase 7: Problem Inversion — Three Reframing Strategies

When stuck or when a problem seems intractable, apply these three inversion strategies:

### Strategy 1: Unfix Parameters

```
CURRENT FRAMING: "How does mutation X cause disease Y in model Z?"
  Fixed: mutation (X), disease (Y), model (Z)
  Issue: Maybe mutation X doesn't cause disease Y

UNFIXED: "What does mutation X actually do in model Z?"
  Released: disease Y (the expected outcome)
  Advantage: Discover what the mutation actually does, which may be unexpected
  Risk: Open-ended, may not converge

ALTERNATIVE UNFIX: "What causes disease Y?"
  Released: mutation X (the expected cause)
  Advantage: Unbiased screen for all causes
  Risk: Much larger problem space
```

### Strategy 2: Comparable Goal Substitution

```
CURRENT GOAL: "Cure Alzheimer's disease"
  Issue: Too ambitious for a single research project

COMPARABLE GOAL 1: "Delay Alzheimer's onset by 5 years"
  Why comparable: 5-year delay reduces prevalence by ~50%
  Why more tractable: Delay is easier to achieve than cure

COMPARABLE GOAL 2: "Identify people who will develop Alzheimer's 10 years before symptoms"
  Why comparable: Enables early intervention trials
  Why more tractable: Biomarker discovery vs drug development

COMPARABLE GOAL 3: "Understand why 30% of people with amyloid plaques never get dementia"
  Why comparable: Reveals natural protection mechanisms
  Why more tractable: Observational study of existing cohorts
```

### Strategy 3: Answer-Seeking Question Reframing

```
CURRENT QUESTION: "Why doesn't immunotherapy work in pancreatic cancer?"
  Problem: Framed around failure, no clear path forward

REFRAMED: "What would need to be true for immunotherapy to work in
           pancreatic cancer?"
  Advantage: Constructive framing, identifies actionable conditions
  Sub-questions:
    - What if the tumor microenvironment were less immunosuppressive?
    - What if T cells could physically access the tumor?
    - What if neoantigen burden were higher?
    - What if checkpoint molecules were the right targets?

FURTHER REFRAMED: "In which pancreatic cancer patients DOES immunotherapy
                   work, and why?"
  Advantage: Starts from positive examples
  Approach: Study exceptional responders
```

### Phase 7 Output Template

```markdown
# Problem Inversion Analysis

## Original Problem Statement
[The problem as initially framed]

## Inversion 1: Unfix Parameters
- **Parameter unfixed**: [which constraint was released]
- **New framing**: [reframed problem statement]
- **Advantages**: [what this gains]
- **Risks**: [what this loses]
- **Verdict**: [better/worse/different than original]

## Inversion 2: Comparable Goal Substitution
- **Original goal**: [ambitious goal]
- **Comparable goal**: [more tractable version]
- **Why comparable**: [preserved impact argument]
- **Tractability gain**: [why this is more achievable]
- **Verdict**: [better/worse/different than original]

## Inversion 3: Answer-Seeking Reframe
- **Original question**: [failure-framed question]
- **Reframed question**: [constructive framing]
- **Sub-questions generated**: [list]
- **Most promising sub-question**: [selection with justification]
- **Verdict**: [better/worse/different than original]

## Recommended Framing
[Which version of the problem to pursue, with justification]
```

---

## Phase 8: Integration & Synthesis

### 3-Slide Presentation (5 minutes)

Structure the selected problem as a 3-slide presentation:

```
SLIDE 1: THE PROBLEM (90 seconds)
  Title: [One-sentence problem statement]
  Content:
    - What is the gap in knowledge? (2-3 bullets)
    - Why does this gap matter? (1-2 bullets)
    - What has been tried and why hasn't it worked? (1-2 bullets)
  Visual: Conceptual diagram showing the gap

SLIDE 2: THE APPROACH (90 seconds)
  Title: [One-sentence approach statement]
  Content:
    - What is the key insight that makes this tractable now? (1 bullet)
    - What is the experimental/computational approach? (2-3 bullets)
    - What are the expected outcomes? (2 bullets)
  Visual: Experimental schematic or workflow diagram

SLIDE 3: THE IMPACT (90 seconds)
  Title: [One-sentence impact statement]
  Content:
    - What changes if this succeeds? (2-3 bullets)
    - Who benefits? (1 bullet)
    - What comes next? (1-2 bullets — downstream research enabled)
  Visual: Impact diagram or timeline
```

### 250-300 Word Summary

```markdown
# [Problem Title]

## The Problem
[50-75 words: What is the gap? Why does it matter?]

## The Approach
[75-100 words: What will you do? What is the key insight?
 What methods will you use? What is the timeline?]

## Expected Outcomes
[50-75 words: What will success look like? What are the deliverables?
 What is the primary metric of success?]

## Impact and Significance
[50-75 words: How does this change the field? Who benefits?
 What future work does this enable?]
```

### 1-Minute Elevator Pitch

```
STRUCTURE (60 seconds total):

[10 seconds] HOOK:
  "Did you know that [surprising fact about the problem]?"

[15 seconds] PROBLEM:
  "The challenge is that [gap in knowledge], which means
   [consequence for patients/science/technology]."

[20 seconds] APPROACH:
  "We're taking a new approach by [key insight]. Using [method],
   we can [what becomes possible]. Our preliminary data shows [evidence]."

[15 seconds] IMPACT:
  "If this works, it would [change X], benefiting [who].
   This could lead to [downstream impact]."
```

---

## Phase 9: Meta-Framework — Orchestration and Iteration

### Timeline Options

#### Intensive Mode (1 week)

```
Day 1: Phase 1 (Intuition Pumps)
  - Apply all 7 pumps, generate 5-10 candidate problems
  - 30-50 papers literature scan for landscape mapping
  - Output: 2-page ideation document

Day 2: Phase 2 (Risk Assessment)
  - Score all candidates on 8 risk dimensions
  - Design go/no-go experiments for top 3
  - Output: Risk matrix with mitigation strategies

Day 3: Phase 3 + 4 (Optimization + Parameters)
  - Score candidates on optimization function
  - Analyze parameter constraints for top 2
  - Output: Impact assessment with parameter strategy

Day 4: Phase 5 + 6 + 7 (Decision Tree + Adversity + Inversion)
  - Structure execution/strategy oscillation plan
  - Anticipate failure modes
  - Apply all 3 inversion strategies to top candidate
  - Output: Adversity plan and inverted framings

Day 5: Phase 8 (Integration)
  - Build 3-slide presentation
  - Write 250-word summary
  - Practice elevator pitch
  - Solicit feedback from 2-3 colleagues
  - Output: Final problem selection with complete documentation
```

#### Distributed Mode (4-6 weeks)

```
Week 1: Phase 1 — Read widely, apply intuition pumps gradually
  - Read 10 papers per day across 3 subfields
  - Generate candidates organically through reading
  - Discuss with 2-3 colleagues informally

Week 2: Phase 2 + 3 — Assess risk and impact
  - Deep dive into top 5 candidates
  - Score on all dimensions
  - Design go/no-go experiments

Week 3: Phase 4 + 5 — Strategic constraints and decision structure
  - Analyze parameter space for top 3
  - Build oscillation framework
  - Present to lab meeting for feedback

Week 4: Phase 6 + 7 — Stress test through adversity and inversion
  - Run inversion strategies on top 2
  - Anticipate failures and plan ensemble
  - Discuss with mentor/advisor

Week 5-6: Phase 8 + 9 — Synthesize and iterate
  - Build all communication products
  - Present to diverse audiences for feedback
  - Iterate based on feedback
  - Make final selection
```

### Literature Integration Strategy

```
LITERATURE BUDGET: 30-50 papers

Allocation:
  - 10 landmark papers in the core field (foundational knowledge)
  - 10 recent papers (last 2 years) in the core field (current state)
  - 5 methodology papers (techniques you'd use)
  - 5 papers in adjacent fields (cross-pollination)
  - 5 review/perspective articles (field-level synthesis)
  - 5 preprints (emerging, not yet peer-reviewed)

Search strategy:
  1. Start with 2-3 recent reviews to map the landscape
  2. Follow citation chains backward for foundational work
  3. Follow citation chains forward for recent developments
  4. Search biorxiv for unpublished cutting-edge work
  5. Search for failed approaches (negative results, retractions) to learn what doesn't work
```

### Iteration Triggers

| Trigger | Action | Which Phase to Revisit |
|---------|--------|----------------------|
| New landmark paper published | Reassess novelty and competition | Phase 2 (risk) + Phase 3 (impact) |
| Go/no-go experiment fails | Reconsider problem feasibility | Phase 2 (risk) + Phase 7 (inversion) |
| Mentor feedback changes framing | Reframe problem | Phase 4 (parameters) + Phase 7 (inversion) |
| Funding opportunity aligns | Adjust constraints to fit | Phase 4 (parameters) |
| Competitor publishes on same problem | Differentiate or pivot | Phase 1 (new pumps) + Phase 7 (inversion) |
| New technology becomes available | Reassess feasibility | Phase 1 (tool trigger) + Phase 2 (risk) |
| Career stage changes | Reassess time horizon | Phase 4 (parameters) + Phase 5 (decision tree) |

### Revision Cycles

```
FIRST PASS (Phases 1-8):
  - Generate and evaluate candidates
  - Select tentative top choice
  - Document all reasoning

SECOND PASS (triggered by feedback or new information):
  - Revisit only affected phases
  - Update scores and rankings
  - Re-evaluate top choice

THIRD PASS (after go/no-go experiment):
  - Incorporate empirical evidence
  - Final commitment or pivot decision
  - Archive rejected candidates with reasoning (they may become relevant later)
```

---

## Multi-Agent Workflow Examples

### Example 1: PhD Student Selecting Dissertation Topic

**Prompt**: "Help me choose a dissertation topic in computational biology"

**Agent Workflow**:
1. **Research Problem Selection** (this skill): Run Phases 1-8 to generate and evaluate 5 candidate topics
2. **Literature Deep Research**: Deep dive into the top 2 candidates to assess novelty and feasibility
3. **Hypothesis Generation**: Generate testable hypotheses for the selected topic
4. **Experimental Design**: Design the first set of experiments/analyses

### Example 2: PI Redirecting Lab Focus

**Prompt**: "My lab studies X, but I think the field is saturated. What should we work on next?"

**Agent Workflow**:
1. **Research Problem Selection**: Apply "Scale Shift" and "Missing Link" pumps to the PI's expertise
2. **Scientific Critical Thinking**: Evaluate whether the field is truly saturated or if the perception is biased
3. **Research Problem Selection**: Complete risk/impact assessment for new directions
4. **Competitive Intelligence**: Map the competitive landscape for candidate directions

### Example 3: Industry R&D Portfolio Decision

**Prompt**: "We have budget for 3 projects. Help us select from these 8 candidates."

**Agent Workflow**:
1. **Research Problem Selection**: Score all 8 on risk (Phase 2) and impact (Phase 3)
2. **Research Problem Selection**: Apply parameter strategy (Phase 4) to find complementary portfolio
3. **Research Problem Selection**: Adversity planning (Phase 6) with ensemble portfolio structure
4. **Research Problem Selection**: Integration (Phase 8) with 3-slide pitch for each selected project

---

## Final Report Structure

```markdown
# Research Problem Selection Report

## Executive Summary
[250-word summary of selected problem and rationale]

## Phase 1: Candidate Problems
### Intuition Pumps Applied
### Candidate List (5-10 problems with one-sentence statements)
### Initial Ranking

## Phase 2: Risk Assessment
### Risk Scoring Matrix (all candidates)
### Go/No-Go Experiment Design (top 3)
### Mitigation Strategies (for high-risk dimensions)

## Phase 3: Impact Assessment
### Optimization Function Selection and Justification
### Impact Scores (all candidates)
### Risk-Adjusted Ranking

## Phase 4: Parameter Strategy
### Fixed vs Floating Parameters for Selected Problem
### Constraint Sensitivity Analysis

## Phase 5: Decision Tree
### Execution/Strategy Oscillation Plan
### Escalation Triggers Defined

## Phase 6: Adversity Plan
### Failure Modes and Responses
### Portfolio Structure

## Phase 7: Problem Inversions
### Three Inversions Applied
### Final Problem Framing Selected

## Phase 8: Communication Products
### 3-Slide Presentation
### 250-Word Summary
### 1-Minute Elevator Pitch

## Phase 9: Meta-Framework
### Timeline Selected (intensive/distributed)
### Literature Reviewed (30-50 papers)
### Iteration Triggers Set
### Next Steps and First Milestone

## Appendix: Rejected Candidates
[Document reasoning for rejection — may revisit later]
```

---

## Completeness Checklist

- [ ] At least 5 candidate problems generated using >= 3 different intuition pumps
- [ ] All candidates scored on 8 risk dimensions with composite scores
- [ ] Go/no-go experiment designed for top candidate (2-8 weeks, clear success criteria)
- [ ] Optimization function selected and justified for the research domain
- [ ] Impact scores calculated for all candidates
- [ ] Parameter strategy explicitly states what is fixed, floating, and implicitly constrained
- [ ] Decision tree oscillation framework defined with escalation triggers
- [ ] At least 3 failure modes anticipated with response plans
- [ ] All 3 inversion strategies applied to the selected problem
- [ ] 3-slide presentation, 250-word summary, and elevator pitch produced
- [ ] Timeline selected (intensive or distributed) with milestones
- [ ] 30-50 papers reviewed for landscape context
- [ ] Iteration triggers defined for when to revisit the selection
- [ ] Rejected candidates documented with reasoning for future reference
