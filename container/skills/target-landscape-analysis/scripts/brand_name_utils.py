"""
Brand name lookup utilities for improving FDA/regulatory data quality.

Provides functions to:
- Resolve generic drug names to brand names
- Validate brand names against FDA labels
- Cache brand name lookups to avoid repeated API calls

NOTE: Adapted from drug-sales-forecasting skill's comparable_drugs.py
FDA databases work much better with brand names than generic INN names.
"""

from typing import List, Optional, Dict, Any
from collections import Counter

# Cache to avoid repeated API calls
_BRAND_NAME_CACHE: Dict[str, Optional[str]] = {}


def _get_all_brand_names_from_fda(fda_lookup_func, generic_name: str) -> List[str]:
    """
    Get ALL brand names for a drug from FDA labels.

    Args:
        fda_lookup_func: lookup_drug function from fda_mcp
        generic_name: Generic drug name (INN)

    Returns:
        List of brand names sorted by frequency (most common first)
    """
    brands = []
    seen = set()
    generic_lower = generic_name.lower().strip()

    try:
        # Search FDA labels by drug name
        fda_result = fda_lookup_func(
            method='lookup_drug',
            search_term=generic_name,
            search_type='label',
            limit=50  # Get enough labels to find all brand variants
        )

        if not fda_result:
            return []

        # Handle nested structure: data.results
        data = fda_result.get('data', {})
        results = data.get('results', [])

        if not results:
            return []

        for label in results:
            openfda = label.get('openfda', {})

            # CRITICAL: Verify generic_name matches before extracting brand
            generic_names = [g.lower() for g in openfda.get('generic_name', [])]
            if not any(generic_lower in g or g in generic_lower for g in generic_names):
                continue  # Skip - different drug

            # Extract brand names from this label
            brand_names = openfda.get('brand_name', [])
            for brand in brand_names:
                brand_clean = brand.strip()
                if brand_clean and brand_clean not in seen:
                    brands.append(brand_clean)
                    seen.add(brand_clean)

        # Count frequency and sort by most common
        brand_counter = Counter(brands)
        sorted_brands = [brand for brand, count in brand_counter.most_common()]

        return sorted_brands

    except Exception as e:
        print(f"Warning: Could not fetch FDA brand names for {generic_name}: {e}")
        return []


def get_brand_name(fda_lookup_func, generic_name: str, use_cache: bool = True) -> Optional[str]:
    """
    Get the primary brand name for a generic drug.

    Uses FDA labels as primary source. Returns the most common brand name
    (by label frequency) that matches the generic name.

    Args:
        fda_lookup_func: lookup_drug function from fda_mcp
        generic_name: Generic drug name (INN)
        use_cache: Use cached results if available

    Returns:
        Brand name or None if not found
    """
    if not generic_name:
        return None

    # Check cache
    cache_key = generic_name.lower().strip()
    if use_cache and cache_key in _BRAND_NAME_CACHE:
        return _BRAND_NAME_CACHE[cache_key]

    # Get all brand names from FDA
    brand_candidates = _get_all_brand_names_from_fda(fda_lookup_func, generic_name)

    # Pick the first one (most common by label count)
    best_brand = brand_candidates[0] if brand_candidates else None

    # Cache result
    _BRAND_NAME_CACHE[cache_key] = best_brand

    return best_brand


def get_brand_or_generic(fda_lookup_func, drug_name: str, use_cache: bool = True) -> str:
    """
    Try to resolve a drug name to its brand name, fall back to input if not found.

    This is a convenience function for regulatory lookups where brand names
    work better but we still want to try if brand lookup fails.

    Args:
        fda_lookup_func: lookup_drug function from fda_mcp
        drug_name: Drug name (generic or brand)
        use_cache: Use cached results

    Returns:
        Brand name if found, otherwise original drug_name
    """
    if not drug_name:
        return drug_name

    brand = get_brand_name(fda_lookup_func, drug_name, use_cache)
    return brand if brand else drug_name


def clear_brand_cache():
    """Clear the brand name cache."""
    global _BRAND_NAME_CACHE
    _BRAND_NAME_CACHE.clear()
