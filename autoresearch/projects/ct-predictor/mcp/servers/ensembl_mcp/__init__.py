"""Ensembl MCP Server - Python API

Provides access to Ensembl genome browser data.
Gene annotations, transcripts, and biotype information.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(method: str, **kwargs) -> Dict[str, Any]:
    """Internal: call an Ensembl MCP tool method."""
    client = get_client('ensembl')
    params = {k: v for k, v in kwargs.items() if v is not None}
    params['method'] = method
    return client.call_tool('ensembl_data', params)


def lookup_gene(gene_id: str) -> Dict[str, Any]:
    """
    Look up gene information in Ensembl.

    Args:
        gene_id: Ensembl gene ID (e.g., "ENSG00000146648")

    Returns:
        dict: Gene annotation including biotype, location, description
    """
    return _call('lookup_gene', gene_id=gene_id)


def get_transcripts(gene_id: str) -> Dict[str, Any]:
    """
    Get transcript variants for a gene.

    Args:
        gene_id: Ensembl gene ID (e.g., "ENSG00000146648")

    Returns:
        dict: Transcript data including count and types
    """
    return _call('get_transcripts', gene_id=gene_id)


__all__ = [
    'lookup_gene',
    'get_transcripts',
]
