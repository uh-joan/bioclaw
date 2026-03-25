---
name: enzyme-engineering
description: "Enzyme engineering, directed evolution, rational design, stability engineering, kinetic characterization, activity screening, immobilization, biocatalysis, cofactor regeneration, codon optimization, expression systems. Use when user mentions enzyme engineering, directed evolution, rational design, enzyme stability, thermostability, biocatalysis, enzyme kinetics, Michaelis-Menten, kcat, Km, substrate specificity, enzyme immobilization, cascade reactions, cofactor regeneration, codon optimization, error-prone PCR, DNA shuffling, PACE, PHAGE, CAST, ISM, LigandMPNN, RFdiffusion enzyme, ProteinMPNN enzyme, or industrial enzyme."
---

# Enzyme Engineering

> **ColabFold recipes**: See [colabfold-recipes.md](colabfold-recipes.md) for mutant stability screening, active site geometry validation, and directed evolution structural analysis via ColabFold.

Specialist skill for enzyme engineering, directed evolution, and rational design of industrial and research enzymes. Covers the full pipeline from target enzyme characterization through variant library design, stability engineering, activity screening, kinetic characterization, immobilization, and process optimization for biocatalysis. Integrates computational prediction tools (ESM, FoldX, Rosetta, LigandMPNN, RFdiffusion) with experimental design guidance for high-throughput screening and validation.

## Report-First Workflow

1. **Create report file immediately**: `[enzyme]_engineering_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## Cross-Reference: Other Skills

- **Antibody/biologics design, immunogenicity, CDR engineering** -> use protein-therapeutic-design skill
- **Protein structure retrieval and AlphaFold models** -> use alphafold-structures or pdb-structures skill
- **Structure prediction for engineered mutants** -> use colabfold-predict skill
- **Small molecule substrate analysis and ADMET** -> use medicinal-chemistry skill
- **Pathway context and gene enrichment** -> use systems-biology or gene-enrichment skill
- **Clinical pharmacology of enzyme therapeutics** -> use clinical-pharmacology skill

## When NOT to Use This Skill

- Antibody humanization, CDR grafting, or biologics CMC -> use `protein-therapeutic-design`
- De novo protein binder design (non-enzymatic) -> use `protein-therapeutic-design`
- Small molecule drug optimization -> use `medicinal-chemistry`
- Protein structure retrieval only (no engineering) -> use `pdb-structures` or `alphafold-structures`
- Gene expression analysis or transcriptomics -> use `rnaseq-analysis`

## Available MCP Tools

### `mcp__uniprot__uniprot_data` (Enzyme Sequence & Annotation)

| Method | Enzyme engineering use | Key parameters |
|--------|----------------------|----------------|
| `search_proteins` | Find enzyme by name, EC number, or keyword | `query`, `organism`, `size` |
| `get_protein_info` | Full enzyme profile: function, cofactors, catalytic activity | `accession`, `format` |
| `search_by_gene` | Find enzyme by gene name | `gene`, `organism`, `size` |
| `get_protein_sequence` | Get enzyme sequence for design input | `accession`, `format` |
| `get_protein_features` | Active site residues, metal binding, disulfides, PTMs | `accession` |
| `get_protein_structure` | Available PDB structures for the enzyme | `accession` |
| `get_protein_domains_detailed` | Domain architecture and catalytic domain boundaries | `accession` |
| `get_protein_variants` | Known natural variants and their functional effects | `accession` |
| `get_protein_homologs` | Homologous enzymes for consensus design input | `accession`, `organism`, `size` |
| `analyze_sequence_composition` | Amino acid composition analysis | `accession` |
| `compare_proteins` | Compare two enzyme sequences (wild-type vs engineered) | `accession1`, `accession2` |

### `mcp__pdb__pdb_data` (Experimental Enzyme Structures)

| Method | Enzyme engineering use | Key parameters |
|--------|----------------------|----------------|
| `search_structures` | Find enzyme crystal structures with substrates/inhibitors | `query`, `limit`, `resolution_range` |
| `get_structure_info` | Structure details: active site geometry, ligand contacts | `pdb_id`, `format` |
| `download_structure` | Download structure for computational design | `pdb_id`, `format` |
| `search_by_uniprot` | Find all PDB structures for an enzyme | `uniprot_id`, `limit` |
| `get_structure_quality` | Resolution, R-factor, validation metrics | `pdb_id` |

### `mcp__alphafold__alphafold_data` (Predicted Structures)

| Method | Enzyme engineering use | Key parameters |
|--------|----------------------|----------------|
| `get_structure` | AlphaFold model for enzymes without crystal structures | `uniprotId`, `format` |
| `get_confidence_scores` | pLDDT for identifying flexible/rigid regions | `uniprotId` |
| `analyze_confidence_regions` | Map high/low confidence regions relative to active site | `uniprotId` |

### `mcp__pubmed__pubmed_articles` (Literature Evidence)

| Method | Enzyme engineering use | Key parameters |
|--------|----------------------|----------------|
| `search_keywords` | Find directed evolution studies, engineering strategies | `keywords`, `num_results` |
| `search_advanced` | Date-filtered search for recent engineering advances | `term`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details by PMID | `pmid` |

### `mcp__chembl__chembl_info` (Substrate/Inhibitor Bioactivity)

| Method | Enzyme engineering use | Key parameters |
|--------|----------------------|----------------|
| `target_search` | Find enzyme target entry in ChEMBL | `query`, `limit` |
| `get_bioactivity` | Known substrates, inhibitors, and kinetic data | `target_id`, `limit` |

### `mcp__stringdb__stringdb_data` (Metabolic Context)

| Method | Enzyme engineering use | Key parameters |
|--------|----------------------|----------------|
| `get_protein_interactions` | Identify pathway partners, complex components | `identifiers`, `species`, `required_score` |
| `get_functional_enrichment` | Metabolic pathway context for the enzyme | `identifiers`, `species` |

---

## Python Environment

The container has Python 3.11+ with standard scientific libraries (numpy, scipy, pandas, matplotlib, seaborn, scikit-learn). All code blocks are executable via Bash.

---

## Directed Evolution Strategies

### Error-Prone PCR (epPCR)

Random mutagenesis across the entire gene to generate diversity.

```
Protocol design parameters:
1. Mutation rate: 1-5 mutations per gene (low), 5-10 (medium), 10-20 (high)
2. MnCl2 concentration: 0.05-0.5 mM (increases error rate)
3. Unbalanced dNTPs: reduce one dNTP to 1/5 concentration
4. Mg2+ excess: 6-7 mM MgCl2 (standard is 1.5 mM)
5. Low-fidelity polymerase: Mutazyme II, GeneMorph II

Decision logic:
- First round: 2-4 mutations/gene (explore broadly)
- Subsequent rounds: 1-2 mutations/gene on improved variants (fine-tune)
- If library size limited: use higher mutation rate with more screening
```

### DNA Shuffling (Stemmer Recombination)

Recombine beneficial mutations from multiple parent enzymes.

```
Requirements:
- 2-5 parent sequences with >60% identity
- DNase I fragmentation: 50-200 bp fragments
- Reassembly PCR without primers, then amplification with outer primers

Applications:
- Combine mutations from parallel epPCR campaigns
- Recombine orthologous enzymes from different species
- Family shuffling for thermostability + activity combinations
```

### Phage-Assisted Continuous Evolution (PACE)

Continuous directed evolution with >100 generations per day.

```
Components:
- Selection phage (SP): carries the evolving gene
- Accessory plasmid (AP): links enzyme activity to phage propagation (gIII expression)
- Host cells: continuously diluted (lagoon flow rate = 1-3 volumes/hr)
- Mutagenesis plasmid (MP): elevated mutation rate in host

Key parameters:
- Lagoon volume: typically 50-500 mL
- Flow rate: sets stringency (faster = more stringent selection)
- Mutation rate: ~10^-3 per bp per generation with MP6

Best for: enzymes with activity linkable to transcriptional output
Not suitable for: enzymes requiring FACS-based selection or complex assays
```

### PHAGE (PHAge and GEnomics-based directed evolution)

Genomic integration-based evolution for in vivo enzyme optimization.

```
Strategy:
1. Integrate enzyme gene into host genome
2. Apply selective pressure for improved enzyme activity
3. Use adaptive laboratory evolution (ALE) with serial passaging
4. Sequence evolved populations to identify beneficial mutations

Timeline: weeks to months (vs. days for PACE)
Best for: enzymes where in vivo function is directly selected
```

---

## Rational Design Approaches

### Active Site Mutagenesis

Target residues in and around the active site for altered specificity or activity.

```
Identification strategy:
1. mcp__uniprot__uniprot_data(method: "get_protein_features", accession: "ENZYME_ACC")
   -> Map active site residues, catalytic residues, substrate binding residues

2. mcp__pdb__pdb_data(method: "search_by_uniprot", uniprot_id: "ENZYME_ACC", limit: 10)
   -> Find structures with bound substrates/inhibitors/transition state analogs

3. mcp__pdb__pdb_data(method: "get_structure_info", pdb_id: "XXXX", format: "json")
   -> Identify residues within 5 A of substrate

Mutagenesis targets:
- First shell: residues directly contacting substrate (1-3 A)
  -> Modify for substrate specificity changes
- Second shell: residues contacting first-shell residues (3-6 A)
  -> Modify for subtle activity/selectivity tuning
- Catalytic residues: usually conserved — mutate only for mechanism change
```

### Disulfide Engineering

Introduce disulfide bonds to increase thermostability.

```python
def identify_disulfide_candidates(sequence, structure_pdb):
    """Identify residue pairs suitable for disulfide bond introduction.

    Criteria for engineered disulfides:
    - C-alpha distance: 4.4-6.8 A (optimal ~5.6 A)
    - C-beta distance: 3.4-4.6 A
    - Not in active site (>10 A from catalytic residues)
    - Both residues on same domain
    - Avoid proline neighbors (conformational constraint)
    """
    # Parse structure (simplified — use BioPython in practice)
    candidates = []
    # For each non-Cys, non-Pro residue pair:
    #   1. Calculate CA-CA distance
    #   2. Calculate CB-CB distance (virtual CB for Gly)
    #   3. Check chi3 dihedral angle (~±90 degrees)
    #   4. Filter by distance criteria
    #   5. Exclude pairs near active site

    print("Disulfide engineering candidates:")
    print("Pair        CA-CA   CB-CB   Near Active Site")
    for c in candidates:
        print(f"{c['res1']}-{c['res2']}  {c['ca_dist']:.1f}A   {c['cb_dist']:.1f}A   {c['near_active']}")
    return candidates
```

### Consensus Design

Use multiple sequence alignment of homologs to identify stabilizing consensus mutations.

```
Protocol:
1. mcp__uniprot__uniprot_data(method: "get_protein_homologs", accession: "ENZYME_ACC", organism: "all", size: 50)
   -> Collect 30-100 homologous enzyme sequences

2. Multiple sequence alignment (MAFFT, MUSCLE, or Clustal Omega)

3. Calculate consensus frequency at each position:
   - Consensus residue = most frequent amino acid at each position
   - Consensus threshold: >50% frequency (conservative) or >30% (aggressive)

4. Identify back-to-consensus mutations:
   - Positions where wild-type differs from consensus
   - Exclude active site residues and positions with <30% consensus
   - Prioritize positions with conservation >60%

5. Expected outcome:
   - Thermostability: +2 to +15 C per 5-10 consensus mutations
   - Activity: usually neutral or slightly reduced (validate)
```

```python
import numpy as np
from collections import Counter

def consensus_mutations(alignment_dict, wt_name, active_site_positions=None,
                        min_frequency=0.5, exclude_positions=None):
    """Identify consensus mutations from MSA.

    Parameters
    ----------
    alignment_dict : dict
        {sequence_name: aligned_sequence_string}
    wt_name : str
        Name of wild-type sequence in alignment.
    active_site_positions : list or None
        Alignment positions to exclude (0-indexed).
    min_frequency : float
        Minimum consensus frequency threshold (0.3-0.7).
    exclude_positions : list or None
        Additional positions to exclude.

    Returns
    -------
    list of dicts with mutation suggestions.
    """
    wt_seq = alignment_dict[wt_name]
    n_seqs = len(alignment_dict)
    exclude = set(active_site_positions or []) | set(exclude_positions or [])

    mutations = []
    for pos in range(len(wt_seq)):
        if pos in exclude or wt_seq[pos] == '-':
            continue

        col = [seq[pos] for seq in alignment_dict.values() if seq[pos] != '-']
        if len(col) < n_seqs * 0.5:
            continue  # Skip gappy columns

        counts = Counter(col)
        consensus_aa, consensus_count = counts.most_common(1)[0]
        freq = consensus_count / len(col)

        if freq >= min_frequency and consensus_aa != wt_seq[pos]:
            mutations.append({
                'position': pos + 1,  # 1-indexed
                'wt_aa': wt_seq[pos],
                'consensus_aa': consensus_aa,
                'frequency': freq,
                'label': f"{wt_seq[pos]}{pos+1}{consensus_aa}",
            })

    mutations.sort(key=lambda m: m['frequency'], reverse=True)
    print(f"Consensus mutations (threshold >= {min_frequency}):")
    print(f"{'Mutation':<12} {'Frequency':>9} {'Priority'}")
    print("-" * 35)
    for m in mutations:
        priority = "HIGH" if m['frequency'] > 0.7 else "MEDIUM" if m['frequency'] > 0.5 else "LOW"
        print(f"{m['label']:<12} {m['frequency']:>8.1%}  {priority}")
    return mutations
```

---

## Semi-Rational Approaches

### Combinatorial Active-Site Saturation Testing (CAST/ISM)

Systematically saturate active site positions in combinations.

```
CAST (Combinatorial Active-Site Saturation Testing):
1. Identify active site residues (typically 5-15 positions)
2. Group into pairs or triplets based on spatial proximity
3. Saturate each group with NNK codons (20 amino acids)
4. Screen each sub-library (~3,000 variants for pairs, ~100,000 for triplets)

ISM (Iterative Saturation Mutagenesis):
1. Saturate one group, screen, identify best variant
2. Use best variant as template for next group saturation
3. Iterate through all groups sequentially
4. Order of groups can affect outcome — try multiple orderings

Library size calculations:
- NNK codon: encodes 20 amino acids in 32 codons
- 1 position NNK: 32 variants, screen ~96 for 95% coverage
- 2 positions NNK: 32^2 = 1,024 variants, screen ~3,066 for 95% coverage
- 3 positions NNK: 32^3 = 32,768 variants, screen ~98,163 for 95% coverage
- NDT codon: encodes 12 amino acids (balanced), 12^2 = 144 for pairs
- 22c-trick: encodes exactly 20 amino acids in 22 codons

Coverage formula: N = -V * ln(1 - P)
  where V = library size (32^n for NNK), P = desired coverage (0.95)
```

```python
import math

def library_coverage_calculator(n_positions, codon_scheme="NNK", target_coverage=0.95):
    """Calculate required screening effort for saturation mutagenesis.

    Parameters
    ----------
    n_positions : int
        Number of positions to saturate simultaneously.
    codon_scheme : str
        'NNK' (32 codons, 20 aa), 'NDT' (12 codons, 12 aa),
        'NNS' (32 codons, 20 aa), '22c' (22 codons, 20 aa).
    target_coverage : float
        Desired fraction of library covered (0.0-1.0).

    Returns
    -------
    dict with library statistics.
    """
    codons = {'NNK': 32, 'NNS': 32, 'NDT': 12, '22c': 22}
    amino_acids = {'NNK': 20, 'NNS': 20, 'NDT': 12, '22c': 20}

    n_codons = codons[codon_scheme]
    n_aa = amino_acids[codon_scheme]

    codon_library_size = n_codons ** n_positions
    aa_library_size = n_aa ** n_positions
    screening_needed = int(-codon_library_size * math.log(1 - target_coverage))

    result = {
        'positions': n_positions,
        'codon_scheme': codon_scheme,
        'codon_library_size': codon_library_size,
        'protein_library_size': aa_library_size,
        'screening_for_95pct': screening_needed,
        'target_coverage': target_coverage,
    }

    print(f"Saturation mutagenesis: {n_positions} positions, {codon_scheme} codons")
    print(f"  Codon library size: {codon_library_size:,}")
    print(f"  Protein variants: {aa_library_size:,}")
    print(f"  Screen for {target_coverage:.0%} coverage: {screening_needed:,}")

    feasibility = "EASY" if screening_needed < 1000 else \
                  "MODERATE" if screening_needed < 10000 else \
                  "HARD" if screening_needed < 100000 else "IMPRACTICAL"
    print(f"  Feasibility: {feasibility}")

    return result

# Example calculations
library_coverage_calculator(1, "NNK")
library_coverage_calculator(2, "NNK")
library_coverage_calculator(2, "NDT")
library_coverage_calculator(3, "NDT")
```

---

## Stability Engineering

### Thermostability: B-Factor Analysis

Use crystallographic B-factors to identify flexible regions for stabilization.

```
Strategy:
1. mcp__pdb__pdb_data(method: "get_structure_info", pdb_id: "XXXX", format: "json")
   -> Extract B-factors per residue from crystal structure

2. Identify high B-factor regions (top 10-20% of residues)
   -> These are the most flexible, often at surface loops

3. Stabilization strategies for high B-factor positions:
   - Proline substitutions at loop positions (rigidify backbone)
   - Salt bridges between flexible loops and stable regions
   - Disulfide bonds anchoring flexible loops (see Disulfide Engineering)
   - Consensus mutations at flexible positions
   - Glycine -> Alanine at positions where flexibility is not needed

4. Avoid stabilizing residues near active site (may reduce activity)
```

```python
import numpy as np

def analyze_bfactors(bfactors, residue_numbers, active_site_residues=None,
                     percentile_cutoff=80):
    """Identify high B-factor residues for stability engineering.

    Parameters
    ----------
    bfactors : list of float
        Per-residue B-factors from crystal structure.
    residue_numbers : list of int
        Corresponding residue numbers.
    active_site_residues : list of int or None
        Residues to exclude from engineering targets.
    percentile_cutoff : int
        Percentile above which residues are flagged (default: 80).

    Returns
    -------
    list of candidate residues for stabilization.
    """
    bfactors = np.array(bfactors)
    threshold = np.percentile(bfactors, percentile_cutoff)
    active_site = set(active_site_residues or [])

    candidates = []
    for resnum, bf in zip(residue_numbers, bfactors):
        if bf >= threshold and resnum not in active_site:
            candidates.append({'residue': resnum, 'bfactor': bf})

    candidates.sort(key=lambda x: x['bfactor'], reverse=True)

    print(f"B-factor analysis (cutoff: {percentile_cutoff}th percentile = {threshold:.1f})")
    print(f"{'Residue':>8} {'B-factor':>10} {'Strategy'}")
    print("-" * 40)
    for c in candidates[:20]:
        strategy = "Pro sub / salt bridge" if c['bfactor'] > threshold * 1.3 else "Consensus / Ala"
        print(f"{c['residue']:>8d} {c['bfactor']:>10.1f} {strategy}")

    return candidates
```

### Thermostability: Rosetta ddG Calculations

Predict stability effects of mutations using Rosetta cartesian_ddg protocol.

```
Rosetta cartesian_ddg protocol:
1. Relax wild-type structure (3 rounds minimum)
2. For each mutation:
   - Introduce mutation with cartesian_ddg application
   - Calculate ddG = G_mutant - G_wildtype
   - Negative ddG = stabilizing, Positive ddG = destabilizing

Interpretation:
  ddG < -1.0 REU: strongly stabilizing (high confidence)
  -1.0 < ddG < -0.5 REU: moderately stabilizing
  -0.5 < ddG < 0.5 REU: neutral
  0.5 < ddG < 1.0 REU: moderately destabilizing
  ddG > 1.0 REU: strongly destabilizing

Limitations:
  - Accuracy ~1 kcal/mol; marginal predictions unreliable
  - Better for buried positions than surface
  - Combine with FoldX for cross-validation
```

### Thermostability: FoldX ddG Predictions

```
FoldX BuildModel protocol:
1. Repair PDB: foldx --command=RepairPDB --pdb=enzyme.pdb
2. Create individual_list.txt with mutations (e.g., "LA45P;")
3. Run: foldx --command=BuildModel --pdb=enzyme_Repair.pdb --mutant-file=individual_list.txt
4. Parse Dif_*.fxout for ddG values

Interpretation:
  ddG < -0.5 kcal/mol: stabilizing
  -0.5 < ddG < 0.5 kcal/mol: neutral
  ddG > 0.5 kcal/mol: destabilizing
  ddG > 2.0 kcal/mol: strongly destabilizing

Best practice: combine FoldX + Rosetta ddG and take consensus predictions
```

### pH Stability Engineering

```
Strategies for pH stability:
1. Surface charge optimization:
   - Acidic stability: reduce surface negative charges (Asp/Glu -> Asn/Gln)
   - Basic stability: reduce surface positive charges (Lys/Arg -> neutral)
   - Use charge ladder approach: systematic Asp->Asn or Glu->Gln

2. Histidine engineering:
   - His pKa ~6.0 — protonation state changes near neutral pH
   - Replace surface His with Asn/Gln for pH-insensitive stability
   - Or exploit His for pH-switchable activity

3. Salt bridge optimization:
   - Identify salt bridges that break at target pH
   - Replace with hydrophobic contacts or H-bonds

4. Computational: use EpHod for pH optimum prediction from sequence
```

### Solvent Tolerance Engineering

```
Strategies for organic solvent tolerance:
1. Surface hydrophobic patch engineering:
   - Increase surface hydrophobicity at positions far from active site
   - Leu/Ile/Val substitutions at surface positions
   - Reduces unfavorable solvent-protein interactions

2. Disulfide bond introduction:
   - Protects against solvent-induced unfolding
   - Critical for enzymes used in >20% organic cosolvent

3. Glycosylation engineering (for yeast/mammalian expression):
   - N-linked glycans shield surface from solvent
   - Introduce Asn-X-Thr/Ser sequons at surface loops

4. Directed evolution in increasing solvent concentrations:
   - Serial rounds of epPCR with 10%, 20%, 30%... solvent
   - PACE adaptable for some solvent-dependent selections
```

---

## Property Prediction Tools

### EpHod: pH Optimum Prediction

```
EpHod predicts optimal pH for enzyme activity from sequence alone.
- Input: protein sequence (FASTA)
- Output: predicted pH optimum (continuous value)
- Method: ESM-based transfer learning on enzyme pH data
- Accuracy: MAE ~0.8 pH units

Usage:
  ephod predict --input enzyme.fasta --output ph_prediction.csv

Interpretation:
  Use predicted pH optimum to guide buffer selection and pH stability engineering.
  If target application pH differs from predicted optimum by >2 units,
  prioritize pH stability engineering.
```

### CLEAN: EC Number Assignment

```
CLEAN (Contrastive Learning for Enzyme ANnotation):
- Input: protein sequence
- Output: EC number prediction with confidence score
- Method: contrastive learning on enzyme-reaction pairs
- Use case: annotate uncharacterized enzymes, verify enzyme function

Usage:
  clean predict --input sequences.fasta --output ec_predictions.csv

Interpretation:
  High confidence (>0.8): reliable EC assignment
  Medium (0.5-0.8): likely correct, verify experimentally
  Low (<0.5): uncertain, multiple possible functions
```

### FireProt / FIREPROTdb: Thermostability Prediction

```
FireProt combines energy-based and evolution-based approaches:
1. Energy-based: FoldX and Rosetta ddG calculations
2. Evolution-based: back-to-consensus mutations from MSA
3. Combined: prioritize mutations that are stabilizing by BOTH methods

FireProt web server: https://loschmidt.chemi.muni.cz/fireprot/
- Input: PDB structure or UniProt ID
- Output: ranked list of stabilizing mutations with ddG predictions
- Filters: removes mutations near active site, catalytic residues

FIREPROTdb: database of experimentally validated thermostability mutations
- Use to benchmark predictions and identify known stabilizing motifs
```

### ProTstab / ThermoMPNN: Melting Temperature Prediction

```
ProTstab: predict Tm from protein sequence
- Input: amino acid sequence
- Output: predicted Tm (degrees C)
- Use case: estimate thermal stability of wild-type and designed variants

ThermoMPNN: structure-based Tm prediction using message passing neural network
- Input: PDB structure
- Output: predicted Tm and per-mutation ddTm
- More accurate than sequence-only methods when structure is available
- Use to rank designed variants by predicted thermostability
```

### CataPro: Kinetic Parameter Prediction

```
CataPro predicts enzyme kinetic parameters from sequence:
- kcat (turnover number)
- Km (Michaelis constant)
- kcat/Km (catalytic efficiency)

Input: enzyme sequence + substrate SMILES
Output: predicted kinetic parameters with confidence intervals

Limitations:
- Training data biased toward well-studied enzyme families
- Less reliable for novel enzyme-substrate combinations
- Use as ranking tool, not absolute value predictor
```

---

## Protein Redesign Tools

### LigandMPNN: Ligand-Conditioned Sequence Design

```
LigandMPNN designs sequences conditioned on ligand/substrate binding:
- Input: backbone structure + ligand coordinates (PDB)
- Output: designed sequences with predicted binding to ligand
- Key difference from ProteinMPNN: accounts for ligand interactions

Parameters:
  --model_type ligand_mpnn
  --pdb_path enzyme_with_substrate.pdb
  --chains_to_design A           # Which chains to redesign
  --fixed_residues A15,A45,A110  # Keep catalytic residues fixed
  --ligand_mpnn_use_side_chain_context  # Use side chain info
  --temperature 0.1              # Low = conservative, high = diverse
  --number_of_batches 10         # Generate 10 sequences per backbone
  --batch_size 8

Use cases:
- Redesign enzyme binding pocket to accept new substrate
- Optimize substrate binding while preserving catalytic residues
- Design enzyme-substrate complementarity for non-natural substrates
```

### Chroma: Generative Diffusion Model

```
Chroma generates novel protein structures via diffusion:
- Unconditional: generate completely novel enzyme folds
- Conditional: generate structures with specified properties
  - Shape constraints
  - Symmetry constraints
  - Secondary structure specifications

Use for enzyme engineering:
1. Generate novel scaffolds for known active site geometries
2. Design symmetric multimeric enzymes (e.g., homo-trimers for cooperative catalysis)
3. Explore fold space for enzymes with improved stability

Parameters:
  chroma.sample(
      chain_lengths=[250],           # Protein length
      conditioner=conditioner,       # Property conditioner
      steps=500,                     # Diffusion steps
      langevin_factor=2.0,          # Sampling diversity
  )
```

### ProteinMPNN: Fixed-Backbone Sequence Design

```
ProteinMPNN designs optimal sequences for a given backbone:
- Input: backbone coordinates (PDB)
- Output: amino acid sequences predicted to fold into that backbone

Parameters for enzyme design:
  --pdb_path enzyme_backbone.pdb
  --chains_to_design A
  --fixed_positions "A15 A45 A110"  # Catalytic residues MUST be fixed
  --num_seq_per_target 32
  --sampling_temp 0.1               # Conservative (high confidence)
  --batch_size 8

Enzyme-specific considerations:
- ALWAYS fix catalytic residues (Ser-His-Asp triad, etc.)
- ALWAYS fix substrate-contacting residues (first shell)
- Allow second-shell residues to redesign (activity tuning)
- Allow surface residues to redesign (stability, solubility)
- Score: lower ProteinMPNN score = higher design confidence
```

### RFdiffusion: Backbone Generation for Enzyme Scaffolds

```
RFdiffusion generates novel backbones, applicable to enzyme design:

1. Motif scaffolding for active sites:
   - Fix catalytic residues in 3D space
   - Generate new scaffold around them
   - contigs: "A15-15/0 A45-45/0 A110-110/0 100-150"
     = fix residues 15, 45, 110 and generate 100-150 aa scaffold

2. De novo enzyme scaffold design:
   - Define active site geometry (theozyme)
   - Place catalytic residues at required distances/angles
   - Generate diverse scaffolds that support the active site

3. Key parameters:
   --inference.num_designs 500
   --contigmap.contigs ["A15-15/0 A45-45/0 A110-110/0 100-150"]
   --potentials.guide_scale 2       # Strength of constraint
   --denoiser.noise_scale_ca 0.5    # Backbone noise level
```

---

## Mutation Effect Prediction

### ESM Log-Likelihood Scoring

```python
def esm_mutation_scoring(wt_sequence, mutations):
    """Score mutations using ESM masked marginal log-likelihood.

    Higher score = more likely to be tolerated/beneficial.
    Requires: pip install fair-esm

    Parameters
    ----------
    wt_sequence : str
        Wild-type protein sequence.
    mutations : list of str
        Mutations in format ['A45V', 'L110F', 'G200P'].

    Returns
    -------
    list of dicts with mutation scores.
    """
    import torch
    import esm

    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    batch_converter = alphabet.get_batch_converter()
    model.eval()

    results = []
    for mut in mutations:
        wt_aa = mut[0]
        pos = int(mut[1:-1]) - 1  # 0-indexed
        mut_aa = mut[-1]

        assert wt_sequence[pos] == wt_aa, f"WT mismatch at {pos+1}: expected {wt_aa}, got {wt_sequence[pos]}"

        # Mask position and score
        data = [("protein", wt_sequence)]
        batch_labels, batch_strs, batch_tokens = batch_converter(data)
        with torch.no_grad():
            token_logits = model(batch_tokens)["logits"]

        # Get log-likelihoods at the mutated position
        pos_logits = token_logits[0, pos + 1]  # +1 for BOS token
        wt_ll = pos_logits[alphabet.get_idx(wt_aa)].item()
        mut_ll = pos_logits[alphabet.get_idx(mut_aa)].item()
        delta_ll = mut_ll - wt_ll

        results.append({
            'mutation': mut,
            'wt_ll': wt_ll,
            'mut_ll': mut_ll,
            'delta_ll': delta_ll,
            'prediction': 'BENEFICIAL' if delta_ll > 0 else 'NEUTRAL' if delta_ll > -2 else 'DELETERIOUS',
        })

    results.sort(key=lambda r: r['delta_ll'], reverse=True)
    print(f"ESM mutation scoring ({len(results)} mutations):")
    print(f"{'Mutation':<10} {'Delta LL':>9} {'Prediction'}")
    print("-" * 35)
    for r in results:
        print(f"{r['mutation']:<10} {r['delta_ll']:>9.2f} {r['prediction']}")
    return results
```

### FoldX and Rosetta Cross-Validation

```python
def cross_validate_stability_predictions(foldx_results, rosetta_results):
    """Combine FoldX and Rosetta ddG predictions for consensus scoring.

    Parameters
    ----------
    foldx_results : dict
        {mutation: ddG_foldx} from FoldX BuildModel.
    rosetta_results : dict
        {mutation: ddG_rosetta} from Rosetta cartesian_ddg.

    Returns
    -------
    list of consensus predictions ranked by confidence.
    """
    consensus = []
    all_mutations = set(foldx_results.keys()) & set(rosetta_results.keys())

    for mut in all_mutations:
        fx = foldx_results[mut]
        ros = rosetta_results[mut]

        # Both agree on stabilizing
        if fx < -0.5 and ros < -0.5:
            category = "STABILIZING (high confidence)"
            priority = 1
        # Both agree on destabilizing
        elif fx > 0.5 and ros > 0.5:
            category = "DESTABILIZING (high confidence)"
            priority = 4
        # One stabilizing, one neutral
        elif (fx < -0.5 and -0.5 <= ros <= 0.5) or (-0.5 <= fx <= 0.5 and ros < -0.5):
            category = "POSSIBLY STABILIZING (medium confidence)"
            priority = 2
        # Disagreement
        elif (fx < -0.5 and ros > 0.5) or (fx > 0.5 and ros < -0.5):
            category = "CONFLICTING (low confidence)"
            priority = 3
        else:
            category = "NEUTRAL"
            priority = 3

        consensus.append({
            'mutation': mut,
            'foldx_ddg': fx,
            'rosetta_ddg': ros,
            'category': category,
            'priority': priority,
        })

    consensus.sort(key=lambda c: c['priority'])
    print(f"Consensus stability predictions:")
    print(f"{'Mutation':<10} {'FoldX':>8} {'Rosetta':>8} {'Category'}")
    print("-" * 60)
    for c in consensus:
        print(f"{c['mutation']:<10} {c['foldx_ddg']:>8.2f} {c['rosetta_ddg']:>8.2f} {c['category']}")
    return consensus
```

---

## Kinetic Characterization

### Michaelis-Menten Fitting

```python
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def michaelis_menten(S, Vmax, Km):
    """Michaelis-Menten equation: v = Vmax * [S] / (Km + [S])"""
    return Vmax * S / (Km + S)

def fit_michaelis_menten(substrate_conc, velocities, enzyme_conc_nM=None):
    """Fit Michaelis-Menten kinetics to experimental data.

    Parameters
    ----------
    substrate_conc : array-like
        Substrate concentrations (uM).
    velocities : array-like
        Initial velocities (uM/min or uM/s).
    enzyme_conc_nM : float or None
        Enzyme concentration in nM for kcat calculation.

    Returns
    -------
    dict with Vmax, Km, kcat (if enzyme_conc provided), kcat/Km.
    """
    S = np.array(substrate_conc, dtype=float)
    v = np.array(velocities, dtype=float)

    # Non-linear least squares fit
    popt, pcov = curve_fit(michaelis_menten, S, v, p0=[max(v), np.median(S)],
                           bounds=([0, 0], [np.inf, np.inf]))
    Vmax, Km = popt
    Vmax_err, Km_err = np.sqrt(np.diag(pcov))

    result = {
        'Vmax': Vmax, 'Vmax_err': Vmax_err,
        'Km': Km, 'Km_err': Km_err,
    }

    if enzyme_conc_nM:
        enzyme_conc_uM = enzyme_conc_nM / 1000
        kcat = Vmax / enzyme_conc_uM  # per second (if v in uM/s) or per min
        result['kcat'] = kcat
        result['kcat_Km'] = kcat / Km  # catalytic efficiency
        result['kcat_Km_unit'] = 'uM-1 s-1' if 's' in 'velocity_unit' else 'uM-1 min-1'

    # R-squared
    ss_res = np.sum((v - michaelis_menten(S, *popt)) ** 2)
    ss_tot = np.sum((v - np.mean(v)) ** 2)
    r_squared = 1 - ss_res / ss_tot

    print(f"Michaelis-Menten Fit (R2 = {r_squared:.4f}):")
    print(f"  Vmax = {Vmax:.3f} +/- {Vmax_err:.3f}")
    print(f"  Km   = {Km:.3f} +/- {Km_err:.3f} uM")
    if enzyme_conc_nM:
        print(f"  kcat = {result['kcat']:.2f}")
        print(f"  kcat/Km = {result['kcat_Km']:.4f}")

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Michaelis-Menten plot
    S_fit = np.linspace(0, max(S) * 1.1, 200)
    axes[0].scatter(S, v, color='black', s=40, zorder=3)
    axes[0].plot(S_fit, michaelis_menten(S_fit, *popt), 'r-', linewidth=2)
    axes[0].set_xlabel('[S] (uM)'); axes[0].set_ylabel('v')
    axes[0].set_title(f'Michaelis-Menten (Km={Km:.1f}, Vmax={Vmax:.2f})')
    axes[0].axhline(Vmax, ls='--', color='gray', alpha=0.5)
    axes[0].axvline(Km, ls='--', color='gray', alpha=0.5)

    # Lineweaver-Burk plot
    S_nz = S[S > 0]; v_nz = v[S > 0]
    axes[1].scatter(1/S_nz, 1/v_nz, color='black', s=40, zorder=3)
    x_lb = np.linspace(-1/Km * 0.5, max(1/S_nz) * 1.2, 100)
    y_lb = (1/Vmax) + (Km/Vmax) * x_lb
    axes[1].plot(x_lb, y_lb, 'b-', linewidth=2)
    axes[1].set_xlabel('1/[S]'); axes[1].set_ylabel('1/v')
    axes[1].set_title('Lineweaver-Burk')
    axes[1].axhline(0, color='gray', lw=0.5); axes[1].axvline(0, color='gray', lw=0.5)

    plt.tight_layout()
    plt.savefig('kinetics_fit.png', dpi=150)
    return result

# Example usage
S = [1, 2, 5, 10, 20, 50, 100, 200, 500]
v = [0.05, 0.09, 0.19, 0.32, 0.48, 0.69, 0.81, 0.88, 0.94]
result = fit_michaelis_menten(S, v, enzyme_conc_nM=10)
```

### Substrate Specificity Profiling

```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def substrate_specificity_profile(substrates, kcat_values, km_values,
                                   enzyme_name="enzyme"):
    """Create substrate specificity profile from kinetic data.

    Parameters
    ----------
    substrates : list of str
        Substrate names.
    kcat_values : list of float
        Turnover numbers (s-1).
    km_values : list of float
        Michaelis constants (uM).
    enzyme_name : str
        Name of the enzyme for plot title.

    Returns
    -------
    pd.DataFrame with specificity metrics.
    """
    df = pd.DataFrame({
        'substrate': substrates,
        'kcat': kcat_values,
        'Km': km_values,
    })
    df['kcat_Km'] = df['kcat'] / df['Km']
    df['relative_efficiency'] = df['kcat_Km'] / df['kcat_Km'].max() * 100

    df = df.sort_values('kcat_Km', ascending=False)

    print(f"Substrate specificity profile for {enzyme_name}:")
    print(f"{'Substrate':<20} {'kcat (s-1)':>10} {'Km (uM)':>10} {'kcat/Km':>12} {'Rel. %':>8}")
    print("-" * 65)
    for _, row in df.iterrows():
        print(f"{row['substrate']:<20} {row['kcat']:>10.2f} {row['Km']:>10.1f} "
              f"{row['kcat_Km']:>12.4f} {row['relative_efficiency']:>7.1f}%")

    # Visualization
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # kcat/Km bar chart
    axes[0].barh(df['substrate'], df['kcat_Km'], color='steelblue')
    axes[0].set_xlabel('kcat/Km (uM-1 s-1)'); axes[0].set_title('Catalytic Efficiency')

    # kcat comparison
    axes[1].barh(df['substrate'], df['kcat'], color='coral')
    axes[1].set_xlabel('kcat (s-1)'); axes[1].set_title('Turnover Number')

    # Km comparison
    axes[2].barh(df['substrate'], df['Km'], color='mediumseagreen')
    axes[2].set_xlabel('Km (uM)'); axes[2].set_title('Michaelis Constant')

    plt.tight_layout()
    plt.savefig(f'{enzyme_name}_specificity.png', dpi=150)
    return df
```

---

## Activity Screening

### High-Throughput Assay Design

```
Colorimetric assays (96/384-well plates):
- pNP-substrates: p-nitrophenol release at 405 nm
  Throughput: ~10,000 variants/day (384-well, automated)
  Best for: esterases, lipases, phosphatases, glycosidases

- ABTS/DMP: oxidase activity via colored product
  Throughput: ~5,000 variants/day
  Best for: laccases, peroxidases

Fluorometric assays:
- 4-MU substrates: 4-methylumbelliferone release (ex 360, em 450 nm)
  Throughput: ~20,000 variants/day (more sensitive than colorimetric)
  Best for: glycosidases, lipases, proteases

- Resorufin substrates: resorufin release (ex 560, em 590 nm)
  Best for: oxidoreductases, CYP enzymes
```

### FACS-Based Selection

```
Compartmentalized selection using FACS:
1. Express enzyme variants on cell surface (display) or in droplets
2. Add fluorogenic substrate
3. Sort cells/droplets with highest fluorescence
4. Recover and sequence enriched variants

Methods:
- Yeast surface display + FACS: ~10^7 variants/sort
- In vitro compartmentalization (IVC): water-in-oil emulsions
- Microfluidic droplets: 10^6-10^8 droplets, sort at kHz rates

Best for: enzymes with fluorogenic substrates or coupled assays
Limitations: requires substrate access to displayed enzyme
```

### Microfluidic Screening

```
Droplet-based microfluidic screening:
1. Encapsulate single cells in picoliter droplets
2. Lyse cells, add substrate
3. Incubate (minutes to hours)
4. Sort droplets by fluorescence at 1,000-10,000 Hz

Advantages:
- Ultra-high throughput: 10^7-10^8 variants per screen
- Minimal reagent consumption (picoliter volumes)
- Quantitative activity measurement per variant

Platforms:
- Absortable FADS (fluorescence-activated droplet sorting)
- Double emulsion + FACS (w/o/w droplets sorted on standard FACS)

Key parameters:
- Droplet size: 10-50 pL (single cell encapsulation)
- Lambda (cells/droplet): 0.1-0.3 (Poisson loading)
- Incubation time: matched to enzyme kinetics
```

---

## Immobilization Strategies

### Covalent Attachment

```
Methods:
1. Epoxide supports (Immobead, Sepabeads):
   - React with Lys, Cys, His side chains
   - Multipoint attachment increases rigidity and stability
   - pH 7-10 for Lys targeting, pH 5-7 for Cys

2. NHS-activated supports:
   - React with primary amines (Lys, N-terminus)
   - Fast coupling (1-2 hours)
   - Use at pH 7.0-8.5

3. Glutaraldehyde crosslinking:
   - Crosslinks between Lys residues
   - Cheap and robust
   - Risk of over-crosslinking (test GA concentration 0.1-2%)

Design considerations:
- Orient active site AWAY from support surface
- Introduce surface Cys at position opposite active site for oriented immobilization
- Test activity retention: typically 30-80% of free enzyme
- Measure stability improvement: often 5-50x increase in operational stability
```

### Cross-Linked Enzyme Aggregates (CLEAs)

```
CLEA preparation:
1. Precipitate enzyme with ammonium sulfate, PEG, or organic solvent
2. Crosslink aggregates with glutaraldehyde (25-75 mM, 1-3 hours)
3. Wash extensively to remove unreacted crosslinker
4. Characterize: activity recovery, stability, recyclability

Advantages:
- No carrier needed (pure enzyme preparation)
- High volumetric activity
- Simple preparation
- Can co-immobilize multiple enzymes (combi-CLEAs for cascades)

Parameters to optimize:
- Precipitant type and concentration
- Glutaraldehyde concentration (25-75 mM)
- Crosslinking time (1-24 hours)
- Addition of BSA as proteic feeder (improves CLEA for dilute enzymes)
```

### Encapsulation

```
Methods:
1. Sol-gel encapsulation (silica):
   - Mild conditions, retains activity
   - Pore size limits substrate access for large molecules

2. Alginate beads:
   - Gentle entrapment in calcium alginate
   - Good for whole-cell biocatalysts
   - Bead size: 1-3 mm (extrusion), 50-200 um (emulsion)

3. MOF (Metal-Organic Framework) encapsulation:
   - Crystalline porous materials
   - Protect enzyme from proteases and harsh conditions
   - ZIF-8 (zinc imidazolate) most common for enzymes
```

---

## Industrial Enzyme Applications

### Biocatalysis: Cascade Reactions

```
Multi-enzyme cascade design:
1. Define target transformation: starting material -> product
2. Identify individual enzymatic steps
3. Check cofactor requirements and compatibility
4. Design cofactor regeneration (see below)
5. Optimize reaction conditions (pH, temperature, cosolvent)

Example cascades:
- Alcohol -> aldehyde -> acid (ADH + AldDH, NAD+ recycling)
- Sugar -> sugar acid -> lactone (oxidase + lactonase)
- Amino acid -> keto acid -> chiral amine (transaminase cascade)

Co-immobilization strategies:
- combi-CLEAs: all enzymes in one CLEA particle
- Layer-by-layer: sequential immobilization on same support
- Microreactor: enzymes in separate compartments with flow
```

### Cofactor Regeneration

```
NAD(P)+/NAD(P)H regeneration:
1. Enzymatic regeneration:
   - FDH (formate dehydrogenase): formate + NAD+ -> CO2 + NADH
     Cheapest cofactor, irreversible, CO2 drives equilibrium
   - GDH (glucose dehydrogenase): glucose + NAD(P)+ -> gluconolactone + NAD(P)H
     Works with both NAD+ and NADP+, cheap glucose substrate
   - ADH (alcohol dehydrogenase): isopropanol + NAD+ -> acetone + NADH
     Acetone removal shifts equilibrium

2. Chemical regeneration:
   - Sodium dithionite (for NADH, but not selective)

3. Electrochemical regeneration:
   - Cathode reduces NAD+ to NADH via mediator
   - Rhodium complex mediators most common

ATP regeneration:
- Polyphosphate kinase: polyphosphate + ADP -> ATP + polyphosphate(n-1)
- Acetate kinase: acetyl-phosphate + ADP -> ATP + acetate
```

---

## Codon Optimization for Heterologous Expression

```python
def analyze_codon_usage(dna_sequence, host="ecoli"):
    """Analyze codon usage and identify rare codons for a host organism.

    Parameters
    ----------
    dna_sequence : str
        DNA coding sequence (must be multiple of 3).
    host : str
        'ecoli', 'yeast', 'human', 'pichia'.

    Returns
    -------
    dict with codon usage statistics and rare codon positions.
    """
    # E. coli rare codons (usage frequency < 10% of synonymous family)
    ecoli_rare = {
        'AGG': 'Arg', 'AGA': 'Arg', 'CGA': 'Arg',  # Arg rare codons
        'CUA': 'Leu',  # Leu rare codon
        'AUA': 'Ile',  # Ile rare codon
        'GGA': 'Gly',  # Gly rare (moderately)
        'CCC': 'Pro',  # Pro rare
    }

    # Pichia pastoris rare codons
    pichia_rare = {
        'CGC': 'Arg', 'CGG': 'Arg',  # Arg rare
        'CTC': 'Leu', 'CTG': 'Leu',  # Leu rare
        'GCG': 'Ala',  # Ala rare
        'ACG': 'Thr',  # Thr rare
    }

    rare_codons = ecoli_rare if host in ('ecoli', 'e_coli') else pichia_rare

    seq = dna_sequence.upper().replace(' ', '').replace('\n', '')
    assert len(seq) % 3 == 0, "Sequence length must be multiple of 3"

    codons = [seq[i:i+3] for i in range(0, len(seq), 3)]
    total = len(codons)
    rare_positions = []

    for i, codon in enumerate(codons):
        if codon in rare_codons:
            rare_positions.append({
                'position': i + 1,
                'codon': codon,
                'amino_acid': rare_codons[codon],
            })

    # GC content
    gc = (seq.count('G') + seq.count('C')) / len(seq) * 100

    # Consecutive rare codons (translation stalling risk)
    consecutive_rare = 0
    max_consecutive = 0
    for codon in codons:
        if codon in rare_codons:
            consecutive_rare += 1
            max_consecutive = max(max_consecutive, consecutive_rare)
        else:
            consecutive_rare = 0

    print(f"Codon analysis for {host} expression:")
    print(f"  Total codons: {total}")
    print(f"  Rare codons: {len(rare_positions)} ({len(rare_positions)/total*100:.1f}%)")
    print(f"  GC content: {gc:.1f}%")
    print(f"  Max consecutive rare: {max_consecutive}")

    if len(rare_positions) > total * 0.05:
        print("  WARNING: >5% rare codons - consider codon optimization")
    if max_consecutive >= 2:
        print("  WARNING: consecutive rare codons may cause ribosome stalling")
    if gc < 30 or gc > 65:
        print(f"  WARNING: GC content ({gc:.1f}%) outside optimal range (30-65%)")

    return {
        'total_codons': total,
        'rare_count': len(rare_positions),
        'rare_fraction': len(rare_positions) / total,
        'gc_content': gc,
        'max_consecutive_rare': max_consecutive,
        'rare_positions': rare_positions,
    }
```

---

## Expression Systems

### E. coli Systems

```
BL21(DE3): Standard workhorse
- Best for: soluble cytoplasmic proteins without disulfides
- Inducer: IPTG (0.1-1 mM)
- Temperature: 16-37 C (lower temp for solubility)
- Yield: 10-200 mg/L

SHuffle (NEB): Disulfide bond formation in cytoplasm
- Best for: enzymes with disulfide bonds
- Expresses DsbC (disulfide isomerase) in cytoplasm
- trxB/gor mutations allow disulfide formation
- Yield: 5-50 mg/L

ArcticExpress: Cold-adapted chaperones
- Best for: aggregation-prone enzymes
- Co-expresses Cpn10/Cpn60 from O. antarctica
- Grow at 10-12 C post-induction
- Yield: 1-20 mg/L

Auto-induction media (Studier ZYM-5052):
- No IPTG needed; lactose auto-induces at glucose depletion
- Higher cell density, often higher yield
- Mix: 1% tryptone, 0.5% yeast extract, 0.5% glycerol, 0.05% glucose, 0.2% lactose
```

### Pichia pastoris

```
Expression system:
- AOX1 promoter: methanol-inducible (strong, but requires MeOH handling)
- GAP promoter: constitutive (simpler, no methanol)
- Secretion: alpha-factor signal peptide -> protein secreted to medium

Advantages for enzymes:
- Eukaryotic folding machinery
- Glycosylation (N-linked)
- Secretion simplifies purification
- High cell density fermentation: 100-500 g/L wet cell weight
- Yield: 0.1-10 g/L secreted protein

Protocol:
1. Clone into pPICZalpha or pGAPZalpha
2. Linearize and electroporate into X-33 or GS115
3. Select on Zeocin plates (100-1000 ug/mL)
4. Screen clones by small-scale expression
5. Scale up in bioreactor with glycerol batch -> glycerol fed-batch -> methanol induction
```

### Cell-Free Expression

```
PURE system (Protein synthesis Using Recombinant Elements):
- Defined composition: purified ribosomes, tRNAs, translation factors, energy regeneration
- Best for: rapid screening of 100s of enzyme variants (1-2 days)
- Yield: 0.01-0.1 mg/mL per reaction
- Volume: 10-50 uL per variant (microtiter plate compatible)

Lysate-based (E. coli S30):
- Cheaper than PURE, higher yield (0.1-1 mg/mL)
- Less defined composition (contains proteases, nucleases)
- Use for initial screening, confirm hits in vivo

Applications in enzyme engineering:
- Rapid activity screening of designed variants
- Co-translational folding assessment
- Combinatorial library testing (100s of variants in parallel)
- Linear DNA template (no cloning required): PCR product -> cell-free -> activity assay
```

---

## Engineering Pipeline

### Phase 1: Enzyme Characterization

```
1. mcp__uniprot__uniprot_data(method: "search_proteins", query: "ENZYME_NAME EC:X.X.X.X", organism: "all", size: 10)
   -> Find enzyme, confirm identity, note organism

2. mcp__uniprot__uniprot_data(method: "get_protein_info", accession: "UNIPROT_ACC", format: "json")
   -> Full profile: catalytic activity, cofactors, metal ions, pH/temp optimum

3. mcp__uniprot__uniprot_data(method: "get_protein_features", accession: "UNIPROT_ACC")
   -> Active site residues, binding site, metal binding, disulfides

4. mcp__pdb__pdb_data(method: "search_by_uniprot", uniprot_id: "UNIPROT_ACC", limit: 10)
   -> Find crystal structures (prioritize substrate-bound or TSA-bound)

5. mcp__alphafold__alphafold_data(method: "get_structure", uniprotId: "UNIPROT_ACC", format: "pdb")
   -> AlphaFold model if no experimental structure available

6. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "ENZYME_NAME directed evolution engineering mutagenesis", num_results: 15)
   -> Published engineering studies on this or homologous enzymes

DECISION GATE: Do we have structural data AND activity assay? Proceed to Phase 2.
```

### Phase 2: Strategy Selection

```
Decision matrix for engineering strategy:

Goal                    | Primary Strategy           | Secondary Strategy
------------------------|---------------------------|-------------------
Thermostability         | Consensus design + B-factor| FoldX/Rosetta ddG screening
pH stability            | Surface charge engineering | Directed evolution
Substrate specificity   | CAST/ISM at active site   | LigandMPNN redesign
Catalytic efficiency    | epPCR + screening         | Active site mutagenesis
Solvent tolerance       | Surface engineering        | Disulfide introduction
Expression improvement  | Codon optimization         | Fusion tags, host change
Novel activity          | PACE/PHAGE                | RFdiffusion scaffolding

Information available   | Best approach
------------------------|---------------------------
Structure + assay       | Rational + semi-rational (CAST/ISM)
Sequence only           | Directed evolution (epPCR, DNA shuffling)
Structure + no assay    | Computational (ESM, FoldX, Rosetta) -> design library
Homologs available      | Consensus design + family shuffling
```

### Phase 3: Library Design and Screening

```
1. Design library based on Phase 2 strategy
2. Calculate library size and screening effort (see library_coverage_calculator)
3. Select screening method based on throughput requirements
4. Screen and identify improved variants
5. Characterize top hits: kinetics, stability, specificity

Validation cascade:
Stage 1: Primary screen (high throughput, ~10,000 variants)
  -> Identify top 1-5% by activity
Stage 2: Secondary screen (medium throughput, ~100-500 variants)
  -> Michaelis-Menten kinetics, thermal stability (Tm by DSF)
Stage 3: Characterization (low throughput, ~10-50 variants)
  -> Full kinetic profile, pH/temp optima, substrate specificity
Stage 4: Combination (5-20 variants)
  -> Combine beneficial mutations, test for additivity
```

---

## Evidence Grading

| Tier | Evidence Type | Confidence | Action |
|------|-------------|------------|--------|
| **T1** | Experimental: kinetics measured, stability validated, industrial conditions tested | Highest | Deploy in process |
| **T2** | Partial experimental: expressed, activity confirmed, basic characterization | High | Full characterization needed |
| **T3** | Computational: FoldX/Rosetta/ESM predictions, no experimental validation | Moderate | Experimental validation required |
| **T4** | Conceptual: literature-based design, no computation or experiment | Low | Computational and experimental validation needed |

---

## Multi-Agent Workflow Examples

**"Engineer a thermostable lipase for biodiesel production"**
1. Enzyme Engineering -> Characterize lipase, consensus design, B-factor analysis, disulfide engineering, stability predictions
2. Protein Structure Retrieval -> Lipase crystal structures with substrate analogs
3. Medicinal Chemistry -> Substrate (triglyceride) analysis if needed

**"Improve the substrate specificity of a transaminase for chiral amine synthesis"**
1. Enzyme Engineering -> Active site mapping, CAST/ISM design at binding pocket, LigandMPNN for new substrate
2. Protein Structure Retrieval -> Transaminase structures with PLP cofactor and substrate
3. Medicinal Chemistry -> Product analysis, enantiopurity assessment

**"Design a cascade reaction with cofactor regeneration"**
1. Enzyme Engineering -> Select enzymes, optimize individual activities, design cofactor regeneration, co-immobilization strategy
2. Systems Biology -> Metabolic context for cascade enzymes

**"Evolve an enzyme for a non-natural reaction"**
1. Enzyme Engineering -> PACE/PHAGE setup, link activity to selectable output, iterative evolution
2. Protein Therapeutic Design -> If enzyme is for therapeutic application
3. Protein Structure Retrieval -> Structures of enzymes with related activities

## Completeness Checklist

- [ ] Target enzyme characterized (structure, active site, cofactors, known kinetics)
- [ ] Engineering goal clearly defined (thermostability, specificity, activity, expression)
- [ ] Strategy selected and justified (directed evolution, rational, semi-rational, computational)
- [ ] Library design specified (mutagenesis method, library size, screening effort)
- [ ] Stability predictions made (consensus, FoldX, Rosetta, ESM) if applicable
- [ ] Active site analysis completed (catalytic residues, substrate contacts, first/second shell)
- [ ] Expression system selected (E. coli strain, Pichia, cell-free)
- [ ] Screening assay designed (colorimetric, fluorometric, FACS, microfluidic)
- [ ] Kinetic characterization protocol defined (Michaelis-Menten, specificity profiling)
- [ ] Evidence tier assigned to all predictions and recommendations
- [ ] Report file finalized with no `[Analyzing...]` placeholders remaining
