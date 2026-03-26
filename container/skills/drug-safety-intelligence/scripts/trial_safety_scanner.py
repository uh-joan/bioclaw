"""Clinical trial safety signal scanner for drug safety intelligence.

Searches ClinicalTrials.gov for TERMINATED and SUSPENDED trials,
classifies termination reasons, and aggregates safety signals.
"""

from typing import Dict, Any, List, Optional
import re

# Safety-related termination reason keywords
SAFETY_REASON_PATTERNS = {
    'safety_concern': [
        'safety', 'adverse', 'toxicity', 'toxic', 'serious adverse',
        'death', 'fatal', 'mortality', 'risk',
    ],
    'lack_of_efficacy': [
        'efficacy', 'futility', 'lack of efficacy', 'insufficient efficacy',
        'no benefit', 'did not meet', 'failed to demonstrate',
    ],
    'benefit_risk': [
        'benefit-risk', 'benefit risk', 'unfavorable',
        'risk-benefit', 'risk benefit',
    ],
    'regulatory': [
        'fda', 'regulatory', 'clinical hold', 'partial clinical hold',
        'dsmb', 'data safety', 'monitoring board',
    ],
    'business': [
        'business', 'strategic', 'funding', 'sponsor decision',
        'portfolio', 'commercial', 'financial',
    ],
    'enrollment': [
        'enrollment', 'recruitment', 'accrual', 'slow enrollment',
        'insufficient enrollment',
    ],
}


def _classify_termination_reason(reason_text: str) -> str:
    """Classify termination reason into category."""
    if not reason_text:
        return 'unknown'

    reason_lower = reason_text.lower()

    # Check patterns in priority order (safety first)
    for category, patterns in SAFETY_REASON_PATTERNS.items():
        for pattern in patterns:
            if pattern in reason_lower:
                return category

    return 'other'


def _parse_trial_from_markdown(section: str) -> Dict[str, Any]:
    """Parse a single trial from CT.gov markdown section."""
    trial = {}

    # NCT ID can appear as "NCT12345678" at start of section or after heading
    nct_match = re.search(r'(NCT\d{7,8})', section)
    if nct_match:
        trial['nct_id'] = nct_match.group(1)

    title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|$)', section)
    if title_match:
        trial['title'] = title_match.group(1).strip()

    status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?:\n|$)', section)
    if status_match:
        trial['status'] = status_match.group(1).strip()

    phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|$)', section)
    if phase_match:
        trial['phase'] = phase_match.group(1).strip()

    enrollment_match = re.search(r'\*\*Enrollment:\*\*\s*(\d+)', section)
    if enrollment_match:
        trial['enrollment'] = int(enrollment_match.group(1))

    sponsor_match = re.search(r'\*\*Lead Sponsor:\*\*\s*(.+?)(?:\n|$)', section)
    if sponsor_match:
        trial['sponsor'] = sponsor_match.group(1).strip()

    conditions_match = re.search(r'\*\*Conditions:\*\*\s*(.+?)(?:\n|$)', section)
    if conditions_match:
        trial['conditions'] = conditions_match.group(1).strip()

    interventions_match = re.search(r'\*\*Interventions:\*\*\s*(.+?)(?:\n|$)', section)
    if interventions_match:
        trial['interventions'] = interventions_match.group(1).strip()

    # WhyStopped field
    why_match = re.search(r'\*\*Why Stopped:\*\*\s*(.+?)(?:\n|$)', section)
    if why_match:
        trial['why_stopped'] = why_match.group(1).strip()

    return trial


def scan_trial_safety_signals(
    ctgov_search_func,
    drug_names: List[str],
    target_name: str = None,
    tracker=None,
) -> Dict[str, Any]:
    """
    Scan CT.gov for terminated/suspended trials with safety signals.

    Args:
        ctgov_search_func: CT.gov search wrapper function
        drug_names: List of drug names to search
        target_name: Optional target name for broader search
        tracker: ProgressTracker instance

    Returns:
        dict with terminated_trials, suspended_trials, safety_signals, summary
    """
    if tracker:
        tracker.start_step('trial_signals', "Searching for terminated/suspended trials...")

    terminated_trials = []
    suspended_trials = []
    safety_signals = []

    # Build intervention search - use first 3 drug names to avoid overly long queries
    drug_query_parts = []
    for drug in drug_names[:3]:
        name = drug[:80] if len(drug) > 80 else drug
        drug_query_parts.append(name)

    intervention_query = ' OR '.join(drug_query_parts)

    def _parse_ctgov_response(result, target_status: str) -> List[Dict]:
        """Parse CT.gov response (markdown string or dict) into trial list."""
        trials = []

        # Handle string (markdown) response
        if isinstance(result, str):
            # Split on study headers like "### 1. NCT..."
            sections = re.split(r'\n###\s+\d+\.\s+', result)
            for section in sections[1:] if len(sections) > 1 else []:
                trial = _parse_trial_from_markdown(section)
                if trial.get('nct_id') or trial.get('title'):
                    trial['status'] = target_status
                    trials.append(trial)

        # Handle dict response
        elif isinstance(result, dict):
            studies = result.get('studies', [])
            if isinstance(studies, list):
                for study in studies:
                    if isinstance(study, dict):
                        trials.append({
                            'nct_id': study.get('nctId', ''),
                            'title': study.get('title', ''),
                            'status': target_status,
                            'phase': study.get('phase', ''),
                            'enrollment': study.get('enrollment', 0),
                            'sponsor': study.get('sponsor', ''),
                            'conditions': study.get('conditions', ''),
                            'why_stopped': study.get('whyStopped', ''),
                        })

            # Also check for embedded text
            text = result.get('text', '')
            if text and isinstance(text, str):
                extra = _parse_ctgov_response(text, target_status)
                seen_ids = {t.get('nct_id') for t in trials if t.get('nct_id')}
                for t in extra:
                    if t.get('nct_id') and t['nct_id'] not in seen_ids:
                        trials.append(t)

        return trials

    # Search for TERMINATED trials
    if tracker:
        tracker.update_step(0.2, "Searching terminated trials...")

    try:
        terminated_result = ctgov_search_func(
            intervention=intervention_query,
            status='terminated',
            pageSize=50,
        )
        terminated_trials = _parse_ctgov_response(terminated_result, 'TERMINATED')
    except Exception as e:
        print(f"  Warning: Terminated trial search failed: {e}")

    if tracker:
        tracker.update_step(0.5, f"Found {len(terminated_trials)} terminated trials. Searching suspended...")

    # Search for SUSPENDED trials
    try:
        suspended_result = ctgov_search_func(
            intervention=intervention_query,
            status='suspended',
            pageSize=50,
        )
        suspended_trials = _parse_ctgov_response(suspended_result, 'SUSPENDED')
    except Exception as e:
        print(f"  Warning: Suspended trial search failed: {e}")

    if tracker:
        tracker.update_step(0.7, f"Found {len(suspended_trials)} suspended trials. Classifying reasons...")

    # Classify termination/suspension reasons
    all_trials = terminated_trials + suspended_trials
    reason_counts = {
        'safety_concern': 0,
        'lack_of_efficacy': 0,
        'benefit_risk': 0,
        'regulatory': 0,
        'business': 0,
        'enrollment': 0,
        'other': 0,
        'unknown': 0,
    }

    for trial in all_trials:
        reason = trial.get('why_stopped', '')
        category = _classify_termination_reason(reason)
        trial['reason_category'] = category
        reason_counts[category] += 1

        # Add to safety signals if safety-related
        if category in ('safety_concern', 'benefit_risk', 'regulatory'):
            safety_signals.append({
                'nct_id': trial.get('nct_id', ''),
                'title': trial.get('title', ''),
                'status': trial.get('status', ''),
                'phase': trial.get('phase', ''),
                'reason': reason,
                'reason_category': category,
                'sponsor': trial.get('sponsor', ''),
            })

    if tracker:
        tracker.complete_step(
            f"Trial scan: {len(terminated_trials)} terminated, "
            f"{len(suspended_trials)} suspended, "
            f"{len(safety_signals)} safety signals"
        )

    return {
        'terminated_trials': terminated_trials,
        'suspended_trials': suspended_trials,
        'safety_signals': safety_signals,
        'reason_breakdown': reason_counts,
        'summary': {
            'total_terminated': len(terminated_trials),
            'total_suspended': len(suspended_trials),
            'safety_related': len(safety_signals),
            'safety_concern_count': reason_counts['safety_concern'],
            'benefit_risk_count': reason_counts['benefit_risk'],
            'regulatory_count': reason_counts['regulatory'],
        },
    }
