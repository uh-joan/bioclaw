# CELLxGENE Atlas Recipes

> Copy-paste executable MCP call sequences for single-cell expression analysis.
> Parent skill: [SKILL.md](SKILL.md) — full CELLxGENE analysis pipeline.

---

## Recipe 1: Find Datasets by Tissue

Discover single-cell datasets for a specific tissue.

```
# 1. Browse all collections
mcp__cellxgene__cellxgene_data(method: "list_collections")
# -> Filter results for tissue of interest (e.g., "lung", "brain", "liver")

# 2. Get collection details
mcp__cellxgene__cellxgene_data(method: "get_collection", collection_id: "COLLECTION_ID")
# -> Datasets, DOI, description, cell types covered

# 3. List all datasets for broader search
mcp__cellxgene__cellxgene_data(method: "list_datasets")
# -> Filter by tissue, organism, assay type
```

---

## Recipe 2: Dataset Deep Dive

Get full details and download links for a specific dataset.

```
# 1. Get version history
mcp__cellxgene__cellxgene_data(method: "get_dataset_versions", dataset_id: "DATASET_ID")

# 2. Get latest version details
mcp__cellxgene__cellxgene_data(method: "get_dataset_version", dataset_version_id: "VERSION_ID")
# -> Cell count, gene count, cell types, assay, organism

# 3. Get download manifest
mcp__cellxgene__cellxgene_data(method: "get_dataset_manifest", dataset_id: "DATASET_ID")
# -> H5AD (for scanpy) and RDS (for Seurat) download URLs
```

---

## Recipe 3: Drug Target Expression Profiling

Assess cell-type expression for a drug target gene.

```
# 1. Confirm gene identity
mcp__uniprot__uniprot_data(method: "search_by_gene", gene: "TARGET_GENE", organism: "human", size: 3)

# 2. Get protein-level tissue expression
mcp__uniprot__uniprot_data(method: "get_protein_info", accession: "UNIPROT_ACC", format: "json")

# 3. Find single-cell datasets for relevant tissues
mcp__cellxgene__cellxgene_data(method: "list_collections")
# -> Identify collections covering tissues where gene is expressed

# 4. Literature on cell-type expression
mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "TARGET_GENE scRNA-seq cell type expression", num_results: 10)

# Output format:
# | Tissue | Cell Type | Expression Level | Source |
# |--------|-----------|-----------------|--------|
# | Liver  | Hepatocyte| High            | CELLxGENE collection X |
# | Liver  | Kupffer   | Low             | CELLxGENE collection X |
```

---

## Recipe 4: Disease Collection Comparison

Find and compare healthy vs disease datasets.

```
# 1. Find disease-specific collections
mcp__cellxgene__cellxgene_data(method: "list_collections")
# -> Filter for disease keyword (e.g., "fibrosis", "cancer", "COVID")

# 2. Get healthy tissue collection
mcp__cellxgene__cellxgene_data(method: "get_collection", collection_id: "HEALTHY_COLLECTION_ID")

# 3. Get disease tissue collection
mcp__cellxgene__cellxgene_data(method: "get_collection", collection_id: "DISEASE_COLLECTION_ID")

# 4. Get download manifests for both
mcp__cellxgene__cellxgene_data(method: "get_dataset_manifest", dataset_id: "HEALTHY_DATASET_ID")
mcp__cellxgene__cellxgene_data(method: "get_dataset_manifest", dataset_id: "DISEASE_DATASET_ID")

# -> Download H5AD files for differential expression analysis with scanpy
```

---

## Recipe 5: Collection Version Tracking

Track updates to a collection over time.

```
# 1. Get collection version history
mcp__cellxgene__cellxgene_data(method: "get_collection_versions", collection_id: "COLLECTION_ID")

# 2. Get specific version details
mcp__cellxgene__cellxgene_data(method: "get_collection_version", collection_version_id: "VERSION_ID")

# -> Compare versions to identify newly added datasets or updated cell annotations
```

---

## Recipe 6: Multi-Tissue Expression Survey

Survey a gene's expression across all available tissues.

```
# 1. List all datasets
mcp__cellxgene__cellxgene_data(method: "list_datasets")
# -> Group by tissue type

# 2. For each tissue with relevant datasets:
mcp__cellxgene__cellxgene_data(method: "get_dataset_versions", dataset_id: "DATASET_ID")
# -> Get latest version for each tissue

# 3. Cross-reference with UniProt tissue expression
mcp__uniprot__uniprot_data(method: "get_protein_info", accession: "UNIPROT_ACC", format: "json")

# 4. Build expression map:
# | Tissue | Datasets Available | Cell Types | Key Expressing Cell Types |
# |--------|-------------------|------------|--------------------------|
# | Brain  | 15                | Neurons, Glia, Micro | Neurons (high), Astrocytes (low) |
# | Liver  | 8                 | Hepato, Stellate, KC | Hepatocytes (high) |
```

---

## Cross-Skill Routing

- Drug target validation with genetic evidence → drug-target-validator
- Pharmacogenomics and drug-gene pairs → pharmacogenomics-specialist (ClinPGx)
- Protein design for expressed targets → [protein-therapeutic-design](../protein-therapeutic-design/SKILL.md)
- ESM structure prediction → [esm-protein-design](../esm-protein-design/SKILL.md)
- Enzyme kinetics for expressed enzymes → [enzyme-kinetics](../enzyme-kinetics/SKILL.md)
