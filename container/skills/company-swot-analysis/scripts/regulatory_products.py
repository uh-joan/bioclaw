#!/usr/bin/env python3
"""
Regulatory products data collection for company SWOT analysis.

This module provides functions for:
- Getting FDA approved products
- Getting Orange Book patent data
- Getting EMA (European) approved products
"""

import re
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional

# All MCP functions are now accessed via mcp_funcs parameter
# No direct imports from mcp.servers.* allowed


# ============================================================================
# FDA Approved Products
# ============================================================================

def get_approved_products(company_name: str, drug_names: List[str] = None, mcp_funcs: Dict[str, Any] = None) -> Dict[str, Any]:
    """Collect FDA approved products by searching drug names from clinical pipeline.

    IMPORTANT: We now prioritize searching by drug names (from pipeline) rather than
    manufacturer name, because manufacturer search has high false positive rates
    (e.g., "Sciences" matches Gilead Sciences, not Exact Sciences).

    Args:
        company_name: Company name (for logging and validation)
        drug_names: List of drug names from clinical pipeline to search for
    """
    print(f"\n💊 Collecting FDA products for {company_name}...")

    if not mcp_funcs:
        return {'total_products': 0, 'product_names': [], 'therapeutic_areas': {}, 'success': False, 'error': 'No MCP functions provided'}

    lookup_drug = mcp_funcs.get('fda_lookup')
    if not lookup_drug:
        return {'total_products': 0, 'product_names': [], 'therapeutic_areas': {}, 'success': False, 'error': 'FDA lookup function not available'}

    if not drug_names:
        drug_names = []

    all_products = {}  # drug_name -> product info
    therapeutic_areas = Counter()
    validated_products = {}  # Products validated to belong to this company

    # Normalize company name for matching
    company_lower = company_name.lower()
    # Extract key identifying words (skip common suffixes)
    company_words = [w.lower() for w in company_name.split()
                     if len(w) >= 3 and w.lower() not in ('inc', 'inc.', 'corp', 'ltd', 'llc', 'co', 'company', 'pharmaceuticals', 'pharma', 'the')]

    def matches_company(manufacturer_name: str) -> bool:
        """Check if a manufacturer name likely belongs to our target company."""
        if not manufacturer_name:
            return False
        mfr_lower = manufacturer_name.lower()
        # Check if ALL significant company words appear in manufacturer name
        # This prevents "Sciences" matching "Gilead Sciences" when searching for "Exact Sciences"
        return all(word in mfr_lower for word in company_words)

    try:
        # STEP 1: Search by drug names from clinical pipeline (most reliable)
        # These are drugs we KNOW the company is developing
        print(f"   Searching by {len(drug_names)} drug names from pipeline...")

        # Skip words that are not real drug names
        skip_words = {'patients', 'placebo', 'standard', 'care', 'treatment', 'therapy',
                      'combination', 'control', 'arm', 'group', 'study', 'trial'}

        # Skip generic/common terms that would match products from many companies
        skip_generics = {'human growth hormone', 'growth hormone', 'hgh', 'insulin',
                         'saline', 'glucose', 'dextrose', 'sodium chloride', 'vitamin',
                         'aspirin', 'ibuprofen', 'acetaminophen'}

        for drug_name in drug_names[:20]:  # Check top 20 drugs
            if not drug_name or len(drug_name) < 3:
                continue

            if drug_name.lower() in skip_words:
                continue

            # Skip generic terms that would match many manufacturers
            if drug_name.lower() in skip_generics:
                continue

            try:
                # Search by drug name in labels
                result = lookup_drug(
                    search_term=drug_name,
                    search_type='label',
                    count='openfda.brand_name.exact',
                    limit=10
                )

                data = result.get('data', {})
                results = data.get('results', [])

                if results:
                    # Found FDA data for this drug
                    # DYNAMIC VALIDATION: drug_names come from the company's own
                    # CT.gov pipeline (lead sponsor) or XBRL segments (SEC filing).
                    # Both already prove ownership. When only 1 brand matches a
                    # specific pipeline drug, accept it — the pipeline is the validation.
                    # When multiple brands match, prefer manufacturer-validated ones.
                    is_single_match = len([r for r in results[:3] if r.get('term')]) == 1

                    for item in results[:3]:  # Top 3 matches per drug
                        brand = item.get('term', '')
                        # Case-insensitive deduplication
                        brand_upper = brand.upper() if brand else ''
                        existing_upper = {k.upper() for k in all_products.keys()}
                        if brand and brand_upper not in existing_upper:
                            # Get label details for generic names and manufacturer info
                            try:
                                detail = lookup_drug(
                                    search_term=brand,
                                    search_type='label',
                                    limit=10
                                )
                                detail_data = detail.get('data', {})
                                detail_results = detail_data.get('results', [])

                                # Check ALL labels for this brand
                                is_mfr_validated = False
                                validated_generic_names = []
                                validated_manufacturer = None

                                for label in detail_results:
                                    openfda = label.get('openfda', {})
                                    manufacturers = openfda.get('manufacturer_name', [])

                                    # Extract generic names from any label
                                    generic_names = openfda.get('generic_name', [])
                                    for gn in generic_names:
                                        if gn and gn not in validated_generic_names:
                                            validated_generic_names.append(gn)

                                    # Check if any manufacturer matches our company
                                    if not is_mfr_validated:
                                        for mfr in manufacturers:
                                            if matches_company(mfr):
                                                is_mfr_validated = True
                                                validated_manufacturer = mfr
                                                break

                                # Accept if: (a) manufacturer matches, OR
                                # (b) single match for a pipeline drug name (pipeline = proof of ownership)
                                #     AND search term is specific enough (>4 chars, not a common word)
                                is_pipeline_validated = (
                                    is_single_match and
                                    len(drug_name) > 4 and
                                    drug_name.lower() not in skip_words and
                                    drug_name.lower() not in skip_generics
                                )

                                if is_mfr_validated or is_pipeline_validated:
                                    if is_pipeline_validated and not is_mfr_validated:
                                        # Get actual manufacturer from first label for display
                                        if detail_results:
                                            first_mfrs = detail_results[0].get('openfda', {}).get('manufacturer_name', [])
                                            validated_manufacturer = first_mfrs[0] if first_mfrs else 'Unknown (co-developed)'

                                        # GUARD: Reject if manufacturer is known and clearly belongs
                                        # to a DIFFERENT company. This catches comparator drugs
                                        # (e.g., Venclexta/AbbVie appearing in BeiGene trials).
                                        if validated_manufacturer and validated_manufacturer != 'Unknown (co-developed)':
                                            mfr_lower = validated_manufacturer.lower()
                                            # Check if manufacturer shares ANY significant word with our company
                                            company_sig_words = [w for w in company_words if len(w) >= 4]
                                            if company_sig_words and not any(w in mfr_lower for w in company_sig_words):
                                                print(f"   Rejected comparator: {brand} (mfr: {validated_manufacturer} ≠ {company_name})")
                                                continue

                                        print(f"   Pipeline-validated: {brand} (mfr: {validated_manufacturer})")

                                    all_products[brand] = {
                                        'brand_name': brand,
                                        'generic_names': validated_generic_names,
                                        'search_term': drug_name,
                                        'count': item.get('count', 0),
                                        'manufacturer': validated_manufacturer
                                    }
                                else:
                                    continue
                            except Exception:
                                continue

                    # Get therapeutic class for this drug
                    try:
                        class_result = lookup_drug(
                            search_term=drug_name,
                            search_type='label',
                            count='openfda.pharm_class_epc.exact',
                            limit=5
                        )
                        class_data = class_result.get('data', {})
                        class_results = class_data.get('results', [])
                        for item in class_results[:3]:
                            area = item.get('term', '').replace(' [EPC]', '')
                            if area:
                                therapeutic_areas[area] += item.get('count', 1)
                    except Exception:
                        pass

            except Exception as e:
                # Drug not found in FDA - that's okay, might be investigational
                continue

        # STEP 1.5: Resolve internal research codes via full-text FDA label search
        # Internal codes like BNT162b2, MEDI4736, RG7204 may appear in label text
        # (e.g. clinical studies section) but won't match brand_name count queries.
        # Search full labels and extract brand names from matching results.
        INTERNAL_CODE_RE = re.compile(r'^[A-Z]{2,5}[-]?\d{3,}', re.IGNORECASE)
        found_brands_upper = {b.upper() for b in all_products.keys()}

        unresolved_codes = [
            name for name in drug_names[:20]
            if name and INTERNAL_CODE_RE.match(name)
            and name.upper() not in found_brands_upper
            and name.lower() not in skip_words
        ]

        if unresolved_codes:
            print(f"   Resolving {len(unresolved_codes)} internal codes via FDA label search...")
            for code in unresolved_codes[:5]:
                try:
                    result = lookup_drug(
                        search_term=code,
                        search_type='label',
                        limit=3
                    )
                    data = result.get('data', {})
                    label_results = data.get('results', [])
                    resolved = False
                    for label in label_results:
                        openfda = label.get('openfda', {})
                        brand_names = openfda.get('brand_name', [])
                        generic_names_found = openfda.get('generic_name', [])
                        manufacturers = openfda.get('manufacturer_name', [])

                        for brand in brand_names[:1]:  # Take first brand
                            if brand.upper() not in found_brands_upper:
                                all_products[brand] = {
                                    'brand_name': brand,
                                    'generic_names': generic_names_found,
                                    'search_term': code,
                                    'count': 0,
                                    'manufacturer': manufacturers[0] if manufacturers else 'Unknown'
                                }
                                found_brands_upper.add(brand.upper())
                                print(f"   Resolved {code} → {brand}")
                                resolved = True
                                break
                        if resolved:
                            break
                except Exception:
                    continue

        # STEP 2: Search by manufacturer name ONLY if we have few results from drug search
        # Use validated matching to avoid false positives
        if len(all_products) < 3 and company_words:
            print(f"   Few products found, trying manufacturer search with validation...")

            # Build search with the most distinctive company word
            # Prefer longer words as they're more specific
            search_word = max(company_words, key=len) if company_words else None

            if search_word and len(search_word) >= 4:
                try:
                    mfr_search = f"openfda.manufacturer_name:{search_word}"
                    print(f"   Searching FDA with: {mfr_search}")

                    result = lookup_drug(
                        search_term=mfr_search,
                        search_type='label',
                        count='openfda.brand_name.exact',
                        limit=50
                    )

                    data = result.get('data', {})
                    results = data.get('results', [])

                    if results:
                        # For each brand, verify it actually belongs to our company
                        # by checking the full label details
                        print(f"   Found {len(results)} candidates, validating...")
                        validated_count = 0

                        for item in results[:30]:  # Check up to 30 candidates
                            brand = item.get('term', '')
                            if brand and brand not in all_products:
                                # Quick validation: search for the brand and check manufacturer
                                try:
                                    detail = lookup_drug(
                                        search_term=brand,  # Search by brand name directly
                                        search_type='label',
                                        limit=1
                                    )
                                    detail_data = detail.get('data', {})
                                    detail_results = detail_data.get('results', [])

                                    if detail_results:
                                        label = detail_results[0]
                                        openfda = label.get('openfda', {})
                                        manufacturers = openfda.get('manufacturer_name', [])

                                        # Check if any manufacturer matches our company
                                        for mfr in manufacturers:
                                            if matches_company(mfr):
                                                # Also extract generic name for matching with pipeline
                                                generic_names = openfda.get('generic_name', [])
                                                validated_products[brand] = {
                                                    'brand_name': brand,
                                                    'generic_names': generic_names,
                                                    'search_term': f'manufacturer:{search_word}',
                                                    'count': item.get('count', 0),
                                                    'manufacturer': mfr
                                                }
                                                validated_count += 1
                                                break
                                except Exception:
                                    continue

                        print(f"   Validated {validated_count} products for {company_name}")

                except Exception as e:
                    print(f"   Manufacturer search failed: {e}")

        # Combine drug-search results with validated manufacturer results
        all_products.update(validated_products)
        product_names = list(all_products.keys())

        # Also collect all generic names (for matching with clinical pipeline)
        generic_names = []
        for prod in all_products.values():
            for gn in prod.get('generic_names', []):
                if gn and gn not in generic_names:
                    generic_names.append(gn)

        # STEP 3: Extract therapeutic areas for ALL products (including those found via manufacturer search)
        # This ensures we populate therapeutic_areas even when products were found in Step 2
        if product_names and len(therapeutic_areas) == 0:
            print(f"   Extracting therapeutic areas for {len(product_names)} products...")
            for product_name in product_names[:20]:  # Check up to 20 products
                try:
                    class_result = lookup_drug(
                        search_term=product_name,
                        search_type='label',
                        count='openfda.pharm_class_epc.exact',
                        limit=5
                    )
                    class_data = class_result.get('data', {})
                    class_results = class_data.get('results', [])
                    for item in class_results[:3]:
                        area = item.get('term', '').replace(' [EPC]', '')
                        if area:
                            therapeutic_areas[area] += item.get('count', 1)
                except Exception as e:
                    print(f"   Failed to get therapeutic area for {product_name}: {e}")
                    continue

            print(f"   Found {len(therapeutic_areas)} therapeutic areas from FDA pharm_class")

        # STEP 4: Deduplicate by generic name to count unique drug franchises
        # Example: CABOMETYX and COMETRIQ both = CABOZANTINIB = 1 franchise, not 2 products
        drug_franchises = {}  # generic_name -> list of brand names
        for prod in all_products.values():
            generic_list = prod.get('generic_names', [])
            brand = prod.get('brand_name', '')

            if generic_list:
                # Use first generic name as the key
                generic = generic_list[0].upper()
                if generic not in drug_franchises:
                    drug_franchises[generic] = []
                if brand:
                    drug_franchises[generic].append(brand)
            elif brand:
                # No generic name - use brand as its own franchise
                drug_franchises[brand.upper()] = [brand]

        unique_drug_count = len(drug_franchises)

        # Build display strings
        franchise_display = []
        for generic, brands in list(drug_franchises.items())[:10]:
            if len(brands) > 1:
                franchise_display.append(f"{generic} ({', '.join(brands)})")
            else:
                franchise_display.append(brands[0])

        print(f"   Deduplicated: {len(product_names)} brands → {unique_drug_count} unique drug franchises")

        return {
            'total_products': unique_drug_count,  # Changed: count unique drugs, not brands
            'total_brands': len(product_names),   # New: original brand count
            'product_names': product_names[:50],  # Keep for backward compatibility
            'franchise_names': franchise_display,  # New: deduplicated display
            'drug_franchises': drug_franchises,   # New: generic -> brands mapping
            'generic_names': generic_names,       # For matching with clinical pipeline
            'products': list(all_products.values())[:50],
            'therapeutic_areas': dict(therapeutic_areas.most_common(10)),
            'success': True
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'total_products': 0, 'product_names': [], 'therapeutic_areas': {}, 'success': False, 'error': str(e)}


# ============================================================================
# Orange Book Patent Data
# ============================================================================

def get_patent_data(product_names: List[str], mcp_funcs: Dict[str, Any] = None) -> Dict[str, Any]:
    """Collect Orange Book patent and exclusivity data for FDA-approved products.

    IMPORTANT: Orange Book only contains NDA applications (small molecules).
    Biologics (BLA applications like gene therapies, monoclonal antibodies) won't have data.

    Args:
        product_names: List of FDA-approved product names to look up

    Returns:
        dict: Patent data summary
        {
            'products_with_patents': {
                'JARDIANCE': {
                    'nda_number': '204629',
                    'earliest_expiry': '2027-04-15',
                    'latest_expiry': '2034-12-11',
                    'patent_count': 15,
                    'has_pediatric_extension': True
                },
                ...
            },
            'earliest_loe': '2027-04-15',  # Earliest patent expiry across all products
            'products_expiring_soon': ['JARDIANCE'],  # Within 3 years
            'success': True
        }
    """
    print(f"\n📜 Collecting Orange Book patent data for {len(product_names)} products...")

    if not mcp_funcs:
        return {'products_with_patents': {}, 'earliest_loe': None, 'products_expiring_soon': [], 'success': False, 'error': 'No MCP functions provided'}

    lookup_drug = mcp_funcs.get('fda_lookup')
    get_patent_exclusivity = mcp_funcs.get('fda_get_patent_exclusivity')
    if not lookup_drug or not get_patent_exclusivity:
        return {'products_with_patents': {}, 'earliest_loe': None, 'products_expiring_soon': [], 'success': False, 'error': 'FDA functions not available'}

    products_with_patents = {}
    all_expiry_dates = []

    for product_name in product_names[:15]:  # Limit to avoid too many API calls
        if not product_name or len(product_name) < 2:
            continue

        try:
            # Step 1: Look up the product to get NDA number
            result = lookup_drug(
                search_term=product_name,
                search_type='label',
                count='openfda.application_number.exact',
                limit=5
            )

            data = result.get('data', {})
            results = data.get('results', [])

            nda_number = None
            for item in results:
                term = item.get('term', '')
                # NDA applications start with 'NDA', skip BLA (biologics)
                if term.startswith('NDA'):
                    nda_number = term.replace('NDA', '').strip()
                    break

            if not nda_number:
                # Product is likely a biologic (BLA) or not in FDA database
                continue

            # Step 2: Get patent data from Orange Book
            patent_result = get_patent_exclusivity(
                nda_number=nda_number,
                search_term=product_name,
                limit=100
            )

            if not patent_result.get('success'):
                continue

            patent_data = patent_result.get('data', {})
            patents = patent_data.get('patents', [])
            exclusivity = patent_data.get('exclusivity', [])

            if not patents:
                continue

            # Parse patent expiry dates
            expiry_dates = []
            has_ped = False

            for patent in patents:
                expire_str = patent.get('patentExpireDate', '')
                patent_no = patent.get('patentNo', '')

                # Check for pediatric extension (adds 6 months)
                if '*PED' in patent_no:
                    has_ped = True

                if expire_str:
                    try:
                        # Parse date like "Apr 15, 2027"
                        expire_date = datetime.strptime(expire_str, "%b %d, %Y")
                        expiry_dates.append(expire_date)
                    except ValueError:
                        pass

            if expiry_dates:
                earliest = min(expiry_dates)
                latest = max(expiry_dates)

                products_with_patents[product_name] = {
                    'nda_number': nda_number,
                    'earliest_expiry': earliest.strftime('%Y-%m-%d'),
                    'latest_expiry': latest.strftime('%Y-%m-%d'),
                    'patent_count': len(set(p.get('patentNo', '').replace('*PED', '') for p in patents)),
                    'has_pediatric_extension': has_ped
                }

                all_expiry_dates.extend(expiry_dates)
                print(f"   ✓ {product_name}: {len(expiry_dates)} patents, expires {earliest.strftime('%b %Y')} - {latest.strftime('%b %Y')}")

        except Exception as e:
            # Skip products that fail - likely biologics or API issues
            continue

    # Find products expiring soon (within 3 years)
    now = datetime.now()
    three_years = datetime(now.year + 3, now.month, now.day)
    products_expiring_soon = []

    for product, info in products_with_patents.items():
        try:
            earliest = datetime.strptime(info['earliest_expiry'], '%Y-%m-%d')
            if earliest <= three_years:
                products_expiring_soon.append(product)
        except ValueError:
            pass

    # Find overall earliest LOE
    earliest_loe = None
    if all_expiry_dates:
        earliest_loe = min(all_expiry_dates).strftime('%Y-%m-%d')

    return {
        'products_with_patents': products_with_patents,
        'earliest_loe': earliest_loe,
        'products_expiring_soon': products_expiring_soon,
        'total_products_checked': len(product_names[:15]),
        'products_with_data': len(products_with_patents),
        'success': True
    }


# ============================================================================
# EMA (European Medicines Agency) Products
# ============================================================================

def get_ema_products(company_name: str, drug_names: List[str] = None, fda_product_names: List[str] = None, subsidiary_names: List[str] = None, mcp_funcs: Dict[str, Any] = None) -> Dict[str, Any]:
    """Collect EMA (European Medicines Agency) approved products by searching for drug names.

    EMA API quirks:
    - get_medicine_by_name: Uses TRADE names (e.g., "Cabometyx", "Ozempic")
    - search_medicines(active_substance=): Uses INN/generic names (e.g., "cabozantinib", "semaglutide")
    - Results are in 'data' key, not 'medicines'
    - Status must match 'Authorised' (British spelling)

    Args:
        company_name: Company name (used for logging and MAH validation)
        drug_names: List of drug names from clinical pipeline to search for
        fda_product_names: List of FDA-approved product names to also search in EMA
    """
    print(f"\n🇪🇺 Collecting EMA products for {company_name}...")

    if not mcp_funcs:
        return {'total_products': 0, 'products': [], 'product_names': [], 'therapeutic_areas': {}, 'success': False, 'error': 'No MCP functions provided'}

    ema_info = mcp_funcs.get('ema_search')
    if not ema_info:
        return {'total_products': 0, 'products': [], 'product_names': [], 'therapeutic_areas': {}, 'success': False, 'error': 'EMA search function not available'}

    if not drug_names:
        drug_names = []
    if not fda_product_names:
        fda_product_names = []
    if not subsidiary_names:
        subsidiary_names = []

    all_products = {}  # product name -> product info
    therapeutic_areas = Counter()

    # Skip words for false positives
    skip_words = {'patients', 'placebo', 'standard', 'care', 'treatment', 'therapy',
                  'combination', 'control', 'arm', 'group', 'study', 'trial'}

    # Skip generic terms that match products from many companies
    skip_generics = {'human growth hormone', 'growth hormone', 'hgh', 'insulin',
                     'saline', 'glucose', 'dextrose', 'sodium chloride', 'vitamin'}

    # Well-known pharma subsidiary → parent mappings for EMA MAH matching
    # EMA MAH names use legal entities (e.g., "Janssen-Cilag") not parent brands ("J&J")
    SUBSIDIARY_MAP = {
        'johnson & johnson': ['janssen', 'cilag', 'actelion'],
        'johnson and johnson': ['janssen', 'cilag', 'actelion'],
        'j&j': ['janssen', 'cilag', 'actelion'],
        'roche': ['genentech', 'chugai'],
        'abbvie': ['allergan', 'pharmacyclics'],
        'pfizer': ['wyeth', 'hospira', 'seagen'],
        'novartis': ['sandoz', 'alcon'],
        'merck': ['organon', 'msd'],  # MSD in EU
        'merck & co': ['organon', 'msd'],
        'sanofi': ['genzyme', 'aventis', 'regeneron'],
        'bristol-myers squibb': ['celgene', 'myriad'],
        'bristol myers squibb': ['celgene', 'myriad'],
        'astrazeneca': ['alexion', 'medimmune'],
        'eli lilly': ['loxo', 'prevail'],
        'lilly': ['loxo', 'prevail'],
        'amgen': ['horizon'],
        'takeda': ['shire', 'millennium'],
        'bayer': ['asklepios'],
        'gilead': ['kite', 'immunomedics'],
        'biogen': ['sage'],
    }

    # Normalize company name for MAH validation
    company_lower = company_name.lower()
    company_words = [w.lower() for w in company_name.split()
                     if len(w) >= 3 and w.lower() not in ('inc', 'inc.', 'corp', 'ltd', 'llc', 'co', 'company', 'pharmaceuticals', 'pharma', 'the', 'gmbh')]

    # Build extended match words: company words + known subsidiaries + passed subsidiary names
    match_words = list(company_words)
    for parent_key, subs in SUBSIDIARY_MAP.items():
        if any(w in parent_key for w in company_words):
            match_words.extend(subs)
    # Add CT.gov-discovered subsidiary names
    for sub in subsidiary_names:
        sub_words = [w.lower() for w in sub.split() if len(w) >= 3
                     and w.lower() not in ('inc', 'corp', 'ltd', 'llc', 'gmbh', 'pharmaceuticals', 'pharma')]
        match_words.extend(sub_words)
    match_words = list(set(match_words))  # deduplicate

    def matches_company(mah_name: str) -> bool:
        """Check if Marketing Authorization Holder matches our target company."""
        if not mah_name:
            return True  # If no MAH data, accept the result
        mah_lower = mah_name.lower()
        # Check if ANY significant word (company + subsidiaries) appears in MAH name
        # EMA MAH names often include country suffixes like "Ultragenyx Germany GmbH"
        return any(word in mah_lower for word in match_words)

    def extract_medicine_data(med: Dict, search_term: str, validate_mah: bool = False) -> Optional[Dict]:
        """Extract product info from EMA medicine record.

        Args:
            med: EMA medicine record
            search_term: The term used to find this medicine
            validate_mah: If True, validate Marketing Authorization Holder matches company
        """
        # EMA API returns different field names than expected:
        # - name_of_medicine (not medicine_name)
        # - medicine_status (not authorisation_status)
        # - international_non_proprietary_name_common_name (INN)
        # - therapeutic_area_mesh (not therapeutic_area)

        name = (med.get('name_of_medicine') or med.get('medicine_name') or
                med.get('name') or med.get('product_name') or '')
        if not name:
            return None

        # Status field - EMA uses 'medicine_status'
        status = (med.get('medicine_status') or med.get('authorisation_status') or
                  med.get('status') or '')

        # Only include authorized products
        status_lower = status.lower() if status else ''
        if status and status_lower not in ('authorised', 'authorized', 'approved', 'active', 'valid'):
            return None

        # MAH (Marketing Authorization Holder) validation
        mah = med.get('marketing_authorisation_developer_applicant_holder') or ''
        if validate_mah and not matches_company(mah):
            return None  # Product belongs to different company

        # Get therapeutic area - EMA uses therapeutic_area_mesh
        therapeutic_area = med.get('therapeutic_area_mesh') or med.get('therapeutic_area') or ''
        if isinstance(therapeutic_area, list):
            therapeutic_area = ', '.join(therapeutic_area[:3])

        return {
            'name': name,
            'active_substance': med.get('active_substance') or med.get('international_non_proprietary_name_common_name') or '',
            'status': status or 'Authorised',
            'therapeutic_area': therapeutic_area,
            'approval_date': med.get('marketing_authorisation_date') or '',
            'search_term': search_term,
            'mah': mah
        }

    try:
        # Combine drug names from pipeline with FDA product names for comprehensive search
        # FDA products are often also approved in EMA under same or similar names
        all_search_terms = set()
        for name in drug_names[:15]:
            if name and len(name) >= 3:
                all_search_terms.add(name)
        for name in fda_product_names[:10]:
            if name and len(name) >= 3:
                all_search_terms.add(name)

        # Search EMA for each drug name
        for drug_name in all_search_terms:
            if drug_name.lower() in skip_words:
                continue

            # Skip generic terms that match products from many companies
            if drug_name.lower() in skip_generics:
                continue

            # Strategy 1: Try get_medicine_by_name (for brand/trade names like "Cabometyx")
            # This returns a single exact match - validate MAH
            try:
                result = ema_info(
                    method='get_medicine_by_name',
                    name=drug_name
                )

                if isinstance(result, dict) and result.get('found'):
                    # EMA returns medicine data in 'medicine' key
                    med_data = result.get('medicine', {})
                    if isinstance(med_data, dict) and med_data:
                        # Validate MAH for exact name matches
                        product = extract_medicine_data(med_data, drug_name, validate_mah=True)
                        if product and product['name'] not in all_products:
                            all_products[product['name']] = product
                            if product['therapeutic_area']:
                                therapeutic_areas[product['therapeutic_area']] += 1
                            print(f"   Found via trade name: {product['name']}")

            except Exception as e:
                pass  # Not found by trade name, try active substance

            # Strategy 2: Try search_medicines with active_substance (for INN/generic names)
            # This can return multiple products - MUST validate MAH to avoid false positives
            try:
                result = ema_info(
                    method='search_medicines',
                    active_substance=drug_name,
                    status='Authorised',
                    limit=10
                )

                if isinstance(result, dict):
                    # EMA returns results in 'results' key (not 'data')
                    medicines = result.get('results', [])
                    if isinstance(medicines, list) and medicines:
                        validated_count = 0
                        for med in medicines:
                            # VALIDATE MAH - active substance search can return products from other companies
                            product = extract_medicine_data(med, drug_name, validate_mah=True)
                            if product and product['name'] not in all_products:
                                all_products[product['name']] = product
                                if product['therapeutic_area']:
                                    therapeutic_areas[product['therapeutic_area']] += 1
                                validated_count += 1
                        if validated_count > 0:
                            print(f"   EMA active substance search: {validated_count}/{len(medicines)} validated for {drug_name}")

            except Exception as e:
                pass  # Not found by active substance either

        products = list(all_products.values())

        if products:
            print(f"   Found {len(products)} EMA authorized products")
        else:
            print(f"   No EMA products found for {len(all_search_terms)} drug names searched")

        return {
            'total_products': len(products),
            'products': products[:20],
            'product_names': [p['name'] for p in products[:20]],
            'therapeutic_areas': dict(therapeutic_areas.most_common(10)),
            'success': True
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'total_products': 0, 'products': [], 'product_names': [], 'therapeutic_areas': {}, 'success': False, 'error': str(e)}
