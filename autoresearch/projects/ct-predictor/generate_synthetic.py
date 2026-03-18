#!/usr/bin/env python3
"""
Generate a synthetic dataset for pipeline testing.

Creates realistic-looking trial data so that features.py, train.py, and
evaluate.py can be validated before real MCP data collection.

Usage: python generate_synthetic.py [--n-trials 300]
"""

import argparse
import csv
import json
import random
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).parent / "data"
random.seed(42)
np.random.seed(42)

# Real-ish indication areas and their base success rates
INDICATION_AREAS = {
    "oncology": 0.30,
    "cns": 0.15,
    "cardiovascular": 0.35,
    "metabolic": 0.40,
    "immunology": 0.35,
    "infectious": 0.45,
    "respiratory": 0.30,
    "rare": 0.25,
}

ENDPOINT_TYPES = ["OS", "PFS", "ORR", "DFS", "biomarker", "composite", "PRO"]
SPONSOR_TYPES = ["Industry", "NIH", "Other"]
INTERVENTION_TYPES = ["Drug", "Biological"]
ALLOCATIONS = ["Randomized", "Non-randomized"]
MASKINGS = ["None", "Single", "Double", "Triple", "Quadruple"]


def generate_trial(trial_id: int) -> dict:
    """Generate a single synthetic trial with correlated features."""

    indication = random.choice(list(INDICATION_AREAS.keys()))
    base_rate = INDICATION_AREAS[indication]
    phase = random.choice([2, 3])

    # Features that influence success probability
    ot_genetic_score = np.clip(np.random.beta(2, 5), 0, 1)
    has_biomarker_selection = int(random.random() < 0.3)
    fda_breakthrough = int(random.random() < 0.15)
    fda_fast_track = int(random.random() < 0.20)
    fda_orphan = int(random.random() < 0.10)
    chembl_selectivity = max(1, int(np.random.exponential(3)))
    enrollment = int(np.random.lognormal(5.5, 1.0))
    gwas_hit_count = max(0, int(np.random.exponential(2)))
    gnomad_pli = np.clip(np.random.beta(2, 3), 0, 1)

    # Success probability (correlated with features)
    logit = (
        np.log(base_rate / (1 - base_rate))  # base rate
        + 1.5 * ot_genetic_score              # strong genetic evidence helps
        + 0.8 * has_biomarker_selection       # biomarker selection helps
        + 0.6 * fda_breakthrough              # breakthrough helps
        + 0.3 * (phase - 2)                   # phase 3 slightly better (survived phase 2)
        - 0.2 * np.log1p(chembl_selectivity)  # more off-targets hurts
        + 0.3 * np.log1p(gwas_hit_count)      # more GWAS hits helps
        - 0.5 * gnomad_pli                    # essential genes harder to drug
        + np.random.normal(0, 0.5)            # noise
    )
    prob = 1 / (1 + np.exp(-logit))
    label = int(random.random() < prob)

    # Generate remaining features
    endpoint_type = random.choice(ENDPOINT_TYPES)
    sponsor_type = random.choices(SPONSOR_TYPES, weights=[0.7, 0.15, 0.15])[0]

    row = {
        "nct_id": f"NCT{10000000 + trial_id:08d}",
        "title": f"Phase {phase} Study of Compound-{trial_id} in {indication.title()}",
        "label": label,

        # ClinicalTrials.gov
        "phase": phase,
        "status": "Completed" if label else random.choice(["Terminated", "Completed", "Withdrawn"]),
        "enrollment": enrollment,
        "start_date": f"20{random.randint(10,23)}-{random.randint(1,12):02d}-01",
        "completion_date": f"20{random.randint(15,25)}-{random.randint(1,12):02d}-01",
        "study_type": "Interventional",
        "allocation": random.choice(ALLOCATIONS),
        "masking": random.choice(MASKINGS),
        "primary_purpose": "Treatment",
        "intervention_type": random.choice(INTERVENTION_TYPES),
        "intervention_name": f"Compound-{trial_id}",
        "condition": f"{indication}_condition_{random.randint(1,20)}",
        "indication_area": indication,
        "sponsor_type": sponsor_type,
        "lead_sponsor": f"Sponsor-{random.randint(1,50)}",
        "num_arms": random.choice([1, 2, 2, 2, 3]),
        "has_dmc": int(random.random() < 0.6),
        "endpoint_type": endpoint_type,
        "num_secondary_endpoints": random.randint(1, 8),
        "num_sites": int(np.random.lognormal(3, 1)),
        "has_biomarker_selection": has_biomarker_selection,
        "competitor_trial_count": int(np.random.exponential(10)),
        "prior_phase_success": int(random.random() < (0.7 if phase == 3 else 0.3)),

        # OpenTargets
        "ot_genetic_score": round(ot_genetic_score, 4),
        "ot_somatic_score": round(np.clip(np.random.beta(2, 8), 0, 1), 4),
        "ot_literature_score": round(np.clip(np.random.beta(3, 4), 0, 1), 4),
        "ot_animal_model_score": round(np.clip(np.random.beta(2, 5), 0, 1), 4),
        "ot_known_drug_score": round(np.clip(np.random.beta(2, 5), 0, 1), 4),
        "ot_affected_pathway_score": round(np.clip(np.random.beta(2, 5), 0, 1), 4),
        "ot_overall_score": round(np.clip(np.random.beta(3, 5), 0, 1), 4),
        "ot_target_tractability": random.randint(1, 10),

        # ChEMBL
        "chembl_selectivity": chembl_selectivity,
        "chembl_best_ic50_nm": round(np.random.lognormal(3, 2), 1),
        "chembl_num_assays": int(np.random.lognormal(3, 1)),
        "chembl_max_phase": random.choice([1, 2, 2, 3, 3, 4]),
        "chembl_moa_count": random.randint(1, 5),

        # DrugBank
        "drugbank_interaction_count": int(np.random.exponential(15)),
        "drugbank_target_count": max(1, int(np.random.exponential(3))),
        "drugbank_enzyme_count": random.randint(0, 8),
        "drugbank_transporter_count": random.randint(0, 5),
        "drugbank_half_life_hours": round(np.random.lognormal(2, 1), 1),
        "drugbank_molecular_weight": round(np.random.normal(450, 150), 1),

        # BindingDB
        "bindingdb_ki_nm": round(np.random.lognormal(3, 2), 1) if random.random() > 0.3 else "",
        "bindingdb_kd_nm": round(np.random.lognormal(3, 2), 1) if random.random() > 0.4 else "",
        "bindingdb_num_measurements": int(np.random.exponential(10)) if random.random() > 0.2 else "",

        # ClinPGx
        "clinpgx_guideline_count": random.choice([0, 0, 0, 1, 1, 2]),
        "clinpgx_actionable": int(random.random() < 0.25),
        "clinpgx_cyp_substrate_count": random.randint(0, 5),

        # FDA
        "fda_prior_approval_class": int(random.random() < 0.4),
        "fda_breakthrough": fda_breakthrough,
        "fda_fast_track": fda_fast_track,
        "fda_orphan": fda_orphan,
        "fda_class_ae_count": int(np.random.exponential(50)),

        # Publication signals
        "pubmed_target_pub_count": int(np.random.lognormal(4, 1.5)),
        "pubmed_drug_pub_count": int(np.random.lognormal(2, 1.5)),
        "openalex_citation_velocity": round(np.random.lognormal(2, 1), 1),
        "biorxiv_preprint_count": int(np.random.exponential(3)),

        # Healthcare spend
        "medicare_indication_spend": round(np.random.lognormal(6, 2), 0),
        "medicaid_indication_spend": round(np.random.lognormal(5, 2), 0),

        # Pathway/network
        "reactome_pathway_count": int(np.random.exponential(8)),
        "stringdb_interaction_degree": int(np.random.lognormal(3, 1)),
        "stringdb_betweenness": round(np.random.exponential(0.01), 6),

        # Genomic
        "gtex_tissue_specificity": round(np.clip(np.random.beta(2, 3), 0, 1), 4),
        "gtex_max_expression_tissue": random.choice(["liver", "brain", "lung", "kidney", "heart", "blood", "colon", "breast", "prostate"]),
        "gnomad_pli": round(gnomad_pli, 4),
        "gnomad_loeuf": round(np.clip(np.random.lognormal(-0.5, 0.8), 0, 3), 4),
        "clinvar_pathogenic_count": int(np.random.exponential(5)),
        "gwas_hit_count": gwas_hit_count,
        "gwas_best_pvalue": round(-np.random.exponential(3), 2) if gwas_hit_count > 0 else "",
        "depmap_essentiality": round(np.random.normal(-0.3, 0.3), 4),
        "cbioportal_mutation_freq": round(np.clip(np.random.exponential(0.05), 0, 1), 4),

        # Disease complexity
        "hpo_phenotype_count": int(np.random.exponential(15)),
        "monarch_gene_count": int(np.random.exponential(10)),

        # EMA
        "ema_approved_similar": int(random.random() < 0.3),
        "eu_filings_count": int(np.random.exponential(2)),
    }

    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-trials", type=int, default=300)
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Get columns from collect.py
    from collect import COLUMNS

    trials = [generate_trial(i) for i in range(args.n_trials)]

    output_path = DATA_DIR / "trials_raw.csv"
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for trial in trials:
            # Ensure all columns exist
            row = {col: trial.get(col, "") for col in COLUMNS}
            writer.writerow(row)

    # Stats
    labels = [t["label"] for t in trials]
    n_success = sum(labels)
    n_failure = len(labels) - n_success
    indications = {}
    for t in trials:
        area = t["indication_area"]
        indications[area] = indications.get(area, 0) + 1

    print(f"Generated {len(trials)} synthetic trials → {output_path}")
    print(f"  Success: {n_success} ({n_success/len(trials):.1%})")
    print(f"  Failure: {n_failure} ({n_failure/len(trials):.1%})")
    print(f"  Indication areas: {dict(sorted(indications.items()))}")


if __name__ == "__main__":
    main()
