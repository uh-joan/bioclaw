# ESM Advanced Recipes

Advanced recipes for ESM protein language models covering ESM3 multimodal generation, ESMFold structure prediction, ESM-IF1 inverse folding, and ESM C embeddings for downstream ML.

> **Parent skill**: [SKILL.md](SKILL.md) — full protein therapeutic design pipeline with MCP tools.
> **See also**: [recipes.md](recipes.md) — ESM basics (sequence generation, structure prediction, embeddings, masked prediction).

---

## Recipe 1: ESM3 Multimodal Generation (Sequence + Structure + Function)

Generate a protein conditioned on multiple tracks simultaneously for constrained design.

```python
from esm.models.esm3 import ESM3
from esm.sdk.api import ESMProtein, GenerationConfig

model = ESM3.from_pretrained("esm3_sm_open_v1")

# Load a target structure as structural constraint
target = ESMProtein.from_pdb("target_scaffold.pdb")
target_len = len(target.sequence)

# Multimodal prompt: fix structure, specify function, let ESM3 design sequence
protein = ESMProtein(
    sequence="_" * target_len,            # Sequence to be generated
    coordinates=target.coordinates,        # Structure constraint (backbone coords)
    function_annotations=[                 # Function constraint
        {"label": "IPR036388", "start": 1, "end": target_len},  # Desired fold
    ],
)

# Step 1: Generate sequence conditioned on structure + function
seq_config = GenerationConfig(
    track="sequence",
    num_steps=100,
    temperature=0.3,    # Conservative for high-confidence design
)
designed = model.generate(protein, seq_config)
print(f"Designed sequence ({target_len} aa): {designed.sequence[:50]}...")

# Step 2: Predict structure from designed sequence (self-consistency check)
check = ESMProtein(sequence=designed.sequence)
struct_config = GenerationConfig(track="structure", num_steps=50, temperature=0.5)
refolded = model.generate(check, struct_config)
refolded.to_pdb("multimodal_designed.pdb")

# Step 3: Predict function from designed sequence
func_config = GenerationConfig(track="function", num_steps=10)
annotated = model.generate(designed, func_config)
print(f"Predicted function: {annotated.function_annotations}")

print("\nSelf-consistency pipeline complete.")
print("Compare multimodal_designed.pdb to target_scaffold.pdb via RMSD.")
print("Low RMSD (<2 A) + matching function = high-confidence design.")
```

**Key Parameters:**
- `coordinates=target.coordinates`: Fixes backbone structure during sequence generation
- `function_annotations`: InterPro family/domain labels that guide functional conditioning
- `temperature=0.3`: Low temperature for designs that closely match constraints; increase to 0.7 for diversity
- Multimodal conditioning produces more constrained, higher-quality designs than single-track generation

**Expected Output:**
- Designed protein sequence that satisfies both structural and functional constraints
- Self-consistency check: refolded structure should match input backbone (RMSD < 2 A)
- Predicted function annotations validating the design matches target fold family

---

## Recipe 2: ESM3 Model Selection Guide

Select the appropriate ESM3 model based on task requirements, compute resources, and accuracy needs.

```python
from esm.models.esm3 import ESM3
from esm.sdk.api import ESMProtein, GenerationConfig
import time

# Model comparison matrix
models = {
    "esm3_sm_open_v1": {
        "params": "1.4B",
        "access": "Local (open weights)",
        "vram": "~16 GB",
        "speed": "Fast",
        "quality": "Good",
        "use_case": "Prototyping, screening, high-throughput design",
    },
    "esm3-medium-2024-08": {
        "params": "7B",
        "access": "Forge API",
        "vram": "API (no local GPU needed)",
        "speed": "Medium",
        "quality": "Better",
        "use_case": "Balanced quality/cost for production design",
    },
    "esm3-large-2024-08": {
        "params": "98B",
        "access": "Forge API",
        "vram": "API (no local GPU needed)",
        "speed": "Slower",
        "quality": "Best",
        "use_case": "Final design candidates, novel fold generation",
    },
}

print("ESM3 Model Selection Guide")
print("=" * 80)
for name, info in models.items():
    print(f"\n{name}")
    for key, val in info.items():
        print(f"  {key:12s}: {val}")

# Local model usage (open weights)
print("\n--- Local Model (esm3_sm_open_v1) ---")
model_local = ESM3.from_pretrained("esm3_sm_open_v1")
prompt = ESMProtein(sequence="_" * 50)
config = GenerationConfig(track="sequence", num_steps=50, temperature=0.7)

start = time.time()
result = model_local.generate(prompt, config)
elapsed = time.time() - start
print(f"Generated 50-aa sequence in {elapsed:.1f}s: {result.sequence}")

# Forge API usage (medium/large models)
print("\n--- Forge API Model (requires API key) ---")
print("Set environment variable: FORGE_API_KEY=<your_key>")
print("Usage:")
print("  from esm.sdk.forge import ESM3ForgeInferenceClient")
print("  client = ESM3ForgeInferenceClient(model='esm3-medium-2024-08', token=api_key)")
print("  result = client.generate(prompt, config)")

# Decision framework
print("\n--- Decision Framework ---")
print("1. Prototyping / >100 designs:     esm3_sm_open_v1 (local, free)")
print("2. Production / 10-100 designs:    esm3-medium (Forge API)")
print("3. Novel folds / final candidates: esm3-large (Forge API)")
print("4. Embeddings for ML:              ESM C 300M/600M (local, fast)")
```

**Key Parameters:**
- `esm3_sm_open_v1`: Free, local, requires GPU with ~16 GB VRAM; best for prototyping and high-throughput
- `esm3-medium-2024-08`: Forge API; 5x quality improvement over small for ~3x cost
- `esm3-large-2024-08`: Forge API; best quality for novel fold generation and final candidates
- API key required for Forge models: set `FORGE_API_KEY` environment variable

**Expected Output:**
- Model comparison table with parameters, access method, speed, and quality ratings
- Decision framework for selecting the right model per use case

---

## Recipe 3: ESMFold Structure Prediction (Single-Sequence)

Predict 3D protein structure from sequence using ESMFold (no MSA required, faster than AlphaFold2).

```python
import torch
from esm.models.esm3 import ESM3
from esm.sdk.api import ESMProtein, GenerationConfig

# ESMFold via ESM3 structure track
model = ESM3.from_pretrained("esm3_sm_open_v1")

sequences = {
    "lysozyme_fragment": "MKALIVLGLVLLSVTVQGKVFGRCELAAAMKRH",
    "insulin_b_chain":   "FVNQHLCGSHLVEALYLVCGERGFFYTPKT",
    "custom_design":     "MEELLKKAAYYIIDDFFLLKKEENNGGKKPPVVTT",
}

for name, seq in sequences.items():
    print(f"\n{'='*60}")
    print(f"Predicting structure for: {name} ({len(seq)} aa)")

    protein = ESMProtein(sequence=seq)
    config = GenerationConfig(
        track="structure",
        num_steps=50,           # Refinement steps (more = better, slower)
        temperature=0.5,        # Lower = more confident structure
    )

    result = model.generate(protein, config)

    # Save PDB
    output_path = f"{name}_esmfold.pdb"
    result.to_pdb(output_path)

    # Report coordinate statistics
    coords = result.coordinates
    if coords is not None:
        print(f"  Coordinates shape: {coords.shape}")
        print(f"  Coordinate range: [{coords.min():.1f}, {coords.max():.1f}]")
    print(f"  Saved to: {output_path}")

print("\n--- ESMFold vs AlphaFold2 ---")
print("ESMFold advantages:")
print("  - Single-sequence (no MSA search needed)")
print("  - 10-100x faster than AF2")
print("  - Good for designed proteins (no evolutionary data)")
print("ESMFold limitations:")
print("  - Lower accuracy than AF2 for natural proteins")
print("  - No multimer prediction")
print("  - Confidence estimation less calibrated")
```

**Key Parameters:**
- `num_steps=50`: Structure refinement iterations; increase to 100 for higher quality
- `temperature=0.5`: Lower values produce more confident (less diverse) structures
- ESMFold is single-sequence: ideal for designed proteins with no homologs
- No MSA database required: runs entirely from sequence

**Expected Output:**
- PDB files with predicted 3D coordinates for each input sequence
- Coordinate statistics for basic sanity checking
- Comparison guide: when to use ESMFold vs AlphaFold2

---

## Recipe 4: ESM C Embeddings for Downstream ML

Extract per-residue and per-sequence embeddings from ESM Cambrian for classification, regression, or clustering.

```python
import torch
import torch.nn.functional as F
import numpy as np
from esm.models.esmc import ESMC

# Select model size based on task
# esmc_300m: 300M params, fast, good for most tasks
# esmc_600m: 600M params, better representations, 2x slower
model = ESMC.from_pretrained("esmc_300m")
model.eval()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

sequences = {
    "kinase_active":   "MTEYKLVVVGAVGVGKSALTIQLIQNHFVDEYDPTIED",
    "kinase_inactive": "MTEYKLVVVGAVGVGKSALTIQLIQNHFVGEYDPTIED",  # G12V mutation
    "phosphatase":     "MTMITDSLAVVLQRRDWENPGVTQLNRLAAHPPFASWRN",
    "protease":        "IVGGYTCGANTVPYQVSLNSGYHFCGGSLINSQWVVSAA",
}

embeddings = {}
for name, seq in sequences.items():
    tokens = model.tokenizer.encode(seq)
    tokens = torch.tensor([tokens], dtype=torch.long).to(device)

    with torch.no_grad():
        output = model(tokens)
        emb = output.embeddings  # (1, seq_len+2, hidden_dim) with BOS/EOS

    # Per-residue embeddings (strip BOS and EOS tokens)
    per_residue = emb[0, 1:-1, :]  # (seq_len, hidden_dim)

    # Per-sequence embedding via mean pooling
    per_sequence = per_residue.mean(dim=0)  # (hidden_dim,)

    embeddings[name] = {
        "per_residue": per_residue.cpu(),
        "per_sequence": per_sequence.cpu(),
    }
    print(f"{name:20s}: residue shape={per_residue.shape}, sequence shape={per_sequence.shape}")

# Pairwise cosine similarity matrix
print("\nPairwise cosine similarity (sequence-level):")
names = list(embeddings.keys())
for i, name_a in enumerate(names):
    for j, name_b in enumerate(names):
        sim = F.cosine_similarity(
            embeddings[name_a]["per_sequence"].unsqueeze(0),
            embeddings[name_b]["per_sequence"].unsqueeze(0),
        ).item()
        print(f"  {name_a:20s} vs {name_b:20s}: {sim:.4f}")

# Save embeddings for downstream ML
torch.save(
    {name: data["per_sequence"] for name, data in embeddings.items()},
    "esmc_embeddings.pt",
)

# Use per-residue embeddings for site-level tasks
# e.g., active site prediction, mutation effect scoring, binding interface prediction
print("\nPer-residue embeddings ready for:")
print("  - Active site residue classification")
print("  - Binding interface prediction")
print("  - Variant effect scoring")
print("  - Secondary structure prediction")
```

**Key Parameters:**
- `esmc_300m`: 300M parameters, balanced speed/quality; `esmc_600m` for better representations
- BOS/EOS tokens must be stripped (`emb[0, 1:-1, :]`) for per-residue embeddings
- Mean pooling for sequence-level embedding; max pooling or CLS token are alternatives
- Cosine similarity > 0.9 indicates very similar proteins; 0.7-0.9 related; < 0.7 distinct

**Expected Output:**
- Per-residue embeddings: (seq_len, hidden_dim) tensors for site-level ML
- Per-sequence embeddings: (hidden_dim,) vectors for protein-level classification/clustering
- Pairwise similarity matrix for quick protein comparison

---

## Recipe 5: Inverse Folding with ESM-IF1

Design novel sequences that fold into a target backbone structure using ESM-IF1 (Inverse Folding model 1).

```python
import esm
import torch

# Load ESM-IF1 model
model, alphabet = esm.pretrained.esm_if1_gvp4_t16_142M_UR50()
model.eval()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Load target backbone structure
from esm.inverse_folding.util import load_structure, extract_coords_from_structure

# Load PDB and extract backbone coordinates
structure = load_structure("target_backbone.pdb", chain="A")
coords, native_seq = extract_coords_from_structure(structure)
coords = coords.to(device)

print(f"Target structure: {len(native_seq)} residues")
print(f"Native sequence:  {native_seq[:50]}...")

# Design multiple sequences at different temperatures
temperatures = [0.1, 0.2, 0.5]
designs = {}

for temp in temperatures:
    sequences = []
    for trial in range(5):  # 5 designs per temperature
        # Sample sequence conditioned on backbone coordinates
        sampled = model.sample(
            coords,
            temperature=temp,
        )
        sequences.append(sampled)

    designs[temp] = sequences
    print(f"\nT={temp}: {len(sequences)} designs generated")
    for i, seq in enumerate(sequences):
        # Calculate sequence identity to native
        identity = sum(a == b for a, b in zip(seq, native_seq)) / len(native_seq)
        print(f"  Design {i+1}: {seq[:40]}... (identity={identity:.1%})")

# Evaluate recovery rate (how much of native sequence is recovered)
print("\n--- Sequence Recovery Analysis ---")
for temp, seqs in designs.items():
    recoveries = []
    for seq in seqs:
        recovery = sum(a == b for a, b in zip(seq, native_seq)) / len(native_seq)
        recoveries.append(recovery)
    mean_rec = sum(recoveries) / len(recoveries)
    print(f"T={temp}: mean recovery = {mean_rec:.1%}")

print("\nRecommendations:")
print("  T=0.1: Highest recovery, most native-like (conservative redesign)")
print("  T=0.2: Balanced novelty and foldability (standard design)")
print("  T=0.5: Maximum diversity (de novo design, validate with ESMFold)")
```

**Key Parameters:**
- `esm_if1_gvp4_t16_142M_UR50`: 142M parameter model trained on CATH structures
- `temperature=0.1`: Very conservative (near-native); `0.2` standard; `0.5` diverse
- `chain="A"`: Specify which PDB chain to use as backbone template
- Higher temperatures produce more diverse but potentially less foldable sequences
- ESM-IF1 operates on backbone coordinates (N, CA, C atoms)

**Expected Output:**
- Multiple designed sequences per temperature setting
- Sequence identity to native protein at each temperature
- Recovery rate analysis showing diversity-fidelity tradeoff

---

## Recipe 6: Masked Language Modeling for Variant Effect Scoring

Score the effect of mutations using ESM3 masked language modeling log-likelihood ratios.

```python
from esm.models.esm3 import ESM3
from esm.sdk.api import ESMProtein, GenerationConfig
import numpy as np

model = ESM3.from_pretrained("esm3_sm_open_v1")

# Wild-type sequence
wt_sequence = "MKTLLILAVFCLAQGGSEAEAPTGTDEKALESNG"
print(f"Wild-type sequence ({len(wt_sequence)} aa): {wt_sequence}")

# Define mutations to score
mutations = [
    ("A10V", 9, "V"),   # Position 10: A -> V (conservative)
    ("G15D", 14, "D"),  # Position 15: G -> D (charge change)
    ("L5P",  4, "P"),   # Position 5: L -> P (helix breaker)
    ("E20K", 19, "K"),  # Position 20: E -> K (charge reversal)
    ("A10A", 9, "A"),   # Synonymous (control, should score ~0)
]

def score_mutation(model, wt_seq, position, alt_aa):
    """Score a single mutation using masked prediction likelihood.

    Returns log-likelihood ratio: positive = favorable, negative = deleterious.
    """
    wt_aa = wt_seq[position]

    # Mask the position of interest
    masked_seq = wt_seq[:position] + "_" + wt_seq[position+1:]
    protein = ESMProtein(sequence=masked_seq)

    # Generate with very low temperature (most likely prediction)
    config = GenerationConfig(
        track="sequence",
        num_steps=1,          # Single step for masked position
        temperature=0.01,     # Near-deterministic
    )

    filled = model.generate(protein, config)
    predicted_aa = filled.sequence[position]

    # Simple scoring: does the model prefer WT or mutant?
    wt_match = 1.0 if predicted_aa == wt_aa else 0.0
    mut_match = 1.0 if predicted_aa == alt_aa else 0.0

    return {
        "predicted": predicted_aa,
        "wt_match": wt_match,
        "mut_match": mut_match,
    }

# Score all mutations
print(f"\n{'Mutation':>10s}  {'WT':>3s}  {'Alt':>3s}  {'Predicted':>9s}  {'Assessment':>12s}")
print("-" * 55)
for name, pos, alt in mutations:
    result = score_mutation(model, wt_sequence, pos, alt)
    wt_aa = wt_sequence[pos]

    if result["predicted"] == wt_aa:
        assessment = "WT preferred"
    elif result["predicted"] == alt:
        assessment = "Mut tolerated"
    else:
        assessment = "Neither"

    print(f"{name:>10s}  {wt_aa:>3s}  {alt:>3s}  {result['predicted']:>9s}  {assessment:>12s}")

print("\nInterpretation:")
print("  WT preferred:   Model strongly predicts wild-type -> mutation likely deleterious")
print("  Mut tolerated:  Model predicts mutant AA -> mutation likely neutral/beneficial")
print("  Neither:        Position is variable -> mutation effect uncertain")
```

**Key Parameters:**
- `num_steps=1`: Single-step prediction at the masked position for scoring
- `temperature=0.01`: Near-deterministic prediction of most likely amino acid
- Log-likelihood ratio scoring: compare probability of WT vs mutant at each position
- Higher probabilities for WT indicate the mutation is likely deleterious
- This is a zero-shot method requiring no training data

**Expected Output:**
- Per-mutation predicted amino acid and assessment
- Classification as WT preferred (deleterious), Mut tolerated (neutral), or uncertain
- Quick variant prioritization without experimental data

---

## Recipe 7: Batch Processing via Forge API

Submit multiple protein design jobs to the ESM3 Forge API with async retrieval for high-throughput workflows.

```python
import os
import asyncio
from esm.sdk.forge import ESM3ForgeInferenceClient
from esm.sdk.api import ESMProtein, GenerationConfig

# Initialize Forge API client
api_key = os.environ.get("FORGE_API_KEY")
if not api_key:
    print("Set FORGE_API_KEY environment variable")
    print("Get your key at: https://forge.evolutionaryscale.ai/")
    exit(1)

client = ESM3ForgeInferenceClient(
    model="esm3-medium-2024-08",  # or "esm3-large-2024-08" for best quality
    token=api_key,
)

# Define batch of design jobs
design_jobs = [
    {"name": f"design_{i}", "length": length, "temperature": temp}
    for i, (length, temp) in enumerate([
        (50, 0.3), (50, 0.5), (50, 0.7),
        (80, 0.3), (80, 0.5), (80, 0.7),
        (100, 0.3), (100, 0.5), (100, 0.7),
    ])
]

async def run_design_job(client, job):
    """Run a single design job via Forge API."""
    prompt = ESMProtein(sequence="_" * job["length"])
    config = GenerationConfig(
        track="sequence",
        num_steps=job["length"],
        temperature=job["temperature"],
    )
    result = client.generate(prompt, config)
    return {
        "name": job["name"],
        "length": job["length"],
        "temperature": job["temperature"],
        "sequence": result.sequence,
    }

async def run_batch(client, jobs, max_concurrent=5):
    """Run batch of design jobs with concurrency control."""
    semaphore = asyncio.Semaphore(max_concurrent)
    results = []

    async def limited_job(job):
        async with semaphore:
            return await asyncio.to_thread(run_design_job_sync, client, job)

    tasks = [limited_job(job) for job in jobs]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

def run_design_job_sync(client, job):
    """Synchronous wrapper for Forge API call."""
    prompt = ESMProtein(sequence="_" * job["length"])
    config = GenerationConfig(
        track="sequence",
        num_steps=job["length"],
        temperature=job["temperature"],
    )
    result = client.generate(prompt, config)
    return {
        "name": job["name"],
        "length": job["length"],
        "temperature": job["temperature"],
        "sequence": result.sequence,
    }

# Sequential execution (simpler, works without async)
print(f"Running {len(design_jobs)} design jobs via Forge API...")
results = []
for i, job in enumerate(design_jobs):
    try:
        result = run_design_job_sync(client, job)
        results.append(result)
        print(f"  [{i+1}/{len(design_jobs)}] {job['name']}: "
              f"L={job['length']}, T={job['temperature']}, "
              f"seq={result['sequence'][:30]}...")
    except Exception as e:
        print(f"  [{i+1}/{len(design_jobs)}] {job['name']}: FAILED - {e}")

# Save results
print(f"\nCompleted {len(results)}/{len(design_jobs)} jobs")
for r in results:
    with open(f"{r['name']}.fasta", "w") as f:
        f.write(f">{r['name']} L={r['length']} T={r['temperature']}\n")
        f.write(f"{r['sequence']}\n")
print("Results saved as FASTA files.")
```

**Key Parameters:**
- `model="esm3-medium-2024-08"`: Medium model for balanced quality/cost; `"esm3-large-2024-08"` for best quality
- `max_concurrent=5`: Limit concurrent API requests to avoid rate limiting
- `FORGE_API_KEY`: Required environment variable for API authentication
- Sequential mode shown for simplicity; async mode available for parallel execution
- Forge API handles GPU allocation server-side

**Expected Output:**
- FASTA files for each design job with metadata in headers
- Progress tracking for batch submission
- Error handling for failed API calls

---

## Recipe 8: ESM Attention-Based Contact Map Prediction

Extract attention weights from ESM to predict residue-residue contacts.

```python
import torch
import numpy as np
import matplotlib.pyplot as plt
from esm.models.esmc import ESMC

model = ESMC.from_pretrained("esmc_300m")
model.eval()

sequence = "MKTLLILAVFCLAQGGSEAEAPTGTDEKALESNG"
tokens = model.tokenizer.encode(sequence)
tokens = torch.tensor([tokens], dtype=torch.long)

# Extract attention maps from all layers
with torch.no_grad():
    output = model(tokens)
    embeddings = output.embeddings

# For contact prediction, use the embeddings to compute an attention-like
# contact score via outer product of per-residue representations
per_residue = embeddings[0, 1:-1, :]  # Strip BOS/EOS
n_residues = per_residue.shape[0]

# Compute pairwise similarity (cosine) as contact proxy
norms = per_residue / per_residue.norm(dim=1, keepdim=True)
contact_scores = torch.mm(norms, norms.t()).numpy()

# Apply sequence separation filter (contacts must be >= 6 residues apart)
min_sep = 6
for i in range(n_residues):
    for j in range(n_residues):
        if abs(i - j) < min_sep:
            contact_scores[i, j] = 0

# Symmetrize
contact_scores = (contact_scores + contact_scores.T) / 2

# Extract top predicted contacts
n_top = min(n_residues, 50)
flat_indices = np.argsort(contact_scores.flatten())[::-1]
top_contacts = []
seen = set()
for idx in flat_indices:
    i, j = divmod(idx, n_residues)
    if (i, j) not in seen and (j, i) not in seen and i != j:
        top_contacts.append((i, j, contact_scores[i, j]))
        seen.add((i, j))
    if len(top_contacts) >= n_top:
        break

print(f"Top {len(top_contacts)} predicted contacts (|i-j| >= {min_sep}):")
for i, j, score in top_contacts[:20]:
    print(f"  {sequence[i]}{i+1} - {sequence[j]}{j+1}: score={score:.3f}")

# Plot contact map
fig, ax = plt.subplots(figsize=(8, 8))
im = ax.imshow(contact_scores, cmap="hot_r", aspect="equal")
ax.set_xlabel("Residue position")
ax.set_ylabel("Residue position")
ax.set_title(f"ESM-derived Contact Map ({len(sequence)} aa)")
plt.colorbar(im, ax=ax, label="Contact score")

# Mark top contacts
for i, j, score in top_contacts[:20]:
    ax.plot(j, i, "go", markersize=3, alpha=0.7)
    ax.plot(i, j, "go", markersize=3, alpha=0.7)

plt.tight_layout()
plt.savefig("esm_contact_map.png", dpi=150)
print("\nContact map saved to esm_contact_map.png")
```

**Key Parameters:**
- `min_sep=6`: Minimum sequence separation for meaningful contacts (short-range contacts are trivial)
- Contact scores derived from cosine similarity of per-residue ESM embeddings
- Top-L/5 contacts (L = sequence length) is a standard benchmark metric
- Higher scores indicate residues likely in spatial proximity

**Expected Output:**
- Ranked list of predicted residue-residue contacts with scores
- Contact map heatmap PNG for visualization
- Contact predictions useful for structure validation and fold assessment

---

## Recipe 9: Zero-Shot Variant Effect Prediction (Log-Likelihood Ratio)

Score all possible single-point mutations at every position using ESM log-likelihood ratios.

```python
import torch
import numpy as np
from esm.models.esmc import ESMC

model = ESMC.from_pretrained("esmc_300m")
model.eval()

AMINO_ACIDS = list("ACDEFGHIKLMNPQRSTVWY")

sequence = "MKTLLILAVFCLAQGGS"
tokens = model.tokenizer.encode(sequence)
tokens_tensor = torch.tensor([tokens], dtype=torch.long)

# Get wild-type log-likelihood
with torch.no_grad():
    wt_output = model(tokens_tensor)
    wt_embeddings = wt_output.embeddings[0, 1:-1, :]  # per-residue

# Score all single mutations
print(f"Scoring all single mutations for {len(sequence)}-aa sequence...")
print(f"Total variants: {len(sequence) * 19} (20 AAs - 1 WT per position)\n")

# Compute mutation scores using embedding perturbation
# For each position, compare WT embedding magnitude vs mutant
scores = np.zeros((len(sequence), 20))

for pos in range(len(sequence)):
    wt_aa = sequence[pos]
    wt_idx = AMINO_ACIDS.index(wt_aa) if wt_aa in AMINO_ACIDS else -1

    for aa_idx, aa in enumerate(AMINO_ACIDS):
        if aa == wt_aa:
            scores[pos, aa_idx] = 0.0  # WT is reference
            continue

        # Create mutant sequence
        mut_seq = sequence[:pos] + aa + sequence[pos+1:]
        mut_tokens = model.tokenizer.encode(mut_seq)
        mut_tokens_tensor = torch.tensor([mut_tokens], dtype=torch.long)

        with torch.no_grad():
            mut_output = model(mut_tokens_tensor)
            mut_emb = mut_output.embeddings[0, 1:-1, :]

        # Score: cosine similarity change at mutated position
        wt_norm = wt_embeddings[pos] / wt_embeddings[pos].norm()
        mut_norm = mut_emb[pos] / mut_emb[pos].norm()
        score = torch.dot(wt_norm, mut_norm).item() - 1.0  # 0 = identical, -2 = opposite

        scores[pos, aa_idx] = score

# Display most deleterious and tolerated mutations
print(f"{'Position':>8} {'WT':>3} {'Mut':>3} {'Score':>8} {'Effect':>12}")
print("-" * 40)

all_mutations = []
for pos in range(len(sequence)):
    for aa_idx, aa in enumerate(AMINO_ACIDS):
        if aa != sequence[pos]:
            all_mutations.append((pos, sequence[pos], aa, scores[pos, aa_idx]))

# Sort by score (most negative = most deleterious)
all_mutations.sort(key=lambda x: x[3])

print("\nTop 10 most deleterious mutations:")
for pos, wt, mut, score in all_mutations[:10]:
    print(f"  {wt}{pos+1}{mut}: score={score:.4f}")

print("\nTop 10 most tolerated mutations:")
for pos, wt, mut, score in all_mutations[-10:]:
    print(f"  {wt}{pos+1}{mut}: score={score:.4f}")

# Per-position tolerance (average mutation score)
pos_tolerance = scores.mean(axis=1)
print(f"\nPer-position mutational tolerance:")
for pos in range(len(sequence)):
    bar = "#" * int(abs(pos_tolerance[pos]) * 100)
    print(f"  {sequence[pos]}{pos+1:3d}: {pos_tolerance[pos]:+.4f} {bar}")
```

**Key Parameters:**
- Zero-shot: no training data required, uses pretrained ESM model directly
- Embedding cosine similarity as mutation effect proxy (more negative = more disruptive)
- Scores all 19 possible substitutions at every position
- Per-position tolerance: average score across all mutations indicates evolutionary constraint

**Expected Output:**
- Ranked list of most deleterious and most tolerated mutations
- Per-position mutational tolerance profile
- Heatmap-ready matrix of mutation effects (positions x amino acids)

---

## Recipe 10: ESM Embeddings + UMAP for Protein Family Visualization

Cluster and visualize protein families using ESM embeddings reduced with UMAP.

```python
import torch
import numpy as np
import matplotlib.pyplot as plt
from esm.models.esmc import ESMC

model = ESMC.from_pretrained("esmc_300m")
model.eval()

# Example protein families (replace with your sequences)
proteins = {
    # Kinases
    "KRAS":    ("kinase", "MTEYKLVVVGAVGVGKSALTIQLIQNHFVDEYDPTIED"),
    "HRAS":    ("kinase", "MTEYKLVVLGAVGVGKSALTIQLIQNHFVDEYDPTIED"),
    "NRAS":    ("kinase", "MTEYKLVVLGAVGVGKSALTTQLIMQLNKFVDEYDPTIED"),
    # Proteases
    "trypsin": ("protease", "IVGGYTCGANTVPYQVSLNSGYHFCGGSLINSQWVVSAA"),
    "chymo":   ("protease", "IVNGEEAVPGSWPWQVSLQDKTGFHFCGGSLINENWVVTAA"),
    "elastase":("protease", "VVGGTEAQRNSWPSQISLQYRSGSSWAHTCGGTLIRQNWVMTA"),
    # Hormones
    "insulin": ("hormone", "MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGER"),
    "glucagon":("hormone", "MKSIYFVAGLFVMLVQGSWQRSLQDTEEKSRSFSASQADPLSDPDQ"),
    "leptin":  ("hormone", "MHWGTLCGFLWLWPYLFYVQASKPICVPLDQQVTLLASLALVTHD"),
}

# Extract embeddings
names, families, embeddings = [], [], []
for name, (family, seq) in proteins.items():
    tokens = model.tokenizer.encode(seq)
    tokens_tensor = torch.tensor([tokens], dtype=torch.long)
    with torch.no_grad():
        output = model(tokens_tensor)
        emb = output.embeddings[0, 1:-1, :].mean(dim=0).numpy()
    names.append(name)
    families.append(family)
    embeddings.append(emb)

embeddings = np.array(embeddings)
print(f"Embedding matrix: {embeddings.shape}")

# UMAP dimensionality reduction
try:
    import umap
    reducer = umap.UMAP(
        n_components=2,
        n_neighbors=min(5, len(embeddings) - 1),
        min_dist=0.3,
        metric="cosine",
        random_state=42,
    )
    coords_2d = reducer.fit_transform(embeddings)
    method = "UMAP"
except ImportError:
    # Fallback to PCA if UMAP not installed
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2, random_state=42)
    coords_2d = pca.fit_transform(embeddings)
    method = "PCA"
    print("UMAP not installed, falling back to PCA. Install: pip install umap-learn")

# Plot
fig, ax = plt.subplots(figsize=(10, 8))
family_colors = {"kinase": "red", "protease": "blue", "hormone": "green"}

for family in set(families):
    mask = [f == family for f in families]
    x = coords_2d[mask, 0]
    y = coords_2d[mask, 1]
    ax.scatter(x, y, c=family_colors.get(family, "grey"),
               label=family, s=100, edgecolors="black", linewidth=0.5)

for i, name in enumerate(names):
    ax.annotate(name, (coords_2d[i, 0], coords_2d[i, 1]),
                fontsize=8, ha="center", va="bottom")

ax.set_xlabel(f"{method} 1")
ax.set_ylabel(f"{method} 2")
ax.set_title(f"Protein Family Visualization (ESM C + {method})")
ax.legend()
plt.tight_layout()
plt.savefig("protein_family_umap.png", dpi=150)
print(f"\nVisualization saved to protein_family_umap.png")
print(f"Method: {method} on ESM C 300M embeddings (cosine metric)")
```

**Key Parameters:**
- `n_neighbors=5`: UMAP local neighborhood size; smaller values preserve local structure, larger values reveal global patterns
- `min_dist=0.3`: Controls cluster tightness; smaller = tighter clusters
- `metric="cosine"`: Cosine distance on ESM embeddings; alternatives: `"euclidean"`, `"correlation"`
- Falls back to PCA if UMAP not installed
- ESM embeddings capture functional similarity beyond sequence identity

**Expected Output:**
- 2D scatter plot with proteins colored by family
- Proteins within the same family should cluster together
- Cross-family distances reveal functional relationships

---

## Recipe 11: Conditional Generation with Fixed Active Site Residues

Design a protein scaffold while keeping specific active site or binding site residues fixed.

```python
from esm.models.esm3 import ESM3
from esm.sdk.api import ESMProtein, GenerationConfig

model = ESM3.from_pretrained("esm3_sm_open_v1")

# Define the design with fixed active site residues
# Example: 80-residue protein with catalytic triad at positions 30, 55, 75
total_length = 80

# Create sequence with fixed positions and masked scaffold
# Fixed residues: H30 (His), D55 (Asp), S75 (Ser) — serine protease triad
sequence_template = list("_" * total_length)
fixed_positions = {
    29: "H",   # His at position 30 (0-indexed: 29)
    54: "D",   # Asp at position 55 (0-indexed: 54)
    74: "S",   # Ser at position 75 (0-indexed: 74)
}

for pos, aa in fixed_positions.items():
    sequence_template[pos] = aa

sequence_with_fixed = "".join(sequence_template)
print(f"Template ({total_length} aa):")
print(f"  {sequence_with_fixed}")
print(f"  Fixed positions: {', '.join(f'{aa}{pos+1}' for pos, aa in fixed_positions.items())}")

# Generate multiple designs
n_designs = 5
designs = []

for i in range(n_designs):
    protein = ESMProtein(sequence=sequence_with_fixed)
    config = GenerationConfig(
        track="sequence",
        num_steps=total_length,
        temperature=0.5,
    )

    result = model.generate(protein, config)

    # Verify fixed residues are preserved
    fixed_preserved = all(result.sequence[pos] == aa for pos, aa in fixed_positions.items())

    designs.append({
        "sequence": result.sequence,
        "fixed_preserved": fixed_preserved,
    })

    print(f"\nDesign {i+1}:")
    print(f"  Sequence: {result.sequence}")
    print(f"  Fixed residues preserved: {fixed_preserved}")
    if not fixed_preserved:
        for pos, aa in fixed_positions.items():
            if result.sequence[pos] != aa:
                print(f"    WARNING: Position {pos+1} changed from {aa} to {result.sequence[pos]}")

# Validate designs: predict structure for each
print("\n--- Structure Validation ---")
for i, design in enumerate(designs):
    if not design["fixed_preserved"]:
        print(f"Design {i+1}: SKIPPED (fixed residues not preserved)")
        continue

    protein = ESMProtein(sequence=design["sequence"])
    struct_config = GenerationConfig(track="structure", num_steps=50)
    structure = model.generate(protein, struct_config)
    structure.to_pdb(f"conditional_design_{i+1}.pdb")
    print(f"Design {i+1}: Structure saved to conditional_design_{i+1}.pdb")

# Check spatial arrangement of active site residues
print("\n--- Active Site Geometry Check ---")
print("After structure prediction, verify:")
print("  1. H30-D55 distance < 4 A (hydrogen bond)")
print("  2. D55-S75 distance < 4 A (charge relay)")
print("  3. Active site residues are solvent-accessible")
print("  4. Scaffold does not occlude the catalytic triad")
```

**Key Parameters:**
- Fixed positions use explicit amino acid letters in the sequence template
- Masked positions use `_` (underscore) for ESM3 to fill
- `num_steps=total_length`: More steps for longer sequences ensures all positions are sampled
- `temperature=0.5`: Balanced between diversity and quality for scaffold design
- Always verify fixed residues are preserved in the output

**Expected Output:**
- Multiple designed protein sequences with catalytic residues at specified positions
- Verification that fixed positions are preserved
- PDB structures for geometric validation of active site arrangement
- Guidelines for checking active site geometry in predicted structures

---

## Quick Reference

| Task | Recipe | Key Model/Method |
|------|--------|-----------------|
| Multimodal design | #1 | ESM3 (sequence + structure + function) |
| Model selection | #2 | esm3_sm / medium / large comparison |
| Structure prediction | #3 | ESMFold (single-sequence) |
| Embeddings for ML | #4 | ESM C (300M/600M) |
| Inverse folding | #5 | ESM-IF1 (backbone -> sequence) |
| Variant scoring | #6 | ESM3 masked LM |
| Batch API processing | #7 | Forge API |
| Contact prediction | #8 | ESM C attention/embedding |
| Zero-shot mutations | #9 | ESM C log-likelihood |
| Family visualization | #10 | ESM C + UMAP |
| Conditional design | #11 | ESM3 fixed-position generation |

---

## Cross-Skill Routing

- ESM basics (generation, embeddings, masked prediction) --> [recipes.md](recipes.md)
- Full protein therapeutic design pipeline --> parent [SKILL.md](SKILL.md)
- AlphaFold2 multimer structure prediction --> `protein-structure-retrieval`
- Antibody CDR design and humanization --> `antibody-engineering`
- Small molecule binding to designed proteins --> `binder-discovery-specialist`
