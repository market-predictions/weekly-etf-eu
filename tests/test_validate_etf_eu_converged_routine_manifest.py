from __future__ import annotations

import hashlib
from pathlib import Path

from tools.validate_etf_eu_converged_routine_manifest import validate


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _file_record(path: Path) -> dict[str, object]:
    path.write_text("fixture\n", encoding="utf-8")
    return {"path": str(path), "sha256": _sha(path), "size_bytes": path.stat().st_size}


def _state_record(path: Path) -> dict[str, str]:
    path.write_text("{}\n", encoding="utf-8")
    return {"path": str(path), "sha256": _sha(path)}


def _base_manifest(tmp_path: Path) -> dict[str, object]:
    files = {
        role: _file_record(tmp_path / f"{role}.dat")
        for role in ("nl_html", "nl_pdf", "en_html", "en_pdf")
    }
    state_artifacts = {
        role: _state_record(tmp_path / f"{role}.json")
        for role in (
            "production_convergence_state",
            "pricing_artifact",
            "macro_policy_pack",
            "client_report_manifest",
        )
    }
    return {
        "schema_version": "etf_eu_routine_run_manifest_v3_converged",
        "report_engine": "production_convergence_v1",
        "report_section_count": 19,
        "languages": ["nl", "en"],
        "expected_attachment_count": 4,
        "run_id": "20260805_test_1",
        "report_date": "2026-08-05",
        "report_suffix": "260805_01",
        "source_commit_sha": "a" * 40,
        "donor_commit_sha": "b" * 40,
        "files": files,
        "state_artifacts": state_artifacts,
        "package_status": "generated_pending_machine_and_visual_review",
        "ready_for_controlled_delivery": False,
        "delivery_authority": False,
        "smtp_transport_success": False,
        "independent_receipt_confirmed": False,
        "portfolio_mutation": False,
        "ledger_write": False,
        "execution_authority": False,
    }


def test_activated_four_position_manifest_is_valid(tmp_path: Path) -> None:
    manifest = _base_manifest(tmp_path)
    positions = [
        {"ticker": "VWCE"},
        {"ticker": "EUNA"},
        {"ticker": "SXR8"},
        {"ticker": "L0CK"},
    ]
    manifest["portfolio_snapshot"] = {
        "position_count": 4,
        "funded_tickers": ["EUNA", "L0CK", "SXR8", "VWCE"],
        "positions": positions,
        "cash_eur": 1000.0,
        "pricing_close_dates": ["2026-08-05"],
        "official_portfolio_state_sha256": "c" * 64,
        "official_trade_ledger_sha256": "d" * 64,
        "model_portfolio_only": True,
        "real_broker_execution": False,
        "activation_id": "STAGE1_20260804",
    }
    manifest["strategy_snapshot"] = {
        "current_promoted_exposure_count": 6,
        "mapped_promoted_exposure_count": 6,
        "unmapped_promoted_exposure_count": 0,
        "stage_1_review_candidate_count": 2,
        "stage_1_decision": "partially_activated",
        "stage_1_activation_authorized": True,
        "activated_tickers": ["L0CK"],
        "remaining_monitored_tickers": ["VVSM"],
        "executable_trade_intents": [],
        "model_portfolio_only": True,
        "real_broker_execution": False,
        "activation_id": "STAGE1_20260804",
    }

    assert validate(manifest) == []


def test_pre_activation_three_position_manifest_remains_valid(tmp_path: Path) -> None:
    manifest = _base_manifest(tmp_path)
    positions = [{"ticker": "VWCE"}, {"ticker": "EUNA"}, {"ticker": "SXR8"}]
    manifest["portfolio_snapshot"] = {
        "position_count": 3,
        "funded_tickers": ["EUNA", "SXR8", "VWCE"],
        "positions": positions,
        "cash_eur": 1000.0,
        "pricing_close_dates": ["2026-08-05"],
        "official_portfolio_state_sha256": "c" * 64,
        "official_trade_ledger_sha256": "d" * 64,
    }
    manifest["strategy_snapshot"] = {
        "current_promoted_exposure_count": 6,
        "mapped_promoted_exposure_count": 6,
        "unmapped_promoted_exposure_count": 0,
        "stage_1_review_candidate_count": 2,
        "stage_1_decision": "blocked",
        "stage_1_activation_authorized": False,
        "activated_tickers": [],
        "remaining_monitored_tickers": ["VVSM", "L0CK"],
        "executable_trade_intents": [],
    }

    assert validate(manifest) == []


def test_activated_manifest_rejects_broker_execution_or_missing_provenance(tmp_path: Path) -> None:
    manifest = _base_manifest(tmp_path)
    positions = [
        {"ticker": "VWCE"},
        {"ticker": "EUNA"},
        {"ticker": "SXR8"},
        {"ticker": "L0CK"},
    ]
    manifest["portfolio_snapshot"] = {
        "position_count": 4,
        "funded_tickers": ["VWCE", "EUNA", "SXR8", "L0CK"],
        "positions": positions,
        "cash_eur": 1000.0,
        "pricing_close_dates": ["2026-08-05"],
        "official_portfolio_state_sha256": "c" * 64,
        "official_trade_ledger_sha256": "d" * 64,
        "model_portfolio_only": True,
        "real_broker_execution": True,
        "activation_id": None,
    }
    manifest["strategy_snapshot"] = {
        "current_promoted_exposure_count": 6,
        "mapped_promoted_exposure_count": 6,
        "unmapped_promoted_exposure_count": 0,
        "stage_1_review_candidate_count": 2,
        "stage_1_decision": "partially_activated",
        "stage_1_activation_authorized": True,
        "activated_tickers": ["L0CK"],
        "remaining_monitored_tickers": ["VVSM"],
        "executable_trade_intents": [],
        "model_portfolio_only": True,
        "real_broker_execution": True,
        "activation_id": None,
    }

    blockers = validate(manifest)
    assert "activated portfolio must not imply broker execution" in blockers
    assert "activated portfolio provenance is missing" in blockers
    assert "activated strategy snapshot must not imply broker execution" in blockers
    assert "activated strategy provenance is missing" in blockers
