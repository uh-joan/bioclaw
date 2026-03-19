"""BRENDA MCP Server - Python API

Provides access to the BRENDA enzyme database.
Enzyme kinetics parameters: Km, kcat, Ki values for substrates and inhibitors.
"""

from mcp.client import get_client
from typing import Dict, Any, Optional


def _call(method: str, **kwargs) -> Dict[str, Any]:
    """Internal: call a BRENDA MCP tool method."""
    client = get_client('brenda')
    params = {k: v for k, v in kwargs.items() if v is not None}
    params['method'] = method
    return client.call_tool('brenda_enzymes', params)


def get_km_value(ec_number: Optional[str] = None, substrate: Optional[str] = None) -> Dict[str, Any]:
    """
    Get Km (Michaelis constant) values from BRENDA.

    Args:
        ec_number: EC enzyme number (e.g., "2.7.10.1")
        substrate: Substrate name (optional)

    Returns:
        dict: Km values for the enzyme/substrate pair
    """
    return _call('get_km_value', ec_number=ec_number, substrate=substrate)


def get_kcat_value(ec_number: Optional[str] = None) -> Dict[str, Any]:
    """
    Get kcat (turnover number) values from BRENDA.

    Args:
        ec_number: EC enzyme number (e.g., "2.7.10.1")

    Returns:
        dict: kcat values for the enzyme
    """
    return _call('get_kcat_value', ec_number=ec_number)


def get_ki_value(ec_number: Optional[str] = None) -> Dict[str, Any]:
    """
    Get Ki (inhibition constant) values from BRENDA.

    Args:
        ec_number: EC enzyme number

    Returns:
        dict: Ki values for the enzyme
    """
    return _call('get_ki_value', ec_number=ec_number)


__all__ = [
    'get_km_value',
    'get_kcat_value',
    'get_ki_value',
]
