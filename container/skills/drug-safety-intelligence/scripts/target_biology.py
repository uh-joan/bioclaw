"""Target biology analysis for drug safety intelligence.

Uses OpenTargets to:
- Get tissue expression profile -> organ toxicity map
- Extract knockout phenotypes -> predicted on-target toxicities
- Identify known safety liabilities from target biology

All classification uses body-system stems (not hardcoded tissue/phenotype lists).
"""

from typing import Dict, Any, List, Optional
import re


# Body-system stems for organ classification and phenotype severity.
# Same organ systems used across the skill (risk_matrix_builder, epidemiology_context).
# These are medical constants (anatomy), not drug-specific.
_BODY_SYSTEM_ORGAN = {
    # stem → (organ_system, severity_weight)
    'cardiac': ('Cardiovascular', 0.75),
    'heart': ('Cardiovascular', 0.75),
    'vascular': ('Cardiovascular', 0.70),
    'hepat': ('Hepatic', 0.70),
    'liver': ('Hepatic', 0.70),
    'renal': ('Renal', 0.65),
    'kidney': ('Renal', 0.65),
    'pulmon': ('Pulmonary', 0.65),
    'lung': ('Pulmonary', 0.65),
    'brain': ('CNS', 0.60),
    'neuron': ('CNS', 0.60),
    'cerebr': ('CNS', 0.60),
    'nervous': ('CNS', 0.60),
    'pancrea': ('Pancreatic', 0.65),
    'intestin': ('GI', 0.30),
    'colon': ('GI', 0.30),
    'stomach': ('GI', 0.30),
    'gastric': ('GI', 0.30),
    'bone marrow': ('Hematologic', 0.60),
    'blood': ('Hematologic', 0.60),
    'haemato': ('Hematologic', 0.60),
    'hemato': ('Hematologic', 0.60),
    'lymph': ('Immune', 0.55),
    'spleen': ('Immune', 0.55),
    'thymus': ('Immune', 0.55),
    'immune': ('Immune', 0.55),
    'skin': ('Dermatologic', 0.25),
    'eye': ('Ocular', 0.40),
    'retina': ('Ocular', 0.40),
    'muscle': ('Musculoskeletal', 0.25),
    'bone': ('Musculoskeletal', 0.25),
    'thyroid': ('Endocrine', 0.50),
    'adrenal': ('Endocrine', 0.50),
    'pituitary': ('Endocrine', 0.50),
    'testis': ('Reproductive', 0.50),
    'ovary': ('Reproductive', 0.50),
    'uterus': ('Reproductive', 0.50),
}

# Severity signal words for phenotype classification (medical severity, not drug-specific)
_SEVERITY_SIGNAL_WORDS = {
    # Severe / life-threatening
    'lethal': 'severe', 'lethality': 'severe', 'death': 'severe',
    'arrest': 'severe', 'failure': 'severe', 'necrosis': 'severe',
    'hemorrhag': 'severe', 'bleeding': 'severe',
    'seizure': 'severe', 'paralysis': 'severe',
    'immunodeficien': 'severe', 'autoimmun': 'severe',
    'tumor': 'severe', 'cancer': 'severe', 'neoplasm': 'severe',
    # Moderate
    'fibrosis': 'moderate', 'edema': 'moderate',
    'inflammation': 'moderate', 'infertil': 'moderate',
    'retard': 'moderate', 'weight loss': 'moderate',
    'anemia': 'moderate', 'anaemia': 'moderate',
    'arrhythmi': 'moderate', 'cardiomyopath': 'moderate',
    'thrombocytopen': 'moderate', 'hypertension': 'moderate',
    'glucose': 'moderate', 'insulin': 'moderate', 'diabetes': 'moderate',
    'hyperlipid': 'moderate',
}


def _classify_tissue(tissue_name: str) -> Optional[str]:
    """Map tissue name to organ system using body-system stems."""
    tissue_lower = tissue_name.lower()
    for pattern, (organ, _) in _BODY_SYSTEM_ORGAN.items():
        if pattern in tissue_lower:
            return organ
    return None


def _classify_phenotype_severity(phenotype: str) -> str:
    """Classify KO phenotype severity using signal words.

    Uses organ-system severity weights + medical severity signal words.
    """
    pheno_lower = phenotype.lower()

    # Check severity signal words first
    for pattern, severity in _SEVERITY_SIGNAL_WORDS.items():
        if pattern in pheno_lower:
            return severity

    # Check body-system severity weight
    for pattern, (_, weight) in _BODY_SYSTEM_ORGAN.items():
        if pattern in pheno_lower:
            if weight >= 0.6:
                return 'severe'
            elif weight >= 0.4:
                return 'moderate'
            return 'mild'

    return 'mild'


def _parse_opentargets_text(text: str) -> Dict[str, Any]:
    """Parse OpenTargets markdown text response."""
    result = {
        'gene_symbol': None,
        'target_name': None,
        'target_class': None,
        'subcellular_locations': [],
        'tissues': [],
        'ko_phenotypes': [],
        'safety_liabilities': [],
        'tractability': {},
    }

    if not isinstance(text, str):
        return result

    # Extract gene symbol
    gene_match = re.search(r'\*\*Approved Symbol:\*\*\s*(\S+)', text)
    if gene_match:
        result['gene_symbol'] = gene_match.group(1)

    # Extract target name
    name_match = re.search(r'\*\*Approved Name:\*\*\s*(.+?)(?:\n|$)', text)
    if name_match:
        result['target_name'] = name_match.group(1).strip()

    # Extract target class
    class_match = re.search(r'\*\*Target Class:\*\*\s*(.+?)(?:\n|$)', text)
    if class_match:
        result['target_class'] = class_match.group(1).strip()

    # Extract subcellular locations
    loc_match = re.search(r'\*\*Subcellular Locations?:\*\*\s*(.+?)(?:\n\n|\n\*\*|$)', text, re.DOTALL)
    if loc_match:
        locations = [loc.strip().strip('- ') for loc in loc_match.group(1).split('\n') if loc.strip()]
        result['subcellular_locations'] = [l for l in locations if l]

    # Extract safety liabilities section
    safety_match = re.search(r'(?:Safety|Known Safety).*?:(.*?)(?:\n\n|\n#{2,}|$)', text, re.DOTALL | re.IGNORECASE)
    if safety_match:
        liabilities = [l.strip().strip('- ') for l in safety_match.group(1).split('\n') if l.strip()]
        result['safety_liabilities'] = [l for l in liabilities if l and len(l) > 3]

    # Extract tractability
    tract_match = re.search(r'(?:Tractability|Druggability).*?:(.*?)(?:\n\n|\n#{2,}|$)', text, re.DOTALL | re.IGNORECASE)
    if tract_match:
        tract_text = tract_match.group(1)
        result['tractability'] = {
            'small_molecule': 'small molecule' in tract_text.lower() and 'yes' in tract_text.lower(),
            'antibody': 'antibod' in tract_text.lower() and 'yes' in tract_text.lower(),
        }

    return result


def _extract_expression_from_json(details: Dict) -> List[Dict]:
    """Extract expression data from OpenTargets JSON response.

    Uses native anatomicalSystems/organs fields when available.
    """
    expressions = []
    target_data = details.get('data', {}).get('target', details)
    expression_data = target_data.get('expressions', [])

    for expr in expression_data:
        tissue_label = expr.get('label', '')
        organ_systems = expr.get('anatomicalSystems', [])
        organs = expr.get('organs', [])

        # Use native organ groupings if available (no need for hardcoded mapping)
        organ_system = None
        if organ_systems:
            organ_system = organ_systems[0].get('label', '') if isinstance(organ_systems[0], dict) else str(organ_systems[0])
        elif organs:
            organ_system = organs[0].get('label', '') if isinstance(organs[0], dict) else str(organs[0])
        elif tissue_label:
            organ_system = _classify_tissue(tissue_label)

        if organ_system or tissue_label:
            expressions.append({
                'tissue': tissue_label,
                'organ_system': organ_system or 'Other',
                'rna_level': expr.get('rna', {}).get('level', 0) if isinstance(expr.get('rna'), dict) else 0,
                'protein_level': expr.get('protein', {}).get('level', 0) if isinstance(expr.get('protein'), dict) else 0,
            })

    return expressions


def analyze_target_biology(
    opentargets_search_func,
    opentargets_get_target_func,
    opentargets_get_associations_func,
    target_name: str,
    tracker=None,
) -> Dict[str, Any]:
    """
    Analyze target biology for safety-relevant insights.

    Args:
        opentargets_search_func: OpenTargets search wrapper
        opentargets_get_target_func: OpenTargets get_target_details wrapper
        opentargets_get_associations_func: OpenTargets associations wrapper
        target_name: Target name or gene symbol
        tracker: ProgressTracker instance

    Returns:
        dict with tissue_expression, organ_toxicity_map, ko_phenotypes, safety_liabilities
    """
    result = {
        'target_name': target_name,
        'gene_symbol': None,
        'ensembl_id': None,
        'target_class': None,
        'tissue_expression': [],
        'organ_toxicity_map': {},
        'ko_phenotypes': [],
        'safety_liabilities': [],
        'tractability': {},
        'error': None,
    }

    if tracker:
        tracker.start_step('target_biology', f"Searching OpenTargets for {target_name}...")

    # Step 1: Resolve target identity
    try:
        search_result = opentargets_search_func(method='search_targets', query=target_name, limit=5)
    except Exception as e:
        result['error'] = f"OpenTargets search failed: {e}"
        return result

    # Parse search result text
    if isinstance(search_result, str):
        id_match = re.search(r'(ENSG\d+)', search_result)
        if id_match:
            result['ensembl_id'] = id_match.group(1)
        gene_match = re.search(r'\*\*Symbol:\*\*\s*(\S+)', search_result)
        if gene_match:
            result['gene_symbol'] = gene_match.group(1)
    elif isinstance(search_result, dict):
        targets = search_result.get('targets', search_result.get('results', []))
        if targets and isinstance(targets, list) and len(targets) > 0:
            first = targets[0]
            result['ensembl_id'] = first.get('ensembl_id', first.get('id'))
            result['gene_symbol'] = first.get('gene_symbol', first.get('approvedSymbol'))

    if not result['ensembl_id']:
        result['error'] = f"Could not resolve target: {target_name}"
        if tracker:
            tracker.complete_step(f"Target not found: {target_name}")
        return result

    if tracker:
        tracker.update_step(0.3, f"Found {result['gene_symbol'] or target_name} ({result['ensembl_id']})")

    # Step 2: Get detailed target info
    try:
        details = opentargets_get_target_func(target_id=result['ensembl_id'])
    except Exception as e:
        result['error'] = f"OpenTargets details failed: {e}"
        if tracker:
            tracker.complete_step(f"Target details error: {e}")
        return result

    if isinstance(details, str):
        parsed = _parse_opentargets_text(details)
        result['target_class'] = parsed.get('target_class')
        result['safety_liabilities'] = parsed.get('safety_liabilities', [])
        result['tractability'] = parsed.get('tractability', {})
        if parsed.get('gene_symbol'):
            result['gene_symbol'] = parsed['gene_symbol']
        if parsed.get('target_name'):
            result['target_name'] = parsed['target_name']
    elif isinstance(details, dict):
        result['target_class'] = details.get('target_class', details.get('targetClass'))
        result['safety_liabilities'] = details.get('safety_liabilities', [])

        # Use native JSON expression data (with anatomicalSystems/organs)
        expressions = _extract_expression_from_json(details)
        result['tissue_expression'] = expressions

    if tracker:
        tracker.update_step(0.6, f"Analyzing tissue expression for {result['gene_symbol'] or target_name}...")

    # Step 3: Build organ toxicity map from expression data
    if isinstance(details, str):
        # Parse tissue mentions from text (fallback for text responses)
        tissue_sections = re.findall(
            r'(?:express|tissue|organ).*?[:]\s*(.+?)(?:\n\n|\n#{2,}|$)',
            details, re.DOTALL | re.IGNORECASE
        )
        for section in tissue_sections:
            tissues = [t.strip().strip('- ') for t in section.split('\n') if t.strip()]
            for tissue in tissues:
                if tissue and len(tissue) > 2:
                    organ = _classify_tissue(tissue)
                    if organ:
                        if organ not in result['organ_toxicity_map']:
                            result['organ_toxicity_map'][organ] = {
                                'tissues': [],
                                'risk_level': 'monitor',
                            }
                        result['organ_toxicity_map'][organ]['tissues'].append(tissue)
    elif result['tissue_expression']:
        # Build from structured expression data
        for expr in result['tissue_expression']:
            organ = expr.get('organ_system')
            if organ and organ != 'Other':
                if organ not in result['organ_toxicity_map']:
                    result['organ_toxicity_map'][organ] = {
                        'tissues': [],
                        'risk_level': 'monitor',
                    }
                result['organ_toxicity_map'][organ]['tissues'].append(expr['tissue'])

    # Step 4: Extract KO phenotypes
    if isinstance(details, str):
        ko_sections = re.findall(
            r'(?:phenotype|knockout|KO|mouse model).*?[:]\s*(.+?)(?:\n\n|\n#{2,}|$)',
            details, re.DOTALL | re.IGNORECASE
        )
        for section in ko_sections:
            phenotypes = [p.strip().strip('- ') for p in section.split('\n') if p.strip()]
            for pheno in phenotypes:
                if pheno and len(pheno) > 3:
                    severity = _classify_phenotype_severity(pheno)
                    result['ko_phenotypes'].append({
                        'phenotype': pheno,
                        'severity': severity,
                    })

    if tracker:
        organs = len(result['organ_toxicity_map'])
        phenotypes = len(result['ko_phenotypes'])
        tracker.complete_step(
            f"Target biology: {organs} organ systems, {phenotypes} KO phenotypes, "
            f"{len(result['safety_liabilities'])} safety liabilities"
        )

    return result
