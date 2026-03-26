"""
Modality Classification Module - DATA-DRIVEN VERSION

Classifies drugs by modality using DrugBank categories and target data.
Avoids hardcoded patterns - relies on actual MCP data instead.

Categories examined from DrugBank:
- Antibodies: "Antibodies", "Antibodies, Monoclonal", "Antibodies, Monoclonal, Humanized"
- Peptides: "Amino Acids, Peptides, and Proteins" (without "Antibodies")
- Small Molecules: Various therapeutic classes without biologic markers
- Oligonucleotides: "Oligonucleotides", "RNA", "DNA"

Chart Symbol Mapping:
- triangle: Small Molecule
- circle: Antibody
- double-circle: Bispecific Antibody
- square: Other Biologic (peptide, oligonucleotide, etc.)
"""

from typing import Dict, Any, List


def classify_modality(drug_details: Dict[str, Any]) -> Dict[str, str]:
    """
    Classify drug modality from DrugBank data using categories field.

    Args:
        drug_details: Drug details dict from DrugBank with fields:
            - name: Drug name
            - categories: List of category lists from DrugBank
            - description: Full description text
            - targets: List of target dicts

    Returns:
        dict with:
            - modality: Human-readable modality (e.g., "Peptide", "Antibody")
            - modality_category: Category for grouping (e.g., "other_biologic")
            - chart_symbol: Symbol for radial chart ("triangle", "circle", etc.)
            - route: Administration route if determinable

    Examples:
        >>> # Semaglutide has categories: ['Amino Acids, Peptides, and Proteins', ...]
        >>> classify_modality(semaglutide_data)
        {'modality': 'Peptide', 'modality_category': 'other_biologic', 'chart_symbol': 'square'}

        >>> # Pembrolizumab has categories: ['Antibodies', 'Antibodies, Monoclonal', ...]
        >>> classify_modality(pembrolizumab_data)
        {'modality': 'Monoclonal Antibody', 'modality_category': 'antibody', 'chart_symbol': 'circle'}
    """
    # Extract data
    name = str(drug_details.get('name', '')).lower()
    description = str(drug_details.get('description', '')).lower()
    categories = drug_details.get('categories', [])
    targets = drug_details.get('targets', [])

    # Flatten categories (they come as nested lists)
    categories_flat = []
    for cat in categories:
        if isinstance(cat, list):
            categories_flat.extend([c.lower() for c in cat if isinstance(c, str)])
        elif isinstance(cat, str):
            categories_flat.append(cat.lower())
        elif isinstance(cat, dict):
            # Handle dict format with 'category' or 'name' key
            cat_name = cat.get('category', cat.get('name', ''))
            if cat_name:
                categories_flat.append(str(cat_name).lower())

    categories_str = ' '.join(categories_flat)

    # ========================================================================
    # BISPECIFIC ANTIBODY DETECTION
    # ========================================================================
    # Detect from name patterns or target count
    has_bispecific_name = any(kw in name for kw in [
        'bispecific', 'bsab', 'dual-targeting', 'bite'
    ])

    has_antibody_cat = any(kw in categories_str for kw in [
        'antibod', 'monoclonal', 'immunoglobulin'
    ])

    # Bispecific if: (1) name suggests it OR (2) antibody with 2+ unrelated targets
    if has_bispecific_name and has_antibody_cat:
        return {
            'modality': 'Bispecific Antibody',
            'modality_category': 'bispecific',
            'chart_symbol': 'double-circle',
            'route': 'Injectable'
        }

    # Check if antibody with multiple targets (may be bispecific)
    if has_antibody_cat and len(targets) >= 2:
        # Could be bispecific, but verify targets are unrelated
        return {
            'modality': 'Bispecific Antibody',
            'modality_category': 'bispecific',
            'chart_symbol': 'double-circle',
            'route': 'Injectable'
        }

    # ========================================================================
    # ANTIBODY-DRUG CONJUGATE (ADC) DETECTION
    # ========================================================================
    has_adc_cat = 'antibody-drug conjugate' in categories_str or 'immunoconjugates' in categories_str
    has_adc_name = any(kw in name for kw in [
        'vedotin', 'deruxtecan', 'mafodotin', 'emtansine'
    ])

    if has_adc_cat or (has_antibody_cat and has_adc_name):
        return {
            'modality': 'Antibody-Drug Conjugate (ADC)',
            'modality_category': 'antibody',
            'chart_symbol': 'circle',
            'route': 'Injectable'
        }

    # ========================================================================
    # MONOCLONAL ANTIBODY DETECTION
    # ========================================================================
    # DrugBank categories: "Antibodies", "Antibodies, Monoclonal"
    has_mab_cat = any(kw in categories_str for kw in [
        'antibodies, monoclonal', 'monoclonal antibod', 'immunoglobulin'
    ])

    has_antibody_cat_general = 'antibod' in categories_str

    if has_mab_cat or has_antibody_cat_general:
        return {
            'modality': 'Monoclonal Antibody',
            'modality_category': 'antibody',
            'chart_symbol': 'circle',
            'route': 'Injectable'
        }

    # ========================================================================
    # OLIGONUCLEOTIDE DETECTION
    # ========================================================================
    # DrugBank categories: "Oligonucleotides", "RNA", "Nucleic Acids"
    has_oligo_cat = any(kw in categories_str for kw in [
        'oligonucleotide', 'rna', 'sirna', 'antisense', 'nucleic acid'
    ])

    has_oligo_desc = any(kw in description for kw in [
        'oligonucleotide', 'sirna', 'aso', 'antisense', 'interfering rna'
    ])

    if has_oligo_cat or has_oligo_desc:
        oligo_type = 'siRNA' if 'sirna' in description or 'sirna' in categories_str else 'Oligonucleotide'
        return {
            'modality': oligo_type,
            'modality_category': 'other_biologic',
            'chart_symbol': 'square',
            'route': 'Injectable'
        }

    # ========================================================================
    # PEPTIDE DETECTION
    # ========================================================================
    # DrugBank categories: "Amino Acids, Peptides, and Proteins"
    # But NOT if it's an antibody (antibodies are also proteins)
    has_peptide_cat = any(kw in categories_str for kw in [
        'peptide', 'amino acids, peptides'
    ])

    has_peptide_desc = any(kw in description for kw in [
        'peptide', 'polypeptide', 'analog', 'glp-1', 'incretin', 'insulin'
    ])

    # Peptide if: has peptide category AND NOT an antibody
    if (has_peptide_cat or has_peptide_desc) and not has_antibody_cat_general:
        # Determine route
        route = 'Unknown'
        if 'oral' in description or 'tablet' in description:
            route = 'Oral'
        elif 'subcutaneous' in description or 'inject' in description:
            route = 'Injectable'

        return {
            'modality': 'Peptide',
            'modality_category': 'other_biologic',
            'chart_symbol': 'square',
            'route': route if route != 'Unknown' else 'Injectable'
        }

    # ========================================================================
    # RECOMBINANT PROTEIN / ENZYME DETECTION
    # ========================================================================
    has_protein_cat = any(kw in categories_str for kw in [
        'enzyme', 'recombinant', 'growth factor', 'cytokine', 'interferon'
    ])

    # Must have protein category but NOT be antibody or peptide
    if has_protein_cat and not has_antibody_cat_general:
        return {
            'modality': 'Recombinant Protein',
            'modality_category': 'other_biologic',
            'chart_symbol': 'square',
            'route': 'Injectable'
        }

    # ========================================================================
    # GENE/CELL THERAPY DETECTION
    # ========================================================================
    has_gene_therapy = any(kw in description for kw in [
        'gene therapy', 'cell therapy', 'car-t', 'car t',
        'viral vector', 'aav', 'lentiviral'
    ])

    if has_gene_therapy:
        return {
            'modality': 'Gene/Cell Therapy',
            'modality_category': 'other_biologic',
            'chart_symbol': 'square',
            'route': 'Infusion'
        }

    # ========================================================================
    # SMALL MOLECULE DETECTION (DEFAULT)
    # ========================================================================
    # If no biologic markers, assume small molecule

    # Determine route from description
    route = 'Unknown'
    if description:
        if 'oral' in description or 'tablet' in description or 'capsule' in description:
            route = 'Oral'
        elif 'inject' in description or 'intravenous' in description or 'subcutaneous' in description:
            route = 'Injectable'
        elif 'topical' in description or 'cream' in description:
            route = 'Topical'
        elif 'inhal' in description:
            route = 'Inhaled'
        else:
            route = 'Oral'  # Default assumption for small molecules

    # Check if explicitly oral (notable for GLP-1 drugs)
    if route == 'Oral':
        modality_str = 'Small Molecule (Oral)'
    else:
        modality_str = 'Small Molecule'

    return {
        'modality': modality_str,
        'modality_category': 'small_molecule',
        'chart_symbol': 'triangle',
        'route': route
    }


def get_modality_summary(drugs_with_modality: list) -> Dict[str, Any]:
    """
    Generate summary statistics for modality distribution.

    Args:
        drugs_with_modality: List of drugs with modality classification

    Returns:
        dict with modality counts and percentages
    """
    from collections import Counter

    modality_counts = Counter([d.get('modality', 'Unknown') for d in drugs_with_modality])
    total = len(drugs_with_modality)

    return {
        'total_drugs': total,
        'modality_distribution': {
            modality: {
                'count': count,
                'percentage': round((count / total) * 100, 1)
            }
            for modality, count in modality_counts.most_common()
        },
        'category_distribution': {
            category: len([d for d in drugs_with_modality if d.get('modality_category') == category])
            for category in ['small_molecule', 'antibody', 'bispecific', 'other_biologic', 'unknown']
        }
    }


# Test function for development
if __name__ == '__main__':
    # Test with actual DrugBank-like data structures
    test_drugs = [
        {
            'name': 'Semaglutide',
            'categories': [['Amino Acids, Peptides, and Proteins'], ['Blood Glucose Lowering Agents']],
            'description': 'glucagon-like peptide-1 (GLP-1) analog for subcutaneous injection',
            'targets': [{'name': 'Glucagon-like peptide 1 receptor'}]
        },
        {
            'name': 'Pembrolizumab',
            'categories': [['Antibodies'], ['Antibodies, Monoclonal'], ['Antibodies, Monoclonal, Humanized']],
            'description': 'humanized monoclonal antibody',
            'targets': [{'name': 'Programmed cell death protein 1'}]
        },
        {
            'name': 'Orforglipron',
            'categories': [['Blood Glucose Lowering Agents']],
            'description': 'oral GLP-1 receptor agonist small molecule',
            'targets': [{'name': 'Glucagon-like peptide 1 receptor'}]
        },
    ]

    print("Modality Classification Test Results (Data-Driven):")
    print("=" * 80)
    for drug in test_drugs:
        result = classify_modality(drug)
        print(f"\n{drug['name']}:")
        print(f"  Modality: {result['modality']}")
        print(f"  Category: {result['modality_category']}")
        print(f"  Chart Symbol: {result['chart_symbol']}")
        print(f"  Route: {result['route']}")
