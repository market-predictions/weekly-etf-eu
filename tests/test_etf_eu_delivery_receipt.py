import json
from pathlib import Path

import pytest

from tools.validate_etf_eu_delivery_receipt import validate_delivery_receipt

SAMPLE = {
    "schema_version": "etf_eu_delivery_receipt_v1",
    "run_id": "20260617_000000",
    "created_at_utc": "2026-06-17T00:00:00Z",
    "report_date": "2026-06-17",
    "status": "sample_only_not_delivery",
    "receipt_type": "sample_only",
    "delivery_attempted": False,
    "delivery_success": False,
    "send_attempted": False,
    "email_delivery": False,
    "production_delivery": False,
    "delivery_receipt": False,
    "pdf_generation": False,
    "recipient_activation": False,
    "mail_transport_enabled": False,
    "channel": "none",
    "recipient_reference": None,
    "delivery_artifact_paths": [],
    "provider_confirmation": None,
    "transport_message_id": None,
    "blockers": [
        "sample receipt only",
        "no delivery attempted",
        "no provider confirmation",
        "no recipient activation",
        "real delivery not authorized",
    ],
}


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "receipt.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _copy_sample() -> dict:
    return json.loads(json.dumps(SAMPLE))


def test_sample_receipt_validates_from_repo_file():
    validate_delivery_receipt(Path("output/delivery/etf_eu_delivery_receipt_sample_20260617_000000.json"))


def test_sample_receipt_validates(tmp_path: Path):
    result = validate_delivery_receipt(_write(tmp_path, SAMPLE))
    assert result["status"] == "sample_only_not_delivery_valid"
    assert result["delivery_attempted"] is False
    assert result["delivery_success"] is False
    assert result["production_delivery"] is False


def test_unsupported_schema_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["schema_version"] = "bad"
    with pytest.raises(RuntimeError, match="unsupported schema_version"):
        validate_delivery_receipt(_write(tmp_path, payload))


def test_wrong_status_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["status"] = "sent"
    with pytest.raises(RuntimeError, match="status must be sample_only_not_delivery"):
        validate_delivery_receipt(_write(tmp_path, payload))


def test_wrong_receipt_type_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["receipt_type"] = "provider"
    with pytest.raises(RuntimeError, match="receipt_type must be sample_only"):
        validate_delivery_receipt(_write(tmp_path, payload))


@pytest.mark.parametrize(
    "flag",
    [
        "delivery_attempted",
        "delivery_success",
        "send_attempted",
        "email_delivery",
        "production_delivery",
        "delivery_receipt",
        "pdf_generation",
        "recipient_activation",
        "mail_transport_enabled",
    ],
)
def test_false_flags_true_fail(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload[flag] = True
    with pytest.raises(RuntimeError, match=f"{flag} must remain false"):
        validate_delivery_receipt(_write(tmp_path, payload))


def test_live_channel_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["channel"] = "email"
    with pytest.raises(RuntimeError, match="channel must be none"):
        validate_delivery_receipt(_write(tmp_path, payload))


def test_non_null_recipient_reference_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["recipient_reference"] = "sample-client"
    with pytest.raises(RuntimeError, match="recipient_reference must be null"):
        validate_delivery_receipt(_write(tmp_path, payload))


def test_non_null_provider_confirmation_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["provider_confirmation"] = "provider-ok"
    with pytest.raises(RuntimeError, match="provider_confirmation must be null"):
        validate_delivery_receipt(_write(tmp_path, payload))


def test_non_null_transport_message_id_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["transport_message_id"] = "msg-1234567890abcdef"
    with pytest.raises(RuntimeError, match="transport_message_id must be null"):
        validate_delivery_receipt(_write(tmp_path, payload))


def test_non_empty_delivery_artifact_paths_fail(tmp_path: Path):
    payload = _copy_sample()
    payload["delivery_artifact_paths"] = ["output/sent.pdf"]
    with pytest.raises(RuntimeError, match="delivery_artifact_paths must be an empty list"):
        validate_delivery_receipt(_write(tmp_path, payload))


def test_missing_required_blocker_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["blockers"] = ["sample receipt only"]
    with pytest.raises(RuntimeError, match="missing blocker"):
        validate_delivery_receipt(_write(tmp_path, payload))


def test_missing_required_top_level_field_fails(tmp_path: Path):
    payload = _copy_sample()
    del payload["run_id"]
    with pytest.raises(RuntimeError, match="missing top-level key"):
        validate_delivery_receipt(_write(tmp_path, payload))


def test_live_proof_like_nested_value_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["metadata"] = {"message_id": "1234567890abcdef1234567890abcdef"}
    with pytest.raises(RuntimeError, match="live-delivery-proof-like"):
        validate_delivery_receipt(_write(tmp_path, payload))
