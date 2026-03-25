---
name: chai-predict
description: "Biomolecular structure prediction using Chai-1. Predicts 3D structures of proteins, ligands, DNA, RNA, glycans, and complexes with experimental restraint support. Unique capabilities: glycosylation modeling, crosslink/contact restraints, single-sequence mode (no MSA needed). Use when user mentions Chai, Chai-1, glycoprotein structure, glycan modeling, glycosylation prediction, restraint-guided folding, crosslink restraints, single-sequence prediction, or sugar chain structure."
---

# Chai-1 Biomolecular Structure Prediction

> **Code recipes**: See [recipes.md](recipes.md) for copy-paste CLI commands and Python analysis templates.

Multi-modal structure prediction using Chai-1 — proteins, ligands, DNA, RNA, glycans, and covalent modifications in a unified model. Uniquely supports experimental restraints (crosslinks, known contacts) as prediction inputs and glycan branching syntax.

**When to use Chai-1 vs alternatives:**
- **Glycoproteins or glycan-containing complexes** → Chai-1 (only tool with native glycan support)
- **Experimental restraints available** (crosslinks, known contacts) → Chai-1 (restraint-guided folding)
- **Quick single-sequence prediction** (no MSA generation) → Chai-1 (ESM embeddings, fast)
- **Protein-only structure validation** → `colabfold-predict` (faster for protein-only)
- **Drug docking with binding affinity** → `boltz-predict` (Boltz-2 has affinity prediction)
- **Pre-computed known structures** → `alphafold-structures`

## Report-First Workflow

1. **Create report file immediately**: `[complex]_chai_prediction_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Predicting...]`
3. **Populate progressively**: Update sections as predictions complete
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Predicting...]` placeholders remain

## When NOT to Use This Skill

- Protein-only structure prediction (no ligands/glycans) → use `colabfold-predict` (faster)
- Drug docking with binding affinity estimation → use `boltz-predict` (has affinity head)
- Pre-computed AlphaFold DB structures → use `alphafold-structures`
- Experimental PDB structure retrieval → use `pdb-structures`

## Cross-Reference: Other Skills

- **Protein-only prediction** → use colabfold-predict skill
- **Drug docking + affinity** → use boltz-predict skill
- **Antibody glycosylation modeling** → use antibody-engineering skill (design) then this skill (glycan prediction)
- **Glycoprotein therapeutic design** → use protein-therapeutic-design skill (design) then this skill (glycan validation)
- **Drug-target structural context** → use drug-research skill (report) with this skill (glycoprotein structure)

## Tool: Chai-1 CLI (`chai-lab fold`)

### Installation Check

```bash
chai-lab fold --help 2>/dev/null || pip install chai_lab
```

### Core Commands

```bash
# Basic folding
chai-lab fold input.fasta output_dir/

# With MSA server (better accuracy)
chai-lab fold --use-msa-server input.fasta output_dir/

# With templates
chai-lab fold --use-msa-server --use-templates-server input.fasta output_dir/

# With restraints
chai-lab fold --constraint-path restraints.csv input.fasta output_dir/
```

### Python API

```python
from chai_lab.chai1 import run_inference

candidates = run_inference(
    fasta_file="input.fasta",
    output_dir="output/",
    num_trunk_recycles=3,
    num_diffn_timesteps=200,
    num_diffn_samples=5,
    use_esm_embeddings=True,    # single-sequence mode (fast, no MSA)
    use_msa_server=False,       # set True for MSA-enhanced accuracy
    constraint_path=None,       # path to restraints CSV
    device="cuda:0",
)

# Access results
cif_paths = candidates.cif_paths
scores = candidates.ranking_data
```

## Input Format: FASTA with Entity Types

### Protein

```
>protein|name=my-protein
MKFLVLLFNILCLFPVLAENQDKGMAHISMDQELRRFKD
```

### Small-Molecule Ligand (SMILES)

```
>ligand|name=erlotinib
C=Cc1cccc(Nc2ncnc3cc(OCCOC)c(OCCOC)cc23)c1
```

### Modified Residues (CCD codes inline)

```
>protein|name=phosphorylated
RKDES(SEP)EESQAT(TPO)KQEL
```

Supported modifications: `SEP` (phosphoserine), `TPO` (phosphothreonine), `MSE` (selenomethionine), `PTR` (phosphotyrosine), any CCD code.

### Glycan (Branched Sugar Chains)

```
>glycan|name=n-linked-glycan
NAG(4-1 NAG(4-1 BMA(3-1 MAN)(6-1 MAN)))
```

Glycan syntax: `RESIDUE(BOND CHILD_RESIDUE(...))` where bond is `DONOR_ATOM-ACCEPTOR_ATOM`.

Common glycan residues: `NAG` (GlcNAc), `BMA` (beta-mannose), `MAN` (mannose), `GAL` (galactose), `FUC` (fucose), `SIA` (sialic acid).

### Complex Example (Protein + Ligand + Glycan)

```
>protein|name=receptor
MVTPEGNVSLVDESLLVHTS(SEP)DKGMA...
>ligand|name=drug
CC(=O)Oc1ccccc1C(=O)O
>glycan|name=n-glycan
NAG(4-1 NAG(4-1 BMA(3-1 MAN(3-1 MAN)(6-1 MAN))(6-1 MAN(3-1 MAN)(6-1 MAN))))
```

## Restraints (CSV Format)

Restraints guide prediction using experimental data (crosslinks, known contacts, covalent bonds).

### Contact Restraint

Force two residues to be close:

```csv
restraint_id,chainA,res_idxA,chainB,res_idxB,connection_type,confidence,min_distance,max_distance,comment
1,A,45,B,78,contact,1.0,0,8.0,crosslink XL-MS
2,A,120,A,200,contact,0.8,0,10.0,known disulfide
```

### Pocket Restraint

Guide a ligand to a binding pocket:

```csv
restraint_id,chainA,res_idxA,chainB,res_idxB,connection_type,confidence,min_distance,max_distance,comment
1,B,,A,45,pocket,1.0,0,6.0,active site
2,B,,A,78,pocket,1.0,0,6.0,active site
3,B,,A,82,pocket,1.0,0,6.0,active site
```

### Covalent Bond Restraint

Specify a covalent bond between protein and ligand:

```csv
restraint_id,chainA,res_idxA,atomA,chainB,res_idxB,atomB,connection_type,confidence,min_distance,max_distance,comment
1,A,82,SG,B,1,C3,covalent,1.0,1.0,2.0,covalent inhibitor
```

## Output Files

| File | Content |
|------|---------|
| `pred.model_idx_N.cif` | Predicted structure (N = sample index) |
| `scores.model_idx_N.npz` | Confidence metrics per sample |

### Confidence Metrics

| Metric | Range | Interpretation |
|--------|-------|---------------|
| `aggregate_score` | 0-1 | Combined ranking score (used to rank samples) |
| `ptm` | 0-1 | Predicted TM-score for full complex |
| `iptm` | 0-1 | Interface TM-score |
| `per_chain_ptm` | 0-1 per chain | Per-chain structural accuracy |
| `per_chain_pair_iptm` | 0-1 per pair | Pairwise interface accuracy |
| `plddt` | 0-1 per atom | Per-atom local confidence |
| `clash_score` | count | Steric clashes (lower = better) |

## Prediction Strategies

### Quick Single-Sequence (no MSA, fastest)

```bash
chai-lab fold input.fasta output/
# Uses ESM embeddings by default, no MSA generation needed
```

### MSA-Enhanced (best accuracy)

```bash
chai-lab fold --use-msa-server --use-templates-server input.fasta output/
```

### Restraint-Guided (experimental data available)

```bash
chai-lab fold --use-msa-server --constraint-path restraints.csv input.fasta output/
```

## Common Workflows

### 1. Glycoprotein Structure Prediction

1. Get protein sequence from UniProt
2. Identify glycosylation sites (N-linked: NxS/T motif; O-linked: Ser/Thr)
3. Write FASTA with protein + glycan chains linked at glycosylation sites
4. Run Chai-1 prediction
5. Analyze glycan orientation and protein-glycan contacts

### 2. Crosslink-Guided Complex Prediction

1. Obtain XL-MS crosslink data (residue pairs + distance constraints)
2. Write restraints CSV with crosslink contacts
3. Run Chai-1 with `--constraint-path`
4. Compare with and without restraints to assess impact

### 3. Antibody Fc Glycosylation

1. Get antibody Fc sequence
2. Define N297 glycan (core fucosylated biantennary)
3. Predict Fc + glycan structure
4. Assess glycan orientation relative to FcγR binding site

### 4. Covalent Drug-Protein Complex

1. Write FASTA with protein + ligand SMILES
2. Write restraints CSV with covalent bond specification
3. Run prediction
4. Verify covalent bond geometry

### 5. Quick Screening (Single-Sequence Mode)

1. Write FASTA with sequences (no MSA preparation needed)
2. Run Chai-1 (uses ESM embeddings automatically)
3. Get structure in seconds-to-minutes instead of hours
4. Use for rapid hypothesis testing before full MSA-enhanced runs

## Tiered Execution (Timeout Resilience)

### Tier 1 — MUST COMPLETE (first 5 min)
```
1. Write FASTA input with entity types
2. Run single-sequence prediction (no MSA, fastest)
3. Extract confidence scores and write to report
>>> CHECKPOINT: Write initial prediction results <<<
```

### Tier 2 — HIGH VALUE (next 10 min)
```
4. Run MSA-enhanced prediction for better accuracy
5. Apply restraints if experimental data available
6. Analyze per-chain and interface confidence
>>> CHECKPOINT: Write detailed structural analysis <<<
```

### Tier 3 — COMPLETE PICTURE (remaining time)
```
7. Template-guided prediction for comparison
8. Multiple samples for conformational diversity
9. Cross-validate with ColabFold or Boltz-2
>>> FINAL CHECKPOINT: Write complete report <<<
```

## Completeness Checklist

**Tier 1 (minimum viable prediction):**
- [ ] FASTA input written with correct entity types
- [ ] Chai-1 prediction completed (at least 1 sample)
- [ ] Confidence metrics extracted (pTM, ipTM, pLDDT)
- [ ] Predicted structure inspected for reasonable geometry
- [ ] Report file saved with initial results

**Tier 2 (standard prediction):**
- [ ] MSA-enhanced prediction completed
- [ ] Restraints applied if experimental data available
- [ ] Per-chain confidence assessed
- [ ] Glycan orientation analyzed (if glycoprotein)
- [ ] Interface quality assessed per chain pair

**Tier 3 (complete analysis):**
- [ ] Multiple samples generated and ranked
- [ ] Template comparison performed (if reference available)
- [ ] Cross-validated with Boltz-2 or ColabFold
- [ ] Clash scores checked
- [ ] Executive structural assessment summarized
