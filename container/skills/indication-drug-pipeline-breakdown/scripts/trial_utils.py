"""Clinical trial data extraction and search utilities."""
import re
from typing import Dict, Any

# All MCP functions are now accessed via mcp_funcs parameter
# No direct imports from mcp.servers.* allowed


def extract_sponsor_from_trial(trial_data) -> str:
    """Extract lead sponsor from trial data (markdown string or dict)."""
    # Handle markdown string from get_study()
    if isinstance(trial_data, str):
        # Pattern: **Lead Sponsor:** Eli Lilly and Company (Industry)
        sponsor_match = re.search(r'\*\*Lead Sponsor:\*\*\s*(.+?)(?:\s*\([^)]+\))?(?:\n|$)', trial_data)
        if sponsor_match:
            return sponsor_match.group(1).strip()
    # Handle dict (fallback)
    if isinstance(trial_data, dict):
        protocol = trial_data.get('protocolSection', {})
        sponsor_module = protocol.get('sponsorCollaboratorsModule', {})
        lead_sponsor = sponsor_module.get('leadSponsor', {})
        sponsor_name = lead_sponsor.get('name', '')
        if sponsor_name:
            return sponsor_name
    return "Unknown"


def extract_drugs_from_trial(trial_data) -> list:
    """Extract drug interventions from trial data (markdown string or dict)."""
    drugs = []
    # Handle markdown string from get_study()
    if isinstance(trial_data, str):
        # Pattern: ### Drug: Tirzepatide
        drug_matches = re.findall(r'###\s+Drug:\s*(.+?)(?:\n|$)', trial_data)
        drugs.extend(drug_matches)
    # Handle dict (fallback)
    if isinstance(trial_data, dict):
        protocol = trial_data.get('protocolSection', {})
        arms_module = protocol.get('armsInterventionsModule', {})
        interventions = arms_module.get('interventions', [])
        for intervention in interventions:
            if intervention.get('type', '').upper() == 'DRUG':
                drug_name = intervention.get('name', '')
                if drug_name:
                    drugs.append(drug_name)
    return drugs


def extract_enrollment_from_trial(trial_data) -> int:
    """Extract target enrollment from trial data (markdown string or dict)."""
    # Handle markdown string from get_study()
    if isinstance(trial_data, str):
        # Pattern: **Enrollment:** 300 participants
        enrollment_match = re.search(r'\*\*Enrollment:\*\*\s*(\d+)', trial_data)
        if enrollment_match:
            return int(enrollment_match.group(1))
    # Handle dict (fallback)
    if isinstance(trial_data, dict):
        protocol = trial_data.get('protocolSection', {})
        design = protocol.get('designModule', {})
        enrollment_info = design.get('enrollmentInfo', {})
        count = enrollment_info.get('count', 0)
        return count if isinstance(count, int) else 0
    return 0


def search_phase_trials(condition_query: str, phase: str, status: str = "recruiting OR active_not_recruiting", mcp_funcs: Dict[str, Any] = None) -> list:
    """Search for trials in a specific phase and collect all NCT IDs with pagination.

    Args:
        condition_query: Condition search query (can be "term1 OR term2 OR term3" for synonyms)
        phase: Clinical trial phase code (PHASE1, PHASE2, etc.)
        status: Trial status filter
    """
    if not mcp_funcs:
        return []

    ct_search = mcp_funcs.get('ctgov_search')
    if not ct_search:
        return []

    all_nct_ids = []
    result = ct_search(
        method='search',
        condition=condition_query,
        phase=phase,
        studyType="interventional",
        interventionType="drug",
        status=status,
        pageSize=1000
    )
    result_text = result if isinstance(result, str) else result.get('text', str(result))
    all_nct_ids.extend(re.findall(r'NCT\d{8}', result_text))

    # Handle pagination
    page_token_match = re.search(r'`pageToken:\s*"([^"]+)"', result_text)
    while page_token_match:
        page_token = page_token_match.group(1)
        result = ct_search(
            method='search',
            condition=condition_query,
            phase=phase,
            studyType="interventional",
            interventionType="drug",
            status=status,
            pageSize=1000,
            pageToken=page_token
        )
        result_text = result if isinstance(result, str) else result.get('text', str(result))
        all_nct_ids.extend(re.findall(r'NCT\d{8}', result_text))
        page_token_match = re.search(r'`pageToken:\s*"([^"]+)"', result_text)
    return all_nct_ids


def get_trial_detail(nct_id: str, mcp_funcs: Dict[str, Any] = None):
    """Fetch detailed trial information by NCT ID.

    Args:
        nct_id: NCT identifier (e.g., "NCT12345678")

    Returns:
        Trial detail data (markdown string or dict)
    """
    if not mcp_funcs:
        return None

    get_study = mcp_funcs.get('ctgov_get_study')
    if not get_study:
        return None

    return get_study(nctId=nct_id)
