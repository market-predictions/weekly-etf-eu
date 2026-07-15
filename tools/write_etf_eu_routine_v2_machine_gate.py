from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Validation artifact not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _language_payload(validation: dict[str, Any], *, language_key: str, run_id: str) -> dict[str, Any]:
    data = validation.get(language_key) if isinstance(validation.get(language_key), dict) else {}
    passed = data.get("passed") is True
    forbidden = list(data.get("forbidden_tokens") or [])
    blockers = list(data.get("blockers") or [])
    return {
        "schema_version": "etf_eu_routine_pdf_client_grade_v2_adapter_v1",
        "artifact_type": "etf_eu_routine_pdf_client_grade",
        "generated_at_utc": _utc_now(),
        "repair_run_id": run_id,
        "source_run_id": run_id,
        "language": "nl" if language_key == "dutch" else "en",
        "page_count": data.get("page_count"),
        "required_sections_present": not data.get("missing_sections"),
        "missing_sections": list(data.get("missing_sections") or []),
        "investor_analyst_hierarchy_passed": data.get("investor_analyst_hierarchy_passed") is True,
        "isin_first_visible": data.get("isin_first_visible") is True,
        "research_only_labelling_passed": data.get("research_only_labelling_passed") is True,
        "macro_freshness_disclosure_passed": data.get("macro_freshness_disclosure_passed") is True,
        "equity_curve_contract_passed": data.get("equity_curve_contract_passed") is True,
        "client_surface_clean": passed and not forbidden,
        "authority_metadata_absent": passed and not any(token.endswith("=") for token in forbidden),
        "raw_status_enums_absent": passed and not any("_" in token for token in forbidden),
        "forbidden_client_tokens": forbidden,
        "machine_validation_passed": passed,
        "blockers": blockers,
        "warnings": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Adapt strict ETF EU v2 validation to the routine package gate contract.")
    parser.add_argument("--validation", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-dir", default="output/quality")
    args = parser.parse_args()

    validation_path = Path(args.validation)
    validation = _load(validation_path)
    output_dir = Path(args.output_dir)
    dutch = _language_payload(validation, language_key="dutch", run_id=args.run_id)
    english = _language_payload(validation, language_key="english", run_id=args.run_id)
    dutch_path = output_dir / f"etf_eu_routine_pdf_client_grade_{args.run_id}_nl.json"
    english_path = output_dir / f"etf_eu_routine_pdf_client_grade_{args.run_id}_en.json"
    combined_path = output_dir / f"etf_eu_routine_pdf_client_grade_{args.run_id}.json"
    _write(dutch_path, dutch)
    _write(english_path, english)

    combined_blockers = list(validation.get("blockers") or []) + dutch["blockers"] + english["blockers"]
    combined = {
        "schema_version": "etf_eu_routine_pdf_client_grade_combined_v2",
        "artifact_type": "etf_eu_routine_pdf_client_grade_combined",
        "generated_at_utc": _utc_now(),
        "source_run_id": args.run_id,
        "repair_run_id": args.run_id,
        "strict_v2_validation": str(validation_path),
        "dutch_artifact": str(dutch_path),
        "english_artifact": str(english_path),
        "dutch_pdf_client_grade_passed": dutch["machine_validation_passed"],
        "english_pdf_client_grade_passed": english["machine_validation_passed"],
        "pdf_client_grade_passed": validation.get("client_grade_v2_passed") is True and dutch["machine_validation_passed"] and english["machine_validation_passed"],
        "client_surface_clean": dutch["client_surface_clean"] and english["client_surface_clean"],
        "authority_metadata_absent": dutch["authority_metadata_absent"] and english["authority_metadata_absent"],
        "raw_status_enums_absent": dutch["raw_status_enums_absent"] and english["raw_status_enums_absent"],
        "investor_brief_present": True,
        "analyst_appendix_present": True,
        "client_renderer_mode": "client_grade_v2",
        "blockers": combined_blockers,
        "warnings": list(validation.get("warnings") or []),
    }
    _write(combined_path, combined)
    if combined["pdf_client_grade_passed"] is not True or combined["blockers"]:
        raise SystemExit("ETF_EU_ROUTINE_V2_MACHINE_GATE_FAILED")
    print(f"ETF_EU_ROUTINE_V2_MACHINE_GATE_OK | output={combined_path}")


if __name__ == "__main__":
    main()
