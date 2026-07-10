from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_delivery_closeout_manifest import validate

MANIFEST = Path("output/run_manifests/etf_eu_delivery_closeout_manifest_20260710_1755.json")


def _load() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_etf_eu_delivery_closeout_manifest_validates() -> None:
    result = validate(MANIFEST)
    assert result["status"] == "valid"
    assert result["receipt_confirmed"] is True
    assert result["next_package"] == "ETF-EU-MVP22_ROUTINE_WEEKLY_EU_REPORT_OPERATING_LOOP"


def test_closeout_manifest_is_redacted_and_does_not_store_raw_gmail_pdf() -> None:
    data = _load()
    assert data["raw_receipt_pdf_stored_in_github"] is False
    assert data["recipient_plaintext_values_exposed"] is False
    assert data["secret_values_exposed"] is False
    dumped = json.dumps(data)
    assert "@" not in dumped
    assert "MRKT_RPRTS_SMTP_PASS" not in dumped


def test_closeout_receipt_requires_manual_receipt_artifact() -> None:
    data = _load()
    receipt_path = Path(data["manual_receipt_confirmation_artifact"])
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["schema_version"] == "etf_eu_manual_receipt_confirmation_v1"
    assert receipt["receipt_confirmed"] is True
    assert receipt["raw_receipt_pdf_stored_in_github"] is False
    assert receipt["recipient_plaintext_values_exposed_in_artifact"] is False


def test_closeout_transport_and_authority_boundaries() -> None:
    data = _load()
    assert data["transport_attempted"] is True
    assert data["transport_success"] is True
    assert data["resend_performed"] is True
    assert data["send_executed"] is True
    assert data["delivery_success_closed"] is True
    assert data["receipt_confirmed"] is True
    assert data["valuation_grade"] is False
    assert data["funding_authority"] is False
    assert data["portfolio_mutation"] is False
    assert data["production_delivery_authority"] is False
