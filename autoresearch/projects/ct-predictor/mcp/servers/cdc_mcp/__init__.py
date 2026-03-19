"""CDC MCP Server - Python API

Provides access to CDC (Centers for Disease Control and Prevention) health data.
Public health surveillance datasets and available measures.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(method: str, **kwargs) -> Dict[str, Any]:
    """Internal: call a CDC MCP tool method."""
    client = get_client('cdc')
    params = {k: v for k, v in kwargs.items() if v is not None}
    params['method'] = method
    return client.call_tool('cdc_health_data', params)


def search_dataset(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Search CDC health surveillance datasets.

    Args:
        query: Health topic or condition (e.g., "diabetes", "cancer mortality")
        limit: Maximum results (optional)

    Returns:
        dict: Matching CDC surveillance datasets
    """
    return _call('search_dataset', query=query, limit=limit)


def get_available_measures() -> Dict[str, Any]:
    """
    Get all available CDC health measures.

    Returns:
        dict: Available measures and health indicators
    """
    return _call('get_available_measures')


__all__ = [
    'search_dataset',
    'get_available_measures',
]
