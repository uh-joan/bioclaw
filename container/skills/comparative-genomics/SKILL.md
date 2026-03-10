---
name: comparative-genomics
description: Cross-species genome comparison and evolutionary analysis. Ortholog inference, synteny analysis, whole-genome alignment, positive selection, dN/dS, gene family evolution, divergence time estimation. Use when user mentions comparative genomics, ortholog, synteny, genome alignment, positive selection, dN/dS, Ka/Ks, PAML, HyPhy, gene family expansion, horizontal gene transfer, ancestral reconstruction, divergence time, molecular evolution, or cross-species comparison.
---

# Comparative Genomics Analysis

Production-ready cross-species genome comparison and evolutionary analysis methodology. The agent writes and executes Python/R code for ortholog inference, synteny detection, whole-genome alignment, selection pressure analysis, gene family evolution, and divergence time estimation. Uses Open Targets, PubMed, and phylogenetic databases for biological annotation.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_comparative-genomics_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Phylogenetic tree construction from marker genes -> use `phylogenomics`
- Population genetics within a single species -> use `population-genetics`
- Metagenomics community composition -> use `metagenomics-analysis`
- Genome assembly and annotation -> use `genome-assembly`
- Variant calling against a reference -> use `variant-calling`

## Cross-Reference: Other Skills

- **Phylogenetic tree building** -> use phylogenomics skill
- **Population-level variation** -> use population-genetics skill
- **Genome annotation for new assemblies** -> use genome-assembly skill
- **Gene enrichment of expanded families** -> use gene-enrichment skill

## Python Environment

Standard scientific Python: `numpy, pandas, scipy, matplotlib, seaborn, biopython, ete3`. For specialized tools, install at runtime: `subprocess.run(["pip", "install", "ete3"], check=True)`.

## Data Input Formats

```python
import pandas as pd
import numpy as np
from pathlib import Path
from Bio import SeqIO

def load_proteomes(proteome_dir):
    """Load proteome FASTA files for ortholog inference."""
    proteomes = {}
    for fasta in Path(proteome_dir).glob("*.fa*"):
        species = fasta.stem
        seqs = list(SeqIO.parse(str(fasta), "fasta"))
        proteomes[species] = seqs
        print(f"  {species}: {len(seqs):,} proteins")
    return proteomes

def load_ortholog_table(orthogroups_file):
    """Load OrthoFinder Orthogroups.tsv output."""
    df = pd.read_csv(orthogroups_file, sep="\t", index_col=0)
    n_groups = len(df)
    n_species = len(df.columns)
    single_copy = df.dropna().apply(lambda row: all(
        "," not in str(v) and str(v) != "nan" for v in row), axis=1).sum()
    print(f"Orthogroups: {n_groups:,}")
    print(f"Species: {n_species}")
    print(f"Single-copy orthogroups: {single_copy:,}")
    return df
```

---

## Analysis Pipeline

### Phase 1: Ortholog Inference

```python
def orthofinder_workflow(proteome_dir, output_dir="orthofinder_out", threads=8):
    """OrthoFinder: comprehensive ortholog inference pipeline."""
    cmd = f"""
    orthofinder -f {proteome_dir} \\
        -t {threads} \\
        -a {threads} \\
        -S diamond \\
        -M msa \\
        -o {output_dir}
    """

    print("OrthoFinder Workflow:")
    print("=" * 50)
    print("  1. All-vs-all DIAMOND BLASTP (sequence similarity)")
    print("  2. Normalize BLAST scores by gene length")
    print("  3. MCL clustering of reciprocal best hits into orthogroups")
    print("  4. Infer species tree from single-copy orthologs")
    print("  5. Root species tree and infer gene duplication events")
    print("  6. Classify orthologs, paralogs, and co-orthologs")
    print()
    print("Key Parameters:")
    print("  -S diamond: Sequence search program (diamond > blast for speed)")
    print("  -M msa: Multiple sequence alignment method for tree inference")
    print("  -I 1.5: MCL inflation parameter (1.1=broad clusters, 5.0=tight)")
    print("     Default 1.5 is good for most analyses")
    print("     Increase for closely related species (avoid merging paralogs)")
    print("     Decrease for distant species (allow divergent orthologs)")
    print()
    print("OrthoFinder Outputs:")
    print("  Orthogroups/Orthogroups.tsv: Gene membership per orthogroup")
    print("  Orthogroups/Orthogroups_SingleCopyOrthologues.txt: 1:1 orthologs")
    print("  Comparative_Genomics/Duplications_per_Orthogroup.tsv: Duplication events")
    print("  Orthologues/: Pairwise ortholog files per species pair")
    print("  Species_Tree/SpeciesTree_rooted.txt: Inferred species tree")
    return cmd

def proteinortho_workflow(proteome_files, output_prefix="proteinortho"):
    """ProteinOrtho: alternative ortholog detection for many species."""
    files_str = " ".join(proteome_files)
    cmd = f"""
    proteinortho \\
        -project={output_prefix} \\
        -cpus=8 \\
        -e=1e-05 \\
        -conn=0.1 \\
        -identity=25 \\
        -cov=50 \\
        -selfblast \\
        -singles \\
        {files_str}
    """

    print("ProteinOrtho vs OrthoFinder:")
    print("  ProteinOrtho: Faster for many species (>20), graph-based clustering")
    print("  OrthoFinder: Better accuracy, phylogeny-aware, standard choice")
    print("  Recommendation: OrthoFinder for <= 20 species, ProteinOrtho for more")
    return cmd
```

### Phase 2: Synteny Analysis

```python
def mcscanx_workflow(gff_files, blast_file, output_prefix="synteny"):
    """MCScanX: collinear gene block detection."""
    cmd = f"""
    # Step 1: Prepare input files
    # GFF format: species_id  gene_id  chrom  start  end
    # BLAST format: all-vs-all BLASTP (outfmt 6)

    # Step 2: Run MCScanX
    MCScanX {output_prefix}
    # Input files: {output_prefix}.gff and {output_prefix}.blast

    # Step 3: Downstream analysis
    MCScanX_h -a -b 2 {output_prefix}         # Synteny dot plot
    dissect_multiple_alignment {output_prefix}  # Pairwise synteny blocks
    """

    print("MCScanX Parameters:")
    print("  -k 50: Max gaps allowed in collinear blocks")
    print("  -g -1: Max gap between hits (-1 = automatic)")
    print("  -s 5: Minimum number of genes per block")
    print("  -e 1e-05: E-value threshold")
    print("  -m 25: Max gene pairs per match")
    print()
    print("Synteny Classification:")
    print("  Intra-species synteny -> WGD (whole-genome duplication) detection")
    print("  Inter-species synteny -> Conserved gene order (shared ancestry)")
    print("  Tandem duplications: Adjacent gene copies (same block)")
    print("  Dispersed duplications: Gene copies in different blocks")
    print()
    print("SyMAP alternative: better for large genomes, interactive visualization")
    print("  Particularly suited for plant genomes (polyploidy)")

def synteny_visualization(synteny_blocks, species_a, species_b, output="synteny_plot.png"):
    """Visualize synteny blocks between two species."""
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    fig, ax = plt.subplots(figsize=(14, 10))

    print("Visualization options:")
    print("  Dot plot: Gene positions species A (x) vs species B (y)")
    print("    - Diagonal = conserved order")
    print("    - Anti-diagonal = inversion")
    print("    - Parallel diagonals = duplication (WGD)")
    print("  Circos: Ribbon connections between chromosomes")
    print("  Microsynteny: Detailed gene-level view of a specific block")

    ax.set_xlabel(f"{species_a} genomic position")
    ax.set_ylabel(f"{species_b} genomic position")
    ax.set_title(f"Synteny: {species_a} vs {species_b}")
    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches="tight")
    plt.show()
```

### Phase 3: Whole-Genome Alignment

```python
def minimap2_genome_alignment(query_fa, reference_fa, preset="asm5"):
    """Whole-genome alignment with minimap2."""
    cmd = f"""
    minimap2 -a -x {preset} \\
        --eqx \\
        -t 8 \\
        {reference_fa} {query_fa} \\
        | samtools sort -o aligned.bam
    samtools index aligned.bam
    """

    print("minimap2 Presets for Genome Comparison:")
    print("=" * 50)
    print("  asm5:  < 5% sequence divergence (same species, e.g., human haplotypes)")
    print("  asm10: 5-10% divergence (closely related species, e.g., human-chimp)")
    print("  asm20: 10-20% divergence (moderately diverged, e.g., human-mouse)")
    print("  splice: For cDNA-to-genome alignment (NOT genome-to-genome)")
    print()
    print("  Decision tree:")
    print("  +-- Same species or subspecies? -> asm5")
    print("  +-- Same genus? -> asm10")
    print("  +-- Same family/order? -> asm20")
    print("  +-- More divergent? -> nucmer (MUMmer) may be more appropriate")
    return cmd

def nucmer_alignment(query_fa, reference_fa, output_prefix="nucmer_out"):
    """MUMmer/nucmer for whole-genome alignment and comparison."""
    cmd = f"""
    # Step 1: Align
    nucmer --maxmatch -c 100 -l 20 \\
        -p {output_prefix} \\
        {reference_fa} {query_fa}

    # Step 2: Filter alignments
    delta-filter -m -i 90 -l 1000 \\
        {output_prefix}.delta > {output_prefix}.filtered.delta

    # Step 3: Generate coordinates
    show-coords -rcl {output_prefix}.filtered.delta > {output_prefix}.coords

    # Step 4: Generate SNPs
    show-snps -Clr {output_prefix}.filtered.delta > {output_prefix}.snps

    # Step 5: Dot plot
    mummerplot --fat --filter --png \\
        -p {output_prefix} \\
        {output_prefix}.filtered.delta
    """

    print("nucmer Parameters:")
    print("  --maxmatch: Use all anchor matches (not just unique)")
    print("  -c 100: Minimum cluster length")
    print("  -l 20: Minimum MUM length")
    print("  delta-filter options:")
    print("    -m: Many-to-many mapping (allow duplications)")
    print("    -1: 1-to-1 mapping (unique best alignment)")
    print("    -i 90: Minimum identity (%)")
    print("    -l 1000: Minimum alignment length")
    return cmd
```

### Phase 4: Positive Selection Analysis

```python
def paml_codeml_branch_site(alignment_file, tree_file, foreground_branch):
    """PAML codeml branch-site model for positive selection."""
    # Model A (alternative): allows positive selection on foreground branch
    control_alt = f"""
    seqfile = {alignment_file}
    treefile = {tree_file}
    outfile = codeml_branch_site_alt.out
    noisy = 0
    verbose = 1
    runmode = 0
    seqtype = 1          * codon sequences
    CodonFreq = 2        * F3x4 codon frequency model
    model = 2            * branch-specific model
    NSsites = 2          * branch-site model
    icode = 0            * universal genetic code
    fix_omega = 0        * estimate omega
    omega = 1.5          * initial omega
    fix_kappa = 0
    kappa = 2
    fix_alpha = 1
    alpha = 0
    cleandata = 1
    """

    # Model A null: omega fixed at 1 on foreground
    control_null = f"""
    seqfile = {alignment_file}
    treefile = {tree_file}
    outfile = codeml_branch_site_null.out
    noisy = 0
    verbose = 1
    runmode = 0
    seqtype = 1
    CodonFreq = 2
    model = 2
    NSsites = 2
    icode = 0
    fix_omega = 1        * fix omega = 1 (null hypothesis)
    omega = 1
    fix_kappa = 0
    kappa = 2
    fix_alpha = 1
    alpha = 0
    cleandata = 1
    """

    print("PAML Branch-Site Model:")
    print("=" * 50)
    print(f"  Foreground branch: {foreground_branch}")
    print("  H0 (null): omega = 1 on foreground (neutral)")
    print("  H1 (alt): omega free on foreground (positive selection possible)")
    print("  LRT: 2 * (lnL_alt - lnL_null) ~ chi2(df=1)")
    print("  Significance: p < 0.05 after FDR correction")
    print()
    print("  Posterior probability of positive selection (BEB):")
    print("    BEB > 0.95: Strong evidence for positive selection at specific sites")
    print("    BEB > 0.99: Very strong evidence")
    print()
    print("  CRITICAL: Alignment quality affects results profoundly")
    print("    - Use PRANK for codon alignment (preserves indel info)")
    print("    - Remove poorly aligned regions with Gblocks or GUIDANCE2")
    print("    - Minimum 6 species for reliable branch-site tests")
    print("    - Check for recombination (GARD in HyPhy) before running")
    return control_alt, control_null

def hyphy_selection_tests(alignment_file, tree_file):
    """HyPhy selection analysis methods."""
    cmds = {
        "MEME": f"""
        # MEME: Mixed Effects Model of Evolution
        # Detects episodic positive selection (site-level, any branch)
        hyphy meme --alignment {alignment_file} \\
            --tree {tree_file} \\
            --output meme_results.json
        # Interpretation: p < 0.05 at a site -> episodic positive selection
        # Advantage over PAML: Detects selection even if not on a priori branch
        """,

        "BUSTED": f"""
        # BUSTED: Branch-site Unrestricted Statistical Test for Episodic Diversification
        # Tests for gene-wide positive selection on foreground branches
        hyphy busted --alignment {alignment_file} \\
            --tree {tree_file} \\
            --branches Foreground \\
            --output busted_results.json
        # Interpretation: p < 0.05 -> evidence of positive selection somewhere in gene
        # Does NOT identify specific sites (use MEME or BEB for that)
        """,

        "aBSREL": f"""
        # aBSREL: adaptive Branch-Site Random Effects Likelihood
        # Tests each branch for positive selection (no a priori hypothesis)
        hyphy absrel --alignment {alignment_file} \\
            --tree {tree_file} \\
            --output absrel_results.json
        # Corrected p < 0.05 per branch -> positive selection on that lineage
        # Exploratory: tests all branches, corrects for multiple testing
        """,

        "FEL": f"""
        # FEL: Fixed Effects Likelihood
        # Site-level selection (pervasive, not episodic)
        hyphy fel --alignment {alignment_file} \\
            --tree {tree_file} \\
            --output fel_results.json
        # p < 0.05: pervasive positive (dN > dS) or negative (dN < dS) selection
        """,
    }

    print("Selection Test Decision Tree:")
    print("  +-- Do you have a specific foreground branch?")
    print("  |   +-- YES: PAML branch-site OR BUSTED (gene-wide) + MEME (site-level)")
    print("  |   +-- NO: aBSREL (all branches) + MEME (all sites)")
    print("  +-- Are you looking for:")
    print("  |   +-- Episodic selection (some lineages): MEME")
    print("  |   +-- Pervasive selection (all lineages): FEL or SLAC")
    print("  |   +-- Gene-wide evidence: BUSTED")
    print("  +-- Relaxed vs intensified selection:")
    print("      +-- RELAX (HyPhy): Tests for relaxation of selection intensity")
    return cmds
```

### Phase 5: dN/dS Ratio Calculation

```python
def calculate_dnds(cds_alignment_file, method="yn00"):
    """Calculate pairwise dN/dS ratios."""
    if method == "yn00":
        control = f"""
        seqfile = {cds_alignment_file}
        outfile = yn00_results.out
        verbose = 0
        icode = 0        * universal code
        weighting = 0
        commonf3x4 = 0
        """
        print("yn00 (Yang & Nielsen 2000):")
        print("  Pairwise dN/dS estimation")
        print("  No phylogenetic tree required")
        print("  Good for initial screening")

    print()
    print("dN/dS Interpretation:")
    print("=" * 50)
    print("  omega (dN/dS) < 1: Purifying (negative) selection")
    print("    0.0-0.1: Strong purifying selection (essential genes)")
    print("    0.1-0.3: Moderate purifying selection")
    print("    0.3-0.8: Weak purifying selection or partial constraint")
    print("  omega = 1: Neutral evolution")
    print("  omega > 1: Positive (diversifying) selection")
    print("    1.0-2.0: Moderate positive selection")
    print("    > 2.0: Strong positive selection")
    print()
    print("  CAUTION: Gene-wide dN/dS rarely exceeds 1 even under positive selection")
    print("  because most sites are under purifying selection.")
    print("  Use site-specific or branch-site models for better detection.")
    print()
    print("  Saturation: dS > 2-3 indicates substitution saturation")
    print("  (synonymous sites have turned over multiple times)")
    print("  Comparisons with saturated dS are unreliable")

def codon_alignment(protein_alignment, cds_fasta, output="codon_alignment.fa"):
    """Create codon-aware alignment from protein alignment and CDS sequences."""
    print("Codon alignment workflow:")
    print("  1. Align protein sequences (MAFFT, MUSCLE, PRANK)")
    print("  2. Back-translate to codon alignment using PAL2NAL or tranalign")
    print("  3. Remove poorly aligned regions (Gblocks, trimAl)")
    print()
    cmd = f"""
    # PAL2NAL: protein alignment -> codon alignment
    pal2nal.pl {protein_alignment} {cds_fasta} \\
        -output fasta \\
        -nogap \\
        -codontable 1 \\
        > {output}
    """
    print("  CRITICAL: Protein alignment first, then back-translate")
    print("  Never align CDS directly (frameshifts cause catastrophic errors)")
    return cmd
```

### Phase 6: Gene Family Evolution

```python
def cafe5_analysis(gene_counts, species_tree, output_dir="cafe5_out"):
    """CAFE5: gene family expansion and contraction analysis."""
    cmd = f"""
    cafe5 \\
        -i {gene_counts} \\
        -t {species_tree} \\
        -o {output_dir} \\
        -p \\
        -k 3
    """

    print("CAFE5 Analysis:")
    print("=" * 50)
    print("  Input: Gene family size table (orthogroups x species)")
    print("  Model: Birth-death process along phylogeny")
    print("  Tests whether gene family size changes exceed neutral expectation")
    print()
    print("  Parameters:")
    print("    -k 3: Number of rate categories (gamma-distributed lambda)")
    print("    -p: Poisson model for error in gene count estimation")
    print("    Lambda: Birth-death rate parameter")
    print("      Single lambda: same rate across tree")
    print("      Multiple lambda: different rates for different clades")
    print()
    print("  Interpretation:")
    print("    Rapidly evolving families: p < 0.05 (family-level test)")
    print("    Branch-specific changes: significant expansion or contraction")
    print("    Viterbi assignments: most likely ancestral gene counts")
    print()
    print("  Input preparation:")
    print("    1. Run OrthoFinder to get orthogroups")
    print("    2. Count genes per species per orthogroup")
    print("    3. Filter: remove families > 100 genes (computational limit)")
    print("    4. Species tree must be ultrametric (branch lengths = time)")
    print("    5. Use r8s or MCMCtree to time-calibrate the tree")
    return cmd

def ancestral_reconstruction(alignment_file, tree_file, method="iqtree"):
    """Ancestral sequence reconstruction."""
    if method == "iqtree":
        cmd = f"""
        iqtree -s {alignment_file} \\
            -te {tree_file} \\
            -m LG+G4 \\
            -asr \\
            -nt AUTO
        """
        print("IQ-TREE ancestral reconstruction:")
        print("  -asr: Ancestral State Reconstruction (marginal)")
        print("  Output: .state file with posterior probabilities per site per node")
        print("  Use marginal reconstruction (not joint) for accuracy")

    elif method == "paml":
        control = f"""
        seqfile = {alignment_file}
        treefile = {tree_file}
        outfile = rst
        RateAncestor = 1      * ancestral reconstruction
        model = 3              * empirical+F model
        fix_alpha = 0
        alpha = 0.5
        """
        print("PAML baseml/codeml ancestral reconstruction:")
        print("  RateAncestor=1 activates marginal reconstruction")
        print("  Output in 'rst' file: ancestral sequences at each node")

    print()
    print("Applications of ancestral reconstruction:")
    print("  1. Infer ancestral protein function (resurrection studies)")
    print("  2. Track amino acid substitutions along lineages")
    print("  3. Identify convergent substitutions")
    print("  4. Map substitutions to protein structure")
    return cmd if method == "iqtree" else control
```

### Phase 7: Divergence Time Estimation

```python
def mcmctree_dating(alignment, tree, calibrations):
    """MCMCtree: Bayesian divergence time estimation."""
    control = f"""
    seed = -1
    seqfile = {alignment}
    treefile = {tree}
    outfile = mcmctree.out
    ndata = 1
    seqtype = 2           * amino acids
    usedata = 2           * approximate likelihood (faster)
    clock = 2             * independent rates (relaxed clock)
    model = 0             * JC69 for approx likelihood
    BDparas = 1 1 0.1     * birth-death-sampling parameters
    rgene_gamma = 2 20    * prior on rate (gamma distribution)
    sigma2_gamma = 1 10   * prior on rate variance
    burnin = 50000
    sampfreq = 10
    nsample = 20000
    """

    print("MCMCtree Divergence Time Estimation:")
    print("=" * 50)
    print("  Calibration points (CRITICAL):")
    print("    Format in tree: '>0.5<1.0' (bounds in 100 Myr)")
    print("    Minimum 2-3 calibrations for reliable estimates")
    print("    Sources: TimeTree.org, fossil record, geological events")
    print()
    print("  Clock models:")
    print("    clock=1: Strict clock (all lineages same rate, rarely appropriate)")
    print("    clock=2: Independent rates (uncorrelated relaxed clock)")
    print("    clock=3: Autocorrelated rates (correlated relaxed clock)")
    print("    Recommendation: clock=2 for most analyses")
    print()
    print("  Workflow:")
    print("    1. Prepare alignment and calibrated tree")
    print("    2. Run usedata=3 (gradient/Hessian calculation)")
    print("    3. Run usedata=2 (approximate likelihood MCMC)")
    print("    4. Check convergence: run 2+ independent chains, compare")
    print("    5. Summarize: posterior means and 95% HPD intervals")
    print()
    print("  RelTime (IQ-TREE/MEGA) alternative:")
    print("    - Faster, non-Bayesian")
    print("    - iqtree -s aln.fa -te tree.nwk -te calibrations.txt --date-ci 100")
    print("    - Good for preliminary estimates or large datasets")
    return control
```

### Phase 8: Genome-Wide Conservation

```python
def conservation_scores(alignment_maf, reference_species):
    """Calculate phastCons and phyloP conservation scores."""
    cmds = f"""
    # phastCons: Conservation probability (0-1)
    # Identifies conserved elements (constrained regions)
    phastCons {alignment_maf} \\
        --target-coverage 0.3 \\
        --expected-length 45 \\
        --rho 0.3 \\
        model.mod \\
        --seqname {reference_species} \\
        --most-conserved conserved_elements.bed \\
        > phastCons_scores.wig

    # phyloP: Per-base conservation/acceleration
    # Positive = conservation, Negative = acceleration
    phyloP --method LRT \\
        --mode CON \\
        model.mod \\
        {alignment_maf} \\
        > phyloP_scores.wig
    """

    print("phastCons vs phyloP:")
    print("=" * 50)
    print("  phastCons:")
    print("    - HMM-based: probability of being in a conserved element")
    print("    - Range: 0 (not conserved) to 1 (conserved)")
    print("    - Outputs: per-base scores AND conserved element calls")
    print("    - Good for: identifying conserved non-coding elements (CNEs)")
    print()
    print("  phyloP:")
    print("    - Per-base test of neutral evolution")
    print("    - Positive: conservation (slower than neutral)")
    print("    - Negative: acceleration (faster than neutral)")
    print("    - Useful for: identifying accelerated regions (HARs)")
    print()
    print("  Pre-computed scores available:")
    print("    UCSC: hg38.phastCons100way, hg38.phyloP100way")
    print("    Use bigWigToBedGraph for extraction")
    return cmds

def hgt_detection(genome_fasta, protein_fasta, reference_genomes):
    """Horizontal gene transfer detection methods."""
    print("HGT Detection Methods:")
    print("=" * 50)
    print()
    print("1. Compositional methods (parametric):")
    print("   - GC content deviation: HGT genes often differ in GC%")
    print("     Threshold: > 2 SD from genome mean GC%")
    print("   - Codon usage bias: CAI (Codon Adaptation Index)")
    print("     HGT genes have atypical codon usage")
    print("   - Tetranucleotide frequency: Alien Hunter, SIGI-HMM")
    print("   - Limitation: Amelioration erases signal over time")
    print()
    print("2. Phylogenetic methods (non-parametric):")
    print("   - Gene tree vs species tree incongruence")
    print("   - Unexpected phylogenetic placement (e.g., bacterial gene in eukaryote)")
    print("   - Tools: Ranger-DTL (reconciliation), T-REX")
    print("   - More reliable than compositional but computationally expensive")
    print()
    print("3. Distribution-based methods:")
    print("   - Phyletic pattern: gene present in distantly related species")
    print("     but absent in close relatives")
    print("   - ORFan genes: no homologs in any known species (possible recent HGT)")
    print()
    print("4. Combined approach (recommended):")
    print("   - Flag candidates with compositional methods")
    print("   - Validate with phylogenetic analysis")
    print("   - Check synteny: HGT genes often near mobile elements (IS, transposons)")
```

---

## Parameter Reference Tables

### Ortholog Inference Tools

| Feature | OrthoFinder | ProteinOrtho | OMA | InParanoid |
|---------|------------|-------------|-----|------------|
| **Algorithm** | MCL + phylogeny | Graph-based | Smith-Waterman | Pairwise RBH |
| **Speed** | Moderate | Fast | Slow | Moderate |
| **Species limit** | ~50 | ~200 | ~2000 | Pairwise |
| **Phylogeny-aware** | Yes | No | Yes | No |
| **Co-orthologs** | Yes | Limited | Yes | Yes |
| **Recommended for** | Standard analyses | Many species | Deep phylogeny | Quick pairwise |

### Selection Test Comparison

| Test | Level | Type | Foreground Required | Best For |
|------|-------|------|-------------------|----------|
| PAML M7 vs M8 | Site | Pervasive | No | Baseline site test |
| PAML branch-site | Branch-site | Episodic | Yes | Specific hypothesis |
| MEME (HyPhy) | Site | Episodic | No | Any-branch episodic |
| BUSTED (HyPhy) | Gene | Episodic | Optional | Gene-wide test |
| aBSREL (HyPhy) | Branch | Episodic | No | Exploratory |
| FEL (HyPhy) | Site | Pervasive | No | Pervasive site selection |
| RELAX (HyPhy) | Gene | Intensity | Yes | Relaxation of constraint |

---

## Evidence Grading

| Tier | Evidence Type | Example |
|------|-------------|---------|
| **T1** | Experimentally validated | Functional study of positively selected gene |
| **T2** | Multiple method concordance | PAML + HyPhy agreeing on same sites |
| **T3** | Single method, well-powered | Branch-site test with >= 10 species |
| **T4** | Exploratory / low power | Pairwise dN/dS or < 6 species |

---

## Multi-Agent Workflow Examples

**"Identify genes under positive selection in primates vs other mammals"**
1. Comparative Genomics -> OrthoFinder for 1:1 orthologs, codon alignment, PAML branch-site + HyPhy MEME
2. Gene Enrichment -> GO/pathway enrichment of positively selected genes
3. Disease Research -> Link positively selected genes to human disease phenotypes

**"Detect whole-genome duplication events in a plant genome"**
1. Comparative Genomics -> Self-synteny with MCScanX, Ks distribution of paralogs
2. Phylogenomics -> Gene tree reconciliation to date WGD event
3. Gene Enrichment -> Functional bias in retained duplicates

**"Compare genome organization between two newly sequenced species"**
1. Comparative Genomics -> Whole-genome alignment (minimap2/nucmer), synteny blocks
2. Genome Assembly -> Assess assembly completeness (BUSCO) before comparison
3. Gene Enrichment -> Genes in rearranged vs conserved regions

## Completeness Checklist

- [ ] Ortholog inference performed (OrthoFinder or equivalent)
- [ ] Single-copy orthologs identified for downstream analysis
- [ ] Synteny analysis if genome-level comparison needed
- [ ] Codon-aware alignment prepared for selection analysis
- [ ] Selection tests run with appropriate model (branch-site/site/branch)
- [ ] dN/dS ratios calculated and interpreted with saturation check
- [ ] Gene family expansion/contraction tested (CAFE5) if relevant
- [ ] Species tree validated against known phylogeny
- [ ] Multiple testing correction applied (FDR)
- [ ] Evidence tier assigned to all key findings (T1-T4)
- [ ] Report file created with all sections populated (no `[Analyzing...]` remaining)
