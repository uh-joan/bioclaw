---
name: long-read-sequencing
description: Long-read sequencing analyst for Oxford Nanopore (ONT) and PacBio platforms. Basecalling, read QC, alignment, variant calling, structural variant detection, methylation calling, isoform analysis, phasing, and de novo assembly. Use when user mentions long-read sequencing, nanopore, Oxford Nanopore, ONT, PacBio, HiFi, CLR, Dorado, Guppy, minimap2, Clair3, Sniffles, cuteSV, SVIM, structural variants from long reads, methylation from nanopore, modified bases, 5mC, 6mA, modkit, IsoSeq, FLAIR, isoform detection, WhatsHap, phasing, haplotype, adaptive sampling, ReadFish, N50, read length distribution, homopolymer errors, or long-read assembly.
---

# Long-Read Sequencing Analysis

Analysis pipeline for Oxford Nanopore Technology (ONT) and PacBio long-read sequencing data. Covers basecalling, quality control, alignment, variant calling (SNVs and structural variants), methylation detection, isoform analysis, haplotype phasing, and platform-specific considerations.

## Report-First Workflow

1. **Create report file immediately**: `[sample]_longread_analysis_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as analysis proceeds
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill
- Short-read WGS/WES variant calling -> use appropriate short-read variant calling skill
- RNA-seq from short reads -> use RNA-seq skill
- Hi-C/3C chromatin conformation -> use hic-analysis skill
- Bisulfite sequencing methylation -> use methylation-analysis skill
- Targeted amplicon sequencing -> specialized amplicon pipeline

## Cross-Reference: Other Skills
- **Structural variants at TAD boundaries** -> use hic-analysis skill for Hi-C context
- **Methylation validation** -> use methylation-analysis skill for bisulfite comparison
- **Isoform-level splicing** -> use alternative-splicing skill for splicing event annotation
- **Neoantigen calling from long-read variants** -> use immunoinformatics skill

---

## Platform Comparison

### ONT vs PacBio Technologies

| Feature | ONT (Nanopore) | PacBio HiFi | PacBio CLR |
|---------|---------------|-------------|------------|
| **Read length** | Ultra-long (>100 kb possible) | 10-25 kb (typical) | 10-50 kb |
| **Accuracy (raw)** | 92-98% (model-dependent) | 99.9% (Q30+) | 85-90% |
| **Error profile** | Systematic homopolymer errors | Random, low rate | Systematic indels |
| **Throughput** | PromethION: 100-300 Gb/flowcell | Revio: 90 Gb/SMRT cell | 20-50 Gb/SMRT cell |
| **Modified bases** | Native (5mC, 6mA, BrdU, etc.) | Native (5mC via kinetics) | Limited |
| **Real-time analysis** | Yes (adaptive sampling) | No | No |
| **Cost per Gb** | Low-moderate | Moderate-high | Moderate |
| **Library prep** | Rapid (<1 hr) or ligation (2 hr) | SMRTbell (4-6 hr) | SMRTbell (4-6 hr) |

### When to Choose Each Platform

```
Choose ONT when:
- Ultra-long reads needed (>50 kb, repeat resolution, phasing)
- Real-time/rapid results required (clinical, field deployment)
- Native methylation detection is primary goal
- Budget-constrained for large genomes
- Adaptive sampling for targeted enrichment without capture

Choose PacBio HiFi when:
- Base-level accuracy is critical (clinical SNV calling)
- De novo assembly quality is paramount
- Resolving complex structural variants with precision
- CpG methylation from kinetics sufficient
- Phased diploid assembly needed

Choose PacBio CLR when:
- Maximum read length from PacBio desired
- De novo assembly of very large genomes
- IsoSeq full-length transcript sequencing
- Budget allows for lower accuracy with high coverage
```

---

## Phase 1: Basecalling (ONT)

### Dorado (Current Standard)

```bash
# Dorado: successor to Guppy, actively maintained by ONT
# Models: fast, hac (high accuracy), sup (super accuracy)

# Basic basecalling
dorado basecaller \
  sup \
  pod5_dir/ \
  --device cuda:all \
  --min-qscore 10 \
  > calls.bam

# Basecalling with modified base detection
dorado basecaller \
  sup \
  pod5_dir/ \
  --modified-bases 5mCG_5hmCG \
  --device cuda:all \
  > calls_modbase.bam

# Basecalling with alignment (basecall + align in one step)
dorado basecaller \
  sup \
  pod5_dir/ \
  --reference reference.fa \
  --device cuda:all \
  > calls_aligned.bam

# Duplex calling (for duplex reads — both strands sequenced)
dorado duplex \
  sup \
  pod5_dir/ \
  --device cuda:all \
  > duplex_calls.bam
```

### Dorado Model Selection Guide

| Model | Speed | Accuracy | Use Case |
|-------|-------|----------|----------|
| **fast** | ~1000 bases/s | ~95-97% | Real-time monitoring, quick look |
| **hac** | ~200 bases/s | ~97-99% | Standard analysis, good balance |
| **sup** | ~50 bases/s | ~99%+ | Publication-quality, variant calling |
| **duplex** | Varies | ~99.5%+ | Highest accuracy (requires duplex library) |

### Dorado Model Versioning

```bash
# List available models
dorado download --list

# Download specific model
dorado download --model dna_r10.4.1_e8.2_400bps_sup@v4.3.0

# Model naming: {chemistry}_{pore}_{speed}_{accuracy}@{version}
# dna_r10.4.1_e8.2_400bps_sup@v4.3.0
#   chemistry: dna
#   pore: r10.4.1
#   translocation speed: e8.2 (enzyme), 400bps
#   accuracy: sup (super)
#   version: v4.3.0
```

### Legacy Guppy (Deprecated)

```bash
# Guppy is deprecated in favor of Dorado. Use only for legacy data.
guppy_basecaller \
  -i fast5_dir/ \
  -s output_dir/ \
  --flowcell FLO-MIN114 \
  --kit SQK-LSK114 \
  --device cuda:all \
  --min_qscore 7
```

---

## Phase 2: Read Quality Control

### NanoPlot

```bash
# Comprehensive QC from FASTQ or BAM
NanoPlot \
  --bam aligned.bam \
  --outdir nanoplot_qc/ \
  --loglength \
  --plots dot kde hex \
  --N50 \
  --title "Sample QC Report" \
  --threads 8

# From unaligned FASTQ
NanoPlot \
  --fastq reads.fastq.gz \
  --outdir nanoplot_qc/ \
  --loglength \
  --N50
```

### Key QC Metrics

| Metric | Good (ONT sup) | Good (HiFi) | Poor | Notes |
|--------|----------------|-------------|------|-------|
| **Median read length** | >5 kb | >10 kb | <1 kb | Depends on library prep |
| **N50** | >10 kb | >15 kb | <5 kb | Half of bases in reads ≥ this length |
| **Median quality (Q)** | >15 (sup) | >30 | <10 | Q20 = 99%, Q30 = 99.9% |
| **Total bases** | >30x coverage | >30x coverage | <10x | Target depth depends on application |
| **Reads >10 kb** | >50% | >80% | <20% | Long reads are the point |
| **Reads >50 kb** | >5% (ultralong) | Rare | - | Valuable for scaffolding |

### pycoQC (Sequencing Run QC)

```bash
# QC from sequencing summary file (ONT-specific)
pycoQC \
  --summary_file sequencing_summary.txt \
  --barcode_file barcoding_summary.txt \
  --html_outfile pycoQC_report.html \
  --min_pass_qual 10
```

### LongQC

```bash
# Platform-aware QC
python longQC.py sampleqc \
  -x ont-rapid \
  -o longqc_output/ \
  reads.fastq.gz

# Presets: ont-ligation, ont-rapid, pb-rs2, pb-sequel, pb-hifi
```

### QC Decision Points

```
Read length too short (<5 kb median):
├── Check shearing during extraction → use gentle lysis
├── Check library prep → avoid excess bead cleanup
├── ONT: check pore quality, run time
└── PacBio: check SMRTbell construction, size selection

Quality too low (<Q10 median, ONT):
├── Wrong model for chemistry → verify pore version + kit
├── Degraded pores → use fresh flow cell
├── Basecalling model → try sup instead of hac
└── Sample quality → check DNA integrity (DIN score)

Low yield:
├── Check library concentration → aim for recommended loading
├── ONT: nuclease flush + reload to extend run
├── PacBio: optimize loading concentration
└── Check for bubbles or flowcell issues
```

---

## Phase 3: Alignment

### minimap2 (Primary Aligner)

```bash
# ONT DNA alignment
minimap2 -ax map-ont \
  -t 16 \
  --secondary=no \
  --MD \
  reference.fa \
  reads.fastq.gz \
  | samtools sort -@ 8 -o aligned.bam

samtools index aligned.bam

# PacBio HiFi alignment
minimap2 -ax map-hifi \
  -t 16 \
  --secondary=no \
  --MD \
  reference.fa \
  reads.fastq.gz \
  | samtools sort -@ 8 -o aligned.bam

# PacBio CLR alignment
minimap2 -ax map-pb \
  -t 16 \
  --secondary=no \
  --MD \
  reference.fa \
  reads.fastq.gz \
  | samtools sort -@ 8 -o aligned.bam

# Direct RNA (ONT)
minimap2 -ax splice \
  -uf \
  -k14 \
  -t 16 \
  reference.fa \
  rna_reads.fastq.gz \
  | samtools sort -@ 8 -o rna_aligned.bam

# cDNA (ONT)
minimap2 -ax splice \
  -t 16 \
  reference.fa \
  cdna_reads.fastq.gz \
  | samtools sort -@ 8 -o cdna_aligned.bam
```

### minimap2 Preset Reference

| Preset | Platform | Type | Key Parameters |
|--------|----------|------|---------------|
| `map-ont` | ONT | DNA | `-k15`, gap-affine scoring tuned for ONT errors |
| `map-hifi` | PacBio HiFi | DNA | `-k19`, high accuracy settings |
| `map-pb` | PacBio CLR | DNA | `-Hk19`, handles high indel rate |
| `splice` | ONT/PacBio | RNA | Splice-aware, `-uf` for direct RNA (strand) |
| `asm5` | Any | Assembly | <5% divergence, assembly-to-reference |
| `asm20` | Any | Assembly | <20% divergence |

### Alignment QC

```bash
# Basic alignment statistics
samtools flagstat aligned.bam

# Coverage statistics
samtools coverage aligned.bam > coverage.tsv
mosdepth --threads 4 --by 500 mosdepth_prefix aligned.bam

# Expected metrics:
# Mapping rate: >95% (clean sample)
# Mean coverage: as planned (30x typical for germline)
# Coverage uniformity: check for dropout regions
```

---

## Phase 4: Small Variant Calling

### Clair3 (ONT and PacBio)

```bash
# Clair3: deep learning variant caller for long reads
# ONT reads
run_clair3.sh \
  --bam_fn=aligned.bam \
  --ref_fn=reference.fa \
  --output=clair3_output/ \
  --threads=16 \
  --platform="ont" \
  --model_path="/opt/models/ont_sup_r10.4.1" \
  --sample_name=sample \
  --include_all_ctgs

# PacBio HiFi reads
run_clair3.sh \
  --bam_fn=aligned.bam \
  --ref_fn=reference.fa \
  --output=clair3_output/ \
  --threads=16 \
  --platform="hifi" \
  --model_path="/opt/models/hifi_revio" \
  --sample_name=sample
```

### PEPPER-Margin-DeepVariant (ONT)

```bash
# PEPPER-Margin-DeepVariant: Google/ONT collaboration
# Best for ONT variant calling (especially with sup basecalling)

# Using Docker
docker run \
  -v "$(pwd):/data" \
  google/deepvariant:latest \
  pepper_margin_deepvariant call_variant \
  --bam /data/aligned.bam \
  --fasta /data/reference.fa \
  --output_dir /data/pepper_output/ \
  --threads 16 \
  --ont_r10_q20

# Key presets:
# --ont_r10_q20: ONT R10 with Q20+ reads
# --ont_r9_guppy5_sup: ONT R9 with Guppy5 sup
# --hifi: PacBio HiFi reads
```

### Variant Caller Comparison

| Caller | Platform | SNV F1 | Indel F1 | Speed | Notes |
|--------|----------|--------|----------|-------|-------|
| **Clair3** | ONT, HiFi | ~99.5% (HiFi) | ~99% (HiFi) | Fast | Good all-around |
| **PEPPER-DeepVariant** | ONT | ~99.7% (sup) | ~95% | Moderate | Best for ONT SNVs |
| **DeepVariant** | HiFi | ~99.8% | ~99.5% | Moderate | Gold standard for HiFi |
| **Medaka** | ONT | ~98% | ~90% | Fast | ONT-specific, lightweight |

### Minimum Coverage for Variant Calling

| Application | ONT (sup) | PacBio HiFi | Notes |
|-------------|-----------|-------------|-------|
| Germline SNVs | 20-30x | 15-20x | Higher for ONT due to error rate |
| Germline indels | 30-40x | 20x | Homopolymer indels challenging on ONT |
| Somatic SNVs | 60-80x | 40-60x | Need to detect low VAF variants |
| De novo assembly | 30-40x | 20-30x | HiFi needs less due to accuracy |

---

## Phase 5: Structural Variant Detection

### Sniffles2

```bash
# Sniffles2: SV caller optimized for long reads
sniffles \
  --input aligned.bam \
  --vcf svs.vcf.gz \
  --reference reference.fa \
  --threads 16 \
  --minsvlen 50 \
  --minsupport 3 \
  --mapq 20

# Population-level calling (multi-sample)
# Step 1: Per-sample SNF file generation
sniffles \
  --input sample1.bam \
  --snf sample1.snf \
  --reference reference.fa \
  --threads 16

sniffles \
  --input sample2.bam \
  --snf sample2.snf \
  --reference reference.fa \
  --threads 16

# Step 2: Multi-sample SV calling
sniffles \
  --input sample1.snf sample2.snf \
  --vcf population_svs.vcf.gz \
  --reference reference.fa \
  --threads 16
```

### cuteSV

```bash
# cuteSV: sensitive SV detection using signature clustering
cuteSV \
  aligned.bam \
  reference.fa \
  cutesv_svs.vcf \
  cutesv_work_dir/ \
  --threads 16 \
  --min_support 3 \
  --min_size 50 \
  --max_size -1 \
  --min_mapq 20 \
  --genotype \
  --sample sample_name

# Platform-specific parameters
# ONT:
  --max_cluster_bias_INS 1000 \
  --diff_ratio_merging_INS 0.9 \
  --max_cluster_bias_DEL 1000 \
  --diff_ratio_merging_DEL 0.5

# PacBio HiFi:
  --max_cluster_bias_INS 1000 \
  --diff_ratio_merging_INS 0.9 \
  --max_cluster_bias_DEL 1000 \
  --diff_ratio_merging_DEL 0.5
```

### SVIM

```bash
# SVIM: structural variant identification using mapped reads
svim alignment \
  svim_output/ \
  aligned.bam \
  reference.fa \
  --min_sv_size 50 \
  --minimum_depth 3 \
  --min_mapq 20 \
  --sample sample_name

# Filter by quality score
bcftools view -i 'QUAL >= 10' svim_output/variants.vcf > svim_filtered.vcf
```

### SV Caller Comparison

| Caller | DEL | INS | INV | DUP | TRA | Speed | Notes |
|--------|-----|-----|-----|-----|-----|-------|-------|
| **Sniffles2** | Excellent | Excellent | Good | Good | Good | Fast | Multi-sample, recommended default |
| **cuteSV** | Excellent | Excellent | Good | Moderate | Good | Fast | Signature clustering |
| **SVIM** | Good | Good | Good | Good | Moderate | Fast | Quality scores useful |

### Minimum Supporting Reads

| Coverage | Min Support | Rationale |
|----------|------------|-----------|
| 10-15x | 2-3 reads | Low coverage; accept more noise |
| 15-30x | 3-5 reads | Standard; good balance |
| 30-50x | 5-8 reads | High confidence |
| >50x | 8-10+ reads | Stringent; minimize false positives |

### Population-Level SV Merging

```bash
# SURVIVOR: merge SV calls across callers or samples
# Merge calls from multiple callers (consensus)
ls sniffles.vcf cutesv.vcf svim.vcf > vcf_list.txt

SURVIVOR merge \
  vcf_list.txt \
  1000 \
  2 \
  1 \
  1 \
  0 \
  50 \
  consensus_svs.vcf

# Parameters: max_distance(bp) min_callers type_agree strand_agree estimate_distance min_size
# 1000: max 1 kb distance between breakpoints to merge
# 2: require ≥2 callers to agree
# 1: require type agreement
# 1: require strand agreement

# Jasmine: alternative merger (better for population-scale)
jasmine \
  file_list=sample_vcfs.txt \
  out_file=merged_svs.vcf \
  genome_file=reference.fa \
  --threads 16 \
  --allow_intrasample \
  max_dist=1000 \
  min_support=2
```

### SV Annotation

```bash
# AnnotSV: comprehensive SV annotation
AnnotSV \
  -SVinputFile consensus_svs.vcf \
  -genomeBuild GRCh38 \
  -outputFile annotated_svs \
  -annotationMode both \
  -SVminSize 50

# Annotations include:
# - Gene overlap (full, partial, intronic)
# - Known pathogenic SVs (ClinVar, ClinGen)
# - Population frequency (gnomAD-SV, DGV)
# - Regulatory element overlap
# - ACMG classification
```

---

## Phase 6: Methylation Calling (ONT)

### Dorado Modified Base Calling

```bash
# Call 5mC and 5hmC during basecalling
dorado basecaller \
  sup \
  pod5_dir/ \
  --modified-bases 5mCG_5hmCG \
  --reference reference.fa \
  --device cuda:all \
  > modbase_aligned.bam

# Available modified base models:
# 5mCG: 5-methylcytosine in CpG context
# 5mCG_5hmCG: 5mC + 5-hydroxymethylcytosine
# 6mA: N6-methyladenine
# 5mC: 5-methylcytosine in all contexts (CpG, CHG, CHH)
```

### modkit (Methylation Extraction)

```bash
# modkit: ONT tool for modified base analysis from BAM
# Pileup: aggregate methylation calls per position
modkit pileup \
  modbase_aligned.bam \
  methylation_pileup.bed \
  --ref reference.fa \
  --threads 16 \
  --filter-threshold 0.75 \
  --cpg

# Output: BED-like format with methylation fraction per CpG
# chrom  start  end  modified_base  score  strand  ...  fraction_modified  Nvalid

# Summary statistics
modkit summary modbase_aligned.bam

# Per-read methylation extraction
modkit extract \
  modbase_aligned.bam \
  per_read_methylation.tsv \
  --ref reference.fa \
  --threads 16

# Convert to bedMethyl format for genome browser
modkit pileup \
  modbase_aligned.bam \
  methylation.bedmethyl \
  --ref reference.fa \
  --bedgraph \
  --cpg
```

### Methylation QC

| Metric | Expected | Poor | Notes |
|--------|----------|------|-------|
| Global CpG methylation | 70-80% (mammalian) | <50% or >90% | Genome-wide average |
| CpG island methylation | <10% (normal tissue) | >30% | Hypermethylation may be biological |
| Coverage per CpG | >10x | <5x | Need sufficient reads for reliable calls |
| Modification call rate | >90% | <70% | Fraction of CpGs with confident calls |

### Integration with Bisulfite Data

```
ONT methylation vs bisulfite:
- ONT detects 5mC and 5hmC (can distinguish with appropriate models)
- Bisulfite converts both 5mC and 5hmC → cannot distinguish
- ONT: per-read methylation (single-molecule resolution)
- Bisulfite: aggregate methylation level per CpG

Concordance: typically r > 0.9 between ONT (sup model) and WGBS
Advantages of ONT: no chemical conversion, single-molecule, allele-specific
Limitations of ONT: lower accuracy per-site without high coverage
```

---

## Phase 7: Isoform Detection

### IsoSeq3 (PacBio Full-Length Transcripts)

```bash
# IsoSeq3 pipeline: PacBio full-length transcript sequencing
# Step 1: CCS generation (if not already HiFi)
ccs input.subreads.bam ccs.bam --min-rq 0.9 --num-threads 16

# Step 2: Primer removal and demultiplexing
lima ccs.bam primers.fasta demux.bam --isoseq

# Step 3: Refine — remove polyA and concatemers
isoseq3 refine demux.5p--3p.bam primers.fasta refined.bam --require-polya

# Step 4: Cluster — group into isoform clusters
isoseq3 cluster refined.bam clustered.bam --num-threads 16

# Step 5: Align to genome
pbmm2 align reference.fa clustered.hq.bam aligned_isoforms.bam \
  --sort --preset ISOSEQ

# Step 6: Collapse redundant isoforms
isoseq3 collapse aligned_isoforms.bam collapsed.gff
```

### FLAIR (ONT Isoform Analysis)

```bash
# FLAIR: Full-Length Alternative Isoform analysis of RNA
# Step 1: Align ONT direct RNA or cDNA reads
minimap2 -ax splice -uf -t 16 reference.fa rna_reads.fastq.gz \
  | samtools sort -o aligned_rna.bam

# Step 2: Correct splice junctions using short-read junctions
flair correct \
  -q aligned_rna.bed \
  -g reference.fa \
  -j short_read_junctions.bed \
  -t 16 \
  -o flair_corrected

# Step 3: Collapse into isoforms
flair collapse \
  -r rna_reads.fastq.gz \
  -q flair_corrected_all_corrected.bed \
  -g reference.fa \
  -t 16 \
  --gtf annotation.gtf \
  -o flair_isoforms

# Step 4: Quantify isoforms
flair quantify \
  -r reads_manifest.tsv \
  -i flair_isoforms.isoforms.fa \
  -t 16 \
  -o flair_counts

# Step 5: Differential isoform usage
flair diffExp \
  -q flair_counts.counts.tsv \
  -o flair_diffexp \
  --threads 16
```

### Isoform Analysis QC

```
Key metrics:
- Full-length read fraction: >80% (IsoSeq), >50% (ONT cDNA)
- Median transcript length: 1-3 kb (typical for mRNA)
- Novel isoform fraction: 20-40% is common
- Single-exon transcripts: <10% (higher may indicate genomic contamination)
- Splice junction support: >90% at known junctions (GT-AG)

ONT-specific considerations:
- Direct RNA: strand-specific, no PCR bias, but lower throughput
- cDNA: higher throughput, PCR bias possible, not strand-specific
- Correct splice junctions with short-read data when possible
```

---

## Phase 8: Haplotype Phasing

### WhatsHap (Read-Based Phasing)

```bash
# WhatsHap: read-based phasing using long reads
# Phase SNVs using long-read alignment
whatshap phase \
  --reference reference.fa \
  --output phased.vcf.gz \
  --ignore-read-groups \
  variants.vcf.gz \
  aligned.bam

# Index phased VCF
tabix -p vcf phased.vcf.gz

# Tag reads with haplotype
whatshap haplotag \
  --reference reference.fa \
  --output haplotagged.bam \
  phased.vcf.gz \
  aligned.bam

samtools index haplotagged.bam

# Phase statistics
whatshap stats phased.vcf.gz --tsv phasing_stats.tsv
```

### LongPhase

```bash
# LongPhase: fast phasing for long reads
longphase phase \
  -s variants.vcf.gz \
  -b aligned.bam \
  -r reference.fa \
  -t 16 \
  -o longphase_phased \
  --ont  # or --pb for PacBio

# LongPhase can also phase SVs
longphase phase \
  -s snvs.vcf.gz \
  --sv-file svs.vcf.gz \
  -b aligned.bam \
  -r reference.fa \
  -t 16 \
  -o longphase_phased_with_sv \
  --ont
```

### Phasing QC Metrics

| Metric | Good | Acceptable | Poor |
|--------|------|-----------|------|
| **Phase block N50** | >1 Mb | 200 kb - 1 Mb | <200 kb |
| **Phased variants (%)** | >95% | 80-95% | <80% |
| **Switch error rate** | <0.5% | 0.5-2% | >2% |
| **Largest phase block** | >5 Mb | 1-5 Mb | <1 Mb |

### Haplotype-Resolved Applications

```
Phased data enables:
1. Allele-specific expression (from RNA-seq + phased SNVs)
2. Allele-specific methylation (from ONT modified bases + haplotags)
3. Compound heterozygosity assessment (cis vs trans variants)
4. Parent-of-origin analysis (with trio data)
5. Haplotype-resolved de novo assembly

Haplotagged BAM usage:
- HP:i:1 → haplotype 1 reads
- HP:i:2 → haplotype 2 reads
- No HP tag → unphased reads

# Extract haplotype-specific reads
samtools view -b -d HP:1 haplotagged.bam > hap1.bam
samtools view -b -d HP:2 haplotagged.bam > hap2.bam
```

---

## Phase 9: Error Profiles and Filtering

### ONT Error Characteristics

| Error Type | Frequency | Context | Mitigation |
|-----------|-----------|---------|------------|
| **Homopolymer length** | Most common | Runs of ≥4 identical bases | Use sup model, consensus, or polish |
| **Insertion** | ~1-2% (sup) | Random | Filtered by variant callers |
| **Deletion** | ~1-2% (sup) | Homopolymers | Use homopolymer-aware callers |
| **Substitution** | ~0.5% (sup) | Context-dependent | Minimal with sup model |
| **Systematic bias** | Low (R10.4.1) | Specific k-mers | Model-dependent, improving |

### PacBio HiFi Error Characteristics

```
HiFi reads (CCS consensus from multiple passes):
- Overall error rate: <0.1% (Q30+)
- Error type: predominantly random substitutions
- No systematic homopolymer bias (unlike ONT)
- Indel errors: very rare
- Practically no systematic errors remaining

CLR reads (single pass):
- Overall error rate: 10-15%
- Dominated by insertions and deletions
- Require high coverage and consensus for accurate variants
```

### Quality Filtering Recommendations

```bash
# ONT read filtering
# Minimum quality score
samtools view -b -q 20 aligned.bam > filtered.bam

# Length filtering (remove very short reads)
# Using NanoFilt
NanoFilt --quality 10 --length 1000 --maxlength 100000 reads.fastq.gz \
  > filtered_reads.fastq.gz

# PacBio HiFi filtering
# HiFi reads are pre-filtered during CCS generation
# Additional filtering rarely needed
# --min-rq 0.99 during CCS for very stringent quality
```

---

## Phase 10: Adaptive Sampling (ONT)

### ReadFish / MinKNOW Adaptive Sampling

```
Adaptive sampling: reject reads in real-time based on sequence identity
- Read ~400 bp, align against target, keep or reject
- Enrichment: ~5-10x for target regions
- Depletion: remove unwanted sequences (e.g., host DNA in metagenomics)

Configuration (in MinKNOW or ReadFish):
- Target BED file: regions to enrich or deplete
- Decision: accept (sequence fully) or reject (reverse voltage, eject)
- Latency: ~1 second per decision

Use cases:
1. Targeted sequencing without capture/amplification
2. Whole-exome-like enrichment from WGS library
3. Host depletion in metagenomics/clinical samples
4. Real-time pathogen detection (deplete human)

Limitations:
- ~400 bp of each read is "wasted" on initial mapping
- Pore damage from repeated ejection (reduced yield ~20%)
- Requires GPU for real-time basecalling
- Best enrichment for targets >1 Mb total size
```

```bash
# ReadFish configuration (TOML)
# readfish targets --toml targets.toml --device MN12345

# targets.toml example:
# [conditions]
# [conditions.0]
# name = "enrich_genes"
# control = false
# min_chunks = 1
# max_chunks = 4
# targets = "targets.bed"
# single_on = "stop_receiving"   # keep target reads
# single_off = "unblock"          # reject non-target reads
# multi_on = "stop_receiving"
# multi_off = "unblock"
```

---

## Decision Trees

### Overall Long-Read Analysis Strategy

```
Input: Long-read sequencing data
│
├── What platform?
│   ├── ONT → Dorado basecalling → minimap2 -ax map-ont
│   ├── PacBio HiFi → minimap2 -ax map-hifi
│   └── PacBio CLR → minimap2 -ax map-pb
│
├── QC
│   ├── NanoPlot/LongQC → N50, quality, yield
│   ├── Coverage sufficient? → mosdepth
│   └── Failed QC → troubleshoot library/sequencing
│
├── What analysis?
│   ├── SNV/indel calling
│   │   ├── ONT → Clair3 or PEPPER-Margin-DeepVariant
│   │   └── HiFi → DeepVariant or Clair3
│   │
│   ├── Structural variants
│   │   ├── Single sample → Sniffles2 + cuteSV (consensus)
│   │   ├── Population → Sniffles2 multi-sample or Jasmine merge
│   │   └── Annotation → AnnotSV
│   │
│   ├── Methylation (ONT)
│   │   ├── Basecall with --modified-bases
│   │   └── Extract with modkit pileup
│   │
│   ├── Isoform detection
│   │   ├── PacBio → IsoSeq3 pipeline
│   │   └── ONT → FLAIR
│   │
│   ├── Phasing
│   │   ├── WhatsHap or LongPhase
│   │   └── Haplotag reads for allele-specific analysis
│   │
│   └── De novo assembly
│       ├── HiFi → hifiasm (diploid-aware)
│       └── ONT → Flye or Shasta
│
└── Integration
    ├── SV + SNV → compound het assessment with phasing
    ├── Methylation + expression → allele-specific methylation
    └── Isoforms + splicing → alternative-splicing skill
```

### SV Calling Strategy Decision Tree

```
How many callers to use?
│
├── Quick/exploratory → Sniffles2 alone
│
├── Publication-quality → Sniffles2 + cuteSV + SVIM
│   └── Merge with SURVIVOR (require ≥2 callers)
│
├── Population study → Sniffles2 multi-sample (.snf files)
│
└── Clinical → ≥2 callers consensus + manual review of candidates
    └── AnnotSV for clinical annotation

Minimum supporting reads:
├── Low coverage (10-15x) → min_support = 2-3
├── Standard (20-30x) → min_support = 3-5
├── High coverage (>30x) → min_support = 5+
└── Somatic SV → adjust for expected VAF
```

---

## Troubleshooting

```
Basecalling issues:
├── Wrong model → verify chemistry (R9/R10) and kit version
├── Slow basecalling → use GPU, check CUDA drivers
├── No output → check POD5/FAST5 file integrity
└── Low quality scores → try sup model, check run metrics

Alignment issues:
├── Low mapping rate → check species match, contamination
├── Wrong preset → verify map-ont vs map-hifi vs map-pb
├── Supplementary alignments → expected for SVs, don't filter
└── High soft-clipping → may indicate structural variants

SV calling issues:
├── Too many calls → increase min_support, raise MAPQ threshold
├── Too few calls → decrease min_support, check coverage
├── False positive insertions (ONT) → homopolymer artifacts, filter by size
└── Missing large SVs → check max_size parameter

Methylation issues:
├── Low call rate → check modified base model availability
├── Unexpected global methylation → verify correct reference genome
├── No signal → confirm --modified-bases flag during basecalling
└── Per-CpG noise → increase coverage (need >10x per site)
```

## Completeness Checklist

- [ ] Platform and chemistry identified (ONT R10/R9, PacBio HiFi/CLR)
- [ ] Basecalling completed with appropriate model (sup recommended for ONT)
- [ ] Read QC: N50, quality distribution, yield assessed
- [ ] Alignment with correct minimap2 preset
- [ ] Coverage verified (mosdepth/samtools coverage)
- [ ] Variant calling completed (SNV and/or SV as needed)
- [ ] SV calls filtered and annotated
- [ ] Methylation extracted (if ONT with modified bases)
- [ ] Phasing performed (if haplotype resolution needed)
- [ ] Isoforms detected (if RNA/cDNA data)
- [ ] Error profile considered in interpretation
- [ ] Results integrated with other data types as appropriate
