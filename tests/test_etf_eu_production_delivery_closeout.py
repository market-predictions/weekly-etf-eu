from __future__ import annotations

import json
from pathlib import Path

from tools.validate_etf_eu_production_delivery_closeout import FORBIDDEN_CLOSEOUT_FIELDS, validate

CLOSEOUT = Path("output/run_manifests/etf_eu_production_delivery_closeout_manifest_20260711_175327.json")
TRANSPORT = Path("output/delivery/etf_eu_current_package_transport_result_20260711_175327.json")
DELIVERY = Path("output/delivery/etf_eu_current_package_delivery_evidence_20260711_175327.json")
RECEIPT = Path("output/delivery/etf_eu_current_package_receipt_evidence_20260711_175327.json")
ROUTINE = Path("output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_required_control_files_exist() -> None:
    assert Path("control/ETF_EU_PRODUCTION_DELIVERY_CLOSEOUT_CONTRACT_V1.md").exists()
    assert Path("control/ETF_EU_ROUTINE_WEEKLY_PRODUCTION_RUNBOOK_V1.md").exists()
    assert CLOSEOUT.exists()


def test_closeout_chain_validates() -> None:
    result = validate(CLOSEOUT, TRANSPORT, DELIVERY, RECEIPT, ROUTINE)
    assert result["status"] == "valid"
    assert result["routine_production_ready"] is True


def test_receipt_and_transport_ids_match() -> None:
    transport = _load(TRANSPORT)
    receipt = _load(RECEIPT)
    closeout = _load(CLOSEOUT)
    assert transport["run_id"] == receipt["runtime_run_id"] == closeout["runtime_run_id"]


def test_attachment_and_receipt_evidence_complete() -> None:
    closeout = _load(CLOSEOUT)
    assert closeout["receipt_confirmed"] is True
    assert closeout["attachment_count_seen"] == 4
    assert closeout["dutch_primary_pdf_seen"] is True
    assert closeout["english_companion_pdf_seen"] is True
    assert closeout["dutch_primary_html_seen"] is True
    assert closeout["english_companion_html_seen"] is True


def test_closeout_has_no_raw_mailbox_fields_or_authority_promotion() -> None:
    closeout = _load(CLOSEOUT)
    assert not (FORBIDDEN_CLOSEOUT_FIELDS & set(closeout))
    for field in [
        "recipient_plaintext_values_exposed",
        "secret_values_exposed",
        "raw_email_content_stored",
        "raw_receipt_pdf_stored_in_github",
        "valuation_grade",
        "funding_authority",
        "portfolio_mutation",
        "production_delivery_authority",
    ]:
        assert closeout[field] is False


def test_control_files_activate_routine_mode() -> None:
    system_index = Path("control/SYSTEM_INDEX.md").read_text(encoding="utf-8")
    current_state = Path("control/CURRENT_STATE.md").read_text(encoding="utf-8")
    next_actions = Path("control/NEXT_ACTIONS.md").read_text(encoding="utf-8")
    assert "ETF_EU_ROUTINE_WEEKLY_PRODUCTION_RUNBOOK_V1.md" in system_index
    assert "etf_eu_production_delivery_closeout_manifest_20260711_175327.json" in current_state
    assert "RUN_NEXT_ROUTINE_WEEKLY_ETF_EU_REPORT" in next_actions
