# TCR/BCR Repertoire Analysis Recipes

Python code templates for immune repertoire analysis. Covers scirpy, Immcantation/Change-O, MiXCR, VDJtools, diversity indices, clonotype overlap, V(D)J gene usage, CDR3 sequence logos, convergent clonotype detection, and paired VDJ + transcriptome integration.

Cross-skill routing: use `immune-repertoire-analysis` for conceptual guidance, `single-cell-analysis` for scRNA-seq integration, `immunotherapy-response-predictor` for clinical response prediction.

---

## 1. scirpy: Read 10x VDJ, Chain QC, Clonotype Definition

Load and process 10x Chromium VDJ data using scirpy.

```python
import scirpy as ir
import scanpy as sc
import warnings
warnings.filterwarnings("ignore")

def load_10x_vdj(vdj_path, gex_path=None):
    """Load 10x VDJ data and optionally integrate with gene expression.

    Parameters:
        vdj_path: path to filtered_contig_annotations.csv (10x VDJ output)
        gex_path: path to GEX AnnData (.h5ad) for paired analysis (optional)
    Returns:
        AnnData with VDJ information in obs/obsm
    """
    # Load VDJ
    adata_vdj = ir.io.read_10x_vdj(vdj_path)
    print(f"VDJ cells: {adata_vdj.n_obs}")

    if gex_path:
        adata_gex = sc.read_h5ad(gex_path)
        # Merge VDJ into GEX
        ir.pp.merge_with_ir(adata_gex, adata_vdj)
        adata = adata_gex
        print(f"GEX cells: {adata_gex.n_obs}")
        print(f"Cells with VDJ: {adata.obs['has_ir'].sum() if 'has_ir' in adata.obs else 'N/A'}")
    else:
        adata = adata_vdj

    return adata


def chain_qc(adata):
    """Run chain quality control and categorization.

    Classifies cells by receptor type and chain pairing status.

    Parameters:
        adata: AnnData with VDJ information from scirpy
    Returns:
        adata with chain QC annotations
    """
    ir.tl.chain_qc(adata)

    print("Chain QC summary:")
    if "chain_pairing" in adata.obs.columns:
        print(adata.obs["chain_pairing"].value_counts())
    if "receptor_type" in adata.obs.columns:
        print(f"\nReceptor types:")
        print(adata.obs["receptor_type"].value_counts())
    if "receptor_subtype" in adata.obs.columns:
        print(f"\nReceptor subtypes:")
        print(adata.obs["receptor_subtype"].value_counts())

    # Plot chain pairing
    ir.pl.group_abundance(adata, groupby="chain_pairing", target_col="receptor_type")

    return adata


def define_clonotypes_scirpy(adata, metric="identity", sequence="aa",
                              receptor_arms="all", dual_ir="primary_only"):
    """Define clonotypes using scirpy's flexible framework.

    Parameters:
        adata: AnnData with VDJ information
        metric: 'identity' (exact match) or 'alignment' (sequence similarity)
        sequence: 'aa' (amino acid) or 'nt' (nucleotide)
        receptor_arms: 'all' (both chains must match), 'any' (either chain)
        dual_ir: 'primary_only' (use only primary chain), 'any' (consider all chains)
    Returns:
        adata with clonotype annotations
    """
    ir.pp.ir_dist(adata, metric=metric, sequence=sequence)
    ir.tl.define_clonotypes(adata, receptor_arms=receptor_arms, dual_ir=dual_ir)
    ir.tl.define_clonotype_clusters(adata, receptor_arms=receptor_arms, dual_ir=dual_ir)

    n_clonotypes = adata.obs["clone_id"].nunique()
    n_clusters = adata.obs["cc_aa_identity"].nunique() if "cc_aa_identity" in adata.obs else "N/A"
    print(f"Clonotypes defined: {n_clonotypes}")
    print(f"Clonotype clusters: {n_clusters}")

    return adata

# Usage
adata = load_10x_vdj("filtered_contig_annotations.csv", gex_path="gex.h5ad")
adata = chain_qc(adata)
adata = define_clonotypes_scirpy(adata, metric="identity", sequence="aa")
```

**Key parameters:**
- `metric="identity"`: exact CDR3 match. Use `"alignment"` for similarity-based clustering (slower).
- `receptor_arms="all"`: both alpha+beta (or heavy+light) must match. Stricter clonotype definition.
- `dual_ir="primary_only"`: for cells with dual receptors, use only primary. Avoids ambiguity.

**Expected output:** AnnData with `clone_id`, `chain_pairing`, `receptor_type` in obs.

---

## 2. Scirpy Clonal Expansion Categorization

Categorize clonotypes by expansion status using scirpy.

```python
import scirpy as ir
import matplotlib.pyplot as plt

def clonal_expansion_scirpy(adata, clone_key="clone_id",
                             categories=None, groupby=None):
    """Categorize and visualize clonal expansion using scirpy.

    Parameters:
        adata: AnnData with clonotype definitions
        clone_key: obs column with clonotype identifiers
        categories: dict of {category_name: (min_count, max_count)} or None for defaults
        groupby: obs column to stratify expansion analysis (e.g., 'sample', 'condition')
    Returns:
        adata with expansion categories
    """
    if categories is None:
        # Default 10x/scirpy expansion categories
        categories = {
            "Singleton": (1, 1),
            "Small (2-5)": (2, 5),
            "Medium (6-20)": (6, 20),
            "Large (21-100)": (21, 100),
            "Hyperexpanded (>100)": (101, None),
        }

    # Compute clonal expansion
    ir.tl.clonal_expansion(adata, clonotype_key=clone_key)

    print("Clonal expansion summary:")
    if "clonal_expansion" in adata.obs.columns:
        print(adata.obs["clonal_expansion"].value_counts())

    # Visualization
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Expansion pie chart
    if "clonal_expansion" in adata.obs.columns:
        counts = adata.obs["clonal_expansion"].value_counts()
        axes[0].pie(counts.values, labels=counts.index, autopct="%1.1f%%")
        axes[0].set_title("Clonal Expansion Distribution")

    # Group comparison
    if groupby:
        ir.pl.group_abundance(
            adata, groupby="clonal_expansion",
            target_col=groupby, ax=axes[1]
        )
    else:
        ir.pl.clonal_expansion(adata, clonotype_key=clone_key, ax=axes[1])

    plt.tight_layout()
    plt.savefig("clonal_expansion_scirpy.png", dpi=150, bbox_inches="tight")
    plt.show()

    return adata

# Usage
adata = clonal_expansion_scirpy(adata, groupby="condition")
```

**Key parameters:**
- Default categories follow 10x Genomics convention: singleton, small, medium, large, hyperexpanded.
- `groupby`: compare expansion patterns across conditions (e.g., tumor vs normal, pre vs post treatment).

**Expected output:** `adata.obs['clonal_expansion']` with expansion category labels; visualization of expansion distribution.

---

## 3. Immcantation/Change-O: Clonal Assignment

Process AIRR-formatted data with Immcantation framework for BCR clonal lineage analysis.

```python
import subprocess
import pandas as pd

def run_changeo_clonal_assignment(airr_tsv, germline_db, threshold=0.15,
                                  method="chen2010"):
    """Run Change-O DefineClones for clonal assignment from AIRR data.

    Parameters:
        airr_tsv: path to AIRR-formatted TSV (from IgBLAST or IMGT/HighV-QUEST)
        germline_db: path to germline V gene database (FASTA)
        threshold: distance threshold for clonal grouping (0.15 = 85% similarity)
        method: clustering method ('chen2010' or 'novj')
    Returns:
        DataFrame with clonal assignments
    """
    output = airr_tsv.replace(".tsv", "_clones.tsv")

    # Step 1: Assign germline sequences
    subprocess.run([
        "CreateGermlines.py",
        "-d", airr_tsv,
        "-r", germline_db,
        "-g", "full",
        "--format", "airr",
    ], check=True)

    germline_file = airr_tsv.replace(".tsv", "_germ-pass.tsv")

    # Step 2: Define clones
    subprocess.run([
        "DefineClones.py",
        "-d", germline_file,
        "--act", "set",
        "--model", "ham",
        "--norm", "len",
        "--dist", str(threshold),
        "--format", "airr",
    ], check=True)

    clone_file = germline_file.replace(".tsv", "_clone-pass.tsv")
    df = pd.read_csv(clone_file, sep="\t")

    print(f"Clonal assignment complete:")
    print(f"  Sequences: {len(df)}")
    print(f"  Clones: {df['clone_id'].nunique()}")
    print(f"  Largest clone: {df['clone_id'].value_counts().max()} sequences")

    return df

# Usage
clones_df = run_changeo_clonal_assignment(
    "airr_data.tsv", "imgt_germlines/human/vdj/",
    threshold=0.15
)
```

**Key parameters:**
- `threshold=0.15`: Hamming distance threshold for clonal grouping. Lower = stricter (fewer clones).
- `method="ham"`: Hamming distance model. Alternatives: `"aa"` for amino acid distance.
- `norm="len"`: normalize distance by sequence length.

**Expected output:** AIRR TSV with `clone_id` column assigning sequences to clonal groups.

---

## 4. Somatic Hypermutation Analysis (SHM)

Quantify somatic hypermutation rates in BCR sequences.

```python
import pandas as pd
import numpy as np

def calculate_shm_rates(airr_df, germline_col="germline_alignment",
                         sequence_col="sequence_alignment"):
    """Calculate somatic hypermutation rates from AIRR data.

    Parameters:
        airr_df: DataFrame with germline and observed sequences (from Change-O)
        germline_col: column with germline (reference) alignment
        sequence_col: column with observed sequence alignment
    Returns:
        DataFrame with per-sequence mutation rates and summary
    """
    results = []
    for _, row in airr_df.iterrows():
        germline = str(row.get(germline_col, ""))
        observed = str(row.get(sequence_col, ""))

        if not germline or not observed or len(germline) != len(observed):
            continue

        total = 0
        mutations = 0
        for g, o in zip(germline, observed):
            if g in "ACGT" and o in "ACGT":
                total += 1
                if g != o:
                    mutations += 1

        if total == 0:
            continue

        mut_rate = mutations / total
        results.append({
            "sequence_id": row.get("sequence_id", ""),
            "clone_id": row.get("clone_id", ""),
            "v_gene": row.get("v_call", "").split("*")[0],
            "isotype": row.get("c_call", ""),
            "total_bases": total,
            "mutations": mutations,
            "mutation_rate": mut_rate,
            "mutations_per_100bp": mut_rate * 100,
        })

    df = pd.DataFrame(results)

    print(f"SHM analysis: {len(df)} sequences")
    print(f"  Mean mutation rate: {df['mutation_rate'].mean():.4f} ({df['mutations_per_100bp'].mean():.2f} per 100bp)")
    print(f"  Median mutations: {df['mutations'].median():.0f}")

    # Per-isotype SHM rates
    if "isotype" in df.columns:
        iso_rates = df.groupby("isotype")["mutation_rate"].agg(["mean", "median", "count"])
        print(f"\nPer-isotype SHM rates:")
        print(iso_rates)

    return df

# Usage
shm_df = calculate_shm_rates(clones_df)
```

**Key parameters:**
- Expected SHM rates: IgM ~0-2%, IgG ~3-8%, IgA ~3-6%.
- Higher SHM in antigen-experienced B cells (germinal center output).
- SHM focused in CDR regions (especially CDR1 and CDR2, and framework regions).

**Expected output:** DataFrame with per-sequence mutation counts, rates, and isotype-stratified summary.

---

## 5. MiXCR: Align, Assemble, Export Workflow

Complete MiXCR pipeline from raw FASTQ to clonotype tables.

```bash
#!/bin/bash
# MiXCR pipeline: align -> assemble -> export

SAMPLE="sample1"
R1="${SAMPLE}_R1.fastq.gz"
R2="${SAMPLE}_R2.fastq.gz"
SPECIES="hsa"  # hsa (human), mmu (mouse)
CHAIN="TRB"    # TRA, TRB, TRG, TRD, IGH, IGK, IGL

# Step 1: Align reads to V/D/J/C reference
mixcr align \
  -s "$SPECIES" \
  -p rna-seq \
  -OallowPartialAlignments=true \
  "$R1" "$R2" \
  "${SAMPLE}.vdjca"

# Step 2: Assemble clonotypes
mixcr assemble \
  -OcloneClusteringParameters.searchDepth=2 \
  -OaddReadsCountOnClustering=true \
  "${SAMPLE}.vdjca" \
  "${SAMPLE}.clns"

# Step 3: Export clonotype table
mixcr exportClones \
  --chains "$CHAIN" \
  -cloneId -count -fraction \
  -vGene -dGene -jGene -cGene \
  -nSeqCDR3 -aaSeqCDR3 \
  "${SAMPLE}.clns" \
  "${SAMPLE}_clonotypes.tsv"

echo "MiXCR complete: ${SAMPLE}_clonotypes.tsv"
```

```python
import pandas as pd

def load_mixcr_output(filepath):
    """Load MiXCR clonotype export file.

    Parameters:
        filepath: path to MiXCR export TSV
    Returns:
        DataFrame with standardized column names
    """
    df = pd.read_csv(filepath, sep="\t")

    rename = {
        "cloneId": "clone_id",
        "cloneCount": "clone_count",
        "cloneFraction": "clone_fraction",
        "aaSeqCDR3": "cdr3_aa",
        "nSeqCDR3": "cdr3_nt",
        "allVHitsWithScore": "v_gene",
        "allDHitsWithScore": "d_gene",
        "allJHitsWithScore": "j_gene",
        "allCHitsWithScore": "c_gene",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    # Clean gene names (take best hit, strip score)
    for col in ["v_gene", "d_gene", "j_gene", "c_gene"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.split("(").str[0].str.split("*").str[0]

    print(f"MiXCR clonotypes: {len(df)}")
    print(f"Total reads: {df['clone_count'].sum():,}")
    print(f"Unique CDR3aa: {df['cdr3_aa'].nunique()}")

    return df

# Usage
clonotypes = load_mixcr_output("sample1_clonotypes.tsv")
```

**Key parameters:**
- `-p rna-seq`: preset for bulk RNA-seq. Use `-p default` for targeted repertoire sequencing.
- `-OallowPartialAlignments=true`: enables rescue of partially aligned reads.
- `--chains TRB`: export specific chain. Use `ALL` for all chains.

**Expected output:** TSV with clonotype ID, count, fraction, CDR3 sequences, and V/D/J/C gene assignments.

---

## 6. VDJtools: Diversity Statistics and Visualization

Repertoire analysis and visualization using VDJtools.

```bash
#!/bin/bash
# VDJtools analysis commands

SAMPLE="sample1_clonotypes.tsv"
OUTPUT_DIR="vdjtools_output"
mkdir -p "$OUTPUT_DIR"

# Diversity statistics
vdjtools CalcDiversityStats \
  -m metadata.txt \
  "$OUTPUT_DIR/diversity"

# V-J gene usage heatmap
vdjtools PlotFancyVJUsage \
  "$SAMPLE" \
  "$OUTPUT_DIR/vj_usage"

# CDR3 spectratype (length distribution by V gene)
vdjtools PlotSpectratypeV \
  "$SAMPLE" \
  "$OUTPUT_DIR/spectratype"

# Rarefaction analysis
vdjtools RarefactionPlot \
  -m metadata.txt \
  "$OUTPUT_DIR/rarefaction"

# Pairwise overlap
vdjtools CalcPairwiseDistances \
  -m metadata.txt \
  -i morisita \
  "$OUTPUT_DIR/overlap"
```

```python
import pandas as pd

def parse_vdjtools_diversity(filepath):
    """Parse VDJtools diversity statistics output.

    Parameters:
        filepath: path to VDJtools CalcDiversityStats output
    Returns:
        DataFrame with diversity metrics per sample
    """
    df = pd.read_csv(filepath, sep="\t")

    key_cols = ["sample_id", "diversity", "observedDiversity", "shannonWienerIndex",
                "inverseSimpsonIndex", "d50Index", "chao1_mean", "efronThisted_mean"]
    available = [c for c in key_cols if c in df.columns]
    result = df[available] if available else df

    print("VDJtools Diversity Metrics:")
    print(result.to_string(index=False))
    return result

# Usage
diversity = parse_vdjtools_diversity("vdjtools_output/diversity.txt")
```

**Expected output:** Diversity statistics (Shannon, Simpson, Chao1, d50) per sample; VJ usage heatmaps; spectratype plots.

---

## 7. Diversity Indices: Shannon, Simpson, Chao1, Rarefied Richness

Comprehensive diversity metric calculation from clonotype counts.

```python
import numpy as np
import pandas as pd
from scipy.stats import entropy

def diversity_indices(clone_counts, n_bootstrap=100, rarefaction_depth=None):
    """Calculate comprehensive diversity indices with confidence intervals.

    Parameters:
        clone_counts: array of clonotype counts
        n_bootstrap: number of bootstrap iterations for CIs
        rarefaction_depth: depth for rarefied richness (None = min sample size)
    Returns:
        dict with diversity metrics and 95% CIs
    """
    counts = np.array(clone_counts, dtype=float)
    counts = counts[counts > 0]
    n_total = counts.sum()
    freqs = counts / n_total

    # Core metrics
    richness = len(counts)
    shannon = entropy(freqs, base=np.e)
    norm_shannon = shannon / np.log(richness) if richness > 1 else 0
    simpson = np.sum(freqs ** 2)
    inv_simpson = 1.0 / simpson if simpson > 0 else float("inf")
    gini_simpson = 1 - simpson

    # Chao1 estimator
    f1 = np.sum(counts == 1)
    f2 = np.sum(counts == 2)
    chao1 = richness + (f1 * (f1 - 1) / (2 * (f2 + 1)))

    # Hill numbers
    hill_q0 = richness
    hill_q1 = np.exp(shannon)
    hill_q2 = inv_simpson

    # Rarefied richness
    if rarefaction_depth is None:
        rarefaction_depth = int(n_total * 0.5)

    rarefied_richness = sum(
        1 - np.exp(
            sum(np.log(max(n_total - c - k + 1, 1)) - np.log(max(n_total - k + 1, 1))
                for k in range(rarefaction_depth))
        )
        for c in counts
        if n_total - c >= rarefaction_depth
    )

    # Bootstrap CIs
    boot_shannon = []
    boot_simpson = []
    for _ in range(n_bootstrap):
        boot_sample = np.random.choice(len(counts), size=int(n_total),
                                        p=freqs, replace=True)
        boot_counts = np.bincount(boot_sample)
        boot_counts = boot_counts[boot_counts > 0]
        boot_freqs = boot_counts / boot_counts.sum()
        boot_shannon.append(entropy(boot_freqs, base=np.e))
        boot_simpson.append(1 / np.sum(boot_freqs ** 2))

    metrics = {
        "richness": richness,
        "shannon": round(shannon, 4),
        "shannon_95ci": (round(np.percentile(boot_shannon, 2.5), 4),
                         round(np.percentile(boot_shannon, 97.5), 4)),
        "normalized_shannon": round(norm_shannon, 4),
        "simpson_index": round(simpson, 4),
        "inverse_simpson": round(inv_simpson, 4),
        "inv_simpson_95ci": (round(np.percentile(boot_simpson, 2.5), 4),
                             round(np.percentile(boot_simpson, 97.5), 4)),
        "gini_simpson": round(gini_simpson, 4),
        "chao1": round(chao1, 1),
        "hill_q0": hill_q0,
        "hill_q1": round(hill_q1, 1),
        "hill_q2": round(hill_q2, 1),
        "singletons": int(f1),
        "doubletons": int(f2),
        "total_sequences": int(n_total),
    }

    for k, v in metrics.items():
        print(f"  {k}: {v}")

    return metrics

# Usage
metrics = diversity_indices(clonotypes["clone_count"].values, n_bootstrap=1000)
```

**Key parameters:**
- Shannon entropy: higher = more diverse. Typical range: 5-12 for deep sequencing.
- Inverse Simpson: effective number of equally-abundant clonotypes.
- Chao1: estimated true richness (accounts for unobserved species).
- Hill numbers: unified framework where q=0 (richness), q=1 (Shannon), q=2 (Simpson).

**Expected output:** Dictionary with all diversity metrics and bootstrap 95% confidence intervals.

---

## 8. Clonotype Overlap Between Samples (Morisita-Horn, Jaccard)

Quantify repertoire sharing between samples.

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def pairwise_overlap(sample_clonotypes, sample_names, metrics=None):
    """Calculate pairwise repertoire overlap using multiple metrics.

    Parameters:
        sample_clonotypes: list of DataFrames with 'cdr3_aa' and 'clone_count' columns
        sample_names: list of sample identifiers
        metrics: list of metrics ('jaccard', 'sorensen', 'morisita_horn', 'cosine')
    Returns:
        dict of {metric: DataFrame (samples x samples)}
    """
    if metrics is None:
        metrics = ["jaccard", "morisita_horn"]

    n = len(sample_clonotypes)
    results = {m: np.zeros((n, n)) for m in metrics}

    for i in range(n):
        for j in range(n):
            if i == j:
                for m in metrics:
                    results[m][i, j] = 1.0
                continue
            if i > j:
                for m in metrics:
                    results[m][i, j] = results[m][j, i]
                continue

            ct_a = sample_clonotypes[i]
            ct_b = sample_clonotypes[j]
            set_a = set(ct_a["cdr3_aa"])
            set_b = set(ct_b["cdr3_aa"])
            shared = set_a & set_b

            for m in metrics:
                if m == "jaccard":
                    union = set_a | set_b
                    results[m][i, j] = len(shared) / len(union) if union else 0

                elif m == "sorensen":
                    results[m][i, j] = 2 * len(shared) / (len(set_a) + len(set_b)) \
                        if (set_a or set_b) else 0

                elif m == "morisita_horn":
                    fa = ct_a.set_index("cdr3_aa")["clone_count"]
                    fb = ct_b.set_index("cdr3_aa")["clone_count"]
                    fa = fa / fa.sum()
                    fb = fb / fb.sum()
                    all_c = sorted(set(fa.index) | set(fb.index))
                    pa = np.array([fa.get(c, 0) for c in all_c])
                    pb = np.array([fb.get(c, 0) for c in all_c])
                    denom = np.sum(pa**2) + np.sum(pb**2)
                    results[m][i, j] = 2 * np.sum(pa * pb) / denom if denom > 0 else 0

                elif m == "cosine":
                    fa = ct_a.set_index("cdr3_aa")["clone_count"]
                    fb = ct_b.set_index("cdr3_aa")["clone_count"]
                    all_c = sorted(set(fa.index) | set(fb.index))
                    va = np.array([fa.get(c, 0) for c in all_c])
                    vb = np.array([fb.get(c, 0) for c in all_c])
                    norm = np.linalg.norm(va) * np.linalg.norm(vb)
                    results[m][i, j] = np.dot(va, vb) / norm if norm > 0 else 0

    # Convert to DataFrames
    overlap_dfs = {m: pd.DataFrame(mat, index=sample_names, columns=sample_names)
                   for m, mat in results.items()}

    # Plot
    fig, axes = plt.subplots(1, len(metrics), figsize=(7 * len(metrics), 6))
    if len(metrics) == 1:
        axes = [axes]
    for ax, m in zip(axes, metrics):
        sns.heatmap(overlap_dfs[m], annot=True, fmt=".3f", cmap="YlOrRd",
                   vmin=0, vmax=1, ax=ax, square=True)
        ax.set_title(f"Repertoire Overlap ({m})")
    plt.tight_layout()
    plt.savefig("repertoire_overlap.png", dpi=150, bbox_inches="tight")
    plt.show()

    return overlap_dfs

# Usage
overlap = pairwise_overlap(
    [ct_sample1, ct_sample2, ct_sample3],
    ["Patient1", "Patient2", "Patient3"],
    metrics=["jaccard", "morisita_horn"]
)
```

**Key parameters:**
- Jaccard: binary overlap (presence/absence). Range 0-1.
- Morisita-Horn: abundance-weighted overlap. More sensitive to dominant clonotypes.
- Cosine similarity: vector-space overlap. Good for comparing frequency distributions.

**Expected output:** Pairwise overlap matrices and heatmap visualizations for each metric.

---

## 9. V(D)J Gene Usage Heatmaps

Visualize V and J gene usage patterns across samples.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def vdj_usage_heatmap(sample_clonotypes, sample_names, gene_col="v_gene",
                       count_col="clone_count", top_n=25):
    """Generate V or J gene usage heatmap across samples.

    Parameters:
        sample_clonotypes: list of DataFrames with gene and count columns
        sample_names: list of sample identifiers
        gene_col: column with gene names ('v_gene', 'j_gene')
        count_col: column with clone counts
        top_n: number of top genes to display
    Returns:
        DataFrame with gene usage frequencies per sample
    """
    # Calculate usage per sample
    usage_list = []
    for ct, name in zip(sample_clonotypes, sample_names):
        freq = ct.groupby(gene_col)[count_col].sum()
        freq = freq / freq.sum()
        freq.name = name
        usage_list.append(freq)

    usage_df = pd.DataFrame(usage_list).fillna(0).T

    # Select top genes (by mean usage across samples)
    top_genes = usage_df.mean(axis=1).nlargest(top_n).index
    usage_top = usage_df.loc[top_genes]

    # Heatmap
    fig, ax = plt.subplots(figsize=(max(10, len(sample_names) * 1.5), max(8, top_n * 0.3)))
    sns.heatmap(usage_top, cmap="YlOrRd", annot=True, fmt=".3f",
               xticklabels=True, yticklabels=True, ax=ax)
    ax.set_title(f"{gene_col.replace('_', ' ').title()} Usage Across Samples")
    ax.set_ylabel(gene_col)
    plt.tight_layout()
    plt.savefig(f"{gene_col}_usage_heatmap.png", dpi=150, bbox_inches="tight")
    plt.show()

    return usage_df

# Usage
v_usage = vdj_usage_heatmap(
    [ct_s1, ct_s2, ct_s3], ["Sample1", "Sample2", "Sample3"],
    gene_col="v_gene", top_n=20
)
```

**Expected output:** Gene usage frequency matrix (genes x samples) and clustered heatmap.

---

## 10. CDR3 Sequence Logo Generation

Generate sequence logos from CDR3 sequences using logomaker.

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def cdr3_sequence_logo(cdr3_sequences, counts=None, target_length=None, title="CDR3 Logo"):
    """Generate sequence logo from CDR3 amino acid sequences.

    Parameters:
        cdr3_sequences: list or Series of CDR3 amino acid sequences
        counts: optional weights per sequence
        target_length: filter to specific CDR3 length (None = most common length)
        title: plot title
    """
    import logomaker

    seqs = pd.Series(cdr3_sequences).dropna()
    if counts is not None:
        weights = pd.Series(counts)
    else:
        weights = pd.Series(np.ones(len(seqs)))

    # Filter to target length
    lengths = seqs.str.len()
    if target_length is None:
        target_length = int(lengths.mode().iloc[0])
    mask = lengths == target_length
    seqs = seqs[mask]
    weights = weights[mask]

    print(f"Sequences for logo: {len(seqs)} (length={target_length})")

    # Build position frequency matrix
    aa_list = list("ACDEFGHIKLMNPQRSTVWY")
    pfm = pd.DataFrame(0.0, index=range(target_length), columns=aa_list)

    for seq, w in zip(seqs, weights):
        for pos, aa in enumerate(seq):
            if aa in aa_list:
                pfm.loc[pos, aa] += w

    # Normalize to frequencies
    pfm = pfm.div(pfm.sum(axis=1), axis=0).fillna(0)

    # Information content
    background = {aa: 1/20 for aa in aa_list}
    info_df = logomaker.transform_matrix(pfm, from_type="probability",
                                          to_type="information",
                                          background=background)

    # Plot
    fig, ax = plt.subplots(figsize=(max(10, target_length * 0.8), 3))
    logo = logomaker.Logo(info_df, ax=ax, color_scheme="chemistry")
    ax.set_xlabel("CDR3 Position")
    ax.set_ylabel("Information (bits)")
    ax.set_title(f"{title} (n={len(seqs)}, length={target_length})")
    plt.tight_layout()
    plt.savefig("cdr3_logo.png", dpi=200, bbox_inches="tight")
    plt.show()

    return pfm

# Usage
pfm = cdr3_sequence_logo(clonotypes["cdr3_aa"], counts=clonotypes["clone_count"],
                          target_length=14, title="TRB CDR3 Logo")
```

**Key parameters:**
- `target_length`: CDR3 length to visualize. Most common TRB CDR3 length is 13-15 aa.
- `color_scheme="chemistry"`: colors by physicochemical properties (hydrophobic, polar, charged).
- Information content: higher bits at a position = less diversity = more conserved.

**Expected output:** Sequence logo PNG showing positional amino acid preferences in CDR3 sequences.

---

## 11. Convergent Clonotype Detection Across Patients

Identify public/convergent clonotypes shared across multiple individuals.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def detect_convergent_clonotypes(sample_clonotypes, sample_names,
                                  min_patients=2, min_frequency=1e-4):
    """Detect convergent/public clonotypes shared across patients.

    Parameters:
        sample_clonotypes: list of DataFrames with 'cdr3_aa', 'v_gene', 'clone_count'
        sample_names: list of patient/sample identifiers
        min_patients: minimum patients sharing a clonotype
        min_frequency: minimum clone fraction in at least one patient
    Returns:
        DataFrame with convergent clonotypes and sharing statistics
    """
    cdr3_data = {}
    for ct, name in zip(sample_clonotypes, sample_names):
        total = ct["clone_count"].sum()
        for _, row in ct.iterrows():
            cdr3 = row["cdr3_aa"]
            freq = row["clone_count"] / total
            v_gene = row.get("v_gene", "")

            if cdr3 not in cdr3_data:
                cdr3_data[cdr3] = {"patients": set(), "v_genes": set(),
                                    "frequencies": {}, "total_count": 0}
            cdr3_data[cdr3]["patients"].add(name)
            cdr3_data[cdr3]["v_genes"].add(v_gene)
            cdr3_data[cdr3]["frequencies"][name] = freq
            cdr3_data[cdr3]["total_count"] += row["clone_count"]

    # Filter convergent clonotypes
    convergent = []
    for cdr3, data in cdr3_data.items():
        n_patients = len(data["patients"])
        max_freq = max(data["frequencies"].values()) if data["frequencies"] else 0

        if n_patients >= min_patients and max_freq >= min_frequency:
            convergent.append({
                "cdr3_aa": cdr3,
                "n_patients": n_patients,
                "patients": ",".join(sorted(data["patients"])),
                "v_genes": ",".join(sorted(data["v_genes"])),
                "max_frequency": max_freq,
                "mean_frequency": np.mean(list(data["frequencies"].values())),
                "total_count": data["total_count"],
            })

    conv_df = pd.DataFrame(convergent).sort_values("n_patients", ascending=False)

    print(f"Convergent clonotypes (shared by >= {min_patients} patients): {len(conv_df)}")
    if len(conv_df) > 0:
        print(f"  Max sharing: {conv_df['n_patients'].max()} patients")
        print(f"  Top 5 most shared:")
        for _, row in conv_df.head(5).iterrows():
            print(f"    {row['cdr3_aa']}: {row['n_patients']} patients, "
                  f"max freq={row['max_frequency']:.4f}")

    # Sharing distribution plot
    if len(conv_df) > 0:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        sharing_counts = conv_df["n_patients"].value_counts().sort_index()
        axes[0].bar(sharing_counts.index, sharing_counts.values, color="steelblue")
        axes[0].set_xlabel("Number of Patients")
        axes[0].set_ylabel("Number of Convergent Clonotypes")
        axes[0].set_title("Clonotype Sharing Distribution")

        axes[1].hist(np.log10(conv_df["max_frequency"]), bins=30, color="coral")
        axes[1].set_xlabel("log10(Max Frequency)")
        axes[1].set_ylabel("Count")
        axes[1].set_title("Convergent Clonotype Frequencies")

        plt.tight_layout()
        plt.savefig("convergent_clonotypes.png", dpi=150, bbox_inches="tight")
        plt.show()

    return conv_df

# Usage
convergent = detect_convergent_clonotypes(
    [ct_p1, ct_p2, ct_p3, ct_p4, ct_p5],
    ["Patient1", "Patient2", "Patient3", "Patient4", "Patient5"],
    min_patients=2, min_frequency=1e-4
)
```

**Key parameters:**
- `min_patients=2`: minimum patients for convergent definition. Increase for stringent public clonotypes.
- `min_frequency=1e-4`: ignore very rare clonotypes (noise).
- Public clonotypes: CDR3 sequences found in many unrelated individuals, often against common antigens (CMV, EBV, influenza).

**Expected output:** DataFrame with convergent clonotypes, sharing statistics, and distribution plot.

---

## 12. Integration with scRNA-seq (Paired TCR + Transcriptome)

Integrate VDJ clonotype information with single-cell gene expression using scirpy.

```python
import scirpy as ir
import scanpy as sc
import matplotlib.pyplot as plt

def integrate_vdj_gex(gex_adata, vdj_path, cell_type_key="cell_type"):
    """Integrate VDJ clonotype data with scRNA-seq gene expression.

    Parameters:
        gex_adata: AnnData with processed scRNA-seq data (clustered, annotated)
        vdj_path: path to 10x filtered_contig_annotations.csv
        cell_type_key: obs column with cell type annotations
    Returns:
        AnnData with integrated VDJ + GEX data
    """
    # Load VDJ
    adata_vdj = ir.io.read_10x_vdj(vdj_path)

    # Merge
    ir.pp.merge_with_ir(gex_adata, adata_vdj)

    # Define clonotypes
    ir.pp.ir_dist(gex_adata, metric="identity", sequence="aa")
    ir.tl.define_clonotypes(gex_adata, receptor_arms="all", dual_ir="primary_only")
    ir.tl.clonal_expansion(gex_adata)

    # Summary
    has_ir = gex_adata.obs["has_ir"].sum() if "has_ir" in gex_adata.obs.columns else 0
    print(f"GEX cells: {gex_adata.n_obs}")
    print(f"Cells with VDJ: {has_ir}")
    print(f"Clonotypes: {gex_adata.obs['clone_id'].nunique()}")

    # Visualizations
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # UMAP colored by clonal expansion
    sc.pl.umap(gex_adata, color="clonal_expansion", ax=axes[0, 0], show=False,
               title="Clonal Expansion on UMAP")

    # Clonal expansion per cell type
    ir.pl.group_abundance(gex_adata, groupby="clonal_expansion",
                          target_col=cell_type_key, ax=axes[0, 1])

    # VDJ presence per cluster
    if cell_type_key in gex_adata.obs.columns:
        ct_vdj = gex_adata.obs.groupby(cell_type_key)["has_ir"].mean()
        ct_vdj.sort_values().plot(kind="barh", ax=axes[1, 0], color="steelblue")
        axes[1, 0].set_xlabel("Fraction with VDJ")
        axes[1, 0].set_title("VDJ Detection by Cell Type")

    # CDR3 length by cell type
    if "IR_VDJ_1_junction_aa" in gex_adata.obs.columns:
        gex_adata.obs["cdr3_length"] = gex_adata.obs["IR_VDJ_1_junction_aa"].str.len()
        sc.pl.violin(gex_adata, keys="cdr3_length", groupby=cell_type_key,
                     ax=axes[1, 1], show=False)
        axes[1, 1].set_title("CDR3 Length by Cell Type")

    plt.tight_layout()
    plt.savefig("vdj_gex_integration.png", dpi=150, bbox_inches="tight")
    plt.show()

    return gex_adata


def clonotype_de(adata, clone_id, cell_type_key="cell_type",
                 min_cells=10, method="wilcoxon"):
    """Differential expression for cells in a specific clonotype vs rest.

    Parameters:
        adata: AnnData with VDJ and GEX
        clone_id: specific clonotype ID to analyze
        cell_type_key: restrict comparison to same cell type
        min_cells: minimum cells in clonotype for DE
        method: DE test method
    Returns:
        DE results DataFrame
    """
    clone_cells = adata.obs["clone_id"] == clone_id
    n_clone = clone_cells.sum()

    if n_clone < min_cells:
        print(f"Clonotype {clone_id} has only {n_clone} cells (min: {min_cells})")
        return None

    # Get dominant cell type of this clonotype
    dom_type = adata.obs.loc[clone_cells, cell_type_key].mode().iloc[0]

    # Subset to same cell type
    type_mask = adata.obs[cell_type_key] == dom_type
    adata_sub = adata[type_mask].copy()
    adata_sub.obs["is_clonotype"] = (adata_sub.obs["clone_id"] == clone_id).astype(str)

    sc.tl.rank_genes_groups(adata_sub, groupby="is_clonotype", reference="False",
                            method=method)
    de_df = sc.get.rank_genes_groups_df(adata_sub, group="True")

    print(f"Clonotype {clone_id}: {n_clone} cells in {dom_type}")
    print(f"Top DE genes: {de_df.head(5)['names'].tolist()}")

    return de_df

# Usage
adata = integrate_vdj_gex(gex_adata, "filtered_contig_annotations.csv")
de = clonotype_de(adata, clone_id="clonotype_1", min_cells=10)
```

**Key parameters:**
- `receptor_arms="all"`: require both chains to match for clonotype definition (strictest).
- `min_cells=10`: minimum cells for meaningful DE analysis within a clonotype.
- UMAP overlay of clonal expansion reveals spatially distinct expanded populations.

**Expected output:** Integrated AnnData with VDJ annotations; multi-panel visualization; clonotype-specific DE results.

---

## Quick Reference

| Task | Recipe | Key tool |
|------|--------|----------|
| 10x VDJ loading + chain QC | #1 | `scirpy ir.io.read_10x_vdj` |
| Clonal expansion categories | #2 | `ir.tl.clonal_expansion` |
| Immcantation clonal assignment | #3 | `DefineClones.py` |
| SHM quantification | #4 | Pairwise germline comparison |
| MiXCR pipeline | #5 | `mixcr align/assemble/export` |
| VDJtools diversity | #6 | `CalcDiversityStats` |
| Diversity indices + CI | #7 | Shannon/Simpson/Chao1/Hill |
| Repertoire overlap | #8 | Jaccard/Morisita-Horn |
| V(D)J usage heatmap | #9 | Gene frequency matrix |
| CDR3 sequence logo | #10 | `logomaker` |
| Convergent clonotypes | #11 | Cross-patient sharing |
| VDJ + scRNA-seq | #12 | `scirpy + scanpy` |

---

## Cross-Skill Routing

- Conceptual guidance and pipeline decisions --> `immune-repertoire-analysis`
- scRNA-seq preprocessing and clustering --> `single-cell-analysis`
- Immunotherapy response prediction --> `immunotherapy-response-predictor`
- Cancer variant interpretation for neoantigens --> `cancer-variant-interpreter`
- Literature review on adaptive immunity --> `literature-deep-research`
