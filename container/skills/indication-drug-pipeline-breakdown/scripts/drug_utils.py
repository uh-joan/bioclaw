"""Drug name normalization and cleaning utilities."""
import re
from typing import Optional

from constants import (
    NON_DRUG_ITEMS,
    COMBINATION_PATTERNS,
    DISPLAY_STRIP_TERMS,
    FORMULATION_TERMS,
)


def normalize_drug_name(drug_name: str) -> str:
    """
    Normalize drug name for FDA lookup by stripping dosages, formulations, and common suffixes.

    Examples:
        "Tirzepatide 15 mg SC injection" -> "tirzepatide"
        "Semaglutide Injectable Product" -> "semaglutide"
        "Cladribine Subcutaneous Injection" -> "cladribine"
        "Tyruko Injectable Product" -> "tyruko"
        "Metformin HCl 500mg tablets" -> "metformin"
        "HRS-4729 injection" -> "hrs-4729"

    Args:
        drug_name: Raw drug name from clinical trial

    Returns:
        Normalized drug name (lowercase, stripped of dosages/formulations)
    """
    if not drug_name:
        return ""

    name = drug_name.lower().strip()

    # Remove dosage patterns (e.g., "15 mg", "500mg", "0.5 mg/ml", "100 iu")
    name = re.sub(r'\d+\.?\d*\s*(mg|mcg|ug|µg|g|ml|l|iu|units?|%)\b', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\d+\.?\d*\s*/\s*\d*\.?\d*\s*(mg|mcg|ml|l)\b', '', name, flags=re.IGNORECASE)

    # Remove common formulation/dosage form terms (these are NOT part of drug names)
    # Order matters - longer phrases first to avoid partial matches
    for term in FORMULATION_TERMS:
        name = re.sub(rf'\b{term}\b', '', name, flags=re.IGNORECASE)

    # Remove parenthetical content (e.g., "(Progestin)")
    name = re.sub(r'\([^)]*\)', '', name)

    # Remove trailing numbers/letters often used for versions (e.g., "Drug 123", "Drug A")
    name = re.sub(r'\s+\d+$', '', name)
    name = re.sub(r'\s+[a-z]$', '', name)

    # Clean up extra whitespace and punctuation
    name = re.sub(r'[-_/,]+', ' ', name)
    name = re.sub(r'\s+', ' ', name)
    name = name.strip()

    return name


def clean_drug_name_for_display(drug_name: str) -> list:
    """
    Clean drug name for display in Notable Drugs section.

    Unlike normalize_drug_name (for FDA lookup), this:
    1. Preserves proper capitalization for readability
    2. Splits combination entries into individual drugs
    3. Filters out non-drug items entirely
    4. Returns a list (may be multiple drugs from one entry)

    Examples:
        "Injection, Triamcinolone Hexacetonide, Per 5 Mg" -> ["Triamcinolone Hexacetonide"]
        "tocilizumab and IV steroids combination" -> ["Tocilizumab"]
        "Prednisone+Tofacitinib" -> ["Prednisone", "Tofacitinib"]
        "Cladribine High Dose" -> ["Cladribine"]
        "Placebo for hydrocortisone" -> []
        "FDG" -> [] (diagnostic tracer, not a drug)
        "5% dextrose injection" -> []
        "CD19-BCMA Targeted CAR-T Dose 1" -> ["CD19-BCMA CAR-T"]

    Args:
        drug_name: Raw drug name from clinical trial

    Returns:
        List of cleaned drug names (may be empty, one, or multiple)
    """
    if not drug_name:
        return []

    name = drug_name.strip()

    # Quick check: if entire name is a non-drug item, skip
    name_lower = name.lower()
    for non_drug in NON_DRUG_ITEMS:
        if name_lower == non_drug or name_lower.startswith(non_drug + ' ') or name_lower.endswith(' ' + non_drug):
            return []

    # Check for "Placebo for X" pattern
    if re.match(r'^placebo\s+(for|of)\s+', name_lower):
        return []

    # Check for percentage-based items (likely vehicles/placebos)
    if re.match(r'^\d+\.?\d*\s*%', name_lower):
        return []

    # Check for descriptive phrases that aren't drug names
    # e.g., "Addition of rituximab if recurrence" -> extract "rituximab"
    addition_match = re.match(r'^addition\s+of\s+(\w+)', name_lower)
    if addition_match:
        drug_candidate = addition_match.group(1)
        # If rest has "if" clause, just return the drug
        if ' if ' in name_lower:
            return [drug_candidate.capitalize()]

    # Skip entries that are clearly descriptions, not drug names
    # These typically contain conditional/descriptive words
    descriptive_patterns = [
        r'\bif\s+(recurrence|relapse|failure|needed)',
        r'\bas\s+needed\b',
        r'\bwhen\s+',
        r'\bafter\s+\d+',
        r'\bprior\s+to\b',
        r'\bbefore\s+',
    ]
    for pattern in descriptive_patterns:
        if re.search(pattern, name_lower):
            # Try to extract just the drug name before the descriptive part
            drug_match = re.match(r'^(?:addition\s+of\s+)?(\w+[-\w]*)', name)
            if drug_match and len(drug_match.group(1)) > 2:
                drug_name_cleaned = drug_match.group(1)
                # Validate it's not just a noise word
                if drug_name_cleaned.lower() not in NON_DRUG_ITEMS:
                    return [drug_name_cleaned]
            return []

    # Handle combination drugs with parenthetical content like "CagriSema (Cagrilintide/Semaglutide)"
    # Extract brand name before parentheses AND components inside
    paren_match = re.match(r'^([A-Za-z][\w-]*)\s*\((.+)\)$', name)
    if paren_match:
        brand_name = paren_match.group(1).strip()
        paren_content = paren_match.group(2).strip()

        # Start with the brand name
        drugs = [brand_name]

        # Split parenthetical content by combination patterns to get components
        components = [paren_content]
        for pattern in COMBINATION_PATTERNS:
            new_components = []
            for c in components:
                parts = re.split(pattern, c, flags=re.IGNORECASE)
                new_components.extend([p.strip() for p in parts if p.strip()])
            components = new_components

        # Add components (they're the generic names)
        drugs.extend(components)
    else:
        # No parentheses - split by combination patterns directly
        drugs = [name]
        for pattern in COMBINATION_PATTERNS:
            new_drugs = []
            for d in drugs:
                parts = re.split(pattern, d, flags=re.IGNORECASE)
                new_drugs.extend([p.strip() for p in parts if p.strip()])
            drugs = new_drugs

    # Clean each drug individually
    cleaned_drugs = []
    for drug in drugs:
        cleaned = _clean_single_drug_for_display(drug)
        if cleaned:
            cleaned_drugs.append(cleaned)

    # Deduplicate while preserving order
    seen = set()
    result = []
    for d in cleaned_drugs:
        d_lower = d.lower()
        if d_lower not in seen:
            seen.add(d_lower)
            result.append(d)

    return result


def _clean_single_drug_for_display(drug_name: str) -> Optional[str]:
    """
    Clean a single drug name for display.

    Returns None if the drug should be excluded.
    """
    if not drug_name:
        return None

    name = drug_name.strip()
    name_lower = name.lower()

    # Filter out non-drug items
    for non_drug in NON_DRUG_ITEMS:
        if non_drug in name_lower:
            # Check if it's a significant part of the name
            if name_lower == non_drug:
                return None
            # "Placebo" anywhere means it's not a real drug entry
            if 'placebo' in name_lower:
                return None
            # "Control" at start or end
            if name_lower.startswith('control') or name_lower.endswith('control'):
                return None

    # Handle "Injection, Drug Name, Per X Mg" format (HCPCS-style)
    if name_lower.startswith('injection,'):
        parts = name.split(',')
        if len(parts) >= 2:
            # Second part is usually the drug name
            name = parts[1].strip()
            name_lower = name.lower()

    # Strip dosage patterns (preserve case by working on lowercase for matching)
    # Remove dosage amounts like "15 mg", "500mg", "0.5 mg/ml", "100 iu", "0.003%"
    name = re.sub(r'\d+\.?\d*\s*%', '', name)
    name = re.sub(r'\d+\.?\d*\s*(mg|mcg|ug|µg|g|ml|l|iu|units?)\b', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\d+\.?\d*\s*/\s*\d*\.?\d*\s*(mg|mcg|ml|l)\b', '', name, flags=re.IGNORECASE)

    # Strip formulation/dosage form terms (case-insensitive but preserve rest of case)
    for term in DISPLAY_STRIP_TERMS:
        # Use word boundaries to avoid partial matches
        name = re.sub(rf'\b{re.escape(term)}\b', '', name, flags=re.IGNORECASE)

    # Remove parenthetical content that's just clarification or abbreviations
    # e.g., "(JAK inhibitor users need to double...)" but keep "(Acoltremon...)"
    # Remove if parenthetical contains common non-drug words or is just an abbreviation
    def should_remove_paren(match):
        content = match.group(1).strip()
        content_lower = content.lower()

        # Remove short abbreviations (2-5 chars, all letters) like (AZA), (MTX), (TNF)
        if re.match(r'^[A-Za-z]{2,5}$', content):
            return True

        noise_words = ['users', 'patients', 'need', 'double', 'initial', 'dose',
                       'previously', 'formerly', 'also known', 'aka']
        return any(word in content_lower for word in noise_words)

    name = re.sub(r'\(([^)]+)\)', lambda m: '' if should_remove_paren(m) else m.group(0), name)

    # Now clean up remaining parentheticals that are just manufacturer names
    name = re.sub(r'\s*\([^)]*(?:viatris|mylan|teva|sandoz|accord)[^)]*\)', '', name, flags=re.IGNORECASE)

    # Clean up parentheticals that are empty or just whitespace (e.g., "TRYPTYR (Acoltremon )")
    name = re.sub(r'\s*\(\s*\)', '', name)  # Empty parens
    name = re.sub(r'\s*\(\s+\)', '', name)  # Parens with only whitespace

    # Remove trailing "combination" word
    name = re.sub(r'\s+combination\s*$', '', name, flags=re.IGNORECASE)

    # Remove trailing single-letter version suffixes (e.g., "Cagrilintide B" -> "Cagrilintide")
    # These are clinical trial version designators, not part of the drug name
    # BUT preserve Vitamin letters (B, C, D, E, K) and other legitimate suffixes
    # Check if stripping would leave a drug-like base name
    trailing_letter_match = re.match(r'^(.+?)\s+([A-Z]|I{1,3}|IV|V|VI{0,3})$', name)
    if trailing_letter_match:
        base_name = trailing_letter_match.group(1)
        # Drug name patterns: -mab, -nib, -tide, etc. or alphanumeric codes like NNC0442
        drug_suffix_pattern = r'(mab|nib|tide|zumab|tinib|ciclib|parin|statin|olol|pril|sartan|glitide|glutide|semide|lukast|\d{3,})$'
        if re.search(drug_suffix_pattern, base_name, re.IGNORECASE):
            name = base_name

    # Handle "Drug - modifier" pattern (e.g., "Dupilumab - discontinuation")
    # Keep just the drug name before the hyphen-separated modifier
    name = re.sub(r'\s+-\s+\w+\s*$', '', name)

    # Remove leading/trailing punctuation and whitespace
    name = re.sub(r'^[\s,;:\-]+', '', name)
    name = re.sub(r'[\s,;:\-]+$', '', name)
    name = re.sub(r'\s+', ' ', name)
    name = name.strip()

    # Final validation
    if not name or len(name) < 2:
        return None

    # Skip if it's now just a non-drug term
    if name.lower() in NON_DRUG_ITEMS:
        return None

    # Skip if it's mostly numbers/symbols (likely a code or dosage that wasn't cleaned)
    if re.match(r'^[\d\s\.\-\+%/]+$', name):
        return None

    # Capitalize properly for display
    # Handle special cases like "CAR-T", "mRNA", "siRNA"
    if name.isupper() and len(name) <= 10:
        # Short all-caps names are likely acronyms, keep as-is
        pass
    elif '-' in name:
        # Hyphenated names: capitalize each part appropriately
        parts = name.split('-')
        name = '-'.join(p.capitalize() if not p.isupper() else p for p in parts)
    else:
        # Title case but preserve existing uppercase in middle of words
        name = name[0].upper() + name[1:] if name else name

    return name


def clean_brand_name(brand_name: str, generic_name: str = "") -> Optional[str]:
    """
    Clean brand name for display by filtering out generic manufacturer names and verbose text.

    Handles issues like:
    - "Dimethyl fumarate Accord" -> None (generic + manufacturer, not a real brand)
    - "Teriflunomide Viatris (previously Teriflunomide Mylan)" -> None (same issue)
    - "NASAL ALLERGY" -> None (indication, not a brand)
    - "NVP-BAF312-AEA" -> None (internal compound code, not a brand)
    - "Gilenya" -> "Gilenya" (real brand name, keep)
    - "Ocrevus" -> "Ocrevus" (real brand name, keep)

    Args:
        brand_name: Raw brand name from API
        generic_name: Optional generic name to check for redundancy

    Returns:
        Cleaned brand name if valid, None if it should be filtered out
    """
    if not brand_name:
        return None

    brand = brand_name.strip()
    brand_lower = brand.lower()
    generic_lower = generic_name.lower() if generic_name else ""

    # Filter out internal compound codes (NOT brand names)
    # Pattern: 2-4 uppercase letters followed by hyphen and alphanumeric (e.g., NVP-BAF312-AEA, BMS-986165)
    # Real brand names don't follow this pattern
    if re.match(r'^[A-Za-z]{2,4}-[A-Za-z0-9]+-?[A-Za-z0-9]*$', brand):
        return None

    # Filter out indication/use-based names (NOT brand names)
    # These are product line names or indications that FDA returns as "brand names"
    indication_based_names = [
        'nasal allergy', 'allergy relief', 'cold relief', 'pain relief',
        'cough', 'cold', 'flu', 'sinus', 'headache', 'migraine',
        'antacid', 'laxative', 'sleep aid', 'anti-itch', 'first aid',
        'eye drops', 'ear drops', 'nasal spray',
    ]
    for indication in indication_based_names:
        if indication in brand_lower:
            return None

    # Known generic manufacturers (not brand names when appended to generic)
    generic_manufacturers = [
        'accord', 'viatris', 'mylan', 'teva', 'sandoz', 'hospira', 'fresenius',
        'aurobindo', 'apotex', 'dr. reddy', 'dr reddy', 'cipla', 'lupin', 'zydus',
        'hikma', 'amneal', 'alvogen', 'pfizer', 'novartis', 'ratiopharm',
        'stada', 'hexal', 'arrow', 'biogaran', 'zentiva', 'krka', 'actavis',
        'ranbaxy', 'watson', 'wockhardt', 'torrent', 'sun pharma', 'intas',
        'glenmark', 'macleods', 'mankind', 'ipca', 'jubilant', 'alkem',
    ]

    # Check if brand is just "Generic + Manufacturer"
    # Pattern: generic name followed by manufacturer name
    if generic_lower:
        for mfr in generic_manufacturers:
            # "Dimethyl fumarate Accord" -> skip
            if brand_lower == f"{generic_lower} {mfr}":
                return None
            # "Teriflunomide Viatris" -> skip
            if brand_lower.startswith(generic_lower) and mfr in brand_lower:
                return None

    # Check if brand name contains "(previously ...)" pattern - extract base name
    if '(previously' in brand_lower or '(formerly' in brand_lower:
        # Extract just the first part before the parenthesis
        base_brand = re.split(r'\s*\(previously|\s*\(formerly', brand, flags=re.IGNORECASE)[0].strip()
        if base_brand:
            # Recursively clean the base brand
            return clean_brand_name(base_brand, generic_name)
        return None

    # Check if brand name is essentially just the generic name
    # e.g., "Dimethyl Fumarate" brand for "dimethyl fumarate" generic
    if generic_lower and brand_lower.replace(' ', '') == generic_lower.replace(' ', ''):
        return None

    # Check if brand is just generic + a manufacturer
    for mfr in generic_manufacturers:
        if mfr in brand_lower and generic_lower:
            # Split brand and check if it's "SomeDrug Manufacturer"
            words = brand_lower.split()
            if len(words) >= 2 and words[-1] == mfr:
                # Last word is manufacturer - check if rest matches generic
                potential_generic = ' '.join(words[:-1])
                if potential_generic == generic_lower or generic_lower.startswith(potential_generic):
                    return None

    # If brand is very long (likely verbose description), try to clean it
    if len(brand) > 30:
        # Check for common verbose patterns
        if ' (' in brand:
            # Take only part before first parenthesis
            base = brand.split(' (')[0].strip()
            if base and len(base) >= 3:
                return clean_brand_name(base, generic_name)

    return brand
