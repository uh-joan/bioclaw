"""Drug Sales & Patent Cliff Forecasting - Main Entry Point

A sophisticated analytical skill that predicts drug sales trajectories using:
1. Phase 1: Market Sizing - Estimate potential sales without historical data
2. Phase 2: Time-Series Forecasting - Project sales with patent cliff modeling

Usage:
    python forecast_drug_sales.py "Ozempic" --indication "type 2 diabetes" --years 5
"""

import sys
import os

# Add script directory to path for local imports
_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _script_dir)

from mcp_client import McpClient
from progress_tracker import create_progress_tracker
from patent_analysis import get_patent_exclusivity, get_patent_cliff_risk, is_biologic
from market_sizing import estimate_market_size, get_drug_spending_data
from comparable_drugs import find_comparable_drugs, get_drug_details, get_brand_name, get_generic_name
from time_series_forecast import forecast_drug_sales as run_forecast, generate_all_scenarios

from typing import Dict, Any, Optional


def drug_sales_forecasting(
    drug_name: str,
    indication: str,
    forecast_years: int = 5,
    include_comparables: bool = True,
    scenario: str = "base",
    progress_callback=None,
    mcp_funcs: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Comprehensive drug sales forecasting with patent cliff modeling.

    This skill performs two-phase analysis:
    1. Market Sizing: Estimate market potential using prevalence, spending, and pricing data
    2. Time-Series Forecasting: Project sales with patent expiry impact modeling

    Args:
        drug_name (str): Drug name - brand (e.g., "Ozempic") or generic (e.g., "semaglutide")
        indication (str): Primary indication for market sizing (e.g., "type 2 diabetes", "obesity").
            REQUIRED because many drugs have multiple approved indications with vastly different
            market sizes (e.g., semaglutide treats both diabetes ~29M patients and obesity ~110M patients).
        forecast_years (int, optional): Number of years to forecast (default: 5)
        include_comparables (bool, optional): Whether to analyze comparable drugs (default: True)
        scenario (str, optional): Forecast scenario - "base", "optimistic", "pessimistic" (default: "base")
        progress_callback: Optional callback(percent, message) for progress reporting
        mcp_funcs: MCP function dictionary from skill_executor

    Returns:
        dict: Comprehensive forecast including:
            - drug_info: Drug identification and details
            - patent_analysis: Patent/exclusivity expiry and risk assessment
            - market_model: Market size estimates and spending data
            - comparable_drugs: Similar drugs with market benchmarks
            - sales_forecast: Year-by-year projections with scenarios
            - risk_factors: Key risks affecting the forecast

    Raises:
        ValueError: If indication is not provided
    """
    # BioClaw adaptation: auto-init MCP functions via McpClient if not injected
    if not mcp_funcs:
        _clients = {}
        mcp_funcs = {}
        _server_map = {
            'fda': ('fda_info', {
                'fda_lookup': {'method': 'lookup_drug'},
                'fda_patent_exclusivity': {'method': 'get_patent_exclusivity'},
                'fda_analyze_patent_cliff': {'method': 'analyze_patent_cliff'},
            }),
            'medicare': ('medicare_info', {
                'medicare_spending': {'method': 'search_spending'},
                'medicare_prescribers': {'method': 'search_prescribers'},
            }),
            'medicaid': ('medicaid_info', {
                'medicaid_info': {},
            }),
            'drugbank': ('drugbank_info', {
                'drugbank_search': {},
            }),
            'ctgov': ('ct_gov_studies', {
                'ctgov_search': {'method': 'search'},
            }),
            'financials': ('financial-intelligence', {
                'financials_lookup': {},
            }),
            'sec': ('sec-edgar', {
                'sec_search_companies': {'method': 'search_companies'},
            }),
            'cdc': ('cdc_data', {
                'cdc_health_data': {},
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

    # Validate required parameters
    if not indication or not indication.strip():
        raise ValueError(
            "indication is required. Many drugs have multiple approved indications with "
            "vastly different market sizes (e.g., semaglutide treats both 'type 2 diabetes' "
            "and 'obesity'). Please specify which indication to analyze."
        )
    # Create progress tracker
    progress = create_progress_tracker(callback=progress_callback)

    # Normalize drug name: try to get generic name if brand was provided
    # This ensures DrugBank lookups work (they need generic names)
    original_name = drug_name
    generic_name = get_generic_name(drug_name, mcp_funcs)
    if generic_name and generic_name.lower() != drug_name.lower():
        print(f"  → Normalized '{drug_name}' to generic name: {generic_name}")
        drug_name = generic_name

    result = {
        'drug_name': drug_name,
        'original_query': original_name if original_name.lower() != drug_name.lower() else None,
        'indication': indication,
        'forecast_years': forecast_years,
        'scenario': scenario,
        'data_quality': {
            'drug_details_found': False,
            'patent_data_found': False,
            'spending_data_found': False,
            'prevalence_data_found': False,
            'comparables_found': False
        }
    }

    print(f"\n💊 Drug Sales Forecasting: {drug_name}")
    print("=" * 70)
    progress.start_step('init', f"Analyzing {drug_name}...")

    # ===========================================================================
    # STEP 1: Drug Identification
    # ===========================================================================
    print(f"\n📋 Step 1: Identifying drug details...")
    progress.start_step('drug_id', "Identifying drug details from DrugBank...")

    try:
        drug_details = get_drug_details(drug_name, mcp_funcs)
        result['drug_info'] = drug_details

        if drug_details.get('drugbank_id'):
            result['data_quality']['drug_details_found'] = True
            print(f"  ✓ Found: {drug_details.get('generic_name', drug_name)}")
            print(f"    DrugBank ID: {drug_details.get('drugbank_id')}")
            print(f"    Type: {drug_details.get('drug_type', 'Unknown')}")
            print(f"    Analyzing for indication: {indication}")
        else:
            print(f"  ⚠ Drug not found in DrugBank, using provided name")

    except Exception as e:
        print(f"  ⚠ Could not identify drug: {e}")
        result['drug_info'] = {'drug_name': drug_name, 'error': str(e)}

    progress.complete_step("Drug identification complete")

    # ===========================================================================
    # STEP 2: Patent & Exclusivity Analysis
    # ===========================================================================
    print(f"\n📜 Step 2: Analyzing patent and exclusivity...")
    progress.start_step('patent', "Analyzing patent and exclusivity status...")

    # Get drug_type from DrugBank (if found) for biologic detection
    drug_type = result.get('drug_info', {}).get('drug_type')

    try:
        patent_data = get_patent_exclusivity(drug_name, drug_type, mcp_funcs)
        risk_assessment = get_patent_cliff_risk(drug_name, drug_type, mcp_funcs)

        result['patent_analysis'] = {
            'patent_expiry_date': patent_data.get('patent_expiry_date'),
            'exclusivity_expiry_date': patent_data.get('exclusivity_expiry_date'),
            'is_biologic': patent_data.get('is_biologic', False),
            'risk_level': risk_assessment.get('risk_level'),
            'years_to_cliff': risk_assessment.get('years_to_cliff'),
            'data_sources': patent_data.get('data_sources', [])
        }

        if patent_data.get('data_sources'):
            result['data_quality']['patent_data_found'] = True
            print(f"  ✓ Patent data found from: {', '.join(patent_data['data_sources'])}")
            print(f"    Is Biologic: {patent_data.get('is_biologic', False)}")
            print(f"    Risk Level: {risk_assessment.get('risk_level', 'Unknown').upper()}")
            if risk_assessment.get('years_to_cliff'):
                print(f"    Years to Cliff: {risk_assessment['years_to_cliff']:.1f}")
        else:
            print(f"  ⚠ Limited patent data available")

    except Exception as e:
        print(f"  ⚠ Patent analysis error: {e}")
        result['patent_analysis'] = {'error': str(e)}

    progress.complete_step("Patent analysis complete")

    # ===========================================================================
    # STEP 3: Market Sizing
    # ===========================================================================
    print(f"\n📊 Step 3: Estimating market size...")
    progress.start_step('market', "Estimating market size from prevalence and spending data...")

    # Get brand name for better Medicare data lookup
    brand_name = result.get('drug_info', {}).get('brand_name')
    if not brand_name:
        # Try to look up brand name from generic
        generic_name = result.get('drug_info', {}).get('generic_name', drug_name)
        brand_name = get_brand_name(generic_name, mcp_funcs)

    # Get DrugBank indication text for refining broad indications
    drug_indication_text = result.get('drug_info', {}).get('indication')

    try:
        if indication:
            market_data = estimate_market_size(
                drug_name, indication,
                brand_name=brand_name,
                drug_indication_text=drug_indication_text,
                mcp_funcs=mcp_funcs
            )
            result['market_model'] = market_data

            sizing = market_data.get('market_sizing', {})
            if sizing.get('total_addressable_market_usd'):
                result['data_quality']['spending_data_found'] = True
                print(f"  ✓ Market sizing complete")
                print(f"    US Patient Population: {sizing.get('us_patient_population', 0):,}")
                print(f"    Addressable Patients: {sizing.get('addressable_patients', 0):,}")
                if sizing.get('total_addressable_market_usd'):
                    print(f"    TAM: ${sizing['total_addressable_market_usd']:,.0f}")

            if market_data.get('prevalence_data', {}).get('us_prevalence_pct'):
                result['data_quality']['prevalence_data_found'] = True

            spending = market_data.get('spending_data', {})
            if spending.get('total_spending'):
                print(f"    Medicare Part D Spending: ${spending['total_spending']:,.0f}")
        else:
            # Just get spending data without full market sizing
            spending = get_drug_spending_data(drug_name, brand_name=brand_name, mcp_funcs=mcp_funcs)
            result['market_model'] = {'spending_data': spending}
            if spending.get('total_spending'):
                result['data_quality']['spending_data_found'] = True
                print(f"  ✓ Spending data found")
                print(f"    Medicare Part D Spending: ${spending['total_spending']:,.0f}")

    except Exception as e:
        print(f"  ⚠ Market sizing error: {e}")
        result['market_model'] = {'error': str(e)}

    progress.complete_step("Market sizing complete")

    # ===========================================================================
    # STEP 4: Comparable Drug Analysis
    # ===========================================================================
    if include_comparables:
        print(f"\n🔍 Step 4: Analyzing comparable drugs...")
        progress.start_step('comparables', "Finding and analyzing comparable drugs...")

        try:
            comparables = find_comparable_drugs(drug_name, indication, mcp_funcs)
            result['comparable_drugs'] = comparables

            if comparables.get('comparable_drugs'):
                result['data_quality']['comparables_found'] = True
                print(f"  ✓ Found {len(comparables['comparable_drugs'])} comparable drugs")
                for comp in comparables['comparable_drugs'][:3]:
                    spend = comp.get('medicare_spending')
                    spend_str = f"${spend:,.0f}" if spend else "N/A"
                    print(f"    • {comp['name']}: {spend_str}")

            landscape = comparables.get('competitive_landscape', {})
            if landscape.get('total_active_trials'):
                print(f"  ✓ Competitive Landscape: {landscape['total_active_trials']} active trials")

        except Exception as e:
            print(f"  ⚠ Comparable analysis error: {e}")
            result['comparable_drugs'] = {'error': str(e)}

        progress.complete_step("Comparable analysis complete")
    else:
        print(f"\n🔍 Step 4: Skipping comparable analysis (disabled)")
        progress.start_step('comparables', "Skipping comparable analysis...")
        progress.complete_step()

    # ===========================================================================
    # STEP 5: Sales Forecasting
    # ===========================================================================
    print(f"\n📈 Step 5: Generating sales forecast...")
    progress.start_step('forecast', "Running time-series forecast with patent cliff modeling...")

    try:
        # Determine current sales from spending data
        current_sales = None
        historical_sales = None
        spending_data = result.get('market_model', {}).get('spending_data', {})

        if spending_data.get('total_spending'):
            # Medicare Part D is ~30% of total market, so multiply
            medicare_spend = spending_data['total_spending']
            current_sales = medicare_spend * 3.3  # Rough multiplier

        # Build historical sales from Medicare yearly data
        historical_spending = spending_data.get('historical_spending', {})
        if historical_spending:
            historical_sales = []
            for year, year_data in sorted(historical_spending.items()):
                if year_data.get('total_spending'):
                    # Scale Medicare to total market
                    total_sales = year_data['total_spending'] * 3.3
                    historical_sales.append({
                        'date': f'{year}-06-30',  # Mid-year
                        'sales': total_sales,
                        'source': 'Medicare Part D (scaled)'
                    })

            if historical_sales:
                print(f"    Historical data: {len(historical_sales)} years ({historical_sales[0]['date'][:4]}-{historical_sales[-1]['date'][:4]})")

        # Get patent expiry for forecast
        patent_expiry = result.get('patent_analysis', {}).get('patent_expiry_date')
        is_biologic = result.get('patent_analysis', {}).get('is_biologic', False)

        # Calculate competitive pressure from pipeline analysis
        competitive_pressure = 0.0
        landscape = result.get('comparable_drugs', {}).get('competitive_landscape', {})
        total_trials = landscape.get('total_active_trials', 0)
        if total_trials > 100:
            competitive_pressure = 0.15  # High competition
        elif total_trials > 50:
            competitive_pressure = 0.10  # Medium competition
        elif total_trials > 20:
            competitive_pressure = 0.05  # Low competition

        # Extract segment revenue and TAM for carrying capacity estimation
        segment_revenue = None
        tam = None
        market_model = result.get('market_model', {})
        segment_data = market_model.get('segment_revenue_data', {})
        if segment_data.get('segment_revenue'):
            segment_revenue = segment_data['segment_revenue']
        market_sizing = market_model.get('market_sizing', {})
        if market_sizing.get('total_addressable_market_usd'):
            tam = market_sizing['total_addressable_market_usd']

        # Generate all scenarios with Monte Carlo simulation (logistic growth)
        if current_sales:
            all_scenarios = generate_all_scenarios(
                drug_name=drug_name,
                current_sales=current_sales,
                patent_expiry_date=patent_expiry,
                forecast_years=forecast_years,
                is_biologic=is_biologic,
                historical_sales=historical_sales,
                run_monte_carlo=True,
                competitive_pressure=competitive_pressure,
                segment_revenue=segment_revenue,
                tam=tam
            )
            result['sales_forecast'] = all_scenarios

            print(f"  ✓ Forecast generated for {forecast_years} years")
            print(f"    Model used: {all_scenarios.get('model_used', 'simple')}")
            print(f"    Current Sales (estimated): ${current_sales:,.0f}")
            print(f"    Peak Sales (base): ${all_scenarios['summary']['peak_sales_base']:,.0f}")
            print(f"    Peak Year: {all_scenarios['summary']['peak_year']}")

            # Show Monte Carlo results if available
            if all_scenarios.get('monte_carlo'):
                mc = all_scenarios['monte_carlo']
                print(f"    Monte Carlo (1000 simulations, logistic growth):")
                cap = mc.get('carrying_capacity', {})
                if cap.get('mean'):
                    print(f"      Market Ceiling (median): ${cap.get('sampled_median', cap['mean'])/1e9:.1f}B")
                print(f"      Final Year P10-P90: ${mc['summary']['final_year_p10_p90'][0]/1e9:.1f}B - ${mc['summary']['final_year_p10_p90'][1]/1e9:.1f}B")
                print(f"      Coefficient of Variation: {mc['summary']['coefficient_of_variation']:.1%}")
        else:
            # Use default $1B if no data available
            print(f"  ⚠ No spending data - using $1B default for illustration")
            all_scenarios = generate_all_scenarios(
                drug_name=drug_name,
                current_sales=1_000_000_000,
                patent_expiry_date=patent_expiry,
                forecast_years=forecast_years,
                is_biologic=is_biologic,
                run_monte_carlo=True,
                competitive_pressure=competitive_pressure,
                segment_revenue=segment_revenue,
                tam=tam
            )
            result['sales_forecast'] = all_scenarios
            result['sales_forecast']['note'] = 'Using default $1B - actual sales data not available'

    except Exception as e:
        print(f"  ⚠ Forecast error: {e}")
        result['sales_forecast'] = {'error': str(e)}

    progress.complete_step("Forecast complete")

    # ===========================================================================
    # STEP 6: Risk Analysis & Summary
    # ===========================================================================
    print(f"\n⚠️  Step 6: Compiling risk factors...")
    progress.start_step('visualization', "Compiling risk factors and summary...")

    risk_factors = []

    # Patent risk
    patent_risk = result.get('patent_analysis', {}).get('risk_level')
    if patent_risk == 'high':
        risk_factors.append('HIGH: Patent/exclusivity expiry within 2 years')
    elif patent_risk == 'medium':
        risk_factors.append('MEDIUM: Patent/exclusivity expiry within 5 years')
    elif patent_risk == 'expired':
        risk_factors.append('CRITICAL: Patent/exclusivity already expired - generic competition active')

    # Biologic vs small molecule
    if result.get('patent_analysis', {}).get('is_biologic'):
        risk_factors.append('Biologic: Biosimilar erosion typically 30-40% slower than generic erosion')
    else:
        risk_factors.append('Small molecule: Expect 80-90% erosion within 12 months of generic entry')

    # Competitive landscape
    landscape = result.get('comparable_drugs', {}).get('competitive_landscape', {})
    if landscape.get('total_active_trials', 0) > 50:
        risk_factors.append(f'Competitive threat: {landscape["total_active_trials"]} active trials in indication')

    # Data quality warnings
    dq = result['data_quality']
    missing = []
    if not dq['patent_data_found']:
        missing.append('patent expiry')
    if not dq['spending_data_found']:
        missing.append('sales/spending')
    if missing:
        risk_factors.append(f'Data gap: Limited {", ".join(missing)} data - forecast uncertainty higher')

    result['risk_factors'] = risk_factors

    # Summary
    result['summary'] = {
        'drug': drug_name,
        'indication': indication or 'Not specified',
        'is_biologic': result.get('patent_analysis', {}).get('is_biologic', False),
        'patent_cliff_risk': patent_risk or 'Unknown',
        'data_quality_score': sum(dq.values()) / len(dq) * 100,
        'forecast_confidence': 'High' if sum(dq.values()) >= 4 else 'Medium' if sum(dq.values()) >= 2 else 'Low'
    }

    progress.complete_step("Analysis complete!")

    # ===========================================================================
    # Final Output
    # ===========================================================================
    print(f"\n{'=' * 70}")
    print(f"✅ DRUG SALES FORECAST COMPLETE")
    print(f"{'=' * 70}")

    print(f"\n📋 Summary:")
    print(f"   Drug: {result['summary']['drug']}")
    print(f"   Indication: {result['summary']['indication']}")
    print(f"   Is Biologic: {result['summary']['is_biologic']}")
    print(f"   Patent Cliff Risk: {result['summary']['patent_cliff_risk'].upper()}")
    print(f"   Forecast Confidence: {result['summary']['forecast_confidence']}")
    print(f"   Data Quality: {result['summary']['data_quality_score']:.0f}%")

    print(f"\n⚠️  Risk Factors:")
    for risk in risk_factors:
        print(f"   • {risk}")

    # PRIMARY FORECAST: Monte Carlo with logistic growth (best-in-class)
    mc = result.get('sales_forecast', {}).get('monte_carlo')
    if mc and mc.get('percentiles_by_year'):
        model_type = mc.get('model', 'monte_carlo')
        years = sorted(mc['percentiles_by_year'].keys())

        print(f"\n📈 Sales Forecast - Logistic Growth Monte Carlo (1,000 simulations):")

        # Show carrying capacity (market ceiling)
        cap = mc.get('carrying_capacity', {})
        if cap.get('mean'):
            cap_p10, cap_p90 = cap.get('sampled_p10_p90', (0, 0))
            print(f"   Market Ceiling: ${cap.get('sampled_median', cap['mean'])/1e9:.1f}B (P10-P90: ${cap_p10/1e9:.1f}B - ${cap_p90/1e9:.1f}B)")

        # Show historical CAGR if available
        params = mc.get('parameters', {})
        if params.get('historical_cagr'):
            print(f"   Historical CAGR: {params['historical_cagr']*100:.0f}% → Adjusted growth rate: {params['market_growth_mean']*100:.0f}%")

        print(f"\n   {'Year':<8} {'P10 (Bear)':>14} {'P50 (Base)':>14} {'P90 (Bull)':>14}")
        print(f"   {'-'*8} {'-'*14} {'-'*14} {'-'*14}")
        for year in years[:forecast_years + 1]:
            pct = mc['percentiles_by_year'].get(year, {})
            if pct:
                print(f"   {year:<8} ${pct['p10']/1e9:>12.1f}B ${pct['p50']/1e9:>12.1f}B ${pct['p90']/1e9:>12.1f}B")

        # Summary stats
        cv = mc['summary']['coefficient_of_variation']
        uncertainty = 'Low' if cv < 0.15 else 'Medium' if cv < 0.30 else 'High'
        print(f"\n   Forecast Uncertainty: {uncertainty} (CV: {cv:.1%})")

    elif result.get('sales_forecast', {}).get('scenarios'):
        # Fallback to simple scenarios if Monte Carlo not available
        scenarios = result['sales_forecast']['scenarios']
        print(f"\n📈 Sales Forecast (next {forecast_years} years):")
        print(f"   {'Year':<8} {'Pessimistic':>15} {'Base':>15} {'Optimistic':>15}")
        print(f"   {'-'*8} {'-'*15} {'-'*15} {'-'*15}")

        years = sorted(scenarios['base'].keys())
        for year in years[:forecast_years + 1]:
            pess = scenarios['pessimistic'].get(year, 0)
            base = scenarios['base'].get(year, 0)
            opt = scenarios['optimistic'].get(year, 0)
            print(f"   {year:<8} ${pess/1e9:>13.1f}B ${base/1e9:>13.1f}B ${opt/1e9:>13.1f}B")

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Drug Sales & Patent Cliff Forecasting')
    parser.add_argument('drug_name', help='Drug name (brand or generic)')
    parser.add_argument('indication', help='Primary indication for market sizing (e.g., "type 2 diabetes", "obesity")')
    parser.add_argument('--years', '-y', type=int, default=5, help='Forecast years (default: 5)')
    parser.add_argument('--no-comparables', action='store_true', help='Skip comparable drug analysis')
    parser.add_argument('--scenario', '-s', choices=['base', 'optimistic', 'pessimistic'], default='base')

    args = parser.parse_args()

    result = drug_sales_forecasting(
        drug_name=args.drug_name,
        indication=args.indication,
        forecast_years=args.years,
        include_comparables=not args.no_comparables,
        scenario=args.scenario
    )
