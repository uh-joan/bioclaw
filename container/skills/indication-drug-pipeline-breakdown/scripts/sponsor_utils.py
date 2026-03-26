"""Sponsor/company attribution and classification utilities."""
import sys
import os

# Add script directory to path for local imports
_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _script_dir)

from constants import (
    COMPANY_HIERARCHY,
    MAJOR_PHARMA,
    GOVERNMENT_KEYWORDS,
    ACADEMIC_KEYWORDS,
    INDUSTRY_KEYWORDS,
)


def attribute_company(sponsor_name: str) -> str:
    """
    Map sponsor to parent company (handles M&A and name variations).

    Args:
        sponsor_name: Sponsor name from trial (e.g., "Celgene")

    Returns:
        Parent company name (e.g., "Bristol Myers Squibb")
    """
    # Direct match in hierarchy
    if sponsor_name in COMPANY_HIERARCHY:
        return COMPANY_HIERARCHY[sponsor_name]

    # Check for partial matches (handle "Inc", "Inc.", "Corporation", etc.)
    for acquired, parent in COMPANY_HIERARCHY.items():
        if acquired.lower() in sponsor_name.lower():
            return parent

    return sponsor_name


def classify_sponsor_type(sponsor_name: str) -> str:
    """
    Classify sponsor as Industry, Academic, or Government.

    Args:
        sponsor_name: Sponsor name from trial

    Returns:
        str: 'Industry', 'Academic', or 'Government'
    """
    if not sponsor_name:
        return 'Unknown'

    name_lower = sponsor_name.lower()

    # Check major pharma first (definitive industry)
    for pharma in MAJOR_PHARMA:
        if pharma in name_lower:
            return 'Industry'

    # Check government keywords
    for keyword in GOVERNMENT_KEYWORDS:
        if keyword in name_lower:
            return 'Government'

    # Check academic keywords
    for keyword in ACADEMIC_KEYWORDS:
        if keyword in name_lower:
            return 'Academic'

    # Check industry keywords
    for keyword in INDUSTRY_KEYWORDS:
        if keyword in name_lower:
            return 'Industry'

    # Default to Academic (conservative - most unknown sponsors are academic)
    return 'Academic'
