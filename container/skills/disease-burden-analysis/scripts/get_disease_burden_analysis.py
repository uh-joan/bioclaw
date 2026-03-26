#!/usr/bin/env python3
"""
Disease Burden Analysis - Main entry point & orchestrator.

Produces a comprehensive disease burden profile by aggregating data from
CDC, WHO, Data Commons, PubMed, ClinicalTrials.gov, and Medicare.

Usage:
    CLI: PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/disease-burden-analysis/scripts/get_disease_burden_analysis.py "type 2 diabetes"
    Server: Injected via skill executor with mcp_funcs
"""

import sys
import os
import re
import traceback
from typing import Dict, Any, Optional, List

# Add script directory to path for local imports
_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _script_dir)

from progress_tracker import create_progress_tracker
from visualization_utils import generate_report


# ─── Helper: safe text extraction ──────────────────────────────
def _flatten_text(val) -> str:
    """Flatten PubMed markup dicts or nested structures to plain text."""
    if isinstance(val, str):
        return val
    if isinstance(val, dict):
        parts = []
        if '_' in val:
            parts.append(str(val['_']))
        for k, v in val.items():
            if k == '_':
                continue
            if isinstance(v, list):
                parts.extend(str(x) for x in v)
            else:
                parts.append(str(v))
        return ' '.join(parts)
    if isinstance(val, list):
        return ' '.join(_flatten_text(x) for x in val)
    return str(val) if val else ''


def _who_keyword(disease: str) -> str:
    """Extract a single meaningful keyword for WHO search_indicators.

    WHO's search_indicators uses OData contains() which fails on multi-word
    phrases. We need the single most informative keyword from the disease name.
    Skips common filler words that would return irrelevant results.
    """
    skip_words = {
        'type', 'stage', 'grade', 'acute', 'chronic', 'major', 'primary',
        'secondary', 'advanced', 'early', 'late', 'mild', 'moderate',
        'severe', 'non', 'small', 'large', 'cell', 'disease', 'disorder',
        'syndrome', 'condition', 'the', 'a', 'an', 'of', 'and', 'or',
    }
    words = disease.lower().strip().split()
    # Return first non-filler word, or the last word as fallback
    for w in words:
        # Strip digits (e.g., "2" in "type 2 diabetes")
        if w.isdigit():
            continue
        if w not in skip_words:
            return w
    return words[-1] if words else disease


def _safe_call(func, timeout_sec=60, **kwargs):
    """Call an MCP function with a timeout wrapper to prevent hangs."""
    if func is None:
        return None
    from concurrent.futures import ThreadPoolExecutor
    pool = ThreadPoolExecutor(max_workers=1)
    try:
        future = pool.submit(func, **kwargs)
        return future.result(timeout=timeout_sec)
    except Exception as e:
        print(f"  [debug] _safe_call failed: {type(e).__name__}: {str(e)[:100]}", file=sys.stderr)
        return None
    finally:
        pool.shutdown(wait=False, cancel_futures=True)


# ─── CDC measure ID mapping ───────────────────────────────────
# Maps disease keywords to CDC PLACES measure IDs
CDC_MEASURE_MAP = {
    'diabetes': 'DIABETES',
    'obesity': 'OBESITY',
    'overweight': 'OBESITY',
    'asthma': 'CASTHMA',
    'copd': 'COPD',
    'chronic obstructive': 'COPD',
    'heart disease': 'CHD',
    'coronary heart': 'CHD',
    'cardiac': 'CHD',
    'stroke': 'STROKE',
    'cerebrovascular': 'STROKE',
    'cancer': 'CANCER',
    'carcinoma': 'CANCER',
    'kidney': 'KIDNEY',
    'renal': 'KIDNEY',
    'nephro': 'KIDNEY',
    'depression': 'DEPRESSION',
    'depressive': 'DEPRESSION',
    'arthritis': 'ARTHRITIS',
    'rheumatoid': 'ARTHRITIS',
    'high blood pressure': 'BPHIGH',
    'hypertension': 'BPHIGH',
    'high cholesterol': 'HIGHCHOL',
    'hypercholesterol': 'HIGHCHOL',
    'dyslipidemia': 'HIGHCHOL',
    'smoking': 'CSMOKING',
    'tobacco': 'CSMOKING',
    'mental health': 'MHLTH',
    'physical health': 'PHLTH',
}


def _find_cdc_measure(disease: str) -> Optional[str]:
    """Find CDC PLACES measure ID for a disease name."""
    disease_lower = disease.lower()
    for keyword, measure_id in CDC_MEASURE_MAP.items():
        if keyword in disease_lower:
            return measure_id
    return None


# ─── BRFSS topic mapping ──────────────────────────────────────
# Maps disease keywords to BRFSS comprehensive dataset topic names.
# These are distinct from CDC PLACES measure IDs above.
BRFSS_TOPIC_MAP = {
    'diabetes': 'Diabetes',
    'obesity': 'BMI Categories',
    'overweight': 'BMI Categories',
    'asthma': 'Asthma',
    'copd': 'COPD',
    'chronic obstructive': 'COPD',
    'heart disease': 'Cardiovascular Disease',
    'coronary': 'Cardiovascular Disease',
    'cardiac': 'Cardiovascular Disease',
    'stroke': 'Cardiovascular Disease',
    'depression': 'Depression',
    'depressive': 'Depression',
    'arthritis': 'Arthritis',
    'kidney': 'Kidney',
    'renal': 'Kidney',
    'hypertension': 'Cardiovascular Disease',
    'high blood pressure': 'Cardiovascular Disease',
}


def _find_brfss_topic(disease: str) -> Optional[str]:
    """Find BRFSS comprehensive topic name for a disease."""
    disease_lower = disease.lower()
    for keyword, topic in BRFSS_TOPIC_MAP.items():
        if keyword in disease_lower:
            return topic
    return None


def _parse_brfss_demographics(data_rows: list, section: dict) -> None:
    """Parse BRFSS comprehensive data into demographic distributions.

    BRFSS uses break_out_category ('Age Group', 'Sex', 'Race/Ethnicity')
    and break_out ('18-24', 'Male', 'White, non-Hispanic', etc.) for
    stratification. National-level rows have no breakdowns, so state-level
    data is averaged across states per group.
    """
    from collections import defaultdict

    # Accumulate values per (category, group) for cross-state averaging
    accum = defaultdict(list)  # (category, group) -> [values]

    for row in data_rows:
        if not row:  # Skip empty dicts
            continue
        cat = row.get('break_out_category', '')
        group = row.get('break_out', '')
        val = row.get('data_value')
        if not cat or not group or val is None:
            continue
        try:
            val = float(val)
        except (ValueError, TypeError):
            continue
        accum[(cat, group)].append(val)

    # Average across states and classify
    for (cat, group), values in sorted(accum.items()):
        if not values:
            continue
        avg = sum(values) / len(values)

        if cat == 'Age Group':
            section['age_distribution'].append({'group': group, 'percent': round(avg, 1)})
        elif cat == 'Sex':
            section['sex_distribution'].append({'group': group, 'percent': round(avg, 1)})
        elif cat == 'Race/Ethnicity':
            section['race_distribution'].append({'group': group, 'percent': round(avg, 1)})
        elif cat == 'Household Income':
            section['income_distribution'].append({'group': group, 'percent': round(avg, 1)})
        elif cat == 'Education Attained':
            section['education_distribution'].append({'group': group, 'percent': round(avg, 1)})


# ─── Section: Epidemiology ─────────────────────────────────────
def _fetch_epidemiology(
    disease: str,
    geography: str,
    cdc_search,
    who_search,
    datacommons_search,
    tracker,
) -> Dict[str, Any]:
    """Fetch prevalence, incidence, mortality from CDC + WHO + DataCommons."""
    section = {
        'prevalence': {},
        'incidence': {},
        'mortality': {},
        'dalys': {},
        'additional_metrics': [],
        'provenance': [],
    }

    tracker.start_step('epidemiology', f"Fetching epidemiology data for {disease}...")

    # --- CDC: US prevalence data ---
    if cdc_search and geography.upper() in ('US', 'GLOBAL'):
        try:
            tracker.update_step(0.1, "Querying CDC for prevalence...")
            measure_id = _find_cdc_measure(disease)

            if measure_id:
                # Use PLACES data for exact measure (try recent years)
                cdc_resp = None
                for year in ('2024', '2023', '2022'):
                    cdc_resp = _safe_call(
                        cdc_search,
                        method='get_places_data',
                        geography_level='county',
                        measure_id=measure_id,
                        year=year,
                        limit=50,
                    )
                    if cdc_resp and isinstance(cdc_resp, dict):
                        data_rows = cdc_resp.get('data', [])
                        if data_rows and isinstance(data_rows, list):
                            break  # Found data for this year
            else:
                # Fallback: search datasets
                cdc_resp = _safe_call(
                    cdc_search,
                    method='search_dataset',
                    dataset_name=disease,
                    limit=50,
                )

            if cdc_resp and isinstance(cdc_resp, dict):
                data_rows = cdc_resp.get('data', [])
                if data_rows and isinstance(data_rows, list):
                    # Extract average prevalence across counties
                    values = []
                    for row in data_rows:
                        val = row.get('Data_Value') or row.get('data_value')
                        if val is not None:
                            try:
                                values.append(float(val))
                            except (ValueError, TypeError):
                                pass
                    if values:
                        avg_prev = sum(values) / len(values)
                        section['prevalence'] = {
                            'value': f"{avg_prev:.1f}%",
                            'unit': 'age-adjusted prevalence',
                            'source': 'CDC PLACES',
                            'year': '2024',
                            'sample_size': len(values),
                        }
                        section['provenance'].append(
                            f"CDC PLACES: {measure_id or disease} prevalence ({len(values)} counties)"
                        )
                elif isinstance(cdc_resp.get('content'), str):
                    # Free-text response - extract what we can
                    text = cdc_resp['content']
                    section['additional_metrics'].append({
                        'label': 'CDC Data',
                        'value': _flatten_text(text)[:200],
                    })
                    section['provenance'].append("CDC: free-text data response")

        except Exception as e:
            section['additional_metrics'].append({
                'label': 'CDC Error',
                'value': str(e)[:100],
            })

    # --- WHO: Global burden ---
    tracker.update_step(0.4, "Querying WHO for global burden...")
    if who_search:
        try:
            # Search for disease indicators
            # WHO search_indicators uses OData contains() — multi-word AND
            # phrases return 0 results. Search single keyword, filter client-side.
            disease_keyword = _who_keyword(disease)
            who_indicators = _safe_call(
                who_search,
                method='search_indicators',
                keywords=disease_keyword,
            )
            indicators = []
            if who_indicators and isinstance(who_indicators, dict):
                indicators = who_indicators.get('indicators', [])
                # Filter for mortality-related indicators client-side
                mortality_indicators = [
                    ind for ind in indicators
                    if any(w in (ind.get('name', '') or '').lower()
                           for w in ('death', 'mortality', 'mort'))
                ]
                # Determine which field this indicator maps to
                is_mortality_specific = bool(mortality_indicators)
                if not mortality_indicators:
                    mortality_indicators = indicators  # fallback to all
                if mortality_indicators:
                    # Take the first relevant indicator and get data
                    indicator_code = mortality_indicators[0].get('code', '')
                    indicator_name = mortality_indicators[0].get('name', '')
                    # Determine correct field based on indicator name
                    ind_name_lower = (indicator_name or '').lower()
                    if any(w in ind_name_lower for w in ('death', 'mortality', 'mort')):
                        who_field = 'mortality'
                    elif any(w in ind_name_lower for w in ('prevalence', 'incidence')):
                        who_field = 'prevalence' if 'prevalence' in ind_name_lower else 'incidence'
                    elif any(w in ind_name_lower for w in ('daly', 'disability', 'burden')):
                        who_field = 'dalys'
                    elif is_mortality_specific:
                        who_field = 'mortality'
                    else:
                        who_field = 'prevalence'  # safe default for non-mortality indicators

                    if indicator_code:
                        who_data = _safe_call(
                            who_search,
                            method='get_health_data',
                            indicator_code=indicator_code,
                            top=20,
                            filter="SpatialDim eq 'USA'" if geography.upper() == 'US' else None,
                        )
                        if who_data and isinstance(who_data, dict):
                            # WHO response uses 'data' key with snake_case fields
                            values_list = who_data.get('data', who_data.get('value', []))
                            if values_list:
                                for rec in values_list[:5]:
                                    num_val = rec.get('numeric_value', rec.get('NumericValue'))
                                    year = rec.get('time_dim', rec.get('TimeDim'))
                                    country = rec.get('spatial_dim', rec.get('SpatialDim', ''))
                                    if num_val is not None:
                                        if not section[who_field].get('value'):
                                            section[who_field] = {
                                                'value': str(num_val),
                                                'unit': indicator_name,
                                                'year': str(year) if year else '',
                                                'source': 'WHO GHO',
                                            }
                                        break

                    section['provenance'].append(
                        f"WHO GHO: searched '{disease_keyword}' -> {len(indicators)} indicators ({len(mortality_indicators)} mortality-related)"
                    )

            # Search for DALY indicators — reuse same indicator list,
            # filter for DALY-related ones client-side
            daly_indicators = [
                ind for ind in indicators
                if any(w in (ind.get('name', '') or '').lower()
                       for w in ('daly', 'disability', 'burden'))
            ]
            if daly_indicators:
                daly_code = daly_indicators[0].get('code', '')
                daly_name = daly_indicators[0].get('name', '')
                if daly_code:
                    daly_data = _safe_call(
                        who_search,
                        method='get_health_data',
                        indicator_code=daly_code,
                        top=10,
                    )
                    if daly_data and isinstance(daly_data, dict):
                        daly_values = daly_data.get('data', daly_data.get('value', []))
                        if daly_values:
                            for rec in daly_values:
                                num_val = rec.get('numeric_value', rec.get('NumericValue'))
                                if num_val is not None:
                                    section['dalys'] = {
                                        'value': str(num_val),
                                        'unit': daly_name,
                                        'source': 'WHO GHO',
                                    }
                                    break
                section['provenance'].append(
                    f"WHO GHO: {len(daly_indicators)} DALY-related indicators found"
                )

        except Exception as e:
            section.setdefault('error', str(e))

    # --- DataCommons: population-level indicators ---
    tracker.update_step(0.7, "Querying Data Commons for population indicators...")
    if datacommons_search:
        try:
            dc_resp = _safe_call(
                datacommons_search,
                query=f"{disease} prevalence",
                places=["United States"] if geography.upper() == 'US' else None,
            )
            if dc_resp and isinstance(dc_resp, dict):
                variables = dc_resp.get('variables', [])
                name_map = dc_resp.get('dcid_name_mappings', {})
                if variables:
                    for var in variables[:3]:
                        dcid = var.get('dcid', '')
                        name = name_map.get(dcid, dcid)
                        section['additional_metrics'].append({
                            'label': f"DataCommons: {name}",
                            'value': dcid,
                        })
                    section['provenance'].append(
                        f"Data Commons: searched '{disease} prevalence' -> {len(variables)} variables"
                    )
        except Exception:
            pass

    tracker.complete_step("Epidemiology data collected")
    return section


# ─── Section: Demographics ─────────────────────────────────────
def _fetch_demographics(
    disease: str,
    geography: str,
    cdc_search,
    pubmed_search,
    tracker,
) -> Dict[str, Any]:
    """Fetch age/sex/race distribution and risk factors."""
    section = {
        'age_distribution': [],
        'sex_distribution': [],
        'race_distribution': [],
        'income_distribution': [],
        'education_distribution': [],
        'risk_factors': [],
        'provenance': [],
    }

    tracker.start_step('demographics', "Fetching demographic data...")

    # --- CDC BRFSS: demographic breakdown via brfss_comprehensive ---
    # BRFSS comprehensive dataset uses break_out_category / break_out fields
    # for demographic stratification. National-level ('US') has no breakdowns,
    # so we query state-level data and average across states.
    if cdc_search and geography.upper() in ('US', 'GLOBAL'):
        try:
            tracker.update_step(0.2, "Querying CDC BRFSS for demographics...")

            # Map disease to BRFSS topic name
            brfss_topic = _find_brfss_topic(disease)
            if brfss_topic:
                brfss_resp = _safe_call(
                    cdc_search,
                    method='search_dataset',
                    dataset_name='brfss_comprehensive',
                    where_clause=f"topic='{brfss_topic}' AND response='Yes' AND year='2024'",
                    limit=1000,
                    timeout_sec=90,
                )
                # Fallback to 2023 if 2024 returns no data
                if brfss_resp and isinstance(brfss_resp, dict):
                    data_rows = brfss_resp.get('data', [])
                    if not data_rows or all(not r for r in data_rows):
                        brfss_resp = _safe_call(
                            cdc_search,
                            method='search_dataset',
                            dataset_name='brfss_comprehensive',
                            where_clause=f"topic='{brfss_topic}' AND response='Yes' AND year='2023'",
                            limit=1000,
                            timeout_sec=90,
                        )

                if brfss_resp and isinstance(brfss_resp, dict):
                    data_rows = brfss_resp.get('data', [])
                    if data_rows:
                        _parse_brfss_demographics(data_rows, section)
                        section['provenance'].append(
                            f"CDC BRFSS Comprehensive: {brfss_topic} demographic data ({len(data_rows)} records)"
                        )

        except Exception as e:
            section['error'] = str(e)

    # --- PubMed: risk factors from epidemiology reviews ---
    if pubmed_search:
        try:
            tracker.update_step(0.6, "Searching PubMed for risk factors...")
            # Use focused query to avoid tangential papers
            pm_resp = _safe_call(
                pubmed_search,
                query=f'"{disease}" risk factors prevalence epidemiology review',
                num_results=5,
            )
            if pm_resp:
                articles = []
                if isinstance(pm_resp, dict):
                    articles = pm_resp.get('articles', [])
                elif isinstance(pm_resp, list):
                    articles = pm_resp

                disease_lower = disease.lower()
                for article in articles[:5]:
                    # Skip articles whose title doesn't mention the disease
                    title = _flatten_text(article.get('title', '')).lower()
                    if not any(w in title for w in disease_lower.split()):
                        continue

                    abstract = _flatten_text(article.get('abstract', ''))
                    if abstract:
                        # Extract risk factors — look for list-like structures
                        risk_patterns = [
                            r'(?:key|major|known|established|modifiable|common)\s+risk\s+factors?\s+(?:include|are|were|for)\s+([^.]+)',
                            r'risk\s+factors?\s+(?:include|are|were|for\s+\w+\s+\w+\s+include)\s+([^.]+)',
                        ]
                        for pattern in risk_patterns:
                            matches = re.findall(pattern, abstract, re.IGNORECASE)
                            for match in matches[:2]:
                                # Split comma-separated list items
                                items = re.split(r',\s*(?:and\s+)?', match.strip())
                                for item in items:
                                    cleaned = item.strip().rstrip('.;')[:80]
                                    # Filter noise: must be short-ish and not contain method words
                                    noise_words = {'regression', 'evaluated', 'adjusted', 'multivariable',
                                                   'confidence', 'interval', 'p-value', 'odds ratio',
                                                   'hazard ratio', 'analyzed', 'significantly', 'logistic'}
                                    if (5 < len(cleaned) < 60
                                            and not any(n in cleaned.lower() for n in noise_words)):
                                        section['risk_factors'].append(cleaned)

                    title_full = _flatten_text(article.get('title', ''))
                    pub_date = article.get('publication_date', '')
                    year = str(pub_date)[:4] if pub_date else ''
                    if title_full:
                        section['provenance'].append(
                            f"PubMed: '{title_full[:60]}...' ({year})"
                        )

        except Exception:
            pass

    # Deduplicate risk factors
    seen = set()
    unique_rf = []
    for rf in section['risk_factors']:
        rf_lower = rf.lower()
        if rf_lower not in seen:
            seen.add(rf_lower)
            unique_rf.append(rf)
    section['risk_factors'] = unique_rf[:8]

    tracker.complete_step("Demographics data collected")
    return section


# ─── Section: Trends ───────────────────────────────────────────
def _fetch_trends(
    disease: str,
    geography: str,
    datacommons_search,
    datacommons_observations,
    cdc_search,
    tracker,
) -> Dict[str, Any]:
    """Fetch 5-10 year prevalence and mortality trends."""
    section = {
        'prevalence_trend': [],
        'mortality_trend': [],
        'summary': '',
        'provenance': [],
    }

    tracker.start_step('trends', "Fetching trend data...")

    # --- DataCommons: time series ---
    if datacommons_search and datacommons_observations:
        try:
            tracker.update_step(0.2, "Searching Data Commons for trend indicators...")
            # Step 1: Find variable DCID
            dc_search_resp = _safe_call(
                datacommons_search,
                query=f"{disease} prevalence",
                places=["United States"] if geography.upper() == 'US' else None,
                include_topics=False,
            )

            if dc_search_resp and isinstance(dc_search_resp, dict):
                variables = dc_search_resp.get('variables', [])
                name_map = dc_search_resp.get('dcid_name_mappings', {})

                # Try multiple variables until one returns time series data
                for var_info in variables[:3]:
                    if section['prevalence_trend']:
                        break  # already got data from a previous variable
                    var_dcid = var_info.get('dcid', '')
                    places_with_data = var_info.get('places_with_data', [])

                    # Use first available place DCID
                    place_dcid = None
                    if geography.upper() == 'US':
                        # Look for US-level place
                        for p in places_with_data:
                            if 'country/USA' in str(p) or p == 'country/USA':
                                place_dcid = p
                                break
                        if not place_dcid and places_with_data:
                            place_dcid = places_with_data[0]
                    elif places_with_data:
                        place_dcid = places_with_data[0]

                    if not (var_dcid and place_dcid):
                        continue

                    tracker.update_step(0.5, "Fetching time series from Data Commons...")
                    # Try date='all' first, fallback to 'latest'
                    for date_param in ('all', 'latest'):
                        obs_resp = _safe_call(
                            datacommons_observations,
                            variable_dcid=var_dcid,
                            place_dcid=place_dcid,
                            date=date_param,
                        )

                        if obs_resp and isinstance(obs_resp, dict):
                            # DataCommons: {place_observations: [{time_series: [[date_str, val], ...]}]}
                            place_obs = obs_resp.get('place_observations', [])
                            if place_obs and isinstance(place_obs, list) and len(place_obs) > 0:
                                time_series = place_obs[0].get('time_series', [])
                                if time_series and isinstance(time_series, list):
                                    for entry in time_series:
                                        if isinstance(entry, (list, tuple)) and len(entry) >= 2:
                                            section['prevalence_trend'].append({
                                                'year': str(entry[0])[:4],
                                                'value': entry[1],
                                            })
                                    # Sort ascending by year (DC returns descending)
                                    section['prevalence_trend'].sort(key=lambda x: x['year'])
                                    # Keep last 10
                                    section['prevalence_trend'] = section['prevalence_trend'][-10:]
                        if section['prevalence_trend']:
                            # Calculate year-over-year changes
                            for i in range(1, len(section['prevalence_trend'])):
                                try:
                                    curr = float(section['prevalence_trend'][i]['value'])
                                    prev = float(section['prevalence_trend'][i - 1]['value'])
                                    if prev != 0:
                                        change_pct = ((curr - prev) / prev) * 100
                                        arrow = '+' if change_pct > 0 else ''
                                        section['prevalence_trend'][i]['change'] = f"{arrow}{change_pct:.1f}%"
                                except (ValueError, TypeError):
                                    pass

                            var_name = name_map.get(var_dcid, var_dcid)
                            section['provenance'].append(
                                f"Data Commons: {var_name} time series for {name_map.get(place_dcid, place_dcid)}"
                            )
                            break  # got data, stop trying date params

        except Exception as e:
            section['error'] = str(e)

    # --- Generate summary ---
    if section['prevalence_trend']:
        try:
            first = float(section['prevalence_trend'][0]['value'])
            last = float(section['prevalence_trend'][-1]['value'])
            years = len(section['prevalence_trend'])
            if first != 0:
                total_change = ((last - first) / first) * 100
                direction = "increased" if total_change > 0 else "decreased"
                section['summary'] = (
                    f"Over {years} data points, prevalence {direction} by "
                    f"{abs(total_change):.1f}% (from {first} to {last})"
                )
        except (ValueError, TypeError):
            pass

    tracker.complete_step("Trend data collected")
    return section


# ─── Drug name extraction helpers ─────────────────────────────
# Expanded INN-stem regex covering major drug classes:
# -mab (antibodies), -nib (kinase inhibitors), -tide (peptides),
# -gliptin (DPP-4), -flozin (SGLT2), -sartan (ARBs), -pril (ACE-i),
# -olol (beta blockers), -statin (HMG-CoA), -prazole (PPIs),
# -cycline (tetracyclines), -cillin (penicillins), -mycin (macrolides),
# -vir (antivirals), -ium (respiratory/anesthesia), -terol (bronchodilators),
# -sonide (corticosteroids), -ast (leukotriene), -ifen (SERMs),
# -azole (antifungals), -oxetine (SSRIs), -dipine (CCBs),
# -formin (biguanides), -semide (loop diuretics)
_DRUG_STEM_RE = re.compile(
    r'\b(\w+(?:mab|nib|lib|tide|gliptin|flozin|sartan|pril|olol'
    r'|statin|prazole|cycline|cillin|mycin|vir|ximab|zumab'
    r'|tinib|lisib|rafenib|ciclib|parin|glutide|reotide'
    r'|ium|terol|sonide|ifen|azole|oxetine|dipine'
    r'|formin|semide|lukast|tadine|setron|vaptan|rizine))\b',
    re.IGNORECASE,
)
# Words that match INN stems but are NOT drug names
_DRUG_FALSE_POSITIVES = {
    'april', 'contrast', 'forum', 'medium', 'premium', 'stadium', 'calcium',
    'sodium', 'potassium', 'magnesium', 'aluminum', 'lithium', 'helium',
    'podium', 'radium', 'barium', 'opium', 'consortium', 'symposium',
    'compendium', 'petroleum', 'equilibrium', 'criterion', 'bacterium',
    'fast', 'last', 'past', 'vast', 'cast', 'mast', 'blast', 'forecast',
    'contrast', 'breakfast',
    # Non-drug nouns that match INN stems
    'peptide', 'polypeptide', 'protein', 'bastide', 'belgium', 'delirium',
    'selenium', 'cystatin', 'gelatin', 'keratin', 'chitin', 'satin',
    'bulletin',
}

# Common drugs not caught by INN stems (established generics)
_COMMON_DISEASE_DRUGS = {
    'diabetes': ['metformin', 'insulin', 'glipizide', 'glyburide', 'pioglitazone'],
    'breast cancer': ['tamoxifen', 'letrozole', 'anastrozole', 'paclitaxel', 'trastuzumab', 'palbociclib'],
    'lung cancer': ['pembrolizumab', 'nivolumab', 'osimertinib', 'carboplatin', 'pemetrexed'],
    'colorectal cancer': ['fluorouracil', 'oxaliplatin', 'bevacizumab', 'cetuximab', 'irinotecan'],
    'prostate cancer': ['enzalutamide', 'abiraterone', 'leuprolide', 'docetaxel', 'apalutamide'],
    'copd': ['tiotropium', 'albuterol', 'ipratropium', 'roflumilast', 'theophylline'],
    'asthma': ['albuterol', 'montelukast', 'theophylline', 'ipratropium', 'fluticasone'],
    'hypertension': ['amlodipine', 'lisinopril', 'losartan', 'metoprolol', 'hydrochlorothiazide'],
    'heart disease': ['aspirin', 'clopidogrel', 'warfarin', 'nitroglycerin', 'metoprolol'],
    'heart failure': ['sacubitril', 'enalapril', 'carvedilol', 'spironolactone', 'furosemide'],
    'depression': ['sertraline', 'fluoxetine', 'escitalopram', 'venlafaxine', 'bupropion'],
    'anxiety': ['sertraline', 'escitalopram', 'buspirone', 'duloxetine', 'venlafaxine'],
    'schizophrenia': ['risperidone', 'olanzapine', 'aripiprazole', 'clozapine', 'quetiapine'],
    'epilepsy': ['levetiracetam', 'lamotrigine', 'valproate', 'carbamazepine', 'phenytoin'],
    'parkinson': ['levodopa', 'carbidopa', 'pramipexole', 'ropinirole', 'rasagiline'],
    'hiv': ['tenofovir', 'emtricitabine', 'dolutegravir', 'lamivudine', 'efavirenz'],
    'alzheimer': ['donepezil', 'memantine', 'rivastigmine', 'galantamine', 'lecanemab'],
    'obesity': ['phentermine', 'orlistat', 'naltrexone', 'semaglutide', 'tirzepatide'],
    'rheumatoid arthritis': ['methotrexate', 'adalimumab', 'etanercept', 'tofacitinib', 'hydroxychloroquine'],
    'multiple sclerosis': ['ocrelizumab', 'dimethyl fumarate', 'fingolimod', 'natalizumab', 'glatiramer'],
    'crohn': ['infliximab', 'adalimumab', 'vedolizumab', 'ustekinumab', 'azathioprine'],
    'ulcerative colitis': ['mesalamine', 'infliximab', 'adalimumab', 'vedolizumab', 'tofacitinib'],
    'psoriasis': ['adalimumab', 'secukinumab', 'ustekinumab', 'apremilast', 'methotrexate'],
    'lupus': ['hydroxychloroquine', 'belimumab', 'mycophenolate', 'azathioprine', 'prednisone'],
    'gout': ['allopurinol', 'febuxostat', 'colchicine', 'probenecid'],
    'osteoporosis': ['alendronate', 'denosumab', 'zoledronic acid', 'teriparatide', 'raloxifene'],
    'migraine': ['sumatriptan', 'erenumab', 'fremanezumab', 'topiramate', 'propranolol'],
    # Rare diseases
    'huntington': ['tetrabenazine', 'deutetrabenazine', 'valbenazine'],
    'amyotrophic lateral sclerosis': ['riluzole', 'edaravone', 'tofersen'],
    'als': ['riluzole', 'edaravone', 'tofersen'],
    'sickle cell': ['hydroxyurea', 'voxelotor', 'crizanlizumab', 'l-glutamine'],
    'cystic fibrosis': ['ivacaftor', 'lumacaftor', 'tezacaftor', 'elexacaftor'],
    'hemophilia': ['emicizumab', 'fitusiran', 'valoctocogene'],
    'spinal muscular atrophy': ['nusinersen', 'onasemnogene', 'risdiplam'],
    # Infectious diseases
    'tuberculosis': ['isoniazid', 'rifampicin', 'pyrazinamide', 'ethambutol', 'bedaquiline'],
    'malaria': ['artemisinin', 'chloroquine', 'atovaquone', 'mefloquine', 'primaquine'],
    'hepatitis c': ['sofosbuvir', 'ledipasvir', 'velpatasvir', 'glecaprevir', 'pibrentasvir'],
    'hepatitis b': ['tenofovir', 'entecavir', 'lamivudine'],
    'influenza': ['oseltamivir', 'baloxavir', 'zanamivir', 'peramivir'],
}


def _extract_drugs_from_text(text: str, section: dict):
    """Extract drug names from text using INN-stem regex."""
    found_drugs = set()
    for m in _DRUG_STEM_RE.finditer(text):
        name = m.group(1).strip().title()
        name_lower = name.lower()
        if (len(name) > 4 and name_lower not in found_drugs
                and name_lower not in _DRUG_FALSE_POSITIVES):
            found_drugs.add(name_lower)
            existing = {d['name'].lower() for d in section['drugs']}
            if name_lower not in existing:
                section['drugs'].append({
                    'name': name,
                    'status': 'Approved',
                    'notes': '',
                })
    if found_drugs:
        section['provenance'].append(
            f"Text extraction: {len(found_drugs)} drugs via INN stem matching"
        )


def _add_common_drugs_fallback(disease: str, section: dict):
    """Add well-known drugs for common diseases when other sources return empty."""
    disease_lower = disease.lower()
    existing = {d['name'].lower() for d in section['drugs']}
    added = 0
    for key, drugs in _COMMON_DISEASE_DRUGS.items():
        if key in disease_lower:
            for drug in drugs:
                if drug not in existing:
                    existing.add(drug)
                    section['drugs'].append({
                        'name': drug.title(),
                        'status': 'Approved',
                        'notes': 'Common treatment',
                    })
                    added += 1
            break
    if added:
        section['provenance'].append(f"Known drugs fallback: {added} common treatments added")


# ─── Section: Treatment Landscape ──────────────────────────────
def _fetch_treatment_landscape(
    disease: str,
    pubmed_search,
    fda_search,
    opentargets_search,
    tracker,
) -> Dict[str, Any]:
    """Fetch current standard of care, approved drugs, treatment guidelines."""
    section = {
        'standard_of_care': '',
        'drugs': [],
        'guidelines': [],
        'provenance': [],
    }

    tracker.start_step('treatment_landscape', "Fetching treatment landscape...")

    # --- Common drugs: seed with well-known treatments first ---
    # Run early so these anchor the list; OpenTargets/PubMed supplement rather than dominate
    _add_common_drugs_fallback(disease, section)

    # --- FDA: Approved drugs for this indication ---
    # FDA lookup_drug takes search_term (not query), search_type, and count.
    # For 'general' search, count is MANDATORY or response exceeds token limit.
    if fda_search:
        try:
            tracker.update_step(0.2, "Querying FDA for approved drugs...")
            fda_resp = _safe_call(
                fda_search,
                search_term=disease,
                search_type='general',
                count='openfda.brand_name.exact',
                limit=25,
            )
            if fda_resp and isinstance(fda_resp, dict):
                results = fda_resp.get('results', [])
                if isinstance(results, list):
                    for item in results[:15]:
                        # Count-mode returns {term: "DRUGNAME", count: N}
                        drug_name = item.get('term', '')
                        if not drug_name or len(drug_name) < 3 or len(drug_name) > 60:
                            continue
                        drug_name = drug_name.strip().title()
                        existing = {d['name'].lower() for d in section['drugs']}
                        if drug_name.lower() not in existing:
                            section['drugs'].append({
                                'name': drug_name,
                                'status': 'FDA Approved',
                                'notes': '',
                            })
                    section['provenance'].append(
                        f"FDA openFDA: {len(results)} brand names for '{disease}'"
                    )
            elif fda_resp and isinstance(fda_resp, str):
                # FDA MCP may return markdown text — extract drug names
                _extract_drugs_from_text(fda_resp, section)
        except Exception:
            pass

    # --- PubMed: Treatment guidelines and drug mentions ---
    if pubmed_search:
        try:
            tracker.update_step(0.5, "Searching PubMed for treatment guidelines...")
            pm_resp = _safe_call(
                pubmed_search,
                query=f"{disease} treatment guidelines standard of care review",
                num_results=5,
            )

            articles = []
            if isinstance(pm_resp, dict):
                articles = pm_resp.get('articles', [])
            elif isinstance(pm_resp, list):
                articles = pm_resp

            # Build disease keywords for title relevance check
            disease_keywords = [w.lower() for w in disease.lower().split() if len(w) > 3]

            for article in articles:
                title = _flatten_text(article.get('title', ''))
                abstract = _flatten_text(article.get('abstract', ''))
                pub_date = article.get('publication_date', '')
                year = str(pub_date)[:4] if pub_date else ''
                journal = article.get('journal', '')
                pmid = article.get('pmid', '')

                # Check title relevance — skip off-topic articles entirely
                title_lower = title.lower() if title else ''
                title_relevant = any(kw in title_lower for kw in disease_keywords) if disease_keywords else True

                if title and title_relevant:
                    section['guidelines'].append({
                        'title': title,
                        'source': f"{journal} ({year})" if journal else year,
                        'pmid': pmid,
                    })
                if abstract and title_relevant:
                    existing = {d['name'].lower() for d in section['drugs']}
                    for m in _DRUG_STEM_RE.finditer(abstract):
                        drug_name = m.group(1).strip().title()
                        dn_lower = drug_name.lower()
                        if (len(drug_name) > 4 and dn_lower not in existing
                                and dn_lower not in _DRUG_FALSE_POSITIVES):
                            existing.add(dn_lower)
                            section['drugs'].append({
                                'name': drug_name,
                                'status': 'Approved',
                                'notes': f'From PubMed ({year})',
                            })

                if title and title_relevant:
                    section['provenance'].append(
                        f"PubMed PMID:{pmid}: '{title[:50]}...' ({year})"
                    )

            # Extract standard of care from first relevant article abstract
            relevant_articles = [a for a in articles if any(
                kw in _flatten_text(a.get('title', '')).lower()
                for kw in disease_keywords
            )] if disease_keywords else articles
            if relevant_articles:
                first_abstract = _flatten_text(relevant_articles[0].get('abstract', ''))
                if first_abstract:
                    soc_patterns = [
                        r'standard of care\s+(?:is|includes|remains)\s+([^.]+)',
                        r'first[- ]line\s+(?:treatment|therapy)\s+(?:is|includes|involves)\s+([^.]+)',
                        r'(?:current|recommended|guideline)\s+(?:treatment|therapy)\s+(?:is|includes|involves|recommends?)\s+([^.]+)',
                        r'(?:mainstay|cornerstone)\s+of\s+(?:treatment|therapy)\s+(?:is|includes|remains)\s+([^.]+)',
                    ]
                    for pattern in soc_patterns:
                        soc_match = re.search(pattern, first_abstract, re.IGNORECASE)
                        if soc_match:
                            section['standard_of_care'] = soc_match.group(1).strip()[:200]
                            break

        except Exception as e:
            section['error'] = str(e)

    # --- OpenTargets: known drugs via disease→targets→knownDrugs chain ---
    if opentargets_search and len(section['drugs']) < 5:
        try:
            tracker.update_step(0.7, "Querying OpenTargets for known drugs...")

            # Step 1: Search for disease ID
            # Response format: {data: {search: {hits: [{id, name, ...}]}}}
            disease_resp = _safe_call(
                opentargets_search,
                method='search_diseases',
                query=disease,
                size=3,
            )
            disease_id = None
            if disease_resp and isinstance(disease_resp, dict):
                # Navigate nested structure: data.search.hits[]
                hits = disease_resp.get('data', {})
                if isinstance(hits, dict):
                    hits = hits.get('search', {}).get('hits', [])
                if isinstance(hits, list) and hits:
                    disease_id = hits[0].get('id')

            if disease_id:
                # Step 2: Get top associated targets
                # Response format: {targets: [{targetId, targetSymbol, ...}]}
                targets_resp = _safe_call(
                    opentargets_search,
                    method='get_disease_targets_summary',
                    diseaseId=disease_id,
                    minScore=0.5,
                    size=5,
                )
                target_ids = []
                if targets_resp and isinstance(targets_resp, dict):
                    targets_list = targets_resp.get('targets', targets_resp.get('data', []))
                    if isinstance(targets_list, list):
                        for assoc in targets_list[:5]:
                            tid = assoc.get('targetId') or assoc.get('target', {}).get('id')
                            if tid:
                                target_ids.append(tid)

                # Step 3: Get knownDrugs from each target (sequentially — MCP not thread-safe)
                # Response format: {data: {target: {knownDrugs: {rows: [...]}}}}
                all_drugs = {}  # drugId -> {name, phase, moa}
                for tid in target_ids[:3]:  # Limit to 3 targets to avoid slow calls
                    target_resp = _safe_call(
                        opentargets_search,
                        method='get_target_details',
                        id=tid,
                        timeout_sec=45,
                    )
                    if not target_resp or not isinstance(target_resp, dict):
                        continue

                    # Navigate: data.target.knownDrugs (or top-level knownDrugs)
                    known_drugs = target_resp.get('knownDrugs', {})
                    if not known_drugs:
                        nested = target_resp.get('data', {})
                        if isinstance(nested, dict):
                            nested = nested.get('target', nested)
                            if isinstance(nested, dict):
                                known_drugs = nested.get('knownDrugs', {})
                    rows = known_drugs.get('rows', []) if isinstance(known_drugs, dict) else []
                    for row in rows:
                        drug_id = row.get('drugId', '')
                        pref_name = row.get('prefName', '')
                        phase = row.get('phase', 0)
                        moa = row.get('mechanismOfAction', '')
                        if not pref_name or len(pref_name) < 3:
                            continue
                        # Keep highest phase per drug
                        if drug_id not in all_drugs or phase > all_drugs[drug_id].get('phase', 0):
                            all_drugs[drug_id] = {
                                'name': pref_name.strip().title(),
                                'phase': phase,
                                'moa': moa,
                            }

                # Add to section (dedup against existing)
                existing = {d['name'].lower() for d in section['drugs']}
                common_count = len([d for d in section['drugs'] if d.get('notes') == 'Common treatment'])
                # If common drugs already anchored the list, only add approved (phase 4) drugs
                # and cap supplemental additions to avoid off-target noise
                only_approved = common_count >= 3
                max_ot_additions = 3 if common_count >= 3 else 7
                ot_added = 0
                # Sort by phase descending (approved drugs first)
                for drug_info in sorted(all_drugs.values(), key=lambda x: x['phase'], reverse=True):
                    if ot_added >= max_ot_additions:
                        break
                    name = drug_info['name']
                    if name.lower() in existing:
                        continue
                    # Skip non-approved drugs when common drugs already provide a solid base
                    if only_approved and drug_info['phase'] < 4:
                        continue
                    # Skip obviously irrelevant multi-word salt forms (e.g., "Benzphetamine Hydrochloride")
                    if len(name.split()) > 2:
                        continue
                    status = 'Approved' if drug_info['phase'] >= 4 else f"Phase {drug_info['phase']}"
                    notes = drug_info['moa'][:80] if drug_info['moa'] else 'From OpenTargets'
                    section['drugs'].append({
                        'name': name,
                        'status': status,
                        'notes': notes,
                    })
                    existing.add(name.lower())
                    ot_added += 1
                    if len(section['drugs']) >= 10:
                        break

                if ot_added:
                    section['provenance'].append(
                        f"OpenTargets: {ot_added} drugs via disease '{disease_id}' → {len(target_ids)} targets"
                    )
        except Exception:
            pass

    tracker.complete_step("Treatment landscape collected")
    return section


# ─── Section: Unmet Need ───────────────────────────────────────
def _fetch_unmet_need(
    disease: str,
    ctgov_search,
    pubmed_search,
    tracker,
) -> Dict[str, Any]:
    """Assess unmet need via trial activity and literature."""
    section = {
        'trial_activity': {},
        'unmet_need_score': None,
        'justification': [],
        'treatment_gaps': [],
        'provenance': [],
    }

    tracker.start_step('unmet_need', "Assessing unmet need...")

    # --- CT.gov: Active trial count as proxy for unmet need ---
    total_recruiting = 0
    by_phase = {}

    if ctgov_search:
        try:
            tracker.update_step(0.3, "Querying ClinicalTrials.gov...")
            ct_resp = _safe_call(
                ctgov_search,
                condition=disease,
                status='RECRUITING',
            )
            if ct_resp:
                # CT.gov returns markdown text — parse for trial count
                text = ''
                if isinstance(ct_resp, str):
                    text = ct_resp
                elif isinstance(ct_resp, dict):
                    text = ct_resp.get('content', '') or str(ct_resp)

                # Extract total from "X of Y studies found" line
                # CT.gov MCP returns markdown: "**Results:** 5 of 2,454 studies found"
                total_match = re.search(r'of\s+([\d,]+)\s+studies?\s+found', text, re.IGNORECASE)
                if total_match:
                    total_recruiting = int(total_match.group(1).replace(',', ''))
                else:
                    # Fallback: count NCT IDs (capped at pageSize)
                    nct_ids = re.findall(r'NCT\d{8}', text)
                    total_recruiting = len(set(nct_ids))

                # Count by phase
                phase_patterns = {
                    'Phase 1': r'(?:Phase\s*1|PHASE1)',
                    'Phase 2': r'(?:Phase\s*2|PHASE2)',
                    'Phase 3': r'(?:Phase\s*3|PHASE3)',
                    'Phase 4': r'(?:Phase\s*4|PHASE4)',
                }
                for phase_name, pattern in phase_patterns.items():
                    count = len(re.findall(pattern, text, re.IGNORECASE))
                    if count > 0:
                        by_phase[phase_name] = count

                section['trial_activity'] = {
                    'total_recruiting': total_recruiting,
                    'by_phase': by_phase,
                }
                section['provenance'].append(
                    f"ClinicalTrials.gov: {total_recruiting} recruiting trials for '{disease}'"
                )

        except Exception as e:
            section['error'] = str(e)

    # --- PubMed: unmet need literature ---
    if pubmed_search:
        try:
            tracker.update_step(0.6, "Searching PubMed for unmet need literature...")
            pm_resp = _safe_call(
                pubmed_search,
                query=f"{disease} unmet need treatment gap 2024 2025",
                num_results=3,
            )

            articles = []
            if isinstance(pm_resp, dict):
                articles = pm_resp.get('articles', [])
            elif isinstance(pm_resp, list):
                articles = pm_resp

            for article in articles:
                abstract = _flatten_text(article.get('abstract', ''))
                if abstract:
                    # Extract unmet need statements
                    gap_patterns = [
                        r'unmet\s+(?:medical\s+)?need[s]?\s+(?:include|are|remain)\s+([^.]+)',
                        r'treatment\s+gap[s]?\s+(?:include|are|remain)\s+([^.]+)',
                        r'(?:lack|absence)\s+of\s+(?:effective\s+)?([^.]+)',
                        r'(?:no|limited)\s+(?:effective\s+)?(?:treatment|therapy)\s+(?:for|exists)\s*([^.]*)',
                    ]
                    for pattern in gap_patterns:
                        matches = re.findall(pattern, abstract, re.IGNORECASE)
                        for match in matches[:2]:
                            cleaned = match.strip()[:150]
                            if len(cleaned) > 15:
                                section['treatment_gaps'].append(cleaned)

                title = _flatten_text(article.get('title', ''))
                pmid = article.get('pmid', '')
                if title:
                    section['provenance'].append(
                        f"PubMed PMID:{pmid}: '{title[:50]}...'"
                    )

        except Exception:
            pass

    # --- Calculate unmet need score (1-10) ---
    score = 5  # Base score
    justification = []

    if total_recruiting > 100:
        score += 2
        justification.append(f"High trial activity ({total_recruiting} recruiting trials)")
    elif total_recruiting > 50:
        score += 1
        justification.append(f"Moderate trial activity ({total_recruiting} recruiting trials)")
    elif total_recruiting < 10:
        score -= 1
        justification.append(f"Low trial activity ({total_recruiting} recruiting trials)")

    phase3_count = by_phase.get('Phase 3', 0)
    if phase3_count > 10:
        score += 1
        justification.append(f"Many Phase 3 trials ({phase3_count}) suggest active competition")

    if section['treatment_gaps']:
        score += 1
        justification.append(f"Literature identifies {len(section['treatment_gaps'])} treatment gaps")

    section['unmet_need_score'] = max(1, min(10, score))
    section['justification'] = justification

    tracker.complete_step("Unmet need assessment complete")
    return section


# ─── Section: Economic Burden ──────────────────────────────────
def _fetch_economic_burden(
    disease: str,
    geography: str,
    medicaid_info,
    pubmed_search,
    tracker,
    treatment_drugs: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Fetch economic burden: direct/indirect costs, Medicaid utilization spending.

    Args:
        medicaid_info: Medicaid MCP function (get_drug_utilization for spending).
        treatment_drugs: Drug names from treatment landscape.
    """
    section = {
        'total_cost': {},
        'direct_costs': {},
        'indirect_costs': {},
        'per_patient_cost': {},
        'medicaid_spending': {},
        'provenance': [],
    }

    tracker.start_step('economic_burden', "Fetching economic burden data...")

    # --- Medicaid: drug utilization spending ---
    # Medicaid get_drug_utilization returns per-state, per-NDC spending data
    # with total_amount_reimbursed, number_of_prescriptions fields.
    if medicaid_info and geography.upper() in ('US', 'GLOBAL'):
        try:
            tracker.update_step(0.2, "Querying Medicaid drug utilization...")

            drug_queries = []
            if treatment_drugs:
                drug_queries.extend(treatment_drugs[:5])

            total_spend = 0
            total_rxs = 0
            drug_spending_details = []

            for drug_name in drug_queries[:5]:
                med_resp = _safe_call(
                    medicaid_info,
                    method='get_drug_utilization',
                    drug_name=drug_name,
                    limit=200,
                    timeout_sec=90,
                )

                if med_resp and isinstance(med_resp, dict):
                    records = med_resp.get('data', [])
                    if isinstance(records, list) and records:
                        drug_spend = 0
                        drug_rxs = 0
                        for rec in records:
                            amt = rec.get('total_amount_reimbursed')
                            rxs = rec.get('number_of_prescriptions')
                            if amt is not None:
                                try:
                                    drug_spend += float(amt)
                                except (ValueError, TypeError):
                                    pass
                            if rxs is not None:
                                try:
                                    drug_rxs += int(float(rxs))
                                except (ValueError, TypeError):
                                    pass
                        if drug_spend > 0:
                            total_spend += drug_spend
                            total_rxs += drug_rxs
                            drug_spending_details.append({
                                'drug': drug_name.title(),
                                'spending': drug_spend,
                                'prescriptions': drug_rxs,
                            })

            if total_spend > 0:
                section['medicaid_spending'] = {
                    'total_spending': total_spend,
                    'total_prescriptions': total_rxs if total_rxs else None,
                    'top_drugs': sorted(drug_spending_details, key=lambda x: x['spending'], reverse=True)[:5],
                }
                if total_rxs > 0:
                    section['per_patient_cost'] = {
                        'value': total_spend / total_rxs,
                        'source': 'Medicaid (per prescription, estimated)',
                    }
                section['provenance'].append(
                    f"Medicaid Drug Utilization: spending for {len(drug_spending_details)} drugs related to {disease}"
                )

        except Exception as e:
            section['error'] = str(e)

    # --- Medicaid NADAC: acquisition pricing for treatment drugs ---
    if medicaid_info and treatment_drugs and geography.upper() in ('US', 'GLOBAL'):
        try:
            tracker.update_step(0.4, "Querying NADAC acquisition pricing...")
            nadac_prices = []
            for drug_name in treatment_drugs[:3]:
                nadac_resp = _safe_call(
                    medicaid_info,
                    method='get_nadac_pricing',
                    drug_name=drug_name,
                    limit=5,
                    timeout_sec=60,
                )
                if nadac_resp and isinstance(nadac_resp, dict):
                    records = nadac_resp.get('data', [])
                    if isinstance(records, list) and records:
                        seen_descs = {p['drug'] for p in nadac_prices}
                        for rec in records[:2]:
                            desc = rec.get('description', drug_name)[:50]
                            price = rec.get('nadac_per_unit')
                            unit = rec.get('pricing_unit', '')
                            if price is not None and desc not in seen_descs:
                                seen_descs.add(desc)
                                nadac_prices.append({
                                    'drug': desc,
                                    'price_per_unit': float(price),
                                    'unit': unit,
                                })
            if nadac_prices:
                section['nadac_pricing'] = nadac_prices
                section['provenance'].append(
                    f"Medicaid NADAC: acquisition pricing for {len(nadac_prices)} formulations"
                )
        except Exception:
            pass

    # --- PubMed: economic burden literature ---
    if pubmed_search:
        try:
            tracker.update_step(0.6, "Searching PubMed for economic burden...")
            pm_resp = _safe_call(
                pubmed_search,
                query=f'"{disease}" economic burden cost United States',
                num_results=5,
            )

            articles = []
            if isinstance(pm_resp, dict):
                articles = pm_resp.get('articles', [])
            elif isinstance(pm_resp, list):
                articles = pm_resp

            for article in articles:
                abstract = _flatten_text(article.get('abstract', ''))
                if abstract:
                    # Extract cost figures from abstracts — multiple patterns
                    cost_patterns = [
                        # "$327 billion", "$1.2 trillion"
                        r'\$\s*([\d,.]+)\s*(billion|million|trillion)',
                        # "327 billion dollars"
                        r'([\d,.]+)\s*(billion|million|trillion)\s*(?:dollars|\$|USD)',
                        # "cost of $12,345 per patient"
                        r'(?:cost|expenditure|spending)\s+(?:of\s+)?\$\s*([\d,.]+)\s*(?:per|/)\s*(?:patient|person|capita|year|annum)',
                        # "$12,345 per patient per year"
                        r'\$\s*([\d,.]+)\s*(?:per|/)\s*(?:patient|person|capita)',
                    ]
                    for pattern in cost_patterns:
                        matches = re.findall(pattern, abstract, re.IGNORECASE)
                        for match in matches:
                            try:
                                if isinstance(match, tuple):
                                    amount_str = match[0]
                                    unit = match[1] if len(match) > 1 else ''
                                else:
                                    amount_str = match
                                    unit = ''
                                amount = float(amount_str.replace(',', ''))
                                unit_lower = unit.lower() if unit else ''
                                if unit_lower == 'trillion':
                                    amount *= 1_000_000_000_000
                                elif unit_lower == 'billion':
                                    amount *= 1_000_000_000
                                elif unit_lower == 'million':
                                    amount *= 1_000_000

                                # Assign to most appropriate bucket
                                idx = abstract.find(amount_str)
                                context = abstract[max(0, idx - 80):idx + 80].lower()

                                # Per-patient costs (no multiplier applied)
                                if 'per patient' in context or 'per person' in context or 'per capita' in context:
                                    if not section['per_patient_cost'].get('value'):
                                        section['per_patient_cost'] = {
                                            'value': amount,
                                            'source': 'PubMed literature',
                                        }
                                elif 'direct' in context:
                                    if not section['direct_costs'].get('value'):
                                        section['direct_costs'] = {'value': amount, 'source': 'PubMed literature'}
                                elif 'indirect' in context or 'productivity' in context:
                                    if not section['indirect_costs'].get('value'):
                                        section['indirect_costs'] = {'value': amount, 'source': 'PubMed literature'}
                                else:
                                    if not section['total_cost'].get('value'):
                                        pub_date = article.get('publication_date', '')
                                        year = str(pub_date)[:4] if pub_date else ''
                                        section['total_cost'] = {
                                            'value': amount,
                                            'year': year,
                                            'source': 'PubMed literature',
                                        }
                            except (ValueError, TypeError):
                                pass

                title = _flatten_text(article.get('title', ''))
                pmid = article.get('pmid', '')
                if title:
                    section['provenance'].append(
                        f"PubMed PMID:{pmid}: '{title[:50]}...'"
                    )

        except Exception:
            pass

    tracker.complete_step("Economic burden data collected")
    return section


# ─── Section: Global Comparison ────────────────────────────────
# ─── Curated WHO indicator codes ──────────────────────────────
# Maps disease keywords to known WHO GHO indicator codes.
# Bypasses unreliable keyword search for top diseases.
# Format: {keyword: [(indicator_code, indicator_name, column_key), ...]}
WHO_INDICATOR_MAP = {
    'diabetes': [
        ('NCD_GLUC_04', 'Age-standardized prevalence of raised fasting blood glucose among adults', 'prevalence'),
        ('NCDMORT3070', 'Probability of dying from NCDs between 30-70', 'mortality'),
        ('WHS2_131', 'Age-standardized DALYs, diabetes mellitus, per 100,000', 'dalys'),
    ],
    'cancer': [
        ('WHS2_131', 'Age-standardized DALYs, malignant neoplasms, per 100,000', 'dalys'),
        ('NCDMORT3070', 'Probability of dying from NCDs between 30-70', 'mortality'),
    ],
    'breast cancer': [
        ('WHS2_131', 'Age-standardized DALYs, malignant neoplasms, per 100,000', 'dalys'),
    ],
    'copd': [
        ('WHS2_131', 'Age-standardized DALYs, chronic respiratory diseases, per 100,000', 'dalys'),
        ('NCDMORT3070', 'Probability of dying from NCDs between 30-70', 'mortality'),
    ],
    'asthma': [
        ('WHS2_131', 'Age-standardized DALYs, chronic respiratory diseases, per 100,000', 'dalys'),
    ],
    'heart disease': [
        ('WHS2_131', 'Age-standardized DALYs, cardiovascular diseases, per 100,000', 'dalys'),
        ('NCDMORT3070', 'Probability of dying from NCDs between 30-70', 'mortality'),
    ],
    'hypertension': [
        ('BP_04', 'Age-standardized prevalence of raised blood pressure', 'prevalence'),
        ('WHS2_131', 'Age-standardized DALYs, cardiovascular diseases, per 100,000', 'dalys'),
    ],
    'hiv': [
        ('MDG_0000000001', 'HIV prevalence among adults (15-49)', 'prevalence'),
        ('WHS2_131', 'Age-standardized DALYs, HIV/AIDS, per 100,000', 'dalys'),
    ],
    'malaria': [
        ('MALARIA_EST_INCIDENCE', 'Estimated malaria incidence per 1000', 'prevalence'),
        ('MALARIA_EST_DEATHS', 'Estimated malaria deaths', 'mortality'),
    ],
    'tuberculosis': [
        ('MDG_0000000020', 'Tuberculosis incidence per 100,000', 'prevalence'),
        ('MDG_0000000021', 'Tuberculosis death rate per 100,000', 'mortality'),
    ],
    'depression': [
        ('WHS2_131', 'Age-standardized DALYs, mental disorders, per 100,000', 'dalys'),
    ],
    'obesity': [
        ('NCD_BMI_30A', 'Age-standardized prevalence of obesity among adults', 'prevalence'),
    ],
    'kidney': [
        ('WHS2_131', 'Age-standardized DALYs, kidney diseases, per 100,000', 'dalys'),
    ],
    'stroke': [
        ('WHS2_131', 'Age-standardized DALYs, cardiovascular diseases, per 100,000', 'dalys'),
    ],
    'alzheimer': [
        ('WHS2_131', 'Age-standardized DALYs, neurological conditions, per 100,000', 'dalys'),
    ],
    'influenza': [
        ('WHS3_49', 'Influenza - number of laboratory-confirmed cases', 'prevalence'),
    ],
}


def _find_who_indicators(disease: str) -> list:
    """Find curated WHO indicator codes for a disease.

    Returns list of (code, name, column_key) tuples, or empty list if no match.
    """
    disease_lower = disease.lower()
    for keyword, indicators in WHO_INDICATOR_MAP.items():
        if keyword in disease_lower:
            return indicators
    return []


def _fetch_global_comparison(
    disease: str,
    geography: str,
    who_search,
    tracker,
) -> Dict[str, Any]:
    """Fetch global comparison metrics across regions."""
    section = {
        'regions': [],
        'notes': [],
        'provenance': [],
    }

    tracker.report("Fetching global comparison...")

    if not who_search:
        section['error'] = 'WHO MCP not available'
        return section

    try:
        # Step 1: Try curated indicator codes first (fast, reliable)
        curated = _find_who_indicators(disease)
        indicator_code = None
        indicator_name = None
        col_key = None

        if curated:
            # Use first curated indicator
            indicator_code, indicator_name, col_key = curated[0]
        else:
            # Step 2: Fall back to keyword search
            disease_keyword = _who_keyword(disease)
            who_indicators = _safe_call(
                who_search,
                method='search_indicators',
                keywords=disease_keyword,
            )

            if who_indicators and isinstance(who_indicators, dict):
                indicators = who_indicators.get('indicators', [])
                # Filter for numeric rate indicators (exclude policy/plan/existence indicators)
                policy_words = ('policy', 'plan', 'strategy', 'existence', 'operational',
                                'programme', 'guideline', 'legislation', 'survey', 'registry')
                rate_indicators = [
                    ind for ind in indicators
                    if any(w in (ind.get('name', '') or '').lower()
                           for w in ('rate', 'prevalence', 'incidence', 'per 100', 'mortality',
                                     'death', 'daly', 'burden', 'per 100 000', 'age-standardized'))
                    and not any(p in (ind.get('name', '') or '').lower() for p in policy_words)
                ]
                if not rate_indicators:
                    rate_indicators = [
                        ind for ind in indicators
                        if not any(p in (ind.get('name', '') or '').lower() for p in policy_words)
                    ]
                if not rate_indicators:
                    rate_indicators = indicators
                if rate_indicators:
                    indicator_code = rate_indicators[0].get('code', '')
                    indicator_name = rate_indicators[0].get('name', '')
                    # Detect column from indicator name
                    ind_name_lower = indicator_name.lower()
                    if 'daly' in ind_name_lower or 'disability' in ind_name_lower or 'burden' in ind_name_lower:
                        col_key = 'dalys'
                    elif 'death' in ind_name_lower or 'mortality' in ind_name_lower or 'mort' in ind_name_lower:
                        col_key = 'mortality'
                    else:
                        col_key = 'prevalence'

        if indicator_code:
            # Get data for key regions
            region_codes = {
                'US': 'USA',
                'UK': 'GBR',
                'Germany': 'DEU',
                'Japan': 'JPN',
                'Global': None,
            }

            for region_name, country_code in region_codes.items():
                filter_str = f"SpatialDim eq '{country_code}'" if country_code else None
                region_data = _safe_call(
                    who_search,
                    method='get_health_data',
                    indicator_code=indicator_code,
                    top=5,
                    filter=filter_str,
                )

                if region_data and isinstance(region_data, dict):
                    values = region_data.get('data', region_data.get('value', []))
                    if values:
                        # Take most recent value
                        latest = values[0]
                        for v in values:
                            v_time = v.get('time_dim', v.get('TimeDim')) or 0
                            l_time = latest.get('time_dim', latest.get('TimeDim')) or 0
                            if str(v_time) > str(l_time):
                                latest = v
                        num_val = latest.get('numeric_value', latest.get('NumericValue'))
                        if num_val is not None:
                            region_entry = {
                                'name': region_name,
                                'prevalence': 'N/A',
                                'mortality': 'N/A',
                                'dalys': 'N/A',
                            }
                            region_entry[col_key] = str(num_val)
                            section['regions'].append(region_entry)

            section['provenance'].append(
                f"WHO GHO: {indicator_name} ({indicator_code}) across regions"
            )
            section['notes'].append(
                f"Indicator: {indicator_name}"
            )

    except Exception as e:
        section['error'] = str(e)

    return section


# ─── Main Orchestrator ─────────────────────────────────────────
def get_disease_burden_analysis(
    disease: str,
    geography: str = "US",
    skip_treatments: bool = False,
    skip_economics: bool = False,
    mcp_funcs: Optional[Dict] = None,
    progress_callback=None,
) -> Dict[str, Any]:
    """
    Main orchestrator for disease burden analysis.

    Sequential execution of 7 sections, each with error tolerance.
    MCP client is NOT thread-safe, so sections run sequentially.

    Args:
        disease: Disease name to analyze (e.g., "type 2 diabetes")
        geography: Focus region - "US", "EU", or "global"
        skip_treatments: Skip treatment landscape section
        skip_economics: Skip economic burden section
        mcp_funcs: Dict of MCP functions (injected by server)
        progress_callback: Callback(percent, message)

    Returns:
        Comprehensive dict with all section data + ASCII visualization
    """
    if not disease:
        return {'error': 'disease is required'}

    if mcp_funcs is None:
        mcp_funcs = {}

    # Extract MCP functions
    cdc_search = mcp_funcs.get('cdc_search') or mcp_funcs.get('cdc_health_data')
    who_search = mcp_funcs.get('who_search')
    datacommons_search = mcp_funcs.get('datacommons_search')
    datacommons_observations = mcp_funcs.get('datacommons_observations')
    pubmed_search = mcp_funcs.get('pubmed_search')
    ctgov_search = mcp_funcs.get('ctgov_search')
    medicaid_info = mcp_funcs.get('medicaid_info')
    fda_search = mcp_funcs.get('fda_search')
    opentargets_search = mcp_funcs.get('opentargets_search')

    # Determine skipped sections for progress tracker
    skip_set = set()
    if skip_treatments:
        skip_set.add('treatment_landscape')
    if skip_economics:
        skip_set.add('economic_burden')

    tracker = create_progress_tracker(
        callback=progress_callback,
        skip_sections=skip_set,
    )

    result = {
        'disease': disease,
        'geography': geography,
        'epidemiology': {},
        'demographics': {},
        'trends': {},
        'treatment_landscape': {},
        'unmet_need': {},
        'economic_burden': {},
        'global_comparison': {},
        'visualization': '',
        'provenance': [],
        'errors': {},
    }

    # ============================================================
    # PHASE 1: Epidemiology
    # ============================================================
    try:
        result['epidemiology'] = _fetch_epidemiology(
            disease, geography, cdc_search, who_search, datacommons_search, tracker,
        )
        if result['epidemiology'].get('error'):
            result['errors']['epidemiology'] = result['epidemiology']['error']
    except Exception as e:
        result['errors']['epidemiology'] = str(e)
        print(f"  Warning: epidemiology failed: {e}")

    # ============================================================
    # PHASE 2: Demographics
    # ============================================================
    try:
        result['demographics'] = _fetch_demographics(
            disease, geography, cdc_search, pubmed_search, tracker,
        )
        if result['demographics'].get('error'):
            result['errors']['demographics'] = result['demographics']['error']
    except Exception as e:
        result['errors']['demographics'] = str(e)
        print(f"  Warning: demographics failed: {e}")

    # ============================================================
    # PHASE 3: Trends
    # ============================================================
    try:
        result['trends'] = _fetch_trends(
            disease, geography, datacommons_search, datacommons_observations,
            cdc_search, tracker,
        )
        if result['trends'].get('error'):
            result['errors']['trends'] = result['trends']['error']
    except Exception as e:
        result['errors']['trends'] = str(e)
        print(f"  Warning: trends failed: {e}")

    # ============================================================
    # PHASE 4: Treatment Landscape (skippable)
    # ============================================================
    if not skip_treatments:
        try:
            result['treatment_landscape'] = _fetch_treatment_landscape(
                disease, pubmed_search, fda_search, opentargets_search, tracker,
            )
            if result['treatment_landscape'].get('error'):
                result['errors']['treatment_landscape'] = result['treatment_landscape']['error']
        except Exception as e:
            result['errors']['treatment_landscape'] = str(e)
            print(f"  Warning: treatment_landscape failed: {e}")

    # ============================================================
    # PHASE 5: Unmet Need
    # ============================================================
    try:
        result['unmet_need'] = _fetch_unmet_need(
            disease, ctgov_search, pubmed_search, tracker,
        )
        if result['unmet_need'].get('error'):
            result['errors']['unmet_need'] = result['unmet_need']['error']
    except Exception as e:
        result['errors']['unmet_need'] = str(e)
        print(f"  Warning: unmet_need failed: {e}")

    # ============================================================
    # PHASE 6: Economic Burden (skippable)
    # ============================================================
    if not skip_economics:
        try:
            # Pass drug names from treatment landscape to improve Medicaid queries
            treatment_drugs = [d['name'] for d in result.get('treatment_landscape', {}).get('drugs', [])[:5]]
            result['economic_burden'] = _fetch_economic_burden(
                disease, geography, medicaid_info, pubmed_search, tracker,
                treatment_drugs=treatment_drugs,
            )
            if result['economic_burden'].get('error'):
                result['errors']['economic_burden'] = result['economic_burden']['error']
        except Exception as e:
            result['errors']['economic_burden'] = str(e)
            print(f"  Warning: economic_burden failed: {e}")

    # ============================================================
    # PHASE 7: Global Comparison
    # ============================================================
    try:
        result['global_comparison'] = _fetch_global_comparison(
            disease, geography, who_search, tracker,
        )
        if result['global_comparison'].get('error'):
            result['errors']['global_comparison'] = result['global_comparison']['error']
    except Exception as e:
        result['errors']['global_comparison'] = str(e)
        print(f"  Warning: global_comparison failed: {e}")

    # ============================================================
    # ASSEMBLY: Collect provenance + generate visualization
    # ============================================================
    tracker.start_step('assembly', "Generating report...")

    # Collect all provenance
    for section_key in ['epidemiology', 'demographics', 'trends', 'treatment_landscape',
                        'unmet_need', 'economic_burden', 'global_comparison']:
        section_data = result.get(section_key, {})
        if isinstance(section_data, dict):
            result['provenance'].extend(section_data.get('provenance', []))

    # Generate ASCII report
    result['visualization'] = generate_report(result)

    tracker.complete_step("Disease burden analysis complete")

    if progress_callback:
        progress_callback(100, "Done")

    return result


# ─── CLI entry point ───────────────────────────────────────────
def _build_bioclaw_mcp_funcs():
    """Build mcp_funcs via McpClient for BioClaw."""
    from mcp_client import McpClient
    clients, mcp_funcs = {}, {}
    for srv, tool, funcs in [
        ('cdc', 'cdc_health_data', {'cdc_health_data': {}}),
        ('pubmed', 'pubmed_articles', {'pubmed_search': {'method': 'search_keywords'}}),
        ('ctgov', 'ct_gov_studies', {'ctgov_search': {'method': 'search'}}),
        ('medicaid', 'medicaid_info', {'medicaid_info': {}}),
        ('fda', 'fda_info', {'fda_search': {'method': 'lookup_drug'}}),
        ('opentargets', 'opentargets_info', {'opentargets_search': {'method': 'search_diseases'}}),
    ]:
        try:
            c = McpClient(srv); c.connect(); clients[srv] = c
            for k, d in funcs.items():
                def make_fn(cl, t, df):
                    def fn(**kw): return cl.call(t, **{**df, **kw})
                    return fn
                mcp_funcs[k] = make_fn(c, tool, d)
        except Exception: pass
    print(f"BioClaw MCP: {len(mcp_funcs)} functions")
    return mcp_funcs, clients


def _build_cli_mcp_funcs_UNUSED():
    """REPLACED by _build_bioclaw_mcp_funcs."""
    import importlib.util

    _abs_script_dir = os.path.abspath(_script_dir)
    _claude_dir = os.path.dirname(os.path.dirname(os.path.dirname(_abs_script_dir)))
    mcp_path = os.path.join(_claude_dir, "mcp")

    if _claude_dir not in sys.path:
        sys.path.insert(0, _claude_dir)

    def _load_module(name, path):
        spec = importlib.util.spec_from_file_location(name, path,
            submodule_search_locations=[os.path.dirname(path)])
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception:
            sys.modules.pop(name, None)
            raise
        return mod

    base = os.path.join(mcp_path, "servers")

    cdc_mod = _load_module("cdc_mcp", os.path.join(base, "cdc_mcp", "__init__.py"))
    who_mod = _load_module("who_mcp", os.path.join(base, "who_mcp", "__init__.py"))
    dc_mod = _load_module("datacommons_mcp", os.path.join(base, "datacommons_mcp", "__init__.py"))
    pubmed_mod = _load_module("pubmed_mcp", os.path.join(base, "pubmed_mcp", "__init__.py"))
    ct_mod = _load_module("ct_gov_mcp", os.path.join(base, "ct_gov_mcp", "__init__.py"))
    medicaid_mod = _load_module("medicaid_mcp", os.path.join(base, "medicaid_mcp", "__init__.py"))
    fda_mod = _load_module("fda_mcp", os.path.join(base, "fda_mcp", "__init__.py"))
    ot_mod = _load_module("opentargets_mcp", os.path.join(base, "opentargets_mcp", "__init__.py"))

    # CDC: cdc_health_data(method, ...)
    def cdc_wrapper(**kwargs):
        return cdc_mod.cdc_health_data(**kwargs)

    # WHO: search_indicators(keywords) or get_health_data(indicator_code, ...)
    def who_wrapper(**kwargs):
        method = kwargs.pop('method', 'search_indicators')
        if method == 'search_indicators':
            return who_mod.search_indicators(**kwargs)
        elif method == 'get_health_data':
            return who_mod.get_health_data(**kwargs)
        elif method == 'get_country_data':
            return who_mod.get_country_data(**kwargs)
        return who_mod.search_indicators(**kwargs)

    # DataCommons: search_indicators(query, ...)
    def dc_search_wrapper(**kwargs):
        kwargs.pop('method', None)
        return dc_mod.search_indicators(**kwargs)

    # DataCommons: get_observations(variable_dcid, place_dcid, ...)
    def dc_observations_wrapper(**kwargs):
        kwargs.pop('method', None)
        return dc_mod.get_observations(**kwargs)

    # PubMed: search_keywords(keywords, num_results)
    def pubmed_wrapper(**kwargs):
        kwargs.pop('method', None)
        # Remap 'query' to 'keywords' if needed
        if 'query' in kwargs and 'keywords' not in kwargs:
            kwargs['keywords'] = kwargs.pop('query')
        return pubmed_mod.search_keywords(**kwargs)

    # CT.gov: search(condition, status, ...)
    def ctgov_wrapper(**kwargs):
        kwargs.pop('method', None)
        return ct_mod.search(**kwargs)

    # Medicaid: medicaid_info(method, ...)
    def medicaid_wrapper(**kwargs):
        return medicaid_mod.medicaid_info(**kwargs)

    # FDA: lookup_drug(search_term, search_type, count, ...)
    def fda_wrapper(**kwargs):
        kwargs.pop('method', None)
        return fda_mod.lookup_drug(**kwargs)

    # OpenTargets: multi-method wrapper matching server interface
    def opentargets_wrapper(**kwargs):
        method = kwargs.pop('method', 'search_diseases')
        if method == 'search_diseases':
            return ot_mod.search_diseases(**kwargs)
        elif method == 'get_disease_targets_summary':
            return ot_mod.get_disease_targets_summary(**kwargs)
        elif method == 'get_target_details':
            return ot_mod.get_target_details(**kwargs)
        return ot_mod.search_diseases(**kwargs)

    return {
        'cdc_search': cdc_wrapper,
        'who_search': who_wrapper,
        'datacommons_search': dc_search_wrapper,
        'datacommons_observations': dc_observations_wrapper,
        'pubmed_search': pubmed_wrapper,
        'ctgov_search': ctgov_wrapper,
        'medicaid_info': medicaid_wrapper,
        'fda_search': fda_wrapper,
        'opentargets_search': opentargets_wrapper,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Disease Burden Analysis")
    parser.add_argument("disease", help="Disease name to analyze")
    parser.add_argument("--geography", default="US", help="Focus region: US, EU, global")
    parser.add_argument("--skip-treatments", action="store_true")
    parser.add_argument("--skip-economics", action="store_true")
    args = parser.parse_args()

    def progress_cb(pct, msg):
        print(f"  [{pct:3d}%] {msg}")

    print(f"\nAnalyzing disease burden for: {args.disease}\n")

    _mcp, _clients = _build_bioclaw_mcp_funcs()

    result = get_disease_burden_analysis(
        disease=args.disease,
        geography=args.geography,
        skip_treatments=args.skip_treatments,
        skip_economics=args.skip_economics,
        mcp_funcs=_mcp,
        progress_callback=progress_cb,
    )

    for c in _clients.values(): c.close()

    print("\n" + result.get('visualization', 'No visualization generated'))

    if result.get('errors'):
        print(f"\nErrors encountered: {result['errors']}")
