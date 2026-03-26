#!/usr/bin/env python3
"""
Company US Earnings - Comprehensive financial analysis from SEC EDGAR filings.

This module extracts and analyzes segment and geographic revenue data from SEC EDGAR
XBRL filings using dimensional analysis. It provides comprehensive financial metrics
including revenue breakdowns, YoY growth, margins, and peer comparisons.

Features:
    - Segment Revenue Analysis: Extract business unit/product line revenue from XBRL
      dimensional data (BusinessSegmentsAxis or SubsegmentsAxis)
    - Geographic Revenue: Extract revenue by region/country (StatementGeographicalAxis)
    - Financial Metrics: Operating income, margins, consolidated revenue, cash flow
    - YoY Growth: Smart segment matching across periods with fuzzy name matching
    - Revenue Reconciliation: Verify segment totals match consolidated revenue
    - Stock Valuation: Real-time pricing, P/E ratios, market cap, dividend data
    - Analyst Estimates: Consensus EPS and revenue forecasts
    - Peer Comparison: Industry benchmarking using Disfold, Yahoo Finance, or SEC SIC
    - Deep Dive: Narrative analysis linking SEC filing text to segment financials
    - Progress Tracking: Real-time progress callbacks for long-running operations

XBRL Dimensional Analysis:
    The module leverages SEC EDGAR's XBRL format to extract multi-dimensional financial
    data. It parses context definitions to identify segment and geographic breakdowns,
    handles both quarterly and cumulative (YTD/QTD) data, and automatically converts
    cumulative values to pure quarterly figures for accurate comparisons.

    Key dimensions analyzed:
    - us-gaap:StatementBusinessSegmentsAxis (business segments)
    - srt:SubsegmentsAxis (product/division subsegments)
    - us-gaap:StatementGeographicalAxis (geographic regions)

Usage Examples:
    Basic usage (8 quarters of segment data):
        >>> result = get_company_us_earnings('JNJ')

    Custom quarters with subsegments:
        >>> result = get_company_us_earnings('ABT', quarters=4, use_subsegments=True)

    With progress tracking:
        >>> def progress(pct, msg):
        ...     print(f"{pct}%: {msg}")
        >>> result = get_company_us_earnings('MDT', progress_callback=progress)

    Command-line usage:
        $ python get_company_us_earnings.py JNJ
        $ python get_company_us_earnings.py ABT 4 --subsegments
        $ python get_company_us_earnings.py MDT 8 --deep-dive "PFA,ablation"

Data Sources:
    - SEC EDGAR: Company submissions, XBRL filings, financial statements
    - Yahoo Finance: Stock pricing, valuation metrics, analyst estimates
    - Disfold: Market-cap ranked peer discovery (same industry)
    - SEC SIC: Standard Industrial Classification peer matching

Returns:
    dict: Comprehensive financial analysis with keys:
        - company: Company name
        - ticker: Stock ticker symbol
        - cik: SEC Central Index Key
        - latest_period: Most recent reporting period
        - quarters_requested/displayed/fetched: Data availability metrics
        - segment_revenue: Business segment breakdown by quarter
        - geographic_revenue: Geographic region breakdown by quarter
        - consolidated_revenue: Total revenue, margins, cash flow
        - reconciliation: Segment total vs consolidated verification
        - stock_valuation: Current pricing and valuation ratios
        - analyst_estimates: Consensus forecasts
        - peer_comparison: Industry benchmarking data
        - deep_dive: Narrative analysis (if requested)

Notes:
    - Requires network access to SEC EDGAR and Yahoo Finance
    - Large companies may take 2-3 minutes due to XBRL parsing
    - Fallback mechanisms ensure data availability even if some sources fail
    - Smart segment matching handles name variations across periods
    - Automatic detection of geographic hierarchies (US vs non-US rollups)
"""

# Standard library imports
import os
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional

# Path setup for imports (works from any working directory)
_this_file = os.path.abspath(__file__)
_scripts_dir = os.path.dirname(_this_file)
_skill_dir = os.path.dirname(_scripts_dir)
_skills_dir = os.path.dirname(_skill_dir)
_claude_dir = os.path.dirname(_skills_dir)

# Add .claude to path for MCP imports
sys.path.insert(0, _claude_dir)

# Add scripts directory to path for local imports
sys.path.insert(0, _scripts_dir)

# BioClaw adaptation: MCP functions accessed via McpClient or mcp_funcs parameter
from mcp_client import McpClient

# Import progress tracker from local module
from progress_tracker import create_progress_tracker

# Import peer validation module
from peer_mapping import validate_yahoo_peers, get_peers_from_sec_sic, get_peers_from_disfold

# Import deep dive module for SEC filing narrative analysis
from deep_dive import perform_deep_dive, format_deep_dive_summary

# Import XBRL parser module for dimensional revenue extraction
from xbrl_parser import (
    parse_xbrl_contexts,
    convert_cumulative_to_quarterly,
    get_quarter_label,
    extract_dimensional_revenue,
)

# Import reconciliation module for segment matching and YoY calculations
from reconciliation import (
    detect_geographic_hierarchy,
    detect_rollup_segments,
    get_prior_year_quarter_label,
    get_best_axis_for_period,
    build_segment_fingerprints,
    calculate_yoy_with_smart_matching,
)

# Import formatters module for output formatting
from formatters import (
    format_consolidated_revenue_table,
    format_capital_allocation_table,
    format_segment_revenue_table,
    format_geographic_revenue_table,
    format_smart_match_footnote,
    format_anomaly_footnote,
    format_stock_valuation_section,
    format_analyst_estimates_section,
    format_peer_comparison_section,
    format_summary_section,
    format_main_output_key_metrics
)

def get_company_us_earnings(
    ticker: str,
    quarters: int = 8,
    use_subsegments: bool = False,
    deep_dive_concepts: Optional[List[str]] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None,
    mcp_funcs: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Extract comprehensive segment & geographic financials from SEC EDGAR filings.

    Uses SEC EDGAR XBRL dimensional analysis to extract:
    - Segment revenue (by business unit/product line)
    - Geographic revenue (by region/country)
    - Operating income and margins by segment
    - Revenue reconciliation (segment total vs consolidated)
    - Optional deep dive into SEC filing narrative text

    Args:
        ticker (str): Stock ticker symbol (e.g., "JNJ", "PFE", "ABT")
        quarters (int, optional): Number of quarters to analyze (default: 8)
        use_subsegments (bool, optional): If True, extract division-level data from SubsegmentsAxis
                                         instead of top-level segments from BusinessSegmentsAxis.
                                         This provides more granular product/division-level revenue.
                                         (default: False)
        deep_dive_concepts (List[str], optional): List of concepts to search in SEC filing narrative text.
                                                 Example: ["PFA", "ablation", "electrophysiology"]
                                                 Searches Business section, MD&A, and Risk Factors.
                                                 (default: None)
        progress_callback: Optional callback(percent, message) for progress reporting

    Returns:
        dict: {
            'company': str,
            'ticker': str,
            'cik': str,
            'latest_period': str,
            'quarters_requested': int,
            'quarters_displayed': int,
            'quarters_fetched': int,
            'segment_revenue': dict,
            'geographic_revenue': dict,
            'reconciliation': dict,
            'deep_dive': dict (if deep_dive_concepts provided),
            'total_segments': int,
            'total_geographies': int,
            'dimensional_facts_count': int
        }
    """

    # Normalize deep_dive_concepts parameter (handle string input from UI)
    if deep_dive_concepts is not None:
        if isinstance(deep_dive_concepts, str):
            # UI passes comma-separated string, convert to list
            deep_dive_concepts = [c.strip() for c in deep_dive_concepts.split(',') if c.strip()]
        elif not isinstance(deep_dive_concepts, list):
            # Ensure it's a list
            deep_dive_concepts = [str(deep_dive_concepts)]

    # Initialize progress tracker
    tracker = create_progress_tracker(callback=progress_callback)
    tracker.start_step('init', f"Looking up {ticker}...")

    print("="*80)
    print(f"EXTRACTING SEGMENT & GEOGRAPHIC FINANCIALS: {ticker}")
    print("="*80)

    # Step 1: Get CIK
    print(f"\nStep 1: Looking up CIK for {ticker}...")

    # BioClaw adaptation: if no mcp_funcs injected, create from McpClient
    if not mcp_funcs:
        try:
            _sec_client = McpClient("sec")
            _sec_client.connect()
            _fin_client = McpClient("financials")
            _fin_client.connect()
        except Exception as e:
            return {'error': f'MCP servers not available: {e}', 'ticker': ticker}

        mcp_funcs = {
            'sec_get_cik': lambda **kw: _sec_client.call("sec-edgar", method="get_company_cik", **kw),
            'sec_get_filing': lambda **kw: _sec_client.call("sec-edgar", method="get_company_submissions", **kw),
            'sec_get_facts': lambda **kw: _sec_client.call("sec-edgar", method="get_company_facts", **kw),
            'sec_get_dimensional': lambda **kw: _sec_client.call("sec-edgar", method="get_dimensional_facts", **kw),
            'sec_filter_filings': lambda **kw: _sec_client.call("sec-edgar", method="filter_filings", **kw),
            'sec_build_fact_table': lambda **kw: _sec_client.call("sec-edgar", method="build_fact_table", **kw),
            'financials_lookup': lambda **kw: _fin_client.call("financial-intelligence", **kw),
        }

    get_cik = mcp_funcs.get('sec_get_cik')
    if not get_cik:
        return {
            'error': 'sec_get_cik not available',
            'ticker': ticker
        }

    cik_result = get_cik(ticker=ticker.upper())

    if 'error' in cik_result or not cik_result.get('cik'):
        return {
            'error': f'Could not find CIK for ticker {ticker}',
            'ticker': ticker
        }

    cik = cik_result['cik']
    # Get proper company name from SEC submissions for Disfold peer lookup
    get_submissions = mcp_funcs.get('sec_get_filing')
    if not get_submissions:
        return {
            'error': 'sec_get_filing not available',
            'ticker': ticker
        }

    submissions_for_name = get_submissions(cik_or_ticker=cik)
    company_name = submissions_for_name.get('name', ticker)
    print(f"✓ Found: {company_name} (CIK: {cik})")

    def parse_mcp_value(text: Optional[str], pattern: str) -> Optional[float]:
        """Extract and parse numeric value from MCP markdown response.

        Parses numeric values from Yahoo Finance MCP responses, handling:
        - Comma separators (1,234.56)
        - Currency symbols ($)
        - Billion/Million suffixes (123.45B, 456.78M)

        Args:
            text: Markdown text from MCP server response
            pattern: Regex pattern to match the numeric value (should capture value in group 1)

        Returns:
            Parsed numeric value as float, or None if not found/parseable

        Examples:
            >>> parse_mcp_value("**Price:** $123.45", r"\\*\\*Price:\\*\\*\\s*\\$?([\\d,\\.]+)")
            123.45
            >>> parse_mcp_value("**Market Cap:** 123.45B", r"\\*\\*Market Cap:\\*\\*\\s*([\\d,\\.]+[BM]?)")
            123450000000.0
        """
        if not text:
            return None
        match = re.search(pattern, text)
        if match:
            val_str = match.group(1).replace(',', '').replace('$', '')
            if val_str.endswith('B'):
                return float(val_str[:-1]) * 1e9
            elif val_str.endswith('M'):
                return float(val_str[:-1]) * 1e6
            try:
                return float(val_str)
            except ValueError:
                return None
        return None

    # Fetch stock valuation data from Yahoo Finance
    tracker.start_step('valuation', f"Fetching stock valuation for {ticker}...")
    stock_valuation = {}
    try:
        print(f"\nFetching stock valuation data for {ticker}...")
        financials_lookup = mcp_funcs.get('financials_lookup')
        summary_data = financials_lookup(method='stock_summary', symbol=ticker.upper())
        pricing_data = financials_lookup(method='stock_pricing', symbol=ticker.upper())
        dividend_data = financials_lookup(method='stock_dividends', symbol=ticker.upper())

        summary_text = summary_data.get('text', '') if isinstance(summary_data, dict) else ''
        pricing_text = pricing_data.get('text', '') if isinstance(pricing_data, dict) else ''
        dividend_text = dividend_data.get('text', '') if isinstance(dividend_data, dict) else ''

        # Parse shares outstanding (format: "1.74B" or "500M")
        shares_outstanding = None
        shares_match = re.search(r'\*\*Shares Outstanding:\*\*\s*([\d,\.]+)([BMK]?)', summary_text)
        if shares_match:
            shares_val = float(shares_match.group(1).replace(',', ''))
            shares_suffix = shares_match.group(2)
            if shares_suffix == 'B':
                shares_outstanding = shares_val * 1e9
            elif shares_suffix == 'M':
                shares_outstanding = shares_val * 1e6
            elif shares_suffix == 'K':
                shares_outstanding = shares_val * 1e3
            else:
                shares_outstanding = shares_val

        cur_price = parse_mcp_value(pricing_text, r'\*\*Current Price:\*\*\s*\$?([\d,\.]+)')
        prev_close = parse_mcp_value(pricing_text, r'\*\*Previous Close:\*\*\s*\$?([\d,\.]+)')

        # Calculate day change from current price and previous close
        # (MCP server returns incorrect Daily Change % values)
        computed_day_change = None
        computed_day_change_pct = None
        if cur_price is not None and prev_close is not None and prev_close != 0:
            computed_day_change = cur_price - prev_close
            computed_day_change_pct = ((cur_price - prev_close) / prev_close) * 100

        stock_valuation = {
            'current_price': cur_price,
            'previous_close': prev_close,
            'day_change': computed_day_change,
            'day_change_pct': computed_day_change_pct,
            'fifty_two_week_low': parse_mcp_value(pricing_text, r'\*\*52-Week Low:\*\*\s*\$?([\d,\.]+)'),
            'fifty_two_week_high': parse_mcp_value(pricing_text, r'\*\*52-Week High:\*\*\s*\$?([\d,\.]+)'),
            'fifty_day_avg': parse_mcp_value(pricing_text, r'\*\*50-Day Average:\*\*\s*\$?([\d,\.]+)'),
            'two_hundred_day_avg': parse_mcp_value(pricing_text, r'\*\*200-Day Average:\*\*\s*\$?([\d,\.]+)'),
            'market_cap': parse_mcp_value(summary_text, r'\*\*Market Cap:\*\*\s*([\d,\.]+[BM]?)'),
            'enterprise_value': parse_mcp_value(summary_text, r'\*\*Enterprise Value:\*\*\s*([\d,\.]+[BM]?)'),
            'shares_outstanding': shares_outstanding,
            'trailing_pe': parse_mcp_value(summary_text, r'\*\*Trailing P/E:\*\*\s*([\d,\.]+)'),
            'forward_pe': parse_mcp_value(summary_text, r'\*\*Forward P/E:\*\*\s*([\d,\.]+)'),
            'peg_ratio': parse_mcp_value(summary_text, r'\*\*PEG Ratio:\*\*\s*([\d,\.]+)'),
            'ev_ebitda': parse_mcp_value(summary_text, r'\*\*EV/EBITDA:\*\*\s*([\d,\.]+)'),
            'ev_revenue': parse_mcp_value(summary_text, r'\*\*EV/Revenue:\*\*\s*([\d,\.]+)'),
            'trailing_eps': parse_mcp_value(summary_text, r'\*\*Trailing EPS:\*\*\s*\$?([\d,\.]+)'),
            'forward_eps': parse_mcp_value(summary_text, r'\*\*Forward EPS:\*\*\s*\$?([\d,\.]+)'),
            'beta': parse_mcp_value(summary_text, r'\*\*Beta:\*\*\s*([\d,\.]+)'),
            'dividend_rate': parse_mcp_value(dividend_text, r'\*\*Annual Dividend Rate:\*\*\s*\$?([\d,\.]+)'),
            'dividend_yield': parse_mcp_value(dividend_text, r'\*\*Dividend Yield:\*\*\s*([\d,\.]+)%'),
            'payout_ratio': parse_mcp_value(dividend_text, r'\*\*Payout Ratio:\*\*\s*([\d,\.]+)%'),
            'ex_dividend_date': None,  # Date parsing not needed for display
        }

        # Calculate market cap from price × shares if not available directly
        if not stock_valuation.get('market_cap') and stock_valuation.get('current_price') and shares_outstanding:
            stock_valuation['market_cap'] = stock_valuation['current_price'] * shares_outstanding
            stock_valuation['market_cap_calculated'] = True

        # Convert dividend yield from percentage to decimal if it was parsed
        if stock_valuation.get('dividend_yield'):
            stock_valuation['dividend_yield'] = stock_valuation['dividend_yield'] / 100

        print(f"✓ Stock valuation data retrieved")
        tracker.complete_step()
    except Exception as e:
        print(f"⚠ Could not fetch stock valuation: {e}")
        tracker.complete_step()

    # Fetch analyst estimates (consensus EPS/Revenue expectations)
    tracker.start_step('estimates', f"Fetching analyst estimates for {ticker}...")
    analyst_estimates = {}
    try:
        print(f"\nFetching analyst estimates for {ticker}...")
        estimates_data = financials_lookup(method='stock_estimates', symbol=ticker.upper())

        estimates_text = estimates_data.get('text', '') if isinstance(estimates_data, dict) else str(estimates_data)

        # Extract section-specific values using a smarter approach
        # First find all Consensus Estimate values - EPS is first, Revenue is second
        consensus_matches = re.findall(r'\*\*Consensus Estimate:\*\*\s*([\d,\.]+[BM]?)\s*USD', estimates_text)

        def _parse_financial_value(val_str):
            """Parse a financial value string with optional B/M/K suffix."""
            val_str = val_str.strip().replace(',', '')
            if val_str.endswith('B'):
                return float(val_str[:-1]) * 1e9
            elif val_str.endswith('M'):
                return float(val_str[:-1]) * 1e6
            elif val_str.endswith('K'):
                return float(val_str[:-1]) * 1e3
            else:
                return float(val_str)

        eps_consensus = None
        rev_consensus = None
        if len(consensus_matches) >= 1:
            try:
                eps_consensus = _parse_financial_value(consensus_matches[0])
            except (ValueError, TypeError):
                eps_consensus = None
        if len(consensus_matches) >= 2:
            try:
                rev_consensus = _parse_financial_value(consensus_matches[1])
            except (ValueError, TypeError):
                rev_consensus = None

        # Extract EPS range from Earnings section
        eps_section = re.search(r'## Earnings.*?(?=## Revenue|## Price|\Z)', estimates_text, re.DOTALL)
        eps_high = None
        eps_low = None
        if eps_section:
            high_match = re.search(r'\*\*High Estimate:\*\*\s*([\d,\.]+)', eps_section.group())
            low_match = re.search(r'\*\*Low Estimate:\*\*\s*([\d,\.]+)', eps_section.group())
            if high_match:
                eps_high = float(high_match.group(1).replace(',', ''))
            if low_match:
                eps_low = float(low_match.group(1).replace(',', ''))

        # Extract Revenue range from Revenue section
        rev_section = re.search(r'## Revenue.*?(?=## Price|## Analyst|\Z)', estimates_text, re.DOTALL)
        rev_high = None
        rev_low = None
        if rev_section:
            high_match = re.search(r'\*\*High Estimate:\*\*\s*([\d,\.]+[BMK]?)', rev_section.group())
            low_match = re.search(r'\*\*Low Estimate:\*\*\s*([\d,\.]+[BMK]?)', rev_section.group())
            if high_match:
                try:
                    rev_high = _parse_financial_value(high_match.group(1))
                except (ValueError, TypeError):
                    rev_high = None
            if low_match:
                try:
                    rev_low = _parse_financial_value(low_match.group(1))
                except (ValueError, TypeError):
                    rev_low = None

        analyst_estimates = {
            'consensus_eps': eps_consensus,
            'eps_high': eps_high,
            'eps_low': eps_low,
            'consensus_revenue': rev_consensus,
            'revenue_high': rev_high,
            'revenue_low': rev_low,
            # Price targets
            'target_mean': parse_mcp_value(estimates_text, r'\*\*Mean Price Target:\*\*\s*([\d,\.]+)'),
            'target_low': parse_mcp_value(estimates_text, r'\*\*Low Target:\*\*\s*([\d,\.]+)'),
            'target_high': parse_mcp_value(estimates_text, r'\*\*High Target:\*\*\s*([\d,\.]+)'),
            'num_analysts': parse_mcp_value(estimates_text, r'\*\*Number of Analysts:\*\*\s*(\d+)'),
            'recommendation': None,
            'recommendation_score': None,
        }

        # Parse recommendation (format: **Recommendation:** Buy (2.21))
        rec_match = re.search(r'\*\*Recommendation:\*\*\s*(\w+)\s*\(([\d,\.]+)\)', estimates_text)
        if rec_match:
            analyst_estimates['recommendation'] = rec_match.group(1)
            analyst_estimates['recommendation_score'] = float(rec_match.group(2).replace(',', ''))

        print(f"✓ Analyst estimates retrieved")
        tracker.complete_step()
    except Exception as e:
        print(f"⚠ Could not fetch analyst estimates: {e}")
        tracker.complete_step()

    # Fetch peer comparison data - Try Disfold first (best quality), then Yahoo
    tracker.start_step('peers', f"Fetching peer comparison for {ticker}...")
    peer_comparison = {}
    disfold_peers_found = False

    try:
        print(f"\nFetching peer comparison for {ticker}...")

        # Strategy 1: Try Disfold first (market-cap ranked, same industry)
        print(f"  Trying Disfold for industry peers...")
        disfold_result = get_peers_from_disfold(company_name, ticker, max_peers=5, mcp_funcs=mcp_funcs)

        if disfold_result.get('peers'):
            disfold_peers_found = True
            peer_tickers = disfold_result['peers']
            peer_details = disfold_result.get('peer_details', [])

            # Build valuation data from Disfold peer details + Yahoo valuation metrics
            valuation_data = []
            print(f"  Fetching valuation metrics for Disfold peers...")
            for p in peer_details:
                peer_ticker = p.get('ticker')
                pe_ratio = None
                forward_pe = None
                peg_ratio = None
                pb_ratio = None

                # Fetch Yahoo valuation data for each peer
                try:
                    peer_summary = financials_lookup(method='stock_summary', symbol=peer_ticker)
                    peer_summary_text = peer_summary.get('text', '') if isinstance(peer_summary, dict) else ''

                    # Parse valuation metrics
                    pe_match = re.search(r'\*\*Trailing P/E:\*\*\s*([\d,\.]+)', peer_summary_text)
                    fwd_pe_match = re.search(r'\*\*Forward P/E:\*\*\s*([\d,\.]+)', peer_summary_text)
                    peg_match = re.search(r'\*\*PEG Ratio:\*\*\s*([\d,\.]+)', peer_summary_text)
                    pb_match = re.search(r'\*\*Price/Book:\*\*\s*([\d,\.]+)', peer_summary_text)

                    if pe_match:
                        pe_ratio = pe_match.group(1)
                    if fwd_pe_match:
                        forward_pe = fwd_pe_match.group(1)
                    if peg_match:
                        peg_ratio = peg_match.group(1)
                    if pb_match:
                        pb_ratio = pb_match.group(1)
                except Exception:
                    pass  # Keep None values if fetch fails

                valuation_data.append({
                    'ticker': peer_ticker,
                    'market_cap': p.get('market_cap_str'),
                    'pe_ratio': pe_ratio,
                    'forward_pe': forward_pe,
                    'peg_ratio': peg_ratio,
                    'pb_ratio': pb_ratio,
                })

            peer_comparison = {
                'industry': disfold_result.get('industry'),
                'sector': None,
                'peer_tickers': peer_tickers,
                'peer_source': 'disfold',
                'valuation': valuation_data,
                'growth': [],
            }
            print(f"✓ Disfold peers found: {', '.join(peer_tickers)}")

        # Strategy 2: Fall back to Yahoo Finance if Disfold failed
        if not disfold_peers_found:
            print(f"  Disfold unavailable, trying Yahoo Finance...")
            peers_data = financials_lookup(method='stock_peers', symbol=ticker.upper())

            peers_text = peers_data.get('text', '') if isinstance(peers_data, dict) else str(peers_data)

            # Extract industry and sector
            industry_match = re.search(r'\*\*Industry:\*\*\s*(.+)', peers_text)
            sector_match = re.search(r'\*\*Sector:\*\*\s*(.+)', peers_text)
            peers_match = re.search(r'\*\*Peer Companies:\*\*\s*(.+)', peers_text)

            # Parse valuation metrics table
            valuation_data = []
            table_match = re.search(r'## Valuation Metrics.*?\n\|.*?\n\|[-|\s]+\|(.*?)(?=\n##|\Z)', peers_text, re.DOTALL)
            if table_match:
                rows = table_match.group(1).strip().split('\n')
                for row in rows:
                    if '|' in row:
                        cols = [c.strip() for c in row.split('|') if c.strip()]
                        if len(cols) >= 6:
                            ticker_name = cols[0].replace('**', '')
                            valuation_data.append({
                                'ticker': ticker_name,
                                'market_cap': cols[1] if cols[1] != 'N/A' else None,
                                'pe_ratio': cols[2] if cols[2] != 'N/A' else None,
                                'forward_pe': cols[3] if cols[3] != 'N/A' else None,
                                'peg_ratio': cols[4] if cols[4] != 'N/A' else None,
                                'pb_ratio': cols[5] if cols[5] != 'N/A' else None,
                            })

            # Parse growth metrics table
            growth_data = []
            growth_match = re.search(r'## Growth Metrics.*?\n\|.*?\n\|[-|\s]+\|(.*?)(?=\n##|\Z)', peers_text, re.DOTALL)
            if growth_match:
                rows = growth_match.group(1).strip().split('\n')
                for row in rows:
                    if '|' in row:
                        cols = [c.strip() for c in row.split('|') if c.strip()]
                        if len(cols) >= 3:
                            ticker_name = cols[0].replace('**', '')
                            growth_data.append({
                                'ticker': ticker_name,
                                'revenue_growth': cols[1] if cols[1] != 'N/A' else None,
                                'earnings_growth': cols[2] if cols[2] != 'N/A' else None,
                            })

            peer_comparison = {
                'industry': industry_match.group(1).strip() if industry_match else None,
                'sector': sector_match.group(1).strip() if sector_match else None,
                'peer_tickers': peers_match.group(1).strip().split(', ') if peers_match else [],
                'valuation': valuation_data,
                'growth': growth_data,
            }
            print(f"✓ Yahoo peer data retrieved ({len(peer_comparison.get('peer_tickers', []))} peers)")

        tracker.complete_step()
    except Exception as e:
        print(f"⚠ Could not fetch peer comparison: {e}")
        tracker.complete_step()

    # Step 2: Get recent 10-Q, 10-K, and 20-F filings
    tracker.start_step('filings', f"Fetching filings for {company_name}...")
    print(f"\nStep 2: Fetching recent filings for {company_name}...")
    submissions = get_submissions(cik_or_ticker=cik)

    if 'error' in submissions:
        return {
            'error': f'Could not get submissions for {ticker}',
            'company': company_name,
            'ticker': ticker,
            'cik': cik
        }

    # Extract fiscal year end (format: MMDD, e.g., '0424' for April 24)
    fiscal_year_end = submissions.get('fiscalYearEnd') or '1231'  # Handle explicit None
    print(f"✓ Fiscal Year End: {fiscal_year_end[:2]}/{fiscal_year_end[2:]}")

    # Get SIC code for peer validation
    sic_code = submissions.get('sic')
    sic_description = submissions.get('sicDescription')

    # Validate peer comparison data using SIC codes (only if not already from Disfold)
    peer_source = peer_comparison.get('peer_source', '')
    if peer_comparison and peer_comparison.get('peer_tickers') and sic_code and peer_source != 'disfold':
        print(f"\nValidating peers using SIC code {sic_code} ({sic_description})...")
        validation = validate_yahoo_peers(ticker, peer_comparison['peer_tickers'], sic_code, mcp_funcs=mcp_funcs)

        if validation.get('invalid_peers'):
            print(f"⚠ Filtered {len(validation['invalid_peers'])} invalid peers (different industry)")

        # Update peer_tickers to only include validated peers
        valid_peers = validation.get('valid_peers', [])
        if valid_peers:
            peer_comparison['peer_tickers'] = valid_peers
            peer_comparison['peer_source'] = validation.get('source', 'yahoo_validated')

            # Filter valuation and growth data to only include valid peers + main ticker
            valid_set = set([p.upper() for p in valid_peers] + [ticker.upper()])
            peer_comparison['valuation'] = [
                v for v in peer_comparison.get('valuation', [])
                if v.get('ticker', '').upper() in valid_set
            ]
            peer_comparison['growth'] = [
                g for g in peer_comparison.get('growth', [])
                if g.get('ticker', '').upper() in valid_set
            ]
            print(f"✓ {len(valid_peers)} valid peers retained")
        else:
            # No valid Yahoo peers - fall back to SEC SIC search
            print("⚠ No valid Yahoo peers in same industry, searching SEC by SIC code...")
            sec_peers = get_peers_from_sec_sic(sic_code, ticker, max_peers=30, use_broad_search=True, mcp_funcs=mcp_funcs)
            if sec_peers:
                peer_comparison['peer_tickers'] = sec_peers
                peer_comparison['peer_source'] = 'sec_sic_search'
                print(f"✓ Found {len(sec_peers)} peers via SEC SIC search: {', '.join(sec_peers)}")

                # Fetch valuation data for SEC SIC peers from Yahoo Finance
                print("  Fetching valuation data for SEC peers...")
                valuation_data = []
                growth_data = []

                # Add main ticker data from already-fetched stock_valuation
                main_mkt_cap = stock_valuation.get('market_cap')
                main_mkt_cap_str = None
                if main_mkt_cap:
                    main_mkt_cap_str = f"${main_mkt_cap/1e9:.1f}B" if main_mkt_cap >= 1e9 else f"${main_mkt_cap/1e6:.1f}M"
                valuation_data.append({
                    'ticker': ticker.upper(),
                    'market_cap': main_mkt_cap_str,
                    'pe_ratio': stock_valuation.get('trailing_pe'),
                    'forward_pe': stock_valuation.get('forward_pe'),
                    'pb_ratio': None,  # Not in our existing data
                })

                # Fetch valuation for SEC peers (filter out those without data)
                # Only check first 15 peers to limit API calls, stop once we have 4 valid
                peer_valuation_raw = []
                max_peers_to_check = 15
                max_valid_peers = 4
                for peer_ticker in sec_peers[:max_peers_to_check]:
                    # Stop early once we have enough valid peers
                    if len(peer_valuation_raw) >= max_valid_peers:
                        break

                    try:
                        summary = financials_lookup(method='stock_summary', symbol=peer_ticker)
                        summary_text = summary.get('text', '') if isinstance(summary, dict) else str(summary)

                        # Skip if Yahoo Finance returned an error
                        if 'ERROR' in summary_text or 'Could not extract' in summary_text:
                            continue

                        # Parse market cap (format: **Market Cap:** 123.45B USD)
                        mkt_cap_match = re.search(r'\*\*Market Cap:\*\*\s*([0-9.]+[BMK]?)\s*USD', summary_text)
                        if not mkt_cap_match:
                            # Try Enterprise Value as fallback
                            mkt_cap_match = re.search(r'\*\*Enterprise Value:\*\*\s*([0-9.]+[BMK]?)\s*USD', summary_text)

                        pe_match = re.search(r'\*\*Trailing P/E:\*\*\s*([0-9.]+)', summary_text)
                        fwd_pe_match = re.search(r'\*\*Forward P/E:\*\*\s*([0-9.]+)', summary_text)
                        pb_match = re.search(r'\*\*Price[/-]to[/-]Book:\*\*\s*([0-9.]+)', summary_text)

                        # Parse market cap value for sorting
                        mkt_cap_str = None
                        mkt_cap_num = None
                        if mkt_cap_match:
                            mkt_cap_val = mkt_cap_match.group(1)
                            mkt_cap_str = f"${mkt_cap_val}"
                            # Convert to number for sorting
                            try:
                                num_part = float(re.search(r'([0-9.]+)', mkt_cap_val).group(1))
                                if 'B' in mkt_cap_val:
                                    mkt_cap_num = num_part * 1e9
                                elif 'M' in mkt_cap_val:
                                    mkt_cap_num = num_part * 1e6
                                elif 'K' in mkt_cap_val:
                                    mkt_cap_num = num_part * 1e3
                                else:
                                    mkt_cap_num = num_part
                            except (ValueError, TypeError):
                                pass
                        else:
                            # Calculate market cap from price × shares outstanding
                            shares_match = re.search(r'\*\*Shares Outstanding:\*\*\s*([0-9.]+)([BMK]?)', summary_text)
                            if shares_match:
                                shares_val = float(shares_match.group(1))
                                shares_suffix = shares_match.group(2)
                                if shares_suffix == 'B':
                                    shares = shares_val * 1e9
                                elif shares_suffix == 'M':
                                    shares = shares_val * 1e6
                                elif shares_suffix == 'K':
                                    shares = shares_val * 1e3
                                else:
                                    shares = shares_val

                                # Get price for this peer
                                try:
                                    pricing = financials_lookup(method='stock_pricing', symbol=peer_ticker)
                                    pricing_text = pricing.get('text', '') if isinstance(pricing, dict) else str(pricing)
                                    price_match = re.search(r'\*\*Current Price:\*\*\s*\$?([0-9,.]+)', pricing_text)
                                    if price_match:
                                        price = float(price_match.group(1).replace(',', ''))
                                        mkt_cap_num = price * shares
                                        if mkt_cap_num >= 1e9:
                                            mkt_cap_str = f"${mkt_cap_num/1e9:.2f}B"
                                        else:
                                            mkt_cap_str = f"${mkt_cap_num/1e6:.1f}M"
                                except Exception:
                                    pass

                        # Only add peer if we have market cap data and it's large enough
                        # Filter out micro/nano-cap companies (<$1B) for meaningful comparison
                        min_peer_market_cap = 1e9  # $1B minimum
                        if mkt_cap_str and mkt_cap_num and mkt_cap_num >= min_peer_market_cap:
                            peer_valuation_raw.append({
                                'ticker': peer_ticker,
                                'market_cap': mkt_cap_str,
                                'market_cap_num': mkt_cap_num,
                                'pe_ratio': pe_match.group(1) if pe_match else None,
                                'forward_pe': fwd_pe_match.group(1) if fwd_pe_match else None,
                                'pb_ratio': pb_match.group(1) if pb_match else None,
                            })
                    except Exception as e:
                        # Skip peers that fail
                        pass

                # Sort peers by market cap (largest first) and take top 4
                peer_valuation_raw.sort(key=lambda x: x.get('market_cap_num', 0), reverse=True)
                peer_valuation_raw = peer_valuation_raw[:4]

                # Update peer_tickers to only include valid peers
                valid_peer_tickers = [p['ticker'] for p in peer_valuation_raw]
                peer_comparison['peer_tickers'] = valid_peer_tickers

                # Remove market_cap_num from output and add to valuation_data
                for p in peer_valuation_raw:
                    del p['market_cap_num']
                    valuation_data.append(p)

                peer_comparison['valuation'] = valuation_data
                peer_comparison['growth'] = growth_data
                print(f"  ✓ Found {len(valid_peer_tickers)} peers with valid data")
            else:
                peer_comparison['peer_tickers'] = []
                peer_comparison['valuation'] = []
                peer_comparison['growth'] = []
                peer_comparison['peer_source'] = 'none'
                print("⚠ No valid peers found")

        # Update industry from SIC if not already set
        if sic_description and not peer_comparison.get('industry'):
            peer_comparison['industry'] = sic_description

    # Get recent filings (10-Q, 10-K, and 20-F for international companies)
    recent_filings = submissions.get('recentFilings', [])

    # Fetch extra quarters for YoY calculation (need 4 quarters back for same quarter last year)
    # User requests N quarters to display, we need N+4 quarters of actual data
    # Example: To show 8 quarters with YoY for all, we need 8+4=12 unique quarterly periods
    # SEC filings: ~3 10-Qs + 1 10-K per year = 4 filings per year covers 4 quarters
    # To get 12 quarters = 3 years of filings = 12 filings minimum
    # Add buffer for safety: fetch N+8 filings (ensures complete YoY coverage)
    quarters_to_fetch = quarters + 8

    # Filter for quarterly and annual reports (including foreign company annual reports)
    target_filings = []
    for filing in recent_filings:
        form = filing.get('form')
        if form in ['10-Q', '10-K', '20-F'] and len(target_filings) < quarters_to_fetch:
            target_filings.append({
                'form': form,
                'accession': filing.get('accessionNumber', '').replace('-', ''),
                'filing_date': filing.get('filingDate', ''),
                'primary_doc': filing.get('primaryDocument', ''),
                'report_date': filing.get('reportDate', '')  # Primary period end date
            })

    if not target_filings:
        return {
            'error': 'No 10-Q, 10-K, or 20-F filings found',
            'company': company_name,
            'ticker': ticker,
            'cik': cik
        }

    print(f"✓ Found {len(target_filings)} recent filings")

    # Step 3: Download and parse XBRL files
    tracker.start_step('xbrl_parsing', f"Parsing {len(target_filings)} XBRL filings...")
    print(f"\nStep 3: Parsing XBRL dimensional data from {len(target_filings)} filings...")

    # Track segment data with filing info to prefer native data over comparative/restated data
    # Structure: {segment_key: {period: {'value': float, 'filing_date': str, 'is_native': bool}}}
    all_segment_data = defaultdict(lambda: defaultdict(lambda: {'value': 0.0, 'filing_date': '', 'is_native': False}))
    all_geography_data = defaultdict(lambda: defaultdict(lambda: {'value': 0.0, 'filing_date': '', 'is_native': False}))
    consolidated_revenue_data = []  # For reconciliation

    # Canonicalize segment names to merge singular/plural variants (e.g., "Service" → "Services")
    # Maps raw segment name → canonical name. Prefers the longer (more specific) form.
    _segment_name_canonical = {}  # {raw_name: canonical_name}

    def _canonicalize_segment_name(name):
        """Resolve singular/plural segment name variants to a single canonical form."""
        if name in _segment_name_canonical:
            return _segment_name_canonical[name]
        # Check if a plural/singular variant already exists
        name_lower = name.lower().strip()
        for existing in list(_segment_name_canonical.values()):
            existing_lower = existing.lower().strip()
            if (name_lower + 's' == existing_lower or
                existing_lower + 's' == name_lower or
                name_lower + 'es' == existing_lower or
                existing_lower + 'es' == name_lower):
                # Prefer the longer name as canonical
                canonical = existing if len(existing) >= len(name) else name
                if canonical != existing:
                    # Re-map all existing references to new canonical
                    for k, v in list(_segment_name_canonical.items()):
                        if v == existing:
                            _segment_name_canonical[k] = canonical
                _segment_name_canonical[name] = canonical
                return canonical
        # No variant found — this name is its own canonical form
        _segment_name_canonical[name] = name
        return name

    # Track XBRL context relationships for product->segment mapping
    # Maps: context_id -> {segment_axis: segment_name, product_axis: product_name}
    context_dimensions_map = defaultdict(dict)  # For fast O(n) product-segment linking

    # Track consolidated cash flow data (non-dimensional) for payout analysis
    consolidated_cf_data = defaultdict(list)  # {concept: [facts]}

    # Track annual segment data separately for Q4 derivation
    # Structure: {segment_key: {period: {'value': float, 'filing_date': str, 'fiscal_year': int}}}
    # Annual data from 10-K can be used to calculate Q4 = Annual - Q3_cumulative
    annual_segment_data = defaultdict(lambda: defaultdict(lambda: {'value': 0.0, 'filing_date': ''}))

    # Track cumulative (YTD) segment data separately for Q4 derivation
    # This stores 9-month (Q3 YTD) data needed to calculate: Q4 = Annual - Q3_cumulative
    # Structure: {segment_key: {period: {'value': float, 'duration': int}}}
    cumulative_segment_data = defaultdict(lambda: defaultdict(lambda: {'value': 0.0, 'duration': 0}))

    # Track annual operating income data separately for Q4 derivation
    # Structure: {segment_key: {period: {'value': float, 'filing_date': str}}}
    annual_oi_data = defaultdict(lambda: defaultdict(lambda: {'value': 0.0, 'filing_date': ''}))

    # Track cumulative (YTD) operating income data for Q4 derivation
    # Structure: {segment_key: {period: {'value': float, 'duration': int}}}
    cumulative_oi_data = defaultdict(lambda: defaultdict(lambda: {'value': 0.0, 'duration': 0}))

    # Track annual geographic data separately for Q4 derivation (mirrors segment logic)
    # Structure: {geography_key: {period: {'value': float, 'filing_date': str}}}
    annual_geographic_data = defaultdict(lambda: defaultdict(lambda: {'value': 0.0, 'filing_date': ''}))

    # Track cumulative (YTD) geographic data for Q4 derivation
    # Structure: {geography_key: {period: {'value': float, 'duration': int}}}
    cumulative_geographic_data = defaultdict(lambda: defaultdict(lambda: {'value': 0.0, 'duration': 0}))

    # Track which filing "owns" each period's segment data
    # Key: (period, axis), Value: {'filing_date': str, 'report_date': str, 'is_native': bool}
    # Native data (period == report_date) always takes priority over comparative data
    period_owner_by_axis = defaultdict(lambda: {'filing_date': '', 'report_date': '', 'is_native': False})

    revenue_concepts = [
        # US GAAP concepts
        'RevenueFromContractWithCustomerExcludingAssessedTax',
        'Revenues',
        'SalesRevenueNet',
        'RevenueFromContractWithCustomerIncludingAssessedTax',
        # IFRS and international concepts
        'Revenue',  # Basic IFRS concept
        'NetSales',  # Common in IFRS filings
        'SalesRevenue',  # Alternative IFRS
        'TotalRevenue',  # Aggregate revenue
        'RevenueFromSaleOfGoods',  # IFRS goods
        'RevenueFromRenderingOfServices',  # IFRS services
        'RevenueFromSalesAndServices',  # Combined
        'RevenueFromOperations',  # Operating revenue
        'Sales',  # Simple sales concept
        'TotalSales',  # Total sales
        'GrossRevenue',  # Gross revenue
        # Additional variations
        'RevenueNet',  # Net revenue
        'OperatingRevenue',  # Operating-specific
        'ProductRevenue',  # Product sales
    ]

    operating_income_concepts = [
        # US GAAP concepts
        'OperatingIncomeLoss',
        'OperatingIncome',
        'IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments',
        'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest',
        'IncomeLossFromContinuingOperationsBeforeIncomeTaxes',
        'IncomeLossFromContinuingOperationsBeforeInterestExpenseInterestIncomeIncomeTaxesExtraordinaryItemsNoncontrollingInterestsNet',
        # IFRS and international concepts
        'OperatingProfit',  # Common IFRS term
        'ProfitLoss',  # IFRS profit/loss
        'ProfitLossFromOperatingActivities',  # Operating activities
        'OperatingProfitLoss',  # Operating profit variant
        'ProfitLossBeforeTax',  # Pre-tax profit
        'EarningsBeforeInterestAndTaxes',  # EBIT
        'EBIT',  # EBIT acronym
        'OperatingResult',  # Operating result
        'ResultFromOperatingActivities',  # Operating activities result
    ]

    rd_expense_concepts = [
        # US GAAP concepts
        'ResearchAndDevelopmentExpense',
        'ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost',
        'ResearchDevelopmentAndComputerSoftwareExpense',
        # IFRS and international concepts
        'ResearchAndDevelopmentExpenses',  # Plural variant
        'ResearchExpense',  # Research only
        'DevelopmentExpense',  # Development only
        'ResearchCosts',  # Cost terminology
        'DevelopmentCosts',  # Development costs
    ]

    # Cash flow concepts for dividend/payout analysis (consolidated, non-dimensional)
    cash_flow_concepts = [
        'NetCashProvidedByUsedInOperatingActivities',
        'DividendsCommonStockCash',
        'PaymentsOfDividends',
        'PaymentsOfDividendsCommonStock',
        'PaymentsForRepurchaseOfCommonStock',
        'PaymentsToAcquirePropertyPlantAndEquipment'  # CapEx
    ]

    dimensional_facts_count = 0
    all_operating_income_data = defaultdict(lambda: defaultdict(lambda: {'value': 0.0, 'filing_date': ''}))
    all_rd_data = defaultdict(lambda: defaultdict(lambda: {'value': 0.0, 'filing_date': ''}))

    # Track annual and cumulative R&D data for Q4 derivation
    annual_rd_data = defaultdict(lambda: defaultdict(lambda: {'value': 0.0, 'filing_date': ''}))
    cumulative_rd_data = defaultdict(lambda: defaultdict(lambda: {'value': 0.0, 'duration': 0}))

    for filing_idx, filing in enumerate(target_filings):
        # Update progress
        tracker.report_filing_progress(filing_idx, len(target_filings))

        # Construct XBRL instance document URL
        cik_padded = cik.zfill(10)
        accession = filing['accession']
        primary_doc = filing['primary_doc']

        # Find the XML instance document (usually ends with .xml or .htm)
        if primary_doc.endswith('.htm'):
            xml_filename = primary_doc.replace('.htm', '_htm.xml')
        else:
            xml_filename = primary_doc

        url = f"https://www.sec.gov/Archives/edgar/data/{cik_padded}/{accession}/{xml_filename}"

        print(f"  Downloading {filing['form']} from {filing['filing_date']}...")

        try:
            # SEC requires User-Agent with email
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Research/Analysis pharma-research@example.com'
            })

            # Rate limiting: SEC allows max 10 req/sec
            time.sleep(0.17)  # ~6 req/sec to be safe

            with urllib.request.urlopen(req) as response:
                xml_content = response.read()

            xml_root = ET.fromstring(xml_content)

            # Parse contexts to extract dimensional information
            contexts, dimension_axes = parse_xbrl_contexts(xml_root)

            # Log dimension axes found (for IFRS debugging)
            if dimension_axes:
                print(f"    📊 Dimension axes found: {', '.join(sorted(dimension_axes))}")

            # Extract revenue facts with dimensions
            filing_facts = extract_dimensional_revenue(
                xml_root, contexts, revenue_concepts, filing['form']
            )

            # Defensive: ensure filing_facts is a list
            if filing_facts is None:
                print(f"    Warning: extract_dimensional_revenue returned None for {filing['form']}")
                filing_facts = []

            dimensional_facts_count += len(filing_facts)

            # Debug: Log unique segments and geographies found in this filing
            if filing_facts:
                unique_segments = {f['segment'] for f in filing_facts if f.get('segment')}
                unique_geos = {f['geography'] for f in filing_facts if f.get('geography')}
                if unique_segments:
                    print(f"    🏢 Segments found: {', '.join(sorted(unique_segments)[:5])}" +
                          (f" + {len(unique_segments)-5} more" if len(unique_segments) > 5 else ""))
                if unique_geos:
                    print(f"    🌍 Geographies found: {', '.join(sorted(unique_geos)[:5])}" +
                          (f" + {len(unique_geos)-5} more" if len(unique_geos) > 5 else ""))

                # Debug: Show sample fact structure
                sample_geo_fact = next((f for f in filing_facts if f.get('geography')), None)
                if sample_geo_fact:
                    start = sample_geo_fact.get('start_date')
                    end = sample_geo_fact['end_date']
                    duration = 'N/A'
                    if start and end:
                        try:
                            from datetime import datetime
                            d1 = datetime.strptime(start, '%Y-%m-%d')
                            d2 = datetime.strptime(end, '%Y-%m-%d')
                            duration = f"{(d2 - d1).days} days"
                        except (ValueError, TypeError):
                            duration = 'N/A'
                    print(f"    📝 Sample geo fact: {sample_geo_fact['geography']} = ${sample_geo_fact['value']:,.0f}, period={end}, duration={duration}")

            # Extract operating income facts with dimensions
            filing_oi_facts = extract_dimensional_revenue(
                xml_root, contexts, operating_income_concepts, filing['form']
            )

            if filing_oi_facts is None:
                filing_oi_facts = []

            dimensional_facts_count += len(filing_oi_facts)

            # Extract R&D expense facts with dimensions
            filing_rd_facts = extract_dimensional_revenue(
                xml_root, contexts, rd_expense_concepts, filing['form']
            )

            if filing_rd_facts is None:
                filing_rd_facts = []

            dimensional_facts_count += len(filing_rd_facts)

            # Extract consolidated cash flow facts (non-dimensional) for payout analysis
            filing_cf_facts = extract_dimensional_revenue(
                xml_root, contexts, cash_flow_concepts, filing['form']
            )

            if filing_cf_facts is None:
                filing_cf_facts = []

            # Store cash flow facts by concept (these are consolidated, not segment-level)
            for cf_fact in filing_cf_facts:
                if not cf_fact.get('segment') and not cf_fact.get('geography'):
                    concept = cf_fact.get('concept', '')
                    # Map to canonical concept names for easier processing
                    if 'NetCashProvided' in concept:
                        cf_fact['canonical'] = 'operating_cash_flow'
                    elif 'Dividend' in concept:
                        cf_fact['canonical'] = 'dividends'
                    elif 'Repurchase' in concept:
                        cf_fact['canonical'] = 'share_buybacks'
                    elif 'PropertyPlantAndEquipment' in concept:
                        cf_fact['canonical'] = 'capex'
                    consolidated_cf_data[cf_fact.get('canonical', 'other')].append(cf_fact)

            # Get filing metadata for ownership determination
            filing_date = filing['filing_date']
            report_date = filing.get('report_date', '')  # Primary period end date for this filing

            def is_native_data(data_period: str, filing_report_date: str) -> bool:
                """Check if data is native to this filing (period matches filing's report date).

                Native data is the primary data the filing reports on. Comparative data is
                historical data restated for comparison purposes.

                Args:
                    data_period: Data period end date (YYYY-MM-DD format)
                    filing_report_date: Filing's primary report period end date (YYYY-MM-DD)

                Returns:
                    True if data period matches filing period (within 7 days tolerance),
                    False otherwise
                """
                if not filing_report_date:
                    return False
                from datetime import datetime
                try:
                    data_dt = datetime.strptime(data_period, '%Y-%m-%d')
                    report_dt = datetime.strptime(filing_report_date, '%Y-%m-%d')
                    return abs((data_dt - report_dt).days) <= 7
                except (ValueError, TypeError):
                    return data_period == filing_report_date

            def should_replace_owner(
                current_owner: Dict[str, Any],
                new_filing_date: str,
                new_report_date: str,
                data_period: str
            ) -> bool:
                """Determine if new filing should replace current owner for this period's data.

                Priority hierarchy:
                1. Native data (primary reporting period) > Comparative data (restatements)
                2. Within same category: prefer filing closer to the data period

                Args:
                    current_owner: Dict with 'filing_date', 'is_native' keys
                    new_filing_date: New filing's filing date (YYYY-MM-DD)
                    new_report_date: New filing's report period (YYYY-MM-DD)
                    data_period: Data period being evaluated (YYYY-MM-DD)

                Returns:
                    True if new filing should own this period's data, False otherwise
                """
                if not current_owner['filing_date']:
                    return True

                new_is_native = is_native_data(data_period, new_report_date)
                current_is_native = current_owner['is_native']

                if new_is_native and not current_is_native:
                    return True
                if current_is_native and not new_is_native:
                    return False

                from datetime import datetime
                try:
                    new_fd = datetime.strptime(new_filing_date, '%Y-%m-%d')
                    current_fd = datetime.strptime(current_owner['filing_date'], '%Y-%m-%d')
                    period_dt = datetime.strptime(data_period, '%Y-%m-%d')
                    return abs((new_fd - period_dt).days) < abs((current_fd - period_dt).days)
                except (ValueError, TypeError):
                    return False

            def calculate_duration(start_date: Optional[str], end_date: Optional[str]) -> Optional[int]:
                """Calculate duration in days between start and end dates.

                Args:
                    start_date: Period start date (YYYY-MM-DD format), None for instant facts
                    end_date: Period end date (YYYY-MM-DD format)

                Returns:
                    Number of days between dates, or None if dates invalid/missing
                """
                if not start_date or not end_date:
                    return None
                from datetime import datetime
                try:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                    return (end_dt - start_dt).days
                except (ValueError, TypeError):
                    return None

            def is_quarterly_duration(duration: Optional[int]) -> bool:
                """Check if duration is approximately quarterly (70-100 days).

                Allows flexibility for fiscal calendar differences (70-100 day range).

                Args:
                    duration: Duration in days, or None

                Returns:
                    True if duration represents a quarter (70-100 days), False otherwise
                """
                if duration is None:
                    return False
                return 70 <= duration <= 100

            def should_prefer_fact(
                new_duration: Optional[int],
                existing_duration: Optional[int],
                new_value: float,
                existing_value: float
            ) -> bool:
                """Determine if new fact should replace existing for same segment/period.

                Priority hierarchy:
                1. Quarterly data (70-100 days) > Cumulative data (YTD/QTD)
                2. Within same type: larger value (handles decimal precision differences)

                Args:
                    new_duration: New fact's duration in days
                    existing_duration: Existing fact's duration in days
                    new_value: New fact's value
                    existing_value: Existing fact's value

                Returns:
                    True if new fact should replace existing, False otherwise
                """
                new_is_quarterly = is_quarterly_duration(new_duration)
                existing_is_quarterly = is_quarterly_duration(existing_duration)

                if new_is_quarterly and not existing_is_quarterly:
                    return True
                if existing_is_quarterly and not new_is_quarterly:
                    return False

                return new_value > existing_value

            # Organize revenue by segment and geography
            # Priority: native data (period == report_date) over comparative/restated data
            # This ensures we use segment names as they were originally reported
            # Also prefer quarterly data over cumulative YTD data (same end_date but different duration)
            for fact in filing_facts:
                segment = fact['segment']
                geography = fact['geography']
                period = fact['end_date']
                value = fact['value']
                dimension_axis = fact.get('segment_axis', '')
                start_date = fact.get('start_date')
                fact_duration = calculate_duration(start_date, period)

                # Track context dimensions for product->segment mapping
                # This builds a map of which segments and products appear together in the same XBRL context
                context_id = fact.get('context_id')
                if context_id and segment and dimension_axis:
                    # Store this dimension in the context map
                    context_dimensions_map[context_id][dimension_axis] = segment

                # Handle annual-duration facts (>300 days) from 10-K filings specially
                # Annual facts represent full-year totals and are stored separately for Q4 derivation
                # Q4 can be calculated as: Annual - Q3_cumulative (when segment names match)
                is_annual_fact = fact_duration is not None and fact_duration > 300

                # Track consolidated revenue (no dimensions)
                if not segment and not geography:
                    consolidated_revenue_data.append(fact)

                # Track segment revenue (with dimension axis for hierarchy detection)
                # IMPORTANT: For IFRS multi-dimensional reporting (e.g., Sanofi), we need segment facts
                # even when geography is present. The same XBRL element may have both dimensions.
                # US GAAP typically has separate segment totals vs segment-geo crosscuts, but IFRS
                # reports revenue with both dimensions on the same fact (e.g., "Dupixent in North America").
                if segment:
                    segment = _canonicalize_segment_name(segment)
                    segment_key = f"{segment}|{dimension_axis}"

                    # Handle annual facts - store in annual_segment_data for Q4 derivation
                    # For IFRS filers that ONLY report annual segment data (no quarterly breakdowns),
                    # we also need to add these to all_segment_data for display purposes.
                    # The convert_cumulative_to_quarterly function will detect annual-only data
                    # (365-day durations) and return as-is without conversion.
                    if is_annual_fact:
                        # Store annual data keyed by segment and period (fiscal year end)
                        # This will be used later to calculate Q4 = Annual - Q3_cumulative for US companies
                        existing_annual = annual_segment_data[segment_key].get(period, {})
                        if not existing_annual.get('value') or value > existing_annual.get('value', 0):
                            annual_segment_data[segment_key][period] = {
                                'value': value,
                                'filing_date': filing_date,
                                'duration': fact_duration
                            }
                        # For IFRS annual-only reporting: also add to all_segment_data
                        # The segment will be processed and displayed if it has no quarterly data
                        # NOTE: We don't continue here anymore - let it fall through to aggregation

                    # Also track 9-month cumulative (Q3 YTD) data for Q4 derivation
                    # Duration ~270 days = 9 months
                    is_q3_cumulative = fact_duration is not None and 250 <= fact_duration <= 290
                    if is_q3_cumulative:
                        existing_cum = cumulative_segment_data[segment_key].get(period, {})
                        if not existing_cum.get('value') or value > existing_cum.get('value', 0):
                            cumulative_segment_data[segment_key][period] = {
                                'value': value,
                                'duration': fact_duration
                            }
                        # Don't continue - we still want to process this for quarterly data too

                    period_axis_key = (period, dimension_axis)
                    current_owner = period_owner_by_axis[period_axis_key]
                    data_is_native = is_native_data(period, report_date)

                    # Check if this filing should own this period's data
                    if should_replace_owner(current_owner, filing_date, report_date, period):
                        # Clear old segment data for this period/axis from the old owner
                        if current_owner['filing_date']:
                            for key in list(all_segment_data.keys()):
                                if key.endswith(f"|{dimension_axis}"):
                                    if period in all_segment_data[key] and all_segment_data[key][period]['filing_date'] == current_owner['filing_date']:
                                        del all_segment_data[key][period]
                        # Set new owner
                        period_owner_by_axis[period_axis_key] = {
                            'filing_date': filing_date,
                            'report_date': report_date,
                            'is_native': data_is_native
                        }
                        all_segment_data[segment_key][period] = {
                            'value': value,
                            'filing_date': filing_date,
                            'is_native': data_is_native,
                            'duration': fact_duration
                        }
                    elif filing_date == current_owner['filing_date']:
                        # Same filing that owns this period - add/update segment
                        # Prefer quarterly data over cumulative data (same end_date, different duration)
                        existing = all_segment_data[segment_key][period]
                        existing_duration = existing.get('duration')
                        if should_prefer_fact(fact_duration, existing_duration, value, existing.get('value', 0)):
                            all_segment_data[segment_key][period] = {
                                'value': value,
                                'filing_date': filing_date,
                                'is_native': data_is_native,
                                'duration': fact_duration
                            }
                    # else: this filing doesn't own this period - skip

                # Track geography revenue (with dimension axis)
                if geography:
                    geography_axis = fact.get('geography_axis', '')
                    geography_key = f"{geography}|{geography_axis}"

                    # Track annual geographic facts for Q4 derivation (mirrors segment logic)
                    if is_annual_fact:
                        existing_annual = annual_geographic_data[geography_key].get(period, {})
                        if not existing_annual.get('value') or value > existing_annual.get('value', 0):
                            annual_geographic_data[geography_key][period] = {
                                'value': value,
                                'filing_date': filing_date,
                                'duration': fact_duration
                            }

                    # Track Q3 cumulative (9-month YTD) geographic data for Q4 derivation
                    is_q3_cumulative_geo = fact_duration is not None and 250 <= fact_duration <= 290
                    if is_q3_cumulative_geo:
                        existing_cum = cumulative_geographic_data[geography_key].get(period, {})
                        if not existing_cum.get('value') or value > existing_cum.get('value', 0):
                            cumulative_geographic_data[geography_key][period] = {
                                'value': value,
                                'duration': fact_duration
                            }

                    period_geo_key = (period, 'geo_' + geography_axis)
                    current_owner = period_owner_by_axis[period_geo_key]
                    data_is_native = is_native_data(period, report_date)

                    if should_replace_owner(current_owner, filing_date, report_date, period):
                        if current_owner['filing_date']:
                            for key in list(all_geography_data.keys()):
                                if key.endswith(f"|{geography_axis}"):
                                    if period in all_geography_data[key] and all_geography_data[key][period]['filing_date'] == current_owner['filing_date']:
                                        del all_geography_data[key][period]
                        period_owner_by_axis[period_geo_key] = {
                            'filing_date': filing_date,
                            'report_date': report_date,
                            'is_native': data_is_native
                        }
                        all_geography_data[geography_key][period] = {
                            'value': value,
                            'filing_date': filing_date,
                            'is_native': data_is_native,
                            'duration': fact_duration
                        }
                        # Debug first geography fact added
                        if len(all_geography_data) == 1 and len(all_geography_data[geography_key]) == 1:
                            print(f"    ✅ First geography fact added: {geography_key} @ {period} = ${value:,.0f} ({fact_duration} days)")
                    elif filing_date == current_owner['filing_date']:
                        existing = all_geography_data[geography_key][period]
                        existing_duration = existing.get('duration')
                        if should_prefer_fact(fact_duration, existing_duration, value, existing.get('value', 0)):
                            all_geography_data[geography_key][period] = {
                                'value': value,
                                'filing_date': filing_date,
                                'is_native': data_is_native,
                                'duration': fact_duration
                            }

            # Organize operating income by segment and geography
            for fact in filing_oi_facts:
                segment = fact['segment']
                geography = fact['geography']
                period = fact['end_date']
                value = fact['value']
                dimension_axis = fact.get('segment_axis', '')
                start_date = fact.get('start_date')
                fact_duration = calculate_duration(start_date, period)

                # Handle annual-duration facts (>300 days) from 10-K filings specially
                is_annual_oi_fact = fact_duration is not None and fact_duration > 300

                # Track segment operating income (with same native-data preference)
                # Only include segment facts WITHOUT geography dimension
                if segment and not geography:
                    segment = _canonicalize_segment_name(segment)
                    segment_key = f"{segment}|{dimension_axis}|OI"

                    # Handle annual OI facts separately - store for Q4 derivation
                    if is_annual_oi_fact:
                        existing_annual = annual_oi_data[segment_key].get(period, {})
                        # Use absolute value comparison for OI (can be negative)
                        if not existing_annual.get('value') or abs(value) > abs(existing_annual.get('value', 0)):
                            annual_oi_data[segment_key][period] = {
                                'value': value,
                                'filing_date': filing_date,
                                'duration': fact_duration
                            }
                        continue  # Don't add annual facts to all_operating_income_data

                    # Track 9-month cumulative (Q3 YTD) OI data for Q4 derivation
                    is_q3_cumulative = fact_duration is not None and 250 <= fact_duration <= 290
                    if is_q3_cumulative:
                        existing_cum = cumulative_oi_data[segment_key].get(period, {})
                        if not existing_cum.get('value') or abs(value) > abs(existing_cum.get('value', 0)):
                            cumulative_oi_data[segment_key][period] = {
                                'value': value,
                                'duration': fact_duration
                            }
                        # Don't continue - still process for quarterly data

                    period_axis_key = (period, dimension_axis + '_OI')
                    current_owner = period_owner_by_axis[period_axis_key]
                    data_is_native = is_native_data(period, report_date)

                    if should_replace_owner(current_owner, filing_date, report_date, period):
                        if current_owner['filing_date']:
                            for key in list(all_operating_income_data.keys()):
                                if key.endswith(f"|{dimension_axis}|OI"):
                                    if period in all_operating_income_data[key] and all_operating_income_data[key][period]['filing_date'] == current_owner['filing_date']:
                                        del all_operating_income_data[key][period]
                        period_owner_by_axis[period_axis_key] = {
                            'filing_date': filing_date,
                            'report_date': report_date,
                            'is_native': data_is_native
                        }
                        all_operating_income_data[segment_key][period] = {
                            'value': value,
                            'filing_date': filing_date,
                            'is_native': data_is_native,
                            'duration': fact_duration
                        }
                    elif filing_date == current_owner['filing_date']:
                        existing = all_operating_income_data[segment_key][period]
                        existing_duration = existing.get('duration')
                        # For OI, use absolute value comparison but still prefer quarterly over cumulative
                        if should_prefer_fact(fact_duration, existing_duration, abs(value), abs(existing.get('value', 0))):
                            all_operating_income_data[segment_key][period] = {
                                'value': value,
                                'filing_date': filing_date,
                                'is_native': data_is_native,
                                'duration': fact_duration
                            }

                # Track geography operating income
                if geography:
                    geography_axis = fact.get('geography_axis', '')
                    geography_key = f"{geography}|{geography_axis}|OI"
                    existing = all_operating_income_data[geography_key].get(period, {'value': 0, 'duration': None})
                    existing_duration = existing.get('duration') if isinstance(existing, dict) else None
                    existing_value = existing.get('value', 0) if isinstance(existing, dict) else existing
                    if should_prefer_fact(fact_duration, existing_duration, abs(value), abs(existing_value)):
                        all_operating_income_data[geography_key][period] = {
                            'value': value,
                            'filing_date': filing_date,
                            'is_native': data_is_native,
                            'duration': fact_duration
                        }

            # Process R&D expense facts
            for fact in filing_rd_facts:
                segment = fact.get('segment')
                geography = fact.get('geography')
                period = fact['end_date']
                value = fact['value']
                dimension_axis = fact.get('segment_axis', '')
                start_date = fact.get('start_date')
                fact_duration = calculate_duration(start_date, period)

                # Handle annual-duration facts (>300 days) for Q4 derivation
                is_annual_rd_fact = fact_duration is not None and fact_duration > 300

                # Track segment R&D expense
                if segment and not geography:
                    segment = _canonicalize_segment_name(segment)
                    segment_key = f"{segment}|{dimension_axis}|RD"

                    # Handle annual R&D facts separately - store for Q4 derivation
                    if is_annual_rd_fact:
                        existing_annual = annual_rd_data[segment_key].get(period, {})
                        if not existing_annual.get('value') or value > existing_annual.get('value', 0):
                            annual_rd_data[segment_key][period] = {
                                'value': value,
                                'filing_date': filing_date,
                                'duration': fact_duration
                            }
                        continue  # Don't add annual facts to all_rd_data

                    # Track 9-month cumulative (Q3 YTD) R&D data for Q4 derivation
                    is_q3_cumulative = fact_duration is not None and 250 <= fact_duration <= 290
                    if is_q3_cumulative:
                        existing_cum = cumulative_rd_data[segment_key].get(period, {})
                        if not existing_cum.get('value') or value > existing_cum.get('value', 0):
                            cumulative_rd_data[segment_key][period] = {
                                'value': value,
                                'duration': fact_duration
                            }
                        # Don't continue - still process for quarterly data

                    existing = all_rd_data[segment_key].get(period, {'value': 0, 'duration': None})
                    existing_duration = existing.get('duration') if isinstance(existing, dict) else None
                    existing_value = existing.get('value', 0) if isinstance(existing, dict) else existing
                    if should_prefer_fact(fact_duration, existing_duration, value, existing_value):
                        all_rd_data[segment_key][period] = {
                            'value': value,
                            'filing_date': filing_date,
                            'is_native': is_native_data(period, report_date),
                            'duration': fact_duration
                        }

        except urllib.error.HTTPError as e:
            print(f"    Error: HTTP {e.code} downloading {filing['form']} from filing date {filing['filing_date']}")
            print(f"           URL: {url}")
            if e.code == 404:
                print(f"           File not found - may use different naming convention or not have XBRL")
            continue
        except urllib.error.URLError as e:
            print(f"    Error: Network error downloading {filing['form']}: {e.reason}")
            continue
        except ET.ParseError as e:
            print(f"    Error: Invalid XML in {filing['form']}: {str(e)[:200]}")
            print(f"           URL: {url}")
            continue
        except Exception as e:
            print(f"    Error: {type(e).__name__} processing {filing['form']}: {e}")
            print(f"           URL: {url}")
            print(f"           This may indicate a data extraction issue - check XBRL namespace/concepts")
            continue

    print(f"✓ Processed {dimensional_facts_count} dimensional facts")

    # Debug: Log what made it into all_geography_data
    total_geo_facts = sum(len(periods) for periods in all_geography_data.values())
    print(f"📊 Geography data stored: {len(all_geography_data)} geographies, {total_geo_facts} period-facts")
    if all_geography_data:
        first_geo_key = list(all_geography_data.keys())[0]
        first_geo_periods = len(all_geography_data[first_geo_key])
        print(f"   Example: {first_geo_key} has {first_geo_periods} periods")

    # Post-process: merge segment keys that were split due to singular/plural naming
    # (e.g., "Service|axis" and "Services|axis" should be one segment)
    # The on-the-fly canonicalization catches most cases but misses the first occurrence
    # of each name variant since there's no match yet when it's first seen.
    if _segment_name_canonical:
        merge_map = {}  # {old_key: canonical_key}
        for raw_name, canonical_name in _segment_name_canonical.items():
            if raw_name != canonical_name:
                # Find all segment data keys using the old name
                for key in list(all_segment_data.keys()):
                    if key.startswith(f"{raw_name}|"):
                        suffix = key[len(raw_name):]  # e.g., "|srt:ProductOrServiceAxis"
                        canonical_key = f"{canonical_name}{suffix}"
                        merge_map[key] = canonical_key

        for old_key, new_key in merge_map.items():
            if old_key in all_segment_data:
                # Merge periods from old key into canonical key
                for period, data in all_segment_data[old_key].items():
                    if period not in all_segment_data[new_key] or \
                       not all_segment_data[new_key][period].get('value'):
                        all_segment_data[new_key][period] = data
                del all_segment_data[old_key]

    # Debug: Log what made it into all_segment_data
    total_seg_facts = sum(len(periods) for periods in all_segment_data.values())
    print(f"📊 Segment data stored: {len(all_segment_data)} segments, {total_seg_facts} period-facts")
    if all_segment_data:
        first_seg_key = list(all_segment_data.keys())[0]
        first_seg_periods = all_segment_data[first_seg_key]
        first_seg_sample = list(first_seg_periods.items())[0] if first_seg_periods else None
        print(f"   Example: {first_seg_key} has {len(first_seg_periods)} periods")
        if first_seg_sample:
            period, data = first_seg_sample
            print(f"   Sample: period={period}, value=${data['value']:,.0f}, duration={data.get('duration', 'N/A')}")

    # Validate that we extracted some data
    if dimensional_facts_count == 0:
        print(f"\n❌ ERROR: No financial data extracted from {len(target_filings)} filings")
        print(f"   This could indicate:")
        print(f"   - Inline XBRL (iXBRL) filings requiring different parsing approach")
        print(f"   - Custom taxonomy not matching standard us-gaap/ifrs-full concepts")
        print(f"   - Files missing actual financial data (only metadata)")
        print(f"\n   For foreign companies filing 20-F with Inline XBRL,")
        print(f"   this skill currently has limited support.")
        return {
            'error': 'No financial data extracted',
            'detail': f'Processed {len(target_filings)} filings but found 0 dimensional facts. This typically occurs with Inline XBRL (iXBRL) filings or custom taxonomies not using standard us-gaap/ifrs-full namespaces.',
            'company': company_name,
            'ticker': ticker,
            'cik': cik,
            'filings_attempted': len(target_filings),
            'recommendation': 'This company may use Inline XBRL format which requires enhanced parsing. Consider using SEC EDGAR viewer or company investor relations site for financial data.'
        }

    # Derive Q4 segment values from annual data where possible
    # For each segment with annual data, try to find matching Q3 cumulative and calculate Q4
    # This handles 10-K filings that only report annual segment totals (no quarterly breakdown)
    q4_derived_count = 0
    for segment_key, annual_periods in annual_segment_data.items():
        for annual_period, annual_info in annual_periods.items():
            annual_value = annual_info.get('value', 0)
            if annual_value <= 0:
                continue

            # Annual period is the fiscal year end (Q4 end date)
            # We need to find Q3's cumulative (YTD through Q3) for the same segment
            # Q3 cumulative end date is typically ~3 months before annual end date
            annual_quarter = get_quarter_label(annual_period, fiscal_year_end)
            if not annual_quarter or 'Q4' not in annual_quarter:
                continue  # Not a Q4 period

            # Look for this segment's Q3 cumulative data (9-month YTD) in cumulative_segment_data
            # First try the dedicated cumulative data store
            cumulative_data = cumulative_segment_data.get(segment_key, {})
            segment_data = all_segment_data.get(segment_key, {})

            # Find Q3 period for the same fiscal year
            q3_cumulative = 0
            q3_period = None
            fiscal_year_match = annual_quarter.replace('Q4', 'Q3')  # e.g., "FY2022 Q4" -> "FY2022 Q3"

            # First, check the dedicated cumulative_segment_data store
            for period, period_info in cumulative_data.items():
                period_quarter = get_quarter_label(period, fiscal_year_end)
                if period_quarter == fiscal_year_match:
                    duration = period_info.get('duration')
                    value = period_info.get('value', 0)
                    # Should be ~270 days (9 months) cumulative
                    if duration and 250 <= duration <= 290 and value > 0:
                        q3_cumulative = value
                        q3_period = period
                        break

            # Fallback: check all_segment_data for cumulative data (in case it wasn't filtered)
            if q3_cumulative == 0:
                for period, period_info in segment_data.items():
                    period_quarter = get_quarter_label(period, fiscal_year_end)
                    if period_quarter == fiscal_year_match:
                        duration = period_info.get('duration')
                        value = period_info.get('value', 0)
                        if duration and 250 <= duration <= 290 and value > 0:
                            q3_cumulative = value
                            q3_period = period
                            break

            # If we found Q3 cumulative, calculate Q4
            if q3_cumulative > 0 and annual_value > q3_cumulative:
                q4_value = annual_value - q3_cumulative

                # Verify the Q4 value is reasonable (between 5% and 60% of annual)
                q4_pct = q4_value / annual_value * 100
                if 5 <= q4_pct <= 60:  # Reasonable Q4 range
                    # Add derived Q4 to all_segment_data
                    all_segment_data[segment_key][annual_period] = {
                        'value': q4_value,
                        'filing_date': annual_info.get('filing_date', ''),
                        'is_native': False,  # Derived, not directly reported
                        'duration': 90,  # Approximate quarterly duration
                        'derived_from_annual': True
                    }
                    q4_derived_count += 1

    if q4_derived_count > 0:
        print(f"✓ Derived {q4_derived_count} Q4 segment values from annual data")

    # Derive Q4 operating income values from annual data where possible
    # Same logic as revenue: Q4 OI = Annual OI - Q3_cumulative OI
    q4_oi_derived_count = 0
    for segment_key, annual_periods in annual_oi_data.items():
        for annual_period, annual_info in annual_periods.items():
            annual_value = annual_info.get('value', 0)
            if annual_value == 0:  # OI can be negative, so check for exactly 0
                continue

            # Annual period is the fiscal year end (Q4 end date)
            annual_quarter = get_quarter_label(annual_period, fiscal_year_end)
            if not annual_quarter or 'Q4' not in annual_quarter:
                continue  # Not a Q4 period

            # Look for Q3 cumulative OI data (9-month YTD)
            cumulative_data = cumulative_oi_data.get(segment_key, {})
            oi_data = all_operating_income_data.get(segment_key, {})

            # Find Q3 period for the same fiscal year
            q3_cumulative = 0
            q3_period = None

            # Extract fiscal year from quarter label (e.g., "FY2024 Q4" -> "FY2024")
            fiscal_year = annual_quarter.replace(' Q4', '')
            fiscal_year_match = f"{fiscal_year} Q3"

            # First check dedicated cumulative OI data
            for period, period_info in cumulative_data.items():
                period_quarter = get_quarter_label(period, fiscal_year_end)
                if period_quarter == fiscal_year_match:
                    q3_cumulative = period_info.get('value', 0)
                    q3_period = period
                    break

            # If not found in cumulative, look for 9-month duration facts in all_operating_income_data
            if q3_cumulative == 0:
                for period, period_info in oi_data.items():
                    period_quarter = get_quarter_label(period, fiscal_year_end)
                    if period_quarter == fiscal_year_match:
                        duration = period_info.get('duration')
                        value = period_info.get('value', 0)
                        if duration and 250 <= duration <= 290 and value != 0:
                            q3_cumulative = value
                            q3_period = period
                            break

            # If we found Q3 cumulative, calculate Q4
            # OI can be negative, so we need different logic than revenue
            if q3_cumulative != 0:
                q4_value = annual_value - q3_cumulative

                # Verify Q4 OI is reasonable (not more than annual in absolute terms)
                if abs(q4_value) <= abs(annual_value) * 1.5:
                    # Add derived Q4 to all_operating_income_data
                    all_operating_income_data[segment_key][annual_period] = {
                        'value': q4_value,
                        'filing_date': annual_info.get('filing_date', ''),
                        'is_native': False,  # Derived, not directly reported
                        'duration': 90,  # Approximate quarterly duration
                        'derived_from_annual': True
                    }
                    q4_oi_derived_count += 1

    if q4_oi_derived_count > 0:
        print(f"✓ Derived {q4_oi_derived_count} Q4 operating income values from annual data")

    # Derive Q4 R&D expense values from annual data where possible
    # Same logic as revenue: Q4 R&D = Annual R&D - Q3_cumulative R&D
    q4_rd_derived_count = 0
    for segment_key, annual_periods in annual_rd_data.items():
        for annual_period, annual_info in annual_periods.items():
            annual_value = annual_info.get('value', 0)
            if annual_value <= 0:
                continue

            # Annual period is the fiscal year end (Q4 end date)
            annual_quarter = get_quarter_label(annual_period, fiscal_year_end)
            if not annual_quarter or 'Q4' not in annual_quarter:
                continue  # Not a Q4 period

            # Look for Q3 cumulative R&D data (9-month YTD)
            cumulative_data = cumulative_rd_data.get(segment_key, {})
            rd_data = all_rd_data.get(segment_key, {})

            # Find Q3 period for the same fiscal year
            q3_cumulative = 0
            q3_period = None

            # Extract fiscal year from quarter label (e.g., "FY2024 Q4" -> "FY2024")
            fiscal_year = annual_quarter.replace(' Q4', '')
            fiscal_year_match = f"{fiscal_year} Q3"

            # First check dedicated cumulative R&D data
            for period, period_info in cumulative_data.items():
                period_quarter = get_quarter_label(period, fiscal_year_end)
                if period_quarter == fiscal_year_match:
                    q3_cumulative = period_info.get('value', 0)
                    q3_period = period
                    break

            # If not found in cumulative, look for 9-month duration facts in all_rd_data
            if q3_cumulative == 0:
                for period, period_info in rd_data.items():
                    period_quarter = get_quarter_label(period, fiscal_year_end)
                    if period_quarter == fiscal_year_match:
                        duration = period_info.get('duration')
                        value = period_info.get('value', 0)
                        if duration and 250 <= duration <= 290 and value > 0:
                            q3_cumulative = value
                            q3_period = period
                            break

            # If we found Q3 cumulative, calculate Q4
            if q3_cumulative > 0 and annual_value > q3_cumulative:
                q4_value = annual_value - q3_cumulative

                # Verify Q4 R&D is reasonable (between 5% and 60% of annual)
                q4_pct = q4_value / annual_value * 100
                if 5 <= q4_pct <= 60:
                    # Add derived Q4 to all_rd_data
                    all_rd_data[segment_key][annual_period] = {
                        'value': q4_value,
                        'filing_date': annual_info.get('filing_date', ''),
                        'is_native': False,
                        'duration': 90,
                        'derived_from_annual': True
                    }
                    q4_rd_derived_count += 1

    if q4_rd_derived_count > 0:
        print(f"✓ Derived {q4_rd_derived_count} Q4 R&D expense values from annual data")

    # Derive Q4 geographic revenue values from annual data where possible
    # Same logic as segment revenue: Q4 = Annual - Q3_cumulative
    q4_geo_derived_count = 0
    for geography_key, annual_periods in annual_geographic_data.items():
        for annual_period, annual_info in annual_periods.items():
            annual_value = annual_info.get('value', 0)
            if annual_value <= 0:
                continue

            annual_quarter = get_quarter_label(annual_period, fiscal_year_end)
            if not annual_quarter or 'Q4' not in annual_quarter:
                continue

            # Look for Q3 cumulative data
            cumulative_data = cumulative_geographic_data.get(geography_key, {})
            geo_data = all_geography_data.get(geography_key, {})

            q3_cumulative = 0
            fiscal_year_match = annual_quarter.replace('Q4', 'Q3')

            # Check dedicated cumulative store first
            for period, period_info in cumulative_data.items():
                period_quarter = get_quarter_label(period, fiscal_year_end)
                if period_quarter == fiscal_year_match:
                    duration = period_info.get('duration')
                    value = period_info.get('value', 0)
                    if duration and 250 <= duration <= 290 and value > 0:
                        q3_cumulative = value
                        break

            # Fallback: check all_geography_data for cumulative data
            if q3_cumulative == 0:
                for period, period_info in geo_data.items():
                    period_quarter = get_quarter_label(period, fiscal_year_end)
                    if period_quarter == fiscal_year_match:
                        duration = period_info.get('duration')
                        value = period_info.get('value', 0)
                        if duration and 250 <= duration <= 290 and value > 0:
                            q3_cumulative = value
                            break

            if q3_cumulative > 0 and annual_value > q3_cumulative:
                q4_value = annual_value - q3_cumulative
                q4_pct = q4_value / annual_value * 100
                if 5 <= q4_pct <= 60:
                    all_geography_data[geography_key][annual_period] = {
                        'value': q4_value,
                        'filing_date': annual_info.get('filing_date', ''),
                        'is_native': False,
                        'duration': 90,
                        'derived_from_annual': True
                    }
                    q4_geo_derived_count += 1

    if q4_geo_derived_count > 0:
        print(f"✓ Derived {q4_geo_derived_count} Q4 geographic revenue values from annual data")

    # Step 4: Calculate reconciliation and identify correct segment axis
    tracker.start_step('reconciliation', "Calculating reconciliation...")
    print(f"\nStep 3: Identifying primary segment axis and calculating reconciliation...")
    print("-"*80)

    # Get latest period
    all_periods = set()
    for segment_periods in all_segment_data.values():
        all_periods.update(segment_periods.keys())
    for geo_periods in all_geography_data.values():
        all_periods.update(geo_periods.keys())

    latest_period = max(all_periods) if all_periods else None

    # Build consolidated revenue by period (for % of Total calculation)
    consolidated_revenue_by_period = {}
    if consolidated_revenue_data:
        consolidated_revenue_data.sort(key=lambda x: x['end_date'], reverse=True)
        for item in consolidated_revenue_data:
            period = item['end_date']
            consolidated_revenue_by_period[period] = max(
                consolidated_revenue_by_period.get(period, 0), item['value']
            )

    # Get consolidated revenue for latest period
    # NOTE: consolidated_revenue_by_period may contain cumulative values (e.g., 6-month YTD)
    # We need to convert to quarterly BEFORE using for rollup detection
    # Otherwise we'd compare quarterly segment values to semi-annual consolidated
    consolidated_revenue_quarterly_early = convert_cumulative_to_quarterly(
        consolidated_revenue_by_period, fiscal_year_end
    )
    consolidated_total = consolidated_revenue_quarterly_early.get(latest_period, 0) if latest_period else 0

    # Pre-compute periods to display (needed for including all segments with data in displayed range)
    periods_by_quarter_early = defaultdict(list)
    for period in all_periods:
        quarter_label = get_quarter_label(period, fiscal_year_end)
        periods_by_quarter_early[quarter_label].append(period)
    unique_periods_early = [max(dates) for dates in periods_by_quarter_early.values()]
    all_periods_sorted_early = sorted(unique_periods_early, reverse=True)
    periods_to_display_set = set(all_periods_sorted_early[:quarters])

    # Group segments by their dimension axis
    # Include ALL segments that have data in ANY displayed period - show legacy and current as-is
    # This allows users to see the full segment history including restructurings
    # (e.g., JNJ: Consumer Health spun off, Pharmaceutical → Innovative Medicine)
    segments_by_axis = defaultdict(dict)
    for segment_key, periods_data in all_segment_data.items():
        if '|' in segment_key:
            segment_name, axis = segment_key.rsplit('|', 1)
        else:
            segment_name, axis = segment_key, ''

        # Include segment if it has data in ANY displayed period
        for period in periods_to_display_set:
            if period in periods_data and periods_data[period]['value'] > 0:
                if segment_name not in segments_by_axis[axis]:
                    # Use latest available period value for this segment
                    latest_val = periods_data.get(latest_period, {}).get('value', 0)
                    if latest_val > 0:
                        segments_by_axis[axis][segment_name] = latest_val
                    else:
                        segments_by_axis[axis][segment_name] = periods_data[period]['value']
                break

    # Find which axis to use for segment breakdown
    # Axis priority order (lower number = higher priority)
    if use_subsegments:
        axis_priority_map = {
            'SubsegmentsAxis': 1,
            'ProductOrServiceAxis': 2,
            'ProductsAndServicesAxis': 2,  # IFRS products (same priority)
            'StatementBusinessSegmentsAxis': 3,
            'SegmentsAxis': 3,  # IFRS business segments (same priority as US GAAP)
        }
    else:
        axis_priority_map = {
            'StatementBusinessSegmentsAxis': 1,
            'SegmentsAxis': 1,  # IFRS business segments (same priority as US GAAP)
            'ProductOrServiceAxis': 2,
            'ProductsAndServicesAxis': 2,  # IFRS products (lower priority)
            'SubsegmentsAxis': 3
        }

    def get_axis_priority(axis: str) -> int:
        """Extract axis priority from full axis name.

        Args:
            axis: Full axis name (e.g., "us-gaap:StatementBusinessSegmentsAxis")

        Returns:
            Priority value (lower = higher priority), 99 if not in priority map
        """
        axis_name = axis.split(':')[-1] if ':' in axis else axis
        return axis_priority_map.get(axis_name, 99)

    # Select the best axis based on priority and segment count
    best_axis = None
    best_priority = 999
    max_segments = 0

    # In default mode, detect single-segment companies:
    # If StatementBusinessSegmentsAxis has exactly 1 segment (e.g., PFE's "Biopharma"),
    # the company is a single-reportable-segment filer. Remember it for potential fallback.
    # Only apply this in default mode — in --subsegments mode, product detail is desired.
    single_segment_business_axis = None
    if not use_subsegments:
        for axis, segments in segments_by_axis.items():
            axis_name = axis.split(':')[-1] if ':' in axis else axis
            if axis_name in ('StatementBusinessSegmentsAxis', 'SegmentsAxis') and len(segments) == 1:
                single_segment_business_axis = axis
                break

    for axis, segments in segments_by_axis.items():
        if len(segments) <= 1:
            continue
        priority = get_axis_priority(axis)
        if priority < best_priority or (priority == best_priority and len(segments) > max_segments):
            best_axis = axis
            best_priority = priority
            max_segments = len(segments)

    # Fallback: if no axis has >1 segment, use the one with most segments
    if best_axis is None and segments_by_axis:
        best_axis = max(segments_by_axis.keys(), key=lambda k: len(segments_by_axis[k]))

    # Use ALL segments from the best axis - no filtering, no reconciliation removal
    # Show everything exactly as reported in SEC filings
    filtered_segments = segments_by_axis.get(best_axis, {})

    # Detect and remove only obvious rollup segments (e.g., "Total Products", "Net Revenue")
    # but keep all actual business segments including legacy ones
    if consolidated_total > 0:
        filtered_segments = detect_rollup_segments(
            filtered_segments, consolidated_total, tolerance_pct=5
        )

    # In default mode, if we still have too many segments after rollup detection (>20),
    # it's likely product-level detail with massive double-counting (e.g., PFE with 45 drugs).
    # If a single-segment business axis exists, fall back to it.
    if not use_subsegments and single_segment_business_axis and best_axis != single_segment_business_axis:
        if len(filtered_segments) > 20:
            best_axis = single_segment_business_axis
            filtered_segments = segments_by_axis.get(single_segment_business_axis, {})
            # Re-run rollup detection on the new axis
            if consolidated_total > 0:
                filtered_segments = detect_rollup_segments(
                    filtered_segments, consolidated_total, tolerance_pct=5
                )

    # Calculate segment total for latest period (only from segments that exist in latest period)
    segment_total = sum(
        v for k, v in filtered_segments.items()
        if any(latest_period in periods_data and periods_data[latest_period]['value'] > 0
               for seg_key, periods_data in all_segment_data.items()
               if (seg_key.rsplit('|', 1)[0] if '|' in seg_key else seg_key) == k)
    ) if latest_period else 0

    # FALLBACK MECHANISM: If primary axis has no useful data, try alternative axes
    # This handles cases like corporate restructuring where SegmentsAxis becomes empty
    # but ProductsAndServicesAxis still has valuable product-level breakdowns
    original_axis = best_axis
    fallback_attempted = False

    # Check if there's ANY segment data across ANY period (not just latest)
    has_any_segment_data = any(
        period in periods_data and periods_data[period]['value'] > 0
        for seg_key, periods_data in all_segment_data.items()
        if not seg_key.endswith('|OI')  # Exclude operating income
        for period in periods_data.keys()
        if period in periods_to_display_set
    ) if best_axis and all_segment_data else False

    # Only fall back if there's truly NO segment data across ANY period
    # Don't fall back just because the latest period is empty
    if not filtered_segments or not has_any_segment_data:
        print(f"\n⚠️  Primary axis '{best_axis}' has NO data across any period")
        print(f"   Segments found: {len(filtered_segments)}, Has any period data: {has_any_segment_data}")
        print(f"   Attempting fallback to alternative axes...")

        # Define fallback hierarchy (in order of business value)
        fallback_hierarchy = [
            ('ProductsAndServicesAxis', 'Product-level breakdown'),
            ('CoreTherapeuticAreaAndEstablishedBrandsAxis', 'Therapeutic area breakdown'),
            ('CoreTherapeuticAreaOtherPromotedBrandsAndEstablishedBrandsAxis', 'Therapeutic area breakdown'),
            ('ProductPortfolioAxis', 'Product portfolio breakdown'),
            ('BrandsAxis', 'Brand-level breakdown'),
        ]

        for fallback_axis_name, description in fallback_hierarchy:
            # Try both IFRS and US-GAAP versions
            for prefix in ['ifrs-full:', 'us-gaap:', '']:
                candidate_axis = f"{prefix}{fallback_axis_name}" if prefix else fallback_axis_name

                if candidate_axis in segments_by_axis and len(segments_by_axis[candidate_axis]) > 1:
                    print(f"   ✓ Found fallback axis: {candidate_axis} ({description})")
                    print(f"     Has {len(segments_by_axis[candidate_axis])} segments")

                    best_axis = candidate_axis
                    filtered_segments = segments_by_axis[candidate_axis]

                    # Apply rollup detection to fallback axis
                    if consolidated_total > 0:
                        filtered_segments = detect_rollup_segments(
                            filtered_segments, consolidated_total, tolerance_pct=5
                        )

                    # Recalculate segment total with fallback data
                    segment_total = sum(
                        v for k, v in filtered_segments.items()
                        if any(latest_period in periods_data and periods_data[latest_period]['value'] > 0
                               for seg_key, periods_data in all_segment_data.items()
                               if (seg_key.rsplit('|', 1)[0] if '|' in seg_key else seg_key) == k)
                    ) if latest_period else 0

                    print(f"     Fallback segment total: ${segment_total:,.0f}")
                    fallback_attempted = True
                    break

            if fallback_attempted:
                break

        if not fallback_attempted:
            print(f"   ⚠️  No fallback axes found with data")

    # DUAL EXTRACTION: Extract product-level data alongside segment data
    # This provides hierarchical drill-down capability without replacing the primary segment view
    product_axis = None
    product_data_by_segment = {}  # Maps: segment_name -> {product_name -> periods_data}
    product_segments_mapping = {}  # Maps: product_name -> segment_name

    print(f"\n🔍 Product-level extraction:")

    # Identify product-level axis (don't use it as primary, but extract it for drill-down)
    product_axis_candidates = [
        'ifrs-full:ProductsAndServicesAxis',
        'us-gaap:ProductOrServiceAxis',
        'ProductsAndServicesAxis',
        'ProductOrServiceAxis'
    ]

    for candidate in product_axis_candidates:
        if candidate in segments_by_axis and len(segments_by_axis[candidate]) > 1:
            product_axis = candidate
            print(f"   ✓ Found product axis: {product_axis} ({len(segments_by_axis[candidate])} products)")
            break

    if product_axis and best_axis and product_axis != best_axis:
        # Extract product-level data and map to segments using XBRL context IDs
        # This is O(contexts) instead of O(facts²) - much faster!
        print(f"   Extracting product-level breakdown using context-based linking...")
        print(f"   Analyzing {len(context_dimensions_map)} contexts...")

        # Debug: Show sample contexts and axes
        if context_dimensions_map:
            sample_contexts = list(context_dimensions_map.items())[:3]
            print(f"   Sample contexts:")
            for ctx_id, dims in sample_contexts:
                print(f"      {ctx_id}: {list(dims.keys())}")

        print(f"   Looking for contexts with BOTH:")
        print(f"      Segment axis: {best_axis}")
        print(f"      Product axis: {product_axis}")

        # Debug: Count how many contexts have each axis
        segment_only_count = sum(1 for dims in context_dimensions_map.values() if best_axis in dims and product_axis not in dims)
        product_only_count = sum(1 for dims in context_dimensions_map.values() if product_axis in dims and best_axis not in dims)
        both_count = sum(1 for dims in context_dimensions_map.values() if best_axis in dims and product_axis in dims)
        neither_count = len(context_dimensions_map) - segment_only_count - product_only_count - both_count

        print(f"   Context breakdown:")
        print(f"      Segment only: {segment_only_count} contexts")
        print(f"      Product only: {product_only_count} contexts")
        print(f"      BOTH axes: {both_count} contexts")
        print(f"      Neither axis: {neither_count} contexts")

        # Find contexts that have BOTH segment and product dimensions
        # These represent products within segments (multi-dimensional facts)
        for context_id, dimensions in context_dimensions_map.items():
            # Check if this context has both our segment axis and product axis
            segment_name = dimensions.get(best_axis)
            product_name = dimensions.get(product_axis)

            if segment_name and product_name:
                # This context has BOTH dimensions = product belongs to segment!
                print(f"      ✓ Found: {product_name} → {segment_name}")

                if segment_name not in product_data_by_segment:
                    product_data_by_segment[segment_name] = {}

                # Get the product's full time series data from all_segment_data
                product_key = f"{product_name}|{product_axis}"
                if product_key in all_segment_data:
                    product_data_by_segment[segment_name][product_name] = all_segment_data[product_key]
                    product_segments_mapping[product_name] = segment_name

        print(f"   ✓ Mapped {len(product_segments_mapping)} products to {len(product_data_by_segment)} segments via context linking")

        # Log sample mappings
        if product_data_by_segment:
            for seg_name, products in list(product_data_by_segment.items())[:3]:
                print(f"      {seg_name}: {len(products)} products ({', '.join(list(products.keys())[:3])}...)")

        # FALLBACK: If context linking found 0 mappings, extract products as unmapped
        # This happens when XBRL doesn't use multi-dimensional contexts (segments and products reported separately)
        if len(product_segments_mapping) == 0:
            print(f"   ℹ️  No hierarchical relationships found in XBRL contexts")
            print(f"   ℹ️  Extracting products as separate (unmapped) dimension...")

            # Extract all products from all_segment_data
            unmapped_products = {}
            for key, periods_data in all_segment_data.items():
                # Check if this is a product (has product_axis)
                if '|' in key:
                    seg_name, axis = key.rsplit('|', 1)
                    if axis == product_axis:
                        unmapped_products[seg_name] = periods_data

            # Store unmapped products with parent_segment=null
            if unmapped_products:
                product_data_by_segment['__UNMAPPED__'] = unmapped_products
                print(f"   ✓ Extracted {len(unmapped_products)} unmapped products")
                # Show sample
                sample_products = list(unmapped_products.keys())[:5]
                print(f"      Sample: {', '.join(sample_products)}")
    else:
        if not product_axis:
            print(f"   ℹ️  No product-level axis found")
        else:
            print(f"   ℹ️  Product axis same as segment axis, skipping dual extraction")

    # Step 4b: Filter geographies using similar logic
    # Include ALL geographies that have data in ANY displayed period
    # Debug: Log geography filtering
    print(f"\n🔍 Geography filtering debug:")
    print(f"   periods_to_display_set has {len(periods_to_display_set)} periods: {sorted(list(periods_to_display_set)[:5]) if periods_to_display_set else []}")
    print(f"   all_geography_data has {len(all_geography_data)} geography keys")
    if all_geography_data:
        first_geo_key = list(all_geography_data.keys())[0]
        first_geo_periods = sorted(list(all_geography_data[first_geo_key].keys()))
        print(f"   Sample geography '{first_geo_key}':")
        print(f"     Has {len(first_geo_periods)} periods: {first_geo_periods[:5]}")
        # Check overlap
        overlap = set(first_geo_periods) & periods_to_display_set
        print(f"     Overlap with display_set: {len(overlap)} periods")
        if overlap:
            print(f"     Overlapping periods: {sorted(list(overlap)[:3])}")

    geographies_by_axis = defaultdict(dict)
    geo_filter_count = 0
    for geography_key, periods_data in all_geography_data.items():
        if '|' in geography_key:
            geography_name, axis = geography_key.rsplit('|', 1)
        else:
            geography_name, axis = geography_key, ''

        # Include geography if it has data in ANY displayed period
        for period in periods_to_display_set:
            if period in periods_data and periods_data[period]['value'] > 0:
                if geography_name not in geographies_by_axis[axis]:
                    latest_val = periods_data.get(latest_period, {}).get('value', 0)
                    if latest_val > 0:
                        geographies_by_axis[axis][geography_name] = latest_val
                    else:
                        geographies_by_axis[axis][geography_name] = periods_data[period]['value']
                    geo_filter_count += 1
                break

    print(f"   {geo_filter_count} geographies passed the period filter")

    # For geography, just use the axis with the most geographies
    filtered_geographies = {}
    if geographies_by_axis:
        # Find axis with most geographies
        best_geo_axis = max(geographies_by_axis.keys(), key=lambda k: len(geographies_by_axis[k]))
        filtered_geographies = geographies_by_axis[best_geo_axis]
        print(f"   ✓ After filtering: {len(filtered_geographies)} geographies in axis '{best_geo_axis}'")
        print(f"   Geographies: {', '.join(list(filtered_geographies.keys())[:5])}" +
              (f" + {len(filtered_geographies)-5} more" if len(filtered_geographies) > 5 else ""))
    else:
        print(f"   ❌ No geographies passed the filter!")

    # Display reconciliation
    reconciliation = {}
    if latest_period:
        print(f"Latest period: {latest_period}")
        if consolidated_total > 0:
            print(f"Consolidated revenue: ${consolidated_total:,.0f}")
            reconciliation['consolidated_revenue'] = consolidated_total
        print(f"Segment total: ${segment_total:,.0f}")
        reconciliation['segment_total'] = segment_total

        if consolidated_total > 0:
            variance = consolidated_total - segment_total
            variance_pct = (variance / consolidated_total * 100) if consolidated_total > 0 else 0
            print(f"Variance: ${variance:,.0f} ({variance_pct:.2f}%)")
            reconciliation['variance'] = variance
            reconciliation['variance_pct'] = variance_pct

    # Step 5: Format results with time series tables
    tracker.start_step('formatting', "Formatting output...")
    print(f"\nStep 4: Formatting results...")
    print("-"*80)

    # Get ALL periods for YoY calculation (includes extra quarters fetched)
    # IMPORTANT: Deduplicate periods by quarter (same quarter can have multiple end dates)
    # Group by quarter label and keep only the LATEST date for each quarter
    periods_by_quarter = defaultdict(list)
    for period in all_periods:
        quarter_label = get_quarter_label(period, fiscal_year_end)
        periods_by_quarter[quarter_label].append(period)

    # For each quarter, keep only the latest (maximum) date
    unique_periods = []
    for quarter_label, dates in periods_by_quarter.items():
        latest_date = max(dates)
        unique_periods.append(latest_date)

    # Sort by date (newest first)
    all_periods_sorted = sorted(unique_periods, reverse=True)

    # Display only the requested number of quarters (user's original request)
    periods_to_display = all_periods_sorted[:quarters]

    # Use all fetched periods for YoY calculation (includes +8 extra filings for YoY coverage)
    periods_for_yoy = all_periods_sorted

    # Build a mapping from quarter label to period date for YoY lookups
    # This allows matching FY2024 Q1 -> FY2023 Q1 even if there are gaps in data
    quarter_label_to_period = {}
    for period in periods_for_yoy:
        label = get_quarter_label(period, fiscal_year_end)
        quarter_label_to_period[label] = period

    # Convert consolidated revenue to quarterly (not cumulative)
    consolidated_revenue_quarterly = convert_cumulative_to_quarterly(consolidated_revenue_by_period, fiscal_year_end)

    # Build segment fingerprints for smart matching across restructurings
    # Convert all segment data to quarterly first for fingerprinting
    all_segment_data_quarterly = {}
    for segment_key, period_data in all_segment_data.items():
        if not segment_key.endswith('|OI'):
            all_segment_data_quarterly[segment_key] = convert_cumulative_to_quarterly(period_data, fiscal_year_end)

    segment_fingerprints = build_segment_fingerprints(
        all_segment_data_quarterly,
        consolidated_revenue_quarterly,
        periods_for_yoy,
        fiscal_year_end
    )

    # Cache for segment matching consistency across quarters
    segment_match_cache = {}

    # Format product-level data for result (if dual extraction was performed)
    product_revenue_summary = {}
    if product_data_by_segment:
        print(f"\n📦 Formatting product-level revenue...")

        for segment_name, products in product_data_by_segment.items():
            for product_name, periods_data in products.items():
                # Convert cumulative to quarterly
                quarterly_periods = convert_cumulative_to_quarterly(periods_data, fiscal_year_end)

                # Build period list for this product
                product_periods = []
                for period in periods_to_display:
                    if period in quarterly_periods:
                        period_data = quarterly_periods[period]
                        # Handle both dict format {'value': X} and direct float format
                        if isinstance(period_data, dict):
                            revenue = period_data.get('value', 0)
                        else:
                            revenue = period_data

                        product_periods.append({
                            'period': period,
                            'quarter': get_quarter_label(period, fiscal_year_end),
                            'revenue': revenue
                        })

                if product_periods:
                    # Handle unmapped products (parent_segment=null when no hierarchical relationship exists)
                    parent_seg = None if segment_name == '__UNMAPPED__' else segment_name

                    # Find actual latest period with non-zero revenue for this product
                    # (Don't assume all products exist in periods_to_display[0])
                    latest_rev = 0
                    latest_per = None

                    # Iterate through periods in reverse chronological order to find most recent non-zero
                    for period in periods_to_display:
                        if period in quarterly_periods:
                            period_data = quarterly_periods[period]
                            revenue = period_data.get('value', 0) if isinstance(period_data, dict) else period_data
                            if revenue and revenue > 0:
                                latest_rev = revenue
                                latest_per = period
                                break  # Found most recent non-zero, stop looking

                    # Only include products that have revenue in at least one displayed period
                    if latest_rev > 0:
                        product_revenue_summary[product_name] = {
                            'parent_segment': parent_seg,
                            'latest_period': latest_per,
                            'latest_revenue': latest_rev,
                            'quarters': product_periods
                        }

        # Count mapped vs unmapped products
        mapped_count = sum(1 for p in product_revenue_summary.values() if p['parent_segment'] is not None)
        unmapped_count = len(product_revenue_summary) - mapped_count

        if unmapped_count > 0:
            print(f"   ✓ Formatted {len(product_revenue_summary)} products: {mapped_count} mapped, {unmapped_count} unmapped")
        else:
            print(f"   ✓ Formatted {len(product_revenue_summary)} products across {len(product_data_by_segment)} segments")

    # Build product totals by period for consolidated revenue fallback
    # This allows us to show consolidated revenue even when segment splits aren't available
    product_totals_by_period = {}
    if product_revenue_summary:
        print(f"\n📊 Aggregating product revenue by period for consolidated totals...")
        for product_name, product_data in product_revenue_summary.items():
            for quarter_data in product_data.get('quarters', []):
                period = quarter_data['period']
                revenue = quarter_data['revenue']
                product_totals_by_period[period] = product_totals_by_period.get(period, 0) + revenue

        if product_totals_by_period:
            print(f"   ✓ Product totals available for {len(product_totals_by_period)} periods")
            # Show sample
            sample_periods = sorted(product_totals_by_period.keys(), reverse=True)[:3]
            for p in sample_periods:
                print(f"      {p}: ${product_totals_by_period[p]/1e9:.2f}B from products")

    # Track if any smart matches were used (for footnote)
    smart_matches_used = []

    # Track anomalous YoY values (likely from restructuring data issues)
    anomalies_detected = []

    # Pre-compute segment totals per quarter to detect data quality issues
    # NOTE: quarters_with_bad_data will be populated AFTER segment_totals_by_period is computed
    # This is done below after the per-period axis detection
    quarters_with_bad_data = set()

    # Compute segment totals per quarter using PER-PERIOD axis detection
    # This handles cases where different filings (10-K vs 10-Q) use different axes
    # and segment renames cause old axes to have missing segments
    # Key insight: each period independently selects its best-reconciling axis
    segment_totals_by_period = {}
    axis_used_by_period = {}  # Track which axis was used for each period (for debugging)

    # Get all unique periods that have segment data
    all_segment_periods = set()
    for seg_key, periods_data in all_segment_data.items():
        if not seg_key.endswith('|OI'):
            all_segment_periods.update(periods_data.keys())

    # For each period, find the best axis and sum its segments
    for period in all_segment_periods:
        # Get consolidated revenue for this period (quarterly)
        consol_rev = consolidated_revenue_quarterly.get(period, 0)

        # Find best axis for this specific period
        period_best_axis, period_segments, variance = get_best_axis_for_period(
            all_segment_data, period, consol_rev, axis_priority_map, fiscal_year_end,
            use_subsegments=use_subsegments
        )

        if period_segments:
            # Apply rollup detection to remove obvious totals (e.g., "Total Products")
            if consol_rev > 0:
                period_segments_filtered = detect_rollup_segments(
                    period_segments, consol_rev, tolerance_pct=5
                )
            else:
                period_segments_filtered = period_segments

            # Sum the filtered segments for this period
            segment_totals_by_period[period] = sum(period_segments_filtered.values())
            axis_used_by_period[period] = period_best_axis

    # Fallback: for periods with no per-period axis match, use the global best_axis
    # This handles edge cases where per-period detection fails
    for segment_name in filtered_segments.keys():
        segment_key_with_axis = None
        for key in all_segment_data.keys():
            if key.startswith(f"{segment_name}|") and not key.endswith("|OI"):
                segment_key_with_axis = key
                break

        if segment_key_with_axis:
            revenue_series = convert_cumulative_to_quarterly(
                all_segment_data[segment_key_with_axis], fiscal_year_end
            )

            for period, revenue in revenue_series.items():
                # Only add if this period wasn't already handled by per-period detection
                if period not in segment_totals_by_period and revenue > 0:
                    segment_totals_by_period[period] = segment_totals_by_period.get(period, 0) + revenue

    # Enhanced fallback: Use product revenue totals when segment data isn't available
    # This handles cases like post-spinoff where segments disappear but products continue
    if product_totals_by_period:
        periods_added_from_products = []
        for period, product_total in product_totals_by_period.items():
            # Only use product total if we don't have segment data for this period
            if period not in segment_totals_by_period and product_total > 0:
                segment_totals_by_period[period] = product_total
                periods_added_from_products.append(period)

        if periods_added_from_products:
            print(f"\n📊 Enhanced consolidated revenue using product totals:")
            print(f"   ✓ Added {len(periods_added_from_products)} periods from product aggregation")
            for p in sorted(periods_added_from_products, reverse=True)[:3]:
                print(f"      {p}: ${segment_totals_by_period[p]/1e9:.2f}B (from {len(product_revenue_summary)} products)")

    # Detect if we're dealing with annual-only segment data (e.g., IFRS 20-F filers)
    # For annual-only reporters, the per-period vs global axis validation is overly strict
    # and causes false positive anomalies. Skip validation in this case.
    total_segment_facts_with_duration = 0
    annual_segment_facts = 0  # Facts with ~365 day durations
    for seg_key, periods_data in all_segment_data.items():
        if not seg_key.endswith('|OI'):
            for period_data in periods_data.values():
                if isinstance(period_data, dict) and period_data.get('duration') is not None:
                    total_segment_facts_with_duration += 1
                    if 350 <= period_data['duration'] <= 380:  # ~365 days (annual)
                        annual_segment_facts += 1

    is_annual_only_segments = False
    if total_segment_facts_with_duration > 0:
        annual_pct = (annual_segment_facts / total_segment_facts_with_duration) * 100
        is_annual_only_segments = annual_pct >= 70  # 70%+ of facts are annual
        if is_annual_only_segments:
            print(f"📅 Detected annual-only segment reporting ({annual_pct:.1f}% of facts are annual)")
            print(f"   Skipping segment reconciliation validation (designed for quarterly reporters)")

    # Now populate quarters_with_bad_data by comparing displayed segments to segment_totals_by_period
    # This detects when the segments shown (from filtered_segments/global best axis) don't match
    # the actual segment totals used for consolidated revenue (from per-period axis detection)
    # SKIP this validation for annual-only reporters (IFRS 20-F filers)
    if not is_annual_only_segments:
        for period in periods_to_display:
            period_total = segment_totals_by_period.get(period, 0)
            if period_total <= 0:
                continue

            # Sum segments from filtered_segments (global best axis) for this period
            displayed_segment_total = 0
            for segment in filtered_segments.keys():
                segment_key_with_axis = None
                for key in all_segment_data.keys():
                    if key.startswith(f"{segment}|") and not key.endswith("|OI"):
                        segment_key_with_axis = key
                        break
                if segment_key_with_axis:
                    revenue_series = convert_cumulative_to_quarterly(
                        all_segment_data[segment_key_with_axis], fiscal_year_end
                    )
                    displayed_segment_total += revenue_series.get(period, 0)

            # If displayed segments don't cover most of the period total, flag it
            # This happens when the global best axis doesn't have all segments for this period
            pct_coverage = (displayed_segment_total / period_total) * 100 if period_total > 0 else 0
            if pct_coverage < 85 or pct_coverage > 115:
                quarter_label = get_quarter_label(period, fiscal_year_end)
                quarters_with_bad_data.add(quarter_label)

    def process_cf_facts(facts_list: List[Dict[str, Any]], fiscal_year_end: str) -> Dict[str, float]:
        """Convert cumulative cash flow facts to quarterly values.

        Processes XBRL cash flow facts by converting cumulative YTD values to
        quarterly values. For annual (10-K) facts, derives Q4 = Annual - Q3 YTD.

        Args:
            facts_list: List of cash flow fact dictionaries with keys:
                       'end_date', 'duration', 'value', 'start_date'
            fiscal_year_end: Fiscal year end in MMDD format (e.g., "1231")

        Returns:
            Dictionary mapping period end dates to quarterly cash flow values
        """
        # Group all facts by period, keeping all durations for Q4 derivation
        all_facts_by_period = defaultdict(list)
        for fact in facts_list:
            period = fact.get('end_date', '')
            if not period:
                continue
            all_facts_by_period[period].append(fact)

        # Separate facts into quarterly vs annual vs cumulative
        quarterly_facts = {}   # period -> value (60-120 day duration)
        annual_facts = {}      # period -> value (>300 day duration, from 10-K)
        cumulative_facts = {}  # period -> {duration: value} (for YTD subtraction)

        for period, facts in all_facts_by_period.items():
            for fact in facts:
                duration = fact.get('duration')
                value = fact.get('value', 0)
                if value == 0:
                    continue

                if duration and 60 <= duration <= 120:
                    # Prefer quarterly facts (most granular)
                    if period not in quarterly_facts or abs(value) > abs(quarterly_facts[period]):
                        quarterly_facts[period] = value
                elif duration and duration > 300:
                    # Annual facts from 10-K
                    annual_facts[period] = value
                elif duration and 150 <= duration <= 300:
                    # Cumulative YTD facts (H1 or 9-month)
                    if period not in cumulative_facts or duration > cumulative_facts[period].get('duration', 0):
                        cumulative_facts[period] = {'value': value, 'duration': duration}

        # Start with quarterly facts
        quarterly_values = dict(quarterly_facts)

        # For annual periods (Q4) without quarterly data, derive Q4 = Annual - Q3 YTD
        for annual_period, annual_value in annual_facts.items():
            if annual_period in quarterly_values:
                continue  # Already have quarterly data

            annual_quarter = get_quarter_label(annual_period, fiscal_year_end)
            if not annual_quarter or 'Q4' not in annual_quarter:
                continue

            # Find Q3 cumulative (9-month YTD) for same fiscal year
            fiscal_year_match = annual_quarter.replace('Q4', 'Q3')
            q3_cumulative = 0

            for cum_period, cum_info in cumulative_facts.items():
                cum_quarter = get_quarter_label(cum_period, fiscal_year_end)
                if cum_quarter == fiscal_year_match and cum_info.get('duration', 0) >= 250:
                    q3_cumulative = cum_info['value']
                    break

            if q3_cumulative != 0:
                q4_value = annual_value - q3_cumulative
                # Verify Q4 is reasonable (same sign as annual, not larger)
                if annual_value != 0 and abs(q4_value) <= abs(annual_value):
                    quarterly_values[annual_period] = q4_value
                else:
                    quarterly_values[annual_period] = annual_value  # Fallback to annual
            else:
                quarterly_values[annual_period] = annual_value  # No cumulative data available

        return quarterly_values

    # Process each cash flow metric
    cf_quarterly = {
        'operating_cash_flow': process_cf_facts(consolidated_cf_data.get('operating_cash_flow', []), fiscal_year_end),
        'dividends': process_cf_facts(consolidated_cf_data.get('dividends', []), fiscal_year_end),
        'share_buybacks': process_cf_facts(consolidated_cf_data.get('share_buybacks', []), fiscal_year_end),
        'capex': process_cf_facts(consolidated_cf_data.get('capex', []), fiscal_year_end)
    }

    # Check if we have any cash flow data
    has_cf_data = any(len(v) > 0 for v in cf_quarterly.values())

    # Display consolidated quarterly totals (sum of segments)
    # Also build data structure for the view template
    consolidated_table, consolidated_quarters = format_consolidated_revenue_table(
        periods_to_display=periods_to_display,
        segment_totals_by_period=segment_totals_by_period,
        quarter_label_to_period=quarter_label_to_period,
        fiscal_year_end=fiscal_year_end,
        get_quarter_label_func=get_quarter_label,
        get_prior_year_quarter_label_func=get_prior_year_quarter_label
    )
    print("\n" + consolidated_table)

    # Extract quarters_data_temp for capital allocation table
    quarters_data_temp = [
        {
            'period': q['period'],
            'quarter_label': q['quarter'],
            'revenue': q['revenue']
        }
        for q in consolidated_quarters
    ]

    # Display Capital Allocation section if we have cash flow data
    capital_allocation_quarters = []
    if has_cf_data:
        capital_allocation_table, capital_allocation_quarters = format_capital_allocation_table(
            quarters_data_temp=quarters_data_temp,
            cf_quarterly=cf_quarterly
        )
        print("\n" + capital_allocation_table)

    # Format segment revenue
    segment_revenue_summary = {}
    if filtered_segments:
        print("\n" + "="*120)
        print("QUARTERLY TIME SERIES - BUSINESS SEGMENTS")
        print("="*120)

        for segment in sorted(filtered_segments.keys()):
            # Get revenue and operating income time series (cumulative)
            revenue_series_cumulative = {}
            oi_series_cumulative = {}

            # Find the segment key in all_segment_data (with axis)
            segment_key_with_axis = None
            for key in all_segment_data.keys():
                if key.startswith(f"{segment}|") and not key.endswith("|OI"):
                    segment_key_with_axis = key
                    break

            rd_series_cumulative = {}

            if segment_key_with_axis:
                revenue_series_cumulative = all_segment_data[segment_key_with_axis]

                # Find corresponding operating income and R&D
                axis_part = segment_key_with_axis.split('|')[1] if '|' in segment_key_with_axis else ''
                oi_key = f"{segment}|{axis_part}|OI"
                rd_key = f"{segment}|{axis_part}|RD"
                if oi_key in all_operating_income_data:
                    oi_series_cumulative = all_operating_income_data[oi_key]
                if rd_key in all_rd_data:
                    rd_series_cumulative = all_rd_data[rd_key]

            # Convert cumulative to quarterly
            revenue_series = convert_cumulative_to_quarterly(revenue_series_cumulative, fiscal_year_end)
            oi_series = convert_cumulative_to_quarterly(oi_series_cumulative, fiscal_year_end)
            rd_series = convert_cumulative_to_quarterly(rd_series_cumulative, fiscal_year_end)

            # Format and display segment revenue table
            segment_table, segment_summary = format_segment_revenue_table(
                segment=segment,
                periods_to_display=periods_to_display,
                revenue_series=revenue_series,
                oi_series=oi_series,
                rd_series=rd_series,
                segment_totals_by_period=segment_totals_by_period,
                consolidated_revenue_quarterly=consolidated_revenue_quarterly,
                quarter_label_to_period=quarter_label_to_period,
                segment_fingerprints=segment_fingerprints,
                segment_match_cache=segment_match_cache,
                quarters_with_bad_data=quarters_with_bad_data,
                fiscal_year_end=fiscal_year_end,
                get_quarter_label_func=get_quarter_label,
                calculate_yoy_func=calculate_yoy_with_smart_matching,
                smart_matches_used=smart_matches_used,
                anomalies_detected=anomalies_detected
            )
            print(segment_table)

            segment_revenue_summary[segment] = segment_summary

        # Print footnotes for smart matching and anomalies
        smart_match_footnote = format_smart_match_footnote(smart_matches_used)
        if smart_match_footnote:
            print("\n" + smart_match_footnote)

        anomaly_footnote = format_anomaly_footnote(anomalies_detected, smart_matches_used)
        if anomaly_footnote:
            print("\n" + anomaly_footnote)

    # Format geographic revenue
    geographic_revenue_summary = {}
    if filtered_geographies:
        print("\n" + "="*120)
        print("QUARTERLY TIME SERIES - GEOGRAPHIC REGIONS")
        print("="*120)

        for geography in sorted(filtered_geographies.keys()):
            # Get revenue and operating income time series (cumulative)
            revenue_series_cumulative = {}
            oi_series_cumulative = {}

            # Find the geography key in all_geography_data (with axis)
            geography_key_with_axis = None
            for key in all_geography_data.keys():
                if key.startswith(f"{geography}|") and not key.endswith("|OI"):
                    geography_key_with_axis = key
                    break

            # Debug: Log geography key matching
            if not geography_key_with_axis:
                print(f"   ⚠️  No data key found for geography '{geography}'")
                # Show what keys exist for debugging
                matching_keys = [k for k in all_geography_data.keys() if geography.lower() in k.lower()]
                if matching_keys:
                    print(f"      Potential matches: {matching_keys[:2]}")

            if geography_key_with_axis:
                revenue_series_cumulative = all_geography_data[geography_key_with_axis]
                print(f"   ✓ Geography '{geography}' mapped to key '{geography_key_with_axis}' with {len(revenue_series_cumulative)} periods")
                # Debug: Show sample values
                if revenue_series_cumulative:
                    sample_periods = sorted(list(revenue_series_cumulative.keys()))[:3]
                    sample_values = [revenue_series_cumulative[p]['value'] for p in sample_periods]
                    print(f"      Sample periods: {sample_periods}")
                    print(f"      Sample values: {['${:,.0f}'.format(v) for v in sample_values]}")

                # Find corresponding operating income
                axis_part = geography_key_with_axis.split('|')[1] if '|' in geography_key_with_axis else ''
                oi_key = f"{geography}|{axis_part}|OI"
                if oi_key in all_operating_income_data:
                    oi_series_cumulative = all_operating_income_data[oi_key]

            # Convert cumulative to quarterly
            revenue_series = convert_cumulative_to_quarterly(revenue_series_cumulative, fiscal_year_end)
            oi_series = convert_cumulative_to_quarterly(oi_series_cumulative, fiscal_year_end)

            # Debug: Show quarterly conversion result
            print(f"      After conversion: {len(revenue_series)} quarterly periods")
            if revenue_series:
                sample_q_periods = sorted(list(revenue_series.keys()))[:3]
                sample_q_values = [revenue_series[p] for p in sample_q_periods]
                print(f"      Quarterly periods: {sample_q_periods}")
                print(f"      Quarterly values: {['${:,.0f}'.format(v) for v in sample_q_values]}")

            # Format and display geographic revenue table
            geography_table, geography_summary = format_geographic_revenue_table(
                geography=geography,
                periods_to_display=periods_to_display,
                revenue_series=revenue_series,
                oi_series=oi_series,
                consolidated_revenue_quarterly=consolidated_revenue_quarterly,
                quarter_label_to_period=quarter_label_to_period,
                fiscal_year_end=fiscal_year_end,
                get_quarter_label_func=get_quarter_label,
                get_prior_year_quarter_label_func=get_prior_year_quarter_label,
                anomalies_detected=anomalies_detected
            )
            print(geography_table)

            geographic_revenue_summary[geography] = geography_summary

        # Print footnote if anomalies were detected in geographies
        geo_anomalies = [a for a in anomalies_detected if a['segment'] in filtered_geographies]
        if geo_anomalies:
            geo_anomaly_footnote = format_anomaly_footnote(geo_anomalies, [])
            print("\n" + geo_anomaly_footnote)

    # Add hierarchy information to geographic data
    geographic_revenue_summary = detect_geographic_hierarchy(geographic_revenue_summary)

    # Display Stock Valuation section if we have data
    if stock_valuation and stock_valuation.get('current_price'):
        valuation_section = format_stock_valuation_section(stock_valuation)
        print("\n" + valuation_section)

    # Print Analyst Estimates section
    if analyst_estimates and (analyst_estimates.get('consensus_eps') or analyst_estimates.get('target_mean')):
        estimates_section = format_analyst_estimates_section(analyst_estimates, stock_valuation)
        print("\n" + estimates_section)

    # Print Peer Comparison section
    if peer_comparison and (peer_comparison.get('valuation') or peer_comparison.get('peer_tickers')):
        peer_section = format_peer_comparison_section(peer_comparison)
        print("\n" + peer_section)

    # Print Summary section
    summary_section = format_summary_section(
        company_name=company_name,
        ticker=ticker,
        cik=cik,
        latest_period=latest_period,
        filtered_segments=filtered_segments,
        filtered_geographies=filtered_geographies,
        periods_to_display=periods_to_display,
        all_periods_sorted=all_periods_sorted,
        dimensional_facts_count=dimensional_facts_count
    )
    print("\n" + summary_section)

    # Deep dive into SEC filing narrative (if requested)
    deep_dive_result = None
    if deep_dive_concepts:
        # Build quarters list from target_filings for deep dive
        # Only include filings for periods being displayed (not extra YoY data)
        # Format: (accession, period_end, form, primary_doc)
        periods_to_display_set = set(periods_to_display)
        quarters_list = [(f['accession'], f['report_date'], f['form'], f['primary_doc'])
                         for f in target_filings
                         if f['report_date'] in periods_to_display_set]

        segment_names = list(filtered_segments.keys()) if filtered_segments else []
        deep_dive_result = perform_deep_dive(
            cik=cik,
            quarters=quarters_list,
            concepts=deep_dive_concepts,
            segment_names=segment_names
        )
        deep_dive_summary = format_deep_dive_summary(deep_dive_result)
        print("\n" + deep_dive_summary)
        sys.stdout.flush()  # Ensure output is flushed to UI

    # Determine segment axis type for display purposes
    segment_axis_type = "business_segments"  # default
    if best_axis and 'ProductsAndServicesAxis' in best_axis:
        segment_axis_type = "products"
    elif best_axis and ('CoreTherapeuticArea' in best_axis or 'TherapeuticArea' in best_axis):
        segment_axis_type = "therapeutic_areas"
    elif best_axis and 'BrandsAxis' in best_axis:
        segment_axis_type = "brands"
    elif best_axis and 'ProductPortfolioAxis' in best_axis:
        segment_axis_type = "product_portfolio"

    # Build return dictionary
    result = {
        'company': company_name,
        'ticker': ticker.upper(),
        'cik': cik,
        'latest_period': latest_period,
        'quarters_requested': quarters,
        'quarters_displayed': len(periods_to_display),
        'quarters_fetched': len(all_periods_sorted),
        'consolidated_quarters': consolidated_quarters,
        'capital_allocation': capital_allocation_quarters,
        'segment_revenue': segment_revenue_summary,
        'geographic_revenue': geographic_revenue_summary,
        'product_revenue': product_revenue_summary if product_revenue_summary else None,
        'reconciliation': reconciliation,
        'stock_valuation': stock_valuation,
        'analyst_estimates': analyst_estimates,
        'peer_comparison': peer_comparison,
        'total_segments': len(filtered_segments),
        'total_geographies': len(filtered_geographies),
        'total_products': len(product_revenue_summary) if product_revenue_summary else 0,
        'dimensional_facts_count': dimensional_facts_count,
        'segment_axis_used': best_axis,
        'segment_axis_type': segment_axis_type,
        'product_axis_used': product_axis if product_axis else None,
        'products_hierarchically_linked': len(product_segments_mapping) > 0 if product_revenue_summary else None,
        'segment_axis_fallback_used': fallback_attempted if 'fallback_attempted' in locals() else False
    }

    # Add deep dive results if available
    if deep_dive_result:
        result['deep_dive'] = deep_dive_result

    return result



































def _build_cli_mcp_funcs():
    """Build MCP functions dict for CLI execution."""
    import importlib.util

    def _load_mcp(name, path):
        spec = importlib.util.spec_from_file_location(name, path,
            submodule_search_locations=[os.path.dirname(path)])
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod  # Register before exec so relative imports work
        try:
            spec.loader.exec_module(mod)
        except Exception:
            sys.modules.pop(name, None)
            raise
        return mod

    sec_mod = _load_mcp('sec_edgar_mcp', os.path.join(_claude_dir, 'mcp', 'servers', 'sec_edgar_mcp', '__init__.py'))
    fin_mod = _load_mcp('financials_mcp', os.path.join(_claude_dir, 'mcp', 'servers', 'financials_mcp', '__init__.py'))

    def sec_get_cik_wrapper(**kw):
        return sec_mod.get_company_cik(**kw)

    def sec_get_filing_wrapper(**kw):
        return sec_mod.get_company_submissions(**kw)

    def sec_search_by_sic_wrapper(*args, **kw):
        return sec_mod.search_companies_by_sic(*args, **kw)

    def financials_lookup_wrapper(**kw):
        return fin_mod.financial_intelligence(**kw)

    def disfold_get_peers_wrapper(company_name, max_peers=10, us_only=True):
        return fin_mod.get_peers_with_tickers(company_name=company_name, max_peers=max_peers, us_only=us_only)

    return {
        'sec_get_cik': sec_get_cik_wrapper,
        'sec_get_filing': sec_get_filing_wrapper,
        'sec_search_by_sic': sec_search_by_sic_wrapper,
        'financials_lookup': financials_lookup_wrapper,
        'disfold_get_peers': disfold_get_peers_wrapper,
    }


if __name__ == "__main__":
    # Ticker parameter is REQUIRED (no default)
    if len(sys.argv) < 2:
        print("Error: Ticker symbol required")
        print("Usage: python3 get_company_us_earnings.py <TICKER> [QUARTERS] [--subsegments] [--deep-dive CONCEPT[,CONCEPT2,...]]")
        print("\nExamples:")
        print("  python3 get_company_us_earnings.py JNJ")
        print("  python3 get_company_us_earnings.py ABT 4")
        print("  python3 get_company_us_earnings.py MDT 8 --subsegments")
        print("  python3 get_company_us_earnings.py MDT 8 --subsegments --deep-dive PFA")
        print("  python3 get_company_us_earnings.py MDT 4 --deep-dive \"PFA,ablation,electrophysiology\"")
        print("\nDescription:")
        print("  Extracts segment and geographic revenue data from SEC EDGAR XBRL filings")
        print("  for any publicly traded company using dimensional analysis.")
        print("  Includes revenue reconciliation to verify data completeness.")
        print("\nOptions:")
        print("  --subsegments: Extract division-level data (more granular than segments)")
        print("  --deep-dive CONCEPT: Search SEC filing narrative text for concept/keyword")
        print("                       and link mentions to segment financial data.")
        print("                       Supports comma-separated list for multiple concepts")
        print("                       (downloads filings once, searches all concepts)")
        sys.exit(1)

    ticker = sys.argv[1].upper()

    # Parse optional arguments
    quarters = 8
    use_subsegments = False
    deep_dive_concepts = None

    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--subsegments':
            use_subsegments = True
            i += 1
        elif arg == '--deep-dive':
            # Next argument should be the concept(s) - can be comma-separated
            if i + 1 < len(sys.argv):
                # Split by comma and strip whitespace
                deep_dive_concepts = [c.strip() for c in sys.argv[i + 1].split(',')]
                i += 2
            else:
                print("Error: --deep-dive requires a concept argument")
                sys.exit(1)
        elif arg.isdigit():
            quarters = int(arg)
            i += 1
        else:
            i += 1

    # BioClaw: mcp_funcs=None triggers auto-init via McpClient
    result = get_company_us_earnings(
        ticker=ticker,
        quarters=quarters,
        use_subsegments=use_subsegments,
        deep_dive_concepts=deep_dive_concepts,
    )

    if 'error' in result:
        print(f"Error: {result['error']}")
        sys.exit(1)

    # Display key metrics
    key_metrics = format_main_output_key_metrics(result)
    print(key_metrics)

    # Deep dive is now handled inside get_company_us_earnings() function
    # Output was already printed during function execution