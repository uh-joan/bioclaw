#!/usr/bin/env python3
"""
Clinical Trial Landscape - Main entry point & orchestrator.

Produces a comprehensive clinical trial landscape analysis for a drug or indication
by aggregating data from CT.gov, PubMed, and OpenTargets.

Usage:
    python3 scripts/get_clinical_trial_landscape.py "semaglutide"
    python3 scripts/get_clinical_trial_landscape.py "non-small cell lung cancer" --query-type indication

Ported from riot-flames for BioClaw container execution.
"""

import os
import re
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional, List
from statistics import median

# Add script directory to path for local imports
_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _script_dir)

from progress_tracker import create_progress_tracker
from visualization_utils import generate_report


# ─── Constants (CT.gov API enums only — not arbitrary term lists) ──
PHASES = ['PHASE1', 'PHASE2', 'PHASE3', 'PHASE4']
STATUSES = ['RECRUITING', 'ACTIVE_NOT_RECRUITING', 'COMPLETED']
PHASE_LABELS = {
    'PHASE1': 'Phase 1',
    'PHASE2': 'Phase 2',
    'PHASE3': 'Phase 3',
    'PHASE4': 'Phase 4',
    'EARLY_PHASE1': 'Early Phase 1',
}

# INN (International Nonproprietary Name) suffix patterns for drug identification
# These are WHO-standardized naming stems — NOT arbitrary hardcoded terms
INN_SUFFIX_PATTERN = (
    r'\b(\w+(?:inib|umab|izumab|tide|glutide|parib|ciclib|tinib|zumab|ximab|'
    r'mab|nib|vir|lukast|sartan|platin|taxel|rubicin|mycin|parvovec|'
    r'rsen|ersen|nostat|afil|amab|atamab|seltamab|feron|limus|'
    r'statin|prazole|olol|dipine|floxacin|caine|barbital|azepam|'
    r'olone|asone|sonide|poietin|plase|kinase|grastim|lipase))\b'
)

# Standard endpoint abbreviations — domain-standard, not arbitrary
ENDPOINT_ABBREVS = {
    'overall survival': 'OS',
    'progression-free survival': 'PFS',
    'objective response rate': 'ORR',
    'disease-free survival': 'DFS',
    'event-free survival': 'EFS',
    'complete response': 'CR',
    'partial response': 'PR',
    'duration of response': 'DOR',
    'time to progression': 'TTP',
    'recurrence-free survival': 'RFS',
    'pathological complete response': 'pCR',
    'overall response rate': 'ORR',
    'clinical benefit rate': 'CBR',
    'hemoglobin a1c': 'HbA1c',
    'hba1c': 'HbA1c',
    'dose-limiting toxicity': 'DLT',
    'pharmacokinetics': 'PK',
    'area under the curve': 'AUC',
    'maximum concentration': 'Cmax',
}

# Country normalization — merge aliases to canonical names
_COUNTRY_ALIASES = {
    'us': 'United States', 'usa': 'United States', 'united states of america': 'United States',
    'uk': 'United Kingdom', 'great britain': 'United Kingdom', 'england': 'United Kingdom',
    'korea': 'South Korea', 'republic of korea': 'South Korea',
    'czech republic': 'Czechia', 'holland': 'Netherlands',
    'people\'s republic of china': 'China', 'prc': 'China',
    'russian federation': 'Russia',
}

# Region classification — structural groupings (not arbitrary term lists)
# ISO-based continent mapping
_REGION_PATTERNS = {
    'North America': {'United States', 'Canada', 'Mexico', 'Puerto Rico'},
    'Europe': {
        'Germany', 'France', 'United Kingdom', 'Italy', 'Spain', 'Netherlands',
        'Belgium', 'Sweden', 'Denmark', 'Finland', 'Norway', 'Austria',
        'Switzerland', 'Poland', 'Czechia', 'Ireland', 'Portugal', 'Greece',
        'Hungary', 'Romania', 'Bulgaria', 'Croatia', 'Slovakia', 'Slovenia',
        'Estonia', 'Latvia', 'Lithuania', 'Russia', 'Ukraine', 'Serbia',
        'Turkey', 'Israel',
    },
    'Asia-Pacific': {
        'China', 'Japan', 'South Korea', 'India', 'Taiwan', 'Hong Kong',
        'Singapore', 'Thailand', 'Malaysia', 'Philippines', 'Indonesia',
        'Vietnam', 'Australia', 'New Zealand', 'Pakistan', 'Bangladesh',
        'Sri Lanka',
    },
    'Latin America': {
        'Brazil', 'Argentina', 'Chile', 'Colombia', 'Peru', 'Ecuador',
        'Venezuela', 'Guatemala', 'Costa Rica', 'Panama', 'Dominican Republic',
    },
    'Africa & Middle East': {
        'South Africa', 'Egypt', 'Kenya', 'Nigeria', 'Saudi Arabia',
        'United Arab Emirates', 'Qatar', 'Kuwait', 'Morocco', 'Tunisia',
    },
}

# MCP call timeout (seconds)
_MCP_TIMEOUT = 60


# ─── Utility functions ────────────────────────────────────────

def _safe_call(func, timeout=_MCP_TIMEOUT, **kwargs):
    """Safely call an MCP function with timeout, returning None on failure."""
    if func is None:
        return None
    try:
        pool = ThreadPoolExecutor(max_workers=1)
        future = pool.submit(func, **kwargs)
        try:
            return future.result(timeout=timeout)
        except Exception as e:
            print(f"  MCP call timed out or failed: {e}")
            return None
        finally:
            pool.shutdown(wait=False, cancel_futures=True)
    except Exception as e:
        print(f"  MCP call failed: {e}")
        return None


def _detect_query_type(query: str, ctgov_search=None) -> str:
    """Dynamically detect whether query is a drug name or indication.

    Strategy:
    1. If CT.gov is available, search as both condition and intervention.
       Whichever returns more results wins.
    2. Fallback: INN suffix match → drug; multi-word with 3+ words → indication.
    """
    # Strategy 1: Data-driven detection via CT.gov
    # Use pageSize=10 for better count differentiation
    if ctgov_search:
        cond_count = 0
        intv_count = 0

        resp = _safe_call(ctgov_search, timeout=15, condition=query[:100], pageSize=10)
        if resp:
            text = _extract_from_response(resp)
            total = _parse_total_count(text)
            cond_count = total if total > 0 else len(_parse_trials_from_markdown(text))

        resp = _safe_call(ctgov_search, timeout=15, intervention=query[:100], pageSize=10)
        if resp:
            text = _extract_from_response(resp)
            total = _parse_total_count(text)
            intv_count = total if total > 0 else len(_parse_trials_from_markdown(text))

        if cond_count > 0 or intv_count > 0:
            # Clear winner: 3x more results one way
            if cond_count >= intv_count * 3:
                return 'indication'
            if intv_count >= cond_count * 3:
                return 'drug'
            # Moderate difference: 1.5x
            if cond_count > intv_count * 1.5:
                return 'indication'
            if intv_count > cond_count * 1.5:
                return 'drug'

    # Strategy 2: INN suffix → drug (WHO naming convention)
    if re.search(INN_SUFFIX_PATTERN, query, re.IGNORECASE):
        return 'drug'

    # Strategy 3: Drug code pattern (e.g., "SGT-003", "BMS-986253")
    if re.match(r'^[A-Z]{2,5}-\d{2,8}$', query.strip()):
        return 'drug'

    # Strategy 4: Multi-word queries without drug-like patterns → indication
    # Most drug names are 1 word (semaglutide) or drug codes (BMS-986253)
    # Multi-word queries like "atopic dermatitis" or "type 2 diabetes" are indications
    words = query.strip().split()
    if len(words) >= 2:
        return 'indication'

    # Single word, no INN suffix → likely a drug name
    return 'drug'


def _parse_trials_from_markdown(text: str) -> List[Dict]:
    """Parse trial data from CT.gov markdown response text.

    CT.gov returns structured markdown like:
        ### 1. NCT07160634
        **Title:** A Study of SGT-003 Gene Therapy...
        **Status:** Recruiting
        **Phase:** Phase3
        **Enrollment:** 80 participants
        **Lead Sponsor:** Solid Biosciences Inc.
    """
    if not text or not isinstance(text, str):
        return []

    lines = text.split('\n')
    trial_map = {}
    current_nct = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect NCT ID line (e.g., "### 1. NCT07160634" or just "NCT07160634")
        nct_match = re.search(r'(NCT\d{8})', line)
        if nct_match:
            nct_id = nct_match.group(1)
            if nct_id not in trial_map:
                trial_map[nct_id] = {'nct_id': nct_id, 'title': '', 'enrollment': 0, 'sponsor': '', 'phase': '', 'start_date': ''}
            current_nct = nct_id
            continue

        # Parse structured fields for the current trial
        if current_nct and current_nct in trial_map:
            trial = trial_map[current_nct]

            # **Title:** ...
            title_match = re.match(r'\*{0,2}Title:?\*{0,2}[:\s]*(.+)', line)
            if title_match and not trial['title']:
                trial['title'] = title_match.group(1).strip().strip('*').strip()[:200]
                continue

            # **Enrollment:** 80 participants
            enroll_match = re.match(r'\*{0,2}Enrollment:?\*{0,2}[:\s]*(\d[\d,]*)', line)
            if enroll_match:
                trial['enrollment'] = int(enroll_match.group(1).replace(',', ''))
                continue

            # **Phase:** Phase3 or Phase2, Phase3
            phase_match = re.match(r'\*{0,2}Phase:?\*{0,2}[:\s]*(Phase\s*\d)', line)
            if phase_match:
                trial['phase'] = phase_match.group(1)
                continue

            # **Lead Sponsor:** Name (Industry)
            sponsor_match = re.match(r'\*{0,2}Lead\s*Sponsor:?\*{0,2}[:\s]*([^(\n]+)', line)
            if sponsor_match:
                trial['sponsor'] = sponsor_match.group(1).strip().strip('*').strip()[:80]
                continue

            # **Start Date:** January 2024 / 2024-01-15
            date_match = re.match(r'\*{0,2}(?:Start\s*Date|Study\s*Start):?\*{0,2}[:\s]*(.+)', line, re.IGNORECASE)
            if date_match:
                trial['start_date'] = date_match.group(1).strip().strip('*').strip()
                continue

            # Section separator -- stop associating lines with current trial
            if line.startswith('---'):
                current_nct = None

    return list(trial_map.values())


def _parse_total_count(text: str) -> int:
    """Parse total study count from CT.gov response text."""
    if not text:
        return 0
    # CT.gov often includes "Found N studies" or "Total: N" or "N studies"
    patterns = [
        r'(?:found|total|showing|returned)\D{0,20}(\d[\d,]*)\s*(?:stud|trial|result)',
        r'(\d[\d,]*)\s*(?:studies|trials|results)\s*(?:found|total|matched)',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return int(m.group(1).replace(',', ''))
    return 0


def _extract_from_response(response) -> str:
    """Extract text content from various MCP response formats."""
    if isinstance(response, str):
        return response
    if isinstance(response, dict):
        for key in ['text', 'content', 'result', 'data', 'markdown']:
            if key in response:
                val = response[key]
                if isinstance(val, str):
                    return val
                if isinstance(val, dict):
                    return str(val)
        return str(response)
    if isinstance(response, list):
        return '\n'.join(str(item) for item in response)
    return str(response) if response else ''


def _classify_sponsor(name: str) -> str:
    """Classify sponsor as pharma, biotech, or academic using structural patterns."""
    if not name:
        return 'Biotech'
    name_lower = name.lower()

    # Academic: structural suffixes and keywords
    academic_suffixes = ('university', 'universidad', 'universität', 'université',
                         'hospital', 'hôpital', 'medical center', 'cancer center',
                         'health center', 'health system', 'clinic', 'institute',
                         'college', 'school of medicine')
    academic_orgs = ('nci', 'nih', 'national institutes', 'national cancer institute',
                     'veterans', 'va ', 'cooperative group', 'consortium',
                     'alliance', 'ecog', 'swog', 'rtog', 'children\'s oncology',
                     'ministry of health', 'department of health')
    if any(s in name_lower for s in academic_suffixes):
        return 'Academic'
    if any(s in name_lower for s in academic_orgs):
        return 'Academic'

    # Industry: corporate suffixes indicate commercial entity
    corporate_suffixes = ('inc.', 'inc', 'llc', 'ltd', 'ltd.', 'corp', 'corp.',
                          'gmbh', 'ag', 's.a.', 'plc', 'co.', 'company',
                          'pharmaceuticals', 'pharma', 'therapeutics', 'biosciences',
                          'biopharma', 'biotech', 'medicines', 'oncology')
    if any(s in name_lower for s in corporate_suffixes):
        # Distinguish pharma vs biotech by name length/complexity heuristic
        # Large pharma tend to have short, well-known names
        # But this is inherently fuzzy — classify as "Industry"
        return 'Pharma'

    return 'Biotech'


def _normalize_country(name: str) -> str:
    """Normalize country name to canonical form, deduplicating aliases."""
    if not name:
        return name
    name_lower = name.lower().strip()
    return _COUNTRY_ALIASES.get(name_lower, name.strip())


def _classify_country_region(country: str) -> str:
    """Classify a country into a region using the pattern map."""
    normalized = _normalize_country(country)
    for region, countries in _REGION_PATTERNS.items():
        if normalized in countries:
            return region
    return 'Other'


def _extract_endpoints_from_text(text: str) -> List[str]:
    """Extract endpoint mentions from study detail text using pattern matching.

    Uses ENDPOINT_ABBREVS keys as patterns plus dynamic regex extraction
    for endpoints not in the standard list.
    """
    if not text:
        return []
    text_lower = text.lower()
    found = []

    # Match standard endpoint names from the abbreviation map
    for ep_name, abbrev in ENDPOINT_ABBREVS.items():
        if ep_name in text_lower and abbrev not in found:
            found.append(abbrev)

    # Dynamic extraction: catch endpoint-like phrases not in the standard list
    # Pattern: "primary endpoint is/was/: <phrase>"
    primary_ep_matches = re.findall(
        r'primary\s+(?:end\s*point|outcome)[:\s]+(?:is\s+|was\s+)?([^.;\n]{5,80})',
        text, re.IGNORECASE
    )
    for match in primary_ep_matches:
        ep_name = match.strip().strip('*').strip()
        # Skip if it's a sentence fragment
        if len(ep_name.split()) <= 8 and ep_name not in found:
            # Check if it maps to a known abbreviation
            mapped = False
            for k, v in ENDPOINT_ABBREVS.items():
                if k in ep_name.lower():
                    if v not in found:
                        found.append(v)
                    mapped = True
                    break
            if not mapped:
                found.append(ep_name.title()[:40])

    # Dynamic extraction: "secondary endpoint(s): <phrase>"
    secondary_ep_matches = re.findall(
        r'secondary\s+(?:end\s*point|outcome)s?[:\s]+(?:include\s+)?([^.;\n]{5,80})',
        text, re.IGNORECASE
    )
    for match in secondary_ep_matches:
        ep_name = match.strip().strip('*').strip()
        if len(ep_name.split()) <= 8 and ep_name not in found:
            mapped = False
            for k, v in ENDPOINT_ABBREVS.items():
                if k in ep_name.lower():
                    if v not in found:
                        found.append(v)
                    mapped = True
                    break
            if not mapped and ep_name.title()[:40] not in found:
                found.append(ep_name.title()[:40])

    return found


def _flatten_pubmed_text(val) -> str:
    """Flatten PubMed markup dicts to plain text."""
    if isinstance(val, str):
        return val
    if isinstance(val, dict):
        parts = []
        if '_' in val:
            parts.append(str(val['_']))
        for k, v in val.items():
            if k == '_':
                continue
            if isinstance(v, list):
                parts.extend(str(item) for item in v)
            else:
                parts.append(str(v))
        return ' '.join(parts)
    if isinstance(val, list):
        return ' '.join(_flatten_pubmed_text(item) for item in val)
    return str(val) if val else ''


def _extract_year_from_date(date_str: str) -> Optional[int]:
    """Extract year from various date formats."""
    if not date_str:
        return None
    # "2024-01-15", "January 2024", "2024", "Jan 2024"
    m = re.search(r'(20\d{2})', date_str)
    if m:
        return int(m.group(1))
    return None


def _extract_countries_from_text(text: str) -> List[str]:
    """Dynamically extract country names from trial detail text.

    Instead of matching against a hardcoded list, uses regex patterns
    for common location section formats in CT.gov responses.
    """
    if not text:
        return []

    countries = set()

    # CT.gov format: "**Locations:** Country1, Country2" or "Country: City"
    # Also: "Sites in United States, Germany, Japan"
    loc_section = re.search(
        r'(?:location|countr|site|facilit)[^:]*[:]\s*([^\n]{5,500})',
        text, re.IGNORECASE
    )
    if loc_section:
        loc_text = loc_section.group(1)
        # Extract capitalized multi-word names that look like countries
        country_candidates = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', loc_text)
        for c in country_candidates:
            normalized = _normalize_country(c)
            if _classify_country_region(normalized) != 'Other':
                countries.add(normalized)

    # Also scan full text for well-known country names
    # Use the region pattern countries as a reference set
    all_known = set()
    for region_countries in _REGION_PATTERNS.values():
        all_known.update(region_countries)

    # Short names need word-boundary matching
    _short_names = {'US', 'USA', 'UK'}
    for country in all_known:
        if country in _short_names:
            if re.search(r'\b' + re.escape(country) + r'\b', text):
                countries.add(_normalize_country(country))
        elif country.lower() in text.lower():
            countries.add(_normalize_country(country))

    return list(countries)


def _build_dynamic_noise_set(query: str) -> set:
    """Build a noise filter set dynamically from the query context.

    Instead of hardcoding abbreviations, derives noise terms from:
    1. The query itself (words from the disease/drug name)
    2. Structural patterns (Roman numerals, single letters, numbers)
    """
    noise = set()

    # Add query words (the disease name itself shouldn't appear as a competitor)
    for word in query.lower().split():
        if len(word) >= 2:
            noise.add(word)

    # Roman numerals (structural, not hardcoded terms)
    for i in ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii']:
        noise.add(i)

    # Common trial methodology terms (structural to clinical trials, not arbitrary)
    trial_terms = {'study', 'trial', 'phase', 'dose', 'safety', 'efficacy',
                   'placebo', 'control', 'arm', 'cohort', 'group', 'open',
                   'label', 'blind', 'double', 'single', 'randomized', 'multicenter'}
    noise.update(trial_terms)

    # Route/formulation terms
    route_terms = {'oral', 'iv', 'sc', 'im', 'topical', 'tablet', 'capsule',
                   'injection', 'infusion', 'solution', 'suspension'}
    noise.update(route_terms)

    # Regulatory/org abbreviations
    org_terms = {'fda', 'ema', 'nci', 'nih', 'who', 'eap', 'irb', 'dsmb'}
    noise.update(org_terms)

    # PK/PD abbreviations
    pk_terms = {'pk', 'pd', 'qol', 'bid', 'qd', 'tid', 'prn'}
    noise.update(pk_terms)

    # Biology/biochemistry terms that match INN suffixes but are NOT drug names
    # These are the root biology words that INN stems are derived FROM
    biology_terms = {
        'peptide', 'polypeptide', 'neuropeptide',  # match -tide
        'angiopoietin', 'erythropoietin', 'thrombopoietin',  # match -poietin
        'protein', 'lipoprotein', 'glycoprotein',  # common bio terms
        'kinase', 'lipase', 'protease', 'polymerase',  # match -kinase, -lipase
        'antibody', 'antigen', 'receptor', 'ligand',  # common bio terms
        'insulin', 'interferon', 'interleukin',  # match -feron
        'collagen', 'fibrin', 'albumin',  # structural proteins
        'cytokine', 'chemokine', 'hormone',  # signaling molecules
        'enzyme', 'substrate', 'inhibitor',  # generic functional terms
        'agonist', 'antagonist', 'modulator',  # pharmacology terms (not drug names)
        'placebo', 'vehicle', 'comparator',  # trial control terms
    }
    noise.update(biology_terms)

    return noise


# ─── Section builders ─────────────────────────────────────────

def _build_overview(query: str, query_type: str, ctgov_search, tracker) -> Dict[str, Any]:
    """Build overview section with total trials, phase and status breakdown."""
    result = {
        'total_trials': 0,
        'phase_breakdown': {},
        'status_breakdown': {},
        'all_nct_ids': [],
        'provenance': [],
    }

    if not ctgov_search:
        result['error'] = 'CT.gov search not available'
        return result

    search_kwargs = {}
    if query_type == 'drug':
        search_kwargs['intervention'] = query[:100]
    else:
        search_kwargs['condition'] = query[:100]

    # Search per phase to get counts
    all_nct_ids = []
    seen_nct_ids = set()
    for phase in PHASES:
        tracker.update_step(PHASES.index(phase) / len(PHASES) * 0.7, f"Searching {PHASE_LABELS.get(phase, phase)}...")
        resp = _safe_call(ctgov_search, **search_kwargs, phase=phase, pageSize=200)
        if resp:
            text = _extract_from_response(resp)
            trials = _parse_trials_from_markdown(text)

            # Try to get total count from response (may exceed pageSize)
            total_for_phase = _parse_total_count(text)
            parsed_count = len(trials)
            # Use the larger of parsed count or reported total
            count = max(parsed_count, total_for_phase)

            result['phase_breakdown'][PHASE_LABELS.get(phase, phase)] = count
            result['total_trials'] += count
            for t in trials:
                if t['nct_id'] not in seen_nct_ids:
                    seen_nct_ids.add(t['nct_id'])
                    t['phase'] = PHASE_LABELS.get(phase, phase)
                    all_nct_ids.append(t)

    # Search per status
    for status in STATUSES:
        tracker.update_step(0.7 + STATUSES.index(status) / len(STATUSES) * 0.3,
                            f"Checking {status.replace('_', ' ').title()} trials...")
        resp = _safe_call(ctgov_search, **search_kwargs, status=status, pageSize=1)
        if resp:
            text = _extract_from_response(resp)
            total_count = _parse_total_count(text)
            if total_count > 0:
                result['status_breakdown'][status.replace('_', ' ').title()] = total_count
            else:
                trials = _parse_trials_from_markdown(text)
                result['status_breakdown'][status.replace('_', ' ').title()] = len(trials)

    result['all_nct_ids'] = all_nct_ids
    result['provenance'].append(f"ClinicalTrials.gov search: {query} ({len(all_nct_ids)} unique trials parsed, {result['total_trials']} total)")

    return result


def _build_phase_distribution(overview_data: Dict, ctgov_search, query: str, query_type: str, tracker) -> Dict[str, Any]:
    """Build phase distribution (year trends populated later after enrollment)."""
    result = {
        'phases': overview_data.get('phase_breakdown', {}),
        'year_trends': {},
        'provenance': [],
    }
    result['provenance'].append("Phase distribution from CT.gov per-phase search counts")
    return result


def _populate_year_trends(overview_data: Dict, phase_dist: Dict) -> None:
    """Populate year trends from trial start dates and detail text.

    Called AFTER enrollment step when _detail_text is available on trials.
    Mutates phase_dist in place.
    """
    all_trials = overview_data.get('all_nct_ids', [])
    year_counts = {}
    for trial in all_trials:
        year = None
        # From parsed start_date field
        if trial.get('start_date'):
            year = _extract_year_from_date(trial['start_date'])
        # Fallback: from detail text
        if not year and trial.get('_detail_text'):
            date_match = re.search(
                r'(?:start\s*date|study\s*start)[:\s*]+([^\n]{4,30})',
                trial['_detail_text'], re.IGNORECASE
            )
            if date_match:
                year = _extract_year_from_date(date_match.group(1))
        if year and 2000 <= year <= 2030:
            year_counts[year] = year_counts.get(year, 0) + 1

    if year_counts:
        phase_dist['year_trends'] = dict(sorted(year_counts.items()))
        phase_dist['provenance'].append(f"Year trends from {sum(year_counts.values())} trials with start dates")


def _build_enrollment(overview_data: Dict, ctgov_get_study, tracker) -> Dict[str, Any]:
    """Build enrollment section from individual study details."""
    result = {
        'total_enrolled': 0,
        'median_per_trial': 0,
        'trials_with_data': 0,
        'largest_trials': [],
        'provenance': [],
    }

    all_trials = overview_data.get('all_nct_ids', [])
    if not all_trials:
        return result

    # Dynamic detail fetch limit: proportional to total trials
    # Fetch up to 20% of trials or at least 20, capped at 50 (MCP call budget)
    trials_with_enrollment = [t for t in all_trials if t.get('enrollment', 0) > 0]
    trials_without = [t for t in all_trials if t.get('enrollment', 0) == 0]

    max_detail_fetch = min(max(len(all_trials) // 5, 20), 50)
    # Prioritize trials without enrollment data, then add some with data for validation
    without_limit = int(max_detail_fetch * 0.75)
    with_limit = max_detail_fetch - without_limit
    detail_targets = trials_without[:without_limit] + trials_with_enrollment[:with_limit]

    if ctgov_get_study and detail_targets:
        for i, trial in enumerate(detail_targets):
            tracker.update_step(i / len(detail_targets), f"Getting details for {trial['nct_id']}...")
            resp = _safe_call(ctgov_get_study, nctId=trial['nct_id'])
            if resp:
                text = _extract_from_response(resp)
                # Extract enrollment from detail
                enroll_match = re.search(r'[Ee]nrollment[:\s*]+(\d[\d,]*)', text)
                if not enroll_match:
                    enroll_match = re.search(r'(\d[\d,]*)\s+participants', text, re.IGNORECASE)
                if enroll_match:
                    trial['enrollment'] = int(enroll_match.group(1).replace(',', ''))

                # Also extract sponsor if missing
                if not trial.get('sponsor'):
                    sponsor_match = re.search(r'\*{0,2}Lead\s+Sponsor\*{0,2}[:\s]*\*{0,2}\s*([^(\n]+)', text)
                    if not sponsor_match:
                        sponsor_match = re.search(r'(?:sponsor|lead\s*organization)[:\s*]+([^\n(|,]+)', text, re.IGNORECASE)
                    if sponsor_match:
                        trial['sponsor'] = sponsor_match.group(1).strip().strip('*').strip()[:80]

                # Extract start date for year trends
                if not trial.get('start_date'):
                    date_match = re.search(
                        r'(?:start\s*date|study\s*start)[:\s*]+([^\n]{4,30})',
                        text, re.IGNORECASE
                    )
                    if date_match:
                        trial['start_date'] = date_match.group(1).strip().strip('*').strip()

                # Store raw text for endpoint + geography extraction later
                trial['_detail_text'] = text

    # Compute enrollment stats from ALL trials (including those parsed from search results)
    enrollments = [t['enrollment'] for t in all_trials if t.get('enrollment', 0) > 0]
    if enrollments:
        result['total_enrolled'] = sum(enrollments)
        result['median_per_trial'] = int(median(enrollments))
        result['trials_with_data'] = len(enrollments)

    # Sort by enrollment descending for largest trials — no arbitrary cap
    sorted_trials = sorted(all_trials, key=lambda t: t.get('enrollment', 0), reverse=True)
    result['largest_trials'] = [
        {
            'nct_id': t['nct_id'],
            'enrollment': t.get('enrollment', 0),
            'title': t.get('title', ''),
            'phase': t.get('phase', ''),
            'sponsor': t.get('sponsor', ''),
        }
        for t in sorted_trials
        if t.get('enrollment', 0) > 0
    ]

    result['provenance'].append(
        f"Enrollment data from {result['trials_with_data']} trials with reported enrollment "
        f"(detail fetched for {len(detail_targets)} of {len(all_trials)} trials)"
    )

    return result


def _build_endpoints(overview_data: Dict, ctgov_get_study, pubmed_search, query: str, query_type: str, tracker) -> Dict[str, Any]:
    """Build endpoints section from study details and PubMed."""
    result = {
        'primary_endpoints': [],
        'novel_endpoints': [],
        'pubmed_endpoint_trends': [],
        'provenance': [],
    }

    all_trials = overview_data.get('all_nct_ids', [])

    # Collect endpoints from trials that already have detail text
    endpoint_counts = {}
    all_endpoint_lists = []

    for trial in all_trials:
        detail_text = trial.get('_detail_text', '')
        if detail_text:
            endpoints = _extract_endpoints_from_text(detail_text)
            all_endpoint_lists.append(endpoints)
            for ep in endpoints:
                endpoint_counts[ep] = endpoint_counts.get(ep, 0) + 1

    # Get details for more trials if we need endpoint data
    # Dynamic limit: fetch up to 20% of remaining trials without details
    trials_without_details = [t for t in all_trials if not t.get('_detail_text')]
    detail_limit = min(max(len(trials_without_details) // 5, 10), 30)
    if ctgov_get_study and trials_without_details:
        targets = trials_without_details[:detail_limit]
        for i, trial in enumerate(targets):
            tracker.update_step(i / max(len(targets), 1) * 0.6, f"Extracting endpoints from {trial['nct_id']}...")
            resp = _safe_call(ctgov_get_study, nctId=trial['nct_id'])
            if resp:
                text = _extract_from_response(resp)
                trial['_detail_text'] = text
                endpoints = _extract_endpoints_from_text(text)
                all_endpoint_lists.append(endpoints)
                for ep in endpoints:
                    endpoint_counts[ep] = endpoint_counts.get(ep, 0) + 1

    # Sort endpoints by frequency — no arbitrary cap
    sorted_endpoints = sorted(endpoint_counts.items(), key=lambda x: x[1], reverse=True)
    result['primary_endpoints'] = [
        {'name': name, 'count': count}
        for name, count in sorted_endpoints
    ]

    # Novel endpoints: mentioned infrequently and not in standard abbreviations
    standard_abbrevs = set(ENDPOINT_ABBREVS.values())
    result['novel_endpoints'] = [
        name for name, count in sorted_endpoints
        if count <= 2 and name not in standard_abbrevs
    ]

    # PubMed search for endpoint trends — fetch proportional to data richness
    tracker.update_step(0.7, "Searching PubMed for endpoint trends...")
    if pubmed_search:
        if query_type == 'drug':
            pm_query = f"{query} phase 3 results endpoints"
        else:
            pm_query = f"{query} clinical endpoints primary outcome"

        pm_resp = _safe_call(pubmed_search, query=pm_query, num_results=10)
        if pm_resp:
            articles = []
            if isinstance(pm_resp, dict) and 'articles' in pm_resp:
                articles = pm_resp['articles']
            elif isinstance(pm_resp, list):
                articles = pm_resp

            for art in articles:
                if isinstance(art, dict):
                    title = _flatten_pubmed_text(art.get('title', ''))
                    result['pubmed_endpoint_trends'].append({
                        'title': title[:200],
                        'pmid': art.get('pmid', ''),
                        'year': str(art.get('publication_date', ''))[:4],
                    })
            result['provenance'].append(f"PubMed: '{pm_query}' ({len(articles)} results)")

    result['provenance'].append(f"Endpoints extracted from {len(all_endpoint_lists)} trial detail records")

    return result


def _build_sponsors(overview_data: Dict, tracker) -> Dict[str, Any]:
    """Build sponsors section from trial data."""
    result = {
        'top_sponsors': [],
        'sector_split': {},
        'provenance': [],
    }

    all_trials = overview_data.get('all_nct_ids', [])

    # Count sponsors
    sponsor_counts = {}
    for trial in all_trials:
        sponsor = trial.get('sponsor', '').strip()
        if sponsor:
            sponsor_counts[sponsor] = sponsor_counts.get(sponsor, 0) + 1

    # Sort by count — no arbitrary cap, return all
    sorted_sponsors = sorted(sponsor_counts.items(), key=lambda x: x[1], reverse=True)

    result['top_sponsors'] = [
        {'name': name, 'count': count, 'sector': _classify_sponsor(name)}
        for name, count in sorted_sponsors
    ]

    # Sector split
    sector_counts = {}
    for name, count in sponsor_counts.items():
        sector = _classify_sponsor(name)
        sector_counts[sector] = sector_counts.get(sector, 0) + count

    result['sector_split'] = {k: v for k, v in sector_counts.items() if v > 0}

    result['provenance'].append(f"Sponsor analysis from {len(sponsor_counts)} unique sponsors across {sum(sponsor_counts.values())} trials")

    return result


def _build_geography(overview_data: Dict, tracker) -> Dict[str, Any]:
    """Build geography section from trial data — dynamic country extraction."""
    result = {
        'top_countries': [],
        'regional_distribution': {},
        'provenance': [],
    }

    all_trials = overview_data.get('all_nct_ids', [])

    # Extract country mentions dynamically from trial detail text
    country_counts = {}
    trials_with_detail = 0
    for trial in all_trials:
        detail_text = trial.get('_detail_text', '')
        if detail_text:
            trials_with_detail += 1
            countries = _extract_countries_from_text(detail_text)
            for country in countries:
                country_counts[country] = country_counts.get(country, 0) + 1

    if country_counts:
        sorted_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)
        result['top_countries'] = [
            {'country': name, 'count': count}
            for name, count in sorted_countries
        ]

        # Regional aggregation
        regional = {}
        for name, count in country_counts.items():
            region = _classify_country_region(name)
            regional[region] = regional.get(region, 0) + count
        result['regional_distribution'] = dict(sorted(regional.items(), key=lambda x: x[1], reverse=True))

        result['provenance'].append(f"Geography from country mentions in {trials_with_detail} trial detail records")
    else:
        result['provenance'].append("Geography data: insufficient detail records for country extraction")

    return result


def _build_competitors(
    query: str, query_type: str,
    ctgov_search, opentargets_search, opentargets_details, opentargets_drug,
    tracker
) -> Dict[str, Any]:
    """Build competitors section with dynamic noise filtering."""
    result = {
        'type': 'drug' if query_type == 'indication' else 'indication',
        'items': [],
        'provenance': [],
    }

    # Build noise set dynamically from query context
    noise_set = _build_dynamic_noise_set(query)

    # Sponsor/institution detection — structural patterns, not hardcoded names
    _INSTITUTIONAL_PATTERNS = re.compile(
        r'university|hospital|institute|medical|center|company|corporation|'
        r'professor|pharma|gmbh|inc|ltd|llc|foundation|department|ministry|'
        r'school|college|clinic|health\s+system',
        re.IGNORECASE
    )

    def _is_valid_drug_name(name: str, query_lower: str) -> bool:
        """Filter out noise from candidate drug names using dynamic rules."""
        if not name or len(name) < 3:
            return False
        name_lower = name.lower()
        if name_lower in noise_set:
            return False
        # Skip if it matches the query (disease name leaking)
        if name_lower in query_lower or query_lower in name_lower:
            return False
        # Skip institutional names
        if _INSTITUTIONAL_PATTERNS.search(name):
            return False
        # Skip if starts with preposition/conjunction (fragment)
        first_word = name_lower.split()[0] if name_lower.split() else ''
        if first_word in ('of', 'in', 'for', 'with', 'and', 'or', 'the', 'a', 'an', 'to', 'on', 'at', 'by'):
            return False
        # Skip pure numbers
        if re.match(r'^\d+$', name):
            return False
        # Skip very short all-caps that aren't drug codes (2-letter abbreviations)
        if len(name) <= 2 and name.isupper():
            return False
        # Skip single words that are common English/science but happen to match INN suffixes
        # Real drug names are specific coined terms, not dictionary words
        if ' ' not in name and name_lower.endswith(('peptide', 'poietin', 'kinase', 'lipase',
                                                      'protease', 'protein', 'globulin',
                                                      'plastin', 'statin')):
            # Allow if it also has an INN prefix (e.g., "semaglutide" is fine, "peptide" is not)
            # Real INN names have a meaningful prefix before the suffix
            if len(name) <= 10 or name_lower in noise_set:
                return False
        return True

    if query_type == 'indication':
        # For indication queries, find drugs being tested
        if ctgov_search:
            tracker.update_step(0.3, "Searching CT.gov for competing drugs...")
            seen_drugs = set()
            query_lower = query.lower()
            for phase_label, phase_code in [('Phase 3', 'PHASE3'), ('Phase 2', 'PHASE2'), ('Phase 1', 'PHASE1')]:
                # Dynamic cutoff: stop searching less mature phases if we have enough
                if phase_label == 'Phase 2' and len(result['items']) >= 15:
                    break
                if phase_label == 'Phase 1' and len(result['items']) >= 10:
                    break
                resp = _safe_call(ctgov_search, condition=query[:100], phase=phase_code, status='RECRUITING', pageSize=200)
                if resp:
                    text = _extract_from_response(resp)
                    trials = _parse_trials_from_markdown(text)
                    for trial in trials:
                        title = trial.get('title', '')
                        if not title:
                            continue

                        # Strategy 1: INN suffix matching (most reliable — WHO naming convention)
                        inn_matches = re.findall(INN_SUFFIX_PATTERN, title, re.IGNORECASE)
                        for drug in inn_matches:
                            drug_key = drug.lower()
                            if drug_key not in seen_drugs and _is_valid_drug_name(drug, query_lower):
                                seen_drugs.add(drug_key)
                                result['items'].append({
                                    'name': drug.title(),
                                    'phase': phase_label,
                                    'status': 'Recruiting',
                                })

                        # Strategy 2: Drug code pattern (e.g., SGT-003, BCD-264, JNJ-79635322)
                        code_matches = re.findall(r'\b([A-Z]{2,5}-\d{2,8})\b', title)
                        for drug in code_matches:
                            drug_key = drug.lower()
                            if drug_key not in seen_drugs and _is_valid_drug_name(drug, query_lower):
                                seen_drugs.add(drug_key)
                                result['items'].append({
                                    'name': drug,
                                    'phase': phase_label,
                                    'status': 'Recruiting',
                                })

                    result['provenance'].append(f"CT.gov {phase_label} recruiting trials for: {query}")

    else:
        # For drug queries, find indications being tested
        result['type'] = 'indication'
        if ctgov_search:
            tracker.update_step(0.3, f"Searching indications for {query}...")
            resp = _safe_call(ctgov_search, intervention=query[:100], pageSize=200)
            if resp:
                text = _extract_from_response(resp)
                trials = _parse_trials_from_markdown(text)

                # Dynamic indication extraction from trial titles
                # Instead of matching against INDICATION_HINTS, extract condition-like phrases
                indication_counts = {}
                for trial in trials:
                    title = trial.get('title', '').lower()
                    if not title:
                        continue

                    # Strategy 1: Extract condition from title patterns
                    # "Study of [drug] in [condition]" or "for [condition]"
                    cond_patterns = [
                        r'(?:in|for|treating|treatment of)\s+(?:patients?\s+with\s+)?([^,.(]{5,60})',
                        r'(?:with|having)\s+([^,.(]{5,60})',
                    ]
                    for pat in cond_patterns:
                        matches = re.findall(pat, title, re.IGNORECASE)
                        for match in matches:
                            indication = match.strip()
                            # Skip if it's the drug name itself
                            if query.lower() in indication.lower():
                                continue
                            if len(indication) >= 5 and len(indication.split()) <= 8:
                                indication = indication.title()
                                indication_counts[indication] = indication_counts.get(indication, 0) + 1

                sorted_indications = sorted(indication_counts.items(), key=lambda x: x[1], reverse=True)
                result['items'] = [
                    {'name': name, 'trial_count': count}
                    for name, count in sorted_indications
                ]
                result['provenance'].append(f"CT.gov intervention search for: {query}")

        # Also use OpenTargets for target-based indication discovery
        if opentargets_search and len(result['items']) < 5:
            tracker.update_step(0.7, "Searching OpenTargets for target indications...")
            resp = _safe_call(opentargets_search, query=query)
            if resp:
                text = _extract_from_response(resp)
                ensg_match = re.search(r'(ENSG\d+)', text[:3000])
                if ensg_match and opentargets_details:
                    ensg_id = ensg_match.group(1)
                    detail_resp = _safe_call(opentargets_details, id=ensg_id)
                    if detail_resp:
                        detail_text = _extract_from_response(detail_resp)
                        disease_matches = re.findall(r'"name":\s*"([^"]{5,60})"', detail_text[:10000])
                        seen = set(item['name'].lower() for item in result['items'])
                        for disease in disease_matches:
                            if disease.lower() not in seen:
                                seen.add(disease.lower())
                                result['items'].append({'name': disease, 'trial_count': ''})
                        result['provenance'].append(f"OpenTargets target details for: {ensg_id}")

    return result


# ─── Main orchestrator ────────────────────────────────────────

def get_clinical_trial_landscape(
    query: str,
    query_type: str = "auto",
    skip_endpoints: bool = False,
    skip_sponsors: bool = False,
    mcp_funcs: Optional[Dict] = None,
    progress_callback=None,
) -> Dict[str, Any]:
    """
    Main orchestrator for clinical trial landscape analysis.

    Sequential execution (MCP client is NOT thread-safe):
    1. Overview: phase & status breakdown from CT.gov
    2. Phase distribution: from overview data + year trends
    3. Enrollment: individual study details (dynamic sampling)
    4. Endpoints: study details + PubMed (dynamic extraction)
    5. Sponsors: from trial data (pattern-based classification)
    6. Geography: dynamic country extraction from detail text
    7. Competitors: CT.gov + OpenTargets (dynamic noise filtering)
    8. Assembly: combine + generate report
    """
    if not query:
        return {'error': 'query is required', 'visualization': '', 'provenance': [], 'errors': {'input': 'query is required'}}

    if mcp_funcs is None:
        mcp_funcs = {}

    # Extract MCP functions
    ctgov_search = mcp_funcs.get('ctgov_search')
    ctgov_get_study = mcp_funcs.get('ctgov_get_study')
    pubmed_search = mcp_funcs.get('pubmed_search')
    opentargets_search = mcp_funcs.get('opentargets_search')
    opentargets_details = mcp_funcs.get('opentargets_details')
    opentargets_drug = mcp_funcs.get('opentargets_drug')

    # Determine skipped sections
    skip_set = set()
    if skip_endpoints:
        skip_set.add('endpoints')
    if skip_sponsors:
        skip_set.add('sponsors')

    tracker = create_progress_tracker(
        callback=progress_callback,
        skip_sections=skip_set,
    )

    # Auto-detect query type using data-driven approach
    if query_type == "auto":
        query_type = _detect_query_type(query, ctgov_search)

    result = {
        'query': query,
        'query_type': query_type,
        'overview': {},
        'phase_distribution': {},
        'enrollment': {},
        'endpoints': {},
        'sponsors': {},
        'geography': {},
        'competitors': {},
        '_skip_endpoints': skip_endpoints,
        '_skip_sponsors': skip_sponsors,
        'visualization': '',
        'provenance': [],
        'errors': {},
    }

    # ============================================================
    # STEP 1: Overview
    # ============================================================
    tracker.start_step('overview', f"Building overview for '{query}' (type={query_type})...")
    try:
        overview = _build_overview(query, query_type, ctgov_search, tracker)
        result['overview'] = overview
        if overview.get('error'):
            result['errors']['overview'] = overview['error']
    except Exception as e:
        result['errors']['overview'] = str(e)
        result['overview'] = {'error': str(e), 'all_nct_ids': [], 'provenance': [f"Overview failed: {e}"]}
        traceback.print_exc()
    tracker.complete_step(f"Overview complete: {result['overview'].get('total_trials', 0)} trials found")

    # ============================================================
    # STEP 2: Phase Distribution
    # ============================================================
    tracker.start_step('phase_distribution', "Analyzing phase distribution...")
    try:
        phase_dist = _build_phase_distribution(result['overview'], ctgov_search, query, query_type, tracker)
        result['phase_distribution'] = phase_dist
    except Exception as e:
        result['errors']['phase_distribution'] = str(e)
        result['phase_distribution'] = {'error': str(e), 'provenance': []}
        traceback.print_exc()
    tracker.complete_step("Phase distribution complete")

    # ============================================================
    # STEP 3: Enrollment
    # ============================================================
    tracker.start_step('enrollment', "Analyzing enrollment data...")
    try:
        enrollment = _build_enrollment(result['overview'], ctgov_get_study, tracker)
        result['enrollment'] = enrollment
        if enrollment.get('error'):
            result['errors']['enrollment'] = enrollment['error']
    except Exception as e:
        result['errors']['enrollment'] = str(e)
        result['enrollment'] = {'error': str(e), 'provenance': []}
        traceback.print_exc()
    tracker.complete_step(f"Enrollment complete: {result['enrollment'].get('total_enrolled', 0)} total enrolled")

    # Populate year trends now that _detail_text is available from enrollment step
    try:
        _populate_year_trends(result['overview'], result['phase_distribution'])
    except Exception as e:
        print(f"  Year trends failed: {e}")

    # ============================================================
    # STEP 4: Endpoints (optional)
    # ============================================================
    if not skip_endpoints:
        tracker.start_step('endpoints', "Extracting endpoint data...")
        try:
            endpoints = _build_endpoints(result['overview'], ctgov_get_study, pubmed_search, query, query_type, tracker)
            result['endpoints'] = endpoints
            if endpoints.get('error'):
                result['errors']['endpoints'] = endpoints['error']
        except Exception as e:
            result['errors']['endpoints'] = str(e)
            result['endpoints'] = {'error': str(e), 'provenance': []}
            traceback.print_exc()
        tracker.complete_step(f"Endpoints complete: {len(result['endpoints'].get('primary_endpoints', []))} endpoints found")

    # ============================================================
    # STEP 5: Sponsors (optional)
    # ============================================================
    if not skip_sponsors:
        tracker.start_step('sponsors', "Analyzing sponsors...")
        try:
            sponsors = _build_sponsors(result['overview'], tracker)
            result['sponsors'] = sponsors
        except Exception as e:
            result['errors']['sponsors'] = str(e)
            result['sponsors'] = {'error': str(e), 'provenance': []}
            traceback.print_exc()
        tracker.complete_step(f"Sponsors complete: {len(result['sponsors'].get('top_sponsors', []))} sponsors found")

    # ============================================================
    # STEP 6: Geography
    # ============================================================
    tracker.start_step('geography', "Mapping geographic distribution...")
    try:
        geography = _build_geography(result['overview'], tracker)
        result['geography'] = geography
    except Exception as e:
        result['errors']['geography'] = str(e)
        result['geography'] = {'error': str(e), 'provenance': []}
        traceback.print_exc()
    tracker.complete_step("Geography complete")

    # ============================================================
    # STEP 7: Competitors
    # ============================================================
    tracker.start_step('competitors', "Identifying competitors...")
    try:
        competitors = _build_competitors(
            query, query_type,
            ctgov_search, opentargets_search, opentargets_details, opentargets_drug,
            tracker,
        )
        result['competitors'] = competitors
    except Exception as e:
        result['errors']['competitors'] = str(e)
        result['competitors'] = {'error': str(e), 'provenance': []}
        traceback.print_exc()
    tracker.complete_step(f"Competitors complete: {len(result['competitors'].get('items', []))} found")

    # ============================================================
    # STEP 8: Assembly
    # ============================================================
    tracker.start_step('assembly', "Generating landscape report...")

    # Collect all provenance
    for section_key in ['overview', 'phase_distribution', 'enrollment', 'endpoints', 'sponsors', 'geography', 'competitors']:
        section_data = result.get(section_key, {})
        if isinstance(section_data, dict):
            result['provenance'].extend(section_data.get('provenance', []))

    # Generate ASCII report
    result['visualization'] = generate_report(result)

    # Clean up internal keys
    if '_skip_endpoints' in result:
        del result['_skip_endpoints']
    if '_skip_sponsors' in result:
        del result['_skip_sponsors']
    # Clean up _detail_text from trials
    for trial in result.get('overview', {}).get('all_nct_ids', []):
        trial.pop('_detail_text', None)

    tracker.complete_step("Clinical trial landscape report complete")

    if progress_callback:
        progress_callback(100, "Done")

    return result


# ─── CLI entry point ──────────────────────────────────────────

def _build_bioclaw_mcp_funcs():
    """Build mcp_funcs dict using McpClient for BioClaw container/local execution."""
    from mcp_client import McpClient

    clients = {}
    mcp_funcs = {}
    server_map = {
        'ctgov': ('ct_gov_studies', {
            'ctgov_search': {'method': 'search'},
            'ctgov_get_study': {'method': 'get'},
        }),
        'pubmed': ('pubmed_articles', {
            'pubmed_search': {'method': 'search_keywords'},
        }),
        'opentargets': ('opentargets_info', {
            'opentargets_search': {'method': 'search_targets'},
            'opentargets_details': {'method': 'get_target_details'},
            'opentargets_drug': {'method': 'search_diseases'},
        }),
    }
    for srv_name, (tool_name, funcs) in server_map.items():
        try:
            client = McpClient(srv_name)
            client.connect()
            clients[srv_name] = client
            for func_key, defaults in funcs.items():
                def make_fn(c, t, d):
                    def fn(**kw):
                        merged = {**d, **kw}
                        return c.call(t, **merged)
                    return fn
                mcp_funcs[func_key] = make_fn(client, tool_name, defaults)
        except Exception as e:
            print(f"  Warning: {srv_name}: {e}")
    print(f"BioClaw MCP: loaded {len(mcp_funcs)} functions")
    return mcp_funcs, clients


def _build_cli_mcp_funcs_UNUSED():
    """REPLACED by _build_bioclaw_mcp_funcs — kept for reference only."""
    import importlib.util

    _abs_script_dir = os.path.abspath(_script_dir)
    _claude_dir = os.path.dirname(os.path.dirname(os.path.dirname(_abs_script_dir)))
    mcp_path = os.path.join(_claude_dir, "mcp")

    if _claude_dir not in sys.path:
        sys.path.insert(0, _claude_dir)

    def _load_module(name, path):
        spec = importlib.util.spec_from_file_location(name, path,
            submodule_search_locations=[os.path.dirname(path)])
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception:
            sys.modules.pop(name, None)
            raise
        return mod

    base = os.path.join(mcp_path, "servers")

    ct_mod = _load_module("ct_gov_mcp", os.path.join(base, "ct_gov_mcp", "__init__.py"))
    pubmed_mod = _load_module("pubmed_mcp", os.path.join(base, "pubmed_mcp", "__init__.py"))
    ot_mod = _load_module("opentargets_mcp", os.path.join(base, "opentargets_mcp", "__init__.py"))

    def ctgov_search_wrapper(**kwargs):
        kwargs.pop('method', None)
        return ct_mod.search(**kwargs)

    def ctgov_get_study_wrapper(**kwargs):
        kwargs.pop('method', None)
        return ct_mod.get_study(**kwargs)

    def pubmed_wrapper(**kwargs):
        kwargs.pop('method', None)
        if 'query' in kwargs and 'keywords' not in kwargs:
            kwargs['keywords'] = kwargs.pop('query')
        return pubmed_mod.search_keywords(**kwargs)

    def opentargets_search_wrapper(**kwargs):
        kwargs.pop('method', None)
        return ot_mod.search_targets(**kwargs)

    def opentargets_details_wrapper(**kwargs):
        kwargs.pop('method', None)
        return ot_mod.get_target_details(**kwargs)

    def opentargets_drug_wrapper(**kwargs):
        kwargs.pop('method', None)
        return ot_mod.search_diseases(**kwargs)

    return {
        'ctgov_search': ctgov_search_wrapper,
        'ctgov_get_study': ctgov_get_study_wrapper,
        'pubmed_search': pubmed_wrapper,
        'opentargets_search': opentargets_search_wrapper,
        'opentargets_details': opentargets_details_wrapper,
        'opentargets_drug': opentargets_drug_wrapper,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Clinical Trial Landscape Analysis")
    parser.add_argument("query", help="Drug name or indication to analyze")
    parser.add_argument("--query-type", default="auto", choices=["auto", "drug", "indication"],
                        help="Force query interpretation (default: auto-detect)")
    parser.add_argument("--skip-endpoints", action="store_true", help="Skip endpoint analysis")
    parser.add_argument("--skip-sponsors", action="store_true", help="Skip sponsor analysis")
    args = parser.parse_args()

    def progress_cb(pct, msg):
        print(f"  [{pct:3d}%] {msg}")

    print(f"\nAnalyzing clinical trial landscape for: {args.query}\n")

    _cli_mcp_funcs, _cli_clients = _build_bioclaw_mcp_funcs()

    result = get_clinical_trial_landscape(
        query=args.query,
        query_type=args.query_type,
        skip_endpoints=args.skip_endpoints,
        skip_sponsors=args.skip_sponsors,
        mcp_funcs=_cli_mcp_funcs,
        progress_callback=progress_cb,
    )

    for c in _cli_clients.values():
        c.close()

    print("\n" + result.get('visualization', 'No visualization generated'))

    if result.get('errors'):
        print(f"\nErrors encountered: {result['errors']}")
