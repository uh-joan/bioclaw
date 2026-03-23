#!/usr/bin/env python3
"""
Hydrate peptigotchi compound database from 12 → 101 compounds.

Reads tpl-seed.json for the target list, skips compounds already in compounds.json,
and writes new entries incrementally after each compound is processed.

Usage:
  # Via NanoClaw container agent (recommended — has MCP access):
  Send this as a task to the main group:
    "Run the compound hydration task: read container/skills/peptigotchi/knowledge/hydrate-compounds.md and execute it"

  # Or run standalone with public APIs (no MCP required):
  python3 scripts/hydrate-peptides.py

The standalone mode uses PubChem REST API + PubMed E-utilities (free, no key needed)
as a fallback when MCP servers aren't available.
"""

import json
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from datetime import datetime, timezone

KNOWLEDGE_DIR = Path(__file__).parent.parent / "container" / "skills" / "peptigotchi" / "knowledge"
COMPOUNDS_FILE = KNOWLEDGE_DIR / "compounds.json"
FINGERPRINTS_FILE = KNOWLEDGE_DIR / "fingerprints.json"
RECONSTITUTION_FILE = KNOWLEDGE_DIR / "reconstitution.json"
SEED_FILE = KNOWLEDGE_DIR / "tpl-seed.json"
LOG_FILE = KNOWLEDGE_DIR / "hydration-progress.log"

# Category mapping from TPL → peptigotchi
CATEGORY_MAP = {
    "weight_loss": "weight_loss",
    "tissue_repair": "healing",
    "growth_hormone": "gh_secretagogue",
    "cognitive": "nootropic",
    "skin_hair": "cosmetic",
    "sexual_function": "sexual_health",
    "anti_aging": "anti_aging",
    "immune": "immune",
    "sleep_stress": "sleep_stress",
}

# Known GLP-1 agonists that should be categorized as "glp1" instead of "weight_loss"
GLP1_COMPOUNDS = {
    "semaglutide", "tirzepatide", "liraglutide", "retatrutide", "orforglipron",
    "survodutide", "cagrilintide", "cagrilintide-semaglutide", "mazdutide",
    "dulaglutide", "eloralintide",
}


def api_get(url: str, retries: int = 3) -> dict | list | None:
    """Fetch JSON from a URL with retries."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "NanoClaw-Hydrator/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError) as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  ⚠ API error for {url}: {e}", file=sys.stderr)
                return None


def pubchem_lookup(name: str) -> dict:
    """Look up compound on PubChem REST API."""
    encoded = urllib.parse.quote(name)
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{encoded}/JSON"
    data = api_get(url)
    if not data:
        return {"cid": 0, "aliases": [], "formula": ""}

    try:
        compound = data["PC_Compounds"][0]
        cid = compound.get("id", {}).get("id", {}).get("cid", 0)
    except (KeyError, IndexError):
        return {"cid": 0, "aliases": [], "formula": ""}

    # Get synonyms
    syn_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/synonyms/JSON"
    syn_data = api_get(syn_url)
    aliases = []
    if syn_data:
        try:
            all_syns = syn_data["InformationList"]["Information"][0]["Synonym"]
            # Take first 5 non-trivial synonyms
            aliases = [s for s in all_syns[:10] if s.lower() != name.lower()][:5]
        except (KeyError, IndexError):
            pass

    return {"cid": cid, "aliases": aliases, "formula": ""}


def pubmed_search(query: str, max_results: int = 5) -> list[dict]:
    """Search PubMed via E-utilities."""
    encoded = urllib.parse.quote(query)
    search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={encoded}&retmax={max_results}&retmode=json"
    search_data = api_get(search_url)
    if not search_data:
        return []

    try:
        ids = search_data["esearchresult"]["idlist"]
    except KeyError:
        return []

    if not ids:
        return []

    # Fetch summaries
    id_str = ",".join(ids)
    summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={id_str}&retmode=json"
    summary_data = api_get(summary_url)
    if not summary_data:
        return []

    results = []
    try:
        for pmid in ids:
            article = summary_data["result"].get(pmid, {})
            results.append({
                "pmid": pmid,
                "title": article.get("title", ""),
                "source": article.get("source", ""),
                "pubdate": article.get("pubdate", ""),
            })
    except (KeyError, TypeError):
        pass

    return results


def determine_evidence_grade(name: str, pubmed_results: list, seed_tiers: dict) -> tuple[str, str]:
    """Determine evidence grade based on PubMed results and TPL tier seeding."""
    compound_id = name.lower().replace(" ", "-").replace("(", "").replace(")", "")

    # Check TPL tier seeding
    tier = None
    for t, compounds in seed_tiers.items():
        if compound_id in compounds or name.lower() in [c.lower() for c in compounds]:
            tier = t
            break

    # Count clinical-relevant papers
    clinical_keywords = ["clinical trial", "randomized", "phase", "rct", "human", "patients", "subjects"]
    clinical_count = sum(1 for r in pubmed_results if any(k in r.get("title", "").lower() for k in clinical_keywords))
    total = len(pubmed_results)

    if tier == "tier_1_fda_approved":
        grade = "green"
        detail = f"FDA-approved. {total} PubMed results found, {clinical_count} clinical studies."
    elif tier == "tier_2_late_stage":
        grade = "yellow"
        detail = f"Late-stage clinical development. {total} PubMed results, {clinical_count} clinical studies. Phase 2/3 data available."
    elif tier == "tier_3_limited_human":
        grade = "yellow"
        detail = f"Limited human data. {total} PubMed results, {clinical_count} clinical studies. Mostly animal/preclinical evidence."
    elif tier == "tier_4_no_human_data":
        grade = "red"
        detail = f"No human clinical trials. {total} PubMed results. Evidence is preclinical only."
    elif clinical_count >= 3:
        grade = "yellow"
        detail = f"{total} PubMed results, {clinical_count} clinical studies. Some human evidence exists."
    elif total >= 5:
        grade = "yellow"
        detail = f"{total} PubMed results but limited clinical data. Mostly preclinical/mechanistic."
    else:
        grade = "red"
        detail = f"Minimal published evidence. {total} PubMed results found."

    return grade, detail


def build_compound_entry(seed: dict, seed_tiers: dict) -> dict:
    """Build a full compound entry from seed data + public API lookups."""
    name = seed["name"]
    compound_id = seed["id"]
    tpl_cat = seed.get("tpl_category", "")

    print(f"  → PubChem lookup: {name}")
    pc = pubchem_lookup(name)
    time.sleep(0.4)  # Rate limit

    print(f"  → PubMed search: {name}")
    pm_mechanism = pubmed_search(f"{name} mechanism of action peptide", max_results=3)
    time.sleep(0.4)
    pm_clinical = pubmed_search(f"{name} clinical trial OR human study", max_results=5)
    time.sleep(0.4)

    grade, detail = determine_evidence_grade(name, pm_mechanism + pm_clinical, seed_tiers)

    # Determine category
    if compound_id in GLP1_COMPOUNDS:
        category = "glp1"
    else:
        category = CATEGORY_MAP.get(tpl_cat, tpl_cat)

    # Build mechanism summary from paper titles
    mechanism = "Mechanism of action not well characterized in available databases."
    if pm_mechanism:
        titles = "; ".join(r["title"][:80] for r in pm_mechanism[:2] if r.get("title"))
        if titles:
            mechanism = f"See literature: {titles}"

    # Determine administration defaults by category
    routes_map = {
        "cosmetic": ["topical"],
        "nootropic": ["intranasal", "subcutaneous"],
        "glp1": ["subcutaneous"],
        "gh_secretagogue": ["subcutaneous"],
        "healing": ["subcutaneous", "intramuscular"],
        "immune": ["subcutaneous"],
        "sexual_health": ["subcutaneous"],
        "anti_aging": ["subcutaneous"],
        "sleep_stress": ["subcutaneous", "intranasal"],
        "weight_loss": ["subcutaneous"],
    }

    entry = {
        "id": compound_id,
        "name": name,
        "aliases": pc["aliases"][:5] if pc["aliases"] else [],
        "pubchem_cid": pc["cid"],
        "category": category,
        "administration": {
            "routes": routes_map.get(category, ["subcutaneous"]),
            "typical_dose": {"min_mcg": 0, "max_mcg": 0},
            "frequency": "See literature — dosing data pending MCP hydration",
            "common_vial_sizes_mg": [],
            "reconstitution": {
                "solvent": "bacteriostatic_water",
                "typical_volume_ml": 2,
                "storage_days_refrigerated": 28,
            },
        },
        "mechanism_summary": mechanism,
        "evidence": {
            "grade": grade,
            "detail": detail,
        },
        "regulatory": {
            "fda_status": "approved" if grade == "green" else "not_approved",
            "fda_category": "prescription" if grade == "green" else "research_chemical",
            "note": "Hydrated via public APIs. Run MCP hydration for full regulatory detail.",
            "last_updated": "2026-03",
        },
        "community_insights": {
            "top_positive_use": "Pending MCP hydration — community data not available via public APIs",
            "top_negative_report": "Pending MCP hydration",
            "common_mistake": "Pending MCP hydration",
            "pro_tip": "Pending MCP hydration",
        },
    }

    return entry


def build_fingerprint_stub(compound_id: str) -> dict:
    """Create a minimal fingerprint entry for new compounds."""
    return {
        "compound_id": compound_id,
        "watch_for": [],
        "critical_alerts": [],
        "dose_dependent": False,
        "context_modifiers": [],
    }


def main():
    # Load seed
    with open(SEED_FILE) as f:
        seed = json.load(f)

    # Load existing compounds
    with open(COMPOUNDS_FILE) as f:
        compounds_data = json.load(f)

    existing_ids = {c["id"] for c in compounds_data["compounds"]}
    seed_tiers = seed.get("evidence_tiers", {})

    # Load existing fingerprints
    with open(FINGERPRINTS_FILE) as f:
        fingerprints_data = json.load(f)
    existing_fp_ids = {fp["compound_id"] for fp in fingerprints_data["fingerprints"]}

    # Determine which compounds need hydration
    to_hydrate = [c for c in seed["compounds"] if c["id"] not in existing_ids]
    print(f"Compounds to hydrate: {len(to_hydrate)} (skipping {len(existing_ids)} existing)")

    # Sort by tier priority
    tier_order = {}
    for priority, (tier_name, ids) in enumerate(seed_tiers.items()):
        for cid in ids:
            tier_order[cid] = priority
    to_hydrate.sort(key=lambda c: tier_order.get(c["id"], 99))

    errors = 0
    for i, seed_compound in enumerate(to_hydrate, 1):
        print(f"\n[{i}/{len(to_hydrate)}] Hydrating: {seed_compound['name']}")
        try:
            entry = build_compound_entry(seed_compound, seed_tiers)
            compounds_data["compounds"].append(entry)

            # Write incrementally
            with open(COMPOUNDS_FILE, "w") as f:
                json.dump(compounds_data, f, indent=2, ensure_ascii=False)

            # Add fingerprint stub if missing
            if seed_compound["id"] not in existing_fp_ids:
                fingerprints_data["fingerprints"].append(build_fingerprint_stub(seed_compound["id"]))
                with open(FINGERPRINTS_FILE, "w") as f:
                    json.dump(fingerprints_data, f, indent=2, ensure_ascii=False)
                existing_fp_ids.add(seed_compound["id"])

            grade = entry["evidence"]["grade"]
            cid = entry["pubchem_cid"]
            print(f"  ✓ {seed_compound['name']} — {grade} — CID:{cid}")

        except Exception as e:
            errors += 1
            print(f"  ✗ Error: {e}", file=sys.stderr)

        # Progress log every 10
        if i % 10 == 0:
            ts = datetime.now(timezone.utc).isoformat()
            with open(LOG_FILE, "a") as f:
                f.write(f"[{ts}] {i}/{len(to_hydrate)} compounds hydrated. Last: {seed_compound['name']}. Errors: {errors}\n")

    # Final log
    ts = datetime.now(timezone.utc).isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] DONE. {len(to_hydrate)}/{len(to_hydrate)} compounds hydrated. Errors: {errors}\n")

    total = len(compounds_data["compounds"])
    print(f"\n{'='*60}")
    print(f"Done. compounds.json now has {total} compounds ({len(to_hydrate)} new, {errors} errors)")
    print(f"Next: run MCP hydration via NanoClaw agent for full dosing, interactions, and community data")
    print(f"  → Send to main group: 'Read hydrate-compounds.md and execute the full MCP pipeline'")


if __name__ == "__main__":
    main()
