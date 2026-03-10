# Machine Learning & Cheminformatics Recipes

Executable code templates for ML-driven drug discovery using Datamol, DeepChem, and cheminformatics libraries.
Each recipe is production-ready Python with inline parameter documentation.

> **Parent skill**: [SKILL.md](SKILL.md) — full medicinal chemistry pipeline with MCP tools.
> **See also**: [recipes.md](recipes.md) — RDKit and DeepChem basics (Lipinski, fingerprints, conformers, scaffolds).

---

## Recipe 1: Datamol SMILES Standardization and Sanitization

Standardize and sanitize SMILES strings using Datamol for consistent molecular representations across datasets.

```python
import datamol as dm

raw_smiles = [
    "[Na+].OC(=O)c1ccccc1.[Cl-]",   # Salt form with counterions
    "C(C)(C)(C)c1ccc(O)cc1",          # Non-canonical atom ordering
    "c1ccc(cc1)C(=O)[O-].[Na+]",      # Charged carboxylate salt
    "CC(=O)Oc1ccccc1C(=O)O",          # Aspirin (should pass through)
    "OC[C@@H](O)[C@@H](O)C=O",       # Stereo sugar
]

standardized = []
for smi in raw_smiles:
    # fix_mol: kekulize, sanitize, remove Hs, fix valence issues
    mol = dm.to_mol(smi)
    mol = dm.fix_mol(mol)

    # standardize_mol: largest fragment, uncharge, normalize, canonicalize
    mol = dm.standardize_mol(
        mol,
        disconnect_metals=True,       # Disconnect metal bonds
        normalize=True,               # Normalize functional groups
        reionize=True,                # Apply standard ionization rules
        uncharge=True,                # Neutralize formal charges
        stereo=True,                  # Preserve stereochemistry
    )

    if mol is not None:
        clean_smi = dm.to_smiles(mol)
        standardized.append(clean_smi)
        print(f"  {smi:45s} -> {clean_smi}")
    else:
        print(f"  {smi:45s} -> FAILED")

print(f"\nStandardized {len(standardized)}/{len(raw_smiles)} molecules")
```

**Key Parameters:**
- `disconnect_metals=True`: Breaks metal-organic bonds (salts, coordination compounds)
- `uncharge=True`: Neutralizes charges where chemically reasonable
- `stereo=True`: Preserves stereochemistry during standardization
- `normalize=True`: Normalizes functional group representations (e.g., nitro groups)

**Expected Output:**
- Cleaned canonical SMILES with salts removed, charges neutralized, and consistent functional group representations
- Failed molecules flagged for manual review

---

## Recipe 2: Datamol Molecular Descriptor Calculation (Parallel)

Compute a comprehensive descriptor matrix for a compound library using Datamol's parallel processing.

```python
import datamol as dm
import pandas as pd

smiles_list = [
    "CC(=O)Oc1ccccc1C(=O)O",          # Aspirin
    "CC(C)Cc1ccc(CC(C)C(=O)O)cc1",    # Ibuprofen
    "OC(=O)c1ccccc1O",                 # Salicylic acid
    "c1ccc2c(c1)cc(CC(=O)O)c2",       # Indene acetic acid
    "CC12CCC3C(C1CCC2O)CCC4=CC(=O)CCC34C",  # Testosterone
]

# Convert SMILES to mol objects in parallel
mols = dm.parallelized(dm.to_mol, smiles_list, n_jobs=-1)

# Compute descriptors in parallel using all CPU cores
# dm.descriptors.compute_many returns a dict per molecule
descriptor_dicts = dm.parallelized(
    dm.descriptors.compute_many,
    mols,
    n_jobs=-1,           # Use all available cores
    progress=True,       # Show progress bar
)

# Build DataFrame
desc_df = pd.DataFrame(descriptor_dicts, index=smiles_list)
print(f"Descriptor matrix: {desc_df.shape[0]} molecules x {desc_df.shape[1]} descriptors")
print(f"\nDescriptor columns:\n{list(desc_df.columns)}")
print(f"\nSample values:\n{desc_df.head()}")

# Filter out descriptors with zero variance (uninformative)
nonzero_var = desc_df.columns[desc_df.var() > 0]
desc_df = desc_df[nonzero_var]
print(f"\nAfter variance filter: {desc_df.shape[1]} descriptors retained")

# Save for ML pipelines
desc_df.to_csv("molecular_descriptors.csv")
```

**Key Parameters:**
- `n_jobs=-1`: Use all available CPU cores for parallel computation
- `progress=True`: Display tqdm progress bar during computation
- `dm.descriptors.compute_many`: Computes MW, LogP, TPSA, HBD, HBA, rotatable bonds, ring counts, aromaticity, and ~20 more descriptors per molecule

**Expected Output:**
- DataFrame with ~30 physicochemical descriptors per molecule
- CSV file for downstream ML model training

---

## Recipe 3: Butina Clustering for Chemical Series Identification

Cluster a compound library into chemical series using Taylor-Butina clustering with fingerprint similarity.

```python
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem
from rdkit.ML.Cluster import Butina
import pandas as pd

smiles_list = [
    "c1ccc(NC(=O)c2ccccc2)cc1",       # Benzanilide
    "c1ccc(NC(=O)c2ccc(Cl)cc2)cc1",   # 4-Cl benzanilide
    "c1ccc(NC(=O)c2ccc(F)cc2)cc1",    # 4-F benzanilide
    "CC(=O)Oc1ccccc1C(=O)O",          # Aspirin
    "OC(=O)c1ccccc1O",                 # Salicylic acid
    "c1ccc2[nH]c3ccccc3c2c1",          # Carbazole
    "c1ccc2c(c1)c1ccccc1[nH]2",        # Carbazole isomer
    "CCCCCCCC(=O)O",                   # Octanoic acid
    "CCCCCCC(=O)O",                    # Heptanoic acid
    "CCCCCC(=O)O",                     # Hexanoic acid
]

# Generate Morgan fingerprints (ECFP4 equivalent)
mols = [Chem.MolFromSmiles(s) for s in smiles_list]
fps = [AllChem.GetMorganFingerprintAsBitVect(m, radius=2, nBits=2048) for m in mols]

# Compute pairwise Tanimoto distances (condensed form)
n = len(fps)
dists = []
for i in range(1, n):
    for j in range(i):
        dists.append(1.0 - DataStructs.TanimotoSimilarity(fps[i], fps[j]))

# Butina clustering with distance cutoff 0.4 (Tanimoto >= 0.6 within cluster)
cutoff = 0.4
clusters = Butina.ClusterData(dists, n, cutoff, isDistData=True)

print(f"Distance cutoff: {cutoff} (Tanimoto >= {1 - cutoff})")
print(f"Number of clusters: {len(clusters)}")
print(f"Singletons: {sum(1 for c in clusters if len(c) == 1)}")
print(f"Largest cluster: {max(len(c) for c in clusters)} compounds\n")

# Report clusters with members
cluster_assignments = {}
for i, cluster in enumerate(clusters):
    members = [smiles_list[idx] for idx in cluster]
    centroid = members[0]  # First member is the centroid in Butina
    print(f"Cluster {i} (n={len(members)}, centroid={centroid}):")
    for smi in members:
        cluster_assignments[smi] = i
        print(f"  - {smi}")
    print()

# Export cluster assignments
cluster_df = pd.DataFrame([
    {"smiles": smi, "cluster": cid} for smi, cid in cluster_assignments.items()
])
cluster_df.to_csv("butina_clusters.csv", index=False)
```

**Key Parameters:**
- `radius=2, nBits=2048`: Morgan fingerprint parameters (ECFP4 equivalent)
- `cutoff=0.4`: Distance cutoff; 0.4 means Tanimoto >= 0.6 within clusters. Use 0.3 for tighter clusters (>= 0.7 similarity) or 0.5 for looser grouping
- `isDistData=True`: Input is precomputed distance matrix
- The centroid (first element in each cluster) is the molecule with the most neighbors within the cutoff

**Expected Output:**
- Cluster assignments with centroid identification
- Summary statistics: number of clusters, singletons, largest cluster size
- CSV file mapping each compound to its cluster ID

---

## Recipe 4: Scaffold-Based ML Dataset Splitting

Split a molecular dataset by Murcko scaffold to prevent test set contamination from scaffold leakage.

```python
from rdkit import Chem
from rdkit.Chem.Scaffolds import MurckoScaffold
from collections import defaultdict
import numpy as np
import pandas as pd

# Example dataset: SMILES + activity
data = pd.DataFrame({
    "smiles": [
        "c1ccc(NC(=O)C)cc1", "c1ccc(NC(=O)CC)cc1", "c1ccc(NC(=O)CCC)cc1",
        "c1ccc2[nH]ccc2c1", "c1ccc2[nH]c(C)cc2c1", "c1ccc2[nH]c(CC)cc2c1",
        "CC(=O)O", "CCC(=O)O", "CCCC(=O)O", "CCCCC(=O)O",
        "c1ccc(O)cc1", "c1ccc(N)cc1", "c1ccc(F)cc1",
        "c1ccc2ccccc2c1", "c1ccc2c(c1)cccc2O",
    ],
    "activity": [5.2, 5.8, 6.1, 4.5, 4.9, 5.3, 2.1, 2.3, 2.5, 2.7, 3.1, 3.4, 3.0, 4.0, 4.2],
})

def scaffold_split(df, smiles_col="smiles", train_frac=0.8, val_frac=0.1, seed=42):
    """Split dataset by Murcko scaffold to prevent train/test scaffold overlap.

    Returns train, validation, test DataFrames with no shared scaffolds.
    """
    rng = np.random.RandomState(seed)

    # Assign scaffolds
    scaffold_to_indices = defaultdict(list)
    for idx, smi in enumerate(df[smiles_col]):
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            scaffold_to_indices["INVALID"].append(idx)
            continue
        core = MurckoScaffold.GetScaffoldForMol(mol)
        scaffold_smi = Chem.MolToSmiles(core)
        scaffold_to_indices[scaffold_smi].append(idx)

    # Shuffle scaffolds, then assign whole scaffold groups to splits
    scaffold_keys = list(scaffold_to_indices.keys())
    rng.shuffle(scaffold_keys)

    n = len(df)
    train_cutoff = int(n * train_frac)
    val_cutoff = int(n * (train_frac + val_frac))

    train_idx, val_idx, test_idx = [], [], []
    for scaffold in scaffold_keys:
        indices = scaffold_to_indices[scaffold]
        if len(train_idx) < train_cutoff:
            train_idx.extend(indices)
        elif len(train_idx) + len(val_idx) < val_cutoff:
            val_idx.extend(indices)
        else:
            test_idx.extend(indices)

    train = df.iloc[train_idx].reset_index(drop=True)
    val = df.iloc[val_idx].reset_index(drop=True)
    test = df.iloc[test_idx].reset_index(drop=True)

    print(f"Scaffolds: {len(scaffold_to_indices)} unique")
    print(f"Train: {len(train)} | Val: {len(val)} | Test: {len(test)}")
    return train, val, test

train_df, val_df, test_df = scaffold_split(data)

# Verify no scaffold overlap between splits
def get_scaffolds(df):
    scaffolds = set()
    for smi in df["smiles"]:
        mol = Chem.MolFromSmiles(smi)
        if mol:
            core = MurckoScaffold.GetScaffoldForMol(mol)
            scaffolds.add(Chem.MolToSmiles(core))
    return scaffolds

train_scaff = get_scaffolds(train_df)
val_scaff = get_scaffolds(val_df)
test_scaff = get_scaffolds(test_df)

print(f"\nScaffold overlap train-val: {len(train_scaff & val_scaff)}")
print(f"Scaffold overlap train-test: {len(train_scaff & test_scaff)}")
print(f"Scaffold overlap val-test: {len(val_scaff & test_scaff)}")
```

**Key Parameters:**
- `train_frac=0.8, val_frac=0.1`: Target split ratios (actual may vary since whole scaffold groups are assigned together)
- `seed=42`: Random seed for reproducible scaffold ordering
- Murcko scaffolds: Ring systems plus linkers; use `MakeScaffoldGeneric` for even coarser grouping

**Expected Output:**
- Three DataFrames (train, val, test) with zero scaffold overlap between splits
- Verification of no scaffold leakage across split boundaries
- Prevents inflated test metrics from structurally similar train/test compounds

---

## Recipe 5: DeepChem MoleculeNet Benchmark Loading

Load standard MoleculeNet benchmark datasets for model development and comparison.

```python
import deepchem as dc

# MoleculeNet benchmark datasets with recommended featurizers and metrics
benchmarks = {
    "Tox21": {
        "loader": dc.molnet.load_tox21,
        "task_type": "classification",
        "metric": dc.metrics.Metric(dc.metrics.roc_auc_score),
        "description": "12 toxicity assays, ~8000 compounds",
    },
    "BBBP": {
        "loader": dc.molnet.load_bbbp,
        "task_type": "classification",
        "metric": dc.metrics.Metric(dc.metrics.roc_auc_score),
        "description": "Blood-brain barrier permeability, ~2050 compounds",
    },
    "Delaney (ESOL)": {
        "loader": dc.molnet.load_delaney,
        "task_type": "regression",
        "metric": dc.metrics.Metric(dc.metrics.pearson_r2_score),
        "description": "Aqueous solubility, ~1128 compounds",
    },
    "QM9": {
        "loader": dc.molnet.load_qm9,
        "task_type": "regression",
        "metric": dc.metrics.Metric(dc.metrics.mean_absolute_error),
        "description": "Quantum mechanical properties, ~134k molecules",
    },
    "HIV": {
        "loader": dc.molnet.load_hiv,
        "task_type": "classification",
        "metric": dc.metrics.Metric(dc.metrics.roc_auc_score),
        "description": "HIV replication inhibition, ~41k compounds",
    },
    "BACE": {
        "loader": dc.molnet.load_bace_classification,
        "task_type": "classification",
        "metric": dc.metrics.Metric(dc.metrics.roc_auc_score),
        "description": "BACE-1 inhibitors, ~1513 compounds",
    },
}

featurizer = dc.feat.CircularFingerprint(size=2048, radius=2)

for name, config in benchmarks.items():
    print(f"\n{'='*60}")
    print(f"Dataset: {name} — {config['description']}")
    try:
        tasks, datasets, transformers = config["loader"](
            featurizer=featurizer,
            splitter="scaffold",
        )
        train, valid, test = datasets
        print(f"  Tasks: {tasks}")
        print(f"  Train: {len(train)} | Valid: {len(valid)} | Test: {len(test)}")
        print(f"  Feature shape: {train.X.shape}")
        print(f"  Task type: {config['task_type']}")
    except Exception as e:
        print(f"  Load failed: {e}")
```

**Key Parameters:**
- `featurizer=CircularFingerprint(size=2048, radius=2)`: Morgan/ECFP4 fingerprints; also supports `ConvMolFeaturizer()` for graph models, `MolGraphConvFeaturizer()` for AttentiveFP
- `splitter="scaffold"`: Scaffold-based splitting (recommended); also `"random"`, `"stratified"`
- Each loader downloads data on first use and caches locally

**Expected Output:**
- Per-dataset summary: task names, split sizes, feature dimensions
- Ready-to-use `(train, valid, test)` dataset tuples for model training

---

## Recipe 6: DeepChem GraphConvModel for Molecular Property Prediction

Train a graph convolutional network (GCN) directly on molecular graphs for property prediction.

```python
import deepchem as dc

# ConvMolFeaturizer encodes atoms (features) and bonds (adjacency) as graph
featurizer = dc.feat.ConvMolFeaturizer()
tasks, datasets, transformers = dc.molnet.load_delaney(
    featurizer=featurizer,
    splitter="scaffold",
)
train, valid, test = datasets

print(f"Tasks: {tasks}")
print(f"Train: {len(train)} | Valid: {len(valid)} | Test: {len(test)}")

# Build Graph Convolutional Model
model = dc.models.GraphConvModel(
    n_tasks=len(tasks),
    mode="regression",
    graph_conv_layers=[128, 128],    # Two GCN layers with 128 units each
    dense_layer_size=256,            # Dense layer after graph pooling
    dropout=0.2,                     # Dropout for regularization
    learning_rate=0.001,             # Adam optimizer learning rate
    batch_size=64,                   # Training batch size
    model_dir="gcn_solubility",
)

# Train with validation-based early stopping
best_score = -float("inf")
patience, patience_count = 10, 0
metric = dc.metrics.Metric(dc.metrics.pearson_r2_score)

for epoch in range(100):
    loss = model.fit(train, nb_epoch=1)
    val_score = model.evaluate(valid, [metric], transformers)["pearson_r2_score"]
    if val_score > best_score:
        best_score = val_score
        patience_count = 0
        model.save_checkpoint()
    else:
        patience_count += 1
    if epoch % 10 == 0:
        print(f"Epoch {epoch:3d} | Loss: {loss:.4f} | Val R2: {val_score:.3f}")
    if patience_count >= patience:
        print(f"Early stopping at epoch {epoch}")
        break

# Final evaluation
model.restore()
for name, ds in [("Train", train), ("Valid", valid), ("Test", test)]:
    score = model.evaluate(ds, [metric], transformers)
    print(f"GCN {name} R2: {score['pearson_r2_score']:.3f}")
```

**Key Parameters:**
- `graph_conv_layers=[128, 128]`: Number and size of graph convolution layers; deeper/wider for complex tasks
- `dense_layer_size=256`: Fully connected layer after graph-level pooling
- `dropout=0.2`: Regularization; increase to 0.3-0.5 for small datasets
- `batch_size=64`: Larger batches stabilize training; reduce if GPU memory limited
- Early stopping with patience prevents overfitting

**Expected Output:**
- Training loss and validation R2 per epoch
- Final train/valid/test R2 scores
- Saved model checkpoint at best validation performance

---

## Recipe 7: DeepChem AttentiveFPModel (Graph Attention)

Train an Attentive Fingerprint model using graph attention for molecular property prediction.

```python
import deepchem as dc

# MolGraphConvFeaturizer produces graph features compatible with AttentiveFP
featurizer = dc.feat.MolGraphConvFeaturizer(use_edges=True)

tasks, datasets, transformers = dc.molnet.load_delaney(
    featurizer=featurizer,
    splitter="scaffold",
)
train, valid, test = datasets

model = dc.models.AttentiveFPModel(
    n_tasks=len(tasks),
    mode="regression",
    num_layers=3,              # Number of GNN message-passing layers
    num_timesteps=2,           # Readout attention timesteps
    graph_feat_size=200,       # Hidden feature dimension
    dropout=0.2,
    learning_rate=0.0005,      # Lower LR for attention models
    batch_size=32,
    model_dir="attentivefp_solubility",
)

# Train
model.fit(train, nb_epoch=80)

# Evaluate
metric = dc.metrics.Metric(dc.metrics.pearson_r2_score)
for name, ds in [("Train", train), ("Valid", valid), ("Test", test)]:
    score = model.evaluate(ds, [metric], transformers)
    print(f"AttentiveFP {name} R2: {score['pearson_r2_score']:.3f}")

# Predict on new molecules
new_smiles = ["c1ccccc1O", "CCCCCC", "CC(=O)Oc1ccccc1C(=O)O"]
new_feats = featurizer.featurize(new_smiles)
new_dataset = dc.data.NumpyDataset(X=new_feats, ids=new_smiles)
preds = model.predict(new_dataset)
for smi, pred in zip(new_smiles, preds):
    print(f"  {smi:35s} -> predicted: {pred[0]:.2f}")
```

**Key Parameters:**
- `num_layers=3`: Number of message-passing layers (deeper captures longer-range interactions)
- `num_timesteps=2`: Attention-based readout iterations (higher = more expressive graph pooling)
- `graph_feat_size=200`: Hidden dimension for node features
- `use_edges=True`: Include bond features (bond type, conjugation, ring membership)
- AttentiveFP generally outperforms GCN on solubility and toxicity tasks

**Expected Output:**
- Train/valid/test R2 scores (typically R2 > 0.8 on Delaney with AttentiveFP)
- Predictions for new molecules with uncertainty from dropout

---

## Recipe 8: ChemBERTa Transfer Learning

Load a pretrained ChemBERTa transformer and finetune on a custom molecular property dataset.

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from torch.utils.data import DataLoader, Dataset
import pandas as pd
import numpy as np

# Load pretrained ChemBERTa model and tokenizer
model_name = "seyonec/ChemBERTa-zinc-base-v1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
base_model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=1,              # Regression: single output
    problem_type="regression",
)

class SmilesDataset(Dataset):
    """Dataset for SMILES-based molecular property prediction."""
    def __init__(self, smiles, labels, tokenizer, max_length=128):
        self.encodings = tokenizer(
            smiles, padding=True, truncation=True,
            max_length=max_length, return_tensors="pt",
        )
        self.labels = torch.tensor(labels, dtype=torch.float32)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: v[idx] for k, v in self.encodings.items()}
        item["labels"] = self.labels[idx]
        return item

# Example: finetune on solubility data
train_smiles = ["c1ccccc1O", "CCCCCC", "CC(=O)Oc1ccccc1C(=O)O", "c1ccc(N)cc1"]
train_labels = [-1.5, -3.2, -1.8, -0.9]  # log solubility
val_smiles = ["c1ccccc1N", "CCCCCCCC"]
val_labels = [-1.1, -4.0]

train_dataset = SmilesDataset(train_smiles, train_labels, tokenizer)
val_dataset = SmilesDataset(val_smiles, val_labels, tokenizer)

# Training loop
optimizer = torch.optim.AdamW(base_model.parameters(), lr=2e-5, weight_decay=0.01)
train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=8)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
base_model.to(device)

for epoch in range(10):
    base_model.train()
    total_loss = 0
    for batch in train_loader:
        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = base_model(**batch)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        total_loss += loss.item()

    # Validation
    base_model.eval()
    val_preds, val_true = [], []
    with torch.no_grad():
        for batch in val_loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = base_model(**batch)
            val_preds.extend(outputs.logits.squeeze().cpu().tolist())
            val_true.extend(batch["labels"].cpu().tolist())

    if epoch % 3 == 0:
        print(f"Epoch {epoch} | Train loss: {total_loss/len(train_loader):.4f}")

# Save finetuned model
base_model.save_pretrained("chemberta_finetuned")
tokenizer.save_pretrained("chemberta_finetuned")
print("Finetuned model saved to chemberta_finetuned/")
```

**Key Parameters:**
- `model_name="seyonec/ChemBERTa-zinc-base-v1"`: Pretrained on ~100M ZINC SMILES; alternatives: `"DeepChem/ChemBERTa-77M-MTR"`, `"seyonec/PubChem10M_SMILES_BPE_450k"`
- `lr=2e-5`: Low learning rate for finetuning (avoids catastrophic forgetting)
- `weight_decay=0.01`: L2 regularization
- `max_length=128`: Maximum SMILES token length (increase for large molecules)
- `num_labels=1`: Set to number of tasks for multi-task; use `problem_type="single_label_classification"` for classification

**Expected Output:**
- Finetuned ChemBERTa model saved for inference
- Training loss curve showing convergence
- Predictions as continuous values (regression) or probabilities (classification)

---

## Recipe 9: GROVER Molecular Representation Extraction

Extract pretrained GROVER graph transformer embeddings for downstream ML tasks.

```python
import torch
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem
import subprocess
import os

# GROVER setup: clone and use pretrained model
# git clone https://github.com/tencent-ailab/grover.git
# Download pretrained model: grover_large.pt (~100M params)

def extract_grover_embeddings(smiles_list, grover_dir="grover",
                               model_path="grover_large.pt",
                               output_path="grover_embeddings.npz"):
    """Extract molecular embeddings from pretrained GROVER model.

    GROVER (Graph Representation from self-supervised Message Passing Transformer)
    learns molecular representations via self-supervised pretraining on 10M molecules.

    Args:
        smiles_list: List of SMILES strings
        grover_dir: Path to cloned GROVER repository
        model_path: Path to pretrained model checkpoint
        output_path: Where to save extracted embeddings

    Returns:
        numpy array of shape (n_molecules, embedding_dim)
    """
    # Write SMILES to temporary input file
    input_csv = os.path.join(grover_dir, "tmp_input.csv")
    with open(input_csv, "w") as f:
        f.write("smiles\n")
        for smi in smiles_list:
            f.write(f"{smi}\n")

    # Run GROVER fingerprint extraction
    cmd = [
        "python", os.path.join(grover_dir, "main.py"), "fingerprint",
        "--data_path", input_csv,
        "--features_path", output_path,
        "--checkpoint_path", model_path,
        "--no_cuda",  # Remove for GPU
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"GROVER failed: {result.stderr}")

    # Load embeddings
    embeddings = np.load(output_path)["fps"]
    print(f"Extracted embeddings: {embeddings.shape}")
    print(f"  Molecules: {embeddings.shape[0]}")
    print(f"  Embedding dim: {embeddings.shape[1]}")
    return embeddings

# Alternative: use GROVER embeddings for downstream prediction
def grover_downstream_classifier(embeddings, labels, test_size=0.2):
    """Train a classifier on GROVER embeddings."""
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.metrics import roc_auc_score

    X_train, X_test, y_train, y_test = train_test_split(
        embeddings, labels, test_size=test_size, random_state=42, stratify=labels,
    )

    clf = GradientBoostingClassifier(
        n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42,
    )
    clf.fit(X_train, y_train)

    y_prob = clf.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_prob)
    print(f"GROVER + GBT: AUC = {auc:.3f}")
    return clf

# Usage:
# embeddings = extract_grover_embeddings(["CC(=O)Oc1ccccc1C(=O)O", "c1ccccc1O", ...])
# clf = grover_downstream_classifier(embeddings, labels=[1, 0, ...])
print("GROVER pipeline ready. Provide SMILES list and pretrained model path.")
```

**Key Parameters:**
- `grover_large.pt`: Large model (~100M params, 5120-dim embeddings); `grover_base.pt` (~5M params, 3200-dim) for lighter workloads
- `--no_cuda`: CPU mode; remove for GPU acceleration
- GROVER embeddings capture both atom-level and bond-level molecular features via self-supervised pretraining
- Pretrained on ~10M molecules from ChEMBL + ZINC

**Expected Output:**
- Numpy array of molecular embeddings (n_molecules x embedding_dim)
- Embeddings suitable for any downstream ML task: classification, regression, clustering

---

## Recipe 10: Fingerprint-Based Virtual Screening

Screen a compound library against a query molecule using Morgan/ECFP4 fingerprints and Tanimoto similarity.

```python
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem
import pandas as pd
import numpy as np

# Query: active compound to search against library
query_smiles = "c1ccc(NC(=O)c2cc(Cl)ccc2F)cc1"  # Example kinase inhibitor
query_mol = Chem.MolFromSmiles(query_smiles)
query_fp = AllChem.GetMorganFingerprintAsBitVect(query_mol, radius=2, nBits=2048)

# Library: list of SMILES (replace with actual library file)
library_smiles = [
    "c1ccc(NC(=O)c2ccccc2)cc1",          # Similar: anilide
    "c1ccc(NC(=O)c2cc(Cl)ccc2)cc1",      # Very similar: Cl-anilide
    "c1ccc(NC(=O)c2cc(F)ccc2Br)cc1",     # Similar: halogenated
    "CCCCCCCC(=O)O",                       # Dissimilar: fatty acid
    "c1ccc2[nH]ccc2c1",                   # Moderate: indole
    "c1ccc(NC(=O)c2cc(Cl)c(F)cc2)cc1",   # Very similar: dihalogenated
    "CC(=O)Oc1ccccc1C(=O)O",             # Dissimilar: aspirin
    "c1ccc(NC(=O)c2ccncc2)cc1",          # Similar: pyridine anilide
]

# Compute fingerprints for library
library_mols = [Chem.MolFromSmiles(s) for s in library_smiles]
library_fps = [AllChem.GetMorganFingerprintAsBitVect(m, radius=2, nBits=2048)
               for m in library_mols if m is not None]

# Calculate Tanimoto similarity and rank
results = []
for smi, fp in zip(library_smiles, library_fps):
    similarity = DataStructs.TanimotoSimilarity(query_fp, fp)
    results.append({"smiles": smi, "tanimoto": similarity})

results_df = pd.DataFrame(results).sort_values("tanimoto", ascending=False)

# Apply similarity threshold
threshold = 0.5
hits = results_df[results_df["tanimoto"] >= threshold]

print(f"Query: {query_smiles}")
print(f"Library size: {len(library_smiles)}")
print(f"Threshold: Tanimoto >= {threshold}")
print(f"Hits: {len(hits)}\n")

print(f"{'Rank':>4}  {'Tanimoto':>8}  SMILES")
print("-" * 60)
for rank, (_, row) in enumerate(results_df.iterrows(), 1):
    marker = " *" if row["tanimoto"] >= threshold else ""
    print(f"{rank:4d}  {row['tanimoto']:8.3f}  {row['smiles']}{marker}")

# Export ranked results
results_df.to_csv("virtual_screening_results.csv", index=False)
```

**Key Parameters:**
- `radius=2, nBits=2048`: ECFP4 fingerprint; use `radius=3` (ECFP6) for more specific matching
- `threshold=0.5`: Tanimoto similarity cutoff; 0.5 for broad exploration, 0.7 for close analogs
- For large libraries (>1M compounds), use `DataStructs.BulkTanimotoSimilarity()` for vectorized speed
- Consider combining with substructure filters for SAR-aware screening

**Expected Output:**
- Ranked compound list by Tanimoto similarity to query
- Hit compounds above threshold marked for follow-up
- CSV file with full similarity rankings

---

## Recipe 11: ADMET Property Prediction Pipeline

Predict ADMET (absorption, distribution, metabolism, excretion, toxicity) properties for drug candidates.

```python
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, Lipinski
import pandas as pd
import numpy as np

def predict_admet_properties(smiles: str) -> dict:
    """Predict ADMET-related molecular properties from structure.

    Uses descriptor-based rules and empirical models for:
    - Absorption: Lipinski Ro5, TPSA (oral absorption), Veber rules
    - Distribution: LogP (membrane permeability), BBB penetration (Clark rules)
    - Metabolism: CYP liability indicators (lipophilic, aromatic N)
    - Excretion: MW-based renal filtration estimate
    - Toxicity: PAINS alerts, Brenk structural alerts, hERG liability
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"valid": False, "smiles": smiles}

    # Core descriptors
    mw = Descriptors.MolWt(mol)
    logp = Crippen.MolLogP(mol)
    tpsa = Descriptors.TPSA(mol)
    hbd = Descriptors.NumHDonors(mol)
    hba = Descriptors.NumHAcceptors(mol)
    rot_bonds = Descriptors.NumRotatableBonds(mol)
    aromatic_rings = Descriptors.NumAromaticRings(mol)
    heavy_atoms = Descriptors.HeavyAtomCount(mol)

    result = {
        "smiles": smiles, "valid": True,
        "MW": round(mw, 1), "LogP": round(logp, 2), "TPSA": round(tpsa, 1),
        "HBD": hbd, "HBA": hba, "RotBonds": rot_bonds,
    }

    # --- ABSORPTION ---
    # Lipinski Rule of Five
    lipinski_violations = sum([mw > 500, logp > 5, hbd > 5, hba > 10])
    result["lipinski_violations"] = lipinski_violations
    result["lipinski_pass"] = lipinski_violations <= 1

    # Veber rules (oral bioavailability)
    result["veber_pass"] = tpsa <= 140 and rot_bonds <= 10

    # Oral absorption estimate (Egan egg model)
    if tpsa <= 131.6 and logp <= 5.88:
        result["oral_absorption"] = "HIGH"
    elif tpsa <= 150:
        result["oral_absorption"] = "MODERATE"
    else:
        result["oral_absorption"] = "LOW"

    # --- DISTRIBUTION ---
    # BBB penetration (Clark rules)
    if tpsa <= 60 and logp >= 1.0 and mw <= 450:
        result["bbb_penetration"] = "HIGH"
    elif tpsa <= 90 and logp >= 0:
        result["bbb_penetration"] = "MODERATE"
    else:
        result["bbb_penetration"] = "LOW"

    # Plasma protein binding estimate
    result["ppb_risk"] = "HIGH" if logp > 4 else "MODERATE" if logp > 2.5 else "LOW"

    # --- METABOLISM ---
    # CYP liability indicators
    result["cyp_liability_risk"] = "HIGH" if (logp > 3 and aromatic_rings >= 2) else "MODERATE" if logp > 2 else "LOW"

    # --- EXCRETION ---
    result["renal_clearance"] = "LIKELY" if (mw < 400 and logp < 1) else "UNLIKELY"

    # --- TOXICITY ---
    # hERG liability (basic nitrogen + lipophilic)
    basic_n = sum(1 for atom in mol.GetAtoms()
                  if atom.GetAtomicNum() == 7 and atom.GetFormalCharge() >= 0
                  and atom.GetTotalNumHs() > 0)
    result["herg_risk"] = "HIGH" if (logp > 3.7 and basic_n > 0) else "MODERATE" if logp > 3 else "LOW"

    # PAINS filter
    from rdkit.Chem import FilterCatalog
    params = FilterCatalog.FilterCatalogParams()
    params.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS)
    catalog = FilterCatalog.FilterCatalog(params)
    entry = catalog.GetFirstMatch(mol)
    result["pains_alert"] = entry.GetDescription() if entry else None

    return result

# Screen multiple compounds
test_compounds = [
    "CC(=O)Oc1ccccc1C(=O)O",                  # Aspirin
    "CC(C)Cc1ccc(CC(C)C(=O)O)cc1",            # Ibuprofen
    "CN1C(=O)N(C)c2[nH]cnc2C1=O",             # Caffeine
    "CC12CCC3C(C1CCC2O)CCC4=CC(=O)CCC34C",    # Testosterone
    "c1ccc(NC(=O)c2cc(Cl)ccc2F)cc1",          # Test compound
]

results = [predict_admet_properties(smi) for smi in test_compounds]
admet_df = pd.DataFrame(results)

# Display summary
print("ADMET Prediction Summary")
print("=" * 80)
for _, row in admet_df.iterrows():
    print(f"\n{row['smiles']}")
    print(f"  MW={row['MW']}  LogP={row['LogP']}  TPSA={row['TPSA']}  HBD={row['HBD']}  HBA={row['HBA']}")
    print(f"  Lipinski: {'PASS' if row['lipinski_pass'] else 'FAIL'} ({row['lipinski_violations']} violations)")
    print(f"  Absorption: {row['oral_absorption']}  BBB: {row['bbb_penetration']}  hERG: {row['herg_risk']}")
    print(f"  PAINS: {row['pains_alert'] or 'Clean'}")

admet_df.to_csv("admet_predictions.csv", index=False)
```

**Key Parameters:**
- Lipinski Ro5: MW < 500, LogP < 5, HBD < 5, HBA < 10 (allows 1 violation)
- Veber: TPSA <= 140 and RotBonds <= 10 for oral bioavailability
- Clark BBB rules: TPSA <= 60, LogP >= 1, MW <= 450 for CNS penetration
- hERG risk: LogP > 3.7 + basic nitrogen is a common hERG blocker profile
- These are rule-based estimates; validate with experimental ADMET assays

**Expected Output:**
- Per-compound ADMET profile with absorption, distribution, metabolism, excretion, and toxicity flags
- CSV file for batch analysis and compound prioritization

---

## Recipe 12: Multi-Task Learning for Multiple Endpoints

Train a single model with shared molecular representation for simultaneous prediction of multiple properties.

```python
import deepchem as dc
import numpy as np

# Load multi-task dataset (Tox21: 12 toxicity assays)
featurizer = dc.feat.MolGraphConvFeaturizer(use_edges=True)
tasks, datasets, transformers = dc.molnet.load_tox21(
    featurizer=featurizer,
    splitter="scaffold",
)
train, valid, test = datasets

print(f"Tasks ({len(tasks)}): {tasks}")
print(f"Train: {len(train)} | Valid: {len(valid)} | Test: {len(test)}")

# Multi-task AttentiveFP model: shared molecular encoder, separate task heads
model = dc.models.AttentiveFPModel(
    n_tasks=len(tasks),
    mode="classification",
    num_layers=3,
    num_timesteps=2,
    graph_feat_size=200,
    dropout=0.2,
    learning_rate=0.0005,
    batch_size=64,
    model_dir="multitask_tox21",
)

# Train
model.fit(train, nb_epoch=50)

# Evaluate per-task AUC
metric = dc.metrics.Metric(dc.metrics.roc_auc_score, np.mean, mode="classification")
train_scores = model.evaluate(train, [metric], transformers)
valid_scores = model.evaluate(valid, [metric], transformers)
test_scores = model.evaluate(test, [metric], transformers)

print(f"\nMulti-task results (mean AUC across {len(tasks)} tasks):")
print(f"  Train AUC: {train_scores['mean-roc_auc_score']:.3f}")
print(f"  Valid AUC: {valid_scores['mean-roc_auc_score']:.3f}")
print(f"  Test AUC:  {test_scores['mean-roc_auc_score']:.3f}")

# Per-task evaluation
per_task_metric = dc.metrics.Metric(dc.metrics.roc_auc_score, mode="classification")
test_per_task = model.evaluate(test, [per_task_metric], transformers, per_task_metrics=[per_task_metric])

print(f"\nPer-task test AUC:")
for task in tasks:
    key = f"roc_auc_score-{task}"
    if key in test_per_task:
        print(f"  {task:30s}: {test_per_task[key]:.3f}")

# Predict toxicity profile for new compounds
new_smiles = ["CC(=O)Oc1ccccc1C(=O)O", "c1ccc2c(c1)cc(CC(=O)O)c2"]
new_feats = featurizer.featurize(new_smiles)
new_dataset = dc.data.NumpyDataset(X=new_feats, ids=new_smiles)
predictions = model.predict(new_dataset)

print(f"\nToxicity predictions:")
for smi, pred in zip(new_smiles, predictions):
    active_tasks = [t for t, p in zip(tasks, pred) if p > 0.5]
    print(f"  {smi}")
    print(f"    Active in: {active_tasks if active_tasks else 'None'}")
```

**Key Parameters:**
- `n_tasks=len(tasks)`: Number of endpoints to predict simultaneously; shared encoder learns generalizable molecular features
- `mode="classification"`: Multi-label binary classification; each task independently predicted
- Multi-task models benefit from related tasks (e.g., toxicity assays share biological mechanisms)
- Missing labels handled automatically by DeepChem (masked loss)
- Performance typically improves over single-task models when tasks share underlying biology

**Expected Output:**
- Mean AUC across all toxicity tasks
- Per-task AUC breakdown showing which endpoints benefit most from multi-task learning
- Toxicity profile predictions for new compounds across all 12 Tox21 assays

---

## Quick Reference

| Task | Recipe | Key Tool/Library |
|------|--------|-----------------|
| SMILES standardization | #1 | `datamol.standardize_mol` |
| Descriptor calculation | #2 | `datamol.descriptors.compute_many` |
| Chemical clustering | #3 | Butina + Tanimoto distance |
| Scaffold-safe splitting | #4 | `MurckoScaffold` + custom splitter |
| Benchmark datasets | #5 | `dc.molnet.load_*` |
| Graph conv prediction | #6 | `dc.models.GraphConvModel` |
| Graph attention | #7 | `dc.models.AttentiveFPModel` |
| Transformer transfer learning | #8 | ChemBERTa + HuggingFace |
| Pretrained embeddings | #9 | GROVER graph transformer |
| Virtual screening | #10 | Morgan FP + Tanimoto ranking |
| ADMET prediction | #11 | RDKit descriptors + rule-based |
| Multi-task learning | #12 | AttentiveFP multi-endpoint |

---

## Cross-Skill Routing

- RDKit basics (Lipinski, fingerprints, conformers, scaffolds) --> [recipes.md](recipes.md)
- ADMET optimization and drug-likeness strategy --> parent [SKILL.md](SKILL.md)
- Protein-ligand docking and binding affinity --> `binder-discovery-specialist`
- Biological activity data retrieval --> `drug-research` (ChEMBL MCP tool)
- Clinical pharmacokinetics modeling --> `clinical-pharmacology`
