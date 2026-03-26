#!/usr/bin/env python3
import sys
import os

# Determine the .claude directory path (works from any working directory)
_this_file = os.path.abspath(__file__)
_scripts_dir = os.path.dirname(_this_file)
_skill_dir = os.path.dirname(_scripts_dir)
_skills_dir = os.path.dirname(_skill_dir)
_claude_dir = os.path.dirname(_skills_dir)

# Add current scripts directory for local imports
sys.path.insert(0, _scripts_dir)

# Add company pipeline skill scripts to path (BioClaw container layout)
_company_pipeline_scripts = os.path.join(_skills_dir, "company-pipeline-breakdown", "scripts")
if os.path.isdir(_company_pipeline_scripts):
    sys.path.insert(0, _company_pipeline_scripts)

# BioClaw adaptation: MCP functions via McpClient
from mcp_client import McpClient

# Import comprehensive pipeline skill
from get_company_pipeline_breakdown import get_company_pipeline_breakdown

import re
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Any, Optional, Tuple

from progress_tracker import create_progress_tracker

# Import constants and utilities from refactored modules
from swot_constants import (
    NON_DRUG_ITEMS,
    FORMULATION_TERMS,
    CURRENCY_TO_USD_FALLBACK,
    CURRENCY_TO_USD,
    COMPANY_SUFFIXES,
)
from ticker_utils import generate_ticker_guesses, find_ticker
from sec_lookup import (
    get_sec_company_tickers,
    normalize_company_name,
    lookup_company_in_sec_tickers,
)
from financial_parser import (
    get_historical_exchange_rate,
    convert_to_usd,
    parse_xbrl_units,
    detect_reporting_currency,
    parse_xbrl_contexts,
    normalize_xbrl_segment_name,
    normalize_xbrl_geography_name,
    extract_xbrl_segment_revenue,
    parse_yahoo_value,
    is_annual_period,
    extract_year,
)
from market_collector import (
    get_market_performance,
    get_peer_comparison,
)
from financial_collector import (
    detect_company_region,
    get_financial_data,
    get_financial_data_from_yahoo,
    get_segment_revenue_from_xbrl,
)
from regulatory_products import (
    get_approved_products,
    get_patent_data,
    get_ema_products,
)
from swot_categorizer import categorize_swot
from report_formatter import format_swot_report

# ============================================================================
# Data collection and SWOT logic functions are now imported from separate modules:
# - financial_collector: detect_company_region, get_financial_data, get_financial_data_from_yahoo, get_segment_revenue_from_xbrl
# - regulatory_products: get_approved_products, get_patent_data, get_ema_products
# - company-pipeline-breakdown skill: get_company_pipeline_breakdown (comprehensive pipeline with M&A, regulatory checks)
# - market_collector: get_market_performance, get_peer_comparison
# - swot_categorizer: categorize_swot
# - report_formatter: format_swot_report
#
# NOTE: pipeline_collector.py is now deprecated - SWOT uses the full company-pipeline-breakdown skill
# ============================================================================


# Helper functions to map comprehensive pipeline output to SWOT expected format

def _extract_phase_counts(phase_summary: Dict) -> Dict[str, int]:
    """Extract simple phase -> count mapping from comprehensive phase_summary."""
    return {
        phase: data.get('trials', 0)
        for phase, data in phase_summary.items()
    }


def _extract_ta_conditions(therapeutic_areas: Dict) -> Dict[str, int]:
    """Extract therapeutic area -> trial count for SWOT compatibility."""
    return {
        ta: data.get('trials', 0)
        for ta, data in therapeutic_areas.items()
    }


def _normalize_drug_name(name: str) -> str:
    """Normalize drug name by stripping dose/formulation suffixes.

    Collapses dose-level entries like 'CV09070101 5μg' and 'CV09070101 12μg'
    into the base drug name 'CV09070101'. Also normalizes Greek characters.
    """
    # Normalize Greek characters to ASCII equivalents
    greek_map = {
        '\u039c': 'M',   # Greek capital Mu (Μ) → M
        '\u03bc': 'u',   # Greek small mu (μ) → u
        '\u0393': 'G',   # Greek capital Gamma
        '\u03b1': 'a',   # Greek small alpha
        '\u03b2': 'b',   # Greek small beta
        '\u03b3': 'g',   # Greek small gamma
        '\u03b4': 'd',   # Greek small delta
    }
    normalized = name
    for greek, ascii_char in greek_map.items():
        normalized = normalized.replace(greek, ascii_char)

    # Strip trailing dose patterns: "5μg", "12 mcg", "100mg", "0.5 mL", etc.
    normalized = re.sub(
        r'\s+[\d.]+\s*(?:mg|mcg|ug|Mg|μg|ΜG|ml|mL|g|kg|IU|U|units?)\s*$',
        '', normalized, flags=re.IGNORECASE
    ).strip()

    return normalized


def _extract_lead_drugs(drugs: Dict) -> List[Dict]:
    """Extract lead drugs with trial counts and highest phase from drugs dict.

    Deduplicates dose-level entries (e.g., 'CV09070101 5μg' and 'CV09070101 12μg')
    by merging them into a single entry with combined trial counts.
    """
    # First pass: collect and merge dose-level duplicates
    merged: Dict[str, Dict] = {}  # normalized_name -> merged drug_data

    for drug_name, drug_data in drugs.items():
        # Filter out non-drug items (PK probes, trial title noise, placebo, etc.)
        if drug_name.lower() in NON_DRUG_ITEMS:
            continue
        # Skip very short names (likely parsing artifacts)
        if len(drug_name) < 3:
            continue

        # Get highest phase (Phase 3 > Phase 2 > Phase 1)
        phases = drug_data.get('phases', [])
        if not phases:
            continue

        base_name = _normalize_drug_name(drug_name)
        if len(base_name) < 3:
            continue

        if base_name in merged:
            # Merge into existing entry
            existing = merged[base_name]
            existing['trial_count'] += drug_data.get('total_trials', 0)
            existing['phases'].update(phases)
            # Keep richer indication list
            for ind in drug_data.get('indications', []):
                if ind and ind not in existing['indications']:
                    existing['indications'].append(ind)
        else:
            merged[base_name] = {
                'name': base_name,
                'trial_count': drug_data.get('total_trials', 0),
                'phases': set(phases),
                'indications': list(drug_data.get('indications', [])),
            }

    # Second pass: build lead_drugs list
    phase_order = {'Phase 4': 4, 'Phase 3': 3, 'Phase 2': 2, 'Phase 1': 1}
    lead_drugs = []
    for entry in merged.values():
        highest_phase = max(entry['phases'], key=lambda p: phase_order.get(p, 0))
        indication = entry['indications'][0] if entry['indications'] else 'Unknown'
        lead_drugs.append({
            'name': entry['name'],
            'trial_count': entry['trial_count'],
            'highest_phase': highest_phase,
            'indication': indication,
            'reason': None  # Not available from pipeline skill
        })

    # Sort by trial count and take top drugs
    lead_drugs.sort(key=lambda x: x['trial_count'], reverse=True)
    return lead_drugs[:10]  # Return top 10


def _extract_drugs_by_phase(phase_summary: Dict) -> Dict[str, List[str]]:
    """Extract phase -> list of drug names mapping."""
    drugs_by_phase = {}
    for phase, data in phase_summary.items():
        # Phase summary doesn't have individual drug lists in the standard output
        # This is less critical for SWOT, so we can leave it as empty or populate from lead_drugs
        drugs_by_phase[phase] = []
    return drugs_by_phase


def generate_company_swot_analysis(
    company_name: str,
    skip_patents: bool = False,
    skip_ema: bool = False,
    skip_peers: bool = False,
    progress_callback=None,
    mcp_funcs: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Generate comprehensive company SWOT analysis.

    Args:
        company_name: Company name (e.g., "Exelixis", "Pfizer")
        skip_patents: Skip Orange Book patent lookup (faster)
        skip_ema: Skip EMA data (US-only analysis)
        skip_peers: Skip peer comparison data
        progress_callback: Optional callback(percent, step) for progress reporting
        mcp_funcs: Dictionary of MCP functions (injected by skill_executor)

    Returns:
        dict: Contains data_sources, swot_analysis, formatted_report
    """
    # Create progress tracker
    progress = create_progress_tracker(callback=progress_callback)

    print(f"\n{'='*80}")
    print(f"Generating SWOT Analysis for {company_name}")
    print(f"{'='*80}")
    skip_info = []
    if skip_patents:
        skip_info.append("patents")
    if skip_ema:
        skip_info.append("EMA")
    if skip_peers:
        skip_info.append("peers")
    if skip_info:
        print(f"Skipping: {', '.join(skip_info)}")
    progress.start_step('init', f"Starting SWOT analysis for {company_name}")

    analysis_date = datetime.now().strftime("%Y-%m-%d")

    # Collect financial data first (needed for segment revenue drug names)
    progress.start_step('financial', "Retrieving financial data from SEC EDGAR...")
    financial_data = get_financial_data(company_name, mcp_funcs=mcp_funcs)

    # Get marketed drugs from XBRL segment revenue for FDA lookup
    segment_revenue = financial_data.get('segment_revenue', {})
    segment_drug_names = list(segment_revenue.keys())
    print(f"   Found {len(segment_drug_names)} segments from XBRL")

    # Extract clean drug names from compound segment names for FDA lookup
    # e.g., "HIVProducts Biktarvy" -> ["HIVProducts Biktarvy", "Biktarvy"]
    def extract_drug_names_from_segments(segment_names):
        """Extract potential drug names from XBRL segment names.

        XBRL segments often have compound names like:
        - "HIVProducts Biktarvy" -> also search "Biktarvy"
        - "Oncology Trodelvy" -> also search "Trodelvy"
        - "Mounjaro" -> just search "Mounjaro"
        """
        drug_names = set(segment_names)  # Start with original names

        for seg_name in segment_names:
            # Split on spaces and look for capitalized words that could be drug names
            words = seg_name.split()
            if len(words) >= 2:
                # The last word is often the drug name in compound names
                last_word = words[-1]
                # Drug names are usually capitalized, 4+ chars, not common words
                if (len(last_word) >= 4 and
                    last_word[0].isupper() and
                    last_word.lower() not in ('sales', 'revenue', 'products', 'total', 'other')):
                    drug_names.add(last_word)

                # Also try combinations of last 2 words (e.g., "Hepatitis C" drugs)
                if len(words) >= 3:
                    last_two = ' '.join(words[-2:])
                    drug_names.add(last_two)

        return list(drug_names)

    # Get both raw segment names and extracted drug names for FDA lookup
    fda_search_names = extract_drug_names_from_segments(segment_drug_names)
    print(f"   Extracted {len(fda_search_names)} drug names for FDA lookup")

    # Get FDA approved products early (needed for pipeline reason detection AND segment filtering)
    progress.start_step('fda', "Checking FDA approved products...")
    fda_data = get_approved_products(company_name, drug_names=fda_search_names, mcp_funcs=mcp_funcs)

    # Extract approved product names AND generic names
    fda_product_names = fda_data.get('product_names', [])
    fda_generic_names = fda_data.get('generic_names', [])

    # Filter segment revenue to keep only FDA-matched products (removes categories)
    # This is data-driven: if a segment name matches an FDA product, it's a real product
    if segment_revenue and fda_product_names:
        # Normalize names for matching (handle format differences between XBRL and FDA)
        def normalize_for_match(name):
            """Normalize a name for fuzzy matching."""
            import re
            # Lowercase, remove special chars, collapse spaces
            n = name.lower()
            n = re.sub(r'[^a-z0-9\s]', '', n)
            n = re.sub(r'\s+', ' ', n).strip()
            return n

        # Build lookup from FDA products + generic names
        fda_names = fda_product_names + fda_generic_names
        fda_normalized = {normalize_for_match(name): name for name in fda_names}

        filtered_segments = {}
        for seg_name, seg_value in segment_revenue.items():
            seg_norm = normalize_for_match(seg_name)

            # Check if segment matches any FDA product
            # 1. Exact normalized match
            # 2. FDA name contained in segment (e.g., "HIVProducts Biktarvy" contains "biktarvy")
            # 3. Segment contained in FDA name (unlikely but check anyway)
            is_fda_product = (
                seg_norm in fda_normalized or
                any(fda_norm in seg_norm for fda_norm in fda_normalized) or
                any(seg_norm in fda_norm for fda_norm in fda_normalized if len(seg_norm) > 3)
            )
            if is_fda_product:
                filtered_segments[seg_name] = seg_value

        if filtered_segments:
            removed_count = len(segment_revenue) - len(filtered_segments)
            if removed_count > 0:
                print(f"   Filtered {removed_count} category segments using FDA cross-reference")
                # Update financial_data with filtered segments
                financial_data['segment_revenue'] = filtered_segments
                segment_revenue = filtered_segments
                segment_drug_names = list(segment_revenue.keys())
            print(f"   Keeping {len(filtered_segments)} FDA-verified products")
    # Combine both for matching - pipeline drugs use generic names (e.g., "Semaglutide" not "Ozempic")
    approved_drugs = fda_product_names + fda_generic_names
    print(f"   Found {len(fda_product_names)} FDA products, {len(fda_generic_names)} generic names")
    if fda_generic_names:
        print(f"   Generic names: {fda_generic_names[:5]}...")

    # Now collect clinical pipeline using comprehensive company pipeline skill
    progress.start_step('pipeline', "Collecting clinical pipeline from ClinicalTrials.gov...")

    # Use comprehensive pipeline skill with progress callback
    # Skip regulatory checks since SWOT does its own FDA/EMA lookups
    def pipeline_progress(percent, step):
        # Pipeline reports 0-100, convert to 0.0-1.0 for update_step
        # ProgressTracker will map this to the correct absolute % (34-65%) based on step weight
        progress.update_step(percent / 100.0, step)

    raw_pipeline = get_company_pipeline_breakdown(
        company=company_name,
        include_subsidiaries=True,  # Include M&A for comprehensive view
        skip_regulatory=True,       # SWOT does its own FDA/EMA checks
        include_drugs=True,
        include_devices=False,      # SWOT focuses on drugs
        include_marketed=False,     # SWOT gets marketed products separately
        progress_callback=pipeline_progress,
        mcp_funcs=mcp_funcs
    )

    # Adapt comprehensive pipeline output to SWOT expected format
    clinical_data = {
        'total_trials': raw_pipeline.get('total_active_trials', 0),
        'phase_distribution': _extract_phase_counts(raw_pipeline.get('phase_summary', {})),
        'status_distribution': {'Recruiting': raw_pipeline.get('total_active_trials', 0)},  # Active trials only
        'therapeutic_areas': _extract_ta_conditions(raw_pipeline.get('therapeutic_areas', {})),
        'lead_drugs': _extract_lead_drugs(raw_pipeline.get('drugs', {})),
        'drugs_by_phase': _extract_drugs_by_phase(raw_pipeline.get('phase_summary', {})),
        'notable_trials': [],  # Not needed for SWOT
        'all_drugs': list(raw_pipeline.get('drugs', {}).keys()),
        'total_enrollment': raw_pipeline.get('total_enrollment', 0),
        'success': raw_pipeline.get('total_active_trials', 0) > 0
    }

    # Enrich FDA data with therapeutic areas from pipeline (when FDA pharm_class is empty)
    # This uses actual clinical trial data instead of hardcoded patterns
    if not fda_data.get('therapeutic_areas') and clinical_data.get('therapeutic_areas'):
        pipeline_tas = clinical_data['therapeutic_areas']
        # Use top therapeutic areas from pipeline as proxy for approved products
        # This is data-driven: if company focuses on Oncology trials, their approved products likely are too
        fda_data['therapeutic_areas'] = dict(list(pipeline_tas.items())[:3])  # Top 3 TAs
        print(f"   Enriched FDA data with {len(fda_data['therapeutic_areas'])} therapeutic areas from pipeline")

    # Extract drug names from clinical pipeline for additional FDA/EMA lookups
    drug_names = list(segment_drug_names)  # Start with segment drugs
    lead_drugs = clinical_data.get('lead_drugs', [])
    for drug in lead_drugs:
        if isinstance(drug, dict) and drug.get('name'):
            if drug['name'] not in drug_names:
                drug_names.append(drug['name'])
        elif isinstance(drug, str) and drug not in drug_names:
            drug_names.append(drug)
    # Also add all unique drugs (cleaned by get_company_pipeline + NON_DRUG_ITEMS filter)
    for drug in clinical_data.get('all_drugs', []):
        if drug and drug not in drug_names and drug.lower() not in NON_DRUG_ITEMS and len(drug) >= 3:
            drug_names.append(drug)
    print(f"   Total {len(drug_names)} drug names for EMA lookup: {drug_names[:10]}...")

    # Resolve internal research codes to brand/trade names via CT.gov study details.
    # Internal codes (BNT162b2, MEDI4736) often appear alongside their brand names
    # in trial descriptions, e.g. "BNT162b2 [Comirnaty]". Resolving these enables
    # FDA and EMA lookups that otherwise fail on alphanumeric codes.
    INTERNAL_CODE_RE = re.compile(r'^[A-Z]{2,5}[-]?\d{3,}', re.IGNORECASE)
    ctgov_search_fn = mcp_funcs.get('ctgov_search')
    ctgov_get_study_fn = mcp_funcs.get('ctgov_get_study')
    if ctgov_search_fn and ctgov_get_study_fn:
        internal_codes = [
            name for name in drug_names
            if name and INTERNAL_CODE_RE.match(name) and len(name) >= 5
        ]
        if internal_codes:
            print(f"   Resolving {len(internal_codes)} internal codes via CT.gov study details...")
            for code in internal_codes[:3]:  # Limit to 3 codes to control API calls
                try:
                    # Find 1 trial for this code
                    search_result = ctgov_search_fn(intervention=code, pageSize=1)
                    search_text = str(search_result) if isinstance(search_result, str) else search_result.get('text', str(search_result))
                    nct_ids = re.findall(r'NCT\d{8}', search_text)
                    if not nct_ids:
                        continue

                    # Get study details (contains full text with brand name mentions)
                    study_result = ctgov_get_study_fn(nctId=nct_ids[0])
                    study_text = str(study_result) if isinstance(study_result, str) else study_result.get('text', str(study_result))

                    # Pattern: CODE [BrandName] or CODE \[BrandName\] or CODE (BrandName)
                    escaped_code = re.escape(code)
                    brand_patterns = [
                        re.compile(escaped_code + r'\s*(?:\\\[|\[|\()([A-Z][a-z]{2,}[a-z]*)(?:\\\]|\]|\))', re.IGNORECASE),
                        re.compile(r'([A-Z][a-z]{2,}[a-z]*)\s*(?:\\\[|\[|\()' + escaped_code + r'(?:\\\]|\]|\))', re.IGNORECASE),
                    ]
                    for pat in brand_patterns:
                        matches = pat.findall(study_text)
                        for brand in matches:
                            brand = brand.strip()
                            # Validate: must be a plausible drug name (not common words)
                            if (brand and len(brand) >= 4
                                    and brand.lower() not in {'also', 'with', 'from', 'that', 'this', 'were', 'been', 'have', 'will', 'dose', 'each', 'after', 'prior'}
                                    and brand not in drug_names):
                                drug_names.insert(0, brand)
                                print(f"   Resolved {code} → {brand}")
                                break
                        else:
                            continue
                        break  # Found a match from one pattern, move to next code
                except Exception as e:
                    print(f"   Warning: Failed to resolve {code}: {e}")
                    continue

    # Second-pass FDA lookup: if initial FDA search found few products (e.g., foreign filers
    # with no XBRL segments), retry with pipeline-discovered drug names.
    # This handles BioNTech-style companies where internal codes (BNT162b2) are only
    # discoverable from CT.gov pipeline, not from SEC filings.
    pipeline_new_names = [n for n in drug_names if n not in fda_search_names]
    if fda_data.get('total_products', 0) < 2 and pipeline_new_names:
        print(f"\n   Second-pass FDA lookup with {len(pipeline_new_names)} pipeline drug names...")
        fda_data_2 = get_approved_products(company_name, drug_names=pipeline_new_names, mcp_funcs=mcp_funcs)
        if fda_data_2.get('total_products', 0) > fda_data.get('total_products', 0):
            # Merge new products into existing FDA data
            existing_brands = {p.upper() for p in fda_data.get('product_names', [])}
            for prod_name in fda_data_2.get('product_names', []):
                if prod_name.upper() not in existing_brands:
                    fda_data.setdefault('product_names', []).append(prod_name)
            for gn in fda_data_2.get('generic_names', []):
                if gn not in fda_data.get('generic_names', []):
                    fda_data.setdefault('generic_names', []).append(gn)
            for prod in fda_data_2.get('products', []):
                fda_data.setdefault('products', []).append(prod)
            # Update counts
            fda_data['total_products'] = fda_data_2['total_products']
            fda_data['total_brands'] = fda_data_2.get('total_brands', fda_data_2['total_products'])
            if fda_data_2.get('drug_franchises'):
                fda_data['drug_franchises'] = fda_data_2['drug_franchises']
            if fda_data_2.get('franchise_names'):
                fda_data['franchise_names'] = fda_data_2['franchise_names']
            # Merge therapeutic areas
            for ta, count in fda_data_2.get('therapeutic_areas', {}).items():
                fda_data.setdefault('therapeutic_areas', {})[ta] = count
            fda_product_names = fda_data.get('product_names', [])
            fda_generic_names = fda_data.get('generic_names', [])
            approved_drugs = fda_product_names + fda_generic_names
            print(f"   Second pass found {fda_data_2['total_products']} products → total {fda_data['total_products']}")

    # Get Orange Book patent data for FDA products (small molecules only)
    if skip_patents:
        print("   Skipping Orange Book patent lookup")
        patent_data = {'success': False, 'skipped': True}
    else:
        progress.start_step('patent', "Checking Orange Book patent data...")
        patent_data = get_patent_data(fda_product_names, mcp_funcs=mcp_funcs)
    fda_data['patent_data'] = patent_data  # Attach to FDA data for use in SWOT analysis

    # Get EMA approved products
    # Extract subsidiary names from pipeline for EMA MAH matching
    # (e.g., J&J → Janssen discovered via CT.gov sponsor analysis)
    subsidiary_names = raw_pipeline.get('subsidiaries', [])
    if isinstance(subsidiary_names, dict):
        subsidiary_names = list(subsidiary_names.keys())

    if skip_ema:
        print("   Skipping EMA lookup")
        ema_data = {'success': False, 'skipped': True, 'total_products': 0}
    else:
        progress.start_step('ema', "Checking EMA approved products...")
        ema_data = get_ema_products(company_name, drug_names=drug_names, fda_product_names=fda_product_names,
                                   subsidiary_names=subsidiary_names, mcp_funcs=mcp_funcs)

    progress.start_step('market', "Getting market performance data...")
    market_data = get_market_performance(company_name, mcp_funcs=mcp_funcs)

    # Get peer comparison data
    peer_data = {'success': False, 'skipped': True}
    if not skip_peers:
        progress.update_step(0.5, "Getting peer comparison data...")
        peer_data = get_peer_comparison(company_name, mcp_funcs=mcp_funcs)

        # Use P/E from peer comparison as fallback (more reliable for ADRs)
        if peer_data.get('target_pe') and not market_data.get('pe_ratio'):
            market_data['pe_ratio'] = peer_data['target_pe']
            print(f"   Using P/E from peer comparison: {peer_data['target_pe']}")

    # Categorize into SWOT
    progress.start_step('categorize', "Categorizing data into SWOT framework...")
    swot_analysis = categorize_swot(
        clinical_data, financial_data, fda_data,
        market_data, ema_data, company_name, peer_data
    )

    # Format report
    progress.start_step('report', "Generating final report...")
    data_sources = {
        'clinical_pipeline': clinical_data,
        'financial_data': financial_data,
        'approved_products': fda_data,
        'ema_products': ema_data,
        'market_performance': market_data,
        'peer_comparison': peer_data
    }

    formatted_report = format_swot_report(
        company_name,
        data_sources,
        swot_analysis,
        analysis_date
    )

    progress.complete_step("Analysis complete!")

    return {
        'company_name': company_name,
        'last_updated': analysis_date,
        'data_sources': data_sources,
        'swot_analysis': swot_analysis,
        'formatted_report': formatted_report
    }


def _build_bioclaw_mcp_funcs():
    """Build mcp_funcs dict using McpClient for BioClaw container/local execution."""
    clients = {}
    mcp_funcs = {}

    server_map = {
        'sec': ('sec-edgar', {
            'sec_search_companies': {'method': 'search_companies'},
            'sec_get_facts': {'method': 'get_company_facts'},
            'sec_get_filing': {'method': 'get_company_submissions'},
            'sec_get_cik': {'method': 'get_company_cik'},
        }),
        'financials': ('financial-intelligence', {
            'financials_lookup': {},  # pass method through
        }),
        'fda': ('fda_info', {
            'fda_lookup': {'method': 'lookup_drug'},
            'fda_get_patent_exclusivity': {'method': 'get_patent_exclusivity'},
        }),
        'ema': ('ema_data', {
            'ema_search': {'method': 'search_medicines'},
        }),
        'ctgov': ('ct_gov_studies', {
            'ctgov_search': {'method': 'search'},
            'ctgov_get_study': {'method': 'get'},
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
    company = sys.argv[1] if len(sys.argv) > 1 else "Exelixis"

    _cli_mcp_funcs, _cli_clients = _build_bioclaw_mcp_funcs()

    result = generate_company_swot_analysis(company, mcp_funcs=_cli_mcp_funcs)

    # Cleanup
    for c in _cli_clients.values():
        c.close()

    print(f"\n{'='*80}")
    print(f"SWOT Analysis Complete: {result['company_name']}")
    print(f"{'='*80}")

    pipeline = result['data_sources']['clinical_pipeline']
    fda = result['data_sources']['approved_products']
    ema = result['data_sources'].get('ema_products', {})
    market = result['data_sources']['market_performance']
    financial = result['data_sources']['financial_data']

    print(f"\nData Collection:")
    print(f"  Clinical Trials: {pipeline['total_trials']}")

    # Show lead drugs
    lead_drugs = pipeline.get('lead_drugs', [])
    if lead_drugs:
        print(f"  Lead Drugs: {', '.join(d['name'] for d in lead_drugs[:3])}")

    print(f"  FDA Products: {fda.get('total_products', 0)}")
    print(f"  EMA Products: {ema.get('total_products', 0) if ema else 'N/A'}")

    market_cap = market.get('market_cap')
    print(f"  Market Cap: ${market_cap/1e9:.1f}B" if market_cap else "  Market Cap: N/A")

    # Show financial trends
    rev = financial.get('revenue', {})
    if rev.get('current'):
        yoy = rev.get('yoy_growth')
        yoy_str = f" ({'+' if yoy >= 0 else ''}{yoy*100:.0f}% YoY)" if yoy else ""
        print(f"  Revenue: ${rev['current']/1e9:.1f}B{yoy_str}")

    print(f"\nSWOT Framework:")
    print(f"  Strengths: {len(result['swot_analysis']['strengths'])} points")
    print(f"  Weaknesses: {len(result['swot_analysis']['weaknesses'])} points")
    print(f"  Opportunities: {len(result['swot_analysis']['opportunities'])} points")
    print(f"  Threats: {len(result['swot_analysis']['threats'])} points")
    print(f"\n{'='*80}\n")
