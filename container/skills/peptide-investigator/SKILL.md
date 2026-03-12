---
name: peptide-investigator
description: "Investigate peptide health claims from Reddit and other sources. Use when a user explicitly asks to investigate, fact-check, or evaluate a peptide claim — phrases like 'investigate this', 'is this legit', 'check this claim', 'is X safe for Y', 'should I try X for Y'. Runs a full 7-step biomedical investigation using MCP servers."
---

# Peptide Investigator

Investigate peptide health claims using biomedical databases. Turn anecdotal Reddit claims into structured, evidence-based assessments.

## When to Use

ONLY when a user **explicitly** asks you to investigate a peptide claim. Look for phrases like:
- "investigate this"
- "is this legit"
- "check this claim"
- "is [peptide] safe for [condition]"
- "should I try [peptide] for [condition]"
- "someone said [peptide] helps with [condition]"

Do NOT auto-trigger on casual mention of peptides in conversation.

## Step 1: Extract the Claim

From the user's message, identify:
1. **Compound** — the peptide (BPC-157, tirzepatide, GHK-Cu, semax, TB-500, etc.)
2. **Condition/goal** — what it's claimed to help (ACL recovery, weight loss, brain fog, sleep, inflammation, etc.)

If either is unclear, ask the user to clarify before proceeding.

## Step 2: Run the 7-Step Investigation

Execute these steps sequentially. For each step, call the specified MCP tools, gather the data, then move to the next step.

### 2.1 — Compound Identification
**Goal:** Confirm this is a real peptide and get its identity.
**Tools:** `mcp__pubchem__*`
- Search for the compound by name
- Get molecular formula, structure type, synonyms, CID
- Confirm it is a peptide (amino acid chain) and not a small molecule, steroid, or other compound class
- If the compound is not found or is not a peptide, stop and report this to the user

### 2.2 — Mechanism
**Goal:** Find a plausible biological mechanism connecting this peptide to the claimed condition.
**Tools:** `mcp__pubmed__*`, `mcp__openalex__*`
- Search PubMed for: "[compound] [condition] mechanism"
- Search OpenAlex for broader coverage if PubMed results are sparse
- Identify the signaling pathways, receptors, or biological processes involved
- Assess whether the mechanism is specific to the claim or generic (e.g., "reduces inflammation" is generic)

### 2.3 — Evidence
**Goal:** What does the actual research show? Grade the evidence quality.
**Tools:** `mcp__pubmed__*`, `mcp__ctgov__*`
- Search PubMed for clinical studies, reviews, and meta-analyses
- Search ClinicalTrials.gov for ongoing or completed trials
- Grade evidence:
  - **RCT** — randomized controlled trials in humans (strongest)
  - **Human observational** — case reports, cohort studies, retrospective analyses
  - **Animal** — rodent or other animal models
  - **In vitro** — cell culture studies only (weakest)
- Note the gap between animal evidence and human evidence when relevant

### 2.4 — Regulatory Status
**Goal:** Is this peptide legal and available? What is its current FDA status?
**Tools:** `mcp__fda__*`, `mcp__clinvar__*`
- Check FDA status — is it approved, investigational, or banned?
- Check if it was affected by the 2023-2024 FDA Category 2 reclassification
- Check if it is among the 14 peptides expected to return to Category 1 (per RFK Feb 2026 announcement)
- Note: many peptides are sold as "research use only" (RUO) in a gray market

### 2.5 — Interactions
**Goal:** Flag conflicts with commonly stacked peptides and compounds.
**Tools:** `mcp__drugbank__*`, `mcp__chembl__*`
- Search DrugBank for known drug interactions
- Search ChEMBL for target activity that could conflict with common stacks
- Common stacks to check against: TRT/testosterone, GLP-1 agonists (semaglutide, tirzepatide, retatrutide), GH secretagogues (CJC-1295, ipamorelin, tesamorelin), BPC-157, TB-500, GHK-Cu, HCG
- Flag any anticoagulant, cardiovascular, or hormonal interactions

### 2.6 — Dosing Context
**Goal:** What does the literature say about dosing? Flag if only anecdotal.
**Tools:** `mcp__pubmed__*`, `mcp__pubchem__*`
- Search for pharmacokinetic data, dose-response studies
- Note whether dosing data comes from human trials, animal studies, or community anecdote
- If only animal data exists, note the species and the allometric scaling uncertainty
- Do NOT recommend a specific dose — report what the literature says

### 2.7 — Risk Synthesis
**Goal:** What could go wrong? Who should avoid this?
**Tools:** No new MCP calls — synthesize from all data gathered above.
- Compile contraindications from DrugBank and PubMed
- Note side effects reported in literature AND in community reports (Reddit, forums)
- Identify populations that should avoid this compound (cancer history, pregnancy, specific conditions)
- Assess the practical risk of gray market sourcing (sterility, purity, degradation)

## Step 3: Format the Response

Use this exact structure. Keep each section concise — the total response should be readable in under 60 seconds.

```
## [Compound] for [Condition] — [VERDICT]

**Verdict:** [Category] — [one sentence explaining why]

**What it is:** [1-2 sentences from PubChem data]

**Mechanism:** [2-3 sentences — biological pathway connecting compound to condition]

**Evidence:** [2-3 sentences — what studies exist, evidence grade]

**Regulatory status:** [1-2 sentences — FDA category, legal status as of 2026]

**Interactions:** [1-2 sentences — conflicts with common stacks]

**Dosing:** [1-2 sentences — literature-reported, flag if anecdotal]

**Risks:** [2-3 sentences — side effects, contraindications, sourcing risks]

**Bottom line:** [1 sentence — honest assessment]
```

### Verdict Categories

Choose exactly one:

- **Plausible** — mechanism makes sense AND human evidence exists (RCT or strong observational)
- **Weak Evidence** — mechanism is plausible BUT only animal or in vitro data supports the specific claim
- **Unsupported** — no credible mechanism or no evidence connecting compound to claimed condition
- **Risky** — may have evidence but significant safety concerns outweigh potential benefit

### Rules

- Be honest. If the evidence is weak, say so directly. Do not hedge with "more research is needed" — say what the research actually shows right now.
- Distinguish between "studied in rats" and "studied in humans." This distinction matters enormously and the peptide community often blurs it.
- When citing studies, include author and year (e.g., "Cerovecki 2010") so the user can look them up.
- If a claim includes a specific timeline (e.g., "healed in 3 weeks"), evaluate whether that timeline is realistic based on the biology, not just whether the compound could help at all.
- Always mention gray market sourcing risk. This is the #1 practical danger in the peptide community — the compound might not be what the label says.
- Do NOT recommend that the user try or avoid the peptide. Present the evidence and risks. The user decides.
