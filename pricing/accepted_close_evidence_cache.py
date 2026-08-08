from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


SCHEMA = "ucits_close_evidence_cache_v1"
REQUIRED_PROVIDERS = {"boerse_frankfurt_xetra", "yahoo_chart"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def cache_path_for(report_date: date, root: Path = Path("state/price_evidence_cache")) -> Path:
    return root / f"ucits_close_evidence_{report_date.isoformat()}.json"


def load_cache(report_date: date, root: Path = Path("state/price_evidence_cache")) -> tuple[Path, dict[str, Any]] | None:
    path = cache_path_for(report_date, root)
    if not path.is_file():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Accepted price evidence cache must be a JSON object")
    validate_cache(payload, report_date)
    return path, payload


def validate_cache(payload: dict[str, Any], report_date: date) -> None:
    blockers: list[str] = []
    requested = report_date.isoformat()
    if payload.get("schema_version") != SCHEMA:
        blockers.append("unexpected_cache_schema")
    if payload.get("report_date") != requested:
        blockers.append("cache_report_date_mismatch")
    if payload.get("report_pricing_gate_passed") is not True:
        blockers.append("source_pricing_gate_not_passed")
    if payload.get("funded_line_count") != 4 or payload.get("funded_consensus_count") != 4 or payload.get("funded_identity_anchor_count") != 4:
        blockers.append("source_funded_gate_not_4_of_4")
    artifact = payload.get("source_actions_artifact") if isinstance(payload.get("source_actions_artifact"), dict) else {}
    digest = str(artifact.get("artifact_digest") or "")
    member_hash = str(artifact.get("qualification_member_sha256") or "")
    if not digest.startswith("sha256:") or len(digest) != 71:
        blockers.append("source_actions_artifact_digest_missing")
    if len(member_hash) != 64:
        blockers.append("qualification_member_hash_missing")
    if not payload.get("source_workflow_run_id") or not payload.get("source_workflow_head_sha") or not payload.get("source_run_id"):
        blockers.append("source_run_provenance_incomplete")

    lines = payload.get("lines") if isinstance(payload.get("lines"), list) else []
    if len(lines) != 4:
        blockers.append("cache_line_count_not_four")
    seen: set[str] = set()
    for row in lines:
        if not isinstance(row, dict):
            blockers.append("malformed_cache_line")
            continue
        basket_id = str(row.get("basket_id") or "")
        if not basket_id or basket_id in seen:
            blockers.append("duplicate_or_missing_basket_id")
        seen.add(basket_id)
        if row.get("selected_close_date") != requested:
            blockers.append(f"{basket_id}:selected_close_date_mismatch")
        if row.get("identity_anchor_passed") is not True:
            blockers.append(f"{basket_id}:identity_anchor_missing")
        spread = float(row.get("agreement_spread_pct") or 0.0)
        if spread > float(payload.get("agreement_tolerance_pct") or 1.0):
            blockers.append(f"{basket_id}:provider_spread_exceeds_tolerance")
        providers = row.get("providers") if isinstance(row.get("providers"), list) else []
        provider_names = {str(item.get("provider") or "") for item in providers if isinstance(item, dict)}
        if provider_names != REQUIRED_PROVIDERS:
            blockers.append(f"{basket_id}:provider_set_mismatch")
        for item in providers:
            if not isinstance(item, dict):
                blockers.append(f"{basket_id}:malformed_provider")
                continue
            if item.get("close_date") != requested:
                blockers.append(f"{basket_id}:{item.get('provider')}:close_date_mismatch")
            if not item.get("provider_symbol"):
                blockers.append(f"{basket_id}:{item.get('provider')}:symbol_missing")
            try:
                if float(item.get("close_price")) <= 0:
                    blockers.append(f"{basket_id}:{item.get('provider')}:invalid_close")
            except (TypeError, ValueError):
                blockers.append(f"{basket_id}:{item.get('provider')}:invalid_close")
    if blockers:
        raise RuntimeError("Accepted price evidence cache invalid: " + "; ".join(blockers))


def line_evidence(
    line: dict[str, Any],
    report_date: date,
    root: Path = Path("state/price_evidence_cache"),
) -> dict[str, Any] | None:
    loaded = load_cache(report_date, root)
    if loaded is None:
        return None
    path, payload = loaded
    basket_id = str(line.get("basket_id") or "")
    isin = str(line.get("isin") or "").upper()
    venue = str(line.get("venue_code") or "").upper()
    currency = str(line.get("currency") or "").upper()
    ticker = str(line.get("ticker") or "").upper()
    for row in payload["lines"]:
        if row.get("basket_id") != basket_id:
            continue
        exact_identity = (
            str(row.get("isin") or "").upper() == isin
            and str(row.get("venue_code") or "").upper() == venue
            and str(row.get("currency") or "").upper() == currency
            and str(row.get("ticker") or "").upper() == ticker
        )
        if not exact_identity:
            raise RuntimeError(f"Cached evidence identity mismatch for {basket_id}")
        return {
            **row,
            "cache_path": str(path),
            "cache_sha256": sha256_file(path),
            "source_run_id": payload.get("source_run_id"),
            "source_workflow_run_id": payload.get("source_workflow_run_id"),
            "source_workflow_head_sha": payload.get("source_workflow_head_sha"),
            "source_actions_artifact": payload.get("source_actions_artifact"),
            "evidence_role": payload.get("evidence_role"),
        }
    return None


def provider_from_cache(
    line: dict[str, Any],
    report_date: date,
    provider_name: str,
    root: Path = Path("state/price_evidence_cache"),
) -> dict[str, Any] | None:
    evidence = line_evidence(line, report_date, root)
    if evidence is None:
        return None
    for provider in evidence.get("providers") or []:
        if provider.get("provider") != provider_name:
            continue
        return {
            "provider": provider_name,
            "configured": True,
            "provider_symbol": provider.get("provider_symbol"),
            "expected_isin": line.get("isin"),
            "expected_venue_code": line.get("venue_code"),
            "expected_currency": line.get("currency"),
            "requested_report_date": report_date.isoformat(),
            "pricing_status": "priced",
            "close_date": provider.get("close_date"),
            "close_price": provider.get("close_price"),
            "close_age_days": 0,
            "returned_symbol": provider.get("provider_symbol"),
            "returned_exchange": "Xetra" if str(line.get("venue_code") or "").upper() == "XETR" else line.get("exchange"),
            "returned_mic": line.get("venue_code") if provider_name == "boerse_frankfurt_xetra" else None,
            "returned_currency": line.get("currency"),
            "venue_match": provider.get("venue_match"),
            "currency_match": provider.get("currency_match"),
            "identity_status": provider.get("identity_status"),
            "retrieval_mode": "immutable_report_time_evidence_cache",
            "observed_at_utc": None,
            "identity_evidence": [
                {
                    "cache_path": evidence.get("cache_path"),
                    "cache_sha256": evidence.get("cache_sha256"),
                    "source_run_id": evidence.get("source_run_id"),
                    "source_workflow_run_id": evidence.get("source_workflow_run_id"),
                    "source_workflow_head_sha": evidence.get("source_workflow_head_sha"),
                    "source_actions_artifact": evidence.get("source_actions_artifact"),
                    "original_retrieval_mode": provider.get("retrieval_mode"),
                    "evidence_role": evidence.get("evidence_role"),
                }
            ],
            "blockers": [],
        }
    return None
