---
name: first-principles
description: Systematic first-principles reasoning that breaks complex problems down to foundational truths and rebuilds understanding from scratch. Uses a 6-phase methodology (State Problem, Strip Assumptions, Identify Foundations, Map Constraints, Reconstruct, Validate) with reasoning traceability chains, analogy detection, and constraint space mapping. Generates structured reports with assumption inventories, constraint classifications, and novel approaches revealed by fundamental analysis. Use when asked to reason from first principles, challenge assumptions, find novel solutions, understand why something works the way it does, question conventional wisdom, or analyze a problem from the ground up.
---

# First Principles Reasoning

Systematic methodology for breaking complex problems down to foundational truths and rebuilding understanding from scratch. Strips away assumptions, conventions, and analogies to identify what is fundamentally true, maps the actual constraint space, and reconstructs solutions that conventional thinking would miss.

Distinct from **systems-thinking** (which maps interconnections and feedback loops within existing systems), **what-if-oracle** (which explores branching scenarios from a decision point), and **hypothesis-generation** (which generates and ranks competing explanations for observed phenomena). This skill operates at the epistemological level, questioning the foundations on which other analyses rest.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_first_principles_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as analysis proceeds through each phase
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Mapping system interconnections, feedback loops, or emergent behavior -> use `systems-biology` or systems-thinking approaches
- Exploring branching scenarios and probability-weighted outcomes -> use `what-if-oracle`
- Generating and ranking competing hypotheses for a phenomenon -> use `hypothesis-generation`
- Reviewing a manuscript or evaluating scientific rigor -> use `peer-review`
- Structured debate between opposing positions -> use `adversarial-collaboration`
- Statistical modeling or data analysis -> use `statistical-modeling`
- Literature search and evidence synthesis -> use `literature-deep-research`
- Critical evaluation of reasoning and logical fallacies -> use `scientific-critical-thinking`

## Cross-Skill Routing

- Need to test hypotheses generated from first-principles reconstruction -> `hypothesis-generation`
- Need to explore scenarios after identifying novel possibilities -> `what-if-oracle`
- Need to debate whether conventional or first-principles approach is better -> `adversarial-collaboration`
- Need to validate scientific claims underlying foundational truths -> `peer-review`
- Need literature evidence to support or challenge assumptions -> `literature-deep-research`
- Need to map system dynamics after identifying fundamental components -> `systems-biology`
- Need regulatory context for constraint classification -> `fda-consultant`
- Need economic modeling for cost constraints -> `what-if-oracle`

---

## Available MCP Tools

### `mcp__pubmed__pubmed_data` (Evidence for Foundational Claims)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search PubMed by keywords, MeSH terms | `query`, `num_results` |
| `fetch_details` | Full article metadata: abstract, authors, DOI, MeSH | `pmid` |

**First-principles uses:** Verify whether claimed "laws" or "fundamental truths" are actually supported by evidence. Find counterexamples that challenge assumptions. Locate original papers establishing foundational principles.

### `mcp__opentargets__opentargets_data` (Biological Foundation Verification)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability) | `id` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId`, `diseaseId`, `minScore`, `size` |

**First-principles uses:** Verify biological mechanisms cited as foundational truths. Distinguish between well-established target biology (hard constraint) and speculative associations (soft or imagined constraint).

### `mcp__chembl__chembl_data` (Chemical/Pharmacological Foundations)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |

**First-principles uses:** Verify chemical feasibility claims. Check whether "impossible" chemistry has actually been achieved. Find precedent for unconventional approaches.

### `mcp__ctgov__ctgov_data` (Clinical Precedent Verification)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search clinical trials by condition, intervention | `condition`, `intervention`, `phase`, `status` |
| `get` | Full trial details by NCT ID | `nctId` |

**First-principles uses:** Check whether "never been tried" assumptions are actually true. Find precedent for unconventional clinical approaches.

---

## Core Framework: 6-Phase First-Principles Methodology

### Phase 1: State the Problem

Define what we are trying to understand, solve, or build with precision.

| Component | Questions to Answer |
|-----------|-------------------|
| **Core question** | What exactly are we trying to achieve? State in one sentence. |
| **Conventional approach** | How does the field currently approach this? Why? |
| **Common knowledge** | What does "everyone know" about this problem? |
| **Conventional constraints** | What limitations are assumed to be immovable? |
| **Success criteria** | What would a successful answer look like? |
| **Scope boundaries** | What is explicitly out of scope for this analysis? |

**Problem precision test:**
```
VAGUE: "How can we treat cancer better?"
PRECISE: "What are the fundamental biological constraints on achieving
          durable complete responses in solid tumors with immunotherapy,
          and which of these constraints are truly immovable vs.
          conventionally assumed to be immovable?"
```

**Conventional wisdom inventory:**
```
"Everyone knows that..."
1. [Statement] — Source: [Where this belief comes from]
2. [Statement] — Source: [Where this belief comes from]
3. [Statement] — Source: [Where this belief comes from]
...
```

---

### Phase 2: Strip Away Assumptions

Systematically identify and categorize every assumption, explicit and implicit.

#### 2.1 Assumption Extraction

For every claim in the conventional understanding, ask:
1. Is this a **fundamental truth** (physical/chemical/biological law)?
2. Is this an **empirical observation** (repeatedly measured, but not a law)?
3. Is this a **convention** (we do it this way because we always have)?
4. Is this an **untested assumption** (believed but never rigorously verified)?
5. Is this an **analogy from another domain** (borrowed reasoning that may not transfer)?

#### 2.2 Assumption Inventory Table

| # | Assumption | Type | Fragile? | Evidence | Source |
|---|-----------|------|----------|----------|--------|
| A1 | [Explicit assumption] | Fundamental / Empirical / Convention / Untested / Analogy | Yes/No | [What supports it] | [Where belief originates] |
| A2 | ... | ... | ... | ... | ... |

**Rules for categorization:**
- **Fundamental truth**: Would require new physics/chemistry/biology to violate. Examples: thermodynamics, conservation of mass, DNA encodes proteins.
- **Empirical observation**: Consistently measured but could have exceptions. Examples: most drugs fail in Phase 3, oral bioavailability correlates with logP.
- **Convention**: Standard practice not derived from fundamental constraint. Examples: 12-week treatment duration, ICH stability testing conditions, 5% significance threshold.
- **Untested assumption**: Widely believed but lacking rigorous evidence. Examples: "patients won't accept this route of administration," "this target is undruggable."
- **Analogy**: Reasoning borrowed from a different context. Examples: "the immune system is like an army" (breaks at mechanistic level), "drug development is like software development" (breaks at regulatory level).

#### 2.3 Analogy Detection and Breaking

For each identified analogy:

```
ANALOGY: [X is like Y]
SOURCE DOMAIN: [Where the analogy comes from]
TARGET DOMAIN: [Where it is being applied]
HOLDS AT: [What levels/scales the analogy is accurate]
BREAKS AT: [Where the analogy fails — specific mechanisms]
CONSEQUENCE: [What we get wrong by relying on this analogy]
REPLACEMENT: [First-principles reasoning to use instead]
```

**Common broken analogies:**
- "Lock and key" for protein-ligand binding (breaks: induced fit, allostery, dynamics)
- "Blueprint" for genome (breaks: epigenetics, regulation, environment)
- "Magic bullet" for targeted therapy (breaks: off-target effects, resistance, heterogeneity)
- "Pipeline" for drug development (breaks: nonlinear, high failure rate, regulatory feedback)
- "Funnel" for patient selection (breaks: enrichment bias, lost populations)

```
Verify assumption evidence:
  mcp__pubmed__pubmed_data(method: "search",
    query: "[assumption] evidence review",
    num_results: 10)
  -> Is there actual evidence, or is this belief self-reinforcing?
```

---

### Phase 3: Identify Foundational Truths

After stripping assumptions, catalog what remains as genuinely fundamental.

#### 3.1 Physical and Chemical Laws

| Law/Principle | Statement | Relevance to Problem | Constraint Type |
|--------------|-----------|---------------------|-----------------|
| Thermodynamics (1st law) | Energy is conserved | [How it constrains the problem] | Hard |
| Thermodynamics (2nd law) | Entropy increases in isolated systems | [How it constrains the problem] | Hard |
| Chemical equilibrium | Reactions reach equilibrium governed by free energy | [How it constrains the problem] | Hard |
| Diffusion limits | Mass transport is governed by Fick's laws | [How it constrains the problem] | Hard |
| Binding kinetics | Kon/Koff rates determine drug-target occupancy | [How it constrains the problem] | Hard |

#### 3.2 Biological Principles

| Principle | Statement | Relevance | Constraint Type |
|-----------|-----------|-----------|-----------------|
| Central dogma | DNA -> RNA -> Protein (with known exceptions) | [Relevance] | Hard (with caveats) |
| Evolution by natural selection | Populations adapt under selective pressure | [Relevance] | Hard |
| Homeostasis | Biological systems resist perturbation | [Relevance] | Hard |
| Dose-response | All substances are toxic at sufficient dose | [Relevance] | Hard |

#### 3.3 Mathematical Constraints

| Constraint | Statement | Relevance | Constraint Type |
|-----------|-----------|-----------|-----------------|
| Information theory | Cannot extract signal below noise floor without more data | [Relevance] | Hard |
| Combinatorics | Chemical space is ~10^60 molecules | [Relevance] | Hard |
| Statistical power | N required scales with effect size squared | [Relevance] | Hard |
| Diminishing returns | Optimization faces diminishing marginal gains near optima | [Relevance] | Soft |

#### 3.4 Economic and Regulatory Realities

| Reality | Statement | Relevance | Constraint Type |
|---------|-----------|-----------|-----------------|
| Opportunity cost | Resources spent here cannot be spent elsewhere | [Relevance] | Hard |
| Supply/demand | Price is set by market dynamics | [Relevance] | Hard |
| Regulatory requirement | [Specific legal requirement] | [Relevance] | Hard (legal) |
| Regulatory convention | [Standard practice not legally required] | [Relevance] | Convention |

```
Verify biological foundations:
  mcp__opentargets__opentargets_data(method: "get_target_details", id: "[ENSG ID]")
  -> Is the claimed mechanism well-established or speculative?
```

---

### Phase 4: Map the Constraint Space

Classify every constraint by its actual rigidity, not its perceived rigidity.

#### 4.1 Constraint Classification

```
HARD CONSTRAINTS (violating would require new physics/biology)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
H1: [Constraint] — Law: [Which fundamental law]
H2: [Constraint] — Law: [Which fundamental law]
...

SOFT CONSTRAINTS (violating requires engineering, not miracles)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
S1: [Constraint] — Barrier: [What engineering challenge]
    Current status: [How close are we to overcoming this?]
S2: [Constraint] — Barrier: [What engineering challenge]
    Current status: [How close are we to overcoming this?]
...

IMAGINED CONSTRAINTS (convention or tradition, not actual limitation)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
I1: [Constraint] — Origin: [Why people believe this]
    Reality: [Why it is not actually a constraint]
I2: [Constraint] — Origin: [Why people believe this]
    Reality: [Why it is not actually a constraint]
...
```

#### 4.2 Constraint Space Visualization

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

def plot_constraint_space(hard, soft, imagined, title="Constraint Space Map"):
    """
    Plot constraints on a 2D map: x-axis = perceived difficulty,
    y-axis = actual difficulty. Reveals where convention overestimates
    or underestimates real constraints.

    Parameters:
    - hard: list of dicts with keys 'name', 'perceived' (0-10), 'actual' (0-10)
    - soft: list of dicts with keys 'name', 'perceived' (0-10), 'actual' (0-10)
    - imagined: list of dicts with keys 'name', 'perceived' (0-10), 'actual' (0-10)
    """
    fig, ax = plt.subplots(figsize=(12, 10))

    # Plot diagonal line (perceived = actual)
    ax.plot([0, 10], [0, 10], 'k--', alpha=0.3, label='Perceived = Actual')

    # Fill regions
    ax.fill_between([0, 10], [0, 10], [10, 10], alpha=0.05, color='red',
                     label='Underestimated difficulty')
    ax.fill_between([0, 10], [0, 0], [0, 10], alpha=0.05, color='green',
                     label='Overestimated difficulty (opportunity zone)')

    # Plot constraints
    for h in hard:
        ax.scatter(h['perceived'], h['actual'], c='#e74c3c', s=200,
                   marker='s', zorder=5, edgecolors='black')
        ax.annotate(h['name'], (h['perceived'], h['actual']),
                    textcoords="offset points", xytext=(10, 5), fontsize=8)

    for s in soft:
        ax.scatter(s['perceived'], s['actual'], c='#f39c12', s=200,
                   marker='D', zorder=5, edgecolors='black')
        ax.annotate(s['name'], (s['perceived'], s['actual']),
                    textcoords="offset points", xytext=(10, 5), fontsize=8)

    for i in imagined:
        ax.scatter(i['perceived'], i['actual'], c='#2ecc71', s=200,
                   marker='o', zorder=5, edgecolors='black')
        ax.annotate(i['name'], (i['perceived'], i['actual']),
                    textcoords="offset points", xytext=(10, 5), fontsize=8)

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='#e74c3c', label='Hard constraint (immovable)'),
        mpatches.Patch(facecolor='#f39c12', label='Soft constraint (engineering)'),
        mpatches.Patch(facecolor='#2ecc71', label='Imagined constraint (convention)'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10)

    ax.set_xlabel('Perceived Difficulty (0 = easy, 10 = impossible)', fontsize=12)
    ax.set_ylabel('Actual Difficulty (0 = easy, 10 = impossible)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-0.5, 10.5)
    ax.grid(True, alpha=0.2)

    plt.tight_layout()
    plt.savefig('constraint_space_map.png', dpi=150, bbox_inches='tight')
    plt.show()

# Example usage:
# hard = [{'name': 'Thermodynamic stability', 'perceived': 9, 'actual': 9}]
# soft = [{'name': 'Blood-brain barrier', 'perceived': 9, 'actual': 6}]
# imagined = [{'name': '"Undruggable" target', 'perceived': 9, 'actual': 3}]
# plot_constraint_space(hard, soft, imagined, "Drug Discovery Constraint Space")
```

#### 4.3 Possibility Frontier Plot

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_possibility_frontier(approaches, title="Possibility Frontier"):
    """
    Plot the theoretical vs conventional possibility space for different approaches.

    Parameters:
    - approaches: list of dicts with keys 'name', 'conventional_reach' (0-10),
                  'theoretical_reach' (0-10), 'current_best' (0-10)
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    y_positions = range(len(approaches))
    names = [a['name'] for a in approaches]

    for i, a in enumerate(approaches):
        # Theoretical maximum (full bar, light)
        ax.barh(i, a['theoretical_reach'], color='#2ecc71', alpha=0.3,
                height=0.6, label='Theoretical limit' if i == 0 else '')
        # Conventional reach (medium bar)
        ax.barh(i, a['conventional_reach'], color='#3498db', alpha=0.5,
                height=0.6, label='Conventional reach' if i == 0 else '')
        # Current best (dark bar)
        ax.barh(i, a['current_best'], color='#2c3e50', alpha=0.8,
                height=0.6, label='Current best' if i == 0 else '')
        # Gap annotation
        gap = a['theoretical_reach'] - a['conventional_reach']
        if gap > 0:
            ax.annotate(f'Untapped: {gap:.0f}', xy=(a['conventional_reach'] + gap/2, i),
                        ha='center', va='center', fontsize=8, color='#27ae60', fontweight='bold')

    ax.set_yticks(y_positions)
    ax.set_yticklabels(names)
    ax.set_xlabel('Performance / Reach (0-10)')
    ax.set_title(title, fontweight='bold')
    ax.legend(loc='lower right')
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig('possibility_frontier.png', dpi=150, bbox_inches='tight')
    plt.show()
```

---

### Phase 5: Reconstruct from Fundamentals

Starting only from the foundational truths identified in Phase 3, within the hard constraints mapped in Phase 4, rebuild understanding of what is actually possible.

#### 5.1 Reconstruction Protocol

```
STARTING POINT: Only foundational truths (Phase 3)
BOUNDARY: Only hard constraints (Phase 4)
IGNORE: All conventions, analogies, and untested assumptions

STEP 1: Given only the fundamental truths, what solutions are theoretically possible?
  -> List ALL possibilities, including ones that seem "crazy" by convention

STEP 2: For each theoretical possibility, what soft constraints stand in the way?
  -> For each soft constraint, what would it take to overcome it?

STEP 3: Which theoretical possibilities are NEWLY visible?
  -> These are solutions that convention obscured but physics allows
  -> These are the high-value outputs of first-principles thinking

STEP 4: Rank by feasibility gap (smallest gap = most actionable)
```

#### 5.2 Novel Approach Discovery

| # | Novel Approach | Why Convention Missed It | Feasibility Gap | Actionability |
|---|---------------|------------------------|-----------------|---------------|
| N1 | [Approach] | [Convention/analogy that obscured it] | [What's needed to implement] | High/Med/Low |
| N2 | [Approach] | [Convention/analogy that obscured it] | [What's needed to implement] | High/Med/Low |

#### 5.3 Reasoning Traceability

Every conclusion must chain back to a specific fundamental truth. This is the core discipline of first-principles reasoning.

**Required format for every claim:**

```
Conclusion: [X is possible]
  <- Because: [Y constraint is soft, not hard]
  <- Because: [Z is a convention, not a law]
  <- Fundamental truth: [Specific law or principle that permits X]
  <- Evidence: [Citation or measurement supporting this chain]
```

**Anti-pattern (reasoning by analogy, NOT first-principles):**
```
Conclusion: [X is not possible]
  <- Because: [It has never been done before]         # Appeal to convention
  <- Because: [Similar things in other fields failed]  # Analogy
  <- NO fundamental truth cited                        # RED FLAG
```

**Traceability validation questions:**
1. Can you name the specific physical/chemical/biological law?
2. If someone asked "why?" at each step, do you reach bedrock?
3. Is any step supported only by "everyone knows" or "it's always been this way"?
4. Would Elon Musk's "idiot index" (ratio of cost to raw material cost) reveal waste?

---

### Phase 6: Validate Reconstruction

Check whether the first-principles reconstruction survives contact with reality.

#### 6.1 Constraint Violation Check

```
For each novel approach from Phase 5:

APPROACH: [Description]
HARD CONSTRAINT CHECK:
  [ ] Does NOT violate thermodynamics
  [ ] Does NOT violate conservation laws
  [ ] Does NOT violate known biological laws
  [ ] Does NOT require currently impossible technology
  RESULT: [PASS / FAIL — if fail, which law is violated?]

SOFT CONSTRAINT CHECK:
  [ ] Engineering challenges are identified
  [ ] No "then a miracle occurs" steps
  [ ] Each soft constraint has a plausible path to resolution
  RESULT: [PASS with [N] engineering challenges / FAIL]
```

#### 6.2 Implementation Gap Assessment

| Gap Dimension | Current State | Required State | Gap Size | Bridgeable? |
|--------------|---------------|----------------|----------|-------------|
| Technology | [Current] | [Needed] | [Small/Med/Large] | [Yes/No/Maybe] |
| Knowledge | [Current] | [Needed] | [Small/Med/Large] | [Yes/No/Maybe] |
| Resources | [Current] | [Needed] | [Small/Med/Large] | [Yes/No/Maybe] |
| Regulatory | [Current] | [Needed] | [Small/Med/Large] | [Yes/No/Maybe] |
| Organizational | [Current] | [Needed] | [Small/Med/Large] | [Yes/No/Maybe] |

#### 6.3 Convention vs. First-Principles Comparison

```
CONVENTIONAL APPROACH:
  Method: [How it's currently done]
  Constraints assumed: [H1, S1, S2, I1, I2, I3]  # includes imagined
  Solution space: [Narrow]
  Performance: [Current benchmark]

FIRST-PRINCIPLES APPROACH:
  Method: [Reconstructed approach]
  Constraints actual: [H1, S1, S2]  # only real ones
  Solution space: [Broader]
  Performance potential: [Theoretical benchmark]
  Gap: [What's needed to get there]

VERDICT:
  [ ] First-principles approach reveals genuinely new possibilities
  [ ] First-principles approach confirms convention is approximately correct
  [ ] Convention is better than first-principles suggests (path dependence has value)
```

#### 6.4 Is Convention Actually Good Enough?

Sometimes first-principles analysis reveals that the conventional approach, while not optimal in theory, is practically good enough. This is a valid and important conclusion.

**Convention is good enough when:**
- The gap between theoretical optimum and convention is small
- The cost of switching exceeds the benefit of the improvement
- Path dependence creates value (established supply chains, trained workforce, regulatory precedent)
- The "imagined constraints" are actually reasonable engineering trade-offs

**Convention is NOT good enough when:**
- The gap is large and growing
- New technology makes the gap bridgeable at low cost
- The "imagined constraints" are genuinely imaginary (no one ever tested them)
- The problem is important enough that even small improvements matter

---

## Analysis Modes

### Quick Analysis (3 Phases)

Phases 1, 2, and 5 only: State the problem, strip assumptions, reconstruct. Skip detailed constraint mapping and validation. Complete in a single analysis session.

**When to use:**
- Initial exploration of a new problem
- Brainstorming sessions where speed matters more than rigor
- Quick challenge to conventional thinking
- When the user wants "fresh eyes" on a problem

### Deep Analysis (All 6 Phases)

Full methodology with complete assumption inventory, constraint mapping, reconstruction, and validation.

**When to use:**
- High-stakes decisions where conventional thinking may be wrong
- R&D strategy decisions about "impossible" problems
- Evaluating whether a field's foundational assumptions are sound
- Any problem where billions of dollars or significant human impact depends on getting it right

### Assumption Audit

Phase 2 only: Deep dive into assumptions of a specific claim, paper, strategy, or business plan. Produces detailed assumption inventory without reconstruction.

**When to use:**
- Due diligence on a scientific claim or business plan
- Evaluating a competitor's strategy for hidden assumptions
- Reviewing a research proposal for untested assumptions
- Pre-mortem analysis: "what are we assuming that might be wrong?"

### Constraint Reclassification

Phases 3 and 4 only: Take a set of "known constraints" and rigorously reclassify them as hard, soft, or imagined. Produces constraint space map without full reconstruction.

**When to use:**
- A team is stuck and needs to know which constraints are real
- Evaluating feasibility of an "impossible" project
- Identifying where engineering effort could unlock new possibilities
- Comparing two approaches by their actual (not perceived) constraint profiles

---

## Python Code Templates

### Assumption Breakdown Visualization

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_assumption_breakdown(assumptions, title="Assumption Inventory Breakdown"):
    """
    Visualize the breakdown of assumptions by type.

    Parameters:
    - assumptions: list of dicts with keys 'name', 'type' (one of:
      'fundamental', 'empirical', 'convention', 'untested', 'analogy')
    """
    type_colors = {
        'fundamental': '#2c3e50',
        'empirical': '#3498db',
        'convention': '#f39c12',
        'untested': '#e74c3c',
        'analogy': '#9b59b6'
    }
    type_labels = {
        'fundamental': 'Fundamental Truth',
        'empirical': 'Empirical Observation',
        'convention': 'Convention/Tradition',
        'untested': 'Untested Assumption',
        'analogy': 'Analogy from Other Domain'
    }

    counts = {}
    for a in assumptions:
        t = a['type']
        counts[t] = counts.get(t, 0) + 1

    types = list(counts.keys())
    values = [counts[t] for t in types]
    colors = [type_colors[t] for t in types]
    labels = [type_labels[t] for t in types]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Pie chart
    wedges, texts, autotexts = ax1.pie(values, labels=labels, colors=colors,
                                         autopct='%1.0f%%', startangle=90)
    ax1.set_title('Assumption Types', fontweight='bold')

    # Bar chart with assumption names
    y_pos = range(len(assumptions))
    bar_colors = [type_colors[a['type']] for a in assumptions]
    ax2.barh(y_pos, [1]*len(assumptions), color=bar_colors, edgecolor='white')
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([a['name'][:40] for a in assumptions], fontsize=8)
    ax2.set_title('Individual Assumptions by Type', fontweight='bold')
    ax2.invert_yaxis()
    ax2.set_xticks([])

    plt.tight_layout()
    plt.savefig('assumption_breakdown.png', dpi=150, bbox_inches='tight')
    plt.show()
```

### Reasoning Chain Diagram

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def plot_reasoning_chain(chain, title="First-Principles Reasoning Chain"):
    """
    Visualize a reasoning chain from conclusion back to fundamental truth.

    Parameters:
    - chain: list of dicts with keys 'statement', 'type' (one of:
      'conclusion', 'because', 'fundamental', 'evidence')
      Listed from conclusion (top) to fundamental truth (bottom).
    """
    fig, ax = plt.subplots(figsize=(10, 2 + len(chain) * 1.5))
    ax.axis('off')

    type_colors = {
        'conclusion': '#2ecc71',
        'because': '#3498db',
        'fundamental': '#e74c3c',
        'evidence': '#9b59b6'
    }
    type_prefixes = {
        'conclusion': 'CONCLUSION',
        'because': 'BECAUSE',
        'fundamental': 'FUNDAMENTAL TRUTH',
        'evidence': 'EVIDENCE'
    }

    y_start = len(chain)
    for i, link in enumerate(chain):
        y = y_start - i
        color = type_colors[link['type']]
        prefix = type_prefixes[link['type']]

        box = mpatches.FancyBboxPatch((1, y - 0.35), 8, 0.7,
                                        boxstyle="round,pad=0.2",
                                        facecolor=color, alpha=0.2,
                                        edgecolor=color, linewidth=2)
        ax.add_patch(box)
        ax.text(5, y, f"{prefix}: {link['statement']}", ha='center', va='center',
                fontsize=9, fontweight='bold' if link['type'] in ('conclusion', 'fundamental') else 'normal',
                wrap=True)

        if i < len(chain) - 1:
            ax.annotate('', xy=(5, y - 0.4), xytext=(5, y - 0.6),
                        arrowprops=dict(arrowstyle='->', color='#7f8c8d', lw=2))

    ax.set_xlim(0, 10)
    ax.set_ylim(0, y_start + 1)
    ax.set_title(title, fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig('reasoning_chain.png', dpi=150, bbox_inches='tight')
    plt.show()
```

---

## Multi-Agent Workflow Examples

### Example 1: "Is this target really undruggable?"

1. **First Principles (this skill)** -> Strip assumptions about "undruggability." Identify: is the constraint thermodynamic (hard), structural (soft), or conventional (imagined)? Map the actual constraint space for targeting this protein.
2. **Drug Target Validator** -> Assess tractability scores, existing chemical matter, structural data to ground the constraint classification.
3. **Hypothesis Generation** -> Generate 3-5 hypotheses for novel drugging approaches revealed by first-principles reconstruction.
4. **What-If Oracle** -> Model scenarios for each novel approach: probability of success, timeline, cost.

### Example 2: "Why do 90% of drugs fail in clinical trials?"

1. **First Principles (this skill)** -> Decompose the drug development process to fundamentals. Which failure modes are inherent (hard constraints) vs. caused by convention (imagined constraints)? Strip assumptions about trial design, patient selection, endpoint choice, and regulatory requirements.
2. **Clinical Trial Protocol Designer** -> Evaluate whether unconventional trial designs could address the imagined constraints identified.
3. **FDA Consultant** -> Clarify which regulatory requirements are actually legally mandated vs. conventional practice.
4. **Adversarial Collaboration** -> Debate: "The 90% failure rate is inherent to biology" vs. "The 90% failure rate is caused by flawed conventional methodology."

### Example 3: "Can we deliver large biologics across the blood-brain barrier?"

1. **First Principles (this skill)** -> Identify the actual physical and biological constraints of the BBB. Strip away "it's impossible" assumption. Map: tight junctions (hard but engineerable), efflux transporters (soft), molecular weight limits (convention based on small molecules, may not apply to biologics with receptor-mediated transcytosis).
2. **Literature Deep Research** -> Find evidence for unconventional BBB crossing approaches.
3. **Formulation Science** -> Evaluate delivery technologies that exploit soft constraints identified in Phase 4.
4. **Drug Research** -> Review existing biologics that DO cross the BBB, studying their mechanisms.

### Example 4: "Should we rethink how we measure clinical efficacy in Alzheimer's disease?"

1. **First Principles (this skill)** -> Strip assumptions about ADAS-Cog and CDR-SB endpoints. Are these measuring what actually matters? What does "efficacy" mean from fundamental biological and patient-centered principles? Identify: convention (historical endpoints), empirical (correlation with outcomes), fundamental (what cognition actually is at the neural level).
2. **Clinical Trial Analyst** -> Review historical Alzheimer's trials to identify patterns in endpoint sensitivity and failure modes.
3. **Hypothesis Generation** -> Generate hypotheses for better endpoints based on first-principles understanding.
4. **Peer Review** -> Evaluate the evidence base for current vs. proposed novel endpoints.

### Example 5: "Why is gene therapy so expensive to manufacture?"

1. **First Principles (this skill)** -> Break down the cost structure to fundamentals. Raw materials cost vs. selling price (the "idiot index"). Which cost drivers are physical constraints (viral vector biology), which are engineering challenges (scale-up), and which are convention (batch sizes, testing paradigms, facility design inherited from monoclonal antibody manufacturing)?
2. **Formulation Science** -> Evaluate manufacturing approaches that address soft constraints.
3. **What-If Oracle** -> Model cost scenarios under different manufacturing paradigms.
4. **Competitive Intelligence** -> Map how competitors are approaching the cost problem.

---

## Report Template

```
# First Principles Analysis: [PROBLEM]
Generated: [DATE]
Analysis Mode: [Quick / Deep / Assumption Audit / Constraint Reclassification]

## 1. Executive Summary
[2-3 paragraphs: problem, key findings from assumption stripping, novel possibilities revealed]

## 2. Problem Statement
### Core Question
[One precise sentence]

### Conventional Understanding
[What "everyone knows" about this problem]

### Conventional Constraints
[What limitations are typically assumed]

## 3. Assumption Inventory

| # | Assumption | Type | Fragile? | Evidence | Source |
|---|-----------|------|----------|----------|--------|
| A1 | | | | | |
| A2 | | | | | |
...

### Broken Analogies
[For each analogy identified: where it holds, where it breaks, what to use instead]

## 4. Foundational Truths
### Physical/Chemical Laws
[Laws that constrain the problem]

### Biological Principles
[Biological fundamentals relevant to the problem]

### Mathematical Constraints
[Mathematical limits and requirements]

### Economic/Regulatory Realities
[Real economic and regulatory constraints]

## 5. Constraint Space Map

### Hard Constraints (immovable)
[Constraints that cannot be violated]

### Soft Constraints (engineering challenges)
[Constraints that can be overcome with effort]

### Imagined Constraints (convention, not law)
[Constraints that are not actually constraints]

### Constraint Space Visualization
[Include Python-generated constraint space plot]

## 6. First-Principles Reconstruction

### What's Actually Possible
[Solutions visible only from first-principles view]

### Novel Approaches Revealed
| # | Approach | Why Convention Missed It | Feasibility Gap | Actionability |
|---|---------|------------------------|-----------------|---------------|

### Reasoning Chains
[Full traceability for each novel conclusion]

## 7. Validation

### Constraint Violation Check
[Does any novel approach violate a real constraint?]

### Implementation Gap Assessment
[Technology, knowledge, resource, regulatory, organizational gaps]

### Is Convention Actually Good Enough?
[Honest assessment of whether first-principles view adds value]

## 8. Conclusion and Recommendations
[Key findings, actionable next steps, areas for further investigation]

## 9. Methodology Notes
[Which phases were performed, evidence quality, limitations of analysis]
```

---

## Evidence Grading for Foundational Claims

| Tier | Label | Criteria | First-Principles Application |
|------|-------|----------|------------------------------|
| **T1** | Law / Proof | Mathematical proof, replicated physical law measurement | Hard constraint classification |
| **T2** | Strong empirical | Replicated experiments, meta-analyses, systematic reviews | Empirical observation classification |
| **T3** | Moderate empirical | Single studies, conference abstracts, preprints | Soft constraint, requires verification |
| **T4** | Weak / Inferred | Expert opinion, analogy, press releases, unverified claims | Convention or untested assumption |

**Rules:** Every foundational truth claim must cite its evidence tier. Hard constraints require T1 evidence. Soft constraints should have T2+ support. Anything supported only by T4 evidence is classified as untested assumption until verified.

---

## Completeness Checklist

- [ ] Problem stated precisely with clear scope and success criteria
- [ ] Conventional understanding documented ("what everyone knows")
- [ ] Complete assumption inventory with explicit categorization (fundamental/empirical/convention/untested/analogy)
- [ ] All analogies identified, tested at mechanistic level, and broken where appropriate
- [ ] Foundational truths catalogued across all relevant domains (physics, chemistry, biology, math, economics, regulatory)
- [ ] Every constraint classified as hard, soft, or imagined with evidence
- [ ] Constraint space visualized (perceived difficulty vs. actual difficulty)
- [ ] Reconstruction performed starting ONLY from foundational truths within hard constraints
- [ ] Novel approaches identified with reasoning traceability chains back to fundamental laws
- [ ] Each reasoning chain validated: no "because everyone knows" or "because it's always been this way" steps
- [ ] Validation performed: no novel approach violates a genuine hard constraint
- [ ] Implementation gap assessed across technology, knowledge, resources, regulatory, and organizational dimensions
- [ ] Honest assessment of whether convention is actually good enough
- [ ] Evidence grading (T1-T4) applied to all foundational claims
- [ ] MCP tools used to verify assumptions and find precedent for unconventional approaches
- [ ] Report file created with all sections populated (no remaining placeholders)
- [ ] Constraint space and/or possibility frontier visualization code included
