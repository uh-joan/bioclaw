#!/usr/bin/env python3
"""
Designations Analyzer - Checks eligibility for regulatory designations and
special considerations (pediatric, companion diagnostics).

Provides evidence-based eligibility signals grounded in:
- Precedent evidence (which similar drugs received designations)
- Indication characteristics (prevalence for orphan, unmet need for breakthrough)
- Modality type (CDx requirements for biomarker-driven therapies)

All classification decisions use dynamic data sources (CT.gov, OpenTargets,
DataCommons) instead of hardcoded disease lists.
"""

import re
from typing import Dict, Any, List, Optional, Callable

from regulatory_constants import DESIGNATIONS, PEDIATRIC_RULES


def analyze_designations(
    indication: str,
    modality: str = None,
    target_regions: List[str] = None,
    precedents: List[Dict[str, Any]] = None,
    mcp_funcs: Dict[str, Callable] = None,
    progress_callback=None,
    search_terms: List[str] = None,
) -> Dict[str, Any]:
    """
    Analyze designation eligibility and special considerations.

    Args:
        indication: Disease/condition
        modality: Drug modality
        target_regions: Regions to analyze
        precedents: Precedent drug data
        mcp_funcs: MCP functions for data lookup
        progress_callback: Callback(progress, message)
        search_terms: Expanded indication synonyms for EMA queries

    Returns:
        Dict with designations, pediatric, companion_diagnostic
    """
    if target_regions is None:
        target_regions = ["US", "EU"]
    if precedents is None:
        precedents = []
    if mcp_funcs is None:
        mcp_funcs = {}
    if search_terms is None:
        search_terms = [indication]

    result = {
        'designations': {},
        'pediatric': {},
        'companion_diagnostic': {},
        'sources': [],
    }

    # Analyze designation eligibility
    if progress_callback:
        progress_callback(0.0, "Analyzing designation eligibility...")

    # Extract designations from precedent drugs
    precedent_designations = _extract_precedent_designations(precedents)

    # Cache CT.gov trial count once — reused by orphan US, orphan EU, and pediatric
    _cached_trial_count = _get_ctgov_trial_count(indication, mcp_funcs)

    # US Designations
    if "US" in target_regions:
        result['designations']['breakthrough_therapy'] = _assess_breakthrough(
            indication, precedents, precedent_designations
        )
        result['designations']['fast_track'] = _assess_fast_track(
            indication, precedents, precedent_designations
        )
        result['designations']['orphan_drug'] = _assess_orphan_us(
            indication, precedents, precedent_designations, mcp_funcs, search_terms,
            cached_trial_count=_cached_trial_count,
        )
        result['designations']['priority_review'] = _assess_priority_review(
            indication, precedents, precedent_designations
        )
        result['designations']['accelerated_approval'] = _assess_accelerated(
            indication, precedents, precedent_designations
        )

    # EU Designations
    if "EU" in target_regions:
        result['designations']['prime'] = _assess_prime(
            indication, precedents, precedent_designations
        )
        result['designations']['orphan_eu'] = _assess_orphan_eu(
            indication, precedents, precedent_designations, mcp_funcs, search_terms,
            cached_trial_count=_cached_trial_count,
        )
        result['designations']['conditional_ma'] = _assess_conditional_ma(
            indication, precedents, precedent_designations
        )

    if progress_callback:
        progress_callback(0.5, "Analyzing pediatric obligations...")

    # Pediatric obligations (reuse cached trial count)
    result['pediatric'] = _analyze_pediatric(
        indication, target_regions, mcp_funcs,
        cached_total_trial_count=_cached_trial_count,
    )

    if progress_callback:
        progress_callback(0.8, "Checking companion diagnostic requirements...")

    # Companion diagnostic (uses precedent data + OpenTargets genetic evidence)
    result['companion_diagnostic'] = _analyze_companion_diagnostic(
        indication, modality, precedents, mcp_funcs
    )

    result['sources'].append("Designation analysis based on precedent evidence and indication characteristics")

    if progress_callback:
        progress_callback(1.0, "Designation analysis complete")

    return result


def _extract_precedent_designations(precedents: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Extract designations granted to precedent drugs."""
    designation_map = {}  # designation_type -> [drug_names]

    for p in precedents:
        drug_name = p.get('brand_name', p.get('drug_name', 'Unknown'))
        designations = p.get('designations_granted', [])
        for d in designations:
            d_lower = d.lower()
            if 'orphan' in d_lower:
                designation_map.setdefault('orphan', []).append(drug_name)
            if 'prime' in d_lower:
                designation_map.setdefault('prime', []).append(drug_name)
            if 'breakthrough' in d_lower:
                designation_map.setdefault('breakthrough', []).append(drug_name)
            if 'fast track' in d_lower:
                designation_map.setdefault('fast_track', []).append(drug_name)
            if 'priority' in d_lower:
                designation_map.setdefault('priority_review', []).append(drug_name)
            if 'accelerated' in d_lower:
                designation_map.setdefault('accelerated', []).append(drug_name)

    return designation_map


# ============================================================================
# Dynamic MCP Helpers (replace hardcoded disease lists)
# ============================================================================

def _get_ctgov_trial_count(indication: str, mcp_funcs: Dict) -> Optional[int]:
    """Get total trial count from CT.gov as disease prevalence proxy.

    High trial counts (>50) strongly correlate with high-prevalence diseases.
    Low counts (<15) suggest potentially rare/orphan-eligible conditions.
    """
    ctgov = mcp_funcs.get('ctgov_search')
    if not ctgov:
        return None
    try:
        result = ctgov(condition=indication, pageSize=1, countTotal=True)
        # Server wrapper returns dict with 'totalCount'; CLI returns raw markdown string
        if isinstance(result, dict):
            tc = result.get('totalCount')
            if tc is not None:
                return int(tc)
            # Fall through to text parsing if dict has 'text' key
            result = result.get('text', '')
        if isinstance(result, str):
            # Parse "N of M studies found" or "M studies found"
            # Numbers may contain commas (e.g., "11,397") so match [\d,]+
            match = re.search(r'([\d,]+)\s+of\s+([\d,]+)\s+stud', result)
            if match:
                return int(match.group(2).replace(',', ''))
            match = re.search(r'([\d,]+)\s+stud(?:y|ies)\s+found', result)
            if match:
                return int(match.group(1).replace(',', ''))
        return None
    except Exception:
        return None


def _get_ctgov_pediatric_trial_count(indication: str, mcp_funcs: Dict) -> Optional[int]:
    """Search CT.gov for pediatric trials in this indication.

    Returns count of trials mentioning "pediatric" or "children" for the condition.
    """
    ctgov = mcp_funcs.get('ctgov_search')
    if not ctgov:
        return None
    try:
        result = ctgov(condition=f"pediatric {indication}", pageSize=1, countTotal=True)
        # Server wrapper returns dict with 'totalCount'; CLI returns raw markdown string
        if isinstance(result, dict):
            tc = result.get('totalCount')
            if tc is not None:
                return int(tc)
            result = result.get('text', '')
        if isinstance(result, str):
            if 'no studies' in result.lower() or '0 studies' in result.lower():
                return 0
            match = re.search(r'([\d,]+)\s+of\s+([\d,]+)\s+stud', result)
            if match:
                return int(match.group(2).replace(',', ''))
            match = re.search(r'([\d,]+)\s+stud(?:y|ies)\s+found', result)
            if match:
                return int(match.group(1).replace(',', ''))
            # If we got results but can't parse count, there are at least some
            if 'nct' in result.lower():
                return 1
            return 0
        return None
    except Exception:
        return None


def _has_strong_genetic_associations(indication: str, mcp_funcs: Dict) -> bool:
    """Check OpenTargets for strong target associations indicating biomarker-driven disease.

    Uses two-step workflow:
    1. search_diseases() to get disease ID (MONDO/EFO)
    2. get_disease_targets_summary() to check for high-scoring target associations

    Diseases with strong genetic drivers (e.g., EGFR/KRAS in NSCLC) have high
    association scores and are more likely to need companion diagnostics.
    """
    ot = mcp_funcs.get('opentargets_search')
    if not ot:
        return False

    try:
        # Step 1: Search for disease to get its ID
        search_result = ot(query=indication, method='search_diseases')

        disease_id = None
        if isinstance(search_result, dict):
            # Try standard nested format: data.search.hits
            hits = search_result.get('data', {}).get('search', {}).get('hits', [])
            if not hits:
                # Try flat format: data[]
                hits = search_result.get('data', [])
                if isinstance(hits, dict):
                    hits = []
            if not hits:
                return False

            # Find the best matching disease
            indication_words = set(indication.lower().split())
            for hit in hits[:5]:
                name = (hit.get('name') or '').lower()
                hit_words = set(name.split())
                if indication_words & hit_words:
                    disease_id = hit.get('id')
                    break
            # Fall back to first result if no word match
            if not disease_id and hits:
                disease_id = hits[0].get('id')

        elif isinstance(search_result, str):
            id_match = re.search(r'((?:MONDO|EFO|OTAR)_\d+)', search_result)
            if id_match:
                disease_id = id_match.group(1)

        if not disease_id:
            return False

        # Step 2: Get disease-target summary with association scores
        assoc_result = ot(
            method='get_disease_targets_summary',
            diseaseId=disease_id,
            minScore=0.5,
            size=10,
        )

        if isinstance(assoc_result, dict):
            # Format 1: targets[] with associationScore (from get_disease_targets_summary)
            targets = assoc_result.get('targets', [])
            if targets:
                for t in targets:
                    score = t.get('associationScore', 0)
                    if score and score > 0.5:
                        return True

            # Format 2: data.disease.associatedTargets.rows (from get_target_disease_associations)
            rows = (assoc_result.get('data', {}).get('disease', {})
                    .get('associatedTargets', {}).get('rows', []))
            for row in rows:
                score = row.get('score', 0)
                if score and score > 0.5:
                    return True

            # Format 3: data[] with datatypeScores (generic fallback)
            associations = assoc_result.get('data', [])
            if isinstance(associations, list):
                for assoc in associations:
                    datatypes = assoc.get('datatypeScores', {})
                    genetic_score = datatypes.get('genetic_association', 0)
                    if genetic_score and genetic_score > 0.3:
                        return True

        elif isinstance(assoc_result, str):
            result_lower = assoc_result.lower()
            if any(kw in result_lower for kw in [
                'genetic_association', 'genetic association',
                'somatic mutation', 'somatic_mutation',
            ]):
                return True

        return False
    except Exception:
        return False


def _is_indication_relevant(indication: str, therapeutic_area: str) -> bool:
    """Check if an EMA orphan drug's therapeutic area is relevant to the queried indication.

    Prevents false positives where broad therapeutic_area searches match orphan drugs
    for unrelated rare subtypes (e.g., "hypertension" matching pulmonary arterial
    hypertension drugs, "neonatal diabetes" matching "type 2 diabetes").

    Two checks:
    1. Forward: indication words must appear in therapeutic_area (prevents unrelated matches)
    2. Reverse: therapeutic_area words must not introduce unrelated qualifiers
       (prevents "Diabetes Mellitus" matching when we want "type 2 diabetes" specifically)
    """
    if not therapeutic_area:
        return False
    indication_lower = indication.lower()
    ta_lower = therapeutic_area.lower()

    # Direct substring match in either direction — strongest signal
    if indication_lower in ta_lower or ta_lower in indication_lower:
        return True

    # Use significant words only (skip short/common words like "of", "the", "non")
    indication_words = [w for w in indication_lower.split() if len(w) > 3]
    if not indication_words:
        return indication_lower in ta_lower

    # Forward check: indication words must appear in therapeutic area
    matching_words = sum(1 for w in indication_words if w in ta_lower)

    # Require majority match (>= 2/3 of significant words)
    # This prevents "Diabetes Mellitus" matching "type 2 diabetes mellitus"
    # because only "diabetes" matches (1/2 = 50% < 67%)
    threshold = max(1, (len(indication_words) * 2 + 2) // 3)  # ceil(2/3)
    return matching_words >= threshold


def _check_ema_orphan_medicines(indication: str, search_terms: List[str], mcp_funcs: Dict) -> List[str]:
    """Query EMA for authorized orphan medicines matching the indication.

    Uses the orphan=True filter in search_medicines and falls back to
    get_orphan_designations endpoint. Returns list of orphan drug names found.

    Applies two filters to prevent false positives:
    1. Skips short/ambiguous search terms (<=2 chars) that match everything
    2. Validates each result's therapeutic_area_mesh against the original indication
    """
    ema = mcp_funcs.get('ema_search')
    if not ema:
        return []

    orphan_drugs = set()

    # Filter search terms: skip very short ones (e.g., "IB", "CF" — too ambiguous for EMA)
    # and terms that are clearly different diseases from the indication
    indication_lower = indication.lower()
    indication_words = set(w for w in indication_lower.split() if len(w) > 3)

    safe_terms = []
    for term in search_terms:
        # Skip terms <=2 chars — too ambiguous
        if len(term) <= 2:
            continue
        # Skip terms that share no significant words with indication
        # (prevents "idiopathic hypereosinophilic syndrome" when searching for IPF)
        term_words = set(w for w in term.lower().split() if len(w) > 3)
        if term_words and indication_words and not (term_words & indication_words):
            continue
        safe_terms.append(term)

    if not safe_terms:
        safe_terms = [indication]  # Fallback to original indication

    # Strategy 1: search_medicines with orphan=True filter
    for term in safe_terms:
        try:
            result = ema(
                method='search_medicines',
                therapeutic_area=term,
                orphan=True,
                status='Authorised',
                limit=10,
            )
            if isinstance(result, dict):
                medicines = result.get('results', result.get('data', []))
                if isinstance(medicines, list):
                    for med in medicines:
                        # Validate relevance via therapeutic_area_mesh
                        ta = med.get('therapeutic_area_mesh', '')
                        if not _is_indication_relevant(indication, ta):
                            continue
                        name = (
                            med.get('name_of_medicine')
                            or med.get('medicine_name')
                            or med.get('active_substance', '')
                        )
                        if name:
                            orphan_drugs.add(name)
            elif isinstance(result, str) and result.strip():
                lines = result.split('\n')
                for line in lines:
                    match = re.search(r'(?:medicine[_ ]name|name):\s*(.+)', line, re.IGNORECASE)
                    if match:
                        orphan_drugs.add(match.group(1).strip())
        except Exception:
            continue

    # Strategy 2: get_orphan_designations as fallback
    if not orphan_drugs:
        for term in safe_terms[:2]:
            try:
                result = ema(
                    method='get_orphan_designations',
                    therapeutic_area=term,
                    limit=10,
                )
                if isinstance(result, dict):
                    designations = result.get('results', result.get('data', []))
                    if isinstance(designations, list):
                        for desig in designations:
                            # Validate relevance via intended_use
                            intended = desig.get('intended_use', desig.get('therapeutic_indication', ''))
                            if intended and not _is_indication_relevant(indication, intended):
                                continue
                            name = (
                                desig.get('medicine_name')
                                or desig.get('name_of_medicine')
                                or desig.get('active_substance', '')
                            )
                            if name:
                                orphan_drugs.add(name)
                elif isinstance(result, str) and result.strip():
                    if any(kw in result.lower() for kw in ['orphan', 'designation', 'rare disease']):
                        lines = result.split('\n')
                        for line in lines:
                            name_match = re.match(r'[-*•]\s*\*?\*?(.+?)\*?\*?\s*[-–:]', line)
                            if name_match:
                                orphan_drugs.add(name_match.group(1).strip())
                        if not orphan_drugs:
                            orphan_drugs.add(f"[EMA orphan medicines for {term}]")
            except Exception:
                continue

    return list(orphan_drugs)


def _assess_breakthrough(indication, precedents, prec_designations):
    """Assess Breakthrough Therapy Designation eligibility."""
    info = dict(DESIGNATIONS['breakthrough_therapy'])

    drugs_with = prec_designations.get('breakthrough', [])
    if drugs_with:
        info['eligibility_signal'] = 'STRONG'
        info['rationale'] = f"Precedent: {', '.join(drugs_with[:3])} received Breakthrough designation"
        info['precedent_evidence'] = drugs_with
    elif len(precedents) < 3:
        info['eligibility_signal'] = 'MODERATE'
        info['rationale'] = "Few approved therapies suggest potential unmet need; requires substantial improvement over existing"
    else:
        info['eligibility_signal'] = 'WEAK'
        info['rationale'] = "Multiple existing therapies available; must demonstrate substantial improvement"

    return info


def _assess_fast_track(indication, precedents, prec_designations):
    """Assess Fast Track Designation eligibility."""
    info = dict(DESIGNATIONS['fast_track'])

    drugs_with = prec_designations.get('fast_track', [])
    if drugs_with:
        info['eligibility_signal'] = 'STRONG'
        info['rationale'] = f"Precedent: {', '.join(drugs_with[:3])} received Fast Track"
        info['precedent_evidence'] = drugs_with
    else:
        info['eligibility_signal'] = 'MODERATE'
        info['rationale'] = "Requires serious condition + unmet need. Assess whether drug fills gap in current treatment"

    return info


def _assess_orphan_us(indication, precedents, prec_designations, mcp_funcs=None, search_terms=None, cached_trial_count=None):
    """Assess Orphan Drug Designation eligibility (US).

    Uses multi-signal evidence:
    (1) Precedent designations (strongest signal — checked FIRST)
    (2) EMA orphan query (with indication-relevance filtering)
    (0) CT.gov trial count as prevalence veto (only if no positive orphan evidence)
    (3) Drug-count heuristic fallback
    """
    info = dict(DESIGNATIONS['orphan_drug'])
    if mcp_funcs is None:
        mcp_funcs = {}
    if search_terms is None:
        search_terms = [indication]

    # Tier 1 FIRST: Precedent drugs with orphan designation (strongest signal)
    # Moved before trial-count veto to prevent well-studied rare diseases
    # (AML ~20K/yr, 4K+ trials) from being incorrectly vetoed
    drugs_with = prec_designations.get('orphan', [])
    if drugs_with:
        info['eligibility_signal'] = 'STRONG'
        verb = 'has' if len(drugs_with) == 1 else 'have'
        info['rationale'] = f"Precedent: {', '.join(drugs_with[:3])} {verb} orphan designation"
        info['precedent_evidence'] = drugs_with
        return info

    # Tier 2: Dedicated EMA orphan query (with indication-relevance filtering)
    ema_orphans = _check_ema_orphan_medicines(indication, search_terms, mcp_funcs)
    if ema_orphans:
        display_names = [n for n in ema_orphans if not n.startswith('[')][:3]
        if display_names:
            info['eligibility_signal'] = 'STRONG'
            info['rationale'] = (
                f"EMA orphan-designated medicines found for this indication: {', '.join(display_names)}. "
                f"Strong US/EU orphan correlation (>90%) — US orphan designation highly likely."
            )
        else:
            info['eligibility_signal'] = 'STRONG'
            info['rationale'] = (
                f"EMA orphan medicines exist for this therapeutic area. "
                f"Strong US/EU orphan correlation (>90%) — US orphan designation highly likely."
            )
        info['ema_orphan_evidence'] = ema_orphans
        return info

    # Tier 0: CT.gov trial count as prevalence veto (only AFTER checking for
    # positive orphan evidence, to avoid vetoing well-studied rare diseases like AML)
    trial_count = cached_trial_count if cached_trial_count is not None else _get_ctgov_trial_count(indication, mcp_funcs)
    is_clearly_common = trial_count is not None and trial_count > 2500

    if is_clearly_common:
        info['eligibility_signal'] = 'NOT_APPLICABLE'
        info['rationale'] = (
            f"{trial_count:,} clinical trials found for {indication} — "
            f"high trial volume indicates prevalence far exceeds 200,000 US patients."
        )
        return info

    # Tier 3: Drug-count + trial-count heuristic fallback
    # Use trial count for moderate-prevalence diseases that fall between
    # the >2500 veto and the "clearly rare" threshold
    if len(precedents) >= 15:
        info['eligibility_signal'] = 'NOT_APPLICABLE'
        info['rationale'] = f"{len(precedents)} approved drug(s) found with no orphan designations — prevalence likely exceeds 200,000 US patients"
    elif trial_count is not None and trial_count > 500 and len(precedents) >= 8:
        info['eligibility_signal'] = 'NOT_APPLICABLE'
        info['rationale'] = f"{len(precedents)} approved drugs and {trial_count:,} clinical trials with no orphan designations — prevalence likely exceeds 200,000 US patients"
    elif len(precedents) <= 2:
        info['eligibility_signal'] = 'MODERATE'
        info['rationale'] = f"Only {len(precedents)} approved drug(s) found — limited market may indicate rare disease. Verify prevalence <200,000."
    elif trial_count is not None and trial_count < 200:
        info['eligibility_signal'] = 'MODERATE'
        info['rationale'] = f"Only {trial_count:,} clinical trials and {len(precedents)} approved drugs (none with orphan designation). Low trial volume suggests possible rare disease. Verify prevalence <200,000."
    else:
        info['eligibility_signal'] = 'MODERATE'
        info['rationale'] = f"Requires prevalence <200,000 in US ({len(precedents)} approved drugs, none with orphan designation). Verify with epidemiology data."

    return info


def _assess_priority_review(indication, precedents, prec_designations):
    """Assess Priority Review eligibility."""
    info = dict(DESIGNATIONS['priority_review'])

    drugs_with = prec_designations.get('priority_review', [])
    if drugs_with:
        info['eligibility_signal'] = 'STRONG'
        info['rationale'] = f"Precedent: {', '.join(drugs_with[:3])} received Priority Review"
    elif len(precedents) < 3:
        info['eligibility_signal'] = 'MODERATE'
        info['rationale'] = "Limited treatment options may support priority review if significant improvement shown"
    else:
        info['eligibility_signal'] = 'MODERATE'
        info['rationale'] = "Must demonstrate significant improvement in safety or effectiveness over existing therapies"

    return info


def _assess_accelerated(indication, precedents, prec_designations):
    """Assess Accelerated Approval eligibility."""
    info = dict(DESIGNATIONS['accelerated_approval'])

    drugs_with = prec_designations.get('accelerated', [])
    if drugs_with:
        info['eligibility_signal'] = 'STRONG'
        info['rationale'] = f"Precedent: {', '.join(drugs_with[:3])} used accelerated approval"
        info['precedent_evidence'] = drugs_with
    elif len(precedents) < 2:
        info['eligibility_signal'] = 'MODERATE'
        info['rationale'] = "Unmet need exists. Requires validated surrogate endpoint. Confirmatory trial mandatory."
    else:
        info['eligibility_signal'] = 'WEAK'
        info['rationale'] = "Existing therapies available; accelerated approval typically for high unmet need"

    return info


def _assess_prime(indication, precedents, prec_designations):
    """Assess PRIME (PRIority MEdicines) eligibility."""
    info = dict(DESIGNATIONS['prime'])

    drugs_with = prec_designations.get('prime', [])
    eu_precedents = [p for p in precedents if p.get('region') == 'EU']

    if drugs_with:
        info['eligibility_signal'] = 'STRONG'
        info['rationale'] = f"Precedent: {', '.join(drugs_with[:3])} received PRIME"
        info['precedent_evidence'] = drugs_with
    elif len(eu_precedents) < 2:
        info['eligibility_signal'] = 'MODERATE'
        info['rationale'] = "Few EU-approved therapies suggest unmet need; requires preliminary clinical evidence of major advantage"
    else:
        info['eligibility_signal'] = 'WEAK'
        info['rationale'] = "Multiple EU-authorized therapies exist; PRIME requires major therapeutic advantage"

    return info


def _assess_orphan_eu(indication, precedents, prec_designations, mcp_funcs=None, search_terms=None, cached_trial_count=None):
    """Assess EU Orphan Designation eligibility.

    Uses multi-signal evidence:
    (1) EU precedent orphan status (strongest signal — checked FIRST)
    (2) EMA orphan query (with indication-relevance filtering)
    (0) CT.gov trial count as prevalence veto (only if no positive orphan evidence)
    (3) Drug-count heuristic fallback
    """
    info = dict(DESIGNATIONS['orphan_eu'])
    if mcp_funcs is None:
        mcp_funcs = {}
    if search_terms is None:
        search_terms = [indication]

    # Tier 1 FIRST: Precedent drugs with EU orphan status (strongest signal)
    eu_orphans = [p for p in precedents if 'Orphan (EU)' in p.get('designations_granted', [])]
    if eu_orphans:
        info['eligibility_signal'] = 'STRONG'
        verb = 'has' if len(eu_orphans) == 1 else 'have'
        info['rationale'] = f"Precedent: {', '.join([p['brand_name'] for p in eu_orphans[:3]])} {verb} EU orphan status"
        return info

    # Tier 2: Dedicated EMA orphan query (with indication-relevance filtering)
    ema_orphans = _check_ema_orphan_medicines(indication, search_terms, mcp_funcs)
    if ema_orphans:
        display_names = [n for n in ema_orphans if not n.startswith('[')][:3]
        if display_names:
            info['eligibility_signal'] = 'STRONG'
            info['rationale'] = (
                f"EMA orphan-designated medicines found: {', '.join(display_names)}. "
                f"EU orphan designation highly likely for this indication."
            )
        else:
            info['eligibility_signal'] = 'STRONG'
            info['rationale'] = (
                f"EMA orphan medicines exist for this therapeutic area. "
                f"EU orphan designation highly likely."
            )
        info['ema_orphan_evidence'] = ema_orphans
        return info

    # Tier 0: CT.gov trial count as prevalence veto (only AFTER checking for
    # positive orphan evidence)
    trial_count = cached_trial_count if cached_trial_count is not None else _get_ctgov_trial_count(indication, mcp_funcs)
    is_clearly_common = trial_count is not None and trial_count > 2500

    if is_clearly_common:
        info['eligibility_signal'] = 'NOT_APPLICABLE'
        info['rationale'] = (
            f"{trial_count:,} clinical trials found for {indication} — "
            f"high trial volume indicates prevalence far exceeds 5 in 10,000 EU."
        )
        return info

    # Tier 3: Drug-count + trial-count heuristic fallback
    if len(precedents) >= 15:
        info['eligibility_signal'] = 'NOT_APPLICABLE'
        info['rationale'] = f"{len(precedents)} approved drug(s) found with no EU orphan designations — prevalence likely exceeds 5 in 10,000 EU"
    elif trial_count is not None and trial_count > 500 and len(precedents) >= 8:
        info['eligibility_signal'] = 'NOT_APPLICABLE'
        info['rationale'] = f"{len(precedents)} approved drugs and {trial_count:,} clinical trials with no EU orphan designations — prevalence likely exceeds 5 in 10,000 EU"
    elif len(precedents) <= 2:
        info['eligibility_signal'] = 'MODERATE'
        info['rationale'] = f"Only {len(precedents)} approved drug(s) found — limited market may indicate rare disease. Verify prevalence <5 in 10,000."
    elif trial_count is not None and trial_count < 200:
        info['eligibility_signal'] = 'MODERATE'
        info['rationale'] = f"Only {trial_count:,} clinical trials and {len(precedents)} approved drugs (none with EU orphan designation). Low trial volume suggests possible rare disease. Verify prevalence <5 in 10,000."
    else:
        info['eligibility_signal'] = 'MODERATE'
        info['rationale'] = f"Requires prevalence <5 in 10,000 EU ({len(precedents)} approved drugs, none with EU orphan designation). Verify with epidemiology data."

    return info


def _assess_conditional_ma(indication, precedents, prec_designations):
    """Assess Conditional MA eligibility."""
    info = dict(DESIGNATIONS['conditional_ma'])

    eu_conditional = [p for p in precedents if p.get('approval_pathway') == 'Conditional MA']
    if eu_conditional:
        info['eligibility_signal'] = 'STRONG'
        info['rationale'] = f"Precedent: {', '.join([p['brand_name'] for p in eu_conditional[:3]])} received conditional MA"
    elif len([p for p in precedents if p.get('region') == 'EU']) < 2:
        info['eligibility_signal'] = 'MODERATE'
        info['rationale'] = "Limited EU treatments suggests unmet need; conditional MA possible with incomplete data"
    else:
        info['eligibility_signal'] = 'WEAK'
        info['rationale'] = "Multiple EU treatments available; conditional MA requires clear unmet need"

    return info


def _analyze_pediatric(indication: str, target_regions: List[str], mcp_funcs: Dict = None, cached_total_trial_count: int = None) -> Dict[str, Any]:
    """Analyze pediatric obligation requirements.

    Uses CT.gov to dynamically check for pediatric trial activity instead of
    hardcoded adult-only/pediatric-relevant keyword lists.
    """
    result = {}
    if mcp_funcs is None:
        mcp_funcs = {}

    # Dynamic check: search CT.gov for pediatric trials in this indication
    pediatric_trial_count = _get_ctgov_pediatric_trial_count(indication, mcp_funcs)
    # Reuse cached total trial count if available (avoids redundant API call)
    total_trial_count = cached_total_trial_count if cached_total_trial_count is not None else _get_ctgov_trial_count(indication, mcp_funcs)

    if pediatric_trial_count is not None and total_trial_count:
        # Calculate pediatric ratio to filter noise (stray trials out of hundreds)
        peds_ratio = pediatric_trial_count / total_trial_count if total_trial_count > 0 else 0

        if pediatric_trial_count == 0 and total_trial_count > 20:
            # Many total trials but zero pediatric → likely adult-only disease
            pediatric_status = 'WAIVER_LIKELY'
            us_rationale = f"0 pediatric trials among {total_trial_count} total for {indication} — disease appears adult-only. Waiver request anticipated."
            eu_rationale = f"0 pediatric trials among {total_trial_count} total for {indication} — disease appears adult-only. Class waiver may apply."
        elif total_trial_count > 50 and peds_ratio < 0.01:
            # Pediatric trials <1% of total → likely noise/misclassification
            # (e.g., 5 out of 4,067 for Alzheimer's = 0.12%)
            pediatric_status = 'WAIVER_LIKELY'
            us_rationale = f"Only {pediatric_trial_count} pediatric trial(s) among {total_trial_count} total ({peds_ratio:.1%}) — minimal pediatric relevance. Waiver request anticipated."
            eu_rationale = f"Only {pediatric_trial_count} pediatric trial(s) among {total_trial_count} total ({peds_ratio:.1%}) — minimal pediatric relevance. Class waiver may apply."
        elif pediatric_trial_count > 0:
            pediatric_status = 'REQUIRED'
            us_rationale = f"{pediatric_trial_count} pediatric trials found for {indication}. Pediatric study plan required. Deferral possible until adult data available."
            eu_rationale = f"{pediatric_trial_count} pediatric trials found for {indication}. PIP required before MAA submission. Deferral possible."
        else:
            pediatric_status = 'ASSESSMENT_NEEDED'
            us_rationale = f"No pediatric trials found ({total_trial_count} total). Evaluate pediatric relevance — if disease occurs in children, study plan required."
            eu_rationale = f"No pediatric trials found ({total_trial_count} total). Evaluate pediatric relevance. PIP or waiver application needed."
    else:
        # No MCP data available — fall back to assessment needed
        pediatric_status = 'ASSESSMENT_NEEDED'
        us_rationale = "Evaluate pediatric relevance. If disease occurs in children, study plan required."
        eu_rationale = "Evaluate pediatric relevance. PIP or waiver application needed."

    if "US" in target_regions:
        prea = dict(PEDIATRIC_RULES['US_PREA'])
        prea['status'] = pediatric_status
        prea['rationale'] = us_rationale
        result['us_prea'] = prea

    if "EU" in target_regions:
        pip = dict(PEDIATRIC_RULES['EU_PIP'])
        pip['status'] = pediatric_status
        pip['rationale'] = eu_rationale
        result['eu_pip'] = pip

    return result


def _analyze_companion_diagnostic(
    indication: str, modality: str = None,
    precedents: List[Dict[str, Any]] = None, mcp_funcs: Dict = None,
) -> Dict[str, Any]:
    """Analyze companion diagnostic requirements.

    Uses OpenTargets genetic association evidence + precedent CDx data instead
    of hardcoded biomarker indication lists.
    """
    if precedents is None:
        precedents = []
    if mcp_funcs is None:
        mcp_funcs = {}

    modality_lower = (modality or '').lower()

    # Check 1: Did any precedent drug require a companion diagnostic?
    cdx_precedents = []
    for p in precedents:
        desigs = p.get('designations_granted', [])
        approval_info = ' '.join([
            p.get('approval_pathway', ''),
            p.get('notes', ''),
            ' '.join(desigs),
        ]).lower()
        if any(kw in approval_info for kw in ['companion diagnostic', 'cdx', 'biomarker', 'companion dx']):
            cdx_precedents.append(p.get('brand_name', p.get('drug_name', 'Unknown')))

    if cdx_precedents:
        return {
            'required': True,
            'rationale': f"Precedent CDx requirement: {', '.join(cdx_precedents[:3])} required companion diagnostic.",
            'recommendation': "Plan concurrent CDx development. FDA requires co-development for biomarker-selected populations.",
            'precedent_evidence': cdx_precedents,
        }

    # Check 2: Use OpenTargets to assess genetic association strength
    has_genetic_drivers = _has_strong_genetic_associations(indication, mcp_funcs)

    # Check 3: Is this a targeted modality? (modality types are a finite set, not disease data)
    targeted_modalities = ['antibody', 'adc', 'car-t', 'cell therapy', 'bispecific']
    is_targeted = any(kw in modality_lower for kw in targeted_modalities)

    # CDx is required for biomarker-SELECTED therapies (e.g., EGFR mutation testing in NSCLC),
    # NOT for genetically-ASSOCIATED diseases (e.g., Crohn's has NOD2 risk variants but
    # biologics are NOT biomarker-selected). When many drugs are approved without CDx,
    # genetic associations are risk factors, not treatment selection biomarkers.
    if has_genetic_drivers and is_targeted and len(precedents) < 10:
        return {
            'required': True,
            'rationale': f"OpenTargets shows strong genetic associations for {indication} + targeted modality ({modality}) — CDx likely required for patient selection.",
            'recommendation': "Plan concurrent CDx development. FDA requires co-development for biomarker-selected populations.",
        }
    elif has_genetic_drivers and is_targeted:
        # Many approved drugs + genetic associations = likely risk factors, not selection biomarkers
        return {
            'required': False,
            'rationale': f"OpenTargets shows genetic associations for {indication}, but {len(precedents)} approved drugs exist without CDx requirements. Genetic associations are likely risk factors, not treatment selection biomarkers.",
            'recommendation': "CDx unlikely required. Consider pharmacogenomic testing only if biomarker-enrichment improves response rates.",
        }
    elif has_genetic_drivers:
        return {
            'required': False,
            'rationale': f"OpenTargets shows genetic associations for {indication}, but modality may not require biomarker-based selection.",
            'recommendation': "Assess whether a biomarker-enrichment strategy would improve efficacy.",
        }
    elif is_targeted:
        return {
            'required': False,
            'rationale': f"Targeted modality ({modality}) but no strong genetic driver evidence found for {indication}.",
            'recommendation': "Evaluate whether patient selection biomarker exists for this target.",
        }
    else:
        return {
            'required': False,
            'rationale': "No genetic driver evidence or targeted modality. Companion diagnostic unlikely to be required.",
            'recommendation': None,
        }
