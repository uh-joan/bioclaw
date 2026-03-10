---
name: meta-cognition
description: Thinking about thinking. Analyze and improve the reasoning process itself. Audit cognitive biases (25+ organized by category), calibrate confidence with reference class forecasting, decompose uncertainty (aleatory/epistemic/model), trace reasoning chains for weakest links, calculate information value, audit perspectives, and assess decision-readiness. Produces Meta-Cognitive Quality Scores (0-100). Use when asked to check reasoning, audit biases, calibrate confidence, evaluate assumptions, assess decision quality, decompose uncertainty, identify blind spots, stress-test logic, or improve the quality of any analytical conclusion.
---

# Meta-Cognition

Thinking about thinking. Systematically analyzes and improves the reasoning process itself. Audits cognitive biases across 25+ types organized by category, calibrates confidence using reference class forecasting, decomposes uncertainty into aleatory/epistemic/model components, traces reasoning chains for weakest links, calculates expected value of information, audits perspective limitations, and assesses decision-readiness. Produces structured Meta-Cognitive Audit reports with quality scores (0-100).

Distinct from **scientific-critical-thinking** (which evaluates research methodology and study quality), **peer-review** (which evaluates manuscripts against journal standards), and **hypothesis-generation** (which formulates and ranks competing hypotheses). This skill operates at the reasoning process level -- it audits *how* you are thinking, not *what* you are thinking about.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_meta-cognitive_audit.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as analysis proceeds
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Evaluating the quality of a published study or its methodology -> use `scientific-critical-thinking`
- Reviewing a manuscript for journal submission -> use `peer-review`
- Generating competing hypotheses for a scientific question -> use `hypothesis-generation`
- Building a structured literature synthesis from many papers -> use `research-synthesis`
- Performing scenario analysis and strategic decision modeling -> use `what-if-oracle`
- Statistical methodology selection or power analysis -> use `statistical-modeling`
- Attacking specific scientific claims with adversarial arguments -> use `red-team-science` (if available) or `scientific-critical-thinking`

## Cross-Skill Routing

- **Evaluating research methodology** -> use scientific-critical-thinking skill
- **Reviewing manuscripts** -> use peer-review skill
- **Generating hypotheses** -> use hypothesis-generation skill
- **Literature synthesis** -> use research-synthesis skill
- **Strategic decision modeling** -> use what-if-oracle skill
- **Statistical assessment** -> use statistical-modeling skill
- **Deep literature investigation** -> use literature-deep-research skill

---

## Available MCP Tools

### `mcp__pubmed__pubmed_data` (Reference Class Evidence)

| Method | Meta-cognition use | Key parameters |
|--------|-------------------|----------------|
| `search` | Find base rates and reference classes for calibration | `query`, `num_results` |
| `fetch_details` | Get study details to validate reasoning assumptions | `pmid` |

**Meta-cognition-specific uses:** Find historical base rates for confidence calibration, locate systematic reviews that provide reference classes for prediction, identify prior instances where similar reasoning led to correct or incorrect conclusions.

### `mcp__biorxiv__biorxiv_data` (Emerging Evidence for Perspective Audit)

| Method | Meta-cognition use | Key parameters |
|--------|-------------------|----------------|
| `search_preprints` | Identify emerging viewpoints that challenge current reasoning | `query`, `limit` |
| `get_preprint_details` | Examine alternative frameworks being proposed | `doi` |

### `mcp__opentargets__opentargets_data` (Evidence Strength Validation)

| Method | Meta-cognition use | Key parameters |
|--------|-------------------|----------------|
| `get_target_disease_associations` | Validate association strength claims in reasoning | `targetId`, `diseaseId` |
| `get_target_details` | Cross-check biological claims against curated data | `id` |

---

## Core Methodology: 7 Capabilities

### Capability 1: Cognitive Bias Audit

Systematically scan reasoning for 25+ cognitive biases organized by category. For each detected bias, document what it is, how it may be affecting the current analysis, and specific mitigation steps.

#### Selection Biases

| Bias | Definition | Detection Question |
|------|-----------|-------------------|
| **Confirmation bias** | Seeking evidence that confirms, ignoring disconfirming evidence | Am I only looking for evidence that supports my preferred conclusion? |
| **Availability heuristic** | Overweighting easily recalled examples | Am I giving too much weight to vivid, recent, or memorable examples? |
| **Survivorship bias** | Only seeing successes, not failures | Am I only considering cases that survived/succeeded? What about the ones that didn't? |
| **Selection bias** | Non-representative sample informing conclusions | Is my evidence base representative, or am I drawing from a biased sample? |
| **Publication bias** | Positive results overrepresented in the evidence | Is the published literature I'm relying on biased toward positive findings? |

#### Anchoring Biases

| Bias | Definition | Detection Question |
|------|-----------|-------------------|
| **Anchoring** | Over-relying on first piece of information encountered | Is my conclusion disproportionately influenced by the first data point I saw? |
| **Framing effect** | Conclusion changes based on how the question is framed | Would I reach a different conclusion if this question were framed differently? |
| **Status quo bias** | Preferring current state over change without justification | Am I favoring the current approach simply because it's familiar? |
| **Sunk cost fallacy** | Continuing because of past investment, not future value | Am I continuing this line of reasoning because of effort already invested? |

#### Social and Authority Biases

| Bias | Definition | Detection Question |
|------|-----------|-------------------|
| **Authority bias** | Accepting a claim because of who said it, not the evidence | Am I accepting this because of the source's reputation rather than the data? |
| **Bandwagon effect** | Accepting because many believe it | Am I influenced by how many people hold this view? |
| **Halo effect** | Positive impression in one area spilling over to unrelated areas | Am I extending credibility from one domain to another without justification? |
| **In-group bias** | Favoring conclusions from own group or field | Am I giving more weight to conclusions from my own field or community? |

#### Reasoning Biases

| Bias | Definition | Detection Question |
|------|-----------|-------------------|
| **Base rate neglect** | Ignoring prior probabilities when evaluating evidence | Have I considered the prior probability before updating on new evidence? |
| **Conjunction fallacy** | Judging A+B as more likely than A alone | Am I treating a specific, detailed scenario as more probable than a general one? |
| **Narrative fallacy** | Constructing coherent stories from random or unrelated events | Am I imposing a narrative on data that may be coincidental? |
| **Hindsight bias** | Believing an outcome was obvious after learning it occurred | Am I treating this outcome as predictable only because I now know it happened? |
| **Dunning-Kruger effect** | Overestimating competence in unfamiliar areas | Am I reasoning about a domain where I lack deep expertise? |
| **Neglect of probability** | Ignoring actual probabilities in favor of possibility | Am I conflating "possible" with "probable"? |
| **Representativeness heuristic** | Judging probability by similarity to a prototype | Am I judging likelihood based on how well something fits a stereotype? |
| **Scope insensitivity** | Failing to scale concern proportionally to magnitude | Am I treating a 10x difference the same as a 2x difference? |
| **Zero-risk bias** | Preferring elimination of small risks over larger risk reductions | Am I prioritizing complete elimination of a minor risk over a larger overall improvement? |
| **Optimism bias** | Systematic tendency to overestimate favorable outcomes | Am I being unrealistically optimistic about outcomes, timelines, or feasibility? |
| **Planning fallacy** | Underestimating time, costs, and risks of future actions | Are my estimates for effort, time, and cost realistic based on historical precedent? |
| **Neglect of regression to the mean** | Expecting extreme results to persist | Am I assuming an extreme observation will continue rather than regress? |

#### Bias Audit Execution Template

```
For each bias category, systematically ask:

1. SELECTION: What evidence am I using? Is it representative?
   - List evidence sources
   - Note any systematic gaps
   - Check for survivorship in the sample

2. ANCHORING: What was my first impression? Has it shifted appropriately?
   - Identify the anchor
   - Re-derive conclusion from scratch without the anchor
   - Compare the two conclusions

3. SOCIAL: Who influenced this reasoning? Why do I trust them?
   - List authority sources relied upon
   - Evaluate if credibility is domain-appropriate
   - Check for consensus vs independent convergence

4. REASONING: Am I applying sound probabilistic thinking?
   - State the base rate
   - Check for conjunction errors
   - Test the narrative for coherence vs causation
```

#### Bias Audit Output Table

| Bias | Detected? | Severity (1-5) | Impact on Conclusion | Mitigation Applied |
|------|----------|-----------------|---------------------|-------------------|
| Confirmation bias | Yes/No | X | [How it skews the analysis] | [Specific countermeasure] |
| Availability heuristic | Yes/No | X | [How it skews the analysis] | [Specific countermeasure] |
| ... | ... | ... | ... | ... |

---

### Capability 2: Uncertainty Decomposition

Every conclusion carries uncertainty. Not all uncertainty is the same. Decomposing uncertainty into its components reveals which can be reduced and which cannot.

#### Three Types of Uncertainty

| Type | Definition | Examples | Reducible? |
|------|-----------|----------|-----------|
| **Aleatory** | Irreducible randomness inherent in the system | Biological variation between patients, measurement noise, stochastic gene expression | No -- can be characterized but not eliminated |
| **Epistemic** | Knowledge gaps that could be filled with more data or research | Unknown mechanism of action, limited clinical data, unexplored dose range | Yes -- with more data, experiments, or research |
| **Model** | Using the wrong conceptual framework entirely | Treating a complex system as linear, wrong disease model, misidentified causal structure | Yes -- but requires paradigm shift, not just more data |

#### Uncertainty Decomposition Process

```
For each major conclusion in the analysis:

1. STATE the conclusion clearly
2. RATE overall uncertainty (Low / Medium / High / Very High)
3. DECOMPOSE into components:
   - What fraction is aleatory? (inherent randomness we can't reduce)
   - What fraction is epistemic? (gaps we could fill with more data)
   - What fraction is model uncertainty? (might be the wrong framework)
4. ASSESS implications:
   - If mostly aleatory: Accept it, characterize the distribution, plan for variation
   - If mostly epistemic: Identify the specific data that would reduce it
   - If mostly model: Question whether we're asking the right question at all
```

#### Model Uncertainty Warning Signs

Model uncertainty is the most dangerous because you don't know what you don't know. Watch for:

- The evidence "sort of" fits but requires many ad hoc explanations
- Multiple equally plausible but mutually exclusive frameworks exist
- Experts in the field fundamentally disagree on the mechanism, not just the details
- The domain is young or rapidly evolving (high paradigm flux)
- Analogies to other domains are the primary evidence (reasoning by analogy without validation)
- Predictions from the model consistently fail in subtle ways

#### Uncertainty Decomposition Output Table

| Conclusion | Overall Uncertainty | Aleatory (%) | Epistemic (%) | Model (%) | Key Reducible Gaps |
|-----------|--------------------|--------------|--------------|-----------|--------------------|
| [Finding 1] | High | 20% | 50% | 30% | [What data would reduce epistemic component] |
| [Finding 2] | Medium | 60% | 30% | 10% | [What data would reduce epistemic component] |

---

### Capability 3: Confidence Calibration

Most people are overconfident. When they say they're 90% sure, they're right about 70% of the time. Calibration corrects this systematic bias.

#### Calibration Protocol

```
For each key claim or prediction:

1. STATE the claim precisely (must be verifiable)
2. INITIAL ESTIMATE: What probability do I assign? (be honest)
3. BETTING TEST: "What would I bet at these odds?"
   - If unwilling to bet at stated odds, adjust downward
   - This forces honesty about true beliefs vs stated beliefs
4. REFERENCE CLASS: Find a reference class of similar predictions
   - How often have similar predictions been correct historically?
   - Use MCP tools to find base rates:
     mcp__pubmed__pubmed_data(method: "search",
       query: "[similar claims OR predictions] systematic review",
       num_results: 10)
5. CALIBRATION ADJUSTMENT:
   - If stated > 80%: Are you really that sure? Most people aren't.
   - Apply typical calibration correction: reduce extreme confidence by 10-15%
   - Exception: well-established, multiply-replicated findings
6. SURPRISE TEST: "How surprised would I be if wrong?" (1-10 scale)
   - 1-3: Not very surprised -> confidence should be 50-65%
   - 4-6: Moderately surprised -> confidence should be 65-80%
   - 7-8: Very surprised -> confidence should be 80-90%
   - 9-10: Shocked -> confidence should be 90-95%
   - Note: Almost nothing deserves >95% outside formal logic
```

#### Common Calibration Errors

| Error | Description | Correction |
|-------|------------|-----------|
| **Overconfidence** | Stating 90% when accuracy is ~70% | Apply 10-15% reduction to high-confidence claims |
| **Narrow intervals** | Prediction intervals too tight | Widen by 50% as a starting correction |
| **Anchored estimates** | Adjusting insufficiently from an initial anchor | Re-derive from scratch using different starting point |
| **Neglecting base rates** | Ignoring how often similar things are true in general | Always start with the base rate before updating |
| **Inside view** | Using only features of the specific case | Force outside view: what does the reference class say? |

#### Confidence Calibration Output Table

| Claim | Initial Confidence | Betting Test | Reference Class Rate | Calibrated Confidence | Surprise Score (1-10) |
|-------|-------------------|--------------|---------------------|-----------------------|----------------------|
| [Claim 1] | 85% | Would bet at 3:1 (75%) | 60% for similar claims | 70% | 5 |
| [Claim 2] | 60% | Would bet at 1:1 (50%) | 45% for similar claims | 50% | 3 |

---

### Capability 4: Reasoning Chain Audit

Every conclusion rests on a chain of inferences. The chain is only as strong as its weakest link. This capability traces and stress-tests each link.

#### Chain Audit Process

```
1. EXTRACT the reasoning chain:
   Premise A -> Inference 1 -> Intermediate conclusion B
   -> Inference 2 -> Intermediate conclusion C
   -> Inference 3 -> Final conclusion D

2. For EACH link, assess:
   - Is the inference logically valid? (Does the conclusion follow from the premise?)
   - Is the premise empirically supported? (Is the starting point true?)
   - Are there hidden premises? (Unstated assumptions the link depends on)
   - What logical fallacies might apply?
   - Strength rating: 1-10

3. IDENTIFY the weakest link:
   - Which single link, if broken, invalidates the entire conclusion?
   - This is where to focus skepticism and evidence-gathering

4. CHECK for logical fallacies at each step:
```

#### Common Logical Fallacies Checklist

| Fallacy | Description | Example |
|---------|------------|---------|
| **Post hoc ergo propter hoc** | Assuming causation from temporal sequence | "Drug was given, then patient improved, so drug caused improvement" |
| **Affirming the consequent** | If A then B; B is true; therefore A | "If the gene is causal, KO shows phenotype; KO shows phenotype; therefore gene is causal" |
| **Hasty generalization** | Drawing broad conclusion from small sample | "3 patients responded, so the drug works" |
| **False dichotomy** | Presenting only two options when more exist | "Either this gene causes the disease or it's irrelevant" |
| **Appeal to nature** | Assuming natural = good or unnatural = bad | "The natural ligand is better than the synthetic one" |
| **Slippery slope** | Assuming one step inevitably leads to extreme | "If we approve this exception, all standards will collapse" |
| **Straw man** | Misrepresenting an opposing argument to attack it | "Critics say this drug is useless" (when they said it needs more data) |
| **Equivocation** | Using a term with different meanings at different steps | Switching between "significant" (statistical) and "significant" (clinical) |
| **Circular reasoning** | Conclusion is assumed in the premise | "This pathway is important because it's in the important pathways list" |
| **Genetic fallacy** | Judging a claim by its origin rather than its merit | "This idea came from a small lab, so it's probably wrong" |

#### Hidden Premises Detection

Hidden premises are unstated assumptions that the reasoning chain depends on. They are dangerous because they are never examined.

```
For each inference step, ask:
- What must also be true for this step to work?
- What am I assuming about the mechanism, context, or conditions?
- Would someone from a different field challenge this assumption?

Common hidden premises in scientific reasoning:
- "The model organism translates to humans"
- "In vitro conditions reflect in vivo conditions"
- "The measurement accurately reflects the biological reality"
- "The study population is representative of the target population"
- "The statistical model correctly captures the data-generating process"
- "Absence of evidence is evidence of absence"
```

#### Reasoning Chain Audit Output Table

| Link # | Premise -> Conclusion | Strength (1-10) | Hidden Premises | Fallacy Risk | Weakest Link? |
|--------|----------------------|-----------------|-----------------|-------------|---------------|
| 1 | [A -> B] | 8 | [Assumes X] | Low | No |
| 2 | [B -> C] | 4 | [Assumes Y, Z] | Hasty generalization | **Yes** |
| 3 | [C -> D] | 7 | [Assumes W] | Low | No |

---

### Capability 5: Information Value Analysis

Not all information is equally useful. Before gathering more data, estimate the expected value of that information to prioritize efficiently.

#### Expected Value of Information (EVI) Framework

```
For each potential data source or experiment:

1. CURRENT STATE: What is the current best estimate and confidence?
2. POSSIBLE OUTCOMES: What could the new information show?
3. DECISION IMPACT: Would each outcome change the decision?
   - If no outcome would change the decision -> information has zero value
   - If some outcomes would change the decision -> calculate EVI
4. EVI CALCULATION (simplified):
   EVI = P(outcome changes decision) x (Value of better decision - Value of current decision)
5. FEASIBILITY: How hard/expensive is it to get this information?
6. PRIORITY: EVI / Feasibility cost = Priority score
```

#### Information Value Decision Rules

| Situation | Action |
|-----------|--------|
| No additional data would change the decision | Stop gathering data; decide now |
| One specific dataset would dramatically reduce uncertainty | Prioritize getting that dataset |
| Many small improvements are possible but none decisive | Assess whether cumulative improvement justifies delay |
| The cost of being wrong is catastrophic | Lower the threshold for gathering more data |
| The cost of delay exceeds the cost of being wrong | Decide now with current information |

#### Information Value Analysis Output Table

| Data Source / Experiment | Information Gain (1-10) | Feasibility (1-10) | Cost | Would It Change Decision? | Priority Score |
|--------------------------|------------------------|--------------------|----- |--------------------------|---------------|
| [Source 1] | 8 | 6 | Low | Yes, if result is X | 48 |
| [Source 2] | 3 | 9 | Low | Unlikely | 27 |
| [Source 3] | 9 | 2 | High | Yes | 18 |

```
Identifying high-value information sources:
  mcp__pubmed__pubmed_data(method: "search",
    query: "[key uncertainty] systematic review OR meta-analysis",
    num_results: 10)
  -> Check if existing reviews already contain the answer
  -> Avoid gathering information that already exists
```

---

### Capability 6: Perspective Audit

Every analysis is conducted from a perspective. That perspective shapes what is visible and what is invisible. Auditing the perspective reveals blind spots.

#### Perspective Audit Process

```
1. IDENTIFY current perspective:
   - What role am I taking? (researcher, clinician, patient, regulator, investor, engineer)
   - What domain am I operating in? (biology, chemistry, clinical, regulatory, commercial)
   - What values am I implicitly prioritizing? (safety, efficacy, speed, cost, novelty)

2. ALTERNATIVE PERSPECTIVES (check at least 3):
   For each alternative perspective, ask:
   - What would a [role] emphasize that I'm overlooking?
   - What risks would a [role] see that I don't?
   - What opportunities would a [role] see that I don't?

3. NAIVE PERSPECTIVE:
   - What would I think if I had no prior exposure to this topic?
   - What would be the most obvious question from a newcomer?
   - Is there something so "obvious" to experts that it's never questioned?

4. TEMPORAL PERSPECTIVE:
   - How would this be viewed 5 years from now?
   - How was this viewed 5 years ago? Has the field shifted?
   - Am I anchored to the current paradigm?

5. ADVERSARIAL PERSPECTIVE:
   - If someone wanted to disprove this conclusion, how would they attack it?
   - What's the strongest counterargument?
   - What evidence would I need to see to change my mind?
```

#### Common Perspective Blind Spots

| Perspective | Typical Blind Spots |
|------------|-------------------|
| **Researcher** | Overvalues novelty, undervalues reproducibility and clinical translation |
| **Clinician** | Overvalues individual patient experience, undervalues population-level evidence |
| **Patient** | Overvalues immediate symptoms, undervalues long-term outcomes and side effects |
| **Regulator** | Overvalues safety, undervalues speed of access to treatments |
| **Investor** | Overvalues market size and speed, undervalues scientific rigor |
| **Specialist** | Overvalues depth in own field, misses cross-domain connections |
| **Generalist** | Overvalues breadth, misses domain-specific nuances |

#### Perspective Audit Output

```
Current perspective: [Role, domain, implicit values]

Alternative perspective 1: [Role]
  - What they'd emphasize: [...]
  - What they'd see that I don't: [...]
  - Impact on conclusion: [...]

Alternative perspective 2: [Role]
  - What they'd emphasize: [...]
  - What they'd see that I don't: [...]
  - Impact on conclusion: [...]

Alternative perspective 3: [Role]
  - What they'd emphasize: [...]
  - What they'd see that I don't: [...]
  - Impact on conclusion: [...]

Naive perspective: [What would a newcomer ask?]
Temporal perspective: [How will this look in 5 years?]
Adversarial perspective: [Strongest counterargument]
```

---

### Capability 7: Decision-Readiness Assessment

After completing all audits, determine whether the reasoning is sound enough to act on, or whether more work is needed.

#### Decision-Readiness Framework

```
1. REASONING SOUNDNESS
   - Bias audit: Were significant biases detected and mitigated?
   - Reasoning chain: Is the weakest link strong enough?
   - Confidence: Are calibrated confidence levels acceptable for the stakes?
   Answer: Sound / Adequate / Weak / Unsound

2. COST OF ERROR
   - What happens if the conclusion is wrong?
   - Low: Minor inconvenience, easily reversed
   - Medium: Significant cost but recoverable
   - High: Major setback, difficult to recover
   - Catastrophic: Irreversible harm, program failure, safety issue

3. COST OF DELAY
   - What is lost by waiting for more information?
   - Consider: competitive timing, patient access, resource allocation, opportunity cost

4. DECISION MATRIX

   | Cost of Error \ Reasoning | Sound | Adequate | Weak | Unsound |
   |---------------------------|-------|----------|------|---------|
   | Low | Act now | Act now | Gather data | Gather data |
   | Medium | Act now | Act with hedge | Gather data | Rethink |
   | High | Act with hedge | Gather data | Gather data | Rethink |
   | Catastrophic | Gather data | Gather data | Rethink | Rethink |

5. RECOMMENDATION
   - **Act now**: Reasoning is sufficient for the stakes. Proceed.
   - **Act with hedge**: Proceed but build in safeguards and monitoring.
   - **Gather specific data**: Identify exactly what data would resolve the key uncertainty. Use Information Value Analysis (Capability 5) to prioritize.
   - **Fundamentally rethink**: The reasoning framework itself may be wrong. Step back and reconsider the entire approach.
```

---

## Meta-Cognitive Quality Score (0-100)

The overall quality score aggregates four dimensions, each scored 0-25.

### Scoring Rubric

| Dimension | 0-5 (Poor) | 6-12 (Weak) | 13-18 (Adequate) | 19-22 (Good) | 23-25 (Excellent) |
|-----------|-----------|------------|------------------|--------------|-------------------|
| **Bias Awareness** | No bias checking | Few biases considered | Major categories checked | Systematic audit with mitigations | Comprehensive audit, all categories, specific mitigations applied |
| **Uncertainty Characterization** | Uncertainty ignored | Some uncertainty noted | Types distinguished | Full decomposition with proportions | Decomposition + reducibility analysis + implications |
| **Calibration Quality** | No calibration | Some hedging | Reference classes used | Full calibration protocol with betting test | Calibrated + reference class + surprise test + historical validation |
| **Reasoning Chain Integrity** | No chain analysis | Chain stated | Links assessed | Weak links identified + fallacies checked | Full audit + hidden premises + adversarial testing |

### Score Interpretation

| Score | Meaning | Action |
|-------|---------|--------|
| **85-100** | Excellent meta-cognitive rigor | High confidence in reasoning process |
| **70-84** | Good with minor gaps | Address identified gaps if stakes warrant |
| **50-69** | Adequate but notable weaknesses | Strengthen weak dimensions before high-stakes decisions |
| **30-49** | Significant meta-cognitive gaps | Major revision of reasoning process recommended |
| **0-29** | Minimal meta-cognitive awareness | Fundamental rethinking needed |

---

## Full Report Structure

```
# Meta-Cognitive Audit: [Topic/Decision]

## Executive Summary
[2-3 sentence overview of the reasoning being audited and key findings]

## The Argument Being Audited
[State the reasoning chain clearly, step by step]

## 1. Cognitive Bias Scan

| Bias | Detected? | Severity (1-5) | Impact on Conclusion | Mitigation Applied |
|------|----------|-----------------|---------------------|-------------------|
| [Bias name] | Yes/No | X | [Description] | [Countermeasure] |

### Key Bias Findings
[Narrative summary of the most impactful biases detected]

## 2. Uncertainty Decomposition

| Conclusion | Overall Uncertainty | Aleatory (%) | Epistemic (%) | Model (%) | Key Reducible Gaps |
|-----------|--------------------|--------------|--------------|-----------|--------------------|
| [Finding] | High/Med/Low | X% | Y% | Z% | [Specific gaps] |

### Uncertainty Implications
[What the decomposition tells us about where to focus]

## 3. Confidence Calibration

| Claim | Initial Confidence | Calibrated Confidence | Reference Class | Surprise Score |
|-------|-------------------|----------------------|-----------------|---------------|
| [Claim] | X% | Y% | [Class] | Z/10 |

### Calibration Findings
[Are we overconfident? Underconfident? Where?]

## 4. Reasoning Chain Audit

| Link # | Premise -> Conclusion | Strength (1-10) | Hidden Premises | Fallacy Risk | Weakest? |
|--------|----------------------|-----------------|-----------------|-------------|----------|
| [N] | [A -> B] | X | [Assumptions] | [Fallacy] | Yes/No |

### Critical Weak Links
[Which links are most vulnerable and why]

## 5. Information Value Analysis

| Data Source | Info Gain (1-10) | Feasibility (1-10) | Would Change Decision? | Priority |
|------------|-----------------|--------------------|-----------------------|----------|
| [Source] | X | Y | Yes/No | X*Y |

### Information Gathering Recommendation
[What to get next, if anything]

## 6. Perspective Audit

### Current Perspective
[Role, domain, implicit values]

### Alternative Perspectives
[At least 3 alternatives with what they'd see differently]

### Blind Spots Identified
[What the current perspective is missing]

## 7. Decision-Readiness Assessment

- Reasoning Soundness: [Sound / Adequate / Weak / Unsound]
- Cost of Error: [Low / Medium / High / Catastrophic]
- Cost of Delay: [Low / Medium / High]
- **Recommendation: [Act Now / Act with Hedge / Gather Specific Data / Fundamentally Rethink]**

## Meta-Cognitive Quality Score

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Bias Awareness | /25 | [Brief rationale] |
| Uncertainty Characterization | /25 | [Brief rationale] |
| Calibration Quality | /25 | [Brief rationale] |
| Reasoning Chain Integrity | /25 | [Brief rationale] |
| **Total** | **/100** | |

## Key Recommendations
1. [Most important action item]
2. [Second priority]
3. [Third priority]
```

---

## Python Code Templates

### Bayesian Confidence Update

```python
"""
Bayesian update for confidence calibration.
Given a prior belief and new evidence, compute the posterior.
"""

def bayesian_update(prior: float, likelihood_given_true: float, likelihood_given_false: float) -> float:
    """
    Compute posterior probability using Bayes' theorem.

    Args:
        prior: P(H) - prior probability of hypothesis
        likelihood_given_true: P(E|H) - probability of evidence if hypothesis is true
        likelihood_given_false: P(E|~H) - probability of evidence if hypothesis is false

    Returns:
        P(H|E) - posterior probability
    """
    numerator = likelihood_given_true * prior
    denominator = numerator + likelihood_given_false * (1 - prior)
    posterior = numerator / denominator
    return round(posterior, 4)


def calibration_adjustment(stated_confidence: float) -> float:
    """
    Apply typical calibration correction.
    Most people are overconfident: 90% stated -> ~75% actual.
    Uses empirical calibration curve from Tetlock's superforecasters research.
    """
    if stated_confidence >= 0.95:
        return stated_confidence * 0.85  # Heavy discount for extreme confidence
    elif stated_confidence >= 0.80:
        return stated_confidence * 0.88  # Moderate discount
    elif stated_confidence >= 0.60:
        return stated_confidence * 0.92  # Mild discount
    else:
        return stated_confidence * 1.05  # Slight boost for underconfidence at low end


def chain_strength(link_strengths: list[float]) -> float:
    """
    Calculate overall reasoning chain strength.
    Chain is multiplicative -- each link's weakness compounds.

    Args:
        link_strengths: List of strength scores (0-1) for each link

    Returns:
        Overall chain strength (0-1)
    """
    import math
    result = 1.0
    for s in link_strengths:
        result *= s
    return round(result, 4)


# Example usage:
# Chain with 3 links at 0.9, 0.4, 0.8 strength
# Overall: 0.9 * 0.4 * 0.8 = 0.288 (weak chain due to link 2)
print(chain_strength([0.9, 0.4, 0.8]))
```

### Information Value Calculator

```python
"""
Expected Value of Information (EVI) calculator.
Helps prioritize which data to gather next.
"""

def expected_value_of_information(
    p_outcome_changes_decision: float,
    value_better_decision: float,
    value_current_decision: float,
    cost_of_information: float
) -> dict:
    """
    Calculate whether gathering specific information is worth it.

    Returns:
        Dict with EVI, net value, and recommendation
    """
    evi = p_outcome_changes_decision * (value_better_decision - value_current_decision)
    net_value = evi - cost_of_information

    return {
        "evi": round(evi, 2),
        "cost": cost_of_information,
        "net_value": round(net_value, 2),
        "recommendation": "Gather" if net_value > 0 else "Skip",
        "priority_score": round(evi / max(cost_of_information, 0.01), 2)
    }
```

### Bias Detection Scorer

```python
"""
Automated bias severity scoring.
"""

BIAS_CATEGORIES = {
    "selection": ["confirmation", "availability", "survivorship", "selection", "publication"],
    "anchoring": ["anchoring", "framing", "status_quo", "sunk_cost"],
    "social": ["authority", "bandwagon", "halo", "ingroup"],
    "reasoning": [
        "base_rate_neglect", "conjunction", "narrative", "hindsight",
        "dunning_kruger", "neglect_of_probability", "representativeness",
        "scope_insensitivity", "zero_risk", "optimism", "planning_fallacy",
        "regression_to_mean"
    ]
}

def score_bias_audit(detected_biases: dict[str, int]) -> dict:
    """
    Score a bias audit based on detected biases and their severity.

    Args:
        detected_biases: Dict of {bias_name: severity (1-5)}

    Returns:
        Category scores and overall bias awareness score (0-25)
    """
    total_possible = len([b for cat in BIAS_CATEGORIES.values() for b in cat])
    total_checked = len(detected_biases)
    coverage = total_checked / total_possible

    max_severity = max(detected_biases.values()) if detected_biases else 0
    avg_severity = (sum(detected_biases.values()) / len(detected_biases)) if detected_biases else 0

    # Score: higher coverage = higher awareness = better
    # But high severity biases reduce the score unless mitigated
    awareness_score = min(25, int(coverage * 25 * (1 - avg_severity / 10)))

    return {
        "biases_checked": total_checked,
        "total_possible": total_possible,
        "coverage": round(coverage, 2),
        "max_severity": max_severity,
        "avg_severity": round(avg_severity, 2),
        "awareness_score": awareness_score
    }
```

---

## Multi-Agent Workflow Examples

**"Audit the reasoning behind our decision to pursue Target X for Disease Y"**
1. Meta-Cognition -> Full 7-capability audit of the reasoning chain
2. Drug Target Validator -> Independent target validation scoring
3. Scientific Critical Thinking -> Evaluate the evidence quality underlying the reasoning
4. What-If Oracle -> Model alternative scenarios if the reasoning is wrong

**"How confident should we be in the conclusion from this literature review?"**
1. Meta-Cognition -> Confidence calibration + bias audit + uncertainty decomposition
2. Literature Deep Research -> Verify completeness of the evidence base
3. Peer Review -> Evaluate the quality of key papers cited
4. Hypothesis Generation -> Generate alternative explanations that were not considered

**"We're about to make a go/no-go decision. Stress-test our reasoning."**
1. Meta-Cognition -> Full reasoning chain audit + decision-readiness assessment
2. What-If Oracle -> Scenario modeling for each possible outcome
3. Competitive Intelligence -> Verify assumptions about competitive landscape
4. Scientific Critical Thinking -> Deep evaluation of the pivotal data

**"This analysis feels right but I'm not sure why. Help me examine my reasoning."**
1. Meta-Cognition -> Bias audit (especially narrative fallacy + confirmation bias) + perspective audit
2. Hypothesis Generation -> Generate competing explanations
3. Literature Deep Research -> Find disconfirming evidence that may have been overlooked
4. Statistical Modeling -> Verify that the quantitative reasoning is sound

**"Review the reasoning in this regulatory submission strategy"**
1. Meta-Cognition -> Reasoning chain audit + perspective audit (regulatory vs sponsor perspectives)
2. FDA Consultant -> Regulatory pathway analysis
3. Clinical Trial Protocol Designer -> Verify trial design assumptions
4. What-If Oracle -> Model scenarios where regulatory assumptions are wrong

---

## Applying Meta-Cognition to Other Skills' Outputs

Meta-cognition can be applied as a second-pass audit on the output of any other skill. Common patterns:

| Primary Skill | Meta-Cognition Adds |
|--------------|-------------------|
| Literature Deep Research | Bias audit on search strategy, confidence calibration on conclusions |
| Hypothesis Generation | Reasoning chain audit on each hypothesis, perspective audit |
| Drug Target Validator | Uncertainty decomposition on validation scores, information value analysis |
| Clinical Trial Protocol Designer | Decision-readiness assessment, perspective audit (patient vs regulator) |
| What-If Oracle | Confidence calibration on probability estimates, bias audit on scenario selection |
| Competitive Intelligence | Perspective audit, survivorship bias check on competitive landscape |
| Research Synthesis | Bias audit on inclusion criteria, model uncertainty assessment |

---

## Completeness Checklist

- [ ] The argument being audited is stated clearly, step by step
- [ ] All 4 bias categories checked (selection, anchoring, social, reasoning)
- [ ] At least 15 specific biases evaluated with detection status
- [ ] Detected biases include severity rating, impact description, and mitigation
- [ ] Uncertainty decomposed into aleatory/epistemic/model for each major conclusion
- [ ] Confidence calibrated using betting test + reference class + surprise score
- [ ] Reasoning chain traced with strength scores for each link
- [ ] Weakest link identified and highlighted
- [ ] Hidden premises documented for critical inference steps
- [ ] Logical fallacies checked at each reasoning step
- [ ] Information value analysis performed with priority ranking
- [ ] At least 3 alternative perspectives audited
- [ ] Adversarial perspective (strongest counterargument) explicitly stated
- [ ] Decision-readiness assessed with cost of error and cost of delay
- [ ] Meta-Cognitive Quality Score calculated (0-100) across 4 dimensions
- [ ] Key recommendations listed with priority order
- [ ] Report follows structured output format with all required sections
- [ ] No `[Analyzing...]` placeholders remain in final report
