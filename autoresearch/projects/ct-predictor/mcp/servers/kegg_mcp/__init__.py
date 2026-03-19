"""KEGG MCP Server - Python API

Provides access to the KEGG (Kyoto Encyclopedia of Genes and Genomes) database.
Pathway maps, gene-pathway associations, and organism-specific data.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(method: str, **kwargs) -> Dict[str, Any]:
    """Internal: call a KEGG MCP tool method."""
    client = get_client('kegg')
    params = {k: v for k, v in kwargs.items() if v is not None}
    params['method'] = method
    return client.call_tool('kegg_data', params)


def search_pathways(query: str, organism: Optional[str] = None) -> Dict[str, Any]:
    """
    Search KEGG pathways by keyword or gene.

    Args:
        query: Pathway keyword or gene symbol (e.g., "apoptosis", "EGFR")
        organism: Organism code (e.g., "hsa" for human) (optional)

    Returns:
        dict: Matching KEGG pathways
    """
    return _call('search_pathways', query=query, organism=organism)


def search_genes(query: str, organism: Optional[str] = None) -> Dict[str, Any]:
    """
    Search KEGG genes by keyword.

    Args:
        query: Gene name or keyword (e.g., "BRAF", "tyrosine kinase")
        organism: Organism code (optional)

    Returns:
        dict: Matching KEGG gene entries
    """
    return _call('search_genes', query=query, organism=organism)


__all__ = [
    'search_pathways',
    'search_genes',
]
