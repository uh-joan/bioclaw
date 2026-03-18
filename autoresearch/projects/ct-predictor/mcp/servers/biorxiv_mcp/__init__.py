"""bioRxiv MCP Server - Python API

Provides access to bioRxiv and medRxiv preprint servers (Cold Spring Harbor Laboratory).
260,000+ preprints across 26 biological and 40+ medical science categories.
Data stays in execution environment - only summaries flow to model.

Local stdio MCP server hitting the public bioRxiv REST API.

CRITICAL BIORXIV MCP QUIRKS:
1. Preprints are NOT peer-reviewed - should not be cited as established fact
2. DOI format: "10.1101/2024.01.15.575123" (bioRxiv prefix 10.1101)
3. Both bioRxiv (biology) and medRxiv (medicine) are searched
4. Categories: 26 bioRxiv + 40+ medRxiv subject areas
5. Publication status: Some preprints get formally published in journals
6. Funder search uses ROR IDs (Research Organization Registry)
7. Common ROR IDs: NIH='021nxhr62', NSF='01cwqze88', EC='02mhbdp94',
   Wellcome='029chgv08', HHMI='05a28rw58', MRC='006wxqw41'
8. search_preprints uses client-side keyword filtering over date-range API
   (bioRxiv API has no keyword search endpoint)
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(method: str, **kwargs) -> Dict[str, Any]:
    """Internal: call a bioRxiv MCP tool method."""
    client = get_client('biorxiv-mcp-server')
    params = {k: v for k, v in kwargs.items() if v is not None}
    params['method'] = method
    return client.call_tool('biorxiv_info', params)


# =============================================================================
# Search Preprints
# =============================================================================

def search_preprints(
    query: str,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    server: Optional[str] = None,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Search preprints by keywords, topics, or authors across bioRxiv and medRxiv

    NOTE: Uses client-side keyword filtering over the date-range browsing API.
    Default date range is last 30 days if not specified.

    Args:
        query: Search keywords, topic, or author name
              Examples: "CRISPR gene editing", "COVID-19 vaccine",
                       "single cell RNA-seq", "Zhang F"

        category: Subject category filter (optional)
                 bioRxiv: "biochemistry", "bioinformatics", "cancer-biology",
                         "cell-biology", "genetics", "genomics",
                         "immunology", "microbiology", "neuroscience",
                         "pharmacology-and-toxicology", etc.
                 medRxiv: "cardiovascular-medicine", "oncology",
                         "infectious-diseases", etc.

        date_from: Start date "YYYY-MM-DD" (optional, default: 30 days ago)

        date_to: End date "YYYY-MM-DD" (optional, default: today)

        server: "biorxiv" or "medrxiv" (optional, default: "biorxiv")

        limit: Maximum results (optional, default: 30)

    Returns:
        dict: Preprint search results

        Key fields per preprint:
        - doi: DOI (e.g., "10.1101/2024.01.15.575123")
        - title: Preprint title
        - authors: Author list
        - abstract: Abstract text (truncated to 500 chars)
        - date: Posting date
        - category: Subject category
        - version: Version number
        - published: Publication status/journal DOI

    Examples:
        results = search_preprints("CRISPR gene editing")
        results = search_preprints(
            "single cell RNA-seq",
            category="neuroscience",
            date_from="2025-01-01"
        )
    """
    return _call(
        'search_preprints',
        query=query,
        category=category,
        date_from=date_from,
        date_to=date_to,
        server=server,
        limit=limit,
    )


# =============================================================================
# Preprint Details
# =============================================================================

def get_preprint_details(
    doi: str,
    server: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get complete metadata for a specific preprint by DOI

    Args:
        doi: Preprint DOI (e.g., "10.1101/2024.01.15.575123")

        server: "biorxiv" or "medrxiv" (optional, default: "biorxiv")

    Returns:
        dict: Complete preprint metadata with all versions

        Key fields per version:
        - doi: Preprint DOI
        - title: Full title
        - authors: Author list
        - abstract: Full abstract
        - date: Posting date
        - category: Subject category
        - version: Version number
        - published: Journal DOI if formally published

    Examples:
        details = get_preprint_details("10.1101/2024.01.15.575123")
    """
    return _call('get_preprint_details', doi=doi, server=server)


# =============================================================================
# Categories
# =============================================================================

def get_categories() -> Dict[str, Any]:
    """
    List all available subject categories for bioRxiv and medRxiv

    Returns:
        dict: Category listings with biorxiv and medrxiv keys

    Examples:
        categories = get_categories()
        bio_cats = categories.get('biorxiv', {}).get('categories', [])
        med_cats = categories.get('medrxiv', {}).get('categories', [])
    """
    return _call('get_categories')


# =============================================================================
# Published Preprints
# =============================================================================

def search_published_preprints(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    publisher: Optional[str] = None,
    server: Optional[str] = None,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Find preprints that have been formally published in peer-reviewed journals

    Args:
        date_from: Start date "YYYY-MM-DD" (optional)

        date_to: End date "YYYY-MM-DD" (optional)

        publisher: Publisher DOI prefix filter (optional)
                  Common prefixes:
                  - "10.1038" (Nature)
                  - "10.1126" (Science)
                  - "10.1016" (Elsevier)
                  - "10.1371" (PLOS)
                  - "10.7554" (eLife)
                  - "10.1073" (PNAS)

        server: "biorxiv" or "medrxiv" (optional)

        limit: Maximum results (optional)

    Returns:
        dict: Published preprint results

    Examples:
        results = search_published_preprints(
            publisher="10.1038",
            date_from="2025-01-01"
        )
    """
    return _call(
        'search_published_preprints',
        date_from=date_from,
        date_to=date_to,
        publisher=publisher,
        server=server,
        limit=limit,
    )


# =============================================================================
# Funder Search
# =============================================================================

def search_by_funder(
    funder_ror_id: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    server: Optional[str] = None,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Find preprints by funding organization using ROR IDs

    NOTE: Funder data only available from 2025-04-10 onwards.

    Args:
        funder_ror_id: Research Organization Registry ID (required)
                      Common funders:
                      - "021nxhr62" (NIH)
                      - "01cwqze88" (NSF)
                      - "02mhbdp94" (European Commission)
                      - "029chgv08" (Wellcome Trust)
                      - "05a28rw58" (HHMI)
                      - "006wxqw41" (MRC)

        date_from: Start date "YYYY-MM-DD" (optional, default: 2025-04-10)

        date_to: End date "YYYY-MM-DD" (optional)

        server: "biorxiv" or "medrxiv" (optional)

        limit: Maximum results (optional)

    Returns:
        dict: Funder search results

    Examples:
        results = search_by_funder("021nxhr62")  # NIH
        results = search_by_funder("029chgv08")  # Wellcome Trust
    """
    return _call(
        'search_by_funder',
        funder_ror_id=funder_ror_id,
        date_from=date_from,
        date_to=date_to,
        server=server,
        limit=limit,
    )


# =============================================================================
# Statistics
# =============================================================================

def get_content_statistics(
    interval: str = "m"
) -> Dict[str, Any]:
    """
    Get submission statistics (papers, revisions, authors)

    Args:
        interval: "m" (monthly) or "y" (yearly)

    Returns:
        dict: Content statistics

    Examples:
        stats = get_content_statistics("m")
        stats = get_content_statistics("y")
    """
    return _call('get_content_statistics', interval=interval)


def get_usage_statistics(
    interval: str = "m",
    server: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get engagement statistics (views, downloads)

    Args:
        interval: "m" (monthly) or "y" (yearly)

        server: "biorxiv" or "medrxiv" (optional, default: "biorxiv")

    Returns:
        dict: Usage statistics

    Examples:
        stats = get_usage_statistics("m")
        stats = get_usage_statistics("y", server="medrxiv")
    """
    return _call('get_usage_statistics', interval=interval, server=server)


__all__ = [
    'search_preprints',
    'get_preprint_details',
    'get_categories',
    'search_published_preprints',
    'search_by_funder',
    'get_content_statistics',
    'get_usage_statistics',
]
