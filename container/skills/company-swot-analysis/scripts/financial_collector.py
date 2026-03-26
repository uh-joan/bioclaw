#!/usr/bin/env python3
"""
Financial data collection for company SWOT analysis.

This module provides functions for:
- Detecting company region (US, EU, UK, CH, JP, KR)
- Getting financial data from SEC EDGAR (US-GAAP)
- Getting financial data from Yahoo Finance (international companies)
- Extracting segment/geographic revenue from XBRL filings
"""

import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

# All MCP functions are now accessed via mcp_funcs parameter
# No direct imports from mcp.servers.* allowed

from sec_lookup import lookup_company_in_sec_tickers
from ticker_utils import generate_ticker_guesses
from financial_parser import (
    get_historical_exchange_rate,
    convert_to_usd,
    detect_reporting_currency,
    parse_xbrl_contexts,
    extract_xbrl_segment_revenue,
    parse_yahoo_value,
)
from swot_constants import COUNTRY_TO_CURRENCY


# ============================================================================
# International Company Detection
# ============================================================================

def detect_company_region(company_name: str, mcp_funcs: Dict[str, Any] = None) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """
    Detect if a company is from Europe, Asia, or US by searching various databases.

    Returns:
        Tuple of (region, company_info) where:
        - region: 'EU', 'UK', 'CH' (Swiss), 'JP', 'KR', 'US', or None
        - company_info: Dict with relevant identifiers (LEI, ticker, EDINET code, etc.)
    """
    print(f"   Detecting company region for {company_name}...")

    if not mcp_funcs:
        return (None, None)

    # Extract MCP functions
    search_swiss_companies = mcp_funcs.get('eu_search_swiss')
    search_uk_companies = mcp_funcs.get('eu_search_uk')
    eu_search_companies = mcp_funcs.get('eu_search_companies')
    search_japan_companies = mcp_funcs.get('asia_search_japan')
    search_korea_companies = mcp_funcs.get('asia_search_korea')

    # Try Swiss companies first (big pharma like Novartis, Roche)
    try:
        if search_swiss_companies:
            swiss_result = search_swiss_companies(query=company_name, limit=5)
        else:
            swiss_result = None

        if swiss_result and isinstance(swiss_result, dict) and swiss_result.get('data'):
            companies = swiss_result['data']
            name_lower = company_name.lower()
            for company in companies:
                company_name_result = company.get('legal_name', '') or company.get('name', '')
                if name_lower in company_name_result.lower() or company_name_result.lower().startswith(name_lower.split()[0].lower()):
                    print(f"   Found Swiss company: {company_name_result}")
                    return ('CH', {'lei': company.get('lei'), 'name': company_name_result})
    except Exception as e:
        print(f"   Swiss search failed: {e}")

    # Try UK companies (AstraZeneca, GSK)
    try:
        if search_uk_companies:
            uk_result = search_uk_companies(query=company_name, limit=5)
        else:
            uk_result = None

        if uk_result and isinstance(uk_result, dict) and uk_result.get('data'):
            companies = uk_result['data']
            name_lower = company_name.lower()
            for company in companies:
                company_name_result = company.get('company_name', '') or company.get('name', '')
                if name_lower in company_name_result.lower() or company_name_result.lower().startswith(name_lower.split()[0].lower()):
                    print(f"   Found UK company: {company_name_result}")
                    return ('UK', {'company_number': company.get('company_number'), 'name': company_name_result})
    except Exception as e:
        print(f"   UK search failed: {e}")

    # Try EU companies via GLEIF
    try:
        if eu_search_companies:
            eu_result = eu_search_companies(query=company_name, limit=5)
        else:
            eu_result = None

        if eu_result and isinstance(eu_result, dict) and eu_result.get('data'):
            companies = eu_result['data']
            name_lower = company_name.lower()
            for company in companies:
                company_name_result = company.get('legal_name', '') or company.get('name', '')
                country = company.get('country', '')
                # Skip US companies from GLEIF results
                if country and country.upper() not in ('US', 'USA'):
                    if name_lower in company_name_result.lower() or company_name_result.lower().startswith(name_lower.split()[0].lower()):
                        print(f"   Found EU company: {company_name_result} ({country})")
                        return ('EU', {'lei': company.get('lei'), 'name': company_name_result, 'country': country})
    except Exception as e:
        print(f"   EU search failed: {e}")

    # Try Japan (Takeda, Astellas, Daiichi Sankyo)
    try:
        if search_japan_companies:
            japan_result = search_japan_companies(query=company_name, limit=5)
        else:
            japan_result = None

        if japan_result and isinstance(japan_result, dict) and japan_result.get('data'):
            companies = japan_result['data']
            name_lower = company_name.lower()
            for company in companies:
                company_name_en = company.get('company_name_en', '') or ''
                company_name_jp = company.get('company_name', '') or ''
                if name_lower in company_name_en.lower() or name_lower in company_name_jp.lower():
                    print(f"   Found Japanese company: {company_name_en or company_name_jp}")
                    return ('JP', {'edinet_code': company.get('edinet_code'), 'name': company_name_en or company_name_jp, 'ticker': company.get('securities_code')})
    except Exception as e:
        print(f"   Japan search failed: {e}")

    # Try Korea (Samsung Biologics, Celltrion)
    try:
        if search_korea_companies:
            korea_result = search_korea_companies(query=company_name, limit=5)
        else:
            korea_result = None

        if korea_result and isinstance(korea_result, dict) and korea_result.get('data'):
            companies = korea_result['data']
            name_lower = company_name.lower()
            for company in companies:
                company_name_en = company.get('corp_name_eng', '') or ''
                company_name_kr = company.get('corp_name', '') or ''
                if name_lower in company_name_en.lower() or name_lower in company_name_kr.lower():
                    print(f"   Found Korean company: {company_name_en or company_name_kr}")
                    return ('KR', {'corp_code': company.get('corp_code'), 'name': company_name_en or company_name_kr, 'ticker': company.get('stock_code')})
    except Exception as e:
        print(f"   Korea search failed: {e}")

    return (None, None)


# ============================================================================
# Yahoo Finance Financial Data
# ============================================================================

def get_financial_data_from_yahoo(company_name: str, ticker: Optional[str] = None, country: Optional[str] = None, mcp_funcs: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Get financial data from Yahoo Finance via financials MCP.

    This works for international companies where SEC EDGAR doesn't have data.
    The MCP returns formatted text which we parse for financial values.

    IMPORTANT: Yahoo Finance returns financials in the company's reporting currency
    (e.g., DKK for Danish companies) but labels them as "USD". We detect foreign
    companies and convert to actual USD.

    Args:
        company_name: Company name
        ticker: Stock ticker (optional, will be guessed if not provided)
        country: Country of incorporation (optional, used for currency detection)

    Returns:
        dict: Financial data with revenue, expenses, etc. in USD
    """
    print(f"   Trying Yahoo Finance for {company_name}...")

    if not mcp_funcs:
        return {'revenue': {}, 'rd_expense': {}, 'net_income': {}, 'success': False, 'error': 'No MCP functions provided'}

    financial_intelligence = mcp_funcs.get('financials_lookup')
    if not financial_intelligence:
        return {'revenue': {}, 'rd_expense': {}, 'net_income': {}, 'success': False, 'error': 'Financial intelligence function not available'}

    # Try to find ticker if not provided
    if not ticker:
        # Common pharma company tickers
        ticker_guesses = []
        name_upper = company_name.upper()

        # Generate guesses
        first_word = name_upper.split()[0] if name_upper else ''
        ticker_guesses.append(first_word[:4])  # First 4 letters
        ticker_guesses.append(first_word[:3])  # First 3 letters

        # Try each guess via Yahoo Finance
        for guess in ticker_guesses[:3]:  # Limit attempts
            try:
                profile = financial_intelligence(method='stock_profile', symbol=guess)
                if isinstance(profile, dict):
                    # Check text content for company name match
                    text = profile.get('text', '')
                    if company_name.lower().split()[0].lower() in text.lower():
                        ticker = guess
                        print(f"   Found ticker via Yahoo: {ticker}")
                        break
            except:
                continue

    if not ticker:
        print(f"   Could not determine ticker for {company_name}")
        return {'revenue': {}, 'rd_expense': {}, 'net_income': {}, 'success': False, 'error': 'No ticker found'}

    try:
        # First get company profile to detect country/currency
        reporting_currency = 'USD'
        detected_country = country

        if not detected_country:
            try:
                profile = financial_intelligence(method='stock_profile', symbol=ticker)
                if isinstance(profile, dict):
                    profile_text = profile.get('text', '')
                    # Extract country from profile
                    country_match = re.search(r'\*\*Country:\*\*\s*(\w+(?:\s+\w+)?)', profile_text)
                    if country_match:
                        detected_country = country_match.group(1).strip()
            except:
                pass

        # Determine reporting currency from country
        if detected_country:
            reporting_currency = COUNTRY_TO_CURRENCY.get(detected_country, 'USD')
            if reporting_currency != 'USD':
                print(f"   Detected country: {detected_country}, reporting currency: {reporting_currency}")

        # Get company financials from Yahoo
        financials = financial_intelligence(method='stock_financials', symbol=ticker)

        result = {
            'ticker': ticker,
            'source': 'yahoo_finance',
            'reporting_currency': reporting_currency,
            'detected_country': detected_country,
            'revenue': {},
            'rd_expense': {},
            'net_income': {},
            'success': True
        }

        # Get exchange rate if needed
        fx_rate = 1.0
        if reporting_currency != 'USD':
            fx_rate = get_historical_exchange_rate(reporting_currency)
            result['fx_rate'] = fx_rate

        if isinstance(financials, dict):
            # The MCP returns formatted text - parse it for financial values
            text = financials.get('text', '')

            if text:
                # Extract revenue and convert to USD
                revenue = parse_yahoo_value(text, 'Total Revenue')
                if revenue:
                    revenue_usd = revenue * fx_rate if reporting_currency != 'USD' else revenue
                    result['revenue']['current'] = revenue_usd
                    result['revenue']['values'] = {'latest': revenue_usd}
                    if reporting_currency != 'USD':
                        result['revenue']['original_currency'] = reporting_currency
                        result['revenue']['original_value'] = revenue
                        print(f"   Found revenue: {reporting_currency} {revenue / 1e9:.2f}B = ${revenue_usd / 1e9:.2f}B USD")
                    else:
                        print(f"   Found revenue: ${revenue_usd / 1e9:.2f}B")

                # Extract EBITDA and convert
                ebitda = parse_yahoo_value(text, 'EBITDA')
                if ebitda:
                    ebitda_usd = ebitda * fx_rate if reporting_currency != 'USD' else ebitda
                    result['ebitda'] = {'current': ebitda_usd, 'values': {'latest': ebitda_usd}}

                # Extract gross profits and convert
                gross_profits = parse_yahoo_value(text, 'Gross Profits')
                if gross_profits:
                    gp_usd = gross_profits * fx_rate if reporting_currency != 'USD' else gross_profits
                    result['gross_profits'] = {'current': gp_usd, 'values': {'latest': gp_usd}}

                # Extract free cash flow and convert
                fcf = parse_yahoo_value(text, 'Free Cash Flow')
                if fcf:
                    fcf_usd = fcf * fx_rate if reporting_currency != 'USD' else fcf
                    result['free_cash_flow'] = {'current': fcf_usd, 'values': {'latest': fcf_usd}}

                # Extract operating cash flow and convert
                ocf = parse_yahoo_value(text, 'Operating Cash Flow')
                if ocf:
                    ocf_usd = ocf * fx_rate if reporting_currency != 'USD' else ocf
                    result['operating_cash_flow'] = {'current': ocf_usd, 'values': {'latest': ocf_usd}}

                # Parse growth metrics (percentages - no conversion needed)
                earnings_growth_match = re.search(r'\*\*Earnings Growth:\*\*\s*([\d.-]+)%', text)
                if earnings_growth_match:
                    result['earnings_growth'] = float(earnings_growth_match.group(1)) / 100

                revenue_growth_match = re.search(r'\*\*Revenue Growth:\*\*\s*([\d.-]+)%', text)
                if revenue_growth_match:
                    result['revenue_growth'] = float(revenue_growth_match.group(1)) / 100
                    result['revenue']['yoy_growth'] = float(revenue_growth_match.group(1)) / 100

                # Parse margin metrics (percentages - no conversion needed)
                profit_margin_match = re.search(r'\*\*Profit Margin:\*\*\s*([\d.-]+)%', text)
                if profit_margin_match:
                    result['profit_margin'] = float(profit_margin_match.group(1)) / 100

        # Backwards compatibility
        if result['revenue'].get('current'):
            result['revenue_current'] = result['revenue']['current']
        if result['rd_expense'].get('current'):
            result['rd_spending'] = result['rd_expense']['current']

        return result

    except Exception as e:
        print(f"   Yahoo Finance failed: {e}")
        import traceback
        traceback.print_exc()
        return {'revenue': {}, 'rd_expense': {}, 'net_income': {}, 'success': False, 'error': str(e)}


# ============================================================================
# XBRL Segment Revenue Extraction
# ============================================================================

def get_segment_revenue_from_xbrl(cik: str, company_name: str, mcp_funcs: Dict[str, Any] = None) -> Dict[str, Any]:
    """Extract segment and geographic revenue from SEC EDGAR XBRL filings.

    Downloads actual XBRL XML files and parses dimensional data to get
    product/segment-level revenue breakdowns.

    Args:
        cik: SEC CIK number (10-digit padded)
        company_name: Company name for logging

    Returns:
        dict: segment_revenue, geographic_revenue, consolidated_revenue, success
    """
    print(f"   Fetching segment revenue from XBRL filings...")

    if not mcp_funcs:
        return {'segment_revenue': {}, 'geographic_revenue': {}, 'success': False, 'error': 'No MCP functions provided'}

    get_company_submissions = mcp_funcs.get('sec_get_filing')
    if not get_company_submissions:
        return {'segment_revenue': {}, 'geographic_revenue': {}, 'success': False, 'error': 'SEC functions not available'}

    try:
        # Get recent filings
        submissions = get_company_submissions(cik_or_ticker=cik)

        if isinstance(submissions, dict) and 'error' in submissions:
            return {'segment_revenue': {}, 'geographic_revenue': {}, 'success': False}

        recent_filings = submissions.get('recentFilings', [])

        # Get latest filing, preferring annual (10-K/20-F) over quarterly (10-Q).
        # If only a 10-Q is available, we still use it but flag it as quarterly.
        target_filing = None
        quarterly_fallback = None
        for filing in recent_filings:
            form = filing.get('form')
            if form in ['10-K', '20-F']:
                target_filing = filing
                break
            elif form == '10-Q' and quarterly_fallback is None:
                quarterly_fallback = filing
        if not target_filing and quarterly_fallback:
            target_filing = quarterly_fallback
            print(f"   Warning: Only 10-Q available (no 10-K/20-F found). Revenue may be quarterly.")

        if not target_filing:
            return {'segment_revenue': {}, 'geographic_revenue': {}, 'success': False}

        # Construct XBRL URL
        cik_padded = cik.zfill(10)
        accession = target_filing.get('accessionNumber', '').replace('-', '')
        primary_doc = target_filing.get('primaryDocument', '')

        if primary_doc.endswith('.htm'):
            xml_filename = primary_doc.replace('.htm', '_htm.xml')
        else:
            xml_filename = primary_doc

        url = f"https://www.sec.gov/Archives/edgar/data/{cik_padded}/{accession}/{xml_filename}"

        # Download XBRL
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Research/Analysis pharma-research@example.com'
        })

        time.sleep(0.2)  # Rate limiting

        with urllib.request.urlopen(req, timeout=15) as response:
            xml_content = response.read()

        xml_root = ET.fromstring(xml_content)

        # Detect reporting currency for foreign filers (e.g., DKK for Novo Nordisk)
        reporting_currency = detect_reporting_currency(xml_root)
        if reporting_currency != 'USD':
            print(f"   Detected reporting currency: {reporting_currency}")

        # Parse contexts and extract revenue
        contexts = parse_xbrl_contexts(xml_root)
        facts = extract_xbrl_segment_revenue(xml_root, contexts)

        # Aggregate segment revenue - use DELTA calculation for cumulative data
        segment_revenue = defaultdict(float)
        geographic_revenue = defaultdict(float)
        consolidated_revenue = 0.0

        def is_annual_period(start_date: str, end_date: str) -> bool:
            """Check if the period is approximately 1 year (350-380 days)."""
            if not start_date or not end_date:
                return False
            try:
                from datetime import datetime
                start = datetime.strptime(start_date[:10], '%Y-%m-%d')
                end = datetime.strptime(end_date[:10], '%Y-%m-%d')
                days = (end - start).days
                return 350 <= days <= 380
            except (ValueError, TypeError):
                return False

        def extract_year(date_str: str) -> int:
            """Extract year from date string."""
            if not date_str:
                return 0
            try:
                return int(date_str[:4])
            except (ValueError, TypeError):
                return 0

        # Try annual period filter first (works for US-GAAP filers)
        annual_facts = [f for f in facts if is_annual_period(f.get('start_date'), f.get('end_date'))]
        annual_periods = set(f['end_date'] for f in annual_facts if f['end_date'])
        latest_period = max(annual_periods) if annual_periods else None

        if latest_period:
            # US-GAAP style: use annual period facts directly
            for fact in annual_facts:
                if fact['end_date'] == latest_period:
                    if fact['segment']:
                        segment_revenue[fact['segment']] = max(
                            segment_revenue[fact['segment']], fact['value']
                        )
                    elif fact['geography']:
                        geographic_revenue[fact['geography']] = max(
                            geographic_revenue[fact['geography']], fact['value']
                        )
                    elif not fact['segment'] and not fact['geography']:
                        consolidated_revenue = max(consolidated_revenue, fact['value'])
        else:
            # IFRS/cumulative style: calculate delta between years
            segment_by_year = defaultdict(lambda: defaultdict(float))
            geo_by_year = defaultdict(lambda: defaultdict(float))
            consolidated_by_year = defaultdict(float)

            for fact in facts:
                end_date = fact.get('end_date') or fact.get('instant')
                year = extract_year(end_date)
                if year == 0:
                    continue

                if fact['segment']:
                    segment_by_year[fact['segment']][year] = max(
                        segment_by_year[fact['segment']][year], fact['value']
                    )
                elif fact['geography']:
                    geo_by_year[fact['geography']][year] = max(
                        geo_by_year[fact['geography']][year], fact['value']
                    )
                elif not fact['segment'] and not fact['geography']:
                    consolidated_by_year[year] = max(consolidated_by_year[year], fact['value'])

            # Find latest two years and calculate delta
            all_years = set()
            for seg_years in segment_by_year.values():
                all_years.update(seg_years.keys())
            for geo_years in geo_by_year.values():
                all_years.update(geo_years.keys())
            all_years.update(consolidated_by_year.keys())

            if len(all_years) >= 2:
                sorted_years = sorted(all_years, reverse=True)
                latest_year = sorted_years[0]
                prev_year = sorted_years[1]
                latest_period = f"{latest_year}-12-31"

                # Calculate segment revenue delta
                for seg, years in segment_by_year.items():
                    if latest_year in years:
                        latest_val = years[latest_year]
                        prev_val = years.get(prev_year, 0)
                        delta = latest_val - prev_val
                        if delta > 0:
                            segment_revenue[seg] = delta

                # Calculate geographic revenue delta
                for geo, years in geo_by_year.items():
                    if latest_year in years:
                        latest_val = years[latest_year]
                        prev_val = years.get(prev_year, 0)
                        delta = latest_val - prev_val
                        if delta > 0:
                            geographic_revenue[geo] = delta

                # Calculate consolidated revenue delta
                if latest_year in consolidated_by_year:
                    latest_val = consolidated_by_year[latest_year]
                    prev_val = consolidated_by_year.get(prev_year, 0)
                    delta = latest_val - prev_val
                    if delta > 0:
                        consolidated_revenue = delta
            elif len(all_years) == 1:
                # Only one year available - can't extract annual from single filing
                latest_year = list(all_years)[0]
                latest_period = f"{latest_year}-12-31"

        # Filter out generic aggregation terms from segment revenue
        generic_aggregates = {
            'product gross', 'product net', 'product revenue', 'product', 'products',
            'reportable', 'total', 'consolidated', 'combined', 'aggregate',
            'service', 'services', 'license', 'collaboration', 'net',
            'product sales discounts', 'allowances', 'adjustments', 'gross',
            'product sales discounts and allowances',
            # Non-product revenue categories
            'collaboration revenue', 'royalty revenue', 'royalties',
            'collaboration arrangement', 'license revenue', 'grant', 'grants',
            'product sales', 'stand ready manufacturing revenue',
            'collaboration arrangement including arrangements with affiliate',
        }

        def is_generic_segment(name: str) -> bool:
            """Check if segment name is a generic aggregation term or parent category."""
            lower = name.lower()
            # Exact match
            if lower in generic_aggregates:
                return True
            # Contains discount/allowance/adjustment patterns
            if 'discount' in lower or 'allowance' in lower or 'adjustment' in lower:
                return True
            # Generic license/service/collaboration revenue (not product-specific)
            if lower.startswith('license') and ('revenue' in lower or 'service' in lower or 'development' in lower):
                return True
            if lower.startswith('collaboration') and ('revenue' in lower or 'arrangement' in lower):
                return True
            if lower.startswith('royalt'):
                return True
            if 'manufacturing revenue' in lower or 'stand ready' in lower:
                return True
            if 'access rights' in lower:
                return True
            # Filter out aggregation segments
            if 'excluding' in lower or 'all other' in lower:
                return True
            if lower == 'other products' or lower == 'other':
                return True
            # Filter out parent category segments
            if lower.startswith('total '):
                return True
            if lower.startswith('operating segment'):
                return True
            if ' and ' in lower:
                return True
            # Common category patterns
            if lower.endswith(' care') and lower not in ['rare disease care']:
                return True
            if lower in ['rare blood disorders', 'rare endocrine disorders']:
                return True
            return False

        segment_revenue = {
            k: v for k, v in segment_revenue.items()
            if not is_generic_segment(k)
        }

        # Filter to leaf nodes only - remove parent/category segments
        # Data-driven approach: Prefix hierarchy detection only
        # (Sum-based detection causes too many false positives with coincidental sums)
        parent_segments = set()

        # Check for hierarchical naming patterns (HIVProduct Sales -> HIVProducts Biktarvy)
        def normalize_for_prefix(s):
            s = s.lower()
            for suffix in [' sales', ' product sales', ' revenue']:
                if s.endswith(suffix):
                    s = s[:-len(suffix)]
            return s.strip()

        for seg_name in list(segment_revenue.keys()):
            if seg_name in parent_segments:
                continue
            seg_norm = normalize_for_prefix(seg_name)

            for other_seg in segment_revenue.keys():
                if other_seg == seg_name:
                    continue
                other_norm = normalize_for_prefix(other_seg)

                if len(other_norm) <= len(seg_norm):
                    continue

                if other_norm.startswith(seg_norm):
                    remainder = other_norm[len(seg_norm):]
                    if remainder.startswith('s ') or remainder.startswith('s-') or remainder.startswith(' '):
                        parent_segments.add(seg_name)
                        break

        def is_leaf_segment(segment_name: str) -> bool:
            """Check if segment is a leaf (not in parent set)."""
            return segment_name not in parent_segments

        leaf_segments = {
            k: v for k, v in segment_revenue.items()
            if is_leaf_segment(k)
        }

        # Only use leaf filtering if it leaves us with data
        if leaf_segments:
            filtered_count = len(segment_revenue) - len(leaf_segments)
            if filtered_count > 0:
                print(f"   Filtered {filtered_count} parent segments, keeping {len(leaf_segments)} leaf products")
            segment_revenue = leaf_segments

        # Convert to USD if reporting in foreign currency
        if reporting_currency != 'USD':
            fx_date = latest_period[:10] if latest_period else None
            currency_rate = get_historical_exchange_rate(reporting_currency, fx_date)
            if currency_rate != 1.0:
                segment_revenue = {k: v * currency_rate for k, v in segment_revenue.items()}
                geographic_revenue = {k: v * currency_rate for k, v in geographic_revenue.items()}
                consolidated_revenue = consolidated_revenue * currency_rate
                print(f"   Converted from {reporting_currency} to USD (rate: {currency_rate:.4f}, date: {fx_date})")

        # Sort by revenue
        segment_revenue = dict(sorted(segment_revenue.items(), key=lambda x: x[1], reverse=True))
        geographic_revenue = dict(sorted(geographic_revenue.items(), key=lambda x: x[1], reverse=True))

        # Determine filing type
        form_type = target_filing.get('form', '')
        is_foreign_filer = form_type in ['20-F', '6-K', '40-F']

        if not segment_revenue and is_foreign_filer:
            print(f"   Foreign filer ({form_type}) - IFRS XBRL typically lacks US-GAAP segment breakdown")
        else:
            print(f"   Found {len(segment_revenue)} segments, {len(geographic_revenue)} geographies")

        return {
            'segment_revenue': segment_revenue,
            'geographic_revenue': geographic_revenue,
            'consolidated_revenue': consolidated_revenue,
            'period': latest_period,
            'form_type': form_type,
            'is_foreign_filer': is_foreign_filer,
            'success': True
        }

    except Exception as e:
        print(f"   XBRL extraction failed: {e}")
        return {'segment_revenue': {}, 'geographic_revenue': {}, 'success': False}


# ============================================================================
# SEC EDGAR Financial Data
# ============================================================================

def calculate_cagr(start_val: float, end_val: float, years: int) -> Optional[float]:
    """Calculate Compound Annual Growth Rate."""
    if start_val <= 0 or end_val <= 0 or years <= 0:
        return None
    return (end_val / start_val) ** (1 / years) - 1


def extract_annual_values(concept_data: dict, max_years: int = 3) -> Dict[str, float]:
    """Extract annual values from XBRL concept data, keyed by year."""
    values = {}
    if not isinstance(concept_data, dict) or 'units' not in concept_data:
        return values

    usd_entries = concept_data.get('units', {}).get('USD', [])
    # Filter for annual filings (form 10-K) and valid fiscal year ends
    annual_entries = [e for e in usd_entries if e.get('form') == '10-K' and e.get('end')]

    # Group by fiscal year (extract year from end date)
    by_year = {}
    for entry in annual_entries:
        year = entry['end'][:4]
        # Keep the most recent entry per year (in case of amendments)
        if year not in by_year or entry.get('filed', '') > by_year[year].get('filed', ''):
            by_year[year] = entry

    # Get last N years, sorted descending
    years_sorted = sorted(by_year.keys(), reverse=True)[:max_years]
    for year in years_sorted:
        values[year] = by_year[year].get('val')

    return values


def _find_company_cik(company_name: str, mcp_funcs: Dict[str, Any] = None) -> Tuple[Optional[str], Optional[str]]:
    """
    Search for company CIK and ticker using SEC company_tickers.json.
    Returns (cik, ticker) tuple.
    """
    if not mcp_funcs:
        return (None, None)

    # Extract MCP functions
    search_companies = mcp_funcs.get('sec_search_companies')
    get_company_submissions = mcp_funcs.get('sec_get_filing')
    get_company_cik = mcp_funcs.get('sec_get_cik')

    # PRIMARY METHOD: Use SEC company_tickers.json (most reliable)
    sec_lookup = lookup_company_in_sec_tickers(company_name)
    if sec_lookup:
        cik, ticker = sec_lookup
        print(f"   Found via SEC tickers: CIK={cik}, Ticker={ticker}")
        return cik, ticker

    # FALLBACK: Try MCP search_companies
    if search_companies:
        search_result = search_companies(query=company_name)
    else:
        search_result = None

    if search_result:
        cik = None
        if isinstance(search_result, dict):
            companies = search_result.get('data', [])
            if companies and isinstance(companies, list):
                for company in companies:
                    if company.get('name', '').lower() == company_name.lower():
                        cik = company.get('cik')
                        break
                if not cik and companies:
                    cik = companies[0].get('cik')
        elif isinstance(search_result, str):
            cik_match = re.search(r'CIK[:\s]+(\d{10})', search_result)
            if cik_match:
                cik = cik_match.group(1)

        if cik:
            print(f"   Found via MCP search: CIK={cik}")
            return cik, None

    # LAST RESORT: Try ticker guesses with validation
    def validate_cik_matches_company(cik_candidate: str, expected_company: str) -> bool:
        if not get_company_submissions:
            return False
        try:
            submissions = get_company_submissions(cik_or_ticker=cik_candidate)
            if isinstance(submissions, dict) and 'name' in submissions:
                sec_name = submissions['name'].upper()
                expected_upper = expected_company.upper()
                for suffix in [' PHARMACEUTICALS', ' THERAPEUTICS', ' BIOSCIENCES', ' BIOPHARMA',
                               ' BIOTHERAPEUTICS', ' BIOTECHNOLOGY', ' BIOTECH', ' INC', ' CORP',
                               ' LLC', ' LTD', ' CO', ' SCIENCES', ' MEDICAL', ' HEALTH']:
                    expected_upper = expected_upper.replace(suffix, '')
                    sec_name = sec_name.replace(suffix, '')
                expected_upper = expected_upper.strip()
                sec_name = sec_name.strip()
                first_word = expected_upper.split()[0] if expected_upper else ''
                if first_word and (first_word in sec_name or sec_name.startswith(first_word)):
                    return True
                if expected_upper and expected_upper in sec_name:
                    return True
                print(f"   CIK {cik_candidate} is for '{submissions['name']}', not '{expected_company}' - skipping")
                return False
        except:
            return False
        return False

    ticker_guesses = generate_ticker_guesses(company_name)
    for ticker_guess in ticker_guesses:
        if not get_company_cik:
            break
        try:
            cik_result = get_company_cik(ticker=ticker_guess)
            cik_candidate = None
            if isinstance(cik_result, str):
                cik_match = re.search(r'CIK:\s*(\d{10})', cik_result)
                if cik_match:
                    cik_candidate = cik_match.group(1)
            elif isinstance(cik_result, dict) and cik_result.get('cik'):
                cik_candidate = cik_result.get('cik')
            if cik_candidate and validate_cik_matches_company(cik_candidate, company_name):
                print(f"   Found via ticker guess: {ticker_guess}")
                return cik_candidate, ticker_guess
        except:
            pass

    return None, None


def get_financial_data(company_name: str, mcp_funcs: Dict[str, Any] = None) -> Dict[str, Any]:
    """Collect multi-year financial data from SEC EDGAR with YoY trends.

    Extracts last 3 years of:
    - Revenue
    - R&D expenses
    - Net income
    And calculates growth rates and CAGR.
    """
    print(f"\n💰 Collecting financial data for {company_name}...")

    if not mcp_funcs:
        return {'revenue': {}, 'rd_expense': {}, 'net_income': {}, 'success': False, 'error': 'No MCP functions provided'}

    get_company_facts = mcp_funcs.get('sec_get_facts')
    if not get_company_facts:
        return {'revenue': {}, 'rd_expense': {}, 'net_income': {}, 'success': False, 'error': 'SEC functions not available'}

    try:
        # Find company CIK dynamically
        cik, ticker = _find_company_cik(company_name, mcp_funcs=mcp_funcs)

        if not cik:
            print(f"   Could not find SEC CIK for {company_name}")
            print(f"   Checking if this is an international company...")

            # Try to detect if this is an international company
            region, region_info = detect_company_region(company_name, mcp_funcs=mcp_funcs)

            if region:
                print(f"   Detected as {region} company - trying Yahoo Finance...")
                yahoo_ticker = region_info.get('ticker') if region_info else None
                yahoo_result = get_financial_data_from_yahoo(company_name, yahoo_ticker, mcp_funcs=mcp_funcs)

                if yahoo_result.get('success'):
                    yahoo_result['detected_region'] = region
                    yahoo_result['region_info'] = region_info
                    return yahoo_result

            return {'revenue': {}, 'rd_expense': {}, 'net_income': {}, 'success': False, 'error': 'CIK not found and no international data available'}

        print(f"   Found CIK: {cik}")

        facts = get_company_facts(cik_or_ticker=cik)

        result = {
            'cik': cik,
            'ticker': ticker,
            'revenue': {},
            'rd_expense': {},
            'net_income': {},
            'success': True
        }

        # Handle structured XBRL response (dict format)
        if isinstance(facts, dict) and 'facts' in facts:
            facts_data = facts.get('facts', {})
            us_gaap = facts_data.get('us-gaap', {})

            # Extract Revenue (try multiple concepts)
            for rev_concept in ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax',
                                'SalesRevenueNet', 'TotalRevenuesAndOtherIncome']:
                if rev_concept in us_gaap:
                    values = extract_annual_values(us_gaap[rev_concept])
                    if values:
                        result['revenue']['values'] = values
                        break

            # Extract R&D Spending
            for rd_concept in ['ResearchAndDevelopmentExpense',
                               'ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost']:
                if rd_concept in us_gaap:
                    values = extract_annual_values(us_gaap[rd_concept])
                    if values:
                        result['rd_expense']['values'] = values
                        break

            # Extract Net Income
            for ni_concept in ['NetIncomeLoss', 'ProfitLoss', 'NetIncomeLossAvailableToCommonStockholdersBasic']:
                if ni_concept in us_gaap:
                    values = extract_annual_values(us_gaap[ni_concept])
                    if values:
                        result['net_income']['values'] = values
                        break

            # Extract Cash and Cash Equivalents (latest quarter for most current view)
            for cash_concept in ['CashAndCashEquivalentsAtCarryingValue', 'CashCashEquivalentsAndShortTermInvestments',
                                 'Cash', 'CashAndCashEquivalentsAtCarryingValueIncludingDiscontinuedOperations']:
                if cash_concept in us_gaap:
                    cash_data = us_gaap[cash_concept]
                    if isinstance(cash_data, dict) and 'units' in cash_data:
                        usd_entries = cash_data.get('units', {}).get('USD', [])
                        # Get most recent quarterly filing (10-Q or 10-K)
                        recent_entries = [e for e in usd_entries if e.get('form') in ('10-Q', '10-K') and e.get('end')]
                        if recent_entries:
                            # Sort by end date descending and take most recent
                            recent_entries.sort(key=lambda x: x.get('end', ''), reverse=True)
                            latest = recent_entries[0]
                            result['cash'] = {
                                'current': latest.get('val'),
                                'period': latest.get('end'),
                                'form': latest.get('form')
                            }
                            break

        # Calculate growth metrics for each category
        for category in ['revenue', 'rd_expense', 'net_income']:
            values = result[category].get('values', {})
            if len(values) >= 2:
                years_sorted = sorted(values.keys(), reverse=True)
                latest_year = years_sorted[0]
                prev_year = years_sorted[1]
                latest_val = values[latest_year]
                prev_val = values[prev_year]

                # YoY growth
                if prev_val and prev_val != 0:
                    result[category]['yoy_growth'] = (latest_val - prev_val) / abs(prev_val)

                # CAGR if we have 3+ years
                if len(values) >= 3:
                    oldest_year = years_sorted[-1]
                    oldest_val = values[oldest_year]
                    years_diff = int(latest_year) - int(oldest_year)
                    if years_diff > 0:
                        cagr = calculate_cagr(oldest_val, latest_val, years_diff)
                        if cagr is not None:
                            result[category]['cagr'] = cagr

                # Set current value for backwards compatibility
                result[category]['current'] = latest_val

        # Backwards compatibility: set top-level revenue/rd_spending
        if result['revenue'].get('current'):
            result['revenue_current'] = result['revenue']['current']
        if result['rd_expense'].get('current'):
            result['rd_spending'] = result['rd_expense']['current']

        # Check if we got meaningful financial data from SEC EDGAR
        # Foreign companies (like Swiss Novartis) may have a CIK but file 20-F with IFRS, not US-GAAP 10-K
        has_revenue = bool(result['revenue'].get('values') or result['revenue'].get('current'))
        has_any_financials = has_revenue or result.get('net_income', {}).get('values')

        if not has_any_financials:
            print(f"   SEC EDGAR returned empty financials (likely foreign filer using 20-F/IFRS)")
            print(f"   Attempting international company detection and Yahoo Finance fallback...")

            # Detect company region and fall back to Yahoo Finance
            region, region_info = detect_company_region(company_name, mcp_funcs=mcp_funcs)

            if region:
                print(f"   Detected region: {region}")
                result['detected_region'] = region
                result['region_info'] = region_info

            # Try Yahoo Finance as universal fallback for international companies
            yahoo_ticker = ticker  # Use SEC ticker if we found one
            if not yahoo_ticker and region_info:
                yahoo_ticker = region_info.get('ticker')

            yahoo_result = get_financial_data_from_yahoo(company_name, yahoo_ticker, mcp_funcs=mcp_funcs)

            if yahoo_result.get('success') and (yahoo_result.get('revenue', {}).get('current') or yahoo_result.get('net_income', {}).get('current')):
                print(f"   Successfully got financials from Yahoo Finance!")
                # Merge Yahoo data into result - include all fields from Yahoo
                result['revenue'] = yahoo_result.get('revenue', {})
                result['rd_expense'] = yahoo_result.get('rd_expense', {})
                result['net_income'] = yahoo_result.get('net_income', {})
                result['source'] = 'yahoo_finance'
                result['success'] = True

                # Include additional Yahoo Finance metrics
                if yahoo_result.get('ebitda'):
                    result['ebitda'] = yahoo_result['ebitda']
                if yahoo_result.get('gross_profits'):
                    result['gross_profits'] = yahoo_result['gross_profits']
                if yahoo_result.get('free_cash_flow'):
                    result['free_cash_flow'] = yahoo_result['free_cash_flow']
                if yahoo_result.get('operating_cash_flow'):
                    result['operating_cash_flow'] = yahoo_result['operating_cash_flow']
                if yahoo_result.get('earnings_growth') is not None:
                    result['earnings_growth'] = yahoo_result['earnings_growth']
                if yahoo_result.get('profit_margin') is not None:
                    result['profit_margin'] = yahoo_result['profit_margin']

                # Update backwards compatibility fields
                if result['revenue'].get('current'):
                    result['revenue_current'] = result['revenue']['current']
                if result['rd_expense'].get('current'):
                    result['rd_spending'] = result['rd_expense']['current']
            else:
                print(f"   Yahoo Finance also returned no data")

        # Attempt to get segment/product revenue breakdown from XBRL dimensional analysis
        # Only try if we have SEC data (not Yahoo data)
        if result.get('source') != 'yahoo_finance':
            try:
                xbrl_data = get_segment_revenue_from_xbrl(cik, company_name, mcp_funcs=mcp_funcs)
                if xbrl_data.get('success'):
                    result['segment_revenue'] = xbrl_data.get('segment_revenue', {})
                    result['geographic_revenue'] = xbrl_data.get('geographic_revenue', {})
                    result['xbrl_period'] = xbrl_data.get('period')
                    result['xbrl_consolidated'] = xbrl_data.get('consolidated_revenue', 0)
            except Exception as e:
                print(f"   XBRL segment extraction failed: {e}")

        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'revenue': {}, 'rd_expense': {}, 'net_income': {}, 'success': False, 'error': str(e)}
