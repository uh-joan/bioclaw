#!/usr/bin/env python3
"""Backfill CT.gov metadata for trials that have NCT IDs but missing phase/enrollment."""
import sys, os, csv, re
sys.path.insert(0, os.path.abspath('.'))
os.environ['MCP_CONFIG_FILE'] = os.path.abspath('mcp-config.json')

import pandas as pd
from mcp.servers.ct_gov_mcp import get_study, search
from collect import COLUMNS

DATA_FILE = 'data/trials_raw.csv'


def parse_markdown_study(text: str) -> dict:
    """Parse CT.gov markdown response into structured fields."""
    out = {}
    if not isinstance(text, str):
        return out

    # NCT ID
    m = re.search(r'(NCT\d{8})', text)
    if m:
        out['nct_id'] = m.group(1)

    # Title
    m = re.search(r'\*\*Study Title:\*\*\s*(.+)', text)
    if m:
        out['title'] = m.group(1).strip()

    # Status
    m = re.search(r'\*\*Status:\*\*\s*(\w+)', text)
    if m:
        out['status'] = m.group(1).strip()

    # Phase
    m = re.search(r'\*\*Phase:\*\*\s*(.+)', text)
    if m:
        phase_raw = m.group(1).strip()
        # Normalize: "Phase 2" -> 2, "Phase2" -> 2, "PHASE3" -> 3, "Phase 2/Phase 3" -> 3
        phases = re.findall(r'(\d)', phase_raw)
        if phases:
            out['phase'] = max(int(p) for p in phases)

    # Study type
    m = re.search(r'\*\*Study Type:\*\*\s*(.+)', text)
    if m:
        out['study_type'] = m.group(1).strip()

    # Lead Sponsor
    m = re.search(r'\*\*Lead Sponsor:\*\*\s*(.+)', text)
    if m:
        sponsor_raw = m.group(1).strip()
        out['lead_sponsor'] = re.sub(r'\s*\(.*\)', '', sponsor_raw).strip()
        # Extract sponsor type from parentheses
        st = re.search(r'\((Industry|NIH|Other|Academic|Government)\)', sponsor_raw, re.I)
        if st:
            out['sponsor_type'] = st.group(1)
        elif any(x in sponsor_raw.lower() for x in ['pharma', 'inc', 'ltd', 'llc', 'corp', 'gmbh', 'sa ']):
            out['sponsor_type'] = 'Industry'
        else:
            out['sponsor_type'] = 'Other'

    # Start date
    m = re.search(r'\*\*Study Start:\*\*\s*(.+)', text)
    if m:
        out['start_date'] = m.group(1).strip()

    # Primary completion
    m = re.search(r'\*\*Primary Completion:\*\*\s*(.+)', text)
    if m:
        out['completion_date'] = re.sub(r'\s*\(.*\)', '', m.group(1)).strip()

    # Allocation
    m = re.search(r'\*\*Allocation:\*\*\s*(\w+)', text)
    if m:
        out['allocation'] = m.group(1).strip()

    # Primary Purpose
    m = re.search(r'\*\*Primary Purpose:\*\*\s*(\w+)', text)
    if m:
        out['primary_purpose'] = m.group(1).strip()

    # Masking
    m = re.search(r'\*\*Masking:\*\*\s*(.+)', text)
    if m:
        out['masking'] = m.group(1).strip()

    # Enrollment — formats: "**Enrollment:** 500", "- **Enrollment:** 6 participants (Actual)"
    m = re.search(r'\*\*Enrollment:\*\*\s*(\d[\d,]*)', text)
    if m:
        out['enrollment'] = m.group(1).replace(',', '')

    # Number of arms
    arms = re.findall(r'Arm \d+|arm \d+|Group \d+|group \d+', text, re.I)
    if arms:
        out['num_arms'] = len(set(arms))

    # Intervention type
    m = re.search(r'\*\*Intervention Type:\*\*\s*(\w+)', text)
    if m:
        out['intervention_type'] = m.group(1).strip()
    elif 'drug' in text.lower()[:500]:
        out['intervention_type'] = 'Drug'
    elif 'biological' in text.lower()[:500]:
        out['intervention_type'] = 'Biological'

    # Has DMC
    if 'data monitoring' in text.lower() or 'dsmb' in text.lower() or 'dmc' in text.lower():
        out['has_dmc'] = 1
    else:
        out['has_dmc'] = 0

    return out


def find_nct_id(drug: str, condition: str) -> str:
    """Search CT.gov for an NCT ID given drug + condition."""
    try:
        result = search(intervention=drug, condition=condition, pageSize=5)
        text = result if isinstance(result, str) else result.get('text', str(result))
        nct_ids = re.findall(r'NCT\d{8}', text)
        return nct_ids[0] if nct_ids else ''
    except Exception as e:
        print(f"  [search error] {e}")
        return ''


def main():
    df = pd.read_csv(DATA_FILE, dtype=str)
    print(f"Loaded {len(df)} trials")

    updated = 0
    errors = 0

    for idx, row in df.iterrows():
        nct_id = str(row.get('nct_id', ''))
        phase = row.get('phase', '')
        drug = str(row.get('intervention_name', ''))
        condition = str(row.get('condition', ''))

        # Skip if already has phase AND enrollment (fully backfilled)
        enrollment_val = row.get('enrollment', '')
        if pd.notna(phase) and str(phase).strip() and str(phase).strip() != 'nan' \
           and pd.notna(enrollment_val) and str(enrollment_val).strip() and str(enrollment_val).strip() != 'nan':
            continue

        # Try to get NCT ID if missing
        if not nct_id.startswith('NCT'):
            nct_id = find_nct_id(drug, condition)
            if nct_id:
                df.at[idx, 'nct_id'] = nct_id
                print(f"  [{idx+1}] Found NCT: {nct_id} for {drug}/{condition}")

        if not nct_id.startswith('NCT'):
            print(f"  [{idx+1}] SKIP no NCT ID for {drug}/{condition}")
            errors += 1
            continue

        # Get study details
        try:
            result = get_study(nctId=nct_id)
            text = result if isinstance(result, str) else result.get('text', str(result))
            features = parse_markdown_study(text)

            if features.get('phase'):
                for col, val in features.items():
                    if col in df.columns and val:
                        df.at[idx, col] = str(val)
                updated += 1
                print(f"  [{idx+1}] OK {nct_id} phase={features.get('phase')} enroll={features.get('enrollment','?')} {drug}")
            else:
                print(f"  [{idx+1}] No phase parsed for {nct_id}")
                errors += 1
        except Exception as e:
            print(f"  [{idx+1}] ERROR {nct_id}: {e}")
            errors += 1

    # Save
    df.to_csv(DATA_FILE, index=False)
    print(f"\nDone. Updated {updated} trials, {errors} errors. Saved to {DATA_FILE}")


if __name__ == '__main__':
    main()
