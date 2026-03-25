---
name: boltz-predict
description: "Biomolecular structure and affinity prediction using Boltz-2. Predicts 3D structures of protein-ligand complexes, protein-nucleic acid complexes, and multi-chain assemblies with binding affinity estimation. Supports SMILES ligands, CCD codes, covalent modifications, pocket conditioning, contact constraints, and template forcing. Use when user mentions Boltz, protein-ligand docking, binding affinity prediction, molecular docking, ligand binding, pocket docking, covalent docking, protein-DNA complex, protein-RNA complex, biomolecular complex prediction, or structure-based drug design."
---

# Boltz-2 Biomolecular Structure & Affinity Prediction

> **Code recipes**: See [recipes.md](recipes.md) for copy-paste CLI commands and Python analysis templates.

Biomolecular structure and binding affinity prediction using Boltz-2 — the first open-source model to jointly predict complex structures and binding affinities at FEP-grade accuracy, 1000x faster than physics-based methods. Predicts 3D structures for proteins, DNA, RNA, small-molecule ligands, covalent modifications, and their interactions.

**Key distinction from `colabfold-predict`**: ColabFold predicts protein-only structures (monomers and multimers). Boltz-2 handles the full biomolecular spectrum — protein-ligand complexes, nucleic acids, covalent mods, and uniquely provides binding affinity predictions. Use ColabFold for fast protein-only screening; use Boltz-2 when ligands, nucleic acids, or affinity estimates are needed.

**When to use Chai-1 instead**: If your prediction involves glycans/glycoproteins, you have experimental restraints (crosslinks, known contacts) to guide folding, or you want fast single-sequence mode without MSA, use the `chai-predict` skill. Boltz-2 is better for binding affinity estimation; Chai-1 is better for glycan modeling and restraint-guided predictions.

**When to use Protenix instead**: If you need highest benchmark accuracy, are predicting hard targets (Ab-Ag), or want inference-time scaling (100+ candidates for log-linear accuracy gains), use the `protenix-predict` skill. Boltz-2 remains the only tool with binding affinity prediction.

## Report-First Workflow

1. **Create report file immediately**: `[complex]_boltz_prediction_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Predicting...]`
3. **Populate progressively**: Update sections as predictions complete
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Predicting...]` placeholders remain

## When NOT to Use This Skill

- Protein-only structure prediction (no ligands) → use `colabfold-predict` (faster for protein-only)
- Pre-computed AlphaFold DB structures → use `alphafold-structures`
- Experimental PDB structure retrieval → use `pdb-structures`
- Protein sequence/function lookups → use UniProt tools
- SAR-driven compound optimization → use `medicinal-chemistry`
- ADMET filtering and drug-likeness → use `binder-discovery-specialist`

## Cross-Reference: Other Skills

- **Protein-only structure prediction** → use colabfold-predict skill (faster, no ligand support)
- **Pre-computed AlphaFold DB structures** → use alphafold-structures skill
- **Hit-to-lead compound prioritization** → use binder-discovery-specialist skill (MCP data) then this skill (docking)
- **Drug-target structural assessment** → use drug-research skill (report) with this skill (structural prediction)
- **Molecular glue ternary complexes** → use molecular-glue-discovery skill (design) then this skill (ternary modeling)
- **Protein therapeutic design validation** → use protein-therapeutic-design skill (design) then this skill (complex prediction)

## Tool: Boltz CLI (`boltz predict`)

Boltz is available as a command-line tool. All predictions run via Bash.

### Installation Check

```bash
boltz predict --help 2>/dev/null || pip install boltz[cuda] -U
```

### Core Command

```bash
boltz predict input.yaml [OPTIONS]
```

### Key Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--out_dir` | `./` | Output directory |
| `--recycling_steps` | 3 | Recycling iterations (10 for AF3-matched quality) |
| `--diffusion_samples` | 1 | Number of structure samples (25 for AF3-matched) |
| `--sampling_steps` | 200 | Diffusion sampling steps |
| `--output_format` | `mmcif` | Output: `mmcif` or `pdb` |
| `--use_msa_server` | off | Auto-generate MSAs via MMseqs2 API |
| `--use_potentials` | off | Inference-time potentials for physical plausibility |
| `--devices` | 1 | Number of GPUs |
| `--accelerator` | `gpu` | `gpu`, `cpu`, or `tpu` |
| `--write_full_pae` | off | Save full PAE matrix (.npz) |
| `--write_full_pde` | off | Save full PDE matrix (.npz) |
| `--step_scale` | 1.638 | Diffusion temperature (lower = more diverse samples) |
| `--no_kernels` | off | Disable cuEquivariance (for older GPUs) |
| `--override` | off | Force re-prediction over cached results |

### Affinity-Specific Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--diffusion_samples_affinity` | 5 | Samples for affinity estimation |
| `--sampling_steps_affinity` | 200 | Diffusion steps for affinity |
| `--affinity_mw_correction` | off | Molecular weight correction |

## Input Format: YAML

YAML is the primary input format. It supports all features: ligands, modifications, constraints, templates, and affinity prediction.

### Basic Protein-Ligand Complex

```yaml
version: 1
sequences:
  - protein:
      id: A
      sequence: MVTPEGNVSLVDESLL...
  - ligand:
      id: B
      smiles: 'CC(=O)Oc1ccccc1C(=O)O'
```

### Protein-Ligand with Affinity Prediction

```yaml
version: 1
sequences:
  - protein:
      id: A
      sequence: MVTPEGNVSLVDESLL...
  - ligand:
      id: B
      smiles: 'CC(=O)Oc1ccccc1C(=O)O'
properties:
  - affinity:
      binder: B
```

### Ligand via CCD Code

```yaml
version: 1
sequences:
  - protein:
      id: A
      sequence: MSEQVENCE...
  - ligand:
      id: B
      ccd: ATP
```

### Protein-DNA Complex

```yaml
version: 1
sequences:
  - protein:
      id: A
      sequence: MPROTEINSEQUENCE...
  - dna:
      id: B
      sequence: ATCGATCGATCG
  - dna:
      id: C
      sequence: CGATCGATCGAT
```

### Pocket-Conditioned Docking

```yaml
version: 1
sequences:
  - protein:
      id: A
      sequence: MPROTEINSEQUENCE...
  - ligand:
      id: B
      smiles: 'c1ccccc1'
constraints:
  - pocket:
      binder: B
      contacts:
        - [A, 45]
        - [A, 78]
        - [A, 82]
        - [A, 153]
      max_distance: 6.0
```

### Covalent Modification

```yaml
version: 1
sequences:
  - protein:
      id: A
      sequence: MPROTEINSEQUENCE...
      modifications:
        - position: 153
          ccd: SEP    # phosphoserine
  - ligand:
      id: B
      smiles: 'CC(=O)Cl'
constraints:
  - bond:
      - [A, 82, SG]     # Cysteine sulfur
      - [B, 1, C1]       # Ligand carbon
```

### Template-Guided Prediction

```yaml
version: 1
sequences:
  - protein:
      id: A
      sequence: MPROTEINSEQUENCE...
      templates:
        - cif_path: template.cif
          chain_id: A
          force: true
          threshold: 2.0    # keep within 2A of template backbone
```

### Contact Constraints

```yaml
version: 1
sequences:
  - protein:
      id: A
      sequence: MFIRSTPROTEIN...
  - protein:
      id: B
      sequence: MSECONDPROTEIN...
constraints:
  - contact:
      - [A, 45, CA]
      - [B, 78, CA]
      max_distance: 8.0
```

### Cyclic Peptide

```yaml
version: 1
sequences:
  - protein:
      id: A
      sequence: CYCLICPEPTIDE
      cyclic: true
```

### MSA Options

```yaml
# Pre-computed MSA
sequences:
  - protein:
      id: A
      sequence: MSEQ...
      msa: path/to/alignment.a3m

# No MSA (single-sequence mode)
sequences:
  - protein:
      id: A
      sequence: MSEQ...
      msa: empty

# Auto-generate (use --use_msa_server flag instead)
```

## Output Files

For each prediction:

| File | Content |
|------|---------|
| `*_model_0.cif` / `.pdb` | Predicted structure (pLDDT in B-factor) |
| `confidence_*_model_0.json` | Confidence metrics (pLDDT, pTM, ipTM, ligand_ipTM) |
| `affinity_*.json` | Binding affinity + binary binding probability |
| `pae_*.npz` | Predicted Aligned Error matrix (with `--write_full_pae`) |
| `pde_*.npz` | Predicted Distance Error matrix (with `--write_full_pde`) |
| `plddt_*.npz` | Per-token pLDDT scores |

### Confidence Metrics

| Metric | Range | Interpretation |
|--------|-------|---------------|
| `confidence_score` | 0-1 | Overall ranking score (0.8 * pLDDT + 0.2 * ipTM) |
| `ptm` | 0-1 | Predicted TM-score for full complex |
| `iptm` | 0-1 | Interface TM-score (all interfaces) |
| `ligand_iptm` | 0-1 | ipTM at protein-ligand interfaces specifically |
| `protein_iptm` | 0-1 | ipTM at protein-protein interfaces |
| `complex_plddt` | 0-1 | Average predicted LDDT across all tokens |
| `complex_iplddt` | 0-1 | Interface-weighted pLDDT |
| `complex_pde` | Angstroms | Predicted distance error (lower = better) |
| `pair_chains_iptm` | 0-1 per pair | Pairwise interface TM between chain pairs |

### Affinity Metrics

| Metric | Description |
|--------|-------------|
| `affinity_pred_value` | Predicted log10(IC50) in micromolar. Lower = more potent. |
| `affinity_probability_binary` | 0-1 probability of being a binder. Use for hit screening. |

**When to use which:**
- **Hit discovery** (binder vs decoy): use `affinity_probability_binary` > 0.5
- **Hit-to-lead / lead optimization**: use `affinity_pred_value` to rank compounds by potency
- **SAR analysis**: compare `affinity_pred_value` across analog series

## Prediction Strategies

### Quick Docking (screening)

For rapid virtual screening of many compounds:
```bash
boltz predict input.yaml --diffusion_samples 1 --recycling_steps 3 --output_format pdb
```

### High-Quality Prediction

For publication-grade structures:
```bash
boltz predict input.yaml --recycling_steps 10 --diffusion_samples 25 --use_msa_server --use_potentials --output_format pdb --write_full_pae
```

### Affinity-Focused

For binding affinity estimation:
```bash
boltz predict input.yaml --diffusion_samples_affinity 5 --sampling_steps_affinity 200 --affinity_mw_correction --use_msa_server
```

### Pocket-Conditioned Docking

For docking to a specific binding site:
```bash
boltz predict pocket_input.yaml --use_potentials --diffusion_samples 10 --use_msa_server
```

### Template-Guided

For prediction guided by known structure:
```bash
boltz predict template_input.yaml --use_potentials --recycling_steps 10
```

## Common Workflows

### 1. Drug-Target Docking Pipeline

1. Get target sequence from UniProt (via `drug-research` or `binder-discovery-specialist`)
2. Get ligand SMILES from ChEMBL/PubChem (via `binder-discovery-specialist`)
3. Write Boltz YAML with protein + ligand + affinity
4. Run `boltz predict` with pocket conditioning if binding site known
5. Analyze confidence (ligand_iptm > 0.5 = plausible) and affinity

### 2. Virtual Screening

1. Get target pocket residues from PDB co-crystal
2. Generate YAML files for each compound (pocket-conditioned)
3. Batch predict: `boltz predict compounds_dir/`
4. Rank by `affinity_probability_binary` (hit discovery) or `affinity_pred_value` (potency)

### 3. Molecular Glue Ternary Complex

1. Get E3 ligase + substrate sequences
2. Write YAML with E3:substrate:glue as three chains
3. Run with potentials for physical plausibility
4. Check interface metrics between all three chains

### 4. Covalent Inhibitor Docking

1. Identify reactive residue (Cys, Ser, Lys)
2. Write YAML with covalent bond constraint
3. Run prediction
4. Verify covalent bond geometry in output

### 5. Protein-Nucleic Acid Complex

1. Get protein sequence + DNA/RNA sequence
2. Write YAML with both chains
3. Run prediction with MSA server
4. Analyze interface confidence for binding specificity

## Tiered Execution (Timeout Resilience)

### Tier 1 — MUST COMPLETE (first 5 min)
```
1. Write YAML input file with sequences and constraints
2. Run quick prediction (--diffusion_samples 1 --recycling_steps 3)
3. Extract confidence scores and write to report
>>> CHECKPOINT: Write initial prediction results <<<
```

### Tier 2 — HIGH VALUE (next 15 min)
```
4. Run high-quality prediction (--diffusion_samples 10 --use_potentials)
5. If affinity requested, run affinity prediction
6. Analyze ligand_iptm and binding pose quality
>>> CHECKPOINT: Write structural and affinity analysis <<<
```

### Tier 3 — COMPLETE PICTURE (remaining time)
```
7. Run with MSA server for deeper evolutionary context
8. Multiple samples for conformational diversity
9. Template-guided comparison if reference structure available
>>> FINAL CHECKPOINT: Write complete report <<<
```

## Completeness Checklist

**Tier 1 (minimum viable prediction):**
- [ ] YAML input written with correct sequences and entity types
- [ ] Boltz prediction completed (at least 1 sample)
- [ ] Confidence metrics extracted (pLDDT, ipTM, ligand_iptm)
- [ ] Predicted structure inspected for reasonable poses
- [ ] Report file saved with initial results

**Tier 2 (standard prediction):**
- [ ] Multiple diffusion samples ranked by confidence
- [ ] Affinity prediction completed (if ligand present)
- [ ] Pocket conditioning or constraints applied (if binding site known)
- [ ] Interface quality assessed per chain pair
- [ ] Cross-referenced with experimental data if available

**Tier 3 (complete analysis):**
- [ ] MSA-informed prediction for deeper context
- [ ] Potentials applied for physical plausibility
- [ ] Template comparison performed (if reference available)
- [ ] PAE/PDE matrices analyzed for domain confidence
- [ ] Executive structural assessment summarized
