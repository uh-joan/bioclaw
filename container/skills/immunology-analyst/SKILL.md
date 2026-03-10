---
name: immunology-analyst
description: Computational immunology analyst. Epitope prediction, MHC binding analysis, neoantigen identification, HLA typing, and vaccine design. Use when user mentions epitope prediction, MHC binding, MHC-I, MHC-II, HLA typing, neoantigen, neoepitope, T-cell epitope, B-cell epitope, immunogenicity, MHCflurry, NetMHCpan, peptide binding, IC50, affinity prediction, tumor mutational burden, TMB, vaccine design, immunopeptidome, antigen presentation, TAP transport, HLA alleles, OptiType, HLA-HD, agretopicity, self-similarity, population coverage, IEDB, immune response prediction, or checkpoint immunotherapy biomarkers.
---

# Immunoinformatics

Computational immunology pipeline covering epitope prediction, MHC binding analysis, neoantigen identification from tumor sequencing data, HLA typing, and rational vaccine design. Integrates variant calling outputs with immune prediction tools to prioritize therapeutic targets.

## Report-First Workflow

1. **Create report file immediately**: `[sample]_immunoinformatics_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as analysis proceeds
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill
- Variant calling from WGS/WES -> use appropriate variant calling skill first, then this skill
- RNA-seq differential expression -> use RNA-seq skill
- Single-cell immune profiling (scRNA-seq) -> use single-cell-analysis skill
- TCR/BCR repertoire sequencing -> specialized repertoire analysis
- Structural modeling of MHC-peptide complexes -> use molecular dynamics/docking skill

## Cross-Reference: Other Skills
- **Variant calling input** -> use variant calling skill to generate VCF first
- **Expression filtering** -> use RNA-seq skill for expression quantification
- **Splicing-derived neoantigens** -> use alternative-splicing skill
- **Methylation-driven neoantigen loss** -> use methylation-analysis skill

---

## Fundamentals: Antigen Presentation Pathway

### MHC Class I Pathway

```
Protein → Proteasomal cleavage → TAP transport into ER
→ Peptide loading onto MHC-I → Cell surface presentation
→ CD8+ T-cell recognition (cytotoxic response)

Peptide length: 8-11 amino acids (9-mer most common)
```

### MHC Class II Pathway

```
Extracellular protein → Endosomal degradation
→ Peptide loading onto MHC-II in endosome
→ Cell surface presentation
→ CD4+ T-cell recognition (helper response)

Peptide length: 13-25 amino acids (15-mer most common)
Core binding region: 9 amino acids within the longer peptide
```

### HLA Gene System

| Locus | Class | Chains | Expression | Role |
|-------|-------|--------|------------|------|
| **HLA-A** | I | Heavy chain + beta2m | All nucleated cells | CD8+ T-cell epitopes |
| **HLA-B** | I | Heavy chain + beta2m | All nucleated cells | CD8+ T-cell epitopes |
| **HLA-C** | I | Heavy chain + beta2m | All nucleated cells | CD8+ T-cell epitopes, NK cell regulation |
| **HLA-DRB1** | II | Alpha + beta | APCs (DCs, macrophages, B cells) | CD4+ T-cell epitopes |
| **HLA-DQB1** | II | Alpha + beta | APCs | CD4+ T-cell epitopes |
| **HLA-DPB1** | II | Alpha + beta | APCs | CD4+ T-cell epitopes |

Each person carries up to 6 class I alleles (2 each: A, B, C) and up to 12 class II alleles.

---

## Phase 1: HLA Typing from NGS Data

### OptiType (MHC Class I)

```bash
# OptiType: HLA-A, -B, -C typing from WGS/WES/RNA-seq
# Step 1: Extract HLA reads
razers3 -i 95 -m 1 -dr 0 -tc 8 \
  -o hla_reads_R1.bam \
  hla_reference.fasta \
  sample_R1.fastq.gz

razers3 -i 95 -m 1 -dr 0 -tc 8 \
  -o hla_reads_R2.bam \
  hla_reference.fasta \
  sample_R2.fastq.gz

# Convert to FASTQ
samtools fastq hla_reads_R1.bam > hla_R1.fastq
samtools fastq hla_reads_R2.bam > hla_R2.fastq

# Step 2: Run OptiType
OptiTypePipeline.py \
  -i hla_R1.fastq hla_R2.fastq \
  --dna \
  --outdir optitype_results/ \
  --prefix sample

# Output: sample_result.tsv
# A1          A2          B1          B2          C1          C2        Reads  Objective
# A*02:01     A*24:02     B*07:02     B*40:01     C*03:04     C*07:02  1234   56789.0
```

### HLA-HD (Class I + Class II)

```bash
# HLA-HD: comprehensive typing including class II
hlahd.sh \
  -t 8 \
  -m 50 \
  -f freq_data/ \
  sample_R1.fastq.gz \
  sample_R2.fastq.gz \
  gene_split_filt/ \
  dictionary/ \
  hlahd_results/ \
  sample

# Output covers: HLA-A, -B, -C, -DRB1, -DQB1, -DPB1 (and others)
```

### HLA Typing Method Comparison

| Tool | Class I | Class II | Input | Speed | Accuracy |
|------|---------|----------|-------|-------|----------|
| **OptiType** | Yes | No | WGS/WES/RNA-seq | Fast | >99% (class I gold standard) |
| **HLA-HD** | Yes | Yes | WGS/WES | Moderate | >95% |
| **POLYSOLVER** | Yes | No | WES (tumor+normal) | Slow | High (cancer-focused) |
| **arcasHLA** | Yes | Yes | RNA-seq | Fast | Good for RNA-seq |
| **xHLA** | Yes | Yes | WGS/WES | Fast | Good |

### HLA Typing QC

```
Confidence checks:
- [ ] Read count supporting top allele >50 reads
- [ ] Clear separation between top 2 candidates (objective function gap)
- [ ] Concordance between DNA and RNA typing (if both available)
- [ ] Verify against known population frequencies for ethnicity
- [ ] Homozygosity confirmed if only one allele called (check coverage)

Red flags:
- Very low read count (<20) → insufficient coverage at HLA locus
- Multiple close candidates → ambiguous typing, may need higher resolution
- Class I/II discordance between tools → use orthogonal validation
```

---

## Phase 2: MHC-I Binding Prediction

### MHCflurry 2.0

```python
from mhcflurry import Class1PresentationPredictor

# Load predictor (includes processing, binding affinity, and presentation)
predictor = Class1PresentationPredictor.load()

# Predict for specific alleles and peptides
results = predictor.predict(
    peptides=["SIINFEKL", "GILGFVFTL", "NLVPMVATV", "YMLDLQPET"],
    alleles=["HLA-A*02:01", "HLA-A*02:01", "HLA-A*02:01", "HLA-A*02:01"],
    verbose=0
)

print(results[["peptide", "allele", "mhcflurry_affinity",
               "mhcflurry_processing_score", "mhcflurry_presentation_score"]])

# Scan all peptides from a protein sequence
from mhcflurry import Class1PresentationPredictor
predictor = Class1PresentationPredictor.load()

# Generate all 8-11mer peptides from a protein
protein = "MFVFLVLLPLVSSQCVNLTTRTQLPPAYTN..."
alleles = ["HLA-A*02:01", "HLA-B*07:02", "HLA-C*07:02",
           "HLA-A*24:02", "HLA-B*40:01", "HLA-C*03:04"]

results = predictor.predict_sequences(
    sequences={"protein1": protein},
    alleles=alleles,
    result="filtered",       # return only good binders
    comparison_quantity="affinity",
    filter_value=500          # IC50 < 500 nM
)
```

### NetMHCpan 4.1

```bash
# NetMHCpan: pan-allele MHC-I binding predictor
# Supports >12,000 MHC-I alleles across species

netMHCpan \
  -a HLA-A02:01,HLA-B07:02,HLA-C07:02 \
  -l 8,9,10,11 \
  -f peptides.fasta \
  -BA \
  -xls \
  -xlsfile netmhcpan_results.xls

# Key output columns:
# Pos  HLA       Peptide      Core    iCore   EL-score  EL_Rank  BA-score  BA_Rank  Aff(nM)
# 1    HLA-A02:01 GILGFVFTL  GILGFVFTL GILGFVFTL 0.9876  0.010    0.8901   0.050    5.2

# Alternative: run as Python subprocess
import subprocess
result = subprocess.run(
    ["netMHCpan", "-a", "HLA-A02:01", "-l", "9", "-p", "GILGFVFTL"],
    capture_output=True, text=True
)
```

### Binding Affinity Interpretation

| Metric | Strong Binder | Weak Binder | Non-Binder | Notes |
|--------|--------------|-------------|------------|-------|
| **IC50 (nM)** | <50 | 50-500 | >500 | Absolute affinity; allele-dependent |
| **%Rank EL** | <0.5% | 0.5-2.0% | >2.0% | Eluted ligand percentile; cross-allele comparable |
| **%Rank BA** | <0.5% | 0.5-2.0% | >2.0% | Binding affinity percentile |
| **Presentation score** | >0.7 | 0.3-0.7 | <0.3 | MHCflurry combined score |

### Why Use Percentile Rank Over IC50

```
Problem with absolute IC50:
- Different alleles have different affinity ranges
- HLA-A*02:01 typical binder: IC50 ~10-50 nM
- HLA-B*27:05 typical binder: IC50 ~50-200 nM
- Same 500 nM threshold means different things for each allele

Solution: percentile rank
- Rank peptide against random peptide set for that specific allele
- %Rank <0.5%: top 0.5% of predicted binding = strong binder
- Comparable across all alleles
- Recommended for filtering and prioritization

Best practice:
- Use %Rank EL (eluted ligand) as primary filter: <2.0%
- Use IC50 as secondary filter: <500 nM
- Report both for transparency
```

---

## Phase 3: MHC-II Binding Prediction

### NetMHCIIpan 4.0

```bash
# MHC-II binding prediction
netMHCIIpan \
  -a DRB1_0101,DRB1_0301,DRB1_0401,DRB1_0701,DRB1_1101,DRB1_1501 \
  -length 15 \
  -f peptides.fasta \
  -BA \
  -xls \
  -xlsfile netmhciipan_results.xls

# Key parameters:
# -a: alleles (DRB1, DQA1-DQB1, DPA1-DPB1)
# -length: peptide length (13-25, default 15)
# -BA: include binding affinity prediction (not just EL)
```

### MHC-II Binding Interpretation

| Parameter | Value | Notes |
|-----------|-------|-------|
| Core region | 9 amino acids | Actual MHC-II binding core within longer peptide |
| Peptide length | 13-25 aa | Typically test 15-mers |
| Strong binder | %Rank <2% | Less strict than class I due to open binding groove |
| Weak binder | %Rank 2-10% | May still be immunogenic |
| CD4+ response | Helper T cells | Enhances CD8+ response and antibody production |

---

## Phase 4: T-Cell Epitope Prediction Beyond MHC Binding

### Immunogenicity Scoring

```python
# MHC binding is necessary but not sufficient for immunogenicity
# Additional factors to consider:

# 1. Proteasomal cleavage prediction
# NetChop: predicts C-terminal cleavage
import subprocess
result = subprocess.run(
    ["netchop", "protein.fasta", "--method", "cterm", "--threshold", "0.5"],
    capture_output=True, text=True
)

# 2. TAP transport prediction
# Peptides must be transported into ER by TAP
# NetCTLpan combines: MHC binding + proteasomal cleavage + TAP transport
result = subprocess.run(
    ["netCTLpan", "-a", "HLA-A02:01", "-l", "9", "protein.fasta"],
    capture_output=True, text=True
)

# 3. IEDB immunogenicity predictor
# Predicts T-cell immunogenicity based on amino acid properties
# Uses position-weighted amino acid features
# Available at: http://tools.iedb.org/immunogenicity/
```

### Immunogenicity Factors Hierarchy

```
MHC binding (necessary):
│ %Rank < 2% (class I) or < 10% (class II)
│
├── Proteasomal cleavage (C-terminus generated):
│   NetChop score > 0.5
│
├── TAP transport efficiency:
│   TAP score > 0.5 (for cytosolic peptides)
│
├── Peptide-MHC stability:
│   Half-life > 1 hour
│
├── TCR-facing residue properties:
│   Positions 4, 5, 6, 7, 8 (for 9-mers)
│   Aromatic/large residues → more immunogenic
│   Self-similarity score < 1.0 → more foreign
│
└── Expression level:
    TPM > 1 in tumor cells → peptide actually produced
```

---

## Phase 5: B-Cell Epitope Prediction

### Linear B-Cell Epitopes

```python
# BepiPred 3.0: sequence-based B-cell epitope prediction
# Uses ESM protein language model embeddings

# Command-line usage
# Input: protein FASTA
# Output: per-residue epitope probability

import subprocess
result = subprocess.run(
    ["bepipred3", "-i", "protein.fasta", "-o", "bepipred_results/",
     "--threshold", "0.5"],
    capture_output=True, text=True
)

# Parse results
import pandas as pd
scores = pd.read_csv("bepipred_results/prediction.csv")
epitope_residues = scores[scores["score"] > 0.5]
```

### B-Cell Epitope Properties

| Property | Method | Tool | Threshold |
|----------|--------|------|-----------|
| **Linear epitope** | Sequence-based ML | BepiPred 3.0 | Score > 0.5 |
| **Surface accessibility** | Emini surface accessibility | IEDB tools | Score > 1.0 |
| **Hydrophilicity** | Parker hydrophilicity | IEDB tools | Score > 0 |
| **Flexibility** | Karplus-Schulz flexibility | IEDB tools | Score > 1.0 |
| **Antigenicity** | Kolaskar-Tongaonkar | IEDB tools | Score > 1.0 |

### Conformational B-Cell Epitopes

```
Conformational epitope prediction requires 3D structure:
- DiscoTope 2.0: uses structure + sequence features
- ElliPro: protrusion index from 3D structure
- SEPPA 3.0: spatial epitope prediction

Input: PDB structure file
- Crystal structure preferred
- AlphaFold2 model acceptable (check pLDDT at epitope residues)
- Minimum pLDDT > 70 for reliable surface prediction
```

---

## Phase 6: Neoantigen Prediction Pipeline

### End-to-End Neoantigen Workflow

```
Tumor WES/WGS + Normal WES/WGS
│
├── 1. Somatic variant calling
│   ├── Mutect2 (SNVs + indels)
│   ├── Strelka2 (SNVs + indels)
│   └── Consensus: ≥2 callers agree
│
├── 2. HLA typing
│   ├── OptiType (class I from WES/WGS)
│   ├── HLA-HD (class I + II)
│   └── Verify with RNA-seq if available
│
├── 3. Peptide generation
│   ├── Extract mutant protein sequences from VCF + reference
│   ├── Generate all 8-11mer peptides spanning each mutation
│   ├── Include matching wildtype peptides for comparison
│   └── Handle frameshifts: novel peptides until stop codon
│
├── 4. MHC binding prediction
│   ├── MHCflurry or NetMHCpan for class I
│   ├── NetMHCIIpan for class II
│   └── Filter: %Rank < 2% (class I), < 10% (class II)
│
├── 5. Expression filtering
│   ├── RNA-seq: TPM > 1 for mutant gene
│   ├── Variant allele frequency in RNA (VAF_RNA > 0.05)
│   └── Verify mutation expressed in tumor
│
├── 6. Prioritization scoring
│   ├── Binding affinity (IC50, %Rank)
│   ├── Expression level (TPM)
│   ├── Clonality (variant allele frequency)
│   ├── Agretopicity (mutant/WT affinity ratio)
│   ├── Foreignness (dissimilarity to self-proteome)
│   └── Combined neoantigen quality score
│
└── 7. Output: ranked neoantigen candidates
```

### pVACseq (pVACtools)

```bash
# pVACseq: comprehensive neoantigen prediction pipeline
pvacseq run \
  annotated_variants.vcf \
  sample_name \
  "HLA-A*02:01,HLA-A*24:02,HLA-B*07:02,HLA-B*40:01,HLA-C*03:04,HLA-C*07:02" \
  MHCflurry MHCnuggetsI NetMHCpan \
  output_dir/ \
  --iedb-install-directory /opt/iedb/ \
  -e1 8,9,10,11 \
  -e2 15 \
  --binding-threshold 500 \
  --percentile-threshold 2 \
  --top-score-metric lowest \
  --net-chop-method cterm \
  --netmhc-stab \
  --normal-sample-name normal \
  -t 8

# Key parameters:
# -e1: MHC-I epitope lengths (8-11)
# -e2: MHC-II epitope lengths (15)
# --binding-threshold: IC50 cutoff (nM)
# --percentile-threshold: %Rank cutoff
# --net-chop-method: include proteasomal cleavage
# --netmhc-stab: include MHC stability prediction
```

### Peptide Generation from Variants

```python
import pyensembl
from pyensembl import EnsemblRelease

# Load Ensembl annotation
ensembl = EnsemblRelease(release=110, species="human")

def generate_mutant_peptides(chrom, pos, ref, alt, flank=10):
    """Generate mutant and wildtype peptides spanning a mutation."""
    # Get affected transcripts
    transcripts = ensembl.transcripts_at_locus(chrom, pos)

    peptides = []
    for tx in transcripts:
        if not tx.is_protein_coding:
            continue

        # Get protein sequence and mutation position
        # ... (variant effect prediction with VEP/SnpEff)

        # For missense: extract flanking peptides
        # For each peptide length (8-11 for class I)
        for length in range(8, 12):
            for start in range(max(0, mut_pos - length + 1), mut_pos + 1):
                end = start + length
                if end <= len(protein_seq):
                    mut_pep = mutant_protein[start:end]
                    wt_pep = wildtype_protein[start:end]
                    peptides.append({
                        "mutant_peptide": mut_pep,
                        "wildtype_peptide": wt_pep,
                        "mutation_position": mut_pos - start,
                        "length": length,
                        "transcript": tx.id,
                        "variant": f"{chrom}:{pos}{ref}>{alt}"
                    })
    return peptides
```

---

## Phase 7: Neoantigen Quality Scoring

### Agretopicity (Differential Agretopicity Index)

```python
# Agretopicity: ratio of mutant to wildtype MHC binding
# High agretopicity = mutation improves MHC binding = more likely immunogenic

def calculate_agretopicity(mutant_ic50, wildtype_ic50):
    """
    DAI = wildtype_IC50 / mutant_IC50
    or equivalently: log2(wildtype_IC50) - log2(mutant_IC50)

    DAI > 1: mutation improves binding (favorable)
    DAI = 1: no change
    DAI < 1: mutation reduces binding (unfavorable for neoantigen)
    """
    import numpy as np
    dai = wildtype_ic50 / mutant_ic50
    log2_dai = np.log2(dai)
    return dai, log2_dai

# Example:
# Mutant IC50 = 10 nM, Wildtype IC50 = 5000 nM
# DAI = 500 (very high agretopicity — excellent neoantigen candidate)
```

### Foreignness Score

```python
# Foreignness: dissimilarity of mutant peptide to closest self-peptide
# High foreignness = peptide looks foreign to immune system

from Bio import pairwise2

def foreignness_score(mutant_peptide, self_proteome_peptides):
    """
    Compare mutant peptide against all self-peptides that bind the same HLA.
    Score = 1 - (max_similarity_to_self)

    Higher foreignness = less likely to be tolerized
    """
    max_similarity = 0
    for self_pep in self_proteome_peptides:
        alignment = pairwise2.align.globalxx(mutant_peptide, self_pep)
        score = alignment[0].score / len(mutant_peptide)
        if score > max_similarity:
            max_similarity = score

    return 1 - max_similarity
```

### Comprehensive Neoantigen Scoring

| Feature | Weight | Threshold | Rationale |
|---------|--------|-----------|-----------|
| **MHC binding (IC50)** | High | <500 nM | Required for presentation |
| **%Rank** | High | <2% | Cross-allele comparable |
| **Expression (TPM)** | High | >1 TPM | Peptide must be produced |
| **Variant allele frequency** | Medium | >0.1 | Prefer clonal mutations |
| **Agretopicity (DAI)** | Medium | >1 | Mutation improves binding |
| **Foreignness** | Medium | >0.5 | Dissimilar to self |
| **Proteasomal cleavage** | Low | Score >0.5 | C-terminus generated |
| **TAP transport** | Low | Score >0.5 | Peptide reaches ER |
| **MHC stability** | Medium | T1/2 >1hr | Stable pMHC complex |
| **Mutation type** | Varies | - | Frameshift > missense for novelty |

### Neoantigen Prioritization Algorithm

```python
import pandas as pd
import numpy as np

def score_neoantigens(df):
    """
    Composite scoring for neoantigen prioritization.
    Input df columns: peptide, allele, ic50, percentile_rank,
                      expression_tpm, vaf, dai, foreignness
    """
    # Binding score (log-scaled IC50, capped)
    df["binding_score"] = 1 - np.log10(df["ic50"].clip(1, 50000)) / np.log10(50000)

    # Expression score (log-scaled TPM)
    df["expression_score"] = np.log2(df["expression_tpm"].clip(0.01, 1000) + 1) / 10

    # Clonality score (prefer high VAF = clonal)
    df["clonality_score"] = df["vaf"].clip(0, 1)

    # Agretopicity score
    df["agretopicity_score"] = np.log2(df["dai"].clip(0.1, 1000)) / 10

    # Composite score
    df["neoantigen_score"] = (
        0.30 * df["binding_score"] +
        0.25 * df["expression_score"] +
        0.20 * df["clonality_score"] +
        0.15 * df["agretopicity_score"] +
        0.10 * df["foreignness"]
    )

    return df.sort_values("neoantigen_score", ascending=False)
```

---

## Phase 8: Tumor Mutational Burden (TMB)

### TMB Calculation

```python
def calculate_tmb(vcf_path, panel_size_mb=None):
    """
    TMB = total nonsynonymous mutations / exome size (Mb)

    Parameters:
    - vcf_path: somatic VCF (filtered, PASS only)
    - panel_size_mb: if panel sequencing, size in Mb
      WES: ~30-40 Mb
      WGS: ~3000 Mb (but report per Mb)
      Panels: F1CDx=0.8 Mb, TSO500=1.94 Mb, MSK-IMPACT=1.2 Mb
    """
    import pysam

    vcf = pysam.VariantFile(vcf_path)
    mutation_count = 0

    for record in vcf:
        if "PASS" not in record.filter:
            continue
        # Count nonsynonymous variants (missense, nonsense, frameshift)
        info_csq = record.info.get("CSQ", None) or record.info.get("ANN", None)
        if is_nonsynonymous(info_csq):
            mutation_count += 1

    if panel_size_mb is None:
        panel_size_mb = 35.0  # default WES size

    tmb = mutation_count / panel_size_mb
    return tmb, mutation_count
```

### TMB Interpretation

| TMB (mut/Mb) | Category | Clinical Context |
|-------------|----------|-----------------|
| <5 | Low | Limited neoantigen generation |
| 5-10 | Intermediate | Moderate neoantigen potential |
| 10-20 | High | Likely responds to checkpoint inhibitors |
| >20 | Very high | Strong candidate for immunotherapy |
| >100 | Hypermutated | MMR deficiency, POLE mutations, UV signature |

### TMB by Cancer Type (Typical Ranges)

```
High TMB cancers (median >10 mut/Mb):
- Melanoma (~15-30 mut/Mb) — UV signature
- NSCLC smokers (~10-15 mut/Mb) — tobacco signature
- Bladder cancer (~10-15 mut/Mb)
- MSI-high cancers (~30-100 mut/Mb)

Low TMB cancers (median <5 mut/Mb):
- Pediatric tumors (~1-2 mut/Mb)
- AML/MDS (~1-2 mut/Mb)
- Breast cancer HR+ (~2-3 mut/Mb)
- Prostate cancer (~2-3 mut/Mb)

Note: individual variation is large; TMB cutoffs are guidelines, not absolute
```

---

## Phase 9: Vaccine Design

### Multi-Epitope Construct Optimization

```python
def design_vaccine_construct(epitopes, linkers="AAY"):
    """
    Design multi-epitope vaccine construct.

    Considerations:
    1. Epitope ordering: avoid creating junctional epitopes
    2. Linker selection: AAY, GPGPG, KK for class I; GPGPG for class II
    3. Adjuvant sequences: optional N-terminal (e.g., beta-defensin)
    4. Signal peptide for secretion
    """
    # Check for junctional epitopes at linker junctions
    construct = ""
    for i, epitope in enumerate(epitopes):
        construct += epitope
        if i < len(epitopes) - 1:
            construct += linkers

    # Verify no junctional epitopes bind MHC strongly
    junctions = []
    for i in range(len(construct) - 9):
        peptide = construct[i:i+9]
        if is_near_junction(i, epitopes, linkers):
            junctions.append(peptide)

    return construct, junctions

# Linker types:
# AAY: promotes proteasomal cleavage (class I epitopes)
# GPGPG: flexible, prevents junctional epitopes (class II)
# KK: cathepsin B cleavage (class II processing)
```

### Population Coverage Analysis

```python
# Ensure vaccine covers diverse HLA backgrounds

def calculate_population_coverage(epitopes_with_alleles, population="World"):
    """
    Calculate fraction of population covered by vaccine epitopes.
    Uses allele frequency data from IEDB/Allele Frequency Net Database.

    Target: >90% population coverage with class I epitopes
    Ideal: >95% with combined class I + class II
    """
    # Allele frequencies for common populations
    allele_freqs = {
        "World": {
            "HLA-A*02:01": 0.277, "HLA-A*01:01": 0.154,
            "HLA-A*03:01": 0.138, "HLA-A*24:02": 0.118,
            "HLA-A*11:01": 0.102, "HLA-B*07:02": 0.108,
            "HLA-B*08:01": 0.088, "HLA-B*44:02": 0.074,
            # ... more alleles
        }
    }

    # Coverage = 1 - product(1 - allele_freq) for all covered alleles
    covered_alleles = set()
    for epitope_data in epitopes_with_alleles:
        for allele in epitope_data["binding_alleles"]:
            covered_alleles.add(allele)

    # Population coverage formula (IEDB methodology)
    uncovered = 1.0
    for allele in covered_alleles:
        freq = allele_freqs.get(population, {}).get(allele, 0)
        uncovered *= (1 - freq)

    coverage = 1 - uncovered
    return coverage

# Minimum coverage targets:
# Global vaccine: >90% world population
# Regional vaccine: >95% target population
# Personalized: patient's own HLA alleles (100%)
```

### Vaccine Design Checklist

```
Epitope selection:
- [ ] ≥5 class I epitopes (8-11 aa) covering ≥3 HLA supertypes
- [ ] ≥3 class II epitopes (15 aa) for CD4+ help
- [ ] Population coverage >90% for target population
- [ ] No epitopes with >80% identity to common human proteins
- [ ] Expression confirmed in target tissue/pathogen

Construct design:
- [ ] Appropriate linkers (AAY for class I, GPGPG for class II)
- [ ] No junctional neoepitopes at linker sites
- [ ] Signal peptide included if secretion needed
- [ ] Codon optimization for expression system
- [ ] Predicted to be soluble (check hydrophobicity)

Validation predictions:
- [ ] Allergenicity check (AllerTOP or AlgPred)
- [ ] Antigenicity check (VaxiJen score > 0.4)
- [ ] Toxicity check (ToxinPred)
- [ ] Molecular weight and pI suitable for production
```

---

## Phase 10: Key Databases and Resources

### Allele Frequency Databases

| Database | Content | URL |
|----------|---------|-----|
| **IEDB** | Experimentally validated epitopes | iedb.org |
| **Allele Frequency Net** | HLA allele frequencies by population | allelefrequencies.net |
| **IPD-IMGT/HLA** | HLA sequence database | ebi.ac.uk/ipd/imgt/hla |
| **dbMHC** | MHC genotype/haplotype data | ncbi.nlm.nih.gov/gv/mhc |

### MHC Supertype Classification

| Supertype | Representative Alleles | Binding Preference |
|-----------|----------------------|-------------------|
| **A02** | A*02:01, A*02:06, A*68:02 | Hydrophobic at P2 (L/M) |
| **A03** | A*03:01, A*11:01, A*31:01 | Basic residue at P9 (K/R) |
| **A01** | A*01:01, A*26:01, A*32:01 | Small at P2 (T/S), aromatic at P9 |
| **A24** | A*24:02, A*23:01 | Aromatic/hydrophobic at P2 (Y/F) |
| **B07** | B*07:02, B*35:01, B*51:01 | Proline at P2 |
| **B27** | B*27:05, B*14:02 | Basic at P2 (R) |
| **B44** | B*44:02, B*44:03, B*18:01 | Acidic at P2 (E/D) |
| **B58** | B*57:01, B*58:01 | Small at P2 (A/S) |
| **B62** | B*15:01, B*46:01 | Hydrophobic at P2 |

---

## Decision Trees

### Neoantigen Analysis Decision Tree

```
Input: Tumor + Normal sequencing data
│
├── HLA typing
│   ├── WES/WGS available → OptiType (class I) + HLA-HD (class I+II)
│   ├── RNA-seq only → arcasHLA
│   └── Targeted panel → may need separate HLA typing assay
│
├── Variant calling → somatic SNVs, indels, fusions
│   ├── SNVs → missense, nonsense mutations
│   ├── Indels → frameshifts (novel ORF), in-frame indels
│   └── Fusions → novel junction peptides
│
├── Peptide generation
│   ├── Missense → 8-11mer windows spanning mutation
│   ├── Frameshift → all novel peptides until stop codon
│   └── Fusion → peptides spanning junction
│
├── Binding prediction
│   ├── Class I → MHCflurry or NetMHCpan-4.1
│   │   └── Filter: %Rank < 2.0%
│   └── Class II → NetMHCIIpan
│       └── Filter: %Rank < 10%
│
├── Expression filter
│   ├── RNA-seq available → TPM > 1, VAF_RNA > 0.05
│   └── No RNA-seq → skip (less confident)
│
├── Prioritization
│   ├── Agretopicity > 1
│   ├── Clonal (VAF > 0.1)
│   ├── Foreignness > 0.5
│   └── Composite neoantigen score
│
└── Output: ranked neoantigen candidates with evidence
```

### MHC Binding Tool Decision Tree

```
Which MHC binding predictor?
│
├── Class I
│   ├── Python workflow → MHCflurry 2.0
│   │   Pros: presentation score, processing model, easy API
│   ├── Maximum allele coverage → NetMHCpan 4.1
│   │   Pros: pan-allele, >12,000 alleles, gold standard
│   └── Multiple tools → pVACseq (runs several in parallel)
│
├── Class II
│   └── NetMHCIIpan → only comprehensive option
│
└── Both classes needed → pVACseq with MHCflurry + NetMHCpan + NetMHCIIpan
```

---

## Troubleshooting

```
Low neoantigen yield (few candidates):
├── Low TMB → expected for some cancer types; consider fusions, splicing neoantigens
├── Restrictive thresholds → relax to %Rank <5% or IC50 <1000 nM for exploratory
├── HLA typing incorrect → verify with orthogonal method
└── Variant filtering too strict → check somatic caller settings

High false positive rate:
├── No expression filtering → add RNA-seq expression requirement
├── Including passenger mutations → filter by clonality (VAF)
├── Germline contamination → verify somatic variant calling with matched normal
└── Self-similar epitopes → add foreignness filtering

HLA typing discordance between tools:
├── Low coverage at HLA locus → check depth (need >30x)
├── Novel alleles → may not be in database
├── Heterozygous vs homozygous ambiguity → check zygosity
└── Use consensus: agreement between ≥2 tools
```

## Completeness Checklist

- [ ] HLA typing performed (class I minimum; class II if possible)
- [ ] HLA typing QC passed (read count, concordance)
- [ ] Somatic variants called and filtered (PASS, nonsynonymous)
- [ ] Mutant and wildtype peptides generated for all variant types
- [ ] MHC-I binding predicted (MHCflurry or NetMHCpan)
- [ ] MHC-II binding predicted (NetMHCIIpan) if class II alleles available
- [ ] Expression filtering applied (if RNA-seq available)
- [ ] Neoantigen quality scored (agretopicity, foreignness, clonality)
- [ ] TMB calculated and contextualized by cancer type
- [ ] Top candidates ranked with supporting evidence
- [ ] Population coverage calculated (if vaccine design)
