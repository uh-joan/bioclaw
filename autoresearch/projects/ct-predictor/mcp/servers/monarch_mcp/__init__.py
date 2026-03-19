"""Monarch Initiative MCP Server - Python API

Access disease-gene-phenotype associations from the Monarch knowledge graph.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(method: str, **kwargs) -> Dict[str, Any]:
    """Internal: call a Monarch MCP tool method."""
    client = get_client('monarch')
    params = {k: v for k, v in kwargs.items() if v is not None}
    params['method'] = method
    return client.call_tool('monarch_data', params)


def search(query: str, category: Optional[str] = None,
           limit: Optional[int] = None) -> Dict[str, Any]:
    """Search Monarch knowledge graph.

    Args:
        query: Search term
        category: Entity category filter
        limit: Max results
    Returns:
        dict with matching entities
    """
    return _call('search', query=query, category=category, limit=limit)


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


def get_disease_genes(disease: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Get genes associated with a disease.

    First searches for disease_id if a text name is given.

    Args:
        disease: Disease name or MONDO ID (e.g. "MONDO:0005105")
        limit: Max results
    Returns:
        dict with associated genes and evidence
    """
    # Resolve text name to MONDO ID
    if not disease.startswith(('MONDO:', 'HP:', 'OMIM:')):
        results = search(query=disease, category='biolink:Disease', limit=1)
        items = results.get('results', results.get('items', []))
        if isinstance(items, list) and items:
            disease_id = items[0].get('id', disease)
        else:
            return {'error': f'No disease found for: {disease}'}
    else:
        disease_id = disease
    return _call('get_disease_genes', disease_id=disease_id, limit=limit)


def get_gene_diseases(gene: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Get diseases associated with a gene.

    Args:
        gene: Gene symbol or ID
        limit: Max results
    Returns:
        dict with associated diseases
    """
    return _call('get_gene_diseases', gene=gene, limit=limit)


def get_gene_phenotypes(gene: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Get phenotypes associated with a gene.

    Args:
        gene: Gene symbol or ID
        limit: Max results
    Returns:
        dict with associated phenotypes
    """
    return _call('get_gene_phenotypes', gene=gene, limit=limit)


def get_disease_phenotypes(disease: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Get phenotypes associated with a disease.

    Args:
        disease: Disease name or MONDO ID
        limit: Max results
    Returns:
        dict with HPO phenotype terms
    """
    return _call('get_disease_phenotypes', disease=disease, limit=limit)


def get_phenotype_genes(phenotype: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Get genes associated with a phenotype.

    Args:
        phenotype: Phenotype name or HP ID
        limit: Max results
    Returns:
        dict with associated genes
    """
    return _call('get_phenotype_genes', phenotype=phenotype, limit=limit)


def phenotype_gene_search(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Search for phenotype-gene associations.

    Args:
        query: Search term
        limit: Max results
    Returns:
        dict with phenotype-gene associations
    """
    return _call('phenotype_gene_search', query=query, limit=limit)


__all__ = [
    'search',
    'get_entity',
    'get_associations',
    'get_disease_genes',
    'get_gene_diseases',
    'get_gene_phenotypes',
    'get_disease_phenotypes',
    'get_phenotype_genes',
    'phenotype_gene_search',
]
