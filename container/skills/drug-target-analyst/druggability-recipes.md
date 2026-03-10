# Multi-Dimensional Druggability Assessment Recipes

Executable code templates for systematic druggability evaluation combining structural, chemical, genetic, expression, and clinical data.
Each recipe is production-ready Python with inline parameter documentation.

> **Parent skill**: [SKILL.md](SKILL.md) — full drug target analyst pipeline with MCP tools.
> **See also**: [molecular-glue-discovery](../molecular-glue-discovery/SKILL.md) for TPD-based tractability assessment of undruggable targets.

---

## Recipe 1: Protein Class Druggability Scoring

Assign a prior druggability score based on the target protein class. Protein class is the single strongest predictor of druggability.

```python
import pandas as pd

# Protein class druggability priors based on historical drug approval rates
# and chemical tractability evidence from ChEMBL and Open Targets
PROTEIN_CLASS_SCORES = {
    # High druggability (score 0.7-1.0)
    "Kinase":                    {"score": 0.90, "modality": "small molecule", "rationale": ">70 FDA-approved kinase inhibitors; deep SAR knowledge; well-defined ATP pocket"},
    "GPCR":                      {"score": 0.90, "modality": "small molecule", "rationale": "~34% of all FDA-approved drugs target GPCRs; orthosteric and allosteric sites"},
    "Nuclear hormone receptor":  {"score": 0.85, "modality": "small molecule", "rationale": "Well-defined ligand-binding domain; extensive precedent (ER, AR, GR, PPAR)"},
    "Protease":                  {"score": 0.85, "modality": "small molecule", "rationale": "Catalytic triad/active site; HCV/HIV protease inhibitors prove tractability"},
    "Phosphodiesterase":         {"score": 0.80, "modality": "small molecule", "rationale": "Conserved catalytic domain; sildenafil, roflumilast precedent"},
    "Epigenetic reader/writer":  {"score": 0.75, "modality": "small molecule", "rationale": "BET bromodomains, HDACs, DNMTs; druggable pockets exist"},

    # Medium druggability (score 0.4-0.7)
    "Ion channel":               {"score": 0.65, "modality": "small molecule", "rationale": "Druggable but selectivity is challenging; many approved channel blockers"},
    "Transporter":               {"score": 0.60, "modality": "small molecule", "rationale": "SGLT2 inhibitors, SSRIs prove tractability; structural biology advancing"},
    "Enzyme (other)":            {"score": 0.60, "modality": "small molecule", "rationale": "Depends on active site accessibility; variable by enzyme class"},
    "Cell surface receptor":     {"score": 0.55, "modality": "antibody/small molecule", "rationale": "Antibody-accessible; small molecule depends on pocket existence"},
    "Ligand-gated ion channel":  {"score": 0.55, "modality": "small molecule", "rationale": "Benzodiazepines, barbiturates; orthosteric/allosteric sites"},
    "E3 ubiquitin ligase":       {"score": 0.50, "modality": "small molecule/degrader", "rationale": "Emerging target class; CRBN/VHL validated for TPD"},

    # Low druggability - conventional (score 0.1-0.4) → consider TPD
    "Transcription factor":      {"score": 0.20, "modality": "TPD/molecular glue", "rationale": "No enzymatic activity; flat surfaces; IKZF1/3 degradation proves TPD approach"},
    "Scaffolding protein":       {"score": 0.15, "modality": "TPD/PROTAC", "rationale": "PPI-mediated function; no catalytic site; consider degradation"},
    "Adaptor protein":           {"score": 0.15, "modality": "TPD/PROTAC", "rationale": "Similar to scaffolding; function through protein interactions"},
    "Intrinsically disordered":  {"score": 0.10, "modality": "TPD/PROTAC", "rationale": "No stable structure for ligand binding; easier to degrade than inhibit"},
    "Structural protein":        {"score": 0.10, "modality": "gene therapy", "rationale": "No enzymatic function; consider gene therapy or ASO"},
}


def score_protein_class(target_name, protein_class):
    """
    Score a target's druggability based on its protein class.

    Parameters
    ----------
    target_name : str
        Gene symbol or protein name
    protein_class : str
        One of the keys in PROTEIN_CLASS_SCORES (case-insensitive match)

    Returns
    -------
    dict with score (0-1), recommended modality, and rationale
    """
    # Case-insensitive lookup
    match = None
    for key, value in PROTEIN_CLASS_SCORES.items():
        if key.lower() == protein_class.lower():
            match = value
            break

    if match is None:
        return {
            "target": target_name,
            "protein_class": protein_class,
            "score": 0.30,  # Default for unknown class
            "modality": "unknown",
            "rationale": f"Protein class '{protein_class}' not in reference database; manual assessment required",
        }

    return {
        "target": target_name,
        "protein_class": protein_class,
        "druggability_score": match["score"],
        "recommended_modality": match["modality"],
        "rationale": match["rationale"],
        "tier": "HIGH" if match["score"] >= 0.7 else "MEDIUM" if match["score"] >= 0.4 else "LOW (consider TPD)",
    }


# Example usage
result = score_protein_class("IKZF1", "Transcription factor")
print(f"Target: {result['target']}")
print(f"Class: {result['protein_class']}")
print(f"Score: {result['druggability_score']}")
print(f"Modality: {result['recommended_modality']}")
print(f"Tier: {result['tier']}")
print(f"Rationale: {result['rationale']}")
```

**Key Parameters:**
- `protein_class`: Target protein family classification (from UniProt, Open Targets, or manual curation)
- Scores are based on historical FDA approval rates and chemical tractability data from ChEMBL

**Expected Output:**
- Druggability score (0-1), recommended therapeutic modality, druggability tier, and evidence-based rationale

---

## Recipe 2: ChEMBL Ligand Count Query

Count the number of bioactive compounds with IC50/Ki < 1 uM for a target. More chemical matter = higher chemical tractability.

```python
import requests
import pandas as pd

def count_chembl_ligands(target_chembl_id, activity_threshold_nm=1000):
    """
    Count bioactive compounds in ChEMBL for a target.

    Parameters
    ----------
    target_chembl_id : str
        ChEMBL target ID (e.g., "CHEMBL202" for EGFR)
    activity_threshold_nm : float
        Activity cutoff in nM (default: 1000 nM = 1 μM)

    Returns
    -------
    dict with ligand counts, potency distribution, and tractability assessment
    """
    base_url = "https://www.ebi.ac.uk/chembl/api/data/activity.json"

    # Query bioactivity data for the target
    params = {
        "target_chembl_id": target_chembl_id,
        "standard_type__in": "IC50,Ki,Kd,EC50",
        "standard_relation": "=",
        "standard_units": "nM",
        "limit": 1000,
    }
    resp = requests.get(base_url, params=params)
    data = resp.json()

    activities = data.get("activities", [])

    # Parse and filter activities
    records = []
    for act in activities:
        try:
            value = float(act.get("standard_value", None))
            records.append({
                "molecule_chembl_id": act.get("molecule_chembl_id"),
                "standard_type": act.get("standard_type"),
                "standard_value_nM": value,
                "pchembl_value": act.get("pchembl_value"),
            })
        except (TypeError, ValueError):
            continue

    df = pd.DataFrame(records)

    if df.empty:
        return {
            "target_chembl_id": target_chembl_id,
            "total_activities": 0,
            "unique_compounds": 0,
            "compounds_below_threshold": 0,
            "tractability": "INTRACTABLE — no chemical matter",
        }

    # Count unique compounds below threshold
    potent = df[df["standard_value_nM"] <= activity_threshold_nm]
    unique_total = df["molecule_chembl_id"].nunique()
    unique_potent = potent["molecule_chembl_id"].nunique()

    # Potency distribution
    sub_10nm = df[df["standard_value_nM"] <= 10]["molecule_chembl_id"].nunique()
    sub_100nm = df[df["standard_value_nM"] <= 100]["molecule_chembl_id"].nunique()
    sub_1um = df[df["standard_value_nM"] <= 1000]["molecule_chembl_id"].nunique()

    # Tractability assessment
    if unique_potent >= 50:
        tractability = "HIGH — extensive chemical matter (≥50 compounds < 1 μM)"
    elif unique_potent >= 10:
        tractability = "MODERATE — meaningful chemical matter (10-49 compounds < 1 μM)"
    elif unique_potent >= 1:
        tractability = "LOW — limited chemical matter (1-9 compounds < 1 μM)"
    else:
        tractability = "INTRACTABLE — no compounds below threshold"

    return {
        "target_chembl_id": target_chembl_id,
        "total_activity_records": len(df),
        "unique_compounds_total": unique_total,
        "compounds_sub_10nM": sub_10nm,
        "compounds_sub_100nM": sub_100nm,
        "compounds_sub_1uM": sub_1um,
        "most_potent_nM": round(df["standard_value_nM"].min(), 2),
        "median_potency_nM": round(df["standard_value_nM"].median(), 2),
        "tractability": tractability,
    }


# Example: EGFR
result = count_chembl_ligands("CHEMBL203", activity_threshold_nm=1000)
for k, v in result.items():
    print(f"  {k}: {v}")
```

**Key Parameters:**
- `target_chembl_id`: ChEMBL target identifier (obtain from `mcp__chembl__chembl_info(method: "target_search")`)
- `activity_threshold_nm`: Potency cutoff in nM (1000 nM = 1 uM is standard for "active")

**Expected Output:**
- Counts of unique compounds at different potency tiers (<10 nM, <100 nM, <1 uM)
- Overall tractability assessment (HIGH / MODERATE / LOW / INTRACTABLE)

---

## Recipe 3: PDB Structure Availability Check

Assess structural druggability by checking for high-resolution experimental structures with bound ligands.

```python
import requests
import pandas as pd

def check_pdb_structures(uniprot_id, resolution_cutoff=3.0):
    """
    Check PDB for experimental structures of a target protein.

    Parameters
    ----------
    uniprot_id : str
        UniProt accession (e.g., "P00533" for EGFR)
    resolution_cutoff : float
        Maximum resolution in Angstroms (default: 3.0 Å)

    Returns
    -------
    dict with structure counts, ligand-bound structures, and structural druggability assessment
    """
    # Query RCSB PDB for structures mapped to this UniProt ID
    search_url = "https://search.rcsb.org/rcsbsearch/v2/query"
    query = {
        "query": {
            "type": "group",
            "logical_operator": "and",
            "nodes": [
                {
                    "type": "terminal",
                    "service": "text",
                    "parameters": {
                        "attribute": "rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_accession",
                        "operator": "exact_match",
                        "value": uniprot_id,
                    },
                },
                {
                    "type": "terminal",
                    "service": "text",
                    "parameters": {
                        "attribute": "rcsb_entry_info.resolution_combined",
                        "operator": "less_or_equal",
                        "value": resolution_cutoff,
                    },
                },
            ],
        },
        "return_type": "entry",
        "request_options": {"return_all_hits": True},
    }

    resp = requests.post(search_url, json=query)
    results = resp.json()

    pdb_ids = [hit["identifier"] for hit in results.get("result_set", [])]
    total_structures = len(pdb_ids)

    # Check for ligand-bound structures (check first 20)
    ligand_bound = 0
    best_resolution = None
    for pdb_id in pdb_ids[:20]:
        info_url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"
        info_resp = requests.get(info_url)
        if info_resp.ok:
            info = info_resp.json()
            resolution = info.get("rcsb_entry_info", {}).get("resolution_combined", [None])
            if resolution and (best_resolution is None or resolution[0] < best_resolution):
                best_resolution = resolution[0]

            # Check for non-solvent ligands
            nonpoly = info.get("rcsb_entry_info", {}).get("nonpolymer_entity_count", 0)
            if nonpoly and nonpoly > 0:
                ligand_bound += 1

    # Structural druggability assessment
    if total_structures >= 10 and ligand_bound >= 5 and best_resolution and best_resolution <= 2.5:
        structural_score = 1.0
        assessment = "EXCELLENT — many high-res ligand-bound structures available"
    elif total_structures >= 5 and ligand_bound >= 2:
        structural_score = 0.75
        assessment = "GOOD — multiple structures with ligands; structure-based design feasible"
    elif total_structures >= 1:
        structural_score = 0.50
        assessment = "MODERATE — structures exist but limited ligand-bound data"
    else:
        structural_score = 0.25
        assessment = "POOR — no experimental structures; rely on AlphaFold prediction"

    return {
        "uniprot_id": uniprot_id,
        "total_structures": total_structures,
        "ligand_bound_structures_checked": ligand_bound,
        "best_resolution_A": best_resolution,
        "resolution_cutoff_A": resolution_cutoff,
        "structural_druggability_score": structural_score,
        "assessment": assessment,
    }


# Example: EGFR
result = check_pdb_structures("P00533", resolution_cutoff=3.0)
for k, v in result.items():
    print(f"  {k}: {v}")
```

**Key Parameters:**
- `uniprot_id`: UniProt accession (obtain from `mcp__uniprot__uniprot_data(method: "search_by_gene")`)
- `resolution_cutoff`: Maximum acceptable resolution in Angstroms (3.0 Å is standard; <2.5 Å preferred for SBDD)

**Expected Output:**
- Total structure count, ligand-bound structure count, best resolution, structural druggability score (0-1)

---

## Recipe 4: Surface Pocket Detection (fpocket)

Run fpocket on a PDB structure to detect druggable binding pockets and score their druggability.

```python
import subprocess
import os
import re

def run_fpocket(pdb_file, min_druggability_score=0.5):
    """
    Detect surface pockets using fpocket and assess druggability.

    Parameters
    ----------
    pdb_file : str
        Path to PDB file
    min_druggability_score : float
        Minimum druggability score to report (0-1, default 0.5)

    Returns
    -------
    list of dicts with pocket properties and druggability scores
    """
    # Run fpocket
    subprocess.run(["fpocket", "-f", pdb_file], check=True, capture_output=True)

    # Parse output directory
    base = os.path.splitext(os.path.basename(pdb_file))[0]
    output_dir = f"{base}_out"
    info_file = os.path.join(output_dir, f"{base}_info.txt")

    if not os.path.exists(info_file):
        raise FileNotFoundError(f"fpocket output not found: {info_file}")

    # Parse pocket information
    pockets = []
    current_pocket = {}

    with open(info_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith("Pocket"):
                if current_pocket:
                    pockets.append(current_pocket)
                pocket_num = int(re.search(r"Pocket\s+(\d+)", line).group(1))
                current_pocket = {"pocket_id": pocket_num}
            elif "Score" in line and ":" in line:
                key, val = line.split(":", 1)
                key = key.strip().lower().replace(" ", "_")
                try:
                    current_pocket[key] = float(val.strip())
                except ValueError:
                    current_pocket[key] = val.strip()
            elif "Volume" in line and ":" in line:
                key, val = line.split(":", 1)
                current_pocket["volume_A3"] = float(val.strip())
            elif "Druggability" in line and ":" in line:
                key, val = line.split(":", 1)
                current_pocket["druggability_score"] = float(val.strip())

    if current_pocket:
        pockets.append(current_pocket)

    # Filter by druggability score
    druggable = [p for p in pockets if p.get("druggability_score", 0) >= min_druggability_score]

    # Assess overall druggability
    if druggable:
        best = max(druggable, key=lambda p: p.get("druggability_score", 0))
        print(f"\nFound {len(druggable)} druggable pocket(s) (score >= {min_druggability_score})")
        print(f"Best pocket: #{best['pocket_id']} (druggability={best.get('druggability_score', 'N/A')})")
        for p in druggable:
            print(f"  Pocket {p['pocket_id']}: "
                  f"druggability={p.get('druggability_score', 'N/A'):.2f}, "
                  f"volume={p.get('volume_A3', 'N/A'):.0f} Å³")
    else:
        print(f"No pockets with druggability score >= {min_druggability_score}")

    return druggable


# Example usage (requires fpocket installed and PDB file)
# pockets = run_fpocket("6VXX.pdb", min_druggability_score=0.5)
```

**Key Parameters:**
- `pdb_file`: Path to PDB structure file (download from RCSB or use AlphaFold model)
- `min_druggability_score`: fpocket druggability threshold (>0.5 = druggable, >0.8 = highly druggable)

**Expected Output:**
- List of detected pockets with volume (Å3) and druggability score (0-1)
- Best pocket highlighted for structure-based drug design

---

## Recipe 5: GTEx Expression Specificity (Tau Index)

Calculate tissue specificity using the tau index from GTEx median expression data. High tau = tissue-selective expression = better therapeutic window.

```python
import numpy as np
import pandas as pd

def calculate_tau_index(expression_by_tissue):
    """
    Calculate the tau tissue specificity index from GTEx expression data.

    Tau = sum(1 - x_i/x_max) / (n - 1)
    Where x_i = expression in tissue i, x_max = max expression, n = number of tissues.

    Parameters
    ----------
    expression_by_tissue : dict
        {tissue_name: median_TPM} from GTEx

    Returns
    -------
    dict with tau index, max-expressing tissue, and specificity classification
    """
    tissues = list(expression_by_tissue.keys())
    values = np.array([expression_by_tissue[t] for t in tissues], dtype=float)

    # Replace zeros and log-transform (log2(TPM + 1))
    log_values = np.log2(values + 1)
    x_max = log_values.max()

    if x_max == 0:
        return {
            "tau": 0.0,
            "max_tissue": "N/A",
            "max_tpm": 0.0,
            "specificity": "NOT EXPRESSED",
        }

    n = len(log_values)
    tau = np.sum(1 - log_values / x_max) / (n - 1)

    # Find max-expressing tissue
    max_idx = np.argmax(log_values)
    max_tissue = tissues[max_idx]
    max_tpm = values[max_idx]

    # Top 3 expressing tissues
    sorted_idx = np.argsort(-values)
    top_tissues = [(tissues[i], round(values[i], 2)) for i in sorted_idx[:3]]

    # Classification
    if tau >= 0.85:
        specificity = "HIGHLY SPECIFIC — expressed in very few tissues (tau >= 0.85)"
    elif tau >= 0.6:
        specificity = "MODERATELY SPECIFIC — enriched in select tissues (tau 0.6-0.85)"
    elif tau >= 0.3:
        specificity = "BROADLY EXPRESSED — most tissues express this gene (tau 0.3-0.6)"
    else:
        specificity = "HOUSEKEEPING — ubiquitously expressed (tau < 0.3)"

    return {
        "tau": round(tau, 4),
        "n_tissues": n,
        "max_tissue": max_tissue,
        "max_tpm": round(max_tpm, 2),
        "top_3_tissues": top_tissues,
        "specificity": specificity,
        "therapeutic_window": "FAVORABLE" if tau >= 0.6 else "NARROW" if tau >= 0.3 else "POOR — ubiquitous expression, systemic toxicity risk",
    }


# Example usage with GTEx data (obtained from mcp__gtex__gtex_data)
example_expression = {
    "Brain - Cortex": 85.3,
    "Brain - Cerebellum": 92.1,
    "Brain - Hippocampus": 78.5,
    "Liver": 2.1,
    "Kidney - Cortex": 1.8,
    "Heart - Left Ventricle": 3.2,
    "Lung": 5.6,
    "Muscle - Skeletal": 1.2,
    "Skin - Sun Exposed": 0.8,
    "Whole Blood": 0.3,
    "Adipose - Subcutaneous": 1.5,
    "Colon - Sigmoid": 2.0,
}

result = calculate_tau_index(example_expression)
print(f"Tau index: {result['tau']}")
print(f"Specificity: {result['specificity']}")
print(f"Max tissue: {result['max_tissue']} ({result['max_tpm']} TPM)")
print(f"Therapeutic window: {result['therapeutic_window']}")
```

**Key Parameters:**
- `expression_by_tissue`: dict mapping tissue names to median TPM values from GTEx
- Tau ranges from 0 (ubiquitous) to 1 (perfectly specific to one tissue)
- Tau > 0.8 is considered highly tissue-specific

**Expected Output:**
- Tau index (0-1), max-expressing tissue, specificity classification, therapeutic window assessment

---

## Recipe 6: Co-Essentiality Network from DepMap

Identify co-essential genes using Pearson correlation of CRISPR dependency scores across cell lines. Co-essential genes are often in the same pathway or complex.

```python
import pandas as pd
import numpy as np
from scipy import stats

def compute_coessentiality(depmap_df, query_gene, min_cell_lines=50, correlation_threshold=0.3, top_n=20):
    """
    Compute co-essentiality network for a gene using DepMap CRISPR scores.

    Parameters
    ----------
    depmap_df : DataFrame
        DepMap CRISPR dependency scores. Rows = cell lines, columns = genes.
        Values = log fold-change (negative = essential).
    query_gene : str
        Gene symbol to find co-essential partners for
    min_cell_lines : int
        Minimum shared cell lines for correlation (default: 50)
    correlation_threshold : float
        Minimum |Pearson r| to report (default: 0.3)
    top_n : int
        Number of top co-essential genes to return (default: 20)

    Returns
    -------
    DataFrame with co-essential genes sorted by absolute correlation
    """
    if query_gene not in depmap_df.columns:
        raise ValueError(f"Gene '{query_gene}' not found in DepMap data")

    query_scores = depmap_df[query_gene].dropna()

    results = []
    for gene in depmap_df.columns:
        if gene == query_gene:
            continue

        gene_scores = depmap_df[gene].dropna()

        # Find shared cell lines
        shared = query_scores.index.intersection(gene_scores.index)
        if len(shared) < min_cell_lines:
            continue

        # Pearson correlation
        r, p_value = stats.pearsonr(query_scores[shared], gene_scores[shared])

        if abs(r) >= correlation_threshold:
            results.append({
                "gene": gene,
                "pearson_r": round(r, 4),
                "p_value": p_value,
                "n_cell_lines": len(shared),
                "abs_r": abs(r),
            })

    results_df = (pd.DataFrame(results)
                  .sort_values("abs_r", ascending=False)
                  .head(top_n)
                  .drop(columns=["abs_r"])
                  .reset_index(drop=True))

    # Add BH-FDR correction
    if len(results_df) > 0:
        from statsmodels.stats.multitest import multipletests
        _, fdr, _, _ = multipletests(results_df["p_value"], method="fdr_bh")
        results_df["fdr_q_value"] = fdr

    # Classify co-essential relationships
    results_df["relationship"] = results_df["pearson_r"].apply(
        lambda r: "SAME COMPLEX/PATHWAY" if r > 0.5
        else "CO-ESSENTIAL" if r > 0.3
        else "ANTI-CORRELATED (synthetic lethal candidate)" if r < -0.3
        else "WEAK"
    )

    print(f"\nCo-essentiality network for {query_gene}")
    print(f"Tested genes with >= {min_cell_lines} shared cell lines")
    print(f"Found {len(results_df)} genes with |r| >= {correlation_threshold}")
    print(results_df.to_string(index=False))

    return results_df


# Example usage (requires DepMap data download from depmap.org)
# depmap = pd.read_csv("CRISPRGeneEffect.csv", index_col=0)
# coessential = compute_coessentiality(depmap, "BRAF", min_cell_lines=50)
```

**Key Parameters:**
- `depmap_df`: DepMap CRISPR dependency scores (download from depmap.org/portal)
- `min_cell_lines`: Minimum overlapping cell lines for reliable correlation (50 recommended)
- `correlation_threshold`: |r| > 0.3 for co-essentiality, r < -0.3 for synthetic lethality candidates

**Expected Output:**
- Ranked list of co-essential genes with Pearson correlation, p-value, FDR, and relationship type

---

## Recipe 7: Open Targets Disease Association Scoring

Query and parse Open Targets association scores by evidence type for a target-disease pair.

```python
import requests
import pandas as pd

def get_opentargets_association(target_ensembl_id, disease_efo_id):
    """
    Get detailed Open Targets association scores for a target-disease pair.

    Parameters
    ----------
    target_ensembl_id : str
        Ensembl gene ID (e.g., "ENSG00000157764" for BRAF)
    disease_efo_id : str
        EFO disease ID (e.g., "EFO_0000616" for melanoma)

    Returns
    -------
    dict with overall score and evidence type breakdown
    """
    # GraphQL query for association scores
    graphql_url = "https://api.platform.opentargets.org/api/v4/graphql"
    query = """
    query associationScore($ensemblId: String!, $efoId: String!) {
      target(ensemblId: $ensemblId) {
        id
        approvedSymbol
        approvedName
      }
      disease(efoId: $efoId) {
        id
        name
      }
      associationByDatasourceDirect(
        ensemblId: $ensemblId,
        efoId: $efoId
      ) {
        datasourceId
        score
      }
    }
    """

    variables = {"ensemblId": target_ensembl_id, "efoId": disease_efo_id}
    resp = requests.post(graphql_url, json={"query": query, "variables": variables})
    data = resp.json().get("data", {})

    target_info = data.get("target", {})
    disease_info = data.get("disease", {})
    associations = data.get("associationByDatasourceDirect", [])

    # Map datasource IDs to evidence categories
    CATEGORY_MAP = {
        "ot_genetics_portal": "Genetic association",
        "gene_burden": "Genetic association (rare)",
        "genomics_england": "Genomics England PanelApp",
        "eva": "ClinVar genetic evidence",
        "chembl": "Drugs (ChEMBL)",
        "europepmc": "Literature mining",
        "expression_atlas": "Expression evidence",
        "impc": "Animal models (IMPC)",
        "intogen": "Somatic mutations (IntOGen)",
        "cancer_gene_census": "Cancer Gene Census",
        "reactome": "Pathway evidence (Reactome)",
        "progeny": "Pathway signatures",
        "slapenrich": "Pathway SLAPenrich",
        "crispr": "CRISPR screen evidence",
    }

    evidence_scores = {}
    for assoc in associations:
        ds = assoc.get("datasourceId", "unknown")
        score = assoc.get("score", 0)
        category = CATEGORY_MAP.get(ds, ds)
        evidence_scores[category] = round(score, 4)

    # Overall association strength
    if evidence_scores:
        overall = max(evidence_scores.values())
        genetic = max(
            evidence_scores.get("Genetic association", 0),
            evidence_scores.get("Genetic association (rare)", 0),
            evidence_scores.get("ClinVar genetic evidence", 0),
        )
    else:
        overall = 0.0
        genetic = 0.0

    # Validation strength
    if genetic > 0.5 and evidence_scores.get("Drugs (ChEMBL)", 0) > 0:
        validation = "STRONG — genetic evidence + existing drugs"
    elif genetic > 0.3:
        validation = "MODERATE — genetic evidence supports target"
    elif evidence_scores.get("Drugs (ChEMBL)", 0) > 0:
        validation = "MODERATE — drug evidence but limited genetics"
    elif overall > 0:
        validation = "WEAK — indirect evidence only"
    else:
        validation = "NONE — no Open Targets evidence"

    result = {
        "target": target_info.get("approvedSymbol", target_ensembl_id),
        "target_name": target_info.get("approvedName", ""),
        "disease": disease_info.get("name", disease_efo_id),
        "overall_max_score": overall,
        "genetic_evidence_score": genetic,
        "validation_strength": validation,
        "evidence_by_source": evidence_scores,
    }

    print(f"\n{result['target']} — {result['disease']}")
    print(f"Overall score: {result['overall_max_score']}")
    print(f"Genetic evidence: {result['genetic_evidence_score']}")
    print(f"Validation: {result['validation_strength']}")
    print(f"\nEvidence breakdown:")
    for source, score in sorted(evidence_scores.items(), key=lambda x: -x[1]):
        bar = "█" * int(score * 20)
        print(f"  {source:40s} {score:.3f} {bar}")

    return result


# Example: BRAF in melanoma
# result = get_opentargets_association("ENSG00000157764", "EFO_0000616")
```

**Key Parameters:**
- `target_ensembl_id`: Ensembl gene ID (obtain from `mcp__opentargets__opentargets_info(method: "search_targets")`)
- `disease_efo_id`: EFO disease ID (obtain from `mcp__opentargets__opentargets_info(method: "search_diseases")`)

**Expected Output:**
- Overall association score, genetic evidence score, evidence breakdown by source, validation strength assessment

---

## Recipe 8: Composite Druggability Score

Weighted combination of structural, chemical, genetic, expression, and safety evidence into a single druggability score.

```python
import pandas as pd

def compute_composite_druggability(
    structure_score,
    ligand_score,
    genetic_score,
    expression_score,
    safety_score,
    weights=None,
):
    """
    Compute a weighted composite druggability score.

    Parameters
    ----------
    structure_score : float
        Structural druggability (0-1): PDB availability, pocket druggability
    ligand_score : float
        Chemical tractability (0-1): ChEMBL ligand count, best potency
    genetic_score : float
        Genetic validation (0-1): GWAS, Mendelian, somatic mutations
    expression_score : float
        Expression profile (0-1): tissue specificity (tau index), disease relevance
    safety_score : float
        Safety profile (0-1): essentiality, off-target liability, known toxicity
    weights : dict, optional
        Custom weights (default: structure 25%, ligands 25%, genetics 20%, expression 15%, safety 15%)

    Returns
    -------
    dict with composite score, component contributions, and druggability tier
    """
    if weights is None:
        weights = {
            "structure": 0.25,
            "ligands": 0.25,
            "genetics": 0.20,
            "expression": 0.15,
            "safety": 0.15,
        }

    # Validate weights sum to 1
    w_sum = sum(weights.values())
    if abs(w_sum - 1.0) > 0.01:
        raise ValueError(f"Weights must sum to 1.0, got {w_sum}")

    scores = {
        "structure": structure_score,
        "ligands": ligand_score,
        "genetics": genetic_score,
        "expression": expression_score,
        "safety": safety_score,
    }

    # Weighted composite
    composite = sum(scores[k] * weights[k] for k in weights)

    # Component contributions
    contributions = {k: round(scores[k] * weights[k], 4) for k in weights}

    # Identify weakest component (risk factor)
    weakest = min(scores, key=scores.get)
    weakest_score = scores[weakest]

    # Tier assignment
    if composite >= 0.75:
        tier = "TIER 1 — Highly Druggable"
        recommendation = "Proceed with hit-finding campaign; strong evidence across all dimensions"
    elif composite >= 0.55:
        tier = "TIER 2 — Moderately Druggable"
        recommendation = f"Feasible but address weakest dimension ({weakest}: {weakest_score:.2f})"
    elif composite >= 0.35:
        tier = "TIER 3 — Challenging"
        recommendation = f"Consider alternative modalities (PROTAC, antibody, gene therapy); key gap: {weakest}"
    else:
        tier = "TIER 4 — Currently Undruggable"
        recommendation = "Targeted protein degradation or genetic medicine may be required; conventional approaches unlikely to succeed"

    result = {
        "composite_score": round(composite, 4),
        "tier": tier,
        "recommendation": recommendation,
        "component_scores": scores,
        "component_contributions": contributions,
        "weakest_dimension": weakest,
        "weakest_score": weakest_score,
    }

    print(f"\nComposite Druggability Score: {composite:.3f}")
    print(f"Tier: {tier}")
    print(f"\nComponent Breakdown:")
    for k in weights:
        bar = "█" * int(scores[k] * 20)
        print(f"  {k:12s}: {scores[k]:.2f} (weight {weights[k]:.0%}) → contribution {contributions[k]:.3f}  {bar}")
    print(f"\nWeakest: {weakest} ({weakest_score:.2f})")
    print(f"Recommendation: {recommendation}")

    return result


# Example: BRAF in melanoma
result = compute_composite_druggability(
    structure_score=0.95,   # Many co-crystal structures, druggable pocket
    ligand_score=0.90,      # >100 ChEMBL compounds with IC50 < 1 μM
    genetic_score=0.85,     # V600E driver mutation, strong GWAS evidence
    expression_score=0.60,  # Broadly expressed (tau ~0.4)
    safety_score=0.70,      # Paradoxical activation risk, skin toxicity
)
```

**Key Parameters:**
- Each component scored 0-1 using dedicated recipes (structure, ligand count, genetics, expression, safety)
- Default weights: structure 25%, ligands 25%, genetics 20%, expression 15%, safety 15%
- Weights are adjustable per therapeutic area (e.g., increase genetics weight for genetically validated oncology targets)

**Expected Output:**
- Composite score (0-1), druggability tier (1-4), component breakdown, weakest dimension, actionable recommendation

---

## Recipe 9: Anti-Target Safety Check

Screen a target against known anti-target lists: essential genes, tumor suppressors, hematopoietic transcription factors, and teratogenic substrates.

```python
import pandas as pd

# Curated anti-target lists (expand as needed)
ESSENTIAL_GENES = {
    # Core essential genes from DepMap (Hart et al., 2017)
    "RPL5", "RPL11", "RPS14", "RPS19", "EIF3A", "EIF4A1",
    "POLR2A", "POLR2B", "PCNA", "MCM2", "MCM4", "MCM7",
    "PSMA1", "PSMB1", "PSMB5", "PSMD1", "PSMD14",
    "UBA1", "UBE2D3", "UBE2I",
    "SF3B1", "SRSF1", "U2AF1", "U2AF2",
    "CDK1", "CDK7", "CDK9", "CCNB1",
}

TUMOR_SUPPRESSORS = {
    # Key tumor suppressors — degrading these would promote cancer
    "TP53", "RB1", "PTEN", "APC", "BRCA1", "BRCA2",
    "VHL", "NF1", "NF2", "SMAD4", "WT1",
    "CDKN2A", "CDKN1A", "CDKN1B",
    "STK11", "KEAP1", "BAP1", "ARID1A",
}

HEMATOPOIETIC_TFS = {
    # Transcription factors critical for hematopoiesis
    "GATA1", "GATA2", "RUNX1", "TAL1", "FLI1",
    "SPI1", "CEBPA", "CEBPB", "MYB", "GFI1", "GFI1B",
    "KLF1", "LMO2", "ERG", "ETV6", "MECOM",
    "IKZF1", "IKZF3", "PAX5", "EBF1", "TCF3",
}

TERATOGENIC_SUBSTRATES = {
    # Known CRBN neosubstrates with teratogenicity risk
    "SALL4": "Limb development — thalidomide teratogenicity target",
    "SALL1": "Townes-Brocks syndrome — renal/limb/ear development",
    "SALL3": "Related SALL family — developmental role",
    "p63": "Ectodermal development — limb and craniofacial",
    "TP63": "Same as p63 — HUGO symbol",
}


def check_anti_target(gene_symbol):
    """
    Screen a gene against anti-target safety lists.

    Parameters
    ----------
    gene_symbol : str
        Gene symbol (e.g., "BRAF", "TP53")

    Returns
    -------
    dict with safety flags, risk level, and recommendations
    """
    flags = []
    risk_level = "LOW"

    gene = gene_symbol.upper()

    if gene in ESSENTIAL_GENES:
        flags.append({
            "category": "CORE ESSENTIAL",
            "severity": "CRITICAL",
            "detail": f"{gene} is a core essential gene (DepMap common essential). Systemic inhibition/degradation will cause toxicity in all dividing cells.",
        })
        risk_level = "CRITICAL"

    if gene in TUMOR_SUPPRESSORS:
        flags.append({
            "category": "TUMOR SUPPRESSOR",
            "severity": "CRITICAL",
            "detail": f"{gene} is a tumor suppressor. Inhibition or degradation may promote tumorigenesis. CANNOT be a therapeutic target for inhibition/degradation.",
        })
        risk_level = "CRITICAL"

    if gene in HEMATOPOIETIC_TFS:
        flags.append({
            "category": "HEMATOPOIETIC TF",
            "severity": "HIGH",
            "detail": f"{gene} is critical for hematopoiesis. Degradation may cause cytopenias (neutropenia, anemia, thrombocytopenia). Requires careful dose optimization and blood count monitoring.",
        })
        if risk_level != "CRITICAL":
            risk_level = "HIGH"

    if gene in TERATOGENIC_SUBSTRATES:
        flags.append({
            "category": "TERATOGENIC SUBSTRATE",
            "severity": "HIGH",
            "detail": f"{gene} — {TERATOGENIC_SUBSTRATES[gene]}. Any degrader hitting this target requires pregnancy prevention program (cf. lenalidomide REMS).",
        })
        if risk_level != "CRITICAL":
            risk_level = "HIGH"

    # Recommendation
    if risk_level == "CRITICAL":
        recommendation = "DO NOT PURSUE — target is an anti-target. Inhibition/degradation will cause unacceptable toxicity or tumorigenesis."
    elif risk_level == "HIGH":
        recommendation = "PROCEED WITH EXTREME CAUTION — significant safety risks require robust mitigation strategy, tissue-selective delivery, or restrictive patient selection."
    else:
        recommendation = "No anti-target flags detected. Proceed with standard safety assessment."

    result = {
        "gene": gene,
        "risk_level": risk_level,
        "n_flags": len(flags),
        "flags": flags,
        "recommendation": recommendation,
    }

    print(f"\nAnti-Target Check: {gene}")
    print(f"Risk Level: {risk_level}")
    if flags:
        for f in flags:
            print(f"  [{f['severity']}] {f['category']}: {f['detail']}")
    else:
        print("  No anti-target flags detected.")
    print(f"Recommendation: {recommendation}")

    return result


# Example
check_anti_target("TP53")    # CRITICAL — tumor suppressor
check_anti_target("IKZF1")   # HIGH — hematopoietic TF
check_anti_target("BRAF")    # LOW — not an anti-target
check_anti_target("SALL4")   # HIGH — teratogenic substrate
```

**Key Parameters:**
- `gene_symbol`: Gene to screen (case-insensitive)
- Anti-target lists are curated from DepMap essential genes (Hart et al.), COSMIC Cancer Gene Census (tumor suppressors), and literature-curated hematopoietic TFs

**Expected Output:**
- Risk level (CRITICAL / HIGH / LOW), specific safety flags with severity and detail, actionable recommendation

---

## Recipe 10: Target Tractability Assessment

Assess whether a target is best approached by small molecule, antibody, PROTAC, or gene therapy based on protein properties.

```python
import pandas as pd

def assess_tractability(
    gene_symbol,
    protein_class,
    subcellular_location,
    has_binding_pocket,
    has_extracellular_domain,
    has_known_ligands,
    n_chembl_compounds,
    has_pdb_structure,
    is_enzyme,
    is_zinc_finger=False,
    is_disordered=False,
    is_resistance_target=False,
):
    """
    Assess target tractability across multiple therapeutic modalities.

    Parameters
    ----------
    gene_symbol : str
        Gene symbol
    protein_class : str
        Protein family (kinase, GPCR, TF, etc.)
    subcellular_location : str
        Primary location (membrane, cytoplasm, nucleus, extracellular)
    has_binding_pocket : bool
        Whether a druggable pocket exists (from fpocket or PDB)
    has_extracellular_domain : bool
        Whether protein has extracellular/surface-accessible domain
    has_known_ligands : bool
        Whether ChEMBL/BindingDB has known binders
    n_chembl_compounds : int
        Number of bioactive compounds in ChEMBL
    has_pdb_structure : bool
        Whether experimental structure exists
    is_enzyme : bool
        Whether protein has catalytic activity
    is_zinc_finger : bool
        Whether protein contains zinc finger domains (CRBN glue susceptibility)
    is_disordered : bool
        Whether protein is intrinsically disordered (>30% IUPred > 0.5)
    is_resistance_target : bool
        Whether target has known resistance mutations to conventional drugs

    Returns
    -------
    dict with modality scores and recommendation
    """
    modalities = {}

    # Small molecule score
    sm_score = 0.0
    if has_binding_pocket:
        sm_score += 0.35
    if is_enzyme:
        sm_score += 0.25
    if has_known_ligands:
        sm_score += 0.20
    if has_pdb_structure:
        sm_score += 0.10
    if n_chembl_compounds >= 10:
        sm_score += 0.10
    if is_resistance_target:
        sm_score -= 0.20  # Resistance reduces small molecule viability
    modalities["Small molecule"] = min(max(sm_score, 0), 1.0)

    # Antibody score
    ab_score = 0.0
    if has_extracellular_domain:
        ab_score += 0.50
    if subcellular_location in ("membrane", "extracellular", "cell surface"):
        ab_score += 0.30
    if not is_enzyme:  # Antibodies often block PPI, not catalysis
        ab_score += 0.10
    if has_pdb_structure:
        ab_score += 0.10
    modalities["Antibody/biologic"] = min(max(ab_score, 0), 1.0)

    # PROTAC/TPD score
    tpd_score = 0.0
    if has_known_ligands or has_binding_pocket:
        tpd_score += 0.25  # Need warhead binding site
    if is_zinc_finger:
        tpd_score += 0.30  # CRBN molecular glue candidate
    if is_disordered:
        tpd_score += 0.15  # Easier proteasomal degradation
    if is_resistance_target:
        tpd_score += 0.25  # TPD overcomes active site mutations
    if not is_enzyme and not has_binding_pocket:
        tpd_score += 0.20  # Undruggable by conventional means → TPD opportunity
    if subcellular_location not in ("extracellular",):
        tpd_score += 0.10  # Intracellular targets amenable to degradation
    modalities["PROTAC/degrader"] = min(max(tpd_score, 0), 1.0)

    # Gene therapy/ASO score
    gt_score = 0.0
    if not has_binding_pocket and not has_known_ligands:
        gt_score += 0.30  # No chemical matter → genetic approach
    if is_disordered:
        gt_score += 0.15  # No structure for drug design
    if not has_extracellular_domain:
        gt_score += 0.10
    if protein_class.lower() in ("structural protein", "scaffolding protein"):
        gt_score += 0.20  # Best addressed genetically
    modalities["Gene therapy/ASO"] = min(max(gt_score, 0), 1.0)

    # Best modality
    best = max(modalities, key=modalities.get)
    best_score = modalities[best]

    result = {
        "gene": gene_symbol,
        "protein_class": protein_class,
        "modality_scores": {k: round(v, 2) for k, v in modalities.items()},
        "recommended_modality": best,
        "recommended_score": round(best_score, 2),
        "all_viable": [k for k, v in modalities.items() if v >= 0.4],
    }

    print(f"\nTractability Assessment: {gene_symbol} ({protein_class})")
    for mod, score in sorted(modalities.items(), key=lambda x: -x[1]):
        bar = "█" * int(score * 20)
        marker = " ← RECOMMENDED" if mod == best else ""
        print(f"  {mod:20s}: {score:.2f} {bar}{marker}")
    print(f"\nViable modalities (score >= 0.4): {', '.join(result['all_viable']) or 'None'}")

    return result


# Example: IKZF1 (zinc finger transcription factor)
result = assess_tractability(
    gene_symbol="IKZF1",
    protein_class="Transcription factor",
    subcellular_location="nucleus",
    has_binding_pocket=False,
    has_extracellular_domain=False,
    has_known_ligands=False,
    n_chembl_compounds=0,
    has_pdb_structure=True,
    is_enzyme=False,
    is_zinc_finger=True,
    is_disordered=True,
    is_resistance_target=False,
)
```

**Key Parameters:**
- Protein properties from UniProt, PDB, ChEMBL, and AlphaFold
- Scores each modality (small molecule, antibody, PROTAC/TPD, gene therapy) independently
- Recommends best modality and lists all viable options

**Expected Output:**
- Modality scores (0-1) for each therapeutic approach, recommended modality, list of all viable modalities

---

## Recipe 11: Competitive Landscape Assessment

Assess the competitive landscape for a drug target using ChEMBL clinical phase data and active program count.

```python
import requests
import pandas as pd

def assess_competitive_landscape(target_chembl_id, target_name):
    """
    Assess competitive landscape for a drug target.

    Parameters
    ----------
    target_chembl_id : str
        ChEMBL target ID
    target_name : str
        Human-readable target name for display

    Returns
    -------
    dict with competitive landscape metrics
    """
    # Query ChEMBL for drugs/clinical candidates targeting this protein
    url = "https://www.ebi.ac.uk/chembl/api/data/mechanism.json"
    params = {
        "target_chembl_id": target_chembl_id,
        "limit": 100,
    }
    resp = requests.get(url, params=params)
    mechanisms = resp.json().get("mechanisms", [])

    # Get molecule details for phase information
    molecules = {}
    for mech in mechanisms:
        mol_id = mech.get("molecule_chembl_id")
        if mol_id and mol_id not in molecules:
            mol_url = f"https://www.ebi.ac.uk/chembl/api/data/molecule/{mol_id}.json"
            mol_resp = requests.get(mol_url)
            if mol_resp.ok:
                mol_data = mol_resp.json()
                molecules[mol_id] = {
                    "chembl_id": mol_id,
                    "name": mol_data.get("pref_name", "Unknown"),
                    "max_phase": mol_data.get("max_phase", 0),
                    "molecule_type": mol_data.get("molecule_type", "Unknown"),
                    "mechanism": mech.get("mechanism_of_action", "Unknown"),
                }

    df = pd.DataFrame(molecules.values())

    if df.empty:
        return {
            "target": target_name,
            "target_chembl_id": target_chembl_id,
            "max_clinical_phase": 0,
            "approved_drugs": 0,
            "phase3_candidates": 0,
            "total_programs": 0,
            "competitive_pressure": "NONE — white space opportunity",
        }

    # Phase distribution
    approved = len(df[df["max_phase"] == 4])
    phase3 = len(df[df["max_phase"] == 3])
    phase2 = len(df[df["max_phase"] == 2])
    phase1 = len(df[df["max_phase"] == 1])
    preclinical = len(df[df["max_phase"] == 0])
    max_phase = int(df["max_phase"].max())

    # Competitive pressure assessment
    if approved >= 3:
        pressure = "VERY HIGH — crowded target, multiple approved drugs; differentiation required"
    elif approved >= 1:
        pressure = "HIGH — approved drugs exist; must demonstrate superiority or novel mechanism"
    elif phase3 >= 1:
        pressure = "MODERATE — late-stage competitors; timing and differentiation critical"
    elif phase2 >= 1:
        pressure = "LOW-MODERATE — early competitors; opportunity to be first-in-class"
    elif phase1 >= 1:
        pressure = "LOW — minimal competition; some validation from early clinical programs"
    else:
        pressure = "NONE — white space opportunity; but lack of competitors may signal target risk"

    # Freedom to operate
    if approved == 0 and phase3 == 0:
        fto = "FAVORABLE — no late-stage programs, likely freedom to operate"
    elif approved >= 1:
        fto = "RESTRICTED — existing drugs likely have method-of-treatment patents; check expiry dates"
    else:
        fto = "MODERATE — check competitor patent filings and composition of matter claims"

    result = {
        "target": target_name,
        "target_chembl_id": target_chembl_id,
        "max_clinical_phase": max_phase,
        "approved_drugs": approved,
        "phase3_candidates": phase3,
        "phase2_candidates": phase2,
        "phase1_candidates": phase1,
        "preclinical_programs": preclinical,
        "total_programs": len(df),
        "competitive_pressure": pressure,
        "freedom_to_operate": fto,
    }

    print(f"\nCompetitive Landscape: {target_name}")
    print(f"Total programs: {len(df)}")
    print(f"  Approved: {approved}")
    print(f"  Phase 3: {phase3}")
    print(f"  Phase 2: {phase2}")
    print(f"  Phase 1: {phase1}")
    print(f"  Preclinical: {preclinical}")
    print(f"Pressure: {pressure}")
    print(f"FTO: {fto}")

    if not df.empty:
        print(f"\nKey programs:")
        for _, row in df[df["max_phase"] >= 2].iterrows():
            print(f"  {row['name']} ({row['chembl_id']}) — Phase {row['max_phase']} — {row['mechanism']}")

    return result


# Example: EGFR
# result = assess_competitive_landscape("CHEMBL203", "EGFR")
```

**Key Parameters:**
- `target_chembl_id`: ChEMBL target ID (from `mcp__chembl__chembl_info(method: "target_search")`)
- Queries ChEMBL mechanism of action data and molecule phase information

**Expected Output:**
- Phase distribution (approved through preclinical), competitive pressure assessment, freedom-to-operate evaluation, key program details
