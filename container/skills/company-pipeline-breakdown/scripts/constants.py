"""Constants used throughout the company drug pipeline breakdown skill.

Design principles:
- Therapeutic area classification: REMOVED from here — handled by MeSH D-code lookup
  + keyword-stem fallback in therapeutic_area_mapping.py
- Company aliases: Only non-obvious mappings (abbreviations, former names, divisions).
  Legal suffix variations (Inc., Ltd., PLC) handled dynamically by _strip_legal_suffixes().
- Drug name filtering: Pattern-based via compiled regexes instead of enumerated lists.
"""

import re

# =============================================================================
# COMPANY NAME ALIASES (slimmed — legal suffixes handled dynamically)
# =============================================================================
# Only entries where the alias is NOT discoverable by stripping legal suffixes.
# e.g., "Pfizer Inc." → "Pfizer" is handled by _strip_legal_suffixes(),
# but "BMS" → "Bristol Myers Squibb" requires an explicit mapping.

COMPANY_ALIASES = {
    'Eli Lilly': ['Eli Lilly', 'Lilly'],
    'Bristol Myers Squibb': ['Bristol Myers Squibb', 'Bristol-Myers Squibb', 'BMS'],
    'Johnson & Johnson': ['Johnson & Johnson', 'Johnson and Johnson', 'J&J',
                          'Janssen', 'Janssen Pharmaceuticals',
                          'Janssen Research & Development'],
    'Merck': ['Merck', 'MSD', 'Merck Sharp & Dohme', 'Merck & Co.'],
    'GSK': ['GSK', 'GlaxoSmithKline', 'Glaxo SmithKline', 'Glaxo'],
    'Gilead Sciences': ['Gilead Sciences', 'Gilead'],
    'Roche': ['Roche', 'F. Hoffmann-La Roche', 'Hoffmann-La Roche'],
    'Sanofi': ['Sanofi', 'Sanofi-Aventis'],
    'Biogen': ['Biogen', 'Biogen Idec'],
    'Moderna': ['Moderna', 'ModernaTX'],
    'Becton Dickinson': ['Becton Dickinson', 'BD'],
}

# =============================================================================
# KNOWN SUBSIDIARIES (M&A)
# =============================================================================
# Maps parent company -> subsidiaries whose CT.gov sponsor name differs from parent.
# Only includes subsidiaries that actively sponsor trials under their own name.
# NOTE: CT.gov MCP's collaborator parameter is broken (silently dropped),
# so dynamic discovery is not possible. This curated list is the reliable alternative.

KNOWN_SUBSIDIARIES = {
    'Bristol Myers Squibb': ['Celgene', 'Mirati Therapeutics', 'Karuna Therapeutics',
                             'RayzeBio', 'Turning Point Therapeutics'],
    'Roche': ['Genentech'],
    'AbbVie': ['Allergan', 'Pharmacyclics'],
    'Johnson & Johnson': ['Janssen', 'Actelion'],
    'Pfizer': ['Seagen', 'Array BioPharma', 'Arena Pharmaceuticals', 'Global Blood Therapeutics'],
    'Sanofi': ['Genzyme', 'Regeneron'],
    'AstraZeneca': ['Alexion', 'MedImmune'],
    'Merck': ['Organon'],
    'Amgen': ['Horizon Therapeutics'],
    'Gilead Sciences': ['Kite Pharma', 'Immunomedics'],
    'Takeda': ['Shire'],
    'Novartis': ['Sandoz', 'AveXis'],
    'Bayer': ['Asklepios BioPharmaceutical'],
    'Daiichi Sankyo': ['Plexxikon'],
    'Eli Lilly': ['Loxo Oncology'],
}

# =============================================================================
# MAJOR PHARMA / MEDTECH (for sponsor type classification)
# =============================================================================
# Substring stems — matched with word-boundary or contains logic.

MAJOR_PHARMA = [
    'pfizer', 'novartis', 'roche', 'merck', 'johnson & johnson', 'j&j', 'janssen',
    'abbvie', 'eli lilly', 'lilly', 'bristol myers', 'bms', 'astrazeneca',
    'sanofi', 'glaxosmithkline', 'gsk', 'gilead', 'amgen', 'regeneron',
    'biogen', 'vertex', 'moderna', 'biontech', 'novo nordisk', 'takeda',
    'boehringer', 'bayer', 'astellas', 'daiichi', 'eisai', 'otsuka',
    'teva', 'allergan', 'celgene', 'alexion', 'incyte', 'seagen',
    'jazz', 'biomarin', 'bluebird', 'alnylam', 'argenx', 'horizon',
    'genentech', 'kite', 'pharmacyclics', 'ultragenyx', 'ionis',
    'exelixis', 'nektar', 'iovance', 'blueprint', 'revolution', 'relay',
    'arcus', 'syndax', 'turning point', 'mirati', 'array', 'immunomedics',
]

MAJOR_MEDTECH = [
    'abbott', 'medtronic', 'boston scientific', 'stryker', 'edwards lifesciences',
    'zimmer biomet', 'intuitive surgical', 'dexcom', 'becton dickinson', 'bd',
    'baxter', 'philips', 'ge healthcare', 'siemens healthineers', 'smith & nephew',
]

# =============================================================================
# SPONSOR TYPE CLASSIFICATION
# =============================================================================

INDUSTRY_KEYWORDS = [
    'pharma', 'therapeutics', 'biotech', 'biosciences', 'biopharma',
    'laboratories', 'labs', 'inc.', 'inc', 'ltd', 'ltd.', 'llc', 'corp',
    'corporation', 'gmbh', 's.a.', 'plc', 'ag', 'co.', 'company',
    'holdings', 'sciences', 'healthcare', 'medical', 'oncology',
    'pharmaceuticals', 'biopharmaceuticals', 'drugs', 'medicines'
]

ACADEMIC_KEYWORDS = [
    'university', 'college', 'hospital', 'medical center', 'medical centre',
    'cancer center', 'cancer centre', 'heart center', 'heart centre',
    'clinic', 'institute', 'school of medicine', 'health system',
    'research center', 'research centre', 'foundation', 'trust',
    'academy', 'centre hospitalier', 'hopital', 'klinik', 'universita',
    'ospedaliero', 'ospedale', 'hopital', 'krankenhaus', 'ziekenhuis',
    'faculty', 'department of', 'irccs', 'assistance publique',
]

GOVERNMENT_KEYWORDS = [
    'nih', 'national institutes', 'national institute', 'cdc', 'fda',
    'va ', 'veterans', 'department of health', 'ministry', 'government',
    'national cancer institute', 'nci', 'national heart', 'nhlbi',
    'national eye', 'nei', 'niaid', 'nimh', 'public health',
    'national center for', 'national centre for',
]

# =============================================================================
# DRUG NAME HANDLING — Pattern-based (replaces enumerated lists)
# =============================================================================

# --- Non-drug detection ---
# Small exact-match set for very short/ambiguous terms
_NON_DRUG_EXACT = {
    'placebo', 'sham', 'vehicle', 'control', 'comparator', 'saline',
    'fdg', 'contrast', 'tracer', 'diluent', 'dextrose', 'glucose',
    'per', 'mg', 'ml', 'mcg', 'unit', 'units', 'soc',
    'standard of care',
    'experimental', 'intervention', 'treatment', 'therapy', 'drug',
    'regimen', 'protocol', 'radiation', 'radiotherapy', 'chemotherapy',
    'plasma', 'serum', 'ivig', 'prp', 'nsaids',
}

# Pattern-based non-drug detection (replaces 39-line NON_DRUG_ITEMS set)
_NON_DRUG_PATTERN = re.compile(r'''(?xi)
    # Controls and standard care
    ^(?:placebo|sham|control|vehicle|saline|comparator)\b
    | ^(?:standard|usual|best\s+supportive|conventional|basic|active)\s+
      (?:care|treatment|therapy|comparator)$
    | ^standard\s+(?:regimen|protocol)$
    # Injectable diluents
    | ^(?:normal\s+saline|sodium\s+chloride|sterile\s+water
        |water\s+for\s+injection|bacteriostatic\s+water|5%\s+dextrose)$
    # Drug class names (singular and plural via s?)
    | ^(?:anti(?:biotic|viral|fungal|microbial|septic|convulsant|depressant
        |psychotic|hypertensive|coagulant|emetic|pyretic))s?$
    | ^(?:corticosteroid|steroid|opioid|narcotic|biologic
        |bronchodilator|stimulant|sedative|analgesic
        |diuretic|laxative|vasodilator
        |immunosuppressant|immunosuppressive|immunoglobulin)s?$
    | ^muscle\s+relaxants?$
    # Biological materials
    | ^(?:amniotic\s+(?:fluid|membrane)|platelet\s+rich\s+plasma
        |bone\s+marrow|stem\s+cells?|blood\s+transfusion
        |red\s+blood\s+cells?|whole\s+blood)$
    # Supplements
    | ^(?:vitamin|mineral|supplement|probiotic|prebiotic|electrolyte)s?$
    | ^(?:fluorodeoxyglucose|18f-fdg)$
''')


def is_non_drug_item(name: str) -> bool:
    """Check if a name refers to a non-drug item (placebo, drug class, etc.).

    Uses compiled regex patterns instead of an enumerated set —
    automatically handles singular/plural and common phrase patterns.
    """
    if not name:
        return True
    name_lower = name.lower().strip()
    if name_lower in _NON_DRUG_EXACT:
        return True
    return bool(_NON_DRUG_PATTERN.search(name_lower))


# --- Formulation stripping ---
# Unified pattern replacing both DISPLAY_STRIP_TERMS (28 lines) and
# FORMULATION_TERMS (24 lines), which were ~70% duplicated.

_FORMULATION_PATTERN = re.compile(r'''(?xi)
    \b(?:
        # Routes of administration
        oral|topical|nasal|ophthalmic|otic
        |subcutaneous|intravenous|intramuscular|intradermal
        |iv|sc|im|po|sq
        # Dosage forms (handles plural via s?)
        |tablets?|capsules?|pills?|solutions?|suspensions?
        |powders?|creams?|ointments?|gels?|lotions?|patch(?:es)?
        |injections?|injectables?|infusions?|inhalations?|nebulizers?
        # Combined route+form phrases
        |(?:subcutaneous|intravenous|intramuscular|oral)\s+
         (?:injection|solution|suspension|tablet|capsule|pill|infusion)
        |injectable\s+product|nasal\s+spray|ophthalmic\s+solution
        |for\s+(?:injection|infusion|inhalation)
        # Delivery devices
        |(?:pre-?filled\s+)?syringes?|pens?|vials?|ampou?les?
        |auto-?injectors?
        # Release modifiers
        |(?:extended|controlled|immediate|sustained|delayed)[\s-]releases?
        |(?:film|enteric)[\s-]coated|coated|enteric
        # Release abbreviations
        |er|sr|xr|xl|cr|dr|ir
        # Dosing frequency
        |q\d*w|qd|bid|tid|qid
        |(?:once|twice|three\s+times)\s+(?:daily|weekly)
        |every\s+\d+\s+weeks?
        # Dose descriptors
        |(?:high|low|standard|loading|higher|lower)\s+dose
        |microgram|milligram|micrograms|milligrams
        # Generic terms
        |products?|formulations?|preparations?|concentrates?
        |administrations?|administered|dos(?:e|ing)
        |monotherapy|treatment(?:\s+of)?|only\s+treatment
        |recombinant|variant-adapted
        # Salt forms
        |hcl|hydrochloride|acetate|succinate|fumarate|maleate
        |sodium|potassium|calcium|phosphate|sulfate|citrate
        |mesylate|besylate|tartrate|tosylate|malate|pamoate
    )\b
''')


def strip_formulation_terms(name: str) -> str:
    """Strip formulation/route/dosage terms from a drug name.

    Replaces both DISPLAY_STRIP_TERMS and FORMULATION_TERMS with a single
    compiled regex — faster (one pass) and auto-handles plurals.
    """
    if not name:
        return ""
    result = _FORMULATION_PATTERN.sub('', name)
    # Clean up whitespace
    return re.sub(r'\s+', ' ', result).strip()
