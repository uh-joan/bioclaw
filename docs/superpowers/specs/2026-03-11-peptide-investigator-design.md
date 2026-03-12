# Peptide Investigator Skill — Design Spec

**Date:** 2026-03-11
**Status:** Approved

## Overview

A container skill that investigates peptide health claims from Reddit and other sources. When a BioClaw group member explicitly asks the agent to investigate a claim, it runs a full 7-step investigation using biomedical MCP servers and responds with a concise, structured verdict in chat.

## Scope

- **Users:** BioClaw group members (WhatsApp/Telegram)
- **Compounds:** Peptides only
- **Trigger:** Explicit request (e.g., "investigate this," "is this legit," "check this claim")
- **Output:** Chat-native response, no files saved
- **Depth:** Full 7-step investigation, concise delivery

## Trigger & Input Extraction

The skill activates when a user explicitly asks to investigate a peptide claim. The agent extracts:

1. **Compound** — the peptide mentioned (BPC-157, tirzepatide, GHK-Cu, etc.)
2. **Condition/goal** — what it's claimed to help with (ACL recovery, weight loss, brain fog, etc.)

Trigger phrases: "investigate this," "is this legit," "check this claim," "is X safe for Y," "should I try X for Y"

Does NOT auto-trigger on casual mention of peptides.

## 7-Step Investigation Pipeline

Each step runs sequentially using specific MCP servers:

| Step | Question | MCP Tools |
|------|----------|-----------|
| 1. Compound ID | Is this a real peptide? What is it? | PubChem |
| 2. Mechanism | Why could this plausibly work? | PubMed, OpenAlex |
| 3. Evidence | What does the research actually show? | PubMed, ClinicalTrials.gov |
| 4. Regulatory | Is this legal/available? Current FDA status? | FDA, ClinVar |
| 5. Interactions | What conflicts with common peptide stacks? | DrugBank, ChEMBL |
| 6. Dosing context | What does the literature say about dosing? | PubMed, PubChem |
| 7. Risk verdict | What could go wrong? Who should avoid this? | All above synthesized |

## Output Format

Fixed structure, kept concise:

```
## [Compound] for [Condition] — [VERDICT]

**Verdict:** [Plausible / Weak Evidence / Unsupported / Risky] + one sentence why

**What it is:** [1-2 sentences — compound identity from PubChem]

**Mechanism:** [2-3 sentences — how it could work biologically]

**Evidence:** [2-3 sentences — what studies exist, quality level]

**Regulatory status:** [1-2 sentences — FDA category, legal status]

**Interactions:** [1-2 sentences — known conflicts with common stacks]

**Dosing:** [1-2 sentences — literature-reported dosing, flag if anecdotal only]

**Risks:** [2-3 sentences — contraindications, side effects, who should avoid]

**Bottom line:** [1 sentence — honest "should you look into this further" take]
```

### Verdict Categories

- **Plausible** — mechanism makes sense, human evidence exists
- **Weak Evidence** — mechanism plausible but only animal/in vitro data
- **Unsupported** — no credible mechanism or evidence
- **Risky** — may work but significant safety concerns

### Evidence Quality Levels

Referenced in the Evidence section:
- **In vitro** — cell culture only
- **Animal** — rodent/animal models
- **Human observational** — case reports, retrospective studies
- **RCT** — randomized controlled trials

## Architecture

Single SKILL.md file in `container/skills/peptide-investigator/`. No subagents, no supporting files. The skill is a prompt document that instructs the agent on:

1. How to recognize investigation requests
2. What to extract from the claim
3. Which MCP tools to call and in what order
4. How to format the response

The agent's existing MCP server access (PubMed, PubChem, FDA, ClinVar, DrugBank, ChEMBL, OpenAlex, ClinicalTrials.gov) provides all required data. No new infrastructure needed.

## Example

**Input:** "investigate this: someone on reddit said BPC-157 healed their torn ACL in 3 weeks"

**Extraction:** compound = BPC-157, condition = ACL tear recovery

**Output:**

```
## BPC-157 for ACL Tear Recovery — Weak Evidence

**Verdict:** Mechanism is plausible and well-studied in animals,
but no human clinical trials exist. The "3 weeks" claim is
unrealistic for a full ACL tear.

**What it is:** Body Protection Compound-157, a synthetic
pentadecapeptide derived from human gastric juice protein BPC.

**Mechanism:** BPC-157 promotes angiogenesis and tendon-to-bone
healing via VEGF and GH receptor upregulation. It accelerates
collagen organization in connective tissue repair in animal models.

**Evidence:** Multiple rat studies show accelerated tendon and
ligament healing (Cerovecki 2010, Chang 2011). Zero human RCTs.
All dosing data extrapolated from rodent models.

**Regulatory status:** FDA Category 2 as of 2024. One of the 14
peptides expected to return to Category 1 per RFK Feb 2026
announcement. Currently gray market in the US.

**Interactions:** No known dangerous interactions. Often stacked
with TB-500 for synergistic healing. Monitor if on anticoagulants
— BPC-157 affects NO system and platelet aggregation.

**Dosing:** Rodent studies use 10 mcg/kg. Community standard is
250-500 mcg/day subQ near injury site. No human pharmacokinetic
data exists.

**Risks:** Rare reports of light sensitivity, eye irritation
(r/bpc_157). Theoretical tumor growth concern due to angiogenesis
promotion — avoid if history of cancer. Sterility of gray market
sources is the biggest practical risk.

**Bottom line:** The biology is real but the evidence is all
animal. "3 weeks for ACL" is fantasy — expect months at best,
as an adjunct to proper rehab, not a replacement.
```

## Dependencies

Requires these MCP servers to be mounted in the container:
- pubmed-mcp-server
- pubchem-mcp-server
- fda-mcp-server
- clinvar-mcp-server
- drugbank-mcp-server
- chembl-mcp-server
- openalex-mcp-server
- ctgov-mcp-server

All are already configured in the current BioClaw setup.
