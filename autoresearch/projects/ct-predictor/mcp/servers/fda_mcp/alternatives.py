"""FDA MCP Alternative Methods

Provides working alternatives for broken FDA MCP methods.
These bypass the MCP and call FDA openFDA API directly with proper field selection.

USE THESE INSTEAD OF:
- Drug label queries without field selection (returns 110k tokens - exceeds 25k limit by 4.4x)
"""

import requests
from typing import Dict, Any, List, Optional


def get_drug_label_alternative(
    search_term: str,
    fields: Optional[List[str]] = None,
    limit: int = 1
) -> Dict[str, Any]:
    """
    Get FDA drug label data with field selection using openFDA API directly.

    This is a working alternative to the broken label query method.

    Args:
        search_term: Drug name or generic name to search
        fields: List of fields to return. If None, returns minimal essential fields.
                Default: ['openfda.brand_name', 'openfda.generic_name',
                         'indications_and_usage', 'warnings', 'dosage_and_administration']
        limit: Number of results to return (default: 1)

    Returns:
        dict with label information (manageable size)

    Token Usage: ~2,000-5,000 tokens (vs 110,000 from broken method)

    Available fields (select only what you need):
        Essential:
        - openfda.brand_name, openfda.generic_name, openfda.manufacturer_name
        - indications_and_usage, warnings, contraindications
        - dosage_and_administration, adverse_reactions

        Additional:
        - boxed_warning, warnings_and_cautions
        - drug_interactions, use_in_specific_populations
        - clinical_pharmacology, mechanism_of_action
        - description, clinical_studies
        - package_label_principal_display_panel
        - information_for_patients
        - pediatric_use, geriatric_use, pregnancy

    Examples:
        # Get essential label info only
        label = get_drug_label_alternative(search_term="aspirin")

        # Get specific sections
        label = get_drug_label_alternative(
            search_term="aspirin",
            fields=['indications_and_usage', 'warnings', 'dosage_and_administration']
        )

        # Get comprehensive label (more tokens but still under limit)
        label = get_drug_label_alternative(
            search_term="aspirin",
            fields=['openfda.brand_name', 'openfda.generic_name',
                   'indications_and_usage', 'warnings', 'contraindications',
                   'adverse_reactions', 'drug_interactions', 'dosage_and_administration',
                   'clinical_pharmacology', 'boxed_warning']
        )
    """

    if fields is None:
        # Minimal essential fields
        fields = [
            'openfda.brand_name',
            'openfda.generic_name',
            'indications_and_usage',
            'warnings',
            'dosage_and_administration'
        ]

    # Build openFDA API URL
    base_url = "https://api.fda.gov/drug/label.json"

    # Format search query
    search_query = f'openfda.brand_name:"{search_term}" OR openfda.generic_name:"{search_term}"'

    # Build parameters
    params = {
        'search': search_query,
        'limit': limit
    }

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Extract only requested fields
        results = []
        for item in data.get('results', []):
            filtered_item = {}
            for field in fields:
                # Handle nested fields (e.g., openfda.brand_name)
                if '.' in field:
                    parts = field.split('.')
                    value = item
                    for part in parts:
                        value = value.get(part, {}) if isinstance(value, dict) else value
                    if value and value != {}:
                        # Create nested structure
                        current = filtered_item
                        for part in parts[:-1]:
                            if part not in current:
                                current[part] = {}
                            current = current[part]
                        current[parts[-1]] = value
                else:
                    # Top-level field
                    if field in item:
                        filtered_item[field] = item[field]

            results.append(filtered_item)

        return {
            'search_term': search_term,
            'total_results': data.get('meta', {}).get('results', {}).get('total', 0),
            'returned': len(results),
            'fields_requested': fields,
            'results': results,
            'source': 'openFDA API (direct)',
            'token_estimate': len(str(results)) // 4  # Rough estimate
        }

    except requests.exceptions.RequestException as e:
        return {
            'error': str(e),
            'search_term': search_term,
            'message': 'Failed to fetch drug label from openFDA API'
        }


def get_adverse_events_summary(
    drug_name: str,
    count_field: str = "patient.reaction.reactionmeddrapt.exact",
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get summarized adverse event data (count aggregation only).

    Ultra-efficient alternative when you only need adverse event counts.

    Args:
        drug_name: Drug name to search
        count_field: Field to count by (default: reaction terms)
        limit: Maximum results to return

    Returns:
        dict with top adverse events and counts

    Token Usage: ~200-500 tokens

    Count field options:
        - patient.reaction.reactionmeddrapt.exact (reactions)
        - patient.drug.medicinalproduct.exact (drugs)
        - serious (serious vs non-serious)
        - receivedate (by date)
        - occurcountry.exact (by country)
        - patient.patientsex (by sex)
        - patient.patientonsetage (by age)

    Example:
        # Get top reactions for aspirin
        events = get_adverse_events_summary(drug_name="aspirin")

        # Get serious event breakdown
        events = get_adverse_events_summary(
            drug_name="aspirin",
            count_field="serious"
        )
    """

    base_url = "https://api.fda.gov/drug/event.json"

    search_query = f'patient.drug.medicinalproduct:"{drug_name}"'

    params = {
        'search': search_query,
        'count': count_field,
        'limit': limit
    }

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        return {
            'drug_name': drug_name,
            'count_field': count_field,
            'results': data.get('results', []),
            'source': 'openFDA API (count aggregation)',
            'token_estimate': len(str(data.get('results', []))) // 4
        }

    except requests.exceptions.RequestException as e:
        return {
            'error': str(e),
            'drug_name': drug_name,
            'message': 'Failed to fetch adverse events from openFDA API'
        }


def get_label_sections_summary(search_term: str) -> Dict[str, Any]:
    """
    Get minimal drug label summary (< 1000 tokens).

    Returns only essential fields: brand name, generic name, indications, warnings.

    Args:
        search_term: Drug name to search

    Returns:
        dict with essential label information only

    Token Usage: ~500-1,000 tokens

    Example:
        # Just get essential label info
        summary = get_label_sections_summary(search_term="aspirin")
    """

    return get_drug_label_alternative(
        search_term=search_term,
        fields=[
            'openfda.brand_name',
            'openfda.generic_name',
            'indications_and_usage',
            'warnings'
        ],
        limit=1
    )


def search_drugs_by_indication(
    indication: str,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Find drugs approved for a specific indication.

    Args:
        indication: Medical condition or indication (e.g., "hypertension", "diabetes")
        limit: Maximum drugs to return

    Returns:
        dict with list of drugs and their basic info

    Token Usage: ~1,000-3,000 tokens

    Example:
        drugs = search_drugs_by_indication(indication="hypertension", limit=5)
    """

    base_url = "https://api.fda.gov/drug/label.json"

    search_query = f'indications_and_usage:"{indication}"'

    params = {
        'search': search_query,
        'limit': limit
    }

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Extract minimal info for each drug
        drugs = []
        for item in data.get('results', []):
            openfda = item.get('openfda', {})
            drugs.append({
                'brand_name': openfda.get('brand_name', ['Unknown'])[0] if openfda.get('brand_name') else 'Unknown',
                'generic_name': openfda.get('generic_name', ['Unknown'])[0] if openfda.get('generic_name') else 'Unknown',
                'manufacturer': openfda.get('manufacturer_name', ['Unknown'])[0] if openfda.get('manufacturer_name') else 'Unknown',
                'indications_snippet': (item.get('indications_and_usage', [''])[0][:200] + '...') if item.get('indications_and_usage') else ''
            })

        return {
            'indication': indication,
            'total_found': data.get('meta', {}).get('results', {}).get('total', 0),
            'returned': len(drugs),
            'drugs': drugs,
            'source': 'openFDA API (direct)',
            'token_estimate': len(str(drugs)) // 4
        }

    except requests.exceptions.RequestException as e:
        return {
            'error': str(e),
            'indication': indication,
            'message': 'Failed to search drugs by indication from openFDA API'
        }


# Export all alternative functions
__all__ = [
    'get_drug_label_alternative',
    'get_adverse_events_summary',
    'get_label_sections_summary',
    'search_drugs_by_indication'
]
