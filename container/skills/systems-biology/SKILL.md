---
name: systems-biology
description: Systems biology and integrated pathway analysis specialist. Multi-database pathway mapping, gene set enrichment, over-representation analysis, pathway perturbation, network topology, cross-database validation, hierarchical pathway context. Use when user mentions systems biology, pathway analysis, gene set enrichment, GSEA, ORA, over-representation, pathway mapping, pathway perturbation, signaling pathway, metabolic pathway, biological network, gene ontology, reactome, KEGG pathway, pathway hierarchy, gene set, enrichment analysis, pathway crosstalk, or systems-level biology.
---

# Systems Biology

Integrated pathway analysis across multiple biological databases for gene set enrichment, pathway mapping, and systems-level biology understanding. Uses Open Targets for target-pathway associations, ChEMBL for compound-target-pathway links, DrugBank for metabolic/signaling pathways, PubMed for pathway literature, and PubChem for compound-pathway and target-pathway relationships.

## Report-First Workflow

1. **Create report file immediately**: `pathway_systems_biology_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## Cross-Reference: Other Skills

- **Individual target identification and druggability** -> use drug-target-analyst skill
- **Disease-specific target landscape** -> use disease-research skill
- **Target validation and functional evidence** -> use target-research skill
- **Network-level polypharmacology** -> use network-pharmacologist skill
- **Gene set enrichment from GWAS hits** -> use gene-enrichment skill

## Available MCP Tools

### `mcp__opentargets__opentargets_info` (Target-Pathway Associations)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `search_diseases` | Search diseases by name/synonym | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId` (Ensembl ID), `diseaseId` (EFO ID), `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes) | `id` (EFO ID) |

### `mcp__chembl__chembl_info` (Bioactivity & Compound-Target Links)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |
| `get_admet` | ADMET/drug-likeness properties | `chembl_id` |

### `mcp__drugbank__drugbank_info` (Drug-Pathway Pharmacology)

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

### `mcp__pubmed__pubmed_articles` (Pathway Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__pubchem__pubchem_info` (Compound-Pathway & Target-Pathway)

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

### `mcp__stringdb__stringdb_data` (Protein-Protein Interactions & Pathway Enrichment)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_functional_enrichment` | GO/KEGG/Reactome enrichment for protein set | `protein_ids`, `species`, `background_string_identifiers` |
| `get_interaction_network` | Build interaction network from protein list | `protein_ids`, `species`, `required_score`, `network_type`, `add_nodes` |
| `get_protein_annotations` | Get functional annotations | `protein_ids`, `species` |
| `search_proteins` | Search proteins by name | `query`, `species`, `limit` |

### `mcp__geneontology__go_data` (Gene Ontology)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_go_terms` | Search GO terms by keyword | `query`, `size`, `ontology` (molecular_function/biological_process/cellular_component), `include_obsolete` |
| `get_go_term` | Get full GO term details (definition, synonyms, xrefs) | `id` (GO:XXXXXXX) |
| `validate_go_id` | Check if GO ID is valid | `id` |
| `get_ontology_stats` | GO ontology statistics | -- |

### `mcp__kegg__kegg_data` (Pathway & Compound Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_pathways` | Search KEGG pathways by keyword | `query` |
| `get_pathway_info` | Full pathway details (description, classes, modules) | `pathway_id` |
| `get_pathway_genes` | All genes in a pathway | `pathway_id` |
| `get_pathway_compounds` | All compounds in a pathway | `pathway_id` |
| `get_pathway_reactions` | All reactions in a pathway | `pathway_id` |
| `search_genes` | Search genes by keyword | `query` |
| `get_gene_info` | Gene details (orthologs, pathways, motifs) | `gene_id` |
| `get_gene_orthologs` | Ortholog groups for a gene | `gene_id` |
| `search_reactions` | Search biochemical reactions | `query` |
| `get_reaction_info` | Reaction details (substrates, products, enzymes) | `reaction_id` |
| `search_modules` | Search functional modules | `query` |
| `get_module_info` | Module details (pathway context, components) | `module_id` |
| `convert_identifiers` | Convert between KEGG and external IDs | `identifiers`, `source_db`, `target_db` |
| `find_related_entries` | Find entries related to a given KEGG entry | `entry_id` |

### `mcp__reactome__reactome_data` (Pathway Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_pathways` | Search pathways by keyword | `query`, `species` |
| `get_pathway_details` | Full pathway info | `pathway_id` |
| `find_pathways_by_gene` | Pathways containing a gene | `gene_id`, `species` |
| `find_pathways_by_disease` | Pathways associated with disease | `disease_name` |
| `get_pathway_hierarchy` | Parent/child pathway tree | `pathway_id` |
| `get_pathway_participants` | Molecules in a pathway | `pathway_id` |
| `get_pathway_reactions` | Reactions in a pathway | `pathway_id` |
| `get_protein_interactions` | Protein interactions from Reactome | `protein_id` |

### `mcp__depmap__depmap_data` (Functional Validation of Systems Models)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_multi_gene_profile` | Functional validation of systems models via multi-gene dependency profiles | `genes`, `lineage`, `dataset` |
| `get_gene_dependency_summary` | Pan-cancer essentiality scores for pathway members | `gene`, `dataset` |

**DepMap workflow:** Validate systems model predictions with functional dependency data -- check whether genes predicted as essential by network topology or pathway models are actually required for cell viability in large-scale CRISPR screens. Pan-cancer essentiality profiles reveal context-dependent vs constitutive pathway dependencies.

```
mcp__depmap__depmap_data(method: "get_multi_gene_profile", genes: ["BRAF", "MAP2K1", "MAPK1"], lineage: "skin")
mcp__depmap__depmap_data(method: "get_gene_dependency_summary", gene: "KRAS")
```

---

## 4-Phase Pathway Analysis Workflow

### Phase 1: Statistical Enrichment — Identify Overrepresented Pathways

```
1. For each gene in your gene set, retrieve target details:
   mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL")
   → Get Ensembl gene ID

2. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Extract pathway annotations (Reactome, GO terms) for each gene

2b. mcp__geneontology__go_data(method: "search_go_terms", query: "kinase activity", ontology: "molecular_function", size: 10)
    → Resolve GO term names from enrichment results to canonical GO IDs and definitions

2c. mcp__geneontology__go_data(method: "get_go_term", id: "GO:0004672")
    → Get full GO term details (definition, synonyms, xrefs) for pathway annotation

3. mcp__stringdb__stringdb_data(method: "get_functional_enrichment", protein_ids: ["GENE_A", "GENE_B", "GENE_C"], species: 9606)
   → GO/KEGG/Reactome enrichment with p-values directly from STRING

3b. mcp__reactome__reactome_data(method: "find_pathways_by_gene", gene_id: "GENE_SYMBOL", species: "Homo sapiens")
    → Direct Reactome pathway lookup per gene with hierarchy context

3c. mcp__kegg__kegg_data(method: "search_pathways", query: "MAPK signaling")
    → Find KEGG pathways matching a keyword
    mcp__kegg__kegg_data(method: "get_pathway_genes", pathway_id: "hsa04010")
    → Get all genes in the KEGG pathway to calculate overlap with your gene set

4. Tabulate pathway membership across your gene set:
   - Count genes per pathway
   - Calculate overlap ratio: (genes in set ∩ pathway) / (total genes in pathway)
   - Rank pathways by gene overlap ratio
   - Cross-validate STRING enrichment results with Open Targets and KEGG pathway annotations

5. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "pathway_name gene set enrichment", num_results: 10)
   → Literature support for top enriched pathways
```

### Phase 2: Protein-to-Pathway Mapping — Resolve Targets to Pathways

```
1. mcp__chembl__chembl_info(method: "target_search", query: "gene_symbol")
   → Get ChEMBL target ID and target classification

2. mcp__drugbank__drugbank_info(method: "search_by_target", target: "gene_symbol")
   → Find drugs modulating this target

3. For each drug found:
   mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   → Map target to metabolic/signaling pathways via drug-pathway associations

4. mcp__pubchem__pubchem_info(method: "get_compound_targets", cid: "CID_NUMBER", limit: 50)
   → Reverse map: find all targets of compounds in the pathway
```

### Phase 3: Cross-Database Parallel Search — Validate Across Sources

```
Execute in parallel for each candidate pathway:

Source 1 — Open Targets:
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Reactome pathway annotations, GO biological processes

Source 2 — DrugBank:
   mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   → SMPDB/KEGG pathway mappings

Source 3 — PubChem:
   mcp__pubchem__pubchem_info(method: "get_compound_pathways", cid: "CID_NUMBER", limit: 50)
   → Pathway associations from PubChem BioAssay data

Source 4 — STRING:
   mcp__stringdb__stringdb_data(method: "get_protein_annotations", protein_ids: ["GENE_SYMBOL"], species: 9606)
   → Functional annotations aggregated from multiple sources

Source 5 — PubMed:
   mcp__pubmed__pubmed_articles(method: "search_advanced", term: "gene_symbol pathway_name signaling", num_results: 15)
   → Published pathway membership evidence

→ A finding is VALIDATED when confirmed by ≥ 2 independent sources
```

### Phase 4: Hierarchical Pathway Context — Place Pathways in Biological Hierarchy

```
1. Classify each validated pathway into hierarchy:
   Top-level category → Specific pathway → Individual reactions

   Examples:
   - Signal transduction → MAPK signaling → RAS-RAF-MEK-ERK cascade
   - Metabolism → Lipid metabolism → Fatty acid beta-oxidation
   - Immune system → Adaptive immunity → T cell receptor signaling

1b. mcp__reactome__reactome_data(method: "get_pathway_hierarchy", pathway_id: "R-HSA-XXXXX")
    → Retrieve parent/child pathway tree from Reactome for precise hierarchical placement

1c. mcp__reactome__reactome_data(method: "get_pathway_participants", pathway_id: "R-HSA-XXXXX")
    → Get all molecules (proteins, small molecules, complexes) in the pathway

1d. mcp__reactome__reactome_data(method: "get_pathway_reactions", pathway_id: "R-HSA-XXXXX")
    → Individual reactions within the pathway for L4-level resolution

2. mcp__pubchem__pubchem_info(method: "get_compound_classification", cid: "CID_NUMBER")
   → Pharmacological classification helps place compounds in pathway context

3. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   → Pharmacodynamics text reveals upstream/downstream pathway relationships

4. Map pathway crosstalk:
   - Identify genes appearing in multiple pathways
   - Score crosstalk: (shared genes between pathway A and B) / (min(|A|, |B|))
   - Flag hub genes that bridge multiple pathways
```

---

## Gene Set Analysis Workflows

### Over-Representation Analysis (ORA)

```
1. Define your gene set (e.g., differentially expressed genes, GWAS hits)

2. For each gene, retrieve pathway annotations:
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Pathway memberships from Reactome, GO

3. Count gene-pathway overlaps and calculate enrichment:
   - Observed overlap vs expected by chance
   - p-value = hypergeometric test (genes in set ∩ pathway / background)
   - Apply multiple testing correction (Bonferroni or FDR)

4. Validate top pathways:
   mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   → Confirm pathway involvement via drug-pathway data

5. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "pathway_name over-representation enrichment gene_symbol", num_results: 10)
   → Literature evidence for enrichment findings
```

### Pathway Perturbation Analysis

```
1. Identify perturbation (drug, mutation, environmental factor):
   mcp__chembl__chembl_info(method: "compound_search", query: "perturbation_agent")
   → Get compound ID

2. Map perturbation targets:
   mcp__pubchem__pubchem_info(method: "get_compound_targets", cid: "CID_NUMBER", limit: 100)
   → All known targets of the perturbation agent

3. For each target, get pathway membership:
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Pathways directly affected by perturbation

4. Assess downstream propagation:
   mcp__drugbank__drugbank_info(method: "search_by_target", target: "downstream_target")
   → Drugs hitting downstream nodes reveal pathway flow direction

5. Score perturbation impact:
   - Direct targets (primary effect)
   - One-hop downstream (secondary effect)
   - Pathway output nodes (functional consequence)
```

### Network Topology Analysis

```
1. Build target interaction network:
   For each gene in set:
   mcp__pubchem__pubchem_info(method: "get_compound_targets", cid: "CID_NUMBER", limit: 50)
   → Shared compound targets reveal functional connections

2. Identify network hubs:
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Targets with many pathway memberships = network hubs

3. Identify bottleneck nodes:
   - Genes that bridge otherwise disconnected pathway clusters
   - High betweenness centrality in the target interaction network

4. mcp__drugbank__drugbank_info(method: "search_by_target", target: "hub_gene")
   → Existing drugs targeting hub nodes (high-impact intervention points)

5. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "hub_gene network topology essential node", num_results: 10)
   → Literature on network importance of hub genes
```

---

## Multi-Database Cross-Validation Framework

### Validation Rules

All pathway findings must meet the following criteria:

| Rule | Requirement | How to verify |
|------|------------|---------------|
| **Minimum sources** | Pathway membership confirmed in >= 2 databases | Cross-reference Open Targets, DrugBank, PubChem pathway data |
| **Gene overlap threshold** | >= 3 genes from set must map to pathway | Count unique gene-pathway mappings |
| **Literature support** | At least 1 published study supports the association | PubMed search for pathway + gene set context |
| **Directional consistency** | Pathway activation/inhibition direction consistent across sources | Compare DrugBank pharmacodynamics with PubChem bioassay data |

### Cross-Database Comparison with Source Attribution

```
For each pathway finding, create attribution table:

| Finding | Open Targets | DrugBank | PubChem | PubMed | Consensus |
|---------|-------------|----------|---------|--------|-----------|
| Gene X in pathway Y | Reactome annotation | SMPDB mapping | BioAssay pathway | 3 publications | CONFIRMED |
| Gene A in pathway B | No data | KEGG mapping | No data | 1 publication | WEAK |
| Gene C in pathway D | GO annotation | SMPDB mapping | Pathway association | 5 publications | STRONG |

Consensus levels:
- CONFIRMED: >= 3 sources agree
- SUPPORTED: 2 sources agree
- WEAK: 1 source only
- CONFLICTING: Sources disagree on membership or direction
```

---

## Pathway Scoring Framework

### Composite Pathway Score

```
Score = (w1 × Enrichment) + (w2 × Overlap) + (w3 × Agreement)

Where:
- Enrichment = -log10(p-value) from over-representation analysis, capped at 10
- Overlap = (genes in set ∩ pathway) / (total genes in pathway), range 0-1
- Agreement = (number of databases confirming) / (total databases queried), range 0-1

Default weights:
- w1 = 0.4 (statistical enrichment)
- w2 = 0.3 (gene overlap ratio)
- w3 = 0.3 (cross-database agreement)

Interpretation:
- Score > 7.0: High-confidence pathway involvement
- Score 4.0-7.0: Moderate evidence, warrants investigation
- Score 2.0-4.0: Suggestive, needs additional validation
- Score < 2.0: Insufficient evidence
```

### Pathway Hierarchy Levels

| Level | Description | Example |
|-------|------------|---------|
| **L1 — Top-level category** | Broad biological process | Signal transduction, Metabolism, Immune system |
| **L2 — Specific pathway** | Named signaling/metabolic pathway | MAPK cascade, Glycolysis, NF-kB signaling |
| **L3 — Sub-pathway** | Specific branch or module | ERK1/2 activation, Hexokinase step, IKK complex activation |
| **L4 — Individual reaction** | Single biochemical event | RAF phosphorylates MEK, Glucose -> G6P |

```
Workflow for hierarchy assignment:

1. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Reactome pathways include hierarchy (top-level → specific)

2. mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   → SMPDB pathways map to specific metabolic sub-pathways

3. mcp__pubchem__pubchem_info(method: "get_compound_pathways", cid: "CID_NUMBER", limit: 50)
   → Pathway associations help place reactions in context

4. Aggregate: group specific pathways under top-level categories
   → Identify which top-level biological processes are most affected
```

---

## Evidence Grading System

### Tier Definitions

| Tier | Label | Criteria | Action |
|------|-------|----------|--------|
| **T1** | Definitive | >= 3 databases confirm + p-value < 0.001 + published functional studies | Report as established pathway involvement |
| **T2** | Strong | 2 databases confirm + p-value < 0.01 + literature support | Report with high confidence |
| **T3** | Moderate | 1-2 databases + p-value < 0.05 + some literature | Report as probable, flag for validation |
| **T4** | Preliminary | Single database or computational prediction only | Report as hypothesis, requires experimental validation |

### Grading Workflow

```
1. Statistical evidence:
   Calculate enrichment p-value from ORA (Phase 1)
   → Assign base tier from p-value alone

2. Database agreement:
   Cross-reference Phase 3 results
   → Upgrade tier if multiple databases confirm

3. Literature validation:
   mcp__pubmed__pubmed_articles(method: "search_advanced", term: "pathway_name gene_set_context functional validation", num_results: 20)
   → Upgrade tier if functional studies exist

4. Downgrade conditions:
   - Small gene set overlap (< 3 genes) → downgrade 1 tier
   - Conflicting database evidence → downgrade 1 tier
   - Pathway is very large (> 500 genes, e.g., "metabolism") → downgrade 1 tier (low specificity)
```

---

## Multi-Agent Workflow Examples

**"Analyze pathway enrichment for a set of differentially expressed genes in breast cancer"**
1. Systems Biology -> ORA across Open Targets, DrugBank, PubChem; pathway scoring; hierarchical classification
2. Disease Research -> Disease-specific pathway context, known driver pathways in breast cancer
3. Target Research -> Functional validation evidence for top enriched targets
4. Drug Target Analyst -> Druggability of targets in enriched pathways

**"Map the signaling network downstream of EGFR mutation"**
1. Systems Biology -> EGFR pathway hierarchy mapping, downstream propagation analysis, crosstalk identification
2. Target Research -> EGFR target details, functional evidence, protein interactions
3. Network Pharmacologist -> Polypharmacology of EGFR inhibitors, off-pathway effects
4. Gene Enrichment -> Formal enrichment analysis of EGFR-dependent gene sets

**"Compare pathway involvement of BRCA1 vs BRCA2 in DNA repair"**
1. Systems Biology -> Pathway membership for both genes, shared vs unique pathways, hierarchy placement
2. Target Research -> Functional characterization of BRCA1 and BRCA2
3. Disease Research -> Cancer types associated with each gene's pathway defects
4. Drug Target Analyst -> Synthetic lethality targets (e.g., PARP inhibitors) in these pathways

**"Identify pathway crosstalk between inflammation and metabolism in obesity"**
1. Systems Biology -> Cross-pathway analysis, shared genes between inflammatory and metabolic pathways, hub identification
2. Disease Research -> Obesity-associated targets and pathway evidence
3. Network Pharmacologist -> Multi-target drugs bridging inflammatory and metabolic pathways
4. Drug Target Analyst -> Druggable nodes at pathway intersection points

## Completeness Checklist

- [ ] Gene set fully resolved to Ensembl IDs via Open Targets
- [ ] STRING functional enrichment performed with p-values for GO/KEGG/Reactome
- [ ] Pathway membership cross-validated across at least 2 databases (Open Targets, DrugBank, PubChem, KEGG, Reactome)
- [ ] Pathway hierarchy assigned (L1-L4) for all validated pathways
- [ ] Composite pathway scores calculated (enrichment + overlap + agreement)
- [ ] Evidence grading (T1-T4) applied to each pathway finding
- [ ] Pathway crosstalk and hub genes identified
- [ ] Literature support retrieved for top enriched pathways
- [ ] Cross-database attribution table completed with consensus levels
- [ ] No unresolved gene symbols or missing identifier mappings remain
