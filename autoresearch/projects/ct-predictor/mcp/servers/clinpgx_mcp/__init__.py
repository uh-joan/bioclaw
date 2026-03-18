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


def get_alleles(gene: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Get known alleles for a pharmacogene.

    Args:
        gene: Gene symbol (e.g. CYP2D6, CYP3A4)
        limit: Max results
    Returns:
        dict with allele definitions and function
    """
    return _call('get_alleles', gene=gene, limit=limit)


def get_chemical(drug: str) -> Dict[str, Any]:
    """Get chemical/drug details from PharmGKB.

    Args:
        drug: Drug name
    Returns:
        dict with drug info and PGx associations
    """
    return _call('get_chemical', drug=drug)


__all__ = [
    'get_clinical_annotations',
    'get_drug_labels',
    'get_alleles',
    'get_chemical',
]
