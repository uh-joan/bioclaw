"""Visualization utilities for real-world utilization analysis.

Provides ASCII table formatting and chart generation.
"""

from typing import List, Dict, Any, Optional
from constants import format_currency, format_number, get_state_name


def build_header(title: str, width: int = 80) -> str:
    """Build a section header.

    Args:
        title: Header title
        width: Total width

    Returns:
        Formatted header string
    """
    return f"\n{'=' * width}\n{title}\n{'=' * width}"


def build_subheader(title: str, width: int = 80) -> str:
    """Build a subsection header.

    Args:
        title: Subheader title
        width: Total width

    Returns:
        Formatted subheader string
    """
    return f"\n{title}\n{'─' * width}"


def build_prescriber_table(
    prescriber_data: List[Dict[str, Any]],
    total_claims: int,
    width: int = 80
) -> str:
    """Build ASCII table for prescriber specialty breakdown.

    Args:
        prescriber_data: List of specialty dictionaries
        total_claims: Total claims for percentage calculation
        width: Table width

    Returns:
        Formatted ASCII table
    """
    lines = []
    lines.append(build_subheader("PRESCRIBER ANALYSIS (Medicare Part D)", width))

    # Header row
    header = f"{'Specialty':<30} {'% Claims':>10} {'Claims':>12} {'Beneficiaries':>14} {'Providers':>10}"
    lines.append(header)
    lines.append("─" * width)

    # Data rows
    for item in prescriber_data[:10]:  # Top 10
        specialty = item.get('specialty', 'Unknown')[:29]
        pct = item.get('pct_of_claims', 0)
        claims = item.get('total_claims', 0)
        beneficiaries = item.get('total_beneficiaries', 0)
        providers = item.get('provider_count', 0)

        row = f"{specialty:<30} {pct:>9.1f}% {format_number(claims):>12} {format_number(beneficiaries):>14} {format_number(providers):>10}"
        lines.append(row)

    return "\n".join(lines)


def build_geographic_table(
    geographic_data: List[Dict[str, Any]],
    width: int = 80
) -> str:
    """Build ASCII table for geographic breakdown.

    Args:
        geographic_data: List of state dictionaries
        width: Table width

    Returns:
        Formatted ASCII table
    """
    lines = []
    lines.append(build_subheader("GEOGRAPHIC HOTSPOTS (Top States by Spending)", width))

    # Header row
    header = f"{'State':<15} {'Spending':>12} {'% Total':>10} {'Claims':>12} {'Per Capita':>12}"
    lines.append(header)
    lines.append("─" * width)

    # Data rows
    for item in geographic_data[:10]:  # Top 10
        state_code = item.get('state', '')
        state_name = get_state_name(state_code)[:14]
        spending = item.get('total_spending', 0)
        pct = item.get('pct_of_total', 0)
        claims = item.get('total_claims', 0)
        per_capita = item.get('per_capita_index', 1.0)

        row = f"{state_name:<15} {format_currency(spending):>12} {pct:>9.1f}% {format_number(claims):>12} {per_capita:>10.1f}x"
        lines.append(row)

    return "\n".join(lines)


def build_spending_summary(
    medicare_part_d_spending: float,
    medicare_part_b_spending: float,
    medicaid_spending: float,
    medicare_beneficiaries: int,
    medicare_claims: int,
    part_d_year: Optional[int] = None,
    part_b_year: Optional[int] = None,
    width: int = 80
) -> str:
    """Build spending summary section with Part B support.

    Args:
        medicare_part_d_spending: Total Medicare Part D spending (retail pharmacy)
        medicare_part_b_spending: Total Medicare Part B spending (physician-administered)
        medicaid_spending: Total Medicaid spending
        medicare_beneficiaries: Number of Medicare beneficiaries
        medicare_claims: Number of Medicare claims
        part_d_year: Data year for Part D
        part_b_year: Data year for Part B
        width: Section width

    Returns:
        Formatted summary string
    """
    lines = []
    lines.append(build_subheader("SPENDING SUMMARY (GROSS - Pre-Rebate)", width))

    combined_medicare = medicare_part_d_spending + medicare_part_b_spending
    combined_all = combined_medicare + medicaid_spending

    # Part D with year
    part_d_label = f"Medicare Part D ({part_d_year}):" if part_d_year else "Medicare Part D:"
    lines.append(f"{part_d_label:<30} {format_currency(medicare_part_d_spending):>15}")

    # Part B with year (if any)
    if medicare_part_b_spending > 0:
        part_b_label = f"Medicare Part B ({part_b_year}):" if part_b_year else "Medicare Part B:"
        lines.append(f"{part_b_label:<30} {format_currency(medicare_part_b_spending):>15}")
        lines.append(f"{'  Combined Medicare:':<30} {format_currency(combined_medicare):>15}")

    lines.append(f"{'Medicaid:':<30} {format_currency(medicaid_spending):>15}")
    lines.append(f"{'Total Government Spend:':<30} {format_currency(combined_all):>15}")
    lines.append("")
    lines.append(f"{'Medicare Beneficiaries:':<30} {format_number(medicare_beneficiaries):>15}")
    lines.append(f"{'Medicare Claims:':<30} {format_number(medicare_claims):>15}")

    return "\n".join(lines)


def build_nadac_table(
    nadac_data: List[Dict[str, Any]],
    width: int = 80
) -> str:
    """Build ASCII table for NADAC pricing.

    Args:
        nadac_data: List of NADAC pricing dictionaries
        width: Table width

    Returns:
        Formatted ASCII table
    """
    lines = []
    lines.append(build_subheader("NADAC PRICING (Pharmacy Acquisition Cost)", width))

    # Header row
    header = f"{'Formulation':<35} {'NDC':<16} {'Price/Unit':>12} {'Eff. Date':>12}"
    lines.append(header)
    lines.append("─" * width)

    # Data rows
    for item in nadac_data[:10]:  # Top 10 formulations
        description = item.get('description', 'Unknown')[:34]
        ndc = item.get('ndc', '')
        price = item.get('nadac_per_unit', 0)
        unit = item.get('pricing_unit', 'EA')
        eff_date = item.get('effective_date', '')[:10]

        price_str = f"${price:.2f}/{unit}"
        row = f"{description:<35} {ndc:<16} {price_str:>12} {eff_date:>12}"
        lines.append(row)

    return "\n".join(lines)


def build_medicaid_table(
    medicaid_data: List[Dict[str, Any]],
    width: int = 80
) -> str:
    """Build ASCII table for Medicaid utilization.

    Args:
        medicaid_data: List of state Medicaid dictionaries
        width: Table width

    Returns:
        Formatted ASCII table
    """
    lines = []
    lines.append(build_subheader("MEDICAID UTILIZATION (Top States)", width))

    # Header row
    header = f"{'State':<15} {'Spending':>12} {'Prescriptions':>14} {'Avg Cost/Rx':>12}"
    lines.append(header)
    lines.append("─" * width)

    # Data rows
    for item in medicaid_data[:5]:  # Top 5
        state_code = item.get('state', '')
        state_name = get_state_name(state_code)[:14]
        spending = item.get('total_spending', 0)
        prescriptions = item.get('total_prescriptions', 0)
        avg_cost = spending / prescriptions if prescriptions > 0 else 0

        row = f"{state_name:<15} {format_currency(spending):>12} {format_number(prescriptions):>14} {format_currency(avg_cost):>12}"
        lines.append(row)

    return "\n".join(lines)


def build_data_caveats(
    data_caveats: List[str],
    width: int = 80
) -> str:
    """Build data caveats section.

    Args:
        data_caveats: List of caveat strings
        width: Section width

    Returns:
        Formatted caveats string
    """
    if not data_caveats:
        return ""

    lines = []
    lines.append(build_subheader("⚠️ DATA CAVEATS & METHODOLOGY NOTES", width))

    for i, caveat in enumerate(data_caveats[:6], 1):  # Show first 6
        # Wrap long caveats
        if len(caveat) > width - 4:
            words = caveat.split()
            current_line = f"{i}. "
            for word in words:
                if len(current_line) + len(word) + 1 > width - 2:
                    lines.append(current_line)
                    current_line = "   " + word + " "
                else:
                    current_line += word + " "
            if current_line.strip():
                lines.append(current_line.rstrip())
        else:
            lines.append(f"{i}. {caveat}")

    return "\n".join(lines)


def build_full_visualization(
    drug_name: str,
    analysis_date: str,
    summary: Dict[str, Any],
    prescriber_data: List[Dict[str, Any]],
    geographic_data: List[Dict[str, Any]],
    nadac_data: List[Dict[str, Any]],
    medicaid_data: List[Dict[str, Any]],
    total_prescribers: int = 0,
    avg_beneficiaries_per_prescriber: float = 0,
    data_caveats: Optional[List[str]] = None,
    width: int = 80
) -> str:
    """Build complete visualization output.

    Args:
        drug_name: Name of drug analyzed
        analysis_date: Date of analysis
        summary: Summary statistics dict
        prescriber_data: Prescriber specialty breakdown
        geographic_data: Geographic breakdown
        nadac_data: NADAC pricing data
        medicaid_data: Medicaid utilization data
        total_prescribers: Total unique prescribers
        avg_beneficiaries_per_prescriber: Average beneficiaries per prescriber
        data_caveats: List of data caveat strings
        width: Output width

    Returns:
        Complete formatted ASCII output
    """
    lines = []

    # Main header
    lines.append("=" * width)
    lines.append(f"REAL-WORLD UTILIZATION ANALYSIS: {drug_name.upper()}")
    lines.append("=" * width)
    lines.append(f"Analysis Date: {analysis_date}")

    # Data sources with years
    part_d_year = summary.get('medicare_part_d_year', '')
    part_b_year = summary.get('medicare_part_b_year', '')
    data_sources = f"Data Sources: Medicare Part D ({part_d_year or 'N/A'})"
    if summary.get('total_medicare_part_b_spending_raw', 0) > 0:
        data_sources += f", Part B ({part_b_year or 'N/A'})"
    data_sources += ", Medicaid, NADAC"
    lines.append(data_sources)

    # Spending summary with Part B support
    medicare_part_d_spending = summary.get('total_medicare_part_d_spending_raw', summary.get('total_medicare_spending_raw', 0))
    medicare_part_b_spending = summary.get('total_medicare_part_b_spending_raw', 0)
    medicaid_spending = summary.get('total_medicaid_spending_raw', 0)
    medicare_beneficiaries = summary.get('medicare_beneficiaries', 0)
    medicare_claims = summary.get('medicare_claims', 0)

    lines.append(build_spending_summary(
        medicare_part_d_spending,
        medicare_part_b_spending,
        medicaid_spending,
        medicare_beneficiaries,
        medicare_claims,
        part_d_year,
        part_b_year,
        width
    ))

    # Prescriber analysis
    if prescriber_data:
        total_claims = summary.get('medicare_claims', 0)
        lines.append(build_prescriber_table(prescriber_data, total_claims, width))

        # Prescriber totals
        lines.append("")
        lines.append(f"Total Prescribers: {format_number(total_prescribers)}")
        if avg_beneficiaries_per_prescriber > 0:
            lines.append(f"Avg Beneficiaries per Prescriber: {avg_beneficiaries_per_prescriber:.1f}")

    # Geographic analysis
    if geographic_data:
        lines.append(build_geographic_table(geographic_data, width))

    # NADAC pricing
    if nadac_data:
        lines.append(build_nadac_table(nadac_data, width))

    # Medicaid utilization
    if medicaid_data:
        lines.append(build_medicaid_table(medicaid_data, width))

    # Data caveats section
    if data_caveats:
        lines.append(build_data_caveats(data_caveats, width))

    # Footer
    lines.append("")
    lines.append("=" * width)

    return "\n".join(lines)
