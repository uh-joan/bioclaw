---
name: network-pharmacologist
description: Systems pharmacology specialist for compound-target-disease network analysis. Constructs and analyzes C-T-D networks to identify drug repurposing opportunities, understand polypharmacology effects, and predict drug mechanisms. Produces a Network Pharmacology Score (0-100). Use when user mentions network pharmacology, drug repurposing, polypharmacology, drug repositioning, compound-target-disease network, C-T-D network, network proximity, multi-target drugs, off-target effects, selectivity entropy, systems pharmacology, network medicine, shortest path analysis, module overlap, degree centrality, betweenness centrality, or proximity Z-score.
---

# Network Pharmacologist

Systems pharmacology specialist that constructs and analyzes compound-target-disease (C-T-D) networks to identify drug repurposing opportunities, understand polypharmacology effects, and predict drug mechanisms of action. Uses Open Targets for target-disease associations, ChEMBL for bioactivity and mechanism data, DrugBank for drug-target pharmacology, PubMed for literature evidence, PubChem for compound properties and structural similarity, FDA for regulatory and labeling data, and ClinicalTrials.gov for clinical evidence.

## Report-First Workflow

1. **Create report file immediately**: `[compound]_network-pharmacologist_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Individual drug-target deep-dive with SAR analysis → use `drug-target-analyst`
- Drug repurposing candidate ranking and therapeutic area mapping → use `drug-repurposing-analyst`
- Drug safety signals and adverse event analysis → use `pharmacovigilance-specialist`
- Chemical toxicity and safety assessment → use `chemical-safety-toxicology`
- Clinical trial evidence synthesis → use `clinical-trial-analyst`
- Medicinal chemistry lead optimization → use `medicinal-chemistry`

## Cross-Reference: Other Skills

- **Individual drug-target deep-dive** → use drug-target-analyst skill
- **Drug repurposing candidate ranking** → use drug-repurposing-analyst skill
- **Drug safety signals and adverse events** → use pharmacovigilance-specialist skill
- **Chemical toxicity and safety assessment** → use chemical-safety-toxicology skill
- **Clinical trial evidence for candidates** → use clinical-trial-analyst skill

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

### `mcp__chembl__chembl_info` (Bioactivity & Mechanism)

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

### `mcp__pubmed__pubmed_articles` (Literature Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__pubchem__pubchem_info` (Compound Properties & Similarity)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_compounds` | Search compounds by name or identifier | `query`, `limit` |
| `get_compound_info` | Full compound profile (structure, properties, identifiers) | `cid` |
| `search_similar_compounds` | Structural similarity search by CID or SMILES | `cid` or `smiles`, `threshold`, `limit` |
| `get_safety_data` | GHS hazard, toxicity, and safety data | `cid` |
| `get_patent_ids` | Patent IDs associated with a compound | `cid`, `limit` |
| `get_bioassay_summary` | Bioassay activity summary for a compound | `cid`, `limit` |
| `get_compound_targets` | Known biological targets for a compound | `cid`, `limit` |
| `get_compound_synonyms` | All synonyms and alternative names | `cid` |
| `get_compound_classification` | Pharmacological and chemical classification | `cid` |
| `get_compound_interactions` | Known drug interactions | `cid`, `limit` |
| `get_compound_pathways` | Biological pathway associations | `cid`, `limit` |
| `get_compound_diseases` | Disease associations for a compound | `cid`, `limit` |

### `mcp__uniprot__uniprot_data` (Protein Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_protein_info` | Full protein profile | `accession`, `format` |
| `search_by_gene` | Find proteins by gene name | `gene`, `organism`, `size` |
| `get_protein_interactions` | Known protein interactions | `accession` |
| `get_protein_pathways` | Pathway involvement | `accession` |
| `search_by_function` | Search by GO term or function | `goTerm`, `function`, `organism`, `size` |
| `get_protein_features` | Protein features (domains, sites, PTMs) | `accession` |

### `mcp__stringdb__stringdb_data` (Protein-Protein Interactions)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_interaction_network` | Build interaction network from protein list | `protein_ids`, `species`, `required_score`, `network_type`, `add_nodes` |
| `get_functional_enrichment` | GO/KEGG/Reactome enrichment for protein set | `protein_ids`, `species`, `background_string_identifiers` |
| `get_protein_interactions` | Get interaction partners for a protein | `protein_id`, `species`, `limit`, `required_score` |
| `search_proteins` | Search proteins by name | `query`, `species`, `limit` |

### `mcp__kegg__kegg_data` (Pathway & Compound Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_pathways` | Search KEGG pathways by keyword | `query` |
| `get_pathway_info` | Full pathway details (description, classes, modules) | `pathway_id` |
| `get_pathway_genes` | All genes in a pathway | `pathway_id` |
| `get_pathway_compounds` | All compounds in a pathway | `pathway_id` |
| `search_compounds` | Search KEGG compounds by keyword | `query` |
| `get_compound_info` | Compound details (formula, reactions, pathways) | `compound_id` |
| `get_compound_reactions` | Reactions involving a compound | `compound_id` |
| `search_drugs` | Search KEGG drug entries | `query` |
| `get_drug_info` | Drug details (targets, interactions, pathways) | `drug_id` |
| `convert_identifiers` | Convert between KEGG and external IDs | `identifiers`, `source_db`, `target_db` |
| `find_related_entries` | Find entries related to a given KEGG entry | `entry_id` |

### `mcp__reactome__reactome_data` (Pathway Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `find_pathways_by_gene` | Pathways containing a gene | `gene_id`, `species` |
| `get_pathway_details` | Full pathway info | `pathway_id` |
| `get_pathway_participants` | Molecules in a pathway | `pathway_id` |
| `get_pathway_reactions` | Reactions in a pathway | `pathway_id` |
| `get_protein_interactions` | Protein interactions from Reactome | `protein_id` |

### `mcp__hmdb__hmdb_data` (Metabolite-Pathway Network Integration)

Use HMDB to integrate metabolite nodes into compound-target-disease networks, enriching network pharmacology analysis with metabolite-pathway edges and metabolite-disease associations. Note: HMDB uses Cloudflare protection so some requests may be blocked intermittently.

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_metabolite` | Comprehensive metabolite data (name, formula, pathways, diseases) — add metabolite nodes to C-T-D networks | `hmdb_id` (required) |
| `search_metabolites` | Search metabolites by name/keyword for network node discovery | `query` (required), `limit` (optional, default 25) |
| `get_metabolite_pathways` | Biological pathways — construct metabolite-pathway edges in the network | `hmdb_id` (required) |
| `get_metabolite_diseases` | Disease associations — add metabolite-disease edges with OMIM cross-references | `hmdb_id` (required) |
| `get_metabolite_concentrations` | Concentration data across biofluids — weight metabolite network edges by biological relevance | `hmdb_id` (required) |
| `search_by_mass` | Find metabolites by molecular weight — integrate mass spec hits as network nodes | `mass` (required), `tolerance` (optional, default 0.05), `limit` (optional, default 25) |

### `mcp__geneontology__go_data` (Gene Ontology)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_go_terms` | Search GO terms by keyword | `query`, `size`, `ontology` (molecular_function/biological_process/cellular_component), `include_obsolete` |
| `get_go_term` | Get full GO term details (definition, synonyms, xrefs) | `id` (GO:XXXXXXX) |
| `validate_go_id` | Check if GO ID is valid | `id` |
| `get_ontology_stats` | GO ontology statistics | -- |

### `mcp__fda__fda_info` (Regulatory & Labeling Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search FDA drug labels and approvals | `query`, `limit` |
| `get_drug_label` | Full prescribing information / label | `application_number` or `query` |
| `search_adverse_events` | FAERS adverse event reports | `query`, `limit` |
| `get_recall_info` | Drug recall information | `query`, `limit` |
| `get_enforcement_actions` | FDA enforcement actions | `query`, `limit` |
| `search_orange_book` | Orange Book patent and exclusivity data | `query`, `limit` |
| `get_ndc_info` | National Drug Code directory lookup | `query`, `limit` |
| `get_approval_history` | Drug approval timeline and supplements | `query`, `limit` |

### `mcp__ctgov__ctgov_info` (Clinical Trial Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_trials` | Search clinical trials by condition/drug/target | `query`, `status`, `limit` |
| `get_trial_details` | Full protocol and results for a trial | `nct_id` |
| `search_by_intervention` | Trials testing a specific drug or intervention | `intervention`, `status`, `limit` |
| `search_by_condition` | Trials for a specific condition | `condition`, `phase`, `limit` |

### BindingDB — Binding Affinity Data

| Tool | Method | Use |
|------|--------|-----|
| `mcp__bindingdb__bindingdb_data` | `get_ligands_by_target` | Binding data for network nodes — quantitative edge weights |
| | `search_by_name` | Multi-target binding profiles for network pharmacology |
| | `get_ki_by_target` | Ki selectivity across related targets in the network |

**BindingDB workflow:** Use BindingDB binding affinities as quantitative edge weights in drug-target networks.

```
mcp__bindingdb__bindingdb_data(method: "get_ligands_by_target", target: "TARGET_NAME")
mcp__bindingdb__bindingdb_data(method: "search_by_name", name: "DRUG_NAME")
mcp__bindingdb__bindingdb_data(method: "get_ki_by_target", target: "TARGET_NAME")
```

### DepMap — Cancer Dependency Map

| Tool | Method | Use |
|------|--------|-----|
| `mcp__depmap__depmap_data` | `get_multi_gene_profile` | Co-dependency profiles for network nodes (up to 20 genes) — functional validation of network connections |
| | `get_biomarker_analysis` | Synthetic lethality detection — network-based combination therapy rationale |
| | `get_gene_dependency` | Node essentiality in the network |
| | `get_gene_dependency_summary` | Prioritize network nodes by essentiality |
| | `get_drug_sensitivity` | Drug response for network-targeted therapies |

---

## 8-Phase Network Pharmacology Pipeline

### Phase 1: Entity Disambiguation

Resolve compound, target, and disease identifiers across databases.

```
1. mcp__pubchem__pubchem_info(method: "search_compounds", query: "compound_name")
   → Get PubChem CID, canonical SMILES, InChI

2. mcp__chembl__chembl_info(method: "compound_search", query: "compound_name")
   → Get ChEMBL compound ID, cross-reference with PubChem

3. mcp__drugbank__drugbank_info(method: "search_by_name", query: "compound_name")
   → Get DrugBank ID, verify identity

4. mcp__drugbank__drugbank_info(method: "get_external_identifiers", drugbank_id: "DBxxxxx")
   → Cross-database mapping (PubChem, ChEMBL, KEGG, UniProt)

5. mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL", size: 10)
   → Get Ensembl gene ID for target nodes

6. mcp__opentargets__opentargets_info(method: "search_diseases", query: "disease_name", size: 10)
   → Get EFO disease ID for disease nodes
```

### Phase 2: Network Node Identification

Build the node sets: drug targets, disease genes, and shared proteins.

```
Drug → Target edges:
1. mcp__pubchem__pubchem_info(method: "get_compound_targets", cid: "CID_NUMBER", limit: 50)
   → All known biological targets for the compound

2. mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "CHEMBLxxxxx", limit: 100)
   → Bioactivity-confirmed targets (IC50, Ki, EC50)

3. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   → Pharmacological targets, enzymes, carriers, transporters

4. mcp__chembl__chembl_info(method: "get_mechanism", chembl_id: "CHEMBLxxxxx")
   → Mechanism of action and target for approved drugs

5. mcp__uniprot__uniprot_data(method: "get_protein_interactions", accession: "UNIPROT_ACC")
   → UniProt-curated interaction partners to expand target node set

6. mcp__uniprot__uniprot_data(method: "get_protein_pathways", accession: "UNIPROT_ACC")
   → Pathway memberships for network edge construction

Disease → Gene edges:
7. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.3, size: 100)
   → All validated disease-associated genes, ranked by evidence

6. mcp__opentargets__opentargets_info(method: "get_disease_details", id: "EFO_xxxxxxx")
   → Disease ontology, phenotypes, related diseases
```

### Phase 3: Edge Construction (Bidirectional Network)

Establish and weight edges between nodes.

```
Drug → Target edges (weighted by bioactivity):
1. For each target from Phase 2:
   mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "COMPOUND_ID", target_id: "TARGET_ID", limit: 50)
   → Activity values (IC50, Ki, EC50) determine edge weight

2. Assign edge evidence tier:
   T1: Clinical/regulatory evidence (approved drug-target pair)
   T2: Functional evidence (IC50 < 1 μM in validated assay)
   T3: GWAS/genetic association
   T4: Computational prediction or text mining

Disease → Gene edges (weighted by association score):
3. For each gene from Phase 2:
   mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   → Association score with evidence breakdown

Protein-Protein interaction edges:
4. mcp__stringdb__stringdb_data(method: "get_interaction_network", protein_ids: ["TARGET_A", "TARGET_B", "TARGET_C"], species: 9606, required_score: 400, network_type: "functional", add_nodes: 5)
   → Build PPI network connecting drug targets and disease genes with STRING confidence scores

5. mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   → Shared pathway membership implies PPI connectivity

6. mcp__pubchem__pubchem_info(method: "get_compound_pathways", cid: "CID_NUMBER", limit: 50)
   → Pathway-based connections between targets

KEGG pathway edges:
6b. mcp__kegg__kegg_data(method: "search_pathways", query: "disease_keyword signaling")
    → Find KEGG pathways relevant to the disease context
    mcp__kegg__kegg_data(method: "get_pathway_genes", pathway_id: "hsa04010")
    → Get all genes in the pathway — shared membership creates target-target edges

Reactome pathway edges:
7. mcp__reactome__reactome_data(method: "find_pathways_by_gene", gene_id: "TARGET_GENE", species: "Homo sapiens")
   → Direct Reactome pathway membership for network targets

8. mcp__reactome__reactome_data(method: "get_protein_interactions", protein_id: "UNIPROT_ACC")
   → Reactome-curated protein interactions to supplement STRING PPI edges
```

### Phase 4: Network Analysis

Compute network topology metrics.

```
Network metrics to compute:

1. Degree centrality
   → Number of edges per node; high-degree targets are network hubs

2. Betweenness centrality
   → Fraction of shortest paths passing through a node; identifies bottleneck targets

3. Shortest path distance
   → Minimum path length between drug target set and disease gene set

4. Network proximity Z-score
   → Z = (d - μ_random) / σ_random
   → d = average shortest distance between drug targets and disease genes
   → μ_random, σ_random from randomized degree-preserved networks
   → Z < -2 indicates significant proximity (p < 0.05)

5. Module overlap
   → Number of shared network modules between drug targets and disease genes
   → Modules identified by community detection on PPI topology

6. Jaccard index
   → |Drug_targets ∩ Disease_genes| / |Drug_targets ∪ Disease_genes|
   → Direct overlap between target sets
```

### Phase 5: Drug Repurposing Prediction

Score and rank repurposing candidates.

```
1. For each candidate drug:
   mcp__pubchem__pubchem_info(method: "get_compound_targets", cid: "CID_NUMBER", limit: 50)
   → Build target profile

2. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.5, size: 50)
   → Build disease gene set

3. mcp__stringdb__stringdb_data(method: "get_functional_enrichment", protein_ids: ["SHARED_TARGET_1", "SHARED_TARGET_2"], species: 9606)
   → Functional enrichment of shared drug-disease targets to validate biological coherence

4. Compute Network Pharmacology Score (see scoring framework below)

5. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "drug_name disease_name repurposing OR repositioning", num_results: 20)
   → Literature support for repurposing hypothesis

5. mcp__ctgov__ctgov_info(method: "search_trials", query: "drug_name disease_name", limit: 10)
   → Existing clinical evidence for the new indication

6. mcp__drugbank__drugbank_info(method: "get_similar_drugs", drugbank_id: "DBxxxxx", limit: 20)
   → Identify structurally/pharmacologically similar drugs with activity in the disease
```

### Phase 6: Polypharmacology Profiling

Characterize multi-target activity and off-target effects.

```
1. mcp__pubchem__pubchem_info(method: "get_compound_targets", cid: "CID_NUMBER", limit: 100)
   → Full target spectrum for the compound

2. mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "CHEMBLxxxxx", limit: 200)
   → All bioactivity data to assess selectivity profile

3. For each off-target:
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Functional consequences of off-target modulation

3b. mcp__geneontology__go_data(method: "search_go_terms", query: "protein binding", ontology: "molecular_function", size: 10)
    → Resolve GO molecular function annotations for network target nodes

3c. mcp__geneontology__go_data(method: "get_go_term", id: "GO:0005515")
    → Get full GO term details (definition, synonyms) for functional annotation of network nodes

4. mcp__uniprot__uniprot_data(method: "search_by_function", function: "kinase activity", organism: "human", size: 50)
   → Identify functionally related proteins that may be off-targets

4. Compute selectivity entropy:
   S = -Σ p_i * log2(p_i)
   where p_i = activity_i / Σ_all_activities
   → Low entropy = selective compound
   → High entropy = promiscuous compound

5. mcp__drugbank__drugbank_info(method: "search_by_target", target: "off_target_name", limit: 20)
   → Known drugs hitting the same off-target (class effect prediction)

6. mcp__pubchem__pubchem_info(method: "get_bioassay_summary", cid: "CID_NUMBER", limit: 50)
   → Broad screening data to identify unexpected activities
```

### Phase 7: Safety and Toxicity Assessment

Evaluate safety implications of network pharmacology findings.

```
1. mcp__fda__fda_info(method: "search_adverse_events", query: "drug_name", limit: 50)
   → Known adverse events (correlate with off-target activity)

2. mcp__fda__fda_info(method: "get_drug_label", query: "drug_name")
   → Black box warnings, contraindications, mechanism-based toxicity

3. mcp__pubchem__pubchem_info(method: "get_safety_data", cid: "CID_NUMBER")
   → GHS hazard classification, toxicity data

4. mcp__chembl__chembl_info(method: "get_admet", chembl_id: "CHEMBLxxxxx")
   → ADMET properties, drug-likeness, predicted toxicity flags

5. mcp__drugbank__drugbank_info(method: "get_drug_interactions", drugbank_id: "DBxxxxx")
   → Drug-drug interactions mediated by shared targets or pathways

6. mcp__fda__fda_info(method: "get_recall_info", query: "drug_name", limit: 10)
   → Historical safety actions
```

### Network Dependency Profiling via DepMap

Validate network pharmacology findings with functional dependency data from the Cancer Dependency Map.

```
1. Take key network nodes (pathway members):
   → Collect high-centrality targets and disease-associated genes from Phases 2-4

2. Query multi-gene dependency profiles:
   mcp__depmap__depmap_data(method: "get_multi_gene_profile", genes: ["BRAF", "KRAS", "MAP2K1", "EGFR"])
   → Co-dependency profiles across cancer cell lines for network nodes (up to 20 genes)
   → Identifies which nodes are functionally linked by correlated essentiality

3. Identify co-dependent gene pairs (synthetic lethality candidates):
   → From multi-gene profile, extract gene pairs with strong negative co-dependency
   → Negative correlation in dependency scores indicates synthetic lethal interaction
   → These pairs represent network edges validated by functional data

4. Test specific synthetic lethality hypotheses with biomarker analysis:
   mcp__depmap__depmap_data(method: "get_biomarker_analysis", gene: "BRAF")
   → Identifies genomic features (mutations, expression, copy number) that predict dependency
   → Confirms network-predicted vulnerabilities with functional evidence

   mcp__depmap__depmap_data(method: "get_gene_dependency", gene: "KRAS")
   → Detailed dependency profile for a specific network node across cell lines

   mcp__depmap__depmap_data(method: "get_gene_dependency_summary", gene: "MAP2K1")
   → Quick essentiality assessment to prioritize network nodes for targeting

5. Map drug sensitivity to network topology:
   mcp__depmap__depmap_data(method: "get_drug_sensitivity", drug: "vemurafenib")
   → Drug response data across cell lines — correlate with network target expression
   → Validates whether network-predicted drug-target relationships translate to cell killing
   → Compare sensitivity patterns with dependency profiles to confirm on-target mechanism
```

### Phase 8: Report Generation

Synthesize findings into a structured network pharmacology report.

```
Report structure:
1. Executive Summary
   → Network Pharmacology Score, scoring tier, key finding

2. Network Overview
   → Node counts (drugs, targets, diseases), edge counts, network density
   → Visualization description (bipartite/tripartite layout)

3. Network Topology
   → Hub targets (high degree centrality)
   → Bottleneck targets (high betweenness centrality)
   → Network proximity Z-score and significance

4. Drug Repurposing Candidates
   → Ranked list with scores, evidence tier, clinical status

5. Polypharmacology Profile
   → Target spectrum, selectivity entropy, off-target risk assessment

6. Safety Assessment
   → Mechanism-based toxicity risks, DDI potential, class effects

7. Evidence Summary Table
   → All evidence graded T1-T4 with source citations

8. Recommendations
   → Prioritized candidates for experimental validation
   → Suggested assays and clinical strategies
```

---

## Network Pharmacology Score (0-100)

### Scoring Components

| Component | Weight | What it measures |
|-----------|--------|------------------|
| **Network Proximity** | 35 pts | Topological closeness of drug targets to disease genes in the PPI network |
| **Clinical Evidence** | 25 pts | Existing clinical data supporting the drug-disease connection |
| **Target-Disease Association** | 20 pts | Strength of Open Targets association scores for shared targets |
| **Safety Profile** | 10 pts | Absence of mechanism-based toxicity and serious adverse events |
| **Mechanism Plausibility** | 10 pts | Biological rationale for therapeutic effect via network targets |

### Network Proximity Scoring (35 pts)

```
Proximity Z-score interpretation:
  Z < -3.0  → 35 pts (highly significant proximity)
  Z < -2.5  → 30 pts
  Z < -2.0  → 25 pts (significant, p < 0.05)
  Z < -1.5  → 18 pts
  Z < -1.0  → 10 pts
  Z >= -1.0 → 0-5 pts (not significant)

Additional proximity metrics:
  Direct target overlap (Jaccard > 0.1)  → +5 pts bonus
  Module overlap ≥ 2 shared modules      → +3 pts bonus
  (Bonuses capped at 35 pts total)
```

### Clinical Evidence Scoring (25 pts)

```
  Approved for the indication          → 25 pts
  Phase III trial with positive results → 20 pts
  Phase II trial with positive results  → 15 pts
  Phase I trial ongoing                 → 10 pts
  Case reports / off-label use          → 7 pts
  In vivo animal model evidence         → 5 pts
  In vitro evidence only                → 3 pts
  No clinical evidence                  → 0 pts
```

### Target-Disease Association Scoring (20 pts)

```
  Average Open Targets score for shared targets:
  > 0.8  → 20 pts (strong genetic + clinical evidence)
  > 0.6  → 15 pts
  > 0.4  → 10 pts
  > 0.2  → 5 pts
  ≤ 0.2  → 0-2 pts

  Bonus for multiple high-scoring shared targets:
  ≥ 5 shared targets with score > 0.5  → +3 pts
  ≥ 3 shared targets with score > 0.5  → +2 pts
  (Capped at 20 pts total)
```

### Safety Profile Scoring (10 pts)

```
  No black box warnings, clean safety record  → 10 pts
  Minor warnings, manageable adverse events    → 7 pts
  Significant warnings but acceptable risk     → 5 pts
  Black box warning related to target class    → 3 pts
  Recall history or serious safety signals     → 0 pts
```

### Mechanism Plausibility Scoring (10 pts)

```
  Known mechanism directly relevant to disease  → 10 pts
  Pathway-level connection with published data   → 7 pts
  Indirect connection via shared modules         → 5 pts
  Computational prediction only                  → 2 pts
  No plausible mechanism identified              → 0 pts
```

### Scoring Tiers

| Tier | Score Range | Interpretation | Recommended Action |
|------|------------|----------------|-------------------|
| **Tier 1** | 80-100 | High repurposing potential | Prioritize for clinical investigation; strong network + clinical evidence |
| **Tier 2** | 60-79 | Moderate repurposing potential | Warrants preclinical validation; good network proximity with some clinical support |
| **Tier 3** | 40-59 | Low repurposing potential | Requires substantial additional evidence; network signal present but weak |
| **Tier 4** | 0-39 | Minimal repurposing potential | Insufficient network evidence; not recommended for further pursuit |

---

## Evidence Grading System

| Grade | Evidence Type | Description | Examples |
|-------|-------------|-------------|----------|
| **T1** | Clinical/Regulatory | Approved drug-target-disease relationship or Phase III data | FDA-approved indication, positive Phase III results |
| **T2** | Functional | Experimentally validated with IC50 < 1 μM or equivalent | In vitro binding assay, cell-based functional assay, CRISPR validation |
| **T3** | Association | GWAS, genetic association, or systematic analysis | GWAS hit, Mendelian disease gene, somatic mutation in disease |
| **T4** | Prediction | Computational prediction or text mining | Network inference, machine learning prediction, literature co-mention |

---

## Polypharmacology Profiling Framework

### Target Spectrum Classification

```
Classification by target count:
  1 target (IC50 < 1 μM)         → Selective compound
  2-5 targets (IC50 < 1 μM)      → Multi-target compound
  6-15 targets (IC50 < 1 μM)     → Broadly active compound
  > 15 targets (IC50 < 1 μM)     → Promiscuous compound

Selectivity entropy calculation:
  S = -Σ p_i * log2(p_i)
  where p_i = (1/IC50_i) / Σ(1/IC50_all)

  S < 1.0   → Highly selective
  S = 1-2   → Moderately selective
  S = 2-3   → Low selectivity
  S > 3.0   → Promiscuous
```

### Off-Target Risk Categories

```
Risk Level 1 (Critical):
  → Anti-targets: hERG, CYP3A4, PXR (safety liabilities)
  → Essential gene targets (cell viability)

Risk Level 2 (Significant):
  → Same-family off-targets (kinase selectivity, GPCR cross-reactivity)
  → Targets with known class-effect toxicities

Risk Level 3 (Moderate):
  → Targets in unrelated pathways
  → Weak activity (IC50 > 10 μM)

Risk Level 4 (Low):
  → Targets with known benign modulation
  → Activity at concentrations far above therapeutic dose
```

---

## Network Construction Patterns

### Bidirectional C-T-D Network

```
Layer 1: Compound → Target edges
  Source: ChEMBL bioactivity, DrugBank targets, PubChem targets
  Weight: -log10(IC50) or binding affinity
  Evidence: T1-T4 grading

Layer 2: Target → Disease edges
  Source: Open Targets associations, GWAS catalog
  Weight: Open Targets association score (0-1)
  Evidence: Genetic, somatic, literature, known drugs, animal models

Layer 3: Target → Target edges (PPI)
  Source: DrugBank pathways, PubChem pathways, literature
  Weight: Co-pathway membership, co-expression, physical interaction

Network metrics:
  Nodes: |Compounds| + |Targets| + |Diseases|
  Edges: |C-T| + |T-D| + |T-T|
  Density: |Edges| / (|Nodes| * (|Nodes| - 1) / 2)
```

### Shortest Path Analysis

```
For drug repurposing assessment:
1. Define drug target set: T_drug = {t1, t2, ..., tn}
2. Define disease gene set: G_disease = {g1, g2, ..., gm}
3. Compute shortest path d(ti, gj) for all pairs
4. Network proximity: d = (1/|T|) * Σ min_j d(ti, gj)
5. Compare to random expectation:
   - Generate 1000 random target sets (degree-preserved)
   - Compute μ_random and σ_random
   - Z = (d - μ_random) / σ_random
6. Significant if Z < -2 (p < 0.05)
```

---

## Multi-Agent Workflow Examples

**"Find repurposing opportunities for metformin in cancer"**
1. Network Pharmacologist → Build C-T-D network for metformin, identify cancer-related targets, compute network proximity to cancer disease modules, score candidates
2. Drug Repurposing Analyst → Deep-dive on top repurposing candidates, therapeutic area mapping, competitive landscape
3. Clinical Trial Analyst → Existing trials of metformin in cancer indications, outcome data
4. Pharmacovigilance Specialist → Safety signals relevant to oncology use (lactic acidosis, GI effects at higher doses)

**"Analyze polypharmacology of imatinib across diseases"**
1. Network Pharmacologist → Full target spectrum (BCR-ABL, KIT, PDGFR, DDR1/2), selectivity entropy, build multi-disease network, identify unexpected disease connections
2. Drug Target Analyst → SAR analysis for each target, activity cliffs, binding mode differences
3. Chemical Safety Toxicology → Toxicity profile correlation with off-target activity, ADMET assessment
4. Clinical Trial Analyst → Trials across all indications (CML, GIST, dermatofibrosarcoma, systemic mastocytosis)

**"Predict mechanisms for an orphan drug in a rare disease"**
1. Network Pharmacologist → Construct C-T-D network from compound targets and disease genes, identify shared modules, compute proximity Z-score, assign Network Pharmacology Score
2. Drug Repurposing Analyst → Evidence synthesis, pathway-based mechanism hypothesis
3. Pharmacovigilance Specialist → Known safety profile, predict mechanism-based risks in new indication
4. Clinical Trial Analyst → Design considerations for rare disease trial based on network-predicted endpoints

**"Compare network profiles of JAK inhibitors for autoimmune diseases"**
1. Network Pharmacologist → Build parallel C-T-D networks for tofacitinib, baricitinib, upadacitinib; compare target spectra, selectivity entropy, network proximity to RA/UC/AD disease modules
2. Drug Target Analyst → JAK1/2/3 selectivity ratios, bioactivity comparison, structural basis for selectivity
3. Pharmacovigilance Specialist → Differential safety profiles (infections, thrombosis, malignancy) correlated with off-target activity
4. Clinical Trial Analyst → Head-to-head trials, indication-specific efficacy data

## Completeness Checklist

- [ ] All entities (compounds, targets, diseases) disambiguated with cross-database IDs
- [ ] Drug-target edges constructed with bioactivity-weighted evidence (IC50, Ki, EC50)
- [ ] Disease-gene edges established with Open Targets association scores
- [ ] PPI network built via STRING with confidence-scored edges
- [ ] Network topology metrics computed (degree centrality, betweenness, shortest path, proximity Z-score)
- [ ] Network Pharmacology Score calculated (0-100) with component breakdown
- [ ] Polypharmacology profile includes selectivity entropy and off-target risk categorization
- [ ] Safety assessment correlates off-target activity with known adverse events
- [ ] All evidence graded T1-T4 with source citations
- [ ] Report file verified: no `[Analyzing...]` placeholders remain
