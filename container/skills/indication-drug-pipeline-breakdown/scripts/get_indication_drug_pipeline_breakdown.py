import sys
import os
import re
import random
from collections import defaultdict

# Add script directory to path for local imports
_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _script_dir)

# Import constants from local module
from constants import (
    DRUG_NAME_MAPPINGS,
)

# Import drug utilities from local module
from drug_utils import (
    normalize_drug_name,
    clean_drug_name_for_display,
    clean_brand_name,
)

# Import brand name lookup utilities from local module
from brand_lookup import (
    get_drug_synonyms,
    extract_brand_name_from_description,
    get_brand_name_from_pubchem,
    get_brand_name_from_fda,
    verify_fda_approval,
    get_brand_name_from_ema,
    get_brand_name_from_drugbank,
    get_all_fda_approved_for_indication,
    get_all_ema_approved_for_indication,
    get_drug_base_name,
    get_generic_name,
)

# Import regulatory checking utilities from local module
from regulatory_checks import (
    check_fda_approval_for_indication,
    check_fda_approval,
    check_ema_approval,
    check_ema_approval_for_indication,
)

# Import trial utilities from local module
from trial_utils import (
    extract_sponsor_from_trial,
    extract_drugs_from_trial,
    extract_enrollment_from_trial,
    search_phase_trials,
    get_trial_detail,
)

# Import sponsor utilities from local module
from sponsor_utils import (
    attribute_company,
    classify_sponsor_type,
)

# Import indication utilities from local module
from indication_utils import (
    resolve_indication_synonyms,
)

# Import visualization utilities from local module
from visualization_utils import (
    dedupe_and_normalize_drugs,
    dedupe_by_base_name,
    build_regulatory_data,
    build_pipeline_highlights,
)

# Import progress tracker from local module
from progress_tracker import create_progress_tracker
from mcp_client import McpClient


def get_indication_drug_pipeline_breakdown(indication: str, sample_per_phase: int = None, skip_regulatory: bool = False, max_regulatory_checks: int = None, progress_callback=None, mcp_funcs=None) -> dict:
    """Analyze drug pipeline for a given indication with phase breakdown and visualization.

    Uses phase-by-phase search strategy for efficiency:
    1. Resolve indication synonyms via NLM API for comprehensive coverage
    2. Search each phase separately (smaller result sets, less pagination)
    3. Fetch detailed trial info via get_study() for accurate drug extraction
    4. Cross-check with FDA/EMA for approval status (optional)

    Args:
        indication (str): Disease/condition (e.g., "obesity", "Alzheimer's disease", "heart failure")
        sample_per_phase (int, optional): Max trials to analyze per phase (default: None = analyze all)
        skip_regulatory (bool): Skip FDA/EMA approval checks for faster results (default: False)
        max_regulatory_checks (int, optional): Max drugs to check against FDA/EMA
            - None (default): Check ALL drugs (full accuracy, ~6-8 min for 100+ drugs)
            - 50: Fast mode (~90s, may miss some approved drugs)
            - 0: Same as None (check all)
        progress_callback: Optional callback(percent, step) for progress reporting

    Returns:
        dict: Contains indication, total_trials, sample_size, total_unique_drugs, approved_drugs,
              phase_breakdown, companies, and visualization
    """
    # BioClaw adaptation: auto-init MCP functions via McpClient if not injected
    if not mcp_funcs:
        _clients = {}
        mcp_funcs = {}
        _server_map = {
            'ctgov': ('ct_gov_studies', {
                'ctgov_search': {'method': 'search'},
                'ctgov_get_study': {'method': 'get'},
            }),
            'fda': ('fda_info', {
                'fda_lookup': {'method': 'lookup_drug'},
            }),
            'ema': ('ema_data', {
                'ema_search': {'method': 'search_medicines'},
            }),
            'pubchem': ('pubchem', {
                'pubchem_search': {'method': 'search_compounds'},
                'pubchem_synonyms': {'method': 'get_compound_synonyms'},
            }),
            'drugbank': ('drugbank_info', {
                'drugbank_get_products': {'method': 'get_drug_details'},
                'drugbank_search_indication': {'method': 'search_by_indication'},
            }),
            'nlm': ('nlm_ct_codes', {
                'nlm_search_codes': {},
            }),
        }
        for srv_name, (tool_name, funcs) in _server_map.items():
            try:
                client = McpClient(srv_name)
                client.connect()
                _clients[srv_name] = client
                for func_key, defaults in funcs.items():
                    def make_fn(c, t, d):
                        def fn(**kw):
                            merged = {**d, **kw}
                            return c.call(t, **merged)
                        return fn
                    mcp_funcs[func_key] = make_fn(client, tool_name, defaults)
            except Exception:
                pass
        print(f"  BioClaw MCP: {len(mcp_funcs)} functions loaded")

    # Create smart progress tracker with realistic time-based weights
    progress = create_progress_tracker(callback=progress_callback, skip_regulatory=skip_regulatory)

    print(f"\n🔍 Analyzing drug pipeline for: {indication}")
    print("=" * 80)
    progress.start_step('init', f"Analyzing drug pipeline for: {indication}")

    # Step 0: Resolve synonyms for comprehensive search
    print(f"\n📖 Resolving indication synonyms via NLM...")
    progress.start_step('synonyms', "Resolving indication synonyms via NLM...")
    synonyms = resolve_indication_synonyms(indication, mcp_funcs)

    if len(synonyms) > 1:
        print(f"  Found {len(synonyms)} terms: {', '.join(synonyms[:5])}{'...' if len(synonyms) > 5 else ''}")
        # Build OR query for CT.gov
        condition_query = ' OR '.join(synonyms)
    else:
        print(f"  Using original term: {indication}")
        condition_query = indication

    # Phase mapping: display name -> CT.gov API value
    # Only include actual drug development phases (exclude "Not Applicable" - observational/device studies)
    PHASES = {
        'Phase 1': 'PHASE1',
        'Phase 2': 'PHASE2',
        'Phase 3': 'PHASE3',
        'Phase 4': 'PHASE4',
    }

    # Step 1: Search each phase separately
    print(f"\n📊 Step 1: Discovering active drug trials by phase...")
    progress.start_step('discovery', "Discovering active drug trials by phase...")

    phase_nct_ids = {}
    total_trials = 0

    for i, (phase_name, phase_code) in enumerate(PHASES.items(), 1):
        progress.report_phase_discovery(i, len(PHASES))
        nct_ids = search_phase_trials(condition_query, phase_code, mcp_funcs=mcp_funcs)
        phase_nct_ids[phase_name] = nct_ids
        count = len(nct_ids)
        total_trials += count
        print(f"  {phase_name}: {count:,} trials")

    progress.complete_step("Phase discovery complete")

    print(f"✓ Total: {total_trials:,} active drug trials across all phases")

    # Step 2: Apply sampling per phase if specified
    sample_size = 0
    for phase_name in PHASES.keys():
        nct_ids = phase_nct_ids[phase_name]
        if sample_per_phase and len(nct_ids) > sample_per_phase:
            phase_nct_ids[phase_name] = random.sample(nct_ids, sample_per_phase)
        sample_size += len(phase_nct_ids[phase_name])

    if sample_per_phase:
        print(f"✓ Sampling up to {sample_per_phase} trials per phase ({sample_size} total)")
    else:
        print(f"✓ Analyzing ALL {sample_size:,} trials (100% coverage)")

    # Phase breakdown data structure
    phase_breakdown = {
        'Phase 1': {'trials': 0, 'drugs': set(), 'enrollment': 0},
        'Phase 2': {'trials': 0, 'drugs': set(), 'enrollment': 0},
        'Phase 3': {'trials': 0, 'drugs': set(), 'enrollment': 0},
        'Phase 4': {'trials': 0, 'drugs': set(), 'enrollment': 0},
    }

    # Company tracking data structure
    company_data = defaultdict(lambda: {
        'trials': 0,
        'phases': set(),
        'drugs': set(),
        'approved': 0,
        'type': 'Unknown',
        'enrollment': 0
    })

    # Sponsor type summary
    sponsor_type_summary = {'Industry': 0, 'Academic': 0, 'Government': 0, 'Unknown': 0}

    all_drugs = set()
    total_processed = 0
    total_enrollment = 0

    # Step 3: Fetch detailed trial info SEQUENTIALLY (accurate but slower)
    print(f"\n💊 Step 2: Fetching detailed trial information by phase...")
    progress.start_step('trial_details', f"Fetching detailed info for {sample_size} trials...")

    # Track overall progress across all phases
    trials_processed_total = 0

    for phase_name in PHASES.keys():
        nct_ids = phase_nct_ids[phase_name]
        if not nct_ids:
            continue

        print(f"\n  Processing {phase_name} ({len(nct_ids)} trials)...")
        processed_in_phase = 0

        for i, nct_id in enumerate(nct_ids):
            # Report granular progress (every trial matters for accurate progress)
            trials_processed_total += 1
            if sample_size > 0:
                progress.report_trial_progress(trials_processed_total, sample_size, phase_name)

            # Console progress indicator
            if (i + 1) % 20 == 0:
                print(f"    {phase_name}: {i + 1}/{len(nct_ids)} processed...")

            try:
                trial_detail = get_trial_detail(nct_id, mcp_funcs=mcp_funcs)

                # Extract data using helper functions
                sponsor_original = extract_sponsor_from_trial(trial_detail)
                sponsor = attribute_company(sponsor_original)
                sponsor_type = classify_sponsor_type(sponsor_original)
                enrollment = extract_enrollment_from_trial(trial_detail)
                drug_interventions = extract_drugs_from_trial(trial_detail)

                if drug_interventions:
                    phase_breakdown[phase_name]['trials'] += 1
                    phase_breakdown[phase_name]['enrollment'] += enrollment
                    total_enrollment += enrollment
                    total_processed += 1
                    processed_in_phase += 1

                    # Track sponsor type
                    sponsor_type_summary[sponsor_type] += 1

                    # Track by company
                    company_data[sponsor]['trials'] += 1
                    company_data[sponsor]['phases'].add(phase_name)
                    company_data[sponsor]['type'] = sponsor_type
                    company_data[sponsor]['enrollment'] += enrollment

                    for drug in drug_interventions:
                        # Clean drug name for display (handles combinations, strips formulations, filters non-drugs)
                        cleaned_drugs = clean_drug_name_for_display(drug)
                        for drug_clean in cleaned_drugs:
                            if drug_clean:
                                phase_breakdown[phase_name]['drugs'].add(drug_clean)
                                all_drugs.add(drug_clean)
                                company_data[sponsor]['drugs'].add(drug_clean)
            except Exception as e:
                continue  # Skip failed trials

        drugs_in_phase = len(phase_breakdown[phase_name]['drugs'])
        enrollment_in_phase = phase_breakdown[phase_name]['enrollment']
        actual_trials = phase_breakdown[phase_name]['trials']
        print(f"  ✓ {phase_name}: {actual_trials} drug trials (of {len(nct_ids)} candidates), {drugs_in_phase} unique drugs, {enrollment_in_phase:,} pts")

    total_unique_drugs = len(all_drugs)
    print(f"\n✓ Processed {total_processed} trials total")
    print(f"✓ Total unique drugs extracted: {total_unique_drugs}")
    print(f"✓ Total target enrollment: {total_enrollment:,} patients")
    print(f"✓ Sponsor breakdown: Industry={sponsor_type_summary['Industry']}, Academic={sponsor_type_summary['Academic']}, Government={sponsor_type_summary['Government']}")

    # Step 3: Cross-check with FDA and EMA for approved drugs (optional)
    approved_drugs = []
    ema_approved_drugs = []

    if skip_regulatory:
        print(f"\n🏛️  Step 3: Skipping regulatory checks (skip_regulatory=True)")
        progress.start_step('regulatory', "Skipping regulatory checks...")
        progress.complete_step()
    else:
        print(f"\n🏛️  Step 3: Cross-checking FDA & EMA for approved drugs...")
        progress.start_step('regulatory', "Preparing regulatory checks...")

        # Track normalized name -> original names mapping (for attribution)
        normalized_to_original = {}

        # Build normalized drug list with deduplication
        for drug in all_drugs:
            normalized = normalize_drug_name(drug)

            # Check if there's a known mapping
            if normalized in DRUG_NAME_MAPPINGS:
                normalized = DRUG_NAME_MAPPINGS[normalized]

            # Skip empty or very short normalized names
            if len(normalized) < 2:
                continue

            if normalized not in normalized_to_original:
                normalized_to_original[normalized] = []
            normalized_to_original[normalized].append(drug)

        unique_normalized = list(normalized_to_original.keys())

        # Determine how many drugs to check based on max_regulatory_checks parameter
        # None or 0 = check all (full accuracy), otherwise limit to specified number
        if max_regulatory_checks is None or max_regulatory_checks == 0:
            drugs_to_check = unique_normalized
            mode_label = "full accuracy mode"
        else:
            drugs_to_check = unique_normalized[:max_regulatory_checks]
            mode_label = f"fast mode (limited to {max_regulatory_checks})"

        total_checks = len(drugs_to_check)
        if total_checks < len(unique_normalized):
            print(f"  Checking {total_checks}/{len(unique_normalized)} drugs ({mode_label})")
        else:
            print(f"  Checking all {total_checks} unique drugs ({mode_label})")
        print(f"  Checking {total_checks} drugs against FDA & EMA (sequential)...")

        approved_normalized = set()
        ema_approved_normalized = set()

        # Sequential checks (MCP doesn't parallelize well)
        # Use indication-specific approval checking to filter to drugs approved for THIS indication
        for i, normalized_name in enumerate(drugs_to_check):
            # Report progress for EVERY drug - this is the slowest step (55% of job time)
            progress.report_regulatory_progress(i + 1, total_checks)

            # Console progress every 5 drugs
            if (i + 1) % 5 == 0:
                print(f"    Progress: {i + 1}/{total_checks}...")

            # FDA check - indication-specific
            fda_result = check_fda_approval_for_indication(normalized_name, synonyms)
            if fda_result['approved']:
                approved_normalized.add(normalized_name)

            # EMA check - indication-specific
            ema_result = check_ema_approval_for_indication(normalized_name, synonyms, mcp_funcs=mcp_funcs)
            if ema_result['approved']:
                ema_approved_normalized.add(normalized_name)

        # Build approved drug lists from normalized matches
        for normalized_name in approved_normalized:
            if normalized_name in normalized_to_original:
                approved_drugs.extend(normalized_to_original[normalized_name])

        # Helper to get base drug name for deduplication (strips INN suffixes)
        # INN suffixes like "alfa", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta"
        # are used for biologics but refer to the same product
        def get_dedup_key(drug_name: str) -> str:
            """Get deduplication key by stripping INN suffixes and normalizing."""
            key = drug_name.lower().strip()
            # Strip common INN suffixes (Greek letters used for biologics)
            inn_suffixes = [
                ' alfa', ' beta', ' gamma', ' delta', ' epsilon', ' zeta', ' eta', ' theta',
                ' pegol', ' vedotin', ' emtansine', ' mertansine', ' ozogamicin',
                ' sudotox', ' tansine', '-ailt', '-adnp', '-bsph', '-ccit', '-cwdp',
                '-dtin', '-fhsr', '-hcpx', '-jjmc', '-kaaz', '-nxsg', '-onrg',
                '-pdon', '-pkpw', '-rwmc', '-svza', '-swsk', '-treg', '-twsp', '-xevg',
            ]
            for suffix in inn_suffixes:
                if key.endswith(suffix):
                    key = key[:-len(suffix)]
                    break
            return key

        # Deduplicate approved_drugs list (case-insensitive, INN-suffix-aware)
        seen = set()
        approved_drugs_deduped = []
        for d in approved_drugs:
            dedup_key = get_dedup_key(d)
            if dedup_key not in seen:
                seen.add(dedup_key)
                approved_drugs_deduped.append(d)
        approved_drugs = approved_drugs_deduped

        print(f"✓ FDA: {len(approved_drugs)} approved drugs (from {len(approved_normalized)} unique matches)")

        # Build EMA approved drug list
        for normalized_name in ema_approved_normalized:
            if normalized_name in normalized_to_original:
                ema_approved_drugs.extend(normalized_to_original[normalized_name])

        # Deduplicate EMA approved drugs (case-insensitive, INN-suffix-aware)
        seen_ema = set()
        ema_approved_drugs_deduped = []
        for d in ema_approved_drugs:
            dedup_key = get_dedup_key(d)
            if dedup_key not in seen_ema:
                seen_ema.add(dedup_key)
                ema_approved_drugs_deduped.append(d)
        ema_approved_drugs = ema_approved_drugs_deduped

        print(f"✓ EMA: {len(ema_approved_drugs)} EU approved drugs (from {len(ema_approved_normalized)} unique matches)")
        progress.complete_step(f"Regulatory checks complete: {len(approved_drugs)} FDA, {len(ema_approved_drugs)} EMA")

    # Attribute approved drugs to companies
    for company in company_data:
        company_approved_count = sum(
            1 for drug in company_data[company]['drugs']
            if drug in approved_drugs
        )
        company_data[company]['approved'] = company_approved_count

    # Step 4: Create visualization
    print(f"\n📈 Step 4: Creating pipeline visualization...")
    progress.start_step('visualization', "Creating pipeline visualization...")

    # Build phase breakdown dict with counts
    phase_summary = {}
    for phase, data in phase_breakdown.items():
        phase_summary[phase] = {
            'trials': data['trials'],
            'unique_drugs': len(data['drugs']),
            'drugs': sorted(list(data['drugs']))[:10],  # Top 10 for display
            'enrollment': data['enrollment']
        }

    print("  Normalizing drug names via PubChem...")
    progress.update_step(0.1, "Normalizing drug names to generic (PubChem)...")

    # Drugs in trials that are approved
    fda_in_trials = dedupe_and_normalize_drugs(approved_drugs)
    ema_in_trials = dedupe_and_normalize_drugs(ema_approved_drugs)

    # Search for ALL approved drugs for this indication (including those not in trials)
    print("  Searching for all approved drugs for indication...")
    progress.update_step(0.3, "Searching for all approved drugs (DrugBank + EMA)...")

    # Now returns dict: {generic_name: brand_name}
    all_fda_approved_dict = get_all_fda_approved_for_indication(synonyms, mcp_funcs)
    all_ema_approved_dict = get_all_ema_approved_for_indication(synonyms, mcp_funcs)

    progress.update_step(0.5, "Building brand name mappings...")

    # Build brand name mappings (normalize generic names, clean brand names)
    fda_brand_map = {}  # {generic_lower: brand_name}
    for generic, brand in all_fda_approved_dict.items():
        normalized = get_generic_name(generic)
        # Clean brand name to filter out generic+manufacturer patterns
        cleaned_brand = clean_brand_name(brand, normalized) if brand else None
        if cleaned_brand and normalized.lower() not in fda_brand_map:
            fda_brand_map[normalized.lower()] = cleaned_brand

    ema_brand_map = {}  # {generic_lower: brand_name}
    for generic, brand in all_ema_approved_dict.items():
        normalized = get_generic_name(generic)
        # Clean brand name to filter out generic+manufacturer patterns (common in EMA)
        cleaned_brand = clean_brand_name(brand, normalized) if brand else None
        if cleaned_brand and normalized.lower() not in ema_brand_map:
            ema_brand_map[normalized.lower()] = cleaned_brand

    # Normalize DrugBank/EMA results with base name deduplication
    # This prevents duplicates like "Cladribine" + "Cladribine Subcutaneous Injection"
    fda_from_drugbank = dedupe_by_base_name(all_fda_approved_dict)
    ema_from_search = dedupe_by_base_name(all_ema_approved_dict)

    # Track which are in trials vs not (use base names for smarter matching)
    # This prevents duplicates like "Fingolimod (Gilenya)" + "Fingolimod Hydrochloride"
    fda_in_trials_lower = {d.lower() for d in fda_in_trials}
    fda_in_trials_base = {get_drug_base_name(d) for d in fda_in_trials}
    ema_in_trials_lower = {d.lower() for d in ema_in_trials}
    ema_in_trials_base = {get_drug_base_name(d) for d in ema_in_trials}

    # Merge: all approved = in trials + not in trials (dedupe by base name)
    # IMPORTANT: Don't modify fda_in_trials_base/ema_in_trials_base - use separate tracking sets
    # These sets are used later to determine which drugs get the ⚗️ "in trials" marker
    all_fda_approved_merged = set(fda_in_trials)
    fda_seen_base = set(fda_in_trials_base)  # Separate tracking for deduplication
    for drug in fda_from_drugbank:
        drug_base = get_drug_base_name(drug)
        # Only add if base name not already present (avoids salt form duplicates)
        if drug.lower() not in fda_in_trials_lower and drug_base not in fda_seen_base:
            all_fda_approved_merged.add(drug)
            fda_seen_base.add(drug_base)  # Track to prevent further duplicates (not in_trials!)

    all_ema_approved_merged = set(ema_in_trials)
    ema_seen_base = set(ema_in_trials_base)  # Separate tracking for deduplication
    for drug in ema_from_search:
        drug_base = get_drug_base_name(drug)
        # Only add if base name not already present (avoids salt form duplicates)
        if drug.lower() not in ema_in_trials_lower and drug_base not in ema_seen_base:
            all_ema_approved_merged.add(drug)
            ema_seen_base.add(drug_base)  # Track to prevent further duplicates (not in_trials!)

    progress.update_step(0.6, "Looking up brand names (FDA, PubChem, EMA)...")

    # Fill in brand names for drugs from trials that don't have brand names yet
    # This catches drugs found via clinical trials cross-check (not in DrugBank search)
    # Try FDA first, then PubChem (excellent synonym data), then EMA as final fallback
    for drug in all_fda_approved_merged:
        drug_lower = drug.lower()
        if drug_lower not in fda_brand_map:
            brand = get_brand_name_from_fda(drug, mcp_funcs)
            if not brand:
                # Try PubChem synonyms - excellent coverage for older generics
                brand = get_brand_name_from_pubchem(drug, mcp_funcs=mcp_funcs)
            if not brand:
                # Try EMA as fallback for newer drugs not yet in FDA label database
                brand = get_brand_name_from_ema(drug, mcp_funcs)
            if brand:
                # Clean brand name to filter generic+manufacturer patterns
                cleaned_brand = clean_brand_name(brand, drug)
                if cleaned_brand:
                    fda_brand_map[drug_lower] = cleaned_brand

    # Fill in EMA brand names for drugs from trials that don't have brand names yet
    # Try EMA first, then PubChem as fallback
    for drug in all_ema_approved_merged:
        drug_lower = drug.lower()
        if drug_lower not in ema_brand_map:
            brand = get_brand_name_from_ema(drug, mcp_funcs)
            if not brand:
                # Try PubChem synonyms as fallback - excellent coverage
                brand = get_brand_name_from_pubchem(drug, mcp_funcs=mcp_funcs)
            if brand:
                # Clean brand name to filter generic+manufacturer patterns (common in EMA)
                cleaned_brand = clean_brand_name(brand, drug)
                if cleaned_brand:
                    ema_brand_map[drug_lower] = cleaned_brand

    progress.update_step(0.8, "Building regulatory status table...")

    # Build structured regulatory data for HTML template
    regulatory_data = build_regulatory_data(
        fda_approved=all_fda_approved_merged,
        ema_approved=all_ema_approved_merged,
        fda_brand_map=fda_brand_map,
        ema_brand_map=ema_brand_map,
        fda_in_trials_lower=fda_in_trials_lower,
        fda_in_trials_base=fda_in_trials_base,
        ema_in_trials_lower=ema_in_trials_lower,
        ema_in_trials_base=ema_in_trials_base,
    )

    progress.update_step(0.9, "Building pipeline highlights...")

    # Build pipeline highlights (unapproved/novel drugs by phase)
    pipeline_highlights = build_pipeline_highlights(
        phase_breakdown=phase_breakdown,
        fda_approved=all_fda_approved_merged,
        ema_approved=all_ema_approved_merged,
    )

    # Filter to industry companies only, sort by drug count
    industry_companies = [
        (name, data) for name, data in company_data.items()
        if data['type'] == 'Industry'
    ]
    sorted_companies = sorted(
        industry_companies,
        key=lambda x: (len(x[1]['drugs']), x[1]['trials']),  # Primary: drugs, secondary: trials
        reverse=True
    )[:10]  # Top 10 industry companies

    progress.complete_step("Analysis complete!")

    # Format company data for return
    formatted_companies = []
    for company, data in sorted_companies:
        formatted_companies.append({
            'company': company,
            'type': data['type'],
            'trials': data['trials'],
            'phases': sorted(list(data['phases'])),
            'drugs': sorted(list(data['drugs'])),
            'approved_count': data['approved'],
            'enrollment': data['enrollment']
        })

    return {
        'indication': indication,
        'synonyms_used': synonyms,  # Show what terms were searched
        'total_trials': total_trials,
        'sample_size': sample_size,
        'total_unique_drugs': total_unique_drugs,
        'total_enrollment': total_enrollment,
        'approved_drugs': approved_drugs,
        'ema_approved_drugs': ema_approved_drugs,
        'regulatory_status': regulatory_data,  # Structured data for HTML rendering
        'pipeline_highlights': pipeline_highlights,  # Unapproved/novel drugs by phase
        'sponsor_breakdown': sponsor_type_summary,
        'phase_breakdown': phase_summary,
        'companies': formatted_companies,
        'total_companies': len(company_data),
    }

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python3 get_indication_drug_pipeline_breakdown.py <INDICATION> [SAMPLE_PER_PHASE] [--skip-regulatory] [--max-checks=N]")
        print("\nExamples:")
        print("  # Full analysis (all trials in each phase)")
        print("  python3 get_indication_drug_pipeline_breakdown.py 'obesity'")
        print("")
        print("  # Sample up to N trials per phase (faster)")
        print("  python3 get_indication_drug_pipeline_breakdown.py 'heart failure' 50")
        print("")
        print("  # Skip regulatory checks (fastest)")
        print("  python3 get_indication_drug_pipeline_breakdown.py 'obesity' 20 --skip-regulatory")
        print("")
        print("  # Limit regulatory checks to top 10 drugs")
        print("  python3 get_indication_drug_pipeline_breakdown.py 'obesity' 20 --max-checks=10")
        sys.exit(1)

    test_indication = sys.argv[1]

    # Parse options
    sample = None
    skip_regulatory = False
    max_checks = 20

    for arg in sys.argv[2:]:
        if arg == '--skip-regulatory':
            skip_regulatory = True
        elif arg.startswith('--max-checks='):
            max_checks = int(arg.split('=')[1])
        elif arg.isdigit():
            sample = int(arg)

    result = get_indication_drug_pipeline_breakdown(
        test_indication,
        sample_per_phase=sample,
        skip_regulatory=skip_regulatory,
        max_regulatory_checks=max_checks
    )

    print("\n" + "=" * 80)
    print("✅ PIPELINE ANALYSIS COMPLETE")
    print("=" * 80)
    coverage = 100 if result['sample_size'] == result['total_trials'] else int(100 * result['sample_size'] / result['total_trials'])
    print(f"Coverage: {result['sample_size']} of {result['total_trials']:,} trials ({coverage}%)")
    print(f"Identified {result['total_unique_drugs']} unique drug interventions")
    print(f"Target enrollment: {result['total_enrollment']:,} patients")
    print(f"FDA approved: {len(result['approved_drugs'])} | EMA approved: {len(result['ema_approved_drugs'])}")
    sb = result['sponsor_breakdown']
    print(f"Sponsors: Industry={sb['Industry']}, Academic={sb['Academic']}, Government={sb['Government']}")
    print(f"Tracked {result['total_companies']} unique companies/sponsors")
    print("=" * 80)
