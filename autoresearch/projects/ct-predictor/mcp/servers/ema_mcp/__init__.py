"""EMA (European Medicines Agency) MCP Server - Python API

Provides Python functions for EU drug approvals, EPARs, orphan designations,
supply shortages, and regulatory information through EMA's public JSON API.
Data stays in execution environment - only summaries flow to model.

CRITICAL EMA MCP QUIRKS:
1. Medicine names: Use trade names (e.g., "Ozempic", "Wegovy", "Humira")
2. Active substances: Use INN names (e.g., "semaglutide", "adalimumab")
3. Status values: "Authorised", "Withdrawn", "Refused"
4. Year format: Integer year (e.g., 2024, 2023)
5. EPAR documents: European Public Assessment Reports
6. Orphan medicines: Rare disease designations
7. DHPC: Direct Healthcare Professional Communications (safety alerts)
8. PSUSA: Periodic Safety Update Single Assessment
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def ema_info(
    method: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Unified EMA data access function

    Args:
        method: Operation to perform
        **kwargs: Method-specific parameters

    Returns:
        dict: EMA API response
    """
    client = get_client('ema-mcp-server')

    params = {'method': method}
    params.update(kwargs)

    return client.call_tool('ema_info', params)


# =============================================================================
# Medicine Search
# =============================================================================

def search_medicines(
    active_substance: Optional[str] = None,
    therapeutic_area: Optional[str] = None,
    status: Optional[str] = None,
    orphan: Optional[bool] = None,
    biosimilar: Optional[bool] = None,
    conditional_approval: Optional[bool] = None,
    prime: Optional[bool] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Search EU approved drugs

    Args:
        active_substance: Active substance name (INN)
                         Examples: "semaglutide", "adalimumab", "pembrolizumab"

        therapeutic_area: Therapeutic area or disease
                         Examples: "diabetes", "cancer", "multiple sclerosis", "obesity"

        status: Medicine authorization status
               Values: "Authorised", "Withdrawn", "Refused"

        orphan: Filter for orphan medicines only (rare diseases)

        biosimilar: Filter for biosimilar medicines only

        conditional_approval: Filter for conditionally approved medicines

        prime: Filter for PRIME (priority) medicines

        limit: Maximum results (default: 100)

    Returns:
        dict: EU medicine data

        Key fields:
        - medicine_name: Trade name
        - active_substance: INN name
        - therapeutic_area: Disease/indication
        - marketing_authorisation_date: Approval date
        - authorisation_status: Current status
        - atc_code: ATC classification

    Examples:
        # Search for GLP-1 medicines
        results = search_medicines(
            active_substance="semaglutide"
        )

        for med in results.get('data', []):
            name = med.get('medicine_name')
            substance = med.get('active_substance')
            status = med.get('authorisation_status')
            print(f"{name} ({substance}): {status}")

        # Diabetes medicines
        results = search_medicines(
            therapeutic_area="diabetes",
            status="Authorised",
            limit=50
        )

        # Orphan medicines for cancer
        results = search_medicines(
            therapeutic_area="cancer",
            orphan=True
        )

        # Biosimilars only
        results = search_medicines(
            biosimilar=True,
            limit=200
        )

        # PRIME medicines (priority review)
        results = search_medicines(
            prime=True
        )
    """
    params = {
        'limit': limit
    }

    if active_substance:
        params['active_substance'] = active_substance
    if therapeutic_area:
        params['therapeutic_area'] = therapeutic_area
    if status:
        params['status'] = status
    if orphan is not None:
        params['orphan'] = orphan
    if biosimilar is not None:
        params['biosimilar'] = biosimilar
    if conditional_approval is not None:
        params['conditional_approval'] = conditional_approval
    if prime is not None:
        params['prime'] = prime

    return ema_info(method='search_medicines', **params)


def get_medicine_by_name(
    name: str
) -> Dict[str, Any]:
    """
    Get specific medicine by trade name

    Args:
        name: Medicine trade name
             Examples: "Ozempic", "Wegovy", "Humira", "Keytruda"

    Returns:
        dict: Detailed medicine information

        Key fields:
        - medicine_name: Trade name
        - active_substance: INN name
        - therapeutic_area: Disease area
        - marketing_authorisation_holder: Company
        - marketing_authorisation_date: Approval date
        - authorisation_status: Current status
        - conditions_of_use: Approved indications

    Examples:
        # Get Ozempic details
        result = get_medicine_by_name(name="Ozempic")

        if result.get('data'):
            med = result['data']
            print(f"Name: {med.get('medicine_name')}")
            print(f"Active substance: {med.get('active_substance')}")
            print(f"Company: {med.get('marketing_authorisation_holder')}")
            print(f"Approved: {med.get('marketing_authorisation_date')}")

        # Get Keytruda details
        result = get_medicine_by_name(name="Keytruda")
    """
    return ema_info(method='get_medicine_by_name', name=name)


# =============================================================================
# Orphan Designations
# =============================================================================

def get_orphan_designations(
    therapeutic_area: Optional[str] = None,
    year: Optional[int] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Get EU orphan drug designations (rare disease medicines)

    Args:
        therapeutic_area: Disease area filter
                         Examples: "oncology", "metabolic", "neurological"

        year: Filter by designation year (e.g., 2024, 2023)

        limit: Maximum results (default: 100)

    Returns:
        dict: Orphan designation data

        Key fields:
        - medicine_name: Drug name
        - active_substance: INN name
        - orphan_designation_status: Active/Withdrawn
        - therapeutic_indication: Rare disease indication
        - decision_date: Designation date

    Examples:
        # Recent orphan designations
        results = get_orphan_designations(
            year=2024,
            limit=50
        )

        for designation in results.get('data', []):
            name = designation.get('medicine_name')
            indication = designation.get('therapeutic_indication')
            print(f"{name}: {indication}")

        # Oncology orphan drugs
        results = get_orphan_designations(
            therapeutic_area="oncology"
        )
    """
    params = {
        'limit': limit
    }

    if therapeutic_area:
        params['therapeutic_area'] = therapeutic_area
    if year:
        params['year'] = year

    return ema_info(method='get_orphan_designations', **params)


# =============================================================================
# Supply Shortages
# =============================================================================

def get_supply_shortages(
    active_substance: Optional[str] = None,
    medicine_name: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get medicine shortage information

    Args:
        active_substance: Filter by active substance

        medicine_name: Filter by medicine name

        status: Shortage status
               Values: "ongoing", "resolved"

        limit: Maximum results (default: 50)

    Returns:
        dict: Supply shortage data

        Key fields:
        - medicine_name: Affected medicine
        - active_substance: INN name
        - shortage_status: ongoing/resolved
        - expected_resolution: Estimated resolution date
        - affected_countries: EU countries affected

    Examples:
        # Ongoing shortages
        results = get_supply_shortages(
            status="ongoing"
        )

        for shortage in results.get('data', []):
            name = shortage.get('medicine_name')
            status = shortage.get('shortage_status')
            resolution = shortage.get('expected_resolution')
            print(f"{name}: {status}, expected resolution: {resolution}")

        # Insulin shortages
        results = get_supply_shortages(
            active_substance="insulin"
        )
    """
    params = {
        'limit': limit
    }

    if active_substance:
        params['active_substance'] = active_substance
    if medicine_name:
        params['medicine_name'] = medicine_name
    if status:
        params['status'] = status

    return ema_info(method='get_supply_shortages', **params)


# =============================================================================
# Referrals and Safety Reviews
# =============================================================================

def get_referrals(
    year: Optional[int] = None,
    safety: Optional[bool] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Get EU safety reviews (referrals)

    Args:
        year: Filter by year (e.g., 2024, 2023)

        safety: Filter for safety-related referrals
               True = Safety referrals only

        limit: Maximum results (default: 100)

    Returns:
        dict: Referral/safety review data

    Examples:
        # Safety referrals in 2024
        results = get_referrals(
            year=2024,
            safety=True
        )

        for referral in results.get('data', []):
            name = referral.get('medicine_name')
            reason = referral.get('referral_reason')
            print(f"{name}: {reason}")
    """
    params = {
        'limit': limit
    }

    if year:
        params['year'] = year
    if safety is not None:
        params['safety'] = safety

    return ema_info(method='get_referrals', **params)


# =============================================================================
# Post-Authorization Procedures
# =============================================================================

def get_post_auth_procedures(
    medicine_name: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Get post-authorization procedures (label updates, variations)

    Args:
        medicine_name: Filter by medicine name

        limit: Maximum results (default: 100)

    Returns:
        dict: Post-authorization procedure data

    Examples:
        # Keytruda label updates
        results = get_post_auth_procedures(
            medicine_name="Keytruda"
        )

        for proc in results.get('data', []):
            type = proc.get('procedure_type')
            date = proc.get('decision_date')
            print(f"{type}: {date}")
    """
    params = {
        'limit': limit
    }

    if medicine_name:
        params['medicine_name'] = medicine_name

    return ema_info(method='get_post_auth_procedures', **params)


# =============================================================================
# Safety Communications
# =============================================================================

def get_dhpcs(
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get Direct Healthcare Professional Communications (safety letters)

    DHPCs are urgent safety communications sent to healthcare professionals.

    Args:
        limit: Maximum results (default: 50)

    Returns:
        dict: DHPC safety communication data

        Key fields:
        - medicine_name: Affected medicine
        - active_substance: INN name
        - dhpc_date: Communication date
        - safety_issue: Description of safety concern

    Examples:
        # Recent safety communications
        results = get_dhpcs(limit=20)

        for dhpc in results.get('data', []):
            name = dhpc.get('medicine_name')
            issue = dhpc.get('safety_issue')
            date = dhpc.get('dhpc_date')
            print(f"{date} - {name}: {issue}")
    """
    return ema_info(method='get_dhpcs', limit=limit)


def get_psusas(
    limit: int = 100
) -> Dict[str, Any]:
    """
    Get Periodic Safety Update Single Assessments

    PSUSAs are regular safety reviews of authorized medicines.

    Args:
        limit: Maximum results (default: 100)

    Returns:
        dict: PSUSA safety assessment data

    Examples:
        # Recent PSUSAs
        results = get_psusas(limit=50)

        for psusa in results.get('data', []):
            substance = psusa.get('active_substance')
            outcome = psusa.get('outcome')
            print(f"{substance}: {outcome}")
    """
    return ema_info(method='get_psusas', limit=limit)


# =============================================================================
# Paediatric Plans
# =============================================================================

def get_pips(
    limit: int = 100
) -> Dict[str, Any]:
    """
    Get Paediatric Investigation Plans

    PIPs are required development plans for medicines for children.

    Args:
        limit: Maximum results (default: 100)

    Returns:
        dict: PIP data

    Examples:
        # Recent PIPs
        results = get_pips(limit=50)

        for pip in results.get('data', []):
            name = pip.get('medicine_name')
            status = pip.get('pip_status')
            print(f"{name}: {status}")
    """
    return ema_info(method='get_pips', limit=limit)


# =============================================================================
# Herbal Medicines
# =============================================================================

def get_herbal_medicines(
    limit: int = 100
) -> Dict[str, Any]:
    """
    Get herbal medicine assessments

    Args:
        limit: Maximum results (default: 100)

    Returns:
        dict: Herbal medicine data

    Examples:
        # Herbal assessments
        results = get_herbal_medicines(limit=50)

        for herbal in results.get('data', []):
            name = herbal.get('herbal_substance')
            use = herbal.get('therapeutic_use')
            print(f"{name}: {use}")
    """
    return ema_info(method='get_herbal_medicines', limit=limit)


# =============================================================================
# Article 58 (Non-EU Use)
# =============================================================================

def get_article58_medicines(
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get Article 58 medicines (approved for non-EU markets)

    Article 58 allows EMA to assess medicines for countries outside EU.

    Args:
        limit: Maximum results (default: 50)

    Returns:
        dict: Article 58 medicine data

    Examples:
        # Article 58 medicines
        results = get_article58_medicines()

        for med in results.get('data', []):
            name = med.get('medicine_name')
            indication = med.get('therapeutic_indication')
            print(f"{name}: {indication}")
    """
    return ema_info(method='get_article58_medicines', limit=limit)


# =============================================================================
# Document Search
# =============================================================================

def search_epar_documents(
    limit: int = 100
) -> Dict[str, Any]:
    """
    Search EPAR (European Public Assessment Report) documents

    EPARs contain detailed assessment information for approved medicines.

    Args:
        limit: Maximum results (default: 100)

    Returns:
        dict: EPAR document data

    Examples:
        # Recent EPARs
        results = search_epar_documents(limit=50)

        for doc in results.get('data', []):
            name = doc.get('medicine_name')
            doc_type = doc.get('document_type')
            print(f"{name}: {doc_type}")
    """
    return ema_info(method='search_epar_documents', limit=limit)


def search_all_documents(
    limit: int = 100
) -> Dict[str, Any]:
    """
    Search all EMA documents

    Args:
        limit: Maximum results (default: 100)

    Returns:
        dict: EMA document data

    Examples:
        # All recent documents
        results = search_all_documents(limit=50)
    """
    return ema_info(method='search_all_documents', limit=limit)


def search_non_epar_documents(
    limit: int = 100
) -> Dict[str, Any]:
    """
    Search non-EPAR EMA documents

    Args:
        limit: Maximum results (default: 100)

    Returns:
        dict: Non-EPAR document data
    """
    return ema_info(method='search_non_epar_documents', limit=limit)


__all__ = [
    'ema_info',
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
    'search_non_epar_documents'
]
