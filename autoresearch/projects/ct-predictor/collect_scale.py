#!/usr/bin/env python3
"""
Scale up trial collection to 500+ by searching CT.gov broadly.
Searches by indication area and phase, collects NCT IDs, dedupes against existing data.
"""
import sys, os, csv, re, time
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.environ['MCP_CONFIG_FILE'] = os.path.join(os.path.dirname(__file__), 'mcp-config.json')

import pandas as pd
from collect import COLUMNS

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'trials_raw.csv')

# Indication areas + search terms + expected base rate
SEARCHES = [
    # (condition, status, phase, indication_area, label)
    # === SUCCESSES (completed Phase 3 with approved drugs) ===
    ("breast cancer", "COMPLETED", "PHASE3", "oncology", 1),
    ("lung cancer", "COMPLETED", "PHASE3", "oncology", 1),
    ("melanoma", "COMPLETED", "PHASE3", "oncology", 1),
    ("colorectal cancer", "COMPLETED", "PHASE3", "oncology", 1),
    ("prostate cancer", "COMPLETED", "PHASE3", "oncology", 1),
    ("renal cell carcinoma", "COMPLETED", "PHASE3", "oncology", 1),
    ("ovarian cancer", "COMPLETED", "PHASE3", "oncology", 1),
    ("lymphoma", "COMPLETED", "PHASE3", "oncology", 1),
    ("leukemia", "COMPLETED", "PHASE3", "oncology", 1),
    ("multiple myeloma", "COMPLETED", "PHASE3", "oncology", 1),
    ("hepatocellular carcinoma", "COMPLETED", "PHASE3", "oncology", 1),
    ("gastric cancer", "COMPLETED", "PHASE3", "oncology", 1),
    ("type 2 diabetes", "COMPLETED", "PHASE3", "metabolic", 1),
    ("obesity", "COMPLETED", "PHASE3", "metabolic", 1),
    ("rheumatoid arthritis", "COMPLETED", "PHASE3", "immunology", 1),
    ("psoriasis", "COMPLETED", "PHASE3", "immunology", 1),
    ("crohn's disease", "COMPLETED", "PHASE3", "immunology", 1),
    ("ulcerative colitis", "COMPLETED", "PHASE3", "immunology", 1),
    ("atopic dermatitis", "COMPLETED", "PHASE3", "immunology", 1),
    ("heart failure", "COMPLETED", "PHASE3", "cardiovascular", 1),
    ("hypertension", "COMPLETED", "PHASE3", "cardiovascular", 1),
    ("asthma", "COMPLETED", "PHASE3", "respiratory", 1),
    ("COPD", "COMPLETED", "PHASE3", "respiratory", 1),
    ("HIV", "COMPLETED", "PHASE3", "infectious", 1),
    ("hepatitis C", "COMPLETED", "PHASE3", "infectious", 1),
    ("epilepsy", "COMPLETED", "PHASE3", "cns", 1),
    ("depression", "COMPLETED", "PHASE3", "cns", 1),
    ("multiple sclerosis", "COMPLETED", "PHASE3", "cns", 1),
    ("Alzheimer", "COMPLETED", "PHASE3", "cns", 1),

    # === FAILURES (terminated Phase 2/3) ===
    ("breast cancer", "TERMINATED", "PHASE3", "oncology", 0),
    ("lung cancer", "TERMINATED", "PHASE3", "oncology", 0),
    ("melanoma", "TERMINATED", "PHASE3", "oncology", 0),
    ("colorectal cancer", "TERMINATED", "PHASE3", "oncology", 0),
    ("prostate cancer", "TERMINATED", "PHASE3", "oncology", 0),
    ("ovarian cancer", "TERMINATED", "PHASE3", "oncology", 0),
    ("pancreatic cancer", "TERMINATED", "PHASE3", "oncology", 0),
    ("glioblastoma", "TERMINATED", "PHASE3", "oncology", 0),
    ("type 2 diabetes", "TERMINATED", "PHASE3", "metabolic", 0),
    ("obesity", "TERMINATED", "PHASE3", "metabolic", 0),
    ("Alzheimer", "TERMINATED", "PHASE3", "cns", 0),
    ("depression", "TERMINATED", "PHASE3", "cns", 0),
    ("Parkinson", "TERMINATED", "PHASE3", "cns", 0),
    ("schizophrenia", "TERMINATED", "PHASE3", "cns", 0),
    ("rheumatoid arthritis", "TERMINATED", "PHASE3", "immunology", 0),
    ("heart failure", "TERMINATED", "PHASE3", "cardiovascular", 0),
    ("stroke", "TERMINATED", "PHASE3", "cardiovascular", 0),
    ("asthma", "TERMINATED", "PHASE3", "respiratory", 0),
    ("COPD", "TERMINATED", "PHASE3", "respiratory", 0),
    ("hepatitis B", "TERMINATED", "PHASE3", "infectious", 0),

    # Phase 2 terminated (extra failures)
    ("breast cancer", "TERMINATED", "PHASE2", "oncology", 0),
    ("lung cancer", "TERMINATED", "PHASE2", "oncology", 0),
    ("melanoma", "TERMINATED", "PHASE2", "oncology", 0),
    ("pancreatic cancer", "TERMINATED", "PHASE2", "oncology", 0),
    ("glioblastoma", "TERMINATED", "PHASE2", "oncology", 0),
    ("Alzheimer", "TERMINATED", "PHASE2", "cns", 0),
    ("Parkinson", "TERMINATED", "PHASE2", "cns", 0),
    ("ALS", "TERMINATED", "PHASE2", "cns", 0),

    # Withdrawn (definite failures)
    ("cancer", "WITHDRAWN", "PHASE3", "oncology", 0),
    ("cancer", "WITHDRAWN", "PHASE2", "oncology", 0),
    ("diabetes", "WITHDRAWN", "PHASE3", "metabolic", 0),
    ("Alzheimer", "WITHDRAWN", "PHASE3", "cns", 0),
]


def parse_markdown_study(text):
    """Parse CT.gov markdown response into structured fields."""
    out = {}
    if not isinstance(text, str):
        return out

    m = re.search(r'(NCT\d{8})', text)
    if m: out['nct_id'] = m.group(1)

    m = re.search(r'\*\*Study Title:\*\*\s*(.+)', text)
    if m: out['title'] = m.group(1).strip()

    m = re.search(r'\*\*Status:\*\*\s*(\w+)', text)
    if m: out['status'] = m.group(1).strip()

    m = re.search(r'\*\*Phase:\*\*\s*(.+)', text)
    if m:
        phases = re.findall(r'(\d)', m.group(1))
        if phases: out['phase'] = str(max(int(p) for p in phases))

    m = re.search(r'\*\*Study Type:\*\*\s*(.+)', text)
    if m: out['study_type'] = m.group(1).strip()

    m = re.search(r'\*\*Lead Sponsor:\*\*\s*(.+)', text)
    if m:
        raw = m.group(1).strip()
        out['lead_sponsor'] = re.sub(r'\s*\(.*\)', '', raw).strip()
        st = re.search(r'\((Industry|NIH|Other|Academic|Government)\)', raw, re.I)
        out['sponsor_type'] = st.group(1) if st else 'Other'

    m = re.search(r'\*\*Study Start:\*\*\s*(.+)', text)
    if m: out['start_date'] = m.group(1).strip()

    m = re.search(r'\*\*Primary Completion:\*\*\s*(.+)', text)
    if m: out['completion_date'] = re.sub(r'\s*\(.*\)', '', m.group(1)).strip()

    m = re.search(r'\*\*Allocation:\*\*\s*(\w+)', text)
    if m: out['allocation'] = m.group(1).strip()

    m = re.search(r'\*\*Primary Purpose:\*\*\s*(\w+)', text)
    if m: out['primary_purpose'] = m.group(1).strip()

    m = re.search(r'\*\*Masking:\*\*\s*(.+)', text)
    if m: out['masking'] = m.group(1).strip()

    m = re.search(r'\*\*Enrollment:\*\*\s*(\d[\d,]*)', text)
    if m: out['enrollment'] = m.group(1).replace(',', '')

    out['intervention_type'] = 'Drug' if 'drug' in text.lower()[:1000] else 'Biological'
    out['has_dmc'] = '1' if any(x in text.lower() for x in ['data monitoring', 'dsmb', 'dmc']) else '0'

    # Extract intervention name
    m = re.search(r'\*\*Intervention.*?:\*\*\s*(.+)', text)
    if m: out['intervention_name'] = m.group(1).strip()[:100]

    return out


def main():
    from mcp.servers.ct_gov_mcp import search, get_study

    # Load existing data
    if os.path.exists(DATA_FILE):
        existing = pd.read_csv(DATA_FILE, dtype=str)
        existing_ncts = set(existing['nct_id'].tolist())
        print(f"Existing: {len(existing)} trials, {len(existing_ncts)} unique NCT IDs")
    else:
        existing_ncts = set()
        # Init CSV
        with open(DATA_FILE, 'w', newline='') as f:
            csv.DictWriter(f, fieldnames=COLUMNS).writeheader()

    total_new = 0
    target_total = 500

    for search_idx, (condition, status, phase, indication_area, label) in enumerate(SEARCHES):
        if len(existing_ncts) + total_new >= target_total:
            print(f"\nReached {target_total} target. Stopping.")
            break

        print(f"\n[Search {search_idx+1}/{len(SEARCHES)}] {condition} / {status} / {phase}")

        try:
            result = search(condition=condition, status=status, phase=phase, pageSize=20)
            text = result if isinstance(result, str) else result.get('text', str(result))
            nct_ids = re.findall(r'NCT\d{8}', text)
            nct_ids = list(dict.fromkeys(nct_ids))  # dedupe preserving order
            print(f"  Found {len(nct_ids)} trials")
        except Exception as e:
            print(f"  Search error: {e}")
            continue

        for nct_id in nct_ids:
            if nct_id in existing_ncts:
                continue
            if len(existing_ncts) + total_new >= target_total:
                break

            try:
                study_result = get_study(nctId=nct_id)
                text = study_result if isinstance(study_result, str) else study_result.get('text', str(study_result))
                features = parse_markdown_study(text)

                if not features.get('phase'):
                    continue

                row = {col: '' for col in COLUMNS}
                row.update(features)
                row['nct_id'] = nct_id
                row['label'] = str(label)
                row['indication_area'] = indication_area
                if not row.get('condition'):
                    row['condition'] = condition

                # Append immediately
                with open(DATA_FILE, 'a', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction='ignore')
                    writer.writerow({col: row.get(col, '') for col in COLUMNS})

                existing_ncts.add(nct_id)
                total_new += 1
                print(f"  + {nct_id} phase={features.get('phase')} enroll={features.get('enrollment','?')} label={label}")

            except Exception as e:
                print(f"  Error {nct_id}: {e}")
                continue

    print(f"\nDone. Added {total_new} new trials. Total now: {len(existing_ncts) + total_new}")


if __name__ == '__main__':
    main()
