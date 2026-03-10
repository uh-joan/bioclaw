---
name: variant-analysis
description: Genomic variant analysis and VCF processing. Variant calling QC, annotation, filtering, population genetics, allele frequency analysis, Hardy-Weinberg equilibrium, burden testing, variant effect prediction, VCF parsing, genotype analysis. Use when user mentions variant analysis, VCF, variant calling, genotype, allele frequency, Hardy-Weinberg, variant filtering, variant annotation, burden test, SKAT, variant QC, or population genetics.
---

# Variant Analysis

> **Code recipes**: See [recipes.md](recipes.md) in this directory for copy-paste executable code templates.

Upstream genomic variant data processing and population-level analysis. The agent writes and executes Python code for VCF parsing, quality control, variant annotation, population frequency analysis, Hardy-Weinberg equilibrium testing, burden testing, and variant prioritization. This skill handles the computational pipeline from raw variant calls to prioritized variant lists. Distinct from variant-interpretation, which performs downstream ACMG clinical classification and pathogenicity scoring on already-processed variants.

## Report-First Workflow

1. **Create report file immediately**: `variants_variant_analysis_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## Cross-Reference: Other Skills

- **ACMG clinical variant classification and pathogenicity scoring** -> use variant-interpretation skill
- **GWAS SNP annotation and locus-to-gene mapping** -> use gwas-snp-interpretation skill
- **Somatic cancer variant interpretation and molecular tumor board** -> use cancer-variant-interpreter skill
- **Structural variant detection and characterization (CNVs, SVs, translocations)** -> use structural-variant-analysis skill

## Python Environment

Python 3 with pandas, numpy, scipy, matplotlib, seaborn, and standard library (re, csv, gzip, collections). No specialized bioinformatics libraries (pysam, cyvcf2, hail). All VCF parsing uses pandas and text processing.

## Available MCP Tools

### `mcp__ensembl__ensembl_data` (Genomic Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `lookup_gene` | Get gene info by ID or symbol | `gene_id`, `species`, `expand` |
| `search_genes` | Search genes by name/description | `query`, `species`, `biotype`, `limit` |
| `get_sequence` | Get genomic/transcript sequence | `region`, `species`, `format`, `mask` |
| `get_variants` | Get variants in a region | `region`, `species`, `consequence_type` |
| `get_variant_consequences` | Predict variant effects (VEP) | `variants` (array of HGVS) |
| `get_xrefs` | Get cross-database references | `gene_id`, `external_db`, `all_levels` |

### `mcp__gnomad__gnomad_data` (Population Frequencies & Gene Constraint)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_variant` | Variant frequencies, consequences, LoF annotations, ClinVar link | `variant_id` (chr-pos-ref-alt) |
| `get_population_frequencies` | Per-population allele frequencies (BA1/BS1/PM2 ACMG criteria) | `variant_id` |
| `get_gene_constraint` | pLI, LOEUF, missense z-score — gene-level intolerance to variation | `gene_symbol` or `gene_id` |
| `filter_rare_variants` | Find rare variants in a gene (max AF filter) | `gene_symbol`, `max_af` |
| `get_gene_variants` | All known variants in a gene with frequencies | `gene_symbol` or `gene_id` |
| `batch_gene_constraint` | Constraint scores for gene panels (up to 20) | `gene_symbols` (array) |

### `mcp__jaspar__jaspar_data` (Transcription Factor Binding Analysis)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `variant_impact` | Assess TF binding impact for non-coding variants | `variant`, `genome`, `threshold` |
| `scan_sequence` | Scan genomic sequence for TF binding sites | `sequence`, `matrix_id`, `threshold` |

**JASPAR Workflow:** Use JASPAR to assess non-coding variant impact on transcription factor binding. During variant annotation (Phase 4) and prioritization (Phase 7), variants in regulatory regions (promoters, enhancers, UTRs) that lack coding consequence predictions can be evaluated for TF binding disruption using `variant_impact`. This adds mechanistic context for MODIFIER-impact variants that might otherwise be deprioritized. Use `scan_sequence` to identify TF binding sites across a region, which helps determine whether a non-coding variant falls within a functionally occupied regulatory element.

---

## Data Input Formats

**VCF fields:** CHROM, POS, ID, REF, ALT, QUAL, FILTER, INFO (AF/DP/AC/AN key-value pairs), FORMAT (GT:GQ:DP:AD field order), then per-sample genotype columns. Header lines start with `##`. Supports gzipped VCF.

**Variant tables:** Tab/CSV with chromosome, position, ref, alt, and annotation columns (VEP, SnpEff, ANNOVAR exports).

**Allele count matrices:** Gene-by-sample matrices for burden testing. Rows = genes/regions, columns = samples, values = qualifying variant counts.

---

## Analysis Pipeline

### Phase 1: VCF Parsing & QC

```python
import pandas as pd
import numpy as np
import re, gzip
from collections import defaultdict

def parse_vcf(vcf_path):
    """Parse VCF into DataFrame. Handles gzip."""
    opener = gzip.open if vcf_path.endswith('.gz') else open
    header_lines, records = [], []
    with opener(vcf_path, 'rt') as f:
        for line in f:
            if line.startswith('##'):
                header_lines.append(line.strip()); continue
            if line.startswith('#CHROM'):
                col_names = line.strip().lstrip('#').split('\t'); continue
            records.append(line.strip().split('\t'))
    df = pd.DataFrame(records, columns=col_names)
    df['POS'] = df['POS'].astype(int)
    df['QUAL'] = pd.to_numeric(df['QUAL'], errors='coerce')
    return df, header_lines

def parse_info_field(info_str):
    """Parse INFO field to dict. Flag entries (no '=') get True."""
    d = {}
    for entry in info_str.split(';'):
        if '=' in entry:
            k, v = entry.split('=', 1); d[k] = v
        else:
            d[entry] = True
    return d

def apply_site_qc(df, min_qual=30, min_dp=10, require_pass=True):
    """Filter by QUAL, INFO/DP, and FILTER field."""
    n_start = len(df)
    df['info_parsed'] = df['INFO'].apply(parse_info_field)
    df['INFO_DP'] = df['info_parsed'].apply(lambda d: int(d.get('DP', 0)))
    mask = (df['QUAL'] >= min_qual) & (df['INFO_DP'] >= min_dp)
    if require_pass:
        mask &= df['FILTER'].isin(['PASS', '.'])
    df_out = df[mask].copy()
    print(f"Site QC: {n_start} -> {len(df_out)} variants")
    return df_out
```

### Phase 2: Sample-Level QC

Metrics: call rate (missingness), mean GQ, mean DP, heterozygosity rate, Ti/Tv ratio.

```python
def compute_sample_qc(df, sample_cols):
    """Per-sample QC: call_rate, het_rate, mean_gq, mean_dp."""
    fmt = df['FORMAT'].iloc[0].split(':')
    gt_i = fmt.index('GT')
    gq_i = fmt.index('GQ') if 'GQ' in fmt else None
    dp_i = fmt.index('DP') if 'DP' in fmt else None
    rows = []
    for s in sample_cols:
        gts, gqs, dps = [], [], []
        for val in df[s]:
            f = val.split(':')
            gts.append(f[gt_i] if gt_i < len(f) else '.')
            if gq_i and gq_i < len(f):
                try: gqs.append(float(f[gq_i]))
                except: gqs.append(np.nan)
            if dp_i and dp_i < len(f):
                try: dps.append(int(f[dp_i]))
                except: dps.append(0)
        called = [g for g in gts if g not in ('.', './.', '.|.')]
        n_het = sum(1 for g in called if _is_het(g))
        rows.append({'sample': s, 'call_rate': len(called)/len(gts),
                     'het_rate': n_het/len(called) if called else 0,
                     'mean_gq': np.nanmean(gqs) if gqs else np.nan,
                     'mean_dp': np.nanmean(dps) if dps else np.nan})
    return pd.DataFrame(rows)

def _is_het(gt):
    sep = '|' if '|' in gt else '/'
    return len(set(gt.split(sep))) > 1

def compute_titv(df, sample_col):
    """Ti/Tv ratio for a sample. Transitions: A<->G, C<->T."""
    ti_set = {('A','G'),('G','A'),('C','T'),('T','C')}
    n_ti = n_tv = 0
    gt_i = df['FORMAT'].iloc[0].split(':').index('GT')
    for _, r in df.iterrows():
        gt = r[sample_col].split(':')[gt_i]
        if gt in ('.', './.', '.|.'): continue
        if not any(a not in ('0','.') for a in gt.replace('|','/').split('/')): continue
        if len(r['REF']) != 1 or len(r['ALT']) != 1: continue
        if (r['REF'], r['ALT']) in ti_set: n_ti += 1
        else: n_tv += 1
    return n_ti / n_tv if n_tv else float('inf')

def flag_samples(qc_df, min_cr=0.95, het_range=(0.1,0.5), min_gq=20):
    """Add qc_pass and qc_flags columns."""
    flags = []
    for _, r in qc_df.iterrows():
        f = []
        if r['call_rate'] < min_cr: f.append('low_call_rate')
        if not (het_range[0] <= r['het_rate'] <= het_range[1]): f.append('het_outlier')
        if r['mean_gq'] < min_gq: f.append('low_gq')
        flags.append(f)
    qc_df['qc_pass'] = [len(f)==0 for f in flags]
    qc_df['qc_flags'] = ['; '.join(f) or 'PASS' for f in flags]
    return qc_df
```

### Phase 3: Variant-Level QC

HWE testing, call rate filtering, allele frequency spectrum.

```python
from scipy import stats

def genotype_counts(gts):
    """Count ref-hom, het, alt-hom, missing from GT strings."""
    rr = het = aa = miss = 0
    for g in gts:
        if g in ('.', './.', '.|.'): miss += 1; continue
        sep = '|' if '|' in g else '/'
        alleles = set(g.split(sep))
        if alleles == {'0'}: rr += 1
        elif len(alleles) > 1: het += 1
        else: aa += 1
    return rr, het, aa, miss

def hwe_test(n_rr, n_het, n_aa):
    """Chi-square HWE test. Returns (chi2, p_value)."""
    n = n_rr + n_het + n_aa
    if n == 0: return np.nan, np.nan
    p = (2*n_rr + n_het) / (2*n); q = 1 - p
    exp = [p**2*n, 2*p*q*n, q**2*n]
    if any(e == 0 for e in exp): return 0.0, 1.0
    chi2 = sum((o-e)**2/e for o, e in zip([n_rr,n_het,n_aa], exp))
    return chi2, 1 - stats.chi2.cdf(chi2, df=1)

def variant_level_qc(df, sample_cols, hwe_thresh=1e-6, min_cr=0.95, min_maf=0.01):
    """Add maf, call_rate, hwe_p, variant_qc_pass columns."""
    gt_i = df['FORMAT'].iloc[0].split(':').index('GT')
    mafs, crs, hwe_ps = [], [], []
    for _, r in df.iterrows():
        gts = [r[s].split(':')[gt_i] if gt_i < len(r[s].split(':')) else '.'
               for s in sample_cols]
        rr, het, aa, miss = genotype_counts(gts)
        n = rr + het + aa
        crs.append(n / len(sample_cols) if sample_cols else 0)
        af = (het + 2*aa) / (2*n) if n else 0
        mafs.append(min(af, 1-af))
        _, p = hwe_test(rr, het, aa)
        hwe_ps.append(p)
    df['maf'] = mafs; df['call_rate'] = crs; df['hwe_p'] = hwe_ps
    df['variant_qc_pass'] = (
        (df['call_rate'] >= min_cr) & (df['maf'] >= min_maf) & (df['hwe_p'] >= hwe_thresh)
    )
    print(f"Variant QC: {df['variant_qc_pass'].sum()} pass / {len(df)} total")
    return df
```

### Phase 4: Variant Annotation

Query Ensembl for gene context and VEP consequence predictions:

```
1. mcp__ensembl__ensembl_data(method: "lookup_gene", gene_id: "GENE_SYMBOL", species: "homo_sapiens")
   -> Gene coordinates, biotype, Ensembl ID for annotation context

2. mcp__ensembl__ensembl_data(method: "get_variant_consequences", variants: ["9:g.22125504G>C"])
   -> VEP consequence predictions: impact, SIFT, PolyPhen scores

3. mcp__ensembl__ensembl_data(method: "get_variants", region: "7:140453100-140453200", species: "homo_sapiens")
   -> Known variants in a region for comparison with called variants
```

Consequence prediction parsing from VEP (CSQ) or SnpEff (ANN) INFO fields.

```python
CONSEQUENCE_SEVERITY = {
    'transcript_ablation': 1, 'splice_acceptor_variant': 2, 'splice_donor_variant': 3,
    'stop_gained': 4, 'frameshift_variant': 5, 'stop_lost': 6, 'start_lost': 7,
    'missense_variant': 8, 'inframe_insertion': 9, 'inframe_deletion': 10,
    'protein_altering_variant': 11, 'synonymous_variant': 12, 'splice_region_variant': 13,
    '5_prime_UTR_variant': 16, '3_prime_UTR_variant': 17, 'intron_variant': 18,
    'upstream_gene_variant': 19, 'downstream_gene_variant': 20, 'intergenic_variant': 21,
}
IMPACT_MAP = {c: ('HIGH' if s <= 7 else 'MODERATE' if s <= 11 else 'LOW' if s <= 15 else 'MODIFIER')
              for c, s in CONSEQUENCE_SEVERITY.items()}

def parse_vep_csq(info_str, fields=None):
    """Parse VEP CSQ from INFO. Returns list of annotation dicts."""
    if fields is None:
        fields = ['Allele','Consequence','IMPACT','SYMBOL','Gene','Feature_type','Feature','BIOTYPE']
    d = parse_info_field(info_str)
    if 'CSQ' not in d: return []
    return [{fields[i]: v for i, v in enumerate(t.split('|')) if i < len(fields)}
            for t in d['CSQ'].split(',')]

def parse_snpeff_ann(info_str):
    """Parse SnpEff ANN from INFO. Returns list of annotation dicts."""
    ann_fields = ['Allele','Annotation','Annotation_Impact','Gene_Name','Gene_ID',
                  'Feature_Type','Feature_ID','Transcript_BioType','Rank',
                  'HGVS.c','HGVS.p','cDNA_pos','CDS_pos','AA_pos','Distance','Errors']
    d = parse_info_field(info_str)
    if 'ANN' not in d: return []
    return [{ann_fields[i]: v for i, v in enumerate(e.split('|')) if i < len(ann_fields)}
            for e in d['ANN'].split(',')]

def annotate_variants(df):
    """Add consequence, impact, gene columns from VEP or SnpEff annotations."""
    csqs, imps, genes = [], [], []
    for _, r in df.iterrows():
        anns = parse_vep_csq(r['INFO']) or parse_snpeff_ann(r['INFO'])
        if anns:
            best = min(anns, key=lambda a: min(
                CONSEQUENCE_SEVERITY.get(c.strip(), 99)
                for c in a.get('Consequence', a.get('Annotation', 'unknown')).split('&')))
            csq = best.get('Consequence', best.get('Annotation', 'unknown')).split('&')[0].strip()
            csqs.append(csq)
            imps.append(best.get('IMPACT', best.get('Annotation_Impact', IMPACT_MAP.get(csq, 'UNKNOWN'))))
            genes.append(best.get('SYMBOL', best.get('Gene_Name', '')))
        else:
            csqs.append('unannotated'); imps.append('UNKNOWN'); genes.append('')
    df['consequence'] = csqs; df['impact'] = imps; df['gene'] = genes
    return df
```

### Phase 5: Population Frequency Analysis

Allele frequency calculation, site frequency spectrum (SFS), Fst for population differentiation.

```python
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

def compute_allele_frequencies(df, sample_cols):
    """Add alt_af, ref_af, alt_ac, an columns from genotype data."""
    gt_i = df['FORMAT'].iloc[0].split(':').index('GT')
    afs, acs, ans = [], [], []
    for _, r in df.iterrows():
        n_alt = n_total = 0
        for s in sample_cols:
            gt = r[s].split(':')[gt_i] if gt_i < len(r[s].split(':')) else '.'
            if gt in ('.', './.', '.|.'): continue
            for a in gt.replace('|', '/').split('/'):
                if a == '.': continue
                n_total += 1
                if a != '0': n_alt += 1
        afs.append(n_alt/n_total if n_total else 0)
        acs.append(n_alt); ans.append(n_total)
    df['alt_af'] = afs; df['ref_af'] = [1-a for a in afs]
    df['alt_ac'] = acs; df['an'] = ans
    return df

def plot_sfs(df, output='sfs.png'):
    """Plot unfolded and folded site frequency spectrum."""
    afs = df['alt_af'][(df['alt_af'] > 0) & (df['alt_af'] < 1)]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    ax1.hist(afs, bins=50, edgecolor='black', alpha=0.7, color='steelblue')
    ax1.set(xlabel='Alt Allele Frequency', ylabel='Count', title='Unfolded SFS')
    mafs = afs.apply(lambda x: min(x, 1-x))
    ax2.hist(mafs, bins=25, edgecolor='black', alpha=0.7, color='darkorange')
    ax2.set(xlabel='Minor Allele Frequency', ylabel='Count', title='Folded SFS')
    plt.tight_layout(); plt.savefig(output, dpi=150); plt.close()
    print(f"SFS saved to {output}")

def compute_fst(df, sample_cols, pop_map):
    """Weir-Cockerham Fst between two populations. pop_map: {sample: pop_label}."""
    pops = sorted(set(pop_map.values()))
    assert len(pops) == 2
    pop_s = {p: [s for s in sample_cols if pop_map.get(s)==p] for p in pops}
    gt_i = df['FORMAT'].iloc[0].split(':').index('GT')
    nums, dens = [], []
    for _, r in df.iterrows():
        p_af = {}
        for p in pops:
            na = nt = 0
            for s in pop_s[p]:
                gt = r[s].split(':')[gt_i] if gt_i < len(r[s].split(':')) else '.'
                if gt in ('.', './.', '.|.'): continue
                for a in gt.replace('|','/').split('/'):
                    if a == '.': continue
                    nt += 1
                    if a != '0': na += 1
            p_af[p] = na/nt if nt else 0
        pbar = np.mean(list(p_af.values()))
        if pbar in (0, 1): continue
        nbar = np.mean([len(pop_s[p])*2 for p in pops])
        msp = sum(len(pop_s[p])*2*(p_af[p]-pbar)**2 for p in pops)
        msg = pbar*(1-pbar) - msp/(2*nbar)
        if msp + msg > 0:
            nums.append(msp - msg); dens.append(msp + msg)
    return max(0, sum(nums)/sum(dens)) if dens else 0
```

### Phase 6: Burden Testing

Gene-based collapsing test for rare variant association.

```python
from scipy.stats import fisher_exact, mannwhitneyu

def burden_test(df, sample_cols, phenotypes, max_maf=0.01,
                impact_filter=('HIGH', 'MODERATE')):
    """Collapsing burden test per gene. Fisher exact (binary) or Mann-Whitney (continuous).
    phenotypes: {sample: value}. Returns per-gene results DataFrame."""
    gt_i = df['FORMAT'].iloc[0].split(':').index('GT')
    is_binary = set(phenotypes.values()) <= {0, 1}
    # Group qualifying variants by gene
    qualify = df[(df['maf'] <= max_maf) & (df['impact'].isin(impact_filter))]
    gene_groups = qualify.groupby('gene')
    results = []
    for gene, gdf in gene_groups:
        carrier = {s: 0 for s in sample_cols}
        for _, r in gdf.iterrows():
            for s in sample_cols:
                gt = r[s].split(':')[gt_i] if gt_i < len(r[s].split(':')) else '.'
                if gt in ('.', './.', '.|.'): continue
                if any(a not in ('0','.') for a in gt.replace('|','/').split('/')):
                    carrier[s] = 1
        n_carriers = sum(carrier.values())
        if is_binary:
            a = sum(1 for s in sample_cols if carrier[s]==1 and phenotypes.get(s)==1)
            b = sum(1 for s in sample_cols if carrier[s]==1 and phenotypes.get(s)==0)
            c = sum(1 for s in sample_cols if carrier[s]==0 and phenotypes.get(s)==1)
            d = sum(1 for s in sample_cols if carrier[s]==0 and phenotypes.get(s)==0)
            stat, pv = fisher_exact([[a,b],[c,d]])
        else:
            cv = [phenotypes[s] for s in sample_cols if carrier[s]==1 and s in phenotypes]
            nv = [phenotypes[s] for s in sample_cols if carrier[s]==0 and s in phenotypes]
            stat, pv = mannwhitneyu(cv, nv, alternative='two-sided') if cv and nv else (np.nan, np.nan)
        results.append({'gene': gene, 'n_variants': len(gdf), 'n_carriers': n_carriers,
                        'test_stat': stat, 'p_value': pv})
    rdf = pd.DataFrame(results)
    if len(rdf):
        rdf['p_adjusted'] = np.minimum(rdf['p_value'] * len(rdf), 1.0)
        rdf = rdf.sort_values('p_value').reset_index(drop=True)
    return rdf

def weighted_burden(df, sample_cols, gene, weights=None):
    """Weighted burden score per sample. Default weights: HIGH=5, MODERATE=2, LOW=1."""
    if weights is None: weights = {'HIGH': 5, 'MODERATE': 2, 'LOW': 1, 'MODIFIER': 0}
    gdf = df[df['gene'] == gene]
    gt_i = df['FORMAT'].iloc[0].split(':').index('GT')
    scores = {s: 0.0 for s in sample_cols}
    for _, r in gdf.iterrows():
        w = weights.get(r.get('impact', 'MODIFIER'), 0)
        for s in sample_cols:
            gt = r[s].split(':')[gt_i] if gt_i < len(r[s].split(':')) else '.'
            if gt in ('.', './.', '.|.'): continue
            n_alt = sum(1 for a in gt.replace('|','/').split('/') if a not in ('0','.'))
            scores[s] += n_alt * w
    return scores
```

### Phase 7: Variant Prioritization

Combined annotation scoring, CADD/REVEL integration, frequency filtering cascade.

```python
def prioritize(df, cadd_col=None, revel_col=None, max_af=0.01, min_cadd=15, min_revel=0.5):
    """Multi-criteria prioritization: QC pass, rare, HIGH/MODERATE impact, prediction scores."""
    f = df[df.get('variant_qc_pass', True)].copy() if 'variant_qc_pass' in df.columns else df.copy()
    if 'alt_af' in f.columns: f = f[f['alt_af'] <= max_af]
    if 'impact' in f.columns: f = f[f['impact'].isin(['HIGH', 'MODERATE'])]
    if cadd_col and cadd_col in f.columns:
        f[cadd_col] = pd.to_numeric(f[cadd_col], errors='coerce')
        has = f[cadd_col].notna()
        f = f[~has | (f[cadd_col] >= min_cadd)]
    if revel_col and revel_col in f.columns:
        f[revel_col] = pd.to_numeric(f[revel_col], errors='coerce')
        is_mis = f['consequence'] == 'missense_variant'
        has = f[revel_col].notna()
        f = f[~(is_mis & has) | (f[revel_col] >= min_revel)]
    imp_ord = {'HIGH': 0, 'MODERATE': 1, 'LOW': 2, 'MODIFIER': 3}
    f['impact_rank'] = f['impact'].map(imp_ord).fillna(4)
    sort_cols = ['impact_rank']
    asc = [True]
    if cadd_col and cadd_col in f.columns: sort_cols.append(cadd_col); asc.append(False)
    f = f.sort_values(sort_cols, ascending=asc).reset_index(drop=True)
    f['priority_rank'] = range(1, len(f)+1)
    print(f"Prioritized: {len(df)} -> {len(f)} variants")
    return f

def variant_report(df, output='variant_report.tsv'):
    """Write prioritized variants to TSV report."""
    cols = [c for c in ['priority_rank','CHROM','POS','ID','REF','ALT','gene',
            'consequence','impact','maf','alt_af','hwe_p','call_rate','QUAL'] if c in df.columns]
    df[cols].to_csv(output, sep='\t', index=False)
    print(f"Report: {output} ({len(df)} variants)")
```

---

## Quality Metrics Reference

| Metric | WGS | WES | Panel | Description |
|--------|-----|-----|-------|-------------|
| QUAL | >= 30 | >= 30 | >= 50 | Phred-scaled call confidence |
| INFO/DP | >= 10 | >= 20 | >= 50 | Total site depth |
| GQ | >= 20 | >= 20 | >= 30 | Genotype quality |
| Sample DP | >= 10 | >= 20 | >= 50 | Per-sample depth |
| AB (het) | 0.25-0.75 | 0.25-0.75 | 0.3-0.7 | Allele balance |
| Ti/Tv (expected) | 2.0-2.1 | 2.8-3.3 | 2.5-3.5 | Transition/transversion |
| Ti/Tv (flag if) | < 1.8 | < 2.3 | < 2.0 | Possible artifact |
| Sample call rate | >= 0.95 | >= 0.95 | >= 0.98 | Minimum genotype completeness |
| HWE p-value | >= 1e-6 | >= 1e-6 | >= 1e-4 | Hardy-Weinberg filter |

---

## Variant Classification by Consequence

| Consequence | Impact | Severity | Typical Approach |
|-------------|--------|----------|-----------------|
| transcript_ablation | HIGH | 1 | Gene loss. Check constraint (pLI, LOEUF). |
| splice_acceptor/donor | HIGH | 2-3 | Canonical splice disruption. Validate with SpliceAI. |
| stop_gained | HIGH | 4 | Premature stop. Likely NMD. Check last-exon position. |
| frameshift_variant | HIGH | 5 | Frame disruption. Check if last exon (NMD escape). |
| stop_lost / start_lost | HIGH | 6-7 | Extended/failed protein. Assess functional domain impact. |
| missense_variant | MODERATE | 8 | AA change. Score with CADD, REVEL, AlphaMissense. |
| inframe_ins/del | MODERATE | 9-10 | Domain insertion/deletion. Check structural context. |
| synonymous_variant | LOW | 12 | No AA change. Check splice boundary. Usually benign. |
| splice_region_variant | LOW | 13 | Near splice site. Score with SpliceAI. Most benign. |
| UTR / intron / intergenic | MODIFIER | 16-21 | Usually benign. Check regulatory overlap (ENCODE). |

---

## Evidence Grading

| Tier | Criteria | Confidence |
|------|----------|------------|
| **T1** | HIGH impact + AF < 0.001 + HWE pass + CADD >= 25 + constrained gene | High |
| **T2** | HIGH/MODERATE + AF < 0.01 + HWE pass + REVEL >= 0.7 or CADD >= 20 | Medium-High |
| **T3** | MODERATE + AF < 0.05 + single predictor support | Medium |
| **T4** | LOW/MODIFIER or AF > 0.05 or HWE failure | Low |

```
T1: Impact=HIGH, AF < 0.001, HWE p >= 1e-6, CADD >= 25, gene pLI > 0.9
T2: Impact=HIGH/MODERATE, AF < 0.01, HWE pass, REVEL >= 0.7 or CADD >= 20
T3: Impact=MODERATE, AF < 0.05, at least one predictor supports deleteriousness
T4: Impact=LOW/MODIFIER, or AF > 0.05, or HWE p < 1e-6 (possible artifact)
```

---

### Population Frequency Context via gnomAD

Use gnomAD MCP to enrich variant prioritization with population frequency data and gene constraint scores.

**Step 1: Look up variant frequency**

```
mcp__gnomad__gnomad_data(method: "get_variant", variant_id: "7-140453136-A-T")
```
Returns overall allele frequency, functional consequence, LoF flags, and ClinVar status. Use the allele frequency to calibrate rarity filters in Phase 7 prioritization.

**Step 2: Per-population frequency breakdown**

```
mcp__gnomad__gnomad_data(method: "get_population_frequencies", variant_id: "7-140453136-A-T")
```
Compare per-ancestry frequencies to detect population-specific enrichment. Variants common in one population but rare globally may be founder variants rather than true disease candidates.

**Step 3: Gene constraint for burden test interpretation**

```
mcp__gnomad__gnomad_data(method: "get_gene_constraint", gene_symbol: "BRAF")
mcp__gnomad__gnomad_data(method: "batch_gene_constraint", gene_symbols: ["BRAF", "TP53", "EGFR", "KRAS"])
```
Genes with high pLI (>0.9) or low LOEUF (<0.35) are intolerant to loss-of-function variation. Use constraint scores to weight burden test results — significant burden in a constrained gene is more likely to be biologically meaningful.

**Step 4: Gene-level variant landscape**

```
mcp__gnomad__gnomad_data(method: "filter_rare_variants", gene_symbol: "BRAF", max_af: 0.001)
mcp__gnomad__gnomad_data(method: "get_gene_variants", gene_symbol: "BRAF")
```
Retrieve all known variants in a gene to compare against called variants. Positions with no gnomAD variation are more likely to be functionally constrained.

---

## Multi-Agent Workflow Examples

**"Analyze my VCF for rare pathogenic variants in epilepsy genes"**
1. Variant Analysis -> Parse VCF, full QC pipeline, annotate, filter rare HIGH/MODERATE in gene panel
2. Variant Interpretation -> ACMG classify prioritized variants
3. Disease Research -> Literature for gene-disease associations

**"Run burden test comparing cases and controls for rare coding variants"**
1. Variant Analysis -> Parse, QC, annotate, collapsing burden test per gene, multiple testing correction
2. Gene Enrichment -> Pathway enrichment on significant genes
3. Drug Target Analyst -> Druggability of significant genes

**"Assess population structure and allele frequency differences"**
1. Variant Analysis -> QC, compute per-population AFs, plot SFS, compute Fst, flag outliers
2. GWAS SNP Interpretation -> Interpret top differentiated SNPs
3. Systems Biology -> Network analysis of differentiated genes

**"QC a whole-exome VCF before clinical analysis"**
1. Variant Analysis -> Site QC (QUAL, DP, FILTER), sample QC (call rate, het, Ti/Tv), variant QC (HWE, MAF), generate report
2. Variant Interpretation -> Clinical classification of passing variants
3. Pharmacogenomics Specialist -> Flag pharmacogenomic variants

## Completeness Checklist

- [ ] VCF parsed and site-level QC applied (QUAL, DP, FILTER thresholds documented)
- [ ] Sample-level QC completed with call rate, het rate, mean GQ, Ti/Tv reported per sample
- [ ] Variant-level QC performed (HWE testing, call rate, MAF filtering)
- [ ] Variants annotated with consequence predictions (VEP or SnpEff)
- [ ] Population allele frequencies calculated and site frequency spectrum plotted
- [ ] gnomAD population frequencies queried for prioritized variants
- [ ] Gene constraint scores (pLI, LOEUF) retrieved for genes with qualifying variants
- [ ] Variant prioritization applied (impact, frequency, prediction score filters)
- [ ] Burden testing completed if case-control design present
- [ ] Final variant report exported as TSV with priority rankings
