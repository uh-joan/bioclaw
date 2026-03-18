"""DepMap MCP Server - Python API

Access cancer dependency data: gene essentiality, biomarkers, copy number.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(method: str, **kwargs) -> Dict[str, Any]:
    """Internal: call a DepMap MCP tool method."""
    client = get_client('depmap')
    params = {k: v for k, v in kwargs.items() if v is not None}
    params['method'] = method
    return client.call_tool('depmap_data', params)


def get_gene_dependency(gene: str, context: Optional[str] = None) -> Dict[str, Any]:
    """Get gene essentiality/dependency scores across cell lines.

    Args:
        gene: Gene symbol (e.g. KRAS, TP53)
        context: Cancer context filter (e.g. "lung", "breast")
    Returns:
        dict with dependency scores (CERES/Chronos)
    """
    return _call('get_gene_dependency', gene=gene, context=context)


def get_biomarker_analysis(gene: str) -> Dict[str, Any]:
    """Get biomarker correlates for a gene dependency.

    Args:
        gene: Gene symbol
    Returns:
        dict with correlated biomarkers
    """
    return _call('get_biomarker_analysis', gene=gene)


def get_context_info(context: str) -> Dict[str, Any]:
    """Get info about a cancer context/lineage.

    Args:
        context: Cancer type or lineage name
    Returns:
        dict with context metadata and cell line count
    """
    return _call('get_context_info', context=context)


def get_copy_number(gene: str, context: Optional[str] = None) -> Dict[str, Any]:
    """Get copy number data for a gene across cell lines.

    Args:
        gene: Gene symbol
        context: Cancer context filter
    Returns:
        dict with copy number values
    """
    return _call('get_copy_number', gene=gene, context=context)


__all__ = [
    'get_gene_dependency',
    'get_biomarker_analysis',
    'get_context_info',
    'get_copy_number',
]
