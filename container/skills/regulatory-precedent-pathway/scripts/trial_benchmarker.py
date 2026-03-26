#!/usr/bin/env python3
"""
Trial Benchmarker - No-Precedent Mode.

When fewer than 2 approved drugs exist for an indication, builds a benchmark
matrix from active Phase 2/3 trials with endpoints, comparators, and design
patterns for clinical discussion.

All MCP functions accessed via mcp_funcs parameter.
"""

import re
from typing import Dict, Any, List, Optional, Callable


def build_trial_benchmarks(
    indication: str,
    mcp_funcs: Dict[str, Callable] = None,
    progress_callback=None,
) -> Dict[str, Any]:
    """
    Build a benchmark matrix from active Phase 2/3 trials.

    Args:
        indication: Disease/condition to search
        mcp_funcs: Dict of MCP functions
        progress_callback: Callback(progress, message)

    Returns:
        Dict with trial_benchmarks list and summary
    """
    if mcp_funcs is None:
        mcp_funcs = {}

    ctgov_search = mcp_funcs.get('ctgov_search')
    if not ctgov_search:
        return {'trial_benchmarks': [], 'summary': 'No CT.gov access available'}

    benchmarks = []
    sources = []

    # Search for Phase 2 and Phase 3 active trials
    for phase, phase_label in [("PHASE3", "Phase 3"), ("PHASE2", "Phase 2")]:
        if progress_callback:
            pct = 0.0 if phase == "PHASE3" else 0.5
            progress_callback(pct, f"Searching active {phase_label} trials for {indication}...")

        try:
            result = ctgov_search(
                method="search",
                condition=indication,
                phase=phase,
                status="RECRUITING",
                pageSize=50,
            )

            text = result if isinstance(result, str) else result.get('text', '') if isinstance(result, dict) else ''
            trials = _parse_benchmark_trials(text, phase_label)
            benchmarks.extend(trials)

        except Exception as e:
            print(f"  [Benchmarker] Error searching {phase_label}: {e}")

    # Also search active_not_recruiting for near-completion trials
    try:
        result = ctgov_search(
            method="search",
            condition=indication,
            phase="PHASE3",
            status="ACTIVE_NOT_RECRUITING",
            pageSize=50,
        )
        text = result if isinstance(result, str) else result.get('text', '') if isinstance(result, dict) else ''
        trials = _parse_benchmark_trials(text, "Phase 3")
        benchmarks.extend(trials)
    except Exception:
        pass

    sources.append("ClinicalTrials.gov (active Phase 2/3 trials)")

    # Deduplicate by NCT ID
    seen = set()
    unique_benchmarks = []
    for b in benchmarks:
        nct = b.get('nct_id', '')
        if nct and nct not in seen:
            seen.add(nct)
            unique_benchmarks.append(b)

    # Sort by enrollment (largest first)
    unique_benchmarks.sort(key=lambda x: x.get('enrollment', 0), reverse=True)

    # Extract common design patterns
    design_patterns = _extract_design_patterns(unique_benchmarks)

    if progress_callback:
        progress_callback(1.0, f"Found {len(unique_benchmarks)} active trial benchmarks")

    return {
        'trial_benchmarks': unique_benchmarks,
        'total_found': len(unique_benchmarks),
        'design_patterns': design_patterns,
        'sources': sources,
    }


def _parse_benchmark_trials(text: str, phase_label: str) -> List[Dict[str, Any]]:
    """Parse CT.gov markdown response into benchmark trial dicts."""
    trials = []
    if not text:
        return trials

    entries = re.split(r'###\s+\d+\.', text)
    for entry in entries:
        if not entry.strip():
            continue

        trial = {'phase': phase_label}

        nct_match = re.search(r'(NCT\d{8})', entry)
        if nct_match:
            trial['nct_id'] = nct_match.group(1)

        title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|$)', entry)
        if title_match:
            trial['title'] = title_match.group(1).strip()

        status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?:\n|$)', entry)
        if status_match:
            trial['status'] = status_match.group(1).strip()

        enroll_match = re.search(r'\*\*Enrollment:\*\*\s*(\d+)', entry)
        if enroll_match:
            trial['enrollment'] = int(enroll_match.group(1))
        else:
            trial['enrollment'] = 0

        sponsor_match = re.search(r'\*\*(?:Lead\s+)?Sponsor:\*\*\s*(.+?)(?:\n|$)', entry)
        if sponsor_match:
            trial['sponsor'] = sponsor_match.group(1).strip()

        # Extract interventions
        interventions = re.findall(r'###\s+(?:Drug|Biological):\s*(.+?)(?:\n|$)', entry)
        if interventions:
            trial['interventions'] = interventions

        # Primary outcome
        outcome_match = re.search(r'\*\*Primary\s+Outcome[s]?:\*\*\s*(.+?)(?:\n\*\*|\n###|\Z)', entry, re.DOTALL)
        if outcome_match:
            trial['primary_endpoints'] = outcome_match.group(1).strip()

        # Completion date
        completion_match = re.search(r'\*\*(?:Estimated\s+)?Completion[:\s]+(.+?)(?:\n|$)', entry)
        if completion_match:
            trial['estimated_completion'] = completion_match.group(1).strip()

        if trial.get('nct_id'):
            trials.append(trial)

    return trials


def _extract_design_patterns(benchmarks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract common design patterns across benchmark trials."""
    if not benchmarks:
        return {}

    total = len(benchmarks)
    phase_counts = {}
    sponsor_types = {'industry': 0, 'academic': 0, 'other': 0}
    avg_enrollment = 0
    endpoints_seen = []

    academic_keywords = ['university', 'hospital', 'institute', 'medical center', 'clinic']

    for b in benchmarks:
        phase = b.get('phase', 'Unknown')
        phase_counts[phase] = phase_counts.get(phase, 0) + 1

        avg_enrollment += b.get('enrollment', 0)

        sponsor = (b.get('sponsor') or '').lower()
        if any(kw in sponsor for kw in academic_keywords):
            sponsor_types['academic'] += 1
        elif sponsor:
            sponsor_types['industry'] += 1

        ep = b.get('primary_endpoints', '')
        if ep:
            endpoints_seen.append(ep[:200])

    avg_enrollment = avg_enrollment // max(total, 1)

    return {
        'total_benchmarks': total,
        'phase_distribution': phase_counts,
        'sponsor_types': sponsor_types,
        'average_enrollment': avg_enrollment,
        'sample_endpoints': endpoints_seen[:5],
    }
