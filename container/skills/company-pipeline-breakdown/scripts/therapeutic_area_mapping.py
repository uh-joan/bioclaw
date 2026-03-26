"""Therapeutic area classification for conditions in clinical trials.

Two-tier classification strategy:
1. PRIMARY: MeSH D-code lookup from mesh_to_ta.json (220 codes mapped via NLM API)
2. FALLBACK: Keyword-stem matching for conditions without MeSH codes

The MeSH map was built by querying the NLM MeSH REST API for ~98 seed disease terms,
resolving D-codes to tree numbers, and mapping tree prefixes to therapeutic areas.
"""

import json
import os
import re
from typing import Tuple, Optional

# =============================================================================
# TIER 1: MeSH D-code lookup (primary classifier)
# =============================================================================
# Load D-code → TA mapping built from NLM API data.
# 220 entries covering 14 therapeutic areas.

_script_dir = os.path.dirname(os.path.abspath(__file__))
_mesh_map_path = os.path.join(_script_dir, 'mesh_to_ta.json')

try:
    with open(_mesh_map_path, 'r') as f:
        _MESH_TO_TA = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    _MESH_TO_TA = {}

# MeSH tree prefix → TA (fallback for D-codes not in the prebuilt map)
# Based on NLM MeSH tree structure: C = Diseases, F = Psychiatry/Psychology
_TREE_PREFIX_TO_TA = {
    'C01': 'Infectious Disease', 'C02': 'Infectious Disease', 'C03': 'Infectious Disease',
    'C04': 'Oncology',
    'C05': 'Musculoskeletal',
    'C06': 'Gastroenterology',
    'C07': 'Dentistry',
    'C08': 'Respiratory',
    'C09': 'Otolaryngology',
    'C10': 'Neurology',
    'C11': 'Ophthalmology',
    'C12': 'Nephrology',  # Male urogenital
    'C13': "Women's Health",
    'C14': 'Cardiovascular',
    'C15': 'Hematology',
    'C16': 'Rare Disease',  # Congenital/hereditary
    'C17': 'Dermatology',
    'C18': 'Metabolic/Endocrine',
    'C19': 'Metabolic/Endocrine',
    'C20': 'Immunology',
    'C23': 'Other',  # Pathological conditions (too broad)
    'C25': 'Oncology',  # Chemically-induced disorders → often chemo
    'C26': 'Other',  # Wounds/injuries
    'F03': 'Psychiatry',
}

# =============================================================================
# TIER 2: Keyword-stem fallback (compact — ~5 stems per TA vs 30+ full keywords)
# =============================================================================
# Each stem covers the root morpheme, catching inflected forms automatically.
# Priority order matters for disambiguation (e.g., "diabetic retinopathy" → Ophthalmology).

_TA_KEYWORD_STEMS = [
    # Check narrow/specific TAs first to avoid broad captures
    ('Ophthalmology', [
        'macular degeneration', 'amd', 'glaucoma', 'retinopathy', 'retinal',
        'uveitis', 'dry eye', 'cataract', 'corneal', 'ocular', 'ophthalm',
        'retinitis pigmentosa', 'stargardt', 'kerato', 'intraocular',
        'diabetic macular edema', 'visual impairment', 'blindness',
        'thyroid eye disease',
    ]),
    ('Nephrology', [
        'kidney', 'renal', 'nephro', 'nephriti', 'nephrotic', 'dialysis',
        'glomerulo', 'proteinuria', 'albuminuria', 'hematuria',
        'ckd', 'esrd', 'eskd', 'fsgs', 'pkd', 'adpkd',
        'hyperkalemia',
    ]),
    ('Oncology', [
        'cancer', 'tumor', 'tumour', 'carcinom', 'lymphoma', 'leukem', 'leukaem',
        'melanoma', 'sarcoma', 'myeloma', 'neoplas', 'metasta', 'malignan',
        'glioblastoma', 'glioma', 'neuroblastoma', 'mesothelioma',
        'hodgkin', 'myelodysplast', 'myeloproliferat', 'waldenstrom',
        'car-t', 'car t', 'chimeric antigen', 'checkpoint inhibitor',
    ]),
    ('Rare Disease', [
        'orphan', 'rare disease', 'ultra-rare', 'genetic disorder',
        'lysosomal', 'gaucher', 'fabry', 'pompe', 'niemann-pick',
        'mucopolysaccharid', 'hemophilia', 'factor viii', 'factor ix',
        'sickle cell', 'thalassem', 'huntington', 'friedreich',
        'phenylketonuria', 'pku', 'hereditary angioedema',
        'tuberous sclerosis', 'neurofibromatosis', 'epidermolysis bullosa',
        'gene therapy', 'gene editing', 'crispr', 'aav',
    ]),
    ('Infectious Disease', [
        'hiv', 'aids', 'hepatitis', 'hcv', 'hbv', 'influenza',
        'covid', 'sars-cov', 'coronavirus', 'rsv', 'respiratory syncytial',
        'tuberculo', 'malaria', 'sepsis', 'bacteremia',
        'pneumonia', 'mrsa', 'c. diff', 'clostridioides',
        'vaccine', 'vaccination', 'immunization', 'prophylaxis',
        'antiretroviral', 'antiviral', 'antibiotic', 'antimicrobial',
        'fungal infection', 'antifungal', 'candida', 'aspergillus',
    ]),
    ('Hematology', [
        'anemia', 'anaemia', 'thrombocytopeni', 'neutropeni',
        'blood disorder', 'coagul', 'bleeding disorder',
        'polycythemia vera', 'myelofibrosis', 'essential thrombocythemia',
        'paroxysmal nocturnal', 'pnh', 'hemolytic uremic',
        'von willebrand', 'hematopoietic', 'bone marrow transplant',
        'itp', 'ttp', 'mds',
    ]),
    ('Metabolic/Endocrine', [
        'diabetes', 'diabetic', 't2dm', 't1dm', 'obesity', 'overweight',
        'weight loss', 'weight management', 'metabolic syndrome',
        'nash', 'nafld', 'fatty liver', 'mash', 'masld', 'steatohepatitis',
        'thyroid', 'hypothyroid', 'hyperthyroid', 'cushing', 'addison',
        'glp-1', 'glp1', 'sglt2', 'dpp-4', 'incretin', 'insulin',
        'osteoporosis', 'gout', 'hyperuricemia', 'acromegaly',
        'pcos', 'polycystic ovary', 'endometriosis', 'hypogonadism',
    ]),
    ('Neurology', [
        'alzheimer', 'parkinson', 'epilepsy', 'seizure', 'migraine',
        'dementia', 'stroke', 'multiple sclerosis', 'neuropath',
        'neuralgia', 'spinal muscular atrophy', 'sma', 'duchenne',
        'muscular dystrophy', 'als', 'amyotrophic lateral',
        'ataxia', 'dystonia', 'tremor', 'narcolepsy', 'insomnia',
        'neurodegenerat', 'brain injury', 'guillain-barre',
        'lewy body', 'progressive supranuclear', 'huntington',
    ]),
    ('Psychiatry', [
        'depression', 'depressive', 'anxiety', 'schizophreni',
        'psychosis', 'psychotic', 'bipolar', 'mania', 'manic',
        'adhd', 'attention deficit', 'ptsd', 'post-traumatic',
        'ocd', 'obsessive', 'psychiatric', 'mental health',
        'autism', 'substance abuse', 'addiction', 'opioid use',
        'alcohol use', 'eating disorder', 'anorexia', 'bulimia',
        'suicid', 'agitation',
    ]),
    ('Cardiovascular', [
        'heart failure', 'cardiomyopath', 'hypertension', 'blood pressure',
        'atrial fibrillation', 'arrhythmia', 'tachycardia', 'bradycardia',
        'coronary', 'angina', 'myocardial infarction', 'heart attack',
        'thrombosis', 'pulmonary embolism', 'atheroscleros',
        'peripheral artery', 'cardiovascular', 'cardiac',
        'pericarditis', 'myocarditis', 'endocarditis',
        'dyslipidemia', 'hyperlipidemia', 'hypercholesterol',
        'pcsk9', 'aortic stenosis', 'congenital heart',
    ]),
    ('Immunology', [
        'rheumatoid arthritis', 'lupus', 'sle', 'autoimmune',
        'ankylosing spondylitis', 'spondyloarthritis',
        'myasthenia gravis', 'pemphigus', 'pemphigoid',
        'scleroderma', 'systemic sclerosis', 'sjogren', 'vasculitis',
        'giant cell arteritis', 'graft versus host', 'gvhd',
        'transplant rejection', 'immune-mediated', 'jak inhibitor',
    ]),
    ('Respiratory', [
        'asthma', 'copd', 'chronic obstructive pulmonary', 'emphysema',
        'cystic fibrosis', 'pulmonary fibrosis', 'ipf',
        'interstitial lung', 'bronchiectasis', 'sarcoidosis',
        'pulmonary hypertension', 'ards', 'sleep apnea',
        'allergic rhinitis', 'sinusitis', 'alpha-1 antitrypsin',
    ]),
    ('Dermatology', [
        'psoriasis', 'psoriatic', 'atopic dermatitis', 'eczema',
        'acne', 'rosacea', 'alopecia', 'hair loss', 'vitiligo',
        'hidradenitis', 'pruritus', 'prurigo', 'urticaria', 'hives',
        'cutaneous', 'dermatolog', 'wound healing',
    ]),
    ('Gastroenterology', [
        'crohn', 'ulcerative colitis', 'inflammatory bowel', 'ibd',
        'irritable bowel', 'ibs', 'gerd', 'gastroesophageal reflux',
        'celiac', 'cirrhosis', 'pancreatitis', 'gallbladder',
        'barrett', 'achalasia', 'eosinophilic esophagitis',
        'gastroparesis', 'constipation', 'gi bleeding',
        'short bowel', 'intestinal failure',
    ]),
    ("Women's Health", [
        'endometriosis', 'uterine fibroid', 'leiomyoma',
        'menopause', 'vasomotor symptoms', 'hot flash',
        'contraception', 'fertility', 'infertility', 'ivf',
        'preeclampsia', 'gestational', 'postpartum',
        'menorrhagia', 'dysmenorrhea', 'vulvovaginal',
    ]),
]

# =============================================================================
# SUBTYPE CLASSIFICATION (compact keyword sets)
# =============================================================================

_SUBTYPE_KEYWORDS = {
    'Solid Tumors': ['carcinoma', 'adenocarcinoma', 'squamous', 'melanoma', 'sarcoma',
                     'lung cancer', 'breast cancer', 'prostate cancer', 'colorectal',
                     'glioblastoma', 'renal cell', 'hepatocellular'],
    'Hematologic': ['leukemia', 'lymphoma', 'myeloma', 'myeloid', 'hodgkin'],
    'Immuno-Oncology': ['checkpoint', 'car-t', 'car t', 'chimeric antigen',
                        'pd-1', 'pd-l1', 'ctla-4', 'immunotherapy'],
    'Neurodegeneration': ['alzheimer', 'parkinson', 'dementia', 'huntington',
                          'frontotemporal', 'lewy body', 'neurodegeneration'],
    'Movement Disorders': ['parkinson', 'tremor', 'dystonia', 'ataxia', 'chorea'],
    'Pain': ['migraine', 'headache', 'neuropathy', 'neuralgia', 'neuropathic pain'],
    'Sleep': ['narcolepsy', 'insomnia', 'sleep disorder', 'restless leg'],
    'Neuromuscular': ['muscular dystrophy', 'duchenne', 'als', 'amyotrophic',
                      'spinal muscular', 'sma', 'myasthenia', 'guillain'],
    'Heart Failure': ['heart failure', 'hfref', 'hfpef', 'cardiomyopathy'],
    'Arrhythmia': ['atrial fibrillation', 'afib', 'arrhythmia', 'tachycardia'],
    'Lipids': ['dyslipidemia', 'hyperlipidemia', 'cholesterol', 'triglyceride', 'pcsk9'],
    'Thrombosis': ['thrombosis', 'dvt', 'pulmonary embolism', 'anticoagulant'],
    'Diabetes': ['diabetes', 'diabetic', 't2dm', 't1dm', 'glycemic', 'hba1c', 'glp-1', 'sglt2'],
    'Obesity': ['obesity', 'overweight', 'weight loss', 'weight management', 'bmi'],
    'Liver Disease': ['nash', 'nafld', 'fatty liver', 'mash', 'steatohepatitis', 'cirrhosis'],
    'Viral': ['hiv', 'hepatitis', 'covid', 'influenza', 'rsv', 'herpes', 'cmv'],
    'Bacterial': ['bacterial', 'antibiotic', 'mrsa', 'c. diff', 'tuberculosis'],
    'Vaccines': ['vaccine', 'vaccination', 'immunization', 'prophylaxis'],
    'Asthma/COPD': ['asthma', 'copd', 'chronic obstructive', 'emphysema'],
    'Fibrosis': ['pulmonary fibrosis', 'ipf', 'interstitial lung'],
    'Mood Disorders': ['depression', 'depressive', 'bipolar', 'mania'],
    'Psychotic Disorders': ['schizophrenia', 'psychosis', 'psychotic'],
    'Anxiety': ['anxiety', 'gad', 'panic', 'ptsd', 'ocd'],
    'Substance Use': ['substance abuse', 'addiction', 'opioid use', 'alcohol use'],
    'Bleeding Disorders': ['hemophilia', 'factor viii', 'factor ix', 'von willebrand'],
    'Anemias': ['anemia', 'sickle cell', 'thalassemia'],
    'IBD': ['crohn', 'ulcerative colitis', 'inflammatory bowel', 'ibd'],
    'Retinal': ['macular degeneration', 'amd', 'diabetic retinopathy', 'retinal',
                'retinitis pigmentosa'],
    'Anterior Segment': ['glaucoma', 'dry eye', 'cataract', 'corneal'],
    'CKD': ['chronic kidney', 'ckd', 'esrd', 'dialysis', 'eskd'],
    'Glomerular Disease': ['glomerulonephritis', 'iga nephropathy', 'fsgs', 'nephrotic'],
    'Inflammatory': ['psoriasis', 'atopic', 'eczema', 'hidradenitis'],
    'Gene Therapy': ['gene therapy', 'gene replacement', 'aav', 'crispr', 'gene editing'],
    'Rheumatology': ['rheumatoid', 'arthritis', 'lupus', 'ankylosing', 'spondylitis'],
    'Transplant': ['graft versus host', 'gvhd', 'transplant rejection'],
}

# TA → list of valid subtypes (for validation)
_TA_SUBTYPES = {
    'Oncology': ['Solid Tumors', 'Hematologic', 'Supportive Care', 'Immuno-Oncology'],
    'Immunology': ['Rheumatology', 'Dermatology', 'Gastroenterology', 'Transplant'],
    'Neurology': ['Neurodegeneration', 'Movement Disorders', 'Pain', 'Sleep', 'Neuromuscular'],
    'Cardiovascular': ['Heart Failure', 'Arrhythmia', 'Vascular', 'Lipids', 'Thrombosis'],
    'Metabolic/Endocrine': ['Diabetes', 'Obesity', 'Liver Disease', 'Lipids', 'Bone', 'Thyroid'],
    'Infectious Disease': ['Viral', 'Bacterial', 'Vaccines', 'Fungal', 'Parasitic'],
    'Respiratory': ['Asthma/COPD', 'Rare Lung Disease', 'Fibrosis', 'Sleep'],
    'Rare Disease': ['Genetic', 'Hematologic', 'Metabolic', 'Neuromuscular', 'Gene Therapy'],
    'Ophthalmology': ['Retinal', 'Anterior Segment', 'Inherited'],
    'Psychiatry': ['Mood Disorders', 'Psychotic Disorders', 'Anxiety', 'Substance Use', 'Developmental'],
    'Hematology': ['Bleeding Disorders', 'Anemias', 'Platelet Disorders', 'Myeloproliferative'],
    "Women's Health": ['Reproductive', 'Menopause', 'Oncology', 'Fertility'],
    'Nephrology': ['CKD', 'Glomerular Disease', 'Transplant', 'Rare Kidney'],
    'Gastroenterology': ['IBD', 'Liver Disease', 'Functional GI', 'Upper GI'],
    'Dermatology': ['Inflammatory', 'Autoimmune', 'Infectious', 'Oncology'],
}


# =============================================================================
# PUBLIC API
# =============================================================================

def classify_therapeutic_area(condition: str) -> Tuple[str, Optional[str]]:
    """
    Map a condition string to a therapeutic area and optional subtype.

    Uses keyword-stem matching (Tier 2 fallback). For MeSH-based classification
    of entire trials, use classify_trial_therapeutic_area() instead.

    Args:
        condition: Condition string (e.g., "Type 2 Diabetes Mellitus")

    Returns:
        Tuple of (therapeutic_area, subtype)
    """
    if not condition:
        return ('Other', None)

    condition_lower = condition.lower().strip()

    for ta_name, stems in _TA_KEYWORD_STEMS:
        for stem in stems:
            if stem in condition_lower:
                subtype = _classify_subtype(condition_lower, ta_name)
                return (ta_name, subtype)

    return ('Other', None)


def classify_trial_therapeutic_area(trial_text: str) -> str:
    """
    Classify a trial's primary therapeutic area using MeSH codes first,
    keyword-stem fallback second.

    This is the preferred classification method — it uses structured MeSH D-codes
    from CT.gov's MeSH Terms section, which are more reliable than keyword matching.

    Args:
        trial_text: Full trial markdown from CT.gov get_study()

    Returns:
        Primary therapeutic area string (e.g., "Oncology")
    """
    # TIER 1: Extract MeSH D-codes and look them up
    d_codes = _extract_mesh_codes(trial_text)
    ta_votes = {}
    for code in d_codes:
        ta = _MESH_TO_TA.get(code)
        if ta:
            ta_votes[ta] = ta_votes.get(ta, 0) + 1

    if ta_votes:
        # Return the TA with the most MeSH term votes
        return max(ta_votes, key=ta_votes.get)

    # TIER 2: Fallback to keyword-stem matching on condition strings
    conditions = extract_conditions_from_trial(trial_text)
    return get_primary_therapeutic_area(conditions)


def classify_conditions(conditions: list) -> dict:
    """Classify multiple conditions and aggregate by therapeutic area."""
    ta_counts = {}
    for condition in conditions:
        ta, _ = classify_therapeutic_area(condition)
        ta_counts[ta] = ta_counts.get(ta, 0) + 1
    return ta_counts


def get_primary_therapeutic_area(conditions: list) -> str:
    """Get the primary (most common) therapeutic area from a list of conditions."""
    if not conditions:
        return 'Other'

    ta_counts = classify_conditions(conditions)
    sorted_tas = sorted(ta_counts.items(), key=lambda x: x[1], reverse=True)

    for ta, count in sorted_tas:
        if ta != 'Other':
            return ta
    return 'Other'


def extract_conditions_from_trial(trial_markdown: str) -> list:
    """
    Extract condition names from trial markdown.

    Returns:
        List of condition strings (human-readable names, not D-codes)
    """
    conditions = []

    # Pattern 1: ## Conditions section with bullet list
    conditions_section = re.search(r'## Conditions\s*\n((?:- .+\n?)+)', trial_markdown)
    if conditions_section:
        section_text = conditions_section.group(1)
        bullet_items = re.findall(r'- (.+?)(?:\n|$)', section_text)
        conditions.extend([item.strip() for item in bullet_items if item.strip()])

    # Pattern 2: ## MeSH Terms (Conditions) section — extract term names (not codes)
    mesh_section = re.search(r'## MeSH Terms \(Conditions\)\s*\n((?:- .+\n?)+)', trial_markdown)
    if mesh_section:
        section_text = mesh_section.group(1)
        mesh_items = re.findall(r'- ([^(]+)\s*\([^)]+\)', section_text)
        conditions.extend([item.strip() for item in mesh_items if item.strip()])

    # Pattern 3: Old format with ### Condition:
    condition_matches = re.findall(r'###\s+Condition:\s*(.+?)(?:\n|$)', trial_markdown)
    conditions.extend([c.strip() for c in condition_matches if c.strip()])

    # Pattern 4: **Conditions:** inline format
    inline_conditions = re.search(
        r'\*\*Conditions?:\*\*\s*(.+?)(?:\n\n|\n\*\*|$)', trial_markdown, re.DOTALL)
    if inline_conditions:
        section_text = inline_conditions.group(1)
        lines = section_text.split('\n')
        for line in lines:
            line = re.sub(r'^[\s\-\*\u2022]+', '', line).strip()
            if line and len(line) > 2 and line not in conditions:
                conditions.append(line)

    # Remove duplicates while preserving order
    seen = set()
    unique_conditions = []
    for c in conditions:
        c_lower = c.lower()
        if c_lower not in seen:
            seen.add(c_lower)
            unique_conditions.append(c)

    return unique_conditions


# =============================================================================
# INTERNAL HELPERS
# =============================================================================

def _extract_mesh_codes(trial_text: str) -> list:
    """Extract MeSH D-codes from trial markdown's MeSH Terms section.

    CT.gov format: "- Alzheimer Disease (D000544)"
    Returns list of D-codes like ["D000544", "D000008"]
    """
    mesh_section = re.search(
        r'## MeSH Terms \(Conditions\)\s*\n((?:- .+\n?)+)', trial_text)
    if not mesh_section:
        return []

    # Extract D-codes (and C-codes) from parenthetical refs
    return re.findall(r'\(([DC]\d+)\)', mesh_section.group(1))


def _classify_subtype(condition_lower: str, ta_name: str) -> Optional[str]:
    """Classify into a subtype within a therapeutic area."""
    valid_subtypes = _TA_SUBTYPES.get(ta_name, [])
    if not valid_subtypes:
        return None

    for subtype in valid_subtypes:
        keywords = _SUBTYPE_KEYWORDS.get(subtype)
        if keywords:
            for keyword in keywords:
                if keyword in condition_lower:
                    return subtype
    return None


if __name__ == "__main__":
    # Test the classifier
    test_conditions = [
        "Type 2 Diabetes Mellitus",
        "Non-Small Cell Lung Cancer",
        "Rheumatoid Arthritis",
        "Alzheimer's Disease",
        "Obesity",
        "Diabetic Retinopathy",
        "Chronic Kidney Disease",
        "Crohn's Disease",
        "Atopic Dermatitis",
        "Heart Failure",
        "Multiple Sclerosis",
        "Psoriasis",
        "Breast Cancer",
        "HIV Infection",
        "Asthma",
        "Duchenne Muscular Dystrophy",
        "Age-Related Macular Degeneration",
        "Major Depressive Disorder",
        "Hemophilia A",
        "Ulcerative Colitis",
    ]

    print("Therapeutic Area Classification Test")
    print("=" * 60)
    print(f"MeSH map loaded: {len(_MESH_TO_TA)} D-codes")
    print()

    for condition in test_conditions:
        ta, subtype = classify_therapeutic_area(condition)
        subtype_str = f" ({subtype})" if subtype else ""
        print(f"{condition:40} -> {ta}{subtype_str}")
