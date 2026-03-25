# Molecular Dynamics Recipes

> Copy-paste CLI (GROMACS) and Python (OpenMM) commands for MD simulation.
> Parent skill: [SKILL.md](SKILL.md) — full MD workflow and analysis guide.

---

## Recipe 1: GROMACS — Protein-Only Simulation (100 ns)

```bash
# 1. Generate topology (AMBER force field, TIP3P water)
gmx pdb2gmx -f protein.pdb -o protein.gro -water tip3p -ff amber99sb-ildn

# 2. Define box (1.0 nm buffer, cubic)
gmx editconf -f protein.gro -o box.gro -c -d 1.0 -bt cubic

# 3. Solvate
gmx solvate -cp box.gro -cs spc216.gro -o solvated.gro -p topol.top

# 4. Add ions (neutralize)
gmx grompp -f ions.mdp -c solvated.gro -p topol.top -o ions.tpr -maxwarn 1
echo "SOL" | gmx genion -s ions.tpr -o system.gro -p topol.top -pname NA -nname CL -neutral

# 5. Energy minimization
cat > em.mdp << 'MDP'
integrator = steep
nsteps = 50000
emtol = 1000.0
emstep = 0.01
MDP
gmx grompp -f em.mdp -c system.gro -p topol.top -o em.tpr
gmx mdrun -v -deffnm em

# 6. NVT equilibration (100 ps, 300 K)
cat > nvt.mdp << 'MDP'
integrator = md
dt = 0.002
nsteps = 50000
tcoupl = V-rescale
ref_t = 300
tc-grps = Protein Non-Protein
tau_t = 0.1 0.1
constraints = h-bonds
nstxout-compressed = 1000
MDP
gmx grompp -f nvt.mdp -c em.gro -r em.gro -p topol.top -o nvt.tpr
gmx mdrun -deffnm nvt

# 7. NPT equilibration (100 ps, 1 bar)
cat > npt.mdp << 'MDP'
integrator = md
dt = 0.002
nsteps = 50000
tcoupl = V-rescale
ref_t = 300
tc-grps = Protein Non-Protein
tau_t = 0.1 0.1
pcoupl = Parrinello-Rahman
ref_p = 1.0
tau_p = 2.0
constraints = h-bonds
nstxout-compressed = 1000
MDP
gmx grompp -f npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -o npt.tpr
gmx mdrun -deffnm npt

# 8. Production MD (100 ns)
cat > md.mdp << 'MDP'
integrator = md
dt = 0.002
nsteps = 50000000
tcoupl = V-rescale
ref_t = 300
tc-grps = Protein Non-Protein
tau_t = 0.1 0.1
pcoupl = Parrinello-Rahman
ref_p = 1.0
tau_p = 2.0
constraints = h-bonds
nstxout-compressed = 5000
MDP
gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -o md.tpr
gmx mdrun -deffnm md -nb gpu
```

---

## Recipe 2: GROMACS — Trajectory Analysis

```bash
# RMSD (backbone vs first frame)
echo "Backbone Backbone" | gmx rms -s md.tpr -f md.xtc -o rmsd.xvg -tu ns

# Per-residue RMSF
echo "Backbone" | gmx rmsf -s md.tpr -f md.xtc -o rmsf.xvg -res

# Radius of gyration
echo "Protein" | gmx gyrate -s md.tpr -f md.xtc -o gyrate.xvg

# Hydrogen bonds (protein internal)
echo "Protein Protein" | gmx hbond -s md.tpr -f md.xtc -num hbonds.xvg

# Energy terms
echo "Potential Temperature Pressure" | gmx energy -f md.edr -o energy.xvg
```

---

## Recipe 3: OpenMM — Protein Simulation (Python)

```python
from openmm.app import *
from openmm import *
from openmm.unit import *

# Load structure
pdb = PDBFile('protein.pdb')
forcefield = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')

# Build system
modeller = Modeller(pdb.topology, pdb.positions)
modeller.addSolvent(forcefield, model='tip3p', padding=1.0*nanometer)
system = forcefield.createSystem(modeller.topology,
    nonbondedMethod=PME, nonbondedCutoff=1.0*nanometer, constraints=HBonds)
system.addForce(MonteCarloBarostat(1*bar, 300*kelvin))

# Setup simulation
integrator = LangevinMiddleIntegrator(300*kelvin, 1/picosecond, 0.002*picoseconds)
simulation = Simulation(modeller.topology, system, integrator)
simulation.context.setPositions(modeller.positions)

# Energy minimization
print("Minimizing...")
simulation.minimizeEnergy()

# Equilibration (100 ps)
simulation.step(50000)

# Production (100 ns)
simulation.reporters.append(DCDReporter('trajectory.dcd', 5000))
simulation.reporters.append(StateDataReporter('log.csv', 5000,
    step=True, time=True, potentialEnergy=True, temperature=True,
    speed=True, totalSteps=50000000))

print("Running production MD (100 ns)...")
simulation.step(50000000)
simulation.saveState('final_state.xml')
```

---

## Recipe 4: MDTraj Analysis (for OpenMM trajectories)

```python
import mdtraj as md
import numpy as np

t = md.load('trajectory.dcd', top='protein.pdb')

# RMSD vs first frame
rmsd = md.rmsd(t, t, 0)
print(f"Final RMSD: {rmsd[-1]:.3f} nm")
print(f"Mean RMSD (last 50%): {np.mean(rmsd[len(rmsd)//2:]):.3f} nm")

# Per-residue RMSF
rmsf = md.rmsf(t, t, 0)
ca_indices = t.topology.select('name CA')
ca_rmsf = rmsf[ca_indices]
print(f"\nTop 5 most flexible residues (RMSF):")
for idx in np.argsort(ca_rmsf)[-5:][::-1]:
    res = list(t.topology.residues)[idx]
    print(f"  {res}: {ca_rmsf[idx]:.3f} nm")

# Radius of gyration
rg = md.compute_rg(t)
print(f"\nRg: {np.mean(rg):.3f} ± {np.std(rg):.3f} nm")

# Hydrogen bonds
hbonds = md.baker_hubbard(t)
print(f"Average hydrogen bonds: {len(hbonds)}")
```

---

## Recipe 5: Designed Protein Stability Check

After protein design (ProteinMPNN + ColabFold), run MD to verify stability.

```bash
# Start from ColabFold-validated design
# Run GROMACS workflow (Recipe 1) on the validated PDB
# Key checks:
echo "Backbone Backbone" | gmx rms -s md.tpr -f md.xtc -o rmsd.xvg -tu ns

python3 << 'PYTHON'
# Quick stability assessment
import numpy as np
data = np.loadtxt("rmsd.xvg", comments=["#", "@"])
time, rmsd = data[:, 0], data[:, 1]

mean_rmsd_last_half = np.mean(rmsd[len(rmsd)//2:])
max_rmsd = np.max(rmsd)
final_rmsd = rmsd[-1]

print(f"Stability Assessment:")
print(f"  Final RMSD: {final_rmsd:.3f} nm")
print(f"  Mean RMSD (last 50%): {mean_rmsd_last_half:.3f} nm")
print(f"  Max RMSD: {max_rmsd:.3f} nm")

if mean_rmsd_last_half < 0.3:
    print("  STABLE — design maintains fold throughout simulation")
elif mean_rmsd_last_half < 0.5:
    print("  MODERATE — some conformational drift, review flexible regions")
else:
    print("  UNSTABLE — design unfolds or significantly rearranges")
PYTHON
```

---

## Recipe 6: Drug-Target Binding Dynamics (Post-Boltz Docking)

After Boltz-2 docking, run MD on the complex to assess binding stability.

```bash
# Start from Boltz-2 docked complex PDB
# Note: ligand parameterization needed (ACPYPE or OpenFF)

# Parameterize ligand with ACPYPE
acpype -i ligand.pdb -c bcc -a gaff2

# Combine protein + ligand topologies
# ... (manual topology editing — see GROMACS ligand tutorial)

# Run full MD workflow (Recipe 1) on the complex

# Analyze ligand binding stability
echo "Protein LIG" | gmx rms -s md.tpr -f md.xtc -o ligand_rmsd.xvg -tu ns

# Protein-ligand hydrogen bonds
echo "Protein LIG" | gmx hbond -s md.tpr -f md.xtc -num prot_lig_hbonds.xvg
```
