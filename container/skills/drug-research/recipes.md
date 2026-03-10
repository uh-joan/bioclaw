# DiffDock Molecular Docking Recipes

> Copy-paste executable code templates for DiffDock protein-ligand docking.
> Parent skill: [SKILL.md](SKILL.md) — full drug research pipeline with MCP tools.

---

## Recipe 1: Single Protein-Ligand Docking (PDB + SMILES)

Dock one ligand into one protein structure using DiffDock.

```bash
# Prepare input CSV with one row
cat > input_single.csv << 'EOF'
protein_path,ligand_description,complex_name
/data/receptor.pdb,CCO,ethanol_dock
EOF

# Run DiffDock inference
python -m inference \
    --config default_inference_args.yaml \
    --protein_ligand_csv input_single.csv \
    --out_dir results/single_dock \
    --samples_per_complex 10 \
    --batch_size 6 \
    --no_final_step_noise

# Output: results/single_dock/ethanol_dock/rank1.sdf (top pose)
ls -la results/single_dock/ethanol_dock/rank*.sdf
```

---

## Recipe 2: Docking with Protein Sequence Instead of PDB

Predict structure from sequence via ESMFold, then dock.

```python
import subprocess, requests, os

# Predict structure from sequence using ESMFold API
sequence = "MKTLLILAVFCLAQGGSEAEAPTGTDEKALESNGKVLDV"
response = requests.post(
    "https://api.esmatlas.com/foldSequence/v1/pdb/",
    data=sequence, headers={"Content-Type": "text/plain"},
)
with open("target.pdb", "w") as f:
    f.write(response.text)

# Prepare DiffDock input
ligand_smiles = "c1ccc(cc1)C(=O)O"  # benzoic acid
with open("input_from_seq.csv", "w") as f:
    f.write("protein_path,ligand_description,complex_name\n")
    f.write(f"{os.path.abspath('target.pdb')},{ligand_smiles},target_dock\n")

# Run DiffDock
subprocess.run([
    "python", "-m", "inference",
    "--config", "default_inference_args.yaml",
    "--protein_ligand_csv", "input_from_seq.csv",
    "--out_dir", "results/from_sequence",
    "--samples_per_complex", "10",
    "--no_final_step_noise",
], check=True)
```

---

## Recipe 3: Batch Docking via CSV Input

Dock multiple ligands against one or more proteins using a CSV manifest.

```bash
# Create batch input CSV: each row is one docking job
cat > batch_input.csv << 'EOF'
protein_path,ligand_description,complex_name
/data/proteins/kinase.pdb,c1ccc2c(c1)cc(=O)oc2,coumarin_kinase
/data/proteins/kinase.pdb,CC(=O)Oc1ccccc1C(=O)O,aspirin_kinase
/data/proteins/kinase.pdb,c1ccc(cc1)O,phenol_kinase
/data/proteins/protease.pdb,CC(C)CC1=CC=C(C=C1)C(C)C(=O)O,ibuprofen_protease
EOF

# Run batch docking
python -m inference \
    --config default_inference_args.yaml \
    --protein_ligand_csv batch_input.csv \
    --out_dir results/batch_run \
    --samples_per_complex 10 \
    --batch_size 6 \
    --no_final_step_noise

# Report top confidence per complex
for dir in results/batch_run/*/; do
    name=$(basename "$dir")
    top_conf=$(cat "$dir/rank1_confidence.txt" 2>/dev/null || echo "N/A")
    echo "  $name: confidence = $top_conf"
done
```

---

## Recipe 4: Pre-Compute ESM Embeddings for Virtual Screening

Cache protein embeddings once to speed up repeated docking against the same target.

```bash
# Step 1: Generate ESM embeddings for the target protein
python datasets/esm_embedding_preparation.py \
    --protein_ligand_csv screen_input.csv \
    --out_file data/esm_embeddings/target_embeddings.pt

# Step 2: Run DiffDock with pre-computed embeddings (~60-80% faster)
python -m inference \
    --config default_inference_args.yaml \
    --protein_ligand_csv screen_input.csv \
    --out_dir results/screen \
    --samples_per_complex 10 \
    --batch_size 10 \
    --no_final_step_noise \
    --esm_embeddings_path data/esm_embeddings/target_embeddings.pt
```

---

## Recipe 5: Analyze Docking Results and Rank by Confidence

Parse DiffDock output directories and rank all poses by confidence score.

```python
import os, glob, csv

def parse_diffdock_results(results_dir):
    """Parse all DiffDock results and return sorted by confidence."""
    results = []
    for complex_dir in glob.glob(os.path.join(results_dir, "*")):
        if not os.path.isdir(complex_dir):
            continue
        name = os.path.basename(complex_dir)
        for sdf_file in sorted(glob.glob(os.path.join(complex_dir, "rank*.sdf"))):
            rank_name = os.path.basename(sdf_file).replace(".sdf", "")
            conf_file = sdf_file.replace(".sdf", "_confidence.txt")
            confidence = None
            if os.path.exists(conf_file):
                with open(conf_file) as f:
                    confidence = float(f.read().strip())
            results.append({"complex": name, "rank": rank_name,
                            "confidence": confidence, "sdf_path": sdf_file})
    results.sort(key=lambda x: x["confidence"] or float("-inf"), reverse=True)
    return results

results = parse_diffdock_results("results/batch_run")
print(f"{'Complex':<30} {'Rank':<8} {'Confidence':>10}")
print("-" * 52)
for r in results[:20]:
    conf = f"{r['confidence']:.3f}" if r['confidence'] is not None else "N/A"
    print(f"{r['complex']:<30} {r['rank']:<8} {conf:>10}")

# Export to CSV
with open("docking_rankings.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["complex", "rank", "confidence", "sdf_path"])
    writer.writeheader()
    writer.writerows(results)
```

---

## Recipe 6: Ensemble Docking Across Multiple Protein Conformations

Dock a ligand against multiple conformations and merge rankings.

```python
import os, subprocess, glob

conformations = [
    "/data/proteins/target_conf1.pdb",
    "/data/proteins/target_conf2.pdb",
    "/data/proteins/target_xray_apo.pdb",
    "/data/proteins/target_xray_holo.pdb",
]
ligand_smiles = "CC(=O)Oc1ccccc1C(=O)O"

# Run DiffDock for each conformation
for i, pdb_path in enumerate(conformations):
    name = f"conf{i+1}"
    csv_path = f"ensemble_{name}.csv"
    with open(csv_path, "w") as f:
        f.write("protein_path,ligand_description,complex_name\n")
        f.write(f"{pdb_path},{ligand_smiles},{name}\n")
    subprocess.run([
        "python", "-m", "inference",
        "--config", "default_inference_args.yaml",
        "--protein_ligand_csv", csv_path,
        "--out_dir", f"results/ensemble/{name}",
        "--samples_per_complex", "10",
        "--no_final_step_noise",
    ], check=True)

# Merge and rank across all conformations
all_results = []
for i in range(len(conformations)):
    name = f"conf{i+1}"
    for conf_file in glob.glob(f"results/ensemble/{name}/{name}/rank*_confidence.txt"):
        with open(conf_file) as f:
            score = float(f.read().strip())
        sdf = conf_file.replace("_confidence.txt", ".sdf")
        all_results.append((name, score, sdf))

all_results.sort(key=lambda x: x[1], reverse=True)
print("Top poses across all conformations:")
for conf, score, sdf in all_results[:10]:
    print(f"  {conf}: confidence={score:.3f}  {os.path.basename(sdf)}")
```

---

## Recipe 7: Virtual Screening Campaign Setup (>100 Compounds)

Large-scale virtual screen with cached embeddings and tiered hit classification.

```python
import csv, os, subprocess, glob

compound_library = "compound_library.csv"  # columns: smiles, compound_id
target_pdb = "/data/proteins/target.pdb"

# Generate DiffDock input CSV from compound library
with open(compound_library) as infile, open("vs_input.csv", "w", newline="") as out:
    reader = csv.DictReader(infile)
    writer = csv.writer(out)
    writer.writerow(["protein_path", "ligand_description", "complex_name"])
    for row in reader:
        writer.writerow([target_pdb, row["smiles"], row["compound_id"]])

# Pre-compute ESM embeddings (once per target)
subprocess.run(["python", "datasets/esm_embedding_preparation.py",
    "--protein_ligand_csv", "vs_input.csv",
    "--out_file", "data/esm_embeddings/vs_embeddings.pt"], check=True)

# Run screen with fewer poses per compound for speed
subprocess.run(["python", "-m", "inference",
    "--config", "default_inference_args.yaml",
    "--protein_ligand_csv", "vs_input.csv",
    "--out_dir", "results/virtual_screen",
    "--samples_per_complex", "5",
    "--batch_size", "16",
    "--no_final_step_noise",
    "--esm_embeddings_path", "data/esm_embeddings/vs_embeddings.pt"], check=True)

# Collect and rank hits
hits = []
for d in glob.glob("results/virtual_screen/*/"):
    name = os.path.basename(d.rstrip("/"))
    conf_file = os.path.join(d, "rank1_confidence.txt")
    if os.path.exists(conf_file):
        with open(conf_file) as f:
            hits.append((name, float(f.read().strip())))
hits.sort(key=lambda x: x[1], reverse=True)

with open("vs_ranked.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["compound_id", "confidence", "tier"])
    for name, score in hits:
        tier = "HIGH" if score > 0 else ("MODERATE" if score > -1.5 else "LOW")
        writer.writerow([name, f"{score:.4f}", tier])

print(f"Top 10 from {len(hits)} compounds:")
for name, score in hits[:10]:
    tier = "HIGH" if score > 0 else ("MODERATE" if score > -1.5 else "LOW")
    print(f"  {name:<30} {score:+.3f}  [{tier}]")
```

---

## Recipe 8: Integration with GNINA for Affinity Rescoring

Rescore DiffDock poses with GNINA CNN scoring for physics-based affinity estimates.

```bash
#!/bin/bash
# Requires: gnina (https://github.com/gnina/gnina)
RESULTS="results/batch_run"
RECEPTOR="/data/proteins/receptor.pdb"
echo "complex,rank,diffdock_conf,gnina_cnn_score,gnina_affinity" > gnina_rescored.csv

for complex_dir in "$RESULTS"/*/; do
    name=$(basename "$complex_dir")
    for rank in 1 2 3; do
        sdf="${complex_dir}rank${rank}.sdf"
        conf_file="${complex_dir}rank${rank}_confidence.txt"
        [ ! -f "$sdf" ] && continue
        dd_conf=$(cat "$conf_file" 2>/dev/null || echo "NA")

        # Score-only mode: rescore the DiffDock pose without redocking
        gnina_out=$(gnina --receptor "$RECEPTOR" --ligand "$sdf" \
            --score_only --cnn_scoring rescore 2>/dev/null | grep "^1" | head -1)
        cnn=$(echo "$gnina_out" | awk '{print $2}')
        aff=$(echo "$gnina_out" | awk '{print $3}')

        echo "${name},rank${rank},${dd_conf},${cnn},${aff}" >> gnina_rescored.csv
    done
done

echo "Rescored results in gnina_rescored.csv"
echo "Top hits by GNINA affinity (most negative = strongest):"
sort -t',' -k5 -n gnina_rescored.csv | head -6
```

---

## Recipe 9: Confidence Score Interpretation

Classify DiffDock confidence scores into actionable tiers.

```python
import os, glob

def interpret_confidence(score):
    """
    DiffDock confidence score tiers:
      HIGH:     score > 0      — likely correct pose (expected RMSD < 2 A)
      MODERATE: -1.5 < score <= 0  — plausible, validate with rescoring
      LOW:      score <= -1.5  — unreliable, try alternative methods

    These are NOT binding affinities. Use GNINA (Recipe 8) for affinity.
    """
    if score > 0:
        return "HIGH", "Likely correct pose (RMSD < 2 A)"
    elif score > -1.5:
        return "MODERATE", "Plausible — validate with rescoring"
    else:
        return "LOW", "Unreliable — try alternative conformations"

results_dir = "results/batch_run"
tier_counts = {"HIGH": 0, "MODERATE": 0, "LOW": 0}

print(f"{'Complex':<25} {'Score':>8} {'Tier':<10} {'Interpretation'}")
print("-" * 80)
for d in sorted(glob.glob(os.path.join(results_dir, "*"))):
    if not os.path.isdir(d):
        continue
    conf_file = os.path.join(d, "rank1_confidence.txt")
    if not os.path.exists(conf_file):
        continue
    with open(conf_file) as f:
        score = float(f.read().strip())
    tier, interp = interpret_confidence(score)
    tier_counts[tier] += 1
    print(f"{os.path.basename(d):<25} {score:>+8.3f} {tier:<10} {interp}")

total = sum(tier_counts.values())
print(f"\nSummary: {total} complexes")
for t in ["HIGH", "MODERATE", "LOW"]:
    print(f"  {t}: {tier_counts[t]} ({tier_counts[t]/max(total,1)*100:.0f}%)")
```

---

## Recipe 10: Extract Top Poses and Convert to PDB for Visualization

Collect best poses, convert to PDB, and generate a PyMOL viewing script.

```python
import os, glob, subprocess, shutil

def extract_top_poses(results_dir, output_dir, min_confidence=None):
    """Extract rank1 poses, optionally filter by confidence, convert to PDB."""
    os.makedirs(output_dir, exist_ok=True)
    extracted = []
    for d in sorted(glob.glob(os.path.join(results_dir, "*"))):
        if not os.path.isdir(d):
            continue
        name = os.path.basename(d)
        sdf = os.path.join(d, "rank1.sdf")
        conf_file = os.path.join(d, "rank1_confidence.txt")
        if not os.path.exists(sdf):
            continue
        confidence = None
        if os.path.exists(conf_file):
            with open(conf_file) as f:
                confidence = float(f.read().strip())
        if min_confidence and confidence is not None and confidence < min_confidence:
            continue
        out_sdf = os.path.join(output_dir, f"{name}.sdf")
        shutil.copy2(sdf, out_sdf)
        # Convert SDF to PDB via Open Babel (if available)
        out_pdb = os.path.join(output_dir, f"{name}.pdb")
        try:
            subprocess.run(["obabel", out_sdf, "-O", out_pdb, "-h"],
                           capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            out_pdb = None
        extracted.append({"name": name, "confidence": confidence,
                          "sdf": out_sdf, "pdb": out_pdb})
    return extracted

poses = extract_top_poses("results/batch_run", "results/top_poses", min_confidence=-1.5)
print(f"Extracted {len(poses)} poses to results/top_poses/")

# Generate PyMOL script
with open("results/top_poses/view_poses.pml", "w") as f:
    f.write("load /data/proteins/receptor.pdb, receptor\n")
    f.write("show cartoon, receptor\ncolor gray80, receptor\n\n")
    for p in poses:
        obj = p["name"].replace("-", "_")
        path = p["pdb"] or p["sdf"]
        f.write(f"load {path}, {obj}\nshow sticks, {obj}\n")
    f.write("\nzoom\nset stick_radius, 0.15\nbg_color white\n")

print("PyMOL script: pymol results/top_poses/view_poses.pml")
```
