---
name: protein-interactions
description: Protein-protein interaction (PPI) network analyst. PPI network construction, functional enrichment, hub protein identification, pathway context, interaction confidence scoring, network topology analysis. Use when user mentions protein interaction, PPI, interactome, protein network, hub protein, bottleneck protein, functional enrichment, GO enrichment, KEGG pathway, Reactome, interaction partners, protein complex, network topology, degree centrality, betweenness centrality, clustering coefficient, STRING, BioGRID, or interaction confidence.
---

# Protein Interactions

Analyzes protein-protein interaction networks for functional enrichment, hub protein identification, and pathway context using multiple databases. Uses Open Targets for target details including PPI data, ChEMBL for target interactions, DrugBank for drug-target-protein connections, PubMed for literature evidence, and PubChem for compound-target-pathway integration.

## Report-First Workflow

1. **Create report file immediately**: `[query]_protein_interactions_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## Cross-Reference: Other Skills

- **Target function and druggability assessment** → use target-research skill
- **Network pharmacology and polypharmacology** → use network-pharmacologist skill
- **Systems-level pathway modeling** → use systems-biology skill
- **Drug target identification and validation** → use drug-target-analyst skill
- **Disease-gene associations and phenotype mapping** → use disease-research skill

## When NOT to Use This Skill

- Target druggability assessment or tractability scoring → use `target-research`
- Polypharmacology analysis or multi-target drug strategy → use `network-pharmacologist`
- Dynamic pathway modeling or flux balance analysis → use `systems-biology`
- Drug target identification and validation scoring → use `drug-target-analyst`
- Disease-gene association mapping or phenotype analysis → use `disease-research`
- Protein 3D structure retrieval and quality assessment → use `protein-structure-retrieval`

## Available MCP Tools

### `mcp__opentargets__opentargets_info` (Target Details & PPI Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `search_diseases` | Search diseases by name/synonym | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId` (Ensembl ID), `diseaseId` (EFO ID), `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability, interactions) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes) | `id` (EFO ID) |

### `mcp__chembl__chembl_info` (Target Interactions & Bioactivity)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |
| `get_admet` | ADMET/drug-likeness properties | `chembl_id` |

### `mcp__drugbank__drugbank_info` (Drug-Target-Protein Connections)

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

### `mcp__pubmed__pubmed_articles` (PPI Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__uniprot__uniprot_data` (Protein Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_protein_info` | Full protein profile | `accession`, `format` |
| `search_by_gene` | Find proteins by gene name | `gene`, `organism`, `size` |
| `get_protein_features` | Protein features (domains, sites, PTMs) | `accession` |
| `get_protein_interactions` | Known protein interactions | `accession` |
| `get_protein_pathways` | Pathway involvement | `accession` |
| `search_by_function` | Search by GO term or function | `goTerm`, `function`, `organism`, `size` |
| `compare_proteins` | Compare 2-10 proteins | `accessions` |
| `get_protein_sequence` | Get protein sequence (FASTA/JSON) | `accession`, `format` |

### `mcp__stringdb__stringdb_data` (Protein-Protein Interactions)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_protein_interactions` | Get interaction partners for a protein | `protein_id`, `species`, `limit`, `required_score` |
| `get_interaction_network` | Build interaction network from protein list | `protein_ids`, `species`, `required_score`, `network_type`, `add_nodes` |
| `get_functional_enrichment` | GO/KEGG/Reactome enrichment for protein set | `protein_ids`, `species`, `background_string_identifiers` |
| `get_protein_annotations` | Get functional annotations | `protein_ids`, `species` |
| `search_proteins` | Search proteins by name | `query`, `species`, `limit` |

### `mcp__pubchem__pubchem_info` (Compound-Target-Pathway Integration)

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

### `mcp__alphafold__alphafold_data` (AlphaFold Predicted Structures)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_structure` | Get AlphaFold predicted structure for interface analysis | `uniprotId`, `format` (json/pdb/cif) |
| `check_availability` | Check if prediction exists | `uniprotId` |
| `get_confidence_scores` | Get pLDDT scores for interaction interface confidence | `uniprotId` |
| `analyze_confidence_regions` | Identify high/low confidence regions at interfaces | `uniprotId` |
| `compare_structures` | Compare structures of two interacting proteins | `uniprotId1`, `uniprotId2` |

### `mcp__pdb__pdb_data` (Experimental Structures from PDB)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_structures` | Search for co-crystal/complex structures | `query`, `limit`, `experimental_method`, `resolution_range`, `sort_by` |
| `get_structure_info` | Get structure details (chains, interfaces) | `pdb_id`, `format` |
| `search_by_uniprot` | Find PDB structures for interacting protein | `uniprot_id`, `limit` |
| `get_structure_quality` | Resolution, R-factor, validation | `pdb_id` |

---

## 4-Phase PPI Analysis Workflow

### Phase 1: Identifier Mapping

Resolve gene symbols to stable identifiers across databases.

```
1. mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL", size: 5)
   → Get Ensembl gene ID (ENSG...) and UniProt accession

2. mcp__chembl__chembl_info(method: "target_search", query: "GENE_SYMBOL", limit: 5)
   → Get ChEMBL target ID and target classification

3. mcp__drugbank__drugbank_info(method: "search_by_target", target: "GENE_SYMBOL", limit: 10)
   → Identify drugs targeting this protein (confirms target identity)

4. mcp__drugbank__drugbank_info(method: "get_external_identifiers", drugbank_id: "DBxxxxx")
   → Cross-database ID mapping (PubChem, ChEMBL, KEGG, UniProt)

5. mcp__uniprot__uniprot_data(method: "search_by_gene", gene: "GENE_SYMBOL", organism: "human", size: 5)
   → Get UniProt accession, protein name, and functional annotations

6. mcp__uniprot__uniprot_data(method: "get_protein_info", accession: "UNIPROT_ACC")
   → Full protein profile with cross-references, function, subcellular location

7. Repeat for all query proteins to build the identifier mapping table:
   Gene Symbol → Ensembl ID → UniProt → ChEMBL Target ID → DrugBank Target
```

### Phase 2: Network Retrieval with Confidence Scores

Retrieve interaction partners and assign confidence scores.

```
1. mcp__stringdb__stringdb_data(method: "get_protein_interactions", protein_id: "GENE_SYMBOL", species: 9606, limit: 50, required_score: 700)
   → Retrieve high-confidence interaction partners directly from STRING

2. mcp__stringdb__stringdb_data(method: "get_interaction_network", protein_ids: ["GENE_A", "GENE_B", "GENE_C"], species: 9606, required_score: 400, network_type: "functional", add_nodes: 10)
   → Build full interaction network from query proteins, adding 10 closest interactors

3. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Retrieve known interaction partners, pathways, and functional annotations
   → Extract PPI data from target profile (interacts_with field)

4. For each query protein, expand the network:
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG_PARTNER")
   → Retrieve interaction partners of partners (second-degree interactions)

5. mcp__chembl__chembl_info(method: "get_bioactivity", target_id: "CHEMBL_TARGET", limit: 100)
   → Bioactivity-confirmed interactions (compounds bridging two targets)

4. mcp__pubchem__pubchem_info(method: "get_compound_targets", cid: "CID_NUMBER", limit: 50)
   → Compound-mediated target connections

5. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "PROTEIN_A PROTEIN_B interaction", num_results: 10)
   → Literature-confirmed physical interactions

6. mcp__uniprot__uniprot_data(method: "get_protein_interactions", accession: "UNIPROT_ACC")
   → UniProt-curated interaction partners with evidence codes

7. mcp__uniprot__uniprot_data(method: "get_protein_features", accession: "UNIPROT_ACC")
   → Domain architecture and binding sites relevant to interaction interfaces

8. Assign confidence scores to each interaction:
   - Experimental evidence (co-IP, Y2H, crosslinking MS): 0.9+
   - Database-curated (multiple sources agree): 0.7-0.9
   - Computational prediction (co-expression, gene neighborhood): 0.4-0.7
   - Text mining only: < 0.4
```

### Phase 3: Functional Enrichment (GO/KEGG/Reactome)

Annotate the network with biological function and pathway context.

```
1. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Extract Gene Ontology annotations: Biological Process, Molecular Function, Cellular Component
   → Extract Reactome pathway memberships

2. mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   → KEGG and SMPDB pathway associations for drug-targeted proteins

3. mcp__pubchem__pubchem_info(method: "get_compound_pathways", cid: "CID_NUMBER", limit: 50)
   → Pathway associations via compound-target links

4. mcp__uniprot__uniprot_data(method: "get_protein_pathways", accession: "UNIPROT_ACC")
   → UniProt pathway annotations (Reactome, KEGG cross-references)

5. mcp__stringdb__stringdb_data(method: "get_functional_enrichment", protein_ids: ["GENE_A", "GENE_B", "GENE_C"], species: 9606)
   → GO/KEGG/Reactome enrichment directly from STRING for the network protein set

6. Perform enrichment analysis on the network:
   - Collect GO terms for all proteins in the network
   - Identify overrepresented terms (enrichment ratio > 2, p < 0.05 after BH correction)
   - Group by GO domain: BP (biological process), MF (molecular function), CC (cellular component)

5. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", minScore: 0.3, size: 50)
   → Disease associations for network proteins (disease enrichment)

6. Build pathway-protein matrix:
   - Rows = pathways (Reactome, KEGG)
   - Columns = network proteins
   - Values = membership (1/0)
   - Identify pathway modules (groups of proteins co-occurring in multiple pathways)
```

### Phase 4: Structural Data Integration

Incorporate structural and biophysical evidence for interactions.

```
1. mcp__pdb__pdb_data(method: "search_structures", query: "PROTEIN_A PROTEIN_B complex", experimental_method: "X-RAY DIFFRACTION", limit: 10)
   → Search for co-crystal structures of the interacting proteins

2. mcp__pdb__pdb_data(method: "search_by_uniprot", uniprot_id: "UNIPROT_ACC", limit: 10)
   → Find all PDB structures for each interacting protein

3. mcp__pdb__pdb_data(method: "get_structure_quality", pdb_id: "XXXX")
   → Assess quality of complex structures for interface analysis

4. mcp__alphafold__alphafold_data(method: "get_structure", uniprotId: "UNIPROT_ACC", format: "pdb")
   → AlphaFold predicted structure for proteins without experimental data

5. mcp__alphafold__alphafold_data(method: "analyze_confidence_regions", uniprotId: "UNIPROT_ACC")
   → Assess confidence at predicted interaction interfaces

6. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Protein structure availability (PDB IDs), domain architecture
   → Subcellular localization (membrane, cytoplasm, nucleus)

7. mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "CHEMBLxxxxx", target_id: "CHEMBL_TARGET", limit: 50)
   → Binding data confirming physical interaction at specific sites

8. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "PROTEIN_A PROTEIN_B crystal structure OR cryo-EM OR co-crystal", num_results: 10)
   → Published co-crystal structures confirming direct interaction

9. mcp__pubchem__pubchem_info(method: "get_bioassay_summary", cid: "CID_NUMBER", limit: 50)
   → Bioassay data confirming compound-mediated protein interactions

10. Integrate structural evidence:
   - Co-crystal structure available (PDB) → highest confidence (direct physical contact)
   - AlphaFold high-confidence interface (pLDDT > 70) → supporting evidence
   - Domain-domain interaction predicted → high confidence
   - Co-localization in same compartment → supporting evidence
   - Different compartments → flag as indirect or conditional interaction
```

---

## Confidence Score Interpretation

### Interaction Confidence Tiers

| Score Range | Confidence | Evidence Types | Interpretation |
|-------------|-----------|----------------|----------------|
| **0.9+** | Highest | Co-crystal structure, co-IP with reciprocal validation, crosslinking MS | Direct physical interaction confirmed by multiple experimental methods |
| **0.7-0.9** | High | Y2H confirmed by co-IP, curated in multiple databases, proximity labeling | Likely direct interaction with strong experimental support |
| **0.4-0.7** | Medium | Single experimental method, co-expression, gene neighborhood, gene fusion | Possible interaction; functional association likely |
| **< 0.4** | Low | Text mining, phylogenetic profile, computational prediction only | Hypothesis level; requires experimental validation |

### Score Aggregation

```
Combined score = 1 - ∏(1 - S_i)
where S_i = individual evidence channel score

Example: experimental = 0.8, database = 0.7, text mining = 0.3
Combined = 1 - (1-0.8)(1-0.7)(1-0.3) = 1 - 0.2 × 0.3 × 0.7 = 1 - 0.042 = 0.958
```

---

## Network Metrics

### Topology Metrics for PPI Networks

| Metric | Formula | Biological Meaning |
|--------|---------|-------------------|
| **Degree centrality** | C_D(v) = deg(v) / (N-1) | Number of interaction partners; high = hub protein |
| **Betweenness centrality** | C_B(v) = Σ σ_st(v) / σ_st | Fraction of shortest paths through node; high = bottleneck protein |
| **Clustering coefficient** | C_C(v) = 2e_v / (k_v(k_v-1)) | How interconnected a protein's neighbors are; high = part of complex |
| **Closeness centrality** | C_Cl(v) = (N-1) / Σ d(v,u) | Average distance to all other proteins; high = central position |
| **Eigenvector centrality** | Ax = λx | Influence measure; high = connected to other well-connected proteins |
| **Network density** | D = 2E / (N(N-1)) | Proportion of possible edges present; typical PPI networks: 0.01-0.1 |

### Computing Network Metrics

```
1. Build adjacency matrix from Phase 2 interactions
   - Rows/columns = proteins
   - Values = confidence scores (weighted) or 1/0 (unweighted)

2. Degree centrality:
   - Count edges per node (weighted: sum of confidence scores)
   - Rank proteins by degree

3. Betweenness centrality:
   - Compute shortest paths between all pairs
   - Count paths passing through each node
   - Normalize by total number of pairs

4. Clustering coefficient:
   - For each protein, count edges among its neighbors
   - Divide by maximum possible edges among neighbors
   - Average across network = global clustering coefficient

5. Hub detection threshold:
   - Mean degree + 2 SD = hub threshold
   - Proteins above this threshold are network hubs

6. Bottleneck detection:
   - Top 5% by betweenness centrality = bottleneck proteins
   - Proteins that are both hubs AND bottlenecks = critical network nodes
```

---

## Hub Protein Identification

### Classification Criteria

```
Hub protein:
  Degree > mean_degree + 2 * SD_degree
  → Interacts with significantly more proteins than average
  → Biological role: scaffold, chaperone, signaling integrator

Bottleneck protein:
  Betweenness centrality in top 5%
  → Controls information flow between network modules
  → Biological role: signal transducer, pathway gatekeeper

Hub-bottleneck (critical node):
  Both hub AND bottleneck criteria met
  → Removal would fragment the network
  → Highest priority for functional studies and drug targeting

Date hub vs Party hub:
  Date hub: interacts with different partners at different times/locations
    → Low co-expression with partners
    → Often in signaling pathways
  Party hub: interacts with all partners simultaneously
    → High co-expression with partners
    → Often in stable complexes
```

### Hub Protein Workflow

```
1. Build interaction network (Phase 1-2 above)

2. Compute degree for all proteins:
   For each protein in network:
     mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
     → Count interaction partners

3. Identify hubs:
   mean_degree = average(all_degrees)
   sd_degree = stdev(all_degrees)
   hub_threshold = mean_degree + 2 * sd_degree
   hubs = proteins where degree > hub_threshold

4. Characterize hubs:
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "HUB_ENSG")
   → Function, subcellular location, tractability
   → Disease associations (essential genes often disease-linked)

5. Assess hub druggability:
   mcp__drugbank__drugbank_info(method: "search_by_target", target: "HUB_GENE_SYMBOL", limit: 20)
   → Existing drugs targeting hub proteins

6. mcp__chembl__chembl_info(method: "get_bioactivity", target_id: "CHEMBL_HUB_TARGET", limit: 50)
   → Chemical tools available for hub protein modulation

7. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "HUB_GENE essential gene lethal knockout", num_results: 10)
   → Essentiality data (caution: targeting essential hubs may cause toxicity)
```

---

## Functional Module Detection

### Identifying Densely Connected Subnetworks

```
Functional modules represent biological complexes or pathway clusters:

1. Build weighted adjacency matrix from Phase 2

2. Community detection approaches:
   a. Clique-based: find maximal cliques (fully connected subgraphs)
   b. Modularity optimization: partition network to maximize Q = Σ(e_ii - a_i²)
   c. Label propagation: iterative neighbor-based module assignment

3. Module quality metrics:
   - Modularity Q > 0.3 indicates significant community structure
   - Module density = edges_within / max_possible_edges_within
   - Module separation = edges_within / (edges_within + edges_between)

4. For each detected module:
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "MODULE_PROTEIN_ENSG")
   → Annotate with GO terms, pathways

5. Module functional annotation:
   - Collect GO terms for all module members
   - Enrichment test vs background network
   - Assign module function based on most enriched term

6. Known complex mapping:
   mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "PROTEIN_A PROTEIN_B PROTEIN_C complex", num_results: 10)
   → Match modules to known protein complexes (CORUM, ComplexPortal)
```

---

## PPI Enrichment Testing

### Do Query Proteins Interact More Than Expected?

```
Null hypothesis: query proteins have no more interactions among themselves
than expected by chance given their individual degrees.

Test procedure:
1. Count observed interactions among query proteins: E_obs

2. Expected interactions under random model:
   E_exp = Σ (d_i × d_j) / (2 × E_total)
   for all query protein pairs (i,j)
   where d_i = degree of protein i, E_total = total network edges

3. Enrichment ratio = E_obs / E_exp

4. P-value estimation:
   - Generate 1000 random protein sets of same size
   - Count interactions among random sets
   - P = fraction of random sets with ≥ E_obs interactions

5. Interpretation:
   Enrichment ratio > 2 and p < 0.01 → proteins form a functional module
   Enrichment ratio ~ 1 → no more connected than random
   Enrichment ratio < 1 → less connected than expected (dispersed functions)
```

### PPI Enrichment Workflow

```
1. Define query protein set:
   mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL", size: 5)
   → Resolve each query protein to Ensembl ID

2. Retrieve interactions for each query protein:
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Count interactions among query proteins vs total interactions

3. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.5, size: 100)
   → Disease gene set as comparison (do disease genes interact more than random?)

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_LIST protein interaction network enrichment", num_results: 10)
   → Published PPI enrichment analyses for this gene set
```

---

## Drug-Target-PPI Integration

### Mapping Known Drugs to Interaction Partners

```
1. Start from protein of interest:
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Get interaction partners list

2. For each interaction partner, find existing drugs:
   mcp__drugbank__drugbank_info(method: "search_by_target", target: "PARTNER_GENE", limit: 20)
   → Approved drugs modulating PPI partners

3. mcp__chembl__chembl_info(method: "get_bioactivity", target_id: "CHEMBL_PARTNER", limit: 50)
   → Chemical probes available for partner proteins

4. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   → Drug mechanism — does it disrupt or stabilize the interaction?

5. mcp__pubchem__pubchem_info(method: "get_compound_targets", cid: "CID_NUMBER", limit: 50)
   → Full target spectrum of drugs hitting PPI partners (off-target effects on network)

6. mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   → Pathway context for drug action within the PPI network

7. mcp__pubchem__pubchem_info(method: "get_compound_pathways", cid: "CID_NUMBER", limit: 50)
   → Pathway overlap between drug targets and PPI network members

8. PPI-informed drug prioritization:
   - Drugs targeting hub proteins → broad network disruption (efficacy + toxicity risk)
   - Drugs targeting bottleneck proteins → selective pathway modulation
   - Drugs targeting peripheral nodes → minimal network perturbation
   - Drugs targeting module members → complex/pathway-specific effects

9. mcp__drugbank__drugbank_info(method: "search_by_carrier", carrier: "CARRIER_PROTEIN", limit: 10)
   → Drugs sharing carrier proteins with PPI network members

10. mcp__drugbank__drugbank_info(method: "search_by_transporter", transporter: "TRANSPORTER", limit: 10)
    → Drugs sharing transporters (pharmacokinetic interactions via PPI network)
```

---

## Evidence Grading Framework

### PPI Evidence Tiers

| Tier | Evidence Type | Confidence | Action |
|------|-------------|------------|--------|
| **T1 (Strongest)** | Co-crystal structure, cryo-EM complex, crosslinking MS with interface mapping | Highest (0.9+) | Direct physical contact confirmed; proceed to functional validation |
| **T2** | Co-immunoprecipitation (reciprocal), proximity labeling (BioID/APEX), FRET/BRET | High (0.7-0.9) | Interaction in cellular context confirmed; map domains and conditions |
| **T3** | Yeast two-hybrid, affinity purification MS, genetic interaction (synthetic lethal) | Medium (0.4-0.7) | Interaction detected but may be indirect; confirm with orthogonal method |
| **T4 (Weakest)** | Co-expression correlation, text mining, phylogenetic profile, computational prediction | Low (< 0.4) | Hypothesis only; requires experimental validation before conclusions |

### Evidence Assessment Workflow

```
1. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Check interaction evidence sources and confidence in target profile

2. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "PROTEIN_A PROTEIN_B (co-immunoprecipitation OR co-crystal OR proximity labeling)", num_results: 15)
   → Classify experimental evidence by tier

3. mcp__pubchem__pubchem_info(method: "get_bioassay_summary", cid: "CID_NUMBER", limit: 30)
   → Bioassay evidence for compound-mediated interactions

4. mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "CHEMBLxxxxx", target_id: "CHEMBL_TARGET", limit: 50)
   → Quantitative binding data supporting interaction

5. Assign composite tier:
   - Any T1 evidence → overall T1
   - Multiple T2 sources → overall T2
   - T3 + T4 concordant → overall T3
   - T4 only → overall T4

6. Report confidence with evidence trail:
   "PROTEIN_A—PROTEIN_B: T2 confidence (co-IP confirmed in 2 studies, PMID: xxxxx, xxxxx;
    corroborated by co-expression and text mining)"
```

---

## Multi-Agent Workflow Examples

**"Map the interaction network of TP53 and identify druggable hub proteins"**
1. Protein Interactions → Build TP53 PPI network, compute network metrics, identify hubs and bottlenecks
2. Drug Target Analyst → Druggability assessment of hub proteins, existing compounds, tractability
3. Disease Research → Disease associations for hub proteins (cancer types, Mendelian disorders)

**"Analyze the PPI network disrupted in Parkinson's disease"**
1. Disease Research → Identify Parkinson's-associated genes and proteins
2. Protein Interactions → Build PPI network from disease genes, detect functional modules, enrichment testing
3. Systems Biology → Pathway modeling, feedback loops, dynamic network behavior
4. Network Pharmacologist → Map existing drugs to network nodes, polypharmacology opportunities

**"Identify protein complexes affected by BRCA1 mutations"**
1. Protein Interactions → BRCA1 interaction network, module detection, confidence scoring
2. Target Research → Functional characterization of interaction partners, mutation impact
3. Drug Target Analyst → Synthetic lethality targets in BRCA1 PPI network (e.g., PARP)
4. Network Pharmacologist → Combination strategies targeting multiple network nodes

**"Evaluate PPI evidence for a novel drug target interaction"**
1. Protein Interactions → Evidence grading (T1-T4), confidence scoring, structural data integration
2. Drug Target Analyst → Bioactivity data, mechanism of action, selectivity profile
3. Target Research → Target validation, genetic evidence, functional genomics data

## Completeness Checklist

- [ ] All query proteins resolved to stable identifiers (Ensembl, UniProt, ChEMBL)
- [ ] Interaction network retrieved with confidence scores from STRING and/or Open Targets
- [ ] Hub and bottleneck proteins identified with degree and betweenness centrality
- [ ] Functional enrichment performed (GO biological process, molecular function, cellular component)
- [ ] Pathway context provided (KEGG, Reactome pathway memberships)
- [ ] Evidence tier assigned to each interaction (T1-T4)
- [ ] Structural data checked for key interactions (co-crystal structures, AlphaFold)
- [ ] Drug-target-PPI integration assessed for druggable network nodes
- [ ] Functional modules detected and annotated
- [ ] Report file finalized with no `[Analyzing...]` placeholders remaining
