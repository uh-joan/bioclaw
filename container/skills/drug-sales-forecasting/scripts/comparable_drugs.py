"""Comparable drug analysis module.

Finds and analyzes comparable drugs based on:
- Same therapeutic target
- Same indication
- Same drug class/mechanism
"""

import sys
import os

# Add parent directories to path for imports
_script_dir = os.path.dirname(os.path.abspath(__file__))
_claude_dir = os.path.dirname(os.path.dirname(os.path.dirname(_script_dir)))
sys.path.insert(0, _claude_dir)

# Import dynamic brand lookup functions from pipeline skill
_pipeline_skill_dir = os.path.join(
    os.path.dirname(_script_dir),
    '..',
    'indication-drug-pipeline-breakdown',
    'scripts'
)
sys.path.insert(0, _pipeline_skill_dir)

from typing import Dict, Any, Optional, List

# Import dynamic brand lookup from pipeline skill (no hardcoding!)
try:
    from brand_lookup import (
        get_brand_name_from_fda,
        get_brand_name_from_pubchem,
        get_brand_name_from_drugbank,
        get_brand_name_from_ema
    )
    _BRAND_LOOKUP_AVAILABLE = True
except ImportError:
    _BRAND_LOOKUP_AVAILABLE = False
    print("  Warning: brand_lookup module not available, brand name lookup disabled")


# In-memory cache for brand name lookups (avoid repeated API calls)
_BRAND_NAME_CACHE: Dict[str, Optional[str]] = {}


def _get_all_brand_names_from_fda(generic_name: str, mcp_funcs: Dict[str, Any]) -> List[str]:
    """
    Get ALL brand names for a drug from FDA API.

    Returns list of brand names sorted by FDA label count (most common first).
    Uses a two-stage approach:
    1. Get drug labels to verify the exact generic name
    2. Extract brand names from labels where generic_name matches

    Args:
        generic_name: Generic drug name
        mcp_funcs: MCP functions dictionary from skill_executor
    """
    fda_lookup = mcp_funcs.get('fda_lookup')
    if not fda_lookup:
        return []

    brands = []
    seen = set()
    generic_lower = generic_name.lower().strip()

    # CRITICAL FIX (2026-01-21): Use label search and verify generic_name field
    # The count API with field search doesn't work with MCP (special char restrictions)
    # Instead, fetch labels and extract brands where generic_name matches exactly

    try:
        # Strategy 1: Search labels by drug name, then validate generic_name field
        fda_result = fda_lookup(
            search_term=generic_name,
            search_type='label',
            limit=50  # Get enough labels to find all brand variants
        )

        if fda_result and fda_result.get('success'):
            data = fda_result.get('data', {})
            results = data.get('results', [])
            if not results and 'data' in data:
                results = data.get('data', {}).get('results', [])

            for label in results:
                if not isinstance(label, dict):
                    continue

                openfda = label.get('openfda', {})

                # CRITICAL: Verify generic_name matches our search
                # This prevents cross-contamination (e.g., Glucagon -> OZEMPIC)
                generic_names = [g.lower() for g in openfda.get('generic_name', [])]
                if not any(generic_lower in g for g in generic_names):
                    continue  # Skip - this label is for a different drug

                # Extract brand names from this label
                brand_names = openfda.get('brand_name', [])
                for brand in brand_names:
                    if not brand:
                        continue

                    # Skip if brand IS the generic name
                    if brand.lower() == generic_lower:
                        continue

                    # Clean up dosage form suffixes
                    clean_brand = brand
                    for suffix in ['SUBLINGUAL', 'INJECTION', 'ORAL', 'TABLET', 'CAPSULE',
                                   'SOLUTION', 'SUSPENSION', 'PEN', 'FLEXPEN', 'SOLOSTAR',
                                   'KWIKPEN', 'AUTOINJECTOR', 'SYRINGE']:
                        if clean_brand.upper().endswith(' ' + suffix):
                            clean_brand = clean_brand[:-len(suffix)-1].strip()

                    if clean_brand and len(clean_brand) > 1 and clean_brand.upper() not in seen:
                        seen.add(clean_brand.upper())
                        brands.append(clean_brand)

    except Exception as e:
        print(f"    FDA label search error: {e}")

    return brands


def _get_best_brand_for_medicare(generic_name: str, brand_candidates: List[str], mcp_funcs: Dict[str, Any]) -> Optional[str]:
    """
    Select the brand with highest Medicare spending from candidates.

    This ensures we pick the most commercially relevant brand name.
    Checks up to 5 top candidates (ordered by FDA label count).

    OPTIMIZATION (2026-01-21): Limit to top 5 candidates since FDA
    returns brands sorted by label count (most common first).
    """
    if not brand_candidates:
        return None

    if len(brand_candidates) == 1:
        return brand_candidates[0]

    medicare_spending = mcp_funcs.get('medicare_spending')
    if not medicare_spending:
        return brand_candidates[0]  # Fallback to first candidate

    best_brand = None
    best_spending = 0

    # Check top 5 candidates (FDA returns sorted by label count, most common first)
    for brand in brand_candidates[:5]:
        try:
            result = medicare_spending(
                spending_drug_name=brand,
                spending_type='part_d',
                size=1
            )
            drugs = result.get('drugs', [])
            if drugs:
                spending_by_year = drugs[0].get('spending_by_year', {})
                if spending_by_year:
                    years = sorted(spending_by_year.keys(), reverse=True)
                    if years:
                        latest = spending_by_year[years[0]]
                        spending = float(latest.get('total_spending', 0))
                        if spending > best_spending:
                            best_spending = spending
                            best_brand = brand
        except Exception:
            pass

    return best_brand or brand_candidates[0]


def get_brand_name(generic_name: str, mcp_funcs: Dict[str, Any] = None) -> Optional[str]:
    """
    Get the BEST brand name for a generic drug DYNAMICALLY via API lookups.

    Strategy: Get all brand names from FDA, then select the one with highest
    Medicare Part D spending (ensures most commercially relevant brand).

    Fallback chain (no hardcoding!):
    1. FDA drug labels API - get ALL brands, pick highest Medicare spending
    2. PubChem synonyms (comprehensive international coverage)
    3. DrugBank products API (good for major brands)
    4. EMA medicines database (European fallback)

    Results are cached in-memory to avoid repeated API calls.

    Args:
        generic_name: Generic drug name
        mcp_funcs: MCP functions dictionary from skill_executor

    Returns:
        str: Brand name or None if not found
    """
    if not generic_name:
        return None

    generic_lower = generic_name.lower().strip()

    # Check cache first
    if generic_lower in _BRAND_NAME_CACHE:
        return _BRAND_NAME_CACHE[generic_lower]

    if not _BRAND_LOOKUP_AVAILABLE or not mcp_funcs:
        return None

    brand_name = None

    # Step 1: Try FDA - get ALL brands, pick best for Medicare
    try:
        all_brands = _get_all_brand_names_from_fda(generic_name, mcp_funcs)
        if all_brands:
            brand_name = _get_best_brand_for_medicare(generic_name, all_brands, mcp_funcs)
            if brand_name:
                _BRAND_NAME_CACHE[generic_lower] = brand_name
                return brand_name
    except Exception:
        pass

    # Step 2: Try PubChem (comprehensive international coverage)
    try:
        brand_name = get_brand_name_from_pubchem(generic_name)
        if brand_name:
            _BRAND_NAME_CACHE[generic_lower] = brand_name
            return brand_name
    except Exception:
        pass

    # Step 3: Try DrugBank products
    try:
        drugbank_search = mcp_funcs.get('drugbank_search')
        if drugbank_search:
            # First need to get DrugBank ID
            result = drugbank_search(method='search_by_name', query=generic_name, limit=1)
            data = result.get('data', result)
            results = data.get('results', []) if isinstance(data, dict) else []
            if results:
                drugbank_id = results[0].get('drugbank_id', results[0].get('primary_id'))
                if drugbank_id:
                    brand_name = get_brand_name_from_drugbank(drugbank_id)
                    if brand_name:
                        _BRAND_NAME_CACHE[generic_lower] = brand_name
                        return brand_name
    except Exception:
        pass

    # Step 4: Try EMA (European fallback)
    try:
        brand_name = get_brand_name_from_ema(generic_name)
        if brand_name:
            _BRAND_NAME_CACHE[generic_lower] = brand_name
            return brand_name
    except Exception:
        pass

    # No brand found - cache None to avoid repeated lookups
    _BRAND_NAME_CACHE[generic_lower] = None
    return None


# Cache for generic name lookups (brand -> generic)
_GENERIC_NAME_CACHE: Dict[str, Optional[str]] = {}

def get_generic_name(drug_name: str, mcp_funcs: Dict[str, Any] = None) -> Optional[str]:
    """
    Get the generic name for a drug (works for both brand and generic names).

    Uses FDA labels API first (best for brand name lookup), then falls back to DrugBank.

    Args:
        drug_name: Drug name (can be brand like "Ozempic" or generic like "semaglutide")
        mcp_funcs: MCP functions dictionary from skill_executor

    Returns:
        str: The generic name, or None if not found
    """
    if not drug_name or not mcp_funcs:
        return None

    drug_lower = drug_name.lower().strip()

    # Check cache first
    if drug_lower in _GENERIC_NAME_CACHE:
        return _GENERIC_NAME_CACHE[drug_lower]

    fda_lookup = mcp_funcs.get('fda_lookup')

    # Step 1: Try FDA labels API - works well with brand names
    if fda_lookup:
        try:
            result = fda_lookup(
                search_term=drug_name,
                search_type='label',
                limit=5
            )

            data = result.get('data', result)
            results = data.get('results', []) if isinstance(data, dict) else data if isinstance(data, list) else []

            if results and isinstance(results, list):
                for r in results:
                    openfda = r.get('openfda', {})
                    # Check if brand name matches our search
                    brand_names = [b.lower() for b in openfda.get('brand_name', [])]
                    generic_names = openfda.get('generic_name', [])

                    if drug_lower in brand_names and generic_names:
                        generic = generic_names[0]
                        _GENERIC_NAME_CACHE[drug_lower] = generic
                        return generic

                    # Also check if search term is in generic names (just normalize case)
                    for gn in generic_names:
                        if gn.lower() == drug_lower:
                            _GENERIC_NAME_CACHE[drug_lower] = gn
                            return gn

                # If we got results but no exact brand match, use first result's generic name
                if results:
                    first_generic = results[0].get('openfda', {}).get('generic_name', [])
                    if first_generic:
                        generic = first_generic[0]
                        _GENERIC_NAME_CACHE[drug_lower] = generic
                        return generic
        except Exception:
            pass

    # Step 2: Try DrugBank - works well with generic names
    drugbank_search = mcp_funcs.get('drugbank_search')
    if drugbank_search:
        try:
            result = drugbank_search(
                method='search_by_name',
                query=drug_name,
                limit=5
            )

            data = result.get('data', result)
            results = data.get('results', []) if isinstance(data, dict) else []

            if results and isinstance(results, list):
                # Find best match - prefer exact match on name
                for r in results:
                    name = r.get('name', '').lower()
                    if name == drug_lower:
                        generic = r.get('name')
                        _GENERIC_NAME_CACHE[drug_lower] = generic
                        return generic

                # No exact match, use first result
                generic = results[0].get('name')
                _GENERIC_NAME_CACHE[drug_lower] = generic
                return generic

        except Exception:
            pass

    # Not found
    _GENERIC_NAME_CACHE[drug_lower] = None
    return None


def get_drug_manufacturer(drug_name: str, mcp_funcs: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
    """
    Dynamically get manufacturer info for a drug from DrugBank.

    Tries multiple approaches:
    1. DrugBank products API (labeller field)
    2. Parse manufacturer from drug description text
    3. Known pharma company patterns in description

    Args:
        drug_name: Drug name (generic or brand)
        mcp_funcs: MCP functions dictionary from skill_executor

    Returns:
        dict with manufacturer_name, or None if not found
    """
    import re

    if not mcp_funcs:
        return None

    drugbank_search = mcp_funcs.get('drugbank_search')
    if not drugbank_search:
        return None

    # Known pharma companies for pattern matching in descriptions
    KNOWN_PHARMA_COMPANIES = [
        'Novo Nordisk', 'AbbVie', 'Eli Lilly', 'Pfizer', 'Merck', 'Johnson & Johnson',
        'Bristol-Myers Squibb', 'Roche', 'Novartis', 'Sanofi', 'AstraZeneca',
        'GlaxoSmithKline', 'Amgen', 'Gilead', 'Biogen', 'Regeneron', 'Takeda',
        'Boehringer Ingelheim', 'Bayer', 'Teva', 'Mylan', 'Viatris', 'Moderna',
        'BioNTech', 'Vertex', 'Alexion', 'Incyte', 'Jazz Pharmaceuticals',
        'Horizon Therapeutics', 'Bausch Health', 'Organon', 'Valeant'
    ]

    try:
        # Step 1: Search for drug
        result = drugbank_search(
            method='search_by_name',
            query=drug_name,
            limit=5
        )

        data = result.get('data', result)
        results = data.get('results', []) if isinstance(data, dict) else []

        if not results:
            return None

        drug = results[0] if isinstance(results, list) else results
        drugbank_id = drug.get('drugbank_id', drug.get('primary_id'))

        if not drugbank_id:
            return None

        # Step 2: Try products API first
        try:
            products = drugbank_search(
                method='get_products',
                drugbank_id=drugbank_id
            )

            prod_data = products.get('data', products)
            prod_results = prod_data.get('products', []) if isinstance(prod_data, dict) else []

            if prod_results and isinstance(prod_results, list):
                for prod in prod_results:
                    if isinstance(prod, dict):
                        mfr = prod.get('labeller', prod.get('manufacturer'))
                        if mfr:
                            return {
                                'manufacturer_name': mfr,
                                'drugbank_id': drugbank_id,
                                'source': 'DrugBank products'
                            }
        except Exception:
            pass  # Continue to fallback

        # Step 3: Get drug details and parse description
        try:
            details = drugbank_search(
                method='get_drug_details',
                drugbank_id=drugbank_id
            )

            drug_data = details.get('drug', details.get('data', details))
            description = drug_data.get('description', '') if isinstance(drug_data, dict) else ''

            if description:
                # Look for patterns like "developed by X", "manufactured by X", "marketed by X"
                patterns = [
                    r'developed by ([A-Z][a-zA-Z\s&\-]+?)(?:\s+and|\s*[,.]|\s+in\s)',
                    r'manufactured by ([A-Z][a-zA-Z\s&\-]+?)(?:\s+and|\s*[,.]|\s+in\s)',
                    r'marketed by ([A-Z][a-zA-Z\s&\-]+?)(?:\s+and|\s*[,.]|\s+in\s)',
                    r'produced by ([A-Z][a-zA-Z\s&\-]+?)(?:\s+and|\s*[,.]|\s+in\s)',
                ]

                for pattern in patterns:
                    match = re.search(pattern, description, re.IGNORECASE)
                    if match:
                        mfr = match.group(1).strip()
                        # Validate it's a known pharma company
                        for known in KNOWN_PHARMA_COMPANIES:
                            if known.lower() in mfr.lower() or mfr.lower() in known.lower():
                                return {
                                    'manufacturer_name': known,  # Use standardized name
                                    'drugbank_id': drugbank_id,
                                    'source': 'DrugBank description'
                                }

                # Fallback: Check if any known company is mentioned in description
                for company in KNOWN_PHARMA_COMPANIES:
                    if company.lower() in description.lower():
                        return {
                            'manufacturer_name': company,
                            'drugbank_id': drugbank_id,
                            'source': 'DrugBank description (mention)'
                        }

        except Exception:
            pass

    except Exception as e:
        print(f"  Note: Could not get manufacturer from DrugBank: {e}")

    return None


# ============================================================================
# SEC Company Tickers Cache (for CIK/Ticker lookup)
# Fetches from https://www.sec.gov/files/company_tickers.json
# ============================================================================

import urllib.request
import time as _time

_SEC_TICKERS_CACHE: Optional[Dict[str, Any]] = None
_SEC_TICKERS_CACHE_TIME: Optional[float] = None
_SEC_TICKERS_CACHE_TTL = 3600  # Cache for 1 hour


def get_sec_company_tickers() -> Dict[str, Any]:
    """Fetch and cache SEC company_tickers.json for CIK/ticker lookup."""
    global _SEC_TICKERS_CACHE, _SEC_TICKERS_CACHE_TIME

    # Check cache validity
    if _SEC_TICKERS_CACHE and _SEC_TICKERS_CACHE_TIME:
        if _time.time() - _SEC_TICKERS_CACHE_TIME < _SEC_TICKERS_CACHE_TTL:
            return _SEC_TICKERS_CACHE

    try:
        url = "https://www.sec.gov/files/company_tickers.json"
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Drug Sales Forecasting Tool contact@example.com',
                'Accept-Encoding': 'gzip, deflate',
                'Accept': 'application/json'
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            import json
            import gzip
            raw_data = response.read()
            # Handle gzip-compressed response
            if raw_data[:2] == b'\x1f\x8b':  # gzip magic bytes
                raw_data = gzip.decompress(raw_data)
            data = json.loads(raw_data.decode('utf-8'))
            _SEC_TICKERS_CACHE = data
            _SEC_TICKERS_CACHE_TIME = _time.time()
            return data
    except Exception as e:
        print(f"    Warning: Failed to fetch SEC tickers: {e}")
        return {}


def lookup_company_in_sec_tickers(company_name: str) -> Optional[tuple]:
    """
    Look up company in SEC tickers JSON by name.
    Returns (cik, ticker) tuple or None if not found.
    """
    tickers_data = get_sec_company_tickers()
    if not tickers_data:
        return None

    # Normalize search term
    search_name = company_name.upper().strip()

    # Remove common suffixes for matching
    for suffix in [' PHARMACEUTICALS', ' THERAPEUTICS', ' BIOSCIENCES', ' BIOPHARMA',
                   ' BIOTHERAPEUTICS', ' BIOTECHNOLOGY', ' BIOTECH', ' INC', ' CORP',
                   ' LLC', ' LTD', ' CO', ' SCIENCES', ' MEDICAL', ' HEALTH',
                   ' INC.', ' CORP.', ' LLC.', ' LTD.', ' A/S', ' AS', ' S.A.', ' PLC']:
        search_name = search_name.replace(suffix, '')
    search_name = search_name.strip()

    best_match = None
    best_score = 0

    for key, company in tickers_data.items():
        sec_title = company.get('title', '').upper()
        sec_ticker = company.get('ticker', '')
        sec_cik = str(company.get('cik_str', ''))

        # Normalize SEC title
        normalized_title = sec_title
        for suffix in [' PHARMACEUTICALS', ' THERAPEUTICS', ' BIOSCIENCES', ' BIOPHARMA',
                       ' BIOTHERAPEUTICS', ' BIOTECHNOLOGY', ' BIOTECH', ' INC', ' CORP',
                       ' LLC', ' LTD', ' CO', ' SCIENCES', ' MEDICAL', ' HEALTH',
                       ' INC.', ' CORP.', ' LTD.', ' LLC.', ' A/S', ' AS', ' S.A.', ' PLC']:
            normalized_title = normalized_title.replace(suffix, '')
        normalized_title = normalized_title.strip()

        # Exact match (highest priority)
        if normalized_title == search_name:
            return (sec_cik.zfill(10), sec_ticker)

        # Match if first word matches and has good overlap
        search_words = search_name.split()
        title_words = normalized_title.split()

        if search_words and title_words:
            if search_words[0] == title_words[0]:
                # Exact first word match
                score = 100 + len(search_words[0])
                if score > best_score:
                    best_score = score
                    best_match = (sec_cik.zfill(10), sec_ticker)
            elif search_words[0] in normalized_title or normalized_title.startswith(search_words[0]):
                # Partial match
                score = 50
                if score > best_score:
                    best_score = score
                    best_match = (sec_cik.zfill(10), sec_ticker)

    return best_match


def search_manufacturer_ticker(manufacturer_name: str, mcp_funcs: Dict[str, Any] = None) -> Optional[str]:
    """
    Search for a pharma company's stock ticker.

    Uses SEC company_tickers.json (most reliable) with MCP fallback.

    Args:
        manufacturer_name: Company name (e.g., "Novo Nordisk", "AbbVie")
        mcp_funcs: MCP functions dictionary from skill_executor

    Returns:
        Stock ticker (e.g., "NVO", "ABBV") or None
    """
    if not manufacturer_name:
        return None

    # Step 1: PRIMARY METHOD - Use SEC company_tickers.json (most reliable)
    sec_lookup = lookup_company_in_sec_tickers(manufacturer_name)
    if sec_lookup:
        cik, ticker = sec_lookup
        return ticker

    # Step 2: FALLBACK - Try SEC MCP search_companies API
    if mcp_funcs:
        sec_search_companies = mcp_funcs.get('sec_search_companies')
        if sec_search_companies:
            try:
                # Clean up company name for search
                search_name = manufacturer_name.replace('Inc.', '').replace('Inc', '')
                search_name = search_name.replace('Corp.', '').replace('Corp', '')
                search_name = search_name.replace('LLC', '').replace('Ltd', '').strip()

                result = sec_search_companies(query=search_name)

                # Check for errors
                if result and not result.get('error'):
                    data = result.get('data', result)
                    companies = data.get('companies', data.get('results', []))

                    if companies and isinstance(companies, list):
                        company = companies[0]
                        ticker = company.get('ticker', company.get('symbol'))
                        if ticker:
                            return ticker
            except Exception:
                pass

    print(f"    Note: Could not find ticker for {manufacturer_name}")
    return None


def _match_segment_to_indication(
    segments: Dict[str, Any],
    indication: str,
    drug_name: str
) -> Optional[Dict[str, Any]]:
    """
    Match SEC/Yahoo segment data to drug indication dynamically.

    Uses fuzzy matching based on indication keywords.

    Args:
        segments: Dict of segment_name -> revenue value or dict
        indication: Drug indication
        drug_name: Drug name

    Returns:
        dict with segment_name, segment_revenue, match_score
    """
    # Build keyword list from indication and drug name
    keywords = []
    if indication:
        keywords.extend(indication.lower().split())
    keywords.append(drug_name.lower())

    # Dynamic keyword categories for pharma segment matching
    # These help bridge gap between indication terms and segment names
    segment_keywords = {
        'diabetes': ['diabetes', 'metabolic', 'glp', 'insulin', 'endocrine', 'glucose'],
        'obesity': ['obesity', 'weight', 'metabolic', 'diet'],
        'oncology': ['oncology', 'cancer', 'tumor', 'immuno-oncology', 'hematology'],
        'immunology': ['immunology', 'inflammation', 'rheumatoid', 'arthritis', 'autoimmune', 'tnf'],
        'cardiovascular': ['cardiovascular', 'heart', 'cardio', 'vascular', 'hypertension'],
        'neurology': ['neurology', 'neuro', 'cns', 'brain', 'alzheimer', 'parkinson', 'psych'],
        'respiratory': ['respiratory', 'lung', 'asthma', 'copd', 'pulmonary'],
        'infectious': ['infectious', 'vaccine', 'antiviral', 'antibacterial', 'hiv'],
    }

    best_match = None
    best_score = 0

    for segment_name, segment_data in segments.items():
        segment_lower = segment_name.lower()
        score = 0

        # Direct segment name match with keywords
        for keyword in keywords:
            if keyword in segment_lower:
                score += 10

        # Check category keyword mappings
        for category, category_keywords in segment_keywords.items():
            if any(kw in segment_lower for kw in category_keywords):
                # Check if indication matches this category
                if any(kw in ' '.join(keywords) for kw in category_keywords):
                    score += 5

        if score > best_score:
            best_score = score
            revenue = segment_data if isinstance(segment_data, (int, float)) else segment_data.get('revenue', segment_data.get('value', 0))
            best_match = {
                'segment_name': segment_name,
                'segment_revenue': revenue,
                'match_score': score
            }

    return best_match


def get_manufacturer_segment_revenue_sec(
    ticker: str,
    indication: str = None,
    drug_name: str = None,
    mcp_funcs: Dict[str, Any] = None
) -> Optional[Dict[str, Any]]:
    """
    Get segment revenue from SEC XBRL dimensional analysis.

    Primary source - uses SEC time_series_dimensional_analysis for
    segment-level revenue breakdown from 10-K/10-Q filings.

    Args:
        ticker: Stock ticker
        indication: Drug indication (for segment matching)
        drug_name: Drug name (for segment matching)
        mcp_funcs: MCP functions dictionary from skill_executor

    Returns:
        dict with segment_name, segment_revenue, total_revenue, source='SEC XBRL'
    """
    # TODO: time_series_dimensional_analysis not yet in wrapper
    # For now, return None to use Yahoo Finance fallback
    return None


def _parse_yahoo_revenue_markdown(text: str) -> Dict[str, float]:
    """
    Parse Yahoo Finance revenue breakdown from markdown table format.

    The API returns markdown like:
    | Segment | Revenue |
    |---------|---------|
    | Diabetes | $33.27B |
    | Obesity | $12.62B |

    Returns:
        dict: segment_name -> revenue in dollars
    """
    import re
    segments = {}

    # Find table rows with segment/revenue pattern
    # Pattern matches: | Segment Name | $XX.XXB/M/K |
    pattern = r'\|\s*([^|]+?)\s*\|\s*\$?([\d,.]+)\s*([BMK])?\s*\|'

    for match in re.finditer(pattern, text):
        segment_name = match.group(1).strip()
        value_str = match.group(2).replace(',', '')
        unit = match.group(3)

        # Skip header rows and total rows
        if segment_name.lower() in ('segment', 'region', '**total**', 'total', '------'):
            continue
        if '---' in segment_name:
            continue

        try:
            value = float(value_str)
            # Convert to dollars based on unit
            if unit == 'B':
                value *= 1e9
            elif unit == 'M':
                value *= 1e6
            elif unit == 'K':
                value *= 1e3

            # Clean segment name (remove markdown bold)
            segment_name = segment_name.replace('**', '').strip()

            if segment_name and value > 0:
                segments[segment_name] = value

        except (ValueError, TypeError):
            continue

    return segments


def get_manufacturer_segment_revenue_yahoo(
    ticker: str,
    indication: str = None,
    drug_name: str = None,
    mcp_funcs: Dict[str, Any] = None
) -> Optional[Dict[str, Any]]:
    """
    Get segment revenue from Yahoo Finance (fallback).

    Parses the markdown table response from Yahoo Finance API.

    Args:
        ticker: Stock ticker
        indication: Drug indication (for segment matching)
        drug_name: Drug name (for segment matching)
        mcp_funcs: MCP functions dictionary from skill_executor

    Returns:
        dict with segment_name, segment_revenue, total_revenue, source='Yahoo Finance'
    """
    if not mcp_funcs:
        return None

    financials_lookup = mcp_funcs.get('financials_lookup')
    if not financials_lookup:
        return None

    try:
        revenue_result = financials_lookup(
            method='stock_revenue_breakdown',
            symbol=ticker
        )

        # Yahoo Finance returns markdown text, not structured data
        text = ''
        if isinstance(revenue_result, dict):
            text = revenue_result.get('text', str(revenue_result))
        elif isinstance(revenue_result, str):
            text = revenue_result

        if not text:
            return None

        # Parse markdown table to extract segments
        segments = _parse_yahoo_revenue_markdown(text)

        if not segments:
            print(f"    No segments parsed from Yahoo Finance response")
            return None

        # Match to indication
        matched = _match_segment_to_indication(
            segments,
            indication or '',
            drug_name or ''
        )

        total = sum(segments.values())

        if matched:
            matched['ticker'] = ticker
            matched['source'] = 'Yahoo Finance'
            matched['total_revenue'] = total
            matched['all_segments'] = segments  # Include all segments for reference
            return matched

        # No match - return total with all segments
        return {
            'segment_name': 'Total Company',
            'segment_revenue': total,
            'total_revenue': total,
            'ticker': ticker,
            'source': 'Yahoo Finance',
            'match_score': 0,
            'all_segments': segments
        }

    except Exception as e:
        print(f"    Yahoo Finance failed: {e}")
        return None


def get_manufacturer_segment_revenue(
    drug_name: str,
    indication: str = None,
    mcp_funcs: Dict[str, Any] = None
) -> Optional[Dict[str, Any]]:
    """
    Dynamically fetch manufacturer segment revenue.

    Fallback chain:
    1. Get manufacturer name from DrugBank
    2. Search for ticker via SEC company search
    3. Try SEC XBRL dimensional analysis (primary)
    4. Fallback to Yahoo Finance revenue breakdown

    Args:
        drug_name: Drug name
        indication: Drug indication (helps match segment)
        mcp_funcs: MCP functions dictionary from skill_executor

    Returns:
        dict with segment_name, segment_revenue, total_revenue, ticker, source
    """
    if not mcp_funcs:
        return None

    # Step 1: Get manufacturer from DrugBank
    mfr_info = get_drug_manufacturer(drug_name, mcp_funcs)
    if not mfr_info:
        return None

    manufacturer_name = mfr_info['manufacturer_name']
    print(f"    Manufacturer: {manufacturer_name}")

    # Step 2: Search for ticker via SEC
    ticker = search_manufacturer_ticker(manufacturer_name, mcp_funcs)
    if not ticker:
        return None

    print(f"    Ticker: {ticker}")

    # Step 3: Try SEC XBRL first (more detailed dimensional data)
    print(f"    Trying SEC XBRL dimensional analysis...")
    sec_result = get_manufacturer_segment_revenue_sec(
        ticker=ticker,
        indication=indication,
        drug_name=drug_name,
        mcp_funcs=mcp_funcs
    )

    if sec_result and sec_result.get('segment_revenue', 0) > 0:
        sec_result['manufacturer'] = manufacturer_name
        print(f"    ✓ SEC XBRL: {sec_result['segment_name']} = ${sec_result['segment_revenue']:,.0f}")
        return sec_result

    # Step 4: Fallback to Yahoo Finance
    print(f"    Trying Yahoo Finance fallback...")
    yahoo_result = get_manufacturer_segment_revenue_yahoo(
        ticker=ticker,
        indication=indication,
        drug_name=drug_name,
        mcp_funcs=mcp_funcs
    )

    if yahoo_result:
        yahoo_result['manufacturer'] = manufacturer_name
        print(f"    ✓ Yahoo Finance: {yahoo_result['segment_name']} = ${yahoo_result['segment_revenue']:,.0f}")
        return yahoo_result

    # Nothing worked
    print(f"    ✗ No segment revenue found")
    return None


def get_drug_details(drug_name: str, mcp_funcs: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Get detailed drug information from DrugBank.

    Args:
        drug_name: Drug name (brand or generic)
        mcp_funcs: MCP functions dictionary from skill_executor

    Returns:
        dict: Drug details including targets, categories, mechanism, brand_name
    """
    result = {
        'drug_name': drug_name,
        'drugbank_id': None,
        'generic_name': None,
        'brand_name': None,  # Added for Medicare lookups
        'drug_type': None,
        'categories': [],
        'targets': [],
        'mechanism': None,
        'indication': None
    }

    if not mcp_funcs:
        return result

    drugbank_search = mcp_funcs.get('drugbank_search')
    if not drugbank_search:
        return result

    try:
        # Search for drug
        search_result = drugbank_search(
            method='search_by_name',
            query=drug_name,
            limit=5
        )

        data = search_result.get('data', search_result)
        results = data.get('results', []) if isinstance(data, dict) else []

        if results:
            drug = results[0] if isinstance(results, list) else results

            result['drugbank_id'] = drug.get('drugbank_id', drug.get('primary_id'))
            result['generic_name'] = drug.get('name', drug.get('generic_name'))
            result['drug_type'] = drug.get('type', drug.get('drug_type'))

            # Look up brand name from our mapping
            generic_name = result['generic_name']
            if generic_name:
                result['brand_name'] = get_brand_name(generic_name, mcp_funcs)

            # Get more details if we have a DrugBank ID
            if result['drugbank_id']:
                try:
                    details = drugbank_search(
                        method='get_drug_details',
                        drugbank_id=result['drugbank_id']
                    )

                    # API returns data under 'drug' key
                    detail_data = details.get('drug', details.get('data', details))
                    if isinstance(detail_data, dict):
                        result['categories'] = detail_data.get('categories', [])
                        result['targets'] = detail_data.get('targets', [])
                        result['mechanism'] = detail_data.get('mechanism_of_action')
                        result['indication'] = detail_data.get('indication')
                except Exception as e:
                    print(f"  Warning: Could not get drug details: {e}")

    except Exception as e:
        print(f"  Warning: DrugBank search failed: {e}")

    return result


def find_drugs_by_target(target: str, limit: int = 20, mcp_funcs: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Find drugs that target the same protein/receptor.

    Args:
        target: Target name (e.g., "GLP-1 receptor", "COX-2")
        limit: Maximum results
        mcp_funcs: MCP functions dictionary from skill_executor

    Returns:
        list: Drugs targeting the same target
    """
    drugs = []

    if not mcp_funcs:
        return drugs

    drugbank_search = mcp_funcs.get('drugbank_search')
    if not drugbank_search:
        return drugs

    try:
        result = drugbank_search(
            method='search_by_target',
            target=target,
            limit=limit
        )

        data = result.get('data', result)
        results = data.get('results', []) if isinstance(data, dict) else []

        for drug in results:
            if isinstance(drug, dict):
                drugs.append({
                    'name': drug.get('name', drug.get('generic_name')),
                    'drugbank_id': drug.get('drugbank_id', drug.get('primary_id')),
                    'type': drug.get('type', drug.get('drug_type'))
                })

    except Exception as e:
        print(f"  Warning: Target search failed: {e}")

    return drugs


def find_drugs_by_indication(indication: str, limit: int = 20, mcp_funcs: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Find drugs approved for the same indication.

    Args:
        indication: Medical indication
        limit: Maximum results
        mcp_funcs: MCP functions dictionary from skill_executor

    Returns:
        list: Drugs with the same indication
    """
    drugs = []

    if not mcp_funcs:
        return drugs

    drugbank_search = mcp_funcs.get('drugbank_search')
    if not drugbank_search:
        return drugs

    try:
        result = drugbank_search(
            method='search_by_indication',
            query=indication,
            limit=limit
        )

        data = result.get('data', result)
        results = data.get('results', []) if isinstance(data, dict) else []

        for drug in results:
            if isinstance(drug, dict):
                drugs.append({
                    'name': drug.get('name', drug.get('generic_name')),
                    'drugbank_id': drug.get('drugbank_id', drug.get('primary_id')),
                    'type': drug.get('type', drug.get('drug_type'))
                })

    except Exception as e:
        print(f"  Warning: Indication search failed: {e}")

    return drugs


def get_competitive_landscape(indication: str) -> Dict[str, Any]:
    """
    Analyze competitive landscape for an indication.

    Uses the indication-drug-pipeline-breakdown skill for comprehensive analysis.
    Runs with skip_regulatory=True for fast results (no FDA/EMA approval checks).

    Args:
        indication: Medical indication

    Returns:
        dict: Competitive landscape analysis with trials, phases, sponsors, drugs
    """
    result = {
        'indication': indication,
        'total_active_trials': 0,
        'phase_distribution': {},
        'top_sponsors': [],
        'active_drugs': [],
        'total_unique_drugs': 0,
        'total_enrollment': 0
    }

    try:
        # Import the pipeline skill - insert at FRONT of path to override local modules
        pipeline_skill_dir = os.path.join(
            os.path.dirname(_script_dir),
            'indication-drug-pipeline-breakdown',
            'scripts'
        )
        # Remove any existing entry first, then insert at front
        if pipeline_skill_dir in sys.path:
            sys.path.remove(pipeline_skill_dir)
        sys.path.insert(0, pipeline_skill_dir)

        # Force reimport of pipeline's progress_tracker to avoid conflicts
        import importlib
        if 'progress_tracker' in sys.modules:
            del sys.modules['progress_tracker']

        from get_indication_drug_pipeline_breakdown import get_indication_drug_pipeline_breakdown

        # Run pipeline analysis with skip_regulatory=True for speed
        # This gets trial/phase/company data without slow FDA/EMA checks
        pipeline_result = get_indication_drug_pipeline_breakdown(
            indication=indication,
            skip_regulatory=True,  # Fast mode - no regulatory checks needed
            sample_per_phase=30    # Sample for speed, still representative
        )

        # Extract relevant data for competitive landscape
        result['total_active_trials'] = pipeline_result.get('total_trials', 0)
        result['total_unique_drugs'] = pipeline_result.get('total_unique_drugs', 0)
        result['total_enrollment'] = pipeline_result.get('total_enrollment', 0)

        # Phase distribution from pipeline
        phase_breakdown = pipeline_result.get('phase_breakdown', {})
        phase_distribution = {}
        active_drugs = []
        for phase_name, phase_data in phase_breakdown.items():
            if isinstance(phase_data, dict):
                phase_distribution[phase_name] = phase_data.get('trials', 0)
                # Collect drugs from each phase
                phase_drugs = phase_data.get('drugs', [])
                active_drugs.extend(phase_drugs)

        result['phase_distribution'] = phase_distribution
        result['active_drugs'] = list(set(active_drugs))[:30]  # Dedupe, limit for display

        # Top sponsors from pipeline companies data
        companies = pipeline_result.get('companies', [])
        top_sponsors = [
            (c['company'], c['trials'])
            for c in companies
            if isinstance(c, dict) and c.get('company')
        ]
        result['top_sponsors'] = top_sponsors[:10]

        # Include sponsor type breakdown
        result['sponsor_breakdown'] = pipeline_result.get('sponsor_breakdown', {})

    except ImportError as e:
        print(f"  Warning: Pipeline skill not available, using fallback: {e}")
        # Fallback to simple CT.gov search if pipeline skill unavailable
        result = _get_competitive_landscape_fallback(indication)
    except Exception as e:
        print(f"  Warning: Competitive landscape analysis failed: {e}")

    return result


def _get_competitive_landscape_fallback(indication: str) -> Dict[str, Any]:
    """
    Fallback competitive landscape using direct CT.gov search.
    Used only if pipeline skill is unavailable.
    """
    import re

    result = {
        'indication': indication,
        'total_active_trials': 0,
        'phase_distribution': {},
        'top_sponsors': [],
        'active_drugs': []
    }

    try:
        trials_response = ct_gov_search(
            condition=indication,
            status='RECRUITING',
            pageSize=100
        )

        text = trials_response if isinstance(trials_response, str) else trials_response.get('text', str(trials_response))

        # Parse total from "X of Y studies found"
        match = re.search(r'(\d+) of (\d+) studies found', text)
        if match:
            result['total_active_trials'] = int(match.group(2))
        else:
            nct_ids = re.findall(r'NCT\d{8}', text)
            result['total_active_trials'] = len(nct_ids)

        # Parse phases
        phase_counts = {}
        for phase in re.findall(r'\*\*Phase:\*\*\s*(\w+)', text):
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
        result['phase_distribution'] = phase_counts

        # Parse sponsors
        sponsors = {}
        for sponsor in re.findall(r'\*\*(?:Sponsor|Lead Sponsor):\*\*\s*([^\n*]+)', text):
            sponsor = sponsor.strip()
            if sponsor:
                sponsors[sponsor] = sponsors.get(sponsor, 0) + 1
        result['top_sponsors'] = sorted(sponsors.items(), key=lambda x: x[1], reverse=True)[:10]

    except Exception as e:
        print(f"  Warning: Fallback competitive landscape failed: {e}")

    return result


def find_comparable_drugs(
    drug_name: str,
    indication: str = None,
    mcp_funcs: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Find comparable drugs and analyze their market performance.

    Args:
        drug_name: Reference drug name
        indication: Primary indication (optional, will be inferred if not provided)
        mcp_funcs: MCP functions dictionary from skill_executor

    Returns:
        dict: Comparable drugs with market data
    """
    if not mcp_funcs:
        return {'drug_name': drug_name, 'error': 'mcp_funcs required'}

    print(f"  Getting drug details...")
    drug_details = get_drug_details(drug_name, mcp_funcs)

    # Get comparable drugs by different criteria
    comparables = {
        'by_target': [],
        'by_indication': [],
        'by_category': []
    }

    # Find by target
    if drug_details.get('targets'):
        for target in drug_details['targets'][:2]:  # Limit to first 2 targets
            target_name = target.get('name', target) if isinstance(target, dict) else target
            if target_name:
                print(f"  Finding drugs by target: {target_name}...")
                target_drugs = find_drugs_by_target(target_name, limit=10, mcp_funcs=mcp_funcs)
                comparables['by_target'].extend(target_drugs)

    # Find by indication
    search_indication = indication or drug_details.get('indication', '')
    if search_indication:
        print(f"  Finding drugs by indication: {search_indication[:50]}...")
        indication_drugs = find_drugs_by_indication(search_indication, limit=10, mcp_funcs=mcp_funcs)
        comparables['by_indication'] = indication_drugs

    # Deduplicate and get spending data for top comparables
    seen_names = {drug_name.lower()}
    unique_comparables = []

    all_comps = comparables['by_target'] + comparables['by_indication']
    for comp in all_comps:
        name = comp.get('name', '').lower()
        if name and name not in seen_names:
            seen_names.add(name)
            unique_comparables.append(comp)

    # Get spending data for top comparables
    # CRITICAL FIX (2026-01-21): Apply brand name lookup before Medicare search
    # Medicare API works with brand names, not generic names
    print(f"  Getting spending data for {min(5, len(unique_comparables))} comparables...")
    medicare_spending = mcp_funcs.get('medicare_spending')
    enriched_comparables = []
    for comp in unique_comparables[:5]:
        generic_name = comp.get('name')
        if generic_name:
            try:
                # CRITICAL FIX: Look up brand name for Medicare API
                brand_name = get_brand_name(generic_name, mcp_funcs)
                search_name = brand_name or generic_name

                if medicare_spending:
                    spending = medicare_spending(
                        spending_drug_name=search_name,
                        spending_type="part_d",
                        size=5
                    )
                else:
                    spending = {}
                data = spending.get('data', spending)

                # Handle different response formats
                drugs = data.get('drugs', []) if isinstance(data, dict) else []
                results = data.get('results', []) if isinstance(data, dict) else []

                total_spend = 0

                # Try 'drugs' format first (newer API response)
                if drugs:
                    for drug in drugs:
                        if isinstance(drug, dict):
                            spending_by_year = drug.get('spending_by_year', {})
                            if spending_by_year:
                                # Get latest year spending
                                years = sorted(spending_by_year.keys(), reverse=True)
                                if years:
                                    latest = spending_by_year[years[0]]
                                    total_spend = float(latest.get('total_spending', 0))
                                    break

                # Fallback to 'results' format
                if total_spend == 0 and results:
                    for item in results:
                        if isinstance(item, dict):
                            spend = item.get('Tot_Spndng', item.get('total_spending', 0))
                            total_spend += float(spend) if spend else 0

                comp['medicare_spending'] = total_spend
                comp['brand_name_used'] = brand_name  # Track for debugging
            except Exception as e:
                comp['medicare_spending'] = 0
                comp['spending_error'] = str(e)

            enriched_comparables.append(comp)

    # Get competitive landscape
    if search_indication:
        print(f"  Analyzing competitive landscape...")
        landscape = get_competitive_landscape(search_indication)
    else:
        landscape = {}

    return {
        'drug_name': drug_name,
        'drug_details': drug_details,
        'comparable_drugs': enriched_comparables,
        'competitive_landscape': landscape
    }


if __name__ == "__main__":
    # Test with a known drug
    if len(sys.argv) > 1:
        drug = sys.argv[1]
        indication = sys.argv[2] if len(sys.argv) > 2 else None
    else:
        drug = "semaglutide"
        indication = "type 2 diabetes"

    print(f"\n🔍 Comparable Drug Analysis for: {drug}")
    print("=" * 60)

    result = find_comparable_drugs(drug, indication)

    print(f"\nDrug Details:")
    details = result['drug_details']
    print(f"  Generic Name: {details.get('generic_name')}")
    print(f"  DrugBank ID: {details.get('drugbank_id')}")
    print(f"  Type: {details.get('drug_type')}")

    print(f"\nComparable Drugs:")
    for comp in result['comparable_drugs']:
        spend = comp.get('medicare_spending')
        spend_str = f"${spend:,.0f}" if spend else "N/A"
        print(f"  • {comp['name']} - Medicare Spending: {spend_str}")

    landscape = result['competitive_landscape']
    if landscape:
        print(f"\nCompetitive Landscape:")
        print(f"  Active Trials: {landscape.get('total_active_trials', 0)}")
        print(f"  Phase Distribution: {landscape.get('phase_distribution', {})}")
