"""Brand name lookup utilities using FDA, EMA, DrugBank, and PubChem APIs."""
import re
from typing import Optional, Dict, Any

# All MCP functions are now accessed via mcp_funcs parameter
# No direct imports from mcp.servers.* allowed

# Cache for PubChem lookups to avoid repeated API calls
_pubchem_cache = {}


def get_drug_synonyms(drug_name: str, mcp_funcs: Dict[str, Any] = None) -> list:
    """
    Get drug name synonyms from PubChem for cross-database matching.

    EMA uses INN (International Nonproprietary Names) which may differ from US names.
    E.g., hydroxyurea (US) = hydroxycarbamide (INN/EU)

    Returns list of synonyms including the original name.
    """
    synonyms = [drug_name]

    if not mcp_funcs:
        return synonyms

    try:
        pubchem_search = mcp_funcs.get('pubchem_search')
        pubchem_synonyms = mcp_funcs.get('pubchem_synonyms')

        if not pubchem_search or not pubchem_synonyms:
            return synonyms

        result = pubchem_search(query=drug_name, max_records=1)
        if result and isinstance(result, dict):
            details = result.get('details', {})
            props = details.get('PropertyTable', {}).get('Properties', [])
            if props:
                cid = props[0].get('CID')
                if cid:
                    syn_result = pubchem_synonyms(cid=cid)
                    if syn_result and isinstance(syn_result, dict):
                        info = syn_result.get('InformationList', {}).get('Information', [])
                        if info:
                            # Get first 10 synonyms (avoid CAS numbers and internal codes)
                            for syn in info[0].get('Synonym', [])[:10]:
                                # Skip CAS numbers (format: 123-45-6)
                                if not re.match(r'^\d+-\d+-\d+$', syn):
                                    syn_clean = syn.lower().strip()
                                    if syn_clean not in [s.lower() for s in synonyms]:
                                        synonyms.append(syn)
    except:
        pass

    return synonyms


def extract_brand_name_from_description(description: str) -> str:
    """Extract brand name from DrugBank description text."""
    if not description:
        return None

    # Common patterns for brand names in descriptions
    patterns = [
        r'brand name[s]?\s+(\w+)',
        r'tradename[s]?\s+(\w+)',
        r'marketed (?:under the (?:trade)?name|as)\s+(\w+)',
        r'sold (?:under the (?:trade)?name|as)\s+(\w+)',
        r'commercially available as\s+(\w+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            brand = match.group(1)
            # Clean up common noise words that regex might capture
            noise_words = ('the', 'a', 'an', 'by', 'in', 'for', 'with', 'and', 'or', 'to', 'is', 'as')
            if brand.lower() not in noise_words and len(brand) > 2:
                return brand

    return None


def get_brand_name_from_pubchem(generic_name: str, mcp_funcs: Dict[str, Any] = None) -> Optional[str]:
    """
    Get brand name from PubChem synonyms list.

    PubChem synonyms include brand names mixed with chemical names, CAS numbers, etc.
    This function filters to extract likely brand names.

    Args:
        generic_name: Generic drug name (e.g., 'almotriptan', 'naratriptan')

    Returns:
        Brand name if found, None otherwise
    """
    if not generic_name or not mcp_funcs:
        return None

    try:
        pubchem_search = mcp_funcs.get('pubchem_search')
        pubchem_synonyms = mcp_funcs.get('pubchem_synonyms')

        if not pubchem_search or not pubchem_synonyms:
            return None

        # First search PubChem to get CID
        result = pubchem_search(query=generic_name, max_records=1)
        if not result:
            return None

        # Extract CID from result
        cid = None
        details = result.get('details', {})
        props = details.get('PropertyTable', {}).get('Properties', [])
        if props and len(props) > 0:
            cid = props[0].get('CID')

        if not cid:
            return None

        # Get synonyms for this compound
        syn_result = pubchem_synonyms(cid=cid)
        if not syn_result:
            return None

        # Extract synonyms list
        info_list = syn_result.get('InformationList', {}).get('Information', [])
        if not info_list:
            return None

        synonyms = info_list[0].get('Synonym', [])
        if not synonyms:
            return None

        generic_lower = generic_name.lower()
        generic_base = generic_lower.split()[0]

        # Patterns to skip - these are NOT brand names
        skip_patterns = (
            # Chemical nomenclature
            'acid', 'amine', 'amide', 'sulfo', 'sulfon', 'indole', 'pyrrol', 'piper',
            'methyl', 'ethyl', 'propyl', 'butyl', 'phenyl', 'benzyl', 'dimethyl',
            'hydroxy', 'chloro', 'fluoro', 'bromo', 'iodo', 'amino', 'nitro', 'oxo',
            # Salt forms
            'hydrochloride', 'malate', 'succinate', 'tartrate', 'citrate', 'fumarate',
            'sulfate', 'phosphate', 'sodium', 'potassium', 'calcium', 'magnesium',
            # Database identifiers
            'chembl', 'chebi', 'pubchem', 'drugbank', 'kegg', 'unii', 'ncgc', 'brd-',
            'dtxsid', 'dtxcid', 'schembl', 'zinc', 'hmdb', 'cas-', 'einecs', 'refchem',
            # Latin/INN forms
            '[inn]', '[usan]', '[ban]', '[mi]', '[vandf]', '[who-dd]', '[orange book]',
            'latin]', 'french]', 'spanish]', 'german]', 'czech]',
            # IUPAC patterns
            'inchi=', 'inchi/', 'smiles',
            # Other non-brand indicators
            'oral pill', 'oral tablet', 'injection', 'solution', 'capsule',
            'reference standard', 'certified', 'pharmacopoeia', 'pharmaceutical',
        )

        for synonym in synonyms:
            if not synonym or not isinstance(synonym, str):
                continue

            syn_lower = synonym.lower()

            # Skip the generic name itself
            if syn_lower == generic_lower or generic_base in syn_lower:
                continue

            # Skip if too short (likely abbreviation) or too long (likely chemical name)
            if len(synonym) < 3 or len(synonym) > 20:
                continue

            # Skip CAS numbers (pattern: digits-digits-digits)
            if '-' in synonym and any(c.isdigit() for c in synonym):
                parts = synonym.split('-')
                if len(parts) >= 3 and all(p.isdigit() for p in parts if p):
                    continue

            # Skip if contains skip patterns
            should_skip = False
            for pattern in skip_patterns:
                if pattern in syn_lower:
                    should_skip = True
                    break
            if should_skip:
                continue

            # Skip if mostly digits or has special chars (likely ID)
            digit_count = sum(1 for c in synonym if c.isdigit())
            if digit_count > len(synonym) * 0.3:
                continue

            # Skip entries with parentheses (usually qualifiers like "Naramig (TN)")
            # But extract the base name
            if '(' in synonym:
                base_name = synonym.split('(')[0].strip()
                if base_name and len(base_name) >= 3:
                    # Verify base name doesn't match skip patterns
                    base_lower = base_name.lower()
                    if base_lower != generic_lower and generic_base not in base_lower:
                        skip_base = False
                        for pattern in skip_patterns:
                            if pattern in base_lower:
                                skip_base = True
                                break
                        if not skip_base:
                            return base_name
                continue

            # This looks like a brand name - return first match
            # Brand names are typically short, capitalized words
            return synonym

    except Exception:
        pass

    return None


def get_brand_name_from_fda(generic_name: str, mcp_funcs: Dict[str, Any] = None) -> str:
    """
    Get brand name from FDA drug database using count-first pattern.

    Uses 'general' search with count aggregation to avoid token limits.
    The 'label' search type returns 110k tokens and fails (exceeds MCP limit).

    Args:
        generic_name: Generic drug name (e.g., 'voxelotor', 'crizanlizumab')

    Returns:
        Brand name if found, None otherwise
    """
    if not generic_name or not mcp_funcs:
        return None

    try:
        fda_lookup = mcp_funcs.get('fda_lookup')
        if not fda_lookup:
            return None

        # Use count-first pattern: aggregates brand names efficiently (~150 tokens)
        # This avoids the 110k token label search that exceeds MCP limits
        fda_result = fda_lookup(
            search_term=generic_name,
            search_type='general',
            count='openfda.brand_name.exact',
            limit=10
        )

        if not fda_result or not fda_result.get('success'):
            return None

        # Handle nested data structure from MCP wrapper
        data = fda_result.get('data', {})
        # The 'data' field might itself have a nested 'data' from MCP response
        if 'data' in data:
            data = data.get('data', {})
        results = data.get('results', [])

        if not results:
            return None

        # Count results return: [{'term': 'BRANDNAME', 'count': 5}, ...]
        # Filter out generic name matches and salt forms, return actual brand name
        generic_lower = generic_name.lower()
        generic_base = generic_lower.split()[0]  # First word of generic name

        # Salt forms - skip entirely (these are NOT brand names)
        salt_patterns = (
            'hydrochloride', 'hcl', 'malate', 'hydrobromide', 'sulfate', 'sulphate',
            'succinate', 'tartrate', 'citrate', 'phosphate', 'maleate', 'tosylate',
            'mesylate', 'besylate', 'fumarate', 'lactate', 'gluconate', 'pamoate',
            'acetate', 'propionate', 'butyrate', 'valerate', 'benzoate', 'salicylate',
            'stearate', 'palmitate', 'oleate', 'laurate', 'myristate',
            # Ionic forms
            'sodium', 'potassium', 'calcium', 'magnesium', 'zinc', 'aluminum',
            'chloride', 'bromide', 'iodide', 'nitrate', 'oxide', 'hydroxide',
        )

        # Dosage form suffixes - strip from brand name (e.g., "ERGOMAR SUBLINGUAL" -> "ERGOMAR")
        dosage_form_suffixes = (
            'sublingual', 'buccal', 'transdermal', 'intranasal', 'nasal',
            'extended-release', 'extended release', 'controlled release', 'cr', 'er', 'xr', 'xl', 'sr',
            'sustained release', 'delayed release', 'immediate release', 'ir',
            'injection', 'injectable', 'solution', 'suspension', 'emulsion',
            'tablet', 'tablets', 'capsule', 'capsules', 'oral', 'topical', 'ophthalmic', 'otic',
            'cream', 'ointment', 'gel', 'lotion', 'spray', 'patch', 'patches',
            'suppository', 'enema', 'inhalation', 'nebulizer', 'inhaler',
            'iv', 'im', 'sc', 'subcutaneous', 'intramuscular', 'intravenous',
        )

        for item in results:
            term = item.get('term', '')
            if not term:
                continue
            term_lower = term.lower()

            # Skip if it contains the generic name (likely a salt form)
            if generic_base in term_lower:
                continue

            # Skip if it contains salt patterns
            is_salt = False
            for pattern in salt_patterns:
                if pattern in term_lower:
                    is_salt = True
                    break
            if is_salt:
                continue

            # Skip if contains non-brand indicators
            if ' in ' in term_lower or ' with ' in term_lower or ' and ' in term_lower:
                continue

            # Strip dosage form suffixes from brand name
            clean_term = term
            for suffix in dosage_form_suffixes:
                # Check if term ends with or contains the suffix as a separate word
                suffix_upper = suffix.upper()
                if clean_term.upper().endswith(' ' + suffix_upper):
                    clean_term = clean_term[:-len(suffix)-1].strip()
                elif ' ' + suffix_upper + ' ' in clean_term.upper():
                    # Remove from middle (rare but possible)
                    idx = clean_term.upper().find(' ' + suffix_upper + ' ')
                    clean_term = clean_term[:idx] + clean_term[idx+len(suffix)+2:]
                    clean_term = clean_term.strip()

            # Return cleaned brand name if it's still valid
            if clean_term and len(clean_term) > 1:
                return clean_term

    except Exception:
        pass

    return None


def verify_fda_approval(drug_name: str, mcp_funcs: Dict[str, Any] = None) -> bool:
    """
    Verify if a drug is FDA approved.

    DrugBank's 'approved' status means approved ANYWHERE in the world, not specifically FDA.
    This function cross-checks against actual FDA databases to verify FDA approval.

    Checks in order:
    1. FDA Drug Labels API (CDER-regulated small molecules)
    2. FDA Purple Book (CBER-regulated biologics/gene therapies)
    3. EMA fallback for drugs approved in both regions

    Gene therapies (e.g., Casgevy, Lyfgenia) are regulated by CBER and are NOT in the
    standard drug labels API - they're only in the Purple Book.

    Args:
        drug_name: Drug name to verify

    Returns:
        True if drug is verified as FDA approved, False otherwise
    """
    if not drug_name or not mcp_funcs:
        return False

    try:
        fda_lookup = mcp_funcs.get('fda_lookup')
        ema_search = mcp_funcs.get('ema_search')

        if not fda_lookup:
            return False

        # Step 1: Check FDA drug labels API (CDER small molecules)
        fda_result = fda_lookup(
            search_term=drug_name,
            search_type='general',
            count='openfda.brand_name.exact',
            limit=1
        )

        if fda_result and fda_result.get('success'):
            data = fda_result.get('data', {})
            if 'data' in data:
                data = data.get('data', {})
            results = data.get('results', [])
            if len(results) > 0:
                return True

        # Step 2: Check FDA Purple Book (CBER biologics/gene therapies)
        # Gene therapies like Casgevy/Lyfgenia are only in Purple Book, not drug labels
        drug_names_to_try = get_drug_synonyms(drug_name, mcp_funcs)
        for name in drug_names_to_try[:3]:
            try:
                purple_result = fda_lookup(method='search_purple_book', search_term=name, limit=5)
                if purple_result and purple_result.get('success'):
                    data = purple_result.get('data', {})
                    if 'data' in data:
                        data = data.get('data', {})
                    total = data.get('totalCount', 0)
                    results = data.get('results', [])
                    # Check for Licensed status
                    for result in results:
                        status = (result.get('licensureStatus', '') or '').lower()
                        if status == 'licensed':
                            return True
                    if total > 0:
                        return True
            except Exception:
                pass

        # Step 3: EMA fallback for drugs approved in both FDA and EMA
        if ema_search:
            for name in drug_names_to_try[:3]:
                try:
                    ema_result = ema_search(method='search_medicines', active_substance=name, limit=3)
                    results = ema_result.get('results', [])
                    for result in results:
                        status = (result.get('medicine_status', '') or '').lower()
                        if status in ('authorised', 'authorized'):
                            return True
                    if results:
                        break
                except Exception:
                    pass

        return False

    except Exception:
        return False


def get_brand_name_from_ema(generic_name: str, mcp_funcs: Dict[str, Any] = None) -> str:
    """
    Get brand name from EMA medicines database.

    Queries EMA API with drug name and synonyms, returns name_of_medicine field.
    Tries synonyms (e.g., hydroxycarbamide for hydroxyurea) for better matching.

    IMPORTANT: Verifies the active_substance field matches our search term to avoid
    false matches (e.g., "interferon beta-1a" matching "peginterferon beta-1a").

    Args:
        generic_name: Generic drug name (e.g., 'hydroxyurea', 'exagamglogene autotemcel')

    Returns:
        Brand name if found, None otherwise
    """
    if not generic_name or not mcp_funcs:
        return None

    try:
        ema_search = mcp_funcs.get('ema_search')
        if not ema_search:
            return None

        # Get synonyms for better EMA matching (e.g., hydroxycarbamide vs hydroxyurea)
        drug_names_to_try = get_drug_synonyms(generic_name, mcp_funcs)

        for drug_name in drug_names_to_try[:5]:
            ema_result = ema_search(method='search_medicines', active_substance=drug_name, limit=5)
            results = ema_result.get('results', [])

            for result in results:
                # Skip non-authorised medicines
                status = (result.get('medicine_status', '') or '').lower()
                if status not in ('authorised', 'authorized', ''):
                    continue

                # CRITICAL: Verify the active_substance actually matches our search term
                # EMA search is fuzzy, so "interferon beta-1a" can return "peginterferon beta-1a"
                active_substance = (result.get('active_substance', '') or '').lower()
                search_term_lower = drug_name.lower()

                # Check for exact match or close match (allowing for minor variations)
                if not (active_substance == search_term_lower or
                        search_term_lower in active_substance.split(';') or
                        active_substance.startswith(search_term_lower + ' ') or
                        active_substance.endswith(' ' + search_term_lower)):
                    # Not a match - skip this result
                    continue

                # Get brand name (name_of_medicine field)
                brand = result.get('name_of_medicine')
                if brand:
                    # Skip if brand is same as generic
                    if brand.lower() != generic_name.lower():
                        return brand

            if results:
                break  # Found results, no need to try more synonyms

    except Exception:
        pass

    return None


def get_brand_name_from_drugbank(drugbank_id: str, country: str = 'US', mcp_funcs: Dict[str, Any] = None) -> str:
    """
    Get brand name from DrugBank products API.

    Args:
        drugbank_id: DrugBank ID (e.g., 'DB00945')
        country: Country code to filter products (default: 'US')

    Returns:
        Brand name if found, None otherwise
    """
    if not drugbank_id or not mcp_funcs:
        return None

    try:
        drugbank_get_products = mcp_funcs.get('drugbank_get_products')
        if not drugbank_get_products:
            return None

        products = drugbank_get_products(drugbank_id=drugbank_id, country=country)
        if not products:
            return None

        results = products.get('results', [])
        if not results:
            return None

        # Return the first product name (typically the main brand)
        for product in results:
            name = product.get('name', '')
            if name:
                return name

    except Exception:
        pass

    return None


def get_all_fda_approved_for_indication(indication_synonyms: list, mcp_funcs: Dict[str, Any] = None) -> dict:
    """
    Search DrugBank for ALL drugs approved for a specific indication.

    Uses DrugBank's comprehensive drug database to find approved drugs,
    filtering to only those with 'approved' status.

    Args:
        indication_synonyms: List of indication terms to search (e.g., ['sickle cell', 'scd'])

    Returns:
        Dict mapping generic names to brand names (or None if unknown)
    """
    approved_drugs = {}  # {generic_name: brand_name}
    seen_drugs = set()

    if not mcp_funcs:
        return approved_drugs

    try:
        drugbank_search_indication = mcp_funcs.get('drugbank_search_indication')
        if not drugbank_search_indication:
            return approved_drugs

        # Try each synonym as a search term
        for synonym in indication_synonyms[:3]:  # Limit to first 3 to avoid too many API calls
            if len(synonym) < 4:  # Skip very short terms
                continue

            # Search DrugBank by indication
            drugbank_result = drugbank_search_indication(query=synonym, limit=30)

            if not drugbank_result:
                continue

            results = drugbank_result.get('results', [])

            for result in results:
                # Only include drugs with 'approved' status
                groups = result.get('groups', [])
                if 'approved' not in groups:
                    continue

                # Skip vaccines and non-therapeutic drugs
                drug_name = result.get('name', '')
                description = result.get('description', '') or ''
                description_lower = description.lower()

                # Skip if it's a vaccine or diagnostic
                if 'vaccine' in drug_name.lower() or 'vaccine' in description_lower[:100]:
                    continue

                # Verify the drug is actually for this indication
                # Check description mentions the indication
                indication_matches = False
                for syn in indication_synonyms:
                    pattern = r'\b' + re.escape(syn.lower()) + r'\b'
                    if re.search(pattern, description_lower):
                        indication_matches = True
                        break

                if indication_matches and drug_name:
                    drug_key = drug_name.lower()
                    if drug_key not in seen_drugs:
                        # CRITICAL: DrugBank's 'approved' means approved ANYWHERE in the world.
                        # We MUST verify against actual FDA database before labeling as FDA approved.
                        if not verify_fda_approval(drug_name, mcp_funcs):
                            continue  # Skip drugs not actually in FDA database

                        seen_drugs.add(drug_key)
                        # Get brand name - try multiple sources:
                        # 1. DrugBank products API
                        # 2. Description text parsing
                        # 3. FDA label API
                        drugbank_id = result.get('drugbank_id', '')
                        brand_name = None
                        if drugbank_id:
                            brand_name = get_brand_name_from_drugbank(drugbank_id, mcp_funcs=mcp_funcs)
                        if not brand_name:
                            brand_name = extract_brand_name_from_description(description)
                        if not brand_name:
                            brand_name = get_brand_name_from_fda(drug_name, mcp_funcs)
                        approved_drugs[drug_name] = brand_name

    except Exception as e:
        pass

    return approved_drugs


def get_all_ema_approved_for_indication(indication_synonyms: list, mcp_funcs: Dict[str, Any] = None) -> dict:
    """
    Search EMA for ALL drugs approved for a specific indication.

    This queries EMA medicines directly by therapeutic area to find approved drugs,
    not just drugs that are in clinical trials.

    Args:
        indication_synonyms: List of indication terms to search (e.g., ['sickle cell', 'scd'])

    Returns:
        Dict mapping generic names to brand names
    """
    approved_drugs = {}  # {generic_name: brand_name}
    seen_drugs = set()

    if not mcp_funcs:
        return approved_drugs

    try:
        ema_search = mcp_funcs.get('ema_search')
        if not ema_search:
            return approved_drugs

        # Try each synonym as a therapeutic area search
        for synonym in indication_synonyms[:3]:
            if len(synonym) < 4:
                continue

            # Search EMA by therapeutic area
            ema_result = ema_search(method='search_medicines', therapeutic_area=synonym, limit=30)

            if not ema_result:
                continue

            results = ema_result.get('results', [])

            for result in results:
                # Skip suspended/withdrawn/revoked medicines
                status = (result.get('medicine_status', '') or '').lower()
                if status in ('suspended', 'withdrawn', 'refused', 'revoked'):
                    continue

                # Get the active substance (generic name) and medicine name (brand)
                active_substance = result.get('active_substance', '') or result.get('international_non_proprietary_name_common_name', '')
                brand_name = result.get('medicine_name', '')

                # Verify indication matches
                indication_text = (result.get('therapeutic_indication', '') or '').lower()
                therapeutic_area = (result.get('therapeutic_area_mesh', '') or '').lower()
                combined_text = indication_text + ' ' + therapeutic_area

                indication_matches = False
                for syn in indication_synonyms:
                    pattern = r'\b' + re.escape(syn.lower()) + r'\b'
                    if re.search(pattern, combined_text):
                        indication_matches = True
                        break

                if indication_matches and active_substance:
                    drug_key = active_substance.lower()
                    if drug_key not in seen_drugs:
                        seen_drugs.add(drug_key)
                        approved_drugs[active_substance] = brand_name

    except Exception as e:
        pass

    return approved_drugs


def get_drug_base_name(drug_name: str) -> str:
    """
    Get the base name of a drug by stripping salt suffixes, formulation info, and brand names.

    This is a fast, local-only operation (no API calls) for deduplication purposes.

    Examples:
        "Fingolimod Hydrochloride" -> "fingolimod"
        "Ozanimod Hydrochloride (Zeposia)" -> "ozanimod"
        "Cladribine (Mavenclad)" -> "cladribine"
        "Cladribine Subcutaneous Injection" -> "cladribine"
        "interferon beta-1a" -> "interferon beta-1a"  (keep variant info)
        "peginterferon beta-1a" -> "peginterferon beta-1a" (different drug)

    Args:
        drug_name: Drug name possibly with salt suffix, formulation, and/or brand name

    Returns:
        Lowercase base name for comparison
    """
    name = drug_name.lower().strip()

    # Remove brand names in parentheses at end
    name = re.sub(r'\s*\([^)]*\)\s*$', '', name).strip()

    # Strip formulation/route suffixes (must be at end)
    formulation_suffixes = [
        'subcutaneous injection', 'subcutaneous', 'intramuscular injection',
        'intramuscular', 'intravenous injection', 'intravenous', 'injection',
        'injectable product', 'injectable', 'oral solution', 'oral tablet',
        'oral capsule', 'oral', 'topical', 'ophthalmic', 'nasal', 'transdermal'
    ]
    for suffix in formulation_suffixes:
        if name.endswith(' ' + suffix):
            name = name[:-len(suffix)-1].strip()
            break

    # Strip common salt suffixes (only at end of string)
    salt_suffixes = [
        'hydrochloride', 'sodium', 'calcium', 'potassium', 'sulfate',
        'acetate', 'maleate', 'tartrate', 'citrate', 'phosphate',
        'carbonate', 'mesylate', 'besylate', 'dihydrochloride', 'fumarate'
    ]
    for suffix in salt_suffixes:
        if name.endswith(' ' + suffix):
            name = name[:-len(suffix)-1].strip()
            break

    # Strip INN suffixes (Greek letters used for biologics)
    # e.g., "efgartigimod alfa" -> "efgartigimod"
    # These indicate the same drug product with different naming conventions
    inn_suffixes = [
        ' alfa', ' beta', ' gamma', ' delta', ' epsilon', ' zeta', ' eta', ' theta',
        ' pegol', ' vedotin', ' emtansine', ' mertansine', ' ozogamicin',
        ' sudotox', ' tansine',
    ]
    for suffix in inn_suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)].strip()
            break

    return name


def get_generic_name(drug_name: str, mcp_funcs: Dict[str, Any] = None) -> str:
    """
    Look up the generic/INN name for a drug using PubChem.

    Uses PubChem's compound search to get CID, then fetches synonyms.
    The first synonym is typically the preferred/generic name.

    Args:
        drug_name: Drug name (could be brand, salt form, or generic)

    Returns:
        Generic name if found, otherwise cleaned original name
    """
    # Check cache first
    cache_key = drug_name.lower().strip()
    if cache_key in _pubchem_cache:
        return _pubchem_cache[cache_key]

    # Clean the name before lookup
    cleaned = re.sub(r'\s*\([^)]*\)\s*$', '', drug_name).strip()
    cleaned = re.sub(r'\s+\d+(\.\d+)?\s*(mg|mg/ml|ml|mcg|g|iu|units?|bid|tid|qd)\b.*$', '', cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r'\s+(Oral\s+)?(Solution|Tablet|Capsule|Injection|Suspension)s?\s*$', '', cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r'\s+(Extended|Immediate|Delayed)\s+Release\s*$', '', cleaned, flags=re.IGNORECASE).strip()

    if not cleaned or len(cleaned) < 3:
        _pubchem_cache[cache_key] = cleaned
        return cleaned

    if not mcp_funcs:
        _pubchem_cache[cache_key] = cleaned
        return cleaned

    pubchem_search = mcp_funcs.get('pubchem_search')
    pubchem_synonyms = mcp_funcs.get('pubchem_synonyms')

    if not pubchem_search or not pubchem_synonyms:
        _pubchem_cache[cache_key] = cleaned
        return cleaned

    def _search_pubchem_and_get_generic(query: str, original_cleaned: str) -> Optional[str]:
        """Helper to search PubChem and validate result is reasonable."""
        try:
            result = pubchem_search(query=query, max_records=1)

            if result and isinstance(result, dict):
                details = result.get('details', {})
                properties = details.get('PropertyTable', {}).get('Properties', [])

                if properties and len(properties) > 0:
                    cid = properties[0].get('CID')

                    if cid:
                        synonyms_result = pubchem_synonyms(cid=cid)

                        if synonyms_result and isinstance(synonyms_result, dict):
                            info_list = synonyms_result.get('InformationList', {})
                            info = info_list.get('Information', [])

                            if info and len(info) > 0:
                                synonyms = info[0].get('Synonym', [])

                                if synonyms and len(synonyms) > 0:
                                    generic = synonyms[0]
                                    generic = generic.title()

                                    # Skip CAS numbers
                                    if re.match(r'^\d+-\d+-\d+$', generic):
                                        for syn in synonyms[1:5]:
                                            if not re.match(r'^\d+-\d+-\d+$', syn):
                                                generic = syn.title()
                                                break

                                    # VALIDATION: Reject if result is too different from input
                                    # This prevents "dimethyl fumarate" → "dimethyl" → "ethane"
                                    generic_lower = generic.lower()
                                    query_lower = query.lower()
                                    original_lower = original_cleaned.lower()

                                    # Check if result shares significant overlap with input
                                    # Allow: "dimethyl fumarate" → "Dimethyl Fumarate" (exact or close)
                                    # Block: "dimethyl fumarate" → "Ethane" (completely different)
                                    if (generic_lower in original_lower or
                                        original_lower in generic_lower or
                                        generic_lower in query_lower or
                                        query_lower in generic_lower or
                                        # Check first word match (e.g., "fingolimod hydrochloride" → "Fingolimod")
                                        generic_lower.split()[0] == query_lower.split()[0] or
                                        # Check if any significant word (>4 chars) matches
                                        any(w in generic_lower for w in original_lower.split() if len(w) > 4)):
                                        return generic

                                    # Result too different - likely wrong compound
                                    return None
        except Exception:
            pass
        return None

    # Strategy: Try full cleaned name first, then strip salt suffix as fallback
    # This prevents "dimethyl fumarate" → "dimethyl" → "ethane" bug

    # Step 1: Try full cleaned name
    result = _search_pubchem_and_get_generic(cleaned, cleaned)
    if result:
        _pubchem_cache[cache_key] = result
        return result

    # Step 2: Only if full name fails, try stripping salt suffixes
    # (but NOT for names like "dimethyl fumarate" where fumarate is part of the drug name)
    lookup_stripped = re.sub(r'\s+(Hydrochloride|Sodium|Calcium|Potassium|Sulfate|Acetate|Maleate|Fumarate|Tartrate|Citrate|Phosphate|Carbonate)\s*$', '', cleaned, flags=re.IGNORECASE).strip()

    if lookup_stripped != cleaned and len(lookup_stripped) >= 3:
        result = _search_pubchem_and_get_generic(lookup_stripped, cleaned)
        if result:
            _pubchem_cache[cache_key] = result
            return result

    _pubchem_cache[cache_key] = cleaned
    return cleaned
