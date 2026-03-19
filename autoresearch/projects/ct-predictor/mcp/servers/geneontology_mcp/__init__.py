"""Gene Ontology MCP Server - Python API

Provides access to the Gene Ontology (GO) knowledgebase.
Functional annotations: biological process, molecular function, cellular component.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(method: str, **kwargs) -> Dict[str, Any]:
    """Internal: call a Gene Ontology MCP tool method."""
    client = get_client('geneontology')
    params = {k: v for k, v in kwargs.items() if v is not None}
    params['method'] = method
    return client.call_tool('go_data', params)


def search_go_terms(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Search Gene Ontology terms by gene or keyword.

    Args:
        query: Gene symbol or GO term keyword (e.g., "EGFR", "kinase activity")
        limit: Maximum results (optional)

    Returns:
        dict: GO term annotations with categories (BP, MF, CC)
    """
    return _call('search_go_terms', query=query, limit=limit)


__all__ = [
    'search_go_terms',
]
