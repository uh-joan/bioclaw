"""DuckDB-backed provider-level Medicaid spending queries.

Reads the HHS provider-spending Parquet file (2018-2024, ~2.9 GB) using DuckDB.
DuckDB reads only the columns/rows needed per query (~50-500 MB memory, 50-500ms).

Parquet location: .cache/medicaid/medicaid-provider-spending.parquet
Override via MEDICAID_PROVIDER_SPENDING_PATH env var.

HCPCS lookup: .cache/medicaid/hcpcs_lookup.json (built from CMS Level II + PFS CPT)
Override via HCPCS_LOOKUP_PATH env var.

NPPES slim: .cache/medicaid/nppes_slim.parquet (provider identity from CMS NPPES)
Override via NPPES_SLIM_PATH env var.

Schema (7 columns):
  BILLING_PROVIDER_NPI_NUM   VARCHAR
  SERVICING_PROVIDER_NPI_NUM VARCHAR
  HCPCS_CODE                 VARCHAR
  CLAIM_FROM_MONTH           VARCHAR  (e.g. "2023-01")
  TOTAL_UNIQUE_BENEFICIARIES BIGINT
  TOTAL_CLAIMS               BIGINT
  TOTAL_PAID                 DOUBLE
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

_connection = None
_hcpcs_lookup: Optional[Dict[str, Dict[str, str]]] = None

# Default paths relative to project root
_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_DEFAULT_PARQUET = _PROJECT_ROOT / ".cache" / "medicaid" / "medicaid-provider-spending.parquet"
_DEFAULT_HCPCS = _PROJECT_ROOT / ".cache" / "medicaid" / "hcpcs_lookup.json"
_DEFAULT_NPPES = _PROJECT_ROOT / ".cache" / "medicaid" / "nppes_slim.parquet"
_PARQUET_PATH = Path(os.environ.get("MEDICAID_PROVIDER_SPENDING_PATH", str(_DEFAULT_PARQUET)))
_HCPCS_PATH = Path(os.environ.get("HCPCS_LOOKUP_PATH", str(_DEFAULT_HCPCS)))
_NPPES_PATH = Path(os.environ.get("NPPES_SLIM_PATH", str(_DEFAULT_NPPES)))


def _get_conn():
    """Lazy singleton DuckDB connection."""
    global _connection
    if _connection is None:
        import duckdb
        _connection = duckdb.connect(":memory:")
    return _connection


def _get_hcpcs_lookup() -> Dict[str, Dict[str, str]]:
    """Lazy-load HCPCS code → description lookup."""
    global _hcpcs_lookup
    if _hcpcs_lookup is None:
        if _HCPCS_PATH.exists():
            with open(_HCPCS_PATH) as f:
                _hcpcs_lookup = json.load(f)
        else:
            _hcpcs_lookup = {}
    return _hcpcs_lookup


def _missing_file_error() -> Dict[str, Any]:
    return {
        "error": "parquet_not_found",
        "message": (
            f"Medicaid provider spending Parquet not found at {_PARQUET_PATH}. "
            "Run: python scripts/download_medicaid_provider_spending.py"
        ),
    }


def _npi_column(npi_role: str) -> str:
    """Return the NPI column name based on role."""
    if npi_role == "servicing":
        return "SERVICING_PROVIDER_NPI_NUM"
    return "BILLING_PROVIDER_NPI_NUM"


def _zero_paid_clause(exclude_zero_paid: bool) -> str:
    """Return SQL clause to exclude zero/negative paid rows."""
    if exclude_zero_paid:
        return "TOTAL_PAID > 0"
    return ""


def _enrich_hcpcs(data: List[Dict]) -> List[Dict]:
    """Add HCPCS description to rows that have an HCPCS_CODE field."""
    lookup = _get_hcpcs_lookup()
    if not lookup:
        return data
    for row in data:
        code = row.get("HCPCS_CODE")
        if code and code in lookup:
            row["hcpcs_description"] = lookup[code]["short"]
    return data


def _enrich_providers(data: List[Dict], npi_field: str = "npi") -> List[Dict]:
    """Add provider identity (name, specialty, state) from NPPES slim Parquet.

    Silently returns data unchanged if NPPES Parquet not available.
    """
    if not _NPPES_PATH.exists() or not data:
        return data

    npis = [str(row.get(npi_field, "")) for row in data if row.get(npi_field)]
    if not npis:
        return data

    conn = _get_conn()
    placeholders = ", ".join(["?"] * len(npis))

    try:
        result = conn.execute(f"""
            SELECT npi, provider_name, specialty, state, zip5
            FROM read_parquet('{_NPPES_PATH}')
            WHERE npi IN ({placeholders})
        """, npis).fetchdf()

        npi_info = {}
        for rec in result.to_dict(orient="records"):
            npi_info[rec["npi"]] = rec

        for row in data:
            npi_val = str(row.get(npi_field, ""))
            if npi_val in npi_info:
                info = npi_info[npi_val]
                row["provider_name"] = info["provider_name"]
                row["specialty"] = info["specialty"]
                row["provider_state"] = info["state"]
                row["provider_zip5"] = info["zip5"]
    except Exception:
        pass  # Graceful degradation — enrichment is optional

    return data


# ---------------------------------------------------------------------------
# Query methods
# ---------------------------------------------------------------------------

def get_provider_spending(
    npi: Optional[str] = None,
    hcpcs_code: Optional[str] = None,
    month_from: Optional[str] = None,
    month_to: Optional[str] = None,
    npi_role: str = "billing",
    exclude_zero_paid: bool = True,
    limit: int = 100,
    offset: int = 0,
) -> Dict[str, Any]:
    """Filter provider spending by NPI, HCPCS code, and/or date range."""
    if not _PARQUET_PATH.exists():
        return _missing_file_error()

    conn = _get_conn()
    npi_col = _npi_column(npi_role)

    conditions = []
    params = []

    if npi:
        conditions.append(f"{npi_col} = ?")
        params.append(str(npi))
    if hcpcs_code:
        conditions.append("HCPCS_CODE = ?")
        params.append(str(hcpcs_code))
    if month_from:
        conditions.append("CLAIM_FROM_MONTH >= ?")
        params.append(str(month_from))
    if month_to:
        conditions.append("CLAIM_FROM_MONTH <= ?")
        params.append(str(month_to))

    zp = _zero_paid_clause(exclude_zero_paid)
    if zp:
        conditions.append(zp)

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    limit = int(limit)
    offset = int(offset)

    sql = f"""
        SELECT
            BILLING_PROVIDER_NPI_NUM,
            SERVICING_PROVIDER_NPI_NUM,
            HCPCS_CODE,
            CLAIM_FROM_MONTH,
            TOTAL_UNIQUE_BENEFICIARIES,
            TOTAL_CLAIMS,
            TOTAL_PAID
        FROM read_parquet('{_PARQUET_PATH}')
        {where}
        ORDER BY TOTAL_PAID DESC
        LIMIT {limit} OFFSET {offset}
    """

    result = conn.execute(sql, params).fetchdf()
    data = _enrich_hcpcs(result.to_dict(orient="records"))
    return {
        "method": "get_provider_spending",
        "count": len(data),
        "data": data,
    }


def get_provider_top_services(
    npi: str,
    npi_role: str = "billing",
    exclude_zero_paid: bool = True,
    limit: int = 20,
) -> Dict[str, Any]:
    """Top HCPCS codes by total payment for a given provider NPI."""
    if not _PARQUET_PATH.exists():
        return _missing_file_error()

    conn = _get_conn()
    npi_col = _npi_column(npi_role)
    limit = int(limit)

    zp = _zero_paid_clause(exclude_zero_paid)
    extra_where = f"AND {zp}" if zp else ""

    sql = f"""
        SELECT
            HCPCS_CODE,
            SUM(TOTAL_CLAIMS) AS total_claims,
            SUM(TOTAL_UNIQUE_BENEFICIARIES) AS total_beneficiaries,
            SUM(TOTAL_PAID) AS total_paid,
            COUNT(*) AS claim_months
        FROM read_parquet('{_PARQUET_PATH}')
        WHERE {npi_col} = ? {extra_where}
        GROUP BY HCPCS_CODE
        ORDER BY total_paid DESC
        LIMIT {limit}
    """

    result = conn.execute(sql, [str(npi)]).fetchdf()
    data = _enrich_hcpcs(result.to_dict(orient="records"))
    return {
        "method": "get_provider_top_services",
        "npi": npi,
        "npi_role": npi_role,
        "count": len(data),
        "data": data,
    }


def get_hcpcs_top_providers(
    hcpcs_code: str,
    npi_role: str = "billing",
    exclude_zero_paid: bool = True,
    limit: int = 20,
) -> Dict[str, Any]:
    """Top providers by total payment for a given HCPCS code."""
    if not _PARQUET_PATH.exists():
        return _missing_file_error()

    conn = _get_conn()
    npi_col = _npi_column(npi_role)
    limit = int(limit)

    zp = _zero_paid_clause(exclude_zero_paid)
    extra_where = f"AND {zp}" if zp else ""

    sql = f"""
        SELECT
            {npi_col} AS npi,
            SUM(TOTAL_CLAIMS) AS total_claims,
            SUM(TOTAL_UNIQUE_BENEFICIARIES) AS total_beneficiaries,
            SUM(TOTAL_PAID) AS total_paid,
            COUNT(*) AS claim_months
        FROM read_parquet('{_PARQUET_PATH}')
        WHERE HCPCS_CODE = ? {extra_where}
        GROUP BY {npi_col}
        ORDER BY total_paid DESC
        LIMIT {limit}
    """

    result = conn.execute(sql, [str(hcpcs_code)]).fetchdf()
    data = _enrich_providers(result.to_dict(orient="records"), npi_field="npi")
    # Add HCPCS description to response metadata
    lookup = _get_hcpcs_lookup()
    hcpcs_desc = lookup.get(hcpcs_code, {}).get("short", "")
    return {
        "method": "get_hcpcs_top_providers",
        "hcpcs_code": hcpcs_code,
        "hcpcs_description": hcpcs_desc,
        "npi_role": npi_role,
        "count": len(data),
        "data": data,
    }


def get_provider_spending_summary(
    npi: str,
    npi_role: str = "billing",
    exclude_zero_paid: bool = True,
) -> Dict[str, Any]:
    """Aggregate spending summary for a provider NPI."""
    if not _PARQUET_PATH.exists():
        return _missing_file_error()

    conn = _get_conn()
    npi_col = _npi_column(npi_role)

    zp = _zero_paid_clause(exclude_zero_paid)
    extra_where = f"AND {zp}" if zp else ""

    sql = f"""
        SELECT
            COUNT(DISTINCT HCPCS_CODE) AS unique_hcpcs_codes,
            SUM(TOTAL_CLAIMS) AS total_claims,
            SUM(TOTAL_UNIQUE_BENEFICIARIES) AS total_beneficiaries,
            SUM(TOTAL_PAID) AS total_paid,
            MIN(CLAIM_FROM_MONTH) AS earliest_month,
            MAX(CLAIM_FROM_MONTH) AS latest_month,
            COUNT(*) AS total_rows
        FROM read_parquet('{_PARQUET_PATH}')
        WHERE {npi_col} = ? {extra_where}
    """

    result = conn.execute(sql, [str(npi)]).fetchdf()
    row = result.to_dict(orient="records")[0] if len(result) > 0 else {}
    return {
        "method": "get_provider_spending_summary",
        "npi": npi,
        "npi_role": npi_role,
        "data": row,
    }


def get_provider_info(
    npi: Optional[str] = None,
    npis: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Look up provider identity from NPPES (name, specialty, state, ZIP).

    Args:
        npi: Single NPI to look up
        npis: List of NPIs to look up (max 100)
    """
    if not _NPPES_PATH.exists():
        return {
            "error": "nppes_not_found",
            "message": (
                f"NPPES slim Parquet not found at {_NPPES_PATH}. "
                "Run: python scripts/download_nppes_slim.py"
            ),
        }

    if npi:
        npi_list = [str(npi)]
    elif npis:
        npi_list = [str(n) for n in npis[:100]]
    else:
        return {"error": "missing_param", "message": "Provide npi or npis parameter"}

    conn = _get_conn()
    placeholders = ", ".join(["?"] * len(npi_list))

    result = conn.execute(f"""
        SELECT npi, entity_type, provider_name, specialty, state, zip5, taxonomy_code
        FROM read_parquet('{_NPPES_PATH}')
        WHERE npi IN ({placeholders})
    """, npi_list).fetchdf()

    data = result.to_dict(orient="records")
    return {
        "method": "get_provider_info",
        "count": len(data),
        "data": data,
    }


def get_hcpcs_spending_by_month(
    hcpcs_code: str,
    month_from: Optional[str] = None,
    month_to: Optional[str] = None,
    exclude_zero_paid: bool = True,
) -> Dict[str, Any]:
    """Monthly spending trend for a HCPCS code across all providers.

    Returns one row per month with aggregate totals — max 84 rows (2018-2024).

    Args:
        hcpcs_code: HCPCS procedure code (e.g. "J9271", "99213")
        month_from: Start month filter (YYYY-MM)
        month_to: End month filter (YYYY-MM)
        exclude_zero_paid: Exclude zero/negative paid rows (default True)
    """
    if not _PARQUET_PATH.exists():
        return _missing_file_error()

    conn = _get_conn()

    conditions = ["HCPCS_CODE = ?"]
    params: List = [str(hcpcs_code)]

    if month_from:
        conditions.append("CLAIM_FROM_MONTH >= ?")
        params.append(str(month_from))
    if month_to:
        conditions.append("CLAIM_FROM_MONTH <= ?")
        params.append(str(month_to))

    zp = _zero_paid_clause(exclude_zero_paid)
    if zp:
        conditions.append(zp)

    where = "WHERE " + " AND ".join(conditions)

    sql = f"""
        SELECT
            CLAIM_FROM_MONTH AS month,
            SUM(TOTAL_CLAIMS) AS total_claims,
            SUM(TOTAL_UNIQUE_BENEFICIARIES) AS total_beneficiaries,
            SUM(TOTAL_PAID) AS total_paid,
            COUNT(DISTINCT BILLING_PROVIDER_NPI_NUM) AS billing_provider_count,
            COUNT(DISTINCT SERVICING_PROVIDER_NPI_NUM) AS servicing_provider_count
        FROM read_parquet('{_PARQUET_PATH}')
        {where}
        GROUP BY CLAIM_FROM_MONTH
        ORDER BY CLAIM_FROM_MONTH
    """

    result = conn.execute(sql, params).fetchdf()
    data = result.to_dict(orient="records")

    # Flag incomplete months: if last N months are <50% of trailing 6-month median
    if len(data) >= 7:
        paid_values = [d["total_paid"] for d in data]
        # Trailing median from months -7 to -2 (6 months before the last one)
        trailing = sorted(paid_values[-7:-1])
        median_paid = trailing[len(trailing) // 2] if trailing else 0
        if median_paid > 0:
            threshold = median_paid * 0.5
            for d in data:
                if d["total_paid"] < threshold:
                    d["incomplete"] = True

    lookup = _get_hcpcs_lookup()
    hcpcs_desc = lookup.get(hcpcs_code, {}).get("short", "")
    return {
        "method": "get_hcpcs_spending_by_month",
        "hcpcs_code": hcpcs_code,
        "hcpcs_description": hcpcs_desc,
        "count": len(data),
        "data": data,
    }


def get_hcpcs_spending_by_state(
    hcpcs_code: str,
    month_from: Optional[str] = None,
    month_to: Optional[str] = None,
    npi_role: str = "billing",
    exclude_zero_paid: bool = True,
    limit: int = 55,
) -> Dict[str, Any]:
    """Spending for a HCPCS code broken down by provider state (via NPPES).

    Joins spending data with NPPES slim Parquet to group by state.

    Args:
        hcpcs_code: HCPCS procedure code (e.g. "J9271", "99213")
        month_from: Start month filter (YYYY-MM)
        month_to: End month filter (YYYY-MM)
        npi_role: "billing" or "servicing"
        exclude_zero_paid: Exclude zero/negative paid rows (default True)
        limit: Max states returned (default: 55 — all US states + territories)
    """
    if not _PARQUET_PATH.exists():
        return _missing_file_error()
    if not _NPPES_PATH.exists():
        return {
            "error": "nppes_not_found",
            "message": (
                f"NPPES slim Parquet not found at {_NPPES_PATH}. "
                "Run: python scripts/download_nppes_slim.py"
            ),
        }

    conn = _get_conn()
    npi_col = _npi_column(npi_role)
    limit = int(limit)

    conditions = ["s.HCPCS_CODE = ?"]
    params: List = [str(hcpcs_code)]

    if month_from:
        conditions.append("s.CLAIM_FROM_MONTH >= ?")
        params.append(str(month_from))
    if month_to:
        conditions.append("s.CLAIM_FROM_MONTH <= ?")
        params.append(str(month_to))

    zp = _zero_paid_clause(exclude_zero_paid)
    if zp:
        conditions.append(f"s.{zp}")

    where = "WHERE " + " AND ".join(conditions)

    sql = f"""
        SELECT
            COALESCE(n.state, 'UNKNOWN') AS state,
            SUM(s.TOTAL_CLAIMS) AS total_claims,
            SUM(s.TOTAL_UNIQUE_BENEFICIARIES) AS total_beneficiaries,
            SUM(s.TOTAL_PAID) AS total_paid,
            COUNT(DISTINCT s.{npi_col}) AS provider_count
        FROM read_parquet('{_PARQUET_PATH}') s
        LEFT JOIN read_parquet('{_NPPES_PATH}') n
            ON s.{npi_col} = n.npi
        {where}
        GROUP BY COALESCE(n.state, 'UNKNOWN')
        ORDER BY total_paid DESC
        LIMIT {limit}
    """

    result = conn.execute(sql, params).fetchdf()
    data = result.to_dict(orient="records")
    lookup = _get_hcpcs_lookup()
    hcpcs_desc = lookup.get(hcpcs_code, {}).get("short", "")
    return {
        "method": "get_hcpcs_spending_by_state",
        "hcpcs_code": hcpcs_code,
        "hcpcs_description": hcpcs_desc,
        "npi_role": npi_role,
        "count": len(data),
        "data": data,
    }


# ---------------------------------------------------------------------------
# HCPCS lookup and search
# ---------------------------------------------------------------------------

def lookup_hcpcs(
    code: Optional[str] = None,
    codes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Look up HCPCS code description(s).

    Args:
        code: Single HCPCS code (e.g. "J0585")
        codes: List of HCPCS codes (e.g. ["J0585", "99213"])
    """
    lookup = _get_hcpcs_lookup()
    if not lookup:
        return {
            "error": "hcpcs_lookup_not_found",
            "message": (
                f"HCPCS lookup not found at {_HCPCS_PATH}. "
                "Run: python scripts/download_hcpcs_lookup.py"
            ),
        }

    if code:
        codes_to_look = [code.upper().strip()]
    elif codes:
        codes_to_look = [c.upper().strip() for c in codes]
    else:
        return {"error": "missing_param", "message": "Provide code or codes parameter"}

    results = {}
    for c in codes_to_look:
        if c in lookup:
            results[c] = lookup[c]
        else:
            results[c] = {"short": "", "long": "", "not_found": True}

    return {
        "method": "lookup_hcpcs",
        "count": sum(1 for v in results.values() if not v.get("not_found")),
        "data": results,
    }


def search_hcpcs(
    query: str,
    limit: int = 20,
) -> Dict[str, Any]:
    """Search HCPCS codes by description text (drug name, procedure, etc.).

    Searches both short and long descriptions case-insensitively.

    Args:
        query: Search text (e.g. "semaglutide", "botulinum", "office visit")
        limit: Max results (default: 20)
    """
    lookup = _get_hcpcs_lookup()
    if not lookup:
        return {
            "error": "hcpcs_lookup_not_found",
            "message": (
                f"HCPCS lookup not found at {_HCPCS_PATH}. "
                "Run: python scripts/download_hcpcs_lookup.py"
            ),
        }

    query_lower = query.lower().strip()
    terms = query_lower.split()
    limit = int(limit)

    matches = []
    for code, info in lookup.items():
        searchable = (info.get("long", "") + " " + info.get("short", "")).lower()
        if all(term in searchable for term in terms):
            matches.append({
                "code": code,
                "short": info["short"],
                "long": info["long"],
            })

    # Sort: exact prefix match first, then alphabetical
    matches.sort(key=lambda m: (
        0 if m["code"].lower().startswith(query_lower) else 1,
        m["code"],
    ))

    return {
        "method": "search_hcpcs",
        "query": query,
        "count": len(matches[:limit]),
        "total_matches": len(matches),
        "data": matches[:limit],
    }


# ---------------------------------------------------------------------------
# Method registry — imported by __init__.py
# ---------------------------------------------------------------------------

LOCAL_METHODS = {
    "get_provider_spending": get_provider_spending,
    "get_provider_top_services": get_provider_top_services,
    "get_hcpcs_top_providers": get_hcpcs_top_providers,
    "get_provider_spending_summary": get_provider_spending_summary,
    "get_provider_info": get_provider_info,
    "get_hcpcs_spending_by_month": get_hcpcs_spending_by_month,
    "get_hcpcs_spending_by_state": get_hcpcs_spending_by_state,
    "lookup_hcpcs": lookup_hcpcs,
    "search_hcpcs": search_hcpcs,
}
