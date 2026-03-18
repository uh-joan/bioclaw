"""Medicare MCP Server - Python API

Provides Python functions for Medicare data: provider services, Part D prescribers,
hospital data, spending information, hospital quality metrics, and ASP pricing.
Data stays in execution environment - only summaries flow to model.

CRITICAL MEDICARE MCP QUIRKS:
1. Dataset types: geography_and_service, provider_and_service, provider
2. Hospital IDs: CMS Certification Number (CCN) format (e.g., "050146")
3. Year parameter: 2013-latest (defaults to latest)
4. HCPCS codes: Must match exactly (e.g., '99213', '27447')
5. ASP quarters: Format "2025Q1", "2024Q4"
6. Quality metrics: Star ratings 1-5, readmission rates as percentages
7. Response size: max 5000 records per query (use pagination)
8. NPI format: 10-digit National Provider Identifier
"""

from mcp.client import get_client
from typing import Dict, Any, Optional, List


def medicare_info(
    method: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Unified Medicare data access function

    Args:
        method: Operation to perform
        **kwargs: Method-specific parameters

    Returns:
        dict: Medicare API response
    """
    client = get_client('medicare')

    params = {'method': method}
    params.update(kwargs)

    return client.call_tool('medicare_info', params)


# =============================================================================
# Provider Services (CMS Medicare Physician Data)
# =============================================================================

def search_providers(
    dataset_type: str,
    year: Optional[str] = None,
    hcpcs_code: Optional[str] = None,
    provider_type: Optional[str] = None,
    geo_level: Optional[str] = None,
    geo_code: Optional[str] = None,
    place_of_service: Optional[str] = None,
    size: int = 10,
    offset: int = 0,
    sort_by: Optional[str] = None,
    sort_order: str = "desc"
) -> Dict[str, Any]:
    """
    Search Medicare Physician & Other Practitioners data

    Args:
        dataset_type: Type of dataset (REQUIRED)
                     - "geography_and_service": Geographic analysis (regions, per-capita rates)
                     - "provider_and_service": Provider-level procedure tracking
                     - "provider": Provider demographics and beneficiary characteristics

        year: Year of dataset (2013-latest, default: latest)

        hcpcs_code: HCPCS procedure code
                   Examples: "99213" (office visit), "27447" (knee replacement)

        provider_type: Specialty type
                      Examples: "Cardiology", "Family Practice", "Internal Medicine"

        geo_level: Geographic level - "National", "State", "County", "ZIP"

        geo_code: Geographic code (e.g., "CA" for state, "06037" for county)

        place_of_service: Service location - "F" (Facility), "O" (Office), "H" (Hospital)

        size: Results per page (1-5000, default: 10)

        offset: Starting position (default: 0)

        sort_by: Sort field - "Tot_Srvcs", "Tot_Benes", "Tot_Mdcr_Pymt_Amt"

        sort_order: "asc" or "desc" (default: "desc")

    Returns:
        dict: Provider data matching criteria

    Examples:
        # Geographic analysis - office visits in California
        results = search_providers(
            dataset_type="geography_and_service",
            geo_level="State",
            geo_code="CA",
            hcpcs_code="99213",
            year="2023"
        )

        # Top knee surgeons in California
        results = search_providers(
            dataset_type="provider_and_service",
            geo_level="State",
            geo_code="CA",
            hcpcs_code="27447",
            sort_by="Tot_Srvcs",
            sort_order="desc",
            size=20
        )

        # Provider demographics
        results = search_providers(
            dataset_type="provider",
            provider_type="Cardiology",
            geo_level="State",
            geo_code="TX",
            size=50
        )
    """
    params = {
        'dataset_type': dataset_type,
        'size': size,
        'offset': offset,
        'sort_order': sort_order
    }

    if year:
        params['year'] = year
    if hcpcs_code:
        params['hcpcs_code'] = hcpcs_code
    if provider_type:
        params['provider_type'] = provider_type
    if geo_level:
        params['geo_level'] = geo_level
    if geo_code:
        params['geo_code'] = geo_code
    if place_of_service:
        params['place_of_service'] = place_of_service
    if sort_by:
        params['sort_by'] = sort_by

    return medicare_info(method='search_providers', **params)


# =============================================================================
# Part D Prescribers
# =============================================================================

def search_prescribers(
    drug_name: Optional[str] = None,
    prescriber_npi: Optional[str] = None,
    prescriber_type: Optional[str] = None,
    state: Optional[str] = None,
    size: int = 25,
    offset: int = 0,
    include_demographics: bool = False
) -> Dict[str, Any]:
    """
    Search Part D prescriber data

    Args:
        drug_name: Drug name to search (brand or generic)
                  Examples: "semaglutide", "Ozempic", "metformin"
                  Note: Not available when include_demographics=True

        prescriber_npi: National Provider Identifier (10-digit)

        prescriber_type: Prescriber specialty
                        Examples: "Endocrinology", "Family Practice", "Internal Medicine"

        state: State abbreviation (e.g., "CA", "TX", "NY")

        size: Results per page (default: 25, max: 5000)

        offset: Starting position (default: 0)

        include_demographics: Include patient demographic breakdowns (age, gender,
                             race, dual-eligible status). When True, uses provider-level
                             aggregated data which doesn't support drug_name filtering.
                             Default: False

    Returns:
        dict: Part D prescriber data with optional demographics
              When include_demographics=True, includes:
              - bene_age_lt_65_cnt, bene_age_65_74_cnt, bene_age_75_84_cnt, bene_age_gt_84_cnt
              - bene_feml_cnt, bene_male_cnt
              - bene_dual_cnt, bene_ndual_cnt
              - bene_race_* fields
              - bene_avg_age, bene_avg_risk_scre

    Examples:
        # Find top semaglutide prescribers (no demographics)
        results = search_prescribers(
            drug_name="semaglutide",
            size=100
        )

        # Endocrinologists in California with demographics
        results = search_prescribers(
            prescriber_type="Endocrinology",
            state="CA",
            size=50,
            include_demographics=True
        )

        # Specific prescriber by NPI with demographics
        results = search_prescribers(
            prescriber_npi="1234567890",
            include_demographics=True
        )
    """
    params = {
        'size': size,
        'offset': offset
    }

    if drug_name:
        params['drug_name'] = drug_name
    if prescriber_npi:
        params['prescriber_npi'] = prescriber_npi
    if prescriber_type:
        params['prescriber_type'] = prescriber_type
    if state:
        params['state'] = state
    if include_demographics:
        params['include_demographics'] = include_demographics

    return medicare_info(method='search_prescribers', **params)


# =============================================================================
# Hospital Data
# =============================================================================

def search_hospitals(
    hospital_id: Optional[str] = None,
    hospital_name: Optional[str] = None,
    state: Optional[str] = None,
    drg_code: Optional[str] = None,
    size: int = 25,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Search hospital utilization data

    Args:
        hospital_id: CMS Certification Number (CCN) - e.g., "050146"

        hospital_name: Hospital name (partial match supported)

        state: State abbreviation (e.g., "CA", "TX")

        drg_code: Diagnosis Related Group code for inpatient

        size: Results per page (default: 25)

        offset: Starting position (default: 0)

    Returns:
        dict: Hospital utilization data

    Examples:
        # Search hospitals in California
        results = search_hospitals(
            state="CA",
            size=50
        )

        # Search by hospital name
        results = search_hospitals(
            hospital_name="Mayo Clinic"
        )

        # Specific hospital by ID
        results = search_hospitals(
            hospital_id="050146"
        )
    """
    params = {
        'size': size,
        'offset': offset
    }

    if hospital_id:
        params['hospital_id'] = hospital_id
    if hospital_name:
        params['hospital_name'] = hospital_name
    if state:
        params['state'] = state
    if drg_code:
        params['drg_code'] = drg_code

    return medicare_info(method='search_hospitals', **params)


# =============================================================================
# Drug Spending
# =============================================================================

def search_spending(
    spending_drug_name: Optional[str] = None,
    spending_type: str = "part_d",
    size: int = 25,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Search drug/service spending data

    Args:
        spending_drug_name: Drug name for spending analysis

        spending_type: Type of spending data
                      - "part_d": Prescription drugs (default)
                      - "part_b": Administered drugs

        size: Results per page (default: 25)

        offset: Starting position (default: 0)

    Returns:
        dict: Drug spending data

    Examples:
        # Part D drug spending
        results = search_spending(
            spending_drug_name="semaglutide",
            spending_type="part_d"
        )

        # Part B drug spending
        results = search_spending(
            spending_drug_name="bevacizumab",
            spending_type="part_b"
        )
    """
    params = {
        'spending_type': spending_type,
        'size': size,
        'offset': offset
    }

    if spending_drug_name:
        params['spending_drug_name'] = spending_drug_name

    return medicare_info(method='search_spending', **params)


# =============================================================================
# Part D Formulary
# =============================================================================

def search_formulary(
    formulary_drug_name: Optional[str] = None,
    ndc_code: Optional[str] = None,
    plan_id: Optional[str] = None,
    plan_state: Optional[str] = None,
    tier: Optional[int] = None,
    requires_prior_auth: Optional[bool] = None,
    has_step_therapy: Optional[bool] = None,
    has_quantity_limit: Optional[bool] = None,
    size: int = 25,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Search Part D formulary coverage

    Args:
        formulary_drug_name: Drug name (partial match, e.g., "metformin", "insulin")

        ndc_code: National Drug Code for exact match (e.g., "00002143380")

        plan_id: Medicare Part D plan ID

        plan_state: State abbreviation for plan filter

        tier: Tier number (1=Preferred Generic, 2=Generic, 3=Preferred Brand,
              4=Non-Preferred Brand, 5=Specialty, 6=Select Care)

        requires_prior_auth: Filter by prior authorization requirement

        has_step_therapy: Filter by step therapy requirement

        has_quantity_limit: Filter by quantity limit

        size: Results per page (default: 25, max: 5000)

        offset: Starting position (default: 0)

    Returns:
        dict: Formulary coverage data

    Examples:
        # Search for metformin coverage
        results = search_formulary(
            formulary_drug_name="metformin",
            plan_state="CA"
        )

        # Find drugs requiring prior auth
        results = search_formulary(
            formulary_drug_name="semaglutide",
            requires_prior_auth=True
        )

        # Tier 1 generics
        results = search_formulary(
            tier=1,
            plan_state="TX",
            size=100
        )
    """
    params = {
        'size': size,
        'offset': offset
    }

    if formulary_drug_name:
        params['formulary_drug_name'] = formulary_drug_name
    if ndc_code:
        params['ndc_code'] = ndc_code
    if plan_id:
        params['plan_id'] = plan_id
    if plan_state:
        params['plan_state'] = plan_state
    if tier is not None:
        params['tier'] = tier
    if requires_prior_auth is not None:
        params['requires_prior_auth'] = requires_prior_auth
    if has_step_therapy is not None:
        params['has_step_therapy'] = has_step_therapy
    if has_quantity_limit is not None:
        params['has_quantity_limit'] = has_quantity_limit

    return medicare_info(method='search_formulary', **params)


# =============================================================================
# Hospital Quality Metrics
# =============================================================================

def get_hospital_star_rating(
    quality_hospital_id: Optional[str] = None,
    quality_state: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get hospital overall quality star ratings (1-5)

    Args:
        quality_hospital_id: CMS Certification Number (CCN)

        quality_state: State abbreviation to filter hospitals

    Returns:
        dict: Hospital star ratings

    Examples:
        # Get star ratings for California hospitals
        results = get_hospital_star_rating(quality_state="CA")

        # Specific hospital
        results = get_hospital_star_rating(quality_hospital_id="050146")
    """
    params = {}

    if quality_hospital_id:
        params['quality_hospital_id'] = quality_hospital_id
    if quality_state:
        params['quality_state'] = quality_state

    return medicare_info(method='get_hospital_star_rating', **params)


def get_readmission_rates(
    quality_hospital_id: Optional[str] = None,
    quality_state: Optional[str] = None,
    condition: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get hospital 30-day readmission rates by condition

    Args:
        quality_hospital_id: CMS Certification Number (CCN)

        quality_state: State abbreviation to filter hospitals

        condition: Medical condition filter
                  Values: "heart_failure", "pneumonia", "heart_attack", "copd", "stroke"

    Returns:
        dict: Readmission rate data

    Examples:
        # Heart failure readmissions in Texas
        results = get_readmission_rates(
            quality_state="TX",
            condition="heart_failure"
        )

        # All readmission rates for specific hospital
        results = get_readmission_rates(
            quality_hospital_id="050146"
        )
    """
    params = {}

    if quality_hospital_id:
        params['quality_hospital_id'] = quality_hospital_id
    if quality_state:
        params['quality_state'] = quality_state
    if condition:
        params['condition'] = condition

    return medicare_info(method='get_readmission_rates', **params)


def get_hospital_infections(
    quality_hospital_id: Optional[str] = None,
    quality_state: Optional[str] = None,
    infection_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get hospital-acquired infections (HAI) data

    Args:
        quality_hospital_id: CMS Certification Number (CCN)

        quality_state: State abbreviation to filter hospitals

        infection_type: Type of infection
                       Values: "CLABSI", "CAUTI", "SSI", "CDIFF", "MRSA"

    Returns:
        dict: Hospital infection data

    Examples:
        # MRSA infections in California
        results = get_hospital_infections(
            quality_state="CA",
            infection_type="MRSA"
        )

        # All infection types for hospital
        results = get_hospital_infections(
            quality_hospital_id="050146"
        )
    """
    params = {}

    if quality_hospital_id:
        params['quality_hospital_id'] = quality_hospital_id
    if quality_state:
        params['quality_state'] = quality_state
    if infection_type:
        params['infection_type'] = infection_type

    return medicare_info(method='get_hospital_infections', **params)


def get_mortality_rates(
    quality_hospital_id: Optional[str] = None,
    quality_state: Optional[str] = None,
    condition: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get hospital 30-day mortality rates

    Args:
        quality_hospital_id: CMS Certification Number (CCN)

        quality_state: State abbreviation to filter hospitals

        condition: Medical condition filter
                  Values: "heart_failure", "pneumonia", "heart_attack", "copd", "stroke"

    Returns:
        dict: Mortality rate data

    Examples:
        # Heart attack mortality in New York
        results = get_mortality_rates(
            quality_state="NY",
            condition="heart_attack"
        )
    """
    params = {}

    if quality_hospital_id:
        params['quality_hospital_id'] = quality_hospital_id
    if quality_state:
        params['quality_state'] = quality_state
    if condition:
        params['condition'] = condition

    return medicare_info(method='get_mortality_rates', **params)


def search_hospitals_by_quality(
    min_star_rating: Optional[float] = None,
    quality_state: Optional[str] = None
) -> Dict[str, Any]:
    """
    Find hospitals by quality metrics

    Args:
        min_star_rating: Minimum star rating (1-5)

        quality_state: State abbreviation to filter hospitals

    Returns:
        dict: Hospitals meeting quality criteria

    Examples:
        # 5-star hospitals in California
        results = search_hospitals_by_quality(
            min_star_rating=5,
            quality_state="CA"
        )

        # 4+ star hospitals nationwide
        results = search_hospitals_by_quality(
            min_star_rating=4
        )
    """
    params = {}

    if min_star_rating is not None:
        params['min_star_rating'] = min_star_rating
    if quality_state:
        params['quality_state'] = quality_state

    return medicare_info(method='search_hospitals_by_quality', **params)


def compare_hospitals(
    hospital_ids: List[str],
    metrics: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Compare quality metrics across hospitals

    Args:
        hospital_ids: Array of hospital CCN IDs to compare

        metrics: Array of metrics to compare
                Values: "star_rating", "readmission_rate", "mortality_rate", "infection_rate"

    Returns:
        dict: Comparison of hospital quality metrics

    Examples:
        # Compare three hospitals
        results = compare_hospitals(
            hospital_ids=["050146", "050001", "050002"],
            metrics=["star_rating", "readmission_rate"]
        )
    """
    params = {
        'hospital_ids': hospital_ids
    }

    if metrics:
        params['metrics'] = metrics

    return medicare_info(method='compare_hospitals', **params)


# =============================================================================
# ASP Pricing (Average Sales Price)
# =============================================================================

def get_asp_pricing(
    hcpcs_code_asp: str,
    quarter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get Medicare Part B ASP (Average Sales Price) pricing data

    Args:
        hcpcs_code_asp: HCPCS code for Part B drug
                       Examples: "J9035" (Bevacizumab), "J2353" (Octreotide)

        quarter: Quarter for ASP data
                Format: "2025Q1", "2024Q4"
                Default: latest available

    Returns:
        dict: ASP pricing data

    Examples:
        # Current ASP for bevacizumab
        results = get_asp_pricing(
            hcpcs_code_asp="J9035"
        )

        # Historical quarter
        results = get_asp_pricing(
            hcpcs_code_asp="J9035",
            quarter="2024Q4"
        )
    """
    params = {
        'hcpcs_code_asp': hcpcs_code_asp
    }

    if quarter:
        params['quarter'] = quarter

    return medicare_info(method='get_asp_pricing', **params)


def get_asp_trend(
    hcpcs_code_asp: str,
    start_quarter: str,
    end_quarter: str
) -> Dict[str, Any]:
    """
    Get ASP pricing trends over time

    Args:
        hcpcs_code_asp: HCPCS code for Part B drug

        start_quarter: Starting quarter (e.g., "2023Q1")

        end_quarter: Ending quarter (e.g., "2025Q1")

    Returns:
        dict: ASP trend data over time period

    Examples:
        # 2-year trend for bevacizumab
        results = get_asp_trend(
            hcpcs_code_asp="J9035",
            start_quarter="2023Q1",
            end_quarter="2025Q1"
        )
    """
    params = {
        'hcpcs_code_asp': hcpcs_code_asp,
        'start_quarter': start_quarter,
        'end_quarter': end_quarter
    }

    return medicare_info(method='get_asp_trend', **params)


def compare_asp_pricing(
    hcpcs_codes: List[str],
    quarter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Compare ASP pricing across drugs

    Args:
        hcpcs_codes: Array of HCPCS codes to compare

        quarter: Quarter for comparison (default: latest)

    Returns:
        dict: Comparison of ASP pricing

    Examples:
        # Compare biosimilars
        results = compare_asp_pricing(
            hcpcs_codes=["J9035", "Q5107", "Q5118"],
            quarter="2025Q1"
        )
    """
    params = {
        'hcpcs_codes': hcpcs_codes
    }

    if quarter:
        params['quarter'] = quarter

    return medicare_info(method='compare_asp_pricing', **params)


__all__ = [
    'medicare_info',
    'search_providers',
    'search_prescribers',
    'search_hospitals',
    'search_spending',
    'search_formulary',
    'get_hospital_star_rating',
    'get_readmission_rates',
    'get_hospital_infections',
    'get_mortality_rates',
    'search_hospitals_by_quality',
    'compare_hospitals',
    'get_asp_pricing',
    'get_asp_trend',
    'compare_asp_pricing'
]
