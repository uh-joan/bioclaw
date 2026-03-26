"""Dynamic peer company lookup using Disfold and SEC SIC codes.

Primary strategy (Disfold):
1. Get company's competitors from Disfold (market-cap ranked, same industry)
2. Resolve ticker symbols for each competitor
3. Return US-traded peers with their market caps

Fallback strategy (SEC SIC codes):
1. Get company's SIC code from SEC EDGAR
2. Find other companies with the same SIC code via SEC browse-edgar API
3. Validate and filter by industry

No hardcoded peer lists - all peer data comes from external APIs at runtime.
"""

import sys
import os
import re
import time
import urllib.request
import xml.etree.ElementTree as ET

# Path setup for imports
_this_file = os.path.abspath(__file__)
_scripts_dir = os.path.dirname(_this_file)
_skill_dir = os.path.dirname(_scripts_dir)
_skills_dir = os.path.dirname(_skill_dir)
_claude_dir = os.path.dirname(_skills_dir)
sys.path.insert(0, _claude_dir)

# All MCP functions are now accessed via mcp_funcs parameter
# No direct imports from mcp.servers.* allowed


def _local_search_companies_by_sic(sic_code: str, max_results: int = 40, mcp_funcs: dict = None) -> dict:
    """Local implementation of SEC SIC search as fallback."""
    SEC_RATE_LIMIT_DELAY = 0.17

    if not sic_code or len(sic_code) < 2:
        return {'companies': [], 'sic_code': sic_code, 'total_found': 0}

    url = (
        f"https://www.sec.gov/cgi-bin/browse-edgar"
        f"?action=getcompany&SIC={sic_code}&type=10-K&dateb=&owner=include"
        f"&count={max_results}&output=atom"
    )

    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'CompanyEarningsBot/1.0 (support@example.com)',
                'Accept': 'application/atom+xml',
            }
        )
        time.sleep(SEC_RATE_LIMIT_DELAY)

        with urllib.request.urlopen(req, timeout=15) as response:
            xml_data = response.read().decode('utf-8')

        xml_data = re.sub(r'xmlns[^"]*"[^"]*"', '', xml_data)
        root = ET.fromstring(xml_data)

        companies = []
        for entry in root.findall('.//entry'):
            company_info = entry.find('.//company-info')
            if company_info is None:
                continue

            cik_elem = company_info.find('cik')
            name_elem = company_info.find('name')
            sic_elem = company_info.find('sic')
            state_elem = company_info.find('state')

            cik = cik_elem.text.strip() if cik_elem is not None and cik_elem.text else None
            name = name_elem.text.strip() if name_elem is not None and name_elem.text else None
            sic = sic_elem.text.strip() if sic_elem is not None and sic_elem.text else None
            state = state_elem.text.strip() if state_elem is not None and state_elem.text else None

            if not cik or not name:
                continue

            ticker = None
            try:
                if mcp_funcs:
                    get_submissions = mcp_funcs.get('sec_get_filing')
                    if get_submissions:
                        submissions = get_submissions(cik_or_ticker=cik)
                        tickers = submissions.get('tickers', [])
                        if tickers:
                            ticker = tickers[0]
            except Exception:
                pass

            companies.append({
                'cik': cik,
                'name': name,
                'ticker': ticker,
                'sic': sic,
                'state': state,
            })

        return {'companies': companies, 'sic_code': sic_code, 'total_found': len(companies)}
    except Exception as e:
        return {'companies': [], 'sic_code': sic_code, 'total_found': 0, 'error': str(e)}


def get_peers_from_sec_sic(sic_code: str, exclude_ticker: str, max_peers: int = 7,
                           use_broad_search: bool = True, mcp_funcs: dict = None) -> list:
    """Get peer company tickers from SEC using SIC code search.

    This is the primary method for finding peer companies - uses SEC's official
    SIC (Standard Industrial Classification) codes which are more reliable than
    Yahoo Finance's peer suggestions.

    Strategy:
    1. First search by exact 4-digit SIC code (most specific)
    2. If use_broad_search=True, also search related SIC codes in the same major group
       (e.g., for 3845, also search 3841, 3842, etc. in the 384x range)
    3. Return combined unique peer tickers

    Args:
        sic_code: 4-digit SIC code (e.g., '2834')
        exclude_ticker: Main company ticker to exclude
        max_peers: Maximum number of peer tickers to return
        use_broad_search: If True, also search related SIC codes for more coverage

    Returns:
        list: List of peer ticker symbols
    """
    exclude_upper = exclude_ticker.upper() if exclude_ticker else None
    all_peer_tickers = []
    seen_tickers = set()

    # Search function helper
    def search_sic(code: str, max_results: int) -> list:
        if mcp_funcs:
            sec_sic_search = mcp_funcs.get('sec_search_by_sic')
            if sec_sic_search:
                result = sec_sic_search(code, max_results=max_results)
            else:
                result = _local_search_companies_by_sic(code, max_results=max_results, mcp_funcs=mcp_funcs)
        else:
            result = _local_search_companies_by_sic(code, max_results=max_results, mcp_funcs=mcp_funcs)
        return result.get('companies', [])

    def add_companies(companies: list):
        for company in companies:
            ticker = company.get('ticker')
            if ticker and ticker.upper() not in seen_tickers:
                if not exclude_upper or ticker.upper() != exclude_upper:
                    all_peer_tickers.append(ticker)
                    seen_tickers.add(ticker.upper())

    # First: Search by exact 4-digit SIC code
    companies = search_sic(sic_code, max_results=max_peers * 5)
    add_companies(companies)

    # Second: If broad search enabled, search related SIC codes in the same 3-digit group
    # For medical devices: 3841, 3842, 3844, 3845 are all related
    if use_broad_search and sic_code and len(sic_code) >= 3:
        sic_3digit = sic_code[:3]  # e.g., '384' from '3845'

        # Search a few related SIC codes (limited to avoid slow API calls)
        for last_digit in range(10):
            related_sic = f"{sic_3digit}{last_digit}"
            if related_sic != sic_code:
                companies = search_sic(related_sic, max_results=30)
                add_companies(companies)
                # Stop after collecting enough candidates
                if len(all_peer_tickers) >= max_peers * 2:
                    break

    # Return up to max_peers (but typically we'll filter by market cap later)
    return all_peer_tickers[:max_peers]


def get_company_sic(ticker: str, mcp_funcs: dict = None) -> dict:
    """Get SIC code and industry description for a company from SEC EDGAR.

    Args:
        ticker: Stock ticker symbol (e.g., 'ABT', 'JNJ')
        mcp_funcs: Dictionary of MCP functions

    Returns:
        dict: {
            'sic': str (e.g., '2834'),
            'sic_description': str (e.g., 'Pharmaceutical Preparations'),
            'company_name': str
        }
    """
    try:
        if not mcp_funcs:
            return {'sic': None, 'sic_description': None, 'company_name': None, 'error': 'mcp_funcs required'}

        get_submissions = mcp_funcs.get('sec_get_filing')
        if not get_submissions:
            return {'sic': None, 'sic_description': None, 'company_name': None, 'error': 'sec_get_filing not available'}

        submissions = get_submissions(cik_or_ticker=ticker.upper())
        return {
            'sic': submissions.get('sic'),
            'sic_description': submissions.get('sicDescription'),
            'company_name': submissions.get('name'),
        }
    except Exception as e:
        return {'sic': None, 'sic_description': None, 'company_name': None, 'error': str(e)}


def validate_yahoo_peers(ticker: str, yahoo_peers: list, ticker_sic: str = None, mcp_funcs: dict = None) -> dict:
    """Validate Yahoo Finance peers by checking their SIC codes.

    Filters out peers that are in completely different industries.

    Args:
        ticker: Main company ticker
        yahoo_peers: List of peer tickers from Yahoo Finance
        ticker_sic: SIC code of the main ticker (optional, will be looked up if not provided)
        mcp_funcs: Dictionary of MCP functions

    Returns:
        dict: {
            'valid_peers': list of peer tickers in same/related industry,
            'invalid_peers': list of peer tickers in different industries,
            'peer_details': list of dicts with peer info,
            'source': 'yahoo_validated' | 'yahoo_filtered',
            'main_sic': SIC code of main ticker,
            'main_industry': Industry description
        }
    """
    ticker = ticker.upper()

    # Get main company's SIC if not provided
    if not ticker_sic:
        main_info = get_company_sic(ticker, mcp_funcs=mcp_funcs)
        ticker_sic = main_info.get('sic')
        main_industry = main_info.get('sic_description')
    else:
        main_industry = None

    if not ticker_sic:
        # Can't validate without SIC code - return unfiltered
        return {
            'valid_peers': yahoo_peers[:7] if yahoo_peers else [],
            'invalid_peers': [],
            'peer_details': [],
            'source': 'yahoo_unvalidated',
            'main_sic': None,
            'main_industry': None,
        }

    # Get the SIC major group (first 2 digits)
    main_sic_group = ticker_sic[:2]

    valid_peers = []
    invalid_peers = []
    peer_details = []

    for peer in (yahoo_peers or []):
        if peer.upper() == ticker:
            continue

        peer_info = get_company_sic(peer, mcp_funcs=mcp_funcs)
        peer_sic = peer_info.get('sic')

        if peer_sic:
            peer_sic_group = peer_sic[:2]
            # Consider valid if same 2-digit SIC group (same major industry)
            is_valid = (peer_sic_group == main_sic_group)

            peer_details.append({
                'ticker': peer,
                'sic': peer_sic,
                'sic_description': peer_info.get('sic_description'),
                'is_valid': is_valid,
            })

            if is_valid:
                valid_peers.append(peer)
            else:
                invalid_peers.append(peer)
        else:
            # No SIC found - might not be SEC filer, mark as invalid
            invalid_peers.append(peer)

    # If most Yahoo peers are invalid, the data is bad
    if len(invalid_peers) > len(valid_peers):
        source = 'yahoo_filtered'
    else:
        source = 'yahoo_validated'

    return {
        'valid_peers': valid_peers[:7],
        'invalid_peers': invalid_peers,
        'peer_details': peer_details,
        'source': source,
        'main_sic': ticker_sic,
        'main_industry': main_industry,
    }


def get_peers_from_disfold(company_name: str, ticker: str, max_peers: int = 5, mcp_funcs: dict = None) -> dict:
    """Get peer companies from Disfold (market-cap ranked, same industry).

    This is the PRIMARY method for finding peer companies. Disfold provides:
    - Competitors already ranked by market cap
    - Same industry classification
    - Ticker symbols for US-traded companies

    Args:
        company_name: Company name (e.g., 'Medtronic plc')
        ticker: Stock ticker to exclude from peers
        max_peers: Maximum number of peers to return
        mcp_funcs: Dictionary of MCP functions

    Returns:
        dict: {
            'peers': list of peer tickers,
            'peer_details': list of dicts with name, ticker, market_cap,
            'industry': Industry name,
            'source': 'disfold'
        }
    """
    if not mcp_funcs:
        return {
            'peers': [],
            'peer_details': [],
            'industry': None,
            'source': 'disfold_unavailable',
            'error': 'mcp_funcs required'
        }

    disfold_get_peers = mcp_funcs.get('disfold_get_peers')
    if not disfold_get_peers:
        return {
            'peers': [],
            'peer_details': [],
            'industry': None,
            'source': 'disfold_unavailable',
            'error': 'Disfold module not available'
        }

    try:
        # Try to get peers using company name
        result = disfold_get_peers(company_name, max_peers=max_peers + 2, us_only=True)

        if result.get('peers'):
            # Filter out the main company if it appears in peers
            ticker_upper = ticker.upper() if ticker else None
            filtered_peers = [
                p for p in result['peers']
                if p.get('ticker', '').upper() != ticker_upper
            ][:max_peers]

            return {
                'peers': [p['ticker'] for p in filtered_peers],
                'peer_details': filtered_peers,
                'industry': result.get('industry'),
                'source': 'disfold',
            }

    except Exception as e:
        return {
            'peers': [],
            'peer_details': [],
            'industry': None,
            'source': 'disfold_error',
            'error': str(e)
        }

    return {
        'peers': [],
        'peer_details': [],
        'industry': None,
        'source': 'disfold_empty',
    }


def get_peers_for_ticker(ticker: str, company_name: str = None, sic_code: str = None,
                         sic_description: str = None, yahoo_peers: list = None,
                         max_peers: int = 5, mcp_funcs: dict = None) -> dict:
    """Get peer companies for a given ticker.

    Strategy (in order of preference):
    1. Disfold: Market-cap ranked competitors from same industry (PRIMARY)
    2. Yahoo validated: Yahoo peers that pass SEC SIC validation
    3. SEC SIC search: Search SEC for companies with same SIC code (FALLBACK)

    Args:
        ticker: Stock ticker symbol (e.g., 'ABT', 'JNJ')
        company_name: Company name for Disfold lookup
        sic_code: SEC SIC code from company submissions (e.g., '2834')
        sic_description: Industry description from SEC
        yahoo_peers: List of peers from Yahoo Finance (for validation)
        max_peers: Maximum number of peers to return
        mcp_funcs: Dictionary of MCP functions

    Returns:
        dict: {
            'peers': list of peer tickers,
            'peer_details': list of dicts with peer info (if available),
            'source': 'disfold' | 'yahoo_validated' | 'sec_sic_search' | 'none',
            'sic_code': SIC code,
            'industry': Industry name
        }
    """
    ticker = ticker.upper()

    # Strategy 1: Try Disfold first (best quality - market-cap ranked peers)
    if company_name and mcp_funcs:
        disfold_result = get_peers_from_disfold(company_name, ticker, max_peers=max_peers, mcp_funcs=mcp_funcs)
        if disfold_result.get('peers'):
            return {
                'peers': disfold_result['peers'],
                'peer_details': disfold_result.get('peer_details', []),
                'source': 'disfold',
                'sic_code': sic_code,
                'industry': disfold_result.get('industry') or sic_description,
            }

    # Strategy 2: Validate Yahoo peers using SIC codes
    if yahoo_peers:
        validation = validate_yahoo_peers(ticker, yahoo_peers, sic_code, mcp_funcs=mcp_funcs)

        if validation['valid_peers']:
            return {
                'peers': validation['valid_peers'][:max_peers],
                'peer_details': validation.get('peer_details', []),
                'source': validation['source'],
                'sic_code': sic_code or validation['main_sic'],
                'industry': sic_description or validation['main_industry'],
                'filtered_count': len(validation['invalid_peers']),
            }

        # Update sic_code from validation if we found it
        if not sic_code and validation.get('main_sic'):
            sic_code = validation['main_sic']
            sic_description = sic_description or validation.get('main_industry')

    # Strategy 3: Fallback to SEC SIC search
    if sic_code:
        sec_peers = get_peers_from_sec_sic(sic_code, ticker, max_peers=max_peers, mcp_funcs=mcp_funcs)
        if sec_peers:
            return {
                'peers': sec_peers,
                'peer_details': [],
                'source': 'sec_sic_search',
                'sic_code': sic_code,
                'industry': sic_description,
            }

    # No valid peers found
    return {
        'peers': [],
        'peer_details': [],
        'source': 'none',
        'sic_code': sic_code,
        'industry': sic_description,
    }
