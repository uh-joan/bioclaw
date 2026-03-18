"""FDA MCP Server - Python API

Provides Python functions for FDA drug database queries.
Data stays in execution environment - only summaries flow to model.

🔴 CRITICAL: USE ALTERNATIVES FOR BROKEN METHODS
See scripts/mcp/servers/fda_mcp/alternatives.py for working alternatives:
- get_drug_label_alternative() - Replaces broken label queries (95.5% token savings)
- get_adverse_events_summary() - Optimized adverse event counts (99.3% savings)
- get_label_sections_summary() - Minimal label data (<1k tokens)
- search_drugs_by_indication() - Find drugs by condition

Full documentation: scripts/mcp/servers/ALTERNATIVES_README.md

CRITICAL FDA API QUIRKS:
1. Count-first pattern MANDATORY for general/adverse_events (prevents 67k token overflow)
2. 🔴 LABEL QUERIES BROKEN: Single label = 110k tokens (4.4x MCP limit) → queries FAIL
   → USE ALTERNATIVE: get_drug_label_alternative() with field selection
3. ❌ Field selection parameter currently not working correctly
   → USE ALTERNATIVE: Direct API calls with proper field filtering
4. OR operators DON'T WORK - use parallel queries instead
5. Some class terms return 404 ("ACE inhibitor", "beta blocker", "statin")
6. Mechanism terms often work ("GLP-1", "NSAID")
7. Field-specific syntax: "openfda.brand_name:DRUGNAME"
8. Response structure: results['data']['results'] (nested)
"""

from mcp.client import get_client
from typing import Dict, Any, Optional, List


def lookup_drug(
    search_term: str,
    search_type: str = "general",
    limit: int = 25,
    count: Optional[str] = None,
    fields_for_general: Optional[str] = None,
    fields_for_label: Optional[str] = None,
    fields_for_adverse_events: Optional[str] = None,
    fields_for_recalls: Optional[str] = None,
    fields_for_shortages: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Search FDA drug database

    Args:
        search_term: Drug name, active ingredient, condition, or manufacturer

                    SEARCH TERM QUIRKS:
                    - ❌ OR operators DON'T WORK: "drug1 OR drug2" returns 404
                    - ❌ Some class terms return 404: "ACE inhibitor", "beta blocker", "statin"
                    - ✅ Mechanism terms often work: "GLP-1", "NSAID"
                    - ✅ Specific drug names always work: "lisinopril", "semaglutide"
                    - ✅ Field-specific syntax: "openfda.brand_name:DRUGNAME"
                    - ✅ Adverse events syntax: "patient.drug.medicinalproduct:drugname"

                    For multiple drugs: Run parallel queries, don't use OR

        search_type: Type of search - 'general', 'label', 'adverse_events', 'recalls', 'shortages'

                    🔴 CRITICAL TOKEN LIMITS BY SEARCH_TYPE:
                    - 'general' WITHOUT count: ~67,000 tokens → EXCEEDS MCP LIMIT → FAILS
                    - 'general' WITH count: ~150 tokens → WORKS (99.8% reduction)
                    - 'adverse_events' WITHOUT count: ~50,000+ tokens → EXCEEDS MCP LIMIT → FAILS
                    - 'adverse_events' WITH count: ~200 tokens → WORKS
                    - 'label' WITHOUT field selection: 110,000 tokens → EXCEEDS MCP LIMIT → FAILS
                    - 'label' WITH field selection: PARAMETER CURRENTLY BROKEN ❌
                    - 'recalls': ~1,400 tokens per result → count optional (dataset small)
                    - 'shortages': ~800 tokens per result → count optional (dataset small)

                    **REQUIRED PARAMETERS BY TYPE**:
                    - general → count MANDATORY
                    - adverse_events → count MANDATORY
                    - label → field selection REQUIRED (but currently broken - DO NOT USE)
                    - recalls → count optional
                    - shortages → count optional

        limit: Maximum results to return (1-100, default: 25)

        count: CRITICAL - Aggregation field for count-first pattern (MANDATORY for general/adverse_events)
               MUST end with ".exact" suffix for proper aggregation

               Recommended values:
               - General searches: "openfda.brand_name.exact"
               - Adverse events: "patient.reaction.reactionmeddrapt.exact"
               - Skip count for: recalls, shortages (small datasets)

               Without count parameter: queries return 67k tokens and FAIL (exceeds 25k MCP limit)
               Without .exact suffix: may return inconsistent aggregations

        fields_for_general: Comma-separated fields for general search
                           Example: "openfda.brand_name,openfda.generic_name,products.marketing_status"
        fields_for_label: Comma-separated fields for label search
        fields_for_adverse_events: Comma-separated fields for adverse events search
        fields_for_recalls: Comma-separated fields for recalls search
        fields_for_shortages: Comma-separated fields for shortages search

    Returns:
        dict: FDA API response with drug records or aggregated counts

        Response structures:
        - Count query: {'data': {'results': [{'term': 'BRANDNAME', 'count': 5}, ...]}}
        - Regular query: {'data': {'results': [{'openfda': {...}, 'products': [...], ...}]}}

        NOTE: Results are always nested under results['data']['results']

    Examples:
        # Example 1: TWO-STEP STRATEGY (recommended for efficiency)

        # Step 1: Count-first to get aggregated list (~400 tokens)
        count_results = lookup_drug(
            search_term="GLP-1",
            search_type="general",
            count="openfda.brand_name.exact",
            limit=50
        )

        # Process count results (nested under 'data')
        brands = []
        data = count_results.get('data', {})
        for item in data.get('results', []):
            brands.append(item['term'])

        # Step 2: Get details for specific drug with field selection (~500 tokens)
        detail_results = lookup_drug(
            search_term="semaglutide",
            search_type="general",
            fields_for_general="openfda.brand_name,openfda.route,submissions",
            limit=5
        )

        # Example 2: MULTIPLE DRUGS (use parallel queries, NOT OR)

        # ❌ WRONG: OR operator fails
        # results = lookup_drug(search_term="semaglutide OR liraglutide")

        # ✅ CORRECT: Run parallel queries
        sema = lookup_drug(
            search_term="semaglutide",
            count="openfda.brand_name.exact"
        )
        lira = lookup_drug(
            search_term="liraglutide",
            count="openfda.brand_name.exact"
        )

        # Example 3: ADVERSE EVENTS with count-first (~200 tokens)
        # Returns aggregated MedDRA reaction terms with occurrence counts
        adverse = lookup_drug(
            search_term="semaglutide",
            search_type="adverse_events",
            count="patient.reaction.reactionmeddrapt.exact",
            limit=10
        )

        # Actual response structure (validated in testing):
        # {
        #   'data': {
        #     'results': [
        #       {'term': 'NAUSEA', 'count': 11180},
        #       {'term': 'VOMITING', 'count': 7205},
        #       {'term': 'DIARRHOEA', 'count': 6226},
        #       ...
        #     ]
        #   }
        # }

        # Process adverse event counts for safety profiling
        for item in adverse.get('data', {}).get('results', []):
            reaction = item.get('term')
            count = item.get('count')
            print(f"{reaction}: {count:,} reports")

        # Output (actual test data):
        # NAUSEA: 11,180 reports
        # VOMITING: 7,205 reports
        # OFF LABEL USE: 6,393 reports
        # DIARRHOEA: 6,226 reports
        # ...

        # Example 4: FIELD-SPECIFIC SEARCH
        brand_search = lookup_drug(
            search_term="openfda.brand_name:OZEMPIC",
            search_type="general",
            count="openfda.generic_name.exact"
        )

        # Example 5: SKIP COUNT for small datasets (recalls/shortages)
        recalls = lookup_drug(
            search_term="semaglutide",
            search_type="recalls",
            limit=50  # No count needed - small dataset
        )
    """
    # VALIDATION: Count-first pattern mandatory for general/adverse_events
    if search_type in ('general', 'adverse_events') and not count:
        import warnings
        warnings.warn(
            f"Count parameter MANDATORY for search_type='{search_type}' to avoid token overflow. "
            f"Without count: query returns 50k-67k tokens → EXCEEDS MCP limit → WILL FAIL. "
            f"Add count='openfda.brand_name.exact' for general searches.",
            UserWarning
        )

    # NOTE: FDA API enforces max 100 results per query
    # We don't cap it here - let the API return its natural error message
    # For comprehensive data, use OpenTargets → FDA two-step pattern

    client = get_client('fda-mcp-server')

    params = {
        'method': 'lookup_drug',
        'search_term': search_term,
        'search_type': search_type,
        'limit': limit
    }

    # CRITICAL: Add count parameter if provided
    if count:
        params['count'] = count

    # Add optional field parameters
    if fields_for_general:
        params['fields_for_general'] = fields_for_general
    if fields_for_label:
        params['fields_for_label'] = fields_for_label
    if fields_for_adverse_events:
        params['fields_for_adverse_events'] = fields_for_adverse_events
    if fields_for_recalls:
        params['fields_for_recalls'] = fields_for_recalls
    if fields_for_shortages:
        params['fields_for_shortages'] = fields_for_shortages

    params.update(kwargs)

    return client.call_tool('fda_info', params)


def lookup_device(
    search: str,
    search_type: str = "device_registration",
    limit: int = 100,
    **kwargs
) -> Dict[str, Any]:
    """
    Search FDA device database

    Args:
        search: Device name, company name, or search query
        search_type: Type of search - 'device_registration', 'device_510k', 'device_pma',
                     'device_udi', 'device_recalls', 'device_adverse_events', 'device_classification'
        limit: Maximum results to return (default: 100)

    Returns:
        dict: FDA API response with device records
    """
    client = get_client('fda-mcp-server')

    params = {
        'method': 'lookup_device',
        'search_term': search,
        'search_type': search_type,
        'limit': limit
    }

    params.update(kwargs)

    return client.call_tool('fda_info', params)


def device_510k(search: str, limit: int = 100, **kwargs) -> Dict[str, Any]:
    """Search FDA 510(k) clearances (Class II devices)"""
    return lookup_device(search=search, search_type='device_510k', limit=limit, **kwargs)


def device_pma(search: str, limit: int = 100, **kwargs) -> Dict[str, Any]:
    """Search FDA PMA approvals (Class III devices)"""
    return lookup_device(search=search, search_type='device_pma', limit=limit, **kwargs)


def device_registration(search: str, limit: int = 100, **kwargs) -> Dict[str, Any]:
    """Search FDA device registrations"""
    return lookup_device(search=search, search_type='device_registration', limit=limit, **kwargs)


def device_udi(search: str, limit: int = 100, **kwargs) -> Dict[str, Any]:
    """Search FDA Unique Device Identifiers"""
    return lookup_device(search=search, search_type='device_udi', limit=limit, **kwargs)


def device_recalls(search: str, limit: int = 100, **kwargs) -> Dict[str, Any]:
    """Search FDA device recalls"""
    return lookup_device(search=search, search_type='device_recalls', limit=limit, **kwargs)


def device_adverse_events(search: str, limit: int = 100, **kwargs) -> Dict[str, Any]:
    """Search FDA MAUDE adverse events for devices"""
    return lookup_device(search=search, search_type='device_adverse_events', limit=limit, **kwargs)


def device_classification(search: str, limit: int = 100, **kwargs) -> Dict[str, Any]:
    """Search FDA device classifications"""
    return lookup_device(search=search, search_type='device_classification', limit=limit, **kwargs)


def search_purple_book(
    search_term: str,
    limit: int = 25,
    **kwargs
) -> Dict[str, Any]:
    """
    Search FDA Purple Book for biologics and gene therapies.

    The Purple Book contains FDA-licensed biological products, including:
    - Reference biological products
    - Biosimilar products
    - Interchangeable biological products
    - Gene therapies (regulated by CBER)

    IMPORTANT: Gene therapies (like Casgevy, Lyfgenia) are NOT in the standard
    drug labels database - they're only in the Purple Book.

    Args:
        search_term: Product name, active ingredient, or BLA number
        limit: Maximum results (default: 25)

    Returns:
        dict: Purple Book entries with licensureStatus, dateOfLicensure, etc.

        Response structure:
        {
            'data': {
                'totalCount': N,
                'results': [
                    {
                        'proprietaryName': 'CASGEVY',
                        'properName': 'exagamglogene autotemcel',
                        'blaNumber': '125787',
                        'licensureStatus': 'Licensed',
                        'dateOfLicensure': 'December 08, 2023',
                        'applicantHolderName': 'VERTEX PHARMACEUTICALS INC',
                        ...
                    }
                ]
            }
        }

    Examples:
        # Search for gene therapy by name
        result = search_purple_book("casgevy")
        result = search_purple_book("exagamglogene")

        # Check if a drug is a licensed biologic
        result = search_purple_book("humira")
        if result.get('data', {}).get('totalCount', 0) > 0:
            print("Found in Purple Book (licensed biologic)")
    """
    client = get_client('fda-mcp-server')

    params = {
        'method': 'search_purple_book',
        'search_term': search_term,
        'limit': limit
    }

    params.update(kwargs)

    return client.call_tool('fda_info', params)


def get_patent_exclusivity(
    nda_number: str,
    search_term: str = "",
    limit: int = 100,
    **kwargs
) -> Dict[str, Any]:
    """
    Get patent and exclusivity data from FDA Orange Book for small molecule drugs.

    IMPORTANT: Orange Book only contains NDA applications (small molecules).
    For biologics (BLA applications), patents are NOT available - use search_purple_book instead.

    Args:
        nda_number: NDA application number (numeric only, e.g., "204629" not "NDA204629")
        search_term: Drug/trade name for logging (optional, helps identify results)
        limit: Maximum results (default: 100)

    Returns:
        dict: Patent and exclusivity data
        {
            'success': True/False,
            'data': {
                'application': {'applNo': '...', 'tradeName': '...', 'ingredient': '...'},
                'patents': [
                    {
                        'patentNo': '7713938',
                        'patentExpireDate': 'Apr 15, 2027',
                        'drugSubstanceFlag': 'Y',  # Patent covers drug substance
                        'drugProductFlag': 'Y',    # Patent covers drug product
                        'patentUseCode': 'U-1234'  # Method of use code
                    },
                    ...
                ],
                'exclusivity': [
                    {
                        'exclusivityCode': 'NCE',  # New Chemical Entity
                        'exclusivityDate': 'Jun 20, 2026'
                    },
                    ...
                ]
            }
        }

    Examples:
        # First look up drug to get NDA number
        labels = lookup_drug("jardiance", search_type='label', limit=1)
        # Extract NDA from openfda.application_number (e.g., "NDA204629")
        nda = "204629"  # Strip "NDA" prefix

        # Then get patent data
        patents = get_patent_exclusivity(nda_number="204629", search_term="jardiance")

        # Parse earliest patent expiry
        if patents.get('success'):
            patent_dates = [p['patentExpireDate'] for p in patents['data']['patents']]
            # Parse dates and find the earliest one for LOE analysis
    """
    client = get_client('fda-mcp-server')

    # Strip common prefixes from NDA number
    clean_nda = nda_number.replace('NDA', '').replace('nda', '').strip()

    params = {
        'method': 'get_patent_exclusivity',
        'nda_number': clean_nda,
        'search_term': search_term or clean_nda,
        'limit': limit
    }

    params.update(kwargs)

    return client.call_tool('fda_info', params)


__all__ = [
    'lookup_drug',
    'lookup_device',
    'device_510k',
    'device_pma',
    'device_registration',
    'device_udi',
    'device_recalls',
    'device_adverse_events',
    'device_classification',
    'search_purple_book',
    'get_patent_exclusivity'
]
