from __future__ import annotations

from pathlib import Path

import pytest

from tools.validate_etf_eu_routine_report_request import validate


def _write_request(root: Path, *, extra: str = "", mode: str = "generate_validate_candidate", delivery: str = "false") -> Path:
    (root / "output/run_manifests").mkdir(parents=True)
    (root / "output/delivery").mkdir(parents=True)
    previous = root / "output/run_manifests/previous.json"
    closeout = root / "output/delivery/previous.json"
    previous.write_text("{}", encoding="utf-8")
    closeout.write_text("{}", encoding="utf-8")
    path = root / "request.md"
    path.write_text(
        "\n".join(
            [
                "schema_version=etf_eu_routine_report_request_v2",
                "artifact_type=etf_eu_routine_report_request",
                "run_id=20260807_220000",
                "report_date=2026-08-07",
                "report_suffix=260807",
                f"previous_routine_manifest={previous.relative_to(root)}",
                f"previous_delivery_closeout_manifest={closeout.relative_to(root)}",
                f"execution_mode={mode}",
                f"delivery_authority={delivery}",
                "recipient_plaintext_values_exposed=false",
                "secret_values_exposed=false",
                "raw_receipt_pdf_stored_in_github=false",
                extra,
            ]
        ),
        encoding="utf-8",
    )
    return path


def test_v2_candidate_request_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_request(tmp_path)
    monkeypatch.chdir(tmp_path)
    data = validate(Path("request.md"))
    assert data["execution_mode"] == "generate_validate_candidate"
    assert data["delivery_authority"] == "false"


def test_send_authority_cannot_be_embedded_in_candidate_request(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_request(tmp_path, extra="send_confirmation=confirm_guarded_send")
    monkeypatch.chdir(tmp_path)
    with pytest.raises(AssertionError, match="delivery-only keys"):
        validate(Path("request.md"))


def test_candidate_request_cannot_grant_delivery_authority(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_request(tmp_path, delivery="true")
    monkeypatch.chdir(tmp_path)
    with pytest.raises(AssertionError, match="cannot grant delivery authority"):
        validate(Path("request.md"))


def test_legacy_generate_validate_send_mode_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_request(tmp_path, mode="generate_validate_send")
    monkeypatch.chdir(tmp_path)
    with pytest.raises(AssertionError, match="candidate-only"):
        validate(Path("request.md"))
