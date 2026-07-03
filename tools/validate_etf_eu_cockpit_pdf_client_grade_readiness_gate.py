from __future__ import annotations

import argparse
import json
from pathlib import Path

CONTRACT = Path("control/ETF_EU_COCKPIT_PDF_CLIENT_GRADE_READINESS_CONTRACT_V1.md")
ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_client_grade_readiness_gate_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_client_grade_readiness_gate_notes_20260703_000000.md")
SOURCE_VISUAL_REVIEW_ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_premium_dutch_refinement_visual_review_checkpoint_20260703_000000.json")
SOURCE_VISUAL_REVIEW_NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_premium_dutch_refinement_visual_review_checkpoint_notes_20260703_000000.md")
PRIOR_CONTENT_CONTRACT = Path("control/ETF_EU_COCKPIT_PDF_CLIENT_GRADE_CONTENT_CONTRACT_V1.md")


class ValidationError(RuntimeError):
    pass


def _need(path: Path, label: str) -> None:
    if not path.exists():
        raise ValidationError(f"missing {label}: {path}")


def _true(data: dict, key: str) -> None:
    if data.get(key) is not True:
        raise ValidationError(f"expected true: {key}")


def _false(data: dict, key: str) -> None:
    if data.get(key) is not False:
        raise ValidationError(f"expected false: {key}")


def _contains(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValidationError(f"{label} missing marker: {marker}")


def validate_readiness_gate(path: Path) -> dict[str, str]:
    if path != ARTIFACT:
        raise ValidationError(f"unexpected WP15V artifact path: {path}")

    for file_path, label in [
        (CONTRACT, "readiness contract"),
        (ARTIFACT, "readiness gate artifact"),
        (NOTES, "readiness gate notes"),
        (SOURCE_VISUAL_REVIEW_ARTIFACT, "source WP15U checkpoint"),
        (SOURCE_VISUAL_REVIEW_NOTES, "source WP15U notes"),
        (PRIOR_CONTENT_CONTRACT, "prior content contract"),
    ]:
        _need(file_path, label)

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    expected = {
        "schema_version": "etf_eu_cockpit_pdf_client_grade_readiness_gate_v1",
        "run_id": "20260703_000000",
        "repository": "market-predictions/weekly-etf-eu",
        "work_package_id": "ETF-EU-WP15V",
        "legacy_work_package_id": "WP15V",
        "status": "completed_after_readiness_contract_and_evidence_gate_definition",
        "source_work_package": "ETF-EU-WP15U",
        "source_visual_review_artifact": str(SOURCE_VISUAL_REVIEW_ARTIFACT),
        "source_visual_review_notes": str(SOURCE_VISUAL_REVIEW_NOTES),
        "readiness_contract_path": str(CONTRACT),
        "readiness_gate_artifact": str(ARTIFACT),
        "readiness_gate_notes": str(NOTES),
        "readiness_gate_validator": "tools/validate_etf_eu_cockpit_pdf_client_grade_readiness_gate.py",
        "readiness_gate_tests": "tests/test_etf_eu_cockpit_pdf_client_grade_readiness_gate.py",
        "readiness_gate_status": "contract_defined_not_passed",
        "delivery_authorization_decision": "remain_blocked",
        "selected_next_package": "ETF-EU-WP15W",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            raise ValidationError(f"unexpected {key}: {data.get(key)!r}")

    for key in [
        "client_grade_readiness_contract_created",
        "evidence_gate_created",
        "validator_created",
        "tests_created",
    ]:
        _true(data, key)

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

    for group_key, minimum in [
        ("decision_framework_gates", 8),
        ("input_state_contract_gates", 18),
        ("output_contract_gates", 11),
        ("operational_runbook_gates", 9),
        ("blocking_gates_before_client_grade", 7),
        ("blocking_gates_before_delivery_preflight", 6),
    ]:
        values = data.get(group_key)
        if not isinstance(values, list) or len(values) < minimum:
            raise ValidationError(f"{group_key} missing or too short")

    contract_text = CONTRACT.read_text(encoding="utf-8")
    for marker in [
        "decision framework",
        "input/state contract",
        "output contract",
        "operational runbook",
        "ISIN-first",
        "UCITS",
        "PRIIPs/KID",
        "pricing freshness",
        "Dutch-first",
        "proxy disclosure",
        "unresolved data",
        "delivery receipt",
        "production manifest",
        "readiness_gate_status=contract_defined_not_passed",
    ]:
        _contains(contract_text, marker, "readiness contract")

    notes = NOTES.read_text(encoding="utf-8")
    for marker in [
        "work_package_id=ETF-EU-WP15V",
        "readiness_gate_status=contract_defined_not_passed",
        "production_delivery=false",
        "valuation_grade=false",
        "ETF-EU-WP15W",
    ]:
        _contains(notes, marker, "readiness notes")

    print(
        "ETF_EU_COCKPIT_PDF_CLIENT_GRADE_READINESS_GATE_OK "
        f"| artifact={ARTIFACT} | contract={CONTRACT} | selected_next_package=ETF-EU-WP15W"
    )
    return {"status": "valid", "artifact": str(ARTIFACT), "contract": str(CONTRACT), "selected_next_package": "ETF-EU-WP15W"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    validate_readiness_gate(Path(parser.parse_args().artifact))


if __name__ == "__main__":
    main()
