#!/usr/bin/env python3
"""Drug switching analysis module.

Provides market share analysis, proxy switching estimation, and competitive
dynamics for drug classes using Medicare Part D spending data.
"""

import sys
import os
from typing import Dict, Any, Optional, List
from collections import defaultdict

# Path setup for imports
_this_file = os.path.abspath(__file__)
_scripts_dir = os.path.dirname(_this_file)
_skill_dir = os.path.dirname(_scripts_dir)
_skills_dir = os.path.dirname(_skill_dir)
_claude_dir = os.path.dirname(_skills_dir)

sys.path.insert(0, _claude_dir)
sys.path.insert(0, _scripts_dir)

# All MCP functions are now accessed via mcp_funcs parameter
# No direct imports from mcp.servers.* allowed

from constants import (
    get_competitive_set,
    get_competitors,
    COMPETITIVE_SETS,
    format_currency,
    format_number,
)


def analyze_market_share(
    drug_name: str,
    years: Optional[List[int]] = None,
    verbose: bool = False,
    mcp_funcs: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Analyze market share for a drug within its competitive set.

    Args:
        drug_name: Brand or generic drug name
        years: Specific years to analyze (default: all available)
        verbose: Print progress messages
        mcp_funcs: Dictionary of MCP functions

    Returns:
        dict: Market share analysis with trends
    """
    if not mcp_funcs:
        return {
            "drug_name": drug_name,
            "competitive_set": None,
            "market_share_by_year": {},
            "has_data": False,
        }

    search_spending = mcp_funcs.get('medicare_spending')
    if not search_spending:
        return {
            "drug_name": drug_name,
            "competitive_set": None,
            "market_share_by_year": {},
            "has_data": False,
        }

    result = {
        "drug_name": drug_name,
        "competitive_set": None,
        "market_share_by_year": {},
        "share_change": {},
        "class_totals_by_year": {},
        "drug_data_by_year": {},
        "competitors": [],
        "has_data": False,
    }

    # Get competitive set
    comp_set = get_competitive_set(drug_name)
    if not comp_set:
        if verbose:
            print(f"  No competitive set found for {drug_name}")
        return result

    result["competitive_set"] = {
        "name": comp_set["name"],
        "set_id": comp_set["set_id"],
        "therapeutic_class": comp_set["therapeutic_class"],
    }

    if verbose:
        print(f"\n  Competitive Set: {comp_set['name']}")
        print(f"  Drugs in class: {len(comp_set['drugs'])}")

    # Collect spending data for all drugs in competitive set
    all_drug_data = {}  # brand -> {year: {spending, beneficiaries, claims}}

    for drug_info in comp_set["drugs"]:
        brand = drug_info["brand"]
        try:
            spending_result = search_spending(
                spending_drug_name=brand,
                spending_type="part_d",
                size=10
            )

            if spending_result and "drugs" in spending_result:
                # Find "Overall" record (excludes manufacturer duplicates)
                for drug_record in spending_result["drugs"]:
                    if drug_record.get("manufacturer") == "Overall":
                        year_data = drug_record.get("spending_by_year", {})
                        if year_data:
                            all_drug_data[brand] = {}
                            for year_str, data in year_data.items():
                                year = int(year_str)
                                all_drug_data[brand][year] = {
                                    "spending": float(data.get("total_spending", 0) or 0),
                                    "beneficiaries": int(float(data.get("total_beneficiaries", 0) or 0)),
                                    "claims": int(float(data.get("total_claims", 0) or 0)),
                                }
                        break

            if verbose and brand in all_drug_data:
                years_found = list(all_drug_data[brand].keys())
                print(f"    {brand}: {len(years_found)} years of data")

        except Exception as e:
            if verbose:
                print(f"    {brand}: Error - {e}")
            continue

    if not all_drug_data:
        if verbose:
            print("  No spending data found for any drugs in class")
        return result

    # Determine years to analyze
    all_years = set()
    for drug_data in all_drug_data.values():
        all_years.update(drug_data.keys())

    if years:
        all_years = all_years.intersection(set(years))

    all_years = sorted(all_years)

    if not all_years:
        return result

    # Calculate market share by year
    for year in all_years:
        # Calculate class totals
        class_spending = 0
        class_beneficiaries = 0
        class_claims = 0

        for brand, year_data in all_drug_data.items():
            if year in year_data:
                class_spending += year_data[year]["spending"]
                class_beneficiaries += year_data[year]["beneficiaries"]
                class_claims += year_data[year]["claims"]

        result["class_totals_by_year"][year] = {
            "total_spending": class_spending,
            "total_beneficiaries": class_beneficiaries,
            "total_claims": class_claims,
        }

        # Calculate market share for each drug
        result["market_share_by_year"][year] = {}
        for brand, year_data in all_drug_data.items():
            if year in year_data:
                drug_spending = year_data[year]["spending"]
                drug_bene = year_data[year]["beneficiaries"]

                spending_share = (drug_spending / class_spending * 100) if class_spending > 0 else 0
                bene_share = (drug_bene / class_beneficiaries * 100) if class_beneficiaries > 0 else 0

                result["market_share_by_year"][year][brand] = {
                    "spending_share": spending_share,
                    "beneficiary_share": bene_share,
                    "spending": drug_spending,
                    "beneficiaries": drug_bene,
                }

    # Store raw drug data for downstream analysis
    result["drug_data_by_year"] = all_drug_data

    # Calculate share change (first year to last year)
    if len(all_years) >= 2:
        first_year = all_years[0]
        last_year = all_years[-1]

        for brand in all_drug_data.keys():
            first_share = result["market_share_by_year"].get(first_year, {}).get(brand, {}).get("beneficiary_share", 0)
            last_share = result["market_share_by_year"].get(last_year, {}).get(brand, {}).get("beneficiary_share", 0)

            result["share_change"][brand] = {
                "from_year": first_year,
                "to_year": last_year,
                "share_change_pp": last_share - first_share,  # Percentage points
                "direction": "gaining" if last_share > first_share else "losing" if last_share < first_share else "stable",
            }

    # List competitors
    result["competitors"] = [brand for brand in all_drug_data.keys() if brand.lower() != drug_name.lower()]
    result["has_data"] = True

    return result


def estimate_switching_patterns(
    market_share_data: Dict[str, Any],
    target_drug: str,
    verbose: bool = False
) -> Dict[str, Any]:
    """Estimate switching patterns from market share changes.

    Uses net flow analysis: if a drug grows faster than the class,
    it's gaining share from competitors (likely switches + new patients).

    Args:
        market_share_data: Output from analyze_market_share()
        target_drug: The drug we're analyzing
        verbose: Print progress messages

    Returns:
        dict: Estimated switching patterns
    """
    result = {
        "target_drug": target_drug,
        "estimated_net_switches": {},
        "class_growth_rate": None,
        "drug_growth_rates": {},
        "switching_direction": {},
        "methodology": "Net flow analysis comparing individual drug growth vs class growth",
        "confidence": "Medium - proxy estimate based on aggregate data, not patient-level tracking",
        "has_data": False,
    }

    if not market_share_data.get("has_data"):
        return result

    drug_data = market_share_data.get("drug_data_by_year", {})
    class_totals = market_share_data.get("class_totals_by_year", {})

    if not drug_data or not class_totals:
        return result

    years = sorted(class_totals.keys())
    if len(years) < 2:
        return result

    # Calculate year-over-year changes
    for i in range(1, len(years)):
        prev_year = years[i - 1]
        curr_year = years[i]

        # Class growth rate
        prev_class_bene = class_totals[prev_year]["total_beneficiaries"]
        curr_class_bene = class_totals[curr_year]["total_beneficiaries"]

        if prev_class_bene > 0:
            class_growth = (curr_class_bene - prev_class_bene) / prev_class_bene * 100
        else:
            class_growth = 0

        result["class_growth_rate"] = {
            "from_year": prev_year,
            "to_year": curr_year,
            "growth_pct": class_growth,
            "absolute_growth": curr_class_bene - prev_class_bene,
        }

        # Individual drug growth rates
        for brand, brand_data in drug_data.items():
            if prev_year in brand_data and curr_year in brand_data:
                prev_bene = brand_data[prev_year]["beneficiaries"]
                curr_bene = brand_data[curr_year]["beneficiaries"]

                if prev_bene > 0:
                    drug_growth = (curr_bene - prev_bene) / prev_bene * 100
                else:
                    # Use a large number instead of infinity for JSON serialization
                    drug_growth = 99999.0 if curr_bene > 0 else 0

                result["drug_growth_rates"][brand] = {
                    "from_year": prev_year,
                    "to_year": curr_year,
                    "growth_pct": drug_growth,
                    "absolute_growth": curr_bene - prev_bene,
                    "prev_beneficiaries": prev_bene,
                    "curr_beneficiaries": curr_bene,
                }

                # Estimate net switching
                # If drug grew faster than class, it gained "extra" patients
                # These could be switchers + organic growth differential
                if class_growth > 0 and prev_bene > 0:
                    expected_growth = prev_bene * (class_growth / 100)
                    actual_growth = curr_bene - prev_bene
                    net_switch_estimate = actual_growth - expected_growth

                    result["estimated_net_switches"][brand] = {
                        "expected_if_class_avg": int(expected_growth),
                        "actual_growth": int(actual_growth),
                        "net_switch_estimate": int(net_switch_estimate),
                        "interpretation": "gained from competitors" if net_switch_estimate > 0 else "lost to competitors",
                    }

                    result["switching_direction"][brand] = "inflow" if net_switch_estimate > 0 else "outflow"

    result["has_data"] = True

    if verbose:
        print(f"\n  Switching Analysis ({result['class_growth_rate']['from_year']}-{result['class_growth_rate']['to_year']}):")
        print(f"    Class growth: {result['class_growth_rate']['growth_pct']:.1f}%")
        for brand, data in result["estimated_net_switches"].items():
            direction = "+" if data["net_switch_estimate"] > 0 else ""
            print(f"    {brand}: {direction}{data['net_switch_estimate']:,} ({data['interpretation']})")

    return result


def analyze_geographic_switching(
    drug_a: str,
    drug_b: str,
    verbose: bool = False,
    mcp_funcs: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Analyze geographic correlation between two drugs.

    If Drug B gains where Drug A loses (negative correlation), suggests switching.

    Args:
        drug_a: First drug (typically older/losing share)
        drug_b: Second drug (typically newer/gaining share)
        verbose: Print progress messages
        mcp_funcs: Dictionary of MCP functions

    Returns:
        dict: Geographic correlation analysis
    """
    result = {
        "drug_a": drug_a,
        "drug_b": drug_b,
        "state_data": {},
        "correlation_coefficient": None,
        "interpretation": None,
        "top_switching_states": [],
        "has_data": False,
    }

    if not mcp_funcs:
        return result

    search_prescribers = mcp_funcs.get('medicare_prescribers')
    if not search_prescribers:
        return result

    if verbose:
        print(f"\n  Analyzing geographic patterns: {drug_a} vs {drug_b}")

    # Get state-level prescriber data for both drugs
    try:
        drug_a_result = search_prescribers(drug_name=drug_a, size=2000)
        drug_b_result = search_prescribers(drug_name=drug_b, size=2000)
    except Exception as e:
        if verbose:
            print(f"    Error fetching prescriber data: {e}")
        return result

    # Aggregate by state
    def aggregate_by_state(prescriber_result):
        state_totals = defaultdict(lambda: {"claims": 0, "spending": 0, "beneficiaries": 0})
        records = []
        if prescriber_result and "prescribers" in prescriber_result:
            records = prescriber_result.get("prescribers", [])

        for record in records:
            state = record.get("state", "")
            if not state or len(state) != 2:
                continue

            claims = int(float(record.get("total_claims", 0) or 0))
            spending = float(record.get("total_drug_cost", 0) or 0)
            bene = int(float(record.get("total_beneficiaries", 0) or 0))

            state_totals[state]["claims"] += claims
            state_totals[state]["spending"] += spending
            state_totals[state]["beneficiaries"] += bene

        return dict(state_totals)

    state_a = aggregate_by_state(drug_a_result)
    state_b = aggregate_by_state(drug_b_result)

    # Find common states
    common_states = set(state_a.keys()) & set(state_b.keys())

    if len(common_states) < 5:
        if verbose:
            print(f"    Insufficient state overlap ({len(common_states)} states)")
        return result

    # Calculate per-state share ratio
    # Higher ratio = more Drug B relative to Drug A
    for state in common_states:
        a_claims = state_a[state]["claims"]
        b_claims = state_b[state]["claims"]

        if a_claims > 0:
            ratio = b_claims / a_claims
        else:
            # Use a large number instead of infinity for JSON serialization
            ratio = 999999.0 if b_claims > 0 else 0

        result["state_data"][state] = {
            "drug_a_claims": a_claims,
            "drug_b_claims": b_claims,
            "ratio_b_to_a": ratio,
        }

    # Sort states by ratio (highest = most switching to Drug B)
    sorted_states = sorted(
        result["state_data"].items(),
        key=lambda x: x[1]["ratio_b_to_a"] if x[1]["ratio_b_to_a"] < 999999 else 999999,
        reverse=True
    )

    result["top_switching_states"] = [
        {"state": state, **data}
        for state, data in sorted_states[:10]
        if data["ratio_b_to_a"] < 999999
    ]

    # Calculate simple correlation (claims Drug A vs claims Drug B)
    # Negative correlation would suggest substitution
    a_values = [state_a[s]["claims"] for s in common_states]
    b_values = [state_b[s]["claims"] for s in common_states]

    # Pearson correlation
    n = len(a_values)
    if n > 2:
        mean_a = sum(a_values) / n
        mean_b = sum(b_values) / n

        numerator = sum((a - mean_a) * (b - mean_b) for a, b in zip(a_values, b_values))
        denom_a = sum((a - mean_a) ** 2 for a in a_values) ** 0.5
        denom_b = sum((b - mean_b) ** 2 for b in b_values) ** 0.5

        if denom_a > 0 and denom_b > 0:
            correlation = numerator / (denom_a * denom_b)
            result["correlation_coefficient"] = round(correlation, 3)

            # Interpretation
            if correlation < -0.5:
                result["interpretation"] = "Strong negative correlation - suggests substitution/switching"
            elif correlation < -0.2:
                result["interpretation"] = "Moderate negative correlation - some evidence of switching"
            elif correlation < 0.2:
                result["interpretation"] = "Weak correlation - inconclusive"
            elif correlation < 0.5:
                result["interpretation"] = "Moderate positive correlation - drugs may serve different populations"
            else:
                result["interpretation"] = "Strong positive correlation - both growing in same markets"

    result["has_data"] = True

    if verbose and result["correlation_coefficient"] is not None:
        print(f"    Correlation: {result['correlation_coefficient']:.3f}")
        print(f"    {result['interpretation']}")

    return result


def search_switching_studies(
    drug_name: str,
    limit: int = 10,
    verbose: bool = False,
    mcp_funcs: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Search PubMed for published switching studies.

    Args:
        drug_name: Drug name to search for
        limit: Maximum number of results
        verbose: Print progress messages
        mcp_funcs: Dictionary of MCP functions

    Returns:
        dict: Published switching studies
    """
    result = {
        "drug_name": drug_name,
        "studies": [],
        "total_found": 0,
        "has_data": False,
    }

    if not mcp_funcs:
        return result

    pubmed_search = mcp_funcs.get('pubmed_search')
    if not pubmed_search:
        return result

    # Build search query for switching/discontinuation studies
    search_terms = [
        f'("{drug_name}" AND (switching OR discontinuation OR "treatment change"))',
        f'("{drug_name}" AND "real-world" AND (claims OR database))',
    ]

    if verbose:
        print(f"\n  Searching PubMed for {drug_name} switching studies...")

    try:
        for query in search_terms:
            pubmed_result = pubmed_search(keywords=query, num_results=limit)

            if pubmed_result:
                for article in pubmed_result:
                    # Check if it's actually about switching
                    title = article.get("title", "").lower()
                    abstract = article.get("abstract", "").lower()

                    switching_keywords = ["switch", "discontinu", "treatment change", "transition"]
                    is_switching_study = any(kw in title or kw in abstract for kw in switching_keywords)

                    if is_switching_study:
                        result["studies"].append({
                            "pmid": article.get("pmid"),
                            "title": article.get("title"),
                            "journal": article.get("journal"),
                            "publication_date": article.get("publication_date"),
                            "abstract": article.get("abstract", "")[:500] + "..." if len(article.get("abstract", "")) > 500 else article.get("abstract", ""),
                            "url": article.get("url"),
                        })

        # Deduplicate by PMID
        seen_pmids = set()
        unique_studies = []
        for study in result["studies"]:
            if study["pmid"] not in seen_pmids:
                seen_pmids.add(study["pmid"])
                unique_studies.append(study)

        result["studies"] = unique_studies[:limit]
        result["total_found"] = len(unique_studies)
        result["has_data"] = len(unique_studies) > 0

        if verbose:
            print(f"    Found {result['total_found']} relevant studies")
            for study in result["studies"][:3]:
                print(f"    - {study['title'][:60]}...")

    except Exception as e:
        if verbose:
            print(f"    Error searching PubMed: {e}")

    return result


def get_full_switching_analysis(
    drug_name: str,
    verbose: bool = False,
    mcp_funcs: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Get comprehensive switching analysis for a drug.

    Combines market share, net flow estimation, geographic analysis,
    and published studies.

    Args:
        drug_name: Drug name to analyze
        verbose: Print progress messages
        mcp_funcs: Dictionary of MCP functions

    Returns:
        dict: Complete switching analysis
    """
    if verbose:
        print(f"\n{'─' * 60}")
        print(f"Analyzing competitive dynamics and switching patterns...")

    result = {
        "drug_name": drug_name,
        "market_share": None,
        "switching_estimates": None,
        "geographic_analysis": None,
        "published_studies": None,
        "summary": {},
        "has_data": False,
    }

    if not mcp_funcs:
        if verbose:
            print("  No MCP functions provided")
        return result

    # 1. Market share analysis
    if verbose:
        print("\n  [1/4] Analyzing market share...")
    market_share = analyze_market_share(drug_name, verbose=verbose, mcp_funcs=mcp_funcs)
    result["market_share"] = market_share

    if not market_share.get("has_data"):
        if verbose:
            print("  No competitive set data available")
        return result

    # 2. Switching estimates
    if verbose:
        print("\n  [2/4] Estimating switching patterns...")
    switching = estimate_switching_patterns(market_share, drug_name, verbose=verbose)
    result["switching_estimates"] = switching

    # 3. Geographic analysis (compare with top competitor)
    if verbose:
        print("\n  [3/4] Analyzing geographic patterns...")

    competitors = market_share.get("competitors", [])
    if competitors:
        # Find the main competitor (highest share change in opposite direction)
        share_changes = market_share.get("share_change", {})
        target_direction = share_changes.get(drug_name, {}).get("direction", "stable")

        main_competitor = None
        for comp in competitors:
            comp_direction = share_changes.get(comp, {}).get("direction", "stable")
            if target_direction == "gaining" and comp_direction == "losing":
                main_competitor = comp
                break
            elif target_direction == "losing" and comp_direction == "gaining":
                main_competitor = comp
                break

        if not main_competitor:
            main_competitor = competitors[0]

        geo_analysis = analyze_geographic_switching(
            drug_a=main_competitor if target_direction == "gaining" else drug_name,
            drug_b=drug_name if target_direction == "gaining" else main_competitor,
            verbose=verbose,
            mcp_funcs=mcp_funcs
        )
        result["geographic_analysis"] = geo_analysis

    # 4. Published studies
    if verbose:
        print("\n  [4/4] Searching published switching studies...")
    studies = search_switching_studies(drug_name, limit=5, verbose=verbose, mcp_funcs=mcp_funcs)
    result["published_studies"] = studies

    # Build summary
    result["summary"] = _build_switching_summary(result, drug_name)
    result["has_data"] = True

    return result


def _build_switching_summary(analysis: Dict[str, Any], drug_name: str) -> Dict[str, Any]:
    """Build a summary of the switching analysis."""
    summary = {
        "competitive_position": "Unknown",
        "market_share_trend": "Unknown",
        "estimated_net_switch": 0,
        "main_competitor": None,
        "published_evidence": False,
        "key_insights": [],
    }

    # Market share trend
    market_share = analysis.get("market_share", {})
    share_change = market_share.get("share_change", {})

    drug_name_upper = drug_name.title()
    for brand, change in share_change.items():
        if brand.lower() == drug_name.lower() or brand.title() == drug_name_upper:
            summary["market_share_trend"] = change.get("direction", "Unknown")
            pp_change = change.get("share_change_pp", 0)
            summary["key_insights"].append(
                f"Market share {'increased' if pp_change > 0 else 'decreased'} by {abs(pp_change):.1f} percentage points"
            )
            break

    # Competitive position
    if summary["market_share_trend"] == "gaining":
        summary["competitive_position"] = "Growing - capturing market share"
    elif summary["market_share_trend"] == "losing":
        summary["competitive_position"] = "Declining - losing to competitors"
    else:
        summary["competitive_position"] = "Stable - maintaining position"

    # Net switch estimate
    switching = analysis.get("switching_estimates", {})
    net_switches = switching.get("estimated_net_switches", {})
    for brand, data in net_switches.items():
        if brand.lower() == drug_name.lower():
            summary["estimated_net_switch"] = data.get("net_switch_estimate", 0)
            if summary["estimated_net_switch"] > 0:
                summary["key_insights"].append(
                    f"Estimated ~{format_number(summary['estimated_net_switch'])} patients gained from competitors"
                )
            elif summary["estimated_net_switch"] < 0:
                summary["key_insights"].append(
                    f"Estimated ~{format_number(abs(summary['estimated_net_switch']))} patients lost to competitors"
                )
            break

    # Main competitor
    competitors = market_share.get("competitors", [])
    if competitors:
        # Find biggest gainer/loser depending on target drug's direction
        if summary["market_share_trend"] == "gaining":
            # Find biggest loser
            biggest_loser = None
            biggest_loss = 0
            for comp in competitors:
                change = share_change.get(comp, {}).get("share_change_pp", 0)
                if change < biggest_loss:
                    biggest_loss = change
                    biggest_loser = comp
            summary["main_competitor"] = biggest_loser
            if biggest_loser:
                summary["key_insights"].append(
                    f"Primary share donor: {biggest_loser} ({biggest_loss:+.1f}pp)"
                )
        else:
            # Find biggest gainer
            biggest_gainer = None
            biggest_gain = 0
            for comp in competitors:
                change = share_change.get(comp, {}).get("share_change_pp", 0)
                if change > biggest_gain:
                    biggest_gain = change
                    biggest_gainer = comp
            summary["main_competitor"] = biggest_gainer
            if biggest_gainer:
                summary["key_insights"].append(
                    f"Primary share winner: {biggest_gainer} ({biggest_gain:+.1f}pp)"
                )

    # Published evidence
    studies = analysis.get("published_studies", {})
    if studies.get("has_data"):
        summary["published_evidence"] = True
        summary["key_insights"].append(
            f"Found {studies.get('total_found', 0)} published switching studies"
        )

    return summary


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python3 switching_analysis.py <DRUG_NAME>")
        print("\nExamples:")
        print("  python3 switching_analysis.py Ozempic")
        print("  python3 switching_analysis.py semaglutide")
        sys.exit(1)

    drug = sys.argv[1]
    print(f"\n{'=' * 60}")
    print(f"SWITCHING ANALYSIS: {drug.upper()}")
    print(f"{'=' * 60}")

    result = get_full_switching_analysis(drug, verbose=True)

    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")

    summary = result.get("summary", {})
    print(f"Competitive Position: {summary.get('competitive_position')}")
    print(f"Market Share Trend: {summary.get('market_share_trend')}")
    print(f"Estimated Net Switch: {format_number(summary.get('estimated_net_switch', 0))} patients")

    print("\nKey Insights:")
    for insight in summary.get("key_insights", []):
        print(f"  • {insight}")
