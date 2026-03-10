# PhyKIT Recipes

Computational recipes for PhyKIT phylogenomic analyses. Each recipe: CLI command + Python parsing + output format + pitfalls.

Cross-skill routing:
- `phylogenetics` — conceptual guidance, study design
- `biostat-recipes` — statistical tests beyond what's here
- `alignment-recipes` — upstream alignment and trimming

---

## 1. Treeness (Stemminess)

Proportion of total tree length on internal branches. Higher = stronger phylogenetic signal.

```bash
phykit treeness <tree_file>
# Output: single float, e.g. 0.4523
```

```python
import subprocess

def get_treeness(tree_file: str) -> float:
    result = subprocess.run(
        ["phykit", "treeness", tree_file],
        capture_output=True, text=True, check=True
    )
    return float(result.stdout.strip())

# Example
treeness = get_treeness("gene1.tre")
print(f"Treeness: {treeness:.4f}")
# Values > 0.5 suggest strong signal; < 0.2 suggest noise/saturation
```

**Pitfalls:**
- Requires rooted or unrooted Newick tree
- Polytomies (zero-length branches) deflate treeness
- NaN if tree has no internal branches

---

## 2. DVMC — Degree of Violation of Molecular Clock

Measures how clock-like a tree is. Lower = more clock-like.

```bash
phykit dvmc -t <tree_file> -r <root_taxa>
# root_taxa: file with one taxon name per line (outgroup taxa)
# Output: single float, e.g. 0.312
```

```python
import subprocess
import tempfile

def get_dvmc(tree_file: str, root_taxa: list[str]) -> float:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("\n".join(root_taxa))
        root_file = f.name
    result = subprocess.run(
        ["phykit", "dvmc", "-t", tree_file, "-r", root_file],
        capture_output=True, text=True, check=True
    )
    return float(result.stdout.strip())

# Example
dvmc = get_dvmc("gene1.tre", ["outgroup_sp1", "outgroup_sp2"])
print(f"DVMC: {dvmc:.4f}")
```

**Pitfalls:**
- Root taxa must match tree tip labels exactly (case-sensitive)
- Fails if root taxa not found in tree
- Values near 0 = clock-like; values near 1 = strong rate variation

---

## 3. RCV — Relative Composition Variability

Detects compositional heterogeneity across taxa. Higher = more heterogeneous.

```bash
phykit rcv -a <alignment_file>
# Output: single float, e.g. 0.0534
```

```python
import subprocess

def get_rcv(alignment_file: str) -> float:
    result = subprocess.run(
        ["phykit", "rcv", "-a", alignment_file],
        capture_output=True, text=True, check=True
    )
    return float(result.stdout.strip())

rcv = get_rcv("gene1.aln")
print(f"RCV: {rcv:.4f}")
# High RCV (> 0.1-0.2) suggests compositional bias may mislead phylogeny
```

**Pitfalls:**
- Input must be aligned FASTA (not unaligned)
- Gaps treated as missing data
- Sensitive to taxon sampling — uneven sampling inflates RCV

---

## 4. Evolutionary Rate

Branch length divided by alignment length (substitutions per site).

```bash
phykit evo_rate -t <tree_file> -a <alignment_file>
# aliases: evolutionary_rate, evo_rate
# Output: single float
```

```python
import subprocess

def get_evo_rate(tree_file: str, alignment_file: str) -> float:
    result = subprocess.run(
        ["phykit", "evo_rate", "-t", tree_file, "-a", alignment_file],
        capture_output=True, text=True, check=True
    )
    return float(result.stdout.strip())

rate = get_evo_rate("gene1.tre", "gene1.aln")
print(f"Evolutionary rate: {rate:.6f}")
```

**Pitfalls:**
- Tree and alignment must correspond (same taxa)
- Rate = total_tree_length / alignment_length
- Mismatched files produce wrong results silently

---

## 5. Tree Length

Sum of all branch lengths.

```bash
phykit tree_length <tree_file>
# aliases: tl
# Output: single float
```

```python
import subprocess

def get_tree_length(tree_file: str) -> float:
    result = subprocess.run(
        ["phykit", "tree_length", tree_file],
        capture_output=True, text=True, check=True
    )
    return float(result.stdout.strip())

tl = get_tree_length("gene1.tre")
print(f"Tree length: {tl:.4f}")
```

**Pitfalls:**
- Very long trees may indicate alignment errors or long-branch attraction
- Compare across genes after normalizing by alignment length (= evo_rate)

---

## 6. Patristic Distances

Pairwise tip-to-tip distances through the tree.

```bash
phykit patristic_distances <tree_file>
# Output: tab-separated, one pair per line
# taxon1\ttaxon2\tdistance
```

```python
import subprocess
import pandas as pd

def get_patristic_distances(tree_file: str) -> pd.DataFrame:
    result = subprocess.run(
        ["phykit", "patristic_distances", tree_file],
        capture_output=True, text=True, check=True
    )
    rows = []
    for line in result.stdout.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) == 3:
            rows.append({
                "taxon1": parts[0],
                "taxon2": parts[1],
                "distance": float(parts[2])
            })
    return pd.DataFrame(rows)

df = get_patristic_distances("gene1.tre")
print(f"Mean patristic distance: {df['distance'].mean():.4f}")
print(f"Max patristic distance: {df['distance'].max():.4f}")

# Find most divergent pair
most_div = df.loc[df["distance"].idxmax()]
print(f"Most divergent: {most_div['taxon1']} — {most_div['taxon2']}")
```

**Pitfalls:**
- Output grows as O(n^2) with number of tips — large trees produce large output
- Distance is sum of branch lengths on the path, not genetic distance

---

## 7. Long Branch Score

Identifies potential long-branch attraction. Higher score = longer branch relative to others.

```bash
phykit long_branch_score <tree_file>
# Output: tab-separated, one taxon per line
# taxon\tscore
```

```python
import subprocess
import pandas as pd

def get_long_branch_scores(tree_file: str) -> pd.DataFrame:
    result = subprocess.run(
        ["phykit", "long_branch_score", tree_file],
        capture_output=True, text=True, check=True
    )
    rows = []
    for line in result.stdout.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) == 2:
            rows.append({"taxon": parts[0], "score": float(parts[1])})
    return pd.DataFrame(rows)

df = get_long_branch_scores("gene1.tre")
df_sorted = df.sort_values("score", ascending=False)
print("Top 5 long branches:")
print(df_sorted.head())

# Flag taxa with score > mean + 2*std
threshold = df["score"].mean() + 2 * df["score"].std()
outliers = df[df["score"] > threshold]
print(f"\nOutlier taxa (score > {threshold:.4f}):")
print(outliers)
```

**Pitfalls:**
- High scores don't always mean LBA — fast-evolving lineages are legitimately long
- Compare with saturation test to distinguish real signal from artifact

---

## 8. Saturation

Tests for substitution saturation (multiple hits). Plots patristic distance vs. uncorrected distance.

```bash
phykit saturation -a <alignment_file> -t <tree_file>
# Output: tab-separated
# uncorrected_distance\tpatristic_distance
# Plus slope info to stderr
```

```python
import subprocess
import pandas as pd

def get_saturation(alignment_file: str, tree_file: str) -> pd.DataFrame:
    result = subprocess.run(
        ["phykit", "saturation", "-a", alignment_file, "-t", tree_file],
        capture_output=True, text=True, check=True
    )
    rows = []
    for line in result.stdout.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) == 2:
            try:
                rows.append({
                    "uncorrected": float(parts[0]),
                    "patristic": float(parts[1])
                })
            except ValueError:
                continue
    return pd.DataFrame(rows)

df = get_saturation("gene1.aln", "gene1.tre")

# Compute R-squared as saturation measure
from scipy import stats
slope, intercept, r_value, p_value, std_err = stats.linregress(
    df["uncorrected"], df["patristic"]
)
print(f"Slope: {slope:.4f}, R^2: {r_value**2:.4f}")
# R^2 close to 1 = low saturation; R^2 << 1 = saturated
```

**Pitfalls:**
- Saturated genes (R^2 < 0.5) should be excluded or downweighted
- Works best with protein alignments for deep divergences

---

## 9. Parsimony Informative Sites

Count sites informative for parsimony analysis.

```bash
phykit pis <alignment_file>
# aliases: parsimony_informative_sites
# Output: two tab-separated values
# num_pis\ttotal_sites
```

```python
import subprocess

def get_pis(alignment_file: str) -> dict:
    result = subprocess.run(
        ["phykit", "pis", alignment_file],
        capture_output=True, text=True, check=True
    )
    parts = result.stdout.strip().split("\t")
    pis_count = int(parts[0])
    total = int(parts[1])
    return {
        "pis": pis_count,
        "total": total,
        "fraction": pis_count / total if total > 0 else 0.0
    }

info = get_pis("gene1.aln")
print(f"PI sites: {info['pis']}/{info['total']} ({info['fraction']:.2%})")
# Low fraction (< 5%) may lack phylogenetic signal
```

**Pitfalls:**
- Constant and singleton sites are not parsimony-informative
- Very high PI fraction in protein data may indicate alignment issues

---

## 10. Batch Processing Across Gene Trees

Run multiple PhyKIT metrics across all genes and collect into a DataFrame.

```python
import subprocess
import pandas as pd
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

def analyze_gene(tree_file: Path, aln_file: Path) -> dict:
    """Run multiple PhyKIT metrics on a single gene."""
    gene = tree_file.stem
    result = {"gene": gene}

    # Treeness
    try:
        out = subprocess.run(
            ["phykit", "treeness", str(tree_file)],
            capture_output=True, text=True, check=True
        )
        result["treeness"] = float(out.stdout.strip())
    except Exception:
        result["treeness"] = None

    # Tree length
    try:
        out = subprocess.run(
            ["phykit", "tree_length", str(tree_file)],
            capture_output=True, text=True, check=True
        )
        result["tree_length"] = float(out.stdout.strip())
    except Exception:
        result["tree_length"] = None

    # Evo rate
    try:
        out = subprocess.run(
            ["phykit", "evo_rate", "-t", str(tree_file), "-a", str(aln_file)],
            capture_output=True, text=True, check=True
        )
        result["evo_rate"] = float(out.stdout.strip())
    except Exception:
        result["evo_rate"] = None

    # RCV
    try:
        out = subprocess.run(
            ["phykit", "rcv", "-a", str(aln_file)],
            capture_output=True, text=True, check=True
        )
        result["rcv"] = float(out.stdout.strip())
    except Exception:
        result["rcv"] = None

    # PIS
    try:
        out = subprocess.run(
            ["phykit", "pis", str(aln_file)],
            capture_output=True, text=True, check=True
        )
        parts = out.stdout.strip().split("\t")
        result["pis"] = int(parts[0])
        result["total_sites"] = int(parts[1])
        result["pis_fraction"] = int(parts[0]) / int(parts[1]) if int(parts[1]) > 0 else 0
    except Exception:
        result["pis"] = None
        result["total_sites"] = None
        result["pis_fraction"] = None

    return result

# Collect all gene trees and alignments
tree_dir = Path("trees/")
aln_dir = Path("alignments/")

pairs = []
for tree_file in sorted(tree_dir.glob("*.tre")):
    aln_file = aln_dir / f"{tree_file.stem}.aln"
    if aln_file.exists():
        pairs.append((tree_file, aln_file))

# Run in parallel
with ProcessPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(lambda p: analyze_gene(*p), pairs))

df = pd.DataFrame(results)
df.to_csv("phykit_summary.csv", index=False)
print(df.describe())
```

---

## 11. Per-Group Statistics (e.g., Fungi vs Animals)

Assign genes to groups and compute per-group summaries.

```python
import pandas as pd

# Load results from batch processing
df = pd.read_csv("phykit_summary.csv")

# Define group membership (gene -> group)
# Option A: from a mapping file
group_map = pd.read_csv("gene_groups.csv")  # columns: gene, group
df = df.merge(group_map, on="gene")

# Option B: from naming convention
# df["group"] = df["gene"].apply(lambda g: "fungi" if g.startswith("FUN") else "animals")

# Per-group summary
summary = df.groupby("group").agg({
    "treeness": ["mean", "median", "std", "count"],
    "evo_rate": ["mean", "median", "std"],
    "rcv": ["mean", "median", "std"],
    "pis_fraction": ["mean", "median", "std"]
}).round(4)
print(summary)
```

---

## 12. Statistical Comparison — Mann-Whitney U

Compare PhyKIT metrics between two groups.

```python
import pandas as pd
from scipy.stats import mannwhitneyu

df = pd.read_csv("phykit_summary.csv")
# Assumes 'group' column exists (see recipe 11)

group_a = df[df["group"] == "animals"]
group_b = df[df["group"] == "fungi"]

metrics = ["treeness", "evo_rate", "rcv", "pis_fraction", "tree_length"]

results = []
for metric in metrics:
    a = group_a[metric].dropna()
    b = group_b[metric].dropna()
    if len(a) < 3 or len(b) < 3:
        continue
    stat, pval = mannwhitneyu(a, b, alternative="two-sided")
    results.append({
        "metric": metric,
        "animals_median": a.median(),
        "fungi_median": b.median(),
        "U_statistic": stat,
        "p_value": pval,
        "significant": pval < 0.05
    })

results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))

# Bonferroni correction
n_tests = len(results_df)
results_df["p_adjusted"] = results_df["p_value"] * n_tests
results_df["significant_corrected"] = results_df["p_adjusted"] < 0.05
print("\nWith Bonferroni correction:")
print(results_df[["metric", "p_value", "p_adjusted", "significant_corrected"]].to_string(index=False))
```

---

## 13. Visualization

Box plots and histograms comparing distributions across groups.

```python
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

df = pd.read_csv("phykit_summary.csv")
# Assumes 'group' column exists

metrics = ["treeness", "evo_rate", "rcv", "pis_fraction"]

# --- Box plots ---
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
for ax, metric in zip(axes.flat, metrics):
    groups = [g[metric].dropna().values for name, g in df.groupby("group")]
    labels = [name for name, g in df.groupby("group")]
    ax.boxplot(groups, labels=labels)
    ax.set_title(metric)
    ax.set_ylabel(metric)
plt.tight_layout()
plt.savefig("phykit_boxplots.png", dpi=150)
plt.close()

# --- Histograms ---
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
for ax, metric in zip(axes.flat, metrics):
    for name, g in df.groupby("group"):
        ax.hist(g[metric].dropna(), alpha=0.5, bins=20, label=name)
    ax.set_title(metric)
    ax.set_xlabel(metric)
    ax.set_ylabel("Frequency")
    ax.legend()
plt.tight_layout()
plt.savefig("phykit_histograms.png", dpi=150)
plt.close()

# --- Scatter: treeness vs evo_rate ---
fig, ax = plt.subplots(figsize=(8, 6))
for name, g in df.groupby("group"):
    ax.scatter(g["treeness"], g["evo_rate"], alpha=0.6, label=name)
ax.set_xlabel("Treeness")
ax.set_ylabel("Evolutionary Rate")
ax.set_title("Treeness vs Evolutionary Rate")
ax.legend()
plt.tight_layout()
plt.savefig("phykit_scatter.png", dpi=150)
plt.close()

print("Saved: phykit_boxplots.png, phykit_histograms.png, phykit_scatter.png")
```

---

## Quick Reference

| Metric | Command | Interpretation |
|--------|---------|---------------|
| Treeness | `phykit treeness <tree>` | >0.5 strong signal |
| DVMC | `phykit dvmc -t <tree> -r <root>` | ~0 clock-like |
| RCV | `phykit rcv -a <aln>` | >0.1 compositional bias |
| Evo rate | `phykit evo_rate -t <tree> -a <aln>` | Subs per site |
| Tree length | `phykit tree_length <tree>` | Sum branch lengths |
| Patristic dist | `phykit patristic_distances <tree>` | Pairwise tip distances |
| Long branch | `phykit long_branch_score <tree>` | LBA candidates |
| Saturation | `phykit saturation -a <aln> -t <tree>` | R^2 ~1 = unsaturated |
| PIS | `phykit pis <aln>` | PI site count/fraction |

## Install

```bash
pip install phykit
# Requires: Python >= 3.6, BioPython
```
