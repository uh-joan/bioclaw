---
name: pharma-ci-monitor
description: "Scheduled competitive intelligence monitoring. Watchlist-based tracking of competitors, therapeutic areas, targets, and mechanisms with change detection, living landscape files, and alert digests. Use when user wants ongoing monitoring, watchlist setup, competitive alerts, landscape tracking, or scheduled CI scans."
---

# Pharma CI Monitor

Scheduled, recurring competitive intelligence monitoring for pharma and biotech. Tracks a user-defined watchlist of competitors, therapeutic areas, targets, and mechanisms across clinical trials, regulatory approvals, publications, and preprints. Detects changes since the last scan, maintains a living landscape file with incremental updates, and sends prioritized alert digests.

Distinct from **competitive-intelligence** (which produces one-off deep-dive landscape reports on demand). This skill operates as an automated surveillance system — lightweight, recurring delta scans that flag what changed and when, so the user stays current without manual effort.

## Report-First Workflow

1. **Create landscape file immediately**: `[watchlist-name]_ci_landscape.md` with all section headers
2. **Add placeholders**: Mark each section `[Scanning...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools
4. **Never show raw tool output**: Synthesize findings into landscape sections
5. **Append dated updates**: On delta scans, add a dated `## Update: YYYY-MM-DD` section — never overwrite previous entries
6. **Final verification**: Ensure no `[Scanning...]` placeholders remain after baseline scan

## When NOT to Use This Skill

- One-off competitive landscape deep dive → use `competitive-intelligence`
- Clinical trial design or statistical analysis → use `clinical-trial-analyst`
- Market sizing, epidemiology, or prevalence data → use `pharma-market-sizing`
- Deal landscape, partner evaluation, or due diligence → use `pharma-bd-intelligence`
- Single drug monograph or compound deep-dive → use `drug-research`
- Biomarker identification or companion diagnostics → use `biomarker-discovery`

## Cross-Reference: Other Skills

- **On-demand competitive landscape deep dive** → use competitive-intelligence skill
- **Market sizing, epidemiology, addressable market** → use pharma-market-sizing skill
- **Deal intelligence, partner screening, due diligence** → use pharma-bd-intelligence skill
- **Clinical trial design, endpoint selection** → use clinical-trial-analyst skill
- **Single drug monograph** → use drug-research skill

---

## Watchlist Configuration

The watchlist is a JSON file stored in the group folder as `ci_watchlist.json`. Create it during watchlist setup.

```json
{
  "name": "oncology-io-landscape",
  "competitors": ["Merck", "Bristol-Myers Squibb", "Roche", "AstraZeneca"],
  "therapeutic_areas": ["non-small cell lung cancer", "melanoma", "renal cell carcinoma"],
  "targets": ["PD-1", "PD-L1", "CTLA-4", "LAG-3", "TIGIT"],
  "mechanisms": ["checkpoint inhibitor", "bispecific antibody", "ADC"],
  "keywords": ["immunotherapy resistance", "tumor microenvironment"],
  "alert_threshold": "any",
  "created": "2026-03-23"
}
```

**Fields:**
- `name`: Human-readable watchlist identifier (used in filenames)
- `competitors`: Sponsor/company names to track in ClinicalTrials.gov and publications
- `therapeutic_areas`: Disease/condition terms for trial and publication searches
- `targets`: Molecular targets for mechanism-class tracking
- `mechanisms`: Drug mechanism categories
- `keywords`: Additional search terms for publication monitoring
- `alert_threshold`: `"any"` (all changes), `"medium_and_high"`, or `"high_only"`

## Scan State

Maintain `ci_scan_state.json` in the group folder to track what was seen on the last scan:

```json
{
  "last_scan": "2026-03-23T07:00:00Z",
  "known_trials": {
    "NCT06123456": { "status": "RECRUITING", "phase": "PHASE3", "last_seen": "2026-03-23" },
    "NCT06789012": { "status": "ACTIVE_NOT_RECRUITING", "phase": "PHASE2", "last_seen": "2026-03-23" }
  },
  "known_approvals": ["NDA123456", "BLA789012"],
  "known_publications": ["PMID39876543", "PMID39876544"],
  "scan_counts": {
    "trials": 47,
    "approvals": 12,
    "publications": 156
  }
}
```

On each delta scan, compare current results against this state to identify new or changed entries.

---

## Available MCP Tools

### `mcp__clinicaltrials__ct_data` (Pipeline Tracking — Primary)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_studies` | Search trials by drug, condition, sponsor, phase | `query`, `status`, `phase`, `limit` |
| `get_study` | Full trial record: design, endpoints, enrollment, sponsor | `nct_id` |
| `get_study_results` | Posted trial results (primary/secondary endpoints) | `nct_id` |

**Monitoring queries:**
- Search by sponsor name for each competitor → new trials, status changes
- Search by condition for each TA → new entrants
- Filter by status `RECRUITING` and `NOT_YET_RECRUITING` → upcoming competition
- Compare trial status against `ci_scan_state.json` → flag transitions (e.g., RECRUITING → COMPLETED)

### `mcp__ctgov__ct_gov_studies` (Pipeline Tracking — Complementary)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search trials with complex queries | `condition`, `intervention`, `lead`, `phase`, `status`, `start`, `pageSize` |
| `get` | Full trial details by NCT ID | `nctId` |
| `suggest` | Autocomplete terms | `input`, `dictionary` |

**Monitoring queries:**
- Use `start` date range parameter to filter trials registered since last scan
- Use `complexQuery` for advanced filters: `AREA[LeadSponsorName]CompetitorName AND AREA[Phase]PHASE3`

### `mcp__fda__fda_data` (US Regulatory Monitoring)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search FDA drug database | `query`, `limit` |
| `get_drug_label` | Full prescribing information | `set_id` or `drug_name` |
| `search_adverse_events` | FAERS adverse event reports | `drug_name`, `limit`, `serious` |

**Monitoring queries:**
- Search by competitor name and TA keywords for new approvals
- Compare NDA/BLA numbers against `known_approvals` in scan state
- Check for supplemental approvals (new indications, formulations)

### `mcp__ema__ema_data` (EU Regulatory Monitoring)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_medicines` | Search EMA-authorized medicines | `query`, `limit` |
| `get_medicine` | Full EMA product information | `product_id` |

**Monitoring queries:**
- Search by TA and competitor for new EU marketing authorizations
- Track conditional approvals and CHMP opinions

### `mcp__pubmed__pubmed_data` (Publication Monitoring)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search PubMed by keywords, MeSH terms | `query`, `num_results` |
| `fetch_details` | Full article metadata | `pmid` |

**Monitoring queries:**
- Search for competitor drug names + TA keywords, filter by date since last scan
- Track congress abstract publications (ASCO, AACR, AHA, ESC, etc.)
- Search for head-to-head comparison studies

### `mcp__pubmed__pubmed_articles` (Targeted Literature Search)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Date-filtered search | `term`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

**Monitoring queries:**
- Use `search_advanced` with `start_date` = last scan date for new publications only

### `mcp__biorxiv__biorxiv_data` (Preprint Early Signals)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search bioRxiv/medRxiv preprints | `query`, `limit` |

**Monitoring queries:**
- Search for competitor names + mechanism keywords
- Early detection of data disclosures before peer review

### `mcp__openalex__openalex_data` (Research Activity Tracking)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_works` | Track publications by keywords | `query` |
| `get_work` | Publication details by DOI or PMID | `id` |
| `search_authors` | Find researchers at competitor organizations | `query` |
| `get_author` | Researcher profile, citation metrics | `id` |
| `get_works_by_institution` | Competitor institution publication output | `institutionId` |
| `search_topics` | Research topic activity trends | `query` |

**Monitoring queries:**
- Track publication volume trends for competitors and mechanisms
- Identify new KOLs publishing on competitive programs
- Detect emerging research topics in the monitored TAs

### `mcp__opentargets__ot_data` (Target Landscape Changes)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drug` | Search drugs across Open Targets | `query`, `size` |
| `get_drug_info` | Drug details: mechanism, indications, trials | `drug_id` |
| `get_associations` | Target-disease evidence scores | `target_id`, `disease_id`, `size` |

**Monitoring queries:**
- Check for new drugs linked to monitored targets
- Track changes in evidence scores for target-disease associations

### `mcp__drugbank__drugbank_data` (Compound Status Changes)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Find drugs by name or category | `query`, `limit` |
| `get_drug` | Full drug profile: mechanism, targets, status | `drugbank_id` |

### `mcp__chembl__chembl_data` (Pipeline Compound Tracking)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_molecule` | Search molecules by name or identifier | `query`, `limit` |
| `get_molecule` | Development status, properties | `chembl_id` |

### `mcp__cbioportal__cbioportal_data` (Oncology Population Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_studies` | Cancer cohorts and datasets | `keyword`, `cancer_type` |
| `get_mutation_frequency` | Target mutation prevalence | `study_id`, `gene`, `profile_id` |

---

## Workflows

### Workflow 1: Watchlist Setup

1. Ask the user for:
   - Competitors to track (company/sponsor names)
   - Therapeutic areas (disease/condition names)
   - Targets and mechanisms of interest
   - Keywords for publication monitoring
   - Schedule preference (e.g., "weekly on Mondays at 7am", "daily at 6am")
   - Alert threshold preference (`any`, `medium_and_high`, `high_only`)

2. Create `ci_watchlist.json` in the group folder with the collected information

3. Run the Baseline Scan (Workflow 2) immediately

4. Schedule recurring delta scans using the `schedule_task` IPC tool:
   ```
   schedule_task(
     prompt: "Read ci_watchlist.json and ci_scan_state.json. Run a delta scan following the pharma-ci-monitor skill. Compare current data against scan state, update the living landscape file with dated changes, update scan state, and send an alert digest if changes are found.",
     schedule_type: "cron",
     schedule_value: "0 7 * * 1",  // e.g., weekly Mondays at 7am
     context_mode: "isolated"
   )
   ```

5. Confirm to the user: watchlist saved, baseline complete, recurring scan scheduled

### Workflow 2: Baseline Scan

Run once on initial setup to establish the landscape snapshot.

**Step 1: Pipeline scan**
- For each competitor in watchlist: `search_studies(query: "[competitor]", status: "RECRUITING,ACTIVE_NOT_RECRUITING,NOT_YET_RECRUITING", limit: 50)`
- For each TA: `search_studies(query: "[TA]", limit: 50)` — filter to phases 1-3
- Record all NCT IDs, statuses, phases, sponsors in `ci_scan_state.json`

**Step 2: Regulatory scan**
- For each competitor + TA combination: `search_drugs(query: "[competitor drug terms]")`
- For EMA: `search_medicines(query: "[TA terms]")`
- Record NDA/BLA numbers in `known_approvals`

**Step 3: Publication scan**
- For each competitor + mechanism: `search_advanced(term: "[competitor] [mechanism]", num_results: 20)`
- For each TA + target: `search(query: "[TA] [target]", num_results: 20)`
- Record PMIDs in `known_publications`

**Step 4: Preprint scan**
- For each mechanism + TA: `search(query: "[mechanism] [TA]", limit: 10)`

**Step 5: Create landscape file**
- Create `[watchlist-name]_ci_landscape.md` with sections:
  - **Pipeline Matrix**: Table of all trials by competitor, phase, status, indication
  - **Approved Products**: Current approved therapies in the monitored TAs
  - **Recent Publications**: Key publications organized by competitor/mechanism
  - **Preprint Signals**: Notable preprints
  - **Key Findings**: Summary of competitive positioning and notable observations

**Step 6: Save scan state**
- Write `ci_scan_state.json` with all recorded IDs and timestamps

### Workflow 3: Delta Scan (Recurring)

Runs on schedule. Produces incremental updates only.

**Step 1: Read state**
- Read `ci_watchlist.json` and `ci_scan_state.json`
- Note `last_scan` timestamp

**Step 2: Trial delta**
- Re-run pipeline queries from Baseline Scan Step 1
- Compare each trial against `known_trials`:
  - **New trial**: NCT ID not in scan state → flag as new
  - **Status change**: Same NCT ID but different status → flag transition (e.g., RECRUITING → COMPLETED)
  - **Phase advance**: Same NCT ID but higher phase → flag progression
- For new or changed trials, get full details with `get_study(nct_id)`
- Check for posted results with `get_study_results(nct_id)` on completed trials

**Step 3: Regulatory delta**
- Re-run regulatory queries
- Compare against `known_approvals` → flag new NDA/BLA numbers

**Step 4: Publication delta**
- Use `search_advanced` with `start_date` = last scan date
- Compare PMIDs against `known_publications` → flag new papers

**Step 5: Preprint delta**
- Re-run preprint queries, filter by date

**Step 6: Update landscape file**
- Append a dated update section to the living landscape file:

```markdown
## Update: 2026-03-30

### New Trials
- **NCT06999888** — [Competitor] Phase 3, [Drug] vs SOC in [indication], recruiting (registered 2026-03-27)

### Status Changes
- **NCT06123456** — [Competitor] [Drug]: RECRUITING → COMPLETED (primary completion reached)

### New Approvals
- **NDA999999** — [Drug] approved for [indication] (2026-03-28)

### New Publications
- **PMID 40123456** — "[Title]" — [Journal], [date]. Key finding: [summary]

### New Preprints
- bioRxiv 2026.03.28.999999 — "[Title]" — [summary]
```

**Step 7: Update scan state**
- Update `last_scan` timestamp
- Add new NCT IDs, approvals, publications to scan state
- Update statuses for changed trials

### Workflow 4: Alert Digest

After each delta scan, compose and send an alert summary.

**Severity classification:**
- **HIGH**: New approval, Phase 3 results posted, trial termination/failure, breakthrough therapy designation
- **MEDIUM**: New Phase 2/3 trial, significant publication (high-impact journal), Phase 2 results, new partnership announcement in publications
- **LOW**: New Phase 1 trial, preprint, conference abstract, minor trial update

**Alert format:**
```
## CI Monitor Alert: [watchlist-name]
**Scan: YYYY-MM-DD HH:MM**

### HIGH
- **New FDA Approval**: [Drug] approved for [indication] (date)
- **Phase 3 Results**: NCT[ID] [Drug] — primary endpoint met/missed

### MEDIUM
- **New Phase 3 Trial**: NCT[ID] [Competitor] — [Drug] vs SOC in [indication]
- **Key Publication**: PMID [ID] — "[short title]" in [journal]

### LOW
- **New Phase 1**: NCT[ID] — Novel [mechanism] [modality]
- **Preprint**: "[short title]" — [key finding]

Full landscape: [watchlist-name]_ci_landscape.md (updated)
```

**Filtering:**
- If `alert_threshold` is `"high_only"`, only include HIGH items
- If `alert_threshold` is `"medium_and_high"`, include HIGH and MEDIUM
- If `alert_threshold` is `"any"`, include all items
- If no changes detected at or above threshold, send: "CI Monitor: No significant changes detected since [last scan date]"

Send the alert via the `send_message` IPC tool.

### Workflow 5: Deep Dive Trigger

When a HIGH-priority change is detected, suggest a full analysis:

```
**Suggested action**: Run `competitive-intelligence` skill for a full landscape analysis of [Drug/Competitor] in [indication].
Prompt: "Produce a competitive intelligence report on [Drug] in [indication], focusing on [specific change detected]."
```

This bridges the monitoring layer (this skill) with the deep-dive layer (`competitive-intelligence`).

---

## Completeness Checklist

Before completing any scan, verify:
- [ ] All competitors in watchlist were queried in ClinicalTrials.gov
- [ ] All therapeutic areas were searched for pipeline entrants
- [ ] FDA and EMA checked for new approvals
- [ ] PubMed searched with date filter for new publications
- [ ] bioRxiv checked for preprints
- [ ] Scan state file updated with all new/changed entries
- [ ] Landscape file updated (baseline: full sections; delta: dated append)
- [ ] Alert digest composed with correct severity classification
- [ ] Alert filtered by user's threshold preference
