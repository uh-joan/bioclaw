---
name: phylogenetics
description: Phylogenetic and molecular evolution analysis. Sequence alignment, phylogenetic tree construction, molecular clock, divergence dating, ancestral sequence reconstruction, pathogen phylogenomics, Newick tree parsing, distance matrices, substitution models. Use when user mentions phylogenetics, phylogenetic tree, molecular evolution, sequence alignment, divergence, molecular clock, ancestral reconstruction, Newick, cladogram, bootstrap, maximum likelihood tree, neighbor joining, pathogen evolution, or viral phylogenomics.
---

# Phylogenetics Analysis

Phylogenetic inference and molecular evolution. The agent writes and executes Python code for sequence parsing, distance calculation, tree construction (NJ, UPGMA, parsimony), bootstrap evaluation, molecular clock estimation, and visualization. All algorithms implemented from scratch using numpy, scipy, pandas, matplotlib (no BioPython/ete3/DendroPy).

## Report-First Workflow

1. **Create report file immediately**: `[taxon]_phylogenetics_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Genomic variant calling and population genetics → use `variant-analysis`
- Pathogen identification and antimicrobial resistance profiling → use `infectious-disease-analyst`
- Protein 3D structure and domain analysis → use `protein-structure-retrieval`
- Sequence retrieval without phylogenetic analysis → use `sequence-retrieval`
- Gene enrichment or pathway analysis → use `gene-enrichment`

## Available MCP Tools

### `mcp__ensembl__ensembl_data` (Genomic Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `lookup_gene` | Get gene info by ID or symbol | `gene_id`, `species`, `expand` |
| `get_gene_tree` | Get phylogenetic gene tree | `gene_id`, `format` |
| `get_homologs` | Get gene homologs across species | `gene_id`, `target_species`, `type` |
| `get_sequence` | Get genomic/transcript sequence | `region`, `species`, `format`, `mask` |
| `get_cds_sequence` | Get coding sequence | `transcript_id` |
| `batch_sequence_fetch` | Batch fetch up to 50 sequences | `regions` |

## Python Environment

Python 3 with numpy, scipy, pandas, matplotlib, and standard library. No BioPython, ete3, or DendroPy.

## Data Input Formats

**FASTA:** `>` headers followed by sequence lines. DNA/RNA/protein. **Newick:** `(A:0.1,B:0.2,(C:0.3,D:0.4):0.5);` **Distance matrices:** Square/triangular with taxon labels. **Alignments:** Equal-length FASTA with `-` gaps.

---

## Analysis Pipeline

### Phase 0: Retrieve Sequences and Gene Trees from Ensembl

When working with known genes, retrieve precomputed gene trees and ortholog sequences from Ensembl before building custom trees.

```
1. mcp__ensembl__ensembl_data(method: "get_gene_tree", gene_id: "ENSG00000139618", format: "newick")
   -> Precomputed Ensembl Compara gene tree in Newick format

2. mcp__ensembl__ensembl_data(method: "get_homologs", gene_id: "ENSG00000139618", type: "orthologues")
   -> Ortholog list across species with percent identity and dN/dS

3. mcp__ensembl__ensembl_data(method: "get_cds_sequence", transcript_id: "ENST00000380152")
   -> Coding sequence for alignment and custom tree building

4. mcp__ensembl__ensembl_data(method: "batch_sequence_fetch", regions: ["homo_sapiens:7:140453100-140453200", "mus_musculus:6:145234000-145234100"])
   -> Batch fetch orthologous regions for multi-species alignment
```

### Phase 1: Sequence Input & Validation

```python
import numpy as np
import pandas as pd
from collections import Counter
import math, copy, random

DNA_ALPHA = set('ACGTN-')
PROTEIN_ALPHA = set('ACDEFGHIKLMNPQRSTVWY*X-')

def parse_fasta(fasta_path):
    """Parse FASTA into list of (name, sequence) tuples."""
    seqs, name, parts = [], None, []
    with open(fasta_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            if line.startswith('>'):
                if name is not None:
                    seqs.append((name, ''.join(parts).upper()))
                name = line[1:].split()[0]; parts = []
            else:
                parts.append(line)
    if name is not None:
        seqs.append((name, ''.join(parts).upper()))
    print(f"Parsed {len(seqs)} sequences from {fasta_path}")
    return seqs

def validate_sequences(seqs):
    """Validate sequences: detect alphabet, check lengths, report composition."""
    report = []
    for name, seq in seqs:
        chars = set(seq)
        alpha = 'DNA' if chars <= DNA_ALPHA else ('protein' if chars <= PROTEIN_ALPHA else 'unknown')
        gc = (seq.count('G') + seq.count('C')) / len(seq.replace('-','')) if alpha == 'DNA' and seq.replace('-','') else None
        report.append({'name': name, 'length': len(seq), 'alphabet': alpha,
                       'gc_content': round(gc, 4) if gc else None, 'gaps': seq.count('-')})
    df = pd.DataFrame(report)
    print(df.to_string(index=False))
    lengths = df['length'].unique()
    if len(lengths) == 1: print(f"All sequences aligned ({lengths[0]} chars).")
    else: print(f"Lengths vary ({df['length'].min()}-{df['length'].max()}). Alignment needed.")
    return df
```

### Phase 2: Pairwise Distance Calculation

```python
def hamming_distance(s1, s2):
    """Raw proportion of differing sites. Ignores gap-gap columns."""
    diffs = total = 0
    for a, b in zip(s1, s2):
        if a == '-' and b == '-': continue
        total += 1
        if a != b: diffs += 1
    return diffs / total if total > 0 else 0.0

def jukes_cantor(p):
    """JC69 correction. Returns corrected distance or inf if saturated."""
    if p >= 0.75: return float('inf')
    return -0.75 * math.log(1 - (4.0 / 3.0) * p)

def kimura_2p(s1, s2):
    """K2P distance separating transitions and transversions."""
    transitions = {('A','G'),('G','A'),('C','T'),('T','C')}
    ti = tv = total = 0
    for a, b in zip(s1, s2):
        if a == '-' or b == '-': continue
        total += 1
        if a != b:
            ti += 1 if (a, b) in transitions else 0
            tv += 1 if (a, b) not in transitions else 0
    if total == 0: return 0.0
    P, Q = ti / total, tv / total
    t1, t2 = 1 - 2*P - Q, 1 - 2*Q
    if t1 <= 0 or t2 <= 0: return float('inf')
    return -0.5 * math.log(t1) - 0.25 * math.log(t2)

def compute_distance_matrix(seqs, model='jc'):
    """Pairwise distance matrix. model: 'raw', 'jc', 'k2p'."""
    n, names = len(seqs), [s[0] for s in seqs]
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            p = hamming_distance(seqs[i][1], seqs[j][1])
            d = jukes_cantor(p) if model == 'jc' else (kimura_2p(seqs[i][1], seqs[j][1]) if model == 'k2p' else p)
            D[i,j] = D[j,i] = d
    print(pd.DataFrame(D, index=names, columns=names).round(4).to_string())
    return D, names
```

### Phase 3: Multiple Sequence Alignment

Needleman-Wunsch pairwise alignment. For production MSA use MAFFT/MUSCLE.

```python
def needleman_wunsch(seq1, seq2, match=1, mismatch=-1, gap=-2):
    """Global pairwise alignment. Returns (aligned_seq1, aligned_seq2, score)."""
    n, m = len(seq1), len(seq2)
    score = np.zeros((n+1, m+1))
    for i in range(1, n+1): score[i, 0] = i * gap
    for j in range(1, m+1): score[0, j] = j * gap
    for i in range(1, n+1):
        for j in range(1, m+1):
            s = match if seq1[i-1] == seq2[j-1] else mismatch
            score[i,j] = max(score[i-1,j-1]+s, score[i-1,j]+gap, score[i,j-1]+gap)
    aln1, aln2, i, j = [], [], n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0:
            s = match if seq1[i-1] == seq2[j-1] else mismatch
            if score[i,j] == score[i-1,j-1]+s:
                aln1.append(seq1[i-1]); aln2.append(seq2[j-1]); i -= 1; j -= 1; continue
        if i > 0 and score[i,j] == score[i-1,j]+gap:
            aln1.append(seq1[i-1]); aln2.append('-'); i -= 1; continue
        aln2.append(seq2[j-1]); aln1.append('-'); j -= 1
    return ''.join(reversed(aln1)), ''.join(reversed(aln2)), score[n, m]
```

### Phase 4: Tree Construction -- Distance Methods

```python
def upgma(D, names):
    """UPGMA tree construction. Returns Newick string."""
    n = len(names); D = D.copy().astype(float)
    clusters = {i: {'name': names[i], 'height': 0.0, 'size': 1} for i in range(n)}
    active = list(range(n)); next_id = n
    while len(active) > 1:
        min_d, mi, mj = float('inf'), -1, -1
        for ii in range(len(active)):
            for jj in range(ii+1, len(active)):
                i, j = active[ii], active[jj]
                if D[i,j] < min_d: min_d = D[i,j]; mi, mj = i, j
        new_h = min_d / 2.0
        c1, c2 = clusters[mi], clusters[mj]
        newick = f"({c1['name']}:{new_h-c1['height']:.6f},{c2['name']}:{new_h-c2['height']:.6f})"
        new_size = c1['size'] + c2['size']
        new_D = np.zeros((next_id+1, next_id+1))
        new_D[:D.shape[0], :D.shape[1]] = D
        for k in active:
            if k not in (mi, mj):
                d_new = (D[mi,k]*c1['size'] + D[mj,k]*c2['size']) / new_size
                new_D[next_id, k] = new_D[k, next_id] = d_new
        D = new_D
        clusters[next_id] = {'name': newick, 'height': new_h, 'size': new_size}
        active = [k for k in active if k not in (mi, mj)] + [next_id]; next_id += 1
    return clusters[active[0]]['name'] + ';'

def neighbor_joining(D, names):
    """Neighbor-Joining tree construction. Returns Newick string."""
    n = len(names); D = D.copy().astype(float)
    nodes = {i: names[i] for i in range(n)}
    active = list(range(n)); next_id = n
    while len(active) > 2:
        r = len(active)
        S = {i: sum(D[i,j] for j in active if j != i) for i in active}
        min_q, mi, mj = float('inf'), -1, -1
        for ii in range(len(active)):
            for jj in range(ii+1, len(active)):
                i, j = active[ii], active[jj]
                q = (r-2)*D[i,j] - S[i] - S[j]
                if q < min_q: min_q = q; mi, mj = i, j
        bl_i = max(D[mi,mj]/2.0 + (S[mi]-S[mj])/(2.0*(r-2)), 0.0)
        bl_j = max(D[mi,mj] - bl_i, 0.0)
        new_D = np.zeros((next_id+1, next_id+1))
        new_D[:D.shape[0], :D.shape[1]] = D
        for k in active:
            if k not in (mi, mj):
                new_D[next_id,k] = new_D[k,next_id] = max((D[mi,k]+D[mj,k]-D[mi,mj])/2.0, 0.0)
        D = new_D
        nodes[next_id] = f"({nodes[mi]}:{bl_i:.6f},{nodes[mj]}:{bl_j:.6f})"
        active = [k for k in active if k not in (mi, mj)] + [next_id]; next_id += 1
    i, j = active
    return f"({nodes[i]}:{D[i,j]/2:.6f},{nodes[j]}:{D[i,j]/2:.6f});"
```

### Phase 5: Tree Construction -- Character Methods

```python
def parse_newick(s):
    """Parse Newick string into nested dict: {name, branch_length, children}."""
    s = s.strip().rstrip(';')
    def _parse(s, pos):
        node = {'name': '', 'branch_length': 0.0, 'children': []}
        if s[pos] == '(':
            pos += 1
            while True:
                child, pos = _parse(s, pos)
                node['children'].append(child)
                if pos < len(s) and s[pos] == ',': pos += 1
                elif pos < len(s) and s[pos] == ')': pos += 1; break
                else: break
        label = []
        while pos < len(s) and s[pos] not in (',',')',':', ';'):
            label.append(s[pos]); pos += 1
        node['name'] = ''.join(label)
        if pos < len(s) and s[pos] == ':':
            pos += 1; bl = []
            while pos < len(s) and s[pos] not in (',',')',';'):
                bl.append(s[pos]); pos += 1
            node['branch_length'] = float(''.join(bl))
        return node, pos
    tree, _ = _parse(s, 0)
    return tree

def to_newick(node):
    """Convert tree dict to Newick string."""
    if not node['children']: s = node['name']
    else: s = f"({','.join(to_newick(c) for c in node['children'])}){node['name']}"
    if node['branch_length'] > 0: s += f":{node['branch_length']:.6f}"
    return s

def get_leaves(node):
    """Return list of leaf names."""
    if not node['children']: return [node['name']]
    return [l for c in node['children'] for l in get_leaves(c)]

def parsimony_score(tree, alignment):
    """Fitch algorithm: compute parsimony score for aligned sequences."""
    seq_len = len(next(iter(alignment.values())))
    total = 0
    for pos in range(seq_len):
        def _fitch(node):
            nonlocal total
            if not node['children']:
                ch = alignment[node['name']][pos]
                node['_s'] = {ch} if ch != '-' else set('ACGT'); return
            for c in node['children']: _fitch(c)
            sets = [c['_s'] for c in node['children']]
            inter = sets[0]
            for s in sets[1:]: inter = inter & s
            if inter: node['_s'] = inter
            else:
                node['_s'] = sets[0]
                for s in sets[1:]: node['_s'] = node['_s'] | s
                total += 1
        _fitch(tree)
    return total

def parsimony_nni_search(tree, alignment, max_iter=100):
    """Heuristic parsimony search via NNI. Returns (best_newick, best_score)."""
    best_score = parsimony_score(copy.deepcopy(tree), alignment)
    best_newick = to_newick(tree)
    for it in range(max_iter):
        candidate = copy.deepcopy(tree)
        internals = [n for n in _all_nodes(candidate) if n['children']]
        if not internals: break
        node = random.choice(internals)
        if len(node['children']) >= 2:
            l, r = node['children'][0], node['children'][1]
            if l['children'] and r['children']:
                l['children'][0], r['children'][0] = r['children'][0], l['children'][0]
        score = parsimony_score(copy.deepcopy(candidate), alignment)
        if score < best_score:
            best_score = score; best_newick = to_newick(candidate); tree = candidate
    return best_newick + ';', best_score

def _all_nodes(node):
    yield node
    for c in node['children']: yield from _all_nodes(c)
```

### Phase 6: Tree Evaluation

```python
def bootstrap_resample(alignment, n_replicates=100):
    """Resample alignment columns. alignment: {name: seq}. Returns list of dicts."""
    names = list(alignment.keys())
    seq_len = len(alignment[names[0]])
    replicates = []
    for _ in range(n_replicates):
        cols = [random.randint(0, seq_len-1) for _ in range(seq_len)]
        replicates.append({n: ''.join(alignment[n][c] for c in cols) for n in names})
    return replicates

def bootstrap_nj(seqs, model='jc', n_replicates=100):
    """NJ trees on bootstrap replicates. Returns list of Newick strings."""
    alignment = {name: seq for name, seq in seqs}
    trees = []
    for i, rep in enumerate(bootstrap_resample(alignment, n_replicates)):
        rep_seqs = [(n, rep[n]) for n in alignment]
        D, names = compute_distance_matrix(rep_seqs, model=model)
        trees.append(neighbor_joining(D, names))
        if (i+1) % 25 == 0: print(f"  Bootstrap {i+1}/{n_replicates}")
    return trees

def get_bipartitions(newick):
    """Extract bipartitions (splits) for RF distance."""
    tree = parse_newick(newick)
    all_leaves = frozenset(get_leaves(tree))
    splits = set()
    def _collect(node):
        if not node['children']: return frozenset([node['name']])
        clade = frozenset()
        for c in node['children']: clade = clade | _collect(c)
        if clade != all_leaves and len(clade) > 1:
            splits.add(frozenset([clade, all_leaves - clade]))
        return clade
    _collect(tree)
    return splits

def robinson_foulds(tree1_nwk, tree2_nwk):
    """RF distance between two trees. Returns (distance, max_possible)."""
    s1, s2 = get_bipartitions(tree1_nwk), get_bipartitions(tree2_nwk)
    return len(s1 ^ s2), len(s1) + len(s2)

def compute_bootstrap_support(ref_tree_nwk, bootstrap_trees):
    """Bootstrap support for each clade. Returns {split: fraction}."""
    ref_splits = get_bipartitions(ref_tree_nwk)
    support = {s: 0 for s in ref_splits}
    for bt in bootstrap_trees:
        bt_splits = get_bipartitions(bt)
        for s in ref_splits:
            if s in bt_splits: support[s] += 1
    n = len(bootstrap_trees)
    result = {s: count/n for s, count in support.items()}
    vals = list(result.values())
    if vals:
        print(f"Bootstrap ({len(vals)} branches): mean={np.mean(vals):.3f}, "
              f">=95%: {sum(1 for v in vals if v>=0.95)}, >=70%: {sum(1 for v in vals if v>=0.70)}")
    return result
```

### Phase 7: Visualization

```python
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

def layout_tree(node, x=0, y_counter=None):
    """Assign (x,y) coords: x=cumulative branch length, y=leaf order."""
    if y_counter is None: y_counter = [0]
    node['_x'] = x + node['branch_length']
    if not node['children']:
        node['_y'] = y_counter[0]; y_counter[0] += 1
    else:
        for c in node['children']: layout_tree(c, node['_x'], y_counter)
        node['_y'] = np.mean([c['_y'] for c in node['children']])
    return node

def draw_tree(node, ax, show_lengths=True, font_size=9):
    """Recursively draw tree branches and labels."""
    if node['children']:
        ys = [c['_y'] for c in node['children']]
        ax.plot([node['_x']]*2, [min(ys), max(ys)], 'k-', lw=1)
        for c in node['children']:
            ax.plot([node['_x'], c['_x']], [c['_y']]*2, 'k-', lw=1)
            if show_lengths and c['branch_length'] > 0:
                ax.text((node['_x']+c['_x'])/2, c['_y']+0.15,
                        f"{c['branch_length']:.4f}", fontsize=font_size-2, ha='center', color='gray')
            draw_tree(c, ax, show_lengths, font_size)
    else:
        ax.text(node['_x']+0.002, node['_y'], f" {node['name']}", fontsize=font_size, va='center')

def plot_phylogram(newick, output='phylogram.png', title='Phylogram', show_lengths=True):
    """Render Newick tree as a phylogram (proportional branch lengths)."""
    tree = layout_tree(parse_newick(newick))
    n = len(get_leaves(tree))
    fig, ax = plt.subplots(figsize=(max(8, n*0.3), max(4, n*0.4)))
    draw_tree(tree, ax, show_lengths=show_lengths)
    ax.set_title(title); ax.set_xlabel('Substitutions per site'); ax.set_yticks([])
    for s in ['top','right','left']: ax.spines[s].set_visible(False)
    plt.tight_layout(); plt.savefig(output, dpi=150, bbox_inches='tight'); plt.close()
    print(f"Tree saved to {output}")

def plot_cladogram(newick, output='cladogram.png', title='Cladogram'):
    """Render Newick tree as a cladogram (equal branch lengths)."""
    tree = parse_newick(newick)
    def _unit(n): n['branch_length'] = 1.0; [_unit(c) for c in n['children']]
    _unit(tree); layout_tree(tree)
    n = len(get_leaves(tree))
    fig, ax = plt.subplots(figsize=(max(6, n*0.3), max(4, n*0.4)))
    draw_tree(tree, ax, show_lengths=False)
    ax.set_title(title); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    plt.tight_layout(); plt.savefig(output, dpi=150, bbox_inches='tight'); plt.close()

```

---

## Substitution Models Reference

| Model | Parameters | Use When |
|-------|-----------|----------|
| **JC69** | 1 (equal base freq, single rate) | Quick estimate, closely related sequences |
| **K80 (K2P)** | 2 (Ti/Tv ratio) | Default for distance methods; corrects Ti/Tv bias |
| **HKY85** | 5 (4 base freq + Ti/Tv) | Unequal base composition + Ti/Tv bias |
| **GTR** | 9 (4 freq + 6 rates) | Most general; formal ML analysis |
| **F81** | 4 (4 base freq) | Unequal composition, no Ti/Tv bias |
| **TN93** | 6 (4 freq + 2 Ti + 1 Tv) | Different purine/pyrimidine Ti rates |

Default to K2P for NJ/UPGMA. Use HKY85 or GTR for ML. Over-parameterization is less harmful than under-correction.

```python
def jc69_rate_matrix():
    """JC69 instantaneous rate matrix Q."""
    Q = np.full((4, 4), 1/3); np.fill_diagonal(Q, -1.0)
    return Q

def k80_rate_matrix(kappa=2.0):
    """K80 rate matrix with Ti/Tv ratio kappa. Order: A, C, G, T."""
    Q = np.array([[0,1,kappa,1],[1,0,1,kappa],[kappa,1,0,1],[1,kappa,1,0]], dtype=float)
    for i in range(4): Q[i,i] = -Q[i].sum()
    scale = -np.dot(np.full(4, 0.25), np.diag(Q))
    return Q / scale

def transition_probability(Q, t):
    """P(t) = expm(Q*t) transition probability matrix."""
    from scipy.linalg import expm
    return expm(Q * t)
```

---

## Molecular Clock & Divergence Dating

Estimates divergence times from branch lengths using calibration points. **Strict clock:** constant rate across lineages. **Relaxed clock:** rate variation among branches (more realistic).

```python
def root_to_tip_regression(tree_nwk, tip_dates):
    """Root-to-tip regression for temporal signal. tip_dates: {taxon: date}.
    Returns (rate, r_squared, intercept)."""
    tree = parse_newick(tree_nwk)
    distances = {}
    def _rtt(node, dist):
        d = dist + node['branch_length']
        if not node['children']: distances[node['name']] = d
        for c in node['children']: _rtt(c, d)
    _rtt(tree, 0)
    tips = [t for t in distances if t in tip_dates]
    if len(tips) < 3: print("Too few dated tips."); return None, None, None
    x = np.array([tip_dates[t] for t in tips])
    y = np.array([distances[t] for t in tips])
    from scipy.stats import linregress
    slope, intercept, r_value, p_value, _ = linregress(x, y)
    print(f"Root-to-tip: rate={slope:.2e}, R2={r_value**2:.4f}, "
          f"tMRCA={-intercept/slope:.1f}, p={p_value:.2e}" if slope > 0 else "No temporal signal")
    return slope, r_value**2, intercept

def apply_clock(tree_nwk, rate):
    """Convert branch lengths to time units using strict clock."""
    tree = parse_newick(tree_nwk)
    def _conv(n):
        n['branch_length'] = n['branch_length'] / rate if rate > 0 else 0
        for c in n['children']: _conv(c)
    _conv(tree)
    return to_newick(tree) + ';'

def plot_root_to_tip(tree_nwk, tip_dates, output='rtt_plot.png'):
    """Plot root-to-tip distance vs sampling date with regression line."""
    tree = parse_newick(tree_nwk)
    distances = {}
    def _rtt(node, dist):
        d = dist + node['branch_length']
        if not node['children']: distances[node['name']] = d
        for c in node['children']: _rtt(c, d)
    _rtt(tree, 0)
    tips = [t for t in distances if t in tip_dates]
    x, y = np.array([tip_dates[t] for t in tips]), np.array([distances[t] for t in tips])
    from scipy.stats import linregress
    sl, ic, _, _, _ = linregress(x, y)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(x, y, alpha=0.7, edgecolors='black', lw=0.5)
    xf = np.linspace(x.min(), x.max(), 100)
    ax.plot(xf, sl*xf+ic, 'r--', alpha=0.7, label=f'Rate={sl:.2e}')
    ax.set(xlabel='Date', ylabel='Root-to-tip Distance', title='Temporal Signal')
    ax.legend(); plt.tight_layout(); plt.savefig(output, dpi=150); plt.close()
```

---

## Pathogen Phylogenomics

Outbreak investigation, transmission tracking, evolutionary surveillance. Workflow: align -> NJ tree + bootstrap -> cluster by SNP threshold -> root-to-tip -> estimate tMRCA/rate.

```python
def snp_distance_matrix(alignment):
    """SNP count matrix (raw differences excluding gaps). alignment: {name: seq}."""
    names = sorted(alignment.keys()); n = len(names)
    D = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(i+1, n):
            diffs = sum(1 for a, b in zip(alignment[names[i]], alignment[names[j]])
                        if a != '-' and b != '-' and a != b)
            D[i,j] = D[j,i] = diffs
    print("SNP distances:"); print(pd.DataFrame(D, index=names, columns=names).to_string())
    return D, names

def identify_clusters(D, names, threshold=10):
    """Single-linkage clustering by SNP threshold."""
    n, visited, clusters = len(names), [False]*len(names), []
    for i in range(n):
        if visited[i]: continue
        cluster, stack = [], [i]
        while stack:
            nd = stack.pop()
            if visited[nd]: continue
            visited[nd] = True; cluster.append(names[nd])
            stack.extend(j for j in range(n) if not visited[j] and D[nd,j] <= threshold)
        clusters.append(sorted(cluster))
    print(f"{len(clusters)} cluster(s) at {threshold} SNPs:")
    for i, c in enumerate(clusters):
        print(f"  Cluster {i+1} ({len(c)}): {', '.join(c[:5])}{'...' if len(c)>5 else ''}")
    return clusters

def detect_reassortment(tree1, tree2, names=('Seg1', 'Seg2')):
    """Compare segment trees via RF distance for reassortment."""
    rf, mx = robinson_foulds(tree1, tree2)
    nrf = rf / mx if mx > 0 else 0
    print(f"Reassortment ({names[0]} vs {names[1]}): RF={rf}/{mx}, norm={nrf:.3f}")
    if nrf > 0.3: print("  HIGH incongruence: reassortment likely.")
    elif nrf > 0.1: print("  Moderate incongruence: possible reassortment.")
    else: print("  Concordant topologies: no strong reassortment signal.")
    return rf, nrf
```

---

## Tree Interpretation Guide

| Feature | Interpretation |
|---------|---------------|
| **Branch length** | Substitutions/site. Longer = more divergence. |
| **Support** | Bootstrap >= 70% or posterior >= 0.95 = well-supported. |
| **Long branches** | Fast evolution, saturation, or long-branch attraction artifact. |
| **Short internals** | Rapid radiation; hard to resolve; expect low support. |
| **Root** | Use outgroup rooting or midpoint rooting. |
| **Polytomy** | Soft (data insufficient) or hard (true simultaneous split). |
| **Ultrametric** | All tips equidistant from root; clock-like (UPGMA output). |

**Pitfalls:** Long-branch attraction (use ML, dense sampling), compositional bias (LogDet), inadequate model (AIC/BIC), sparse sampling.

---

## Evidence Grading

| Tier | Criteria | Confidence |
|------|----------|------------|
| **T1** | >= 100 bootstraps, support >= 95%, multiple methods agree, adequate model | High |
| **T2** | >= 100 bootstraps, support >= 70%, two+ methods agree | Medium-High |
| **T3** | Single method, support >= 50%, or few replicates | Medium |
| **T4** | No bootstrap, single distance method, or poor model fit | Low |

---

## Multi-Agent Workflow Examples

**"Build a phylogenetic tree from viral sequences"**
1. Phylogenetics -> Parse FASTA, K2P distances, NJ tree, bootstrap, visualize
2. Infectious Disease Analyst -> Literature on related strains

**"Estimate divergence time of these species"**
1. Phylogenetics -> Align, build tree, root-to-tip regression, molecular clock
2. Variant Analysis -> Fixed differences between lineages

**"Investigate outbreak using pathogen genomes"**
1. Phylogenetics -> Align, SNP matrix, NJ tree, cluster, temporal signal
2. Infectious Disease Analyst -> Resistance mutations, transmission patterns

**"Compare segment phylogenies for reassortment"**
1. Phylogenetics -> Per-segment trees, RF distances, flag incongruence
2. Infectious Disease Analyst -> Reassortment history, pandemic risk

## Completeness Checklist

- [ ] Sequences parsed and validated (alphabet, length, gap content)
- [ ] Appropriate substitution model selected and justified (JC69, K2P, HKY85, GTR)
- [ ] Pairwise distance matrix computed and reported
- [ ] Tree constructed using at least one method (NJ, UPGMA, or parsimony)
- [ ] Bootstrap analysis performed (>=100 replicates) with support values reported
- [ ] Tree visualization saved as phylogram and/or cladogram image
- [ ] Evidence tier assigned (T1-T4) based on bootstrap support and method agreement
- [ ] Molecular clock or divergence dating applied if temporal data available
- [ ] Report file verified with no remaining `[Analyzing...]` placeholders
