from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any
import json

SCHEMA_VERSION = "ucits_close_price_validation_basket_results_v2"
AUTHORIZED_EXACT_STATUSES = {"fresh_exact_verified", "fresh_exact_unverified"}


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
    """Validate funded pricing authority under primary+verification semantics.

    The historical parameter name `require_funded_consensus` is retained for
    caller compatibility. When true, it means that every funded line must have
    valuation-grade exact requested-date pricing authority. A second provider is
    confidence verification, not a universal liveness requirement.
    """

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

    policy = payload.get("pricing_authority_policy") or {}
    if policy.get("mode") != "donor_aligned_primary_plus_verification_v1":
        blockers.append("primary+verification pricing authority policy missing")
    if policy.get("second_provider_required_for_liveness") is not False:
        blockers.append("second provider must not be a universal liveness dependency")
    if policy.get("same_date_disagreement_blocks") is not True:
        blockers.append("same-date provider disagreement must fail closed")

    if require_funded_consensus and payload.get("report_pricing_gate_passed") is not True:
        blockers.append("funded exact-close pricing authority gate is not passed")
    if require_funded_consensus and payload.get("valuation_grade") is not True:
        blockers.append("pricing artifact is not valuation-grade for the funded set")

    funded_positions: list[dict[str, Any]] = []
    if portfolio_state is not None:
        funded_positions = [row for row in portfolio_state.get("positions") or [] if isinstance(row, dict)]
        if not funded_positions:
            blockers.append("protected portfolio has no funded positions")

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
        authority_status = str(row.get("source_agreement_status") or "")
        if row.get("pricing_status") != "priced_non_authoritative":
            row_blockers.append("not_priced")
        if authority_status not in AUTHORIZED_EXACT_STATUSES:
            row_blockers.append("no_authorized_exact_primary_close")
        if row.get("valuation_grade") is not True:
            row_blockers.append("not_valuation_grade")
        if row.get("static_identity_binding") is not True:
            row_blockers.append("static_exact_line_identity_not_bound")
        if row.get("identity_assurance_status") != "static_registry_verified_exact_line":
            row_blockers.append("static_identity_assurance_missing")
        if row.get("completed_close_on_requested_report_date") is not True:
            row_blockers.append("exact_requested_date_close_gate_missing")
        if str(row.get("requested_report_date") or "") != report_date_raw:
            row_blockers.append("row_report_date_mismatch")
        close_date_raw = str(row.get("close_date") or "")
        try:
            close_date = date.fromisoformat(close_date_raw)
        except ValueError:
            close_date = None
            row_blockers.append("invalid_close_date")
        if close_date and report_date and close_date != report_date:
            row_blockers.append("close_date_not_exact_requested_date")
        if row.get("close_price") in (None, ""):
            row_blockers.append("missing_close_price")
        if not str(row.get("primary_provider") or "").strip():
            row_blockers.append("primary_provider_missing")
        same_date_count = int(row.get("same_date_provider_count") or 0)
        if same_date_count < 1:
            row_blockers.append("no_exact_same_date_provider")
        if authority_status == "fresh_exact_verified":
            if same_date_count < 2:
                row_blockers.append("verified_status_without_verifier")
            if not row.get("verification_providers"):
                row_blockers.append("verified_status_without_verification_provider")
        if authority_status == "fresh_exact_unverified" and same_date_count != 1:
            row_blockers.append("unverified_status_requires_one_exact_provider")

        if row_blockers:
            blockers.append(f"funded pricing contract failed for {ticker or isin}: " + ",".join(row_blockers))
        funded_evidence.append(
            {
                "ticker": ticker,
                "isin": isin,
                "close_date": close_date_raw or None,
                "primary_provider": row.get("primary_provider"),
                "verification_providers": row.get("verification_providers") or [],
                "source_agreement_status": authority_status,
                "static_identity_binding": row.get("static_identity_binding") is True,
                "valuation_grade": row.get("valuation_grade"),
                "passed": not row_blockers,
                "blockers": row_blockers,
            }
        )

    return {
        "schema_version": "etf_eu_pricing_contract_validation_v2",
        "pricing_schema": payload.get("schema_version"),
        "pricing_authority_mode": policy.get("mode"),
        "report_date": report_date_raw or None,
        "expected_report_date": expected_report_date,
        "report_pricing_gate_passed": payload.get("report_pricing_gate_passed") is True,
        "require_funded_consensus": require_funded_consensus,
        "requirement_semantics": "funded_exact_primary_pricing_authority",
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
