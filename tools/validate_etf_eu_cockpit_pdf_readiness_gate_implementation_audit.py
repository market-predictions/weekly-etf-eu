from __future__ import annotations

import argparse
import json
from pathlib import Path

READINESS_CONTRACT = Path("control/ETF_EU_COCKPIT_PDF_CLIENT_GRADE_READINESS_CONTRACT_V1.md")
SOURCE_READINESS_GATE_ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_client_grade_readiness_gate_20260703_000000.json")
SOURCE_READINESS_GATE_NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_client_grade_readiness_gate_notes_20260703_000000.md")
SOURCE_VISUAL_REVIEW_ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_dutch_refinement_visual_review_checkpoint_20260703_000000.json")
SOURCE_VISUAL_REVIEW_NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_dutch_refinement_visual_review_checkpoint_notes_20260703_000000.md")
SOURCE_REFINEMENT_ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_dutch_refinement_candidate_build_20260703_000000.json")
SOURCE_REFINEMENT_NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_dutch_refinement_candidate_build_notes_20260703_000000.md")
ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_readiness_gate_implementation_audit_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_readiness_gate_implementation_audit_notes_20260703_000000.md")

AUDIT_GROUPS = [
    "decision_framework_audit",
    "input_state_contract_audit",
    "output_contract_audit",
    "operational_runbook_audit",
    "blocking_gates_before_client_grade",
    "blocking_gates_before_delivery_preflight",
]
ALLOWED_STATUSES = {"pass", "fail", "blocked", "not_applicable"}


class ValidationError(RuntimeError):
    pass


def _need(path: Path, label: str) -> None:
    if not path.exists():
        raise ValidationError(f"missing {label}: {path}")


def _false(data: dict, key: str) -> None:
    if data.get(key) is not False:
        raise ValidationError(f"expected false: {key}")


def _true(data: dict, key: str) -> None:
    if data.get(key) is not True:
        raise ValidationError(f"expected true: {key}")


def _expect(data: dict, key: str, value: str) -> None:
    if data.get(key) != value:
        raise ValidationError(f"unexpected {key}: {data.get(key)!r}")


def _validate_rows(data: dict) -> None:
    for group_name in AUDIT_GROUPS:
        rows = data.get(group_name)
        if not isinstance(rows, list) or not rows:
            raise ValidationError(f"missing audit group rows: {group_name}")
        for row in rows:
            if not isinstance(row, dict):
                raise ValidationError(f"audit row is not object in {group_name}")
            for key in ["gate", "status", "rationale", "evidence_reference"]:
                if key not in row or not row[key]:
                    raise ValidationError(f"missing {key} in {group_name}: {row}")
            if row["status"] not in ALLOWED_STATUSES:
                raise ValidationError(f"invalid status in {group_name}: {row['status']}")


def _has_blocking_gap(data: dict) -> bool:
    for group_name in AUDIT_GROUPS:
        for row in data.get(group_name, []):
            if row.get("status") in {"fail", "blocked"}:
                return True
    return False


def validate_readiness_gate_implementation_audit(path: Path) -> dict[str, str]:
    if path != ARTIFACT:
        raise ValidationError(f"unexpected WP15W artifact path: {path}")

    for file_path, label in [
        (READINESS_CONTRACT, "readiness contract"),
        (SOURCE_READINESS_GATE_ARTIFACT, "WP15V readiness gate artifact"),
        (SOURCE_READINESS_GATE_NOTES, "WP15V readiness gate notes"),
        (SOURCE_VISUAL_REVIEW_ARTIFACT, "WP15U visual review artifact"),
        (SOURCE_VISUAL_REVIEW_NOTES, "WP15U visual review notes"),
        (SOURCE_REFINEMENT_ARTIFACT, "WP15T refinement artifact"),
        (SOURCE_REFINEMENT_NOTES, "WP15T refinement notes"),
        (ARTIFACT, "WP15W readiness audit artifact"),
        (NOTES, "WP15W readiness audit notes"),
    ]:
        _need(file_path, label)

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    expected = {
        "schema_version": "etf_eu_cockpit_pdf_readiness_gate_implementation_audit_v1",
        "run_id": "20260703_000000",
        "repository": "market-predictions/weekly-etf-eu",
        "work_package_id": "ETF-EU-WP15W",
        "legacy_work_package_id": "WP15W",
        "status": "completed_after_readiness_gate_implementation_audit",
        "source_work_package": "ETF-EU-WP15V",
        "readiness_contract_path": str(READINESS_CONTRACT),
        "source_readiness_gate_artifact": str(SOURCE_READINESS_GATE_ARTIFACT),
        "source_readiness_gate_notes": str(SOURCE_READINESS_GATE_NOTES),
        "source_visual_review_artifact": str(SOURCE_VISUAL_REVIEW_ARTIFACT),
        "source_visual_review_notes": str(SOURCE_VISUAL_REVIEW_NOTES),
        "readiness_audit_artifact": str(ARTIFACT),
        "readiness_audit_notes": str(NOTES),
        "readiness_audit_validator": "tools/validate_etf_eu_cockpit_pdf_readiness_gate_implementation_audit.py",
        "readiness_audit_tests": "tests/test_etf_eu_cockpit_pdf_readiness_gate_implementation_audit.py",
        "readiness_audit_status": "completed_with_blocking_gaps",
        "client_grade_readiness_audit_result": "fail_blocked_by_missing_evidence",
        "delivery_authorization_decision": "remain_blocked",
        "selected_next_package": "ETF-EU-WP15X",
    }
    for key, value in expected.items():
        _expect(data, key, value)

    _true(data, "readiness_audit_created")
    _true(data, "validator_created")
    _true(data, "tests_created")

    for key in [
        "client_grade_claim",
        "client_grade_enough_for_delivery_preflight_discussion",
        "delivery_ready",
        "production_delivery",
        "portfolio_mutation",
        "candidate_promotion",
        "funding_authority",
        "valuation_grade",
        "delivery_preflight_allowed",
        "outbound_path_enabled",
        "live_data_fetch_performed",
        "pricing_evidence_changed",
        "recommendation_logic_changed",
        "client_distribution_claimed",
        "receipt_artifact_created",
        "production_manifest_created",
        "source_pdf_replaced",
        "new_pdf_created",
        "renderer_changed",
    ]:
        _false(data, key)

    _validate_rows(data)

    summary = data.get("summary")
    if not isinstance(summary, dict):
        raise ValidationError("missing summary object")
    if summary.get("readiness_audit_result") != "fail_blocked_by_missing_evidence":
        raise ValidationError("unexpected summary readiness_audit_result")
    if not summary.get("primary_blocking_gaps"):
        raise ValidationError("missing primary blocking gaps")
    if not _has_blocking_gap(data):
        raise ValidationError("audit result requires at least one fail or blocked gap")

    notes = NOTES.read_text(encoding="utf-8")
    for marker in [
        "work_package_id=ETF-EU-WP15W",
        "readiness_audit_status=completed_with_blocking_gaps",
        "client_grade_readiness_audit_result=fail_blocked_by_missing_evidence",
        "production_delivery=false",
        "valuation_grade=false",
        "ETF-EU-WP15X",
    ]:
        if marker not in notes:
            raise ValidationError(f"notes missing marker: {marker}")

    print(
        "ETF_EU_COCKPIT_PDF_READINESS_GATE_IMPLEMENTATION_AUDIT_OK "
        f"| artifact={ARTIFACT} | result=fail_blocked_by_missing_evidence | selected_next_package=ETF-EU-WP15X"
    )
    return {"status": "valid", "artifact": str(ARTIFACT), "result": "fail_blocked_by_missing_evidence", "selected_next_package": "ETF-EU-WP15X"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    validate_readiness_gate_implementation_audit(Path(parser.parse_args().artifact))


if __name__ == "__main__":
    main()
