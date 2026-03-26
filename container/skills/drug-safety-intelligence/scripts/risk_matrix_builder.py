"""Risk matrix builder for drug safety intelligence.

Builds a 4-dimensional risk matrix:
- Severity (0-1): How dangerous is the adverse event?
- Evidence (0-1): How strong is the evidence?
- Reversibility (0-1): Is it reversible on discontinuation? (higher = more reversible)
- Monitorability (0-1): Can it be monitored/detected early? (higher = more monitorable)

Overall score = 0.40 * severity + 0.30 * evidence + 0.20 * (1 - reversibility) + 0.10 * (1 - monitorability)

Tiers: >= 0.7 = HIGH, >= 0.4 = MODERATE, < 0.4 = LOW

All scoring uses body-system-level defaults + FDA label section positioning.
No hardcoded individual AE terms, brand names, or drug names.
"""

from typing import Dict, Any, List, Optional, Set
from collections import defaultdict
import re

# Import fuzzy matcher — available when FAERS terms are present
try:
    from dynamic_vocabulary import fuzzy_match_to_faers
except ImportError:
    fuzzy_match_to_faers = None


# =============================================================================
# Body-system severity ranges (11 organ systems — covers ALL adverse events)
# These are medical constants (organ failure severity), not drug-specific.
# =============================================================================
_BODY_SYSTEM_SEVERITY = {
    # System keyword stems -> (default_severity, reversibility_default, monitorability_default)
    # Fatal / life-threatening organ systems
    'cardiac': (0.75, 0.3, 0.7),    # ECG, echo, troponin
    'vascular': (0.70, 0.3, 0.5),
    'hepat': (0.70, 0.4, 0.8),      # LFTs
    'renal': (0.65, 0.4, 0.8),      # creatinine, eGFR
    'pulmon': (0.65, 0.4, 0.5),
    'nervous': (0.60, 0.3, 0.4),    # hard to monitor
    'haem': (0.60, 0.5, 0.9),       # CBC
    'hem': (0.60, 0.5, 0.9),        # hematologic (US spelling)
    'blood': (0.60, 0.5, 0.9),
    'immune': (0.55, 0.4, 0.5),
    'infect': (0.55, 0.5, 0.6),
    'neoplas': (0.80, 0.1, 0.4),    # tumors/malignancies
    'malignan': (0.80, 0.1, 0.4),
    'tumor': (0.75, 0.1, 0.4),
    'endocri': (0.50, 0.5, 0.7),    # thyroid, glucose tests
    'thyroid': (0.50, 0.5, 0.7),
    'pancrea': (0.65, 0.4, 0.6),    # lipase
    'gastro': (0.30, 0.8, 0.6),     # generally reversible
    'intestin': (0.30, 0.8, 0.6),
    'musculo': (0.25, 0.7, 0.5),
    'skin': (0.25, 0.8, 0.5),
    'dermat': (0.25, 0.8, 0.5),
    'eye': (0.40, 0.4, 0.6),
    'ocular': (0.40, 0.4, 0.6),
    'reproduct': (0.50, 0.2, 0.3),  # embryo-fetal
    'fetal': (0.60, 0.1, 0.3),
    'embryo': (0.60, 0.1, 0.3),
    'psych': (0.55, 0.5, 0.4),      # suicidal, psychosis
    'suicid': (0.80, 0.3, 0.4),
}

# High-severity signal words (not drug-specific, just medical severity)
_SEVERITY_SIGNAL_WORDS = {
    'death': 1.0, 'fatal': 1.0, 'lethal': 1.0,
    'arrest': 0.95, 'failure': 0.85, 'shock': 0.85,
    'anaphyla': 0.90, 'stevens-johnson': 0.95, 'toxic epidermal': 0.95,
    'embolism': 0.85, 'infarction': 0.85, 'stroke': 0.85,
    'perforation': 0.80, 'necrosis': 0.80, 'sepsis': 0.80,
    'syndrome': 0.55,  # moderate default for named syndromes
}

# Label section → severity modifier (replaces per-AE hardcoding)
_SECTION_SEVERITY_BOOST = {
    'boxed_warning': 0.90,        # BBW = highest severity signal
    'warnings_precautions': 0.65, # W&P = serious
    'adverse_reactions': 0.30,    # AR = moderate (common, expected)
}


def _get_body_system_scores(event_name: str) -> tuple:
    """Get severity, reversibility, monitorability from body system matching.

    Returns (severity, reversibility, monitorability) or None if no match.
    """
    event_lower = event_name.lower()

    # Check severity signal words first (organ-independent)
    for word, sev in sorted(_SEVERITY_SIGNAL_WORDS.items(), key=lambda x: -len(x[0])):
        if word in event_lower:
            return (sev, 0.2, 0.4)  # severe events default low reversibility

    # Match body system
    for stem, (sev, rev, mon) in _BODY_SYSTEM_SEVERITY.items():
        if stem in event_lower:
            return (sev, rev, mon)

    return None


def _get_severity_score(
    event_name: str,
    label_section: str = None,
) -> float:
    """Score severity using body system + label section positioning.

    Priority:
    1. Label section (BBW=0.9, W&P=0.65, AR=0.3)
    2. Body system severity
    3. Severity signal words
    4. Default 0.3
    """
    # Start with body system / signal word score
    system_scores = _get_body_system_scores(event_name)
    base_severity = system_scores[0] if system_scores else 0.3

    # Label section positioning overrides/adjusts
    if label_section:
        section_floor = _SECTION_SEVERITY_BOOST.get(label_section, 0.3)
        # Use the higher of body-system severity and section-implied severity
        base_severity = max(base_severity, section_floor)

    return round(min(1.0, base_severity), 2)


def _get_reversibility_score(
    event_name: str,
    label_section: str = None,
) -> float:
    """Score reversibility using body system defaults.

    BBW events default to lower reversibility.
    """
    system_scores = _get_body_system_scores(event_name)
    if system_scores:
        rev = system_scores[1]
    else:
        rev = 0.5  # default

    # BBW events are generally less reversible
    if label_section == 'boxed_warning':
        rev = min(rev, 0.3)

    return round(rev, 2)


def _get_monitorability_score(
    event_name: str,
) -> float:
    """Score monitorability using body system defaults."""
    system_scores = _get_body_system_scores(event_name)
    if system_scores:
        return round(system_scores[2], 2)
    return 0.4  # default


def _get_evidence_score(
    in_label: bool = False,
    is_bbw: bool = False,
    trial_signal: bool = False,
    literature_count: int = 0,
    faers_count: int = 0,
    class_effect: bool = False,
) -> float:
    """Score evidence strength (0-1)."""
    score = 0.0

    if is_bbw:
        score = max(score, 0.95)
    elif in_label:
        score = max(score, 0.7)

    if trial_signal:
        score = max(score, 0.6)

    if literature_count >= 5:
        score = max(score, 0.7)
    elif literature_count >= 2:
        score = max(score, 0.5)
    elif literature_count >= 1:
        score = max(score, 0.3)

    if faers_count >= 1000:
        score = max(score, 0.6)
    elif faers_count >= 100:
        score = max(score, 0.4)

    if class_effect:
        score = min(1.0, score + 0.15)

    return min(1.0, score)


def calculate_overall_score(
    severity: float,
    evidence: float,
    reversibility: float,
    monitorability: float,
) -> float:
    """Calculate overall risk score."""
    return round(
        0.40 * severity +
        0.30 * evidence +
        0.20 * (1 - reversibility) +
        0.10 * (1 - monitorability),
        3
    )


def classify_tier(score: float) -> str:
    """Classify risk tier from overall score."""
    if score >= 0.7:
        return 'HIGH'
    elif score >= 0.4:
        return 'MODERATE'
    return 'LOW'


# =============================================================================
# Noise filter — generic patterns only (no hardcoded brand/drug names)
# =============================================================================

# Generic noise patterns — sentence fragments, methodology, formatting artifacts
_GENERIC_NOISE = [
    'patients ', 'subjects ', 'months ', 'years ', 'weeks ',
    'cludes ', 'cluding ', 'monother', 'combinat',
    'treated with', 'receiving ', 'compared to', 'versus ',
    'was reported', 'were reported', 'occurred in', 'observed in',
    'was evaluated', 'were exposed', 'were enrolled', 'were treated',
    'administered ', 'a total of', 'among these', 'among the',
    'study ', 'studies ', 'clinical trial', 'randomized', 'median',
    'table ', 'section ', 'see ', 'figure', 'contact', 'telephone',
    'mg ', 'daily ', 'twice', 'dose ', 'the following', 'have been',
    'should be', 'may be', 'can be', 'for more', 'refer to', 'included',
    'approximately', 'www.', 'http', '.com',
    'flects ', 'reflects ', 'exposure to',
    'performance status', 'ecog ', 'or longer',
    'received ', 'total of', 'evaluated in',
    'institute ', 'medical ',
    'can cause', 'can caus', 'may cause',
    'tumors ', ' causes ', ' caused ', 'monitor for', 'early ident',
    'd an ', 'an ecog', 'in a ', 'of the ', 'with a ',
    'ions ', 'ons ', 'tion ',  # prefix artifacts from truncated words
]

_SENTENCE_STARTS = [
    'a ', 'an ', 'the ', 'in ', 'of ', 'for ', 'with ', 'from ',
    'to ', 'by ', 'at ', 'on ', 'was ', 'were ', 'had ', 'has ',
    'is ', 'are ', 'it ', 'this ', 'that ', 'which ', 'who ',
    'd ', 'and ', 'or ', 'but ', 'not ', 'no ',
]


def _is_valid_event_name(event_name: str, dynamic_noise: Set[str] = None) -> bool:
    """Filter out garbage event names that aren't real adverse events.

    Uses generic language patterns + dynamic noise set (brand/drug/company names).
    No hardcoded drug names or brand names.
    """
    if not event_name or len(event_name) < 4:
        return False
    t = event_name.lower().strip()
    if len(t) > 80 or len(t.split()) > 8:
        return False
    words = t.split()
    if len(words) < 2 and len(t) < 6:
        return False
    alpha_count = sum(1 for c in t if c.isalpha())
    if alpha_count < len(t) * 0.5:
        return False

    # Generic noise patterns
    if any(p in t for p in _GENERIC_NOISE):
        return False

    # Dynamic noise (drug names, brand names, company names)
    if dynamic_noise:
        if any(p in t for p in dynamic_noise if len(p) > 3):
            return False

    # Reject sentence-start words
    if any(t.startswith(p) for p in _SENTENCE_STARTS):
        return False

    return True


def _normalize_event_key(
    event_name: str,
    canonical_map: Dict[str, str] = None,
    faers_terms: List[str] = None,
) -> str:
    """Normalize event name for deduplication.

    Uses fuzzy matching against FAERS MedDRA Preferred Terms to handle:
    - Typos ('arrythmia' → 'arrhythmia')
    - US/UK spelling ('haemorrhage' → 'hemorrhage')
    - Minor variants ('cardiac arrythmias' → 'cardiac arrhythmia')

    No hardcoded correction tables — scales to any drug class automatically.
    Falls back to stem-based canonical map when fuzzy match doesn't hit.
    """
    t = event_name.lower().strip()

    # Strip trailing single-character artifacts (e.g., "Hemorrhage F" → "hemorrhage")
    t = re.sub(r'\s+[a-z]$', '', t)

    # 1. Exact match against FAERS canonical map (fast path)
    if canonical_map and t in canonical_map:
        return canonical_map[t]

    # 2. Fuzzy match against FAERS MedDRA PTs (catches typos + spelling variants)
    if faers_terms and fuzzy_match_to_faers:
        match = fuzzy_match_to_faers(t, faers_terms, cutoff=0.75)
        if match:
            return match

    return t


def _get_monitoring_recommendation(
    event_name: str,
    tier: str,
    label_monitoring: List[str] = None,
) -> str:
    """Generate monitoring recommendation.

    Priority:
    1. Use monitoring text extracted from actual FDA label
    2. Fall back to body-system-based generic guidance
    """
    event_lower = event_name.lower()

    # Try to find a matching recommendation from extracted label text
    if label_monitoring:
        for rec in label_monitoring:
            rec_lower = rec.lower()
            # Match if the event name (or a significant stem) appears in the recommendation
            words = event_lower.split()
            for word in words:
                if len(word) > 4 and word in rec_lower:
                    return rec[:200]

    # Body-system-based generic monitoring (NOT AE-specific hardcoding)
    system_scores = _get_body_system_scores(event_name)
    if system_scores:
        mon_score = system_scores[2]
        if mon_score >= 0.8:
            return "Lab monitoring at baseline and periodically per prescribing information"
        elif mon_score >= 0.6:
            return "Clinical monitoring; educate patient on early signs and symptoms"

    # Tier-based fallback
    if tier == 'HIGH':
        return "Close monitoring required; consider specialist referral"
    elif tier == 'MODERATE':
        return "Regular monitoring; patient education on early signs"
    return "Standard monitoring per prescribing information"


def build_risk_matrix(
    label_data: Dict = None,
    trial_signals: Dict = None,
    literature_data: Dict = None,
    target_biology: Dict = None,
    interaction_data: Dict = None,
    epidemiology_data: Dict = None,
    dynamic_noise: Set[str] = None,
    canonical_map: Dict[str, str] = None,
    faers_terms: List[str] = None,
    label_section_origins: Dict[str, str] = None,
    label_monitoring: List[str] = None,
) -> Dict[str, Any]:
    """
    Build comprehensive risk matrix from all evidence sources.

    Args:
        label_data: Output from label_comparator
        trial_signals: Output from trial_safety_scanner
        literature_data: Output from literature_synthesizer
        target_biology: Output from target_biology
        interaction_data: Output from interaction_analyzer
        epidemiology_data: Output from epidemiology_context
        dynamic_noise: Dynamic noise set for filtering (brand/drug/company names)
        canonical_map: FAERS-derived canonical event name mapping
        faers_terms: FAERS MedDRA PTs for fuzzy matching (replaces hardcoded typo/spelling dicts)
        label_section_origins: Map of event_lower -> label section name
        label_monitoring: Monitoring recommendations extracted from labels

    Returns:
        dict with risks (list), summary, recommendations
    """
    section_origins = label_section_origins or {}
    monitoring_recs = label_monitoring or []

    # Also pull section origins and monitoring from label_data if not passed separately
    if label_data:
        section_origins.update(label_data.get('label_section_origins', {}))
        monitoring_recs.extend(label_data.get('monitoring_recommendations', []))

    # Also use dynamic noise from label_data if not passed separately
    if not dynamic_noise and label_data:
        dynamic_noise = label_data.get('dynamic_noise', set())

    # Collect all adverse events with evidence
    event_evidence = defaultdict(lambda: {
        'sources': [],
        'in_label': False,
        'is_bbw': False,
        'trial_signal': False,
        'literature_count': 0,
        'faers_count': 0,
        'class_effect': False,
        'drugs_affected': set(),
        'details': [],
    })

    # 1. Label data
    if label_data:
        for effect in label_data.get('class_effects', []):
            event_name = effect.get('event', '')
            if event_name:
                ev = event_evidence[event_name.lower()]
                ev['class_effect'] = True
                ev['in_label'] = True
                ev['sources'].append('FDA Label (class effect)')
                ev['drugs_affected'].update(effect.get('drugs', []))

        for drug_label in label_data.get('drug_labels', []):
            drug_name = drug_label.get('drug_name', '')
            for warning in drug_label.get('boxed_warnings', []):
                if warning:
                    ev = event_evidence[warning.lower()[:80]]
                    ev['is_bbw'] = True
                    ev['in_label'] = True
                    ev['sources'].append(f'BBW ({drug_name})')
                    ev['drugs_affected'].add(drug_name)
            for warning in drug_label.get('warnings_precautions', []):
                if warning:
                    ev = event_evidence[warning.lower()[:80]]
                    ev['in_label'] = True
                    ev['sources'].append(f'W&P ({drug_name})')
                    ev['drugs_affected'].add(drug_name)
            for ar in drug_label.get('adverse_reactions', []):
                if ar:
                    ev = event_evidence[ar.lower()[:80]]
                    ev['in_label'] = True
                    ev['sources'].append(f'AR ({drug_name})')
                    ev['drugs_affected'].add(drug_name)

    # 2. Trial signals
    if trial_signals:
        for signal in trial_signals.get('safety_signals', []):
            reason = signal.get('reason', '')
            if reason:
                ev = event_evidence[reason.lower()[:80]]
                ev['trial_signal'] = True
                ev['sources'].append(f"Trial signal ({signal.get('nct_id', 'NCT?')})")

    # 3. Literature
    if literature_data:
        for article in literature_data.get('articles', []):
            title = article.get('title', '').lower()
            for event_key in list(event_evidence.keys()):
                if event_key in title:
                    event_evidence[event_key]['literature_count'] += 1
                    event_evidence[event_key]['sources'].append(
                        f"PubMed ({article.get('pmid', 'PMID?')})"
                    )

    # 4. Target biology
    if target_biology:
        for liability in target_biology.get('safety_liabilities', []):
            if liability:
                ev = event_evidence[liability.lower()[:80]]
                ev['sources'].append('Target biology (OpenTargets)')
                ev['details'].append(f"Predicted from target biology: {liability}")
        for pheno in target_biology.get('ko_phenotypes', []):
            phenotype = pheno.get('phenotype', '')
            if phenotype and pheno.get('severity') in ('severe', 'moderate'):
                ev = event_evidence[phenotype.lower()[:80]]
                ev['sources'].append('KO phenotype (OpenTargets)')

    # 5. Deduplicate events using canonical keys
    deduped_evidence = defaultdict(lambda: {
        'sources': [],
        'in_label': False,
        'is_bbw': False,
        'trial_signal': False,
        'literature_count': 0,
        'faers_count': 0,
        'class_effect': False,
        'drugs_affected': set(),
        'details': [],
        'display_name': '',
    })

    for event_name, ev_data in event_evidence.items():
        if not _is_valid_event_name(event_name, dynamic_noise):
            continue
        canonical = _normalize_event_key(event_name, canonical_map, faers_terms)
        merged = deduped_evidence[canonical]
        merged['sources'].extend(ev_data['sources'])
        merged['in_label'] = merged['in_label'] or ev_data['in_label']
        merged['is_bbw'] = merged['is_bbw'] or ev_data['is_bbw']
        merged['trial_signal'] = merged['trial_signal'] or ev_data['trial_signal']
        merged['literature_count'] += ev_data['literature_count']
        merged['faers_count'] += ev_data['faers_count']
        merged['class_effect'] = merged['class_effect'] or ev_data['class_effect']
        merged['drugs_affected'].update(ev_data['drugs_affected'])
        merged['details'].extend(ev_data['details'])
        # Clean display name: strip trailing single chars (e.g., "Hemorrhage F")
        clean_name = re.sub(r'\s+[a-z]$', '', event_name)
        if not merged['display_name'] or len(clean_name) > len(merged['display_name']):
            merged['display_name'] = clean_name

    # 6. Word-subset dedup — merge "second malignancies" into "second primary malignancies"
    keys_to_merge = []
    all_keys = sorted(deduped_evidence.keys(), key=len)  # shortest first
    for i, short_key in enumerate(all_keys):
        short_words = set(short_key.split())
        if len(short_words) < 2:
            continue  # Don't merge single-word keys into longer ones
        for long_key in all_keys[i + 1:]:
            long_words = set(long_key.split())
            # Merge if all words in short key appear in long key
            if short_words.issubset(long_words):
                keys_to_merge.append((short_key, long_key))
    for short_key, long_key in keys_to_merge:
        if short_key in deduped_evidence and long_key in deduped_evidence:
            merged = deduped_evidence[long_key]
            donor = deduped_evidence[short_key]
            merged['sources'].extend(donor['sources'])
            merged['in_label'] = merged['in_label'] or donor['in_label']
            merged['is_bbw'] = merged['is_bbw'] or donor['is_bbw']
            merged['trial_signal'] = merged['trial_signal'] or donor['trial_signal']
            merged['literature_count'] += donor['literature_count']
            merged['faers_count'] += donor['faers_count']
            merged['class_effect'] = merged['class_effect'] or donor['class_effect']
            merged['drugs_affected'].update(donor['drugs_affected'])
            merged['details'].extend(donor['details'])
            del deduped_evidence[short_key]

    # 7. Pairwise fuzzy dedup — catches typos between collected terms
    #    (e.g., "cardiac arrythmias" vs "cardiac arrhythmias" when neither is in FAERS)
    from difflib import SequenceMatcher
    fuzzy_merges = []
    all_dedup_keys = sorted(deduped_evidence.keys(), key=len)
    for i, key_a in enumerate(all_dedup_keys):
        if key_a not in deduped_evidence:
            continue
        for key_b in all_dedup_keys[i + 1:]:
            if key_b not in deduped_evidence:
                continue
            if abs(len(key_a) - len(key_b)) > 3:
                continue  # Skip pairs with very different lengths
            ratio = SequenceMatcher(None, key_a, key_b).ratio()
            if ratio >= 0.85:
                fuzzy_merges.append((key_a, key_b))
    for shorter, longer in fuzzy_merges:
        if shorter in deduped_evidence and longer in deduped_evidence:
            merged = deduped_evidence[longer]
            donor = deduped_evidence[shorter]
            merged['sources'].extend(donor['sources'])
            merged['in_label'] = merged['in_label'] or donor['in_label']
            merged['is_bbw'] = merged['is_bbw'] or donor['is_bbw']
            merged['trial_signal'] = merged['trial_signal'] or donor['trial_signal']
            merged['literature_count'] += donor['literature_count']
            merged['faers_count'] += donor['faers_count']
            merged['class_effect'] = merged['class_effect'] or donor['class_effect']
            merged['drugs_affected'].update(donor['drugs_affected'])
            merged['details'].extend(donor['details'])
            del deduped_evidence[shorter]

    # Build scored risk entries
    risks = []
    for canonical_key, evidence in deduped_evidence.items():
        event_name = evidence.get('display_name', canonical_key)
        if not event_name or len(event_name) < 3:
            continue

        # Get label section for this event (for severity scoring)
        label_section = section_origins.get(event_name.lower())
        if not label_section and evidence['is_bbw']:
            label_section = 'boxed_warning'
        elif not label_section and evidence['in_label']:
            label_section = 'adverse_reactions'  # conservative default

        severity = _get_severity_score(event_name, label_section)
        evidence_score = _get_evidence_score(
            in_label=evidence['in_label'],
            is_bbw=evidence['is_bbw'],
            trial_signal=evidence['trial_signal'],
            literature_count=evidence['literature_count'],
            faers_count=evidence['faers_count'],
            class_effect=evidence['class_effect'],
        )
        reversibility = _get_reversibility_score(event_name, label_section)
        monitorability = _get_monitorability_score(event_name)
        overall = calculate_overall_score(severity, evidence_score, reversibility, monitorability)
        tier = classify_tier(overall)

        risks.append({
            'event': event_name.title(),
            'severity': round(severity, 2),
            'evidence': round(evidence_score, 2),
            'reversibility': round(reversibility, 2),
            'monitorability': round(monitorability, 2),
            'overall_score': overall,
            'tier': tier,
            'is_class_effect': evidence['class_effect'],
            'is_bbw': evidence['is_bbw'],
            'sources': list(set(evidence['sources'])),
            'drugs_affected': sorted(evidence['drugs_affected']),
            'monitoring': _get_monitoring_recommendation(event_name, tier, monitoring_recs),
        })

    risks.sort(key=lambda x: -x['overall_score'])

    high_risks = [r for r in risks if r['tier'] == 'HIGH']
    moderate_risks = [r for r in risks if r['tier'] == 'MODERATE']
    low_risks = [r for r in risks if r['tier'] == 'LOW']

    recommendations = []
    for risk in high_risks[:5]:
        recommendations.append({
            'event': risk['event'],
            'tier': risk['tier'],
            'action': risk['monitoring'],
            'rationale': f"Score {risk['overall_score']:.2f} — "
                        f"{'BBW' if risk['is_bbw'] else 'labeled'}, "
                        f"{'class effect' if risk['is_class_effect'] else 'drug-specific'}",
        })

    return {
        'risks': risks,
        'summary': {
            'total_risks_identified': len(risks),
            'high_risk_count': len(high_risks),
            'moderate_risk_count': len(moderate_risks),
            'low_risk_count': len(low_risks),
            'class_effects_count': sum(1 for r in risks if r['is_class_effect']),
            'bbw_count': sum(1 for r in risks if r['is_bbw']),
        },
        'recommendations': recommendations,
        'high_risks': high_risks,
        'moderate_risks': moderate_risks,
        'low_risks': low_risks,
    }
