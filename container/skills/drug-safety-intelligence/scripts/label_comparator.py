"""Cross-class FDA/EMA label comparison for drug safety intelligence.

Compares safety sections across drugs in the same class to identify:
- Class-wide effects (present in >50% of drug labels)
- Drug-specific outliers (unique safety signals)
- Boxed warning (BBW) patterns
- Warnings & Precautions (W&P) commonalities

All term lists are dynamic — no hardcoded drug names, brand names, or AE terms.
"""

from typing import Dict, Any, List, Optional, Set
import re
from collections import defaultdict

from dynamic_vocabulary import build_noise_set_from_label


def _title_case_drug(name: str) -> str:
    """Normalize drug name to title case."""
    if not name:
        return name
    return name.strip().title()


# Generic noise patterns — sentence fragments, study methodology, formatting artifacts.
# These are language patterns, NOT drug/company/AE names (those come from dynamic vocab).
_GENERIC_NOISE_PATTERNS = [
    'approximately', 'mg ', ' at ', 'reflect exposure', 'the most common',
    'hours in', 'please report', 'telephone', 'www.', 'http', '.com',
    'section', 'table ', 'see ', 'figure', 'included', 'patients in',
    'months and', 'years of', 'clinical trial', 'randomized',
    'cludes ', 'cluding ', 'monother', 'combinat', 'median',
    'treated with', 'receiving ', 'compared to', 'versus ',
    'was reported', 'were reported', 'occurred in', 'observed in',
    'study ', 'studies ', 'trial ', 'trials ', 'n = ', 'n=',
    'of patients', 'of subjects', 'dose ', 'daily ', 'twice',
    'week', 'the following', 'have been', 'has been',
    'should be', 'may be', 'can be', 'is not', 'are not',
    'for more', 'for additional', 'refer to', 'contact',
    'fda at',  # FDA contact info (generic, not company-specific)
]


def _make_noise_checker(dynamic_noise: Set[str] = None):
    """Create a noise checker function that combines generic + dynamic noise patterns.

    Args:
        dynamic_noise: Set of lowercase strings (brand names, company names, drug names)
                       built dynamically from FDA label responses.
    """
    dynamic = dynamic_noise or set()

    def _is_noise(text: str) -> bool:
        t = text.lower().strip()
        if len(t) < 8 or len(t) > 80:
            return True
        if any(p in t for p in _GENERIC_NOISE_PATTERNS):
            return True
        # Check dynamic noise terms (brand names, company names, drug names)
        if any(p in t for p in dynamic if len(p) > 3):
            return True
        # Skip lines that are mostly numbers or short fragments
        alpha_count = sum(1 for c in t if c.isalpha())
        if alpha_count < len(t) * 0.5:
            return True
        # Skip lines with too many words (likely sentence fragments, not event names)
        if len(t.split()) > 8:
            return True
        return False

    return _is_noise


def _extract_monitoring_text(label: Dict) -> List[str]:
    """Extract monitoring/lab test recommendations from FDA label.

    FDA labels often have subsections like "5.X Monitoring and Laboratory Tests"
    or embedded monitoring guidance within W&P subsections.
    """
    monitoring = []
    wp_fields = ['warnings_and_cautions', 'warnings_and_precautions', 'warnings']
    for field in wp_fields:
        wp = label.get(field)
        if not wp:
            continue
        texts = wp if isinstance(wp, list) else [wp]
        for text in texts:
            if not isinstance(text, str):
                continue
            # Look for monitoring-specific subsections
            mon_matches = re.findall(
                r'(?:monitor|laboratory|lab test|baseline|periodic|assess|measure|check)'
                r'[^.]*?(?:CBC|LFT|ECG|echocardiogram|creatinine|lipase|troponin|thyroid|'
                r'blood count|liver function|renal function|electrolyte|glucose|hemoglobin|'
                r'platelet|neutrophil|bilirubin|ALT|AST|eGFR|BNP|INR|coagulation)[^.]*\.',
                text[:8000], re.IGNORECASE
            )
            for m in mon_matches:
                m = m.strip()
                if 20 < len(m) < 300:
                    monitoring.append(m)
    return monitoring[:10]


def _extract_from_structured_label(
    label_result: Dict,
    dynamic_noise: Set[str] = None,
    faers_warning_stems: List[str] = None,
    faers_ar_terms: List[str] = None,
) -> Dict[str, Any]:
    """Extract safety sections from structured FDA label API response.

    Args:
        label_result: Raw FDA label API response
        dynamic_noise: Dynamic noise set (brand names, company names)
        faers_warning_stems: FAERS-derived W&P vocabulary (replaces hardcoded known_warnings)
        faers_ar_terms: FAERS-derived AR vocabulary (replaces hardcoded known_ars)
    """
    sections = {
        'boxed_warnings': [],
        'warnings_precautions': [],
        'adverse_reactions': [],
        'contraindications': [],
        'monitoring_recommendations': [],
        'label_section_origins': {},  # event -> section it came from (for severity scoring)
    }

    data = label_result.get('data', {})
    results = data.get('results', [])
    if not results:
        return sections

    label = results[0]

    # Boxed warning
    bbw = label.get('boxed_warning', [])
    if isinstance(bbw, list):
        for w in bbw:
            if w and isinstance(w, str):
                warnings = [s.strip() for s in w[:500].split('\n') if s.strip() and len(s.strip()) > 10]
                sections['boxed_warnings'].extend(warnings[:5])
    elif isinstance(bbw, str) and bbw:
        sections['boxed_warnings'] = [s.strip() for s in bbw[:500].split('\n') if s.strip() and len(s.strip()) > 10][:5]

    # Build noise checker with dynamic terms
    _is_noise = _make_noise_checker(dynamic_noise)

    # Warnings and precautions — extract numbered subsection headers (e.g., "5.1 Hemorrhage")
    wp = label.get('warnings_and_cautions', label.get('warnings_and_precautions', label.get('warnings', [])))

    def _extract_wp_headers(text: str) -> list:
        """Extract W&P subsection headers from FDA label text."""
        headers = []

        # Strategy 1: Summary format "Term : description ( 5.X )"
        # Common in FDA labels — the top of W&P lists all subsections
        summary_matches = re.findall(
            r'([A-Z][A-Za-z\s,]+?)\s*:\s*[A-Z].*?\(\s*5\.\d+\s*\)',
            text[:2000]
        )
        for h in summary_matches:
            h = h.strip()
            # Strip leading section title artifacts
            for prefix in ['WARNINGS AND PRECAUTIONS ', 'WARNINGS AND CAUTIONS ']:
                if h.upper().startswith(prefix.rstrip()):
                    h = h[len(prefix):].strip()
            if h and not _is_noise(h) and h not in headers:
                headers.append(h)

        # Strategy 2: Numbered headers like "5.1 Hemorrhage" (deeper in text)
        if not headers:
            numbered = re.findall(
                r'5\.\d+\s+([A-Z][A-Za-z\s,/\-]{4,60}?)(?:\s{2,}|\n|\.(?:\s|$)|[A-Z][a-z])',
                text[:8000]
            )
            for h in numbered:
                h = h.strip().rstrip('.')
                if h and re.match(r'^[a-z]+\s+', h):
                    h = re.sub(r'^[a-z]+\s+', '', h)
                if h and not _is_noise(h) and h not in headers:
                    headers.append(h)

        # Strategy 3: Dynamic FAERS-derived warning vocabulary
        if not headers and faers_warning_stems:
            text_lower = text[:8000].lower()
            for kw in faers_warning_stems:
                if kw in text_lower:
                    idx = text_lower.index(kw)
                    snippet = text[idx:idx + len(kw) + 40]
                    match = re.search(r'([A-Z][A-Za-z\s,/\-]{4,50})', snippet)
                    if match:
                        h = match.group(1).strip()
                        if h and not _is_noise(h) and h not in headers:
                            headers.append(h)
        return headers

    if isinstance(wp, list):
        for w in wp:
            if w and isinstance(w, str):
                sections['warnings_precautions'].extend(_extract_wp_headers(w))
    elif isinstance(wp, str) and wp:
        sections['warnings_precautions'] = _extract_wp_headers(wp)
    sections['warnings_precautions'] = sections['warnings_precautions'][:10]

    # Track label section origins for severity scoring
    for wp_term in sections['warnings_precautions']:
        sections['label_section_origins'][wp_term.lower()] = 'warnings_precautions'
    for bbw_term in sections['boxed_warnings']:
        sections['label_section_origins'][bbw_term.lower()] = 'boxed_warning'

    # Adverse reactions — extract medical terms from tabular data
    ar = label.get('adverse_reactions', [])

    def _extract_ar_terms(text: str) -> list:
        """Extract adverse reaction terms from FDA label AR section."""
        terms = []
        # Strategy 1: Terms followed by percentage/parenthetical numbers
        matches = re.findall(
            r'(?:^|\n)\s*[-•]?\s*([A-Z][a-z]+(?:\s+[a-z]+){0,2})\s+(?:\(?(\d+(?:\.\d+)?)\s*%|\(\d+)',
            text[:8000]
        )
        for m in matches:
            term = m[0].strip() if isinstance(m, tuple) else m.strip()
            if term and not _is_noise(term) and len(term) > 4:
                terms.append(term)

        # Strategy 2: Tabular data — "Term  Number" (term followed by count, common in FDA tables)
        if len(terms) < 3:
            table_matches = re.findall(
                r'([A-Z][a-z]+(?:\s+[a-z]+){0,2})\s+(\d{1,3})(?:\s|$)',
                text[1000:8000]  # skip header area
            )
            for term, count in table_matches:
                term = term.strip()
                # Filter noise: skip study/table/grade references
                if (term and not _is_noise(term) and len(term) > 4
                        and term.lower() not in ('study', 'table', 'grade', 'four', 'three')):
                    if term not in terms:
                        terms.append(term)

        # Strategy 3: Dynamic FAERS-derived AR vocabulary
        if len(terms) < 3 and faers_ar_terms:
            text_lower = text[:8000].lower()
            for ar_term in faers_ar_terms:
                if ar_term in text_lower and ar_term.title() not in terms:
                    terms.append(ar_term.title())
        return terms

    if isinstance(ar, list):
        for a in ar:
            if a and isinstance(a, str):
                sections['adverse_reactions'].extend(_extract_ar_terms(a))
    sections['adverse_reactions'] = list(dict.fromkeys(sections['adverse_reactions']))[:15]

    # Track AR section origins
    for ar_term in sections['adverse_reactions']:
        if ar_term.lower() not in sections['label_section_origins']:
            sections['label_section_origins'][ar_term.lower()] = 'adverse_reactions'

    # Contraindications
    ci = label.get('contraindications', [])
    if isinstance(ci, list):
        for c in ci:
            if c and isinstance(c, str):
                contras = [s.strip() for s in c[:500].split('\n') if s.strip() and len(s.strip()) > 10]
                sections['contraindications'].extend(contras)
    sections['contraindications'] = sections['contraindications'][:5]

    # Extract monitoring recommendations from label
    sections['monitoring_recommendations'] = _extract_monitoring_text(label)

    return sections


def compare_labels(
    fda_lookup_func,
    ema_search_func,
    drug_names: List[str],
    tracker=None,
    faers_warning_stems: List[str] = None,
    faers_ar_terms: List[str] = None,
) -> Dict[str, Any]:
    """
    Compare FDA/EMA labels across drugs in a class.

    Args:
        fda_lookup_func: FDA lookup function
        ema_search_func: EMA search function
        drug_names: List of drug names to compare
        tracker: ProgressTracker instance
        faers_warning_stems: FAERS-derived warning vocabulary (dynamic)
        faers_ar_terms: FAERS-derived adverse reaction vocabulary (dynamic)

    Returns:
        dict with drug_labels, class_effects, outliers, dynamic_noise, label_section_origins, summary
    """
    if tracker:
        tracker.start_step('label_comparison', f"Comparing labels for {len(drug_names)} drugs...")

    drug_labels = []
    all_warnings = defaultdict(list)  # warning -> [drugs that have it]
    all_reactions = defaultdict(list)
    all_label_section_origins = {}  # event_lower -> section name (aggregated)
    all_monitoring = []  # monitoring recommendations extracted from labels

    # Dynamic noise set — built from each FDA label response as we go
    dynamic_noise = set()
    # Seed with drug names themselves
    for dn in drug_names:
        if dn:
            dynamic_noise.add(dn.lower())

    # Cap at 10 drugs to control API calls
    drugs_to_analyze = drug_names[:10]

    for i, drug_name in enumerate(drugs_to_analyze):
        if tracker:
            progress = (i + 1) / len(drugs_to_analyze)
            tracker.update_step(progress * 0.8, f"Analyzing label for {_title_case_drug(drug_name)}...")

        drug_label = {
            'drug_name': _title_case_drug(drug_name),
            'boxed_warnings': [],
            'warnings_precautions': [],
            'adverse_reactions': [],
            'contraindications': [],
            'has_bbw': False,
            'fda_found': False,
            'ema_found': False,
        }

        # FDA label lookup
        try:
            fda_result = fda_lookup_func(
                search_term=drug_name,
                search_type='label',
                limit=1,
            )

            if fda_result:
                # Extract brand/manufacturer names for dynamic noise filtering
                label_noise = build_noise_set_from_label(fda_result)
                dynamic_noise.update(label_noise)

                sections = _extract_from_structured_label(
                    fda_result,
                    dynamic_noise=dynamic_noise,
                    faers_warning_stems=faers_warning_stems,
                    faers_ar_terms=faers_ar_terms,
                )
                drug_label['boxed_warnings'] = sections['boxed_warnings']
                drug_label['warnings_precautions'] = sections['warnings_precautions']
                drug_label['adverse_reactions'] = sections['adverse_reactions']
                drug_label['contraindications'] = sections['contraindications']
                drug_label['has_bbw'] = len(sections['boxed_warnings']) > 0
                drug_label['fda_found'] = True

                # Collect label section origins for severity scoring
                all_label_section_origins.update(sections.get('label_section_origins', {}))

                # Collect monitoring recommendations
                all_monitoring.extend(sections.get('monitoring_recommendations', []))

                # Track for class effect detection
                for w in sections['warnings_precautions']:
                    all_warnings[w.lower()].append(drug_name)
                for r in sections['adverse_reactions']:
                    all_reactions[r.lower()].append(drug_name)
        except Exception as e:
            print(f"  Warning: FDA label lookup failed for {drug_name}: {e}")

        # EMA lookup (graceful - often returns 0)
        if ema_search_func:
            try:
                ema_result = ema_search_func(method='search_medicines', query=drug_name)
                if ema_result and isinstance(ema_result, str) and drug_name.lower() in ema_result.lower():
                    drug_label['ema_found'] = True
            except Exception:
                pass  # EMA often returns 0 results - graceful fallback

        drug_labels.append(drug_label)

    # Identify class effects (present in >50% of drugs WITH label data)
    drugs_with_data = sum(1 for d in drug_labels if d['fda_found'] and
                          (d['warnings_precautions'] or d['adverse_reactions']))
    threshold = max(2, drugs_with_data // 2) if drugs_with_data > 0 else 2
    class_effects = []
    drug_specific = []

    for warning, drugs in all_warnings.items():
        if len(drugs) >= threshold:
            class_effects.append({
                'event': warning.title(),
                'drugs': [_title_case_drug(d) for d in drugs],
                'prevalence': f"{len(drugs)}/{len(drugs_to_analyze)}",
                'type': 'warning',
            })
        elif len(drugs) == 1:
            drug_specific.append({
                'event': warning.title(),
                'drug': _title_case_drug(drugs[0]),
                'type': 'warning',
            })

    for reaction, drugs in all_reactions.items():
        if len(drugs) >= threshold:
            class_effects.append({
                'event': reaction.title(),
                'drugs': [_title_case_drug(d) for d in drugs],
                'prevalence': f"{len(drugs)}/{len(drugs_to_analyze)}",
                'type': 'adverse_reaction',
            })

    if tracker:
        tracker.complete_step(
            f"Labels compared: {len(drug_labels)} drugs, "
            f"{len(class_effects)} class effects, "
            f"{len(drug_specific)} drug-specific signals"
        )

    return {
        'drug_labels': drug_labels,
        'class_effects': class_effects,
        'drug_specific_outliers': drug_specific[:20],
        'dynamic_noise': dynamic_noise,  # Pass to risk_matrix_builder
        'label_section_origins': all_label_section_origins,  # For severity scoring
        'monitoring_recommendations': all_monitoring,  # For dynamic monitoring
        'summary': {
            'total_drugs_analyzed': len(drug_labels),
            'drugs_with_fda_labels': sum(1 for d in drug_labels if d['fda_found']),
            'drugs_with_ema_data': sum(1 for d in drug_labels if d['ema_found']),
            'drugs_with_bbw': sum(1 for d in drug_labels if d['has_bbw']),
            'class_effects_count': len(class_effects),
            'drug_specific_outliers_count': len(drug_specific),
        },
    }
