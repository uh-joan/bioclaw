---
name: target-research
description: Comprehensive biological target intelligence gathering through 9 parallel research paths. Protein identity, structure, interactions, pathways, expression, variants, drugs, and literature. The MOST thorough target profiling skill. Use when user mentions target research, target profiling, target intelligence, target characterization, protein research, gene research, target dossier, target deep dive, comprehensive target analysis, target landscape, target biology, or target report.
---

# Target Research

Comprehensive biological target intelligence gathering through 9 parallel research paths covering protein identity, structure, interactions, pathways, expression, variants, drugs, and literature. This is the MOST thorough target profiling skill in the system — pure intelligence gathering with no scoring or GO/NO-GO decisions.

**Key distinction from related skills:**
- **drug-target-analyst** focuses on druggability, SAR, and bioactivity data
- **drug-target-validator** scores targets with a quantitative GO/NO-GO pipeline
- **target-research** (this skill) is pure, exhaustive intelligence gathering across all biological dimensions

## Cross-Reference: Other Skills

- **Druggability assessment, SAR, bioactivity analysis** -> use drug-target-analyst skill
- **Quantitative target validation score, GO/NO-GO decisions** -> use drug-target-validator skill
- **Network-level pathway pharmacology and polypharmacology** -> use network-pharmacologist skill
- **Disease biology, epidemiology, mechanisms** -> use disease-research skill
- **Binder/lead discovery and optimization** -> use binder-discovery-specialist skill

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

### `mcp__chembl__chembl_info` (Bioactivity & SAR)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |
| `get_admet` | ADMET/drug-likeness properties | `chembl_id` |

### `mcp__drugbank__drugbank_info` (Drug-Target Pharmacology)

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

### `mcp__pubmed__pubmed_articles` (Target Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__pubchem__pubchem_info` (Chemical & Structural Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_compounds` | Compound lookup by name/CID/SMILES | `query`, `search_type` |
| `get_compound_properties` | Molecular properties (MW, logP, PSA, rotatable bonds) | `cid` |
| `get_compound_info` | Full compound record | `cid` |
| `get_safety_data` | GHS hazard classifications, signal words, pictograms | `cid` |
| `search_similar_compounds` | Structural analogs for scaffold analysis | `smiles`, `threshold` |
| `analyze_stereochemistry` | Stereo-specific assessment | `cid` |
| `get_patent_ids` | Patent landscape | `cid` |
| `get_bioassay_results` | Bioassay activity data | `cid`, `limit` |
| `get_3d_conformer` | 3D structure for binding analysis | `cid` |
| `get_pharmacology` | Pharmacological action data | `cid` |
| `get_synonyms` | All synonyms and identifiers | `cid` |
| `classify_compound` | Chemical classification hierarchy | `cid` |

### `mcp__fda__fda_info` (Regulatory & Safety Intelligence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `lookup_drug` | Search drugs by name, adverse events, labels, recalls, shortages | `search_term`, `search_type`, `limit`, `count` |
| `lookup_device` | Search medical devices | `search_term`, `search_type`, `limit` |
| `search_orange_book` | Find brand/generic drug products by name | `drug_name`, `include_generics` |
| `get_therapeutic_equivalents` | Find AB-rated generic equivalents | `drug_name` |
| `get_patent_exclusivity` | Look up patents and exclusivity by NDA number | `nda_number` |
| `analyze_patent_cliff` | Forecast when a drug loses patent protection | `drug_name`, `years_ahead` |
| `search_purple_book` | Find biological products and biosimilars | `drug_name` |
| `get_biosimilar_interchangeability` | Check which biosimilars are interchangeable | `reference_product` |

### `mcp__ctgov__ctgov_info` (Clinical Trial Intelligence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search clinical trials | `condition`, `intervention`, `phase`, `status`, `location`, `lead`, `ages`, `studyType`, `pageSize` |
| `get` | Get full trial details by NCT ID | `nctId` |
| `suggest` | Autocomplete terms | `input`, `dictionary` |
| `stats` | Trial statistics and counts | `condition`, `intervention` |

### `mcp__nlm__nlm_ct_codes` (Clinical Coding & Terminology)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `icd-10-cm` | Diagnosis codes | `terms`, `maxList` |
| `icd-11` | ICD-11 diagnosis codes (WHO 2023) | `terms`, `maxList` |
| `rx-terms` | Drug names with strengths/forms | `terms`, `maxList` |
| `loinc-questions` | Lab test codes (LOINC) | `terms`, `maxList` |
| `conditions` | Medical conditions with ICD mappings | `terms`, `maxList` |
| `npi-organizations` | Healthcare organization lookup | `terms`, `maxList` |
| `npi-individuals` | Provider lookup by name/specialty | `terms`, `maxList` |
| `hcpcs-LII` | Procedure/equipment codes | `terms`, `maxList` |
| `ncbi-genes` | Gene information (BRCA1, TP53) | `terms`, `maxList` |
| `major-surgeries-implants` | Surgical procedure codes | `terms`, `maxList` |
| `hpo-vocabulary` | Human Phenotype Ontology terms | `terms`, `maxList` |

---

## Report-First Approach

**MANDATORY:** Before beginning any research, create the report file with all section placeholders. Populate progressively as each research path completes. This ensures no section is forgotten and the user can see progress.

```
1. Create file: target_research_[GENE_SYMBOL].md

2. Write skeleton with these sections:
   # Target Research Report: [GENE_SYMBOL] ([Full Name])
   ## 1. Identifier Resolution
   ## 2. OpenTargets Foundation
   ## 3. Protein Identity & Function
   ## 4. Structural Data
   ## 5. Protein-Protein Interactions
   ## 6. Pathway Context
   ## 7. Expression Profile
   ## 8. Variant Landscape
   ## 9. Drug Landscape
   ## 10. Literature Deep Dive
   ## 11. Evidence Summary
   ## 12. Completeness Audit

3. Fill each section as the corresponding PATH completes
4. Mark incomplete sections as "[PENDING — PATH X]" until populated
```

---

## Mandatory Identifier Resolution

**MUST be completed before any research path begins.** All downstream queries depend on correct cross-database identifiers.

```
1. mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL", size: 10)
   -> Get Ensembl gene ID (ENSG00000xxxxx)
   -> Confirm correct gene (check aliases, description)

2. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Get UniProt ID (Pxxxxx or Qxxxxx)
   -> Get protein name, function, subcellular location

3. mcp__chembl__chembl_info(method: "target_search", query: "GENE_SYMBOL", limit: 10)
   -> Get ChEMBL target ID (CHEMBLxxxxx)
   -> Confirm target type (SINGLE PROTEIN vs PROTEIN COMPLEX)

4. mcp__nlm__nlm_ct_codes(method: "ncbi-genes", terms: "GENE_SYMBOL", maxList: 5)
   -> Get NCBI Gene ID
   -> Confirm chromosomal location

5. mcp__drugbank__drugbank_info(method: "search_by_target", target: "GENE_SYMBOL", limit: 5)
   -> Get DrugBank target reference
   -> Note any existing drug-target relationships
```

**Critical:** If the gene symbol returns multiple targets or protein isoforms, resolve ambiguity before proceeding. Record ALL canonical identifiers:
- Gene symbol: (e.g., EGFR)
- Ensembl: ENSG00000xxxxx
- UniProt: Pxxxxx
- ChEMBL: CHEMBLxxxxx
- NCBI Gene: xxxxx
- DrugBank target reference

---

## 9 Research Paths

### PATH 0: OpenTargets Foundation

Establish the baseline target profile from Open Targets as the anchor for all subsequent research.

```
1. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Function description, protein class, subcellular location
   -> Tractability assessment (small molecule, antibody, other modalities)
   -> Pharos Target Development Level (Tclin/Tchem/Tbio/Tdark)
   -> Reactome pathways, GO biological processes

2. mcp__opentargets__opentargets_info(method: "search_diseases", query: "primary_disease_of_interest")
   -> Get EFO disease IDs for downstream association queries

3. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx", size: 50)
   -> Evidence scores across all data types (genetic, somatic, literature, known drug, animal model)
   -> For EACH significant disease association, record the score breakdown

4. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.3, size: 50)
   -> Competitive target landscape: where does this target rank?
```

**Output:** Target overview card with function, location, tractability, top disease associations, and competitive rank.

### PATH 1: Protein Identity & Function

Deep characterization of the protein product — isoforms, domains, post-translational modifications, molecular function.

```
1. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Protein domains, molecular function GO terms
   -> Protein family classification

2. mcp__nlm__nlm_ct_codes(method: "ncbi-genes", terms: "GENE_SYMBOL", maxList: 5)
   -> Gene summary, aliases, chromosomal location, RefSeq IDs

3. mcp__nlm__nlm_ct_codes(method: "hpo-vocabulary", terms: "GENE_SYMBOL", maxList: 10)
   -> Associated human phenotype ontology terms (monogenic disease phenotypes)

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL protein structure function domain review", num_results: 15)
   -> Review articles covering protein biology

5. mcp__pubchem__pubchem_info(method: "search_compounds", query: "GENE_SYMBOL inhibitor", search_type: "name")
   -> Known chemical probes (confirms enzymatic/binding function)
```

**Output:** Protein identity card — domains, function, family, isoforms, key GO terms, phenotype associations.

### PATH 2: Structural Data

Collect all available structural information for rational drug design assessment.

```
1. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL crystal structure X-ray cryo-EM binding site", num_results: 15)
   -> Published structural studies, PDB IDs

2. mcp__pubchem__pubchem_info(method: "search_compounds", query: "GENE_SYMBOL", search_type: "name")
   -> Find CIDs for known ligands

3. mcp__pubchem__pubchem_info(method: "get_3d_conformer", cid: CID_NUMBER)
   -> 3D conformer of known ligand (binding mode inference)

4. mcp__pubchem__pubchem_info(method: "get_compound_properties", cid: CID_NUMBER)
   -> Physicochemical properties of best ligands (MW, logP, PSA)

5. mcp__pubchem__pubchem_info(method: "search_similar_compounds", smiles: "SMILES_STRING", threshold: 80)
   -> Structural analogs for chemotype diversity assessment
```

**Output:** Structural dossier — available PDB structures, binding sites, ligand co-crystals, structural druggability assessment.

**Structural Readiness Classification:**

| Level | Status | Implication |
|-------|--------|------------|
| **High** | Co-crystal structure with ligand available (PDB) | Structure-based drug design possible |
| **Medium** | Apo structure available, homology model feasible | Computational docking possible |
| **Low** | No structure, no close homolog | Ligand-based or phenotypic screening required |

### PATH 3: Protein-Protein Interactions

Map the target's interaction network — binding partners, complexes, functional associations.

```
1. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Known protein interactions from Open Targets
   -> Pathway membership (Reactome)

2. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL protein interaction binding partner complex co-immunoprecipitation", num_results: 20)
   -> Published PPI studies (co-IP, yeast two-hybrid, proximity ligation)

3. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "GENE_SYMBOL interactome STRING network", num_results: 10)
   -> Network-level interaction studies

4. mcp__drugbank__drugbank_info(method: "search_by_target", target: "GENE_SYMBOL", limit: 20)
   -> Drugs targeting this protein (confirms functional relevance of interactions)

5. mcp__drugbank__drugbank_info(method: "search_by_carrier", carrier: "GENE_SYMBOL", limit: 10)
   -> Is this protein a drug carrier? (relevant for pharmacokinetics)

6. mcp__drugbank__drugbank_info(method: "search_by_transporter", transporter: "GENE_SYMBOL", limit: 10)
   -> Is this protein a drug transporter? (relevant for drug resistance, efflux)
```

**Output:** Interaction map — top interactors (minimum 20 if available), functional categories, complex membership, hub vs peripheral status.

### PATH 4: Pathway Context

Place the target within its biological signaling and metabolic pathways.

```
1. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Reactome pathways, GO biological process terms

2. mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   -> Metabolic/signaling pathway mapping (if drug exists for target)

3. mcp__drugbank__drugbank_info(method: "search_by_target", target: "upstream_target", limit: 10)
   -> Drugs hitting upstream nodes in the pathway

4. mcp__drugbank__drugbank_info(method: "search_by_target", target: "downstream_target", limit: 10)
   -> Drugs hitting downstream nodes (combination rationale)

5. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL signaling pathway mechanism feedback", num_results: 15)
   -> Pathway reviews, feedback loops, compensatory mechanisms

6. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL resistance compensatory bypass", num_results: 10)
   -> Known resistance mechanisms upon target inhibition
```

**Output:** Pathway map — upstream regulators, downstream effectors, parallel pathways, feedback loops, redundancy assessment, combination opportunities.

### PATH 5: Expression Profile

Characterize where and when the target is expressed — tissue distribution, disease-specific expression changes.

```
1. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Expression data from Open Targets (GTEx, HPA)
   -> Tissue-specific expression levels

2. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL expression tissue distribution RNA-seq single-cell", num_results: 15)
   -> Expression profiling studies

3. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL overexpression upregulation disease", num_results: 15)
   -> Disease-specific expression changes (tumor vs normal, inflamed vs healthy)

4. mcp__nlm__nlm_ct_codes(method: "loinc-questions", terms: "GENE_SYMBOL", maxList: 5)
   -> Clinical lab tests that measure this target (if any — indicates clinical utility)

5. mcp__nlm__nlm_ct_codes(method: "conditions", terms: "GENE_SYMBOL deficiency", maxList: 10)
   -> Conditions associated with target loss-of-function
```

**Output:** Expression atlas — high-expression tissues, disease-altered expression, cell-type specificity, clinical measurement availability.

### PATH 6: Variant Landscape

Catalog genetic variants affecting the target — germline, somatic, pharmacogenomic.

```
1. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", size: 100)
   -> Genetic association evidence (GWAS hits, somatic mutations)
   -> Filter for genetic_association and somatic_mutation data types

2. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL mutation variant polymorphism GWAS", num_results: 20)
   -> Published variant studies

3. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL pharmacogenomics drug response genotype", num_results: 10)
   -> Pharmacogenomic variants affecting drug response

4. mcp__nlm__nlm_ct_codes(method: "ncbi-genes", terms: "GENE_SYMBOL", maxList: 5)
   -> Gene-level variant summary (ClinVar, OMIM links)

5. mcp__nlm__nlm_ct_codes(method: "hpo-vocabulary", terms: "GENE_SYMBOL mutation", maxList: 10)
   -> Phenotypic consequences of loss-of-function variants

6. mcp__nlm__nlm_ct_codes(method: "icd-10-cm", terms: "GENE_SYMBOL deficiency", maxList: 5)
   -> Clinical diagnoses linked to target variants

7. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL gain-of-function activating mutation oncogene", num_results: 10)
   -> Gain-of-function variants (oncology context)
```

**Output:** Variant catalog — GWAS associations, Mendelian mutations, somatic hotspots, pharmacogenomic variants, clinical phenotypes, functional impact.

### PATH 7: Drug Landscape

Comprehensive survey of all therapeutic agents targeting or related to this target.

```
1. mcp__drugbank__drugbank_info(method: "search_by_target", target: "GENE_SYMBOL", limit: 30)
   -> All drugs with known activity against this target

2. mcp__chembl__chembl_info(method: "get_bioactivity", target_id: "CHEMBLxxxxx", limit: 100)
   -> Complete bioactivity dataset (IC50, Ki, EC50, Kd values)

3. mcp__chembl__chembl_info(method: "drug_search", query: "GENE_SYMBOL", limit: 30)
   -> Drugs in ChEMBL database linked to target

4. For each approved drug found:
   mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   -> Mechanism, pharmacodynamics, indications, contraindications

5. mcp__fda__fda_info(method: "lookup_drug", search_term: "drug_name", search_type: "label", limit: 10)
   -> FDA label information, approved indications

6. mcp__fda__fda_info(method: "search_orange_book", drug_name: "drug_name")
   -> Approval status, formulations, generic availability

7. mcp__fda__fda_info(method: "search_purple_book", drug_name: "drug_name")
   -> Biological products and biosimilars (if applicable)

8. mcp__ctgov__ctgov_info(method: "search", intervention: "GENE_SYMBOL inhibitor", pageSize: 50)
   -> Active and completed clinical trials

9. mcp__ctgov__ctgov_info(method: "stats", intervention: "GENE_SYMBOL inhibitor")
   -> Trial statistics and phase distribution

10. mcp__fda__fda_info(method: "lookup_drug", search_term: "drug_name", search_type: "adverse_events", count: "patient.reaction.reactionmeddrapt.exact", limit: 20)
    -> Post-market safety signals for approved drugs hitting this target

11. mcp__pubchem__pubchem_info(method: "get_bioassay_results", cid: CID_NUMBER, limit: 50)
    -> Bioassay confirmatory data for key compounds

12. mcp__pubchem__pubchem_info(method: "get_pharmacology", cid: CID_NUMBER)
    -> Pharmacological action data
```

**Output:** Drug landscape map — approved drugs, clinical candidates, tool compounds, bioactivity ranges, mechanism classes, trial pipeline, safety signals.

### PATH 8: Literature Deep Dive

Exhaustive literature mining across all dimensions of target biology.

```
1. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL review", num_results: 20)
   -> Comprehensive review articles (start here for orientation)

2. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "GENE_SYMBOL", start_date: "2022/01/01", num_results: 30)
   -> Recent publications (last 2-3 years) — cutting-edge findings

3. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL therapeutic target drug development", num_results: 15)
   -> Target-as-drug-target literature

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL knockout mouse phenotype", num_results: 10)
   -> In vivo biology — knockout phenotype is proxy for on-target effects

5. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL biomarker diagnostic prognostic", num_results: 10)
   -> Biomarker utility (clinical trial stratification, companion diagnostics)

6. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL CRISPR siRNA knockdown functional", num_results: 10)
   -> Functional genomics studies (CRISPR screens, siRNA knockdown)

7. For key articles found, get full metadata:
   mcp__pubmed__pubmed_articles(method: "get_article_metadata", pmid: "PMID_NUMBER")
   -> Full abstract, authors, journal, citations
```

**Output:** Literature synthesis — key reviews, recent breakthroughs, therapeutic rationale papers, functional studies, biomarker studies, landmark publications with PMIDs.

---

## Evidence Grading System (T1-T4)

Assign an evidence grade to each major finding in the report.

| Grade | Evidence Type | Description | Examples |
|-------|-------------|-------------|----------|
| **T1 — Clinical Proof** | Human clinical data showing target modulation leads to therapeutic benefit | Approved drug, positive Phase 2/3 trial data | Sotorasib approved for KRAS G12C NSCLC |
| **T2 — Functional Studies** | CRISPR/siRNA knockdown, overexpression in human cells showing disease-relevant phenotype change | Cell-based functional validation | CRISPR screen identifies gene as essential in cancer cell line |
| **T3 — Associations** | GWAS, Mendelian genetics, somatic mutations, expression changes in disease tissue | Correlative but not causal proof | GWAS variant in gene locus associated with disease risk |
| **T4 — Predictions** | Text mining, pathway inference, animal model only, computational prediction | Hypothesis-generating only | Network analysis places target in disease-relevant pathway |

**Grading rules:**
- Every factual claim in the report MUST carry a T-grade tag
- Multiple evidence types for the same finding upgrade the grade (T3 + T2 = report as T2)
- Absence of evidence is NOT T4 — it is "No data" and must be explicitly stated

---

## Collision-Aware Literature Search

**MANDATORY before PubMed deep dive:** Gene symbols are frequently ambiguous (e.g., ACE = angiotensin-converting enzyme OR a gene in Drosophila, BRAF = the kinase OR unrelated contexts, CAT = catalase OR feline medicine).

### Detection Protocol

```
1. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL", num_results: 20)
   -> Scan first 20 results for relevance

2. Count off-topic results:
   - If > 20% of results are clearly off-topic (wrong organism, wrong protein, unrelated field):
     -> COLLISION DETECTED

3. If collision detected, add disambiguation terms to ALL subsequent searches:
   - Add protein name: "BRAF AND (serine-threonine kinase OR melanoma OR V600E)"
   - Add organism: "GENE_SYMBOL AND (human OR Homo sapiens)"
   - Exclude noise: "GENE_SYMBOL NOT Drosophila NOT yeast NOT veterinary"
   - Use full gene name instead of symbol where possible

4. Record collision status in the report header:
   - "Literature collision: NONE" or
   - "Literature collision: DETECTED — filtering applied: [terms]"
```

---

## Completeness Audit Checklist

**MANDATORY at the end of every target research report.** Every section must meet minimum data requirements.

| Section | Minimum Requirement | Pass/Fail Criteria |
|---------|-------------------|-------------------|
| **Identifier Resolution** | All 6 IDs resolved (Gene, Ensembl, UniProt, ChEMBL, NCBI, DrugBank ref) | FAIL if any ID missing without documented reason |
| **OpenTargets Foundation** | Target details retrieved, top 5 disease associations listed | FAIL if no disease associations queried |
| **Protein Identity** | Protein family, domains, molecular function, subcellular location documented | FAIL if function unknown and no literature search attempted |
| **Structural Data** | PDB availability assessed, structural readiness classified (High/Medium/Low) | FAIL if structural readiness not classified |
| **Protein Interactions** | Minimum 20 interactors listed OR documented reason for fewer | FAIL if < 10 interactors without explanation |
| **Pathway Context** | At least 2 pathways identified, upstream/downstream nodes named | FAIL if no pathway information and no fallback attempted |
| **Expression Profile** | Tissue distribution documented, disease expression changes noted | FAIL if expression not queried |
| **Variant Landscape** | GWAS, somatic, Mendelian variants each assessed | FAIL if any variant category not queried |
| **Drug Landscape** | All approved drugs listed, clinical trial count provided, bioactivity range stated | FAIL if DrugBank and ChEMBL not both queried |
| **Literature Deep Dive** | Minimum 10 key references with PMIDs, reviews + recent papers included | FAIL if < 10 references cited |
| **Evidence Summary** | Every major finding has T-grade assigned | FAIL if any finding lacks evidence grade |

**Audit output format:**

```
COMPLETENESS AUDIT
==================
Identifier Resolution:    [PASS/FAIL] — [note]
OpenTargets Foundation:   [PASS/FAIL] — [note]
Protein Identity:         [PASS/FAIL] — [note]
Structural Data:          [PASS/FAIL] — [note]
Protein Interactions:     [PASS/FAIL] — [note]
Pathway Context:          [PASS/FAIL] — [note]
Expression Profile:       [PASS/FAIL] — [note]
Variant Landscape:        [PASS/FAIL] — [note]
Drug Landscape:           [PASS/FAIL] — [note]
Literature Deep Dive:     [PASS/FAIL] — [note]
Evidence Summary:         [PASS/FAIL] — [note]

Overall: [X/11 PASS] — [COMPLETE / INCOMPLETE — requires PATH X, Y remediation]
```

---

## Fallback Chains

When primary tools fail or return no data, use these documented alternatives.

| Primary Source | If it fails... | Fallback 1 | Fallback 2 |
|---------------|---------------|------------|------------|
| Open Targets `get_target_details` | Target not in Open Targets | PubMed review search + NLM `ncbi-genes` | ChEMBL `target_search` |
| ChEMBL `get_bioactivity` | No bioactivity data | PubChem `get_bioassay_results` | PubMed search for "GENE inhibitor IC50" |
| DrugBank `search_by_target` | No drugs found | ChEMBL `drug_search` + FDA `lookup_drug` | PubMed "GENE therapeutic drug" |
| DrugBank `get_pathways` | No pathway data | Open Targets Reactome pathways | PubMed "GENE pathway signaling" |
| PubChem `get_3d_conformer` | No 3D data | PubMed "GENE crystal structure PDB" | PubChem `get_compound_properties` (2D only) |
| NLM `ncbi-genes` | Gene not found | Open Targets `search_targets` | PubMed "GENE symbol human" |
| ClinicalTrials.gov `search` | No trials | FDA `lookup_drug` for approved drugs | PubMed "GENE clinical trial" |
| FDA `lookup_drug` | No FDA data | DrugBank `get_drug_details` | ClinicalTrials.gov `search` |

**Fallback rules:**
- Always attempt at least one fallback before marking a section as "No data available"
- Document which fallback was used in the report
- If all fallbacks fail, record: "No data from [Primary], [Fallback 1], [Fallback 2]. Section scored as empty."

---

## GPCR-Specific Branching

When the target is identified as a G protein-coupled receptor (GPCR), activate this specialized workflow in addition to the standard 9 paths.

### GPCR Detection

```
Trigger: Open Targets target details contains "GPCR" or "G protein-coupled receptor" in protein class
OR: ChEMBL target classification contains "7TM" or "GPCR"
```

### GPCR-Specific Research Extensions

```
1. Receptor pharmacology:
   mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL GPCR agonist antagonist allosteric biased signaling", num_results: 15)
   -> Agonist vs antagonist biology, biased agonism, allosteric modulation

2. G-protein coupling:
   mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL G-protein coupling Gs Gi Gq arrestin", num_results: 10)
   -> Which G-proteins? Arrestin recruitment? Biased signaling potential?

3. Receptor subtypes and selectivity:
   mcp__opentargets__opentargets_info(method: "search_targets", query: "RECEPTOR_FAMILY", size: 20)
   -> All family members — selectivity challenge assessment

4. Structural pharmacology:
   mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL cryo-EM structure active inactive conformations", num_results: 10)
   -> GPCR structures in active/inactive states

5. Allosteric sites:
   mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL allosteric modulator PAM NAM", num_results: 10)
   -> Known allosteric modulators (PAM = positive, NAM = negative)

6. Desensitization and tolerance:
   mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL desensitization internalization tolerance tachyphylaxis", num_results: 10)
   -> Receptor downregulation risk (critical for chronic dosing)
```

**GPCR-specific output additions:**
- G-protein coupling profile (Gs/Gi/Gq/G12-13/arrestin)
- Biased signaling opportunities
- Allosteric vs orthosteric druggability
- Desensitization risk for chronic treatment
- Receptor subtype selectivity matrix

---

## Complete Target Research Workflow Example

### Researching EGFR (Epidermal Growth Factor Receptor)

```
IDENTIFIER RESOLUTION:
mcp__opentargets__opentargets_info(method: "search_targets", query: "EGFR", size: 5)
-> Ensembl: ENSG00000146648
mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000146648")
-> UniProt: P00533, RTK family, membrane-bound
mcp__chembl__chembl_info(method: "target_search", query: "EGFR", limit: 5)
-> ChEMBL: CHEMBL203
mcp__nlm__nlm_ct_codes(method: "ncbi-genes", terms: "EGFR", maxList: 3)
-> NCBI Gene: 1956, chr7p11.2

PATH 0 — OpenTargets Foundation:
mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000146648")
-> Tclin, small molecule + antibody tractable
-> Top diseases: NSCLC (0.97), glioblastoma (0.89), colorectal (0.85)

PATH 1 — Protein Identity:
-> Receptor tyrosine kinase, 4 domains (L1, CR1, L2, CR2), kinase domain
-> Ligands: EGF, TGF-alpha, amphiregulin, betacellulin
-> Subcellular: plasma membrane

PATH 2 — Structural Data:
mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "EGFR crystal structure kinase domain", num_results: 15)
-> 100+ PDB structures, active and inactive conformations
-> Structural readiness: HIGH

PATH 3 — Protein Interactions:
-> HER2/3/4 heterodimerization, GRB2, SOS1, SHC, PLCgamma
-> >50 known interactors from multiple studies

PATH 4 — Pathway Context:
-> RAS-MAPK, PI3K-AKT, PLCgamma-PKC, STAT3
-> Feedback: MET amplification bypass, HER3 upregulation

PATH 5 — Expression:
-> High in epithelial tissues (lung, skin, colon, kidney)
-> Overexpressed/amplified in NSCLC, glioblastoma, CRC, HNSCC

PATH 6 — Variants:
-> Activating: L858R, exon 19 deletions (NSCLC driver)
-> Resistance: T790M (1st-gen), C797S (3rd-gen)
-> GWAS: lung cancer susceptibility locus

PATH 7 — Drug Landscape:
mcp__drugbank__drugbank_info(method: "search_by_target", target: "EGFR", limit: 30)
-> Approved: erlotinib, gefitinib, afatinib, osimertinib, cetuximab, panitumumab
-> >500 compounds in ChEMBL with IC50 < 1 uM
mcp__ctgov__ctgov_info(method: "stats", intervention: "EGFR inhibitor")
-> >2000 clinical trials

PATH 8 — Literature:
mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "EGFR review", num_results: 20)
-> >100,000 publications total, >500 reviews
-> Literature collision: NONE

EVIDENCE SUMMARY:
- Target biology: T1 (clinical proof — multiple approved drugs)
- Disease association: T1 (NSCLC driver mutations)
- Druggability: T1 (Tclin, multiple modalities)
- Safety: Known class effects — rash, diarrhea, ILD (rare)

COMPLETENESS AUDIT: 11/11 PASS — COMPLETE
```

---

## Multi-Agent Workflow Examples

**"Build a complete target dossier for CDK4/6"**
1. Target Research -> 9-path intelligence gathering: protein biology, structure, interactions, pathways, expression, variants, drugs, literature
2. Drug Target Analyst -> Deep bioactivity SAR, selectivity vs CDK family, druggability assessment
3. Drug Target Validator -> Quantitative validation score with GO/NO-GO for specific indications
4. Network Pharmacologist -> CDK4/6 in cell cycle network context, combination rationale (CDK4/6i + endocrine therapy)

**"Comprehensive profiling of a novel kinase target"**
1. Target Research -> Full 9-path profile (especially critical for less-characterized targets where completeness matters)
2. Drug Target Analyst -> Kinase selectivity assessment across kinome, available chemical matter quality
3. Binder Discovery Specialist -> Design strategy for lead identification based on structural data from PATH 2
4. Disease Research -> Disease biology context for the target's therapeutic area

**"Profile a GPCR target for CNS indication"**
1. Target Research -> 9 paths + GPCR-specific branching (G-protein coupling, biased signaling, desensitization)
2. Drug Target Analyst -> SAR of known ligands, CNS-penetrant compound identification
3. Drug Target Validator -> Validation score with emphasis on safety (brain expression = critical tissue)
4. Network Pharmacologist -> Neurotransmitter pathway context, receptor cross-talk

**"Evaluate a Tdark target from a GWAS hit"**
1. Target Research -> 9-path intelligence (expect sparse data — fallback chains critical, completeness audit will flag gaps)
2. Disease Research -> Disease mechanism and context to interpret the GWAS signal
3. Drug Target Validator -> Honest NO-GO scoring expected for Tdark, but documents exactly what validation experiments are needed
4. Network Pharmacologist -> Pathway placement to find druggable neighbors even if target itself is intractable

**"Compare 5 targets for portfolio prioritization"**
1. Target Research -> Run 9-path profile for each of 5 targets (batch mode — create separate report per target)
2. Drug Target Validator -> Score all 5, produce comparison table
3. Drug Target Analyst -> Comparative druggability and chemical matter assessment
4. Binder Discovery Specialist -> Rank by lead discovery feasibility based on structural and chemical intelligence
