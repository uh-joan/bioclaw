---
name: immune-repertoire-analysis
description: Immune repertoire and adaptive immunity analysis. TCR sequencing, BCR sequencing, clonotype analysis, V(D)J recombination, CDR3 analysis, diversity metrics, clonal expansion, repertoire overlap, immunoglobulin analysis, T-cell receptor analysis. Use when user mentions immune repertoire, TCR, BCR, T-cell receptor, B-cell receptor, clonotype, V(D)J, CDR3, repertoire sequencing, clonal expansion, immunoglobulin sequencing, adaptive immunity profiling, or repertoire diversity.
---

# Immune Repertoire Analysis

> **Code recipes**: See [repertoire-recipes.md](repertoire-recipes.md) for copy-paste executable code templates covering scirpy, Immcantation, MiXCR, VDJtools, diversity indices, CDR3 logos, and VDJ+scRNA-seq integration.

Production-ready immune repertoire analysis methodology. The agent writes and executes Python code for TCR/BCR sequencing data covering clonotype identification, diversity quantification, V(D)J gene usage, CDR3 characterization, clonal expansion tracking, repertoire overlap, and antigen-specificity prediction. Uses Open Targets, PubMed, ChEMBL, and DrugBank for biological annotation of results.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_immune-repertoire-analysis_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Immunotherapy response prediction from repertoire features → use `immunotherapy-response-predictor`
- Single-cell VDJ + gene expression integration → use `single-cell-analysis`
- Somatic variant interpretation in lymphoid malignancies → use `cancer-variant-interpreter`
- Pharmacogenomic analysis of immunotherapy drugs → use `pharmacogenomics-specialist`
- Deep literature review on adaptive immunity topics → use `literature-deep-research`

## Cross-Reference: Other Skills

- **Immunotherapy response prediction from repertoire features** -> use immunotherapy-response-predictor skill
- **Single-cell VDJ + gene expression integration** -> use single-cell-analysis skill
- **Somatic variant interpretation in lymphoid malignancies** -> use cancer-variant-interpreter skill

## Python Environment

Standard scientific Python: `numpy, pandas, scipy, matplotlib, seaborn, scikit-learn, networkx, biopython`. For specialized tools, install at runtime: `subprocess.run(["pip", "install", "scirpy"], check=True)`.

## Data Input Formats

```python
import pandas as pd
import numpy as np

def load_repertoire(path, fmt="auto"):
    """Load immune repertoire data. Supports AIRR (TSV), MiXCR, immunoSEQ, 10x VDJ."""
    if fmt == "auto":
        with open(path, "r") as f:
            header = f.readline().strip().lower()
        if "sequence_id" in header and "v_call" in header: fmt = "airr"
        elif "cloneid" in header or "clonecount" in header: fmt = "mixcr"
        elif "nucleotide" in header and "aminoacid" in header: fmt = "immunoseq"
        elif "barcode" in header and "contig_id" in header: fmt = "10x_vdj"
        else: raise ValueError(f"Cannot detect format: {header[:100]}")

    df = pd.read_csv(path, sep="\t" if fmt != "10x_vdj" else ",",
                     comment="#" if fmt == "immunoseq" else None)

    col_maps = {
        "airr": {"junction_aa": "cdr3_aa", "junction": "cdr3_nt", "v_call": "v_gene",
                 "d_call": "d_gene", "j_call": "j_gene", "duplicate_count": "clone_count"},
        "mixcr": {"aaSeqCDR3": "cdr3_aa", "nSeqCDR3": "cdr3_nt", "cloneCount": "clone_count",
                  "cloneFraction": "clone_fraction"},
        "immunoseq": {"aminoAcid": "cdr3_aa", "nucleotide": "cdr3_nt", "vGeneName": "v_gene",
                      "jGeneName": "j_gene"},
        "10x_vdj": {"cdr3": "cdr3_aa", "cdr3_nt": "cdr3_nt", "umis": "clone_count"},
    }
    df = df.rename(columns={k: v for k, v in col_maps.get(fmt, {}).items() if k in df.columns})

    # Strip allele info from gene names (e.g., TRBV7-2*01 -> TRBV7-2)
    for col in ["v_gene", "d_gene", "j_gene"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.split("*").str[0]

    # Filter productive contigs for 10x
    if fmt == "10x_vdj":
        for col in ["productive", "is_cell"]:
            if col in df.columns:
                df = df[df[col].astype(str).str.lower() == "true"]
    return df
```

---

## Analysis Pipeline

### Phase 1: Data Loading & Clonotype Definition

```python
import matplotlib.pyplot as plt
import seaborn as sns

df = load_repertoire("repertoire.tsv")
df = df[df["cdr3_aa"].notna() & ~df["cdr3_aa"].str.contains(r"\*|_", na=False)].copy()
if "clone_count" in df.columns:
    df["clone_count"] = pd.to_numeric(df["clone_count"], errors="coerce").fillna(1).astype(int)
else:
    df["clone_count"] = 1

print(f"Loaded {len(df)} sequences, {df['cdr3_aa'].nunique()} unique CDR3s")

def define_clonotypes(df, mode="cdr3_vj"):
    """Group sequences into clonotypes by CDR3aa (cdr3_only) or CDR3aa+V+J (cdr3_vj)."""
    group_cols = ["cdr3_aa"] if mode == "cdr3_only" else ["cdr3_aa", "v_gene", "j_gene"]
    clonotypes = df.groupby(group_cols).agg(clone_count=("clone_count", "sum")).reset_index()
    clonotypes = clonotypes.sort_values("clone_count", ascending=False).reset_index(drop=True)
    clonotypes["clone_fraction"] = clonotypes["clone_count"] / clonotypes["clone_count"].sum()
    clonotypes["rank"] = range(1, len(clonotypes) + 1)
    return clonotypes

clonotypes = define_clonotypes(df, mode="cdr3_vj")
print(f"Total clonotypes: {len(clonotypes)}")
print(f"Top 10 account for {clonotypes.head(10)['clone_fraction'].sum():.1%} of repertoire")
print(clonotypes.head(10)[["cdr3_aa", "v_gene", "j_gene", "clone_count", "clone_fraction"]])
```

### Phase 2: Diversity Analysis

```python
from scipy.stats import entropy

def calculate_diversity_metrics(clonotypes):
    """Shannon entropy, Simpson's index, Chao1, Hill numbers, Pielou's evenness."""
    counts = clonotypes["clone_count"].values
    freqs = counts / counts.sum()
    richness = len(counts)

    shannon = entropy(freqs, base=np.e)
    norm_shannon = shannon / np.log(richness) if richness > 1 else 0.0
    simpson = np.sum(freqs ** 2)
    inv_simpson = 1.0 / simpson if simpson > 0 else float("inf")

    f1, f2 = np.sum(counts == 1), np.sum(counts == 2)
    chao1 = richness + (f1 ** 2 / (2 * f2) if f2 > 0 else f1 * (f1 - 1) / 2 if f1 > 0 else 0)

    return {
        "richness": richness, "shannon_entropy": shannon, "normalized_shannon": norm_shannon,
        "simpson_index": simpson, "inverse_simpson": inv_simpson, "gini_simpson": 1 - simpson,
        "chao1": chao1, "hill_q0": richness, "hill_q1": np.exp(shannon), "hill_q2": inv_simpson,
        "evenness": norm_shannon, "singletons": int(f1), "total_sequences": int(counts.sum()),
    }

metrics = calculate_diversity_metrics(clonotypes)
for k, v in metrics.items():
    print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")

def rarefaction_curve(clonotypes, steps=50):
    """Rarefaction curve to assess sampling depth."""
    counts = clonotypes["clone_count"].values
    n_total = counts.sum()
    sample_sizes = np.linspace(1, n_total, steps, dtype=int)
    expected = []
    for n in sample_sizes:
        e_s = sum(1 - np.exp(np.sum(np.log(np.maximum(np.arange(n_total - ni - n + 1, n_total - ni + 1), 1)))
                 - np.sum(np.log(np.maximum(np.arange(n_total - n + 1, n_total + 1), 1))))
                 if n_total - ni >= n else 1 for ni in counts)
        expected.append(e_s)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(sample_sizes, expected, "b-", linewidth=2)
    ax.set_xlabel("Sample Size"); ax.set_ylabel("Expected Clonotypes"); ax.set_title("Rarefaction Curve")
    ax.axvline(n_total, color="r", linestyle="--", label=f"Depth: {n_total}")
    ax.legend(); plt.tight_layout(); plt.savefig("rarefaction_curve.png", dpi=150, bbox_inches="tight"); plt.show()

rarefaction_curve(clonotypes)
```

### Phase 3: V(D)J Gene Usage

```python
def plot_gene_usage(clonotypes, count_col="clone_count", top_n=25):
    """V, J, D gene usage bar charts and V-J pairing heatmap."""
    gene_types = [(c, l) for c, l in [("v_gene","V Gene"),("j_gene","J Gene"),("d_gene","D Gene")] if c in clonotypes.columns]
    fig, axes = plt.subplots(1, len(gene_types), figsize=(7*len(gene_types), 6))
    if len(gene_types) == 1: axes = [axes]
    for ax, (col, label) in zip(axes, gene_types):
        usage = clonotypes.groupby(col)[count_col].sum()
        usage = (usage / usage.sum()).sort_values(ascending=False).head(top_n)
        ax.barh(range(len(usage)), usage.values, color="steelblue")
        ax.set_yticks(range(len(usage))); ax.set_yticklabels(usage.index, fontsize=8)
        ax.set_xlabel("Frequency"); ax.set_title(f"{label} Usage"); ax.invert_yaxis()
    plt.tight_layout(); plt.savefig("vdj_gene_usage.png", dpi=150, bbox_inches="tight"); plt.show()

def vj_pairing_heatmap(clonotypes, count_col="clone_count", top_v=20, top_j=10):
    """V-J gene pairing heatmap."""
    if "v_gene" not in clonotypes.columns or "j_gene" not in clonotypes.columns: return
    pivot = clonotypes.groupby(["v_gene","j_gene"])[count_col].sum().reset_index()
    pivot = pivot.pivot_table(index="v_gene", columns="j_gene", values=count_col, fill_value=0)
    top_vs = pivot.sum(axis=1).nlargest(top_v).index
    top_js = pivot.sum(axis=0).nlargest(top_j).index
    pivot = pivot.loc[top_vs, top_js].div(pivot.loc[top_vs, top_js].sum(axis=1), axis=0)

    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(pivot, cmap="YlOrRd", ax=ax, xticklabels=True, yticklabels=True)
    ax.set_title("V-J Gene Pairing"); plt.tight_layout()
    plt.savefig("vj_pairing_heatmap.png", dpi=150, bbox_inches="tight"); plt.show()

plot_gene_usage(clonotypes)
vj_pairing_heatmap(clonotypes)
```

### Phase 4: CDR3 Analysis

```python
def cdr3_analysis(clonotypes, count_col="clone_count"):
    """CDR3 length distribution, amino acid composition, physicochemical properties."""
    ct = clonotypes[clonotypes["cdr3_aa"].notna()].copy()
    ct["cdr3_length"] = ct["cdr3_aa"].str.len()
    aa_props = {"hydrophobic": set("AILMFWVP"), "polar": set("STNQYC"),
                "positive": set("RHK"), "negative": set("DE"), "aromatic": set("FWY")}

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    axes[0].hist(ct["cdr3_length"], bins=range(5,35), color="steelblue", edgecolor="white")
    axes[0].set_xlabel("CDR3 Length (aa)"); axes[0].set_title("CDR3 Length Distribution")
    axes[0].axvline(ct["cdr3_length"].median(), color="red", linestyle="--",
                    label=f"Median: {ct['cdr3_length'].median():.0f}"); axes[0].legend()

    # AA composition
    from collections import Counter
    aa_counts = Counter()
    for _, row in ct.iterrows():
        for aa in row["cdr3_aa"]: aa_counts[aa] += row[count_col]
    total = sum(aa_counts.values())
    aa_freq = {aa: c/total for aa, c in sorted(aa_counts.items())}
    axes[1].bar(aa_freq.keys(), aa_freq.values(), color="steelblue")
    axes[1].set_xlabel("Amino Acid"); axes[1].set_title("CDR3 AA Composition")

    # Physicochemical
    prop_f = {p: sum(aa_freq.get(a,0) for a in s) for p, s in aa_props.items()}
    axes[2].barh(list(prop_f.keys()), list(prop_f.values()), color="coral")
    axes[2].set_xlabel("Fraction"); axes[2].set_title("CDR3 Properties")
    plt.tight_layout(); plt.savefig("cdr3_analysis.png", dpi=150, bbox_inches="tight"); plt.show()
    return aa_freq, prop_f

def identify_public_clonotypes(sample_dfs, sample_names, min_samples=2):
    """Identify public clonotypes shared across individuals (convergent selection)."""
    cdr3_samples = {}
    for name, df in zip(sample_names, sample_dfs):
        for cdr3 in df["cdr3_aa"].unique():
            cdr3_samples.setdefault(cdr3, set()).add(name)
    public = pd.DataFrame([{"cdr3_aa": c, "n_samples": len(s), "samples": ", ".join(sorted(s))}
                           for c, s in cdr3_samples.items() if len(s) >= min_samples])
    print(f"Public clonotypes (>= {min_samples} samples): {len(public)}")
    return public.sort_values("n_samples", ascending=False)

aa_freq, prop_fracs = cdr3_analysis(clonotypes)
```

### Phase 5: Clonal Expansion Analysis

```python
def clonal_expansion_analysis(clonotypes, count_col="clone_count"):
    """Clone size distribution, Gini coefficient, Lorenz curve, rank-abundance."""
    fracs = clonotypes[count_col].values / clonotypes[count_col].sum()
    categories = {"Hyperexpanded (>1%)": fracs > 0.01, "Large (0.1-1%)": (fracs > 0.001) & (fracs <= 0.01),
                  "Medium (0.01-0.1%)": (fracs > 0.0001) & (fracs <= 0.001), "Small (<0.01%)": fracs <= 0.0001}
    for cat, mask in categories.items():
        print(f"{cat}: {mask.sum()} clonotypes ({fracs[mask].sum():.1%} of repertoire)")

    sorted_f = np.sort(fracs)
    n = len(sorted_f)
    gini = (2 * np.sum(np.arange(1, n+1) * sorted_f) - (n+1) * sorted_f.sum()) / (n * sorted_f.sum())
    print(f"Gini coefficient: {gini:.4f}")

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    axes[0].loglog(range(1, len(fracs)+1), np.sort(fracs)[::-1], "b-", linewidth=1.5)
    axes[0].set_xlabel("Clone Rank"); axes[0].set_ylabel("Fraction"); axes[0].set_title("Rank-Abundance")

    cum_clones = np.arange(1, n+1) / n
    cum_abund = np.cumsum(sorted_f) / sorted_f.sum()
    axes[1].plot(cum_clones, cum_abund, "b-", linewidth=2)
    axes[1].plot([0,1],[0,1], "k--", alpha=0.5)
    axes[1].set_title(f"Lorenz Curve (Gini={gini:.3f})")

    cat_sizes = [fracs[m].sum() for m in categories.values()]
    axes[2].pie(cat_sizes, labels=list(categories.keys()), autopct="%1.1f%%",
                colors=["#d62728","#ff7f0e","#2ca02c","#1f77b4"])
    axes[2].set_title("Clone Size Distribution")
    plt.tight_layout(); plt.savefig("clonal_expansion.png", dpi=150, bbox_inches="tight"); plt.show()
    return categories, gini

def track_clones_longitudinal(timepoint_dfs, timepoint_labels, top_n=20):
    """Track top clonotypes across timepoints."""
    all_clones = {}
    for label, df in zip(timepoint_labels, timepoint_dfs):
        total = df["clone_count"].sum()
        for _, row in df.iterrows():
            all_clones.setdefault(row["cdr3_aa"], {})[label] = row["clone_count"] / total
    top = sorted(all_clones, key=lambda c: max(all_clones[c].values()), reverse=True)[:top_n]
    tracking = pd.DataFrame({c: {l: all_clones[c].get(l, 0) for l in timepoint_labels} for c in top}).T

    fig, ax = plt.subplots(figsize=(10, 7))
    for cdr3 in top:
        ax.plot(timepoint_labels, [all_clones[cdr3].get(l, 0) for l in timepoint_labels],
                marker="o", label=cdr3[:15])
    ax.set_ylabel("Fraction"); ax.set_yscale("log"); ax.set_title("Clone Tracking")
    ax.legend(bbox_to_anchor=(1.05, 1), fontsize=7); plt.tight_layout()
    plt.savefig("clone_tracking.png", dpi=150, bbox_inches="tight"); plt.show()
    return tracking

expansion, gini = clonal_expansion_analysis(clonotypes)
```

### Phase 6: Repertoire Comparison

```python
def repertoire_overlap(ct_a, ct_b, count_col="clone_count"):
    """Jaccard, Sorensen, Morisita-Horn overlap between two repertoires."""
    set_a, set_b = set(ct_a["cdr3_aa"]), set(ct_b["cdr3_aa"])
    shared = set_a & set_b
    jaccard = len(shared) / len(set_a | set_b) if set_a | set_b else 0
    sorensen = 2 * len(shared) / (len(set_a) + len(set_b)) if set_a or set_b else 0

    fa = ct_a.set_index("cdr3_aa")[count_col]; fa = fa / fa.sum()
    fb = ct_b.set_index("cdr3_aa")[count_col]; fb = fb / fb.sum()
    all_c = sorted(set(fa.index) | set(fb.index))
    pa, pb = np.array([fa.get(c,0) for c in all_c]), np.array([fb.get(c,0) for c in all_c])
    mh = 2 * np.sum(pa * pb) / (np.sum(pa**2) + np.sum(pb**2)) if np.sum(pa**2) + np.sum(pb**2) > 0 else 0

    return {"jaccard": jaccard, "sorensen": sorensen, "morisita_horn": mh,
            "shared": len(shared), "unique_a": len(set_a - set_b), "unique_b": len(set_b - set_a)}

def pairwise_overlap_matrix(sample_dfs, sample_names, metric="morisita_horn"):
    """Pairwise overlap heatmap across samples."""
    n = len(sample_dfs)
    matrix = np.eye(n)
    for i in range(n):
        for j in range(i+1, n):
            v = repertoire_overlap(sample_dfs[i], sample_dfs[j])[metric]
            matrix[i,j] = matrix[j,i] = v
    df = pd.DataFrame(matrix, index=sample_names, columns=sample_names)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(df, annot=True, fmt=".3f", cmap="YlOrRd", vmin=0, vmax=1, ax=ax, square=True)
    ax.set_title(f"Repertoire Overlap ({metric})"); plt.tight_layout()
    plt.savefig("overlap_matrix.png", dpi=150, bbox_inches="tight"); plt.show()
    return df

def differential_abundance(ct_a, ct_b, label_a="A", label_b="B", count_col="clone_count"):
    """Log2 fold-change of clonotype frequencies between two repertoires."""
    fa = ct_a.set_index("cdr3_aa")[count_col]; fa = fa / fa.sum()
    fb = ct_b.set_index("cdr3_aa")[count_col]; fb = fb / fb.sum()
    all_c = sorted(set(fa.index) | set(fb.index))
    pseudo = 1e-7
    diff = pd.DataFrame({"cdr3_aa": all_c, f"freq_{label_a}": [fa.get(c,0) for c in all_c],
                         f"freq_{label_b}": [fb.get(c,0) for c in all_c]})
    diff["log2fc"] = np.log2((diff[f"freq_{label_b}"]+pseudo) / (diff[f"freq_{label_a}"]+pseudo))
    diff["mean_freq"] = (diff[f"freq_{label_a}"] + diff[f"freq_{label_b}"]) / 2

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(np.log10(diff["mean_freq"]+pseudo), diff["log2fc"], alpha=0.3, s=10, c="grey")
    sig = diff[abs(diff["log2fc"]) > 2]
    ax.scatter(np.log10(sig["mean_freq"]+pseudo), sig["log2fc"], alpha=0.6, s=15, c="red",
               label=f"|log2FC|>2 (n={len(sig)})")
    ax.axhline(0, color="black", linewidth=0.5); ax.set_xlabel("log10(Mean Freq)")
    ax.set_ylabel(f"log2FC ({label_b}/{label_a})"); ax.set_title("Differential Abundance"); ax.legend()
    plt.tight_layout(); plt.savefig("diff_abundance.png", dpi=150, bbox_inches="tight"); plt.show()
    return diff.sort_values("log2fc", key=abs, ascending=False)
```

### Phase 7: Antigen-Specificity Prediction

```python
from sklearn.cluster import DBSCAN

def cluster_cdr3_sequences(clonotypes, distance_threshold=0.15, max_seqs=5000):
    """Cluster CDR3s by sequence similarity to identify specificity groups."""
    seqs = clonotypes["cdr3_aa"].values
    if len(seqs) > max_seqs:
        seqs = np.random.choice(seqs, max_seqs, replace=False)
    n = len(seqs)
    dist = np.ones((n, n))
    for i in range(n):
        dist[i,i] = 0
        for j in range(i+1, n):
            if len(seqs[i]) == len(seqs[j]):
                d = sum(a != b for a, b in zip(seqs[i], seqs[j])) / len(seqs[i])
            else:
                d = 1.0
            dist[i,j] = dist[j,i] = d

    labels = DBSCAN(eps=distance_threshold, min_samples=2, metric="precomputed").fit_predict(dist)
    cluster_df = pd.DataFrame({"cdr3_aa": seqs, "cluster": labels})
    n_clusters = len(set(labels) - {-1})
    print(f"CDR3 specificity clusters: {n_clusters}, unclustered: {(labels==-1).sum()}")

    summary = cluster_df[cluster_df["cluster"] >= 0].groupby("cluster").agg(
        n_members=("cdr3_aa", "count"), representative=("cdr3_aa", "first")).sort_values("n_members", ascending=False)
    print(summary.head(10))
    return cluster_df, summary

cluster_df, cluster_summary = cluster_cdr3_sequences(clonotypes)
```

---

## TCR vs BCR Considerations

| Feature | TCR | BCR |
|---------|-----|-----|
| **Chains** | alpha/beta or gamma/delta | Heavy (IGH) + Light (IGK/IGL) |
| **Somatic hypermutation** | Absent | Present (affinity maturation) |
| **Isotype switching** | N/A | IgM -> IgG/IgA/IgE |
| **Key additional metrics** | Public TCRs, epitope prediction | SHM rate, isotype distribution, lineage trees |

```python
def isotype_analysis(clonotypes, count_col="clone_count"):
    """BCR isotype distribution analysis."""
    if "c_gene" not in clonotypes.columns: return None
    iso_map = {"IGHM":"IgM","IGHD":"IgD","IGHG1":"IgG1","IGHG2":"IgG2","IGHG3":"IgG3",
               "IGHG4":"IgG4","IGHA1":"IgA1","IGHA2":"IgA2","IGHE":"IgE"}
    clonotypes["isotype"] = clonotypes["c_gene"].map(iso_map).fillna(clonotypes["c_gene"])
    frac = clonotypes.groupby("isotype")[count_col].sum()
    frac = frac / frac.sum()
    fig, ax = plt.subplots(figsize=(8, 5))
    frac.sort_values().plot(kind="barh", ax=ax, color="steelblue")
    ax.set_xlabel("Fraction"); ax.set_title("Isotype Distribution")
    plt.tight_layout(); plt.savefig("isotype_distribution.png", dpi=150, bbox_inches="tight"); plt.show()
    return frac
```

---

## Clinical Applications

### Minimal Residual Disease Tracking

```python
def mrd_tracking(diag_clonotypes, followup_dfs, followup_labels, threshold=1e-6):
    """Track dominant diagnostic clonotype for MRD in lymphoid malignancies."""
    dom = diag_clonotypes.iloc[0]
    results = [{"timepoint": "Diagnosis", "frequency": dom["clone_fraction"], "status": "Positive"}]
    for label, df in zip(followup_labels, followup_dfs):
        total = df["clone_count"].sum()
        match = df[df["cdr3_aa"] == dom["cdr3_aa"]]
        freq = match["clone_count"].sum() / total if len(match) > 0 else 0
        results.append({"timepoint": label, "frequency": freq,
                        "status": "Positive" if freq > threshold else "Negative"})
    mrd_df = pd.DataFrame(results)
    fig, ax = plt.subplots(figsize=(10, 5))
    freqs = np.where(mrd_df["frequency"] == 0, threshold/10, mrd_df["frequency"])
    ax.semilogy(mrd_df["timepoint"], freqs, "ro-", markersize=10)
    ax.axhline(threshold, color="blue", linestyle="--", label=f"Threshold ({threshold:.0e})")
    ax.set_ylabel("Frequency"); ax.set_title("MRD Tracking"); ax.legend()
    plt.xticks(rotation=45); plt.tight_layout()
    plt.savefig("mrd_tracking.png", dpi=150, bbox_inches="tight"); plt.show()
    return mrd_df
```

### Checkpoint Response & Vaccine Response Features

```python
def repertoire_response_features(clonotypes, count_col="clone_count"):
    """Extract repertoire features predictive of ICI response or vaccine efficacy."""
    m = calculate_diversity_metrics(clonotypes)
    fracs = clonotypes[count_col].values / clonotypes[count_col].sum()
    sorted_f = np.sort(fracs)
    n = len(sorted_f)
    gini = (2*np.sum(np.arange(1,n+1)*sorted_f) - (n+1)*sorted_f.sum()) / (n*sorted_f.sum())
    features = {"richness": m["richness"], "shannon": m["shannon_entropy"],
                "inverse_simpson": m["inverse_simpson"], "evenness": m["evenness"],
                "gini": gini, "top1_frac": fracs.max(),
                "top10_frac": np.sort(fracs)[-10:].sum() if len(fracs)>=10 else fracs.sum()}
    for k, v in features.items(): print(f"  {k}: {v:.4f}")
    return features

def vaccine_response(pre, post, count_col="clone_count"):
    """Compare pre/post-vaccination repertoires."""
    pre_m, post_m = calculate_diversity_metrics(pre), calculate_diversity_metrics(post)
    for k in ["richness","shannon_entropy","inverse_simpson"]:
        pct = (post_m[k]-pre_m[k])/pre_m[k]*100 if pre_m[k] else 0
        print(f"  {k}: {pre_m[k]:.4f} -> {post_m[k]:.4f} ({pct:+.1f}%)")
    new = post[~post["cdr3_aa"].isin(set(pre["cdr3_aa"])) &
               (post[count_col]/post[count_col].sum() > 0.001)]
    print(f"Newly expanded clonotypes (>0.1%): {len(new)}")
    return new
```

---

## Evidence Grading

| Tier | Evidence Type | Example |
|------|-------------|---------|
| **T1** | Validated clinical assay | ClonoSEQ MRD (Adaptive Biotechnologies) |
| **T2** | Prospective clinical study | TCR diversity predicting ICI response |
| **T3** | Retrospective analysis | Clonal expansion and vaccine efficacy |
| **T4** | Exploratory / preclinical | CDR3 clustering for specificity prediction |

**MCP-assisted evidence annotation:**
```
1. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "immune repertoire TCR sequencing clinical biomarker", num_results: 10)
2. mcp__opentargets__opentargets_info(method: "search_targets", query: "TCR alpha")
3. mcp__drugbank__drugbank_info(method: "search_by_category", category: "immunotherapy", limit: 20)
4. mcp__chembl__chembl_info(method: "target_search", query: "T-cell receptor")
```

---

## Multi-Agent Workflow Examples

**"Analyze TCR repertoire from tumor-infiltrating lymphocytes and identify expanded clones"**
1. Immune Repertoire Analysis -> Full pipeline: clonotype definition, diversity, V(D)J usage, CDR3 analysis, clonal expansion
2. Immunotherapy Response Predictor -> Use repertoire diversity and expansion features to predict ICI response
3. Cancer Variant Interpreter -> Tumor mutations generating neoantigens driving TIL expansion

**"Compare BCR repertoires pre- and post-vaccination to assess immune response"**
1. Immune Repertoire Analysis -> Paired comparison: diversity changes, new expanded clonotypes, SHM rate, isotype switching
2. Gene Enrichment -> Pathway analysis of genes linked to vaccine-responsive clonotype clusters
3. Disease Research -> Known antigenic targets for the pathogen

**"Track minimal residual disease in ALL using repertoire sequencing"**
1. Immune Repertoire Analysis -> MRD tracking: identify diagnostic clonotype, quantify at follow-ups
2. Clinical Trial Analyst -> Active trials using repertoire-based MRD monitoring
3. Precision Medicine Stratifier -> Risk stratification from MRD kinetics

**"Characterize TCR diversity in autoimmune disease tissue biopsies"**
1. Immune Repertoire Analysis -> Clonotype analysis, diversity comparison, public clonotype identification
2. Disease Research -> Known autoantigens and associated TCR sequences
3. Single-Cell Analysis -> Integrate VDJ with transcriptomic profiles of infiltrating T cells

## Completeness Checklist

- [ ] Data format detected and loaded correctly (AIRR, MiXCR, immunoSEQ, 10x VDJ)
- [ ] Productive sequences filtered and non-productive removed
- [ ] Clonotype definition method documented (CDR3-only vs CDR3+V+J)
- [ ] Diversity metrics calculated (Shannon, Simpson, Chao1, evenness)
- [ ] V(D)J gene usage plotted and V-J pairing heatmap generated
- [ ] CDR3 length distribution and amino acid composition analyzed
- [ ] Clonal expansion categories quantified with Gini coefficient
- [ ] Repertoire overlap computed if multiple samples present
- [ ] Evidence tier assigned to all key findings (T1-T4)
- [ ] Report file created with all sections populated (no `[Analyzing...]` remaining)
