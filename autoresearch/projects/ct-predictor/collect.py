#!/usr/bin/env python3
"""
Clinical Trial Data Collector

This script is designed to be run BY the NanoClaw agent inside a container,
where MCP tools are available. It issues structured queries and writes results
to data/trials_raw.csv.

Usage (from agent prompt or container):
  python collect.py --indication oncology --phases 2,3 --max-trials 500

The agent should run this once to build the dataset cache. The autoresearch
loop then operates on the cached CSV without needing MCP access.
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# This file is a TEMPLATE that the container agent fills in by calling MCPs.
# It can also be used as documentation of the data schema.
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_FILE = DATA_DIR / "trials_raw.csv"

# Column schema for the raw dataset
COLUMNS = [
    # === Trial identifiers ===
    "nct_id",                      # ClinicalTrials.gov NCT number
    "title",                       # Brief title
    "label",                       # 1=success (FDA approval), 0=failure

    # === ClinicalTrials.gov features ===
    "phase",                       # 2 or 3
    "status",                      # Completed, Terminated, Withdrawn, etc.
    "enrollment",                  # Number of participants
    "start_date",                  # Trial start date
    "completion_date",             # Primary completion date
    "study_type",                  # Interventional, Observational
    "allocation",                  # Randomized, Non-randomized
    "masking",                     # None, Single, Double, Triple, Quadruple
    "primary_purpose",             # Treatment, Prevention, Diagnostic, etc.
    "intervention_type",           # Drug, Biological, Device, etc.
    "intervention_name",           # Drug/biologic name
    "condition",                   # Primary condition studied
    "indication_area",             # Broad category (oncology, cns, metabolic, etc.)
    "sponsor_type",                # Industry, NIH, Other
    "lead_sponsor",                # Sponsor name
    "num_arms",                    # Number of study arms
    "has_dmc",                     # Data monitoring committee (1/0)
    "endpoint_type",               # OS, PFS, ORR, biomarker, composite, etc.
    "num_secondary_endpoints",     # Count of secondary endpoints
    "num_sites",                   # Number of study sites
    "has_biomarker_selection",     # Biomarker-selected population (1/0)
    "competitor_trial_count",      # Trials with same condition+intervention type
    "prior_phase_success",         # Had successful earlier phase (1/0)

    # === OpenTargets features ===
    "ot_genetic_score",            # Overall genetic association score (0-1)
    "ot_somatic_score",            # Somatic mutation evidence score
    "ot_literature_score",         # Literature mining score
    "ot_animal_model_score",       # Animal model evidence score
    "ot_known_drug_score",         # Known drug evidence for target-disease
    "ot_affected_pathway_score",   # Affected pathway evidence
    "ot_overall_score",            # Overall association score
    "ot_target_tractability",      # Tractability bucket (1-10, lower=more tractable)

    # === ChEMBL features ===
    "chembl_selectivity",          # Number of targets with IC50 < 100nM
    "chembl_best_ic50_nm",         # Best IC50 for primary target (nM)
    "chembl_num_assays",           # Total bioactivity assays for compound
    "chembl_max_phase",            # Max clinical phase in ChEMBL
    "chembl_moa_count",            # Number of known mechanisms of action

    # === DrugBank features ===
    "drugbank_interaction_count",  # Number of known drug interactions
    "drugbank_target_count",       # Number of known targets
    "drugbank_enzyme_count",       # Number of metabolizing enzymes
    "drugbank_transporter_count",  # Number of transporters
    "drugbank_half_life_hours",    # Reported half-life in hours
    "drugbank_molecular_weight",   # Molecular weight

    # === BindingDB features ===
    "bindingdb_ki_nm",             # Best Ki for primary target (nM)
    "bindingdb_kd_nm",             # Best Kd for primary target (nM)
    "bindingdb_num_measurements",  # Total binding measurements

    # === ClinPGx features ===
    "clinpgx_guideline_count",     # Number of CPIC guidelines for drug
    "clinpgx_actionable",          # Has actionable PGx (1/0)
    "clinpgx_cyp_substrate_count", # Number of CYP enzymes that metabolize it

    # === FDA features ===
    "fda_prior_approval_class",    # FDA already approved similar MOA (1/0)
    "fda_breakthrough",            # Breakthrough therapy designation (1/0)
    "fda_fast_track",              # Fast track designation (1/0)
    "fda_orphan",                  # Orphan drug designation (1/0)
    "fda_class_ae_count",          # Adverse events for drug class in FAERS

    # === PubMed + OpenAlex features ===
    "pubmed_target_pub_count",     # Publications about target in last 5 years
    "pubmed_drug_pub_count",       # Publications about compound in last 5 years
    "openalex_citation_velocity",  # Citations per year for key target papers
    "biorxiv_preprint_count",      # Preprints about target in last 2 years

    # === Medicare + Medicaid features ===
    "medicare_indication_spend",   # Annual Medicare spend on indication ($M)
    "medicaid_indication_spend",   # Annual Medicaid spend on indication ($M)

    # === Pathway + network features ===
    "reactome_pathway_count",      # Number of pathways target participates in
    "stringdb_interaction_degree",  # PPI network degree of target
    "stringdb_betweenness",        # Network betweenness centrality

    # === Genomic features ===
    "gtex_tissue_specificity",     # Tau index (0=ubiquitous, 1=tissue-specific)
    "gtex_max_expression_tissue",  # Tissue with highest expression
    "gnomad_pli",                  # Probability of loss-of-function intolerance
    "gnomad_loeuf",                # Loss-of-function observed/expected upper bound
    "clinvar_pathogenic_count",    # Number of pathogenic variants in target
    "gwas_hit_count",              # GWAS hits for target-disease pair
    "gwas_best_pvalue",            # Best GWAS p-value (log10)
    "depmap_essentiality",         # Mean gene effect score across cell lines
    "cbioportal_mutation_freq",    # Mutation frequency across cancer studies

    # === Disease complexity ===
    "hpo_phenotype_count",         # Number of HPO phenotypes for disease
    "monarch_gene_count",          # Number of genes associated with disease

    # === EMA features ===
    "ema_approved_similar",        # EMA approved similar MOA (1/0)
    "eu_filings_count",            # Related EU regulatory filings
]


def create_empty_dataset():
    """Create an empty CSV with the full schema."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
    print(f"Created empty dataset at {OUTPUT_FILE} with {len(COLUMNS)} columns")


def append_trial(row: dict):
    """Append a single trial row to the dataset."""
    with open(OUTPUT_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writerow(row)


# ---------------------------------------------------------------------------
# MCP QUERY INSTRUCTIONS FOR THE CONTAINER AGENT
# ---------------------------------------------------------------------------
#
# The container agent should execute this data collection by:
#
# 1. SEARCH COMPLETED TRIALS:
#    mcp__ctgov__ct_gov_studies(method: "search",
#      status: "COMPLETED", phase: "PHASE2|PHASE3",
#      condition: "<indication>", pageSize: 100)
#
# 2. FOR EACH TRIAL, EXTRACT:
#    a) Trial metadata from the search results
#    b) Full trial details: mcp__ctgov__ct_gov_studies(method: "get", nctId: "<NCT_ID>")
#
# 3. LABEL DETERMINATION:
#    a) Check FDA approval: mcp__fda__fda_info(method: "search_drugs", query: "<drug_name>")
#    b) If drug has NDA/BLA approval for the studied indication → label = 1
#    c) If trial terminated/withdrawn OR completed without approval → label = 0
#
# 4. FOR EACH TRIAL'S DRUG TARGET, ENRICH WITH:
#    a) OpenTargets: mcp__opentargets__opentargets_info(method: "search_targets", query: "<gene>")
#       Then: mcp__opentargets__opentargets_info(method: "get_target_disease_associations",
#             targetId: "<ensembl_id>", diseaseId: "<efo_id>")
#    b) ChEMBL: mcp__chembl__chembl_info(method: "compound_search", query: "<drug>")
#       Then: mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "<id>")
#    c) DrugBank: mcp__drugbank__drugbank_data(method: "search_drugs", query: "<drug>")
#    d) BindingDB: mcp__bindingdb__bindingdb_data(method: "search_by_name", name: "<drug>")
#    e) ClinPGx: mcp__clinpgx__clinpgx_data(method: "search_drug_gene_pairs", drug: "<drug>")
#    f) FDA FAERS: mcp__fda__fda_info(method: "get_adverse_events", drug_name: "<drug>")
#    g) PubMed: mcp__pubmed__pubmed_articles(method: "search_keywords",
#              keywords: "<target> <disease>", num_results: 5)
#    h) OpenAlex: mcp__openalex__openalex_data(method: "search_works", query: "<target> <disease>")
#    i) Reactome: mcp__reactome__reactome_data(method: "search", query: "<target>")
#    j) STRING-db: mcp__stringdb__stringdb_data(method: "get_interactions", protein: "<target>")
#    k) GTEx: mcp__gtex__gtex_data(method: "get_gene_expression", gene: "<gene>")
#    l) gnomAD: mcp__gnomad__gnomad_data(method: "get_gene_constraint", gene: "<gene>")
#    m) ClinVar: mcp__clinvar__clinvar_data(method: "search_variants", gene: "<gene>")
#    n) GWAS: mcp__gwas__gwas_data(method: "search_associations", query: "<gene> <disease>")
#    o) DepMap: mcp__depmap__depmap_data(method: "get_gene_dependency", gene: "<gene>")
#    p) cBioPortal: mcp__cbioportal__cbioportal_data(method: "get_gene_mutations", gene: "<gene>")
#    q) HPO: mcp__hpo__hpo_data(method: "search_terms", query: "<disease>")
#    r) Monarch: mcp__monarch__monarch_data(method: "search_diseases", query: "<disease>")
#    s) EMA: mcp__ema__ema_data(method: "search_medicines", query: "<drug>")
#    t) Medicare: mcp__medicare__medicare_data(method: "search", query: "<disease>")
#    u) Medicaid: mcp__medicaid__medicaid_data(method: "search", query: "<disease>")
#    v) bioRxiv: mcp__biorxiv__biorxiv_data(method: "search", query: "<target> <disease>")
#
# 5. WRITE EACH ROW:
#    Call append_trial({...}) with all extracted features
#
# 6. REPEAT for terminated/withdrawn trials to get failure examples
#
# Target: 200-500 trials total, ~50/50 success/failure split
# Focus on oncology (most data available), then expand to other indication areas
#
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create dataset schema")
    parser.add_argument("--init", action="store_true", help="Create empty dataset")
    args = parser.parse_args()

    if args.init:
        create_empty_dataset()
    else:
        print("Usage:")
        print("  python collect.py --init    # Create empty dataset with schema")
        print("")
        print("Data collection is done by the NanoClaw agent inside a container.")
        print("See MCP QUERY INSTRUCTIONS in this file for the collection protocol.")
        print(f"Schema: {len(COLUMNS)} columns")
