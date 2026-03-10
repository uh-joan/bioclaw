# Nextflow and nf-core Pipeline Recipes

Code templates for running nf-core community pipelines, acquiring public data from GEO/SRA, generating samplesheets, writing custom Nextflow processes, configuring execution profiles, managing resources, and handling reference genomes.

Cross-skill routing: use `SKILL.md` for general Nextflow/Snakemake/CWL/WDL concepts, `single-cell-analysis` for scRNA-seq analysis downstream of pipeline output.

---

## 1. nf-core/rnaseq: Bulk RNA-seq Pipeline

Run the community-standard RNA-seq pipeline with STAR + Salmon quantification.

```bash
#!/bin/bash
# nf-core/rnaseq with STAR-Salmon aligner and GRCh38 reference

# Samplesheet format (samplesheet.csv):
# sample,fastq_1,fastq_2,strandedness
# CONTROL_REP1,/data/fastq/ctrl1_R1.fastq.gz,/data/fastq/ctrl1_R2.fastq.gz,auto
# CONTROL_REP2,/data/fastq/ctrl2_R1.fastq.gz,/data/fastq/ctrl2_R2.fastq.gz,auto
# TREATED_REP1,/data/fastq/treat1_R1.fastq.gz,/data/fastq/treat1_R2.fastq.gz,auto
# TREATED_REP2,/data/fastq/treat2_R1.fastq.gz,/data/fastq/treat2_R2.fastq.gz,auto

nextflow run nf-core/rnaseq \
    -r 3.14.0 \
    -profile docker \
    --input samplesheet.csv \
    --outdir results/rnaseq \
    --genome GRCh38 \
    --aligner star_salmon \
    --extra_star_align_args '--outSAMtype BAM SortedByCoordinate --quantMode GeneCounts' \
    --skip_biotype_qc false \
    --min_mapped_reads 5 \
    -with-report report.html \
    -with-trace trace.txt \
    -with-timeline timeline.html \
    -resume
```

**Key parameters**:
- `--aligner star_salmon`: STAR alignment + Salmon quantification (most accurate for DE analysis). Alternatives: `hisat2`, `salmon` (pseudo-alignment only).
- `--genome GRCh38`: Uses iGenomes reference. For mouse: `GRCm39`. For custom genome, use `--fasta` and `--gtf` instead.
- `--strandedness auto`: Auto-detect strandedness from first reads. Explicit options: `forward`, `reverse`, `unstranded`.
- `-resume`: Skip completed processes on re-run (uses Nextflow cache).

**Expected output**: `results/rnaseq/` containing: `star_salmon/` (BAM files, gene counts), `multiqc/multiqc_report.html` (comprehensive QC), `salmon/` (TPM/count matrices), `fastqc/`, `trimgalore/`.

---

## 2. nf-core/sarek: Somatic Variant Calling

Run tumor/normal variant calling with Mutect2 and Strelka.

```bash
#!/bin/bash
# nf-core/sarek for somatic variant calling

# Samplesheet format (samplesheet.csv):
# patient,sample,lane,fastq_1,fastq_2,status
# PATIENT1,TUMOR,lane1,/data/tumor_R1.fastq.gz,/data/tumor_R2.fastq.gz,1
# PATIENT1,NORMAL,lane1,/data/normal_R1.fastq.gz,/data/normal_R2.fastq.gz,0
# PATIENT2,TUMOR,lane1,/data/p2_tumor_R1.fastq.gz,/data/p2_tumor_R2.fastq.gz,1
# PATIENT2,NORMAL,lane1,/data/p2_normal_R1.fastq.gz,/data/p2_normal_R2.fastq.gz,0
#
# status: 0 = normal, 1 = tumor

nextflow run nf-core/sarek \
    -r 3.4.4 \
    -profile docker \
    --input samplesheet.csv \
    --outdir results/sarek \
    --genome GATK.GRCh38 \
    --tools mutect2,strelka,vep \
    --joint_germline false \
    --wes false \
    --intervals /data/targets.bed \
    --pon /data/pon.vcf.gz \
    --pon_index /data/pon.vcf.gz.tbi \
    -with-report report.html \
    -resume

# For WES (whole exome), add:
# --wes true --intervals /data/exome_targets.bed

# For germline-only analysis:
# nextflow run nf-core/sarek -r 3.4.4 \
#     --input samplesheet_germline.csv \
#     --genome GATK.GRCh38 \
#     --tools haplotypecaller,deepvariant,vep \
#     -profile docker
```

**Key parameters**:
- `--genome GATK.GRCh38`: GATK bundle reference (includes known sites for BQSR). For mouse: `GATK.GRCm39`.
- `--tools mutect2,strelka,vep`: Somatic callers + VEP annotation. Other callers: `freebayes`, `manta` (SVs), `cnvkit`, `tiddit`.
- `--pon`: Panel of normals VCF for Mutect2 artifact filtering.
- `--intervals`: BED file for targeted sequencing (WES/panel). Omit for WGS.
- `status`: In samplesheet, 0=normal, 1=tumor. Patient column links tumor-normal pairs.

**Expected output**: `results/sarek/` with: `variant_calling/mutect2/` (filtered VCFs), `variant_calling/strelka/` (SNVs + indels), `annotation/vep/` (annotated VCFs), `reports/` (MultiQC, BAM stats).

---

## 3. nf-core/atacseq: ATAC-seq Pipeline

Run ATAC-seq peak calling with replicate-aware analysis.

```bash
#!/bin/bash
# nf-core/atacseq with replicate groups

# Samplesheet format (samplesheet.csv):
# sample,fastq_1,fastq_2,replicate
# CONTROL,/data/ctrl_rep1_R1.fastq.gz,/data/ctrl_rep1_R2.fastq.gz,1
# CONTROL,/data/ctrl_rep2_R1.fastq.gz,/data/ctrl_rep2_R2.fastq.gz,2
# TREATED,/data/treat_rep1_R1.fastq.gz,/data/treat_rep1_R2.fastq.gz,1
# TREATED,/data/treat_rep2_R1.fastq.gz,/data/treat_rep2_R2.fastq.gz,2
#
# Replicates with same sample name are merged for peak calling

nextflow run nf-core/atacseq \
    -r 2.1.2 \
    -profile docker \
    --input samplesheet.csv \
    --outdir results/atacseq \
    --genome GRCh38 \
    --narrow_peak \
    --min_trimmed_reads 10000 \
    --macs_gsize 2.7e9 \
    --keep_dups false \
    --skip_diff_analysis false \
    -with-report report.html \
    -resume

# For broad peaks (histone marks like H3K27me3):
# --broad_cutoff 0.1 (instead of --narrow_peak)
```

**Key parameters**:
- `--narrow_peak`: Call narrow peaks with MACS2 (standard for ATAC-seq). For histone ChIP with broad marks, use `--broad_cutoff 0.1`.
- `--macs_gsize`: Effective genome size. Human: `2.7e9`, Mouse: `1.87e9`.
- `replicate` column: Replicates with the same sample name are processed individually for QC, then merged for consensus peak calling.
- `--keep_dups false`: Remove PCR duplicates (essential for ATAC-seq).

**Expected output**: `results/atacseq/` with: `macs2/narrow_peak/` (peak files per sample), `macs2/consensus/` (consensus peaks across replicates), `bigwig/` (normalized coverage tracks), `multiqc/`, `picard/` (insert size distributions).

---

## 4. GEO/SRA Data Acquisition

Fetch metadata and download FASTQ files from public repositories.

```python
import subprocess
import os
import pandas as pd
from Bio import Entrez

def fetch_geo_metadata(geo_accession: str, email: str = "user@example.com") -> pd.DataFrame:
    """Fetch sample metadata from GEO using NCBI Entrez.

    Parameters
    ----------
    geo_accession : str
        GEO series accession (e.g., 'GSE123456').
    email : str
        Email for NCBI Entrez API (required).

    Returns
    -------
    pd.DataFrame with sample metadata including SRR accessions.
    """
    Entrez.email = email

    # Search GEO for the series
    handle = Entrez.esearch(db="gds", term=f"{geo_accession}[Accession]")
    record = Entrez.read(handle)
    handle.close()

    if not record["IdList"]:
        raise ValueError(f"No GEO record found for {geo_accession}")

    # Get series metadata
    handle = Entrez.esummary(db="gds", id=record["IdList"][0])
    summary = Entrez.read(handle)
    handle.close()

    print(f"Title: {summary[0].get('title', 'N/A')}")
    print(f"Summary: {summary[0].get('summary', 'N/A')[:200]}...")

    # Get SRA accessions linked to the GEO series
    handle = Entrez.esearch(db="sra", term=f"{geo_accession}[All Fields]", retmax=500)
    sra_ids = Entrez.read(handle)
    handle.close()

    samples = []
    for sra_id in sra_ids["IdList"]:
        handle = Entrez.efetch(db="sra", id=sra_id, rettype="full", retmode="xml")
        sra_record = Entrez.read(handle)
        handle.close()

        for exp_pkg in sra_record:
            for run in exp_pkg.get("RUN_SET", {}).get("RUN", []):
                samples.append({
                    "srr": run.get("accession", ""),
                    "title": exp_pkg.get("SAMPLE", {}).get("TITLE", ""),
                    "organism": exp_pkg.get("SAMPLE", {}).get("SAMPLE_NAME", {}).get("SCIENTIFIC_NAME", ""),
                })

    df = pd.DataFrame(samples)
    print(f"\nFound {len(df)} runs")
    print(df)
    return df

def download_fastqs_ena(srr_list: list, outdir: str = "fastq", threads: int = 8):
    """Download FASTQ files from ENA (faster than SRA for most locations).

    Parameters
    ----------
    srr_list : list
        List of SRR accession numbers.
    outdir : str
        Output directory for FASTQ files.
    threads : int
        Download threads for wget/aria2c.

    Returns
    -------
    List of downloaded file paths.
    """
    os.makedirs(outdir, exist_ok=True)
    downloaded = []

    for srr in srr_list:
        # Construct ENA FTP path
        prefix = srr[:6]
        if len(srr) > 9:
            subdir = f"0{srr[-2:]}" if len(srr) == 11 else f"00{srr[-1]}" if len(srr) == 10 else ""
            ftp_base = f"ftp://ftp.sra.ebi.ac.uk/vol1/fastq/{prefix}/{subdir}/{srr}"
        else:
            ftp_base = f"ftp://ftp.sra.ebi.ac.uk/vol1/fastq/{prefix}/{srr}"

        # Try paired-end first, fall back to single-end
        for suffix in [f"/{srr}_1.fastq.gz", f"/{srr}_2.fastq.gz", f"/{srr}.fastq.gz"]:
            url = ftp_base + suffix.split("/")[-1]
            outfile = os.path.join(outdir, suffix.split("/")[-1])
            cmd = f"wget -q -O {outfile} {url}"
            result = subprocess.run(cmd, shell=True)
            if result.returncode == 0:
                downloaded.append(outfile)
                print(f"  Downloaded: {outfile}")

    print(f"\nTotal files: {len(downloaded)}")
    return downloaded

# Alternative: use nf-core/fetchngs for automated download
def fetchngs_command(accession_list_file: str, outdir: str = "fastq"):
    """Generate nf-core/fetchngs command for automated SRA download.

    Parameters
    ----------
    accession_list_file : str
        Text file with one SRR/SRX/GSE/GSM accession per line.
    outdir : str
        Output directory.

    Returns
    -------
    str: Nextflow command to run.
    """
    cmd = (
        f"nextflow run nf-core/fetchngs "
        f"-r 1.12.0 "
        f"-profile docker "
        f"--input {accession_list_file} "
        f"--outdir {outdir} "
        f"--nf_core_pipeline rnaseq "
        f"--download_method aspera "
    )
    print(f"Run:\n  {cmd}")
    print(f"\nInput file format ({accession_list_file}):")
    print("  SRR12345678")
    print("  SRR12345679")
    print("  SRR12345680")
    return cmd

# Usage
# metadata = fetch_geo_metadata("GSE123456")
# download_fastqs_ena(metadata["srr"].tolist(), outdir="fastq")
# Or: fetchngs_command("accessions.txt", outdir="fastq")
```

**Expected output**: DataFrame with sample metadata (SRR accessions, titles, organism). FASTQ files downloaded to output directory. nf-core/fetchngs can also auto-generate samplesheets compatible with downstream nf-core pipelines.

---

## 5. Samplesheet Generation from Downloaded FASTQs

Auto-detect paired-end reads and generate nf-core-compatible samplesheets.

```python
import os
import re
import pandas as pd
from pathlib import Path

def generate_samplesheet(fastq_dir: str, output: str = "samplesheet.csv",
                         pipeline: str = "rnaseq", strandedness: str = "auto"):
    """Generate nf-core samplesheet by auto-detecting R1/R2 pairs.

    Parameters
    ----------
    fastq_dir : str
        Directory containing FASTQ files.
    output : str
        Output samplesheet path.
    pipeline : str
        Target pipeline: 'rnaseq', 'sarek', 'atacseq'. Changes column format.
    strandedness : str
        Strandedness for RNA-seq: 'auto', 'forward', 'reverse', 'unstranded'.

    Returns
    -------
    pd.DataFrame with samplesheet contents.
    """
    fastq_dir = Path(fastq_dir).resolve()
    fastq_files = sorted(fastq_dir.glob("*.fastq.gz"))

    if not fastq_files:
        fastq_files = sorted(fastq_dir.glob("*.fq.gz"))

    print(f"Found {len(fastq_files)} FASTQ files in {fastq_dir}")

    # Match R1/R2 pairs using common naming patterns
    r1_patterns = [
        r"(.+?)(?:_R1|_1|\.R1|\.1)(?:_\d+)?\.(?:fastq|fq)\.gz$",
    ]
    r2_patterns = [
        r"(.+?)(?:_R2|_2|\.R2|\.2)(?:_\d+)?\.(?:fastq|fq)\.gz$",
    ]

    r1_files = {}
    r2_files = {}

    for f in fastq_files:
        name = f.name
        for pattern in r1_patterns:
            m = re.match(pattern, name)
            if m:
                r1_files[m.group(1)] = str(f)
                break
        for pattern in r2_patterns:
            m = re.match(pattern, name)
            if m:
                r2_files[m.group(1)] = str(f)
                break

    # Build samplesheet
    rows = []
    for sample_base in sorted(set(r1_files.keys()) | set(r2_files.keys())):
        r1 = r1_files.get(sample_base, "")
        r2 = r2_files.get(sample_base, "")

        # Extract sample name (remove lane/run info)
        sample_name = re.sub(r"_S\d+(_L\d+)?$", "", sample_base)
        sample_name = re.sub(r"_lane\d+$", "", sample_name)

        if pipeline == "rnaseq":
            rows.append({
                "sample": sample_name,
                "fastq_1": r1,
                "fastq_2": r2,
                "strandedness": strandedness,
            })
        elif pipeline == "sarek":
            rows.append({
                "patient": sample_name.split("_")[0],
                "sample": sample_name,
                "lane": "lane1",
                "fastq_1": r1,
                "fastq_2": r2,
                "status": 0,  # default to normal; edit manually for tumor samples
            })
        elif pipeline == "atacseq":
            rows.append({
                "sample": sample_name,
                "fastq_1": r1,
                "fastq_2": r2,
                "replicate": 1,
            })

    df = pd.DataFrame(rows)

    # Validate
    n_paired = (df["fastq_2"] != "").sum()
    n_single = (df["fastq_2"] == "").sum()
    print(f"Samples: {len(df)} ({n_paired} paired-end, {n_single} single-end)")

    df.to_csv(output, index=False)
    print(f"Samplesheet saved: {output}")
    print(df.to_string(index=False))

    return df

# Usage
samplesheet = generate_samplesheet("fastq/", output="samplesheet.csv", pipeline="rnaseq")

# For sarek, edit status column manually:
# samplesheet.loc[samplesheet["sample"].str.contains("tumor", case=False), "status"] = 1
# samplesheet.to_csv("samplesheet.csv", index=False)
```

**Expected output**: CSV samplesheet compatible with the target nf-core pipeline. Auto-detects R1/R2 pairs from filename patterns (_R1/_R2, _1/_2). Review and edit sample names and metadata before running.

---

## 6. Custom Nextflow Process Definition (DSL2)

Write a custom Nextflow process with proper input/output channels.

```groovy
// === Custom DSL2 Process Template ===
// File: modules/local/custom_analysis/main.nf

nextflow.enable.dsl = 2

process CUSTOM_ANALYSIS {
    tag "${meta.id}"        // Process tag for logging
    label 'process_medium'   // Resource label (defined in config)

    // Container specification
    container 'quay.io/biocontainers/samtools:1.17--h6b7c446_2'

    // Output publishing
    publishDir "${params.outdir}/custom_analysis", mode: 'copy',
        saveAs: { filename -> filename.endsWith('.log') ? "logs/$filename" : filename }

    // Error handling
    errorStrategy { task.exitStatus in [137, 140, 143] ? 'retry' : 'finish' }
    maxRetries 2

    input:
    tuple val(meta), path(bam), path(bai)  // meta map with sample info
    path(reference)                         // reference genome
    val(extra_args)                          // optional extra arguments

    output:
    tuple val(meta), path("*.filtered.bam"), path("*.filtered.bam.bai"), emit: filtered_bam
    path("*.stats.txt"),                                                  emit: stats
    path("*.log"),                                                        emit: log
    path("versions.yml"),                                                 emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    # Run analysis
    samtools view \\
        -b -q 30 -F 4 \\
        --threads ${task.cpus} \\
        ${args} \\
        ${bam} \\
        -o ${prefix}.filtered.bam

    samtools index ${prefix}.filtered.bam
    samtools flagstat ${prefix}.filtered.bam > ${prefix}.stats.txt

    # Version tracking
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        samtools: \$(samtools --version | head -1 | sed 's/samtools //')
    END_VERSIONS

    echo "Completed: ${prefix}" > ${prefix}.log
    """

    stub:
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    touch ${prefix}.filtered.bam
    touch ${prefix}.filtered.bam.bai
    touch ${prefix}.stats.txt
    touch ${prefix}.log
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        samtools: 1.17
    END_VERSIONS
    """
}

// === Workflow using the custom process ===
// File: workflows/custom_pipeline.nf

include { CUSTOM_ANALYSIS } from '../modules/local/custom_analysis/main'

workflow CUSTOM_PIPELINE {
    take:
    bam_ch          // channel: [ val(meta), path(bam), path(bai) ]
    reference_ch    // channel: path(reference)

    main:
    CUSTOM_ANALYSIS(
        bam_ch,
        reference_ch,
        params.extra_args ?: '',
    )

    emit:
    filtered_bam = CUSTOM_ANALYSIS.out.filtered_bam
    stats        = CUSTOM_ANALYSIS.out.stats
    versions     = CUSTOM_ANALYSIS.out.versions
}
```

**Key elements**:
- `tag`: Identifies which sample is running in logs.
- `label`: Maps to resource definitions in nextflow.config.
- `meta` map: Carries sample metadata through the pipeline (e.g., `[id: 'sample1', single_end: false]`).
- `stub` block: Mock outputs for `-stub-run` testing.
- `versions.yml`: Standard nf-core version tracking format.
- `task.ext.args`: Allows config-level argument injection without modifying the process.

**Expected output**: Filtered BAM file, index, flagstat statistics, and version tracking file. The `stub` block enables fast dry-run testing.

---

## 7. Nextflow Config Profiles: Local, Docker, Singularity, SLURM

Configure execution environments for different compute platforms.

```groovy
// === nextflow.config ===

// Default parameters
params {
    input         = null
    outdir        = 'results'
    genome        = 'GRCh38'
    max_cpus      = 16
    max_memory    = '128.GB'
    max_time      = '72.h'
    extra_args    = ''
}

// Resource labels
process {
    withLabel: 'process_low' {
        cpus   = { check_max(2, 'cpus') }
        memory = { check_max(4.GB * task.attempt, 'memory') }
        time   = { check_max(4.h * task.attempt, 'time') }
    }
    withLabel: 'process_medium' {
        cpus   = { check_max(8, 'cpus') }
        memory = { check_max(16.GB * task.attempt, 'memory') }
        time   = { check_max(12.h * task.attempt, 'time') }
    }
    withLabel: 'process_high' {
        cpus   = { check_max(16, 'cpus') }
        memory = { check_max(64.GB * task.attempt, 'memory') }
        time   = { check_max(24.h * task.attempt, 'time') }
    }
    withLabel: 'process_high_memory' {
        cpus   = { check_max(8, 'cpus') }
        memory = { check_max(128.GB * task.attempt, 'memory') }
        time   = { check_max(24.h * task.attempt, 'time') }
    }
}

// Profiles
profiles {
    local {
        process.executor = 'local'
        docker.enabled   = true
        docker.runOptions = '-u $(id -u):$(id -g)'
    }

    docker {
        docker.enabled    = true
        docker.runOptions = '-u $(id -u):$(id -g)'
        singularity.enabled = false
    }

    singularity {
        singularity.enabled    = true
        singularity.autoMounts = true
        singularity.cacheDir   = "${HOME}/.singularity/cache"
        docker.enabled         = false
    }

    slurm {
        process.executor       = 'slurm'
        process.queue          = 'normal'
        process.clusterOptions = '--account=myproject'
        singularity.enabled    = true
        singularity.autoMounts = true
        singularity.cacheDir   = '/scratch/singularity_cache'

        // Queue-specific overrides
        process {
            withLabel: 'process_high_memory' {
                queue = 'highmem'
            }
        }
    }

    test {
        params.input     = "${baseDir}/test_data/samplesheet.csv"
        params.genome    = 'GRCh38'
        params.max_cpus  = 2
        params.max_memory = '6.GB'
        params.max_time  = '1.h'
    }
}

// Helper function: cap resources at max
def check_max(obj, type) {
    if (type == 'memory') {
        try {
            if (obj.compareTo(params.max_memory as nextflow.util.MemoryUnit) == 1)
                return params.max_memory as nextflow.util.MemoryUnit
            else
                return obj
        } catch (all) {
            println "WARNING: Max memory '${params.max_memory}' is not valid. Using default."
            return obj
        }
    } else if (type == 'time') {
        try {
            if (obj.compareTo(params.max_time as nextflow.util.Duration) == 1)
                return params.max_time as nextflow.util.Duration
            else
                return obj
        } catch (all) {
            println "WARNING: Max time '${params.max_time}' is not valid. Using default."
            return obj
        }
    } else if (type == 'cpus') {
        try {
            return Math.min(obj, params.max_cpus as int)
        } catch (all) {
            println "WARNING: Max cpus '${params.max_cpus}' is not valid. Using default."
            return obj
        }
    }
}
```

**Key concepts**:
- Resource labels (`process_low`, `process_medium`, etc.) decouple resource needs from process definitions.
- `task.attempt` enables dynamic scaling: memory doubles on each retry for OOM errors.
- `check_max` prevents processes from exceeding system limits.
- SLURM profile sets executor, queue, and account for HPC submission.
- Singularity for HPC (no root), Docker for local/cloud.

**Expected output**: Configuration file enabling `nextflow run main.nf -profile docker`, `-profile slurm`, or `-profile test` execution.

---

## 8. Resource Management: Per-Process Allocation and Error Strategy

Configure memory, CPUs, time, and retry behavior for each pipeline step.

```groovy
// === Resource management in nextflow.config ===

process {
    // Default error strategy: retry on OOM, finish on other errors
    errorStrategy = { task.exitStatus in [137, 140, 143] ? 'retry' : 'finish' }
    maxRetries = 3
    maxErrors = '-1'  // don't stop on retryable errors

    // Dynamic memory scaling on retry
    withName: 'STAR_ALIGN' {
        cpus   = 8
        memory = { 32.GB * task.attempt }
        time   = { 8.h * task.attempt }
        // Exit 137 = OOM kill, 140 = SIGTERM (timeout), 143 = SIGTERM
    }

    withName: 'SAMTOOLS_SORT' {
        cpus   = 4
        memory = { 8.GB * task.attempt }
        time   = '4h'
    }

    withName: 'GATK_HAPLOTYPECALLER' {
        cpus   = 4
        memory = { 16.GB * task.attempt }
        time   = { 12.h * task.attempt }
    }

    withName: 'FASTQC' {
        cpus   = 2
        memory = '4 GB'
        time   = '2h'
        // FastQC rarely OOMs; no retry needed
        errorStrategy = 'finish'
    }

    withName: 'MULTIQC' {
        cpus   = 1
        memory = '4 GB'
        time   = '1h'
    }

    // Catch-all for unlabeled processes
    cpus   = { check_max(1, 'cpus') }
    memory = { check_max(4.GB, 'memory') }
    time   = { check_max(4.h, 'time') }
}

// Resource allocation reference:
// ┌──────────────────────┬──────┬────────┬──────┐
// │ Process              │ CPUs │ Memory │ Time │
// ├──────────────────────┼──────┼────────┼──────┤
// │ FastQC               │  2   │  4 GB  │  2h  │
// │ Trimming             │  4   │  8 GB  │  2h  │
// │ STAR alignment       │  8   │ 32 GB  │  8h  │
// │ STAR genome generate │  8   │ 64 GB  │  2h  │
// │ BWA-MEM2 alignment   │  8   │ 16 GB  │  8h  │
// │ samtools sort/index   │  4   │  8 GB  │  2h  │
// │ GATK HaplotypeCaller │  4   │ 16 GB  │ 12h  │
// │ DeepVariant          │  8   │ 32 GB  │  8h  │
// │ MACS2 peak calling   │  2   │  8 GB  │  2h  │
// │ featureCounts        │  4   │  8 GB  │ 30m  │
// │ DESeq2               │  1   │  8 GB  │ 30m  │
// │ MultiQC              │  1   │  4 GB  │ 15m  │
// └──────────────────────┴──────┴────────┴──────┘
```

**Key parameters**:
- `errorStrategy`: `'retry'` for OOM/timeout, `'finish'` to complete running tasks then stop, `'ignore'` to skip failed samples.
- `maxRetries`: Maximum retry attempts per process instance.
- Dynamic resources: `{ 32.GB * task.attempt }` doubles memory on each retry.
- Exit codes: 137 = Linux OOM killer (SIGKILL), 140 = shell timeout, 143 = SIGTERM.

**Expected output**: Pipeline that auto-scales resources on failure and retries OOM-killed processes with more memory, while failing fast on genuine errors.

---

## 9. Resume Failed Pipelines

Resume a partially completed pipeline from the last checkpoint.

```bash
#!/bin/bash
# === Resume strategies for Nextflow pipelines ===

# Basic resume: reuse cached results for completed processes
nextflow run nf-core/rnaseq \
    -r 3.14.0 \
    -profile docker \
    --input samplesheet.csv \
    --outdir results \
    --genome GRCh38 \
    -resume

# Resume from a specific session
nextflow log                        # list previous runs
nextflow run main.nf -resume abc123 # resume specific session ID

# Resume after modifying a failed process (only re-runs affected processes)
# 1. Fix the issue (e.g., increase memory in config)
# 2. Re-run with -resume
nextflow run main.nf -resume

# Clean up work directory (remove old cached files)
nextflow clean -f -before 2024-01-01  # remove runs before date
nextflow clean -f -but last           # keep only the last run

# Troubleshoot resume failures:
# 1. Check what ran and what was cached:
nextflow log last -f hash,name,status,exit

# 2. Inspect a specific task's work directory:
nextflow log last -f workdir,name | head -20
# Then: ls -la /path/to/work/ab/cdef1234/

# 3. View task-level resource usage:
# Open trace.txt or timeline.html from previous run

# Force re-run of a specific process (invalidate its cache):
# Method: touch an input file or change a parameter that affects the process
# Or: delete the process hash from the .nextflow/ directory
```

**Key concepts**:
- `-resume` matches processes by hash (inputs + script + container). Unchanged processes are skipped.
- Modifying a process script invalidates its cache and all downstream processes.
- Changing parameters only invalidates processes that use those parameters.
- `nextflow log` shows run history with session IDs for targeted resume.
- Work directory (`work/`) stores intermediate files; clean periodically to reclaim disk space.

**Expected output**: Pipeline continues from the last successful checkpoint, saving compute time and cost. Typical resume for a 50-sample RNA-seq pipeline: 90%+ processes cached, only failed/modified processes re-run.

---

## 10. Custom nf-core Module: main.nf + meta.yml

Create a module following nf-core conventions for reusability.

```groovy
// === modules/local/deseq2/main.nf ===

process DESEQ2 {
    tag "$meta.id"
    label 'process_low'

    conda "bioconda::bioconductor-deseq2=1.40.0"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/bioconductor-deseq2:1.40.0' :
        'quay.io/biocontainers/bioconductor-deseq2:1.40.0' }"

    publishDir "${params.outdir}/deseq2", mode: 'copy'

    input:
    tuple val(meta), path(counts)
    path(samplesheet)

    output:
    tuple val(meta), path("*_deseq2_results.csv"), emit: results
    tuple val(meta), path("*_normalized_counts.csv"), emit: normalized
    path("*_pca.png"), emit: pca
    path("*_volcano.png"), emit: volcano
    path("versions.yml"), emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    #!/usr/bin/env Rscript

    library(DESeq2)

    # Load count matrix and sample info
    counts <- read.csv("${counts}", row.names=1, check.names=FALSE)
    coldata <- read.csv("${samplesheet}", row.names=1)

    # Ensure column order matches
    counts <- counts[, rownames(coldata)]

    # Run DESeq2
    dds <- DESeqDataSetFromMatrix(
        countData = round(counts),
        colData = coldata,
        design = ~ condition
    )
    dds <- DESeq(dds)
    res <- results(dds, alpha=0.05)

    # Save results
    write.csv(as.data.frame(res), file="${prefix}_deseq2_results.csv")
    write.csv(counts(dds, normalized=TRUE), file="${prefix}_normalized_counts.csv")

    # PCA plot
    vsd <- vst(dds, blind=FALSE)
    png("${prefix}_pca.png", width=800, height=600)
    plotPCA(vsd, intgroup="condition")
    dev.off()

    # Volcano plot
    png("${prefix}_volcano.png", width=800, height=600)
    plot(res\$log2FoldChange, -log10(res\$padj),
         pch=20, cex=0.5,
         col=ifelse(res\$padj < 0.05 & abs(res\$log2FoldChange) > 1, "red", "grey"),
         xlab="Log2 Fold Change", ylab="-Log10 Adjusted P-value",
         main="Volcano Plot")
    abline(h=-log10(0.05), lty=2)
    abline(v=c(-1, 1), lty=2)
    dev.off()

    # Versions
    writeLines(c(
        '\\"${task.process}\\":',
        paste0('    deseq2: ', packageVersion('DESeq2'))
    ), 'versions.yml')
    """

    stub:
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    touch ${prefix}_deseq2_results.csv
    touch ${prefix}_normalized_counts.csv
    touch ${prefix}_pca.png
    touch ${prefix}_volcano.png
    echo '"${task.process}":' > versions.yml
    echo '    deseq2: 1.40.0' >> versions.yml
    """
}
```

```yaml
# === modules/local/deseq2/meta.yml ===

name: deseq2
description: Differential expression analysis using DESeq2
keywords:
  - differential expression
  - RNA-seq
  - DESeq2
tools:
  - deseq2:
      description: |
        Differential gene expression analysis based on the negative
        binomial distribution.
      homepage: https://bioconductor.org/packages/DESeq2
      documentation: https://bioconductor.org/packages/DESeq2
      doi: 10.1186/s13059-014-0550-8
      licence: ["LGPL-3.0"]

input:
  - meta:
      type: map
      description: Groovy Map containing sample information
  - counts:
      type: file
      description: Gene count matrix (genes x samples CSV)
      pattern: "*.csv"
  - samplesheet:
      type: file
      description: Sample metadata with 'condition' column
      pattern: "*.csv"

output:
  - results:
      type: file
      description: DESeq2 results table
      pattern: "*_deseq2_results.csv"
  - normalized:
      type: file
      description: Normalized count matrix
      pattern: "*_normalized_counts.csv"
  - pca:
      type: file
      description: PCA plot of samples
      pattern: "*_pca.png"
  - volcano:
      type: file
      description: Volcano plot of DE results
      pattern: "*_volcano.png"
  - versions:
      type: file
      description: File containing software versions
      pattern: "versions.yml"

authors:
  - "@username"
```

**Key nf-core module conventions**:
- `main.nf`: Process definition with conda, docker, and singularity support.
- `meta.yml`: Machine-readable metadata for documentation and validation.
- `task.ext.args`: Allows config-level parameter injection.
- `versions.yml`: Standardized version tracking across all modules.
- `stub` block: Required for `-stub-run` testing.
- Container auto-selection: Singularity for HPC, Docker otherwise.

**Expected output**: Reusable module that can be included in any Nextflow DSL2 pipeline with `include { DESEQ2 } from './modules/local/deseq2/main'`.

---

## 11. Reference Genome Management

Configure iGenomes references or provide custom genome files.

```bash
#!/bin/bash
# === Reference Genome Management ===

# Option 1: Use iGenomes (built-in references)
# Supported genomes: GRCh38, GRCh37, GRCm39, GRCm38, TAIR10, etc.
nextflow run nf-core/rnaseq \
    --genome GRCh38 \
    --input samplesheet.csv \
    -profile docker

# Custom iGenomes base (if pre-downloaded to shared storage):
nextflow run nf-core/rnaseq \
    --genome GRCh38 \
    --igenomes_base /shared/igenomes \
    --input samplesheet.csv \
    -profile docker

# Option 2: Custom genome with FASTA + GTF
nextflow run nf-core/rnaseq \
    --fasta /data/genomes/custom_genome.fa \
    --gtf /data/genomes/custom_annotation.gtf \
    --gene_bed /data/genomes/genes.bed \
    --star_index /data/genomes/star_index/ \
    --input samplesheet.csv \
    -profile docker

# Option 3: Generate STAR index (omit --star_index to auto-generate)
nextflow run nf-core/rnaseq \
    --fasta /data/genomes/GRCh38.primary_assembly.fa \
    --gtf /data/genomes/gencode.v44.annotation.gtf \
    --save_reference \
    --input samplesheet.csv \
    -profile docker

# Download reference files:
# GENCODE (recommended for RNA-seq):
wget https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/GRCh38.primary_assembly.genome.fa.gz
wget https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.primary_assembly.annotation.gtf.gz

# Ensembl:
wget https://ftp.ensembl.org/pub/release-110/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz
wget https://ftp.ensembl.org/pub/release-110/gtf/homo_sapiens/Homo_sapiens.GRCh38.110.gtf.gz

# Mouse (GRCm39):
wget https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M33/GRCm39.primary_assembly.genome.fa.gz
wget https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M33/gencode.vM33.primary_assembly.annotation.gtf.gz

# Set up custom genome in nextflow.config:
# params {
#     genomes {
#         'custom_human' {
#             fasta  = '/data/genomes/GRCh38.primary_assembly.fa'
#             gtf    = '/data/genomes/gencode.v44.annotation.gtf'
#             star   = '/data/genomes/star_index/'
#             bwa    = '/data/genomes/bwa_index/'
#         }
#     }
# }
# Then: nextflow run pipeline.nf --genome custom_human
```

**Key considerations**:
- `--save_reference`: Save auto-generated indices for reuse (STAR index generation takes ~1h and ~32GB RAM).
- GENCODE vs Ensembl: GENCODE includes more transcript isoforms; Ensembl is simpler. Use GENCODE for RNA-seq.
- `primary_assembly` FASTAs exclude haplotype patches (recommended over `toplevel`).
- Pre-built indices save significant compute time across multiple pipeline runs.

**Expected output**: Pipeline runs with either iGenomes built-in references or custom FASTA/GTF files. Auto-generated indices are saved with `--save_reference` for reuse.

---

## 12. Pipeline Output Parsing: MultiQC Report Interpretation

Extract key metrics from nf-core pipeline outputs programmatically.

```python
import json
import pandas as pd
from pathlib import Path

def parse_multiqc_data(multiqc_dir: str) -> dict:
    """Parse MultiQC output data for programmatic quality assessment.

    Parameters
    ----------
    multiqc_dir : str
        Path to MultiQC output directory (contains multiqc_data/).

    Returns
    -------
    dict with parsed metrics per sample.
    """
    data_dir = Path(multiqc_dir) / "multiqc_data"

    results = {}

    # General stats (most useful summary)
    general_stats = data_dir / "multiqc_general_stats.txt"
    if general_stats.exists():
        df = pd.read_csv(general_stats, sep="\t")
        results["general_stats"] = df
        print(f"General stats: {len(df)} samples x {len(df.columns)} metrics")

    # FastQC results
    fastqc_file = data_dir / "multiqc_fastqc.txt"
    if fastqc_file.exists():
        fastqc = pd.read_csv(fastqc_file, sep="\t")
        results["fastqc"] = fastqc
        print(f"FastQC: {len(fastqc)} files")

    # STAR alignment stats
    star_file = data_dir / "multiqc_star.txt"
    if star_file.exists():
        star = pd.read_csv(star_file, sep="\t")
        results["star"] = star
        print(f"STAR alignment: {len(star)} samples")

    # Salmon quantification
    salmon_file = data_dir / "multiqc_salmon.txt"
    if salmon_file.exists():
        salmon = pd.read_csv(salmon_file, sep="\t")
        results["salmon"] = salmon

    # Picard duplication metrics
    picard_file = data_dir / "multiqc_picard_dups.txt"
    if picard_file.exists():
        picard = pd.read_csv(picard_file, sep="\t")
        results["picard"] = picard

    return results

def quality_check(results: dict, min_reads: int = 10_000_000,
                  min_alignment_rate: float = 70.0,
                  max_duplication_rate: float = 60.0) -> pd.DataFrame:
    """Flag samples failing quality thresholds.

    Parameters
    ----------
    results : dict
        Output from parse_multiqc_data().
    min_reads : int
        Minimum total reads per sample.
    min_alignment_rate : float
        Minimum alignment rate (%).
    max_duplication_rate : float
        Maximum duplication rate (%).

    Returns
    -------
    pd.DataFrame with pass/fail flags per sample.
    """
    flags = []

    if "general_stats" in results:
        gs = results["general_stats"]

        for _, row in gs.iterrows():
            sample = row.get("Sample", "unknown")
            issues = []

            # Check total reads
            reads_col = [c for c in gs.columns if "total_reads" in c.lower() or "total_sequences" in c.lower()]
            if reads_col:
                total_reads = row[reads_col[0]]
                if total_reads < min_reads:
                    issues.append(f"LOW_READS ({total_reads:,.0f})")

            # Check alignment rate
            align_col = [c for c in gs.columns if "uniquely_mapped" in c.lower() or "aligned" in c.lower()]
            if align_col:
                align_rate = row[align_col[0]]
                if align_rate < min_alignment_rate:
                    issues.append(f"LOW_ALIGNMENT ({align_rate:.1f}%)")

            # Check duplication
            dup_col = [c for c in gs.columns if "duplication" in c.lower() or "percent_duplication" in c.lower()]
            if dup_col:
                dup_rate = row[dup_col[0]]
                if dup_rate > max_duplication_rate:
                    issues.append(f"HIGH_DUPLICATION ({dup_rate:.1f}%)")

            flags.append({
                "sample": sample,
                "pass": len(issues) == 0,
                "issues": "; ".join(issues) if issues else "OK",
            })

    flag_df = pd.DataFrame(flags)
    n_pass = flag_df["pass"].sum()
    n_fail = (~flag_df["pass"]).sum()
    print(f"\nQuality check: {n_pass} passed, {n_fail} flagged")

    if n_fail > 0:
        print("\nFlagged samples:")
        for _, row in flag_df[~flag_df["pass"]].iterrows():
            print(f"  {row['sample']}: {row['issues']}")

    return flag_df

# Usage
results = parse_multiqc_data("results/rnaseq/multiqc/")
flags = quality_check(results, min_reads=10_000_000, min_alignment_rate=70)
```

**Expected output**: Parsed metrics from MultiQC output files as DataFrames. Quality check flags samples with low read counts, poor alignment rates, or high duplication. Use to automate QC decisions before downstream analysis.
