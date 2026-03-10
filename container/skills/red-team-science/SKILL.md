---
name: red-team-science
description: Systematic adversarial analysis of scientific claims, research plans, drug candidates, clinical trial designs, and high-stakes scientific decisions. Implements five attack modes (pre-mortem, steel-man attack, failure mode enumeration, hidden assumption extraction, devil's advocate protocol) with quantitative Adversarial Severity Scoring (0-100). Use when asked to red team, challenge assumptions, find vulnerabilities, stress test, devil's advocate, pre-mortem, failure analysis, adversarial review, critique a plan, attack a hypothesis, find weaknesses, or challenge scientific claims.
---

# Red Team Science

Systematic adversarial analysis engine for high-stakes scientific decisions. Applies structured attack methodologies to identify vulnerabilities in scientific claims, research plans, drug candidates, clinical trial designs, regulatory strategies, and investment theses. Produces quantitative Adversarial Severity Scores (0-100) with actionable mitigation recommendations.

Distinct from **peer-review** (which evaluates manuscript quality and methodology), **scientific-critical-thinking** (which assesses evidence and detects biases), and **what-if-oracle** (which explores scenarios and models outcomes). This skill is explicitly adversarial: its purpose is to find what is wrong, weak, or likely to fail. It assumes the role of an informed, motivated critic.

## Report-First Workflow

1. **Create report file immediately**: `[target]_red-team-science_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as each attack mode completes
4. **Never show raw tool output**: Synthesize findings into vulnerability assessments
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain
6. **Score last**: Calculate Adversarial Severity Score only after all attacks are complete

## When NOT to Use This Skill

- Evaluating manuscript quality or providing reviewer feedback -> use `peer-review`
- Assessing methodology and detecting biases in published research -> use `scientific-critical-thinking`
- Exploring what-if scenarios or modeling strategic outcomes -> use `what-if-oracle`
- Generating competing hypotheses for a phenomenon -> use `hypothesis-generation`
- Conducting iterative research investigation -> use `deep-research`
- Writing a manuscript or scientific document -> use `scientific-writing`
- Designing a clinical trial protocol -> use `clinical-trial-protocol-designer`
- Comprehensive literature review -> use `literature-deep-research`

## Cross-Reference: Other Skills

- **Manuscript quality evaluation** -> use peer-review skill
- **Methodology assessment and bias detection** -> use scientific-critical-thinking skill
- **Scenario modeling and strategic decisions** -> use what-if-oracle skill
- **Hypothesis formulation and scoring** -> use hypothesis-generation skill
- **Iterative hypothesis-driven investigation** -> use deep-research skill
- **Drug target validation evidence** -> use drug-target-validator skill
- **Clinical trial landscape analysis** -> use clinical-trial-analyst skill
- **Regulatory pathway guidance** -> use fda-consultant skill
- **Drug safety signal detection** -> use pharmacovigilance-specialist skill
- **Competitive landscape mapping** -> use competitive-intelligence skill

---

## Available MCP Tools

### `mcp__pubmed__pubmed_articles` (Counter-Evidence Search)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search across PubMed | `keywords`, `num_results` |
| `search_advanced` | Filtered search with journal, date, author constraints | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details (abstract, authors, MeSH, journal) | `pmid` |

**Red-team-specific uses:** Search for negative results, failed replications, contradictory findings, retracted papers in the field, safety signals, and published criticisms of the target claim or approach.

### `mcp__biorxiv__biorxiv_info` (Emerging Counter-Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_preprints` | Search bioRxiv/medRxiv preprints | `query`, `server`, `date_from`, `date_to`, `limit` |
| `get_preprint_details` | Full preprint metadata and abstract | `doi` |
| `search_published_preprints` | Find preprints that became peer-reviewed publications | `query`, `server`, `limit` |

**Red-team-specific uses:** Find recent negative preprints, failed replication attempts, emerging safety concerns, and competing approaches that may invalidate the target's premise.

### `mcp__opentargets__opentargets_info` (Target Vulnerability Assessment)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Resolve gene symbols/protein names to Ensembl IDs | `query`, `size` |
| `search_diseases` | Resolve disease names to EFO IDs | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId`, `diseaseId`, `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target profile (function, pathways, tractability) | `id` (Ensembl ID) |

**Red-team-specific uses:** Assess target validation strength, identify competing targets with stronger evidence, check tractability concerns, find off-target pathway liabilities.

### `mcp__chembl__chembl_info` (Compound Vulnerability Analysis)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |
| `get_admet` | ADMET/drug-likeness properties | `chembl_id` |

**Red-team-specific uses:** Find selectivity liabilities, ADMET red flags, mechanism-based toxicity risks, historical failures of similar compounds, off-target activity profiles.

### `mcp__drugbank__drugbank_info` (Drug Safety and Interaction Risks)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_by_name` | Find drug by name | `query` |
| `get_drug_details` | Full drug profile | `drugbank_id` |
| `search_by_target` | All drugs acting on a target | `target`, `limit` |
| `get_drug_interactions` | Drug-drug interactions | `drugbank_id` |

### `mcp__fda__fda_info` (Regulatory Risk Assessment)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search FDA drug database | `query`, `limit` |
| `search_adverse_events` | FAERS adverse event reports | `query`, `limit` |
| `get_recall_info` | Drug recall information | `query`, `limit` |
| `get_approval_history` | Drug approval timeline | `drug_name` |

### `mcp__ctgov__ctgov_info` (Clinical Trial Failure Patterns)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search clinical trials (use status: "Terminated"/"Withdrawn" for failures) | `intervention`, `condition`, `status`, `phase` |
| `get` | Full trial record including results | `nct_id` |
| `get_results` | Trial results data | `nct_id` |

### `mcp__pubchem__pubchem_info` (Chemical Liability Profiling)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_by_name` | Find compound by name | `name`, `limit` |
| `get_compound_details` | Full compound profile | `cid` |
| `get_compound_targets` | Known biological targets (off-target risk) | `cid`, `limit` |
| `get_bioassay_summary` | Bioassay results summary | `cid`, `limit` |

---

## Five Attack Modes

### Attack Mode Selection

```
Target analysis:
|-- Scientific claim or published finding
|   --> STEEL-MAN ATTACK or DEVIL'S ADVOCATE PROTOCOL
|
|-- Research plan or drug development program
|   --> PRE-MORTEM or FAILURE MODE ENUMERATION
|
|-- Decision or strategic commitment
|   --> PRE-MORTEM
|
|-- Experimental design or protocol
|   --> HIDDEN ASSUMPTION EXTRACTION or FAILURE MODE ENUMERATION
|
|-- Consensus view or widely-held belief
|   --> DEVIL'S ADVOCATE PROTOCOL
|
|-- Any target (comprehensive)
    --> Run ALL FIVE MODES sequentially
```

**Mode selection guidance:**
- If time-limited, select the single most appropriate mode
- For high-stakes decisions, run all five modes
- For scientific claims, prioritize Steel-Man Attack + Devil's Advocate
- For drug programs, prioritize Pre-Mortem + Failure Mode Enumeration
- For experimental designs, prioritize Hidden Assumption Extraction

---

### Mode 1: Pre-Mortem

**Purpose:** Assume the target (project, trial, drug program) has failed completely. Write the post-mortem from the future.

**Methodology:**

```
Step 1: Set the failure scenario
  "It is [date 3-5 years in the future]. [The program/trial/project] has been
  terminated as a complete failure. The post-mortem analysis reveals the following..."

Step 2: Timeline reconstruction
  Work backward from failure to identify when things went wrong:
  - When did the first warning signs appear?
  - What decision points were critical?
  - When did failure become inevitable?
  - What was the total cost (time, money, opportunity)?

Step 3: Root cause analysis (5 Whys applied to each failure domain)
  TECHNICAL FAILURES:
  - What technical assumption was wrong?
    - Why was this assumption made?
      - Why was it not tested earlier?
        - Why did the test not reveal the problem?
          - Why was the test designed that way?

  BIOLOGICAL FAILURES:
  - What biological reality was misunderstood?
  - Was the target validated in the right context?
  - Was the disease model predictive?
  - Were resistance mechanisms anticipated?

  REGULATORY FAILURES:
  - What regulatory expectation was misjudged?
  - Were endpoints acceptable to the agency?
  - Were safety standards met?
  - Was the comparator appropriate?

  MARKET FAILURES:
  - Was the commercial thesis correct?
  - Did competitive dynamics change?
  - Was pricing/access viable?
  - Did physician adoption materialize?

  TEAM/ORGANIZATIONAL FAILURES:
  - Were the right people in the right roles?
  - Was the timeline realistic?
  - Were resources adequate?
  - Did organizational politics interfere?

Step 4: Warning signs analysis
  List warning signs that were available but ignored or downplayed:
  - [Signal]: Available since [date] -- Why it was ignored: [reason]
  - What cognitive biases contributed to ignoring these signals?
    (confirmation bias, sunk cost fallacy, groupthink, anchoring, optimism bias)

Step 5: Retrospective recommendations
  "If we could go back, we would have..."
  - [Action 1]: At [decision point] -- Expected impact: [what would have changed]
  - [Action 2]: At [decision point] -- Expected impact: [what would have changed]
```

**MCP tool usage for Pre-Mortem:**
```
# Search for historical failures of similar programs
mcp__pubmed__pubmed_articles(method: "search_advanced",
  term: "(TARGET OR MECHANISM) AND (failure OR discontinued OR terminated OR negative)",
  num_results: 30)

# Find terminated trials with same target/mechanism
mcp__ctgov__ctgov_info(method: "search",
  intervention: "DRUG_CLASS", condition: "DISEASE", status: "Terminated")
mcp__ctgov__ctgov_info(method: "search",
  intervention: "DRUG_CLASS", condition: "DISEASE", status: "Withdrawn")

# Check for safety signals in related drugs
mcp__fda__fda_info(method: "search_adverse_events", query: "DRUG_CLASS", limit: 50)
mcp__fda__fda_info(method: "get_recall_info", query: "DRUG_CLASS", limit: 20)

# Assess target validation weaknesses
mcp__opentargets__opentargets_info(method: "get_target_disease_associations",
  targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx", minScore: 0.1, size: 50)
```

---

### Mode 2: Steel-Man Attack

**Purpose:** Construct the strongest possible counter-argument against the target claim, then evaluate its force.

**Methodology:**

```
Step 1: State the target claim precisely
  "The claim being attacked: [exact statement]"
  "Context: [where/how/by whom this claim is made]"
  "Significance: [why this claim matters]"

Step 2: Identify the claim's weakest assumptions
  For each supporting pillar of the claim:
  - [Pillar 1]: [what evidence supports it] -- Weakness: [most fragile point]
  - [Pillar 2]: [what evidence supports it] -- Weakness: [most fragile point]
  - [Pillar 3]: [what evidence supports it] -- Weakness: [most fragile point]

  Rank pillars by fragility (most fragile first):
  1. [Most fragile pillar]: because [reason]
  2. [Second most fragile]: because [reason]
  3. [Third most fragile]: because [reason]

Step 3: Find the best evidence against the claim
  Search systematically for:
  - Failed replications
  - Contradictory findings from independent groups
  - Negative results in related systems
  - Methodological critiques of key supporting studies
  - Alternative explanations for the same data

Step 4: Construct the strongest counter-argument
  "The claim that [X] is wrong because:
  1. [Strongest counter-evidence]: [citation, T1-T4]
  2. [Second strongest]: [citation, T1-T4]
  3. [Third strongest]: [citation, T1-T4]

  The most compelling alternative explanation is:
  [Alternative hypothesis with supporting evidence]"

Step 5: Rate the counter-argument strength
  Counter-Argument Strength: [1-10]
  1-3: Weak -- claim is well-supported, counter-argument is speculative
  4-6: Moderate -- legitimate concerns but claim likely holds
  7-8: Strong -- significant evidence against the claim
  9-10: Devastating -- claim is likely wrong or fundamentally flawed

  Justification: [why this rating]
```

**MCP tool usage for Steel-Man Attack:**
```
# Search for negative/contradictory evidence
mcp__pubmed__pubmed_articles(method: "search_advanced",
  term: "(CLAIM_SUBJECT) AND (negative results OR failed OR no effect OR contradicts OR replication failure)",
  num_results: 30)

# Search for alternative explanations
mcp__pubmed__pubmed_articles(method: "search_keywords",
  keywords: "CLAIM_SUBJECT alternative mechanism explanation",
  num_results: 20)

# Search for critiques and commentaries
mcp__pubmed__pubmed_articles(method: "search_advanced",
  term: "(CLAIM_SUBJECT) AND (comment[pt] OR editorial[pt] OR letter[pt]) AND (critique OR concerns OR limitations)",
  num_results: 20)

# Check preprints for recent contradictory findings
mcp__biorxiv__biorxiv_info(method: "search_preprints",
  query: "CLAIM_SUBJECT negative failure",
  server: "biorxiv",
  limit: 20)
```

---

### Mode 3: Failure Mode Enumeration

**Purpose:** Systematically enumerate all possible failure modes across a comprehensive taxonomy, then score each by likelihood and impact.

**Methodology:**

```
Step 1: Define the target system
  "System being analyzed: [drug program / trial design / research plan / claim]"
  "Success criteria: [what must happen for the system to succeed]"
  "Critical path: [sequence of events required for success]"

Step 2: Enumerate failure modes by domain

  For each domain, create a table with columns:
  | ID | Failure Mode | Description | Likelihood (1-5) | Impact (1-5) | Risk Score | Mitigation |

  DOMAIN 1: TECHNICAL FAILURES (T1-T5)
  Assay failure, compound instability, model inadequacy, manufacturing failure, formulation failure

  DOMAIN 2: BIOLOGICAL FAILURES (B1-B7)
  Target not validated, resistance mechanisms, off-target toxicity, on-target toxicity,
  bioavailability, patient heterogeneity, biomarker failure

  DOMAIN 3: REGULATORY FAILURES (R1-R5)
  Endpoint rejected, safety signal, comparator issues, data integrity, label restrictions

  DOMAIN 4: MARKET FAILURES (M1-M5)
  Competition, pricing pressure, access barriers, physician adoption, market size overestimate

  DOMAIN 5: ETHICAL FAILURES (E1-E4)
  Consent issues, equity concerns, dual-use risk, data privacy

Step 3: Score each failure mode
  Likelihood (1-5): 1=Very unlikely, 2=Unlikely, 3=Possible, 4=Likely, 5=Very likely
  Impact (1-5): 1=Negligible, 2=Minor, 3=Moderate, 4=Major, 5=Catastrophic
  Risk Score = Likelihood x Impact (1-25)

Step 4: Risk matrix visualization
  Create risk heatmap with failure modes plotted by likelihood vs impact

Step 5: Prioritize mitigation
  Top 5 failure modes by risk score:
  1. [ID]: Risk [score] -- Mitigation: [specific action]
  2. [ID]: Risk [score] -- Mitigation: [specific action]
  ...
```

**MCP tool usage for Failure Mode Enumeration:**
```
# Assess target validation for biological failure modes
mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")

# Check ADMET for compound liability
mcp__chembl__chembl_info(method: "get_admet", chembl_id: "CHEMBLxxxxx")

# Search for class-related safety signals
mcp__fda__fda_info(method: "search_adverse_events", query: "DRUG_CLASS", limit: 50)

# Find terminated trials in the same space (regulatory/clinical failures)
mcp__ctgov__ctgov_info(method: "search",
  intervention: "MECHANISM_CLASS", condition: "DISEASE", status: "Terminated")

# Check compound selectivity for off-target risk
mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "CHEMBLxxxxx", limit: 100)
mcp__pubchem__pubchem_info(method: "get_compound_targets", cid: "CID", limit: 50)
```

---

### Mode 4: Hidden Assumption Extraction

**Purpose:** Surface every assumption (stated and unstated) underlying the target, rate fragility, and design tests for the most fragile ones.

**Methodology:**

```
Step 1: Identify the target's stated assumptions
  Read the plan/claim/protocol and extract every explicit assumption:
  - "The authors assume that..."
  - "The protocol requires that..."
  - "The program depends on..."

Step 2: Surface unstated assumptions
  For each component of the target, ask: "What must be true for this to work?"

  SCIENTIFIC ASSUMPTIONS (often unstated):
  - Target biology is understood correctly
  - In vitro findings translate to in vivo
  - Animal models predict human response
  - Pathway is not redundant
  - Biomarker reflects disease activity
  - Disease mechanism is the same across patient populations

  METHODOLOGICAL ASSUMPTIONS (often unstated):
  - Assay is measuring what we think it measures
  - Controls are appropriate
  - Sample size is adequate
  - Statistical model is correct
  - Missing data is random (not informative)
  - Effect size estimate from Phase 2 is reliable

  OPERATIONAL ASSUMPTIONS (often unstated):
  - Enrollment will proceed as planned
  - Supply chain will be reliable
  - Key personnel will remain
  - Budget will not be cut
  - Timeline is achievable

  MARKET ASSUMPTIONS (often unstated):
  - Standard of care will not change during development
  - Competitive landscape will not shift dramatically
  - Regulatory requirements will not change
  - Payer environment will remain favorable
  - Physician and patient willingness to adopt

Step 3: Rate assumption fragility

| # | Assumption | Type | Fragility (1-5) | Testable? | Test Design | Cost to Test |
|---|-----------|------|-----------------|-----------|-------------|-------------|
| 1 | [assumption] | [stated/unstated] | [1-5] | [Yes/No] | [how] | [estimate] |

Fragility scale:
  1 = Rock solid -- would require extraordinary evidence to break
  2 = Stable -- unlikely to break but not guaranteed
  3 = Moderate -- plausible scenarios could break it
  4 = Fragile -- known risks or weak evidence
  5 = Extremely fragile -- assumption rests on hope, not evidence

Step 4: Design quick tests for the most fragile assumptions (top 5)

For each fragile assumption:
  Assumption: [statement]
  Fragility: [score]
  Quick Test: [experiment or analysis that could validate/invalidate]
  Timeline: [days/weeks/months]
  Cost: [estimate]
  Kill Criterion: [what result would invalidate the assumption]
  Implication if Broken: [what happens to the program/claim]

Step 5: Classify as testable vs articles of faith

TESTABLE ASSUMPTIONS (can be validated before commitment):
- [assumption]: Test = [method], timeline = [X]

ARTICLES OF FAITH (cannot be tested, must be accepted):
- [assumption]: Why untestable = [reason]
- Risk if wrong: [consequence]
- Hedging strategy: [how to protect against being wrong]
```

**MCP tool usage for Hidden Assumption Extraction:**
```
# Validate target biology assumptions
mcp__opentargets__opentargets_info(method: "get_target_disease_associations",
  targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx", minScore: 0.1, size: 50)
mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")

# Check if animal model predictions hold
mcp__pubmed__pubmed_articles(method: "search_advanced",
  term: "(TARGET) AND (animal model OR preclinical) AND (translation OR predictive OR failure)",
  num_results: 20)

# Assess standard of care stability
mcp__ctgov__ctgov_info(method: "search",
  condition: "DISEASE", phase: "Phase 3", status: "Active, not recruiting")

# Check competitive landscape for market assumptions
mcp__chembl__chembl_info(method: "drug_search", query: "INDICATION", limit: 30)

# Validate biomarker assumptions
mcp__pubmed__pubmed_articles(method: "search_keywords",
  keywords: "BIOMARKER predictive validity DISEASE",
  num_results: 20)
```

---

### Mode 5: Devil's Advocate Protocol

**Purpose:** Argue against the consensus position with evidence, constructing the strongest possible dissenting case.

**Methodology:**

```
Step 1: State the consensus position clearly
  "The current consensus is: [precise statement]"
  "This consensus is held by: [community/organizations]"
  "Key supporting evidence: [citations]"
  "How long has this been the consensus: [timeframe]"
  "Level of consensus: [unanimous / strong majority / slim majority / contested]"

Step 2: Find published evidence that contradicts the consensus
  Systematic search for:
  - Negative results in well-powered studies
  - Failed replications
  - Evidence from different populations/contexts
  - Mechanistic evidence that undermines the consensus explanation
  - New data that was not available when consensus formed
  - Retracted or corrected papers that were foundational to the consensus

Step 3: Identify experts who disagree and why
  Search for:
  - Published dissenting opinions (editorials, commentaries, letters)
  - Alternative theoretical frameworks
  - Researchers whose data contradicts the consensus
  - Historical precedents where similar consensus was later overturned

Step 4: Construct the strongest dissenting case
  "The consensus that [X] is wrong because:

  EVIDENCE AGAINST:
  1. [Study/finding]: [what it shows] -- [why it matters] -- [citation, T1-T4]
  2. [Study/finding]: [what it shows] -- [why it matters] -- [citation, T1-T4]
  3. [Study/finding]: [what it shows] -- [why it matters] -- [citation, T1-T4]

  ALTERNATIVE EXPLANATION:
  [Coherent alternative that explains the same data better]
  Supporting evidence: [citations]

  WHY THE CONSENSUS MAY PERSIST DESPITE BEING WRONG:
  [Assess: publication bias, funding incentives, career incentives, cognitive factors, historical inertia]"

Step 5: Assess the consensus
  Is the consensus actually well-supported?

  Consensus Robustness Score (1-10):
  1-3: FRAGILE -- significant credible challenges exist, consensus may be wrong
  4-6: MODERATE -- some legitimate challenges but consensus holds on balance
  7-8: STRONG -- challenges exist but are outweighed by supporting evidence
  9-10: UNASSAILABLE -- no credible challenge found despite thorough search

  Assessment: [detailed justification for the score]
  Key vulnerability: [the single strongest challenge to the consensus]
  Implication: [what should change if the dissenting view is correct]
```

**MCP tool usage for Devil's Advocate:**
```
# Search for contradictory evidence
mcp__pubmed__pubmed_articles(method: "search_advanced",
  term: "(CONSENSUS_TOPIC) AND (negative OR contradicts OR challenges OR refutes OR questions)",
  num_results: 30)

# Search for failed replications
mcp__pubmed__pubmed_articles(method: "search_keywords",
  keywords: "CONSENSUS_TOPIC replication failure",
  num_results: 20)

# Search for dissenting expert opinions
mcp__pubmed__pubmed_articles(method: "search_advanced",
  term: "(CONSENSUS_TOPIC) AND (editorial[pt] OR comment[pt] OR letter[pt]) AND (disagree OR challenge OR alternative OR reconsider)",
  num_results: 20)

# Check preprints for emerging challenges
mcp__biorxiv__biorxiv_info(method: "search_preprints",
  query: "CONSENSUS_TOPIC challenge alternative",
  server: "biorxiv",
  limit: 20)

# Look for paradigm shifts in the field
mcp__pubmed__pubmed_articles(method: "search_advanced",
  term: "(CONSENSUS_TOPIC) AND (paradigm shift OR reconsidered OR revised understanding)",
  num_results: 15)
```

---

## Adversarial Severity Score (0-100)

### Score Interpretation

| Range | Severity | Meaning | Recommended Action |
|-------|---------|---------|-------------------|
| **0-20** | Robust | Attack found no significant vulnerabilities | Proceed with confidence; monitor for future risks |
| **21-40** | Minor Concerns | Addressable weaknesses identified | Proceed with mitigation plan for identified weaknesses |
| **41-60** | Significant | Requires mitigation before proceeding | Pause and address vulnerabilities; do not proceed without fixes |
| **61-80** | Critical | Fundamental issues that may be fatal | Serious reconsideration needed; major redesign may be required |
| **81-100** | Fatally Flawed | Recommend abandoning or major redesign | Stop; redirect resources; fundamental rethinking required |

### Score Calculation

```
Adversarial Severity Score = weighted average across all attack modes performed

Component scores (each 0-100):
1. Vulnerability Count Score:
   - 0 critical + 0 major = 0-10
   - 1 critical or 2+ major = 30-50
   - 2+ critical = 60-80
   - 3+ critical + multiple major = 80-100

2. Evidence Quality of Vulnerabilities:
   - Vulnerabilities supported by T1/T2 evidence: score higher
   - Vulnerabilities based on T3/T4 or speculation: score lower

3. Mitigation Feasibility:
   - All vulnerabilities have clear, low-cost mitigations: score lower (less severe)
   - Vulnerabilities are inherent and difficult to mitigate: score higher (more severe)

4. Cascading Risk:
   - Vulnerabilities are independent: score lower
   - Vulnerabilities compound or trigger each other: score higher

Final Score = 0.3 * Vulnerability Count + 0.25 * Evidence Quality
            + 0.25 * Mitigation Difficulty + 0.2 * Cascading Risk
```

---

## Python Code Templates

### Risk Heatmap (Failure Mode Enumeration)

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_risk_heatmap(failure_modes, likelihoods, impacts, labels=None, title="Failure Mode Risk Heatmap"):
    fig, ax = plt.subplots(figsize=(10, 8))
    risk_scores = [l * i for l, i in zip(likelihoods, impacts)]
    scatter = ax.scatter(likelihoods, impacts, s=[r * 40 for r in risk_scores],
                         c=risk_scores, cmap='RdYlGn_r', edgecolors='black',
                         linewidth=1, alpha=0.8, vmin=1, vmax=25)
    for i, fm in enumerate(failure_modes):
        label = labels[i] if labels else fm
        ax.annotate(label, (likelihoods[i], impacts[i]),
                    textcoords="offset points", xytext=(10, 5),
                    fontsize=8, fontweight='bold')
    ax.set_xlabel('Likelihood (1-5)', fontsize=12)
    ax.set_ylabel('Impact (1-5)', fontsize=12)
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_xticklabels(['Very\nUnlikely', 'Unlikely', 'Possible', 'Likely', 'Very\nLikely'])
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(['Negligible', 'Minor', 'Moderate', 'Major', 'Catastrophic'])
    ax.axhline(y=3.5, color='gray', linestyle=':', alpha=0.5)
    ax.axvline(x=3.5, color='gray', linestyle=':', alpha=0.5)
    ax.fill_between([3.5, 5.5], 3.5, 5.5, alpha=0.08, color='red', label='Critical Zone')
    ax.fill_between([0.5, 2.5], 0.5, 2.5, alpha=0.08, color='green', label='Low Risk Zone')
    plt.colorbar(scatter, label='Risk Score (Likelihood x Impact)')
    ax.set_title(title, fontweight='bold', fontsize=14)
    ax.legend(loc='lower left')
    plt.tight_layout()
    plt.savefig('risk_heatmap.png', dpi=150, bbox_inches='tight')
    plt.show()

# Example usage:
# plot_risk_heatmap(
#     ['B1: Target not validated', 'B3: Off-target toxicity', 'R1: Endpoint rejected',
#      'M1: Competition', 'T3: Model inadequacy'],
#     [3, 2, 3, 4, 3],  # likelihoods
#     [5, 4, 4, 3, 4],  # impacts
#     labels=['B1', 'B3', 'R1', 'M1', 'T3']
# )
```

### Assumption Fragility Chart

```python
import matplotlib.pyplot as plt

def plot_assumption_fragility(assumptions, fragility_scores, testable, title="Hidden Assumption Fragility"):
    fig, ax = plt.subplots(figsize=(12, max(6, len(assumptions) * 0.6)))
    colors = ['#2ecc71' if t else '#e74c3c' for t in testable]
    bars = ax.barh(range(len(assumptions)), fragility_scores, color=colors, edgecolor='white', height=0.6)
    for i, (bar, score) in enumerate(zip(bars, fragility_scores)):
        label = 'Testable' if testable[i] else 'Article of Faith'
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                f'{score}/5 ({label})', va='center', fontsize=9, fontweight='bold')
    ax.set_yticks(range(len(assumptions)))
    ax.set_yticklabels(assumptions, fontsize=9)
    ax.set_xlabel('Fragility Score (1=Rock Solid, 5=Extremely Fragile)', fontsize=11)
    ax.set_xlim(0, 6)
    ax.axvline(x=3, color='orange', linestyle='--', alpha=0.7, label='Moderate Fragility Threshold')
    ax.set_title(title, fontweight='bold', fontsize=14)
    ax.legend(loc='lower right')
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig('assumption_fragility.png', dpi=150, bbox_inches='tight')
    plt.show()

# Example usage:
# plot_assumption_fragility(
#     ['Target is causal', 'Animal model predicts human', 'Biomarker is valid',
#      'No resistance mechanisms', 'SOC wont change', 'Enrollment on track'],
#     [2, 4, 3, 4, 3, 2],
#     [True, True, True, True, False, True]
# )
```

### Vulnerability Summary Bar Chart

```python
import matplotlib.pyplot as plt

def plot_vulnerability_summary(domains, critical, major, minor, cosmetic, title="Vulnerability Summary by Domain"):
    fig, ax = plt.subplots(figsize=(12, 6))
    x = range(len(domains))
    width = 0.2
    ax.bar([xi - 1.5*width for xi in x], critical, width, label='Critical (80-100)', color='#e74c3c', edgecolor='white')
    ax.bar([xi - 0.5*width for xi in x], major, width, label='Major (50-79)', color='#e67e22', edgecolor='white')
    ax.bar([xi + 0.5*width for xi in x], minor, width, label='Minor (20-49)', color='#f1c40f', edgecolor='white')
    ax.bar([xi + 1.5*width for xi in x], cosmetic, width, label='Cosmetic (0-19)', color='#2ecc71', edgecolor='white')
    ax.set_xlabel('Domain', fontsize=12)
    ax.set_ylabel('Number of Vulnerabilities', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(domains)
    ax.legend(loc='upper right')
    ax.set_title(title, fontweight='bold', fontsize=14)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig('vulnerability_summary.png', dpi=150, bbox_inches='tight')
    plt.show()

# Example usage:
# plot_vulnerability_summary(
#     ['Technical', 'Biological', 'Regulatory', 'Market', 'Ethical'],
#     [0, 1, 0, 0, 0], [1, 2, 1, 1, 0], [2, 1, 1, 2, 1], [1, 0, 1, 1, 0]
# )
```

---

## Evidence Grading for Red Team Analysis

| Tier | Label | Criteria | Red Team Application |
|------|-------|----------|---------------------|
| **T1** | Definitive Counter-Evidence | Published RCTs, pivotal trial failures, FDA CRLs, retracted foundational papers | Strongest attacks; vulnerabilities backed by T1 are near-certain |
| **T2** | Strong Counter-Evidence | Peer-reviewed negative results, meta-analyses showing no effect, class-wide safety signals | Solid attacks; require mitigation before proceeding |
| **T3** | Suggestive Counter-Evidence | Preprints, conference reports, failed replications in related systems | Legitimate concerns; warrant investigation |
| **T4** | Speculative Concerns | Expert opinion, theoretical arguments, analogies to other failures | Worth noting but low weight in severity scoring |

**Red team evidence rules:**
- Vulnerabilities backed by T1/T2 evidence score higher in severity
- T3/T4 vulnerabilities are reported but weighted lower
- Every vulnerability must cite its evidence tier
- Counter-arguments are only as strong as their evidence
- Absence of counter-evidence is not evidence of robustness (check for publication bias)

---

## Multi-Agent Workflow Examples

**"Red team our CDK4/6 inhibitor program in triple-negative breast cancer"**
1. Red Team Science (this skill, all 5 modes) -> Pre-mortem of program failure, steel-man attack on CDK4/6 rationale in TNBC, failure mode enumeration across all domains, hidden assumption extraction from preclinical package, devil's advocate on CDK4/6 activity in non-luminal subtypes
2. Drug Target Validator -> CDK4/6 validation evidence specifically in TNBC (vs HR+ where validated)
3. Clinical Trial Analyst -> Historical CDK4/6 trials in TNBC (identify failures)
4. Competitive Intelligence -> TNBC therapeutic landscape and competing approaches

**"Challenge the hypothesis that tau aggregation drives neurodegeneration"**
1. Red Team Science (this skill, Steel-Man Attack + Devil's Advocate) -> Strongest counter-evidence to tau hypothesis, alternative mechanisms (inflammation, synaptic dysfunction, metabolic), assessment of tauopathy clinical trial failures
2. Deep Research -> Multi-cycle investigation of anti-tau therapy failures
3. Literature Deep Research -> Comprehensive review of tau-neurodegeneration evidence
4. Scientific Critical Thinking -> Methodology assessment of key tau studies

**"Stress test our Phase 3 clinical trial design for NASH"**
1. Red Team Science (this skill, Failure Mode Enumeration + Hidden Assumption Extraction) -> Enumerate trial design failure modes, extract assumptions about endpoints, enrollment, biomarkers, comparator
2. Clinical Trial Protocol Designer -> Review protocol against best practices
3. FDA Consultant -> Regulatory precedent for NASH trial endpoints and recent FDA guidance
4. What-If Oracle -> Scenario analysis for trial outcomes

**"Pre-mortem analysis of our antibody drug conjugate platform"**
1. Red Team Science (this skill, Pre-Mortem) -> Full pre-mortem: timeline to failure, root causes across technical/biological/regulatory/market, warning signs, cognitive biases in the team
2. Formulation Science -> ADC stability and manufacturing risk assessment
3. Pharmacovigilance Specialist -> Safety signals from approved ADCs
4. Drug Research -> Profiles of approved ADCs and their development histories
5. Competitive Intelligence -> ADC competitive landscape and pipeline

**"Evaluate whether the amyloid hypothesis should be abandoned"**
1. Red Team Science (this skill, Devil's Advocate Protocol) -> State consensus, find contradictory evidence, identify dissenting experts, construct strongest anti-amyloid case, assess consensus robustness
2. Deep Research -> Multi-cycle investigation of amyloid hypothesis evidence
3. Hypothesis Generation -> Generate and score alternative hypotheses for AD pathogenesis
4. Scientific Critical Thinking -> Evaluate methodology of key amyloid studies

---

## Report Template

```
# Red Team Report: [Target]
Generated: [DATE]
Attack Mode(s): [Pre-Mortem / Steel-Man Attack / Failure Mode Enumeration / Hidden Assumption Extraction / Devil's Advocate Protocol / All]
Adversarial Severity Score: [X/100] ([Robust / Minor Concerns / Significant / Critical / Fatally Flawed])

## 1. Target Summary
[What is being red-teamed]
[Why it matters]
[Who requested this analysis]
[Scope and constraints]

## 2. Attack Mode: [Selected Mode]

### [Mode-specific content following the methodology above]

[If multiple modes are used, repeat Section 2 for each mode]

## 3. Vulnerabilities Found

### Critical (Score 80-100)
| # | Vulnerability | Attack Mode | Evidence Tier | Evidence | Mitigation Feasibility |
|---|-------------|------------|--------------|---------|----------------------|

### Major (Score 50-79)
| # | Vulnerability | Attack Mode | Evidence Tier | Evidence | Mitigation Feasibility |

### Minor (Score 20-49)
| # | Vulnerability | Attack Mode | Evidence Tier | Evidence | Mitigation Feasibility |

### Cosmetic (Score 0-19)
| # | Vulnerability | Attack Mode | Evidence Tier | Evidence | Mitigation Feasibility |

## 4. Adversarial Severity Score: [X/100]

### Score Breakdown
| Component | Score (0-100) | Weight | Weighted Score | Rationale |
|-----------|-------------|--------|---------------|-----------|
| Vulnerability Count | [X] | 0.30 | [X] | |
| Evidence Quality | [X] | 0.25 | [X] | |
| Mitigation Difficulty | [X] | 0.25 | [X] | |
| Cascading Risk | [X] | 0.20 | [X] | |
| **TOTAL** | | | **[X/100]** | **[Severity Tier]** |

### Interpretation
[What this score means for the target]

## 5. Recommendations

### Must Address Before Proceeding
1. [Vulnerability]: [Specific mitigation action] -- [Cost/effort estimate] -- [Owner]
2. ...

### Should Address
1. [Vulnerability]: [Specific mitigation action] -- [Cost/effort estimate] -- [Owner]
2. ...

### Consider Addressing
1. [Vulnerability]: [Specific mitigation action] -- [Cost/effort estimate] -- [Owner]
2. ...

## 6. Residual Risk Assessment
[After all "Must Address" recommendations are implemented, what risk remains?]
[Are there inherent vulnerabilities that cannot be mitigated?]
[What ongoing monitoring is needed?]

## 7. Cognitive Bias Audit
[Which biases influenced the target? Assess: confirmation bias, optimism bias, sunk cost fallacy, anchoring, groupthink]

## 8. References
[All citations organized by evidence tier: T1 Definitive, T2 Strong, T3 Suggestive, T4 Speculative]
```

---

## Combining Attack Modes

When running all five modes, execute in this order: (1) Hidden Assumption Extraction -> (2) Failure Mode Enumeration -> (3) Steel-Man Attack -> (4) Devil's Advocate Protocol -> (5) Pre-Mortem. Each mode feeds into the next: fragile assumptions become root causes in the pre-mortem, high-risk failure modes become targets for the steel-man attack, and counter-evidence from the steel-man feeds the devil's advocate case.

---

## Completeness Checklist

- [ ] Target clearly defined with scope and success criteria
- [ ] Appropriate attack mode(s) selected and justified
- [ ] At least one attack mode executed completely (all steps followed)
- [ ] Vulnerabilities categorized by severity (Critical / Major / Minor / Cosmetic)
- [ ] Each vulnerability backed by evidence with tier grading (T1-T4)
- [ ] Adversarial Severity Score calculated with component breakdown
- [ ] Recommendations prioritized (Must Address / Should Address / Consider)
- [ ] Residual risk assessment provided (what risk remains after mitigation)
- [ ] Cognitive bias audit performed (which biases may have influenced the target)
- [ ] MCP tools used to gather counter-evidence and validate vulnerabilities
- [ ] All PMIDs verified via `get_article_metadata` (no fabricated citations)
- [ ] Counter-arguments are steel-manned (strongest version, not strawmen)
- [ ] Mitigation actions are specific and actionable (not vague platitudes)
- [ ] Report file created with all sections populated (no remaining placeholders)
- [ ] Visualization code provided for risk heatmap and severity assessment
