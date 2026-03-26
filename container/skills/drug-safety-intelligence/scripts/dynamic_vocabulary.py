"""Dynamic vocabulary builder for drug safety intelligence.

Replaces all hardcoded term lists with data fetched from MCP servers:
- Brand names + manufacturer names from FDA labels (for noise filtering)
- Top adverse event terms from FAERS (for AE extraction and canonical dedup)
- Drug generic names / synonyms from ChEMBL (for noise filtering)

No hardcoded drug names, brand names, company names, or AE terms.
Spelling/typo normalization uses fuzzy matching against FAERS MedDRA PTs
(difflib.get_close_matches), not hardcoded correction tables.
"""

from typing import Dict, Any, List, Set, Optional
from difflib import get_close_matches


def build_noise_set_from_label(label_result: Dict) -> Set[str]:
    """Extract brand names, manufacturer names, and generic names from a single FDA label response.

    Called during the label comparison loop — no extra API calls needed.
    """
    noise = set()

    data = label_result.get('data', {})
    results = data.get('results', [])
    if not results:
        return noise

    openfda = results[0].get('openfda', {})

    # Brand names (e.g., ["KEYTRUDA"])
    for bn in openfda.get('brand_name', []):
        if bn and isinstance(bn, str):
            noise.add(bn.lower().strip())
            # Also add individual words for multi-word brands (e.g., "HUMIRA PEN")
            for word in bn.lower().split():
                if len(word) > 3:
                    noise.add(word)

    # Manufacturer names (e.g., ["Merck Sharp & Dohme LLC"])
    for mn in openfda.get('manufacturer_name', []):
        if mn and isinstance(mn, str):
            mn_lower = mn.lower().strip()
            noise.add(mn_lower)
            # Add individual significant words
            for word in mn_lower.replace(',', ' ').replace('&', ' ').split():
                word = word.strip().rstrip('.')
                # Skip generic corporate suffixes
                if word and len(word) > 3 and word not in {
                    'inc', 'inc.', 'llc', 'ltd', 'corp', 'corporation',
                    'labs', 'laboratories', 'pharma', 'pharmaceutical',
                    'pharmaceuticals', 'company', 'and', 'the',
                }:
                    noise.add(word)

    # Generic/substance names
    for gn in openfda.get('generic_name', []):
        if gn and isinstance(gn, str):
            noise.add(gn.lower().strip())
            # Multi-ingredient names: "NIVOLUMAB AND RELATLIMAB"
            for part in gn.lower().replace(' and ', ',').split(','):
                part = part.strip()
                if part and len(part) > 3:
                    noise.add(part)

    # Substance name
    for sn in openfda.get('substance_name', []):
        if sn and isinstance(sn, str):
            noise.add(sn.lower().strip())

    return noise


def build_noise_set_from_drug_names(drug_names: List[str]) -> Set[str]:
    """Build baseline noise set from the drug names being analyzed.

    Drug names themselves should be filtered as noise in risk event names.
    """
    noise = set()
    for dn in drug_names:
        if dn:
            noise.add(dn.lower().strip())
            # First word of multi-word names
            first = dn.lower().split()[0]
            if len(first) > 3:
                noise.add(first)
    return noise


def fetch_faers_top_aes(
    fda_lookup_func,
    drug_names: List[str],
    limit: int = 50,
) -> List[str]:
    """Fetch top adverse event terms from FAERS for the drug class.

    Uses openFDA drug/event endpoint with MedDRA preferred term counts.
    Returns lowercase MedDRA PT strings sorted by frequency.

    This replaces hardcoded known_warnings and known_ars lists.
    """
    if not fda_lookup_func or not drug_names:
        return []

    # Try each drug individually until we get results
    for drug_name in drug_names[:3]:
        try:
            search_term = drug_name.strip()

            result = fda_lookup_func(
                search_term=search_term,
                search_type='adverse_events',
                count='patient.reaction.reactionmeddrapt.exact',
                limit=limit,
            )

            if not result:
                continue

            data = result.get('data', {})
            results = data.get('results', [])
            if not results:
                continue

            # Extract terms — FAERS returns them in ALL CAPS MedDRA format
            terms = []
            for r in results:
                term = r.get('term', '')
                if term and isinstance(term, str):
                    terms.append(term.lower())

            if terms:
                return terms

        except Exception as e:
            print(f"  Warning: FAERS AE query failed for {drug_name}: {e}")

    return []


def faers_terms_to_warning_vocabulary(faers_terms: List[str]) -> List[str]:
    """Convert FAERS terms to warning-category vocabulary.

    FAERS returns fine-grained MedDRA PTs like 'nausea', 'diarrhoea'.
    For W&P section matching (Strategy 2), we need broader category stems
    like 'hemorrhag', 'hepatotoxic', 'cardiac'.

    Extracts stems from FAERS terms + adds broader category patterns.
    """
    stems = set()
    for term in faers_terms:
        t = term.lower().strip()
        if len(t) < 4:
            continue
        # Use the first significant word as a stem
        words = t.split()
        if words:
            stem = words[0]
            if len(stem) >= 4:
                # Truncate to get stems (e.g., "haemorrhage" → "haemorrhag")
                if len(stem) > 8:
                    stems.add(stem[:len(stem) - 1])  # chop last char for stemming
                stems.add(stem)

    return sorted(stems)


def faers_terms_to_ar_vocabulary(faers_terms: List[str]) -> List[str]:
    """Convert FAERS terms to adverse reaction vocabulary.

    For AR section matching (Strategy 2), we need exact MedDRA PTs
    to search for in FDA label text.
    """
    # Filter to terms that look like clinical AE names (not sentences)
    terms = []
    for t in faers_terms:
        t = t.lower().strip()
        words = t.split()
        if 1 <= len(words) <= 4 and len(t) >= 4 and len(t) <= 50:
            terms.append(t)
    return terms


def build_canonical_map_from_faers(faers_terms: List[str]) -> Dict[str, str]:
    """Build canonical event name mapping from FAERS MedDRA preferred terms.

    Maps each FAERS term to itself (exact match lookup). This provides a fast
    exact-match path before falling through to the slower fuzzy_match_to_faers.

    No hardcoded synonym groups or spelling corrections — fuzzy matching
    handles typos, US/UK spelling, and clinical synonyms automatically.
    """
    canonical = {}
    for term in faers_terms:
        t = term.lower().strip()
        if len(t) >= 4:
            canonical[t] = t
    return canonical


def fuzzy_match_to_faers(term: str, faers_terms: List[str], cutoff: float = 0.75) -> Optional[str]:
    """Fuzzy-match a term against FAERS MedDRA preferred terms.

    Uses difflib.get_close_matches (SequenceMatcher ratio) — no external deps.
    Handles typos ('arrythmia' → 'arrhythmia'), US/UK spelling
    ('haemorrhage' → 'hemorrhage'), and minor variants automatically.

    Args:
        term: The event name to normalize (lowercase)
        faers_terms: List of FAERS MedDRA PTs (lowercase)
        cutoff: Minimum similarity ratio (0-1). Default 0.75 balances
                catching typos without false merges.

    Returns:
        Closest FAERS PT if similarity >= cutoff, else None
    """
    if not term or not faers_terms:
        return None

    t = term.lower().strip()
    if len(t) < 4:
        return None

    # Exact match first (fast path)
    if t in faers_terms:
        return t

    # For multi-word terms, try matching just the key word (first significant word)
    # This catches "cardiac arrhythmias" → "arrhythmia" etc.
    words = t.split()
    candidates = faers_terms

    # Fuzzy match the full term
    matches = get_close_matches(t, candidates, n=1, cutoff=cutoff)
    if matches:
        return matches[0]

    # For multi-word terms, also try matching the longest word
    if len(words) > 1:
        longest_word = max(words, key=len)
        if len(longest_word) >= 5:
            matches = get_close_matches(longest_word, candidates, n=1, cutoff=cutoff)
            if matches:
                return matches[0]

    return None
