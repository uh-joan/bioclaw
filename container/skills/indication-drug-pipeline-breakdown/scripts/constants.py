"""Constants used throughout the indication drug pipeline breakdown skill."""

# Company M&A hierarchy (acquired → parent company)
# Updated: 2025-11-25
COMPANY_HIERARCHY = {
    # Major pharma M&A
    'Celgene': 'Bristol Myers Squibb',
    'Celgene Corporation': 'Bristol Myers Squibb',
    'Array BioPharma': 'Pfizer',
    'Array BioPharma Inc.': 'Pfizer',
    'Five Prime Therapeutics': 'Amgen',
    'Mirati Therapeutics': 'Bristol Myers Squibb',  # Acquired Jan 2024
    'ChemoCentryx': 'Amgen',  # Acquired 2022
    'Immunomedics': 'Gilead Sciences',  # Acquired 2020
    'Kite Pharma': 'Gilead Sciences',  # Acquired 2017
    'Tesaro': 'GlaxoSmithKline',  # Acquired 2019
    'Loxo Oncology': 'Eli Lilly',  # Acquired 2019
    'Spark Therapeutics': 'Roche',  # Acquired 2019
    'Genmab': 'Johnson & Johnson',  # Partnership, not acquisition
    'Pharmacyclics': 'AbbVie',  # Acquired 2015

    # Normalize company name variations
    'Pfizer Inc': 'Pfizer',
    'Pfizer Inc.': 'Pfizer',
    'Amgen Inc': 'Amgen',
    'Amgen Inc.': 'Amgen',
    'Bristol-Myers Squibb': 'Bristol Myers Squibb',
    'Bristol-Myers Squibb Company': 'Bristol Myers Squibb',
    'Eli Lilly and Company': 'Eli Lilly',
    'Merck & Co.': 'Merck',
    'Merck & Co., Inc.': 'Merck',
    'Novartis Pharmaceuticals': 'Novartis',
    'Roche Holding AG': 'Roche',
    'F. Hoffmann-La Roche': 'Roche',
    'Hoffmann-La Roche': 'Roche',
}

# Items that should be excluded from drug lists (not actual drugs)
NON_DRUG_ITEMS = {
    # Placebos and controls
    'placebo', 'saline', 'sodium chloride', 'normal saline', 'vehicle', 'sham',
    'control', 'comparator', 'standard of care', 'soc', 'usual care',
    # Diagnostic agents (not treatments)
    'fdg', '18f-fdg', 'fluorodeoxyglucose', 'contrast', 'tracer',
    # Generic terms and regimens
    'basic treatment', 'conventional treatment', 'standard treatment',
    'best supportive care', 'supportive care', 'active comparator',
    'experimental', 'intervention', 'treatment', 'therapy', 'drug',
    'regimen', 'protocol', 'standard regimen', 'standard protocol',
    'standard lymphodepletion regimen', 'lymphodepletion regimen',
    'conditioning regimen', 'chemotherapy regimen',
    # Vehicles/diluents
    'dextrose', '5% dextrose', 'water for injection', 'sterile water',
    'bacteriostatic water', 'diluent',
    # Residual noise words from parsing
    'per', 'mg', 'ml', 'mcg', 'unit', 'units',
    # Generic drug class names (too vague)
    'corticosteroids', 'steroids', 'nsaids', 'antibiotics',
}

# Combination splitters - patterns that indicate multiple drugs
COMBINATION_PATTERNS = [
    r'\s+and\s+',           # "Drug A and Drug B"
    r'\s*\+\s*',            # "Drug A + Drug B"
    r'\s*/\s*',             # "Drug A / Drug B"
    r'\s+or\s+',            # "Drug A or Drug B"
    r'\s+with\s+',          # "Drug A with Drug B"
    r'\s+plus\s+',          # "Drug A plus Drug B"
    r',\s*',                # "Drug A, Drug B" or "Drug A,Drug B"
]

# Dosage/formulation terms to strip for display
DISPLAY_STRIP_TERMS = [
    # Multi-word phrases first (order matters)
    'injectable product', 'subcutaneous injection', 'intravenous injection',
    'intramuscular injection', 'oral solution', 'oral suspension',
    'oral tablet', 'oral capsule', 'ophthalmic solution', 'nasal spray',
    'calming cream', 'calming lotion',  # Product names
    'for injection', 'for infusion', 'for inhalation',
    'extended release', 'extended-release', 'controlled release',
    'immediate release', 'sustained release', 'delayed release',
    'film-coated', 'film coated', 'enteric coated',
    'prefilled syringe', 'pre-filled syringe', 'autoinjector', 'auto-injector',
    'high dose', 'low dose', 'standard dose', 'loading dose',
    'dose reduction', 'dose escalation', 'dose titration',
    'per 5 mg', 'per mg',
    'iv steroids', 'iv steroid',
    # Dosing schedules
    'q2w', 'q4w', 'qw', 'qd', 'bid', 'tid', 'qid',
    'once weekly', 'twice weekly', 'every 2 weeks', 'every 4 weeks',
    'once daily', 'twice daily', 'three times daily',
    # Single words/short terms
    'injection', 'injectable', 'infusion', 'inhalation',
    'tablets', 'tablet', 'capsules', 'capsule', 'pills', 'pill',
    'solution', 'suspension', 'powder', 'cream', 'ointment', 'gel', 'lotion', 'patch',
    'oral', 'topical', 'nasal', 'ophthalmic', 'otic',
    'iv', 'sc', 'im', 'po', 'sq',
    'subcutaneous', 'intravenous', 'intramuscular', 'intradermal',
    'product', 'formulation', 'preparation', 'concentrate',
    'syringe', 'pen', 'vial', 'ampule', 'ampoule',
    'dose 1', 'dose 2', 'dose 3',
    'discontinuation', 'continuation', 'maintenance',
    'dose', 'dosing',
    'administration', 'administered',
]

# Known drug name mappings (clinical trial name -> FDA generic/brand name)
# This handles cases where normalization alone isn't sufficient
DRUG_NAME_MAPPINGS = {
    'anti-cd20': 'rituximab',
    'anti-cd19': 'blinatumomab',
    'anti-il6': 'tocilizumab',
    'anti-tnf': 'adalimumab',  # Could be multiple, default to most common
    'jak inhibitor': 'tofacitinib',  # Default JAK inhibitor
    'btk inhibitor': 'ibrutinib',  # Default BTK inhibitor
    'glp-1': 'glucagon-like peptide-1',
    'glp1': 'glucagon-like peptide-1',
    'incretin-based therapy': 'semaglutide',  # Common trial term
    'lng-iud': 'levonorgestrel',
    'sglt2 inhibitor': 'dapagliflozin',  # Class -> example
    'dpp-4 inhibitor': 'sitagliptin',  # Class -> example
}

# Sponsor type classification keywords (dict format for backwards compatibility)
SPONSOR_TYPE_KEYWORDS = {
    'academic': [
        'university', 'université', 'universität', 'universidad', 'universidade',
        'universiteit', 'università', 'universitetet', 'college', 'school of',
        'institute', 'institut', 'hospital', 'hôpital', 'clinic', 'clinique',
        'medical center', 'centre hospitalier', 'health system', 'health center',
        'research center', 'research foundation', 'academy', 'foundation',
        'trust', 'nhs', 'va ', 'veterans', 'department of', 'ministry',
        'assistance publique', 'ap-hp', 'inserm', 'cnrs', 'nih', 'nci',
        'consortium', 'network', 'alliance', 'cooperative group', 'study group',
    ],
    'government': [
        'national institutes', 'national cancer institute', 'national institute',
        'centers for disease', 'cdc', 'fda', 'nih', 'nci', 'nhlbi', 'niaid',
        'department of defense', 'department of veterans', 'army', 'navy',
        'air force', 'military', 'government', 'federal', 'state of',
        'ministry', 'public health', 'health canada', 'ema', 'mhra',
        'national health service', 'nhs',
    ],
}

# Sponsor type classification keywords (separate lists - used by classify_sponsor_type)
INDUSTRY_KEYWORDS = [
    'pharma', 'therapeutics', 'biotech', 'biosciences', 'biopharma',
    'laboratories', 'labs', 'inc.', 'inc', 'ltd', 'ltd.', 'llc', 'corp',
    'corporation', 'gmbh', 's.a.', 'plc', 'ag', 'co.', 'company',
    'holdings', 'sciences', 'healthcare', 'medical', 'oncology',
    'pharmaceuticals', 'biopharmaceuticals', 'drugs', 'medicines'
]

ACADEMIC_KEYWORDS = [
    'university', 'college', 'hospital', 'medical center', 'medical centre',
    'clinic', 'institute', 'school of medicine', 'health system',
    'research center', 'research centre', 'foundation', 'trust',
    'academy', 'centre hospitalier', 'hopital', 'klinik', 'universitä',
    'faculty', 'department of'
]

GOVERNMENT_KEYWORDS = [
    'nih', 'national institutes', 'national institute', 'cdc', 'fda',
    'va ', 'veterans', 'department of health', 'ministry', 'government',
    'national cancer institute', 'nci', 'national heart', 'nhlbi',
    'national eye', 'nei', 'niaid', 'nimh', 'public health'
]

# Major pharma companies (for accurate industry classification)
# List format used by classify_sponsor_type
MAJOR_PHARMA = [
    'pfizer', 'novartis', 'roche', 'merck', 'johnson & johnson', 'j&j',
    'abbvie', 'eli lilly', 'lilly', 'bristol myers', 'bms', 'astrazeneca',
    'sanofi', 'glaxosmithkline', 'gsk', 'gilead', 'amgen', 'regeneron',
    'biogen', 'vertex', 'moderna', 'biontech', 'novo nordisk', 'takeda',
    'boehringer', 'bayer', 'astellas', 'daiichi', 'eisai', 'otsuka',
    'teva', 'allergan', 'celgene', 'alexion', 'incyte', 'seagen',
    'jazz', 'biomarin', 'bluebird', 'alnylam', 'argenx', 'horizon'
]

# INN suffixes (Greek letters used for biologics)
# e.g., "efgartigimod alfa" -> "efgartigimod"
INN_SUFFIXES = [
    ' alfa', ' beta', ' gamma', ' delta', ' epsilon', ' zeta', ' eta', ' theta',
    ' pegol', ' vedotin', ' emtansine', ' mertansine', ' ozogamicin',
    ' sudotox', ' tansine',
]

# Salt suffixes for drug name normalization
SALT_SUFFIXES = [
    'hydrochloride', 'sodium', 'calcium', 'potassium', 'sulfate',
    'acetate', 'maleate', 'tartrate', 'citrate', 'phosphate',
    'carbonate', 'mesylate', 'besylate', 'dihydrochloride', 'fumarate',
]

# Formulation suffixes for drug name normalization
FORMULATION_SUFFIXES = [
    'subcutaneous injection', 'subcutaneous', 'intramuscular injection',
    'intramuscular', 'intravenous injection', 'intravenous', 'injection',
    'injectable product', 'injectable', 'oral solution', 'oral tablet',
    'oral capsule', 'oral', 'topical', 'ophthalmic', 'nasal', 'transdermal',
]

# Formulation terms for normalize_drug_name function
FORMULATION_TERMS = [
    # Multi-word phrases first
    'injectable product', 'subcutaneous injection', 'oral solution',
    'oral suspension', 'oral tablet', 'oral capsule', 'oral pill',
    'extended release', 'extended-release', 'controlled release',
    'immediate release', 'delayed release', 'sustained release',
    'film-coated', 'film coated', 'enteric coated',
    'for injection', 'for infusion', 'for inhalation',
    'once weekly', 'once daily', 'twice daily',
    'prefilled syringe', 'pre-filled syringe', 'autoinjector',
    'intravenous infusion', 'intravenous injection',
    'subcutaneous infusion', 'intramuscular injection',
    'reference formulation', 'test formulation',
    'open label', 'blinded',
    # Single words
    'injection', 'injectable', 'tablets?', 'capsules?', 'solution',
    'suspension', 'powder', 'cream', 'ointment', 'gel', 'patch',
    'oral', 'iv', 'sc', 'im', 'subcutaneous', 'intravenous', 'intramuscular',
    'er', 'sr', 'xr', 'xl', 'cr', 'dr', 'ir',
    'coated', 'enteric',
    'product', 'formulation', 'preparation', 'concentrate',
    'infusion', 'inhalation', 'nebulizer',
    'prefilled', 'pre-filled', 'syringe', 'pen', 'vial', 'ampule',
    'bid', 'qd', 'qw', 'tid', 'qid',
    # Salt forms
    'hcl', 'hydrochloride', 'acetate', 'succinate', 'fumarate', 'maleate',
    'sodium', 'potassium', 'calcium', 'phosphate', 'sulfate', 'citrate',
    'mesylate', 'besylate', 'tartrate', 'tosylate', 'malate', 'pamoate',
    'lactate', 'gluconate', 'carbonate', 'bicarbonate',
]
