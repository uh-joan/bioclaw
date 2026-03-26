"""Visualization and display utilities for drug pipeline analysis."""
import re
import sys
import os

# Add script directory to path for local imports
_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _script_dir)

from brand_lookup import (
    get_drug_base_name,
    get_generic_name,
)


def clean_drug_for_regulatory_display(name: str) -> str:
    """Extract clean drug name for regulatory status display.

    Simpler cleaning than the global clean_drug_name_for_display() -
    just strips doses and formulations for FDA/EMA approved drug display.

    Handles patterns like:
    - "Cladribine Subcutaneous Injection" -> "Cladribine"
    - "Tyruko Injectable Product" -> "Tyruko"
    - "Riluzole (100 mg)" -> "Riluzole"
    - "Lithium Carbonate 400 MG" -> "Lithium Carbonate"
    """
    # Skip obvious non-drug entries
    skip_patterns = [
        r'^optional',
        r'^rescue',
        r'^placebo',
        r'^vehicle',
        r'^saline',
        r'^standard',
    ]
    name_lower = name.lower()
    for pattern in skip_patterns:
        if re.match(pattern, name_lower):
            return None

    # Remove parenthetical content (doses, concentrations)
    # e.g., "Riluzole (100 mg)" -> "Riluzole"
    # e.g., "Masitinib (4.5)" -> "Masitinib"
    cleaned = re.sub(r'\s*\([^)]*\)\s*$', '', name).strip()

    # Remove trailing dose patterns (including mid-string)
    # e.g., "Lithium Carbonate 400 MG" -> "Lithium Carbonate"
    # e.g., "Darifenacin 7.5 MG Extended Release" -> "Darifenacin"
    cleaned = re.sub(r'\s+\d+(\.\d+)?\s*(mg|mg/ml|ml|mcg|g|iu|units?|bid|tid|qd)\b.*$', '', cleaned, flags=re.IGNORECASE).strip()

    # Remove multi-word dosage form phrases (order matters - longest first)
    # e.g., "Cladribine Subcutaneous Injection" -> "Cladribine"
    # e.g., "Tyruko Injectable Product" -> "Tyruko"
    multi_word_forms = [
        r'\s+Injectable\s+Product\s*$',
        r'\s+Subcutaneous\s+Injection\s*$',
        r'\s+Intramuscular\s+Injection\s*$',
        r'\s+Intravenous\s+Injection\s*$',
        r'\s+Intravenous\s+Infusion\s*$',
        r'\s+Oral\s+Solution\s*$',
        r'\s+Oral\s+Suspension\s*$',
        r'\s+Oral\s+Tablet\s*$',
        r'\s+Oral\s+Capsule\s*$',
        r'\s+Extended\s+Release\s*$',
        r'\s+Immediate\s+Release\s*$',
        r'\s+Delayed\s+Release\s*$',
        r'\s+Controlled\s+Release\s*$',
        r'\s+Reference\s+Formulation\s*$',
        r'\s+Test\s+Formulation\s*$',
        r'\s+For\s+Injection\s*$',
        r'\s+For\s+Infusion\s*$',
    ]
    for pattern in multi_word_forms:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE).strip()

    # Remove single-word dosage forms at end
    # e.g., "Drug Injection" -> "Drug"
    cleaned = re.sub(r'\s+(Injection|Injectable|Solution|Tablet|Capsule|Suspension|Infusion|Product|Formulation)s?\s*$', '', cleaned, flags=re.IGNORECASE).strip()

    return cleaned if cleaned else None


def dedupe_and_normalize_drugs(drug_list: list) -> list:
    """Clean drug names, normalize to generic via PubChem, and deduplicate.

    Uses base name matching to catch duplicates like:
    - "Cladribine Subcutaneous Injection" vs "Cladribine" (same drug, different formulation)
    - "Fingolimod Hydrochloride" vs "Fingolimod" (same drug, salt form)
    """
    seen_exact = set()  # Exact lowercase matches
    seen_base = set()   # Base name matches (strips salt/formulation)
    result = []
    for d in drug_list:
        # First clean obvious noise
        cleaned = clean_drug_for_regulatory_display(d)
        if not cleaned:
            continue

        # Now normalize to generic name via PubChem
        generic = get_generic_name(cleaned)

        key_exact = generic.lower()
        key_base = get_drug_base_name(generic)

        # Skip if we've seen this exact name OR its base name
        if key_exact in seen_exact or key_base in seen_base:
            continue

        seen_exact.add(key_exact)
        seen_base.add(key_base)
        result.append(generic)
    return result


def dedupe_by_base_name(drug_dict: dict) -> list:
    """Normalize and dedupe drug names using base name matching."""
    seen_base = set()
    result = []
    for drug in drug_dict.keys():
        generic = get_generic_name(drug)
        base = get_drug_base_name(generic)
        if base not in seen_base:
            seen_base.add(base)
            result.append(generic)
    return result


def normalize_brand_case(brand: str) -> str:
    """Normalize brand name to Title Case for consistent display.

    FDA uses UPPERCASE (VYVGART), EMA uses Title Case (Vyvgart).
    Standardize to Title Case for cleaner table display.
    """
    if not brand:
        return None
    # Handle special cases like "BRIUMVI" -> "Briumvi"
    # But preserve intentional mixed case like "mRNA" or "CAR-T"
    if brand.isupper():
        return brand.title()
    return brand


def build_regulatory_data(
    fda_approved: set,
    ema_approved: set,
    fda_brand_map: dict,
    ema_brand_map: dict,
    fda_in_trials_lower: set,
    fda_in_trials_base: set,
    ema_in_trials_lower: set,
    ema_in_trials_base: set,
) -> dict:
    """Build structured regulatory data for HTML template rendering.

    Returns:
        dict with 'drugs' list and 'summary' counts
    """
    all_drugs = fda_approved | ema_approved

    if not all_drugs:
        return {'drugs': [], 'summary': {'fda': 0, 'ema': 0, 'both': 0, 'in_trials': 0}}

    both_approved = []
    fda_only = []
    ema_only = []

    for drug in all_drugs:
        drug_lower = drug.lower()
        drug_base = get_drug_base_name(drug)

        in_fda = drug in fda_approved
        in_ema = drug in ema_approved

        fda_brand = normalize_brand_case(fda_brand_map.get(drug_lower))
        ema_brand = normalize_brand_case(ema_brand_map.get(drug_lower))

        in_trials = (
            drug_lower in fda_in_trials_lower or
            drug_base in fda_in_trials_base or
            drug_lower in ema_in_trials_lower or
            drug_base in ema_in_trials_base
        )

        entry = {
            'drug': drug,
            'fda_brand': fda_brand if in_fda else None,
            'ema_brand': ema_brand if in_ema else None,
            'in_fda': in_fda,
            'in_ema': in_ema,
            'in_trials': in_trials
        }

        if in_fda and in_ema:
            both_approved.append(entry)
        elif in_fda:
            fda_only.append(entry)
        else:
            ema_only.append(entry)

    # Sort each category
    both_approved.sort(key=lambda x: x['drug'].lower())
    fda_only.sort(key=lambda x: x['drug'].lower())
    ema_only.sort(key=lambda x: x['drug'].lower())

    # Combine in order: both first, then FDA-only, then EMA-only
    all_entries = both_approved + fda_only + ema_only

    trials_count = sum(1 for e in all_entries if e['in_trials'])

    return {
        'drugs': all_entries,
        'summary': {
            'fda': len(fda_approved),
            'ema': len(ema_approved),
            'both': len(both_approved),
            'in_trials': trials_count
        }
    }


def _is_drug_approved(drug: str, approved_lower: set, approved_base: set) -> bool:
    """Check if a drug is in the approved sets."""
    return drug.lower() in approved_lower or get_drug_base_name(drug) in approved_base


def build_pipeline_highlights(
    phase_breakdown: dict,
    fda_approved: set,
    ema_approved: set,
    max_drugs_per_phase: int = 8,
) -> dict:
    """Build comprehensive pipeline analysis with multiple views.

    Returns:
        dict with:
        - 'novel_by_phase': Unapproved drugs grouped by phase (Phase 3 highlighted)
        - 'phase3_focus': Phase 3 drugs split by novel vs approved-elsewhere
        - 'repurposed': Approved drugs being tested for new indication
        - 'drug_journeys': Drugs appearing in multiple phases
        - 'summary': Overall stats
    """
    # Build approved drug sets for matching
    approved_lower = {d.lower() for d in fda_approved | ema_approved}
    approved_base = {get_drug_base_name(d) for d in fda_approved | ema_approved}

    # Track drugs across phases for journey analysis
    drug_to_phases = {}  # {drug_base: {phases}}
    all_phase_drugs = {}  # {phase: {drugs}}

    for phase_name in ['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4']:
        phase_data = phase_breakdown.get(phase_name, {})
        drugs = phase_data.get('drugs', [])
        all_phase_drugs[phase_name] = set(drugs)

        for drug in drugs:
            base = get_drug_base_name(drug)
            if base not in drug_to_phases:
                drug_to_phases[base] = {'phases': set(), 'name': drug}
            drug_to_phases[base]['phases'].add(phase_name)

    # 1. Novel drugs by phase (existing functionality, enhanced)
    novel_by_phase = []
    total_novel = 0

    for phase_name in ['Phase 3', 'Phase 2', 'Phase 1', 'Phase 4']:
        all_drugs = list(all_phase_drugs.get(phase_name, []))
        novel_drugs = [d for d in all_drugs if not _is_drug_approved(d, approved_lower, approved_base)]
        novel_drugs_sorted = sorted(novel_drugs, key=str.lower)[:max_drugs_per_phase]
        total_in_phase = len(novel_drugs)

        if novel_drugs_sorted:
            novel_by_phase.append({
                'phase': phase_name,
                'drugs': novel_drugs_sorted,
                'total_novel': total_in_phase,
                'is_late_stage': phase_name == 'Phase 3',
            })
            total_novel += total_in_phase

    # 2. Phase 3 Focus: Novel vs Approved-Elsewhere
    phase3_drugs = list(all_phase_drugs.get('Phase 3', []))
    phase3_novel = []
    phase3_repurposed = []

    for drug in phase3_drugs:
        if _is_drug_approved(drug, approved_lower, approved_base):
            phase3_repurposed.append(drug)
        else:
            phase3_novel.append(drug)

    phase3_focus = {
        'novel': sorted(phase3_novel, key=str.lower),
        'repurposed': sorted(phase3_repurposed, key=str.lower),
        'total_novel': len(phase3_novel),
        'total_repurposed': len(phase3_repurposed),
    }

    # 3. Repurposed drugs (approved elsewhere, being tested here)
    repurposed_drugs = []
    for phase_name in ['Phase 3', 'Phase 2', 'Phase 1', 'Phase 4']:
        for drug in all_phase_drugs.get(phase_name, []):
            if _is_drug_approved(drug, approved_lower, approved_base):
                base = get_drug_base_name(drug)
                # Avoid duplicates
                if not any(get_drug_base_name(d['drug']) == base for d in repurposed_drugs):
                    # Find highest phase this drug is in
                    highest_phase = phase_name
                    for p in ['Phase 4', 'Phase 3', 'Phase 2', 'Phase 1']:
                        if any(get_drug_base_name(d) == base for d in all_phase_drugs.get(p, [])):
                            highest_phase = p
                            break
                    repurposed_drugs.append({
                        'drug': drug,
                        'highest_phase': highest_phase,
                    })

    # Sort repurposed by phase (Phase 3 first)
    phase_order = {'Phase 3': 0, 'Phase 2': 1, 'Phase 4': 2, 'Phase 1': 3}
    repurposed_drugs.sort(key=lambda x: (phase_order.get(x['highest_phase'], 9), x['drug'].lower()))

    # 4. Drug Journeys (drugs in multiple phases)
    drug_journeys = []
    for base, info in drug_to_phases.items():
        if len(info['phases']) >= 2:
            # Sort phases in order
            phases_ordered = sorted(info['phases'], key=lambda p: int(p.split()[1]))
            drug_journeys.append({
                'drug': info['name'],
                'phases': phases_ordered,
                'phase_count': len(info['phases']),
                'is_approved': _is_drug_approved(info['name'], approved_lower, approved_base),
            })

    # Sort by phase count (most phases first), then by name
    drug_journeys.sort(key=lambda x: (-x['phase_count'], x['drug'].lower()))

    return {
        'novel_by_phase': novel_by_phase,
        'phase3_focus': phase3_focus,
        'repurposed': repurposed_drugs[:10],  # Top 10
        'drug_journeys': drug_journeys[:10],  # Top 10
        'summary': {
            'total_novel': total_novel,
            'phase3_novel': phase3_focus['total_novel'],
            'phase3_repurposed': phase3_focus['total_repurposed'],
            'total_repurposed': len(repurposed_drugs),
            'drugs_multi_phase': len(drug_journeys),
        }
    }
