# Variant Annotation and Functional Prediction Recipes

Code templates for variant annotation, functional impact prediction, and pathogenicity scoring. Covers VEP, SnpEff, ANNOVAR, bcftools, CADD, SpliceAI, REVEL, ClinVar, gnomAD filtering, LOFTEE, VCF parsing, and multi-sample annotation pipelines.

Cross-skill routing: use `variant-analysis` for upstream QC and filtering, `variant-interpretation` for ACMG classification, `cancer-variant-interpreter` for somatic variant interpretation.

---

## 1. VEP (Ensembl Variant Effect Predictor) Command-Line with Cache

Run VEP with local cache for fast offline annotation.

```bash
#!/bin/bash
# VEP annotation with local cache
# Prerequisites: VEP installed, cache downloaded for species/assembly

INPUT_VCF="input.vcf.gz"
OUTPUT_VCF="annotated_vep.vcf"
CACHE_DIR="$HOME/.vep"
ASSEMBLY="GRCh38"
SPECIES="homo_sapiens"

vep \
  --input_file "$INPUT_VCF" \
  --output_file "$OUTPUT_VCF" \
  --vcf \
  --cache \
  --dir_cache "$CACHE_DIR" \
  --assembly "$ASSEMBLY" \
  --species "$SPECIES" \
  --offline \
  --force_overwrite \
  --everything \
  --fork 4 \
  --buffer_size 5000 \
  --pick \
  --plugin CADD,"$CACHE_DIR/CADD_GRCh38_whole_genome_SNVs.tsv.gz" \
  --plugin SpliceAI,snv="$CACHE_DIR/spliceai_scores.raw.snv.hg38.vcf.gz",indel="$CACHE_DIR/spliceai_scores.raw.indel.hg38.vcf.gz" \
  --plugin REVEL,"$CACHE_DIR/new_tabbed_revel_grch38.tsv.gz" \
  --plugin LOFTEE,loftee_path="$CACHE_DIR/loftee" \
  --plugin ClinVar,file="$CACHE_DIR/clinvar.vcf.gz" \
  --fasta "$CACHE_DIR/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz"

echo "VEP annotation complete: $OUTPUT_VCF"
```

**Key parameters:**
- `--everything`: includes SIFT, PolyPhen, frequencies, regulatory, conservation scores.
- `--pick`: selects one consequence per variant (most severe). Use `--per_gene` for one per gene.
- `--fork 4`: parallel processes. Adjust based on available cores.
- `--buffer_size 5000`: variants processed in each batch. Increase for faster throughput.
- Plugins: CADD, SpliceAI, REVEL, LOFTEE, ClinVar provide additional prediction scores.

**Expected output:** VCF with CSQ INFO field containing pipe-delimited annotation fields.

---

## 2. SnpEff Annotation with Custom Genome Databases

Annotate variants using SnpEff with built-in or custom genome databases.

```bash
#!/bin/bash
# SnpEff annotation
INPUT_VCF="input.vcf.gz"
OUTPUT_VCF="annotated_snpeff.vcf"
GENOME="GRCh38.105"  # or hg38, GRCh37.75

# Basic annotation
snpEff ann \
  -v "$GENOME" \
  -stats snpeff_stats.html \
  -csvStats snpeff_stats.csv \
  "$INPUT_VCF" > "$OUTPUT_VCF"

# With custom database
# First build: snpEff build -gff3 custom_genome
snpEff ann \
  -v "$GENOME" \
  -canon \
  -nodownload \
  -no-intergenic \
  -no-downstream \
  -no-upstream \
  "$INPUT_VCF" > "$OUTPUT_VCF"

echo "SnpEff annotation complete: $OUTPUT_VCF"
```

```python
import pandas as pd
import re

def parse_snpeff_ann(info_str):
    """Parse SnpEff ANN field from VCF INFO column.

    Returns list of dicts with annotation fields.
    ANN format: Allele|Annotation|Impact|Gene_Name|Gene_ID|Feature_Type|
                Feature_ID|Transcript_BioType|Rank|HGVS.c|HGVS.p|...
    """
    ann_fields = [
        "Allele", "Annotation", "Annotation_Impact", "Gene_Name", "Gene_ID",
        "Feature_Type", "Feature_ID", "Transcript_BioType", "Rank",
        "HGVS_c", "HGVS_p", "cDNA_pos", "CDS_pos", "AA_pos", "Distance", "Errors"
    ]
    match = re.search(r'ANN=([^;]+)', info_str)
    if not match:
        return []

    annotations = []
    for ann_entry in match.group(1).split(","):
        fields = ann_entry.split("|")
        ann_dict = {ann_fields[i]: fields[i] if i < len(fields) else ""
                    for i in range(len(ann_fields))}
        annotations.append(ann_dict)

    return annotations

def extract_snpeff_summary(vcf_path):
    """Extract gene-level summary from SnpEff annotated VCF."""
    import gzip
    opener = gzip.open if vcf_path.endswith(".gz") else open
    gene_counts = {}
    with opener(vcf_path, "rt") as f:
        for line in f:
            if line.startswith("#"):
                continue
            fields = line.strip().split("\t")
            info = fields[7]
            for ann in parse_snpeff_ann(info):
                gene = ann["Gene_Name"]
                impact = ann["Annotation_Impact"]
                if gene:
                    gene_counts.setdefault(gene, {"HIGH": 0, "MODERATE": 0, "LOW": 0, "MODIFIER": 0})
                    gene_counts[gene][impact] = gene_counts[gene].get(impact, 0) + 1

    df = pd.DataFrame(gene_counts).T
    df["total"] = df.sum(axis=1)
    return df.sort_values("total", ascending=False)

# Usage
gene_summary = extract_snpeff_summary("annotated_snpeff.vcf")
print(gene_summary.head(20))
```

**Key parameters:**
- `-canon`: use only canonical transcripts (reduces annotation redundancy).
- `-no-intergenic`: skip intergenic variants (reduces output size for coding analyses).
- SnpEff impacts: HIGH (frameshift, stop_gained), MODERATE (missense), LOW (synonymous), MODIFIER (intronic).

**Expected output:** VCF with ANN INFO field; gene-level variant count summary.

---

## 3. ANNOVAR: table_annovar.pl with Multiple Databases

Comprehensive annotation using ANNOVAR's multi-database pipeline.

```bash
#!/bin/bash
# ANNOVAR multi-database annotation
INPUT_VCF="input.vcf"
ANNOVAR_DIR="/opt/annovar"
HUMANDB="$ANNOVAR_DIR/humandb"
OUTPUT_PREFIX="annotated"

# Convert VCF to ANNOVAR format
"$ANNOVAR_DIR/convert2annovar.pl" \
  -format vcf4 "$INPUT_VCF" \
  -outfile input.avinput \
  -includeinfo

# Run table_annovar with multiple databases
"$ANNOVAR_DIR/table_annovar.pl" \
  input.avinput \
  "$HUMANDB" \
  -buildver hg38 \
  -out "$OUTPUT_PREFIX" \
  -remove \
  -protocol refGene,gnomad30_genome,clinvar_20230416,dbnsfp42a,dbscsnv11,avsnp150 \
  -operation g,f,f,f,f,f \
  -nastring . \
  -csvout \
  -polish

echo "ANNOVAR annotation complete: ${OUTPUT_PREFIX}.hg38_multianno.csv"
```

```python
import pandas as pd

def load_annovar_output(filepath):
    """Load ANNOVAR multianno output and extract key columns.

    Parameters:
        filepath: path to .hg38_multianno.csv or .hg38_multianno.txt
    Returns:
        DataFrame with parsed annotations
    """
    sep = "," if filepath.endswith(".csv") else "\t"
    df = pd.read_csv(filepath, sep=sep, low_memory=False)

    # Standardize column names
    rename_map = {
        "Chr": "CHROM", "Start": "POS", "End": "END",
        "Ref": "REF", "Alt": "ALT",
        "Func.refGene": "func_region", "Gene.refGene": "gene",
        "ExonicFunc.refGene": "exonic_func",
        "AAChange.refGene": "aa_change",
        "gnomAD_genome_ALL": "gnomad_af",
        "CLNSIG": "clinvar_sig",
        "SIFT_pred": "sift_pred", "Polyphen2_HDIV_pred": "polyphen_pred",
        "CADD_phred": "cadd_phred", "REVEL_score": "revel_score",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # Convert numeric columns
    for col in ["gnomad_af", "cadd_phred", "revel_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    print(f"Loaded {len(df)} variants from ANNOVAR output")
    print(f"Functional regions: {df['func_region'].value_counts().head()}")
    return df

# Usage
annovar_df = load_annovar_output("annotated.hg38_multianno.csv")

# Filter for exonic non-synonymous variants
coding = annovar_df[
    (annovar_df["func_region"].isin(["exonic", "splicing"])) &
    (annovar_df["exonic_func"] != "synonymous SNV")
]
print(f"Coding non-synonymous: {len(coding)}")
```

**Key parameters:**
- `-protocol`: comma-separated database list. `g` = gene-based, `f` = filter-based, `r` = region-based.
- Common databases: refGene (gene annotation), gnomad30_genome (population freq), clinvar (clinical significance), dbnsfp42a (SIFT/PolyPhen/CADD/REVEL), avsnp150 (rsIDs).
- `-nastring .`: replaces missing annotations with ".".

**Expected output:** CSV/TSV with one row per variant, columns from each annotation database.

---

## 4. bcftools annotate with Custom BED/VCF Annotation Sources

Add custom annotations to VCF files using bcftools.

```bash
#!/bin/bash
# Annotate VCF with custom BED regions and VCF databases

INPUT_VCF="input.vcf.gz"
CUSTOM_BED="regulatory_regions.bed.gz"  # must be bgzipped + tabixed
CUSTOM_VCF="custom_database.vcf.gz"     # must be bgzipped + tabixed
OUTPUT_VCF="annotated_custom.vcf.gz"

# Step 1: Annotate with BED file (adds INFO tags based on overlap)
bcftools annotate \
  -a "$CUSTOM_BED" \
  -c CHROM,FROM,TO,REGION_TYPE \
  -h <(echo '##INFO=<ID=REGION_TYPE,Number=1,Type=String,Description="Regulatory region type">') \
  "$INPUT_VCF" \
  -Oz -o temp_annotated.vcf.gz

tabix -p vcf temp_annotated.vcf.gz

# Step 2: Annotate with custom VCF (transfer INFO fields)
bcftools annotate \
  -a "$CUSTOM_VCF" \
  -c INFO/CUSTOM_AF,INFO/CUSTOM_SCORE \
  temp_annotated.vcf.gz \
  -Oz -o "$OUTPUT_VCF"

tabix -p vcf "$OUTPUT_VCF"
echo "Custom annotation complete: $OUTPUT_VCF"
```

```python
import subprocess

def bcftools_annotate(input_vcf, annotation_source, columns, output_vcf,
                      header_lines=None):
    """Annotate VCF using bcftools annotate.

    Parameters:
        input_vcf: input VCF path (bgzipped)
        annotation_source: BED or VCF file (bgzipped + tabixed)
        columns: column specification string (e.g., 'CHROM,FROM,TO,INFO/TAG')
        output_vcf: output VCF path
        header_lines: list of VCF header lines for new INFO fields
    """
    cmd = ["bcftools", "annotate", "-a", annotation_source, "-c", columns]

    if header_lines:
        header_file = "_temp_header.txt"
        with open(header_file, "w") as f:
            f.write("\n".join(header_lines) + "\n")
        cmd.extend(["-h", header_file])

    cmd.extend([input_vcf, "-Oz", "-o", output_vcf])
    subprocess.run(cmd, check=True)
    subprocess.run(["tabix", "-p", "vcf", output_vcf], check=True)

    print(f"Annotated: {output_vcf}")

# Usage
bcftools_annotate(
    "input.vcf.gz",
    "gnomad.exomes.vcf.gz",
    "INFO/AF,INFO/AC,INFO/AN",
    "annotated.vcf.gz"
)
```

**Key parameters:**
- `-c`: column specification. For BED: `CHROM,FROM,TO,TAG`. For VCF: `INFO/FIELD1,INFO/FIELD2`.
- `-h`: header file with new INFO field definitions (required for BED annotations).
- Annotation source must be bgzipped and tabix-indexed.

**Expected output:** VCF with new INFO fields from the annotation source.

---

## 5. CADD Score Retrieval and Interpretation

Retrieve and interpret Combined Annotation Dependent Depletion (CADD) scores.

```python
import pandas as pd
import numpy as np

def parse_cadd_scores(tsv_path):
    """Parse CADD score output file.

    Parameters:
        tsv_path: path to CADD output TSV (from CADD web service or local scoring)
    Returns:
        DataFrame with CADD scores
    """
    df = pd.read_csv(tsv_path, sep="\t", comment="#",
                     names=["Chrom", "Pos", "Ref", "Alt", "RawScore", "PHRED"])
    print(f"Loaded {len(df)} CADD scores")
    print(f"PHRED range: [{df['PHRED'].min():.1f}, {df['PHRED'].max():.1f}]")
    return df

def interpret_cadd(phred_score):
    """Interpret CADD PHRED score.

    CADD PHRED interpretation:
        >= 30: top 0.1% most deleterious (likely pathogenic)
        >= 20: top 1% most deleterious (possibly pathogenic)
        >= 15: top 3% most deleterious (uncertain)
        >= 10: top 10% most deleterious (likely benign)
        < 10:  bottom 90% (benign)
    """
    if phred_score >= 30:
        return "Likely deleterious (top 0.1%)"
    elif phred_score >= 20:
        return "Possibly deleterious (top 1%)"
    elif phred_score >= 15:
        return "Uncertain significance (top 3%)"
    elif phred_score >= 10:
        return "Likely benign (top 10%)"
    else:
        return "Benign"

def add_cadd_to_variants(variant_df, cadd_df, chrom_col="CHROM", pos_col="POS",
                          ref_col="REF", alt_col="ALT"):
    """Merge CADD scores into a variant DataFrame.

    Parameters:
        variant_df: DataFrame with variant positions
        cadd_df: DataFrame from parse_cadd_scores
        chrom_col, pos_col, ref_col, alt_col: column names in variant_df
    Returns:
        variant_df with CADD_PHRED and CADD_interpretation columns
    """
    cadd_df["key"] = cadd_df["Chrom"].astype(str) + ":" + cadd_df["Pos"].astype(str) + \
                     ":" + cadd_df["Ref"] + ">" + cadd_df["Alt"]
    variant_df["key"] = variant_df[chrom_col].astype(str) + ":" + variant_df[pos_col].astype(str) + \
                        ":" + variant_df[ref_col] + ">" + variant_df[alt_col]

    cadd_map = dict(zip(cadd_df["key"], cadd_df["PHRED"]))
    variant_df["CADD_PHRED"] = variant_df["key"].map(cadd_map)
    variant_df["CADD_interpretation"] = variant_df["CADD_PHRED"].apply(
        lambda x: interpret_cadd(x) if pd.notna(x) else "No score"
    )
    variant_df = variant_df.drop(columns=["key"])

    scored = variant_df["CADD_PHRED"].notna().sum()
    print(f"CADD scores mapped: {scored}/{len(variant_df)}")
    print(f"PHRED >= 20: {(variant_df['CADD_PHRED'] >= 20).sum()}")

    return variant_df

# Usage
cadd_scores = parse_cadd_scores("cadd_output.tsv")
variants = add_cadd_to_variants(variants, cadd_scores)
```

**Key parameters:**
- PHRED >= 20: commonly used threshold for "likely deleterious" in clinical pipelines.
- PHRED >= 15: more permissive threshold used in some research contexts.
- CADD scores SNVs and short indels; not applicable to structural variants.

**Expected output:** Variant DataFrame with CADD_PHRED scores and human-readable interpretations.

---

## 6. SpliceAI: Splice-Altering Variant Prediction

Predict splice-altering effects using SpliceAI deep learning scores.

```bash
#!/bin/bash
# SpliceAI command-line scoring
spliceai \
  -I input.vcf \
  -O spliceai_output.vcf \
  -R reference.fa \
  -A grch38 \
  -D 500

# D=500: maximum distance from variant to splice site (bp)
# Higher D = slower but more comprehensive (up to 10000)
```

```python
import pandas as pd
import re

def parse_spliceai_scores(vcf_path):
    """Parse SpliceAI scores from annotated VCF.

    SpliceAI INFO format: SpliceAI=ALLELE|SYMBOL|DS_AG|DS_AL|DS_DG|DS_DL|DP_AG|DP_AL|DP_DG|DP_DL
    DS = delta score (0-1), DP = delta position (distance to splice site)
    AG = acceptor gain, AL = acceptor loss, DG = donor gain, DL = donor loss
    """
    import gzip
    opener = gzip.open if vcf_path.endswith(".gz") else open
    records = []

    with opener(vcf_path, "rt") as f:
        for line in f:
            if line.startswith("#"):
                continue
            fields = line.strip().split("\t")
            chrom, pos, _, ref, alt = fields[0], int(fields[1]), fields[2], fields[3], fields[4]
            info = fields[7]

            match = re.search(r'SpliceAI=([^;]+)', info)
            if not match:
                continue

            for entry in match.group(1).split(","):
                parts = entry.split("|")
                if len(parts) < 10:
                    continue
                records.append({
                    "CHROM": chrom, "POS": pos, "REF": ref, "ALT": alt,
                    "gene": parts[1],
                    "DS_AG": float(parts[2]), "DS_AL": float(parts[3]),
                    "DS_DG": float(parts[4]), "DS_DL": float(parts[5]),
                    "DP_AG": int(parts[6]), "DP_AL": int(parts[7]),
                    "DP_DG": int(parts[8]), "DP_DL": int(parts[9]),
                })

    df = pd.DataFrame(records)
    df["max_DS"] = df[["DS_AG", "DS_AL", "DS_DG", "DS_DL"]].max(axis=1)

    # Classify splice impact
    df["splice_impact"] = df["max_DS"].apply(lambda x:
        "High (likely splice-altering)" if x >= 0.8 else
        "Moderate (possibly splice-altering)" if x >= 0.5 else
        "Low (unlikely splice-altering)" if x >= 0.2 else
        "Benign"
    )

    print(f"SpliceAI results: {len(df)} variants")
    print(f"  High impact (DS >= 0.8): {(df['max_DS'] >= 0.8).sum()}")
    print(f"  Moderate (DS >= 0.5): {((df['max_DS'] >= 0.5) & (df['max_DS'] < 0.8)).sum()}")

    return df

# Usage
spliceai_df = parse_spliceai_scores("spliceai_output.vcf")
splice_altering = spliceai_df[spliceai_df["max_DS"] >= 0.5]
```

**Key parameters:**
- DS >= 0.8: high confidence splice-altering (recommended clinical threshold).
- DS >= 0.5: moderate confidence (research threshold).
- DS >= 0.2: low confidence (flag for review).
- `-D 500`: distance parameter. 500 bp is standard; increase to 10000 for deep intronic variants.

**Expected output:** DataFrame with per-variant SpliceAI delta scores for acceptor/donor gain/loss.

---

## 7. REVEL: Rare Variant Pathogenicity Scoring

REVEL is an ensemble method combining 13 predictors for missense variant pathogenicity.

```python
import pandas as pd
import numpy as np

def load_revel_scores(revel_path, chrom=None):
    """Load REVEL score database (pre-computed genome-wide).

    Parameters:
        revel_path: path to REVEL TSV file (downloaded from https://sites.google.com/site/revelgenomics/)
        chrom: optional chromosome filter for memory efficiency
    Returns:
        DataFrame with REVEL scores indexed by variant key
    """
    cols = ["chr", "hg19_pos", "grch38_pos", "ref", "alt", "aaref", "aaalt",
            "REVEL_score"]
    df = pd.read_csv(revel_path, sep=",", usecols=cols, low_memory=False)

    if chrom:
        df = df[df["chr"] == int(chrom.replace("chr", ""))]

    df["key"] = "chr" + df["chr"].astype(str) + ":" + df["grch38_pos"].astype(str) + \
                ":" + df["ref"] + ">" + df["alt"]
    df = df.set_index("key")

    print(f"REVEL scores loaded: {len(df)} missense variants")
    return df

def interpret_revel(score):
    """Interpret REVEL score for missense variants.

    REVEL interpretation (Ioannidis et al., AJHG 2016):
        >= 0.932: Pathogenic (high specificity threshold, ClinGen)
        >= 0.773: Likely pathogenic (ClinGen supporting evidence)
        >= 0.5:   Uncertain (commonly used research threshold)
        >= 0.25:  Likely benign (ClinGen)
        < 0.25:   Benign
    """
    if score >= 0.932:
        return "Pathogenic"
    elif score >= 0.773:
        return "Likely pathogenic"
    elif score >= 0.5:
        return "Uncertain"
    elif score >= 0.25:
        return "Likely benign"
    else:
        return "Benign"

def add_revel_to_variants(variant_df, revel_df, chrom_col="CHROM", pos_col="POS",
                           ref_col="REF", alt_col="ALT"):
    """Merge REVEL scores into variant DataFrame."""
    variant_df["revel_key"] = variant_df[chrom_col].astype(str) + ":" + \
                               variant_df[pos_col].astype(str) + ":" + \
                               variant_df[ref_col] + ">" + variant_df[alt_col]

    revel_map = revel_df["REVEL_score"].to_dict()
    variant_df["REVEL_score"] = variant_df["revel_key"].map(revel_map)
    variant_df["REVEL_interpretation"] = variant_df["REVEL_score"].apply(
        lambda x: interpret_revel(x) if pd.notna(x) else "No score (non-missense)"
    )
    variant_df = variant_df.drop(columns=["revel_key"])

    scored = variant_df["REVEL_score"].notna().sum()
    print(f"REVEL scores mapped: {scored}/{len(variant_df)}")
    return variant_df

# Usage
revel_db = load_revel_scores("revel_all_chromosomes.csv")
variants = add_revel_to_variants(variants, revel_db)
```

**Key parameters:**
- REVEL >= 0.5: commonly used research threshold for pathogenicity screening.
- REVEL >= 0.773: ClinGen-recommended threshold for supporting pathogenic evidence.
- REVEL applies only to missense variants; not informative for LoF or synonymous.

**Expected output:** Variant DataFrame with REVEL_score and interpretation for missense variants.

---

## 8. ClinVar Annotation via VEP Plugin

Annotate variants with ClinVar clinical significance using VEP or direct lookup.

```python
import pandas as pd
import re

def parse_clinvar_from_vep(vcf_path, clinvar_field="ClinVar_CLNSIG"):
    """Extract ClinVar annotations from VEP-annotated VCF.

    Parameters:
        vcf_path: path to VEP-annotated VCF with ClinVar plugin
        clinvar_field: CSQ field name for ClinVar significance
    Returns:
        DataFrame with ClinVar annotations
    """
    import gzip
    opener = gzip.open if vcf_path.endswith(".gz") else open

    # Parse CSQ header to get field positions
    csq_fields = None
    records = []
    with opener(vcf_path, "rt") as f:
        for line in f:
            if line.startswith("##INFO=<ID=CSQ"):
                match = re.search(r'Format: (.+)"', line)
                if match:
                    csq_fields = match.group(1).split("|")
                continue
            if line.startswith("#"):
                continue
            if csq_fields is None:
                continue

            fields = line.strip().split("\t")
            info = fields[7]
            csq_match = re.search(r'CSQ=([^;]+)', info)
            if not csq_match:
                continue

            for csq_entry in csq_match.group(1).split(","):
                vals = csq_entry.split("|")
                csq_dict = {csq_fields[i]: vals[i] if i < len(vals) else ""
                           for i in range(len(csq_fields))}

                clinvar_sig = csq_dict.get(clinvar_field, "")
                if clinvar_sig:
                    records.append({
                        "CHROM": fields[0], "POS": int(fields[1]),
                        "REF": fields[3], "ALT": fields[4],
                        "gene": csq_dict.get("SYMBOL", ""),
                        "consequence": csq_dict.get("Consequence", ""),
                        "clinvar_sig": clinvar_sig,
                        "clinvar_id": csq_dict.get("ClinVar_CLNID", ""),
                    })

    df = pd.DataFrame(records)
    if len(df) > 0:
        print(f"ClinVar annotations: {len(df)} variants")
        print(f"Significance distribution:\n{df['clinvar_sig'].value_counts()}")
    return df

def classify_clinvar_actionability(clinvar_sig):
    """Classify ClinVar significance into actionable categories."""
    pathogenic = {"Pathogenic", "Likely_pathogenic", "Pathogenic/Likely_pathogenic"}
    benign = {"Benign", "Likely_benign", "Benign/Likely_benign"}
    vus = {"Uncertain_significance"}

    if clinvar_sig in pathogenic:
        return "Pathogenic"
    elif clinvar_sig in benign:
        return "Benign"
    elif clinvar_sig in vus:
        return "VUS"
    elif "Conflicting" in clinvar_sig:
        return "Conflicting"
    else:
        return "Other"

# Usage
clinvar_df = parse_clinvar_from_vep("annotated_vep.vcf")
clinvar_df["actionability"] = clinvar_df["clinvar_sig"].apply(classify_clinvar_actionability)
```

**Expected output:** DataFrame with ClinVar significance, variant IDs, and actionability classification.

---

## 9. gnomAD Allele Frequency Filtering

Filter variants by population allele frequency for rare disease analysis.

```python
import pandas as pd
import numpy as np

def gnomad_frequency_filter(variant_df, af_col="gnomad_af", max_af=0.01,
                            pop_af_cols=None, max_pop_af=0.03):
    """Filter variants by gnomAD allele frequency.

    Parameters:
        variant_df: DataFrame with gnomAD allele frequencies
        af_col: column with global allele frequency
        max_af: maximum global AF threshold (0.01 for rare disease)
        pop_af_cols: list of population-specific AF columns (e.g., gnomAD_AFR, gnomAD_NFE)
        max_pop_af: maximum AF in any single population
    Returns:
        filtered DataFrame
    """
    df = variant_df.copy()
    n_start = len(df)

    # Convert AF column
    df[af_col] = pd.to_numeric(df[af_col], errors="coerce")

    # Global AF filter
    global_mask = df[af_col].isna() | (df[af_col] <= max_af)
    df = df[global_mask]
    print(f"Global AF filter (AF <= {max_af}): {n_start} -> {len(df)}")

    # Population-specific AF filter
    if pop_af_cols:
        for col in pop_af_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
                pop_mask = df[col].isna() | (df[col] <= max_pop_af)
                before = len(df)
                df = df[pop_mask]
                if before != len(df):
                    print(f"  {col} filter (AF <= {max_pop_af}): {before} -> {len(df)}")

    # ACMG frequency criteria
    df["acmg_freq"] = "Unknown"
    df.loc[df[af_col] > 0.05, "acmg_freq"] = "BA1_standalone_benign"
    df.loc[(df[af_col] > 0.01) & (df[af_col] <= 0.05), "acmg_freq"] = "BS1_strong_benign"
    df.loc[(df[af_col] <= 0.01) & df[af_col].notna(), "acmg_freq"] = "PM2_supporting_pathogenic"
    df.loc[df[af_col].isna(), "acmg_freq"] = "PM2_absent_pathogenic"

    print(f"\nACMG frequency criteria:")
    print(df["acmg_freq"].value_counts())

    return df

# Usage
pop_cols = ["gnomAD_AFR", "gnomAD_AMR", "gnomAD_ASJ", "gnomAD_EAS",
            "gnomAD_FIN", "gnomAD_NFE", "gnomAD_SAS"]
rare_variants = gnomad_frequency_filter(variants, max_af=0.01, pop_af_cols=pop_cols)
```

**Key parameters:**
- `max_af=0.01`: standard rare disease threshold. Use 0.001 for dominant diseases.
- `max_pop_af=0.03`: prevents filtering variants common in underrepresented populations.
- BA1 (AF > 5%): standalone benign evidence. BS1 (AF > 1%): strong benign. PM2 (absent): supporting pathogenic.

**Expected output:** Filtered DataFrame with ACMG frequency classification.

---

## 10. LOFTEE: Loss-of-Function Variant Annotation

Parse LOFTEE (Loss-Of-Function Transcript Effect Estimator) annotations from VEP output.

```python
import pandas as pd
import re

def parse_loftee(vcf_path):
    """Parse LOFTEE annotations from VEP-annotated VCF.

    LOFTEE fields in CSQ: LoF, LoF_filter, LoF_flags, LoF_info
    LoF values: HC (high confidence), LC (low confidence), or empty (not LoF)

    Parameters:
        vcf_path: path to VEP+LOFTEE annotated VCF
    Returns:
        DataFrame with LoF variant classifications
    """
    import gzip
    opener = gzip.open if vcf_path.endswith(".gz") else open

    csq_fields = None
    records = []
    with opener(vcf_path, "rt") as f:
        for line in f:
            if line.startswith("##INFO=<ID=CSQ"):
                match = re.search(r'Format: (.+)"', line)
                if match:
                    csq_fields = match.group(1).split("|")
            if line.startswith("#"):
                continue
            if csq_fields is None:
                continue

            fields = line.strip().split("\t")
            info = fields[7]
            csq_match = re.search(r'CSQ=([^;]+)', info)
            if not csq_match:
                continue

            for csq_entry in csq_match.group(1).split(","):
                vals = csq_entry.split("|")
                csq_dict = {csq_fields[i]: vals[i] if i < len(vals) else ""
                           for i in range(len(csq_fields))}

                lof = csq_dict.get("LoF", "")
                if lof in ("HC", "LC"):
                    records.append({
                        "CHROM": fields[0], "POS": int(fields[1]),
                        "REF": fields[3], "ALT": fields[4],
                        "gene": csq_dict.get("SYMBOL", ""),
                        "consequence": csq_dict.get("Consequence", ""),
                        "LoF": lof,
                        "LoF_filter": csq_dict.get("LoF_filter", ""),
                        "LoF_flags": csq_dict.get("LoF_flags", ""),
                    })

    df = pd.DataFrame(records)
    print(f"LoF variants: {len(df)}")
    print(f"  High confidence (HC): {(df['LoF'] == 'HC').sum()}")
    print(f"  Low confidence (LC): {(df['LoF'] == 'LC').sum()}")

    if len(df) > 0 and "LoF_filter" in df.columns:
        # Common LOFTEE filters
        filters = df["LoF_filter"].str.split(",").explode().value_counts()
        print(f"\nLOFTEE filters applied:\n{filters.head(10)}")

    return df

# Common LOFTEE filter reasons:
# END_TRUNC: variant in last 5% of transcript
# PHYLOCSF_WEAK/UNLIKELY: weak evolutionary conservation
# NON_CAN_SPLICE: non-canonical splice site
# SINGLE_EXON: gene with only one exon
# ANC_ALLELE: ancestral allele is the alternative allele

# Usage
lof_variants = parse_loftee("vep_loftee_output.vcf")
hc_lof = lof_variants[lof_variants["LoF"] == "HC"]
print(f"\nHigh-confidence LoF genes: {hc_lof['gene'].nunique()}")
```

**Key parameters:**
- HC (High Confidence): passes all LOFTEE filters. Use for clinical analyses.
- LC (Low Confidence): flagged by one or more filters. Review manually.
- Common flags: END_TRUNC (last exon, may escape NMD), PHYLOCSF_WEAK (poor conservation).

**Expected output:** DataFrame with LoF confidence class, filter reasons, and flags per variant.

---

## 11. VCF to pandas DataFrame Parsing for Downstream Analysis

Comprehensive VCF parser that extracts all relevant fields into a flat DataFrame.

```python
import pandas as pd
import numpy as np
import gzip
import re

def vcf_to_dataframe(vcf_path, info_fields=None, format_fields=None):
    """Parse VCF into a flat pandas DataFrame with INFO and FORMAT fields extracted.

    Parameters:
        vcf_path: path to VCF (plain or gzipped)
        info_fields: list of INFO keys to extract (None = auto-detect common fields)
        format_fields: list of FORMAT keys to extract (None = GT, DP, GQ, AD)
    Returns:
        DataFrame with one row per variant, columns for fixed fields, INFO, and per-sample FORMAT
    """
    opener = gzip.open if vcf_path.endswith(".gz") else open

    if info_fields is None:
        info_fields = ["DP", "AF", "AC", "AN", "MQ", "QD", "FS", "SOR", "MQRankSum",
                       "ReadPosRankSum", "VQSLOD"]
    if format_fields is None:
        format_fields = ["GT", "DP", "GQ", "AD"]

    header_lines = []
    col_names = None
    records = []

    with opener(vcf_path, "rt") as f:
        for line in f:
            if line.startswith("##"):
                header_lines.append(line.strip())
                continue
            if line.startswith("#CHROM"):
                col_names = line.strip().lstrip("#").split("\t")
                sample_cols = col_names[9:] if len(col_names) > 9 else []
                continue

            fields = line.strip().split("\t")
            rec = {
                "CHROM": fields[0], "POS": int(fields[1]), "ID": fields[2],
                "REF": fields[3], "ALT": fields[4],
                "QUAL": float(fields[5]) if fields[5] != "." else np.nan,
                "FILTER": fields[6],
            }

            # Parse INFO
            info_dict = {}
            for item in fields[7].split(";"):
                if "=" in item:
                    k, v = item.split("=", 1)
                    info_dict[k] = v
                else:
                    info_dict[item] = True

            for key in info_fields:
                val = info_dict.get(key)
                if val is True:
                    rec[f"INFO_{key}"] = True
                elif val is not None:
                    try:
                        rec[f"INFO_{key}"] = float(val.split(",")[0])
                    except (ValueError, AttributeError):
                        rec[f"INFO_{key}"] = val
                else:
                    rec[f"INFO_{key}"] = np.nan

            # Parse FORMAT fields per sample
            if len(fields) > 8:
                fmt_keys = fields[8].split(":")
                for sample_idx, sample_name in enumerate(sample_cols):
                    if 9 + sample_idx >= len(fields):
                        continue
                    sample_vals = fields[9 + sample_idx].split(":")
                    for fmt_key in format_fields:
                        if fmt_key in fmt_keys:
                            idx = fmt_keys.index(fmt_key)
                            val = sample_vals[idx] if idx < len(sample_vals) else "."
                            col_name = f"{sample_name}_{fmt_key}"
                            if fmt_key == "GT":
                                rec[col_name] = val
                            elif fmt_key == "AD":
                                rec[col_name] = val  # keep as string "ref,alt"
                            else:
                                try:
                                    rec[col_name] = float(val) if val != "." else np.nan
                                except ValueError:
                                    rec[col_name] = val

            records.append(rec)

    df = pd.DataFrame(records)
    print(f"Parsed {len(df)} variants, {len(sample_cols)} samples")
    print(f"Chromosomes: {df['CHROM'].nunique()}")
    print(f"FILTER: {df['FILTER'].value_counts().head()}")

    return df

# Usage
df = vcf_to_dataframe("cohort.vcf.gz",
                       info_fields=["DP", "AF", "AC", "AN", "MQ", "VQSLOD"],
                       format_fields=["GT", "DP", "GQ", "AD"])
```

**Expected output:** Flat DataFrame with fixed VCF columns, INFO fields as `INFO_*` columns, and per-sample FORMAT fields as `{sample}_{field}` columns.

---

## 12. Multi-Sample VCF Annotation and Filtering Pipeline

End-to-end pipeline combining annotation, filtering, and prioritization for a multi-sample cohort.

```python
import pandas as pd
import numpy as np
from statsmodels.stats.multitest import multipletests

def annotation_pipeline(vcf_path, af_threshold=0.01, cadd_threshold=15,
                        impact_filter=("HIGH", "MODERATE")):
    """Complete annotation and filtering pipeline for multi-sample VCF.

    Parameters:
        vcf_path: path to annotated VCF (VEP or SnpEff)
        af_threshold: maximum gnomAD allele frequency
        cadd_threshold: minimum CADD PHRED score
        impact_filter: tuple of impact levels to retain
    Returns:
        dict with filtered variants, gene summary, and pipeline stats
    """
    # Step 1: Parse VCF
    df = vcf_to_dataframe(vcf_path)
    stats = {"total_variants": len(df)}

    # Step 2: PASS filter
    df_pass = df[df["FILTER"].isin(["PASS", "."])]
    stats["pass_filter"] = len(df_pass)

    # Step 3: Quality filter
    df_qc = df_pass[
        (df_pass["QUAL"] >= 30) &
        (df_pass["INFO_DP"].fillna(0) >= 10)
    ]
    stats["quality_filter"] = len(df_qc)

    # Step 4: Frequency filter (if gnomAD AF available)
    if "INFO_AF" in df_qc.columns:
        df_rare = df_qc[df_qc["INFO_AF"].fillna(0) <= af_threshold]
    else:
        df_rare = df_qc
    stats["frequency_filter"] = len(df_rare)

    # Step 5: Impact filter (requires annotation)
    if "impact" in df_rare.columns:
        df_impact = df_rare[df_rare["impact"].isin(impact_filter)]
    else:
        df_impact = df_rare
    stats["impact_filter"] = len(df_impact)

    # Step 6: Prediction score filter
    if "CADD_PHRED" in df_impact.columns:
        has_cadd = df_impact["CADD_PHRED"].notna()
        df_scored = df_impact[~has_cadd | (df_impact["CADD_PHRED"] >= cadd_threshold)]
    else:
        df_scored = df_impact
    stats["score_filter"] = len(df_scored)

    # Gene-level summary
    if "gene" in df_scored.columns:
        gene_summary = df_scored.groupby("gene").agg(
            n_variants=("POS", "count"),
            max_cadd=("CADD_PHRED", "max") if "CADD_PHRED" in df_scored.columns else ("POS", "count"),
            impacts=("impact", lambda x: ",".join(x.unique())) if "impact" in df_scored.columns else ("POS", "count"),
        ).sort_values("n_variants", ascending=False)
    else:
        gene_summary = pd.DataFrame()

    # Print pipeline summary
    print("\nAnnotation Pipeline Summary:")
    print(f"  Total variants:     {stats['total_variants']:,}")
    print(f"  After PASS filter:  {stats['pass_filter']:,}")
    print(f"  After quality QC:   {stats['quality_filter']:,}")
    print(f"  After freq filter:  {stats['frequency_filter']:,}")
    print(f"  After impact:       {stats['impact_filter']:,}")
    print(f"  After scores:       {stats['score_filter']:,}")

    return {
        "variants": df_scored,
        "gene_summary": gene_summary,
        "stats": stats,
    }

# Usage
results = annotation_pipeline("vep_annotated.vcf.gz", af_threshold=0.01)
results["variants"].to_csv("prioritized_variants.tsv", sep="\t", index=False)
results["gene_summary"].to_csv("gene_variant_summary.tsv", sep="\t")
```

**Key parameters:**
- Pipeline order matters: PASS > Quality > Frequency > Impact > Scores.
- `af_threshold=0.01`: for rare disease. Use 0.05 for common variant studies.
- `cadd_threshold=15`: permissive. Use 20 for stringent filtering.

**Expected output:** Filtered variant list, gene-level summary, and pipeline statistics showing variant counts at each stage.

---

## Quick Reference

| Task | Recipe | Key tool/function |
|------|--------|------------------|
| VEP annotation | #1 | `vep --cache --everything` |
| SnpEff annotation | #2 | `snpEff ann` |
| ANNOVAR multi-DB | #3 | `table_annovar.pl` |
| bcftools custom annotation | #4 | `bcftools annotate` |
| CADD scores | #5 | PHRED >= 20 threshold |
| SpliceAI | #6 | DS >= 0.5 / 0.8 thresholds |
| REVEL scores | #7 | Score >= 0.5 / 0.773 |
| ClinVar | #8 | VEP ClinVar plugin |
| gnomAD filtering | #9 | AF <= 0.01 + pop-specific |
| LOFTEE LoF | #10 | HC/LC classification |
| VCF parsing | #11 | `vcf_to_dataframe()` |
| Full pipeline | #12 | `annotation_pipeline()` |

---

## Cross-Skill Routing

- Upstream variant calling and QC --> `variant-analysis` (recipes.md)
- ACMG clinical classification --> `variant-interpretation`
- Cancer somatic interpretation --> `cancer-variant-interpreter`
- Structural variant annotation --> `structural-variant-analysis`
- GWAS variant context --> `gwas-snp-interpretation`
