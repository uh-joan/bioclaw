#!/usr/bin/env python3
"""
Clinical pipeline data collection for company SWOT analysis.

This module provides functions for:
- Collecting active clinical trials from ClinicalTrials.gov
- Normalizing and cleaning drug names
- Extracting drug names from trial titles
"""

import re
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional

# All MCP functions are now accessed via mcp_funcs parameter
# No direct imports from mcp.servers.* allowed

from swot_constants import NON_DRUG_ITEMS, FORMULATION_TERMS


# ============================================================================
# Drug Name Normalization
# ============================================================================

def normalize_drug_name(drug_name: str) -> str:
    """Normalize drug name for comparison and grouping."""
    if not drug_name:
        return ""

    name = drug_name.lower().strip()

    # Remove dosage patterns
    name = re.sub(r'\d+\.?\d*\s*(mg|mcg|ug|g|ml|l|iu|units?|%)\b', '', name, flags=re.IGNORECASE)

    # Remove formulation terms
    for term in FORMULATION_TERMS:
        name = re.sub(rf'\b{term}\b', '', name, flags=re.IGNORECASE)

    # Remove parenthetical content
    name = re.sub(r'\([^)]*\)', '', name)

    # Clean up
    name = re.sub(r'[-_/,]+', ' ', name)
    name = re.sub(r'\s+', ' ', name)
    return name.strip()


def clean_drug_for_display(drug_name: str) -> Optional[str]:
    """Clean drug name for display, returning None if it's not a real drug."""
    if not drug_name:
        return None

    name = drug_name.strip()
    name_lower = name.lower()

    # Skip non-drug items
    for non_drug in NON_DRUG_ITEMS:
        if non_drug in name_lower:
            return None

    # Skip percentage-based items
    if re.match(r'^\d+\.?\d*\s*%', name_lower):
        return None

    # Remove dosage patterns but keep case
    name = re.sub(r'\d+\.?\d*\s*(mg|mcg|ug|g|ml|l|iu|units?)\b', '', name, flags=re.IGNORECASE)

    # Strip formulation terms
    for term in FORMULATION_TERMS:
        name = re.sub(rf'\b{term}\b', '', name, flags=re.IGNORECASE)

    name = re.sub(r'\s+', ' ', name).strip()

    if not name or len(name) < 2:
        return None

    if name.lower() in NON_DRUG_ITEMS:
        return None

    # Capitalize properly
    if not name.isupper() or len(name) > 10:
        name = name.capitalize()

    return name


# ============================================================================
# Clinical Pipeline Collection
# ============================================================================

def get_clinical_pipeline(company_name: str, mcp_funcs: Dict[str, Any] = None) -> Dict[str, Any]:
    """Collect ACTIVE clinical trial pipeline from ClinicalTrials.gov with drug extraction.

    Focuses on active/recruiting trials only (not historical completed/terminated trials).
    Extracts specific drug names, trial IDs, and groups by development stage.
    """
    print(f"\n📊 Collecting ACTIVE clinical pipeline for {company_name}...")

    if not mcp_funcs:
        return {'trials': [], 'by_phase': {}, 'drug_count': 0, 'trial_count': 0, 'success': False, 'error': 'No MCP functions provided'}

    ct_search = mcp_funcs.get('ctgov_search')
    if not ct_search:
        return {'trials': [], 'by_phase': {}, 'drug_count': 0, 'trial_count': 0, 'success': False, 'error': 'CT.gov search function not available'}

    try:
        all_trials = []
        page_token = None

        # Active pipeline statuses (exclude completed, terminated, withdrawn, suspended)
        active_status = "recruiting OR not_yet_recruiting OR active_not_recruiting OR enrolling_by_invitation"

        # Pagination loop - collect ALL active trials
        while True:
            if page_token:
                result = ct_search(
                    lead=company_name,
                    status=active_status,
                    pageSize=1000,
                    pageToken=page_token
                )
            else:
                result = ct_search(
                    lead=company_name,
                    status=active_status,
                    pageSize=1000
                )

            trials_text = result if isinstance(result, str) else str(result)

            # Parse trials from this page - extract rich data
            trial_blocks = re.split(r'###\s+\d+\.\s+(NCT\d{8})', trials_text)

            # Process in pairs (NCT ID, block content)
            i = 1
            while i < len(trial_blocks) - 1:
                nct_id = trial_blocks[i]
                block = trial_blocks[i + 1]

                trial_data = {'nct_id': nct_id}

                # Extract title
                title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|$)', block)
                if title_match:
                    trial_data['title'] = title_match.group(1).strip()

                # Extract phase
                phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|$)', block)
                if phase_match:
                    trial_data['phase'] = phase_match.group(1).strip()

                # Extract status
                status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?:\n|$)', block)
                if status_match:
                    trial_data['status'] = status_match.group(1).strip()

                # Extract conditions
                condition_match = re.search(r'\*\*Conditions:\*\*\s*(.+?)(?:\n|$)', block)
                if condition_match:
                    trial_data['conditions'] = condition_match.group(1).strip()

                # Extract drug names from title
                # Pattern: "A Study of DrugName" or "DrugName vs X" or "DrugName in Participants"
                title = trial_data.get('title', '')
                drugs = []

                # Pattern 1: "Study of XYZ123" or "Study of Drugname"
                study_of = re.search(r'Study\s+of\s+([A-Z][A-Za-z0-9\-]+)', title)
                if study_of:
                    drug_candidate = study_of.group(1)
                    # Skip common non-drug words
                    if drug_candidate.lower() not in ('the', 'an', 'a'):
                        cleaned = clean_drug_for_display(drug_candidate)
                        if cleaned:
                            drugs.append(cleaned)

                # Pattern 2: "DrugName Versus/vs X" at start
                versus_match = re.match(r'^([A-Z][A-Za-z0-9\-]+)\s+(?:Versus|vs\.?|Compared)', title)
                if versus_match and not drugs:
                    cleaned = clean_drug_for_display(versus_match.group(1))
                    if cleaned:
                        drugs.append(cleaned)

                # Pattern 3: Known drug code patterns (XB123, XL309, etc)
                drug_codes = re.findall(r'\b([A-Z]{2,3}\d{2,4})\b', title)
                for code in drug_codes:
                    if code not in [d.upper() for d in drugs]:
                        drugs.append(code)

                # Pattern 4: Generic drug name patterns (ending in -inib, -mab, -nib, etc)
                generic_drugs = re.findall(r'\b([A-Z][a-z]*(?:inib|mab|nib|tinib|zumab|ximab|lizumab))\b', title, re.I)
                for drug in generic_drugs:
                    cleaned = clean_drug_for_display(drug)
                    if cleaned and cleaned.lower() not in [d.lower() for d in drugs]:
                        drugs.append(cleaned)

                trial_data['drugs'] = drugs

                # Extract trial acronym from title if present (e.g., "STELLAR-001")
                acronym_match = re.search(r'\b([A-Z]{3,}[-\s]?\d{2,3})\b', title)
                if acronym_match:
                    trial_data['acronym'] = acronym_match.group(1)

                all_trials.append(trial_data)
                i += 2

            # Check for next page
            page_match = re.search(r'pageToken:\s*"([^"]+)"', trials_text)
            if page_match:
                page_token = page_match.group(1)
                print(f"   Fetched page, continuing pagination...")
            else:
                break

        print(f"   Active trials collected: {len(all_trials)} (recruiting/ongoing only)")

        # Aggregate data
        phases = [t.get('phase', 'Unknown') for t in all_trials]
        statuses = [t.get('status', 'Unknown') for t in all_trials]
        conditions = [t.get('conditions', '') for t in all_trials]

        # Group drugs by phase
        drugs_by_phase = defaultdict(set)
        drug_trial_count = Counter()
        drug_phase_max = {}  # Track highest phase per drug

        phase_order = {'Phase 4': 4, 'Phase 3': 3, 'Phase 2': 2, 'Phase 1': 1, 'Phase 2/Phase 3': 2.5, 'Phase 1/Phase 2': 1.5}

        for trial in all_trials:
            phase = trial.get('phase', 'Unknown')
            phase_num = phase_order.get(phase, 0)
            for drug in trial.get('drugs', []):
                drug_lower = drug.lower()
                drugs_by_phase[phase].add(drug)
                drug_trial_count[drug_lower] += 1
                # Track highest phase for this drug
                if drug_lower not in drug_phase_max or phase_num > drug_phase_max[drug_lower][0]:
                    drug_phase_max[drug_lower] = (phase_num, phase, drug)

        # Identify lead/franchise drugs (most trials, highest phase)
        # For small biotechs, include all drugs found (>=1 trial)
        # For larger companies, prioritize drugs with multiple trials
        lead_drugs = []
        for drug_lower, count in drug_trial_count.most_common(10):
            if count >= 1:  # Include any drug with at least 1 trial
                phase_num, phase, display_name = drug_phase_max[drug_lower]
                lead_drugs.append({
                    'name': display_name,
                    'trial_count': count,
                    'highest_phase': phase
                })

        # Get notable trial names (acronyms)
        notable_trials = []
        for trial in all_trials:
            if trial.get('acronym') and trial.get('phase') in ('Phase 3', 'Phase 2/Phase 3'):
                notable_trials.append({
                    'acronym': trial['acronym'],
                    'nct_id': trial['nct_id'],
                    'phase': trial['phase'],
                    'condition': trial.get('conditions', '')[:50]
                })

        return {
            'total_trials': len(all_trials),
            'phase_distribution': dict(Counter(phases).most_common()),
            'status_distribution': dict(Counter(statuses).most_common(5)),
            'therapeutic_areas': dict(Counter(conditions).most_common(10)),
            'lead_drugs': lead_drugs[:5],  # Top 5 drugs by trial count
            'drugs_by_phase': {k: list(v) for k, v in drugs_by_phase.items()},
            'notable_trials': notable_trials[:10],  # Top 10 named trials
            'all_drugs': list(set(d for drugs in drugs_by_phase.values() for d in drugs)),
            'success': True
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'total_trials': 0, 'success': False, 'error': str(e)}
