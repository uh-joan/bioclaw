"""Open Targets MCP Server - Python API

Provides Python functions for Open Targets genetic evidence and drug-target-disease data.
Data stays in execution environment - only summaries flow to model.

CRITICAL OPEN TARGETS QUIRKS:
1. Gene IDs: Use Ensembl gene IDs (e.g., "ENSG00000012048")
2. Disease IDs: PRIMARY format is MONDO (e.g., "MONDO_0005148"), also supports EFO (e.g., "EFO_0000305") - validated in testing
3. Gene symbols: Search with approved symbols (GLP1R, DPP4, BRCA1)
4. minScore filter: 0.5+ for strong associations, 0.3+ for moderate
5. Evidence types: Check datatypeScores for genetic, literature, somatic, etc.
6. Response format: JSON with nested association data
7. TOKEN USAGE (measured): search ~180-250 tokens, associations ~1,350 tokens, summaries ~2,550 tokens, details ~160-220 tokens
8. Size parameter: May be overridden by score filtering (requested 10, got 25 when minScore applied)
9. Detail endpoints: Return basic info; tractability/safety data optional/not always available
10. Both MONDO and EFO IDs appear in association results (validated in testing)
"""

from mcp.client import get_client
from typing import Dict, Any, Optional, Union


def search_targets(
    query: str,
    size: int = 10
) -> Dict[str, Any]:
    """
    Search for therapeutic targets by gene symbol or name

    Args:
        query: Gene symbol, name, or description
               Examples: "GLP1R", "BRCA1", "DPP4", "insulin receptor"

        size: Maximum results to return (1-500, default: 10)

    Returns:
        dict: Open Targets API response with target matches

        Key fields:
        - id: Ensembl gene ID (use for get_target_details)
        - approvedSymbol: Official gene symbol
        - approvedName: Full gene name
        - biotype: Gene type (protein_coding, etc.)

    Examples:
        # Search for GLP-1 receptor
        results = search_targets(query="GLP1R", size=5)

        # Extract Ensembl IDs
        for target in results.get('data', []):
            ensembl_id = target.get('id')
            symbol = target.get('approvedSymbol')
            name = target.get('approvedName')
            print(f"{symbol} ({ensembl_id}): {name}")

        # Search by description
        results = search_targets(query="insulin receptor", size=10)
    """
    client = get_client('opentargets-mcp-server')

    params = {
        'method': 'search_targets',
        'query': query,
        'size': size
    }

    return client.call_tool('opentargets_info', params)


def search_diseases(
    query: str,
    size: int = 10
) -> Dict[str, Any]:
    """
    Search for diseases by name or synonym

    Args:
        query: Disease name, synonym, or description
               Examples: "diabetes", "obesity", "Alzheimer", "breast cancer"

        size: Maximum results to return (1-500, default: 10)

    Returns:
        dict: Open Targets API response with disease matches

        Key fields:
        - id: Disease ID - MONDO format (e.g., "MONDO_0005148") or EFO format (e.g., "EFO_0000305")
        - name: Disease name
        - description: Disease description
        - synonyms: Alternative names (may not be present in all responses)

    Examples:
        # Search for diabetes
        results = search_diseases(query="diabetes", size=5)

        # Extract EFO IDs
        for disease in results.get('data', []):
            efo_id = disease.get('id')
            name = disease.get('name')
            print(f"{name} ({efo_id})")

        # Search for cancer types
        results = search_diseases(query="breast cancer", size=10)
    """
    client = get_client('opentargets-mcp-server')

    params = {
        'method': 'search_diseases',
        'query': query,
        'size': size
    }

    return client.call_tool('opentargets_info', params)


def get_target_disease_associations(
    targetId: Optional[str] = None,
    diseaseId: Optional[str] = None,
    minScore: float = 0.0,
    size: int = 50
) -> Dict[str, Any]:
    """
    Get target-disease associations with genetic evidence

    Args:
        targetId: Ensembl gene ID (e.g., "ENSG00000012048")
                 Get from search_targets()

        diseaseId: Disease ID - MONDO (e.g., "MONDO_0005148") or EFO (e.g., "EFO_0000305")
                  Get from search_diseases()

        minScore: Minimum association score (0-1)
                 Recommended thresholds:
                 - 0.5+: Strong associations (high confidence)
                 - 0.3-0.5: Moderate associations
                 - 0.0-0.3: Weak associations
                 Default: 0.0 (all associations)

        size: Maximum associations to return (1-500, default: 50)

    Returns:
        dict: Association data with evidence scores

        Key fields:
        - targetId: Ensembl gene ID
        - diseaseId: EFO disease ID
        - score: Overall association score (0-1)
        - datatypeScores: Evidence by type (genetic, literature, somatic, etc.)

    Examples:
        # Get all associations for a target
        results = get_target_disease_associations(
            targetId="ENSG00000012048",
            minScore=0.5,
            size=50
        )

        # Process associations
        for assoc in results.get('data', []):
            disease_id = assoc.get('diseaseId')
            score = assoc.get('score')
            datatypes = assoc.get('datatypeScores', {})
            print(f"Disease: {disease_id}, Score: {score:.2f}")
            print(f"  Genetic evidence: {datatypes.get('genetic_association', 0):.2f}")

        # Get associations for a specific target-disease pair
        results = get_target_disease_associations(
            targetId="ENSG00000012048",
            diseaseId="EFO_0000305",
            minScore=0.0
        )

        # Get all diseases for a target (strong evidence only)
        results = get_target_disease_associations(
            targetId="ENSG00000012048",
            minScore=0.5,
            size=100
        )
    """
    client = get_client('opentargets-mcp-server')

    params = {
        'method': 'get_target_disease_associations',
        'minScore': minScore,
        'size': size
    }

    if targetId:
        params['targetId'] = targetId
    if diseaseId:
        params['diseaseId'] = diseaseId

    return client.call_tool('opentargets_info', params)


def get_disease_targets_summary(
    diseaseId: str,
    minScore: float = 0.0,
    size: int = 50
) -> Dict[str, Any]:
    """
    Get overview of all targets associated with a disease

    Args:
        diseaseId: Disease ID - MONDO (e.g., "MONDO_0005148") or EFO (e.g., "EFO_0000305")
                  Get from search_diseases()

        minScore: Minimum association score (0-1)
                 See get_target_disease_associations for thresholds

        size: Maximum targets to return (1-500, default: 50)

    Returns:
        dict: Summary of disease-target associations

    Examples:
        # Get top targets for diabetes
        results = get_disease_targets_summary(
            diseaseId="EFO_0000305",
            minScore=0.5,
            size=20
        )

        # Rank targets by evidence
        targets = []
        for assoc in results.get('data', []):
            target_id = assoc.get('targetId')
            score = assoc.get('score')
            targets.append((target_id, score))

        targets.sort(key=lambda x: x[1], reverse=True)
        print("Top 10 targets:")
        for target_id, score in targets[:10]:
            print(f"  {target_id}: {score:.2f}")
    """
    client = get_client('opentargets-mcp-server')

    params = {
        'method': 'get_disease_targets_summary',
        'diseaseId': diseaseId,
        'minScore': minScore,
        'size': size
    }

    return client.call_tool('opentargets_info', params)


def get_target_details(
    id: str
) -> Dict[str, Any]:
    """
    Get comprehensive information about a specific target

    Args:
        id: Ensembl gene ID (e.g., "ENSG00000012048")
            Get from search_targets()

    Returns:
        dict: Detailed target information

        Key fields (always present):
        - id: Ensembl gene ID
        - approvedSymbol: Gene symbol
        - approvedName: Full gene name
        - biotype: Gene type

        Optional fields (may not be present):
        - proteinAnnotations: Protein function data
        - safetyLiabilities: Known safety issues
        - tractability: Druggability assessment

    Examples:
        # Get details for GLP1R
        details = get_target_details(id="ENSG00000012048")

        # Extract key information
        symbol = details.get('approvedSymbol')
        name = details.get('approvedName')
        biotype = details.get('biotype')

        print(f"Target: {symbol}")
        print(f"Name: {name}")
        print(f"Type: {biotype}")

        # Check druggability
        tractability = details.get('tractability', {})
        small_molecule = tractability.get('smallmolecule', {})
        antibody = tractability.get('antibody', {})

        print(f"Small molecule tractability: {small_molecule.get('top_category')}")
        print(f"Antibody tractability: {antibody.get('top_category')}")

        # Check safety
        safety = details.get('safetyLiabilities', [])
        if safety:
            print(f"Safety concerns: {len(safety)} identified")
    """
    client = get_client('opentargets-mcp-server')

    params = {
        'method': 'get_target_details',
        'id': id
    }

    return client.call_tool('opentargets_info', params)


def get_disease_details(
    id: str
) -> Dict[str, Any]:
    """
    Get comprehensive information about a specific disease

    Args:
        id: EFO disease ID (e.g., "EFO_0000305")
            Get from search_diseases()

    Returns:
        dict: Detailed disease information

        Key fields:
        - id: Disease ID (MONDO or EFO format)
        - name: Disease name
        - description: Disease description
        - synonyms: Alternative names (optional - may not be present)
        - therapeuticAreas: Disease classification (optional - may not be present)

    Examples:
        # Get details for diabetes
        details = get_disease_details(id="EFO_0000305")

        # Extract information
        name = details.get('name')
        description = details.get('description')
        synonyms = details.get('synonyms', [])

        print(f"Disease: {name}")
        print(f"Description: {description}")
        print(f"Also known as: {', '.join(synonyms)}")
    """
    client = get_client('opentargets-mcp-server')

    params = {
        'method': 'get_disease_details',
        'id': id
    }

    return client.call_tool('opentargets_info', params)


__all__ = [
    'search_targets',
    'search_diseases',
    'get_target_disease_associations',
    'get_disease_targets_summary',
    'get_target_details',
    'get_disease_details'
]
