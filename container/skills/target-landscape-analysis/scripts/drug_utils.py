"""
Drug discovery and analysis utilities for DrugBank integration.
"""

from typing import Dict, Any, List

# Import classification modules
try:
    from modality_classifier import classify_modality
    from mechanism_classifier import classify_mechanism
    from target_utils import analyze_selectivity
except ImportError:
    # Fallback if running from different directory
    classify_modality = None
    classify_mechanism = None
    analyze_selectivity = None


def search_drugs_by_indication(search_by_indication_func, indication: str, max_drugs: int = 1000) -> Dict[str, Any]:
    """
    Search DrugBank for drugs by indication (disease).

    Args:
        search_by_indication_func: search_by_indication function from drugbank_mcp
        indication: Disease name (e.g., "diabetes", "obesity")
        max_drugs: Maximum drugs to return

    Returns:
        dict with drugs list and count
    """
    try:
        search_result = search_by_indication_func(
            query=indication,
            limit=max_drugs
        )

        if not search_result or 'results' not in search_result:
            return {'drugs': [], 'total': 0}

        return {
            'drugs': search_result['results'],
            'total': len(search_result['results'])
        }

    except Exception as e:
        return {
            'drugs': [],
            'total': 0,
            'error': str(e)
        }


def search_drugs_by_target(search_by_target_func, gene_symbol: str, target_name: str = None,
                          search_by_indication_func=None, key_indications: List[str] = None,
                          max_drugs: int = 1000, get_drug_details_func=None) -> Dict[str, Any]:
    """
    Search DrugBank for drugs targeting a specific protein.

    Strategy (due to DrugBank API limitations):
    1. Try direct target search (gene symbol, target name, variations)
    2. If that fails, search by indication and VALIDATE targets match

    NOTE: DrugBank's target→drug search is unreliable, so we use indication search
    as fallback but validate each drug actually targets the protein.

    Args:
        search_by_target_func: search_by_target function from drugbank_mcp
        gene_symbol: Gene symbol (e.g., "GLP1R")
        target_name: Target name for fallback search (e.g., "glucagon-like peptide 1 receptor")
        search_by_indication_func: search_by_indication function for fallback
        key_indications: List of disease names from genetic validation
        max_drugs: Maximum drugs to return
        get_drug_details_func: get_drug_details function to validate targets

    Returns:
        dict with drugs list and count
    """
    try:
        # Generate search variations
        # IMPORTANT: Prioritize target_name (from Open Targets) over gene_symbol
        # DrugBank stores full target names like "Glucagon-like peptide 1 receptor"
        # not gene symbols like "GLP1R"
        search_terms = []

        if target_name:
            search_terms.append(target_name)  # Try resolved name FIRST

        if gene_symbol:
            search_terms.append(gene_symbol)  # Fallback to symbol

        # Add common variations for gene symbol
        if gene_symbol:
            # Try with hyphens (GLP1R -> GLP-1R)
            if '-' not in gene_symbol and len(gene_symbol) > 3:
                # Insert hyphen before last character if it's a digit followed by letter
                import re
                hyphenated = re.sub(r'([0-9])([A-Z])', r'\1-\2', gene_symbol)
                if hyphenated != gene_symbol:
                    search_terms.append(hyphenated)

            # Try "receptor" suffix
            if 'receptor' not in gene_symbol.lower():
                search_terms.append(f"{gene_symbol} receptor")
                if '-' in gene_symbol:
                    search_terms.append(gene_symbol.replace('-', '-1 ') + ' receptor')

        # Try each search term
        for term in search_terms:
            search_result = search_by_target_func(
                target=term,
                limit=max_drugs
            )

            # DrugBank MCP returns 'results' key
            if search_result and 'results' in search_result and search_result['results']:
                return {
                    'drugs': search_result['results'],
                    'total': len(search_result['results']),
                    'strategy': f'target_search: {term}'
                }

        # Fallback: Search by indication and validate targets
        if search_by_indication_func and key_indications and get_drug_details_func and target_name:
            validated_drugs = []
            seen_ids = set()

            # Prepare target matching strings (lowercase for fuzzy matching)
            target_keywords = set()
            if target_name:
                target_keywords.add(target_name.lower())
            if gene_symbol:
                target_keywords.add(gene_symbol.lower())

            for indication in key_indications[:3]:  # Try top 3 indications
                indication_result = search_drugs_by_indication(
                    search_by_indication_func,
                    indication,
                    max_drugs=max_drugs
                )

                if indication_result['drugs']:
                    for drug in indication_result['drugs']:
                        drug_id = drug.get('drugbank_id')
                        if drug_id and drug_id not in seen_ids:
                            seen_ids.add(drug_id)

                            # Get full details to check targets
                            try:
                                drug_details_result = get_drug_details_func(drugbank_id=drug_id)
                                if drug_details_result:
                                    drug_details = drug_details_result.get('drug', drug_details_result)
                                    targets = drug_details.get('targets', [])

                                    # Check if any target matches our protein
                                    for target in targets:
                                        target_name_db = target.get('name', '').lower()
                                        # Check if target name contains any of our keywords
                                        if any(keyword in target_name_db for keyword in target_keywords):
                                            validated_drugs.append(drug)
                                            break  # Found match, add drug once
                            except:
                                continue  # Skip if validation fails

            if validated_drugs:
                return {
                    'drugs': validated_drugs[:max_drugs],
                    'total': len(validated_drugs[:max_drugs]),
                    'strategy': 'indication_search_with_target_validation',
                    'indications_searched': key_indications[:3],
                    'validated_from': len(seen_ids)
                }

        # No results found
        return {
            'drugs': [],
            'total': 0,
            'strategy': 'no_match_found',
            'searches_tried': search_terms
        }

    except Exception as e:
        return {
            'drugs': [],
            'total': 0,
            'error': str(e),
            'strategy': 'error'
        }


def get_drug_details_batch(
    get_drug_details_func,
    drugs: List[Dict],
    max_details: int = 1000,
    target_gene: str = None,
    target_name: str = None,
    classify: bool = True
) -> List[Dict[str, Any]]:
    """
    Fetch detailed information for multiple drugs with optional classification.

    Args:
        get_drug_details_func: get_drug_details function from drugbank_mcp
        drugs: List of drug dicts from search_drugs_by_target
        max_details: Maximum drugs to fetch details for
        target_gene: Primary target gene symbol (e.g., "GLP1R") for classification
        target_name: Human-readable target name for classification
        classify: Enable modality/mechanism/selectivity classification (default: True)

    Returns:
        List of dicts with drug details + classification (if enabled)
    """
    drugs_with_details = []

    for drug in drugs[:max_details]:
        drugbank_id = drug.get('drugbank_id')
        if not drugbank_id:
            continue

        try:
            drug_details_result = get_drug_details_func(
                drugbank_id=drugbank_id
            )

            if drug_details_result:
                # Extract nested 'drug' object from result
                drug_details = drug_details_result.get('drug', drug_details_result)

                # Handle groups - can be list of strings or list of dicts
                groups = drug_details.get('groups', [])
                if groups and isinstance(groups[0], dict):
                    groups = [g.get('name', str(g)) for g in groups]

                # Build base drug dict
                drug_dict = {
                    'drug_name': drug_details.get('name', drug.get('name', 'Unknown')),
                    'drugbank_id': drugbank_id,
                    'type': drug_details.get('type', drug.get('type', 'Unknown')),
                    'groups': groups,
                    'indication': drug_details.get('indication', 'Not specified'),
                    'mechanism': drug_details.get('mechanism_of_action', 'Not specified'),
                    'categories': drug_details.get('categories', [])[:3],
                    'cas_number': drug_details.get('cas_number', drug.get('cas_number')),
                    'description': (drug_details.get('description', '')[:200] + '...') if drug_details.get('description') else '',
                    # Keep full drug_details for classification
                    '_full_details': drug_details
                }

                # === CLASSIFICATION (Phase A) ===
                if classify and target_gene:
                    # Modality classification
                    if classify_modality:
                        try:
                            modality_result = classify_modality(drug_details)
                            drug_dict.update(modality_result)  # Adds modality, modality_category, chart_symbol, route
                        except Exception as e:
                            # Fallback if classification fails
                            drug_dict.update({
                                'modality': 'Unknown',
                                'modality_category': 'unknown',
                                'chart_symbol': 'circle',
                                'route': 'Unknown'
                            })

                    # Mechanism classification
                    if classify_mechanism:
                        try:
                            mechanism_result = classify_mechanism(drug_details, target_gene, target_name)
                            drug_dict.update({
                                'mechanism_summary': mechanism_result['mechanism_summary'],
                                'mechanism_type': mechanism_result['mechanism_type'],
                                'is_multispecific': mechanism_result['is_multispecific'],
                                'targets': mechanism_result['targets'],
                                'target_count': mechanism_result['target_count'],
                                'sector': mechanism_result['sector'],
                                'mechanism_detail': mechanism_result['mechanism_detail']
                            })
                        except Exception as e:
                            # Fallback
                            drug_dict.update({
                                'mechanism_summary': 'Unknown',
                                'mechanism_type': 'other',
                                'is_multispecific': False,
                                'targets': [target_gene] if target_gene else [],
                                'target_count': 1,
                                'sector': 'Other',
                                'mechanism_detail': ''
                            })

                    # Selectivity analysis
                    if analyze_selectivity:
                        try:
                            # Use targets from mechanism classification
                            drug_targets = drug_dict.get('targets', [target_gene] if target_gene else [])
                            selectivity_result = analyze_selectivity(
                                drug_targets=drug_targets,
                                primary_target=target_gene,
                                drug_name=drug_dict['drug_name']
                            )
                            drug_dict.update({
                                'selectivity': selectivity_result['selectivity'],
                                'selectivity_description': selectivity_result['description'],
                                'color_code': selectivity_result['color_code']
                            })
                        except Exception as e:
                            # Fallback
                            drug_dict.update({
                                'selectivity': 'Unknown',
                                'selectivity_description': '',
                                'color_code': '#888888'
                            })

                drugs_with_details.append(drug_dict)

        except Exception as e:
            print(f"Warning: Could not fetch details for {drug.get('name')}: {e}")
            continue

    return drugs_with_details


def classify_drugs_by_status(drugs: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Classify drugs by development/approval status.

    Args:
        drugs: List of drugs with 'groups' field

    Returns:
        dict with approved, investigational, experimental lists
    """
    approved = []
    investigational = []
    experimental = []
    other = []

    for drug in drugs:
        groups_lower = [g.lower() for g in drug.get('groups', [])]

        if 'approved' in groups_lower:
            approved.append(drug)
        elif 'investigational' in groups_lower:
            investigational.append(drug)
        elif 'experimental' in groups_lower:
            experimental.append(drug)
        else:
            other.append(drug)

    return {
        'approved': approved,
        'investigational': investigational,
        'experimental': experimental,
        'other': other
    }


def filter_active_drugs(drugs: List[Dict]) -> Dict[str, Any]:
    """
    Filter drugs to only include active/relevant ones for competitive landscape.

    Excludes:
    - Withdrawn drugs
    - Illicit substances
    - Nutraceuticals/supplements
    - Veterinary-only drugs

    Args:
        drugs: List of drugs with 'groups' field

    Returns:
        dict with active_drugs list and exclusion counts
    """
    active_drugs = []
    excluded_counts = {
        'withdrawn': 0,
        'illicit': 0,
        'nutraceutical': 0,
        'vet_only': 0
    }

    for drug in drugs:
        groups_lower = [g.lower() for g in drug.get('groups', [])]

        # Check for exclusion criteria
        if 'withdrawn' in groups_lower:
            excluded_counts['withdrawn'] += 1
            continue
        if 'illicit' in groups_lower:
            excluded_counts['illicit'] += 1
            continue
        if 'nutraceutical' in groups_lower:
            excluded_counts['nutraceutical'] += 1
            continue
        if 'vet_approved' in groups_lower and 'approved' not in groups_lower:
            # Exclude vet-only (but keep drugs approved for both human and vet)
            excluded_counts['vet_only'] += 1
            continue

        # Include this drug
        active_drugs.append(drug)

    return {
        'active_drugs': active_drugs,
        'excluded_counts': excluded_counts,
        'total_excluded': sum(excluded_counts.values())
    }


def summarize_drug_discovery(classified_drugs: Dict, total_drugs: int) -> Dict[str, Any]:
    """
    Create summary statistics for drug discovery.

    Args:
        classified_drugs: Output from classify_drugs_by_status
        total_drugs: Total drugs found in initial search

    Returns:
        dict with summary statistics
    """
    return {
        'total_drugs_found': total_drugs,
        'with_details': sum(len(drugs) for drugs in classified_drugs.values()),
        'by_status': {
            'approved': len(classified_drugs['approved']),
            'investigational': len(classified_drugs['investigational']),
            'experimental': len(classified_drugs['experimental']),
            'other': len(classified_drugs['other'])
        }
    }


def extract_drugs_from_opentargets(get_target_details_func, target_id: str) -> Dict[str, Any]:
    """
    Extract drug information from Open Targets knownDrugs.

    Args:
        get_target_details_func: get_target_details function from opentargets_mcp
        target_id: Ensembl gene ID (e.g., "ENSG00000181634")

    Returns:
        dict with drugs list and metadata
    """
    try:
        details = get_target_details_func(id=target_id)
        known_drugs = details.get('data', {}).get('target', {}).get('knownDrugs', {})

        if not known_drugs.get('rows'):
            return {
                'drugs': [],
                'total': 0,
                'source': 'open_targets',
                'strategy': 'no_drugs_found'
            }

        # Extract unique drugs (rows can have duplicate drugs for different diseases)
        seen_drugs = {}
        for row in known_drugs['rows']:
            drug_id = row.get('drugId')
            if not drug_id or drug_id in seen_drugs:
                continue

            # Convert phase to groups (map phase number to DrugBank-like groups)
            phase = row.get('phase', 0)
            groups = []
            if phase == 4:
                groups = ['approved']
            elif phase == 3:
                groups = ['investigational']
            elif phase in [1, 2]:
                groups = ['experimental']
            else:
                groups = ['other']

            seen_drugs[drug_id] = {
                'drug_name': row.get('prefName', 'Unknown'),
                'drugbank_id': drug_id,  # ChEMBL ID in this case
                'type': row.get('drugType', 'Unknown'),
                'groups': groups,
                'phase': phase,
                'mechanism': row.get('mechanismOfAction', 'Not specified'),
                'indication': 'Multiple indications',  # Open Targets has multiple disease links
                'source': 'open_targets',
                # Add classification fields for compatibility
                'modality': row.get('drugType', 'Unknown'),
                'modality_category': 'biologic' if row.get('drugType') in ['Antibody', 'Protein'] else 'small_molecule',
                'chart_symbol': 'circle',
                'route': 'Unknown',
                'mechanism_summary': row.get('mechanismOfAction', 'Unknown')[:50],
                'mechanism_type': 'inhibitor' if 'inhibitor' in row.get('mechanismOfAction', '').lower() else 'other',
                'is_multispecific': False,
                'targets': [],
                'target_count': 1,
                'sector': 'Unknown',
                'mechanism_detail': row.get('mechanismOfAction', ''),
                'selectivity': 'Unknown',
                'selectivity_description': 'Data from Open Targets',
                'color_code': '#888888',
                '_opentargets_data': row
            }

        return {
            'drugs': list(seen_drugs.values()),
            'total': len(seen_drugs),
            'source': 'open_targets',
            'strategy': 'opentargets_known_drugs',
            'unique_drugs': known_drugs.get('uniqueDrugs', 0),
            'total_disease_drug_pairs': known_drugs.get('count', 0)
        }

    except Exception as e:
        return {
            'drugs': [],
            'total': 0,
            'source': 'open_targets',
            'error': str(e),
            'strategy': 'error'
        }


def extract_drugs_from_clinical_trials(search_func, get_study_func, gene_symbol: str,
                                       target_name: str = None, max_trials: int = 50) -> Dict[str, Any]:
    """
    Extract drug interventions from ClinicalTrials.gov.

    Args:
        search_func: search function from ct_gov_mcp
        get_study_func: get_study function from ct_gov_mcp
        gene_symbol: Gene symbol (e.g., "TNFSF15")
        target_name: Target name for search (e.g., "TNF superfamily member 15")
        max_trials: Maximum trials to process (default: 50)

    Returns:
        dict with drugs list and metadata
    """
    import re

    try:
        # Search for trials mentioning the target
        search_terms = [gene_symbol]
        if target_name:
            # Add common abbreviations/aliases
            if 'TNF' in target_name:
                search_terms.append('TL1A')  # Known alias for TNFSF15

        search_query = ' OR '.join(search_terms)
        search_result = search_func(term=search_query, limit=max_trials)

        # Extract NCT IDs from markdown response
        nct_ids = list(set(re.findall(r'NCT\d{8}', search_result)))

        if not nct_ids:
            return {
                'drugs': [],
                'total': 0,
                'source': 'clinicaltrials_gov',
                'strategy': 'no_trials_found',
                'search_terms': search_terms
            }

        # Extract interventions from each trial
        all_drugs = {}
        for nct in nct_ids[:max_trials]:
            try:
                study = get_study_func(nctId=nct)

                # Extract phase
                phase_match = re.search(r'\*\*Phase:\*\*\s+(\w+)', study)
                phase_str = phase_match.group(1) if phase_match else 'Unknown'

                # Map phase string to number
                phase_map = {'Phase1': 1, 'Phase2': 2, 'Phase3': 3, 'Phase4': 4, 'Na': 0}
                phase_num = phase_map.get(phase_str, 0)

                # Extract status
                status_match = re.search(r'\*\*Status:\*\*\s+([^\n]+)', study)
                status = status_match.group(1) if status_match else 'Unknown'

                # Extract interventions (Drug or Biological)
                interventions = re.findall(r'###\s+(Drug|Biological):\s+([^\n]+)', study)

                for itype, name in interventions:
                    clean_name = name.strip()

                    # Skip placebo
                    if 'placebo' in clean_name.lower():
                        continue

                    # Normalize drug name (remove dosing info for grouping)
                    # e.g., "Induction- PF-06480605 50 mg" -> "PF-06480605"
                    base_name = re.sub(r'\s+\d+\s*mg.*$', '', clean_name)
                    base_name = re.sub(r'^(Induction|Chronic|IV|SC|Oral)[-\s]+', '', base_name)

                    if base_name not in all_drugs:
                        all_drugs[base_name] = {
                            'drug_name': base_name,
                            'drugbank_id': None,  # No standard ID from trials
                            'type': itype,
                            'groups': [],  # Will populate based on phase
                            'phase': 0,
                            'mechanism': f'Targets {gene_symbol}',
                            'indication': 'See clinical trials',
                            'source': 'clinicaltrials_gov',
                            # Add classification fields for compatibility
                            'modality': itype,
                            'modality_category': 'biologic' if itype == 'Biological' else 'small_molecule',
                            'chart_symbol': 'circle',
                            'route': 'Unknown',
                            'mechanism_summary': f'Targets {gene_symbol}',
                            'mechanism_type': 'other',
                            'is_multispecific': False,
                            'targets': [gene_symbol] if gene_symbol else [],
                            'target_count': 1,
                            'sector': 'Unknown',
                            'mechanism_detail': f'Targets {gene_symbol}',
                            'selectivity': 'Unknown',
                            'selectivity_description': 'Data from ClinicalTrials.gov',
                            'color_code': '#888888',
                            'trials': [],
                            'phases': set(),
                            'statuses': set(),
                            '_trial_names': []  # Store variant names
                        }

                    # Update with trial info
                    all_drugs[base_name]['trials'].append(nct)
                    all_drugs[base_name]['phases'].add(phase_num)
                    all_drugs[base_name]['statuses'].add(status)
                    all_drugs[base_name]['_trial_names'].append(clean_name)

                    # Update to highest phase
                    if phase_num > all_drugs[base_name]['phase']:
                        all_drugs[base_name]['phase'] = phase_num

            except Exception as e:
                # Skip trials that fail to parse
                continue

        # Convert to list and assign groups based on phase
        drugs_list = []
        for drug_name, drug_data in all_drugs.items():
            phase = drug_data['phase']

            # Map phase to groups
            if phase == 4:
                drug_data['groups'] = ['approved']
            elif phase == 3:
                drug_data['groups'] = ['investigational']
            elif phase in [1, 2]:
                drug_data['groups'] = ['experimental']
            else:
                drug_data['groups'] = ['other']

            # Convert sets to lists for JSON serialization
            drug_data['phases'] = sorted(list(drug_data['phases']), reverse=True)
            drug_data['statuses'] = list(drug_data['statuses'])

            drugs_list.append(drug_data)

        return {
            'drugs': drugs_list,
            'total': len(drugs_list),
            'source': 'clinicaltrials_gov',
            'strategy': 'trial_intervention_extraction',
            'trials_found': len(nct_ids),
            'trials_processed': min(len(nct_ids), max_trials),
            'search_terms': search_terms
        }

    except Exception as e:
        return {
            'drugs': [],
            'total': 0,
            'source': 'clinicaltrials_gov',
            'error': str(e),
            'strategy': 'error'
        }


def search_drugs_hybrid(
    # DrugBank functions
    drugbank_search_by_target,
    drugbank_get_drug_details,
    drugbank_search_by_indication,
    # Open Targets functions
    opentargets_get_target_details,
    # ClinicalTrials.gov functions
    ctgov_search,
    ctgov_get_study,
    # Target info
    gene_symbol: str,
    target_name: str = None,
    target_id: str = None,  # Ensembl ID for Open Targets
    key_indications: List[str] = None,
    max_drugs: int = 1000
) -> Dict[str, Any]:
    """
    Hybrid drug discovery with 3-tier fallback strategy.

    Strategy:
    1. Try DrugBank (approved + investigational drugs)
    2. If no results, try Open Targets knownDrugs
    3. If still no results, extract from ClinicalTrials.gov

    Args:
        drugbank_search_by_target: DrugBank search_by_target function
        drugbank_get_drug_details: DrugBank get_drug_details function
        drugbank_search_by_indication: DrugBank search_by_indication function
        opentargets_get_target_details: Open Targets get_target_details function
        ctgov_search: ClinicalTrials.gov search function
        ctgov_get_study: ClinicalTrials.gov get_study function
        gene_symbol: Gene symbol (e.g., "TNFSF15")
        target_name: Target name (e.g., "TNF superfamily member 15")
        target_id: Ensembl gene ID (e.g., "ENSG00000181634")
        key_indications: List of disease names from genetic validation
        max_drugs: Maximum drugs to return

    Returns:
        dict with drugs list, total count, and source metadata
    """

    # Tier 1: DrugBank
    drugbank_result = search_drugs_by_target(
        search_by_target_func=drugbank_search_by_target,
        gene_symbol=gene_symbol,
        target_name=target_name,
        search_by_indication_func=drugbank_search_by_indication,
        key_indications=key_indications,
        max_drugs=max_drugs,
        get_drug_details_func=drugbank_get_drug_details
    )

    if drugbank_result['total'] > 0:
        drugbank_result['tier'] = 1
        drugbank_result['source'] = 'drugbank'
        return drugbank_result

    # Tier 2: Open Targets (if we have Ensembl ID)
    if target_id:
        opentargets_result = extract_drugs_from_opentargets(
            get_target_details_func=opentargets_get_target_details,
            target_id=target_id
        )

        if opentargets_result['total'] > 0:
            opentargets_result['tier'] = 2
            return opentargets_result

    # Tier 3: ClinicalTrials.gov
    ctgov_result = extract_drugs_from_clinical_trials(
        search_func=ctgov_search,
        get_study_func=ctgov_get_study,
        gene_symbol=gene_symbol,
        target_name=target_name,
        max_trials=50
    )

    if ctgov_result['total'] > 0:
        ctgov_result['tier'] = 3
        return ctgov_result

    # No drugs found in any source
    return {
        'drugs': [],
        'total': 0,
        'tier': None,
        'source': 'none',
        'strategy': 'no_drugs_found_in_any_source',
        'sources_tried': ['drugbank', 'open_targets' if target_id else None, 'clinicaltrials_gov']
    }
