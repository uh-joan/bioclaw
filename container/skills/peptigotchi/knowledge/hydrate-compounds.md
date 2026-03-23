# Compound Hydration Task

You are hydrating the peptigotchi compound database from 12 → 101 compounds. The seed list is in `tpl-seed.json`. The target schema is in `compounds.json` (12 existing entries — do NOT overwrite or modify them).

## Process

For each compound in `tpl-seed.json` that is NOT already in `compounds.json`, run this pipeline:

### Step 1: PubChem Identification
Use `mcp__pubchem__*` tools to:
- Search by compound name
- Get CID, molecular formula, synonyms
- Confirm it is a peptide or peptide-adjacent compound
- If not found, set `pubchem_cid: 0` and note in aliases

### Step 2: Mechanism & Evidence
Use `mcp__pubmed__*` and `mcp__openalex__*` to:
- Search for "[compound name] mechanism of action"
- Search for "[compound name] clinical trial" or "[compound name] human study"
- Determine evidence grade:
  - `"green"` = FDA-approved with Phase 3 RCTs
  - `"yellow"` = Some human data OR strong animal data with plausible mechanism
  - `"red"` = No human data, preclinical only or theoretical

### Step 3: Regulatory Status
Use `mcp__fda__*` and `mcp__chembl__*` to:
- Check FDA approval status
- Check ChEMBL max phase
- Determine fda_category: "prescription", "investigational", "category_2_as_of_2024", "research_chemical"
- Check if included in RFK Feb 2026 Category 1 return list

### Step 4: Dosing & Administration
Use `mcp__pubmed__*` and `mcp__drugbank__*` to:
- Find pharmacokinetic data (routes, doses, frequency)
- Find common vial sizes from literature/community sources
- If only animal data, note "animal-derived dosing" in frequency field

### Step 5: Interactions
Use `mcp__drugbank__*` and `mcp__chembl__*` to:
- Search for known drug interactions
- Identify target activity that could conflict with common peptide stacks

### Step 6: Write to compounds.json

**CRITICAL: Write incrementally.** After completing each compound, immediately:

1. Read the current `compounds.json`
2. Append the new compound to the `compounds` array
3. Write the updated file back
4. Log: `✓ {compound_name} — {evidence_grade} — {pubchem_cid}`

Use this exact schema for each new compound:

```json
{
  "id": "compound-id",
  "name": "Compound Name",
  "aliases": ["Alias1", "Alias2"],
  "pubchem_cid": 12345,
  "category": "tpl_category from seed file",
  "administration": {
    "routes": ["subcutaneous", "oral", "intranasal", "topical", "intramuscular"],
    "typical_dose": { "min_mcg": 100, "max_mcg": 500 },
    "frequency": "1x daily",
    "common_vial_sizes_mg": [5, 10],
    "reconstitution": {
      "solvent": "bacteriostatic_water",
      "typical_volume_ml": 2,
      "storage_days_refrigerated": 28
    }
  },
  "mechanism_summary": "2-3 sentences on mechanism of action from PubMed/OpenAlex.",
  "evidence": {
    "grade": "green|yellow|red",
    "detail": "2-3 sentences on what studies exist, evidence quality, key papers."
  },
  "regulatory": {
    "fda_status": "approved|not_approved|withdrawn",
    "fda_category": "prescription|investigational|category_2_as_of_2024|research_chemical",
    "note": "Relevant regulatory context",
    "last_updated": "2026-03"
  },
  "community_insights": {
    "top_positive_use": "Most reported positive use case",
    "top_negative_report": "Most reported side effect or concern",
    "common_mistake": "Frequent error users make",
    "pro_tip": "Practical advice from literature + community"
  }
}
```

## Category Mapping

Map `tpl_category` from seed to these peptigotchi categories:
- `weight_loss` → `"glp1"` (if GLP-1 agonist) or `"weight_loss"`
- `tissue_repair` → `"healing"`
- `growth_hormone` → `"gh_secretagogue"`
- `cognitive` → `"nootropic"`
- `skin_hair` → `"cosmetic"`
- `sexual_function` → `"sexual_health"`
- `anti_aging` → `"regenerative"` or `"anti_aging"`
- `immune` → `"immune"`
- `sleep_stress` → `"sleep_stress"` or `"nootropic"`

## Evidence Tier Seeding

Use `tpl-seed.json` evidence_tiers as a starting point, but VERIFY and OVERRIDE with actual MCP data:
- Tier 1 → likely `"green"`
- Tier 2 → likely `"yellow"` or `"green"`
- Tier 3 → likely `"yellow"`
- Tier 4 → likely `"red"`

## Blends and Combinations

For blend entries (e.g., "BPC-157 + TB-500"), reference the individual compound data. Note the blend in mechanism_summary and community_insights.

## Order

Process compounds in this order:
1. FDA-approved compounds first (Tier 1) — these have the most MCP data
2. Late-stage clinical (Tier 2)
3. Limited human data (Tier 3)
4. No human data (Tier 4)
5. Cosmetic peptides last (least MCP coverage expected)

## Error Handling

If MCP calls return no data for a compound:
- Still create the entry with what you have
- Set `pubchem_cid: 0` if not found
- Use `"red"` evidence grade
- Note "Limited data available from biomedical databases" in evidence.detail
- Still write it to compounds.json — partial data is better than no entry

## Also Update: fingerprints.json and reconstitution.json

After adding a compound to compounds.json, also add entries to:

### fingerprints.json
Add a fingerprint entry with known side effects from PubMed/DrugBank. Schema:
```json
{
  "compound_id": "compound-id",
  "watch_for": [
    { "symptom": "symptom_name", "frequency": "common|uncommon|rare", "severity": "mild|moderate|severe", "mechanism": "Why this happens", "onset_days": { "min": 1, "max": 14 } }
  ],
  "critical_alerts": [
    { "condition": "when to worry", "action": "what to do" }
  ],
  "dose_dependent": true,
  "context_modifiers": [
    { "when": "user_condition", "effect": "what changes" }
  ]
}
```

### reconstitution.json
Add to the `compounds` object if the compound requires reconstitution:
```json
"compound-id": {
  "common_vial_sizes_mg": [5, 10],
  "recommended_solvent": "bacteriostatic_water",
  "recommended_volume_ml": [1, 2],
  "notes": "Reconstitution notes"
}
```

Skip reconstitution for topical-only or oral-only compounds.

## Progress Tracking

After every 10 compounds, write a progress line to `hydration-progress.log`:
```
[2026-03-23T12:00:00] 10/89 compounds hydrated. Last: MK-677. Errors: 0
```
