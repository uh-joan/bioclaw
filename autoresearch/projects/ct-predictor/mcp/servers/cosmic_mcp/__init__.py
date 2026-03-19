"""COSMIC MCP Server - Python API

Provides access to the COSMIC (Catalogue Of Somatic Mutations In Cancer) database.
Somatic mutation data across cancer genomes, driver gene annotations.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(method: str, **kwargs) -> Dict[str, Any]:
    """Internal: call a COSMIC MCP tool method."""
    client = get_client('cosmic')
    params = {k: v for k, v in kwargs.items() if v is not None}
    params['method'] = method
    return client.call_tool('cosmic_data', params)


def search_by_gene(gene: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Search COSMIC mutations by gene symbol.

    Args:
        gene: Gene symbol (e.g., "BRAF", "TP53")
        limit: Maximum results (optional)

    Returns:
        dict: Mutation search results for the gene
    """
    return _call('search_by_gene', gene=gene, limit=limit)


def get_gene_mutation_profile(gene: str) -> Dict[str, Any]:
    """
    Get the full mutation profile for a gene in COSMIC.

    Args:
        gene: Gene symbol (e.g., "EGFR", "KRAS")

    Returns:
        dict: Mutation profile including counts, types, and driver status
    """
    return _call('get_gene_mutation_profile', gene=gene)


__all__ = [
    'search_by_gene',
    'get_gene_mutation_profile',
]
