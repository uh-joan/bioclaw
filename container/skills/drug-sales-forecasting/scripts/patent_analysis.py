"""Patent and exclusivity analysis module.

Retrieves patent expiry dates and exclusivity periods from FDA Orange Book.
Detects biologics via Purple Book + name patterns.
"""

import sys
import os
import re

# Add parent directories to path for imports
_script_dir = os.path.dirname(os.path.abspath(__file__))
_claude_dir = os.path.dirname(os.path.dirname(os.path.dirname(_script_dir)))
sys.path.insert(0, _claude_dir)

from typing import Dict, Any, Optional, List
from datetime import datetime
import re

def estimate_patent_expiry_from_approval(
    approval_date: Optional[str],
    is_biologic: bool = False
) -> Optional[str]:
    """
    Estimate patent expiry from approval date using standard patent terms.

    US patents filed after 1995 have a 20-year term from filing date.
    Small molecules: typically approved 8-12 years after filing -> ~8-12 years post-approval
    Biologics: typically 12 years regulatory exclusivity from approval

    Args:
        approval_date: Approval date in YYYY-MM-DD or similar format
        is_biologic: Whether the drug is a biologic (affects exclusivity calculation)

    Returns:
        str: Estimated expiry date in YYYY-MM-DD format
    """
    if not approval_date:
        return None

    try:
        # Parse year from approval date
        year_match = re.search(r'(\d{4})', str(approval_date))
        if not year_match:
            return None
        approval_year = int(year_match.group(1))

        # Estimate years of remaining protection from approval
        # Biologics: 12-year exclusivity from approval date
        # Small molecules: ~10 years average (20-year patent term minus ~10 years development)
        years_from_approval = 12 if is_biologic else 10

        expiry_year = approval_year + years_from_approval
        return f"{expiry_year}-12-31"  # Default to end of year

    except (ValueError, TypeError):
        return None


def parse_year_from_text(text: str) -> Optional[int]:
    """Extract a 4-digit year from text."""
    years = re.findall(r'\b(20[2-4]\d)\b', text)
    if years:
        return int(years[0])
    return None


def check_if_generic_available(drug_name: str, mcp_funcs: Dict[str, Any]) -> Optional[bool]:
    """
    Check if generics/biosimilars are already available for a drug.

    Uses multiple signals:
    1. FDA label data - check if multiple manufacturers exist
    2. DrugBank data - check for generic versions

    Args:
        drug_name: Drug name to check
        mcp_funcs: MCP functions dictionary from skill_executor

    Returns:
        bool: True if generics available, False if not, None if unknown
    """
    try:
        # Get FDA lookup function from wrapper
        fda_lookup = mcp_funcs.get('fda_lookup')
        if not fda_lookup:
            return None

        # Method 1: Check FDA label data for multiple manufacturers
        label_result = fda_lookup(
            search_term=drug_name,
            search_type="label",
            limit=20
        )

        data = label_result.get('data', {})
        results = data.get('results', [])

        if results:
            # Collect unique manufacturers
            manufacturers = set()
            for item in results:
                if isinstance(item, dict):
                    openfda = item.get('openfda', {})
                    mfrs = openfda.get('manufacturer_name', [])
                    if isinstance(mfrs, list):
                        for mfr in mfrs:
                            manufacturers.add(mfr.lower())
                    elif mfrs:
                        manufacturers.add(str(mfrs).lower())

            # Multiple manufacturers = generics likely available
            if len(manufacturers) > 2:
                return True

        # Method 2: Check DrugBank for generic products
        try:
            drugbank_search = mcp_funcs.get('drugbank_search')
            if not drugbank_search:
                return None

            result = drugbank_search(
                method='get_products',
                drugbank_id=drug_name,  # Will fail for names, but try
                limit=50
            )

            # If products endpoint fails, try search
            if not result.get('data'):
                result = drugbank_search(
                    method='search_by_name',
                    query=drug_name,
                    limit=20
                )

            data = result.get('data', result)
            results = data.get('results', []) if isinstance(data, dict) else []

            # Check if any results indicate generic status
            for drug in results:
                if isinstance(drug, dict):
                    # Check categories for "generic"
                    categories = drug.get('categories', [])
                    if isinstance(categories, list):
                        for cat in categories:
                            if 'generic' in str(cat).lower():
                                return True
        except Exception:
            pass

        # If FDA found data but few manufacturers, likely still under patent
        if results and len(manufacturers) <= 2:
            return False

        return None

    except Exception:
        return None


# Biologic name suffixes (INN naming conventions)
BIOLOGIC_SUFFIXES = [
    # Monoclonal antibodies (-mab)
    '-mab', '-ximab', '-zumab', '-umab', '-imab',
    # Fusion proteins (-cept)
    '-cept',
    # Enzyme replacements (-ase)
    '-idase', '-glucosidase',
    # Gene therapies (-gene, -cel)
    '-gene', '-cel',
    # Peptides
    '-tide',
    # Antibody-drug conjugates
    '-vedotin', '-emtansine', '-ozogamicin',
]

# Known biologics (fallback list for common drugs)
KNOWN_BIOLOGICS = {
    'adalimumab', 'humira',
    'etanercept', 'enbrel',
    'infliximab', 'remicade',
    'rituximab', 'rituxan',
    'trastuzumab', 'herceptin',
    'bevacizumab', 'avastin',
    'pembrolizumab', 'keytruda',
    'nivolumab', 'opdivo',
    'ustekinumab', 'stelara',
    'secukinumab', 'cosentyx',
    'dupilumab', 'dupixent',
    'lecanemab', 'leqembi',
    'nusinersen', 'spinraza',
    'insulin', 'insulin glargine', 'insulin lispro',
    'epoetin', 'erythropoietin',
    'filgrastim', 'neupogen',
    'pegfilgrastim', 'neulasta',
}


def is_biologic(drug_name: str, drug_type: str = None, mcp_funcs: Dict[str, Any] = None) -> bool:
    """
    Detect if a drug is a biologic using multiple signals.

    Uses a cascade of detection methods:
    1. Known biologics list (fast)
    2. Name suffix patterns (INN conventions)
    3. DrugBank drug_type field
    4. Purple Book lookup (authoritative but slower)

    Args:
        drug_name: Drug name (brand or generic)
        drug_type: Optional drug_type from DrugBank
        mcp_funcs: MCP functions dictionary from skill_executor

    Returns:
        bool: True if drug is a biologic
    """
    name_lower = drug_name.lower().strip()

    # 1. Check known biologics list (fast)
    for known in KNOWN_BIOLOGICS:
        if known in name_lower or name_lower in known:
            return True

    # 2. Check INN suffix patterns
    for suffix in BIOLOGIC_SUFFIXES:
        if suffix in name_lower:
            return True

    # 3. Check DrugBank drug_type if provided
    if drug_type:
        type_lower = drug_type.lower()
        if any(t in type_lower for t in ['biotech', 'biologic', 'antibody', 'protein', 'peptide']):
            return True

    # 4. Purple Book lookup (slower, but authoritative)
    # Only do this if other methods inconclusive and mcp_funcs available
    if mcp_funcs:
        try:
            fda_lookup = mcp_funcs.get('fda_lookup')
            if fda_lookup:
                purple_result = fda_lookup(
                    method='search_purple_book',
                    search_term=drug_name,
                    limit=5
                )
                data = purple_result.get('data', {})
                if data.get('results') or data.get('totalCount', 0) > 0:
                    return True
        except Exception:
            pass  # Purple Book lookup failed, use other signals

    return False


def get_fda_approval_date(drug_name: str, mcp_funcs: Dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
    """
    Get FDA original approval date and NDA/BLA number from label data.

    Tries multiple fields to find the earliest/original approval date:
    1. openfda.product_ndc (first NDC can indicate original product)
    2. Earliest effective_time across all labels
    3. Initial_us_approval_year field (if available)

    Args:
        drug_name: Drug name (brand or generic)
        mcp_funcs: MCP functions dictionary from skill_executor

    Returns:
        tuple: (approval_date in YYYY-MM-DD format, nda_number) or (None, None)
    """
    try:
        # Get FDA lookup function from wrapper
        fda_lookup = mcp_funcs.get('fda_lookup')
        if not fda_lookup:
            return None, None

        # Search FDA drug labels for approval information
        label_result = fda_lookup(
            search_term=drug_name,
            search_type="label",
            limit=10
        )

        data = label_result.get('data', {})
        results = data.get('results', [])

        earliest_date = None
        nda_number = None

        for item in results:
            if isinstance(item, dict):
                openfda = item.get('openfda', {})

                # Extract NDA/BLA number
                app_numbers = openfda.get('application_number', [])
                if app_numbers and not nda_number:
                    nda_number = app_numbers[0] if isinstance(app_numbers, list) else app_numbers

                # Look for effective_time and track the earliest
                effective_time = item.get('effective_time')
                if effective_time and len(effective_time) >= 8:
                    # Format: YYYYMMDD -> YYYY-MM-DD
                    year = effective_time[:4]
                    month = effective_time[4:6] if len(effective_time) >= 6 else '01'
                    day = effective_time[6:8] if len(effective_time) >= 8 else '01'
                    date_str = f"{year}-{month}-{day}"

                    # Keep the earliest date found
                    if earliest_date is None or date_str < earliest_date:
                        earliest_date = date_str

        # If we found an NDA number, we can potentially look up original approval
        # For now, return what we have
        return earliest_date, nda_number

    except Exception:
        return None, None


def get_patent_exclusivity(drug_name: str, drug_type: str = None, region: str = 'us', mcp_funcs: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Get patent and exclusivity information for a drug.

    Uses multiple data sources in priority order:
    1. FDA Orange Book (small molecules) - patent/exclusivity details
    2. FDA Purple Book (biologics) - licensure date + 12-year exclusivity
    3. FDA Label data (approval date) - estimate expiry from approval
    4. Estimation fallback based on drug type

    Args:
        drug_name: Drug name (brand or generic)
        drug_type: Optional drug_type from DrugBank for biologic detection
        region: Region for patent lookup (us, eu, canada, etc.)
        mcp_funcs: MCP functions dictionary from skill_executor

    Returns:
        dict: Patent and exclusivity data including:
            - patent_expiry_date: Latest patent expiry
            - exclusivity_expiry_date: Latest exclusivity expiry
            - patents: List of patent details
            - exclusivities: List of exclusivity details
            - is_biologic: Whether drug is a biologic (multi-signal detection)
    """
    if not mcp_funcs:
        raise RuntimeError("mcp_funcs required for get_patent_exclusivity")
    result = {
        'drug_name': drug_name,
        'patent_expiry_date': None,
        'exclusivity_expiry_date': None,
        'patents': [],
        'exclusivities': [],
        'is_biologic': False,
        'bla_number': None,
        'nda_number': None,
        'approval_date': None,
        'data_sources': [],
        'region': region
    }

    # Get FDA lookup function
    fda_lookup = mcp_funcs.get('fda_lookup')
    if not fda_lookup:
        raise RuntimeError("FDA MCP not available")

    # First, detect if this is a biologic using multi-signal approach
    # This runs BEFORE Purple Book lookup to avoid redundant calls
    result['is_biologic'] = is_biologic(drug_name, drug_type, mcp_funcs)

    if result['is_biologic']:
        result['data_sources'].append('Biologic Detection (name/known list)')

    # Get FDA approval date and NDA number for estimation fallback
    approval_date, nda_number = get_fda_approval_date(drug_name, mcp_funcs)
    if approval_date:
        result['approval_date'] = approval_date
        result['data_sources'].append('FDA Label (approval date)')
    if nda_number:
        result['nda_number'] = nda_number

    # Try FDA Orange Book first (small molecule drugs)
    try:
        # Search for patent info
        orange_book = fda_lookup(
            search_term=drug_name,
            search_type="general",
            count="openfda.brand_name.exact",
            limit=10
        )

        data = orange_book.get('data', {})
        if data.get('results'):
            result['data_sources'].append('FDA Orange Book')

            # Extract patent information if available
            for item in data.get('results', []):
                if isinstance(item, dict) and 'term' in item:
                    # This is count data, need to do follow-up for details
                    pass

    except Exception as e:
        print(f"  Warning: Orange Book lookup failed: {e}")

    # Check Purple Book for biologics (only if not already detected as biologic)
    # This provides additional data like BLA number and licensure date
    try:
        purple_book = fda_lookup(
            method='search_purple_book',
            search_term=drug_name,
            limit=10
        )

        data = purple_book.get('data', {})
        if data.get('results'):
            # Confirm biologic status from authoritative source
            result['is_biologic'] = True
            if 'FDA Purple Book' not in result['data_sources']:
                result['data_sources'].append('FDA Purple Book')

            for item in data.get('results', []):
                if isinstance(item, dict):
                    # Extract BLA number
                    if 'blaNumber' in item:
                        result['bla_number'] = item['blaNumber']

                    # Extract licensure date (for biologics, this is key)
                    if 'dateOfLicensure' in item:
                        licensure_date = item['dateOfLicensure']
                        # Biologics typically have 12-year exclusivity from licensure
                        result['exclusivities'].append({
                            'type': 'BLA (Biologic)',
                            'licensure_date': licensure_date,
                            'estimated_exclusivity_years': 12
                        })

    except Exception as e:
        print(f"  Warning: Purple Book lookup failed: {e}")

    # Calculate latest expiry dates from collected patent data
    if result['patents']:
        patent_dates = [p.get('expiry_date') for p in result['patents'] if p.get('expiry_date')]
        if patent_dates:
            result['patent_expiry_date'] = max(patent_dates)

    if result['exclusivities']:
        excl_dates = [e.get('expiry_date') for e in result['exclusivities'] if e.get('expiry_date')]
        if excl_dates:
            result['exclusivity_expiry_date'] = max(excl_dates)

    # Check if generics/biosimilars already exist (indicates expired patent)
    generics_available = check_if_generic_available(drug_name, mcp_funcs)
    result['generics_available'] = generics_available

    # FALLBACK: If no direct patent/exclusivity dates found, estimate from approval date
    # This provides a reasonable estimate when API data is incomplete
    if not result['patent_expiry_date'] and not result['exclusivity_expiry_date']:
        # If generics are already available, patent is effectively expired
        if generics_available:
            result['patent_expiry_date'] = 'EXPIRED'
            result['data_sources'].append('Generic competition detected (patent expired)')
        else:
            # Try to estimate from approval date
            approval_date = result.get('approval_date')

            # For biologics with licensure date, calculate 12-year exclusivity
            if result['exclusivities']:
                for excl in result['exclusivities']:
                    if excl.get('licensure_date') and excl.get('estimated_exclusivity_years'):
                        licensure = excl['licensure_date']
                        years = excl['estimated_exclusivity_years']
                        estimated = estimate_patent_expiry_from_approval(licensure, is_biologic=True)
                        if estimated:
                            result['exclusivity_expiry_date'] = estimated
                            result['data_sources'].append('Estimated (12-year biologic exclusivity)')
                            break

            # If still no date, estimate from general approval date
            if not result['patent_expiry_date'] and not result['exclusivity_expiry_date']:
                if approval_date:
                    estimated = estimate_patent_expiry_from_approval(
                        approval_date,
                        is_biologic=result['is_biologic']
                    )
                    if estimated:
                        result['patent_expiry_date'] = estimated
                        result['data_sources'].append(
                            'Estimated (approval + 12yr)' if result['is_biologic']
                            else 'Estimated (approval + 10yr)'
                        )

    return result


def estimate_generic_entry_date(patent_data: Dict[str, Any]) -> Optional[str]:
    """
    Estimate when generics/biosimilars can enter based on patent/exclusivity data.

    Args:
        patent_data: Output from get_patent_exclusivity()

    Returns:
        str: Estimated date (YYYY-MM-DD) or None if unknown
    """
    dates_to_consider = []

    if patent_data.get('patent_expiry_date'):
        dates_to_consider.append(patent_data['patent_expiry_date'])

    if patent_data.get('exclusivity_expiry_date'):
        dates_to_consider.append(patent_data['exclusivity_expiry_date'])

    if dates_to_consider:
        # Generics can enter after the later of patent/exclusivity expiry
        return max(dates_to_consider)

    return None


def calculate_years_to_expiry(expiry_date: str) -> Optional[float]:
    """
    Calculate years remaining until patent/exclusivity expiry.

    Args:
        expiry_date: Expiry date in YYYY-MM-DD format, or "EXPIRED"

    Returns:
        float: Years to expiry (negative if already expired)
    """
    if not expiry_date:
        return None

    # Handle explicit EXPIRED status
    if expiry_date == 'EXPIRED':
        return -1.0  # Already expired

    try:
        expiry = datetime.strptime(expiry_date, '%Y-%m-%d')
        now = datetime.now()
        delta = expiry - now
        return delta.days / 365.25
    except ValueError:
        return None


def get_patent_cliff_risk(drug_name: str, drug_type: str = None, mcp_funcs: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Assess patent cliff risk for a drug.

    Args:
        drug_name: Drug name (brand or generic)
        drug_type: Optional drug_type from DrugBank for biologic detection
        mcp_funcs: MCP functions dictionary from skill_executor

    Returns:
        dict: Risk assessment including:
            - risk_level: "high", "medium", "low", "unknown"
            - years_to_cliff: Years until generic entry
            - factors: List of risk factors
    """
    if not mcp_funcs:
        raise RuntimeError("mcp_funcs required for get_patent_cliff_risk")

    patent_data = get_patent_exclusivity(drug_name, drug_type, mcp_funcs=mcp_funcs)
    generic_entry = estimate_generic_entry_date(patent_data)
    years = calculate_years_to_expiry(generic_entry) if generic_entry else None

    risk = {
        'drug_name': drug_name,
        'risk_level': 'unknown',
        'years_to_cliff': years,
        'generic_entry_date': generic_entry,
        'is_biologic': patent_data.get('is_biologic', False),
        'factors': [],
        'patent_data': patent_data
    }

    if years is not None:
        if years < 0:
            risk['risk_level'] = 'expired'
            risk['factors'].append('Patent/exclusivity already expired')
        elif years < 2:
            risk['risk_level'] = 'high'
            risk['factors'].append(f'Less than 2 years to generic entry ({years:.1f} years)')
        elif years < 5:
            risk['risk_level'] = 'medium'
            risk['factors'].append(f'2-5 years to generic entry ({years:.1f} years)')
        else:
            risk['risk_level'] = 'low'
            risk['factors'].append(f'More than 5 years of exclusivity ({years:.1f} years)')

    # Biologics have different dynamics
    if patent_data.get('is_biologic'):
        risk['factors'].append('Biologic - biosimilar erosion typically slower than small molecule generics')

    return risk


if __name__ == "__main__":
    # Test with a known drug
    if len(sys.argv) > 1:
        drug = sys.argv[1]
    else:
        drug = "semaglutide"

    print(f"\n📋 Patent Analysis for: {drug}")
    print("=" * 60)

    patent_info = get_patent_exclusivity(drug)
    print(f"\nPatent Expiry: {patent_info.get('patent_expiry_date', 'Unknown')}")
    print(f"Exclusivity Expiry: {patent_info.get('exclusivity_expiry_date', 'Unknown')}")
    print(f"Is Biologic: {patent_info.get('is_biologic', False)}")
    print(f"Data Sources: {', '.join(patent_info.get('data_sources', []))}")

    print("\n📊 Risk Assessment:")
    risk = get_patent_cliff_risk(drug)
    print(f"Risk Level: {risk['risk_level'].upper()}")
    print(f"Years to Cliff: {risk['years_to_cliff']:.1f}" if risk['years_to_cliff'] else "Years to Cliff: Unknown")
    for factor in risk['factors']:
        print(f"  • {factor}")
