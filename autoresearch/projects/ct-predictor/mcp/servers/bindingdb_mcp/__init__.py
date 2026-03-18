"""BindingDB MCP Server - Python API

Access binding affinity data (Ki, Kd, IC50, EC50) for drug-target interactions.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(method: str, **kwargs) -> Dict[str, Any]:
    """Internal: call a BindingDB MCP tool method."""
    client = get_client('bindingdb')
    params = {k: v for k, v in kwargs.items() if v is not None}
    params['method'] = method
    return client.call_tool('bindingdb_data', params)


def search_by_name(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Search BindingDB by compound or target name.

    Args:
        query: Drug or target name
        limit: Max results
    Returns:
        dict with matching entries and binding data
    """
    return _call('search_by_name', compound_name=query, limit=limit)


def search_by_smiles(smiles: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Search BindingDB by SMILES string.

    Args:
        smiles: SMILES chemical notation
        limit: Max results
    Returns:
        dict with matching compounds
    """
    return _call('search_by_smiles', smiles=smiles, limit=limit)


def search_by_target_name(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Search BindingDB by target name.

    Args:
        query: Target protein name
        limit: Max results
    Returns:
        dict with matching targets
    """
    return _call('search_by_target_name', query=query, limit=limit)


def get_ki_by_target(target: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Get Ki values for a target protein.

    Args:
        target: Target protein name or ID
        limit: Max results
    Returns:
        dict with Ki measurements
    """
    return _call('get_ki_by_target', target=target, limit=limit)


def get_ligands_by_target(target: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Get all ligands binding a target.

    Args:
        target: Target protein name or ID
        limit: Max results
    Returns:
        dict with ligands and their binding data
    """
    return _call('get_ligands_by_target', target=target, limit=limit)


def get_ligand_info(ligand_id: str) -> Dict[str, Any]:
    """Get detailed info for a specific ligand.

    Args:
        ligand_id: BindingDB ligand monomer ID
    Returns:
        dict with ligand details and binding affinities
    """
    return _call('get_ligand_info', ligand_id=ligand_id)


def get_target_info(target: str) -> Dict[str, Any]:
    """Get info about a specific target.

    Args:
        target: Target protein name or UniProt ID
    Returns:
        dict with target details
    """
    return _call('get_target_info', target=target)


__all__ = [
    'search_by_name',
    'search_by_smiles',
    'search_by_target_name',
    'get_ki_by_target',
    'get_ligands_by_target',
    'get_ligand_info',
    'get_target_info',
]
