---
name: pharma-patent-analyst
description: "Drug patent landscape and IP strategy using USPTO data. Patent landscape mapping, LOE/patent cliff timeline, freedom-to-operate assessment, Orange Book patent identification, Paragraph IV analysis, biosimilar entry timing, patent family tracking, composition of matter vs formulation vs method of use patents. Use when user mentions patent landscape, drug patent, IP strategy, patent cliff, LOE, loss of exclusivity, Orange Book, Paragraph IV, paragraph iv, freedom to operate, FTO, biosimilar patents, patent expiry, patent family, or composition of matter patent."
---

# Pharma Patent Analyst & IP Strategy

Drug patent landscape and IP strategy specialist. Maps composition of matter, formulation, and method of use patents using USPTO data. Tracks patent cliffs, biosimilar entry windows, Paragraph IV challenges, and freedom-to-operate assessments. Cross-references with FDA Orange Book exclusivity data.

## Report-First Workflow

1. **Create report file immediately**: `[drug]_patent_landscape.md`
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update as data is gathered
4. **Final verification**: Ensure no placeholders remain

## When NOT to Use This Skill

- Drug mechanism and pharmacology → use `drug-research`
- Financial impact of patent cliff → use `pharma-financial-analyst`
- BD deal IP terms → use `pharma-deal-valuation`
- Competitive pipeline → use `pharma-ci-monitor`

## Cross-Reference: Other Skills

- **Financial impact of LOE** → use pharma-financial-analyst (revenue cliff modeling)
- **Competitive intelligence** → use competitive-intelligence and pharma-ci-monitor
- **Deal IP terms** → use pharma-deal-valuation (SEC 8-K deal terms)
- **Biosimilar development** → use drug-research (for biosimilar compound profiles)
- **Regulatory exclusivity** → use fda-consultant (regulatory pathway, orphan exclusivity)

## Available MCP Tools

### `mcp__patents__patents_mcp_server` (USPTO Patent Search)

| Method | Patent analysis use |
|--------|-------------------|
| `ppubs_search_patents` | **Search granted patents** by keyword, assignee, inventor, CPC class |
| `ppubs_search_applications` | Search published patent applications |
| `ppubs_get_full_document` | Full patent text (claims, description, abstract) |
| `ppubs_get_patent_by_number` | Retrieve specific patent by number |
| `ppubs_download_patent_pdf` | Download patent PDF |
| `get_app` | Patent application data from Open Data Portal |
| `search_applications` | Search applications with filters |
| `get_app_assignment` | **Patent assignment/ownership** (who owns the patent) |
| `get_app_continuity` | Patent family continuity (parent/child applications) |
| `get_app_foreign_priority` | Foreign priority claims (international filing strategy) |
| `get_app_transactions` | Prosecution history (office actions, amendments) |
| `get_app_documents` | Filed documents in the application |

### `mcp__fda__fda_data` (FDA — Orange Book & Exclusivity)

| Method | Patent analysis use |
|--------|-------------------|
| `search_orange_book` | **Orange Book patents** listed for approved drugs |
| `search_drugs` | Approved drugs with exclusivity dates |
| `get_drug_label` | Label for indication scope of patents |

### Existing MCP Tools

| Tool | Patent analysis use |
|------|-------------------|
| `mcp__chembl__chembl_info` | Compound structure for composition of matter scope |
| `mcp__drugbank__drugbank_info` | Drug formulations and delivery for formulation patents |
| `mcp__pubmed__pubmed_data` | Prior art publications |

---

## Patent Analysis Workflow

### Phase 1: Orange Book Patent Mapping

```
1. FDA search_orange_book → list all patents for the drug
2. For each patent number:
   - ppubs_get_patent_by_number → patent type, claims, expiry
   - Classify: composition of matter / formulation / method of use
3. Map exclusivity dates: NCE (5yr), orphan (7yr), pediatric (+6mo)
4. Identify earliest LOE date (first patent expiry + exclusivity end)
```

### Phase 2: Patent Landscape Mapping

```
1. ppubs_search_patents → search by:
   - Drug name / INN / USAN
   - Mechanism of action keywords
   - Target gene/protein name
   - Assignee (originator company)
2. For each relevant patent:
   - Full claims analysis (independent claims define scope)
   - Priority date, filing date, grant date, expiry date
   - Assignment chain (who currently owns it)
3. Categorize patents:
   - Core (composition of matter) — strongest, expires first
   - Formulation — extends protection for specific forms
   - Method of use — indication-specific, can be designed around
   - Process — manufacturing method, weakest
```

### Phase 3: Freedom-to-Operate Assessment

```
1. Define the target product profile (indication, formulation, route)
2. Search patents by:
   - CPC class (e.g., A61K for pharmaceuticals, C07D for heterocycles)
   - Key structural features / SMILES substructure
   - Target/mechanism keywords
3. For each blocking patent:
   - Analyze independent claims for overlap
   - Check expiry date (expired = no issue)
   - Check assignment (is this a competitor's patent?)
   - Assess design-around options
4. Risk classification: Freedom (no blocking), Caution (design-around possible), Block (unavoidable)
```

### Phase 4: Patent Cliff / LOE Timeline

```
1. List all drugs for a company or therapeutic area
2. For each: Orange Book patents + exclusivity dates
3. Calculate LOE date = latest of (patent expiry, exclusivity end)
4. Sort by LOE date → patent cliff timeline
5. Cross-reference with revenue (pharma-financial-analyst)
6. Revenue at risk = drug revenue × expected generic erosion (typically 80-90% over 2 years)
```

### Phase 5: Paragraph IV / Biosimilar Entry Analysis

```
1. FDA Orange Book → identify listed patents for target drug
2. ppubs_get_full_document → review claims breadth
3. Assess Paragraph IV certification viability:
   - Claim interpretation (narrow vs broad claims)
   - Potential invalidity arguments (prior art, obviousness)
   - Design-around feasibility
4. For biosimilars: identify interchangeability pathway, patent dance timeline
5. Estimate earliest possible generic/biosimilar entry date
```

---

## Patent Types in Pharma

| Patent Type | Scope | Strength | Typical Life |
|------------|-------|----------|-------------|
| Composition of Matter | New chemical entity itself | **Strongest** — hardest to design around | 20 years from filing |
| Salt/Polymorph | Specific crystal forms | Moderate — limited to specific form | 20 years |
| Formulation | Delivery system, dosage form | Moderate — can be designed around | 20 years |
| Method of Use | Specific indication/dosing | Weak-moderate — indication-specific | 20 years |
| Process | Manufacturing method | **Weakest** — easily designed around | 20 years |

## Key Exclusivity Types (US)

| Exclusivity | Duration | Trigger |
|------------|----------|---------|
| NCE (New Chemical Entity) | 5 years | First NDA for new molecule |
| New Clinical Investigation | 3 years | New indication/formulation supplement |
| Orphan Drug | 7 years | Approval for orphan indication |
| Pediatric | +6 months | Completion of pediatric studies |
| Patent Challenge (180-day) | 180 days | First successful Paragraph IV filer |

## Completeness Checklist

- [ ] Orange Book patents mapped with types and expiry dates
- [ ] Patent landscape searched (composition, formulation, method of use)
- [ ] Each patent classified by type and strength
- [ ] Assignment/ownership chain verified
- [ ] Patent family/continuity mapped
- [ ] LOE date calculated (latest of patent + exclusivity)
- [ ] Freedom-to-operate assessed for target product
- [ ] Paragraph IV / biosimilar entry feasibility analyzed
- [ ] Revenue impact of LOE estimated (with pharma-financial-analyst)
