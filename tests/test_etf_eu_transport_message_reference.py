from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.validate_etf_eu_current_package_transport_runner import validate_result


def _write_result(tmp_path: Path, *, reference: str | None) -> Path:
    evidence = tmp_path / "evidence.json"
    evidence.write_text("{}\n", encoding="utf-8")
    result = {
        "schema_version": "etf_eu_current_package_transport_result_v1",
        "delivery_mode": "send",
        "transport_attempted": True,
        "transport_success": True,
        "recipient_plaintext_values_exposed": False,
        "secret_values_exposed": False,
        "raw_receipt_pdf_stored_in_github": False,
        "receipt_confirmed": False,
        "delivery_evidence_path": str(evidence),
        "message_reference_hash": reference,
    }
    path = tmp_path / "result.json"
    path.write_text(json.dumps(result) + "\n", encoding="utf-8")
    return path


def test_success_accepts_redacted_message_reference_hash(tmp_path: Path) -> None:
    path = _write_result(tmp_path, reference="sha256:" + "a" * 64)
    assert validate_result(path)["status"] == "valid"


def test_success_rejects_missing_message_reference(tmp_path: Path) -> None:
    path = _write_result(tmp_path, reference=None)
    with pytest.raises(AssertionError, match="redacted message reference"):
        validate_result(path)
