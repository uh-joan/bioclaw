"""
Clinical trials search and analysis utilities for ClinicalTrials.gov integration.

Note: CT.gov MCP returns markdown text, not JSON. Parse with regex.
"""

import re
from typing import Dict, Any, List
from collections import defaultdict


PHASE_PRIORITY = {
    'PHASE1': 1,
    'PHASE2': 2,
    'PHASE3': 3,
    'PHASE4': 4,
    'NA': 0,
    'EARLY_PHASE1': 0.5
}

PHASE_MAP = {
    'PHASE1': 'Phase 1',
    'PHASE2': 'Phase 2',
    'PHASE3': 'Phase 3',
    'PHASE4': 'Phase 4',
    'EARLY_PHASE1': 'Early Phase 1',
    'NA': 'Not Applicable'
}


def search_trials_for_drug(search_studies_func, drug_name: str, max_trials: int = 1000) -> List[Dict[str, Any]]:
    """
    Search ClinicalTrials.gov for trials testing a specific drug.
    Filters to primary interventions (drug in title) to exclude comparator/control trials.

    Note: CT.gov MCP returns markdown text - parse with regex.

    Args:
        search_studies_func: search_studies function from ct_gov_mcp
        drug_name: Drug name to search
        max_trials: Maximum trials to return

    Returns:
        List of trial dicts with nct_id, title, phase, status
    """
    try:
        # Request more results to account for filtering (3x buffer)
        request_size = max_trials * 3

        # CT.gov MCP returns markdown text
        trials_result = search_studies_func(
            intervention=drug_name,
            pageSize=min(request_size, 1000)  # Cap at API max
        )

        if not trials_result:
            return []

        # Convert to string if needed
        text = trials_result if isinstance(trials_result, str) else str(trials_result)

        # Parse markdown response
        trials = []

        # Normalize drug name for matching (remove spaces, lowercase)
        drug_normalized = drug_name.lower().replace(' ', '').replace('-', '')

        # Split by trial sections (starts with "### N. NCT")
        trial_sections = re.split(r'\n### \d+\. (NCT\d{8})', text)

        # Process pairs: (nct_id, content)
        for i in range(1, len(trial_sections), 2):
            if i + 1 >= len(trial_sections):
                break

            nct_id = trial_sections[i]
            content = trial_sections[i + 1]

            # Extract title
            title_match = re.search(r'\*\*Title:\*\* (.+?)(?:\n|$)', content)
            title = title_match.group(1).strip() if title_match else 'Unknown'

            # Extract status
            status_match = re.search(r'\*\*Status:\*\* (.+?)(?:\n|$)', content)
            status = status_match.group(1).strip() if status_match else 'Unknown'

            # Extract phase (raw format: "Phase3", "Phase2", etc.)
            phase_match = re.search(r'\*\*Phase:\*\* (.+?)(?:\n|$)', content)
            phase_raw = phase_match.group(1).strip() if phase_match else 'NA'

            # Normalize phase to API format for consistent processing
            phase = normalize_phase_from_markdown(phase_raw)

            # Filter for primary interventions (exclude comparator/control trials)
            title_normalized = title.lower().replace(' ', '').replace('-', '')

            # Check if drug name appears in title (strong signal of primary intervention)
            drug_parts = drug_name.lower().split()
            title_lower = title.lower()

            # Accept if:
            # 1. Full drug name in title, OR
            # 2. Significant part of drug name in title (for multi-word drugs), OR
            # 3. Title starts with drug name, OR
            # 4. Phase 1/2 trial (often test single drugs primarily)
            is_primary = False

            # Check full name match
            if drug_normalized in title_normalized:
                is_primary = True
            # Check if major words from drug name appear in title
            elif len(drug_parts) > 1:
                # For multi-word drugs, check if key parts appear
                major_parts = [p for p in drug_parts if len(p) > 3]
                if major_parts and any(part in title_lower for part in major_parts):
                    is_primary = True
            # Check title starts with drug name
            elif title_lower.startswith(drug_name.lower()[:5]):  # First 5 chars
                is_primary = True
            # Early phase trials (Phase 1/2) are usually testing primary drug
            elif phase in ['Phase 1', 'Phase 2', 'Early Phase 1']:
                # For early phase, be more lenient with title matching
                if any(part in title_lower for part in drug_parts if len(part) > 3):
                    is_primary = True

            if not is_primary:
                continue  # Skip comparator/background therapy trials

            trial_info = {
                'nct_id': nct_id,
                'title': title,
                'phase': phase,
                'status': status
            }

            trials.append(trial_info)

            # Stop when we have enough filtered results
            if len(trials) >= max_trials:
                break

        return trials[:max_trials]

    except Exception as e:
        print(f"Warning: Could not search trials for {drug_name}: {e}")
        return []


def normalize_phase_from_markdown(phase_text: str) -> str:
    """
    Normalize phase from CT.gov markdown response.

    Args:
        phase_text: Phase string from markdown (e.g., "Phase3", "Phase2", "NA")

    Returns:
        Normalized phase string (e.g., "Phase 3", "Phase 2")
    """
    # Remove spaces and convert to uppercase
    phase_upper = phase_text.replace(' ', '').upper()

    # Map markdown format to display format
    if phase_upper == 'PHASE1':
        return 'Phase 1'
    elif phase_upper == 'PHASE2':
        return 'Phase 2'
    elif phase_upper == 'PHASE3':
        return 'Phase 3'
    elif phase_upper == 'PHASE4':
        return 'Phase 4'
    elif phase_upper == 'EARLYPHASE1':
        return 'Early Phase 1'
    elif phase_upper == 'NA' or phase_upper == 'N/A':
        return 'Not Applicable'
    else:
        return phase_text  # Return as-is if unrecognized


def normalize_phase(phases: List[str]) -> str:
    """
    Normalize phase list to single phase string.
    Takes highest phase if multiple.

    Args:
        phases: List of phase strings from CT.gov API

    Returns:
        Normalized phase string
    """
    if not phases:
        return "Not Applicable"

    # Sort by priority and take highest
    phases_sorted = sorted(phases, key=lambda p: PHASE_PRIORITY.get(p, 0), reverse=True)
    phase = phases_sorted[0] if phases_sorted else "Not Applicable"

    return PHASE_MAP.get(phase, phase)


def aggregate_trials_by_drug(search_studies_func, drugs: List[Dict], max_trials_per_drug: int = 1000) -> Dict[str, Any]:
    """
    Search trials for multiple drugs and aggregate results.

    Args:
        search_studies_func: search_studies function from ct_gov_mcp
        drugs: List of drug dicts with 'drug_name' field
        max_trials_per_drug: Max trials per drug

    Returns:
        dict with trials_by_drug, phase_distribution, all_trials
    """
    trials_by_drug = {}
    phase_distribution = defaultdict(int)
    all_trials = []

    for drug in drugs:
        drug_name = drug['drug_name']

        trials = search_trials_for_drug(search_studies_func, drug_name, max_trials_per_drug)

        if trials:
            trials_by_drug[drug_name] = {
                'trials': trials,
                'count': len(trials)
            }

            # Update phase distribution
            for trial in trials:
                phase_distribution[trial['phase']] += 1
                all_trials.append({**trial, 'drug': drug_name})

    return {
        'trials_by_drug': trials_by_drug,
        'phase_distribution': dict(phase_distribution),
        'all_trials': all_trials,
        'summary': {
            'total_trials': len(all_trials),
            'drugs_with_trials': len(trials_by_drug)
        }
    }


def get_phase_distribution_summary(phase_distribution: Dict[str, int]) -> Dict[str, int]:
    """
    Summarize phase distribution with ordered phases.

    Args:
        phase_distribution: Dict of phase -> count

    Returns:
        Ordered dict of phase counts
    """
    ordered_phases = ['Early Phase 1', 'Phase 1', 'Phase 2', 'Phase 3', 'Phase 4', 'Not Applicable']
    summary = {}

    for phase in ordered_phases:
        if phase in phase_distribution:
            summary[phase] = phase_distribution[phase]

    return summary


def generate_trial_intelligence_summary(trials_by_drug: Dict[str, Any], phase_distribution: Dict[str, int], total_trials: int) -> Dict[str, Any]:
    """
    Generate high-level intelligence summary of ACTIVE clinical trial landscape.

    Focuses exclusively on current pipeline activity (Recruiting/Active/Enrolling trials).

    Args:
        trials_by_drug: Dict of drug_name -> {trials: [], count: int}
        phase_distribution: Dict of phase -> count (will be recalculated for active only)
        total_trials: Total number of trials (will be recalculated for active only)

    Returns:
        Dict with active trial intelligence summary
    """
    # Calculate active trials by drug
    active_by_drug = []
    all_active_trials = []

    for drug_name, drug_data in trials_by_drug.items():
        trials = drug_data.get('trials', [])
        active_trials = [t for t in trials if 'Recruiting' in t.get('status', '') or
                        'Active' in t.get('status', '') or
                        'Enrolling' in t.get('status', '')]

        if active_trials:
            active_by_drug.append({
                'drug': drug_name,
                'active_trials': len(active_trials),
                'total_trials': len(trials)
            })
            all_active_trials.extend(active_trials)

    # Sort by active trials descending
    active_by_drug.sort(key=lambda x: x['active_trials'], reverse=True)

    # Calculate total active trials
    total_active = len(all_active_trials)

    # Active phase distribution (ONLY active trials)
    # Combine phases: Early Phase 1 + Phase 1 -> Phase 1
    # Ignore: Not Applicable, Phase1,Phase2, Phase2,Phase3
    active_phase_distribution = defaultdict(int)
    for trial in all_active_trials:
        phase = trial.get('phase', 'Not Applicable')

        # Map phases
        if phase == 'Early Phase 1':
            active_phase_distribution['Phase 1'] += 1
        elif phase in ['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4']:
            active_phase_distribution[phase] += 1
        # Ignore: Not Applicable, Phase1,Phase2, Phase2,Phase3

    # Phase distribution percentages (ACTIVE ONLY) - ordered
    ordered_phases = ['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4']
    phase_percentages = {}
    for phase in ordered_phases:
        if phase in active_phase_distribution:
            count = active_phase_distribution[phase]
            percentage = (count / total_active * 100) if total_active > 0 else 0
            phase_percentages[phase] = {
                'count': count,
                'percentage': round(percentage, 1)
            }

    return {
        'total_active_trials': total_active,
        'drugs_with_active_trials': len(active_by_drug),
        'top_5_active': active_by_drug[:5],
        'active_phase_distribution': phase_percentages,
        'key_insights': generate_active_trial_insights(active_by_drug, phase_percentages, total_active)
    }


def generate_active_trial_insights(active_by_drug: List[Dict],
                                   phase_percentages: Dict[str, Dict[str, Any]],
                                   total_active: int) -> List[str]:
    """
    Generate key insights from ACTIVE trial data.

    Args:
        active_by_drug: List of drugs with active trial counts
        phase_percentages: Phase percentages dict with 'count' and 'percentage' for each phase
        total_active: Total number of active trials

    Returns:
        List of insight strings
    """
    insights = []

    # Lead drug insight
    if active_by_drug:
        top_active = active_by_drug[0]
        insights.append(f"{top_active['drug']} dominates with {top_active['active_trials']} active trials")

    # Count trials in defined phases (excludes Not Applicable, mixed phases)
    total_in_phases = sum(v.get('count', 0) for v in phase_percentages.values())

    # Phase 3 + Phase 4 = late-stage pipeline
    phase3_count = phase_percentages.get('Phase 3', {}).get('count', 0)
    phase4_count = phase_percentages.get('Phase 4', {}).get('count', 0)
    late_stage_count = phase3_count + phase4_count

    if late_stage_count > 0:
        late_stage_pct = round(late_stage_count / total_in_phases * 100, 1) if total_in_phases > 0 else 0
        insights.append(f"{late_stage_count} late-stage trials (Phase 3/4, {late_stage_pct}%)")

    # Phase 2 insight (mid-stage pipeline)
    phase2_count = phase_percentages.get('Phase 2', {}).get('count', 0)
    if phase2_count > 0:
        phase2_pct = round(phase2_count / total_in_phases * 100, 1) if total_in_phases > 0 else 0
        insights.append(f"{phase2_count} mid-stage trials (Phase 2, {phase2_pct}%)")

    # Early stage
    phase1_count = phase_percentages.get('Phase 1', {}).get('count', 0)
    if phase1_count > 0:
        phase1_pct = round(phase1_count / total_in_phases * 100, 1) if total_in_phases > 0 else 0
        insights.append(f"{phase1_count} early-stage trials (Phase 1, {phase1_pct}%)")

    return insights
