# Variant Recipes

Python code templates for somatic variant analysis, CHIP variant classification, VCF parsing, and VAF filtering.

Cross-skill routing: use `variant-analysis` for conceptual guidance, `biostat-recipes` for statistical tests, `alignment-recipes` for upstream variant calling (GATK).

---

## 1. Loading VCF Data into Pandas

### Using cyvcf2

```python
import pandas as pd
from cyvcf2 import VCF

def load_vcf_cyvcf2(vcf_path: str) -> pd.DataFrame:
    """Parse VCF file into a DataFrame using cyvcf2."""
    records = []
    vcf = VCF(vcf_path)
    samples = vcf.samples

    for v in vcf:
        rec = {
            'CHROM': v.CHROM,
            'POS': v.POS,
            'ID': v.ID,
            'REF': v.REF,
            'ALT': ','.join(v.ALT),
            'QUAL': v.QUAL,
            'FILTER': v.FILTER,
        }
        # Extract common INFO fields
        for field in ['DP', 'AF', 'AC', 'AN', 'MQ']:
            try:
                rec[field] = v.INFO.get(field)
            except Exception:
                rec[field] = None

        # Per-sample genotype fields
        for i, sample in enumerate(samples):
            try:
                rec[f'{sample}_GT'] = v.genotypes[i][:2]
                rec[f'{sample}_DP'] = v.format('DP')[i][0] if v.format('DP') is not None else None
                ad = v.format('AD')
                if ad is not None:
                    rec[f'{sample}_AD_REF'] = ad[i][0]
                    rec[f'{sample}_AD_ALT'] = ad[i][1] if len(ad[i]) > 1 else 0
            except Exception:
                pass
        records.append(rec)

    return pd.DataFrame(records)
```

### Manual parsing (no dependencies)

```python
import pandas as pd

def load_vcf_manual(vcf_path: str) -> pd.DataFrame:
    """Parse VCF without external libraries."""
    header = None
    records = []
    with open(vcf_path) as f:
        for line in f:
            if line.startswith('##'):
                continue
            if line.startswith('#'):
                header = line.strip('#\n').split('\t')
                continue
            fields = line.strip().split('\t')
            rec = dict(zip(header, fields))
            # Parse INFO into dict
            info_dict = {}
            for item in rec.get('INFO', '').split(';'):
                if '=' in item:
                    k, v = item.split('=', 1)
                    info_dict[k] = v
                else:
                    info_dict[item] = True
            rec['INFO_DICT'] = info_dict
            records.append(rec)
    return pd.DataFrame(records)
```

---

## 2. Calculating Variant Allele Frequency (VAF)

### From AD field

```python
def calc_vaf_from_ad(df: pd.DataFrame, sample: str) -> pd.Series:
    """Calculate VAF from allelic depth (AD) fields."""
    ad_ref = df[f'{sample}_AD_REF'].astype(float)
    ad_alt = df[f'{sample}_AD_ALT'].astype(float)
    total = ad_ref + ad_alt
    vaf = ad_alt / total
    vaf = vaf.fillna(0.0)
    return vaf

# Usage
df['VAF'] = calc_vaf_from_ad(df, sample='SAMPLE1')
```

### From DP and AD fields separately

```python
def calc_vaf_from_dp(alt_depth: pd.Series, total_depth: pd.Series) -> pd.Series:
    """VAF = alt_depth / total_depth."""
    vaf = alt_depth / total_depth
    return vaf.fillna(0.0).clip(0, 1)
```

### Batch VAF for multi-sample VCF

```python
def calc_vaf_all_samples(df: pd.DataFrame, samples: list[str]) -> pd.DataFrame:
    """Add VAF columns for every sample."""
    for s in samples:
        ref_col = f'{s}_AD_REF'
        alt_col = f'{s}_AD_ALT'
        if ref_col in df.columns and alt_col in df.columns:
            total = df[ref_col].astype(float) + df[alt_col].astype(float)
            df[f'{s}_VAF'] = (df[alt_col].astype(float) / total).fillna(0).clip(0, 1)
    return df
```

---

## 3. Filtering Somatic Variants

```python
def filter_somatic_chip(df: pd.DataFrame, vaf_col: str = 'VAF',
                         min_vaf: float = 0.02, max_vaf: float = 0.30) -> pd.DataFrame:
    """Filter for somatic CHIP variants by VAF range.
    Typical CHIP: VAF between 2% and 30%.
    """
    mask = (df[vaf_col] >= min_vaf) & (df[vaf_col] < max_vaf)
    return df[mask].copy()

# Quick one-liner
somatic = df[(df['VAF'] >= 0.02) & (df['VAF'] < 0.30)]
```

### With depth filter

```python
def filter_somatic_strict(df: pd.DataFrame, min_depth: int = 20,
                           min_vaf: float = 0.02, max_vaf: float = 0.30,
                           min_alt_reads: int = 3) -> pd.DataFrame:
    """Strict somatic filter: VAF range + minimum depth + minimum alt reads."""
    mask = (
        (df['VAF'] >= min_vaf) &
        (df['VAF'] < max_vaf) &
        (df['DP'].astype(float) >= min_depth) &
        (df['SAMPLE1_AD_ALT'].astype(float) >= min_alt_reads)
    )
    return df[mask].copy()
```

---

## 4. Filtering by Variant Type (Functional Annotation)

```python
# Exclude non-coding / non-functional variants
EXCLUDE_ANNOTATIONS = {
    'intronic', 'intergenic', 'UTR3', 'UTR5',
    'upstream', 'downstream', 'ncRNA_intronic', 'ncRNA_exonic'
}

def filter_exonic(df: pd.DataFrame, anno_col: str = 'Func.refGene') -> pd.DataFrame:
    """Keep only exonic/splicing variants."""
    return df[~df[anno_col].isin(EXCLUDE_ANNOTATIONS)].copy()

# Filter by specific exonic function
PATHOGENIC_TYPES = {'nonsynonymous_SNV', 'stopgain', 'stoploss',
                     'frameshift_deletion', 'frameshift_insertion',
                     'splicing', 'nonframeshift_deletion', 'nonframeshift_insertion'}

def filter_pathogenic_types(df: pd.DataFrame,
                             exonic_col: str = 'ExonicFunc.refGene') -> pd.DataFrame:
    """Keep likely pathogenic variant types."""
    return df[df[exonic_col].isin(PATHOGENIC_TYPES)].copy()

# Remove synonymous
nonsynonymous = df[df['ExonicFunc.refGene'] != 'synonymous_SNV']
```

---

## 5. Filtering Reference Calls

```python
def remove_ref_calls(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows where ALT equals REF or ALT is empty/dot."""
    mask = (
        (df['ALT'] != df['REF']) &
        (df['ALT'] != '.') &
        (df['ALT'] != '') &
        (df['ALT'].notna())
    )
    return df[mask].copy()

# One-liner
non_ref = df[(df['ALT'] != df['REF']) & (df['ALT'] != '.')]
```

### Remove homozygous reference genotypes

```python
def remove_hom_ref(df: pd.DataFrame, gt_col: str = 'SAMPLE1_GT') -> pd.DataFrame:
    """Remove 0/0 genotypes."""
    return df[df[gt_col].apply(lambda g: g != [0, 0] if isinstance(g, list) else True)].copy()
```

---

## 6. CHIP Variant Classification (Benign vs Pathogenic)

```python
CHIP_GENES = {
    'DNMT3A', 'TET2', 'ASXL1', 'JAK2', 'TP53', 'PPM1D', 'SF3B1',
    'SRSF2', 'U2AF1', 'ZRSR2', 'IDH1', 'IDH2', 'KRAS', 'NRAS',
    'CBL', 'GNB1', 'GNAS', 'BCOR', 'BCORL1', 'STAG2', 'RAD21',
    'SMC1A', 'SMC3', 'CALR', 'MPL', 'RUNX1', 'EZH2', 'SUZ12',
    'ARID1A', 'ARID2', 'KMT2C', 'NF1', 'CHEK2', 'ATM', 'BRCC3'
}

def classify_chip(df: pd.DataFrame, gene_col: str = 'Gene.refGene') -> pd.DataFrame:
    """Flag CHIP-associated genes and classify pathogenicity."""
    df = df.copy()
    df['is_chip_gene'] = df[gene_col].isin(CHIP_GENES)

    # ClinVar-based classification
    clinvar_pathogenic = {'Pathogenic', 'Likely_pathogenic', 'Pathogenic/Likely_pathogenic'}
    clinvar_benign = {'Benign', 'Likely_benign', 'Benign/Likely_benign'}

    if 'CLNSIG' in df.columns:
        df['clinvar_class'] = df['CLNSIG'].apply(
            lambda x: 'pathogenic' if x in clinvar_pathogenic
            else 'benign' if x in clinvar_benign
            else 'VUS'
        )

    # In-silico prediction composite
    if 'SIFT_pred' in df.columns and 'Polyphen2_HDIV_pred' in df.columns:
        df['in_silico_damaging'] = (
            (df['SIFT_pred'] == 'D') |
            (df['Polyphen2_HDIV_pred'].isin(['D', 'P']))
        )

    return df

# Filter to known CHIP genes only
chip_variants = df[df['Gene.refGene'].isin(CHIP_GENES)]
```

---

## 7. Per-Sample Variant Counting

```python
def count_variants_per_sample(df: pd.DataFrame,
                               sample_col: str = 'sample_id') -> pd.DataFrame:
    """Count total variants per sample."""
    counts = df.groupby(sample_col).size().reset_index(name='variant_count')
    return counts

# By mutation type
def count_by_type(df: pd.DataFrame, sample_col: str = 'sample_id',
                  type_col: str = 'ExonicFunc.refGene') -> pd.DataFrame:
    """Count variants per sample grouped by mutation type."""
    return df.groupby([sample_col, type_col]).size().unstack(fill_value=0)

# Group by mutation status
def count_by_status(df: pd.DataFrame, status_col: str = 'mutation_status') -> pd.DataFrame:
    """Summarize variant counts by patient mutation status."""
    return df.groupby(status_col).agg(
        n_patients=('sample_id', 'nunique'),
        total_variants=('sample_id', 'size'),
        mean_variants=('sample_id', lambda x: x.value_counts().mean()),
        median_variants=('sample_id', lambda x: x.value_counts().median())
    )
```

---

## 8. Variant Frequency Comparison Between Groups

```python
import numpy as np
from scipy.stats import kruskal, mannwhitneyu

def compare_variant_counts(df: pd.DataFrame, count_col: str = 'variant_count',
                            group_col: str = 'group') -> dict:
    """Compare variant counts across groups (carrier, affected, control)."""
    groups = {name: grp[count_col].values for name, grp in df.groupby(group_col)}
    group_names = list(groups.keys())
    group_values = list(groups.values())

    result = {'group_summaries': {}}
    for name, vals in groups.items():
        result['group_summaries'][name] = {
            'n': len(vals),
            'mean': np.mean(vals),
            'median': np.median(vals),
            'std': np.std(vals),
        }

    # Kruskal-Wallis (3+ groups)
    if len(group_values) >= 3:
        H, p = kruskal(*group_values)
        result['kruskal_wallis'] = {'H': H, 'p': p}

    # Pairwise Mann-Whitney U
    pairwise = {}
    for i in range(len(group_names)):
        for j in range(i + 1, len(group_names)):
            U, p = mannwhitneyu(group_values[i], group_values[j], alternative='two-sided')
            pairwise[f'{group_names[i]}_vs_{group_names[j]}'] = {'U': U, 'p': p}
    result['pairwise_mannwhitney'] = pairwise

    return result

# Usage
per_sample = df.groupby(['sample_id', 'group']).size().reset_index(name='variant_count')
stats = compare_variant_counts(per_sample)
print(f"Kruskal-Wallis p = {stats['kruskal_wallis']['p']:.4e}")
for pair, res in stats['pairwise_mannwhitney'].items():
    print(f"  {pair}: U={res['U']:.1f}, p={res['p']:.4e}")
```

---

## 9. Transition/Transversion (Ts/Tv) Ratio

```python
def calc_tstv_ratio(df: pd.DataFrame, ref_col: str = 'REF',
                     alt_col: str = 'ALT') -> dict:
    """Calculate transition/transversion ratio for SNPs."""
    transitions = {'AG', 'GA', 'CT', 'TC'}

    # Filter to SNPs only (single base REF and ALT)
    snps = df[(df[ref_col].str.len() == 1) & (df[alt_col].str.len() == 1)].copy()

    ts_count = 0
    tv_count = 0
    for _, row in snps.iterrows():
        pair = row[ref_col] + row[alt_col]
        if pair in transitions:
            ts_count += 1
        else:
            tv_count += 1

    ratio = ts_count / tv_count if tv_count > 0 else float('inf')

    return {
        'total_snps': len(snps),
        'transitions': ts_count,
        'transversions': tv_count,
        'ts_tv_ratio': ratio,
    }

# Vectorized version (faster for large datasets)
def calc_tstv_vectorized(df: pd.DataFrame) -> float:
    """Vectorized Ts/Tv calculation."""
    snps = df[(df['REF'].str.len() == 1) & (df['ALT'].str.len() == 1)]
    pairs = snps['REF'] + snps['ALT']
    ts = pairs.isin(['AG', 'GA', 'CT', 'TC']).sum()
    tv = len(pairs) - ts
    return ts / tv if tv > 0 else float('inf')

# Expected: ~2.0-2.1 for whole genome, ~2.8-3.0 for exome
```

---

## 10. IQR Calculation for Variant Counts

```python
import numpy as np

def calc_iqr_stats(counts: np.ndarray) -> dict:
    """Compute IQR and outlier bounds for variant counts."""
    q1 = np.percentile(counts, 25)
    q3 = np.percentile(counts, 75)
    iqr = q3 - q1
    lower_fence = q1 - 1.5 * iqr
    upper_fence = q3 + 1.5 * iqr

    return {
        'q1': q1,
        'median': np.median(counts),
        'q3': q3,
        'iqr': iqr,
        'lower_fence': max(0, lower_fence),
        'upper_fence': upper_fence,
        'outliers_low': int(np.sum(counts < lower_fence)),
        'outliers_high': int(np.sum(counts > upper_fence)),
    }

# Per-group IQR
def iqr_by_group(df: pd.DataFrame, count_col: str = 'variant_count',
                  group_col: str = 'group') -> pd.DataFrame:
    """IQR stats per group."""
    results = []
    for name, grp in df.groupby(group_col):
        stats = calc_iqr_stats(grp[count_col].values)
        stats['group'] = name
        results.append(stats)
    return pd.DataFrame(results).set_index('group')
```

---

## 11. Cross-Tabulation: Variant Type Proportions by Group

```python
import pandas as pd

def variant_type_crosstab(df: pd.DataFrame, group_col: str = 'group',
                           type_col: str = 'ExonicFunc.refGene') -> pd.DataFrame:
    """Cross-tabulation of variant types by group (proportions)."""
    ct = pd.crosstab(df[group_col], df[type_col], normalize='index')
    return ct

# Raw counts
ct_counts = pd.crosstab(df['group'], df['ExonicFunc.refGene'])

# Proportions per group (rows sum to 1)
ct_prop = pd.crosstab(df['group'], df['ExonicFunc.refGene'], normalize='index')

# Chi-square test on the cross-tabulation
from scipy.stats import chi2_contingency

def test_variant_distribution(df: pd.DataFrame, group_col: str = 'group',
                               type_col: str = 'ExonicFunc.refGene') -> dict:
    """Chi-square test for independence of variant types across groups."""
    ct = pd.crosstab(df[group_col], df[type_col])
    chi2, p, dof, expected = chi2_contingency(ct)
    return {'chi2': chi2, 'p': p, 'dof': dof, 'observed': ct, 'expected': pd.DataFrame(expected, index=ct.index, columns=ct.columns)}
```
