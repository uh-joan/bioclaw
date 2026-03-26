#!/usr/bin/env python3
"""
Target Landscape Analysis - Phase 1: Core Target Discovery

Provides comprehensive competitive intelligence around a biological target.

Phase 1 (Current):
- Target resolution (Open Targets)
- Genetic validation and druggability
- Drug discovery (DrugBank)
- Clinical trials search (ClinicalTrials.gov)

Future Phases:
- Phase 2: FDA/EMA regulatory status + company analysis
- Phase 3: Safety profiling (FAERS, label warnings)
"""

import sys
import os
from typing import Dict, Any, List, Optional

# Add script directory for local imports
_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _script_dir)

from mcp_client import McpClient

# Import utility modules
from target_utils import (
    resolve_target_identity,
    get_druggability_assessment,
    get_genetic_validation
)
from drug_utils import (
    search_drugs_by_target,
    search_drugs_hybrid,
    get_drug_details_batch,
    classify_drugs_by_status,
    summarize_drug_discovery,
    filter_active_drugs
)
from trial_utils import (
    aggregate_trials_by_drug,
    get_phase_distribution_summary,
    generate_trial_intelligence_summary
)
from regulatory_utils import (
    get_regulatory_status_batch,
    classify_by_regulatory_status,
    get_regulatory_timeline
)
from company_utils import (
    aggregate_by_company,
    get_top_companies,
    generate_company_summary
)
from safety_utils import (
    get_safety_profile_batch,
    classify_by_safety_risk,
    calculate_safety_risk_score,
    aggregate_class_wide_safety
)
from visualization_utils import (
    generate_ascii_visualization,
    format_summary_stats,
    create_progress_printer,
    generate_radial_chart_data
)
from deduplication_utils import (
    deduplicate_drugs,
    add_data_quality_indicators
)


def get_target_landscape_analysis(
    target_name: str = None,
    gene_symbol: str = None,
    include_genetic_validation: bool = True,
    include_company_positioning: bool = True,  # Phase 2 (enabled by default - provides regulatory + company data)
    include_safety_analysis: bool = True,  # Phase 3 (enabled by default - provides valuable FAERS data)
    max_drugs: int = None,
    max_trials_per_drug: int = None,
    progress_callback=None,
    mcp_funcs: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Analyze competitive landscape for a biological target.

    Phases:
    - Phase 1 (always): Target resolution, genetic validation, drug/trial discovery
    - Phase 2 (optional): FDA/EMA regulatory status + company analysis
    - Phase 3 (optional): Safety profiling (FAERS adverse events)

    Args:
        target_name: Common name (e.g., "GLP-1 receptor", "PD-1")
        gene_symbol: Gene symbol (e.g., "GLP1R", "PDCD1")
        include_genetic_validation: Get genetic evidence (default: True)
        include_company_positioning: Enable Phase 2 - regulatory + companies (default: False)
        include_safety_analysis: Enable Phase 3 - safety profiling (default: False)
        max_drugs: Max drugs to analyze (default: None = all)
        max_trials_per_drug: Max trials per drug (default: None = all)
        progress_callback: Optional callback(percent, message)

    Returns:
        dict with target_summary, genetic_validation, competitive_landscape, etc.
    """

    if not target_name and not gene_symbol:
        raise ValueError("Must provide either target_name or gene_symbol")

    # BioClaw: auto-init MCP functions via McpClient if not injected
    if not mcp_funcs:
        _clients = {}
        mcp_funcs = {}
        _server_map = {
            'opentargets': ('opentargets_info', {
                'opentargets_search': {'method': 'search_targets'},
                'opentargets_get_target': {'method': 'get_target_details'},
                'opentargets_get_associations': {'method': 'get_target_disease_associations'},
            }),
            'drugbank': ('drugbank_info', {
                'drugbank_search_by_target': {'method': 'search_by_target'},
                'drugbank_get_drug': {'method': 'get_drug_details'},
                'drugbank_search_by_indication': {'method': 'search_by_indication'},
            }),
            'ctgov': ('ct_gov_studies', {
                'ctgov_search': {'method': 'search'},
                'ctgov_get_study': {'method': 'get'},
            }),
            'fda': ('fda_info', {
                'fda_lookup': {'method': 'lookup_drug'},
            }),
            'ema': ('ema_data', {
                'ema_search': {'method': 'search_medicines'},
            }),
        }
        for srv_name, (tool_name, funcs) in _server_map.items():
            try:
                client = McpClient(srv_name)
                client.connect()
                _clients[srv_name] = client
                for func_key, defaults in funcs.items():
                    def make_fn(c, t, d):
                        def fn(**kw):
                            merged = {**d, **kw}
                            return c.call(t, **merged)
                        return fn
                    mcp_funcs[func_key] = make_fn(client, tool_name, defaults)
            except Exception:
                pass
        print(f"  BioClaw MCP: {len(mcp_funcs)} functions loaded")

    search_targets = mcp_funcs.get('opentargets_search')
    get_target_details = mcp_funcs.get('opentargets_get_target')
    get_target_disease_associations = mcp_funcs.get('opentargets_get_associations')
    search_by_target = mcp_funcs.get('drugbank_search_by_target')
    get_drug_details = mcp_funcs.get('drugbank_get_drug')
    search_by_indication = mcp_funcs.get('drugbank_search_by_indication')
    search_ctgov = mcp_funcs.get('ctgov_search')
    get_study = mcp_funcs.get('ctgov_get_study')
    fda_lookup = mcp_funcs.get('fda_lookup')
    ema_search = mcp_funcs.get('ema_search')

    if not search_targets:
        return {'error': 'Open Targets search function not available'}

    # Set defaults for None values
    if max_drugs is None:
        max_drugs = 1000  # High limit to get all drugs
    if max_trials_per_drug is None:
        max_trials_per_drug = 1000  # High limit to get all trials

    if progress_callback:
        progress_callback(0, "Starting target landscape analysis...")

    # Step 1: Resolve target identity
    if progress_callback:
        progress_callback(5, "Resolving target identity via Open Targets...")

    target_identity = resolve_target_identity(
        search_targets,
        target_name=target_name,
        gene_symbol=gene_symbol
    )

    if 'error' in target_identity:
        return {'error': target_identity['error']}

    resolved_gene = target_identity['gene_symbol']
    resolved_name = target_identity['official_name']
    ensembl_id = target_identity['ensembl_id']

    if progress_callback:
        progress_callback(10, f"Target resolved: {resolved_gene} ({resolved_name})")

    # Step 2: Get druggability assessment
    if progress_callback:
        progress_callback(12, "Assessing druggability...")

    druggability = get_druggability_assessment(get_target_details, ensembl_id)

    target_summary = {
        'official_name': resolved_name,
        'gene_symbol': resolved_gene,
        'ensembl_id': ensembl_id,
        'uniprot_id': target_identity.get('uniprot_id'),
        'target_class': target_identity['target_class'],
        'druggability_assessment': druggability
    }

    # Step 3: Genetic validation
    genetic_validation = None
    if include_genetic_validation:
        if progress_callback:
            progress_callback(15, "Analyzing genetic validation...")

        genetic_validation = get_genetic_validation(get_target_disease_associations, ensembl_id, top_n=5)

        if progress_callback:
            progress_callback(20, f"Genetic validation score: {genetic_validation['overall_score']}")

    # Step 4: Drug discovery (hybrid approach with 3-tier fallback)
    if progress_callback:
        progress_callback(25, f"Searching for drugs targeting {resolved_gene}...")

    # Extract key indications from genetic validation for fallback search
    key_indications = []
    if genetic_validation and genetic_validation['key_associations']:
        key_indications = [assoc['disease'] for assoc in genetic_validation['key_associations'][:3]]

    # Use hybrid search: DrugBank → Open Targets → ClinicalTrials.gov
    drugs_search = search_drugs_hybrid(
        # DrugBank functions
        drugbank_search_by_target=search_by_target,
        drugbank_get_drug_details=get_drug_details,
        drugbank_search_by_indication=search_by_indication,
        # Open Targets functions
        opentargets_get_target_details=get_target_details,
        # ClinicalTrials.gov functions
        ctgov_search=search_ctgov,
        ctgov_get_study=get_study,
        # Target info
        gene_symbol=resolved_gene,
        target_name=resolved_name,
        target_id=ensembl_id,  # Ensembl ID for Open Targets
        key_indications=key_indications,
        max_drugs=max_drugs
    )

    if 'error' in drugs_search:
        return {'error': drugs_search['error']}

    tier = drugs_search.get('tier', None)
    source = drugs_search.get('source', 'unknown')
    strategy_used = drugs_search.get('strategy', 'unknown')

    if progress_callback:
        tier_label = f"Tier {tier}" if tier else "No data"
        progress_callback(30, f"Found {drugs_search['total']} drugs (strategy: {strategy_used})")

    # Step 5: Get drug details
    # For DrugBank (tier 1), fetch full details from DrugBank
    # For Open Targets/ClinicalTrials.gov (tier 2-3), use data as-is
    if source == 'drugbank':
        if progress_callback:
            progress_callback(35, "Fetching detailed drug information...")

        drugs_with_details = get_drug_details_batch(
            get_drug_details,
            drugs_search['drugs'],
            max_details=max_drugs,  # Use the max_drugs parameter from function args
            target_gene=resolved_gene,  # Enable classification with primary target
            target_name=resolved_name,  # Provide target name for mechanism classification
            classify=True  # Enable modality, mechanism, and selectivity classification
        )
    else:
        if progress_callback:
            if source == 'open_targets':
                progress_callback(35, "Processing Open Targets drug data...")
            else:
                progress_callback(35, "Processing trial-derived drug data...")
        # Open Targets and ClinicalTrials.gov drugs already have basic info
        drugs_with_details = drugs_search['drugs']

    if progress_callback:
        progress_callback(40, f"Retrieved details for {len(drugs_with_details)} drugs")

    # Step 6: Filter to active drugs only (exclude withdrawn/illicit/nutraceutical/vet)
    filtering_result = filter_active_drugs(drugs_with_details)
    drugs_active = filtering_result['active_drugs']
    excluded_counts = filtering_result['excluded_counts']

    if progress_callback:
        total_excluded = filtering_result['total_excluded']
        progress_callback(42, f"Filtered to {len(drugs_active)} active drugs (excluded {total_excluded}: "
                              f"{excluded_counts['withdrawn']} withdrawn, {excluded_counts['illicit']} illicit, "
                              f"{excluded_counts['nutraceutical']} nutraceutical, {excluded_counts['vet_only']} vet-only)")

    # Step 6b: Deduplicate drugs across sources (cross-tier matching)
    if progress_callback:
        progress_callback(43, "Deduplicating drugs across data sources...")

    drugs_deduplicated = deduplicate_drugs(drugs_active, threshold=0.85)
    num_duplicates = len(drugs_active) - len(drugs_deduplicated)

    if progress_callback:
        if num_duplicates > 0:
            progress_callback(44, f"Deduplicated {num_duplicates} duplicate drugs, {len(drugs_deduplicated)} unique drugs remain")
        else:
            progress_callback(44, f"No duplicates found, {len(drugs_deduplicated)} unique drugs")

    # Step 6c: Add data quality indicators
    if progress_callback:
        progress_callback(45, "Calculating data quality metrics...")

    drugs_with_quality = add_data_quality_indicators(drugs_deduplicated)

    # Step 7: Classify drugs by status
    classified_drugs = classify_drugs_by_status(drugs_with_quality)
    drug_summary = summarize_drug_discovery(classified_drugs, len(drugs_with_quality))

    # Step 8: Search clinical trials
    if progress_callback:
        progress_callback(45, f"Searching clinical trials for {len(drugs_with_quality)} drugs...")

    trials_data = aggregate_trials_by_drug(
        search_ctgov,
        drugs_with_quality,  # Use deduplicated drugs with quality metrics
        max_trials_per_drug=max_trials_per_drug
    )

    if progress_callback:
        progress_callback(75, f"Found {trials_data['summary']['total_trials']} total trials")

    # Generate trial intelligence summary
    trial_intelligence = generate_trial_intelligence_summary(
        trials_data['trials_by_drug'],
        trials_data['phase_distribution'],
        trials_data['summary']['total_trials']
    )

    # Step 9: Get regulatory status (Phase 2)
    regulatory_status = None
    if include_company_positioning:  # Uses same flag as company analysis
        if progress_callback:
            progress_callback(77, "Checking FDA/EMA approval status...")

        regulatory_status = get_regulatory_status_batch(
            fda_lookup,
            ema_search,
            drugs_with_quality,  # Use deduplicated drugs with quality metrics
            include_fda=True,
            include_ema=True
        )

        if progress_callback:
            progress_callback(78, f"Found {regulatory_status['summary']['fda_approved']} FDA approved, "
                                   f"{regulatory_status['summary']['ema_approved']} EMA approved")

    # Step 10: Company analysis (Phase 2)
    company_analysis = None
    if include_company_positioning:
        if progress_callback:
            progress_callback(79, "Aggregating drugs by company...")

        company_analysis = aggregate_by_company(
            drugs_with_quality,  # Use deduplicated drugs with quality metrics
            regulatory_batch=regulatory_status,
            trials_by_drug=trials_data['trials_by_drug'],
            get_study_func=get_study
        )

        if progress_callback:
            progress_callback(80, f"Found {company_analysis['summary']['total_companies']} companies")

    # Step 11: Safety profiling (Phase 3)
    safety_analysis = None
    if include_safety_analysis:
        if progress_callback:
            progress_callback(81, "Analyzing safety profiles (FAERS adverse events)...")

        safety_analysis = get_safety_profile_batch(
            fda_lookup,
            drugs_with_quality,  # Use deduplicated drugs with quality metrics
            include_adverse_events=True,
            include_warnings=True
        )

        # Aggregate class-wide safety signals
        class_wide_safety = aggregate_class_wide_safety(
            safety_analysis,
            target_name=target_identity.get('gene_symbol') or target_identity.get('official_name', 'this target')
        )
        safety_analysis['class_wide_safety'] = class_wide_safety

        if progress_callback:
            progress_callback(82, f"Safety data: {safety_analysis['summary']['drugs_with_adverse_event_data']} "
                                   f"with AE data, {class_wide_safety['total_reaction_reports']:,} total reaction reports")

    # Step 11: Build competitive landscape
    if progress_callback:
        progress_callback(86, "Building competitive landscape summary...")

    # Calculate data quality statistics
    high_quality = sum(1 for d in drugs_with_quality if d.get('data_quality', {}).get('confidence_score', 0) >= 0.85)
    medium_quality = sum(1 for d in drugs_with_quality if 0.70 <= d.get('data_quality', {}).get('confidence_score', 0) < 0.85)
    low_quality = sum(1 for d in drugs_with_quality if d.get('data_quality', {}).get('confidence_score', 0) < 0.70)
    deduplicated_count = sum(1 for d in drugs_with_quality if d.get('data_quality', {}).get('is_deduplicated', False))
    avg_confidence = sum(d.get('data_quality', {}).get('confidence_score', 0) for d in drugs_with_quality) / len(drugs_with_quality) if drugs_with_quality else 0

    competitive_landscape = {
        'summary': {
            'total_drugs_found': len(drugs_with_details),  # Total before filtering
            'total_drugs': len(drugs_with_quality),  # Active drugs after filtering and deduplication
            'drugs_excluded': filtering_result['total_excluded'],
            'excluded_breakdown': excluded_counts,
            'approved': drug_summary['by_status']['approved'],
            'investigational': drug_summary['by_status']['investigational'],
            'experimental': drug_summary['by_status']['experimental'],
            'total_trials': trials_data['summary']['total_trials'],
            'drugs_with_trials': trials_data['summary']['drugs_with_trials'],
            # Phase 2 additions
            'fda_approved': regulatory_status['summary']['fda_approved'] if regulatory_status else 0,
            'ema_approved': regulatory_status['summary']['ema_approved'] if regulatory_status else 0,
            'total_companies': company_analysis['summary']['total_companies'] if company_analysis else 0,
            # Phase 3 additions
            'drugs_with_safety_data': safety_analysis['summary']['drugs_with_adverse_event_data'] if safety_analysis else 0,
            'drugs_with_boxed_warnings': safety_analysis['summary']['drugs_with_boxed_warnings'] if safety_analysis else 0,
            # Drug discovery metadata (hybrid source tracking)
            'drug_discovery_source': source,  # 'drugbank', 'open_targets', or 'clinicaltrials_gov'
            'drug_discovery_tier': tier,  # 1, 2, 3, or None
            'drug_discovery_strategy': strategy_used,
            # Data quality metrics
            'duplicates_removed': num_duplicates,
            'high_quality_drugs': high_quality,
            'medium_quality_drugs': medium_quality,
            'low_quality_drugs': low_quality,
            'deduplicated_drugs': deduplicated_count,
            'avg_confidence_score': round(avg_confidence, 2)
        },
        'drugs': drugs_with_quality,  # Return deduplicated drugs with quality metrics
        'phase_distribution': get_phase_distribution_summary(trials_data['phase_distribution']),
        'trials_by_drug': trials_data['trials_by_drug'],
        'trial_intelligence': trial_intelligence  # Add intelligence summary
    }

    # Step 12b: Generate radial chart data (Phase B)
    if progress_callback:
        progress_callback(88, "Generating radial chart visualization data...")

    radial_chart = generate_radial_chart_data(
        drugs=drugs_active,
        trials_by_drug=trials_data['trials_by_drug']
    )

    # Step 13: Determine current phase based on features enabled
    if safety_analysis:
        current_phase = 'Phase 3 (Complete)'
    elif regulatory_status or company_analysis:
        current_phase = 'Phase 2'
    else:
        current_phase = 'Phase 1'

    completed_features = [
        'Target resolution',
        'Genetic validation',
        'Drug discovery',
        'Clinical trials'
    ]
    if regulatory_status:
        completed_features.append('Regulatory status')
    if company_analysis:
        completed_features.append('Company analysis')
    if safety_analysis:
        completed_features.append('Safety profiling')

    pending_features = []
    if not regulatory_status or not company_analysis:
        if not regulatory_status:
            pending_features.append('Regulatory status (Phase 2)')
        if not company_analysis:
            pending_features.append('Company analysis (Phase 2)')
    if not safety_analysis:
        pending_features.append('Safety profiling (Phase 3)')

    phase_implementation = {
        'current': current_phase,
        'completed': completed_features,
        'pending': pending_features
    }

    # Step 14: Generate visualization
    if progress_callback:
        progress_callback(90, "Generating visualization...")

    visualization = generate_ascii_visualization(
        target_summary=target_summary,
        genetic_validation=genetic_validation,
        competitive_landscape=competitive_landscape,
        company_analysis=company_analysis,
        safety_analysis=safety_analysis
    )

    if progress_callback:
        progress_callback(100, "Analysis complete!")

    return {
        'query_parameters': {
            'target_name': target_name,
            'gene_symbol': gene_symbol,
            'resolved_gene': resolved_gene,
            'resolved_name': resolved_name
        },
        'target_summary': target_summary,
        'genetic_validation': genetic_validation,
        'competitive_landscape': competitive_landscape,
        'regulatory_status': regulatory_status,
        'company_analysis': company_analysis,
        'safety_analysis': safety_analysis,
        'visualization': visualization,
        'phase_implementation': phase_implementation,
        'radial_chart': radial_chart  # Phase B: Radial chart data for frontend
    }


# CLI execution
if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description='Target Landscape Analysis - Comprehensive competitive intelligence',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python get_target_landscape_analysis.py GLP1R
  python get_target_landscape_analysis.py "GLP-1 receptor"
  python get_target_landscape_analysis.py EGFR --no-phase3
  python get_target_landscape_analysis.py PD-1
        """
    )

    parser.add_argument('target', type=str, nargs='+',
                        help='Target name or gene symbol (e.g., GLP1R, "GLP-1 receptor")')
    parser.add_argument('--no-phase2', action='store_true',
                        help='Disable Phase 2 (regulatory status + company analysis)')
    parser.add_argument('--no-phase3', action='store_true',
                        help='Disable Phase 3 (safety profiling)')

    args = parser.parse_args()

    target_input = " ".join(args.target)

    print(f"\n{'='*80}")
    print(f"TARGET LANDSCAPE ANALYSIS - COMPLETE (Phases 1-3)")
    print(f"{'='*80}\n")

    result = get_target_landscape_analysis(
        target_name=target_input,
        include_company_positioning=not args.no_phase2,  # Enable Phase 2
        include_safety_analysis=not args.no_phase3,  # Enable Phase 3
        progress_callback=create_progress_printer()
    )

    if 'error' in result:
        print(f"\nError: {result['error']}")
        sys.exit(1)

    print("\n" + result['visualization'])
    print(format_summary_stats(result))

    phase_msg = result['phase_implementation']['current']
    print("\n" + "="*80)
    print(f"{phase_msg} Implementation Complete!")
    print("="*80)
