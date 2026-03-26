"""Visualization utilities for drug safety intelligence reports.

Generates ASCII tables, risk matrix displays, and formatted summaries.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


def _truncate(text: str, max_len: int) -> str:
    """Truncate text with ellipsis."""
    if not text:
        return ''
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + '...'


def _tier_indicator(tier: str) -> str:
    """Get ASCII indicator for risk tier."""
    if tier == 'HIGH':
        return '[!!!]'
    elif tier == 'MODERATE':
        return '[ ! ]'
    return '[ . ]'


def _bar(value: float, width: int = 10) -> str:
    """Create ASCII bar for 0-1 value."""
    filled = int(value * width)
    return '#' * filled + '-' * (width - filled)


def generate_risk_matrix_table(risk_matrix: Dict) -> str:
    """Generate ASCII risk matrix table."""
    lines = []
    lines.append("RISK MATRIX (4-Dimensional Scoring)")
    lines.append("=" * 100)
    lines.append(f"{'Risk':<30} {'Tier':<8} {'Score':<7} {'Sev':<6} {'Evid':<6} {'Rev':<6} {'Mon':<6} {'Class?':<7}")
    lines.append("-" * 100)

    risks = risk_matrix.get('risks', [])
    for risk in risks[:20]:  # Top 20 risks
        event = _truncate(risk['event'], 28)
        tier = risk['tier']
        indicator = _tier_indicator(tier)
        score = f"{risk['overall_score']:.2f}"
        sev = f"{risk['severity']:.1f}"
        evid = f"{risk['evidence']:.1f}"
        rev = f"{risk['reversibility']:.1f}"
        mon = f"{risk['monitorability']:.1f}"
        class_flag = 'CLASS' if risk.get('is_class_effect') else ''
        bbw_flag = 'BBW' if risk.get('is_bbw') else ''
        flags = f"{bbw_flag} {class_flag}".strip()

        lines.append(f"{event:<30} {indicator:<8} {score:<7} {sev:<6} {evid:<6} {rev:<6} {mon:<6} {flags:<7}")

    lines.append("-" * 100)

    summary = risk_matrix.get('summary', {})
    lines.append(f"Total: {summary.get('total_risks_identified', 0)} risks | "
                 f"HIGH: {summary.get('high_risk_count', 0)} | "
                 f"MODERATE: {summary.get('moderate_risk_count', 0)} | "
                 f"LOW: {summary.get('low_risk_count', 0)} | "
                 f"Class Effects: {summary.get('class_effects_count', 0)} | "
                 f"BBW: {summary.get('bbw_count', 0)}")
    lines.append("")
    lines.append("Scoring: overall = 0.40*severity + 0.30*evidence + 0.20*(1-reversibility) + 0.10*(1-monitorability)")
    lines.append("Tiers: [!!!] >= 0.70 HIGH | [ ! ] >= 0.40 MODERATE | [ . ] < 0.40 LOW")

    return "\n".join(lines)


def generate_label_comparison_table(label_data: Dict) -> str:
    """Generate ASCII label comparison table."""
    lines = []
    lines.append("\nLABEL COMPARISON (FDA/EMA)")
    lines.append("=" * 100)

    # Drug-level summary
    drug_labels = label_data.get('drug_labels', [])
    if drug_labels:
        lines.append(f"{'Drug':<25} {'BBW?':<6} {'W&P Count':<10} {'AR Count':<10} {'FDA':<5} {'EMA':<5}")
        lines.append("-" * 70)
        for dl in drug_labels:
            name = _truncate(dl['drug_name'], 23)
            bbw = 'YES' if dl.get('has_bbw') else 'No'
            wp_count = str(len(dl.get('warnings_precautions', [])))
            ar_count = str(len(dl.get('adverse_reactions', [])))
            fda = 'Y' if dl.get('fda_found') else 'N'
            ema = 'Y' if dl.get('ema_found') else 'N'
            lines.append(f"{name:<25} {bbw:<6} {wp_count:<10} {ar_count:<10} {fda:<5} {ema:<5}")
        lines.append("")

    # Class effects
    class_effects = label_data.get('class_effects', [])
    if class_effects:
        lines.append("CLASS EFFECTS (present in >50% of drugs):")
        lines.append("-" * 70)
        for ce in class_effects:
            prevalence = ce.get('prevalence', '?')
            event = _truncate(ce['event'], 40)
            drugs = ', '.join(ce.get('drugs', [])[:5])
            lines.append(f"  [{prevalence}] {event}")
            if drugs:
                lines.append(f"          Drugs: {_truncate(drugs, 60)}")
        lines.append("")

    # Drug-specific outliers
    outliers = label_data.get('drug_specific_outliers', [])
    if outliers:
        lines.append("DRUG-SPECIFIC OUTLIERS (unique to one drug):")
        lines.append("-" * 70)
        for outlier in outliers[:10]:
            drug = outlier.get('drug', '')
            event = _truncate(outlier['event'], 50)
            lines.append(f"  {drug}: {event}")
        lines.append("")

    summary = label_data.get('summary', {})
    lines.append(f"Summary: {summary.get('total_drugs_analyzed', 0)} drugs analyzed | "
                 f"{summary.get('drugs_with_bbw', 0)} with BBW | "
                 f"{summary.get('class_effects_count', 0)} class effects | "
                 f"{summary.get('drug_specific_outliers_count', 0)} drug-specific signals")

    return "\n".join(lines)


def generate_trial_signals_table(trial_data: Dict) -> str:
    """Generate ASCII trial safety signals table."""
    lines = []
    lines.append("\nTRIAL SAFETY SIGNALS (Terminated/Suspended)")
    lines.append("=" * 100)

    # Safety signals
    signals = trial_data.get('safety_signals', [])
    if signals:
        lines.append(f"{'NCT ID':<15} {'Phase':<10} {'Status':<12} {'Category':<18} {'Reason':<45}")
        lines.append("-" * 100)
        for signal in signals[:15]:
            nct = signal.get('nct_id', '')[:14]
            phase = signal.get('phase', '')[:9]
            status = signal.get('status', '')[:11]
            category = signal.get('reason_category', '')[:17]
            reason = _truncate(signal.get('reason', ''), 43)
            lines.append(f"{nct:<15} {phase:<10} {status:<12} {category:<18} {reason:<45}")
        lines.append("")

    # Reason breakdown
    reason_breakdown = trial_data.get('reason_breakdown', {})
    if reason_breakdown:
        lines.append("TERMINATION REASON BREAKDOWN:")
        lines.append("-" * 50)
        for reason, count in sorted(reason_breakdown.items(), key=lambda x: -x[1]):
            if count > 0:
                max_count = max(reason_breakdown.values()) if reason_breakdown else 1
                bar = _bar(count / max(max_count, 1), 15)
                lines.append(f"  {reason:<20} {count:>3} {bar}")
        lines.append("")

    summary = trial_data.get('summary', {})
    lines.append(f"Summary: {summary.get('total_terminated', 0)} terminated | "
                 f"{summary.get('total_suspended', 0)} suspended | "
                 f"{summary.get('safety_related', 0)} safety-related")

    return "\n".join(lines)


def generate_interaction_summary(interaction_data: Dict) -> str:
    """Generate ASCII interaction summary."""
    lines = []
    lines.append("\nDRUG-DRUG INTERACTIONS")
    lines.append("=" * 100)

    summary = interaction_data.get('summary', {})
    lines.append(f"Drugs analyzed: {summary.get('drugs_analyzed', 0)} | "
                 f"Total DDIs: {summary.get('total_interactions', 0)} | "
                 f"Polypharmacy risk: {summary.get('polypharmacy_risk', 'N/A')}")
    lines.append("")

    # Severity breakdown
    lines.append(f"  Major:    {summary.get('major_interactions', 0)}")
    lines.append(f"  Moderate: {summary.get('moderate_interactions', 0)}")
    lines.append(f"  Minor:    {summary.get('minor_interactions', 0)}")
    lines.append("")

    # Top major interactions
    interactions = interaction_data.get('interactions', [])
    major = [i for i in interactions if i['severity'] == 'major']
    if major:
        lines.append("TOP MAJOR INTERACTIONS:")
        lines.append("-" * 80)
        for item in major[:10]:
            source = _truncate(item.get('source_drug', ''), 15)
            target = _truncate(item.get('interacting_drug', ''), 20)
            desc = _truncate(item.get('description', ''), 40)
            lines.append(f"  {source} x {target}: {desc}")
        lines.append("")

    # CYP enzymes
    cyp_enzymes = interaction_data.get('cyp_enzymes', [])
    if cyp_enzymes:
        lines.append(f"CYP450 Enzymes Involved: {', '.join(cyp_enzymes)}")
        lines.append("")

    # Food interactions
    food = interaction_data.get('food_interactions', [])
    if food:
        lines.append(f"Food Interactions: {summary.get('food_interactions_count', 0)}")
        for f_item in food[:5]:
            drug = f_item.get('drug', '')
            interaction = _truncate(f_item.get('interaction', ''), 60)
            lines.append(f"  {drug}: {interaction}")

    return "\n".join(lines)


def generate_literature_summary(literature_data: Dict) -> str:
    """Generate ASCII literature summary."""
    lines = []
    lines.append("\nSAFETY LITERATURE")
    lines.append("=" * 100)

    summary = literature_data.get('summary', {})
    lines.append(f"PubMed: {summary.get('total_articles', 0)} articles | "
                 f"bioRxiv: {summary.get('total_preprints', 0)} preprints")
    lines.append("")

    # Publication type breakdown
    pub_types = literature_data.get('pub_type_breakdown', {})
    if pub_types:
        lines.append("PUBLICATION TYPES:")
        for pt, count in sorted(pub_types.items(), key=lambda x: -x[1]):
            label = pt.replace('_', ' ').title()
            lines.append(f"  {label:<25} {count}")
        lines.append("")

    # Top articles
    articles = literature_data.get('articles', [])
    if articles:
        lines.append("KEY PUBLICATIONS:")
        lines.append("-" * 80)
        for article in articles[:5]:
            title = _truncate(article.get('title', ''), 70)
            pmid = article.get('pmid', '')
            year = article.get('year', '')
            pt = article.get('pub_type', '').replace('_', ' ')
            lines.append(f"  [{pt}] {title}")
            if pmid:
                lines.append(f"    PMID: {pmid} ({year})")
        lines.append("")

    # Preprints
    preprints = literature_data.get('preprints', [])
    if preprints:
        lines.append("RECENT PREPRINTS (not peer-reviewed):")
        for pp in preprints[:3]:
            title = _truncate(pp.get('title', ''), 70)
            doi = pp.get('doi', '')
            lines.append(f"  {title}")
            if doi:
                lines.append(f"    DOI: {doi}")

    return "\n".join(lines)


def generate_recommendations_block(risk_matrix: Dict) -> str:
    """Generate monitoring recommendations block."""
    lines = []
    lines.append("\nMONITORING RECOMMENDATIONS")
    lines.append("=" * 100)

    recommendations = risk_matrix.get('recommendations', [])
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            event = rec.get('event', '')
            tier = rec.get('tier', '')
            action = rec.get('action', '')
            rationale = rec.get('rationale', '')
            lines.append(f"\n  {i}. {event} [{tier}]")
            lines.append(f"     Action: {action}")
            lines.append(f"     Rationale: {rationale}")
    else:
        lines.append("  No high-risk events requiring specific monitoring recommendations.")

    return "\n".join(lines)


def generate_target_biology_section(target_biology: Dict) -> str:
    """Generate target biology section."""
    lines = []
    lines.append("\nTARGET BIOLOGY")
    lines.append("=" * 100)

    gene = target_biology.get('gene_symbol', 'Unknown')
    name = target_biology.get('target_name', 'Unknown')
    target_class = target_biology.get('target_class', 'Unknown')
    lines.append(f"Target: {gene} ({name}) | Class: {target_class}")
    lines.append("")

    # Organ toxicity map
    organ_map = target_biology.get('organ_toxicity_map', {})
    if organ_map:
        lines.append("PREDICTED ORGAN TOXICITY (from expression profile):")
        lines.append("-" * 50)
        for organ, data in sorted(organ_map.items()):
            tissues = ', '.join(data.get('tissues', [])[:3])
            risk = data.get('risk_level', 'monitor')
            lines.append(f"  {organ:<20} [{risk}] Tissues: {_truncate(tissues, 40)}")
        lines.append("")

    # KO phenotypes
    ko_phenotypes = target_biology.get('ko_phenotypes', [])
    if ko_phenotypes:
        lines.append("KNOCKOUT PHENOTYPES:")
        lines.append("-" * 50)
        for pheno in ko_phenotypes[:10]:
            severity = pheno.get('severity', 'unknown')
            phenotype = _truncate(pheno.get('phenotype', ''), 60)
            lines.append(f"  [{severity:<8}] {phenotype}")
        lines.append("")

    # Safety liabilities
    liabilities = target_biology.get('safety_liabilities', [])
    if liabilities:
        lines.append("KNOWN SAFETY LIABILITIES:")
        for lia in liabilities[:5]:
            lines.append(f"  - {_truncate(lia, 70)}")

    return "\n".join(lines)


def generate_full_report(
    input_summary: Dict,
    target_biology: Dict = None,
    label_data: Dict = None,
    trial_signals: Dict = None,
    literature_data: Dict = None,
    interaction_data: Dict = None,
    epidemiology_data: Dict = None,
    risk_matrix: Dict = None,
) -> str:
    """Generate the full ASCII safety intelligence report."""
    lines = []

    # Header
    query_desc = input_summary.get('query_description', 'Unknown')
    drug_count = len(input_summary.get('drug_names', []))
    date = datetime.now().strftime('%Y-%m-%d')

    lines.append("=" * 100)
    lines.append(f"DRUG SAFETY INTELLIGENCE REPORT")
    lines.append(f"Query: {query_desc} | Drugs: {drug_count} | Date: {date}")
    lines.append("=" * 100)

    # Drug list
    drugs = input_summary.get('drug_names', [])
    if drugs:
        lines.append(f"\nDrugs analyzed: {', '.join(drugs[:10])}")
        if len(drugs) > 10:
            lines.append(f"  ... and {len(drugs) - 10} more")
    lines.append("")

    # Risk Matrix (most important - goes first)
    if risk_matrix:
        lines.append(generate_risk_matrix_table(risk_matrix))
        lines.append("")

    # Target Biology
    if target_biology and not target_biology.get('error'):
        lines.append(generate_target_biology_section(target_biology))
        lines.append("")

    # Label Comparison
    if label_data:
        lines.append(generate_label_comparison_table(label_data))
        lines.append("")

    # Trial Signals
    if trial_signals:
        lines.append(generate_trial_signals_table(trial_signals))
        lines.append("")

    # Interactions
    if interaction_data:
        lines.append(generate_interaction_summary(interaction_data))
        lines.append("")

    # Literature
    if literature_data:
        lines.append(generate_literature_summary(literature_data))
        lines.append("")

    # Epidemiology
    if epidemiology_data:
        bg_rates = epidemiology_data.get('background_rates', [])
        if bg_rates:
            lines.append("\nEPIDEMIOLOGY CONTEXT (Background Rates)")
            lines.append("=" * 100)
            for rate in bg_rates:
                ae = rate.get('adverse_event', '')
                note = rate.get('background_note', '')
                lines.append(f"  {ae}: {note}")
            lines.append("")

    # Monitoring Recommendations
    if risk_matrix:
        lines.append(generate_recommendations_block(risk_matrix))
        lines.append("")

    # Provenance
    lines.append("\nDATA SOURCES & PROVENANCE")
    lines.append("=" * 100)
    sources = []
    if target_biology and not target_biology.get('error'):
        sources.append("OpenTargets (target biology, expression, KO phenotypes)")
    if label_data and label_data.get('summary', {}).get('drugs_with_fda_labels', 0) > 0:
        sources.append(f"FDA Labels ({label_data['summary']['drugs_with_fda_labels']} drugs)")
    if label_data and label_data.get('summary', {}).get('drugs_with_ema_data', 0) > 0:
        sources.append(f"EMA ({label_data['summary']['drugs_with_ema_data']} drugs)")
    if trial_signals and trial_signals.get('summary', {}).get('total_terminated', 0) > 0:
        sources.append(f"ClinicalTrials.gov ({trial_signals['summary']['total_terminated']} terminated trials)")
    if literature_data and literature_data.get('summary', {}).get('total_articles', 0) > 0:
        sources.append(f"PubMed ({literature_data['summary']['total_articles']} articles)")
    if literature_data and literature_data.get('summary', {}).get('total_preprints', 0) > 0:
        sources.append(f"bioRxiv ({literature_data['summary']['total_preprints']} preprints)")
    if interaction_data and interaction_data.get('summary', {}).get('total_interactions', 0) > 0:
        sources.append(f"DrugBank ({interaction_data['summary']['total_interactions']} DDIs)")
    if epidemiology_data and epidemiology_data.get('summary', {}).get('events_contextualized', 0) > 0:
        sources.append("CDC PLACES, WHO Global Health Observatory")

    for i, source in enumerate(sources, 1):
        lines.append(f"  {i}. {source}")

    lines.append("")
    lines.append("=" * 100)
    lines.append("Note: This report is for informational purposes. Always verify safety data against")
    lines.append("primary sources (prescribing information, regulatory documents, published literature).")
    lines.append("=" * 100)

    return "\n".join(lines)
