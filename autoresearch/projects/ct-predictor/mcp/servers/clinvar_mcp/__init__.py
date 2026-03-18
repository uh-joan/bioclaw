"""ClinVar MCP Server - Python API

Access clinical variant data: pathogenic variants, gene-disease associations.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(method: str, **kwargs) -> Dict[str, Any]:
    """Internal: call a ClinVar MCP tool method."""
    client = get_client('clinvar')
    params = {k: v for k, v in kwargs.items() if v is not None}
    params['method'] = method
    return client.call_tool('clinvar_data', params)


def combined_search(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Search ClinVar by gene, variant, or condition.

    Args:
        query: Gene symbol, variant ID, or condition name
        limit: Max results
    Returns:
        dict with matching ClinVar records
    """
    return _call('combined_search', query=query, limit=limit)


def get_gene_variants_summary(gene: str) -> Dict[str, Any]:
    """Get summary of variants for a gene including pathogenicity counts.

    Args:
        gene: Gene symbol (e.g. BRCA1)
    Returns:
        dict with variant counts by clinical significance
    """
    return _call('get_gene_variants_summary', gene=gene)


def get_variant_details(variant_id: str) -> Dict[str, Any]:
    """Get detailed info for a specific ClinVar variant.

    Args:
        variant_id: ClinVar variation ID
    Returns:
        dict with variant details and clinical assertions
    """
    return _call('get_variant_details', variant_id=variant_id)


def get_variant_summary(variant_id: str) -> Dict[str, Any]:
    """Get brief summary for a ClinVar variant.

    Args:
        variant_id: ClinVar variation ID
    Returns:
        dict with variant summary
    """
    return _call('get_variant_summary', variant_id=variant_id)


__all__ = [
    'combined_search',
    'get_gene_variants_summary',
    'get_variant_details',
    'get_variant_summary',
]
