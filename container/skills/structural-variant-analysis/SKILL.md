---
name: structural-variant-analysis
description: Structural variant and copy number variation analysis. CNV detection, SV calling, fusion genes, breakpoint analysis, cytogenetic interpretation, chromosomal rearrangements, deletions, duplications, inversions, translocations, copy number arrays. Use when user mentions structural variant, CNV, copy number variation, fusion gene, translocation, deletion, duplication, inversion, breakpoint, chromosomal rearrangement, cytogenetics, array CGH, SNP array copy number, or SV calling.
---

# Structural Variant Analysis

Structural variant and copy number variation analysis methodology. The agent writes and executes Python code for CNV detection, SV calling, fusion gene identification, breakpoint analysis, cytogenetic interpretation, and copy number analysis from arrays and sequencing.

## Report-First Workflow

1. **Create report file immediately**: `[sample]_structural_variant_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill
- Germline SNV/indel interpretation and ACMG classification → use `variant-interpretation`
- Somatic cancer variant tiering and molecular tumor board → use `cancer-variant-interpreter`
- GWAS SNP annotation and locus-to-gene mapping → use `gwas-snp-interpretation`
- Clinical variant pathogenicity scoring → use `variant-analysis`
- Protein structure impact of variants → use `protein-structure-retrieval`

## Cross-Reference: Other Skills

- **Germline variant interpretation and ACMG classification** -> use variant-interpretation skill
- **Somatic cancer variant interpretation and molecular tumor board** -> use cancer-variant-interpreter skill
- **GWAS SNP annotation and locus-to-gene mapping** -> use gwas-snp-interpretation skill
- **Clinical variant interpretation with pathogenicity scoring** -> use variant-analysis skill

## Available MCP Tools

### `mcp__ensembl__ensembl_data` (Genomic Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `lookup_gene` | Get gene info by ID or symbol | `gene_id`, `species`, `expand` |
| `search_genes` | Search genes by name/description | `query`, `species`, `biotype`, `limit` |
| `get_regulatory_features` | Get regulatory elements in region | `region`, `species`, `feature_type`, `cell_type` |
| `get_sequence` | Get genomic/transcript sequence | `region`, `species`, `format`, `mask` |
| `map_coordinates` | Map between assemblies | `region`, `species`, `target_assembly` |
| `get_xrefs` | Get cross-database references | `gene_id`, `external_db`, `all_levels` |

### `mcp__gnomad__gnomad_data` (gnomAD Population Genomics)

| Method | SV analysis use | Key parameters |
|--------|----------------|----------------|
| `get_structural_variants` | Query gnomAD SV catalog for a gene — distinguish rare from common SVs | `gene` |
| `get_gene_constraint` | Gene tolerance to loss-of-function (pLI/LOEUF for dosage sensitivity) | `gene` |

### `mcp__cosmic__cosmic_data` (COSMIC — Somatic Mutation Catalogue)

Use COSMIC for fusion gene and breakpoint annotation in cancer samples. Query known fusion partners, breakpoint positions, and recurrent structural rearrangements to determine whether detected SVs correspond to known oncogenic fusions with established clinical significance.

| Method | SV analysis use | Key parameters |
|--------|----------------|----------------|
| `search_by_gene` | Find fusion-associated mutations for a gene involved in a breakpoint | `gene`, `site`, `limit` |
| `get_mutation` | Look up a specific structural variant by COSMIC ID e.g. COSM476 | `mutation_id` |
| `search_by_site` | Find recurrent fusions/SVs by tissue site and histology | `site`, `histology`, `gene`, `limit` |
| `search_by_position` | Search breakpoint region by genomic coordinates e.g. 2:29446394-29446394 | `position`, `limit` |
| `search_by_mutation_cds` | Search by CDS-level rearrangement notation | `mutation`, `gene`, `limit` |
| `search_free_text` | General search for fusion names or structural rearrangement terms | `query`, `filter`, `limit` |
| `get_gene_mutation_profile` | Comprehensive gene profile including fusion prevalence and tissue distribution | `gene` |
| `get_file_download_url` | Get authenticated URL for COSMIC bulk data files (e.g., fusion export) | `filepath` |
| `list_fields` | List all searchable fields, common sites, and histologies |

## Python Environment

The container has Python 3 with `pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy`, `scikit-learn`. For genomic file parsing, use `pandas` to read VCF, BED, BEDPE, and segment files. The agent writes and executes all code directly via Bash.

---

## SV Types & Classification

| SV Type | Abbr | Definition | Detection |
|---------|------|------------|-----------|
| Deletion | DEL | Loss of a genomic segment (50 bp - arm) | Read depth drop, split reads, discordant pairs |
| Duplication | DUP | Gain of a segment, tandem or dispersed | Read depth increase, split reads |
| Inversion | INV | Reversal of segment orientation | Discordant pair orientation, split reads |
| Translocation | TRA/BND | Joining of segments from different chromosomes | Discordant pairs across chromosomes |
| Insertion | INS | Insertion of novel sequence (50 bp - kb) | Split reads, local assembly |
| Complex | CPX | Multi-breakpoint rearrangement | Combination of evidence types |

VCF SV INFO fields: `SVTYPE`, `END`, `SVLEN`, `CIPOS`, `CIEND`, `PE` (paired-end support), `SR` (split-read support). BND ALT notation encodes partner breakpoint: `N[chr:pos[`, `N]chr:pos]`, `[chr:pos[N`, `]chr:pos]N`.

---

## Analysis Pipeline

### Phase 1: SV Data Loading & QC

```python
import pandas as pd
import numpy as np
import re
from collections import Counter

def parse_sv_vcf(vcf_path):
    """Parse structural variant VCF file into a DataFrame."""
    records = []
    with open(vcf_path, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            fields = line.strip().split('\t')
            chrom, pos, sv_id, ref, alt, qual, filt = fields[0], int(fields[1]), fields[2], fields[3], fields[4], fields[5], fields[6]
            info_dict = {}
            for entry in fields[7].split(';'):
                if '=' in entry:
                    k, v = entry.split('=', 1)
                    info_dict[k] = v
            records.append({
                'chrom': chrom, 'pos': pos, 'id': sv_id, 'alt': alt,
                'qual': float(qual) if qual != '.' else 0, 'filter': filt,
                'svtype': info_dict.get('SVTYPE', 'UNK'),
                'end': int(info_dict.get('END', pos)),
                'svlen': abs(int(info_dict.get('SVLEN', 0))),
                'pe_support': int(info_dict.get('PE', 0)),
                'sr_support': int(info_dict.get('SR', 0)),
            })
    df = pd.DataFrame(records)
    print(f"Loaded {len(df)} SV records from {vcf_path}")
    return df

def parse_cnv_segments(seg_path):
    """Parse CNV segment file (SEG format from CBS/GATK/CNVkit)."""
    df = pd.read_csv(seg_path, sep='\t', comment='#')
    col_map = {}
    for col in df.columns:
        cl = col.lower()
        if 'chrom' in cl or cl == 'chr': col_map[col] = 'chrom'
        elif cl in ('start', 'loc.start', 'begin'): col_map[col] = 'start'
        elif cl in ('end', 'loc.end', 'stop'): col_map[col] = 'end'
        elif 'log2' in cl or 'seg.mean' in cl.replace('_', '.'): col_map[col] = 'log2_ratio'
    df = df.rename(columns=col_map)
    print(f"Loaded {len(df)} CNV segments from {seg_path}")
    return df

def sv_qc_summary(sv_df):
    """Generate QC summary for SV calls."""
    print(f"Total SVs: {len(sv_df)}")
    print(f"\nSV type distribution:\n{sv_df['svtype'].value_counts().to_string()}")
    sized = sv_df[sv_df['svlen'] > 0]['svlen']
    if len(sized) > 0:
        print(f"\nSize (bp): median={sized.median():,.0f}, mean={sized.mean():,.0f}, range={sized.min():,.0f}-{sized.max():,.0f}")
    passing = sv_df[sv_df['filter'] == 'PASS']
    print(f"PASS filter: {len(passing)} / {len(sv_df)} ({100*len(passing)/max(len(sv_df),1):.1f}%)")
```

### Phase 2: SV Filtering & Quality Assessment

```python
def filter_sv_calls(sv_df, min_qual=20, min_total_support=3,
                    min_size=50, max_size=None, svtypes=None, pass_only=True):
    """Filter SV calls by quality metrics."""
    df = sv_df.copy()
    n_start = len(df)
    if pass_only:
        df = df[df['filter'] == 'PASS']
    if min_qual > 0:
        df = df[df['qual'] >= min_qual]
    if svtypes:
        df = df[df['svtype'].isin(svtypes)]
    df['total_support'] = df['pe_support'] + df['sr_support']
    df = df[df['total_support'] >= min_total_support]
    sized_mask = ~df['svtype'].isin(['BND', 'TRA'])
    if min_size > 0:
        df = df[~sized_mask | (df['svlen'] >= min_size)]
    if max_size is not None:
        df = df[~sized_mask | (df['svlen'] <= max_size)]
    print(f"Filtering: {n_start} -> {len(df)} SVs ({n_start - len(df)} removed)")
    return df

def assess_sv_quality_tiers(sv_df):
    """Assign quality tiers based on evidence strength."""
    df = sv_df.copy()
    df['total_support'] = df['pe_support'] + df['sr_support']
    conditions = [
        (df['total_support'] >= 10) & (df['sr_support'] >= 3) & (df['pe_support'] >= 3),
        (df['total_support'] >= 5) & ((df['sr_support'] >= 1) | (df['pe_support'] >= 2)),
        (df['total_support'] >= 3),
    ]
    df['quality_tier'] = np.select(conditions, ['HIGH', 'MEDIUM', 'LOW'], default='VERY_LOW')
    print(f"Quality tiers:\n{df['quality_tier'].value_counts().to_string()}")
    return df
```

### Phase 3: CNV Analysis

Log2 ratio thresholds: gain > 0.3 (~2.5 copies), loss < -0.3 (~1.5 copies), amplification > 1.0 (~4 copies), homozygous deletion < -1.0 (~0.5 copies).

```python
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def analyze_cnv_segments(seg_df, gain_thr=0.3, loss_thr=-0.3, amp_thr=1.0, homdel_thr=-1.0):
    """Classify CNV segments by copy number state."""
    df = seg_df.copy()
    conditions = [df['log2_ratio'] > amp_thr, df['log2_ratio'] > gain_thr,
                  df['log2_ratio'] < homdel_thr, df['log2_ratio'] < loss_thr]
    choices = ['AMPLIFICATION', 'GAIN', 'HOMOZYGOUS_DELETION', 'LOSS']
    df['cnv_state'] = np.select(conditions, choices, default='NEUTRAL')
    df['approx_copies'] = np.round(2 * (2 ** df['log2_ratio'])).astype(int).clip(0, 20)
    df['segment_size'] = df['end'] - df['start']
    for state in ['AMPLIFICATION', 'GAIN', 'NEUTRAL', 'LOSS', 'HOMOZYGOUS_DELETION']:
        sub = df[df['cnv_state'] == state]
        print(f"  {state:25s}: {len(sub):5d} segments, {sub['segment_size'].sum()/1e6:10.2f} Mb")
    return df

def plot_genome_cnv(seg_df, output_path='cnv_genome_plot.png', title='Genome-wide CNV Profile'):
    """Generate genome-wide CNV plot with chromosomes on x-axis."""
    chrom_order = [f'chr{i}' for i in range(1, 23)] + ['chrX', 'chrY']
    chrom_sizes = {'chr1': 248956422, 'chr2': 242193529, 'chr3': 198295559, 'chr4': 190214555,
        'chr5': 181538259, 'chr6': 170805979, 'chr7': 159345973, 'chr8': 145138636,
        'chr9': 138394717, 'chr10': 133797422, 'chr11': 135086622, 'chr12': 133275309,
        'chr13': 114364328, 'chr14': 107043718, 'chr15': 101991189, 'chr16': 90338345,
        'chr17': 83257441, 'chr18': 80373285, 'chr19': 58617616, 'chr20': 64444167,
        'chr21': 46709983, 'chr22': 50818468, 'chrX': 156040895, 'chrY': 57227415}
    offsets, cumulative = {}, 0
    for c in chrom_order:
        offsets[c] = cumulative
        cumulative += chrom_sizes.get(c, 0)
    df = seg_df.copy()
    df['chrom_norm'] = df['chrom'].apply(lambda x: x if x.startswith('chr') else f'chr{x}')
    df = df[df['chrom_norm'].isin(chrom_order)]
    df['plot_start'] = df.apply(lambda r: offsets.get(r['chrom_norm'], 0) + r['start'], axis=1)
    df['plot_end'] = df.apply(lambda r: offsets.get(r['chrom_norm'], 0) + r['end'], axis=1)
    fig, ax = plt.subplots(figsize=(18, 5))
    colors = {'AMPLIFICATION': 'darkred', 'GAIN': 'red', 'NEUTRAL': 'gray',
              'LOSS': 'blue', 'HOMOZYGOUS_DELETION': 'darkblue'}
    for _, row in df.iterrows():
        ax.plot([row['plot_start'], row['plot_end']], [row['log2_ratio'], row['log2_ratio']],
                color=colors.get(row.get('cnv_state', 'NEUTRAL'), 'gray'), linewidth=1.5, alpha=0.8)
    for c in chrom_order:
        ax.axvline(offsets[c], color='lightgray', linewidth=0.5, alpha=0.5)
    ax.set_xticks([offsets[c] + chrom_sizes.get(c, 0) / 2 for c in chrom_order])
    ax.set_xticklabels([c.replace('chr', '') for c in chrom_order], fontsize=8)
    ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
    ax.set_ylabel('Log2 Ratio'); ax.set_title(title); ax.set_ylim(-3, 3)
    plt.tight_layout(); plt.savefig(output_path, dpi=150); plt.close()
    print(f"Saved to {output_path}")
```

### Phase 4: Gene Impact Assessment

Query Ensembl for gene overlap and regulatory context at breakpoint regions:

```
1. mcp__ensembl__ensembl_data(method: "search_genes", query: "tumor suppressor", species: "homo_sapiens", limit: 50)
   -> Find genes in breakpoint region by functional description

2. mcp__ensembl__ensembl_data(method: "lookup_gene", gene_id: "GENE_SYMBOL", species: "homo_sapiens", expand: true)
   -> Confirm gene coordinates, exon boundaries for overlap calculation

3. mcp__ensembl__ensembl_data(method: "get_regulatory_features", region: "17:7661779-7687550", species: "homo_sapiens")
   -> Regulatory elements (enhancers, promoters) disrupted by SV breakpoints
```

```python
def find_overlapping_genes(sv_df, gene_df, min_overlap_fraction=0.0):
    """Find genes overlapping with SVs using interval intersection."""
    results = []
    for _, sv in sv_df.iterrows():
        sv_start = sv.get('pos', sv.get('start', 0))
        mask = (gene_df['chrom'] == sv['chrom']) & (gene_df['start'] < sv['end']) & (gene_df['end'] > sv_start)
        for _, gene in gene_df[mask].iterrows():
            overlap_bp = min(sv['end'], gene['end']) - max(sv_start, gene['start'])
            gene_size = gene['end'] - gene['start']
            frac = overlap_bp / gene_size if gene_size > 0 else 0
            if frac >= min_overlap_fraction:
                results.append({
                    'sv_id': sv.get('id', 'NA'), 'svtype': sv['svtype'],
                    'gene': gene['gene'], 'overlap_bp': overlap_bp,
                    'gene_overlap_fraction': round(frac, 4),
                    'impact': classify_gene_impact(sv['svtype'], frac)
                })
    return pd.DataFrame(results)

def classify_gene_impact(svtype, overlap_fraction):
    """Classify impact of an SV on a gene."""
    if svtype == 'DEL':
        return 'WHOLE_GENE_DELETION' if overlap_fraction >= 0.99 else 'PARTIAL_GENE_DELETION' if overlap_fraction >= 0.5 else 'EXON_LEVEL_DELETION'
    elif svtype == 'DUP':
        return 'WHOLE_GENE_DUPLICATION' if overlap_fraction >= 0.99 else 'PARTIAL_GENE_DUPLICATION' if overlap_fraction >= 0.5 else 'INTRAGENIC_DUPLICATION'
    elif svtype == 'INV':
        return 'WHOLE_GENE_INVERSION' if overlap_fraction >= 0.99 else 'DISRUPTION_BY_INVERSION'
    elif svtype in ('BND', 'TRA'):
        return 'DISRUPTION_BY_TRANSLOCATION'
    return 'UNKNOWN_IMPACT'

# ClinGen dosage sensitivity (score 3 = sufficient evidence, 2 = emerging)
HAPLOINSUFFICIENT_GENES = {
    'TP53': 3, 'BRCA1': 3, 'BRCA2': 3, 'RB1': 3, 'APC': 3, 'PTEN': 3,
    'NF1': 3, 'NF2': 3, 'WT1': 3, 'CDKN2A': 3, 'STK11': 3, 'VHL': 3,
    'MLH1': 3, 'MSH2': 3, 'MSH6': 3, 'PMS2': 2, 'CDH1': 3, 'PALB2': 3,
    'ATM': 2, 'CHEK2': 2, 'SMAD4': 3, 'BMPR1A': 3, 'MEN1': 3, 'RET': 3,
}
TRIPLOSENSITIVE_GENES = {
    'MYC': 3, 'ERBB2': 3, 'EGFR': 3, 'MDM2': 3, 'CDK4': 3, 'CCND1': 3,
    'MET': 3, 'FGFR1': 2, 'FGFR2': 2, 'KRAS': 2, 'PIK3CA': 2, 'ALK': 2,
}

def annotate_dosage_sensitivity(gene_impact_df):
    """Annotate gene-SV overlaps with dosage sensitivity scores."""
    df = gene_impact_df.copy()
    df['hi_score'] = df['gene'].map(HAPLOINSUFFICIENT_GENES).fillna(0).astype(int)
    df['ts_score'] = df['gene'].map(TRIPLOSENSITIVE_GENES).fillna(0).astype(int)
    df['clinically_significant'] = (
        ((df['svtype'] == 'DEL') & (df['hi_score'] >= 2)) |
        ((df['svtype'] == 'DUP') & (df['ts_score'] >= 2)) |
        df['impact'].str.contains('DISRUPTION')
    )
    sig = df[df['clinically_significant']]
    if len(sig) > 0:
        print(f"Clinically significant: {len(sig)} hits")
        print(sig[['gene', 'svtype', 'impact', 'hi_score', 'ts_score']].to_string(index=False))
    return df
```

### Phase 5: Fusion Gene Detection

```python
KNOWN_ONCOGENIC_FUSIONS = {
    'BCR--ABL1': {'disease': 'CML/ALL', 'therapy': 'Imatinib/Dasatinib/Nilotinib', 'tier': 'I'},
    'EML4--ALK': {'disease': 'NSCLC', 'therapy': 'Crizotinib/Alectinib/Lorlatinib', 'tier': 'I'},
    'TMPRSS2--ERG': {'disease': 'Prostate', 'therapy': 'Diagnostic marker', 'tier': 'II'},
    'PML--RARA': {'disease': 'APL', 'therapy': 'ATRA/Arsenic trioxide', 'tier': 'I'},
    'EWSR1--FLI1': {'disease': 'Ewing sarcoma', 'therapy': 'Diagnostic', 'tier': 'I'},
    'SS18--SSX1': {'disease': 'Synovial sarcoma', 'therapy': 'Diagnostic', 'tier': 'I'},
    'RUNX1--RUNX1T1': {'disease': 'AML', 'therapy': 'Favorable prognosis', 'tier': 'I'},
    'CBFB--MYH11': {'disease': 'AML', 'therapy': 'Favorable prognosis', 'tier': 'I'},
    'ETV6--NTRK3': {'disease': 'Multiple', 'therapy': 'Larotrectinib/Entrectinib', 'tier': 'I'},
    'FGFR3--TACC3': {'disease': 'GBM/Bladder', 'therapy': 'Erdafitinib', 'tier': 'II'},
    'ROS1--CD74': {'disease': 'NSCLC', 'therapy': 'Crizotinib/Entrectinib', 'tier': 'I'},
    'RET--KIF5B': {'disease': 'NSCLC/Thyroid', 'therapy': 'Selpercatinib/Pralsetinib', 'tier': 'I'},
    'PAX3--FOXO1': {'disease': 'Alveolar RMS', 'therapy': 'Diagnostic/Prognostic', 'tier': 'I'},
    'DNAJB1--PRKACA': {'disease': 'Fibrolamellar HCC', 'therapy': 'Diagnostic', 'tier': 'I'},
}

def detect_fusion_genes(sv_df, gene_df):
    """Detect potential fusion genes from BND/TRA breakpoints in two genes."""
    fusions = []
    bp_window = 1000
    for _, sv in sv_df.iterrows():
        if sv['svtype'] != 'BND':
            continue
        match = re.search(r'[\[\]]([^:\[\]]+):(\d+)[\[\]]', sv.get('alt', ''))
        if not match:
            continue
        chrom2, pos2 = match.group(1), int(match.group(2))
        genes1 = gene_df[(gene_df['chrom'] == sv['chrom']) &
                         (gene_df['start'] <= sv['pos'] + bp_window) &
                         (gene_df['end'] >= sv['pos'] - bp_window)]
        genes2 = gene_df[(gene_df['chrom'] == chrom2) &
                         (gene_df['start'] <= pos2 + bp_window) &
                         (gene_df['end'] >= pos2 - bp_window)]
        for _, g1 in genes1.iterrows():
            for _, g2 in genes2.iterrows():
                if g1['gene'] != g2['gene']:
                    name = f"{g1['gene']}--{g2['gene']}"
                    fusions.append({'fusion_name': name, 'gene_5prime': g1['gene'],
                        'gene_3prime': g2['gene'], 'chrom1': sv['chrom'], 'pos1': sv['pos'],
                        'chrom2': chrom2, 'pos2': pos2, 'sv_id': sv.get('id', 'NA')})
    fusion_df = pd.DataFrame(fusions)
    if len(fusion_df) > 0:
        print(f"Detected {fusion_df['fusion_name'].nunique()} unique fusion candidates")
    return fusion_df

def annotate_known_fusions(fusion_df):
    """Annotate fusions against known oncogenic fusion database."""
    df = fusion_df.copy()
    def lookup(row):
        for name in [f"{row['gene_5prime']}--{row['gene_3prime']}", f"{row['gene_3prime']}--{row['gene_5prime']}"]:
            if name in KNOWN_ONCOGENIC_FUSIONS:
                return KNOWN_ONCOGENIC_FUSIONS[name]
        return None
    info = df.apply(lookup, axis=1)
    df['known_oncogenic'] = info.apply(lambda x: x is not None)
    df['associated_disease'] = info.apply(lambda x: x['disease'] if x else 'Unknown')
    df['therapeutic_option'] = info.apply(lambda x: x['therapy'] if x else 'None known')
    df['evidence_tier'] = info.apply(lambda x: x['tier'] if x else 'NA')
    for _, row in df[df['known_oncogenic']].iterrows():
        print(f"  *** {row['fusion_name']}: {row['associated_disease']} -> {row['therapeutic_option']} (Tier {row['evidence_tier']})")
    return df
```

### gnomAD SV Cross-Reference

Cross-reference structural variants with the gnomAD SV catalog to distinguish rare from common SVs:

```
1. Query gnomAD SV catalog for SVs overlapping a gene of interest:
   mcp__gnomad__gnomad_data(method: "get_structural_variants", gene: "GENE_SYMBOL")
   → Returns known SVs (DEL, DUP, INV, etc.) with population frequencies

2. Compare patient SVs against gnomAD catalog:
   - If patient SV matches a common gnomAD SV (AF > 1%) → likely benign
   - If patient SV is absent from gnomAD → rare, prioritize for clinical review

3. Assess gene constraint for dosage sensitivity interpretation:
   mcp__gnomad__gnomad_data(method: "get_gene_constraint", gene: "GENE_SYMBOL")
   → pLI/LOEUF scores inform whether deletions in this gene are tolerated
```

### Phase 6: Population SV Frequency

```python
def reciprocal_overlap(start1, end1, start2, end2, threshold=0.5):
    """Check if two intervals have reciprocal overlap >= threshold."""
    overlap = min(end1, end2) - max(start1, start2)
    if overlap <= 0:
        return 0.0, False
    ro = min(overlap / (end1 - start1), overlap / (end2 - start2))
    return ro, ro >= threshold

def annotate_sv_frequency(sv_df, pop_sv_df, ro_threshold=0.5):
    """Annotate SVs with population frequency using reciprocal overlap matching."""
    results = []
    for _, sv in sv_df.iterrows():
        sv_start = sv.get('pos', sv.get('start', 0))
        candidates = pop_sv_df[(pop_sv_df['chrom'] == sv['chrom']) & (pop_sv_df['svtype'] == sv['svtype']) &
                               (pop_sv_df['start'] < sv['end'] + 1000) & (pop_sv_df['end'] > sv_start - 1000)]
        best_af, best_ro = 0.0, 0.0
        for _, pop in candidates.iterrows():
            ro, passes = reciprocal_overlap(sv_start, sv['end'], pop['start'], pop['end'], ro_threshold)
            if passes and ro > best_ro:
                best_ro, best_af = ro, pop['af']
        results.append({'sv_id': sv.get('id', 'NA'), 'pop_frequency': best_af,
                        'reciprocal_overlap': round(best_ro, 4), 'is_rare': best_af < 0.01})
    result_df = pd.DataFrame(results)
    print(f"Rare (AF < 1%): {result_df['is_rare'].sum()}, Common: {(~result_df['is_rare']).sum()}")
    return result_df
```

### Phase 7: Clinical Interpretation

ACMG/ClinGen SV interpretation framework. Scoring: >= 0.99 Pathogenic, 0.90-0.98 Likely Pathogenic, -0.89 to 0.89 VUS, -0.90 to -0.89 Likely Benign, <= -0.90 Benign.

Evidence sections: (1) Genomic content (0 to 0.45), (2) Overlap with established regions (0 to 0.45), (3) Gene number evaluation (0 to 0.15), (4) Literature/database evidence (0 to 0.30), (5) Inheritance/segregation (0 to 0.15).

```python
def classify_sv_acmg_clingen(sv_record, gene_impacts, pop_freq, fusion_info=None):
    """Apply ACMG/ClinGen SV interpretation framework."""
    score, evidence = 0.0, []
    svtype = sv_record.get('svtype', 'UNK')
    pop_af = pop_freq.get('pop_frequency', 0.0)
    n_genes = len(gene_impacts)
    has_hi = any(g.get('hi_score', 0) >= 2 for g in gene_impacts) if gene_impacts else False
    has_ts = any(g.get('ts_score', 0) >= 2 for g in gene_impacts) if gene_impacts else False

    # Section 1: Genomic content
    if svtype == 'DEL' and has_hi:
        score += 0.45; evidence.append('1A: HI gene deleted (0.45)')
    elif svtype == 'DUP' and has_ts:
        score += 0.45; evidence.append('1A: TS gene duplicated (0.45)')
    elif n_genes >= 35:
        score += 0.30; evidence.append(f'1B: {n_genes} genes (0.30)')
    elif n_genes == 0:
        score -= 0.30; evidence.append('1C: No protein-coding genes (-0.30)')

    # Section 2: Established regions / fusions
    if fusion_info and any(f.get('known_oncogenic', False) for f in fusion_info):
        score += 0.45; evidence.append('2A: Known oncogenic fusion (0.45)')

    # Section 3: Gene number
    if n_genes >= 3:
        score += 0.10; evidence.append(f'3: {n_genes} genes (0.10)')
    elif n_genes >= 1:
        score += 0.05; evidence.append(f'3: {n_genes} gene(s) (0.05)')

    # Section 4: Population frequency
    if pop_af > 0.01:
        score -= 0.45; evidence.append(f'4: Common AF={pop_af:.4f} (-0.45)')
    elif pop_af == 0:
        score += 0.10; evidence.append('4: Absent from databases (0.10)')

    classification = ('PATHOGENIC' if score >= 0.99 else 'LIKELY_PATHOGENIC' if score >= 0.90 else
                      'BENIGN' if score <= -0.90 else 'LIKELY_BENIGN' if score <= -0.89 else 'VUS')
    return {'classification': classification, 'score': round(score, 3), 'evidence': evidence,
            'n_genes_affected': n_genes, 'svtype': svtype}

def generate_sv_report(classifications, output_path='sv_report.txt'):
    """Generate text report summarizing SV analysis results."""
    class_counts = Counter(c['classification'] for c in classifications)
    with open(output_path, 'w') as f:
        f.write("STRUCTURAL VARIANT ANALYSIS REPORT\n" + "=" * 60 + "\n")
        for cls in ['PATHOGENIC', 'LIKELY_PATHOGENIC', 'VUS', 'LIKELY_BENIGN', 'BENIGN']:
            f.write(f"  {cls:25s}: {class_counts.get(cls, 0)}\n")
        significant = [c for c in classifications if c['classification'] in ('PATHOGENIC', 'LIKELY_PATHOGENIC')]
        for c in significant:
            f.write(f"\n  {c['svtype']} | {c['classification']} (score: {c['score']})\n")
            for ev in c['evidence']:
                f.write(f"    - {ev}\n")
    print(f"Report written to {output_path}")
```

---

## Cytogenetic Nomenclature (ISCN)

```
Format: total chromosomes, sex chromosomes, abnormalities

  46,XX                             Normal female
  46,XY                             Normal male
  47,XX,+21                         Trisomy 21 (Down syndrome)
  45,X                              Monosomy X (Turner syndrome)
  46,XX,del(5)(q13q33)              Interstitial deletion on 5q
  46,XY,t(9;22)(q34;q11.2)         Philadelphia translocation (BCR-ABL1)
  46,XX,inv(16)(p13.1q22)           Pericentric inversion (CBFB-MYH11)
  46,XY,dup(1)(q21.1q21.2)         Duplication on 1q
  46,XX,i(17)(q10)                  Isochromosome 17q

Band notation: p = short arm, q = long arm. Numbered from centromere outward.
Sub-bands: p11.1, p11.2. Resolution: 300-band (low) to 850-band (high).
```

```python
def iscn_to_description(iscn_string):
    """Parse ISCN notation into human-readable descriptions."""
    parts = [p.strip() for p in iscn_string.split(',')]
    descriptions = [f"Total chromosomes: {parts[0]}", f"Sex: {parts[1] if len(parts) > 1 else ''}"]
    parsers = {'del': 'Deletion', 'dup': 'Duplication', 'inv': 'Inversion',
               't(': 'Translocation', 'der': 'Derivative', 'i(': 'Isochromosome'}
    for abn in parts[2:]:
        if abn.startswith('+'): descriptions.append(f"Trisomy: {abn[1:]}")
        elif abn.startswith('-'): descriptions.append(f"Monosomy: {abn[1:]}")
        else:
            label = next((v for k, v in parsers.items() if abn.startswith(k)), 'Abnormality')
            descriptions.append(f"{label}: {abn}")
    return descriptions
```

---

## Cancer-Specific SV Analysis

### Chromothripsis Detection

Hallmarks: (1) clustered breakpoints on one/few chromosomes, (2) oscillating copy number (typically 2 states), (3) random segment orientation, (4) retention of heterozygosity.

```python
def detect_chromothripsis(sv_df, seg_df, chrom, min_breakpoints=10, max_cn_states=3, window_mb=50):
    """Screen for chromothripsis on a given chromosome."""
    sv_chrom = sv_df[sv_df['chrom'] == chrom]
    if len(sv_chrom) < min_breakpoints:
        return {'chrom': chrom, 'chromothripsis': False, 'reason': 'Insufficient breakpoints'}
    breakpoints = sorted(sv_chrom['pos'].tolist() + sv_chrom['end'].tolist())
    window_bp = window_mb * 1e6
    best = {'count': 0, 'start': 0, 'end': 0}
    for bp in breakpoints:
        count = sum(1 for b in breakpoints if bp <= b <= bp + window_bp)
        if count > best['count']:
            best = {'count': count, 'start': bp, 'end': int(bp + window_bp)}
    if best['count'] < min_breakpoints:
        return {'chrom': chrom, 'chromothripsis': False, 'reason': 'No cluster'}
    region_segs = seg_df[(seg_df['chrom'] == chrom) & (seg_df['start'] < best['end']) & (seg_df['end'] > best['start'])]
    cn_states = region_segs['approx_copies'].nunique() if 'approx_copies' in region_segs.columns else 0
    return {'chrom': chrom, 'chromothripsis': best['count'] >= min_breakpoints and cn_states <= max_cn_states,
            'n_breakpoints': best['count'], 'cn_states': cn_states}

def find_focal_amplifications(seg_df, min_log2=1.5, max_size_mb=10):
    """Identify focal amplifications (oncogene amplification: ERBB2, MYC, EGFR)."""
    df = seg_df.copy()
    df['size_mb'] = (df['end'] - df['start']) / 1e6
    focal = df[(df['log2_ratio'] >= min_log2) & (df['size_mb'] <= max_size_mb)].sort_values('log2_ratio', ascending=False)
    for _, r in focal.head(20).iterrows():
        cn = round(2 * (2 ** r['log2_ratio']))
        print(f"  {r['chrom']}:{r['start']:,}-{r['end']:,} ({r['size_mb']:.2f} Mb) log2={r['log2_ratio']:.2f} (~{cn} copies)")
    return focal

def find_homozygous_deletions(seg_df, max_log2=-1.0, max_size_mb=20):
    """Identify homozygous deletions (tumor suppressor loss: TP53, RB1, CDKN2A, PTEN)."""
    df = seg_df.copy()
    df['size_mb'] = (df['end'] - df['start']) / 1e6
    homdel = df[(df['log2_ratio'] <= max_log2) & (df['size_mb'] <= max_size_mb)].sort_values('log2_ratio')
    for _, r in homdel.head(20).iterrows():
        cn = max(0, round(2 * (2 ** r['log2_ratio'])))
        print(f"  {r['chrom']}:{r['start']:,}-{r['end']:,} ({r['size_mb']:.2f} Mb) log2={r['log2_ratio']:.2f} (~{cn} copies)")
    return homdel
```

---

## Evidence Grading & Multi-Agent Examples

### Evidence Grading (T1-T4)

| Grade | Type | Description |
|-------|------|-------------|
| **T1** | Human/Clinical | ClinGen pathogenic CNV, ISCN from clinical cytogenetics, FDA-recognized SV biomarker |
| **T2** | Functional | FISH confirmation, RNA-seq fusion transcript, protein expression loss by IHC |
| **T3** | Association | Absent from DGV/gnomAD-SV, enriched in cohort, segregation with phenotype |
| **T4** | Computational | Breakpoint in gene body, predicted haploinsufficiency, in silico fusion frame |

Rules: every classification carries T-grade per evidence line. Multiple evidence types upgrade (T3 + T2 = T2). Absence of data is "No data", not T4. Discordant evidence must be documented.

### Multi-Agent Workflow Examples

**"Analyze CNV report from clinical microarray for a child with developmental delay"**
1. Structural Variant Analysis -> load segments, classify CNV states, gene impacts, dosage sensitivity, ClinGen framework
2. Variant Interpretation -> ACMG classification for single-gene CNVs, haploinsufficiency evidence

**"Interpret structural variants from tumor whole-genome sequencing"**
1. Structural Variant Analysis -> parse SV VCF, filter, detect fusions, focal amplifications, homozygous deletions, chromothripsis
2. Cancer Variant Interpreter -> tier classification for actionable SVs, therapeutic matching

**"What fusion genes are present in this WGS data?"**
1. Structural Variant Analysis -> parse breakpoints, fusion detection, annotate against COSMIC fusions
2. Cancer Variant Interpreter -> therapeutic actionability, clinical trial matching

**"Classify 1.5 Mb deletion on 22q11.2 from prenatal microarray"**
1. Structural Variant Analysis -> map to coordinates, identify genes, population frequency, ClinGen framework
2. Variant Interpretation -> gene dosage sensitivity, microdeletion syndrome cross-reference

**"Review karyotype showing t(9;22)(q34;q11.2) in leukemia"**
1. Structural Variant Analysis -> parse ISCN, map to coordinates, identify BCR-ABL1 fusion
2. Cancer Variant Interpreter -> Philadelphia chromosome interpretation, TKI eligibility, resistance monitoring

## Completeness Checklist
- [ ] SV data loaded and QC summary generated (type distribution, size, PASS rate)
- [ ] SVs filtered by quality metrics and assigned quality tiers
- [ ] CNV segments classified by copy number state with genome-wide plot
- [ ] Gene impact assessment completed with dosage sensitivity annotation
- [ ] Fusion gene candidates detected and annotated against known oncogenic fusions
- [ ] Population frequency annotated via gnomAD SV cross-reference
- [ ] ACMG/ClinGen classification applied to clinically relevant SVs
- [ ] Chromothripsis screening performed for cancer samples
- [ ] Focal amplifications and homozygous deletions identified
- [ ] Final SV report generated with evidence tiers (T1-T4)
