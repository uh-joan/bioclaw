"""Visualization utilities for clinical trial landscape ASCII report."""

from typing import Dict, Any, List
from datetime import datetime, timezone


def _truncate(text: str, max_len: int) -> str:
    if not text:
        return ''
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + '...'


def _fmt_count(count) -> str:
    if count is None:
        return 'N/A'
    if isinstance(count, str):
        try:
            count = int(float(count))
        except ValueError:
            return count
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    if count >= 1_000:
        return f"{count / 1_000:.1f}K"
    return str(count)


def _bar(value: int, max_value: int, width: int = 30) -> str:
    """Generate a simple ASCII bar."""
    if max_value <= 0:
        return ''
    filled = int((value / max_value) * width)
    filled = min(filled, width)
    return '#' * filled + '.' * (width - filled)


def _display_limit(items: list, min_show: int = 5, max_show: int = 25) -> int:
    """Calculate display limit based on data size — no arbitrary hardcoded caps.

    Shows all items up to max_show, with a minimum of min_show.
    For large lists, shows top ~30% but at least min_show.
    """
    n = len(items)
    if n <= max_show:
        return n
    return max(min_show, min(max_show, n * 3 // 10))


def generate_report(data: Dict[str, Any]) -> str:
    """Generate complete ASCII clinical trial landscape report."""
    lines = []
    query = data.get('query', 'Unknown')
    query_type = data.get('query_type', 'auto')
    overview = data.get('overview', {})
    phase_dist = data.get('phase_distribution', {})
    enrollment = data.get('enrollment', {})
    endpoints = data.get('endpoints', {})
    sponsors = data.get('sponsors', {})
    geography = data.get('geography', {})
    competitors = data.get('competitors', {})
    errors = data.get('errors', {})

    w = 80

    # === HEADER ===
    lines.append("=" * w)
    lines.append(f"  CLINICAL TRIAL LANDSCAPE: {query.upper()}")
    lines.append(f"  Query Type: {query_type}")
    lines.append("=" * w)

    # === OVERVIEW ===
    lines.append("")
    lines.append("OVERVIEW")
    lines.append("-" * w)
    if overview.get('error') and not overview.get('total_trials'):
        lines.append(f"  [Data unavailable: {overview['error']}]")
    else:
        total = overview.get('total_trials', 0)
        lines.append(f"  Total Trials Found:  {total}")
        lines.append("")

        phase_bkdn = overview.get('phase_breakdown', {})
        if phase_bkdn:
            lines.append(f"  Phase Breakdown:")
            for phase, count in sorted(phase_bkdn.items()):
                lines.append(f"    {phase:<12} {count:>5}")

        lines.append("")
        status_bkdn = overview.get('status_breakdown', {})
        if status_bkdn:
            lines.append(f"  Status Breakdown:")
            for status, count in sorted(status_bkdn.items()):
                lines.append(f"    {status:<30} {count:>5}")

    # === PHASE DISTRIBUTION ===
    lines.append("")
    lines.append("PHASE DISTRIBUTION")
    lines.append("-" * w)
    if phase_dist.get('error') and not phase_dist.get('phases'):
        lines.append(f"  [Data unavailable: {phase_dist['error']}]")
    else:
        phases = phase_dist.get('phases', {})
        if phases:
            max_count = max(phases.values()) if phases else 1
            for phase, count in sorted(phases.items()):
                bar = _bar(count, max_count, 30)
                lines.append(f"  {phase:<12} {count:>5}  {bar}")
        else:
            lines.append("  No phase data available")

        trends = phase_dist.get('year_trends', {})
        if trends:
            lines.append("")
            lines.append("  Year-over-Year Trend:")
            max_year_count = max(trends.values()) if trends else 1
            for year, count in sorted(trends.items()):
                bar = _bar(count, max_year_count, 20)
                lines.append(f"    {year}  {count:>5} trials  {bar}")

    # === ENROLLMENT ===
    lines.append("")
    lines.append("ENROLLMENT")
    lines.append("-" * w)
    if enrollment.get('error') and not enrollment.get('total_enrolled'):
        lines.append(f"  [Data unavailable: {enrollment['error']}]")
    else:
        total_enrolled = enrollment.get('total_enrolled', 0)
        median_enrolled = enrollment.get('median_per_trial', 0)
        lines.append(f"  Total Enrolled:       {_fmt_count(total_enrolled)}")
        lines.append(f"  Median per Trial:     {_fmt_count(median_enrolled)}")
        lines.append(f"  Trials with Data:     {enrollment.get('trials_with_data', 0)}")

        largest = enrollment.get('largest_trials', [])
        if largest:
            show_count = _display_limit(largest, min_show=5, max_show=15)
            lines.append("")
            lines.append(f"  Largest Trials (top {show_count}):")
            lines.append(f"  {'NCT ID':<15} {'Enrollment':>10}  {'Title'}")
            lines.append(f"  {'~' * 15} {'~' * 10}  {'~' * 45}")
            for t in largest[:show_count]:
                lines.append(
                    f"  {t.get('nct_id', 'N/A'):<15} "
                    f"{t.get('enrollment', 0):>10}  "
                    f"{_truncate(t.get('title', ''), 45)}"
                )

    # === ENDPOINTS ===
    if not data.get('_skip_endpoints'):
        lines.append("")
        lines.append("ENDPOINTS")
        lines.append("-" * w)
        if endpoints.get('error') and not endpoints.get('primary_endpoints'):
            lines.append(f"  [Data unavailable: {endpoints['error']}]")
        else:
            primary = endpoints.get('primary_endpoints', [])
            if primary:
                show_count = _display_limit(primary, min_show=5, max_show=20)
                lines.append(f"  Primary Endpoint Frequency:")
                max_ep = primary[0].get('count', 1) if primary else 1
                for ep in primary[:show_count]:
                    bar = _bar(ep.get('count', 0), max_ep, 20)
                    lines.append(
                        f"    {_truncate(ep.get('name', ''), 35):<37} "
                        f"{ep.get('count', 0):>3}  {bar}"
                    )
            else:
                lines.append("  No endpoint data extracted")

            novel = endpoints.get('novel_endpoints', [])
            if novel:
                show_count = _display_limit(novel, min_show=3, max_show=10)
                lines.append("")
                lines.append("  Novel / Emerging Endpoints:")
                for ep in novel[:show_count]:
                    lines.append(f"    - {ep}")

            pub_endpoints = endpoints.get('pubmed_endpoint_trends', [])
            if pub_endpoints:
                show_count = _display_limit(pub_endpoints, min_show=3, max_show=10)
                lines.append("")
                lines.append("  Recent Publications on Endpoints:")
                for p in pub_endpoints[:show_count]:
                    lines.append(f"    - {_truncate(p.get('title', ''), 70)}")
                    if p.get('pmid'):
                        lines.append(f"      PMID: {p['pmid']}")

    # === SPONSORS ===
    if not data.get('_skip_sponsors'):
        lines.append("")
        lines.append("SPONSORS")
        lines.append("-" * w)
        if sponsors.get('error') and not sponsors.get('top_sponsors'):
            lines.append(f"  [Data unavailable: {sponsors['error']}]")
        else:
            top_sponsors = sponsors.get('top_sponsors', [])
            if top_sponsors:
                show_count = _display_limit(top_sponsors, min_show=5, max_show=20)
                lines.append(f"  Top Sponsors by Trial Count (showing {show_count} of {len(top_sponsors)}):")
                lines.append(f"  {'Sponsor':<45} {'Trials':>6}")
                lines.append(f"  {'~' * 45} {'~' * 6}")
                for s in top_sponsors[:show_count]:
                    lines.append(
                        f"  {_truncate(s.get('name', ''), 43):<45} "
                        f"{s.get('count', 0):>6}"
                    )

            sector = sponsors.get('sector_split', {})
            if sector:
                lines.append("")
                lines.append("  Sector Split:")
                for sec, count in sector.items():
                    lines.append(f"    {sec:<20} {count:>5}")

    # === GEOGRAPHY ===
    lines.append("")
    lines.append("GEOGRAPHY")
    lines.append("-" * w)
    if geography.get('error') and not geography.get('top_countries'):
        lines.append(f"  [Data unavailable: {geography['error']}]")
    else:
        top_countries = geography.get('top_countries', [])
        if top_countries:
            show_count = _display_limit(top_countries, min_show=5, max_show=20)
            lines.append(f"  Top Countries by Site Count:")
            max_sites = top_countries[0].get('count', 1) if top_countries else 1
            for c in top_countries[:show_count]:
                bar = _bar(c.get('count', 0), max_sites, 20)
                lines.append(
                    f"    {_truncate(c.get('country', ''), 25):<27} "
                    f"{c.get('count', 0):>5}  {bar}"
                )

        regional = geography.get('regional_distribution', {})
        if regional:
            lines.append("")
            lines.append("  Regional Distribution:")
            for region, count in regional.items():
                lines.append(f"    {region:<20} {count:>5}")

    # === COMPETITORS ===
    lines.append("")
    lines.append("COMPETITORS")
    lines.append("-" * w)
    if competitors.get('error') and not competitors.get('items'):
        lines.append(f"  [Data unavailable: {competitors['error']}]")
    else:
        items = competitors.get('items', [])
        if items:
            show_count = _display_limit(items, min_show=5, max_show=25)
            comp_type = competitors.get('type', 'drug')
            if comp_type == 'drug':
                lines.append(f"  Drugs in Development ({len(items)} found, showing {show_count}):")
                lines.append(f"  {'Drug':<30} {'Phase':>8}  {'Status'}")
                lines.append(f"  {'~' * 30} {'~' * 8}  {'~' * 20}")
                for item in items[:show_count]:
                    lines.append(
                        f"  {_truncate(item.get('name', ''), 28):<30} "
                        f"{item.get('phase', 'N/A'):>8}  "
                        f"{item.get('status', '')}"
                    )
            else:
                lines.append(f"  Indications Being Tested ({len(items)} found, showing {show_count}):")
                for item in items[:show_count]:
                    trial_count = item.get('trial_count', '')
                    extra = f" ({trial_count} trials)" if trial_count else ''
                    lines.append(f"    - {item.get('name', '')}{extra}")
        else:
            lines.append("  No competitor data available")

    # === PROVENANCE ===
    lines.append("")
    lines.append("=" * w)
    lines.append("PROVENANCE")
    lines.append("-" * w)
    provenance = data.get('provenance', [])
    for p in provenance:
        lines.append(f"  > {p}")

    # === ERRORS ===
    if errors:
        lines.append("")
        lines.append(f"  Sections with errors: {', '.join(errors.keys())}")

    lines.append("")
    lines.append(f"  Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("=" * w)

    return "\n".join(lines)
