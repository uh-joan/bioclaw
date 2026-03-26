#!/usr/bin/env python3
"""
Constants and lookup tables for company SWOT analysis.

This module contains:
- NON_DRUG_ITEMS: Set of terms that are not drugs (for filtering)
- FORMULATION_TERMS: List of drug formulation terms (for cleaning)
- CURRENCY_TO_USD_FALLBACK: Static fallback exchange rates
- COMPANY_SUFFIXES: Common company name suffixes for normalization
"""

from typing import Dict

# ============================================================================
# Drug Name Filtering Constants
# ============================================================================

NON_DRUG_ITEMS = {
    'placebo', 'saline', 'sodium chloride', 'normal saline', 'vehicle', 'sham',
    'control', 'comparator', 'standard of care', 'soc', 'usual care',
    'fdg', '18f-fdg', 'fluorodeoxyglucose', 'contrast', 'tracer',
    'best supportive care', 'supportive care', 'active comparator',
    'experimental', 'intervention', 'treatment', 'therapy', 'drug',
    'regimen', 'protocol', 'standard regimen', 'standard protocol',
    'dextrose', '5% dextrose', 'water for injection', 'sterile water',
    # Common false positives from clinical trial fields
    'patients', 'participant', 'participants', 'subject', 'subjects',
    'arm', 'group', 'cohort', 'study', 'trial', 'combination',
    'investigator', 'physician', 'care', 'screening', 'follow-up',
    'observation', 'monitoring', 'assessment', 'evaluation',
    # PK probe drugs used in DDI (drug-drug interaction) studies — not real pipeline drugs
    'midazolam', 'fexofenadine', 'digoxin', 'warfarin', 'caffeine',
    'metoprolol', 'omeprazole', 'dextromethorphan', 'tolbutamide',
    'efavirenz', 'flurbiprofen', 'repaglinide', 'rosuvastatin',
    'pitavastatin', 'pravastatin', 'furosemide', 'metformin',
    # Trial title noise words parsed as drug names
    'called', 'named', 'known', 'entitled', 'versus', 'compared',
    'evaluated', 'administered', 'combined', 'followed',
    # XBRL financial line items misidentified as drugs
    'non cash royalty', 'noncash royalty', 'royalty', 'royalties',
    'total', 'other', 'other products', 'other revenue', 'all other',
    'net revenue', 'net sales', 'gross profit', 'operating income',
    'cost of sales', 'cost of goods', 'selling general',
    'research and development', 'collaboration revenue',
    'product sales', 'product revenue', 'license revenue',
    'milestone', 'milestones', 'contract revenue',
    # Medtech / device categories from XBRL (not drugs)
    'knees', 'hips', 'spine', 'trauma', 'sports medicine',
    'surgical', 'wound closure', 'electrophysiology',
    'orthopedics', 'cardiovascular', 'neurovascular',
    'endoscopy', 'robotics', 'interventional',
    'vision care', 'contact lenses', 'surgical vision',
    'consumer health', 'consumer', 'medtech',
    # Common generic substance classes (not specific drugs)
    'bisphosphonate', 'bisphosphonates', 'corticosteroid', 'corticosteroids',
    'antibiotic', 'antibiotics', 'antiviral', 'antivirals',
    'chemotherapy', 'radiation', 'radiotherapy',
}

FORMULATION_TERMS = [
    'injectable product', 'subcutaneous injection', 'oral solution',
    'oral suspension', 'oral tablet', 'oral capsule',
    'extended release', 'extended-release', 'controlled release',
    'for injection', 'for infusion', 'for inhalation',
    'injection', 'injectable', 'tablets', 'tablet', 'capsules', 'capsule',
    'solution', 'suspension', 'powder', 'cream', 'ointment', 'gel',
    'oral', 'iv', 'sc', 'im', 'subcutaneous', 'intravenous', 'intramuscular',
    'product', 'formulation', 'preparation', 'concentrate',
    'infusion', 'inhalation',
]


# ============================================================================
# Currency Conversion Constants
# ============================================================================

# Fallback static rates (used when API is unavailable)
CURRENCY_TO_USD_FALLBACK: Dict[str, float] = {
    'USD': 1.0,
    'DKK': 0.143,   # Danish Krone (~7 DKK = 1 USD)
    'EUR': 1.08,    # Euro
    'GBP': 1.27,    # British Pound
    'CHF': 1.13,    # Swiss Franc
    'JPY': 0.0067,  # Japanese Yen (~150 JPY = 1 USD)
    'CNY': 0.14,    # Chinese Yuan
    'KRW': 0.00075, # Korean Won (~1340 KRW = 1 USD)
    'SEK': 0.095,   # Swedish Krona
    'NOK': 0.093,   # Norwegian Krone
    'AUD': 0.65,    # Australian Dollar
    'CAD': 0.74,    # Canadian Dollar
    'INR': 0.012,   # Indian Rupee
    'BRL': 0.20,    # Brazilian Real
    'MXN': 0.059,   # Mexican Peso
    'ILS': 0.27,    # Israeli Shekel
}

# For backward compatibility
CURRENCY_TO_USD = CURRENCY_TO_USD_FALLBACK

# Country to reporting currency mapping (for foreign filers)
COUNTRY_TO_CURRENCY: Dict[str, str] = {
    'Denmark': 'DKK',
    'DK': 'DKK',
    'Switzerland': 'CHF',
    'CH': 'CHF',
    'United Kingdom': 'GBP',
    'UK': 'GBP',
    'GB': 'GBP',
    'Japan': 'JPY',
    'JP': 'JPY',
    'Germany': 'EUR',
    'DE': 'EUR',
    'France': 'EUR',
    'FR': 'EUR',
    'Ireland': 'EUR',
    'IE': 'EUR',
    'Netherlands': 'EUR',
    'NL': 'EUR',
    'Belgium': 'EUR',
    'BE': 'EUR',
    'Italy': 'EUR',
    'IT': 'EUR',
    'Spain': 'EUR',
    'ES': 'EUR',
    'Sweden': 'SEK',
    'SE': 'SEK',
    'Norway': 'NOK',
    'NO': 'NOK',
    'Australia': 'AUD',
    'AU': 'AUD',
    'Canada': 'CAD',
    'CA': 'CAD',
    'China': 'CNY',
    'CN': 'CNY',
    'South Korea': 'KRW',
    'KR': 'KRW',
    'Israel': 'ILS',
    'IL': 'ILS',
    'India': 'INR',
    'IN': 'INR',
}


# ============================================================================
# Company Name Normalization Constants
# ============================================================================

COMPANY_SUFFIXES = [
    ' PHARMACEUTICALS', ' THERAPEUTICS', ' BIOSCIENCES', ' BIOPHARMA',
    ' BIOTHERAPEUTICS', ' BIOTECHNOLOGY', ' BIOTECH', ' INC', ' CORP',
    ' LLC', ' LTD', ' CO', ' SCIENCES', ' MEDICAL', ' HEALTH',
    ' INC.', ' CORP.', ' LLC.', ' LTD.', ' COMPANY', ' HOLDINGS',
    ' INTERNATIONAL', ' GROUP', ' PLC', ' LP', ' L.P.',
    # Foreign entity suffixes (critical for CureVac NV, BeiGene Ltd, etc.)
    ' N.V.', ' NV', ' N V', ' S.A.', ' SA', ' SE', ' AG', ' A/S',
    ' GMBH', ' B.V.', ' BV', ' S.P.A.', ' SPA', ' OYJ',
    ' LIMITED', ' LTD.',
]
