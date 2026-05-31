from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("PyYAML is required for UCITS investability validation") from exc

DEFAULT_REGISTRY = Path("config/ucits_symbol_registry.yml")
FUNDABLE_STATUSES = {"fundable", "verified_fundable"}
CANDIDATE_STATUSES = {"candidate_requires_verification", "verified_candidate_not_funded", "policy_review_required_not_ucits"}
PENDING_VALUES = {"", "TBD", "pending_verification", None}


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _as_str(value: Any) -> str:
    return str(value or "").strip()


def _is_pending(value: Any) -> bool:
    return value in PENDING_VALUES or _as_str(value) in PENDING_VALUES


def validate(path: Path) -> None:
    payload = _load_yaml(path)
    errors: list[str] = []
    funds = payload.get("funds") or []
    fundable_count = 0
    blocked_count = 0
    candidate_count = 0
    for fund in funds:
        rid = _as_str(fund.get("registry_id")) or _as_str(fund.get("fund_name")) or "unknown_fund"
        status = _as_str(fund.get("investability_status"))
        instrument_type = _as_str(fund.get("instrument_type"))
        ucits_status = _as_str(fund.get("ucits_status"))
        kid_status = _as_str(fund.get("priips_kid_status"))
        if status in FUNDABLE_STATUSES:
            fundable_count += 1
            if instrument_type != "ETF":
                errors.append(f"{rid}:fundable_must_be_etf_not_{instrument_type}")
            if ucits_status not in {"confirmed", "confirmed_by_fund_name"}:
                errors.append(f"{rid}:fundable_requires_ucits_confirmed")
            if kid_status != "available":
                errors.append(f"{rid}:fundable_requires_priips_kid_available")
            for field in ["isin", "provider", "domicile", "base_currency", "distribution_policy", "replication_method", "benchmark_index", "ter_pct"]:
                if _is_pending(fund.get(field)):
                    errors.append(f"{rid}:fundable_missing_{field}")
            good_lines = 0
            for line in fund.get("trading_lines") or []:
                if all(not _is_pending(line.get(field)) for field in ["exchange", "exchange_ticker", "trading_currency", "provider_symbol", "pricing_symbol_yahoo"]):
                    good_lines += 1
            if good_lines < 1:
                errors.append(f"{rid}:fundable_requires_at_least_one_complete_trading_line")
        elif status in CANDIDATE_STATUSES:
            candidate_count += 1
            if instrument_type == "ETC" or ucits_status == "not_ucits_etc":
                blocked_count += 1
                if "not_fundable" not in _as_str(fund.get("fundable_status")):
                    errors.append(f"{rid}:non_ucits_etc_requires_not_fundable_status")
        else:
            errors.append(f"{rid}:unknown_investability_status:{status}")
    if fundable_count > 0:
        errors.append("bootstrap_phase_must_not_mark_any_candidate_fundable_yet")
    if candidate_count < 1:
        errors.append("at_least_one_candidate_required")
    if errors:
        raise RuntimeError("UCITS investability contract validation failed: " + "; ".join(errors))
    print(f"UCITS_INVESTABILITY_CONTRACT_OK | candidates={candidate_count} | fundable={fundable_count} | blocked_policy_review={blocked_count} | path={path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    args = parser.parse_args()
    validate(Path(args.registry))


if __name__ == "__main__":
    main()
