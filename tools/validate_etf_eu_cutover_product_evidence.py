from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


EXPECTED = {
    "VVSM": "IE00BMC38736",
    "LOCK": "IE00BG0J4C88",
    "IXUA": "IE000R4ZNTN3",
}
VALID_GRADES = {"pass", "partial", "fail", "not_assessed"}


def load(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Cutover evidence must be a YAML object")
    return payload


def validate(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if payload.get("schema_version") != "etf_eu_cutover_product_evidence_v1":
        blockers.append("unexpected schema_version")
    if payload.get("artifact_type") != "etf_eu_cutover_product_evidence_review":
        blockers.append("unexpected artifact_type")
    if payload.get("status") != "cutover_evidence_incomplete":
        blockers.append("initial review must remain cutover_evidence_incomplete")
    for key in (
        "activation_authority",
        "portfolio_mutation",
        "funding_authority",
        "execution_authority",
        "production_delivery_authority",
    ):
        if payload.get(key) is not False:
            blockers.append(f"{key} must be false")

    rows = payload.get("candidates") if isinstance(payload.get("candidates"), list) else []
    index = {
        str(row.get("ticker")): row
        for row in rows
        if isinstance(row, dict) and row.get("ticker")
    }
    if set(index) != set(EXPECTED):
        blockers.append("candidate set must be exactly VVSM, LOCK and IXUA")

    for ticker, isin in EXPECTED.items():
        row = index.get(ticker, {})
        if row.get("isin") != isin:
            blockers.append(f"{ticker} ISIN mismatch")
        if row.get("exchange") != "Xetra" or row.get("currency") != "EUR":
            blockers.append(f"{ticker} exact Xetra EUR line is not recorded")
        if row.get("activation_ready") is not False:
            blockers.append(f"{ticker} must not be activation-ready in this evidence version")
        if row.get("candidate_status") != "cutover_evidence_incomplete":
            blockers.append(f"{ticker} candidate status must remain incomplete")

        for grade_name in (
            "identity_grade",
            "document_grade",
            "valuation_grade",
            "tradability_grade",
        ):
            grade = row.get(grade_name) if isinstance(row.get(grade_name), dict) else {}
            if grade.get("status") not in VALID_GRADES:
                blockers.append(f"{ticker} has invalid or missing {grade_name} status")

        identity = row.get("identity_grade") or {}
        if identity.get("status") != "pass" or identity.get("exact_line_confirmed") is not True:
            blockers.append(f"{ticker} identity grade must pass for the exact line")

        valuation = row.get("valuation_grade") or {}
        if valuation.get("exact_eur_line_valuation_grade") != "fail":
            blockers.append(f"{ticker} must not claim an accepted EUR-line valuation")
        if valuation.get("connectivity_source_authoritative_for_activation") is not False:
            blockers.append(f"{ticker} connectivity pricing must remain non-authoritative")

        tradability = row.get("tradability_grade") or {}
        if tradability.get("status") != "fail":
            blockers.append(f"{ticker} tradability must remain blocking until bid/ask is captured")
        if tradability.get("accepted_bid_ask_snapshot_captured") is not False:
            blockers.append(f"{ticker} must not claim a bid/ask snapshot")
        if tradability.get("accepted_quote_size_captured") is not False:
            blockers.append(f"{ticker} must not claim quote-size evidence")

    vvsm_document = (index.get("VVSM") or {}).get("document_grade") or {}
    if vvsm_document.get("status") != "pass":
        blockers.append("VVSM exact KID evidence should pass")
    if vvsm_document.get("exact_kid_artifact_captured") is not True:
        blockers.append("VVSM exact KID artifact is not recorded")
    if vvsm_document.get("kid_document_date") != "2026-03-27":
        blockers.append("VVSM KID date mismatch")

    for ticker in ("LOCK", "IXUA"):
        document = (index.get(ticker) or {}).get("document_grade") or {}
        if document.get("status") != "partial":
            blockers.append(f"{ticker} document grade must remain partial")
        if document.get("exact_kid_artifact_captured") is not False:
            blockers.append(f"{ticker} must not claim an exact KID artifact")
        if document.get("issuer_confirms_priips_kid_availability") is not True:
            blockers.append(f"{ticker} issuer document-availability evidence is missing")

    ixua_reclassification = (((index.get("IXUA") or {}).get("document_grade") or {}).get("previous_blocker_reclassification") or {})
    if ixua_reclassification.get("from") != "kid_missing" or ixua_reclassification.get("to") != "exact_kid_artifact_not_captured":
        blockers.append("IXUA KID blocker has not been reclassified precisely")

    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    expected_summary = {
        "candidate_count": 3,
        "identity_pass_count": 3,
        "document_pass_count": 1,
        "fund_nav_pass_count": 2,
        "exact_eur_line_valuation_pass_count": 0,
        "tradability_pass_count": 0,
        "activation_ready_count": 0,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            blockers.append(f"summary {key} mismatch")

    return blockers


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ETF EU cutover product evidence")
    parser.add_argument(
        "path",
        type=Path,
        nargs="?",
        default=Path("config/etf_eu_cutover_product_evidence_20260728.yml"),
    )
    args = parser.parse_args()
    payload = load(args.path)
    blockers = validate(payload)
    print(json.dumps({
        "artifact_type": "etf_eu_cutover_product_evidence_validation",
        "review_date": str(payload.get("review_date")),
        "valid": not blockers,
        "blockers": blockers,
        "activation_ready_count": ((payload.get("summary") or {}).get("activation_ready_count")),
    }, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
