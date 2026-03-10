---
name: infectious-disease-analyst
description: Anti-infective drug development research analyst. Therapeutic landscape mapping, target literature review, clinical trial pipeline analysis, approved therapeutics catalog, preprint monitoring. Use when user mentions infectious disease, anti-infective, antiviral, antibacterial, antifungal, antiparasitic, antimicrobial, antibiotic, AMR, antimicrobial resistance, pathogen, HIV, HCV, HBV, RSV, influenza, tuberculosis, malaria, COVID, SARS, MRSA, emerging disease, pandemic preparedness, anti-infective pipeline, infectious disease drug development, or tropical disease.
---

# Infectious Disease Analyst

Anti-infective drug development research. Analyzes published literature and public databases to support therapeutic development programs for infectious disease indications. Uses Open Targets for target-disease evidence, ChEMBL for bioactivity data, DrugBank for approved therapeutics, PubMed/BioRxiv for literature, ClinicalTrials.gov for pipeline analysis, FDA for regulatory intelligence, and PubChem for chemical data.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_infectious-disease-analyst_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Target validation and druggability assessment → use `drug-target-validator`
- Drug repurposing screen for anti-infectives → use `drug-repurposing-analyst`
- Safety and adverse event monitoring for anti-infectives → use `pharmacovigilance-specialist`
- Clinical trial design and protocol analysis → use `clinical-trial-analyst`
- Systematic literature review methodology → use `systematic-literature-reviewer`
- Medicinal chemistry and SAR optimization → use `medicinal-chemistry`

## Cross-Reference: Other Skills

- **Target validation and druggability** → use drug-target-validator skill
- **Target identification and characterization** → use drug-target-analyst skill
- **Drug repurposing candidates** → use drug-repurposing-analyst skill
- **Safety and adverse events** → use pharmacovigilance-specialist skill
- **Clinical trial design and analysis** → use clinical-trial-analyst skill
- **Systematic literature reviews** → use systematic-literature-reviewer skill

## Available MCP Tools

### `mcp__opentargets__opentargets_info` (Target-Disease Associations)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `search_diseases` | Search diseases by name/synonym | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId` (Ensembl ID), `diseaseId` (EFO ID), `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes) | `id` (EFO ID) |

### `mcp__chembl__chembl_info` (Bioactivity & Compounds)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |
| `get_admet` | ADMET/drug-likeness properties | `chembl_id` |

### `mcp__drugbank__drugbank_info` (Approved Therapeutics)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_by_name` | Find drug by name | `query` |
| `get_drug_details` | Full drug profile (mechanism, pharmacodynamics, targets) | `drugbank_id` |
| `search_by_target` | All drugs acting on a target | `target`, `limit` |
| `get_drug_interactions` | Drug-drug interactions | `drugbank_id` |
| `get_similar_drugs` | Pharmacologically similar drugs | `drugbank_id`, `limit` |
| `get_pathways` | Metabolic/signaling pathways | `drugbank_id` |
| `search_by_category` | Drugs by therapeutic category | `category`, `limit` |
| `search_by_structure` | Structural similarity search | `smiles` or `inchi`, `limit` |
| `search_by_carrier` | Drugs using same carrier protein | `carrier`, `limit` |
| `search_by_transporter` | Drugs using same transporter | `transporter`, `limit` |
| `get_external_identifiers` | Cross-database IDs (PubChem, ChEMBL, KEGG) | `drugbank_id` |

### `mcp__pubmed__pubmed_articles` (Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__biorxiv__biorxiv_info` (Preprints)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_preprints` | Search BioRxiv/MedRxiv preprints | `query`, `num_results` |
| `get_preprint_details` | Full preprint metadata | `doi` |
| `get_categories` | List available categories | — |
| `search_published_preprints` | Preprints that became peer-reviewed | `query`, `num_results` |

### `mcp__ctgov__ctgov_info` (Clinical Trials)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_studies` | Search trials by keyword | `query`, `limit` |
| `get_study_details` | Full trial record | `nct_id` |
| `search_by_condition` | Trials for a disease/condition | `condition`, `limit` |
| `search_by_intervention` | Trials using a drug/treatment | `intervention`, `limit` |

### `mcp__fda__fda_info` (Regulatory Intelligence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search approved drugs | `query`, `limit` |
| `get_drug_label` | Full prescribing information | `drug_name` |
| `get_adverse_events` | Post-market adverse event reports | `drug_name`, `limit` |
| `search_by_active_ingredient` | Find drugs by ingredient | `ingredient` |
| `get_drug_interactions` | FDA-reported interactions | `drug_name` |
| `get_recalls` | Drug recall history | `query`, `limit` |
| `get_approvals` | Recent drug approvals | `query`, `limit` |
| `search_devices` | Medical device data | `query`, `limit` |

### `mcp__pubchem__pubchem_info` (Chemical Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_compounds` | Search by name/SMILES/InChI | `query`, `limit` |
| `get_compound_info` | Full compound profile | `cid` |
| `search_similar_compounds` | Structural similarity search | `smiles`, `threshold`, `limit` |
| `get_safety_data` | GHS hazard and safety data | `cid` |
| `get_patent_ids` | Associated patent IDs | `cid` |

### `mcp__kegg__kegg_data` (Disease Pathways & Drug Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_diseases` | Search KEGG disease entries | `query` |
| `get_disease_info` | Disease details (pathways, genes, drugs) | `disease_id` |
| `search_pathways` | Search pathways (e.g., infection-specific pathways) | `query` |
| `get_pathway_info` | Full pathway details | `pathway_id` |
| `get_pathway_genes` | All genes in a disease/infection pathway | `pathway_id` |
| `search_drugs` | Search KEGG drug entries | `query` |
| `get_drug_info` | Drug details (targets, interactions) | `drug_id` |
| `convert_identifiers` | Convert between KEGG and external IDs | `identifiers`, `source_db`, `target_db` |

---

## Anti-Infective Research Pipeline

### Phase 1: Disease Landscape Analysis

```
1. mcp__opentargets__opentargets_info(method: "search_diseases", query: "disease_name")
   → Get EFO disease ID and ontology classification

2. mcp__opentargets__opentargets_info(method: "get_disease_details", id: "EFO_xxxxxxx")
   → Full disease profile: subtypes, phenotypes, therapeutic areas

3. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "disease_name epidemiology treatment landscape review", num_results: 20)
   → Recent reviews and epidemiological data

4. mcp__biorxiv__biorxiv_info(method: "search_preprints", query: "disease_name therapeutics", num_results: 15)
   → Latest preprint research

5. mcp__kegg__kegg_data(method: "search_diseases", query: "disease_name")
   → Get KEGG disease entry with associated pathways, genes, and drugs
   mcp__kegg__kegg_data(method: "get_disease_info", disease_id: "H00001")
   → Full disease record: pathogen genes, host pathways, approved drugs

6. mcp__kegg__kegg_data(method: "get_pathway_genes", pathway_id: "hsa05170")
   → Get all genes in KEGG disease-specific pathway (e.g., HIV infection pathway)
```

### Phase 2: Published Target Literature Review

```
1. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.3, size: 30)
   → All published validated targets, ranked by evidence

2. For each top target:
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Target function, tractability, pathway involvement

3. mcp__chembl__chembl_info(method: "target_search", query: "target_name")
   → ChEMBL target classification and available bioactivity data

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "target_name drug_target validation infectious_disease", num_results: 15)
   → Published target validation studies
```

### Phase 3: Approved Therapeutics Landscape

```
1. mcp__drugbank__drugbank_info(method: "search_by_category", category: "anti-infective_category", limit: 50)
   → All approved therapeutics in this class

2. mcp__fda__fda_info(method: "search_drugs", query: "disease_indication", limit: 30)
   → FDA-approved drugs for this indication

3. For key approved drugs:
   mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   → Mechanism, pharmacodynamics, targets

4. mcp__chembl__chembl_info(method: "drug_search", query: "disease_indication", limit: 30)
   → All drugs with activity data in ChEMBL
```

### Phase 4: Clinical Trial Pipeline Analysis

```
1. mcp__ctgov__ctgov_info(method: "search_by_condition", condition: "disease_name", limit: 50)
   → Active clinical trials for this indication

2. mcp__ctgov__ctgov_info(method: "search_by_intervention", intervention: "drug_name", limit: 20)
   → Trials for specific investigational agents

3. Group trials by:
   - Phase (1, 2, 3, 4)
   - Mechanism of action
   - Sponsor (pharma vs academic)
   - Status (recruiting, completed, terminated)

4. mcp__fda__fda_info(method: "get_approvals", query: "anti-infective_class", limit: 20)
   → Recent regulatory approvals in this space
```

### Phase 5: Preprint Literature Monitoring

```
1. mcp__biorxiv__biorxiv_info(method: "search_preprints", query: "disease_name novel therapeutic target", num_results: 20)
   → Emerging targets from preprint literature

2. mcp__biorxiv__biorxiv_info(method: "search_published_preprints", query: "disease_name drug development", num_results: 15)
   → Preprints that became peer-reviewed (validated findings)

3. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "disease_name therapeutic target", start_date: "last_6_months", num_results: 20)
   → Recent peer-reviewed publications
```

### Phase 6: Evidence Synthesis Report

Compile findings into a structured report:

```
1. Disease Overview & Unmet Medical Need
2. Published Target Landscape (ranked by validation evidence)
3. Approved Therapeutics Catalog
4. Clinical Trial Pipeline Map (by phase and mechanism)
5. Emerging Research (preprint highlights)
6. Gap Analysis & Opportunities
7. Evidence Quality Assessment
```

---

## Target Assessment Framework

### Published Target Scoring (0-100)

| Dimension | Weight | Scoring Criteria |
|-----------|--------|-----------------|
| **Published Validation Evidence** | 30% | Human genetic association (10), functional studies (8), animal models (6), in vitro only (3), computational (1) |
| **Conservation Data** | 25% | Highly conserved across strains (10), conserved in major strains (7), variable (4), highly variable (1) |
| **Structural Tractability** | 25% | Crystal structure + binding pocket (10), AlphaFold high confidence (7), homology model (4), no structural data (1) |
| **Existing Chemical Matter** | 20% | Approved drug for target (10), clinical candidate (8), validated hit <1μM (6), screening hits (3), none (0) |

### Target Priority Classification

| Score | Priority | Recommendation |
|-------|----------|---------------|
| 80-100 | **HIGH** | Well-validated, tractable target with chemical matter — advance to lead optimization |
| 60-79 | **MEDIUM-HIGH** | Good evidence, tractable — invest in hit identification or expand SAR |
| 40-59 | **MEDIUM** | Partial evidence — requires additional validation studies |
| 20-39 | **LOW** | Limited evidence — early-stage research target |
| 0-19 | **EXPLORATORY** | Insufficient data — monitor literature |

---

## Disease Classification & Therapeutic Strategy

### Therapeutic Strategy by Disease Class

| Class | Key Target Strategies | Standard Approaches |
|-------|----------------------|-------------------|
| **Viral** | Polymerase, protease, entry/fusion, integrase, capsid | Direct-acting antivirals, host-directed therapy, combination regimens |
| **Bacterial** | Cell wall synthesis, protein synthesis, DNA replication, folate pathway | Beta-lactams, fluoroquinolones, macrolides, combination therapy |
| **Fungal** | Ergosterol synthesis, cell wall (glucan), nucleic acid synthesis | Azoles, echinocandins, polyenes |
| **Parasitic** | Metabolic enzymes, ion channels, cytoskeletal proteins | Combination chemotherapy, target-specific agents |

### Resistance Considerations

| Factor | Assessment Method |
|--------|------------------|
| Known resistance mechanisms | PubMed literature search for "[drug class] resistance mechanism" |
| Resistance prevalence | WHO/CDC surveillance reports via PubMed |
| Cross-resistance patterns | DrugBank drug class analysis + literature |
| Resistance barrier | Number of mutations needed — single vs multi-step |

---

## Evidence Grading

| Tier | Evidence Type | Criteria |
|------|-------------|----------|
| **T1** | Clinical/regulatory | Phase 3 data, FDA-approved indication, clinical guidelines |
| **T2** | Clinical-stage | Phase 1-2 data, clinical proof-of-concept published |
| **T3** | Preclinical published | In vivo efficacy, validated in vitro models, published in peer-reviewed journals |
| **T4** | Early research | Computational predictions, in vitro screening, preprint data |

### Evidence Quality Checklist

```
For each key finding, document:
□ Source database (Open Targets, ChEMBL, DrugBank, PubMed, ClinicalTrials.gov)
□ Evidence tier (T1-T4)
□ Publication year (recency matters in fast-moving fields)
□ Replication status (confirmed by independent groups?)
□ Clinical relevance (translatable to human disease?)
```

---

## Clinical Trial Pipeline Metrics

### Pipeline Health Assessment

| Metric | What to Measure | Source |
|--------|----------------|--------|
| **Pipeline depth** | Number of candidates by phase | ClinicalTrials.gov |
| **Mechanism diversity** | Distinct MOAs in development | ChEMBL + ClinicalTrials.gov |
| **Sponsor mix** | Industry vs academic ratio | ClinicalTrials.gov |
| **Attrition signals** | Terminated/suspended trials | ClinicalTrials.gov status field |
| **Time to approval** | Phase transition timelines | FDA approvals + trial dates |
| **Combination strategies** | Multi-drug regimen trials | ClinicalTrials.gov intervention field |

### Trial Landscape Report Template

```
For each disease indication:
1. Total active trials: [N]
2. By phase: Phase 1 [n], Phase 2 [n], Phase 3 [n], Phase 4 [n]
3. By mechanism: [list top 5 MOAs with trial counts]
4. Novel mechanisms in Phase 1: [list emerging approaches]
5. Recent completions: [last 12 months]
6. Recent terminations: [with reasons if available]
7. Key sponsors: [top 5 by trial count]
```

---

## Preprint Intelligence Framework

### Why Preprints Matter for Anti-Infective Research

- Peer review takes 6-12 months; preprints provide early access
- Critical during emerging disease situations
- Track which preprints later become peer-reviewed publications

### Preprint Monitoring Workflow

```
1. mcp__biorxiv__biorxiv_info(method: "search_preprints", query: "disease target therapeutic")
   → New research findings

2. mcp__biorxiv__biorxiv_info(method: "search_published_preprints", query: "same_query")
   → Validated preprints (now peer-reviewed)

3. Cross-reference with PubMed:
   mcp__pubmed__pubmed_articles(method: "search_advanced", term: "same_topic", start_date: "recent")
   → Compare preprint claims with peer-reviewed evidence

4. Quality assessment:
   - Sample size and methodology
   - Replication by independent groups
   - Consistency with established knowledge
   - Peer-review status
```

### Preprint Evidence Weighting

| Status | Weight | Notes |
|--------|--------|-------|
| Now peer-reviewed | Full weight (T2-T3) | Validated by peer review |
| >100 citations, no concerns | 80% weight | Community-validated |
| Recent, single group | 50% weight | Treat as preliminary |
| Contradicts established findings | 20% weight | Flag for further review |

---

## Multi-Agent Workflow Examples

**"Map the therapeutic landscape for drug-resistant tuberculosis"**
1. Infectious Disease Analyst → Approved therapeutics catalog, clinical trial pipeline, target landscape from Open Targets, preprint monitoring
2. Drug Target Analyst → Deep characterization of top 5 targets (bioactivity data, SAR)
3. Drug Repurposing Analyst → Screen approved drugs for TB target activity
4. Clinical Trial Analyst → Detailed analysis of Phase 2-3 combination trials

**"Identify research targets for a novel antifungal program"**
1. Infectious Disease Analyst → Published target literature, approved antifungal landscape, clinical pipeline gaps
2. Drug Target Validator → Validate top 3 targets (druggability, safety, GO/NO-GO scores)
3. Binder Discovery Specialist → Known ligands and chemical matter for validated targets
4. Systematic Literature Reviewer → Comprehensive review of target validation evidence

**"Analyze the HIV treatment pipeline and emerging targets"**
1. Infectious Disease Analyst → Current approved therapies, clinical trials by mechanism, preprint intelligence
2. Network Pharmacologist → Map drug-target-disease network for HIV targets
3. Pharmacovigilance Specialist → Safety profiles of approved antiretrovirals
4. Clinical Trial Analyst → Pipeline analysis by phase, sponsor, and mechanism

**"Evaluate antimicrobial resistance trends and new therapeutic approaches"**
1. Infectious Disease Analyst → Literature landscape, approved pipeline, resistance data from PubMed
2. Drug Target Analyst → Novel target characterization (essential bacterial enzymes, virulence factors)
3. Chemical Safety Toxicology → Safety assessment of candidate compounds
4. FDA Consultant → Regulatory pathways for anti-infective approvals (QIDP, LPAD)

## Completeness Checklist

- [ ] Disease landscape analyzed with EFO ID and epidemiological context
- [ ] Target landscape retrieved from Open Targets with evidence scores
- [ ] Approved therapeutics cataloged from DrugBank and FDA databases
- [ ] Clinical trial pipeline mapped by phase, mechanism, and sponsor
- [ ] Preprint literature monitored and cross-referenced with peer-reviewed sources
- [ ] Resistance mechanisms and prevalence data included
- [ ] Evidence tier (T1-T4) assigned to all key findings
- [ ] Gap analysis identifying unmet needs and opportunities completed
- [ ] KEGG pathways explored for pathogen-specific targets
- [ ] Report file created with all sections populated (no `[Analyzing...]` remaining)
