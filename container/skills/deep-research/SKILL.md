---
name: deep-research
description: Iterative hypothesis-driven investigation with multi-cycle research loops. Implements planning-execute-hypothesize-reflect-assess cycles with convergence detection, contradiction handling, and evidence provenance tracking. Supports guided, semi-autonomous, and fully-autonomous research modes. Use when asked to do deep research, iterative investigation, hypothesis-driven research, multi-cycle analysis, convergence research, systematic investigation, evidence-based inquiry, research deep dive, comprehensive investigation, or knowledge graph construction.
---

# Deep Research

Iterative hypothesis-driven investigation engine inspired by BioAgents and Kosmos research frameworks. Executes multi-cycle research loops where each cycle includes planning, execution, hypothesis formation, reflection, and discovery assessment. Tracks information gain per cycle and converges when diminishing returns are detected. Maintains a two-tier state model separating ephemeral working notes from persistent accumulated knowledge.

Distinct from **literature-deep-research** (which performs structured literature review with collision-aware search) and **hypothesis-generation** (which formulates and scores competing hypotheses without iterative investigation). This skill operates as an iterative research engine that refines understanding through multiple cycles of evidence gathering, hypothesis revision, and convergence tracking.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_deep-research_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as each research cycle completes
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain
6. **Cycle log grows**: Each cycle appends to the Cycle Log section as it completes

## When NOT to Use This Skill

- Single-pass literature review without iteration -> use `literature-deep-research`
- Generating hypotheses without multi-cycle investigation -> use `hypothesis-generation`
- Evaluating a specific paper or manuscript -> use `peer-review`
- Quick factual lookup or verification -> use domain-specific MCP tools directly
- Scenario analysis or what-if modeling -> use `what-if-oracle`
- PRISMA-compliant systematic review -> use `systematic-literature-reviewer`
- Methodology critique or bias detection -> use `scientific-critical-thinking`
- Adversarial analysis of claims -> use `red-team-science`

## Cross-Reference: Other Skills

- **Single-pass literature review** -> use literature-deep-research skill
- **Hypothesis formulation and scoring** -> use hypothesis-generation skill
- **Manuscript evaluation** -> use peer-review skill
- **Adversarial challenge of findings** -> use red-team-science skill
- **Scenario modeling for decisions** -> use what-if-oracle skill
- **Target validation evidence** -> use drug-target-validator skill
- **Disease mechanism overview** -> use disease-research skill
- **Drug compound profiling** -> use drug-research skill
- **Clinical trial landscape** -> use clinical-trial-analyst skill

---

## Available MCP Tools

### `mcp__pubmed__pubmed_articles` (Literature Search)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search across PubMed | `keywords`, `num_results` |
| `search_advanced` | Filtered search with journal, date, author constraints | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details (abstract, authors, MeSH, journal) | `pmid` |

### `mcp__biorxiv__biorxiv_info` (Preprint Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_preprints` | Search bioRxiv/medRxiv preprints | `query`, `server`, `date_from`, `date_to`, `limit` |
| `get_preprint_details` | Full preprint metadata and abstract | `doi` |
| `search_published_preprints` | Find preprints that became peer-reviewed publications | `query`, `server`, `limit` |

### `mcp__opentargets__opentargets_info` (Target/Disease Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Resolve gene symbols/protein names to Ensembl IDs | `query`, `size` |
| `search_diseases` | Resolve disease names to EFO IDs | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId`, `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target profile (function, pathways, tractability) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes) | `id` (EFO ID) |

### `mcp__chembl__chembl_info` (Compound/Drug Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |

### `mcp__drugbank__drugbank_info` (Drug Profiling)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_by_name` | Find drug by name | `query` |
| `get_drug_details` | Full drug profile (mechanism, pharmacodynamics, targets) | `drugbank_id` |
| `search_by_target` | All drugs acting on a target | `target`, `limit` |
| `get_drug_interactions` | Drug-drug interactions | `drugbank_id` |

### `mcp__pubchem__pubchem_info` (Compound Profiling)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_by_name` | Find compound by name | `name`, `limit` |
| `get_compound_details` | Full compound profile | `cid` |
| `get_compound_targets` | Known biological targets | `cid`, `limit` |
| `get_bioassay_summary` | Bioassay results summary | `cid`, `limit` |

### `mcp__ctgov__ctgov_info` (Clinical Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search registered clinical trials | `intervention`, `condition`, `status`, `phase` |
| `get` | Full trial record including results | `nct_id` |
| `get_results` | Trial results data | `nct_id` |

### `mcp__fda__fda_info` (Regulatory Context)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search FDA drug database | `query`, `limit` |
| `get_drug_label` | Full drug labeling/prescribing info | `application_number` or `drug_name` |
| `search_adverse_events` | FAERS adverse event reports | `query`, `limit` |
| `get_approval_history` | Drug approval timeline | `drug_name` |

### `mcp__openalex__openalex_data` (Citation Networks & Research Landscape)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_works` | Search papers by keywords; returns citation counts and publication dates | `query` |
| `get_work` | Get work details by OpenAlex ID, DOI, or PMID | `id` |
| `search_authors` | Search researchers by name with institution and topic data | `query` |
| `get_author` | Author profile with citation counts by year for trend detection | `id` |
| `search_topics` | Search research topics; returns field/domain classification and citation metrics | `query` |
| `get_cited_by` | Forward citation expansion — find papers citing a given work | `workId` |
| `get_works_by_author` | Author's works sorted by citation count | `authorId` |
| `get_works_by_institution` | Institution's recent works for emerging research detection | `institutionId` |

**Usage note:** Use OpenAlex for citation network expansion during the Execute phase (forward citation chaining via `get_cited_by`), topic-based landscape mapping to identify adjacent research areas, and detecting emerging research trends via `search_topics` and institution-level publication tracking. Citation counts help prioritize papers during the Reflect phase.

---

## Core Research Loop

The deep research process executes iterative cycles until convergence is detected. Each cycle follows six phases:

```
CYCLE N
  |
  v
[1. PLANNING] --> Define focus, identify gaps, plan search strategy
  |
  v
[2. EXECUTE] --> Search literature, fetch data, run computations
  |
  v
[3. HYPOTHESIZE] --> Form or refine hypotheses based on new evidence
  |
  v
[4. REFLECT] --> Assess evidence quality, identify contradictions
  |
  v
[5. ASSESS DISCOVERY] --> Score information gain, detect novelty
  |
  v
[6. CONTINUE?] --> Convergence check: if <5% new info, conclude
  |
  +--> YES: Return to [1. PLANNING] for next cycle
  +--> NO: Proceed to final synthesis
```

### Phase 1: Planning

Define the focus for this cycle. In cycle 1, this is the original research question. In subsequent cycles, planning is driven by gaps identified in the previous reflection phase.

```
Cycle [N] Planning:
- Focus: [What aspect are we investigating this cycle?]
- Knowledge Gaps: [What do we not yet know?]
- Search Strategy:
  - Primary queries: [exact search terms]
  - Databases to query: [PubMed, bioRxiv, OpenTargets, ChEMBL, etc.]
  - Computational analyses planned: [if any]
- Expected Information Gain: [What do we expect to learn?]
- Success Criteria: [How will we know this cycle was productive?]
```

### Phase 2: Execute

Run the planned searches and analyses. Use MCP tools for literature and database queries. Use Python for computation and analysis.

**Literature search pattern:**
```
mcp__pubmed__pubmed_articles(method: "search_advanced",
  term: "(QUERY_TERM_1 OR QUERY_TERM_2) AND (FOCUS_TERM)",
  start_date: "YYYY/01/01",
  num_results: 30)

mcp__biorxiv__biorxiv_info(method: "search_preprints",
  query: "QUERY FOCUS",
  server: "biorxiv",
  limit: 20)
```

**Database query pattern:**
```
mcp__opentargets__opentargets_info(method: "get_target_disease_associations",
  targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx", minScore: 0.5, size: 25)

mcp__chembl__chembl_info(method: "get_bioactivity",
  chembl_id: "CHEMBLxxxxx", limit: 50)
```

**Key rules for execution:**
- Record every query executed (exact parameters)
- Note result counts and relevance
- Flag unexpected or contradictory results immediately
- Cross-validate findings across multiple databases
- Never fabricate PMIDs or data -- only report what tools return

### Phase 3: Hypothesize

Based on evidence gathered in the execute phase, form or revise hypotheses.

```
Cycle [N] Hypotheses:

HYPOTHESIS 1 (cycle [N] status: [NEW / REVISED / CONFIRMED / WEAKENED / REJECTED]):
  Statement: [Clear, falsifiable hypothesis]
  Supporting Evidence: [citations with evidence tiers T1-T4]
  Contradicting Evidence: [citations, if any]
  Confidence: [0-100%]
  Change from Prior Cycle: [What changed and why]

HYPOTHESIS 2:
  ...
```

**Hypothesis quality criteria:**
- Must be falsifiable (what evidence would disprove it?)
- Must be specific (not vague directional claims)
- Must reference evidence gathered in this or prior cycles
- Must track confidence changes across cycles

### Phase 4: Reflect

Critically assess what was learned and what remains uncertain.

```
Cycle [N] Reflection:

Evidence Quality Assessment:
- T1 (Mechanistic/Definitive): [count] findings
- T2 (Functional/Clinical): [count] findings
- T3 (Association/Computational): [count] findings
- T4 (Mention/Inferred): [count] findings

Contradictions Detected:
- [Finding A] contradicts [Finding B] because [reason]
  Resolution status: [UNRESOLVED / PARTIALLY RESOLVED / RESOLVED]
  Impact on hypotheses: [which hypotheses are affected]

Confidence Assessment:
- Overall confidence in primary hypothesis: [0-100%]
- Delta from prior cycle: [+/- X%]
- Remaining uncertainties: [list]

Blind Spots Identified:
- [What aspects haven't we investigated yet?]
- [What assumptions are we making without evidence?]
```

**Contradiction handling rules:**
1. Never silently resolve contradictions -- always flag them explicitly
2. Assess whether contradictions are real (methodological differences, population differences, temporal changes) or apparent (different definitions, scope differences)
3. Design targeted queries in the next cycle to resolve contradictions
4. If contradictions persist after investigation, report both sides with evidence quality

### Phase 5: Assess Discovery

Quantify what was learned in this cycle relative to prior knowledge.

```
Cycle [N] Discovery Assessment:

New Information Gained:
- [Finding 1]: [brief description] -- Novelty: [HIGH/MEDIUM/LOW]
- [Finding 2]: [brief description] -- Novelty: [HIGH/MEDIUM/LOW]

Information Gain Score: [0-100%]
  Calculation:
  - New findings not present in prior cycles: [count]
  - Revised hypotheses: [count]
  - Contradictions identified: [count]
  - Knowledge graph nodes added: [count]
  - Score = weighted sum / maximum possible

Cumulative Information Gain Curve:
  Cycle 1: [X]%
  Cycle 2: [Y]%
  Cycle 3: [Z]%
  ...

Does This Change Prior Understanding?
- [YES: How? / NO: Why not?]
```

### Phase 6: Continue Decision

Apply convergence criteria to decide whether another cycle is needed.

```
Convergence Check:

Information gain this cycle: [X]%
Convergence threshold: [5]% (default, adjustable by user)
Cycles completed: [N]
Max cycles allowed: [M] (if set by user)

Decision: [CONTINUE / CONVERGE]
Reason: [
  - CONTINUE if: information gain >= threshold AND unresolved contradictions exist AND max cycles not reached
  - CONVERGE if: information gain < threshold OR max cycles reached OR all hypotheses confirmed/rejected
]

If CONTINUING:
  Next cycle focus: [derived from reflection gaps and unresolved contradictions]
  Priority queries: [specific searches for next cycle]

If CONVERGING:
  Proceed to final synthesis
```

---

## Three Research Modes

### Mode Selection

```
User request analysis:
|-- "Walk me through each step" / "let me approve"
|   --> GUIDED MODE
|
|-- "Run N cycles focusing on X" / "max 5 cycles"
|   --> SEMI-AUTONOMOUS MODE
|
|-- "Research this thoroughly" / "find out everything"
    --> FULLY-AUTONOMOUS MODE
```

### Guided Mode

User approves each cycle before the next begins.

```
After each cycle:
1. Present cycle summary (planning, execution, hypotheses, reflection, discovery)
2. Present proposed next cycle focus
3. Ask user: "Proceed with cycle [N+1] focusing on [X]? Or redirect?"
4. Wait for user approval or redirection
5. If user redirects, incorporate new focus into next cycle planning
```

**When to use:** Exploratory research where the user wants to steer direction. Complex topics where the user has domain expertise to contribute. High-stakes investigations where intermediate findings need validation.

### Semi-Autonomous Mode

User sets constraints upfront; agent runs within them.

```
User-specified constraints:
- Max cycles: [N] (default: 5)
- Focus areas: [list of priority topics]
- Convergence threshold: [X]% (default: 5%)
- Must-answer questions: [specific questions to address]
- Excluded topics: [what to skip]

Agent behavior:
- Runs cycles autonomously within constraints
- Reports after each cycle (brief status, not full detail)
- Stops if convergence threshold met or max cycles reached
- Delivers full report at end
```

**When to use:** Well-defined research questions with clear scope. Time-constrained investigations. Topics where the user trusts the agent's direction.

### Fully-Autonomous Mode

Agent runs until convergence threshold is met with no user interaction.

```
Default parameters:
- Max cycles: 8
- Convergence threshold: 5%
- Focus: derived entirely from the research question
- Contradiction resolution: attempt resolution, flag if unresolvable

Agent behavior:
- Runs all cycles without pausing
- Manages its own focus transitions
- Delivers complete report only at the end
- Includes full cycle log for transparency
```

**When to use:** Background research tasks. Comprehensive investigations where thoroughness matters more than speed. Topics where the agent has sufficient tool access to investigate fully.

---

## Two-Tier State Model

### Ephemeral State (Per-Cycle Scratchpad)

Reset at the start of each new cycle. Contains working notes that inform the cycle but are not preserved.

```
EPHEMERAL STATE (Cycle N):
  Search Results Buffer:
    - [raw results from MCP tool queries]
  Working Hypotheses:
    - [preliminary ideas being evaluated]
  Analysis Notes:
    - [intermediate calculations, comparisons]
  Candidate Findings:
    - [findings being evaluated for promotion to persistent state]
```

### Persistent State (Accumulated Knowledge Graph)

Grows across cycles. Only confirmed or high-quality findings are promoted from ephemeral to persistent state.

```
PERSISTENT STATE (Accumulated):
  Confirmed Findings:
    - [Finding]: [evidence] -- Source: [PMID/DOI] -- Tier: [T1-T4] -- Confirmed in Cycle: [N]

  Working Hypotheses:
    - [Hypothesis]: Confidence [X]% -- First proposed: Cycle [N] -- Last updated: Cycle [M]

  Contradiction Log:
    - [Contradiction]: [Side A] vs [Side B] -- Status: [RESOLVED/UNRESOLVED] -- Cycle detected: [N]

  Evidence Chains:
    - [Chain name]: [Finding A] -> [Finding B] -> [Finding C] -- Strength: [STRONG/MODERATE/WEAK]

  Search History:
    - Cycle [N]: [query] -> [result count] -> [relevant count]

  Information Gain Log:
    - Cycle 1: [X]% | Cycle 2: [Y]% | Cycle 3: [Z]% | ...
```

**Promotion rules:**
- A finding moves from ephemeral to persistent when supported by T1 or T2 evidence from at least one source
- A hypothesis becomes "confirmed" when supported by T1 evidence with no unresolved contradictions
- A hypothesis is "rejected" when contradicted by T1 evidence that survives scrutiny
- Contradictions are logged immediately and persist until explicitly resolved

---

## Python Code Templates

### Information Gain Curve

```python
import matplotlib.pyplot as plt

def plot_information_gain(cycles, gains, threshold=5.0, title="Information Gain per Cycle"):
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#2ecc71' if g >= threshold else '#e74c3c' for g in gains]
    bars = ax.bar(cycles, gains, color=colors, edgecolor='white', width=0.6)
    ax.axhline(y=threshold, color='#e67e22', linestyle='--', linewidth=2,
               label=f'Convergence Threshold ({threshold}%)')
    for bar, gain in zip(bars, gains):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{gain:.1f}%', ha='center', fontweight='bold', fontsize=10)
    ax.set_xlabel('Research Cycle', fontsize=12)
    ax.set_ylabel('Information Gain (%)', fontsize=12)
    ax.set_title(title, fontweight='bold', fontsize=14)
    ax.legend(loc='upper right')
    ax.set_ylim(0, max(gains) + 15)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig('information_gain_curve.png', dpi=150, bbox_inches='tight')
    plt.show()

# Example usage:
# plot_information_gain([1, 2, 3, 4, 5], [45, 28, 15, 8, 3])
```

### Hypothesis Confidence Tracker

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_hypothesis_confidence(hypotheses, confidence_history, title="Hypothesis Confidence Across Cycles"):
    fig, ax = plt.subplots(figsize=(12, 7))
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#9b59b6', '#f39c12']
    markers = ['o', 's', '^', 'D', 'v']
    for i, (hyp, history) in enumerate(zip(hypotheses, confidence_history)):
        cycles = list(range(1, len(history) + 1))
        color = colors[i % len(colors)]
        marker = markers[i % len(markers)]
        ax.plot(cycles, history, marker=marker, color=color, linewidth=2,
                markersize=8, label=hyp, zorder=3)
        for c, conf in zip(cycles, history):
            ax.annotate(f'{conf}%', (c, conf), textcoords="offset points",
                        xytext=(0, 10), ha='center', fontsize=8, color=color)
    ax.axhline(y=80, color='#2ecc71', linestyle=':', alpha=0.5, label='Confirmation threshold')
    ax.axhline(y=20, color='#e74c3c', linestyle=':', alpha=0.5, label='Rejection threshold')
    ax.fill_between(ax.get_xlim(), 80, 100, alpha=0.05, color='green')
    ax.fill_between(ax.get_xlim(), 0, 20, alpha=0.05, color='red')
    ax.set_xlabel('Research Cycle', fontsize=12)
    ax.set_ylabel('Confidence (%)', fontsize=12)
    ax.set_title(title, fontweight='bold', fontsize=14)
    ax.set_ylim(0, 105)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig('hypothesis_confidence.png', dpi=150, bbox_inches='tight')
    plt.show()

# Example usage:
# plot_hypothesis_confidence(
#     ['H1: Target X drives disease', 'H2: Pathway Y is compensatory', 'H3: Resistance via Z'],
#     [[30, 55, 70, 82, 85], [40, 35, 50, 45, 42], [20, 25, 40, 60, 55]]
# )
```

### Knowledge Graph Visualization

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

def plot_knowledge_graph(nodes, edges, title="Accumulated Knowledge Graph"):
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    tier_colors = {'confirmed': '#2ecc71', 'working': '#f39c12', 'contradicted': '#e74c3c', 'rejected': '#95a5a6'}
    tier_shapes = {'confirmed': 's', 'working': 'o', 'contradicted': '^', 'rejected': 'x'}
    for node in nodes:
        color = tier_colors.get(node['status'], '#3498db')
        ax.scatter(node['x'], node['y'], s=300, color=color, zorder=5, edgecolors='white', linewidth=2)
        ax.annotate(node['label'], (node['x'], node['y']), textcoords="offset points",
                    xytext=(0, 15), ha='center', fontsize=8, fontweight='bold')
    for edge in edges:
        start = next(n for n in nodes if n['id'] == edge['from'])
        end = next(n for n in nodes if n['id'] == edge['to'])
        style = '-' if edge.get('strength') == 'strong' else '--'
        color = '#2c3e50' if edge.get('type') == 'supports' else '#e74c3c'
        ax.annotate('', xy=(end['x'], end['y']), xytext=(start['x'], start['y']),
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.5, linestyle=style))
        mid_x = (start['x'] + end['x']) / 2
        mid_y = (start['y'] + end['y']) / 2
        if edge.get('label'):
            ax.text(mid_x, mid_y, edge['label'], fontsize=7, ha='center', color=color, style='italic')
    legend_elements = [mpatches.Patch(color=c, label=l.capitalize()) for l, c in tier_colors.items()]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)
    ax.set_title(title, fontweight='bold', fontsize=14)
    plt.tight_layout()
    plt.savefig('knowledge_graph.png', dpi=150, bbox_inches='tight')
    plt.show()
```

### Evidence Tier Distribution

```python
import matplotlib.pyplot as plt

def plot_evidence_distribution(tier_counts, cycle_labels=None, title="Evidence Tier Distribution by Cycle"):
    tiers = ['T1: Mechanistic', 'T2: Functional', 'T3: Association', 'T4: Mention']
    colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
    if cycle_labels is None:
        cycle_labels = [f'Cycle {i+1}' for i in range(len(tier_counts))]
    fig, ax = plt.subplots(figsize=(12, 6))
    x = range(len(cycle_labels))
    width = 0.18
    for i, (tier, color) in enumerate(zip(tiers, colors)):
        values = [tc[i] for tc in tier_counts]
        offset = (i - 1.5) * width
        bars = ax.bar([xi + offset for xi in x], values, width, label=tier, color=color, edgecolor='white')
        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                        str(val), ha='center', fontsize=8, fontweight='bold')
    ax.set_xlabel('Research Cycle', fontsize=12)
    ax.set_ylabel('Number of Findings', fontsize=12)
    ax.set_title(title, fontweight='bold', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(cycle_labels)
    ax.legend(loc='upper right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig('evidence_distribution.png', dpi=150, bbox_inches='tight')
    plt.show()

# Example usage:
# plot_evidence_distribution(
#     [[2, 5, 8, 3], [4, 8, 6, 2], [6, 10, 4, 1], [7, 11, 3, 1]],
#     ['Cycle 1', 'Cycle 2', 'Cycle 3', 'Cycle 4']
# )
```

---

## Convergence Detection

### Information Gain Calculation

```
Information Gain (Cycle N) = weighted sum of:
  - New findings not in prior cycles:     weight 0.3
  - Hypothesis confidence changes > 10%:  weight 0.25
  - Contradictions identified:            weight 0.2
  - Knowledge graph nodes added:          weight 0.15
  - Evidence tier upgrades (T3->T2, etc): weight 0.1

Normalize to 0-100% scale.
```

### Convergence Criteria

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Information gain < threshold | Default 5% | CONVERGE |
| Max cycles reached | User-specified or 8 | CONVERGE |
| All hypotheses confirmed or rejected | N/A | CONVERGE |
| No unresolved contradictions remain | N/A | CONVERGE (if info gain also low) |
| Unresolved contradictions persist but no new evidence found | 2 consecutive low-gain cycles | CONVERGE with caveats |

### Convergence Override

The agent may override convergence and continue if:
- A high-impact contradiction was just discovered
- A T1 finding was just identified that changes a hypothesis
- The user explicitly requests more cycles (guided mode)

---

## Contradiction Handling Protocol

### Detection

```
Contradiction detected when:
1. Two T1/T2 findings directly contradict each other
2. A new finding reverses a previously confirmed hypothesis
3. Different databases report conflicting data for the same entity
4. A preprint contradicts a published peer-reviewed finding
```

### Classification

| Type | Description | Resolution Strategy |
|------|-------------|-------------------|
| **Methodological** | Different methods yield different results | Compare study designs, sample sizes, controls |
| **Population** | Different populations show different effects | Investigate subgroup differences, genetic backgrounds |
| **Temporal** | Earlier and later studies disagree | Check for field paradigm shifts, new techniques |
| **Definitional** | Same term used differently | Clarify definitions, scope of claims |
| **Genuine** | Real scientific disagreement | Report both sides with evidence quality, flag for future resolution |

### Resolution Workflow

```
1. Log contradiction in persistent state
2. Classify type (methodological, population, temporal, definitional, genuine)
3. In next cycle planning, prioritize resolution:
   - Search for meta-analyses or systematic reviews addressing the contradiction
   - Look for studies that directly compare the conflicting approaches
   - Check for retractions or corrections
4. If resolved: document resolution in knowledge graph with evidence
5. If unresolved after 2 targeted cycles: flag as genuine disagreement in final report
```

---

## Evidence Provenance Tracking

Every finding in the persistent state must include provenance:

```
Finding: [Statement]
  Source Type: [PubMed article / Preprint / Database record / Computation / Clinical trial]
  Source ID: [PMID / DOI / ChEMBL ID / NCT ID / computation hash]
  Evidence Tier: [T1 / T2 / T3 / T4]
  Retrieval Method: [MCP tool name and parameters used]
  Cycle Discovered: [N]
  Cycle Last Validated: [M]
  Cross-Validation: [other sources that confirm or contradict]
```

**Provenance rules:**
- No finding without a source ID
- No PMID that wasn't retrieved via `get_article_metadata`
- Computational findings must include the code or logic used
- Cross-validation attempted for all T1/T2 findings
- Preprint findings flagged as "not yet peer-reviewed"

---

## Report Structure

```
# Deep Research Report: [Research Question]

## Research Configuration
- Mode: [Guided / Semi-autonomous / Fully-autonomous]
- Max cycles: [N]
- Convergence threshold: [X]%
- Date: [YYYY-MM-DD]
- MCP tools used: [list]

## Executive Summary
[Final synthesis after all cycles. Written LAST, after all evidence is gathered.
Includes: primary conclusion, confidence level, key findings, remaining uncertainties.]

## Cycle Log

### Cycle 1: [Focus Area]
- **Planned**: [what we set out to investigate]
- **Executed**: [searches performed, computations run, data fetched]
  - [query 1]: [result count] relevant results
  - [query 2]: [result count] relevant results
- **Hypotheses Formed/Revised**:
  - H1: [statement] -- Confidence: [X]% -- Status: [NEW]
  - H2: [statement] -- Confidence: [X]% -- Status: [NEW]
- **Evidence Quality**: [T1: n, T2: n, T3: n, T4: n]
- **Contradictions**: [none / description]
- **Information Gain**: [X]%
- **Key Finding**: [one-liner summary of most important discovery]

### Cycle 2: [Focus Area]
- **Planned**: [derived from Cycle 1 gaps]
- **Executed**: [searches, computations]
- **Hypotheses Formed/Revised**:
  - H1: [statement] -- Confidence: [X]% -- Status: [REVISED, +Y%]
  - H3: [statement] -- Confidence: [X]% -- Status: [NEW]
- **Evidence Quality**: [T1: n, T2: n, T3: n, T4: n]
- **Contradictions**: [description if any]
- **Information Gain**: [X]%
- **Key Finding**: [one-liner]

### Cycle N: [Focus Area]
...

## Knowledge Graph

### Confirmed Findings (High Confidence >= 80%)
| Finding | Evidence Tier | Source | Confirmed in Cycle |
|---------|--------------|--------|-------------------|
| [Finding 1] | T1 | [PMID/DOI] | Cycle [N] |

### Working Hypotheses (Moderate Confidence 40-79%)
| Hypothesis | Confidence | First Proposed | Last Updated | Key Evidence |
|-----------|-----------|---------------|-------------|-------------|
| [H1] | [X]% | Cycle [N] | Cycle [M] | [PMID/DOI] |

### Contradictions and Unresolved Questions
| Contradiction | Side A | Side B | Status | Impact |
|--------------|--------|--------|--------|--------|
| [Description] | [Evidence A] | [Evidence B] | [RESOLVED/UNRESOLVED] | [Which hypotheses affected] |

### Evidence Chains
| Chain | Path | Strength | Cycles Involved |
|-------|------|----------|----------------|
| [Name] | Finding A -> B -> C | [STRONG/MODERATE/WEAK] | [1, 3, 4] |

## Convergence Analysis
- Total cycles completed: [N]
- Information gain per cycle: [C1: X%, C2: Y%, C3: Z%, ...]
- Convergence achieved: [YES at cycle N / NO, max cycles reached]
- Final information gain: [X]% (below threshold of [Y]%)
- Remaining gaps: [what we still do not know]
- Suggested follow-up investigations: [if any]

## Recommendations
[Actionable recommendations based on confirmed findings and working hypotheses.
Distinguish between high-confidence and tentative recommendations.
Note any caveats from unresolved contradictions.]

## Complete Reference List
### T1: Mechanistic/Definitive Evidence
- [Author et al., Journal Year, PMID:XXXXXXXX]

### T2: Functional/Clinical Evidence
- [Author et al., Journal Year, PMID:XXXXXXXX]

### T3: Association/Computational Evidence
- [Author et al., Journal Year, PMID:XXXXXXXX]

### T4: Mention/Inferred Evidence
- [Author et al., Journal Year, PMID:XXXXXXXX]
```

---

## Multi-Agent Workflow Examples

**"What is the role of gut microbiome in immunotherapy response?"**
1. Deep Research (this skill, semi-autonomous, 5 cycles) -> Iterative investigation starting with gut-immune axis, expanding to checkpoint inhibitor studies, refining hypotheses about specific bacterial taxa, resolving contradictions between cohort studies
2. Literature Deep Research -> Targeted literature search for specific bacterial species identified during deep research
3. Hypothesis Generation -> Formalize top hypotheses about microbiome-immunotherapy mechanisms
4. Clinical Trial Analyst -> Active trials investigating microbiome interventions with immunotherapy

**"Investigate whether APOE4 drives Alzheimer's through neuroinflammation vs amyloid"**
1. Deep Research (this skill, guided mode, 6 cycles) -> Cycle 1: amyloid evidence, Cycle 2: neuroinflammation evidence, Cycle 3: APOE4-specific mechanisms, Cycle 4: resolve contradictions between hypotheses, Cycle 5: integrate with recent clinical trial failures, Cycle 6: synthesize
2. Disease Research -> Alzheimer's disease overview and target landscape
3. Drug Target Validator -> APOE4 as therapeutic target assessment
4. Red Team Science -> Adversarial analysis of the winning hypothesis

**"Explore the mechanism of action of GLP-1 agonists in neurodegeneration"**
1. Deep Research (this skill, fully-autonomous) -> Multi-cycle investigation: GLP-1R CNS expression, neuroprotective signaling, animal model data, clinical evidence from diabetes cohorts, hypotheses about direct vs indirect mechanisms, convergence analysis
2. Drug Research -> GLP-1 agonist compound profiles (semaglutide, liraglutide, etc.)
3. Target Research -> GLP-1R target characterization in CNS tissues
4. Peer Review -> Evaluate key papers identified during deep research

**"Is ferroptosis a viable therapeutic target in pancreatic cancer?"**
1. Deep Research (this skill, semi-autonomous, max 6 cycles, focus: ferroptosis regulators, pancreatic cancer vulnerabilities, existing compounds) -> Iterative investigation with hypothesis tracking: H1 (GPX4 inhibition is sufficient), H2 (iron metabolism is the key vulnerability), H3 (combination with gemcitabine is needed)
2. Hypothesis Generation -> Formalize and score competing mechanistic hypotheses
3. Drug Target Analyst -> Druggability assessment of ferroptosis regulators (GPX4, SLC7A11, FSP1)
4. What-If Oracle -> Scenario analysis for ferroptosis-targeting drug development strategy
5. Red Team Science -> Pre-mortem analysis of a ferroptosis-targeting program

**"Research the emerging link between viral infections and autoimmune disease"**
1. Deep Research (this skill, fully-autonomous, 8 cycles) -> Broad investigation: molecular mimicry, bystander activation, viral persistence, EBV-MS link, SARS-CoV-2-autoimmunity, resolve contradictions between epidemiological and mechanistic evidence
2. Disease Research -> Autoimmune disease mechanism overview
3. Systematic Literature Reviewer -> PRISMA-quality review of EBV-MS epidemiological studies
4. Scientific Critical Thinking -> Evaluate methodology of key cohort studies

---

## Cycle Summary Template

After each cycle (used for status updates in guided/semi-autonomous modes):

```
=== CYCLE [N] SUMMARY ===
Focus: [what was investigated]
Key Finding: [most important discovery]
Hypothesis Update: [which hypotheses changed and how]
Contradictions: [new contradictions found / contradictions resolved]
Information Gain: [X]%
Cumulative Gains: [C1: X%, C2: Y%, ..., CN: Z%]
Next Cycle Focus: [planned direction]
Status: [CONTINUING / CONVERGING]
===
```

---

## Completeness Checklist

- [ ] Research question clearly defined and scoped
- [ ] Research mode selected (guided / semi-autonomous / fully-autonomous)
- [ ] At least 3 research cycles completed
- [ ] Each cycle has all six phases (planning, execution, hypothesis, reflection, discovery assessment, continue decision)
- [ ] Hypotheses tracked across cycles with confidence scores
- [ ] Contradictions explicitly flagged and not silently resolved
- [ ] Evidence provenance recorded for all findings (PMID, DOI, database ID)
- [ ] All PMIDs verified via `get_article_metadata` (no fabricated citations)
- [ ] Two-tier state model maintained (ephemeral scratchpad vs persistent knowledge graph)
- [ ] Convergence assessment performed with information gain tracking
- [ ] Knowledge graph distinguishes confirmed findings from working hypotheses
- [ ] Evidence tier distribution reported per cycle (T1, T2, T3, T4)
- [ ] Executive summary synthesizes across all cycles (written last)
- [ ] Remaining gaps and future directions identified
- [ ] Information gain tracked per cycle with convergence curve
- [ ] Report file created with all sections populated (no remaining placeholders)
- [ ] Visualization code provided for information gain curve and hypothesis confidence
- [ ] Cross-validation attempted for T1/T2 findings across multiple sources
