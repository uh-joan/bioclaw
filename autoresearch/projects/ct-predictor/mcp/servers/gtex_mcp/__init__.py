"""GTEx MCP Server - Python API

Access gene expression data across human tissues: expression levels, eQTLs, tissue specificity.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(tool: str, **kwargs) -> Dict[str, Any]:
    """Internal: call a GTEx MCP tool."""
    client = get_client('gtex')
    params = {k: v for k, v in kwargs.items() if v is not None}
    return client.call_tool(tool, params)


def get_gene_expression(gene: str, tissue: Optional[str] = None) -> Dict[str, Any]:
    """Get gene expression data across tissues.

    Args:
        gene: Gene symbol or Ensembl ID
        tissue: Specific tissue (optional, all tissues if omitted)
    Returns:
        dict with expression values (TPM) per tissue
    """
    return _call('get_gene_expression', gene=gene, tissue=tissue)


def get_median_gene_expression(gene: str) -> Dict[str, Any]:
    """Get median expression across all GTEx tissues.

    Args:
        gene: Gene symbol or Ensembl ID
    Returns:
        dict with median TPM per tissue (for tau index calculation)
    """
    return _call('get_median_gene_expression', gene=gene)


def get_gene_info(gene: str) -> Dict[str, Any]:
    """Get gene metadata from GTEx.

    Args:
        gene: Gene symbol or Ensembl ID
    Returns:
        dict with gene info
    """
    return _call('get_gene_info', gene=gene)


def get_tissue_info(tissue: Optional[str] = None) -> Dict[str, Any]:
    """Get GTEx tissue metadata.

    Args:
        tissue: Specific tissue ID (optional, all tissues if omitted)
    Returns:
        dict with tissue details and sample counts
    """
    return _call('get_tissue_info', tissue=tissue)


def get_single_tissue_eqtls(gene: str, tissue: str) -> Dict[str, Any]:
    """Get single-tissue eQTLs for a gene.

    Args:
        gene: Gene symbol or Ensembl ID
        tissue: GTEx tissue ID
    Returns:
        dict with eQTL variants and effect sizes
    """
    return _call('get_single_tissue_eqtls', gene=gene, tissue=tissue)


def get_top_expressed_genes(tissue: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Get top expressed genes in a tissue.

    Args:
        tissue: GTEx tissue ID
        limit: Max results
    Returns:
        dict with top genes by expression
    """
    return _call('get_top_expressed_genes', tissue=tissue, limit=limit)


__all__ = [
    'get_gene_expression',
    'get_median_gene_expression',
    'get_gene_info',
    'get_tissue_info',
    'get_single_tissue_eqtls',
    'get_top_expressed_genes',
]
