"""Indication/disease synonym resolution utilities using NLM API."""
import re
from typing import Dict, Any

# All MCP functions are now accessed via mcp_funcs parameter
# No direct imports from mcp.servers.* allowed

# Common words that should NOT be treated as disease synonyms
# These appear in disease descriptions but are not conditions themselves
STOPWORD_SYNONYMS = {
    'adult', 'adults', 'child', 'children', 'pediatric', 'juvenile',
    'infantile', 'infant', 'elderly', 'geriatric', 'adolescent',
    'young', 'old', 'age', 'onset', 'early', 'late', 'chronic',
    'acute', 'severe', 'mild', 'moderate', 'primary', 'secondary',
    'familial', 'hereditary', 'congenital', 'acquired', 'idiopathic',
    'type', 'form', 'variant', 'subtype', 'stage', 'grade',
}

# Patterns to detect comparator drugs from trial title
# e.g., "Drug A Compared to Drug B" -> Drug B is comparator
COMPARATOR_TITLE_PATTERNS = [
    r'compared\s+to\s+(.+?)(?:,|\s+in\s+|\s+for\s+|\s+both\s+|$)',
    r'versus\s+(.+?)(?:,|\s+in\s+|\s+for\s+|$)',
    r'vs\.?\s+(.+?)(?:,|\s+in\s+|\s+for\s+|$)',
]

# Patterns to detect reason for Phase 3/4 trials on approved drugs
# Returns (pattern, reason) tuples - order matters, first match wins
TRIAL_REASON_PATTERNS = [
    # Pediatric/new population (check first - very specific)
    (r'\b(children|child|pediatric|adolescent|teenager|infant|elderly|geriatric)\b', 'New population'),
    # New formulation
    (r'formulation|tablet|oral\s+.+\s+vs|different\s+.*dose|bioequivalence|pharmacokinetic', 'New formulation'),
    # New geographic market
    (r'\b(japanese|chinese|korean|asian|indian|brazilian|latin|european)\b.*\b(people|patients|participants|subjects|adults)\b', 'New market'),
    (r'\bin\s+(japan|china|korea|asia|india|brazil|europe)\b', 'New market'),
    # Combination with other drugs (check "administered.*with", "following.*initiation", etc.)
    (r'combination|combined|together\s+with|plus\s+|added\s+to|administered.*(?:with|same\s+time)|following.*initiation|\+', 'Combination'),
    # Post-marketing / long-term safety / real-world evidence
    (r'long-term|safety\s+extension|post-marketing|real-world|observational|standard\s+of\s+care|clinical\s+practice', 'Post-marketing'),
    # New indication - expanded list of disease areas that indicate indication expansion
    # This should catch trials studying approved drugs in new disease contexts
    (r"alzheimer|parkinson|nash|nafl|heart\s+failure|kidney|renal|liver|hepatic|pulmonary|respiratory|"
     r"arthritis|colitis|crohn|psoria|lupus|multiple\s+sclerosis|"
     r"type\s*1\s*diabetes|t1d|"  # Type 1 diabetes distinct from Type 2
     r"cancer|carcinoma|tumor|oncol|leukemia|lymphoma|melanoma|sarcoma|"
     r"fibrosis|cirrhosis|steatosis|"
     r"sleep\s+apnea|apnoea|"
     r"cardiovascular|cardio|atrial\s+fibrillation|stroke|"
     r"osteo|bone\s+loss|fracture", 'New indication'),
]


def detect_trial_reason(trial_title: str, drug_name: str, is_approved: bool = False) -> str:
    """
    Detect the reason for a trial based on title patterns.

    Only returns a reason if the drug is already approved (is_approved=True).
    For pipeline drugs, returns None since they don't need a "reason" for trials.

    Args:
        trial_title: The trial's study title
        drug_name: The drug being studied
        is_approved: Whether the drug is already FDA/EMA approved

    Returns:
        str: Reason like 'New formulation', 'New market', etc. or None for standard pipeline
    """
    if not trial_title:
        return None

    # Only detect reasons for approved drugs
    # Pipeline drugs don't need a reason - trials are expected
    if not is_approved:
        return None

    title_lower = trial_title.lower()

    for pattern, reason in TRIAL_REASON_PATTERNS:
        if re.search(pattern, title_lower, re.IGNORECASE):
            return reason

    return None


def resolve_indication_synonyms(indication: str, mcp_funcs: Dict[str, Any] = None) -> list:
    """
    Resolve an indication to all its synonyms using NLM Conditions API.

    Parses the NLM response to extract synonyms from entries like:
    "Lou Gehrig's disease (amyotrophic lateral sclerosis; ALS)"

    Uses progressive word-based fallback with relevance filtering.

    Args:
        indication: User-provided indication (e.g., "ALS", "Lou Gehrig's disease")

    Returns:
        list: Deduplicated list of synonyms including original term
    """
    synonyms = {indication.lower()}  # Always include original
    indication_words = set(w.lower() for w in indication.split() if len(w) > 2)

    if not mcp_funcs:
        return [indication]

    search_conditions = mcp_funcs.get('nlm_search_codes')
    if not search_conditions:
        return [indication]

    def query_nlm(terms: str) -> list:
        """Query NLM and normalize response to list."""
        results = search_conditions(method='search_codes', terms=terms, maxList=5)
        if isinstance(results, dict):
            return results.get('results', [])
        return results if isinstance(results, list) else []

    def is_relevant(entry: dict, query_word: str) -> bool:
        """Check if NLM result is relevant to original query."""
        display = (entry.get('display', '') or '').lower()
        # Result must contain the query word we searched for
        return query_word.lower() in display

    try:
        # Try 1: Full query as-is
        results = query_nlm(indication)

        # Try 2: If no results, try individual words with progressive truncation
        if not results:
            words = [w for w in indication.split() if len(w) > 3]
            # Sort by length descending - longer words are more specific
            words.sort(key=len, reverse=True)

            for word in words:
                # Try the word, then progressively shorter versions (remove trailing chars)
                # This handles suffixes like 's, 'es, 'ing without hardcoding rules
                for end in range(len(word), 3, -1):  # Min 4 chars
                    truncated = word[:end]
                    print(f"  Trying: '{truncated}'")
                    candidate_results = query_nlm(truncated)
                    # Filter to results containing truncated term (case-insensitive)
                    relevant = [r for r in candidate_results if truncated.lower() in (r.get('display', '') or '').lower()]
                    if relevant:
                        results = relevant
                        break
                if results:
                    break

        if not results or len(results) == 0:
            return [indication]

        # Filter results to only those containing the search term as a whole word (handles ambiguous acronyms)
        # Use word boundary matching to avoid "HIV" matching "Hives" or "MS" matching "MSUD"
        indication_lower = indication.lower()
        word_pattern = re.compile(r'\b' + re.escape(indication_lower) + r'\b', re.IGNORECASE)
        relevant_results = [r for r in results if word_pattern.search(r.get('display', '') or '')]
        # If no exact matches, use first result only (most relevant by NLM ranking)
        if not relevant_results:
            relevant_results = results[:1]

        for entry in relevant_results:
            # Get display/consumer_name which contains synonyms
            display = entry.get('display', '') or entry.get('consumer_name', '')

            if display:
                # Parse format: "Lou Gehrig's disease (amyotrophic lateral sclerosis; ALS)"
                # Extract main term
                main_match = re.match(r'^([^(]+)', display)
                if main_match:
                    main_term = main_match.group(1).strip()
                    if main_term:
                        synonyms.add(main_term.lower())

                # Extract parenthetical terms (separated by ; or ,)
                paren_match = re.search(r'\(([^)]+)\)', display)
                if paren_match:
                    paren_content = paren_match.group(1)
                    # Split by ; or ,
                    for term in re.split(r'[;,]', paren_content):
                        term = term.strip()
                        # Skip stopwords and short terms
                        if term and len(term) > 1 and term.lower() not in STOPWORD_SYNONYMS:
                            synonyms.add(term.lower())

            # Also check primary_name if available
            primary = entry.get('primary_name', '')
            if primary:
                synonyms.add(primary.lower())

    except Exception as e:
        print(f"  Warning: NLM synonym lookup failed: {e}")
        return [indication]

    # Convert back to list, preserving original casing for first term
    result_list = list(synonyms)

    # Put original term first
    if indication.lower() in result_list:
        result_list.remove(indication.lower())
        result_list.insert(0, indication)

    return result_list


# ============================================================================
# Company Pipeline Analysis
# ============================================================================

def get_company_pipeline(company_name: str, progress_callback=None, approved_drugs: list = None, mcp_funcs: Dict[str, Any] = None) -> dict:
    """
    Get drug pipeline for a specific company with proper drug extraction.

    Uses the same battle-tested parsing logic as indication_drug_pipeline_breakdown
    but searches by lead sponsor instead of condition.

    This function is designed to be called from the SWOT analysis skill to get
    accurate drug names and phase distribution for a company.

    Args:
        company_name: Company name (e.g., "BioMarin", "Novo Nordisk")
        progress_callback: Optional callback(percent, step) for progress reporting
        approved_drugs: Optional list of already-approved drug names (for reason detection)

    Args:
        company_name: Company name (e.g., "BioMarin", "Ultragenyx", "Exact Sciences")
        progress_callback: Optional callback(percent, step) for progress reporting

    Returns:
        dict: {
            'total_trials': int,
            'phase_distribution': Dict[phase, trial_count],
            'drugs_by_phase': Dict[phase, List[drug_names]],
            'lead_drugs': List[{name, trial_count, highest_phase}],
            'all_drugs': List[str],
            'indications': Dict[indication, trial_count],
            'status_distribution': Dict[status, count],
            'total_enrollment': int,
            'success': bool
        }
    """
    import os
    import sys
    from collections import defaultdict, Counter

    if not mcp_funcs:
        return {
            'total_trials': 0,
            'phase_distribution': {},
            'drugs_by_phase': {},
            'lead_drugs': [],
            'all_drugs': [],
            'indications': {},
            'status_distribution': {},
            'total_enrollment': 0,
            'success': False,
            'error': 'mcp_funcs required'
        }

    ct_search = mcp_funcs.get('ctgov_search')
    if not ct_search:
        return {
            'total_trials': 0,
            'phase_distribution': {},
            'drugs_by_phase': {},
            'lead_drugs': [],
            'all_drugs': [],
            'indications': {},
            'status_distribution': {},
            'total_enrollment': 0,
            'success': False,
            'error': 'ctgov_search not available'
        }

    # Import sibling modules for drug extraction
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    if _script_dir not in sys.path:
        sys.path.insert(0, _script_dir)

    from trial_utils import extract_drugs_from_trial, extract_enrollment_from_trial, get_trial_detail
    from drug_utils import clean_drug_name_for_display

    def report_progress(percent, step):
        if progress_callback:
            progress_callback(percent, step)
        print(f"  [{percent}%] {step}")

    report_progress(5, f"Starting pipeline analysis for {company_name}")

    # Phase mapping: display name -> CT.gov API value
    PHASES = {
        'Phase1': 'PHASE1',
        'Phase2': 'PHASE2',
        'Phase3': 'PHASE3',
        'Phase4': 'PHASE4',
    }

    # Status for active trials
    ACTIVE_STATUS = "recruiting OR active_not_recruiting OR not_yet_recruiting OR enrolling_by_invitation"

    # Data structures
    phase_trials = defaultdict(int)
    phase_drugs = defaultdict(set)
    drug_trial_ids = defaultdict(set)  # drug -> set of NCT IDs (for accurate counting)
    drug_highest_phase = {}
    drug_indications = defaultdict(Counter)  # drug -> indication -> count
    drug_trial_titles = defaultdict(list)  # drug -> list of trial titles at highest phase
    indications = Counter()
    status_dist = Counter()
    total_enrollment = 0
    all_nct_ids = set()

    try:
        # Search each phase separately for the company
        report_progress(10, "Searching clinical trials by phase...")

        for phase_idx, (phase_name, phase_code) in enumerate(PHASES.items()):
            progress_pct = 10 + (phase_idx * 15)
            report_progress(progress_pct, f"Searching {phase_name} trials...")

            try:
                # Search by lead sponsor
                result = ct_search(
                    lead=company_name,
                    phase=phase_code,
                    studyType="interventional",
                    interventionType="drug",
                    status=ACTIVE_STATUS,
                    pageSize=1000
                )

                result_text = result if isinstance(result, str) else str(result)

                # Extract NCT IDs
                nct_ids = re.findall(r'NCT\d{8}', result_text)
                nct_ids = list(set(nct_ids))  # Dedupe

                if nct_ids:
                    print(f"    {phase_name}: {len(nct_ids)} trials found")

                for nct_id in nct_ids:
                    if nct_id in all_nct_ids:
                        continue
                    all_nct_ids.add(nct_id)

                    try:
                        # Get trial details
                        trial_detail = get_trial_detail(nct_id)

                        # Extract drugs using battle-tested logic
                        raw_drugs = extract_drugs_from_trial(trial_detail)

                        if raw_drugs:
                            # Extract ACTUAL phase from trial detail (CT.gov API returns trials across phases)
                            # Skip observational/non-phased trials (they have no **Phase:** field)
                            actual_phase = None
                            if isinstance(trial_detail, str):
                                phase_match = re.search(r'\*\*Phase:\*\*\s*(Phase\d)', trial_detail)
                                if phase_match:
                                    actual_phase = phase_match.group(1)

                            # Skip trials without a valid phase (observational studies)
                            if not actual_phase:
                                continue

                            phase_trials[actual_phase] += 1

                            # Extract enrollment
                            enrollment = extract_enrollment_from_trial(trial_detail)
                            total_enrollment += enrollment

                            # Extract condition/indication from trial FIRST (needed for drug-indication mapping)
                            trial_conditions = []
                            if isinstance(trial_detail, str):
                                # Format: ## Conditions\n\n- Condition1\n- Condition2
                                cond_section = re.search(r'## Conditions\s*\n+((?:- .+\n?)+)', trial_detail)
                                if cond_section:
                                    cond_lines = cond_section.group(1).strip().split('\n')
                                    for line in cond_lines[:3]:  # Top 3 conditions
                                        cond = line.lstrip('- ').strip()
                                        if cond and len(cond) > 2:
                                            # Truncate long names
                                            if len(cond) > 50:
                                                cond = cond[:47] + '...'
                                            indications[cond] += 1
                                            trial_conditions.append(cond)

                                # Extract status
                                status_match = re.search(r'\*\*Status:\*\*\s*(\w+)', trial_detail)
                                if status_match:
                                    status_dist[status_match.group(1)] += 1

                            # Extract trial title for comparator detection and reason analysis
                            # e.g., "Drug A Compared to Drug B" -> Drug B is comparator
                            comparator_drugs_in_trial = set()
                            trial_title_raw = None
                            if isinstance(trial_detail, str):
                                # Extract Study Title from markdown format: **Study Title:** ...
                                title_match = re.search(r'\*\*Study Title:\*\*\s*(.+?)(?:\n|$)', trial_detail)
                                if title_match:
                                    trial_title_raw = title_match.group(1).strip()
                                    trial_title = trial_title_raw.lower()
                                    for pattern in COMPARATOR_TITLE_PATTERNS:
                                        comp_match = re.search(pattern, trial_title, re.IGNORECASE)
                                        if comp_match:
                                            comparator_name = comp_match.group(1).strip()
                                            # Clean up comparator name (remove trailing words like "in patients")
                                            comparator_name = re.sub(r'\s+(in|for|both|and|or)\s+.*$', '', comparator_name, flags=re.IGNORECASE)
                                            if comparator_name and len(comparator_name) > 2:
                                                comparator_drugs_in_trial.add(comparator_name.lower())

                            # Clean and track drugs
                            for raw_drug in raw_drugs:
                                cleaned_drugs = clean_drug_name_for_display(raw_drug)
                                for drug in cleaned_drugs:
                                    if drug:
                                        # Additional cleaning for company pipeline context
                                        # Handle "RDD to Palynziq" -> "Palynziq"
                                        if ' to ' in drug:
                                            parts = drug.split(' to ')
                                            if len(parts) == 2 and len(parts[1]) > 2:
                                                drug = parts[1].strip()
                                        # Handle "switch from X to Y" patterns
                                        if drug.lower().startswith('switch '):
                                            continue  # Skip protocol descriptions

                                        # Filter out comparator drugs detected from trial title
                                        drug_lower = drug.lower()
                                        is_comparator = False
                                        for comp in comparator_drugs_in_trial:
                                            # Check if drug name matches or is contained in comparator
                                            if drug_lower in comp or comp in drug_lower:
                                                is_comparator = True
                                                break
                                        if is_comparator:
                                            continue  # Skip comparator drug

                                        phase_drugs[actual_phase].add(drug)

                                        # Track highest phase per drug AND trials/indications at highest phase
                                        phase_rank = {'Phase1': 1, 'Phase2': 2, 'Phase3': 3, 'Phase4': 4}
                                        current_rank = phase_rank.get(drug_highest_phase.get(drug), 0)
                                        new_rank = phase_rank.get(actual_phase, 0)
                                        if new_rank > current_rank:
                                            drug_highest_phase[drug] = actual_phase
                                            # Reset indications, trial count, and titles when we find a higher phase
                                            drug_indications[drug] = Counter()
                                            drug_trial_ids[drug] = set()  # Reset to count only highest phase trials
                                            drug_trial_titles[drug] = []  # Reset titles for highest phase

                                        # Only track trials/indications/titles at the highest phase seen so far
                                        if new_rank >= current_rank:
                                            drug_trial_ids[drug].add(nct_id)
                                            if trial_title_raw:
                                                drug_trial_titles[drug].append(trial_title_raw)
                                            for cond in trial_conditions:
                                                drug_indications[drug][cond] += 1

                    except Exception as e:
                        # Skip failed trials silently
                        continue

                # Handle pagination if needed
                page_token_match = re.search(r'`pageToken:\s*"([^"]+)"', result_text)
                while page_token_match:
                    page_token = page_token_match.group(1)
                    result = ct_search(
                        lead=company_name,
                        phase=phase_code,
                        studyType="interventional",
                        interventionType="drug",
                        status=ACTIVE_STATUS,
                        pageSize=1000,
                        pageToken=page_token
                    )
                    result_text = result if isinstance(result, str) else str(result)
                    more_nct_ids = re.findall(r'NCT\d{8}', result_text)

                    for nct_id in more_nct_ids:
                        if nct_id in all_nct_ids:
                            continue
                        all_nct_ids.add(nct_id)
                        # Process same as above (simplified - skip details for pagination)

                    page_token_match = re.search(r'`pageToken:\s*"([^"]+)"', result_text)

            except Exception as e:
                print(f"    Warning: {phase_name} search failed: {e}")
                continue

        report_progress(75, "Processing results...")

        # Build lead drugs list (sorted by trial count, then by phase)
        phase_rank = {'Phase4': 4, 'Phase3': 3, 'Phase2': 2, 'Phase1': 1, 'Unknown': 0}
        lead_drugs = []
        # Sort drugs by number of unique trials (not extractions)
        sorted_drugs = sorted(drug_trial_ids.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        for drug, trial_ids in sorted_drugs:
            # Get top indication for this drug
            top_indication = None
            if drug in drug_indications and drug_indications[drug]:
                top_indication = drug_indications[drug].most_common(1)[0][0]

            # Check if this drug is already approved (for reason detection)
            is_approved = False
            if approved_drugs:
                drug_lower = drug.lower()
                for approved in approved_drugs:
                    approved_lower = approved.lower()
                    # Check for exact match or partial match (e.g., "semaglutide" in "Oral semaglutide")
                    if drug_lower == approved_lower or drug_lower in approved_lower or approved_lower in drug_lower:
                        is_approved = True
                        break

            # Detect trial reason from titles (only for approved drugs with ongoing trials)
            trial_reason = None
            titles = drug_trial_titles.get(drug, [])
            if titles and is_approved:
                # Check all titles and take the first detected reason
                for title in titles:
                    reason = detect_trial_reason(title, drug, is_approved=True)
                    if reason:
                        trial_reason = reason
                        break

            lead_drugs.append({
                'name': drug,
                'trial_count': len(trial_ids),  # Count unique trials, not extractions
                'highest_phase': drug_highest_phase.get(drug, 'Unknown'),
                'indication': top_indication,
                'reason': trial_reason  # None for pipeline drugs, or reason for approved drugs
            })

        # Sort by phase (descending), then by trial count
        lead_drugs.sort(key=lambda x: (phase_rank.get(x['highest_phase'], 0), x['trial_count']), reverse=True)

        # Collect all unique drugs
        all_drugs = set()
        for drugs in phase_drugs.values():
            all_drugs.update(drugs)

        # Convert phase_drugs sets to lists
        drugs_by_phase = {phase: sorted(list(drugs)) for phase, drugs in phase_drugs.items() if drugs}

        # Build phase distribution
        phase_distribution = dict(phase_trials)

        # Sort indications by count
        top_indications = dict(indications.most_common(10))

        report_progress(90, "Finalizing results...")

        total_trials = sum(phase_trials.values())

        result = {
            'total_trials': total_trials,
            'phase_distribution': phase_distribution,
            'drugs_by_phase': drugs_by_phase,
            'lead_drugs': lead_drugs[:10],
            'all_drugs': sorted(list(all_drugs)),
            'indications': top_indications,
            'status_distribution': dict(status_dist),
            'total_enrollment': total_enrollment,
            'success': True
        }

        report_progress(95, f"Found {total_trials} trials, {len(all_drugs)} unique drugs")

        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'total_trials': 0,
            'phase_distribution': {},
            'drugs_by_phase': {},
            'lead_drugs': [],
            'all_drugs': [],
            'indications': {},
            'status_distribution': {},
            'total_enrollment': 0,
            'success': False,
            'error': str(e)
        }
