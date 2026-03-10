# CRISPR Experiment Design Recipes

Code templates for CRISPR experiment design: guide RNA design, off-target analysis, library construction, delivery methods, validation assays, and advanced editing strategies (base editing, prime editing).

Cross-skill routing: use `crispr-screen-analysis` SKILL.md for screen data analysis pipelines, `mageck-recipes.md` for MAGeCK CLI workflows and downstream analysis.

---

## 1. Guide RNA Design: On-Target Efficiency Scoring (Rule Set 2 / Azimuth)

Score candidate guide RNAs for predicted on-target cutting efficiency using the Azimuth/Rule Set 2 model.

```python
import numpy as np
import pandas as pd

def rule_set_2_features(guide_30mer):
    """Extract features for Rule Set 2 (Doench et al. 2016) on-target scoring.

    Parameters
    ----------
    guide_30mer : str
        30-nt context sequence: 4nt upstream + 20nt guide + 3nt PAM + 3nt downstream.
        The PAM (NGG) occupies positions 25-27 (1-indexed).

    Returns
    -------
    dict with feature values for scoring.
    """
    seq = guide_30mer.upper()
    assert len(seq) == 30, f"Expected 30-mer, got {len(seq)}-mer"
    assert seq[25:27] == 'GG', f"Expected NGG PAM at positions 25-27, got {seq[24:27]}"

    guide = seq[4:24]  # 20-nt guide (positions 5-24)
    features = {}

    # Position-specific nucleotide features
    for pos in range(20):
        for nt in 'ACGT':
            features[f'pos{pos+1}_{nt}'] = 1 if guide[pos] == nt else 0

    # Dinucleotide features at each position
    for pos in range(19):
        dinuc = guide[pos:pos+2]
        for d in ['AA','AC','AG','AT','CA','CC','CG','CT',
                  'GA','GC','GG','GT','TA','TC','TG','TT']:
            features[f'dinuc{pos+1}_{d}'] = 1 if dinuc == d else 0

    # GC content of guide
    gc = (guide.count('G') + guide.count('C')) / 20
    features['gc_content'] = gc
    features['gc_gt_70'] = 1 if gc > 0.7 else 0
    features['gc_lt_30'] = 1 if gc < 0.3 else 0

    # Positional GC content (last 6 nt of guide, seed region)
    seed = guide[14:20]
    features['seed_gc'] = (seed.count('G') + seed.count('C')) / 6

    # PAM-proximal nucleotide (position 20 of guide)
    features['pos20_G'] = 1 if guide[19] == 'G' else 0

    # Thermodynamic features (simplified: poly-T terminator check)
    features['has_TTTT'] = 1 if 'TTTT' in guide else 0

    return features

def score_guides_rule_set_2(guide_30mers, min_gc=0.3, max_gc=0.7):
    """Score a list of guide 30-mers using simplified Rule Set 2 heuristics.

    For production use, install Azimuth: pip install azimuth
    This function provides a heuristic approximation for environments without Azimuth.

    Parameters
    ----------
    guide_30mers : list of str
        30-nt context sequences (4 + 20 + NGG + 3).
    min_gc : float
        Minimum GC content filter.
    max_gc : float
        Maximum GC content filter.

    Returns
    -------
    pd.DataFrame with guide sequences and scores.
    """
    results = []
    for seq_30 in guide_30mers:
        seq_30 = seq_30.upper()
        if len(seq_30) != 30:
            results.append({'30mer': seq_30, 'guide': 'INVALID', 'score': 0, 'pass_filter': False})
            continue

        guide = seq_30[4:24]
        gc = (guide.count('G') + guide.count('C')) / 20

        # Heuristic scoring (0-1 scale)
        score = 0.5  # baseline

        # GC content bonus/penalty
        if 0.4 <= gc <= 0.7:
            score += 0.15
        elif gc < 0.3 or gc > 0.8:
            score -= 0.2

        # Position 20 (PAM-proximal): G preferred
        if guide[19] == 'G':
            score += 0.1
        elif guide[19] == 'C':
            score += 0.05

        # Position 16: C preferred (seed region)
        if guide[15] == 'C':
            score += 0.05

        # Poly-T terminator (aborts Pol III transcription)
        if 'TTTT' in guide:
            score -= 0.3

        # Poly-nucleotide runs
        for nt in 'ACGT':
            if nt * 4 in guide:
                score -= 0.1

        # Seed GC (positions 15-20)
        seed_gc = (guide[14:20].count('G') + guide[14:20].count('C')) / 6
        if 0.3 <= seed_gc <= 0.7:
            score += 0.05

        score = max(0, min(1, score))

        pass_filter = (min_gc <= gc <= max_gc and 'TTTT' not in guide and score >= 0.4)

        results.append({
            '30mer': seq_30,
            'guide': guide,
            'gc_content': gc,
            'score': round(score, 3),
            'pass_filter': pass_filter,
        })

    df = pd.DataFrame(results).sort_values('score', ascending=False)

    print(f"Guide RNA scoring (Rule Set 2 heuristic):")
    print(f"  Total guides: {len(df)}")
    print(f"  Passing filter: {df['pass_filter'].sum()}")
    print(f"\n{'Guide (20nt)':<24} {'GC':>5} {'Score':>6} {'Pass':>5}")
    print("-" * 45)
    for _, row in df.iterrows():
        mark = "YES" if row['pass_filter'] else "NO"
        print(f"{row['guide']:<24} {row['gc_content']:>4.0%} {row['score']:>6.3f} {mark:>5}")

    return df

# Example usage
test_30mers = [
    "ACGTGCATGCTAGCTAGCTAGCNGGACGTAC",  # Replace N with A/C/G/T
    "TTTTAGCTAGCTTTTGCTAGCAGGACGTAC",   # Has poly-T
    "ACGTCCCCCCCCCCCCCCCCCCAGGACGTAC",   # Extreme GC
]
# In practice, extract 30-mers from your target gene sequence
print("Replace test sequences with actual target-derived 30-mers.")
```

**Key parameters**: Rule Set 2 requires a 30-mer context (4nt + 20nt guide + NGG + 3nt). GC content 40-70% is optimal. Poly-T runs (TTTT) serve as Pol III terminators and must be avoided. Position 20 G is associated with higher activity.

**Expected output**: Ranked list of guides with on-target efficiency scores and filter status. Use Azimuth package for full model predictions in production.

---

## 2. Off-Target Analysis: Cas-OFFinder and CRISPOR Scoring

Identify potential off-target sites genome-wide using Cas-OFFinder and score them with CRISPOR-like heuristics.

```python
import subprocess
import pandas as pd
import os

def run_cas_offinder(guide_sequence, genome_fasta, pam="NRG", max_mismatches=4,
                      output_file="off_targets.txt"):
    """Run Cas-OFFinder to find potential off-target sites genome-wide.

    Parameters
    ----------
    guide_sequence : str
        20-nt guide RNA sequence (without PAM).
    genome_fasta : str
        Path to reference genome FASTA file.
    pam : str
        PAM sequence pattern ('NRG' for SpCas9, 'TTTN' for Cpf1/Cas12a).
    max_mismatches : int
        Maximum number of mismatches to report (0-5).
    output_file : str
        Output file path for off-target results.

    Returns
    -------
    pd.DataFrame with off-target sites, positions, and mismatch counts.
    """
    # Create Cas-OFFinder input file
    input_file = "cas_offinder_input.txt"
    with open(input_file, 'w') as f:
        f.write(f"{genome_fasta}\n")
        f.write(f"{'N' * len(guide_sequence)}{pam}\n")
        f.write(f"{guide_sequence}{'N' * len(pam)} {max_mismatches}\n")

    # Run Cas-OFFinder (CPU version)
    cmd = f"cas-offinder {input_file} C {output_file}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Cas-OFFinder error: {result.stderr}")
        print("Install: conda install -c bioconda cas-offinder")
        return None

    # Parse results
    cols = ['pattern', 'chromosome', 'position', 'off_target_seq', 'strand', 'mismatches']
    df = pd.read_csv(output_file, sep='\t', header=None, names=cols)

    print(f"Off-target analysis for: {guide_sequence}")
    print(f"  Genome: {genome_fasta}")
    print(f"  Max mismatches: {max_mismatches}")
    print(f"  Total off-target sites found: {len(df)}")
    for mm in range(max_mismatches + 1):
        count = (df['mismatches'] == mm).sum()
        print(f"  {mm} mismatches: {count} sites")

    return df

def score_off_target_risk(guide_sequence, off_target_seq, mismatch_positions):
    """Score off-target risk using mismatch position weighting.

    Mismatches in the seed region (positions 1-12 from PAM) are weighted
    more heavily than distal mismatches (positions 13-20).

    Parameters
    ----------
    guide_sequence : str
        20-nt guide RNA sequence.
    off_target_seq : str
        20-nt off-target DNA sequence.
    mismatch_positions : list of int
        0-indexed positions of mismatches (0 = PAM-proximal).

    Returns
    -------
    float: off-target risk score (0 = no risk, 1 = highest risk).
    """
    # Position weights (PAM-proximal positions weighted higher)
    # Positions 1-8: seed region (highest importance)
    # Positions 9-12: intermediate
    # Positions 13-20: distal (lower importance)
    weights = [0, 0, 0.014, 0, 0, 0.395, 0.317, 0, 0.389, 0.079,
               0.445, 0.508, 0.613, 0.851, 0.732, 0.828, 0.615, 0.804, 0.685, 0.583]
    # From Hsu et al. 2013 (CFD scoring matrix, simplified)

    if not mismatch_positions:
        return 1.0  # Perfect match = highest risk

    score = 1.0
    for pos in mismatch_positions:
        if 0 <= pos < 20:
            score *= (1 - weights[pos])

    # Penalty for consecutive mismatches
    sorted_pos = sorted(mismatch_positions)
    for i in range(len(sorted_pos) - 1):
        if sorted_pos[i+1] - sorted_pos[i] == 1:
            score *= 0.5  # Consecutive mismatches reduce cutting

    return round(score, 4)

def aggregate_off_target_score(guide_sequence, off_targets_df):
    """Calculate aggregate off-target score for a guide.

    Parameters
    ----------
    guide_sequence : str
        20-nt guide sequence.
    off_targets_df : pd.DataFrame
        Output from run_cas_offinder.

    Returns
    -------
    dict with aggregate specificity metrics.
    """
    total_risk = 0
    high_risk_sites = 0

    for _, row in off_targets_df.iterrows():
        ot_seq = row['off_target_seq'][:20]
        mm_positions = [i for i in range(20) if guide_sequence[i] != ot_seq[i]]
        risk = score_off_target_risk(guide_sequence, ot_seq, mm_positions)
        total_risk += risk
        if risk > 0.1:
            high_risk_sites += 1

    # MIT specificity score (Hsu et al. 2013)
    specificity = 100 / (100 + total_risk) * 100

    result = {
        'guide': guide_sequence,
        'total_off_targets': len(off_targets_df),
        'high_risk_sites': high_risk_sites,
        'aggregate_risk': total_risk,
        'specificity_score': round(specificity, 1),
    }

    print(f"\nOff-target summary for {guide_sequence}:")
    print(f"  Total OT sites: {result['total_off_targets']}")
    print(f"  High-risk sites (score > 0.1): {result['high_risk_sites']}")
    print(f"  Specificity score: {result['specificity_score']}%")
    risk_level = "LOW" if specificity > 80 else "MODERATE" if specificity > 50 else "HIGH"
    print(f"  Risk level: {risk_level}")

    return result
```

**Key parameters**: `max_mismatches=4` covers most detectable off-targets. The seed region (positions 1-12 from PAM) is most critical for specificity. MIT specificity score >80% indicates low off-target risk. For clinical applications, use max_mismatches=3 and require specificity >90%.

**Expected output**: List of genome-wide off-target sites with mismatch counts and risk scores. Aggregate specificity score for each guide to inform selection.

---

## 3. GC Content and Secondary Structure Filtering

Filter guide RNA candidates by GC content, secondary structure, and sequence features.

```python
import numpy as np
import pandas as pd

def filter_guides_by_sequence_features(guides, min_gc=0.4, max_gc=0.7,
                                        max_homopolymer=4, check_structure=True):
    """Filter guide RNAs by GC content, homopolymers, and secondary structure.

    Parameters
    ----------
    guides : list of str
        20-nt guide RNA sequences.
    min_gc : float
        Minimum GC fraction (default 0.4).
    max_gc : float
        Maximum GC fraction (default 0.7).
    max_homopolymer : int
        Maximum allowed homopolymer run length (default 4).
    check_structure : bool
        Check for self-complementary regions that form hairpins.

    Returns
    -------
    pd.DataFrame with filter results per guide.
    """
    results = []

    for guide in guides:
        guide = guide.upper()
        gc = (guide.count('G') + guide.count('C')) / len(guide)

        # Homopolymer check
        max_run = 1
        current_run = 1
        for i in range(1, len(guide)):
            if guide[i] == guide[i-1]:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 1

        # Poly-T terminator (Pol III)
        has_polyt = 'TTTT' in guide

        # Self-complementarity check (simplified hairpin detection)
        has_hairpin = False
        if check_structure:
            complement = str.maketrans('ACGT', 'TGCA')
            for stem_len in range(4, 8):
                for i in range(len(guide) - 2 * stem_len - 3):
                    left = guide[i:i+stem_len]
                    # Check if reverse complement exists downstream (with 3+ nt loop)
                    right_rc = guide[i+stem_len+3:].translate(complement)[::-1]
                    if left in right_rc:
                        has_hairpin = True
                        break
                if has_hairpin:
                    break

        # Dinucleotide repeat check (e.g., ATATAT)
        has_dinuc_repeat = False
        for i in range(len(guide) - 5):
            dinuc = guide[i:i+2]
            if guide[i:i+6] == dinuc * 3:
                has_dinuc_repeat = True
                break

        # Filter decisions
        gc_pass = min_gc <= gc <= max_gc
        homo_pass = max_run <= max_homopolymer and not has_polyt
        structure_pass = not has_hairpin
        dinuc_pass = not has_dinuc_repeat

        all_pass = gc_pass and homo_pass and structure_pass and dinuc_pass

        results.append({
            'guide': guide,
            'gc': gc,
            'max_homopolymer': max_run,
            'has_poly_T': has_polyt,
            'has_hairpin': has_hairpin,
            'has_dinuc_repeat': has_dinuc_repeat,
            'gc_pass': gc_pass,
            'homo_pass': homo_pass,
            'structure_pass': structure_pass,
            'all_pass': all_pass,
        })

    df = pd.DataFrame(results)

    print(f"Guide RNA sequence filtering:")
    print(f"  Total guides: {len(df)}")
    print(f"  GC filter pass: {df['gc_pass'].sum()}")
    print(f"  Homopolymer pass: {df['homo_pass'].sum()}")
    print(f"  Structure pass: {df['structure_pass'].sum()}")
    print(f"  ALL filters pass: {df['all_pass'].sum()}")

    return df

# Example
test_guides = [
    "GCTAGCTAGCTAGCTAGCTA",  # 50% GC, should pass
    "GGGGCCCCGGGGCCCCGGGG",  # 100% GC, fail
    "ATATATATATATATATATAT",  # 0% GC, fail + dinuc repeat
    "GCTAGCTTTTGCTAGCTAAG",  # Has poly-T, fail
    "GCATGCATGCATGCATGCAT",  # 50% GC, should pass
]
result = filter_guides_by_sequence_features(test_guides)
```

**Key parameters**: Optimal GC range is 40-70% (below 30% or above 80% reduces activity). Poly-T runs (TTTT+) terminate Pol III transcription and must be excluded. Hairpin structures reduce guide loading into Cas9.

**Expected output**: Per-guide filter results showing GC content, homopolymer status, structure issues, and overall pass/fail.

---

## 4. Guide RNA Library Design for Genome-Wide Screens

Design and validate a genome-wide sgRNA library referencing Brunello/TKOv3 standards.

```python
import pandas as pd
import numpy as np

def design_genome_wide_library(gene_list, guides_per_gene=4, library_type="knockout",
                                reference_library="brunello"):
    """Design a genome-wide CRISPR screen library.

    Parameters
    ----------
    gene_list : list of str
        Target gene symbols.
    guides_per_gene : int
        Number of guides per gene (typically 4-6).
    library_type : str
        'knockout' (SpCas9), 'CRISPRi' (dCas9-KRAB), 'CRISPRa' (dCas9-VP64).
    reference_library : str
        'brunello' (Doench 2016, 4 guides/gene, human),
        'tkov3' (Hart 2017, 4 guides/gene, human),
        'brie' (Doench 2016, 4 guides/gene, mouse).

    Returns
    -------
    dict with library design specifications and QC metrics.
    """
    # Reference library statistics
    ref_stats = {
        'brunello': {
            'organism': 'human', 'genes': 19114, 'guides_per_gene': 4,
            'total_guides': 76441, 'ntc_guides': 1000,
            'targeting_strategy': 'Rule Set 2 top-scoring constitutive exons',
        },
        'tkov3': {
            'organism': 'human', 'genes': 18053, 'guides_per_gene': 4,
            'total_guides': 70948, 'ntc_guides': 142,
            'targeting_strategy': 'Optimized from TKOv1/v2 screening data',
        },
        'brie': {
            'organism': 'mouse', 'genes': 19674, 'guides_per_gene': 4,
            'total_guides': 78637, 'ntc_guides': 1000,
            'targeting_strategy': 'Rule Set 2 top-scoring constitutive exons',
        },
    }

    ref = ref_stats.get(reference_library, ref_stats['brunello'])

    # Library composition
    n_targeting = len(gene_list) * guides_per_gene
    n_ntc = max(100, int(n_targeting * 0.01))  # 1% NTCs or minimum 100
    n_positive_ctrl = 50  # Core essential gene guides for QC
    total_guides = n_targeting + n_ntc + n_positive_ctrl

    # Guide design rules by library type
    design_rules = {
        'knockout': {
            'target_region': 'Constitutive exons, first 50% of CDS',
            'avoid': 'First exon (incomplete KO), last exon, intron-exon junctions',
            'pam': 'NGG (SpCas9)',
            'guide_length': 20,
        },
        'CRISPRi': {
            'target_region': 'TSS -50 to +300 bp (promoter/5UTR)',
            'avoid': 'Regions >500 bp from TSS',
            'pam': 'NGG (dCas9-KRAB)',
            'guide_length': 20,
        },
        'CRISPRa': {
            'target_region': 'TSS -400 to -50 bp (upstream promoter)',
            'avoid': 'Regions overlapping TSS or downstream',
            'pam': 'NGG (dCas9-VP64/p65/Rta)',
            'guide_length': 20,
        },
    }

    rules = design_rules[library_type]

    # Coverage calculations
    cells_per_guide_500x = total_guides * 500
    cells_per_guide_1000x = total_guides * 1000
    moi = 0.3

    cells_needed_500x = int(cells_per_guide_500x / moi)
    cells_needed_1000x = int(cells_per_guide_1000x / moi)

    result = {
        'library_type': library_type,
        'reference_library': reference_library,
        'n_genes': len(gene_list),
        'guides_per_gene': guides_per_gene,
        'n_targeting_guides': n_targeting,
        'n_ntc_guides': n_ntc,
        'n_positive_controls': n_positive_ctrl,
        'total_guides': total_guides,
        'design_rules': rules,
        'cells_for_500x': cells_needed_500x,
        'cells_for_1000x': cells_needed_1000x,
    }

    print(f"Genome-wide CRISPR library design:")
    print(f"  Type: {library_type} | Reference: {reference_library}")
    print(f"  Target genes: {len(gene_list):,}")
    print(f"  Guides/gene: {guides_per_gene}")
    print(f"  Targeting guides: {n_targeting:,}")
    print(f"  Non-targeting controls: {n_ntc}")
    print(f"  Positive controls: {n_positive_ctrl}")
    print(f"  Total library size: {total_guides:,}")
    print(f"\n  Target region: {rules['target_region']}")
    print(f"  Avoid: {rules['avoid']}")
    print(f"  PAM: {rules['pam']}")
    print(f"\n  Cell requirements (MOI=0.3):")
    print(f"    500x coverage: {cells_needed_500x:,} cells at infection")
    print(f"    1000x coverage: {cells_needed_1000x:,} cells at infection")

    return result

# Example: design a genome-wide knockout library
import json
gene_list = [f"GENE_{i}" for i in range(19000)]  # Replace with actual gene list
library = design_genome_wide_library(gene_list, guides_per_gene=4, library_type="knockout")
```

**Key parameters**: Brunello (human) and Brie (mouse) are the gold-standard libraries for knockout screens. TKOv3 is optimized for essentiality screens. Always include non-targeting controls (1% of library) and positive controls (core essential genes). MOI 0.3-0.5 ensures single-guide-per-cell.

**Expected output**: Complete library specification with guide counts, design rules, and cell requirements for desired coverage.

---

## 5. Delivery Method Selection Decision Tree

Select optimal CRISPR delivery method based on experimental requirements.

```python
def select_delivery_method(application, cell_type, scale, duration="stable",
                            off_target_tolerance="low", budget="moderate"):
    """Select CRISPR delivery method based on experimental requirements.

    Parameters
    ----------
    application : str
        'screen' (pooled library), 'arrayed' (individual guides),
        'therapeutic' (clinical), 'validation' (single gene).
    cell_type : str
        'cell_line', 'primary_cells', 'stem_cells', 'in_vivo', 'organoid'.
    scale : str
        'single_gene', 'small_panel' (<100), 'large_panel' (100-1000),
        'genome_wide' (>1000).
    duration : str
        'stable' (permanent integration) or 'transient' (temporary).
    off_target_tolerance : str
        'high' (screening OK), 'low' (clinical grade), 'medium'.
    budget : str
        'low', 'moderate', 'high'.

    Returns
    -------
    dict with recommended delivery method and protocol parameters.
    """
    methods = {
        'lentiviral': {
            'integration': 'stable',
            'off_target': 'moderate',
            'throughput': 'genome-wide',
            'cost_per_guide': 'low (pooled)',
            'cell_types': ['cell_line', 'primary_cells', 'stem_cells', 'organoid'],
            'advantages': 'Stable integration, pooled screening, uniform MOI control',
            'disadvantages': 'Insertional mutagenesis, biosafety level 2, long prep time',
            'timeline': '2-3 weeks (virus production + transduction + selection)',
        },
        'RNP_electroporation': {
            'integration': 'transient',
            'off_target': 'very low',
            'throughput': 'single to small panel',
            'cost_per_guide': 'high ($50-200/guide)',
            'cell_types': ['cell_line', 'primary_cells', 'stem_cells', 'in_vivo'],
            'advantages': 'Lowest off-target, no DNA integration, fast clearance',
            'disadvantages': 'Expensive for large scale, transient only, cell death from EP',
            'timeline': '1-2 days',
        },
        'plasmid_transfection': {
            'integration': 'transient (mostly)',
            'off_target': 'moderate-high',
            'throughput': 'single to large panel',
            'cost_per_guide': 'very low ($5-10/guide)',
            'cell_types': ['cell_line'],
            'advantages': 'Cheapest, easy to prepare, scalable',
            'disadvantages': 'High off-target (prolonged expression), variable efficiency',
            'timeline': '1-3 days',
        },
        'AAV': {
            'integration': 'episomal (mostly)',
            'off_target': 'moderate',
            'throughput': 'single to small panel',
            'cost_per_guide': 'very high',
            'cell_types': ['in_vivo', 'primary_cells', 'organoid'],
            'advantages': 'In vivo delivery, tissue tropism with serotypes',
            'disadvantages': 'Size limit (~4.7 kb), immune response, expensive',
            'timeline': '4-8 weeks (production + injection)',
        },
    }

    # Decision logic
    recommended = []

    if application == 'screen' and scale == 'genome_wide':
        recommended.append('lentiviral')
    elif application == 'therapeutic' or off_target_tolerance == 'low':
        recommended.append('RNP_electroporation')
        if cell_type == 'in_vivo':
            recommended.append('AAV')
    elif application == 'validation' and cell_type == 'cell_line':
        if budget == 'low':
            recommended.append('plasmid_transfection')
        else:
            recommended.append('RNP_electroporation')
    elif application == 'arrayed':
        recommended.append('RNP_electroporation')
        recommended.append('plasmid_transfection')
    else:
        # Default ranking
        if cell_type == 'in_vivo':
            recommended = ['AAV', 'RNP_electroporation']
        elif duration == 'stable':
            recommended = ['lentiviral']
        else:
            recommended = ['RNP_electroporation', 'plasmid_transfection']

    print(f"CRISPR Delivery Method Selection:")
    print(f"  Application: {application}")
    print(f"  Cell type: {cell_type}")
    print(f"  Scale: {scale}")
    print(f"  Duration: {duration}")
    print(f"  Off-target tolerance: {off_target_tolerance}")
    print(f"\nRecommended method(s):")
    for i, method_name in enumerate(recommended, 1):
        m = methods[method_name]
        print(f"\n  #{i}: {method_name.upper()}")
        print(f"    Integration: {m['integration']}")
        print(f"    Off-target risk: {m['off_target']}")
        print(f"    Cost/guide: {m['cost_per_guide']}")
        print(f"    Timeline: {m['timeline']}")
        print(f"    Advantages: {m['advantages']}")
        print(f"    Disadvantages: {m['disadvantages']}")

    return {'recommended': recommended, 'details': {r: methods[r] for r in recommended}}

# Example selections
select_delivery_method('screen', 'cell_line', 'genome_wide')
select_delivery_method('therapeutic', 'primary_cells', 'single_gene', off_target_tolerance='low')
select_delivery_method('validation', 'cell_line', 'single_gene', budget='low')
```

**Key parameters**: Lentiviral is standard for pooled screens (stable integration, MOI control). RNP electroporation has the lowest off-target profile (protein degrades in 24-48h). Plasmid transfection is cheapest but has higher off-target rates due to prolonged Cas9 expression.

**Expected output**: Ranked delivery method recommendations with protocol parameters, cost estimates, and timeline for each option.

---

## 6. Lentiviral Packaging Protocol

Design lentiviral packaging experiments with optimized parameters.

```python
def lentiviral_packaging_protocol(transfer_vector, scale="6_well",
                                    generation="3rd", titer_method="qPCR"):
    """Generate lentiviral packaging protocol with optimized parameters.

    Parameters
    ----------
    transfer_vector : str
        Name of transfer vector (e.g., 'lentiCRISPRv2', 'pLKO.1').
    scale : str
        '6_well', '10cm', 'T75', 'T175'.
    generation : str
        '2nd' or '3rd' (3rd gen is safer, requires 3 helper plasmids).
    titer_method : str
        'qPCR', 'FACS', 'puromycin_selection'.

    Returns
    -------
    dict with complete packaging protocol.
    """
    scales = {
        '6_well': {'area_cm2': 9.6, 'media_ml': 2, 'cells': 0.8e6, 'dna_ug': 2.5},
        '10cm': {'area_cm2': 78.5, 'media_ml': 10, 'cells': 5e6, 'dna_ug': 20},
        'T75': {'area_cm2': 75, 'media_ml': 10, 'cells': 5e6, 'dna_ug': 20},
        'T175': {'area_cm2': 175, 'media_ml': 25, 'cells': 12e6, 'dna_ug': 50},
    }

    s = scales[scale]

    # DNA ratios for 3rd generation packaging
    if generation == '3rd':
        # Transfer : psPAX2 (packaging) : pMD2.G (envelope) : pRSV-Rev
        # Ratio: 4 : 3 : 1.5 : 1.5 (by mass)
        total_ratio = 4 + 3 + 1.5 + 1.5
        plasmids = {
            'transfer_vector': round(s['dna_ug'] * 4 / total_ratio, 2),
            'psPAX2_packaging': round(s['dna_ug'] * 3 / total_ratio, 2),
            'pMD2.G_envelope': round(s['dna_ug'] * 1.5 / total_ratio, 2),
            'pRSV_Rev': round(s['dna_ug'] * 1.5 / total_ratio, 2),
        }
    else:
        # 2nd generation: Transfer : psPAX2 : pMD2.G = 4:3:2
        total_ratio = 4 + 3 + 2
        plasmids = {
            'transfer_vector': round(s['dna_ug'] * 4 / total_ratio, 2),
            'psPAX2_packaging': round(s['dna_ug'] * 3 / total_ratio, 2),
            'pMD2.G_envelope': round(s['dna_ug'] * 2 / total_ratio, 2),
        }

    protocol = {
        'scale': scale,
        'generation': generation,
        'transfer_vector': transfer_vector,
        'plasmid_amounts_ug': plasmids,
        'total_dna_ug': s['dna_ug'],
    }

    print(f"Lentiviral Packaging Protocol ({generation} generation)")
    print(f"{'=' * 60}")
    print(f"Transfer vector: {transfer_vector}")
    print(f"Scale: {scale} (area: {s['area_cm2']} cm2)")
    print(f"\nDay -1: Seed HEK293T/Lenti-X cells")
    print(f"  Cells: {s['cells']:.1e} in {s['media_ml']} mL complete DMEM + 10% FBS")
    print(f"  Target: 70-80% confluency at transfection")
    print(f"\nDay 0: Transfection (PEI or Lipofectamine 3000)")
    print(f"  Total DNA: {s['dna_ug']} ug")
    for name, amount in plasmids.items():
        print(f"    {name}: {amount} ug")
    print(f"  PEI (1 mg/mL): {s['dna_ug'] * 3} uL (3:1 PEI:DNA ratio)")
    print(f"  Mix DNA + PEI in {s['media_ml'] * 0.1:.1f} mL OptiMEM, vortex, 15 min RT")
    print(f"  Add dropwise to cells")
    print(f"\nDay 1: Media change")
    print(f"  Replace with fresh DMEM + 10% FBS + 1% BSA (reduces aggregation)")
    print(f"  Optional: add 10 mM sodium butyrate (enhances expression, remove after 4h)")
    print(f"\nDay 2: First harvest (48h)")
    print(f"  Collect supernatant, replace with fresh media")
    print(f"  Filter: 0.45 um PES filter (NOT cellulose acetate)")
    print(f"  Store at 4C")
    print(f"\nDay 3: Second harvest (72h)")
    print(f"  Collect supernatant, filter 0.45 um")
    print(f"  Pool with Day 2 harvest")
    print(f"\nConcentration (optional, for high-titer needs):")
    print(f"  Ultracentrifugation: 25,000 rpm, 2h, 4C, SW28 rotor")
    print(f"  OR Lenti-X concentrator: mix 1:3, incubate 4C overnight, spin 1500g 45min")
    print(f"  Resuspend pellet in 1/100 original volume")
    print(f"\nTiter determination ({titer_method}):")
    if titer_method == 'qPCR':
        print(f"  Extract genomic DNA from transduced cells (Day 3 post-transduction)")
        print(f"  qPCR with WPRE or psi primers vs genomic reference (albumin)")
        print(f"  Expected titer: 10^6-10^8 TU/mL (unconcentrated)")
    print(f"\nTransduction for screen:")
    print(f"  MOI target: 0.3-0.5 (ensures single guide per cell)")
    print(f"  MOI = (titer * volume) / cell_number")
    print(f"  Add polybrene: 8 ug/mL (reduces charge repulsion)")
    print(f"  Spinoculation: 1000g, 1h, 32C (optional, improves efficiency)")
    print(f"  Begin puromycin selection 24-48h post-transduction (1-3 ug/mL)")

    return protocol

# Example
protocol = lentiviral_packaging_protocol('lentiCRISPRv2', scale='10cm', generation='3rd')
```

**Key parameters**: 3rd generation packaging is safer (self-inactivating, split packaging). PEI:DNA ratio of 3:1 is cost-effective; Lipofectamine 3000 gives higher titer. 0.45 um PES filters preserve titer better than 0.22 um. MOI 0.3-0.5 for screens.

**Expected output**: Complete day-by-day protocol with plasmid amounts, media volumes, concentration steps, and titering instructions.

---

## 7. RNP Electroporation Protocol: Cas9 + Synthetic sgRNA

Design RNP electroporation experiments for high-efficiency, low off-target editing.

```python
def rnp_electroporation_protocol(cell_type, cas9_source="IDT", guide_format="synthetic_sgRNA",
                                   nucleofector_program=None):
    """Generate RNP electroporation protocol with Lonza 4D-Nucleofector parameters.

    Parameters
    ----------
    cell_type : str
        'HEK293', 'K562', 'Jurkat', 'T_cells', 'iPSC', 'HSC', 'primary_fibroblast'.
    cas9_source : str
        'IDT' (Alt-R), 'Synthego', 'in_house'.
    guide_format : str
        'synthetic_sgRNA' (full-length), 'crRNA_tracrRNA' (two-part).
    nucleofector_program : str or None
        Override default program (e.g., 'CM-130' for T cells).

    Returns
    -------
    dict with complete RNP electroporation protocol.
    """
    # Lonza 4D-Nucleofector optimized programs
    cell_params = {
        'HEK293': {
            'program': 'CM-130', 'solution': 'SF', 'cells_per_rxn': 200000,
            'recovery': '24h', 'expected_efficiency': '80-95%',
        },
        'K562': {
            'program': 'FF-120', 'solution': 'SF', 'cells_per_rxn': 200000,
            'recovery': '24h', 'expected_efficiency': '85-95%',
        },
        'Jurkat': {
            'program': 'CL-120', 'solution': 'SE', 'cells_per_rxn': 200000,
            'recovery': '24-48h', 'expected_efficiency': '70-90%',
        },
        'T_cells': {
            'program': 'EO-115', 'solution': 'P3', 'cells_per_rxn': 1000000,
            'recovery': '48-72h', 'expected_efficiency': '70-90%',
        },
        'iPSC': {
            'program': 'CA-137', 'solution': 'P3', 'cells_per_rxn': 500000,
            'recovery': '48h', 'expected_efficiency': '60-85%',
        },
        'HSC': {
            'program': 'DZ-100', 'solution': 'P3', 'cells_per_rxn': 200000,
            'recovery': '48h', 'expected_efficiency': '50-80%',
        },
        'primary_fibroblast': {
            'program': 'CM-150', 'solution': 'P2', 'cells_per_rxn': 500000,
            'recovery': '48h', 'expected_efficiency': '40-70%',
        },
    }

    params = cell_params.get(cell_type, cell_params['HEK293'])
    if nucleofector_program:
        params['program'] = nucleofector_program

    # RNP complex amounts (per 20 uL reaction)
    cas9_pmol = 100  # 100 pmol Cas9 per reaction
    guide_pmol = 120  # 1.2x molar excess of guide
    cas9_ug = cas9_pmol * 0.16  # ~160 kDa Cas9

    protocol = {
        'cell_type': cell_type,
        'nucleofector_program': params['program'],
        'solution': params['solution'],
        'cas9_pmol': cas9_pmol,
        'guide_pmol': guide_pmol,
    }

    print(f"RNP Electroporation Protocol")
    print(f"{'=' * 60}")
    print(f"Cell type: {cell_type}")
    print(f"Expected efficiency: {params['expected_efficiency']}")
    print(f"\n1. RNP Complex Assembly (prepare on ice):")
    print(f"   Cas9 protein ({cas9_source}): {cas9_pmol} pmol ({cas9_ug:.1f} ug)")
    if guide_format == 'synthetic_sgRNA':
        print(f"   Synthetic sgRNA: {guide_pmol} pmol (1.2:1 guide:Cas9 ratio)")
        print(f"   Mix Cas9 + sgRNA in 5 uL total (PBS or nuclease-free water)")
    else:
        print(f"   crRNA: {guide_pmol} pmol")
        print(f"   tracrRNA: {guide_pmol} pmol")
        print(f"   Pre-anneal crRNA + tracrRNA: 95C 5min, cool to RT (20 min)")
        print(f"   Then add Cas9, mix in 5 uL total")
    print(f"   Incubate RT for 10-15 min to form RNP complex")
    print(f"\n2. Cell Preparation:")
    print(f"   Cells per reaction: {params['cells_per_rxn']:,}")
    print(f"   Wash with PBS (no serum)")
    print(f"   Resuspend in {params['solution']} nucleofection solution (20 uL per rxn)")
    print(f"   Add 5 uL RNP complex to 20 uL cell suspension")
    print(f"\n3. Nucleofection:")
    print(f"   Lonza 4D-Nucleofector program: {params['program']}")
    print(f"   Cuvette: 16-well Nucleocuvette Strip (20 uL)")
    print(f"   Run program immediately after adding cells")
    print(f"\n4. Recovery:")
    print(f"   Add 100 uL pre-warmed complete media to cuvette")
    print(f"   Wait 10 min in incubator (37C)")
    print(f"   Transfer to 96-well or 24-well plate with full media")
    print(f"   Recovery time: {params['recovery']}")
    print(f"\n5. Analysis (48-72h post-electroporation):")
    print(f"   Extract genomic DNA (QuickExtract or column)")
    print(f"   PCR amplify target locus (250-400 bp amplicon)")
    print(f"   Quantify editing: T7EI, Sanger + ICE, or amplicon-seq + CRISPResso2")
    print(f"\nControls:")
    print(f"   - Cas9 only (no guide): assess toxicity of protein delivery")
    print(f"   - RNP with non-targeting guide: assess guide-independent effects")
    print(f"   - Unelectroporated cells: baseline for cell health")

    return protocol

# Example
rnp_electroporation_protocol('T_cells', cas9_source='IDT', guide_format='synthetic_sgRNA')
rnp_electroporation_protocol('iPSC', nucleofector_program='CA-137')
```

**Key parameters**: 100 pmol Cas9 + 120 pmol sgRNA per 20 uL reaction is standard. 1.2:1 guide:Cas9 molar ratio ensures complete complex formation. Nucleofector programs are cell-type-specific and critical for efficiency/viability tradeoff.

**Expected output**: Step-by-step RNP electroporation protocol with optimized parameters, Lonza programs, and expected efficiency for each cell type.

---

## 8. Selection and Enrichment Protocols

Design puromycin selection timelines and FACS sorting strategies for CRISPR screens.

```python
def selection_protocol(selection_type, cell_type="generic", puromycin_conc=None):
    """Design selection and enrichment protocol for CRISPR screen.

    Parameters
    ----------
    selection_type : str
        'puromycin' (antibiotic selection), 'FACS_reporter' (fluorescent sorting),
        'FACS_surface' (antibody-based), 'drug_treatment' (resistance screen).
    cell_type : str
        Cell line name for puromycin kill curve reference.
    puromycin_conc : float or None
        Override puromycin concentration (ug/mL). If None, uses default for cell type.

    Returns
    -------
    dict with selection protocol parameters.
    """
    # Typical puromycin concentrations by cell type
    puro_defaults = {
        'HEK293T': 2.0, 'HeLa': 1.0, 'A549': 1.5, 'K562': 2.0,
        'MCF7': 1.0, 'U2OS': 2.0, 'RPE1': 10.0, 'generic': 2.0,
    }

    if selection_type == 'puromycin':
        conc = puromycin_conc or puro_defaults.get(cell_type, 2.0)

        print(f"Puromycin Selection Protocol")
        print(f"{'=' * 60}")
        print(f"Cell type: {cell_type}")
        print(f"Puromycin concentration: {conc} ug/mL")
        print(f"\nPre-requisite: Determine kill curve BEFORE screen")
        print(f"  Test: 0, 0.5, 1, 2, 3, 5, 10 ug/mL puromycin")
        print(f"  Duration: 48-72h")
        print(f"  Select lowest concentration that kills 100% untransduced cells")
        print(f"\nTimeline:")
        print(f"  Day 0: Transduction (MOI 0.3-0.5)")
        print(f"  Day 1: Media change (remove virus)")
        print(f"  Day 2: Begin puromycin selection ({conc} ug/mL)")
        print(f"  Day 2-5: Selection (replace puro media every 2 days)")
        print(f"  Day 5-7: Selection complete (confirm by uninfected control death)")
        print(f"  Day 7: Remove puromycin, begin experiment")
        print(f"  Day 7-21: Culture under experimental conditions (maintain 500x coverage)")
        print(f"  Day 21: Harvest cells, extract genomic DNA")
        print(f"\nCritical checkpoints:")
        print(f"  - Day 3: uninfected control should be >90% dead")
        print(f"  - Day 5-7: count surviving cells, verify >= 500x library coverage")
        print(f"  - Passage: never let cells overgrow (split at 80% confluency)")
        print(f"  - Maintain >=500 cells per guide throughout experiment")

    elif selection_type == 'FACS_reporter':
        print(f"FACS Reporter Screen Protocol")
        print(f"{'=' * 60}")
        print(f"\nLibrary transduction:")
        print(f"  MOI: 0.3, maintain 500x coverage")
        print(f"  Select with puromycin (see puromycin protocol)")
        print(f"\nReporter induction:")
        print(f"  Stimulate cells to activate reporter pathway")
        print(f"  Wait for reporter expression (4-24h depending on reporter)")
        print(f"\nFACS sorting:")
        print(f"  Sort top 10% (reporter HIGH) and bottom 10% (reporter LOW)")
        print(f"  Collect >= 3 million cells per bin (for 60k-guide library)")
        print(f"  Use untransduced reporter cells to set gates")
        print(f"  Include unsorted population as reference")
        print(f"\nGenomic DNA extraction and sequencing:")
        print(f"  Extract gDNA from each sorted bin")
        print(f"  PCR amplify guide region (use screen-specific primers)")
        print(f"  Sequence at >= 500x coverage per bin")
        print(f"\nAnalysis:")
        print(f"  Compare guide abundance in HIGH vs LOW bins")
        print(f"  Genes enriched in HIGH bin: positive regulators")
        print(f"  Genes enriched in LOW bin: negative regulators / required for expression")

    elif selection_type == 'drug_treatment':
        print(f"Drug Resistance Screen Protocol")
        print(f"{'=' * 60}")
        print(f"\nLibrary transduction and selection (Days 0-7):")
        print(f"  Standard lentiviral transduction + puromycin selection")
        print(f"\nDrug treatment (Days 7-21+):")
        print(f"  Determine IC50/IC90 of drug in parental cells FIRST")
        print(f"  Treat library cells at IC90 concentration")
        print(f"  Duration: 10-21 days (until resistant colonies emerge)")
        print(f"  Replace drug-containing media every 3-4 days")
        print(f"  Maintain untreated control population in parallel")
        print(f"\nHarvest:")
        print(f"  Treated population: survivors = enriched for resistance genes")
        print(f"  Untreated control: reference for guide abundance")
        print(f"  Extract gDNA, PCR, sequence")
        print(f"\nAnalysis:")
        print(f"  Enriched guides in treated vs untreated = resistance genes")
        print(f"  Depleted guides in treated vs untreated = sensitizer genes")

    return {'selection_type': selection_type, 'cell_type': cell_type}

# Example protocols
selection_protocol('puromycin', cell_type='HeLa')
selection_protocol('FACS_reporter')
selection_protocol('drug_treatment')
```

**Key parameters**: Puromycin kill curve is essential before every screen (concentrations vary by cell line). FACS reporter screens: sort top/bottom 10% for maximum contrast. Drug resistance screens: use IC90 concentration to select for strong resistance phenotypes.

**Expected output**: Step-by-step selection timeline with checkpoints, cell number requirements, and analysis strategy for each screen type.

---

## 9. Validation Assays: T7 Endonuclease I and Sanger Sequencing + ICE/TIDE

Validate CRISPR editing at individual loci using mismatch detection and deconvolution.

```python
def t7_endonuclease_protocol(target_gene, amplicon_size_bp=600):
    """Generate T7 Endonuclease I mismatch detection protocol.

    Parameters
    ----------
    target_gene : str
        Name of the target gene.
    amplicon_size_bp : int
        Expected PCR amplicon size (400-800 bp optimal).

    Returns
    -------
    dict with protocol steps and analysis instructions.
    """
    print(f"T7 Endonuclease I (T7EI) Mismatch Detection Protocol")
    print(f"{'=' * 60}")
    print(f"Target gene: {target_gene}")
    print(f"Amplicon size: {amplicon_size_bp} bp")
    print(f"\n1. PCR Amplification:")
    print(f"   Design primers flanking cut site (200-400 bp on each side)")
    print(f"   Expected amplicon: ~{amplicon_size_bp} bp")
    print(f"   Use high-fidelity polymerase (Q5, Phusion, KAPA HiFi)")
    print(f"   PCR: 98C 30s -> 35 cycles (98C 10s, 60C 20s, 72C 30s) -> 72C 2min")
    print(f"   Verify single band on 1% agarose gel")
    print(f"   Clean up: column purification or bead cleanup")
    print(f"\n2. Heteroduplex Formation:")
    print(f"   Mix: 200 ng purified PCR product in 19 uL")
    print(f"   Add 2 uL NEB Buffer 2 (10x)")
    print(f"   Total volume: 20 uL")
    print(f"   Denature-reanneal program:")
    print(f"     95C 5 min -> ramp to 85C at -2C/s -> ramp to 25C at -0.1C/s")
    print(f"\n3. T7EI Digestion:")
    print(f"   Add 1 uL T7 Endonuclease I (NEB M0302)")
    print(f"   Incubate 37C for 15 min (do NOT exceed 30 min)")
    print(f"   Stop: add 1.5 uL 0.25 M EDTA")
    print(f"\n4. Analysis:")
    print(f"   Run on 2% agarose gel (or TapeStation/Bioanalyzer)")
    print(f"   Expected bands:")
    print(f"     Uncut: ~{amplicon_size_bp} bp (wild-type homoduplexes)")
    print(f"     Cut: two fragments summing to ~{amplicon_size_bp} bp")
    print(f"   Quantify: % editing = 100 * (1 - sqrt(1 - fraction_cut))")
    print(f"     where fraction_cut = (cut band intensities) / (cut + uncut)")
    print(f"\nLimitations:")
    print(f"   - Detection limit: ~5% editing")
    print(f"   - Semi-quantitative (gel densitometry variability)")
    print(f"   - Cannot distinguish indel types or sizes")
    print(f"   - For precise quantification, use Sanger + ICE or amplicon-seq")

    return {'target': target_gene, 'amplicon_bp': amplicon_size_bp}

def sanger_ice_tide_protocol(target_gene):
    """Generate Sanger sequencing + ICE/TIDE deconvolution protocol.

    ICE (Inference of CRISPR Edits): Synthego tool, free web interface.
    TIDE (Tracking of Indels by DEcomposition): desktop tool from Brinkman lab.

    Parameters
    ----------
    target_gene : str
        Name of the target gene.

    Returns
    -------
    dict with protocol steps.
    """
    print(f"Sanger Sequencing + ICE/TIDE Deconvolution Protocol")
    print(f"{'=' * 60}")
    print(f"Target gene: {target_gene}")
    print(f"\n1. PCR Amplification:")
    print(f"   Same as T7EI protocol (primers 200-400 bp from cut site)")
    print(f"   Amplicon size: 500-800 bp (must extend >200 bp past cut site)")
    print(f"   IMPORTANT: sequencing primer should be 100-200 bp from cut site")
    print(f"   (Not too close — need clean sequence before cut site for alignment)")
    print(f"\n2. Sanger Sequencing:")
    print(f"   Submit: purified PCR product + sequencing primer")
    print(f"   Sequence BOTH edited sample AND unedited wild-type control")
    print(f"   Wild-type control is REQUIRED for deconvolution")
    print(f"\n3. ICE Analysis (Synthego, https://ice.synthego.com):")
    print(f"   Upload: edited .ab1 trace + control .ab1 trace + guide sequence")
    print(f"   Output:")
    print(f"     - Overall editing efficiency (%)")
    print(f"     - Knockout score (% frameshifting indels)")
    print(f"     - Indel size distribution")
    print(f"     - Individual allele contributions")
    print(f"   Interpretation:")
    print(f"     - ICE score >70%: high editing, good for functional studies")
    print(f"     - KO score: most relevant for knockout experiments")
    print(f"     - R-squared >0.9: reliable deconvolution")
    print(f"\n4. TIDE Analysis (https://tide.nki.nl):")
    print(f"   Similar inputs and outputs to ICE")
    print(f"   Additionally provides:")
    print(f"     - Aberrant sequence signal (%)")
    print(f"     - p-value for each indel size")
    print(f"     - Decomposition window optimization")
    print(f"\nAdvantages over T7EI:")
    print(f"   - Quantitative (not semi-quantitative)")
    print(f"   - Resolves indel types and sizes")
    print(f"   - Distinguishes frameshifts from in-frame indels")
    print(f"   - Free, fast, no special reagents beyond Sanger sequencing")
    print(f"\nLimitations:")
    print(f"   - Detection limit: ~3-5% editing")
    print(f"   - Large deletions (>50 bp) may not decompose well")
    print(f"   - For heterogeneous populations, amplicon-seq is more precise")

    return {'target': target_gene, 'method': 'ICE/TIDE'}

# Example
t7_endonuclease_protocol('TP53', amplicon_size_bp=650)
sanger_ice_tide_protocol('TP53')
```

**Key parameters**: T7EI detection limit is ~5% editing; Sanger+ICE can detect ~3%. Sequencing primer should be 100-200 bp upstream of the cut site for clean deconvolution. Always include a wild-type control for ICE/TIDE analysis.

**Expected output**: Complete validation protocols with step-by-step instructions, expected results, and interpretation guidelines.

---

## 10. Next-Gen Validation: Amplicon-Seq with CRISPResso2

Quantify editing outcomes precisely using targeted amplicon sequencing.

```bash
# ---- CRISPResso2 amplicon analysis ----
# Install: pip install CRISPResso2

# Single sample analysis
CRISPResso \
    --fastq_r1 sample_R1.fastq.gz \
    --fastq_r2 sample_R2.fastq.gz \
    --amplicon_seq ATGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGC \
    --guide_seq GCTAGCTAGCTAGCTAGCTA \
    --output_folder crispresso_validation/ \
    --name TP53_guide1_sample1 \
    --quantification_window_size 10 \
    --min_average_read_quality 30 \
    --plot_window_size 40 \
    --max_rows_alleles_around_cut_to_plot 50
```

```python
import subprocess
import pandas as pd
import os

def run_crispresso2_validation(fastq_r1, fastq_r2, amplicon_seq, guide_seq,
                                sample_name, output_dir="crispresso_output",
                                quantification_window=10):
    """Run CRISPResso2 for precise editing quantification.

    Parameters
    ----------
    fastq_r1 : str
        Path to R1 FASTQ file.
    fastq_r2 : str
        Path to R2 FASTQ file (or None for single-end).
    amplicon_seq : str
        Full amplicon sequence (include primer-to-primer).
    guide_seq : str
        20-nt guide RNA sequence (without PAM).
    sample_name : str
        Sample identifier for output naming.
    output_dir : str
        Output directory.
    quantification_window : int
        Window size around cut site for quantification (default 10 bp).

    Returns
    -------
    dict with editing metrics.
    """
    cmd = [
        "CRISPResso",
        "--fastq_r1", fastq_r1,
        "--amplicon_seq", amplicon_seq,
        "--guide_seq", guide_seq,
        "--output_folder", output_dir,
        "--name", sample_name,
        "--quantification_window_size", str(quantification_window),
        "--min_average_read_quality", "30",
        "--min_single_bp_quality", "20",
        "--plot_window_size", "40",
        "--max_rows_alleles_around_cut_to_plot", "50",
    ]
    if fastq_r2:
        cmd.extend(["--fastq_r2", fastq_r2])

    print(f"Running CRISPResso2 for {sample_name}...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr[:500]}")
        return None

    # Parse results
    result_dir = os.path.join(output_dir, f"CRISPResso_on_{sample_name}")
    quant_file = os.path.join(result_dir,
                              "CRISPResso_quantification_of_editing_frequency.txt")

    if not os.path.exists(quant_file):
        print(f"Results not found at {quant_file}")
        return None

    quant = pd.read_csv(quant_file, sep='\t')

    metrics = {
        'sample': sample_name,
        'total_reads_aligned': quant['Reads_aligned'].sum(),
        'unmodified_pct': quant.loc[0, 'Unmodified%'] if 'Unmodified%' in quant.columns else None,
        'modified_pct': quant.loc[0, 'Modified%'] if 'Modified%' in quant.columns else None,
        'nhej_pct': quant.loc[0, 'NHEJ%'] if 'NHEJ%' in quant.columns else None,
    }

    print(f"\nCRISPResso2 Results for {sample_name}:")
    print(f"  Total aligned reads: {metrics['total_reads_aligned']:,}")
    print(f"  Unmodified: {metrics.get('unmodified_pct', 'N/A')}%")
    print(f"  Modified: {metrics.get('modified_pct', 'N/A')}%")
    print(f"  NHEJ: {metrics.get('nhej_pct', 'N/A')}%")
    print(f"\nOutput directory: {result_dir}")
    print(f"Key output files:")
    print(f"  - CRISPResso_quantification_of_editing_frequency.txt")
    print(f"  - Alleles_frequency_table.zip")
    print(f"  - CRISPResso_NHEJ_quantification.png")
    print(f"  - CRISPResso_pie_chart.png")

    return metrics

# Example
# run_crispresso2_validation(
#     "sample_R1.fastq.gz", "sample_R2.fastq.gz",
#     "ATGCTAGC...FULL_AMPLICON...GCTAGCTA",
#     "GCTAGCTAGCTAGCTAGCTA",
#     "TP53_guide1"
# )
print("Replace paths and sequences with actual experimental data.")
```

**Key parameters**: `quantification_window_size=10` captures most indels around the cut site (3 bp upstream of PAM). `min_average_read_quality=30` filters low-quality reads. Amplicon sequence must be primer-to-primer (include entire PCR product).

**Expected output**: Precise editing quantification with % unmodified, % NHEJ (insertions/deletions), allele frequency table, and publication-quality plots.

---

## 11. Base Editing Experiment Design: CBE and ABE

Design base editing experiments with optimal editor selection and editing window positioning.

```python
def design_base_editing_experiment(target_gene, target_mutation, genome_build="hg38"):
    """Design a base editing experiment for a specific target mutation.

    Parameters
    ----------
    target_gene : str
        Gene name.
    target_mutation : str
        Desired base change (e.g., 'C>T at chr17:7577121' or 'A>G at position 245').
    genome_build : str
        Reference genome.

    Returns
    -------
    dict with editor selection and guide design parameters.
    """
    # Base editor properties
    editors = {
        'BE4max': {
            'type': 'CBE', 'conversion': 'C->T (G->A on opposite strand)',
            'editing_window': 'positions 4-8 (counting from 5\' end of protospacer)',
            'pam': 'NGG (SpCas9)',
            'efficiency': '40-80%', 'indel_rate': '1-5%',
            'best_context': 'TC > CC > AC > GC',
            'use_when': 'C-to-T or G-to-A transitions',
        },
        'ABE8e': {
            'type': 'ABE', 'conversion': 'A->G (T->C on opposite strand)',
            'editing_window': 'positions 4-8 (counting from 5\' end of protospacer)',
            'pam': 'NGG (SpCas9)',
            'efficiency': '50-90%', 'indel_rate': '<1%',
            'best_context': 'TA > CA > AA > GA',
            'use_when': 'A-to-G or T-to-C transitions',
        },
        'BE4max-NG': {
            'type': 'CBE', 'conversion': 'C->T',
            'editing_window': 'positions 4-8',
            'pam': 'NG (SpCas9-NG, more flexible PAM)',
            'efficiency': '20-60%', 'indel_rate': '1-5%',
            'best_context': 'TC > CC > AC > GC',
            'use_when': 'C-to-T when NGG PAM not available',
        },
        'ABE8e-NG': {
            'type': 'ABE', 'conversion': 'A->G',
            'editing_window': 'positions 4-8',
            'pam': 'NG',
            'efficiency': '30-70%', 'indel_rate': '<1%',
            'best_context': 'TA > CA > AA > GA',
            'use_when': 'A-to-G when NGG PAM not available',
        },
    }

    print(f"Base Editing Experiment Design")
    print(f"{'=' * 60}")
    print(f"Target gene: {target_gene}")
    print(f"Desired mutation: {target_mutation}")
    print(f"\n--- Editor Selection Guide ---")
    print(f"\n{'Editor':<15} {'Type':<5} {'Conversion':<20} {'Window':<15} {'Efficiency':<12}")
    print("-" * 70)
    for name, e in editors.items():
        print(f"{name:<15} {e['type']:<5} {e['conversion']:<20} {e['editing_window']:<15} {e['efficiency']:<12}")

    print(f"\n--- Guide Design for Base Editing ---")
    print(f"\nCritical positioning rules:")
    print(f"  1. Target base must fall within editing window (positions 4-8)")
    print(f"     Position 1 = 5' end of protospacer (most distal from PAM)")
    print(f"     Position 20 = 3' end of protospacer (PAM-proximal)")
    print(f"  2. PAM (NGG) must be present at correct distance")
    print(f"  3. Multiple C's (CBE) or A's (ABE) in window cause bystander edits")
    print(f"\nBystander editing mitigation:")
    print(f"  - Ideal: only ONE target base in the editing window")
    print(f"  - If multiple bases in window: check if bystander edit is silent/tolerable")
    print(f"  - Consider narrow-window editors (YE1-BE4, ~2 nt window)")
    print(f"  - Consider different PAM variants to shift window position")
    print(f"\nControls for base editing experiments:")
    print(f"  - Non-targeting guide + editor: assess editor-dependent background")
    print(f"  - Cas9 nickase (editor without deaminase): assess nicking-only effects")
    print(f"  - Dead editor (catalytic mutant): assess binding-only effects")
    print(f"\nQuantification:")
    print(f"  - Sanger + EditR (base editing-specific deconvolution)")
    print(f"  - Amplicon-seq + CRISPResso2 (with --base_editor_output flag)")
    print(f"  - Report: target edit %, bystander edit %, indel %")

    return {'target_gene': target_gene, 'editors': editors}

# Example
design_base_editing_experiment('PCSK9', 'C>T to introduce W159X (nonsense)')
```

**Key parameters**: Editing window is positions 4-8 counting from the 5' end of the protospacer (PAM-distal). CBE converts C-to-T (best in TC context), ABE converts A-to-G (best in TA context). ABE8e has higher efficiency and lower indel rates than CBE. Bystander edits at other C/A positions within the window must be assessed.

**Expected output**: Editor selection guide, positioning rules, bystander edit considerations, control design, and quantification strategy.

---

## 12. Prime Editing: pegRNA Design

Design prime editing guide RNAs (pegRNAs) with optimized PBS and RT template lengths.

```python
def design_pegrna(target_sequence, edit_type, edit_position, new_sequence,
                   pbs_length_range=(10, 16), rt_template_range=(10, 20)):
    """Design pegRNA for prime editing.

    Parameters
    ----------
    target_sequence : str
        ~60 nt genomic sequence centered on the edit site.
    edit_type : str
        'substitution', 'insertion', 'deletion'.
    edit_position : int
        Position of edit within target_sequence (0-indexed).
    new_sequence : str
        Replacement sequence (for substitution/insertion).
    pbs_length_range : tuple
        Min and max primer binding site lengths to test.
    rt_template_range : tuple
        Min and max RT template lengths to test.

    Returns
    -------
    list of pegRNA designs ranked by predicted efficiency.
    """
    target = target_sequence.upper()

    print(f"Prime Editing pegRNA Design")
    print(f"{'=' * 60}")
    print(f"Edit type: {edit_type}")
    print(f"Target sequence (60 nt context):")
    print(f"  {target}")
    print(f"  {'':>{edit_position}}^ edit site")

    # Find NGG PAMs near edit site (nick must be within ~50 nt of edit)
    pam_positions = []
    for i in range(len(target) - 2):
        if target[i+1:i+3] == 'GG':
            # PAM is at i (N) + i+1,i+2 (GG)
            # Nick site is 3 bp upstream of PAM on the protospacer strand
            nick_pos = i - 3
            distance_to_edit = abs(nick_pos - edit_position)
            if distance_to_edit <= 50 and nick_pos >= 0:
                pam_positions.append({
                    'pam_start': i,
                    'nick_position': nick_pos,
                    'distance_to_edit': distance_to_edit,
                    'strand': '+',
                })

    # Also check reverse strand
    complement = str.maketrans('ACGT', 'TGCA')
    rev_target = target.translate(complement)[::-1]
    for i in range(len(rev_target) - 2):
        if rev_target[i+1:i+3] == 'GG':
            orig_pos = len(target) - i - 1
            nick_pos = orig_pos + 3
            distance_to_edit = abs(nick_pos - edit_position)
            if distance_to_edit <= 50 and nick_pos < len(target):
                pam_positions.append({
                    'pam_start': orig_pos,
                    'nick_position': nick_pos,
                    'distance_to_edit': distance_to_edit,
                    'strand': '-',
                })

    pam_positions.sort(key=lambda p: p['distance_to_edit'])

    print(f"\nCandidate PAM positions (sorted by distance to edit):")
    print(f"  {'PAM pos':>8} {'Nick pos':>9} {'Distance':>9} {'Strand':>7}")
    for p in pam_positions[:5]:
        print(f"  {p['pam_start']:>8} {p['nick_position']:>9} {p['distance_to_edit']:>9} {p['strand']:>7}")

    # Design pegRNAs for best PAM position
    designs = []
    if pam_positions:
        best_pam = pam_positions[0]
        nick = best_pam['nick_position']

        print(f"\n--- pegRNA designs for best PAM (nick at position {nick}) ---")
        print(f"\nPBS length optimization (recommended: 10-16 nt):")
        print(f"  Shorter PBS (10-12 nt): higher efficiency, risk of mispriming")
        print(f"  Longer PBS (14-16 nt): more specific, potentially lower efficiency")
        print(f"  Tm of PBS should be ~30C (for PE2) or ~35-40C (for PE3)")

        for pbs_len in range(pbs_length_range[0], pbs_length_range[1] + 1):
            for rt_len in range(rt_template_range[0], rt_template_range[1] + 1, 2):
                # PBS = complement of sequence upstream of nick
                pbs_start = nick - pbs_len
                if pbs_start < 0:
                    continue
                pbs_seq = target[pbs_start:nick]
                pbs_complement = pbs_seq.translate(complement)[::-1]

                # RT template = edited sequence downstream of nick
                rt_template_start = nick
                rt_template_end = min(nick + rt_len, len(target))
                rt_seq = target[rt_template_start:rt_template_end]

                # Apply edit to RT template
                if edit_type == 'substitution' and edit_position >= nick:
                    edit_offset = edit_position - nick
                    if edit_offset < len(rt_seq):
                        rt_seq = rt_seq[:edit_offset] + new_sequence + rt_seq[edit_offset+len(new_sequence):]

                rt_complement = rt_seq.translate(complement)[::-1]

                # GC content of PBS
                pbs_gc = (pbs_complement.count('G') + pbs_complement.count('C')) / len(pbs_complement)

                designs.append({
                    'pbs_length': pbs_len,
                    'rt_template_length': rt_len,
                    'pbs_sequence': pbs_complement,
                    'rt_template': rt_complement,
                    'pbs_gc': pbs_gc,
                })

        print(f"\nGenerated {len(designs)} pegRNA designs")
        print(f"\nTop designs (PBS 13 nt, varying RT):")
        print(f"  {'PBS len':>7} {'RT len':>7} {'PBS GC':>7}")
        print("  " + "-" * 25)
        for d in designs:
            if d['pbs_length'] == 13:
                print(f"  {d['pbs_length']:>7} {d['rt_template_length']:>7} {d['pbs_gc']:>6.0%}")

    print(f"\npegRNA structure (5' to 3'):")
    print(f"  [spacer (20 nt)] + [scaffold] + [RT template] + [PBS]")
    print(f"\nPE3 nicking guide:")
    print(f"  Design a second nicking guide 40-90 bp from the pegRNA nick")
    print(f"  On the non-edited strand (opposite strand from pegRNA)")
    print(f"  PE3 improves efficiency 2-5x over PE2 alone")
    print(f"\nPE3b (preferred when possible):")
    print(f"  Nicking guide overlaps the edit site")
    print(f"  Only nicks AFTER editing occurs (reduces indels)")
    print(f"\nControls:")
    print(f"  - pegRNA with scrambled RT template: assess nick-only effects")
    print(f"  - PE2 without nicking guide: baseline PE efficiency")
    print(f"  - Non-targeting pegRNA: assess PE-dependent background")

    return designs

# Example: design pegRNA for a C>T substitution
design_pegrna(
    target_sequence="ATGCTAGCTAGCTAGCTAGCTAGCNGGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTA",
    edit_type="substitution",
    edit_position=25,
    new_sequence="T",
)
```

**Key parameters**: PBS length 10-16 nt (13 nt is a good starting point). RT template 10-20 nt (longer needed for insertions). PE3 adds a nicking guide 40-90 bp away on the non-edited strand, improving efficiency 2-5x. PE3b is preferred when the nicking guide can overlap the edit site.

**Expected output**: Ranked pegRNA designs with PBS and RT template sequences, PE3 nicking guide positioning, and control experiment design.

---

## Quick Reference

| Task | Recipe | Key Tool/Method |
|------|--------|----------------|
| On-target scoring | #1 | Rule Set 2 / Azimuth heuristics |
| Off-target analysis | #2 | Cas-OFFinder + CFD scoring |
| Sequence filtering | #3 | GC content, poly-T, hairpin detection |
| Library design | #4 | Brunello/TKOv3/Brie reference |
| Delivery selection | #5 | Decision tree (lentiviral/RNP/plasmid/AAV) |
| Lentiviral packaging | #6 | 3rd gen packaging, MOI optimization |
| RNP electroporation | #7 | Lonza 4D-Nucleofector protocols |
| Selection/enrichment | #8 | Puromycin, FACS, drug treatment |
| T7EI/Sanger validation | #9 | T7EI mismatch, ICE/TIDE deconvolution |
| Amplicon-seq | #10 | CRISPResso2 quantification |
| Base editing design | #11 | CBE/ABE editor selection, window positioning |
| Prime editing design | #12 | pegRNA PBS/RT optimization, PE3 nicking |

---

## Cross-Skill Routing

- Screen data analysis (MAGeCK, RRA, gene scoring) --> [mageck-recipes.md](mageck-recipes.md) and parent [SKILL.md](SKILL.md)
- Pathway enrichment on screen hits --> `gene-enrichment` skill
- Target druggability for screen hits --> `drug-target-validator` skill
- Variant-level interpretation of edited loci --> `variant-analysis` skill
