#!/usr/bin/env python3
"""
SEC company lookup utilities for SWOT analysis.

This module provides functions for:
- Fetching and caching SEC company_tickers.json
- Company name normalization for matching
- Looking up CIK and ticker by company name
"""

import gzip
import json
import time
import urllib.request
from typing import Any, Dict, Optional, Tuple

from swot_constants import COMPANY_SUFFIXES


# ============================================================================
# SEC Company Tickers Cache
# ============================================================================

_SEC_TICKERS_CACHE: Optional[Dict[str, Any]] = None
_SEC_TICKERS_CACHE_TIME: Optional[float] = None
_SEC_TICKERS_CACHE_TTL = 3600  # Cache for 1 hour


def get_sec_company_tickers() -> Dict[str, Any]:
    """Fetch and cache SEC company_tickers.json for CIK/ticker lookup.

    Returns:
        dict: SEC company tickers data keyed by index
    """
    global _SEC_TICKERS_CACHE, _SEC_TICKERS_CACHE_TIME

    # Check cache validity
    if _SEC_TICKERS_CACHE and _SEC_TICKERS_CACHE_TIME:
        if time.time() - _SEC_TICKERS_CACHE_TIME < _SEC_TICKERS_CACHE_TTL:
            return _SEC_TICKERS_CACHE

    try:
        url = "https://www.sec.gov/files/company_tickers.json"
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Company Research Tool contact@example.com',
                'Accept-Encoding': 'gzip, deflate',
                'Accept': 'application/json'
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            raw_data = response.read()
            # Handle gzip-compressed response
            if raw_data[:2] == b'\x1f\x8b':  # gzip magic number
                raw_data = gzip.decompress(raw_data)
            data = json.loads(raw_data.decode('utf-8'))
            _SEC_TICKERS_CACHE = data
            _SEC_TICKERS_CACHE_TIME = time.time()
            return data
    except Exception as e:
        print(f"   Warning: Failed to fetch SEC tickers: {e}")
        return {}


def normalize_company_name(name: str) -> str:
    """Normalize company name for matching: uppercase, remove suffixes, normalize hyphens.

    Args:
        name: Raw company name

    Returns:
        str: Normalized company name (uppercase, no suffixes)
    """
    normalized = name.upper().strip()

    # Normalize hyphens, commas, periods to spaces for consistent matching
    # SEC entries like "BEIGENE, LTD." need comma/period removal to match "BeiGene"
    normalized = normalized.replace('-', ' ')
    normalized = normalized.replace(',', ' ')
    normalized = normalized.replace('.', ' ')

    # Remove common suffixes for matching (word-boundary safe)
    # Sort by length descending so longer suffixes match first
    # (e.g., ' BIOSCIENCES' before ' SCIENCES')
    sorted_suffixes = sorted(COMPANY_SUFFIXES, key=len, reverse=True)
    for suffix in sorted_suffixes:
        upper_suffix = suffix.upper()
        if normalized.endswith(upper_suffix):
            normalized = normalized[:-len(upper_suffix)]
            break  # Only remove one suffix to avoid over-stripping

    # Collapse multiple spaces and strip
    normalized = ' '.join(normalized.split())
    return normalized


def lookup_company_in_sec_tickers(company_name: str) -> Optional[Tuple[str, str]]:
    """
    Look up company in SEC tickers JSON by name.

    Uses fuzzy matching with scoring to find the best match:
    - Exact normalized name match (highest priority)
    - All words match (high priority)
    - First word exact match (medium priority)
    - Partial/prefix match (low priority)

    Args:
        company_name: Company name to search for

    Returns:
        Tuple of (cik, ticker) or None if not found
    """
    tickers_data = get_sec_company_tickers()
    if not tickers_data:
        return None

    # Normalize search term
    search_name = normalize_company_name(company_name)

    best_match = None
    best_score = 0

    for key, company in tickers_data.items():
        sec_title = company.get('title', '').upper()
        sec_ticker = company.get('ticker', '')
        sec_cik = str(company.get('cik_str', ''))

        # Normalize SEC title
        normalized_title = normalize_company_name(sec_title)

        # Exact match (highest priority)
        if normalized_title == search_name:
            return (sec_cik.zfill(10), sec_ticker)

        # Match if first word matches and second word starts with same letter
        search_words = search_name.split()
        title_words = normalized_title.split()

        if search_words and title_words:
            # For multi-word names, check if all search words appear in title
            if len(search_words) > 1:
                all_words_match = all(sw in title_words for sw in search_words)
                if all_words_match:
                    # All words match - very high score
                    score = 200 + len(search_words)
                    if score > best_score:
                        best_score = score
                        best_match = (sec_cik.zfill(10), sec_ticker)
                    continue

            if search_words[0] == title_words[0]:
                # Exact first word match
                score = 100 + len(search_words[0])
                if score > best_score:
                    best_score = score
                    best_match = (sec_cik.zfill(10), sec_ticker)
            elif search_words[0] in normalized_title or normalized_title.startswith(search_words[0]):
                # Partial match
                score = 50
                if score > best_score:
                    best_score = score
                    best_match = (sec_cik.zfill(10), sec_ticker)

    return best_match
