"""Monarch Initiative MCP Server - Python API

Access disease-gene-phenotype associations from the Monarch knowledge graph.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(tool: str, **kwargs) -> Dict[str, Any]:
    """Internal: call a Monarch MCP tool."""
    client = get_client('monarch')
    params = {k: v for k, v in kwargs.items() if v is not None}
    return client.call_tool(tool, params)


def get_disease_genes(disease: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Get genes associated with a disease.

    Args:
        disease: Disease name or MONDO ID
        limit: Max results
    Returns:
        dict with associated genes and evidence
    """
    return _call('get_disease_genes', disease=disease, limit=limit)


def get_disease_phenotypes(disease: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Get phenotypes associated with a disease.

    Args:
        disease: Disease name or MONDO ID
        limit: Max results
    Returns:
        dict with HPO phenotype terms
    """
    return _call('get_disease_phenotypes', disease=disease, limit=limit)


def get_gene_diseases(gene: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Get diseases associated with a gene.

    Args:
        gene: Gene symbol or ID
        limit: Max results
    Returns:
        dict with associated diseases
    """
    return _call('get_gene_diseases', gene=gene, limit=limit)


def get_entity(entity_id: str) -> Dict[str, Any]:
    """Get details for any Monarch entity (gene, disease, phenotype).

    Args:
        entity_id: Monarch entity ID (MONDO, HGNC, HP, etc.)
    Returns:
        dict with entity details
    """
    return _call('get_entity', entity_id=entity_id)


def get_associations(subject: Optional[str] = None, object: Optional[str] = None,
                      category: Optional[str] = None,
                      limit: Optional[int] = None) -> Dict[str, Any]:
    """Get associations between entities in Monarch.

    Args:
        subject: Subject entity ID
        object: Object entity ID
        category: Association category filter
        limit: Max results
    Returns:
        dict with associations
    """
    return _call('get_associations', subject=subject, object=object,
                 category=category, limit=limit)


__all__ = [
    'get_disease_genes',
    'get_disease_phenotypes',
    'get_gene_diseases',
    'get_entity',
    'get_associations',
]
