---
name: systems-thinking
description: Analyze phenomena as interconnected systems using systems dynamics, complexity science, and Donella Meadows' leverage points framework. Maps stocks, flows, feedback loops, emergent properties, and identifies high-leverage intervention points. Use when asked to understand complex systems, map feedback loops, find leverage points, analyze systemic behavior, understand emergent properties, design system interventions, model dynamic behavior, or analyze why a system resists change. Applies to drug resistance, disease pathways, clinical trials, healthcare delivery, drug development pipelines, organizational dynamics, and any domain where interconnected components produce emergent behavior.
---

# Systems Thinking

Analyze phenomena as interconnected systems rather than isolated components. This skill applies systems dynamics, complexity science, and Donella Meadows' leverage points framework to map feedback structures, identify emergent properties, and find high-leverage intervention points where small changes produce large systemic effects.

Distinct from **first-principles** (which decomposes problems to fundamental truths and rebuilds), **what-if-oracle** (which explores branching future scenarios), and **deep-research** (which investigates questions iteratively through literature). Systems thinking focuses on the *structure* of interconnections that produces observed behavior -- why systems behave the way they do and where to intervene effectively.

## Report-First Workflow

1. **Create report file immediately**: `[system]_systems_analysis_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Decomposing a problem to fundamental axioms and rebuilding -> use `first-principles`
- Exploring branching future scenarios with probability-weighted outcomes -> use `what-if-oracle`
- Generating and ranking competing hypotheses for a phenomenon -> use `hypothesis-generation`
- Evaluating the rigor and quality of a specific study -> use `scientific-critical-thinking`
- Iterative literature investigation with search refinement -> use `deep-research`
- Inferring the best explanation from incomplete data -> use `abductive-reasoning`
- Clinical trial protocol design or statistical powering -> use `clinical-trial-protocol-designer`
- Target druggability and validation scoring -> use `drug-target-validator`

## Cross-Skill Routing

- Need to decompose a subsystem to fundamentals -> `first-principles`
- Need to explore future scenarios for a system -> `what-if-oracle`
- Need to generate hypotheses about a feedback mechanism -> `hypothesis-generation`
- Need to evaluate evidence quality for a causal claim -> `scientific-critical-thinking`
- Need to investigate a system component through literature -> `deep-research`
- Need to infer which causal structure best explains observations -> `abductive-reasoning`
- Need disease pathway molecular details -> `disease-research`
- Need drug target validation data -> `drug-target-validator`
- Need pathway interaction data -> `reactome-pathways` or `kegg-database`
- Need protein-protein interaction networks -> `protein-interactions` or `stringdb-interactions`

---

## Available MCP Tools

### `mcp__pubmed__pubmed_data` (Evidence for System Components)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search PubMed by keywords, MeSH terms, author, journal | `query`, `num_results` |
| `fetch_details` | Full article metadata: abstract, authors, journal, DOI, MeSH | `pmid` |

**Systems-specific uses:** Find evidence for feedback loop existence, validate causal relationships between system components, identify published system dynamics models, find evidence for delay magnitudes and stock sizes.

### `mcp__ctgov__ctgov_data` (Clinical System Dynamics)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search clinical trials by condition, intervention, phase, status | `condition`, `intervention`, `phase`, `status`, `pageSize` |
| `get` | Full trial details by NCT ID | `nctId` |
| `stats` | Trial statistics and counts | `condition`, `intervention` |

**Systems-specific uses:** Map clinical development system flows (trial starts, completions, failures), identify feedback loops in trial design (adaptive trials), quantify system throughput and bottlenecks.

### `mcp__opentargets__opentargets_data` (Biological System Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId`, `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability) | `id` |
| `get_disease_details` | Disease info including associated targets and drugs | `id` |

**Systems-specific uses:** Map biological system components (targets, pathways, disease associations), identify feedback regulation between targets, quantify evidence strength for causal links in biological systems.

### `mcp__reactome__reactome_data` (Pathway Feedback Structures)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_pathway` | Get pathway details | `id` |
| `get_pathway_participants` | Entities in a pathway | `id` |
| `search` | Search pathways by keyword | `query` |

**Systems-specific uses:** Map signaling cascade feedback structures, identify reinforcing and balancing loops in biological pathways, find pathway crosstalk (inter-system connections).

### `mcp__kegg__kegg_data` (Metabolic System Maps)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_pathway` | Get KEGG pathway details | `pathway_id` |
| `search_pathway` | Search pathways by keyword | `query` |
| `get_compound` | Get compound details | `compound_id` |

**Systems-specific uses:** Map metabolic stocks and flows, identify enzyme-regulated flow rates, find metabolic feedback inhibition loops.

### `mcp__stringdb__stringdb_data` (Interaction Network Structure)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_interactions` | Get protein-protein interaction network | `identifiers`, `species`, `required_score` |
| `get_network_image` | Network visualization | `identifiers`, `species` |
| `get_enrichment` | Functional enrichment of network | `identifiers`, `species` |

**Systems-specific uses:** Map system component interactions, identify network hubs (high-leverage nodes), find modular subsystem boundaries, assess network robustness and redundancy.

---

## Core Framework: 7-Phase Systems Analysis

### Phase 1: System Boundary Definition

What is in the system? What is outside? Boundary choices fundamentally shape analysis.

**Steps:**
1. State the phenomenon or behavior to be explained
2. Define the system of interest (what is included)
3. Identify boundary choices and what they exclude
4. Note boundary critique: what important things are left out?
5. Identify cross-boundary flows (inputs and outputs)

**Boundary Definition Template:**

```
SYSTEM: [Name]
PURPOSE OF ANALYSIS: [What behavior are we trying to explain or change?]

INCLUDED IN SYSTEM:
- [Component 1]: [Why included]
- [Component 2]: [Why included]
- ...

EXCLUDED FROM SYSTEM (boundary choices):
- [External factor 1]: [Why excluded, what we lose by excluding]
- [External factor 2]: [Why excluded, what we lose by excluding]

CROSS-BOUNDARY FLOWS:
- Inputs: [What enters the system from outside]
- Outputs: [What leaves the system]

BOUNDARY CRITIQUE:
- [What important dynamics are we missing by drawing the boundary here?]
- [Would shifting the boundary change our conclusions?]
```

**MCP tool usage:**
```
# Find published system boundaries for comparison
mcp__pubmed__pubmed_data(method: "search", query: "systems dynamics model [SYSTEM TOPIC]", num_results: 10)

# Map biological system boundaries using pathway data
mcp__reactome__reactome_data(method: "search", query: "[PATHWAY]")
```

---

### Phase 2: Component Mapping

Identify all system elements: stocks, flows, variables, and external inputs/outputs.

**Stocks** (accumulations) -- things that build up or deplete:
- Physical: drug concentration, tumor burden, immune cells, inventory
- Informational: knowledge, data, clinical evidence
- Organizational: workforce skill, institutional trust, regulatory goodwill

**Flows** (rates) -- things that move between stocks:
- Inflows: production, recruitment, synthesis, learning
- Outflows: degradation, attrition, clearance, forgetting
- Transformation flows: conversion from one stock to another

**Variables** (auxiliaries) -- things that influence flow rates:
- Parameters: constants that set flow rates (e.g., clearance rate, mutation rate)
- Information variables: signals that modulate flows (e.g., biomarker levels, market signals)

**Component Mapping Template:**

```
STOCKS:
| Stock | Units | Current Level | Range | Residence Time |
|-------|-------|---------------|-------|----------------|
| [Name] | [units] | [level] | [min-max] | [time] |

FLOWS:
| Flow | From | To | Rate | Regulated By |
|------|------|----|------|-------------|
| [Name] | [stock/external] | [stock/external] | [units/time] | [variables] |

VARIABLES:
| Variable | Type | Influences | Current Value | Range |
|----------|------|-----------|---------------|-------|
| [Name] | [parameter/info] | [which flows] | [value] | [range] |
```

**MCP tool usage:**
```
# Map biological system components
mcp__opentargets__opentargets_data(method: "get_target_details", id: "[TARGET_ID]")
mcp__reactome__reactome_data(method: "get_pathway_participants", id: "[PATHWAY_ID]")

# Map interaction structure
mcp__stringdb__stringdb_data(method: "get_interactions", identifiers: "[GENE1,GENE2,GENE3]", species: 9606, required_score: 700)
```

---

### Phase 3: Causal Loop Diagramming

Map the feedback structure that drives system behavior.

**Reinforcing Loops (R)** -- positive feedback, exponential growth or collapse:
- Each variable in the loop amplifies the next
- Produces exponential growth when running forward, exponential collapse when reversed
- Examples: viral replication, drug resistance selection, market share snowball, publication bias

**Balancing Loops (B)** -- negative feedback, goal-seeking behavior:
- The loop acts to bring a stock toward a target or equilibrium
- Produces goal-seeking, oscillation around target, or stability
- Examples: homeostasis, dose adjustment, market correction, immune regulation

**Delays** -- where information or material takes time to propagate:
- Material delays: drug absorption, trial enrollment, manufacturing lead time
- Information delays: data readout lag, regulatory review time, publication delay
- Perception delays: time to recognize a trend, acknowledge failure, detect signal

**Loop Dominance** -- which loops currently control system behavior:
- At any given time, one or a few loops dominate behavior
- Dominance can shift as stocks change (e.g., exponential growth eventually hits balancing loop)
- Identifying dominance shifts is key to understanding system transitions

**Causal Loop Template:**

```
REINFORCING LOOPS:
R1: [Name]
  [Variable A] --(+)--> [Variable B] --(+)--> [Variable C] --(+)--> [Variable A]
  Behavior: [What this loop produces when dominant]
  Current strength: [Strong/Moderate/Weak]
  Evidence: [Source]

BALANCING LOOPS:
B1: [Name]
  [Variable A] --(+)--> [Variable B] --(-)--> [Variable C] --(+)--> [Variable A]
  Goal/Target: [What this loop seeks]
  Current strength: [Strong/Moderate/Weak]
  Evidence: [Source]

DELAYS:
D1: [Name]
  Location: [Between which variables]
  Duration: [Time]
  Type: [Material/Information/Perception]
  Effect: [How delay changes behavior -- oscillation, overshoot, etc.]

LOOP DOMINANCE:
Currently dominant: [Loop ID] because [reason]
Expected dominance shift: [When and why dominance will shift]
```

---

### Phase 4: Emergent Property Analysis

What does the whole system do that individual parts do not?

**Common emergent behaviors:**
- **Resistance to change**: system pushes back against interventions (policy resistance)
- **Resilience**: system absorbs shocks and returns to previous behavior
- **Oscillation**: system cycles around an equilibrium due to delays
- **Overshoot and collapse**: growth beyond carrying capacity followed by crash
- **Lock-in**: reinforcing loops make system path-dependent, resistant to alternatives
- **Drift to low performance**: gradual erosion of standards when goals adjust to reality
- **Tragedy of the commons**: individually rational actions deplete shared resource
- **Escalation**: competing reinforcing loops drive arms-race dynamics
- **Success to the successful**: early advantage compounds, creating inequality

**Emergent Property Template:**

```
EMERGENT BEHAVIOR: [Name]
Description: [What the system does]
Producing loops: [Which R/B loops and delays create this behavior]
Tipping points: [Conditions that would shift behavior to a different mode]
Phase transitions: [What triggers a qualitative change in system behavior]

Evidence:
- [Observation 1 that confirms this emergent behavior]
- [Observation 2]
```

**MCP tool usage:**
```
# Find evidence of emergent behavior in biological systems
mcp__pubmed__pubmed_data(method: "search", query: "drug resistance feedback loop [DISEASE]", num_results: 10)
mcp__pubmed__pubmed_data(method: "search", query: "systems dynamics emergent [PHENOMENON]", num_results: 10)
```

---

### Phase 5: Leverage Point Identification

Where can small changes produce large systemic effects? Apply Donella Meadows' 12 leverage points, ranked from least to most powerful.

**The 12 Leverage Points (ascending power):**

| Rank | Leverage Point | Description | Difficulty | Impact |
|------|---------------|-------------|-----------|--------|
| 12 | Constants, parameters, numbers | Adjusting quantities (doses, budgets, thresholds) | Low | Low |
| 11 | Buffer sizes | Size of stabilizing stocks relative to flows | Low | Low-Med |
| 10 | Structure of material stocks and flows | Physical infrastructure, supply chains | Medium | Medium |
| 9 | Delays relative to rate of change | Shortening or lengthening feedback delays | Medium | Medium |
| 8 | Strength of negative feedback loops | Increasing regulation, monitoring, correction | Medium | Med-High |
| 7 | Gain of positive feedback loops | Reducing or redirecting amplification | Medium | Med-High |
| 6 | Structure of information flows | Who has access to what information, when | Med-High | High |
| 5 | Rules of the system | Incentives, constraints, penalties, permissions | Med-High | High |
| 4 | Power to add/change/evolve system structure | Self-organization, adaptation capacity | High | High |
| 3 | Goals of the system | What the system is trying to achieve | High | Very High |
| 2 | Mindset or paradigm | Shared assumptions from which the system arises | Very High | Very High |
| 1 | Power to transcend paradigms | Ability to operate from multiple paradigms | Very High | Highest |

**Leverage Point Assessment Template:**

```
LEVERAGE POINT: [Rank] - [Name]
Location in system: [Which stock, flow, loop, or structure]
Current state: [How it currently operates]
Proposed intervention: [What change to make]
Expected primary effect: [Direct result]
Expected secondary effects: [Ripple through feedback loops]
Unintended consequence risk: [What could go wrong]
Feasibility: [High/Medium/Low]
Time to effect: [Immediate/Months/Years]
Reversibility: [High/Medium/Low]
```

---

### Phase 6: Intervention Design

Design interventions at identified leverage points, anticipating system responses.

**Intervention Design Principles:**
1. **Intervene at multiple leverage points simultaneously** -- single-point interventions are often absorbed by the system
2. **Anticipate compensating feedback** -- the system will push back; design for it
3. **Monitor for unintended consequences** -- feedback loops produce surprises
4. **Design adaptive interventions** -- build in monitoring and adjustment capacity
5. **Respect delays** -- effects take time; premature abandonment is a common failure mode

**Intervention Template:**

```
INTERVENTION: [Name]
Target leverage point(s): [Rank(s)]
Mechanism: [How the intervention changes the system]

EXPECTED SYSTEM RESPONSE:
- Primary effect (0-3 months): [Direct result]
- Compensating feedback (3-12 months): [How system pushes back]
- New equilibrium (12+ months): [Where system settles]

MONITORING PLAN:
| Indicator | Measure | Frequency | Threshold for Adjustment |
|-----------|---------|-----------|------------------------|
| [Indicator] | [How measured] | [How often] | [When to modify intervention] |

UNINTENDED CONSEQUENCE ASSESSMENT:
| Possible Consequence | Mechanism (which loop) | Severity | Mitigation |
|---------------------|----------------------|----------|------------|
| [Consequence] | [Feedback loop] | [H/M/L] | [Response] |

ADAPTIVE STRATEGY:
- If [indicator] exceeds [threshold]: [adjustment]
- If [unexpected behavior] observed: [response]
- Decision point at [time]: [evaluate and adjust or continue]
```

---

### Phase 7: Dynamic Hypothesis

How will the system behave over time? What feedback structure produces the observed behavior pattern?

**Reference Modes** -- observed behavior patterns to explain:
- Exponential growth (reinforcing loop dominant)
- Goal-seeking (balancing loop dominant)
- Oscillation (balancing loop with delay)
- S-shaped growth (reinforcing then balancing)
- Overshoot and collapse (reinforcing, delayed balancing, stock depletion)
- Growth with overshoot and oscillation (combination)

**Dynamic Hypothesis Template:**

```
REFERENCE MODE: [Describe the behavior pattern observed or expected]
  - Data source: [Where this pattern is documented]
  - Time horizon: [Over what period]

DYNAMIC HYPOTHESIS:
  - Dominant loop(s): [Which R/B loops drive this pattern]
  - Mechanism: [Step-by-step explanation of how loops produce the pattern]
  - Dominance shift: [When/why loop dominance changes, causing behavior transition]

PREDICTION:
  - Without intervention: [Expected trajectory over next N years]
  - With intervention at LP[X]: [How trajectory changes]
  - With intervention at LP[Y]: [Alternative trajectory]

VALIDATION:
  - Historical data consistent: [Yes/No, with evidence]
  - Model boundary adequate: [Yes/No, what might be missing]
  - Key uncertainties: [What could make this hypothesis wrong]
```

---

## Python Visualization Templates

### Causal Loop Diagram

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

def plot_causal_loop_diagram(variables, links, title="Causal Loop Diagram"):
    """
    variables: list of dicts with 'name', 'x', 'y'
    links: list of dicts with 'from', 'to', 'polarity' (+/-), 'loop' (R1/B1), 'delay' (bool)
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal')
    ax.axis('off')

    # Draw variables as boxes
    var_positions = {}
    for var in variables:
        var_positions[var['name']] = (var['x'], var['y'])
        bbox = dict(boxstyle='round,pad=0.4', facecolor='#ecf0f1', edgecolor='#2c3e50', linewidth=2)
        ax.text(var['x'], var['y'], var['name'], ha='center', va='center',
                fontsize=10, fontweight='bold', bbox=bbox)

    # Draw links with polarity
    for link in links:
        x_from, y_from = var_positions[link['from']]
        x_to, y_to = var_positions[link['to']]
        color = '#27ae60' if link['polarity'] == '+' else '#e74c3c'
        style = '--' if link.get('delay', False) else '-'

        ax.annotate('', xy=(x_to, y_to), xytext=(x_from, y_from),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2, linestyle=style,
                                   connectionstyle='arc3,rad=0.2'))

        mid_x = (x_from + x_to) / 2
        mid_y = (y_from + y_to) / 2
        ax.text(mid_x + 0.08, mid_y + 0.08, link['polarity'],
                fontsize=14, fontweight='bold', color=color)

        if link.get('delay', False):
            ax.text(mid_x - 0.08, mid_y - 0.12, '||', fontsize=12, color='#7f8c8d')

    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='#27ae60', label='Positive link (+)'),
        mpatches.Patch(facecolor='#e74c3c', label='Negative link (-)'),
        plt.Line2D([0], [0], color='gray', linestyle='--', label='Delay (||)'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)

    plt.tight_layout()
    plt.savefig('causal_loop_diagram.png', dpi=150, bbox_inches='tight')
    plt.show()

# Example usage:
# variables = [
#     {'name': 'Drug Pressure', 'x': 0, 'y': 1},
#     {'name': 'Resistant Population', 'x': 1, 'y': 0},
#     {'name': 'Treatment Efficacy', 'x': 0, 'y': -1},
#     {'name': 'Dose Escalation', 'x': -1, 'y': 0},
# ]
# links = [
#     {'from': 'Drug Pressure', 'to': 'Resistant Population', 'polarity': '+', 'delay': True},
#     {'from': 'Resistant Population', 'to': 'Treatment Efficacy', 'polarity': '-'},
#     {'from': 'Treatment Efficacy', 'to': 'Dose Escalation', 'polarity': '-'},
#     {'from': 'Dose Escalation', 'to': 'Drug Pressure', 'polarity': '+'},
# ]
# plot_causal_loop_diagram(variables, links, "Drug Resistance Feedback System")
```

### Stock-and-Flow Diagram

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def plot_stock_flow_diagram(stocks, flows, title="Stock-and-Flow Diagram"):
    """
    stocks: list of dicts with 'name', 'x', 'y', 'level' (0-1 fill)
    flows: list of dicts with 'name', 'from_x', 'from_y', 'to_x', 'to_y', 'rate'
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(-1, 11)
    ax.set_ylim(-1, 7)
    ax.axis('off')

    # Draw stocks as filled rectangles
    for stock in stocks:
        rect = mpatches.FancyBboxPatch((stock['x'] - 0.8, stock['y'] - 0.5), 1.6, 1.0,
                                        boxstyle="square,pad=0", facecolor='#d5e8d4',
                                        edgecolor='#2c3e50', linewidth=2)
        ax.add_patch(rect)

        # Fill level
        fill_height = stock.get('level', 0.5) * 1.0
        fill_rect = mpatches.FancyBboxPatch((stock['x'] - 0.8, stock['y'] - 0.5),
                                             1.6, fill_height, boxstyle="square,pad=0",
                                             facecolor='#82b366', edgecolor='none', alpha=0.6)
        ax.add_patch(fill_rect)

        ax.text(stock['x'], stock['y'], stock['name'], ha='center', va='center',
                fontsize=10, fontweight='bold')

    # Draw flows as arrows with valve symbol
    for flow in flows:
        ax.annotate('', xy=(flow['to_x'], flow['to_y']),
                    xytext=(flow['from_x'], flow['from_y']),
                    arrowprops=dict(arrowstyle='->', color='#3498db', lw=3))

        mid_x = (flow['from_x'] + flow['to_x']) / 2
        mid_y = (flow['from_y'] + flow['to_y']) / 2

        # Valve symbol (bowtie)
        valve = plt.Polygon([[mid_x - 0.15, mid_y + 0.15], [mid_x, mid_y],
                              [mid_x - 0.15, mid_y - 0.15], [mid_x + 0.15, mid_y + 0.15],
                              [mid_x, mid_y], [mid_x + 0.15, mid_y - 0.15]],
                             closed=True, facecolor='#3498db', edgecolor='#2c3e50')
        ax.add_patch(valve)

        ax.text(mid_x, mid_y + 0.3, f"{flow['name']}\n({flow['rate']})",
                ha='center', va='bottom', fontsize=8, style='italic')

    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('stock_flow_diagram.png', dpi=150, bbox_inches='tight')
    plt.show()
```

### Behavior-Over-Time Graph

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_behavior_over_time(time_points, variables, reference_modes=None,
                            intervention_point=None, title="Behavior Over Time"):
    """
    time_points: array of time values
    variables: list of dicts with 'name', 'values', 'color', 'style'
    reference_modes: list of dicts with 'name', 'values', 'color' (dashed overlays)
    intervention_point: float (x-value where intervention occurs)
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    for var in variables:
        ax.plot(time_points, var['values'], label=var['name'],
                color=var.get('color', '#3498db'),
                linestyle=var.get('style', '-'), linewidth=2)

    if reference_modes:
        for ref in reference_modes:
            ax.plot(time_points, ref['values'], label=f"{ref['name']} (reference)",
                    color=ref.get('color', '#95a5a6'), linestyle=':', linewidth=1.5, alpha=0.7)

    if intervention_point is not None:
        ax.axvline(x=intervention_point, color='#e74c3c', linestyle='--', linewidth=1.5,
                   label='Intervention', alpha=0.8)
        ax.annotate('Intervention', xy=(intervention_point, ax.get_ylim()[1] * 0.9),
                    fontsize=9, color='#e74c3c', fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color='#e74c3c'))

    ax.set_xlabel('Time', fontsize=11)
    ax.set_ylabel('Level', fontsize=11)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('behavior_over_time.png', dpi=150, bbox_inches='tight')
    plt.show()

# Example: S-shaped growth with overshoot
# t = np.linspace(0, 20, 200)
# carrying_capacity = 100
# growth = carrying_capacity * 1.2 / (1 + np.exp(-0.5*(t-8))) * np.exp(-0.01*(t-15)**2 * (t>15))
# plot_behavior_over_time(t, [{'name': 'Population', 'values': growth, 'color': '#2ecc71'}],
#                         intervention_point=10, title="Overshoot and Oscillation")
```

### Leverage Point Heat Map

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_leverage_point_heatmap(leverage_points, title="Leverage Point Assessment"):
    """
    leverage_points: list of dicts with 'name', 'rank' (1-12), 'feasibility' (0-100),
                     'impact' (0-100), 'time_to_effect' (0-100, higher=faster)
    """
    fig, ax = plt.subplots(figsize=(12, max(6, len(leverage_points) * 0.7)))

    # Sort by rank (most powerful first)
    lps = sorted(leverage_points, key=lambda x: x['rank'])

    names = [f"LP{lp['rank']}: {lp['name']}" for lp in lps]
    feasibility = [lp['feasibility'] for lp in lps]
    impact = [lp['impact'] for lp in lps]
    time_effect = [lp['time_to_effect'] for lp in lps]

    data = np.array([feasibility, impact, time_effect]).T
    categories = ['Feasibility', 'Expected Impact', 'Speed of Effect']

    im = ax.imshow(data, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)

    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels(categories, fontsize=10, fontweight='bold')
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=9)

    # Add value annotations
    for i in range(len(names)):
        for j in range(len(categories)):
            text_color = 'white' if data[i, j] < 40 or data[i, j] > 80 else 'black'
            ax.text(j, i, f'{data[i, j]:.0f}', ha='center', va='center',
                    fontsize=10, fontweight='bold', color=text_color)

    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    plt.colorbar(im, ax=ax, label='Score (0-100)', shrink=0.8)
    plt.tight_layout()
    plt.savefig('leverage_point_heatmap.png', dpi=150, bbox_inches='tight')
    plt.show()
```

### System Archetype Diagram

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

def plot_system_archetype(archetype, title=None):
    """
    archetype: one of 'fixes_that_fail', 'shifting_burden', 'limits_to_growth',
               'tragedy_of_commons', 'escalation', 'success_to_successful',
               'eroding_goals', 'growth_and_underinvestment'
    """
    archetypes = {
        'limits_to_growth': {
            'title': 'Limits to Growth',
            'loops': [
                ('R', 'Growing Action -> Performance -> Growing Action', '#2ecc71'),
                ('B', 'Performance -> Limiting Condition -> Performance', '#e74c3c'),
            ],
            'narrative': 'Reinforcing growth hits a balancing constraint.\nEarly: R dominates (growth). Late: B dominates (plateau/decline).',
            'leverage': 'Address the limiting condition BEFORE growth stalls.',
        },
        'fixes_that_fail': {
            'title': 'Fixes That Fail',
            'loops': [
                ('B', 'Problem -> Fix -> Problem (quick relief)', '#3498db'),
                ('R', 'Fix -> Unintended Consequence -> Problem (delayed worsening)', '#e74c3c'),
            ],
            'narrative': 'Quick fix reduces symptom but creates delayed side effect\nthat worsens the original problem.',
            'leverage': 'Address root cause instead of symptom.',
        },
        'shifting_burden': {
            'title': 'Shifting the Burden',
            'loops': [
                ('B1', 'Problem -> Symptomatic Solution -> Problem', '#3498db'),
                ('B2', 'Problem -> Fundamental Solution -> Problem', '#2ecc71'),
                ('R', 'Symptomatic Solution -> Side Effect -> Fundamental Capacity (eroded)', '#e74c3c'),
            ],
            'narrative': 'Symptomatic solution is easier/faster, but erodes capacity\nfor fundamental solution over time.',
            'leverage': 'Strengthen fundamental solution; weaken dependence on symptomatic fix.',
        },
    }

    arch = archetypes.get(archetype, archetypes['limits_to_growth'])
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.axis('off')

    ax.text(0.5, 0.95, arch['title'] if not title else title,
            ha='center', va='top', fontsize=16, fontweight='bold', transform=ax.transAxes)

    y_pos = 0.80
    for loop_type, description, color in arch['loops']:
        ax.text(0.1, y_pos, f"[{loop_type}]", fontsize=12, fontweight='bold',
                color=color, transform=ax.transAxes)
        ax.text(0.18, y_pos, description, fontsize=10, transform=ax.transAxes)
        y_pos -= 0.08

    y_pos -= 0.05
    ax.text(0.1, y_pos, 'Narrative:', fontsize=11, fontweight='bold', transform=ax.transAxes)
    y_pos -= 0.03
    ax.text(0.1, y_pos, arch['narrative'], fontsize=10, transform=ax.transAxes,
            verticalalignment='top', style='italic')

    y_pos -= 0.12
    ax.text(0.1, y_pos, 'Leverage:', fontsize=11, fontweight='bold', transform=ax.transAxes)
    y_pos -= 0.05
    ax.text(0.1, y_pos, arch['leverage'], fontsize=10, transform=ax.transAxes,
            color='#27ae60', fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'archetype_{archetype}.png', dpi=150, bbox_inches='tight')
    plt.show()
```

---

## System Archetypes Quick Reference

Common recurring system structures. Recognizing these accelerates analysis.

| Archetype | Pattern | Leverage |
|-----------|---------|----------|
| **Limits to Growth** | Growth stalls as it hits constraint | Remove or raise the limiting condition early |
| **Fixes That Fail** | Quick fix worsens problem long-term | Address root cause, not symptom |
| **Shifting the Burden** | Symptomatic fix erodes fundamental capacity | Strengthen fundamental solution |
| **Tragedy of the Commons** | Individual rationality depletes shared resource | Regulate access or align incentives |
| **Escalation** | Competing parties ratchet up actions | Break the loop; negotiate ceiling |
| **Success to the Successful** | Early advantage compounds via reinforcing loop | Equalize starting conditions or cap advantage |
| **Eroding Goals** | Standards drift down to match poor performance | Anchor goals externally; resist adjustment |
| **Growth and Underinvestment** | Growth demands capacity that is not invested in | Invest in capacity ahead of demand |
| **Accidental Adversaries** | Partners inadvertently undermine each other | Improve information flows between partners |
| **Attractiveness Principle** | Resources flow to most attractive option, starving others | Portfolio balancing; protect seed investments |

---

## Domain-Specific Templates

### Template 1: Drug Resistance System

```
SYSTEM: Drug Resistance in [Disease/Pathogen]

STOCKS:
- Sensitive pathogen/cell population
- Resistant pathogen/cell population
- Drug concentration (plasma/tissue)
- Immune effector capacity
- Mutation reservoir (genetic diversity)

KEY FEEDBACK LOOPS:
R1 (Selection Pressure): Drug pressure -> kill sensitive -> resistant proportion increases -> treatment failure -> dose escalation -> more selection pressure
R2 (Resistance Amplification): Resistant cells -> proliferation -> larger resistant population -> more mutations -> broader resistance
B1 (Immune Clearance): Pathogen burden -> immune activation -> pathogen killing -> reduced burden
B2 (Drug Clearance): Drug administered -> plasma concentration -> clearance/metabolism -> reduced concentration
B3 (Toxicity Limit): Dose escalation -> toxicity -> dose reduction/discontinuation -> reduced drug pressure

CRITICAL DELAYS:
- Mutation emergence to clinical detection (weeks to months)
- Resistance testing turnaround (days to weeks)
- New drug development (years)

LEVERAGE POINTS:
- LP7: Reduce gain of R1 by combination therapy (multiple drugs prevent single-mutation escape)
- LP6: Improve resistance detection information flow (rapid genotyping)
- LP5: Change treatment rules (cycling, adaptive dosing)
- LP3: Redefine goal from eradication to sustainable control
```

### Template 2: Disease Pathway System

```
SYSTEM: [Disease] Signaling Pathway

STOCKS:
- Receptor activation level
- Downstream effector concentration
- Transcription factor activation
- Gene expression products
- Phenotypic outcome measures

KEY FEEDBACK LOOPS:
R1 (Autocrine signaling): Ligand -> receptor -> signal -> gene expression -> more ligand
R2 (Pathway amplification): Signal -> kinase cascade -> amplified signal
B1 (Negative regulation): Signal -> phosphatase activation -> signal dampening
B2 (Receptor downregulation): Sustained activation -> receptor internalization -> reduced sensitivity
B3 (Feedback inhibition): Downstream product -> inhibits upstream activator

CROSS-TALK:
- Pathway X feeds into this system at [node]
- This system feeds into Pathway Y at [node]
- Compensatory pathway Z activates when this pathway is inhibited

LEVERAGE POINTS:
- LP10: Block flow at rate-limiting enzyme (traditional drug target)
- LP8: Strengthen B1 negative feedback (allosteric activator of phosphatase)
- LP7: Reduce R1 autocrine gain (antibody blocks ligand)
- LP6: Biomarker-guided therapy (measure pathway activation, adjust treatment)
```

### Template 3: Clinical Trial System

```
SYSTEM: Clinical Trial [Phase X] for [Drug] in [Indication]

STOCKS:
- Eligible patient pool
- Screened patients
- Enrolled patients
- Active participants
- Completed participants
- Accumulated data (efficacy + safety)

KEY FEEDBACK LOOPS:
R1 (Momentum): Enrollment -> investigator engagement -> referrals -> more enrollment
R2 (Evidence): Data -> interim results -> investigator confidence -> enrollment enthusiasm
B1 (Pool depletion): Enrollment -> smaller eligible pool -> harder recruitment -> slower enrollment
B2 (Dropout): Treatment burden -> adverse events -> dropout -> data loss -> need more enrollment
B3 (Competition): Competitor trials -> patient diversion -> recruitment difficulty

CRITICAL DELAYS:
- Protocol amendment approval (weeks to months)
- Site activation lag (months)
- Data cleaning and database lock (months)
- Regulatory review (6-12 months)

LEVERAGE POINTS:
- LP9: Reduce site activation delay (master protocols, platform trials)
- LP8: Strengthen B2 management (patient support, telemedicine visits)
- LP6: Real-time data dashboards for enrollment and safety signals
- LP5: Adaptive design rules (sample size re-estimation, futility boundaries)
```

### Template 4: Healthcare Delivery System

```
SYSTEM: Healthcare Delivery for [Condition] in [Setting]

STOCKS:
- Undiagnosed patients
- Diagnosed patients waiting for treatment
- Patients on treatment
- Healthcare workforce capacity
- Financial resources (payer budgets)

KEY FEEDBACK LOOPS:
R1 (Disease burden): Untreated disease -> complications -> more healthcare demand -> resource strain -> more untreated disease
R2 (Innovation cost): New treatments -> higher per-patient cost -> budget pressure -> access restriction -> unmet need -> demand for innovation
B1 (Treatment effect): Treatment -> improved outcomes -> reduced downstream demand
B2 (Workforce adjustment): Demand -> training programs -> more providers (long delay)
B3 (Cost containment): Spending -> payer intervention -> utilization management -> reduced access

THE IRON TRIANGLE:
- Access, Quality, Cost: improving two degrades the third
- System goal determines which two to optimize

LEVERAGE POINTS:
- LP6: Information flows (outcomes data to payers, wait times to patients)
- LP5: Rules (reimbursement policies, formulary decisions, treatment guidelines)
- LP3: System goal (population health vs. individual treatment vs. cost containment)
```

### Template 5: Drug Development Pipeline

```
SYSTEM: Drug Development Pipeline for [Organization/Therapeutic Area]

STOCKS:
- Discovery-stage compounds
- Preclinical candidates
- IND-ready compounds
- Phase 1/2/3 assets
- Approved products (revenue-generating)
- Cash/investment capital

KEY FEEDBACK LOOPS:
R1 (Revenue reinvestment): Approved drugs -> revenue -> R&D investment -> more discovery -> more approved drugs
R2 (Reputation): Successful programs -> talent attraction -> better science -> more success
B1 (Attrition): Pipeline advancement -> failure rate -> fewer late-stage assets -> revenue gap
B2 (Capital constraint): R&D spending -> cash depletion -> funding pressure -> program cuts
B3 (Regulatory tightening): Safety signals -> stricter requirements -> longer/costlier development

CRITICAL DELAYS:
- Discovery to IND: 3-5 years
- IND to approval: 6-10 years
- Patent filing to LOE: 20 years (but clock starts early)
- Revenue ramp to peak sales: 3-5 years post-launch

LEVERAGE POINTS:
- LP10: Pipeline flow rates (phase transition probabilities)
- LP9: Reduce development delays (adaptive designs, rolling submissions)
- LP7: Manage R1 reinvestment gain (disciplined portfolio management)
- LP5: Portfolio rules (kill criteria, resource allocation frameworks)
- LP3: Pipeline goal (blockbuster vs. niche, innovation vs. fast-follow)
```

---

## Analysis Modes

### Quick Systems Scan (Phases 1-3 only)

Rapid identification of system boundary, key stocks/flows, and dominant feedback loops. Complete in a single analysis session.

**When to use:**
- Initial orientation to an unfamiliar system
- Quick check for obvious feedback structures
- Preliminary assessment before committing to deep analysis
- Time-constrained advisory responses

### Full Systems Analysis (All 7 phases)

Complete analysis from boundary definition through dynamic hypothesis. Requires MCP tool data gathering.

**When to use:**
- Complex multi-stakeholder systems with non-obvious behavior
- Systems exhibiting policy resistance (interventions not working)
- High-stakes decisions requiring understanding of systemic dynamics
- Research or strategic planning with long time horizons

### Archetype Matching

Match observed system behavior to known system archetypes, then apply archetype-specific leverage strategies.

**When to use:**
- System behavior matches a recognizable pattern
- Need quick leverage point identification without full analysis
- Teaching or communication contexts requiring intuitive framing

### Comparative Systems Analysis

Analyze two or more systems in parallel, comparing their feedback structures, leverage points, and dynamic behavior.

**When to use:**
- Comparing drug resistance dynamics across pathogens
- Evaluating healthcare delivery models across settings
- Assessing pipeline strategies across therapeutic areas
- Learning from analogous systems in different domains

---

## Multi-Agent Workflow Examples

### Example 1: "Why does antibiotic resistance keep getting worse despite new drugs?"

1. **Systems Thinking (this skill)** -> Map drug resistance feedback system: selection pressure (R1), resistance amplification (R2), immune clearance (B1), development pipeline (B2). Identify that R1 dominance is sustained by prescribing practices and agricultural use. Leverage points: information flows (LP6 -- rapid diagnostics), rules (LP5 -- prescribing guidelines), and system goals (LP3 -- stewardship vs. eradication).
2. **Deep Research** -> Investigate specific resistance mechanisms and intervention evidence in literature
3. **Hypothesis Generation** -> Generate hypotheses about which leverage points would be most effective
4. **What-If Oracle** -> Model scenarios for different intervention strategies

### Example 2: "Why do clinical trials for Alzheimer's keep failing?"

1. **Systems Thinking (this skill)** -> Map the Alzheimer's trial system: patient heterogeneity stock, diagnostic accuracy flow, endpoint sensitivity, disease modification delay, competitive enrollment pressure. Identify eroding goals archetype (endpoints get easier as trials fail). Key delay: disease modification effect takes years but trials measure months.
2. **Disease Research** -> Detailed molecular pathway analysis of Alzheimer's disease
3. **Clinical Trial Analyst** -> Historical trial data and failure analysis
4. **Scientific Critical Thinking** -> Evaluate methodology of past trials

### Example 3: "How should we think about the drug pricing system in the US?"

1. **Systems Thinking (this skill)** -> Map healthcare delivery system: innovation incentive (R1), cost escalation (R2), access restriction (B1), generic/biosimilar entry (B2). Identify tragedy-of-the-commons and shifting-the-burden archetypes. Leverage points: information flows (LP6 -- price transparency), rules (LP5 -- negotiation authority), goals (LP3 -- innovation vs. access).
2. **Competitive Intelligence** -> Market landscape and pricing trends
3. **What-If Oracle** -> Model scenarios for policy changes (IRA impact, reference pricing, etc.)
4. **FDA Consultant** -> Regulatory pathway implications for pricing

### Example 4: "Why does our drug development pipeline keep producing Phase 2 failures?"

1. **Systems Thinking (this skill)** -> Map pipeline system: discovery throughput, preclinical validation rigor, Phase 1/2 transition criteria, portfolio pressure. Identify limits-to-growth (discovery output hits validation bottleneck) and success-to-successful (resources flow to advanced programs, starving early validation). Key leverage: strengthen negative feedback at preclinical gate (LP8), improve information flows from failures back to discovery (LP6).
2. **Drug Target Validator** -> Assess target validation quality for recent failures
3. **Hypothesis Generation** -> Generate hypotheses about root causes of Phase 2 attrition
4. **Statistical Modeling** -> Analyze Phase 2 failure patterns and predictive factors

### Example 5: "Map the feedback loops in the tumor microenvironment"

1. **Systems Thinking (this skill)** -> Map TME system: tumor cell proliferation (R1), immune surveillance (B1), immune evasion (R2), angiogenesis (R3), hypoxia response (B2). Identify which loops dominate at each tumor stage. Leverage: checkpoint inhibitors (strengthen B1 at LP8), anti-angiogenics (weaken R3 at LP7), combination therapy (address multiple loops).
2. **Systems Biology** -> Detailed molecular pathway modeling
3. **Immunotherapy Response Predictor** -> Predict which patients respond based on loop dominance
4. **Target Research** -> Identify druggable nodes in the TME feedback network

---

## Evidence Grading for Systems Analysis

| Tier | Label | Criteria | Systems Application |
|------|-------|----------|-------------------|
| **T1** | Definitive | Published system dynamics models, validated with data | Loop structure, stock/flow quantification |
| **T2** | Strong | Peer-reviewed mechanistic studies, clinical evidence | Causal link validation, delay estimation |
| **T3** | Emerging | Conference presentations, preprints, expert opinion | New feedback mechanisms, emerging dynamics |
| **T4** | Inferred | Theoretical reasoning, analogy from other systems | Hypothesized loops, archetype matching |

**Rules:** Always cite the tier with each causal link. Higher tiers for critical assumptions. Flag when an entire loop is supported only by T3/T4 evidence. Cross-validate system structure with multiple data sources.

---

## Report Template

```
# Systems Analysis: [System Name]
Generated: [DATE]
Analysis Mode: [Quick Scan / Full Analysis / Archetype Matching / Comparative]

## 1. Executive Summary
[2-3 paragraphs: what system, key feedback structures, dominant behavior,
 highest-leverage intervention points, and recommended actions]

## 2. System Boundary
- System of interest: [definition]
- Included components: [list with justification]
- Excluded factors: [list with impact of exclusion]
- Cross-boundary flows: [inputs and outputs]
- Boundary critique: [what we miss]

## 3. Component Map

### Stocks
| Stock | Units | Current Level | Residence Time |
|-------|-------|---------------|----------------|

### Flows
| Flow | From | To | Rate | Regulated By |
|------|------|----|------|-------------|

### Variables
| Variable | Type | Influences | Current Value |
|----------|------|-----------|---------------|

## 4. Causal Loop Diagram

### Reinforcing Loops
| Loop | Structure | Behavior | Strength | Evidence Tier |
|------|-----------|----------|----------|---------------|

### Balancing Loops
| Loop | Structure | Goal/Target | Strength | Evidence Tier |
|------|-----------|-------------|----------|---------------|

### Delays
| Delay | Location | Duration | Type | Effect |
|-------|----------|----------|------|--------|

### Loop Dominance
- Currently dominant: [loop] because [reason]
- Expected shift: [when and why]

## 5. Emergent Properties
| Property | Description | Producing Loops | Tipping Points |
|----------|-------------|----------------|----------------|

## 6. Leverage Points (ranked by expected impact)
| Rank | Leverage Point | Intervention | Feasibility | Impact | Time to Effect |
|------|---------------|-------------|-------------|--------|----------------|

## 7. Intervention Recommendations
### Intervention 1: [Name]
- Target: LP[X]
- Mechanism: [how it changes the system]
- Expected primary effect: [direct result]
- Expected system response: [compensating feedback]
- Monitoring plan: [indicators and thresholds]
- Unintended consequence risk: [assessment]

## 8. Dynamic Hypothesis & Predictions
- Reference mode: [observed behavior pattern]
- Hypothesis: [which loops produce this pattern]
- Without intervention: [predicted trajectory]
- With intervention: [predicted trajectory change]

## 9. Unintended Consequence Assessment
| Intervention | Possible Consequence | Mechanism | Severity | Mitigation |
|-------------|---------------------|-----------|----------|------------|

## 10. System Archetype Match
- Primary archetype: [name]
- Supporting evidence: [observations matching archetype pattern]
- Archetype-specific leverage: [recommended approach]
```

---

## Completeness Checklist

- [ ] System boundary explicitly defined with inclusion/exclusion justification
- [ ] Boundary critique performed: identified what important dynamics are excluded
- [ ] All major stocks identified with units, levels, and residence times
- [ ] All major flows identified with rates and regulatory variables
- [ ] At least 2 reinforcing loops identified and described
- [ ] At least 2 balancing loops identified and described
- [ ] Delays identified with duration estimates and behavioral effects
- [ ] Loop dominance assessed: which loops currently control behavior
- [ ] Emergent properties identified and traced to producing feedback structures
- [ ] Tipping points and phase transitions identified where applicable
- [ ] Leverage points ranked using Meadows' 12-point framework
- [ ] At least 3 leverage points assessed with feasibility, impact, and time estimates
- [ ] Interventions designed with expected system response and monitoring plans
- [ ] Unintended consequences assessed for each intervention using feedback loop analysis
- [ ] Dynamic hypothesis formulated linking feedback structure to observed behavior
- [ ] Predictions made for system trajectory with and without intervention
- [ ] System archetype matching attempted (at least one archetype considered)
- [ ] Evidence tiers (T1-T4) assigned to all causal links and assumptions
- [ ] MCP tools used to validate system components and causal relationships
- [ ] Report file created with all sections populated (no remaining placeholders)
- [ ] Visualization code provided for causal loop diagram and behavior-over-time graph
