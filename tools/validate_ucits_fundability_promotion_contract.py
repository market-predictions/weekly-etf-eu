from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("PyYAML is required for UCITS fundability validation") from exc

PLACEHOLDER_VALUES = {"", "TBD", "pending_verification", "primary_line_pending_verification"}


def _as_str(value: Any) -> str:
    return str(value if value is not None else "").strip()


def _is_placeholder(value: Any) -> bool:
    return _as_str(value) in PLACEHOLDER_VALUES


def _funds(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return list(payload.get("funds") or [])


def _has_verified_trading_line(fund: dict[str, Any]) -> bool:
    for line in fund.get("trading_lines") or []:
        if not _is_placeholder(line.get("exchange")) and not _is_placeholder(line.get("exchange_ticker")) and not _is_placeholder(line.get("trading_currency")) and not _is_placeholder(line.get("pricing_symbol_yahoo")):
            return True
    return False


def validate_registry(path: Path) -> None:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    errors: list[str] = []
    fundable_count = 0

    for fund in _funds(payload):
        registry_id = _as_str(fund.get("registry_id")) or "unknown"
        fundable_status = _as_str(fund.get("fundable_status"))
        investability_status = _as_str(fund.get("investability_status"))
        instrument_type = _as_str(fund.get("instrument_type"))
        ucits_status = _as_str(fund.get("ucits_status"))
        kid_status = _as_str(fund.get("priips_kid_status"))
        us_proxy = _as_str(fund.get("us_research_proxy"))

        if fundable_status == "fundable":
            fundable_count += 1
            if investability_status != "fundable":
                errors.append(f"{registry_id}:fundable_status_requires_investability_status_fundable")
            if instrument_type != "ETF":
                errors.append(f"{registry_id}:fundable_status_requires_etf_under_current_ucits_policy")
            if "confirmed" not in ucits_status:
                errors.append(f"{registry_id}:fundable_status_requires_confirmed_ucits_status")
            if kid_status != "available":
                errors.append(f"{registry_id}:fundable_status_requires_kid_available")
            if not _has_verified_trading_line(fund):
                errors.append(f"{registry_id}:fundable_status_requires_verified_trading_line")
            if us_proxy and us_proxy != "TBD":
                # U.S. proxy is allowed only as research context, never as the funded holding.
                pass

        if instrument_type == "ETC" and "fundable" in fundable_status and "not_fundable" not in fundable_status:
            errors.append(f"{registry_id}:etc_must_not_be_fundable_under_current_ucits_only_policy")
        if investability_status == "verified_candidate_not_funded" and fundable_status == "fundable":
            errors.append(f"{registry_id}:verified_candidate_not_funded_must_not_be_auto_promoted")

    if fundable_count:
        errors.append("current_bootstrap_registry_must_not_have_fundable_candidates_without_separate_decision")
    if errors:
        raise RuntimeError("UCITS fundability promotion validation failed: " + "; ".join(errors))
    print(f"UCITS_FUNDABILITY_PROMOTION_CONTRACT_OK | registry={path} | fundable_candidates=0")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default="config/ucits_symbol_registry.yml")
    args = parser.parse_args()
    validate_registry(Path(args.registry))


if __name__ == "__main__":
    main()
