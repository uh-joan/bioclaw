"""AlphaFold MCP Server - Python API

Provides access to AlphaFold protein structure predictions.
Predicted 3D structures and per-residue confidence scores (pLDDT).
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(method: str, **kwargs) -> Dict[str, Any]:
    """Internal: call an AlphaFold MCP tool method."""
    client = get_client('alphafold')
    params = {k: v for k, v in kwargs.items() if v is not None}
    params['method'] = method
    return client.call_tool('alphafold_data', params)


def get_structure(uniprot_id: str) -> Dict[str, Any]:
    """
    Get AlphaFold predicted structure for a UniProt entry.

    Args:
        uniprot_id: UniProt accession (e.g., "P04637", "Q9Y6K9")

    Returns:
        dict: Structure prediction data and availability
    """
    # MCP server uses camelCase 'uniprotId'
    return _call('get_structure', uniprotId=uniprot_id)


def get_confidence_scores(uniprot_id: str) -> Dict[str, Any]:
    """
    Get per-residue confidence (pLDDT) scores for a predicted structure.

    Args:
        uniprot_id: UniProt accession (e.g., "P04637")

    Returns:
        dict: Confidence scores (pLDDT 0-100, higher = more confident)
    """
    return _call('get_confidence_scores', uniprotId=uniprot_id)


__all__ = [
    'get_structure',
    'get_confidence_scores',
]
