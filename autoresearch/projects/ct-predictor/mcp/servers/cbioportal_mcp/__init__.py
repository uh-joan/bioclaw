"""cBioPortal MCP Server - Python API

Access cancer genomics data: mutations, copy number, molecular profiles across studies.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(method: str, **kwargs) -> Dict[str, Any]:
    """Internal: call a cBioPortal MCP tool method."""
    client = get_client('cbioportal')
    params = {k: v for k, v in kwargs.items() if v is not None}
    params['method'] = method
    return client.call_tool('cbioportal_data', params)


def get_gene(gene: str) -> Dict[str, Any]:
    """Get gene info and mutation frequency across cancer studies.

    Args:
        gene: Gene symbol (e.g. TP53, KRAS, EGFR)
    Returns:
        dict with gene details and mutation data
    """
    return _call('get_gene', gene=gene)


def get_molecular_profiles(study_id: str) -> Dict[str, Any]:
    """Get molecular profiles available for a cancer study.

    Args:
        study_id: cBioPortal study ID (e.g. "tcga_brca")
    Returns:
        dict with available molecular profiles
    """
    return _call('get_molecular_profiles', study_id=study_id)


def get_clinical_attributes(study_id: str) -> Dict[str, Any]:
    """Get clinical attributes for a cancer study.

    Args:
        study_id: cBioPortal study ID
    Returns:
        dict with clinical attribute definitions
    """
    return _call('get_clinical_attributes', study_id=study_id)


def get_copy_number(gene: str, study_id: Optional[str] = None) -> Dict[str, Any]:
    """Get copy number alterations for a gene.

    Args:
        gene: Gene symbol
        study_id: Specific study ID (optional)
    Returns:
        dict with CNA data across samples
    """
    return _call('get_copy_number', gene=gene, study_id=study_id)


__all__ = [
    'get_gene',
    'get_molecular_profiles',
    'get_clinical_attributes',
    'get_copy_number',
]
