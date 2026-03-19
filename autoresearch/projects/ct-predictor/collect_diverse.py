#!/usr/bin/env python3
"""
Collect more trials with focus on:
1. More failures (terminated/withdrawn) — currently only 24%
2. More non-oncology indications — currently 68% oncology
3. Target 500 new trials to reach 1000 total
"""
import sys, os, csv, re, time, json
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.environ['MCP_CONFIG_FILE'] = os.path.join(os.path.dirname(__file__), 'mcp-config.json')

import pandas as pd
from collect import COLUMNS
from collect_scale2 import (
    extract_drug_from_title, resolve_target, parse_search_block,
    infer_indication_area, DRUG_TARGET_CACHE, _save_cache, _load_cache
)

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'trials_raw.csv')

# Heavy emphasis on non-oncology and failures
SEARCHES = [
    # === NON-ONCOLOGY SUCCESSES ===
    # Metabolic
    ("type 2 diabetes", "COMPLETED", 1, 50),
    ("obesity", "COMPLETED", 1, 30),
    ("NASH", "COMPLETED", 1, 15),
    ("dyslipidemia", "COMPLETED", 1, 15),
    ("gout", "COMPLETED", 1, 10),
    # Immunology
    ("rheumatoid arthritis", "COMPLETED", 1, 30),
    ("psoriasis", "COMPLETED", 1, 20),
    ("psoriatic arthritis", "COMPLETED", 1, 15),
    ("ankylosing spondylitis", "COMPLETED", 1, 15),
    ("crohn's disease", "COMPLETED", 1, 20),
    ("ulcerative colitis", "COMPLETED", 1, 20),
    ("atopic dermatitis", "COMPLETED", 1, 15),
    ("lupus", "COMPLETED", 1, 10),
    # CNS
    ("Alzheimer", "COMPLETED", 1, 20),
    ("Parkinson", "COMPLETED", 1, 15),
    ("depression", "COMPLETED", 1, 20),
    ("schizophrenia", "COMPLETED", 1, 15),
    ("epilepsy", "COMPLETED", 1, 15),
    ("migraine", "COMPLETED", 1, 15),
    ("multiple sclerosis", "COMPLETED", 1, 20),
    ("bipolar", "COMPLETED", 1, 10),
    ("ADHD", "COMPLETED", 1, 10),
    ("insomnia", "COMPLETED", 1, 10),
    # Cardiovascular
    ("heart failure", "COMPLETED", 1, 20),
    ("hypertension", "COMPLETED", 1, 20),
    ("atrial fibrillation", "COMPLETED", 1, 15),
    ("pulmonary arterial hypertension", "COMPLETED", 1, 10),
    ("coronary artery disease", "COMPLETED", 1, 15),
    ("stroke prevention", "COMPLETED", 1, 10),
    # Respiratory
    ("asthma", "COMPLETED", 1, 20),
    ("COPD", "COMPLETED", 1, 20),
    ("idiopathic pulmonary fibrosis", "COMPLETED", 1, 10),
    ("cystic fibrosis", "COMPLETED", 1, 10),
    # Infectious
    ("HIV", "COMPLETED", 1, 20),
    ("hepatitis C", "COMPLETED", 1, 15),
    ("hepatitis B", "COMPLETED", 1, 10),
    ("COVID-19", "COMPLETED", 1, 15),
    ("influenza", "COMPLETED", 1, 10),
    # Rare
    ("sickle cell", "COMPLETED", 1, 10),
    ("hemophilia", "COMPLETED", 1, 10),
    ("muscular dystrophy", "COMPLETED", 1, 10),

    # === FAILURES (heavy emphasis — need more) ===
    # Oncology failures
    ("breast cancer", "TERMINATED", 0, 30),
    ("lung cancer", "TERMINATED", 0, 30),
    ("prostate cancer", "TERMINATED", 0, 20),
    ("pancreatic cancer", "TERMINATED", 0, 20),
    ("glioblastoma", "TERMINATED", 0, 15),
    ("gastric cancer", "TERMINATED", 0, 15),
    ("ovarian cancer", "TERMINATED", 0, 15),
    ("bladder cancer", "TERMINATED", 0, 10),
    # CNS failures (historically high failure rate)
    ("Alzheimer", "TERMINATED", 0, 30),
    ("Parkinson", "TERMINATED", 0, 15),
    ("depression", "TERMINATED", 0, 15),
    ("schizophrenia", "TERMINATED", 0, 15),
    ("ALS", "TERMINATED", 0, 10),
    ("Huntington", "TERMINATED", 0, 10),
    ("neuropathic pain", "TERMINATED", 0, 10),
    # Metabolic failures
    ("type 2 diabetes", "TERMINATED", 0, 15),
    ("obesity", "TERMINATED", 0, 15),
    ("NASH", "TERMINATED", 0, 15),
    # Cardiovascular failures
    ("heart failure", "TERMINATED", 0, 15),
    ("stroke", "TERMINATED", 0, 10),
    ("atherosclerosis", "TERMINATED", 0, 10),
    # Immunology failures
    ("rheumatoid arthritis", "TERMINATED", 0, 10),
    ("lupus", "TERMINATED", 0, 15),
    ("crohn's disease", "TERMINATED", 0, 10),
    # Respiratory failures
    ("asthma", "TERMINATED", 0, 10),
    ("COPD", "TERMINATED", 0, 10),
    ("idiopathic pulmonary fibrosis", "TERMINATED", 0, 10),
    # Infectious failures
    ("hepatitis B", "TERMINATED", 0, 10),
    ("tuberculosis", "TERMINATED", 0, 10),
    # Withdrawn (guaranteed failures)
    ("diabetes", "WITHDRAWN", 0, 15),
    ("Alzheimer", "WITHDRAWN", 0, 15),
    ("heart failure", "WITHDRAWN", 0, 10),
    ("depression", "WITHDRAWN", 0, 10),
    ("arthritis", "WITHDRAWN", 0, 10),
    ("cancer", "WITHDRAWN", 0, 20),
    ("COPD", "WITHDRAWN", 0, 10),
    ("HIV", "WITHDRAWN", 0, 10),

    # === Phase 2 failures (more volume) ===
    ("Alzheimer", "TERMINATED", 0, 20),  # Phase 2 will be mixed in
    ("depression", "TERMINATED", 0, 15),
    ("NASH", "TERMINATED", 0, 15),
    ("lupus", "TERMINATED", 0, 10),
    ("pain", "TERMINATED", 0, 15),
]


def main():
    from mcp.servers.ct_gov_mcp import search, get_study
    from backfill_ctgov import parse_markdown_study

    # Load existing
    if os.path.exists(DATA_FILE):
        existing = pd.read_csv(DATA_FILE, dtype=str)
        existing_ncts = set(existing['nct_id'].tolist())
        print(f"Existing: {len(existing)} trials, {len(existing_ncts)} unique NCT IDs")
    else:
        existing_ncts = set()

    # Add new columns if needed
    all_cols = list(pd.read_csv(DATA_FILE, dtype=str, nrows=0).columns)

    total_new = 0
    target = 500  # Add 500 more

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

        # Split into blocks and extract NCT IDs
        nct_ids = re.findall(r'NCT\d{8}', text)
        nct_ids = list(dict.fromkeys(nct_ids))  # dedupe

        for nct_id in nct_ids:
            if nct_id in existing_ncts or total_new >= target:
                continue

            try:
                # Get full study details
                study_result = get_study(nctId=nct_id)
                study_text = study_result if isinstance(study_result, str) else study_result.get('text', str(study_result))
                features = parse_markdown_study(study_text)

                if not features.get('phase'):
                    continue

                # Extract drug name from Interventions section
                drugs = re.findall(r'###\s+(?:Drug|Biological):\s*(.+)', study_text)
                drug_name = ''
                if drugs:
                    drug_name = drugs[0].strip()
                    drug_name = re.split(r'\s+\d+\s*(?:mg|ml|mcg)', drug_name, flags=re.I)[0].strip()
                    drug_name = re.sub(r'\s*\(.*?\)', '', drug_name).strip()
                    drug_name = drug_name.rstrip('/, ')
                    if drug_name.lower() in ('placebo', 'chemotherapy', 'standard of care', 'observation', 'radiation', ''):
                        drug_name = ''

                if not drug_name:
                    # Try extracting from title
                    drug_name = extract_drug_from_title(features.get('title', ''))

                # Resolve target
                target_gene = ''
                if drug_name:
                    target_gene = resolve_target(drug_name.lower())

                indication = infer_indication_area(features.get('condition', condition))

                row = {col: '' for col in all_cols}
                row.update(features)
                row['nct_id'] = nct_id
                row['label'] = str(label)
                row['indication_area'] = indication
                row['intervention_name'] = drug_name or 'unknown'
                if not row.get('condition'):
                    row['condition'] = condition

                # Append immediately
                with open(DATA_FILE, 'a', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=all_cols, extrasaction='ignore')
                    writer.writerow({col: row.get(col, '') for col in all_cols})

                existing_ncts.add(nct_id)
                total_new += 1
                print(f"  + {nct_id} {drug_name[:25]:25s} target={target_gene:10s} phase={features.get('phase','')} enroll={features.get('enrollment','?'):>6s} label={label} [{indication}]")

            except Exception as e:
                continue

            time.sleep(0.2)

    _save_cache()
    print(f"\nDone. Added {total_new} new trials. Total: {len(existing_ncts)}")


if __name__ == '__main__':
    main()
