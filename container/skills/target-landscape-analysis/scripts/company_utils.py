"""
Company analysis utilities for competitive positioning.

Provides functions to:
- Aggregate drugs by company
- Track company pipeline depth
- Attribute acquisitions and partnerships
- Generate company competitive positioning
"""

from typing import Dict, Any, List
from collections import defaultdict


def extract_company_from_drug(drug: Dict, regulatory_data: Dict = None, trial_data: Dict = None, get_study_func=None) -> str:
    """
    Extract company name from drug data, with multiple fallbacks.

    Priority order:
    1. EMA regulatory data (has company field)
    2. FDA regulatory data (manufacturer)
    3. Trial sponsor (lead sponsor from clinical trials - requires get_study_func)
    4. "Unknown"

    Args:
        drug: Drug dict with drug_name, drugbank_id
        regulatory_data: Optional regulatory data for company attribution
        trial_data: Optional trial data dict with trials list
        get_study_func: Optional get_study function to fetch detailed trial info for sponsor

    Returns:
        Company name or "Unknown"
    """
    # Try EMA first (most complete company data)
    if regulatory_data:
        ema_status = regulatory_data.get('ema_status', {})
        company = ema_status.get('company')
        if company and company != 'Unknown' and company is not None:
            return clean_company_name(company)

        # Try FDA manufacturer
        fda_status = regulatory_data.get('fda_status', {})
        manufacturer = fda_status.get('manufacturer')
        if manufacturer and manufacturer != 'Unknown' and manufacturer is not None:
            return clean_company_name(manufacturer)

    # Try trial sponsor as fallback (requires get_study API call)
    # OPTIMIZED: Only fetch first active trial, not 3
    if trial_data and 'trials' in trial_data and get_study_func:
        # Find first active trial (recruiting or active_not_recruiting)
        active_statuses = ['recruiting', 'active_not_recruiting', 'not_yet_recruiting']

        for trial in trial_data['trials'][:10]:  # Check up to 10 to find 1 active
            nct_id = trial.get('nct_id')
            status = trial.get('status', '').lower()

            if not nct_id or status not in active_statuses:
                continue

            try:
                # Fetch detailed trial info to get sponsor
                study_data = get_study_func(nctId=nct_id)
                sponsor = extract_sponsor_from_study(study_data)

                if sponsor and sponsor not in ['Unknown', None, '']:
                    return clean_company_name(sponsor)
            except:
                continue  # Skip if API call fails, try next trial

    # Fallback to "Unknown" if no company found
    return "Unknown"


def extract_sponsor_from_study(study_data: str) -> str:
    """
    Extract lead sponsor from get_study() markdown output.

    Args:
        study_data: Markdown string from get_study()

    Returns:
        Lead sponsor name or None
    """
    import re

    if not isinstance(study_data, str):
        return None

    # Pattern: **Lead Sponsor:** Eli Lilly and Company (Industry)
    sponsor_match = re.search(r'\*\*Lead Sponsor:\*\*\s*(.+?)(?:\s*\([^)]+\))?(?:\n|$)', study_data)
    if sponsor_match:
        return sponsor_match.group(1).strip()

    return None


def clean_company_name(company: str) -> str:
    """
    Clean and standardize company names by removing common suffixes.

    Args:
        company: Raw company name

    Returns:
        Cleaned company name
    """
    if not company or company.lower() == 'unknown':
        return "Unknown"

    # Remove common suffixes
    company = company.strip()
    suffixes = [
        ' Inc.', ' Inc', ' LLC', ' Ltd.', ' Ltd', ' GmbH', ' S.A.', ' plc',
        ' (UK)', ' (US)', ' Corporation', ' Corp.', ' Corp', ' Co.', ' Co',
        ' Limited', ' Pharmaceuticals', ' Pharma'
    ]

    for suffix in suffixes:
        if company.endswith(suffix):
            company = company[:-len(suffix)].strip()
            break  # Only remove one suffix

    return company


def aggregate_by_company(
    drugs: List[Dict],
    regulatory_batch: Dict = None,
    trials_by_drug: Dict = None,
    get_study_func=None
) -> Dict[str, Any]:
    """
    Aggregate drugs by company/sponsor.

    Args:
        drugs: List of drug dicts
        regulatory_batch: Optional regulatory data for company attribution
        trials_by_drug: Optional trials data for pipeline depth
        get_study_func: Optional get_study function for fetching detailed trial info

    Returns:
        dict with company_portfolios, summary statistics
    """
    company_portfolios = defaultdict(lambda: {
        'drugs': [],
        'total_drugs': 0,
        'approved_drugs': 0,
        'investigational_drugs': 0,
        'total_trials': 0,
        'phase_distribution': defaultdict(int)
    })

    # Build regulatory lookup
    regulatory_lookup = {}
    if regulatory_batch and 'regulatory_data' in regulatory_batch:
        for reg_data in regulatory_batch['regulatory_data']:
            drug_name = reg_data.get('drug_name')
            if drug_name:
                regulatory_lookup[drug_name] = reg_data

    # Aggregate drugs by company
    for drug in drugs:
        drug_name = drug.get('drug_name', '')
        reg_data = regulatory_lookup.get(drug_name)
        trial_data = trials_by_drug.get(drug_name) if trials_by_drug else None

        company = extract_company_from_drug(drug, reg_data, trial_data, get_study_func)

        # Add drug to company portfolio
        company_portfolios[company]['drugs'].append({
            'drug_name': drug_name,
            'drugbank_id': drug.get('drugbank_id'),
            'groups': drug.get('groups', []),
            'indication': drug.get('indication', 'Not specified')
        })

        company_portfolios[company]['total_drugs'] += 1

        # Count approved vs investigational
        groups = [g.lower() for g in drug.get('groups', [])]
        if 'approved' in groups:
            company_portfolios[company]['approved_drugs'] += 1
        elif 'investigational' in groups:
            company_portfolios[company]['investigational_drugs'] += 1

        # Add trial data if available - ONLY count trials where company is lead sponsor
        if trials_by_drug and drug_name in trials_by_drug and get_study_func:
            trial_info = trials_by_drug[drug_name]

            # Filter trials: only count active trials where this company is the lead sponsor
            active_statuses = ['recruiting', 'active_not_recruiting', 'not_yet_recruiting', 'enrolling_by_invitation']

            for trial in trial_info.get('trials', []):
                nct_id = trial.get('nct_id')
                status = trial.get('status', '').lower()

                # Skip inactive trials
                if status not in active_statuses:
                    continue

                # Fetch detailed trial info to verify sponsor
                try:
                    study_data = get_study_func(nctId=nct_id)
                    trial_sponsor = extract_sponsor_from_study(study_data)

                    # Clean sponsor name for comparison
                    trial_sponsor_clean = clean_company_name(trial_sponsor) if trial_sponsor else None

                    # Only count if this company is the lead sponsor
                    if trial_sponsor_clean == company:
                        company_portfolios[company]['total_trials'] += 1
                        phase = trial.get('phase', 'Unknown')
                        company_portfolios[company]['phase_distribution'][phase] += 1
                except:
                    continue  # Skip if API call fails

    # Convert to regular dict and sort by total drugs
    company_portfolios_dict = dict(company_portfolios)

    # Sort companies by pipeline depth (total drugs + trials)
    sorted_companies = sorted(
        company_portfolios_dict.items(),
        key=lambda x: (x[1]['total_drugs'], x[1]['total_trials']),
        reverse=True
    )

    return {
        'company_portfolios': dict(sorted_companies),
        'summary': {
            'total_companies': len(company_portfolios_dict),
            'companies_with_approved': sum(
                1 for p in company_portfolios_dict.values() if p['approved_drugs'] > 0
            ),
            'companies_with_investigational': sum(
                1 for p in company_portfolios_dict.values() if p['investigational_drugs'] > 0
            )
        }
    }


def get_top_companies(company_aggregation: Dict, top_n: int = 10) -> List[Dict[str, Any]]:
    """
    Get top companies by pipeline depth.

    Args:
        company_aggregation: Output from aggregate_by_company
        top_n: Number of top companies to return

    Returns:
        List of top company portfolios
    """
    company_portfolios = company_aggregation['company_portfolios']

    top_companies = []
    for company, portfolio in list(company_portfolios.items())[:top_n]:
        top_companies.append({
            'company': company,
            'total_drugs': portfolio['total_drugs'],
            'approved': portfolio['approved_drugs'],
            'investigational': portfolio['investigational_drugs'],
            'total_trials': portfolio['total_trials'],
            'leading_phase': get_leading_phase(portfolio['phase_distribution'])
        })

    return top_companies


def get_leading_phase(phase_distribution: Dict[str, int]) -> str:
    """
    Get the most advanced phase in a company's pipeline.

    Args:
        phase_distribution: Dict of phase -> count

    Returns:
        Leading phase name
    """
    if not phase_distribution:
        return "Unknown"

    # Priority order for phases
    phase_priority = ['Phase 4', 'Phase 3', 'Phase 2', 'Phase 1', 'Early Phase 1']

    for phase in phase_priority:
        if phase_distribution.get(phase, 0) > 0:
            return phase

    return "Not Applicable"


def generate_company_summary(company_aggregation: Dict, top_n: int = 5) -> str:
    """
    Generate text summary of company competitive positioning.

    Args:
        company_aggregation: Output from aggregate_by_company
        top_n: Number of top companies to summarize

    Returns:
        Formatted text summary
    """
    top_companies = get_top_companies(company_aggregation, top_n)
    summary = company_aggregation['summary']

    lines = []
    lines.append(f"\nCOMPANY COMPETITIVE POSITIONING")
    lines.append("-" * 80)
    lines.append(f"Total Companies: {summary['total_companies']}")
    lines.append(f"Companies with Approved Drugs: {summary['companies_with_approved']}")
    lines.append(f"Companies with Investigational Drugs: {summary['companies_with_investigational']}")
    lines.append("")
    lines.append(f"TOP {top_n} COMPANIES BY PIPELINE DEPTH:")
    lines.append("-" * 80)

    for i, company_info in enumerate(top_companies, 1):
        company = company_info['company']
        lines.append(
            f"{i}. {company:<30} "
            f"Drugs: {company_info['total_drugs']:<3} "
            f"Approved: {company_info['approved']:<3} "
            f"Trials: {company_info['total_trials']:<4} "
            f"Leading: {company_info['leading_phase']}"
        )

    return "\n".join(lines)


def classify_by_development_stage(company_aggregation: Dict) -> Dict[str, List[str]]:
    """
    Classify companies by their development stage focus.

    Args:
        company_aggregation: Output from aggregate_by_company

    Returns:
        dict with commercial_stage, late_stage, early_stage, preclinical
    """
    company_portfolios = company_aggregation['company_portfolios']

    commercial = []
    late_stage = []
    early_stage = []
    unknown = []

    for company, portfolio in company_portfolios.items():
        if portfolio['approved_drugs'] > 0:
            commercial.append(company)
        else:
            leading_phase = get_leading_phase(portfolio['phase_distribution'])
            if leading_phase in ['Phase 3', 'Phase 4']:
                late_stage.append(company)
            elif leading_phase in ['Phase 1', 'Phase 2', 'Early Phase 1']:
                early_stage.append(company)
            else:
                unknown.append(company)

    return {
        'commercial_stage': commercial,
        'late_stage_clinical': late_stage,
        'early_stage_clinical': early_stage,
        'unknown': unknown
    }
