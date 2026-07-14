from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

PACKAGE_SCHEMA = "etf_eu_corrected_resend_package_v1"
FORBIDDEN_ORIGINAL_PDFS = {
    "output/fresh_generation/weekly_etf_eu_review_nl_260712.pdf",
    "output/fresh_generation/weekly_etf_eu_review_260712.pdf",
}
REQUIRED_KEYS = {
    "dutch_primary_html",
    "dutch_primary_pdf",
    "english_companion_html",
    "english_companion_pdf",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _load(path: Path) -> dict[str, Any]:
    _require(path.exists(), f"missing package manifest: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _reject_superseded(package: dict[str, Any]) -> None:
    control_id = str(package.get("correction_control_id") or "")
    supersession = Path("output/delivery_control") / f"etf_eu_corrected_resend_package_supersession_{control_id}.json"
    if not supersession.exists():
        return
    payload = _load(supersession)
    _require(payload.get("superseded") is not True, f"corrected package {control_id} is superseded and cannot be used for transport")
    _require(payload.get("live_send_allowed") is not False, f"live send is blocked for corrected package {control_id}")


def validate_package(path: Path) -> dict[str, Any]:
    package = _load(path)
    _require(package.get("schema_version") == PACKAGE_SCHEMA, "corrected package schema mismatch")
    _require(package.get("artifact_type") == "etf_eu_corrected_resend_package", "corrected package type mismatch")
    _reject_superseded(package)

    _require(package.get("source_run_id") == "20260712_125000", "source_run_id mismatch")
    _require(package.get("source_runtime_run_id") == "20260712_182002", "source_runtime_run_id mismatch")
    repair_run_id = str(package.get("repair_run_id") or "")
    control_id = str(package.get("correction_control_id") or "")
    _require(bool(repair_run_id), "repair_run_id missing")
    _require(bool(control_id), "correction_control_id missing")
    _require(package.get("report_date") == "2026-07-12", "report_date mismatch")
    _require(str(package.get("report_suffix")) == "260712", "report_suffix mismatch")
    _require(package.get("original_client_output_valid") is False, "original output must remain invalid")
    _require(package.get("dutch_machine_gate_passed") is True, "Dutch machine gate missing")
    _require(package.get("english_machine_gate_passed") is True, "English machine gate missing")
    _require(package.get("combined_machine_gate_passed") is True, "combined machine gate missing")
    _require(package.get("visual_review_passed") is True, "visual review missing")
    _require(package.get("corrected_client_output_valid") is True, "corrected output is not valid")
    _require(package.get("client_surface_clean") is True, "client-surface clean gate missing")
    _require(package.get("authority_separation_gate_passed") is True, "authority-separation gate missing")
    _require(package.get("corrected_resend_prepared") is True, "corrected resend is not prepared")
    _require(package.get("corrected_resend_executed") is False, "corrected resend must not be marked executed during preparation")
    _require(package.get("byte_identity_passed") is True, "byte identity flag missing")
    _require(not package.get("blockers"), "corrected package contains blockers")

    for key in (
        "recipient_plaintext_values_exposed",
        "secret_values_exposed",
        "raw_receipt_pdf_stored_in_github",
        "valuation_grade",
        "funding_authority",
        "portfolio_mutation",
        "production_delivery_authority",
    ):
        _require(package.get(key) is False, f"{key} must be false")

    approved = package.get("approved_source_files") or {}
    delivery = package.get("corrected_delivery_files") or {}
    source_sha = package.get("source_sha256") or {}
    delivery_sha = package.get("delivery_sha256") or {}
    _require(set(approved) == REQUIRED_KEYS, "approved source file keys mismatch")
    _require(set(delivery) == REQUIRED_KEYS, "corrected delivery file keys mismatch")
    _require(set(source_sha) == REQUIRED_KEYS, "source sha keys mismatch")
    _require(set(delivery_sha) == REQUIRED_KEYS, "delivery sha keys mismatch")

    expected_source_root = Path("output/repair_preview") / repair_run_id
    expected_delivery_root = Path("output/corrected_delivery_package") / control_id
    for key in sorted(REQUIRED_KEYS):
        source = Path(str(approved[key]))
        destination = Path(str(delivery[key]))
        _require(source.parent == expected_source_root, f"unapproved source path: {source}")
        _require(str(source) not in FORBIDDEN_ORIGINAL_PDFS, f"malformed original PDF selected: {source}")
        _require(destination.parent == expected_delivery_root, f"delivery file outside correction package: {destination}")
        _require(source.exists(), f"approved source missing: {source}")
        _require(destination.exists(), f"corrected delivery file missing: {destination}")
        source_actual = _sha256(source)
        destination_actual = _sha256(destination)
        _require(source_actual == str(source_sha[key]), f"source hash mismatch: {key}")
        _require(destination_actual == str(delivery_sha[key]), f"delivery hash mismatch: {key}")
        _require(source_actual == destination_actual, f"source/delivery byte identity mismatch: {key}")

    combined = _load(Path(str(package["combined_machine_gate_artifact"])))
    visual = _load(Path(str(package["visual_review_artifact"])))
    separation = _load(Path(str(package["authority_separation_artifact"])))
    _require(combined.get("repair_run_id") == repair_run_id, "combined machine gate repair identity mismatch")
    _require(combined.get("pdf_client_grade_passed") is True, "combined machine gate artifact failed")
    _require(not combined.get("blockers"), "combined machine gate artifact contains blockers")
    _require(visual.get("repair_run_id") == repair_run_id or visual.get("sanitization_run_id") == repair_run_id, "visual review identity mismatch")
    _require(visual.get("visual_review_passed") is True, "visual review artifact failed")
    _require(not visual.get("blockers"), "visual review artifact contains blockers")
    _require(separation.get("separation_gate_passed") is True, "authority-separation artifact failed")
    _require(not separation.get("blockers"), "authority-separation artifact contains blockers")

    original_result = _load(Path(str(package["original_transport_result"])))
    original_evidence = _load(Path(str(package["original_delivery_evidence"])))
    _require(original_result.get("transport_success") is True, "original transport success missing")
    _require(original_result.get("receipt_confirmed") is False, "original receipt state changed")
    _require(original_evidence.get("transport_success") is True, "original delivery evidence missing")
    _require(original_evidence.get("receipt_confirmed") is False, "original delivery receipt state changed")

    return {
        "status": "valid",
        "package": str(path),
        "correction_control_id": control_id,
        "repair_run_id": repair_run_id,
        "delivery_file_count": len(delivery),
        "byte_identity_passed": True,
        "machine_gate_passed": True,
        "visual_gate_passed": True,
        "client_surface_clean": True,
        "authority_separation_gate_passed": True,
        "superseded": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the Weekly ETF EU corrected-resend package.")
    parser.add_argument("--package", required=True)
    args = parser.parse_args()
    print(json.dumps(validate_package(Path(args.package)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
