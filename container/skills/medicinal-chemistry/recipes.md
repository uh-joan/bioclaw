# Medicinal Chemistry Code Recipes

Executable code templates for computational chemistry using RDKit and DeepChem.
Each recipe is 15-30 lines of working Python with inline comments.

---

## Recipe 1: Parse SMILES and Calculate Lipinski Descriptors

Use when you need a quick physicochemical profile of a compound.

```python
from rdkit import Chem
from rdkit.Chem import Descriptors

smiles = "CC(=O)Oc1ccccc1C(=O)O"  # Aspirin
mol = Chem.MolFromSmiles(smiles)
assert mol is not None, f"Invalid SMILES: {smiles}"

# Calculate Lipinski Rule-of-Five descriptors
mw = Descriptors.MolWt(mol)                  # Molecular weight (< 500)
logp = Descriptors.MolLogP(mol)              # Partition coefficient (< 5)
hbd = Descriptors.NumHDonors(mol)            # H-bond donors (< 5)
hba = Descriptors.NumHAcceptors(mol)         # H-bond acceptors (< 10)
tpsa = Descriptors.TPSA(mol)                # Topological polar surface area
rot_bonds = Descriptors.NumRotatableBonds(mol)  # Rotatable bonds

print(f"MW={mw:.1f}  LogP={logp:.2f}  HBD={hbd}  HBA={hba}  TPSA={tpsa:.1f}  RotBonds={rot_bonds}")

# Check Lipinski compliance (allow at most 1 violation)
violations = sum([mw > 500, logp > 5, hbd > 5, hba > 10])
print(f"Lipinski violations: {violations} -> {'PASS' if violations <= 1 else 'FAIL'}")
```

---

## Recipe 2: Morgan Fingerprints and Tanimoto Similarity

Use when comparing structural similarity between two molecules.

```python
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem

mol1 = Chem.MolFromSmiles("c1ccc(CC(=O)O)cc1")   # Phenylacetic acid
mol2 = Chem.MolFromSmiles("c1ccc(CCC(=O)O)cc1")  # Hydrocinnamic acid

# Generate Morgan fingerprints (radius=2 ~ ECFP4, 2048-bit)
fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, radius=2, nBits=2048)
fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, radius=2, nBits=2048)

# Tanimoto similarity (1.0 = identical, 0.0 = no overlap)
similarity = DataStructs.TanimotoSimilarity(fp1, fp2)
print(f"Tanimoto similarity: {similarity:.3f}")

# Bulk comparison against a library
library_smiles = ["c1ccccc1", "CC(=O)O", "c1ccc(CC(=O)O)cc1"]
library_fps = [AllChem.GetMorganFingerprintAsBitVect(Chem.MolFromSmiles(s), 2, nBits=2048)
               for s in library_smiles]
scores = [(s, DataStructs.TanimotoSimilarity(fp1, fp)) for s, fp in zip(library_smiles, library_fps)]
scores.sort(key=lambda x: x[1], reverse=True)
for smi, score in scores:
    print(f"  {smi:30s}  Tanimoto={score:.3f}")
```

---

## Recipe 3: Substructure Search with SMARTS

Use when filtering molecules for a specific functional group or pattern.

```python
from rdkit import Chem

# SMARTS pattern for a carboxylic acid group
pattern = Chem.MolFromSmarts("[CX3](=O)[OX2H1]")

smiles_list = [
    "CC(=O)O",           # Acetic acid (has COOH)
    "c1ccccc1",          # Benzene (no COOH)
    "OC(=O)c1ccccc1",   # Benzoic acid (has COOH)
    "CC(=O)N",           # Acetamide (no COOH)
    "OC(=O)CC(=O)O",    # Malonic acid (two COOH)
]

for smi in smiles_list:
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        continue
    n_matches = len(mol.GetSubstructMatches(pattern))
    status = f"{n_matches} match(es)" if n_matches > 0 else "no match"
    print(f"  {smi:25s}  -> {status}")
```

---

## Recipe 4: Batch SDF File Processing with Property Calculation

Use when processing an SD file and computing properties for each molecule.

```python
from rdkit import Chem
from rdkit.Chem import Descriptors
import csv, sys

supplier = Chem.SDMolSupplier("compounds.sdf", removeHs=True)

writer = csv.writer(sys.stdout)
writer.writerow(["Name", "SMILES", "MW", "LogP", "TPSA", "HBA", "HBD"])

for mol in supplier:
    if mol is None:
        continue  # Skip unparseable entries
    name = mol.GetProp("_Name") if mol.HasProp("_Name") else "unknown"
    smiles = Chem.MolToSmiles(mol)
    writer.writerow([
        name, smiles,
        f"{Descriptors.MolWt(mol):.1f}",
        f"{Descriptors.MolLogP(mol):.2f}",
        f"{Descriptors.TPSA(mol):.1f}",
        Descriptors.NumHAcceptors(mol),
        Descriptors.NumHDonors(mol),
    ])
```

---

## Recipe 5: Molecular Standardization

Use when preparing molecules for consistent database storage or comparison.

```python
from rdkit import Chem
from rdkit.Chem.MolStandardize import rdMolStandardize

raw_smiles = "[Na+].OC(=O)c1ccccc1.[Cl-]"  # Salt form with counterions
mol = Chem.MolFromSmiles(raw_smiles)
assert mol is not None, f"Invalid SMILES: {raw_smiles}"

# Remove salt fragments, keep the largest organic fragment
mol = rdMolStandardize.LargestFragmentChooser().choose(mol)
# Neutralize formal charges where possible
mol = rdMolStandardize.Uncharger().uncharge(mol)
# Normalize functional group representations
mol = rdMolStandardize.Normalizer().normalize(mol)
# Generate canonical SMILES
canonical = Chem.MolToSmiles(mol)
print(f"Raw: {raw_smiles}  ->  Standardized: {canonical}")

# Reusable helper function
def standardize(smiles: str) -> str | None:
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        return None
    m = rdMolStandardize.LargestFragmentChooser().choose(m)
    m = rdMolStandardize.Uncharger().uncharge(m)
    m = rdMolStandardize.Normalizer().normalize(m)
    return Chem.MolToSmiles(m)
```

---

## Recipe 6: 3D Conformer Generation and MMFF Optimization

Use when you need a 3D structure for docking, shape analysis, or visualization.

```python
from rdkit import Chem
from rdkit.Chem import AllChem

smiles = "c1ccc(NC(=O)C2CC2)cc1"  # An aniline amide
mol = Chem.MolFromSmiles(smiles)
mol = Chem.AddHs(mol)  # Explicit hydrogens needed for 3D

# Generate conformers using ETKDG distance geometry
params = AllChem.ETKDGv3()
params.randomSeed = 42
params.numThreads = 0  # Use all available cores
conf_ids = AllChem.EmbedMultipleConfs(mol, numConfs=10, params=params)
print(f"Generated {len(conf_ids)} conformers")

# Optimize each with MMFF94 force field
results = AllChem.MMFFOptimizeMoleculeConfs(mol, maxIters=500)
for cid, (converged, energy) in zip(conf_ids, results):
    status = "converged" if converged == 0 else "not converged"
    print(f"  Conformer {cid}: energy={energy:.2f} kcal/mol ({status})")

# Write lowest-energy conformer to SDF
best_idx = min(range(len(results)), key=lambda i: results[i][1])
writer = Chem.SDWriter("best_conformer.sdf")
writer.write(mol, confId=conf_ids[best_idx])
writer.close()
```

---

## Recipe 7: Murcko Scaffold Decomposition

Use when analyzing scaffold diversity or grouping molecules by their core.

```python
from rdkit import Chem
from rdkit.Chem.Scaffolds import MurckoScaffold

smiles_list = [
    "c1ccc2c(c1)cc(CC(=O)O)c2",     # Indene acetic acid
    "c1ccc2[nH]ccc2c1",              # Indole
    "c1ccc2c(c1)cccc2N",             # Naphthylamine
    "c1ccc(CC(N)C(=O)O)cc1",         # Phenylalanine
    "c1ccc(NC(=O)C)cc1",             # Acetanilide
]

scaffold_map = {}  # scaffold SMILES -> list of input SMILES
for smi in smiles_list:
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        continue
    core = MurckoScaffold.GetScaffoldForMol(mol)  # Ring systems + linkers
    generic = MurckoScaffold.MakeScaffoldGeneric(core)  # All atoms -> C, bonds -> single
    scaffold_smi = Chem.MolToSmiles(core)
    scaffold_map.setdefault(scaffold_smi, []).append(smi)
    print(f"  {smi:40s} -> {scaffold_smi}")

print(f"\nTotal: {len(smiles_list)} molecules, {len(scaffold_map)} unique scaffolds")
for scaffold, members in scaffold_map.items():
    print(f"  {scaffold}: {len(members)} compound(s)")
```

---

## Recipe 8: Chemical Reaction Application via Reaction SMARTS

Use when applying a synthetic transformation to a set of starting materials.

```python
from rdkit import Chem
from rdkit.Chem import AllChem

# Amide coupling: carboxylic acid + amine -> amide
rxn_smarts = "[C:1](=[O:2])[OH].[NH2:3][C:4]>>[C:1](=[O:2])[NH:3][C:4]"
rxn = AllChem.ReactionFromSmarts(rxn_smarts)
assert rxn.GetNumReactantTemplates() == 2

acids = ["OC(=O)c1ccccc1", "OC(=O)CC"]         # Benzoic acid, propionic acid
amines = ["NCc1ccccc1", "NCC", "NC1CCCCC1"]    # Benzylamine, ethylamine, cyclohexylamine

# Enumerate all products
products_set = set()
for acid_smi in acids:
    for amine_smi in amines:
        acid = Chem.MolFromSmiles(acid_smi)
        amine = Chem.MolFromSmiles(amine_smi)
        for products in rxn.RunReactants((acid, amine)):
            for prod in products:
                Chem.SanitizeMol(prod)
                prod_smi = Chem.MolToSmiles(prod)
                products_set.add(prod_smi)
                print(f"  {acid_smi} + {amine_smi} -> {prod_smi}")
print(f"\nTotal unique products: {len(products_set)}")
```

---

## Recipe 9: Maximum Common Substructure (MCS)

Use when identifying the shared chemical core between two or more molecules.

```python
from rdkit import Chem
from rdkit.Chem import rdFMCS

smiles_list = [
    "c1ccc(NC(=O)C)cc1",        # Acetanilide
    "c1ccc(NC(=O)CC)cc1",       # Propionanilide
    "c1ccc(NC(=O)c2ccccc2)cc1", # Benzanilide
]
mols = [Chem.MolFromSmiles(s) for s in smiles_list]

mcs_result = rdFMCS.FindMCS(
    mols,
    atomCompare=rdFMCS.AtomCompare.CompareElements,
    bondCompare=rdFMCS.BondCompare.CompareOrder,
    ringMatchesRingOnly=True,
    timeout=60,
)

print(f"MCS SMARTS: {mcs_result.smartsString}")
print(f"MCS atoms: {mcs_result.numAtoms}, bonds: {mcs_result.numBonds}")

# Highlight MCS in each molecule
mcs_mol = Chem.MolFromSmarts(mcs_result.smartsString)
for smi, mol in zip(smiles_list, mols):
    match = mol.GetSubstructMatch(mcs_mol)
    print(f"  {smi:45s} -> atom indices: {match}")
```

---

## Recipe 10: Drug-Likeness Filters (Lipinski, Veber, PAINS)

Use when triaging a compound set for drug-likeness and structural alerts.

```python
from rdkit import Chem
from rdkit.Chem import Descriptors, FilterCatalog

# Initialize PAINS filter catalog
params = FilterCatalog.FilterCatalogParams()
params.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS)
pains_catalog = FilterCatalog.FilterCatalog(params)

def assess_drug_likeness(smiles: str) -> dict:
    """Evaluate Lipinski, Veber, and PAINS filters."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"valid": False}
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    hbd = Descriptors.NumHDonors(mol)
    hba = Descriptors.NumHAcceptors(mol)
    lipinski_violations = sum([mw > 500, logp > 5, hbd > 5, hba > 10])
    # Veber rules for oral bioavailability
    tpsa = Descriptors.TPSA(mol)
    rot_bonds = Descriptors.NumRotatableBonds(mol)
    veber_pass = tpsa <= 140 and rot_bonds <= 10
    # PAINS structural alerts
    pains_entry = pains_catalog.GetFirstMatch(mol)
    pains_alert = pains_entry.GetDescription() if pains_entry else None
    return {"lipinski_violations": lipinski_violations, "veber_pass": veber_pass,
            "pains_alert": pains_alert}

test_smiles = ["CC(=O)Oc1ccccc1C(=O)O", "O=C1CC(/N=N/c2ccccc2)C(=O)N1"]
for smi in test_smiles:
    r = assess_drug_likeness(smi)
    print(f"{smi}  Lipinski={r['lipinski_violations']}  Veber={r['veber_pass']}  PAINS={r['pains_alert'] or 'None'}")
```

---

## Recipe 11: Molecular Visualization with Substructure Highlighting

Use when generating 2D depictions with highlighted functional groups.

```python
from rdkit import Chem
from rdkit.Chem import Draw, AllChem
from rdkit.Chem.Draw import rdMolDraw2D

smiles = "c1ccc(NC(=O)CC2=CC(=O)C=CC2=O)cc1"
mol = Chem.MolFromSmiles(smiles)

# Find a quinone substructure to highlight
pattern = Chem.MolFromSmarts("C1=CC(=O)C=CC1=O")
match_atoms = mol.GetSubstructMatch(pattern)
match_bonds = [b.GetIdx() for b in mol.GetBonds()
               if b.GetBeginAtomIdx() in match_atoms and b.GetEndAtomIdx() in match_atoms]

AllChem.Compute2DCoords(mol)

# Draw SVG with highlighted atoms and bonds
drawer = rdMolDraw2D.MolDraw2DSVG(400, 300)
drawer.DrawMolecule(mol, highlightAtoms=list(match_atoms), highlightBonds=match_bonds)
drawer.FinishDrawing()
with open("highlighted_molecule.svg", "w") as f:
    f.write(drawer.GetDrawingText())
print(f"Saved SVG with {len(match_atoms)} highlighted atoms")

# Grid image of multiple molecules
mols = [Chem.MolFromSmiles(s) for s in ["c1ccccc1O", "c1ccccc1N", "c1ccccc1F"]]
img = Draw.MolsToGridImage(mols, molsPerRow=3, subImgSize=(300, 200))
img.save("molecule_grid.png")
```

---

## Recipe 12: Butina Clustering by Fingerprint Similarity

Use when grouping a compound set into clusters based on structural similarity.

```python
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem
from rdkit.ML.Cluster import Butina

smiles_list = [
    "c1ccccc1O", "c1ccccc1N", "c1ccccc1F",     # Phenol, aniline, fluorobenzene
    "c1ccc2ccccc2c1", "c1ccc2c(c1)cccc2O",      # Naphthalene, naphthol
    "CC(=O)O", "CCC(=O)O", "CCCC(=O)O",         # Acetic, propionic, butyric acid
]

fps = [AllChem.GetMorganFingerprintAsBitVect(Chem.MolFromSmiles(s), 2, nBits=2048)
       for s in smiles_list]

# Pairwise distance matrix (1 - Tanimoto) in condensed form
n = len(fps)
dists = []
for i in range(1, n):
    for j in range(i):
        dists.append(1.0 - DataStructs.TanimotoSimilarity(fps[i], fps[j]))

# Butina clustering: cutoff 0.4 means Tanimoto >= 0.6 within clusters
clusters = Butina.ClusterData(dists, n, 0.4, isDistData=True)
print(f"Number of clusters: {len(clusters)}")
for i, cluster in enumerate(clusters):
    members = [smiles_list[idx] for idx in cluster]
    print(f"  Cluster {i}: centroid={members[0]}, size={len(members)}")
```

---

## Recipe 13: R-Group Decomposition Around a Core Scaffold

Use when analyzing SAR by decomposing analogs around a shared core.

```python
from rdkit import Chem
from rdkit.Chem import rdRGroupDecomposition, AllChem

# Core scaffold with labeled attachment points
core = Chem.MolFromSmiles("c1ccc([*:1])c([*:2])c1")
AllChem.Compute2DCoords(core)

analog_smiles = [
    "c1ccc(O)c(N)c1",       # R1=OH, R2=NH2
    "c1ccc(F)c(Cl)c1",      # R1=F, R2=Cl
    "c1ccc(C)c(OC)c1",      # R1=CH3, R2=OCH3
    "c1ccc(NC(=O)C)c(O)c1", # R1=NHAc, R2=OH
]
mols = [Chem.MolFromSmiles(s) for s in analog_smiles]

decomp, unmatched = rdRGroupDecomposition.RGroupDecompose([core], mols, asSmiles=True)

print(f"Core: {Chem.MolToSmiles(core)}")
print(f"Matched: {len(decomp)}, Unmatched: {len(unmatched)}")
print(f"{'Input':35s} {'R1':15s} {'R2':15s}")
print("-" * 65)
for smi, row in zip(analog_smiles, decomp):
    print(f"  {smi:33s} {row.get('R1', '—'):15s} {row.get('R2', '—'):15s}")
```

---

## Recipe 14: Load Molecular Dataset with ScaffoldSplitter

Use when preparing train/validation/test splits that prevent scaffold leakage.

```python
import deepchem as dc

# CircularFingerprint converts SMILES to Morgan fingerprint vectors
featurizer = dc.feat.CircularFingerprint(size=2048, radius=2)

# MoleculeNet loader handles download, featurization, and splitting
tasks, datasets, transformers = dc.molnet.load_delaney(
    featurizer=featurizer,
    splitter="scaffold",  # ScaffoldSplitter avoids train/test scaffold overlap
)
train, valid, test = datasets

print(f"Task(s): {tasks}")
print(f"Train: {len(train)}, Valid: {len(valid)}, Test: {len(test)}")

# Inspect a few training samples
for i in range(min(3, len(train))):
    smi = train.ids[i]
    y = train.y[i]
    print(f"  {smi:40s}  y={y[0]:.2f}  fp_bits_on={train.X[i].sum():.0f}")
```

---

## Recipe 15: Train Random Forest on Morgan Fingerprints

Use when building a quick baseline property prediction model.

```python
import deepchem as dc
from sklearn.ensemble import RandomForestRegressor

featurizer = dc.feat.CircularFingerprint(size=2048, radius=2)
tasks, datasets, transformers = dc.molnet.load_delaney(
    featurizer=featurizer, splitter="scaffold",
)
train, valid, test = datasets

# Wrap scikit-learn RF in DeepChem's SklearnModel
sklearn_model = RandomForestRegressor(
    n_estimators=100, max_depth=10, random_state=42, n_jobs=-1,
)
model = dc.models.SklearnModel(sklearn_model, model_dir="rf_model")
model.fit(train)

# Evaluate with Pearson R^2
metric = dc.metrics.Metric(dc.metrics.pearson_r2_score)
for name, ds in [("Train", train), ("Valid", valid), ("Test", test)]:
    score = model.evaluate(ds, [metric], transformers)
    print(f"{name} R^2: {score['pearson_r2_score']:.3f}")

# Predict on new molecules
new_smiles = ["c1ccccc1O", "CCCCCC"]
new_feats = featurizer.featurize(new_smiles)
predictions = model.predict(dc.data.NumpyDataset(X=new_feats, ids=new_smiles))
for smi, pred in zip(new_smiles, predictions):
    print(f"  {smi:20s} -> predicted solubility: {pred[0]:.2f}")
```

---

## Recipe 16: Graph Convolutional Network for Molecular Property Prediction

Use when leveraging molecular graph structure for end-to-end learned representations.

```python
import deepchem as dc

# ConvMolFeaturizer encodes atoms and bonds as graph features
featurizer = dc.feat.ConvMolFeaturizer()
tasks, datasets, transformers = dc.molnet.load_delaney(
    featurizer=featurizer, splitter="scaffold",
)
train, valid, test = datasets

model = dc.models.GraphConvModel(
    n_tasks=len(tasks),
    mode="regression",
    graph_conv_layers=[64, 64],   # Two graph convolution layers
    dense_layer_size=128,
    dropout=0.2,
    learning_rate=0.001,
    batch_size=64,
    model_dir="gcn_model",
)

model.fit(train, nb_epoch=50)

metric = dc.metrics.Metric(dc.metrics.pearson_r2_score)
for name, ds in [("Train", train), ("Valid", valid), ("Test", test)]:
    score = model.evaluate(ds, [metric], transformers)
    print(f"GCN {name} R^2: {score['pearson_r2_score']:.3f}")
```

---

## Recipe 17: MoleculeNet Benchmark Dataset Loading and Evaluation

Use when benchmarking models across standard molecular property datasets.

```python
import deepchem as dc
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

benchmark_configs = [
    ("delaney", "regression", dc.molnet.load_delaney),
    ("sampl",   "regression", dc.molnet.load_sampl),
    ("tox21",   "classification", dc.molnet.load_tox21),
    ("bbbp",    "classification", dc.molnet.load_bbbp),
]

featurizer = dc.feat.CircularFingerprint(size=2048, radius=2)

for name, task_type, loader in benchmark_configs:
    print(f"\n{'='*50}\nDataset: {name} ({task_type})")
    try:
        tasks, datasets, transformers = loader(featurizer=featurizer, splitter="scaffold")
        train, valid, test = datasets
        print(f"  Tasks: {tasks}  Train/Valid/Test: {len(train)}/{len(valid)}/{len(test)}")
        # Pick metric and model by task type
        if task_type == "regression":
            metric = dc.metrics.Metric(dc.metrics.pearson_r2_score)
            sk_model = RandomForestRegressor(n_estimators=50, random_state=42)
        else:
            metric = dc.metrics.Metric(dc.metrics.roc_auc_score)
            sk_model = RandomForestClassifier(n_estimators=50, random_state=42)
        model = dc.models.SklearnModel(sk_model)
        model.fit(train)
        test_score = model.evaluate(test, [metric], transformers)
        metric_name = list(test_score.keys())[0]
        print(f"  RF baseline test {metric_name}: {test_score[metric_name]:.3f}")
    except Exception as e:
        print(f"  Skipped: {e}")
```
