"""GWAS Catalog MCP Server - Python API

Access genome-wide association study data: gene-trait associations, variants, studies.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(method: str, **kwargs) -> Dict[str, Any]:
    """Internal: call a GWAS MCP tool method."""
    client = get_client('gwas')
    params = {k: v for k, v in kwargs.items() if v is not None}
    params['method'] = method
    return client.call_tool('gwas_data', params)


def search_associations(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Search GWAS associations by keyword.

    Args:
        query: Search term
        limit: Max results
    Returns:
        dict with matching associations
    """
    return _call('search_associations', query=query, limit=limit)


def get_gene_associations(gene: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Get GWAS associations for a gene.

    Args:
        gene: Gene symbol (e.g. APOE, BRCA1)
        limit: Max results
    Returns:
        dict with GWAS hits, p-values, traits
    """
    return _call('get_gene_associations', gene=gene, limit=limit)


def get_trait_associations(trait: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Get GWAS associations for a trait/disease.

    Args:
        trait: Trait or disease name (e.g. "type 2 diabetes")
        limit: Max results
    Returns:
        dict with associated variants and genes
    """
    return _call('get_trait_associations', trait=trait, limit=limit)


def get_study(study_id: str) -> Dict[str, Any]:
    """Get details for a specific GWAS study.

    Args:
        study_id: GWAS Catalog study accession (e.g. GCST000001)
    Returns:
        dict with study metadata
    """
    return _call('get_study', study_id=study_id)


def get_variant(variant_id: str) -> Dict[str, Any]:
    """Get GWAS data for a specific variant.

    Args:
        variant_id: rsID (e.g. rs7903146)
    Returns:
        dict with variant associations
    """
    return _call('get_variant', variant_id=variant_id)


def get_variant_associations(variant_id: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Get all GWAS associations for a variant.

    Args:
        variant_id: rsID
        limit: Max results
    Returns:
        dict with variant associations
    """
    return _call('get_variant_associations', variant_id=variant_id, limit=limit)


def search_by_trait(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Search GWAS studies by trait name.

    Note: Uses search_associations which works reliably.
    The dedicated trait endpoint requires an EFO ID.

    Args:
        query: Trait or disease name
        limit: Max results
    Returns:
        dict with matching associations (total, associations with pvalue data)
    """
    return _call('search_associations', query=query, limit=limit)


def search_studies(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Search GWAS studies.

    Args:
        query: Search term
        limit: Max results
    Returns:
        dict with matching studies
    """
    return _call('search_studies', query=query, limit=limit)


def get_region_associations(region: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Get GWAS associations in a genomic region.

    Args:
        region: Genomic region (e.g. "6:28000000-34000000")
        limit: Max results
    Returns:
        dict with associations in the region
    """
    return _call('get_region_associations', region=region, limit=limit)


def search_genes(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Search genes in GWAS catalog.

    Args:
        query: Gene name or keyword
        limit: Max results
    Returns:
        dict with matching genes
    """
    return _call('search_genes', query=query, limit=limit)


__all__ = [
    'search_associations',
    'get_gene_associations',
    'get_trait_associations',
    'get_study',
    'get_variant',
    'get_variant_associations',
    'search_by_trait',
    'search_studies',
    'get_region_associations',
    'search_genes',
]
