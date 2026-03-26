"""Drug-drug interaction analyzer for drug safety intelligence.

Uses DrugBank to analyze:
- Drug-drug interactions with severity inference
- CYP450 enzyme interactions
- Food interactions
- Polypharmacy risk scoring
"""

from typing import Dict, Any, List, Optional


def _infer_severity(description: str) -> str:
    """Infer interaction severity from description text.

    Reuses pattern from real-world-utilization skill.
    DrugBank free data doesn't include severity field directly.
    """
    desc_lower = description.lower()

    # Major severity indicators
    if any(term in desc_lower for term in [
        'contraindicated', 'avoid', 'do not', 'life-threatening',
        'serious', 'fatal', 'death', 'hemorrhag', 'bleeding',
        'serotonin syndrome', 'qt prolongation', 'torsade',
        'significantly increase', 'significantly decrease',
    ]):
        return 'major'

    # Minor severity indicators
    if any(term in desc_lower for term in [
        'minor', 'slight', 'minimal', 'unlikely',
        'not clinically significant', 'no clinically significant',
    ]):
        return 'minor'

    # Default to moderate
    return 'moderate'


def _extract_cyp_interactions(description: str) -> List[str]:
    """Extract CYP450 enzyme mentions from interaction description."""
    import re
    cyp_pattern = r'CYP\d[A-Z]\d+'
    matches = re.findall(cyp_pattern, description, re.IGNORECASE)
    return list(set(m.upper() for m in matches))


def _analyze_via_chembl(
    chembl_drug_search_func,
    chembl_get_mechanism_func,
    chembl_get_admet_func,
    drug_names: List[str],
) -> Dict[str, Any]:
    """Fallback interaction analysis via ChEMBL when DrugBank is unavailable.

    Uses ChEMBL mechanism data and ADMET properties to infer interaction risk.
    """
    mechanisms = []
    admet_data = []
    cyp_enzymes = set()
    drugs_analyzed = 0

    for drug_name in drug_names[:5]:
        try:
            # Find drug in ChEMBL
            result = chembl_drug_search_func(method='drug_search', query=drug_name, limit=3)
            if not result or not result.get('results'):
                continue

            chembl_id = None
            for r in result['results']:
                if (r.get('pref_name', '') or '').lower() == drug_name.lower():
                    chembl_id = r.get('molecule_chembl_id')
                    break
            if not chembl_id:
                chembl_id = result['results'][0].get('molecule_chembl_id')
            if not chembl_id:
                continue

            drugs_analyzed += 1

            # Get mechanism of action
            if chembl_get_mechanism_func:
                mech = chembl_get_mechanism_func(method='get_mechanism', chembl_id=chembl_id)
                if mech and mech.get('mechanisms'):
                    for m in mech['mechanisms']:
                        mechanisms.append({
                            'drug': drug_name,
                            'chembl_id': chembl_id,
                            'mechanism': m.get('mechanism_of_action', ''),
                            'action_type': m.get('action_type', ''),
                            'target': m.get('target_chembl_id', ''),
                        })

            # Get ADMET properties
            if chembl_get_admet_func:
                admet = chembl_get_admet_func(method='get_admet', chembl_id=chembl_id)
                if admet and admet.get('properties'):
                    props = admet['properties']
                    admet_entry = {
                        'drug': drug_name,
                        'chembl_id': chembl_id,
                    }
                    # Extract relevant ADMET flags
                    for key in ['alogp', 'hba', 'hbd', 'psa', 'ro5_violations',
                                'molecular_weight', 'full_mwt', 'cx_logp']:
                        if key in props:
                            admet_entry[key] = props[key]
                    admet_data.append(admet_entry)

                    # Check for CYP-related flags in properties
                    for key, val in props.items():
                        if 'cyp' in str(key).lower() and val:
                            cyp_enzymes.add(str(key).upper())

        except Exception as e:
            print(f"  Warning: ChEMBL interaction analysis failed for {drug_name}: {e}")

    return {
        'mechanisms': mechanisms,
        'admet_data': admet_data,
        'cyp_enzymes': sorted(cyp_enzymes),
        'drugs_analyzed': drugs_analyzed,
    }


def analyze_interactions(
    drugbank_search_func,
    drug_names: List[str],
    tracker=None,
    chembl_get_admet_func=None,
    chembl_drug_search_func=None,
    chembl_get_mechanism_func=None,
) -> Dict[str, Any]:
    """
    Analyze drug-drug interactions for drugs in the class.

    Args:
        drugbank_search_func: DrugBank search wrapper function (may be None)
        drug_names: List of drug names to analyze
        tracker: ProgressTracker instance
        chembl_get_admet_func: ChEMBL ADMET function (fallback)
        chembl_drug_search_func: ChEMBL drug search function (fallback)
        chembl_get_mechanism_func: ChEMBL mechanism function (fallback)

    Returns:
        dict with interactions, food_interactions, cyp_interactions, polypharmacy_score
    """
    if tracker:
        tracker.start_step('interactions', "Analyzing drug interactions...")

    all_interactions = []
    all_food_interactions = []
    cyp_enzymes = set()
    drugs_analyzed = 0
    drugbank_worked = False

    # Try DrugBank first (primary source for DDI data)
    if drugbank_search_func:
        for i, drug_name in enumerate(drug_names[:5]):
            if tracker:
                tracker.update_step(
                    (i + 1) / min(len(drug_names), 5) * 0.6,
                    f"Analyzing interactions for {drug_name}..."
                )

            try:
                db_search = drugbank_search_func(method='search_by_name', query=drug_name, limit=3)
                if not db_search or 'results' not in db_search:
                    continue

                results = db_search.get('results', [])
                if not results:
                    continue

                drugbank_id = None
                for drug in results:
                    name = drug.get('name', '').lower()
                    if name == drug_name.lower():
                        drugbank_id = drug.get('drugbank_id')
                        break

                if not drugbank_id and results:
                    drugbank_id = results[0].get('drugbank_id')

                if not drugbank_id:
                    continue

                details_result = drugbank_search_func(
                    method='get_drug_details', drugbank_id=drugbank_id
                )
                if not details_result or 'drug' not in details_result:
                    continue

                drug_data = details_result.get('drug', {})
                drugs_analyzed += 1
                drugbank_worked = True

                # Extract DDIs
                ddi_list = drug_data.get('drug_interactions', [])
                for interaction in ddi_list:
                    desc = interaction.get('description', '')
                    severity = _infer_severity(desc)
                    cyps = _extract_cyp_interactions(desc)
                    cyp_enzymes.update(cyps)

                    db_ids = interaction.get('drugbank_id', [])
                    all_interactions.append({
                        'source_drug': drug_name,
                        'interacting_drug': interaction.get('name', 'Unknown'),
                        'drugbank_id': db_ids[0] if db_ids else '',
                        'description': desc[:200],
                        'severity': severity,
                        'cyp_enzymes': cyps,
                    })

                # Extract food interactions
                food_list = drug_data.get('food_interactions', [])
                for food in food_list:
                    if isinstance(food, str) and food:
                        all_food_interactions.append({
                            'drug': drug_name,
                            'interaction': food[:200],
                        })

                # Extract CYP enzymes
                enzymes = drug_data.get('enzymes', [])
                if isinstance(enzymes, list):
                    for enzyme in enzymes:
                        if isinstance(enzyme, dict):
                            enzyme_name = enzyme.get('name', '')
                            if 'CYP' in enzyme_name.upper():
                                cyp_enzymes.add(enzyme_name.upper())
                        elif isinstance(enzyme, str) and 'CYP' in enzyme.upper():
                            cyp_enzymes.add(enzyme.upper())

            except Exception as e:
                print(f"  Warning: Interaction analysis failed for {drug_name}: {e}")

    # ChEMBL fallback if DrugBank returned nothing
    chembl_data = None
    if not drugbank_worked and chembl_drug_search_func:
        if tracker:
            tracker.update_step(0.6, "DrugBank unavailable, using ChEMBL for mechanism/ADMET data...")
        chembl_data = _analyze_via_chembl(
            chembl_drug_search_func, chembl_get_mechanism_func,
            chembl_get_admet_func, drug_names,
        )
        drugs_analyzed = chembl_data.get('drugs_analyzed', 0)
        cyp_enzymes.update(chembl_data.get('cyp_enzymes', []))

    # Sort interactions by severity
    severity_order = {'major': 0, 'moderate': 1, 'minor': 2}
    all_interactions.sort(key=lambda x: (severity_order.get(x['severity'], 1), x.get('interacting_drug', '')))

    # Count by severity
    severity_counts = {'major': 0, 'moderate': 0, 'minor': 0}
    for item in all_interactions:
        severity_counts[item['severity']] = severity_counts.get(item['severity'], 0) + 1

    # Polypharmacy risk score (0-1)
    total_interactions = len(all_interactions)
    major_count = severity_counts.get('major', 0)
    cyp_count = len(cyp_enzymes)

    polypharmacy_score = min(1.0, round(
        0.3 * min(total_interactions / 100, 1.0) +
        0.4 * min(major_count / 20, 1.0) +
        0.3 * min(cyp_count / 5, 1.0),
        2
    ))

    # Determine data source for reporting
    data_source = 'DrugBank' if drugbank_worked else ('ChEMBL' if chembl_data else 'None')

    if tracker:
        if drugbank_worked:
            tracker.complete_step(
                f"Interactions ({data_source}): {total_interactions} DDIs "
                f"({major_count} major, {severity_counts.get('moderate', 0)} moderate), "
                f"{len(all_food_interactions)} food, {cyp_count} CYP enzymes"
            )
        elif chembl_data:
            n_mech = len(chembl_data.get('mechanisms', []))
            n_admet = len(chembl_data.get('admet_data', []))
            tracker.complete_step(
                f"Interactions (ChEMBL fallback): {n_mech} mechanisms, "
                f"{n_admet} ADMET profiles, {cyp_count} CYP enzymes"
            )
        else:
            tracker.complete_step("Interactions: No data available from DrugBank or ChEMBL")

    result = {
        'interactions': all_interactions,
        'food_interactions': all_food_interactions,
        'cyp_enzymes': sorted(cyp_enzymes),
        'severity_counts': severity_counts,
        'polypharmacy_score': polypharmacy_score,
        'data_source': data_source,
        'summary': {
            'drugs_analyzed': drugs_analyzed,
            'total_interactions': total_interactions,
            'major_interactions': major_count,
            'moderate_interactions': severity_counts.get('moderate', 0),
            'minor_interactions': severity_counts.get('minor', 0),
            'food_interactions_count': len(all_food_interactions),
            'cyp_enzymes_count': cyp_count,
            'polypharmacy_risk': 'HIGH' if polypharmacy_score >= 0.7 else
                                 'MODERATE' if polypharmacy_score >= 0.4 else 'LOW',
            'data_source': data_source,
        },
    }

    # Include ChEMBL data if it was the fallback
    if chembl_data:
        result['chembl_mechanisms'] = chembl_data.get('mechanisms', [])
        result['chembl_admet'] = chembl_data.get('admet_data', [])

    return result
