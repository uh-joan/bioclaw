---
name: pharma-bd-intelligence
description: "Business development intelligence: deal landscape, partner screening, asset due diligence, rapid TA briefings, out-licensing differentiation, deal comps, portfolio comparison, go/no-go scoring. Orchestrates competitive-intelligence, pharma-market-sizing, and pharma-ci-monitor. Use when user mentions deals, partnerships, licensing, in-license, out-license, due diligence, get smart fast, partner evaluation, portfolio comparison, or BD."
---

# Pharma BD Intelligence

On-demand business development intelligence and strategic orchestration for pharma and biotech. Adds deal/partnership intelligence on top of competitive landscape and market sizing data. Composes outputs from multiple skills for rapid strategic assessments, asset due diligence, and portfolio prioritization.

This skill is the **orchestration layer** — it pulls together competitive intelligence, market sizing, and deal data to answer BD-specific questions: Is this a good deal? Who should we partner with? How does this asset compare to alternatives? Give me a rapid briefing on this therapeutic area.

Distinct from **competitive-intelligence** (landscape analysis without deal context), **pharma-market-sizing** (market fundamentals without competitive or deal overlay), and **pharma-ci-monitor** (scheduled surveillance without strategic assessment).

## Report-First Workflow

1. **Create report file immediately**: `[topic]_bd_intelligence_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools
4. **Label data sources**: Each section should note which domain the data comes from (epi, competitive, deal, regulatory)
5. **Never show raw tool output**: Synthesize findings into report sections
6. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Ongoing competitive monitoring → use `pharma-ci-monitor`
- Market sizing or epidemiology data only → use `pharma-market-sizing`
- Full competitive landscape deep dive without BD context → use `competitive-intelligence`
- Clinical trial design or statistical analysis → use `clinical-trial-analyst`
- Biomarker strategy or companion diagnostics → use `biomarker-discovery`
- FDA regulatory pathway or submission strategy → use `fda-consultant`
- Single drug monograph → use `drug-research`

## Cross-Reference: Other Skills

- **Scheduled competitive monitoring and alerts** → use pharma-ci-monitor skill
- **Disease epidemiology and market sizing** → use pharma-market-sizing skill
- **On-demand competitive landscape deep dive** → use competitive-intelligence skill
- **Clinical trial design, endpoint selection** → use clinical-trial-analyst skill
- **Biomarker identification, patient stratification** → use biomarker-discovery skill
- **Drug safety profiling** → use adverse-event-detection skill

---

## Skill Composition Architecture

This skill orchestrates data from multiple domains. Follow the workflow patterns from each source skill:

```
pharma-ci-monitor (scheduled)
  │ ongoing competitor alerts, living landscape file
  v
pharma-market-sizing (on-demand)
  │ epi data, market size, subpopulations, forecasting
  v
competitive-intelligence (deep dive)
  │ pipeline matrix, differentiation, patent/LOE, regulatory
  v
pharma-bd-intelligence (this skill)
  │ adds: deal landscape, partner screening, orchestration
  │ adds: portfolio comparison, go/no-go scoring
  v
 STRATEGIC DECISION
```

When a workflow below says "use competitive-intelligence patterns" or "use market sizing patterns", follow the corresponding workflow steps from those skills using the same MCP tools. This avoids duplicating the detailed instructions.

---

## Deal Data Strategy

**No dedicated MCP exists for pharmaceutical deal databases** (Evaluate Pharma, Cortellis, GlobalData). Use these public data sources as fallbacks:

1. **PubMed** — Search for deal-related press releases and partnership announcements indexed in biomedical literature
   - Query: `"[mechanism/company] license agreement OR partnership OR collaboration OR acquisition OR deal"`
   - Many pharma deals are announced in publications or covered by journals like Nature Biotechnology

2. **OpenAlex** — Search for deal-related publications and track institutional research collaborations
   - Research partnerships often precede commercial deals

3. **Browser automation** (`agent-browser` skill) — For data not in MCP tools:
   - SEC EDGAR: Search 8-K filings for material agreements (public companies)
   - Company press release pages for deal announcements
   - Always note that browser-sourced data should be verified

4. **FDA/EMA** — Approval records show applicant (company) information
   - Identify co-development partners from NDA/BLA applicant fields
   - Track license transfers via supplemental applications

**Data limitations:**
- Most deal terms (upfront payments, milestones, royalties) are confidential
- Public data skews toward large deals by public companies
- Always note confidence level: HIGH (SEC filing with disclosed terms), MEDIUM (press release with partial terms), LOW (inferred from public data)

---

## Available MCP Tools

### Clinical & Regulatory

#### `mcp__clinicaltrials__ct_data` (Pipeline Assessment)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_studies` | Search trials by drug, condition, sponsor, phase | `query`, `status`, `phase`, `limit` |
| `get_study` | Full trial record: design, endpoints, enrollment | `nct_id` |
| `get_study_results` | Posted trial results | `nct_id` |

**BD usage:** Identify sponsors active in a TA, assess pipeline depth, evaluate clinical data for asset due diligence.

#### `mcp__ctgov__ct_gov_studies` (Complex Trial Queries)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Advanced trial search | `condition`, `intervention`, `lead`, `phase`, `status`, `start`, `pageSize` |
| `get` | Full trial details | `nctId` |
| `suggest` | Autocomplete terms | `input`, `dictionary` |

**BD usage:** Use `complexQuery` for sponsor-specific pipeline searches: `AREA[LeadSponsorName]CompanyName AND AREA[Phase]PHASE2,PHASE3`

#### `mcp__fda__fda_data` (US Regulatory & Safety)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search FDA drug database | `query`, `limit` |
| `get_drug_label` | Full prescribing information | `set_id` or `drug_name` |
| `search_adverse_events` | FAERS adverse event reports | `drug_name`, `limit`, `serious` |

**BD usage:** Label analysis for competitive positioning, safety profile comparison for differentiation narrative, applicant field for partner identification.

#### `mcp__ema__ema_data` (EU Regulatory)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_medicines` | Search EMA-authorized medicines | `query`, `limit` |
| `get_medicine` | Full EMA product information | `product_id` |

### Drug & Target

#### `mcp__opentargets__ot_data` (Target Validation for Due Diligence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drug` | Search drugs across Open Targets | `query`, `size` |
| `get_drug_info` | Drug mechanism, indications, trials | `drug_id` |
| `get_associations` | Target-disease evidence scores | `target_id`, `disease_id`, `size` |

**BD usage:** Genetic evidence strength supports or weakens asset valuation. Strong genetic association = higher probability of success.

#### `mcp__drugbank__drugbank_data` (Pharmacology Comparison)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Find drugs by name or category | `query`, `limit` |
| `get_drug` | Full drug profile: mechanism, targets, metabolism | `drugbank_id` |
| `get_interactions` | Drug-drug interactions | `drugbank_id` |

**BD usage:** Mechanism comparison for differentiation, DDI burden as competitive factor, pharmacology for out-licensing narrative.

#### `mcp__chembl__chembl_data` (Compound Properties)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_molecule` | Search molecules by name | `query`, `limit` |
| `get_molecule` | Development status, properties | `chembl_id` |

**BD usage:** Compare drug-like properties across competing assets. Development status tracking for pipeline landscape.

### Literature & Research

#### `mcp__pubmed__pubmed_data` (Scientific Evidence & Deal Press Releases)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search PubMed by keywords | `query`, `num_results` |
| `fetch_details` | Full article metadata | `pmid` |

**BD usage:** Scientific evidence supporting asset value, deal announcement search, KOL publications.

#### `mcp__pubmed__pubmed_articles` (Targeted Search)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Date-filtered search | `term`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

#### `mcp__biorxiv__biorxiv_data` (Preprint Intelligence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search bioRxiv/medRxiv preprints | `query`, `limit` |

**BD usage:** Early data disclosures that affect asset valuation.

#### `mcp__openalex__openalex_data` (Research Strength Assessment)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_works` | Search publications by keywords | `query` |
| `get_work` | Publication details | `id` |
| `search_authors` | Find researchers | `query` |
| `get_author` | Researcher profile, citations, affiliation | `id` |
| `get_works_by_author` | Researcher publication record | `authorId` |
| `get_works_by_institution` | Institutional publication output | `institutionId` |
| `search_institutions` | Find research institutions | `query` |
| `get_institution` | Institution profile, output, topics | `id` |
| `search_topics` | Research topic trends | `query` |
| `get_cited_by` | Citation impact | `workId` |

**BD usage:** Assess partner research strength by publication volume and citation impact. Map KOLs and their affiliations. Identify institutions with relevant expertise for partnership.

### Cancer & Population

#### `mcp__cbioportal__cbioportal_data` (Oncology Market Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_studies` | Cancer cohorts | `keyword`, `cancer_type` |
| `get_mutation_frequency` | Mutation prevalence | `study_id`, `gene`, `profile_id` |

### Payer & Commercial

#### `mcp__medicare__medicare_info` (US Pricing & Access)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `formulary` | Medicare formulary coverage | query varies |
| `asp_pricing` | Average Sales Price | query varies |
| `prescriber_data` | Prescriber utilization | query varies |

**BD usage:** Pricing benchmarks for commercial assessment, prescriber data for market penetration estimates.

#### `mcp__medicaid__medicaid_info` (Medicaid Landscape)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `formulary` | Medicaid coverage | query varies |
| `nadac_pricing` | Acquisition cost data | query varies |
| `utilization_data` | Drug utilization stats | query varies |

---

## Workflows

### Workflow 1: Deal Landscape

Find all known deals for a mechanism, indication, or company.

**Step 1: Literature search for deals**
- PubMed: `"[mechanism] license agreement OR partnership OR collaboration OR acquisition"` (limit: 30)
- PubMed: `"[company] pharma deal OR partnership OR license"` (limit: 20)
- OpenAlex: `search_works(query: "[mechanism] licensing deal pharmaceutical")` for broader coverage

**Step 2: Identify deal parties and context**
- For each relevant publication, extract: parties, date, mechanism/indication, deal type (in-license, out-license, co-development, acquisition)
- Search ClinicalTrials.gov by sponsor to cross-reference: `search_studies(query: "[company]", limit: 20)` — co-sponsored trials indicate partnerships

**Step 3: Browser research for deal terms (when needed)**
- SEC EDGAR 8-K filings for public companies — material agreements with disclosed terms
- Company investor relations pages for deal announcements
- Note: use `agent-browser` skill for browser automation

**Step 4: Compile deal landscape**
- Table: Date | Parties | Mechanism | Indication | Stage | Deal Type | Terms (if public) | Confidence
- Note confidence level for each deal (HIGH/MEDIUM/LOW based on data source)

**Step 5: Deal comp benchmarks**
- Where enough public data exists, compute: median upfront, range of total deal values by stage and mechanism
- Flag: "Based on N public deals — confidence [HIGH/MEDIUM/LOW]"

**Output:** Deal landscape table + benchmark analysis with confidence levels.

### Workflow 2: Partner Screening

Identify and evaluate potential partners for a therapeutic area or asset.

**Step 1: Pipeline-based screening**
- ClinicalTrials.gov: `search_studies(query: "[TA/mechanism]", limit: 50)` → extract unique sponsors
- Filter by: pipeline depth (number of trials), phase advancement, geographic presence (trial sites)

**Step 2: Research strength assessment**
- OpenAlex: `search_institutions(query: "[TA/mechanism]")` → find institutions with strong publication records
- For top candidates: `get_works_by_institution(institutionId)` → assess research output and recency
- `search_authors(query: "[TA] [mechanism]")` → identify KOLs and their institutional affiliations

**Step 3: Regulatory track record**
- FDA: `search_drugs(query: "[candidate company]")` → have they successfully brought products to market?
- EMA: `search_medicines(query: "[candidate company]")` → EU track record

**Step 4: Deal history**
- Run Deal Landscape (Workflow 1) filtered for each candidate → assess deal-making activity
- PubMed: `"[candidate company] partnership OR collaboration"` → recent deal activity

**Step 5: Evaluate and rank**
- Score each candidate across dimensions: pipeline depth (1-5), research strength (1-5), regulatory track record (1-5), deal-making activity (1-5), strategic fit (1-5)
- Present as a partner screening matrix

**Output:** Partner screening matrix with scored evaluations and supporting evidence.

### Workflow 3: Asset Due Diligence

Comprehensive evaluation of a specific asset for in-licensing or investment.

**Step 1: Clinical data assessment**
- ClinicalTrials.gov: find all trials for the asset → `search_studies(query: "[drug name]")`
- For each trial: `get_study(nct_id)` for design, enrollment, endpoints
- For completed trials: `get_study_results(nct_id)` for posted results
- PubMed: `"[drug name] clinical trial results"` for published data

**Step 2: Mechanism validation**
- Open Targets: `get_associations(target_id, disease_id)` → genetic evidence score
- DrugBank: `get_drug(drugbank_id)` → mechanism, pharmacology, selectivity
- ChEMBL: `get_molecule(chembl_id)` → compound properties, development status

**Step 3: Competitive positioning**
Follow competitive-intelligence skill patterns:
- Pipeline matrix: all competitors in the same TA/mechanism, organized by phase
- Differentiation assessment: mechanism uniqueness, clinical profile advantages/disadvantages
- Patent/LOE landscape: exclusivity position vs. competitors

**Step 4: Market opportunity**
Follow pharma-market-sizing skill patterns:
- Disease epidemiology (CDC + PubMed)
- Subpopulation sizing (cBioPortal for oncology + PubMed)
- Addressable market estimation
- Payer landscape (Medicare/Medicaid)

**Step 5: Regulatory path**
- FDA/EMA: find approval precedent for similar mechanisms → `search_drugs(query: "[mechanism class]")`
- Label analysis of comparable approved products → `get_drug_label(drug_name: "[comparable]")`
- Assess: standard pathway vs. accelerated approval vs. breakthrough

**Step 6: Safety profile**
- FDA: `search_adverse_events(drug_name: "[drug]")` if any data exists
- Compare safety profile vs. competitors using label warnings and FAERS data

**Step 7: Deal context**
- Run Deal Landscape (Workflow 1) for comparable deals in the mechanism/indication
- What have others paid for similar assets at similar stages?

**Output:** Comprehensive due diligence report with clearly labeled sections per domain, overall assessment, and key risks.

### Workflow 4: "Get Smart Fast" Briefing

Rapid therapeutic area overview combining all domains. Target: a 3-5 page executive briefing.

**Step 1: Disease overview** (market sizing patterns)
- CDC: prevalence, incidence, mortality
- PubMed: 1-2 key epi review papers
- One paragraph summary

**Step 2: Current standard of care**
- FDA: approved therapies, label indications
- Brief comparison table of current options

**Step 3: Pipeline landscape** (competitive-intelligence patterns)
- ClinicalTrials.gov: Phase 3 and filed drugs
- Pipeline waterfall: one table, sorted by phase

**Step 4: Key competitors**
- Top 3-5 sponsors by trial activity
- One sentence each on their competitive position

**Step 5: Recent deals**
- Deal Landscape (Workflow 1) — summarize top 3-5 most relevant deals
- Deal activity trend: increasing or decreasing?

**Step 6: Unmet need**
- Gap between current SOC and patient needs
- Key limitations of existing therapies

**Step 7: Key takeaways**
- 3-5 bullet points: biggest opportunities, risks, and trends

**Output:** Executive briefing — concise, structured, and actionable. One paragraph per section, not exhaustive.

### Workflow 5: Out-Licensing Package

Generate a competitive differentiation narrative for an asset the user wants to out-license.

**Step 1: Full competitive landscape** (competitive-intelligence patterns)
- All approved and pipeline competitors in the indication

**Step 2: Identify differentiation axes**
- Mechanism: novel target, first-in-class, best-in-class?
- Efficacy: published clinical data showing superiority or non-inferiority
- Safety: better tolerability, fewer black box warnings, lower DDI burden (DrugBank)
- Convenience: oral vs. injectable, dosing frequency, no monitoring required
- Patient population: broader or more targeted label potential

**Step 3: Market opportunity data** (market sizing patterns)
- Addressable market size and growth
- Unmet need score

**Step 4: Scientific evidence**
- PubMed/OpenAlex: key publications supporting the differentiation claim
- Cite specific data points (hazard ratios, response rates, safety events)

**Step 5: Compose narrative**
- Structure: "Why [Drug] — differentiated [mechanism] for [indication]"
- Lead with the strongest differentiation axis
- Support with data, market opportunity, and competitive context
- Note: this is a data-backed positioning narrative, not marketing copy

**Output:** Out-licensing differentiation document with evidence citations.

### Workflow 6: Deal Comp Analysis

For a specific proposed deal, find comparable transactions.

**Step 1: Define comparability criteria**
- Mechanism class (e.g., checkpoint inhibitor, ADC, bispecific)
- Development stage (preclinical, Phase 1, Phase 2, Phase 3, approved)
- Indication category (oncology, immunology, neuroscience, etc.)
- Modality (small molecule, biologic, cell therapy, gene therapy)

**Step 2: Search for comparable deals**
- Run Deal Landscape (Workflow 1) filtered by the criteria above
- Broaden search if too few results (e.g., same mechanism class in any indication)

**Step 3: Extract public terms**
- For each comparable deal: upfront payment, total potential value, royalty range, milestone structure
- Note which terms are disclosed vs. inferred

**Step 4: Compute benchmarks**
- Median and range for: upfront, total deal value, royalties
- Stratify by stage if enough data points
- Flag sample size and confidence

**Output:** Deal comp table with ranges, confidence level, and methodology notes.

### Workflow 7: Portfolio Comparison Matrix (Portfolio Strategy Extension)

Compare N assets or opportunities side by side.

**Step 1: For each asset, gather data across dimensions:**
- Market size (pharma-market-sizing patterns): addressable patients, market value
- Competitive intensity (competitive-intelligence patterns): number of competitors, pipeline density
- Mechanism validation (Open Targets): genetic evidence score
- Development stage: current phase, estimated time to market
- Differentiation: mechanism uniqueness assessment
- Deal context (Workflow 1): comparable deal values

**Step 2: Normalize scores**
- Convert each dimension to a 1-5 scale for comparability
- Document the scoring criteria

**Step 3: Build comparison matrix**

| Dimension | Asset A | Asset B | Asset C |
|-----------|---------|---------|---------|
| Market size | 4 | 3 | 5 |
| Competitive intensity | 2 (crowded) | 4 (open) | 3 |
| Target validation | 5 | 3 | 4 |
| Development stage | Phase 2 | Phase 1 | Phase 3 |
| Differentiation | 3 | 5 | 2 |
| **Overall** | **3.4** | **3.6** | **3.6** |

**Step 4: Highlight insights**
- Best opportunity overall
- Highest risk (crowded + undifferentiated)
- Best risk/reward ratio
- Recommended prioritization with reasoning

**Output:** Side-by-side comparison matrix with scores, evidence, and prioritization recommendation.

### Workflow 8: Go/No-Go Scoring (Portfolio Strategy Extension)

Structured investment decision framework for a single asset.

| Dimension | Weight | Score (1-5) | Evidence |
|-----------|--------|------------|----------|
| Clinical feasibility | 20% | | Target validation (Open Targets), trial design precedent |
| Commercial attractiveness | 20% | | Market size, unmet need (market sizing) |
| Competitive intensity | 15% | | Number/phase of competitors (CI) |
| Differentiation potential | 15% | | Mechanism uniqueness, clinical advantages |
| Time to market | 15% | | Comparable trial timelines (ClinicalTrials.gov) |
| Investment required | 15% | | Estimated from comparable program costs |

**Weighted score**: Sum of (weight x score) → 1.0-5.0 scale
- **4.0-5.0**: Strong GO
- **3.0-3.9**: Conditional GO (address key risks)
- **2.0-2.9**: Reassess (significant concerns)
- **1.0-1.9**: NO-GO

User can supply custom weights. Default is the distribution above.

**Output:** Go/no-go scorecard with weighted scores, evidence per dimension, key risks, and recommendation.

### Workflow 9: Portfolio Risk Heatmap (Portfolio Strategy Extension)

Map portfolio assets against competitive threat.

**Axes:**
- X: Competitive crowding (number of competitors in same mechanism/indication) — LOW (0-2), MEDIUM (3-5), HIGH (6+)
- Y: Differentiation strength (mechanism uniqueness + clinical data) — LOW, MEDIUM, HIGH

**Quadrants:**
```
                    LOW COMPETITION    HIGH COMPETITION
HIGH DIFFERENTIATION   [STRONG]          [DEFENSIBLE]
LOW DIFFERENTIATION    [OPPORTUNISTIC]   [AT RISK]
```

- **STRONG**: Clear differentiation, low competition — prioritize
- **DEFENSIBLE**: Differentiated but crowded — invest in differentiation narrative
- **OPPORTUNISTIC**: Undifferentiated but low competition — speed matters
- **AT RISK**: Undifferentiated and crowded — reconsider or find differentiation

**Output:** Text-based heatmap with each portfolio asset placed in the appropriate quadrant and rationale.

---

## Completeness Checklist

- [ ] Deal data sourced from multiple public channels (PubMed, OpenAlex, browser if needed)
- [ ] Confidence levels noted for all deal data (HIGH/MEDIUM/LOW)
- [ ] Partner screening covers pipeline + publications + regulatory track record
- [ ] Due diligence cross-references clinical + competitive + market + deal data
- [ ] "Get smart fast" briefing covers all 6 domains concisely
- [ ] Out-licensing narrative backed by specific data points with citations
- [ ] Portfolio comparison uses normalized scoring across consistent dimensions
- [ ] All data limitations and confidence levels explicitly stated
- [ ] Recommendations include key risks and mitigants
