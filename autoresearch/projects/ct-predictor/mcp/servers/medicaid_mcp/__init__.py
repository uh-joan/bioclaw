"""Medicaid MCP Server - Python API

Provides Python functions for Medicaid data: enrollment trends, drug pricing (NADAC),
quality measures, and program performance from data.medicaid.gov via Socrata SODA API.
Data stays in execution environment - only summaries flow to model.

PROVIDER-LEVEL DATA (via DuckDB on local Parquet):
- get_provider_spending: Filter by NPI/HCPCS/date range
- get_provider_top_services: Top HCPCS codes for a provider
- get_hcpcs_top_providers: Top providers for a HCPCS code (auto-enriched with NPPES identity)
- get_provider_spending_summary: Aggregate stats for an NPI
- get_provider_info: Provider identity lookup (name, specialty, state, ZIP)
- get_hcpcs_spending_by_month: Monthly spending trend for a HCPCS code
Run scripts/download_medicaid_provider_spending.py to fetch the 2.9 GB Parquet.
Run scripts/download_nppes_slim.py to build the NPPES provider lookup (~30-80 MB).

STATE-LEVEL DATA (via Node.js MCP / Socrata API):
- get_nadac_pricing, compare_drug_pricing
- get_enrollment_trends, compare_state_enrollment
- get_drug_rebate_info, search_state_formulary
- get_drug_utilization, get_federal_upper_limits
- list_available_datasets, search_datasets

CRITICAL MEDICAID MCP QUIRKS:
1. State-level data: Aggregates at state level, not individual providers
2. NADAC pricing: National Average Drug Acquisition Cost (updated weekly)
3. NDC codes: 11-digit National Drug Code format (e.g., "00002-7510-01")
4. Date formats: YYYY-MM-DD for queries
5. Enrollment types: total, medicaid, chip, adult, child
6. Socrata API: Uses SoQL WHERE clause syntax for filtering
7. Response limit: max 5000 per query
"""

from mcp.client import get_client
from typing import Dict, Any, Optional, List

from .provider_spending import LOCAL_METHODS as _LOCAL_METHODS


def medicaid_info(
    method: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Unified Medicaid data access function

    Args:
        method: Operation to perform
        **kwargs: Method-specific parameters

    Returns:
        dict: Medicaid API response
    """
    # Route provider-spending methods to local DuckDB
    if method in _LOCAL_METHODS:
        return _LOCAL_METHODS[method](**kwargs)

    # Forward all other methods to Node.js MCP server
    client = get_client('medicaid')

    params = {'method': method}
    params.update(kwargs)

    return client.call_tool('medicaid_info', params)


# =============================================================================
# Drug Pricing (NADAC - National Average Drug Acquisition Cost)
# =============================================================================

def get_nadac_pricing(
    drug_name: Optional[str] = None,
    ndc_code: Optional[str] = None,
    price_date: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Get NADAC drug pricing data (National Average Drug Acquisition Cost)

    NADAC is updated weekly and represents pharmacy acquisition costs.

    Args:
        drug_name: Drug name (partial match supported)
                  Examples: "semaglutide", "insulin", "metformin"

        ndc_code: National Drug Code (11-digit)
                 Example: "00002-7510-01", "00169-7501-11"

        price_date: Specific pricing date (YYYY-MM-DD)
                   Default: latest available

        limit: Maximum results (default: 100, max: 5000)

        offset: Pagination offset (default: 0)

    Returns:
        dict: NADAC pricing data

        Key fields:
        - ndc: National Drug Code
        - drug_name: Drug name
        - nadac_per_unit: Price per unit
        - effective_date: Price effective date
        - pricing_unit: Unit type (EA, ML, GM)

    Examples:
        # Get semaglutide pricing
        results = get_nadac_pricing(
            drug_name="semaglutide",
            limit=50
        )

        for drug in results.get('data', []):
            ndc = drug.get('ndc')
            name = drug.get('drug_name')
            price = drug.get('nadac_per_unit')
            print(f"{name} ({ndc}): ${price}/unit")

        # Specific NDC lookup
        results = get_nadac_pricing(
            ndc_code="00169-7501-11"
        )

        # Historical pricing
        results = get_nadac_pricing(
            drug_name="insulin",
            price_date="2024-01-01"
        )
    """
    params = {
        'limit': limit,
        'offset': offset
    }

    if drug_name:
        params['drug_name'] = drug_name
    if ndc_code:
        params['ndc_code'] = ndc_code
    if price_date:
        params['price_date'] = price_date

    return medicaid_info(method='get_nadac_pricing', **params)


def compare_drug_pricing(
    drug_names: Optional[List[str]] = None,
    ndc_codes: Optional[List[str]] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Compare NADAC pricing across multiple drugs

    Args:
        drug_names: Array of drug names to compare
                   Example: ["semaglutide", "dulaglutide"]

        ndc_codes: Array of NDC codes to compare
                  Example: ["00002-7510-01", "00169-7501-11"]

        limit: Maximum results per drug (default: 100)

    Returns:
        dict: Comparative pricing data

    Examples:
        # Compare GLP-1 drugs
        results = compare_drug_pricing(
            drug_names=["semaglutide", "dulaglutide", "liraglutide"]
        )

        # Compare specific NDCs
        results = compare_drug_pricing(
            ndc_codes=["00002-7510-01", "00169-7501-11"]
        )
    """
    params = {
        'limit': limit
    }

    if drug_names:
        params['drug_names'] = drug_names
    if ndc_codes:
        params['ndc_codes'] = ndc_codes

    return medicaid_info(method='compare_drug_pricing', **params)


# =============================================================================
# Enrollment Data
# =============================================================================

def get_enrollment_trends(
    state: str,
    enrollment_type: str = "total",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Get state Medicaid enrollment trends

    Args:
        state: State abbreviation (REQUIRED)
              Examples: "CA", "TX", "NY", "FL"

        enrollment_type: Type of enrollment data
                        - "total": All Medicaid/CHIP
                        - "medicaid": Medicaid only
                        - "chip": CHIP only
                        - "adult": Adult enrollees
                        - "child": Child enrollees

        start_date: Start date for time range (YYYY-MM-DD)

        end_date: End date for time range (YYYY-MM-DD)

        limit: Maximum results (default: 100)

        offset: Pagination offset (default: 0)

    Returns:
        dict: Enrollment trend data

        Key fields:
        - state: State abbreviation
        - month: Enrollment month
        - enrollment: Total enrollees
        - enrollment_type: Type of enrollment

    Examples:
        # California total enrollment trends
        results = get_enrollment_trends(
            state="CA",
            enrollment_type="total"
        )

        for month in results.get('data', []):
            date = month.get('month')
            count = month.get('enrollment')
            print(f"{date}: {count:,} enrollees")

        # Texas CHIP enrollment for 2024
        results = get_enrollment_trends(
            state="TX",
            enrollment_type="chip",
            start_date="2024-01-01",
            end_date="2024-12-31"
        )

        # Adult vs child enrollment
        adults = get_enrollment_trends(state="NY", enrollment_type="adult")
        children = get_enrollment_trends(state="NY", enrollment_type="child")
    """
    params = {
        'state': state,
        'enrollment_type': enrollment_type,
        'limit': limit,
        'offset': offset
    }

    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date

    return medicaid_info(method='get_enrollment_trends', **params)


def compare_state_enrollment(
    states: List[str],
    month: Optional[str] = None,
    enrollment_type: str = "total"
) -> Dict[str, Any]:
    """
    Compare Medicaid enrollment across multiple states

    Args:
        states: Array of state abbreviations
               Example: ["CA", "TX", "NY"]

        month: Specific month for comparison (YYYY-MM)
              Default: latest available

        enrollment_type: Type of enrollment to compare
                        Values: "total", "medicaid", "chip", "adult", "child"

    Returns:
        dict: State comparison data

    Examples:
        # Compare largest states
        results = compare_state_enrollment(
            states=["CA", "TX", "NY", "FL", "PA"],
            enrollment_type="total"
        )

        for state in results.get('data', []):
            abbrev = state.get('state')
            count = state.get('enrollment')
            print(f"{abbrev}: {count:,}")

        # CHIP comparison for September 2024
        results = compare_state_enrollment(
            states=["CA", "TX"],
            month="2024-09",
            enrollment_type="chip"
        )
    """
    params = {
        'states': states,
        'enrollment_type': enrollment_type
    }

    if month:
        params['month'] = month

    return medicaid_info(method='compare_state_enrollment', **params)


# =============================================================================
# Drug Rebate Program
# =============================================================================

def get_drug_rebate_info(
    drug_name: Optional[str] = None,
    labeler_name: Optional[str] = None,
    rebate_year: Optional[int] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Get Medicaid Drug Rebate Program information

    Args:
        drug_name: Drug name to search

        labeler_name: Manufacturer/labeler name
                     Examples: "Novo Nordisk", "Pfizer"

        rebate_year: Year for rebate data (e.g., 2024, 2023)

        limit: Maximum results (default: 100)

        offset: Pagination offset (default: 0)

    Returns:
        dict: Drug rebate program data

    Examples:
        # Novo Nordisk drugs in rebate program
        results = get_drug_rebate_info(
            labeler_name="Novo Nordisk",
            rebate_year=2024
        )

        # Search by drug name
        results = get_drug_rebate_info(
            drug_name="insulin",
            rebate_year=2024
        )
    """
    params = {
        'limit': limit,
        'offset': offset
    }

    if drug_name:
        params['drug_name'] = drug_name
    if labeler_name:
        params['labeler_name'] = labeler_name
    if rebate_year:
        params['rebate_year'] = rebate_year

    return medicaid_info(method='get_drug_rebate_info', **params)


# =============================================================================
# State Formulary
# =============================================================================

def search_state_formulary(
    drug_name: Optional[str] = None,
    state: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Search state Medicaid formularies (CA, NY, TX, OH, IL)

    Args:
        drug_name: Drug name to search

        state: State abbreviation (CA, NY, TX, OH, IL)
              Only large state formularies available

        limit: Maximum results (default: 100)

        offset: Pagination offset (default: 0)

    Returns:
        dict: State formulary data

    Examples:
        # Search California formulary
        results = search_state_formulary(
            drug_name="semaglutide",
            state="CA"
        )

        # Search Texas formulary
        results = search_state_formulary(
            drug_name="metformin",
            state="TX"
        )
    """
    params = {
        'limit': limit,
        'offset': offset
    }

    if drug_name:
        params['drug_name'] = drug_name
    if state:
        params['state'] = state

    return medicaid_info(method='search_state_formulary', **params)


# =============================================================================
# Drug Utilization
# =============================================================================

def get_drug_utilization(
    drug_name: Optional[str] = None,
    state: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Get state-level prescription utilization data

    Args:
        drug_name: Drug name to search

        state: State abbreviation

        start_date: Start date (YYYY-MM-DD)

        end_date: End date (YYYY-MM-DD)

        limit: Maximum results (default: 100)

        offset: Pagination offset (default: 0)

    Returns:
        dict: Drug utilization data

    Examples:
        # Semaglutide utilization in California
        results = get_drug_utilization(
            drug_name="semaglutide",
            state="CA",
            start_date="2024-01-01",
            end_date="2024-12-31"
        )

        for record in results.get('data', []):
            period = record.get('quarter')
            scripts = record.get('number_of_prescriptions')
            spending = record.get('total_spending')
            print(f"{period}: {scripts:,} prescriptions, ${spending:,.0f}")
    """
    params = {
        'limit': limit,
        'offset': offset
    }

    if drug_name:
        params['drug_name'] = drug_name
    if state:
        params['state'] = state
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date

    return medicaid_info(method='get_drug_utilization', **params)


# =============================================================================
# Federal Upper Limits (FUL)
# =============================================================================

def get_federal_upper_limits(
    drug_name: Optional[str] = None,
    ndc_code: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Get Federal Upper Limit (FUL) pricing

    FUL sets maximum federal matching for generic drugs.

    Args:
        drug_name: Drug name to search

        ndc_code: National Drug Code

        limit: Maximum results (default: 100)

        offset: Pagination offset (default: 0)

    Returns:
        dict: FUL pricing data

    Examples:
        # Get FUL for metformin
        results = get_federal_upper_limits(
            drug_name="metformin"
        )

        for drug in results.get('data', []):
            name = drug.get('drug_name')
            ful = drug.get('ful_amount')
            print(f"{name}: FUL ${ful}")
    """
    params = {
        'limit': limit,
        'offset': offset
    }

    if drug_name:
        params['drug_name'] = drug_name
    if ndc_code:
        params['ndc_code'] = ndc_code

    return medicaid_info(method='get_federal_upper_limits', **params)


# =============================================================================
# Dataset Discovery
# =============================================================================

def list_available_datasets() -> Dict[str, Any]:
    """
    List all available Medicaid datasets

    Returns:
        dict: Catalog of available datasets

    Examples:
        # Get dataset catalog
        datasets = list_available_datasets()

        for ds in datasets.get('datasets', []):
            name = ds.get('name')
            desc = ds.get('description')
            print(f"{name}: {desc}")
    """
    return medicaid_info(method='list_available_datasets')


def search_datasets(
    dataset_id: str,
    where_clause: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Custom search across any Medicaid dataset

    Args:
        dataset_id: Dataset identifier from list_available_datasets()
                   Example: "99315a95-37ac-4eee-946a-3c523b4c481e"

        where_clause: SoQL WHERE clause for filtering
                     Example: "state='CA' AND year=2024"

        limit: Maximum results (default: 100)

        offset: Pagination offset (default: 0)

    Returns:
        dict: Dataset query results

    Examples:
        # Custom query with SoQL
        results = search_datasets(
            dataset_id="99315a95-37ac-4eee-946a-3c523b4c481e",
            where_clause="state='CA' AND year=2024",
            limit=500
        )
    """
    params = {
        'dataset_id': dataset_id,
        'limit': limit,
        'offset': offset
    }

    if where_clause:
        params['where_clause'] = where_clause

    return medicaid_info(method='search_datasets', **params)


# =============================================================================
# Provider-Level Spending (local DuckDB on Parquet)
# =============================================================================

def get_provider_spending(
    npi: Optional[str] = None,
    hcpcs_code: Optional[str] = None,
    month_from: Optional[str] = None,
    month_to: Optional[str] = None,
    npi_role: str = "billing",
    limit: int = 100,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    Query Medicaid provider-level spending data (2018-2024).

    Requires local Parquet file. Run scripts/download_medicaid_provider_spending.py first.

    Args:
        npi: National Provider Identifier (10-digit)
        hcpcs_code: HCPCS procedure code (e.g., "99213", "J3490")
        month_from: Start month filter (YYYY-MM format)
        month_to: End month filter (YYYY-MM format)
        npi_role: "billing" or "servicing" NPI to filter on
        limit: Max results (default: 100)
        offset: Pagination offset

    Returns:
        dict with 'data' list of spending records containing:
        BILLING_PROVIDER_NPI_NUM, SERVICING_PROVIDER_NPI_NUM,
        HCPCS_CODE, CLAIM_FROM_MONTH, TOTAL_UNIQUE_BENEFICIARIES,
        TOTAL_CLAIMS, TOTAL_PAID

    Examples:
        # Top spending for a HCPCS code
        results = get_provider_spending(hcpcs_code='J3490', limit=10)

        # Provider's claims in 2023
        results = get_provider_spending(
            npi='1234567890',
            month_from='2023-01',
            month_to='2023-12'
        )
    """
    return medicaid_info(
        method='get_provider_spending',
        npi=npi, hcpcs_code=hcpcs_code,
        month_from=month_from, month_to=month_to,
        npi_role=npi_role, limit=limit, offset=offset,
    )


def get_provider_top_services(
    npi: str,
    npi_role: str = "billing",
    limit: int = 20,
) -> Dict[str, Any]:
    """
    Top HCPCS codes by total Medicaid payment for a provider.

    Args:
        npi: National Provider Identifier (10-digit)
        npi_role: "billing" or "servicing"
        limit: Number of top services (default: 20)

    Returns:
        dict with 'data' list ranked by total_paid

    Examples:
        results = get_provider_top_services(npi='1234567890', limit=10)
    """
    return medicaid_info(
        method='get_provider_top_services',
        npi=npi, npi_role=npi_role, limit=limit,
    )


def get_hcpcs_top_providers(
    hcpcs_code: str,
    npi_role: str = "billing",
    limit: int = 20,
) -> Dict[str, Any]:
    """
    Top Medicaid providers by total payment for a HCPCS code.

    Args:
        hcpcs_code: HCPCS procedure code (e.g., "99213")
        npi_role: "billing" or "servicing"
        limit: Number of top providers (default: 20)

    Returns:
        dict with 'data' list ranked by total_paid

    Examples:
        results = get_hcpcs_top_providers(hcpcs_code='99213', limit=10)
    """
    return medicaid_info(
        method='get_hcpcs_top_providers',
        hcpcs_code=hcpcs_code, npi_role=npi_role, limit=limit,
    )


def get_provider_spending_summary(
    npi: str,
    npi_role: str = "billing",
) -> Dict[str, Any]:
    """
    Aggregate Medicaid spending summary for a provider.

    Args:
        npi: National Provider Identifier (10-digit)
        npi_role: "billing" or "servicing"

    Returns:
        dict with 'data' containing aggregate stats (total_paid,
        unique_hcpcs_codes, total_beneficiaries, date range, etc.)

    Examples:
        summary = get_provider_spending_summary(npi='1234567890')
        print(f"Total paid: ${summary['data']['total_paid']:,.0f}")
    """
    return medicaid_info(
        method='get_provider_spending_summary',
        npi=npi, npi_role=npi_role,
    )


def get_provider_info(
    npi: Optional[str] = None,
    npis: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Look up provider identity from NPPES (name, specialty, state, ZIP).

    Requires local NPPES slim Parquet. Run scripts/download_nppes_slim.py first.

    Args:
        npi: Single NPI to look up
        npis: List of NPIs to look up (max 100)

    Returns:
        dict with 'data' list of provider records containing:
        npi, entity_type, provider_name, specialty, state, zip5, taxonomy_code

    Examples:
        result = get_provider_info(npi='1730491945')
        print(result['data'][0]['provider_name'])

        result = get_provider_info(npis=['1730491945', '1234567890'])
    """
    kwargs = {}
    if npi:
        kwargs['npi'] = npi
    if npis:
        kwargs['npis'] = npis
    return medicaid_info(method='get_provider_info', **kwargs)


def get_hcpcs_spending_by_month(
    hcpcs_code: str,
    month_from: Optional[str] = None,
    month_to: Optional[str] = None,
    exclude_zero_paid: bool = True,
) -> Dict[str, Any]:
    """
    Monthly spending trend for a HCPCS code across all providers.

    Returns one row per month with aggregate totals — max 84 rows (2018-2024).
    Useful for spotting utilization growth, seasonal patterns, or market shifts.

    Args:
        hcpcs_code: HCPCS procedure code (e.g., "J9271", "99213")
        month_from: Start month filter (YYYY-MM)
        month_to: End month filter (YYYY-MM)
        exclude_zero_paid: Exclude zero/negative paid rows (default True)

    Returns:
        dict with 'data' list of monthly aggregates containing:
        month, total_claims, total_beneficiaries, total_paid,
        billing_provider_count, servicing_provider_count

    Examples:
        # Pembrolizumab monthly trend
        result = get_hcpcs_spending_by_month(hcpcs_code='J9271')

        # 2024 only
        result = get_hcpcs_spending_by_month(
            hcpcs_code='J9271',
            month_from='2024-01',
            month_to='2024-12'
        )
    """
    return medicaid_info(
        method='get_hcpcs_spending_by_month',
        hcpcs_code=hcpcs_code,
        month_from=month_from,
        month_to=month_to,
        exclude_zero_paid=exclude_zero_paid,
    )


def get_hcpcs_spending_by_state(
    hcpcs_code: str,
    month_from: Optional[str] = None,
    month_to: Optional[str] = None,
    npi_role: str = "billing",
    exclude_zero_paid: bool = True,
    limit: int = 55,
) -> Dict[str, Any]:
    """
    Spending for a HCPCS code broken down by provider state.

    Joins spending with NPPES to group by provider state. Returns ~50 rows.
    Requires both local Parquet files (spending + NPPES slim).

    Args:
        hcpcs_code: HCPCS procedure code (e.g., "J9271", "99213")
        month_from: Start month filter (YYYY-MM)
        month_to: End month filter (YYYY-MM)
        npi_role: "billing" or "servicing"
        exclude_zero_paid: Exclude zero/negative paid rows (default True)
        limit: Max states (default: 55)

    Returns:
        dict with 'data' list of per-state aggregates containing:
        state, total_claims, total_beneficiaries, total_paid, provider_count

    Examples:
        result = get_hcpcs_spending_by_state(hcpcs_code='J9271')
        for row in result['data']:
            print(f"{row['state']}: ${row['total_paid']:,.0f}")
    """
    return medicaid_info(
        method='get_hcpcs_spending_by_state',
        hcpcs_code=hcpcs_code,
        month_from=month_from,
        month_to=month_to,
        npi_role=npi_role,
        exclude_zero_paid=exclude_zero_paid,
        limit=limit,
    )


def lookup_hcpcs(
    code: Optional[str] = None,
    codes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Look up HCPCS code description(s).

    Requires local lookup file. Run scripts/download_hcpcs_lookup.py first.

    Args:
        code: Single HCPCS code (e.g., "J0585", "99213")
        codes: List of HCPCS codes

    Returns:
        dict with 'data' mapping code → {short, long} descriptions

    Examples:
        result = lookup_hcpcs(code='J0585')
        # {'J0585': {'short': 'Injection,onabotulinumtoxina', 'long': '...'}}

        result = lookup_hcpcs(codes=['J0585', '99213', 'T1019'])
    """
    kwargs = {}
    if code:
        kwargs['code'] = code
    if codes:
        kwargs['codes'] = codes
    return medicaid_info(method='lookup_hcpcs', **kwargs)


def search_hcpcs(
    query: str,
    limit: int = 20,
) -> Dict[str, Any]:
    """
    Search HCPCS codes by description text (drug name, procedure, etc.).

    This is the key bridge from drug names to HCPCS codes for provider
    spending queries. Searches both short and long descriptions.

    Args:
        query: Search text (e.g., "semaglutide", "botulinum", "office visit")
        limit: Max results (default: 20)

    Returns:
        dict with 'data' list of {code, short, long} matches

    Examples:
        # Find HCPCS codes for a drug
        result = search_hcpcs(query='pembrolizumab')
        for match in result['data']:
            print(f"{match['code']}: {match['long']}")

        # Then query provider spending for that code
        providers = get_hcpcs_top_providers(
            hcpcs_code=result['data'][0]['code'],
            limit=10
        )
    """
    return medicaid_info(method='search_hcpcs', query=query, limit=limit)


__all__ = [
    'medicaid_info',
    # State-level (Node.js MCP)
    'get_nadac_pricing',
    'compare_drug_pricing',
    'get_enrollment_trends',
    'compare_state_enrollment',
    'get_drug_rebate_info',
    'search_state_formulary',
    'get_drug_utilization',
    'get_federal_upper_limits',
    'list_available_datasets',
    'search_datasets',
    # Provider-level (local DuckDB)
    'get_provider_spending',
    'get_provider_top_services',
    'get_hcpcs_top_providers',
    'get_provider_spending_summary',
    'get_hcpcs_spending_by_month',
    'get_hcpcs_spending_by_state',
    'get_provider_info',
    # HCPCS lookup (local JSON)
    'lookup_hcpcs',
    'search_hcpcs',
]
