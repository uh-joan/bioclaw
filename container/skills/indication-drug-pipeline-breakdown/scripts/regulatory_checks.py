"""Regulatory approval checking utilities for FDA and EMA."""
import re
import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any

# All MCP functions are now accessed via mcp_funcs parameter
# No direct imports from mcp.servers.* allowed


def _fetch_fda_label_direct(drug_name: str, limit: int = 3) -> list:
    """
    Fetch FDA label data directly using urllib (no external dependencies).

    Returns list of label results with indications_and_usage field.
    """
    try:
        base_url = "https://api.fda.gov/drug/label.json"
        search_query = f'openfda.brand_name:"{drug_name}" OR openfda.generic_name:"{drug_name}"'

        params = urllib.parse.urlencode({
            'search': search_query,
            'limit': limit
        })

        url = f"{base_url}?{params}"

        req = urllib.request.Request(url, headers={'User-Agent': 'Python/urllib'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('results', [])
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        return []
    except Exception:
        return []


def check_fda_approval_for_indication(normalized_name: str, indication_synonyms: list) -> dict:
    """
    Check if a drug is FDA approved for a SPECIFIC indication.

    Uses direct FDA API with urllib to get indications_and_usage,
    then performs client-side matching (same pattern as EMA check).

    Args:
        normalized_name: Drug name to check
        indication_synonyms: List of indication terms to match (e.g., ['als', 'amyotrophic lateral sclerosis'])

    Returns:
        dict with drug name, approved status, and matched indication (if any)
    """
    try:
        # Use just the normalized name directly - FDA API handles variations
        # Skip PubChem synonym expansion to avoid slow MCP calls
        results = _fetch_fda_label_direct(normalized_name, limit=3)

        if not results:
            return {'name': normalized_name, 'approved': False, 'indication_match': None}

        # Check each label's indications for our indication (client-side matching)
        for result in results:
            indications = result.get('indications_and_usage', [])
            if isinstance(indications, list):
                indications_text = ' '.join(indications).lower()
            else:
                indications_text = str(indications).lower()

            if not indications_text:
                continue

            # Check if any synonym appears in the indications text
            for synonym in indication_synonyms:
                # Use word boundary matching to avoid partial matches
                pattern = r'\b' + re.escape(synonym.lower()) + r'\b'
                if re.search(pattern, indications_text):
                    return {
                        'name': normalized_name,
                        'approved': True,
                        'indication_match': synonym
                    }

        return {'name': normalized_name, 'approved': False, 'indication_match': None}

    except Exception as e:
        return {'name': normalized_name, 'approved': False, 'indication_match': None}


def check_fda_approval(normalized_name: str, mcp_funcs: Dict[str, Any] = None) -> dict:
    """
    Check FDA approval for a drug name (any indication). Used for parallel processing.
    DEPRECATED: Use check_fda_approval_for_indication for indication-specific checks.

    Returns:
        dict with drug name and approval status
    """
    if not mcp_funcs:
        return {'name': normalized_name, 'approved': False}

    try:
        fda_lookup = mcp_funcs.get('fda_lookup')
        if not fda_lookup:
            return {'name': normalized_name, 'approved': False}

        # Strategy 1: Search by generic name
        fda_result = fda_lookup(search_term=normalized_name, search_type='general', count='openfda.generic_name.exact', limit=1)
        data = fda_result.get('data', {})
        if data.get('results') and len(data.get('results', [])) > 0:
            return {'name': normalized_name, 'approved': True}

        # Strategy 2: Search by brand name
        fda_result = fda_lookup(search_term=normalized_name, search_type='general', count='openfda.brand_name.exact', limit=1)
        data = fda_result.get('data', {})
        if data.get('results') and len(data.get('results', [])) > 0:
            return {'name': normalized_name, 'approved': True}

        # Strategy 3: General label search (using count pattern to avoid token overflow)
        fda_result = fda_lookup(
            search_term=normalized_name,
            search_type='label',
            count='openfda.brand_name.exact',
            limit=1
        )
        data = fda_result.get('data', {})
        if data.get('results') and len(data.get('results', [])) > 0:
            return {'name': normalized_name, 'approved': True}

        return {'name': normalized_name, 'approved': False}
    except:
        return {'name': normalized_name, 'approved': False}


def check_ema_approval(normalized_name: str, mcp_funcs: Dict[str, Any] = None) -> dict:
    """
    Check EMA approval for a drug name. Used for parallel processing.
    DEPRECATED: Use check_ema_approval_for_indication for indication-specific checks.

    Returns:
        dict with drug name and approval status
    """
    if not mcp_funcs:
        return {'name': normalized_name, 'approved': False}

    try:
        ema_search = mcp_funcs.get('ema_search')
        if not ema_search:
            return {'name': normalized_name, 'approved': False}

        ema_result = ema_search(method='search_medicines', active_substance=normalized_name, status="Authorised", limit=1)
        # EMA API returns 'results' not 'data'
        results = ema_result.get('results', [])
        if results and len(results) > 0:
            return {'name': normalized_name, 'approved': True}
        return {'name': normalized_name, 'approved': False}
    except:
        return {'name': normalized_name, 'approved': False}


def check_ema_approval_for_indication(normalized_name: str, indication_synonyms: list, mcp_funcs: Dict[str, Any] = None) -> dict:
    """
    Check if a drug is EMA approved for a SPECIFIC indication.

    Queries EMA medicines API and checks if any indication synonym appears
    in the therapeutic_indication field.

    Args:
        normalized_name: Drug name to check
        indication_synonyms: List of indication terms to match (e.g., ['als', 'amyotrophic lateral sclerosis'])

    Returns:
        dict with drug name, approved status, and matched indication (if any)
    """
    if not mcp_funcs:
        return {'name': normalized_name, 'approved': False, 'indication_match': None}

    try:
        ema_search = mcp_funcs.get('ema_search')
        if not ema_search:
            return {'name': normalized_name, 'approved': False, 'indication_match': None}

        # Use just the normalized name - skip slow PubChem synonym expansion
        ema_result = ema_search(method='search_medicines', active_substance=normalized_name, limit=10)
        results = ema_result.get('results', [])

        if not results:
            return {'name': normalized_name, 'approved': False, 'indication_match': None}

        # Check each medicine's therapeutic indication for our indication
        for result in results:
            # Skip suspended/withdrawn/refused medicines
            status = (result.get('medicine_status', '') or '').lower()
            if status in ('suspended', 'withdrawn', 'refused', 'revoked'):
                continue

            # EMA provides therapeutic_indication field with approved uses
            indication_text = result.get('therapeutic_indication', '') or ''
            indication_lower = indication_text.lower()

            # Also check therapeutic_area if available
            therapeutic_area = result.get('therapeutic_area', '') or ''
            combined_text = (indication_lower + ' ' + therapeutic_area.lower()).strip()

            if not combined_text:
                continue

            # Check if any synonym appears in the indication text
            for synonym in indication_synonyms:
                # Use word boundary matching to avoid partial matches
                pattern = r'\b' + re.escape(synonym.lower()) + r'\b'
                if re.search(pattern, combined_text):
                    return {
                        'name': normalized_name,
                        'approved': True,
                        'indication_match': synonym
                    }

        # Drug found in EMA but not approved for this indication
        return {'name': normalized_name, 'approved': False, 'indication_match': None}

    except Exception as e:
        return {'name': normalized_name, 'approved': False, 'indication_match': None}
