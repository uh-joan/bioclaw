#!/usr/bin/env python3
"""
Scale up trial collection to 500+ using CT.gov search results directly.

Key insight: search() returns title, NCT ID, phase, enrollment, sponsor, status
all in one response. No need for get_study() for basic metadata. Drug name is
extracted from the title. Target gene is resolved via ChEMBL mechanism lookup.
"""
import sys, os, csv, re, time, json
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.environ['MCP_CONFIG_FILE'] = os.path.join(os.path.dirname(__file__), 'mcp-config.json')

import pandas as pd
from collect import COLUMNS

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'trials_raw.csv')

# Dynamic cache — populated by ChEMBL lookups, no hardcoded entries
DRUG_TARGET_CACHE = {}
CACHE_FILE = os.path.join(os.path.dirname(__file__), 'data', 'drug_target_cache.json')

def _load_cache():
    global DRUG_TARGET_CACHE
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            DRUG_TARGET_CACHE = json.load(f)
        print(f"Loaded {len(DRUG_TARGET_CACHE)} cached drug→target mappings")

def _save_cache():
    with open(CACHE_FILE, 'w') as f:
        json.dump(DRUG_TARGET_CACHE, f, indent=2)

_load_cache()


def extract_drug_from_title(title: str) -> str:
    """Extract likely drug name from a trial title."""
    title_lower = title.lower()

    # Check known drugs first
    for drug in DRUG_TARGET_CACHE:
        if drug in title_lower:
            return drug

    # Common patterns: "Study of DRUG", "DRUG versus", "DRUG in", "DRUG for"
    patterns = [
        r'(?:study|trial|evaluation|efficacy|safety)\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        r'^([A-Z][a-z]{3,}(?:mab|nib|lib|sib|tide|stat|pril|olol|azole|mycin|cillin|ximab|zumab|umab))',
        r'([A-Z][a-z]+(?:mab|nib|lib|sib|tide|stat|pril|olol|azole|mycin|cillin|ximab|zumab|umab))',
    ]
    for pat in patterns:
        m = re.search(pat, title, re.IGNORECASE)
        if m:
            return m.group(1).lower().strip()

    return ''


def resolve_target(drug: str) -> str:
    """Get target gene for a drug. Uses cache first, then ChEMBL.

    Chain: drug → compound_search → get_mechanism → target_chembl_id → target_search → gene symbol
    """
    if drug in DRUG_TARGET_CACHE:
        return DRUG_TARGET_CACHE[drug]

    try:
        from mcp.servers.chembl_mcp import compound_search, get_mechanism, target_search
        r = compound_search(query=drug, limit=1)
        mols = r.get('molecules', [])
        if not mols:
            DRUG_TARGET_CACHE[drug] = ''
            return ''

        chembl_id = mols[0].get('molecule_chembl_id', '')
        if not chembl_id:
            return ''

        mech = get_mechanism(chembl_id=chembl_id)
        mechs = mech.get('mechanisms', [])
        if not mechs:
            DRUG_TARGET_CACHE[drug] = ''
            return ''

        target_chembl_id = mechs[0].get('target_chembl_id', '')
        if not target_chembl_id:
            return ''

        # Resolve target ChEMBL ID → gene symbol
        t = target_search(query=target_chembl_id, limit=1)
        targets = t.get('targets', [])
        if targets:
            components = targets[0].get('components', [])
            if components:
                synonyms = components[0].get('synonyms', [])
                # Gene symbols are short uppercase strings
                gene = next((s for s in synonyms if s.isupper() and len(s) <= 10 and s.isalpha()), '')
                if not gene and synonyms:
                    gene = synonyms[0]
                if gene:
                    DRUG_TARGET_CACHE[drug] = gene
                    _save_cache()
                    return gene
    except Exception as e:
        pass

    DRUG_TARGET_CACHE[drug] = ''
    return ''


def parse_search_block(block: str) -> dict:
    """Parse one trial block from CT.gov search markdown."""
    out = {}

    m = re.search(r'(NCT\d{8})', block)
    if m: out['nct_id'] = m.group(1)

    m = re.search(r'\*\*Title:\*\*\s*(.+)', block)
    if m: out['title'] = m.group(1).strip()

    m = re.search(r'\*\*Status:\*\*\s*(\w+)', block)
    if m: out['status'] = m.group(1).strip()

    m = re.search(r'\*\*Phase:\*\*\s*(.+)', block)
    if m:
        phases = re.findall(r'(\d)', m.group(1))
        if phases: out['phase'] = str(max(int(p) for p in phases))

    m = re.search(r'\*\*Enrollment:\*\*\s*(\d[\d,]*)', block)
    if m: out['enrollment'] = m.group(1).replace(',', '')

    m = re.search(r'\*\*Conditions:\*\*\s*(.+)', block)
    if m: out['condition'] = m.group(1).strip()

    m = re.search(r'\*\*Lead Sponsor:\*\*\s*(.+)', block)
    if m:
        raw = m.group(1).strip()
        out['lead_sponsor'] = re.sub(r'\s*\(.*\)', '', raw).strip()
        if any(x in raw.lower() for x in ['pharma', 'inc', 'ltd', 'llc', 'corp', 'gmbh', 'sa ', 'ag ', 'therapeutics', 'oncology', 'biopharm']):
            out['sponsor_type'] = 'Industry'
        elif 'nih' in raw.lower() or 'national' in raw.lower():
            out['sponsor_type'] = 'NIH'
        else:
            out['sponsor_type'] = 'Other'

    m = re.search(r'\*\*Study Type:\*\*\s*(.+)', block)
    if m: out['study_type'] = m.group(1).strip()

    return out


def infer_indication_area(condition: str) -> str:
    c = condition.lower()
    if any(x in c for x in ['cancer', 'tumor', 'carcinoma', 'melanoma', 'leukemia', 'lymphoma', 'sarcoma', 'myeloma', 'glioblastoma', 'neuroblastoma', 'mesothelioma']):
        return 'oncology'
    if any(x in c for x in ['alzheimer', 'parkinson', 'epilepsy', 'depression', 'schizophrenia', 'sclerosis', 'als', 'huntington', 'migraine', 'neuropath']):
        return 'cns'
    if any(x in c for x in ['diabetes', 'obesity', 'nash', 'lipid', 'metabolic']):
        return 'metabolic'
    if any(x in c for x in ['arthritis', 'lupus', 'psoriasis', 'crohn', 'colitis', 'dermatitis', 'spondylitis']):
        return 'immunology'
    if any(x in c for x in ['heart', 'cardiac', 'hypertension', 'atrial', 'stroke', 'thrombosis', 'embolism']):
        return 'cardiovascular'
    if any(x in c for x in ['asthma', 'copd', 'pulmonary', 'respiratory', 'fibrosis']):
        return 'respiratory'
    if any(x in c for x in ['hiv', 'hepatitis', 'influenza', 'covid', 'infection', 'tuberculosis', 'malaria']):
        return 'infectious'
    return 'other'


SEARCHES = [
    # (condition, status, label, pageSize)
    # Successes
    ("breast cancer", "COMPLETED", 1, 50),
    ("lung cancer", "COMPLETED", 1, 50),
    ("melanoma", "COMPLETED", 1, 30),
    ("colorectal cancer", "COMPLETED", 1, 30),
    ("prostate cancer", "COMPLETED", 1, 30),
    ("renal cell carcinoma", "COMPLETED", 1, 20),
    ("ovarian cancer", "COMPLETED", 1, 20),
    ("lymphoma", "COMPLETED", 1, 30),
    ("leukemia", "COMPLETED", 1, 30),
    ("multiple myeloma", "COMPLETED", 1, 20),
    ("hepatocellular carcinoma", "COMPLETED", 1, 20),
    ("gastric cancer", "COMPLETED", 1, 20),
    ("head and neck cancer", "COMPLETED", 1, 15),
    ("pancreatic cancer", "COMPLETED", 1, 15),
    ("bladder cancer", "COMPLETED", 1, 15),
    ("thyroid cancer", "COMPLETED", 1, 10),
    ("type 2 diabetes", "COMPLETED", 1, 30),
    ("rheumatoid arthritis", "COMPLETED", 1, 20),
    ("psoriasis", "COMPLETED", 1, 15),
    ("crohn's disease", "COMPLETED", 1, 15),
    ("ulcerative colitis", "COMPLETED", 1, 15),
    ("atopic dermatitis", "COMPLETED", 1, 10),
    ("multiple sclerosis", "COMPLETED", 1, 15),
    ("heart failure", "COMPLETED", 1, 20),
    ("asthma", "COMPLETED", 1, 15),
    ("COPD", "COMPLETED", 1, 15),
    ("HIV", "COMPLETED", 1, 15),
    ("depression", "COMPLETED", 1, 15),
    ("Alzheimer", "COMPLETED", 1, 15),
    ("migraine", "COMPLETED", 1, 10),
    # Failures
    ("breast cancer", "TERMINATED", 0, 40),
    ("lung cancer", "TERMINATED", 0, 40),
    ("melanoma", "TERMINATED", 0, 20),
    ("colorectal cancer", "TERMINATED", 0, 20),
    ("prostate cancer", "TERMINATED", 0, 20),
    ("ovarian cancer", "TERMINATED", 0, 15),
    ("pancreatic cancer", "TERMINATED", 0, 20),
    ("glioblastoma", "TERMINATED", 0, 15),
    ("leukemia", "TERMINATED", 0, 15),
    ("lymphoma", "TERMINATED", 0, 15),
    ("type 2 diabetes", "TERMINATED", 0, 15),
    ("Alzheimer", "TERMINATED", 0, 20),
    ("depression", "TERMINATED", 0, 10),
    ("Parkinson", "TERMINATED", 0, 10),
    ("rheumatoid arthritis", "TERMINATED", 0, 10),
    ("heart failure", "TERMINATED", 0, 15),
    ("asthma", "TERMINATED", 0, 10),
    ("COPD", "TERMINATED", 0, 10),
    ("hepatitis", "TERMINATED", 0, 10),
    ("schizophrenia", "TERMINATED", 0, 10),
    # Withdrawn = definite failures
    ("cancer", "WITHDRAWN", 0, 30),
    ("diabetes", "WITHDRAWN", 0, 10),
    ("Alzheimer", "WITHDRAWN", 0, 10),
]


def main():
    from mcp.servers.ct_gov_mcp import search

    # Load existing
    if os.path.exists(DATA_FILE):
        existing = pd.read_csv(DATA_FILE, dtype=str)
        existing_ncts = set(existing['nct_id'].tolist())
        print(f"Existing: {len(existing)} trials")
    else:
        existing_ncts = set()
        with open(DATA_FILE, 'w', newline='') as f:
            csv.DictWriter(f, fieldnames=COLUMNS).writeheader()

    total_new = 0
    no_drug = 0
    target = 500 - len(existing_ncts)

    for si, (condition, status, label, page_size) in enumerate(SEARCHES):
        if total_new >= target:
            break

        print(f"\n[{si+1}/{len(SEARCHES)}] {condition} / {status} (pageSize={page_size})")

        try:
            result = search(condition=condition, status=status, phase="PHASE3", pageSize=page_size)
            text = result if isinstance(result, str) else result.get('text', str(result))
        except Exception as e:
            print(f"  Search error: {e}")
            continue

        # Split into trial blocks
        blocks = re.split(r'---\s*\n|###\s+\d+\.', text)

        for block in blocks:
            if total_new >= target:
                break

            trial = parse_search_block(block)
            nct_id = trial.get('nct_id', '')
            if not nct_id or nct_id in existing_ncts:
                continue

            title = trial.get('title', '')
            drug = extract_drug_from_title(title)

            if not drug:
                no_drug += 1
                continue

            target_gene = resolve_target(drug)
            indication = infer_indication_area(trial.get('condition', condition))

            row = {col: '' for col in COLUMNS}
            row.update(trial)
            row['label'] = str(label)
            row['intervention_name'] = drug
            row['indication_area'] = indication
            row['primary_purpose'] = 'Treatment'
            if not row.get('condition'):
                row['condition'] = condition

            # Append
            with open(DATA_FILE, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction='ignore')
                writer.writerow({col: row.get(col, '') for col in COLUMNS})

            existing_ncts.add(nct_id)
            total_new += 1
            print(f"  + {nct_id} {drug:25s} target={target_gene:10s} phase={trial.get('phase','')} enroll={trial.get('enrollment','?'):>6s} label={label}")

    _save_cache()
    print(f"\nDone. Added {total_new} new trials (skipped {no_drug} with no drug name).")
    print(f"Total: {len(existing_ncts)} trials")
    print(f"Drug→target cache: {len(DRUG_TARGET_CACHE)} entries")


if __name__ == '__main__':
    main()
