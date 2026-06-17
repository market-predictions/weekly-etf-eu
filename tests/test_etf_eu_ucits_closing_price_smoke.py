from __future__ import annotations

import copy
from pathlib import Path

import pytest

from tools.fetch_etf_eu_ucits_closing_price_smoke import (
    build_smoke_artifact,
    extract_price_candidates,
)
from tools.validate_etf_eu_ucits_closing_price_smoke import (
    ClosingPriceSmokeError,
    validate_closing_price_smoke,
)

PRICING_REGISTRY_FIXTURE = Path("fixtures/pricing/etf_eu_ucits_symbol_registry_pricing_fixture.yml")
PRICE_FIXTURE = Path("fixtures/pricing/etf_eu_ucits_closing_price_smoke_fixture.json")
LIVE_REGISTRY = Path("config/ucits_symbol_registry.yml")


def _artifact(tmp_path: Path) -> dict:
    output = tmp_path / "price_smoke.json"
    return build_smoke_artifact(
        registry=PRICING_REGISTRY_FIXTURE,
        output=output,
        run_id="test_run",
        fixture_prices_path=PRICE_FIXTURE,
    )


def _artifact_path(tmp_path: Path) -> Path:
    output = tmp_path / "price_smoke.json"
    build_smoke_artifact(
        registry=PRICING_REGISTRY_FIXTURE,
        output=output,
        run_id="test_run",
        fixture_prices_path=PRICE_FIXTURE,
    )
    return output


def _write_json(tmp_path: Path, payload: dict) -> Path:
    import json

    path = tmp_path / "mutated.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_fixture_mode_fetcher_writes_valid_artifact(tmp_path: Path):
    output = _artifact_path(tmp_path)
    assert output.exists()
    result = validate_closing_price_smoke(output)
    assert result["prices_found"] == 1
    assert result["symbols_skipped"] == 1


def test_valid_artifact_passes_validator(tmp_path: Path):
    result = validate_closing_price_smoke(_artifact_path(tmp_path))
    assert result["selected_next_package"] == "WP14F"


def test_bad_schema_fails(tmp_path: Path):
    payload = _artifact(tmp_path)
    payload["schema_version"] = "bad"
    with pytest.raises(ClosingPriceSmokeError, match="bad schema_version"):
        validate_closing_price_smoke(_write_json(tmp_path, payload))


def test_bad_status_fails(tmp_path: Path):
    payload = _artifact(tmp_path)
    payload["status"] = "bad"
    with pytest.raises(ClosingPriceSmokeError, match="bad status"):
        validate_closing_price_smoke(_write_json(tmp_path, payload))


def test_missing_source_policy_fails(tmp_path: Path):
    payload = _artifact(tmp_path)
    del payload["source_policy"]
    with pytest.raises(ClosingPriceSmokeError, match="source_policy missing"):
        validate_closing_price_smoke(_write_json(tmp_path, payload))


@pytest.mark.parametrize("flag", ["us_proxy_substitution_allowed", "paid_api_required", "secrets_required"])
def test_source_policy_false_flags_fail_when_true(tmp_path: Path, flag: str):
    payload = _artifact(tmp_path)
    payload["source_policy"][flag] = True
    with pytest.raises(ClosingPriceSmokeError, match=f"source_policy.{flag} must be false"):
        validate_closing_price_smoke(_write_json(tmp_path, payload))


def test_summary_count_mismatch_fails(tmp_path: Path):
    payload = _artifact(tmp_path)
    payload["summary"]["prices_found"] = 99
    with pytest.raises(ClosingPriceSmokeError, match="summary count mismatch"):
        validate_closing_price_smoke(_write_json(tmp_path, payload))


def test_empty_prices_and_failures_fails(tmp_path: Path):
    payload = _artifact(tmp_path)
    payload["prices"] = []
    payload["failures"] = []
    payload["summary"]["prices_found"] = 0
    payload["summary"]["symbols_skipped"] = 0
    payload["summary"]["pricing_symbols_attempted"] = 0
    with pytest.raises(ClosingPriceSmokeError, match="prices and failures cannot both be empty"):
        validate_closing_price_smoke(_write_json(tmp_path, payload))


def test_price_row_missing_required_field_fails(tmp_path: Path):
    payload = _artifact(tmp_path)
    del payload["prices"][0]["isin"]
    with pytest.raises(ClosingPriceSmokeError, match="price row missing"):
        validate_closing_price_smoke(_write_json(tmp_path, payload))


def test_price_row_zero_close_fails(tmp_path: Path):
    payload = _artifact(tmp_path)
    payload["prices"][0]["close"] = 0
    with pytest.raises(ClosingPriceSmokeError, match="price row close must be positive"):
        validate_closing_price_smoke(_write_json(tmp_path, payload))


def test_price_row_missing_close_date_fails(tmp_path: Path):
    payload = _artifact(tmp_path)
    payload["prices"][0]["close_date"] = ""
    with pytest.raises(ClosingPriceSmokeError, match="price row close_date missing"):
        validate_closing_price_smoke(_write_json(tmp_path, payload))


def test_failure_row_missing_required_field_fails(tmp_path: Path):
    payload = _artifact(tmp_path)
    del payload["failures"][0]["reason"]
    with pytest.raises(ClosingPriceSmokeError, match="failure row missing"):
        validate_closing_price_smoke(_write_json(tmp_path, payload))


def test_authority_flag_true_fails(tmp_path: Path):
    payload = _artifact(tmp_path)
    payload["authority"]["production_delivery"] = True
    with pytest.raises(ClosingPriceSmokeError, match="authority.production_delivery must be false"):
        validate_closing_price_smoke(_write_json(tmp_path, payload))


def test_wrong_selected_next_package_fails(tmp_path: Path):
    payload = _artifact(tmp_path)
    payload["selected_next_package"] = "WP14E"
    with pytest.raises(ClosingPriceSmokeError, match="selected_next_package"):
        validate_closing_price_smoke(_write_json(tmp_path, payload))


def test_pending_pricing_symbol_is_skipped(tmp_path: Path):
    payload = _artifact(tmp_path)
    skipped = [row for row in payload["failures"] if row["status"] == "skipped_pending_symbol"]
    assert len(skipped) == 1
    assert skipped[0]["pricing_symbol"] == "pending_verification"


def test_fixture_valid_symbol_records_price_found(tmp_path: Path):
    payload = _artifact(tmp_path)
    assert payload["prices"][0]["status"] == "price_found"
    assert payload["prices"][0]["pricing_symbol"] == "CSPX.L"
    assert payload["prices"][0]["close"] > 0


def test_live_registry_extraction_includes_only_non_pending_symbols():
    candidates, failures, seen = extract_price_candidates(LIVE_REGISTRY)
    symbols = {candidate.pricing_symbol for candidate in candidates}
    assert "CSPX.L" in symbols
    assert "SXR8.DE" in symbols
    assert "pending_verification" not in symbols
    assert seen["trading_lines_seen"] >= len(candidates)
    assert any(row["status"] == "skipped_pending_symbol" for row in failures)


def test_us_proxy_substitution_not_allowed(tmp_path: Path):
    payload = _artifact(tmp_path)
    payload["prices"][0]["pricing_symbol"] = "SPY"
    with pytest.raises(ClosingPriceSmokeError, match="U.S. proxy pricing substitution"):
        validate_closing_price_smoke(_write_json(tmp_path, payload))


def test_zero_price_artifact_selects_source_review(tmp_path: Path):
    payload = _artifact(tmp_path)
    payload["prices"] = []
    payload["failures"] = [
        {
            "registry_id": "core_us_equity_cspx_fixture",
            "exchange_ticker": "CSPX",
            "pricing_symbol": "CSPX.L",
            "status": "source_error",
            "reason": "fixture source unavailable",
        }
    ]
    payload["summary"]["prices_found"] = 0
    payload["summary"]["prices_missing"] = 0
    payload["summary"]["symbols_skipped"] = 0
    payload["summary"]["source_errors"] = 1
    payload["summary"]["pricing_symbols_attempted"] = 1
    payload["selected_next_package"] = "WP14F_SOURCE_REVIEW"
    result = validate_closing_price_smoke(_write_json(tmp_path, payload))
    assert result["selected_next_package"] == "WP14F_SOURCE_REVIEW"
