"""STRING-DB MCP Server - Python API

Access protein-protein interaction data: interaction networks, enrichment, annotations.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(tool: str, **kwargs) -> Dict[str, Any]:
    """Internal: call a STRING-DB MCP tool."""
    client = get_client('stringdb')
    params = {k: v for k, v in kwargs.items() if v is not None}
    return client.call_tool(tool, params)


def get_protein_interactions(protein: str, species: Optional[int] = None,
                              score_threshold: Optional[float] = None,
                              limit: Optional[int] = None) -> Dict[str, Any]:
    """Get protein-protein interactions for a query protein.

    Args:
        protein: Protein name or identifier
        species: NCBI taxonomy ID (9606 for human)
        score_threshold: Minimum combined score (0-1)
        limit: Max interactions
    Returns:
        dict with interaction partners and scores
    """
    return _call('get_protein_interactions', protein=protein, species=species,
                 score_threshold=score_threshold, limit=limit)


def get_interaction_network(proteins: str, species: Optional[int] = None,
                             score_threshold: Optional[float] = None) -> Dict[str, Any]:
    """Get interaction network for multiple proteins.

    Args:
        proteins: Comma-separated protein names
        species: NCBI taxonomy ID (9606 for human)
        score_threshold: Minimum combined score (0-1)
    Returns:
        dict with network edges and scores
    """
    return _call('get_interaction_network', proteins=proteins, species=species,
                 score_threshold=score_threshold)


def get_functional_enrichment(proteins: str, species: Optional[int] = None) -> Dict[str, Any]:
    """Get functional enrichment analysis for a set of proteins.

    Args:
        proteins: Comma-separated protein names
        species: NCBI taxonomy ID (9606 for human)
    Returns:
        dict with enriched GO terms, KEGG pathways, etc.
    """
    return _call('get_functional_enrichment', proteins=proteins, species=species)


def get_protein_annotations(protein: str, species: Optional[int] = None) -> Dict[str, Any]:
    """Get annotations for a protein.

    Args:
        protein: Protein name or identifier
        species: NCBI taxonomy ID (9606 for human)
    Returns:
        dict with protein annotations
    """
    return _call('get_protein_annotations', protein=protein, species=species)


__all__ = [
    'get_protein_interactions',
    'get_interaction_network',
    'get_functional_enrichment',
    'get_protein_annotations',
]
