---
name: pharmacovigilance-specialist
description: Pharmacovigilance and drug safety specialist. Adverse event signal detection, safety signal investigation, drug-drug interactions, FAERS analysis, benefit-risk assessment, safety reporting (PSUR/PBRER/IND safety). Use when user mentions adverse events, drug safety, FAERS, pharmacovigilance, safety signal, drug interaction, side effects, MedWatch, PSUR, PBRER, risk management plan, or REMS.
---

# Pharmacovigilance Specialist

Drug safety monitoring, adverse event analysis, and signal detection. Uses three MCP servers for comprehensive safety intelligence.

## Report-First Workflow

1. **Create report file immediately**: `[drug]_pharmacovigilance_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- FDA regulatory submissions, recalls, or approval status queries → use `fda-consultant`
- EU safety reviews, referrals, DHPCs, or PSUSAs → use `mdr-745-consultant`
- Clinical trial safety data extraction and analysis → use `clinical-trial-analyst`
- QMS CAPA processes triggered by safety findings → use `iso-13485-consultant`
- Adverse event detection in clinical notes or narratives → use `adverse-event-detection`
- Drug-drug interaction pharmacology without safety signal context → use `clinical-pharmacology`

## Available MCP Tools

### `mcp__fda__fda_info` (FDA Adverse Events & Recalls)

| Call | What it does |
|------|-------------|
| `method: "lookup_drug", search_type: "adverse_events"` | FAERS database — adverse event reports |
| `method: "lookup_drug", search_type: "adverse_events", count: "patient.reaction.reactionmeddrapt.exact"` | Top adverse reactions by frequency |
| `method: "lookup_drug", search_type: "adverse_events", count: "patient.patientsex"` | Demographic breakdown |
| `method: "lookup_drug", search_type: "recalls"` | Drug recall history |
| `method: "lookup_drug", search_type: "shortages"` | Drug shortage tracking |
| `method: "lookup_drug", search_type: "label"` | Prescribing info (warnings, boxed warnings) |
| `method: "lookup_device", search_type: "device_adverse_events"` | Device adverse events (MDR reports) |

**Advanced FAERS queries:**
- Serious events: `search_term: "drugname+AND+serious:1"`
- Deaths: `search_term: "drugname+AND+seriousnessdeath:1"`
- By age: `search_term: "drugname+AND+patient.patientonsetage:[65+TO+*]"`
- By country: `search_term: "drugname+AND+occurcountry:US"`
- Date range: `search_term: "drugname+AND+receiptdate:[20230101+TO+20241231]"`
- Suspect drug only: `search_term: "patient.drug.medicinalproduct:drugname+AND+patient.drug.drugcharacterization:1"`

### `mcp__drugbank__drugbank_info` (Drug Pharmacology & Interactions)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_by_name` | Find drug by name | `query` |
| `get_drug_details` | Full drug profile (pharmacology, toxicity, mechanism) | `drugbank_id` |
| `get_drug_interactions` | All drug-drug interactions | `drugbank_id` |
| `search_by_target` | Drugs acting on same target | `target` |
| `get_similar_drugs` | Similar drugs (shared targets/categories) | `drugbank_id` |
| `get_pathways` | Metabolic pathways | `drugbank_id` |
| `search_by_indication` | Drugs for same indication | `query` |
| `search_by_carrier` | Drugs using same carrier protein | `carrier` |
| `search_by_transporter` | Drugs using same transporter | `transporter` |
| `get_products` | Market products, FDA approval status | `drugbank_id`, `country` |

### `mcp__pubmed__pubmed_articles` (Safety Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__ema__ema_info` (EU Safety Data)

| Method | What it does |
|--------|-------------|
| `get_referrals` | EU-wide safety reviews |
| `get_dhpcs` | Direct Healthcare Professional Communications |
| `get_psusas` | Periodic Safety Update Single Assessments |
| `get_supply_shortages` | EU supply shortage data |

### `mcp__hmdb__hmdb_data` (Metabolite Safety Signal Investigation)

Use HMDB to investigate metabolite-level safety signals by checking whether drug-related metabolite perturbations correlate with known disease associations, and to retrieve reference concentration ranges for safety biomarker assessment. Note: HMDB uses Cloudflare protection so some requests may be blocked intermittently.

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_metabolites` | Search for metabolites implicated in safety signals | `query` (required), `limit` (optional, default 25) |
| `get_metabolite` | Full metabolite profile including disease associations and biofluid locations | `hmdb_id` (required) |
| `get_metabolite_diseases` | Disease associations with OMIM IDs — link metabolite changes to safety signals | `hmdb_id` (required) |
| `get_metabolite_concentrations` | Normal and abnormal concentration data — establish safety reference intervals | `hmdb_id` (required) |
| `get_metabolite_pathways` | Biological pathways — trace metabolic disruptions driving safety concerns | `hmdb_id` (required) |

---

## Signal Detection Methodology

### Disproportionality Analysis

Quantify whether an adverse event is reported more frequently for a drug than expected.

**Proportional Reporting Ratio (PRR):**
```
PRR = (a / (a+b)) / (c / (c+d))

Where:
a = reports of event E with drug D
b = reports of event E with all other drugs
c = reports of all other events with drug D
d = reports of all other events with all other drugs

Signal threshold: PRR >= 2, chi-squared >= 4, N >= 3
```

**Reporting Odds Ratio (ROR):**
```
ROR = (a * d) / (b * c)

Signal threshold: lower bound of 95% CI > 1
```

**Multi-Item Gamma Poisson Shrinker (MGPS):**
Used by FDA. Bayesian approach that handles sparse data better than frequentist methods.

### Signal Prioritization

After detecting a signal, prioritize by:

1. **Seriousness** — Death > life-threatening > hospitalization > disability
2. **Strength of association** — Higher PRR/ROR = stronger signal
3. **Biological plausibility** — Does the mechanism explain it?
4. **Temporal relationship** — Onset timing consistent with drug exposure?
5. **Dose-response** — Higher dose = more events?
6. **Dechallenge/Rechallenge** — Did it stop/recur when drug stopped/restarted?
7. **Novelty** — Is this a NEW signal not in the label?

---

## Safety Investigation Workflow

### Step 1: Characterize the Signal

```
1. mcp__fda__fda_info(method: "lookup_drug", search_term: "drug_name", search_type: "adverse_events", count: "patient.reaction.reactionmeddrapt.exact", limit: 25)
   → Top 25 adverse reactions

2. mcp__fda__fda_info(method: "lookup_drug", search_term: "drug_name+AND+patient.reaction.reactionmeddrapt:EVENT_NAME", search_type: "adverse_events", limit: 50)
   → Detailed case reports for the specific event

3. mcp__fda__fda_info(method: "lookup_drug", search_term: "drug_name+AND+serious:1", search_type: "adverse_events", count: "patient.reaction.reactionmeddrapt.exact", limit: 25)
   → Serious events only
```

### Step 2: Assess Pharmacological Plausibility

```
1. mcp__drugbank__drugbank_info(method: "search_by_name", query: "drug_name")
   → Get DrugBank ID

2. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   → Mechanism of action, pharmacodynamics, toxicity

3. mcp__drugbank__drugbank_info(method: "get_drug_interactions", drugbank_id: "DBxxxxx")
   → Drug-drug interactions that may contribute

4. mcp__drugbank__drugbank_info(method: "search_by_target", target: "target_protein")
   → Other drugs hitting same target (class effect?)
```

### Step 3: Review Literature Evidence

```
1. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "drug_name adverse_event case report", num_results: 20)
   → Published case reports

2. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "drug_name safety", journal: "Drug Safety", start_date: "2020/01/01", num_results: 10)
   → Recent safety publications

3. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "drug_name meta-analysis safety", num_results: 10)
   → Meta-analyses of safety data
```

### Step 4: Check Regulatory Actions

```
1. mcp__fda__fda_info(method: "lookup_drug", search_term: "drug_name", search_type: "recalls")
   → US recall history

2. mcp__fda__fda_info(method: "lookup_drug", search_term: "drug_name", search_type: "label")
   → Current label warnings (boxed warnings, contraindications)

3. mcp__ema__ema_info(method: "get_referrals", active_substance: "drug_name", safety: true)
   → EU safety referrals

4. mcp__ema__ema_info(method: "get_dhpcs", active_substance: "drug_name")
   → EU safety communications to HCPs

5. mcp__ema__ema_info(method: "get_psusas", active_substance: "drug_name")
   → EU periodic safety assessments
```

### Step 5: Assess Class Effect

```
1. mcp__drugbank__drugbank_info(method: "get_similar_drugs", drugbank_id: "DBxxxxx")
   → Find pharmacologically similar drugs

2. For each similar drug, repeat Step 1 FAERS analysis
   → Compare adverse event profiles across the class

3. mcp__drugbank__drugbank_info(method: "search_by_target", target: "shared_target")
   → All drugs hitting the same target
```

---

## Safety Reporting Requirements

### FDA Requirements

| Report Type | When | Timeline |
|-------------|------|----------|
| **IND Safety Report** (21 CFR 312.32) | Unexpected serious suspected ADR | 15 calendar days (7 for fatal/life-threatening) |
| **NDA/BLA Field Alert** (21 CFR 314.81) | Product quality issue | 3 business days |
| **NDA/BLA Periodic Report** | Routine safety update | Quarterly (year 1-3), annually (after) |
| **MedWatch 3500A** (mandatory) | Serious ADR from manufacturer | 15 calendar days |
| **REMS Assessment** | If REMS required | Per approved REMS timetable |

### EU Requirements

| Report Type | When | Timeline |
|-------------|------|----------|
| **Expedited Report (EudraVigilance)** | Serious unexpected ADR in EU | 15 days (7 for fatal/life-threatening) |
| **PSUR/PBRER** | Periodic safety review | Per EU reference dates (EURD list) |
| **Signal Detection** | Ongoing screening | Continuous (EudraVigilance data) |
| **Risk Management Plan (RMP)** | At authorization and updates | With application, then upon request |
| **DHPC** | New safety information for HCPs | Approved by PRAC before dissemination |

### ICH E2E Pharmacovigilance Planning

Risk categorization:
- **Identified risks**: Adverse reactions confirmed by evidence
- **Potential risks**: Suspected but not confirmed
- **Missing information**: Gaps in knowledge (pediatric use, pregnancy, long-term, etc.)

---

## Benefit-Risk Assessment Framework

### ICH E2C(R2) PBRER Structure

1. Introduction
2. Worldwide Marketing Authorization Status
3. Actions Taken for Safety Reasons
4. Changes to Reference Safety Information
5. Estimated Exposure (patient-years)
6. Data in Summary Tabulations (line listings)
7. Summaries of Significant Safety Findings
8. Signal and Risk Evaluation
9. Benefit Evaluation
10. Integrated Benefit-Risk Analysis
11. Conclusions and Actions

### Benefit-Risk Matrix

| | Favorable benefit | Unfavorable benefit |
|---|---|---|
| **Favorable risk** | Continue marketing | Restrict indication |
| **Unfavorable risk** | Add warnings / REMS | Consider withdrawal |

---

## Drug Interaction Assessment

### CYP450 Interaction Categories

| CYP Enzyme | Major Substrates | Common Inhibitors | Common Inducers |
|------------|-----------------|-------------------|-----------------|
| CYP3A4 | Statins, immunosuppressants, many oncology drugs | Ketoconazole, ritonavir, grapefruit | Rifampin, carbamazepine, St. John's wort |
| CYP2D6 | Codeine, tamoxifen, many antidepressants | Fluoxetine, paroxetine, bupropion | None clinically significant |
| CYP2C19 | Clopidogrel, PPIs, some antidepressants | Omeprazole, fluvoxamine | Rifampin |
| CYP2C9 | Warfarin, phenytoin, NSAIDs | Fluconazole, amiodarone | Rifampin |
| CYP1A2 | Theophylline, caffeine, tizanidine | Fluvoxamine, ciprofloxacin | Smoking, charbroiled food |

### Investigation Workflow

```
1. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   → Get metabolism enzymes, transporters

2. mcp__drugbank__drugbank_info(method: "get_drug_interactions", drugbank_id: "DBxxxxx")
   → All known DDIs

3. mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   → Metabolic pathways (identify shared pathways with co-medications)

4. mcp__drugbank__drugbank_info(method: "search_by_transporter", transporter: "P-glycoprotein")
   → Other drugs competing for same transporter
```

---

## Multi-Agent Workflow Examples

**"Investigate reports of liver injury with Drug X"**
1. Pharmacovigilance Specialist → FAERS hepatotoxicity data, DrugBank mechanism/interactions, literature case reports, EU referrals
2. Clinical Trial Analyst → search for terminated trials (hepatotoxicity), published trial safety data
3. FDA Consultant → check label warnings, recall history

**"Compare safety profiles of two competing drugs"**
1. Pharmacovigilance Specialist (Agent 1) → full safety workup for Drug A
2. Pharmacovigilance Specialist (Agent 2) → full safety workup for Drug B
3. Lead Agent → synthesize head-to-head comparison

**"Prepare a PBRER for our product"**
1. Pharmacovigilance Specialist → FAERS data, literature safety review, EU PSUSA history, drug interactions
2. FDA Consultant → US label changes, recall history, shortage status
3. MDR 745 Consultant → EU referrals, DHPCs, post-authorization procedures

## Completeness Checklist

- [ ] FAERS adverse event data queried and top reactions characterized
- [ ] Disproportionality analysis performed (PRR/ROR calculated where data permits)
- [ ] DrugBank pharmacological mechanism reviewed for biological plausibility
- [ ] Drug-drug interactions assessed via DrugBank
- [ ] PubMed literature searched for published case reports and safety meta-analyses
- [ ] FDA label warnings and recall history checked
- [ ] EU safety data reviewed (EMA referrals, DHPCs, PSUSAs)
- [ ] Signal prioritization applied (seriousness, strength, novelty)
- [ ] Class effect assessed using similar drugs and shared-target analysis
- [ ] Report file verified with no remaining `[Analyzing...]` placeholders
