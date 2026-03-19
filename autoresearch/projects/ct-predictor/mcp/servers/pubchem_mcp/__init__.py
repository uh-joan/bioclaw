"""PubChem MCP Server - Python API

Provides access to PubChem chemical compound database (NCBI/NIH).
Chemical properties, bioassay data, and molecular descriptors for 100M+ compounds.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(method: str, **kwargs) -> Dict[str, Any]:
    """Internal: call a PubChem MCP tool method."""
    client = get_client('pubchem')
    params = {k: v for k, v in kwargs.items() if v is not None}
    params['method'] = method
    return client.call_tool('pubchem', params)


def search_compounds(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Search PubChem compounds by name, SMILES, or InChI.

    Args:
        query: Compound name, SMILES, or identifier (e.g., "aspirin", "imatinib")
        limit: Maximum results (optional)

    Returns:
        dict: Matching compounds with CID identifiers
    """
    return _call('search_compounds', query=query, limit=limit)


def get_compound_properties(cid: str) -> Dict[str, Any]:
    """
    Get molecular properties for a PubChem compound.

    Args:
        cid: PubChem compound ID (CID)

    Returns:
        dict: Molecular properties including MW, XLogP, H-bond donors/acceptors,
              rotatable bonds, complexity score
    """
    return _call('get_compound_properties', cid=cid)


__all__ = [
    'search_compounds',
    'get_compound_properties',
]
