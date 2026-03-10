# scvi-tools Deep Learning Model Recipes

Python code templates for scvi-tools deep generative models: scVI batch correction, scANVI label transfer, totalVI CITE-seq, PeakVI ATAC-seq, MultiVI multiome, DestVI spatial deconvolution, veloVI RNA velocity, sysVI cross-platform integration, scArches transfer learning, differential expression, HVG selection, data preparation, and training diagnostics.

Cross-skill routing: use `recipes` for basic scVI/scANVI/totalVI setup (recipes 11-15), `clustering-recipes` for downstream clustering and annotation, `qc-recipes` for upstream QC.

---

## 1. scVI Batch Correction: Full Workflow

Train a variational autoencoder for batch-corrected latent representation with proper data preparation.

```python
import scanpy as sc
import scvi
import matplotlib.pyplot as plt

def scvi_batch_correction(adata, batch_key: str = "batch", n_latent: int = 30,
                          n_layers: int = 2, n_top_genes: int = 4000,
                          max_epochs: int = 400, early_stopping: bool = True):
    """Full scVI workflow: HVG selection, setup, training, latent extraction.

    Parameters
    ----------
    adata : AnnData
        Must contain raw integer counts in adata.layers['counts'] or adata.X.
    batch_key : str
        Column in adata.obs identifying batches.
    n_latent : int
        Latent space dimensionality. 10-30 typical; higher for complex datasets.
    n_layers : int
        Encoder/decoder hidden layers. 1-2 typical.
    n_top_genes : int
        HVGs to select. 2000-5000 typical; 4000 recommended for multi-batch.
    max_epochs : int
        Maximum training epochs.
    early_stopping : bool
        Stop when validation loss plateaus.

    Returns
    -------
    Tuple of (adata, model). adata has 'X_scVI' in obsm.
    """
    # Ensure raw counts are available
    count_layer = None
    if "counts" in adata.layers:
        count_layer = "counts"
    else:
        import numpy as np
        sample = adata.X[:100].toarray() if hasattr(adata.X, "toarray") else adata.X[:100]
        if not np.allclose(sample, np.round(sample), equal_nan=True):
            raise ValueError("adata.X does not contain integer counts. "
                             "Store raw counts in adata.layers['counts'].")

    # HVG selection per batch (reduces batch-specific gene selection bias)
    adata_hvg = adata.copy()
    sc.pp.highly_variable_genes(
        adata_hvg,
        n_top_genes=n_top_genes,
        subset=False,
        flavor="seurat_v3",
        batch_key=batch_key,
        layer=count_layer,
    )
    adata_hvg = adata_hvg[:, adata_hvg.var.highly_variable].copy()

    print(f"Selected {adata_hvg.n_vars} HVGs across {adata.obs[batch_key].nunique()} batches")

    # Register with scVI
    scvi.model.SCVI.setup_anndata(
        adata_hvg,
        layer=count_layer,
        batch_key=batch_key,
    )

    # Initialize model
    model = scvi.model.SCVI(
        adata_hvg,
        n_latent=n_latent,
        n_layers=n_layers,
        dropout_rate=0.1,
        gene_likelihood="zinb",  # zero-inflated negative binomial
    )

    # Train
    model.train(
        max_epochs=max_epochs,
        early_stopping=early_stopping,
        early_stopping_patience=15,
        train_size=0.9,
        batch_size=128,
    )

    # Extract latent representation
    latent = model.get_latent_representation()
    adata.obsm["X_scVI"] = latent

    # Build downstream embeddings
    sc.pp.neighbors(adata, use_rep="X_scVI", n_neighbors=15)
    sc.tl.umap(adata)
    sc.tl.leiden(adata, resolution=0.8, key_added="leiden_scVI")

    print(f"Training complete: {len(model.history['elbo_train'])} epochs")
    print(f"Final ELBO: {model.history['elbo_train'].iloc[-1].values[0]:.2f}")
    print(f"Clusters: {adata.obs['leiden_scVI'].nunique()}")

    return adata, model

# Usage
adata, model = scvi_batch_correction(adata, batch_key="batch", n_latent=30)
model.save("scvi_model/")
```

**Expected output**: Batch-corrected latent space in `adata.obsm['X_scVI']`. UMAP should show batches intermixed while cell types remain separated. ELBO should decrease and stabilize during training.

---

## 2. scANVI Semi-Supervised Label Transfer

Transfer cell type labels from annotated reference to unlabeled query data, chained from a pre-trained scVI model.

```python
import scvi
import numpy as np

def scanvi_label_transfer(adata, scvi_model, labels_key: str = "cell_type",
                          unlabeled_category: str = "Unknown",
                          max_epochs: int = 50, n_samples_per_label: int = 100):
    """Train scANVI from pre-trained scVI for semi-supervised label transfer.

    Parameters
    ----------
    adata : AnnData
        Same adata used for scVI, with partial labels in obs[labels_key].
        Unlabeled cells should be marked with unlabeled_category.
    scvi_model : scvi.model.SCVI
        Pre-trained scVI model.
    labels_key : str
        Column with cell type labels (including unlabeled_category for unknown cells).
    unlabeled_category : str
        Value indicating unlabeled cells.
    max_epochs : int
        Training epochs for scANVI fine-tuning.
    n_samples_per_label : int
        Cells sampled per label during training. Balances rare types.

    Returns
    -------
    Tuple of (adata, scanvi_model) with predictions in obs.
    """
    n_labeled = (adata.obs[labels_key] != unlabeled_category).sum()
    n_unlabeled = (adata.obs[labels_key] == unlabeled_category).sum()
    n_types = adata.obs[labels_key].nunique() - 1  # exclude unlabeled
    print(f"Labeled: {n_labeled} cells, {n_types} types")
    print(f"Unlabeled: {n_unlabeled} cells")

    # Setup scANVI from scVI
    scvi.model.SCANVI.setup_anndata(
        adata,
        batch_key=scvi_model.adata_manager.get_state_registry("batch").original_key,
        labels_key=labels_key,
        unlabeled_category=unlabeled_category,
    )

    scanvi_model = scvi.model.SCANVI.from_scvi_model(
        scvi_model,
        unlabeled_category=unlabeled_category,
        adata=adata,
    )

    # Train (typically needs fewer epochs than scVI since it starts from pre-trained weights)
    scanvi_model.train(
        max_epochs=max_epochs,
        n_samples_per_label=n_samples_per_label,
    )

    # Predict labels for all cells
    adata.obs["scanvi_prediction"] = scanvi_model.predict(adata)

    # Soft predictions (probability per label)
    soft_preds = scanvi_model.predict(adata, soft=True)
    adata.obs["scanvi_confidence"] = soft_preds.max(axis=1).values

    # Store latent representation
    adata.obsm["X_scANVI"] = scanvi_model.get_latent_representation()

    # Summary
    print(f"\nPrediction summary:")
    print(adata.obs["scanvi_prediction"].value_counts())
    print(f"\nMean confidence: {adata.obs['scanvi_confidence'].mean():.3f}")
    print(f"Low confidence (<0.5): {(adata.obs['scanvi_confidence'] < 0.5).sum()} cells")

    # Accuracy on labeled cells
    labeled_mask = adata.obs[labels_key] != unlabeled_category
    if labeled_mask.sum() > 0:
        accuracy = (adata.obs.loc[labeled_mask, "scanvi_prediction"] ==
                    adata.obs.loc[labeled_mask, labels_key]).mean()
        print(f"Accuracy on labeled cells: {accuracy:.3f}")

    return adata, scanvi_model

# Usage
# First, mark some cells as unlabeled
adata.obs["cell_type_partial"] = adata.obs["cell_type"].copy()
mask = np.random.choice([True, False], size=len(adata), p=[0.7, 0.3])
adata.obs.loc[mask, "cell_type_partial"] = "Unknown"

adata, scanvi_model = scanvi_label_transfer(
    adata, model, labels_key="cell_type_partial"
)
```

**Expected output**: Every cell receives a predicted label and confidence score. Accuracy on held-out labeled cells should be >0.85 for well-separated types. Low-confidence cells may represent transitional states or novel types not in the reference.

---

## 3. totalVI: Joint RNA + Protein (CITE-seq/ADT) Modeling

Jointly model RNA and surface protein data from CITE-seq experiments.

```python
import scvi
import scanpy as sc

def totalvi_cite_seq(adata, batch_key: str = "batch",
                     protein_obsm_key: str = "protein_expression",
                     n_latent: int = 20, max_epochs: int = 300):
    """Train totalVI for joint RNA + protein modeling.

    Parameters
    ----------
    adata : AnnData
        RNA counts in .X or .layers['counts'].
        Protein counts in .obsm[protein_obsm_key] as DataFrame or ndarray.
    batch_key : str
        Batch column in obs.
    protein_obsm_key : str
        Key in adata.obsm with protein expression matrix.
    n_latent : int
        Latent space dimensionality.
    max_epochs : int
        Maximum training epochs.

    Returns
    -------
    Tuple of (adata, model) with denoised expression and latent space.
    """
    # Verify protein data exists
    assert protein_obsm_key in adata.obsm, f"Protein data not found in adata.obsm['{protein_obsm_key}']"
    n_proteins = adata.obsm[protein_obsm_key].shape[1]
    print(f"RNA features: {adata.n_vars}, Protein features: {n_proteins}")

    # Setup
    scvi.model.TOTALVI.setup_anndata(
        adata,
        batch_key=batch_key,
        protein_expression_obsm_key=protein_obsm_key,
        layer="counts" if "counts" in adata.layers else None,
    )

    # Train
    model = scvi.model.TOTALVI(
        adata,
        n_latent=n_latent,
        latent_distribution="normal",
    )
    model.train(max_epochs=max_epochs, early_stopping=True, early_stopping_patience=15)

    # Extract outputs
    adata.obsm["X_totalVI"] = model.get_latent_representation()

    # Denoised expression (normalized across batches)
    rna_denoised, protein_denoised = model.get_normalized_expression(
        adata, n_samples=25, return_mean=True,
    )
    adata.obsm["denoised_protein"] = protein_denoised.values

    # Protein foreground probability (signal vs background)
    protein_fg = model.get_protein_foreground_probability(adata)
    adata.obsm["protein_foreground_prob"] = protein_fg.values

    # Build UMAP from joint latent space
    sc.pp.neighbors(adata, use_rep="X_totalVI", n_neighbors=15)
    sc.tl.umap(adata)
    sc.tl.leiden(adata, resolution=0.8, key_added="leiden_totalVI")

    print(f"Training: {len(model.history['elbo_train'])} epochs")
    print(f"Latent shape: {adata.obsm['X_totalVI'].shape}")
    print(f"Clusters: {adata.obs['leiden_totalVI'].nunique()}")

    return adata, model

# Usage
adata, totalvi_model = totalvi_cite_seq(adata, batch_key="batch")
```

**Expected output**: Joint latent space capturing both RNA and protein information. Denoised protein expression removes background noise. Foreground probability >0.5 indicates true protein signal.

---

## 4. PeakVI: scATAC-seq Peak Analysis

Model chromatin accessibility from scATAC-seq peak matrices.

```python
import scvi
import scanpy as sc

def peakvi_atacseq(adata, batch_key: str = "batch", n_latent: int = 20,
                   max_epochs: int = 300):
    """Train PeakVI for scATAC-seq latent representation.

    Parameters
    ----------
    adata : AnnData
        Binary peak-by-cell matrix from scATAC-seq (e.g., ArchR, SnapATAC, CellRanger ATAC).
        .X should contain binarized peak counts (0/1).
    batch_key : str
        Batch column in obs.
    n_latent : int
        Latent space dimensionality.
    max_epochs : int
        Maximum training epochs.

    Returns
    -------
    Tuple of (adata, model).
    """
    print(f"Peaks: {adata.n_vars}, Cells: {adata.n_obs}")

    # Filter peaks: present in at least 5% of cells
    import numpy as np
    if hasattr(adata.X, "toarray"):
        peak_freq = np.array((adata.X > 0).mean(axis=0)).flatten()
    else:
        peak_freq = (adata.X > 0).mean(axis=0)
    adata = adata[:, peak_freq > 0.05].copy()
    print(f"Peaks after filtering (>5% cells): {adata.n_vars}")

    # Setup
    scvi.model.PEAKVI.setup_anndata(
        adata,
        batch_key=batch_key,
    )

    # Train
    model = scvi.model.PEAKVI(
        adata,
        n_latent=n_latent,
    )
    model.train(max_epochs=max_epochs, early_stopping=True)

    # Latent representation
    adata.obsm["X_PeakVI"] = model.get_latent_representation()

    # Accessibility probabilities (denoised)
    adata.obsm["accessibility_prob"] = model.get_accessibility_estimates()

    # Downstream
    sc.pp.neighbors(adata, use_rep="X_PeakVI", n_neighbors=15)
    sc.tl.umap(adata)
    sc.tl.leiden(adata, resolution=0.8, key_added="leiden_peakvi")

    print(f"Latent shape: {adata.obsm['X_PeakVI'].shape}")
    print(f"Clusters: {adata.obs['leiden_peakvi'].nunique()}")

    return adata, model

# Usage
adata_atac, peakvi_model = peakvi_atacseq(adata_atac, batch_key="batch")
```

**Expected output**: Latent representation for ATAC-seq data. Accessibility probabilities provide denoised peak accessibility per cell. Useful for identifying cell-type-specific regulatory elements.

---

## 5. MultiVI: Joint RNA + ATAC Multiome

Jointly model RNA and ATAC data, including datasets where only one modality is measured.

```python
import scvi
import scanpy as sc
import numpy as np

def multivi_multiome(adata, batch_key: str = "batch", n_latent: int = 20,
                     max_epochs: int = 300):
    """Train MultiVI for joint RNA + ATAC analysis.

    Parameters
    ----------
    adata : AnnData
        Combined AnnData with RNA features and ATAC peaks.
        Cells with only RNA should have 0s in ATAC columns and vice versa.
        Use scvi.data.organize_multiome_anndatas() to prepare.
    batch_key : str
        Batch column in obs.
    n_latent : int
        Latent space dimensionality.
    max_epochs : int
        Maximum training epochs.

    Returns
    -------
    Tuple of (adata, model).

    Notes
    -----
    MultiVI handles three data types:
    1. Paired RNA + ATAC (e.g., 10x Multiome)
    2. RNA-only cells
    3. ATAC-only cells
    """
    # Setup
    scvi.model.MULTIVI.setup_anndata(
        adata,
        batch_key=batch_key,
    )

    # Train
    model = scvi.model.MULTIVI(
        adata,
        n_latent=n_latent,
        n_genes=adata.uns.get("n_genes", adata.n_vars),
        n_regions=adata.uns.get("n_regions", 0),
    )
    model.train(max_epochs=max_epochs, early_stopping=True)

    # Joint latent representation
    adata.obsm["X_MultiVI"] = model.get_latent_representation()

    # Impute missing modality
    # For RNA-only cells, impute ATAC accessibility:
    # imputed_atac = model.get_accessibility_estimates()
    # For ATAC-only cells, impute RNA expression:
    # imputed_rna = model.get_normalized_expression()

    sc.pp.neighbors(adata, use_rep="X_MultiVI", n_neighbors=15)
    sc.tl.umap(adata)
    sc.tl.leiden(adata, resolution=0.8, key_added="leiden_multivi")

    print(f"Latent shape: {adata.obsm['X_MultiVI'].shape}")
    print(f"Clusters: {adata.obs['leiden_multivi'].nunique()}")

    return adata, model

# Prepare multiome data
# adata_rna = sc.read_h5ad("rna_data.h5ad")
# adata_atac = sc.read_h5ad("atac_data.h5ad")
# adata = scvi.data.organize_multiome_anndatas(adata_rna, adata_atac)
# adata, model = multivi_multiome(adata)
```

**Expected output**: Joint latent space integrating RNA and ATAC modalities. Missing modalities can be imputed using the trained model. Enables cross-modality cell type identification.

---

## 6. DestVI: Spatial Transcriptomics Deconvolution

Deconvolve spatial transcriptomics spots using a single-cell reference.

```python
import scvi
import scanpy as sc

def destvi_spatial(adata_sc, adata_spatial, cell_type_key: str = "cell_type",
                   batch_key: str = None, n_latent: int = 15, max_epochs_sc: int = 300,
                   max_epochs_st: int = 2500):
    """DestVI spatial deconvolution using single-cell reference.

    Parameters
    ----------
    adata_sc : AnnData
        Single-cell reference with raw counts and cell type annotations.
    adata_spatial : AnnData
        Spatial transcriptomics data (e.g., Visium) with raw counts.
    cell_type_key : str
        Column in adata_sc.obs with cell type labels.
    batch_key : str or None
        Batch column in adata_sc.obs (if multi-sample reference).
    n_latent : int
        Latent space dimensionality.
    max_epochs_sc : int
        Training epochs for single-cell model (CondSCVI).
    max_epochs_st : int
        Training epochs for spatial model (DestVI).

    Returns
    -------
    Tuple of (adata_spatial, st_model) with deconvolution results.
    """
    # Step 1: Train conditional scVI on reference
    sc.pp.highly_variable_genes(
        adata_sc, n_top_genes=4000, flavor="seurat_v3", subset=True,
        layer="counts" if "counts" in adata_sc.layers else None,
    )

    scvi.model.CondSCVI.setup_anndata(
        adata_sc,
        layer="counts" if "counts" in adata_sc.layers else None,
        labels_key=cell_type_key,
    )
    sc_model = scvi.model.CondSCVI(adata_sc, n_latent=n_latent)
    sc_model.train(max_epochs=max_epochs_sc, early_stopping=True)
    print(f"CondSCVI training: {len(sc_model.history['elbo_train'])} epochs")

    # Step 2: Subset spatial data to reference genes
    shared_genes = list(set(adata_sc.var_names) & set(adata_spatial.var_names))
    adata_spatial_sub = adata_spatial[:, shared_genes].copy()
    print(f"Shared genes: {len(shared_genes)}")

    # Step 3: Train DestVI on spatial data
    scvi.model.DestVI.setup_anndata(
        adata_spatial_sub,
        layer="counts" if "counts" in adata_spatial_sub.layers else None,
    )
    st_model = scvi.model.DestVI.from_rna_model(
        adata_spatial_sub, sc_model
    )
    st_model.train(max_epochs=max_epochs_st)

    # Step 4: Get proportions per spot
    proportions = st_model.get_proportions()
    for ct in proportions.columns:
        adata_spatial.obs[f"prop_{ct}"] = proportions[ct].values

    print(f"\nDeconvolution complete:")
    print(f"Cell types deconvolved: {len(proportions.columns)}")
    print(f"Mean proportions per type:")
    print(proportions.mean().sort_values(ascending=False))

    return adata_spatial, st_model

# Usage
# adata_spatial, st_model = destvi_spatial(
#     adata_sc, adata_spatial, cell_type_key="cell_type"
# )
# sc.pl.spatial(adata_spatial, color="prop_T cells", spot_size=1.5)
```

**Expected output**: Per-spot cell type proportions. Visualize on spatial coordinates to see cell type distributions across the tissue. Proportions should sum to ~1 per spot.

---

## 7. veloVI: RNA Velocity with Uncertainty

Model RNA velocity with uncertainty quantification using variational inference.

```python
import scvi
import scanpy as sc
import scvelo as scv

def velovi_velocity(adata, n_latent: int = 10, max_epochs: int = 500):
    """Train veloVI for RNA velocity with uncertainty estimates.

    Parameters
    ----------
    adata : AnnData
        Must contain spliced (adata.layers['spliced']) and unspliced
        (adata.layers['unspliced']) count matrices from velocyto/STARsolo.
    n_latent : int
        Latent space dimensionality.
    max_epochs : int
        Maximum training epochs.

    Returns
    -------
    Tuple of (adata, model) with velocity and uncertainty.

    Notes
    -----
    veloVI provides per-gene uncertainty estimates for velocity, unlike
    deterministic scVelo which gives point estimates only.
    """
    # Preprocessing with scVelo
    scv.pp.filter_and_normalize(adata, min_shared_counts=20, n_top_genes=2000)
    scv.pp.moments(adata, n_pcs=30, n_neighbors=30)

    # Setup veloVI
    scvi.model.VELOVI.setup_anndata(
        adata,
        spliced_layer="Ms",    # smoothed spliced
        unspliced_layer="Mu",  # smoothed unspliced
    )

    # Train
    model = scvi.model.VELOVI(adata, n_latent=n_latent)
    model.train(max_epochs=max_epochs, early_stopping=True)

    # Get velocity and uncertainty
    latent_time = model.get_latent_time(adata)
    adata.obs["velovi_latent_time"] = latent_time
    adata.layers["velocity"] = model.get_velocity(adata)

    # Per-gene uncertainty (permutation score)
    velocity_samples = model.get_velocity(adata, n_samples=25, return_mean=False)
    import numpy as np
    adata.layers["velocity_uncertainty"] = np.std(velocity_samples, axis=0)

    # Velocity graph for streamlines
    scv.tl.velocity_graph(adata, vkey="velocity")

    print(f"Training: {len(model.history['elbo_train'])} epochs")
    print(f"Latent time range: [{latent_time.min():.3f}, {latent_time.max():.3f}]")

    # Visualize
    scv.pl.velocity_embedding_stream(adata, basis="umap", vkey="velocity",
                                      color="cell_type", save="velovi_stream.png")

    return adata, model

# Usage
# adata, velovi_model = velovi_velocity(adata)
```

**Expected output**: Velocity vectors and per-gene uncertainty. Latent time provides a pseudotemporal ordering. High-uncertainty genes should be treated cautiously in trajectory interpretation.

---

## 8. sysVI: Cross-Platform/Cross-Technology Integration

Integrate datasets generated with different technologies (e.g., 10x vs Smart-seq2, different species).

```python
import scvi
import scanpy as sc
import numpy as np

def sysvi_cross_platform(adata, system_key: str = "technology",
                          batch_key: str = "batch", n_latent: int = 30,
                          max_epochs: int = 300):
    """Train sysVI for cross-platform integration.

    Parameters
    ----------
    adata : AnnData
        Combined AnnData from multiple technologies with raw counts.
    system_key : str
        Column identifying the technology/system (e.g., '10x', 'Smart-seq2').
    batch_key : str
        Column identifying batches within each system.
    n_latent : int
        Latent space dimensionality.
    max_epochs : int
        Maximum training epochs.

    Returns
    -------
    Tuple of (adata, model).

    Notes
    -----
    sysVI models system-specific effects separately from biological variation,
    making it more appropriate than scVI for cross-technology integration where
    technical differences are systematic (e.g., full-length vs 3' counting).
    """
    systems = adata.obs[system_key].unique().tolist()
    for sys in systems:
        n = (adata.obs[system_key] == sys).sum()
        print(f"  {sys}: {n} cells")

    # HVG selection per system
    sc.pp.highly_variable_genes(
        adata, n_top_genes=4000, flavor="seurat_v3", subset=True,
        batch_key=system_key,
        layer="counts" if "counts" in adata.layers else None,
    )

    # Setup sysVI
    scvi.model.SYSVI.setup_anndata(
        adata,
        layer="counts" if "counts" in adata.layers else None,
        batch_key=batch_key,
        categorical_covariate_keys=[system_key],
    )

    # Train
    model = scvi.model.SYSVI(adata, n_latent=n_latent)
    model.train(max_epochs=max_epochs, early_stopping=True)

    # Latent representation
    adata.obsm["X_sysVI"] = model.get_latent_representation()

    sc.pp.neighbors(adata, use_rep="X_sysVI", n_neighbors=15)
    sc.tl.umap(adata)
    sc.tl.leiden(adata, resolution=0.8, key_added="leiden_sysVI")

    print(f"Clusters: {adata.obs['leiden_sysVI'].nunique()}")

    return adata, model

# Usage
# adata, sysvi_model = sysvi_cross_platform(adata, system_key="technology")
```

**Expected output**: Integrated latent space where cells cluster by biology rather than technology. Compare UMAP colored by system_key (should be mixed) and cell_type (should be separated).

---

## 9. scArches: Transfer Learning onto Pre-Trained Reference

Map new query data onto a pre-trained reference model without retraining.

```python
import scvi
import scanpy as sc

def scarches_query_to_reference(adata_ref, adata_query, ref_model_path: str,
                                 batch_key: str = "batch", max_epochs: int = 100):
    """Map query data onto a pre-trained scVI reference using scArches.

    Parameters
    ----------
    adata_ref : AnnData
        Reference AnnData used to train the original model.
    adata_query : AnnData
        New query AnnData to map onto the reference.
    ref_model_path : str
        Path to saved reference scVI model directory.
    batch_key : str
        Batch column in obs (query batch must be a new value).
    max_epochs : int
        Fine-tuning epochs for query mapping.

    Returns
    -------
    Tuple of (adata_combined, query_model).

    Notes
    -----
    scArches (Lotfollahi et al. 2022) freezes most model weights and only
    updates batch-specific parameters, enabling efficient mapping of new
    data without full retraining.
    """
    # Load reference model
    ref_model = scvi.model.SCVI.load(ref_model_path, adata=adata_ref)

    # Ensure query has the same genes as reference
    shared_genes = list(set(adata_ref.var_names) & set(adata_query.var_names))
    print(f"Shared genes: {len(shared_genes)} / {adata_ref.n_vars} reference genes")

    adata_query_sub = adata_query[:, shared_genes].copy()

    # Prepare query data for scArches
    scvi.model.SCVI.prepare_query_anndata(adata_query_sub, ref_model)

    # Create query model (inherits reference weights)
    query_model = scvi.model.SCVI.load_query_data(adata_query_sub, ref_model)

    # Fine-tune on query data
    query_model.train(
        max_epochs=max_epochs,
        plan_kwargs={"weight_decay": 0.0},
    )

    # Get latent for both reference and query
    adata_ref.obsm["X_scArches"] = ref_model.get_latent_representation(adata_ref)
    adata_query_sub.obsm["X_scArches"] = query_model.get_latent_representation(adata_query_sub)

    # Combine for visualization
    adata_combined = adata_ref.concatenate(adata_query_sub, batch_key="dataset",
                                           batch_categories=["reference", "query"])
    sc.pp.neighbors(adata_combined, use_rep="X_scArches", n_neighbors=15)
    sc.tl.umap(adata_combined)

    print(f"Combined: {adata_combined.n_obs} cells (ref: {adata_ref.n_obs}, query: {adata_query_sub.n_obs})")

    return adata_combined, query_model

# Usage
# adata_combined, query_model = scarches_query_to_reference(
#     adata_ref, adata_query, "scvi_model/"
# )
# sc.pl.umap(adata_combined, color=["dataset", "cell_type"])
```

**Expected output**: Query cells mapped onto the reference latent space. Query cells should co-localize with matching reference cell types in UMAP. Enables atlas-level annotation of new datasets.

---

## 10. Differential Expression with scVI

Bayesian differential expression using trained scVI posterior.

```python
import scvi
import pandas as pd

def scvi_differential_expression(model, adata, groupby: str, group1: str, group2: str,
                                  delta: float = 0.25, batch_correction: bool = True,
                                  fdr_threshold: float = 0.05, lfc_threshold: float = 0.5):
    """Bayesian DE testing between two groups using scVI model.

    Parameters
    ----------
    model : scvi.model.SCVI
        Trained scVI model.
    adata : AnnData
        AnnData registered with the model.
    groupby : str
        Column in adata.obs defining groups.
    group1, group2 : str
        Groups to compare (group1 is numerator in fold change).
    delta : float
        Log fold change threshold for Bayesian hypothesis test.
        DE is called if P(|LFC| > delta) is high.
    batch_correction : bool
        Correct for batch effects in DE test.
    fdr_threshold : float
        FDR cutoff for significance.
    lfc_threshold : float
        Minimum absolute LFC for reporting.

    Returns
    -------
    pd.DataFrame with DE results sorted by LFC.
    """
    de_results = model.differential_expression(
        adata,
        groupby=groupby,
        group1=group1,
        group2=group2,
        delta=delta,
        batch_correction=batch_correction,
    )

    # Filter significant genes
    de_sig = de_results[
        (de_results["is_de_fdr_0.05"] == True) &
        (de_results["lfc_mean"].abs() > lfc_threshold)
    ].sort_values("lfc_mean", ascending=False)

    n_up = (de_sig["lfc_mean"] > 0).sum()
    n_down = (de_sig["lfc_mean"] < 0).sum()

    print(f"DE: {group1} vs {group2}")
    print(f"  Total significant (FDR<{fdr_threshold}, |LFC|>{lfc_threshold}): {len(de_sig)}")
    print(f"  Upregulated in {group1}: {n_up}")
    print(f"  Downregulated in {group1}: {n_down}")

    print(f"\nTop 10 upregulated:")
    print(de_sig.head(10)[["lfc_mean", "lfc_std", "bayes_factor", "non_zeros_proportion1", "non_zeros_proportion2"]])

    print(f"\nTop 10 downregulated:")
    print(de_sig.tail(10)[["lfc_mean", "lfc_std", "bayes_factor", "non_zeros_proportion1", "non_zeros_proportion2"]])

    return de_sig

# Usage
de_sig = scvi_differential_expression(
    model, adata, groupby="condition",
    group1="treatment", group2="control",
    delta=0.25, lfc_threshold=0.5,
)
```

**Expected output**: DataFrame with per-gene log fold changes, standard deviations, Bayes factors, and DE calls. scVI DE accounts for batch effects and dropout, providing more calibrated p-values than standard tests for single-cell data.

---

## 11. HVG Selection Per Batch

Select highly variable genes that are consistently variable across batches.

```python
import scanpy as sc
import pandas as pd
import numpy as np

def select_hvgs_per_batch(adata, batch_key: str = "batch", n_top_genes: int = 4000,
                          flavor: str = "seurat_v3"):
    """Select HVGs that are variable across batches, not just within one.

    Parameters
    ----------
    adata : AnnData
        Must contain raw counts for flavor='seurat_v3'.
    batch_key : str
        Column identifying batches.
    n_top_genes : int
        Target number of HVGs. 4000 recommended for multi-batch scVI input.
    flavor : str
        HVG selection method: 'seurat_v3' (variance-stabilizing, recommended),
        'seurat' (log-mean-variance), 'cell_ranger'.

    Returns
    -------
    adata with .var['highly_variable'] updated.
    """
    count_layer = "counts" if "counts" in adata.layers else None
    batches = adata.obs[batch_key].unique()
    print(f"Selecting {n_top_genes} HVGs across {len(batches)} batches (flavor={flavor})")

    sc.pp.highly_variable_genes(
        adata,
        n_top_genes=n_top_genes,
        flavor=flavor,
        batch_key=batch_key,
        layer=count_layer,
        subset=False,
    )

    n_hvg = adata.var["highly_variable"].sum()
    n_batches_variable = adata.var["highly_variable_nbatches"]

    print(f"HVGs selected: {n_hvg}")
    print(f"HVGs variable in all batches: {(n_batches_variable == len(batches)).sum()}")
    print(f"HVGs variable in >50% batches: {(n_batches_variable > len(batches)/2).sum()}")
    print(f"Mean highly_variable_rank: {adata.var.loc[adata.var['highly_variable'], 'highly_variable_rank'].mean():.1f}")

    return adata

# Usage
adata = select_hvgs_per_batch(adata, batch_key="batch", n_top_genes=4000)
adata_hvg = adata[:, adata.var.highly_variable].copy()
```

**Expected output**: HVG selection that avoids batch-specific artifacts. Genes variable in multiple batches are preferred. The `highly_variable_nbatches` column shows how many batches each gene was selected in.

---

## 12. Data Preparation: Ensuring Raw Integer Counts

Validate and prepare data for scvi-tools models which require raw counts.

```python
import scanpy as sc
import numpy as np
from scipy.sparse import issparse

def prepare_for_scvi(adata, verbose: bool = True):
    """Validate and prepare AnnData for scvi-tools input.

    Parameters
    ----------
    adata : AnnData
        AnnData to prepare. Will store raw counts in layers['counts'] if not present.
    verbose : bool
        Print diagnostic information.

    Returns
    -------
    AnnData ready for scvi.model.SCVI.setup_anndata().

    Notes
    -----
    scvi-tools models expect:
    - Raw integer counts (not normalized, not log-transformed)
    - No NaN or Inf values
    - Genes as columns, cells as rows
    """
    if verbose:
        print(f"Shape: {adata.n_obs} cells x {adata.n_vars} genes")

    # Check X content
    if issparse(adata.X):
        sample = adata.X[:min(100, adata.n_obs)].toarray()
    else:
        sample = adata.X[:min(100, adata.n_obs)]

    is_integer = np.allclose(sample, np.round(sample), equal_nan=True)
    is_nonneg = np.all(sample >= 0)
    x_max = np.max(sample)
    has_nan = np.any(np.isnan(sample))

    if verbose:
        print(f"X: integers={is_integer}, non-negative={is_nonneg}, max={x_max:.2f}, NaN={has_nan}")

    # Strategy 1: X has raw counts
    if is_integer and is_nonneg and x_max > 10:
        if "counts" not in adata.layers:
            adata.layers["counts"] = adata.X.copy()
            if verbose:
                print("Stored X as layers['counts']")
        return adata

    # Strategy 2: counts in a layer
    if "counts" in adata.layers:
        if issparse(adata.layers["counts"]):
            ct_sample = adata.layers["counts"][:100].toarray()
        else:
            ct_sample = adata.layers["counts"][:100]
        ct_integer = np.allclose(ct_sample, np.round(ct_sample), equal_nan=True)
        if ct_integer:
            if verbose:
                print("Using existing layers['counts'] (verified integer)")
            return adata

    # Strategy 3: X is log-normalized, try to reverse
    if not is_integer and x_max < 20:
        if verbose:
            print("X appears log-normalized. Attempting to reverse log1p...")
        reversed_x = np.expm1(sample)
        reversed_rounded = np.round(reversed_x)
        if np.allclose(reversed_x, reversed_rounded, atol=0.5):
            if issparse(adata.X):
                from scipy.sparse import csr_matrix
                adata.layers["counts"] = csr_matrix(np.round(np.expm1(adata.X.toarray())))
            else:
                adata.layers["counts"] = np.round(np.expm1(adata.X))
            if verbose:
                print("Reversed log1p and stored in layers['counts']")
            return adata

    # Strategy 4: raw attribute
    if adata.raw is not None:
        if verbose:
            print("Checking adata.raw for counts...")
        if issparse(adata.raw.X):
            raw_sample = adata.raw.X[:100].toarray()
        else:
            raw_sample = adata.raw.X[:100]
        if np.allclose(raw_sample, np.round(raw_sample), equal_nan=True) and np.max(raw_sample) > 10:
            adata_new = adata.raw.to_adata()
            adata_new.obs = adata.obs
            adata_new.obsm = adata.obsm
            adata_new.layers["counts"] = adata_new.X.copy()
            if verbose:
                print("Used adata.raw as count source")
            return adata_new

    raise ValueError(
        "Could not find raw integer counts. Provide counts in:\n"
        "  - adata.X (raw counts)\n"
        "  - adata.layers['counts']\n"
        "  - adata.raw"
    )

# Usage
adata = prepare_for_scvi(adata)
# Now safe to call:
# scvi.model.SCVI.setup_anndata(adata, layer="counts", batch_key="batch")
```

**Expected output**: AnnData validated with raw integer counts in `layers['counts']`. Prints diagnostic info about data format. Raises clear error if counts cannot be found or reconstructed.

---

## 13. Training Diagnostics: Loss Curves and Reconstruction Quality

Monitor and diagnose scvi-tools model training.

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_training_diagnostics(model, save_path: str = "training_diagnostics.png"):
    """Plot training diagnostics for scvi-tools models.

    Parameters
    ----------
    model : scvi.model.BaseModelClass
        Any trained scvi-tools model (SCVI, SCANVI, TOTALVI, etc.).
    save_path : str
        Path to save diagnostic plot.

    Returns
    -------
    dict with training summary statistics.
    """
    history = model.history
    n_epochs = len(history["elbo_train"])

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Panel 1: ELBO loss curves
    axes[0].plot(history["elbo_train"].index, history["elbo_train"].values, label="Train", alpha=0.8)
    if "elbo_validation" in history:
        axes[0].plot(history["elbo_validation"].index, history["elbo_validation"].values,
                     label="Validation", alpha=0.8)
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("ELBO")
    axes[0].set_title("Evidence Lower Bound (ELBO)")
    axes[0].legend()

    # Panel 2: Reconstruction loss
    if "reconstruction_loss_train" in history:
        axes[1].plot(history["reconstruction_loss_train"].index,
                     history["reconstruction_loss_train"].values, label="Train", alpha=0.8)
        if "reconstruction_loss_validation" in history:
            axes[1].plot(history["reconstruction_loss_validation"].index,
                         history["reconstruction_loss_validation"].values,
                         label="Validation", alpha=0.8)
        axes[1].set_xlabel("Epoch")
        axes[1].set_ylabel("Reconstruction Loss")
        axes[1].set_title("Reconstruction Loss")
        axes[1].legend()
    else:
        axes[1].text(0.5, 0.5, "Reconstruction loss\nnot recorded", ha="center", va="center",
                     transform=axes[1].transAxes)
        axes[1].set_title("Reconstruction Loss")

    # Panel 3: KL divergence
    if "kl_local_train" in history:
        axes[2].plot(history["kl_local_train"].index,
                     history["kl_local_train"].values, label="KL Local (Train)", alpha=0.8)
        if "kl_local_validation" in history:
            axes[2].plot(history["kl_local_validation"].index,
                         history["kl_local_validation"].values,
                         label="KL Local (Val)", alpha=0.8)
        axes[2].set_xlabel("Epoch")
        axes[2].set_ylabel("KL Divergence")
        axes[2].set_title("KL Divergence")
        axes[2].legend()
    else:
        axes[2].text(0.5, 0.5, "KL divergence\nnot recorded", ha="center", va="center",
                     transform=axes[2].transAxes)
        axes[2].set_title("KL Divergence")

    plt.suptitle(f"Training Diagnostics ({n_epochs} epochs)", fontsize=14)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()

    # Summary statistics
    final_elbo = history["elbo_train"].iloc[-1].values[0]
    best_elbo = history["elbo_train"].min().values[0]
    stats = {
        "n_epochs": n_epochs,
        "final_train_elbo": final_elbo,
        "best_train_elbo": best_elbo,
    }

    if "elbo_validation" in history:
        stats["final_val_elbo"] = history["elbo_validation"].iloc[-1].values[0]
        val_train_gap = stats["final_val_elbo"] - final_elbo
        stats["val_train_gap"] = val_train_gap
        if abs(val_train_gap) > abs(final_elbo) * 0.1:
            print("WARNING: Large train-validation gap suggests overfitting")

    # Check for convergence
    last_10 = history["elbo_train"].iloc[-10:].values.flatten()
    elbo_std = np.std(last_10)
    stats["converged"] = elbo_std < abs(np.mean(last_10)) * 0.01
    if not stats["converged"]:
        print("WARNING: ELBO may not have converged. Consider increasing max_epochs.")

    print(f"\nTraining Summary:")
    for k, v in stats.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")
        else:
            print(f"  {k}: {v}")

    print(f"\nSaved: {save_path}")
    return stats

# Usage
stats = plot_training_diagnostics(model)
```

**Expected output**: Three-panel figure showing ELBO convergence, reconstruction loss, and KL divergence over training. ELBO should decrease monotonically and plateau. Large train-validation gaps indicate overfitting. Increasing KL divergence at end of training suggests posterior collapse.
