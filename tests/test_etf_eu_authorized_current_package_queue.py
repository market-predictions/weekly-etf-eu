from __future__ import annotations

import json
from pathlib import Path

from tools.validate_etf_eu_current_package_delivery_queue import validate


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_current_package_queue_accepts_routine_guarded_delivery_selection(tmp_path: Path) -> None:
    run_id = "20260717_141500"
    common = {
        "run_id": run_id,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
    }
    package = tmp_path / "package.json"
    authorization = tmp_path / "authorization.json"
    decision = tmp_path / "decision.json"
    selection = tmp_path / "selection.json"
    routine = tmp_path / "routine.json"
    _write(package, {**common, "schema_version": "etf_eu_fresh_generation_package_v1", "ready_for_controlled_delivery": True})
    _write(authorization, {**common, "delivery_authorized": True, "send_command_allowed": True})
    _write(decision, {**common, "controlled_delivery_decision_status": "routine_guarded_delivery_selected"})
    _write(selection, {**common, "transport_selection_status": "current_package_smtp_runner_selected"})
    _write(routine, common)

    queue = tmp_path / "queue.md"
    queue.write_text(
        "\n".join(
            [
                "schema_version=etf_eu_current_package_delivery_queue_v1",
                "artifact_type=etf_eu_current_package_delivery_queue",
                f"run_id={run_id}",
                "report_date=2026-07-17",
                "report_suffix=260717_06",
                f"package_manifest={package}",
                f"authorization_artifact={authorization}",
                f"controlled_delivery_decision_artifact={decision}",
                f"transport_selection_artifact={selection}",
                f"routine_run_manifest={routine}",
                "delivery_authorized=true",
                "send_command_allowed=true",
                "recipient_plaintext_values_exposed=false",
                "secret_values_exposed=false",
                "raw_receipt_pdf_stored_in_github=false",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = validate(queue)
    assert result["status"] == "valid"
    assert result["run_id"] == run_id
