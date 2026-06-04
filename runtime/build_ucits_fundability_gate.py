from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("PyYAML is required for UCITS fundability gate building") from exc

DEFAULT_REGISTRY = Path("config/ucits_symbol_registry.yml")
DEFAULT_OUTPUT_DIR = Path("output/fundability")
DEFAULT_VALUATION_DIR = Path("output/pricing")
PLACEHOLDER_VALUES = {
    "",
    "TBD",
    "pending",
    "pending_verification",
    "primary_line_pending_verification",
    "not_in_scope_or_pending",
    None,
}
REQUIRED_GATES = (
    "instrument_identity",
    "eu_investability",
    "trading_line",
    "pricing_quality",
    "tradability_liquidity",
    "portfolio_role",
    "decision",
)


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_json(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _latest_file(output_dir: Path, pattern: str) -> Path | None:
    files = sorted(output_dir.glob(pattern))
    return files[-1] if files else None


def _as_str(value: Any) -> str:
    return str(value if value is not None else "").strip()


def _is_placeholder(value: Any) -> bool:
    return value in PLACEHOLDER_VALUES or _as_str(value) in PLACEHOLDER_VALUES


def _looks_pending(value: Any) -> bool:
    text = _as_str(value).lower()
    return not text or text in {str(item).lower() for item in PLACEHOLDER_VALUES if item is not None} or text.startswith("pending_")


def _gate(blockers: list[str], details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "status": "passed" if not blockers else "blocked",
        "blockers": blockers,
        "details": details or {},
    }


def _valuation_rows_by_registry_id(valuation_payload: dict[str, Any] | None) -> dict[str, list[dict[str, Any]]]:
    rows_by_id: dict[str, list[dict[str, Any]]] = {}
    if not valuation_payload:
        return rows_by_id
    for row in valuation_payload.get("rows") or []:
        registry_id = _as_str(row.get("registry_id"))
        if registry_id:
            rows_by_id.setdefault(registry_id, []).append(row)
    return rows_by_id


def _instrument_identity_gate(fund: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    if _is_placeholder(fund.get("isin")):
        blockers.append("isin_missing_or_placeholder")
    if _is_placeholder(fund.get("fund_name")):
        blockers.append("fund_name_missing")
    if _is_placeholder(fund.get("provider")):
        blockers.append("provider_missing")
    if _as_str(fund.get("instrument_type")) != "ETF":
        blockers.append("instrument_type_not_ucits_etf_under_current_policy")

    proxy_boundary_ok = True
    for proxy in fund.get("research_proxies") or []:
        if proxy.get("proxy_must_not_be_funded") is not True:
            proxy_boundary_ok = False
    if fund.get("us_research_proxy") and not proxy_boundary_ok:
        blockers.append("us_proxy_research_only_boundary_missing")

    return _gate(blockers, {"instrument_type": fund.get("instrument_type"), "us_research_proxy": fund.get("us_research_proxy")})


def _eu_investability_gate(fund: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    if _as_str(fund.get("ucits_status")) != "confirmed":
        blockers.append("ucits_status_not_fully_confirmed")
    if _as_str(fund.get("priips_kid_status")) != "available":
        blockers.append("priips_kid_not_confirmed_available")
    for field in ["domicile", "distribution_policy", "replication_method", "benchmark_index", "ter_pct"]:
        if _is_placeholder(fund.get(field)):
            blockers.append(f"{field}_missing_or_pending")
    return _gate(blockers, {"investability_status": fund.get("investability_status"), "fundable_status": fund.get("fundable_status")})


def _line_is_verified(line: dict[str, Any]) -> bool:
    required = ["exchange", "exchange_ticker", "trading_currency", "provider_symbol", "pricing_symbol_yahoo"]
    if any(_is_placeholder(line.get(field)) for field in required):
        return False
    if _looks_pending(line.get("line_verification_status")):
        return False
    return True


def _trading_line_gate(fund: dict[str, Any]) -> dict[str, Any]:
    line_assessments: list[dict[str, Any]] = []
    verified_count = 0
    for line in fund.get("trading_lines") or []:
        line_blockers: list[str] = []
        for field in ["exchange", "exchange_ticker", "trading_currency", "provider_symbol", "pricing_symbol_yahoo"]:
            if _is_placeholder(line.get(field)):
                line_blockers.append(f"{field}_missing_or_pending")
        if _looks_pending(line.get("line_verification_status")):
            line_blockers.append("line_verification_status_pending")
        if not line_blockers:
            verified_count += 1
        line_assessments.append({
            "exchange": line.get("exchange"),
            "exchange_ticker": line.get("exchange_ticker"),
            "trading_currency": line.get("trading_currency"),
            "provider_symbol": line.get("provider_symbol"),
            "pricing_symbol_yahoo": line.get("pricing_symbol_yahoo"),
            "line_verification_status": line.get("line_verification_status"),
            "pricing_status": line.get("pricing_status"),
            "status": "passed" if not line_blockers else "blocked",
            "blockers": line_blockers,
        })
    blockers = [] if verified_count else ["no_verified_trading_line"]
    return _gate(blockers, {"verified_trading_line_count": verified_count, "lines": line_assessments})


def _pricing_quality_gate(fund: dict[str, Any], valuation_rows: list[dict[str, Any]]) -> dict[str, Any]:
    blockers: list[str] = []
    if not valuation_rows:
        blockers.append("agreement_gate_valuation_status_missing")
        return _gate(blockers, {"valuation_rows": []})

    valuation_grade_rows = [row for row in valuation_rows if row.get("valuation_grade") is True and row.get("valuation_status") == "valuation_grade"]
    if not valuation_grade_rows:
        blockers.append("valuation_grade_false")
    for row in valuation_rows:
        evidence = row.get("non_authoritative_preflight_evidence") or {}
        if evidence.get("source_id") in {"yahoo_yfinance", "issuer_nav", "blackrock_issuer_reference", "issuer_factsheet"}:
            blockers.append("pricing_evidence_provisional_or_reference_only")
            break
    blockers = sorted(set(blockers))
    return _gate(
        blockers,
        {
            "valuation_row_count": len(valuation_rows),
            "valuation_grade_row_count": len(valuation_grade_rows),
            "valuation_statuses": sorted({_as_str(row.get("valuation_status")) for row in valuation_rows}),
        },
    )


def _tradability_liquidity_gate(fund: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    if _as_str(fund.get("liquidity_check_status")) != "passed":
        blockers.append("liquidity_check_missing_or_not_passed")
    if _as_str(fund.get("spread_check_status")) != "passed":
        blockers.append("spread_check_missing_or_not_passed")
    if _as_str(fund.get("broker_availability_status")) != "confirmed":
        blockers.append("broker_availability_not_confirmed")
    return _gate(blockers)


def _portfolio_role_gate(fund: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    if _is_placeholder(fund.get("role")):
        blockers.append("candidate_role_missing")
    if _as_str(fund.get("portfolio_role_review_status")) != "approved":
        blockers.append("portfolio_role_review_missing")
    if _as_str(fund.get("alternative_comparison_status")) != "completed":
        blockers.append("alternative_comparison_missing")
    if _as_str(fund.get("risk_concentration_review_status")) != "completed":
        blockers.append("risk_concentration_review_missing")
    return _gate(blockers, {"role": fund.get("role")})


def _decision_gate(fund: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    if _as_str(fund.get("promotion_decision_status")) != "approved":
        blockers.append("portfolio_promotion_decision_missing")
    if _is_placeholder(fund.get("promotion_decision_reference")):
        blockers.append("promotion_decision_reference_missing")
    return _gate(blockers)


def build_fundability_gate(registry_path: Path, run_id: str, valuation_artifact_path: Path | None = None) -> dict[str, Any]:
    registry = _load_yaml(registry_path)
    valuation_payload = _load_json(valuation_artifact_path)
    valuation_index = _valuation_rows_by_registry_id(valuation_payload)

    rows: list[dict[str, Any]] = []
    for fund in registry.get("funds") or []:
        registry_id = _as_str(fund.get("registry_id"))
        gates = {
            "instrument_identity": _instrument_identity_gate(fund),
            "eu_investability": _eu_investability_gate(fund),
            "trading_line": _trading_line_gate(fund),
            "pricing_quality": _pricing_quality_gate(fund, valuation_index.get(registry_id, [])),
            "tradability_liquidity": _tradability_liquidity_gate(fund),
            "portfolio_role": _portfolio_role_gate(fund),
            "decision": _decision_gate(fund),
        }
        blockers = [f"{gate_name}:{blocker}" for gate_name, gate in gates.items() for blocker in gate["blockers"]]
        gate_status = "gate_passed_no_promotion" if not blockers else "not_fundable_blocked"
        rows.append({
            "registry_id": registry_id,
            "isin": fund.get("isin"),
            "fund_name": fund.get("fund_name"),
            "provider": fund.get("provider"),
            "role": fund.get("role"),
            "us_research_proxy": fund.get("us_research_proxy"),
            "instrument_type": fund.get("instrument_type"),
            "investability_status": fund.get("investability_status"),
            "current_fundable_status": fund.get("fundable_status"),
            "fundability_gate_status": gate_status,
            "gate_blockers": blockers,
            "gates": gates,
            "candidate_promotion": False,
            "funding_authority": False,
            "portfolio_mutation": False,
            "production_delivery": False,
        })

    gate_passed_count = sum(1 for row in rows if row["fundability_gate_status"] == "gate_passed_no_promotion")
    return {
        "schema_version": "ucits_fundability_gate_v1",
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_registry": str(registry_path),
        "source_valuation_artifact": str(valuation_artifact_path) if valuation_artifact_path else None,
        "portfolio_mutation": False,
        "production_delivery": False,
        "funding_authority": False,
        "candidate_promotion": False,
        "candidate_count": len(rows),
        "gate_passed_no_promotion_count": gate_passed_count,
        "not_fundable_count": len(rows) - gate_passed_count,
        "required_gates": list(REQUIRED_GATES),
        "rows": rows,
    }


def write_fundability_gate(registry_path: Path, output_dir: Path, run_id: str, valuation_artifact_path: Path | None = None) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = build_fundability_gate(registry_path, run_id, valuation_artifact_path)
    path = output_dir / f"ucits_fundability_gate_{run_id}.json"
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(
        "UCITS_FUNDABILITY_GATE_OK"
        f" | artifact={path}"
        f" | candidates={artifact['candidate_count']}"
        f" | not_fundable={artifact['not_fundable_count']}"
        " | candidate_promotion=false"
        " | portfolio_mutation=false"
        " | delivery=false"
    )
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--valuation-artifact", default=None)
    parser.add_argument("--valuation-dir", default=str(DEFAULT_VALUATION_DIR))
    args = parser.parse_args()

    valuation_artifact = Path(args.valuation_artifact) if args.valuation_artifact else _latest_file(Path(args.valuation_dir), "ucits_valuation_prices_*.json")
    write_fundability_gate(Path(args.registry), Path(args.output_dir), args.run_id or _run_id(), valuation_artifact)


if __name__ == "__main__":
    main()
