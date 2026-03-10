---
name: what-if-oracle
description: Structured scenario analysis and strategic decision-making for drug development, research planning, and portfolio management. Uses multi-branch scenario modeling (best/likely/worst/wildcard/contrarian/second-order) with probability-weighted outcomes, trigger conditions, and hedge strategies. Generates quantitative Decision Confidence Scores (0-100) and actionable decision frameworks. Use when asked to evaluate what-if scenarios, make go/no-go decisions, assess strategic options, plan for contingencies, evaluate portfolio risks, or model outcomes for drug development programs, clinical trial strategies, or research investments.
---

# What-If Oracle

Structured scenario analysis specialist for strategic decision-making in drug development, research planning, and portfolio management. This skill applies multi-branch scenario modeling with probability-weighted outcomes, trigger conditions, and hedge strategies to produce quantitative Decision Confidence Scores (0-100) and actionable decision frameworks.

Distinct from **competitive-intelligence** (which maps therapeutic landscapes and competitive positioning) and **drug-target-validator** (which scores individual targets for druggability). This skill operates at the strategic decision level, evaluating "what if" questions across multiple possible futures to inform go/no-go decisions, portfolio prioritization, and contingency planning.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_what-if-oracle_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Therapeutic area landscape mapping or competitor tracking -> use `competitive-intelligence`
- Individual target validation and druggability scoring -> use `drug-target-validator`
- Clinical trial protocol design or statistical analysis -> use `clinical-trial-protocol-designer`
- FDA regulatory pathway strategy or submission planning -> use `fda-consultant`
- Drug repurposing opportunity identification -> use `drug-repurposing-analyst`
- Hypothesis generation from literature or data -> use `hypothesis-generation`
- Comprehensive single-drug monograph -> use `drug-research`

## Cross-Skill Routing

- Drug target assessment needed for scenario assumptions -> `drug-target-validator`
- Clinical trial design options to model -> `clinical-trial-protocol-designer`
- Competitive landscape data for scenario inputs -> `competitive-intelligence`
- Regulatory pathway analysis for timeline scenarios -> `fda-consultant`
- Drug repurposing as alternative scenario -> `drug-repurposing-analyst`
- Hypothesis testing underlying scenario logic -> `hypothesis-generation`

---

## Available MCP Tools

### `mcp__pubmed__pubmed_data` (Evidence for Scenario Assumptions)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search PubMed by keywords, MeSH terms, author, journal | `query`, `num_results` |
| `fetch_details` | Full article metadata: abstract, authors, journal, DOI, MeSH | `pmid` |

**Oracle-specific uses:** Validate scenario assumptions with published evidence, find historical precedent for similar decisions, quantify probabilities using systematic reviews and meta-analyses, track publication trends signaling paradigm shifts.

### `mcp__ctgov__ctgov_data` (Clinical Trial Landscape & Competitive Timing)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search clinical trials by condition, intervention, phase, status | `condition`, `intervention`, `phase`, `status`, `pageSize` |
| `get` | Full trial details by NCT ID | `nctId` |
| `stats` | Trial statistics and counts | `condition`, `intervention` |

**Oracle-specific uses:** Map competitor trial timelines, assess enrollment velocity for data readout prediction, identify adaptive designs with branching decision points, quantify clinical development attrition rates by phase and therapeutic area.

### `mcp__opentargets__opentargets_data` (Target Validation Evidence Quality)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId`, `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability) | `id` |

**Oracle-specific uses:** Assess evidence quality underlying target-based assumptions, quantify genetic association strength for probability calibration, evaluate tractability scores to anchor feasibility scenarios.

### `mcp__fda__fda_data` (Regulatory Precedent Analysis)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `lookup_drug` | Search drugs by name, adverse events, labels, recalls | `search_term`, `search_type`, `limit` |
| `search_orange_book` | Find brand/generic drug products | `drug_name`, `include_generics` |
| `analyze_patent_cliff` | Forecast patent protection loss | `drug_name`, `years_ahead` |

**Oracle-specific uses:** Find regulatory precedents for approval probability estimation, analyze historical approval timelines, assess patent cliff scenarios and generic entry timing.

### `mcp__chembl__chembl_data` (Compound & Pipeline Intelligence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |

**Oracle-specific uses:** Assess compound development status for competitive timing scenarios, evaluate mechanism-of-action landscape for differentiation scenarios, retrieve historical phase transition data for probability anchoring.

---

## Core Framework: Scenario Analysis Pipeline

### Phase 1: Question Framing

Decompose every scenario question into four components:

| Component | Definition | Example |
|-----------|-----------|---------|
| **Variable** | What changes in this scenario | Phase 3 trial misses primary endpoint |
| **Magnitude** | How significant the change is | Narrow miss (p=0.08) vs wide miss (p=0.4) |
| **Timeframe** | When it occurs or over what period | Interim analysis (Q3 2026) vs final (Q1 2027) |
| **Context** | Conditions and constraints | Competitive landscape, regulatory environment, portfolio dependencies |

**Define the decision space:**
- What specific decision is being made? (go/no-go, resource allocation, pathway selection)
- Who are the key stakeholders? (R&D, commercial, regulatory, investors, patients)
- What are the constraints? (budget, timeline, portfolio balance, regulatory requirements)
- What is the cost of being wrong in each direction?

**Separate knowns from uncertainties:**

```
KNOWNS (high confidence)          UNCERTAINTIES (scenario drivers)
- Approved mechanism of action    - Efficacy magnitude in target population
- Phase 2 safety profile          - Competitive timing (competitor readouts)
- Regulatory pathway selected     - Payer willingness to reimburse at target price
- Manufacturing process validated - Enrollment rate for pivotal trial
```

---

### Phase 2: Scenario Branch Generation (4-6 Branches)

| Branch | Description | Probability Anchor | Purpose |
|--------|-------------|-------------------|---------|
| **Best Case** | Everything goes right | 10-15% | Defines upside; calibrates ambition |
| **Likely Case** | Most probable outcome | 40-50% | Base case for planning |
| **Worst Case** | Major setbacks occur | 15-20% | Defines downside; stress-tests resilience |
| **Wild Card** | Black swan / unexpected disruption | 5-10% | Captures tail risk |
| **Contrarian** | Conventional wisdom is wrong | 10-15% | Challenges assumptions; identifies blind spots |
| **Second Order** | Indirect / cascading effects dominate | 5-10% | Non-obvious consequences; systemic effects |

**Branch rules:**
1. Probabilities across all branches must sum to approximately 100% (95-105% acceptable)
2. Each branch must have a distinct core assumption differentiating it
3. Branches must be internally consistent (no contradictions within a branch)
4. At least one branch must challenge the dominant organizational assumption
5. Wild Card and Second Order must identify specific mechanisms, not vague risks

---

### Phase 3: Branch Analysis (for each branch)

#### 3.1 Probability Estimate

```
Branch: [Name]
Probability: [X]% (range: [low]% - [high]%)
Confidence in estimate: [High/Medium/Low]
Basis: [Evidence or reasoning, with T1-T4 grading]
```

Use base rates from historical data when available. Search for precedent:
```
mcp__pubmed__pubmed_data(method: "search", query: "phase 3 success rate [THERAPEUTIC AREA]", num_results: 10)
mcp__ctgov__ctgov_data(method: "stats", condition: "[DISEASE]", intervention: "[DRUG CLASS]")
```

#### 3.2 Narrative

Step-by-step description of what happens, specific enough to be falsifiable. Avoid vague statements; instead: "Phase 3 hits primary endpoint with p<0.001, showing 35% reduction in disease progression vs placebo."

#### 3.3 Key Assumptions

```
CRITICAL ASSUMPTIONS (branch fails if wrong):
1. [Assumption] — Evidence: [source] — Tier: T[X] — Confidence: [H/M/L]

SUPPORTING ASSUMPTIONS (branch weakened if wrong):
1. [Assumption] — Evidence: [source] — Tier: T[X] — Confidence: [H/M/L]
```

#### 3.4 Trigger Conditions

```
LEADING INDICATORS (6-12 months early):
- [Signal]: [What to monitor] — [Data source]

LAGGING INDICATORS (0-3 months, confirmatory):
- [Signal]: [What to monitor] — [Data source]
```

Examples: enrollment rate changes, competitor trial status changes, FDA advisory committee scheduled, key competitor publication, patent challenge filing, analyst estimate revisions.

#### 3.5 Consequences at Three Timeframes

| Timeframe | Consequence | Severity (1-5) | Reversibility |
|-----------|-------------|----------------|---------------|
| **Near-term (0-6 mo)** | [Immediate effects] | | [High/Med/Low] |
| **Mid-term (6-18 mo)** | [Developing effects] | | [High/Med/Low] |
| **Long-term (18 mo+)** | [Enduring effects] | | [High/Med/Low] |

Cover: scientific, clinical, regulatory, commercial, portfolio, and organizational dimensions.

#### 3.6 Required Response

```
IF this branch materializes:
  IMMEDIATE (within 30 days): [actions with owners and resources]
  MEDIUM-TERM (30-180 days): [actions with owners and resources]
  STRATEGIC PIVOT (if needed): [description + decision point for commitment]
```

#### 3.7 Non-Obvious Insight

Each branch must include one insight most analysts would miss, with explanation of why it matters and what cognitive bias or information asymmetry obscures it.

---

### Phase 4: Synthesis and Decision Framework

#### 4.1 Probability Distribution

```
Best Case      [|||||||||||]     12%
Likely Case    [|||||||||||||||||||||||||||||||||||||||||||||] 45%
Worst Case     [||||||||||||||||||]  18%
Wild Card      [|||||]        5%
Contrarian     [||||||||||||]   12%
Second Order   [||||||||]      8%
                              -----
                              100%
```

#### 4.2 Robust Actions (good across all scenarios)
- Data generation informing multiple decisions
- Capability building serving multiple programs
- Relationships (regulatory, KOL, payer) providing optionality
- Risk monitoring and early warning systems

#### 4.3 Hedge Actions (protect against worst cases)
- Backup compound in earlier development
- Alternative indication strategy (pivot-ready)
- Partnership/licensing as risk-sharing mechanism
- Adaptive trial design with built-in decision points

#### 4.4 Decision Triggers

```
Trigger Event                    → Action                         Deadline
──────────────────────────────── → ──────────────────────────────  ──────────
[Enrollment < 60% at month 12]  → [Expand sites / revise design]  [Date]
[Competitor Phase 3 positive]   → [Accelerate or differentiate]   [Date]
[Interim futility boundary met] → [Terminate or redesign]         [Date]
```

#### 4.5 The "1% Insight"

The single most important non-obvious conclusion: a concise statement with supporting evidence and strategic implication.

---

## Decision Confidence Score (0-100)

### Score Components

| Dimension | Max Points | Criteria |
|-----------|-----------|----------|
| **Data Quality** | 25 | Evidence-based inputs, not speculation |
| **Scenario Coverage** | 20 | All major branches explored, no blind spots |
| **Probability Calibration** | 20 | Probabilities sum to ~100%, reasonable ranges |
| **Actionability** | 20 | Clear decision triggers and response plans |
| **Robustness** | 15 | Robust actions identified across scenarios |

### Scoring Rubric

**Data Quality (0-25):** 21-25: >80% T1/T2 evidence | 16-20: >60% T1/T2 | 11-15: mixed T1-T4 | 6-10: mostly T3/T4 | 0-5: minimal evidence

**Scenario Coverage (0-20):** 17-20: all 6 branches, no blind spots | 13-16: 4-5 branches | 9-12: 3-4 branches | 5-8: best/likely/worst only | 0-4: fewer than 3

**Probability Calibration (0-20):** 17-20: sum 95-105%, anchored to base rates | 13-16: sum 90-110% | 9-12: sum 85-115% | 5-8: poor calibration | 0-4: arbitrary estimates

**Actionability (0-20):** 17-20: all branches have response plans with triggers and owners | 13-16: most branches covered | 9-12: partial | 5-8: limited | 0-4: descriptive only

**Robustness (0-15):** 13-15: 3+ robust actions tested across all branches, hedges with triggers | 10-12: 2-3 actions, major risks hedged | 7-9: partial | 4-6: mentioned but untested | 0-3: none

### Confidence Tiers

| Score | Tier | Interpretation | Recommended Action |
|-------|------|---------------|-------------------|
| **80-100** | High Confidence | Comprehensive, well-evidenced, actionable | Proceed with recommended strategy |
| **60-79** | Moderate Confidence | Solid but has gaps | Proceed with hedges in place |
| **40-59** | Low Confidence | Directionally useful but incomplete | Gather more data before deciding |
| **0-39** | Very Low Confidence | Fundamental uncertainty | Staged approach; invest in reducing uncertainties |

---

## Drug Development Scenario Templates

### 1. Go/No-Go Decision

Phase transition decision with efficacy, safety, commercial, and competitive branches.

**Key MCP queries:**
```
mcp__ctgov__ctgov_data(method: "stats", condition: "[DISEASE]", intervention: "[DRUG CLASS]")
mcp__pubmed__pubmed_data(method: "search", query: "phase [X] to phase [Y] transition success rate [AREA]", num_results: 10)
mcp__fda__fda_data(method: "lookup_drug", search_term: "[DRUG CLASS]", search_type: "labels", limit: 10)
```

**Branches:**
1. STRONG GO — Efficacy exceeds expectations, clean safety, clear regulatory path
2. CONDITIONAL GO — Adequate efficacy, manageable safety, competitive position viable
3. CONDITIONAL NO-GO — Borderline efficacy, safety concerns, requires trial redesign
4. CLEAR NO-GO — Failed efficacy, unacceptable safety, competitive disadvantage
5. CONTRARIAN — Negative topline but subgroup signal worth pursuing
6. WILD CARD — External event changes the decision calculus entirely

### 2. Clinical Trial Strategy

Adaptive design vs. traditional, biomarker-selected vs. all-comers.

**Decision parameters:**

| Design Option | Timeline | Cost | P(Success) | Risk |
|--------------|----------|------|-----------|------|
| Traditional Phase 3 | [X] months | $[X]M | [X]% | Low operational risk |
| Adaptive design | [X] months | $[X]M | [X]% | Moderate complexity risk |
| Biomarker-selected | [X] months | $[X]M | [X]% | Enrichment risk |
| All-comers | [X] months | $[X]M | [X]% | Dilution risk |

**Branches:** ADAPTIVE SUCCESS, TRADITIONAL SUCCESS, BIOMARKER WIN, ALL-COMERS REQUIRED, DESIGN FAILURE, REGULATORY SURPRISE.

### 3. Portfolio Prioritization

Resource allocation across multiple programs when budget or capacity is constrained.

**Program comparison matrix:**

| Program | Phase | Indication | Est. Peak Sales | P(Success) | Investment Needed |
|---------|-------|-----------|-----------------|-----------|------------------|
| [A] | [X] | [disease] | $[X]B | [X]% | $[X]M |
| [B] | [X] | [disease] | $[X]B | [X]% | $[X]M |

**Branches:** RISK-BALANCED (diversified), CONCENTRATED BET (highest-probability), OPTION VALUE (multiple early-stage), COMMERCIAL FIRST (nearest-to-market), SCIENCE FIRST (strongest rationale), EXTERNAL SHOCK (budget cut forces hard choices).

### 4. Competitive Response

React to competitor data (positive, negative, or surprising).

**Competitor event analysis:**
- What happened: [Specific data release or strategic action]
- Timing: [When announced]
- Significance: [Impact on our program]

**Branches:** DATA HOLDS (robust, changes landscape), DATA FADES (doesn't replicate), MARKET EXPANDS (validates market for all), MARKET SEGMENTS (forces niche positioning), REGULATORY SHIFT (changes FDA expectations for class), PARTNERSHIP OPPORTUNITY (creates collaboration openings).

### 5. Regulatory Strategy

Standard vs. accelerated pathway with regulatory risk scenarios.

**Pathway comparison:**

| Pathway | Timeline | Data Required | Risk Level | Precedent |
|---------|----------|--------------|-----------|-----------|
| Standard NDA | [X] months | Full Phase 3 | Low | [examples] |
| Accelerated Approval | [X] months | Surrogate endpoint | Medium | [examples] |
| Breakthrough + Priority | [X] months | Expedited package | Medium | [examples] |

**Branches:** STANDARD SUCCESS, ACCELERATED WIN, ACCELERATED RISK (confirmatory trial fails, approval withdrawn), CRL SCENARIO (resubmission required), ADVISORY COMMITTEE (uncertain vote), REGULATORY INNOVATION (novel pathway accepted).

### 6. Market Entry

First-in-class vs. best-in-class positioning and commercial strategy.

**Positioning comparison:**

| Strategy | Advantages | Risks | Required Differentiation |
|----------|-----------|-------|------------------------|
| First-in-class | Pricing power, market education | Unproven market | Novel mechanism |
| Best-in-class | Proven market, clear benchmarks | Crowded field | Superior profile |
| Niche position | Less competition | Limited market | Unique patient segment |

**Branches:** MARKET CREATION, FAST FOLLOWER, PRICE WAR, PAYER BLOCK, STANDARD OF CARE SHIFT, COMBINATION STANDARD.

### 7. Partnership/Licensing

Deal structure scenarios with valuation sensitivity.

**Deal parameter ranges:**

| Parameter | Range | Key Driver |
|-----------|-------|-----------|
| Upfront payment | $[X-Y]M | Phase, indication, competition |
| Milestones (total) | $[X-Y]M | Development + regulatory + commercial |
| Royalty rate | [X-Y]% | Net sales tier structure |
| Territory | [options] | Geographic rights and restrictions |

**Branches:** PREMIUM DEAL (competitive auction), FAIR VALUE (aligned partner), DISTRESSED DEAL (below-value terms), NO DEAL (fund internally or shelve), REVERSE DEAL (in-license instead), STRUCTURED DEAL (co-development, opt-in, profit share).

---

## Analysis Modes

### Quick Oracle (3 Branches)

Best Case, Likely Case, Worst Case only. Complete in a single analysis session.

**When to use:**
- Early-stage decisions with limited data
- Reversible decisions (can change course later)
- Time-sensitive responses to competitive events
- Preliminary assessment before committing to deep analysis

### Deep Oracle (6 Branches)

All six branches with full MCP tool data gathering. Comprehensive analysis required for high-stakes decisions.

**When to use:**
- Phase transition go/no-go decisions
- Portfolio prioritization with budget constraints
- Major partnership or licensing decisions
- Regulatory pathway selection for pivotal programs
- Any irreversible decision with significant financial commitment

### Scenario Chain (Recursive)

When one scenario triggers another decision point, creating a chain of dependent scenarios.

**Structure:**
```
Decision 1 → Scenario A → Decision 2a → Scenario A1, A2, A3
                        → Decision 2b → Scenario B1, B2, B3
           → Scenario B → Decision 3  → Scenario C1, C2, C3
```

**When to use:**
- Multi-phase drug development planning (Phase 1 -> 2 -> 3 -> filing)
- Sequential regulatory decisions (US then EU then Japan)
- Portfolio decisions with interdependent programs
- Adaptive trial designs with pre-specified decision points

### Reverse Oracle

Start from the desired outcome and work backward to identify conditions, decisions, and events required to reach it.

**Structure:**
```
DESIRED OUTCOME: [Specific end state]
REQUIRED CONDITIONS: [Met/Unmet/Uncertain with probabilities]
CRITICAL PATH: [Event N] <- [Event N-1] <- ... <- [Event 1 (NOW)]
FAILURE MODES: [Where the chain can break, with mitigation]
```

**When to use:**
- "What would it take to achieve X?" questions
- Working backward from a launch date or revenue target
- Identifying the weakest link in a development plan
- Stress-testing strategic plans against required assumptions

### Competitive Oracle

Multi-stakeholder perspective analysis modeling decisions and reactions from multiple players.

**Structure:**
```
PLAYER MAP:
| Player | Position | Key Assets | Likely Strategy | Our Vulnerability |

GAME THEORY:
- If we [action], competitor A will likely [response]
- If competitor B [action], the market will [effect]
- Nash equilibrium suggests [optimal strategy]
```

**When to use:**
- Competitive response planning after competitor data readout
- Market entry timing decisions in crowded therapeutic areas
- Pricing strategy in competitive markets with biosimilar/generic entry
- Partnership negotiations with competitive dynamics

---

## Python Code Templates

### Probability Distribution Bar Chart

```python
import matplotlib.pyplot as plt

def plot_scenario_probabilities(scenarios, probabilities, confidence_ranges=None, title="Scenario Probability Distribution"):
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#2ecc71', '#3498db', '#e74c3c', '#9b59b6', '#f39c12', '#1abc9c']
    bars = ax.barh(scenarios, probabilities, color=colors[:len(scenarios)], edgecolor='white')
    if confidence_ranges:
        xerr_low = [p - cr[0] for p, cr in zip(probabilities, confidence_ranges)]
        xerr_high = [cr[1] - p for p, cr in zip(probabilities, confidence_ranges)]
        ax.errorbar(probabilities, range(len(scenarios)), xerr=[xerr_low, xerr_high],
                     fmt='none', ecolor='black', capsize=4)
    for bar, prob in zip(bars, probabilities):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, f'{prob}%', va='center', fontweight='bold')
    ax.set_xlabel('Probability (%)')
    ax.set_title(title, fontweight='bold')
    ax.set_xlim(0, max(probabilities) + 15)
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig('scenario_probabilities.png', dpi=150, bbox_inches='tight')
    plt.show()
```

### Tornado Sensitivity Chart

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_tornado(variables, low_values, high_values, base_value, title="Sensitivity Analysis"):
    ranges = [abs(h - l) for h, l in zip(high_values, low_values)]
    sorted_idx = np.argsort(ranges)[::-1]
    variables = [variables[i] for i in sorted_idx]
    low_values = [low_values[i] for i in sorted_idx]
    high_values = [high_values[i] for i in sorted_idx]
    fig, ax = plt.subplots(figsize=(12, max(6, len(variables) * 0.8)))
    for i, (var, low, high) in enumerate(zip(variables, low_values, high_values)):
        ax.barh(i, high - base_value, left=base_value, color='#2ecc71', height=0.6)
        ax.barh(i, low - base_value, left=base_value, color='#e74c3c', height=0.6)
    ax.axvline(x=base_value, color='black', linewidth=1.5, linestyle='--', label=f'Base: {base_value}')
    ax.set_yticks(range(len(variables)))
    ax.set_yticklabels(variables)
    ax.set_title(title, fontweight='bold')
    ax.legend(loc='lower right')
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig('tornado_sensitivity.png', dpi=150, bbox_inches='tight')
    plt.show()
```

### Decision Tree Diagram

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

def plot_decision_tree(decision_label, branches, title="Decision Tree"):
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')
    decision_box = mpatches.FancyBboxPatch((0.5, 4), 2.5, 2, boxstyle="round,pad=0.3",
                                            facecolor='#2c3e50', edgecolor='white')
    ax.add_patch(decision_box)
    ax.text(1.75, 5, decision_label, ha='center', va='center', fontsize=9, color='white', fontweight='bold')
    y_positions = np.linspace(9, 1, len(branches))
    for branch, y_pos in zip(branches, y_positions):
        color = branch.get('color', '#3498db')
        ax.annotate('', xy=(5, y_pos), xytext=(3, 5), arrowprops=dict(arrowstyle='->', color=color, lw=2))
        ax.text(3.7, (5 + y_pos) / 2, f"{branch['probability']}%", fontsize=9, fontweight='bold', color=color)
        outcome_box = mpatches.FancyBboxPatch((5, y_pos - 0.5), 4.5, 1, boxstyle="round,pad=0.2",
                                               facecolor=color, alpha=0.15, edgecolor=color)
        ax.add_patch(outcome_box)
        ax.text(7.25, y_pos, f"{branch['name']}\n{branch['outcome']}", ha='center', va='center', fontsize=8)
    ax.set_title(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('decision_tree.png', dpi=150, bbox_inches='tight')
    plt.show()
```

### Timeline with Trigger Points

```python
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

def plot_trigger_timeline(events, triggers, title="Decision Timeline with Trigger Points"):
    fig, ax = plt.subplots(figsize=(14, 6))
    branch_colors = {'Best Case': '#2ecc71', 'Likely Case': '#3498db', 'Worst Case': '#e74c3c',
                     'Wild Card': '#9b59b6', 'Contrarian': '#f39c12', 'Second Order': '#1abc9c'}
    all_dates = []
    for event in events:
        d = datetime.strptime(event['date'], '%Y-%m-%d'); all_dates.append(d)
        marker = 'D' if event.get('type') == 'milestone' else 'o'
        ax.scatter(d, 0.5, color='#2c3e50', s=120, zorder=5, marker=marker)
        ax.annotate(event['label'], (d, 0.5), textcoords="offset points", xytext=(0, 20),
                     ha='center', fontsize=8, rotation=45)
    for trigger in triggers:
        d = datetime.strptime(trigger['date'], '%Y-%m-%d'); all_dates.append(d)
        color = branch_colors.get(trigger.get('branch', ''), '#e67e22')
        ax.scatter(d, -0.5, color=color, s=150, zorder=5, marker='^')
        ax.annotate(f"TRIGGER: {trigger['label']}", (d, -0.5), textcoords="offset points",
                     xytext=(0, -35), ha='center', fontsize=7, color=color, fontweight='bold')
    if all_dates:
        ax.hlines(0, min(all_dates) - timedelta(days=30), max(all_dates) + timedelta(days=30), color='black', lw=2)
        ax.set_xlim(min(all_dates) - timedelta(days=30), max(all_dates) + timedelta(days=30))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.set_ylim(-2, 2); ax.set_yticks([])
    ax.set_title(title, fontweight='bold')
    plt.tight_layout()
    plt.savefig('trigger_timeline.png', dpi=150, bbox_inches='tight')
    plt.show()
```

---

## Evidence Grading for Scenario Analysis

| Tier | Label | Criteria | Oracle Application |
|------|-------|----------|-------------------|
| **T1** | Regulatory / Definitive | Official filings, approved labels, published pivotal results | Base rates, efficacy/safety benchmarks, regulatory precedent |
| **T2** | Clinical / Published | Peer-reviewed RCTs, meta-analyses, treatment guidelines | Probability anchoring, historical success rates |
| **T3** | Conference / Emerging | Congress abstracts, preprints, interim analyses | Competitive timing signals, emerging trends |
| **T4** | Analyst / Inferred | Press releases, analyst reports, investor presentations | Timeline estimates, commercial forecasts, strategic intent |

**Rules:** Always cite the tier with data. Weight higher tiers more heavily. Flag T3/T4 dependence explicitly. Date-stamp all evidence. Cross-validate critical assumptions with T2+ sources.

---

## Multi-Agent Workflow Examples

**"Should we advance our JAK inhibitor to Phase 3 in RA?"**
1. What-If Oracle (this skill) -> Go/No-Go scenario analysis with efficacy, safety, competitive, regulatory branches
2. Drug Target Validator -> JAK target validation and safety liability assessment
3. Competitive Intelligence -> RA landscape with pipeline waterfall and JAK inhibitor LOE timeline
4. FDA Consultant -> Regulatory precedent for JAK inhibitor approvals

**"What happens if our competitor's Phase 3 NASH trial succeeds?"**
1. What-If Oracle (this skill) -> Competitive response: data holds vs fades vs market expansion vs segmentation
2. Competitive Intelligence -> NASH/MASH landscape with competitive position scoring

**"How should we allocate R&D budget across 4 oncology programs?"**
1. What-If Oracle (this skill) -> Portfolio prioritization with 6 allocation strategies
2. Competitive Intelligence -> Landscape analysis per indication for competitive inputs

**"Should we pursue accelerated approval or wait for Phase 3?"**
1. What-If Oracle (this skill) -> Regulatory strategy: accelerated vs standard pathway scenarios
2. FDA Consultant -> Precedent for accelerated approval, confirmatory trial requirements
3. Competitive Intelligence -> Competitive timing analysis

---

## Report Template

```
# What-If Oracle Report: [DECISION QUESTION]
Generated: [DATE]
Analysis Mode: [Quick/Deep/Chain/Reverse/Competitive Oracle]
Decision Confidence Score: [X/100] ([Tier])

## 1. Executive Summary
[2-3 paragraph synthesis with key findings and recommended action]

## 2. Question Frame
- Variable: [what changes] | Magnitude: [how much] | Timeframe: [when] | Context: [conditions]
- Decision: [specific decision] | Stakeholders: [who is affected]

## 3. Key Uncertainties vs Knowns
| Category | Item | Status | Evidence Tier |

## 4. Scenario Branches
### Branch [N]: [Name] — Probability: [X]% (range: [low]-[high]%)
**Narrative:** [step-by-step]
**Key Assumptions:** [with evidence tiers]
**Trigger Conditions:** [leading and lagging indicators]
**Consequences:** [near/mid/long-term with severity and reversibility]
**Required Response:** [immediate, medium-term, strategic pivot]
**Non-Obvious Insight:** [insight + why it matters]
[Repeat for each branch]

## 5. Synthesis
- Probability Distribution | Robust Actions | Hedge Actions | Decision Triggers | The 1% Insight

## 6. Decision Confidence Score Breakdown
| Dimension | Score | Max | Rationale |
| Data Quality | [X] | 25 | |
| Scenario Coverage | [X] | 20 | |
| Probability Calibration | [X] | 20 | |
| Actionability | [X] | 20 | |
| Robustness | [X] | 15 | |
| **TOTAL** | **[X]** | **100** | **[Tier]** |

## 7. Recommendation
[Clear, actionable recommendation with conditions]

## 8. Next Steps
[Specific actions with owners and deadlines]
```

---

## Completeness Checklist

- [ ] Question decomposed into Variable, Magnitude, Timeframe, and Context
- [ ] Decision space and stakeholders defined
- [ ] Key uncertainties vs knowns identified and catalogued
- [ ] Appropriate number of scenario branches generated (3 for Quick, 6 for Deep)
- [ ] Probabilities assigned to all branches and sum to 95-105%
- [ ] Each branch has a specific, falsifiable step-by-step narrative
- [ ] Key assumptions listed for each branch with evidence tiers (T1-T4)
- [ ] Trigger conditions defined (leading and lagging indicators) for each branch
- [ ] Consequences analyzed at three timeframes for each branch
- [ ] Required response plans defined for each branch with owners and timelines
- [ ] Non-obvious insight provided for each branch
- [ ] Robust actions identified and tested against all branches
- [ ] Hedge actions defined with activation triggers and cost estimates
- [ ] Decision triggers are specific, measurable, and have deadlines
- [ ] The 1% Insight captured with evidence and strategic implication
- [ ] Decision Confidence Score calculated with dimension-by-dimension breakdown
- [ ] Evidence grading (T1-T4) applied to all data points and assumptions
- [ ] MCP tools used to validate assumptions and gather evidence
- [ ] Report file created with all sections populated (no remaining placeholders)
- [ ] Visualization code provided for key charts (probability, tornado, timeline)
