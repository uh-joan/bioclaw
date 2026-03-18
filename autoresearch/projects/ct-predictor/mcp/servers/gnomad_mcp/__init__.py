"""gnomAD MCP Server - Python API

Access population genetic constraint data: pLI, LOEUF, variant frequencies.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional, List


def _call(tool: str, **kwargs) -> Dict[str, Any]:
    """Internal: call a gnomAD MCP tool."""
    client = get_client('gnomad')
    params = {k: v for k, v in kwargs.items() if v is not None}
    return client.call_tool(tool, params)


def get_gene_constraint(gene: str) -> Dict[str, Any]:
    """Get genetic constraint metrics for a gene.

    Args:
        gene: Gene symbol (e.g. BRCA1, TP53)
    Returns:
        dict with pLI, LOEUF, missense Z-score, syn Z-score
    """
    return _call('get_gene_constraint', gene=gene)


def batch_gene_constraint(genes: str) -> Dict[str, Any]:
    """Get constraint metrics for multiple genes.

    Args:
        genes: Comma-separated gene symbols
    Returns:
        dict with constraint data per gene
    """
    return _call('batch_gene_constraint', genes=genes)


def get_gene_info(gene: str) -> Dict[str, Any]:
    """Get gene information from gnomAD.

    Args:
        gene: Gene symbol
    Returns:
        dict with gene metadata and coordinates
    """
    return _call('get_gene_info', gene=gene)


def get_gene_variants(gene: str, consequence: Optional[str] = None,
                       limit: Optional[int] = None) -> Dict[str, Any]:
    """Get variants in a gene from gnomAD.

    Args:
        gene: Gene symbol
        consequence: Filter by variant consequence (e.g. missense, lof)
        limit: Max variants
    Returns:
        dict with variant list and allele frequencies
    """
    return _call('get_gene_variants', gene=gene, consequence=consequence, limit=limit)


def filter_rare_variants(gene: str, max_af: Optional[float] = None,
                          consequence: Optional[str] = None) -> Dict[str, Any]:
    """Filter rare variants by allele frequency.

    Args:
        gene: Gene symbol
        max_af: Maximum allele frequency threshold
        consequence: Variant consequence filter
    Returns:
        dict with rare variants
    """
    return _call('filter_rare_variants', gene=gene, max_af=max_af, consequence=consequence)


__all__ = [
    'get_gene_constraint',
    'batch_gene_constraint',
    'get_gene_info',
    'get_gene_variants',
    'filter_rare_variants',
]
