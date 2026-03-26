"""
Regulatory status utilities for FDA and EMA approval tracking.

Provides functions to:
- Check FDA approval status for drugs
- Check EMA approval status for drugs
- Aggregate regulatory timelines
- Classify drugs by regulatory status
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from brand_name_utils import get_brand_or_generic


def get_fda_approval_status(fda_lookup_func, drug_name: str) -> Dict[str, Any]:
    """
    Get FDA approval status for a drug.

    NOTE: Uses brand name lookup to improve data quality.
    FDA databases work much better with brand names than generic INN names.

    Args:
        fda_lookup_func: lookup_drug function from fda_mcp
        drug_name: Drug name to search

    Returns:
        dict with approval_status, approval_date, indications, warnings
    """
    try:
        # Try to resolve to brand name for better FDA results
        search_name = get_brand_or_generic(fda_lookup_func, drug_name)

        result = fda_lookup_func(
            method='lookup_drug',
            search_term=search_name,
            search_type='general',
            limit=5
        )

        if not result:
            return {
                'approved': False,
                'approval_date': None,
                'indications': [],
                'warnings': [],
                'source': 'FDA',
                'error': 'No response from FDA'
            }

        # Handle nested structure: data.results
        data = result.get('data', {})
        if not data or 'results' not in data:
            return {
                'approved': False,
                'approval_date': None,
                'indications': [],
                'warnings': [],
                'source': 'FDA',
                'error': 'Not found in FDA database'
            }

        # Get first result
        first_result = data['results'][0] if data['results'] else None
        if not first_result:
            return {
                'approved': False,
                'approval_date': None,
                'indications': [],
                'warnings': [],
                'source': 'FDA'
            }

        # Extract approval info
        openfda = first_result.get('openfda', {})

        # Get approval date from original submission
        approval_date = None
        submissions = first_result.get('submissions', [])
        for sub in submissions:
            if sub.get('submission_type') == 'ORIG':
                approval_date = sub.get('submission_status_date')
                break

        # Extract manufacturer and application number
        manufacturer = None
        application_number = first_result.get('application_number')

        # Try to get manufacturer from openfda first
        if openfda.get('manufacturer_name'):
            manufacturer = openfda.get('manufacturer_name')[0]
        elif first_result.get('sponsor_name'):
            manufacturer = first_result.get('sponsor_name')

        # If still no manufacturer or app number, try label search as fallback
        if (not manufacturer or not application_number) and not openfda.get('brand_name'):
            try:
                label_result = fda_lookup_func(
                    method='lookup_drug',
                    search_term=search_name,  # Use brand name if resolved
                    search_type='label',
                    limit=1
                )
                if label_result and 'data' in label_result:
                    label_data = label_result['data']
                    if 'results' in label_data and label_data['results']:
                        label_first = label_data['results'][0]
                        label_openfda = label_first.get('openfda', {})

                        # Update manufacturer if not found
                        if not manufacturer and label_openfda.get('manufacturer_name'):
                            manufacturer = label_openfda['manufacturer_name'][0]

                        # Update application number if not found
                        if not application_number and label_first.get('application_number'):
                            application_number = label_first.get('application_number')
            except:
                pass  # Fallback failed, continue with what we have

        return {
            'approved': True,
            'approval_date': approval_date,
            'brand_names': openfda.get('brand_name', []),
            'generic_names': openfda.get('generic_name', []),
            'application_number': application_number,
            'manufacturer': manufacturer if manufacturer else 'Unknown',
            'source': 'FDA'
        }

    except Exception as e:
        return {
            'approved': False,
            'approval_date': None,
            'indications': [],
            'warnings': [],
            'source': 'FDA',
            'error': str(e)
        }


def get_ema_approval_status(ema_search_func, drug_name: str) -> Dict[str, Any]:
    """
    Get EMA approval status for a drug.

    Args:
        ema_search_func: search_medicines function from ema_mcp
        drug_name: Drug name to search

    Returns:
        dict with approval_status, approval_date, indications, company
    """
    try:
        # EMA search
        result = ema_search_func(
            active_substance=drug_name,
            limit=5
        )

        if not result or 'results' not in result:
            return {
                'approved': False,
                'approval_date': None,
                'therapeutic_area': None,
                'company': None,
                'source': 'EMA',
                'error': 'Not found in EMA database'
            }

        # Get first result
        first_result = result['results'][0] if result['results'] else None
        if not first_result:
            return {
                'approved': False,
                'approval_date': None,
                'therapeutic_area': None,
                'company': None,
                'source': 'EMA'
            }

        # Extract approval info
        status = first_result.get('medicine_status', '')
        approved = 'authorised' in status.lower()

        return {
            'approved': approved,
            'approval_date': first_result.get('marketing_authorisation_date'),
            'status': status,
            'therapeutic_area': first_result.get('therapeutic_area_mesh', 'Not specified'),
            'company': first_result.get('marketing_authorisation_developer_applicant_holder', 'Unknown'),
            'active_substance': first_result.get('active_substance', drug_name),
            'product_name': first_result.get('name_of_medicine', drug_name),
            'source': 'EMA'
        }

    except Exception as e:
        return {
            'approved': False,
            'approval_date': None,
            'therapeutic_area': None,
            'company': None,
            'source': 'EMA',
            'error': str(e)
        }


def get_regulatory_status_batch(
    fda_lookup_func,
    ema_search_func,
    drugs: List[Dict],
    max_drugs: int = 1000,
    include_fda: bool = True,
    include_ema: bool = True
) -> Dict[str, Any]:
    """
    Get regulatory status for multiple drugs.

    Args:
        fda_lookup_func: FDA lookup function
        ema_search_func: EMA search function
        drugs: List of drug dicts with 'drug_name' field
        max_drugs: Maximum drugs to check
        include_fda: Check FDA status
        include_ema: Check EMA status

    Returns:
        dict with regulatory_data, summary statistics
    """
    regulatory_data = []

    for drug in drugs[:max_drugs]:
        drug_name = drug.get('drug_name', '')
        if not drug_name:
            continue

        drug_regulatory = {
            'drug_name': drug_name,
            'drugbank_id': drug.get('drugbank_id'),
            'fda_status': None,
            'ema_status': None
        }

        # Check FDA
        if include_fda:
            fda_status = get_fda_approval_status(fda_lookup_func, drug_name)
            drug_regulatory['fda_status'] = fda_status

        # Check EMA
        if include_ema:
            ema_status = get_ema_approval_status(ema_search_func, drug_name)
            drug_regulatory['ema_status'] = ema_status

        regulatory_data.append(drug_regulatory)

    # Calculate summary
    fda_approved = sum(1 for d in regulatory_data if d.get('fda_status', {}).get('approved', False))
    ema_approved = sum(1 for d in regulatory_data if d.get('ema_status', {}).get('approved', False))
    both_approved = sum(
        1 for d in regulatory_data
        if d.get('fda_status', {}).get('approved', False) and d.get('ema_status', {}).get('approved', False)
    )

    return {
        'regulatory_data': regulatory_data,
        'summary': {
            'total_drugs_checked': len(regulatory_data),
            'fda_approved': fda_approved,
            'ema_approved': ema_approved,
            'both_markets': both_approved,
            'us_only': fda_approved - both_approved,
            'eu_only': ema_approved - both_approved
        }
    }


def classify_by_regulatory_status(regulatory_batch: Dict) -> Dict[str, List[Dict]]:
    """
    Classify drugs by their regulatory approval status.

    Args:
        regulatory_batch: Output from get_regulatory_status_batch

    Returns:
        dict with categorized drugs: both_markets, us_only, eu_only, neither
    """
    both_markets = []
    us_only = []
    eu_only = []
    neither = []

    for drug_reg in regulatory_batch['regulatory_data']:
        fda_approved = drug_reg.get('fda_status', {}).get('approved', False)
        ema_approved = drug_reg.get('ema_status', {}).get('approved', False)

        if fda_approved and ema_approved:
            both_markets.append(drug_reg)
        elif fda_approved:
            us_only.append(drug_reg)
        elif ema_approved:
            eu_only.append(drug_reg)
        else:
            neither.append(drug_reg)

    return {
        'both_markets': both_markets,
        'us_only': us_only,
        'eu_only': eu_only,
        'neither': neither
    }


def get_regulatory_timeline(regulatory_batch: Dict) -> List[Dict[str, Any]]:
    """
    Create timeline of regulatory approvals.

    Args:
        regulatory_batch: Output from get_regulatory_status_batch

    Returns:
        List of approval events sorted by date
    """
    timeline = []

    for drug_reg in regulatory_batch['regulatory_data']:
        drug_name = drug_reg['drug_name']

        # FDA approval
        fda_status = drug_reg.get('fda_status', {})
        if fda_status.get('approved') and fda_status.get('approval_date'):
            timeline.append({
                'drug_name': drug_name,
                'region': 'US (FDA)',
                'approval_date': fda_status['approval_date'],
                'company': fda_status.get('manufacturer', 'Unknown')
            })

        # EMA approval
        ema_status = drug_reg.get('ema_status', {})
        if ema_status.get('approved') and ema_status.get('approval_date'):
            timeline.append({
                'drug_name': drug_name,
                'region': 'EU (EMA)',
                'approval_date': ema_status['approval_date'],
                'company': ema_status.get('company', 'Unknown')
            })

    # Sort by date (most recent first)
    timeline.sort(key=lambda x: x['approval_date'], reverse=True)

    return timeline
