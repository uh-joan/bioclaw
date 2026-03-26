"""
Visualization and output formatting utilities.
"""

from typing import Dict, Any


def generate_ascii_visualization(
    target_summary: Dict,
    genetic_validation: Dict,
    competitive_landscape: Dict,
    company_analysis: Dict = None,
    safety_analysis: Dict = None
) -> str:
    """
    Generate ASCII visualization of target landscape.

    Args:
        target_summary: Target information
        genetic_validation: Genetic evidence
        competitive_landscape: Competitive data
        company_analysis: Optional company positioning data (Phase 2)
        safety_analysis: Optional safety profiling data (Phase 3)

    Returns:
        Multi-line ASCII art string
    """
    lines = []

    # Header
    lines.append("=" * 80)
    lines.append(f"TARGET LANDSCAPE: {target_summary['official_name'].upper()} ({target_summary['gene_symbol']})")
    lines.append("=" * 80)
    lines.append(f"Target Class: {target_summary['target_class']}")
    lines.append(f"Druggability Score: {target_summary['druggability_assessment']['score']}/1.0")

    # Handle optional genetic validation
    if genetic_validation:
        lines.append(f"Genetic Validation: {genetic_validation['overall_score']}/1.0 ({genetic_validation['evidence_strength']} evidence)")

    lines.append("")

    # Competitive Landscape
    lines.append("COMPETITIVE LANDSCAPE")
    lines.append("-" * 80)
    summary = competitive_landscape['summary']
    lines.append(f"Total Drugs: {summary['total_drugs']:<15} Approved: {summary['approved']:<15}")
    lines.append(f"Investigational: {summary['investigational']:<10} Experimental: {summary['experimental']:<10}")
    lines.append(f"Total Trials: {summary['total_trials']:<15} Drugs with Trials: {summary['drugs_with_trials']:<15}")
    lines.append("")

    # Phase Distribution
    if competitive_landscape['phase_distribution']:
        lines.append("PHASE DISTRIBUTION (by trial count)")
        lines.append("-" * 80)
        phase_dist = competitive_landscape['phase_distribution']
        max_count = max(phase_dist.values()) if phase_dist else 1

        for phase in ['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4', 'Not Applicable']:
            count = phase_dist.get(phase, 0)
            if count > 0:
                bar_length = int((count / max_count) * 40)
                bar = "█" * bar_length + "░" * (40 - bar_length)
                lines.append(f"{phase:<20} {count:>4}  {bar}")
        lines.append("")

    # Top Drugs
    if competitive_landscape['drugs']:
        lines.append("TOP DRUGS (sample)")
        lines.append("-" * 80)
        for drug in competitive_landscape['drugs'][:10]:
            groups = ', '.join(drug.get('groups', ['Unknown']))
            lines.append(f"  • {drug['drug_name']} - {groups}")
        lines.append("")

    # Key Disease Associations
    if genetic_validation and genetic_validation['key_associations']:
        lines.append("KEY DISEASE ASSOCIATIONS")
        lines.append("-" * 80)
        for assoc in genetic_validation['key_associations'][:5]:
            lines.append(f"  • {assoc['disease']} (score: {assoc['association_score']})")
        lines.append("")

    # Company Competitive Positioning (Phase 2)
    if company_analysis:
        from company_utils import get_top_companies

        lines.append("COMPANY COMPETITIVE POSITIONING (Phase 2)")
        lines.append("-" * 80)
        summary = company_analysis['summary']
        lines.append(f"Total Companies: {summary['total_companies']}")
        lines.append(f"Companies with Approved Drugs: {summary['companies_with_approved']}")
        lines.append("")

        top_companies = get_top_companies(company_analysis, top_n=5)
        if top_companies:
            lines.append("TOP 5 COMPANIES BY PIPELINE DEPTH:")
            for i, company_info in enumerate(top_companies, 1):
                company = company_info['company']
                lines.append(
                    f"  {i}. {company:<25} "
                    f"Drugs: {company_info['total_drugs']:<2} "
                    f"Approved: {company_info['approved']:<2} "
                    f"Trials: {company_info['total_trials']:<3}"
                )
            lines.append("")

    # Safety Analysis (Phase 3)
    if safety_analysis:
        from safety_utils import classify_by_safety_risk

        lines.append("SAFETY ANALYSIS (Phase 3)")
        lines.append("-" * 80)
        summary = safety_analysis['summary']
        lines.append(f"Drugs Analyzed: {summary['total_drugs_analyzed']}")
        lines.append(f"With Adverse Event Data: {summary['drugs_with_adverse_event_data']}")
        lines.append(f"With Boxed Warnings: {summary['drugs_with_boxed_warnings']}")
        lines.append("")

        # Risk classification
        classified = classify_by_safety_risk(safety_analysis)
        lines.append("RISK CLASSIFICATION:")
        lines.append(f"  High Risk: {len(classified['high_risk'])} drugs")
        lines.append(f"  Moderate Risk: {len(classified['moderate_risk'])} drugs")
        lines.append(f"  Low Risk: {len(classified['low_risk'])} drugs")
        lines.append(f"  Insufficient Data: {len(classified['insufficient_data'])} drugs")
        lines.append("")

    # Footer
    lines.append("=" * 80)
    if safety_analysis:
        phase_status = "ALL PHASES COMPLETE (1-3)"
        next_phase = "Ready for competitive intelligence!"
    elif company_analysis:
        phase_status = "Phase 2 Implementation Complete"
        next_phase = "Phase 3 (Safety profiling)"
    else:
        phase_status = "Phase 1 Implementation Complete"
        next_phase = "Phase 2 (Regulatory status + Company analysis)"
    lines.append(phase_status)
    lines.append(f"Next: {next_phase}")
    lines.append("=" * 80)

    return "\n".join(lines)


def format_summary_stats(result: Dict) -> str:
    """
    Format key statistics for quick display.

    Args:
        result: Full result dict from get_target_landscape_analysis

    Returns:
        Formatted summary string
    """
    lines = []
    target = result['target_summary']
    validation = result['genetic_validation']
    competitive = result['competitive_landscape']['summary']

    lines.append("\nKEY STATISTICS:")
    lines.append(f"  Target: {target['official_name']} ({target['gene_symbol']})")
    lines.append(f"  Druggability: {target['druggability_assessment']['score']}/1.0")
    lines.append(f"  Genetic Validation: {validation['overall_score']}/1.0 ({validation['evidence_strength']})")
    lines.append(f"  Total Drugs Found: {competitive['total_drugs']}")
    lines.append(f"  Approved Drugs: {competitive['approved']}")
    lines.append(f"  Total Clinical Trials: {competitive['total_trials']}")

    return "\n".join(lines)


def create_progress_printer():
    """
    Create a simple progress printing function for CLI.

    Returns:
        Function that prints progress updates
    """
    def print_progress(percent, message):
        print(f"[{percent:3d}%] {message}")

    return print_progress


def generate_radial_chart_data(
    drugs: list,
    trials_by_drug: dict = None
) -> Dict[str, Any]:
    """
    Generate radial/polar chart data for competitive landscape visualization.

    Encoding:
    - Rings (radius): Clinical development phase (Preclinical → Phase 1 → ... → Approved)
    - Sectors (angle): Target biology / mechanism (e.g., "GLP1R Agonist", "GLP1R/GIPR Dual")
    - Shape: Drug modality (triangle=small molecule, circle=antibody, square=other biologic)
    - Color: Target selectivity (green=selective, blue=pan-target, red=multi-specific)

    Args:
        drugs: List of drug dicts with classification fields:
            - modality, modality_category, chart_symbol
            - mechanism_summary, mechanism_type, sector, targets
            - selectivity, color_code
        trials_by_drug: Optional dict mapping drug_name → trial data (for phase detection)

    Returns:
        dict with:
            - data: List of Plotly trace dicts for polar scatter chart
            - layout: Plotly layout configuration
            - metadata: Summary statistics (sector counts, modality distribution, etc.)
    """
    import math
    from collections import defaultdict

    # Filter drugs with classification data
    classified_drugs = [
        d for d in drugs
        if d.get('sector') and d.get('chart_symbol') and d.get('color_code')
    ]

    if not classified_drugs:
        return {
            'data': [],
            'layout': {},
            'metadata': {'error': 'No classified drugs found'}
        }

    # ========================================================================
    # STEP 1: Determine clinical phase for each drug (for radius)
    # ========================================================================
    def get_max_phase(drug_name: str) -> float:
        """Get maximum clinical phase as numeric radius (inverted: approved=center, phase 1=outer)."""
        # Check drug groups first
        groups = [g.lower() for g in drug.get('groups', [])]
        if 'approved' in groups:
            return 1.0  # Innermost ring (center)

        # Check trials if available
        if trials_by_drug and drug_name in trials_by_drug:
            trials = trials_by_drug[drug_name].get('trials', [])
            # Inverted phase values (lower = more advanced)
            phase_values = {
                'Phase 4': 1.5,
                'Phase 3': 2.0,
                'Phase 2': 2.5,
                'Phase 1': 3.0,
                'Early Phase 1': 3.0
            }
            max_phase = 3.0  # Default to Phase 1 if no match
            for trial in trials:
                phase_str = trial.get('phase', '')
                # Extract first phase number from combined phases (e.g., "Phase1, Phase2" → take most advanced)
                if 'Phase 4' in phase_str or 'Phase4' in phase_str:
                    max_phase = min(max_phase, 1.5)
                elif 'Phase 3' in phase_str or 'Phase3' in phase_str:
                    max_phase = min(max_phase, 2.0)
                elif 'Phase 2' in phase_str or 'Phase2' in phase_str:
                    max_phase = min(max_phase, 2.5)
                elif 'Phase 1' in phase_str or 'Phase1' in phase_str or 'Early Phase 1' in phase_str:
                    max_phase = min(max_phase, 3.0)
            return max_phase

        # Default: Investigational without trial data = Phase 2
        if 'investigational' in groups:
            return 2.5  # Phase 2
        else:
            return 3.0  # Phase 1

    for drug in classified_drugs:
        drug['_phase_radius'] = get_max_phase(drug['drug_name'])

    # ========================================================================
    # STEP 2: Aggregate drugs by sector and assign angles
    # ========================================================================
    sectors = defaultdict(list)
    for drug in classified_drugs:
        sector = drug.get('sector', 'Unknown')
        sectors[sector].append(drug)

    # Sort sectors alphabetically for consistent positioning
    sector_names = sorted(sectors.keys())
    num_sectors = len(sector_names)

    # Assign angle range to each sector (evenly divide 360°)
    sector_angles = {}
    angle_per_sector = 360.0 / num_sectors if num_sectors > 0 else 360.0

    for i, sector_name in enumerate(sector_names):
        # Center angle for this sector
        center_angle = i * angle_per_sector
        sector_angles[sector_name] = {
            'center': center_angle,
            'start': center_angle - angle_per_sector / 2,
            'end': center_angle + angle_per_sector / 2
        }

    # ========================================================================
    # STEP 3: Position drugs within sectors (spread around center angle)
    # ========================================================================
    for sector_name, drugs_in_sector in sectors.items():
        angle_info = sector_angles[sector_name]
        num_drugs = len(drugs_in_sector)

        if num_drugs == 1:
            # Single drug: place at center
            drugs_in_sector[0]['_angle'] = angle_info['center']
        else:
            # Multiple drugs: spread evenly within sector range
            # Use 80% of sector width to avoid overlap with adjacent sectors
            spread_width = angle_per_sector * 0.8
            spread_start = angle_info['center'] - spread_width / 2

            for i, drug in enumerate(drugs_in_sector):
                drug['_angle'] = spread_start + (i / (num_drugs - 1)) * spread_width

    # ========================================================================
    # STEP 4: Build Plotly traces (group by modality for legend)
    # ========================================================================
    def radius_to_phase_name(r: float) -> str:
        """Convert radius value to human-readable phase name."""
        if r <= 1.25:
            return 'Approved'
        elif r <= 1.75:
            return 'Phase 4'
        elif r <= 2.25:
            return 'Phase 3'
        elif r <= 2.75:
            return 'Phase 2'
        else:
            return 'Phase 1'

    modality_groups = defaultdict(list)
    for drug in classified_drugs:
        modality_cat = drug.get('modality_category', 'unknown')
        modality_groups[modality_cat].append(drug)

    # Shape mapping for Plotly
    shape_map = {
        'triangle': 'triangle-up',
        'circle': 'circle',
        'square': 'square',
        'double-circle': 'circle-open',  # Approximate - will need custom rendering
    }

    traces = []
    for modality_cat, modality_drugs in modality_groups.items():
        # Extract coordinates
        r_values = [d['_phase_radius'] for d in modality_drugs]
        theta_values = [d['_angle'] for d in modality_drugs]
        colors = [d.get('color_code', '#888888') for d in modality_drugs]
        drug_names = [d['drug_name'] for d in modality_drugs]
        mechanisms = [d.get('mechanism_summary', 'Unknown') for d in modality_drugs]
        selectivities = [d.get('selectivity', 'Unknown') for d in modality_drugs]

        # Get representative modality name and shape
        modality_name = modality_drugs[0].get('modality', modality_cat.replace('_', ' ').title())
        symbol = modality_drugs[0].get('chart_symbol', 'circle')
        plotly_symbol = shape_map.get(symbol, 'circle')

        # Build hover text with phase names
        hover_texts = [
            f"<b>{name}</b><br>"
            f"Mechanism: {mech}<br>"
            f"Selectivity: {sel}<br>"
            f"Phase: {radius_to_phase_name(r)}"
            for name, mech, sel, r in zip(drug_names, mechanisms, selectivities, r_values)
        ]

        trace = {
            'type': 'scatterpolar',
            'r': r_values,
            'theta': theta_values,
            'mode': 'markers',
            'name': modality_name,
            'marker': {
                'size': 12,
                'color': colors,
                'symbol': plotly_symbol,
                'line': {
                    'width': 1,
                    'color': '#0d0d0d'
                }
            },
            'text': drug_names,
            'hovertext': hover_texts,
            'hoverinfo': 'text'
        }
        traces.append(trace)

    # ========================================================================
    # STEP 5: Build layout configuration
    # ========================================================================
    layout = {
        'polar': {
            'radialaxis': {
                'visible': True,
                'range': [0, 3.5],
                'tickmode': 'array',
                'tickvals': [1.0, 1.5, 2.0, 2.5, 3.0],
                'ticktext': ['Approved', 'Phase 4', 'Phase 3', 'Phase 2', 'Phase 1'],
                'showline': True,
                'linecolor': '#333',
                'gridcolor': '#2a2a2a'
            },
            'angularaxis': {
                'visible': True,
                'tickmode': 'array',
                'tickvals': [sector_angles[s]['center'] for s in sector_names],
                'ticktext': sector_names,
                'direction': 'clockwise',
                'rotation': 90,
                'showline': True,
                'linecolor': '#333',
                'gridcolor': '#2a2a2a'
            },
            'bgcolor': '#0d0d0d'
        },
        'showlegend': True,
        'legend': {
            'bgcolor': '#1a1a1a',
            'bordercolor': '#333',
            'borderwidth': 1,
            'font': {'color': '#e0e0e0', 'size': 11}
        },
        'paper_bgcolor': '#0d0d0d',
        'plot_bgcolor': '#0d0d0d',
        'font': {'color': '#e0e0e0', 'family': 'monospace'},
        'height': 700,
        'margin': {'t': 80, 'b': 80, 'l': 80, 'r': 80}
    }

    # ========================================================================
    # STEP 6: Generate metadata
    # ========================================================================
    modality_counts = {k: len(v) for k, v in modality_groups.items()}
    sector_counts = {k: len(v) for k, v in sectors.items()}

    # Phase distribution (inverted: lower radius = more advanced)
    phase_dist = defaultdict(int)
    for drug in classified_drugs:
        r = drug['_phase_radius']
        if r <= 1.25:
            phase_dist['Approved'] += 1
        elif r <= 1.75:
            phase_dist['Phase 4'] += 1
        elif r <= 2.25:
            phase_dist['Phase 3'] += 1
        elif r <= 2.75:
            phase_dist['Phase 2'] += 1
        else:  # r <= 3.0
            phase_dist['Phase 1'] += 1

    # Selectivity distribution
    selectivity_counts = defaultdict(int)
    for drug in classified_drugs:
        sel = drug.get('selectivity', 'Unknown')
        selectivity_counts[sel] += 1

    metadata = {
        'total_drugs': len(classified_drugs),
        'num_sectors': num_sectors,
        'sectors': list(sector_names),
        'sector_counts': dict(sector_counts),
        'modality_distribution': modality_counts,
        'phase_distribution': dict(phase_dist),
        'selectivity_distribution': dict(selectivity_counts)
    }

    return {
        'data': traces,
        'layout': layout,
        'metadata': metadata
    }
