#!/usr/bin/env python3
"""
Regulatory Precedent & Pathway Analyzer - Main entry point.

Orchestrates all analysis phases:
1. Precedent Discovery (FDA + EMA + CT.gov)
2. No-Precedent Mode (active trial benchmarks) - if <2 approved drugs
3. Pathway Analysis (US + EU submission options)
4. Designations & Special Considerations
5. Visualization (ASCII report)

Usage:
    python3 scripts/get_regulatory_precedent_pathway.py "MASH" --modality "small molecule"
    python3 scripts/get_regulatory_precedent_pathway.py "obesity" --modality "biologic"

Ported from riot-flames for BioClaw container execution.
"""

import sys
import os
import argparse
from typing import Dict, Any, List, Optional

# Add script directory to path for local imports
_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _script_dir)

from regulatory_constants import DEFAULT_REGIONS
from progress_tracker import create_progress_tracker
from precedent_finder import find_precedents
from trial_benchmarker import build_trial_benchmarks
from pathway_analyzer import analyze_pathways
from designations_analyzer import analyze_designations
from patent_scanner import scan_patent_landscape
from visualization_utils import generate_report


def get_regulatory_precedent_pathway(
    indication: str,
    modality: str = None,
    target_regions: List[str] = None,
    drug_name: str = None,
    phase: str = None,
    include_pathway_analysis: bool = True,
    include_designations: bool = True,
    include_patents: bool = True,
    include_rwe: bool = False,
    include_epidemiology: bool = False,
    mcp_funcs: Optional[Dict] = None,
    progress_callback=None,
) -> Dict[str, Any]:
    """
    Main orchestrator for regulatory precedent & pathway analysis.

    Args:
        indication: Disease/condition (e.g., "MASH", "obesity", "Alzheimer's")
        modality: Drug modality (e.g., "small molecule", "biologic", "antibody")
        target_regions: Regions to analyze (default: ["US", "EU"])
        drug_name: Specific drug name if known
        phase: Current development phase
        include_pathway_analysis: Whether to analyze submission pathways
        include_designations: Whether to check designation eligibility
        include_rwe: Whether to include RWE context (future)
        include_epidemiology: Whether to include epidemiology (future)
        mcp_funcs: Dict of MCP functions (injected by server)
        progress_callback: Callback(percent, message) for progress updates

    Returns:
        Comprehensive dict with all analysis results + ASCII visualization
    """
    # Validate indication input
    if not indication or not indication.strip():
        return {
            'indication': indication or '',
            'modality': modality or 'Not specified',
            'target_regions': target_regions or list(DEFAULT_REGIONS),
            'mode': 'error',
            'error': 'No indication provided. Please specify a disease or condition.',
            'visualization': 'ERROR: No indication provided. Please specify a disease or condition to analyze.',
            'provenance': [],
        }

    if target_regions is None:
        target_regions = list(DEFAULT_REGIONS)
    if mcp_funcs is None:
        mcp_funcs = {}

    # Initialize progress tracker
    tracker = create_progress_tracker(
        callback=progress_callback,
        include_rwe=include_rwe,
        include_epidemiology=include_epidemiology,
    )

    result = {
        'indication': indication,
        'modality': modality or 'Not specified',
        'target_regions': target_regions,
        'mode': None,
    }

    # ========================================================================
    # Phase 1: Precedent Discovery
    # ========================================================================
    tracker.start_step('precedent_discovery', f"Phase 1: Searching for approved precedents in {indication}...")

    precedent_data = find_precedents(
        indication=indication,
        target_regions=target_regions,
        mcp_funcs=mcp_funcs,
        progress_callback=lambda p, m: tracker.update_step(p, m),
    )

    result['mode'] = precedent_data['mode']
    result['precedent_data'] = precedent_data

    tracker.complete_step(
        f"Found {precedent_data['unique_drug_count']} unique drugs ({precedent_data['mode']} mode)"
    )

    # If no-precedent mode, build trial benchmarks
    if precedent_data['mode'] == 'no_precedent':
        tracker.update_step(0.8, "Switching to no-precedent mode: building trial benchmarks...")
        benchmark_data = build_trial_benchmarks(
            indication=indication,
            mcp_funcs=mcp_funcs,
            progress_callback=lambda p, m: tracker.update_step(0.8 + p * 0.2, m),
        )
        result['benchmark_data'] = benchmark_data
        tracker.complete_step(f"Built {benchmark_data.get('total_found', 0)} trial benchmarks")

    # ========================================================================
    # Phase 1.5: Patent Landscape
    # ========================================================================
    if include_patents and precedent_data.get('precedents'):
        tracker.start_step('patent_scan', "Phase 1.5: Scanning patent landscape...")
        patent_data = scan_patent_landscape(
            precedents=precedent_data['precedents'],
            mcp_funcs=mcp_funcs,
            progress_callback=lambda p, m: tracker.update_step(p, m),
        )
        result['patent_data'] = patent_data
        tracker.complete_step(
            f"Scanned {len(patent_data.get('drug_patents', []))} drugs: "
            f"{patent_data.get('active_patent_count', 0)} with active patents, "
            f"{patent_data.get('active_exclusivity_count', 0)} with active exclusivity"
        )

    # ========================================================================
    # Phase 2: Pathway Analysis
    # ========================================================================
    if include_pathway_analysis:
        tracker.start_step('pathway_analysis', "Phase 2: Analyzing submission pathways...")

        pathway_data = analyze_pathways(
            indication=indication,
            modality=modality,
            target_regions=target_regions,
            precedents=precedent_data.get('precedents', []),
            mcp_funcs=mcp_funcs,
        )
        result['pathway_data'] = pathway_data

        tracker.complete_step("Pathway analysis complete")

    # ========================================================================
    # Phase 3: Designations & Special Considerations
    # ========================================================================
    if include_designations:
        tracker.start_step('designations', "Phase 3: Analyzing designations & special considerations...")

        designation_data = analyze_designations(
            indication=indication,
            modality=modality,
            target_regions=target_regions,
            precedents=precedent_data.get('precedents', []),
            mcp_funcs=mcp_funcs,
            progress_callback=lambda p, m: tracker.update_step(p, m),
            search_terms=precedent_data.get('search_terms', [indication]),
        )
        result['designation_data'] = designation_data

        tracker.complete_step("Designation analysis complete")

    # ========================================================================
    # Phase 4: RWE Context (future)
    # ========================================================================
    if include_rwe:
        tracker.start_step('rwe', "Phase 4: Gathering real-world evidence context...")
        # TODO: Implement Medicare/Medicaid utilization for precedent drugs
        result['rwe_data'] = {'status': 'not_implemented'}
        tracker.complete_step("RWE context: not yet implemented")

    # ========================================================================
    # Phase 5: Epidemiology (future)
    # ========================================================================
    if include_epidemiology:
        tracker.start_step('epidemiology', "Phase 5: Gathering epidemiology data...")
        # TODO: Implement DataCommons/WHO/CDC prevalence data
        result['epidemiology_data'] = {'status': 'not_implemented'}
        tracker.complete_step("Epidemiology: not yet implemented")

    # ========================================================================
    # Generate Report
    # ========================================================================
    tracker.start_step('report', "Generating regulatory strategy brief...")

    visualization = generate_report(result)
    result['visualization'] = visualization

    tracker.complete_step("Report generated")

    return result


def _build_bioclaw_mcp_funcs() -> Dict:
    """Build mcp_funcs dict using McpClient for BioClaw container/local execution."""
    from mcp_client import McpClient

    clients = {}
    mcp_funcs = {}

    server_map = {
        'fda': ('fda_info', {
            'fda_search': {'method': 'lookup_drug'},
            'fda_get_patent_exclusivity': {'method': 'get_patent_exclusivity'},
        }),
        'ema': ('ema_data', {
            'ema_search': {'method': 'search_medicines'},
        }),
        'ctgov': ('ct_gov_studies', {
            'ctgov_search': {'method': 'search'},
        }),
        'nlm': ('nlm_ct_codes', {
            'nlm_search_codes': {'method': 'conditions'},
        }),
        'opentargets': ('opentargets_info', {
            'opentargets_search': {'method': 'search_diseases'},
        }),
    }

    for srv_name, (tool_name, funcs) in server_map.items():
        try:
            client = McpClient(srv_name)
            client.connect()
            clients[srv_name] = client
            for func_key, defaults in funcs.items():
                def make_fn(c, t, d):
                    def fn(**kw):
                        merged = {**d, **kw}
                        return c.call(t, **merged)
                    return fn
                mcp_funcs[func_key] = make_fn(client, tool_name, defaults)
        except Exception as e:
            print(f"  Warning: {srv_name} MCP not available: {e}")

    print(f"BioClaw MCP: loaded {len(mcp_funcs)} functions")
    return mcp_funcs, clients


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Regulatory Precedent & Pathway Analyzer")
    parser.add_argument("indication", help="Disease/condition to analyze")
    parser.add_argument("--modality", default=None, help="Drug modality (small molecule, biologic, etc.)")
    parser.add_argument("--regions", default="US,EU", help="Comma-separated regions")
    parser.add_argument("--no-pathways", action="store_true", help="Skip pathway analysis")
    parser.add_argument("--no-designations", action="store_true", help="Skip designation analysis")

    args = parser.parse_args()
    regions = [r.strip() for r in args.regions.split(",")]

    def progress(pct, msg):
        print(f"  [{pct:3d}%] {msg}")

    _cli_mcp_funcs, _cli_clients = _build_bioclaw_mcp_funcs()

    result = get_regulatory_precedent_pathway(
        indication=args.indication,
        modality=args.modality,
        target_regions=regions,
        include_pathway_analysis=not args.no_pathways,
        include_designations=not args.no_designations,
        mcp_funcs=_cli_mcp_funcs,
        progress_callback=progress,
    )

    for c in _cli_clients.values():
        c.close()

    print("\n" + result['visualization'])
