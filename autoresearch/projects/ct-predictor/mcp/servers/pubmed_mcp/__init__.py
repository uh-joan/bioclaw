"""PubMed MCP Server - Python API

Provides Python functions for PubMed biomedical literature queries.
Data stays in execution environment - only summaries flow to model.

CRITICAL PUBMED API QUIRKS:
1. MeSH terms for precision: Use "Diabetes Mellitus, Type 2"[MeSH] syntax
2. Date filters: Use "YYYY/MM/DD" format (e.g., "2020/01/01") - validated in testing
3. Study type filters: Add "AND (randomized controlled trial[pt])"
4. Human studies: Add "AND humans[MeSH]"
5. Result count limitation: May return fewer results than requested (validated: requested 5, got 3)
6. Conservative requests: Request 10-20 results, expect partial returns
7. TOKEN USAGE (measured): ~750 tokens per article with full abstract
8. JSON format: Returns structured JSON (unlike CT.gov markdown)
"""

from mcp.client import get_client
from typing import Dict, Any, Optional, Union


def search_keywords(
    keywords: str,
    num_results: int = 10
) -> Dict[str, Any]:
    """
    Search PubMed by keywords

    Args:
        keywords: Search query with keywords, medical terms, drug names, diseases

                 ADVANCED SEARCH SYNTAX:
                 - Basic: "semaglutide diabetes" (implicit AND)
                 - MeSH terms: "Diabetes Mellitus, Type 2"[MeSH]
                 - Multiple terms: "GLP-1 agonist" AND obesity
                 - Study types: AND (randomized controlled trial[pt])
                 - Human studies: AND humans[MeSH]
                 - Date range: AND ("2020/01/01"[PDAT] : "2024/12/31"[PDAT])
                 - Exclude: NOT review[pt]

                 Examples:
                 - Simple: "semaglutide obesity"
                 - MeSH: "Diabetes Mellitus, Type 2"[MeSH] AND treatment
                 - RCT only: "GLP-1 agonist" AND (randomized controlled trial[pt])
                 - Recent: "obesity treatment" AND ("2023/01/01"[PDAT] : "2024/12/31"[PDAT])

        num_results: Maximum results to return (1-100, default: 10)

                    ⚠️  CRITICAL LIMITATION:
                    MCP may return fewer results than requested
                    - Requested 30 → may receive only 2 articles
                    - Appears to be MCP tool limitation, not query issue
                    - WORKAROUND: Request conservative numbers (10-20)
                    - Expect partial returns

    Returns:
        dict: PubMed API response with articles

        Key fields:
        - pmid: PubMed ID
        - title: Article title
        - abstract: Full abstract text
        - authors: Author list
        - journal: Journal name
        - pub_date: Publication date

    Examples:
        # Example 1: Basic keyword search
        results = search_keywords(
            keywords="semaglutide obesity",
            num_results=10  # Conservative request
        )

        # Process articles
        pmids = []
        titles = []
        for article in results.get('articles', []):
            pmids.append(article.get('pmid'))
            titles.append(article.get('title', 'No title'))

        print(f"Found {len(pmids)} articles (may be less than requested)")

        # Example 2: MeSH term search (more precise)
        results = search_keywords(
            keywords='"Diabetes Mellitus, Type 2"[MeSH] AND "GLP-1 agonist"',
            num_results=20
        )

        # Example 3: RCT filter
        results = search_keywords(
            keywords="obesity treatment AND (randomized controlled trial[pt])",
            num_results=15
        )

        # Example 4: Date-filtered search
        results = search_keywords(
            keywords='semaglutide AND ("2023/01/01"[PDAT] : "2024/12/31"[PDAT])',
            num_results=10
        )

        # Example 5: Human studies only
        results = search_keywords(
            keywords="GLP-1 agonist AND humans[MeSH]",
            num_results=10
        )
    """
    client = get_client('pubmed')

    params = {
        'method': 'search_keywords',
        'keywords': keywords,
        'num_results': num_results
    }

    return client.call_tool('pubmed_articles', params)


def search_advanced(
    term: Optional[str] = None,
    author: Optional[str] = None,
    journal: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    num_results: int = 10
) -> Dict[str, Any]:
    """
    Search PubMed with advanced filters

    Args:
        term: General search term (e.g., "GLP-1 agonist", "obesity treatment")

        author: Author name (e.g., "Smith J", "John Smith")

        journal: Journal name or abbreviation (e.g., "Nature", "N Engl J Med", "Science")

        start_date: Start date for publication date range
                   Format: "YYYY/MM/DD" (e.g., "2020/01/01")

        end_date: End date for publication date range
                 Format: "YYYY/MM/DD" (e.g., "2024/12/31")

        num_results: Maximum results to return (1-100, default: 10)
                    ⚠️  See search_keywords for MCP limitation details

    Returns:
        dict: PubMed API response with filtered articles

    Examples:
        # Example 1: High-impact journal filter
        results = search_advanced(
            term="semaglutide",
            journal="N Engl J Med",
            num_results=10
        )

        # Example 2: Date range filter
        results = search_advanced(
            term="GLP-1 agonist obesity",
            start_date="2020/01/01",
            end_date="2024/12/31",
            num_results=20
        )

        # Example 3: Author search
        results = search_advanced(
            author="Smith J",
            term="diabetes",
            num_results=15
        )

        # Example 4: Combined filters
        results = search_advanced(
            term="obesity treatment",
            journal="Diabetes Care",
            start_date="2023/01/01",
            end_date="2024/12/31",
            num_results=10
        )
    """
    client = get_client('pubmed')

    params = {
        'method': 'search_advanced',
        'num_results': num_results
    }

    if term:
        params['term'] = term
    if author:
        params['author'] = author
    if journal:
        params['journal'] = journal
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date

    return client.call_tool('pubmed_articles', params)


def get_article_metadata(
    pmid: Union[str, int]
) -> Dict[str, Any]:
    """
    Get detailed metadata for a specific PubMed article

    Args:
        pmid: PubMed ID (PMID) - unique identifier for PubMed articles
              Can be string or integer (e.g., "12345678" or 12345678)

    Returns:
        dict: Detailed article metadata

        Key fields:
        - pmid: PubMed ID
        - title: Article title
        - abstract: Full abstract text
        - authors: Complete author list with affiliations
        - journal: Journal name, volume, issue
        - pub_date: Publication date
        - doi: Digital Object Identifier
        - keywords: MeSH terms and keywords
        - citation: Full citation string

    Examples:
        # Get metadata for specific article
        article = get_article_metadata(pmid="12345678")

        # Extract key information
        title = article.get('title')
        abstract = article.get('abstract')
        authors = article.get('authors', [])
        journal = article.get('journal')
        doi = article.get('doi')

        print(f"Title: {title}")
        print(f"Authors: {', '.join([a.get('name') for a in authors])}")
        print(f"Journal: {journal}")
        print(f"DOI: {doi}")

        # Get MeSH terms
        mesh_terms = article.get('keywords', {}).get('mesh', [])
        print(f"MeSH terms: {', '.join(mesh_terms)}")
    """
    client = get_client('pubmed')

    params = {
        'method': 'get_article_metadata',
        'pmid': str(pmid)
    }

    return client.call_tool('pubmed_articles', params)


def get_article_pdf(
    pmid: Union[str, int]
) -> Dict[str, Any]:
    """
    Download full-text PDF for a PubMed article (when available)

    Args:
        pmid: PubMed ID (PMID) - unique identifier
              Can be string or integer (e.g., "12345678" or 12345678)

    Returns:
        dict: PDF download information

        Response may contain:
        - pdf_url: Direct URL to PDF (if available)
        - pdf_data: Base64-encoded PDF content (if downloaded)
        - available: Boolean indicating PDF availability
        - message: Status message or error

    Note:
        Not all PubMed articles have freely available PDFs.
        Availability depends on:
        - Publisher open access policies
        - PubMed Central (PMC) availability
        - Journal subscription status

    Examples:
        # Attempt to download PDF
        pdf_result = get_article_pdf(pmid="12345678")

        if pdf_result.get('available'):
            pdf_url = pdf_result.get('pdf_url')
            print(f"PDF available at: {pdf_url}")

            # If PDF data is provided
            if 'pdf_data' in pdf_result:
                import base64
                pdf_bytes = base64.b64decode(pdf_result['pdf_data'])
                with open('article.pdf', 'wb') as f:
                    f.write(pdf_bytes)
        else:
            print("PDF not available:", pdf_result.get('message'))
    """
    client = get_client('pubmed')

    params = {
        'method': 'get_article_pdf',
        'pmid': str(pmid)
    }

    return client.call_tool('pubmed_articles', params)


__all__ = ['search_keywords', 'search_advanced', 'get_article_metadata', 'get_article_pdf']
