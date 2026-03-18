"""OpenAlex MCP Server - Python API

Access scholarly metadata: works, authors, institutions, citations.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(method: str, **kwargs) -> Dict[str, Any]:
    """Internal: call an OpenAlex MCP tool method."""
    client = get_client('openalex')
    params = {k: v for k, v in kwargs.items() if v is not None}
    params['method'] = method
    return client.call_tool('openalex_data', params)


def search_works(query: str, limit: Optional[int] = None,
                 filter: Optional[str] = None) -> Dict[str, Any]:
    """Search for scholarly works by keyword.

    Args:
        query: Search query (title, abstract keywords)
        limit: Max results
        filter: OpenAlex filter string
    Returns:
        dict with matching works and metadata
    """
    return _call('search_works', query=query, limit=limit, filter=filter)


def get_work(work_id: str) -> Dict[str, Any]:
    """Get details for a specific work by OpenAlex ID or DOI.

    Args:
        work_id: OpenAlex work ID or DOI
    Returns:
        dict with work metadata, citations, concepts
    """
    return _call('get_work', work_id=work_id)


def get_cited_by(work_id: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Get works that cite a given work.

    Args:
        work_id: OpenAlex work ID or DOI
        limit: Max results
    Returns:
        dict with citing works
    """
    return _call('get_cited_by', work_id=work_id, limit=limit)


def search_authors(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Search for authors by name.

    Args:
        query: Author name
        limit: Max results
    Returns:
        dict with matching authors
    """
    return _call('search_authors', query=query, limit=limit)


def get_author(author_id: str) -> Dict[str, Any]:
    """Get author details by OpenAlex ID.

    Args:
        author_id: OpenAlex author ID
    Returns:
        dict with author profile and works count
    """
    return _call('get_author', author_id=author_id)


def get_works_by_author(author_id: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Get works by a specific author.

    Args:
        author_id: OpenAlex author ID
        limit: Max results
    Returns:
        dict with author's works
    """
    return _call('get_works_by_author', author_id=author_id, limit=limit)


__all__ = [
    'search_works',
    'get_work',
    'get_cited_by',
    'search_authors',
    'get_author',
    'get_works_by_author',
]
