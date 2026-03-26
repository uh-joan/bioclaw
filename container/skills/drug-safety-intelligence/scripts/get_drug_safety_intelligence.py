#!/usr/bin/env python3
"""
Drug Safety Intelligence - Main entry point & orchestrator.

Answers: "What are the known and emerging safety liabilities for [drug / target / drug class]?"

Orchestrates all analysis modules:
1. Drug Resolution (DrugBank target search -> drug list)
2. Target Biology (OpenTargets expression, KO phenotypes)
3. Label Comparison (FDA/EMA cross-class label analysis)
4. Trial Safety Signals (CT.gov terminated/suspended)
5. Literature Synthesis (PubMed + bioRxiv)
6. Interaction Analysis (DrugBank DDI, CYP450, food)
7. Epidemiology Context (CDC/WHO background rates)
8. Risk Matrix (4-dim scoring + recommendations)

Usage:
    python3 scripts/get_drug_safety_intelligence.py "BTK"
    python3 scripts/get_drug_safety_intelligence.py --drug "ibrutinib"
    python3 scripts/get_drug_safety_intelligence.py --class "checkpoint inhibitors"

Ported from riot-flames for BioClaw container execution.
"""

import sys
import os
import argparse
from typing import Dict, Any, List, Optional

# Add script directory to path for local imports
_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _script_dir)

from mcp_client import McpClient
from progress_tracker import create_progress_tracker
from target_biology import analyze_target_biology
from label_comparator import compare_labels
from trial_safety_scanner import scan_trial_safety_signals
from literature_synthesizer import synthesize_literature
from interaction_analyzer import analyze_interactions
from epidemiology_context import get_epidemiology_context
from risk_matrix_builder import build_risk_matrix
from visualization_utils import generate_full_report
from dynamic_vocabulary import (
    fetch_faers_top_aes,
    faers_terms_to_warning_vocabulary,
    faers_terms_to_ar_vocabulary,
    build_canonical_map_from_faers,
    fuzzy_match_to_faers,
)


def _title_case_drug(name: str) -> str:
    """Normalize drug name to title case."""
    if not name:
        return name
    return name[0].upper() + name[1:].lower() if len(name) > 1 else name.upper()


def _resolve_drugs_via_opentargets(
    opentargets_search_func,
    opentargets_get_target_func,
    target_name: str,
    min_phase: int = 3,
) -> List[str]:
    """Resolve target name to drug list via OpenTargets knownDrugs.

    This is the PRIMARY drug resolution method (DrugBank is unreliable).
    OpenTargets get_target_details returns knownDrugs with prefName and phase.
    """
    try:
        # Step 1: Search for the target to get Ensembl gene ID
        search_result = opentargets_search_func(method='search_targets', query=target_name, size=5)
        if not search_result:
            return []

        # Navigate response to find the target ID
        hits = []
        data = search_result.get('data', {})
        search_data = data.get('search', {})
        hits = search_data.get('hits', [])

        if not hits:
            return []

        # Use first hit (best match)
        target_id = hits[0].get('id', '')
        if not target_id:
            return []

        # Step 2: Get target details with knownDrugs
        details = opentargets_get_target_func(method='get_target_details', id=target_id)
        if not details:
            return []

        # Navigate to knownDrugs
        target_data = details.get('data', {}).get('target', {})
        known_drugs = target_data.get('knownDrugs', {})
        rows = known_drugs.get('rows', [])

        # Extract unique drug names at or above min_phase
        seen = set()
        drugs = []
        for row in rows:
            name = row.get('prefName', '')
            phase = row.get('phase', 0)
            drug_type = row.get('drugType', '')

            if not name or phase < min_phase:
                continue

            # Normalize: skip salt forms / duplicates
            name_lower = name.lower()
            base_name = name_lower.split(' ')[0]  # "acalabrutinib maleate" → "acalabrutinib"

            if base_name in seen:
                continue
            seen.add(base_name)

            # Skip non-small-molecule unless explicitly relevant
            clean_name = _title_case_drug(base_name)
            if len(clean_name) <= 80:
                drugs.append(clean_name)

        return drugs

    except Exception as e:
        print(f"  Warning: OpenTargets drug resolution failed: {e}")
        return []


def _resolve_drugs_via_chembl(
    chembl_drug_search_func,
    chembl_get_mechanism_func,
    chembl_target_search_func,
    drug_name: str,
) -> List[str]:
    """Resolve a drug name to class peers via ChEMBL mechanism of action.

    Flow: drug_search(name) → get_mechanism(chembl_id) → target_chembl_id
          → find other drugs with same target via bioactivity.
    """
    drugs = [drug_name]
    try:
        # Step 1: Find the drug in ChEMBL
        result = chembl_drug_search_func(method='drug_search', query=drug_name, limit=5)
        if not result or not result.get('results'):
            return drugs

        # Find the matching drug
        chembl_id = None
        for r in result['results']:
            pref_name = (r.get('pref_name', '') or '').lower()
            if pref_name == drug_name.lower():
                chembl_id = r.get('molecule_chembl_id')
                break
        if not chembl_id and result['results']:
            chembl_id = result['results'][0].get('molecule_chembl_id')

        if not chembl_id:
            return drugs

        # Step 2: Get mechanism to find target
        mech = chembl_get_mechanism_func(method='get_mechanism', chembl_id=chembl_id)
        if not mech or not mech.get('mechanisms'):
            return drugs

        target_chembl_id = mech['mechanisms'][0].get('target_chembl_id')
        moa = mech['mechanisms'][0].get('mechanism_of_action', '')

        if not target_chembl_id:
            return drugs

        # Step 3: Search for the target to get its name, then search drugs
        target_result = chembl_target_search_func(
            method='target_search', query=target_chembl_id, limit=1
        )
        target_name = ''
        if target_result and target_result.get('targets'):
            target_name = target_result['targets'][0].get('pref_name', '')

        # For now, return what we have — ChEMBL doesn't easily enumerate
        # all drugs by target without heavy API calls
        return drugs

    except Exception as e:
        print(f"  Warning: ChEMBL drug resolution failed: {e}")
        return drugs


def _resolve_drugs_from_drugbank(drugbank_search_func, target_name: str) -> List[str]:
    """Resolve target name to list of drug names via DrugBank (legacy fallback)."""
    try:
        result = drugbank_search_func(method='search_by_target', query=target_name, limit=20)
        if not result:
            return []

        results = result.get('results', [])
        if not results:
            return []

        drugs = []
        for drug in results:
            name = drug.get('name', '')
            if name and len(name) <= 80:
                drugs.append(name)

        return drugs

    except Exception as e:
        print(f"  Warning: DrugBank target search failed: {e}")
        return []


def _resolve_drugs_from_name_drugbank(drugbank_search_func, drug_name: str) -> List[str]:
    """Resolve a single drug name and find class peers via DrugBank (legacy fallback)."""
    drugs = [drug_name]

    try:
        result = drugbank_search_func(method='search_by_name', query=drug_name, limit=3)
        if not result or 'results' not in result:
            return drugs

        results = result.get('results', [])
        if not results:
            return drugs

        drugbank_id = None
        for drug in results:
            if drug.get('name', '').lower() == drug_name.lower():
                drugbank_id = drug.get('drugbank_id')
                break
        if not drugbank_id and results:
            drugbank_id = results[0].get('drugbank_id')

        if not drugbank_id:
            return drugs

        details = drugbank_search_func(method='get_drug_details', drugbank_id=drugbank_id)
        if not details or 'drug' not in details:
            return drugs

        drug_data = details.get('drug', {})
        targets = drug_data.get('targets', [])

        if targets:
            primary_target = None
            if isinstance(targets, list) and len(targets) > 0:
                first_target = targets[0]
                if isinstance(first_target, dict):
                    primary_target = first_target.get('name', first_target.get('gene_name', ''))
                elif isinstance(first_target, str):
                    primary_target = first_target

            if primary_target:
                peer_drugs = _resolve_drugs_from_drugbank(drugbank_search_func, primary_target)
                for peer in peer_drugs:
                    if peer.lower() != drug_name.lower() and peer not in drugs:
                        drugs.append(peer)

    except Exception as e:
        print(f"  Warning: Drug peer resolution failed: {e}")

    return drugs


def get_drug_safety_intelligence(
    drug_name: str = None,
    target_name: str = None,
    drug_class: str = None,
    include_target_biology: bool = True,
    include_label_comparison: bool = True,
    include_trial_signals: bool = True,
    include_literature: bool = True,
    include_interactions: bool = True,
    include_epidemiology: bool = False,
    mcp_funcs: Optional[Dict] = None,
    progress_callback=None,
) -> Dict[str, Any]:
    """
    Main orchestrator for drug safety intelligence analysis.

    Args:
        drug_name: Single drug name (e.g., "ibrutinib")
        target_name: Target name (e.g., "BTK", "GLP-1 receptor")
        drug_class: Drug class name (e.g., "BTK inhibitors")
        include_target_biology: Analyze target biology
        include_label_comparison: Compare FDA/EMA labels
        include_trial_signals: Search terminated/suspended trials
        include_literature: Search PubMed + bioRxiv
        include_interactions: Analyze drug-drug interactions
        include_epidemiology: Get epidemiology context
        mcp_funcs: Dict of MCP functions (injected by server)
        progress_callback: Callback(percent, message)

    Returns:
        Comprehensive dict with all analysis results + ASCII visualization
    """
    if not drug_name and not target_name and not drug_class:
        return {'error': 'Must provide drug_name, target_name, or drug_class'}

    # BioClaw adaptation: auto-init MCP functions via McpClient if not injected
    if not mcp_funcs:
        _clients = {}
        mcp_funcs = {}
        _server_map = {
            'drugbank': ('drugbank_info', {
                'drugbank_search': {'method': 'search_by_target'},
            }),
            'fda': ('fda_info', {
                'fda_lookup': {'method': 'lookup_drug'},
            }),
            'ema': ('ema_data', {
                'ema_search': {'method': 'search_medicines'},
            }),
            'opentargets': ('opentargets_info', {
                'opentargets_search': {'method': 'search_targets'},
                'opentargets_get_target': {'method': 'get_target'},
                'opentargets_get_associations': {'method': 'get_associations'},
            }),
            'ctgov': ('ct_gov_studies', {
                'ctgov_search': {'method': 'search'},
            }),
            'pubmed': ('pubmed_articles', {
                'pubmed_search': {'method': 'search_keywords'},
            }),
            'biorxiv': ('biorxiv_data', {
                'biorxiv_search': {},
            }),
            'cdc': ('cdc_health_data', {
                'cdc_health_data': {},
            }),
            'chembl': ('chembl_info', {
                'chembl_drug_search': {'method': 'molecule_search'},
                'chembl_get_mechanism': {'method': 'mechanism_search'},
                'chembl_target_search': {'method': 'target_search'},
                'chembl_get_admet': {'method': 'molecule_search'},
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
            except Exception as e:
                pass  # Optional servers silently skipped
        print(f"  BioClaw MCP: {len(mcp_funcs)} functions loaded")

    # Extract MCP functions (now populated from either injection or auto-init)
    drugbank_search = mcp_funcs.get('drugbank_search')
    fda_lookup = mcp_funcs.get('fda_lookup')
    ema_search = mcp_funcs.get('ema_search')
    opentargets_search = mcp_funcs.get('opentargets_search')
    opentargets_get_target = mcp_funcs.get('opentargets_get_target')
    opentargets_get_associations = mcp_funcs.get('opentargets_get_associations')
    ctgov_search = mcp_funcs.get('ctgov_search')
    pubmed_search = mcp_funcs.get('pubmed_search')
    biorxiv_search = mcp_funcs.get('biorxiv_search')
    cdc_health_data = mcp_funcs.get('cdc_health_data')
    who_health_data = mcp_funcs.get('who_health_data')
    chembl_drug_search = mcp_funcs.get('chembl_drug_search')
    chembl_get_mechanism = mcp_funcs.get('chembl_get_mechanism')
    chembl_target_search = mcp_funcs.get('chembl_target_search')
    chembl_get_admet = mcp_funcs.get('chembl_get_admet')

    # Initialize progress tracker
    tracker = create_progress_tracker(
        callback=progress_callback,
        include_epidemiology=include_epidemiology,
    )

    # =========================================================================
    # Step 1: Drug Resolution (multi-source: OpenTargets → DrugBank → ChEMBL)
    # =========================================================================
    tracker.start_step('drug_resolution', "Resolving drug/target to drug list...")

    drug_names = []
    resolved_target = target_name
    query_description = ''

    if target_name:
        query_description = f"Target: {target_name}"
        resolved_target = target_name

        # PRIMARY: OpenTargets knownDrugs (most reliable for target→drug resolution)
        if opentargets_search and opentargets_get_target:
            tracker.update_step(0.2, f"Searching OpenTargets for {target_name} drugs...")
            drug_names = _resolve_drugs_via_opentargets(
                opentargets_search, opentargets_get_target, target_name, min_phase=3
            )

        # FALLBACK: DrugBank
        if not drug_names and drugbank_search:
            tracker.update_step(0.5, "OpenTargets empty, trying DrugBank...")
            drug_names = _resolve_drugs_from_drugbank(drugbank_search, target_name)

        tracker.update_step(0.8, f"Found {len(drug_names)} drugs targeting {target_name}")

    elif drug_class:
        query_description = f"Class: {drug_class}"
        resolved_target = drug_class

        # Try OpenTargets first (strip "inhibitors" etc. to get target name)
        class_target = drug_class
        for suffix in [' inhibitors', ' inhibitor', ' agonists', ' agonist',
                       ' antagonists', ' antagonist', ' blockers', ' blocker',
                       ' modulators', ' modulator']:
            if drug_class.lower().endswith(suffix):
                class_target = drug_class[:len(drug_class) - len(suffix)].strip()
                break

        if opentargets_search and opentargets_get_target:
            tracker.update_step(0.2, f"Searching OpenTargets for {class_target} drugs...")
            drug_names = _resolve_drugs_via_opentargets(
                opentargets_search, opentargets_get_target, class_target, min_phase=3
            )

        if not drug_names and drugbank_search:
            tracker.update_step(0.5, "Trying DrugBank...")
            drug_names = _resolve_drugs_from_drugbank(drugbank_search, drug_class)

        tracker.update_step(0.8, f"Found {len(drug_names)} drugs in class {drug_class}")

    elif drug_name:
        query_description = f"Drug: {drug_name}"
        drug_names = [drug_name]

        # Try to find class peers via ChEMBL mechanism → target name → OpenTargets
        if chembl_drug_search and chembl_get_mechanism:
            tracker.update_step(0.2, f"Looking up {drug_name} mechanism via ChEMBL...")
            try:
                # Find ChEMBL ID
                cresult = chembl_drug_search(method='drug_search', query=drug_name, limit=3)
                if cresult and cresult.get('results'):
                    chembl_id = None
                    for r in cresult['results']:
                        if (r.get('pref_name', '') or '').lower() == drug_name.lower():
                            chembl_id = r.get('molecule_chembl_id')
                            break
                    if not chembl_id:
                        chembl_id = cresult['results'][0].get('molecule_chembl_id')

                    if chembl_id:
                        # Get mechanism to find target
                        mech = chembl_get_mechanism(method='get_mechanism', chembl_id=chembl_id)
                        if mech and mech.get('mechanisms'):
                            target_chembl_id = mech['mechanisms'][0].get('target_chembl_id', '')
                            moa = mech['mechanisms'][0].get('mechanism_of_action', '')

                            # Get target preferred name from ChEMBL
                            target_search_name = ''
                            if target_chembl_id and chembl_target_search:
                                tresult = chembl_target_search(
                                    method='target_search', query=target_chembl_id, limit=1
                                )
                                if tresult and tresult.get('targets'):
                                    target_info = tresult['targets'][0]
                                    target_search_name = target_info.get('pref_name', '')
                                    # Also try gene symbol from target components
                                    components = target_info.get('target_components', [])
                                    if components and isinstance(components, list):
                                        for comp in components:
                                            if isinstance(comp, dict):
                                                gene = comp.get('accession', '')
                                                if gene:
                                                    target_search_name = gene
                                                    break

                            # Search OpenTargets using target name
                            if target_search_name and opentargets_search and opentargets_get_target:
                                tracker.update_step(0.5, f"Found target '{target_search_name}', searching peers...")
                                resolved_target = target_search_name
                                peers = _resolve_drugs_via_opentargets(
                                    opentargets_search, opentargets_get_target,
                                    target_search_name, min_phase=3
                                )
                                for peer in peers:
                                    if peer.lower() != drug_name.lower() and peer not in drug_names:
                                        drug_names.append(peer)

                            # Fallback: try MoA text directly with OpenTargets
                            if len(drug_names) <= 1 and moa and opentargets_search and opentargets_get_target:
                                import re
                                # Clean MoA for search: remove "inhibitor/agonist" suffix
                                clean_moa = re.sub(
                                    r'\s*(inhibitor|agonist|antagonist|blocker|modulator)$',
                                    '', moa, flags=re.IGNORECASE
                                ).strip()
                                if clean_moa and len(clean_moa) > 3:
                                    tracker.update_step(0.6, f"Trying MoA: '{clean_moa}'...")
                                    resolved_target = clean_moa
                                    peers = _resolve_drugs_via_opentargets(
                                        opentargets_search, opentargets_get_target,
                                        clean_moa, min_phase=3
                                    )
                                    for peer in peers:
                                        if peer.lower() != drug_name.lower() and peer not in drug_names:
                                            drug_names.append(peer)
            except Exception as e:
                print(f"  Warning: ChEMBL peer resolution failed: {e}")

        # DrugBank fallback for peer discovery
        if len(drug_names) <= 1 and drugbank_search:
            tracker.update_step(0.6, "Trying DrugBank for peers...")
            db_drugs = _resolve_drugs_from_name_drugbank(drugbank_search, drug_name)
            for d in db_drugs:
                if d not in drug_names:
                    drug_names.append(d)

        tracker.update_step(0.8, f"Found {len(drug_names)} drugs (including class peers)")

    if not drug_names:
        # Ultimate fallback: use input directly
        if drug_name:
            drug_names = [drug_name]
        elif target_name:
            drug_names = [target_name]
        elif drug_class:
            drug_names = [drug_class]

    tracker.complete_step(f"Resolved {len(drug_names)} drugs: {', '.join(drug_names[:8])}")

    input_summary = {
        'drug_name': drug_name,
        'target_name': target_name,
        'drug_class': drug_class,
        'resolved_target': resolved_target,
        'drug_names': drug_names,
        'query_description': query_description,
    }

    # =========================================================================
    # Step 2: Target Biology (OpenTargets)
    # =========================================================================
    target_biology_result = None
    if include_target_biology and opentargets_search and resolved_target:
        target_biology_result = analyze_target_biology(
            opentargets_search_func=opentargets_search,
            opentargets_get_target_func=opentargets_get_target or opentargets_search,
            opentargets_get_associations_func=opentargets_get_associations,
            target_name=resolved_target,
            tracker=tracker,
        )
    elif include_target_biology:
        tracker.start_step('target_biology', "Skipping target biology (no OpenTargets)")
        tracker.complete_step("Skipped: OpenTargets not available")

    # =========================================================================
    # Step 2b: FAERS Dynamic Vocabulary (feeds into label comparison + risk matrix)
    # =========================================================================
    faers_terms = []
    faers_warning_stems = None
    faers_ar_terms = None
    canonical_map = None
    if fda_lookup and drug_names:
        try:
            faers_terms = fetch_faers_top_aes(fda_lookup, drug_names, limit=50)
            if faers_terms:
                faers_warning_stems = faers_terms_to_warning_vocabulary(faers_terms)
                faers_ar_terms = faers_terms_to_ar_vocabulary(faers_terms)
                canonical_map = build_canonical_map_from_faers(faers_terms)
        except Exception as e:
            print(f"  Warning: FAERS vocabulary build failed: {e}")

    # =========================================================================
    # Step 3: Label Comparison (FDA + EMA)
    # =========================================================================
    label_data = None
    if include_label_comparison and fda_lookup:
        label_data = compare_labels(
            fda_lookup_func=fda_lookup,
            ema_search_func=ema_search,
            drug_names=drug_names,
            tracker=tracker,
            faers_warning_stems=faers_warning_stems,
            faers_ar_terms=faers_ar_terms,
        )
    elif include_label_comparison:
        tracker.start_step('label_comparison', "Skipping labels (no FDA)")
        tracker.complete_step("Skipped: FDA not available")

    # =========================================================================
    # Step 4: Trial Safety Signals (CT.gov)
    # =========================================================================
    trial_signals = None
    if include_trial_signals and ctgov_search:
        trial_signals = scan_trial_safety_signals(
            ctgov_search_func=ctgov_search,
            drug_names=drug_names,
            target_name=resolved_target,
            tracker=tracker,
        )
    elif include_trial_signals:
        tracker.start_step('trial_signals', "Skipping trials (no CT.gov)")
        tracker.complete_step("Skipped: CT.gov not available")

    # =========================================================================
    # Step 5: Literature Synthesis (PubMed + bioRxiv)
    # =========================================================================
    literature_data = None
    if include_literature and pubmed_search:
        literature_data = synthesize_literature(
            pubmed_search_func=pubmed_search,
            biorxiv_search_func=biorxiv_search,
            drug_names=drug_names,
            target_name=resolved_target,
            tracker=tracker,
        )
    elif include_literature:
        tracker.start_step('literature', "Skipping literature (no PubMed)")
        tracker.complete_step("Skipped: PubMed not available")

    # =========================================================================
    # Step 6: Interaction Analysis (DrugBank + ChEMBL fallback)
    # =========================================================================
    interaction_data = None
    if include_interactions and (drugbank_search or chembl_get_admet):
        interaction_data = analyze_interactions(
            drugbank_search_func=drugbank_search,
            drug_names=drug_names,
            tracker=tracker,
            chembl_get_admet_func=chembl_get_admet,
            chembl_drug_search_func=chembl_drug_search,
            chembl_get_mechanism_func=chembl_get_mechanism,
        )
    elif include_interactions:
        tracker.start_step('interactions', "Skipping interactions (no DrugBank or ChEMBL)")
        tracker.complete_step("Skipped: No interaction data sources available")

    # =========================================================================
    # Step 7: Epidemiology Context (CDC + WHO) - Optional
    # =========================================================================
    epidemiology_data = None
    if include_epidemiology and (cdc_health_data or who_health_data):
        # Gather top adverse events for contextualization
        top_events = []
        if label_data:
            for ce in label_data.get('class_effects', [])[:5]:
                top_events.append(ce.get('event', ''))
        if trial_signals:
            for signal in trial_signals.get('safety_signals', [])[:5]:
                top_events.append(signal.get('reason', ''))

        epidemiology_data = get_epidemiology_context(
            cdc_health_data_func=cdc_health_data,
            who_health_data_func=who_health_data,
            adverse_events=top_events,
            tracker=tracker,
        )

    # =========================================================================
    # Step 8: Risk Matrix + Report
    # =========================================================================
    tracker.start_step('risk_matrix', "Building risk matrix...")

    risk_matrix = build_risk_matrix(
        label_data=label_data,
        trial_signals=trial_signals,
        literature_data=literature_data,
        target_biology=target_biology_result,
        interaction_data=interaction_data,
        epidemiology_data=epidemiology_data,
        canonical_map=canonical_map,
        faers_terms=faers_terms,
    )

    tracker.update_step(0.5, "Generating report...")

    # Generate visualization
    visualization = generate_full_report(
        input_summary=input_summary,
        target_biology=target_biology_result,
        label_data=label_data,
        trial_signals=trial_signals,
        literature_data=literature_data,
        interaction_data=interaction_data,
        epidemiology_data=epidemiology_data,
        risk_matrix=risk_matrix,
    )

    tracker.complete_step("Analysis complete!")

    # Print report to console
    print(visualization)

    return {
        'input_summary': input_summary,
        'target_biology': target_biology_result,
        'label_comparison': label_data,
        'trial_signals': trial_signals,
        'literature': literature_data,
        'interactions': interaction_data,
        'epidemiology': epidemiology_data,
        'risk_matrix': risk_matrix,
        'recommendations': risk_matrix.get('recommendations', []),
        'visualization': visualization,
    }


# CLI execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Drug Safety Intelligence Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python get_drug_safety_intelligence.py "BTK"
  python get_drug_safety_intelligence.py --drug ibrutinib
  python get_drug_safety_intelligence.py --target "GLP-1 receptor"
  python get_drug_safety_intelligence.py --drug-class "checkpoint inhibitors"
  python get_drug_safety_intelligence.py "BTK" --include-epidemiology
        """
    )

    parser.add_argument('query', type=str, nargs='*',
                        help='Target name, drug name, or class (positional)')
    parser.add_argument('--drug', type=str, help='Drug name')
    parser.add_argument('--target', type=str, help='Target name')
    parser.add_argument('--drug-class', type=str, help='Drug class name')
    parser.add_argument('--include-epidemiology', action='store_true',
                        help='Include epidemiology context (CDC/WHO)')
    parser.add_argument('--no-target-biology', action='store_true')
    parser.add_argument('--no-labels', action='store_true')
    parser.add_argument('--no-trials', action='store_true')
    parser.add_argument('--no-literature', action='store_true')
    parser.add_argument('--no-interactions', action='store_true')

    args = parser.parse_args()

    # Resolve positional args
    target_name = args.target
    drug_name = args.drug
    drug_class = args.drug_class

    if args.query:
        query = ' '.join(args.query)
        if not target_name and not drug_name and not drug_class:
            # Default: treat positional arg as target name
            target_name = query

    if not target_name and not drug_name and not drug_class:
        parser.error("Must provide a target, drug, or drug class")

    def progress_printer(pct, msg):
        print(f"[{pct:3d}%] {msg}")

    print(f"\n{'=' * 80}")
    print(f"DRUG SAFETY INTELLIGENCE ANALYSIS")
    print(f"{'=' * 80}\n")

    # BioClaw: mcp_funcs=None triggers auto-init via McpClient
    result = get_drug_safety_intelligence(
        drug_name=drug_name,
        target_name=target_name,
        drug_class=drug_class,
        include_target_biology=not args.no_target_biology,
        include_label_comparison=not args.no_labels,
        include_trial_signals=not args.no_trials,
        include_literature=not args.no_literature,
        include_interactions=not args.no_interactions,
        include_epidemiology=args.include_epidemiology,
        progress_callback=progress_printer,
    )

    if 'error' in result:
        print(f"\nError: {result['error']}")
        sys.exit(1)

    # Summary stats
    rm = result.get('risk_matrix', {})
    summary = rm.get('summary', {})
    print(f"\n{'=' * 80}")
    print(f"ANALYSIS COMPLETE")
    print(f"Risks: {summary.get('total_risks_identified', 0)} total "
          f"({summary.get('high_risk_count', 0)} HIGH, "
          f"{summary.get('moderate_risk_count', 0)} MODERATE, "
          f"{summary.get('low_risk_count', 0)} LOW)")
    print(f"{'=' * 80}")
