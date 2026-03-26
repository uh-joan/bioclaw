#!/usr/bin/env python3
"""
Financial data parsing utilities for SWOT analysis.

This module provides functions for:
- Currency conversion (API-based with fallback)
- XBRL parsing (units, contexts, segment revenue)
- Yahoo Finance text parsing
"""

import json
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from swot_constants import CURRENCY_TO_USD_FALLBACK, CURRENCY_TO_USD


# ============================================================================
# Currency Conversion (API-based with fallback)
# ============================================================================

# Cache for exchange rates to avoid repeated API calls
_exchange_rate_cache: Dict[str, float] = {}


def get_historical_exchange_rate(currency: str, date: str = None) -> float:
    """Fetch historical exchange rate from Frankfurter API (uses ECB rates).

    Args:
        currency: ISO 4217 currency code (e.g., 'DKK', 'EUR', 'GBP')
        date: Date string in YYYY-MM-DD format. If None, uses latest rate.

    Returns:
        float: Exchange rate to USD (how many USD per 1 unit of foreign currency)
    """
    currency = currency.upper()

    if currency == 'USD':
        return 1.0

    # Check cache first
    cache_key = f"{currency}_{date or 'latest'}"
    if cache_key in _exchange_rate_cache:
        return _exchange_rate_cache[cache_key]

    try:
        # Frankfurter API uses ECB rates, base is EUR
        # We need to convert: Foreign Currency -> EUR -> USD
        # Rate = (1/foreign_to_eur) * eur_to_usd

        # Get the date endpoint
        date_path = date if date else 'latest'

        # First get EUR to USD rate
        eur_url = f"https://api.frankfurter.app/{date_path}?from=EUR&to=USD"
        req = urllib.request.Request(eur_url, headers={'User-Agent': 'SWOT-Analysis-Tool/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status != 200:
                raise ValueError(f"Failed to fetch EUR/USD rate: {resp.status}")
            eur_data = json.loads(resp.read().decode('utf-8'))
        eur_to_usd = eur_data.get('rates', {}).get('USD', 1.08)

        if currency == 'EUR':
            rate = eur_to_usd
        else:
            # Get foreign currency to EUR rate
            fx_url = f"https://api.frankfurter.app/{date_path}?from={currency}&to=EUR"
            req = urllib.request.Request(fx_url, headers={'User-Agent': 'SWOT-Analysis-Tool/1.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status != 200:
                    raise ValueError(f"Failed to fetch {currency}/EUR rate: {resp.status}")
                fx_data = json.loads(resp.read().decode('utf-8'))
            foreign_to_eur = fx_data.get('rates', {}).get('EUR')

            if foreign_to_eur is None:
                # Currency not supported by API, use fallback
                print(f"   Currency {currency} not supported by API, using fallback rate")
                return CURRENCY_TO_USD_FALLBACK.get(currency, 1.0)

            # Calculate: 1 foreign currency -> EUR -> USD
            rate = foreign_to_eur * eur_to_usd

        # Cache the result
        _exchange_rate_cache[cache_key] = rate
        print(f"   Fetched exchange rate: 1 {currency} = {rate:.4f} USD (date: {date_path})")
        return rate

    except Exception as e:
        print(f"   Failed to fetch exchange rate for {currency}: {e}. Using fallback.")
        return CURRENCY_TO_USD_FALLBACK.get(currency, 1.0)


def convert_to_usd(value: float, currency: str, date: str = None) -> float:
    """Convert a value from foreign currency to USD using historical exchange rates.

    Args:
        value: Amount in foreign currency
        currency: ISO 4217 currency code
        date: Optional date string (YYYY-MM-DD) for historical rate. If None, uses latest rate.

    Returns:
        float: Amount in USD
    """
    rate = get_historical_exchange_rate(currency, date)
    return value * rate


# ============================================================================
# XBRL Unit and Currency Parsing
# ============================================================================

def parse_xbrl_units(xml_root) -> Dict[str, str]:
    """Parse XBRL units to detect currency.

    Args:
        xml_root: Parsed XML ElementTree root

    Returns:
        dict: unit_id -> currency_code (e.g., {'usd': 'USD', 'iso4217_DKK': 'DKK'})
    """
    units = {}

    for unit in xml_root.findall('.//{http://www.xbrl.org/2003/instance}unit'):
        unit_id = unit.get('id')
        if not unit_id:
            continue

        # Look for measure element (e.g., <measure>iso4217:DKK</measure>)
        measure = unit.find('{http://www.xbrl.org/2003/instance}measure')
        if measure is not None and measure.text:
            measure_text = measure.text.strip()
            # Extract currency from iso4217:XXX format
            if 'iso4217' in measure_text.lower():
                currency = measure_text.split(':')[-1].upper()
                units[unit_id] = currency
            elif measure_text.upper() in CURRENCY_TO_USD:
                units[unit_id] = measure_text.upper()

    return units


def detect_reporting_currency(xml_root) -> str:
    """Detect the primary reporting currency from XBRL.

    Counts facts by currency unit to find the dominant reporting currency.

    Args:
        xml_root: Parsed XML ElementTree root

    Returns:
        str: Currency code (e.g., 'USD', 'DKK', 'EUR')
    """
    units = parse_xbrl_units(xml_root)

    # Count facts by currency to find the dominant one
    currency_counts = {}
    for unit_id, currency in units.items():
        # Count how many facts reference this unit
        for elem in xml_root.iter():
            if elem.get('unitRef') == unit_id:
                currency_counts[currency] = currency_counts.get(currency, 0) + 1

    if currency_counts:
        # Return the most common currency
        return max(currency_counts, key=currency_counts.get)

    return 'USD'  # Default to USD


# ============================================================================
# XBRL Context and Dimensional Parsing
# ============================================================================

def normalize_xbrl_segment_name(raw_segment: str) -> Optional[str]:
    """Normalize XBRL segment names for readability.

    Handles garbled CamelCase concatenations (e.g., 'EYLEAHDAndEYLEAMember')
    by detecting repeated substrings and keeping the clean version.

    Args:
        raw_segment: Raw segment name from XBRL (e.g., 'PharmaceuticalsMember')

    Returns:
        str: Normalized segment name or None if should be filtered
    """
    if not raw_segment:
        return None

    # Remove "Member" suffix
    segment = re.sub(r'Member$', '', raw_segment)

    # Detect garbled CamelCase concatenations before splitting.
    # Pattern: a recognizable product name appears twice in the segment
    # e.g., "EYLEAHDAndEYLEA" → "EYLEA" (the second clean occurrence)
    # Strategy: if "And" or "Or" joins two parts, check if any part is
    # a clean prefix/suffix of the other → keep the shorter clean one.
    and_split = re.split(r'(?<=[a-z])And(?=[A-Z])|(?<=[A-Z])And(?=[A-Z])', segment)
    if len(and_split) >= 2:
        # Check if parts share a common root (garbled concatenation)
        parts = [p.strip() for p in and_split if p.strip()]
        if len(parts) == 2:
            p1, p2 = parts
            # If one part ends with the other (e.g., "EYLEAHD" ends with overlap of "EYLEA")
            # or one contains the other, keep the shorter clean version
            if p2 in p1 or p1 in p2:
                segment = min(parts, key=len)
            elif len(p1) > len(p2) and p1.startswith(p2[:3]):
                segment = p2  # Second part is likely the clean name
            elif len(p2) > len(p1) and p2.startswith(p1[:3]):
                segment = p1

    # Convert camelCase to readable format
    segment = re.sub(r'([a-z])([A-Z])', r'\1 \2', segment)

    # Also split between consecutive uppercase followed by lowercase (e.g., "HIVProducts" → "HIV Products")
    segment = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', segment)

    # Remove common suffixes
    for suffix in ['Segment', 'Business', 'Product Line', 'Division']:
        segment = re.sub(rf'\s*{suffix}\s*$', '', segment, flags=re.I)

    # Clean up
    segment = ' '.join(segment.split())

    # Filter out corporate/other segments that aren't product-specific
    skip_terms = ['corporate', 'eliminations', 'other', 'unallocated', 'reconciling']
    if any(term in segment.lower() for term in skip_terms):
        return None

    # Filter out generic aggregation terms (not specific products)
    generic_terms = [
        'product', 'products', 'product gross', 'product net', 'product revenue',
        'reportable', 'total', 'consolidated', 'combined', 'aggregate',
        'service', 'services', 'license', 'collaboration',
        'product sales discounts', 'allowances', 'adjustments'
    ]
    if segment.lower() in generic_terms:
        return None

    return segment if segment else None


def normalize_xbrl_geography_name(raw_geography: str) -> Optional[str]:
    """Normalize XBRL geography names for readability.

    Args:
        raw_geography: Raw geography name from XBRL (e.g., 'UnitedStatesMember')

    Returns:
        str: Normalized geography name or None
    """
    if not raw_geography:
        return None

    # Remove "Member" suffix
    geography = re.sub(r'Member$', '', raw_geography)

    # Convert camelCase to readable format
    geography = re.sub(r'([a-z])([A-Z])', r'\1 \2', geography)

    geography = ' '.join(geography.split())

    return geography if geography else None


def parse_xbrl_contexts(xml_root) -> Dict[str, Dict]:
    """Parse XBRL contexts to extract dimensional information (segment, geography, time).

    Args:
        xml_root: Parsed XML ElementTree root

    Returns:
        dict: context_id -> {start_date, end_date, segments_by_axis, geographies_by_axis}
    """
    contexts = {}

    for context in xml_root.findall('.//{http://www.xbrl.org/2003/instance}context'):
        context_id = context.get('id')

        # Extract period information
        period = context.find('{http://www.xbrl.org/2003/instance}period')
        start_date = None
        end_date = None

        if period is not None:
            instant = period.find('{http://www.xbrl.org/2003/instance}instant')
            if instant is not None:
                end_date = instant.text
            else:
                start_elem = period.find('{http://www.xbrl.org/2003/instance}startDate')
                end_elem = period.find('{http://www.xbrl.org/2003/instance}endDate')
                if start_elem is not None:
                    start_date = start_elem.text
                if end_elem is not None:
                    end_date = end_elem.text

        # Extract dimensions (segment, geography)
        segments_by_axis = {}
        geographies_by_axis = {}

        entity = context.find('{http://www.xbrl.org/2003/instance}entity')
        if entity is not None:
            for member in entity.findall('.//{http://xbrl.org/2006/xbrldi}explicitMember'):
                dimension_attr = member.get('dimension')
                member_value = member.text

                if not dimension_attr or not member_value:
                    continue

                # Extract local name from member value
                if ':' in member_value:
                    member_value = member_value.split(':')[1]

                axis_name = dimension_attr.split(':')[-1] if ':' in dimension_attr else dimension_attr
                dim_lower = dimension_attr.lower()

                # Classify as segment or geography
                if 'segment' in dim_lower or 'product' in dim_lower or 'business' in dim_lower:
                    normalized = normalize_xbrl_segment_name(member_value)
                    if normalized:
                        segments_by_axis[dimension_attr] = {'segment': normalized, 'axis': axis_name}

                elif ('geograph' in dim_lower or 'region' in dim_lower or 'country' in dim_lower
                      or 'statement' in dim_lower and 'axis' in dim_lower  # StatementGeographicalAxis
                      or 'territory' in dim_lower or 'market' in dim_lower):
                    normalized = normalize_xbrl_geography_name(member_value)
                    if normalized:
                        geographies_by_axis[dimension_attr] = normalized

        contexts[context_id] = {
            'start_date': start_date,
            'end_date': end_date,
            'segments_by_axis': segments_by_axis,
            'geographies_by_axis': geographies_by_axis
        }

    return contexts


def extract_xbrl_segment_revenue(xml_root, contexts: Dict) -> List[Dict]:
    """Extract revenue facts with dimensional context from XBRL.

    Args:
        xml_root: Parsed XML ElementTree root
        contexts: Parsed context dictionary from parse_xbrl_contexts

    Returns:
        list: Revenue facts with segment/geography information
    """
    facts = []

    # Discover namespaces
    namespaces_found = {}
    for elem in xml_root.iter():
        tag = elem.tag
        if '}' in tag:
            ns = tag.split('}')[0].strip('{')
            if 'us-gaap' in ns:
                namespaces_found['us-gaap'] = ns
            elif 'ifrs-full' in ns.lower():
                namespaces_found['ifrs-full'] = ns
        if len(namespaces_found) >= 2:
            break

    if not namespaces_found:
        return facts

    revenue_concepts = [
        'RevenueFromContractWithCustomerExcludingAssessedTax',
        'Revenues',
        'SalesRevenueNet',
        'Revenue'
    ]

    for concept_name in revenue_concepts:
        for ns_key, ns_uri in namespaces_found.items():
            xpath = f".//{{{ns_uri}}}{concept_name}"
            for elem in xml_root.findall(xpath):
                context_ref = elem.get('contextRef')

                if context_ref and elem.text and context_ref in contexts:
                    try:
                        value = float(elem.text)
                        context_info = contexts[context_ref]

                        if not context_info['end_date']:
                            continue

                        segments_by_axis = context_info.get('segments_by_axis', {})
                        geographies_by_axis = context_info.get('geographies_by_axis', {})

                        # Extract segment facts
                        if segments_by_axis:
                            for axis, seg_info in segments_by_axis.items():
                                facts.append({
                                    'concept': concept_name,
                                    'value': value,
                                    'start_date': context_info['start_date'],
                                    'end_date': context_info['end_date'],
                                    'segment': seg_info['segment'],
                                    'geography': None,
                                    'axis': seg_info['axis']
                                })

                        # Extract geography facts (standalone or combined with segment)
                        if geographies_by_axis:
                            for axis, geo_name in geographies_by_axis.items():
                                facts.append({
                                    'concept': concept_name,
                                    'value': value,
                                    'start_date': context_info['start_date'],
                                    'end_date': context_info['end_date'],
                                    'segment': None,
                                    'geography': geo_name,
                                    'axis': axis
                                })

                        # Consolidated (no dimensions)
                        if not segments_by_axis and not geographies_by_axis:
                            facts.append({
                                'concept': concept_name,
                                'value': value,
                                'start_date': context_info['start_date'],
                                'end_date': context_info['end_date'],
                                'segment': None,
                                'geography': None,
                                'axis': None
                            })

                    except (ValueError, TypeError):
                        pass

    return facts


# ============================================================================
# Yahoo Finance Text Parsing
# ============================================================================

def parse_yahoo_value(text: str, label: str) -> Optional[float]:
    """Parse a value from Yahoo Finance formatted text response.

    Handles formats like:
    - **Total Revenue:** 56.37B USD
    - **EBITDA:** 24.92B USD
    - **Net Income:** 1.5T USD

    Args:
        text: Formatted text from Yahoo Finance MCP
        label: Label to search for (e.g., 'Total Revenue', 'EBITDA')

    Returns:
        float: Parsed numeric value or None if not found
    """
    pattern = rf'\*\*{label}:\*\*\s*([\d.]+)([BTMKbtmk])?\s*USD'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        value = float(match.group(1))
        multiplier = match.group(2).upper() if match.group(2) else ''
        if multiplier == 'T':
            value *= 1_000_000_000_000
        elif multiplier == 'B':
            value *= 1_000_000_000
        elif multiplier == 'M':
            value *= 1_000_000
        elif multiplier == 'K':
            value *= 1_000
        return value
    return None


# ============================================================================
# XBRL Period Helpers
# ============================================================================

def is_annual_period(start_date: str, end_date: str) -> bool:
    """Check if the period is approximately 1 year (350-380 days).

    Args:
        start_date: Period start date (YYYY-MM-DD format)
        end_date: Period end date (YYYY-MM-DD format)

    Returns:
        bool: True if period is approximately 1 year
    """
    if not start_date or not end_date:
        return False
    try:
        start = datetime.strptime(start_date[:10], '%Y-%m-%d')
        end = datetime.strptime(end_date[:10], '%Y-%m-%d')
        days = (end - start).days
        return 350 <= days <= 380
    except (ValueError, TypeError):
        return False


def extract_year(date_str: str) -> int:
    """Extract year from date string.

    Args:
        date_str: Date string in YYYY-MM-DD or similar format

    Returns:
        int: Year or 0 if parsing fails
    """
    if not date_str:
        return 0
    try:
        return int(date_str[:4])
    except (ValueError, TypeError):
        return 0
