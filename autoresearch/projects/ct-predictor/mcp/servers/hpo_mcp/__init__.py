"""HPO (Human Phenotype Ontology) MCP Server - Python API

Access phenotype data: HPO terms, disease phenotypes, phenotype matching.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional, List


def _call(tool: str, **kwargs) -> Dict[str, Any]:
    """Internal: call an HPO MCP tool."""
    client = get_client('hpo')
    params = {k: v for k, v in kwargs.items() if v is not None}
    return client.call_tool(tool, params)


def search_terms(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Search HPO terms by name or synonym.

    Args:
        query: Phenotype description (e.g. "seizure", "cardiomyopathy")
        limit: Max results
    Returns:
        dict with matching HPO terms
    """
    return _call('search_terms', query=query, limit=limit)


def get_term_details(term_id: str) -> Dict[str, Any]:
    """Get details for a specific HPO term.

    Args:
        term_id: HPO term ID (e.g. HP:0001250)
    Returns:
        dict with term name, definition, synonyms
    """
    return _call('get_term_details', term_id=term_id)


def batch_get_hpo_terms(term_ids: str) -> Dict[str, Any]:
    """Get multiple HPO terms at once.

    Args:
        term_ids: Comma-separated HPO term IDs
    Returns:
        dict with term details for each ID
    """
    return _call('batch_get_hpo_terms', term_ids=term_ids)


def compare_hpo_terms(terms_a: str, terms_b: str) -> Dict[str, Any]:
    """Compare two sets of HPO terms for phenotype similarity.

    Args:
        terms_a: Comma-separated HPO term IDs (first set)
        terms_b: Comma-separated HPO term IDs (second set)
    Returns:
        dict with similarity scores
    """
    return _call('compare_hpo_terms', terms_a=terms_a, terms_b=terms_b)


def get_hpo_ancestors(term_id: str) -> Dict[str, Any]:
    """Get ancestor terms in the HPO hierarchy.

    Args:
        term_id: HPO term ID
    Returns:
        dict with ancestor terms
    """
    return _call('get_hpo_ancestors', term_id=term_id)


def get_all_hpo_terms(limit: Optional[int] = None) -> Dict[str, Any]:
    """Get all HPO terms (or a subset).

    Args:
        limit: Max results
    Returns:
        dict with HPO terms
    """
    return _call('get_all_hpo_terms', limit=limit)


__all__ = [
    'search_terms',
    'get_term_details',
    'batch_get_hpo_terms',
    'compare_hpo_terms',
    'get_hpo_ancestors',
    'get_all_hpo_terms',
]
