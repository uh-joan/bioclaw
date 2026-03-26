"""Company name resolution and normalization utilities.

Handles company name variations via COMPANY_ALIASES reverse-index,
and discovers CT.gov sponsor name variations via the suggest API.
Known M&A relationships are maintained in KNOWN_SUBSIDIARIES (lightweight map).
"""

import re
from typing import List, Dict, Optional

# Add script directory to path for local imports
import sys
import os
_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _script_dir)

from constants import (
    COMPANY_ALIASES,
    KNOWN_SUBSIDIARIES,
    MAJOR_PHARMA,
    MAJOR_MEDTECH,
    INDUSTRY_KEYWORDS,
    ACADEMIC_KEYWORDS,
    GOVERNMENT_KEYWORDS,
)

# =============================================================================
# Build reverse alias index at module load time (O(1) lookups)
# =============================================================================
# Maps any known alias (lowercased) → canonical company name.
# Example: 'bms' → 'Bristol Myers Squibb', 'lilly' → 'Eli Lilly'
_ALIAS_REVERSE = {}
for _canonical, _aliases in COMPANY_ALIASES.items():
    for _alias in _aliases:
        _ALIAS_REVERSE[_alias.lower()] = _canonical


def normalize_company_name(company_input: str) -> str:
    """
    Normalize a company name to its canonical form.

    Uses a two-step approach:
    1. Reverse-lookup in COMPANY_ALIASES (handles abbreviations, former names)
    2. Legal suffix stripping + re-lookup (handles "Pfizer Inc." → "Pfizer")

    Args:
        company_input: User input company name (e.g., "Lilly", "BMS", "Pfizer Inc.")

    Returns:
        Normalized company name (e.g., "Eli Lilly", "Bristol Myers Squibb", "Pfizer")
    """
    if not company_input:
        return ""

    name = company_input.strip()
    name_lower = name.lower()

    # Step 1: Direct reverse-alias lookup (catches BMS, Lilly, MSD, etc.)
    if name_lower in _ALIAS_REVERSE:
        return _ALIAS_REVERSE[name_lower]

    # Step 2: Strip legal suffixes and try again
    stripped = _strip_legal_suffixes(name)
    stripped_lower = stripped.lower()
    if stripped_lower != name_lower and stripped_lower in _ALIAS_REVERSE:
        return _ALIAS_REVERSE[stripped_lower]

    # Step 3: Return stripped name (best effort)
    return stripped if stripped else name


def _strip_legal_suffixes(name: str) -> str:
    """Remove common legal suffixes from company names."""
    suffixes = [
        r',?\s+Inc\.?$',
        r',?\s+Corp\.?$',
        r',?\s+Corporation$',
        r',?\s+Ltd\.?$',
        r',?\s+Limited$',
        r',?\s+LLC$',
        r',?\s+L\.L\.C\.$',
        r',?\s+PLC$',
        r',?\s+plc$',
        r',?\s+AG$',
        r',?\s+GmbH$',
        r',?\s+S\.A\.$',
        r',?\s+SE$',
        r',?\s+A/S$',
        r',?\s+Co\.$',
        r',?\s+& Co\.$',
        r',?\s+and Company$',
    ]

    result = name
    for pattern in suffixes:
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)

    return result.strip()


def get_all_company_names(company_input: str) -> List[str]:
    """
    Get all known name variations for a company from COMPANY_ALIASES.

    Args:
        company_input: User input company name

    Returns:
        List of company name variations to search for
    """
    names = set()

    normalized = normalize_company_name(company_input)
    names.add(normalized)

    # Add all known aliases for the canonical name
    if normalized in COMPANY_ALIASES:
        names.update(COMPANY_ALIASES[normalized])

    # Add original input if different
    if company_input != normalized:
        names.add(company_input)

    return list(names)


def get_subsidiary_companies(company_name: str) -> List[str]:
    """
    Get known subsidiary/acquired companies from KNOWN_SUBSIDIARIES.

    Only includes subsidiaries whose CT.gov sponsor name differs significantly
    from the parent (e.g., Genentech for Roche, Allergan for AbbVie).

    Args:
        company_name: Normalized parent company name

    Returns:
        List of subsidiary company names
    """
    normalized = normalize_company_name(company_name)
    return KNOWN_SUBSIDIARIES.get(normalized, [])


def discover_sponsor_names_from_ctgov(company_name: str, ct_search=None) -> List[str]:
    """
    Dynamically discover company sponsor name variations from CT.gov suggest API.

    Queries CT.gov's autocomplete for actual sponsor names in their database.

    Args:
        company_name: Company name to search for (e.g., "Abbott", "Medtronic")
        ct_search: CT.gov search function (injected)

    Returns:
        List of actual sponsor names found in CT.gov
    """
    if not ct_search:
        return [company_name]

    try:
        result = ct_search(
            method="suggest",
            dictionary="LeadSponsorName",
            input=company_name
        )

        result_text = result if isinstance(result, str) else result.get('text', str(result))

        suggestions = re.findall(r'\d+\.\s+\*\*([^*]+)\*\*', result_text)

        return suggestions if suggestions else [company_name]

    except Exception as e:
        print(f"Warning: CT.gov suggest API failed: {e}")
        return [company_name]


def resolve_company_names(
    company_input: str,
    include_subsidiaries: bool = True,
    use_ctgov_discovery: bool = True,
    ct_search=None,
) -> Dict:
    """
    Comprehensive company name resolution.

    Two-layer approach:
    1. COMPANY_ALIASES — abbreviations/former names (BMS → Bristol Myers Squibb)
    2. CT.gov suggest API — legal name variations (Pfizer → Pfizer Inc., Pfizer Ltd.)

    Plus known M&A subsidiaries from KNOWN_SUBSIDIARIES (lightweight, curated map).

    Args:
        company_input: User input (e.g., "Lilly", "BMS", "Pfizer")
        include_subsidiaries: Whether to include known acquired companies
        use_ctgov_discovery: Whether to use CT.gov APIs for discovery
        ct_search: CT.gov search function (injected)

    Returns:
        Dict with normalized name, search names, subsidiaries, etc.
    """
    normalized = normalize_company_name(company_input)

    # Layer 1: Known aliases (abbreviations, former names)
    search_names = get_all_company_names(company_input)

    # Layer 2: CT.gov suggest API for legal name variations
    discovered_names = []
    if use_ctgov_discovery and ct_search:
        discovered_names = discover_sponsor_names_from_ctgov(normalized, ct_search=ct_search)
        for name in discovered_names:
            if name not in search_names:
                search_names.append(name)

    # Known subsidiaries from curated M&A map
    subsidiaries = []
    if include_subsidiaries:
        subsidiaries = get_subsidiary_companies(normalized)

        # Also discover CT.gov name variations for each subsidiary
        for sub in subsidiaries:
            if sub not in search_names:
                search_names.append(sub)
            # Add aliases for the subsidiary too
            sub_aliases = get_all_company_names(sub)
            for alias in sub_aliases:
                if alias not in search_names:
                    search_names.append(alias)
            if use_ctgov_discovery and ct_search:
                sub_variations = discover_sponsor_names_from_ctgov(sub, ct_search=ct_search)
                for v in sub_variations:
                    if v not in search_names:
                        search_names.append(v)

    aliases = COMPANY_ALIASES.get(normalized, [normalized])

    return {
        'normalized': normalized,
        'search_names': search_names,
        'discovered_names': discovered_names,
        'subsidiaries': subsidiaries,
        'subsidiary_evidence': {},
        'aliases': aliases,
        'original_input': company_input,
    }


def attribute_company(sponsor_name: str, dynamic_hierarchy: dict = None) -> str:
    """
    Map a sponsor name from CT.gov to its parent company.

    Uses known subsidiaries and alias lookups.

    Args:
        sponsor_name: Sponsor name from trial (e.g., "Celgene Corporation")
        dynamic_hierarchy: Optional mapping of subsidiary → parent

    Returns:
        Parent company name (e.g., "Bristol Myers Squibb")
    """
    if not sponsor_name:
        return "Unknown"

    # Check dynamic hierarchy first
    if dynamic_hierarchy:
        if sponsor_name in dynamic_hierarchy:
            return dynamic_hierarchy[sponsor_name]

        # Case-insensitive + suffix-stripped lookup
        stripped = _strip_legal_suffixes(sponsor_name)
        for key, parent in dynamic_hierarchy.items():
            if key.lower() == stripped.lower() or key.lower() == sponsor_name.lower():
                return parent

    # Fall back to alias-based normalization
    normalized = normalize_company_name(sponsor_name)
    return normalized


def _keyword_match(keyword: str, text: str) -> bool:
    """Match keyword in text, using word boundaries for short keywords (<=4 chars)."""
    if len(keyword) <= 4:
        return bool(re.search(r'\b' + re.escape(keyword) + r'\b', text))
    return keyword in text


def classify_sponsor_type(sponsor_name: str) -> str:
    """
    Classify a sponsor as Industry, Academic, Government, or Unknown.

    Args:
        sponsor_name: Sponsor name from trial

    Returns:
        Classification string
    """
    if not sponsor_name:
        return 'Unknown'

    name_lower = sponsor_name.lower()

    # Check government keywords FIRST (before pharma — prevents "national center"
    # from matching pharma keywords like short abbreviations)
    for keyword in GOVERNMENT_KEYWORDS:
        if _keyword_match(keyword, name_lower):
            return 'Government'

    # Check academic keywords (before pharma — prevents "cancer center"
    # entities from matching pharma keywords)
    for keyword in ACADEMIC_KEYWORDS:
        if _keyword_match(keyword, name_lower):
            return 'Academic'

    # Check major pharma (definitive industry)
    for pharma in MAJOR_PHARMA:
        if _keyword_match(pharma, name_lower):
            return 'Industry'

    # Check industry keywords
    for keyword in INDUSTRY_KEYWORDS:
        if _keyword_match(keyword, name_lower):
            return 'Industry'

    # Default to Unknown (could be either)
    return 'Unknown'


def is_major_pharma(company_name: str) -> bool:
    """Check if a company is a major pharmaceutical company."""
    normalized = normalize_company_name(company_name)
    name_lower = normalized.lower()

    for pharma in MAJOR_PHARMA:
        if _keyword_match(pharma, name_lower):
            return True

    return False


def is_major_medtech(company_name: str) -> bool:
    """Check if a company is a major medical device/medtech company."""
    normalized = normalize_company_name(company_name)
    name_lower = normalized.lower()

    for medtech in MAJOR_MEDTECH:
        if _keyword_match(medtech, name_lower):
            return True

    return False


def get_company_type(company_name: str) -> str:
    """
    Get company type: 'Big Pharma', 'Medtech', 'Biotech', 'Academic', 'Government'.
    """
    if is_major_pharma(company_name):
        return 'Big Pharma'

    if is_major_medtech(company_name):
        return 'Medtech'

    sponsor_type = classify_sponsor_type(company_name)

    if sponsor_type == 'Industry':
        return 'Biotech'
    elif sponsor_type == 'Academic':
        return 'Academic'
    elif sponsor_type == 'Government':
        return 'Government'
    else:
        return 'Other'


if __name__ == "__main__":
    # Test the resolution
    test_companies = [
        "Lilly",
        "Eli Lilly",
        "Eli Lilly and Company",
        "BMS",
        "Bristol Myers Squibb",
        "Bristol-Myers Squibb Company",
        "Pfizer Inc.",
        "Genentech",
        "Novo Nordisk",
        "AbbVie",
        "Gilead Sciences",
        "Merck & Co., Inc.",
        "MSD",
        "ModernaTX",
        "Sanofi-Aventis",
        "Biogen Idec",
    ]

    print("Company Resolution Test")
    print("=" * 80)

    for company in test_companies:
        normalized = normalize_company_name(company)
        print(f"  {company:<35} → {normalized}")

    # Test subsidiary lookup
    print("\nSubsidiary Lookup Test")
    print("=" * 80)
    for parent in ['Bristol Myers Squibb', 'Roche', 'AbbVie', 'Johnson & Johnson', 'Pfizer']:
        subs = get_subsidiary_companies(parent)
        print(f"  {parent:<30} → {subs if subs else '(none)'}")
