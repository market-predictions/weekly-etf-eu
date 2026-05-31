from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT_DIR = Path("output/pricing")
US_PROXY_TICKERS = {"SPY", "QQQ", "SMH", "GLD", "GSG", "PPA", "PAVE", "URNM", "IWM", "TLT", "KWEB", "ICLN", "SOXX", "ITA", "GRID", "URA", "NLR"}
ALLOWED_STATUSES = {"verified_candidate_not_funded"}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _latest_candidate_file(output_dir: Path) -> Path:
    files = sorted(output_dir.glob("ucits_pricing_candidates_*.json"))
    if not files:
        raise RuntimeError(f"No UCITS pricing candidate artifacts found in {output_dir}")
    return files[-1]


def _as_str(value: Any) -> str:
    return str(value or "").strip()


def validate(path: Path) -> None:
    payload = _load_json(path)
    errors: list[str] = []
    if payload.get("schema_version") != "ucits_pricing_candidates_v1":
        errors.append("schema_version_must_be_ucits_pricing_candidates_v1")
    for field in ["portfolio_mutation", "production_delivery", "funding_authority"]:
        if payload.get(field) is not False:
            errors.append(f"top_level_{field}_must_be_false")
    candidates = payload.get("candidates") or []
    if not isinstance(candidates, list) or not candidates:
        errors.append("at_least_one_pricing_candidate_required")
    seen_keys: set[tuple[str, str]] = set()
    for idx, row in enumerate(candidates):
        label = f"candidate:{idx}:{_as_str(row.get('registry_id')) or 'unknown'}"
        for field in [
            "registry_id",
            "isin",
            "fund_name",
            "provider",
            "instrument_type",
            "investability_status",
            "ucits_status",
            "priips_kid_status",
            "exchange",
            "exchange_ticker",
            "trading_currency",
            "provider_symbol",
            "pricing_symbol_yahoo",
        ]:
            if not _as_str(row.get(field)) or _as_str(row.get(field)) in {"TBD", "pending_verification"}:
                errors.append(f"{label}:missing_or_pending_{field}")
        if _as_str(row.get("investability_status")) not in ALLOWED_STATUSES:
            errors.append(f"{label}:invalid_investability_status:{row.get('investability_status')}")
        for field in ["portfolio_mutation", "production_delivery", "funding_authority"]:
            if row.get(field) is not False:
                errors.append(f"{label}:{field}_must_be_false")
        exchange_ticker = _as_str(row.get("exchange_ticker")).upper()
        us_proxy = _as_str(row.get("us_research_proxy")).upper()
        if us_proxy and us_proxy not in US_PROXY_TICKERS:
            errors.append(f"{label}:unexpected_us_proxy:{us_proxy}")
        if exchange_ticker in US_PROXY_TICKERS and exchange_ticker == us_proxy:
            errors.append(f"{label}:exchange_ticker_equals_us_proxy:{exchange_ticker}")
        key = (_as_str(row.get("registry_id")), _as_str(row.get("pricing_symbol_yahoo")))
        if key in seen_keys:
            errors.append(f"{label}:duplicate_registry_pricing_symbol:{key}")
        seen_keys.add(key)
    if errors:
        raise RuntimeError("UCITS pricing candidate validation failed: " + "; ".join(errors))
    print(f"UCITS_PRICING_CANDIDATES_VALIDATION_OK | artifact={path} | candidates={len(candidates)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", default=None)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    artifact = Path(args.artifact) if args.artifact else _latest_candidate_file(Path(args.output_dir))
    validate(artifact)


if __name__ == "__main__":
    main()
