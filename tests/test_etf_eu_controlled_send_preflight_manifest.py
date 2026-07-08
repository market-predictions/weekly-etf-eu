from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.build_etf_eu_controlled_send_preflight_manifest import build_controlled_send_preflight_manifest
from tools.validate_etf_eu_controlled_send_preflight_manifest import validate


def _base_manifest(path: Path) -> Path:
    payload = {
        "schema_version": "etf_eu_delivery_manifest_v1",
        "run_id": "base",
        "created_at_utc": "2026-07-08T00:00:00Z",
        "report_date": "2026-07-08",
        "status": "blocked_design_only",
        "delivery_enabled": False,
        "gates": {
            "main_workflow_green": True,
            "dutch_first_report_contract_green": True,
            "fundability_rules_clear": True,
            "delivery_manifest_exists": True,
            "receipt_path_exists": False,
        },
        "artifacts": {
            "dutch_report_path": "old_nl.md",
            "english_report_path": "old_en.md",
            "valuation_artifact_path": "valuation.json",
            "fundability_artifact_path": "fundability.json",
            "validation_evidence_paths": ["validation.json"],
        },
        "receipt": {"receipt_required": True, "receipt_path": "", "receipt_status": "not_created"},
        "authority": {
            "funding_authority": False,
            "portfolio_mutation": False,
            "valuation_grade_promotion": False,
            "candidate_promotion_to_fundable": False,
            "pdf_generation": False,
            "email_delivery": False,
            "delivery_receipt": False,
            "production_delivery": False,
        },
        "blockers": ["blocked"],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _sender_preflight(path: Path, *, send_performed: bool = False) -> Path:
    payload = {
        "schema_version": "etf_eu_sender_preflight_v1",
        "delivery_mode": "preflight_no_send",
        "report_suffix": "260708",
        "dutch_primary_report_path": "output/weekly_etf_eu_review_nl_260708.md",
        "english_companion_report_path": "output/weekly_etf_eu_review_260708.md",
        "dutch_primary_exists": True,
        "english_companion_exists": True,
        "preflight_no_send_mode_supported": True,
        "us_report_name_assumption_detected": False,
        "send_performed": send_performed,
        "production_delivery": False,
        "email_delivery": False,
        "delivery_receipt": False,
        "delivery_success_claimed": False,
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_preflight_manifest_shape_and_boundaries(tmp_path: Path) -> None:
    base = _base_manifest(tmp_path / "base.json")
    sender = json.loads(_sender_preflight(tmp_path / "sender.json").read_text(encoding="utf-8"))
    sender["sender_preflight_artifact_path"] = str(tmp_path / "sender.json")
    manifest = build_controlled_send_preflight_manifest(
        run_id="20260708_000000",
        report_date="2026-07-08",
        sender_preflight=sender,
        base_delivery_manifest_path=base,
        created_at_utc="2026-07-08T00:00:00Z",
    )

    assert manifest["status"] == "ready_for_future_delivery"
    assert manifest["delivery_enabled"] is False
    assert manifest["receipt"]["receipt_status"] == "pending"
    assert manifest["receipt"]["receipt_path"] == "output/delivery/pending_receipt_20260708_000000.json"
    assert not Path(manifest["receipt"]["receipt_path"]).exists()
    assert manifest["artifacts"]["dutch_report_path"] == "output/weekly_etf_eu_review_nl_260708.md"
    assert manifest["artifacts"]["english_report_path"] == "output/weekly_etf_eu_review_260708.md"
    for key in ["email_delivery", "production_delivery", "delivery_receipt", "pdf_generation"]:
        assert manifest["authority"][key] is False
    assert manifest["blockers"]


def test_validator_accepts_safe_preflight_manifest(tmp_path: Path) -> None:
    base = _base_manifest(tmp_path / "base.json")
    sender_path = _sender_preflight(tmp_path / "sender.json")
    sender = json.loads(sender_path.read_text(encoding="utf-8"))
    sender["sender_preflight_artifact_path"] = str(sender_path)
    manifest = build_controlled_send_preflight_manifest(
        run_id="20260708_000000",
        report_date="2026-07-08",
        sender_preflight=sender,
        base_delivery_manifest_path=base,
        created_at_utc="2026-07-08T00:00:00Z",
    )
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = validate(manifest_path, sender_path)

    assert result["status"] == "valid"
    assert result["manifest_status"] == "ready_for_future_delivery"
    assert result["delivery_enabled"] is False
    assert result["receipt_status"] == "pending"
    assert result["receipt_file_created"] is False


def test_validator_rejects_sent_status(tmp_path: Path) -> None:
    base = _base_manifest(tmp_path / "base.json")
    sender_path = _sender_preflight(tmp_path / "sender.json")
    sender = json.loads(sender_path.read_text(encoding="utf-8"))
    manifest = build_controlled_send_preflight_manifest(run_id="x", report_date="2026-07-08", sender_preflight=sender, base_delivery_manifest_path=base)
    manifest["status"] = "sent"
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises((AssertionError, RuntimeError)):
        validate(manifest_path, sender_path)


def test_validator_rejects_delivery_enabled_true(tmp_path: Path) -> None:
    base = _base_manifest(tmp_path / "base.json")
    sender_path = _sender_preflight(tmp_path / "sender.json")
    sender = json.loads(sender_path.read_text(encoding="utf-8"))
    manifest = build_controlled_send_preflight_manifest(run_id="x", report_date="2026-07-08", sender_preflight=sender, base_delivery_manifest_path=base)
    manifest["delivery_enabled"] = True
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises((AssertionError, RuntimeError)):
        validate(manifest_path, sender_path)


def test_validator_rejects_receipt_status_created(tmp_path: Path) -> None:
    base = _base_manifest(tmp_path / "base.json")
    sender_path = _sender_preflight(tmp_path / "sender.json")
    sender = json.loads(sender_path.read_text(encoding="utf-8"))
    manifest = build_controlled_send_preflight_manifest(run_id="x", report_date="2026-07-08", sender_preflight=sender, base_delivery_manifest_path=base)
    manifest["receipt"]["receipt_status"] = "created"
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises((AssertionError, RuntimeError)):
        validate(manifest_path, sender_path)


def test_validator_rejects_sender_preflight_send_performed(tmp_path: Path) -> None:
    base = _base_manifest(tmp_path / "base.json")
    sender_path = _sender_preflight(tmp_path / "sender.json", send_performed=True)
    sender = json.loads(sender_path.read_text(encoding="utf-8"))

    with pytest.raises(RuntimeError):
        build_controlled_send_preflight_manifest(run_id="x", report_date="2026-07-08", sender_preflight=sender, base_delivery_manifest_path=base)
