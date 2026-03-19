"""NLM MCP Server - Python API

Provides access to the National Library of Medicine clinical trial code lookups.
Condition codes (ICD-10-CM) and standardized condition terminology.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(method: str, **kwargs) -> Dict[str, Any]:
    """Internal: call an NLM MCP tool method."""
    client = get_client('nlm')
    params = {k: v for k, v in kwargs.items() if v is not None}
    params['method'] = method
    return client.call_tool('nlm_ct_codes', params)


def search_conditions(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Search NLM condition codes for clinical trials.

    Args:
        query: Condition name (e.g., "breast cancer", "diabetes")
        limit: Maximum results (optional)

    Returns:
        dict: Matching condition codes and terminology
    """
    return _call('conditions', query=query, limit=limit)


def search_icd10(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Search ICD-10-CM diagnosis codes.

    Args:
        query: Condition or code (e.g., "melanoma", "C43")
        limit: Maximum results (optional)

    Returns:
        dict: Matching ICD-10-CM codes (count = disease complexity signal)
    """
    return _call('icd-10-cm', query=query, limit=limit)


__all__ = [
    'search_conditions',
    'search_icd10',
]
