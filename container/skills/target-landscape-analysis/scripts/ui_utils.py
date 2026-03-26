"""
UI utilities for generating rich HTML visualization of target landscape analysis.
"""

from typing import Dict, Any
import json


def generate_html_ui(result: Dict[str, Any]) -> str:
    """
    Generate interactive HTML UI for target landscape analysis results.

    Args:
        result: Complete result dict from get_target_landscape_analysis

    Returns:
        str: Complete HTML document
    """
    target_summary = result['target_summary']
    genetic_validation = result.get('genetic_validation', {})
    competitive_landscape = result['competitive_landscape']
    company_analysis = result.get('company_analysis')
    safety_analysis = result.get('safety_analysis')
    patent_analysis = result.get('patent_analysis')
    phase_impl = result['phase_implementation']

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Target Landscape: {target_summary['gene_symbol']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            font-size: 32px;
            color: #667eea;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            font-size: 18px;
            color: #666;
            margin-bottom: 20px;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}

        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 8px;
            color: white;
        }}

        .metric-card .label {{
            font-size: 12px;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .metric-card .value {{
            font-size: 28px;
            font-weight: bold;
            margin-top: 5px;
        }}

        .metric-card .subvalue {{
            font-size: 14px;
            opacity: 0.9;
            margin-top: 5px;
        }}

        .section {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .section h2 {{
            font-size: 24px;
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }}

        .section h3 {{
            font-size: 18px;
            color: #764ba2;
            margin: 20px 0 10px 0;
        }}

        .two-column {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}

        .chart-container {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
        }}

        .bar-chart {{
            margin: 10px 0;
        }}

        .bar-item {{
            margin-bottom: 10px;
        }}

        .bar-item .label {{
            font-size: 14px;
            margin-bottom: 5px;
            display: flex;
            justify-content: space-between;
        }}

        .bar-item .bar {{
            height: 30px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 4px;
            position: relative;
            overflow: hidden;
        }}

        .bar-item .bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
        }}

        .drug-list {{
            list-style: none;
            padding: 0;
        }}

        .drug-list li {{
            padding: 12px;
            background: #f8f9fa;
            margin-bottom: 8px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }}

        .drug-list li strong {{
            color: #667eea;
        }}

        .disease-list {{
            list-style: none;
            padding: 0;
        }}

        .disease-list li {{
            padding: 10px;
            background: #f8f9fa;
            margin-bottom: 6px;
            border-radius: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .score-badge {{
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }}

        .company-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}

        .company-table th {{
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #e0e0e0;
            font-size: 14px;
        }}

        .company-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid #f0f0f0;
        }}

        .company-table tr:hover {{
            background: #f8f9fa;
        }}

        .risk-badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            display: inline-block;
        }}

        .risk-high {{ background: #fee; color: #c00; }}
        .risk-moderate {{ background: #fef3cd; color: #856404; }}
        .risk-low {{ background: #d4edda; color: #155724; }}
        .risk-insufficient {{ background: #e2e3e5; color: #383d41; }}

        .phase-badge {{
            background: #667eea;
            color: white;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 15px;
        }}

        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}

        .info-item {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
        }}

        .info-item .label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }}

        .info-item .value {{
            font-size: 16px;
            font-weight: 600;
            color: #333;
        }}

        @media (max-width: 768px) {{
            .two-column {{
                grid-template-columns: 1fr;
            }}

            .metrics-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>{target_summary['official_name']}</h1>
            <div class="subtitle">Gene Symbol: {target_summary['gene_symbol']} | Target Class: {target_summary['target_class']}</div>
            <div class="subtitle">Ensembl ID: {target_summary['ensembl_id']}</div>
            <span class="phase-badge">{phase_impl['current']}</span>

            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="label">Druggability</div>
                    <div class="value">{target_summary['druggability_assessment']['score']}/1.0</div>
                </div>
                <div class="metric-card">
                    <div class="label">Genetic Validation</div>
                    <div class="value">{genetic_validation.get('overall_score', 'N/A')}/1.0</div>
                    <div class="subvalue">{genetic_validation.get('evidence_strength', 'Unknown')} Evidence</div>
                </div>
                <div class="metric-card">
                    <div class="label">Total Drugs</div>
                    <div class="value">{competitive_landscape['summary']['total_drugs']}</div>
                </div>
                <div class="metric-card">
                    <div class="label">Clinical Trials</div>
                    <div class="value">{competitive_landscape['summary']['total_trials']}</div>
                </div>
            </div>
        </div>

        <!-- Genetic Validation -->
        {_render_genetic_validation_section(genetic_validation)}

        <!-- Competitive Landscape -->
        {_render_competitive_landscape_section(competitive_landscape)}

        <!-- Company Analysis -->
        {_render_company_section(company_analysis) if company_analysis else ''}

        <!-- Safety Analysis -->
        {_render_safety_section(safety_analysis) if safety_analysis else ''}

        <!-- Patent Landscape -->
        {_render_patent_section(patent_analysis) if patent_analysis else ''}

    </div>
</body>
</html>"""

    return html


def _render_genetic_validation_section(genetic_validation: Dict) -> str:
    """Render genetic validation section."""
    if not genetic_validation:
        return ""

    associations = genetic_validation.get('key_associations', [])

    associations_html = ""
    if associations:
        associations_html = "<ul class='disease-list'>"
        for assoc in associations[:10]:
            associations_html += f"""
            <li>
                <span>{assoc['disease']}</span>
                <span class='score-badge'>{assoc['association_score']}</span>
            </li>
            """
        associations_html += "</ul>"

    return f"""
    <div class="section">
        <h2>Genetic Validation</h2>
        <div class="info-grid">
            <div class="info-item">
                <div class="label">Overall Score</div>
                <div class="value">{genetic_validation.get('overall_score', 'N/A')}/1.0</div>
            </div>
            <div class="info-item">
                <div class="label">Evidence Strength</div>
                <div class="value">{genetic_validation.get('evidence_strength', 'Unknown')}</div>
            </div>
            <div class="info-item">
                <div class="label">Key Associations</div>
                <div class="value">{len(associations)} diseases</div>
            </div>
        </div>

        <h3>Top Disease Associations</h3>
        {associations_html}
    </div>
    """


def _render_competitive_landscape_section(competitive_landscape: Dict) -> str:
    """Render competitive landscape section."""
    summary = competitive_landscape['summary']
    phase_dist = competitive_landscape.get('phase_distribution', {})
    drugs = competitive_landscape.get('drugs', [])[:15]

    # Phase distribution bar chart
    phase_html = ""
    if phase_dist:
        max_count = max(phase_dist.values()) if phase_dist else 1
        phase_html = "<div class='chart-container'><div class='bar-chart'>"
        for phase in ['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4', 'Not Applicable']:
            count = phase_dist.get(phase, 0)
            if count > 0:
                width = int((count / max_count) * 100)
                phase_html += f"""
                <div class='bar-item'>
                    <div class='label'>
                        <span>{phase}</span>
                        <span><strong>{count}</strong> trials</span>
                    </div>
                    <div class='bar'>
                        <div class='bar-fill' style='width: {width}%'></div>
                    </div>
                </div>
                """
        phase_html += "</div></div>"

    # Top drugs list
    drugs_html = ""
    if drugs:
        drugs_html = "<ul class='drug-list'>"
        for drug in drugs:
            groups = ', '.join(drug.get('groups', ['Unknown']))
            drugs_html += f"""
            <li>
                <strong>{drug['drug_name']}</strong><br>
                <small>Status: {groups if groups else 'Not specified'}</small>
            </li>
            """
        drugs_html += "</ul>"

    return f"""
    <div class="section">
        <h2>Competitive Landscape</h2>
        <div class="info-grid">
            <div class="info-item">
                <div class="label">Total Drugs Found</div>
                <div class="value">{summary['total_drugs']}</div>
            </div>
            <div class="info-item">
                <div class="label">Total Clinical Trials</div>
                <div class="value">{summary['total_trials']}</div>
            </div>
            <div class="info-item">
                <div class="label">Drugs with Trials</div>
                <div class="value">{summary['drugs_with_trials']}</div>
            </div>
            <div class="info-item">
                <div class="label">FDA Approved</div>
                <div class="value">{summary.get('fda_approved', 0)}</div>
            </div>
        </div>

        <h3>Phase Distribution</h3>
        {phase_html}

        <h3>Top Drugs ({len(drugs)} shown)</h3>
        {drugs_html}
    </div>
    """


def _render_company_section(company_analysis: Dict) -> str:
    """Render company competitive positioning section."""
    if not company_analysis:
        return ""

    from company_utils import get_top_companies

    summary = company_analysis['summary']
    top_companies = get_top_companies(company_analysis, top_n=10)

    table_html = ""
    if top_companies:
        table_html = """
        <table class='company-table'>
            <thead>
                <tr>
                    <th>Company</th>
                    <th>Total Drugs</th>
                    <th>Approved</th>
                    <th>Investigational</th>
                    <th>Total Trials</th>
                    <th>Leading Phase</th>
                </tr>
            </thead>
            <tbody>
        """
        for company_info in top_companies:
            table_html += f"""
            <tr>
                <td><strong>{company_info['company']}</strong></td>
                <td>{company_info['total_drugs']}</td>
                <td>{company_info['approved']}</td>
                <td>{company_info['investigational']}</td>
                <td>{company_info['total_trials']}</td>
                <td>{company_info['leading_phase']}</td>
            </tr>
            """
        table_html += "</tbody></table>"

    return f"""
    <div class="section">
        <h2>Company Competitive Positioning</h2>
        <div class="info-grid">
            <div class="info-item">
                <div class="label">Total Companies</div>
                <div class="value">{summary['total_companies']}</div>
            </div>
            <div class="info-item">
                <div class="label">With Approved Drugs</div>
                <div class="value">{summary['companies_with_approved']}</div>
            </div>
            <div class="info-item">
                <div class="label">With Investigational</div>
                <div class="value">{summary['companies_with_investigational']}</div>
            </div>
        </div>

        <h3>Top 10 Companies by Pipeline Depth</h3>
        {table_html}
    </div>
    """


def _render_safety_section(safety_analysis: Dict) -> str:
    """Render safety analysis section."""
    if not safety_analysis:
        return ""

    from safety_utils import classify_by_safety_risk

    summary = safety_analysis['summary']
    classified = classify_by_safety_risk(safety_analysis)

    risk_cards = f"""
    <div class="info-grid">
        <div class="info-item">
            <div class="label">High Risk</div>
            <div class="value">{len(classified['high_risk'])} drugs</div>
        </div>
        <div class="info-item">
            <div class="label">Moderate Risk</div>
            <div class="value">{len(classified['moderate_risk'])} drugs</div>
        </div>
        <div class="info-item">
            <div class="label">Low Risk</div>
            <div class="value">{len(classified['low_risk'])} drugs</div>
        </div>
        <div class="info-item">
            <div class="label">Insufficient Data</div>
            <div class="value">{len(classified['insufficient_data'])} drugs</div>
        </div>
    </div>
    """

    # Show top safety concerns
    drugs_html = ""
    all_drugs = (classified['high_risk'] + classified['moderate_risk'] +
                 classified['low_risk'] + classified['insufficient_data'])
    if all_drugs:
        drugs_html = "<ul class='drug-list'>"
        for drug_info in all_drugs[:10]:
            risk_score = drug_info.get('risk_score', 0)
            if risk_score >= 0.6:
                risk_class = "risk-high"
                risk_label = "High Risk"
            elif risk_score >= 0.3:
                risk_class = "risk-moderate"
                risk_label = "Moderate Risk"
            elif risk_score > 0:
                risk_class = "risk-low"
                risk_label = "Low Risk"
            else:
                risk_class = "risk-insufficient"
                risk_label = "Insufficient Data"

            drugs_html += f"""
            <li>
                <strong>{drug_info['drug_name']}</strong>
                <span class='risk-badge {risk_class}'>{risk_label} ({risk_score})</span>
            </li>
            """
        drugs_html += "</ul>"

    return f"""
    <div class="section">
        <h2>Safety Analysis</h2>
        <div class="info-grid">
            <div class="info-item">
                <div class="label">Drugs Analyzed</div>
                <div class="value">{summary['total_drugs_analyzed']}</div>
            </div>
            <div class="info-item">
                <div class="label">With AE Data</div>
                <div class="value">{summary['drugs_with_adverse_event_data']}</div>
            </div>
            <div class="info-item">
                <div class="label">With Boxed Warnings</div>
                <div class="value">{summary['drugs_with_boxed_warnings']}</div>
            </div>
        </div>

        <h3>Risk Classification</h3>
        {risk_cards}

        <h3>Drugs by Safety Risk</h3>
        {drugs_html}
    </div>
    """


def _render_patent_section(patent_analysis: Dict) -> str:
    """Render patent landscape section."""
    if not patent_analysis:
        return ""

    summary = patent_analysis['summary']
    all_cliffs = patent_analysis.get('all_patent_cliffs', [])

    # Patent cliffs by year
    cliffs_by_year = summary.get('cliffs_by_year', {})
    cliffs_html = ""
    if cliffs_by_year:
        cliffs_html = "<div class='chart-container'><div class='bar-chart'>"
        max_count = max(cliffs_by_year.values()) if cliffs_by_year else 1
        for year in sorted(cliffs_by_year.keys()):
            count = cliffs_by_year[year]
            width = int((count / max_count) * 100)
            cliffs_html += f"""
            <div class='bar-item'>
                <div class='label'>
                    <span>Year {year}</span>
                    <span><strong>{count}</strong> events</span>
                </div>
                <div class='bar'>
                    <div class='bar-fill' style='width: {width}%'></div>
                </div>
            </div>
            """
        cliffs_html += "</div></div>"

    # Next LOE events
    loe_html = ""
    if all_cliffs:
        loe_html = "<ul class='drug-list'>"
        for i, cliff in enumerate(all_cliffs[:5], 1):
            loe_html += f"""
            <li>
                <strong>{cliff['drug_name']}</strong><br>
                <small>{cliff['event_type']} in {cliff['years_until']} years ({cliff.get('date', 'N/A')})</small>
            </li>
            """
        loe_html += "</ul>"

    return f"""
    <div class="section">
        <h2>Patent Landscape (FDA Orange Book)</h2>
        <div class="info-grid">
            <div class="info-item">
                <div class="label">Drugs Analyzed</div>
                <div class="value">{summary['total_drugs_analyzed']}</div>
            </div>
            <div class="info-item">
                <div class="label">With Patent Data</div>
                <div class="value">{summary['drugs_with_patents']}</div>
            </div>
            <div class="info-item">
                <div class="label">LOE Events (5yr)</div>
                <div class="value">{summary['total_patent_cliffs']}</div>
            </div>
        </div>

        {('<h3>Upcoming LOE Events by Year</h3>' + cliffs_html) if cliffs_by_year else ''}
        {('<h3>Next 5 LOE Events</h3>' + loe_html) if all_cliffs else '<p>No patent cliffs identified in the next 5 years.</p>'}
    </div>
    """
