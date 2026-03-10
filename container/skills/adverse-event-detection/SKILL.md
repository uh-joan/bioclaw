---
name: adverse-event-detection
description: Adverse drug event signal detection and pharmacovigilance analysis. FAERS signal detection, disproportionality analysis, PRR, ROR, information component, safety signal scoring, post-market surveillance, adverse event reporting. Use when user mentions adverse event detection, FAERS, safety signal, disproportionality, PRR, proportional reporting ratio, reporting odds ratio, ROR, information component, IC, post-market surveillance, drug safety signal, signal detection, pharmacovigilance signal, or adverse event analysis.
---

# Adverse Event Detection

Quantitative signal detection and disproportionality analysis for post-market drug safety surveillance. This skill focuses specifically on mining the FDA FAERS database, computing statistical disproportionality measures (PRR, ROR, IC, EBGM), and generating composite Safety Signal Scores. It is distinct from the pharmacovigilance-specialist skill, which handles broader safety profiling, regulatory reporting timelines, benefit-risk assessment, and PSUR/PBRER preparation. Use this skill when the task requires numerical signal detection, scoring, or quantitative pharmacovigilance analysis.

## Report-First Workflow

1. **Create report file immediately**: `[drug]_adverse_event_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Broad safety profiling, PSUR/PBRER preparation, or benefit-risk frameworks -> use `pharmacovigilance-specialist`
- Drug-drug interaction evaluation and clinical DDI risk -> use `drug-interaction-analyst`
- FDA labeling interpretation, recalls, or regulatory submissions -> use `fda-consultant`
- Chemical or toxicological safety assessment -> use `chemical-safety-toxicology`
- Risk management plans and risk minimization measures -> use `risk-management-specialist`
- Clinical pharmacology or PK/PD modeling -> use `clinical-pharmacology`

## Cross-Reference: Other Skills

- **Broader safety profiling and regulatory reporting** -> use pharmacovigilance-specialist skill
- **Drug-drug interaction evaluation** -> use drug-interaction-analyst skill
- **FDA labeling, recalls, regulatory submissions** -> use fda-consultant skill
- **Chemical/toxicological safety assessment** -> use chemical-safety-toxicology skill
- **Risk management plans and risk-benefit frameworks** -> use risk-management-specialist skill

## Available MCP Tools

### `mcp__fda__fda_info` (FAERS Adverse Events & Drug Labels)

| Call | What it does |
|------|-------------|
| `method: "search_drugs", query: "drug_name"` | Search drugs by name to identify products |
| `method: "get_adverse_events", query: "drug_name"` | Retrieve FAERS adverse event reports for a drug |
| `method: "get_adverse_events", query: "drug_name", count: "patient.reaction.reactionmeddrapt.exact"` | Top adverse reactions by frequency |
| `method: "get_adverse_events", query: "drug_name+AND+serious:1"` | Serious adverse events only |
| `method: "get_adverse_events", query: "drug_name+AND+seriousnessdeath:1"` | Fatal outcome reports |
| `method: "get_adverse_events", query: "drug_name+AND+patient.drug.drugcharacterization:1"` | Suspect drug reports only (exclude concomitants) |
| `method: "get_adverse_events", query: "drug_name+AND+receiptdate:[20230101+TO+20251231]"` | Date-restricted queries for temporal analysis |
| `method: "get_drug_label", query: "drug_name"` | Current prescribing information (warnings, black box) |
| `method: "get_recalls", query: "drug_name"` | Recall history |

**Counting dimensions for disproportionality:**

| Count field | Use |
|-------------|-----|
| `count: "patient.reaction.reactionmeddrapt.exact"` | Reaction frequency (build 2x2 table rows) |
| `count: "patient.drug.medicinalproduct.exact"` | Co-reported drugs (confounder screening) |
| `count: "patient.patientsex"` | Sex stratification |
| `count: "receiptdate"` | Temporal trend (signal emergence timing) |

### `mcp__drugbank__drugbank_info` (Drug Pharmacology)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_by_name` | Find drug by name, get DrugBank ID | `query` |
| `get_drug_details` | Mechanism of action, pharmacodynamics, toxicity, targets | `drugbank_id` |
| `get_drug_interactions` | Known drug-drug interactions | `drugbank_id` |
| `search_by_target` | Other drugs acting on same target (class effect analysis) | `target` |
| `get_similar_drugs` | Pharmacologically similar drugs for class-wide signal check | `drugbank_id` |

### `mcp__opentargets__opentargets_info` (Target-Disease Associations)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Find molecular targets by name | `query` |
| `get_target_disease_associations` | Disease associations for a target (biological plausibility) | `target_id` |
| `get_target_details` | Target function, pathways, expression | `target_id` |

### `mcp__pubmed__pubmed_articles` (Literature Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search for case reports, reviews | `keywords`, `num_results` |
| `search_advanced` | Filtered search by journal, date range | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article metadata for a known PMID | `pmid` |

### `mcp__clinpgx__clinpgx_data` (Pharmacogenomic ADE Risk)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_clinical_annotations` | PGx-related adverse drug event risk annotations | `gene`, `drug` |
| `get_gene_drug_pairs` | Gene-drug interactions that may cause ADEs | `gene`, `drug` |
| `search_variants` | PGx variants associated with adverse events | `query`, `limit` |

**ClinPGx workflow:** Check ClinPGx for pharmacogenomic variants that increase risk of adverse drug events.

```
1. mcp__clinpgx__clinpgx_data(method: "get_gene_drug_pairs", gene: "CYP2D6", drug: "DRUG_NAME")
   → Identify gene-drug pairs with known ADE risk

2. mcp__clinpgx__clinpgx_data(method: "get_clinical_annotations", gene: "CYP2D6", drug: "DRUG_NAME")
   → Clinical annotations linking PGx variants to adverse outcomes

3. mcp__clinpgx__clinpgx_data(method: "search_variants", query: "DRUG_NAME adverse")
   → Search for PGx variants associated with drug-specific adverse events
```

### `mcp__chembl__chembl_info` (Mechanism & Bioactivity)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search compounds by name or structure | `query` |
| `get_mechanism` | Mechanism of action with target details | `chembl_id` |
| `get_bioactivity` | Binding affinity, IC50 for on/off-target effects | `chembl_id`, `target_id` |

### `mcp__hmdb__hmdb_data` (Metabolite-Associated Adverse Event Patterns)

Use HMDB to identify metabolites associated with adverse event patterns, check whether altered metabolite concentrations correlate with reported adverse events, and investigate metabolite-disease links that may explain AE signals. Note: HMDB uses Cloudflare protection so some requests may be blocked intermittently.

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_metabolites` | Search for metabolites linked to observed adverse events | `query` (required), `limit` (optional, default 25) |
| `get_metabolite` | Full metabolite profile including disease associations and biofluid locations | `hmdb_id` (required) |
| `get_metabolite_diseases` | Disease associations with OMIM IDs — link metabolite perturbations to AE mechanisms | `hmdb_id` (required) |
| `get_metabolite_concentrations` | Normal and abnormal concentration data — detect AE-correlated metabolite shifts | `hmdb_id` (required) |
| `get_metabolite_pathways` | Biological pathways — identify metabolic disruptions underlying adverse events | `hmdb_id` (required) |

---

## Python Environment

The container has `scipy`, `statsmodels`, `pandas`, and `numpy` available for statistical calculations. Run Python code via the Bash tool.

---

## Signal Detection Pipeline

### Phase 1: Drug & Event Identification

**Step 1a: Identify the drug and retrieve top adverse reactions**

```
mcp__fda__fda_info(method: "search_drugs", query: "atorvastatin")

mcp__fda__fda_info(
  method: "get_adverse_events",
  query: "atorvastatin",
  count: "patient.reaction.reactionmeddrapt.exact",
  limit: 100
)
```

**Step 1b: Retrieve background rates (all drugs) for the 2x2 table**

```
mcp__fda__fda_info(
  method: "get_adverse_events",
  query: "",
  count: "patient.reaction.reactionmeddrapt.exact",
  limit: 1000
)
```

**Step 1c: Event term standardization (MedDRA)**

FAERS uses MedDRA Preferred Terms (PTs). Always check related PTs within the same HLT/HLGT to avoid missing grouped signals. For example, "Rhabdomyolysis", "Myalgia", "Blood creatine phosphokinase increased", and "Myopathy" all fall under musculoskeletal SOC and may represent a single muscle-injury signal.

**Step 1d: Filter to suspect drug reports only**

```
mcp__fda__fda_info(
  method: "get_adverse_events",
  query: "patient.drug.medicinalproduct:atorvastatin+AND+patient.drug.drugcharacterization:1",
  count: "patient.reaction.reactionmeddrapt.exact",
  limit: 100
)
```

`drugcharacterization:1` = suspect, 2 = concomitant, 3 = interacting.

---

### Phase 2: Disproportionality Analysis

**2x2 Table:**

|  | Event E | All other events | Total |
|--|---------|-----------------|-------|
| **Drug D** | a | c | a+c |
| **All other drugs** | b | d | b+d |

**Python template -- PRR:**

```python
import numpy as np
from scipy import stats

def calculate_prr(a, b, c, d):
    """Proportional Reporting Ratio. Signal: PRR >= 2, chi2 >= 4, a >= 3"""
    if a == 0 or (a + b) == 0 or (c + d) == 0:
        return {"prr": None, "signal": False, "reason": "insufficient data"}
    prr = (a / (a + c)) / (b / (b + d))
    se_log = np.sqrt(1/a - 1/(a+c) + 1/b - 1/(b+d))
    ci = (np.exp(np.log(prr) - 1.96*se_log), np.exp(np.log(prr) + 1.96*se_log))
    chi2_val, p_val, _, _ = stats.chi2_contingency([[a,b],[c,d]], correction=True)
    return {
        "prr": round(prr, 3), "ci_95": (round(ci[0],3), round(ci[1],3)),
        "chi2": round(chi2_val, 3), "p_value": round(p_val, 6),
        "case_count": a, "signal": (prr >= 2) and (chi2_val >= 4) and (a >= 3),
    }
```

**Python template -- ROR:**

```python
def calculate_ror(a, b, c, d):
    """Reporting Odds Ratio. Signal: lower 95% CI > 1"""
    if 0 in (a, b, c, d):
        a, b, c, d = a+0.5, b+0.5, c+0.5, d+0.5  # continuity correction
    ror = (a * d) / (b * c)
    se_log = np.sqrt(1/a + 1/b + 1/c + 1/d)
    ci_lower = np.exp(np.log(ror) - 1.96*se_log)
    ci_upper = np.exp(np.log(ror) + 1.96*se_log)
    return {
        "ror": round(ror, 3), "ci_95": (round(ci_lower,3), round(ci_upper,3)),
        "signal": ci_lower > 1,
    }
```

**Python template -- IC (Information Component):**

```python
def calculate_ic(a, b, c, d):
    """Information Component (WHO-UMC Bayesian). Signal: IC025 > 0"""
    n = a + b + c + d
    expected = ((a + c) * (a + b)) / n if n > 0 else 0
    if expected == 0:
        return {"ic": None, "signal": False}
    obs = max(a, 0.5)
    ic = np.log2(obs / expected)
    se_ic = np.sqrt(1 / (obs * (np.log(2)**2)))
    ic025 = ic - 1.96 * se_ic
    return {
        "ic": round(ic, 4), "ic025": round(ic025, 4),
        "observed": a, "expected": round(expected, 2),
        "signal": ic025 > 0,
    }
```

**Python template -- EBGM approximation:**

```python
def calculate_ebgm(a, b, c, d, alpha1=0.2, beta1=0.1, alpha2=2.0, beta2=4.0, w=0.1):
    """Simplified EBGM (two-component Gamma-Poisson). Signal: EB05 >= 2"""
    from scipy.special import gammaln
    from scipy.stats import gamma as gdist
    from scipy.optimize import brentq

    n = a + b + c + d
    expected = ((a + c) * (a + b)) / n if n > 0 else 0
    if expected == 0:
        return {"ebgm": None, "signal": False}

    def lm(obs, exp, al, be):
        return gammaln(al+obs) - gammaln(al) + al*np.log(be/(be+exp)) + obs*np.log(exp/(be+exp))

    lm1, lm2 = lm(a, expected, alpha1, beta1), lm(a, expected, alpha2, beta2)
    mx = max(lm1, lm2)
    q1, q2 = w*np.exp(lm1-mx), (1-w)*np.exp(lm2-mx)
    w1 = q1 / (q1+q2)
    ebgm = w1*(alpha1+a)/(beta1+expected) + (1-w1)*(alpha2+a)/(beta2+expected)

    def mix_cdf(x):
        return w1*gdist.cdf(x,alpha1+a,scale=1/(beta1+expected)) + (1-w1)*gdist.cdf(x,alpha2+a,scale=1/(beta2+expected))
    try:
        eb05 = brentq(lambda x: mix_cdf(x)-0.05, 1e-10, ebgm*10)
    except Exception:
        eb05 = None
    return {"ebgm": round(ebgm,3), "eb05": round(eb05,3) if eb05 else None, "signal": eb05 is not None and eb05 >= 2}
```

**Run all measures:**

```python
def run_disproportionality(a, b, c, d, drug, event):
    prr = calculate_prr(a, b, c, d)
    ror = calculate_ror(a, b, c, d)
    ic = calculate_ic(a, b, c, d)
    ebgm = calculate_ebgm(a, b, c, d)
    any_signal = prr["signal"] or ror["signal"] or ic["signal"] or ebgm["signal"]
    print(f"Signal analysis: {drug} <-> {event}")
    print(f"  PRR={prr['prr']} CI={prr.get('ci_95')} chi2={prr.get('chi2')} signal={prr['signal']}")
    print(f"  ROR={ror['ror']} CI={ror['ci_95']} signal={ror['signal']}")
    print(f"  IC={ic['ic']} IC025={ic.get('ic025')} signal={ic['signal']}")
    print(f"  EBGM={ebgm['ebgm']} EB05={ebgm.get('eb05')} signal={ebgm['signal']}")
    print(f"  Any signal: {any_signal}")
    return {"drug": drug, "event": event, "prr": prr, "ror": ror, "ic": ic, "ebgm": ebgm, "any_signal": any_signal}
```

---

### Phase 3: Signal Prioritization

Combine statistical evidence with clinical context into a Safety Signal Score (0-100).

**Score components:**
1. Disproportionality strength (0-30): PRR magnitude (0-10), ROR CI lower (0-8), IC025 (0-6), EB05 (0-6)
2. Case count and seriousness (0-25): case count (0-10), serious proportion (0-10), fatalities (0-5)
3. Temporal pattern (0-10): onset timing consistent with drug exposure
4. Biological plausibility (0-15): mechanism explains the event
5. Literature support (0-15): none=0, case_reports=5, series=10, systematic_review=15
6. Novelty (0-5): unlabeled event gets bonus

**Python template:**

```python
def safety_signal_score(prr_r, ror_r, ic_r, ebgm_r, case_count, serious_pct,
                        fatal_n, temporal_ok, mech_plausible, lit_level, labeled):
    s = 0.0
    # Disproportionality (0-30)
    d = 0.0
    if prr_r.get("prr"):
        d += min(10, {10:10,5:7,2:4,1.5:2}.get(next((k for k in [10,5,2,1.5] if prr_r["prr"]>=k),0),0))
    if ror_r.get("ci_95"):
        cl = ror_r["ci_95"][0]
        d += 8 if cl>=5 else 5 if cl>=2 else 3 if cl>=1 else 0
    if ic_r.get("ic025") is not None:
        d += 6 if ic_r["ic025"]>=2 else 4 if ic_r["ic025"]>=1 else 2 if ic_r["ic025"]>0 else 0
    if ebgm_r.get("eb05") is not None:
        d += 6 if ebgm_r["eb05"]>=5 else 4 if ebgm_r["eb05"]>=2 else 2 if ebgm_r["eb05"]>=1 else 0
    s += min(d, 30)
    # Cases (0-25)
    c = (10 if case_count>=100 else 7 if case_count>=50 else 5 if case_count>=20 else 3 if case_count>=5 else 1 if case_count>=3 else 0)
    c += serious_pct * 10
    c += 5 if fatal_n>=10 else 3 if fatal_n>=3 else 1 if fatal_n>=1 else 0
    s += min(c, 25)
    # Temporal, plausibility, literature, novelty
    s += 10 if temporal_ok else 0
    s += 15 if mech_plausible else 0
    s += {"none":0,"case_reports":5,"series":10,"systematic_review":15}.get(lit_level, 0)
    s += 5 if not labeled else 0
    s = min(round(s, 1), 100)
    cls = "HIGH PRIORITY" if s>=75 else "MODERATE" if s>=50 else "LOW" if s>=25 else "MINIMAL"
    return {"score": s, "classification": cls}
```

**Classification thresholds:**
- 75-100: HIGH PRIORITY -- immediate review recommended
- 50-74: MODERATE -- scheduled review recommended
- 25-49: LOW -- monitor and re-evaluate
- 0-24: MINIMAL -- no action at this time

---

### Phase 4: Mechanism-Based Analysis

Determine whether the event is on-target or off-target; check for class effects.

**Step 4a: Drug mechanism**

```
mcp__drugbank__drugbank_info(method: "search_by_name", query: "atorvastatin")
   -> extract drugbank_id (e.g., DB01076)

mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DB01076")
   -> mechanism of action, targets, pharmacodynamics
```

**Step 4b: Target-disease associations (biological plausibility)**

```
mcp__opentargets__opentargets_info(method: "search_targets", query: "HMGCR")
   -> get target_id (e.g., ENSG00000113161)

mcp__opentargets__opentargets_info(
  method: "get_target_disease_associations",
  target_id: "ENSG00000113161"
)
   -> does the AE match a known target-disease association?
```

**Step 4c: Off-target binding via ChEMBL**

```
mcp__chembl__chembl_info(method: "compound_search", query: "atorvastatin")
   -> get chembl_id (e.g., CHEMBL1487)

mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "CHEMBL1487")
   -> off-target hits with low IC50 values may explain unexpected AEs
```

**Step 4d: Class effect**

```
mcp__drugbank__drugbank_info(method: "search_by_target", target: "HMGCR")
   -> all drugs on the same target

mcp__drugbank__drugbank_info(method: "get_similar_drugs", drugbank_id: "DB01076")
   -> pharmacologically similar drugs
```

For each class member, repeat Phase 2 for the same event. Signal across all members indicates a class effect.

---

### Phase 5: Literature Corroboration

**Step 5a: Case reports**

```
mcp__pubmed__pubmed_articles(
  method: "search_keywords",
  keywords: "atorvastatin rhabdomyolysis case report",
  num_results: 20
)
```

**Step 5b: Systematic reviews**

```
mcp__pubmed__pubmed_articles(
  method: "search_advanced",
  term: "atorvastatin rhabdomyolysis systematic review OR meta-analysis",
  start_date: "2018/01/01",
  num_results: 15
)
```

**Step 5c: Pharmacoepidemiology literature**

```
mcp__pubmed__pubmed_articles(
  method: "search_advanced",
  term: "atorvastatin disproportionality FAERS",
  journal: "Drug Safety",
  num_results: 10
)
```

**Step 5d: Article details**

```
mcp__pubmed__pubmed_articles(method: "get_article_metadata", pmid: "12345678")
```

---

### Phase 6: Signal Assessment Report

**Output format:**

```
## Signal Assessment Report

### Drug-Event Pair
- Drug: [name] ([DrugBank ID])
- Adverse Event: [MedDRA PT] (SOC: [System Organ Class])
- Assessment Date: [date]

### Executive Summary
[1-2 sentences with Safety Signal Score and classification]

### 1. FAERS Data Summary
- Total reports (drug): [n]
- Reports with this event: [a]
- Suspect drug only: [n]
- Serious: [n] ([%])
- Fatal: [n]

### 2. Disproportionality Measures
| Measure | Value | 95% CI | Threshold | Signal? |
|---------|-------|--------|-----------|---------|
| PRR | [val] | [CI] | >= 2, chi2 >= 4, n >= 3 | [Yes/No] |
| ROR | [val] | [CI] | Lower CI > 1 | [Yes/No] |
| IC | [val] | IC025=[val] | IC025 > 0 | [Yes/No] |
| EBGM | [val] | EB05=[val] | EB05 >= 2 | [Yes/No] |

### 3. Safety Signal Score
- **Score: [0-100] -- [Classification]**
- Breakdown: disproportionality [x/30], cases [x/25], temporal [x/10],
  plausibility [x/15], literature [x/15], novelty [x/5]

### 4. Mechanism Analysis
- Primary target: [name]
- On-target / off-target: [assessment]
- Class effect: [Yes/No]

### 5. Literature Evidence
- Case reports: [n], Systematic reviews: [n]
- Key references: [citations]

### 6. Recommendation
[Continue monitoring / update label / initiate formal review / etc.]
```

---

## Disproportionality Measures Reference

### PRR (Proportional Reporting Ratio)

```
PRR = (a / (a + c)) / (b / (b + d))
Signal: PRR >= 2  AND  chi-squared >= 4  AND  N >= 3  (Evans et al.)
Strengths: Simple, intuitive, widely used
Limitations: Sensitive to masking, no sparse-data correction
```

### ROR (Reporting Odds Ratio)

```
ROR = (a * d) / (b * c)
Signal: Lower bound of 95% CI > 1
Strengths: Analogous to case-control OR, continuity correction available
Limitations: Unstable with small counts
```

### IC (Information Component)

```
IC = log2(observed / expected)   where expected = ((a+c)*(a+b)) / N
Signal: IC025 (lower 95% credibility bound) > 0
Used by: WHO Uppsala Monitoring Centre
Strengths: Bayesian shrinkage for rare events
```

### EBGM (Empirical Bayes Geometric Mean)

```
EBGM = posterior mean of relative reporting rate (Gamma-Poisson shrinkage)
Signal: EB05 (5th percentile) >= 2
Used by: FDA (MGPS method for FAERS)
Strengths: Best sparse-data handling, database-wide calibration
```

### Threshold Comparison

| Measure | Minimum | Strong | Very strong |
|---------|---------|--------|-------------|
| PRR | >= 2 | >= 5 | >= 10 |
| ROR (CI lower) | > 1 | > 2 | > 5 |
| IC025 | > 0 | > 1 | > 2 |
| EB05 | >= 2 | >= 5 | >= 10 |

---

## Signal Classification Framework

### Confirmed Signal
- 3-4 of 4 measures positive, Score >= 75
- Biological plausibility established, supporting literature (series or review)
- Action: Update label, safety communication, consider REMS

### Potential Signal
- At least one measure positive, Score 50-74
- Plausible mechanism, limited literature (case reports)
- Action: Initiate targeted review, request additional data

### Refuted Signal
- Statistical signal explained by confounding (protopathic bias, channeling bias, notoriety bias)
- No biological plausibility after investigation
- Action: Document rationale, close with justification

### Unclassifiable
- Insufficient data, conflicting measures, unclear mechanism
- Action: Flag for re-evaluation, request more data

---

## MedDRA Hierarchy Concepts

```
Level 1: SOC  (System Organ Class)         ~27 classes
Level 2: HLGT (High Level Group Term)      ~337 terms
Level 3: HLT  (High Level Term)            ~1,737 terms
Level 4: PT   (Preferred Term)             ~24,000+ terms   <- FAERS uses this
Level 5: LLT  (Lowest Level Term)          ~80,000+ terms
```

**Example (hepatotoxicity):**

```
SOC:  Hepatobiliary disorders
  HLGT: Hepatocellular damage and hepatitis NEC
    HLT: Hepatocellular injury and hepatitis NEC
      PT: Drug-induced liver injury
        LLT: Hepatotoxicity due to drug
      PT: Hepatitis
      PT: Hepatic failure
        LLT: Acute hepatic failure
```

**Grouping strategy:**
- **Narrow**: Single PT for specificity
- **Broad**: All PTs under an HLT or HLGT
- **SMQ**: Standardised MedDRA Queries for common safety topics (e.g., "Drug related hepatic disorders" covers ~130 PTs)

Always report which hierarchy level was used in the assessment.

---

## Evidence Grading

| Grade | Label | Criteria |
|-------|-------|----------|
| A | Definitive | RCT evidence, consistent disproportionality, labeled, mechanism proven |
| B | Strong | Multiple measures positive, case series published, mechanism plausible |
| C | Moderate | At least one measure positive, case reports exist, mechanism possible |
| D | Weak | Single measure marginally positive, anecdotal reports, mechanism unclear |
| E | Insufficient | No statistical signal, no published evidence |

---

## Multi-Agent Workflow Examples

**"Detect signals for a newly approved drug"**
1. Adverse Event Detection (this skill) -> mine FAERS, calculate disproportionality, generate Safety Signal Scores
2. Pharmacovigilance Specialist -> regulatory context, labeled events, reporting requirements
3. Drug Interaction Analyst -> evaluate interaction-mediated signals

**"Investigate a specific adverse event cluster"**
1. Adverse Event Detection (this skill) -> quantify signal (PRR, ROR, IC, EBGM), stratify by demographics
2. Pharmacovigilance Specialist -> regulatory actions, PSUR history, benefit-risk
3. FDA Consultant -> label status, recall history, pending actions

**"Compare safety signals between two class members"**
1. Adverse Event Detection (Agent 1) -> disproportionality analysis for Drug A
2. Adverse Event Detection (Agent 2) -> disproportionality analysis for Drug B
3. Lead Agent -> head-to-head comparison, shared class signals vs. drug-specific

**"Evaluate whether a signal is a class effect"**
1. Adverse Event Detection (this skill) -> disproportionality for index drug and all class members
2. Chemical Safety Toxicology -> off-target toxicity profiles, structural alerts
3. Drug Interaction Analyst -> rule out interaction-mediated signals

**"Screen for new unlabeled signals"**
1. Adverse Event Detection (this skill) -> top 100 FAERS events, disproportionality for each, filter unlabeled with Score >= 50
2. Pharmacovigilance Specialist -> formal signal assessment for flagged pairs
3. Risk Management Specialist -> risk minimization measures for confirmed signals

## Completeness Checklist

- [ ] Report file created with all section headers and placeholders populated
- [ ] FAERS data retrieved for the drug-event pair (total reports, serious, fatal)
- [ ] All four disproportionality measures computed (PRR, ROR, IC, EBGM) with confidence intervals
- [ ] 2x2 contingency table constructed with background rates
- [ ] Safety Signal Score calculated with component breakdown
- [ ] Mechanism analysis performed (on-target vs. off-target, class effect assessment)
- [ ] Drug label checked for whether the event is already labeled
- [ ] Literature corroboration completed (case reports, systematic reviews)
- [ ] Signal classified (Confirmed / Potential / Refuted / Unclassifiable)
- [ ] Evidence grade assigned (A-E) with supporting rationale
