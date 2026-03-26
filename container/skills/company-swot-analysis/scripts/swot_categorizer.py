#!/usr/bin/env python3
"""
SWOT categorization logic for company SWOT analysis.

This module provides the core business logic for categorizing
collected data into Strengths, Weaknesses, Opportunities, and Threats.
"""

from typing import Any, Dict, List, Optional


def categorize_swot(clinical_data, financial_data, fda_data, market_data,
                    ema_data=None, company_name=None, peer_data=None):
    """Categorize data into SWOT framework with specific, named insights.

    Args:
        clinical_data: Clinical trial pipeline data (with lead_drugs, notable_trials)
        financial_data: SEC EDGAR financial data (with multi-year trends)
        fda_data: FDA approved products data
        peer_data: Peer comparison data (optional)
        market_data: Yahoo Finance market data
        ema_data: EMA approved products data (optional)
        company_name: Company name (optional)
    """
    print("\n🎯 Categorizing into SWOT framework...")

    swot = {'strengths': [], 'weaknesses': [], 'opportunities': [], 'threats': []}

    # =========================================================================
    # STRENGTHS - Specific, named insights
    # =========================================================================

    # Lead drug franchise
    lead_drugs = clinical_data.get('lead_drugs', [])
    if lead_drugs:
        lead = lead_drugs[0]
        drug_names = ', '.join(d['name'] for d in lead_drugs[:3])
        swot['strengths'].append({
            'category': 'Lead Drug Franchise',
            'point': f"Strong clinical programs for: {drug_names}",
            'evidence': f"Lead asset {lead['name']} in {lead['trial_count']} active trials (highest: {lead['highest_phase']})"
        })

    # FDA approved products with specific names (deduplicated by generic)
    if fda_data.get('total_products', 0) > 0:
        # Use franchise_names (deduplicated) if available, otherwise fall back to product_names
        franchise_names = fda_data.get('franchise_names', fda_data.get('product_names', []))
        names_str = ', '.join(franchise_names[:5]) if franchise_names else 'multiple products'

        # Get counts
        unique_drugs = fda_data.get('total_products', 0)  # Already deduplicated count
        total_brands = fda_data.get('total_brands', unique_drugs)  # Original brand count

        # Build evidence string
        if unique_drugs == total_brands:
            evidence = f"{unique_drugs} drug{'s' if unique_drugs != 1 else ''} across {len(fda_data.get('therapeutic_areas', {}))} therapeutic areas"
        else:
            evidence = f"{unique_drugs} drug franchise{'s' if unique_drugs != 1 else ''} ({total_brands} formulations) across {len(fda_data.get('therapeutic_areas', {}))} therapeutic areas"

        swot['strengths'].append({
            'category': 'Commercial Portfolio',
            'point': f"FDA-approved portfolio: {names_str}",
            'evidence': evidence
        })

    # EMA products (if different from FDA, shows global reach)
    # Single consolidated entry — no duplicate "EU Market Access" added below
    if ema_data and ema_data.get('total_products', 0) > 0:
        ema_names = ema_data.get('product_names', [])[:3]
        ema_str = ', '.join(ema_names) if ema_names else 'products'
        ema_areas = ema_data.get('therapeutic_areas', {})
        evidence = f"{ema_data['total_products']} EU-approved products"
        if ema_areas:
            evidence += f" in {len(ema_areas)} therapeutic areas"
        swot['strengths'].append({
            'category': 'Global Regulatory',
            'point': f"EMA-authorized in Europe: {ema_str}",
            'evidence': evidence
        })

    # Pipeline depth with specific drug names
    total_trials = clinical_data.get('total_trials', 0)
    if total_trials >= 2:  # Lowered from >10 to work for small biotechs
        phase_dist = clinical_data.get('phase_distribution', {})
        phase3 = phase_dist.get('Phase 3', 0) or phase_dist.get('Phase3', 0)

        # Get phase 3 drugs specifically
        phase3_drugs = clinical_data.get('drugs_by_phase', {}).get('Phase 3', [])[:3]
        drugs_str = ', '.join(phase3_drugs) if phase3_drugs else ''

        evidence = f"Phase 3: {phase3}"
        if drugs_str:
            evidence += f" ({drugs_str})"

        swot['strengths'].append({
            'category': 'Pipeline Depth',
            'point': f"Active pipeline with {total_trials} ongoing trials",
            'evidence': evidence
        })

    # Financial strength with trends
    # Prefer XBRL consolidated revenue (more accurate) over basic facts
    segment_revenue = financial_data.get('segment_revenue', {})
    xbrl_consolidated = financial_data.get('xbrl_consolidated', 0)

    # Calculate total from segment revenue if available
    total_segment_revenue = sum(segment_revenue.values()) if segment_revenue else 0
    xbrl_revenue = max(xbrl_consolidated, total_segment_revenue)

    revenue_data = financial_data.get('revenue', {})
    basic_revenue = revenue_data.get('current', 0)

    # Use XBRL revenue if significantly larger (more accurate)
    actual_revenue = xbrl_revenue if xbrl_revenue > basic_revenue * 2 else basic_revenue

    if actual_revenue > 0:
        rev_b = actual_revenue / 1e9
        point = f"Revenue base of ${rev_b:.1f}B"

        # Add growth rate if available (from basic data)
        yoy = revenue_data.get('yoy_growth')
        cagr = revenue_data.get('cagr')
        if yoy is not None:
            direction = "+" if yoy >= 0 else ""
            point += f" ({direction}{yoy*100:.0f}% YoY)"

        evidence = "SEC EDGAR XBRL" if xbrl_revenue > basic_revenue else "SEC EDGAR filings"
        if cagr is not None:
            evidence += f", {cagr*100:.0f}% CAGR"

        swot['strengths'].append({
            'category': 'Financial Performance',
            'point': point,
            'evidence': evidence
        })

    # Lead franchise drug (from XBRL segment revenue) - shows commercial products with revenue
    if segment_revenue:
        top_product = list(segment_revenue.items())[0] if segment_revenue else None
        if top_product and top_product[1] >= 100e6:  # >$100M revenue
            product_name, product_revenue = top_product
            rev_str = f"${product_revenue/1e9:.1f}B" if product_revenue >= 1e9 else f"${product_revenue/1e6:.0f}M"

            # Count approved products from FDA data
            fda_products = fda_data.get('product_names', [])
            indication_count = len(fda_data.get('therapeutic_areas', {}))

            evidence = f"{rev_str} annual revenue"
            if indication_count > 0:
                evidence += f", approved in {indication_count} therapeutic areas"

            swot['strengths'].append({
                'category': 'Lead Franchise',
                'point': f"{product_name} franchise: {rev_str} annual sales",
                'evidence': evidence
            })

            # Additional products if any
            other_products = list(segment_revenue.items())[1:3]
            other_strs = []
            for name, val in other_products:
                if val >= 1e6:
                    other_strs.append(f"{name}: ${val/1e6:.0f}M")
            if other_strs:
                swot['strengths'].append({
                    'category': 'Product Portfolio',
                    'point': f"Additional commercial products",
                    'evidence': '; '.join(other_strs)
                })

    # Geographic revenue breakdown
    geographic_revenue = financial_data.get('geographic_revenue', {})
    if geographic_revenue and len(geographic_revenue) >= 2:
        geo_strs = []
        for geo_name, geo_value in list(geographic_revenue.items())[:3]:
            if geo_value >= 1e9:
                geo_strs.append(f"{geo_name}: ${geo_value/1e9:.1f}B")
            elif geo_value >= 1e6:
                geo_strs.append(f"{geo_name}: ${geo_value/1e6:.0f}M")

        if geo_strs:
            swot['strengths'].append({
                'category': 'Geographic Diversification',
                'point': f"Revenue across {len(geographic_revenue)} geographies",
                'evidence': '; '.join(geo_strs)
            })

    # Market position - show for any company with market cap data
    if market_data.get('market_cap'):
        cap_b = market_data['market_cap'] / 1e9
        if cap_b >= 0.5:  # Lowered from >$10B to >=$500M for small biotechs
            swot['strengths'].append({
                'category': 'Market Position',
                'point': f"Market capitalization of ${cap_b:.1f}B",
                'evidence': "Public company with established investor base"
            })

    # NOTE: EMA strength entry is consolidated above in "Global Regulatory" — no duplicate here

    # =========================================================================
    # WEAKNESSES - Data-driven concerns
    # =========================================================================

    # Limited late-stage pipeline
    # Helper to count Phase 3 trials including combined phases (Phase2, Phase3)
    phase_dist = clinical_data.get('phase_distribution', {})
    phase3 = phase_dist.get('Phase 3', 0) or phase_dist.get('Phase3', 0)
    # Also count combined phases that include Phase 3
    for phase_key, count in phase_dist.items():
        if 'Phase 3' in phase_key or 'Phase3' in phase_key:
            if phase_key not in ('Phase 3', 'Phase3'):  # Don't double count
                phase3 += count
    phase2 = phase_dist.get('Phase 2', 0) or phase_dist.get('Phase2', 0)
    total = clinical_data.get('total_trials', 0)

    if total > 5 and phase3 < 3:
        swot['weaknesses'].append({
            'category': 'Late-Stage Pipeline',
            'point': f"Limited Phase 3 programs ({phase3} trials)",
            'evidence': f"Pipeline concentration in earlier phases (Phase 2: {phase2})"
        })

    # R&D spending trend
    rd_data = financial_data.get('rd_expense', {})
    if rd_data.get('yoy_growth') and rd_data['yoy_growth'] > 0.3:  # >30% increase
        rd_current = rd_data.get('current', 0) / 1e6
        swot['weaknesses'].append({
            'category': 'R&D Costs',
            'point': f"R&D expenses grew {rd_data['yoy_growth']*100:.0f}% YoY",
            'evidence': f"Current R&D: ${rd_current:.0f}M - may pressure margins"
        })

    # Limited product diversity
    if fda_data.get('total_products', 0) > 0 and fda_data.get('total_products', 0) < 5:
        swot['weaknesses'].append({
            'category': 'Product Concentration',
            'point': f"Limited commercial portfolio ({fda_data['total_products']} products)",
            'evidence': "Revenue concentration risk from few approved drugs"
        })

    # Revenue decline warning
    revenue_data = financial_data.get('revenue', {})
    if revenue_data.get('yoy_growth') and revenue_data['yoy_growth'] < -0.05:  # >5% decline
        rev_current = revenue_data.get('current', 0) / 1e9
        swot['weaknesses'].append({
            'category': 'Revenue Decline',
            'point': f"Revenue declined {abs(revenue_data['yoy_growth'])*100:.0f}% YoY",
            'evidence': f"Current annual revenue: ${rev_current:.1f}B"
        })

    # Net income decline / losses
    ni_data = financial_data.get('net_income', {})
    ni_current = ni_data.get('current', 0)
    if ni_current < 0:
        loss_m = abs(ni_current) / 1e6
        swot['weaknesses'].append({
            'category': 'Profitability',
            'point': f"Operating at a net loss (${loss_m:.0f}M)",
            'evidence': "Negative net income may require capital raises or limit investment"
        })
    elif ni_data.get('yoy_growth') and ni_data['yoy_growth'] < -0.2:  # >20% decline
        swot['weaknesses'].append({
            'category': 'Earnings Pressure',
            'point': f"Net income declined {abs(ni_data['yoy_growth'])*100:.0f}% YoY",
            'evidence': "Profitability under pressure from costs or competition"
        })

    # High R&D burn rate (R&D > 50% of revenue indicates pre-profit biotech risk)
    rd_data = financial_data.get('rd_expense', {})
    rd_current = rd_data.get('current', 0)
    # Use best available revenue figure: XBRL consolidated > segment sum > basic SEC
    segment_revenue = financial_data.get('segment_revenue', {})
    xbrl_consolidated = financial_data.get('xbrl_consolidated', 0)
    segment_sum = sum(segment_revenue.values()) if segment_revenue else 0
    basic_rev = revenue_data.get('current', 0)
    rev_for_ratio = max(xbrl_consolidated, segment_sum, basic_rev)

    if rd_current > 0 and rev_for_ratio > 0:
        rd_ratio = rd_current / rev_for_ratio
        if rd_ratio > 0.5:  # R&D > 50% of revenue
            swot['weaknesses'].append({
                'category': 'Capital Intensity',
                'point': f"High R&D intensity ({rd_ratio*100:.0f}% of revenue)",
                'evidence': f"R&D: ${rd_current/1e6:.0f}M vs Revenue: ${rev_for_ratio/1e9:.1f}B"
            })

    # Cash runway analysis for loss-making companies
    cash_data = financial_data.get('cash', {})
    cash_current = cash_data.get('current', 0) if isinstance(cash_data, dict) else 0
    ni_data = financial_data.get('net_income', {})
    ni_current = ni_data.get('current', 0) if isinstance(ni_data, dict) else ni_data

    if cash_current > 0 and rd_current > 0:
        cash_runway_years = cash_current / rd_current
        cash_m = cash_current / 1e6
        rd_m = rd_current / 1e6

        # Pre-revenue or loss-making: flag as weakness if runway < 2 years
        if ni_current is not None and ni_current < 0:
            if cash_runway_years < 2.0:
                swot['weaknesses'].append({
                    'category': 'Cash Runway',
                    'point': f"Limited cash runway ({cash_runway_years:.1f} years at current burn)",
                    'evidence': f"Cash: ${cash_m:.0f}M, Annual R&D: ${rd_m:.0f}M, Net Loss: ${abs(ni_current)/1e6:.0f}M"
                })
            else:
                # Mention runway for loss-making companies (informational)
                swot['strengths'].append({
                    'category': 'Financial Position',
                    'point': f"Strong cash runway ({cash_runway_years:.1f} years)",
                    'evidence': f"Cash: ${cash_m:.0f}M supports R&D at ${rd_m:.0f}M/year despite losses"
                })

    # -------------------------------------------------------------------------
    # Factual risk factors (presented without judgment - user interprets)
    # -------------------------------------------------------------------------

    # Valuation context — contextual P/E classification
    pe_ratio = market_data.get('pe_ratio')
    if pe_ratio:
        # Get peer median P/E for context (if available)
        peer_data = peer_data or {}
        peer_pes = [p.get('pe_ratio') for p in peer_data.get('peers', []) if p.get('pe_ratio')]
        peer_median = sorted(peer_pes)[len(peer_pes)//2] if peer_pes else None

        if peer_median and pe_ratio < peer_median * 0.7:
            # Trading at >30% discount to peers — strength (undervalued)
            swot['strengths'].append({
                'category': 'Valuation',
                'point': f"Attractive valuation at {pe_ratio:.1f}x P/E",
                'evidence': f"Below peer median of {peer_median:.1f}x — potential value opportunity"
            })
        elif pe_ratio > 80:
            # Very high P/E — weakness (overvalued or minimal earnings)
            swot['weaknesses'].append({
                'category': 'Valuation Risk',
                'point': f"Elevated valuation at {pe_ratio:.1f}x P/E",
                'evidence': "High multiple may reflect growth premium or thin earnings base"
            })
        else:
            # Neutral — present as factual context, not weakness
            evidence = "Valuation multiple for investor consideration"
            if peer_median:
                ratio_to_peers = pe_ratio / peer_median
                evidence = f"vs peer median {peer_median:.1f}x ({ratio_to_peers:.1f}x relative)"
            swot['weaknesses'].append({
                'category': 'Valuation',
                'point': f"Trading at {pe_ratio:.1f}x P/E",
                'evidence': evidence
            })

    # Revenue concentration - factual breakdown
    segment_revenue = financial_data.get('segment_revenue', {})
    if segment_revenue:
        # Use sum of segment revenue as denominator (more reliable than basic SEC facts)
        total_revenue = sum(segment_revenue.values())
        if total_revenue <= 0:
            revenue_data = financial_data.get('revenue', {})
            total_revenue = revenue_data.get('current', 0) if isinstance(revenue_data, dict) else 0
        if total_revenue <= 0:
            total_revenue = financial_data.get('revenue_current', 0)

        if total_revenue > 0:
            sorted_segments = sorted(segment_revenue.items(), key=lambda x: x[1], reverse=True)
            if sorted_segments:
                top_product, top_revenue = sorted_segments[0]
                top_concentration = top_revenue / total_revenue
                swot['weaknesses'].append({
                    'category': 'Revenue Concentration',
                    'point': f"Top franchise: {top_product} ({top_concentration*100:.0f}% of revenue)",
                    'evidence': f"${top_revenue/1e9:.1f}B from lead franchise"
                })

    # Geographic mix - factual breakdown
    geo_revenue = financial_data.get('geographic_revenue', {})
    if geo_revenue:
        total_geo = sum(geo_revenue.values())
        if total_geo > 0:
            us_revenue = geo_revenue.get('US', 0) or geo_revenue.get('United States', 0)
            us_pct = us_revenue / total_geo if total_geo > 0 else 0
            non_us_pct = 1 - us_pct
            swot['weaknesses'].append({
                'category': 'Geographic Mix',
                'point': f"US: {us_pct*100:.0f}% | Ex-US: {non_us_pct*100:.0f}%",
                'evidence': "Revenue distribution across regions"
            })

    # Pipeline phase distribution - factual
    phase1 = phase_dist.get('Phase 1', 0) or phase_dist.get('Phase1', 0)
    total = clinical_data.get('total_trials', 0)
    if total >= 10:
        phase1_pct = phase1 / total if total > 0 else 0
        phase3_pct = phase3 / total if total > 0 else 0
        swot['weaknesses'].append({
            'category': 'Pipeline Distribution',
            'point': f"Phase 1: {phase1_pct*100:.0f}% | Phase 3: {phase3_pct*100:.0f}%",
            'evidence': f"{phase1} early-stage, {phase3} late-stage of {total} total trials"
        })

    # Patent expiry timeline - factual
    patent_info = fda_data.get('patent_data', {}) or {}
    earliest_expiries = patent_info.get('earliest_expiry', {})
    if earliest_expiries:
        expiry_list = []
        for product, expiry_date in list(earliest_expiries.items())[:3]:
            if expiry_date:
                expiry_list.append(f"{product} ({str(expiry_date)[:7]})")
        if expiry_list:
            swot['weaknesses'].append({
                'category': 'Patent Timeline',
                'point': f"Upcoming expiries: {', '.join(expiry_list)}",
                'evidence': "Loss of exclusivity dates from Orange Book"
            })

    # Peer landscape - factual
    peer_data = peer_data or {}
    peers = peer_data.get('peers', [])
    if peers:
        peer_names = [p.get('name') or p.get('ticker') for p in peers[:5]]
        swot['weaknesses'].append({
            'category': 'Competitive Landscape',
            'point': f"Key peers: {', '.join(peer_names)}",
            'evidence': f"{len(peers)} comparable companies identified"
        })

    # =========================================================================
    # OPPORTUNITIES - Growth potential
    # =========================================================================

    # Notable late-stage trials (named)
    notable = clinical_data.get('notable_trials', [])
    if notable:
        trials_str = ', '.join(f"{t['acronym']}" for t in notable[:3])
        conditions = list(set(t.get('condition', '')[:30] for t in notable[:3] if t.get('condition')))
        swot['opportunities'].append({
            'category': 'Near-term Catalysts',
            'point': f"Phase 3 readouts expected: {trials_str}",
            'evidence': f"Indications: {', '.join(conditions)}" if conditions else "Multiple Phase 3 trials"
        })

    # Pipeline expansion areas
    drugs_by_phase = clinical_data.get('drugs_by_phase', {})
    phase1_drugs = drugs_by_phase.get('Phase 1', []) or drugs_by_phase.get('Phase1', [])
    phase2_drugs = drugs_by_phase.get('Phase 2', []) or drugs_by_phase.get('Phase2', [])

    early_pipeline = list(set(phase1_drugs + phase2_drugs))[:5]
    if early_pipeline:
        swot['opportunities'].append({
            'category': 'Pipeline Expansion',
            'point': f"Early-stage candidates: {', '.join(early_pipeline)}",
            'evidence': f"Phase 1-2 development across {len(early_pipeline)} programs"
        })

    # Therapeutic area expansion
    therapeutic_areas = clinical_data.get('therapeutic_areas', {})
    # Filter out noise
    exclude = {'Healthy', 'Healthy Volunteers', 'Normal', 'Adult', 'Child'}
    filtered_areas = [k for k in therapeutic_areas.keys() if k not in exclude and not k.startswith('Healthy')]
    if len(filtered_areas) > 3:
        swot['opportunities'].append({
            'category': 'Market Diversification',
            'point': f"Active in {len(filtered_areas)} therapeutic areas",
            'evidence': f"Top areas: {', '.join(filtered_areas[:3])}"
        })

    # Revenue growth momentum
    revenue_data = financial_data.get('revenue', {})
    if revenue_data.get('yoy_growth') and revenue_data['yoy_growth'] > 0.1:  # >10% growth
        swot['opportunities'].append({
            'category': 'Growth Momentum',
            'point': f"Strong revenue growth trajectory (+{revenue_data['yoy_growth']*100:.0f}% YoY)",
            'evidence': "Commercial execution supporting pipeline investments"
        })

    # M&A / Strategic optionality - profitable companies have deal-making capacity
    net_income = financial_data.get('net_income', {})
    net_income_current = net_income.get('current') if isinstance(net_income, dict) else net_income
    if net_income_current and net_income_current > 0:
        net_income_m = net_income_current / 1e6
        swot['opportunities'].append({
            'category': 'Strategic Optionality',
            'point': "Profitability enables M&A and partnership opportunities",
            'evidence': f"Net income ${net_income_m:.0f}M provides capacity for strategic deals"
        })

    # Cash position opportunity (for cash-rich companies without pipeline data)
    cash_data = financial_data.get('cash', {})
    cash_current_opp = cash_data.get('current', 0) if isinstance(cash_data, dict) else 0
    if cash_current_opp > 1e9 and not swot['opportunities']:
        swot['opportunities'].append({
            'category': 'Financial Capacity',
            'point': f"Strong cash position (${cash_current_opp/1e9:.1f}B) enables strategic investments",
            'evidence': "Capital available for in-licensing, partnerships, or acquisitions"
        })

    # Market cap opportunity (large enough to attract partnerships)
    if market_data.get('market_cap') and market_data['market_cap'] > 10e9 and not swot['opportunities']:
        cap_b = market_data['market_cap'] / 1e9
        swot['opportunities'].append({
            'category': 'Platform Value',
            'point': f"${cap_b:.0f}B market cap provides platform for strategic growth",
            'evidence': "Scale supports business development and partnership leverage"
        })

    # Ensure at least 1 opportunity exists (financial fallback)
    if not swot['opportunities'] and actual_revenue > 0:
        swot['opportunities'].append({
            'category': 'Revenue Base',
            'point': f"Established revenue base (${actual_revenue/1e9:.1f}B) supports expansion",
            'evidence': "Commercial infrastructure in place for pipeline advancement"
        })

    # Pipeline-based opportunity fallback for pre-revenue/clinical-stage companies
    # When no financial data is available, active trials ARE the opportunity
    total_trials = clinical_data.get('total_trials', 0)
    if not swot['opportunities'] and total_trials > 0:
        lead_drugs = clinical_data.get('lead_drugs', [])
        lead_names = [d['name'] for d in lead_drugs[:3] if isinstance(d, dict)] if lead_drugs else []
        lead_str = f" ({', '.join(lead_names)})" if lead_names else ""
        swot['opportunities'].append({
            'category': 'Clinical Development',
            'point': f"Active clinical pipeline with {total_trials} trials{lead_str}",
            'evidence': f"Pipeline advancement across {len(filtered_areas)} therapeutic areas represents near-term value creation"
        })

    # =========================================================================
    # THREATS - External risks
    # =========================================================================

    # Competition in key therapeutic areas
    # Always add a competitive threat if they have clinical programs
    if filtered_areas:
        top_area = filtered_areas[0]
        area_trials = therapeutic_areas.get(top_area, 0)
        # Shorten long indication names
        top_area_short = top_area[:50] + '...' if len(top_area) > 50 else top_area
        swot['threats'].append({
            'category': 'Competitive Landscape',
            'point': f"Competition in key markets ({top_area_short})",
            'evidence': f"Active in competitive oncology/specialty pharma space with {len(filtered_areas)} indications"
        })

    # Revenue concentration risk - if top product > 50% of total
    if segment_revenue:
        total_seg_rev = sum(segment_revenue.values())
        top_product_rev = list(segment_revenue.values())[0] if segment_revenue else 0
        if total_seg_rev > 0 and top_product_rev / total_seg_rev > 0.5:
            top_product_name = list(segment_revenue.keys())[0]
            concentration_pct = (top_product_rev / total_seg_rev) * 100
            swot['threats'].append({
                'category': 'Revenue Concentration',
                'point': f"{top_product_name} represents {concentration_pct:.0f}% of product revenue",
                'evidence': "High dependence on single asset increases business risk"
            })

    # Generic/biosimilar exposure - for any company with commercial products
    # Now with ACTUAL patent dates from Orange Book
    fda_products = fda_data.get('total_products', 0)
    patent_data = fda_data.get('patent_data', {})
    products_expiring_soon = patent_data.get('products_expiring_soon', [])
    earliest_loe = patent_data.get('earliest_loe')
    products_with_patents = patent_data.get('products_with_patents', {})

    if fda_products >= 1:
        # Get product names for more specific threat
        product_names = fda_data.get('product_names', [])[:3]
        products_str = ', '.join(product_names) if product_names else 'approved products'

        # If we have actual patent data, use it for specific LOE threats
        if products_expiring_soon and earliest_loe:
            # Parse earliest LOE date for display
            try:
                from datetime import datetime
                loe_date = datetime.strptime(earliest_loe, '%Y-%m-%d')
                loe_str = loe_date.strftime('%b %Y')
                years_until_loe = (loe_date - datetime.now()).days / 365

                # Product(s) expiring within 3 years - specific threat
                expiring_str = ', '.join(products_expiring_soon[:3])
                swot['threats'].append({
                    'category': 'Near-Term Patent Cliff',
                    'point': f"LOE risk: {expiring_str} - patents expire {loe_str}",
                    'evidence': f"{len(products_expiring_soon)} product(s) face generic/biosimilar competition within 3 years"
                })
            except Exception:
                pass
        elif products_with_patents and earliest_loe:
            # Have patent data but no imminent expirations - show overall LOE timeline
            try:
                from datetime import datetime
                loe_date = datetime.strptime(earliest_loe, '%Y-%m-%d')
                loe_str = loe_date.strftime('%b %Y')

                # Get product with earliest expiry
                earliest_product = None
                for prod, info in products_with_patents.items():
                    if info.get('earliest_expiry') == earliest_loe:
                        earliest_product = prod
                        break

                swot['threats'].append({
                    'category': 'Patent/LOE Risk',
                    'point': f"Earliest patent expiry: {earliest_product or 'key product'} ({loe_str})",
                    'evidence': f"{len(products_with_patents)} products with Orange Book patent data"
                })
            except Exception:
                pass
        elif fda_products >= 10:
            # No Orange Book data (likely biologics) - generic message for large portfolio
            swot['threats'].append({
                'category': 'Patent Exposure',
                'point': "Large portfolio with potential patent cliff exposure",
                'evidence': f"{fda_products} approved products (biologics may have BLA protection)"
            })
        else:
            # Small portfolio, no patent data
            swot['threats'].append({
                'category': 'Patent/LOE Risk',
                'point': f"Key products face eventual loss of exclusivity",
                'evidence': f"Products: {products_str} (patent data unavailable - may be biologics)"
            })

    # Negative income trend
    net_income = financial_data.get('net_income', {})
    if net_income.get('yoy_growth') and net_income['yoy_growth'] < -0.2:  # >20% decline
        swot['threats'].append({
            'category': 'Profitability Pressure',
            'point': f"Net income declined {abs(net_income['yoy_growth'])*100:.0f}% YoY",
            'evidence': "May impact R&D investment capacity"
        })

    # Market cap concerns (small cap = vulnerability)
    if market_data.get('market_cap') and market_data['market_cap'] < 5e9:
        cap_b = market_data['market_cap'] / 1e9
        swot['threats'].append({
            'category': 'Capital Access',
            'point': f"Smaller market cap (${cap_b:.1f}B) limits financial flexibility",
            'evidence': "May face challenges funding late-stage development"
        })

    # Clinical trial failure risk - high early-stage concentration
    phase_dist = clinical_data.get('phase_distribution', {})
    total_trials = sum(phase_dist.values()) if phase_dist else 0
    phase1_count = phase_dist.get('Phase 1', 0) or phase_dist.get('Phase1', 0)
    if total_trials >= 3 and phase1_count > 0:
        phase1_pct = (phase1_count / total_trials) * 100
        if phase1_pct >= 60:  # More than 60% in Phase 1
            swot['threats'].append({
                'category': 'Clinical Development Risk',
                'point': f"High early-stage concentration ({phase1_pct:.0f}% Phase 1)",
                'evidence': f"{phase1_count} of {total_trials} trials in Phase 1 - historically ~90% attrition rate"
            })

    # Ensure at least 1 threat exists (industry-level fallback)
    if not swot['threats']:
        # Pharma industry pricing pressure is always relevant
        swot['threats'].append({
            'category': 'Industry Headwinds',
            'point': "Pharmaceutical sector faces ongoing pricing and regulatory pressure",
            'evidence': "IRA drug pricing provisions, global reference pricing trends, and payer consolidation"
        })

    # Empty SWOT guard: when all quadrants are nearly empty, flag insufficient data
    total_points = sum(len(v) for v in swot.values())
    if total_points <= 1:
        swot['_insufficient_data'] = True
        company_str = f" for {company_name}" if company_name else ""
        print(f"   Warning: Insufficient data{company_str} — SWOT analysis may be unreliable")

    return swot
