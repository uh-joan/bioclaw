# Alignment Recipes

Computational recipes for sequence alignment, quality control, and variant calling. Each recipe: CLI command + parsing code + output format + pitfalls.

Cross-skill routing:
- `phykit-recipes` — downstream phylogenetic analysis
- `phylogenetics` — study design and conceptual guidance
- `sequence-retrieval` — fetching sequences from databases

---

## 1. BUSCO — Genome/Proteome Completeness

Assess assembly or annotation completeness against lineage-specific orthologs.

```bash
# Protein mode
busco -i proteome.fasta -l eukaryota_odb10 -o busco_out -m proteins -c 8

# Genome mode
busco -i assembly.fasta -l fungi_odb10 -o busco_out -m genome -c 8

# Transcriptome mode
busco -i transcripts.fasta -l metazoa_odb10 -o busco_out -m transcriptome -c 8

# List available lineages
busco --list-datasets
```

**Parse summary:**

```python
import re
from pathlib import Path

def parse_busco_summary(busco_dir: str) -> dict:
    """Parse BUSCO short_summary file."""
    summary_files = list(Path(busco_dir).rglob("short_summary*.txt"))
    if not summary_files:
        raise FileNotFoundError(f"No BUSCO summary in {busco_dir}")

    text = summary_files[0].read_text()

    results = {}
    patterns = {
        "complete": r"(\d+)\s+Complete BUSCOs",
        "single_copy": r"(\d+)\s+Complete and single-copy BUSCOs",
        "duplicated": r"(\d+)\s+Complete and duplicated BUSCOs",
        "fragmented": r"(\d+)\s+Fragmented BUSCOs",
        "missing": r"(\d+)\s+Missing BUSCOs",
        "total": r"(\d+)\s+Total BUSCO groups"
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        results[key] = int(match.group(1)) if match else 0

    total = results["total"]
    if total > 0:
        results["complete_pct"] = results["complete"] / total * 100
        results["fragmented_pct"] = results["fragmented"] / total * 100
        results["missing_pct"] = results["missing"] / total * 100

    return results

busco = parse_busco_summary("busco_out")
print(f"Complete: {busco['complete']}/{busco['total']} ({busco['complete_pct']:.1f}%)")
print(f"  Single-copy: {busco['single_copy']}")
print(f"  Duplicated:  {busco['duplicated']}")
print(f"Fragmented: {busco['fragmented']} ({busco['fragmented_pct']:.1f}%)")
print(f"Missing:    {busco['missing']} ({busco['missing_pct']:.1f}%)")
```

**Batch across species:**

```python
import pandas as pd
from pathlib import Path

species_dirs = Path("busco_results/").iterdir()
rows = []
for sp_dir in species_dirs:
    if sp_dir.is_dir():
        try:
            result = parse_busco_summary(str(sp_dir))
            result["species"] = sp_dir.name
            rows.append(result)
        except FileNotFoundError:
            continue

df = pd.DataFrame(rows)
df = df.sort_values("complete_pct", ascending=False)
print(df[["species", "complete_pct", "duplicated", "fragmented", "missing"]].to_string(index=False))
```

**Pitfalls:**
- Choose the most specific lineage dataset (fungi_odb10 > eukaryota_odb10)
- High duplication in genome mode may indicate polyploidy, not assembly error
- Protein mode is fastest; genome mode slowest (runs gene prediction)

---

## 2. MAFFT — Multiple Sequence Alignment

```bash
# Auto mode (recommended for most cases)
mafft --auto input.fasta > output.aln

# L-INS-i (most accurate, < 200 seqs)
mafft --localpair --maxiterate 1000 input.fasta > output.aln

# FFT-NS-2 (fast, > 2000 seqs)
mafft --retree 2 input.fasta > output.aln

# With threading
mafft --auto --thread 8 input.fasta > output.aln

# Amino acid alignment (explicit)
mafft --amino --auto input.fasta > output.aln
```

**Parse alignment stats:**

```python
from Bio import AlignIO

def alignment_stats(aln_file: str, fmt: str = "fasta") -> dict:
    """Compute basic alignment statistics."""
    aln = AlignIO.read(aln_file, fmt)
    n_seqs = len(aln)
    aln_len = aln.get_alignment_length()

    total_chars = 0
    total_gaps = 0
    for record in aln:
        seq = str(record.seq)
        total_chars += len(seq)
        total_gaps += seq.count("-")

    non_gap = total_chars - total_gaps
    gap_pct = (total_gaps / total_chars * 100) if total_chars > 0 else 0

    return {
        "n_sequences": n_seqs,
        "alignment_length": aln_len,
        "total_characters": total_chars,
        "total_gaps": total_gaps,
        "non_gap_characters": non_gap,
        "gap_percentage": gap_pct
    }

stats = alignment_stats("output.aln")
print(f"Sequences: {stats['n_sequences']}")
print(f"Alignment length: {stats['alignment_length']}")
print(f"Gap percentage: {stats['gap_percentage']:.1f}%")
```

**Pitfalls:**
- `--auto` picks strategy based on sequence count — good default
- Very divergent sequences may need `--localpair`
- Output is FASTA by default; use `--clustalout` for Clustal format
- Redirect stdout (`>`) — MAFFT writes alignment to stdout, logs to stderr

---

## 3. ClipKIT — Alignment Trimming

```bash
# Default (smart-gap mode)
clipkit input.aln -o output.trimmed

# Gappy mode (remove columns > threshold gaps)
clipkit input.aln -m gappy -o output.trimmed -g 0.9

# kpi-gappy (keep parsimony-informative + gappy filter)
clipkit input.aln -m kpi-gappy -o output.trimmed

# Keep log of trimmed sites
clipkit input.aln -o output.trimmed -l
```

**Before/after comparison:**

```python
from Bio import AlignIO

def trimming_report(before_file: str, after_file: str) -> dict:
    before = AlignIO.read(before_file, "fasta")
    after = AlignIO.read(after_file, "fasta")

    before_len = before.get_alignment_length()
    after_len = after.get_alignment_length()
    removed = before_len - after_len
    pct_removed = (removed / before_len * 100) if before_len > 0 else 0

    return {
        "before_length": before_len,
        "after_length": after_len,
        "sites_removed": removed,
        "pct_removed": pct_removed
    }

report = trimming_report("input.aln", "output.trimmed")
print(f"Before: {report['before_length']} sites")
print(f"After:  {report['after_length']} sites")
print(f"Removed: {report['sites_removed']} ({report['pct_removed']:.1f}%)")
```

**Batch trim all alignments:**

```python
import subprocess
from pathlib import Path

aln_dir = Path("alignments/")
out_dir = Path("trimmed/")
out_dir.mkdir(exist_ok=True)

for aln_file in sorted(aln_dir.glob("*.aln")):
    out_file = out_dir / f"{aln_file.stem}.trimmed"
    subprocess.run(
        ["clipkit", str(aln_file), "-o", str(out_file)],
        check=True
    )
    report = trimming_report(str(aln_file), str(out_file))
    print(f"{aln_file.stem}: {report['before_length']} -> {report['after_length']} ({report['pct_removed']:.1f}% removed)")
```

**Pitfalls:**
- Default smart-gap mode is recommended; aggressive trimming can remove signal
- Removing > 50% of sites may indicate alignment quality issues upstream
- ClipKIT preserves parsimony-informative sites by default — better than Gblocks

---

## 4. Trimmomatic — Read Quality Trimming

```bash
# Paired-end
trimmomatic PE -phred33 -threads 8 \
  reads_R1.fastq.gz reads_R2.fastq.gz \
  R1_paired.fastq.gz R1_unpaired.fastq.gz \
  R2_paired.fastq.gz R2_unpaired.fastq.gz \
  ILLUMINACLIP:TruSeq3-PE.fa:2:30:10 \
  LEADING:3 TRAILING:3 SLIDINGWINDOW:4:15 MINLEN:36

# Single-end
trimmomatic SE -phred33 -threads 8 \
  reads.fastq.gz trimmed.fastq.gz \
  ILLUMINACLIP:TruSeq3-SE.fa:2:30:10 \
  LEADING:3 TRAILING:3 SLIDINGWINDOW:4:15 MINLEN:36
```

**Parse Trimmomatic log (stderr):**

```python
import subprocess
import re

def run_trimmomatic_pe(r1: str, r2: str, prefix: str, adapters: str, threads: int = 8) -> dict:
    cmd = [
        "trimmomatic", "PE", "-phred33", "-threads", str(threads),
        r1, r2,
        f"{prefix}_R1_paired.fastq.gz", f"{prefix}_R1_unpaired.fastq.gz",
        f"{prefix}_R2_paired.fastq.gz", f"{prefix}_R2_unpaired.fastq.gz",
        f"ILLUMINACLIP:{adapters}:2:30:10",
        "LEADING:3", "TRAILING:3", "SLIDINGWINDOW:4:15", "MINLEN:36"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Parse summary from stderr
    stderr = result.stderr
    stats = {}
    match = re.search(
        r"Input Read Pairs: (\d+).*?"
        r"Both Surviving: (\d+).*?"
        r"Forward Only Surviving: (\d+).*?"
        r"Reverse Only Surviving: (\d+).*?"
        r"Dropped: (\d+)",
        stderr, re.DOTALL
    )
    if match:
        stats["input_pairs"] = int(match.group(1))
        stats["both_surviving"] = int(match.group(2))
        stats["forward_only"] = int(match.group(3))
        stats["reverse_only"] = int(match.group(4))
        stats["dropped"] = int(match.group(5))
        stats["survival_rate"] = stats["both_surviving"] / stats["input_pairs"] * 100

    return stats

stats = run_trimmomatic_pe(
    "reads_R1.fastq.gz", "reads_R2.fastq.gz",
    "sample1", "TruSeq3-PE.fa"
)
print(f"Input pairs: {stats['input_pairs']:,}")
print(f"Both surviving: {stats['both_surviving']:,} ({stats['survival_rate']:.1f}%)")
print(f"Dropped: {stats['dropped']:,}")
```

**Pitfalls:**
- Adapter file must match your library prep (TruSeq2 vs TruSeq3, PE vs SE)
- SLIDINGWINDOW:4:15 is standard for Illumina; adjust for other platforms
- Run FastQC before and after to verify improvement
- Step order matters: ILLUMINACLIP should come first

---

## 5. BWA-MEM — Read Mapping

```bash
# Index reference (one-time)
bwa index reference.fasta

# Map paired-end reads, add read group, sort output
bwa mem -t 8 -R '@RG\tID:sample1\tSM:sample1\tPL:ILLUMINA\tLB:lib1' \
  reference.fasta R1_paired.fastq.gz R2_paired.fastq.gz | \
  samtools sort -@ 4 -o sample1.bam

# Index BAM
samtools index sample1.bam

# Mark duplicates (optional, recommended before variant calling)
gatk MarkDuplicates -I sample1.bam -O sample1.dedup.bam -M metrics.txt
samtools index sample1.dedup.bam
```

**Coverage calculation:**

```python
import subprocess
import numpy as np

def get_coverage(bam_file: str, region: str = None) -> dict:
    """Calculate coverage statistics from BAM."""
    cmd = ["samtools", "depth", "-a", bam_file]
    if region:
        cmd.extend(["-r", region])

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    depths = []
    for line in result.stdout.strip().split("\n"):
        if line:
            parts = line.split("\t")
            depths.append(int(parts[2]))

    depths = np.array(depths) if depths else np.array([0])
    return {
        "mean_coverage": float(np.mean(depths)),
        "median_coverage": float(np.median(depths)),
        "min_coverage": int(np.min(depths)),
        "max_coverage": int(np.max(depths)),
        "bases_covered": int(np.sum(depths > 0)),
        "total_bases": len(depths),
        "breadth": float(np.sum(depths > 0) / len(depths) * 100),
        "bases_above_10x": float(np.sum(depths >= 10) / len(depths) * 100)
    }

cov = get_coverage("sample1.bam")
print(f"Mean coverage: {cov['mean_coverage']:.1f}x")
print(f"Median coverage: {cov['median_coverage']:.1f}x")
print(f"Breadth (>0x): {cov['breadth']:.1f}%")
print(f"Bases >= 10x: {cov['bases_above_10x']:.1f}%")
```

**Pitfalls:**
- Always add read groups (`-R`) — GATK requires them
- `samtools depth -a` includes zero-coverage positions; without `-a` only covered positions
- Large genomes: pipe through samtools sort to avoid massive unsorted BAMs
- Index both reference (.fai) and BAM (.bai) before downstream tools

---

## 6. GATK HaplotypeCaller — Variant Calling

```bash
# Create sequence dictionary (one-time)
gatk CreateSequenceDictionary -R reference.fasta

# Index reference (one-time, if not done)
samtools faidx reference.fasta

# Call variants
gatk HaplotypeCaller \
  -R reference.fasta \
  -I sample1.dedup.bam \
  -O sample1.g.vcf.gz \
  -ERC GVCF

# Joint genotyping (multi-sample)
gatk CombineGVCFs -R reference.fasta \
  -V sample1.g.vcf.gz -V sample2.g.vcf.gz \
  -O combined.g.vcf.gz

gatk GenotypeGVCFs -R reference.fasta \
  -V combined.g.vcf.gz \
  -O genotyped.vcf.gz
```

**Parse VCF:**

```python
def parse_vcf_stats(vcf_file: str) -> dict:
    """Parse VCF and compute basic variant statistics."""
    import gzip

    opener = gzip.open if vcf_file.endswith(".gz") else open

    snps = 0
    indels = 0
    transitions = 0  # A<->G, C<->T
    transversions = 0
    ts_pairs = {("A", "G"), ("G", "A"), ("C", "T"), ("T", "C")}

    with opener(vcf_file, "rt") as f:
        for line in f:
            if line.startswith("#"):
                continue
            fields = line.strip().split("\t")
            ref = fields[3]
            alts = fields[4].split(",")

            for alt in alts:
                if alt == ".":
                    continue
                if len(ref) == 1 and len(alt) == 1:
                    snps += 1
                    if (ref, alt) in ts_pairs:
                        transitions += 1
                    else:
                        transversions += 1
                else:
                    indels += 1

    ts_tv = transitions / transversions if transversions > 0 else float("inf")
    return {
        "total_variants": snps + indels,
        "snps": snps,
        "indels": indels,
        "transitions": transitions,
        "transversions": transversions,
        "ts_tv_ratio": ts_tv
    }

stats = parse_vcf_stats("genotyped.vcf.gz")
print(f"Total variants: {stats['total_variants']:,}")
print(f"SNPs: {stats['snps']:,}")
print(f"Indels: {stats['indels']:,}")
print(f"Ts/Tv ratio: {stats['ts_tv_ratio']:.2f}")
# Expected Ts/Tv: ~2.0-2.1 for whole genome, ~2.8-3.0 for exomes
```

**Pitfalls:**
- Use GVCF mode (`-ERC GVCF`) for multi-sample workflows
- Ts/Tv < 1.5 may indicate false positive calls
- Reference needs .fai (samtools faidx) and .dict (CreateSequenceDictionary)
- Mark duplicates before calling variants

---

## 7. samtools stats — BAM Statistics

```bash
# Full stats
samtools stats input.bam > stats.txt

# Summary numbers only
samtools stats input.bam | grep ^SN

# Flagstat (quick mapping summary)
samtools flagstat input.bam

# Idxstats (per-chromosome read counts)
samtools idxstats input.bam
```

**Parse samtools stats:**

```python
import subprocess

def parse_samtools_stats(bam_file: str) -> dict:
    result = subprocess.run(
        ["samtools", "stats", bam_file],
        capture_output=True, text=True, check=True
    )

    stats = {}
    for line in result.stdout.split("\n"):
        if line.startswith("SN\t"):
            parts = line.split("\t")
            key = parts[1].rstrip(":")
            try:
                stats[key] = int(parts[2])
            except ValueError:
                try:
                    stats[key] = float(parts[2])
                except ValueError:
                    stats[key] = parts[2]

    return stats

def parse_flagstat(bam_file: str) -> dict:
    result = subprocess.run(
        ["samtools", "flagstat", bam_file],
        capture_output=True, text=True, check=True
    )
    import re
    stats = {}
    lines = result.stdout.strip().split("\n")
    for line in lines:
        match = re.match(r"(\d+)\s+\+\s+(\d+)\s+(.*)", line)
        if match:
            stats[match.group(3).strip()] = int(match.group(1))
    return stats

stats = parse_samtools_stats("sample1.bam")
print(f"Total reads: {stats.get('raw total sequences', 'N/A'):,}")
print(f"Mapped reads: {stats.get('reads mapped', 'N/A'):,}")
print(f"Error rate: {stats.get('error rate', 'N/A')}")
print(f"Average quality: {stats.get('average quality', 'N/A')}")
print(f"Insert size avg: {stats.get('insert size average', 'N/A')}")

flagstat = parse_flagstat("sample1.bam")
total = flagstat.get("in total (QC-passed reads + QC-failed reads)", 0)
mapped = flagstat.get("mapped", 0)
print(f"\nMapping rate: {mapped/total*100:.1f}%" if total > 0 else "")
```

**Pitfalls:**
- `samtools stats` is comprehensive but slow on large BAMs
- `samtools flagstat` is fast for a quick mapping summary
- Filter by quality first if needed: `samtools view -q 20 -b input.bam`

---

## 8. Sequence Counting — Total Characters in FASTA

```python
from Bio import SeqIO

def count_sequences(fasta_file: str) -> dict:
    """Count sequences and total residues in FASTA."""
    n_seqs = 0
    total_len = 0
    lengths = []
    for record in SeqIO.parse(fasta_file, "fasta"):
        n_seqs += 1
        seq_len = len(record.seq)
        total_len += seq_len
        lengths.append(seq_len)

    lengths.sort(reverse=True)
    # N50 calculation
    cumsum = 0
    n50 = 0
    for l in lengths:
        cumsum += l
        if cumsum >= total_len / 2:
            n50 = l
            break

    return {
        "n_sequences": n_seqs,
        "total_residues": total_len,
        "mean_length": total_len / n_seqs if n_seqs > 0 else 0,
        "min_length": min(lengths) if lengths else 0,
        "max_length": max(lengths) if lengths else 0,
        "n50": n50
    }

stats = count_sequences("proteome.fasta")
print(f"Sequences: {stats['n_sequences']:,}")
print(f"Total residues: {stats['total_residues']:,}")
print(f"Mean length: {stats['mean_length']:.0f}")
print(f"N50: {stats['n50']:,}")
```

**No BioPython alternative:**

```python
def count_fasta_simple(fasta_file: str) -> tuple[int, int]:
    """Count sequences and total characters without BioPython."""
    n_seqs = 0
    total = 0
    with open(fasta_file) as f:
        for line in f:
            if line.startswith(">"):
                n_seqs += 1
            else:
                total += len(line.strip())
    return n_seqs, total

n, total = count_fasta_simple("proteome.fasta")
print(f"{n} sequences, {total} residues")
```

---

## 9. Gap Analysis — Alignment Quality

```python
from Bio import AlignIO
import numpy as np

def gap_analysis(aln_file: str, fmt: str = "fasta") -> dict:
    """Detailed gap analysis of a multiple sequence alignment."""
    aln = AlignIO.read(aln_file, fmt)
    n_seqs = len(aln)
    aln_len = aln.get_alignment_length()

    # Per-position gap counts
    gap_counts = np.zeros(aln_len, dtype=int)
    per_seq_gaps = []

    for record in aln:
        seq = str(record.seq)
        seq_gaps = seq.count("-")
        per_seq_gaps.append({
            "taxon": record.id,
            "gaps": seq_gaps,
            "gap_pct": seq_gaps / aln_len * 100
        })
        for i, char in enumerate(seq):
            if char == "-":
                gap_counts[i] += 1

    # Position stats
    gap_fractions = gap_counts / n_seqs
    fully_gapped = int(np.sum(gap_counts == n_seqs))
    mostly_gapped = int(np.sum(gap_fractions > 0.5))
    no_gaps = int(np.sum(gap_counts == 0))

    return {
        "alignment_length": aln_len,
        "n_sequences": n_seqs,
        "positions_no_gaps": no_gaps,
        "positions_mostly_gapped": mostly_gapped,
        "positions_fully_gapped": fully_gapped,
        "mean_gap_fraction": float(np.mean(gap_fractions)),
        "per_sequence": sorted(per_seq_gaps, key=lambda x: -x["gap_pct"])
    }

result = gap_analysis("output.aln")
print(f"Alignment: {result['alignment_length']} positions, {result['n_sequences']} sequences")
print(f"No gaps: {result['positions_no_gaps']} positions")
print(f"Mostly gapped (>50%): {result['positions_mostly_gapped']} positions")
print(f"Mean gap fraction: {result['mean_gap_fraction']:.3f}")
print("\nTop gappy sequences:")
for s in result["per_sequence"][:5]:
    print(f"  {s['taxon']}: {s['gap_pct']:.1f}%")
```

---

## Quick Reference

| Tool | Command | Purpose |
|------|---------|---------|
| BUSCO | `busco -i <in> -l <lineage> -m <mode>` | Completeness assessment |
| MAFFT | `mafft --auto <in> > <out>` | Multiple alignment |
| ClipKIT | `clipkit <in> -o <out>` | Alignment trimming |
| Trimmomatic | `trimmomatic PE ...` | Read quality trimming |
| BWA-MEM | `bwa mem <ref> <R1> <R2> \| samtools sort` | Read mapping |
| GATK HC | `gatk HaplotypeCaller -R <ref> -I <bam> -O <vcf>` | Variant calling |
| samtools stats | `samtools stats <bam>` | BAM statistics |

## Install

```bash
# Conda (recommended for bioinformatics)
conda install -c bioconda busco mafft clipkit trimmomatic bwa samtools gatk4

# Pip (Python tools only)
pip install clipkit biopython
```
