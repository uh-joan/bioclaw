"""Visualization utilities for disease burden analysis ASCII report."""

from typing import Dict, Any, List
from datetime import datetime


def _truncate(text: str, max_len: int) -> str:
    if not text:
        return ''
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + '...'


def _fmt_number(n, suffix='') -> str:
    """Format a number with K/M/B suffixes."""
    if n is None:
        return 'N/A'
    if isinstance(n, str):
        try:
            n = float(n)
        except ValueError:
            return n
    if abs(n) >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B{suffix}"
    if abs(n) >= 1_000_000:
        return f"{n / 1_000_000:.1f}M{suffix}"
    if abs(n) >= 1_000:
        return f"{n / 1_000:.1f}K{suffix}"
    if isinstance(n, float):
        return f"{n:.1f}{suffix}"
    return f"{n}{suffix}"


def _fmt_money(amount, prefix='$') -> str:
    """Format currency amount."""
    if amount is None:
        return 'N/A'
    if isinstance(amount, str):
        try:
            amount = float(amount)
        except ValueError:
            return amount
    if amount >= 1_000_000_000:
        return f"{prefix}{amount / 1_000_000_000:.1f}B"
    if amount >= 1_000_000:
        return f"{prefix}{amount / 1_000_000:.1f}M"
    if amount >= 1_000:
        return f"{prefix}{amount / 1_000:.1f}K"
    return f"{prefix}{amount:.2f}"


def _bar(pct, width=30) -> str:
    """Generate a percentage bar."""
    if pct is None:
        return '[N/A]'
    try:
        pct = float(pct)
    except (ValueError, TypeError):
        return '[N/A]'
    filled = int(width * min(pct, 100) / 100)
    return f"[{'#' * filled}{'.' * (width - filled)}] {pct:.1f}%"


def generate_report(data: Dict[str, Any]) -> str:
    """Generate complete ASCII disease burden report."""
    lines = []
    disease = data.get('disease', 'Unknown Disease')
    geography = data.get('geography', 'US')
    epi = data.get('epidemiology', {})
    demo = data.get('demographics', {})
    trends = data.get('trends', {})
    treatment = data.get('treatment_landscape', {})
    unmet = data.get('unmet_need', {})
    econ = data.get('economic_burden', {})
    global_comp = data.get('global_comparison', {})
    errors = data.get('errors', {})

    w = 80

    # === HEADER ===
    lines.append("=" * w)
    lines.append(f"  DISEASE BURDEN ANALYSIS: {disease.upper()}")
    lines.append(f"  Geography: {geography.upper()}")
    lines.append("=" * w)

    # === EPIDEMIOLOGY ===
    lines.append("")
    lines.append("EPIDEMIOLOGY")
    lines.append("-" * w)
    if epi.get('error') and not epi.get('prevalence'):
        lines.append(f"  [Data unavailable: {epi['error']}]")
    else:
        prevalence = epi.get('prevalence', {})
        incidence = epi.get('incidence', {})
        mortality = epi.get('mortality', {})

        if prevalence:
            val = prevalence.get('value', 'N/A')
            unit = prevalence.get('unit', '')
            source = prevalence.get('source', '')
            year = prevalence.get('year', '')
            year_str = f" ({year})" if year else ''
            lines.append(f"  Prevalence:    {val} {unit}{year_str}")
            if source:
                lines.append(f"                 Source: {source}")
        else:
            lines.append("  Prevalence:    N/A")

        if incidence:
            val = incidence.get('value', 'N/A')
            unit = incidence.get('unit', '')
            year = incidence.get('year', '')
            year_str = f" ({year})" if year else ''
            lines.append(f"  Incidence:     {val} {unit}{year_str}")
        else:
            lines.append("  Incidence:     N/A")

        if mortality:
            val = mortality.get('value', 'N/A')
            unit = mortality.get('unit', '')
            year = mortality.get('year', '')
            year_str = f" ({year})" if year else ''
            lines.append(f"  Mortality:     {val} {unit}{year_str}")
        else:
            lines.append("  Mortality:     N/A")

        dalys = epi.get('dalys', {})
        if dalys:
            val = dalys.get('value', 'N/A')
            unit = dalys.get('unit', '')
            lines.append(f"  DALYs:         {val} {unit}")

        extra_metrics = epi.get('additional_metrics', [])
        if extra_metrics:
            lines.append("")
            for m in extra_metrics[:5]:
                lines.append(f"  {m.get('label', 'Metric')}: {m.get('value', 'N/A')}")

    # === DEMOGRAPHICS ===
    lines.append("")
    lines.append("DEMOGRAPHICS")
    lines.append("-" * w)
    if demo.get('error') and not demo.get('age_distribution') and not demo.get('sex_distribution'):
        lines.append(f"  [Data unavailable: {demo['error']}]")
    else:
        age_dist = demo.get('age_distribution', [])
        sex_dist = demo.get('sex_distribution', [])
        race_dist = demo.get('race_distribution', [])
        risk_factors = demo.get('risk_factors', [])

        if age_dist:
            lines.append("  Age Distribution:")
            for entry in age_dist:
                label = entry.get('group', 'Unknown')
                pct = entry.get('percent')
                if pct is not None:
                    lines.append(f"    {label:<25} {_bar(pct)}")
                else:
                    val = entry.get('value', 'N/A')
                    lines.append(f"    {label:<25} {val}")

        if sex_dist:
            lines.append("")
            lines.append("  Sex Distribution:")
            for entry in sex_dist:
                label = entry.get('group', 'Unknown')
                pct = entry.get('percent')
                if pct is not None:
                    lines.append(f"    {label:<25} {_bar(pct)}")
                else:
                    val = entry.get('value', 'N/A')
                    lines.append(f"    {label:<25} {val}")

        if race_dist:
            lines.append("")
            lines.append("  Race/Ethnicity Distribution:")
            for entry in race_dist:
                label = entry.get('group', 'Unknown')
                pct = entry.get('percent')
                if pct is not None:
                    lines.append(f"    {label:<25} {_bar(pct, width=25)}")
                else:
                    val = entry.get('value', 'N/A')
                    lines.append(f"    {label:<25} {val}")

        income_dist = demo.get('income_distribution', [])
        if income_dist:
            lines.append("")
            lines.append("  Income Distribution:")
            for entry in income_dist:
                label = entry.get('group', 'Unknown')
                pct = entry.get('percent')
                if pct is not None:
                    lines.append(f"    {label:<25} {_bar(pct, width=25)}")
                else:
                    lines.append(f"    {label:<25} {entry.get('value', 'N/A')}")

        edu_dist = demo.get('education_distribution', [])
        if edu_dist:
            lines.append("")
            lines.append("  Education Distribution:")
            for entry in edu_dist:
                label = entry.get('group', 'Unknown')
                pct = entry.get('percent')
                if pct is not None:
                    lines.append(f"    {label:<25} {_bar(pct, width=25)}")
                else:
                    lines.append(f"    {label:<25} {entry.get('value', 'N/A')}")

        if risk_factors:
            lines.append("")
            lines.append("  Key Risk Factors:")
            for rf in risk_factors[:8]:
                if isinstance(rf, str):
                    lines.append(f"    - {rf}")
                elif isinstance(rf, dict):
                    lines.append(f"    - {rf.get('factor', 'Unknown')}: {rf.get('detail', '')}")

    # === TRENDS ===
    lines.append("")
    lines.append("TRENDS (5-10 Year)")
    lines.append("-" * w)
    if trends.get('error') and not trends.get('prevalence_trend') and not trends.get('mortality_trend'):
        lines.append(f"  [Data unavailable: {trends['error']}]")
    else:
        prev_trend = trends.get('prevalence_trend', [])
        mort_trend = trends.get('mortality_trend', [])
        summary = trends.get('summary', '')

        if prev_trend:
            lines.append("  Prevalence Trend:")
            lines.append(f"    {'Year':<8} {'Value':<15} {'Change'}")
            lines.append(f"    {'----':<8} {'-----':<15} {'------'}")
            for entry in prev_trend:
                year = entry.get('year', '?')
                val = entry.get('value', 'N/A')
                change = entry.get('change', '')
                change_str = f"  {change}" if change else ''
                lines.append(f"    {year:<8} {str(val):<15}{change_str}")

        if mort_trend:
            lines.append("")
            lines.append("  Mortality Trend:")
            lines.append(f"    {'Year':<8} {'Value':<15} {'Change'}")
            lines.append(f"    {'----':<8} {'-----':<15} {'------'}")
            for entry in mort_trend:
                year = entry.get('year', '?')
                val = entry.get('value', 'N/A')
                change = entry.get('change', '')
                change_str = f"  {change}" if change else ''
                lines.append(f"    {year:<8} {str(val):<15}{change_str}")

        if summary:
            lines.append("")
            lines.append(f"  Summary: {summary}")

        if not prev_trend and not mort_trend and not summary:
            lines.append("  No trend data available")

    # === TREATMENT LANDSCAPE ===
    lines.append("")
    lines.append("TREATMENT LANDSCAPE")
    lines.append("-" * w)
    if treatment.get('error') and not treatment.get('drugs') and not treatment.get('guidelines'):
        lines.append(f"  [Data unavailable: {treatment['error']}]")
    elif not treatment:
        lines.append("  [Section skipped]")
    else:
        soc = treatment.get('standard_of_care', '')
        if soc:
            lines.append(f"  Standard of Care: {_truncate(soc, 70)}")
            lines.append("")

        drugs = treatment.get('drugs', [])
        if drugs:
            lines.append(f"  Approved Drugs ({len(drugs)}):")
            lines.append(f"    {'Drug':<30} {'Status':<15} {'Notes'}")
            lines.append(f"    {'----':<30} {'------':<15} {'-----'}")
            for d in drugs[:15]:
                name = _truncate(d.get('name', 'Unknown'), 28)
                status = d.get('status', 'N/A')
                notes = _truncate(d.get('notes', ''), 30)
                lines.append(f"    {name:<30} {status:<15} {notes}")

        guidelines = treatment.get('guidelines', [])
        if guidelines:
            lines.append("")
            lines.append("  Treatment Guidelines:")
            for g in guidelines[:5]:
                if isinstance(g, str):
                    lines.append(f"    - {_truncate(g, 70)}")
                elif isinstance(g, dict):
                    lines.append(f"    - {_truncate(g.get('title', ''), 70)}")
                    if g.get('source'):
                        lines.append(f"      Source: {g['source']}")

    # === UNMET NEED ===
    lines.append("")
    lines.append("UNMET NEED ASSESSMENT")
    lines.append("-" * w)
    if unmet.get('error') and not unmet.get('trial_activity'):
        lines.append(f"  [Data unavailable: {unmet['error']}]")
    else:
        trial_activity = unmet.get('trial_activity', {})
        if trial_activity:
            total = trial_activity.get('total_recruiting', 0)
            by_phase = trial_activity.get('by_phase', {})
            phase_str = ', '.join(f"{k}: {v}" for k, v in sorted(by_phase.items())) if by_phase else 'N/A'
            lines.append(f"  Active Recruiting Trials: {total}")
            lines.append(f"  By Phase: {phase_str}")

        score = unmet.get('unmet_need_score')
        if score is not None:
            # Visual score bar
            score_bar = '#' * int(score) + '.' * (10 - int(score))
            lines.append(f"")
            lines.append(f"  Unmet Need Score: [{score_bar}] {score}/10")

        justification = unmet.get('justification', [])
        if justification:
            lines.append("")
            lines.append("  Justification:")
            for j in justification[:5]:
                lines.append(f"    - {_truncate(j, 70)}")

        gaps = unmet.get('treatment_gaps', [])
        if gaps:
            lines.append("")
            lines.append("  Identified Treatment Gaps:")
            for g in gaps[:5]:
                lines.append(f"    - {_truncate(g, 70)}")

    # === ECONOMIC BURDEN ===
    lines.append("")
    lines.append("ECONOMIC BURDEN")
    lines.append("-" * w)
    if econ.get('error') and not econ.get('direct_costs') and not econ.get('total_cost'):
        lines.append(f"  [Data unavailable: {econ['error']}]")
    elif not econ:
        lines.append("  [Section skipped]")
    else:
        total = econ.get('total_cost')
        if total:
            lines.append(f"  Total Economic Burden: {_fmt_money(total.get('value'))} ({total.get('year', '')})")

        direct = econ.get('direct_costs')
        if direct:
            lines.append(f"  Direct Healthcare Costs: {_fmt_money(direct.get('value'))}")
            if direct.get('detail'):
                lines.append(f"    {direct['detail']}")

        indirect = econ.get('indirect_costs')
        if indirect:
            lines.append(f"  Indirect Costs (productivity): {_fmt_money(indirect.get('value'))}")
            if indirect.get('detail'):
                lines.append(f"    {indirect['detail']}")

        per_patient = econ.get('per_patient_cost')
        if per_patient:
            source = per_patient.get('source', '')
            label = "Per-Prescription Cost" if 'per prescription' in source.lower() else "Per-Patient Annual Cost"
            lines.append(f"  {label}: {_fmt_money(per_patient.get('value'))}")

        medicaid = econ.get('medicaid_spending', {})
        if medicaid:
            lines.append("")
            lines.append("  Medicaid Drug Utilization:")
            total_spend = medicaid.get('total_spending')
            if total_spend is not None:
                lines.append(f"    Total Reimbursed: {_fmt_money(total_spend)}")
            total_rxs = medicaid.get('total_prescriptions')
            if total_rxs is not None:
                lines.append(f"    Prescriptions: {_fmt_number(total_rxs)}")
            top_drugs = medicaid.get('top_drugs', [])
            if top_drugs:
                lines.append("    Top drugs by spending:")
                for td in top_drugs[:5]:
                    rxs = td.get('prescriptions')
                    rxs_str = f" ({_fmt_number(rxs)} Rx)" if rxs else ""
                    lines.append(f"      {td.get('drug', '?')}: {_fmt_money(td.get('spending'))}{rxs_str}")

        nadac = econ.get('nadac_pricing', [])
        if nadac:
            lines.append("")
            lines.append("  NADAC Acquisition Pricing:")
            for np in nadac[:5]:
                drug = _truncate(np.get('drug', '?'), 40)
                price = np.get('price_per_unit')
                unit = np.get('unit', '')
                if price is not None:
                    lines.append(f"    {drug:<42} ${price:.4f}/{unit}")

    # === GLOBAL COMPARISON ===
    lines.append("")
    lines.append("GLOBAL COMPARISON")
    lines.append("-" * w)
    if global_comp.get('error') and not global_comp.get('regions'):
        lines.append(f"  [Data unavailable: {global_comp['error']}]")
    elif not global_comp.get('regions'):
        lines.append("  No global comparison data available")
    else:
        regions = global_comp.get('regions', [])
        if regions:
            lines.append(f"  {'Region':<20} {'Prevalence':<15} {'Mortality':<15} {'DALYs'}")
            lines.append(f"  {'------':<20} {'----------':<15} {'---------':<15} {'-----'}")
            for r in regions:
                name = r.get('name', 'Unknown')
                prev = str(r.get('prevalence', 'N/A'))
                mort = str(r.get('mortality', 'N/A'))
                dalys = str(r.get('dalys', 'N/A'))
                lines.append(f"  {name:<20} {prev:<15} {mort:<15} {dalys}")

        notes = global_comp.get('notes', [])
        if notes:
            lines.append("")
            for n in notes[:3]:
                lines.append(f"  Note: {n}")

    # === PROVENANCE ===
    lines.append("")
    lines.append("=" * w)
    lines.append("PROVENANCE")
    lines.append("-" * w)
    prov_list = data.get('provenance', [])
    if prov_list:
        for p in prov_list:
            lines.append(f"  > {p}")
    else:
        lines.append("  No provenance data recorded")

    # Errors
    if errors:
        lines.append(f"\n  Sections with errors: {', '.join(errors.keys())}")

    lines.append("")
    lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("=" * w)

    return "\n".join(lines)
