from __future__ import annotations

import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from tools.validate_etf_eu_ucits_symbol_registry_identity import (
    RegistryIdentityError,
    validate_registry_identity,
)

LIVE_REGISTRY = Path("config/ucits_symbol_registry.yml")
VALID_FIXTURE = Path("fixtures/ucits_identity/valid_bootstrap_registry.yml")
BAD_MISSING_ISIN = Path("fixtures/ucits_identity/bad_verified_candidate_missing_isin.yml")
BAD_PROXY_FUNDABLE = Path("fixtures/ucits_identity/bad_proxy_marked_fundable.yml")
BAD_MISSING_CURRENCY = Path("fixtures/ucits_identity/bad_exchange_line_missing_currency.yml")
BAD_ETC_FUNDABLE = Path("fixtures/ucits_identity/bad_etc_marked_fundable.yml")
BAD_PROXY_FLAG = Path("fixtures/ucits_identity/bad_research_proxy_missing_block_flag.yml")
VALIDATOR = Path("tools/validate_etf_eu_ucits_symbol_registry_identity.py")


def _load_fixture() -> dict:
    return yaml.safe_load(VALID_FIXTURE.read_text(encoding="utf-8"))


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "registry.yml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def test_current_live_registry_passes_bootstrap_validator():
    result = validate_registry_identity(LIVE_REGISTRY)
    assert result["funds_checked"] >= 1
    assert result["blocking_errors"] == 0


def test_valid_bootstrap_fixture_passes():
    result = validate_registry_identity(VALID_FIXTURE)
    assert result["funds_checked"] == 2
    assert result["research_proxies_checked"] == 2


def test_root_missing_schema_version_fails(tmp_path: Path):
    payload = _load_fixture()
    del payload["schema_version"]
    with pytest.raises(RegistryIdentityError, match="schema_version missing"):
        validate_registry_identity(_write(tmp_path, payload))


def test_wrong_canonical_identity_fails(tmp_path: Path):
    payload = _load_fixture()
    payload["canonical_identity"] = "ticker_first"
    with pytest.raises(RegistryIdentityError, match="canonical_identity must be isin_first"):
        validate_registry_identity(_write(tmp_path, payload))


def test_empty_funds_fails(tmp_path: Path):
    payload = _load_fixture()
    payload["funds"] = []
    with pytest.raises(RegistryIdentityError, match="funds must be non-empty list"):
        validate_registry_identity(_write(tmp_path, payload))


def test_fund_missing_required_field_fails(tmp_path: Path):
    payload = _load_fixture()
    del payload["funds"][0]["provider"]
    with pytest.raises(RegistryIdentityError, match="fund missing provider"):
        validate_registry_identity(_write(tmp_path, payload))


def test_verified_candidate_missing_isin_fails():
    with pytest.raises(RegistryIdentityError, match="verified candidate must have ISIN"):
        validate_registry_identity(BAD_MISSING_ISIN)


def test_fundable_candidate_with_pending_isin_fails(tmp_path: Path):
    payload = _load_fixture()
    fund = deepcopy(payload["funds"][0])
    fund["registry_id"] = "bad_fundable_pending_isin"
    fund["isin"] = "pending_verification"
    fund["investability_status"] = "fundable"
    fund["fundable_status"] = "fundable"
    payload["funds"] = [fund]
    with pytest.raises(RegistryIdentityError, match="actionable/fundable candidate must have ISIN"):
        validate_registry_identity(_write(tmp_path, payload))


def test_trading_line_missing_required_field_fails(tmp_path: Path):
    payload = _load_fixture()
    del payload["funds"][0]["trading_lines"][0]["provider_symbol"]
    with pytest.raises(RegistryIdentityError, match="trading line missing provider_symbol"):
        validate_registry_identity(_write(tmp_path, payload))


def test_verified_fundable_candidate_missing_trading_currency_fails():
    with pytest.raises(RegistryIdentityError, match="trading_currency must be non-empty"):
        validate_registry_identity(BAD_MISSING_CURRENCY)


def test_research_proxy_missing_block_flag_fails():
    with pytest.raises(RegistryIdentityError, match="proxy_must_not_be_funded must be true"):
        validate_registry_identity(BAD_PROXY_FLAG)


def test_research_proxy_wrong_purpose_fails(tmp_path: Path):
    payload = _load_fixture()
    payload["funds"][0]["research_proxies"][0]["purpose"] = "portfolio_candidate"
    with pytest.raises(RegistryIdentityError, match="research proxy purpose must be benchmark_reference_only"):
        validate_registry_identity(_write(tmp_path, payload))


def test_us_proxy_marked_fundable_fails():
    with pytest.raises(RegistryIdentityError, match="ticker/proxy collision requires safe non-fundable status"):
        validate_registry_identity(BAD_PROXY_FUNDABLE)


def test_etc_marked_fundable_under_ucits_only_policy_fails():
    with pytest.raises(RegistryIdentityError, match="ETC cannot be fundable under UCITS-only policy"):
        validate_registry_identity(BAD_ETC_FUNDABLE)


def test_candidate_marked_fundable_while_kid_pending_fails(tmp_path: Path):
    payload = _load_fixture()
    fund = payload["funds"][0]
    fund["priips_kid_status"] = "pending_verification"
    fund["investability_status"] = "fundable"
    fund["fundable_status"] = "fundable"
    with pytest.raises(RegistryIdentityError, match="pending priips_kid_status"):
        validate_registry_identity(_write(tmp_path, payload))


def test_candidate_marked_fundable_while_ucits_pending_fails(tmp_path: Path):
    payload = _load_fixture()
    fund = payload["funds"][0]
    fund["ucits_status"] = "pending_verification"
    fund["investability_status"] = "fundable"
    fund["fundable_status"] = "fundable"
    with pytest.raises(RegistryIdentityError, match="pending ucits_status"):
        validate_registry_identity(_write(tmp_path, payload))


def test_candidate_marked_fundable_while_exchange_line_pending_fails(tmp_path: Path):
    payload = _load_fixture()
    fund = payload["funds"][0]
    fund["investability_status"] = "fundable"
    fund["fundable_status"] = "fundable"
    fund["trading_lines"][0]["line_verification_status"] = "pending_exchange_line_verification"
    with pytest.raises(RegistryIdentityError, match="pending verification"):
        validate_registry_identity(_write(tmp_path, payload))


def test_ticker_proxy_collision_without_safe_status_fails(tmp_path: Path):
    payload = _load_fixture()
    fund = payload["funds"][1]
    fund["isin"] = "IE00BMC38736"
    fund["ucits_status"] = "confirmed"
    fund["investability_status"] = "fundable"
    fund["fundable_status"] = "fundable"
    fund["trading_lines"][0]["line_verification_status"] = "issuer_verified_bloomberg_ticker"
    fund["trading_lines"][0]["pricing_symbol_yahoo"] = "SMH.L"
    fund["trading_lines"][0]["pricing_status"] = "verified"
    with pytest.raises(RegistryIdentityError, match="ticker/proxy collision requires safe non-fundable status"):
        validate_registry_identity(_write(tmp_path, payload))


def test_pending_bootstrap_candidate_with_explicit_non_fundable_status_passes(tmp_path: Path):
    payload = _load_fixture()
    payload["funds"] = [payload["funds"][1]]
    result = validate_registry_identity(_write(tmp_path, payload))
    assert result["funds_checked"] == 1
    assert result["pending_items_detected"] > 0


def test_validator_prints_expected_ok_marker():
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(VALID_FIXTURE)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "ETF_EU_UCITS_SYMBOL_REGISTRY_IDENTITY_OK" in result.stdout
    assert "blocking_errors=0" in result.stdout
