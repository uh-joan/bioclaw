#!/usr/bin/env python3
"""
Ticker symbol utilities for company SWOT analysis.

This module provides functions for:
- Generating plausible ticker guesses from company names
- Finding tickers using SEC data and MCP APIs
"""

import re
from typing import List, Optional

from swot_constants import COMPANY_SUFFIXES
from sec_lookup import get_sec_company_tickers, normalize_company_name


# ============================================================================
# Ticker Constants
# ============================================================================

VOWELS = 'AEIOU'
CONSONANTS = 'BCDFGHJKLMNPQRSTVWXYZ'
CONSONANTS_NO_Y = 'BCDFGHJKLMNPQRSTVWXZ'  # Y often treated as vowel in tickers


# ============================================================================
# Ticker Generation Functions
# ============================================================================

def generate_ticker_guesses(company_name: str) -> List[str]:
    """
    Generate plausible ticker guesses from company name.

    Uses multiple heuristics based on common ticker patterns:
    - First word as-is
    - First N letters
    - Consonant-based patterns (SNDX from Syndax)
    - Initials for multi-word names (BMY from Bristol Myers)
    - Biotech patterns (NBIX, RLAY)

    Args:
        company_name: Full company name

    Returns:
        List of unique ticker guesses in priority order
    """
    guesses = []
    original_name = company_name.upper().strip()
    name = original_name

    # Remove common suffixes (but keep original for multi-word logic later)
    for suffix in COMPANY_SUFFIXES:
        name = name.replace(suffix.upper(), '')
    name = name.strip()

    first_word = name.split()[0] if ' ' in name else name

    # Guess 1: First word as-is (common for single-word companies)
    guesses.append(first_word)

    # Guess 2: First 4 letters of first word (common pattern)
    if len(first_word) >= 4:
        guesses.append(first_word[:4])

    # Guess 3: First letter + consonants (e.g., "Syndax" -> "SNDX", "Bicycle" -> "BCYC")
    # Try both with and without Y as consonant
    if first_word:
        # Version treating Y as consonant
        first_plus_consonants = first_word[0] + ''.join(c for c in first_word[1:] if c in CONSONANTS)
        if len(first_plus_consonants) >= 3:
            guesses.append(first_plus_consonants[:4])
        # Version treating Y as vowel (common in biotech tickers like SNDX from Syndax)
        first_plus_consonants_no_y = first_word[0] + ''.join(c for c in first_word[1:] if c in CONSONANTS_NO_Y)
        if len(first_plus_consonants_no_y) >= 3:
            guesses.append(first_plus_consonants_no_y[:4])

    # Guess 4: Remove vowels from middle, keep first and last char
    # e.g., "ARCUS" -> "ARCS"
    if len(first_word) >= 4:
        middle = first_word[1:-1]
        middle_no_vowels = ''.join(c for c in middle if c in CONSONANTS)
        result = first_word[0] + middle_no_vowels + first_word[-1]
        if len(result) >= 3:
            guesses.append(result[:4])

        # Also try removing first vowel entirely (ARCUS -> RCUS)
        if first_word[0] in VOWELS:
            no_first_vowel = first_word[1:]
            if len(no_first_vowel) >= 3:
                guesses.append(no_first_vowel[:4])

    # Guess 5: Consonants only
    consonants = ''.join(c for c in first_word if c in CONSONANTS)
    if len(consonants) >= 3:
        guesses.append(consonants[:4])

    # Guess 6: First 3 letters (less common but worth trying)
    if len(first_word) >= 3:
        guesses.append(first_word[:3])

    # Guess 7: Initials if multi-word (e.g., "Bristol Myers" -> "BMY")
    if ' ' in name:
        words = name.split()
        initials = ''.join(w[0] for w in words if w)
        if len(initials) >= 2:
            guesses.append(initials)

    # Guess 8: For multi-word biotech names, try first letter + second word initial + IX/X pattern
    # Common biotech pattern: Neurocrine Biosciences -> NBIX, Ultragenyx -> RARE
    # Use original_name to preserve multi-word structure before suffix removal
    if ' ' in original_name:
        original_words = original_name.split()
        if len(original_words) >= 2:
            # First letter of first word + first letter of second + common suffixes
            prefix = original_words[0][0] + original_words[1][0]
            guesses.append(prefix + 'IX')  # NBIX pattern
            guesses.append(prefix + 'X')   # NBX pattern
            guesses.append(prefix + 'I')   # NBI pattern

    # Guess 9: First word + first letter of second word (e.g., "Relay Therapeutics" -> "RLAY")
    if ' ' in original_name:
        original_words = original_name.split()
        if len(original_words) >= 2:
            # Try first 3 letters + first letter of second word
            first_part = original_words[0][:3] if len(original_words[0]) >= 3 else original_words[0]
            second_initial = original_words[1][0]
            guesses.append(first_part + second_initial)

    # Guess 10: First 2 letters + last 2 letters of first word
    # e.g., "Syndax" -> "SNDX" (already covered), but try "SYAX"
    if len(first_word) >= 4:
        guesses.append(first_word[:2] + first_word[-2:])

    # Guess 11: First letter + key consonants from middle + last letter
    # e.g., "Sarepta" -> "SRPT"
    if len(first_word) >= 5:
        middle_consonants = ''.join(c for c in first_word[1:-1] if c in CONSONANTS)[:2]
        if middle_consonants:
            guesses.append(first_word[0] + middle_consonants + first_word[-1])

    # Guess 12: First 4 consonants from first word (common for biotech)
    first_consonants = ''.join(c for c in first_word if c in CONSONANTS)[:4]
    if len(first_consonants) >= 3 and first_consonants not in guesses:
        guesses.append(first_consonants)

    # Remove duplicates while preserving order
    seen = set()
    unique_guesses = []
    for g in guesses:
        if g not in seen and len(g) >= 2:
            seen.add(g)
            unique_guesses.append(g)

    return unique_guesses


def find_ticker(company_name: str,
                lookup_company_in_sec_tickers_fn,
                search_companies_fn,
                get_company_cik_fn) -> Optional[str]:
    """
    Find stock ticker dynamically using SEC company_tickers.json and fallbacks.

    Args:
        company_name: Company name to search for
        lookup_company_in_sec_tickers_fn: Function to lookup in SEC tickers
        search_companies_fn: MCP function to search companies
        get_company_cik_fn: MCP function to get CIK by ticker

    Returns:
        Stock ticker symbol or None
    """
    # PRIMARY METHOD: Use SEC company_tickers.json (most reliable)
    sec_lookup = lookup_company_in_sec_tickers_fn(company_name)
    if sec_lookup:
        cik, ticker = sec_lookup
        return ticker

    # FALLBACK: Try MCP search_companies
    try:
        search_result = search_companies_fn(query=company_name)
        if isinstance(search_result, dict):
            companies = search_result.get('data', [])
            if companies and isinstance(companies, list):
                for company in companies:
                    if company.get('name', '').lower() == company_name.lower():
                        if company.get('ticker'):
                            return company['ticker']
                for company in companies:
                    if company.get('ticker'):
                        return company['ticker']
    except Exception:
        pass

    # LAST RESORT: Try ticker guesses with validation
    # Cross-check guessed tickers against SEC company_tickers.json to ensure
    # the ticker actually belongs to our target company (not a random match
    # like BMI = Badger Meter instead of BPMC = Blueprint Medicines)
    ticker_guesses = generate_ticker_guesses(company_name)
    search_name = normalize_company_name(company_name)
    search_words = [w for w in search_name.split() if len(w) >= 3]
    sec_tickers = get_sec_company_tickers()

    # Build ticker → company name lookup from SEC data
    ticker_to_company = {}
    if sec_tickers:
        for key, company in sec_tickers.items():
            t = company.get('ticker', '')
            if t:
                ticker_to_company[t.upper()] = company.get('title', '')

    for ticker_guess in ticker_guesses:
        try:
            # First validate the ticker exists via CIK
            cik_result = get_company_cik_fn(ticker=ticker_guess)
            ticker_valid = False
            if isinstance(cik_result, dict) and cik_result.get('cik'):
                ticker_valid = True
            elif isinstance(cik_result, str) and re.search(r'CIK:\s*\d{10}', cik_result):
                ticker_valid = True

            if ticker_valid:
                # Cross-check: verify the SEC company name for this ticker
                # shares at least one significant word with our target company
                sec_company_name = ticker_to_company.get(ticker_guess.upper(), '')
                if sec_company_name and search_words:
                    sec_normalized = normalize_company_name(sec_company_name)
                    sec_words = sec_normalized.split()
                    # At least one significant word must match
                    has_match = any(sw in sec_words or any(sw in secw or secw in sw for secw in sec_words)
                                   for sw in search_words)
                    if not has_match:
                        print(f"   Ticker {ticker_guess} maps to '{sec_company_name}', skipping (doesn't match '{company_name}')")
                        continue
                return ticker_guess
        except Exception:
            pass

    # Final fallback: return None (no valid ticker found)
    # Previously returned first word of company name, which caused silent failures downstream
    print(f"   Warning: Could not find ticker for '{company_name}'")
    return None
