---
name: molecular-dynamics
description: "Molecular dynamics simulation using GROMACS and OpenMM. Simulates protein-ligand complexes, protein stability, binding free energy, and conformational dynamics. Covers energy minimization, NVT/NPT equilibration, production MD, and trajectory analysis (RMSD, RMSF, Rg, PCA, hydrogen bonds). Use when user mentions molecular dynamics, MD simulation, GROMACS, OpenMM, protein simulation, binding free energy, conformational dynamics, energy minimization, RMSD analysis, RMSF, radius of gyration, trajectory analysis, or force field simulation."
---

# Molecular Dynamics — GROMACS & OpenMM

> **Code recipes**: See [recipes.md](recipes.md) for copy-paste CLI/Python commands.

Molecular dynamics simulation for drug discovery and protein engineering. Simulates atomic-level dynamics of proteins, protein-ligand complexes, and biomolecular systems. Two engines: GROMACS (CLI, HPC-optimized) and OpenMM (Python API, rapid prototyping).

**When to use MD vs structure prediction:**
- **Structure prediction** (ColabFold, Boltz, Protenix) — static snapshots of likely structures
- **Molecular dynamics** (this skill) — dynamic behavior: binding kinetics, conformational changes, stability, free energy

## Report-First Workflow

1. **Create report file immediately**: `[system]_md_simulation_report.md`
2. **Populate progressively**: system setup → equilibration → production → analysis
3. **Final**: trajectory analysis with RMSD, RMSF, Rg, binding metrics

## When NOT to Use This Skill

- Structure prediction from sequence → use `colabfold-predict`, `boltz-predict`, etc.
- Protein design → use `rfdiffusion-design`, `proteinmpnn-design`, etc.
- Static binding affinity prediction → use `boltz-predict` (faster, approximate)

## Cross-Reference: Other Skills

- **Starting structures** → use colabfold-predict, boltz-predict, or alphafold-structures
- **Ligand docking before MD** → use boltz-predict for initial pose
- **Drug research context** → use drug-research skill for target/compound data
- **Designed protein stability** → use after protein-therapeutic-design for dynamics validation

## GROMACS (CLI)

### Installation

```bash
conda install -c conda-forge gromacs
```

### Standard Protein-Ligand MD Workflow

```
PDB → pdb2gmx (topology) → editconf (box) → solvate → genion
  → EM → NVT equilibration → NPT equilibration → Production MD
  → Analysis (RMSD, RMSF, Rg, Hbonds, PCA)
```

### Key Commands

| Command | Purpose |
|---------|---------|
| `gmx pdb2gmx` | Generate topology from PDB |
| `gmx editconf` | Set simulation box |
| `gmx solvate` | Add water molecules |
| `gmx genion` | Add ions (neutralize charge) |
| `gmx grompp` | Compile run input (.tpr) |
| `gmx mdrun` | Run simulation |
| `gmx energy` | Extract energy terms |
| `gmx rms` | RMSD analysis |
| `gmx rmsf` | Per-residue fluctuation |
| `gmx gyrate` | Radius of gyration |
| `gmx hbond` | Hydrogen bond analysis |
| `gmx covar` + `gmx anaeig` | PCA analysis |

### Force Fields

| Force Field | Use for |
|-------------|---------|
| `amber99sb-ildn` | General proteins (most validated) |
| `charmm36` | Proteins + lipids |
| `opls-aa` | Organic molecules |

### Simulation Parameters

| Phase | Timestep | Steps | Duration |
|-------|----------|-------|----------|
| Energy minimization | - | 50,000 | Until converged |
| NVT equilibration | 2 fs | 50,000 | 100 ps |
| NPT equilibration | 2 fs | 50,000 | 100 ps |
| Production MD | 2 fs | 50,000,000 | 100 ns |

## OpenMM (Python)

### Installation

```bash
conda install -c conda-forge openmm
pip install mdtraj  # for analysis
```

### Key API

```python
from openmm.app import *
from openmm import *
from openmm.unit import *

pdb = PDBFile('complex.pdb')
ff = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
system = ff.createSystem(pdb.topology, nonbondedMethod=PME,
                         nonbondedCutoff=1.0*nanometer, constraints=HBonds)
integrator = LangevinMiddleIntegrator(300*kelvin, 1/picosecond, 0.002*picoseconds)
simulation = Simulation(pdb.topology, system, integrator)
simulation.context.setPositions(pdb.positions)

# Energy minimization
simulation.minimizeEnergy()

# Production MD
simulation.reporters.append(DCDReporter('trajectory.dcd', 1000))
simulation.reporters.append(StateDataReporter('log.csv', 1000,
    step=True, potentialEnergy=True, temperature=True))
simulation.step(50000000)  # 100 ns
```

### Analysis with MDTraj

```python
import mdtraj as md
t = md.load('trajectory.dcd', top='complex.pdb')
rmsd = md.rmsd(t, t, 0)        # RMSD vs first frame
rmsf = md.rmsf(t, t, 0)        # Per-atom fluctuation
rg = md.compute_rg(t)           # Radius of gyration
```

## Common Workflows

### 1. Designed Protein Stability Assessment

After protein design, run 100 ns MD to check if the design is stable:
1. Get designed structure from ProteinMPNN + ColabFold validation
2. Run GROMACS: pdb2gmx → solvate → EM → NVT → NPT → 100 ns production
3. Analyze: RMSD (should plateau < 3A), RMSF (identify flexible regions), Rg (should be stable)

### 2. Drug-Target Binding Dynamics

After Boltz-2 docking, simulate the drug-target complex:
1. Get docked complex from Boltz-2 prediction
2. Parameterize ligand (ACPYPE or OpenFF)
3. Run 100 ns MD of the complex
4. Analyze: protein-ligand RMSD, hydrogen bonds, binding pocket RMSF

### 3. Binding Free Energy (MM/PBSA)

Estimate binding free energy from MD trajectory:
1. Run production MD of protein-ligand complex
2. Extract snapshots from stable trajectory region
3. Run `gmx_MMPBSA` for ΔG_bind estimation

### 4. Conformational Sampling for Structure Prediction Validation

Compare MD ensemble to predicted structures:
1. Run MD on the predicted structure
2. Cluster trajectory conformations
3. Compare cluster centroids to predictions from different tools

## Tiered Execution

### Tier 1 (first 5 min)
```
1. Prepare system (topology, solvation, ions)
2. Energy minimization
3. Brief NVT/NPT equilibration (100 ps each)
>>> CHECKPOINT: Report system setup <<<
```

### Tier 2 (next 30 min - hours)
```
4. Production MD (10-100 ns depending on system)
5. Basic analysis (RMSD, Rg)
>>> CHECKPOINT: Report equilibration and stability <<<
```

### Tier 3 (extended)
```
6. Extended production (100 ns - 1 us)
7. Full analysis (RMSF, PCA, H-bonds, MM/PBSA)
>>> FINAL: Complete dynamics report <<<
```

## Completeness Checklist

- [ ] Input structure prepared (from PDB, prediction, or design)
- [ ] Topology generated with appropriate force field
- [ ] System solvated and neutralized
- [ ] Energy minimization converged
- [ ] NVT and NPT equilibration completed
- [ ] Production MD run to adequate length
- [ ] RMSD analysis shows stable trajectory
- [ ] RMSF identifies flexible/rigid regions
- [ ] Rg confirms structural integrity
- [ ] Relevant binding/interaction metrics computed
