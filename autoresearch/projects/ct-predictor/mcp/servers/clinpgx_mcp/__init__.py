"""ClinPGx MCP Server - Python API

Access pharmacogenomics data: drug-gene pairs, clinical guidelines, alleles, drug labels.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(method: str, **kwargs) -> Dict[str, Any]:
    """Internal: call a ClinPGx MCP tool method."""
    client = get_client('clinpgx')
    params = {k: v for k, v in kwargs.items() if v is not None}
    params['method'] = method
    return client.call_tool('clinpgx_data', params)


def get_gene(gene: str) -> Dict[str, Any]:
    """Get pharmacogene details.

    Args:
        gene: Gene symbol (e.g. CYP2D6)
    Returns:
        dict with gene PGx info
    """
    return _call('get_gene', gene=gene)


def get_chemical(drug: str) -> Dict[str, Any]:
    """Get chemical/drug details from PharmGKB.

    This is the most reliable ClinPGx method.

    Args:
        drug: Drug name (e.g. "warfarin", "pembrolizumab")
    Returns:
        dict with PharmGKB chemical data
    """
    return _call('get_chemical', drug=drug)


def search_genes(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Search pharmacogenes.

    Args:
        query: Gene name or keyword
        limit: Max results
    Returns:
        dict with matching genes
    """
    return _call('search_genes', query=query, limit=limit)


def get_chemical(drug: str) -> Dict[str, Any]:
    """Get chemical/drug details from PharmGKB.

    Args:
        drug: Drug name
    Returns:
        dict with drug info and PGx associations
    """
    return _call('get_chemical', drug=drug)


def get_gene_drug_pairs(gene: Optional[str] = None, drug: Optional[str] = None,
                         limit: Optional[int] = None) -> Dict[str, Any]:
    """Get gene-drug pair information.

    Args:
        gene: Gene symbol
        drug: Drug name
        limit: Max results
    Returns:
        dict with gene-drug pair data
    """
    return _call('get_gene_drug_pairs', gene=gene, drug=drug, limit=limit)


def get_guidelines(gene: Optional[str] = None, drug: Optional[str] = None,
                    limit: Optional[int] = None) -> Dict[str, Any]:
    """Get clinical PGx guidelines (CPIC, DPWG).

    Args:
        gene: Gene symbol
        drug: Drug name
        limit: Max results
    Returns:
        dict with clinical guidelines
    """
    return _call('get_guidelines', gene=gene, drug=drug, limit=limit)


def get_alleles(gene: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Get known alleles for a pharmacogene.

    Args:
        gene: Gene symbol (e.g. CYP2D6, CYP3A4)
        limit: Max results
    Returns:
        dict with allele definitions and function
    """
    return _call('get_alleles', gene=gene, limit=limit)


def get_clinical_annotations(drug: Optional[str] = None, gene: Optional[str] = None,
                              limit: Optional[int] = None) -> Dict[str, Any]:
    """Get clinical annotations for drug-gene pairs.

    Args:
        drug: Drug name
        gene: Gene symbol (e.g. CYP2D6)
        limit: Max results
    Returns:
        dict with clinical annotations including level of evidence
    """
    return _call('get_clinical_annotations', drug=drug, gene=gene, limit=limit)


def get_drug_labels(drug: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Get FDA/EMA drug labels with PGx information.

    Args:
        drug: Drug name
        limit: Max results
    Returns:
        dict with drug label annotations
    """
    return _call('get_drug_labels', drug=drug, limit=limit)


def search_variants(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Search PGx variants.

    Args:
        query: Variant or gene name
        limit: Max results
    Returns:
        dict with matching variants
    """
    return _call('search_variants', query=query, limit=limit)


__all__ = [
    'get_gene',
    'search_genes',
    'get_chemical',
    'get_gene_drug_pairs',
    'get_guidelines',
    'get_alleles',
    'get_clinical_annotations',
    'get_drug_labels',
    'search_variants',
]
