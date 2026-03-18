"""DrugBank MCP Server - Python API

Provides comprehensive pharmaceutical data from DrugBank database (13,000+ drugs).
Access drug information, interactions, targets, pathways, and market products.
Data stays in execution environment - only summaries flow to model.

CRITICAL DRUGBANK MCP QUIRKS:
1. DrugBank IDs: Format "DB00945" (aspirin), "DB00316" (acetaminophen)
2. Drug search: Fuzzy matching by name, indication, or target
3. ATC codes: Anatomical Therapeutic Chemical classification (e.g., "N02BA01")
4. SMILES/InChI: Chemical structure notation for structure search
5. Half-life: Reported in hours
6. Targets: Proteins, enzymes, transporters, carriers
7. Cross-references: Links to PubChem, ChEMBL, KEGG, etc.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def drugbank_info(
    method: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Unified DrugBank data access function

    Args:
        method: Operation to perform
        **kwargs: Method-specific parameters

    Returns:
        dict: DrugBank API response
    """
    client = get_client('drugbank')

    params = {'method': method}
    params.update(kwargs)

    return client.call_tool('drugbank_info', params)


# =============================================================================
# Drug Search
# =============================================================================

def search_by_name(
    query: str,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Search drugs by name (fuzzy matching)

    Args:
        query: Drug name to search
              Examples: "aspirin", "metformin", "semaglutide"

        limit: Maximum results (default: 20)

    Returns:
        dict: Drug search results

        Key fields:
        - drugbank_id: DrugBank ID (e.g., "DB00945")
        - name: Drug name
        - type: small molecule, biotech, etc.
        - groups: approved, investigational, etc.
        - description: Drug description

    Examples:
        # Search for aspirin
        results = search_by_name(query="aspirin")

        for drug in results.get('data', []):
            db_id = drug.get('drugbank_id')
            name = drug.get('name')
            groups = drug.get('groups', [])
            print(f"{db_id}: {name} ({', '.join(groups)})")

        # Search for GLP-1 drugs
        results = search_by_name(query="semaglutide")

        # Fuzzy search
        results = search_by_name(query="tylenol", limit=10)
    """
    return drugbank_info(method='search_by_name', query=query, limit=limit)


def search_by_indication(
    query: str,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Find drugs by medical indication

    Args:
        query: Indication/condition to search
              Examples: "pain", "diabetes", "hypertension", "cancer"

        limit: Maximum results (default: 20)

    Returns:
        dict: Drugs with matching indications

    Examples:
        # Find diabetes drugs
        results = search_by_indication(query="diabetes")

        for drug in results.get('data', []):
            name = drug.get('name')
            indication = drug.get('indication')
            print(f"{name}: {indication[:100]}...")

        # Find pain medications
        results = search_by_indication(query="pain", limit=50)

        # Find cancer drugs
        results = search_by_indication(query="cancer")
    """
    return drugbank_info(method='search_by_indication', query=query, limit=limit)


def search_by_target(
    target: str,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Find drugs by target protein/enzyme

    Args:
        target: Target protein/enzyme name
               Examples: "COX-2", "ACE", "HMG-CoA reductase", "GLP-1 receptor"

        limit: Maximum results (default: 20)

    Returns:
        dict: Drugs targeting the specified protein

    Examples:
        # Find COX-2 inhibitors
        results = search_by_target(target="COX-2")

        for drug in results.get('data', []):
            name = drug.get('name')
            db_id = drug.get('drugbank_id')
            print(f"{name} ({db_id})")

        # Find ACE inhibitors
        results = search_by_target(target="ACE")

        # Find GLP-1 receptor agonists
        results = search_by_target(target="GLP-1 receptor")
    """
    return drugbank_info(method='search_by_target', target=target, limit=limit)


def search_by_category(
    category: str,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Search drugs by category

    Args:
        category: Drug category
                 Examples: "Anti-inflammatory", "Antidiabetic", "Antihypertensive"

        limit: Maximum results (default: 20)

    Returns:
        dict: Drugs in the specified category

    Examples:
        # Find anti-inflammatory drugs
        results = search_by_category(category="Anti-inflammatory")

        for drug in results.get('data', []):
            name = drug.get('name')
            categories = drug.get('categories', [])
            print(f"{name}: {categories}")

        # Find antidiabetic drugs
        results = search_by_category(category="Antidiabetic", limit=50)
    """
    return drugbank_info(method='search_by_category', category=category, limit=limit)


def search_by_atc_code(
    code: str,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Search by ATC (Anatomical Therapeutic Chemical) classification code

    Args:
        code: ATC code (partial or complete)
             Examples: "N02BA" (salicylic acid), "A10B" (blood glucose lowering)

        limit: Maximum results (default: 20)

    Returns:
        dict: Drugs with matching ATC code

    Examples:
        # Find salicylic acid derivatives
        results = search_by_atc_code(code="N02BA")

        for drug in results.get('data', []):
            name = drug.get('name')
            atc = drug.get('atc_codes', [])
            print(f"{name}: {atc}")

        # Find oral blood glucose lowering drugs
        results = search_by_atc_code(code="A10B")
    """
    return drugbank_info(method='search_by_atc_code', code=code, limit=limit)


def search_by_halflife(
    min_hours: Optional[float] = None,
    max_hours: Optional[float] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Find drugs by elimination half-life range (in hours)

    Args:
        min_hours: Minimum half-life in hours

        max_hours: Maximum half-life in hours

        limit: Maximum results (default: 20)

    Returns:
        dict: Drugs within half-life range

    Examples:
        # Find long-acting drugs (12-48 hour half-life)
        results = search_by_halflife(min_hours=12, max_hours=48)

        for drug in results.get('data', []):
            name = drug.get('name')
            halflife = drug.get('half_life')
            print(f"{name}: {halflife}")

        # Short-acting drugs (< 4 hours)
        results = search_by_halflife(max_hours=4)

        # Very long-acting drugs (> 24 hours)
        results = search_by_halflife(min_hours=24)
    """
    params = {
        'limit': limit
    }

    if min_hours is not None:
        params['min_hours'] = min_hours
    if max_hours is not None:
        params['max_hours'] = max_hours

    return drugbank_info(method='search_by_halflife', **params)


def search_by_structure(
    smiles: Optional[str] = None,
    inchi: Optional[str] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Search by chemical structure (SMILES or InChI)

    Args:
        smiles: SMILES notation (optional)
               Example: "CC(=O)Oc1ccccc1C(=O)O" (aspirin)

        inchi: InChI notation (optional)

        limit: Maximum results (default: 20)

    Returns:
        dict: Drugs with similar structure

    Examples:
        # Search by SMILES (aspirin)
        results = search_by_structure(
            smiles="CC(=O)Oc1ccccc1C(=O)O"
        )

        for drug in results.get('data', []):
            name = drug.get('name')
            smiles = drug.get('smiles')
            print(f"{name}: {smiles}")

        # Search by InChI
        results = search_by_structure(
            inchi="InChI=1S/C9H8O4/c1-6(10)..."
        )
    """
    params = {
        'limit': limit
    }

    if smiles:
        params['smiles'] = smiles
    if inchi:
        params['inchi'] = inchi

    return drugbank_info(method='search_by_structure', **params)


# =============================================================================
# Drug Details
# =============================================================================

def get_drug_details(
    drugbank_id: str
) -> Dict[str, Any]:
    """
    Get complete drug information by DrugBank ID

    Args:
        drugbank_id: DrugBank ID (e.g., "DB00945")

    Returns:
        dict: Complete drug information

        Key fields:
        - drugbank_id: DrugBank ID
        - name: Drug name
        - type: Drug type (small molecule, biotech)
        - groups: Status (approved, investigational, etc.)
        - description: Drug description
        - indication: Approved indications
        - pharmacodynamics: How drug works
        - mechanism_of_action: Molecular mechanism
        - toxicity: Toxicity information
        - metabolism: Metabolic pathways
        - half_life: Elimination half-life
        - route_of_elimination: Excretion route
        - volume_of_distribution: Vd
        - clearance: Drug clearance
        - smiles: SMILES notation
        - inchi: InChI notation
        - molecular_weight: MW
        - categories: Drug categories
        - atc_codes: ATC classification

    Examples:
        # Get aspirin details
        details = get_drug_details(drugbank_id="DB00945")

        drug = details.get('data', {})
        print(f"Name: {drug.get('name')}")
        print(f"Type: {drug.get('type')}")
        print(f"Groups: {drug.get('groups')}")
        print(f"Half-life: {drug.get('half_life')}")
        print(f"\\nIndication:")
        print(drug.get('indication'))
        print(f"\\nMechanism:")
        print(drug.get('mechanism_of_action'))

        # Get semaglutide details
        details = get_drug_details(drugbank_id="DB13928")
    """
    return drugbank_info(method='get_drug_details', drugbank_id=drugbank_id)


# =============================================================================
# Drug Interactions
# =============================================================================

def get_drug_interactions(
    drugbank_id: str
) -> Dict[str, Any]:
    """
    Get drug-drug interactions

    Args:
        drugbank_id: DrugBank ID (e.g., "DB00945")

    Returns:
        dict: Drug interaction data

        Key fields:
        - drugbank_id: Reference drug
        - interactions: List of interactions
          - drug: Interacting drug name
          - drugbank_id: Interacting drug ID
          - description: Interaction description
          - severity: Interaction severity

    Examples:
        # Get aspirin interactions
        interactions = get_drug_interactions(drugbank_id="DB00945")

        for interaction in interactions.get('data', []):
            drug = interaction.get('drug')
            description = interaction.get('description')
            severity = interaction.get('severity')
            print(f"{drug} ({severity}): {description[:100]}...")

        # Count interactions
        data = interactions.get('data', [])
        print(f"\\nTotal interactions: {len(data)}")
    """
    return drugbank_info(method='get_drug_interactions', drugbank_id=drugbank_id)


# =============================================================================
# Pathways
# =============================================================================

def get_pathways(
    drugbank_id: str
) -> Dict[str, Any]:
    """
    Get metabolic pathways for a drug

    Args:
        drugbank_id: DrugBank ID (e.g., "DB00945")

    Returns:
        dict: Metabolic pathway data

        Key fields:
        - drugbank_id: Drug ID
        - pathways: List of pathways
          - name: Pathway name
          - smpdb_id: SMPDB pathway ID
          - category: Pathway category
          - enzymes: Enzymes involved

    Examples:
        # Get aspirin pathways
        pathways = get_pathways(drugbank_id="DB00945")

        for pathway in pathways.get('data', []):
            name = pathway.get('name')
            category = pathway.get('category')
            enzymes = pathway.get('enzymes', [])
            print(f"{name} ({category})")
            print(f"  Enzymes: {', '.join(enzymes)}")
    """
    return drugbank_info(method='get_pathways', drugbank_id=drugbank_id)


# =============================================================================
# Market Products
# =============================================================================

def get_products(
    drugbank_id: str,
    country: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get market products for a drug

    Args:
        drugbank_id: DrugBank ID (e.g., "DB00945")

        country: Country code filter (optional)
                Examples: "US", "CA", "EU"

    Returns:
        dict: Market product data

        Key fields:
        - drugbank_id: Drug ID
        - products: List of products
          - name: Product/brand name
          - labeller: Manufacturer
          - dosage_form: Form (tablet, injection, etc.)
          - strength: Dosage strength
          - route: Administration route
          - country: Country

    Examples:
        # Get all aspirin products
        products = get_products(drugbank_id="DB00945")

        for product in products.get('data', [])[:10]:
            name = product.get('name')
            labeller = product.get('labeller')
            strength = product.get('strength')
            form = product.get('dosage_form')
            print(f"{name} by {labeller}: {strength} {form}")

        # US products only
        products = get_products(drugbank_id="DB00945", country="US")
    """
    params = {
        'drugbank_id': drugbank_id
    }

    if country:
        params['country'] = country

    return drugbank_info(method='get_products', **params)


# =============================================================================
# External Identifiers
# =============================================================================

def get_external_identifiers(
    drugbank_id: str
) -> Dict[str, Any]:
    """
    Get cross-database identifiers (PubChem, ChEMBL, KEGG, etc.)

    Args:
        drugbank_id: DrugBank ID (e.g., "DB00945")

    Returns:
        dict: External identifier data

        Key fields:
        - drugbank_id: DrugBank ID
        - identifiers: Dict of external IDs
          - pubchem: PubChem CID
          - chembl: ChEMBL ID
          - kegg: KEGG Drug ID
          - chebi: ChEBI ID
          - pdb: PDB ligand ID
          - uniprot: UniProt IDs (for biologics)

    Examples:
        # Get external IDs for aspirin
        ids = get_external_identifiers(drugbank_id="DB00945")

        data = ids.get('data', {})
        print(f"DrugBank: {data.get('drugbank_id')}")
        print(f"PubChem: {data.get('pubchem')}")
        print(f"ChEMBL: {data.get('chembl')}")
        print(f"KEGG: {data.get('kegg')}")
    """
    return drugbank_info(method='get_external_identifiers', drugbank_id=drugbank_id)


# =============================================================================
# Similar Drugs
# =============================================================================

def get_similar_drugs(
    drugbank_id: str,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Find drugs similar to a given drug (by shared targets, categories, ATC codes)

    Args:
        drugbank_id: DrugBank ID (e.g., "DB00945")

        limit: Maximum results (default: 20)

    Returns:
        dict: Similar drugs

        Key fields:
        - reference: Reference drug info
        - similar: List of similar drugs
          - drugbank_id: Similar drug ID
          - name: Drug name
          - similarity_type: How it's similar (target, category, ATC)
          - shared_features: Shared characteristics

    Examples:
        # Find drugs similar to aspirin
        similar = get_similar_drugs(drugbank_id="DB00945")

        for drug in similar.get('data', []):
            name = drug.get('name')
            sim_type = drug.get('similarity_type')
            shared = drug.get('shared_features', [])
            print(f"{name} ({sim_type}): {shared}")
    """
    return drugbank_info(
        method='get_similar_drugs',
        drugbank_id=drugbank_id,
        limit=limit
    )


# =============================================================================
# Carriers and Transporters
# =============================================================================

def search_by_carrier(
    carrier: str,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Find drugs by carrier protein (proteins that transport drugs in the body)

    Args:
        carrier: Carrier protein name
                Examples: "Albumin", "Alpha-1-acid glycoprotein"

        limit: Maximum results (default: 20)

    Returns:
        dict: Drugs carried by the specified protein

    Examples:
        # Find drugs carried by albumin
        results = search_by_carrier(carrier="Albumin")

        for drug in results.get('data', []):
            name = drug.get('name')
            binding = drug.get('carrier_binding')
            print(f"{name}: {binding}")
    """
    return drugbank_info(method='search_by_carrier', carrier=carrier, limit=limit)


def search_by_transporter(
    transporter: str,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Find drugs by transporter protein (membrane proteins that move drugs across cells)

    Args:
        transporter: Transporter protein name
                    Examples: "P-glycoprotein", "OATP1B1", "BCRP"

        limit: Maximum results (default: 20)

    Returns:
        dict: Drugs transported by the specified protein

    Examples:
        # Find P-glycoprotein substrates
        results = search_by_transporter(transporter="P-glycoprotein")

        for drug in results.get('data', []):
            name = drug.get('name')
            action = drug.get('transporter_action')  # substrate, inhibitor, inducer
            print(f"{name}: {action}")

        # Find OATP1B1 substrates
        results = search_by_transporter(transporter="OATP1B1")
    """
    return drugbank_info(method='search_by_transporter', transporter=transporter, limit=limit)


# =============================================================================
# Salt Forms
# =============================================================================

def get_salts(
    drugbank_id: str
) -> Dict[str, Any]:
    """
    Get salt forms for a drug (e.g., hydrochloride, sulfate)

    Args:
        drugbank_id: DrugBank ID (e.g., "DB00945")

    Returns:
        dict: Salt form data

        Key fields:
        - drugbank_id: Parent drug ID
        - salts: List of salt forms
          - name: Salt name (e.g., "Metformin hydrochloride")
          - drugbank_salt_id: Salt ID
          - cas_number: CAS registry number
          - inchi: InChI notation

    Examples:
        # Get metformin salts
        salts = get_salts(drugbank_id="DB00331")

        for salt in salts.get('data', []):
            name = salt.get('name')
            cas = salt.get('cas_number')
            print(f"{name} (CAS: {cas})")
    """
    return drugbank_info(method='get_salts', drugbank_id=drugbank_id)


__all__ = [
    'drugbank_info',
    # Search
    'search_by_name',
    'search_by_indication',
    'search_by_target',
    'search_by_category',
    'search_by_atc_code',
    'search_by_halflife',
    'search_by_structure',
    # Details
    'get_drug_details',
    'get_drug_interactions',
    'get_pathways',
    'get_products',
    'get_external_identifiers',
    'get_similar_drugs',
    # Carriers/Transporters
    'search_by_carrier',
    'search_by_transporter',
    # Salts
    'get_salts'
]
