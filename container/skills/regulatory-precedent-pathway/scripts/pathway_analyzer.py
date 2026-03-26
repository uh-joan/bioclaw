#!/usr/bin/env python3
"""
Pathway Analyzer - Determines optimal submission pathways by region.

Analyzes precedent data to recommend:
- US: NDA vs BLA vs 505(b)(2)
- EU: Centralized vs Decentralized vs National vs Conditional MA

All recommendations grounded in precedent evidence.
"""

from typing import Dict, Any, List, Optional, Callable

from regulatory_constants import US_PATHWAYS, EU_PATHWAYS, MODALITY_KEYWORDS


def classify_modality(modality: str) -> str:
    """Normalize user modality input to canonical category."""
    if not modality:
        return "small molecule"

    modality_lower = modality.lower().strip()
    for canonical, keywords in MODALITY_KEYWORDS.items():
        if any(kw in modality_lower for kw in keywords):
            return canonical
    return modality_lower


def analyze_pathways(
    indication: str,
    modality: str = None,
    target_regions: List[str] = None,
    precedents: List[Dict[str, Any]] = None,
    mcp_funcs: Dict[str, Callable] = None,
) -> Dict[str, Any]:
    """
    Analyze submission pathway options based on modality and precedent data.

    Args:
        indication: Disease/condition
        modality: Drug modality (small molecule, biologic, etc.)
        target_regions: Regions to analyze
        precedents: List of precedent drugs (from precedent_finder)
        mcp_funcs: MCP functions for dynamic data lookup

    Returns:
        Dict with us_pathways, eu_pathways, recommendation_rationale
    """
    if target_regions is None:
        target_regions = ["US", "EU"]
    if precedents is None:
        precedents = []
    if mcp_funcs is None:
        mcp_funcs = {}

    canonical_modality = classify_modality(modality)
    result = {}

    # Analyze precedent pathway distribution
    precedent_pathways = _count_precedent_pathways(precedents)

    if "US" in target_regions:
        result['us_pathways'] = _analyze_us_pathways(
            canonical_modality, precedent_pathways, precedents
        )

    if "EU" in target_regions:
        result['eu_pathways'] = _analyze_eu_pathways(
            canonical_modality, indication, precedent_pathways, precedents
        )

    result['modality'] = canonical_modality
    result['precedent_pathway_distribution'] = precedent_pathways

    return result


def _count_precedent_pathways(precedents: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count pathway types across precedent drugs."""
    counts = {}
    for p in precedents:
        pathway = p.get('approval_pathway', 'Unknown')
        counts[pathway] = counts.get(pathway, 0) + 1
    return counts


def _analyze_us_pathways(
    modality: str,
    precedent_pathways: Dict[str, int],
    precedents: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Analyze US submission pathway options."""
    pathways = []

    # Determine applicable pathways based on modality
    biologic_types = ["biologic", "antibody", "gene therapy", "cell therapy", "vaccine", "peptide", "oligonucleotide"]
    is_biologic = modality in biologic_types

    if is_biologic:
        # BLA is the only option for biologics
        bla = dict(US_PATHWAYS["BLA"])
        bla['recommended'] = True
        bla['rationale'] = f"BLA required for {modality} products."

        # Check precedent support
        bla_count = precedent_pathways.get('BLA', 0)
        if bla_count > 0:
            bla['precedent_support'] = f"{bla_count} precedent(s) used BLA pathway"
            bla_precedents = [p['brand_name'] for p in precedents if p.get('approval_pathway') == 'BLA'][:3]
            bla['precedent_drugs'] = bla_precedents
        else:
            bla['precedent_support'] = "No BLA precedents found (may be first biologic in this indication)"

        pathways.append(bla)
    else:
        # NDA is standard for small molecules
        nda = dict(US_PATHWAYS["NDA"])
        nda_count = precedent_pathways.get('NDA', 0)
        nda['precedent_support'] = f"{nda_count} precedent(s) used NDA pathway"
        nda_precedents = [p['brand_name'] for p in precedents if p.get('approval_pathway') == 'NDA'][:3]
        nda['precedent_drugs'] = nda_precedents

        # 505(b)(2) option
        b2_count = precedent_pathways.get('505(b)(2)', 0)

        # Recommend based on precedent
        if nda_count >= b2_count:
            nda['recommended'] = True
            nda['rationale'] = "Standard pathway with strongest precedent support."
        else:
            nda['recommended'] = False
            nda['rationale'] = "Standard pathway, requires full data package."

        nda['pros'] = ["Well-established pathway", "Clear regulatory expectations", "Full data ownership"]
        nda['cons'] = ["Requires complete clinical data package", "Longer development timeline"]
        pathways.append(nda)

        # Only show 505(b)(2) if there's actual precedent OR few NDA precedents
        # (in crowded therapeutic areas with many NDAs and zero 505(b)(2), it's noise)
        if b2_count > 0 or nda_count < 10:
            b2 = dict(US_PATHWAYS["505(b)(2)"])
            b2['precedent_support'] = f"{b2_count} precedent(s) used 505(b)(2) pathway"

            if b2_count > nda_count:
                b2['recommended'] = True
                b2['rationale'] = "More precedent support than standard NDA in this indication."
            else:
                b2['recommended'] = False
                b2['rationale'] = "Consider if leveraging existing FDA findings for a previously approved drug."

            b2['pros'] = ["Can leverage prior FDA findings", "Potentially reduced clinical program", "Faster path if referencing approved drug"]
            b2['cons'] = ["Must establish bridge to reference drug", "May face additional requirements", "More complex regulatory strategy"]
            pathways.append(b2)

    return pathways


def _analyze_eu_pathways(
    modality: str,
    indication: str,
    precedent_pathways: Dict[str, int],
    precedents: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Analyze EU submission pathway options.

    Uses precedent data to determine if centralized procedure is mandatory
    instead of hardcoded therapeutic area keywords.
    """
    pathways = []

    centralized = dict(EU_PATHWAYS["Centralized"])

    # Check if centralized is mandatory
    mandatory_modalities = centralized.get('mandatory_for', [])

    # Dynamic check: use EU precedent data to determine if centralized is mandatory
    # If all EU precedents used centralized procedure, it's mandatory for this area
    is_mandatory_by_precedent = _eu_precedents_all_centralized(precedents)
    is_mandatory = modality in mandatory_modalities or is_mandatory_by_precedent

    centralized_count = precedent_pathways.get('Centralized MAA', 0)
    eu_precedents = [p for p in precedents if p.get('region') == 'EU']

    if is_mandatory:
        centralized['recommended'] = True
        centralized['rationale'] = f"Mandatory for {modality} products" if modality in mandatory_modalities else f"Mandatory for this therapeutic area"
        centralized['precedent_support'] = f"{centralized_count} EU precedent(s)"
        centralized['pros'] = ["Single application for all EU", "Mandatory pathway (no alternative)", "Largest market access"]
        centralized['cons'] = ["Longer review timeline (~15 months)", "Higher regulatory bar"]
        pathways.append(centralized)
    else:
        centralized['recommended'] = True
        centralized['rationale'] = "Recommended for novel drugs seeking broad EU access."
        centralized['precedent_support'] = f"{centralized_count} EU precedent(s)"
        centralized['pros'] = ["Single application for all EU", "EMA scientific advice available", "Broadest market access"]
        centralized['cons'] = ["Longer review timeline (~15 months)", "Higher regulatory bar"]

        dcp = dict(EU_PATHWAYS["Decentralized"])
        dcp['recommended'] = False
        dcp['rationale'] = "Alternative for well-established drug classes with clear regulatory path."
        dcp['pros'] = ["Faster than centralized", "Reference member state leads", "Can target specific markets"]
        dcp['cons'] = ["Not valid in all EU states simultaneously", "Limited to specific product types"]

        pathways.extend([centralized, dcp])

    # Add Conditional MA only if there's actual precedent or few EU precedents
    # (in crowded areas with many centralized MAAs and zero conditional, it's noise)
    conditional_count = precedent_pathways.get('Conditional MA', 0)
    conditional_drugs = [p for p in eu_precedents if p.get('approval_pathway') == 'Conditional MA']

    if conditional_count > 0 or centralized_count < 10:
        conditional = dict(EU_PATHWAYS["Conditional"])
        conditional['recommended'] = False
        conditional['rationale'] = "Available for drugs addressing unmet medical need with less comprehensive data."
        conditional['precedent_support'] = f"{conditional_count} conditional MA precedent(s) in indication"
        conditional['pros'] = ["Earlier market access", "Addresses unmet need", "Allows data generation post-approval"]
        conditional['cons'] = ["Annual renewal required", "Obligation to complete confirmatory data", "Uncertainty for commercial planning"]

        if conditional_drugs:
            conditional['precedent_drugs'] = [d['brand_name'] for d in conditional_drugs]

        pathways.append(conditional)

    return pathways


def _eu_precedents_all_centralized(precedents: List[Dict[str, Any]]) -> bool:
    """Check if all EU precedents used centralized procedure.

    Fully data-driven: if EU precedent drugs exist and all used centralized MAA,
    the therapeutic area is mandatory for centralized. No hardcoded disease lists.
    """
    eu_precedents = [p for p in precedents if p.get('region') == 'EU']
    if not eu_precedents:
        return False
    # If we have EU precedents and all used centralized, it's mandatory
    centralized_count = sum(
        1 for p in eu_precedents
        if 'centralized' in (p.get('approval_pathway') or '').lower()
        or 'centralised' in (p.get('approval_pathway') or '').lower()
    )
    return centralized_count == len(eu_precedents) and centralized_count > 0
