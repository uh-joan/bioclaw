"""
Drug deduplication and data quality utilities.

Handles cross-tier drug matching and merging with data quality scoring.
"""

from typing import Dict, Any, List, Tuple
from difflib import SequenceMatcher


def normalize_drug_name(name: str) -> str:
    """
    Normalize drug name for matching.

    Args:
        name: Drug name

    Returns:
        Normalized name
    """
    if not name:
        return ""

    # Convert to lowercase
    normalized = name.lower().strip()

    # Remove common suffixes/prefixes
    prefixes_to_remove = ['recombinant', 'human', 'monoclonal', 'antibody']
    for prefix in prefixes_to_remove:
        if normalized.startswith(prefix + ' '):
            normalized = normalized[len(prefix) + 1:]

    # Remove parentheses content (e.g., "Drug (Company)" -> "Drug")
    import re
    normalized = re.sub(r'\([^)]*\)', '', normalized).strip()

    # Remove hyphens and spaces for fuzzy matching
    normalized = normalized.replace('-', '').replace(' ', '')

    return normalized


def calculate_name_similarity(name1: str, name2: str) -> float:
    """
    Calculate similarity between two drug names.

    Args:
        name1: First drug name
        name2: Second drug name

    Returns:
        Similarity score (0-1)
    """
    if not name1 or not name2:
        return 0.0

    # Exact match
    if name1.lower() == name2.lower():
        return 1.0

    # Normalize and compare
    norm1 = normalize_drug_name(name1)
    norm2 = normalize_drug_name(name2)

    if norm1 == norm2:
        return 0.95

    # Fuzzy match using SequenceMatcher
    similarity = SequenceMatcher(None, norm1, norm2).ratio()

    # Boost score if one name contains the other
    if norm1 in norm2 or norm2 in norm1:
        similarity = max(similarity, 0.85)

    return similarity


def match_by_id(drug1: Dict[str, Any], drug2: Dict[str, Any]) -> bool:
    """
    Check if two drugs match by database IDs.

    Args:
        drug1: First drug dict
        drug2: Second drug dict

    Returns:
        True if IDs match
    """
    # DrugBank ID matching
    db_id1 = drug1.get('drugbank_id')
    db_id2 = drug2.get('drugbank_id')

    if db_id1 and db_id2 and db_id1 == db_id2:
        return True

    # Check ChEMBL ID in Open Targets data
    ot_data1 = drug1.get('_opentargets_data', {})
    ot_data2 = drug2.get('_opentargets_data', {})

    chembl_id1 = ot_data1.get('drugId') if ot_data1 else None
    chembl_id2 = ot_data2.get('drugId') if ot_data2 else None

    if chembl_id1 and chembl_id2 and chembl_id1 == chembl_id2:
        return True

    return False


def drugs_match(drug1: Dict[str, Any], drug2: Dict[str, Any], threshold: float = 0.85) -> bool:
    """
    Determine if two drugs are the same based on IDs and names.

    Args:
        drug1: First drug dict
        drug2: Second drug dict
        threshold: Name similarity threshold (default: 0.85)

    Returns:
        True if drugs match
    """
    # First check ID matching (most reliable)
    if match_by_id(drug1, drug2):
        return True

    # Then check name similarity
    name1 = drug1.get('drug_name', '')
    name2 = drug2.get('drug_name', '')

    similarity = calculate_name_similarity(name1, name2)

    return similarity >= threshold


def get_source_priority(source: str) -> int:
    """
    Get priority score for data source (higher = better).

    Args:
        source: Source name

    Returns:
        Priority score
    """
    priorities = {
        'drugbank': 3,
        'open_targets': 2,
        'clinicaltrials_gov': 1,
        'unknown': 0
    }

    return priorities.get(source, 0)


def merge_drug_data(primary: Dict[str, Any], secondary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two drug dicts, preferring primary source but supplementing missing data.

    Args:
        primary: Primary drug dict (higher quality source)
        secondary: Secondary drug dict

    Returns:
        Merged drug dict
    """
    merged = primary.copy()

    # Track which fields came from secondary source
    supplemented_fields = []

    # Fields to supplement if missing in primary
    supplement_fields = [
        'mechanism', 'indication', 'type', 'phase',
        'modality', 'route', 'mechanism_summary', 'mechanism_detail'
    ]

    for field in supplement_fields:
        primary_val = primary.get(field)
        secondary_val = secondary.get(field)

        # Supplement if primary is missing/generic and secondary has data
        if secondary_val and (
            not primary_val or
            primary_val in ['Unknown', 'Not specified', 'N/A'] or
            (isinstance(primary_val, str) and len(primary_val) < 10)
        ):
            merged[field] = secondary_val
            supplemented_fields.append(field)

    # Merge trials lists
    primary_trials = set(primary.get('trials', []))
    secondary_trials = set(secondary.get('trials', []))
    if secondary_trials:
        merged['trials'] = sorted(list(primary_trials | secondary_trials))

    # Track deduplication metadata
    merged['_deduplication'] = {
        'primary_source': primary.get('source', 'unknown'),
        'merged_from': secondary.get('source', 'unknown'),
        'supplemented_fields': supplemented_fields,
        'name_match_score': calculate_name_similarity(
            primary.get('drug_name', ''),
            secondary.get('drug_name', '')
        )
    }

    return merged


def deduplicate_drugs(drugs: List[Dict[str, Any]], threshold: float = 0.85) -> List[Dict[str, Any]]:
    """
    Deduplicate a list of drugs from potentially multiple sources.

    Args:
        drugs: List of drug dicts
        threshold: Name similarity threshold

    Returns:
        Deduplicated list with merged data
    """
    if not drugs:
        return []

    # Sort by source priority (highest first)
    drugs_sorted = sorted(
        drugs,
        key=lambda d: get_source_priority(d.get('source', 'unknown')),
        reverse=True
    )

    deduplicated = []
    seen_drugs = []

    for drug in drugs_sorted:
        # Check if this drug matches any already seen
        matched = False
        for i, seen_drug in enumerate(seen_drugs):
            if drugs_match(drug, seen_drug, threshold):
                # Merge data, preferring higher-priority source
                if get_source_priority(drug.get('source', '')) > get_source_priority(seen_drug.get('source', '')):
                    # Current drug is higher priority
                    merged = merge_drug_data(drug, seen_drug)
                else:
                    # Seen drug is higher priority
                    merged = merge_drug_data(seen_drug, drug)

                # Replace in list
                deduplicated[i] = merged
                seen_drugs[i] = merged
                matched = True
                break

        if not matched:
            # New unique drug
            deduplicated.append(drug)
            seen_drugs.append(drug)

    return deduplicated


def calculate_data_quality(drug: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate data quality metrics for a drug.

    Args:
        drug: Drug dict

    Returns:
        Data quality dict with scores and indicators
    """
    source = drug.get('source', 'unknown')

    # Base scores by source
    source_reliability = {
        'drugbank': 0.95,
        'open_targets': 0.80,
        'clinicaltrials_gov': 0.65,
        'unknown': 0.30
    }

    reliability_score = source_reliability.get(source, 0.30)

    # Check field completeness
    required_fields = [
        'drug_name', 'type', 'groups', 'mechanism', 'indication',
        'modality', 'route', 'mechanism_summary'
    ]

    fields_present = sum(1 for field in required_fields if drug.get(field) and drug.get(field) not in ['Unknown', 'Not specified', 'N/A'])
    completeness_score = fields_present / len(required_fields)

    # Field quality indicators
    field_quality = {}

    # Mechanism quality
    mechanism = drug.get('mechanism', '')
    if source == 'drugbank':
        field_quality['mechanism'] = 'high'
    elif source == 'open_targets' and mechanism and len(mechanism) > 20:
        field_quality['mechanism'] = 'high'
    elif mechanism and mechanism not in ['Unknown', 'Not specified']:
        field_quality['mechanism'] = 'medium'
    else:
        field_quality['mechanism'] = 'low'

    # Selectivity quality
    selectivity = drug.get('selectivity', 'Unknown')
    if source == 'drugbank' and selectivity != 'Unknown':
        field_quality['selectivity'] = 'high'
    elif drug.get('_opentargets_data'):
        field_quality['selectivity'] = 'inferred'
    else:
        field_quality['selectivity'] = 'unknown'

    # Route quality
    route = drug.get('route', 'Unknown')
    if source == 'drugbank' and route != 'Unknown':
        field_quality['route'] = 'confirmed'
    elif source == 'open_targets':
        field_quality['route'] = 'inferred'
    else:
        field_quality['route'] = 'unknown'

    # Trial data quality
    trials = drug.get('trials', [])
    if len(trials) > 0:
        field_quality['trials'] = 'external_source'
    else:
        field_quality['trials'] = 'none'

    # Overall confidence score (0-1)
    confidence_score = (reliability_score * 0.6) + (completeness_score * 0.4)

    # Add deduplication boost if merged
    if drug.get('_deduplication'):
        confidence_score = min(confidence_score + 0.05, 1.0)

    return {
        'source': source,
        'reliability_score': round(reliability_score, 2),
        'completeness_score': round(completeness_score, 2),
        'confidence_score': round(confidence_score, 2),
        'field_quality': field_quality,
        'is_deduplicated': bool(drug.get('_deduplication')),
        'data_tier': 1 if source == 'drugbank' else (2 if source == 'open_targets' else 3)
    }


def add_data_quality_indicators(drugs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Add data quality indicators to all drugs.

    Args:
        drugs: List of drug dicts

    Returns:
        Drugs with data_quality field added
    """
    enriched_drugs = []

    for drug in drugs:
        drug_copy = drug.copy()
        drug_copy['data_quality'] = calculate_data_quality(drug)
        enriched_drugs.append(drug_copy)

    return enriched_drugs
