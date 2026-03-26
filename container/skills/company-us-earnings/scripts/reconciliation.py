"""
Revenue Reconciliation Module

This module provides functions for reconciling segment revenue data with consolidated
revenue from SEC EDGAR XBRL filings. It handles complex scenarios including:

1. Geographic hierarchy detection (US vs Non-US, with sub-regions)
2. Rollup segment detection and filtering to prevent double-counting
3. Per-period axis selection based on revenue reconciliation quality
4. Segment fingerprinting for smart matching across corporate restructurings
5. YoY growth calculation with anomaly detection

Key Concepts:

- **Hierarchy Detection**: Identifies parent-child relationships in geographic data
  (e.g., US + Non-US = Total, with Europe/Asia/Americas as Non-US children)

- **Rollup Segments**: Detects and filters aggregate segments that duplicate revenue
  (e.g., "Total Reportable Segments" that equals sum of individual segments)

- **Per-Period Axis Selection**: Different SEC filings (10-K vs 10-Q) may use different
  axes for segment reporting. This module selects the best axis for each period based
  on how well segment revenue reconciles to consolidated revenue.

- **Segment Fingerprinting**: Tracks segments by revenue amount and % of total, enabling
  matching across corporate restructurings when segment names change (e.g., "Pharmaceutical"
  renamed to "Innovative Medicine").

- **Anomaly Detection**: Flags extreme YoY growth rates that indicate data quality issues
  from restatements, spin-offs, or other corporate actions.

Usage:
    from reconciliation import (
        detect_geographic_hierarchy,
        detect_rollup_segments,
        get_best_axis_for_period,
        calculate_yoy_with_smart_matching
    )
"""

import re
from difflib import SequenceMatcher
from typing import Dict, Tuple, Optional, Set
from collections import defaultdict

# Import helper functions from xbrl_parser module
from xbrl_parser import (
    normalize_segment_name,
    convert_cumulative_to_quarterly,
    get_quarter_label
)


def detect_geographic_hierarchy(geographic_data):
    """
    Detect geographic hierarchy and add parent/child relationships.

    Identifies patterns like:
    - US + Non US = Total (top-level split)
    - Europe, Asia Pacific, Western Hemisphere = Non US breakdown (sub-regions)

    Args:
        geographic_data: Dict of {geo_name: {latest_revenue, quarters, ...}}

    Returns:
        Dict with added 'hierarchy' field indicating level and parent
    """
    if not geographic_data or len(geographic_data) <= 2:
        return geographic_data

    # Get latest revenues for hierarchy detection
    geo_revenues = {name: data.get('latest_revenue', 0) for name, data in geographic_data.items()}

    # Common top-level patterns (US vs Non-US, Domestic vs International)
    top_level_patterns = [
        ('US', 'Non Us'),
        ('United States', 'Non United States'),
        ('Domestic', 'International'),
        ('U S', 'Non U S'),
        ('Americas', 'Non Americas'),
    ]

    # Detect if we have a US/Non-US split
    us_region = None
    non_us_region = None
    sub_regions = []

    for geo_name in geo_revenues.keys():
        geo_lower = geo_name.lower().replace('-', ' ').replace('_', ' ')

        # Check for US/Domestic
        if geo_lower in ['us', 'u s', 'united states', 'domestic', 'americas']:
            us_region = geo_name
        # Check for Non-US/International (must contain "non" or be "international")
        elif 'non' in geo_lower or geo_lower == 'international':
            non_us_region = geo_name
        else:
            # Potential sub-region
            sub_regions.append(geo_name)

    # Validate hierarchy: sub-regions should sum to Non-US (within tolerance)
    if us_region and non_us_region and sub_regions:
        non_us_value = geo_revenues.get(non_us_region, 0)
        sub_region_sum = sum(geo_revenues.get(sr, 0) for sr in sub_regions)

        # Check if sub-regions are children of Non-US (within 5% tolerance)
        if non_us_value > 0:
            variance_pct = abs(non_us_value - sub_region_sum) / non_us_value * 100
            is_hierarchy = variance_pct < 5

            if is_hierarchy:
                # Mark hierarchy levels
                for geo_name, data in geographic_data.items():
                    if geo_name == us_region:
                        data['hierarchy'] = {'level': 'top', 'parent': None, 'group': 'primary'}
                    elif geo_name == non_us_region:
                        data['hierarchy'] = {'level': 'top', 'parent': None, 'group': 'primary'}
                    elif geo_name in sub_regions:
                        data['hierarchy'] = {'level': 'sub', 'parent': non_us_region, 'group': 'sub_regions'}

                return geographic_data

    # No clear hierarchy detected - mark all as top-level
    for geo_name, data in geographic_data.items():
        data['hierarchy'] = {'level': 'top', 'parent': None, 'group': 'flat'}

    return geographic_data


def _dedup_similar_segments(segments_dict):
    """Merge near-identical segment names (e.g., 'Service' vs 'Services').

    When both singular and plural forms exist with similar values,
    keep the one with the longer name (more specific) and discard the other.
    """
    if len(segments_dict) <= 1:
        return segments_dict

    names = list(segments_dict.keys())
    to_remove = set()

    for i, name_a in enumerate(names):
        if name_a in to_remove:
            continue
        for name_b in names[i + 1:]:
            if name_b in to_remove:
                continue
            a_lower = name_a.lower().strip()
            b_lower = name_b.lower().strip()
            # Check if one is the plural of the other (or vice versa)
            is_plural_pair = (
                a_lower + 's' == b_lower or
                b_lower + 's' == a_lower or
                a_lower + 'es' == b_lower or
                b_lower + 'es' == a_lower
            )
            if is_plural_pair:
                # Keep the longer name (more specific), remove the shorter
                if len(name_a) >= len(name_b):
                    to_remove.add(name_b)
                else:
                    to_remove.add(name_a)

    if to_remove:
        return {k: v for k, v in segments_dict.items() if k not in to_remove}
    return segments_dict


def detect_rollup_segments(segments_dict, consolidated_revenue, tolerance_pct=5):
    """
    Detect and filter out rollup/aggregate segments that create double-counting.

    A segment is identified as a rollup if:
    1. Its name contains rollup keywords (Total, Gross, Net Product, etc.)
    2. Its value approximately equals the sum of other segments (hierarchical parent)
    3. Removing it improves reconciliation with consolidated revenue (greedy elimination)

    Args:
        segments_dict: Dictionary of {segment_name: revenue_value}
        consolidated_revenue: Total consolidated revenue for validation
        tolerance_pct: Tolerance percentage for sum-equals detection

    Returns:
        dict: Filtered segments with rollups removed
    """
    if not segments_dict or len(segments_dict) <= 1:
        return segments_dict

    # Step 0: Deduplicate near-identical segment names (e.g., "Service" vs "Services")
    segments_dict = _dedup_similar_segments(segments_dict)

    # Step 1: Identify potential rollups by keyword
    rollup_keywords = ['total', 'reportables', 'gross', 'net product', 'net sales', 'consolidated',
                       'sales revenue', 'all other', 'combined', 'brands', ' other']

    potential_rollups = {}
    potential_components = {}

    for seg_name, value in segments_dict.items():
        seg_lower = seg_name.lower()
        if any(keyword in seg_lower for keyword in rollup_keywords):
            potential_rollups[seg_name] = value
        else:
            potential_components[seg_name] = value

    # Step 2: Simple strategy - if variance with components-only is better, use it
    result = segments_dict
    if potential_components:
        component_sum = sum(potential_components.values())
        component_variance_pct = abs(consolidated_revenue - component_sum) / max(consolidated_revenue, 1) * 100

        original_sum = sum(segments_dict.values())
        original_variance_pct = abs(consolidated_revenue - original_sum) / max(consolidated_revenue, 1) * 100

        # If removing rollups significantly improves variance, use components only
        if component_variance_pct < original_variance_pct * 0.5:  # At least 50% improvement
            result = potential_components

    # Step 3: Greedy elimination of hierarchical parents
    # If segment total significantly exceeds consolidated revenue (>30% over),
    # iteratively remove whichever segment's removal most improves reconciliation.
    # This catches parent categories (e.g., "Cardiometabolic Health" parent of
    # "Mounjaro", "Jardiance", etc.) that aren't caught by keyword filtering.
    total = sum(result.values())
    if consolidated_revenue > 0:
        variance = abs(total - consolidated_revenue) / consolidated_revenue * 100
    else:
        return result

    if variance > 30 and total > consolidated_revenue * 1.3 and len(result) > 2:
        filtered = dict(result)
        removed = []

        while len(filtered) > 2:
            best_removal = None
            best_new_variance = variance

            for seg_name, seg_value in filtered.items():
                new_total = total - seg_value
                new_variance = abs(new_total - consolidated_revenue) / consolidated_revenue * 100
                if new_variance < best_new_variance:
                    best_new_variance = new_variance
                    best_removal = seg_name

            # Only remove if it gives at least 20% improvement in variance
            if best_removal and best_new_variance < variance * 0.8:
                removed.append(best_removal)
                total -= filtered[best_removal]
                del filtered[best_removal]
                variance = best_new_variance

                # Stop if we've reached acceptable variance
                if variance <= tolerance_pct:
                    break
            else:
                break

        # Only use filtered result if it's meaningfully better
        final_variance = abs(sum(filtered.values()) - consolidated_revenue) / consolidated_revenue * 100
        original_variance = abs(sum(result.values()) - consolidated_revenue) / consolidated_revenue * 100
        if final_variance < original_variance * 0.5 and len(filtered) >= 2:
            result = filtered

    # Step 4: Single-segment overlap detection for small overages
    # When the segment total slightly exceeds consolidated revenue (e.g., 2-30% over),
    # check if removing a single small segment brings variance very close to zero.
    # This catches legacy/parent segments that overlap with renamed successors
    # (e.g., JNJ "Pharmaceutical" overlapping with "Innovative Medicine").
    total = sum(result.values())
    if consolidated_revenue > 0 and len(result) > 2:
        variance = abs(total - consolidated_revenue) / consolidated_revenue * 100
        # Only apply when total overshoots (segments sum to MORE than consolidated)
        # and variance is non-trivial but below the greedy threshold
        if 1.0 < variance <= 30.0 and total > consolidated_revenue:
            best_removal = None
            best_new_variance = variance

            for seg_name, seg_value in result.items():
                new_total = total - seg_value
                new_variance = abs(new_total - consolidated_revenue) / consolidated_revenue * 100
                if new_variance < best_new_variance:
                    best_new_variance = new_variance
                    best_removal = seg_name

            # Remove only if:
            # 1. New variance is under 1% (near-perfect reconciliation)
            # 2. The removed segment is small relative to total (<15% of total)
            #    This prevents removing a legitimate large segment
            # 3. Improvement is at least 60% better
            if (best_removal and
                    best_new_variance < 1.0 and
                    result[best_removal] / total < 0.15 and
                    best_new_variance < variance * 0.4):
                filtered = {k: v for k, v in result.items() if k != best_removal}
                if len(filtered) >= 2:
                    result = filtered

    return result


def get_prior_year_quarter_label(quarter_label):
    """Get the prior year's quarter label.

    Args:
        quarter_label: Quarter label like 'FY2024 Q1'

    Returns:
        Prior year quarter label like 'FY2023 Q1'
    """
    # Parse the quarter label (format: FY2024 Q1)
    match = re.match(r'FY(\d{4})\s+(Q\d)', quarter_label)
    if match:
        year = int(match.group(1))
        quarter = match.group(2)
        return f"FY{year - 1} {quarter}"
    return None


def get_best_axis_for_period(all_segment_data, period, consolidated_revenue, axis_priority_map, fiscal_year_end, use_subsegments=False):
    """Find the best axis for a specific period based on reconciliation with consolidated revenue.

    This enables per-period axis detection, which handles cases where:
    - 10-K filings use different axes than 10-Q filings
    - Segment renames cause old axis to have missing segments
    - Corporate restructurings change segment structure

    Args:
        all_segment_data: Dict of segment_key (format: "name|axis") -> {period -> {'value': ...}}
        period: The specific period date (YYYY-MM-DD) to find best axis for
        consolidated_revenue: Consolidated revenue for this period (quarterly, not cumulative)
        axis_priority_map: Dict mapping axis names to priority (lower = higher priority)
        fiscal_year_end: Fiscal year end in MMDD format
        use_subsegments: If True, prefer axes with more segments (more granular breakdown)

    Returns:
        Tuple of (best_axis, segments_for_period, variance_pct):
        - best_axis: The axis that best reconciles for this period
        - segments_for_period: Dict of {segment_name: revenue} for this period from best axis
        - variance_pct: Variance percentage from consolidated revenue
    """
    if consolidated_revenue <= 0:
        return None, {}, 100.0

    def get_axis_priority(axis):
        """Extract axis priority from full axis name."""
        axis_name = axis.split(':')[-1] if ':' in axis else axis
        return axis_priority_map.get(axis_name, 99)

    # Group segments by axis for this specific period
    segments_by_axis_for_period = defaultdict(dict)

    for segment_key, periods_data in all_segment_data.items():
        # Skip operating income entries
        if segment_key.endswith('|OI'):
            continue

        if '|' in segment_key:
            segment_name, axis = segment_key.rsplit('|', 1)
        else:
            segment_name, axis = segment_key, ''

        # Convert to quarterly if needed and get this period's value
        quarterly_data = convert_cumulative_to_quarterly(periods_data, fiscal_year_end)
        period_value = quarterly_data.get(period, 0)

        if period_value > 0:
            segments_by_axis_for_period[axis][segment_name] = period_value

    if not segments_by_axis_for_period:
        return None, {}, 100.0

    # Find the axis that best reconciles with consolidated revenue
    best_axis = None
    best_variance = float('inf')
    best_segments = {}

    # In default mode, detect single-segment business axes (e.g., PFE's "Biopharma").
    # These are valid single-reportable-segment filers and should be preferred over
    # ProductOrServiceAxis which would show 40+ individual products.
    single_segment_business_axis = None
    if not use_subsegments:
        for axis, segments in segments_by_axis_for_period.items():
            axis_name = axis.split(':')[-1] if ':' in axis else axis
            if axis_name in ('StatementBusinessSegmentsAxis', 'SegmentsAxis') and len(segments) == 1:
                single_segment_business_axis = axis
                break

    # First pass: find best reconciling axis
    # When use_subsegments is True, prefer higher-priority axes (more granular) as long as
    # their reconciliation variance is reasonable (within 50% of consolidated revenue).
    # This allows ProductOrServiceAxis to win over StatementBusinessSegmentsAxis even when
    # the product-level axis has slightly worse reconciliation.
    for axis, segments in segments_by_axis_for_period.items():
        if len(segments) < 2:
            continue  # Need at least 2 segments

        # Sum all segments for this axis
        axis_total = sum(segments.values())
        variance_pct = abs(axis_total - consolidated_revenue) / consolidated_revenue * 100 if consolidated_revenue > 0 else 100.0

        priority = get_axis_priority(axis)

        if use_subsegments:
            # In subsegments mode, prefer the axis with best priority (most granular)
            # as long as variance is reasonable (<50%). Only override for much better variance.
            if variance_pct < 50.0:  # Axis must have reasonable reconciliation
                if (priority < get_axis_priority(best_axis or '')) or \
                   (priority == get_axis_priority(best_axis or '') and len(segments) > len(best_segments)) or \
                   (best_variance >= 50.0):  # Always beat an unreasonable previous best
                    best_variance = variance_pct
                    best_axis = axis
                    best_segments = segments.copy()
        else:
            # Default mode: prefer axis with better reconciliation, breaking ties by axis priority
            if (variance_pct < best_variance - 1.0) or \
               (abs(variance_pct - best_variance) < 1.0 and priority < get_axis_priority(best_axis or '')):
                best_variance = variance_pct
                best_axis = axis
                best_segments = segments.copy()

    # Second pass: if variance is very high (>30%), the consolidated revenue may be wrong
    # Prefer StatementBusinessSegmentsAxis with 1-4 business segments over product-level axes
    # Skip this override in subsegments mode — user explicitly wants granular data
    if best_variance > 30.0 and not use_subsegments:
        for axis, segments in segments_by_axis_for_period.items():
            axis_name = axis.split(':')[-1] if ':' in axis else axis
            # Check if this is a business segment axis with reasonable segment count
            # Include single-segment filers (e.g., PFE "Biopharma")
            if 'StatementBusinessSegmentsAxis' in axis_name and 1 <= len(segments) <= 4:
                axis_total = sum(segments.values())
                # Use this axis if it has a reasonable total (>$1B for major companies)
                if axis_total > 1_000_000_000:
                    best_axis = axis
                    best_segments = segments.copy()
                    best_variance = abs(axis_total - consolidated_revenue) / consolidated_revenue * 100 if consolidated_revenue > 0 else 100.0
                    break

    # In default mode, if the selected axis has too many segments (>20), it's likely
    # product-level detail, not business segments. If a single-segment business axis
    # exists, prefer it instead.
    if not use_subsegments and single_segment_business_axis and best_axis != single_segment_business_axis:
        if len(best_segments) > 20:
            seg = segments_by_axis_for_period.get(single_segment_business_axis, {})
            best_axis = single_segment_business_axis
            best_segments = seg.copy()
            axis_total = sum(best_segments.values())
            best_variance = abs(axis_total - consolidated_revenue) / consolidated_revenue * 100 if consolidated_revenue > 0 else 100.0

    # Fallback: if no axis reconciles well, use highest priority axis with most segments
    if best_axis is None:
        for axis, segments in sorted(segments_by_axis_for_period.items(),
                                     key=lambda x: (get_axis_priority(x[0]), -len(x[1]))):
            if len(segments) >= 1:
                best_axis = axis
                best_segments = segments.copy()
                axis_total = sum(segments.values())
                best_variance = abs(axis_total - consolidated_revenue) / consolidated_revenue * 100 if consolidated_revenue > 0 else 100.0
                break

    # If best single axis has poor reconciliation (>10% variance), try cross-axis aggregation
    # This handles cases where segments are split across different axes (e.g., after restructuring)
    if best_variance > 10.0 and len(segments_by_axis_for_period) > 1:
        # Try to find a combination of segments from different axes that reconciles better
        # Strategy: start with best axis, add segments from other axes if they improve reconciliation
        combined_segments = best_segments.copy()
        combined_total = sum(combined_segments.values())

        for other_axis, other_segments in segments_by_axis_for_period.items():
            if other_axis == best_axis:
                continue

            # Check if segments from this axis are complementary (not duplicates)
            # Segments are likely duplicates if they have similar values AND similar names
            for seg_name, seg_value in other_segments.items():
                is_duplicate = False
                for existing_name, existing_value in combined_segments.items():
                    # Check for value similarity (within 5%)
                    if existing_value > 0:
                        value_diff_pct = abs(seg_value - existing_value) / existing_value * 100
                        if value_diff_pct < 5:
                            is_duplicate = True
                            break
                    # Check for name similarity (simplified check)
                    existing_lower = existing_name.lower()
                    seg_lower = seg_name.lower()
                    # Known name mappings for segment renames
                    rename_pairs = [
                        ('pharmaceutical', 'innovative medicine'),
                        ('medical devices', 'med tech'),
                        ('medtech', 'med tech'),
                    ]
                    for old_name, new_name in rename_pairs:
                        if (old_name in existing_lower and new_name in seg_lower) or \
                           (new_name in existing_lower and old_name in seg_lower):
                            is_duplicate = True
                            break
                    if is_duplicate:
                        break

                if not is_duplicate:
                    # Add this segment to the combined set
                    # But only if it improves reconciliation
                    test_total = combined_total + seg_value
                    test_variance = abs(test_total - consolidated_revenue) / consolidated_revenue * 100 if consolidated_revenue > 0 else 100.0
                    if test_variance < best_variance:
                        combined_segments[seg_name] = seg_value
                        combined_total = test_total
                        best_variance = test_variance

        # Use combined segments if they reconcile better
        if len(combined_segments) > len(best_segments):
            best_segments = combined_segments
            best_axis = 'COMBINED'  # Mark as combined

    return best_axis, best_segments, best_variance


def build_segment_fingerprints(all_segment_data, consolidated_revenue_quarterly, periods, fiscal_year_end):
    """Build fingerprints for each segment in each period for smart matching.

    A fingerprint contains: revenue, % of total, segment name
    This allows matching segments across restructurings when names change.

    Args:
        all_segment_data: Dict of segment_key -> {period -> revenue}
        consolidated_revenue_quarterly: Dict of period -> consolidated revenue
        periods: List of period dates
        fiscal_year_end: Fiscal year end in MMDD format

    Returns:
        Dict of quarter_label -> {segment_name -> {'revenue': float, 'pct_of_total': float}}
    """
    fingerprints = defaultdict(dict)

    for segment_key, period_data in all_segment_data.items():
        # Skip operating income entries
        if segment_key.endswith('|OI'):
            continue

        # Extract segment name from key (format: "SegmentName|Axis")
        segment_name = segment_key.split('|')[0] if '|' in segment_key else segment_key

        for period, revenue in period_data.items():
            if revenue <= 0:
                continue

            quarter_label = get_quarter_label(period, fiscal_year_end)
            consolidated_rev = consolidated_revenue_quarterly.get(period, 0)

            pct_of_total = (revenue / consolidated_rev * 100) if consolidated_rev > 0 else 0

            fingerprints[quarter_label][segment_name] = {
                'revenue': revenue,
                'pct_of_total': pct_of_total,
                'period': period
            }

    return fingerprints


def _name_similarity(name_a: str, name_b: str) -> float:
    """Calculate name similarity between two segment names.

    Uses SequenceMatcher ratio on lowercased names. Also checks for
    substring containment (one name contained in the other) which handles
    cases like 'Oncology' -> 'Oncology Products'.

    Returns:
        Float between 0.0 and 1.0 indicating similarity.
    """
    a_lower = name_a.strip().lower()
    b_lower = name_b.strip().lower()

    # Exact match (case-insensitive)
    if a_lower == b_lower:
        return 1.0

    # Substring containment: "Oncology" in "Oncology Products" => high similarity
    if a_lower in b_lower or b_lower in a_lower:
        # Scale by length ratio so very short substrings don't over-match
        shorter = min(len(a_lower), len(b_lower))
        longer = max(len(a_lower), len(b_lower))
        if shorter >= 3 and shorter / longer >= 0.4:
            return 0.85

    return SequenceMatcher(None, a_lower, b_lower).ratio()


def find_matching_segment(current_segment, current_fingerprint, prior_quarter_fingerprints,
                          already_matched_segments, tolerance_pct=15.0, tolerance_revenue_ratio=0.35,
                          min_name_similarity=0.55):
    """Find the best matching segment from prior year when exact name match fails.

    Uses a combination of name similarity AND revenue fingerprint matching.
    Name similarity acts as a gate: segments with completely different names
    (e.g., 'BLINCYTO' vs 'Aranesp') are never matched regardless of revenue similarity.

    Args:
        current_segment: Name of current segment to match
        current_fingerprint: Dict with 'revenue' and 'pct_of_total' for current segment
        prior_quarter_fingerprints: Dict of segment_name -> fingerprint for prior year quarter
        already_matched_segments: Set of segment names already matched (to avoid double-matching)
        tolerance_pct: Max difference in % of total to consider a match (default 15 percentage points)
        tolerance_revenue_ratio: Max revenue ratio difference (default 35% = allows for organic growth)
        min_name_similarity: Minimum name similarity ratio to consider a match (default 0.55).
            This prevents matching completely unrelated product names.

    Returns:
        Tuple of (matched_segment_name, confidence, match_details) or (None, None, None) if no match
        confidence: 'high' (exact name), 'medium' (fingerprint match), 'low' (weak match)
    """
    if not prior_quarter_fingerprints or not current_fingerprint:
        return None, None, None

    current_revenue = current_fingerprint.get('revenue', 0)
    current_pct = current_fingerprint.get('pct_of_total', 0)

    if current_revenue <= 0:
        return None, None, None

    # First, try exact name match
    if current_segment in prior_quarter_fingerprints:
        return current_segment, 'high', {'match_type': 'exact_name'}

    # Score all potential matches — require BOTH name similarity AND revenue fingerprint match
    candidates = []

    for prior_segment, prior_fp in prior_quarter_fingerprints.items():
        # Skip if already matched to another current segment
        if prior_segment in already_matched_segments:
            continue

        prior_revenue = prior_fp.get('revenue', 0)
        prior_pct = prior_fp.get('pct_of_total', 0)

        if prior_revenue <= 0:
            continue

        # Gate 1: Name similarity check — reject if names are too different
        name_sim = _name_similarity(current_segment, prior_segment)
        if name_sim < min_name_similarity:
            continue

        # Gate 2: Revenue fingerprint check
        pct_diff = abs(current_pct - prior_pct)
        revenue_ratio = current_revenue / prior_revenue if prior_revenue > 0 else float('inf')
        revenue_ratio_diff = abs(1.0 - revenue_ratio)  # How far from 1:1 ratio

        if pct_diff <= tolerance_pct and revenue_ratio_diff <= tolerance_revenue_ratio:
            # Score: lower is better (weighted combination — name similarity bonus reduces score)
            fingerprint_score = pct_diff * 2 + revenue_ratio_diff * 100
            name_bonus = (1.0 - name_sim) * 50  # Lower bonus for higher similarity
            score = fingerprint_score + name_bonus
            candidates.append({
                'segment': prior_segment,
                'score': score,
                'pct_diff': pct_diff,
                'revenue_ratio': revenue_ratio,
                'prior_revenue': prior_revenue,
                'prior_pct': prior_pct,
                'name_similarity': name_sim
            })

    if not candidates:
        return None, None, None

    # Sort by score (lower is better)
    candidates.sort(key=lambda x: x['score'])
    best = candidates[0]

    # Determine confidence based on match quality
    if best['pct_diff'] <= 5 and abs(1.0 - best['revenue_ratio']) <= 0.15 and best['name_similarity'] >= 0.7:
        confidence = 'medium'  # Strong fingerprint + name match
    else:
        confidence = 'low'  # Weaker match, more uncertainty

    match_details = {
        'match_type': 'fingerprint',
        'pct_diff': best['pct_diff'],
        'revenue_ratio': best['revenue_ratio'],
        'name_similarity': best['name_similarity'],
        'score': best['score']
    }

    return best['segment'], confidence, match_details


def calculate_yoy_with_smart_matching(current_segment, current_revenue, current_pct_of_total,
                                       current_quarter_label, segment_fingerprints,
                                       revenue_series, quarter_label_to_period,
                                       segment_match_cache,
                                       anomaly_threshold_high=200, anomaly_threshold_low=-60):
    """Calculate YoY growth using smart segment matching.

    First tries exact name match, then falls back to fingerprint-based matching
    for handling corporate restructurings (renames, spin-offs).

    Includes anomaly detection to flag extreme YoY values that may indicate
    data issues from corporate restructurings (spin-offs, segment renames)
    where newer filings contain restated historical data.

    Args:
        current_segment: Name of current segment
        current_revenue: Revenue for current period
        current_pct_of_total: % of total revenue for current period
        current_quarter_label: e.g., 'FY2024 Q1'
        segment_fingerprints: Fingerprints built by build_segment_fingerprints()
        revenue_series: Dict of period -> revenue for current segment
        quarter_label_to_period: Mapping of quarter label -> period date
        segment_match_cache: Dict to cache matches for consistency across quarters
        anomaly_threshold_high: YoY % above this is flagged as anomaly (default: 200%)
        anomaly_threshold_low: YoY % below this is flagged as anomaly (default: -60%)

    Returns:
        Tuple of (yoy_growth_pct, confidence, matched_segment)
        - yoy_growth_pct: Float percentage or None if no match
        - confidence: 'high', 'medium', 'low', 'anomaly', or None
        - matched_segment: Name of matched prior-year segment
    """
    prior_year_label = get_prior_year_quarter_label(current_quarter_label)
    if not prior_year_label:
        return None, None, None

    # Get prior year period
    prior_year_period = quarter_label_to_period.get(prior_year_label)
    if not prior_year_period:
        return None, None, None

    # Try exact name match first (from revenue_series which is segment-specific)
    prior_year_revenue = revenue_series.get(prior_year_period, 0)
    if prior_year_revenue > 0:
        yoy_growth = ((current_revenue - prior_year_revenue) / prior_year_revenue) * 100

        # Check for anomalous YoY values that indicate data issues
        # This can happen when newer filings contain restated historical data
        # with different segment definitions (e.g., JNJ post-Kenvue spinoff)
        if yoy_growth > anomaly_threshold_high or yoy_growth < anomaly_threshold_low:
            return yoy_growth, 'anomaly', current_segment

        return yoy_growth, 'high', current_segment

    # No exact match - try fingerprint-based matching
    prior_quarter_fingerprints = segment_fingerprints.get(prior_year_label, {})
    if not prior_quarter_fingerprints:
        return None, None, None

    # Check if we've already matched this segment in previous quarters (cache for consistency)
    cache_key = current_segment
    if cache_key in segment_match_cache:
        matched_segment = segment_match_cache[cache_key]
        # Get revenue for the matched segment in prior year
        matched_fp = prior_quarter_fingerprints.get(matched_segment, {})
        matched_revenue = matched_fp.get('revenue', 0)
        if matched_revenue > 0:
            yoy_growth = ((current_revenue - matched_revenue) / matched_revenue) * 100
            return yoy_growth, 'medium', matched_segment

    # Find best match using fingerprints
    current_fingerprint = {
        'revenue': current_revenue,
        'pct_of_total': current_pct_of_total
    }

    # Track which segments are already matched in this quarter
    already_matched = set(segment_match_cache.values())

    matched_segment, confidence, match_details = find_matching_segment(
        current_segment,
        current_fingerprint,
        prior_quarter_fingerprints,
        already_matched
    )

    if matched_segment and confidence:
        # Cache the match for consistency
        segment_match_cache[cache_key] = matched_segment

        # Get the matched segment's revenue
        matched_fp = prior_quarter_fingerprints.get(matched_segment, {})
        matched_revenue = matched_fp.get('revenue', 0)

        if matched_revenue > 0:
            yoy_growth = ((current_revenue - matched_revenue) / matched_revenue) * 100
            return yoy_growth, confidence, matched_segment

    return None, None, None
