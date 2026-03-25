---
name: proteinmpnn-design
description: "Protein sequence design from structure using ProteinMPNN (inverse folding). Designs amino acid sequences predicted to fold into a given 3D backbone. Supports fixed residues, tied positions, homooligomer symmetry, amino acid bias, PSSM integration, and multi-chain design. Use when user mentions ProteinMPNN, inverse folding, sequence design from structure, protein design, backbone design, redesign protein sequence, fixed-backbone design, or computational protein design."
---

# ProteinMPNN — Inverse Folding / Sequence Design

> **Code recipes**: See [recipes.md](recipes.md) for copy-paste CLI commands and Python analysis templates.

Protein sequence design from 3D backbone structure using ProteinMPNN. Given a fixed backbone (from PDB, AlphaFold, RFdiffusion, or any structure), designs amino acid sequences predicted to fold into that structure. The standard tool for computational protein sequence design from the Baker lab.

**Where ProteinMPNN fits in the design pipeline:**
```
Structure (PDB/AlphaFold/RFdiffusion) → ProteinMPNN (this skill) → ColabFold/Boltz/Chai (validation)
```

**Key distinction from structure prediction tools**: ColabFold, Boltz-2, and Chai-1 predict structures from sequences (folding). ProteinMPNN does the reverse — it designs sequences from structures (inverse folding).

## Report-First Workflow

1. **Create report file immediately**: `[target]_proteinmpnn_design_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Designing...]`
3. **Populate progressively**: Update sections as designs are generated
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Designing...]` placeholders remain

## When NOT to Use This Skill

- Structure prediction from sequence → use `colabfold-predict`, `boltz-predict`, or `chai-predict`
- De novo backbone generation → use RFdiffusion (via `protein-therapeutic-design` skill concepts)
- Protein-ligand docking or affinity → use `boltz-predict`
- Antibody humanization strategy → use `antibody-engineering` (then this skill for CDR design)
- Pre-computed AlphaFold structures → use `alphafold-structures`

## Cross-Reference: Other Skills

- **Design validation (predict designed sequence)** → use colabfold-predict skill (protein-only) or boltz-predict (with ligands)
- **Full protein therapeutic pipeline** → use protein-therapeutic-design skill (combines ProteinMPNN with other tools)
- **Enzyme active site redesign** → use enzyme-engineering skill (context) then this skill (sequence design)
- **CDR loop redesign** → use antibody-engineering skill (strategy) then this skill (sequence design)
- **Glycoprotein design validation** → use chai-predict skill (glycan-aware structure prediction)

## Tool: ProteinMPNN CLI

ProteinMPNN is a Python script-based tool. All design runs use `protein_mpnn_run.py`.

### Installation Check

```bash
python ProteinMPNN/protein_mpnn_run.py --help 2>/dev/null || {
  git clone https://github.com/dauparas/ProteinMPNN.git
  pip install torch numpy
}
```

### Core Command

```bash
python ProteinMPNN/protein_mpnn_run.py \
  --pdb_path input.pdb \
  --out_folder output/ \
  --num_seq_per_target 8 \
  --sampling_temp "0.1" \
  --seed 37
```

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--pdb_path` | - | Input PDB file |
| `--pdb_path_chains` | all | Which chains to design (e.g., `"A B"`) |
| `--out_folder` | - | Output directory |
| `--num_seq_per_target` | 1 | Number of sequences to generate |
| `--sampling_temp` | `"0.1"` | Temperature(s) for sampling. Lower = more confident. Can specify multiple: `"0.1 0.2 0.3"` |
| `--batch_size` | 1 | Sequences per batch (increase for GPU utilization) |
| `--model_name` | `v_48_020` | Weight file. v_48_020 (0.20A noise) recommended |
| `--seed` | 0 | Random seed (0 = random) |
| `--backbone_noise` | 0.0 | Gaussian noise (A) added to backbone at inference |
| `--omit_AAs` | `"X"` | Amino acids to exclude (e.g., `"CX"` to ban cysteine) |
| `--use_soluble_model` | off | Use soluble-only model (avoids hydrophobic patches) |
| `--ca_only` | off | Use CA-only model (for low-resolution structures) |
| `--score_only` | 0 | Evaluate existing sequences without designing new ones |
| `--save_probs` | 0 | Save per-position probability distributions |
| `--save_score` | 0 | Save scores as .npz files |
| `--max_length` | 200000 | Maximum total residue count |

### Constraint Parameters

| Parameter | Description |
|-----------|-------------|
| `--chain_id_jsonl` | Specify designed vs fixed chains |
| `--fixed_positions_jsonl` | Fix specific residue positions |
| `--tied_positions_jsonl` | Tie positions to have same amino acid |
| `--omit_AA_jsonl` | Per-position amino acid exclusion |
| `--bias_AA_jsonl` | Global amino acid composition bias |
| `--bias_by_res_jsonl` | Per-residue amino acid bias matrix |
| `--pssm_jsonl` | PSSM-based bias from evolutionary profiles |
| `--pssm_multi` | PSSM blending weight (0.0 = pure MPNN, 1.0 = pure PSSM) |
| `--homooligomer` | 1 = tie all corresponding positions across identical chains |

### Batch Pipeline (Multiple PDBs)

```bash
# Step 1: Parse PDB folder to JSONL
python ProteinMPNN/helper_scripts/parse_multiple_chains.py \
  --input_path pdbs/ \
  --output_path parsed.jsonl

# Step 2: Assign designed vs fixed chains
python ProteinMPNN/helper_scripts/assign_fixed_chains.py \
  --input_path parsed.jsonl \
  --output_path chain_assignments.jsonl \
  --chain_list "A"  # chains to design

# Step 3: Fix specific positions (optional)
python ProteinMPNN/helper_scripts/make_fixed_positions_dict.py \
  --input_path parsed.jsonl \
  --output_path fixed_positions.jsonl \
  --chain_list "A" \
  --position_list "1 2 3 45 78"  # 1-based positions to fix

# Step 4: Run design
python ProteinMPNN/protein_mpnn_run.py \
  --jsonl_path parsed.jsonl \
  --chain_id_jsonl chain_assignments.jsonl \
  --fixed_positions_jsonl fixed_positions.jsonl \
  --out_folder output/ \
  --num_seq_per_target 8 \
  --sampling_temp "0.1"
```

## Model Variants

| Variant | Flag | Use when |
|---------|------|----------|
| **Vanilla** (default) | - | General protein design, most applications |
| **Soluble** | `--use_soluble_model` | Soluble protein design (avoids transmembrane hydrophobic patches) |
| **CA-only** | `--ca_only` | Low-resolution structures, coarse-grained models |

**Noise levels** (v_48_NNN): Higher noise = more robust to backbone imprecision.
- `v_48_002` (0.02A): For high-resolution experimental structures
- `v_48_010` (0.10A): For good computational models
- `v_48_020` (0.20A): **Default**, good balance for most uses
- `v_48_030` (0.30A): For noisy or uncertain backbones

## Output Format

FASTA files in `out_folder/seqs/PDBNAME.fa`:

```
>5L33, score=1.5874, global_score=1.5874, fixed_chains=[], designed_chains=['A'], model_name=v_48_020, seed=37
HMPEEEKAARLFIEALEKGDP...   (native/input sequence)
>T=0.1, sample=1, score=0.8221, global_score=0.8221, seq_recovery=0.5094
MINEEEKKALDFIEALEKADP...   (designed sequence 1)
>T=0.1, sample=2, score=0.7943, global_score=0.7943, seq_recovery=0.4811
MIPEEEKKALDFIEALEKADP...   (designed sequence 2)
```

**Interpreting scores:**
- **score** — average negative log probability over designed positions. Lower = more confident design.
- **global_score** — average over ALL positions (including fixed). Context-aware quality metric.
- **seq_recovery** — fraction of positions matching native sequence. Higher recovery at key positions suggests the backbone strongly constrains those residues.

**Score guidance:**
- score < 1.0: High confidence — backbone strongly constrains sequence
- score 1.0-1.5: Good — reasonable design, validate with structure prediction
- score 1.5-2.0: Moderate — consider optimizing backbone or constraints
- score > 2.0: Low confidence — backbone may be unfavorable

## Temperature Guidance

| Temperature | Character | Use for |
|-------------|-----------|---------|
| 0.1 | Conservative, high confidence | Final candidates for synthesis |
| 0.15-0.2 | Balanced diversity | Exploring sequence space, library design |
| 0.25-0.3 | High diversity | Maximum exploration, directed evolution seeds |

## Common Workflows

### 1. Basic Sequence Design

1. Obtain backbone structure (PDB download or AlphaFold prediction)
2. Run ProteinMPNN to generate 8-16 sequences at T=0.1
3. Validate top sequences with ColabFold (self-consistency check)
4. Select sequences with pLDDT > 80 and RMSD < 1.5A to target

### 2. Design-Predict-Validate Loop

1. **Design**: ProteinMPNN generates sequences from backbone
2. **Predict**: ColabFold/Boltz/Chai predicts structure from each sequence
3. **Compare**: RMSD between predicted and target backbone
4. **Filter**: Keep sequences where prediction matches target (self-consistent designs)

### 3. Interface Redesign (Fixed Core)

1. Fix all positions except the interface
2. Design interface residues for improved binding
3. Validate complex with ColabFold-Multimer or Boltz-2

### 4. Homooligomer Design

1. Use `--homooligomer 1` to tie corresponding positions across chains
2. Design once, symmetry enforced automatically
3. Validate with multimer prediction

### 5. Score Existing Sequences

1. Use `--score_only 1` to evaluate sequences without designing
2. Compare natural vs designed sequences
3. Identify positions where the backbone strongly constrains amino acid identity

## Tiered Execution (Timeout Resilience)

### Tier 1 — MUST COMPLETE (first 3 min)
```
1. Prepare PDB input (download or extract from prediction)
2. Run ProteinMPNN with --num_seq_per_target 4 --sampling_temp "0.1"
3. Save designed sequences to report
>>> CHECKPOINT: Write initial designs <<<
```

### Tier 2 — HIGH VALUE (next 5 min)
```
4. Run with constraints (fixed positions, AA bias)
5. Generate diverse sequences at multiple temperatures
6. Score all designs and rank by confidence
>>> CHECKPOINT: Write constrained designs <<<
```

### Tier 3 — COMPLETE PICTURE (remaining time)
```
7. Validate top designs with ColabFold (self-consistency)
8. Compare designs across temperatures
9. Generate final recommendations
>>> FINAL CHECKPOINT: Write validated design report <<<
```

## Completeness Checklist

**Tier 1 (minimum viable design):**
- [ ] Input backbone PDB prepared
- [ ] ProteinMPNN run completed (at least 4 sequences)
- [ ] Design scores reported (score, global_score, seq_recovery)
- [ ] Top sequences saved to FASTA
- [ ] Report file saved with initial designs

**Tier 2 (standard design):**
- [ ] Constraints applied (fixed positions, chain assignments)
- [ ] Multiple temperatures sampled for diversity
- [ ] Amino acid bias applied if needed (solubility, no Cys, etc.)
- [ ] All sequences ranked by score
- [ ] Design rationale documented

**Tier 3 (complete design):**
- [ ] Top designs validated with ColabFold/Boltz (self-consistency)
- [ ] Self-consistent designs identified (RMSD < 1.5A, pLDDT > 80)
- [ ] Sequence diversity analyzed across designs
- [ ] Final candidate recommendations with confidence assessment
