"""Reactome MCP Server - Python API

Access biological pathway data: pathway lookup, hierarchy, participants.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(tool: str, **kwargs) -> Dict[str, Any]:
    """Internal: call a Reactome MCP tool."""
    client = get_client('reactome')
    params = {k: v for k, v in kwargs.items() if v is not None}
    return client.call_tool(tool, params)


def find_pathways_by_gene(gene: str, species: Optional[str] = None) -> Dict[str, Any]:
    """Find pathways involving a gene.

    Args:
        gene: Gene symbol (e.g. BRCA1, TP53)
        species: Species name (default: Homo sapiens)
    Returns:
        dict with pathways containing the gene
    """
    return _call('find_pathways_by_gene', gene=gene, species=species)


def get_pathway_details(pathway_id: str) -> Dict[str, Any]:
    """Get details for a specific Reactome pathway.

    Args:
        pathway_id: Reactome stable ID (e.g. R-HSA-1640170)
    Returns:
        dict with pathway name, summary, species
    """
    return _call('get_pathway_details', pathway_id=pathway_id)


def get_pathway_hierarchy(pathway_id: str) -> Dict[str, Any]:
    """Get pathway hierarchy (parent/child relationships).

    Args:
        pathway_id: Reactome stable ID
    Returns:
        dict with hierarchy tree
    """
    return _call('get_pathway_hierarchy', pathway_id=pathway_id)


def get_pathway_participants(pathway_id: str) -> Dict[str, Any]:
    """Get genes/proteins participating in a pathway.

    Args:
        pathway_id: Reactome stable ID
    Returns:
        dict with participant entities
    """
    return _call('get_pathway_participants', pathway_id=pathway_id)


def find_pathways_by_disease(disease: str, species: Optional[str] = None) -> Dict[str, Any]:
    """Find pathways associated with a disease.

    Args:
        disease: Disease name
        species: Species name (default: Homo sapiens)
    Returns:
        dict with disease-associated pathways
    """
    return _call('find_pathways_by_disease', disease=disease, species=species)


__all__ = [
    'find_pathways_by_gene',
    'get_pathway_details',
    'get_pathway_hierarchy',
    'get_pathway_participants',
    'find_pathways_by_disease',
]
