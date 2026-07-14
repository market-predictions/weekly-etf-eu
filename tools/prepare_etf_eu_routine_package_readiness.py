from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

AUTHORITY_FALSE = [
    "send_executed",
    "transport_attempted",
    "receipt_confirmed",
    "valuation_grade",
    "funding_authority",
    "portfolio_mutation",
    "production_delivery_authority",
]
CLIENT_FORBIDDEN = [
    "candidate_requires_verification",
    "verified_ucits_trading_line",
    "priced_non_authoritative",
    "fetch_failed",
    "ready_for_controlled_delivery=",
    "send_executed=",
    "transport_attempted=",
    "receipt_confirmed=",
    "valuation_grade=",
    "funding_authority=",
    "portfolio_mutation=",
    "production_delivery_authority=",
    "Authority flags",
]
STALE_TOKENS = ["MVP24", "MVP25", "controlled resend", "guarded resend", "herverzending"]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AssertionError(f"missing artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _check_outputs(manifest: dict[str, Any]) -> None:
    expected = {
        "dutch_primary_markdown": (".md", "Weekly ETF EU Review | Nederlands"),
        "english_companion_markdown": (".md", "Weekly ETF EU Review | English Companion"),
        "dutch_primary_html": (".html", "Weekly ETF EU Review | Nederlands"),
        "english_companion_html": (".html", "Weekly ETF EU Review | English Companion"),
    }
    for key, (suffix, marker) in expected.items():
        path = Path(str(manifest.get(key) or ""))
        _require(path.exists(), f"{key} missing: {path}")
        _require(path.suffix == suffix, f"{key} suffix mismatch")
        text = path.read_text(encoding="utf-8")
        _require(marker in text, f"{key} title marker missing")
        for token in STALE_TOKENS:
            _require(token.lower() not in text.lower(), f"{key} contains stale token: {token}")
        for token in CLIENT_FORBIDDEN:
            _require(token.lower() not in text.lower(), f"{key} contains internal client-surface token: {token}")

    for key in ["dutch_primary_pdf", "english_companion_pdf"]:
        path = Path(str(manifest.get(key) or ""))
        _require(path.exists(), f"{key} missing: {path}")
        raw = path.read_bytes()
        _require(raw.startswith(b"%PDF-"), f"{key} missing PDF header")
        _require(b"%%EOF" in raw[-512:], f"{key} missing PDF EOF")


def _check_pricing(manifest: dict[str, Any], pricing: dict[str, Any]) -> None:
    _require(pricing.get("min_threshold_met") is True, "pricing minimum threshold not met")
    _require(int(pricing.get("priced_line_count") or 0) >= 8, "insufficient priced lines")
    close_dates = sorted(
        {
            str(row.get("close_date"))
            for row in pricing.get("rows", [])
            if isinstance(row, dict) and row.get("close_date")
        }
    )
    _require(bool(close_dates), "pricing has no close dates")
    latest = date.fromisoformat(close_dates[-1])
    report_date = date.fromisoformat(str(manifest["report_date"]))
    age = (report_date - latest).days
    _require(age >= 0, "pricing close is after report date")
    _require(age <= 3, f"pricing close is stale by {age} days")
    _require(str(manifest.get("pricing_as_of")) == close_dates[-1], "manifest pricing_as_of mismatch")


def _language_machine_gates(machine_gate: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    dutch_path = Path(str(machine_gate.get("dutch_artifact") or ""))
    english_path = Path(str(machine_gate.get("english_artifact") or ""))
    return _load(dutch_path), _load(english_path)


def _check_pdf_quality(machine_gate: dict[str, Any], visual_review: dict[str, Any]) -> dict[str, bool]:
    _require(machine_gate.get("dutch_pdf_client_grade_passed") is True, "Dutch PDF machine gate did not pass")
    _require(machine_gate.get("english_pdf_client_grade_passed") is True, "English PDF machine gate did not pass")
    _require(machine_gate.get("pdf_client_grade_passed") is True, "Combined PDF client-grade gate did not pass")
    _require(not machine_gate.get("blockers"), "Combined PDF/client-surface gate has blockers")

    dutch, english = _language_machine_gates(machine_gate)
    client_surface_clean = (
        machine_gate.get("client_surface_clean") is True
        or (dutch.get("client_surface_clean") is True and english.get("client_surface_clean") is True)
    )
    authority_metadata_absent = (
        machine_gate.get("authority_metadata_absent") is True
        or (dutch.get("authority_metadata_absent") is True and english.get("authority_metadata_absent") is True)
    )
    raw_status_enums_absent = (
        machine_gate.get("raw_status_enums_absent") is True
        or (dutch.get("raw_status_enums_absent") is True and english.get("raw_status_enums_absent") is True)
    )
    _require(client_surface_clean, "Combined client-surface gate did not pass")
    _require(authority_metadata_absent, "Authority metadata remains on client surface")
    _require(raw_status_enums_absent, "Raw status enums remain on client surface")
    _require(visual_review.get("visual_review_passed") is True, "Rendered-page visual review did not pass")
    _require(not visual_review.get("blockers"), "Rendered-page visual review has blockers")
    return {
        "client_surface_clean": client_surface_clean,
        "authority_metadata_absent": authority_metadata_absent,
        "raw_status_enums_absent": raw_status_enums_absent,
    }


def prepare(
    *,
    manifest_path: Path,
    ready_path: Path,
    routine_path: Path,
    gate_path: Path,
    pdf_client_grade_gate_path: Path,
    pdf_visual_review_path: Path,
) -> dict[str, Any]:
    manifest = _load(manifest_path)
    ready = _load(ready_path)
    routine = _load(routine_path)
    pricing_path = Path(str(manifest.get("pricing_artifact_path") or ""))
    pricing = _load(pricing_path)
    machine_gate = _load(pdf_client_grade_gate_path)
    visual_review = _load(pdf_visual_review_path)

    _require(manifest.get("schema_version") == "etf_eu_fresh_generation_package_v1", "manifest schema mismatch")
    _require(manifest.get("run_id") == routine.get("run_id"), "run id mismatch")
    _require(manifest.get("report_date") == routine.get("report_date"), "report date mismatch")
    _require(manifest.get("report_suffix") == routine.get("report_suffix"), "report suffix mismatch")
    _require(routine.get("delivery_package_manifest") == str(manifest_path), "routine manifest package reference mismatch")
    _require(manifest.get("source_of_truth_repo") == "market-predictions/weekly-etf-eu", "EU source-of-truth mismatch")
    _require(manifest.get("reference_architecture_repo") == "market-predictions/weekly-etf", "donor repo mismatch")

    for payload_name, payload in [("manifest", manifest), ("ready", ready), ("routine", routine)]:
        for key in AUTHORITY_FALSE:
            _require(payload.get(key) is False, f"{payload_name}.{key} must be false")

    _check_outputs(manifest)
    _check_pricing(manifest, pricing)
    clean_state = _check_pdf_quality(machine_gate, visual_review)

    gate = {
        "schema_version": "etf_eu_routine_package_readiness_v3",
        "artifact_type": "etf_eu_routine_package_readiness",
        "generated_at_utc": _utc_now(),
        "run_id": manifest["run_id"],
        "report_date": manifest["report_date"],
        "report_suffix": manifest["report_suffix"],
        "package_manifest": str(manifest_path),
        "ready_artifact": str(ready_path),
        "routine_run_manifest": str(routine_path),
        "pricing_artifact": str(pricing_path),
        "pricing_as_of": manifest.get("pricing_as_of"),
        "pdf_client_grade_gate": str(pdf_client_grade_gate_path),
        "dutch_pdf_machine_gate": True,
        "english_pdf_machine_gate": True,
        **clean_state,
        "pdf_visual_review_artifact": str(pdf_visual_review_path),
        "pdf_visual_review_passed": True,
        "client_output_valid": True,
        "readiness_gate_passed": True,
        "ready_for_controlled_delivery": True,
        "delivery_authorized": False,
        "recipient_plaintext_values_exposed": False,
        "secret_values_exposed": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "next_action": "RUN_ROUTINE_GUARDED_DELIVERY",
        "warnings": [],
        "blockers": [],
    }
    _write(gate_path, gate)

    common_update = {
        "package_readiness_gate": str(gate_path),
        "pdf_client_grade_gate": str(pdf_client_grade_gate_path),
        "pdf_machine_gate_passed": True,
        **clean_state,
        "pdf_visual_review_artifact": str(pdf_visual_review_path),
        "pdf_visual_gate_passed": True,
        "client_output_valid": True,
        "readiness_gate_passed": True,
        "ready_for_controlled_delivery": True,
        "delivery_authorized": False,
        "next_action": "RUN_ROUTINE_GUARDED_DELIVERY",
    }
    manifest.update(common_update)
    ready.update(common_update)
    routine.update(
        {
            "routine_stage": "routine_package_readiness_passed",
            "workflow_status": "routine_package_readiness_passed",
            **common_update,
            "transport_attempted": False,
            "transport_success": False,
            "receipt_confirmed": False,
            "next_package": None,
        }
    )
    _write(manifest_path, manifest)
    _write(ready_path, ready)
    _write(routine_path, routine)
    return gate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--ready-artifact", required=True)
    parser.add_argument("--routine-manifest", required=True)
    parser.add_argument("--write-gate", required=True)
    parser.add_argument("--pdf-client-grade-gate", required=True)
    parser.add_argument("--pdf-visual-review", required=True)
    args = parser.parse_args()
    gate = prepare(
        manifest_path=Path(args.manifest),
        ready_path=Path(args.ready_artifact),
        routine_path=Path(args.routine_manifest),
        gate_path=Path(args.write_gate),
        pdf_client_grade_gate_path=Path(args.pdf_client_grade_gate),
        pdf_visual_review_path=Path(args.pdf_visual_review),
    )
    print(json.dumps(gate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
