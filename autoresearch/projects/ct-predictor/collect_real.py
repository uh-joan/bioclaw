#!/usr/bin/env python3
"""
Real Clinical Trial Data Collector
Queries ClinicalTrials.gov + all MCP sources and appends to data/trials_raw.csv
"""

import sys, os
sys.path.insert(0, os.path.abspath('.'))
os.environ['MCP_CONFIG_FILE'] = os.path.abspath('mcp-config.json')

# Pre-stub mcp.servers to bypass broken __init__.py (imports non-existent modules)
import types as _types
_mcp_servers_stub = _types.ModuleType('mcp.servers')
_mcp_servers_stub.__path__ = [os.path.join(os.path.abspath('.'), 'mcp', 'servers')]
_mcp_servers_stub.__package__ = 'mcp.servers'
sys.modules['mcp.servers'] = _mcp_servers_stub

import csv
import re
import json
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Column schema (from collect.py)
# ─────────────────────────────────────────────────────────────────────────────
COLUMNS = [
    "nct_id", "title", "label",
    "phase", "status", "enrollment", "start_date", "completion_date",
    "study_type", "allocation", "masking", "primary_purpose",
    "intervention_type", "intervention_name", "condition", "indication_area",
    "sponsor_type", "lead_sponsor", "num_arms", "has_dmc",
    "endpoint_type", "num_secondary_endpoints", "num_sites",
    "has_biomarker_selection", "competitor_trial_count", "prior_phase_success",
    "ot_genetic_score", "ot_somatic_score", "ot_literature_score",
    "ot_animal_model_score", "ot_known_drug_score", "ot_affected_pathway_score",
    "ot_overall_score", "ot_target_tractability",
    "chembl_selectivity", "chembl_best_ic50_nm", "chembl_num_assays",
    "chembl_max_phase", "chembl_moa_count",
    "drugbank_interaction_count", "drugbank_target_count",
    "drugbank_enzyme_count", "drugbank_transporter_count",
    "drugbank_half_life_hours", "drugbank_molecular_weight",
    "bindingdb_ki_nm", "bindingdb_kd_nm", "bindingdb_num_measurements",
    "clinpgx_guideline_count", "clinpgx_actionable", "clinpgx_cyp_substrate_count",
    "fda_prior_approval_class", "fda_breakthrough", "fda_fast_track",
    "fda_orphan", "fda_class_ae_count",
    "pubmed_target_pub_count", "pubmed_drug_pub_count",
    "openalex_citation_velocity", "biorxiv_preprint_count",
    "medicare_indication_spend", "medicaid_indication_spend",
    "reactome_pathway_count", "stringdb_interaction_degree", "stringdb_betweenness",
    "gtex_tissue_specificity", "gtex_max_expression_tissue",
    "gnomad_pli", "gnomad_loeuf",
    "clinvar_pathogenic_count", "gwas_hit_count", "gwas_best_pvalue",
    "depmap_essentiality", "cbioportal_mutation_freq",
    "hpo_phenotype_count", "monarch_gene_count",
    "ema_approved_similar", "eu_filings_count",
]

DATA_DIR = Path("data")
OUTPUT_FILE = DATA_DIR / "trials_raw.csv"

# ─────────────────────────────────────────────────────────────────────────────
# Hardcoded trial list: drug, target gene, condition, label, search_phase
# ─────────────────────────────────────────────────────────────────────────────
TRIALS = [
    # ── Successes (label=1) ────────────────────────────────────────────────
    {"drug": "pembrolizumab", "target": "PDCD1", "condition": "melanoma", "label": 1, "phase": "PHASE3"},
    {"drug": "pembrolizumab", "target": "PDCD1", "condition": "non-small cell lung cancer", "label": 1, "phase": "PHASE3"},
    {"drug": "pembrolizumab", "target": "PDCD1", "condition": "head and neck squamous cell carcinoma", "label": 1, "phase": "PHASE3"},
    {"drug": "nivolumab", "target": "PDCD1", "condition": "melanoma", "label": 1, "phase": "PHASE3"},
    {"drug": "nivolumab", "target": "PDCD1", "condition": "non-small cell lung cancer", "label": 1, "phase": "PHASE3"},
    {"drug": "nivolumab", "target": "PDCD1", "condition": "renal cell carcinoma", "label": 1, "phase": "PHASE3"},
    {"drug": "trastuzumab", "target": "ERBB2", "condition": "breast cancer", "label": 1, "phase": "PHASE3"},
    {"drug": "trastuzumab", "target": "ERBB2", "condition": "gastric cancer", "label": 1, "phase": "PHASE3"},
    {"drug": "olaparib", "target": "PARP1", "condition": "ovarian cancer", "label": 1, "phase": "PHASE3"},
    {"drug": "olaparib", "target": "PARP1", "condition": "breast cancer", "label": 1, "phase": "PHASE3"},
    {"drug": "osimertinib", "target": "EGFR", "condition": "non-small cell lung cancer", "label": 1, "phase": "PHASE3"},
    {"drug": "palbociclib", "target": "CDK4", "condition": "breast cancer", "label": 1, "phase": "PHASE3"},
    {"drug": "atezolizumab", "target": "CD274", "condition": "urothelial carcinoma", "label": 1, "phase": "PHASE3"},
    {"drug": "atezolizumab", "target": "CD274", "condition": "non-small cell lung cancer", "label": 1, "phase": "PHASE3"},
    {"drug": "durvalumab", "target": "CD274", "condition": "non-small cell lung cancer", "label": 1, "phase": "PHASE3"},
    {"drug": "alectinib", "target": "ALK", "condition": "non-small cell lung cancer", "label": 1, "phase": "PHASE3"},
    {"drug": "dabrafenib", "target": "BRAF", "condition": "melanoma", "label": 1, "phase": "PHASE3"},
    {"drug": "trametinib", "target": "MAP2K1", "condition": "melanoma", "label": 1, "phase": "PHASE3"},
    {"drug": "ribociclib", "target": "CDK4", "condition": "breast cancer", "label": 1, "phase": "PHASE3"},
    {"drug": "lorlatinib", "target": "ALK", "condition": "non-small cell lung cancer", "label": 1, "phase": "PHASE3"},
    {"drug": "sotorasib", "target": "KRAS", "condition": "non-small cell lung cancer", "label": 1, "phase": "PHASE3"},
    {"drug": "encorafenib", "target": "BRAF", "condition": "colorectal cancer", "label": 1, "phase": "PHASE3"},
    {"drug": "tucatinib", "target": "ERBB2", "condition": "breast cancer", "label": 1, "phase": "PHASE3"},
    {"drug": "capmatinib", "target": "MET", "condition": "non-small cell lung cancer", "label": 1, "phase": "PHASE2"},
    {"drug": "trastuzumab deruxtecan", "target": "ERBB2", "condition": "breast cancer", "label": 1, "phase": "PHASE3"},
    {"drug": "sacituzumab govitecan", "target": "TACSTD2", "condition": "breast cancer", "label": 1, "phase": "PHASE3"},
    {"drug": "avelumab", "target": "CD274", "condition": "Merkel cell carcinoma", "label": 1, "phase": "PHASE3"},
    {"drug": "cemiplimab", "target": "PDCD1", "condition": "squamous cell carcinoma", "label": 1, "phase": "PHASE3"},
    {"drug": "lenvatinib", "target": "FLT4", "condition": "hepatocellular carcinoma", "label": 1, "phase": "PHASE3"},
    {"drug": "cabozantinib", "target": "MET", "condition": "renal cell carcinoma", "label": 1, "phase": "PHASE3"},
    {"drug": "baricitinib", "target": "JAK1", "condition": "rheumatoid arthritis", "label": 1, "phase": "PHASE3"},
    {"drug": "upadacitinib", "target": "JAK1", "condition": "rheumatoid arthritis", "label": 1, "phase": "PHASE3"},

    # ── Failures (label=0) ──────────────────────────────────────────────────
    {"drug": "epacadostat", "target": "IDO1", "condition": "melanoma", "label": 0, "phase": "PHASE3"},
    {"drug": "rociletinib", "target": "EGFR", "condition": "non-small cell lung cancer", "label": 0, "phase": "PHASE3"},
    {"drug": "onartuzumab", "target": "MET", "condition": "non-small cell lung cancer", "label": 0, "phase": "PHASE3"},
    {"drug": "selumetinib", "target": "MAP2K1", "condition": "thyroid cancer", "label": 0, "phase": "PHASE3"},
    {"drug": "iniparib", "target": "PARP1", "condition": "breast cancer", "label": 0, "phase": "PHASE3"},
    {"drug": "bavituximab", "target": "PTDSS1", "condition": "non-small cell lung cancer", "label": 0, "phase": "PHASE3"},
    {"drug": "ganitumab", "target": "IGF1R", "condition": "pancreatic cancer", "label": 0, "phase": "PHASE3"},
    {"drug": "figitumumab", "target": "IGF1R", "condition": "non-small cell lung cancer", "label": 0, "phase": "PHASE3"},
    {"drug": "dalotuzumab", "target": "IGF1R", "condition": "breast cancer", "label": 0, "phase": "PHASE3"},
    {"drug": "linsitinib", "target": "IGF1R", "condition": "adrenocortical carcinoma", "label": 0, "phase": "PHASE3"},
    {"drug": "trebananib", "target": "ANGPT1", "condition": "ovarian cancer", "label": 0, "phase": "PHASE3"},
    {"drug": "ipatasertib", "target": "AKT1", "condition": "breast cancer", "label": 0, "phase": "PHASE3"},
    {"drug": "buparlisib", "target": "PIK3CA", "condition": "breast cancer", "label": 0, "phase": "PHASE3"},
    {"drug": "taselisib", "target": "PIK3CA", "condition": "breast cancer", "label": 0, "phase": "PHASE3"},
    {"drug": "sapanisertib", "target": "MTOR", "condition": "cancer", "label": 0, "phase": "PHASE2"},
    {"drug": "mocetinostat", "target": "HDAC2", "condition": "lymphoma", "label": 0, "phase": "PHASE2"},
    {"drug": "entinostat", "target": "HDAC1", "condition": "breast cancer", "label": 0, "phase": "PHASE3"},
    {"drug": "tivozanib", "target": "FLT4", "condition": "non-small cell lung cancer", "label": 0, "phase": "PHASE3"},
    {"drug": "custirsen", "target": "CLU", "condition": "prostate cancer", "label": 0, "phase": "PHASE3"},
    {"drug": "perifosine", "target": "AKT1", "condition": "colorectal cancer", "label": 0, "phase": "PHASE3"},
    {"drug": "evacetrapib", "target": "CETP", "condition": "cardiovascular disease", "label": 0, "phase": "PHASE3"},
    {"drug": "atabecestat", "target": "BACE1", "condition": "Alzheimer disease", "label": 0, "phase": "PHASE3"},
    {"drug": "verubecestat", "target": "BACE1", "condition": "Alzheimer disease", "label": 0, "phase": "PHASE3"},
    {"drug": "lanabecestat", "target": "BACE1", "condition": "Alzheimer disease", "label": 0, "phase": "PHASE3"},
    {"drug": "aducanumab", "target": "APP", "condition": "Alzheimer disease", "label": 0, "phase": "PHASE3"},
    {"drug": "ramucirumab", "target": "KDR", "condition": "non-small cell lung cancer", "label": 0, "phase": "PHASE3"},
]

# ─────────────────────────────────────────────────────────────────────────────
# CSV helpers
# ─────────────────────────────────────────────────────────────────────────────

def init_csv():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=COLUMNS).writeheader()
        print(f"Created {OUTPUT_FILE}")
    else:
        print(f"Appending to existing {OUTPUT_FILE}")


def append_row(row: dict):
    with open(OUTPUT_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction='ignore')
        writer.writerow({col: row.get(col, "") for col in COLUMNS})


# ─────────────────────────────────────────────────────────────────────────────
# CT.gov helpers
# ─────────────────────────────────────────────────────────────────────────────

def extract_nct_ids(text):
    if isinstance(text, dict):
        text = text.get("text", "")
    return re.findall(r'NCT\d{8}', str(text))


def parse_study(study) -> dict:
    """Extract trial design features from a full get_study response."""
    out = {}
    # Handle different return shapes from ct_gov_mcp.get_study
    if isinstance(study, str):
        try:
            import json as _json
            study = _json.loads(study)
        except Exception:
            return out
    if isinstance(study, list):
        study = study[0] if study else {}
    if isinstance(study, dict):
        # Unwrap common envelope keys
        for key in ('data', 'study', 'result'):
            if key in study and isinstance(study[key], dict):
                study = study[key]
                break
    if not isinstance(study, dict):
        return out
    proto = study.get("protocolSection", {})

    # identifiers
    id_mod = proto.get("identificationModule", {})
    out["nct_id"] = id_mod.get("nctId", "")
    out["title"] = id_mod.get("briefTitle", "")

    # status
    status_mod = proto.get("statusModule", {})
    out["status"] = status_mod.get("overallStatus", "")
    out["start_date"] = status_mod.get("startDateStruct", {}).get("date", "")
    out["completion_date"] = status_mod.get("primaryCompletionDateStruct", {}).get("date", "")

    # design
    design_mod = proto.get("designModule", {})
    phases = design_mod.get("phases", [])
    out["phase"] = phases[0] if phases else ""
    out["study_type"] = design_mod.get("studyType", "")
    enrollment_info = design_mod.get("enrollmentInfo", {})
    out["enrollment"] = enrollment_info.get("count", "")
    design_info = design_mod.get("designInfo", {})
    out["allocation"] = design_info.get("allocation", "")
    out["primary_purpose"] = design_info.get("primaryPurpose", "")
    masking_info = design_info.get("maskingInfo", {})
    out["masking"] = masking_info.get("masking", "")
    out["num_arms"] = len(design_mod.get("armGroups", []))

    # sponsor
    sponsor_mod = proto.get("sponsorCollaboratorsModule", {})
    lead = sponsor_mod.get("leadSponsor", {})
    out["lead_sponsor"] = lead.get("name", "")
    sponsor_class = lead.get("class", "")
    if sponsor_class == "INDUSTRY":
        out["sponsor_type"] = "Industry"
    elif sponsor_class == "NIH":
        out["sponsor_type"] = "NIH"
    else:
        out["sponsor_type"] = "Other"

    # oversight
    oversight_mod = proto.get("oversightModule", {})
    has_dmc = oversight_mod.get("oversightHasDmc")
    out["has_dmc"] = 1 if has_dmc else 0

    # conditions
    cond_mod = proto.get("conditionsModule", {})
    conditions = cond_mod.get("conditions", [])
    out["condition"] = conditions[0] if conditions else ""

    # interventions
    arms_interventions = proto.get("armsInterventionsModule", {})
    interventions = arms_interventions.get("interventions", [])
    if interventions:
        first = interventions[0]
        out["intervention_type"] = first.get("type", "")
        out["intervention_name"] = first.get("name", "")

    # outcomes
    outcomes_mod = proto.get("outcomesModule", {})
    primary_outcomes = outcomes_mod.get("primaryOutcomes", [])
    secondary_outcomes = outcomes_mod.get("secondaryOutcomes", [])
    out["num_secondary_endpoints"] = len(secondary_outcomes)
    if primary_outcomes:
        measure = primary_outcomes[0].get("measure", "").lower()
        if "survival" in measure or " os " in measure or "overall survival" in measure:
            out["endpoint_type"] = "OS"
        elif "progression" in measure or "pfs" in measure:
            out["endpoint_type"] = "PFS"
        elif "response" in measure or "orr" in measure:
            out["endpoint_type"] = "ORR"
        elif "biomarker" in measure:
            out["endpoint_type"] = "biomarker"
        else:
            out["endpoint_type"] = "other"

    # sites
    contacts_mod = proto.get("contactsLocationsModule", {})
    locations = contacts_mod.get("locations", [])
    out["num_sites"] = len(locations)

    # biomarker selection (check eligibility criteria text)
    elig_mod = proto.get("eligibilityModule", {})
    criteria_text = elig_mod.get("eligibilityCriteria", "").lower()
    biomarker_keywords = ["mutation", "expression", "positive", "amplification", "fusion", "msih", "pd-l1", "her2"]
    out["has_biomarker_selection"] = 1 if any(kw in criteria_text for kw in biomarker_keywords) else 0

    return out


# ─────────────────────────────────────────────────────────────────────────────
# MCP feature extraction
# ─────────────────────────────────────────────────────────────────────────────

def get_ot_features(target: str, condition: str) -> dict:
    from mcp.servers.opentargets_mcp import search_targets, get_target_disease_associations
    out = {}
    try:
        targets_result = search_targets(query=target, size=3)
        target_id = None
        tractability = ""
        for t in targets_result.get("data", []):
            if t.get("approvedSymbol", "").upper() == target.upper():
                target_id = t.get("id")
                tractability = t.get("tractability", {})
                break
        if not target_id and targets_result.get("data"):
            target_id = targets_result["data"][0].get("id")
            tractability = targets_result["data"][0].get("tractability", {})

        if target_id:
            assoc = get_target_disease_associations(targetId=target_id, size=50)
            scores = []
            for a in assoc.get("data", []):
                scores.append(a)
                break  # just need first match
            if assoc.get("data"):
                first = assoc["data"][0]
                dt = first.get("datatypeScores", {})
                out["ot_genetic_score"] = dt.get("genetic_association", "")
                out["ot_somatic_score"] = dt.get("somatic_mutation", "")
                out["ot_literature_score"] = dt.get("literature", "")
                out["ot_animal_model_score"] = dt.get("animal_model", "")
                out["ot_known_drug_score"] = dt.get("known_drug", "")
                out["ot_affected_pathway_score"] = dt.get("affected_pathway", "")
                out["ot_overall_score"] = first.get("score", "")
            # tractability bucket
            if isinstance(tractability, dict):
                sm = tractability.get("smallmolecule", {})
                ab = tractability.get("antibody", {})
                bucket = sm.get("top_category") or ab.get("top_category") or ""
                out["ot_target_tractability"] = str(bucket)
    except Exception as e:
        print(f"    [OT] {e}")
    return out


def get_chembl_features(drug: str) -> dict:
    from mcp.servers.chembl_mcp import compound_search, get_bioactivity, get_mechanism
    out = {}
    try:
        res = compound_search(query=drug, limit=5)
        compounds = res.get("data", res.get("results", []))
        if not compounds:
            return out
        first = compounds[0]
        chembl_id = first.get("molecule_chembl_id", "")
        out["chembl_max_phase"] = first.get("max_phase", "")
        out["drugbank_molecular_weight"] = first.get("molecular_weight", "") or first.get("full_mwt", "")

        try:
            bio = get_bioactivity(chembl_id=chembl_id, limit=200)
            activities = bio.get("data", bio.get("results", []))
            # count unique targets with IC50 < 100 nM
            ic50s = [a for a in activities if a.get("standard_type") == "IC50"
                     and a.get("standard_units") == "nM"
                     and a.get("standard_value") is not None]
            targets_under_100nm = set()
            best_ic50 = None
            for a in ic50s:
                val = float(a.get("standard_value", 999999))
                if val < 100:
                    targets_under_100nm.add(a.get("target_chembl_id", ""))
                if best_ic50 is None or val < best_ic50:
                    best_ic50 = val
            out["chembl_selectivity"] = len(targets_under_100nm)
            out["chembl_best_ic50_nm"] = best_ic50 if best_ic50 is not None else ""
            out["chembl_num_assays"] = len(activities)
        except Exception as e:
            print(f"    [ChEMBL bioactivity] {e}")

        try:
            moa = get_mechanism(chembl_id=chembl_id)
            mechs = moa.get("data", moa.get("results", []))
            out["chembl_moa_count"] = len(mechs)
        except Exception as e:
            print(f"    [ChEMBL MOA] {e}")
    except Exception as e:
        print(f"    [ChEMBL] {e}")
    return out


def get_drugbank_features(drug: str) -> dict:
    from mcp.servers.drugbank_mcp import search_by_name, get_drug_interactions, get_drug_details
    out = {}
    try:
        res = search_by_name(query=drug, limit=5)
        drugs = res.get("data", [])
        if not drugs:
            return out
        db_id = drugs[0].get("drugbank_id", "")

        try:
            details = get_drug_details(drugbank_id=db_id)
            d = details.get("data", {})
            out["drugbank_molecular_weight"] = d.get("molecular_weight", "")
            hl = d.get("half_life", "")
            # try to extract numeric hours
            if hl:
                nums = re.findall(r'[\d.]+', str(hl))
                out["drugbank_half_life_hours"] = nums[0] if nums else ""
            targets = d.get("targets", [])
            enzymes = d.get("enzymes", [])
            transporters = d.get("transporters", [])
            out["drugbank_target_count"] = len(targets) if isinstance(targets, list) else ""
            out["drugbank_enzyme_count"] = len(enzymes) if isinstance(enzymes, list) else ""
            out["drugbank_transporter_count"] = len(transporters) if isinstance(transporters, list) else ""
        except Exception as e:
            print(f"    [DrugBank details] {e}")

        try:
            interactions = get_drug_interactions(drugbank_id=db_id)
            inter_list = interactions.get("data", [])
            out["drugbank_interaction_count"] = len(inter_list)
        except Exception as e:
            print(f"    [DrugBank interactions] {e}")
    except Exception as e:
        print(f"    [DrugBank] {e}")
    return out


def get_bindingdb_features(drug: str) -> dict:
    from mcp.servers.bindingdb_mcp import search_by_name as bindingdb_search
    out = {}
    try:
        res = bindingdb_search(query=drug, limit=100)
        entries = res.get("data", res.get("results", []))
        ki_vals, kd_vals = [], []
        for e in entries:
            ki = e.get("ki_nm") or e.get("Ki (nM)")
            kd = e.get("kd_nm") or e.get("Kd (nM)")
            if ki:
                try: ki_vals.append(float(ki))
                except: pass
            if kd:
                try: kd_vals.append(float(kd))
                except: pass
        out["bindingdb_ki_nm"] = min(ki_vals) if ki_vals else ""
        out["bindingdb_kd_nm"] = min(kd_vals) if kd_vals else ""
        out["bindingdb_num_measurements"] = len(entries)
    except Exception as e:
        print(f"    [BindingDB] {e}")
    return out


def get_clinpgx_features(drug: str) -> dict:
    from mcp.servers.clinpgx_mcp import get_clinical_annotations
    out = {}
    try:
        res = get_clinical_annotations(drug=drug, limit=50)
        annotations = res.get("data", res.get("results", []))
        out["clinpgx_guideline_count"] = len(annotations)
        out["clinpgx_actionable"] = 1 if annotations else 0
        # count CYP substrates
        cyp_genes = set()
        for a in annotations:
            gene = a.get("gene", "")
            if gene.startswith("CYP"):
                cyp_genes.add(gene)
        out["clinpgx_cyp_substrate_count"] = len(cyp_genes)
    except Exception as e:
        print(f"    [ClinPGx] {e}")
    return out


def get_fda_features(drug: str) -> dict:
    from mcp.servers.fda_mcp import lookup_drug
    out = {}
    # Check for breakthrough / fast track in label
    try:
        res = lookup_drug(
            search_term=drug,
            search_type="general",
            count="openfda.brand_name.exact",
            limit=50
        )
        results = res.get("data", {}).get("results", [])
        out["fda_prior_approval_class"] = 1 if results else 0
    except Exception as e:
        print(f"    [FDA general] {e}")
        out["fda_prior_approval_class"] = ""

    # AE count
    try:
        ae_res = lookup_drug(
            search_term=drug,
            search_type="adverse_events",
            count="patient.reaction.reactionmeddrapt.exact",
            limit=10
        )
        ae_list = ae_res.get("data", {}).get("results", [])
        total_ae = sum(item.get("count", 0) for item in ae_list)
        out["fda_class_ae_count"] = total_ae
    except Exception as e:
        print(f"    [FDA AE] {e}")

    # Designation flags — check recalls for orphan/breakthrough hints (best effort)
    out.setdefault("fda_breakthrough", "")
    out.setdefault("fda_fast_track", "")
    out.setdefault("fda_orphan", "")
    return out


def get_pubmed_features(target: str, drug: str) -> dict:
    from mcp.servers.pubmed_mcp import search_keywords as pubmed_search
    out = {}
    try:
        res1 = pubmed_search(keywords=f"{target} cancer", num_results=20)
        out["pubmed_target_pub_count"] = len(res1.get("articles", []))
    except Exception as e:
        print(f"    [PubMed target] {e}")
    try:
        res2 = pubmed_search(keywords=drug, num_results=20)
        out["pubmed_drug_pub_count"] = len(res2.get("articles", []))
    except Exception as e:
        print(f"    [PubMed drug] {e}")
    return out


def get_openalex_features(target: str, condition: str) -> dict:
    from mcp.servers.openalex_mcp import search_works
    out = {}
    try:
        res = search_works(query=f"{target} {condition}", limit=10)
        works = res.get("data", res.get("results", []))
        velocities = []
        for w in works:
            cpy = w.get("cited_by_count") or w.get("citations_per_year")
            if cpy:
                try: velocities.append(float(cpy))
                except: pass
        out["openalex_citation_velocity"] = velocities[0] if velocities else ""
    except Exception as e:
        print(f"    [OpenAlex] {e}")
    return out


def get_biorxiv_features(target: str, condition: str) -> dict:
    from mcp.servers.biorxiv_mcp import search_preprints
    out = {}
    try:
        res = search_preprints(query=f"{target} {condition}", limit=20)
        preprints = res.get("data", res.get("results", []))
        out["biorxiv_preprint_count"] = len(preprints)
    except Exception as e:
        print(f"    [bioRxiv] {e}")
    return out


def get_reactome_features(target: str) -> dict:
    from mcp.servers.reactome_mcp import find_pathways_by_gene
    out = {}
    try:
        res = find_pathways_by_gene(gene=target)
        pathways = res.get("data", res.get("pathways", res.get("results", [])))
        out["reactome_pathway_count"] = len(pathways)
    except Exception as e:
        print(f"    [Reactome] {e}")
    return out


def get_stringdb_features(target: str) -> dict:
    from mcp.servers.stringdb_mcp import get_protein_interactions
    out = {}
    try:
        res = get_protein_interactions(protein=target, species=9606, score_threshold=0.4, limit=200)
        interactions = res.get("data", res.get("interactions", res.get("results", [])))
        out["stringdb_interaction_degree"] = len(interactions)
        out["stringdb_betweenness"] = ""  # not available from basic call
    except Exception as e:
        print(f"    [STRING-db] {e}")
    return out


def get_gtex_features(target: str) -> dict:
    from mcp.servers.gtex_mcp import get_gene_expression
    out = {}
    try:
        res = get_gene_expression(gene=target)
        data = res.get("data", res.get("results", {}))
        # Calculate tissue specificity (tau index approximation)
        if isinstance(data, dict):
            values = [v for v in data.values() if isinstance(v, (int, float))]
        elif isinstance(data, list):
            values = []
            max_tissue = ""
            max_val = -1
            for item in data:
                tpm = item.get("median_tpm") or item.get("tpm") or 0
                try: tpm = float(tpm)
                except: tpm = 0
                values.append(tpm)
                tissue = item.get("tissue_site_detail") or item.get("tissue", "")
                if tpm > max_val:
                    max_val = tpm
                    max_tissue = tissue
            out["gtex_max_expression_tissue"] = max_tissue
        else:
            values = []

        if values:
            total = sum(values)
            max_val = max(values)
            if total > 0 and len(values) > 1:
                tau = sum(1 - v/max_val for v in values) / (len(values) - 1)
                out["gtex_tissue_specificity"] = round(tau, 4)
    except Exception as e:
        print(f"    [GTEx] {e}")
    return out


def get_gnomad_features(target: str) -> dict:
    from mcp.servers.gnomad_mcp import get_gene_constraint
    out = {}
    try:
        res = get_gene_constraint(gene=target)
        data = res.get("data", res.get("constraint", res))
        if isinstance(data, list) and data:
            data = data[0]
        if isinstance(data, dict):
            out["gnomad_pli"] = data.get("pLI") or data.get("pli", "")
            out["gnomad_loeuf"] = data.get("oe_lof_upper") or data.get("loeuf", "")
    except Exception as e:
        print(f"    [gnomAD] {e}")
    return out


def get_clinvar_features(target: str) -> dict:
    from mcp.servers.clinvar_mcp import get_gene_variants_summary
    out = {}
    try:
        res = get_gene_variants_summary(gene=target)
        data = res.get("data", res.get("summary", res))
        if isinstance(data, dict):
            pathogenic = data.get("Pathogenic", 0) or data.get("pathogenic", 0)
            likely_pathogenic = data.get("Likely pathogenic", 0) or data.get("likely_pathogenic", 0)
            out["clinvar_pathogenic_count"] = int(pathogenic) + int(likely_pathogenic)
    except Exception as e:
        print(f"    [ClinVar] {e}")
    return out


def get_gwas_features(target: str) -> dict:
    from mcp.servers.gwas_mcp import get_gene_associations
    out = {}
    try:
        res = get_gene_associations(gene=target, limit=200)
        assocs = res.get("data", res.get("associations", res.get("results", [])))
        out["gwas_hit_count"] = len(assocs)
        best_p = None
        for a in assocs:
            pval = a.get("pvalue") or a.get("p_value") or a.get("p-value")
            if pval:
                try:
                    p = float(pval)
                    if best_p is None or p < best_p:
                        best_p = p
                except: pass
        if best_p is not None and best_p > 0:
            import math
            out["gwas_best_pvalue"] = round(math.log10(best_p), 2)
    except Exception as e:
        print(f"    [GWAS] {e}")
    return out


def get_depmap_features(target: str) -> dict:
    from mcp.servers.depmap_mcp import get_gene_dependency
    out = {}
    try:
        res = get_gene_dependency(gene=target)
        data = res.get("data", {})
        scores = data.get("dependency_scores") or data.get("scores") or []
        if isinstance(scores, list) and scores:
            try:
                numeric = [float(s) for s in scores if s is not None]
                out["depmap_essentiality"] = round(sum(numeric)/len(numeric), 4) if numeric else ""
            except: pass
        elif isinstance(data, dict):
            mean_score = data.get("mean_gene_effect") or data.get("mean_score") or data.get("mean")
            out["depmap_essentiality"] = mean_score or ""
    except Exception as e:
        print(f"    [DepMap] {e}")
    return out


def get_cbioportal_features(target: str) -> dict:
    from mcp.servers.cbioportal_mcp import get_gene as cbioportal_gene
    out = {}
    try:
        res = cbioportal_gene(gene=target)
        data = res.get("data", res)
        if isinstance(data, dict):
            out["cbioportal_mutation_freq"] = data.get("mutation_frequency") or data.get("mutation_rate") or ""
    except Exception as e:
        print(f"    [cBioPortal] {e}")
    return out


def get_hpo_features(condition: str) -> dict:
    from mcp.servers.hpo_mcp import search_terms as hpo_search
    out = {}
    try:
        res = hpo_search(query=condition, limit=100)
        terms = res.get("data", res.get("terms", res.get("results", [])))
        out["hpo_phenotype_count"] = len(terms)
    except Exception as e:
        print(f"    [HPO] {e}")
    return out


def get_monarch_features(condition: str) -> dict:
    from mcp.servers.monarch_mcp import get_disease_genes
    out = {}
    try:
        res = get_disease_genes(disease=condition, limit=200)
        genes = res.get("data", res.get("genes", res.get("results", [])))
        out["monarch_gene_count"] = len(genes)
    except Exception as e:
        print(f"    [Monarch] {e}")
    return out


def get_ema_features(drug: str) -> dict:
    from mcp.servers.ema_mcp import search_medicines as ema_search
    out = {}
    try:
        res = ema_search(active_substance=drug, limit=20)
        medicines = res.get("data", res.get("results", []))
        out["ema_approved_similar"] = 1 if medicines else 0
        out["eu_filings_count"] = len(medicines)
    except Exception as e:
        print(f"    [EMA] {e}")
    return out


def infer_indication_area(condition: str) -> str:
    c = condition.lower()
    if any(k in c for k in ["cancer", "carcinoma", "melanoma", "lymphoma", "leukemia", "tumor", "sarcoma", "myeloma", "glioma"]):
        return "oncology"
    if any(k in c for k in ["alzheimer", "parkinson", "dementia", "neurolog", "cns"]):
        return "cns"
    if any(k in c for k in ["diabetes", "metabolic", "obesity", "insulin"]):
        return "metabolic"
    if any(k in c for k in ["arthritis", "lupus", "immune", "autoimmune", "crohn"]):
        return "immunology"
    if any(k in c for k in ["cardiovascular", "heart", "coronary", "lipid", "cholesterol"]):
        return "cardiovascular"
    return "other"


# ─────────────────────────────────────────────────────────────────────────────
# Main loop
# ─────────────────────────────────────────────────────────────────────────────

def collect_trial(trial_def: dict, idx: int, total: int) -> dict:
    from mcp.servers.ct_gov_mcp import search, get_study

    drug = trial_def["drug"]
    target = trial_def["target"]
    condition = trial_def["condition"]
    label = trial_def["label"]
    phase = trial_def.get("phase", "PHASE3")

    row = {col: "" for col in COLUMNS}
    row["label"] = label
    row["condition"] = condition
    row["intervention_name"] = drug
    row["indication_area"] = infer_indication_area(condition)

    # ── Step 1: Search CT.gov ────────────────────────────────────────────────
    nct_id = ""
    try:
        search_result = search(
            intervention=drug,
            condition=condition,
            phase=phase,
            pageSize=5
        )
        nct_ids = extract_nct_ids(search_result)
        if not nct_ids:
            # Try broader search without phase
            search_result2 = search(intervention=drug, condition=condition, pageSize=5)
            nct_ids = extract_nct_ids(search_result2)
        if nct_ids:
            nct_id = nct_ids[0]
    except Exception as e:
        print(f"    [CT.gov search] {e}")

    # ── Step 2: Get full study details ───────────────────────────────────────
    if nct_id:
        try:
            study = get_study(nctId=nct_id)
            study_features = parse_study(study)
            row.update(study_features)
        except Exception as e:
            print(f"    [CT.gov get_study] {e}")
            row["nct_id"] = nct_id

    if not row.get("nct_id"):
        row["nct_id"] = nct_id or f"UNKNOWN_{drug.replace(' ','_')}_{condition[:20].replace(' ','_')}"

    # ── Step 3: OpenTargets ──────────────────────────────────────────────────
    row.update(get_ot_features(target, condition))

    # ── Step 4: ChEMBL ──────────────────────────────────────────────────────
    row.update(get_chembl_features(drug))

    # ── Step 5: DrugBank ────────────────────────────────────────────────────
    row.update(get_drugbank_features(drug))

    # ── Step 6: BindingDB ───────────────────────────────────────────────────
    row.update(get_bindingdb_features(drug))

    # ── Step 7: ClinPGx ─────────────────────────────────────────────────────
    row.update(get_clinpgx_features(drug))

    # ── Step 8: FDA ─────────────────────────────────────────────────────────
    row.update(get_fda_features(drug))

    # ── Step 9: PubMed ──────────────────────────────────────────────────────
    row.update(get_pubmed_features(target, drug))

    # ── Step 10: OpenAlex ───────────────────────────────────────────────────
    row.update(get_openalex_features(target, condition))

    # ── Step 11: bioRxiv ────────────────────────────────────────────────────
    row.update(get_biorxiv_features(target, condition))

    # ── Step 12: Reactome ───────────────────────────────────────────────────
    row.update(get_reactome_features(target))

    # ── Step 13: STRING-db ──────────────────────────────────────────────────
    row.update(get_stringdb_features(target))

    # ── Step 14: GTEx ───────────────────────────────────────────────────────
    row.update(get_gtex_features(target))

    # ── Step 15: gnomAD ─────────────────────────────────────────────────────
    row.update(get_gnomad_features(target))

    # ── Step 16: ClinVar ────────────────────────────────────────────────────
    row.update(get_clinvar_features(target))

    # ── Step 17: GWAS ───────────────────────────────────────────────────────
    row.update(get_gwas_features(target))

    # ── Step 18: DepMap ─────────────────────────────────────────────────────
    row.update(get_depmap_features(target))

    # ── Step 19: cBioPortal ─────────────────────────────────────────────────
    row.update(get_cbioportal_features(target))

    # ── Step 20: HPO ────────────────────────────────────────────────────────
    row.update(get_hpo_features(condition))

    # ── Step 21: Monarch ────────────────────────────────────────────────────
    row.update(get_monarch_features(condition))

    # ── Step 22: EMA ────────────────────────────────────────────────────────
    row.update(get_ema_features(drug))

    print(f"[{idx+1}/{total}] {row['nct_id']} {drug} label={label}")
    return row


def main():
    init_csv()
    total = len(TRIALS)
    print(f"\nCollecting {total} trials...\n")

    for idx, trial_def in enumerate(TRIALS):
        try:
            row = collect_trial(trial_def, idx, total)
            append_row(row)
        except Exception as e:
            print(f"[{idx+1}/{total}] ERROR on {trial_def['drug']}: {e}")
            # Write partial row with what we know
            row = {col: "" for col in COLUMNS}
            row["label"] = trial_def["label"]
            row["intervention_name"] = trial_def["drug"]
            row["condition"] = trial_def["condition"]
            row["nct_id"] = f"ERROR_{trial_def['drug'].replace(' ','_')[:20]}"
            row["indication_area"] = infer_indication_area(trial_def["condition"])
            append_row(row)

    print(f"\nDone. Wrote to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
