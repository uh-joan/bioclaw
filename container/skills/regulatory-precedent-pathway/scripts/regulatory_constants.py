"""
Constants and configuration for regulatory precedent & pathway analysis.
"""

# ============================================================================
# Submission Pathways by Region
# ============================================================================

US_PATHWAYS = {
    "NDA": {
        "full_name": "New Drug Application (NDA)",
        "code": "NDA",
        "applies_to": ["small molecule"],
        "description": "Standard pathway for new small molecule drugs with full clinical data package.",
        "typical_review_months": 10,
        "priority_review_months": 6,
    },
    "BLA": {
        "full_name": "Biologics License Application (BLA)",
        "code": "BLA",
        "applies_to": ["biologic", "antibody", "gene therapy", "cell therapy", "vaccine", "peptide", "oligonucleotide"],
        "description": "Required for biological products. Full clinical data package.",
        "typical_review_months": 10,
        "priority_review_months": 6,
    },
    "505(b)(2)": {
        "full_name": "505(b)(2) NDA",
        "code": "505(b)(2)",
        "applies_to": ["small molecule"],
        "description": "Relies partially on FDA's prior findings for a previously approved drug. Faster if leveraging existing data.",
        "typical_review_months": 10,
        "priority_review_months": 6,
    },
}

EU_PATHWAYS = {
    "Centralized": {
        "full_name": "Centralized Marketing Authorization (EMA)",
        "code": "Centralized",
        "mandatory_for": ["biologic", "orphan", "HIV", "cancer", "diabetes", "neurodegenerative", "autoimmune", "gene therapy", "cell therapy"],
        "description": "Single application to EMA, valid in all EU member states. Mandatory for certain product types.",
        "typical_review_months": 15,
        "accelerated_months": 10,
    },
    "Decentralized": {
        "full_name": "Decentralized Procedure (DCP)",
        "code": "Decentralized",
        "applies_to": ["small molecule"],
        "description": "Simultaneous application to multiple EU member states. Reference member state leads assessment.",
        "typical_review_months": 12,
    },
    "National": {
        "full_name": "National Authorization",
        "code": "National",
        "applies_to": ["small molecule"],
        "description": "Single member state authorization. Limited use for novel drugs.",
        "typical_review_months": 10,
    },
    "Conditional": {
        "full_name": "Conditional Marketing Authorization",
        "code": "Conditional",
        "applies_to": ["all"],
        "description": "For drugs addressing unmet medical need with less comprehensive data. Requires annual renewal.",
        "typical_review_months": 10,
    },
}


# ============================================================================
# Regulatory Designations
# ============================================================================

DESIGNATIONS = {
    "breakthrough_therapy": {
        "region": "US",
        "full_name": "Breakthrough Therapy Designation",
        "agency": "FDA",
        "criteria": "Substantial improvement over existing therapies for serious conditions",
        "benefits": "Intensive FDA guidance, rolling review, organizational commitment",
    },
    "fast_track": {
        "region": "US",
        "full_name": "Fast Track Designation",
        "agency": "FDA",
        "criteria": "Treats serious condition and fills unmet medical need",
        "benefits": "More frequent FDA meetings, rolling review eligibility",
    },
    "orphan_drug": {
        "region": "US",
        "full_name": "Orphan Drug Designation",
        "agency": "FDA",
        "criteria": "Disease affects <200,000 people in the US",
        "benefits": "7-year market exclusivity, tax credits, reduced filing fees",
        "prevalence_threshold": 200000,
    },
    "priority_review": {
        "region": "US",
        "full_name": "Priority Review",
        "agency": "FDA",
        "criteria": "Significant improvement in safety or effectiveness",
        "benefits": "6-month review (vs 10-month standard)",
    },
    "accelerated_approval": {
        "region": "US",
        "full_name": "Accelerated Approval",
        "agency": "FDA",
        "criteria": "Serious condition with unmet need; surrogate endpoint reasonably likely to predict clinical benefit",
        "benefits": "Earlier approval based on surrogate endpoint; confirmatory trial required",
    },
    "prime": {
        "region": "EU",
        "full_name": "PRIME (PRIority MEdicines)",
        "agency": "EMA",
        "criteria": "Targets unmet medical need with preliminary clinical evidence of major therapeutic advantage",
        "benefits": "Early and enhanced dialogue with EMA, accelerated assessment eligibility",
    },
    "orphan_eu": {
        "region": "EU",
        "full_name": "Orphan Designation (EU)",
        "agency": "EMA",
        "criteria": "Disease affects <5 in 10,000 in EU (approx <228,000)",
        "benefits": "10-year market exclusivity, protocol assistance, fee reductions",
        "prevalence_threshold_per_10k": 5,
    },
    "conditional_ma": {
        "region": "EU",
        "full_name": "Conditional Marketing Authorization",
        "agency": "EMA",
        "criteria": "Unmet medical need, positive benefit-risk on less comprehensive data",
        "benefits": "Earlier market access; annual renewal with additional data",
    },
}


# ============================================================================
# Modality Classification
# ============================================================================

MODALITY_KEYWORDS = {
    "small molecule": ["tablet", "capsule", "oral", "small molecule", "chemical entity"],
    "biologic": ["biologic", "biological", "recombinant", "fusion protein"],
    "antibody": ["antibody", "monoclonal", "mab", "bispecific", "adc", "antibody-drug conjugate"],
    "gene therapy": ["gene therapy", "aav", "adeno-associated", "lentiviral", "gene transfer"],
    "cell therapy": ["cell therapy", "car-t", "car t", "stem cell", "adoptive cell"],
    "peptide": ["peptide", "glp-1", "incretin"],
    "vaccine": ["vaccine", "mrna", "immunization"],
    "oligonucleotide": ["antisense", "sirna", "mirna", "oligonucleotide", "aso"],
}


# ============================================================================
# Pediatric Obligation Rules
# ============================================================================

PEDIATRIC_RULES = {
    "US_PREA": {
        "full_name": "Pediatric Research Equity Act",
        "default": "required",
        "waiver_conditions": [
            "Disease does not occur in pediatric population",
            "Studies are impossible or highly impractical",
            "No meaningful therapeutic benefit expected",
            "Orphan drug (partial exemption)",
        ],
        "deferral_conditions": [
            "Adult studies must be completed first",
            "Pediatric formulation not yet available",
        ],
    },
    "EU_PIP": {
        "full_name": "Paediatric Investigation Plan",
        "default": "required",
        "waiver_conditions": [
            "Disease does not occur in children",
            "Product is unsafe or ineffective in children",
            "No significant therapeutic benefit over existing treatments",
        ],
        "deferral_conditions": [
            "Appropriate to conduct pediatric studies after adult authorization",
            "Pediatric formulation development ongoing",
        ],
    },
}


# ============================================================================
# FDA Application Type Codes
# ============================================================================

FDA_APPLICATION_TYPES = {
    "NDA": "New Drug Application",
    "BLA": "Biologic License Application",
    "ANDA": "Abbreviated New Drug Application",
    "NDA-505(b)(2)": "505(b)(2) Application",
}


# ============================================================================
# Visualization Constants
# ============================================================================

ASCII_TABLE_WIDTH = 100
ASCII_BAR_WIDTH = 25
REPORT_SEPARATOR = "=" * ASCII_TABLE_WIDTH
SECTION_SEPARATOR = "-" * ASCII_TABLE_WIDTH


# ============================================================================
# Defaults
# ============================================================================

DEFAULT_REGIONS = ["US", "EU"]
DEFAULT_MAX_PRECEDENTS = 30
DEFAULT_MAX_TRIALS = 20
NO_PRECEDENT_THRESHOLD = 2  # If fewer than this many approved drugs, switch to no-precedent mode
