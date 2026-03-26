#!/usr/bin/env python3
"""
Market data collection for company SWOT analysis.

This module provides functions for:
- Getting market performance data (market cap, P/E, stock price)
- Peer comparison analysis
"""

import re
from typing import Any, Dict, List, Optional

# All MCP functions are now accessed via mcp_funcs parameter
# No direct imports from mcp.servers.* allowed

from sec_lookup import lookup_company_in_sec_tickers
from ticker_utils import find_ticker


def _find_ticker_for_market(company_name: str, mcp_funcs: Dict[str, Any] = None) -> Optional[str]:
    """Find stock ticker using available lookup methods."""
    if not mcp_funcs:
        return None

    search_companies = mcp_funcs.get('sec_search_companies')
    get_company_cik = mcp_funcs.get('sec_get_cik')

    return find_ticker(
        company_name,
        lookup_company_in_sec_tickers_fn=lookup_company_in_sec_tickers,
        search_companies_fn=search_companies,
        get_company_cik_fn=get_company_cik
    )


def get_market_performance(company_name: str, mcp_funcs: Dict[str, Any] = None) -> Dict[str, Any]:
    """Collect market data from Yahoo Finance.

    Returns:
        dict: market_cap, stock_price, pe_ratio, success, error (if any)
    """
    print(f"\n📈 Collecting market data for {company_name}...")

    if not mcp_funcs:
        return {'market_cap': None, 'stock_price': None, 'pe_ratio': None, 'success': False, 'error': 'No MCP functions provided'}

    financial_intelligence = mcp_funcs.get('financials_lookup')
    if not financial_intelligence:
        return {'market_cap': None, 'stock_price': None, 'pe_ratio': None, 'success': False, 'error': 'Financial intelligence function not available'}

    try:
        # Find ticker dynamically - no hardcoded map!
        symbol = _find_ticker_for_market(company_name, mcp_funcs=mcp_funcs)
        if not symbol:
            return {'market_cap': None, 'stock_price': None, 'pe_ratio': None, 'success': False, 'error': f'Could not find ticker for {company_name}'}
        print(f"   Using ticker: {symbol}")
        result = financial_intelligence(method='stock_summary', symbol=symbol)

        market_cap = None
        stock_price = None

        # Handle dict response with 'text' key (markdown format)
        text = None
        if isinstance(result, dict):
            text = result.get('text', '')
        elif isinstance(result, str):
            text = result

        if text:
            # Parse Enterprise Value (Market Cap often N/A, use EV as proxy)
            ev_match = re.search(r'Enterprise\s+Value[:\*\s]+(\d+\.?\d*)\s*([BMK])?\s*USD', text, re.I)
            mcap_match = re.search(r'Market\s+Cap[:\*\s]+(\d+\.?\d*)\s*([BMK])?\s*USD', text, re.I)
            eps_match = re.search(r'Trailing\s+EPS[:\*\s]+(\d+\.?\d*)\s*USD', text, re.I)

            # Use EV if Market Cap not available
            cap_match = mcap_match or ev_match
            if cap_match:
                val = float(cap_match.group(1))
                unit = cap_match.group(2)
                market_cap = val * (1e9 if unit == 'B' else 1e6 if unit == 'M' else 1e3 if unit == 'K' else 1)

            # Extract P/E ratio - prefer trailing P/E over forward P/E
            pe_ratio = None
            trailing_pe_match = re.search(r'Trailing\s+P/E[:\*\s]+(\d+\.?\d*)', text, re.I)
            forward_pe_match = re.search(r'Forward\s+P/E[:\*\s]+(\d+\.?\d*)', text, re.I)

            if trailing_pe_match and 'N/A' not in text[trailing_pe_match.start():trailing_pe_match.end()+10]:
                pe_ratio = float(trailing_pe_match.group(1))
            elif forward_pe_match:
                # Only use forward P/E if it's reasonable (> 5)
                forward_pe = float(forward_pe_match.group(1))
                if forward_pe > 5:  # Sanity check - P/E < 5 is likely wrong
                    pe_ratio = forward_pe

            # Estimate stock price from EPS * P/E if available
            if eps_match and pe_ratio:
                eps = float(eps_match.group(1))
                stock_price = eps * pe_ratio

        return {'market_cap': market_cap, 'stock_price': stock_price, 'pe_ratio': pe_ratio, 'success': True}
    except Exception as e:
        return {'market_cap': None, 'stock_price': None, 'pe_ratio': None, 'success': False, 'error': str(e)}


def get_peer_comparison(company_name: str, mcp_funcs: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get peer comparison data from Yahoo Finance.

    Returns:
        dict: peers (list), peer_count, success, error (if any)
    """
    print(f"\n👥 Getting peer comparison for {company_name}...")

    if not mcp_funcs:
        return {'peers': [], 'peer_count': 0, 'success': False, 'error': 'No MCP functions provided'}

    financial_intelligence = mcp_funcs.get('financials_lookup')
    if not financial_intelligence:
        return {'peers': [], 'peer_count': 0, 'success': False, 'error': 'Financial intelligence function not available'}

    try:
        # Find ticker using imported function from ticker_utils
        symbol = _find_ticker_for_market(company_name, mcp_funcs=mcp_funcs)
        if not symbol:
            return {'peers': [], 'peer_count': 0, 'success': False, 'error': f'Could not find ticker for {company_name}'}
        print(f"   Using ticker: {symbol}")

        result = financial_intelligence(method='stock_peers', symbol=symbol)

        peers = []
        target_pe = None
        target_market_cap = None
        text = None
        if isinstance(result, dict):
            text = result.get('text', '')
        elif isinstance(result, str):
            text = result

        if text:
            # Parse peer data from markdown table format
            # Format: | Company | Market Cap (B) | P/E Ratio | Forward P/E | PEG Ratio | P/B Ratio |
            lines = text.split('\n')
            in_valuation_table = False
            header_parts = []

            for line in lines:
                # Detect valuation metrics table
                if 'Valuation Metrics' in line:
                    in_valuation_table = True
                    continue
                if 'Growth Metrics' in line:
                    in_valuation_table = False
                    continue

                if '|' in line and in_valuation_table:
                    parts = [p.strip() for p in line.split('|') if p.strip()]

                    # Skip separator lines
                    if parts and parts[0].startswith('-'):
                        continue

                    # Capture header row
                    if parts and ('Company' in parts[0] or 'Ticker' in parts[0]):
                        header_parts = parts
                        continue

                    if len(parts) >= 3:
                        company_col = parts[0]
                        # Extract ticker - handle **NVO** format for target company
                        ticker_match = re.search(r'\*\*(\w+)\*\*', company_col)
                        if ticker_match:
                            ticker = ticker_match.group(1)
                            is_target = True
                        else:
                            ticker = company_col
                            is_target = False

                        # Skip header-like rows
                        if ticker and ticker.upper() not in ('TICKER', 'COMPANY') and not ticker.startswith('-'):
                            peer_info = {'ticker': ticker}

                            # Parse Market Cap (B) - usually column 2
                            if len(parts) > 1:
                                mcap_str = parts[1]
                                mcap_match = re.search(r'\$?([\d.]+)([BMK])?', mcap_str)
                                if mcap_match:
                                    val = float(mcap_match.group(1))
                                    unit = mcap_match.group(2) or 'B'
                                    mcap = val * (1e9 if unit == 'B' else 1e6 if unit == 'M' else 1e3)
                                    peer_info['market_cap'] = mcap
                                    if is_target:
                                        target_market_cap = mcap

                            # Parse P/E Ratio - usually column 3
                            if len(parts) > 2:
                                pe_str = parts[2]
                                pe_match = re.search(r'([\d.]+)', pe_str)
                                if pe_match and 'N/A' not in pe_str:
                                    pe = float(pe_match.group(1))
                                    peer_info['pe_ratio'] = pe
                                    if is_target:
                                        target_pe = pe

                            # Only add non-target companies as peers
                            # Also filter out non-pharma peers (AAPL, MSFT, etc.)
                            non_pharma_tickers = {'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'GOOG', 'META', 'NVDA', 'TSLA'}
                            if not is_target and ticker not in non_pharma_tickers:
                                peers.append(peer_info)

        # Get peer names for display
        peer_display = []
        for p in peers[:5]:
            name = p.get('name') or p.get('ticker', '')
            mcap = p.get('market_cap')
            if mcap:
                peer_display.append(f"{name} (${mcap/1e9:.1f}B)")
            else:
                peer_display.append(name)

        print(f"   Found {len(peers)} peers: {', '.join(peer_display)}")

        return {
            'peers': peers[:10],  # Top 10 peers
            'peer_count': len(peers),
            'target_pe': target_pe,
            'target_market_cap': target_market_cap,
            'success': True
        }
    except Exception as e:
        print(f"   Error getting peers: {e}")
        return {'peers': [], 'peer_count': 0, 'success': False, 'error': str(e)}
