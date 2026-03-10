---
name: metagenomics-analyst
description: Shotgun metagenomics analysis for microbial community profiling. Read QC and host decontamination with Bowtie2, taxonomic classification with Kraken2 and Bracken abundance estimation, MetaPhlAn4 marker-gene profiling, custom Kraken2 database construction, functional profiling with HUMAnN3 for UniRef to MetaCyc pathways, antimicrobial resistance gene detection with AMRFinderPlus and CARD RGI, metagenome assembly with MEGAHIT and metaSPAdes, genome binning with MetaBAT2 and MaxBin2 and CONCOCT and DAS Tool refinement, MAG quality assessment with CheckM2, strain-level tracking with StrainPhlAn and inStrain, taxonomic visualization with Krona and GraPhlAn. Use when user asks about metagenomics, shotgun metagenomics, metagenomic sequencing, microbial communities, microbiome WGS, Kraken2, Bracken, MetaPhlAn, HUMAnN, AMR genes, antimicrobial resistance, metagenome assembly, MAGs, metagenome-assembled genomes, genome binning, MetaBAT, CheckM, StrainPhlAn, inStrain, functional profiling, or community composition from whole genome sequencing.
---

# Shotgun Metagenomics Analysis

Comprehensive pipeline for whole-genome shotgun metagenomic sequencing analysis. Covers taxonomic profiling, functional characterization, metagenome assembly, genome binning, MAG quality assessment, AMR gene detection, and strain-level tracking. Distinct from 16S/ITS amplicon sequencing which targets specific marker genes.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_metagenomics_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as analysis completes
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- 16S rRNA or ITS amplicon sequencing analysis -> use `microbiome` or `amplicon-analysis`
- Metatranscriptomics (RNA-based community analysis) -> use `transcriptomics`
- Viral metagenomics (virome) -> use specialized virome pipeline
- Deep pathway enrichment on gene lists -> use `gene-enrichment`
- Single-species genome assembly -> use `genome-assembly`

## Cross-Reference: Other Skills

- **16S/ITS amplicon analysis** -> use microbiome skill
- **Genome assembly from isolate sequencing** -> use genome-assembly skill
- **Pathway enrichment on functional gene lists** -> use gene-enrichment skill
- **Phylogenetics of recovered genomes** -> use phylogenetics skill

---

## Shotgun Metagenomics vs 16S Amplicon

| Feature | Shotgun Metagenomics | 16S Amplicon |
|---------|---------------------|--------------|
| Resolution | Species/strain-level | Genus-level (V3-V4), species (V1-V2) |
| Functional data | Yes (gene content, pathways) | No (inferred only) |
| Cost per sample | Higher ($100-500) | Lower ($20-50) |
| Sequencing depth | 5-20 Gbp/sample | 50-100K reads/sample |
| Host contamination | Can be significant | Minimal (targeted amplification) |
| Database dependency | High (uncharacterized taxa missed) | Moderate (16S databases comprehensive) |
| Assembly possible | Yes (MAGs) | No |
| AMR detection | Direct gene detection | Not possible |
| Eukaryotes/viruses | Detectable | No (bacteria/archaea only) |

---

## Phase 1: Read QC and Host Decontamination

### Quality Control with fastp

```bash
# Quality trimming and adapter removal
fastp -i sample_R1.fastq.gz -I sample_R2.fastq.gz \
  -o sample_clean_R1.fastq.gz -O sample_clean_R2.fastq.gz \
  --qualified_quality_phred 20 \
  --length_required 50 \
  --cut_front --cut_tail --cut_window_size 4 --cut_mean_quality 20 \
  --detect_adapter_for_pe \
  --thread 16 \
  --json sample_fastp.json \
  --html sample_fastp.html
```

### Host Decontamination with Bowtie2

```bash
# Build host reference index (do this once)
bowtie2-build --threads 16 /ref/GRCh38_noalt.fa /ref/bowtie2/GRCh38_noalt

# Map reads against host genome
bowtie2 --very-sensitive -p 16 -x /ref/bowtie2/GRCh38_noalt \
  -1 sample_clean_R1.fastq.gz -2 sample_clean_R2.fastq.gz \
  --un-conc-gz sample_hostfree_R%.fastq.gz \
  -S /dev/null 2> sample_host_mapping.log

# Check host contamination rate
grep "overall alignment rate" sample_host_mapping.log
```

**Host contamination expectations:**

| Sample Type | Expected Host % | Action if Higher |
|-------------|----------------|------------------|
| Stool | < 5% | Normal for healthy gut |
| Skin swab | 50-90% | Normal; sequence deeper |
| Oral | 20-50% | Normal |
| BAL (lung) | 80-99% | Very high; need deep sequencing |
| Soil/water | 0% | No host decontamination needed |
| Tissue biopsy | > 95% | May need enrichment methods |

### QC Decision Tree

```
Read QC Assessment:
|
+-> Total reads after QC < 1M pairs?
|   -> Insufficient depth. Need to re-sequence.
|
+-> Host contamination > 90%?
|   -> Insufficient microbial reads. Consider:
|   -> Sequence deeper (aim for >5M microbial read pairs)
|   -> Use host depletion methods (saponin, differential lysis)
|
+-> Adapter contamination > 5% after trimming?
|   -> Check adapter sequences; re-run with explicit adapter
|
+-> Mean quality < Q20 after trimming?
|   -> Poor sequencing run; check flowcell/library QC
|
+-> Duplicate rate > 50%?
|   -> Low library complexity; check input DNA amount
```

---

## Phase 2: Taxonomic Classification

### Kraken2 + Bracken Pipeline

```bash
# Kraken2 taxonomic classification
kraken2 --db /ref/kraken2_standard \
  --paired sample_hostfree_R1.fastq.gz sample_hostfree_R2.fastq.gz \
  --output sample_kraken2.out \
  --report sample_kraken2.report \
  --confidence 0.1 \
  --threads 16

# Bracken: re-estimate abundance at species level
bracken -d /ref/kraken2_standard \
  -i sample_kraken2.report \
  -o sample_bracken_species.txt \
  -w sample_bracken_species.report \
  -r 150 \
  -l S \
  -t 10

# Bracken at genus level
bracken -d /ref/kraken2_standard \
  -i sample_kraken2.report \
  -o sample_bracken_genus.txt \
  -w sample_bracken_genus.report \
  -r 150 \
  -l G \
  -t 10
```

**Kraken2 parameters:**

| Parameter | Value | Description |
|-----------|-------|-------------|
| `--confidence` | 0.0 (default) | Fraction of k-mers mapping to a taxon required. 0.1 reduces false positives. |
| `--minimum-hit-groups` | 2 (default) | Minimum distinct minimizer groups for classification |

**Bracken parameters:**

| Parameter | Value | Description |
|-----------|-------|-------------|
| `-r` | 150 | Read length used to build k-mer distributions |
| `-l` | S, G, F, O, C, P | Taxonomic level (Species, Genus, Family, etc.) |
| `-t` | 10 | Minimum reads assigned to a taxon (filter rare taxa) |

### Custom Kraken2 Database Construction

```bash
# Build custom Kraken2 database
kraken2-build --download-taxonomy --db custom_db --threads 16

# Add reference genomes
kraken2-build --download-library bacteria --db custom_db --threads 16
kraken2-build --download-library archaea --db custom_db --threads 16
kraken2-build --download-library fungi --db custom_db --threads 16
kraken2-build --download-library viral --db custom_db --threads 16

# Add custom genomes (e.g., newly sequenced isolates)
kraken2-build --add-to-library custom_genome.fna --db custom_db

# Build the database
kraken2-build --build --db custom_db --threads 16

# Build Bracken database for the custom Kraken2 DB
bracken-build -d custom_db -t 16 -k 35 -l 150

# Clean up intermediate files
kraken2-build --clean --db custom_db
```

**Database size considerations:**

| Database | Disk Space | RAM Required | Content |
|----------|-----------|-------------|---------|
| Standard | ~70 GB | ~70 GB | RefSeq bacteria, archaea, viral, human |
| Standard-16 | ~16 GB | ~16 GB | Reduced version of Standard |
| PlusPF | ~100 GB | ~100 GB | Standard + protozoa + fungi |
| Custom (bacteria only) | ~50 GB | ~50 GB | All RefSeq bacteria |
| MinusB | ~8 GB | ~8 GB | Standard minus bacteria (for targeted) |

### MetaPhlAn4 Marker-Gene Profiling

```bash
# MetaPhlAn4 taxonomic profiling
metaphlan sample_hostfree_R1.fastq.gz,sample_hostfree_R2.fastq.gz \
  --input_type fastq \
  --nproc 16 \
  --bowtie2db /ref/metaphlan4_db \
  -o sample_metaphlan4.txt \
  --bowtie2out sample_metaphlan4.bowtie2.bz2 \
  --unclassified_estimation \
  --add_viruses

# Merge multiple sample profiles
merge_metaphlan_tables.py sample1_metaphlan4.txt sample2_metaphlan4.txt \
  > merged_metaphlan4_profiles.txt

# Generate species-level abundance table
grep "s__" merged_metaphlan4_profiles.txt | grep -v "t__" \
  > species_abundance_table.txt
```

**MetaPhlAn4 vs Kraken2 comparison:**

| Feature | MetaPhlAn4 | Kraken2 + Bracken |
|---------|-----------|-------------------|
| Method | Clade-specific marker genes | k-mer exact matching |
| Speed | Moderate | Very fast |
| RAM usage | ~1.5 GB | 16-100 GB |
| Sensitivity (novel taxa) | Lower (needs markers) | Higher (any k-mer match) |
| Specificity | Very high | Good with confidence threshold |
| Quantification | Relative abundance | Read counts (Bracken: relative) |
| Strain-level | Yes (StrainPhlAn) | No (separate tools needed) |

### Taxonomic Profile Analysis in Python

```python
import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests
from scipy.spatial.distance import braycurtis
from scipy.cluster.hierarchy import linkage, dendrogram
from skbio.diversity import alpha_diversity, beta_diversity

def load_bracken_profiles(file_list, sample_names, level='S'):
    """Load and merge Bracken output files into abundance matrix.

    Returns: taxa x samples DataFrame with relative abundance values.
    """
    all_data = {}
    for fname, sname in zip(file_list, sample_names):
        df = pd.read_csv(fname, sep='\t')
        total = df['new_est_reads'].sum()
        abundance = df.set_index('name')['new_est_reads'] / total
        all_data[sname] = abundance

    merged = pd.DataFrame(all_data).fillna(0)
    print(f"Taxa detected: {len(merged)}")
    print(f"Samples: {len(merged.columns)}")
    return merged

def alpha_diversity_analysis(abundance_matrix, metadata, group_col):
    """Calculate alpha diversity metrics and compare between groups."""
    counts = (abundance_matrix * 10000).round().astype(int)

    metrics = {}
    for metric in ['shannon', 'simpson', 'observed_otus', 'chao1']:
        try:
            values = alpha_diversity(metric, counts.T.values,
                                      ids=counts.columns.tolist())
            metrics[metric] = values
        except Exception:
            continue

    diversity_df = pd.DataFrame(metrics, index=abundance_matrix.columns)
    diversity_df = diversity_df.join(metadata[[group_col]])

    # Compare groups
    groups = metadata[group_col].unique()
    if len(groups) == 2:
        for metric in metrics:
            g1 = diversity_df[diversity_df[group_col] == groups[0]][metric]
            g2 = diversity_df[diversity_df[group_col] == groups[1]][metric]
            _, pval = mannwhitneyu(g1, g2, alternative='two-sided')
            print(f"{metric}: {groups[0]}={g1.median():.3f}, "
                  f"{groups[1]}={g2.median():.3f}, p={pval:.4f}")

    return diversity_df

def beta_diversity_analysis(abundance_matrix, metadata, group_col,
                             metric='braycurtis', output_png="beta_div.png"):
    """Calculate beta diversity and perform PERMANOVA."""
    from skbio.stats.distance import permanova
    from sklearn.manifold import MDS
    import matplotlib.pyplot as plt

    dm = beta_diversity(metric, abundance_matrix.T.values,
                        ids=abundance_matrix.columns.tolist())

    # PERMANOVA test
    grouping = metadata.loc[abundance_matrix.columns, group_col]
    result = permanova(dm, grouping, permutations=999)
    print(f"PERMANOVA: pseudo-F={result['test statistic']:.3f}, "
          f"p={result['p-value']:.4f}")

    # PCoA / MDS visualization
    mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
    coords = mds.fit_transform(dm.data)

    fig, ax = plt.subplots(figsize=(8, 6))
    groups = grouping.unique()
    colors = ['#e74c3c', '#2980b9', '#27ae60', '#f39c12']
    for i, grp in enumerate(groups):
        mask = grouping == grp
        ax.scatter(coords[mask, 0], coords[mask, 1],
                   c=colors[i % len(colors)], label=grp, s=60, alpha=0.7)
    ax.set_xlabel('MDS1')
    ax.set_ylabel('MDS2')
    ax.set_title(f'Beta Diversity ({metric})\nPERMANOVA p={result["p-value"]:.4f}')
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_png, dpi=150)

    return dm, result

def differential_abundance(abundance_matrix, metadata, group_col, alpha=0.05,
                            min_prevalence=0.1):
    """Test differential abundance between two groups (Mann-Whitney U)."""
    groups = metadata[group_col].unique()
    assert len(groups) == 2

    g1 = metadata[metadata[group_col] == groups[0]].index
    g2 = metadata[metadata[group_col] == groups[1]].index
    g1 = g1.intersection(abundance_matrix.columns)
    g2 = g2.intersection(abundance_matrix.columns)

    # Filter by prevalence
    prevalence = (abundance_matrix > 0).mean(axis=1)
    filtered = abundance_matrix[prevalence >= min_prevalence]

    results = []
    for taxon in filtered.index:
        g1_vals = filtered.loc[taxon, g1].values
        g2_vals = filtered.loc[taxon, g2].values

        mean_g1 = g1_vals.mean()
        mean_g2 = g2_vals.mean()
        log2fc = np.log2((mean_g2 + 1e-10) / (mean_g1 + 1e-10))

        try:
            _, pval = mannwhitneyu(g1_vals, g2_vals, alternative='two-sided')
        except ValueError:
            pval = 1.0

        results.append({
            'taxon': taxon,
            'mean_abundance_g1': mean_g1,
            'mean_abundance_g2': mean_g2,
            'log2FC': log2fc,
            'pvalue': pval
        })

    results_df = pd.DataFrame(results).set_index('taxon')
    _, results_df['padj'], _, _ = multipletests(results_df['pvalue'], method='fdr_bh')
    sig = results_df[results_df['padj'] < alpha].sort_values('padj')

    print(f"Tested taxa: {len(results_df)}")
    print(f"Differentially abundant (padj < {alpha}): {len(sig)}")
    print(f"  Enriched in {groups[1]}: {(sig['log2FC'] > 0).sum()}")
    print(f"  Enriched in {groups[0]}: {(sig['log2FC'] < 0).sum()}")
    return results_df, sig
```

---

## Phase 3: Functional Profiling with HUMAnN3

### HUMAnN3 Pipeline

```bash
# HUMAnN3: functional profiling (gene families + pathways)
# Requires MetaPhlAn4 output and ChocoPhlAn/UniRef databases

# Concatenate paired reads (HUMAnN3 takes single file input)
cat sample_hostfree_R1.fastq.gz sample_hostfree_R2.fastq.gz > sample_concat.fastq.gz

# Run HUMAnN3
humann --input sample_concat.fastq.gz \
  --output humann_output/ \
  --threads 16 \
  --nucleotide-database /ref/chocophlan \
  --protein-database /ref/uniref90_diamond \
  --metaphlan-options="--bowtie2db /ref/metaphlan4_db" \
  --search-mode uniref90

# Key outputs:
# humann_output/sample_genefamilies.tsv    - UniRef90 gene family abundances (RPK)
# humann_output/sample_pathabundance.tsv   - MetaCyc pathway abundances
# humann_output/sample_pathcoverage.tsv    - Pathway coverage (0-1)

# Normalize gene families to CPM (copies per million)
humann_renorm_table --input humann_output/sample_genefamilies.tsv \
  --output humann_output/sample_genefamilies_cpm.tsv \
  --units cpm

# Normalize pathway abundance to CPM
humann_renorm_table --input humann_output/sample_pathabundance.tsv \
  --output humann_output/sample_pathabundance_cpm.tsv \
  --units cpm

# Regroup to functional categories
humann_regroup_table --input humann_output/sample_genefamilies_cpm.tsv \
  --output humann_output/sample_ko_cpm.tsv \
  --groups uniref90_ko   # KEGG Orthologs

humann_regroup_table --input humann_output/sample_genefamilies_cpm.tsv \
  --output humann_output/sample_ec_cpm.tsv \
  --groups uniref90_level4ec  # EC numbers

# Join tables from multiple samples
humann_join_tables --input humann_output/ \
  --output merged_pathabundance.tsv \
  --file_name pathabundance_cpm

# Split into community-level and species-stratified tables
humann_split_stratified_table --input merged_pathabundance.tsv \
  --output humann_output/split/
```

### HUMAnN3 Output Interpretation

```
Gene families (UniRef90):
  - RPK: Reads Per Kilobase (raw counts normalized by gene length)
  - CPM: Copies Per Million (RPK normalized by total sum)
  - Stratified rows: show which species contributes each gene family
  - UNMAPPED: reads that didn't map to any gene family
  - UNGROUPED: gene families that couldn't be assigned to a pathway

Pathway abundance (MetaCyc):
  - Quantifies metabolic pathway completeness and abundance
  - UNMAPPED/UNINTEGRATED: pathway-level unassigned
  - Stratified by species: which organisms contribute each pathway

Pathway coverage (0-1):
  - Fraction of pathway genes detected
  - Coverage < 0.5: pathway likely not complete in the community
  - Coverage > 0.8: pathway well-represented
```

---

## Phase 4: AMR Gene Detection

### AMRFinderPlus

```bash
# AMRFinderPlus: NCBI's AMR gene detection tool
# Run on assembled contigs (preferred) or translated reads

# From assembled contigs
amrfinder --nucleotide contigs.fasta \
  --output amrfinder_results.tsv \
  --threads 16 \
  --plus \
  --organism Escherichia  # Optional: use organism-specific breakpoints

# From protein sequences (if gene prediction done upstream)
amrfinder --protein predicted_proteins.faa \
  --output amrfinder_protein_results.tsv \
  --threads 16 \
  --plus
```

### CARD/RGI (Resistance Gene Identifier)

```bash
# RGI: Comprehensive Antibiotic Resistance Database
# Run on assembled contigs or metagenomic reads

# From contigs
rgi main --input_sequence contigs.fasta \
  --output_file rgi_results \
  --input_type contig \
  --alignment_tool BLAST \
  --num_threads 16 \
  --clean

# From metagenomic reads (bwt mode)
rgi bwt --read_one sample_R1.fastq.gz --read_two sample_R2.fastq.gz \
  --output_file rgi_reads \
  --threads 16 \
  --aligner bowtie2

# Key output columns:
# ARO (Antibiotic Resistance Ontology) accession
# Best_Hit_ARO: gene name
# Drug Class: antibiotic class
# Resistance Mechanism: efflux, target alteration, inactivation, etc.
# Model Type: Strict (high confidence) vs Loose (exploratory)
```

```python
def summarize_amr_results(amrfinder_file, rgi_file=None):
    """Summarize AMR detection results."""
    amr = pd.read_csv(amrfinder_file, sep='\t')

    print("=== AMRFinderPlus Summary ===")
    print(f"Total AMR genes detected: {len(amr)}")

    # By drug class
    if 'Subclass' in amr.columns:
        print("\nAMR genes by drug class:")
        class_counts = amr['Subclass'].value_counts()
        for cls, count in class_counts.head(15).items():
            print(f"  {cls}: {count}")

    # By resistance mechanism
    if 'Element subtype' in amr.columns:
        print("\nBy element type:")
        type_counts = amr['Element subtype'].value_counts()
        for t, count in type_counts.items():
            print(f"  {t}: {count}")

    if rgi_file:
        rgi = pd.read_csv(rgi_file + '.txt', sep='\t')
        print(f"\n=== RGI Summary ===")
        print(f"Total hits: {len(rgi)}")
        strict = rgi[rgi['Model_type'] == 'Strict']
        print(f"Strict hits: {len(strict)}")

        if 'Drug Class' in rgi.columns:
            drug_classes = rgi['Drug Class'].str.split('; ').explode().value_counts()
            print("\nDrug classes (RGI):")
            for cls, count in drug_classes.head(15).items():
                print(f"  {cls}: {count}")

    return amr
```

---

## Phase 5: Metagenome Assembly

### MEGAHIT Assembly

```bash
# MEGAHIT: memory-efficient metagenome assembly
megahit -1 sample_hostfree_R1.fastq.gz -2 sample_hostfree_R2.fastq.gz \
  -o megahit_assembly/ \
  --min-contig-len 1000 \
  --k-min 21 --k-max 141 --k-step 12 \
  -t 16 \
  --memory 0.9

# For co-assembly of multiple samples
megahit -1 s1_R1.fq.gz,s2_R1.fq.gz,s3_R1.fq.gz \
  -2 s1_R2.fq.gz,s2_R2.fq.gz,s3_R2.fq.gz \
  -o coassembly/ \
  --min-contig-len 1000 \
  -t 32 \
  --memory 0.9
```

### metaSPAdes Assembly

```bash
# metaSPAdes: more contiguous assemblies but higher resource usage
metaspades.py -1 sample_hostfree_R1.fastq.gz -2 sample_hostfree_R2.fastq.gz \
  -o metaspades_assembly/ \
  --threads 16 \
  --memory 100 \
  -k 21,33,55,77,99,127

# metaSPAdes is preferred when:
# - Higher contiguity is needed
# - Strain-level resolution is important
# - Sufficient compute resources available (>100 GB RAM)
```

**Assembly choice decision:**

| Criterion | MEGAHIT | metaSPAdes |
|-----------|---------|------------|
| Memory | Low (< 50 GB for most) | High (100+ GB) |
| Speed | Faster | Slower |
| Contiguity (N50) | Good | Better |
| Complex communities | Handles well | May struggle with very high diversity |
| Co-assembly | Good | Limited |
| Recommended for | Most projects, co-assembly | Individual samples, when resources allow |

### Assembly QC with QUAST

```bash
# Assembly statistics
quast contigs.fasta \
  -o assembly_qc/ \
  --min-contig 1000 \
  --threads 16 \
  -r /ref/none  # No reference for metagenomes

# Key metrics to check:
# Total length: total assembled bp
# Number of contigs: fewer is generally better
# N50: half of assembly in contigs >= this length
# L50: number of contigs that make up N50
```

---

## Phase 6: Genome Binning and MAG Recovery

### Binning Pipeline

```bash
# Step 1: Map reads back to assembly for coverage information
bowtie2-build contigs.fasta contigs_idx
bowtie2 -x contigs_idx -1 sample_R1.fastq.gz -2 sample_R2.fastq.gz \
  --very-sensitive -p 16 | samtools sort -@ 8 -o sample_mapped.bam
samtools index sample_mapped.bam

# Step 2: Generate depth file for MetaBAT2
jgi_summarize_bam_contig_depths --outputDepth depth.txt sample_mapped.bam

# Step 3: Run MetaBAT2
metabat2 -i contigs.fasta -a depth.txt \
  -o bins/metabat2/bin \
  -m 1500 \
  --minClsSize 200000 \
  -t 16

# Step 4: Run MaxBin2
run_MaxBin.pl -contig contigs.fasta \
  -reads sample_hostfree_R1.fastq.gz \
  -reads2 sample_hostfree_R2.fastq.gz \
  -out bins/maxbin2/bin \
  -thread 16

# Step 5: Run CONCOCT
cut_up_fasta.py contigs.fasta -c 10000 -o 0 \
  --merge_last -b contigs_10K.bed > contigs_10K.fa
concoct_coverage_table.py contigs_10K.bed sample_mapped.bam > coverage_table.tsv
concoct --composition_file contigs_10K.fa \
  --coverage_file coverage_table.tsv \
  -b bins/concoct/ \
  --threads 16
merge_cutup_clustering.py bins/concoct/clustering_gt1000.csv > bins/concoct/clustering_merged.csv
extract_fasta_bins.py contigs.fasta bins/concoct/clustering_merged.csv \
  --output_path bins/concoct/fasta_bins/

# Step 6: Bin refinement with DAS Tool
DAS_Tool -i bins/metabat2_scaffolds2bin.tsv,bins/maxbin2_scaffolds2bin.tsv,bins/concoct_scaffolds2bin.tsv \
  -l MetaBAT2,MaxBin2,CONCOCT \
  -c contigs.fasta \
  -o bins/das_tool_refined/ \
  --write_bins \
  --threads 16 \
  --score_threshold 0.5
```

### MAG Quality Assessment with CheckM2

```bash
# CheckM2: assess MAG completeness and contamination
checkm2 predict --threads 16 \
  --input bins/das_tool_refined/_DASTool_bins/ \
  --output_directory checkm2_results/ \
  --extension fa

# Quality tiers (MIMAG standards):
# High-quality:  Completeness > 90%, Contamination < 5%,
#                + 16S rRNA, + 23S rRNA, + 5S rRNA, + >= 18 tRNAs
# Medium-quality: Completeness >= 50%, Contamination < 10%
# Low-quality:   Completeness < 50% or Contamination >= 10%
```

```python
def assess_mag_quality(checkm2_results_file):
    """Assess MAG quality based on MIMAG standards."""
    checkm = pd.read_csv(checkm2_results_file, sep='\t')

    checkm['quality_tier'] = 'Low'
    checkm.loc[
        (checkm['Completeness'] >= 50) & (checkm['Contamination'] < 10),
        'quality_tier'
    ] = 'Medium'
    checkm.loc[
        (checkm['Completeness'] > 90) & (checkm['Contamination'] < 5),
        'quality_tier'
    ] = 'High'

    print("MAG Quality Summary:")
    print(checkm['quality_tier'].value_counts())
    print(f"\nHigh-quality MAGs (>90% complete, <5% contamination):")
    high = checkm[checkm['quality_tier'] == 'High'].sort_values('Completeness', ascending=False)
    for _, row in high.iterrows():
        print(f"  {row['Name']}: {row['Completeness']:.1f}% complete, "
              f"{row['Contamination']:.1f}% contamination")

    return checkm
```

### Binning Strategy Decision Tree

```
How many samples?
|
+-> Single sample
|   -> Run MetaBAT2, MaxBin2, CONCOCT independently
|   -> Refine with DAS Tool
|   -> Use single-sample depth profiles
|
+-> Multiple samples (same environment)
|   -> Co-assemble all samples (MEGAHIT or metaSPAdes)
|   -> Map each sample's reads to co-assembly
|   -> Use multi-sample depth profiles for binning
|   -> MetaBAT2 + DAS Tool generally sufficient
|
+-> Time series
|   -> Co-assemble all time points
|   -> Multi-sample depth profiles capture temporal variation
|   -> Differential abundance of MAGs across time (inStrain)
|
+-> Very high diversity (soil, ocean)
|   -> Consider SemiBin2 (semi-supervised deep learning)
|   -> May need very deep sequencing (>50 Gbp/sample)
|   -> Co-assembly may not be practical (too diverse)
```

---

## Phase 7: Strain-Level Tracking

### StrainPhlAn

```bash
# StrainPhlAn: strain-level phylogenomics from MetaPhlAn output

# Step 1: Extract markers from MetaPhlAn4 bowtie2 output
sample2markers.py -i sample_metaphlan4.bowtie2.bz2 \
  -o consensus_markers/ \
  --nproc 16 \
  --database /ref/metaphlan4_db/mpa_vJan21_CHOCOPhlAnSGB_202103.pkl

# Step 2: Extract reference markers for a species
extract_markers.py -c s__Escherichia_coli \
  -o ref_markers/ \
  --database /ref/metaphlan4_db/mpa_vJan21_CHOCOPhlAnSGB_202103.pkl

# Step 3: Build strain tree
strainphlan -s consensus_markers/*.pkl \
  -m ref_markers/s__Escherichia_coli.fna \
  -o strainphlan_output/ \
  -c s__Escherichia_coli \
  --nproc 16 \
  --phylophlan_mode accurate

# Output: Phylogenetic tree showing strain-level relationships
```

### inStrain: Strain-Level Population Genomics

```bash
# inStrain: compare strain populations within and between samples

# Step 1: Profile each sample against reference genome or MAG
inStrain profile sample_mapped.bam reference.fasta \
  -o inStrain_output/ \
  -p 16 \
  --min_cov 5 \
  --database_mode

# Step 2: Compare strain populations between samples
inStrain compare \
  -i inStrain_s1/ inStrain_s2/ inStrain_s3/ \
  -o inStrain_comparison/ \
  -p 16 \
  --database_mode

# Key outputs:
# genome_info.tsv: coverage, breadth, ANI per genome
# SNVs.tsv: single nucleotide variants detected
# gene_info.tsv: per-gene SNV rates and coverage
# comparisons: popANI and conANI between sample pairs
```

```
inStrain metric interpretation:
  popANI: Population-level ANI between two samples
    > 99.999%: Same strain
    99.99-99.999%: Very closely related strains
    < 99.99%: Different strains

  conANI: Consensus ANI (ignoring heterogeneous positions)
    Higher than popANI when within-sample diversity exists

  Coverage breadth: Fraction of genome covered at >= min_cov
    > 0.5: Reliable strain comparison possible
    < 0.5: Insufficient coverage for strain-level analysis
```

---

## Phase 8: Taxonomic Visualization

### Krona Interactive Charts

```bash
# Generate Krona chart from Kraken2 output
ktImportTaxonomy -q 2 -t 3 sample_kraken2.out \
  -o sample_krona.html

# From Bracken output
ktImportText sample_bracken_species.txt \
  -o sample_krona_bracken.html

# Multiple samples in one chart
ktImportTaxonomy -q 2 -t 3 \
  sample1_kraken2.out,sample1 \
  sample2_kraken2.out,sample2 \
  -o multi_sample_krona.html
```

### GraPhlAn Publication-Quality Phylogenetic Trees

```bash
# GraPhlAn: circular phylogenetic tree with abundance annotations

# Step 1: Convert MetaPhlAn output to GraPhlAn format
export2graphlan.py --skip_rows 1 -i merged_metaphlan4_profiles.txt \
  --tree merged_tree.txt \
  --annotation merged_annot.txt \
  --most_abundant 100 \
  --abundance_threshold 1 \
  --least_biomarkers 10 \
  --annotations 5,6 \
  --external_annotations 7 \
  --min_clade_size 1

# Step 2: Generate figure
graphlan_annotate.py --annot merged_annot.txt merged_tree.txt merged_tree_annotated.xml
graphlan.py merged_tree_annotated.xml merged_graphlan.png \
  --dpi 300 --size 10
```

---

## Evidence Grading Framework

| Tier | Criteria | Confidence |
|------|----------|------------|
| **T1** | Taxon detected by both Kraken2+Bracken and MetaPhlAn4, relative abundance >1%, consistent across replicates, validated by MAG recovery | High |
| **T2** | Detected by one method with abundance >0.1%, present in multiple samples, functional genes confirmed | Medium-High |
| **T3** | Detected by one method only, low abundance (0.01-0.1%), single sample | Medium |
| **T4** | Very low abundance (<0.01%), single method, potential database artifact | Low |

---

## Boundary Rules

```
DO:
- Perform read QC and host decontamination
- Run taxonomic classification (Kraken2+Bracken, MetaPhlAn4)
- Build custom Kraken2 databases
- Run functional profiling (HUMAnN3)
- Detect AMR genes (AMRFinderPlus, RGI)
- Assemble metagenomes (MEGAHIT, metaSPAdes)
- Bin genomes (MetaBAT2, MaxBin2, CONCOCT, DAS Tool)
- Assess MAG quality (CheckM2)
- Track strains (StrainPhlAn, inStrain)
- Visualize taxonomy (Krona, GraPhlAn)
- Calculate diversity metrics (alpha, beta, PERMANOVA)

DO NOT:
- Analyze 16S/ITS amplicon data (use microbiome/amplicon skill)
- Single-species genome assembly and annotation (use genome-assembly skill)
- Deep pathway enrichment (use gene-enrichment skill)
- Clinical interpretation of AMR (use clinical-microbiology skill)
- Phylogenetic tree construction from marker genes (use phylogenetics skill)
```

## Completeness Checklist

- [ ] Read QC completed (fastp, quality reports generated)
- [ ] Host decontamination performed (Bowtie2 against host reference)
- [ ] Taxonomic classification run (Kraken2+Bracken and/or MetaPhlAn4)
- [ ] Alpha diversity calculated and compared between groups
- [ ] Beta diversity computed with PERMANOVA significance test
- [ ] Differential abundance tested for taxa between conditions
- [ ] Functional profiling completed (HUMAnN3: gene families + pathways)
- [ ] AMR gene detection performed (if clinically relevant)
- [ ] Metagenome assembly completed with QC stats (QUAST)
- [ ] Genome binning and MAG recovery (if assembly performed)
- [ ] MAG quality assessed (CheckM2: completeness/contamination)
- [ ] Taxonomic visualization generated (Krona/GraPhlAn)
- [ ] Evidence tier assigned to all major findings
