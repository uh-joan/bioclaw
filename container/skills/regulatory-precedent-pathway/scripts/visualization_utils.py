#!/usr/bin/env python3
"""
Visualization utilities for regulatory precedent & pathway analysis.

Generates ASCII report with:
- Precedent table (or no-precedent benchmark matrix)
- Pathway comparison
- Designation eligibility checklist
- Pediatric obligations
- Source provenance
"""

from datetime import datetime
from typing import Dict, Any, List

from regulatory_constants import REPORT_SEPARATOR, SECTION_SEPARATOR, ASCII_TABLE_WIDTH

# Acronyms that should NOT be title-cased (preserve original casing)
_ACRONYM_PRESERVES = {
    'glp-1', 'rna', 'dna', 'mrna', 'sirna', 'mirna', 'aso', 'adc',
    'car-t', 'nsclc', 'sclc', 'hcc', 'cll', 'aml', 'all', 'dlbcl',
    'egfr', 'her2', 'pd-1', 'pd-l1', 'vegf', 'ctla-4', 'btk', 'jak',
    'attr', 'mash', 'nash', 'copd', 'ckd', 'hiv', 'hcv', 'hbv',
}


def _smart_title(text: str) -> str:
    """Title-case text while preserving known acronyms."""
    if not text:
        return text
    words = text.split()
    result = []
    for word in words:
        if word.lower() in _ACRONYM_PRESERVES:
            result.append(word.upper() if word.lower() == word else word)
        else:
            result.append(word.title() if word == word.lower() or word == word.upper() else word)
    return ' '.join(result)


def generate_report(result: Dict[str, Any]) -> str:
    """Generate full ASCII report from analysis results."""
    lines = []

    # Handle error mode (e.g., empty indication)
    if result.get('mode') == 'error':
        return result.get('error', 'An error occurred.')

    indication = result.get('indication', 'Unknown')
    modality = result.get('modality', 'Not specified')
    regions = result.get('target_regions', ['US', 'EU'])
    mode = result.get('mode', 'precedent')
    date_str = datetime.now().strftime('%Y-%m-%d')

    # Header
    lines.append(REPORT_SEPARATOR)
    lines.append(f"REGULATORY PRECEDENT & PATHWAY ANALYSIS: {indication.upper()}")
    lines.append(f"Modality: {_smart_title(modality)} | Regions: {', '.join(regions)} | Date: {date_str}")
    lines.append(REPORT_SEPARATOR)
    lines.append("")

    # Section 1: Precedents or Benchmarks
    if mode == 'precedent':
        lines.extend(_render_precedents(result.get('precedent_data', {})))
    else:
        lines.extend(_render_benchmarks(result.get('benchmark_data', {})))

    # Section 1.5: Patent Landscape
    patent_data = result.get('patent_data', {})
    if patent_data and patent_data.get('drug_patents'):
        lines.extend(_render_patent_landscape(patent_data))

    # Section 2: Pathway Analysis
    pathways = result.get('pathway_data', {})
    if pathways:
        lines.extend(_render_pathways(pathways, regions))

    # Section 3: Designations
    designation_data = result.get('designation_data', {})
    if designation_data:
        lines.extend(_render_designations(designation_data))

    # Section 4: Pediatric
    pediatric = designation_data.get('pediatric', {})
    if pediatric:
        lines.extend(_render_pediatric(pediatric))

    # Section 5: Companion Diagnostic
    cdx = designation_data.get('companion_diagnostic', {})
    if cdx:
        lines.extend(_render_cdx(cdx))

    # Sources
    lines.extend(_render_sources(result))

    lines.append(REPORT_SEPARATOR)
    return '\n'.join(lines)


def _render_precedents(prec_data: Dict[str, Any]) -> List[str]:
    """Render precedent drugs table."""
    lines = []
    precedents = prec_data.get('precedents', [])
    unique_count = prec_data.get('unique_drug_count', 0)

    lines.append(f"REGULATORY PRECEDENTS ({unique_count} unique drugs found)")
    lines.append(SECTION_SEPARATOR)

    if not precedents:
        lines.append("No approved precedents found.")
        lines.append("")
        return lines

    # Table header
    lines.append(f"{'Drug':<30} {'Region':<8} {'Pathway':<15} {'App #':<15} {'Pivotal Trial'}")
    lines.append(SECTION_SEPARATOR)

    for p in precedents:
        drug = (p.get('brand_name') or p.get('drug_name', ''))[:28]
        region = p.get('region', '?')
        pathway = (p.get('approval_pathway') or 'Unknown')[:13]
        app_num = (p.get('application_number') or 'N/A')[:13]

        trial = p.get('pivotal_trial')
        trial_str = ''
        if trial:
            nct = trial.get('nct_id', '')
            enrollment = trial.get('enrollment', 0)
            trial_str = f"{nct} ({enrollment} pts)" if nct else ''

        lines.append(f"{drug:<30} {region:<8} {pathway:<15} {app_num:<15} {trial_str}")

    lines.append("")
    return lines


def _render_benchmarks(bench_data: Dict[str, Any]) -> List[str]:
    """Render no-precedent trial benchmarks."""
    lines = []
    benchmarks = bench_data.get('trial_benchmarks', [])
    total = bench_data.get('total_found', 0)

    lines.append(f"NO-PRECEDENT MODE: ACTIVE TRIAL BENCHMARKS ({total} found)")
    lines.append(SECTION_SEPARATOR)
    lines.append("NOTE: These are active trials, NOT approved precedents. Use as design benchmarks.")
    lines.append("")

    if not benchmarks:
        lines.append("No active Phase 2/3 trials found.")
        lines.append("")
        return lines

    lines.append(f"{'NCT ID':<14} {'Phase':<10} {'Enrollment':<12} {'Sponsor':<30} {'Status'}")
    lines.append(SECTION_SEPARATOR)

    for b in benchmarks:
        nct = b.get('nct_id', 'N/A')
        phase = b.get('phase', '?')
        enrollment = str(b.get('enrollment', '?'))
        sponsor = (b.get('sponsor') or 'Unknown')[:28]
        status = b.get('status', '?')

        lines.append(f"{nct:<14} {phase:<10} {enrollment:<12} {sponsor:<30} {status}")

    # Design patterns
    patterns = bench_data.get('design_patterns', {})
    if patterns:
        lines.append("")
        lines.append("Design Patterns Observed:")
        phase_dist = patterns.get('phase_distribution', {})
        if phase_dist:
            dist_str = ', '.join(f"{k}: {v}" for k, v in phase_dist.items())
            lines.append(f"  Phase distribution: {dist_str}")
        avg_enroll = patterns.get('average_enrollment', 0)
        if avg_enroll:
            lines.append(f"  Average enrollment: {avg_enroll}")

    lines.append("")
    return lines


def _render_patent_landscape(patent_data: Dict[str, Any]) -> List[str]:
    """Render compact patent & exclusivity landscape from FDA Orange Book."""
    lines = []
    drug_patents = patent_data.get('drug_patents', [])
    active_pat = patent_data.get('active_patent_count', 0)
    total_scanned = patent_data.get('total_scanned', 0)

    if not drug_patents:
        return lines

    lines.append(f"PATENT & EXCLUSIVITY LANDSCAPE ({active_pat} ingredients with active protection, {total_scanned} NDAs scanned)")
    lines.append(SECTION_SEPARATOR)
    lines.append("Source: FDA Orange Book (US NDAs only — BLAs/EU not covered)")
    lines.append("")

    # Compact table header
    lines.append(f"{'Ingredient':<25} {'Brands':<20} {'Patents':<10} {'Latest Expiry':<18} {'Exclusivity'}")
    lines.append(SECTION_SEPARATOR)

    for dp in drug_patents:
        ingredient = (dp.get('ingredient') or '?')[:23]
        trade_names = dp.get('trade_names', [])
        brands = ', '.join(trade_names[:3])[:18] if trade_names else '-'
        patent_count = str(dp.get('patent_count', 0))
        latest = dp.get('latest_expiry', '-')

        # Compact exclusivity: show most important one
        exclusivities = dp.get('exclusivities', [])
        if exclusivities:
            exc = exclusivities[0]
            excl_str = f"{exc.get('description', exc.get('code', '?'))} ({exc.get('expires', '?')})"
            if len(exclusivities) > 1:
                excl_str += f" +{len(exclusivities)-1}"
        else:
            excl_str = '-'

        lines.append(f"{ingredient:<25} {brands:<20} {patent_count:<10} {latest:<18} {excl_str}")

        # Show key patent link on next line (substance patent preferred)
        key_pat = dp.get('key_patent')
        if key_pat:
            pat_type = 'substance' if key_pat.get('substance') else 'product'
            lines.append(f"  {'':>23} Key patent: US{key_pat['patent_no']} ({pat_type}) {key_pat.get('url', '')}")

    lines.append("")
    return lines


def _render_pathways(pathway_data: Dict[str, Any], regions: List[str]) -> List[str]:
    """Render pathway comparison."""
    lines = []
    lines.append("SUBMISSION PATHWAY OPTIONS")
    lines.append(SECTION_SEPARATOR)

    for region in regions:
        key = f"{'us' if region == 'US' else 'eu'}_pathways"
        pathways = pathway_data.get(key, [])
        if not pathways:
            continue

        lines.append(f"\n  {region}:")
        for p in pathways:
            name = p.get('full_name', p.get('code', '?'))
            recommended = " [RECOMMENDED]" if p.get('recommended') else ""
            rationale = p.get('rationale', '')
            precedent_support = p.get('precedent_support', '')

            lines.append(f"    {name}{recommended}")
            if rationale:
                lines.append(f"      Rationale: {rationale}")
            if precedent_support:
                lines.append(f"      Precedent: {precedent_support}")

            pros = p.get('pros', [])
            cons = p.get('cons', [])
            if pros:
                lines.append(f"      Pros: {'; '.join(pros)}")
            if cons:
                lines.append(f"      Cons: {'; '.join(cons)}")

    lines.append("")
    return lines


def _render_designations(designation_data: Dict[str, Any]) -> List[str]:
    """Render designation eligibility checklist."""
    lines = []
    designations = designation_data.get('designations', {})
    if not designations:
        return lines

    lines.append("DESIGNATIONS & ACCELERATORS")
    lines.append(SECTION_SEPARATOR)
    lines.append(f"{'Designation':<35} {'Signal':<18} {'Rationale'}")
    lines.append(SECTION_SEPARATOR)

    signal_icons = {
        'STRONG': 'STRONG',
        'MODERATE': 'MODERATE',
        'WEAK': 'WEAK',
        'NOT_APPLICABLE': 'N/A',
    }

    for key, info in designations.items():
        name = info.get('full_name', key)[:33]
        signal = signal_icons.get(info.get('eligibility_signal', ''), '?')
        rationale = info.get('rationale', '')[:100]
        lines.append(f"{name:<35} {signal:<18} {rationale}")

    lines.append("")
    return lines


def _render_pediatric(pediatric: Dict[str, Any]) -> List[str]:
    """Render pediatric obligations."""
    lines = []
    if not pediatric:
        return lines

    lines.append("PEDIATRIC OBLIGATIONS")
    lines.append(SECTION_SEPARATOR)

    prea = pediatric.get('us_prea', {})
    if prea:
        status = prea.get('status', '?')
        rationale = prea.get('rationale', '')
        lines.append(f"  US (PREA): {status} - {rationale}")

    pip = pediatric.get('eu_pip', {})
    if pip:
        status = pip.get('status', '?')
        rationale = pip.get('rationale', '')
        lines.append(f"  EU (PIP):  {status} - {rationale}")

    lines.append("")
    return lines


def _render_cdx(cdx: Dict[str, Any]) -> List[str]:
    """Render companion diagnostic assessment."""
    lines = []
    if not cdx:
        return lines

    required = cdx.get('required', False)
    rationale = cdx.get('rationale', '')

    lines.append("COMPANION DIAGNOSTIC")
    lines.append(SECTION_SEPARATOR)
    lines.append(f"  Required: {'Yes' if required else 'No'}")
    lines.append(f"  {rationale}")

    rec = cdx.get('recommendation')
    if rec:
        lines.append(f"  Recommendation: {rec}")

    lines.append("")
    return lines


def _render_sources(result: Dict[str, Any]) -> List[str]:
    """Render source provenance."""
    lines = []
    lines.append("SOURCES & PROVENANCE")
    lines.append(SECTION_SEPARATOR)

    all_sources = set()

    for key in ['precedent_data', 'benchmark_data', 'designation_data', 'patent_data']:
        data = result.get(key, {})
        for src in data.get('sources', []):
            all_sources.add(src)

    for src in sorted(all_sources):
        lines.append(f"  * {src}")

    lines.append(f"  * Analysis date: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("")
    return lines
