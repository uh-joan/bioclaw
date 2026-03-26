"""Market sizing module for drug sales forecasting.

Estimates market size using:
- Disease prevalence from CDC
- Drug utilization from Medicare/Medicaid
- Pricing data from NADAC and Medicare Part D
"""

import sys
import os

# Add parent directories to path for imports
_script_dir = os.path.dirname(os.path.abspath(__file__))
_claude_dir = os.path.dirname(os.path.dirname(os.path.dirname(_script_dir)))
sys.path.insert(0, _claude_dir)

from typing import Dict, Any, Optional, List, Tuple

# Import segment revenue function from comparable_drugs
try:
    from .comparable_drugs import get_manufacturer_segment_revenue
except ImportError:
    # Direct import for standalone testing
    from comparable_drugs import get_manufacturer_segment_revenue


# ============================================================================
# Dynamic Population & Prevalence Lookup (Data Commons + WHO)
# No hardcoded mappings - uses search APIs to discover indicators dynamically
# ============================================================================


def _parse_dc_observations(result: Dict) -> Tuple[Any, str]:
    """
    Parse Data Commons observation response format.

    Data Commons returns: {place_observations: [{time_series: [[date, value], ...]}]}

    Returns:
        tuple: (latest_value, year) or (None, None)
    """
    place_obs = result.get('place_observations', [])
    if not place_obs:
        return None, None

    time_series = place_obs[0].get('time_series', [])
    if not time_series:
        return None, None

    # Time series is sorted newest first: [[date, value], ...]
    latest = time_series[0]
    if len(latest) >= 2:
        return latest[1], str(latest[0])

    return None, None


def get_us_adult_population(mcp_funcs: Dict[str, Any] = None) -> Tuple[int, str]:
    """
    Get current US adult population from Data Commons.

    Returns:
        tuple: (population_count, data_year) or (None, None) if unavailable
    """
    if not mcp_funcs:
        return None, None

    dc_get_observations = mcp_funcs.get('datacommons_observations')
    if not dc_get_observations:
        return None, None

    try:
        # Use Data Commons to get US adult population (18+)
        result = dc_get_observations(
            variable_dcid='Count_Person_18OrMoreYears',
            place_dcid='country/USA',
            date='latest'
        )

        pop, year = _parse_dc_observations(result)
        if pop:
            return int(float(pop)), year

    except Exception as e:
        print(f"    Note: Data Commons adult population lookup failed: {e}")

    # Fallback: try total population
    try:
        result = dc_get_observations(
            variable_dcid='Count_Person',
            place_dcid='country/USA',
            date='latest'
        )

        pop, year = _parse_dc_observations(result)
        if pop:
            # Estimate adult population as ~77% of total (US demographics)
            adult_pop = int(float(pop) * 0.77)
            return adult_pop, f"{year} (est. adult)"

    except Exception as e:
        print(f"    Note: Data Commons total population lookup failed: {e}")

    return None, None


def get_disease_prevalence_datacommons(indication: str, mcp_funcs: Dict[str, Any] = None) -> Tuple[float, str, str]:
    """
    Get disease prevalence from Data Commons using dynamic search.

    No hardcoded mappings - discovers indicators via search API.

    Args:
        indication: Disease/condition name
        mcp_funcs: MCP function dictionary

    Returns:
        tuple: (prevalence_pct, data_year, variable_used) or (None, None, None)
    """
    if not mcp_funcs:
        return None, None, None

    dc_search = mcp_funcs.get('datacommons_search')
    dc_get_observations = mcp_funcs.get('datacommons_observations')
    if not dc_search or not dc_get_observations:
        return None, None, None

    # Build search queries to try (most specific first)
    search_queries = [
        f"{indication} prevalence",
        f"{indication}",
        f"percent {indication}",
    ]

    # Extract key terms for matching
    indication_lower = indication.lower()
    key_terms = [w for w in indication_lower.split() if len(w) > 3]

    for query in search_queries:
        try:
            search_result = dc_search(
                query=query,
                places=['United States'],
                per_search_limit=10
            )

            variables = search_result.get('variables', [])

            # Score and rank variables by relevance
            scored_vars = []
            for var in variables:
                var_dcid = var.get('dcid', '')
                var_name = var.get('name', '').lower()

                # Must be a percentage/prevalence indicator
                if not ('Percent' in var_dcid or 'percent' in var_name.lower()):
                    continue

                # Score based on relevance
                score = 0

                # Higher score for "With" pattern (indicates disease prevalence)
                if 'With' in var_dcid:
                    score += 20

                # Check if indication terms appear in variable
                for term in key_terms:
                    if term in var_dcid.lower() or term in var_name:
                        score += 10

                # Prefer Person-level indicators
                if 'Person' in var_dcid:
                    score += 5

                # Avoid screening/testing indicators
                if any(x in var_dcid.lower() for x in ['screening', 'test', 'check']):
                    score -= 10

                if score > 0:
                    scored_vars.append((score, var_dcid, var))

            # Sort by score descending
            scored_vars.sort(key=lambda x: -x[0])

            # Try top candidates
            for score, var_dcid, var in scored_vars[:5]:
                try:
                    obs_result = dc_get_observations(
                        variable_dcid=var_dcid,
                        place_dcid='country/USA',
                        date='latest'
                    )

                    prevalence, year = _parse_dc_observations(obs_result)
                    if prevalence:
                        pct = float(prevalence)
                        # Validate it's a reasonable prevalence (0-100%)
                        if 0 < pct < 100:
                            return pct, str(year), var_dcid

                except Exception:
                    continue

        except Exception as e:
            print(f"    Note: Data Commons search for '{query}' failed: {e}")
            continue

    return None, None, None


def get_global_prevalence_who(indication: str, mcp_funcs: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Get global disease prevalence from WHO using dynamic search.

    No hardcoded indicator mappings - discovers via WHO search API.

    Args:
        indication: Disease/condition name
        mcp_funcs: MCP function dictionary

    Returns:
        dict: Global prevalence data by country/region
    """
    result = {
        'global_prevalence_pct': None,
        'us_prevalence_pct': None,
        'countries_with_data': 0,
        'indicator_code': None,
        'data_year': None
    }

    if not mcp_funcs:
        return result

    who_search = mcp_funcs.get('who_search')
    who_health_data = mcp_funcs.get('who_health_data')
    if not who_search or not who_health_data:
        return result

    # Dynamic search for WHO indicators
    indicator_code = None
    indication_lower = indication.lower()
    key_terms = [w for w in indication_lower.split() if len(w) > 3]

    try:
        # Search WHO for matching indicators
        search_result = who_search(
            keywords=indication
        )

        indicators = search_result.get('indicators', [])

        # Score and rank indicators
        scored_indicators = []
        for ind in indicators:
            code = ind.get('IndicatorCode', '')
            name = ind.get('IndicatorName', '').lower()

            score = 0

            # Prefer prevalence indicators
            if 'PREVALENCE' in code.upper() or 'prevalence' in name:
                score += 30

            # NCD (non-communicable disease) indicators are good
            if 'NCD' in code.upper():
                score += 20

            # Check for indication terms
            for term in key_terms:
                if term in code.lower() or term in name:
                    score += 10

            # Avoid mortality/death indicators when looking for prevalence
            if 'MORT' in code.upper() or 'death' in name:
                score -= 15

            if score > 0:
                scored_indicators.append((score, code, ind))

        # Sort by score
        scored_indicators.sort(key=lambda x: -x[0])

        if scored_indicators:
            indicator_code = scored_indicators[0][1]

    except Exception as e:
        print(f"    Note: WHO indicator search failed: {e}")

    if not indicator_code:
        return result

    result['indicator_code'] = indicator_code

    try:
        # Get global data for the indicator
        who_data = who_health_data(
            indicator_code=indicator_code,
            top=200
        )

        observations = who_data.get('observations', who_data.get('value', []))

        if observations:
            prevalences = []
            us_prevalence = None
            latest_year = None

            for obs in observations:
                if isinstance(obs, dict):
                    value = obs.get('NumericValue', obs.get('Value'))
                    country = obs.get('SpatialDim', obs.get('COUNTRY', ''))
                    year = obs.get('TimeDim', obs.get('YEAR'))

                    if value:
                        try:
                            pct = float(value)
                            if 0 < pct < 100:
                                prevalences.append(pct)
                                if country in ('USA', 'US', 'United States'):
                                    us_prevalence = pct
                                if year:
                                    latest_year = year
                        except (ValueError, TypeError):
                            pass

            if prevalences:
                result['global_prevalence_pct'] = sum(prevalences) / len(prevalences)
                result['countries_with_data'] = len(prevalences)
                result['data_year'] = latest_year

            if us_prevalence:
                result['us_prevalence_pct'] = us_prevalence

    except Exception as e:
        print(f"    Note: WHO data fetch failed: {e}")

    return result


def calculate_dynamic_addressable_market_pct(
    indication: str,
    current_sales: float = None,
    segment_revenue: float = None,
    patient_population: int = None,
    annual_cost: float = None
) -> Tuple[float, Optional[str]]:
    """
    Calculate addressable market percentage dynamically based on available data.

    Uses current penetration when available, otherwise defaults to 10%.
    Flags potential "indication mismatch" when penetration is suspiciously low.

    Args:
        indication: Disease indication
        current_sales: Current drug sales
        segment_revenue: Manufacturer segment revenue
        patient_population: Total patient population
        annual_cost: Annual cost per patient

    Returns:
        tuple: (addressable_market_pct, warning_message or None)
    """
    warning = None

    # If we have enough data, calculate dynamically from actual market penetration
    if current_sales and patient_population and annual_cost and patient_population > 0:
        theoretical_max = patient_population * annual_cost
        if theoretical_max > 0:
            current_penetration = current_sales / theoretical_max

            # Check for indication mismatch: if penetration is < 0.1%, the indication
            # is likely too broad (e.g., "arthritis" when drug treats "rheumatoid arthritis")
            if current_penetration < 0.001:  # < 0.1%
                warning = (
                    f"INDICATION MISMATCH WARNING: Calculated penetration is only "
                    f"{current_penetration*100:.3f}%. This usually means the indication "
                    f"'{indication}' is too broad. For example, 'arthritis' (23% prevalence) "
                    f"vs 'rheumatoid arthritis' (0.5-1% prevalence). TAM estimate may be "
                    f"significantly overstated. Using default 10% addressable rate."
                )
                print(f"    ⚠ {warning}")
                return 0.10, warning

            # Use current penetration with growth headroom
            if current_penetration > 0.01:  # At least 1% penetration
                # Allow 50% growth headroom from current level
                dynamic_rate = min(current_penetration * 1.5, 0.50)
                print(f"    ✓ Dynamic addressable rate: {dynamic_rate*100:.1f}% (from current penetration {current_penetration*100:.2f}%)")
                return max(0.05, dynamic_rate), None

    # If we have segment revenue, use it to estimate addressable
    if segment_revenue and patient_population and annual_cost:
        theoretical_max = patient_population * annual_cost
        if theoretical_max > 0:
            max_from_segment = segment_revenue / theoretical_max

            # Check for indication mismatch via segment revenue too
            if max_from_segment < 0.001:  # < 0.1%
                warning = (
                    f"INDICATION MISMATCH WARNING: Segment penetration is only "
                    f"{max_from_segment*100:.3f}%. The indication '{indication}' may be "
                    f"too broad for this drug. TAM estimate may be overstated."
                )
                print(f"    ⚠ {warning}")
                return 0.10, warning

            if max_from_segment > 0.01:
                dynamic_rate = min(max_from_segment * 0.5, 0.50)  # 50% of segment max
                print(f"    ✓ Segment-based addressable rate: {dynamic_rate*100:.1f}%")
                return max(0.05, dynamic_rate), None

    # Default: 10% addressable market
    print(f"    ⚠ Using default addressable rate: 10% (insufficient data for dynamic calculation)")
    return 0.10, None


def get_drug_spending_data(drug_name: str, brand_name: str = None, mcp_funcs: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Get Medicare spending data for a drug (Part D + Part B combined).

    Part D: Retail/oral drugs (pharmacies)
    Part B: Infusion/injectable drugs (administered in doctor offices/hospitals)

    Many biologics (Keytruda, Opdivo, Herceptin) are Part B drugs.
    This function checks BOTH and uses the higher value or combines them.

    Note: Medicare API works best with BRAND names (Ozempic, Humira, Lipitor)
    rather than generic names (semaglutide, adalimumab, atorvastatin).

    Args:
        drug_name: Drug name (brand or generic)
        brand_name: Optional brand name override (recommended for better results)
        mcp_funcs: MCP function dictionary

    Returns:
        dict: Spending data including total spend, beneficiaries, cost per claim,
              plus historical yearly data when available
    """
    result = {
        'drug_name': drug_name,
        'brand_name': brand_name,
        'total_spending': None,
        'total_claims': None,
        'total_beneficiaries': None,
        'avg_cost_per_claim': None,
        'avg_cost_per_beneficiary': None,
        'latest_year': None,
        'historical_spending': {},  # year -> spending dict
        'data_source': None,
        'part_d_spending': None,
        'part_b_spending': None
    }

    if not mcp_funcs:
        return result

    medicare_spending = mcp_funcs.get('medicare_spending')
    if not medicare_spending:
        return result

    # Try brand name first (more reliable), then drug name
    search_names = []
    if brand_name:
        search_names.append(brand_name)
    search_names.append(drug_name)

    def _fetch_spending(search_name: str, spending_type: str) -> Dict:
        """Fetch spending data for a specific part type."""
        try:
            spending = medicare_spending(
                spending_drug_name=search_name,
                spending_type=spending_type,
                size=10
            )
            drugs = spending.get('drugs', [])
            if drugs and len(drugs) > 0:
                return drugs[0]
        except Exception as e:
            pass
        return None

    def _parse_spending_data(drug_data: Dict, part_type: str) -> Dict:
        """Parse spending data from Medicare response."""
        parsed = {
            'brand_name': drug_data.get('brand_name'),
            'generic_name': drug_data.get('generic_name'),
            'total_spending': None,
            'total_claims': None,
            'total_beneficiaries': None,
            'latest_year': None,
            'historical_spending': {},
            'data_source': f'Medicare {part_type}'
        }

        spending_by_year = drug_data.get('spending_by_year', {})
        if spending_by_year:
            years = sorted(spending_by_year.keys(), reverse=True)
            latest_year = years[0] if years else None

            if latest_year:
                latest = spending_by_year[latest_year]
                parsed['latest_year'] = latest_year
                parsed['total_spending'] = float(latest.get('total_spending', 0))
                parsed['total_claims'] = int(float(latest.get('total_claims', 0)))
                parsed['total_beneficiaries'] = int(float(latest.get('total_beneficiaries', 0)))
                # Part B doesn't always have avg_spending fields
                parsed['avg_cost_per_claim'] = float(latest.get('avg_spending_per_claim', 0)) if latest.get('avg_spending_per_claim') else None
                parsed['avg_cost_per_beneficiary'] = float(latest.get('avg_spending_per_beneficiary', 0)) if latest.get('avg_spending_per_beneficiary') else None

            for year, year_data in spending_by_year.items():
                parsed['historical_spending'][year] = {
                    'total_spending': float(year_data.get('total_spending', 0)),
                    'total_claims': int(float(year_data.get('total_claims', 0))),
                    'total_beneficiaries': int(float(year_data.get('total_beneficiaries', 0)))
                }

        return parsed

    # Try both Part D and Part B for each search name
    part_d_data = None
    part_b_data = None

    for search_name in search_names:
        # Fetch Part D (retail)
        if not part_d_data:
            drug_data = _fetch_spending(search_name, 'part_d')
            if drug_data:
                part_d_data = _parse_spending_data(drug_data, 'Part D')

        # Fetch Part B (infusion/injectable)
        if not part_b_data:
            drug_data = _fetch_spending(search_name, 'part_b')
            if drug_data:
                part_b_data = _parse_spending_data(drug_data, 'Part B')

        # If we have both, stop searching
        if part_d_data and part_b_data:
            break

    # Determine which source to use (or combine)
    part_d_spend = part_d_data.get('total_spending', 0) if part_d_data else 0
    part_b_spend = part_b_data.get('total_spending', 0) if part_b_data else 0

    result['part_d_spending'] = part_d_spend
    result['part_b_spending'] = part_b_spend

    # Use the larger source as primary, note both in data_source
    if part_b_spend > part_d_spend and part_b_data:
        # Part B is primary (infusion drugs like Keytruda, Opdivo)
        primary = part_b_data
        result['data_source'] = 'Medicare Part B (infusion)'
        if part_d_spend > 0:
            result['data_source'] += f' + Part D'
    elif part_d_data:
        # Part D is primary (retail drugs)
        primary = part_d_data
        result['data_source'] = 'Medicare Part D (retail)'
        if part_b_spend > 0:
            result['data_source'] += f' + Part B'
    else:
        return result  # No data found

    # Copy primary data
    result['brand_name'] = primary.get('brand_name')
    result['generic_name'] = primary.get('generic_name')
    result['latest_year'] = primary.get('latest_year')
    result['avg_cost_per_claim'] = primary.get('avg_cost_per_claim')
    result['avg_cost_per_beneficiary'] = primary.get('avg_cost_per_beneficiary')

    # Combine spending from both sources
    result['total_spending'] = part_d_spend + part_b_spend
    result['total_claims'] = (
        (part_d_data.get('total_claims', 0) if part_d_data else 0) +
        (part_b_data.get('total_claims', 0) if part_b_data else 0)
    )
    result['total_beneficiaries'] = (
        (part_d_data.get('total_beneficiaries', 0) if part_d_data else 0) +
        (part_b_data.get('total_beneficiaries', 0) if part_b_data else 0)
    )

    # Combine historical spending
    all_years = set()
    if part_d_data:
        all_years.update(part_d_data.get('historical_spending', {}).keys())
    if part_b_data:
        all_years.update(part_b_data.get('historical_spending', {}).keys())

    for year in all_years:
        d_data = part_d_data.get('historical_spending', {}).get(year, {}) if part_d_data else {}
        b_data = part_b_data.get('historical_spending', {}).get(year, {}) if part_b_data else {}

        result['historical_spending'][year] = {
            'total_spending': d_data.get('total_spending', 0) + b_data.get('total_spending', 0),
            'total_claims': d_data.get('total_claims', 0) + b_data.get('total_claims', 0),
            'total_beneficiaries': d_data.get('total_beneficiaries', 0) + b_data.get('total_beneficiaries', 0),
            'part_d': d_data.get('total_spending', 0),
            'part_b': b_data.get('total_spending', 0)
        }

    return result


def get_nadac_pricing(drug_name: str, brand_name: str = None, mcp_funcs: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Get NADAC (National Average Drug Acquisition Cost) pricing.

    ENHANCED (2026-01-21): Now returns all matching NDCs with aggregate statistics.
    This helps estimate annual drug cost more accurately.

    Args:
        drug_name: Drug name (generic preferred)
        brand_name: Brand name (optional, for additional search)
        mcp_funcs: MCP function dictionary

    Returns:
        dict: NADAC pricing data with min/max/median per unit costs
    """
    result = {
        'drug_name': drug_name,
        'brand_name': brand_name,
        'nadac_per_unit': None,
        'nadac_min': None,
        'nadac_max': None,
        'nadac_median': None,
        'effective_date': None,
        'pricing_unit': None,
        'data_source': 'Medicaid NADAC',
        'ndc_count': 0,
        'product_descriptions': []
    }

    if not mcp_funcs:
        return result

    medicaid_lookup = mcp_funcs.get('medicaid_info')
    if not medicaid_lookup:
        return result

    # Track unique NDCs with their most recent price (keyed by NDC)
    ndc_prices = {}  # {ndc: {'price': float, 'date': str, 'description': str}}

    # Try both generic and brand name searches
    search_terms = [drug_name]
    if brand_name and brand_name.lower() != drug_name.lower():
        search_terms.append(brand_name)

    for search_term in search_terms:
        try:
            nadac = medicaid_lookup(
                method='get_nadac_pricing',
                drug_name=search_term,
                limit=500  # Get all available NDCs for accurate aggregate stats
            )

            data = nadac.get('data', [])
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        price = item.get('nadac_per_unit')
                        ndc = item.get('ndc', '')
                        desc = item.get('description', item.get('ndc_description', ''))
                        eff_date = item.get('effective_date', '')

                        # Only include products that contain our search term
                        # (NADAC search is partial match, may return unrelated combos)
                        if price and ndc and search_term.upper() in desc.upper():
                            # Keep only the most recent price for each unique NDC
                            if ndc not in ndc_prices or eff_date > ndc_prices[ndc]['date']:
                                ndc_prices[ndc] = {
                                    'price': float(price),
                                    'date': eff_date,
                                    'description': desc,
                                    'pricing_unit': item.get('pricing_unit')
                                }

        except Exception as e:
            print(f"    Note: NADAC lookup for '{search_term}' failed: {e}")

    if ndc_prices:
        # Extract unique prices (one per NDC)
        all_prices = sorted([v['price'] for v in ndc_prices.values()])
        all_descriptions = list(set([v['description'] for v in ndc_prices.values()]))

        # Get the most recent effective date across all NDCs
        most_recent = max(ndc_prices.values(), key=lambda x: x['date'])

        result['nadac_min'] = all_prices[0]
        result['nadac_max'] = all_prices[-1]
        result['nadac_median'] = all_prices[len(all_prices) // 2]
        result['nadac_per_unit'] = result['nadac_median']  # Use median as default
        result['ndc_count'] = len(ndc_prices)  # Count of unique NDCs
        result['product_descriptions'] = all_descriptions[:5]  # Top 5 unique
        result['effective_date'] = most_recent['date']
        result['pricing_unit'] = most_recent['pricing_unit']

        print(f"    ✓ NADAC: {len(ndc_prices)} unique NDCs, median ${result['nadac_median']:.2f}/unit")

    return result


def _fuzzy_match_measure(indication: str, measures: List[Dict]) -> Optional[str]:
    """
    Find the best matching CDC measure for an indication using fuzzy matching.

    Args:
        indication: Disease/condition name
        measures: List of CDC measure dicts with 'measureid' and 'measure' keys

    Returns:
        str: Best matching measureid or None
    """
    if not indication or not measures:
        return None

    indication_lower = indication.lower()
    indication_words = set(indication_lower.split())

    best_match = None
    best_score = 0

    for m in measures:
        measure_id = m.get('measureid', '')
        measure_name = m.get('measure', '').lower()

        # Skip non-disease measures (screenings, social determinants, behaviors)
        skip_keywords = ['screening', 'checkup', 'insurance', 'dentist', 'mammography',
                         'transportation', 'housing', 'food stamp', 'utility', 'loneliness',
                         'emotional', 'leisure']
        if any(kw in measure_name for kw in skip_keywords):
            continue

        score = 0

        # Exact measureid match in indication (e.g., "diabetes" matches "DIABETES")
        if measure_id.lower() in indication_lower:
            score += 100

        # Exact indication match in measure name
        if indication_lower in measure_name:
            score += 80

        # Word overlap scoring
        measure_words = set(measure_name.split())
        common_words = indication_words & measure_words
        # Exclude common words like "among", "adults", "the", "of"
        stopwords = {'among', 'adults', 'the', 'of', 'in', 'or', 'and', 'with', 'aged', 'years'}
        meaningful_common = common_words - stopwords
        score += len(meaningful_common) * 20

        # Partial word matching (e.g., "diabetic" matches "diabetes")
        for ind_word in indication_words - stopwords:
            for meas_word in measure_words - stopwords:
                if len(ind_word) > 3 and len(meas_word) > 3:
                    if ind_word[:4] == meas_word[:4]:  # Same prefix
                        score += 15

        if score > best_score:
            best_score = score
            best_match = measure_id

    # Only return if we have a reasonable match
    return best_match if best_score >= 15 else None


def _get_cdc_measures(mcp_funcs: Dict[str, Any] = None) -> List[Dict]:
    """
    Fetch available CDC PLACES measures dynamically.

    Args:
        mcp_funcs: MCP function dictionary

    Returns:
        list: List of measure dicts with 'measureid' and 'measure' keys
    """
    if not mcp_funcs:
        return []

    cdc_health = mcp_funcs.get('cdc_health_data')
    if not cdc_health:
        return []

    try:
        result = cdc_health(
            method='get_available_measures',
            dataset_name='places_county_2024'
        )
        return result.get('measures', [])
    except Exception as e:
        print(f"  Warning: Could not fetch CDC measures: {e}")
        return []


def refine_indication_from_drugbank(indication: str, drug_indication_text: str = None) -> str:
    """
    Refine a broad indication using DrugBank indication text.

    CRITICAL FIX (2026-01-21): This prevents searching for broad indications
    like "arthritis" (23% prevalence) when the drug actually treats specific
    conditions like "rheumatoid arthritis" (0.5-1% prevalence).

    Args:
        indication: User-provided indication (may be broad)
        drug_indication_text: DrugBank indication text (if available)

    Returns:
        str: Refined indication (more specific if possible)
    """
    import re

    if not drug_indication_text:
        return indication

    indication_lower = indication.lower().strip()

    # Common broad-to-specific mappings with disease patterns
    # These are patterns to extract from DrugBank text
    REFINEMENT_PATTERNS = {
        'arthritis': [
            r'rheumatoid\s+arthritis',
            r'psoriatic\s+arthritis',
            r'juvenile\s+(?:idiopathic\s+)?arthritis',
            r'ankylosing\s+spondylitis',
        ],
        'diabetes': [
            r'type\s*2\s+diabetes(?:\s+mellitus)?',
            r'type\s*1\s+diabetes(?:\s+mellitus)?',
            r'diabetic\s+(?:nephropathy|retinopathy|neuropathy)',
        ],
        'cancer': [
            r'(?:non-small\s+cell\s+)?lung\s+cancer',
            r'breast\s+cancer',
            r'colorectal\s+cancer',
            r'melanoma',
            r'lymphoma',
            r'leukemia',
            r'prostate\s+cancer',
            r'ovarian\s+cancer',
        ],
        'heart disease': [
            r'heart\s+failure',
            r'atrial\s+fibrillation',
            r'coronary\s+artery\s+disease',
            r'myocardial\s+infarction',
        ],
        'obesity': [
            r'obesity',
            r'chronic\s+weight\s+management',
        ],
        'depression': [
            r'major\s+depressive\s+disorder',
            r'treatment[- ]resistant\s+depression',
        ],
        'asthma': [
            r'(?:moderate\s+to\s+)?severe\s+(?:persistent\s+)?asthma',
            r'eosinophilic\s+asthma',
        ],
        'psoriasis': [
            r'plaque\s+psoriasis',
            r'pustular\s+psoriasis',
        ],
    }

    # Check if user indication matches a broad category
    for broad_category, patterns in REFINEMENT_PATTERNS.items():
        if broad_category in indication_lower or indication_lower in broad_category:
            # Search for specific conditions in DrugBank text
            db_text_lower = drug_indication_text.lower()

            for pattern in patterns:
                match = re.search(pattern, db_text_lower)
                if match:
                    refined = match.group(0)
                    # Capitalize properly
                    refined = ' '.join(w.capitalize() for w in refined.split())
                    print(f"    ✓ Refined indication: '{indication}' → '{refined}'")
                    return refined

    return indication


def get_disease_prevalence(indication: str, drug_indication_text: str = None, mcp_funcs: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Get disease prevalence data using multiple sources (Data Commons → CDC → WHO).

    Uses dynamic population lookup from Data Commons instead of hardcoded values.

    Args:
        indication: Disease/condition name
        drug_indication_text: Optional DrugBank indication text for refinement
        mcp_funcs: MCP function dictionary

    Returns:
        dict: Prevalence data including US patient population estimates
    """
    # CRITICAL FIX (2026-01-21): Refine broad indications using DrugBank text
    # This prevents searching for "arthritis" (23%) when drug treats "rheumatoid arthritis" (0.5%)
    original_indication = indication
    if drug_indication_text:
        indication = refine_indication_from_drugbank(indication, drug_indication_text)

    result = {
        'indication': indication,
        'original_indication': original_indication if original_indication != indication else None,
        'us_prevalence_pct': None,
        'us_patient_population': None,
        'us_adult_population': None,
        'data_year': None,
        'data_source': None,
        'matched_measure': None,
        'global_prevalence_pct': None,
        'population_source': None
    }

    if not mcp_funcs:
        return result

    cdc_health = mcp_funcs.get('cdc_health_data')

    # Step 1: Get US adult population from Data Commons (dynamic, not hardcoded)
    print(f"    Fetching US population from Data Commons...")
    us_adult_pop, pop_year = get_us_adult_population(mcp_funcs)

    if us_adult_pop:
        result['us_adult_population'] = us_adult_pop
        result['population_source'] = f'Data Commons ({pop_year})'
        print(f"    ✓ US adult population: {us_adult_pop:,} ({pop_year})")
    else:
        # Fallback to reasonable estimate (will be logged)
        us_adult_pop = 261_000_000  # 2023 estimate
        result['us_adult_population'] = us_adult_pop
        result['population_source'] = 'Fallback estimate (2023)'
        print(f"    ⚠ Using fallback US adult population: {us_adult_pop:,}")

    # Step 2: Try Data Commons for prevalence first (more direct API)
    print(f"    Searching Data Commons for '{indication}' prevalence...")
    dc_prevalence, dc_year, dc_variable = get_disease_prevalence_datacommons(indication, mcp_funcs)

    if dc_prevalence:
        result['us_prevalence_pct'] = dc_prevalence
        result['data_year'] = dc_year
        result['data_source'] = f'Data Commons ({dc_variable})'
        result['matched_measure'] = dc_variable
        result['us_patient_population'] = int(us_adult_pop * (dc_prevalence / 100))
        print(f"    ✓ Prevalence from Data Commons: {dc_prevalence:.1f}% ({dc_year})")
        return result

    # Step 3: Fallback to CDC PLACES
    print(f"    Trying CDC PLACES for '{indication}'...")
    measures = _get_cdc_measures(mcp_funcs)

    if measures:
        measure_id = _fuzzy_match_measure(indication, measures)

        if measure_id:
            result['matched_measure'] = measure_id

            if cdc_health:
                try:
                    cdc_data = cdc_health(
                        method='get_places_data',
                        measure_id=measure_id,
                        geography_level='county',
                        year='2023',
                        limit=100
                    )

                    data = cdc_data.get('data', cdc_data)
                    results = data.get('results', []) if isinstance(data, dict) else []

                    if results:
                        prevalences = []
                        for item in results:
                            if isinstance(item, dict):
                                prev = item.get('data_value', item.get('Data_Value'))
                                if prev:
                                    try:
                                        prevalences.append(float(prev))
                                    except (ValueError, TypeError):
                                        pass

                        if prevalences:
                            avg_prevalence = sum(prevalences) / len(prevalences)
                            result['us_prevalence_pct'] = avg_prevalence
                            result['us_patient_population'] = int(us_adult_pop * (avg_prevalence / 100))
                            result['data_year'] = '2023'
                            result['data_source'] = f'CDC PLACES ({measure_id})'
                            print(f"    ✓ Prevalence from CDC: {avg_prevalence:.1f}%")
                            return result

                except Exception as e:
                    print(f"    Warning: CDC PLACES lookup failed: {e}")

    # Step 4: Try WHO for global data as final fallback
    print(f"    Trying WHO for global prevalence...")
    who_data = get_global_prevalence_who(indication, mcp_funcs)

    if who_data.get('us_prevalence_pct'):
        result['us_prevalence_pct'] = who_data['us_prevalence_pct']
        result['us_patient_population'] = int(us_adult_pop * (who_data['us_prevalence_pct'] / 100))
        result['data_source'] = f'WHO ({who_data.get("indicator_code", "unknown")})'
        result['data_year'] = who_data.get('data_year')
        print(f"    ✓ Prevalence from WHO: {who_data['us_prevalence_pct']:.1f}%")
    elif who_data.get('global_prevalence_pct'):
        # Use global average as estimate
        result['us_prevalence_pct'] = who_data['global_prevalence_pct']
        result['us_patient_population'] = int(us_adult_pop * (who_data['global_prevalence_pct'] / 100))
        result['data_source'] = f'WHO Global Average ({who_data.get("indicator_code", "unknown")})'
        result['data_year'] = who_data.get('data_year')
        print(f"    ⚠ Using global average: {who_data['global_prevalence_pct']:.1f}%")

    result['global_prevalence_pct'] = who_data.get('global_prevalence_pct')

    if not result['us_prevalence_pct']:
        print(f"    ⚠ No prevalence data found for '{indication}'")

    return result


def get_prescriber_volume(drug_name: str, state: str = None, mcp_funcs: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Get prescriber volume data for a drug.

    Args:
        drug_name: Drug name
        state: Optional state filter
        mcp_funcs: MCP function dictionary

    Returns:
        dict: Prescriber volume data
    """
    result = {
        'drug_name': drug_name,
        'total_prescribers': 0,
        'top_specialties': [],
        'data_source': 'Medicare Part D Prescribers'
    }

    if not mcp_funcs:
        return result

    medicare_prescribers = mcp_funcs.get('medicare_prescribers')
    if not medicare_prescribers:
        return result

    try:
        params = {
            'drug_name': drug_name,
            'size': 100
        }
        if state:
            params['state'] = state

        prescribers = medicare_prescribers(**params)

        data = prescribers.get('data', prescribers)
        results = data.get('results', []) if isinstance(data, dict) else []

        result['total_prescribers'] = len(results)

        # Count by specialty
        specialty_counts = {}
        for item in results:
            if isinstance(item, dict):
                specialty = item.get('Prscrbr_Type', item.get('provider_type', 'Unknown'))
                specialty_counts[specialty] = specialty_counts.get(specialty, 0) + 1

        # Sort by count
        sorted_specialties = sorted(specialty_counts.items(), key=lambda x: x[1], reverse=True)
        result['top_specialties'] = [
            {'specialty': s, 'count': c}
            for s, c in sorted_specialties[:5]
        ]

    except Exception as e:
        print(f"  Warning: Prescriber lookup failed: {e}")

    return result


def get_segment_revenue_validation(
    drug_name: str,
    indication: str = None,
    mcp_funcs: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Get manufacturer segment revenue as a validation/cross-check source.

    Uses SEC XBRL dimensional analysis (primary) or Yahoo Finance (fallback)
    to get segment-level revenue that can validate Medicare spending data.

    Args:
        drug_name: Drug name
        indication: Drug indication (helps match segment)
        mcp_funcs: MCP function dictionary

    Returns:
        dict: Segment revenue data or empty dict if unavailable
    """
    result = {
        'segment_name': None,
        'segment_revenue': None,
        'total_company_revenue': None,
        'manufacturer': None,
        'ticker': None,
        'source': None
    }

    if not mcp_funcs:
        return result

    try:
        print(f"  Fetching manufacturer segment revenue (SEC/Yahoo)...")
        segment_data = get_manufacturer_segment_revenue(drug_name, indication, mcp_funcs)

        if segment_data:
            result['segment_name'] = segment_data.get('segment_name')
            result['segment_revenue'] = segment_data.get('segment_revenue')
            result['total_company_revenue'] = segment_data.get('total_revenue')
            result['manufacturer'] = segment_data.get('manufacturer')
            result['ticker'] = segment_data.get('ticker')
            result['source'] = segment_data.get('source')

    except Exception as e:
        print(f"  Note: Segment revenue lookup failed: {e}")

    return result


def estimate_market_size(
    drug_name: str,
    indication: str,
    brand_name: str = None,
    addressable_market_pct: float = None,  # Now dynamic by default
    include_segment_validation: bool = True,
    current_sales: float = None,
    drug_indication_text: str = None,
    mcp_funcs: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Estimate total addressable market for a drug using dynamic data sources.

    Uses Data Commons + WHO for population/prevalence (no hardcoding).
    Calculates addressable market percentage dynamically based on:
    - Therapeutic area adoption rates
    - Current market penetration
    - Segment revenue constraints

    Args:
        drug_name: Drug name (generic preferred)
        indication: Primary indication
        brand_name: Brand name (Ozempic, Humira) - improves Medicare data lookup
        addressable_market_pct: Override for addressable % (None = dynamic calculation)
        include_segment_validation: Whether to fetch SEC/Yahoo segment revenue
        current_sales: Current drug sales (helps calibrate addressable %)
        drug_indication_text: DrugBank indication text (for refining broad indications)
        mcp_funcs: MCP function dictionary

    Returns:
        dict: Market size estimates with full data source attribution
    """
    if not mcp_funcs:
        return {
            'drug_name': drug_name,
            'indication': indication,
            'error': 'mcp_funcs required for market sizing'
        }

    print(f"  Fetching spending data...")
    spending = get_drug_spending_data(drug_name, brand_name=brand_name, mcp_funcs=mcp_funcs)

    print(f"  Fetching disease prevalence (Data Commons → CDC → WHO)...")
    prevalence = get_disease_prevalence(indication, drug_indication_text=drug_indication_text, mcp_funcs=mcp_funcs)

    print(f"  Fetching pricing data (NADAC)...")
    pricing = get_nadac_pricing(drug_name, brand_name=brand_name, mcp_funcs=mcp_funcs)

    # Optional: Get segment revenue for validation
    segment_revenue = {}
    if include_segment_validation:
        segment_revenue = get_segment_revenue_validation(drug_name, indication, mcp_funcs)

    # Calculate market estimates
    patient_pop = prevalence.get('us_patient_population', 0)

    # Estimate annual cost per patient
    annual_cost = None
    if spending.get('avg_cost_per_beneficiary'):
        annual_cost = spending['avg_cost_per_beneficiary']
    elif pricing.get('nadac_per_unit'):
        # Rough estimate: assume 365 daily doses
        annual_cost = pricing['nadac_per_unit'] * 365

    # Get current sales for penetration calculation
    if not current_sales and spending.get('total_spending'):
        current_sales = spending['total_spending']

    # Get segment revenue value
    seg_rev_value = segment_revenue.get('segment_revenue') if segment_revenue else None

    # Calculate dynamic addressable market percentage
    indication_mismatch_warning = None
    if addressable_market_pct is None:
        addressable_market_pct, indication_mismatch_warning = calculate_dynamic_addressable_market_pct(
            indication=indication,
            current_sales=current_sales,
            segment_revenue=seg_rev_value,
            patient_population=patient_pop,
            annual_cost=annual_cost
        )
        print(f"  ✓ Addressable market: {addressable_market_pct*100:.1f}%")

    addressable_patients = int(patient_pop * addressable_market_pct) if patient_pop else None

    # Calculate TAM
    tam = None
    if addressable_patients and annual_cost:
        tam = addressable_patients * annual_cost

    return {
        'drug_name': drug_name,
        'indication': indication,
        'market_sizing': {
            'us_patient_population': patient_pop,
            'us_adult_population': prevalence.get('us_adult_population'),
            'addressable_market_pct': addressable_market_pct,
            'addressable_patients': addressable_patients,
            'avg_annual_cost_per_patient': annual_cost,
            'total_addressable_market_usd': tam,
            'population_source': prevalence.get('population_source'),
            'prevalence_source': prevalence.get('data_source'),
            'indication_mismatch_warning': indication_mismatch_warning
        },
        'spending_data': spending,
        'prevalence_data': prevalence,
        'pricing_data': pricing,
        'segment_revenue_data': segment_revenue
    }


if __name__ == "__main__":
    # Test with a known drug
    if len(sys.argv) > 1:
        drug = sys.argv[1]
        indication = sys.argv[2] if len(sys.argv) > 2 else "type 2 diabetes"
    else:
        drug = "semaglutide"
        indication = "type 2 diabetes"

    print(f"\n📊 Market Sizing for: {drug}")
    print(f"   Indication: {indication}")
    print("=" * 60)

    market = estimate_market_size(drug, indication)

    sizing = market['market_sizing']
    print(f"\nUS Patient Population: {sizing['us_patient_population']:,}" if sizing['us_patient_population'] else "\nUS Patient Population: Unknown")
    print(f"Addressable Patients ({sizing['addressable_market_pct']*100:.0f}%): {sizing['addressable_patients']:,}" if sizing['addressable_patients'] else "Addressable Patients: Unknown")
    print(f"Avg Annual Cost: ${sizing['avg_annual_cost_per_patient']:,.2f}" if sizing['avg_annual_cost_per_patient'] else "Avg Annual Cost: Unknown")
    print(f"Total Addressable Market: ${sizing['total_addressable_market_usd']:,.0f}" if sizing['total_addressable_market_usd'] else "Total Addressable Market: Unknown")

    spending = market['spending_data']
    print(f"\nMedicare Part D Spending: ${spending['total_spending']:,.0f}" if spending['total_spending'] else "\nMedicare Part D Spending: Unknown")
    print(f"Total Beneficiaries: {spending['total_beneficiaries']:,}" if spending['total_beneficiaries'] else "Total Beneficiaries: Unknown")
