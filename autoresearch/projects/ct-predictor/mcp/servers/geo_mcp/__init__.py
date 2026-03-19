"""GEO MCP Server - Python API

Provides access to NCBI Gene Expression Omnibus (GEO).
Genomics datasets, gene expression profiles, and research maturity signals.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(method: str, **kwargs) -> Dict[str, Any]:
    """Internal: call a GEO MCP tool method."""
    client = get_client('geo')
    params = {k: v for k, v in kwargs.items() if v is not None}
    params['method'] = method
    return client.call_tool('geo_data', params)


def search_by_gene(gene: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Search GEO datasets by gene symbol.

    Args:
        gene: Gene symbol (e.g., "TP53", "EGFR")
        limit: Maximum results (optional)

    Returns:
        dict: GEO datasets studying this gene
    """
    return _call('search_by_gene', gene=gene, limit=limit)


def search_datasets(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Search GEO datasets by keyword.

    Args:
        query: Search term (e.g., "breast cancer RNA-seq")
        limit: Maximum results (optional)

    Returns:
        dict: Matching GEO datasets
    """
    return _call('search_datasets', query=query, limit=limit)


__all__ = [
    'search_by_gene',
    'search_datasets',
]
