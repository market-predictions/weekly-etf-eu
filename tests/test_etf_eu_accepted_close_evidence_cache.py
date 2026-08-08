from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from pricing.accepted_close_evidence_cache import load_cache, provider_from_cache


REPORT_DATE = date(2026, 8, 5)
LINE = {
    "basket_id": "vwce_xetra_eur",
    "ticker": "VWCE",
    "isin": "IE00BK5BQT80",
    "venue_code": "XETR",
    "currency": "EUR",
    "exchange": "Xetra",
}


def test_repository_cache_is_valid_and_bound_to_original_actions_artifact() -> None:
    loaded = load_cache(REPORT_DATE)
    assert loaded is not None
    path, payload = loaded
    assert path.name == "ucits_close_evidence_2026-08-05.json"
    assert payload["source_workflow_run_id"] == 31051399761
    assert payload["source_workflow_head_sha"] == "476579ecc0644250d7d12a8f69784a279118d389"
    assert payload["source_actions_artifact"]["artifact_id"] == 8948609199
    assert payload["source_actions_artifact"]["artifact_digest"] == "sha256:631f90f24caabc271b1d290b519adf5c3e667cb717f35563f522d030cb49c55a"
    assert payload["source_actions_artifact"]["qualification_member_sha256"] == "02ad0fa5dd431eebadf73c370b6ab9fdc85a570332667a26234ad0d1758611d4"


def test_provider_replay_preserves_original_close_and_provider_identity() -> None:
    boerse = provider_from_cache(LINE, REPORT_DATE, "boerse_frankfurt_xetra")
    yahoo = provider_from_cache(LINE, REPORT_DATE, "yahoo_chart")
    assert boerse is not None and yahoo is not None
    assert boerse["close_price"] == 168.04
    assert yahoo["close_price"] == 168.04
    assert boerse["close_date"] == "2026-08-05"
    assert yahoo["close_date"] == "2026-08-05"
    assert boerse["provider_symbol"] == "XETR:IE00BK5BQT80"
    assert yahoo["provider_symbol"] == "VWCE.DE"
    assert boerse["retrieval_mode"] == "immutable_report_time_evidence_cache"
    assert boerse["identity_evidence"][0]["source_workflow_run_id"] == 31051399761


def test_identity_mismatch_is_rejected() -> None:
    bad = dict(LINE)
    bad["isin"] = "IE00WRONG0000"
    with pytest.raises(RuntimeError, match="Cached evidence identity mismatch"):
        provider_from_cache(bad, REPORT_DATE, "boerse_frankfurt_xetra")


def test_wrong_report_date_has_no_cache() -> None:
    assert load_cache(date(2026, 8, 4)) is None


def test_tampered_provider_set_is_rejected(tmp_path: Path) -> None:
    _, payload = load_cache(REPORT_DATE)  # type: ignore[misc]
    tampered = json.loads(json.dumps(payload))
    tampered["lines"][0]["providers"] = tampered["lines"][0]["providers"][:1]
    path = tmp_path / "ucits_close_evidence_2026-08-05.json"
    path.write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(RuntimeError, match="provider_set_mismatch"):
        load_cache(REPORT_DATE, tmp_path)


def test_tampered_report_date_is_rejected(tmp_path: Path) -> None:
    _, payload = load_cache(REPORT_DATE)  # type: ignore[misc]
    tampered = json.loads(json.dumps(payload))
    tampered["report_date"] = "2026-08-04"
    path = tmp_path / "ucits_close_evidence_2026-08-05.json"
    path.write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(RuntimeError, match="cache_report_date_mismatch"):
        load_cache(REPORT_DATE, tmp_path)
