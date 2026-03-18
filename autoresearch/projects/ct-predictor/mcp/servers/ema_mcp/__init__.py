"""EMA (European Medicines Agency) MCP Server - Python API

Access EU drug approvals, EPARs, orphan designations, supply shortages,
and regulatory information through EMA's public JSON API.

CRITICAL EMA MCP QUIRKS:
1. Medicine names: Use trade names (e.g., "Ozempic", "Wegovy", "Humira")
2. Active substances: Use INN names (e.g., "semaglutide", "adalimumab")
3. Status values: "Authorised", "Withdrawn", "Refused"
4. Year format: Integer year (e.g., 2024, 2023)
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(method: str, **kwargs) -> Dict[str, Any]:
    """Internal: call an EMA MCP tool method."""
    client = get_client('ema')
    params = {k: v for k, v in kwargs.items() if v is not None}
    params['method'] = method
    return client.call_tool('ema_info', params)


def search_medicines(active_substance: Optional[str] = None,
                     therapeutic_area: Optional[str] = None,
                     status: Optional[str] = None,
                     orphan: Optional[bool] = None,
                     biosimilar: Optional[bool] = None,
                     limit: Optional[int] = None) -> Dict[str, Any]:
    """Search EU approved drugs.

    Args:
        active_substance: Active substance name (INN)
        therapeutic_area: Disease area
        status: Authorization status ("Authorised", "Withdrawn", "Refused")
        orphan: Filter for orphan medicines
        biosimilar: Filter for biosimilar medicines
        limit: Max results
    Returns:
        dict with EU medicine data
    """
    return _call('search_medicines', active_substance=active_substance,
                 therapeutic_area=therapeutic_area, status=status,
                 orphan=orphan, biosimilar=biosimilar, limit=limit)


def get_medicine_by_name(name: str) -> Dict[str, Any]:
    """Get specific medicine by trade name.

    Args:
        name: Medicine trade name (e.g. "Ozempic", "Keytruda")
    Returns:
        dict with detailed medicine information
    """
    return _call('get_medicine_by_name', name=name)


def get_orphan_designations(therapeutic_area: Optional[str] = None,
                             year: Optional[int] = None,
                             limit: Optional[int] = None) -> Dict[str, Any]:
    """Get EU orphan drug designations (rare disease medicines).

    Args:
        therapeutic_area: Disease area filter
        year: Filter by designation year
        limit: Max results
    Returns:
        dict with orphan designation data
    """
    return _call('get_orphan_designations', therapeutic_area=therapeutic_area,
                 year=year, limit=limit)


def get_supply_shortages(active_substance: Optional[str] = None,
                          medicine_name: Optional[str] = None,
                          status: Optional[str] = None,
                          limit: Optional[int] = None) -> Dict[str, Any]:
    """Get medicine shortage information.

    Args:
        active_substance: Filter by active substance
        medicine_name: Filter by medicine name
        status: Shortage status ("ongoing", "resolved")
        limit: Max results
    Returns:
        dict with supply shortage data
    """
    return _call('get_supply_shortages', active_substance=active_substance,
                 medicine_name=medicine_name, status=status, limit=limit)


def get_referrals(year: Optional[int] = None, safety: Optional[bool] = None,
                   limit: Optional[int] = None) -> Dict[str, Any]:
    """Get EU safety reviews (referrals).

    Args:
        year: Filter by year
        safety: Filter for safety-related referrals
        limit: Max results
    Returns:
        dict with referral data
    """
    return _call('get_referrals', year=year, safety=safety, limit=limit)


def get_post_auth_procedures(medicine_name: Optional[str] = None,
                              limit: Optional[int] = None) -> Dict[str, Any]:
    """Get post-authorization procedures (label updates, variations).

    Args:
        medicine_name: Filter by medicine name
        limit: Max results
    Returns:
        dict with post-authorization procedure data
    """
    return _call('get_post_auth_procedures', medicine_name=medicine_name, limit=limit)


def get_dhpcs(limit: Optional[int] = None) -> Dict[str, Any]:
    """Get Direct Healthcare Professional Communications (safety letters).

    Args:
        limit: Max results
    Returns:
        dict with DHPC safety communication data
    """
    return _call('get_dhpcs', limit=limit)


def get_psusas(limit: Optional[int] = None) -> Dict[str, Any]:
    """Get Periodic Safety Update Single Assessments.

    Args:
        limit: Max results
    Returns:
        dict with PSUSA data
    """
    return _call('get_psusas', limit=limit)


def get_pips(limit: Optional[int] = None) -> Dict[str, Any]:
    """Get Paediatric Investigation Plans.

    Args:
        limit: Max results
    Returns:
        dict with PIP data
    """
    return _call('get_pips', limit=limit)


def get_herbal_medicines(limit: Optional[int] = None) -> Dict[str, Any]:
    """Get herbal medicine assessments.

    Args:
        limit: Max results
    Returns:
        dict with herbal medicine data
    """
    return _call('get_herbal_medicines', limit=limit)


def get_article58_medicines(limit: Optional[int] = None) -> Dict[str, Any]:
    """Get Article 58 medicines (approved for non-EU markets).

    Args:
        limit: Max results
    Returns:
        dict with Article 58 medicine data
    """
    return _call('get_article58_medicines', limit=limit)


def search_epar_documents(limit: Optional[int] = None) -> Dict[str, Any]:
    """Search EPAR documents.

    Args:
        limit: Max results
    Returns:
        dict with EPAR document data
    """
    return _call('search_epar_documents', limit=limit)


def search_all_documents(limit: Optional[int] = None) -> Dict[str, Any]:
    """Search all EMA documents.

    Args:
        limit: Max results
    Returns:
        dict with EMA document data
    """
    return _call('search_all_documents', limit=limit)


def search_non_epar_documents(limit: Optional[int] = None) -> Dict[str, Any]:
    """Search non-EPAR EMA documents.

    Args:
        limit: Max results
    Returns:
        dict with non-EPAR document data
    """
    return _call('search_non_epar_documents', limit=limit)


__all__ = [
    'search_medicines',
    'get_medicine_by_name',
    'get_orphan_designations',
    'get_supply_shortages',
    'get_referrals',
    'get_post_auth_procedures',
    'get_dhpcs',
    'get_psusas',
    'get_pips',
    'get_herbal_medicines',
    'get_article58_medicines',
    'search_epar_documents',
    'search_all_documents',
    'search_non_epar_documents',
]
