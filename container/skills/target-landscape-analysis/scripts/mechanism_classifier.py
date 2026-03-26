"""
Mechanism Classification Module - DATA-DRIVEN VERSION

Parses drug mechanism using DrugBank targets and mechanism_of_action text.
Avoids hardcoded target-specific logic - relies on actual MCP data.

Uses:
- DrugBank 'targets' field: List of protein targets with names
- DrugBank 'mechanism_of_action' text: Mechanism description
- DrugBank 'pharmacodynamics' text: Additional mechanism details

Classifies by:
- Mechanism type: agonist, antagonist, inhibitor, modulator, etc. (from text parsing)
- Multi-specificity: Single vs multiple targets (from targets list)
- Sector assignment: For radial chart visualization (derived from mechanism + targets)
"""

from typing import Dict, Any, List


def classify_mechanism(
    drug_details: Dict[str, Any],
    target_gene: str,
    target_name: str = None
) -> Dict[str, Any]:
    """
    Classify drug mechanism from DrugBank data using targets and mechanism_of_action.

    Args:
        drug_details: Drug details dict from DrugBank with:
            - name: Drug name
            - mechanism_of_action: Mechanism description text
            - pharmacodynamics: Additional mechanism text
            - targets: List of target dicts with 'name' field
        target_gene: Primary target gene symbol (e.g., "GLP1R")
        target_name: Optional human-readable target name

    Returns:
        dict with:
            - mechanism_summary: Human-readable summary
            - mechanism_type: Category (agonist, antagonist, inhibitor, etc.)
            - is_multispecific: Boolean - targets multiple proteins
            - targets: List of target gene symbols
            - target_count: Number of targets
            - sector: Radial chart sector assignment
            - mechanism_detail: Extended description

    Examples:
        >>> # Semaglutide targets GLP1R only
        >>> classify_mechanism(semaglutide_data, 'GLP1R')
        {'mechanism_type': 'agonist', 'is_multispecific': False, 'targets': ['GLP1R'], ...}

        >>> # Tirzepatide targets GLP1R and GIPR
        >>> classify_mechanism(tirzepatide_data, 'GLP1R')
        {'mechanism_type': 'dual-agonist', 'is_multispecific': True, 'targets': ['GLP1R', 'GIPR'], ...}
    """
    name = str(drug_details.get('name', '')).lower()
    mechanism = str(drug_details.get('mechanism_of_action', '')).lower()
    pharmacodynamics = str(drug_details.get('pharmacodynamics', '')).lower()
    description = str(drug_details.get('description', '')).lower()

    # Combine all text for mechanism analysis
    all_text = f"{mechanism} {pharmacodynamics} {description}"

    # Extract targets from DrugBank
    targets_raw = drug_details.get('targets', [])
    target_names = []

    for t in targets_raw:
        if isinstance(t, dict):
            tname = t.get('name', '')
            if tname:
                target_names.append(tname)
        elif isinstance(t, str):
            target_names.append(t)

    # Normalize primary target
    target_gene_norm = target_gene.upper()

    # ========================================================================
    # DETERMINE MECHANISM TYPE FROM TEXT
    # ========================================================================
    mechanism_type = _parse_mechanism_type(all_text)

    # ========================================================================
    # DETERMINE MULTI-SPECIFICITY FROM TARGETS
    # ========================================================================
    is_multispecific = len(target_names) > 1
    target_count = len(target_names) if target_names else 1

    # Extract target gene symbols (simplified - use names if genes not available)
    target_genes = _extract_target_genes(target_names, target_gene_norm)

    # ========================================================================
    # GENERATE MECHANISM SUMMARY
    # ========================================================================
    if is_multispecific and target_count == 2:
        # Dual agonist/inhibitor
        if 'agonist' in mechanism_type:
            mechanism_summary = f"{'/'.join(target_genes[:2])} dual agonist"
            mech_detail = f"Activates {' and '.join(target_genes[:2])} receptors"
        else:
            mechanism_summary = f"{'/'.join(target_genes[:2])} dual {mechanism_type}"
            mech_detail = f"{mechanism_type.capitalize()} targeting {' and '.join(target_genes[:2])}"
    elif is_multispecific and target_count >= 3:
        # Triple or multi-target
        mechanism_summary = f"Multi-target {mechanism_type}"
        mech_detail = f"{mechanism_type.capitalize()} targeting {target_count} proteins"
    else:
        # Single target
        mechanism_summary = f"{target_gene} {mechanism_type}"
        mech_detail = f"{mechanism_type.capitalize()} of {target_gene}"

    # ========================================================================
    # DETERMINE SECTOR FOR RADIAL CHART
    # ========================================================================
    sector = _determine_sector(
        target_genes,
        mechanism_type,
        is_multispecific,
        target_gene_norm
    )

    return {
        'mechanism_summary': mechanism_summary,
        'mechanism_type': mechanism_type,
        'is_multispecific': is_multispecific,
        'targets': target_genes if target_genes else [target_gene],
        'target_count': target_count,
        'sector': sector,
        'mechanism_detail': mech_detail
    }


def _parse_mechanism_type(text: str) -> str:
    """
    Parse mechanism type from text using keyword detection.

    Precedence:
    1. Agonist (activates receptor)
    2. Antagonist (blocks receptor)
    3. Inhibitor (blocks enzyme/protein)
    4. Modulator (allosteric, PAM, NAM)
    5. Activator
    6. Other
    """
    text_lower = text.lower()

    # Check for agonist (but not antagonist which contains "agonist")
    if 'agonist' in text_lower and 'antagonist' not in text_lower:
        # Check if partial agonist
        if 'partial agonist' in text_lower:
            return 'partial-agonist'
        return 'agonist'

    # Check for antagonist or blocker
    if 'antagonist' in text_lower or 'blocker' in text_lower:
        return 'antagonist'

    # Check for inhibitor
    if 'inhibit' in text_lower:
        # Determine subtype
        if 'allosteric' in text_lower:
            return 'allosteric-inhibitor'
        elif 'competitive' in text_lower:
            return 'competitive-inhibitor'
        elif 'irreversible' in text_lower:
            return 'irreversible-inhibitor'
        return 'inhibitor'

    # Check for modulator
    if 'modulator' in text_lower:
        if 'positive allosteric' in text_lower or 'pam' in text_lower:
            return 'positive-modulator'
        elif 'negative allosteric' in text_lower or 'nam' in text_lower:
            return 'negative-modulator'
        return 'modulator'

    # Check for activator
    if 'activat' in text_lower:
        return 'activator'

    # Check for degrader (PROTACs)
    if 'degrader' in text_lower or 'protac' in text_lower:
        return 'degrader'

    # Default
    return 'other'


def _extract_target_genes(target_names: List[str], primary_gene: str) -> List[str]:
    """
    Extract gene symbols from target names.

    DrugBank targets have full names like:
    - "Glucagon-like peptide 1 receptor" → GLP1R
    - "Glucose-dependent insulinotropic receptor" → GIPR
    - "Programmed cell death protein 1" → PDCD1 (PD-1)

    For now, use simplified mapping. In future, could use Open Targets API.
    """
    gene_symbols = []

    # Common target name → gene symbol mappings
    name_to_gene = {
        'glucagon-like peptide 1 receptor': 'GLP1R',
        'glucose-dependent insulinotropic receptor': 'GIPR',
        'glucagon receptor': 'GCGR',
        'programmed cell death protein 1': 'PDCD1',
        'programmed cell death 1 ligand 1': 'CD274',
        'cytotoxic t-lymphocyte protein 4': 'CTLA4',
        'epidermal growth factor receptor': 'EGFR',
        'human epidermal growth factor receptor 2': 'ERBB2',
        'vascular endothelial growth factor a': 'VEGFA',
        'transforming growth factor beta-1': 'TGFB1',
        'transforming growth factor beta-2': 'TGFB2',
        'transforming growth factor beta-3': 'TGFB3',
        'proprotein convertase subtilisin/kexin type 9': 'PCSK9',
    }

    for target_name in target_names:
        target_lower = target_name.lower()

        # Try exact match
        if target_lower in name_to_gene:
            gene_symbols.append(name_to_gene[target_lower])
        else:
            # Try partial match for complex names
            matched = False
            for name_key, gene_key in name_to_gene.items():
                if name_key in target_lower or target_lower in name_key:
                    gene_symbols.append(gene_key)
                    matched = True
                    break

            # Fallback: use simplified name
            if not matched:
                # Extract first letters of each word (crude gene symbol)
                words = target_lower.split()
                if len(words) <= 3:
                    gene_symbols.append(''.join([w[0].upper() for w in words if w]))
                else:
                    gene_symbols.append(target_name[:10])  # Use first 10 chars

    # Ensure primary target is first
    if gene_symbols and primary_gene.upper() in [g.upper() for g in gene_symbols]:
        # Move primary to front
        gene_symbols = [g for g in gene_symbols if g.upper() != primary_gene.upper()]
        gene_symbols.insert(0, primary_gene.upper())
    elif not gene_symbols:
        gene_symbols = [primary_gene.upper()]

    return gene_symbols


def _determine_sector(
    target_genes: List[str],
    mechanism_type: str,
    is_multispecific: bool,
    primary_target: str
) -> str:
    """
    Determine radial chart sector based on targets and mechanism.

    Sectors group drugs by:
    - Single target: "{TARGET} {TYPE}" (e.g., "GLP1R Agonist")
    - Dual target: "{TARGET1}/{TARGET2} Dual" (e.g., "GLP1R/GIPR Dual")
    - Multi-target: "Multi-{TYPE}" (e.g., "Multi-Agonist")
    """
    if is_multispecific:
        if len(target_genes) == 2:
            # Dual-target sector
            return f"{'/'.join(target_genes[:2])} Dual"
        else:
            # Multi-target sector
            return f"Multi-{mechanism_type.capitalize()}"
    else:
        # Single-target sector
        return f"{primary_target} {mechanism_type.capitalize()}"


# Test function
if __name__ == '__main__':
    test_cases = [
        {
            'drug': {
                'name': 'Semaglutide',
                'mechanism_of_action': 'Semaglutide is a glucagon-like peptide-1 (GLP-1) receptor agonist',
                'targets': [{'name': 'Glucagon-like peptide 1 receptor'}]
            },
            'gene': 'GLP1R',
            'expected_type': 'agonist',
            'expected_multi': False
        },
        {
            'drug': {
                'name': 'Tirzepatide',
                'mechanism_of_action': 'dual glucose-dependent insulinotropic polypeptide (GIP) and GLP-1 receptor agonist',
                'targets': [
                    {'name': 'Glucagon-like peptide 1 receptor'},
                    {'name': 'Glucose-dependent insulinotropic receptor'}
                ]
            },
            'gene': 'GLP1R',
            'expected_type': 'agonist',
            'expected_multi': True
        },
        {
            'drug': {
                'name': 'Pembrolizumab',
                'mechanism_of_action': 'Pembrolizumab is a PD-1 blocking antibody',
                'targets': [{'name': 'Programmed cell death protein 1'}]
            },
            'gene': 'PDCD1',
            'expected_type': 'antagonist',
            'expected_multi': False
        },
    ]

    print("Mechanism Classification Test Results (Data-Driven):")
    print("=" * 80)
    for case in test_cases:
        result = classify_mechanism(case['drug'], case['gene'])
        print(f"\n{case['drug']['name']} ({case['gene']}):")
        print(f"  Summary: {result['mechanism_summary']}")
        print(f"  Type: {result['mechanism_type']} (expected: {case['expected_type']})")
        print(f"  Multi-specific: {result['is_multispecific']} (expected: {case['expected_multi']})")
        print(f"  Targets: {result['targets']}")
        print(f"  Sector: {result['sector']}")
