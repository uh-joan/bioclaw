#!/usr/bin/env python3
"""Real-world drug utilization analysis from Medicare Part D and Medicaid claims.

Provides prescriber specialty breakdown, spending trends, geographic hotspots,
and NADAC acquisition pricing - data completely missing from consulting reports.
"""

import sys
import os
from datetime import datetime
from collections import defaultdict
from typing import Dict, Any, Optional, List

# Path setup for imports
_this_file = os.path.abspath(__file__)
_scripts_dir = os.path.dirname(_this_file)
_skill_dir = os.path.dirname(_scripts_dir)
_skills_dir = os.path.dirname(_skill_dir)
_claude_dir = os.path.dirname(_skills_dir)

# Add scripts directory for local imports
sys.path.insert(0, _scripts_dir)

# BioClaw adaptation
from mcp_client import McpClient

# Local imports
from progress_tracker import create_progress_tracker
from constants import (
    US_STATES,
    TOP_STATES_BY_POPULATION,
    MEDICAID_FORMULARY_STATES,
    normalize_drug_name,
    get_brand_names,
    normalize_specialty,
    get_state_name,
    format_currency,
    format_number,
)
from visualization_utils import build_full_visualization


def get_real_world_utilization_analysis(
    drug_name: str,
    include_prescriber_analysis: bool = True,
    include_spending_trends: bool = True,
    include_geographic_breakdown: bool = True,
    include_nadac_pricing: bool = True,
    include_medicaid: bool = True,
    include_asp_pricing: bool = True,
    include_drug_interactions: bool = True,
    include_fda_safety: bool = True,
    include_switching_analysis: bool = True,
    include_part_b_spending: bool = True,  # NEW: Part B spending for IV drugs
    top_states: int = 10,
    top_specialties: int = 10,
    progress_callback=None,
    mcp_funcs: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Analyze real-world drug utilization from Medicare and Medicaid claims.

    Args:
        drug_name: Drug name to analyze (brand or generic)
        include_prescriber_analysis: Include specialty breakdown
        include_spending_trends: Include Medicare/Medicaid spending
        include_geographic_breakdown: Include state-level analysis
        include_nadac_pricing: Include NADAC acquisition cost data
        include_medicaid: Include Medicaid utilization data
        include_asp_pricing: Include Medicare Part B ASP reimbursement data
        include_drug_interactions: Include DrugBank drug-drug interactions
        include_fda_safety: Include FDA safety context (recalls, shortages)
        include_switching_analysis: Include competitive switching analysis
        include_part_b_spending: Include Medicare Part B spending (for IV/infusion drugs)
        top_states: Number of top states to show
        top_specialties: Number of top specialties to show
        progress_callback: Function for progress updates (percent, message)

    Returns:
        dict: Complete utilization analysis with visualization
    """
    # Initialize progress tracker
    progress = create_progress_tracker(
        callback=progress_callback,
        skip_medicaid=not include_medicaid
    )

    # BioClaw: auto-init MCP functions via McpClient if not injected
    if not mcp_funcs:
        _clients = {}
        mcp_funcs = {}
        _server_map = {
            'medicare': ('medicare_info', {
                'medicare_prescribers': {'method': 'search_prescribers'},
                'medicare_spending': {'method': 'search_spending'},
                'medicare_asp_pricing': {'method': 'get_asp_pricing'},
            }),
            'medicaid': ('medicaid_info', {
                'medicaid_info': {},
            }),
            'nlm': ('nlm_ct_codes', {
                'nlm_search_codes': {},
            }),
            'drugbank': ('drugbank_info', {
                'drugbank_search': {},
            }),
            'fda': ('fda_info', {
                'fda_lookup': {'method': 'lookup_drug'},
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

    medicare_prescribers = mcp_funcs.get('medicare_prescribers')
    medicare_spending = mcp_funcs.get('medicare_spending')
    medicare_asp_pricing = mcp_funcs.get('medicare_asp_pricing')
    medicaid_info = mcp_funcs.get('medicaid_info')
    nlm_search_codes = mcp_funcs.get('nlm_search_codes')
    drugbank_search_func = mcp_funcs.get('drugbank_search')
    fda_lookup_func = mcp_funcs.get('fda_lookup')
    datacommons_observations = mcp_funcs.get('datacommons_observations')

    # Initialize result structure
    result = {
        "drug_name": drug_name,
        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "summary": {},
        "prescriber_analysis": {},
        "patient_demographics": {},
        "geographic_analysis": {},
        "spending_trends": {},
        "nadac_pricing": {},
        "asp_pricing": {},
        "drug_interactions": {},
        "fda_safety": {},
        "medicaid_utilization": {},
        "switching_analysis": {},
        "visualization": "",
        # NEW: Data provenance tracking
        "data_sources": {
            "medicare_part_d_year": None,
            "medicare_part_b_year": None,
            "medicaid_year": None,
            "nadac_effective_date": None,
            "data_lag_warning": "Medicare data is typically 18-24 months behind current date",
        },
        # NEW: Drug administration route detection
        "drug_characteristics": {
            "administration_routes": [],
            "is_iv_infusion": False,
            "part_b_relevant": False,
            "route_warning": None,
        },
        # NEW: Data caveats
        "data_caveats": [],
    }

    # Normalize drug name
    generic_name = normalize_drug_name(drug_name)
    brand_names = get_brand_names(generic_name)

    progress.start_step('init', f"Analyzing utilization for {drug_name}...")
    print(f"\n{'=' * 60}")
    print(f"REAL-WORLD UTILIZATION ANALYSIS: {drug_name.upper()}")
    print(f"{'=' * 60}")
    print(f"Generic name: {generic_name}")
    if brand_names:
        print(f"Brand names: {', '.join(brand_names)}")

    # =========================================================================
    # NEW: Drug Administration Route Detection
    # =========================================================================
    # Detect if drug is IV/infusion (Part B relevant) vs oral/SC (Part D relevant)
    is_iv_drug = False
    administration_routes = []

    if drugbank_search_func:
        try:
            db_search = drugbank_search_func(method='search_by_name', query=drug_name, limit=3)
            if db_search and 'results' in db_search:
                for drug_result in db_search.get('results', []):
                    drug_name_lower = drug_result.get('name', '').lower()
                    if drug_name_lower == drug_name.lower() or (generic_name and drug_name_lower == generic_name.lower()):
                        db_id = drug_result.get('drugbank_id')
                        if db_id:
                            details = drugbank_search_func(method='get_drug_details', drugbank_id=db_id)
                            if details and 'drug' in details:
                                routes = details['drug'].get('routes', [])
                                administration_routes = routes if routes else []

                                # Check for IV/infusion routes
                                iv_keywords = ['intravenous', 'iv', 'infusion', 'injection', 'parenteral']
                                for route in administration_routes:
                                    if any(kw in route.lower() for kw in iv_keywords):
                                        is_iv_drug = True
                                        break
                        break
        except Exception as e:
            print(f"  Note: Could not detect administration route: {e}")

    result['drug_characteristics'] = {
        'administration_routes': administration_routes,
        'is_iv_infusion': is_iv_drug,
        'part_b_relevant': is_iv_drug,
        'route_warning': None,
    }

    if is_iv_drug:
        warning_msg = (
            f"⚠️ {drug_name.upper()} is primarily administered via IV/infusion. "
            "Most utilization is captured in Medicare Part B (physician-administered), "
            "NOT Part D (retail pharmacy). Part D figures may represent <10% of actual Medicare spending."
        )
        result['drug_characteristics']['route_warning'] = warning_msg
        result['data_caveats'].append(warning_msg)
        print(f"\n  {warning_msg}")

    if administration_routes:
        print(f"  Administration routes: {', '.join(administration_routes)}")

    # Track totals
    total_medicare_spending = 0
    total_medicare_claims = 0
    total_medicare_beneficiaries = 0
    total_prescribers = 0

    # =========================================================================
    # Phase 2: Medicare Part D Prescriber Analysis
    # =========================================================================
    prescriber_data = []
    specialty_aggregates = defaultdict(lambda: {
        'total_claims': 0,
        'total_beneficiaries': 0,
        'total_drug_cost': 0,
        'provider_count': 0,
        'npis': set(),  # Track unique NPIs
    })

    # Demographics tracking (Phase 1 improvement)
    demographics_totals = {
        'age_under_65': 0,
        'age_65_74': 0,
        'age_75_84': 0,
        'age_85_plus': 0,
        'female': 0,
        'male': 0,
        'dual_eligible': 0,
        'non_dual': 0,
        'low_income_subsidy': 0,
    }

    # Track all prescriber records for concentration analysis (Phase 2 improvement)
    all_prescriber_records = []

    if include_prescriber_analysis:
        progress.start_step('prescriber_search', "Collecting Medicare Part D prescriber data...")
        print(f"\n{'─' * 60}")
        print("Collecting Medicare Part D prescriber data...")

        try:
            # Search for prescribers of this drug
            prescriber_result = medicare_prescribers(
                drug_name=drug_name,
                size=1000  # Get substantial sample
            )

            # Handle Medicare MCP response format: {'prescribers': [...], 'total': N}
            records = []
            if prescriber_result:
                if 'prescribers' in prescriber_result:
                    records = prescriber_result.get('prescribers', [])
                elif 'data' in prescriber_result:
                    records = prescriber_result.get('data', [])

            print(f"  Found {len(records)} prescriber records")

            # Aggregate by specialty
            for record in records:
                # Handle Medicare field names: prescriber_type, total_claims, total_drug_cost
                specialty_raw = record.get('prescriber_type', record.get('prscrbr_type', 'Unknown'))
                specialty = normalize_specialty(specialty_raw)

                # Parse claims (may be string)
                claims_val = record.get('total_claims', record.get('tot_clms', 0))
                claims = int(float(claims_val)) if claims_val else 0

                # Parse beneficiaries (may be empty string)
                bene_val = record.get('total_beneficiaries', record.get('tot_benes', ''))
                beneficiaries = int(float(bene_val)) if bene_val and bene_val != '' else 0

                # Parse drug cost
                cost_val = record.get('total_drug_cost', record.get('tot_drug_cst', 0))
                drug_cost = float(cost_val) if cost_val else 0

                # Track unique NPIs for provider count
                npi = record.get('npi', '')

                specialty_aggregates[specialty]['total_claims'] += claims
                specialty_aggregates[specialty]['total_beneficiaries'] += beneficiaries
                specialty_aggregates[specialty]['total_drug_cost'] += drug_cost
                if npi:
                    specialty_aggregates[specialty]['npis'].add(npi)

                total_medicare_claims += claims
                total_medicare_beneficiaries += beneficiaries
                total_medicare_spending += drug_cost

                # Extract demographics (Phase 1 improvement)
                # Age bands - Medicare Part D uses these field names
                def safe_int(val):
                    """Safely convert value to int, handling empty strings and None."""
                    if val is None or val == '':
                        return 0
                    try:
                        return int(float(val))
                    except (ValueError, TypeError):
                        return 0

                # Note: Demographics come from separate API call with include_demographics=True
                # The drug-level dataset doesn't have these fields, they're extracted later

                # Store for concentration analysis (Phase 2 improvement)
                if claims > 0:
                    all_prescriber_records.append({
                        'npi': npi,
                        'specialty': specialty,
                        'claims': claims,
                        'beneficiaries': beneficiaries,
                        'drug_cost': drug_cost,
                        'state': record.get('state', record.get('prscrbr_state_abrvtn', '')),
                    })

            # Count unique prescribers
            all_npis = set()
            for data in specialty_aggregates.values():
                all_npis.update(data['npis'])
            total_prescribers = len(all_npis)

            # Fetch demographics from provider-level dataset
            # Since drug-level dataset doesn't have demographics, we fetch from
            # the top prescribing specialties to get a representative sample
            if total_prescribers > 0 and specialty_aggregates:
                print(f"\n  Fetching patient demographics...")
                try:
                    # Get top specialties for this drug (sorted by claims)
                    top_specialties_for_demo = [spec for spec, data in sorted(
                        specialty_aggregates.items(),
                        key=lambda x: x[1]['total_claims'],
                        reverse=True
                    )[:3] if data['total_claims'] > 0]

                    for specialty in top_specialties_for_demo:
                        demo_result = medicare_prescribers(
                            prescriber_type=specialty,
                            size=500,
                            include_demographics=True
                        )

                        if demo_result and 'prescribers' in demo_result:
                            for record in demo_result['prescribers']:
                                demographics_totals['age_under_65'] += safe_int(record.get('bene_age_lt_65_cnt', 0))
                                demographics_totals['age_65_74'] += safe_int(record.get('bene_age_65_74_cnt', 0))
                                demographics_totals['age_75_84'] += safe_int(record.get('bene_age_75_84_cnt', 0))
                                demographics_totals['age_85_plus'] += safe_int(record.get('bene_age_gt_84_cnt', 0))
                                demographics_totals['female'] += safe_int(record.get('bene_feml_cnt', 0))
                                demographics_totals['male'] += safe_int(record.get('bene_male_cnt', 0))
                                demographics_totals['dual_eligible'] += safe_int(record.get('bene_dual_cnt', 0))
                                demographics_totals['non_dual'] += safe_int(record.get('bene_ndual_cnt', 0))
                                # Note: LIS is returned as lis_claims/lis_drug_cost, not bene_lis_cnt
                    print(f"    Collected demographics from {len(top_specialties_for_demo)} specialty groups")
                except Exception as demo_err:
                    print(f"  Warning: Could not fetch demographics: {demo_err}")

            # Convert to sorted list
            for specialty, data in specialty_aggregates.items():
                pct = (data['total_claims'] / total_medicare_claims * 100) if total_medicare_claims > 0 else 0
                prescriber_data.append({
                    'specialty': specialty,
                    'total_claims': data['total_claims'],
                    'total_beneficiaries': data['total_beneficiaries'],
                    'total_drug_cost': data['total_drug_cost'],
                    'provider_count': len(data['npis']),
                    'pct_of_claims': pct,
                })

            # Sort by claims descending
            prescriber_data.sort(key=lambda x: x['total_claims'], reverse=True)

            # Show top specialties
            if prescriber_data:
                print(f"\n  Top Prescribing Specialties:")
                for i, item in enumerate(prescriber_data[:5], 1):
                    print(f"    {i}. {item['specialty']}: {item['pct_of_claims']:.1f}% ({format_number(item['total_claims'])} claims)")

                print(f"\n  Total Spending from Prescribers: {format_currency(total_medicare_spending)}")

        except Exception as e:
            print(f"  Warning: Error collecting prescriber data: {e}")
            import traceback
            traceback.print_exc()

        progress.complete_step("Prescriber analysis complete")

    # Calculate demographics percentages (Phase 1 improvement)
    total_age = (demographics_totals['age_under_65'] + demographics_totals['age_65_74'] +
                 demographics_totals['age_75_84'] + demographics_totals['age_85_plus'])
    total_gender = demographics_totals['female'] + demographics_totals['male']
    total_dual = demographics_totals['dual_eligible'] + demographics_totals['non_dual']

    patient_demographics = {
        'age_distribution': {
            'under_65': demographics_totals['age_under_65'],
            'age_65_74': demographics_totals['age_65_74'],
            'age_75_84': demographics_totals['age_75_84'],
            'age_85_plus': demographics_totals['age_85_plus'],
            'under_65_pct': (demographics_totals['age_under_65'] / total_age * 100) if total_age > 0 else 0,
            'age_65_74_pct': (demographics_totals['age_65_74'] / total_age * 100) if total_age > 0 else 0,
            'age_75_84_pct': (demographics_totals['age_75_84'] / total_age * 100) if total_age > 0 else 0,
            'age_85_plus_pct': (demographics_totals['age_85_plus'] / total_age * 100) if total_age > 0 else 0,
            'total': total_age,
        },
        'gender_distribution': {
            'female': demographics_totals['female'],
            'male': demographics_totals['male'],
            'female_pct': (demographics_totals['female'] / total_gender * 100) if total_gender > 0 else 0,
            'male_pct': (demographics_totals['male'] / total_gender * 100) if total_gender > 0 else 0,
            'total': total_gender,
        },
        'coverage_status': {
            'dual_eligible': demographics_totals['dual_eligible'],
            'non_dual': demographics_totals['non_dual'],
            'dual_eligible_pct': (demographics_totals['dual_eligible'] / total_dual * 100) if total_dual > 0 else 0,
            'low_income_subsidy': demographics_totals['low_income_subsidy'],
            'low_income_subsidy_pct': (demographics_totals['low_income_subsidy'] / total_dual * 100) if total_dual > 0 else 0,
            'total': total_dual,
        },
        'has_data': total_age > 0 or total_gender > 0,
    }

    # Print demographics summary if available
    if patient_demographics['has_data']:
        print(f"\n  Patient Demographics:")
        if total_gender > 0:
            print(f"    Gender: {patient_demographics['gender_distribution']['female_pct']:.1f}% Female, {patient_demographics['gender_distribution']['male_pct']:.1f}% Male")
        if total_age > 0:
            print(f"    Age: {patient_demographics['age_distribution']['age_65_74_pct']:.1f}% are 65-74, {patient_demographics['age_distribution']['age_75_84_pct']:.1f}% are 75-84")
        if total_dual > 0:
            print(f"    Dual-Eligible (Medicare+Medicaid): {patient_demographics['coverage_status']['dual_eligible_pct']:.1f}%")
    else:
        # Demographics not available in current API response
        print(f"\n  Patient Demographics: Not available (API limitation)")

    # Calculate prescriber concentration metrics (Phase 2 improvement)
    prescriber_concentration = {
        'top_prescribers': [],
        'top_10_concentration': 0,
        'top_20_concentration': 0,
        'hhi': 0,  # Herfindahl-Hirschman Index
        'has_data': False,
    }

    if all_prescriber_records and total_medicare_claims > 0:
        # Sort by claims descending
        sorted_prescribers = sorted(all_prescriber_records, key=lambda x: x['claims'], reverse=True)

        # Top 20 prescribers (anonymized - just specialty and state)
        for i, p in enumerate(sorted_prescribers[:20], 1):
            pct = (p['claims'] / total_medicare_claims * 100) if total_medicare_claims > 0 else 0
            prescriber_concentration['top_prescribers'].append({
                'rank': i,
                'specialty': p['specialty'],
                'state': p['state'],
                'claims': p['claims'],
                'beneficiaries': p['beneficiaries'],
                'pct_of_total': pct,
            })

        # Top 10 prescribers concentration (CR10)
        top_10_claims = sum(p['claims'] for p in sorted_prescribers[:10])
        cr10 = (top_10_claims / total_medicare_claims * 100) if total_medicare_claims > 0 else 0
        prescriber_concentration['top_10_concentration'] = cr10
        prescriber_concentration['cr10'] = cr10  # Alias for template clarity

        # CR10 interpretation - based on testing across drug types:
        # <5%: Highly distributed (generics like metformin)
        # 5-15%: Moderately distributed (specialty drugs like Humira)
        # 15-30%: Concentrated (subspecialty like oncology)
        # >30%: Highly concentrated (ultra-specialty like Tepezza)
        if cr10 < 5:
            prescriber_concentration['cr10_interpretation'] = 'Highly distributed'
        elif cr10 < 15:
            prescriber_concentration['cr10_interpretation'] = 'Moderately distributed'
        elif cr10 < 30:
            prescriber_concentration['cr10_interpretation'] = 'Concentrated'
        else:
            prescriber_concentration['cr10_interpretation'] = 'Highly concentrated'

        # Top 20 prescribers concentration
        top_20_claims = sum(p['claims'] for p in sorted_prescribers[:20])
        prescriber_concentration['top_20_concentration'] = (top_20_claims / total_medicare_claims * 100) if total_medicare_claims > 0 else 0

        # Calculate HHI (sum of squared market shares)
        # Scale: 0-10000, where <1500 = unconcentrated, 1500-2500 = moderate, >2500 = highly concentrated
        hhi = sum((p['claims'] / total_medicare_claims * 100) ** 2 for p in sorted_prescribers)
        prescriber_concentration['hhi'] = min(hhi, 10000)  # Cap at 10000

        # HHI interpretation
        if prescriber_concentration['hhi'] < 1500:
            prescriber_concentration['hhi_interpretation'] = 'Unconcentrated (competitive)'
        elif prescriber_concentration['hhi'] < 2500:
            prescriber_concentration['hhi_interpretation'] = 'Moderately concentrated'
        else:
            prescriber_concentration['hhi_interpretation'] = 'Highly concentrated'

        prescriber_concentration['has_data'] = True
        prescriber_concentration['total_prescribers_analyzed'] = len(sorted_prescribers)

        print(f"\n  Prescriber Concentration:")
        print(f"    CR10 (Top 10): {prescriber_concentration['cr10']:.1f}% of claims ({prescriber_concentration['cr10_interpretation']})")
        print(f"    Top 20 prescribers: {prescriber_concentration['top_20_concentration']:.1f}% of claims")
        print(f"    HHI: {prescriber_concentration['hhi']:.0f} ({prescriber_concentration['hhi_interpretation']})")

    # Store prescriber results
    result['prescriber_analysis'] = {
        'by_specialty': prescriber_data[:top_specialties],
        'total_prescribers': total_prescribers,
        'avg_beneficiaries_per_prescriber': (
            total_medicare_beneficiaries / total_prescribers if total_prescribers > 0 else 0
        ),
        'concentration': prescriber_concentration,
    }

    # Store patient demographics
    result['patient_demographics'] = patient_demographics

    # =========================================================================
    # Phase 2b: Medicare Part D Spending Data (with YoY Trends)
    # =========================================================================
    spending_by_year = {}  # Year -> {spending, claims, beneficiaries, yoy_growth}
    latest_year = None

    if include_spending_trends:
        progress.start_step('spending_data', "Collecting Medicare Part D spending data...")
        print(f"\n{'─' * 60}")
        print("Collecting Medicare Part D spending data...")

        # Try brand names first, then generic - the spending API uses brand names
        spending_search_names = brand_names.copy() if brand_names else []
        if drug_name not in spending_search_names:
            spending_search_names.append(drug_name)

        for search_name in spending_search_names:
            try:
                spending_result = medicare_spending(
                    spending_drug_name=search_name,
                    spending_type="part_d",
                    size=50
                )

                # The API returns {drugs: [{brand_name, generic_name, manufacturer, spending_by_year: {year: {...}}}]}
                if spending_result and 'drugs' in spending_result:
                    drugs_list = spending_result.get('drugs', [])

                    for drug_record in drugs_list:
                        # Skip duplicate manufacturer entries (prefer "Overall")
                        manufacturer = drug_record.get('manufacturer', '')
                        if manufacturer and manufacturer != 'Overall':
                            continue

                        year_data = drug_record.get('spending_by_year', {})

                        for year_str, data in year_data.items():
                            year = int(year_str)
                            spending = float(data.get('total_spending', 0) or 0)
                            claims = int(float(data.get('total_claims', 0) or 0))
                            beneficiaries = int(float(data.get('total_beneficiaries', 0) or 0))

                            # Aggregate if multiple brand forms (Ozempic + Rybelsus)
                            if year not in spending_by_year:
                                spending_by_year[year] = {
                                    'spending': 0,
                                    'claims': 0,
                                    'beneficiaries': 0,
                                    'avg_cost_per_claim': 0,
                                    'yoy_spending_growth': None,
                                    'yoy_beneficiaries_growth': None,
                                }
                            spending_by_year[year]['spending'] += spending
                            spending_by_year[year]['claims'] += claims
                            spending_by_year[year]['beneficiaries'] += beneficiaries

                    if spending_by_year:
                        print(f"  Found spending data for '{search_name}' ({len(spending_by_year)} years)")
                        break  # Found data, stop searching

            except Exception as e:
                print(f"  Warning: Error for '{search_name}': {e}")
                continue

        # Calculate YoY growth rates
        years_sorted = sorted(spending_by_year.keys())
        for i, year in enumerate(years_sorted):
            data = spending_by_year[year]
            # Calculate avg cost per claim
            if data['claims'] > 0:
                data['avg_cost_per_claim'] = data['spending'] / data['claims']

            # Calculate YoY growth
            if i > 0:
                prev_year = years_sorted[i - 1]
                prev_data = spending_by_year[prev_year]

                if prev_data['spending'] > 0:
                    data['yoy_spending_growth'] = (
                        (data['spending'] - prev_data['spending']) / prev_data['spending'] * 100
                    )
                if prev_data['beneficiaries'] > 0:
                    data['yoy_beneficiaries_growth'] = (
                        (data['beneficiaries'] - prev_data['beneficiaries']) / prev_data['beneficiaries'] * 100
                    )

        # Use latest year for totals
        if years_sorted:
            latest_year = years_sorted[-1]
            total_medicare_spending = spending_by_year[latest_year]['spending']
            total_medicare_claims = spending_by_year[latest_year]['claims']
            total_medicare_beneficiaries = spending_by_year[latest_year]['beneficiaries']

            print(f"\n  Spending Trends (Medicare Part D):")
            for year in years_sorted:
                data = spending_by_year[year]
                yoy = f" (+{data['yoy_spending_growth']:.0f}% YoY)" if data['yoy_spending_growth'] else ""
                print(f"    {year}: {format_currency(data['spending'])} | {format_number(data['beneficiaries'])} patients{yoy}")

            # Calculate CAGR if we have multiple years
            if len(years_sorted) >= 2:
                first_year = years_sorted[0]
                last_year = years_sorted[-1]
                first_val = spending_by_year[first_year]['spending']
                last_val = spending_by_year[last_year]['spending']
                num_years = last_year - first_year
                if first_val > 0 and num_years > 0:
                    cagr = ((last_val / first_val) ** (1 / num_years) - 1) * 100
                    print(f"\n    CAGR ({first_year}-{last_year}): {cagr:.1f}%")

        progress.complete_step("Spending data complete")

    result['spending_trends']['medicare_part_d'] = {
        'total_spending': total_medicare_spending,
        'total_claims': total_medicare_claims,
        'avg_cost_per_claim': (
            total_medicare_spending / total_medicare_claims if total_medicare_claims > 0 else 0
        ),
        'total_beneficiaries': total_medicare_beneficiaries,
        'latest_year': latest_year,
        'by_year': [
            {
                'year': year,
                'spending': spending_by_year[year]['spending'],
                'claims': spending_by_year[year]['claims'],
                'beneficiaries': spending_by_year[year]['beneficiaries'],
                'avg_cost_per_claim': spending_by_year[year]['avg_cost_per_claim'],
                'yoy_spending_growth': spending_by_year[year]['yoy_spending_growth'],
                'yoy_beneficiaries_growth': spending_by_year[year]['yoy_beneficiaries_growth'],
            }
            for year in sorted(spending_by_year.keys())
        ],
    }

    # Store data year for provenance
    result['data_sources']['medicare_part_d_year'] = latest_year

    # =========================================================================
    # Phase 2c: Medicare Part B Spending Data (Physician-Administered Drugs)
    # =========================================================================
    # Part B covers drugs administered in physician offices/clinics (IV infusions)
    # This is CRITICAL for oncology drugs, biologics, and other infusion therapies
    total_part_b_spending = 0
    part_b_spending_by_year = {}
    part_b_latest_year = None

    if include_part_b_spending:
        progress.start_step('part_b_spending', "Collecting Medicare Part B spending data...")
        print(f"\n{'─' * 60}")
        print("Collecting Medicare Part B spending data (physician-administered)...")

        # Search with brand names first, then generic
        part_b_search_names = brand_names.copy() if brand_names else []
        if drug_name not in part_b_search_names:
            part_b_search_names.append(drug_name)
        if generic_name and generic_name not in [n.lower() for n in part_b_search_names]:
            part_b_search_names.append(generic_name)

        for search_name in part_b_search_names:
            try:
                part_b_result = medicare_spending(
                    spending_drug_name=search_name,
                    spending_type="part_b",  # KEY: Part B instead of Part D
                    size=50
                )

                if part_b_result and 'drugs' in part_b_result:
                    drugs_list = part_b_result.get('drugs', [])

                    for drug_record in drugs_list:
                        # Skip duplicate manufacturer entries
                        manufacturer = drug_record.get('manufacturer', '')
                        if manufacturer and manufacturer != 'Overall':
                            continue

                        year_data = drug_record.get('spending_by_year', {})

                        for year_str, data in year_data.items():
                            year = int(year_str)
                            spending = float(data.get('total_spending', 0) or 0)
                            claims = int(float(data.get('total_claims', data.get('total_services', 0)) or 0))
                            beneficiaries = int(float(data.get('total_beneficiaries', 0) or 0))

                            if year not in part_b_spending_by_year:
                                part_b_spending_by_year[year] = {
                                    'spending': 0,
                                    'claims': 0,
                                    'beneficiaries': 0,
                                    'yoy_spending_growth': None,
                                }
                            part_b_spending_by_year[year]['spending'] += spending
                            part_b_spending_by_year[year]['claims'] += claims
                            part_b_spending_by_year[year]['beneficiaries'] += beneficiaries

                    if part_b_spending_by_year:
                        print(f"  Found Part B spending data for '{search_name}' ({len(part_b_spending_by_year)} years)")
                        break

            except Exception as e:
                print(f"  Warning: Part B error for '{search_name}': {e}")
                continue

        # Calculate YoY growth for Part B
        years_sorted_b = sorted(part_b_spending_by_year.keys())
        for i, year in enumerate(years_sorted_b):
            data = part_b_spending_by_year[year]
            if i > 0:
                prev_year = years_sorted_b[i - 1]
                prev_data = part_b_spending_by_year[prev_year]
                if prev_data['spending'] > 0:
                    data['yoy_spending_growth'] = (
                        (data['spending'] - prev_data['spending']) / prev_data['spending'] * 100
                    )

        if years_sorted_b:
            part_b_latest_year = years_sorted_b[-1]
            total_part_b_spending = part_b_spending_by_year[part_b_latest_year]['spending']

            print(f"\n  Spending Trends (Medicare Part B - Physician-Administered):")
            for year in years_sorted_b:
                data = part_b_spending_by_year[year]
                yoy = f" (+{data['yoy_spending_growth']:.0f}% YoY)" if data['yoy_spending_growth'] else ""
                print(f"    {year}: {format_currency(data['spending'])}{yoy}")

            # Add warning if Part B is significantly larger than Part D
            if total_part_b_spending > 0 and total_medicare_spending > 0:
                ratio = total_part_b_spending / total_medicare_spending
                if ratio > 2:
                    caveat = (
                        f"⚠️ Medicare Part B spending ({format_currency(total_part_b_spending)}) is "
                        f"{ratio:.1f}x larger than Part D ({format_currency(total_medicare_spending)}). "
                        "This drug is primarily physician-administered."
                    )
                    result['data_caveats'].append(caveat)
                    print(f"\n  {caveat}")
        else:
            print("  No Part B spending data found (drug may be primarily retail/Part D)")

        progress.complete_step("Part B spending complete")

    result['spending_trends']['medicare_part_b'] = {
        'total_spending': total_part_b_spending,
        'latest_year': part_b_latest_year,
        'by_year': [
            {
                'year': year,
                'spending': part_b_spending_by_year[year]['spending'],
                'claims': part_b_spending_by_year[year]['claims'],
                'beneficiaries': part_b_spending_by_year[year]['beneficiaries'],
                'yoy_spending_growth': part_b_spending_by_year[year]['yoy_spending_growth'],
            }
            for year in sorted(part_b_spending_by_year.keys())
        ],
    }

    # Store data year for provenance
    result['data_sources']['medicare_part_b_year'] = part_b_latest_year

    # =========================================================================
    # Phase 3: Geographic Breakdown (from prescriber data already collected)
    # =========================================================================
    geographic_data = []
    state_aggregates = defaultdict(lambda: {
        'total_spending': 0,
        'total_claims': 0,
    })

    if include_geographic_breakdown:
        print(f"\n{'─' * 60}")
        print("Analyzing geographic distribution...")

        # First, try to extract state data from the prescriber records we already have
        # Re-process prescriber data for geographic breakdown
        try:
            prescriber_result = medicare_prescribers(
                drug_name=drug_name,
                size=2000  # Get more records for better geographic coverage
            )

            records = []
            if prescriber_result:
                if 'prescribers' in prescriber_result:
                    records = prescriber_result.get('prescribers', [])
                elif 'data' in prescriber_result:
                    records = prescriber_result.get('data', [])

            # Aggregate by state
            for record in records:
                state = record.get('state', '')
                if not state or len(state) != 2:
                    continue

                claims_val = record.get('total_claims', record.get('tot_clms', 0))
                claims = int(float(claims_val)) if claims_val else 0

                cost_val = record.get('total_drug_cost', record.get('tot_drug_cst', 0))
                drug_cost = float(cost_val) if cost_val else 0

                state_aggregates[state]['total_claims'] += claims
                state_aggregates[state]['total_spending'] += drug_cost

        except Exception as e:
            print(f"  Warning: Error in geographic analysis: {e}")

        # Calculate totals and percentages
        total_state_spending = sum(s['total_spending'] for s in state_aggregates.values())

        # Fetch state populations from DataCommons API for per-capita normalization
        state_populations = {}
        population_data_available = False

        # FIPS to state abbreviation mapping
        fips_to_state = {
            "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA",
            "08": "CO", "09": "CT", "10": "DE", "11": "DC", "12": "FL",
            "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN",
            "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME",
            "24": "MD", "25": "MA", "26": "MI", "27": "MN", "28": "MS",
            "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
            "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND",
            "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
            "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT",
            "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI",
            "56": "WY"
        }

        if datacommons_observations:
            try:
                # Get US state populations using DataCommons API
                pop_result = datacommons_observations(
                    variable_dcid="Count_Person",
                    place_dcid="country/USA",
                    child_place_type="State",
                    date="latest"
                )

                # Parse response: {place_observations: [{place: {dcid, name}, time_series: [[date, value], ...]}]}
                if pop_result and 'place_observations' in pop_result:
                    for obs in pop_result.get('place_observations', []):
                        place_info = obs.get('place', {})
                        place_dcid = place_info.get('dcid', '')
                        time_series = obs.get('time_series', [])

                        # Get most recent value from time_series
                        if time_series and place_dcid.startswith('geoId/'):
                            fips = place_dcid.replace('geoId/', '')
                            state_abbr = fips_to_state.get(fips)
                            # time_series is list of [date, value] pairs
                            latest_value = time_series[0][1] if time_series else 0
                            if state_abbr and latest_value:
                                state_populations[state_abbr] = int(latest_value)

                if state_populations:
                    population_data_available = True
                    print(f"\n  Retrieved population data for {len(state_populations)} states from DataCommons")

            except Exception as e:
                print(f"\n  Warning: Could not fetch population data from DataCommons: {e}")

        # Fallback message if no population data
        if not population_data_available:
            print(f"\n  Note: Population data unavailable, per-capita calculation will use spending ratios")

        # Calculate national totals for per-capita
        total_national_population = sum(state_populations.values()) if state_populations else 0
        national_spending_per_capita = (
            total_state_spending / total_national_population if total_national_population > 0 else 0
        )

        for state, data in state_aggregates.items():
            pct = (data['total_spending'] / total_state_spending * 100) if total_state_spending > 0 else 0

            # NEW: Proper population-based per-capita calculation
            state_pop = state_populations.get(state, 0)
            if state_pop > 0 and national_spending_per_capita > 0:
                state_spending_per_capita = data['total_spending'] / state_pop
                per_capita_index = state_spending_per_capita / national_spending_per_capita
            else:
                # Fallback to old method if population unavailable
                avg_spending = total_state_spending / len(state_aggregates) if state_aggregates else 0
                per_capita_index = data['total_spending'] / avg_spending if avg_spending > 0 else 1.0

            geographic_data.append({
                'state': state,
                'state_name': get_state_name(state),
                'total_spending': data['total_spending'],
                'total_claims': data['total_claims'],
                'pct_of_total': pct,
                'per_capita_index': per_capita_index,
                'population': state_pop,  # NEW: Include population for transparency
                'spending_per_capita': data['total_spending'] / state_pop if state_pop > 0 else None,
            })

        # Add caveat about per-capita calculation method
        if not population_data_available:
            caveat = (
                "⚠️ Per-capita index calculated using simple state average (not population-adjusted). "
                "Large states may appear disproportionately high."
            )
            result['data_caveats'].append(caveat)
            print(f"\n  {caveat}")

        # Sort by spending descending
        geographic_data.sort(key=lambda x: x['total_spending'], reverse=True)

        if geographic_data:
            print(f"\n  Top States by Spending:")
            for item in geographic_data[:5]:
                print(f"    {item['state']}: {format_currency(item['total_spending'])} ({item['pct_of_total']:.1f}%)")
        else:
            print("  No geographic data available")

    result['geographic_analysis'] = {
        'by_state': geographic_data[:top_states],
    }

    # =========================================================================
    # Phase 3b: Medicaid Utilization
    # =========================================================================
    medicaid_data = []
    total_medicaid_spending = 0
    total_medicaid_prescriptions = 0

    if include_medicaid:
        progress.start_step('medicaid_utilization', "Collecting Medicaid utilization data...")
        print(f"\n{'─' * 60}")
        print("Collecting Medicaid utilization data...")

        # Build search names: use UPPERCASE brand names for best results
        # The Medicaid drug utilization API works best with brand names
        medicaid_search_names = []
        for brand in brand_names:
            medicaid_search_names.append(brand.upper())
        # Also try the original name in uppercase
        if drug_name.upper() not in medicaid_search_names:
            medicaid_search_names.append(drug_name.upper())

        state_aggregates_medicaid = defaultdict(lambda: {
            'total_spending': 0,
            'total_prescriptions': 0,
        })

        for i, search_name in enumerate(medicaid_search_names):
            try:
                # Note: State filter now works with the fixed DKAN API
                util_result = medicaid_info(method='get_drug_utilization', 
                    drug_name=search_name,
                    limit=5000  # Get all records (most drugs have <2000 records)
                )

                if util_result and 'data' in util_result:
                    records = util_result.get('data', [])
                    if records:
                        print(f"  Found {len(records)} Medicaid records for '{search_name}'")

                    for record in records:
                        state = record.get('state', '')
                        if not state:
                            continue

                        spending = float(record.get('total_amount_reimbursed', record.get('medicaid_amount_reimbursed', 0)) or 0)
                        prescriptions = int(record.get('number_of_prescriptions', 0) or 0)

                        state_aggregates_medicaid[state]['total_spending'] += spending
                        state_aggregates_medicaid[state]['total_prescriptions'] += prescriptions

                progress.update_step_progress((i + 1) / len(medicaid_search_names))

            except Exception as e:
                print(f"    Warning: Error for '{search_name}' Medicaid: {e}")
                continue

        # Convert aggregates to list
        for state, data in state_aggregates_medicaid.items():
            if data['total_spending'] > 0 or data['total_prescriptions'] > 0:
                medicaid_data.append({
                    'state': state,
                    'state_name': get_state_name(state),
                    'total_spending': data['total_spending'],
                    'total_prescriptions': data['total_prescriptions'],
                })
                total_medicaid_spending += data['total_spending']
                total_medicaid_prescriptions += data['total_prescriptions']

        # Sort by spending descending
        medicaid_data.sort(key=lambda x: x['total_spending'], reverse=True)

        if medicaid_data:
            print(f"\n  Medicaid Utilization ({len(medicaid_data)} states):")
            for item in medicaid_data[:3]:
                print(f"    {item['state']}: {format_currency(item['total_spending'])} ({format_number(item['total_prescriptions'])} Rx)")
        else:
            print("  No Medicaid utilization data found (API limitation)")

        print(f"\n  Total Medicaid Spending: {format_currency(total_medicaid_spending)}")

        progress.complete_step("Medicaid data complete")

    result['medicaid_utilization'] = {
        'total_spending': total_medicaid_spending,
        'total_prescriptions': total_medicaid_prescriptions,
        'by_state': medicaid_data,
    }

    result['spending_trends']['medicaid'] = {
        'total_spending': total_medicaid_spending,
        'total_prescriptions': total_medicaid_prescriptions,
        'by_state': medicaid_data,
    }

    # =========================================================================
    # Phase 3c: NADAC Pricing
    # =========================================================================
    nadac_data = []

    if include_nadac_pricing:
        progress.start_step('nadac_pricing', "Collecting NADAC pricing data...")
        print(f"\n{'─' * 60}")
        print("Collecting NADAC pricing data...")

        # Search with multiple names: original, generic, and brand names
        search_names = [drug_name]
        if generic_name and generic_name != drug_name.lower():
            search_names.append(generic_name)
        for brand in brand_names:
            if brand.lower() not in [n.lower() for n in search_names]:
                search_names.append(brand)

        seen_ndcs = set()

        for search_name in search_names:
            try:
                nadac_result = medicaid_info(method='get_nadac_pricing', 
                    drug_name=search_name,
                    limit=20
                )

                if nadac_result and 'data' in nadac_result:
                    records = nadac_result.get('data', [])
                    if records:
                        print(f"  Found {len(records)} NADAC records for '{search_name}'")

                    for record in records:
                        ndc = record.get('ndc', '')
                        # Skip duplicates
                        if ndc in seen_ndcs:
                            continue
                        seen_ndcs.add(ndc)

                        nadac_data.append({
                            'ndc': ndc,
                            'description': record.get('description', record.get('ndc_description', search_name)),
                            'nadac_per_unit': float(record.get('nadac_per_unit', 0) or 0),
                            'pricing_unit': record.get('pricing_unit', 'EA'),
                            'effective_date': record.get('effective_date', '')[:10] if record.get('effective_date') else '',
                        })

            except Exception as e:
                print(f"    Warning: Error for '{search_name}': {e}")
                continue

        # Sort by price descending (often shows different formulations)
        nadac_data.sort(key=lambda x: x['nadac_per_unit'], reverse=True)

        if nadac_data:
            print(f"\n  NADAC Pricing ({len(nadac_data)} formulations):")
            for item in nadac_data[:3]:
                print(f"    {item['description'][:40]}: ${item['nadac_per_unit']:.2f}/{item['pricing_unit']}")
        else:
            print("  No NADAC pricing data found")

        progress.complete_step("NADAC pricing complete")

    result['nadac_pricing'] = {
        'drug_name': drug_name,
        'formulations': nadac_data,
    }

    # =========================================================================
    # Phase 3d: ASP Pricing (Medicare Part B Reimbursement)
    # =========================================================================
    asp_data = []

    if include_asp_pricing:
        progress.start_step('asp_pricing', "Collecting ASP pricing data...")
        print(f"\n{'─' * 60}")
        print("Collecting ASP pricing data (Medicare Part B)...")

        # First, search for HCPCS J-codes for this drug
        try:
            # Search for injectable drug codes using drug name
            search_names = [drug_name]
            if generic_name and generic_name != drug_name.lower():
                search_names.append(generic_name)
            for brand in brand_names:
                if brand.lower() not in [n.lower() for n in search_names]:
                    search_names.append(brand)

            hcpcs_codes = []
            seen_codes = set()

            for search_name in search_names:
                try:
                    hcpcs_result = nlm_search_codes(method='search_codes', 
                        terms=search_name,
                        maxList=20,
                        extraFields="short_desc,long_desc"
                    )

                    if hcpcs_result and 'results' in hcpcs_result:
                        for item in hcpcs_result.get('results', []):
                            code = item.get('code', '')
                            # J-codes are injectable drugs
                            if code and code.startswith('J') and code not in seen_codes:
                                seen_codes.add(code)
                                hcpcs_codes.append({
                                    'code': code,
                                    'description': item.get('display', item.get('short_desc', '')),
                                })

                except Exception as e:
                    print(f"    Warning: HCPCS search error for '{search_name}': {e}")
                    continue

            if hcpcs_codes:
                print(f"  Found {len(hcpcs_codes)} HCPCS J-codes")

                # Now get ASP pricing for each J-code
                for hcpcs in hcpcs_codes:
                    try:
                        asp_result = medicare_asp_pricing(hcpcs_code_asp=hcpcs['code'])

                        if asp_result and 'data' in asp_result:
                            data = asp_result.get('data', {})
                            if data:
                                asp_data.append({
                                    'hcpcs_code': hcpcs['code'],
                                    'description': hcpcs['description'],
                                    'asp_price': data.get('asp_price', data.get('payment_limit', 0)),
                                    'payment_limit': data.get('payment_limit', 0),
                                    'dosage_descriptor': data.get('dosage_descriptor', ''),
                                    'effective_date': data.get('effective_date', data.get('quarter', '')),
                                })

                    except Exception as e:
                        print(f"    Warning: ASP lookup error for {hcpcs['code']}: {e}")
                        continue

                if asp_data:
                    print(f"\n  ASP Pricing ({len(asp_data)} codes):")
                    for item in asp_data[:3]:
                        price = item.get('asp_price') or item.get('payment_limit', 0)
                        print(f"    {item['hcpcs_code']}: ${price:.2f} - {item['description'][:40]}")
            else:
                print("  No HCPCS J-codes found for this drug")

        except Exception as e:
            print(f"  Warning: Error collecting ASP pricing: {e}")
            import traceback
            traceback.print_exc()

    result['asp_pricing'] = {
        'drug_name': drug_name,
        'hcpcs_codes': asp_data,
    }

    # =========================================================================
    # Phase 3e: Drug Interactions (DrugBank)
    # =========================================================================
    interactions_data = []
    food_interactions = []
    drugbank_id = None

    if include_drug_interactions:
        progress.start_step('drug_interactions', "Collecting drug interaction data...")
        print(f"\n{'─' * 60}")
        print("Collecting drug interaction data (DrugBank)...")

        try:
            # First find the DrugBank ID for this drug
            db_search = drugbank_search_func(method='search_by_name', query=drug_name, limit=5)

            # Search returns 'results' not 'data'
            if db_search and 'results' in db_search:
                results = db_search.get('results', [])
                if results:
                    # Find best match
                    for drug in results:
                        name = drug.get('name', '').lower()
                        if name == drug_name.lower() or name == generic_name.lower():
                            drugbank_id = drug.get('drugbank_id')
                            break

                    # If no exact match, use first result
                    if not drugbank_id and results:
                        drugbank_id = results[0].get('drugbank_id')

            if drugbank_id:
                print(f"  Found DrugBank ID: {drugbank_id}")

                # Get full drug details (includes interactions in the response)
                details_result = drugbank_search_func(method='get_drug_details', drugbank_id=drugbank_id)

                if details_result and 'drug' in details_result:
                    drug_data = details_result.get('drug', {})

                    # Extract drug-drug interactions
                    all_interactions = drug_data.get('drug_interactions', [])
                    total_interaction_count = len(all_interactions)

                    # Infer severity from description text (DrugBank free data doesn't include severity)
                    def infer_severity(desc: str) -> str:
                        desc_lower = desc.lower()
                        # Major severity indicators
                        if any(kw in desc_lower for kw in [
                            'fatal', 'death', 'life-threatening', 'serious', 'severe',
                            'contraindicated', 'avoid', 'do not', 'dangerous',
                            'cardiotoxic', 'arrhythm', 'qt prolong', 'torsade',
                            'serotonin syndrome', 'neuroleptic malignant'
                        ]):
                            return 'major'
                        # Minor severity indicators
                        if any(kw in desc_lower for kw in [
                            'may decrease', 'slightly', 'minor', 'minimal',
                            'unlikely', 'theoretical'
                        ]):
                            return 'minor'
                        # Default to moderate
                        return 'moderate'

                    # Store all interactions with inferred severity
                    for interaction in all_interactions:
                        db_ids = interaction.get('drugbank_id', [])
                        desc = interaction.get('description', '')
                        interactions_data.append({
                            'drug': interaction.get('name', 'Unknown'),
                            'drugbank_id': db_ids[0] if db_ids else '',
                            'description': desc[:200],
                            'severity': infer_severity(desc),
                        })

                    # Sort by severity (major first, then moderate, then minor), then alphabetically
                    severity_order = {'major': 0, 'moderate': 1, 'minor': 2}
                    interactions_data.sort(key=lambda x: (severity_order.get(x['severity'], 1), x['drug']))

                    # Extract food interactions
                    food_interactions = drug_data.get('food_interactions', [])

                    print(f"  Found {total_interaction_count} drug interactions")
                    print(f"  Found {len(food_interactions)} food interactions")

                    # Count by severity
                    severity_counts = {}
                    for item in interactions_data:
                        sev = item['severity']
                        severity_counts[sev] = severity_counts.get(sev, 0) + 1
                    if severity_counts:
                        print(f"  Severity breakdown: {severity_counts}")

                    if interactions_data:
                        print(f"\n  Top Drug Interactions:")
                        for item in interactions_data[:3]:
                            print(f"    - [{item['severity']}] {item['drug']}: {item['description'][:50]}...")
            else:
                print("  Drug not found in DrugBank")

        except Exception as e:
            print(f"  Warning: Error collecting interactions: {e}")
            import traceback
            traceback.print_exc()

    result['drug_interactions'] = {
        'drug_name': drug_name,
        'drugbank_id': drugbank_id,
        'total_count': len(interactions_data),
        'interactions': interactions_data,
        'food_interactions': food_interactions,
        'food_interactions_count': len(food_interactions),
    }

    # =========================================================================
    # Phase 3f: FDA Safety Context (Recalls, Shortages)
    # =========================================================================
    fda_recalls = []
    fda_shortages = []

    if include_fda_safety:
        progress.start_step('fda_safety', "Collecting FDA safety data...")
        print(f"\n{'─' * 60}")
        print("Collecting FDA safety data...")

        # Check for recalls (get all - typically small dataset for specific drugs)
        try:
            recalls_result = fda_lookup_func(
                search_term=drug_name,
                search_type="recalls",
                limit=100
            )

            if recalls_result and 'data' in recalls_result:
                data = recalls_result.get('data', {})
                recalls_list = data.get('results', [])

                for recall in recalls_list:
                    fda_recalls.append({
                        'recall_number': recall.get('recall_number', ''),
                        'product_description': recall.get('product_description', '')[:100],
                        'reason_for_recall': recall.get('reason_for_recall', '')[:150],
                        'classification': recall.get('classification', ''),
                        'status': recall.get('status', ''),
                        'recall_initiation_date': recall.get('recall_initiation_date', ''),
                    })

                # Sort by date (most recent first), then by classification severity
                classification_order = {'Class I': 0, 'Class II': 1, 'Class III': 2}
                fda_recalls.sort(
                    key=lambda x: (
                        -int(x.get('recall_initiation_date', '0') or '0'),  # Most recent first
                        classification_order.get(x.get('classification', ''), 3)  # Most severe first
                    )
                )

            if fda_recalls:
                print(f"  Found {len(fda_recalls)} recalls")
            else:
                print("  No recalls found")

        except Exception as e:
            print(f"  Warning: Error checking recalls: {e}")

        # Check for shortages (get all - typically small dataset for specific drugs)
        try:
            shortages_result = fda_lookup_func(
                search_term=drug_name,
                search_type="shortages",
                limit=100
            )

            if shortages_result and 'data' in shortages_result:
                data = shortages_result.get('data', {})
                shortages_list = data.get('results', [])

                for shortage in shortages_list:
                    fda_shortages.append({
                        'generic_name': shortage.get('generic_name', ''),
                        'proprietary_name': shortage.get('proprietary_name', ''),
                        'status': shortage.get('status', ''),
                        'reason': shortage.get('reason', '')[:150] if shortage.get('reason') else '',
                        'company_name': shortage.get('company_name', ''),
                        'updated_date': shortage.get('updated_date', ''),
                    })

            if fda_shortages:
                print(f"  Found {len(fda_shortages)} shortage records")
            else:
                print("  No shortages found")

        except Exception as e:
            print(f"  Warning: Error checking shortages: {e}")

        # Check adverse events (FAERS data) - use count aggregation
        fda_adverse_events = []
        try:
            ae_result = fda_lookup_func(
                search_term=drug_name,
                search_type="adverse_events",
                count="patient.reaction.reactionmeddrapt.exact",
                limit=15
            )

            if ae_result and 'data' in ae_result:
                data = ae_result.get('data', {})
                ae_list = data.get('results', [])

                for ae in ae_list[:15]:
                    fda_adverse_events.append({
                        'reaction': ae.get('term', ''),
                        'count': ae.get('count', 0),
                    })

            if fda_adverse_events:
                print(f"  Found {len(fda_adverse_events)} adverse event types (FAERS)")
                total_ae = sum(ae.get('count', 0) for ae in fda_adverse_events)
                print(f"    Top: {fda_adverse_events[0]['reaction']} ({fda_adverse_events[0]['count']:,} reports)")
            else:
                print("  No adverse events found")

        except Exception as e:
            print(f"  Warning: Error checking adverse events: {e}")

    result['fda_safety'] = {
        'drug_name': drug_name,
        'recalls': fda_recalls,
        'recalls_count': len(fda_recalls),
        'shortages': fda_shortages,
        'shortages_count': len(fda_shortages),
        'adverse_events': fda_adverse_events,
        'adverse_events_count': len(fda_adverse_events),
        'has_safety_concerns': len(fda_recalls) > 0 or len(fda_shortages) > 0,
    }

    # =========================================================================
    # Phase 3g: Competitive Switching Analysis
    # =========================================================================
    switching_data = {
        'has_data': False,
        'competitive_set': None,
        'market_share': {},
        'switching_estimates': {},
        'summary': {},
    }

    if include_switching_analysis:
        progress.start_step('switching_analysis', "Analyzing competitive switching patterns...")
        print(f"\n{'─' * 60}")
        print("Analyzing competitive switching patterns...")

        try:
            # Import the switching analysis module
            from switching_analysis import get_full_switching_analysis

            switching_result = get_full_switching_analysis(drug_name, verbose=True, mcp_funcs=mcp_funcs)

            if switching_result.get('has_data'):
                switching_data = {
                    'has_data': True,
                    'competitive_set': switching_result.get('market_share', {}).get('competitive_set'),
                    'market_share': switching_result.get('market_share', {}),
                    'switching_estimates': switching_result.get('switching_estimates', {}),
                    'geographic_analysis': switching_result.get('geographic_analysis', {}),
                    'published_studies': switching_result.get('published_studies', {}),
                    'summary': switching_result.get('summary', {}),
                }

                # Print summary
                summary = switching_data['summary']
                print(f"\n  Competitive Position: {summary.get('competitive_position', 'Unknown')}")
                print(f"  Market Share Trend: {summary.get('market_share_trend', 'Unknown')}")

                net_switch = summary.get('estimated_net_switch', 0)
                if net_switch != 0:
                    direction = "gained" if net_switch > 0 else "lost"
                    print(f"  Estimated Net Switch: {format_number(abs(net_switch))} patients {direction}")

                for insight in summary.get('key_insights', [])[:3]:
                    print(f"    • {insight}")

        except Exception as e:
            print(f"  Warning: Error in switching analysis: {e}")
            import traceback
            traceback.print_exc()

        progress.complete_step("Switching analysis complete")

    result['switching_analysis'] = switching_data

    # =========================================================================
    # Phase 4: Build Summary and Visualization
    # =========================================================================
    progress.start_step('visualization', "Building summary and visualization...")

    # Build summary
    top_specialty = prescriber_data[0]['specialty'] if prescriber_data else "N/A"
    top_specialty_pct = prescriber_data[0]['pct_of_claims'] if prescriber_data else 0
    top_state = geographic_data[0]['state'] if geographic_data else "N/A"

    # Calculate combined Medicare spending (Part D + Part B)
    combined_medicare_spending = total_medicare_spending + total_part_b_spending

    # Add standard data caveats
    standard_caveats = [
        "💰 Spending figures are GROSS (pre-rebate). Actual government cost is 20-40% lower after manufacturer rebates.",
        f"📅 Medicare Part D data year: {latest_year or 'Unknown'}. Medicare Part B data year: {part_b_latest_year or 'Unknown'}.",
        "⏰ Medicare data typically lags 18-24 months behind current date.",
        "🏥 340B hospitals receive significant discounts not reflected in these figures.",
    ]
    for caveat in standard_caveats:
        if caveat not in result['data_caveats']:
            result['data_caveats'].append(caveat)

    # =========================================================================
    # Post-hoc IV Drug Detection via Part B/D Ratio
    # =========================================================================
    # If DrugBank didn't provide route info, use Part B >> Part D as heuristic
    # Drugs where Part B is >5x Part D are almost certainly IV/infusion
    if total_part_b_spending > 0 and total_medicare_spending > 0:
        part_b_to_d_ratio = total_part_b_spending / total_medicare_spending
        if part_b_to_d_ratio >= 5 and not result['drug_characteristics']['is_iv_infusion']:
            # Update drug characteristics
            result['drug_characteristics']['is_iv_infusion'] = True
            result['drug_characteristics']['part_b_relevant'] = True
            result['drug_characteristics']['detection_method'] = 'spending_ratio'

            # Add caveat about this
            ratio_msg = (
                f"⚠️ Medicare Part B spending (${total_part_b_spending/1e9:.1f}B) is "
                f"{part_b_to_d_ratio:.1f}x larger than Part D (${total_medicare_spending/1e6:.1f}M). "
                "This drug is primarily physician-administered (IV/infusion)."
            )
            # Insert at beginning of caveats for visibility
            result['data_caveats'].insert(0, ratio_msg)
            print(f"\n  {ratio_msg}")

    result['summary'] = {
        # Part D (retail pharmacy)
        'total_medicare_part_d_spending': format_currency(total_medicare_spending),
        'total_medicare_part_d_spending_raw': total_medicare_spending,
        'medicare_part_d_year': latest_year,
        # Part B (physician-administered)
        'total_medicare_part_b_spending': format_currency(total_part_b_spending),
        'total_medicare_part_b_spending_raw': total_part_b_spending,
        'medicare_part_b_year': part_b_latest_year,
        # Combined Medicare
        'total_medicare_spending': format_currency(combined_medicare_spending),
        'total_medicare_spending_raw': combined_medicare_spending,
        # Legacy fields for backward compatibility
        'total_medicaid_spending': format_currency(total_medicaid_spending),
        'total_medicaid_spending_raw': total_medicaid_spending,
        'combined_spending': format_currency(combined_medicare_spending + total_medicaid_spending),
        'combined_spending_raw': combined_medicare_spending + total_medicaid_spending,
        'medicare_beneficiaries': total_medicare_beneficiaries,
        'medicare_claims': total_medicare_claims,
        'top_prescribing_specialty': f"{top_specialty} ({top_specialty_pct:.1f}%)",
        'top_state': top_state,
        # NEW: Spending breakdown clarity
        'spending_note': (
            f"Medicare Part D (retail): {format_currency(total_medicare_spending)} | "
            f"Medicare Part B (physician-admin): {format_currency(total_part_b_spending)} | "
            f"Medicaid: {format_currency(total_medicaid_spending)}"
        ),
        'is_gross_spending': True,
        'rebate_caveat': "Figures are gross spending before manufacturer rebates (actual cost is 20-40% lower)",
    }

    # Build visualization
    result['visualization'] = build_full_visualization(
        drug_name=drug_name,
        analysis_date=result['analysis_date'],
        summary=result['summary'],
        prescriber_data=prescriber_data,
        geographic_data=geographic_data,
        nadac_data=nadac_data,
        medicaid_data=medicaid_data,
        total_prescribers=total_prescribers,
        avg_beneficiaries_per_prescriber=result['prescriber_analysis'].get('avg_beneficiaries_per_prescriber', 0),
        data_caveats=result['data_caveats'],
    )

    progress.complete_step("Analysis complete")

    print(f"\n{'=' * 60}")
    print("✅ ANALYSIS COMPLETE")
    print(f"{'=' * 60}")
    print(f"Medicare Part D (retail pharmacy): {format_currency(total_medicare_spending)} ({latest_year or 'N/A'})")
    print(f"Medicare Part B (physician-admin): {format_currency(total_part_b_spending)} ({part_b_latest_year or 'N/A'})")
    print(f"Combined Medicare Spending: {format_currency(combined_medicare_spending)}")
    print(f"Medicaid Spending: {format_currency(total_medicaid_spending)}")
    print(f"Total Government Spending: {format_currency(combined_medicare_spending + total_medicaid_spending)}")
    print(f"Total Prescribers: {format_number(total_prescribers)}")

    # Print data caveats
    if result['data_caveats']:
        print(f"\n{'─' * 60}")
        print("DATA CAVEATS:")
        for caveat in result['data_caveats'][:5]:  # Show first 5 caveats
            print(f"  {caveat}")

    return result


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 get_real_world_utilization_analysis.py <DRUG_NAME> [OPTIONS]")
        print("\nExamples:")
        print("  python3 get_real_world_utilization_analysis.py semaglutide")
        print("  python3 get_real_world_utilization_analysis.py tirzepatide --top-states=15")
        print("  python3 get_real_world_utilization_analysis.py metformin --skip-medicaid")
        print("\nOptions:")
        print("  --top-states=N     Number of top states to show (default: 10)")
        print("  --top-specialties=N  Number of top specialties (default: 10)")
        print("  --skip-medicaid    Skip Medicaid data collection (faster)")
        print("  --skip-nadac       Skip NADAC pricing data")
        sys.exit(1)

    drug_name = sys.argv[1]

    # Parse optional arguments
    top_states = 10
    top_specialties = 10
    include_medicaid = True
    include_nadac = True

    for arg in sys.argv[2:]:
        if arg.startswith('--top-states='):
            top_states = int(arg.split('=')[1])
        elif arg.startswith('--top-specialties='):
            top_specialties = int(arg.split('=')[1])
        elif arg == '--skip-medicaid':
            include_medicaid = False
        elif arg == '--skip-nadac':
            include_nadac = False

    # Run analysis
    result = get_real_world_utilization_analysis(
        drug_name=drug_name,
        top_states=top_states,
        top_specialties=top_specialties,
        include_medicaid=include_medicaid,
        include_nadac_pricing=include_nadac,
    )

    # Print full visualization
    print("\n")
    print(result['visualization'])
