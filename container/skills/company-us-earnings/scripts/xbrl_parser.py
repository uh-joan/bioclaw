"""
XBRL Parser Module

This module provides functions for parsing XBRL dimensional data from SEC EDGAR filings.
Extracts segment and geographic revenue with dimensional context information.

Key Functions:
    - parse_xbrl_contexts: Parse XBRL contexts to extract dimensional information
    - extract_dimensional_revenue: Extract revenue facts with dimensional context
    - convert_cumulative_to_quarterly: Convert YTD cumulative data to quarterly figures
    - get_quarter_label: Convert dates to fiscal quarter labels
    - extract_values_from_segment_data: Extract values from segment data structures
    - is_data_already_quarterly: Check if data is already quarterly (not cumulative)
    - _process_revenue_element: Helper to process individual revenue elements
"""

import xml.etree.ElementTree as ET
import re


def parse_xbrl_contexts(xml_root):
    """Parse XBRL contexts to extract dimensional information.

    Contexts define the dimensional attributes of facts:
    - Segment (business unit, product line)
    - Geography (region, country)
    - Time period (instant or duration)

    Returns:
        tuple: (contexts_dict, all_dimension_axes_set)
        contexts_dict: context_id -> {
            'start_date': str or None,
            'end_date': str,
            'segment': str or None,
            'geography': str or None
        }
        all_dimension_axes_set: set of all dimension axis names found
    """
    contexts = {}
    all_dimension_axes = set()

    # Find all context elements
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

        # Extract dimensions (segment, geography, etc.)
        # Collect ALL segments from ALL axes (don't filter at context level)
        segments_by_axis = {}
        geographies_by_axis = {}

        # Preference order for segment axes (prefer top-level over subsegments)
        segment_priority = {
            # US GAAP axes
            'StatementBusinessSegmentsAxis': 1,
            'ProductOrServiceAxis': 2,
            'SubsegmentsAxis': 3,
            # IFRS axes
            'SegmentsAxis': 1,  # Business segments (e.g., Pharmaceuticals, Vaccines)
            'ProductsAndServicesAxis': 2,  # Individual products/drugs (lower priority)
        }

        entity = context.find('{http://www.xbrl.org/2003/instance}entity')
        if entity is not None:
            for member in entity.findall('.//{http://xbrl.org/2006/xbrldi}explicitMember'):
                dimension_attr = member.get('dimension')
                member_value = member.text

                if not dimension_attr or not member_value:
                    continue

                # Track this dimension axis globally
                axis_name = dimension_attr.split(':')[-1] if ':' in dimension_attr else dimension_attr
                all_dimension_axes.add(axis_name)

                # Extract namespace and local name
                if ':' in member_value:
                    member_value = member_value.split(':')[1]

                dim_lower = dimension_attr.lower()

                # Classify as segment or geography
                # Handle both US GAAP and IFRS naming conventions:
                # - US GAAP: 'SegmentAxis', 'ProductAxis', 'BusinessLineAxis'
                # - IFRS: 'SegmentsAxis', 'ProductsAndServicesAxis'
                if 'segment' in dim_lower or 'product' in dim_lower or 'business' in dim_lower:
                    normalized = normalize_segment_name(member_value)
                    if normalized:
                        priority = segment_priority.get(axis_name, 99)
                        # Store segment with axis and priority
                        segments_by_axis[dimension_attr] = {
                            'segment': normalized,
                            'priority': priority
                        }

                # Handle both US GAAP and IFRS geography naming:
                # - US GAAP: 'GeographyAxis', 'RegionAxis', 'CountryAxis'
                # - IFRS: 'GeographicalAreasAxis'
                elif 'geograph' in dim_lower or 'region' in dim_lower or 'country' in dim_lower or 'areas' in dim_lower:
                    normalized = normalize_geography_name(member_value)
                    if normalized:
                        geographies_by_axis[dimension_attr] = normalized

        contexts[context_id] = {
            'start_date': start_date,
            'end_date': end_date,
            'segments_by_axis': segments_by_axis,  # Dict of {axis: {segment, priority}}
            'geographies_by_axis': geographies_by_axis  # Dict of {axis: geography}
        }

    return contexts, all_dimension_axes


def _fix_camelcase_conjunctions(name):
    """Fix missing spaces around conjunctions in CamelCase-converted names.

    XBRL member names like 'InstrumentsandAccessories' become 'Instrumentsand Accessories'
    after standard CamelCase splitting. This fixes them to 'Instruments and Accessories'.

    Only matches conjunctions that are stuck to adjacent words (no space on at least one side).
    Uses negative lookahead/lookbehind to avoid splitting inside real words like 'Foreign'.
    """
    # Only fix conjunctions that appear stuck between two words separated by a space
    # Pattern: "wordCONJ " -> "word CONJ " (stuck to preceding word)
    # Pattern: " CONJword" -> " CONJ word" (stuck to following word)
    # Must have a space on the other side to confirm it's a word boundary from CamelCase splitting
    for conj in ['and', 'of', 'the']:
        # Conjunction stuck to end of preceding word, space after: "Instrumentsand " -> "Instruments and "
        name = re.sub(rf'([a-z])({conj})\s', rf'\1 {conj} ', name)
        # Conjunction stuck to start of following word, space before: " andAccessories" -> " and Accessories"
        name = re.sub(rf'\s({conj})([A-Z])', rf' {conj} \2', name)
    return name


def normalize_segment_name(raw_segment):
    """Normalize segment names for consistency."""
    if not raw_segment:
        return None

    # Remove common suffixes
    segment = raw_segment.replace('Member', '').replace('Segment', '')

    # Convert camelCase to readable format
    # First: split acronym+Word patterns like "HIVProduct" -> "HIV Product", "USRevenue" -> "US Revenue"
    segment = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', segment)
    # Split digits followed by a capitalized word like "COVID19Antibodies" -> "COVID19 Antibodies"
    segment = re.sub(r'([0-9])([A-Z][a-z])', r'\1 \2', segment)
    # Then: split camelCase like "instrumentsAndAccessories" -> "instruments And Accessories"
    segment = re.sub(r'([a-z])([A-Z])', r'\1 \2', segment)

    # Fix conjunctions stuck to adjacent words
    segment = _fix_camelcase_conjunctions(segment)

    # Remove extra whitespace
    segment = ' '.join(segment.split())

    return segment if segment else None


def normalize_geography_name(raw_geography):
    """Normalize geography names for consistency."""
    if not raw_geography:
        return None

    # Remove common suffixes
    geography = raw_geography.replace('Member', '').replace('Countries', '')

    # Convert camelCase to readable format
    # First: split acronym+Word patterns like "USRevenue" -> "US Revenue"
    geography = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', geography)
    # Split digits followed by a capitalized word like "COVID19Antibodies" -> "COVID19 Antibodies"
    geography = re.sub(r'([0-9])([A-Z][a-z])', r'\1 \2', geography)
    # Then: split camelCase like "unitedStates" -> "united States"
    geography = re.sub(r'([a-z])([A-Z])', r'\1 \2', geography)

    # Fix conjunctions stuck to adjacent words
    geography = _fix_camelcase_conjunctions(geography)

    # Remove extra whitespace
    geography = ' '.join(geography.split())

    return geography if geography else None


def extract_values_from_segment_data(segment_data):
    """Extract just the values from segment data structure.

    Args:
        segment_data: Dict of {period: {'value': float, 'filing_date': str}} or {period: float}

    Returns:
        Dict of {period: float}
    """
    if not segment_data:
        return {}

    result = {}
    for period, data in segment_data.items():
        if isinstance(data, dict):
            result[period] = data.get('value', 0)
        else:
            result[period] = data
    return result


def is_data_already_quarterly(segment_data):
    """Check if segment data appears to already be quarterly (not cumulative).

    Returns True if most data points have quarterly duration (70-100 days).
    This indicates the data was sourced from quarterly XBRL facts,
    not cumulative YTD facts that need conversion.
    """
    if not segment_data:
        return False

    quarterly_count = 0
    total_with_duration = 0

    for period, data in segment_data.items():
        if isinstance(data, dict):
            duration = data.get('duration')
            if duration is not None:
                total_with_duration += 1
                if 70 <= duration <= 100:
                    quarterly_count += 1

    # If we have duration info and most points are quarterly, data is already quarterly
    if total_with_duration > 0:
        return quarterly_count / total_with_duration >= 0.5

    # No duration info - assume it needs conversion (legacy behavior)
    return False


def convert_cumulative_to_quarterly(time_series_data, fiscal_year_end='1231'):
    """Convert cumulative YTD data to actual quarterly figures.

    Args:
        time_series_data: Dict of {period: cumulative_value} or {period: {'value': ..., 'filing_date': ...}}
        fiscal_year_end: Fiscal year end in MMDD format (default: '1231' for Dec 31)

    Returns:
        Dict of {period: quarterly_value}
    """
    if not time_series_data:
        return {}

    # Check if data is already quarterly (has quarterly duration markers)
    # If so, skip conversion - the data is already in quarterly form
    if is_data_already_quarterly(time_series_data):
        return extract_values_from_segment_data(time_series_data)

    # Check if data is annual-only (all periods have ~365 day durations)
    # This happens with IFRS geographic data that's only reported annually
    # In this case, return as-is without conversion
    annual_count = 0
    total_with_duration = 0
    for period, data in time_series_data.items():
        if isinstance(data, dict) and data.get('duration') is not None:
            total_with_duration += 1
            if 350 <= data['duration'] <= 380:  # ~365 days (annual)
                annual_count += 1

    if total_with_duration > 0 and annual_count / total_with_duration >= 0.7:
        # Data is annual-only, return as-is
        return extract_values_from_segment_data(time_series_data)

    # Handle new data structure with value/filing_date
    time_series_data = extract_values_from_segment_data(time_series_data)

    # Sort periods chronologically (oldest first)
    sorted_periods = sorted(time_series_data.keys())

    quarterly_data = {}
    prev_cumulative = 0
    prev_fiscal_year = None
    prev_quarter = None

    # Build a map of which fiscal years have Q1 data (for detecting mid-year segment starts)
    periods_by_fy = {}
    for period in sorted_periods:
        quarter_label = get_quarter_label(period, fiscal_year_end)
        match = re.match(r'FY(\d{4})\s+Q(\d)', quarter_label)
        if match:
            fy = int(match.group(1))
            q = int(match.group(2))
            if fy not in periods_by_fy:
                periods_by_fy[fy] = set()
            periods_by_fy[fy].add(q)

    for i, period in enumerate(sorted_periods):
        cumulative_value = time_series_data[period]

        # Use get_quarter_label to correctly determine fiscal year and quarter
        quarter_label = get_quarter_label(period, fiscal_year_end)
        # Parse: "FY2023 Q1" -> fiscal_year=2023, quarter=1
        match = re.match(r'FY(\d{4})\s+Q(\d)', quarter_label)
        if match:
            fiscal_year = int(match.group(1))
            quarter = int(match.group(2))
        else:
            # Fallback - can't parse, just use the value as-is
            quarterly_data[period] = cumulative_value
            continue

        # Detect fiscal year change
        is_new_fiscal_year = prev_fiscal_year is not None and fiscal_year != prev_fiscal_year

        # Also detect Q1 directly
        is_q1 = (quarter == 1)

        # Detect if this segment is missing Q1 for this fiscal year
        # This happens when a segment starts mid-year (e.g., renamed from another segment)
        # In this case, Q2/Q3/Q4 values are cumulative YTD but we can't properly subtract Q1
        fy_has_q1 = 1 in periods_by_fy.get(fiscal_year, set())

        # Special case: fiscal year change to a non-Q1 quarter where this FY has no Q1
        # This means the segment started mid-year and the value is cumulative YTD
        # We CANNOT calculate the true quarterly value, so skip it
        if is_new_fiscal_year and not is_q1 and not fy_has_q1:
            # SKIP - this is cumulative YTD for a segment that started mid-year
            # We can't calculate quarterly because there's no Q1 to reference
            prev_cumulative = cumulative_value
            prev_fiscal_year = fiscal_year
            prev_quarter = quarter
            continue

        # Detect if this is first data point for a NEW segment starting mid-year
        # Skip if: first period AND not Q1 AND this FY has no Q1
        is_first_period = (i == 0)

        if is_first_period and not is_q1 and not fy_has_q1:
            # SKIP this data point - it's YTD cumulative but we can't properly calculate quarterly
            # because the prior quarters were under a different segment name
            prev_cumulative = cumulative_value
            prev_fiscal_year = fiscal_year
            prev_quarter = quarter
            continue

        if is_new_fiscal_year or is_q1:
            # Q1 is actual quarterly (not cumulative)
            quarterly_value = cumulative_value
            prev_cumulative = cumulative_value
        else:
            # Q2, Q3, Q4 are cumulative - calculate delta
            quarterly_value = cumulative_value - prev_cumulative
            prev_cumulative = cumulative_value

        quarterly_data[period] = quarterly_value
        prev_fiscal_year = fiscal_year
        prev_quarter = quarter

    return quarterly_data


def get_quarter_label(date_str, fiscal_year_end='1231'):
    """Convert date string to fiscal quarter label based on company's fiscal year.

    Args:
        date_str: Date string in format YYYY-MM-DD
        fiscal_year_end: Fiscal year end in MMDD format (e.g., '0424' for April 24, '1231' for Dec 31)

    Returns:
        Quarter label like 'FY2025 Q3', 'FY2026 Q1', etc.

    Note:
        Many companies use 52/53-week fiscal years where period ends don't align
        with calendar months. For example, JNJ's Q3 ends in early October, not
        September. This function handles such cases by looking at which quarter
        boundary the date is closest to.
    """
    # Parse date
    year = int(date_str[:4])
    month = int(date_str.split('-')[1])
    day = int(date_str.split('-')[2])

    # Parse fiscal year end
    fye_month = int(fiscal_year_end[:2])
    fye_day = int(fiscal_year_end[2:4])

    # For December year-end companies (most common)
    if fye_month == 12:
        # SEC quarter-end boundaries for 52/53-week fiscal years:
        # Q1 ends late March / early April (period end around day 1-10)
        # Q2 ends late June / early July (period end around day 1-10)
        # Q3 ends late September / early October (period end around day 1-10)
        # Q4 ends late December / early January (period end around Dec 25 - Jan 5)

        if month == 1:
            if day <= 10:
                # Early January: Q4 of prior calendar year (10-K overflow)
                return f"FY{year - 1} Q4"
            else:
                # Mid/late January: Q1 of current year
                return f"FY{year} Q1"

        elif month == 2 or month == 3:
            # Feb-Mar: Q1
            return f"FY{year} Q1"

        elif month == 4:
            if day <= 10:
                # Early April: Q1 end (52/53-week calendar overflow)
                return f"FY{year} Q1"
            else:
                # Mid/late April: Q2
                return f"FY{year} Q2"

        elif month == 5 or month == 6:
            # May-Jun: Q2
            return f"FY{year} Q2"

        elif month == 7:
            if day <= 10:
                # Early July: Q2 end (52/53-week calendar overflow)
                return f"FY{year} Q2"
            else:
                # Mid/late July: Q3
                return f"FY{year} Q3"

        elif month == 8 or month == 9:
            # Aug-Sep: Q3
            return f"FY{year} Q3"

        elif month == 10:
            if day <= 10:
                # Early October: Q3 end (52/53-week calendar overflow)
                return f"FY{year} Q3"
            else:
                # Mid/late October: Q4
                return f"FY{year} Q4"

        elif month == 11:
            # November: Q4
            return f"FY{year} Q4"

        else:  # month == 12
            # December: Q4
            return f"FY{year} Q4"

    # For non-December year-end companies

    # Check for FYE overflow: 10-K period ends often extend 1-5 days past the official FYE date
    # E.g., MDT FYE is April 25 but 10-K period end might be April 26-30
    # These should be treated as Q4 of the ending fiscal year, not Q1 of the next
    if month == fye_month and day > fye_day and day <= fye_day + 10:
        # This is a Q4/FYE overflow - treat as Q4 of fiscal year ending this month
        return f"FY{year} Q4"

    # Also check for early-month-after-FYE overflow (e.g., FYE is Dec 28 but period end is Jan 2)
    fye_next_month = (fye_month % 12) + 1
    if month == fye_next_month and day <= 10:
        # Early days of month after FYE - this is Q4 of prior fiscal year
        if fye_month == 12:
            return f"FY{year - 1} Q4"
        else:
            return f"FY{year} Q4"

    # Fiscal year starts the month after fiscal year end
    fye_start_month = (fye_month % 12) + 1

    # Calculate month offset from fiscal year start
    if month >= fye_start_month:
        month_in_fy = month - fye_start_month + 1
    else:
        month_in_fy = month + 12 - fye_start_month + 1

    # Adjust for 52/53-week calendars (allow ~10 days overflow into next quarter's month)
    # Period ends in days 1-10 of a month usually belong to the prior quarter
    # But not if it's the FYE month (handled above)
    if day <= 10 and month != fye_month:
        # Check if this is likely a quarter-end overflow
        # Q1 ends around month 3 of FY, Q2 around month 6, Q3 around month 9
        if month_in_fy in [4, 7, 10]:  # First month of quarters 2, 3, 4
            # This looks like a quarter-end overflow, subtract 1 from month_in_fy
            month_in_fy = month_in_fy - 1

    # Determine quarter based on month in fiscal year
    # Q1: months 1-3, Q2: months 4-6, Q3: months 7-9, Q4: months 10-12
    if month_in_fy <= 3:
        quarter = 'Q1'
    elif month_in_fy <= 6:
        quarter = 'Q2'
    elif month_in_fy <= 9:
        quarter = 'Q3'
    else:
        quarter = 'Q4'

    # Determine fiscal year
    # The fiscal year is named by when it ENDS, not when it starts
    if month > fye_month:
        fiscal_year = year + 1
    elif month == fye_month and day > fye_day:
        # Past FYE day in FYE month - but this is handled by overflow check above
        # If we get here, it's a significant overflow (>10 days), treat as next FY
        fiscal_year = year + 1
    else:
        fiscal_year = year

    return f"FY{fiscal_year} {quarter}"


def extract_dimensional_revenue(xml_root, contexts, revenue_concepts, form):
    """Extract revenue facts with dimensional context information.

    Args:
        xml_root: XML root element
        contexts: Parsed context dictionary
        revenue_concepts: List of revenue concept names to search for
        form: Filing form type (10-Q, 10-K, or 20-F)

    Returns:
        list: Revenue facts with dimensions
    """
    facts = []

    # Discover us-gaap, ifrs-full, and company-specific namespaces (support all XBRL formats)
    namespaces_found = {}
    all_namespaces_seen = set()

    # CRITICAL FIX: Scan entire document for accounting namespace elements
    # XBRL files have thousands of <context> elements before financial facts
    # We need to find actual revenue/financial elements, not just contexts
    print(f"    XBRL namespace discovery: scanning for us-gaap, ifrs-full elements...")

    elem_count = 0
    for elem in xml_root.iter():
        tag = elem.tag
        if '}' in tag:
            ns = tag.split('}')[0].strip('{')
            all_namespaces_seen.add(ns)
            ns_lower = ns.lower()

            # Standard accounting namespaces
            if 'us-gaap' in ns_lower and 'us-gaap' not in namespaces_found:
                namespaces_found['us-gaap'] = ns
                print(f"    ✓ Found us-gaap namespace: {ns[:65]}...")
            elif ('ifrs-full' in ns_lower or 'ifrs.org' in ns_lower) and 'ifrs-full' not in namespaces_found:
                namespaces_found['ifrs-full'] = ns
                print(f"    ✓ Found IFRS namespace: {ns[:65]}...")
            # Company-specific taxonomy
            elif 'company' not in namespaces_found and not any(std in ns_lower for std in ['xbrl.org', 'sec.gov', 'fasb.org', 'w3.org', 'iso4217']):
                # Only consider non-standard namespaces as company namespaces
                if any(indicator in ns_lower for indicator in ['/20', 'company', 'corp', ns.split('/')[-2] if '/' in ns else '']):
                    namespaces_found['company'] = ns
                    print(f"    ✓ Found company namespace: {ns[:65]}...")

        elem_count += 1
        # Don't stop early - keep searching until we find all accounting namespaces
        # But limit to reasonable size to avoid hanging
        if len(namespaces_found) >= 2 or elem_count > 100000:
            break

    # Log discovered namespaces
    print(f"    XBRL namespace discovery: scanned {elem_count} elements")
    if not namespaces_found:
        print(f"    ⚠ No us-gaap, ifrs-full, or company namespace found!")
        # Show sample of actual namespaces to help diagnose
        sample_ns = [ns.split('/')[-1] for ns in list(all_namespaces_seen)[:5]]
        if sample_ns:
            print(f"      Namespaces seen: {', '.join(sample_ns)}")

    # Must have at least one accounting standard namespace (or company-specific)
    if not namespaces_found:
        return facts

    # Search for revenue concepts in US GAAP, IFRS, and company-specific namespaces
    facts_before = len(facts)
    concepts_found = []

    for concept_name in revenue_concepts:
        concept_facts_count = 0
        # Try US GAAP namespace
        if 'us-gaap' in namespaces_found:
            xpath = f".//{{{namespaces_found['us-gaap']}}}{concept_name}"
            for elem in xml_root.findall(xpath):
                _process_revenue_element(elem, facts, contexts, concept_name, form)
                concept_facts_count += 1

        # Try IFRS namespace
        if 'ifrs-full' in namespaces_found:
            xpath = f".//{{{namespaces_found['ifrs-full']}}}{concept_name}"
            for elem in xml_root.findall(xpath):
                _process_revenue_element(elem, facts, contexts, concept_name, form)
                concept_facts_count += 1

        # Try company-specific namespace
        if 'company' in namespaces_found:
            xpath = f".//{{{namespaces_found['company']}}}{concept_name}"
            for elem in xml_root.findall(xpath):
                _process_revenue_element(elem, facts, contexts, concept_name, form)
                concept_facts_count += 1

        if concept_facts_count > 0:
            concepts_found.append(f"{concept_name}({concept_facts_count})")

    facts_added = len(facts) - facts_before
    if concepts_found:
        print(f"    ✓ Found {facts_added} facts from concepts: {', '.join(concepts_found[:3])}")
        if len(concepts_found) > 3:
            print(f"      ...and {len(concepts_found) - 3} more")
    else:
        print(f"    ⚠ No matching revenue concepts found in {form}")
        print(f"      Searched {len(revenue_concepts)} concepts: {', '.join(revenue_concepts[:5])}...")

    return facts


def _process_revenue_element(elem, facts, contexts, concept_name, form):
    """Helper function to process a single revenue element."""
    context_ref = elem.get('contextRef')

    if context_ref and elem.text and context_ref in contexts:
        try:
            value = float(elem.text)
            context_info = contexts[context_ref]

            # Only include facts with valid end dates
            if not context_info['end_date']:
                return

            # Extract segments and geographies from all axes
            segments_by_axis = context_info.get('segments_by_axis', {})
            geographies_by_axis = context_info.get('geographies_by_axis', {})

            # If this context has segment dimensions, create one fact per segment axis
            # Include geography info if present (for tracking if this is a segment-geo crosscut)
            if segments_by_axis:
                # Get first geography if present (for tracking if this is a segment-geo crosscut)
                first_geo = None
                first_geo_axis = None
                if geographies_by_axis:
                    first_geo_axis = next(iter(geographies_by_axis.keys()))
                    first_geo = geographies_by_axis[first_geo_axis]

                for axis, seg_info in segments_by_axis.items():
                    facts.append({
                        'concept': concept_name,
                        'value': value,
                        'end_date': context_info['end_date'],
                        'start_date': context_info['start_date'],
                        'segment': seg_info['segment'],
                        'geography': first_geo,  # Include geography if this is a segment-geo crosscut
                        'segment_axis': axis,
                        'geography_axis': first_geo_axis,
                        'form': form,
                        'context_id': context_ref  # Preserve context for multi-dimensional linking
                    })

            # If this context has geography dimensions, create geography facts
            # IMPORTANT: For IFRS multi-dimensional reporting (e.g., Sanofi), we need geography facts
            # even when segments are present. The same XBRL element may have both dimensions.
            if geographies_by_axis:
                for axis, geo_name in geographies_by_axis.items():
                    facts.append({
                        'concept': concept_name,
                        'value': value,
                        'end_date': context_info['end_date'],
                        'start_date': context_info['start_date'],
                        'segment': None,
                        'geography': geo_name,
                        'segment_axis': None,
                        'geography_axis': axis,
                        'form': form
                    })

            # If no dimensions, this is consolidated revenue
            if not segments_by_axis and not geographies_by_axis:
                facts.append({
                    'concept': concept_name,
                    'value': value,
                    'end_date': context_info['end_date'],
                    'start_date': context_info['start_date'],
                    'segment': None,
                    'geography': None,
                    'segment_axis': None,
                    'geography_axis': None,
                    'form': form
                })

        except (ValueError, TypeError):
            pass  # Skip invalid values
