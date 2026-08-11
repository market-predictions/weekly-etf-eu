from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any
import json

SCHEMA_VERSION = "ucits_close_price_validation_basket_results_v2"


def _ticker(row: dict[str, Any]) -> str:
    return str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper()


def _isin(row: dict[str, Any]) -> str:
    return str(row.get("isin") or "").strip().upper()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def validate_payload(
    payload: dict[str, Any],
    *,
    expected_report_date: str | None = None,
    portfolio_state: dict[str, Any] | None = None,
    require_funded_consensus: bool = True,
) -> dict[str, Any]:
    blockers: list[str] = []

    if payload.get("schema_version") != SCHEMA_VERSION:
        blockers.append(f"pricing schema must be {SCHEMA_VERSION}")

    report_date_raw = str(payload.get("report_date") or "").strip()
    try:
        report_date = date.fromisoformat(report_date_raw)
    except ValueError:
        report_date = None
        blockers.append("pricing report_date is missing or invalid")

    if expected_report_date and report_date_raw != expected_report_date:
        blockers.append(
            f"pricing report_date mismatch: expected={expected_report_date} actual={report_date_raw or 'missing'}"
        )

    if payload.get("source_basket") != "config/ucits_close_price_validation_basket.yml":
        blockers.append("unexpected pricing source_basket")

    for field in ("funding_authority", "portfolio_mutation", "production_delivery_authority"):
        if payload.get(field) is not False:
            blockers.append(f"pricing authority field must be false: {field}")

    rows = [row for row in payload.get("rows") or [] if isinstance(row, dict)]
    if int(payload.get("line_count") or 0) != len(rows):
        blockers.append("pricing line_count does not match rows")
    priced_count = sum(row.get("pricing_status") == "priced_non_authoritative" for row in rows)
    if int(payload.get("priced_line_count") or 0) != priced_count:
        blockers.append("pricing priced_line_count does not match rows")

    if require_funded_consensus and payload.get("report_pricing_gate_passed") is not True:
        blockers.append("funded two-provider pricing consensus gate is not passed")
    if require_funded_consensus and payload.get("valuation_grade") is not True:
        blockers.append("pricing artifact is not valuation-grade for the funded set")

    funded_positions: list[dict[str, Any]] = []
    if portfolio_state is not None:
        funded_positions = [
            row for row in portfolio_state.get("positions") or [] if isinstance(row, dict)
        ]
        if not funded_positions:
            blockers.append("protected portfolio has no funded positions")

    # ISIN identifies the fund/share class, not the exchange trading line. One
    # UCITS share class can legitimately have multiple venue/ticker rows (e.g.
    # SXR8/Xetra and CSPX/LSE share IE00B5BMR087). Pricing authority therefore
    # resolves the protected holding by exact (ISIN, trading-line ticker). Never
    # let a sibling venue row overwrite the funded line merely because ISIN is
    # shared.
    rows_by_exact_identity = {
        (_isin(row), _ticker(row)): row
        for row in rows
        if _isin(row) and _ticker(row)
    }
    rows_by_ticker = {_ticker(row): row for row in rows if _ticker(row)}
    funded_evidence: list[dict[str, Any]] = []

    for position in funded_positions:
        ticker = _ticker(position)
        isin = _isin(position)
        row = rows_by_exact_identity.get((isin, ticker)) or rows_by_ticker.get(ticker)
        if row is None:
            blockers.append(f"funded position missing from pricing artifact: {ticker or isin}")
            continue
        if isin and _isin(row) != isin:
            blockers.append(
                f"funded exact-line identity mismatch for {ticker}: expected_isin={isin} actual_isin={_isin(row) or 'missing'}"
            )
            continue

        row_blockers: list[str] = []
        if row.get("pricing_status") != "priced_non_authoritative":
            row_blockers.append("not_priced")
        if row.get("source_agreement_status") != "qualified_development_consensus":
            row_blockers.append("no_qualified_two_provider_consensus")
        agreeing = [str(value) for value in row.get("agreeing_providers") or [] if str(value).strip()]
        if len(set(agreeing)) < 2:
            row_blockers.append("fewer_than_two_agreeing_providers")
        if row.get("valuation_grade") is not True:
            row_blockers.append("not_valuation_grade")
        if row.get("completed_close_on_or_before_report_date") is not True:
            row_blockers.append("completed_close_gate_missing")
        if str(row.get("requested_report_date") or "") != report_date_raw:
            row_blockers.append("row_report_date_mismatch")
        close_date_raw = str(row.get("close_date") or "")
        try:
            close_date = date.fromisoformat(close_date_raw)
        except ValueError:
            close_date = None
            row_blockers.append("invalid_close_date")
        if close_date and report_date and close_date > report_date:
            row_blockers.append("close_after_report_date")
        if row.get("close_price") in (None, ""):
            row_blockers.append("missing_close_price")

        if row_blockers:
            blockers.append(
                f"funded pricing contract failed for {ticker or isin}: " + ",".join(row_blockers)
            )
        funded_evidence.append(
            {
                "ticker": ticker,
                "isin": isin,
                "close_date": close_date_raw or None,
                "agreeing_providers": sorted(set(agreeing)),
                "source_agreement_status": row.get("source_agreement_status"),
                "valuation_grade": row.get("valuation_grade"),
                "passed": not row_blockers,
                "blockers": row_blockers,
            }
        )

    return {
        "schema_version": "etf_eu_pricing_contract_validation_v2",
        "pricing_schema": payload.get("schema_version"),
        "report_date": report_date_raw or None,
        "expected_report_date": expected_report_date,
        "report_pricing_gate_passed": payload.get("report_pricing_gate_passed") is True,
        "require_funded_consensus": require_funded_consensus,
        "funded_position_count": len(funded_positions),
        "funded_evidence": funded_evidence,
        "valid": not blockers,
        "blockers": blockers,
    }


def validate_artifact(
    artifact_path: Path,
    *,
    expected_report_date: str | None = None,
    portfolio_state_path: Path | None = None,
    require_funded_consensus: bool = True,
) -> dict[str, Any]:
    payload = _load_json(artifact_path)
    portfolio_state = _load_json(portfolio_state_path) if portfolio_state_path else None
    result = validate_payload(
        payload,
        expected_report_date=expected_report_date,
        portfolio_state=portfolio_state,
        require_funded_consensus=require_funded_consensus,
    )
    result["artifact"] = str(artifact_path)
    result["portfolio_state"] = str(portfolio_state_path) if portfolio_state_path else None
    return result