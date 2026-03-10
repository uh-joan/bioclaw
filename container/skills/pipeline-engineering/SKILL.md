---
name: pipeline-engineering
description: Bioinformatics workflow engines for reproducible pipelines. Nextflow, Snakemake, CWL, WDL, nf-core, container integration, resource management, cluster execution. Use when user mentions workflow, pipeline, Nextflow, Snakemake, CWL, WDL, Cromwell, nf-core, reproducible pipeline, workflow engine, pipeline management, DAG, process definition, or bioinformatics workflow.
---

# Workflow Management

> **Code recipes**: See [nextflow-recipes.md](nextflow-recipes.md) for nf-core pipeline templates (rnaseq, sarek, atacseq), GEO/SRA data acquisition, samplesheet generation, custom process definitions, config profiles, resource management, and MultiQC output parsing.

Production-ready bioinformatics workflow engine methodology. The agent writes and executes code for building, configuring, and deploying reproducible pipelines using Nextflow, Snakemake, CWL, and WDL. Covers process definitions, container integration, resource management, error handling, cluster/cloud execution profiles, testing, and best practices for modular pipeline design.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_workflow-management_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Running a specific analysis (RNA-seq, variant calling, etc.) -> use the relevant analysis skill
- Data visualization only -> use `visualization` or the analysis skill
- Statistical methods selection -> use `biostatistics`
- Container/Docker image building -> use DevOps tools
- Job scheduler configuration (SLURM/PBS alone) -> use system admin tools

## Cross-Reference: Other Skills

- **Specific analysis methodology** -> use the relevant analysis skill (rnaseq-analysis, variant-calling, etc.)
- **Container best practices** -> refer to Docker/Singularity documentation
- **Cloud deployment** -> refer to platform-specific guides (AWS, GCP)

## Environment

Nextflow (Java-based), Snakemake (Python), cwltool (Python), Cromwell (Java/WDL). Install at runtime as needed.

---

## Nextflow

### Process Definitions and DSL2

```groovy
// === Nextflow DSL2 Pipeline Structure ===

// Enable DSL2 (required for modules)
nextflow.enable.dsl = 2

// Parameters with defaults
params.reads = "${baseDir}/data/*_{1,2}.fastq.gz"
params.genome = "${baseDir}/ref/genome.fa"
params.outdir = "results"

// Process definition
process FASTQC {
    // Resource allocation
    cpus 4
    memory '8 GB'
    time '2h'

    // Container
    container 'biocontainers/fastqc:v0.11.9'

    // Publishing results
    publishDir "${params.outdir}/fastqc", mode: 'copy'

    // Error handling
    errorStrategy { task.exitStatus in [137, 140] ? 'retry' : 'finish' }
    maxRetries 3
    maxErrors '-1'

    input:
    tuple val(sample_id), path(reads)

    output:
    path("*.html"), emit: html
    path("*.zip"), emit: zip

    script:
    """
    fastqc -t ${task.cpus} ${reads}
    """
}

process TRIM_GALORE {
    cpus 4
    memory '8 GB'

    container 'quay.io/biocontainers/trim-galore:0.6.7'

    input:
    tuple val(sample_id), path(reads)

    output:
    tuple val(sample_id), path("*_val_{1,2}.fq.gz"), emit: trimmed_reads
    path("*_trimming_report.txt"), emit: reports

    script:
    """
    trim_galore --paired --cores ${task.cpus} ${reads[0]} ${reads[1]}
    """
}

process STAR_ALIGN {
    cpus 8
    memory '32 GB'

    container 'quay.io/biocontainers/star:2.7.10a'

    input:
    tuple val(sample_id), path(reads)
    path(genome_index)

    output:
    tuple val(sample_id), path("*.bam"), emit: bam
    path("*Log.final.out"), emit: log

    script:
    """
    STAR --runThreadN ${task.cpus} \\
         --genomeDir ${genome_index} \\
         --readFilesIn ${reads[0]} ${reads[1]} \\
         --readFilesCommand zcat \\
         --outSAMtype BAM SortedByCoordinate \\
         --outFileNamePrefix ${sample_id}_
    """
}

// Workflow definition (connects processes via channels)
workflow {
    // Create channel from file pairs
    read_pairs_ch = Channel.fromFilePairs(params.reads, checkIfExists: true)

    // Run processes
    FASTQC(read_pairs_ch)
    TRIM_GALORE(read_pairs_ch)
    STAR_ALIGN(TRIM_GALORE.out.trimmed_reads, params.genome)
}
```

### Channels and Operators

```groovy
// === Nextflow Channels ===

// Queue channels (consumed once)
Channel.fromPath("data/*.fastq.gz")                    // Files by glob
Channel.fromFilePairs("data/*_{1,2}.fastq.gz")         // Paired files
Channel.fromSRA("SRP043510")                           // From SRA
Channel.of(1, 2, 3, 4, 5)                              // Values

// Value channels (reusable, broadcast)
Channel.value(file("reference.fa"))

// Key operators
reads_ch
    .map { sample_id, reads -> tuple(sample_id, reads, "paired") }  // Transform
    .filter { sample_id, reads -> reads.size() > 0 }                // Filter
    .groupTuple()                                                     // Group by key
    .join(other_ch)                                                   // Join channels
    .combine(reference_ch)                                            // Cartesian product
    .collect()                                                        // Collect all items
    .flatten()                                                        // Flatten nested
    .mix(other_ch)                                                    // Merge channels
    .branch { item ->                                                 // Conditional split
        large: item.size() > 1e9
        small: true
    }

// Common patterns:
// 1. Add metadata from a samplesheet
Channel.fromPath(params.samplesheet)
    .splitCsv(header: true)
    .map { row -> tuple(row.sample_id, file(row.fastq_1), file(row.fastq_2)) }

// 2. Collect outputs for multiqc
FASTQC.out.zip.collect()  // Wait for all, pass as list
```

### Profiles and Configuration

```groovy
// === nextflow.config ===

// Default parameters
params {
    reads = "data/*_{1,2}.fastq.gz"
    genome = null
    outdir = "results"
    max_cpus = 16
    max_memory = '64.GB'
    max_time = '48.h'
}

// Profiles
profiles {
    local {
        process.executor = 'local'
        docker.enabled = true
    }

    slurm {
        process.executor = 'slurm'
        process.queue = 'normal'
        singularity.enabled = true
        singularity.autoMounts = true
    }

    pbs {
        process.executor = 'pbs'
        process.queue = 'batch'
        singularity.enabled = true
    }

    aws_batch {
        process.executor = 'awsbatch'
        process.queue = 'nextflow-queue'
        aws.region = 'us-east-1'
        aws.batch.cliPath = '/home/ec2-user/miniconda/bin/aws'
        workDir = 's3://my-bucket/work'
    }

    google_lifesciences {
        process.executor = 'google-lifesciences'
        google.project = 'my-project'
        google.zone = 'us-central1-a'
        workDir = 'gs://my-bucket/work'
    }

    test {
        params.reads = "${baseDir}/test_data/*_{1,2}.fastq.gz"
        params.genome = "${baseDir}/test_data/genome.fa"
        process.cpus = 1
        process.memory = '2.GB'
    }
}

// Process-specific resources
process {
    withName: 'STAR_ALIGN' {
        cpus = 8
        memory = '32.GB'
    }
    withName: 'FASTQC' {
        cpus = 2
        memory = '4.GB'
    }
    withLabel: 'high_memory' {
        memory = '64.GB'
    }
}

// Resource limits (cap all processes)
process {
    cpus = { check_max(task.cpus, params.max_cpus) }
    memory = { check_max(task.memory, params.max_memory) }
    time = { check_max(task.time, params.max_time) }
}
```

### Nextflow Testing and Debugging

```groovy
// === Testing ===

// Stub run (dry run with placeholder outputs)
// nextflow run main.nf -stub-run -profile test
process EXAMPLE {
    input: path(x)
    output: path("result.txt")

    stub:
    """
    touch result.txt
    """

    script:
    """
    real_analysis ${x} > result.txt
    """
}

// Resume from cache
// nextflow run main.nf -resume

// Execution reports
// nextflow run main.nf -with-report report.html -with-trace trace.txt -with-timeline timeline.html -with-dag dag.png
```

---

## Snakemake

### Rules and Wildcards

```python
# === Snakefile ===

# Configuration
configfile: "config.yaml"
SAMPLES = config["samples"]

# Target rule (defines final outputs)
rule all:
    input:
        expand("results/aligned/{sample}.bam", sample=SAMPLES),
        "results/multiqc/multiqc_report.html"

# Rule definition
rule fastqc:
    input:
        r1 = "data/{sample}_1.fastq.gz",
        r2 = "data/{sample}_2.fastq.gz"
    output:
        html = "results/fastqc/{sample}_1_fastqc.html",
        zip = "results/fastqc/{sample}_1_fastqc.zip"
    threads: 4
    resources:
        mem_mb = 8000,
        time_min = 120
    conda:
        "envs/fastqc.yaml"
    container:
        "docker://biocontainers/fastqc:v0.11.9"
    log:
        "logs/fastqc/{sample}.log"
    benchmark:
        "benchmarks/fastqc/{sample}.tsv"
    shell:
        "fastqc -t {threads} {input.r1} {input.r2} -o results/fastqc/ 2> {log}"

rule trim_galore:
    input:
        r1 = "data/{sample}_1.fastq.gz",
        r2 = "data/{sample}_2.fastq.gz"
    output:
        r1 = "results/trimmed/{sample}_1_val_1.fq.gz",
        r2 = "results/trimmed/{sample}_2_val_2.fq.gz",
        report = "results/trimmed/{sample}_trimming_report.txt"
    threads: 4
    conda:
        "envs/trim_galore.yaml"
    shell:
        """
        trim_galore --paired --cores {threads} \
            -o results/trimmed/ \
            {input.r1} {input.r2} 2> {log}
        """

rule star_align:
    input:
        r1 = rules.trim_galore.output.r1,
        r2 = rules.trim_galore.output.r2,
        index = config["star_index"]
    output:
        bam = "results/aligned/{sample}.bam"
    threads: 8
    resources:
        mem_mb = 32000
    conda:
        "envs/star.yaml"
    shell:
        """
        STAR --runThreadN {threads} \
             --genomeDir {input.index} \
             --readFilesIn {input.r1} {input.r2} \
             --readFilesCommand zcat \
             --outSAMtype BAM SortedByCoordinate \
             --outFileNamePrefix results/aligned/{wildcards.sample}_
        mv results/aligned/{wildcards.sample}_Aligned.sortedByCoord.out.bam {output.bam}
        """

rule multiqc:
    input:
        expand("results/fastqc/{sample}_1_fastqc.zip", sample=SAMPLES),
        expand("results/aligned/{sample}.bam", sample=SAMPLES)
    output:
        "results/multiqc/multiqc_report.html"
    conda:
        "envs/multiqc.yaml"
    shell:
        "multiqc results/ -o results/multiqc/"
```

### Snakemake Cluster Execution

```python
# === Cluster profiles ===

# profiles/slurm/config.yaml
# executor: slurm
# default-resources:
#   slurm_partition: normal
#   mem_mb: 4000
#   runtime: 60
# set-resources:
#   star_align:
#     mem_mb: 32000
#     runtime: 480
#     slurm_partition: highmem

# Command:
# snakemake --profile profiles/slurm -j 100

# Dry run (always do first):
# snakemake -n --printshellcmds

# DAG visualization:
# snakemake --dag | dot -Tpng > dag.png

# Rerun from specific rule:
# snakemake --forcerun rule_name
```

### Snakemake Conda Integration

```yaml
# === envs/star.yaml ===
name: star
channels:
  - bioconda
  - conda-forge
dependencies:
  - star=2.7.10a
  - samtools=1.16.1
```

---

## CWL (Common Workflow Language)

### CommandLineTool

```yaml
# === fastqc.cwl ===
cwlVersion: v1.2
class: CommandLineTool
label: "FastQC quality control"

requirements:
  DockerRequirement:
    dockerPull: biocontainers/fastqc:v0.11.9
  ResourceRequirement:
    coresMin: 4
    ramMin: 8000

baseCommand: fastqc

arguments:
  - prefix: -t
    valueFrom: $(runtime.cores)
  - prefix: -o
    valueFrom: $(runtime.outdir)

inputs:
  reads:
    type: File[]
    inputBinding:
      position: 1

outputs:
  html_report:
    type: File[]
    outputBinding:
      glob: "*.html"
  zip_report:
    type: File[]
    outputBinding:
      glob: "*.zip"
```

### CWL Workflow

```yaml
# === workflow.cwl ===
cwlVersion: v1.2
class: Workflow
label: "RNA-seq analysis workflow"

requirements:
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}

inputs:
  read_pairs:
    type:
      type: array
      items:
        type: record
        fields:
          - name: sample_id
            type: string
          - name: reads
            type: File[]
  genome_index:
    type: Directory

steps:
  fastqc:
    run: fastqc.cwl
    scatter: reads
    in:
      reads:
        source: read_pairs
        valueFrom: $(self.reads)
    out: [html_report, zip_report]

  star_align:
    run: star.cwl
    scatter: [sample_id, reads]
    scatterMethod: dotproduct
    in:
      sample_id:
        source: read_pairs
        valueFrom: $(self.sample_id)
      reads:
        source: read_pairs
        valueFrom: $(self.reads)
      genome_index: genome_index
    out: [aligned_bam]

outputs:
  qc_reports:
    type: File[]
    outputSource: fastqc/html_report
  alignments:
    type: File[]
    outputSource: star_align/aligned_bam

# Run: cwltool workflow.cwl inputs.yaml
```

---

## WDL (Workflow Description Language)

### Task and Workflow

```wdl
# === rna_seq.wdl ===
version 1.0

task fastqc {
    input {
        Array[File] reads
        Int threads = 4
        String docker_image = "biocontainers/fastqc:v0.11.9"
    }

    command <<<
        fastqc -t ~{threads} ~{sep=' ' reads}
    >>>

    output {
        Array[File] html_reports = glob("*.html")
        Array[File] zip_reports = glob("*.zip")
    }

    runtime {
        docker: docker_image
        cpu: threads
        memory: "8 GB"
        disks: "local-disk 50 HDD"
    }
}

task star_align {
    input {
        String sample_id
        File read1
        File read2
        File genome_index_tar
        Int threads = 8
    }

    command <<<
        tar xf ~{genome_index_tar}
        STAR --runThreadN ~{threads} \
             --genomeDir genome_index/ \
             --readFilesIn ~{read1} ~{read2} \
             --readFilesCommand zcat \
             --outSAMtype BAM SortedByCoordinate \
             --outFileNamePrefix ~{sample_id}_
    >>>

    output {
        File aligned_bam = "~{sample_id}_Aligned.sortedByCoord.out.bam"
        File align_log = "~{sample_id}_Log.final.out"
    }

    runtime {
        docker: "quay.io/biocontainers/star:2.7.10a"
        cpu: threads
        memory: "32 GB"
        disks: "local-disk 100 SSD"
    }
}

workflow rna_seq_pipeline {
    input {
        Array[Pair[String, Pair[File, File]]] samples
        File genome_index_tar
    }

    scatter (sample in samples) {
        call fastqc {
            input:
                reads = [sample.right.left, sample.right.right]
        }

        call star_align {
            input:
                sample_id = sample.left,
                read1 = sample.right.left,
                read2 = sample.right.right,
                genome_index_tar = genome_index_tar
        }
    }

    output {
        Array[File] all_bams = star_align.aligned_bam
        Array[Array[File]] all_qc = fastqc.html_reports
    }
}

# Run with Cromwell:
# java -jar cromwell.jar run rna_seq.wdl -i inputs.json
```

---

## Error Handling and Resource Management

```
Error Handling Strategies:
=========================

Nextflow:
  errorStrategy 'terminate'   # Stop pipeline on any failure (default)
  errorStrategy 'finish'      # Complete running tasks, then stop
  errorStrategy 'ignore'      # Skip failed tasks, continue
  errorStrategy 'retry'       # Retry failed tasks
  maxRetries 3                 # Maximum retry attempts

  # Dynamic error strategy (retry OOM, fail on other errors):
  errorStrategy { task.exitStatus in [137, 140] ? 'retry' : 'finish' }

  # Dynamic resources on retry:
  memory { 8.GB * task.attempt }   # Double memory on each retry
  cpus { 4 * task.attempt }

Snakemake:
  # In Snakefile rule:
  resources:
      mem_mb = lambda wildcards, attempt: 8000 * attempt
  retries: 3

  # Command line:
  snakemake --restart-times 3
  snakemake --keep-going  # Continue with independent jobs on failure

CWL:
  # No built-in retry (handled by runner)
  # cwltool: No retry support
  # Toil-cwl-runner: --retryCount 3

WDL:
  # In runtime block:
  maxRetries: 3
  preemptible: 3  # Use preemptible VMs, retry on preemption
```

### Resource Management Guide

```
Resource Allocation Guide:
==========================

Process Type           | CPUs | Memory  | Time    | Disk
-----------------------|------|---------|---------|--------
FastQC                 | 2-4  | 4 GB    | 1h      | 10 GB
Trimming               | 4    | 8 GB    | 2h      | 20 GB
BWA/STAR alignment     | 8-16 | 32 GB   | 4-8h    | 100 GB
STAR genome generate   | 8    | 64 GB   | 2h      | 50 GB
GATK HaplotypeCaller   | 4    | 16 GB   | 4-12h   | 50 GB
DeepVariant            | 8    | 32 GB   | 4-8h    | 50 GB
samtools sort/index    | 4    | 8 GB    | 1-2h    | 50 GB
featureCounts          | 4    | 8 GB    | 30min   | 10 GB
DESeq2/edgeR           | 1    | 8 GB    | 30min   | 5 GB
MultiQC                | 1    | 4 GB    | 15min   | 5 GB
MACS2 peak calling     | 2    | 8 GB    | 1-2h    | 20 GB

Tips:
  - Always set memory limits (OOM kills are silent failures)
  - Use dynamic resources: increase on retry for OOM errors
  - Local SSDs for I/O-intensive tasks (sorting, indexing)
  - Profile first, optimize later (use trace/benchmark features)
```

---

## nf-core Pipelines

```bash
# === nf-core: Community-curated Nextflow pipelines ===

# List available pipelines
nf-core list

# Key pipelines:
#   nf-core/rnaseq          - RNA-seq analysis
#   nf-core/sarek           - Variant calling (germline + somatic)
#   nf-core/atacseq         - ATAC-seq analysis
#   nf-core/chipseq         - ChIP-seq analysis
#   nf-core/methylseq       - Bisulfite sequencing
#   nf-core/ampliseq        - Amplicon sequencing (16S/ITS)
#   nf-core/scrnaseq        - Single-cell RNA-seq
#   nf-core/viralrecon      - Viral genome analysis
#   nf-core/mag             - Metagenome assembly
#   nf-core/fetchngs        - Download from SRA/ENA

# Run a pipeline
nextflow run nf-core/rnaseq \
    -r 3.12.0 \
    -profile docker \
    --input samplesheet.csv \
    --genome GRCh38 \
    --outdir results/

# Download pipeline for offline use
nf-core download rnaseq -r 3.12.0 --compress tar.gz

# Launch interactive parameter selection
nf-core launch rnaseq

# Samplesheet format (CSV):
# sample,fastq_1,fastq_2,strandedness
# sample1,/path/to/s1_R1.fastq.gz,/path/to/s1_R2.fastq.gz,auto
# sample2,/path/to/s2_R1.fastq.gz,/path/to/s2_R2.fastq.gz,auto

# Institutional configs (automatic resource profiles):
# nextflow run nf-core/rnaseq -profile institutional_config_name
```

```
nf-core Pipeline Selection Guide:
==================================

Analysis Type              | nf-core Pipeline  | Key Parameters
---------------------------|-------------------|---------------------------
Bulk RNA-seq               | nf-core/rnaseq    | --aligner star_salmon
Variant calling (germline) | nf-core/sarek     | --tools haplotypecaller
Variant calling (somatic)  | nf-core/sarek     | --tools mutect2
ATAC-seq                   | nf-core/atacseq   | --narrow_peak
ChIP-seq                   | nf-core/chipseq   | --narrow_peak / --broad
Whole-genome bisulfite     | nf-core/methylseq | --aligner bismark
16S amplicon               | nf-core/ampliseq  | --FW_primer / --RV_primer
Single-cell RNA-seq        | nf-core/scrnaseq  | --aligner cellranger
Metagenome assembly        | nf-core/mag       | --assembler megahit
```

---

## Testing and Provenance

```
Testing Strategies:
===================

Nextflow:
  # Stub run (fast dry run with mock outputs)
  nextflow run main.nf -stub-run -profile test

  # Test profile (small test data)
  nextflow run main.nf -profile test

  # nf-test (unit testing framework)
  nf-test test tests/

  # Resume (skip completed processes)
  nextflow run main.nf -resume

Snakemake:
  # Dry run (show planned execution)
  snakemake -n --printshellcmds

  # Reason for execution
  snakemake -n --reason

  # Generate DAG
  snakemake --dag | dot -Tpng > dag.png

  # Lint rules
  snakemake --lint

CWL:
  # Validate CWL document
  cwltool --validate workflow.cwl

  # Dry run
  cwltool --no-container workflow.cwl inputs.yaml

WDL:
  # Validate WDL
  womtool validate workflow.wdl

  # Generate inputs template
  womtool inputs workflow.wdl > inputs.json

  # Dry run with Cromwell
  java -jar cromwell.jar run workflow.wdl --options dry_run.json

Provenance and Reporting:
=========================

Nextflow:
  -with-report report.html      # Execution report (resources, duration)
  -with-trace trace.txt         # Per-process resource usage
  -with-timeline timeline.html  # Gantt chart of execution
  -with-dag dag.png             # Pipeline DAG visualization
  -with-tower                   # Nextflow Tower monitoring

Snakemake:
  --report report.html          # HTML report with stats and DAG
  --benchmark                   # Per-rule benchmarks
  --stats stats.json            # Runtime statistics

CWL:
  cwltool --provenance prov/    # W3C PROV provenance recording
```

---

## Best Practices

```
Pipeline Design Best Practices:
================================

1. VERSION PINNING:
   - Pin all tool versions (container tags, conda versions)
   - Pin workflow engine version
   - Use release tags, not 'latest' or 'main'
   BAD:  container 'biocontainers/samtools'
   GOOD: container 'biocontainers/samtools:1.16.1'

2. CONFIG SEPARATION:
   - Parameters in params file (not hardcoded)
   - Resources in config (not in process)
   - Environment in profiles (not assumed)
   Structure:
     main.nf / Snakefile    -> Pipeline logic
     nextflow.config         -> Resources, profiles
     params.yaml             -> Analysis parameters
     samplesheet.csv         -> Input data

3. MODULAR DESIGN:
   Nextflow: DSL2 modules (one process per file)
     modules/fastqc/main.nf
     modules/star/main.nf
     workflows/rnaseq.nf     -> Imports and connects modules
   Snakemake: Include rules from separate files
     rules/qc.smk
     rules/alignment.smk
     Snakefile               -> Includes + target rule

4. CONTAINER STRATEGY:
   - One container per process/rule (not one monolithic container)
   - Use BioContainers when available
   - Singularity for HPC (no root required)
   - Test containers locally before deploying to cluster

5. ERROR HANDLING:
   - Always set memory limits
   - Use dynamic resources on retry
   - Log stderr to files (for debugging)
   - Use 'finish' strategy (complete running tasks before stopping)

6. REPRODUCIBILITY:
   - Lock file for dependencies (conda lock, requirements.txt)
   - Commit workflow + config to version control
   - Record execution parameters in output
   - Use checksums for input validation

7. TESTING:
   - Include small test dataset in repository
   - Test profile for CI/CD
   - Stub/dry run before full execution
   - Validate outputs (check file sizes, expected content)
```

---

## Workflow Engine Comparison

| Feature | Nextflow | Snakemake | CWL | WDL |
|---------|----------|-----------|-----|-----|
| **Language** | Groovy/DSL | Python | YAML | Custom DSL |
| **Paradigm** | Dataflow | Rule-based (Make) | Declarative | Declarative |
| **Learning curve** | Moderate | Easy (Python) | Steep | Moderate |
| **Modularity** | DSL2 modules | Include rules | Tools + Workflows | Tasks + Workflows |
| **Containers** | Docker, Singularity, Podman | Docker, Singularity, Conda | Docker, Singularity | Docker |
| **Cloud** | AWS, GCP, Azure | GCP, AWS (plugins) | Various runners | Cromwell (GCP, AWS) |
| **HPC** | SLURM, PBS, SGE, LSF | SLURM, PBS, SGE, LSF | Toil | Cromwell |
| **Community** | nf-core (80+ pipelines) | Snakemake catalog | CWL registry | Terra/WDL registry |
| **Resume** | Built-in (-resume) | Built-in (timestamps) | Runner-dependent | Cromwell call caching |
| **Testing** | nf-test, stub-run | --dryrun, --lint | --validate | womtool validate |
| **Provenance** | Report, trace, timeline | Report, benchmarks | W3C PROV | Cromwell metadata |

### Decision Tree

```
Which workflow engine should I use?
===================================

+-- Do you use Python regularly?
|   +-- YES, and my pipeline is straightforward:
|   |   -> Snakemake (easiest for Python users)
|   +-- YES, but I need cloud scalability:
|       -> Nextflow (better cloud support) or Snakemake (improving cloud)
+-- Do you need nf-core community pipelines?
|   +-- YES: Nextflow (nf-core is Nextflow-only)
+-- Do you need strict portability/standards?
|   +-- YES: CWL (most portable, W3C-inspired)
+-- Are you working on Terra/Broad Institute platforms?
|   +-- YES: WDL + Cromwell (native integration)
+-- Are you building from scratch for a lab?
|   +-- Small lab: Snakemake (lowest barrier to entry)
|   +-- Large lab / production: Nextflow (best scaling + nf-core)
+-- Default recommendation:
    -> Nextflow (best balance of features, community, scalability)
```

---

## Evidence Grading

| Tier | Evidence Type | Example |
|------|-------------|---------|
| **T1** | Published nf-core / community pipeline | nf-core/rnaseq, nf-core/sarek |
| **T2** | Published pipeline with benchmarks | Pipeline in Nature Methods/Bioinformatics |
| **T3** | In-house pipeline, tested + documented | Lab pipeline with test data + CI/CD |
| **T4** | Ad hoc script collection | Bash scripts without formal workflow |

---

## Multi-Agent Workflow Examples

**"Build a reproducible RNA-seq pipeline with Nextflow"**
1. Workflow Management -> Nextflow DSL2 pipeline: FastQC, trimming, STAR, featureCounts
2. RNA-seq Analysis -> Validate analysis steps and parameter choices
3. Gene Enrichment -> Add pathway analysis as final step

**"Set up nf-core/sarek for variant calling on our HPC cluster"**
1. Workflow Management -> Configure SLURM profile, Singularity containers, institutional config
2. Variant Calling -> Verify tool selections (GATK vs DeepVariant)
3. Cancer Variant Interpreter -> Add annotation step post-calling

**"Convert our Snakemake pipeline to run on AWS"**
1. Workflow Management -> Add AWS profile, S3 staging, Batch executor
2. DevOps -> IAM roles, cost estimation, spot instance configuration

## Completeness Checklist

- [ ] Workflow engine selected with justification
- [ ] All processes/rules/tasks defined with proper inputs/outputs
- [ ] Container images specified for each process (version-pinned)
- [ ] Resource allocation set (CPU, memory, time, disk)
- [ ] Error handling configured (retry strategy, dynamic resources)
- [ ] Execution profiles defined (local, HPC, cloud)
- [ ] Test dataset and test profile included
- [ ] Dry run / stub run successful
- [ ] Provenance tracking enabled (reports, traces)
- [ ] Configuration separated from pipeline logic
- [ ] Pipeline version-controlled with documentation
- [ ] Evidence tier assigned to pipeline validation level (T1-T4)
- [ ] Report file created with all sections populated (no `[Analyzing...]` remaining)
