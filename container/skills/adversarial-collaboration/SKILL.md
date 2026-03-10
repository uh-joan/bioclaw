---
name: adversarial-collaboration
description: Structured scientific debate between opposing positions to find truth, inspired by Daniel Kahneman's adversarial collaboration framework. Uses a 5-phase deliberation process (Position Statement, Steel-Manning, Crux Identification, Resolution Design, Joint Synthesis) with debate archetypes, collaboration quality scoring (0-100), and resolution experiments. Produces structured debate reports with crux analysis, joint recommendations, and evidence-based resolutions. Use when asked to debate both sides, evaluate opposing views, find the truth between two positions, resolve a scientific disagreement, compare competing theories, or determine which of two approaches is better.
---

# Adversarial Collaboration

Structured scientific debate between opposing positions to find truth, inspired by Daniel Kahneman's adversarial collaboration framework. This skill generates genuine, high-quality debate between two opposing sides, identifies the actual cruxes of disagreement, designs experiments that would resolve those cruxes, and produces joint syntheses that fairly represent both perspectives.

Distinct from **peer-review** (which evaluates a single piece of work, not debates between positions), **scientific-critical-thinking** (which applies logical analysis to a single argument), and **hypothesis-generation** (which generates multiple hypotheses without pitting them against each other in structured debate). Also distinct from multi-perspective consultation approaches (Delphi method, consciousness council) which gather many viewpoints rather than conducting binary adversarial exchange.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_adversarial_collaboration_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as each phase of deliberation completes
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Evaluating a single manuscript or proposal -> use `peer-review`
- Attacking a claim from one direction (red-teaming) -> use `scientific-critical-thinking`
- Generating multiple hypotheses without structured debate -> use `hypothesis-generation`
- Gathering multiple expert perspectives (not binary opposition) -> use multi-perspective approaches
- Exploring branching scenarios for a decision -> use `what-if-oracle`
- Breaking a problem down to fundamental truths -> use `first-principles`
- Writing a literature review or evidence synthesis -> use `systematic-literature-reviewer`
- Statistical analysis of data -> use `statistical-modeling`

## Cross-Skill Routing

- Need evidence to support one side's arguments -> `literature-deep-research`
- Need to verify empirical claims made during debate -> `peer-review`
- Need to generate hypotheses from the debate's conclusions -> `hypothesis-generation`
- Need to explore scenarios based on resolved cruxes -> `what-if-oracle`
- Need to break assumptions down to fundamentals -> `first-principles`
- Need to design an experiment resolving an empirical crux -> `clinical-trial-protocol-designer`
- Need statistical methodology for resolution experiments -> `statistical-modeling`
- Need regulatory context for a methodological crux -> `fda-consultant`

---

## Available MCP Tools

### `mcp__pubmed__pubmed_data` (Evidence for Both Sides)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search PubMed by keywords, MeSH terms | `query`, `num_results` |
| `fetch_details` | Full article metadata: abstract, authors, DOI, MeSH | `pmid` |

**Adversarial uses:** Gather evidence supporting Side A and Side B independently. Find systematic reviews and meta-analyses that address cruxes. Identify studies that both sides would accept as informative. Verify specific empirical claims made by either side.

### `mcp__opentargets__opentargets_data` (Biological Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability) | `id` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId`, `diseaseId`, `minScore`, `size` |

**Adversarial uses:** Resolve mechanism debates with evidence-scored associations. Evaluate target-disease link strength when sides disagree about biological relevance.

### `mcp__ctgov__ctgov_data` (Clinical Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search clinical trials by condition, intervention | `condition`, `intervention`, `phase`, `status` |
| `get` | Full trial details by NCT ID | `nctId` |
| `stats` | Trial statistics and counts | `condition`, `intervention` |

**Adversarial uses:** Resolve efficacy debates with clinical trial data. Find trials addressing specific cruxes. Evaluate whether resolution experiments have already been conducted.

### `mcp__chembl__chembl_data` (Pharmacological Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |

**Adversarial uses:** Resolve mechanism-of-action debates with compound-target data. Evaluate competing claims about drug pharmacology.

### `mcp__fda__fda_data` (Regulatory Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `lookup_drug` | Search drugs by name, adverse events, labels | `search_term`, `search_type`, `limit` |

**Adversarial uses:** Resolve risk-benefit debates with regulatory data. Find adverse event rates to ground safety arguments. Check approved labeling for efficacy claims.

---

## Core Framework: 5-Phase Adversarial Deliberation

### Phase 1: Position Statement

Each side presents its strongest case with the best available evidence.

#### Side A: Position Statement

```
POSITION: [Clear, specific statement of Side A's position]
CONFIDENCE: [0-100]%

KEY ARGUMENTS:
1. [Argument with supporting evidence]
   Evidence: [Citation or data] — Tier: T[X]
   Strength: [Strong / Moderate / Suggestive]

2. [Argument with supporting evidence]
   Evidence: [Citation or data] — Tier: T[X]
   Strength: [Strong / Moderate / Suggestive]

3. [Argument with supporting evidence]
   Evidence: [Citation or data] — Tier: T[X]
   Strength: [Strong / Moderate / Suggestive]

4. [Optional: 4th argument]
5. [Optional: 5th argument]

WEAKEST POINT (self-identified):
  [What is the biggest vulnerability in this position?]
```

#### Side B: Position Statement

```
POSITION: [Clear, specific statement of Side B's opposing position]
CONFIDENCE: [0-100]%

KEY ARGUMENTS:
1. [Argument with supporting evidence]
   Evidence: [Citation or data] — Tier: T[X]
   Strength: [Strong / Moderate / Suggestive]

2. [Argument with supporting evidence]
   Evidence: [Citation or data] — Tier: T[X]
   Strength: [Strong / Moderate / Suggestive]

3. [Argument with supporting evidence]
   Evidence: [Citation or data] — Tier: T[X]
   Strength: [Strong / Moderate / Suggestive]

4. [Optional: 4th argument]
5. [Optional: 5th argument]

WEAKEST POINT (self-identified):
  [What is the biggest vulnerability in this position?]
```

**Rules for position statements:**
- Each side must present its BEST case, not a strawman
- Evidence must be cited with tiers (T1-T4)
- Minimum 3, maximum 5 key arguments per side
- Each side must self-identify its weakest point (intellectual honesty test)
- Positions must be specific enough to be falsifiable

```
Gather evidence for both sides:
  # Side A evidence
  mcp__pubmed__pubmed_data(method: "search",
    query: "[Side A position] evidence support",
    num_results: 15)

  # Side B evidence
  mcp__pubmed__pubmed_data(method: "search",
    query: "[Side B position] evidence support",
    num_results: 15)
```

---

### Phase 2: Steel-Manning

Each side identifies the BEST argument from the opposing side and explains why it is compelling. This phase forces genuine engagement and prevents strawmanning.

#### Side A Steel-Mans Side B

```
STRONGEST OPPOSING ARGUMENT: [Side B's argument #X]
WHY IT IS COMPELLING:
  [Genuine explanation of why this argument has force]
  [What evidence or logic makes it hard to dismiss]

WHAT WOULD MAKE ME UPDATE:
  [If I saw [specific evidence], I would increase Side B's probability by [X]%]

DOES THIS CHANGE MY CONFIDENCE?
  Original: [X]% -> Updated: [Y]% (delta: [Z]%)
  Reason: [Why or why not]
```

#### Side B Steel-Mans Side A

```
STRONGEST OPPOSING ARGUMENT: [Side A's argument #X]
WHY IT IS COMPELLING:
  [Genuine explanation of why this argument has force]
  [What evidence or logic makes it hard to dismiss]

WHAT WOULD MAKE ME UPDATE:
  [If I saw [specific evidence], I would increase Side A's probability by [X]%]

DOES THIS CHANGE MY CONFIDENCE?
  Original: [X]% -> Updated: [Y]% (delta: [Z]%)
  Reason: [Why or why not]
```

**Steel-manning quality test:**
- Would the opposing side agree "yes, that is my best argument"?
- Is the engagement genuine, or does it subtly undermine the argument?
- Does the steel-man include the strongest evidence for the opposing position?
- Is the "what would make me update" specific and measurable?

---

### Phase 3: Crux Identification

Identify the actual points of disagreement, categorized by type. This is the most intellectually valuable phase -- many debates persist because the participants do not realize what they actually disagree about.

#### 3.1 Crux Types

| Type | Definition | Resolvability | Example |
|------|-----------|---------------|---------|
| **Empirical** | Disagreement about facts | High (data can resolve) | "Does drug X cross the BBB?" |
| **Methodological** | Disagreement about how to measure/analyze | Medium (can design neutral test) | "Is surrogate endpoint Y valid?" |
| **Value** | Disagreement about what matters | Low (requires negotiation, not data) | "Is a 2-month survival gain worth severe toxicity?" |
| **Framework** | Disagreement about which mental model applies | Medium (can test predictions) | "Is this disease driven by inflammation or autoimmunity?" |

#### 3.2 Crux Inventory

```
CRUX 1: [Concise statement of the disagreement]
  Type: [Empirical / Methodological / Value / Framework]
  Side A believes: [X]
  Side B believes: [Y]
  Why this matters: [How resolving this crux would change the debate]
  Current evidence: [What data exists, with gaps identified]
  Resolvability: [High / Medium / Low]

CRUX 2: [Concise statement of the disagreement]
  Type: [Empirical / Methodological / Value / Framework]
  Side A believes: [X]
  Side B believes: [Y]
  ...

[Continue for all identified cruxes]
```

#### 3.3 Crux Map Visualization

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_crux_map(cruxes, title="Crux Map: Disagreement Landscape"):
    """
    Visualize cruxes on a 2D map: x-axis = importance to debate outcome,
    y-axis = resolvability.

    Parameters:
    - cruxes: list of dicts with keys 'name', 'importance' (0-10),
              'resolvability' (0-10), 'type' (empirical/methodological/value/framework)
    """
    fig, ax = plt.subplots(figsize=(12, 10))

    type_colors = {
        'empirical': '#2ecc71',
        'methodological': '#3498db',
        'value': '#e74c3c',
        'framework': '#9b59b6'
    }

    # Fill quadrants
    ax.axhline(y=5, color='gray', linestyle='--', alpha=0.3)
    ax.axvline(x=5, color='gray', linestyle='--', alpha=0.3)

    # Quadrant labels
    ax.text(7.5, 8, 'HIGH PRIORITY\nImportant + Resolvable', ha='center', va='center',
            fontsize=10, alpha=0.3, fontweight='bold', color='green')
    ax.text(2.5, 8, 'WORTH TRYING\nLess important but resolvable', ha='center', va='center',
            fontsize=10, alpha=0.3, fontweight='bold', color='blue')
    ax.text(7.5, 2, 'FUNDAMENTAL\nImportant but hard to resolve', ha='center', va='center',
            fontsize=10, alpha=0.3, fontweight='bold', color='red')
    ax.text(2.5, 2, 'PARK IT\nLess important + hard to resolve', ha='center', va='center',
            fontsize=10, alpha=0.3, fontweight='bold', color='gray')

    for c in cruxes:
        color = type_colors.get(c['type'], '#7f8c8d')
        ax.scatter(c['importance'], c['resolvability'], c=color, s=250,
                   zorder=5, edgecolors='black', linewidth=1.5)
        ax.annotate(c['name'], (c['importance'], c['resolvability']),
                    textcoords="offset points", xytext=(12, 5), fontsize=9,
                    fontweight='bold')

    # Legend
    import matplotlib.patches as mpatches
    legend_elements = [
        mpatches.Patch(facecolor=v, label=k.capitalize())
        for k, v in type_colors.items()
    ]
    ax.legend(handles=legend_elements, loc='lower left', fontsize=10)

    ax.set_xlabel('Importance to Debate Outcome (0-10)', fontsize=12)
    ax.set_ylabel('Resolvability (0 = intractable, 10 = easily resolved)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-0.5, 10.5)
    ax.grid(True, alpha=0.15)

    plt.tight_layout()
    plt.savefig('crux_map.png', dpi=150, bbox_inches='tight')
    plt.show()
```

#### 3.4 Hidden Agreement Discovery

Before proceeding, explicitly identify points where the two sides actually AGREE. Debates often focus on disagreements and overlook substantial common ground.

```
POINTS OF AGREEMENT:
1. [Both sides agree that...] — Significance: [Why this matters]
2. [Both sides agree that...] — Significance: [Why this matters]
3. [Both sides agree that...] — Significance: [Why this matters]

SURPRISING AGREEMENTS:
  [Areas where the sides agree but would not have expected to]

AGREEMENT PERCENTAGE: [Rough estimate of what fraction of the relevant
  claims both sides accept — often much higher than participants realize]
```

---

### Phase 4: Resolution Design

For each empirical and methodological crux, design an experiment or analysis that would resolve the disagreement. Value cruxes cannot be resolved with data but can be clarified.

#### 4.1 Resolution Experiment Design

```
CRUX: [Statement of the disagreement]
TYPE: [Empirical / Methodological]

SIDE A'S PREDICTION: [If we ran this experiment, Side A predicts...]
SIDE B'S PREDICTION: [If we ran this experiment, Side B predicts...]

PROPOSED RESOLUTION EXPERIMENT:
  Design: [Experiment description]
  Key measurement: [What exactly would be measured]
  Decision criterion: [What result would favor Side A vs Side B]
    Side A wins if: [specific, quantitative threshold]
    Side B wins if: [specific, quantitative threshold]
    Inconclusive if: [what would fail to distinguish]

PRE-COMMITMENT:
  Side A: "If the result shows [X], I will update my confidence to [Y]%"
  Side B: "If the result shows [X], I will update my confidence to [Y]%"

FEASIBILITY:
  Can this experiment actually be done? [Yes / Partially / No]
  If not, why? [Cost, ethics, time, technology]
  Proxy experiment: [What's the closest feasible alternative?]

EXISTING EVIDENCE:
  Has this experiment (or a close analogue) already been done?
  [Search results from MCP tools]
```

```
Search for existing resolution evidence:
  mcp__pubmed__pubmed_data(method: "search",
    query: "[crux topic] randomized controlled trial OR meta-analysis",
    num_results: 15)

  mcp__ctgov__ctgov_data(method: "search",
    condition: "[relevant condition]",
    intervention: "[relevant intervention]")
```

#### 4.2 Value Crux Clarification

Value cruxes cannot be resolved with experiments, but they can be clarified so that the disagreement is transparent.

```
VALUE CRUX: [Statement]

SIDE A'S VALUE PRIORITY: [What Side A considers most important and why]
SIDE B'S VALUE PRIORITY: [What Side B considers most important and why]

REFRAME AS TRADE-OFF:
  [Restate as: "How much of X are we willing to sacrifice for Y?"]
  Side A threshold: [X amount of sacrifice is acceptable for Y gain]
  Side B threshold: [X amount of sacrifice is acceptable for Y gain]

BRIDGING QUESTION:
  [Is there a solution that partially satisfies both value priorities?]
```

#### 4.3 Framework Crux Resolution

Framework cruxes can sometimes be resolved by identifying predictions where the frameworks diverge.

```
FRAMEWORK CRUX: [Side A uses framework X, Side B uses framework Y]

SHARED PREDICTIONS: [Where both frameworks predict the same thing]
DIVERGENT PREDICTIONS: [Where the frameworks predict different outcomes]

CRITICAL TEST:
  If we observe [Z], Framework X is supported because [reason]
  If we observe [NOT Z], Framework Y is supported because [reason]

EXISTING EVIDENCE ON DIVERGENT PREDICTIONS:
  [What do we already know about the predictions where frameworks diverge?]
```

---

### Phase 5: Joint Synthesis

Produce a fair summary that both sides could endorse, covering areas of agreement, resolved disagreements, and remaining unresolved disagreements.

#### 5.1 Joint Statement

```
JOINT STATEMENT:
  [A paragraph both sides could sign, summarizing what was learned]

RESOLVED CRUXES:
  Crux [N]: [Statement]
    Resolution: [What the evidence shows]
    Confidence: [How certain is this resolution?]
    Updated positions:
      Side A: [Updated confidence and any position modification]
      Side B: [Updated confidence and any position modification]

UNRESOLVED CRUXES:
  Crux [N]: [Statement]
    Type: [Empirical / Methodological / Value / Framework]
    Why unresolved: [Insufficient data / Value difference / Framework difference]
    Path to resolution: [What would be needed]

JOINT RECOMMENDATIONS:
  Despite remaining disagreements, both sides recommend:
  1. [Action both sides support]
  2. [Action both sides support]
  3. [Action both sides support]

CONDITIONAL RECOMMENDATIONS:
  If [Crux N is resolved in Side A's favor]:
    [Recommended action]
  If [Crux N is resolved in Side B's favor]:
    [Recommended action]
```

#### 5.2 Confidence Update Tracking

```
CONFIDENCE EVOLUTION:
                    Phase 1    Phase 2    Phase 5    Delta
Side A confidence:  [X]%       [Y]%       [Z]%       [+/-N]%
Side B confidence:  [X]%       [Y]%       [Z]%       [+/-N]%

BAYESIAN UPDATE LOG:
  Side A updated because: [specific evidence or argument that changed confidence]
  Side B updated because: [specific evidence or argument that changed confidence]

  If neither side updated significantly:
    [Is this because the evidence is genuinely balanced,
     or because both sides are anchored to their priors?]
```

#### 5.3 Confidence Evolution Visualization

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_confidence_evolution(phases, side_a_confidence, side_b_confidence,
                              side_a_label="Side A", side_b_label="Side B",
                              title="Confidence Evolution Through Deliberation"):
    """
    Track how each side's confidence changes through the 5 phases.

    Parameters:
    - phases: list of phase names ['Position', 'Steel-Man', 'Crux ID', 'Resolution', 'Synthesis']
    - side_a_confidence: list of confidence values (0-100) for Side A at each phase
    - side_b_confidence: list of confidence values (0-100) for Side B at each phase
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(phases))

    ax.plot(x, side_a_confidence, 'o-', color='#3498db', linewidth=2.5,
            markersize=10, label=side_a_label)
    ax.plot(x, side_b_confidence, 's-', color='#e74c3c', linewidth=2.5,
            markersize=10, label=side_b_label)

    # Annotate confidence values
    for i, (a, b) in enumerate(zip(side_a_confidence, side_b_confidence)):
        ax.annotate(f'{a}%', (i, a), textcoords="offset points",
                    xytext=(0, 12), ha='center', fontweight='bold', color='#3498db')
        ax.annotate(f'{b}%', (i, b), textcoords="offset points",
                    xytext=(0, -18), ha='center', fontweight='bold', color='#e74c3c')

    # Convergence zone
    final_gap = abs(side_a_confidence[-1] - side_b_confidence[-1])
    if final_gap < 20:
        convergence_y = (side_a_confidence[-1] + side_b_confidence[-1]) / 2
        ax.annotate(f'Gap: {final_gap}%', (len(phases)-1, convergence_y),
                    textcoords="offset points", xytext=(30, 0), fontsize=11,
                    fontweight='bold', color='green',
                    arrowprops=dict(arrowstyle='->', color='green'))

    ax.set_xticks(x)
    ax.set_xticklabels(phases, fontsize=11)
    ax.set_ylabel('Confidence in Own Position (%)', fontsize=12)
    ax.set_ylim(0, 105)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(fontsize=12, loc='best')
    ax.grid(True, alpha=0.2, axis='y')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig('confidence_evolution.png', dpi=150, bbox_inches='tight')
    plt.show()
```

---

## Debate Archetypes

The user may specify a debate type, or it can be auto-detected from the question.

### 1. Mechanism Debate
**Pattern:** "Works via pathway A vs. pathway B" | **Typical cruxes:** Empirical + framework | **Resolution:** Find experiments where pathways predict different outcomes; use pathway-specific inhibitors.

### 2. Efficacy Debate
**Pattern:** "Treatment works vs. doesn't work" | **Typical cruxes:** Empirical + methodological | **Resolution:** Meta-analysis of existing trials; identify methodological factors predicting positive vs. negative results; design the definitive trial.

### 3. Risk-Benefit Debate
**Pattern:** "Benefits outweigh risks vs. risks too high" | **Typical cruxes:** Value + empirical | **Resolution:** Separate empirical questions (actual rates) from value questions (acceptable thresholds).

### 4. Methodology Debate
**Pattern:** "Approach X is valid vs. flawed" | **Typical cruxes:** Methodological + empirical | **Resolution:** Identify method assumptions, test each, find cases where method produces known-wrong or known-right answers.

### 5. Priority Debate
**Pattern:** "Focus on X vs. Y" | **Typical cruxes:** Value + empirical | **Resolution:** Separate feasibility (empirical) from importance (value); both sides rate opposing priority.

### 6. Interpretation Debate
**Pattern:** "Data supports conclusion A vs. B" | **Typical cruxes:** Framework + methodological | **Resolution:** Find divergent predictions between interpretations; check confounders.

---

## Collaboration Quality Score (0-100)

Rate the quality of the debate process, NOT who wins.

### Score Components

| Dimension | Max Points | Criteria |
|-----------|-----------|----------|
| **Genuine Engagement** | 20 | Did each side truly engage with the other's arguments? |
| **Evidence Quality** | 20 | Was evidence cited, tiered, and verifiable? |
| **Crux Identification** | 20 | Were real disagreements identified and categorized? |
| **Resolution Feasibility** | 20 | Are proposed experiments practical and decisive? |
| **Synthesis Quality** | 20 | Does the conclusion fairly represent both sides? |

### Scoring Rubric

**Genuine Engagement (0-20):**
- 17-20: Both sides meaningfully updated confidence; steel-mans acknowledged by opposing side as accurate
- 13-16: Good engagement with some residual strawmanning
- 9-12: Engagement present but superficial; steel-mans are weak
- 5-8: Minimal engagement; each side mostly restated its own position
- 0-4: No genuine engagement; talking past each other

**Evidence Quality (0-20):**
- 17-20: >80% of claims cite T1/T2 evidence; all key claims verifiable
- 13-16: >60% T1/T2 evidence; most claims supported
- 9-12: Mixed evidence quality; some key claims unsupported
- 5-8: Mostly T3/T4 evidence; many claims are assertions
- 0-4: Minimal evidence cited; argument by assertion

**Crux Identification (0-20):**
- 17-20: All cruxes identified, correctly typed, importance ranked; hidden agreements discovered
- 13-16: Most cruxes identified and typed; some agreements found
- 9-12: Some cruxes identified but typing incomplete
- 5-8: Cruxes vaguely stated; types not distinguished
- 0-4: No meaningful crux identification

**Resolution Feasibility (0-20):**
- 17-20: All empirical cruxes have feasible resolution experiments with clear decision criteria and pre-commitments
- 13-16: Most cruxes have resolution designs; some decision criteria unclear
- 9-12: Resolution designs exist but are vague or impractical
- 5-8: Minimal resolution design; mostly "more research needed"
- 0-4: No resolution experiments proposed

**Synthesis Quality (0-20):**
- 17-20: Both sides endorse the synthesis; joint recommendations are actionable; conditional recommendations cover remaining uncertainty
- 13-16: Fair synthesis with minor imbalances; recommendations mostly actionable
- 9-12: Synthesis present but favors one side; recommendations vague
- 5-8: Synthesis is a restatement of positions, not a joint product
- 0-4: No meaningful synthesis

### Quality Tiers

| Score | Tier | Interpretation |
|-------|------|---------------|
| **80-100** | Excellent | Genuine adversarial collaboration; both sides engaged, updated, and synthesized |
| **60-79** | Good | Solid debate with room for deeper engagement or better resolution designs |
| **40-59** | Adequate | Debate occurred but lacked depth in crux identification or resolution |
| **20-39** | Poor | Superficial debate; mostly restating positions without genuine engagement |
| **0-19** | Failed | Not a real debate; one-sided or no meaningful exchange |

---

## Analysis Modes

### Quick Debate (3 Phases)

Phases 1, 3, and 5 only: Position statements, crux identification, joint synthesis. Skip steel-manning and resolution design.

**When to use:**
- Initial exploration of a debate space
- Time-sensitive analysis where key disagreements need identification
- When the user wants to understand what the core disagreements ARE, not resolve them
- Preliminary assessment before committing to full adversarial collaboration

### Full Adversarial Collaboration (All 5 Phases)

Complete methodology with steel-manning, detailed crux analysis, resolution experiments, and joint synthesis.

**When to use:**
- High-stakes decisions where the truth matters more than speed
- Evaluating competing scientific theories with substantial evidence on both sides
- Resolving persistent disagreements within research teams
- Any situation where the cost of being wrong is high

### Serial Debate
Multiple rounds of the 5-phase process, incorporating evidence from previous rounds. Use for complex topics with interrelated cruxes or long-running research questions.

### Panel Debate (2+ Sides)
Extension to 3+ positions. Run pairwise crux identification for each pair, then synthesize into multi-position joint statement. Use when binary framing oversimplifies or for multi-stakeholder decisions.

---

## Python Code Templates

### Debate Summary Dashboard

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_debate_dashboard(side_a_label, side_b_label, side_a_args, side_b_args,
                           cruxes, quality_scores, title="Adversarial Collaboration Dashboard"):
    """
    Generate a multi-panel dashboard: argument strength comparison, crux status,
    quality radar, and summary statistics.

    Parameters:
    - side_a/b_label: str, side_a/b_args: list of dicts {'name', 'strength' (0-10)}
    - cruxes: list of dicts {'name', 'type', 'resolved' (bool)}
    - quality_scores: dict with 5 scoring dimensions -> int scores
    """
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.3)

    # Panel 1: Argument Strength Comparison
    ax1 = fig.add_subplot(gs[0, 0])
    max_args = max(len(side_a_args), len(side_b_args))
    y = np.arange(max_args)
    a_s = [a['strength'] for a in side_a_args] + [0]*(max_args-len(side_a_args))
    b_s = [b['strength'] for b in side_b_args] + [0]*(max_args-len(side_b_args))
    ax1.barh(y-0.2, a_s, 0.35, color='#3498db', label=side_a_label)
    ax1.barh(y+0.2, b_s, 0.35, color='#e74c3c', label=side_b_label)
    ax1.set_yticks(y); ax1.set_yticklabels([f'Arg {i+1}' for i in range(max_args)])
    ax1.set_xlabel('Strength (0-10)'); ax1.set_title('Argument Comparison', fontweight='bold')
    ax1.legend(); ax1.invert_yaxis()

    # Panel 2: Crux Status
    ax2 = fig.add_subplot(gs[0, 1])
    tc = {'empirical':'#2ecc71','methodological':'#3498db','value':'#e74c3c','framework':'#9b59b6'}
    for i, c in enumerate(cruxes):
        ax2.scatter(i, 0.5, c=tc.get(c['type'],'#7f8c8d'), s=300,
                    marker='o' if c['resolved'] else 'x', zorder=5, edgecolors='black', linewidth=2)
        ax2.annotate(c['name'][:20], (i,0.5), textcoords="offset points", xytext=(0,20),
                     ha='center', fontsize=8, rotation=45)
    ax2.set_ylim(0,1); ax2.set_yticks([]); ax2.set_title('Cruxes (o=resolved, x=open)', fontweight='bold')

    # Panel 3: Quality Radar
    ax3 = fig.add_subplot(gs[1, 0], polar=True)
    cats = list(quality_scores.keys()); vals = [v/20 for v in quality_scores.values()]
    angles = np.linspace(0, 2*np.pi, len(cats), endpoint=False).tolist()
    vals += vals[:1]; angles += angles[:1]
    ax3.fill(angles, vals, color='#3498db', alpha=0.25)
    ax3.plot(angles, vals, 'o-', color='#3498db', linewidth=2)
    ax3.set_xticks(angles[:-1]); ax3.set_xticklabels([c[:12] for c in cats], fontsize=8)
    ax3.set_ylim(0,1); ax3.set_title(f'Quality: {sum(quality_scores.values())}/100', fontweight='bold', pad=20)

    # Panel 4: Summary
    ax4 = fig.add_subplot(gs[1, 1]); ax4.axis('off')
    r = sum(1 for c in cruxes if c['resolved']); t = len(cruxes)
    txt = f"Sides: {side_a_label} vs {side_b_label}\nCruxes: {r}/{t} resolved\nScore: {sum(quality_scores.values())}/100"
    ax4.text(0.1, 0.7, txt, transform=ax4.transAxes, fontsize=13, fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='#ecf0f1', alpha=0.8))
    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.savefig('debate_dashboard.png', dpi=150, bbox_inches='tight'); plt.show()
```

### Agreement vs Disagreement Pie Chart

```python
import matplotlib.pyplot as plt

def plot_agreement_breakdown(agree, resolved, unresolved, title="Agreement vs Disagreement"):
    """Visualize agreed, resolved, and unresolved portions of the debate."""
    fig, ax = plt.subplots(figsize=(8, 8))
    sizes = [agree, resolved, unresolved]
    labels = [f'Agreed ({agree})', f'Resolved ({resolved})', f'Unresolved ({unresolved})']
    colors = ['#2ecc71', '#3498db', '#e74c3c']
    ax.pie(sizes, explode=(0,0,0.05), labels=labels, colors=colors, autopct='%1.0f%%',
           startangle=90, textprops={'fontsize': 12})
    ax.set_title(title, fontsize=14, fontweight='bold')
    plt.tight_layout(); plt.savefig('agreement_breakdown.png', dpi=150, bbox_inches='tight'); plt.show()
```

---

## Evidence Grading for Debate Arguments

| Tier | Label | Criteria | Debate Application |
|------|-------|----------|-------------------|
| **T1** | Definitive | Regulatory filings, replicated RCTs, established physical laws | Arguments supported by T1 evidence carry highest weight |
| **T2** | Strong | Peer-reviewed studies, meta-analyses, systematic reviews | Standard evidence for debate arguments |
| **T3** | Moderate | Conference abstracts, preprints, single studies | Acceptable but flagged as requiring confirmation |
| **T4** | Weak | Expert opinion, press releases, analogy, theoretical reasoning | Must be explicitly flagged; cannot be sole support for a key argument |

**Debate-specific rules:**
- Both sides' evidence must be graded by the same standards
- A T1 argument on one side does not automatically defeat a T1 argument on the other
- Asymmetric evidence quality should be noted (one side has stronger evidence base)
- When evidence tiers are equal, argument quality and internal consistency determine strength

---

## Multi-Agent Workflow Examples

### Example 1: "Does metformin extend lifespan in non-diabetic humans?"

1. **Adversarial Collaboration (this skill)** -> Side A: Yes, based on observational data and biological mechanisms. Side B: No, observational data is confounded and mechanisms do not translate. Identify cruxes: empirical (does TAME trial show benefit?), methodological (are observational studies valid here?), framework (is aging a treatable condition?).
2. **Literature Deep Research** -> Gather T1/T2 evidence for both sides from clinical and preclinical literature.
3. **Clinical Trial Analyst** -> Analyze TAME trial design and whether it can resolve the empirical crux.
4. **Hypothesis Generation** -> Generate hypotheses for mechanisms that would reconcile conflicting evidence.

### Example 2: "Surrogate endpoints: are accelerated approvals based on biomarkers good for patients?"

1. **Adversarial Collaboration (this skill)** -> Side A: Faster access to potentially life-saving drugs justifies biomarker-based approvals. Side B: Too many accelerated approvals fail confirmatory trials, exposing patients to ineffective drugs. Cruxes: empirical (what % fail confirmation?), value (how much risk is acceptable for speed?), methodological (are current surrogates validated?).
2. **FDA Consultant** -> Regulatory history of accelerated approvals and confirmatory trial outcomes.
3. **What-If Oracle** -> Model scenarios under different accelerated approval threshold policies.
4. **Systematic Literature Reviewer** -> Meta-analysis of surrogate endpoint correlation with clinical outcomes.

### Example 3: "Should this drug program pivot from monotherapy to combination?"

1. **Adversarial Collaboration (this skill)** -> Side A: Monotherapy has best-in-class potential; combination adds complexity without clear benefit. Side B: Monotherapy ceiling is too low; combination unlocks synergy and competitive differentiation. Cruxes: empirical (is there preclinical synergy data?), methodological (can synergy be measured reliably?), value (risk of complexity vs. potential upside).
2. **Drug Research** -> Comprehensive monotherapy profile and competitive landscape.
3. **Clinical Trial Protocol Designer** -> Design a trial that would resolve the efficacy crux (monotherapy vs. combination arm).
4. **Competitive Intelligence** -> Map competitor combination strategies in the same indication.

### Example 4: "Is AI-driven drug discovery fundamentally better, or is it hype?"

1. **Adversarial Collaboration (this skill)** -> Side A: AI identifies candidates faster, cheaper, with better properties. Side B: AI-discovered drugs have not yet proven superior in clinical outcomes; successes are selection-biased. Cruxes: empirical (clinical success rates of AI-discovered vs. traditional drugs), methodological (how to compare fairly given different development timelines), framework (is drug discovery an optimization problem or a discovery problem?).
2. **First Principles** -> Break down drug discovery to fundamentals: what constraints does AI actually relax vs. which remain immovable?
3. **Literature Deep Research** -> Gather evidence on AI-discovered drugs in clinical development.
4. **What-If Oracle** -> Model scenarios for AI-driven drug discovery over the next 10 years.

### Example 5: "CRISPR gene therapy: in vivo vs. ex vivo editing"

1. **Adversarial Collaboration (this skill)** -> Side A: In vivo editing is the future (no cell manufacturing, broader tissue access). Side B: Ex vivo editing is safer and more controllable (known cell product, easier quality control). Cruxes: empirical (in vivo off-target rates), methodological (how to measure off-targets in vivo), value (safety vs. accessibility trade-off).
2. **Hypothesis Generation** -> Generate hypotheses about which diseases favor which approach.
3. **Clinical Trial Analyst** -> Compare clinical outcomes of in vivo vs. ex vivo gene therapy trials.
4. **FDA Consultant** -> Regulatory perspective on safety requirements for each approach.

---

## Report Template

```
# Adversarial Collaboration Report: [DEBATE TOPIC]
Generated: [DATE]
Analysis Mode: [Quick / Full / Serial / Panel]
Collaboration Quality Score: [X/100] ([Tier])
Debate Archetype: [Mechanism / Efficacy / Risk-Benefit / Methodology / Priority / Interpretation]

## 1. Executive Summary
[2-3 paragraphs: the question, key findings, what was resolved vs. not]

## 2. Side A: [Position Label]
### Position Statement
[Clear statement with confidence level]

### Key Arguments
| # | Argument | Evidence | Tier | Strength |
|---|---------|----------|------|----------|

### Self-Identified Weakness
[Weakest point in own position]

## 3. Side B: [Position Label]
### Position Statement
[Clear statement with confidence level]

### Key Arguments
| # | Argument | Evidence | Tier | Strength |
|---|---------|----------|------|----------|

### Self-Identified Weakness
[Weakest point in own position]

## 4. Steel-Manning
### Side A acknowledges Side B's strongest argument
[Genuine engagement with opposing best argument]

### Side B acknowledges Side A's strongest argument
[Genuine engagement with opposing best argument]

## 5. Crux Analysis
### Crux Inventory
| # | Crux | Type | Importance | Resolvability | Status |
|---|------|------|-----------|---------------|--------|

### Hidden Agreements
[Points where both sides agree, including surprises]

## 6. Resolution Designs
### Crux [N]: [Statement]
[Experiment design, decision criteria, pre-commitments, feasibility]

[Repeat for each empirical/methodological crux]

### Value Crux Clarifications
[For value cruxes: trade-off reframing, bridging questions]

## 7. Joint Synthesis
### Joint Statement
[Statement both sides could endorse]

### Resolved Cruxes
[What was resolved and how]

### Unresolved Cruxes
[What remains and what would resolve it]

### Joint Recommendations
[Actions both sides support]

### Conditional Recommendations
[Actions contingent on crux resolution]

## 8. Confidence Evolution
| Phase | Side A | Side B |
|-------|--------|--------|
| Position Statement | [X]% | [X]% |
| Steel-Manning | [X]% | [X]% |
| Crux Identification | [X]% | [X]% |
| Resolution Design | [X]% | [X]% |
| Joint Synthesis | [X]% | [X]% |

## 9. Collaboration Quality Score
| Dimension | Score | Max | Rationale |
|-----------|-------|-----|-----------|
| Genuine Engagement | [X] | 20 | |
| Evidence Quality | [X] | 20 | |
| Crux Identification | [X] | 20 | |
| Resolution Feasibility | [X] | 20 | |
| Synthesis Quality | [X] | 20 | |
| **TOTAL** | **[X]** | **100** | **[Tier]** |

## 10. Next Steps
[Specific actions: experiments to run, data to gather, decisions to make]
```

---

## Completeness Checklist

- [ ] Both sides' positions stated clearly with 3-5 arguments each and evidence tiers
- [ ] Both sides self-identified their weakest point (intellectual honesty check)
- [ ] Steel-manning completed: each side identified the opposing side's BEST argument
- [ ] Steel-mans are genuine (would the opposing side agree "yes, that's my best point"?)
- [ ] Both sides explicitly stated what evidence would make them update their confidence
- [ ] All cruxes identified and categorized by type (empirical, methodological, value, framework)
- [ ] Hidden agreements discovered and documented
- [ ] Resolution experiments designed for each empirical and methodological crux
- [ ] Decision criteria for resolution experiments are specific and quantitative
- [ ] Pre-commitments made: both sides stated how they would update given specific results
- [ ] Value cruxes reframed as trade-offs with threshold analysis
- [ ] Framework cruxes analyzed for divergent predictions
- [ ] Joint statement written that both sides could endorse
- [ ] Confidence tracked across all phases with Bayesian update log
- [ ] Collaboration Quality Score calculated with dimension-by-dimension breakdown
- [ ] Evidence grading (T1-T4) applied consistently to both sides' arguments
- [ ] MCP tools used to gather evidence for both sides (not selectively)
- [ ] Debate archetype identified and archetype-specific analysis applied
- [ ] Report file created with all sections populated (no remaining placeholders)
- [ ] Visualization code provided for key charts (crux map, confidence evolution, agreement breakdown)
