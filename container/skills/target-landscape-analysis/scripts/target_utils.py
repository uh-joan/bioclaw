"""
Target resolution and validation utilities for Open Targets integration.
"""

from typing import Dict, Any, Optional


def resolve_target_identity(search_targets_func, target_name: str = None, gene_symbol: str = None) -> Dict[str, Any]:
    """
    Resolve target to official gene symbol and Ensembl ID.

    Args:
        search_targets_func: search_targets function from opentargets_mcp
        target_name: Common name like "GLP-1 receptor"
        gene_symbol: Gene symbol like "GLP1R"

    Returns:
        dict with gene_symbol, official_name, ensembl_id, target_class or error
    """
    search_query = gene_symbol if gene_symbol else target_name

    try:
        search_result = search_targets_func(
            query=search_query,
            size=5
        )

        # Handle nested structure: data.search.hits
        if not search_result or 'data' not in search_result:
            return {'error': f"Target not found: {search_query}"}

        search_data = search_result['data'].get('search', {})
        hits = search_data.get('hits', [])

        if not hits:
            return {'error': f"Target not found: {search_query}"}

        top_target = hits[0]

        return {
            'gene_symbol': top_target.get('name', gene_symbol),
            'official_name': top_target.get('description', target_name),
            'ensembl_id': top_target.get('id'),
            'target_class': 'protein_coding',  # Biotype not in search results
            'uniprot_id': None  # Not in search results
        }

    except Exception as e:
        return {'error': f"Error resolving target: {str(e)}"}


def get_druggability_assessment(get_target_details_func, ensembl_id: str) -> Dict[str, Any]:
    """
    Get druggability and tractability assessment.

    Args:
        get_target_details_func: get_target_details function from opentargets_mcp
        ensembl_id: Ensembl gene ID

    Returns:
        dict with druggability score and tractability details
    """
    try:
        target_details = get_target_details_func(
            id=ensembl_id
        )

        tractability = target_details.get('tractability', {})
        druggability_score = 0.5  # Base score

        # Score based on tractability evidence
        tractable_methods = []
        if tractability.get('smallmolecule', {}).get('buckets', []):
            tractable_methods.append('small_molecule')
            druggability_score += 0.2
        if tractability.get('antibody', {}).get('buckets', []):
            tractable_methods.append('antibody')
            druggability_score += 0.15
        if tractability.get('clinicalPrecedence', False):
            tractable_methods.append('clinical_precedent')
            druggability_score += 0.25

        return {
            'score': min(1.0, round(druggability_score, 2)),
            'tractability': {
                'small_molecule': 'small_molecule' in tractable_methods,
                'antibody': 'antibody' in tractable_methods,
                'clinical_precedent': 'clinical_precedent' in tractable_methods
            }
        }

    except Exception as e:
        return {
            'score': 0.5,
            'tractability': {},
            'error': str(e)
        }


def get_genetic_validation(get_associations_func, ensembl_id: str, top_n: int = 5) -> Dict[str, Any]:
    """
    Get genetic validation evidence from disease associations.

    Args:
        get_associations_func: get_target_disease_associations function from opentargets_mcp
        ensembl_id: Ensembl gene ID
        top_n: Number of top associations to return

    Returns:
        dict with overall_score, evidence_strength, key_associations
    """
    try:
        associations = get_associations_func(
            targetId=ensembl_id,
            minScore=0.3,
            size=top_n * 2  # Get extra to filter
        )

        # Handle nested structure: data.target.associatedDiseases.rows
        key_associations = []
        if associations and 'data' in associations:
            target_data = associations['data'].get('target', {})
            assoc_data = target_data.get('associatedDiseases', {})
            rows = assoc_data.get('rows', [])

            for assoc in rows[:top_n]:
                disease = assoc.get('disease', {})
                key_associations.append({
                    'disease': disease.get('name', 'Unknown'),
                    'disease_id': disease.get('id', 'Unknown'),
                    'association_score': round(assoc.get('score', 0), 2),
                    'evidence_sources': []  # Not available in this response
                })

        # Calculate overall score (average of top associations)
        overall_score = 0.0
        if key_associations:
            overall_score = sum(a['association_score'] for a in key_associations) / len(key_associations)

        # Determine evidence strength
        if overall_score > 0.6:
            strength = "Strong"
        elif overall_score > 0.3:
            strength = "Moderate"
        else:
            strength = "Weak"

        return {
            'overall_score': round(overall_score, 2),
            'evidence_strength': strength,
            'key_associations': key_associations
        }

    except Exception as e:
        return {
            'overall_score': 0.0,
            'evidence_strength': 'Unknown',
            'key_associations': [],
            'error': str(e)
        }


def analyze_selectivity(
    drug_targets: list,
    primary_target: str,
    drug_name: str = None
) -> Dict[str, Any]:
    """
    Analyze target selectivity for radial chart color encoding.

    Classifies drugs as:
    - Selective: Single target (e.g., GLP1R only)
    - Pan-target: Multiple isoforms of same protein (e.g., TGFβ1, TGFβ2, TGFβ3)
    - Multi-specific: Multiple unrelated proteins (e.g., GLP1R + GIPR)

    Args:
        drug_targets: List of target gene symbols (e.g., ['GLP1R', 'GIPR'])
        primary_target: Primary target gene symbol (e.g., 'GLP1R')
        drug_name: Optional drug name for logging

    Returns:
        dict with:
            - selectivity: 'Selective', 'Pan-target', or 'Multi-specific'
            - target_count: Number of targets
            - target_list: List of target genes
            - color_code: Hex color for radial chart
            - description: Human-readable description

    Examples:
        >>> analyze_selectivity(['GLP1R'], 'GLP1R')
        {'selectivity': 'Selective', 'target_count': 1, 'color_code': '#5af78e', ...}

        >>> analyze_selectivity(['TGFB1', 'TGFB2', 'TGFB3'], 'TGFB1')
        {'selectivity': 'Pan-target', 'target_count': 3, 'color_code': '#57c7ff', ...}

        >>> analyze_selectivity(['GLP1R', 'GIPR'], 'GLP1R')
        {'selectivity': 'Multi-specific', 'target_count': 2, 'color_code': '#ff5f56', ...}
    """
    # Normalize inputs
    if not drug_targets:
        drug_targets = [primary_target]

    # Remove duplicates and normalize
    drug_targets = list(set([t.upper().strip() for t in drug_targets if t]))
    primary_target = primary_target.upper().strip()

    # Single target = Selective
    if len(drug_targets) == 1:
        return {
            'selectivity': 'Selective',
            'target_count': 1,
            'target_list': drug_targets,
            'color_code': '#5af78e',  # Green
            'description': f'Selective {drug_targets[0]} targeting'
        }

    # Multiple targets - determine if pan-target or multi-specific
    # Pan-target: All targets share same root (e.g., TGFB1, TGFB2, TGFB3)

    # Extract protein family root (first 3-5 characters)
    # Examples:
    #   TGFB1, TGFB2, TGFB3 → TGFB (pan-target)
    #   TGFBR1, TGFBR2 → TGFBR (pan-target)
    #   GLP1R, GIPR, GCGR → Different roots (multi-specific)

    def get_protein_family(target: str) -> str:
        """Extract protein family root"""
        # Handle common patterns
        if target.startswith('TGFB'):
            return 'TGFB'  # TGFB1, TGFB2, TGFB3, TGFBR1, TGFBR2
        elif target.startswith('ERBB'):
            return 'ERBB'  # ERBB1 (EGFR), ERBB2 (HER2), ERBB3, ERBB4
        elif target.startswith('VEGF'):
            return 'VEGF'  # VEGFA, VEGFB, VEGFC, VEGFR1, VEGFR2
        elif target.startswith('FGF'):
            return 'FGF'   # FGFR1, FGFR2, FGFR3, FGFR4
        elif target.startswith('PDGF'):
            return 'PDGF'  # PDGFR A/B
        elif target.endswith('R'):
            # Receptor - use root without R
            return target[:-1] if len(target) > 2 else target
        else:
            # Use first 3-4 characters
            return target[:4] if len(target) > 4 else target

    # Get families for all targets
    families = [get_protein_family(t) for t in drug_targets]
    unique_families = set(families)

    # If all targets in same family → Pan-target
    if len(unique_families) == 1:
        family = list(unique_families)[0]
        return {
            'selectivity': 'Pan-target',
            'target_count': len(drug_targets),
            'target_list': sorted(drug_targets),
            'color_code': '#57c7ff',  # Blue
            'description': f'Pan-{family} (targets {len(drug_targets)} isoforms: {", ".join(sorted(drug_targets))})'
        }

    # Different families → Multi-specific
    return {
        'selectivity': 'Multi-specific',
        'target_count': len(drug_targets),
        'target_list': sorted(drug_targets),
        'color_code': '#ff5f56',  # Red
        'description': f'Multi-specific ({len(drug_targets)} targets: {", ".join(sorted(drug_targets)[:3])}{"..." if len(drug_targets) > 3 else ""})'
    }
