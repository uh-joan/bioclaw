"""MCP Server Python APIs

All available MCP server wrappers for healthcare, regulatory, and financial data.
Import specific servers or use the unified interfaces.

Healthcare & Drug Data:
- ct_gov_mcp: ClinicalTrials.gov clinical trials
- fda_mcp: FDA drug labels, adverse events, recalls
- pubmed_mcp: PubMed biomedical literature
- pubchem_mcp: PubChem chemical compounds
- who_mcp: WHO global health data
- cdc_mcp: CDC public health surveillance
- ema_mcp: European Medicines Agency
- opentargets_mcp: Open Targets drug-disease associations
- drugbank_mcp: DrugBank comprehensive drug database
- formulary_mcp: US health insurance formulary coverage
- nlm_codes_mcp: NLM clinical codes (ICD-10, HCPCS, NPI)
- chembl_mcp: ChEMBL bioactive compounds (EMBL-EBI)
- biorxiv_mcp: bioRxiv/medRxiv preprints (Cold Spring Harbor)

Government Healthcare Programs:
- medicare_mcp: CMS Medicare provider data, Part D, hospital quality
- medicaid_mcp: Medicaid enrollment, NADAC pricing, drug rebates

Financial & Regulatory:
- sec_edgar_mcp: SEC EDGAR company filings
- financials_mcp: Financial data and FRED economic indicators
- uspto_patents_mcp: USPTO and Google patent data
- eu_filings_mcp: European ESEF filings, UK Companies House
- asia_filings_mcp: Japan EDINET and Korea DART filings
- datacommons_mcp: Google Data Commons indicators

Example usage:
    from mcp.servers import fda_mcp, medicare_mcp

    # Search FDA drug labels
    results = fda_mcp.search_drug_labels(drug_name="semaglutide")

    # Get Medicare hospital quality
    rating = medicare_mcp.get_hospital_star_rating(state="CA")
"""

# Healthcare & Drug Data
from . import ct_gov_mcp
from . import fda_mcp
from . import pubmed_mcp
from . import pubchem_mcp
from . import who_mcp
from . import cdc_mcp
from . import ema_mcp
from . import opentargets_mcp
from . import drugbank_mcp
from . import formulary_mcp
from . import nlm_codes_mcp
from . import chembl_mcp
from . import biorxiv_mcp

# Government Healthcare Programs
from . import medicare_mcp
from . import medicaid_mcp

# Financial & Regulatory
from . import sec_edgar_mcp
from . import financials_mcp
from . import uspto_patents_mcp
from . import eu_filings_mcp
from . import asia_filings_mcp
from . import datacommons_mcp

__all__ = [
    # Healthcare & Drug Data
    'ct_gov_mcp',
    'fda_mcp',
    'pubmed_mcp',
    'pubchem_mcp',
    'who_mcp',
    'cdc_mcp',
    'ema_mcp',
    'opentargets_mcp',
    'drugbank_mcp',
    'formulary_mcp',
    'nlm_codes_mcp',
    'chembl_mcp',
    'biorxiv_mcp',
    # Government Healthcare Programs
    'medicare_mcp',
    'medicaid_mcp',
    # Financial & Regulatory
    'sec_edgar_mcp',
    'financials_mcp',
    'uspto_patents_mcp',
    'eu_filings_mcp',
    'asia_filings_mcp',
    'datacommons_mcp',
]
