---
name: genome-assembly
description: De novo genome assembly from sequencing reads. Long-read assembly with Flye for Oxford Nanopore and PacBio HiFi reads, Canu, hifiasm for phased assemblies, short-read assembly with SPAdes and MEGAHIT, hybrid assembly combining long and short reads, assembly polishing with Medaka for ONT and Pilon for Illumina and NextPolish, scaffolding with RagTag and SALSA2 for Hi-C, quality assessment with QUAST for N50 and L50 and misassemblies, BUSCO for gene completeness, contamination detection with BlobToolKit and Kraken2 screening, haplotig purging with purge_dups, genome size estimation with GenomeScope2 from k-mer histograms using jellyfish or KMC, assembly graph visualization with Bandage. Use when user asks about genome assembly, de novo assembly, Flye, Canu, hifiasm, SPAdes, hybrid assembly, polishing, Medaka, Pilon, NextPolish, scaffolding, RagTag, SALSA2, Hi-C scaffolding, QUAST, N50, BUSCO, contamination screening, BlobToolKit, purge_dups, haplotig purging, GenomeScope, k-mer analysis, genome size estimation, assembly graph, Bandage, long-read assembly, short-read assembly, contig, scaffold, or chromosome-level assembly.
---

# De Novo Genome Assembly

Comprehensive pipeline for assembling genomes from sequencing reads. Covers long-read (Oxford Nanopore, PacBio HiFi/CLR), short-read (Illumina), and hybrid assembly strategies. Includes polishing, scaffolding, quality assessment, and contamination screening.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_assembly_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as analysis completes
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Metagenome assembly and binning -> use `metagenomics-analyst`
- Transcriptome assembly (RNA-seq) -> use `transcriptomics`
- Variant calling from aligned reads -> use `variant-calling`
- Genome annotation (gene prediction) -> use `genome-annotation`
- Comparative genomics and synteny -> use `comparative-genomics`

## Cross-Reference: Other Skills

- **Metagenome assembly and MAG recovery** -> use metagenomics-analyst skill
- **Genome annotation after assembly** -> use genome-annotation skill
- **Variant calling from assembly** -> use variant-calling skill
- **Phylogenomics from assembled genomes** -> use phylogenetics skill

---

## Assembly Strategy Decision Tree

```
What sequencing data do you have?
|
+-> PacBio HiFi only
|   -> hifiasm (preferred: phased, high quality)
|   -> Or Flye --pacbio-hifi
|   -> Minimal polishing needed (HiFi base accuracy > Q30)
|
+-> PacBio HiFi + Hi-C
|   -> hifiasm with Hi-C phasing (best for diploid genomes)
|   -> Produces haplotype-resolved assembly
|
+-> Oxford Nanopore (ONT) only
|   -> Flye --nano-hq (for Guppy SUP/Dorado basecalling, Q20+)
|   -> Flye --nano-raw (for older basecalling, Q10-15)
|   -> Polish with Medaka (1-2 rounds)
|   -> Optional: further polish with Illumina (Pilon/NextPolish)
|
+-> ONT + Illumina (hybrid)
|   -> Flye (ONT reads) -> Medaka polish -> Pilon/NextPolish (Illumina)
|   -> Achieves high contiguity (ONT) + high accuracy (Illumina)
|
+-> Illumina only (short reads)
|   -> SPAdes --careful (small genomes < 100 Mb)
|   -> MEGAHIT (larger genomes, memory-constrained)
|   -> Limited contiguity (N50 typically 10-50 kb)
|
+-> PacBio CLR (older continuous long reads)
|   -> Canu or Flye --pacbio-raw
|   -> Requires extensive polishing (CLR error rate ~10-15%)
|   -> Polish: 2x Arrow/gcpp + 2x Pilon
|
+-> Any long reads + Hi-C
|   -> Assemble long reads -> Scaffold with SALSA2 or YaHS
|   -> Can achieve chromosome-level scaffolding
```

---

## Phase 1: Genome Size Estimation

### K-mer Counting with Jellyfish

```bash
# Count k-mers from Illumina reads
jellyfish count -C -m 21 -s 5G -t 16 \
  <(zcat sample_R1.fastq.gz) <(zcat sample_R2.fastq.gz) \
  -o kmer_counts.jf

# Generate histogram
jellyfish histo -t 16 kmer_counts.jf > kmer_histogram.histo
```

### K-mer Counting with KMC

```bash
# KMC: faster k-mer counting, handles large datasets
mkdir kmc_tmp
kmc -k21 -t16 -ci1 -cs10000 \
  @input_list.txt \    # File containing paths to FASTQ files
  kmc_output \
  kmc_tmp/

# Generate histogram
kmc_tools transform kmc_output histogram kmer_histogram.histo
```

### GenomeScope2 Analysis

```bash
# GenomeScope2: estimate genome size, heterozygosity, repeat content
genomescope2 -i kmer_histogram.histo \
  -o genomescope_output/ \
  -k 21 \
  -p 2 \
  --fitted_hist
```

```python
def interpret_genomescope(summary_file):
    """Parse and interpret GenomeScope2 results.

    Key metrics:
      - Genome haploid length: estimated genome size
      - Heterozygosity: fraction of heterozygous sites
      - Repeat content: percentage of genome in repeats
      - Model fit: R-squared of k-mer model (> 0.9 = good fit)
    """
    with open(summary_file) as f:
        content = f.read()

    print("GenomeScope2 Interpretation:")
    print("=" * 50)
    print(content)

    # Decision guidance
    print("\n--- Assembly Parameter Guidance ---")
    # Parse genome size (implementation depends on output format)
    # Example:
    # genome_size_mb = estimated_size / 1e6
    # if genome_size_mb < 100:
    #     print("Small genome: SPAdes recommended for short reads")
    # elif genome_size_mb < 1000:
    #     print("Medium genome: Flye or hifiasm recommended")
    # else:
    #     print("Large genome: consider splitting by chromosome")

    return content
```

### GenomeScope Interpretation Guide

```
K-mer histogram peaks:
  - Homozygous peak: Main peak at coverage ~X
    (X = total bases / genome size)
  - Heterozygous peak: Peak at ~X/2
    Only visible in diploid organisms with heterozygosity > 0.1%
  - Error peak: Sharp peak at very low coverage (1-3x)
    Should be ignored; represents sequencing errors

GenomeScope model fit:
  R² > 0.95: Excellent fit, reliable estimates
  R² 0.85-0.95: Good fit, estimates likely accurate
  R² < 0.85: Poor fit, possible issues:
    - High repeat content (confounds k-mer model)
    - Polyploidy (use -p 4 or -p 6)
    - Mixed species contamination
    - Insufficient sequencing depth
```

---

## Phase 2: Long-Read Assembly

### Flye Assembler

```bash
# ONT reads: high quality (Dorado/Guppy SUP, Q20+)
flye --nano-hq reads.fastq.gz \
  --out-dir flye_assembly/ \
  --threads 16 \
  --genome-size 3g \
  --iterations 2

# ONT reads: standard quality (Q10-15)
flye --nano-raw reads.fastq.gz \
  --out-dir flye_assembly/ \
  --threads 16 \
  --genome-size 3g

# PacBio HiFi reads
flye --pacbio-hifi reads.fastq.gz \
  --out-dir flye_assembly/ \
  --threads 16 \
  --genome-size 3g

# PacBio CLR reads
flye --pacbio-raw reads.fastq.gz \
  --out-dir flye_assembly/ \
  --threads 16 \
  --genome-size 3g

# Key output files:
# assembly.fasta: Final assembled contigs
# assembly_info.txt: Per-contig statistics
# assembly_graph.gfa: Assembly graph (for Bandage)
```

**Flye input mode selection:**

| Mode | Read Type | Expected Quality | Notes |
|------|-----------|-----------------|-------|
| `--nano-raw` | ONT R9/R10, Guppy fast/hac | Q10-15 | Most ONT data before 2023 |
| `--nano-hq` | ONT R10+, Dorado SUP | Q20+ | Modern ONT with high accuracy |
| `--nano-corr` | ONT, error-corrected | Q25+ | Pre-corrected reads |
| `--pacbio-raw` | PacBio CLR | Q10-15 | Older PacBio technology |
| `--pacbio-corr` | PacBio, error-corrected | Q25+ | Pre-corrected reads |
| `--pacbio-hifi` | PacBio HiFi (CCS) | Q30+ | Highest quality long reads |

**Flye parameters:**

| Parameter | Default | When to Change |
|-----------|---------|---------------|
| `--genome-size` | Required | Estimate from GenomeScope or expected size |
| `--iterations` | 1 | Increase to 2-3 for ONT assemblies needing polishing |
| `--min-overlap` | Auto | Increase (3000-5000) for highly repetitive genomes |
| `--asm-coverage` | Auto | Set to 40-60 if coverage is very high (>200x) to subsample |
| `--keep-haplotypes` | Off | Enable for heterozygous diploid genomes |
| `--scaffold` | On | Disable with `--no-alt-contigs` for haploid assemblies |

### hifiasm (PacBio HiFi)

```bash
# Standard HiFi assembly (primary + alternate contigs)
hifiasm -o assembly -t 16 reads.hifi.fastq.gz

# Hi-C phased assembly (haplotype-resolved)
hifiasm -o assembly -t 16 \
  --h1 hic_R1.fastq.gz \
  --h2 hic_R2.fastq.gz \
  reads.hifi.fastq.gz

# ONT UL (ultra-long) integration for HiFi assembly
hifiasm -o assembly -t 16 \
  --ul ont_ultralong.fastq.gz \
  reads.hifi.fastq.gz

# Convert GFA output to FASTA
awk '/^S/{print ">"$2; print $3}' assembly.bp.p_ctg.gfa > assembly.p_ctg.fa   # Primary
awk '/^S/{print ">"$2; print $3}' assembly.bp.hap1.p_ctg.gfa > assembly.hap1.fa  # Haplotype 1
awk '/^S/{print ">"$2; print $3}' assembly.bp.hap2.p_ctg.gfa > assembly.hap2.fa  # Haplotype 2
```

**hifiasm output files:**

| File | Content | When to Use |
|------|---------|------------|
| `*.bp.p_ctg.gfa` | Primary contigs | Default assembly output |
| `*.bp.hap1.p_ctg.gfa` | Haplotype 1 contigs | Hi-C phased diploid |
| `*.bp.hap2.p_ctg.gfa` | Haplotype 2 contigs | Hi-C phased diploid |
| `*.bp.a_ctg.gfa` | Alternate contigs | Heterozygous regions |

### Canu Assembler

```bash
# Canu: best for PacBio CLR and very long ONT reads
canu -p assembly -d canu_output \
  genomeSize=3g \
  -nanopore reads.fastq.gz \
  maxThreads=16 \
  maxMemory=64g \
  correctedErrorRate=0.105

# For PacBio CLR
canu -p assembly -d canu_output \
  genomeSize=3g \
  -pacbio reads.fastq.gz \
  maxThreads=16 \
  maxMemory=64g

# For PacBio HiFi (Canu in HiCanu mode)
canu -p assembly -d canu_output \
  genomeSize=3g \
  -pacbio-hifi reads.fastq.gz \
  maxThreads=16
```

---

## Phase 3: Short-Read Assembly

### SPAdes

```bash
# Standard SPAdes for small-medium genomes
spades.py -1 sample_R1.fastq.gz -2 sample_R2.fastq.gz \
  -o spades_assembly/ \
  --careful \
  --threads 16 \
  --memory 64 \
  -k 21,33,55,77,99,127

# Isolate mode (better for bacterial genomes)
spades.py -1 sample_R1.fastq.gz -2 sample_R2.fastq.gz \
  -o spades_assembly/ \
  --isolate \
  --threads 16

# With long reads for hybrid assembly
spades.py -1 short_R1.fastq.gz -2 short_R2.fastq.gz \
  --nanopore nanopore_reads.fastq.gz \
  -o hybrid_spades/ \
  --threads 16 \
  --memory 128

# Key outputs:
# contigs.fasta: assembled contigs
# scaffolds.fasta: scaffolded contigs (if paired-end)
# assembly_graph.fastg: assembly graph
```

### MEGAHIT

```bash
# MEGAHIT: memory-efficient, good for larger genomes
megahit -1 sample_R1.fastq.gz -2 sample_R2.fastq.gz \
  -o megahit_assembly/ \
  --min-contig-len 500 \
  --k-min 21 --k-max 141 --k-step 12 \
  -t 16 \
  --memory 0.9
```

### Short-Read vs Long-Read Assembly Expectations

| Metric | Short-Read | Long-Read (ONT/HiFi) |
|--------|-----------|---------------------|
| Contig N50 | 10-100 kb | 1-50 Mb |
| Misassemblies | Fewer (high accuracy) | More (repeat traversal) |
| Completeness | Good for gene space | Excellent (resolves repeats) |
| Repeat resolution | Poor (> read length) | Good (most repeats < read length) |
| Base accuracy | Very high (Q50+) | HiFi: Q30+; ONT: Q20-30 raw |
| Cost per Gb | Lowest | Higher (but dropping) |

---

## Phase 4: Hybrid Assembly

### Strategy: Long-Read Base + Short-Read Polish

```bash
# Step 1: Assemble with long reads
flye --nano-hq ont_reads.fastq.gz \
  --out-dir flye_assembly/ \
  --threads 16 \
  --genome-size 5m

# Step 2: Polish with long reads (Medaka for ONT)
medaka_polish -i ont_reads.fastq.gz \
  -d flye_assembly/assembly.fasta \
  -o medaka_polished/ \
  -t 16 \
  -m r1041_e82_400bps_sup_v4.3.0

# Step 3: Polish with short reads (Pilon)
bowtie2-build medaka_polished/consensus.fasta polished_idx
bowtie2 -x polished_idx -1 illumina_R1.fastq.gz -2 illumina_R2.fastq.gz \
  --very-sensitive -p 16 | samtools sort -@ 8 -o illumina_mapped.bam
samtools index illumina_mapped.bam

pilon --genome medaka_polished/consensus.fasta \
  --frags illumina_mapped.bam \
  --output pilon_polished \
  --outdir pilon_output/ \
  --threads 16 \
  --fix all \
  --mindepth 10
```

### Alternative: Unicycler (Bacterial Hybrid Assembly)

```bash
# Unicycler: specifically designed for bacterial hybrid assembly
unicycler -1 short_R1.fastq.gz -2 short_R2.fastq.gz \
  -l long_reads.fastq.gz \
  -o unicycler_output/ \
  -t 16 \
  --mode normal

# Modes:
# --mode conservative: fewer misassemblies, lower contiguity
# --mode normal: balanced (default)
# --mode bold: higher contiguity, more risk of misassembly
```

---

## Phase 5: Assembly Polishing

### Medaka (ONT Polishing)

```bash
# Medaka: neural network-based ONT consensus polishing
# Select model matching your basecaller and flowcell
medaka_polish -i ont_reads.fastq.gz \
  -d assembly.fasta \
  -o medaka_output/ \
  -t 16 \
  -m r1041_e82_400bps_sup_v4.3.0

# Available models (select based on your data):
# r1041_e82_400bps_sup_v4.3.0  - R10.4.1, SUP basecalling
# r1041_e82_400bps_hac_v4.3.0  - R10.4.1, HAC basecalling
# r941_min_sup_g507             - R9.4.1, SUP basecalling
# r941_min_hac_g507             - R9.4.1, HAC basecalling
```

### Pilon (Illumina Polishing)

```bash
# Pilon: iterative short-read polishing (run 2-3 rounds)
for round in 1 2 3; do
  if [ $round -eq 1 ]; then
    ref=assembly.fasta
  else
    prev=$((round - 1))
    ref=pilon_round${prev}/pilon.fasta
  fi

  bowtie2-build $ref ref_idx
  bowtie2 -x ref_idx -1 illumina_R1.fastq.gz -2 illumina_R2.fastq.gz \
    --very-sensitive -p 16 | samtools sort -@ 8 -o mapped_round${round}.bam
  samtools index mapped_round${round}.bam

  pilon --genome $ref \
    --frags mapped_round${round}.bam \
    --output pilon \
    --outdir pilon_round${round}/ \
    --threads 16 \
    --fix all \
    --mindepth 10 \
    --changes

  # Check if changes are decreasing
  n_changes=$(wc -l < pilon_round${round}/pilon.changes)
  echo "Round $round: $n_changes changes"

  # Stop if < 100 changes (convergence)
  if [ $n_changes -lt 100 ]; then
    echo "Converged at round $round"
    break
  fi
done
```

### NextPolish

```bash
# NextPolish: faster alternative to Pilon for large genomes
# Create config file
cat > nextpolish.cfg << 'EOF'
[General]
job_type = local
job_prefix = nextPolish
task = best
rewrite = yes
rerun = 3
parallel_jobs = 4
multithread_jobs = 8
genome = assembly.fasta
genome_size = auto
workdir = ./nextpolish_output
[sgs_option]
sgs_fofn = illumina_reads.fofn
sgs_options = -max_depth 100
EOF

# Create reads file list
echo "illumina_R1.fastq.gz" > illumina_reads.fofn
echo "illumina_R2.fastq.gz" >> illumina_reads.fofn

# Run NextPolish
nextPolish nextpolish.cfg
```

### Polishing Decision Matrix

| Data Type | Polisher | Rounds | Expected Improvement |
|-----------|----------|--------|---------------------|
| ONT (Q10-15) | Medaka x1 + Pilon x2 | 3 total | Q10 -> Q30+ |
| ONT (Q20+, SUP) | Medaka x1 | 1 | Q20 -> Q35+ |
| PacBio HiFi | None (or 1x Pilon) | 0-1 | Already Q30+, marginal improvement |
| PacBio CLR | gcpp/Arrow x2 + Pilon x2 | 4 total | Q15 -> Q40+ |
| Short-read only | Not applicable | 0 | Already high base accuracy |

---

## Phase 6: Haplotig Purging

### purge_dups

```bash
# purge_dups: remove haplotigs and overlaps from primary assembly
# Essential for diploid assemblies from long-read data

# Step 1: Map reads to assembly
minimap2 -x map-ont -t 16 assembly.fasta reads.fastq.gz \
  | gzip > reads_mapped.paf.gz

# Step 2: Calculate base coverage cutoffs
pbcstat reads_mapped.paf.gz
calcuts PB.stat > cutoffs

# Step 3: Split assembly by coverage
split_fa assembly.fasta > assembly.split.fa
minimap2 -x asm5 -DP assembly.split.fa assembly.split.fa \
  | gzip > self_aligned.paf.gz

# Step 4: Purge haplotigs and overlaps
purge_dups -2 -T cutoffs -c PB.base.cov assembly.split.fa > dups.bed
get_seqs -e dups.bed assembly.fasta

# Outputs:
# purged.fa: Primary assembly with haplotigs removed
# hap.fa: Haplotig sequences
```

```
When to use purge_dups:
  - Diploid organisms assembled with non-phasing assemblers
  - Assembly size is ~2x expected genome size (haplotigs inflating size)
  - BUSCO shows high duplication rate (> 10-15%)
  - Not needed for: hifiasm Hi-C phased assemblies, haploid organisms

purge_dups coverage interpretation:
  - Homozygous peak: ~expected coverage (e.g., 50x)
  - Haplotig peak: ~half coverage (e.g., 25x)
  - Junk peak: very low coverage (< 5x)
  - Collapsed repeat peak: > 1.5x expected coverage
```

---

## Phase 7: Scaffolding

### RagTag (Reference-Guided Scaffolding)

```bash
# RagTag: scaffold assembly using a reference genome
ragtag.py scaffold reference.fasta assembly.fasta \
  -o ragtag_output/ \
  -t 16 \
  --aligner minimap2

# RagTag can also correct misassemblies
ragtag.py correct reference.fasta assembly.fasta \
  -o ragtag_corrected/ \
  -t 16

# Then scaffold the corrected assembly
ragtag.py scaffold reference.fasta ragtag_corrected/ragtag.correct.fasta \
  -o ragtag_scaffolded/ \
  -t 16
```

### SALSA2 (Hi-C Scaffolding)

```bash
# SALSA2: Hi-C-based scaffolding for chromosome-level assembly

# Step 1: Align Hi-C reads to assembly
bwa index assembly.fasta
bwa mem -5SP -t 16 assembly.fasta hic_R1.fastq.gz hic_R2.fastq.gz \
  | samtools view -bhS -F 2316 - > hic_aligned.bam

# Step 2: Filter and sort Hi-C alignments
samtools sort -n -@ 8 hic_aligned.bam -o hic_sorted.bam

# Step 3: Generate BED file
bedtools bamtobed -i hic_sorted.bam > hic_aligned.bed
sort -k 4 hic_aligned.bed > hic_sorted.bed

# Step 4: Run SALSA2
python run_pipeline.py -a assembly.fasta \
  -l assembly.fasta.fai \
  -b hic_sorted.bed \
  -e GATC,GANTC \
  -o salsa2_output/ \
  -m yes

# Output: salsa2_output/scaffolds_FINAL.fasta
```

### YaHS (Yet Another Hi-C Scaffolder)

```bash
# YaHS: modern Hi-C scaffolder (often better than SALSA2)
# Step 1: Align Hi-C reads
bwa mem -5SP -t 16 assembly.fasta hic_R1.fastq.gz hic_R2.fastq.gz \
  | samtools view -bhS -F 2316 - \
  | samtools sort -n -@ 8 - -o hic_sorted.bam

# Step 2: Run YaHS
yahs assembly.fasta hic_sorted.bam -o yahs_output

# Step 3: Generate Hi-C contact map for visualization
juicer pre yahs_output.bin yahs_output_scaffolds_final.agp \
  assembly.fasta.fai > yahs_output.pre
java -jar juicer_tools.jar pre yahs_output.pre yahs_output.hic \
  <(cat yahs_output_scaffolds_final.fa.fai | awk '{print $1" "$2}')
```

### Scaffolding Method Comparison

| Method | Input Required | Typical N50 Improvement | Best For |
|--------|---------------|------------------------|----------|
| RagTag | Reference genome | Depends on reference quality | Close reference available |
| SALSA2 | Hi-C reads | 10-1000x (contigs -> chromosomes) | Chromosome-level assembly |
| YaHS | Hi-C reads | 10-1000x | Chromosome-level, faster than SALSA2 |
| LRScaf | Long reads | 2-10x | When only long reads available |

---

## Phase 8: Quality Assessment

### QUAST

```bash
# QUAST: comprehensive assembly statistics
quast assembly.fasta \
  -o quast_output/ \
  -r reference.fasta \     # Optional: reference genome
  -g genes.gff \           # Optional: gene annotation
  --threads 16 \
  --min-contig 1000 \
  --large                  # For large genomes

# Without reference
quast assembly.fasta -o quast_output/ --threads 16 --min-contig 1000
```

**Key QUAST metrics:**

| Metric | Description | Good Value |
|--------|-------------|------------|
| Total length | Sum of all contig lengths | Close to expected genome size |
| Number of contigs | Fewer is better | Species-dependent |
| N50 | 50% of assembly in contigs >= this length | Higher is better |
| L50 | Number of contigs making up N50 | Lower is better |
| NG50 | N50 relative to expected genome size | More comparable across assemblies |
| Largest contig | Size of longest contig | Ideally chromosome-scale |
| GC content | Overall GC% | Should match expected for species |
| Misassemblies | Structural errors (requires reference) | < 100 for good assembly |
| Mismatches/100kb | Base-level errors (requires reference) | < 1 for polished assembly |
| Genome fraction | % of reference covered | > 95% for complete assembly |

### BUSCO

```bash
# BUSCO: assess gene space completeness
busco -i assembly.fasta \
  -o busco_output \
  -m genome \
  -l eukaryota_odb10 \      # Or bacteria_odb10, fungi_odb10, etc.
  -c 16

# For specific lineages (more sensitive):
# vertebrata_odb10, mammalia_odb10, insecta_odb10
# actinobacteria_odb10, proteobacteria_odb10
# ascomycota_odb10, basidiomycota_odb10

# Compare multiple assemblies
python generate_plot.py -wd busco_summaries/
```

**BUSCO interpretation:**

| Category | Meaning | Expectation |
|----------|---------|-------------|
| Complete (C) | Gene found, full-length | > 95% for high quality |
| Single-copy (S) | One copy found | High for haploid |
| Duplicated (D) | Multiple copies found | Low (<15%) unless polyploid |
| Fragmented (F) | Partial gene found | < 5% |
| Missing (M) | Gene not found | < 5% for high quality |

```
BUSCO score interpretation:
  C > 95%, D < 5%, M < 3%:  Excellent assembly
  C > 90%, D < 10%, M < 5%:  Good assembly
  C > 80%, D < 15%, M < 10%: Acceptable, may need improvement
  C < 80%:                    Poor; investigate contamination, low coverage

High duplication (D > 15%):
  - Haplotigs not purged (use purge_dups)
  - Polyploid organism
  - Recent whole-genome duplication

High missing (M > 10%):
  - Insufficient sequencing coverage
  - Assembly gaps in gene-rich regions
  - Contamination masking host genome
  - Wrong BUSCO lineage selected
```

### Assembly Quality Assessment Pipeline

```python
import subprocess
import pandas as pd

def assembly_quality_report(assembly_fasta, expected_size_bp, busco_lineage):
    """Run comprehensive assembly quality assessment."""

    # Basic stats
    from Bio import SeqIO
    contigs = list(SeqIO.parse(assembly_fasta, 'fasta'))
    lengths = sorted([len(c) for c in contigs], reverse=True)
    total = sum(lengths)
    gc_count = sum(str(c.seq).upper().count('G') + str(c.seq).upper().count('C')
                   for c in contigs)

    # N50 calculation
    cumsum = 0
    n50 = 0
    l50 = 0
    for i, length in enumerate(lengths):
        cumsum += length
        if cumsum >= total / 2:
            n50 = length
            l50 = i + 1
            break

    # NG50 (relative to expected genome size)
    cumsum = 0
    ng50 = 0
    for length in lengths:
        cumsum += length
        if cumsum >= expected_size_bp / 2:
            ng50 = length
            break

    report = {
        'Total assembly size': f'{total:,} bp',
        'Expected genome size': f'{expected_size_bp:,} bp',
        'Assembly/Expected ratio': f'{total/expected_size_bp:.2f}',
        'Number of contigs': len(lengths),
        'Largest contig': f'{lengths[0]:,} bp',
        'N50': f'{n50:,} bp',
        'L50': l50,
        'NG50': f'{ng50:,} bp',
        'GC content': f'{gc_count/total:.1%}',
        'Contigs > 1 Mb': sum(1 for l in lengths if l >= 1e6),
        'Contigs > 10 Mb': sum(1 for l in lengths if l >= 1e7),
    }

    print("Assembly Quality Report")
    print("=" * 50)
    for key, value in report.items():
        print(f"  {key}: {value}")

    # Quality assessment
    ratio = total / expected_size_bp
    if ratio > 1.3:
        print("\nWARNING: Assembly is >30% larger than expected.")
        print("Possible causes: haplotigs, contamination, or inaccurate size estimate.")
        print("Action: Run purge_dups and BlobToolKit.")
    elif ratio < 0.8:
        print("\nWARNING: Assembly is >20% smaller than expected.")
        print("Possible causes: collapsed repeats, insufficient coverage, or filtering too strict.")

    return report
```

---

## Phase 9: Contamination Detection

### BlobToolKit

```bash
# BlobToolKit: detect contamination by comparing taxonomic assignment and coverage

# Step 1: Map reads to assembly
minimap2 -ax map-ont -t 16 assembly.fasta reads.fastq.gz \
  | samtools sort -@ 8 -o mapped.bam
samtools index mapped.bam

# Step 2: BLAST contigs against nt database
blastn -query assembly.fasta -db /ref/nt \
  -outfmt '6 qseqid staxids bitscore std' \
  -max_target_seqs 10 -max_hsps 1 -evalue 1e-25 \
  -num_threads 16 -out blast_results.txt

# Step 3: Run BlobToolKit
blobtools create \
  --fasta assembly.fasta \
  --cov mapped.bam \
  --hits blast_results.txt \
  --taxdump /ref/taxdump/ \
  blobdir/

# Step 4: View results
blobtools view --remote blobdir/

# Step 5: Filter contigs by taxonomy
blobtools filter \
  --param bestsumorder_phylum--Keys=Arthropoda \
  --fasta assembly.fasta \
  --output filtered_assembly.fasta \
  blobdir/
```

### Kraken2 Contamination Screen

```bash
# Quick contamination check with Kraken2
kraken2 --db /ref/kraken2_standard \
  --threads 16 \
  --output contig_kraken2.out \
  --report contig_kraken2.report \
  assembly.fasta

# Check for unexpected taxa
awk '$4 == "P"' contig_kraken2.report | sort -k1,1nr | head -20
```

```
Contamination assessment:
  - Primary target species should represent > 90% of classified contigs
  - Common contaminants:
    - Bacteria in eukaryotic assemblies (lab contamination)
    - Human DNA in non-human samples
    - Adapter/vector sequences
    - Symbiont DNA (may be real biology, not contamination)

  BlobToolKit plot interpretation:
  - Each blob = one contig
  - X-axis: GC content
  - Y-axis: Coverage (log scale)
  - Color: Taxonomic assignment
  - Target species contigs cluster together (similar GC + coverage)
  - Contamination appears as separate clusters
```

---

## Phase 10: Assembly Graph Visualization

### Bandage

```bash
# Bandage: visualize assembly graphs
# Load GFA/FASTG file in Bandage GUI
Bandage load assembly_graph.gfa

# Command-line image generation
Bandage image assembly_graph.gfa assembly_graph.png \
  --height 1000 --width 1000

# Generate assembly graph info
Bandage info assembly_graph.gfa

# Extract specific components
Bandage reduce assembly_graph.gfa reduced_graph.gfa --scope aroundnodes \
  --nodes "contig_1,contig_2" --distance 5
```

```
Assembly graph interpretation:
  - Linear paths: Well-resolved regions
  - Bubbles: Heterozygosity (two haplotype paths)
  - Tangles: Unresolved repeats
  - Dead ends: Contig tips (may indicate breaks at repeats)
  - Self-loops: Circular elements (plasmids, mitochondria, chloroplast)
  - Complex tangles: Highly repetitive regions (centromeres, telomeres)
```

---

## Evidence Grading Framework

| Tier | Criteria | Confidence |
|------|----------|------------|
| **T1** | Chromosome-level scaffolding, BUSCO C > 95%, QUAST misassemblies < 10, no contamination detected | High |
| **T2** | Contig N50 > 1 Mb, BUSCO C > 90%, polished, haplotigs purged | Medium-High |
| **T3** | Contig N50 > 100 kb, BUSCO C > 80%, some contamination or haplotig issues | Medium |
| **T4** | Fragmented assembly (N50 < 50 kb), BUSCO C < 80%, or significant contamination | Low |

---

## Boundary Rules

```
DO:
- Assemble genomes from long and/or short reads (Flye, hifiasm, Canu, SPAdes, MEGAHIT)
- Polish assemblies (Medaka, Pilon, NextPolish)
- Scaffold with reference or Hi-C data (RagTag, SALSA2, YaHS)
- Assess assembly quality (QUAST, BUSCO)
- Detect and remove contamination (BlobToolKit, Kraken2)
- Purge haplotigs (purge_dups)
- Estimate genome size (GenomeScope2, jellyfish, KMC)
- Visualize assembly graphs (Bandage)
- Guide assembler and parameter selection

DO NOT:
- Annotate genes on the assembly (use genome-annotation skill)
- Perform variant calling from assemblies (use variant-calling skill)
- Assemble metagenomes with binning (use metagenomics-analyst skill)
- Run comparative genomics (use comparative-genomics skill)
- Assemble transcriptomes (use transcriptomics skill)
```

## Completeness Checklist

- [ ] Genome size estimated (GenomeScope2 from k-mer analysis)
- [ ] Appropriate assembler selected based on data type and genome characteristics
- [ ] Assembly completed with optimized parameters
- [ ] Polishing rounds completed (Medaka/Pilon/NextPolish as appropriate)
- [ ] Haplotigs purged if diploid organism (purge_dups)
- [ ] Scaffolding attempted (reference-guided or Hi-C)
- [ ] QUAST statistics calculated (N50, total size, contig count)
- [ ] BUSCO completeness assessed with appropriate lineage
- [ ] Contamination screened (BlobToolKit or Kraken2)
- [ ] Assembly graph inspected (Bandage)
- [ ] Assembly size matches expected genome size (+/- 10%)
- [ ] Evidence tier assigned to assembly quality
