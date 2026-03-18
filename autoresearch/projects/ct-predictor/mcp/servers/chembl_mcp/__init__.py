"""ChEMBL MCP Server - Python API

Provides access to the ChEMBL database of bioactive drug-like compounds (EMBL-EBI).
2.4M+ compounds, 1.5M+ assays, 16M+ bioactivities from ChEMBL v34.
Data stays in execution environment - only summaries flow to model.

Local stdio MCP server hitting the public ChEMBL REST API.

CRITICAL CHEMBL MCP QUIRKS:
1. ChEMBL IDs: Format "CHEMBL25" (aspirin), "CHEMBL941" (imatinib)
2. Bioactivity units: IC50/EC50/Ki/Kd reported in nM or uM
3. ADMET: Rule of Five - MW<500, LogP<5, HBD<=5, HBA<=10
4. QED score: 0-1 (higher = more drug-like)
5. PSA thresholds: <140 A^2 oral bioavailability, <90 A^2 CNS penetration
6. Action types: Inhibitor, Agonist, Antagonist, Blocker, Modulator, Activator
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(method: str, **kwargs) -> Dict[str, Any]:
    """Internal: call a ChEMBL MCP tool method."""
    client = get_client('chembl-mcp-server')
    params = {k: v for k, v in kwargs.items() if v is not None}
    params['method'] = method
    return client.call_tool('chembl_info', params)


# =============================================================================
# Compound Search
# =============================================================================

def compound_search(
    query: str,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Search chemical compounds by name, SMILES structure, or ChEMBL ID

    Args:
        query: Compound name, SMILES string, or ChEMBL ID
              Examples: "aspirin", "imatinib", "CHEMBL25",
                       "CC(=O)Oc1ccccc1C(=O)O" (SMILES)

        limit: Maximum results (optional)

    Returns:
        dict: Compound search results

        Key fields per compound:
        - molecule_chembl_id: ChEMBL ID (e.g., "CHEMBL25")
        - pref_name: Preferred name
        - molecular_weight: MW in Daltons
        - alogp: Lipophilicity (LogP)
        - hba: Hydrogen bond acceptors
        - hbd: Hydrogen bond donors
        - psa: Polar surface area
        - num_ro5_violations: Rule of Five violations (0-1 preferred)
        - max_phase: Clinical development phase (4 = approved)
        - canonical_smiles: SMILES structure notation

    Examples:
        results = compound_search("imatinib")
        results = compound_search("CHEMBL941")
    """
    return _call('compound_search', query=query, limit=limit)


# =============================================================================
# Target Search
# =============================================================================

def target_search(
    query: str,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Search biological targets (proteins, genes, receptors)

    Args:
        query: Target name, gene symbol, or ChEMBL target ID
              Examples: "EGFR", "BCR-ABL", "CHEMBL203", "kinase"

        limit: Maximum results (optional)

    Returns:
        dict: Target search results

        Key fields per target:
        - target_chembl_id: Target ChEMBL ID
        - pref_name: Preferred target name
        - organism: Species (e.g., "Homo sapiens")
        - target_type: single protein, protein complex, protein family
        - components: [{accession, synonyms}]

    Examples:
        results = target_search("EGFR")
        results = target_search("kinase")
    """
    return _call('target_search', query=query, limit=limit)


# =============================================================================
# Bioactivity Data
# =============================================================================

def get_bioactivity(
    chembl_id: str,
    target_id: Optional[str] = None,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Retrieve bioactivity data for compound-target interactions

    Args:
        chembl_id: Compound ChEMBL ID (e.g., "CHEMBL25", "CHEMBL941")

        target_id: Target ChEMBL ID to filter by (optional)

        limit: Maximum results (optional)

    Returns:
        dict: Bioactivity measurements

        Key fields per activity:
        - standard_type: Measurement type (IC50, EC50, Ki, Kd)
        - standard_value: Numeric value
        - standard_units: Units (nM, uM)
        - target_pref_name: Target protein name
        - pchembl_value: -log(activity), higher = more potent
        - assay_type: Binding, Functional, ADMET

    Examples:
        results = get_bioactivity("CHEMBL941")
        results = get_bioactivity("CHEMBL25", target_id="CHEMBL2094253")
    """
    return _call('get_bioactivity', chembl_id=chembl_id, target_id=target_id, limit=limit)


# =============================================================================
# Mechanism of Action
# =============================================================================

def get_mechanism(
    chembl_id: str
) -> Dict[str, Any]:
    """
    Get mechanism of action and target binding information

    Args:
        chembl_id: Drug ChEMBL ID (e.g., "CHEMBL941", "CHEMBL25")

    Returns:
        dict: Mechanism of action data

        Key fields per mechanism:
        - mechanism_of_action: Description of how the drug works
        - action_type: Inhibitor, Agonist, Antagonist, Blocker, etc.
        - target_chembl_id: Target ID
        - max_phase: Clinical development phase
        - mechanism_refs: [{ref_type, ref_id, ref_url}]

    Examples:
        results = get_mechanism("CHEMBL941")  # imatinib
        results = get_mechanism("CHEMBL25")   # aspirin
    """
    return _call('get_mechanism', chembl_id=chembl_id)


# =============================================================================
# Drug Search
# =============================================================================

def drug_search(
    query: str,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Search drugs by indication or name

    Args:
        query: Indication, drug name, or therapeutic area
              Examples: "breast cancer", "hypertension", "imatinib"

        limit: Maximum results (optional)

    Returns:
        dict: Drug search results

        Key fields per result:
        - molecule_chembl_id: ChEMBL compound ID
        - drug_name: Drug name
        - mesh_heading / efo_term: Indication terms
        - max_phase_for_ind: Development phase for that indication

    Examples:
        results = drug_search("breast cancer")
        results = drug_search("kinase inhibitors")
    """
    return _call('drug_search', query=query, limit=limit)


# =============================================================================
# ADMET Properties
# =============================================================================

def get_admet(
    chembl_id: str
) -> Dict[str, Any]:
    """
    Get ADMET properties (Absorption, Distribution, Metabolism, Excretion, Toxicity)

    Args:
        chembl_id: Compound ChEMBL ID (e.g., "CHEMBL941", "CHEMBL25")

    Returns:
        dict: ADMET property data

        Key fields in properties:
        - alogp: Lipophilicity (optimal 1-3 for oral drugs)
        - full_mwt: MW in Daltons (<500 preferred)
        - psa: Polar Surface Area (<140 oral, <90 CNS)
        - hba: H-bond acceptors (<=10 Rule of Five)
        - hbd: H-bond donors (<=5 Rule of Five)
        - num_ro5_violations: Rule of Five violations (0-1 preferred)
        - qed_weighted: Quantitative Estimate of Drug-likeness (0-1)

    Interpretation:
        - QED > 0.67: Good drug-likeness
        - QED 0.49-0.67: Moderate
        - QED < 0.49: Poor drug-likeness
        - Ro5 violations = 0: Likely orally bioavailable

    Examples:
        results = get_admet("CHEMBL941")  # imatinib
        results = get_admet("CHEMBL25")   # aspirin
    """
    return _call('get_admet', chembl_id=chembl_id)


__all__ = [
    'compound_search',
    'target_search',
    'get_bioactivity',
    'get_mechanism',
    'drug_search',
    'get_admet',
]
