"""Constants for real-world utilization analysis.

Contains specialty mappings, state codes, and drug name normalization data.
"""
from typing import Optional

# =============================================================================
# US State Codes and Names
# =============================================================================

US_STATES = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District of Columbia",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}

# States with Medicaid formulary data available
MEDICAID_FORMULARY_STATES = ["CA", "NY", "TX", "OH", "IL"]

# Top states by population (for prioritized queries)
TOP_STATES_BY_POPULATION = [
    "CA", "TX", "FL", "NY", "PA", "IL", "OH", "GA", "NC", "MI",
    "NJ", "VA", "WA", "AZ", "MA", "TN", "IN", "MO", "MD", "WI"
]


# =============================================================================
# Prescriber Specialty Mappings
# =============================================================================

# Normalize specialty names from Medicare data
SPECIALTY_NORMALIZATION = {
    # Family Practice variations
    "Family Practice": "Family Practice",
    "Family Medicine": "Family Practice",
    "General Practice": "Family Practice",

    # Internal Medicine variations
    "Internal Medicine": "Internal Medicine",
    "General Internal Medicine": "Internal Medicine",

    # Endocrinology
    "Endocrinology": "Endocrinology",
    "Endocrinology, Diabetes & Metabolism": "Endocrinology",
    "Diabetes & Metabolism": "Endocrinology",

    # Nurse Practitioners
    "Nurse Practitioner": "Nurse Practitioner",
    "Certified Nurse Practitioner": "Nurse Practitioner",
    "Family Nurse Practitioner": "Nurse Practitioner",
    "Adult Nurse Practitioner": "Nurse Practitioner",

    # Physician Assistants
    "Physician Assistant": "Physician Assistant",
    "PA": "Physician Assistant",

    # Obesity Medicine
    "Obesity Medicine": "Obesity Medicine",
    "Bariatric Medicine": "Obesity Medicine",

    # Cardiology
    "Cardiology": "Cardiology",
    "Cardiovascular Disease": "Cardiology",

    # Gastroenterology
    "Gastroenterology": "Gastroenterology",
    "GI": "Gastroenterology",

    # Other common specialties
    "Geriatric Medicine": "Geriatric Medicine",
    "Pediatrics": "Pediatrics",
    "Psychiatry": "Psychiatry",
    "Nephrology": "Nephrology",
    "Rheumatology": "Rheumatology",
    "Pulmonology": "Pulmonology",
    "Pulmonary Disease": "Pulmonology",
}

# Specialties most relevant for obesity/diabetes drugs
RELEVANT_SPECIALTIES = [
    "Family Practice",
    "Internal Medicine",
    "Endocrinology",
    "Nurse Practitioner",
    "Physician Assistant",
    "Obesity Medicine",
    "Cardiology",
    "Gastroenterology",
    "Geriatric Medicine",
]


# =============================================================================
# Drug Name Mappings
# =============================================================================

# Brand to generic mappings for common drugs
BRAND_TO_GENERIC = {
    # GLP-1 agonists
    "ozempic": "semaglutide",
    "wegovy": "semaglutide",
    "rybelsus": "semaglutide",
    "mounjaro": "tirzepatide",
    "zepbound": "tirzepatide",
    "victoza": "liraglutide",
    "saxenda": "liraglutide",
    "trulicity": "dulaglutide",
    "byetta": "exenatide",
    "bydureon": "exenatide",

    # Other common drugs
    "metformin": "metformin",
    "glucophage": "metformin",
    "januvia": "sitagliptin",
    "jardiance": "empagliflozin",
    "farxiga": "dapagliflozin",
    "invokana": "canagliflozin",
}

# Generic to brand mappings (primary brand)
GENERIC_TO_BRAND = {
    "semaglutide": ["Ozempic", "Wegovy", "Rybelsus"],
    "tirzepatide": ["Mounjaro", "Zepbound"],
    "liraglutide": ["Victoza", "Saxenda"],
    "dulaglutide": ["Trulicity"],
    "exenatide": ["Byetta", "Bydureon"],
    "metformin": ["Glucophage"],
    "sitagliptin": ["Januvia"],
    "empagliflozin": ["Jardiance"],
    "dapagliflozin": ["Farxiga"],
    "canagliflozin": ["Invokana"],
}


# =============================================================================
# Competitive Sets for Switching Analysis
# =============================================================================

COMPETITIVE_SETS = {
    "glp1_agonists": {
        "name": "GLP-1 Receptor Agonists",
        "therapeutic_class": "Incretin Mimetics",
        "indications": ["Type 2 Diabetes", "Obesity", "Weight Management"],
        "drugs": [
            # Brand name is key for Medicare spending API
            {"brand": "Ozempic", "generic": "semaglutide", "form": "injectable", "frequency": "weekly"},
            {"brand": "Wegovy", "generic": "semaglutide", "form": "injectable", "frequency": "weekly", "indication": "obesity"},
            {"brand": "Rybelsus", "generic": "semaglutide", "form": "oral", "frequency": "daily"},
            {"brand": "Mounjaro", "generic": "tirzepatide", "form": "injectable", "frequency": "weekly"},
            {"brand": "Zepbound", "generic": "tirzepatide", "form": "injectable", "frequency": "weekly", "indication": "obesity"},
            {"brand": "Trulicity", "generic": "dulaglutide", "form": "injectable", "frequency": "weekly"},
            {"brand": "Victoza", "generic": "liraglutide", "form": "injectable", "frequency": "daily"},
            {"brand": "Saxenda", "generic": "liraglutide", "form": "injectable", "frequency": "daily", "indication": "obesity"},
            {"brand": "Byetta", "generic": "exenatide", "form": "injectable", "frequency": "twice daily"},
            {"brand": "Bydureon", "generic": "exenatide", "form": "injectable", "frequency": "weekly"},
        ],
        "market_entry_years": {
            "Byetta": 2005,
            "Victoza": 2010,
            "Bydureon": 2012,
            "Trulicity": 2014,
            "Saxenda": 2014,
            "Ozempic": 2017,
            "Rybelsus": 2019,
            "Wegovy": 2021,
            "Mounjaro": 2022,
            "Zepbound": 2023,
        },
    },
    "sglt2_inhibitors": {
        "name": "SGLT2 Inhibitors",
        "therapeutic_class": "Sodium-Glucose Co-Transporter 2 Inhibitors",
        "indications": ["Type 2 Diabetes", "Heart Failure", "Chronic Kidney Disease"],
        "drugs": [
            {"brand": "Jardiance", "generic": "empagliflozin", "form": "oral", "frequency": "daily"},
            {"brand": "Farxiga", "generic": "dapagliflozin", "form": "oral", "frequency": "daily"},
            {"brand": "Invokana", "generic": "canagliflozin", "form": "oral", "frequency": "daily"},
            {"brand": "Steglatro", "generic": "ertugliflozin", "form": "oral", "frequency": "daily"},
        ],
        "market_entry_years": {
            "Invokana": 2013,
            "Farxiga": 2014,
            "Jardiance": 2014,
            "Steglatro": 2017,
        },
    },
    "dpp4_inhibitors": {
        "name": "DPP-4 Inhibitors",
        "therapeutic_class": "Dipeptidyl Peptidase-4 Inhibitors",
        "indications": ["Type 2 Diabetes"],
        "drugs": [
            {"brand": "Januvia", "generic": "sitagliptin", "form": "oral", "frequency": "daily"},
            {"brand": "Tradjenta", "generic": "linagliptin", "form": "oral", "frequency": "daily"},
            {"brand": "Onglyza", "generic": "saxagliptin", "form": "oral", "frequency": "daily"},
            {"brand": "Nesina", "generic": "alogliptin", "form": "oral", "frequency": "daily"},
        ],
        "market_entry_years": {
            "Januvia": 2006,
            "Onglyza": 2009,
            "Tradjenta": 2011,
            "Nesina": 2013,
        },
    },
    "obesity_drugs": {
        "name": "Anti-Obesity Medications",
        "therapeutic_class": "Weight Management Agents",
        "indications": ["Obesity", "Weight Management"],
        "drugs": [
            {"brand": "Wegovy", "generic": "semaglutide", "form": "injectable", "frequency": "weekly"},
            {"brand": "Zepbound", "generic": "tirzepatide", "form": "injectable", "frequency": "weekly"},
            {"brand": "Saxenda", "generic": "liraglutide", "form": "injectable", "frequency": "daily"},
            {"brand": "Qsymia", "generic": "phentermine/topiramate", "form": "oral", "frequency": "daily"},
            {"brand": "Contrave", "generic": "naltrexone/bupropion", "form": "oral", "frequency": "twice daily"},
            {"brand": "Xenical", "generic": "orlistat", "form": "oral", "frequency": "with meals"},
        ],
        "market_entry_years": {
            "Xenical": 1999,
            "Qsymia": 2012,
            "Contrave": 2014,
            "Saxenda": 2014,
            "Wegovy": 2021,
            "Zepbound": 2023,
        },
    },
}

# Drug to competitive set mapping (for quick lookup)
DRUG_TO_COMPETITIVE_SET = {}
for set_id, set_data in COMPETITIVE_SETS.items():
    for drug in set_data["drugs"]:
        brand_lower = drug["brand"].lower()
        generic_lower = drug["generic"].lower()
        DRUG_TO_COMPETITIVE_SET[brand_lower] = set_id
        if generic_lower not in DRUG_TO_COMPETITIVE_SET:
            DRUG_TO_COMPETITIVE_SET[generic_lower] = set_id


def get_competitive_set(drug_name: str) -> Optional[dict]:
    """Get competitive set for a drug.

    Args:
        drug_name: Brand or generic drug name

    Returns:
        Competitive set dict or None if not found
    """
    name_lower = drug_name.lower().strip()

    # Try direct lookup
    set_id = DRUG_TO_COMPETITIVE_SET.get(name_lower)
    if set_id:
        return {"set_id": set_id, **COMPETITIVE_SETS[set_id]}

    # Try normalized generic lookup
    generic = normalize_drug_name(name_lower)
    set_id = DRUG_TO_COMPETITIVE_SET.get(generic)
    if set_id:
        return {"set_id": set_id, **COMPETITIVE_SETS[set_id]}

    return None


def get_competitors(drug_name: str) -> list:
    """Get list of competitor brand names for a drug.

    Args:
        drug_name: Brand or generic drug name

    Returns:
        List of competitor brand names (excluding the input drug)
    """
    comp_set = get_competitive_set(drug_name)
    if not comp_set:
        return []

    name_lower = drug_name.lower().strip()
    generic = normalize_drug_name(name_lower)

    competitors = []
    for drug in comp_set["drugs"]:
        # Skip the input drug itself
        if drug["brand"].lower() == name_lower or drug["generic"].lower() == generic:
            continue
        competitors.append(drug["brand"])

    return competitors


# =============================================================================
# Formatting Constants
# =============================================================================

# Number formatting thresholds
BILLION_THRESHOLD = 1_000_000_000
MILLION_THRESHOLD = 1_000_000
THOUSAND_THRESHOLD = 1_000


def format_currency(value: float) -> str:
    """Format currency value with appropriate suffix.

    Args:
        value: Dollar amount

    Returns:
        Formatted string (e.g., "$4.2B", "$890M", "$45K")
    """
    if value >= BILLION_THRESHOLD:
        return f"${value / BILLION_THRESHOLD:.1f}B"
    elif value >= MILLION_THRESHOLD:
        return f"${value / MILLION_THRESHOLD:.1f}M"
    elif value >= THOUSAND_THRESHOLD:
        return f"${value / THOUSAND_THRESHOLD:.1f}K"
    else:
        return f"${value:,.0f}"


def format_number(value: int) -> str:
    """Format large number with commas.

    Args:
        value: Integer value

    Returns:
        Formatted string with commas
    """
    return f"{value:,}"


def normalize_drug_name(drug_name: str) -> str:
    """Normalize drug name to generic form.

    Args:
        drug_name: Brand or generic drug name

    Returns:
        Normalized generic name (lowercase)
    """
    if not drug_name:
        return ""

    name_lower = drug_name.lower().strip()

    # Check brand to generic mapping
    if name_lower in BRAND_TO_GENERIC:
        return BRAND_TO_GENERIC[name_lower]

    return name_lower


def get_brand_names(generic_name: str) -> list:
    """Get brand names for a generic drug.

    Args:
        generic_name: Generic drug name

    Returns:
        List of brand names
    """
    name_lower = generic_name.lower().strip()
    return GENERIC_TO_BRAND.get(name_lower, [])


def normalize_specialty(specialty: str) -> str:
    """Normalize prescriber specialty name.

    Args:
        specialty: Raw specialty name from Medicare data

    Returns:
        Normalized specialty name
    """
    if not specialty:
        return "Other"

    # Check direct mapping
    if specialty in SPECIALTY_NORMALIZATION:
        return SPECIALTY_NORMALIZATION[specialty]

    # Check case-insensitive
    for key, value in SPECIALTY_NORMALIZATION.items():
        if key.lower() == specialty.lower():
            return value

    return specialty


def get_state_name(state_code: str) -> str:
    """Get full state name from abbreviation.

    Args:
        state_code: Two-letter state abbreviation

    Returns:
        Full state name or the code if not found
    """
    return US_STATES.get(state_code.upper(), state_code)
