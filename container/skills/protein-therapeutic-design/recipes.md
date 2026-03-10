# ESM Protein Language Model Recipes

> Copy-paste executable code templates for ESM3 and ESM C protein language models.
> Parent skill: [SKILL.md](SKILL.md) — full design pipeline with MCP tools.

---

## Recipe 1: Generate Protein Sequence with ESM3

Generate a novel protein sequence using ESM3 generative model with basic settings.

```python
# pip install esm
from esm.models.esm3 import ESM3
from esm.sdk.api import ESMProtein, GenerationConfig

# Load ESM3 open model (requires GPU with ~16 GB VRAM)
model = ESM3.from_pretrained("esm3_sm_open_v1")

# Create a prompt: specify desired length via sequence track
prompt = ESMProtein(sequence="_" * 100)  # 100-residue protein

# Generate with default sampling
config = GenerationConfig(
    track="sequence",
    num_steps=100,        # number of iterative refinement steps
    temperature=0.7,      # controls diversity (0.1=conservative, 1.0=diverse)
)

generated = model.generate(prompt, config)
print(f"Generated sequence ({len(generated.sequence)} aa):")
print(generated.sequence)
```

---

## Recipe 2: Structure Prediction from Sequence

Predict 3D structure from an amino acid sequence using ESM3.

```python
from esm.models.esm3 import ESM3
from esm.sdk.api import ESMProtein, GenerationConfig

model = ESM3.from_pretrained("esm3_sm_open_v1")

# Input: amino acid sequence
protein = ESMProtein(sequence="MKTLLILAVFCLAQGGSEAEAPTGTDEKALESNG")

# Generate structure coordinates from sequence
config = GenerationConfig(
    track="structure",
    num_steps=50,
    temperature=0.5,
)

result = model.generate(protein, config)

# Save predicted structure as PDB
result.to_pdb("predicted_structure.pdb")
print(f"Structure saved. Residues: {len(result.sequence)}")
print(f"Coordinates shape: {result.coordinates.shape}")
```

---

## Recipe 3: Inverse Folding (Design Sequence from Structure)

Given a backbone structure, design a new amino acid sequence that folds into it.

```python
from esm.models.esm3 import ESM3
from esm.sdk.api import ESMProtein, GenerationConfig

model = ESM3.from_pretrained("esm3_sm_open_v1")

# Load target backbone structure from PDB file
protein = ESMProtein.from_pdb("target_backbone.pdb")

# Clear existing sequence — keep only structure
protein.sequence = "_" * len(protein.sequence)

# Design new sequence conditioned on structure
config = GenerationConfig(
    track="sequence",
    num_steps=100,
    temperature=0.2,  # low temp for high-confidence designs
)

designed = model.generate(protein, config)
print(f"Designed sequence: {designed.sequence}")

# Validate: predict structure from designed sequence and compare
protein_check = ESMProtein(sequence=designed.sequence)
check_config = GenerationConfig(track="structure", num_steps=50)
folded = model.generate(protein_check, check_config)
folded.to_pdb("designed_refolded.pdb")
print("Refolded structure saved — compare RMSD to target backbone.")
```

---

## Recipe 4: Protein Embeddings with ESM C for Downstream ML

Extract per-residue and per-protein embeddings using ESM Cambrian for classification, clustering, or regression tasks.

```python
import torch
from esm.models.esmc import ESMC

# Load ESM Cambrian model
model = ESMC.from_pretrained("esmc_300m")
model.eval()

# Tokenize sequence
sequence = "MKTLLILAVFCLAQGGSEAEAPTGTDEKALESNG"
tokens = model.tokenizer.encode(sequence)
tokens = torch.tensor([tokens], dtype=torch.long)

# Extract embeddings from last hidden layer
with torch.no_grad():
    output = model(tokens)
    embeddings = output.embeddings          # (1, seq_len, hidden_dim)

# Per-residue embeddings for site-level predictions
per_residue = embeddings[0, 1:-1, :]        # strip BOS/EOS tokens
print(f"Per-residue shape: {per_residue.shape}")

# Mean-pool for a single protein-level embedding vector
protein_embedding = per_residue.mean(dim=0)
print(f"Protein embedding shape: {protein_embedding.shape}")

# Save for downstream ML (e.g., fitness prediction, localization)
torch.save(protein_embedding, "protein_embedding.pt")
```

---

## Recipe 5: Function-Conditioned Protein Generation

Generate a protein sequence conditioned on desired functional annotations.

```python
from esm.models.esm3 import ESM3
from esm.sdk.api import ESMProtein, GenerationConfig

model = ESM3.from_pretrained("esm3_sm_open_v1")

# Define function keywords via the function track
# InterPro annotations describe desired protein function
protein = ESMProtein(
    sequence="_" * 120,
    function_annotations=[
        # Specify desired InterPro family/domain annotations
        # These guide ESM3 toward generating proteins with matching function
        {"label": "IPR036388", "start": 1, "end": 120},   # immunoglobulin-like fold
    ],
)

config = GenerationConfig(
    track="sequence",
    num_steps=100,
    temperature=0.7,
)

result = model.generate(protein, config)
print(f"Function-conditioned sequence ({len(result.sequence)} aa):")
print(result.sequence)

# Verify: predict structure to confirm fold matches annotation
struct_config = GenerationConfig(track="structure", num_steps=50)
structure = model.generate(ESMProtein(sequence=result.sequence), struct_config)
structure.to_pdb("function_conditioned.pdb")
print("Structure saved — inspect for immunoglobulin-like fold.")
```

---

## Recipe 6: Chain-of-Thought Iterative Protein Design

Multi-step design: generate structure, design sequence, predict function, then refine.

```python
from esm.models.esm3 import ESM3
from esm.sdk.api import ESMProtein, GenerationConfig

model = ESM3.from_pretrained("esm3_sm_open_v1")

# Step 1: Generate a backbone structure (unconditional)
backbone_prompt = ESMProtein(sequence="_" * 80)
struct_config = GenerationConfig(track="structure", num_steps=80, temperature=0.7)
backbone = model.generate(backbone_prompt, struct_config)
print("Step 1: Backbone generated")

# Step 2: Design sequence for the generated backbone (inverse folding)
backbone.sequence = "_" * len(backbone.sequence)
seq_config = GenerationConfig(track="sequence", num_steps=100, temperature=0.2)
designed = model.generate(backbone, seq_config)
print(f"Step 2: Sequence designed: {designed.sequence[:40]}...")

# Step 3: Predict function annotations for designed protein
func_config = GenerationConfig(track="function", num_steps=10)
annotated = model.generate(designed, func_config)
print(f"Step 3: Function annotations: {annotated.function_annotations}")

# Step 4: Validate by re-predicting structure from sequence
check = ESMProtein(sequence=designed.sequence)
refold_config = GenerationConfig(track="structure", num_steps=50)
refolded = model.generate(check, refold_config)

# Step 5: Save all intermediates for comparison
backbone.to_pdb("cot_step1_backbone.pdb")
refolded.to_pdb("cot_step4_refolded.pdb")
print("Step 5: Intermediates saved — compare backbone vs refolded RMSD")
print("Self-consistency check: low RMSD = high-confidence design")
```

---

## Recipe 7: Batch Protein Embedding Extraction

Extract embeddings for a list of protein sequences from a FASTA file.

```python
import torch
from esm.models.esmc import ESMC

model = ESMC.from_pretrained("esmc_300m")
model.eval()

def read_fasta(filepath):
    """Parse FASTA file into list of (header, sequence) tuples."""
    sequences = []
    header, seq = None, []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if header:
                    sequences.append((header, "".join(seq)))
                header, seq = line[1:], []
            else:
                seq.append(line)
    if header:
        sequences.append((header, "".join(seq)))
    return sequences

# Load sequences from FASTA
sequences = read_fasta("proteins.fasta")
print(f"Loaded {len(sequences)} sequences")

# Extract embeddings in batches
embeddings_dict = {}
for header, seq in sequences:
    tokens = model.tokenizer.encode(seq)
    tokens = torch.tensor([tokens], dtype=torch.long)
    with torch.no_grad():
        output = model(tokens)
        emb = output.embeddings[0, 1:-1, :].mean(dim=0)  # mean-pool
    embeddings_dict[header] = emb
    print(f"  {header[:30]}... -> {emb.shape}")

# Save all embeddings as a single file
torch.save(embeddings_dict, "batch_embeddings.pt")
print(f"Saved {len(embeddings_dict)} embeddings to batch_embeddings.pt")
```

---

## Recipe 8: Protein Sequence Similarity via Embedding Cosine Distance

Compare proteins by cosine similarity of their ESM C embeddings.

```python
import torch
import torch.nn.functional as F
from esm.models.esmc import ESMC

model = ESMC.from_pretrained("esmc_300m")
model.eval()

def get_embedding(sequence):
    """Get mean-pooled protein embedding."""
    tokens = model.tokenizer.encode(sequence)
    tokens = torch.tensor([tokens], dtype=torch.long)
    with torch.no_grad():
        output = model(tokens)
        emb = output.embeddings[0, 1:-1, :].mean(dim=0)
    return emb

# Define sequences to compare
sequences = {
    "human_insulin":  "MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKT",
    "mouse_insulin":  "MALWMRFLPLLALLVLWEPKPAQAFVKQHLCGPHLVEALYLVCGERGFFYTPKS",
    "human_glucagon": "MKSIYFVAGLFVMLVQGSWQRSLQDTEEKSRSFSASQADPLSDPDQMNEDKRHSQ",
}

# Compute pairwise cosine similarity
names = list(sequences.keys())
embeddings = {name: get_embedding(seq) for name, seq in sequences.items()}

print("Pairwise cosine similarity:")
print(f"{'':>20}", end="")
for name in names:
    print(f"{name:>20}", end="")
print()

for name_a in names:
    print(f"{name_a:>20}", end="")
    for name_b in names:
        sim = F.cosine_similarity(
            embeddings[name_a].unsqueeze(0),
            embeddings[name_b].unsqueeze(0),
        ).item()
        print(f"{sim:>20.4f}", end="")
    print()

# Interpretation: >0.9 = very similar, 0.7-0.9 = related, <0.7 = distinct
```

---

## Recipe 9: Masked Position Prediction (Fill in Missing Residues)

Predict the most likely amino acids at masked (unknown) positions in a sequence.

```python
from esm.models.esm3 import ESM3
from esm.sdk.api import ESMProtein, GenerationConfig

model = ESM3.from_pretrained("esm3_sm_open_v1")

# Original sequence with unknown residues marked as underscores
# Example: residues 15-20 are missing or unknown
sequence = "MKTLLILAVFCLAQ_____EAPTGTDEKALESNGKVLDV"
#                     ^^^^^^ positions 15-20 masked

print(f"Input sequence:  {sequence}")
print(f"Masked positions: {[i+1 for i,c in enumerate(sequence) if c == '_']}")

# Use ESM3 to fill in the masked positions
protein = ESMProtein(sequence=sequence)

config = GenerationConfig(
    track="sequence",
    num_steps=50,
    temperature=0.1,  # low temperature for most-likely prediction
)

filled = model.generate(protein, config)
print(f"Filled sequence: {filled.sequence}")

# Highlight what changed
diffs = []
for i, (orig, new) in enumerate(zip(sequence, filled.sequence)):
    if orig == "_":
        diffs.append(f"  Position {i+1}: _ -> {new}")
for d in diffs:
    print(d)
```

---

## Recipe 10: Fine-Grained Temperature Control for Diversity

Generate multiple sequence variants at different temperatures to explore the diversity-quality tradeoff.

```python
from esm.models.esm3 import ESM3
from esm.sdk.api import ESMProtein, GenerationConfig

model = ESM3.from_pretrained("esm3_sm_open_v1")

# Target backbone for inverse folding at varying diversity levels
backbone = ESMProtein.from_pdb("target_scaffold.pdb")
target_len = len(backbone.sequence)

# Temperature sweep: low (conservative) to high (diverse)
temperatures = [0.1, 0.2, 0.5, 0.7, 1.0]
results = {}

for temp in temperatures:
    prompt = ESMProtein.from_pdb("target_scaffold.pdb")
    prompt.sequence = "_" * target_len

    config = GenerationConfig(
        track="sequence",
        num_steps=100,
        temperature=temp,
    )

    designed = model.generate(prompt, config)
    results[temp] = designed.sequence
    print(f"T={temp:.1f}: {designed.sequence[:50]}...")

# Compare diversity: count unique residues at each position
print("\nDiversity analysis (unique residues per position):")
for pos in range(min(20, target_len)):
    residues_at_pos = set(results[t][pos] for t in temperatures)
    print(f"  Position {pos+1}: {len(residues_at_pos)} unique — {', '.join(sorted(residues_at_pos))}")

# Recommendations:
# - T=0.1-0.2: Use for final design candidates (highest confidence)
# - T=0.5:     Balanced exploration for initial screening
# - T=0.7-1.0: Maximum diversity for discovering novel solutions
# Low temperature sequences tend to score better on ProteinMPNN
# High temperature sequences explore more of sequence space
print("\nTip: Start with T=0.5 for screening, refine hits at T=0.1")
