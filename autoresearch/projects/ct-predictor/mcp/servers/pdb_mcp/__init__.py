"""PDB MCP Server - Python API

Provides access to the Protein Data Bank (PDB).
3D structural data for proteins, nucleic acids, and complex assemblies.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(method: str, **kwargs) -> Dict[str, Any]:
    """Internal: call a PDB MCP tool method."""
    client = get_client('pdb')
    params = {k: v for k, v in kwargs.items() if v is not None}
    params['method'] = method
    return client.call_tool('pdb_data', params)


def search_by_uniprot(uniprot_id: str) -> Dict[str, Any]:
    """
    Search PDB structures by UniProt accession.

    Args:
        uniprot_id: UniProt accession (e.g., "P04637")

    Returns:
        dict: PDB structures mapped to the UniProt entry
    """
    return _call('search_by_uniprot', uniprot_id=uniprot_id)


def search_structures(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Search PDB structures by keyword or protein name.

    Args:
        query: Search query (e.g., "EGFR kinase", "insulin receptor")
        limit: Maximum results (optional)

    Returns:
        dict: Matching PDB structures with metadata
    """
    return _call('search_structures', query=query, limit=limit)


__all__ = [
    'search_by_uniprot',
    'search_structures',
]
