"""
Safety profiling utilities for adverse events and label warnings.

Provides functions to:
- Query FAERS adverse events database
- Analyze adverse event severity and frequency
- Extract safety warnings from drug labels
- Calculate safety risk scores
"""

from typing import Dict, Any, List
from collections import defaultdict


def get_adverse_events(fda_lookup_func, drug_name: str, top_reactions: int = 10) -> Dict[str, Any]:
    """
    Get adverse events for a drug from FAERS database using count aggregation.

    Args:
        fda_lookup_func: lookup_drug function from fda_mcp
        drug_name: Drug name to search
        top_reactions: Number of top reactions to return (default: 10)

    Returns:
        dict with total reports and top common reactions
    """
    try:
        # Use count aggregation to get top reactions by frequency
        result = fda_lookup_func(
            search_term=drug_name,
            search_type='adverse_events',
            limit=top_reactions,  # Limit is used for count results
            count='patient.reaction.reactionmeddrapt.exact'
        )

        if not result:
            return {
                'total_reports': 0,
                'common_reactions': [],
                'data_source': 'FDA FAERS',
                'error': 'No adverse event data found'
            }

        # Parse count aggregation response
        # Structure: {"meta": {...}, "results": [{"term": "reaction", "count": 123}, ...]}
        data = result.get('data', {})

        # Get total from meta
        meta = result.get('meta', {})
        total_reports = meta.get('results', {}).get('total', 0)

        # Parse aggregated reaction counts
        results = data.get('results', [])
        if not results:
            return {
                'total_reports': total_reports,
                'common_reactions': [],
                'data_source': 'FDA FAERS',
                'error': 'No reaction counts found'
            }

        # Extract top reactions from count aggregation
        common_reactions = []
        for item in results[:top_reactions]:
            reaction = item.get('term', 'Unknown')
            count = item.get('count', 0)
            common_reactions.append({
                'reaction': reaction,
                'count': count
            })

        return {
            'total_reports': total_reports,
            'common_reactions': common_reactions,
            'data_source': 'FDA FAERS'
        }

    except Exception as e:
        return {
            'total_reports': 0,
            'common_reactions': [],
            'data_source': 'FDA FAERS',
            'error': str(e)
        }


def get_safety_warnings(fda_lookup_func, drug_name: str) -> Dict[str, Any]:
    """
    Extract safety warnings from FDA drug labels.

    Args:
        fda_lookup_func: lookup_drug function from fda_mcp
        drug_name: Drug name to search

    Returns:
        dict with boxed warnings, contraindications, warnings
    """
    try:
        result = fda_lookup_func(
            search_term=drug_name,
            search_type='label',
            limit=1,
            count='openfda.brand_name.exact'
        )

        if not result:
            return {
                'boxed_warning': None,
                'contraindications': None,
                'warnings_and_precautions': None,
                'error': 'No label data found'
            }

        # Handle nested structure
        data = result.get('data', {})
        if not data or 'results' not in data:
            return {
                'boxed_warning': None,
                'contraindications': None,
                'warnings_and_precautions': None,
                'error': 'No label results'
            }

        first_result = data['results'][0] if data['results'] else None
        if not first_result:
            return {
                'boxed_warning': None,
                'contraindications': None,
                'warnings_and_precautions': None
            }

        # Extract warnings (truncate for display)
        boxed_warning = first_result.get('boxed_warning')
        contraindications = first_result.get('contraindications')
        warnings = first_result.get('warnings_and_cautions') or first_result.get('warnings')

        return {
            'boxed_warning': boxed_warning[:500] + '...' if boxed_warning and len(boxed_warning) > 500 else boxed_warning,
            'contraindications': contraindications[:300] + '...' if contraindications and len(contraindications) > 300 else contraindications,
            'warnings_and_precautions': warnings[:300] + '...' if warnings and len(warnings) > 300 else warnings,
            'has_boxed_warning': bool(boxed_warning)
        }

    except Exception as e:
        return {
            'boxed_warning': None,
            'contraindications': None,
            'warnings_and_precautions': None,
            'error': str(e)
        }


def get_safety_profile_batch(
    fda_lookup_func,
    drugs: List[Dict],
    max_drugs: int = 1000,
    include_adverse_events: bool = True,
    include_warnings: bool = True
) -> Dict[str, Any]:
    """
    Get safety profiles for multiple drugs.

    Args:
        fda_lookup_func: FDA lookup function
        drugs: List of drug dicts with 'drug_name' field
        max_drugs: Maximum drugs to analyze
        include_adverse_events: Include FAERS data
        include_warnings: Include label warnings

    Returns:
        dict with safety_profiles, summary statistics
    """
    safety_profiles = []

    for drug in drugs[:max_drugs]:
        drug_name = drug.get('drug_name', '')
        if not drug_name:
            continue

        drug_safety = {
            'drug_name': drug_name,
            'drugbank_id': drug.get('drugbank_id'),
            'adverse_events': None,
            'warnings': None
        }

        # Get adverse events
        if include_adverse_events:
            adverse_events = get_adverse_events(fda_lookup_func, drug_name, top_reactions=10)
            drug_safety['adverse_events'] = adverse_events

        # Get label warnings
        if include_warnings:
            warnings = get_safety_warnings(fda_lookup_func, drug_name)
            drug_safety['warnings'] = warnings

        safety_profiles.append(drug_safety)

    # Calculate summary
    # Count drugs with adverse event data (check if common_reactions is not empty)
    total_with_ae_data = sum(
        1 for p in safety_profiles
        if p.get('adverse_events') and (
            p['adverse_events'].get('total_reports', 0) > 0 or
            len(p['adverse_events'].get('common_reactions', [])) > 0
        )
    )
    total_with_boxed_warnings = sum(
        1 for p in safety_profiles
        if p.get('warnings') and p['warnings'].get('has_boxed_warning', False)
    )

    return {
        'safety_profiles': safety_profiles,
        'summary': {
            'total_drugs_analyzed': len(safety_profiles),
            'drugs_with_adverse_event_data': total_with_ae_data,
            'drugs_with_boxed_warnings': total_with_boxed_warnings
        }
    }


def calculate_safety_risk_score(safety_profile: Dict) -> float:
    """
    Calculate safety risk score (0.0-1.0, higher = more risk).

    Args:
        safety_profile: Safety profile for a single drug

    Returns:
        Risk score (0.0-1.0)
    """
    risk_score = 0.0

    adverse_events = safety_profile.get('adverse_events', {})
    warnings = safety_profile.get('warnings', {})

    # Factor 1: Serious adverse event rate (weight: 0.4)
    serious_pct = adverse_events.get('serious_percentage', 0)
    if serious_pct > 0:
        # Normalize: 0-10% serious = 0-0.4 risk
        risk_score += min(serious_pct / 25, 0.4)

    # Factor 2: Boxed warning present (weight: 0.3)
    if warnings.get('has_boxed_warning'):
        risk_score += 0.3

    # Factor 3: Death reports (weight: 0.3)
    serious_outcomes = adverse_events.get('serious_outcomes', {})

    # Handle serious_outcomes as either dict or list
    death_count = 0
    if isinstance(serious_outcomes, dict):
        death_count = serious_outcomes.get('Death', 0)
    elif isinstance(serious_outcomes, list):
        # Count death outcomes in list
        death_count = sum(1 for outcome in serious_outcomes if 'death' in str(outcome).lower())

    total_reports = adverse_events.get('total_reports', 1)
    if death_count > 0:
        death_rate = death_count / total_reports
        risk_score += min(death_rate * 100, 0.3)

    return min(round(risk_score, 2), 1.0)


def classify_by_safety_risk(safety_batch: Dict) -> Dict[str, List[Dict]]:
    """
    Classify drugs by safety risk level.

    Args:
        safety_batch: Output from get_safety_profile_batch

    Returns:
        dict with high_risk, moderate_risk, low_risk, insufficient_data
    """
    high_risk = []
    moderate_risk = []
    low_risk = []
    insufficient_data = []

    for profile in safety_batch['safety_profiles']:
        risk_score = calculate_safety_risk_score(profile)

        drug_info = {
            'drug_name': profile['drug_name'],
            'risk_score': risk_score
        }

        if risk_score == 0:
            insufficient_data.append(drug_info)
        elif risk_score >= 0.6:
            high_risk.append(drug_info)
        elif risk_score >= 0.3:
            moderate_risk.append(drug_info)
        else:
            low_risk.append(drug_info)

    return {
        'high_risk': high_risk,
        'moderate_risk': moderate_risk,
        'low_risk': low_risk,
        'insufficient_data': insufficient_data
    }


def generate_safety_summary(safety_batch: Dict) -> str:
    """
    Generate text summary of safety analysis.

    Args:
        safety_batch: Output from get_safety_profile_batch

    Returns:
        Formatted text summary
    """
    summary = safety_batch['summary']
    classified = classify_by_safety_risk(safety_batch)

    lines = []
    lines.append("\nSAFETY ANALYSIS")
    lines.append("-" * 80)
    lines.append(f"Drugs Analyzed: {summary['total_drugs_analyzed']}")
    lines.append(f"With Adverse Event Data: {summary['drugs_with_adverse_event_data']}")
    lines.append(f"With Boxed Warnings: {summary['drugs_with_boxed_warnings']}")
    lines.append("")
    lines.append("RISK CLASSIFICATION:")
    lines.append(f"  High Risk: {len(classified['high_risk'])} drugs")
    lines.append(f"  Moderate Risk: {len(classified['moderate_risk'])} drugs")
    lines.append(f"  Low Risk: {len(classified['low_risk'])} drugs")
    lines.append(f"  Insufficient Data: {len(classified['insufficient_data'])} drugs")

    return "\n".join(lines)


def aggregate_class_wide_safety(safety_batch: Dict, target_name: str = None) -> Dict[str, Any]:
    """
    Aggregate adverse events across all drugs targeting the same protein.

    Shows class-wide safety signals for the entire drug class.

    Args:
        safety_batch: Output from get_safety_profile_batch
        target_name: Target name for display (optional)

    Returns:
        dict with class_wide_reactions, total_drugs, total_reports
    """
    from collections import defaultdict

    # Aggregate all reactions across all drugs
    class_reactions = defaultdict(int)
    total_drugs_with_data = 0
    drugs_contributing = []

    for profile in safety_batch['safety_profiles']:
        adverse_events = profile.get('adverse_events', {})
        reactions = adverse_events.get('common_reactions', [])

        if reactions:
            total_drugs_with_data += 1
            drugs_contributing.append(profile['drug_name'])

            # Sum reaction counts across all drugs
            for reaction in reactions:
                reaction_name = reaction.get('reaction', 'Unknown')
                count = reaction.get('count', 0)
                class_reactions[reaction_name] += count

    # Sort by total count descending
    sorted_reactions = sorted(
        class_reactions.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # Get top 15 class-wide reactions
    top_class_reactions = [
        {
            'reaction': reaction,
            'total_count': count
        }
        for reaction, count in sorted_reactions[:15]
    ]

    # Calculate total reports (sum of all reaction counts)
    total_reports = sum(class_reactions.values())

    return {
        'target_name': target_name or 'this target',
        'class_wide_reactions': top_class_reactions,
        'total_drugs_analyzed': safety_batch['summary']['total_drugs_analyzed'],
        'drugs_with_data': total_drugs_with_data,
        'drugs_contributing': drugs_contributing,
        'total_reaction_reports': total_reports,
        'unique_reactions': len(class_reactions)
    }
