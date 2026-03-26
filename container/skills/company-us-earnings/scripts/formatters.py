#!/usr/bin/env python3
"""
Output formatting functions for company US earnings reports.

This module provides functions for:
- Formatting segment revenue time series tables
- Formatting geographic revenue tables
- Formatting consolidated revenue tables
- Formatting capital allocation tables
- Formatting stock valuation metrics
- Formatting analyst estimates
- Formatting peer comparison tables
- Formatting summary sections
"""

from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict


def format_consolidated_revenue_table(
    periods_to_display: List[str],
    segment_totals_by_period: Dict[str, float],
    quarter_label_to_period: Dict[str, str],
    fiscal_year_end: str,
    get_quarter_label_func,
    get_prior_year_quarter_label_func
) -> Tuple[str, List[Dict]]:
    """Format consolidated quarterly revenue table with YoY and QoQ growth.

    Args:
        periods_to_display: List of period dates to display
        segment_totals_by_period: Dict mapping period -> total revenue
        quarter_label_to_period: Dict mapping quarter label -> period date
        fiscal_year_end: Fiscal year end date (MMDD format)
        get_quarter_label_func: Function to convert period to quarter label
        get_prior_year_quarter_label_func: Function to get prior year quarter label

    Returns:
        Tuple of (formatted table string, list of quarter data dicts)
    """
    lines = []
    lines.append("=" * 120)
    lines.append("QUARTERLY CONSOLIDATED REVENUE")
    lines.append("=" * 120)
    lines.append("")
    lines.append(f"| {'Quarter':<10} | {'Revenue':>12} | {'YoY %':>8} | {'QoQ %':>8} |")
    lines.append(f"|{'-'*12}|{'-'*14}|{'-'*10}|{'-'*10}|")

    consolidated_quarters = []

    # First pass: collect all data in order (oldest to newest for QoQ calc)
    quarters_data_temp = []
    for period in reversed(periods_to_display):  # Reverse to go oldest first
        quarter_label = get_quarter_label_func(period, fiscal_year_end)
        revenue = segment_totals_by_period.get(period, 0)
        if revenue > 0:
            quarters_data_temp.append({
                'period': period,
                'quarter_label': quarter_label,
                'revenue': revenue
            })

    # Calculate QoQ for each quarter (comparing to previous quarter)
    for i, q_data in enumerate(quarters_data_temp):
        if i > 0:
            prev_rev = quarters_data_temp[i-1]['revenue']
            if prev_rev > 0:
                q_data['qoq_growth'] = ((q_data['revenue'] - prev_rev) / prev_rev) * 100
            else:
                q_data['qoq_growth'] = None
        else:
            q_data['qoq_growth'] = None

    # Reverse back to newest first for display
    quarters_data_temp.reverse()

    for q_data in quarters_data_temp:
        quarter_label = q_data['quarter_label']
        revenue = q_data['revenue']
        revenue_str = f"${revenue/1_000_000_000:.2f}B"

        # Calculate YoY using segment totals
        prior_year_label = get_prior_year_quarter_label_func(quarter_label)
        prior_period = quarter_label_to_period.get(prior_year_label)
        prior_revenue = segment_totals_by_period.get(prior_period, 0) if prior_period else 0

        if prior_revenue > 0:
            yoy_growth = ((revenue - prior_revenue) / prior_revenue) * 100
            yoy_str = f"{yoy_growth:+.1f}%"
        else:
            yoy_growth = None
            yoy_str = "-"

        # QoQ formatting
        qoq_growth = q_data.get('qoq_growth')
        if qoq_growth is not None:
            qoq_str = f"{qoq_growth:+.1f}%"
        else:
            qoq_str = "-"

        lines.append(f"| {quarter_label:<10} | {revenue_str:>12} | {yoy_str:>8} | {qoq_str:>8} |")

        # Add to consolidated quarters list for return data
        consolidated_quarters.append({
            'quarter': quarter_label,
            'period': q_data['period'],
            'revenue': revenue,
            'yoy_growth': yoy_growth,
            'qoq_growth': qoq_growth
        })

    return "\n".join(lines), consolidated_quarters


def format_capital_allocation_table(
    quarters_data_temp: List[Dict],
    cf_quarterly: Dict[str, Dict[str, float]]
) -> Tuple[str, List[Dict]]:
    """Format capital allocation table with operating CF, dividends, buybacks, capex.

    Args:
        quarters_data_temp: List of quarter data dicts (from consolidated revenue)
        cf_quarterly: Dict of cash flow metrics by period

    Returns:
        Tuple of (formatted table string, list of capital allocation data dicts)
    """
    lines = []
    lines.append("=" * 120)
    lines.append("QUARTERLY CAPITAL ALLOCATION")
    lines.append("=" * 120)
    lines.append("")
    lines.append(f"| {'Quarter':<10} | {'Op. CF':>12} | {'Dividends':>12} | {'Payout %':>10} | {'Buybacks':>12} | {'CapEx':>12} | {'FCF':>12} |")
    lines.append(f"|{'-'*12}|{'-'*14}|{'-'*14}|{'-'*12}|{'-'*14}|{'-'*14}|{'-'*14}|")

    capital_allocation_quarters = []

    for q_data in quarters_data_temp:
        quarter_label = q_data['quarter_label']
        period = q_data['period']

        ocf = cf_quarterly['operating_cash_flow'].get(period, 0)
        div = cf_quarterly['dividends'].get(period, 0)
        buybacks = cf_quarterly['share_buybacks'].get(period, 0)
        capex = cf_quarterly['capex'].get(period, 0)

        # Free cash flow = Operating CF - CapEx
        fcf = ocf - capex if ocf and capex else 0

        # Payout ratio = Dividends / Operating CF
        payout_pct = (div / ocf * 100) if ocf > 0 and div > 0 else None

        # Format values
        ocf_str = f"${ocf/1_000_000_000:.2f}B" if ocf else "-"
        div_str = f"${div/1_000_000_000:.2f}B" if div else "-"
        buybacks_str = f"${buybacks/1_000_000_000:.2f}B" if buybacks else "-"
        capex_str = f"${capex/1_000_000_000:.2f}B" if capex else "-"
        fcf_str = f"${fcf/1_000_000_000:.2f}B" if fcf else "-"
        payout_str = f"{payout_pct:.1f}%" if payout_pct else "-"

        lines.append(f"| {quarter_label:<10} | {ocf_str:>12} | {div_str:>12} | {payout_str:>10} | {buybacks_str:>12} | {capex_str:>12} | {fcf_str:>12} |")

        capital_allocation_quarters.append({
            'quarter': quarter_label,
            'period': period,
            'operating_cash_flow': ocf if ocf else None,
            'dividends': div if div else None,
            'payout_ratio': payout_pct,
            'share_buybacks': buybacks if buybacks else None,
            'capex': capex if capex else None,
            'free_cash_flow': fcf if fcf else None
        })

    return "\n".join(lines), capital_allocation_quarters


def format_segment_revenue_table(
    segment: str,
    periods_to_display: List[str],
    revenue_series: Dict[str, float],
    oi_series: Dict[str, float],
    rd_series: Dict[str, float],
    segment_totals_by_period: Dict[str, float],
    consolidated_revenue_quarterly: Dict[str, float],
    quarter_label_to_period: Dict[str, str],
    segment_fingerprints: Dict,
    segment_match_cache: Dict,
    quarters_with_bad_data: set,
    fiscal_year_end: str,
    get_quarter_label_func,
    calculate_yoy_func,
    smart_matches_used: List[Dict],
    anomalies_detected: List[Dict]
) -> Tuple[str, Dict]:
    """Format segment revenue time series table with YoY growth and margins.

    Args:
        segment: Segment name
        periods_to_display: List of periods to display
        revenue_series: Dict mapping period -> revenue
        oi_series: Dict mapping period -> operating income
        rd_series: Dict mapping period -> R&D expense
        segment_totals_by_period: Dict mapping period -> total segment revenue
        consolidated_revenue_quarterly: Dict mapping period -> consolidated revenue
        quarter_label_to_period: Dict mapping quarter label -> period
        segment_fingerprints: Segment fingerprints for smart matching
        segment_match_cache: Cache for segment matching
        quarters_with_bad_data: Set of quarter labels with data quality issues
        fiscal_year_end: Fiscal year end date (MMDD)
        get_quarter_label_func: Function to get quarter label
        calculate_yoy_func: Function to calculate YoY with smart matching
        smart_matches_used: List to append smart match info
        anomalies_detected: List to append anomaly info

    Returns:
        Tuple of (formatted table string, segment summary dict)
    """
    lines = []

    # Check if this segment has R&D data
    has_rd_data = any(rd_series.get(p, 0) > 0 for p in periods_to_display)

    # Build table for this segment
    lines.append(f"\n{segment} Trends:")
    if has_rd_data:
        lines.append(f"| {'Quarter':<10} | {'Revenue':>12} | {'YoY %':>8} | {'Op. Income':>12} | {'Margin':>8} | {'R&D':>10} | {'R&D %':>6} | {'% Total':>8} |")
        lines.append(f"|{'-'*12}|{'-'*14}|{'-'*10}|{'-'*14}|{'-'*10}|{'-'*12}|{'-'*8}|{'-'*10}|")
    else:
        lines.append(f"| {'Quarter':<10} | {'Revenue':>12} | {'YoY %':>8} | {'Operating Income':>18} | {'Margin':>8} | {'% of Total':>11} |")
        lines.append(f"|{'-'*12}|{'-'*14}|{'-'*10}|{'-'*20}|{'-'*10}|{'-'*13}|")

    quarters_data = []

    for period in periods_to_display:
        revenue = revenue_series.get(period, 0)
        oi = oi_series.get(period, 0)
        rd = rd_series.get(period, 0)
        margin = (oi / revenue * 100) if revenue > 0 and oi != 0 else 0
        rd_pct = (rd / revenue * 100) if revenue > 0 and rd > 0 else 0

        if revenue > 0:
            quarter_label = get_quarter_label_func(period, fiscal_year_end)
            revenue_str = f"${revenue/1_000_000_000:.2f}B"
            oi_str = f"${oi/1_000_000_000:.2f}B" if oi != 0 else "-"
            margin_str = f"{margin:.1f}%" if oi != 0 else "-"
            rd_str = f"${rd/1_000_000_000:.2f}B" if rd > 0 else "-"
            rd_pct_str = f"{rd_pct:.1f}%" if rd > 0 else "-"

            # Calculate % of Total using segment totals (more reliable than consolidated revenue)
            period_total = segment_totals_by_period.get(period, 0)
            # Fallback to consolidated revenue if segment totals not available
            if period_total <= 0:
                period_total = consolidated_revenue_quarterly.get(period, 0)
            pct_of_total = 0
            pct_of_total_str = "-"
            if period_total > 0:
                pct_of_total = (revenue / period_total) * 100
                pct_of_total_str = f"{pct_of_total:.1f}%"

            # Calculate YoY growth with smart matching for restructurings
            yoy_growth, confidence, matched_segment = calculate_yoy_func(
                segment, revenue, pct_of_total,
                quarter_label, segment_fingerprints,
                revenue_series, quarter_label_to_period,
                segment_match_cache
            )

            # Check if current quarter has bad data (segments don't sum to ~100%)
            if quarter_label in quarters_with_bad_data:
                if yoy_growth is not None and confidence != 'anomaly':
                    confidence = 'anomaly'

            # Format YoY with confidence indicator
            yoy_growth_str = "-"
            if yoy_growth is not None:
                if confidence == 'high':
                    yoy_growth_str = f"{yoy_growth:+.1f}%"
                elif confidence == 'anomaly':
                    yoy_growth_str = f"*{yoy_growth:+.0f}%"
                    anomalies_detected.append({
                        'segment': segment,
                        'quarter': quarter_label,
                        'yoy': yoy_growth
                    })
                elif confidence == 'medium':
                    yoy_growth_str = f"~{yoy_growth:+.1f}%"
                    if matched_segment and matched_segment != segment:
                        smart_matches_used.append({
                            'current': segment,
                            'matched': matched_segment,
                            'quarter': quarter_label
                        })
                elif confidence == 'low':
                    yoy_growth_str = f"~~{yoy_growth:+.1f}%"
                    if matched_segment and matched_segment != segment:
                        smart_matches_used.append({
                            'current': segment,
                            'matched': matched_segment,
                            'quarter': quarter_label
                        })

            # Print row with or without R&D columns
            if has_rd_data:
                lines.append(f"| {quarter_label:<10} | {revenue_str:>12} | {yoy_growth_str:>8} | {oi_str:>12} | {margin_str:>8} | {rd_str:>10} | {rd_pct_str:>6} | {pct_of_total_str:>8} |")
            else:
                lines.append(f"| {quarter_label:<10} | {revenue_str:>12} | {yoy_growth_str:>8} | {oi_str:>18} | {margin_str:>8} | {pct_of_total_str:>11} |")

            # Store quarter data
            margin_val = (oi / revenue * 100) if revenue > 0 and oi != 0 else None
            pct_of_total_val = (revenue / consolidated_revenue_quarterly.get(period, 0) * 100) if consolidated_revenue_quarterly.get(period, 0) > 0 else None
            rd_pct_val = (rd / revenue * 100) if revenue > 0 and rd > 0 else None

            quarters_data.append({
                'quarter': quarter_label,
                'period': period,
                'revenue': revenue,
                'operating_income': oi if oi != 0 else None,
                'margin': margin_val,
                'rd_expense': rd if rd > 0 else None,
                'rd_intensity': rd_pct_val,
                'yoy_growth': yoy_growth,
                'yoy_confidence': confidence,
                'yoy_matched_segment': matched_segment if matched_segment != segment else None,
                'pct_of_total': pct_of_total_val
            })

    segment_summary = {
        'latest_period': periods_to_display[0] if periods_to_display else None,
        'latest_revenue': revenue_series.get(periods_to_display[0], 0) if periods_to_display else 0,
        'quarters': quarters_data
    }

    return "\n".join(lines), segment_summary


def format_geographic_revenue_table(
    geography: str,
    periods_to_display: List[str],
    revenue_series: Dict[str, float],
    oi_series: Dict[str, float],
    consolidated_revenue_quarterly: Dict[str, float],
    quarter_label_to_period: Dict[str, str],
    fiscal_year_end: str,
    get_quarter_label_func,
    get_prior_year_quarter_label_func,
    anomalies_detected: List[Dict]
) -> Tuple[str, Dict]:
    """Format geographic revenue time series table.

    Args:
        geography: Geography name
        periods_to_display: List of periods to display
        revenue_series: Dict mapping period -> revenue
        oi_series: Dict mapping period -> operating income
        consolidated_revenue_quarterly: Dict mapping period -> consolidated revenue
        quarter_label_to_period: Dict mapping quarter label -> period
        fiscal_year_end: Fiscal year end date (MMDD)
        get_quarter_label_func: Function to get quarter label
        get_prior_year_quarter_label_func: Function to get prior year quarter label
        anomalies_detected: List to append anomaly info

    Returns:
        Tuple of (formatted table string, geography summary dict)
    """
    lines = []

    # Build table for this geography
    lines.append(f"\n{geography} Trends:")
    lines.append(f"| {'Quarter':<10} | {'Revenue':>12} | {'YoY %':>8} | {'Operating Income':>18} | {'Margin':>8} | {'% of Total':>11} |")
    lines.append(f"|{'-'*12}|{'-'*14}|{'-'*10}|{'-'*20}|{'-'*10}|{'-'*13}|")

    quarters_data = []

    for period in periods_to_display:
        revenue = revenue_series.get(period, 0)
        oi = oi_series.get(period, 0)
        margin = (oi / revenue * 100) if revenue > 0 and oi != 0 else 0

        if revenue > 0:
            quarter_label = get_quarter_label_func(period, fiscal_year_end)
            revenue_str = f"${revenue/1_000_000_000:.2f}B"
            oi_str = f"${oi/1_000_000_000:.2f}B" if oi != 0 else "-"
            margin_str = f"{margin:.1f}%" if oi != 0 else "-"

            # Calculate YoY growth by matching quarter labels
            yoy_growth_str = "-"
            yoy_growth = None
            yoy_confidence = None
            prior_year_label = get_prior_year_quarter_label_func(quarter_label)
            if prior_year_label and prior_year_label in quarter_label_to_period:
                prior_year_period = quarter_label_to_period[prior_year_label]
                prior_year_revenue = revenue_series.get(prior_year_period, 0)
                if prior_year_revenue > 0:
                    yoy_growth = ((revenue - prior_year_revenue) / prior_year_revenue) * 100
                    # Check for anomalous values (>200% or <-60%)
                    if yoy_growth > 200 or yoy_growth < -60:
                        yoy_growth_str = f"*{yoy_growth:+.0f}%"
                        yoy_confidence = 'anomaly'
                        anomalies_detected.append({
                            'segment': geography,
                            'quarter': quarter_label,
                            'yoy': yoy_growth
                        })
                    else:
                        yoy_growth_str = f"{yoy_growth:+.1f}%"
                        yoy_confidence = 'high'

            # Calculate % of Total
            consolidated_rev = consolidated_revenue_quarterly.get(period, 0)
            pct_of_total_str = "-"
            pct_of_total = None
            if consolidated_rev > 0:
                pct_of_total = (revenue / consolidated_rev) * 100
                pct_of_total_str = f"{pct_of_total:.1f}%"

            lines.append(f"| {quarter_label:<10} | {revenue_str:>12} | {yoy_growth_str:>8} | {oi_str:>18} | {margin_str:>8} | {pct_of_total_str:>11} |")

            # Store quarter data
            margin_val = (oi / revenue * 100) if revenue > 0 and oi != 0 else None

            quarters_data.append({
                'quarter': quarter_label,
                'period': period,
                'revenue': revenue,
                'operating_income': oi if oi != 0 else None,
                'margin': margin_val,
                'yoy_growth': yoy_growth,
                'yoy_confidence': yoy_confidence,
                'pct_of_total': pct_of_total
            })

    geography_summary = {
        'latest_period': periods_to_display[0] if periods_to_display else None,
        'latest_revenue': revenue_series.get(periods_to_display[0], 0) if periods_to_display else 0,
        'quarters': quarters_data
    }

    return "\n".join(lines), geography_summary


def format_smart_match_footnote(smart_matches_used: List[Dict]) -> str:
    """Format footnote for smart matching usage.

    Args:
        smart_matches_used: List of smart match info dicts

    Returns:
        Formatted footnote string
    """
    if not smart_matches_used:
        return ""

    lines = []

    # Deduplicate matches (same current->matched pair)
    unique_matches = {}
    for match in smart_matches_used:
        key = (match['current'], match['matched'])
        if key not in unique_matches:
            unique_matches[key] = match

    lines.append("-" * 80)
    lines.append("Note: ~ indicates YoY calculated using revenue fingerprint matching")
    lines.append("      (segment names changed due to corporate restructuring)")
    for (current, matched), match_info in unique_matches.items():
        lines.append(f"      • {current} matched to prior-year '{matched}'")

    return "\n".join(lines)


def format_anomaly_footnote(anomalies_detected: List[Dict], smart_matches_used: List[Dict]) -> str:
    """Format footnote for anomaly detection.

    Args:
        anomalies_detected: List of anomaly info dicts
        smart_matches_used: List of smart match info (to determine if separator needed)

    Returns:
        Formatted footnote string
    """
    if not anomalies_detected:
        return ""

    lines = []

    if not smart_matches_used:
        lines.append("-" * 80)

    lines.append("Note: * indicates unreliable YoY (segments don't sum to 100% in current or prior year)")
    lines.append("      Caused by corporate restructuring (spin-off/segment redefinition)")

    return "\n".join(lines)


def format_stock_valuation_section(stock_valuation: Dict) -> str:
    """Format stock valuation metrics section.

    Args:
        stock_valuation: Dict of stock valuation data

    Returns:
        Formatted section string
    """
    if not stock_valuation or not stock_valuation.get('current_price'):
        return ""

    lines = []
    lines.append("=" * 80)
    lines.append("STOCK VALUATION")
    lines.append("=" * 80)

    price = stock_valuation.get('current_price')
    change = stock_valuation.get('day_change')
    change_pct = stock_valuation.get('day_change_pct')
    low_52w = stock_valuation.get('fifty_two_week_low')
    high_52w = stock_valuation.get('fifty_two_week_high')

    price_line = f"\nPrice: ${price:.2f}"
    if change is not None and change_pct is not None:
        price_line += f" ({change:+.2f}, {change_pct:+.2f}%)"
    lines.append(price_line)

    if low_52w and high_52w:
        # Calculate position within 52-week range
        range_pct = ((price - low_52w) / (high_52w - low_52w) * 100) if high_52w > low_52w else 0
        lines.append(f"52-Week Range: ${low_52w:.2f} - ${high_52w:.2f} (currently at {range_pct:.0f}%)")

    lines.append("")
    lines.append(f"| {'Metric':<20} | {'Value':>15} |")
    lines.append(f"|{'-'*22}|{'-'*17}|")

    # Market Cap
    mkt_cap = stock_valuation.get('market_cap')
    if mkt_cap:
        mkt_cap_str = f"${mkt_cap/1e9:.1f}B" if mkt_cap >= 1e9 else f"${mkt_cap/1e6:.1f}M"
        lines.append(f"| {'Market Cap':<20} | {mkt_cap_str:>15} |")

    # Enterprise Value
    ev = stock_valuation.get('enterprise_value')
    if ev:
        ev_str = f"${ev/1e9:.1f}B" if ev >= 1e9 else f"${ev/1e6:.1f}M"
        lines.append(f"| {'Enterprise Value':<20} | {ev_str:>15} |")

    # P/E Ratios
    trailing_pe = stock_valuation.get('trailing_pe')
    forward_pe = stock_valuation.get('forward_pe')
    if trailing_pe:
        lines.append(f"| {'Trailing P/E':<20} | {trailing_pe:>15.2f} |")
    if forward_pe:
        lines.append(f"| {'Forward P/E':<20} | {forward_pe:>15.2f} |")

    # EV/EBITDA
    ev_ebitda = stock_valuation.get('ev_ebitda')
    if ev_ebitda:
        lines.append(f"| {'EV/EBITDA':<20} | {ev_ebitda:>15.2f} |")

    # EV/Revenue
    ev_rev = stock_valuation.get('ev_revenue')
    if ev_rev:
        lines.append(f"| {'EV/Revenue':<20} | {ev_rev:>15.2f} |")

    # PEG Ratio
    peg = stock_valuation.get('peg_ratio')
    if peg:
        lines.append(f"| {'PEG Ratio':<20} | {peg:>15.2f} |")

    # Beta
    beta = stock_valuation.get('beta')
    if beta:
        lines.append(f"| {'Beta':<20} | {beta:>15.2f} |")

    # Dividend info
    div_yield = stock_valuation.get('dividend_yield')
    div_rate = stock_valuation.get('dividend_rate')
    if div_yield:
        div_yield_pct = div_yield * 100 if div_yield < 1 else div_yield
        lines.append(f"| {'Dividend Yield':<20} | {div_yield_pct:>14.2f}% |")
    if div_rate:
        lines.append(f"| {'Annual Dividend':<20} | ${div_rate:>14.2f} |")

    # Moving averages context
    ma_50 = stock_valuation.get('fifty_day_avg')
    ma_200 = stock_valuation.get('two_hundred_day_avg')
    if ma_50 and ma_200 and price:
        lines.append("")
        above_50 = "above" if price > ma_50 else "below"
        above_200 = "above" if price > ma_200 else "below"
        lines.append(f"Price is {above_50} 50-day MA (${ma_50:.2f}) and {above_200} 200-day MA (${ma_200:.2f})")

    return "\n".join(lines)


def format_analyst_estimates_section(analyst_estimates: Dict, stock_valuation: Optional[Dict] = None) -> str:
    """Format analyst estimates section.

    Args:
        analyst_estimates: Dict of analyst estimate data
        stock_valuation: Optional dict of stock valuation (for current price)

    Returns:
        Formatted section string
    """
    if not analyst_estimates or not (analyst_estimates.get('consensus_eps') or analyst_estimates.get('target_mean')):
        return ""

    lines = []
    lines.append("=" * 80)
    lines.append("ANALYST ESTIMATES")
    lines.append("=" * 80)

    num_analysts = analyst_estimates.get('num_analysts')
    rec = analyst_estimates.get('recommendation')
    rec_score = analyst_estimates.get('recommendation_score')

    if num_analysts or rec:
        consensus_line = f"\nConsensus: {rec if rec else 'N/A'}"
        if rec_score:
            consensus_line += f" (Score: {rec_score:.2f}/5)"
        if num_analysts:
            consensus_line += f" from {int(num_analysts)} analysts"
        lines.append(consensus_line)

    # Price targets
    target_mean = analyst_estimates.get('target_mean')
    target_low = analyst_estimates.get('target_low')
    target_high = analyst_estimates.get('target_high')

    if target_mean:
        price = stock_valuation.get('current_price') if stock_valuation else None
        upside = ((target_mean / price - 1) * 100) if price else None

        lines.append("\nPrice Targets:")
        target_str = f"${target_mean:.2f}"
        if upside is not None:
            target_str += f" ({upside:+.1f}% vs current)"
        lines.append(f"  Mean Target: {target_str}")
        if target_low and target_high:
            lines.append(f"  Range: ${target_low:.2f} - ${target_high:.2f}")

    # EPS Estimates (consensus-based)
    consensus_eps = analyst_estimates.get('consensus_eps')
    eps_low = analyst_estimates.get('eps_low')
    eps_high = analyst_estimates.get('eps_high')

    if consensus_eps:
        lines.append("\nEPS Estimate (Next Quarter):")
        lines.append(f"  Consensus: ${consensus_eps:.2f}")
        if eps_low and eps_high:
            lines.append(f"  Range: ${eps_low:.2f} - ${eps_high:.2f}")

    # Revenue Estimates (consensus-based)
    consensus_rev = analyst_estimates.get('consensus_revenue')
    rev_low = analyst_estimates.get('revenue_low')
    rev_high = analyst_estimates.get('revenue_high')

    if consensus_rev:
        lines.append("\nRevenue Estimate (Next Quarter):")
        rev_str = f"${consensus_rev/1e9:.2f}B" if consensus_rev >= 1e9 else f"${consensus_rev/1e6:.1f}M"
        lines.append(f"  Consensus: {rev_str}")
        if rev_low and rev_high:
            low_str = f"${rev_low/1e9:.2f}B" if rev_low >= 1e9 else f"${rev_low/1e6:.1f}M"
            high_str = f"${rev_high/1e9:.2f}B" if rev_high >= 1e9 else f"${rev_high/1e6:.1f}M"
            lines.append(f"  Range: {low_str} - {high_str}")

    return "\n".join(lines)


def format_peer_comparison_section(peer_comparison: Dict) -> str:
    """Format peer comparison section.

    Args:
        peer_comparison: Dict of peer comparison data

    Returns:
        Formatted section string
    """
    if not peer_comparison or not (peer_comparison.get('valuation') or peer_comparison.get('peer_tickers')):
        return ""

    lines = []
    lines.append("=" * 80)
    lines.append("PEER COMPARISON")
    lines.append("=" * 80)

    industry = peer_comparison.get('industry')
    sector = peer_comparison.get('sector')
    peers = peer_comparison.get('peer_tickers', [])
    peer_source = peer_comparison.get('peer_source', 'unknown')

    if industry or sector:
        lines.append(f"\nIndustry: {industry or 'N/A'}")
        if sector:
            lines.append(f"Sector: {sector}")

    if peers:
        source_label = ''
        if peer_source == 'sec_sic_search':
            source_label = ' (via SEC SIC search)'
        elif peer_source == 'yahoo_validated':
            source_label = ' (Yahoo, validated)'
        elif peer_source == 'yahoo_filtered':
            source_label = ' (Yahoo, filtered)'
        lines.append(f"Peers{source_label}: {', '.join(peers)}")

    valuation = peer_comparison.get('valuation', [])
    if valuation:
        lines.append(f"\n| {'Company':<8} | {'Market Cap':>12} | {'Fwd P/E':>8} |")
        lines.append(f"|{'-'*10}|{'-'*14}|{'-'*10}|")

        for v in valuation:
            ticker_str = (v.get('ticker') or 'N/A')[:8]
            mkt_cap = v.get('market_cap') or '-'
            fwd_pe = v.get('forward_pe') or '-'
            lines.append(f"| {ticker_str:<8} | {str(mkt_cap):>12} | {str(fwd_pe):>8} |")

    growth = peer_comparison.get('growth', [])
    if growth:
        lines.append(f"\n| {'Company':<8} | {'Rev Growth':>12} | {'Earn Growth':>12} |")
        lines.append(f"|{'-'*10}|{'-'*14}|{'-'*14}|")

        for g in growth:
            ticker_str = (g.get('ticker') or 'N/A')[:8]
            rev_growth = g.get('revenue_growth') or '-'
            earn_growth = g.get('earnings_growth') or '-'
            lines.append(f"| {ticker_str:<8} | {str(rev_growth):>12} | {str(earn_growth):>12} |")

    return "\n".join(lines)


def format_summary_section(
    company_name: str,
    ticker: str,
    cik: str,
    latest_period: str,
    filtered_segments: Dict,
    filtered_geographies: Dict,
    periods_to_display: List,
    all_periods_sorted: List,
    dimensional_facts_count: int
) -> str:
    """Format summary section.

    Args:
        company_name: Company name
        ticker: Stock ticker
        cik: CIK number
        latest_period: Latest period date
        filtered_segments: Dict of filtered segments
        filtered_geographies: Dict of filtered geographies
        periods_to_display: List of periods displayed
        all_periods_sorted: List of all periods fetched
        dimensional_facts_count: Count of XBRL dimensional facts

    Returns:
        Formatted section string
    """
    lines = []
    lines.append("=" * 80)
    lines.append("SUMMARY")
    lines.append("=" * 80)
    lines.append(f"\nCompany: {company_name} ({ticker})")
    lines.append(f"CIK: {cik}")
    lines.append(f"Latest Period: {latest_period}")
    lines.append(f"\nSegments analyzed: {len(filtered_segments)}")
    lines.append(f"Geographies analyzed: {len(filtered_geographies)}")
    lines.append(f"Quarters displayed: {len(periods_to_display)}")
    lines.append(f"Quarters fetched (for YoY): {len(all_periods_sorted)}")
    lines.append(f"XBRL dimensional facts: {dimensional_facts_count}")

    return "\n".join(lines)


def format_main_output_key_metrics(result: Dict) -> str:
    """Format key metrics for main script output (after main function returns).

    Args:
        result: Result dict from get_company_us_earnings()

    Returns:
        Formatted key metrics string
    """
    lines = []
    lines.append("=" * 80)
    lines.append("KEY METRICS")
    lines.append("=" * 80)

    if result.get('segment_revenue'):
        lines.append("\nSegments by Revenue:")
        segments_sorted = sorted(
            result['segment_revenue'].items(),
            key=lambda x: x[1]['latest_revenue'],
            reverse=True
        )
        for i, (segment, data) in enumerate(segments_sorted, 1):
            revenue = data['latest_revenue']
            total_segment = sum(s['latest_revenue'] for s in result['segment_revenue'].values())
            pct = (revenue / total_segment * 100) if total_segment > 0 else 0
            lines.append(f"{i}. {segment}: ${revenue:,.0f} ({pct:.1f}%)")

    if result.get('geographic_revenue') and len(result['geographic_revenue']) > 0:
        lines.append("\nGeographies by Revenue:")
        geographies_sorted = sorted(
            result['geographic_revenue'].items(),
            key=lambda x: x[1]['latest_revenue'],
            reverse=True
        )
        for i, (geography, data) in enumerate(geographies_sorted, 1):
            revenue = data['latest_revenue']
            total_geo = sum(g['latest_revenue'] for g in result['geographic_revenue'].values())
            pct = (revenue / total_geo * 100) if total_geo > 0 else 0
            lines.append(f"{i}. {geography}: ${revenue:,.0f} ({pct:.1f}%)")

    return "\n".join(lines)
