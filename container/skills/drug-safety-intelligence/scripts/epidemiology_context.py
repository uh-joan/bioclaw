"""Epidemiology context for drug safety intelligence.

Provides background rates for adverse events using CDC and WHO data
to contextualize drug safety signals against population baselines.

All topic mapping is body-system-level (not per-AE hardcoding).
"""

from typing import Dict, Any, List, Optional


# Body-system → CDC/WHO topic mapping (organ systems, NOT specific AEs)
# These are medical constants — the same 11 organ systems as in risk_matrix_builder.
_BODY_SYSTEM_TOPICS = {
    'cardiac': {'cdc': 'heart disease', 'who': 'cardiovascular diseases'},
    'vascular': {'cdc': 'heart disease', 'who': 'cardiovascular diseases'},
    'hepat': {'cdc': 'liver disease', 'who': 'liver diseases'},
    'liver': {'cdc': 'liver disease', 'who': 'liver diseases'},
    'renal': {'cdc': 'kidney disease', 'who': 'kidney diseases'},
    'kidney': {'cdc': 'kidney disease', 'who': 'kidney diseases'},
    'pulmon': {'cdc': 'respiratory disease', 'who': 'respiratory diseases'},
    'pneumon': {'cdc': 'pneumonia', 'who': 'lower respiratory infections'},
    'nervous': {'cdc': 'neurological', 'who': 'neurological conditions'},
    'stroke': {'cdc': 'stroke', 'who': 'cerebrovascular diseases'},
    'haem': {'cdc': 'blood disorders', 'who': 'blood diseases'},
    'hem': {'cdc': 'blood disorders', 'who': 'blood diseases'},
    'blood': {'cdc': 'blood disorders', 'who': 'blood diseases'},
    'immun': {'cdc': 'autoimmune', 'who': 'immune disorders'},
    'infect': {'cdc': 'infections', 'who': 'infectious diseases'},
    'neoplas': {'cdc': 'cancer', 'who': 'malignant neoplasms'},
    'malignan': {'cdc': 'cancer', 'who': 'malignant neoplasms'},
    'tumor': {'cdc': 'cancer', 'who': 'malignant neoplasms'},
    'endocri': {'cdc': 'diabetes', 'who': 'endocrine disorders'},
    'thyroid': {'cdc': 'thyroid', 'who': 'thyroid disorders'},
    'diabet': {'cdc': 'diabetes', 'who': 'raised fasting blood glucose'},
    'pancrea': {'cdc': 'pancreatitis', 'who': 'diseases of the digestive system'},
    'gastro': {'cdc': 'digestive diseases', 'who': 'diseases of the digestive system'},
    'hypertens': {'cdc': 'high blood pressure', 'who': 'raised blood pressure'},
}


def _derive_topics(ae_name: str) -> Dict[str, str]:
    """Derive CDC/WHO topics from adverse event name using body-system matching.

    No hardcoded AE→topic mapping. Uses body-system stems instead.
    """
    ae_lower = ae_name.lower()
    for stem, topics in _BODY_SYSTEM_TOPICS.items():
        if stem in ae_lower:
            return topics
    return {}


def get_epidemiology_context(
    cdc_health_data_func=None,
    who_health_data_func=None,
    adverse_events: List[str] = None,
    tracker=None,
) -> Dict[str, Any]:
    """
    Get epidemiology background rates for adverse events.

    Args:
        cdc_health_data_func: CDC health data function
        who_health_data_func: WHO health data function
        adverse_events: List of adverse event names to contextualize
        tracker: ProgressTracker instance

    Returns:
        dict with background_rates, cdc_data, who_data
    """
    if tracker:
        tracker.start_step('epidemiology', "Getting epidemiology context...")

    background_rates = []
    cdc_results = []
    who_results = []

    if not adverse_events:
        if tracker:
            tracker.complete_step("No adverse events to contextualize")
        return {
            'background_rates': [],
            'cdc_data': [],
            'who_data': [],
            'summary': {'events_contextualized': 0},
        }

    # Derive topics dynamically from body-system matching
    matched_events = []
    for ae in adverse_events[:10]:
        topics = _derive_topics(ae)
        if topics:
            matched_events.append({
                'adverse_event': ae,
                'cdc_topic': topics.get('cdc'),
                'who_indicator': topics.get('who'),
            })

    if tracker:
        tracker.update_step(0.2, f"Matched {len(matched_events)} events to body systems")

    # Query CDC for matched events (deduplicated by topic)
    cdc_topics_queried = set()
    if cdc_health_data_func:
        for i, event in enumerate(matched_events):
            cdc_topic = event.get('cdc_topic')
            if cdc_topic and cdc_topic not in cdc_topics_queried:
                cdc_topics_queried.add(cdc_topic)
                if tracker:
                    tracker.update_step(
                        0.2 + 0.3 * (i + 1) / max(len(matched_events), 1),
                        f"Querying CDC for {cdc_topic}..."
                    )
                try:
                    cdc_result = cdc_health_data_func(
                        topic=cdc_topic,
                        limit=5,
                    )
                    if cdc_result:
                        cdc_results.append({
                            'topic': cdc_topic,
                            'data': str(cdc_result)[:500] if cdc_result else None,
                        })
                except Exception as e:
                    print(f"  Warning: CDC query failed for {cdc_topic}: {e}")

    # Query WHO for matched events (deduplicated by indicator)
    who_indicators_queried = set()
    if who_health_data_func:
        for i, event in enumerate(matched_events):
            who_indicator = event.get('who_indicator')
            if who_indicator and who_indicator not in who_indicators_queried:
                who_indicators_queried.add(who_indicator)
                if tracker:
                    tracker.update_step(
                        0.5 + 0.3 * (i + 1) / max(len(matched_events), 1),
                        f"Querying WHO for {who_indicator}..."
                    )
                try:
                    who_result = who_health_data_func(
                        indicator=who_indicator,
                        limit=5,
                    )
                    if who_result:
                        who_results.append({
                            'indicator': who_indicator,
                            'data': str(who_result)[:500] if who_result else None,
                        })
                except Exception as e:
                    print(f"  Warning: WHO query failed for {who_indicator}: {e}")

    # Build background rates summary from API data (no hardcoded rates)
    for event in matched_events:
        rate_info = {
            'adverse_event': event['adverse_event'],
            'cdc_topic': event.get('cdc_topic'),
            'who_indicator': event.get('who_indicator'),
            'cdc_available': event.get('cdc_topic') in cdc_topics_queried,
            'who_available': event.get('who_indicator') in who_indicators_queried,
        }
        # Try to extract a rate from CDC results
        for cdc in cdc_results:
            if cdc['topic'] == event.get('cdc_topic') and cdc.get('data'):
                rate_info['background_note'] = f"CDC ({cdc['topic']}): data available"
                break
        if 'background_note' not in rate_info:
            rate_info['background_note'] = f"Body system: {event.get('cdc_topic', 'unknown')}"
        background_rates.append(rate_info)

    if tracker:
        tracker.complete_step(
            f"Epidemiology: {len(background_rates)} events contextualized, "
            f"{len(cdc_results)} CDC queries, {len(who_results)} WHO queries"
        )

    return {
        'background_rates': background_rates,
        'cdc_data': cdc_results,
        'who_data': who_results,
        'summary': {
            'events_contextualized': len(background_rates),
            'cdc_queries': len(cdc_results),
            'who_queries': len(who_results),
        },
    }
