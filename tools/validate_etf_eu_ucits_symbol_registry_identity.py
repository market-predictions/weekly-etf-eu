from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

ROOT_SCHEMA = "ucits_symbol_registry_v1"
ROOT_IDENTITY = "isin_first"
FUND_REQUIRED = {
    "registry_id",
    "role",
    "us_research_proxy",
    "isin",
    "fund_name",
    "provider",
    "instrument_type",
    "ucits_status",
    "priips_kid_status",
    "investability_status",
    "fundable_status",
    "domicile",
    "base_currency",
    "distribution_policy",
    "replication_method",
    "benchmark_index",
    "ter_pct",
    "trading_lines",
    "research_proxies",
}
LINE_REQUIRED = {
    "exchange",
    "exchange_ticker",
    "trading_currency",
    "provider_symbol",
    "pricing_symbol_yahoo",
    "line_verification_status",
    "pricing_status",
}
PROXY_REQUIRED = {"us_proxy", "purpose", "proxy_must_not_be_funded"}
PENDING_VALUES = {"", "tbd", "pending_verification", "none", "null"}
UNSAFE_STATUS_TOKENS = {
    "fundable",
    "funded",
    "approved",
    "current_holding",
    "client_surface_current_truth",
    "production_ready",
}
SAFE_NEGATIVE_PREFIXES = ("not_", "candidate_requires_", "policy_review_required_")
SAFE_NEGATIVE_CONTAINS = ("not_funded", "not_fundable", "requires_full_verification", "requires_broker")


class RegistryIdentityError(RuntimeError):
    pass


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RegistryIdentityError("registry root must be an object")
    return payload


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _norm(value: Any) -> str:
    return _as_text(value).lower()


def _is_pending(value: Any) -> bool:
    return _norm(value) in PENDING_VALUES or _norm(value).startswith("pending_")


def _missing(required: set[str], payload: dict[str, Any]) -> list[str]:
    return sorted(required - set(payload))


def _is_unsafe_status(value: Any) -> bool:
    status = _norm(value)
    if not status:
        return False
    if status.startswith(SAFE_NEGATIVE_PREFIXES):
        return False
    if any(token in status for token in SAFE_NEGATIVE_CONTAINS):
        return False
    return any(token in status for token in UNSAFE_STATUS_TOKENS)


def _is_actionable_or_fundable(fund: dict[str, Any]) -> bool:
    return _is_unsafe_status(fund.get("investability_status")) or _is_unsafe_status(fund.get("fundable_status"))


def _is_verified_candidate(fund: dict[str, Any]) -> bool:
    return _norm(fund.get("investability_status")) == "verified_candidate_not_funded"


def _is_collision_safe(fund: dict[str, Any]) -> bool:
    if _is_actionable_or_fundable(fund):
        return False
    status_blob = " ".join(
        [
            _norm(fund.get("investability_status")),
            _norm(fund.get("fundable_status")),
            _norm(fund.get("ucits_status")),
        ]
    )
    notes = " ".join(_norm(note) for note in fund.get("notes", []) if isinstance(note, str))
    return any(token in status_blob for token in ("pending", "requires", "not_funded", "not_fundable")) or "isin-first" in notes or "isin first" in notes


def _validate_root(payload: dict[str, Any]) -> list[dict[str, str]]:
    if "schema_version" not in payload:
        raise RegistryIdentityError("schema_version missing")
    if payload["schema_version"] != ROOT_SCHEMA:
        raise RegistryIdentityError("schema_version must be ucits_symbol_registry_v1")
    if "canonical_identity" not in payload:
        raise RegistryIdentityError("canonical_identity missing")
    if payload["canonical_identity"] != ROOT_IDENTITY:
        raise RegistryIdentityError("canonical_identity must be isin_first")
    if "registry_status" not in payload:
        raise RegistryIdentityError("registry_status missing")
    funds = payload.get("funds")
    if not isinstance(funds, list) or not funds:
        raise RegistryIdentityError("funds must be non-empty list")
    return funds


def _validate_line(fund_id: str, fund: dict[str, Any], line: Any) -> None:
    if not isinstance(line, dict):
        raise RegistryIdentityError(f"{fund_id}: trading line must be object")
    missing = _missing(LINE_REQUIRED, line)
    if missing:
        raise RegistryIdentityError(f"{fund_id}: trading line missing {', '.join(missing)}")
    if not _as_text(line.get("exchange_ticker")):
        raise RegistryIdentityError(f"{fund_id}: exchange_ticker must be non-empty")
    if not _as_text(line.get("trading_currency")):
        raise RegistryIdentityError(f"{fund_id}: trading_currency must be non-empty")
    if _is_actionable_or_fundable(fund):
        if _is_pending(line.get("trading_currency")):
            raise RegistryIdentityError(f"{fund_id}: actionable/fundable line cannot have pending trading_currency")
        if _is_pending(line.get("line_verification_status")):
            raise RegistryIdentityError(f"{fund_id}: actionable/fundable line cannot have pending verification")


def _validate_proxy(fund_id: str, proxy: Any) -> None:
    if not isinstance(proxy, dict):
        raise RegistryIdentityError(f"{fund_id}: research proxy must be object")
    missing = _missing(PROXY_REQUIRED, proxy)
    if missing:
        raise RegistryIdentityError(f"{fund_id}: research proxy missing {', '.join(missing)}")
    if proxy.get("purpose") != "benchmark_reference_only":
        raise RegistryIdentityError(f"{fund_id}: research proxy purpose must be benchmark_reference_only")
    if proxy.get("proxy_must_not_be_funded") is not True:
        raise RegistryIdentityError(f"{fund_id}: proxy_must_not_be_funded must be true")


def _validate_fund(fund: Any) -> tuple[int, int, int]:
    if not isinstance(fund, dict):
        raise RegistryIdentityError("fund entry must be object")
    fund_id = _as_text(fund.get("registry_id")) or "unknown_fund"
    missing = _missing(FUND_REQUIRED, fund)
    if missing:
        raise RegistryIdentityError(f"{fund_id}: fund missing {', '.join(missing)}")

    if _is_verified_candidate(fund) and _is_pending(fund.get("isin")):
        raise RegistryIdentityError(f"{fund_id}: verified candidate must have ISIN")
    if _is_actionable_or_fundable(fund) and _is_pending(fund.get("isin")):
        raise RegistryIdentityError(f"{fund_id}: actionable/fundable candidate must have ISIN")
    if _norm(fund.get("ucits_status")) == "confirmed" and _is_pending(fund.get("isin")):
        raise RegistryIdentityError(f"{fund_id}: confirmed UCITS status requires ISIN")

    if not _as_text(fund.get("ucits_status")):
        raise RegistryIdentityError(f"{fund_id}: ucits_status must be non-empty")
    if not _as_text(fund.get("priips_kid_status")):
        raise RegistryIdentityError(f"{fund_id}: priips_kid_status must be non-empty")
    if _is_actionable_or_fundable(fund):
        for key in ("ucits_status", "priips_kid_status", "isin"):
            if _is_pending(fund.get(key)):
                raise RegistryIdentityError(f"{fund_id}: actionable/fundable candidate cannot have pending {key}")
        if _norm(fund.get("instrument_type")) == "etc":
            raise RegistryIdentityError(f"{fund_id}: ETC cannot be fundable under UCITS-only policy")
        if _norm(fund.get("ucits_status")) == "not_ucits_etc":
            raise RegistryIdentityError(f"{fund_id}: non-UCITS ETC cannot be fundable")

    trading_lines = fund.get("trading_lines")
    if not isinstance(trading_lines, list) or not trading_lines:
        raise RegistryIdentityError(f"{fund_id}: trading_lines must be non-empty list")
    for line in trading_lines:
        _validate_line(fund_id, fund, line)

    proxies = fund.get("research_proxies")
    if not isinstance(proxies, list) or not proxies:
        raise RegistryIdentityError(f"{fund_id}: research_proxies must be non-empty list")
    for proxy in proxies:
        _validate_proxy(fund_id, proxy)

    us_proxy = _norm(fund.get("us_research_proxy"))
    for line in trading_lines:
        if us_proxy and us_proxy == _norm(line.get("exchange_ticker")) and not _is_collision_safe(fund):
            raise RegistryIdentityError(f"{fund_id}: ticker/proxy collision requires safe non-fundable status")

    pending_count = 0
    for key, value in fund.items():
        if key in {"trading_lines", "research_proxies", "evidence", "notes"}:
            continue
        if _is_pending(value):
            pending_count += 1
    return 1, len(trading_lines), len(proxies), pending_count


def validate_registry_identity(path: Path) -> dict[str, int]:
    payload = _load_yaml(path)
    funds = _validate_root(payload)
    funds_checked = trading_lines_checked = research_proxies_checked = pending_items_detected = 0
    for fund in funds:
        fund_count, line_count, proxy_count, pending_count = _validate_fund(fund)
        funds_checked += fund_count
        trading_lines_checked += line_count
        research_proxies_checked += proxy_count
        pending_items_detected += pending_count
    return {
        "funds_checked": funds_checked,
        "trading_lines_checked": trading_lines_checked,
        "research_proxies_checked": research_proxies_checked,
        "pending_items_detected": pending_items_detected,
        "blocking_errors": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("registry")
    args = parser.parse_args()
    result = validate_registry_identity(Path(args.registry))
    print(
        "ETF_EU_UCITS_SYMBOL_REGISTRY_IDENTITY_OK | "
        f"funds_checked={result['funds_checked']} | "
        f"trading_lines_checked={result['trading_lines_checked']} | "
        f"research_proxies_checked={result['research_proxies_checked']} | "
        f"pending_items_detected={result['pending_items_detected']} | blocking_errors=0"
    )


if __name__ == "__main__":
    main()
