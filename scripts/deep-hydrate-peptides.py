#!/usr/bin/env python3
"""
Deep hydration pass: fill in dosing, side effects, interactions, community insights,
fingerprints, and reconstitution data using public APIs.

APIs used:
- ChEMBL REST API (mechanism, max phase, targets)
- ClinicalTrials.gov v2 API (trial data, dosing from protocols)
- PubMed E-utilities (side effects, pharmacology)
- PubChem REST API (molecular properties)
"""

import json
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
import re
from pathlib import Path
from datetime import datetime, timezone

KNOWLEDGE_DIR = Path(__file__).parent.parent / "container" / "skills" / "peptigotchi" / "knowledge"
COMPOUNDS_FILE = KNOWLEDGE_DIR / "compounds.json"
FINGERPRINTS_FILE = KNOWLEDGE_DIR / "fingerprints.json"
RECONSTITUTION_FILE = KNOWLEDGE_DIR / "reconstitution.json"
LOG_FILE = KNOWLEDGE_DIR / "deep-hydration-progress.log"


def api_get(url: str, retries: int = 3) -> dict | list | None:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "NanoClaw-DeepHydrate/1.0",
                "Accept": "application/json",
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                return None


# ── ChEMBL ──────────────────────────────────────────────────────────────────

def chembl_search(name: str) -> dict:
    """Search ChEMBL for molecule data (mechanism, max phase, targets)."""
    encoded = urllib.parse.quote(name)
    url = f"https://www.ebi.ac.uk/chembl/api/data/molecule/search.json?q={encoded}&limit=1"
    data = api_get(url)
    if not data or not data.get("molecules"):
        return {}

    mol = data["molecules"][0]
    chembl_id = mol.get("molecule_chembl_id", "")
    result = {
        "chembl_id": chembl_id,
        "max_phase": mol.get("max_phase", 0),
        "molecule_type": mol.get("molecule_type", ""),
        "oral": mol.get("oral", False),
        "parenteral": mol.get("parenteral", False),
        "topical": mol.get("topical", False),
    }

    # Get mechanism of action
    if chembl_id:
        mech_url = f"https://www.ebi.ac.uk/chembl/api/data/mechanism.json?molecule_chembl_id={chembl_id}&limit=5"
        mech_data = api_get(mech_url)
        if mech_data and mech_data.get("mechanisms"):
            mechs = mech_data["mechanisms"]
            result["mechanisms"] = [
                {
                    "action_type": m.get("action_type", ""),
                    "mechanism_of_action": m.get("mechanism_of_action", ""),
                    "target_name": m.get("target_chembl_id", ""),
                }
                for m in mechs[:3]
            ]

    return result


# ── ClinicalTrials.gov v2 ───────────────────────────────────────────────────

def ctgov_search(name: str) -> list[dict]:
    """Search ClinicalTrials.gov for trial data."""
    # Clean name for search
    clean = re.sub(r'\s*\([^)]*\)', '', name).strip()
    encoded = urllib.parse.quote(clean)
    url = f"https://clinicaltrials.gov/api/v2/studies?query.intr={encoded}&pageSize=5&format=json"
    data = api_get(url)
    if not data or not data.get("studies"):
        return []

    results = []
    for study in data["studies"][:5]:
        proto = study.get("protocolSection", {})
        ident = proto.get("identificationModule", {})
        status_mod = proto.get("statusModule", {})
        design = proto.get("designModule", {})
        arms = proto.get("armsInterventionsModule", {})

        # Extract dosing from arm descriptions
        dosing_info = []
        for arm in arms.get("armGroups", []):
            desc = arm.get("description", "")
            if any(kw in desc.lower() for kw in ["mg", "mcg", "µg", "dose", "injection", "daily", "weekly"]):
                dosing_info.append(desc[:200])

        results.append({
            "nct_id": ident.get("nctId", ""),
            "title": ident.get("briefTitle", ""),
            "status": status_mod.get("overallStatus", ""),
            "phase": design.get("phases", []),
            "enrollment": design.get("enrollmentInfo", {}).get("count", 0),
            "dosing_info": dosing_info[:2],
        })

    return results


# ── PubMed side effects ─────────────────────────────────────────────────────

def pubmed_side_effects(name: str) -> list[str]:
    """Search PubMed for side effect reports."""
    clean = re.sub(r'\s*\([^)]*\)', '', name).strip()
    query = urllib.parse.quote(f"{clean} (side effects OR adverse effects OR toxicity)")
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmax=5&retmode=json"
    data = api_get(url)
    if not data:
        return []

    ids = data.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []

    id_str = ",".join(ids)
    sum_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={id_str}&retmode=json"
    sum_data = api_get(sum_url)
    if not sum_data:
        return []

    titles = []
    for pmid in ids:
        article = sum_data.get("result", {}).get(pmid, {})
        title = article.get("title", "")
        if title:
            titles.append(title)

    return titles


# ── PubChem properties ──────────────────────────────────────────────────────

def pubchem_properties(cid: int) -> dict:
    """Get molecular properties from PubChem."""
    if cid <= 0:
        return {}
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/MolecularWeight,MolecularFormula,IsomericSMILES/JSON"
    data = api_get(url)
    if not data:
        return {}
    try:
        props = data["PropertyTable"]["Properties"][0]
        return {
            "molecular_weight": props.get("MolecularWeight", 0),
            "formula": props.get("MolecularFormula", ""),
        }
    except (KeyError, IndexError):
        return {}


# ── Known data for major compounds ──────────────────────────────────────────
# For compounds where public APIs are sparse, use curated knowledge

CURATED_DATA = {
    "liraglutide": {
        "dose": {"min_mcg": 600, "max_mcg": 3000},
        "frequency": "1x daily",
        "routes": ["subcutaneous", "oral"],
        "vials": [6, 18],
        "community": {
            "top_positive_use": "Sustained weight loss and glycemic control — LEADER trial showed 13% CV event reduction",
            "top_negative_report": "Nausea (40% in trials), injection site reactions, pancreatitis risk",
            "common_mistake": "Not titrating slowly enough — start at 0.6mg, increase by 0.6mg weekly to target dose",
            "pro_tip": "Daily injection vs semaglutide's weekly. Consider switching to semaglutide for convenience unless liraglutide is specifically indicated."
        },
        "fingerprint": [
            {"symptom": "nausea", "frequency": "very_common", "severity": "mild_to_moderate", "mechanism": "GLP-1 receptor activation in brainstem", "onset_days": {"min": 1, "max": 7}},
            {"symptom": "diarrhea", "frequency": "common", "severity": "mild", "mechanism": "GI motility changes", "onset_days": {"min": 1, "max": 14}},
            {"symptom": "pancreatitis", "frequency": "rare", "severity": "severe", "mechanism": "GLP-1 mediated pancreatic stimulation", "onset_days": {"min": 30, "max": 180}},
        ],
    },
    "pt-141": {
        "dose": {"min_mcg": 1750, "max_mcg": 1750},
        "frequency": "As needed, max 1x per 24h",
        "routes": ["subcutaneous"],
        "vials": [10],
        "community": {
            "top_positive_use": "FDA-approved for female HSDD — works via central melanocortin pathway, not vascular",
            "top_negative_report": "Nausea (40%), flushing, headache. Skin darkening with repeated use (melanocortin effect)",
            "common_mistake": "Using as a daily supplement — it's an as-needed medication, not a routine peptide",
            "pro_tip": "Inject 45 minutes before desired effect. Nausea is dose-dependent — some users find 500-1000mcg effective with fewer side effects."
        },
        "fingerprint": [
            {"symptom": "nausea", "frequency": "very_common", "severity": "moderate", "mechanism": "Melanocortin receptor activation in area postrema", "onset_days": {"min": 0, "max": 0}},
            {"symptom": "flushing", "frequency": "common", "severity": "mild", "mechanism": "Vasodilation from melanocortin activation", "onset_days": {"min": 0, "max": 0}},
            {"symptom": "skin_darkening", "frequency": "uncommon", "severity": "mild", "mechanism": "MC1R activation stimulates melanogenesis", "onset_days": {"min": 14, "max": 60}},
        ],
    },
    "aod-9604": {
        "dose": {"min_mcg": 250, "max_mcg": 500},
        "frequency": "1x daily (fasted)",
        "routes": ["subcutaneous", "oral"],
        "vials": [3, 5],
        "community": {
            "top_positive_use": "Targeted fat loss without GH side effects — the lipolytic fragment of HGH",
            "top_negative_report": "Failed Phase IIb trial (900+ subjects, no efficacy vs placebo). Questionable real-world efficacy.",
            "common_mistake": "Expecting results comparable to GLP-1 agonists — AOD-9604 failed its clinical trial for obesity",
            "pro_tip": "If using, take fasted in the morning. Be aware this peptide FAILED its pivotal trial — evidence is very weak."
        },
    },
    "sermorelin": {
        "dose": {"min_mcg": 200, "max_mcg": 300},
        "frequency": "1x daily (before bed)",
        "routes": ["subcutaneous"],
        "vials": [3, 9, 15],
        "community": {
            "top_positive_use": "Sleep quality and anti-aging via physiologic GH stimulation — was FDA-approved for pediatric GH deficiency",
            "top_negative_report": "Voluntarily withdrawn from US market in 2008 (manufacturing, not safety). Quality concerns with compounded versions.",
            "common_mistake": "Stacking with other GHRH analogs (CJC-1295, tesamorelin) — redundant pathway stimulation",
            "pro_tip": "One of the oldest and best-studied GH secretagogues. Inject before bed fasted. Effects are subtle — expect 4-6 weeks for noticeable sleep improvement."
        },
    },
    "mk-677": {
        "dose": {"min_mcg": 10000, "max_mcg": 25000},
        "frequency": "1x daily (oral)",
        "routes": ["oral"],
        "vials": [],
        "community": {
            "top_positive_use": "Oral GH secretagogue — no injections needed. Sleep quality and appetite increase.",
            "top_negative_report": "Water retention, increased appetite (problematic for weight loss), elevated blood sugar, lethargy",
            "common_mistake": "Using for weight loss — MK-677 dramatically increases appetite and can cause weight gain",
            "pro_tip": "Not actually a peptide — it's a non-peptide ghrelin mimetic. Take before bed to minimize appetite effects. Monitor fasting glucose."
        },
        "fingerprint": [
            {"symptom": "water_retention", "frequency": "very_common", "severity": "moderate", "mechanism": "GH-mediated sodium retention", "onset_days": {"min": 3, "max": 14}},
            {"symptom": "increased_appetite", "frequency": "very_common", "severity": "moderate", "mechanism": "Ghrelin receptor activation", "onset_days": {"min": 1, "max": 3}},
            {"symptom": "elevated_blood_sugar", "frequency": "common", "severity": "moderate", "mechanism": "GH antagonizes insulin action", "onset_days": {"min": 14, "max": 60}},
            {"symptom": "lethargy", "frequency": "common", "severity": "mild", "mechanism": "GH release during waking hours", "onset_days": {"min": 1, "max": 7}},
        ],
    },
    "epithalon": {
        "dose": {"min_mcg": 5000, "max_mcg": 10000},
        "frequency": "1x daily for 10-20 day cycles",
        "routes": ["subcutaneous"],
        "vials": [10, 20, 50],
        "community": {
            "top_positive_use": "Telomerase activation and anti-aging — based on Khavinson's research",
            "top_negative_report": "All evidence from a single Russian lab. Zero Western replication. Telomerase activation claims based on cell culture only.",
            "common_mistake": "Expecting measurable anti-aging results — no validated biomarkers to track its effect",
            "pro_tip": "Typically cycled 10 days on, 6 months off. Evidence is Tier 4 (no human clinical trials). Pure faith-based supplementation."
        },
    },
    "dsip": {
        "dose": {"min_mcg": 100, "max_mcg": 250},
        "frequency": "1x daily (before bed)",
        "routes": ["subcutaneous", "intranasal"],
        "vials": [2, 5],
        "community": {
            "top_positive_use": "Sleep onset and quality improvement — the 'delta sleep' peptide",
            "top_negative_report": "Tolerance builds quickly with daily use. Inconsistent effects reported. Limited evidence.",
            "common_mistake": "Using nightly without cycling — tolerance develops within 1-2 weeks",
            "pro_tip": "Cycle 5 days on, 2 days off maximum. Stack with low-dose melatonin for synergistic effect. Keep expectations modest."
        },
    },
    "ghrp-2": {
        "dose": {"min_mcg": 100, "max_mcg": 300},
        "frequency": "1-3x daily",
        "routes": ["subcutaneous"],
        "vials": [2, 5],
        "community": {
            "top_positive_use": "Strong GH release — most potent GHRP. Good for body recomposition goals.",
            "top_negative_report": "Significant hunger increase (ghrelin mimetic), cortisol and prolactin elevation",
            "common_mistake": "Not accounting for appetite increase when using for cutting/fat loss",
            "pro_tip": "More potent than ipamorelin but dirtier (raises cortisol/prolactin). Start at 100mcg. Take fasted."
        },
        "fingerprint": [
            {"symptom": "intense_hunger", "frequency": "very_common", "severity": "moderate", "mechanism": "Ghrelin receptor agonism", "onset_days": {"min": 0, "max": 0}},
            {"symptom": "water_retention", "frequency": "common", "severity": "mild", "mechanism": "GH-mediated", "onset_days": {"min": 3, "max": 14}},
            {"symptom": "cortisol_elevation", "frequency": "common", "severity": "mild", "mechanism": "GHRP-2 stimulates ACTH/cortisol release", "onset_days": {"min": 1, "max": 7}},
        ],
    },
    "ghrp-6": {
        "dose": {"min_mcg": 100, "max_mcg": 300},
        "frequency": "1-3x daily",
        "routes": ["subcutaneous"],
        "vials": [2, 5],
        "community": {
            "top_positive_use": "Strong GH release with pronounced appetite stimulation — useful for underweight/recovery",
            "top_negative_report": "Extreme hunger (strongest appetite stimulant in GHRP class), cortisol/prolactin spikes",
            "common_mistake": "Using GHRP-6 when appetite increase is unwanted — choose ipamorelin instead",
            "pro_tip": "Reserved for when appetite stimulation is a FEATURE not a bug (cachexia, recovery from illness, underweight)."
        },
    },
    "hexarelin": {
        "dose": {"min_mcg": 100, "max_mcg": 200},
        "frequency": "1-2x daily",
        "routes": ["subcutaneous"],
        "vials": [2, 5],
        "community": {
            "top_positive_use": "Strongest GH release of any GHRP — cardiac protective properties in animal studies",
            "top_negative_report": "Rapid desensitization (GH response diminishes within 2-4 weeks of continuous use)",
            "common_mistake": "Using continuously — hexarelin desensitizes faster than other GHRPs. Must cycle.",
            "pro_tip": "Use in short cycles (2 weeks on, 2 weeks off) to prevent receptor desensitization. Some users rotate with ipamorelin."
        },
    },
    "mots-c": {
        "dose": {"min_mcg": 5000, "max_mcg": 10000},
        "frequency": "3-5x weekly",
        "routes": ["subcutaneous"],
        "vials": [5, 10],
        "community": {
            "top_positive_use": "Exercise mimetic — AMPK activation, metabolic improvement without exercise",
            "top_negative_report": "Entirely preclinical. Zero human data. Expensive. Questionable if injectable form reaches mitochondria.",
            "common_mistake": "Replacing exercise with MOTS-C — even if it works, it's meant to complement, not replace physical activity",
            "pro_tip": "Mitochondrial-derived peptide with interesting biology but zero clinical validation. Pure research compound."
        },
    },
    "ll-37": {
        "dose": {"min_mcg": 50, "max_mcg": 100},
        "frequency": "1x daily",
        "routes": ["subcutaneous"],
        "vials": [5],
        "community": {
            "top_positive_use": "Antimicrobial peptide — natural part of innate immunity. Used for chronic infections, biofilm disruption.",
            "top_negative_report": "Very limited dosing data. Can cause injection site reactions. Pro-inflammatory at high doses.",
            "common_mistake": "Using high doses — LL-37 is pro-inflammatory at elevated concentrations, anti-inflammatory at low doses",
            "pro_tip": "Start at 50mcg. This is a human cathelicidin — your body naturally produces it. SubQ for systemic, topical for skin infections."
        },
    },
    "kpv": {
        "dose": {"min_mcg": 200, "max_mcg": 500},
        "frequency": "1-2x daily",
        "routes": ["subcutaneous", "oral", "topical"],
        "vials": [5],
        "community": {
            "top_positive_use": "Anti-inflammatory — fragment of alpha-MSH. Used for gut inflammation, skin conditions.",
            "top_negative_report": "Very limited evidence. Most data extrapolated from alpha-MSH research.",
            "common_mistake": "Expecting it to work like a standalone treatment for IBD — use as adjunctive, not primary therapy",
            "pro_tip": "Oral bioavailability may be sufficient for GI targeting. Some users take oral for gut, SubQ for systemic."
        },
    },
    "oxytocin": {
        "dose": {"min_mcg": 10000, "max_mcg": 24000},
        "frequency": "As needed (intranasal) or per protocol",
        "routes": ["intranasal", "subcutaneous", "intravenous"],
        "vials": [10, 30],
        "community": {
            "top_positive_use": "Social bonding, anxiety reduction, trust — the 'love hormone'. FDA-approved for labor induction.",
            "top_negative_report": "Tolerance with chronic use. Can paradoxically increase anxiety in some contexts. Nasal irritation.",
            "common_mistake": "Using daily for anxiety — tolerance develops. Works best as-needed for social situations.",
            "pro_tip": "Intranasal is standard for behavioral effects. FDA-approved for obstetric use. Off-label for autism, social anxiety research."
        },
    },
    "gonadorelin": {
        "dose": {"min_mcg": 100, "max_mcg": 500},
        "frequency": "2x weekly",
        "routes": ["subcutaneous"],
        "vials": [2],
        "community": {
            "top_positive_use": "Maintains testicular function during TRT — stimulates natural LH/FSH release",
            "top_negative_report": "Short half-life (~4 min) means pulsatile dosing is key. Headache, nausea in some users.",
            "common_mistake": "Using continuous (daily) instead of pulsatile — continuous GnRH actually SUPPRESSES LH (same mechanism as triptorelin for chemical castration)",
            "pro_tip": "Alternative to HCG for preserving fertility on TRT. 2x/week SubQ. Half-life is very short so timing matters less than frequency."
        },
    },
    "enclomiphene": {
        "dose": {"min_mcg": 12500, "max_mcg": 25000},
        "frequency": "1x daily (oral)",
        "routes": ["oral"],
        "vials": [],
        "community": {
            "top_positive_use": "Raises testosterone by blocking estrogen feedback at the pituitary — alternative to TRT that preserves fertility",
            "top_negative_report": "Not FDA-approved (FDA rejected in 2015). Visual disturbances, headaches, mood changes.",
            "common_mistake": "Confusing with clomiphene (Clomid) — enclomiphene is the trans-isomer only, fewer side effects than racemic clomiphene",
            "pro_tip": "Popular in the peptide/optimization community as TRT alternative. Oral, no injections. Monitor estrogen levels."
        },
    },
    "dihexa": {
        "dose": {"min_mcg": 10000, "max_mcg": 20000},
        "frequency": "1x daily (oral or intranasal)",
        "routes": ["oral", "intranasal", "topical"],
        "vials": [10, 30],
        "community": {
            "top_positive_use": "Potent nootropic — 10 million times more potent than BDNF at promoting synaptogenesis in vitro",
            "top_negative_report": "Zero human data. HGF/c-Met pathway activation raises theoretical cancer risk. Single lab.",
            "common_mistake": "Citing the '10 million times more potent than BDNF' stat without context — that's an in vitro binding assay, not a clinical outcome",
            "pro_tip": "One of the most controversial nootropic peptides. Theoretical cancer risk from c-Met activation is real. Not for long-term use."
        },
    },
    "cerebrolysin": {
        "dose": {"min_mcg": 5000000, "max_mcg": 30000000},
        "frequency": "1x daily for 10-20 day cycles (IV/IM)",
        "routes": ["intramuscular", "intravenous"],
        "vials": [],
        "community": {
            "top_positive_use": "Neuroprotection and cognitive enhancement — approved in 40+ countries for stroke and TBI recovery",
            "top_negative_report": "Not FDA-approved. Requires IV/IM administration. Derived from porcine brain tissue.",
            "common_mistake": "Attempting SubQ — cerebrolysin is designed for IM or IV only. Large volumes needed.",
            "pro_tip": "One of few nootropics with actual clinical trial data (stroke recovery, dementia). Approved widely outside US. Needs medical supervision."
        },
    },
    "follistatin": {
        "dose": {"min_mcg": 100, "max_mcg": 200},
        "frequency": "1x daily for limited cycles",
        "routes": ["subcutaneous"],
        "vials": [1],
        "community": {
            "top_positive_use": "Myostatin inhibitor — promotes muscle growth by blocking the muscle-growth-limiting protein",
            "top_negative_report": "Extremely expensive. Very limited human data. Theoretical reproductive concerns (follistatin regulates FSH).",
            "common_mistake": "Expecting steroid-like muscle gains — myostatin inhibition effects in adults are modest at best",
            "pro_tip": "315 and 344 are different isoforms. 344 is more commonly available but less tissue-specific. Cycle short (10-30 days)."
        },
    },
    "vip": {
        "dose": {"min_mcg": 50, "max_mcg": 200},
        "frequency": "1x daily (intranasal)",
        "routes": ["intranasal", "subcutaneous"],
        "vials": [5],
        "community": {
            "top_positive_use": "Immune modulation and CIRS (chronic inflammatory response syndrome) treatment — popularized by Dr. Shoemaker protocol",
            "top_negative_report": "Must be used as final step in Shoemaker protocol. Can worsen symptoms if used prematurely. Limited evidence.",
            "common_mistake": "Using VIP before completing upstream CIRS treatments (binders, antifungals, etc.)",
            "pro_tip": "Vasoactive intestinal peptide — naturally produced. Intranasal is standard route for CIRS. Must be compounded fresh."
        },
    },
    "humanin": {
        "dose": {"min_mcg": 500, "max_mcg": 3000},
        "frequency": "1x daily",
        "routes": ["subcutaneous"],
        "vials": [5],
        "community": {
            "top_positive_use": "Mitochondrial-derived peptide with neuroprotective and metabolic benefits — related to MOTS-C",
            "top_negative_report": "Entirely preclinical. Zero human clinical trials. Very expensive.",
            "common_mistake": "Conflating in-vitro neuroprotection with clinical cognitive enhancement",
            "pro_tip": "Humanin and MOTS-C are both mitochondrial peptides. Research is promising but at discovery stage, not therapeutic stage."
        },
    },
    "ss-31": {
        "dose": {"min_mcg": 5000, "max_mcg": 40000},
        "frequency": "1x daily or per clinical protocol",
        "routes": ["subcutaneous", "intravenous"],
        "vials": [5, 40],
        "community": {
            "top_positive_use": "Mitochondrial-targeted peptide — FDA-approved Sept 2025 for Barth syndrome. Cardiolipin stabilization.",
            "top_negative_report": "Extremely expensive. Mostly studied via IV infusion. SubQ bioavailability uncertain.",
            "common_mistake": "Expecting oral bioavailability — SS-31 must be injected (SubQ or IV)",
            "pro_tip": "The only mitochondrial peptide with FDA approval. If you're interested in mito-targeted peptides, this has the strongest evidence base."
        },
    },
    "retatrutide": {
        "dose": {"min_mcg": 1000, "max_mcg": 12000},
        "frequency": "1x weekly",
        "routes": ["subcutaneous"],
        "vials": [5, 10, 15],
        "community": {
            "top_positive_use": "Dramatic weight loss exceeding semaglutide/tirzepatide results",
            "top_negative_report": "Sleep disruption (~8% of users), emotional blunting, suspected fake/underdosed products",
            "common_mistake": "Starting at high dose — titrate from 1mg. Product authenticity is a major concern with gray market sources",
            "pro_tip": "If sleep disruption occurs, it's likely dose-dependent and may resolve at lower doses. Overnight glucose dips triggering cortisol is the suspected mechanism."
        },
    },
    "orforglipron": {
        "dose": {"min_mcg": 3000, "max_mcg": 45000},
        "frequency": "1x daily (oral)",
        "routes": ["oral"],
        "vials": [],
        "community": {
            "top_positive_use": "Oral GLP-1 — no injections. Phase 2: 14.7% weight loss. Phase 3 ongoing by Eli Lilly.",
            "top_negative_report": "Not yet approved. GI side effects similar to injectable GLP-1s. Limited real-world data.",
            "common_mistake": "Treating gray market orforglipron as equivalent to the clinical formulation — bioavailability depends heavily on formulation",
            "pro_tip": "First non-peptide oral GLP-1 agonist. If Phase 3 succeeds, this will be game-changing for the GLP-1 space."
        },
    },
    "survodutide": {
        "dose": {"min_mcg": 600, "max_mcg": 4800},
        "frequency": "1x weekly",
        "routes": ["subcutaneous"],
        "vials": [5, 10],
        "community": {
            "top_positive_use": "Dual GLP-1/glucagon agonist — Phase 2 showed 18.7% weight loss + liver fat reduction (NAFLD potential)",
            "top_negative_report": "Not yet approved. Standard GLP-1 GI side effects. Less data than tirzepatide.",
            "common_mistake": "Confusing with survodutide — currently only available through clinical trials or gray market",
            "pro_tip": "Interesting for NASH/NAFLD patients where the glucagon component may provide liver-specific benefits beyond weight loss."
        },
    },
    "dulaglutide": {
        "dose": {"min_mcg": 750, "max_mcg": 4500},
        "frequency": "1x weekly",
        "routes": ["subcutaneous"],
        "vials": [],
        "community": {
            "top_positive_use": "FDA-approved GLP-1 agonist (Trulicity). Auto-injector pen — easiest GLP-1 to self-administer.",
            "top_negative_report": "Less weight loss than semaglutide or tirzepatide. Standard GLP-1 GI side effects.",
            "common_mistake": "Choosing dulaglutide over semaglutide for weight loss — semaglutide has superior efficacy data for obesity",
            "pro_tip": "Best for patients who want the simplest possible injection experience. The auto-injector pen is very user-friendly."
        },
    },
    "triptorelin": {
        "dose": {"min_mcg": 100, "max_mcg": 100},
        "frequency": "Single dose or per protocol",
        "routes": ["intramuscular"],
        "vials": [],
        "community": {
            "top_positive_use": "HPTA restart after steroid cycle — single 100mcg dose is common PCT protocol",
            "top_negative_report": "CONTINUOUS use causes chemical castration (used clinically for prostate cancer). Must be pulsed, not continuous.",
            "common_mistake": "Using repeated doses — a single 100mcg IM injection is the standard PCT protocol. Repeated dosing SUPPRESSES testosterone.",
            "pro_tip": "GnRH agonist. A single pulse stimulates LH/FSH. Continuous exposure suppresses them. This is NOT a peptide to cycle."
        },
    },
    "kisspeptin-10": {
        "dose": {"min_mcg": 1000, "max_mcg": 10000},
        "frequency": "As needed or per research protocol",
        "routes": ["subcutaneous", "intravenous"],
        "vials": [5],
        "community": {
            "top_positive_use": "Upstream regulator of GnRH — stimulates natural testosterone production via hypothalamic kisspeptin neurons",
            "top_negative_report": "Very short half-life (~28 min). Limited human data for off-label uses. Expensive.",
            "common_mistake": "Expecting sustained testosterone elevation — kisspeptin-10 has a very short half-life, effects are transient",
            "pro_tip": "Interesting research compound for understanding HPG axis. Not practical for ongoing testosterone optimization due to short half-life."
        },
    },
    "melanotan-ii": {
        "dose": {"min_mcg": 250, "max_mcg": 1000},
        "frequency": "Loading: 1x daily for 1-2 weeks, then 1-2x weekly maintenance",
        "routes": ["subcutaneous"],
        "vials": [10],
        "community": {
            "top_positive_use": "Tanning without UV exposure — also increases libido (melanocortin agonist)",
            "top_negative_report": "Nausea (very common), facial flushing, mole darkening (raises melanoma screening concerns), spontaneous erections",
            "common_mistake": "Not getting a full skin check before starting — MT-II darkens moles and can mask melanoma changes",
            "pro_tip": "Start at 250mcg to assess nausea tolerance. ALWAYS get a baseline mole check. Darkened moles are expected but need monitoring."
        },
        "fingerprint": [
            {"symptom": "nausea", "frequency": "very_common", "severity": "moderate", "mechanism": "Melanocortin receptor activation", "onset_days": {"min": 0, "max": 0}},
            {"symptom": "facial_flushing", "frequency": "very_common", "severity": "mild", "mechanism": "Vasodilation from MC receptor activation", "onset_days": {"min": 0, "max": 0}},
            {"symptom": "mole_darkening", "frequency": "very_common", "severity": "moderate", "mechanism": "MC1R activation increases melanin production in nevi", "onset_days": {"min": 7, "max": 30}},
            {"symptom": "spontaneous_erections", "frequency": "common", "severity": "mild", "mechanism": "MC4R activation in hypothalamus", "onset_days": {"min": 0, "max": 1}},
        ],
    },
    "mt-1": {
        "dose": {"min_mcg": 1000, "max_mcg": 16000},
        "frequency": "Per protocol — FDA-approved as Scenesse implant",
        "routes": ["subcutaneous"],
        "vials": [10],
        "community": {
            "top_positive_use": "FDA-approved (as afamelanotide/Scenesse) for EPP — photoprotective tanning",
            "top_negative_report": "Less potent than MT-II. Nausea, headache. Implant form only in approved use.",
            "common_mistake": "Confusing MT-I with MT-II — MT-I is more selective (less sexual side effects) but weaker tanning effect",
            "pro_tip": "If you want tanning without the sexual side effects of MT-II, MT-I is the cleaner option."
        },
    },
    "glutathione": {
        "dose": {"min_mcg": 200000, "max_mcg": 600000},
        "frequency": "1-3x weekly (IV) or daily (oral)",
        "routes": ["intravenous", "oral", "subcutaneous"],
        "vials": [200, 600],
        "community": {
            "top_positive_use": "Master antioxidant — supports detoxification, immune function, skin brightening",
            "top_negative_report": "Oral bioavailability is poor. IV is expensive. Skin lightening effect is controversial.",
            "common_mistake": "Taking oral glutathione expecting same effect as IV — oral glutathione is largely degraded in the gut",
            "pro_tip": "Liposomal oral forms have better absorption. IV is most effective but expensive. NAC (N-acetyl cysteine) is a cheaper precursor."
        },
    },
    "nad-plus": {
        "dose": {"min_mcg": 100000, "max_mcg": 500000},
        "frequency": "1-2x weekly (IV) or daily (SubQ/oral precursor)",
        "routes": ["intravenous", "subcutaneous", "oral"],
        "vials": [100, 250, 500],
        "community": {
            "top_positive_use": "Anti-aging and cellular energy — supports sirtuins, DNA repair, mitochondrial function",
            "top_negative_report": "IV infusions cause intense flushing, nausea, chest tightness. Very expensive. Oral NAD+ has poor bioavailability.",
            "common_mistake": "Choosing expensive IV NAD+ over oral precursors (NMN, NR) which have better evidence and are vastly cheaper",
            "pro_tip": "Most longevity researchers recommend NMN or NR (oral precursors) over direct NAD+ supplementation. Save IV NAD+ for acute recovery."
        },
    },
    "aicar": {
        "dose": {"min_mcg": 150000, "max_mcg": 500000},
        "frequency": "1x daily for limited cycles",
        "routes": ["subcutaneous"],
        "vials": [50],
        "community": {
            "top_positive_use": "Exercise mimetic — AMPK activator. Increases endurance capacity in animal studies.",
            "top_negative_report": "Zero human efficacy data for performance. WADA banned substance. Very expensive. Potential cardiac risk.",
            "common_mistake": "Using as a replacement for exercise — AICAR is a WADA-banned research compound, not a fitness supplement",
            "pro_tip": "Acadesine (the clinical name) was studied for cardiac surgery, not performance. The 'exercise pill' hype comes from a single 2008 mouse study."
        },
    },
}


def enrich_compound(compound: dict, chembl: dict, ctgov: list, side_effects: list, pubchem_props: dict) -> dict:
    """Enrich compound with API data and curated knowledge."""
    cid = compound["id"]
    curated = CURATED_DATA.get(cid, {})

    # Update mechanism from ChEMBL if available
    if chembl.get("mechanisms"):
        mech_texts = [m["mechanism_of_action"] for m in chembl["mechanisms"] if m.get("mechanism_of_action")]
        if mech_texts:
            compound["mechanism_summary"] = ". ".join(mech_texts[:2]) + "."

    # Update dosing from curated data or trials
    if curated.get("dose"):
        compound["administration"]["typical_dose"] = curated["dose"]
    if curated.get("frequency"):
        compound["administration"]["frequency"] = curated["frequency"]
    if curated.get("routes"):
        compound["administration"]["routes"] = curated["routes"]
    if curated.get("vials"):
        compound["administration"]["common_vial_sizes_mg"] = curated["vials"]

    # Extract dosing from clinical trials if no curated data
    if not curated.get("dose") and ctgov:
        for trial in ctgov:
            for d in trial.get("dosing_info", []):
                # Try to extract dose numbers
                mg_match = re.search(r'(\d+(?:\.\d+)?)\s*mg', d, re.I)
                mcg_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:mcg|µg)', d, re.I)
                if mcg_match:
                    val = float(mcg_match.group(1))
                    compound["administration"]["typical_dose"] = {"min_mcg": val, "max_mcg": val}
                    break
                elif mg_match:
                    val = float(mg_match.group(1)) * 1000
                    compound["administration"]["typical_dose"] = {"min_mcg": val, "max_mcg": val}
                    break

    # Update regulatory from ChEMBL max_phase
    if chembl.get("max_phase"):
        try:
            phase = int(chembl["max_phase"])
        except (ValueError, TypeError):
            phase = 0
        if phase >= 4:
            compound["regulatory"]["fda_status"] = "approved"
            compound["regulatory"]["fda_category"] = "prescription"
        elif phase >= 2:
            compound["regulatory"]["fda_category"] = "investigational"
        compound["regulatory"]["note"] = f"ChEMBL max phase: {phase}. " + compound["regulatory"].get("note", "")

    # Update community insights from curated data
    if curated.get("community"):
        compound["community_insights"] = curated["community"]
    elif compound["community_insights"]["top_positive_use"].startswith("Pending"):
        # Generate from available data
        if ctgov:
            phases = []
            for t in ctgov:
                phases.extend(t.get("phase", []))
            trial_info = f"{len(ctgov)} clinical trials found"
            if phases:
                trial_info += f" ({', '.join(set(phases))})"
            compound["community_insights"]["top_positive_use"] = trial_info
        if side_effects:
            compound["community_insights"]["top_negative_report"] = f"See literature: {side_effects[0][:120]}"

    return compound


def build_fingerprint(compound_id: str, curated: dict, side_effects: list) -> dict:
    """Build or enhance fingerprint entry."""
    fp = {
        "compound_id": compound_id,
        "watch_for": curated.get("fingerprint", []),
        "critical_alerts": [],
        "dose_dependent": bool(curated.get("fingerprint")),
        "context_modifiers": [],
    }
    return fp


def main():
    with open(COMPOUNDS_FILE) as f:
        data = json.load(f)

    with open(FINGERPRINTS_FILE) as f:
        fp_data = json.load(f)

    with open(RECONSTITUTION_FILE) as f:
        recon_data = json.load(f)

    # Index fingerprints by compound_id
    fp_index = {fp["compound_id"]: i for i, fp in enumerate(fp_data["fingerprints"])}

    # Only process compounds that still need enrichment
    to_enrich = []
    for i, c in enumerate(data["compounds"]):
        needs_work = (
            c["administration"]["typical_dose"]["min_mcg"] == 0
            or c["community_insights"]["top_positive_use"].startswith("Pending")
            or c["mechanism_summary"].startswith("See literature:")
            or c["mechanism_summary"].startswith("Mechanism of action not")
        )
        if needs_work:
            to_enrich.append((i, c))

    print(f"Compounds needing enrichment: {len(to_enrich)}/{len(data['compounds'])}")

    for idx, (i, compound) in enumerate(to_enrich, 1):
        name = compound["name"]
        cid = compound["id"]
        print(f"\n[{idx}/{len(to_enrich)}] Enriching: {name}")

        # ChEMBL lookup
        clean_name = re.sub(r'\s*\([^)]*\)', '', name).strip()
        print(f"  → ChEMBL: {clean_name}")
        chembl = chembl_search(clean_name)
        time.sleep(0.4)

        # ClinicalTrials.gov
        print(f"  → ClinicalTrials.gov: {clean_name}")
        ctgov = ctgov_search(clean_name)
        time.sleep(0.4)

        # PubMed side effects
        print(f"  → PubMed side effects: {clean_name}")
        side_effects = pubmed_side_effects(clean_name)
        time.sleep(0.4)

        # PubChem properties
        pubchem_props = {}
        if compound.get("pubchem_cid", 0) > 0:
            pubchem_props = pubchem_properties(compound["pubchem_cid"])
            time.sleep(0.3)

        # Enrich
        data["compounds"][i] = enrich_compound(compound, chembl, ctgov, side_effects, pubchem_props)

        # Update fingerprint if we have curated data
        curated = CURATED_DATA.get(cid, {})
        if curated.get("fingerprint") and cid in fp_index:
            fp_data["fingerprints"][fp_index[cid]] = build_fingerprint(cid, curated, side_effects)

        # Update reconstitution if we have vial data
        if curated.get("vials") and cid not in recon_data.get("compounds", {}):
            routes = curated.get("routes", compound["administration"]["routes"])
            if "subcutaneous" in routes or "intramuscular" in routes:
                recon_data.setdefault("compounds", {})[cid] = {
                    "common_vial_sizes_mg": curated["vials"],
                    "recommended_solvent": "bacteriostatic_water",
                    "recommended_volume_ml": [1, 2],
                    "notes": f"Reconstitution data for {name}.",
                }

        # Write incrementally every 5
        if idx % 5 == 0 or idx == len(to_enrich):
            with open(COMPOUNDS_FILE, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            with open(FINGERPRINTS_FILE, "w") as f:
                json.dump(fp_data, f, indent=2, ensure_ascii=False)
            with open(RECONSTITUTION_FILE, "w") as f:
                json.dump(recon_data, f, indent=2, ensure_ascii=False)

        print(f"  ✓ {name} — dose: {compound['administration']['typical_dose']} — trials: {len(ctgov)}")

        # Progress log every 10
        if idx % 10 == 0:
            ts = datetime.now(timezone.utc).isoformat()
            with open(LOG_FILE, "a") as f:
                f.write(f"[{ts}] {idx}/{len(to_enrich)} enriched. Last: {name}\n")

    # Final write
    with open(COMPOUNDS_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    with open(FINGERPRINTS_FILE, "w") as f:
        json.dump(fp_data, f, indent=2, ensure_ascii=False)
    with open(RECONSTITUTION_FILE, "w") as f:
        json.dump(recon_data, f, indent=2, ensure_ascii=False)

    # Stats
    enriched_dose = sum(1 for c in data["compounds"] if c["administration"]["typical_dose"]["min_mcg"] > 0)
    enriched_community = sum(1 for c in data["compounds"] if not c["community_insights"]["top_positive_use"].startswith("Pending"))
    enriched_mechanism = sum(1 for c in data["compounds"] if not c["mechanism_summary"].startswith("See literature:") and not c["mechanism_summary"].startswith("Mechanism of action not"))
    recon_count = len(recon_data.get("compounds", {}))

    ts = datetime.now(timezone.utc).isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] DONE. Dosing: {enriched_dose}/102, Community: {enriched_community}/102, Mechanism: {enriched_mechanism}/102, Reconstitution: {recon_count}\n")

    print(f"\n{'='*60}")
    print(f"Deep hydration complete.")
    print(f"  Dosing data:       {enriched_dose}/102")
    print(f"  Community insights: {enriched_community}/102")
    print(f"  Mechanism detail:  {enriched_mechanism}/102")
    print(f"  Reconstitution:    {recon_count} entries")


if __name__ == "__main__":
    main()
