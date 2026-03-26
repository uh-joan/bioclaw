"""Company Pipeline Breakdown - Main entry point.

Analyzes a pharmaceutical company's drug and/or device development pipeline showing
therapeutic area focus, phase distribution, late-stage assets, and regulatory status.

Core question answered: "What is [COMPANY]'s drug/device pipeline?"

Ported from riot-flames for BioClaw container execution.
MCP servers are called directly via mcp_client.McpClient.

Usage:
    python3 get_company_pipeline_breakdown.py "Eli Lilly"
    python3 get_company_pipeline_breakdown.py "Pfizer" --skip-regulatory
    python3 get_company_pipeline_breakdown.py "Medtronic" --include-devices --no-drugs
"""

import sys
import os
import re
from collections import defaultdict
from typing import Dict, List, Optional, Callable

# Add script directory to path for local imports
_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _script_dir)

# Local imports
from constants import (
    is_non_drug_item,
    strip_formulation_terms,
)
from company_resolution import (
    resolve_company_names,
    attribute_company,
    classify_sponsor_type,
    normalize_company_name,
)
from therapeutic_area_mapping import (
    classify_therapeutic_area,
    classify_trial_therapeutic_area,
    extract_conditions_from_trial,
    get_primary_therapeutic_area,
)
from progress_tracker import create_progress_tracker
from mcp_client import McpClient


def get_company_pipeline_breakdown(
    company: str,
    include_subsidiaries: bool = True,
    skip_regulatory: bool = False,
    max_trials: int = None,
    include_drugs: bool = True,
    include_devices: bool = False,
    include_marketed: bool = True,
    progress_callback: Callable[[int, str], None] = None,
    mcp_funcs: Dict = None,
    ctgov_server: str = "ctgov",
    fda_server: str = "fda",
    ema_server: str = "ema",
) -> dict:
    """
    Analyze a pharmaceutical company's drug and/or device development pipeline.

    Searches ClinicalTrials.gov by lead sponsor to find all active trials,
    then classifies by therapeutic area, phase, and regulatory status.

    Args:
        company: Company name (e.g., "Eli Lilly", "Novo Nordisk", "Medtronic")
        include_subsidiaries: Include acquired company pipelines (default: True)
        skip_regulatory: Skip FDA/EMA approval checks for faster results (default: False)
        max_trials: Maximum trials to analyze (default: None = all)
        include_drugs: Include drug/biologics pipeline (default: True)
        include_devices: Include medical device pipeline (default: False)
        include_marketed: Include FDA-approved marketed products (default: True)
        progress_callback: Optional callback(percent, message) for progress updates

    Returns:
        dict: Comprehensive pipeline analysis including:
            - company: Normalized company name
            - total_active_trials: Count of active drug trials (if include_drugs=True)
            - total_unique_drugs: Count of distinct drug interventions
            - therapeutic_areas: Breakdown by therapeutic area
            - phase_summary: Breakdown by clinical phase
            - late_stage_pipeline: Phase 3+ drugs with details
            - drugs: Drug-level detail
            - collaborations: Partnership analysis
            - device_pipeline: (if include_devices=True) Medical device pipeline
            - marketed_products: (if include_marketed=True) FDA-approved marketed drugs/devices
    """
    # Initialize MCP clients (BioClaw container adaptation)
    # In riot-flames, these were injected via mcp_funcs dict.
    # In BioClaw, we call the MCP servers directly via stdio.
    _ctgov_client = McpClient(ctgov_server)
    _fda_client = McpClient(fda_server)
    _ema_client = McpClient(ema_server)

    try:
        _ctgov_client.connect()
    except Exception as e:
        return {'error': f'ClinicalTrials.gov MCP not available: {e}', 'success': False}

    try:
        _fda_client.connect()
    except Exception:
        pass  # FDA is optional (skip_regulatory)

    try:
        _ema_client.connect()
    except Exception:
        pass  # EMA is optional

    # Wrap MCP calls to match riot-flames function signatures.
    # riot-flames callers pass method="search" or method="suggest" etc.
    # We pass those through to the MCP tool as-is.
    def ct_search(**kwargs):
        method = kwargs.pop("method", "search")
        return _ctgov_client.call("ct_gov_studies", method=method, **kwargs)

    def get_study(**kwargs):
        method = kwargs.pop("method", "get")
        return _ctgov_client.call("ct_gov_studies", method=method, **kwargs)

    def fda_lookup(**kwargs):
        method = kwargs.pop("method", "lookup_drug")
        return _fda_client.call("fda_info", method=method, **kwargs)

    fda_device_lookup = None  # Device lookup not yet implemented

    def ema_search(**kwargs):
        method = kwargs.pop("method", "search_medicines")
        return _ema_client.call("ema_data", method=method, **kwargs)

    # Create progress tracker with mode awareness
    progress = create_progress_tracker(
        callback=progress_callback,
        skip_regulatory=skip_regulatory,
        include_drugs=include_drugs,
        include_devices=include_devices,
        include_marketed=include_marketed,
    )

    pipeline_type = "drug" if include_drugs and not include_devices else "device" if include_devices and not include_drugs else "drug and device"
    print(f"\n🔍 Analyzing {pipeline_type} pipeline for: {company}")
    print("=" * 80)

    # Dynamic step counter for console output
    step_num = [0]  # Use list to allow mutation in nested functions
    def next_step():
        step_num[0] += 1
        return step_num[0]

    progress.start_step('init', f"Resolving company name: {company}")

    # Step 1: Resolve company names
    company_info = resolve_company_names(company, include_subsidiaries, ct_search=ct_search)
    normalized_company = company_info['normalized']
    search_names = company_info['search_names']
    subsidiaries = company_info['subsidiaries']

    print(f"  Normalized: {normalized_company}")
    if subsidiaries:
        print(f"  Including subsidiaries: {', '.join(subsidiaries[:5])}{'...' if len(subsidiaries) > 5 else ''}")
    print(f"  Search names ({len(search_names)}): {', '.join(search_names[:3])}...")

    progress.complete_step(f"Company resolved: {normalized_company}")

    # Initialize variables for drug pipeline
    all_nct_ids = set()
    search_results = {}
    total_trials = 0
    sample_size = 0
    processed_trials = 0
    total_enrollment = 0

    # Data structures for aggregation (initialize empty)
    therapeutic_areas = defaultdict(lambda: {
        'trials': 0,
        'unique_drugs': set(),
        'enrollment': 0,
        'conditions': set(),
        'phase_breakdown': defaultdict(lambda: {'trials': 0, 'drugs': set()}),
    })
    phase_summary = defaultdict(lambda: {
        'trials': 0,
        'drugs': set(),
        'areas': set(),
        'enrollment': 0,
    })
    drugs = defaultdict(lambda: {
        'indications': set(),
        'therapeutic_areas': set(),
        'phases': set(),
        'total_trials': 0,
        'total_enrollment': 0,
        'conditions': [],
        'nct_ids': [],
    })
    collaborations = defaultdict(lambda: {
        'trials': 0,
        'drugs': set(),
        'therapeutic_areas': set(),
    })
    fda_approved_drugs = set()
    ema_approved_drugs = set()

    # Search CT.gov by lead sponsor using partial match (if include_drugs=True)
    nct_id_list = []
    if include_drugs:
        print(f"\n📊 Step {next_step()}: Searching ClinicalTrials.gov for drug trials...")
        progress.start_step('search', "Searching CT.gov for drug trials...")

        # Use complexQuery with AREA[LeadSponsorName] for partial matching
        # This finds all sponsors CONTAINING the company name in a single query
        # Much more efficient than iterating through exact name matches
        progress.report_search_progress(1, f"Searching for sponsors containing '{normalized_company}'...")

        try:
            # Use simple parameter query instead of complexQuery (which causes 400 errors)
            # Search for lead sponsor with drug/biological interventions and active status
            result = ct_search(
                lead=normalized_company,
                studyType="interventional",
                interventionType="drug OR biological",
                status="RECRUITING OR ACTIVE_NOT_RECRUITING",
                pageSize=1000
            )

            result_text = result if isinstance(result, str) else result.get('text', str(result))
            nct_ids = re.findall(r'NCT\d{8}', result_text)
            all_nct_ids.update(nct_ids)

            if nct_ids:
                search_results[normalized_company] = len(nct_ids)

            # Handle pagination
            page_token_match = re.search(r'`pageToken:\s*"([^"]+)"', result_text)
            page = 1
            while page_token_match and page < 10:  # Max 10 pages
                page += 1
                page_token = page_token_match.group(1)
                result = ct_search(
                    lead=normalized_company,
                    studyType="interventional",
                    interventionType="drug OR biological",
                    status="RECRUITING OR ACTIVE_NOT_RECRUITING",
                    pageSize=1000,
                    pageToken=page_token
                )
                result_text = result if isinstance(result, str) else result.get('text', str(result))
                nct_ids = re.findall(r'NCT\d{8}', result_text)
                all_nct_ids.update(nct_ids)
                page_token_match = re.search(r'`pageToken:\s*"([^"]+)"', result_text)

        except Exception as e:
            print(f"    Warning: Error in primary search: {e}")

        # If primary search found nothing, try all discovered/alias names
        # This handles cases where the CT.gov sponsor name differs from common name
        # (e.g., "Moderna" vs "ModernaTX, Inc.", "BioNTech" vs "BioNTech SE")
        if not all_nct_ids and len(search_names) > 1:
            print(f"    Primary search found 0 results, trying {len(search_names) - 1} name variations...")
            for i, lead_name in enumerate(search_names):
                if lead_name == normalized_company:
                    continue  # Already tried
                progress.report_search_progress(i + 1, f"Trying '{lead_name}'...")
                try:
                    result = ct_search(
                        lead=lead_name,
                        studyType="interventional",
                        interventionType="drug OR biological",
                        status="RECRUITING OR ACTIVE_NOT_RECRUITING",
                        pageSize=1000
                    )
                    result_text = result if isinstance(result, str) else result.get('text', str(result))
                    nct_ids = re.findall(r'NCT\d{8}', result_text)
                    all_nct_ids.update(nct_ids)
                    if nct_ids:
                        search_results[lead_name] = len(nct_ids)
                        print(f"    Found {len(nct_ids)} trials via '{lead_name}'")
                except Exception as e2:
                    print(f"    Warning: Error searching for '{lead_name}': {e2}")
                    continue

        # Also search for subsidiaries if they have different base names
        if include_subsidiaries and subsidiaries:
            for sub in subsidiaries:
                # Only search if subsidiary name doesn't contain the main company name
                if normalized_company.lower() not in sub.lower():
                    progress.report_search_progress(1, f"Searching subsidiary '{sub}'...")
                    try:
                        # Use simple parameter query instead of complexQuery
                        result = ct_search(
                            lead=sub,
                            studyType="interventional",
                            interventionType="drug OR biological",
                            status="RECRUITING OR ACTIVE_NOT_RECRUITING",
                            pageSize=1000
                        )
                        result_text = result if isinstance(result, str) else result.get('text', str(result))
                        nct_ids = re.findall(r'NCT\d{8}', result_text)
                        all_nct_ids.update(nct_ids)
                        if nct_ids:
                            search_results[sub] = len(nct_ids)
                    except Exception as e:
                        print(f"    Warning: Error searching for '{sub}': {e}")

        total_trials = len(all_nct_ids)
        nct_id_list = list(all_nct_ids)

        print(f"\n✓ Found {total_trials} active drug trials")
        for name, count in sorted(search_results.items(), key=lambda x: -x[1])[:5]:
            print(f"    {name}: {count} trials")

        progress.complete_step(f"Found {total_trials} active trials")

        # Apply max_trials limit if specified
        if max_trials and total_trials > max_trials:
            import random
            nct_id_list = random.sample(nct_id_list, max_trials)
            print(f"✓ Sampling {max_trials} trials for analysis")

        sample_size = len(nct_id_list)

        # Fetch detailed trial information
        print(f"\n💊 Step {next_step()}: Fetching detailed trial information...")
        progress.start_step('trial_details', f"Fetching details for {sample_size} trials...")

        for i, nct_id in enumerate(nct_id_list):
            # Report progress
            if i % 5 == 0 or i == len(nct_id_list) - 1:
                progress.report_trial_progress(i + 1, sample_size)

            if (i + 1) % 20 == 0:
                print(f"    Processing: {i + 1}/{sample_size} trials...")

            try:
                trial_detail = get_study(nctId=nct_id)
                if not trial_detail:
                    continue

                trial_text = trial_detail if isinstance(trial_detail, str) else str(trial_detail)

                # Post-filter: Skip completed/terminated trials (CT.gov API sometimes returns these)
                status_match = re.search(r'\*\*Status:\*\*\s*(\S+)', trial_text)
                if status_match:
                    trial_status = status_match.group(1).lower()
                    if trial_status in ['completed', 'terminated', 'withdrawn', 'suspended']:
                        continue

                # Extract phase
                phase = _extract_phase(trial_text)
                if not phase:
                    continue

                # Extract conditions and classify therapeutic area
                conditions = extract_conditions_from_trial(trial_text)
                primary_ta = classify_trial_therapeutic_area(trial_text)

                # Extract drugs
                drug_interventions = _extract_drugs_from_trial(trial_text)
                if not drug_interventions:
                    continue

                # Extract drug name mapping from trial title (internal code → marketing name)
                drug_name_mapping = _extract_drug_name_mapping(trial_text)

                # Extract enrollment
                enrollment = _extract_enrollment(trial_text)
                total_enrollment += enrollment

                # Extract collaborators
                collabs = _extract_collaborators(trial_text)

                # Update aggregations
                therapeutic_areas[primary_ta]['trials'] += 1
                therapeutic_areas[primary_ta]['enrollment'] += enrollment
                therapeutic_areas[primary_ta]['conditions'].update(conditions)
                therapeutic_areas[primary_ta]['phase_breakdown'][phase]['trials'] += 1

                phase_summary[phase]['trials'] += 1
                phase_summary[phase]['enrollment'] += enrollment
                phase_summary[phase]['areas'].add(primary_ta)

                for drug_raw in drug_interventions:
                    drug = _clean_drug_name(drug_raw)
                    if not drug or _is_non_drug(drug):
                        continue

                    # Normalize to title case for consistent grouping
                    # Use drug name mapping to convert internal codes to marketing names
                    drug_normalized = _normalize_drug_display_name(drug, drug_name_mapping)

                    # Post-normalization filter: reject names that became too short or noise after mapping
                    if not drug_normalized or len(drug_normalized.strip()) <= 2 or _is_non_drug(drug_normalized):
                        continue

                    therapeutic_areas[primary_ta]['unique_drugs'].add(drug_normalized)
                    therapeutic_areas[primary_ta]['phase_breakdown'][phase]['drugs'].add(drug_normalized)
                    phase_summary[phase]['drugs'].add(drug_normalized)

                    drugs[drug_normalized]['indications'].update(conditions)
                    drugs[drug_normalized]['therapeutic_areas'].add(primary_ta)
                    drugs[drug_normalized]['phases'].add(phase)
                    drugs[drug_normalized]['total_trials'] += 1
                    drugs[drug_normalized]['total_enrollment'] += enrollment
                    drugs[drug_normalized]['nct_ids'].append(nct_id)

                for collab in collabs:
                    collaborations[collab]['trials'] += 1
                    collaborations[collab]['drugs'].update(drug_interventions)
                    collaborations[collab]['therapeutic_areas'].add(primary_ta)

                processed_trials += 1

            except Exception as e:
                continue

        print(f"\n✓ Processed {processed_trials} trials with drug interventions")
        print(f"✓ Total unique drugs (pre-dedup): {len(drugs)}")
        print(f"✓ Target enrollment: {total_enrollment:,} patients")

        # Merge dose/formulation variants (e.g., "Etavopivat A" + "Etavopivat B" → "Etavopivat")
        drugs, variant_merges = _merge_drug_variants(drugs)
        if variant_merges:
            print(f"✓ Merged {variant_merges} dose/formulation variants → {len(drugs)} unique drugs")
            # Also update TA and phase sets to reflect merged names
            for ta_name, ta_data in therapeutic_areas.items():
                ta_data['unique_drugs'] = _apply_variant_map_to_set(ta_data['unique_drugs'], drugs)
                for phase_key, phase_data in ta_data['phase_breakdown'].items():
                    phase_data['drugs'] = _apply_variant_map_to_set(phase_data['drugs'], drugs)
            for phase_key, phase_data in phase_summary.items():
                phase_data['drugs'] = _apply_variant_map_to_set(phase_data['drugs'], drugs)
        else:
            print(f"✓ Total unique drugs: {len(drugs)}")

        progress.complete_step(f"Processed {processed_trials} trials, {len(drugs)} drugs")

        # Regulatory cross-check (optional)
        if skip_regulatory:
            print(f"\n🏛️  Step {next_step()}: Skipping regulatory checks (skip_regulatory=True)")
            progress.start_step('regulatory', "Skipping regulatory checks...")
            progress.complete_step()
        else:
            print(f"\n🏛️  Step {next_step()}: Cross-checking FDA/EMA for approved drugs...")
            progress.start_step('regulatory', "Checking regulatory approvals...")

            drug_list = list(drugs.keys())
            total_drugs_count = len(drug_list)

            for i, drug_name in enumerate(drug_list):
                if i % 3 == 0:
                    progress.report_regulatory_progress(i + 1, total_drugs_count)

                if (i + 1) % 10 == 0:
                    print(f"    Checking: {i + 1}/{total_drugs_count} drugs...")

                normalized = _normalize_drug_name(drug_name)

                # FDA check
                try:
                    fda_result = fda_lookup(
                        search_term=normalized,
                        search_type='general',
                        limit=1
                    )
                    if fda_result and fda_result.get('data', {}).get('results'):
                        fda_approved_drugs.add(drug_name)
                except Exception:
                    pass

                # EMA check
                try:
                    ema_result = ema_search(method="search_medicines", active_substance=normalized, limit=1)
                    if ema_result and ema_result.get('results'):
                        ema_approved_drugs.add(drug_name)
                except Exception:
                    pass

            print(f"✓ FDA approved: {len(fda_approved_drugs)} drugs")
            print(f"✓ EMA approved: {len(ema_approved_drugs)} drugs")
            progress.complete_step(f"Regulatory complete: {len(fda_approved_drugs)} FDA, {len(ema_approved_drugs)} EMA")
    else:
        # include_drugs=False: skip drug pipeline entirely
        print(f"\n📊 Skipping drug pipeline (include_drugs=False)")

    # Device pipeline (if enabled)
    device_pipeline_result = None
    if include_devices:
        device_pipeline_result = _get_device_pipeline(
            search_names=search_names,
            normalized_company=normalized_company,
            max_trials=max_trials,
            skip_regulatory=skip_regulatory,
            progress=progress,
            step_counter=next_step,
            ct_search=ct_search,
            get_study=get_study,
            fda_device_lookup=fda_device_lookup,
        )

    # Marketed products (if enabled)
    marketed_products_result = None
    if include_marketed:
        marketed_products_result = _get_marketed_products(
            search_names=search_names,
            normalized_company=normalized_company,
            progress=progress,
            step_counter=next_step,
            fda_lookup=fda_lookup,
            fda_device_lookup=fda_device_lookup,
        )

    # Final step: Build output structure
    print(f"\n📈 Step {next_step()}: Building pipeline analysis...")
    progress.start_step('aggregation', "Building output structure...")

    # Format therapeutic areas
    ta_output = {}
    for ta_name, ta_data in therapeutic_areas.items():
        phase_breakdown = {}
        for phase, phase_data in ta_data['phase_breakdown'].items():
            phase_breakdown[phase] = {
                'trials': phase_data['trials'],
                'drugs': sorted(list(phase_data['drugs']))[:10],
            }

        ta_output[ta_name] = {
            'trials': ta_data['trials'],
            'unique_drugs': len(ta_data['unique_drugs']),
            'enrollment': ta_data['enrollment'],
            'phase_breakdown': phase_breakdown,
            'sample_conditions': sorted(list(ta_data['conditions']))[:5],
        }

    progress.update_step(0.3, "Building phase summary...")

    # Format phase summary
    phase_output = {}
    for phase in ['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4']:
        if phase in phase_summary:
            phase_data = phase_summary[phase]
            phase_output[phase] = {
                'trials': phase_data['trials'],
                'drugs': len(phase_data['drugs']),
                'areas': sorted(list(phase_data['areas'])),
                'enrollment': phase_data['enrollment'],
            }
        else:
            phase_output[phase] = {'trials': 0, 'drugs': 0, 'areas': [], 'enrollment': 0}

    progress.update_step(0.5, "Building late-stage pipeline...")

    # Build late-stage pipeline (Phase 3+)
    late_stage = []
    for drug_name, drug_data in drugs.items():
        if 'Phase 3' in drug_data['phases'] or 'Phase 4' in drug_data['phases']:
            highest_phase = 'Phase 4' if 'Phase 4' in drug_data['phases'] else 'Phase 3'
            late_stage.append({
                'drug': drug_name,
                'indications': sorted(list(drug_data['indications']))[:3],
                'therapeutic_areas': sorted(list(drug_data['therapeutic_areas'])),
                'phase': highest_phase,
                'trials': drug_data['total_trials'],
                'enrollment': drug_data['total_enrollment'],
                'fda_approved': drug_name in fda_approved_drugs,
                'ema_approved': drug_name in ema_approved_drugs,
            })

    # Sort by enrollment (proxy for investment)
    late_stage.sort(key=lambda x: -x['enrollment'])

    progress.update_step(0.7, "Building drug details...")

    # Phase ranking for sorting (higher = more advanced)
    phase_rank = {'Phase 4': 4, 'Phase 3': 3, 'Phase 2': 2, 'Phase 1': 1}

    # Format drug details (sorted by highest phase, then by trials)
    drugs_with_phase = []
    for drug_name, drug_data in drugs.items():
        highest_phase = _get_highest_phase(drug_data['phases'])
        drugs_with_phase.append((drug_name, drug_data, phase_rank.get(highest_phase, 0)))

    # Sort by phase rank (descending), then by trials (descending) - include ALL drugs
    drugs_sorted = sorted(drugs_with_phase, key=lambda x: (-x[2], -x[1]['total_trials']))

    drugs_output = {}
    for drug_name, drug_data, _ in drugs_sorted:
        highest_phase = _get_highest_phase(drug_data['phases'])
        drugs_output[drug_name] = {
            'indications': sorted(list(drug_data['indications']))[:5],
            'therapeutic_areas': sorted(list(drug_data['therapeutic_areas'])),
            'phases': sorted(list(drug_data['phases'])),
            'highest_phase': highest_phase,
            'total_trials': drug_data['total_trials'],
            'total_enrollment': drug_data['total_enrollment'],
            'fda_approved': drug_name in fda_approved_drugs,
            'ema_approved': drug_name in ema_approved_drugs,
        }

    progress.update_step(0.9, "Building collaboration details...")

    # Format collaborations (top partners)
    collab_sorted = sorted(
        [(k, v) for k, v in collaborations.items()
         if k.lower() != normalized_company.lower()],
        key=lambda x: -x[1]['trials']
    )[:10]

    collab_output = []
    for partner, collab_data in collab_sorted:
        collab_output.append({
            'partner': partner,
            'trials': collab_data['trials'],
            'drugs': sorted(list(collab_data['drugs']))[:5],
            'therapeutic_areas': sorted(list(collab_data['therapeutic_areas'])),
        })

    progress.complete_step("Analysis complete!")

    # Cleanup MCP clients
    _ctgov_client.close()
    _fda_client.close()
    _ema_client.close()

    # Build final output
    return {
        # Company identification
        'company': normalized_company,
        'company_input': company,
        'aliases_matched': search_results,
        'subsidiaries_included': subsidiaries if include_subsidiaries else [],

        # Search options (for template rendering)
        'include_drugs': include_drugs,
        'include_devices': include_devices,

        # Pipeline summary
        'total_active_trials': total_trials,
        'sample_size': sample_size,
        'trials_analyzed': processed_trials,
        'total_unique_drugs': len(drugs),
        'total_enrollment': total_enrollment,
        'therapeutic_area_count': len(therapeutic_areas),

        # Primary view: Therapeutic area breakdown
        'therapeutic_areas': ta_output,

        # Secondary view: Phase-first breakdown
        'phase_summary': phase_output,

        # Late-stage pipeline (Phase 3+)
        'late_stage_pipeline': late_stage,  # All late-stage drugs

        # Drug-level detail
        'drugs': drugs_output,

        # Partnership analysis
        'collaborations': {
            'total_collaborator_trials': sum(c['trials'] for c in collab_output),
            'key_partners': collab_output,
        },

        # Regulatory summary
        'regulatory_summary': {
            'fda_approved_count': len(fda_approved_drugs),
            'ema_approved_count': len(ema_approved_drugs),
            'fda_approved_drugs': sorted(list(fda_approved_drugs)),
            'ema_approved_drugs': sorted(list(ema_approved_drugs)),
        },

        # Medical device pipeline (if requested)
        'device_pipeline': device_pipeline_result,

        # Marketed products (FDA-approved, if requested)
        'marketed_products': marketed_products_result,
    }


# Marketed products function

def _get_marketed_products(
    search_names: List[str],
    normalized_company: str,
    progress: 'ProgressTracker' = None,
    step_counter: Callable[[], int] = None,
    fda_lookup = None,
    fda_device_lookup = None,
) -> dict:
    """
    Get FDA-approved marketed drugs and devices for a company.

    Uses FDA OpenFDA API to retrieve brand names of approved drugs
    and devices currently on market. Complements pipeline data (in development)
    with commercial products (already approved).

    Returns:
        dict: Marketed products including:
            - drugs: FDA-approved marketed drugs
            - devices: FDA-cleared (510k) and FDA-approved (PMA) devices
    """
    step_label = f"Step {step_counter()}: " if step_counter else ""
    print(f"\n🏷️  {step_label}Fetching FDA-approved marketed products...")
    if progress:
        progress.start_step('marketed', "Fetching FDA-approved marketed products...")

    marketed_drugs = []
    marketed_devices_510k = []
    marketed_devices_pma = []

    # Try multiple company name variations for drug search
    for company_name in search_names[:3]:  # Limit to first 3 names
        try:
            # Search for FDA-approved drugs by manufacturer
            result = fda_lookup(
                search_term=company_name,
                search_type='general',
                openfda_manufacturer_name=company_name,
                count='openfda.brand_name.exact',
                limit=100
            )

            if result and result.get('data', {}).get('results'):
                for item in result['data']['results']:
                    brand_name = item.get('term', '')
                    if brand_name and brand_name not in [d['name'] for d in marketed_drugs]:
                        marketed_drugs.append({
                            'name': brand_name,
                            'count': item.get('count', 1),
                        })

            if marketed_drugs:
                break  # Found results, no need to try other names

        except Exception as e:
            continue

    # Deduplicate and clean up drug names (handle formulation variants)
    marketed_drugs = _dedupe_marketed_drugs(marketed_drugs)

    print(f"  ✓ Found {len(marketed_drugs)} marketed drug brands")
    if progress:
        progress.update_step(0.3, f"Found {len(marketed_drugs)} marketed drug brands")

    # Search for FDA-cleared devices (510k)
    for company_name in search_names[:2]:
        # Sanitize company name for FDA API (replace special chars that cause validation errors)
        # Replace & with 'and' to preserve search semantics (e.g., "Johnson & Johnson" -> "Johnson and Johnson")
        fda_name = company_name.replace('&', 'and').replace(',', '').strip()
        fda_name = ' '.join(fda_name.split())
        try:
            result = fda_device_lookup(
                search=f'applicant:{fda_name}',
                search_type='device_510k',
                limit=100
            )

            if result and result.get('data', {}).get('results'):
                seen_device_names = set()
                for item in result['data']['results']:
                    device_name = item.get('device_name', '') or item.get('openfda', {}).get('device_name', '')
                    if device_name and device_name.lower() not in seen_device_names:
                        seen_device_names.add(device_name.lower())
                        marketed_devices_510k.append({
                            'name': device_name,
                            'product_code': item.get('product_code', ''),
                            'clearance_date': item.get('decision_date', ''),
                        })

            if marketed_devices_510k:
                break

        except Exception as e:
            continue

    print(f"  ✓ Found {len(marketed_devices_510k)} 510(k)-cleared devices")
    if progress:
        progress.update_step(0.6, f"Found {len(marketed_devices_510k)} 510(k)-cleared devices")

    # Search for FDA-approved devices (PMA)
    for company_name in search_names[:2]:
        # Sanitize company name for FDA API (replace special chars that cause validation errors)
        # Replace & with 'and' to preserve search semantics (e.g., "Johnson & Johnson" -> "Johnson and Johnson")
        fda_name = company_name.replace('&', 'and').replace(',', '').strip()
        fda_name = ' '.join(fda_name.split())
        try:
            result = fda_device_lookup(
                search=f'applicant:{fda_name}',
                search_type='device_pma',
                limit=100
            )

            if result and result.get('data', {}).get('results'):
                seen_trade_names = set()
                for item in result['data']['results']:
                    trade_name = item.get('trade_name', '')
                    generic_name = item.get('generic_name', '')
                    # Use trade_name if available, otherwise generic_name
                    display_name = trade_name or generic_name
                    if display_name:
                        # PMA has many supplements - dedupe by trade_name
                        key = display_name.lower().split(',')[0].strip()  # Take first name if comma-separated
                        if key not in seen_trade_names:
                            seen_trade_names.add(key)
                            marketed_devices_pma.append({
                                'name': display_name.split(',')[0].strip(),  # Clean name
                                'generic_name': generic_name,
                                'advisory_committee': item.get('advisory_committee_description', ''),
                                'approval_date': item.get('decision_date', ''),
                            })

            if marketed_devices_pma:
                break

        except Exception as e:
            continue

    print(f"  ✓ Found {len(marketed_devices_pma)} PMA-approved devices")
    if progress:
        progress.complete_step(f"Found {len(marketed_drugs)} drugs, {len(marketed_devices_510k) + len(marketed_devices_pma)} devices")

    # Sort by count (drugs) or date (devices)
    marketed_drugs.sort(key=lambda x: -x.get('count', 1))
    marketed_devices_pma.sort(key=lambda x: x.get('approval_date', ''), reverse=True)
    marketed_devices_510k.sort(key=lambda x: x.get('clearance_date', ''), reverse=True)

    # Aggregate PMA devices by category (advisory_committee)
    pma_category_counts = {}
    for device in marketed_devices_pma:
        category = device.get('advisory_committee', '') or 'Unknown'
        if category not in pma_category_counts:
            pma_category_counts[category] = 0
        pma_category_counts[category] += 1

    # Sort categories by count descending
    pma_categories_sorted = sorted(
        [{'category': k, 'count': v} for k, v in pma_category_counts.items()],
        key=lambda x: -x['count']
    )

    return {
        'drugs': {
            'total_count': len(marketed_drugs),
            'brands': marketed_drugs[:50],  # Limit to top 50 for display
        },
        'devices': {
            'cleared_510k_count': len(marketed_devices_510k),
            'approved_pma_count': len(marketed_devices_pma),
            'cleared_510k': marketed_devices_510k[:30],  # Limit for display
            'approved_pma': marketed_devices_pma[:30],
            'pma_by_category': pma_categories_sorted,  # Category breakdown with counts
        },
    }


def _get_drug_base_name(drug_name: str) -> Optional[str]:
    """Extract the base drug name by stripping variant suffixes.

    Merges entries like:
    - "Etavopivat A", "Etavopivat B", "Etavopivat C" → "Etavopivat"
    - "BNT162B2 Original", "BNT162B2 Omicron-Adapted" → "BNT162B2"
    - "Semaglutide Oral", "Semaglutide Injectable" → "Semaglutide"

    Returns the base name if a variant suffix was found, None otherwise.
    """
    if not drug_name:
        return None

    # Don't merge compound codes that differ in their code suffix (e.g., PF-06882961 vs PF-07055480)
    if re.match(r'^[A-Z]{2,5}[-\s]?\d', drug_name):
        # For codes, only strip trailing descriptors after a space
        # e.g., "BNT162B2 Original" → "BNT162B2", but NOT "PF-06882961" → "PF"
        m = re.match(r'^([A-Z]{2,5}[-\s]?\d[\w-]*)\s+(.+)$', drug_name)
        if m:
            suffix = m.group(2).lower()
            # Only strip if suffix is a variant descriptor, not part of the code
            variant_descriptors = {
                'original', 'adapted', 'omicron', 'delta', 'bivalent', 'monovalent',
                'updated', 'modified', 'next-gen', 'next gen', 'variant',
                'vaccine', 'booster', 'adjuvanted', 'unadjuvanted',
            }
            # Also match pure numeric suffixes like "BNT162B2 10" or "BNT162B2 3"
            if suffix in variant_descriptors or suffix.endswith('-adapted') or suffix.isdigit():
                return m.group(1)
        return None

    # For INN-style names: strip single-letter suffixes or short variant tags
    # "Etavopivat A" → "Etavopivat", "Ritlecitinib B" → "Ritlecitinib"
    m = re.match(r'^(.+?)\s+([A-Z])$', drug_name)
    if m and len(m.group(1)) >= 4:
        return m.group(1)

    # Strip formulation route suffixes: "Semaglutide Oral" → "Semaglutide"
    route_suffixes = {'oral', 'injectable', 'subcutaneous', 'intravenous', 'topical',
                      'inhaled', 'nasal', 'ophthalmic', 'transdermal'}
    words = drug_name.rsplit(None, 1)
    if len(words) == 2 and words[1].lower() in route_suffixes and len(words[0]) >= 4:
        return words[0]

    return None


def _merge_drug_variants(drugs: dict) -> tuple:
    """Merge dose/formulation variant drug entries into their base drug.

    Args:
        drugs: defaultdict of drug_name → {indications, phases, total_trials, ...}

    Returns:
        (merged_drugs dict, count of merges performed)
    """
    # Build a map: variant_name → base_name
    variant_to_base = {}
    all_drug_names = list(drugs.keys())

    for name in all_drug_names:
        base = _get_drug_base_name(name)
        if base and base != name:
            # Only merge if the base name also exists as a separate entry OR
            # if multiple variants share the same base
            variant_to_base[name] = base

    # Group variants by base name
    base_groups = defaultdict(list)
    for variant, base in variant_to_base.items():
        base_groups[base].append(variant)

    # Only merge if the base exists as its own entry OR there are 2+ variants
    merge_count = 0
    for base, variants in base_groups.items():
        if base not in drugs and len(variants) < 2:
            # Single variant with no base entry — don't merge (could be a real distinct drug)
            continue

        # Create base entry if it doesn't exist
        if base not in drugs:
            drugs[base] = {
                'indications': set(),
                'therapeutic_areas': set(),
                'phases': set(),
                'total_trials': 0,
                'total_enrollment': 0,
                'conditions': [],
                'nct_ids': [],
            }

        # Merge all variants into base
        for variant in variants:
            if variant in drugs:
                variant_data = drugs[variant]
                drugs[base]['indications'].update(variant_data['indications'])
                drugs[base]['therapeutic_areas'].update(variant_data['therapeutic_areas'])
                drugs[base]['phases'].update(variant_data['phases'])
                drugs[base]['total_trials'] += variant_data['total_trials']
                drugs[base]['total_enrollment'] += variant_data['total_enrollment']
                drugs[base]['nct_ids'].extend(variant_data['nct_ids'])
                del drugs[variant]
                merge_count += 1

    return drugs, merge_count


def _apply_variant_map_to_set(name_set: set, merged_drugs: dict) -> set:
    """Update a set of drug names to reflect merged variants.

    Names that were merged away get replaced with their base name.
    """
    result = set()
    for name in name_set:
        if name in merged_drugs:
            result.add(name)
        else:
            # This name was merged — find its base by checking _get_drug_base_name
            base = _get_drug_base_name(name)
            if base and base in merged_drugs:
                result.add(base)
            else:
                result.add(name)  # Keep as-is if no merge happened
    return result


def _dedupe_marketed_drugs(drugs: List[dict]) -> List[dict]:
    """
    Deduplicate marketed drugs by combining formulation variants.

    For example, "HUMALOG KWIKPEN", "HUMALOG MIX75/25", "HUMALOG" should all
    be grouped under "HUMALOG" with combined counts.
    """
    # Group by base name (first word or two)
    base_groups = {}

    for drug in drugs:
        name = drug['name']
        count = drug.get('count', 1)

        # Extract base name (handle multi-word brand names)
        words = name.split()
        if len(words) == 1:
            base = name
        else:
            # Check if second word is a formulation term
            formulation_terms = ['KWIKPEN', 'PEN', 'MIX', 'JUNIOR', 'TEMPO', 'SOLOSTAR', 'FLEXPEN', 'FLEXTOUCH']
            if words[1].upper() in formulation_terms:
                base = words[0]
            else:
                # Keep first two words as base
                base = ' '.join(words[:2])

        base_upper = base.upper()

        if base_upper not in base_groups:
            base_groups[base_upper] = {
                'name': base,  # Use proper casing from first occurrence
                'count': 0,
                'variants': [],
            }

        base_groups[base_upper]['count'] += count
        if name != base:
            base_groups[base_upper]['variants'].append(name)

    # Convert back to list
    result = []
    for base_name, data in base_groups.items():
        result.append({
            'name': data['name'],
            'count': data['count'],
            'variants': data['variants'][:3] if data['variants'] else [],  # Show up to 3 variants
        })

    return result


# Device pipeline function

def _get_device_pipeline(
    search_names: List[str],
    normalized_company: str,
    max_trials: int = None,
    skip_regulatory: bool = False,
    progress: 'ProgressTracker' = None,
    step_counter: Callable[[], int] = None,
    ct_search = None,
    get_study = None,
    fda_device_lookup = None,
) -> dict:
    """
    Analyze a company's medical device pipeline separately from drugs.

    Device trials use different terminology:
    - Feasibility = Early development (like Phase 1)
    - Pivotal = Late development (like Phase 3)
    - Post-Market = Surveillance (like Phase 4)

    Returns:
        dict: Device pipeline analysis including:
            - total_trials: Count of active device trials
            - total_devices: Count of distinct devices
            - stage_summary: Breakdown by development stage
            - therapeutic_areas: Breakdown by therapeutic area
            - devices: Device-level detail
            - late_stage_devices: Pivotal/post-market devices
            - regulatory_summary: FDA 510(k)/PMA approval status
    """
    step_label = f"Step {step_counter()}: " if step_counter else ""
    print(f"\n🔧 {step_label}Searching for medical device trials...")
    if progress:
        progress.start_step('device_search', "Searching CT.gov for device trials...")

    # Search CT.gov for device trials using partial sponsor name match
    all_device_nct_ids = set()
    device_search_results = {}

    try:
        # Use simple parameter query instead of complexQuery
        result = ct_search(
            lead=normalized_company,
            studyType="interventional",
            interventionType="device",
            status="RECRUITING OR ACTIVE_NOT_RECRUITING",
            pageSize=1000
        )

        result_text = result if isinstance(result, str) else result.get('text', str(result))
        nct_ids = re.findall(r'NCT\d{8}', result_text)
        all_device_nct_ids.update(nct_ids)

        if nct_ids:
            device_search_results[normalized_company] = len(nct_ids)

        # Handle pagination
        page_token_match = re.search(r'`pageToken:\s*"([^"]+)"', result_text)
        page = 1
        while page_token_match and page < 5:  # Max 5 pages for devices
            page += 1
            page_token = page_token_match.group(1)
            result = ct_search(
                lead=normalized_company,
                studyType="interventional",
                interventionType="device",
                status="RECRUITING OR ACTIVE_NOT_RECRUITING",
                pageSize=1000,
                pageToken=page_token
            )
            result_text = result if isinstance(result, str) else result.get('text', str(result))
            nct_ids = re.findall(r'NCT\d{8}', result_text)
            all_device_nct_ids.update(nct_ids)
            page_token_match = re.search(r'`pageToken:\s*"([^"]+)"', result_text)

    except Exception as e:
        print(f"    Warning: Error in device search: {e}")
        # Fallback to individual name searches
        for lead_name in search_names:
            try:
                result = ct_search(
                    lead=lead_name,
                    studyType="interventional",
                    interventionType="device",
                    status="recruiting OR active_not_recruiting",
                    pageSize=1000
                )
                result_text = result if isinstance(result, str) else result.get('text', str(result))
                nct_ids = re.findall(r'NCT\d{8}', result_text)
                all_device_nct_ids.update(nct_ids)
                if nct_ids:
                    device_search_results[lead_name] = len(nct_ids)
            except Exception as e2:
                continue

    total_device_trials = len(all_device_nct_ids)
    device_nct_list = list(all_device_nct_ids)

    if total_device_trials == 0:
        print("  No device trials found")
        if progress:
            progress.complete_step("No device trials found")
        return {
            'total_trials': 0,
            'total_devices': 0,
            'stage_summary': {},
            'therapeutic_areas': {},
            'devices': {},
            'late_stage_devices': [],
        }

    print(f"✓ Found {total_device_trials} active device trials")
    if progress:
        progress.complete_step(f"Found {total_device_trials} device trials")

    # Apply max_trials limit if specified
    if max_trials and total_device_trials > max_trials:
        import random
        device_nct_list = random.sample(device_nct_list, min(max_trials, 50))

    # Fetch device trial details
    step_label2 = f"Step {step_counter()}: " if step_counter else ""
    print(f"\n💊 {step_label2}Fetching details for {len(device_nct_list)} device trials...")
    if progress:
        progress.start_step('device_trials', f"Fetching details for {len(device_nct_list)} device trials...")

    # Data structures for device aggregation
    device_therapeutic_areas = defaultdict(lambda: {
        'trials': 0,
        'devices': set(),
        'enrollment': 0,
        'conditions': set(),
    })

    stage_summary = defaultdict(lambda: {
        'trials': 0,
        'devices': set(),
        'enrollment': 0,
    })

    devices = defaultdict(lambda: {
        'indications': set(),
        'therapeutic_areas': set(),
        'stages': set(),
        'total_trials': 0,
        'total_enrollment': 0,
        'nct_ids': [],
    })

    total_device_enrollment = 0
    processed_device_trials = 0

    for i, nct_id in enumerate(device_nct_list):
        # Report progress every 5 trials or at end
        if progress and (i % 5 == 0 or i == len(device_nct_list) - 1):
            progress.report_trial_progress(i + 1, len(device_nct_list))
        if (i + 1) % 10 == 0:
            print(f"    Processing: {i + 1}/{len(device_nct_list)} device trials...")

        try:
            trial_detail = get_study(nctId=nct_id)
            if not trial_detail:
                continue

            trial_text = trial_detail if isinstance(trial_detail, str) else str(trial_detail)

            # Extract device stage (different from drug phases)
            stage = _extract_device_stage(trial_text)
            if not stage:
                stage = 'Unknown'

            # Extract conditions and classify therapeutic area
            conditions = extract_conditions_from_trial(trial_text)
            primary_ta = classify_trial_therapeutic_area(trial_text)

            # Extract device names
            device_names = _extract_devices_from_trial(trial_text)
            if not device_names:
                continue

            # Extract enrollment
            enrollment = _extract_enrollment(trial_text)
            total_device_enrollment += enrollment

            # Update aggregations
            device_therapeutic_areas[primary_ta]['trials'] += 1
            device_therapeutic_areas[primary_ta]['enrollment'] += enrollment
            device_therapeutic_areas[primary_ta]['conditions'].update(conditions)

            stage_summary[stage]['trials'] += 1
            stage_summary[stage]['enrollment'] += enrollment

            for device_name in device_names:
                device_clean = _clean_device_name(device_name)
                if not device_clean:
                    continue

                device_therapeutic_areas[primary_ta]['devices'].add(device_clean)
                stage_summary[stage]['devices'].add(device_clean)

                devices[device_clean]['indications'].update(conditions)
                devices[device_clean]['therapeutic_areas'].add(primary_ta)
                devices[device_clean]['stages'].add(stage)
                devices[device_clean]['total_trials'] += 1
                devices[device_clean]['total_enrollment'] += enrollment
                devices[device_clean]['nct_ids'].append(nct_id)

            processed_device_trials += 1

        except Exception as e:
            continue

    print(f"✓ Processed {processed_device_trials} device trials, {len(devices)} unique devices")
    if progress:
        progress.complete_step(f"Processed {processed_device_trials} trials, {len(devices)} devices")

    # Build output structure
    ta_output = {}
    for ta_name, ta_data in device_therapeutic_areas.items():
        ta_output[ta_name] = {
            'trials': ta_data['trials'],
            'unique_devices': len(ta_data['devices']),
            'enrollment': ta_data['enrollment'],
            'sample_conditions': sorted(list(ta_data['conditions']))[:5],
        }

    # Stage summary with proper ordering
    stage_output = {}
    for stage_name in ['Feasibility', 'Pivotal', 'Post-Market', 'Unknown']:
        if stage_name in stage_summary:
            stage_data = stage_summary[stage_name]
            stage_output[stage_name] = {
                'trials': stage_data['trials'],
                'devices': len(stage_data['devices']),
                'enrollment': stage_data['enrollment'],
            }

    # FDA device approval check (510(k) and PMA)
    # Strategy: Search FDA by COMPANY NAME to get all their approved devices,
    # then fuzzy match against CT.gov device names
    fda_cleared_devices = set()  # 510(k) cleared
    fda_approved_devices = set()  # PMA approved

    if not skip_regulatory and devices:
        step_label3 = f"Step {step_counter()}: " if step_counter else ""
        print(f"\n🏛️  {step_label3}Checking FDA device approvals...")
        if progress:
            progress.start_step('device_regulatory', "Checking FDA device approvals...")
        unique_device_names = list(devices.keys())

        # Common words to ignore in matching (too generic)
        STOP_WORDS = {
            'system', 'device', 'catheter', 'implant', 'implantable', 'medical',
            'therapy', 'treatment', 'procedure', 'the', 'and', 'for', 'with',
            'lead', 'pulse', 'generator', 'model', 'models', 'kit', 'set',
            'permanent', 'temporary', 'external', 'internal', 'left', 'right',
        }

        def normalize_for_match(name: str) -> set:
            """Extract key words for fuzzy matching"""
            name = name.lower().replace('™', '').replace('®', '')
            # Keep meaningful words (4+ chars, not stop words)
            words = [w.strip() for w in re.split(r'[\s\-/,&()]+', name)
                     if len(w.strip()) >= 4 and w.strip() not in STOP_WORDS]
            return set(words)

        device_keywords = {dn: normalize_for_match(dn) for dn in unique_device_names}

        # Sanitize company name for FDA API (replace special chars that cause validation errors)
        # Replace & with 'and' to preserve search semantics (e.g., "Johnson & Johnson" -> "Johnson and Johnson")
        fda_search_name = normalized_company.replace('&', 'and').replace(',', '').strip()
        # Also remove double spaces that might result from character removal
        fda_search_name = ' '.join(fda_search_name.split())

        # Search FDA 510(k) by company name (applicant field)
        try:
            result_510k = fda_device_lookup(
                search=f'applicant:{fda_search_name}',
                search_type='device_510k',
                limit=100  # Get more results for matching
            )
            if result_510k.get('success') and result_510k.get('data', {}).get('results'):
                fda_510k_names = []
                for item in result_510k['data']['results']:
                    fda_device_name = item.get('device_name', '')
                    if fda_device_name:
                        fda_510k_names.append(fda_device_name.lower())
                    # Also check openfda.device_name if available
                    openfda = item.get('openfda', {})
                    if openfda.get('device_name'):
                        fda_510k_names.append(openfda['device_name'].lower())

                # Match CT.gov devices against FDA 510(k) devices
                for ct_device, ct_keywords in device_keywords.items():
                    if not ct_keywords:
                        continue
                    for fda_name in fda_510k_names:
                        fda_words = normalize_for_match(fda_name)
                        # Match criteria (relaxed):
                        # 1. At least 1 significant word (6+ chars) overlaps, OR
                        # 2. At least 2 words (4+ chars) overlap, OR
                        # 3. A distinctive keyword appears as substring
                        overlap = ct_keywords & fda_words
                        long_overlap = [w for w in overlap if len(w) >= 6]
                        if (len(long_overlap) >= 1 or
                            len(overlap) >= 2 or
                            any(kw in fda_name for kw in ct_keywords if len(kw) >= 6)):
                            fda_cleared_devices.add(ct_device)
                            break
        except Exception as e:
            print(f"  Warning: 510(k) lookup failed: {e}")

        # Search FDA PMA by company name (use sanitized name)
        try:
            result_pma = fda_device_lookup(
                search=f'applicant:{fda_search_name}',
                search_type='device_pma',
                limit=100
            )
            if result_pma.get('success') and result_pma.get('data', {}).get('results'):
                fda_pma_names = []
                for item in result_pma['data']['results']:
                    # PMA has both generic_name and trade_name - use both
                    generic = item.get('generic_name', '')
                    trade = item.get('trade_name', '')
                    if generic:
                        fda_pma_names.append(generic.lower())
                    if trade:
                        fda_pma_names.append(trade.lower())

                # Match CT.gov devices against FDA PMA devices
                for ct_device, ct_keywords in device_keywords.items():
                    if not ct_keywords:
                        continue
                    for fda_name in fda_pma_names:
                        fda_words = normalize_for_match(fda_name)
                        overlap = ct_keywords & fda_words
                        long_overlap = [w for w in overlap if len(w) >= 6]
                        if (len(long_overlap) >= 1 or
                            len(overlap) >= 2 or
                            any(kw in fda_name for kw in ct_keywords if len(kw) >= 6)):
                            fda_approved_devices.add(ct_device)
                            break
        except Exception as e:
            print(f"  Warning: PMA lookup failed: {e}")

        print(f"✓ FDA 510(k) cleared: {len(fda_cleared_devices)} devices")
        print(f"✓ FDA PMA approved: {len(fda_approved_devices)} devices")
        if progress:
            progress.complete_step(f"FDA checks: {len(fda_cleared_devices)} cleared, {len(fda_approved_devices)} approved")

    # Build late-stage devices (Pivotal + Post-Market)
    late_stage_devices = []
    for device_name, device_data in devices.items():
        if 'Pivotal' in device_data['stages'] or 'Post-Market' in device_data['stages']:
            highest_stage = 'Post-Market' if 'Post-Market' in device_data['stages'] else 'Pivotal'
            late_stage_devices.append({
                'device': device_name,
                'indications': sorted(list(device_data['indications']))[:3],
                'therapeutic_areas': sorted(list(device_data['therapeutic_areas'])),
                'stage': highest_stage,
                'trials': device_data['total_trials'],
                'enrollment': device_data['total_enrollment'],
                'fda_cleared': device_name in fda_cleared_devices,
                'fda_approved': device_name in fda_approved_devices,
            })

    late_stage_devices.sort(key=lambda x: -x['enrollment'])

    # Format device details
    stage_rank = {'Post-Market': 3, 'Pivotal': 2, 'Feasibility': 1, 'Unknown': 0}

    devices_output = {}
    devices_sorted = sorted(
        devices.items(),
        key=lambda x: (-max(stage_rank.get(s, 0) for s in x[1]['stages']), -x[1]['total_trials'])
    )[:30]

    for device_name, device_data in devices_sorted:
        highest_stage = _get_highest_device_stage(device_data['stages'])
        devices_output[device_name] = {
            'indications': sorted(list(device_data['indications']))[:5],
            'therapeutic_areas': sorted(list(device_data['therapeutic_areas'])),
            'stages': sorted(list(device_data['stages'])),
            'highest_stage': highest_stage,
            'total_trials': device_data['total_trials'],
            'total_enrollment': device_data['total_enrollment'],
            'fda_cleared': device_name in fda_cleared_devices,
            'fda_approved': device_name in fda_approved_devices,
        }

    return {
        'total_trials': total_device_trials,
        'trials_analyzed': processed_device_trials,
        'total_devices': len(devices),
        'total_enrollment': total_device_enrollment,
        'stage_summary': stage_output,
        'therapeutic_areas': ta_output,
        'devices': devices_output,
        'late_stage_devices': late_stage_devices,  # All late-stage devices
        'regulatory_summary': {
            'fda_cleared_count': len(fda_cleared_devices),
            'fda_approved_count': len(fda_approved_devices),
            'fda_cleared_devices': sorted(list(fda_cleared_devices)),
            'fda_approved_devices': sorted(list(fda_approved_devices)),
        },
    }


def _extract_device_stage(trial_text: str) -> Optional[str]:
    """
    Extract device development stage from trial markdown.

    Device stages differ from drug phases:
    - Feasibility/First-in-Human/EFS = Early (like Phase 1)
    - Pivotal/IDE/PMA = Late (like Phase 3)
    - Post-Market/PMCF/Registry = Surveillance (like Phase 4)

    Common device trial acronyms:
    - IDE: Investigational Device Exemption (FDA pivotal)
    - EFS: Early Feasibility Study
    - PMCF: Post-Market Clinical Follow-up (EU MDR requirement)
    - PMA: Pre-Market Approval
    - PAS: Pre-Market Approval Supplement
    - HDE: Humanitarian Device Exemption
    """
    # Extract title first - most reliable source for device stage
    title = ""
    title_match = re.search(r'\*\*Study Title:\*\*\s*(.+?)(?:\n|$)', trial_text)
    if title_match:
        title = title_match.group(1).lower()

    # Check phase field
    phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|$)', trial_text)
    phase_raw = ""
    if phase_match:
        phase_raw = phase_match.group(1).strip().lower()

        # Post-market surveillance (Phase 4 equivalent)
        if 'phase 4' in phase_raw or 'post-market' in phase_raw or 'post market' in phase_raw:
            return 'Post-Market'

        # Map drug phases to device equivalents
        if 'phase 3' in phase_raw:
            return 'Pivotal'
        if 'phase 2' in phase_raw:
            return 'Pivotal'
        if 'phase 1' in phase_raw or 'early' in phase_raw:
            return 'Feasibility'

    # === Title-based heuristics (most reliable for devices) ===

    # Post-Market indicators (check first - most specific)
    post_market_patterns = [
        r'\bpmcf\b',           # Post-Market Clinical Follow-up (EU MDR)
        r'\bpost[- ]?market\b',
        r'\bpost[- ]?approval\b',  # Post-Approval Study
        r'\bpms\b',            # Post-Market Surveillance (Japan)
        r'\bced\b',            # Coverage with Evidence Development (CMS)
        r'coverage with evidence',  # CMS CED studies
        r'\bregistry\b',
        r'\breal[- ]?world\b',
        r'\brwe\b',            # Real-World Evidence
        r'\brwd\b',            # Real-World Data
        r'\bsurveillance\b',
        r'\blong[- ]?term follow',
        r'\bfollow[- ]?up study\b',
        r'\bcontinued access\b',
        r'japan\s+study\b',    # Japan regional studies (typically post-market)
    ]
    for pattern in post_market_patterns:
        if re.search(pattern, title):
            return 'Post-Market'

    # Pivotal/IDE indicators (FDA approval pathway)
    pivotal_patterns = [
        r'\bide\b',            # Investigational Device Exemption
        r'\bpivotal\b',
        r'\bpma\b',            # Pre-Market Approval
        r'\bpremarket\b',
        r'\bpre[- ]?market\b',
        r'\b510\s*\(?k\)?\b',  # 510(k) clearance
        r'\bpas\b',            # PMA Supplement
        r'\bhde\b',            # Humanitarian Device Exemption
        r'\brandomized controlled\b',
        r'\brct\b',
    ]
    for pattern in pivotal_patterns:
        if re.search(pattern, title):
            return 'Pivotal'

    # Feasibility indicators (early development)
    feasibility_patterns = [
        r'\befs\b',            # Early Feasibility Study
        r'\bfeasibility\b',
        r'\bfirst[- ]?in[- ]?human\b',
        r'\bfih\b',
        r'\bfirst[- ]?in[- ]?man\b',
        r'\bfim\b',
        r'\bpilot\b',
        r'\bproof[- ]?of[- ]?concept\b',
        r'\bpoc\b',
        r'\bearly[- ]?stage\b',
        r'\binitial\b.*\bsafety\b',
    ]
    for pattern in feasibility_patterns:
        if re.search(pattern, title):
            return 'Feasibility'

    # === Secondary checks ===

    # Check study purpose
    purpose_match = re.search(r'\*\*Primary Purpose:\*\*\s*(.+?)(?:\n|$)', trial_text)
    if purpose_match:
        purpose = purpose_match.group(1).lower()
        if 'device feasibility' in purpose:
            return 'Feasibility'

    # Check for specific design patterns in full text
    if re.search(r'ce[- ]?mark', trial_text.lower()):
        # CE marking studies are typically post-market in EU
        return 'Post-Market'

    # If phase is "Na" (Not Applicable) - common for devices
    # Try to infer from enrollment size as last resort
    if phase_raw in ['na', 'n/a', 'not applicable']:
        enrollment = _extract_enrollment(trial_text)
        if enrollment > 0:
            # Large enrollment (>300) typically indicates pivotal
            # Small enrollment (<50) typically indicates feasibility
            # This is a rough heuristic
            if enrollment >= 300:
                return 'Pivotal'
            elif enrollment <= 50:
                return 'Feasibility'

    return None


def _extract_devices_from_trial(trial_text: str) -> List[str]:
    """Extract device intervention names from trial markdown."""
    devices = []

    # Parse the ## Interventions section for devices
    interventions_section = re.search(r'## Interventions\s*\n([\s\S]*?)(?=\n## |$)', trial_text)
    if interventions_section:
        section_text = interventions_section.group(1)

        # Find device interventions
        device_matches = re.findall(r'###\s+Device:\s*(.+?)(?:\n|$)', section_text)
        devices.extend(device_matches)

        # Also check for Combination Product that might be device
        combo_matches = re.findall(r'###\s+Combination Product:\s*(.+?)(?:\n|$)', section_text)
        for combo in combo_matches:
            # Only include if it looks device-related
            if any(kw in combo.lower() for kw in ['stent', 'catheter', 'implant', 'pump', 'monitor', 'sensor']):
                devices.append(combo)

    # Remove duplicates while preserving order
    seen = set()
    unique_devices = []
    for d in devices:
        d_clean = d.strip()
        d_lower = d_clean.lower()
        if d_lower not in seen and d_clean:
            seen.add(d_lower)
            unique_devices.append(d_clean)

    return unique_devices


def _clean_device_name(device_name: str) -> str:
    """Clean device name for display."""
    if not device_name:
        return ""

    name = device_name.strip()

    # Remove parenthetical content
    name = re.sub(r'\([^)]*\)', '', name)

    # Remove version numbers
    name = re.sub(r'\bv?\d+(\.\d+)*\b', '', name, flags=re.IGNORECASE)

    # Clean up whitespace
    name = re.sub(r'\s+', ' ', name).strip()

    # Skip if too short or generic
    if len(name) < 3:
        return ""

    generic_terms = ['device', 'system', 'product', 'instrument']
    if name.lower() in generic_terms:
        return ""

    return name


def _get_highest_device_stage(stages: set) -> str:
    """Get the highest device stage from a set of stages."""
    stage_order = ['Post-Market', 'Pivotal', 'Feasibility', 'Unknown']
    for stage in stage_order:
        if stage in stages:
            return stage
    return list(stages)[0] if stages else 'Unknown'


# Helper functions

def _extract_phase(trial_text: str) -> Optional[str]:
    """Extract normalized phase from trial markdown."""
    phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|$)', trial_text)
    if not phase_match:
        return None

    phase_raw = phase_match.group(1).strip()

    # Handle combined phases like "Phase2, Phase3" -> use highest
    if 'Phase 4' in phase_raw or 'Phase4' in phase_raw:
        return 'Phase 4'
    elif 'Phase 3' in phase_raw or 'Phase3' in phase_raw:
        return 'Phase 3'
    elif 'Phase 2' in phase_raw or 'Phase2' in phase_raw:
        return 'Phase 2'
    elif 'Phase 1' in phase_raw or 'Phase1' in phase_raw:
        return 'Phase 1'
    elif 'early' in phase_raw.lower():
        return 'Phase 1'
    elif 'na' in phase_raw.lower() or 'not applicable' in phase_raw.lower():
        return None  # Skip non-applicable phases

    return None


def _extract_drugs_from_trial(trial_text: str) -> List[str]:
    """Extract drug and biological intervention names from trial markdown.

    Uses multiple heuristics to identify sponsor's pipeline drugs vs comparators:
    1. Drug mentioned in trial TITLE = sponsor's drug being studied (always include)
    2. Drug is a compound code (letters+numbers like NNC0123) = sponsor's internal code
    3. Drug appears in experimental arm names = likely sponsor's drug
    4. Drug only in comparator arms = competitor drug (filtered out)

    A drug is filtered out if:
    1. It only appears in comparator arms (placebo, control, chemotherapy, SOC)
    2. It is placebo/sham/vehicle itself
    3. It appears in "all arms" (background therapy)

    NO HARDCODED DRUG LISTS - purely arm-based and title-based heuristics.
    """
    drugs_with_arm_text = {}  # drug_name -> raw "Used in" text

    # Extract trial title for drug name matching
    title_match = re.search(r'\*\*Study Title:\*\*\s*(.+?)(?:\n|$)', trial_text)
    trial_title = title_match.group(1).lower() if title_match else ""

    # Parse the ## Interventions section to get drugs and their arm assignments
    interventions_section = re.search(r'## Interventions\s*\n([\s\S]*?)(?=\n## |$)', trial_text)
    if interventions_section:
        section_text = interventions_section.group(1)

        # Split by intervention headers and parse each
        intervention_blocks = re.split(r'\n(?=### (?:Drug|Biological|Combination Product):)', section_text)

        for block in intervention_blocks:
            # Extract drug name
            drug_match = re.match(r'###\s+(?:Drug|Biological|Combination Product):\s*(.+?)(?:\n|$)', block)
            if not drug_match:
                continue

            drug_name = drug_match.group(1).strip()

            # Extract arm assignments from "**Used in:**" line
            used_in_match = re.search(r'\*\*Used in:\*\*\s*(.+?)(?:\n|$)', block)
            if used_in_match:
                drugs_with_arm_text[drug_name] = used_in_match.group(1).lower()
            else:
                drugs_with_arm_text[drug_name] = None

    # Determine which drugs are pipeline assets vs standard of care
    pipeline_drugs = []

    # Keywords that indicate comparator/control arms
    comparator_keywords = [
        'placebo', 'control', 'comparator', 'soc', 'standard of care',
        'chemotherapy', 'chemo', 'doublet', 'platinum-based', 'active control',
        'best available', 'investigator choice', 'physician choice',
    ]

    for drug_name, arm_text in drugs_with_arm_text.items():
        drug_lower = drug_name.lower()

        # Skip obvious non-drugs
        if any(nd in drug_lower for nd in ['placebo', 'sham', 'vehicle', 'saline']):
            continue

        # Get first significant word of drug name for matching
        drug_words = [w for w in drug_lower.split() if len(w) > 3]
        first_word = drug_words[0] if drug_words else drug_lower

        # KEY HEURISTIC 1: Drug appears in trial TITLE = sponsor's drug (always include)
        # The trial is literally named after this drug, so it's the focus
        drug_in_title = first_word in trial_title or drug_lower in trial_title
        if drug_in_title:
            pipeline_drugs.append(drug_name)
            continue

        # KEY HEURISTIC 2: Compound code pattern = sponsor's internal code (always include)
        # Pattern: 2-4 letters followed by digits (LY123456, NNC0065-0001, ABC-123)
        is_compound_code = re.match(r'^[A-Z]{2,4}[-\s]?\d', drug_name)
        if is_compound_code:
            pipeline_drugs.append(drug_name)
            continue

        # If we have arm info, use it to determine if this is SOC
        if arm_text:
            # Check if this drug is used across "all arms" (background therapy)
            if 'all arm' in arm_text or arm_text.strip() == 'all':
                continue

            # Check if drug name appears in any arm name
            # This means the arm is named after/for this drug = experimental
            drug_in_arm_name = first_word in arm_text

            # Special case: "X or Drug" pattern means Drug is experimental alternative
            # e.g., "Chemotherapy or Mirvetuximab Soravtansine" - MIRV is the experimental
            is_alternative_experimental = False
            if ' or ' in arm_text:
                for arm_segment in arm_text.split(','):
                    if ' or ' in arm_segment:
                        # Check if drug appears AFTER "or" - it's the experimental alternative
                        parts = arm_segment.split(' or ')
                        if len(parts) > 1:
                            experimental_part = parts[-1]  # Part after "or"
                            if first_word in experimental_part or drug_lower in experimental_part:
                                is_alternative_experimental = True
                                break

            if is_alternative_experimental:
                pipeline_drugs.append(drug_name)
                continue

            # Check each arm this drug appears in to determine if it's experimental
            named_in_experimental_arm = False  # Drug name appears in non-comparator arm name
            named_in_comparator_arm = False    # Drug name appears in comparator arm name

            for arm_segment in arm_text.split(','):
                arm_segment = arm_segment.strip()
                is_comparator = any(kw in arm_segment for kw in comparator_keywords)

                # Check if drug name appears in this arm name
                drug_named_in_arm = first_word in arm_segment or drug_lower in arm_segment

                if drug_named_in_arm:
                    if is_comparator:
                        # Drug name appears in a comparator arm (e.g., "Placebo + DrugX" as control)
                        named_in_comparator_arm = True
                    else:
                        # Drug name is in a non-comparator arm - it's the focus
                        named_in_experimental_arm = True

            # Include drug if named in experimental arm, or in any arm but not only comparator
            if named_in_experimental_arm:
                # Named in at least one experimental arm - it's a pipeline asset
                pipeline_drugs.append(drug_name)
            elif drug_in_arm_name and not named_in_comparator_arm:
                # Drug name appears in arm names and not in comparator
                pipeline_drugs.append(drug_name)
        else:
            # No arm info - include by default
            pipeline_drugs.append(drug_name)

    # Remove duplicates while preserving order
    seen = set()
    unique_drugs = []
    for d in pipeline_drugs:
        d_clean = d.strip()
        d_lower = d_clean.lower()
        if d_lower not in seen and d_clean:
            seen.add(d_lower)
            unique_drugs.append(d_clean)

    return unique_drugs


def _extract_enrollment(trial_text: str) -> int:
    """Extract target enrollment from trial markdown."""
    enrollment_match = re.search(r'\*\*Enrollment:\*\*\s*(\d+)', trial_text)
    if enrollment_match:
        return int(enrollment_match.group(1))
    return 0


def _extract_collaborators(trial_text: str) -> List[str]:
    """Extract collaborator names from trial markdown."""
    collabs = []

    # Pattern: ### Collaborator: <name>
    collab_matches = re.findall(r'###\s+Collaborator:\s*(.+?)(?:\n|$)', trial_text)
    collabs.extend(collab_matches)

    # Also check for **Collaborators:** section
    collab_section = re.search(r'\*\*Collaborators?:\*\*\s*(.+?)(?:\n\n|\n\*\*|$)', trial_text, re.DOTALL)
    if collab_section:
        section_text = collab_section.group(1)
        # Split on newlines first, then strip bullet/dash markers from each line.
        # Do NOT split on hyphens (they appear in names like "Bristol-Myers Squibb").
        for line in section_text.split('\n'):
            # Strip leading bullet/dash markers: "- Name", "• Name", "* Name"
            line = re.sub(r'^\s*[-•\*]\s+', '', line).strip()
            # Remove parenthetical content like "(Industry)"
            line = re.sub(r'\s*\([^)]+\)\s*$', '', line)
            if line and len(line) > 2:
                collabs.append(line)

    return collabs


def _clean_drug_name(drug_name: str) -> str:
    """Clean drug name for display."""
    if not drug_name:
        return ""

    name = drug_name.strip()

    # Protect compound codes (e.g., PF-06882961, LY3502970, NNC0065-0001)
    # Don't strip digits or formulation terms from these
    is_compound_code = bool(re.match(r'^[A-Z]{2,5}[-\s]?\d', name))

    if not is_compound_code:
        # Strip dosage patterns (e.g., "100 mg", "5 mL")
        # Note: Use word boundary and require space before unit to avoid stripping "L" from "CDR132L"
        name = re.sub(r'\d+\.?\d*\s+(mg|mcg|ug|ml|iu|units?)\b', '', name, flags=re.IGNORECASE)
        # Also handle "5mg" with no space
        name = re.sub(r'\d+\.?\d*(mg|mcg|ug|ml|iu)\b', '', name, flags=re.IGNORECASE)

        # Strip formulation terms
        name = strip_formulation_terms(name)

    # Remove parenthetical content (safe for codes too — strips descriptions like "(gene therapy)")
    name = re.sub(r'\([^)]*\)', '', name)

    # Strip colon-separated descriptions (e.g., "PF-07055480 : RECOMBINANT AAV2/6...")
    if ':' in name:
        name = name.split(':')[0]

    # Clean up whitespace
    name = re.sub(r'\s+', ' ', name).strip()

    return name


def _is_non_drug(drug_name: str) -> bool:
    """Check if a drug name is actually a non-drug item (placebo, control, etc.)."""
    if not drug_name:
        return True

    name_lower = drug_name.lower().strip()

    # Pattern-based non-drug detection
    if is_non_drug_item(name_lower):
        return True

    # Check if name starts with or contains key non-drug terms
    non_drug_prefixes = ['placebo', 'control', 'sham', 'vehicle', 'saline', 'comparator']
    for prefix in non_drug_prefixes:
        if name_lower.startswith(prefix) or prefix in name_lower:
            return True

    # Filter out single letters or very short names
    if len(name_lower) <= 2:
        return True

    # Common English words that leak through from title parsing
    non_drug_words = {'called', 'study', 'medicine', 'drug', 'trial', 'treatment',
                      'therapy', 'higher', 'lower', 'dose', 'only', 'monotherapy',
                      'combination', 'regimen', 'standard', 'care', 'best', 'available'}
    if name_lower in non_drug_words:
        return True

    return False


def _extract_drug_name_mapping(trial_text: str) -> dict:
    """Extract mapping of internal drug codes to marketing names from trial title.

    Pharma companies often include marketing names in trial titles while using
    internal codes (NNC..., LY..., etc.) as the intervention name.

    Patterns detected:
    - "MarketingName (InternalCode)" → maps InternalCode → MarketingName
    - "(MarketingName)" after "Study Medicine" or similar → captures name
    - "...Called MarketingName (InternalCode)..." → maps code to name

    Returns:
        Dict mapping internal code (lowercase) → marketing name
    """
    mapping = {}

    # Extract title
    title_match = re.search(r'\*\*Study Title:\*\*\s*(.+?)(?:\n|$)', trial_text)
    if not title_match:
        return mapping

    title = title_match.group(1)

    # Pattern 1: "MarketingName (InternalCode)" - e.g., "Coramitug (NNC6019-0001)"
    # The marketing name comes BEFORE the code in parentheses
    pattern1 = re.findall(r'\b([A-Z][a-z]+(?:[A-Z][a-z]*)*)\s*\(([A-Z]{2,4}[-\s]?\d[\w-]*)\)', title)
    for marketing_name, code in pattern1:
        code_lower = code.lower().replace(' ', '')
        mapping[code_lower] = marketing_name

    # Pattern 2: "Study Medicine (MarketingName)" or "a Medicine Called MarketingName"
    # e.g., "Study Medicine (Inno8)" where Inno8 is the marketing name
    # Match "Called X" where X follows (not "Called" itself)
    pattern2 = re.search(r'(?:Study Medicine|Medicine Called|Drug Called)\s*\(?([A-Z][a-z0-9]+)\)?', title, re.IGNORECASE)
    if pattern2:
        marketing_name = pattern2.group(1)
        # Skip common English words that aren't marketing names
        if marketing_name.lower() not in ('called', 'study', 'medicine', 'drug', 'trial', 'the', 'this', 'that', 'with', 'from'):
            mapping['__marketing_name__'] = marketing_name

    # Pattern 3: "Called MarketingName (Code)" - e.g., "Called Coramitug (NNC6019-0001)"
    pattern3 = re.search(r'[Cc]alled\s+([A-Z][a-z]+(?:[A-Z][a-z]*)*)\s*\(([A-Z]{2,4}[-\s]?\d[\w-]*)\)', title)
    if pattern3:
        marketing_name = pattern3.group(1)
        code = pattern3.group(2).lower().replace(' ', '')
        mapping[code] = marketing_name

    return mapping


def _normalize_drug_display_name(drug_name: str, code_to_name_map: dict = None) -> str:
    """Normalize drug name for consistent display and grouping.

    Handles case normalization to avoid duplicates like 'Semaglutide' vs 'semaglutide'.
    Also maps internal codes to marketing names when available.

    Args:
        drug_name: Raw drug name from trial
        code_to_name_map: Optional mapping of internal codes to marketing names
    """
    if not drug_name:
        return ""

    name = drug_name.strip()

    # Check if we have a marketing name mapping for this code
    if code_to_name_map:
        name_lower = name.lower().replace(' ', '')
        if name_lower in code_to_name_map:
            # Use the marketing name instead of the code
            return code_to_name_map[name_lower]

        # Also check if there's a marketing name hint and this is the only drug code
        if '__marketing_name__' in code_to_name_map:
            # If this looks like a code and we have a marketing name, use it
            if re.match(r'^[A-Z]{2,4}[-\s]?\d', name, re.IGNORECASE):
                marketing = code_to_name_map['__marketing_name__']
                # Validate the marketing name is a real drug name (not a prefix like "PF")
                if len(marketing.strip()) >= 3 and not _is_non_drug(marketing):
                    # Store the mapping for future reference
                    code_to_name_map[name_lower] = marketing
                    return marketing

    # If it looks like a code (starts with letters followed by numbers), keep original case
    if re.match(r'^[A-Z]{2,4}[-\s]?\d', name, re.IGNORECASE):
        return name.upper()  # Normalize codes to uppercase

    # Otherwise, use title case for drug names
    return name.title()


def _normalize_drug_name(drug_name: str) -> str:
    """Normalize drug name for FDA/EMA lookup."""
    if not drug_name:
        return ""

    name = drug_name.lower().strip()

    # Remove dosage patterns
    name = re.sub(r'\d+\.?\d*\s*(mg|mcg|ug|ml|l|iu|units?)\b', '', name, flags=re.IGNORECASE)

    # Remove formulation terms
    name = strip_formulation_terms(name)

    # Remove parenthetical content
    name = re.sub(r'\([^)]*\)', '', name)

    # Clean up
    name = re.sub(r'[-_/,]+', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()

    return name


def _get_highest_phase(phases: set) -> str:
    """Get the highest phase from a set of phases."""
    phase_order = ['Phase 4', 'Phase 3', 'Phase 2', 'Phase 1']
    for phase in phase_order:
        if phase in phases:
            return phase
    return list(phases)[0] if phases else 'Unknown'


def _build_cli_mcp_funcs():
    """Build MCP functions dict for CLI execution."""
    import importlib.util

    def _load_mcp(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    ct_mod = _load_mcp('ctgov', os.path.join('.claude', 'mcp', 'servers', 'ct_gov_mcp', '__init__.py'))
    fda_mod = _load_mcp('fda', os.path.join('.claude', 'mcp', 'servers', 'fda_mcp', '__init__.py'))
    ema_mod = _load_mcp('ema', os.path.join('.claude', 'mcp', 'servers', 'ema_mcp', '__init__.py'))

    def ct_search_wrapper(**kw):
        kw.pop('method', None)
        return ct_mod.search(**kw)

    def ct_get_study_wrapper(**kw):
        kw.pop('method', None)
        return ct_mod.get_study(**kw)

    def fda_lookup_wrapper(**kw):
        kw.pop('method', None)
        # Route device searches to lookup_device, drug searches to lookup_drug
        search_type = kw.get('search_type', 'general')
        if search_type.startswith('device_'):
            return fda_mod.lookup_device(**kw)
        return fda_mod.lookup_drug(**kw)

    def ema_search_wrapper(**kw):
        # EMA ema_info() requires method as positional arg — pass it through
        return ema_mod.ema_info(**kw)

    return {
        'ctgov_search': ct_search_wrapper,
        'ctgov_get_study': ct_get_study_wrapper,
        'fda_lookup': fda_lookup_wrapper,
        'fda_device_lookup': fda_lookup_wrapper,
        'ema_search': ema_search_wrapper,
    }


if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python3 get_company_pipeline_breakdown.py <COMPANY> [OPTIONS]")
        print("\nExamples:")
        print("  # Full analysis (drugs only)")
        print("  python3 get_company_pipeline_breakdown.py 'Eli Lilly'")
        print("")
        print("  # Skip regulatory checks (faster)")
        print("  python3 get_company_pipeline_breakdown.py 'Novo Nordisk' --skip-regulatory")
        print("")
        print("  # Include medical devices (both drugs and devices)")
        print("  python3 get_company_pipeline_breakdown.py 'J&J' --include-devices")
        print("")
        print("  # Devices only (for medtech companies)")
        print("  python3 get_company_pipeline_breakdown.py 'Medtronic' --include-devices --no-drugs")
        print("")
        print("  # Limit trials analyzed")
        print("  python3 get_company_pipeline_breakdown.py 'Pfizer' --max-trials=100")
        print("")
        print("  # Exclude subsidiaries")
        print("  python3 get_company_pipeline_breakdown.py 'Bristol Myers Squibb' --no-subsidiaries")
        print("")
        print("  # Skip marketed products (faster)")
        print("  python3 get_company_pipeline_breakdown.py 'Pfizer' --no-marketed")
        sys.exit(1)

    company_name = sys.argv[1]

    # Parse options
    skip_regulatory = '--skip-regulatory' in sys.argv
    include_subsidiaries = '--no-subsidiaries' not in sys.argv
    include_drugs = '--no-drugs' not in sys.argv
    include_devices = '--include-devices' in sys.argv
    include_marketed = '--no-marketed' not in sys.argv
    max_trials = None

    for arg in sys.argv[2:]:
        if arg.startswith('--max-trials='):
            max_trials = int(arg.split('=')[1])

    result = get_company_pipeline_breakdown(
        company=company_name,
        include_subsidiaries=include_subsidiaries,
        skip_regulatory=skip_regulatory,
        max_trials=max_trials,
        include_drugs=include_drugs,
        include_devices=include_devices,
        include_marketed=include_marketed,
    )

    print("\n" + "=" * 80)
    print("✅ PIPELINE ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"Company: {result['company']}")
    print(f"Active Trials: {result['total_active_trials']}")
    print(f"Analyzed: {result['trials_analyzed']} trials")
    print(f"Unique Drugs: {result['total_unique_drugs']}")
    print(f"Therapeutic Areas: {result['therapeutic_area_count']}")
    print(f"Late-Stage Pipeline: {len(result['late_stage_pipeline'])} drugs in Phase 3+")
    if not skip_regulatory:
        print(f"FDA Approved: {result['regulatory_summary']['fda_approved_count']}")
        print(f"EMA Approved: {result['regulatory_summary']['ema_approved_count']}")
    print("=" * 80)

    # Print TA breakdown
    print("\nTherapeutic Area Distribution:")
    ta_sorted = sorted(result['therapeutic_areas'].items(), key=lambda x: -x[1]['trials'])
    for ta_name, ta_data in ta_sorted[:8]:
        print(f"  {ta_name}: {ta_data['trials']} trials, {ta_data['unique_drugs']} drugs")

    # Print phase breakdown
    print("\nPhase Distribution:")
    for phase in ['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4']:
        data = result['phase_summary'].get(phase, {})
        print(f"  {phase}: {data.get('trials', 0)} trials, {data.get('drugs', 0)} drugs")

    # Print late-stage drugs
    if result['late_stage_pipeline']:
        print("\nLate-Stage Pipeline (Phase 3+):")
        for drug in result['late_stage_pipeline'][:5]:
            status = []
            if drug.get('fda_approved'):
                status.append('FDA')
            if drug.get('ema_approved'):
                status.append('EMA')
            status_str = f" [Approved: {', '.join(status)}]" if status else " [Novel]"
            print(f"  {drug['drug']}: {drug['phase']}, {drug['trials']} trials{status_str}")

    # Print drug portfolio (top 30 by trial count)
    if result['drugs']:
        print("\nDrug Pipeline (Top 30 by Trial Count):")
        drugs_sorted = sorted(
            result['drugs'].items(),
            key=lambda x: (-x[1].get('total_trials', 0), x[0])
        )
        for drug_name, drug_data in drugs_sorted[:30]:
            phases = drug_data.get('phases', [])
            highest_phase = drug_data.get('highest_phase', phases[0] if phases else 'Unknown')
            # Show indications instead of therapeutic areas
            indications = list(drug_data.get('indications', []))[:2]
            indication_str = ', '.join(indications) if indications else 'Unknown'
            trials = drug_data.get('total_trials', 0)
            print(f"  {drug_name}: {highest_phase} | {trials} trial(s) | {indication_str}")

    # Print medical device pipeline if available
    device_pipeline = result.get('device_pipeline')
    if device_pipeline and device_pipeline.get('total_trials', 0) > 0:
        print("\n" + "=" * 80)
        print("🔧 MEDICAL DEVICE PIPELINE")
        print("=" * 80)
        print(f"Active Device Trials: {device_pipeline['total_trials']}")
        print(f"Analyzed: {device_pipeline.get('trials_analyzed', 0)} trials")
        print(f"Unique Devices: {device_pipeline['total_devices']}")
        print(f"Target Enrollment: {device_pipeline.get('total_enrollment', 0):,} patients")

        # Stage distribution
        stage_summary = device_pipeline.get('stage_summary', {})
        if stage_summary:
            print("\nDevelopment Stage Distribution:")
            for stage_name in ['Feasibility', 'Pivotal', 'Post-Market', 'Unknown']:
                if stage_name in stage_summary:
                    data = stage_summary[stage_name]
                    print(f"  {stage_name}: {data.get('trials', 0)} trials, {data.get('devices', 0)} devices")

        # Device therapeutic areas
        ta_output = device_pipeline.get('therapeutic_areas', {})
        if ta_output:
            print("\nDevice Therapeutic Areas:")
            ta_sorted = sorted(ta_output.items(), key=lambda x: -x[1].get('trials', 0))
            for ta_name, ta_data in ta_sorted[:5]:
                print(f"  {ta_name}: {ta_data['trials']} trials, {ta_data['unique_devices']} devices")

        # Late-stage devices
        late_stage_devices = device_pipeline.get('late_stage_devices', [])
        if late_stage_devices:
            print("\nLate-Stage Devices (Pivotal/Post-Market):")
            for device in late_stage_devices[:5]:
                print(f"  {device['device']}: {device['stage']}, {device['trials']} trials")

        # Device portfolio
        devices = device_pipeline.get('devices', {})
        if devices:
            print("\nDevice Pipeline (Top 15):")
            for device_name, device_data in list(devices.items())[:15]:
                stages = device_data.get('stages', [])
                highest_stage = device_data.get('highest_stage', stages[0] if stages else 'Unknown')
                ta_list = list(device_data.get('therapeutic_areas', []))[:2]
                ta_str = ', '.join(ta_list) if ta_list else 'Unknown'
                trials = device_data.get('total_trials', 0)
                print(f"  {device_name[:40]}: {highest_stage} | {trials} trial(s) | {ta_str}")

    # Print marketed products if available
    marketed = result.get('marketed_products')
    if marketed:
        print("\n" + "=" * 80)
        print("🏷️  MARKETED PRODUCTS (FDA-Approved)")
        print("=" * 80)

        # Marketed drugs
        if marketed.get('drugs', {}).get('total_count', 0) > 0:
            drug_brands = marketed['drugs']['brands']
            print(f"\nMarketed Drug Brands ({marketed['drugs']['total_count']}):")
            for drug in drug_brands[:15]:
                variants = drug.get('variants', [])
                variant_str = f" (+ {', '.join(variants[:2])})" if variants else ""
                print(f"  {drug['name']}{variant_str}")

        # Marketed devices
        if marketed.get('devices', {}).get('approved_pma_count', 0) > 0:
            pma_devices = marketed['devices']['approved_pma']
            print(f"\nPMA-Approved Devices ({marketed['devices']['approved_pma_count']}):")
            for device in pma_devices[:10]:
                print(f"  {device['name'][:50]} - {device.get('advisory_committee', 'N/A')}")

        if marketed.get('devices', {}).get('cleared_510k_count', 0) > 0:
            cleared_devices = marketed['devices']['cleared_510k']
            print(f"\n510(k)-Cleared Devices ({marketed['devices']['cleared_510k_count']}):")
            for device in cleared_devices[:10]:
                print(f"  {device['name'][:50]}")
